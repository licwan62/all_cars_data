# 任务：all 第 8201-8300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0083__ad947534


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8201-8300 行

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
all 第 8201-8300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A8-D2-SEDAN-FACELIFT-01	5034	1880	1438
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440
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
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-E39-WAGON-01	4805	1800	1440
EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	4910	1860	1454
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	5202	1801	1379
EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	4658	1732	1367
EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	4580	1725	1460
EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	4560	1760	1285
EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	4399	1660	1431
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	4230	1650	1358
EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	4237	1690	1350
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	4237	1682	1370
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420
EU-CITROEN-XM-Y3-HATCHBACK-01	4708	1794	1385
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1467
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	5489	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	4759	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4759	1965	2100
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-NATURAL-POWER-01	4030	1687	1514
EU-FIAT-PANDA-I-FACELIFT-4X4-01	3408	1500	1468
EU-FIAT-PANDA-I-FACELIFT-4X4-TREKKING-01	3408	1500	1485
EU-FIAT-PANDA-I-HATCHBACK-FACELIFT-01	3408	1494	1420
EU-FIAT-PANDA-I-HATCHBACK-PREFL-01	3380	1460	1445
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540
EU-FIAT-PANDA-II-4X4-HATCHBACK-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-4X4-01	3574	1605	1632
EU-FIAT-PANDA-II-HATCHBACK-NATURAL-POWER-01	3538	1589	1614
EU-FIAT-PANDA-III-319-HATCHBACK-01	3653	1643	1551
EU-FIAT-PANDA-I-PREFL-4X4-01	3390	1485	1470
EU-FORD-ESCORT-VI-ALL-CONVERTIBLE-FACELIFT-01	4040	1692	1379
EU-FORD-ESCORT-VI-ALL-HATCHBACK-5D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE55-01	4290	1688	1591
EU-FORD-ESCORT-VI-AVL-EXPRESS-VAN-TYPE75-01	4290	1688	1603
EU-FORD-ESCORT-VI-GAL-SEDAN-01	4229	1690	1397
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398
EU-FORD-ESCORT-VI-WAGON-FACELIFT-01	4268	1690	1410
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407
EU-FORD-SIERRA-MK1-HATCHBACK-3D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-GHIA-01	4425	1725	1408
EU-FORD-SIERRA-MK1-WAGON-01	4491	1712	1438
EU-FORD-SIERRA-MK1-WAGON-GHIA-01	4522	1729	1438
EU-FORD-SIERRA-MK1-XR4I-HATCHBACK-3D-01	4459	1728	1392
EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	4459	1725	1378
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-MK2-PLATFORM-LWB-DROPSIDE-01	5302	2125	1990
EU-FORD-TRANSIT-MK2-PLATFORM-SWB-DROPSIDE-01	4552	1960	1990
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	4750	1790	1640
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-13IE-01	3392	1507	1424
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-4WD-01	3392	1537	1460
EU-LANCIA-Y10-156-S1-HATCHBACK-3D-STD-01	3392	1507	1423
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-13IE-01	3392	1507	1450
EU-LANCIA-Y10-156-S2-HATCHBACK-3D-STD-01	3392	1507	1440
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-4WD-01	3423	1507	1460
EU-LANCIA-Y10-156-S3-HATCHBACK-3D-STD-01	3423	1507	1440
EU-LANCIA-Y-840-HATCHBACK-3D-01	3725	1690	1440
EU-LANCIA-YPSILON-843-FACELIFT-HATCHBACK-3D-01	3810	1704	1530
EU-MERCEDES-BENZ-124-W124-SEDAN-01	4740	1740	1428
EU-MERCEDES-BENZ-124-W124-SEDAN-400E-01	4740	1740	1431
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-LWB-01	4405	1700	1920
EU-MERCEDES-BENZ-G-KLASSE-W460-CLOSED-SWB-01	3955	1700	1925
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-NARROW-01	4225	1690	1940
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	4275	1760	1941
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-01	4662	1760	1951
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-02	4662	1760	1931
EU-MERCEDES-BENZ-M-KLASSE-W166-SUV-5D-ML500-01	4804	1926	1796
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650
EU-NISSAN-PRAIRIE-M11-MPV-5D-01	4350	1690	1625
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630
EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	4230	1665	1685
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390
EU-NISSAN-PRIMERA-I-W10-WAGON-5D-01	4460	1700	1500
EU-NISSAN-SUNNY-B11-COUPE-3D-01	4135	1620	1355
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385
EU-NISSAN-SUNNY-B11-WAGON-5D-01	4255	1620	1360
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400
EU-NISSAN-SUNNY-B310-HBL310-SEDAN-01	3995	1590	1370
EU-NISSAN-SUNNY-B310-WAGON-5D-01	4050	1590	1390
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-02	4030	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-02	4215	1645	1380
EU-NISSAN-SUNNY-N13-SEDAN-4D-4WD-01	4215	1640	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-3D-01	3975	1690	1395
EU-NISSAN-SUNNY-N14-HATCHBACK-5D-01	4145	1690	1395
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525
EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	3740	1680	1590
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500
EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	4698	1814	1535
EU-RENAULT-CLIO-III-X85-VAN-3D-01	3986	1719	1495
EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	4620	1810	1730
EU-SEAT-ALHAMBRA-II-7N-MPV-01	4854	1904	1720
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940
EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535
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
VW	Passat b5	2.3 VR5 Syncro/4motion	Stufenheck	Allrad	Benzin	110	150	Oct 1997	Nov 2000	2024-03-01	9036
Mercedes-benz	M-Klasse	ML 320	SUV	Allrad	Benzin	160	218	Feb 1998	Jun 2003	2026-01-01	9037
Mercedes-benz	M-Klasse	ML 230	SUV	Allrad	Benzin	110	150	Feb 1998	Jun 2005	2024-03-01	9038
Mercedes-benz	C-Klasse	C 200 T Kompressor	Kombi	Heckantrieb	Benzin	141	192	Nov 1996	Mar 2001	2024-03-01	9039
Renault	Clio ii	1.2	Schrägheck	Frontantrieb	Benzin	43	58	Sep 1998	Feb 2010	2026-05-01	9040
Renault	Clio ii	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1998	May 2005	2026-05-01	9041
Renault	Clio ii	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1998	May 2005	2026-05-01	9042
Renault	Clio ii	1.6 16V	Schrägheck	Frontantrieb	Benzin	79	107	Sep 1998	Apr 2005	2026-05-01	9043
Renault	Clio ii	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Sep 1998	May 2005	2026-05-01	9044
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	100	136	Apr 1998	Sep 2001	2024-03-01	9045
Mercedes-benz	G-Klasse	G 320	Geländewagen geschlossen	Allrad	Benzin	158	215	Jul 1997	Aug 2004	2024-03-01	9046
Mercedes-benz	G-Klasse	G 320	Geländewagen offen	Allrad	Benzin	158	215	Nov 1997	Aug 2004	2024-03-01	9047
Seat	Alhambra	1.8 T 20V	Großraumlimousine	Frontantrieb	Benzin	110	150	Oct 1997	Mar 2010	2024-03-01	9048
Citroën	Xm	3.0 V6	Schrägheck	Frontantrieb	Benzin	123	167	May 1994	Oct 2000	2024-03-01	9049
Citroën	Xm	3.0 V6 24V	Schrägheck	Frontantrieb	Benzin	147	200	May 1994	Oct 2000	2024-03-01	9050
Citroën	Xm	2.1 TD 12V	Schrägheck	Frontantrieb	Diesel	80	109	May 1994	Oct 2000	2024-03-01	9051
Citroën	Xm	3.0 V6	Kombi	Frontantrieb	Benzin	123	167	May 1994	Oct 2000	2024-03-01	9052
Citroën	Xm	2.1 TD 12V	Kombi	Frontantrieb	Diesel	80	109	May 1994	Oct 2000	2024-03-01	9053
Chevrolet	Lacetti	2.0 D	Kombi	Frontantrieb	Diesel	89	121	Jan 2007	-	2024-03-01	9054
VW	Polo	1.4	Kombi	Frontantrieb	Benzin	44	60	May 1997	Sep 2001	2024-03-01	9055
VW	Polo	1.6	Kombi	Frontantrieb	Benzin	55	75	May 1997	Sep 2001	2024-03-01	9056
VW	Polo	1.6	Kombi	Frontantrieb	Benzin	74	101	May 1997	Sep 2001	2024-03-01	9057
VW	Polo	1.9 TDI	Kombi	Frontantrieb	Diesel	66	90	May 1997	Sep 2001	2024-03-01	9058
VW	Polo	1.7 SDI	Kombi	Frontantrieb	Diesel	44	60	Aug 1997	Sep 2001	2026-05-01	9059
Renault	Clio iii	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	63	86	Jun 2005	Jul 2010	2026-05-01	9061
Skoda	Octavia	1.9 TDI	Schrägheck	Frontantrieb	Diesel	81	110	Aug 1997	Jan 2006	2024-03-01	9063
Mercedes-benz	Sprinter 2-T	210 D	Bus	Heckantrieb	Diesel	75	102	Mar 1997	Apr 2000	2024-03-01	9064
VW	Polo	57 1.7 SDI	Stufenheck	Frontantrieb	Diesel	44	60	Jul 1997	Sep 2001	2026-05-01	9065
Lancia	Y	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Nov 1995	Sep 2003	2024-03-01	9066
Lancia	Y	1.2 16V	Schrägheck	Frontantrieb	Benzin	63	86	Apr 1997	Sep 2003	2024-03-01	9067
Citroën	Xantia	3.0 V6	Kombi	Frontantrieb	Benzin	140	190	Jan 1998	Apr 2003	2024-03-01	9073
Suzuki	Sx4 / classic	1.6 VVT 4X4	Schrägheck	Allrad	Benzin	82	112	Jul 2009	-	2024-03-01	9086
Suzuki	Swift iv	1.2	Schrägheck	Frontantrieb	Benzin	66	90	Oct 2010	Apr 2017	2026-03-01	9087
BMW	5	528 I	Kombi	Heckantrieb	Benzin	142	193	Nov 1996	Aug 2000	2024-03-01	9090
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	125	170	Mar 1998	Sep 2000	2024-03-01	9091
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	110	150	Mar 1998	Sep 2000	2024-03-01	9092
Ssangyong	Korando	2.3	Geländewagen offen	Allrad	Benzin	103	140	Nov 1997	Feb 2000	2024-03-01	9093
Daewoo	Korando	2.9 D	Geländewagen offen	Allrad	Diesel	72	98	Feb 1999	-	2024-03-01	9094
Honda	Shuttle	2.3 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Oct 1997	Jun 2004	2024-03-01	9095
Citroën	Xsara	1.8 I	Coupe	Frontantrieb	Benzin	66	90	Feb 1998	Sep 2000	2024-03-01	9096
Citroën	Xsara	1.8 I 16V	Coupe	Frontantrieb	Benzin	81	110	Feb 1998	Sep 2000	2024-03-01	9097
Citroën	Xsara	2.0 I 16V	Coupe	Frontantrieb	Benzin	120	163	Feb 1998	Mar 2005	2024-03-01	9098
Mercedes-benz	124	220 TE	Kombi	Heckantrieb	Benzin	110	150	Oct 1992	May 1993	2024-03-01	9099
Audi	A8 d2	2.8	Stufenheck	Frontantrieb	Benzin	120	163	Jul 1995	Mar 1996	2024-03-01	9102
Audi	A8 d2	2.8 Quattro	Stufenheck	Allrad	Benzin	120	163	Jul 1995	Mar 1996	2024-03-01	9103
Alfa Romeo	Sz	3.0 V6 Zagato	Coupe	Heckantrieb	Benzin	152	207	Sep 1988	Aug 1994	2024-03-01	9105
Cadillac	Seville	4.5 V8	Stufenheck	Frontantrieb	Benzin	134	182	Sep 1987	Sep 1990	2024-03-01	9107
Citroën	Bx	19 CAT	Kombi	Frontantrieb	Benzin	75	102	Jul 1986	Dec 1994	2024-03-01	9108
Citroën	Bx	14	Kombi	Frontantrieb	Benzin	55	75	Jan 1989	Feb 1993	2024-03-01	9110
Citroën	Xm	2.0 I	Kombi	Frontantrieb	Benzin	79	107	Nov 1991	Apr 1994	2024-03-01	9112
Suzuki	Swift iv	1.2 4X4	Schrägheck	Allrad	Benzin	66	90	Oct 2010	Apr 2017	2026-03-01	9113
Honda	Jazz iii	1.3 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	75	102	Apr 2011	Dec 2015	2025-12-01	9114
Saab	9-3	2.0 T Biopower XWD	Stufenheck	Allrad	Benzin/Ethanol	154	210	Jan 2008	Feb 2015	2024-03-01	9115
Saab	9-3	2.8 Turbo V6	Stufenheck	Frontantrieb	Benzin	169	230	Mar 2005	Feb 2015	2024-03-01	9116
Nissan	Prairie	2.4 I 4X4	Großraumlimousine	Allrad	Benzin	98	133	Apr 1992	Jul 1994	2024-03-01	9119
Chrysler	Daytona	2.5 I Turbo	Coupe	Frontantrieb	Benzin	110	150	Jan 1989	Oct 1992	2024-03-01	9122
Saab	9-3	2.0 T BIO Power	Kombi	Frontantrieb	Benzin/Ethanol	147	200	Feb 2009	Feb 2015	2024-03-01	9123
Saab	9-3	2.0 T BIO Power XWD	Kombi	Allrad	Benzin/Ethanol	154	209	Jun 2008	Feb 2015	2024-03-01	9124
Saab	9-3	2.0 T Biopower XWD	Kombi	Allrad	Benzin/Ethanol	120	163	Jan 2007	Feb 2015	2024-03-01	9125
Fiat	Ducato	150 Multijet 3,0 D	Kasten	Frontantrieb	Diesel	107	146	Apr 2010	Jul 2014	2025-06-01	9126
Saab	9-3	2.8 Turbo V6	Kombi	Frontantrieb	Benzin	169	230	Mar 2005	Feb 2015	2024-03-01	9128
Fiat	Ducato	150 Multijet 3,0 D	Bus	Frontantrieb	Diesel	107	146	Apr 2010	Jul 2014	2025-06-01	9129
Fiat	Ducato	150 Multijet 3,0 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2010	Jul 2014	2025-06-01	9130
Saab	9-3	2.8 Turbo V6	Cabriolet	Frontantrieb	Benzin	169	230	Feb 2006	Feb 2015	2024-03-01	9131
Saab	9-3	1.9 Ttid	Cabriolet	Frontantrieb	Diesel	118	160	Dec 2007	Feb 2015	2024-03-01	9132
Hyundai	Grand santa fé	2.2 Crdi Allrad	SUV	Allrad	Diesel	145	197	Jun 2013	Nov 2018	2024-03-01	9135
Saab	9-3	2.0 T Biopower XWD	Stufenheck	Allrad	Benzin/Ethanol	120	163	Jan 2008	Feb 2015	2024-03-01	9136
Saab	9-3	1.9 Ttid	Stufenheck	Frontantrieb	Diesel	118	160	Dec 2007	Feb 2015	2024-03-01	9137
Saab	9-3	2.0 T XWD	Stufenheck	Allrad	Benzin	120	163	Jan 2007	Feb 2015	2024-03-01	9138
Opel	Agila b	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	48	65	Jan 2010	Jun 2011	2025-06-01	9139
Opel	Agila b	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	63	86	Apr 2008	Oct 2010	2025-06-01	9140
Chevrolet	Corsica	3.1	Stufenheck	Frontantrieb	Benzin	101	137	Sep 1989	Dec 1990	2024-03-01	9143
Nissan	Sunny	1.6 16V 4X4	Kombi	Allrad	Benzin	66	90	Nov 1990	May 1995	2024-03-01	9147
Nissan	Sunny	1.6 I 12V 4X4	Kombi	Allrad	Benzin	66	90	Oct 1988	Aug 1990	2024-03-01	9148
Alfa Romeo	159	2.0 Jtdm	Stufenheck	Frontantrieb	Diesel	120	163	May 2009	Nov 2011	2024-03-01	9154
Alfa Romeo	159	2.0 Jtdm	Kombi	Frontantrieb	Diesel	120	163	May 2009	Nov 2011	2024-03-01	9155
Opel	Astra h caravan	1.4	Kombi	Frontantrieb	Benzin	55	75	Aug 2004	Oct 2010	2024-03-01	9156
Opel	Corsa d	1	Schrägheck	Frontantrieb	Benzin	48	65	Dec 2009	Aug 2014	2024-03-01	9157
Fiat	Grande punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	62	84	Apr 2010	-	2024-03-01	9158
Fiat	Panda	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	51	69	Nov 2010	Aug 2013	2024-03-01	9159
Opel	Astra j	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	88	120	Oct 2010	Oct 2015	2024-03-01	9160
Nissan	Primera	2.0 16V 4X4	Stufenheck	Allrad	Benzin	85	116	Apr 1991	Jun 1996	2024-03-01	9161
Nissan	Primera	2.0 16V 4X4	Schrägheck	Allrad	Benzin	85	116	Apr 1991	Jun 1996	2024-03-01	9162
Nissan	Pick up	2.4 4WD	Pick-up	Allrad	Benzin	74	101	Mar 1986	Apr 1992	2024-03-01	9163
Nissan	Pick up	2.4 I 12V 4WD	Pick-up	Allrad	Benzin	93	126	Apr 1992	Feb 1998	2024-03-01	9165
Daihatsu	Hijet	1.0 I	Bus	Heckantrieb	Benzin	35	48	Jul 1994	May 1998	2024-03-01	9168
Daihatsu	Hijet	1.2 D	Kasten	Heckantrieb	Diesel	26	35	May 1995	Mar 1998	2024-03-01	9169
Opel	Corsa d	1.3 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	Jul 2006	Aug 2014	2024-03-01	9171
Opel	Corsa d	1.3 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Jul 2006	Jun 2010	2024-03-01	9172
Opel	Corsa d	1	Kasten/Schrägheck	Frontantrieb	Benzin	48	65	Jan 2010	Aug 2014	2024-03-01	9173
Opel	Corsa d	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Jan 2010	Aug 2014	2024-03-01	9174
Opel	Corsa d	1.3 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	70	95	Nov 2009	Aug 2014	2024-03-01	9175
Opel	Corsa d	1	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Aug 2006	Aug 2014	2024-03-01	9176
Opel	Corsa d	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	59	80	Aug 2006	Aug 2014	2024-03-01	9177
Ford	Escort vi	RS 2000 4X4	Schrägheck	Allrad	Benzin	110	150	Feb 1995	Oct 1998	2024-03-01	9181
Ford	Sierra	2.8 Xr4i	Kombi	Heckantrieb	Benzin	105	143	Aug 1982	Dec 1986	2024-03-01	9183
Ford	Sierra	2.9	Kombi	Heckantrieb	Benzin	107	145	Aug 1988	Feb 1993	2024-03-01	9184
Ford	Scorpio i turnier	2.9 I 4X4	Kombi	Allrad	Benzin	107	145	May 1988	Feb 1993	2024-03-01	9185
Ford	Transit	2	Bus	Heckantrieb	Benzin	66	90	Sep 1991	Sep 1994	2024-03-01	9186
Ford	Transit	2	Kasten	Heckantrieb	Benzin	66	90	Sep 1991	Jun 1994	2024-03-01	9187


--- Round 1 / 首次发送 ---
## 更新点

* 完成 100 个输入 Ktype 的首轮物理车身聚类与缓存关联。
* 直接闭合 50 个 Ktype，共形成 56 条 `READY` 映射。
* 首次建立 Corsa D 三门、五门两个尺寸组；其他已闭合映射均复用跨批次尺寸组。
* 剩余 50 个 Ktype 主要受改款、门数、轴距/车顶、CAB/BED 或输入字段冲突阻塞。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：50
* 尚有 PENDING 的 Ktype：50
* READY 映射行：56
* PENDING 映射行：50
* 已引用尺寸组：37
* 复用已有尺寸组：35
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9036	9036	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	B5前期四门轿车。	READY
9037	9037	SUV	M-Class W163	W163	5		MEDIUM	W163五门SUV；待闭合统一三维与来源。	PENDING: W163尺寸组尚未闭合
9038	9038	SUV	M-Class W163	W163	5		MEDIUM	与ML 320共用W163外廓候选。	PENDING: W163尺寸组尚未闭合
9039_prefl	9039	Wagon	C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	MEDIUM	S202前期旅行车分支。	READY
9039_facelift	9039	Wagon	C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	MEDIUM	S202改款旅行车分支。	READY
9040	9040	Hatchback	Clio II				LOW	生产期跨多个Clio II阶段，门数和改款外廓尚未拆清。	PENDING: Clio II物理分支未闭合
9041	9041	Hatchback	Clio II				LOW	生产期跨多个Clio II阶段，门数和改款外廓尚未拆清。	PENDING: Clio II物理分支未闭合
9042	9042	Hatchback	Clio II				LOW	生产期跨多个Clio II阶段，门数和改款外廓尚未拆清。	PENDING: Clio II物理分支未闭合
9043	9043	Hatchback	Clio II				LOW	生产期跨多个Clio II阶段，门数和改款外廓尚未拆清。	PENDING: Clio II物理分支未闭合
9044	9044	Hatchback	Clio II				LOW	生产期跨多个Clio II阶段，门数和改款外廓尚未拆清。	PENDING: Clio II物理分支未闭合
9045	9045	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9046	9046	SUV	G-Class W463	W463			LOW	封闭式W463可能覆盖短轴三门与长轴五门。	PENDING: W463封闭式车身分支未闭合
9047	9047	Convertible	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	MEDIUM	1997年后宽体敞篷分支。	READY
9048_prefl	9048	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	MEDIUM	7M前期分支。	READY
9048_facelift	9048	MPV	Alhambra I	7M	5		MEDIUM	生产期覆盖7M改款分支。	PENDING: Alhambra I改款尺寸组缺失
9049	9049	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9050	9050	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9051	9051	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9052	9052	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4旅行车外廓。	READY
9053	9053	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4旅行车外廓。	READY
9054	9054	Wagon	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	HIGH	J200五门旅行车。	READY
9055	9055	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9056	9056	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9057	9057	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9058	9058	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9059	9059	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9061	9061	Van	Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	HIGH	三门厢式外廓。	READY
9063_prefl	9063	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	1U前期五门掀背分支。	READY
9063_facelift	9063	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	1U改款五门掀背分支。	READY
9064	9064	MPV	Sprinter I				LOW	Bus版本存在轴距和车顶高度分支。	PENDING: Sprinter 2-T车身配置未闭合
9065	9065	Sedan	Polo III	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门轿车。	READY
9066	9066	Hatchback	Y 840	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH	840三门掀背。	READY
9067	9067	Hatchback	Y 840	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH	840三门掀背。	READY
9073	9073	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2五门旅行车。	READY
9086	9086	Hatchback	SX4		5		MEDIUM	四驱五门掀背外廓待确认。	PENDING: SX4尺寸组尚未闭合
9087_3dr	9087	Hatchback	Swift IV		3	EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	MEDIUM	三门外廓分支。	READY
9087_5dr	9087	Hatchback	Swift IV		5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	MEDIUM	五门外廓分支。	READY
9090	9090	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH	E39 Touring。	READY
9091	9091	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9092	9092	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9093	9093	Convertible	Korando II	KJ	3		LOW	开放式KJ外廓与封闭式高度组不可直接混用。	PENDING: Korando开放式尺寸组缺失
9094	9094	Convertible	Korando II	KJ	3		LOW	开放式KJ外廓与封闭式高度组不可直接混用。	PENDING: Korando开放式尺寸组缺失
9095	9095	MPV	Shuttle I	RA1	5	EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	HIGH	RA1五门MPV。	READY
9096	9096	Coupe	Xsara I	N0	3		MEDIUM	三门Coupe外廓尚未建立独立尺寸组。	PENDING: Xsara Coupe尺寸组缺失
9097	9097	Coupe	Xsara I	N0	3		MEDIUM	三门Coupe外廓尚未建立独立尺寸组。	PENDING: Xsara Coupe尺寸组缺失
9098	9098	Coupe	Xsara I	N0	3		MEDIUM	三门Coupe外廓尚未建立独立尺寸组。	PENDING: Xsara Coupe尺寸组缺失
9099	9099	Wagon	124 Series	S124	5		MEDIUM	S124旅行车外廓待闭合。	PENDING: S124尺寸组缺失
9102	9102	Sedan	A8 D2	D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	D2前期四门轿车。	READY
9103	9103	Sedan	A8 D2	D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	D2前期四门轿车。	READY
9105	9105	Coupe	SZ	ES30	2		MEDIUM	ES30双门Coupe外廓待闭合。	PENDING: Alfa Romeo SZ尺寸组缺失
9107	9107	Sedan	Seville II		4	EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	HIGH	第二代Seville四门轿车。	READY
9108	9108	Wagon	BX I Phase II		5		LOW	生产期内Break高度存在标准/后期差异。	PENDING: BX Phase II Break高度分支未闭合
9110	9110	Wagon	BX I Phase II		5		LOW	需确认对应标准或后期Break高度。	PENDING: BX Phase II Break高度分支未闭合
9112	9112	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH	Y3五门旅行车。	READY
9113	9113	Hatchback	Swift IV		5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	HIGH	五门四驱外廓。	READY
9114	9114	Hatchback	Jazz III		5		MEDIUM	Hybrid五门外廓待确认统一三维。	PENDING: Jazz III Hybrid尺寸组缺失
9115	9115	Sedan	9-3 II		4		LOW	轿车生产期及XWD/前驱高度边界尚未闭合。	PENDING: Saab 9-3 Sedan尺寸组未闭合
9116	9116	Sedan	9-3 II		4		LOW	轿车生产期及XWD/前驱高度边界尚未闭合。	PENDING: Saab 9-3 Sedan尺寸组未闭合
9119	9119	MPV	Prairie M11		5		LOW	四驱版本需确认M11/NM11及对应高度。	PENDING: Prairie 2.4 4X4尺寸组未闭合
9122	9122	Coupe	Daytona		3	EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	MEDIUM	同代三门Daytona外廓复用。	READY
9123	9123	Wagon	9-3 II		5		LOW	SportCombi前驱/XWD及改款边界尚未闭合。	PENDING: Saab 9-3 Wagon尺寸组未闭合
9124	9124	Wagon	9-3 II		5		LOW	SportCombi前驱/XWD及改款边界尚未闭合。	PENDING: Saab 9-3 Wagon尺寸组未闭合
9125	9125	Wagon	9-3 II		5		LOW	SportCombi前驱/XWD及改款边界尚未闭合。	PENDING: Saab 9-3 Wagon尺寸组未闭合
9126	9126	Van	Ducato X250	X250			LOW	Kasten覆盖多个轴距和车顶高度。	PENDING: Ducato X250 Van配置未拆分
9128	9128	Wagon	9-3 II		5		LOW	SportCombi前驱/XWD及改款边界尚未闭合。	PENDING: Saab 9-3 Wagon尺寸组未闭合
9129	9129	MPV	Ducato X250	X250			LOW	Bus覆盖多个轴距和车顶高度。	PENDING: Ducato X250 Bus配置未拆分
9130	9130	Pickup	Ducato X250	X250			LOW	底盘/平台版本覆盖轴距、单排/双排配置。	PENDING: Ducato X250平台配置未拆分
9131	9131	Convertible	9-3 II		2		LOW	Cabriolet改款阶段及统一三维尚未闭合。	PENDING: Saab 9-3 Cabriolet尺寸组未闭合
9132	9132	Convertible	9-3 II		2		LOW	Cabriolet改款阶段及统一三维尚未闭合。	PENDING: Saab 9-3 Cabriolet尺寸组未闭合
9135	9135	SUV	Grand Santa Fe	NC	5		MEDIUM	长轴五门SUV外廓待闭合。	PENDING: Grand Santa Fe尺寸组缺失
9136	9136	Sedan	9-3 II		4		LOW	轿车前驱/XWD及改款高度边界尚未闭合。	PENDING: Saab 9-3 Sedan尺寸组未闭合
9137	9137	Sedan	9-3 II		4		LOW	轿车前驱/XWD及改款高度边界尚未闭合。	PENDING: Saab 9-3 Sedan尺寸组未闭合
9138	9138	Sedan	9-3 II		4		LOW	轿车前驱/XWD及改款高度边界尚未闭合。	PENDING: Saab 9-3 Sedan尺寸组未闭合
9139	9139	Hatchback	Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH	H08五门掀背。	READY
9140	9140	Hatchback	Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH	H08五门掀背。	READY
9143	9143	Sedan	Corsica I		4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH	第一代四门轿车。	READY
9147	9147	Wagon	Sunny Y10	Y10	5	EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	HIGH	Y10五门四驱旅行车。	READY
9148	9148	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	HIGH	B12五门四驱旅行车。	READY
9154	9154	Sedan	159	939	4		MEDIUM	939四门轿车外廓待闭合。	PENDING: Alfa Romeo 159 Sedan尺寸组缺失
9155	9155	Wagon	159	939	5		MEDIUM	939 Sportwagon外廓待闭合。	PENDING: Alfa Romeo 159 Wagon尺寸组缺失
9156	9156	Wagon	Astra H		5		LOW	生产期跨前期/改款，现有缓存仅标注改款组。	PENDING: Astra H Caravan阶段边界未闭合
9157_3dr	9157	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	MEDIUM	L08三门分支。	READY
9157_5dr	9157	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	MEDIUM	L68五门分支。	READY
9158_3dr	9158	Hatchback	Grande Punto 199	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	三门分支。	READY
9158_5dr	9158	Hatchback	Grande Punto 199	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	五门分支。	READY
9159	9159	Hatchback	Panda		5		LOW	生产期可能跨Panda II与Panda III LPG版本。	PENDING: Panda LPG代际边界未闭合
9160	9160	Hatchback	Astra J		5		MEDIUM	五门掀背尺寸组尚未建立。	PENDING: Astra J Hatchback尺寸组缺失
9161	9161	Sedan	Primera I P10	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车。	READY
9162	9162	Hatchback	Primera I P10	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背。	READY
9163	9163	Pickup	Pickup D21	D21			LOW	Ktype未区分驾驶室与货斗长度。	PENDING: D21 Pickup CAB/BED分支未闭合
9165	9165	Pickup	Pickup D21	D21			LOW	Ktype未区分驾驶室与货斗长度。	PENDING: D21 Pickup CAB/BED分支未闭合
9168	9168	MPV	Hijet		5		LOW	Bus车身长度与车顶高度待确认。	PENDING: Hijet Bus尺寸组缺失
9169	9169	Van	Hijet		5		LOW	Van车身长度与车顶高度待确认。	PENDING: Hijet Van尺寸组缺失
9171	9171	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9172	9172	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9173	9173	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9174	9174	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9175	9175	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9176	9176	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9177	9177	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9181	9181	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	RS 2000 4x4三门改款外廓。	READY
9183	9183	Wagon	Sierra I				LOW	XR4i通常对应三门掀背，与输入Kombi冲突。	PENDING: VariantName与BodyStyle冲突
9184	9184	Wagon	Sierra II		5	EU-FORD-SIERRA-TURNIER-II-01	MEDIUM	第二代Turnier五门旅行车。	READY
9185	9185	Wagon	Scorpio I		5		MEDIUM	第一代Turnier四驱外廓待闭合。	PENDING: Scorpio I Turnier尺寸组缺失
9186	9186	MPV	Transit VE6	VE6			LOW	Bus覆盖短轴/长轴及不同车顶。	PENDING: Transit VE6 Bus配置未拆分
9187	9187	Van	Transit VE6	VE6			LOW	Kasten覆盖短轴/长轴及不同车顶。	PENDING: Transit VE6 Van配置未拆分
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
```

## 下一步优先处理

1. 优先闭合 Saab 9-3 Sedan、SportCombi、Cabriolet 车身组，一次解决 10 个 Ktype。
2. 批量处理 Clio II 各改款阶段与三门/五门边界，一次解决 5 个 Ktype。
3. 闭合 Mercedes-Benz W163、Alhambra I facelift、Xsara Coupe、Alfa Romeo 159 等乘用车尺寸组。
4. 最后处理 Ducato、Sprinter、Transit、D21 Pickup 的轴距、车顶和 CAB/BED 多分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Citroën Xsara Coupe 的 1.8i 标准外廓，以及 2.0 16V VTS 改款前、改款后三维分支。([汽车数据][1])
* 闭合 Saab 9-3 II SportCombi 改款组，以及 Griffin Sedan、SportCombi、Convertible 三个车身组，解决 7 个 Ktype。([汽车目录][2])
* 闭合 Alfa Romeo 159 939 Sedan 与 Sportwagon 两个车身组。
* 本轮共将 11 个 Ktype 从 `PENDING` 更新为 `READY`，首次创建 9 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：61
* 尚有 PENDING 的 Ktype：39
* READY 映射行：68
* PENDING 映射行：39
* 已确认尺寸组：46
* 跨批次复用尺寸组：35
* 本批累计首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9096	9096	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	前期标准外廓三门Coupe。	READY
9098_prefl	9098	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	HIGH	前期VTS三门Coupe。	READY
9098_facelift	9098	Coupe	Xsara I Phase II	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	HIGH	改款VTS三门Coupe。	READY
9123	9123	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款五门SportCombi。	READY
9124	9124	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款XWD五门SportCombi。	READY
9125	9125	Wagon	9-3 II Griffin		5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	163 PS BioPower XWD对应Griffin五门SportCombi。	READY
9132	9132	Convertible	9-3 II Griffin		2	EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	MEDIUM	160 PS TTiD对应Griffin双门敞篷。	READY
9136	9136	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS BioPower XWD对应Griffin四门轿车。	READY
9137	9137	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	160 PS TTiD对应Griffin四门轿车。	READY
9138	9138	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS XWD对应Griffin四门外廓。	READY
9154	9154	Sedan	159	939	4	EU-ALFA-ROMEO-159-939-SEDAN-4D-01	HIGH	939四门轿车。	READY
9155	9155	Wagon	159	939	5	EU-ALFA-ROMEO-159-939-WAGON-5D-01	HIGH	939五门Sportwagon。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405	Auto-Data Citroën Xsara Coupe 1.8i specifications	https://www.auto-data.net/en/citroen-xsara-coupe-n0-phase-i-1.8-i-90hp-15142
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	4167	1698	1391	Automobile-Catalog Citroën Xsara Coupe VTS specifications	https://www.automobile-catalog.com/car/2000/546770/citroen_xsara_coupe_vts_2_0i_16v.html
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405	Automobile-Catalog Citroën Xsara Coupe VTS specifications	https://www.automobile-catalog.com/car/2001/547535/citroen_xsara_coupe_vts_2_0i_16v.html
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498	Automobile-Catalog Saab 9-3 BioPower SportCombi; Automobile-Catalog Saab 9-3 XWD SportCombi	https://www.automobile-catalog.com/car/2007/3037220/saab_9-3_2_0t_biopower_sportcombi.html;https://www.automobile-catalog.com/car/2008/3037250/saab_9-3_2_0t_xwd_sportcombi.html
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492	Auto-Data Saab 9-3 SportCombi II Griffin specifications	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-griffin-facelift-2011-2.0t-biopower-163hp-xwd-54603
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437	Auto-Data Saab 9-3 Convertible II Griffin specifications	https://www.auto-data.net/en/saab-9-3-convertible-ii-griffin-facelift-2011-1.9-ttid-160hp-54619
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486	Auto-Data Saab 9-3 Griffin BioPower XWD; Auto-Data Saab 9-3 Griffin TTiD	https://www.auto-data.net/en/saab-9-3-sedan-ii-griffin-facelift-2011-2.0t-biopower-163hp-xwd-54577;https://www.auto-data.net/en/saab-9-3-sedan-ii-griffin-facelift-2011-1.9-ttid-160hp-54571
EU-ALFA-ROMEO-159-939-SEDAN-4D-01	4660	1828	1417	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-ALFA-ROMEO-159-939-WAGON-5D-01	4660	1828	1417	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
```

## 下一步优先处理

1. 闭合 Clio II 的门数与 Phase I、II、III/Campus 外廓分支。
2. 处理 Saab 9-3 仍跨越改款前后的 2.8 Turbo Sedan、SportCombi 和 Cabriolet。
3. 闭合 M-Class W163、Alhambra I facelift、Mercedes-Benz S124 和 Xsara 1.8 16V 来源冲突。
4. 最后处理 Sprinter、Ducato、Transit、D21 Pickup 的轴距、车顶及 CAB/BED 多分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-xsara-coupe-n0-phase-i-1.8-i-90hp-15142?utm_source=chatgpt.com "Citroen Xsara Coupe (N0, Phase I) 1.8 i (90 Hp)"
[2]: https://www.automobile-catalog.com/car/2007/3037220/saab_9-3_2_0t_biopower_sportcombi.html?utm_source=chatgpt.com "2007 Saab 9-3 2.0t BioPower SportCombi Specs Review (147 kW / 200 PS / 197 hp) (since Autumn 2007 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Renault Clio II 前期与 Phase III 的三门、五门共四个物理外廓分支。
* Ktype `9040`–`9044` 均覆盖尺寸变化阶段，已移除原无后缀 PENDING 行，各拆分为四条 READY 映射。
* 本轮新增 20 条 READY 映射、4 个尺寸组，消除 5 个 PENDING Ktype。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：66
* 尚有 PENDING 的 Ktype：34
* READY 映射行：88
* PENDING 映射行：34
* 已确认尺寸组：50
* 跨批次复用尺寸组：35
* 本批累计首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9040_pre03_3dr	9040	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9040_pre03_5dr	9040	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9040_post03_3dr	9040	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9040_post03_5dr	9040	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9041_pre03_3dr	9041	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9041_pre03_5dr	9041	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9041_post03_3dr	9041	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9041_post03_5dr	9041	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9042_pre03_3dr	9042	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9042_pre03_5dr	9042	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9042_post03_3dr	9042	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9042_post03_5dr	9042	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9043_pre03_3dr	9043	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9043_pre03_5dr	9043	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9043_post03_3dr	9043	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9043_post03_5dr	9043	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9044_pre03_3dr	9044	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9044_pre03_5dr	9044	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9044_post03_3dr	9044	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9044_post03_5dr	9044	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	3773	1640	1417	Auto-Data Renault Clio II Phase I 3-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-i-3-door-1.2-58hp-46358
EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	3773	1640	1417	Auto-Data Renault Clio II Phase I 5-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-i-5-door-1.2-58hp-10417
EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	3811	1639	1417	Auto-Data Renault Clio II Phase III 3-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-iii-2003-3-door-1.2-60hp-46398
EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	3811	1639	1417	Auto-Data Renault Clio II Phase III 5-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-iii-2003-5-door-1.2-16v-75hp-quickshift-46389
```

## 下一步优先处理

1. 闭合 Mercedes-Benz M-Class W163 的改款前、改款后及版本高度分支。
2. 处理剩余 Saab 9-3 Sedan、SportCombi、Cabriolet 的阶段分支。
3. 集中解决 Alhambra I facelift、S124、Alfa Romeo SZ、Jazz III Hybrid。
4. 随后处理 Ducato、Sprinter、Transit 和 Nissan D21 的轴距、车顶及 CAB/BED 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-clio-ii-phase-i-5-door-1.2-58hp-10417?utm_source=chatgpt.com "Renault Clio II (Phase I) 5-door 1.2 (58 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 M-Class W163 的 ML 320 改款前、改款后分支及 ML 230 外廓，共解决 2 个 Ktype。([汽车数据][1])
* 闭合 Alhambra I facelift、Mercedes-Benz S124 220 TE 两个尺寸组。([汽车目录][2])
* 将 Xsara 1.8i 16V 关联到本批已建立的前期标准 Coupe 尺寸组。
* 闭合 Saab 9-3 II facelift Sedan，以及改款前 Sedan、SportCombi、Convertible 外廓，共解决 4 个 Ktype。([汽车数据][3])
* 本轮共消除 9 个 PENDING Ktype，首次创建 9 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：75
* 尚有 PENDING 的 Ktype：25
* READY 映射行：98
* PENDING 映射行：25
* 已确认尺寸组：59
* 跨批次复用尺寸组：35
* 本批累计首次创建尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9037_prefl	9037	SUV	M-Class W163	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-PREFL-01	HIGH	ML 320改款前外廓。	READY
9037_facelift	9037	SUV	M-Class W163 facelift	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-FACELIFT-01	HIGH	ML 320改款后外廓。	READY
9038	9038	SUV	M-Class W163	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML230-PREFL-01	HIGH	ML 230改款前外廓。	READY
9048_facelift	9048	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-FACELIFT-01	HIGH	7M改款五门MPV。	READY
9097	9097	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	前期标准外廓三门Coupe。	READY
9099	9099	Wagon	124 Series	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-5D-01	HIGH	S124五门旅行车。	READY
9115	9115	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	改款四门XWD轿车。	READY
9116	9116	Sedan	9-3 II		4	EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	MEDIUM	改款前四门V6轿车。	READY
9128	9128	Wagon	9-3 II		5	EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	HIGH	改款前五门V6 SportCombi。	READY
9131	9131	Convertible	9-3 II		2	EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	MEDIUM	改款前双门V6敞篷。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-PREFL-01	4587	1833	1820	Auto-Data Mercedes-Benz M-Class W163 ML 320 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-ml-320-v6-218hp-4matic-5g-tronic-12770
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-FACELIFT-01	4638	1840	1820	Auto-Data Mercedes-Benz M-Class W163 facelift ML 320 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-facelift-2001-ml-320-v6-218hp-4matic-5g-tronic-54500
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML230-PREFL-01	4587	1833	1802	Auto-Data Mercedes-Benz M-Class W163 ML 230 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-ml-230-150hp-4matic-12767
EU-SEAT-ALHAMBRA-I-7M-MPV-FACELIFT-01	4634	1810	1730	Automobile-Catalog SEAT Alhambra I facelift specifications	https://www.automobile-catalog.com/car/2008/3071810/seat_alhambra_2_0_tdi_140.html
EU-MERCEDES-BENZ-124-S124-WAGON-5D-01	4765	1740	1489	Auto-Data Mercedes-Benz S124 220 TE specifications	https://www.auto-data.net/en/mercedes-benz-s124-facelift-1989-220-te-150hp-12669
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466	Auto-Data Saab 9-3 Sedan II facelift generation specifications	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-generation-7157
EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	4635	1762	1466	Auto-Data Saab 9-3 Sedan II 2.8 Turbo V6 specifications	https://www.auto-data.net/en/saab-9-3-sedan-ii-2.8-turbo-v6-250hp-11921
EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	4654	1782	1507	Auto-Data Saab 9-3 SportCombi II 2.8 V6 specifications	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-2.8-i-v6-24v-230hp-11944
EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	4635	1762	1434	Auto-Data Saab 9-3 Convertible II 2.8T V6 specifications	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.8t-v6-250hp-11952
```

## 下一步优先处理

1. 集中闭合 Suzuki SX4、Alfa Romeo SZ、Honda Jazz III Hybrid、Hyundai Grand Santa Fe 和 Astra J 等单一乘用车尺寸组。
2. 处理 W463 封闭式、Korando 开放式、BX Break 和 Astra H Caravan 的物理分支边界。
3. 最后拆分 Sprinter、Ducato、Transit、Nissan D21 与 Hijet 的轴距、车顶、CAB/BED 配置。
4. 单独解决 Sierra `9183` 的 VariantName 与 BodyStyle 冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-m-class-w163-ml-320-v6-218hp-4matic-5g-tronic-12770 "Mercedes-Benz M-class (W163) ML 320 V6 (218 Hp) 4MATIC 5G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2008/3071810/seat_alhambra_2_0_tdi_140.html?utm_source=chatgpt.com "2008 Seat Alhambra 2.0 TDI (140) Specs Review (103 kW / ..."
[3]: https://www.auto-data.net/en/saab-9-3-sedan-ii-2.8-turbo-v6-250hp-11921 "2005 Saab 9-3 Sedan II 2.8 Turbo V6 (250 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Alfa Romeo SZ、Honda Jazz Hybrid、Hyundai Grand Santa Fe 和 Opel Astra J 五门掀背四个尺寸组。([汽车数据][1])
* Ktype `9159` 的生产年月、69 hp LPG 和 `169CXF1A` 边界对应 Panda II 169，复用已有 Panda II 标准五门尺寸组；Astra H Caravan 前期与后期外廓均为 `4515×1753×1500 mm`，复用已有尺寸组。([Auto Doc][2])
* 本轮将 6 个 Ktype 从 `PENDING` 更新为 `READY`，首次创建 4 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：81
* 尚有 PENDING 的 Ktype：19
* READY 映射行：104
* PENDING 映射行：19
* 已确认尺寸组：65
* 跨批次复用尺寸组：37
* 本批累计首次创建尺寸组：28
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9105	9105	Coupe	SZ	ES30	2	EU-ALFA-ROMEO-SZ-ES30-COUPE-2D-01	HIGH	ES30双门Coupe。	READY
9114	9114	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HYBRID-HATCHBACK-5D-01	HIGH	GE五门Hybrid外廓。	READY
9135	9135	SUV	Grand Santa Fe	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-NC-SUV-5D-01	HIGH	NC长轴五门SUV。	READY
9156	9156	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	Astra H五门Caravan外廓。	READY
9159	9159	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-01	HIGH	169五门LPG版本。	READY
9160	9160	Hatchback	Astra J		5	EU-OPEL-ASTRA-J-HATCHBACK-5D-01	HIGH	Astra J五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-SZ-ES30-COUPE-2D-01	4060	1730	1310	Auto-Data Alfa Romeo SZ specifications	https://www.auto-data.net/en/alfa-romeo-sz-generation-402
EU-HONDA-JAZZ-III-GE-HYBRID-HATCHBACK-5D-01	3900	1695	1525	Honda News Europe 2011 Honda Jazz technical specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/1523/honda-jazz-3
EU-HYUNDAI-GRAND-SANTA-FE-NC-SUV-5D-01	4915	1885	1695	Automobile-Catalog 2013 Hyundai Grand Santa Fe 2.2 CRDi 4WD specifications	https://www.automobile-catalog.com/car/2013/2311055/hyundai_grand_santa_fe_2_2_crdi_4wd.html
EU-OPEL-ASTRA-J-HATCHBACK-5D-01	4419	1814	1510	Auto-Data Opel Astra J 1.4 Turbo specifications	https://www.auto-data.net/en/opel-astra-j-1.4-turbo-120hp-16961
```

## 下一步优先处理

1. 处理 Citroën BX Break、W463 封闭式和 Korando 开放式等已有候选分支。
2. 闭合 Suzuki SX4、Daihatsu Hijet Bus/Van、Ford Scorpio I Turnier。
3. 集中拆分 Sprinter、Ducato、Transit 和 Nissan D21 的轴距、车顶及 CAB/BED 配置。
4. 最后解决 Sierra `9183` 的 VariantName 与 BodyStyle 冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/alfa-romeo-sz-generation-402 "Alfa Romeo SZ | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-doc.ie/car-parts/fuel-filter-10361/fiat/panda/panda-169/9159-1-2-lpg-169cxf1a?srsltid=AfmBOoofzH9mLOR3T_T-7hntnLjIKPcpx22JWt2wXrFfYoqMkTXMhzJr&utm_source=chatgpt.com "Fiat Panda Mk2 1.2 LPG Fuel filter (69 hp Petrol/Liquified ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Suzuki SX4 1.6 VVT 4×4、Citroën BX Break 19 CAT、BX Break 14、Nissan Prairie 2.4 4×4、Ford Sierra Turnier 2.8 XR4i 和 Scorpio Turnier 2.9i 4×4，共消除 6 个 PENDING Ktype。([汽车目录][1])
* BX 两个 Ktype 与 Sierra Turnier 直接复用现有尺寸组。
* 本轮首次创建 SX4、Prairie 4×4、Scorpio 4×4 三个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：87
* 尚有 PENDING 的 Ktype：13
* READY 映射行：110
* PENDING 映射行：13
* 已确认尺寸组：71
* 跨批次复用尺寸组：40
* 本批累计首次创建尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9086	9086	Hatchback	SX4 I facelift	RW416	5	EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-5D-4X4-01	HIGH	五门四驱改款外廓。	READY
9108	9108	Wagon	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH	Phase II标准高度五门Break。	READY
9110	9110	Wagon	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	HIGH	14系列后期低车高五门Break。	READY
9119	9119	MPV	Prairie M11	M11	4	EU-NISSAN-PRAIRIE-M11-MPV-4D-4X4-01	HIGH	M11四驱MPV外廓。	READY
9183	9183	Wagon	Sierra Turnier I	BNC	5	EU-FORD-SIERRA-TURNIER-I-01	HIGH	BNC五门旅行车。	READY
9185	9185	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-5D-4X4-01	HIGH	GGE五门四驱旅行车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-5D-4X4-01	4150	1755	1620	Automobile-Catalog Suzuki SX4 1.6 VVT i-AWD specifications	https://www.automobile-catalog.com/car/2012/3409175/suzuki_sx4_1_6_vvt_i-awd.html
EU-NISSAN-PRAIRIE-M11-MPV-4D-4X4-01	4360	1690	1660	AutoData24 Nissan Prairie M11 2.4 i 4X4 specifications	https://autodata24.com/nissan/prairie/prairie-m11/24-i-4x4-133-hp/details
EU-FORD-SCORPIO-I-GGE-WAGON-5D-4X4-01	4744	1760	1490	Auto-Data Ford Scorpio I Turnier GGE 2.9i 4x4 specifications	https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-2.9i-145hp-4x4-8187
```

## 下一步优先处理

1. 闭合 W463 G 320 封闭式短轴、长轴物理分支。
2. 闭合 SsangYong/Daewoo Korando KJ 开放式和 Daihatsu Hijet Bus/Van。
3. 集中拆分 Sprinter、Ducato、Transit 的轴距与车顶分支。
4. 最后处理 Nissan D21 Pickup 的驾驶室和货斗分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2012/3409175/suzuki_sx4_1_6_vvt_i-awd.html?utm_source=chatgpt.com "2012 Suzuki SX4 1.6 VVT i-AWD (man. 5)"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* Mercedes-Benz 官方资料确认 G 320 W463 同时存在三门短轴和五门长轴封闭式车身；两阶段尺寸一致，因此 Ktype `9046` 拆为两个 READY 分支。现有五门缓存组尺寸不一致，未覆盖旧组，改用下一可用序号新建组。([marsClassic][1])
* 闭合 SsangYong Korando 2.3 Cabrio 与 Daewoo Korando 2.9 D Cabrio；品牌切换后的 Daewoo 车身三维不同，分别建组。([Autocentrum.pl][2])
* 闭合 Daihatsu Hijet S85 乘用 Bus 与封闭 Van；两者复用同一微型厢式车外廓尺寸组。1.0 汽油与 1.2 柴油规格均为 `3295×1395×1870 mm`。([ParuVendu][3])
* 本轮消除 5 个 PENDING Ktype，新增 6 条 READY 映射和 5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：92
* 尚有 PENDING 的 Ktype：8
* READY 映射行：116
* PENDING 映射行：8
* 已确认尺寸组：76
* 跨批次复用尺寸组：40
* 本批累计首次创建尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9046_swb	9046	SUV	G-Class W463	463.232	3	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	HIGH	三门短轴封闭式Station Wagon。	READY
9046_lwb	9046	SUV	G-Class W463	463.233	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-03	HIGH	五门长轴封闭式Station Wagon。	READY
9093	9093	Convertible	Korando II	KJ	2	EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	HIGH	SsangYong时期双门开放式车身。	READY
9094	9094	Convertible	Korando	KJ	2	EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-2D-01	HIGH	Daewoo时期双门开放式车身。	READY
9168	9168	MPV	Hijet S85	S85		EU-DAIHATSU-HIJET-S85-MICROVAN-01	MEDIUM	乘用玻璃窗微型厢式车身。	READY
9169	9169	Van	Hijet S85	S85	3	EU-DAIHATSU-HIJET-S85-MICROVAN-01	HIGH	封闭式微型厢式车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	4230	1760	1931	Mercedes-Benz Public Archive G 320 V6 short wheelbase 1997-2000; Mercedes-Benz Public Archive G 320 short wheelbase 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-V6-engine-short-wheelbase-1997---2000.xhtml?oid=191039030;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-short-wheelbase-2001---2006.xhtml?oid=191039049
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-03	4680	1760	1936	Mercedes-Benz Public Archive G 320 V6 long wheelbase 1997-2000; Mercedes-Benz Public Archive G 320 long wheelbase 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-V6-engine-long-wheelbase-1997---2000.xhtml?oid=191039031;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-long-wheelbase-2001---2006.xhtml?oid=191039050
EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	4340	1850	1850	AutoCentrum SsangYong Korando II Cabrio 2.3 specifications	https://www.autocentrum.pl/dane-techniczne/ssangyong/korando/ii/cabrio/silnik-benzynowy-2.3-150km-1997-1999/
EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-2D-01	4260	1855	1840	AutoCentrum Daewoo Korando Cabrio 2.9 D specifications	https://www.autocentrum.pl/dane-techniczne/daewoo/korando/cabrio/silnik-diesla-2.9-d-98km-1999-2001/
EU-DAIHATSU-HIJET-S85-MICROVAN-01	3295	1395	1870	ParuVendu Daihatsu Hijet 1.0ie Van specifications; ParuVendu Daihatsu Hijet 1.2 D Van specifications	https://www.paruvendu.fr/fiches-techniques-utilitaire/daihatsu-hijet/tole-1-0ie-2pl-6-cv-essence/3057906/;https://www.paruvendu.fr/fiches-techniques-utilitaire/daihatsu-hijet/tole-1-2-d-6-cv-diesel/3058322/
```

## 下一步优先处理

1. 拆分 Mercedes-Benz Sprinter 2-T Bus 的轴距和车顶分支。
2. 集中闭合 Fiat Ducato X250 Van、Bus、Pritsche/Fahrgestell。
3. 拆分 Ford Transit VE6 Bus 与 Van 的短轴、长轴及车顶配置。
4. 最后处理 Nissan D21 Pickup 两个 Ktype 的驾驶室和货斗分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-V6-engine-short-wheelbase-1997---2000.xhtml?oid=191039030 "G 320 (V6 engine, short wheelbase), 1997 - 2000"
[2]: https://www.autocentrum.pl/dane-techniczne/ssangyong/korando/ii/cabrio/silnik-benzynowy-2.3-150km-1997-1999/ "Ssangyong Korando II Cabrio 2.3 150KM 110kW 1997-1999 • Dane techniczne • AutoCentrum.pl"
[3]: https://www.paruvendu.fr/fiches-techniques-utilitaire/daihatsu-hijet/tole-1-2-d-6-cv-diesel/3058322/?utm_source=chatgpt.com "Fiche technique utilitaire Daihatsu Hijet TOLE 1.2 D (6 CV) 1996"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Ktype `9186`、`9187` 已确认分别对应 Ford Transit VE64 的 Bus 与 Kasten 2.0 90 PS 类型。([AUTODOC][1])
* 根据已缓存的轴距、车顶和载重级别尺寸组，将两个原 PENDING 基础行替换为 7 条 READY 派生映射。
* 本轮全部复用既有尺寸组，未重新抓取或修改尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：94
* 尚有 PENDING 的 Ktype：6
* READY 映射行：123
* PENDING 映射行：6
* 已确认尺寸组：71
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9186_swb_80-100	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	MEDIUM	短轴80/100载重级别Bus分支。	READY
9186_swb_120	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	MEDIUM	短轴120载重级别Bus分支。	READY
9186_swb_150	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	MEDIUM	短轴150载重级别Bus分支。	READY
9186_lwb_100	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	MEDIUM	长轴100载重级别Bus分支。	READY
9187_swb_lowroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	短轴低顶Kasten分支。	READY
9187_lwb_midroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	长轴中顶Kasten分支。	READY
9187_xlwb_highroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长轴高顶Kasten分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 根据 `902.471`、`902.472` 精确车身代码闭合 Sprinter 210 D Bus 的短轴、长轴和车顶分支。
2. 集中拆分 Ducato X250 Van、Bus、Pritsche/Fahrgestell 的车长、车顶和驾驶室分支。
3. 最后闭合 Nissan D21 两个 Ktype 的 Standard Cab、King Cab、Double Cab 与货斗组合。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/doors-parts-10289/ford/transit/transit-bus-e-1991/9186-2-0?utm_source=chatgpt.com "FORD Transit Mk3 Minibus (VE64) 2.0 Door parts (90 hp Petrol ..."


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* Ktype `9064` 已按明确车身代码拆分为两个分支：`902.471` 为 3000 mm 轴距，`902.472` 为 3550 mm 轴距。([PartSouq][1])
* 两个 Sprinter Bus 外廓已首次闭合；原 `id=9064` 的 PENDING 基础行移除，新增两条 READY 映射。对应 Window Van 外廓分别为 `4835×1933×2350 mm` 和 `5585×1933×2345 mm`。([CarExpert NZ][2])

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：95
* 尚有 PENDING 的 Ktype：5
* READY 映射行：125
* PENDING 映射行：5
* 已确认尺寸组：78
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9064_swb	9064	MPV	Sprinter I	902.471		EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-SWB-01	HIGH	3000 mm轴距Bus分支。	READY
9064_mwb	9064	MPV	Sprinter I	902.472		EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-MWB-01	HIGH	3550 mm轴距Bus分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-SWB-01	4835	1933	2350	Mercedes-Benz EPC via PartSouq; JATO Dynamics 1999 Mercedes-Benz Sprinter Window Van specifications via CarExpert	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0009902104;https://www.carexpert.co.nz/mercedes-benz/sprinter/1999/features-and-specs
EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-MWB-01	5585	1933	2345	Mercedes-Benz EPC via PartSouq; JATO Dynamics 1999 Mercedes-Benz Sprinter Window Van specifications via CarExpert	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0001500224;https://www.carexpert.co.nz/mercedes-benz/sprinter/1999/features-and-specs
```

## 下一步优先处理

1. 集中拆分 Fiat Ducato X250 Kasten、Bus 和 Pritsche/Fahrgestell 的轴距、车长、车顶及驾驶室分支。
2. 最后闭合 Nissan D21 两个 Ktype 的驾驶室与货斗组合。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0009902104&ssd=%24%2AKwHi1sfUlrWluaiWr6DWzrqujomX5unk5ffY66OllpiVnKiL-fTtkJDm5-Do7-S7tqvkr6CyuJGt9v-lob6kurv887u3q7256eHk4-fg9Pir9Pjy6_T1_PO7v6u9ueGC9Pvysrj2s6Wo5ZX0-_KntfazpajyrAAAAADIDq35%24&utm_source=chatgpt.com "BODY SHELL | Mercedes-Benz SPRINTER 210 D,212 D Standard, Japan 902.471 | Parts Catalogs | PartSouq"
[2]: https://www.carexpert.co.nz/mercedes-benz/sprinter/1999/features-and-specs "1999 Mercedes-Benz Sprinter Features & Specs | CarExpert | CarExpert NZ"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Fiat Ducato X250 的 Kasten、Bus 与 Pritsche/Fahrgestell 三个 Ktype。
* `9126` 拆分为八种 L/H 封闭厢式车外廓；`9129` 的 Bus 车身复用对应的八个封闭车身尺寸组。
* `9130` 拆分为五种单排驾驶室底盘和三种双排驾驶室底盘。
* 官方技术表确认 X250 封闭车身的八种长/高组合，以及单排、双排底盘的轴距和外部尺寸；宽度均为不含后视镜的 `2050 mm`。([Stellantis Media][1])
* 本轮消除 3 个 PENDING Ktype，首次创建 15 个尺寸组；已有 `EU-FIAT-DUCATO-X250-VAN-L2H2-01` 直接复用。

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：98
* 尚有 PENDING 的 Ktype：2
* READY 映射行：149
* PENDING 映射行：2
* 已确认尺寸组：93
* 本轮首次创建尺寸组：15
* 剩余 PENDING：`9163`、`9165`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9126_l1h1	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H1-01	MEDIUM	L1H1封闭厢式分支。	READY
9126_l1h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H2-01	MEDIUM	L1H2封闭厢式分支。	READY
9126_l2h1	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H1-01	MEDIUM	L2H1封闭厢式分支。	READY
9126_l2h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	MEDIUM	L2H2封闭厢式分支。	READY
9126_l3h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H2-01	MEDIUM	L3H2封闭厢式分支。	READY
9126_l3h3	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H3-01	MEDIUM	L3H3封闭厢式分支。	READY
9126_l4h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H2-01	MEDIUM	L4H2加长封闭厢式分支。	READY
9126_l4h3	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H3-01	MEDIUM	L4H3加长高顶封闭厢式分支。	READY
9129_l1h1	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H1-01	MEDIUM	L1H1乘用Bus外廓分支。	READY
9129_l1h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H2-01	MEDIUM	L1H2乘用Bus外廓分支。	READY
9129_l2h1	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H1-01	MEDIUM	L2H1乘用Bus外廓分支。	READY
9129_l2h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	MEDIUM	L2H2乘用Bus外廓分支。	READY
9129_l3h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H2-01	MEDIUM	L3H2乘用Bus外廓分支。	READY
9129_l3h3	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H3-01	MEDIUM	L3H3乘用Bus外廓分支。	READY
9129_l4h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H2-01	MEDIUM	L4H2加长乘用Bus外廓分支。	READY
9129_l4h3	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H3-01	MEDIUM	L4H3加长高顶乘用Bus外廓分支。	READY
9130_singlecab_l1	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	MEDIUM	单排驾驶室L1底盘分支。	READY
9130_singlecab_l2	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	MEDIUM	单排驾驶室L2底盘分支。	READY
9130_singlecab_l3	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	MEDIUM	单排驾驶室L3底盘分支。	READY
9130_singlecab_l4	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	MEDIUM	单排驾驶室L4底盘分支。	READY
9130_singlecab_l5	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	MEDIUM	单排驾驶室L5底盘分支。	READY
9130_doublecab_l3	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	MEDIUM	双排驾驶室L3底盘分支。	READY
9130_doublecab_l4	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	MEDIUM	双排驾驶室L4底盘分支。	READY
9130_doublecab_l5	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	MEDIUM	双排驾驶室L5底盘分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-X250-VAN-L1H1-01	4963	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L1H2-01	4963	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L2H1-01	5413	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L3H2-01	5998	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L3H3-01	5998	2050	2764	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L4H2-01	6363	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L4H3-01	6363	2050	2764	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	4908	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	5358	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	5708	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	5943	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	6308	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	5708	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	5943	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	6308	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
```

## 下一步优先处理

闭合最后两个 Nissan D21 Ktype：分别确认早期、后期 2.4 四驱车型的 Regular Cab Regular Bed、Regular Cab Long Bed 与 King Cab 物理分支及改款后宽度口径。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf "Microsoft Word - 110505_FP_NoweDucato_Pl"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8201-8300_ktype_dimension_mapping_final.tsv
- all_8201-8300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 最后两个 Nissan D21 Ktype 已闭合：`9163` 拆分为 Regular Cab 短轴、Regular Cab 长轴和 King Cab 三个前期分支；`9165` 拆分为改款后的 Regular Cab 与 King Cab 两个分支。D21 工厂资料分别列出了对应驾驶室、轴距、车长、无镜车宽和车高，版本时间也与输入的 2.4 4WD、2.4i 12V 4WD 匹配。([Auto Doc][1])
* 当前批次全部 PENDING 已消除。
* 已完成表头、唯一性、引用闭合、尺寸正整数、来源非空及孤立尺寸组检查。

## 当前批次进度

* 输入 Ktype：100
* 完全 READY 的 Ktype：100
* 最终 Ktype 映射行：154
* PENDING：0
* 最终 DIMENSION_GROUP：106
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
9036	9036	Sedan	Passat B5	3B2	4	EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	HIGH	B5前期四门轿车。	READY
9037_prefl	9037	SUV	M-Class W163	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-PREFL-01	HIGH	ML 320改款前外廓。	READY
9037_facelift	9037	SUV	M-Class W163 facelift	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-FACELIFT-01	HIGH	ML 320改款后外廓。	READY
9038	9038	SUV	M-Class W163	W163	5	EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML230-PREFL-01	HIGH	ML 230改款前外廓。	READY
9039_prefl	9039	Wagon	C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	MEDIUM	S202前期旅行车分支。	READY
9039_facelift	9039	Wagon	C-Class W202	S202	5	EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	MEDIUM	S202改款旅行车分支。	READY
9040_pre03_3dr	9040	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9040_pre03_5dr	9040	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9040_post03_3dr	9040	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9040_post03_5dr	9040	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9041_pre03_3dr	9041	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9041_pre03_5dr	9041	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9041_post03_3dr	9041	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9041_post03_5dr	9041	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9042_pre03_3dr	9042	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9042_pre03_5dr	9042	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9042_post03_3dr	9042	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9042_post03_5dr	9042	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9043_pre03_3dr	9043	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9043_pre03_5dr	9043	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9043_post03_3dr	9043	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9043_post03_5dr	9043	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9044_pre03_3dr	9044	Hatchback	Clio II Phase I-II		3	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	MEDIUM	三门前期外廓分支。	READY
9044_pre03_5dr	9044	Hatchback	Clio II Phase I-II		5	EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	MEDIUM	五门前期外廓分支。	READY
9044_post03_3dr	9044	Hatchback	Clio II Phase III		3	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	MEDIUM	三门Phase III外廓分支。	READY
9044_post03_5dr	9044	Hatchback	Clio II Phase III		5	EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	MEDIUM	五门Phase III外廓分支。	READY
9045	9045	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9046_swb	9046	SUV	G-Class W463	463.232	3	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	HIGH	三门短轴封闭式Station Wagon。	READY
9046_lwb	9046	SUV	G-Class W463	463.233	5	EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-03	HIGH	五门长轴封闭式Station Wagon。	READY
9047	9047	Convertible	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	MEDIUM	1997年后宽体敞篷分支。	READY
9048_prefl	9048	MPV	Alhambra I	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	MEDIUM	7M前期分支。	READY
9048_facelift	9048	MPV	Alhambra I facelift	7M	5	EU-SEAT-ALHAMBRA-I-7M-MPV-FACELIFT-01	HIGH	7M改款五门MPV。	READY
9049	9049	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9050	9050	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9051	9051	Hatchback	XM Y4	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH	Y4五门掀背外廓。	READY
9052	9052	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4旅行车外廓。	READY
9053	9053	Wagon	XM Y4	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH	Y4旅行车外廓。	READY
9054	9054	Wagon	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	HIGH	J200五门旅行车。	READY
9055	9055	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9056	9056	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9057	9057	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9058	9058	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9059	9059	Wagon	Polo III	6KV5	5	EU-VW-POLO-III-6KV5-WAGON-5D-01	HIGH	6KV5五门旅行车。	READY
9061	9061	Van	Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	HIGH	三门厢式外廓。	READY
9063_prefl	9063	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	MEDIUM	1U前期五门掀背分支。	READY
9063_facelift	9063	Hatchback	Octavia I	1U2	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	MEDIUM	1U改款五门掀背分支。	READY
9064_swb	9064	MPV	Sprinter I	902.471		EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-SWB-01	HIGH	3000 mm轴距Bus分支。	READY
9064_mwb	9064	MPV	Sprinter I	902.472		EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-MWB-01	HIGH	3550 mm轴距Bus分支。	READY
9065	9065	Sedan	Polo III	6KV	4	EU-VW-POLO-III-6KV-SEDAN-01	HIGH	6KV四门轿车。	READY
9066	9066	Hatchback	Y 840	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH	840三门掀背。	READY
9067	9067	Hatchback	Y 840	840	3	EU-LANCIA-Y-840-HATCHBACK-3D-01	HIGH	840三门掀背。	READY
9073	9073	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2五门旅行车。	READY
9086	9086	Hatchback	SX4 I facelift	RW416	5	EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-5D-4X4-01	HIGH	五门四驱改款外廓。	READY
9087_3dr	9087	Hatchback	Swift IV		3	EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	MEDIUM	三门外廓分支。	READY
9087_5dr	9087	Hatchback	Swift IV		5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	MEDIUM	五门外廓分支。	READY
9090	9090	Wagon	5 Series E39	E39	5	EU-BMW-5-E39-WAGON-01	HIGH	E39 Touring。	READY
9091	9091	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9092	9092	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH	E46四门轿车。	READY
9093	9093	Convertible	Korando II	KJ	2	EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	HIGH	SsangYong时期双门开放式车身。	READY
9094	9094	Convertible	Korando	KJ	2	EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-2D-01	HIGH	Daewoo时期双门开放式车身。	READY
9095	9095	MPV	Shuttle I	RA1	5	EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	HIGH	RA1五门MPV。	READY
9096	9096	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	前期标准外廓三门Coupe。	READY
9097	9097	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	HIGH	前期标准外廓三门Coupe。	READY
9098_prefl	9098	Coupe	Xsara I Phase I	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	HIGH	前期VTS三门Coupe。	READY
9098_facelift	9098	Coupe	Xsara I Phase II	N0	3	EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	HIGH	改款VTS三门Coupe。	READY
9099	9099	Wagon	124 Series	S124	5	EU-MERCEDES-BENZ-124-S124-WAGON-5D-01	HIGH	S124五门旅行车。	READY
9102	9102	Sedan	A8 D2	D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	D2前期四门轿车。	READY
9103	9103	Sedan	A8 D2	D2	4	EU-AUDI-A8-D2-SEDAN-PREFL-01	HIGH	D2前期四门轿车。	READY
9105	9105	Coupe	SZ	ES30	2	EU-ALFA-ROMEO-SZ-ES30-COUPE-2D-01	HIGH	ES30双门Coupe。	READY
9107	9107	Sedan	Seville II		4	EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	HIGH	第二代Seville四门轿车。	READY
9108	9108	Wagon	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH	Phase II标准高度五门Break。	READY
9110	9110	Wagon	BX I Phase II	XB	5	EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	HIGH	14系列后期低车高五门Break。	READY
9112	9112	Wagon	XM Y3	Y3	5	EU-CITROEN-XM-Y3-WAGON-01	HIGH	Y3五门旅行车。	READY
9113	9113	Hatchback	Swift IV		5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	HIGH	五门四驱外廓。	READY
9114	9114	Hatchback	Jazz III	GE	5	EU-HONDA-JAZZ-III-GE-HYBRID-HATCHBACK-5D-01	HIGH	GE五门Hybrid外廓。	READY
9115	9115	Sedan	9-3 II facelift		4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH	改款四门XWD轿车。	READY
9116	9116	Sedan	9-3 II		4	EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	MEDIUM	改款前四门V6轿车。	READY
9119	9119	MPV	Prairie M11	M11	4	EU-NISSAN-PRAIRIE-M11-MPV-4D-4X4-01	HIGH	M11四驱MPV外廓。	READY
9122	9122	Coupe	Daytona		3	EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	MEDIUM	同代三门Daytona外廓复用。	READY
9123	9123	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款五门SportCombi。	READY
9124	9124	Wagon	9-3 II facelift		5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款XWD五门SportCombi。	READY
9125	9125	Wagon	9-3 II Griffin		5	EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	MEDIUM	163 PS BioPower XWD对应Griffin五门SportCombi。	READY
9126_l1h1	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H1-01	MEDIUM	L1H1封闭厢式分支。	READY
9126_l1h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H2-01	MEDIUM	L1H2封闭厢式分支。	READY
9126_l2h1	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H1-01	MEDIUM	L2H1封闭厢式分支。	READY
9126_l2h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	MEDIUM	L2H2封闭厢式分支。	READY
9126_l3h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H2-01	MEDIUM	L3H2封闭厢式分支。	READY
9126_l3h3	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H3-01	MEDIUM	L3H3封闭厢式分支。	READY
9126_l4h2	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H2-01	MEDIUM	L4H2加长封闭厢式分支。	READY
9126_l4h3	9126	Van	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H3-01	MEDIUM	L4H3加长高顶封闭厢式分支。	READY
9128	9128	Wagon	9-3 II		5	EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	HIGH	改款前五门V6 SportCombi。	READY
9129_l1h1	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H1-01	MEDIUM	L1H1乘用Bus外廓分支。	READY
9129_l1h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L1H2-01	MEDIUM	L1H2乘用Bus外廓分支。	READY
9129_l2h1	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H1-01	MEDIUM	L2H1乘用Bus外廓分支。	READY
9129_l2h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L2H2-01	MEDIUM	L2H2乘用Bus外廓分支。	READY
9129_l3h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H2-01	MEDIUM	L3H2乘用Bus外廓分支。	READY
9129_l3h3	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L3H3-01	MEDIUM	L3H3乘用Bus外廓分支。	READY
9129_l4h2	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H2-01	MEDIUM	L4H2加长乘用Bus外廓分支。	READY
9129_l4h3	9129	MPV	Ducato X250	X250		EU-FIAT-DUCATO-X250-VAN-L4H3-01	MEDIUM	L4H3加长高顶乘用Bus外廓分支。	READY
9130_singlecab_l1	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	MEDIUM	单排驾驶室L1底盘分支。	READY
9130_singlecab_l2	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	MEDIUM	单排驾驶室L2底盘分支。	READY
9130_singlecab_l3	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	MEDIUM	单排驾驶室L3底盘分支。	READY
9130_singlecab_l4	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	MEDIUM	单排驾驶室L4底盘分支。	READY
9130_singlecab_l5	9130	Pickup	Ducato X250	X250	2	EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	MEDIUM	单排驾驶室L5底盘分支。	READY
9130_doublecab_l3	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	MEDIUM	双排驾驶室L3底盘分支。	READY
9130_doublecab_l4	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	MEDIUM	双排驾驶室L4底盘分支。	READY
9130_doublecab_l5	9130	Pickup	Ducato X250	X250	4	EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	MEDIUM	双排驾驶室L5底盘分支。	READY
9131	9131	Convertible	9-3 II		2	EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	MEDIUM	改款前双门V6敞篷。	READY
9132	9132	Convertible	9-3 II Griffin		2	EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	MEDIUM	160 PS TTiD对应Griffin双门敞篷。	READY
9135	9135	SUV	Grand Santa Fe	NC	5	EU-HYUNDAI-GRAND-SANTA-FE-NC-SUV-5D-01	HIGH	NC长轴五门SUV。	READY
9136	9136	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS BioPower XWD对应Griffin四门轿车。	READY
9137	9137	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	160 PS TTiD对应Griffin四门轿车。	READY
9138	9138	Sedan	9-3 II Griffin		4	EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	MEDIUM	163 PS XWD对应Griffin四门外廓。	READY
9139	9139	Hatchback	Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH	H08五门掀背。	READY
9140	9140	Hatchback	Agila B	H08	5	EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	HIGH	H08五门掀背。	READY
9143	9143	Sedan	Corsica I		4	EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	HIGH	第一代四门轿车。	READY
9147	9147	Wagon	Sunny Y10	Y10	5	EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	HIGH	Y10五门四驱旅行车。	READY
9148	9148	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	HIGH	B12五门四驱旅行车。	READY
9154	9154	Sedan	159	939	4	EU-ALFA-ROMEO-159-939-SEDAN-4D-01	HIGH	939四门轿车。	READY
9155	9155	Wagon	159	939	5	EU-ALFA-ROMEO-159-939-WAGON-5D-01	HIGH	939五门Sportwagon。	READY
9156	9156	Wagon	Astra H		5	EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	HIGH	Astra H五门Caravan外廓。	READY
9157_3dr	9157	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	MEDIUM	L08三门分支。	READY
9157_5dr	9157	Hatchback	Corsa D	L68	5	EU-OPEL-CORSA-D-HATCHBACK-5D-01	MEDIUM	L68五门分支。	READY
9158_3dr	9158	Hatchback	Grande Punto 199	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	MEDIUM	三门分支。	READY
9158_5dr	9158	Hatchback	Grande Punto 199	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	MEDIUM	五门分支。	READY
9159	9159	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-01	HIGH	169五门LPG版本。	READY
9160	9160	Hatchback	Astra J		5	EU-OPEL-ASTRA-J-HATCHBACK-5D-01	HIGH	Astra J五门掀背外廓。	READY
9161	9161	Sedan	Primera I P10	P10	4	EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	HIGH	P10四门轿车。	READY
9162	9162	Hatchback	Primera I P10	P10	5	EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	HIGH	P10五门掀背。	READY
9163_regcab_swb	9163	Pickup	Pickup D21	D21	2	EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-SWB-PREFL-01	MEDIUM	Regular Cab短轴短货斗分支。	READY
9163_regcab_lwb	9163	Pickup	Pickup D21	D21	2	EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-LWB-PREFL-01	MEDIUM	Regular Cab长轴长货斗分支。	READY
9163_kingcab_swb	9163	Pickup	Pickup D21	D21	2	EU-NISSAN-PICKUP-D21-PICKUP-KINGCAB-SWB-PREFL-01	MEDIUM	King Cab长轴短货斗分支。	READY
9165_regcab_swb	9165	Pickup	Pickup D21 facelift	D21	2	EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-SWB-FACELIFT-01	MEDIUM	Regular Cab短轴短货斗分支。	READY
9165_kingcab_swb	9165	Pickup	Pickup D21 facelift	D21	2	EU-NISSAN-PICKUP-D21-PICKUP-KINGCAB-SWB-FACELIFT-01	MEDIUM	King Cab长轴短货斗分支。	READY
9168	9168	MPV	Hijet S85	S85		EU-DAIHATSU-HIJET-S85-MICROVAN-01	MEDIUM	乘用玻璃窗微型厢式车身。	READY
9169	9169	Van	Hijet S85	S85	3	EU-DAIHATSU-HIJET-S85-MICROVAN-01	HIGH	封闭式微型厢式车身。	READY
9171	9171	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9172	9172	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9173	9173	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9174	9174	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9175	9175	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9176	9176	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9177	9177	Van	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-01	HIGH	三门厢式车与L08三门外廓一致。	READY
9181	9181	Hatchback	Escort VI		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	RS 2000 4x4三门改款外廓。	READY
9183	9183	Wagon	Sierra Turnier I	BNC	5	EU-FORD-SIERRA-TURNIER-I-01	HIGH	BNC五门旅行车。	READY
9184	9184	Wagon	Sierra II		5	EU-FORD-SIERRA-TURNIER-II-01	MEDIUM	第二代Turnier五门旅行车。	READY
9185	9185	Wagon	Scorpio I Turnier	GGE	5	EU-FORD-SCORPIO-I-GGE-WAGON-5D-4X4-01	HIGH	GGE五门四驱旅行车。	READY
9186_swb_80-100	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	MEDIUM	短轴80/100载重级别Bus分支。	READY
9186_swb_120	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	MEDIUM	短轴120载重级别Bus分支。	READY
9186_swb_150	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	MEDIUM	短轴150载重级别Bus分支。	READY
9186_lwb_100	9186	MPV	Transit VE64	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	MEDIUM	长轴100载重级别Bus分支。	READY
9187_swb_lowroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	短轴低顶Kasten分支。	READY
9187_lwb_midroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	长轴中顶Kasten分支。	READY
9187_xlwb_highroof	9187	Van	Transit VE64	VE64		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长轴高顶Kasten分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8201-8300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B5-3B2-SEDAN-PREFL-01	4675	1740	1459	Auto-Data Volkswagen Passat B5 2.3 VR5 specifications	https://www.auto-data.net/en/volkswagen-passat-b5-2.3-vr5-150hp-8921
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-PREFL-01	4587	1833	1820	Auto-Data Mercedes-Benz M-Class W163 ML 320 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-ml-320-v6-218hp-4matic-5g-tronic-12770
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML320-FACELIFT-01	4638	1840	1820	Auto-Data Mercedes-Benz M-Class W163 facelift ML 320 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-facelift-2001-ml-320-v6-218hp-4matic-5g-tronic-54500
EU-MERCEDES-BENZ-M-KLASSE-W163-SUV-ML230-PREFL-01	4587	1833	1802	Auto-Data Mercedes-Benz M-Class W163 ML 230 specifications	https://www.auto-data.net/en/mercedes-benz-m-class-w163-ml-230-150hp-4matic-12767
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 C 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-c-200-kompressor-192hp-12630
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460	Auto-Data Mercedes-Benz C-Class T-modell S202 facelift C 200 Kompressor specifications	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s202-facelift-1997-c-200-kompressor-192hp-44215
EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-3D-01	3773	1640	1417	Auto-Data Renault Clio II Phase I 3-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-i-3-door-1.2-58hp-46358
EU-RENAULT-CLIO-II-PHASE-I-II-HATCHBACK-5D-01	3773	1640	1417	Auto-Data Renault Clio II Phase I 5-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-i-5-door-1.2-58hp-10417
EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-3D-01	3811	1639	1417	Auto-Data Renault Clio II Phase III 3-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-iii-2003-3-door-1.2-60hp-46398
EU-RENAULT-CLIO-II-PHASE-III-HATCHBACK-5D-01	3811	1639	1417	Auto-Data Renault Clio II Phase III 5-door specifications	https://www.auto-data.net/en/renault-clio-ii-phase-iii-2003-5-door-1.2-16v-75hp-quickshift-46389
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan E46 320d specifications	https://www.auto-data.net/en/bmw-3-series-sedan-e46-320d-136hp-9980
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-3D-01	4230	1760	1931	Mercedes-Benz Public Archive G 320 V6 short wheelbase 1997-2000; Mercedes-Benz Public Archive G 320 short wheelbase 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-V6-engine-short-wheelbase-1997---2000.xhtml?oid=191039030;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-short-wheelbase-2001---2006.xhtml?oid=191039049
EU-MERCEDES-BENZ-G-KLASSE-W463-SUV-5D-03	4680	1760	1936	Mercedes-Benz Public Archive G 320 V6 long wheelbase 1997-2000; Mercedes-Benz Public Archive G 320 long wheelbase 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-V6-engine-long-wheelbase-1997---2000.xhtml?oid=191039031;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/G-320-long-wheelbase-2001---2006.xhtml?oid=191039050
EU-MERCEDES-BENZ-G-KLASSE-W463-CABRIO-WIDE-01	4275	1760	1941	Auto-Data Mercedes-Benz G-Class Cabriolet W463 G 320 specifications	https://www.auto-data.net/en/mercedes-benz-g-class-cabriolet-w463-facelift-2000-g-320-v6-215hp-4matic-automatic-42207
EU-SEAT-ALHAMBRA-I-7M-MPV-PREFL-01	4620	1810	1730	Automobile-Catalog 1998 SEAT Alhambra 1.8 T 20V specifications	https://www.automobile-catalog.com/car/1998/3071420/seat_alhambra_1_8_t_20v.html
EU-SEAT-ALHAMBRA-I-7M-MPV-FACELIFT-01	4634	1810	1730	Automobile-Catalog SEAT Alhambra I facelift specifications	https://www.automobile-catalog.com/car/2008/3071810/seat_alhambra_2_0_tdi_140.html
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396	Auto-Data Citroën XM Y4 specifications	https://www.auto-data.net/en/citroen-xm-y4-generation-3317
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467	Auto-Data Citroën XM Break Y4 specifications	https://www.auto-data.net/en/citroen-xm-break-y4-generation-3318
EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	4580	1725	1460	Auto-Data Chevrolet Lacetti Wagon specifications	https://www.auto-data.net/en/chevrolet-lacetti-wagon-generation-3151
EU-VW-POLO-III-6KV5-WAGON-5D-01	4137	1640	1433	Auto-Data Volkswagen Polo III Variant specifications	https://www.auto-data.net/en/volkswagen-polo-iii-variant-generation-1858
EU-RENAULT-CLIO-III-X85-VAN-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door specifications	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-1.5-dci-86hp-25045
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429	Auto-Data Škoda Octavia I Tour 1.9 TDI specifications	https://www.auto-data.net/en/skoda-octavia-i-tour-1.9-tdi-110hp-14249
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431	Auto-Data Škoda Octavia I Tour facelift 1.9 TDI specifications	https://www.auto-data.net/en/skoda-octavia-i-tour-facelift-2000-1.9-tdi-110hp-56458
EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-SWB-01	4835	1933	2350	Mercedes-Benz EPC via PartSouq; JATO Dynamics 1999 Mercedes-Benz Sprinter Window Van specifications via CarExpert	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0009902104;https://www.carexpert.co.nz/mercedes-benz/sprinter/1999/features-and-specs
EU-MERCEDES-BENZ-SPRINTER-I-B901-B902-BUS-MWB-01	5585	1933	2345	Mercedes-Benz EPC via PartSouq; JATO Dynamics 1999 Mercedes-Benz Sprinter Window Van specifications via CarExpert	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0001500224;https://www.carexpert.co.nz/mercedes-benz/sprinter/1999/features-and-specs
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414	Auto-Data Volkswagen Polo III Classic 1.7 SDI specifications	https://www.auto-data.net/en/volkswagen-polo-iii-classic-6n-1.7-sdi-60hp-8449
EU-LANCIA-Y-840-HATCHBACK-3D-01	3725	1690	1440	Auto-Data Lancia Y 840 specifications	https://www.auto-data.net/en/lancia-y-840-generation-1166
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420	Auto-Data Citroën Xantia Break X2 specifications	https://www.auto-data.net/en/citroen-xantia-break-x2-generation-3305
EU-SUZUKI-SX4-I-FACELIFT-HATCHBACK-5D-4X4-01	4150	1755	1620	Automobile-Catalog Suzuki SX4 1.6 VVT i-AWD specifications	https://www.automobile-catalog.com/car/2012/3409175/suzuki_sx4_1_6_vvt_i-awd.html
EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510	Auto-Data Suzuki Swift 2010 specifications	https://www.auto-data.net/en/suzuki-swift-model-1906
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	Auto-Data Suzuki Swift 2010 specifications	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133
EU-BMW-5-E39-WAGON-01	4805	1800	1440	Auto-Data BMW 5 Series Touring E39 specifications	https://www.auto-data.net/en/bmw-5-series-touring-e39-generation-1978
EU-SSANGYONG-KORANDO-II-KJ-CONVERTIBLE-2D-01	4340	1850	1850	AutoCentrum SsangYong Korando II Cabrio 2.3 specifications	https://www.autocentrum.pl/dane-techniczne/ssangyong/korando/ii/cabrio/silnik-benzynowy-2.3-150km-1997-1999/
EU-DAEWOO-KORANDO-KJ-CONVERTIBLE-2D-01	4260	1855	1840	AutoCentrum Daewoo Korando Cabrio 2.9 D specifications	https://www.autocentrum.pl/dane-techniczne/daewoo/korando/cabrio/silnik-diesla-2.9-d-98km-1999-2001/
EU-HONDA-SHUTTLE-I-RA1-MPV-5D-01	4750	1790	1640	EngineInDetail Honda Shuttle specifications	https://www.engineindetail.com/cars/honda/shuttle
EU-CITROEN-XSARA-I-N0-COUPE-3D-STD-PREFL-01	4167	1698	1405	Auto-Data Citroën Xsara Coupe 1.8i specifications	https://www.auto-data.net/en/citroen-xsara-coupe-n0-phase-i-1.8-i-90hp-15142
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-PREFL-01	4167	1698	1391	Automobile-Catalog Citroën Xsara Coupe VTS specifications	https://www.automobile-catalog.com/car/2000/546770/citroen_xsara_coupe_vts_2_0i_16v.html
EU-CITROEN-XSARA-I-N0-COUPE-3D-VTS-FACELIFT-01	4188	1705	1405	Automobile-Catalog Citroën Xsara Coupe VTS specifications	https://www.automobile-catalog.com/car/2001/547535/citroen_xsara_coupe_vts_2_0i_16v.html
EU-MERCEDES-BENZ-124-S124-WAGON-5D-01	4765	1740	1489	Auto-Data Mercedes-Benz S124 220 TE specifications	https://www.auto-data.net/en/mercedes-benz-s124-facelift-1989-220-te-150hp-12669
EU-AUDI-A8-D2-SEDAN-PREFL-01	5034	1880	1440	Auto-Data Audi A8 D2 2.8 specifications	https://www.auto-data.net/en/audi-a8-d2-4d-2.8-v6-12v-174hp-4835
EU-ALFA-ROMEO-SZ-ES30-COUPE-2D-01	4060	1730	1310	Auto-Data Alfa Romeo SZ specifications	https://www.auto-data.net/en/alfa-romeo-sz-generation-402
EU-CADILLAC-SEVILLE-II-SEDAN-4D-01	5202	1801	1379	Carsales Cadillac Seville specifications	https://www.carsales.com.au/research/cadillac/seville/1983/no-badge/
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431	Auto-Data Citroën BX I Break Phase II specifications	https://www.auto-data.net/en/citroen-bx-i-break-phase-ii-1987-1.8-trd-turbo-90hp-15281
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410	Automobile-Catalog Citroën BX Break 14 TE CAT specifications	https://www.automobile-catalog.com/car/1990/539390/citroen_bx_break_14_te_cat.html
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1467	Auto-Data Citroën XM model specifications	https://www.auto-data.net/en/citroen-xm-model-1688
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535	Automobile-Catalog Suzuki Swift 1.2 4x4 specifications	https://www.automobile-catalog.com/car/2011/3405905/suzuki_swift_1_2_4x4.html
EU-HONDA-JAZZ-III-GE-HYBRID-HATCHBACK-5D-01	3900	1695	1525	Honda News Europe 2011 Honda Jazz technical specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/1523/honda-jazz-3
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1466	Auto-Data Saab 9-3 Sedan II facelift generation specifications	https://www.auto-data.net/en/saab-9-3-sedan-ii-facelift-2007-generation-7157
EU-SAAB-9-3-II-PREFL-SEDAN-4D-01	4635	1762	1466	Auto-Data Saab 9-3 Sedan II 2.8 Turbo V6 specifications	https://www.auto-data.net/en/saab-9-3-sedan-ii-2.8-turbo-v6-250hp-11921
EU-NISSAN-PRAIRIE-M11-MPV-4D-4X4-01	4360	1690	1660	AutoData24 Nissan Prairie M11 2.4 i 4X4 specifications	https://autodata24.com/nissan/prairie/prairie-m11/24-i-4x4-133-hp/details
EU-CHRYSLER-DAYTONA-SHELBY-G-COUPE-3D-01	4560	1760	1285	Auto-Data Chrysler Daytona Shelby specifications	https://www.auto-data.net/en/chrysler-daytona-shelby-generation-3230
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1498	Automobile-Catalog Saab 9-3 BioPower SportCombi; Automobile-Catalog Saab 9-3 XWD SportCombi	https://www.automobile-catalog.com/car/2007/3037220/saab_9-3_2_0t_biopower_sportcombi.html;https://www.automobile-catalog.com/car/2008/3037250/saab_9-3_2_0t_xwd_sportcombi.html
EU-SAAB-9-3-II-GRIFFIN-WAGON-5D-01	4691	1762	1492	Auto-Data Saab 9-3 SportCombi II Griffin specifications	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-griffin-facelift-2011-2.0t-biopower-163hp-xwd-54603
EU-FIAT-DUCATO-X250-VAN-L1H1-01	4963	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L1H2-01	4963	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L2H1-01	5413	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L3H2-01	5998	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L3H3-01	5998	2050	2764	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L4H2-01	6363	2050	2524	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-VAN-L4H3-01	6363	2050	2764	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-SAAB-9-3-II-PREFL-WAGON-5D-AERO-01	4654	1782	1507	Auto-Data Saab 9-3 SportCombi II 2.8 V6 specifications	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-2.8-i-v6-24v-230hp-11944
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	4908	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	5358	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	5708	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	5943	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	6308	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	5708	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	5943	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	6308	2050	2254	Fiat Professional Ducato official technical specifications	https://www.media.stellantis.com/uploads/pl/PL/2011/FIAT_PROF/SPECIFICATIONS/110505_FP_Ducato_TS_PL.pdf
EU-SAAB-9-3-II-PREFL-CONVERTIBLE-2D-01	4635	1762	1434	Auto-Data Saab 9-3 Convertible II 2.8T V6 specifications	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.8t-v6-250hp-11952
EU-SAAB-9-3-II-GRIFFIN-CONVERTIBLE-2D-01	4668	1762	1437	Auto-Data Saab 9-3 Convertible II Griffin specifications	https://www.auto-data.net/en/saab-9-3-convertible-ii-griffin-facelift-2011-1.9-ttid-160hp-54619
EU-HYUNDAI-GRAND-SANTA-FE-NC-SUV-5D-01	4915	1885	1695	Automobile-Catalog 2013 Hyundai Grand Santa Fe 2.2 CRDi 4WD specifications	https://www.automobile-catalog.com/car/2013/2311055/hyundai_grand_santa_fe_2_2_crdi_4wd.html
EU-SAAB-9-3-II-GRIFFIN-SEDAN-4D-01	4668	1762	1486	Auto-Data Saab 9-3 Griffin BioPower XWD; Auto-Data Saab 9-3 Griffin TTiD	https://www.auto-data.net/en/saab-9-3-sedan-ii-griffin-facelift-2011-2.0t-biopower-163hp-xwd-54577;https://www.auto-data.net/en/saab-9-3-sedan-ii-griffin-facelift-2011-1.9-ttid-160hp-54571
EU-OPEL-AGILA-B-H08-HATCHBACK-5D-01	3740	1680	1590	Auto-Data Opel Agila B specifications	https://www.auto-data.net/en/opel-agila-model-237
EU-CHEVROLET-CORSICA-I-SEDAN-4D-01	4658	1732	1367	Automobile-Catalog 1990 Chevrolet Corsica 3.1 specifications	https://www.automobile-catalog.com/car/1990/469910/chevrolet_corsica_sedan_3_1l_v-6.html
EU-NISSAN-SUNNY-Y10-WAGON-5D-4WD-01	4175	1665	1525	Automobile-Catalog 1994 Nissan Sunny Wagon 4x4 specifications	https://www.automobile-catalog.com/car/1994/2248430/nissan_sunny_1_6i_slx_wagon_4x4.html
EU-NISSAN-SUNNY-B12-WAGON-5D-4WD-01	4270	1640	1400	Automobile-Catalog 1987 Nissan Sunny Traveller 4WD specifications	https://www.automobile-catalog.com/car/1987/2222630/nissan_sunny_1_6_slx_traveller_4wd_cat.html
EU-ALFA-ROMEO-159-939-SEDAN-4D-01	4660	1828	1417	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-ALFA-ROMEO-159-939-WAGON-5D-01	4660	1828	1417	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-OPEL-ASTRA-H-CARAVAN-FACELIFT-01	4515	1753	1500	Auto-Data Opel Astra H Caravan specifications	https://www.auto-data.net/en/opel-astra-h-caravan-1.9-cdti-150hp-2370
EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	Vauxhall New Corsa official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/corsa-d/CorsaD_February_2007.pdf
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-3D-01	4030	1687	1490	Fiat Grande Punto UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2007-UK.pdf
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-5D-01	4030	1687	1490	Fiat Grande Punto UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/03/Fiat-Punto-2007-UK.pdf
EU-FIAT-PANDA-II-169-HATCHBACK-01	3538	1578	1540	Auto-Data Fiat Panda II 169 specifications	https://www.auto-data.net/en/fiat-panda-ii-169-1.1-mpi-54hp-6902
EU-OPEL-ASTRA-J-HATCHBACK-5D-01	4419	1814	1510	Auto-Data Opel Astra J 1.4 Turbo specifications	https://www.auto-data.net/en/opel-astra-j-1.4-turbo-120hp-16961
EU-NISSAN-PRIMERA-I-P10-SEDAN-4D-01	4400	1700	1390	Auto-Data Nissan Primera P10 specifications	https://www.auto-data.net/en/nissan-primera-p10-2.0-16v-115hp-automatic-25003
EU-NISSAN-PRIMERA-I-P10-HATCHBACK-5D-01	4400	1700	1390	Auto-Data Nissan Primera Hatch P10 specifications	https://www.auto-data.net/en/nissan-primera-hatch-p10-2.0-16v-115hp-automatic-25004
EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-SWB-PREFL-01	4435	1690	1695	Nissan 1989 Truck Service Manual	https://www.zonedatsun.fr/wp-content/uploads/2023/05/Nissan-Hardbody-D21-Truck-1989d21_truck_1989_compressed.pdf
EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-LWB-PREFL-01	4825	1690	1695	Nissan 1989 Truck Service Manual	https://www.zonedatsun.fr/wp-content/uploads/2023/05/Nissan-Hardbody-D21-Truck-1989d21_truck_1989_compressed.pdf
EU-NISSAN-PICKUP-D21-PICKUP-KINGCAB-SWB-PREFL-01	4825	1690	1695	Nissan 1989 Truck Service Manual	https://www.zonedatsun.fr/wp-content/uploads/2023/05/Nissan-Hardbody-D21-Truck-1989d21_truck_1989_compressed.pdf
EU-NISSAN-PICKUP-D21-PICKUP-REGULARCAB-SWB-FACELIFT-01	4435	1690	1705	Nissan 1996 Truck Owner's Manual	https://www.nissan-techinfo.com/View.ashx?d=1&sku=frontier1996-og&z=1
EU-NISSAN-PICKUP-D21-PICKUP-KINGCAB-SWB-FACELIFT-01	4825	1690	1705	Nissan 1996 Truck Owner's Manual	https://www.nissan-techinfo.com/View.ashx?d=1&sku=frontier1996-og&z=1
EU-DAIHATSU-HIJET-S85-MICROVAN-01	3295	1395	1870	ParuVendu Daihatsu Hijet 1.0ie Van specifications; ParuVendu Daihatsu Hijet 1.2 D Van specifications	https://www.paruvendu.fr/fiches-techniques-utilitaire/daihatsu-hijet/tole-1-0ie-2pl-6-cv-essence/3057906/;https://www.paruvendu.fr/fiches-techniques-utilitaire/daihatsu-hijet/tole-1-2-d-6-cv-diesel/3058322/
EU-FORD-ESCORT-VI-HATCHBACK-3D-FACELIFT-01	4136	1691	1398	EngineInDetail Ford Escort RS specifications	https://www.engineindetail.com/cars/ford/escort/escort-v-rs-1995-1996
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428	Auto-Data Ford Sierra Turnier I specifications	https://www.auto-data.net/en/ford-sierra-turnier-i-generation-1689
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428	Auto-Data Ford Sierra Turnier II specifications	https://www.auto-data.net/en/ford-sierra-turnier-ii-2.0i-120hp-7605
EU-FORD-SCORPIO-I-GGE-WAGON-5D-4X4-01	4744	1760	1490	Auto-Data Ford Scorpio I Turnier GGE 2.9i 4x4 specifications	https://www.auto-data.net/en/ford-scorpio-i-turnier-gge-2.9i-145hp-4x4-8187
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021	CarsGuide 1999 Ford Transit dimensions	https://www.carsguide.com.au/ford/transit/car-dimensions/1999
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024	CarsGuide 1999 Ford Transit dimensions	https://www.carsguide.com.au/ford/transit/car-dimensions/1999
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048	CarsGuide 1999 Ford Transit dimensions	https://www.carsguide.com.au/ford/transit/car-dimensions/1999
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247	CarsGuide 1999 Ford Transit dimensions	https://www.carsguide.com.au/ford/transit/car-dimensions/1999
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974	Transit Center Ford Transit Mk3 specifications	https://www.transitcenter.ie/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653	Transit Center Ford Transit Mk3 specifications	https://www.transitcenter.ie/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653	Transit Center Ford Transit Mk3 specifications	https://www.transitcenter.ie/transit-mk3-data-specification.php
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8201-8300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-doc.ie/spares/nissan/pick-up/pick-up-d21 "https://www.auto-doc.ie/spares/nissan/pick-up/pick-up-d21"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8201-8300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8201-8300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10214 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3140 行）

