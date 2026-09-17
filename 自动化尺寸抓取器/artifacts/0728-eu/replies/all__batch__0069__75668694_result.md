# 任务：all 第 6801-6900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0069__75668694


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6801-6900 行

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
all 第 6801-6900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6801-6900_ktype_dimension_mapping_final.tsv
- all_6801-6900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	4140	1560	1430
EU-ALFA-ROMEO-GIULIA-GT-105-COUPE-STEPFRONT-01	4080	1580	1315
EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	4108	1698	1802
EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	4137	1724	1810
EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	4145	1785	1845
EU-MITSUBISHI-PAJERO-II-V23C-CANVAS-TOP-SUV-3D-01	4140	1780	1820
EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	4725	1785	1900
EU-MITSUBISHI-SPACE-RUNNER-I-N11W-MPV-01	4290	1695	1640
EU-MITSUBISHI-SPACE-RUNNER-I-N21W-MPV-01	4270	1695	1680
EU-NISSAN-300ZX-Z31-COUPE-2D-01	4540	1725	1310
EU-NISSAN-300ZX-Z32-COUPE-2D-01	4520	1800	1255
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650
EU-NISSAN-PRAIRIE-M11-MPV-5D-01	4350	1690	1625
EU-NISSAN-PRAIRIE-M11-MPV-5D-02	4360	1690	1630
EU-NISSAN-PRAIRIE-NM10-MPV-5D-01	4230	1665	1685
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
EU-NISSAN-URVAN-E24-MPV-4D-01	4690	1690	1965
EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	4596	1850	1717
EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	4520	1732	1435
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435
EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	4358	1692	1315
EU-RENAULT-FUEGO-136-COUPE-TURBO-01	4385	1692	1336
EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	4667	1764	1420
EU-SAAB-9000-CC-HATCHBACK-5D-01	4620	1764	1430
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420
EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	4761	1806	1405
EU-SAAB-9000-CS-HATCHBACK-5D-01	4761	1778	1420
EU-SAAB-900-I-CONVERTIBLE-01	4680	1690	1420
EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	4687	1690	1420
EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	4687	1690	1420
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-3D-01	4687	1693	1420
EU-SAAB-900-I-FACELIFT-LATE-HATCHBACK-5D-01	4687	1693	1420
EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	4687	1695	1405
EU-SAAB-900-II-CONVERTIBLE-2D-01	4637	1711	1435
EU-SAAB-900-II-HATCHBACK-3D-01	4637	1711	1436
EU-SAAB-900-II-HATCHBACK-5D-01	4637	1711	1436
EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	4740	1690	1420
EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-SEDAN-4D-01	4740	1690	1420
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-3D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-TURBO16-HATCHBACK-5D-01	4740	1690	1425
EU-SAAB-900-I-PREFL-TURBO16S-HATCHBACK-3D-01	4740	1690	1425
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420
EU-SAAB-99-SEDAN-2D-EARLY-01	4420	1690	1440
EU-SAAB-99-SEDAN-2D-LATE-01	4477	1690	1440
EU-SAAB-99-SEDAN-4D-EARLY-01	4420	1690	1440
EU-SAAB-99-SEDAN-4D-LATE-01	4477	1690	1440
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-TOYOTA-CAMRY-III-XV10-SEDAN-4D-01	4725	1770	1415
EU-TOYOTA-CAMRY-III-XV10-WAGON-5D-01	4795	1770	1420
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-01	4520	1710	1400
EU-TOYOTA-CAMRY-II-V20-WAGON-5D-01	4610	1710	1440
EU-TOYOTA-CAMRY-I-V10-HATCHBACK-5D-01	4415	1690	1370
EU-TOYOTA-CAMRY-I-V10-SEDAN-4D-01	4460	1690	1395
EU-TOYOTA-CARINA-V-T170-WAGON-01	4470	1690	1380
EU-VOLVO-760-SEDAN-FACELIFT-01	4790	1760	1410
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410
EU-VOLVO-760-WAGON-FACELIFT-01	4790	1760	1435
EU-VOLVO-760-WAGON-PREFL-01	4800	1750	1435
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Antara a	2.4 4X4	SUV	Allrad	Benzin	123	167	Dec 2010	Feb 2015	2024-03-01	7239
Opel	Antara a	2.2 Cdti	SUV	Frontantrieb	Diesel	120	163	Dec 2010	Dec 2015	2024-03-01	7240
Opel	Antara a	2.2 Cdti 4X4	SUV	Allrad	Diesel	120	163	Dec 2010	Dec 2015	2024-03-01	7241
Opel	Antara a	2.2 Cdti 4X4	SUV	Allrad	Diesel	135	184	Dec 2010	Dec 2015	2024-03-01	7242
Skoda	Octavia	1.1	Stufenheck	Heckantrieb	Benzin	31	42	Feb 1962	Oct 1971	2024-03-01	7243
Citroën	C3 picasso	1.6 HDI 110	Großraumlimousine	Frontantrieb	Diesel	82	112	May 2010	Feb 2013	2024-08-01	7244
Alfa Romeo	Giulia	1300 TI	Stufenheck	Heckantrieb	Benzin	62	84	Apr 1969	Jul 1975	2024-03-01	7245
Alfa Romeo	Giulia	1600 Super	Stufenheck	Heckantrieb	Benzin	71	97	Jun 1964	Aug 1969	2024-03-01	7246
Citroën	Berlingo	1.6 HDI 90	Großraumlimousine	Frontantrieb	Diesel	68	92	Jul 2010	Dec 2018	2026-05-01	7247
Volvo	S70	2	Stufenheck	Frontantrieb	Benzin	93	126	Jan 1997	Nov 2000	2024-03-01	7250
Volvo	S70	2.4	Stufenheck	Frontantrieb	Benzin	106	144	Jan 1997	Nov 2000	2024-03-01	7251
Volvo	S70	2.4	Stufenheck	Frontantrieb	Benzin	125	170	Jan 1997	Nov 2000	2024-03-01	7252
Volvo	S70	2.4 Turbo	Stufenheck	Frontantrieb	Benzin	142	193	Jan 1997	Nov 2000	2024-03-01	7253
Volvo	S70	T5	Stufenheck	Frontantrieb	Benzin	176	239	Jan 1997	Nov 2000	2024-03-01	7254
Volvo	S70	2.5 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Jan 1997	Nov 2000	2024-03-01	7255
Volvo	V70 i	2	Kombi	Frontantrieb	Benzin	93	126	Dec 1995	Mar 2000	2024-03-01	7256
Volvo	V70 i	2.4	Kombi	Frontantrieb	Benzin	106	144	Dec 1995	Mar 2000	2024-03-01	7257
Volvo	V70 i	2.4	Kombi	Frontantrieb	Benzin	125	170	Dec 1995	May 2000	2024-03-01	7258
Volvo	V70 i	2.4 Turbo	Kombi	Frontantrieb	Benzin	142	193	Apr 1996	Dec 2000	2024-03-01	7259
Volvo	V70 i	2.4 Turbo AWD	Kombi	Allrad	Benzin	142	193	Apr 1996	Dec 2000	2024-03-01	7260
Volvo	V70 i	2.3 T-5	Kombi	Frontantrieb	Benzin	176	239	Nov 1996	Dec 2000	2024-03-01	7261
Volvo	V70 i	2.5 TDI	Kombi	Frontantrieb	Diesel	103	140	Dec 1995	Dec 2000	2024-03-01	7262
Volvo	S90 i	2.9	Stufenheck	Heckantrieb	Benzin	132	180	Jan 1997	May 1998	2024-03-01	7263
Volvo	S90 i	2.9	Stufenheck	Heckantrieb	Benzin	150	204	Jan 1997	May 1998	2024-03-01	7264
Volvo	V90 i	2.9	Kombi	Heckantrieb	Benzin	132	180	Jan 1997	Dec 1998	2024-03-01	7265
Volvo	V90 i	2.9	Kombi	Heckantrieb	Benzin	150	204	Jan 1997	Dec 1998	2024-03-01	7266
Nissan	Datsun 100a	1	Schrägheck	Frontantrieb	Benzin	33	45	Dec 1974	Jun 1978	2024-03-01	7267
Nissan	Datsun 100a	F-ii 1.0	Schrägheck	Frontantrieb	Benzin	33	45	Dec 1975	Aug 1980	2024-03-01	7268
Nissan	Datsun 100a	F-ii 1.0	Kombi	Frontantrieb	Benzin	33	45	Dec 1975	Aug 1980	2024-03-01	7269
Nissan	Datsun 120y	1.2	Coupe	Heckantrieb	Benzin	38	52	Apr 1962	Jul 1980	2024-03-01	7270
Nissan	Datsun 120	Y 1.2	Stufenheck	Heckantrieb	Benzin	38	52	Sep 1974	Jul 1980	2024-03-01	7271
Nissan	Datsun 120y	A F-ii 1.2	Coupe	Heckantrieb	Benzin	38	52	Dec 1975	Aug 1980	2024-03-01	7272
Chevrolet	Lacetti	1.6	Kombi	Frontantrieb	Benzin	80	109	Mar 2005	-	2024-03-01	7273
Nissan	Datsun 120	A F-ii 1.2	Stufenheck	Heckantrieb	Benzin	38	52	Dec 1975	Jul 1980	2024-03-01	7274
Nissan	Datsun 120	Y 1.2	Stufenheck	Heckantrieb	Benzin	38	52	Jun 1976	Jul 1980	2024-03-01	7275
Nissan	Datsun 140y	1.4	Kombi	Heckantrieb	Benzin	49	67	Feb 1979	Jun 1983	2024-03-01	7276
Nissan	Datsun 160j	1.6	Stufenheck	Heckantrieb	Benzin	61	83	Jan 1973	Feb 1982	2024-03-01	7277
Nissan	Datsun 160j	1.6 I.e.	Stufenheck	Heckantrieb	Benzin	65	88	Jan 1978	Feb 1982	2024-03-01	7278
Nissan	Datsun 180b	1.8	Stufenheck	Heckantrieb	Benzin	65	88	May 1977	Jan 1981	2024-03-01	7279
Nissan	Datsun 180b	1.8	Stufenheck	Heckantrieb	Benzin	66	90	May 1977	Jan 1981	2024-03-01	7280
Nissan	Datsun 240	KGT 2.4	Coupe	Heckantrieb	Benzin	96	131	Mar 1978	Jul 1981	2024-03-01	7281
Nissan	300zx	3.0 Turbo	Targa	Heckantrieb	Benzin	168	228	Apr 1984	Oct 1990	2024-03-01	7283
Nissan	280zx,zxt	2.8	Coupe	Heckantrieb	Benzin	147	200	Jan 1983	Feb 1984	2024-03-01	7284
Nissan	Urvan	2	Kasten	Heckantrieb	Benzin	55	75	Jul 1981	Nov 1982	2024-03-01	7285
Nissan	Urvan	2.2 D	Kasten	Heckantrieb	Diesel	47	64	Jul 1981	Nov 1982	2024-03-01	7286
Nissan	Urvan	2	Bus	Heckantrieb	Benzin	64	87	Dec 1982	Nov 1988	2024-03-01	7287
Nissan	Urvan	2.3 D	Bus	Heckantrieb	Diesel	51	69	Apr 1985	Nov 1988	2024-03-01	7289
Nissan	Sunny	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Mar 1982	Sep 1987	2024-03-01	7291
Nissan	Sunny	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Jul 1986	Oct 1991	2024-03-01	7293
Nissan	Patrol gr iv	4.2 D	Geländewagen geschlossen	Allrad	Diesel	85	116	Nov 1988	Jun 1997	2024-03-01	7295
Nissan	Patrol iii/2 station wagon	3.3 D	Geländewagen geschlossen	Allrad	Diesel	81	110	Aug 1988	Jun 1990	2024-03-01	7296
Nissan	Urvan	2.3 D	Kasten	Heckantrieb	Diesel	50	68	Nov 1982	May 1987	2024-03-01	7297
Mitsubishi	Space runner	2.0 TD	Großraumlimousine	Frontantrieb	Diesel	60	82	Oct 1992	Aug 1999	2024-03-01	7298
Mitsubishi	Pajero ii	2.4	Geländewagen geschlossen	Allrad	Benzin	82	112	Apr 1991	Oct 1999	2024-03-01	7300
Mitsubishi	Pajero ii canvas top	2.4	Geländewagen offen	Allrad	Benzin	82	112	Apr 1991	Apr 2000	2024-03-01	7301
Nissan	Maxima / qx iv	3	Stufenheck	Frontantrieb	Benzin	142	193	Jan 1995	Aug 2000	2024-03-01	7303
Nissan	Prairie	1.5 S	Großraumlimousine	Frontantrieb	Benzin	55	75	Jan 1984	Dec 1987	2024-03-01	7304
Hyundai	Elantra iv	1.6 Cvvt	Stufenheck	Frontantrieb	Benzin	90	122	Jun 2006	Jun 2011	2024-03-01	7305
Nissan	Sunny	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1986	Oct 1988	2024-03-01	7308
Saab	99	2.0 EMS	Stufenheck	Frontantrieb	Benzin	87	118	Sep 1974	Dec 1978	2024-03-01	7309
Nissan	Sunny	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	75	102	Oct 1992	May 1995	2024-03-01	7310
Saab	99	2	Schrägheck	Frontantrieb	Benzin	79	107	Mar 1976	May 1978	2024-03-01	7311
Saab	99	2	Stufenheck	Frontantrieb	Benzin	70	95	Oct 1972	Aug 1974	2024-03-01	7313
Saab	99	2.0 EMS	Stufenheck	Frontantrieb	Benzin	81	110	Apr 1972	Aug 1974	2024-03-01	7314
Saab	99	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	107	146	Oct 1977	Jun 1980	2024-03-01	7316
Nissan	Sunny	1.6	Coupe	Frontantrieb	Benzin	62	84	Jun 1986	Oct 1988	2024-03-01	7317
Nissan	Sunny	1.6	Kombi	Frontantrieb	Benzin	62	84	Jun 1986	Oct 1988	2024-03-01	7318
Nissan	Sunny	1.6	Stufenheck	Frontantrieb	Benzin	62	84	Jun 1986	Oct 1988	2024-03-01	7319
Nissan	Sunny	1.6	Schrägheck	Frontantrieb	Benzin	62	84	Jun 1986	Oct 1988	2024-03-01	7320
Volvo	760	2.4 TD Interc.	Kombi	Heckantrieb	Diesel	85	116	Aug 1987	Jul 1992	2024-03-01	7321
Opel	Kadett e combo	1.3 N	Kasten/Kombi	Frontantrieb	Benzin	44	60	Jan 1986	Dec 1989	2024-03-01	7322
Opel	Kadett e combo	1.3 S	Kasten/Kombi	Frontantrieb	Benzin	55	75	Jan 1986	Dec 1989	2024-03-01	7323
Opel	Kadett e combo	1.6	Kasten/Kombi	Frontantrieb	Benzin	60	82	Sep 1986	Dec 1991	2024-03-01	7324
Opel	Kadett e combo	1.6 D	Kasten/Kombi	Frontantrieb	Diesel	40	54	Jan 1986	Dec 1989	2024-03-01	7326
Opel	Kadett e combo	1.7 D	Kasten/Kombi	Frontantrieb	Diesel	42	57	Jan 1989	Jul 1994	2024-03-01	7327
Barkas	B 1000	1.3	Kasten	Frontantrieb	Benzin	43	58	Jan 1976	Dec 1991	2024-03-01	7328
Barkas	B 1000	1.3	Bus	Frontantrieb	Benzin	43	58	Jan 1976	Dec 1991	2024-03-01	7332
Dacia	1300	1.3	Stufenheck	Frontantrieb	Benzin	40	54	Dec 1972	May 1983	2024-03-01	7333
Dacia	1310	1.3	Stufenheck	Frontantrieb	Benzin	40	54	May 1983	Jul 2004	2024-03-01	7334
Renault	20	1.6	Schrägheck	Frontantrieb	Benzin	71	97	May 1977	Dec 1983	2024-03-01	7335
Renault	Fuego	1.4 Tl/gtl	Coupe	Frontantrieb	Benzin	47	64	Feb 1980	Oct 1985	2024-03-01	7336
Hyundai	Genesis	2.0 T	Coupe	Heckantrieb	Benzin	157	214	Jan 2008	Dec 2012	2024-03-01	7337
Saab	9000	2.0 -16	Stufenheck	Frontantrieb	Benzin	94	128	Jan 1989	Jan 1993	2024-03-01	7338
Saab	900 i	2.0 Turbo-16 S	Stufenheck	Frontantrieb	Benzin	129	175	Jan 1984	Dec 1988	2024-03-01	7339
Saab	900 i	2.0 C	Stufenheck	Frontantrieb	Benzin	74	101	Jul 1982	Dec 1988	2024-03-01	7340
Saab	900 i	2.0 S Turbo-16	Stufenheck	Frontantrieb	Benzin	104	141	Jul 1991	Dec 1993	2024-03-01	7341
Saab	900 i	2.0 -16	Stufenheck	Frontantrieb	Benzin	93	126	Jan 1989	Dec 1993	2024-03-01	7342
Saab	900 i	2.0 Turbo-16	Stufenheck	Frontantrieb	Benzin	118	160	Nov 1985	Dec 1993	2024-03-01	7343
Toyota	Camry	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Oct 1986	Aug 1988	2024-03-01	7344
Saab	900 i combi coupe	2.0 Turbo-16 S CAT	Schrägheck	Frontantrieb	Benzin	125	170	Jan 1989	Dec 1993	2024-03-01	7345
Saab	900 i	2.0 Turbo-16 S CAT	Stufenheck	Frontantrieb	Benzin	129	175	Jan 1989	Dec 1993	2024-03-01	7346
Saab	900 i	2.0 S Turbo-16	Stufenheck	Frontantrieb	Benzin	107	146	Jan 1992	Dec 1993	2024-03-01	7347
Saab	900 i	2.1 -16	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1990	Dec 1993	2024-03-01	7348
Saab	900 i	2.1 -16	Cabriolet	Frontantrieb	Benzin	100	136	Aug 1990	Jun 1994	2024-03-01	7349
Toyota	Carina v	2	Kombi	Frontantrieb	Benzin	89	121	Dec 1987	Apr 1992	2024-03-01	7350
Saab	9000	2.0 -16 Turbo	Schrägheck	Frontantrieb	Benzin	127	172	Jun 1989	Dec 1992	2024-03-01	7351
Saab	9000	2.0 -16 Turbo	Stufenheck	Frontantrieb	Benzin	129	175	Apr 1985	Dec 1991	2024-03-01	7352
Saab	900 i	2.0 Turbo-16 S	Cabriolet	Frontantrieb	Benzin	129	175	Nov 1986	Jun 1994	2024-03-01	7353
Saab	900 i combi coupe	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	103	140	Oct 1986	Dec 1991	2024-03-01	7354
Saab	900 i	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	103	140	Oct 1986	Dec 1991	2024-03-01	7355


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类完成缓存复用与新尺寸组闭合。
* 对跨代际、改款、门数、短轴/长轴及历史车型同名差异进行了派生拆分。
* Giulia 1300 TI、Camry 1.8、早期 Saab 9000 CD、Volvo 760 Kombi TD 的直接规格与累计同系列尺寸组存在差异，已按冲突保护规则创建后续序号，未覆盖已有尺寸事实。([汽车目录][1])
* 已修正 Ktype 7309 为早期 Saab 99 两门轿车尺寸组，并删除未被当前批次引用的孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：117
* PENDING 映射：0
* DIMENSION_GROUP：71
* `id` 唯一性：通过
* `DIMENSION_GROUP_ID` 唯一性：通过
* 映射引用闭合：通过
* 三维、来源和 URL 完整性：通过
* 固定表头与列数：通过
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7239	7239	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
7240	7240	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
7241	7241	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
7242	7242	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
7243	7243	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	HIGH		READY
7244	7244	MPV	C3 Picasso I Phase I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
7245_pre70	7245	Sedan	Giulia 105 pre-1970	105	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	MEDIUM	输入生产区间跨越1970年前后车身长度变化。	READY
7245_post70	7245	Sedan	Giulia 105 1970-on	105	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	MEDIUM	输入生产区间跨越1970年前后车身长度变化。	READY
7246	7246	Sedan	Giulia 105	105	4	EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	HIGH		READY
7247	7247	MPV	Berlingo II	B9	5	EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	HIGH		READY
7250	7250	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7251	7251	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7252	7252	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7253	7253	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7254	7254	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7255	7255	Sedan	S70 I		4	EU-VOLVO-S70-I-SEDAN-4D-01	HIGH		READY
7256	7256	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7257	7257	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7258	7258	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7259	7259	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7260	7260	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7261	7261	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7262	7262	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-5D-01	HIGH		READY
7263	7263	Sedan	S90 I		4	EU-VOLVO-S90-I-SEDAN-4D-01	HIGH		READY
7264	7264	Sedan	S90 I		4	EU-VOLVO-S90-I-SEDAN-4D-01	HIGH		READY
7265	7265	Wagon	V90 I		5	EU-VOLVO-V90-I-WAGON-5D-01	HIGH		READY
7266	7266	Wagon	V90 I		5	EU-VOLVO-V90-I-WAGON-5D-01	HIGH		READY
7267	7267	Hatchback	Datsun 100A E10	E10	2	EU-NISSAN-DATSUN-100A-E10-HATCHBACK-2D-01	HIGH		READY
7268	7268	Hatchback	Datsun 100A F-II	BLF10	2	EU-NISSAN-DATSUN-100A-F10-HATCHBACK-2D-01	HIGH		READY
7269	7269	Wagon	Datsun 100A F-II	WBLF10	3	EU-NISSAN-DATSUN-100A-F10-WAGON-3D-01	HIGH		READY
7270	7270	Coupe	Datsun 120Y B210	KB210	2	EU-NISSAN-DATSUN-120Y-B210-COUPE-2D-01	HIGH		READY
7271	7271	Sedan	Datsun 120Y B210	B210	4	EU-NISSAN-DATSUN-120Y-B210-SEDAN-4D-01	HIGH		READY
7272	7272	Coupe	Datsun Cherry 120A F-II	KLF10	3	EU-NISSAN-DATSUN-120A-F10-COUPE-3D-01	HIGH		READY
7273	7273	Wagon	Lacetti J200	J200	5	EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	HIGH		READY
7274	7274	Sedan	Datsun Cherry 120A F-II	LF10	4	EU-NISSAN-DATSUN-120A-F10-SEDAN-4D-01	HIGH		READY
7275	7275	Sedan	Datsun 120Y B210	LB210	4	EU-NISSAN-DATSUN-120Y-B210-SEDAN-4D-01	HIGH		READY
7276	7276	Wagon	Datsun Sunny B310	HBL310	5	EU-NISSAN-SUNNY-B310-WAGON-5D-01	HIGH		READY
7277_710	7277	Sedan	Datsun 160J 710	710	4	EU-NISSAN-DATSUN-160J-710-SEDAN-4D-01	MEDIUM	输入生产区间跨越710与A10两代外廓。	READY
7277_a10	7277	Sedan	Datsun 160J A10	A10	4	EU-NISSAN-DATSUN-160J-A10-SEDAN-4D-01	MEDIUM	输入生产区间跨越710与A10两代外廓。	READY
7278	7278	Sedan	Datsun 160J A10	A10	4	EU-NISSAN-DATSUN-160J-A10-SEDAN-4D-01	HIGH		READY
7279	7279	Sedan	Datsun 180B 810	PL810	4	EU-NISSAN-DATSUN-180B-PL810-SEDAN-4D-01	HIGH		READY
7280	7280	Sedan	Datsun 180B 810	PL810	4	EU-NISSAN-DATSUN-180B-PL810-SEDAN-4D-01	HIGH		READY
7281	7281	Coupe	Datsun 240K C210	C210	2	EU-NISSAN-DATSUN-240K-C210-COUPE-2D-01	HIGH		READY
7283	7283	Coupe	300ZX Z31	Z31	2	EU-NISSAN-300ZX-Z31-COUPE-2D-01	HIGH	Targa顶不改变闭合状态外廓尺寸组。	READY
7284	7284	Coupe	280ZX S130	HGS130	3	EU-NISSAN-280ZX-S130-COUPE-2PLUS2-01	HIGH		READY
7285	7285	Van	Urvan E23	E23	4	EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	HIGH		READY
7286	7286	Van	Urvan E23	E23	4	EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	HIGH		READY
7287	7287	MPV	Urvan E23	E23	4	EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	HIGH		READY
7289	7289	MPV	Urvan E23	E23	4	EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	HIGH		READY
7291	7291	Sedan	Sunny B11	B11	4	EU-NISSAN-SUNNY-B11-SEDAN-4D-01	HIGH		READY
7293	7293	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH		READY
7295	7295	SUV	Patrol IV Y60	Y60	3	EU-NISSAN-PATROL-IV-Y60-SUV-3D-01	HIGH		READY
7296	7296	SUV	Patrol 260	W260	5	EU-NISSAN-PATROL-260-W260-SUV-5D-LWB-01	HIGH		READY
7297	7297	Van	Urvan E23	E23	4	EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	HIGH		READY
7298	7298	MPV	Space Runner I	N18W	4	EU-MITSUBISHI-SPACE-RUNNER-I-N18W-MPV-01	HIGH		READY
7300_3dr	7300	SUV	Pajero II	V20	3	EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	MEDIUM	输入Ktype未限定短轴或长轴，保留两种已确认外廓。	READY
7300_5dr	7300	SUV	Pajero II	V40	5	EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	MEDIUM	输入Ktype未限定短轴或长轴，保留两种已确认外廓。	READY
7301	7301	SUV	Pajero II canvas top	V23C	3	EU-MITSUBISHI-PAJERO-II-V23C-CANVAS-TOP-SUV-3D-01	HIGH		READY
7303_prefl	7303	Sedan	Maxima QX IV A32 pre-facelift	A32	4	EU-NISSAN-MAXIMA-QX-IV-A32-SEDAN-PREFL-01	MEDIUM	输入生产区间跨越A32改款前后外廓。	READY
7303_facelift	7303	Sedan	Maxima QX IV A32 facelift	A32	4	EU-NISSAN-MAXIMA-QX-IV-A32-SEDAN-FACELIFT-01	MEDIUM	输入生产区间跨越A32改款前后外廓。	READY
7304	7304	MPV	Prairie M10	M10	5	EU-NISSAN-PRAIRIE-M10-MPV-5D-01	HIGH		READY
7305	7305	Sedan	Elantra IV	HD	4	EU-HYUNDAI-ELANTRA-IV-HD-SEDAN-4D-01	HIGH		READY
7308_3dr	7308	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	输入Ktype未限定三门或五门。	READY
7308_5dr	7308	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	输入Ktype未限定三门或五门。	READY
7309	7309	Sedan	Saab 99 early		2	EU-SAAB-99-SEDAN-2D-EARLY-01	HIGH		READY
7310	7310	Sedan	Sunny N14	N14	4	EU-NISSAN-SUNNY-N14-SEDAN-4D-01	HIGH		READY
7311_3dr	7311	Hatchback	Saab 99 Combi Coupé		3	EU-SAAB-99-COMBI-COUPE-HATCHBACK-3D-01	MEDIUM	输入Ktype未限定三门或五门Combi Coupé。	READY
7311_5dr	7311	Hatchback	Saab 99 Combi Coupé		5	EU-SAAB-99-COMBI-COUPE-HATCHBACK-5D-01	MEDIUM	输入Ktype未限定三门或五门Combi Coupé。	READY
7313_2dr	7313	Sedan	Saab 99 early		2	EU-SAAB-99-SEDAN-2D-EARLY-01	MEDIUM	输入Ktype未限定两门或四门轿车。	READY
7313_4dr	7313	Sedan	Saab 99 early		4	EU-SAAB-99-SEDAN-4D-EARLY-01	MEDIUM	输入Ktype未限定两门或四门轿车。	READY
7314	7314	Sedan	Saab 99 early		2	EU-SAAB-99-SEDAN-2D-EARLY-01	HIGH		READY
7316	7316	Hatchback	Saab 99 Combi Coupé		3	EU-SAAB-99-COMBI-COUPE-HATCHBACK-3D-01	HIGH		READY
7317	7317	Coupe	Sunny B12	B12	3	EU-NISSAN-SUNNY-B12-COUPE-3D-01	HIGH		READY
7318	7318	Wagon	Sunny B12	B12	5	EU-NISSAN-SUNNY-B12-WAGON-5D-01	HIGH		READY
7319	7319	Sedan	Sunny N13	N13	4	EU-NISSAN-SUNNY-N13-SEDAN-4D-01	HIGH		READY
7320_3dr	7320	Hatchback	Sunny N13	N13	3	EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	MEDIUM	输入Ktype未限定三门或五门。	READY
7320_5dr	7320	Hatchback	Sunny N13	N13	5	EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	MEDIUM	输入Ktype未限定三门或五门。	READY
7321	7321	Wagon	760 facelift		5	EU-VOLVO-760-WAGON-FACELIFT-02	HIGH	当前直接规格与既有01组三维冲突，按规则新建02组。	READY
7322	7322	Van	Kadett E Combo		3	EU-OPEL-KADETT-E-COMBO-VAN-3D-01	HIGH		READY
7323	7323	Van	Kadett E Combo		3	EU-OPEL-KADETT-E-COMBO-VAN-3D-01	HIGH		READY
7324	7324	Van	Kadett E Combo		3	EU-OPEL-KADETT-E-COMBO-VAN-3D-01	HIGH		READY
7326	7326	Van	Kadett E Combo		3	EU-OPEL-KADETT-E-COMBO-VAN-3D-01	HIGH		READY
7327	7327	Van	Kadett E Combo		3	EU-OPEL-KADETT-E-COMBO-VAN-3D-01	HIGH		READY
7328	7328	Van	Barkas B1000	B1000	4	EU-BARKAS-B1000-VAN-MPV-4D-01	HIGH		READY
7332	7332	MPV	Barkas B1000	B1000	4	EU-BARKAS-B1000-VAN-MPV-4D-01	HIGH		READY
7333	7333	Sedan	Dacia 1300	1300	4	EU-DACIA-1300-SEDAN-4D-01	HIGH		READY
7334_early	7334	Sedan	Dacia 1310 early	1310	4	EU-DACIA-1310-SEDAN-EARLY-4D-01	MEDIUM	输入生产区间跨越多次外廓改型。	READY
7334_mid	7334	Sedan	Dacia 1310 mid	1310	4	EU-DACIA-1310-SEDAN-MID-4D-01	MEDIUM	输入生产区间跨越多次外廓改型。	READY
7334_late	7334	Sedan	Dacia 1310 late	1310	4	EU-DACIA-1310-SEDAN-LATE-4D-01	MEDIUM	输入生产区间跨越多次外廓改型。	READY
7335_prefl	7335	Hatchback	Renault 20 pre-facelift	127	5	EU-RENAULT-20-127-HATCHBACK-PREFL-01	MEDIUM	输入生产区间跨越改款前后车宽变化。	READY
7335_facelift	7335	Hatchback	Renault 20 facelift	127	5	EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	MEDIUM	输入生产区间跨越改款前后车宽变化。	READY
7336	7336	Coupe	Fuego	136	3	EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	HIGH		READY
7337	7337	Coupe	Genesis Coupe pre-facelift	BK	2	EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	HIGH		READY
7338	7338	Sedan	9000 CD	CD	4	EU-SAAB-9000-CD-SEDAN-02	HIGH	早期CD直接规格与既有01组三维不一致，按规则新建02组。	READY
7339	7339	Sedan	900 I post-1983 pre-facelift		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	HIGH		READY
7340_pre83	7340	Sedan	900 I pre-1983		4	EU-SAAB-900-I-SEDAN-PRE83-01	MEDIUM	输入生产区间跨越1983年前后高度边界。	READY
7340_post83	7340	Sedan	900 I post-1983 pre-facelift		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产区间跨越1983年前后高度边界。	READY
7341	7341	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH		READY
7342	7342	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH		READY
7343_prefl	7343	Sedan	900 I post-1983 pre-facelift		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产区间跨越1987/1988外廓改款。	READY
7343_facelift	7343	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产区间跨越1987/1988外廓改款。	READY
7344	7344	Sedan	Camry II V20	V20	4	EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-02	HIGH	1.8欧洲版直接规格与既有01组长度不同，按规则新建02组。	READY
7345	7345	Hatchback	900 I facelift Turbo 16 S		3	EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	HIGH		READY
7346	7346	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH		READY
7347	7347	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH		READY
7348	7348	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	HIGH		READY
7349	7349	Convertible	900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH		READY
7350	7350	Wagon	Carina V T170	T170	5	EU-TOYOTA-CARINA-V-T170-WAGON-01	HIGH		READY
7351	7351	Hatchback	9000 CC facelift	CC	5	EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	HIGH		READY
7352	7352	Sedan	9000 CD	CD	4	EU-SAAB-9000-CD-SEDAN-02	HIGH	早期CD直接规格与既有01组三维不一致，按规则新建02组。	READY
7353	7353	Convertible	900 I		2	EU-SAAB-900-I-CONVERTIBLE-01	HIGH		READY
7354_3dr_prefl	7354	Hatchback	900 I pre-facelift		3	EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	MEDIUM	输入Ktype跨三/五门及改款前后外廓。	READY
7354_3dr_facelift	7354	Hatchback	900 I facelift		3	EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入Ktype跨三/五门及改款前后外廓。	READY
7354_5dr_prefl	7354	Hatchback	900 I pre-facelift		5	EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	MEDIUM	输入Ktype跨三/五门及改款前后外廓。	READY
7354_5dr_facelift	7354	Hatchback	900 I facelift		5	EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入Ktype跨三/五门及改款前后外廓。	READY
7355_prefl	7355	Sedan	900 I post-1983 pre-facelift		4	EU-SAAB-900-I-SEDAN-POST83-PREFL-01	MEDIUM	输入生产区间跨越改款前后外廓。	READY
7355_facelift	7355	Sedan	900 I facelift		4	EU-SAAB-900-I-SEDAN-FACELIFT-01	MEDIUM	输入生产区间跨越改款前后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6801-6900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	4596	1850	1717	Auto-Data	https://www.auto-data.net/en/opel-antara-facelift-2010-2.4-167hp-4x4-19644
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/3130460/skoda_octavia.html
EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	4078	1766	1669	Citroën C3 Picasso UK brochure	https://autocatalogarchive.com/wp-content/uploads/2022/09/Citroern-C3-Picasso-2011-UK.pdf
EU-ALFA-ROMEO-GIULIA-105-SEDAN-01	4140	1560	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/33290/alfa_romeo_giulia_super.html
EU-ALFA-ROMEO-GIULIA-105-SEDAN-02	4160	1560	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1971/33305/alfa_romeo_giulia_1300_ti.html
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801	Auto-Data	https://www.auto-data.net/en/citroen-berlingo-ii-phase-i-2008-1.6-hdi-90hp-15152
EU-VOLVO-S70-I-SEDAN-4D-01	4720	1760	1400	Auto-Data	https://www.auto-data.net/en/volvo-s70-2.0-126hp-9299
EU-VOLVO-V70-I-WAGON-5D-01	4730	1760	1430	Auto-Data	https://www.auto-data.net/en/volvo-v70-i-2.0-126hp-9254
EU-VOLVO-S90-I-SEDAN-4D-01	4870	1750	1420	AutoEvolution	https://www.autoevolution.com/cars/volvo-s90-1997.html
EU-VOLVO-V90-I-WAGON-5D-01	4860	1750	1460	CarsGuide	https://www.carsguide.com.au/volvo/v90/car-dimensions/1998
EU-NISSAN-DATSUN-100A-E10-HATCHBACK-2D-01	3670	1490	1365	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/129185/datsun_100a_cherry.html
EU-NISSAN-DATSUN-100A-F10-HATCHBACK-2D-01	3840	1500	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/129560/datsun_cherry_100a__f-ii.html
EU-NISSAN-DATSUN-100A-F10-WAGON-3D-01	3825	1500	1360	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/129230/datsun_cherry_100a__f-ii_wagon.html
EU-NISSAN-DATSUN-120Y-B210-COUPE-2D-01	3950	1545	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/132575/datsun_120y_sunny_coupe.html
EU-NISSAN-DATSUN-120Y-B210-SEDAN-4D-01	3950	1545	1370	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/132620/datsun_120y_germany.html
EU-NISSAN-DATSUN-120A-F10-COUPE-3D-01	3840	1500	1310	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/129245/datsun_cherry_120a__f-ii_gt_coupe.html
EU-CHEVROLET-LACETTI-J200-WAGON-5D-01	4580	1725	1460	Auto-Data	https://www.auto-data.net/en/chevrolet-lacetti-wagon-1.6-i-16v-109hp-14442
EU-NISSAN-DATSUN-120A-F10-SEDAN-4D-01	3840	1500	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/2093105/datsun_cherry__f-ii_120a_4d.html
EU-NISSAN-SUNNY-B310-WAGON-5D-01	4050	1590	1390	Auto-Data	https://www.auto-data.net/en/nissan-sunny-traveller-140y-150y-generation-153
EU-NISSAN-DATSUN-160J-710-SEDAN-4D-01	4120	1580	1375	Datsuns.co.uk	https://datsuns.co.uk/?p=403
EU-NISSAN-DATSUN-160J-A10-SEDAN-4D-01	4260	1600	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/33935/datsun_violet_160_j.html
EU-NISSAN-DATSUN-180B-PL810-SEDAN-4D-01	4260	1630	1390	Nissan Heritage Collection	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/datsun_bluebird_1800sss_1977.html
EU-NISSAN-DATSUN-240K-C210-COUPE-2D-01	4600	1625	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1979/35390/datsun_skyline_240_k.html
EU-NISSAN-300ZX-Z31-COUPE-2D-01	4540	1725	1310	Auto-Data	https://www.auto-data.net/en/nissan-300-zx-z31-3.0-turbo-228hp-662
EU-NISSAN-280ZX-S130-COUPE-2PLUS2-01	4620	1690	1300	Automobile-Catalog	https://www.automobile-catalog.com/car/1983/2184155/datsun_280_zxt_turbo.html
EU-NISSAN-URVAN-E23-MPV-VAN-4D-01	4009	1690	1905	Drive.Place	https://datsun.drive.place/urvan/e23/group_minivan/373103
EU-NISSAN-SUNNY-B11-SEDAN-4D-01	4135	1620	1385	Auto-Data	https://www.auto-data.net/en/nissan-sunny-i-b11-1.7-d-54hp-524
EU-NISSAN-SUNNY-N13-SEDAN-4D-01	4215	1640	1380	Auto-Data	https://www.auto-data.net/en/nissan-sunny-ii-n13-1.3-60hp-507
EU-NISSAN-PATROL-IV-Y60-SUV-3D-01	4240	1800	1790	Auto-Data	https://www.auto-data.net/en/nissan-patrol-iv-3-door-y60-4.2-d-y60gr-116hp-302
EU-NISSAN-PATROL-260-W260-SUV-5D-LWB-01	4725	1690	1800	Automobile-Catalog; UltimateSpecs	https://www.automobile-catalog.com/make/nissan/patrol_3gen/patrol_3gen_wagon/1987.html;https://www.ultimatespecs.com/car-specs/Nissan/6738/Nissan-Patrol-K160-Wagon-33-Turbo-D.html
EU-MITSUBISHI-SPACE-RUNNER-I-N18W-MPV-01	4270	1695	1665	Auto-Data	https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-2.0-td-glx-82hp-15541
EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	4145	1785	1845	Auto-Data	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-generation-3407
EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	4725	1785	1900	Auto-Data	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15508
EU-MITSUBISHI-PAJERO-II-V23C-CANVAS-TOP-SUV-3D-01	4140	1780	1820	Automobile-Catalog	https://www.automobile-catalog.com/make/mitsubishi/pajero_2gen/pajero_2gen_canvas/1992.html
EU-NISSAN-MAXIMA-QX-IV-A32-SEDAN-PREFL-01	4770	1770	1415	Auto-Data	https://www.auto-data.net/en/nissan-maxima-qx-iv-a32-3.0-193hp-automatic-24983
EU-NISSAN-MAXIMA-QX-IV-A32-SEDAN-FACELIFT-01	4800	1770	1450	Auto-Data	https://www.auto-data.net/en/nissan-maxima-qx-iv-a32-facelift-1997-3.0-193hp-680
EU-NISSAN-PRAIRIE-M10-MPV-5D-01	4090	1660	1650	Auto-Data	https://www.auto-data.net/en/nissan-prairie-m10-nm10-1.8-sgl-m10-90hp-413
EU-HYUNDAI-ELANTRA-IV-HD-SEDAN-4D-01	4505	1775	1490	Auto-Data	https://www.auto-data.net/en/hyundai-elantra-iv-1.6-i-16v-122hp-13899
EU-NISSAN-SUNNY-N13-HATCHBACK-3D-01	4030	1640	1380	Auto-Data	https://www.auto-data.net/en/nissan-sunny-ii-hatchback-n13-1.3-60hp-498
EU-NISSAN-SUNNY-N13-HATCHBACK-5D-01	4030	1640	1380	Auto-Data	https://www.auto-data.net/en/nissan-sunny-ii-hatchback-n13-1.6-84hp-501
EU-SAAB-99-SEDAN-2D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/3018395/saab_99_l_2-door.html
EU-NISSAN-SUNNY-N14-SEDAN-4D-01	4230	1690	1395	Auto-Data	https://www.auto-data.net/en/nissan-sunny-iii-n14-1.6-16v-90hp-467
EU-SAAB-99-COMBI-COUPE-HATCHBACK-3D-01	4530	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/3019145/saab_99_gl_combi_coupe_3-door.html
EU-SAAB-99-COMBI-COUPE-HATCHBACK-5D-01	4530	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1976/3019175/saab_99_gl_combi_coupe_5-door.html
EU-SAAB-99-SEDAN-4D-EARLY-01	4420	1690	1440	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/3018620/saab_99_le_4-door.html
EU-NISSAN-SUNNY-B12-COUPE-3D-01	4235	1665	1325	Auto-Data	https://www.auto-data.net/en/nissan-sunny-ii-coupe-b12-1.6-84hp-493
EU-NISSAN-SUNNY-B12-WAGON-5D-01	4270	1640	1385	Auto-Data	https://www.auto-data.net/en/nissan-sunny-model-71
EU-VOLVO-760-WAGON-FACELIFT-02	4785	1761	1435	Auto Motor und Sport	https://www.auto-motor-und-sport.de/marken-modelle/volvo/760/technische-daten/
EU-OPEL-KADETT-E-COMBO-VAN-3D-01	4221	1674	1670	Auto-Data	https://www.auto-data.net/en/opel-kadett-e-combo-1.7-td-60hp-1853
EU-BARKAS-B1000-VAN-MPV-4D-01	4520	1860	1910	WheelsAge	https://en.wheelsage.org/barkas/b1000/kb_kleinbus/specifications
EU-DACIA-1300-SEDAN-4D-01	4340	1636	1434	Dacia 1300 technical data	https://de.wikipedia.org/wiki/Dacia_1300
EU-DACIA-1310-SEDAN-EARLY-4D-01	4340	1636	1430	Carfolio	https://www.carfolio.com/dacia-1310-berline-229669
EU-DACIA-1310-SEDAN-MID-4D-01	4390	1615	1440	Auto-Data	https://www.auto-data.net/en/dacia-1310-1.6-72hp-15900
EU-DACIA-1310-SEDAN-LATE-4D-01	4351	1660	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1999/554375/dacia_1310_1_4.html
EU-RENAULT-20-127-HATCHBACK-PREFL-01	4520	1726	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/32690/renault_20_gtl.html
EU-RENAULT-20-127-HATCHBACK-FACELIFT-01	4520	1732	1435	Automobile-Catalog	https://www.automobile-catalog.com/car/1981/2930075/renault_20_tl.html
EU-RENAULT-FUEGO-136-COUPE-STANDARD-01	4358	1692	1315	Automobile-Catalog	https://www.automobile-catalog.com/car/1980/2930855/renault_fuego_gtl.html
EU-HYUNDAI-GENESIS-COUPE-BK-PREFL-COUPE-2D-01	4630	1864	1379	Auto-Data	https://www.auto-data.net/en/hyundai-genesis-coupe-generation-2968
EU-SAAB-9000-CD-SEDAN-02	4780	1764	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/3028310/saab_9000_cd_i_2_0-16.html
EU-SAAB-900-I-SEDAN-POST83-PREFL-01	4740	1690	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/3023330/saab_900_i_4-door.html
EU-SAAB-900-I-SEDAN-PRE83-01	4740	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/make/saab/900_1gen/900_1_1_4d/1982.html
EU-SAAB-900-I-SEDAN-FACELIFT-01	4680	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/3024920/saab_900_i_4-door.html
EU-TOYOTA-CAMRY-II-V20-SEDAN-4D-02	4500	1710	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1987/3551270/toyota_camry_1_8_xl.html
EU-SAAB-900-I-FACELIFT-TURBO16S-HATCHBACK-3D-01	4687	1695	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/3026510/saab_900_turbo_16_s_3-door.html
EU-SAAB-900-I-CONVERTIBLE-01	4680	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/make/saab/900_1gen/900_1gen_cabrio/1991.html
EU-TOYOTA-CARINA-V-T170-WAGON-01	4470	1690	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/3547295/toyota_carina_surf_1_8_sx_5speed.html
EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	4667	1764	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1991/3028445/saab_9000_2_0_turbo_automatic.html
EU-SAAB-900-I-PREFL-HATCHBACK-3D-01	4740	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/make/saab/900_1gen/900_1_1_3d/1986.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-3D-01	4687	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/1989/3024860/saab_900_i_3-door.html
EU-SAAB-900-I-PREFL-HATCHBACK-5D-01	4740	1690	1425	Automobile-Catalog	https://www.automobile-catalog.com/make/saab/900_1gen/900_1gen/1986.html
EU-SAAB-900-I-FACELIFT-HATCHBACK-5D-01	4687	1690	1420	Automobile-Catalog	https://www.automobile-catalog.com/make/saab/900_1gen/900_1_2_5d/1989.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6801-6900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1971/33305/alfa_romeo_giulia_1300_ti.html "https://www.automobile-catalog.com/car/1971/33305/alfa_romeo_giulia_1300_ti.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6801-6900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6801-6900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8660 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2689 行）

- 尺寸冲突协调：
  - EU-NISSAN-PATROL-IV-Y60-SUV-3D-01 -> EU-NISSAN-PATROL-IV-Y60-SUV-3D-02：4250x1800x1800 与 4240x1800x1790，创建新尺寸组
