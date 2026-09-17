# 任务：all 第 12601-12700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0127__df178409


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 12601-12700 行

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
all 第 12601-12700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-DODGE-CARAVAN-III-MPV-LWB-01	5070	1950	1740
EU-DODGE-CARAVAN-III-MPV-SWB-01	4733	1920	1740
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1832
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-LOWROOF-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-LWB-LOWROOF-01	4633	1722	1817
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-HIGHROOF-01	4253	1722	2086
EU-FIAT-DOBLO-I-223-CARGO-FACELIFT-SWB-LOWROOF-01	4253	1722	1831
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	4253	1722	2073
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	4253	1722	1818
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-HIGHROOF-01	4756	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-LWB-LOWROOF-01	4756	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-HIGHROOF-01	4406	1832	2125
EU-FIAT-DOBLO-II-263-CARGO-FACELIFT-SWB-LOWROOF-01	4406	1832	1845
EU-FIAT-DOBLO-II-263-CARGO-PREFL-LWB-LOWROOF-01	4740	1832	1880
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-HIGHROOF-01	4390	1832	2100
EU-FIAT-DOBLO-II-263-CARGO-PREFL-SWB-LOWROOF-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-FACELIFT-01	4577	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-LWB-PREFL-01	4561	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-FACELIFT-01	4227	1789	1845
EU-FIAT-DOBLO-II-263-CHASSIS-CAB-SWB-PREFL-01	4211	1789	1845
EU-FIAT-DOBLO-II-263-MPV-FACELIFT-01	4406	1832	1899
EU-FIAT-DOBLO-II-263-MPV-PREFL-01	4390	1832	1845
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-FACELIFT-01	4406	1832	2125
EU-FIAT-DOBLO-II-CARGO-HIGHROOF-PREFL-01	4390	1832	2100
EU-FIAT-DOBLO-II-CARGO-MAXI-FACELIFT-01	4756	1832	1880
EU-FIAT-DOBLO-II-CARGO-MAXI-PREFL-01	4740	1832	1880
EU-FIAT-DOBLO-II-CARGO-SWB-FACELIFT-01	4406	1832	1845
EU-FIAT-DOBLO-II-CARGO-SWB-PREFL-01	4390	1832	1845
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
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-DOUBLECAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L1-01	4908	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L2-01	5358	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L3-01	5708	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L4-01	5943	2050	2254
EU-FIAT-DUCATO-X250-CHASSIS-SINGLECAB-L5-01	6308	2050	2254
EU-FIAT-DUCATO-X250-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-X250-VAN-L1H2-01	4963	2050	2524
EU-FIAT-DUCATO-X250-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-X250-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-X250-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-X250-VAN-L4H2-01	6363	2050	2524
EU-FIAT-DUCATO-X250-VAN-L4H3-01	6363	2050	2764
EU-FIAT-SCUDO-I-COMBINATO-MPV-01	4440	1810	1940
EU-FIAT-SCUDO-II-VAN-L1H1-01	4805	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H1-01	5135	1895	1942
EU-FIAT-SCUDO-II-VAN-L2H2-01	5135	1895	2276
EU-JEEP-GRAND-CHEROKEE-III-WH-SUV-01	4750	1870	1740
EU-LADA-NIVA-2121-SUV-3D-01	3720	1680	1640
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-996-CARRERA-COUPE-01	4430	1765	1305
EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	4430	1765	1305
EU-PORSCHE-911-996-TARGA-FACELIFT-01	4430	1770	1305
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-0-SWB-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	4035	1672	1825
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
EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	4046	1672	1870
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	3995	1672	1835
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466
EU-SAAB-9-5-I-YS3E-SEDAN-FACELIFT-2001-01	4827	1792	1449
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	4828	1792	1501
EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	4841	1792	1459
EU-SAAB-9-5-I-YS3E-WAGON-PREFL-01	4808	1792	1492
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-3D-01	4180	1710	1475
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-5D-01	4180	1710	1475
EU-TOYOTA-COROLLA-IX-E120-HATCHBACK-COMPRESSOR-3D-01	4200	1710	1460
EU-TOYOTA-COROLLA-IX-E120-SEDAN-4D-01	4375	1710	1470
EU-TOYOTA-COROLLA-IX-E120-WAGON-5D-01	4375	1710	1500
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	4240	1710	1610
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	4100	1690	1380
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	4290	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	4270	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	4295	1690	1385
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	4340	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	4320	1690	1505
EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	4320	1690	1445
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493
EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	4850	1833	1454
EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	4822	1832	1434
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547
EU-VW-BORA-1J6-WAGON-5D-01	4409	1735	1485
EU-VW-GOLF-IV-1E7-CONVERTIBLE-2D-01	4081	1695	1425
EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	4149	1735	1439
EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	4149	1735	1439
EU-VW-GOLF-IV-1J5-WAGON-5D-01	4397	1735	1485

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Dodge	Caravan	3.3 I	Großraumlimousine	Frontantrieb	Benzin	116	158	Jan 1995	Mar 2001	2024-03-01	16414
Dodge	Caravan	3.8 I AWD	Großraumlimousine	Allrad	Benzin	122	166	Jan 1995	Mar 2001	2024-03-01	16415
Dodge	Caravan	3.8 I AWD	Großraumlimousine	Allrad	Benzin	131	178	Jan 1995	Mar 2001	2024-03-01	16416
Dodge	Caravan	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	85	116	Jan 1995	Mar 2001	2024-03-01	16417
Renault	Vel satis	2.0 16V Turbo	Schrägheck	Frontantrieb	Benzin	120	163	Jun 2002	Aug 2009	2024-03-01	16418
Renault	Vel satis	3.5 V6	Schrägheck	Frontantrieb	Benzin	177	241	Jun 2002	Aug 2009	2025-12-01	16419
Dodge	Caravan	3.8 I	Großraumlimousine	Frontantrieb	Benzin	122	166	Jan 1995	Mar 2001	2024-03-01	16420
Dodge	Caravan	3.8 I	Großraumlimousine	Frontantrieb	Benzin	131	178	Jan 1995	Mar 2001	2024-03-01	16421
Renault	Vel satis	2.2 DCI	Schrägheck	Frontantrieb	Diesel	110	150	Jun 2002	Aug 2009	2024-03-01	16422
Renault	Vel satis	3.0 DCI	Schrägheck	Frontantrieb	Diesel	130	177	Jun 2002	Jun 2006	2024-03-01	16423
Plymouth	Voyager / grand	2.0 I	Großraumlimousine	Frontantrieb	Benzin	98	133	Jan 1995	Mar 2001	2024-03-01	16424
Plymouth	Voyager / grand	2.4 I	Großraumlimousine	Frontantrieb	Benzin	111	151	Jan 1995	Mar 2001	2024-03-01	16425
Plymouth	Voyager / grand	3	Großraumlimousine	Frontantrieb	Benzin	112	152	Jan 1995	Mar 2001	2024-03-01	16426
Plymouth	Voyager / grand	3.3 I	Großraumlimousine	Frontantrieb	Benzin	116	158	Jan 1995	Mar 2001	2024-03-01	16427
Plymouth	Voyager / grand	3.8 I	Großraumlimousine	Frontantrieb	Benzin	122	166	Jan 1995	Mar 2001	2024-03-01	16428
Plymouth	Voyager / grand	3.8 I AWD	Großraumlimousine	Allrad	Benzin	122	166	Jan 1995	Mar 2001	2024-03-01	16429
Plymouth	Voyager / grand	3.8 I	Großraumlimousine	Frontantrieb	Benzin	131	178	Jan 1995	Mar 2001	2024-03-01	16430
Plymouth	Voyager / grand	3.8 I AWD	Großraumlimousine	Allrad	Benzin	131	178	Jan 1995	Mar 2001	2024-03-01	16431
Plymouth	Voyager / grand	2.5 TD	Großraumlimousine	Frontantrieb	Diesel	85	116	Jan 1995	Mar 2001	2024-03-01	16432
Chrysler	Voyager iv	3.8	Großraumlimousine	Frontantrieb	Benzin	160	218	Feb 2000	Dec 2008	2024-03-01	16433
Chrysler	Voyager iv	3.8 AWD	Großraumlimousine	Allrad	Benzin	160	218	Feb 2000	Dec 2008	2024-03-01	16434
Chrysler	Voyager iv	3.3 AWD	Großraumlimousine	Allrad	Benzin	128	174	Feb 2000	Dec 2008	2024-03-01	16435
Dodge	Caravan	3.3	Großraumlimousine	Frontantrieb	Benzin	128	174	Feb 2000	Dec 2007	2024-03-01	16436
Dodge	Caravan	3.3 AWD	Großraumlimousine	Allrad	Benzin	128	174	Feb 2000	Dec 2007	2024-03-01	16437
Dodge	Caravan	3.8	Großraumlimousine	Frontantrieb	Benzin	160	218	Feb 2000	Dec 2007	2024-03-01	16438
Dodge	Caravan	3.8 AWD	Großraumlimousine	Allrad	Benzin	160	218	Feb 2000	Dec 2007	2024-03-01	16439
Dodge	Caravan	2.4	Großraumlimousine	Frontantrieb	Benzin	112	152	Feb 2000	Dec 2007	2024-03-01	16440
Alfa Romeo	147	1.9 JTD	Schrägheck	Frontantrieb	Diesel	85	115	Apr 2001	Mar 2010	2024-03-01	16441
Saab	9-5	2.3 Turbo	Kombi	Frontantrieb	Benzin	184	250	Sep 2001	Dec 2009	2024-03-01	16442
Mitsubishi	Space star	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	72	98	Jan 2001	Dec 2004	2024-03-01	16443
Mitsubishi	Galant viii	2	Stufenheck	Frontantrieb	Benzin	98	133	Sep 2000	Oct 2004	2024-03-01	16444
Mitsubishi	Galant viii	2.4 GDI	Stufenheck	Frontantrieb	Benzin	106	144	Sep 2000	Oct 2004	2024-03-01	16445
Mitsubishi	Galant viii	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	118	160	Sep 2000	Oct 2004	2024-03-01	16446
Mitsubishi	Galant viii	2	Kombi	Frontantrieb	Benzin	98	133	Sep 2000	Oct 2003	2024-03-01	16447
Mitsubishi	Galant viii	2.4 GDI	Kombi	Frontantrieb	Benzin	106	144	Sep 2000	Oct 2003	2024-03-01	16448
Mitsubishi	Galant viii	2.5 V6 24V	Kombi	Frontantrieb	Benzin	118	160	Sep 2000	Oct 2003	2024-03-01	16449
Opel	Vectra c	2.2 16V	Stufenheck	Frontantrieb	Benzin	108	147	Apr 2002	Dec 2008	2024-03-01	16450
Opel	Vectra c	2.2 DTI 16V	Stufenheck	Frontantrieb	Diesel	92	125	Apr 2002	Jul 2004	2024-03-01	16451
Ford	Mondeo iii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	96	130	Oct 2001	Mar 2007	2024-03-01	16452
Ford	Mondeo iii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	96	130	Oct 2001	Mar 2007	2024-03-01	16453
Ford	Mondeo iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	96	130	Oct 2001	Mar 2007	2024-03-01	16454
Mitsubishi	Pajero iii canvas top	3.2 Di-d	Geländewagen offen	Allrad	Diesel	118	160	Oct 2001	Dec 2006	2024-03-01	16455
Fiat	Scudo	1.9 D	Kasten	Frontantrieb	Diesel	51	69	Apr 1998	Dec 2006	2024-03-01	16456
Fiat	Doblo	1.9 JTD	Großraumlimousine	Frontantrieb	Diesel	74	100	Oct 2001	-	2024-03-01	16457
Opel	Vectra c	2.0 DTI 16V	Stufenheck	Frontantrieb	Diesel	74	101	Apr 2002	Aug 2006	2024-03-01	16458
Opel	Vectra c	1.8 16V	Stufenheck	Frontantrieb	Benzin	90	122	Apr 2002	Sep 2008	2024-03-01	16459
Porsche	911	3.6 Carrera	Coupe	Heckantrieb	Benzin	235	320	Oct 2001	Aug 2004	2024-03-01	16460
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	235	320	Oct 2001	Aug 2004	2024-03-01	16461
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	235	320	Oct 2001	Aug 2005	2024-03-01	16462
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	235	320	Oct 2001	Aug 2005	2024-03-01	16463
Audi	A4 b6 avant	1.8 T Quattro	Kombi	Allrad	Benzin	110	150	Sep 2001	Jul 2002	2024-03-01	16464
Audi	A4 b6 avant	3.0 Quattro	Kombi	Allrad	Benzin	162	220	Sep 2001	Dec 2004	2024-03-01	16465
Opel	Movano a	1.9 DTI	Bus	Frontantrieb	Diesel	60	82	Oct 2001	-	2024-03-01	16466
Opel	Movano a	1.9 DTI	Kasten	Frontantrieb	Diesel	60	82	Oct 2001	-	2024-03-01	16467
Opel	Movano a	2.5 DTI	Bus	Frontantrieb	Diesel	84	115	Oct 2001	-	2024-03-01	16468
Opel	Movano a	2.5 DTI	Kasten	Frontantrieb	Diesel	84	115	Oct 2001	-	2024-03-01	16470
Opel	Movano a	2.5 DTI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	115	Oct 2001	-	2024-03-01	16471
Volvo	S40 i	1.8 I	Stufenheck	Frontantrieb	Benzin	90	122	Jun 2001	Dec 2003	2024-03-01	16472
Volvo	V40	1.8 I	Kombi	Frontantrieb	Benzin	90	122	Jun 2001	Jun 2004	2024-03-01	16473
Volvo	S80 i	3	Stufenheck	Frontantrieb	Benzin	144	196	Jun 2001	Jul 2006	2024-03-01	16474
Volvo	S80 i	T6	Stufenheck	Frontantrieb	Benzin	200	272	Jun 2001	Jul 2006	2024-03-01	16475
Volvo	S80 i	2.4 D	Stufenheck	Frontantrieb	Diesel	96	131	Oct 2001	Jul 2006	2024-03-01	16476
Jeep	Grand cherokee ii	2.7 CRD 4X4	Geländewagen geschlossen	Allrad	Diesel	120	163	Oct 2001	Sep 2005	2024-03-01	16477
Jeep	Grand cherokee ii	4.7 V8 4X4	Geländewagen geschlossen	Allrad	Benzin	190	258	Oct 2001	Sep 2005	2024-03-01	16478
Lada	110	1.5	Stufenheck	Frontantrieb	Benzin	56	76	Oct 2000	Dec 2005	2024-03-01	16479
Lada	110	1.5 16V	Stufenheck	Frontantrieb	Benzin	67	91	Oct 2000	Dec 2010	2024-03-01	16480
Lada	111	1.5	Kombi	Frontantrieb	Benzin	56	76	Oct 2000	Feb 2009	2024-03-01	16481
Lada	111	1.5 16V	Kombi	Frontantrieb	Benzin	67	91	Oct 2000	Dec 2005	2024-03-01	16482
Lada	112	1.5 16V	Schrägheck	Frontantrieb	Benzin	67	91	Oct 2000	Dec 2005	2024-03-01	16483
Lada	112	1.5	Schrägheck	Frontantrieb	Benzin	56	76	Oct 2000	Dec 2005	2024-03-01	16484
Lada	Niva	1700 I 4X4	Geländewagen geschlossen	Allrad	Benzin	60	82	Oct 2000	Dec 2015	2024-03-01	16485
Fiat	Ducato	2.0 JTD	Kasten	Frontantrieb	Diesel	62	84	Oct 2001	Apr 2002	2024-03-01	16486
Fiat	Ducato	2.0 JTD	Bus	Frontantrieb	Diesel	62	84	Oct 2001	Apr 2002	2024-03-01	16487
Renault	Master ii	2.5 DCI 120	Bus	Frontantrieb	Diesel	84	115	Oct 2001	Dec 2006	2024-08-01	16488
Renault	Master ii	2.5 DCI 120	Kasten	Frontantrieb	Diesel	84	115	Oct 2001	Sep 2007	2024-08-01	16489
Renault	Master ii	2.5 DCI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	115	Oct 2001	May 2010	2024-08-01	16490
Renault	Master ii	1.9 DCI 80	Bus	Frontantrieb	Diesel	60	82	Nov 2001	Oct 2006	2024-08-01	16491
Renault	Master ii	1.9 DCI 80	Kasten	Frontantrieb	Diesel	60	82	Nov 2001	Oct 2006	2024-08-01	16492
Volvo	V70 ii	2.0 T	Kombi	Frontantrieb	Benzin	132	180	Nov 1999	Aug 2007	2024-03-01	16493
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	115	156	Oct 2000	Aug 2003	2024-03-01	16494
Volvo	V70 ii	2.4 T AWD	Kombi	Allrad	Benzin	147	200	Sep 2001	Aug 2002	2024-03-01	16495
Opel	Omega b	2	Stufenheck	Heckantrieb	Benzin	85	115	Mar 1994	Dec 2000	2024-03-01	16496
Renault	Kangoo	1.9 DCI 4X4	Großraumlimousine	Allrad	Diesel	59	80	Oct 2001	-	2024-03-01	16500
Renault	Kangoo	1.6 16V 4X4	Kasten/Großraumlimousine	Allrad	Benzin	70	95	Oct 2001	-	2024-03-01	16501
Renault	Kangoo	1.9 DCI 4X4	Kasten/Großraumlimousine	Allrad	Diesel	59	80	Oct 2001	-	2024-03-01	16502
Renault	Kangoo	1.2 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	Oct 2001	-	2024-03-01	16503
Renault	Kangoo	1.6 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin	70	95	Oct 2001	Mar 2018	2025-12-01	16504
Lancia	Thesis	3.0 V6	Stufenheck	Frontantrieb	Benzin	158	215	Jul 2002	Jul 2009	2024-03-01	16505
Mitsubishi	Pajero pinin i	1.8	Geländewagen geschlossen	Allrad	Benzin	84	114	Nov 2001	Jun 2007	2024-03-01	16506
Mazda	Premacy	2	Großraumlimousine	Frontantrieb	Benzin	96	131	Nov 2001	Mar 2005	2024-03-01	16507
Mazda	Tribute	2	SUV	Frontantrieb	Benzin	91	124	Mar 2000	May 2008	2024-03-01	16508
VW	Golf iv	1.6 FSI	Schrägheck	Frontantrieb	Benzin	81	110	Jan 2002	Jun 2005	2024-03-01	16509
VW	Golf iv variant	1.6 FSI	Kombi	Frontantrieb	Benzin	81	110	Jan 2002	Jun 2006	2024-03-01	16510
VW	Bora	1.6 FSI	Stufenheck	Frontantrieb	Benzin	81	110	Jan 2002	May 2005	2024-03-01	16511
VW	Bora	1.6 FSI	Kombi	Frontantrieb	Benzin	81	110	Jan 2002	May 2005	2024-03-01	16512
Fiat	Doblo	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	76	103	Oct 2001	-	2024-03-01	16513
Toyota	Corolla	1.8 Vvt-i	Großraumlimousine	Frontantrieb	Benzin	99	135	Dec 2001	May 2004	2024-03-01	16514
Daewoo	Rezzo	1.8	Großraumlimousine	Frontantrieb	Benzin	72	98	Sep 2000	-	2024-03-01	16515
Daewoo	Rezzo	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Sep 2000	-	2024-03-01	16517
Daewoo	Rezzo	2	Großraumlimousine	Frontantrieb	Benzin	89	121	Sep 2001	Dec 2004	2024-03-01	16518


--- Round 1 / 首次发送 ---
## 更新点

* 复用 19 个跨批次既有尺寸组，新增闭合 41 条映射，覆盖 28 个输入 Ktype。
* Dodge Caravan III 与 Plymouth Voyager III 已按 SWB/LWB 拆分；3.8 AWD 仅关联长轴距组。Voyager 与 Grand Voyager 的车身分支及 3.0/3.3/3.8、AWD 配置边界已按 Plymouth 官方规格表核对。
* Saab 9-5、Volvo S80、Opel Omega B 中跨越外廓变化的 Ktype 已拆分改款分支。
* 本轮全部复用既有尺寸组，没有重复输出或重新抓取尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：28
* READY 映射：41
* 尚未闭合 Ktype：72
* 当前已引用尺寸组：19
* 本轮新建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16414_swb	16414	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	短轴距分支。	READY
16414_lwb	16414	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	长轴距分支。	READY
16415	16415	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	AWD长轴距分支。	READY
16416	16416	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	AWD长轴距分支。	READY
16420_swb	16420	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	短轴距分支。	READY
16420_lwb	16420	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	长轴距分支。	READY
16421_swb	16421	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	短轴距分支。	READY
16421_lwb	16421	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	长轴距分支。	READY
16426_swb	16426	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	Voyager短轴距分支。	READY
16426_lwb	16426	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager长轴距分支。	READY
16427_swb	16427	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	Voyager短轴距分支。	READY
16427_lwb	16427	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager长轴距分支。	READY
16428_swb	16428	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	Voyager短轴距分支。	READY
16428_lwb	16428	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager长轴距分支。	READY
16429	16429	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager AWD长轴距分支。	READY
16430_swb	16430	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	Voyager短轴距分支。	READY
16430_lwb	16430	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager长轴距分支。	READY
16431	16431	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	Grand Voyager AWD长轴距分支。	READY
16442_facelift2001	16442	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2001-01	HIGH	2001改款外廓。	READY
16442_facelift2005	16442	Wagon	9-5 I	YS3E	5	EU-SAAB-9-5-I-YS3E-WAGON-FACELIFT-2005-01	HIGH	2005改款外廓。	READY
16460	16460	Coupe	911 (996)	996	2	EU-PORSCHE-911-996-CARRERA-COUPE-01	HIGH		READY
16461	16461	Coupe	911 (996)	996	2	EU-PORSCHE-911-996-CARRERA-COUPE-01	HIGH		READY
16462	16462	Convertible	911 (996)	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH		READY
16463	16463	Convertible	911 (996)	996	2	EU-PORSCHE-911-996-CONVERTIBLE-CARRERA-01	HIGH		READY
16472	16472	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
16473	16473	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
16474_prefl	16474	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16474_facelift	16474	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
16475_prefl	16475	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16475_facelift	16475	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
16476_prefl	16476	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-PREFL-01	HIGH	改款前外廓。	READY
16476_facelift	16476	Sedan	S80 I	P2	4	EU-VOLVO-S80-I-P2-SEDAN-4D-FACELIFT-01	HIGH	改款后外廓。	READY
16485	16485	SUV	Niva 2121	2121	3	EU-LADA-NIVA-2121-SUV-3D-01	HIGH		READY
16496_prefl	16496	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	MEDIUM	改款前外廓。	READY
16496_facelift	16496	Sedan	Omega B		4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	MEDIUM	改款后外廓。	READY
16500	16500	MPV	Kangoo I	KC	5	EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	HIGH	四驱乘用车身。	READY
16509_3dr	16509	Hatchback	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-HATCHBACK-3D-01	HIGH	三门外廓。	READY
16509_5dr	16509	Hatchback	Golf IV	1J1	5	EU-VW-GOLF-IV-1J1-HATCHBACK-5D-01	HIGH	五门外廓。	READY
16510	16510	Wagon	Golf IV	1J5	5	EU-VW-GOLF-IV-1J5-WAGON-5D-01	HIGH		READY
16512	16512	Wagon	Bora I	1J6	5	EU-VW-BORA-1J6-WAGON-5D-01	HIGH		READY
16514	16514	MPV	Corolla Verso I	E120	5	EU-TOYOTA-COROLLA-VERSO-I-E120-MPV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合第三代 Voyager/Caravan 剩余的 2.0、2.4、2.5 TD 分支，以及第四代 Chrysler/Dodge Voyager/Caravan 的 SWB/LWB、FWD/AWD 边界。
2. 集中创建 Vel Satis、Alfa 147、Space Star、Galant VIII、Vectra C、Mondeo III 等乘用车型尺寸组。
3. 最后按轴距、车顶和车身形式批量处理 Movano A、Master II、Ducato、Doblo、Kangoo 等多外廓商用车。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 9 条 READY 映射，闭合 Vel Satis 4 个 Ktype、Alfa Romeo 147 1 个 Ktype，以及 Mondeo III 3 个 Ktype。
* 首次创建 Vel Satis 五门尺寸组，官方车型手册尺寸为 4860 × 1860 × 1577 mm。([汽车档案馆][1])
* Alfa Romeo 147 1.9 JTD 85 kW 已按官方资料确认同时存在三门和五门车身，分别建组；两者尺寸均为 4170 × 1729 × 1442 mm。([Stellantis Media][2])
* Mondeo III 按 Hatchback、Sedan、Wagon 三种物理车身建组；宽度均采用官方手册明确标注的不含后视镜口径。([汽车档案馆][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：36
* READY 映射：50
* PENDING Ktype：64
* 已确认并引用尺寸组：25
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16418	16418	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-HATCHBACK-5D-01	HIGH		READY
16419	16419	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-HATCHBACK-5D-01	HIGH		READY
16422	16422	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-HATCHBACK-5D-01	HIGH		READY
16423	16423	Hatchback	Vel Satis I		5	EU-RENAULT-VEL-SATIS-I-HATCHBACK-5D-01	HIGH		READY
16441_3dr	16441	Hatchback	147 I		3	EU-ALFA-ROMEO-147-I-HATCHBACK-3D-PREFL-01	HIGH	三门物理车身分支。	READY
16441_5dr	16441	Hatchback	147 I		5	EU-ALFA-ROMEO-147-I-HATCHBACK-5D-PREFL-01	HIGH	五门物理车身分支。	READY
16452	16452	Hatchback	Mondeo III		5	EU-FORD-MONDEO-III-HATCHBACK-5D-01	HIGH		READY
16453	16453	Sedan	Mondeo III		4	EU-FORD-MONDEO-III-SEDAN-4D-01	HIGH		READY
16454	16454	Wagon	Mondeo III		5	EU-FORD-MONDEO-III-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-VEL-SATIS-I-HATCHBACK-5D-01	4860	1860	1577	Renault Vel Satis official brochure 2008 FR	https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Vel-Satis-2008-FR-.pdf
EU-ALFA-ROMEO-147-I-HATCHBACK-3D-PREFL-01	4170	1729	1442	Alfa Romeo UK official press technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-ALFA-ROMEO-147-I-HATCHBACK-5D-PREFL-01	4170	1729	1442	Alfa Romeo UK official press technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147
EU-FORD-MONDEO-III-HATCHBACK-5D-01	4731	1812	1429	Ford Mondeo official brochure 2004 UK	https://autocatalogarchive.com/wp-content/uploads/2022/12/Ford-Mondeo-2004-UK.pdf
EU-FORD-MONDEO-III-SEDAN-4D-01	4731	1812	1429	Ford Mondeo official brochure 2004 UK	https://autocatalogarchive.com/wp-content/uploads/2022/12/Ford-Mondeo-2004-UK.pdf
EU-FORD-MONDEO-III-WAGON-5D-01	4804	1812	1441	Ford Mondeo official brochure 2004 UK	https://autocatalogarchive.com/wp-content/uploads/2022/12/Ford-Mondeo-2004-UK.pdf
```

## 下一步优先处理

1. 集中闭合 Mitsubishi Space Star、Galant VIII Sedan/Wagon。
2. 批量处理 Vectra C 四个相同代际 Sedan Ktype，先确认具体功率版本对应的改款边界。
3. 继续处理 Pajero III Canvas Top、Scudo I、Doblo I 等尚未闭合的相邻车型。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2019/04/Renault-Vel-Satis-2008-FR-.pdf?utm_source=chatgpt.com "VEL SATIS"
[2]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-performance-diesel-for-alfa-147?utm_source=chatgpt.com "NEW PERFORMANCE DIESEL FOR ALFA 147 | Alfa Romeo"
[3]: https://autocatalogarchive.com/wp-content/uploads/2022/12/Ford-Mondeo-2004-UK.pdf?utm_source=chatgpt.com "!\"#$%!!\"#$%\"&"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Opel Vectra C Sedan 的 4 个 Ktype；其中 16450、16458、16459 的输入生产区间跨越 2005 年外廓改款，拆分为改款前后分支。
* 首次建立两个 Sedan 尺寸组：改款前为 4596 × 1798 × 1460 mm；改款后为 4611 × 1798 × 1460 mm。两份官方规格均明确区分车身宽度与含后视镜宽度，落盘采用不含后视镜的 1798 mm。([Dezo's Garage][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：40
* READY 映射：57
* PENDING Ktype：60
* 已确认并引用尺寸组：27
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16450_prefl	16450	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-PREFL-01	MEDIUM	输入生产区间跨越改款；改款前外廓。	READY
16450_facelift	16450	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-FACELIFT-01	MEDIUM	输入生产区间跨越改款；改款后外廓。	READY
16451	16451	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-PREFL-01	HIGH	生产区间止于改款前。	READY
16458_prefl	16458	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-PREFL-01	MEDIUM	输入生产区间跨越改款；改款前外廓。	READY
16458_facelift	16458	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-FACELIFT-01	MEDIUM	输入生产区间跨越改款；改款后外廓。	READY
16459_prefl	16459	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-PREFL-01	HIGH	输入生产区间跨越改款；改款前外廓。	READY
16459_facelift	16459	Sedan	Vectra C		4	EU-OPEL-VECTRA-C-SEDAN-4D-FACELIFT-01	HIGH	输入生产区间跨越改款；改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VECTRA-C-SEDAN-4D-PREFL-01	4596	1798	1460	Holden Vectra official brochure 2003 AUS	https://xr793.com/wp-content/uploads/2023/05/2003-Holden-Vectra-AUS.pdf
EU-OPEL-VECTRA-C-SEDAN-4D-FACELIFT-01	4611	1798	1460	Vauxhall New Vectra official specifications 2006 UK	https://xr793.com/wp-content/uploads/2022/11/2006-Vauxhall-Vectra-New-Signum-UK.pdf
```

## 下一步优先处理

1. 集中闭合 Mitsubishi Space Star 的改款前后分支，以及 Galant VIII Sedan/Wagon 共 7 个 Ktype。
2. 随后处理 Pajero III Canvas Top、Pajero Pinin、Mazda Premacy、Mazda Tribute 等单一或少分支车身。
3. 商用车簇继续按车型、轴距、车顶和 Bus/Van/Chassis 分组批量建组。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2023/05/2003-Holden-Vectra-AUS.pdf?utm_source=chatgpt.com "vectra"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Mitsubishi Space Star 16443；其生产区间跨越 2002 年 6 月外廓变更，拆分为改款前后两个物理分支。
* 改款前 Space Star 为 4030 × 1700 × 1515 mm，改款后为 4050 × 1695 × 1515 mm，宽度均为不含后视镜口径。([汽车目录][1])
* 闭合 Mitsubishi Galant VIII 的 6 个 Ktype，Sedan 三个动力版本复用一个尺寸组，Wagon 三个动力版本复用另一个尺寸组。
* Galant VIII Sedan 为 4630 × 1740 × 1415 mm，Wagon 为 4680 × 1740 × 1495 mm；各动力版本的外廓数据一致，宽度均明确为不含后视镜。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：47
* READY 映射：65
* PENDING Ktype：53
* 已确认并引用尺寸组：31
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16443_prefl	16443	MPV	Space Star I	DG0	5	EU-MITSUBISHI-SPACE-STAR-I-DG0-MPV-5D-PREFL-01	HIGH	生产区间跨越2002年外廓变更；改款前分支。	READY
16443_facelift	16443	MPV	Space Star I	DG0	5	EU-MITSUBISHI-SPACE-STAR-I-DG0-MPV-5D-FACELIFT-01	HIGH	生产区间跨越2002年外廓变更；改款后分支。	READY
16444	16444	Sedan	Galant VIII		4	EU-MITSUBISHI-GALANT-VIII-SEDAN-4D-01	HIGH		READY
16445	16445	Sedan	Galant VIII		4	EU-MITSUBISHI-GALANT-VIII-SEDAN-4D-01	HIGH		READY
16446	16446	Sedan	Galant VIII		4	EU-MITSUBISHI-GALANT-VIII-SEDAN-4D-01	HIGH		READY
16447	16447	Wagon	Galant VIII		5	EU-MITSUBISHI-GALANT-VIII-WAGON-5D-01	HIGH		READY
16448	16448	Wagon	Galant VIII		5	EU-MITSUBISHI-GALANT-VIII-WAGON-5D-01	HIGH		READY
16449	16449	Wagon	Galant VIII		5	EU-MITSUBISHI-GALANT-VIII-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-STAR-I-DG0-MPV-5D-PREFL-01	4030	1700	1515	Automobile-Catalog 2002 Mitsubishi Space Star 1.6 pre-facelift specifications	https://www.automobile-catalog.com/car/2002/2008085/mitsubishi_space_star_1_6.html
EU-MITSUBISHI-SPACE-STAR-I-DG0-MPV-5D-FACELIFT-01	4050	1695	1515	Automobile-Catalog 2002 Mitsubishi Space Star 1.6 facelift specifications	https://www.automobile-catalog.com/car/2002/2008190/mitsubishi_space_star_1_6.html
EU-MITSUBISHI-GALANT-VIII-SEDAN-4D-01	4630	1740	1415	Automobile-Catalog 2001 Mitsubishi Galant 2.0 Europe specifications	https://www.automobile-catalog.com/car/2001/2001635/mitsubishi_galant_2_0.html
EU-MITSUBISHI-GALANT-VIII-WAGON-5D-01	4680	1740	1495	Automobile-Catalog 2001 Mitsubishi Galant Wagon 2.0 Europe specifications	https://www.automobile-catalog.com/car/2001/2001725/mitsubishi_galant_wagon_2_0.html
```

## 下一步优先处理

1. 闭合 Pajero III Canvas Top、Pajero Pinin、Mazda Premacy、Mazda Tribute 等少分支车型。
2. 批量处理 Lada 110、111、112，以及 Lancia Thesis、Daewoo Rezzo 等单一乘用车外廓。
3. 随后集中处理 Movano A、Master II、Ducato、Scudo、Doblo 和 Kangoo 的轴距、车顶及 Bus/Van/Chassis 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/2008085/mitsubishi_space_star_1_6.html?utm_source=chatgpt.com "2001 Mitsubishi Space Star 1.6 Specs Review (72 kW / 98 PS / 97 hp) (since March 2001 for Europe Germany)"
[2]: https://www.automobile-catalog.com/car/2001/2001635/mitsubishi_galant_2_0.html?utm_source=chatgpt.com "2001 Mitsubishi Galant 2.0 Specs Review (98 kW / 133 PS / 131 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Jeep Grand Cherokee II 的 2 个 Ktype；2.7 CRD 与 4.7 V8 采用相同 WJ 五门外廓。([汽车目录][1])
* 闭合 Lada 110、111、112 共 6 个 Ktype，分别建立 Sedan、Wagon、Hatchback 三个尺寸组。([AutoEvolution][2])
* 闭合 Lancia Thesis 3.0 V6、Mazda Premacy 2.0、Mazda Tribute 2.0，以及 Daewoo Rezzo 的 1.6、1.8、2.0 Ktype。Premacy 和 Tribute 的宽度来源明确为不含后视镜。([ManualsLib][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：61
* READY 映射：79
* PENDING Ktype：39
* 已确认并引用尺寸组：39
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16477	16477	SUV	Grand Cherokee II	WJ	5	EU-JEEP-GRAND-CHEROKEE-II-WJ-SUV-5D-01	HIGH		READY
16478	16478	SUV	Grand Cherokee II	WJ	5	EU-JEEP-GRAND-CHEROKEE-II-WJ-SUV-5D-01	HIGH		READY
16479	16479	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	HIGH		READY
16480	16480	Sedan	110	2110	4	EU-LADA-110-2110-SEDAN-4D-01	HIGH		READY
16481	16481	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
16482	16482	Wagon	111	2111	5	EU-LADA-111-2111-WAGON-5D-01	HIGH		READY
16483	16483	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
16484	16484	Hatchback	112	2112	5	EU-LADA-112-2112-HATCHBACK-5D-01	HIGH		READY
16505	16505	Sedan	Thesis I	841	4	EU-LANCIA-THESIS-I-841-SEDAN-4D-V6-01	HIGH	3.0 V6高度分支。	READY
16507	16507	MPV	Premacy I	CP	5	EU-MAZDA-PREMACY-I-CP-MPV-5D-FACELIFT-01	HIGH		READY
16508	16508	SUV	Tribute I	EP	5	EU-MAZDA-TRIBUTE-I-EP-SUV-5D-2-0-01	HIGH	2.0窄体外廓。	READY
16515	16515	MPV	Rezzo I	KLAU	5	EU-DAEWOO-REZZO-I-KLAU-MPV-5D-01	MEDIUM		READY
16517	16517	MPV	Rezzo I	KLAU	5	EU-DAEWOO-REZZO-I-KLAU-MPV-5D-01	HIGH		READY
16518	16518	MPV	Rezzo I	KLAU	5	EU-DAEWOO-REZZO-I-KLAU-MPV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-GRAND-CHEROKEE-II-WJ-SUV-5D-01	4611	1858	1805	Automobile-Catalog 2002 Jeep Grand Cherokee 2.7 CRD Europe specifications	https://www.automobile-catalog.com/car/2002/1323410/jeep_grand_cherokee_2_7_crd_laredo_quadra-trac_ii.html
EU-LADA-110-2110-SEDAN-4D-01	4260	1679	1420	Autoevolution Lada 110 specifications	https://www.autoevolution.com/cars/lada-110-1998.html
EU-LADA-111-2111-WAGON-5D-01	4280	1679	1499	Autoevolution Lada 111 specifications	https://www.autoevolution.com/cars/lada-111-1999.html
EU-LADA-112-2112-HATCHBACK-5D-01	4171	1679	1420	Autoevolution Lada 112 specifications	https://www.autoevolution.com/cars/lada-112-1999.html
EU-LANCIA-THESIS-I-841-SEDAN-4D-V6-01	4888	1830	1470	Lancia Thesis official owner's handbook	https://www.manualslib.com/manual/454195/Lancia-Thesis.html
EU-MAZDA-PREMACY-I-CP-MPV-5D-FACELIFT-01	4340	1705	1600	Automobile-Catalog 2002 Mazda Premacy 2.0 Sportive Europe specifications	https://www.automobile-catalog.com/car/2002/1668770/mazda_premacy_2_0_sportive.html
EU-MAZDA-TRIBUTE-I-EP-SUV-5D-2-0-01	4395	1800	1710	Automobile-Catalog 2001 Mazda Tribute 2.0L 4x2 Europe specifications	https://www.automobile-catalog.com/car/2001/1670855/mazda_tribute_2_0l_4x2.html
EU-DAEWOO-REZZO-I-KLAU-MPV-5D-01	4350	1755	1580	Automobile-Catalog 2001 Daewoo Rezzo/Tacuma 1.6 SX Europe specifications; Auto-Data Daewoo Rezzo KLAU 1.8 i specifications; Automobile-Catalog 2001 Daewoo Rezzo/Tacuma 2.0 CDX Europe specifications	https://www.automobile-catalog.com/car/2001/2056730/daewoo_rezzo_1_6_sx.html; https://www.auto-data.net/en/daewoo-rezzo-klau-1.8-i-101hp-16287; https://www.automobile-catalog.com/car/2001/557810/daewoo_rezzo_2_0_cdx.html
```

## 下一步优先处理

1. 闭合 Dodge/Plymouth Voyager III 剩余柴油和小排量 Ktype，以及 Chrysler/Dodge Voyager IV 的 SWB/LWB 分支。
2. 处理 Audi A4 B6 Avant、Volvo V70 II、Subaru Outback、VW Bora Sedan 等乘用车。
3. 最后集中处理 Movano A、Master II、Ducato、Scudo、Doblo、Kangoo 的轴距、车顶及车身形式分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/1323410/jeep_grand_cherokee_2_7_crd_laredo_quadra-trac_ii.html?utm_source=chatgpt.com "2002 Jeep Grand Cherokee 2.7 CRD Laredo Quadra-Trac II Specs Review (120 kW / 163 PS / 161 hp) (for Europe )"
[2]: https://www.autoevolution.com/cars/lada-110-1998.html "LADA 110 Specs, Performance & Photos - 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 - autoevolution"
[3]: https://www.manualslib.com/manual/454195/Lancia-Thesis.html "LANCIA THESIS OWNER'S HANDBOOK MANUAL Pdf Download | ManualsLib"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Audi A4 B6 Avant 两个 Ktype，1.8 T quattro 与 3.0 quattro 复用同一 8E5 Wagon 尺寸组；两种动力对应相同外廓。([汽车目录][1])
* 闭合 Volvo V70 II 两个 Ktype、Subaru Outback II 与 VW Bora Sedan 各一个 Ktype。Bora 尺寸采用 Volkswagen 官方车型档案。([encyCARpedia][2])
* Pajero Pinin 1.8 MPI 已确认覆盖三门和五门两种不同长度车身，拆分为两个派生映射和两个尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：68
* READY 映射：87
* PENDING Ktype：32
* 已确认并引用尺寸组：45
* 本轮新增 READY Ktype：7
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16464	16464	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16465	16465	Wagon	A4 B6	8E5	5	EU-AUDI-A4-B6-8E5-WAGON-5D-01	HIGH		READY
16493	16493	Wagon	V70 II	P26	5	EU-VOLVO-V70-II-P26-WAGON-5D-01	HIGH		READY
16494	16494	Wagon	Outback II	BH	5	EU-SUBARU-OUTBACK-II-BH-WAGON-5D-01	HIGH		READY
16495	16495	Wagon	V70 II	P26	5	EU-VOLVO-V70-II-P26-WAGON-5D-01	HIGH		READY
16506_3dr	16506	SUV	Pajero Pinin I		3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	三门短车身分支。	READY
16506_5dr	16506	SUV	Pajero Pinin I		5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	五门长车身分支。	READY
16511	16511	Sedan	Bora I	1J2	4	EU-VW-BORA-I-1J2-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B6-8E5-WAGON-5D-01	4548	1772	1428	Automobile-Catalog 2002 Audi A4 Avant 1.8 T Europe specifications; Automobile-Catalog 2002 Audi A4 Avant 3.0 Quattro Europe specifications	https://www.automobile-catalog.com/car/2002/246470/audi_a4_avant_1_8_t.html; https://www.automobile-catalog.com/car/2002/246905/audi_a4_avant_3_0_quattro.html
EU-VOLVO-V70-II-P26-WAGON-5D-01	4710	1804	1488	EncyCARpedia 2002 Volvo V70 2.0T specifications; Auto-Selection Volvo V70 2.4 T AWD specifications	https://www.encycarpedia.com/volvo/02-v70-2-0t-estate; https://www.auto-selection.com/fiche-technique/volvo/v70/2000/2-4-t-awd-200ch-727904
EU-SUBARU-OUTBACK-II-BH-WAGON-5D-01	4720	1745	1580	Automobile-Catalog 2002 Subaru Outback 2.5 AWD Europe specifications	https://www.automobile-catalog.com/car/2002/3251540/subaru_outback_2_5_awd.html
EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	3735	1695	1735	Automobile-Catalog 2001 Mitsubishi Pajero Pinin 1.8 MPI 3-door Europe specifications	https://www.automobile-catalog.com/car/2001/2013860/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_3door.html
EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	4035	1695	1735	Automobile-Catalog 2001 Mitsubishi Pajero Pinin 1.8 MPI 5-door Europe specifications	https://www.automobile-catalog.com/car/2001/2013890/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_5door.html
EU-VW-BORA-I-1J2-SEDAN-4D-01	4376	1735	1446	Volkswagen Newsroom Bora vehicle profile	https://www.volkswagen-newsroom.com/en/vehicle-data-bora-profile-19676
```

## 下一步优先处理

1. 闭合 Dodge/Plymouth Voyager III 剩余 2.0、2.4、2.5 TD Ktype，以及 Chrysler/Dodge Voyager IV 的 SWB/LWB 分支。
2. 处理 Pajero III Canvas Top 和 Fiat Scudo、Doblo、Ducato 的既有尺寸组复用。
3. 集中处理 Movano A、Master II 与 Kangoo 的 Bus、Van、Chassis、轴距及车顶分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2002/246470/audi_a4_avant_1_8_t.html?utm_source=chatgpt.com "2002 Audi A4 Avant 1.8 T Specs Review (110 kW / 150 PS / 148 hp) (up to mid-year 2002 for Europe )"
[2]: https://www.encycarpedia.com/volvo/02-v70-2-0t-estate?utm_source=chatgpt.com "2002 Volvo V70 2.0T Specifications & Performance"
[3]: https://www.automobile-catalog.com/car/2001/2013860/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_3door.html?utm_source=chatgpt.com "2001 Mitsubishi Pajero Pinin (Shogun Pinin) 1.8 MPI 3door Specs Review (84 kW / 114 PS / 113 hp) (since November 2001 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合第三代 Caravan/Voyager 剩余 4 个 Ktype：2.0 仅关联 SWB；2.4 覆盖 SWB/LWB；2.5 TD 覆盖 SWB/LWB。欧洲规格记录分别确认了这些发动机对应的短轴与长轴车身边界。([汽车目录][1])
* Fiat Scudo I Kasten 复用既有标准外廓尺寸组。
* Renault Kangoo I 的两个 4×4 混合车身 Ktype 复用既有四驱尺寸组；1.6 16V 与1.9 dCi 4×4采用相同外廓。([汽车目录][2])
* 本轮没有首次创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：75
* READY 映射：97
* PENDING Ktype：25
* 已确认并引用尺寸组：45
* 本轮新增 READY Ktype：7
* 本轮新增 READY 映射：10
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16417_swb	16417	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	2.5 TD短轴距分支。	READY
16417_lwb	16417	MPV	Caravan III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	2.5 TD长轴距分支。	READY
16424	16424	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	2.0仅覆盖短轴距外廓。	READY
16425_swb	16425	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	2.4短轴距分支。	READY
16425_lwb	16425	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	2.4长轴距分支。	READY
16432_swb	16432	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-SWB-01	HIGH	2.5 TD短轴距分支。	READY
16432_lwb	16432	MPV	Voyager III			EU-DODGE-CARAVAN-III-MPV-LWB-01	HIGH	2.5 TD长轴距分支。	READY
16456	16456	Van	Scudo I				EU-FIAT-SCUDO-I-COMBINATO-MPV-01	MEDIUM	标准短轴低顶外廓。	READY
16501	16501	Van/MPV	Kangoo I				EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	MEDIUM	货运与乘用版本共用四驱外廓。	READY
16502	16502	Van/MPV	Kangoo I				EU-RENAULT-KANGOO-I-KC-4X4-MPV-5D-01	MEDIUM	货运与乘用版本共用四驱外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Chrysler Voyager IV 与 Dodge Caravan IV 的 SWB/LWB、FWD/AWD 分支，并分别处理品牌保险杠造成的外廓差异。
2. 批量处理 Fiat Ducato 230 的 Van、Bus 轴距和车顶组合。
3. 继续处理 Doblo I、Kangoo I 前后改款，以及 Movano A、Master II 的多轴距商用车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1998/519755/chrysler_voyager_se_2_4.html?utm_source=chatgpt.com "1998 Chrysler Voyager SE 2.4 Specs Review (110 kW / 150 PS / 148 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2001/2948675/renault_kangoo_4x4_1_6_16v.html?utm_source=chatgpt.com "2001 Renault Kangoo 4x4 1.6 16V Specs Review (70 kW ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Chrysler Voyager IV 与 Dodge Caravan IV 共 8 个 Ktype，新增 12 条 READY 映射。
* Chrysler 3.8 FWD 与 3.3 AWD 均确认存在 SWB、LWB 两种外廓；3.8 AWD 当前直接闭合 SWB 分支。Chrysler SWB 为 4805 × 1995 × 1750 mm，LWB 为 5094 × 1997 × 1749 mm。([汽车数据][1])
* Dodge 3.3、3.8 FWD 按 SWB/LWB 拆分；3.3 AWD、3.8 AWD 仅关联 LWB；2.4 仅关联 SWB。Dodge SWB 为 4803 × 1996 × 1750 mm，LWB 为 5093 × 1995 × 1750 mm。([汽车数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* READY 映射：109
* PENDING Ktype：17
* 已确认并引用尺寸组：49
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16433_swb	16433	MPV	Voyager IV			EU-CHRYSLER-VOYAGER-IV-MPV-SWB-01	HIGH	短轴距分支。	READY
16433_lwb	16433	MPV	Voyager IV			EU-CHRYSLER-VOYAGER-IV-MPV-LWB-01	HIGH	长轴距分支。	READY
16434	16434	MPV	Voyager IV			EU-CHRYSLER-VOYAGER-IV-MPV-SWB-01	HIGH	短轴距四驱分支。	READY
16435_swb	16435	MPV	Voyager IV			EU-CHRYSLER-VOYAGER-IV-MPV-SWB-01	HIGH	短轴距四驱分支。	READY
16435_lwb	16435	MPV	Voyager IV			EU-CHRYSLER-VOYAGER-IV-MPV-LWB-01	HIGH	长轴距四驱分支。	READY
16436_swb	16436	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-SWB-01	HIGH	短轴距分支。	READY
16436_lwb	16436	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	长轴距分支。	READY
16437	16437	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	长轴距四驱分支。	READY
16438_swb	16438	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-SWB-01	HIGH	短轴距分支。	READY
16438_lwb	16438	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	长轴距分支。	READY
16439	16439	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-LWB-01	HIGH	长轴距四驱分支。	READY
16440	16440	MPV	Caravan IV			EU-DODGE-CARAVAN-IV-MPV-SWB-01	HIGH	短轴距分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-VOYAGER-IV-MPV-SWB-01	4805	1995	1750	Auto-Data Chrysler Voyager IV 3.8 i V6 specifications	https://www.auto-data.net/en/chrysler-voyager-iv-3.8-i-v6-218hp-14832
EU-CHRYSLER-VOYAGER-IV-MPV-LWB-01	5094	1997	1749	Auto-Data Chrysler Grand Voyager IV 3.8 i V6 specifications	https://www.auto-data.net/en/chrysler-grand-voyager-iv-3.8-i-v6-218hp-14771
EU-DODGE-CARAVAN-IV-MPV-SWB-01	4803	1996	1750	Auto-Data Dodge Caravan IV SWB specifications	https://www.auto-data.net/en/dodge-caravan-iv-swb-generation-690
EU-DODGE-CARAVAN-IV-MPV-LWB-01	5093	1995	1750	Auto-Data Dodge Caravan IV LWB specifications	https://www.auto-data.net/en/dodge-caravan-iv-lwb-generation-5779
```

## 下一步优先处理

1. 复用或补齐 Fiat Ducato 230 的 Van、Bus 轴距和车顶组合。
2. 闭合 Fiat Doblo I MPV 与 Renault Kangoo I 前后改款及 Van/MPV 分支。
3. 最后集中处理 Movano A、Master II 和 Pajero III Canvas Top。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/chrysler-grand-voyager-iv-3.8-i-v6-218hp-14771 "Chrysler Grand Voyager IV 3.8 i V6 (218 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/dodge-caravan-iv-lwb-3.3-v6-182hp-automatic-30008?utm_source=chatgpt.com "Dodge Caravan IV LWB 3.3 V6 (182 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 5 个 Ktype，新增 15 条 READY 映射。
* Fiat Ducato 230P 的 Van、Bus 分支，以及 Kangoo I 改款前后分支，全部直接复用既有尺寸组，本轮不重复输出尺寸事实。
* Pajero III Canvas Top 的该 Ktype 明确覆盖 V68W、V78W 两个车身代码，因此拆为三门短车身和五门长车身。三门外廓为 4280 × 1875 × 1845 mm，五门外廓为 4795 × 1885 × 1855 mm。([Meyer Motoren][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* READY 映射：124
* PENDING Ktype：12
* 已确认并引用尺寸组：61
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16455_3dr	16455	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-V68W-SUV-3D-01	HIGH	三门短车身分支。	READY
16455_5dr	16455	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-V78W-SUV-5D-01	HIGH	五门长车身分支。	READY
16486_swb_lowroof	16486	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	HIGH	短轴低顶分支。	READY
16486_swb_highroof	16486	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶分支。	READY
16486_mwb_lowroof	16486	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	HIGH	中轴低顶分支。	READY
16486_mwb_highroof	16486	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶分支。	READY
16486_lwb_highroof	16486	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶分支。	READY
16487_swb	16487	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	短轴客车分支。	READY
16487_mwb_highroof	16487	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	HIGH	中轴高顶客车分支。	READY
16503_prefl	16503	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	改款前16V外廓。	READY
16503_facelift_lowroof	16503	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	MEDIUM	改款后低车身分支。	READY
16503_facelift_highroof	16503	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	MEDIUM	改款后高车身分支。	READY
16504_prefl	16504	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-16V-01	HIGH	改款前16V外廓。	READY
16504_facelift_lowroof	16504	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-02	MEDIUM	改款后低车身分支。	READY
16504_facelift_highroof	16504	Van/MPV	Kangoo I	KC		EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	MEDIUM	改款后高车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-III-V68W-SUV-3D-01	4280	1875	1845	Automobile-Catalog 2001 Mitsubishi Pajero 3.2 DI-D Elegance 3door Europe specifications	https://www.automobile-catalog.com/car/2001/2015015/mitsubishi_pajero_3_2_di-d_elegance_3door_automatic.html
EU-MITSUBISHI-PAJERO-III-V78W-SUV-5D-01	4795	1885	1855	Auto-Data Mitsubishi Pajero III 3.2 DI-D specifications	https://www.auto-data.net/en/mitsubishi-pajero-iii-generation-3402
```

## 下一步优先处理

1. 闭合 Fiat Doblò I MPV 的 16457、16513，并处理改款前后及高低车身边界。
2. 集中建立 Opel Movano A 与 Renault Master II 共用平台下的 Bus、Van、Chassis、轴距和车顶尺寸组。
3. 剩余 12 个 Ktype 全部位于 Doblò、Movano、Master 三个车型簇。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/fahrzeuge/16455/mitsubishi/pajero_3_canvas_top_v6_v7_/3_2_di-d_v68w_v78w_?utm_source=chatgpt.com "3.2 DI-D (V68W, V78W) | Pajero 3 Canvas Top (V6, V7) | MITSUBISHI | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Fiat Doblò I 的 16457、16513 两个 Ktype。
* 首次创建改款前乘用版尺寸组，外廓为 4159 × 1714 × 1810 mm，宽度为不含后视镜口径。16457 仅关联改款前组；16513 按改款前、改款后低顶和改款后高顶三个物理分支拆分，后两个分支直接复用既有尺寸组。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：90
* READY 映射：128
* PENDING Ktype：10
* 已确认并引用尺寸组：62
* 本轮首次创建尺寸组：1
* 剩余 Ktype 全部集中于 Movano A / Master II 商用车簇。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16457	16457	MPV	Doblò I	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车外廓。	READY
16513_prefl	16513	MPV	Doblò I	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前乘用车外廓。	READY
16513_facelift_lowroof	16513	MPV	Doblò I	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-LOWROOF-01	MEDIUM	改款后低顶乘用车分支。	READY
16513_facelift_highroof	16513	MPV	Doblò I	223	5	EU-FIAT-DOBLO-I-223-MPV-FACELIFT-HIGHROOF-01	MEDIUM	改款后高顶乘用车分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-I-223-MPV-PREFL-01	4159	1714	1810	Automobile-Catalog 2001 Fiat Doblo 1.9 JTD SX specifications	https://www.automobile-catalog.com/car/2001/725795/fiat_doblo_1_9_jtd_sx.html
```

## 下一步优先处理

1. 先闭合 Movano A 与 Master II 的 1.9 DTI/dCi 80 Bus、Van Ktype，确认 L1H1 及改款前后外廓边界。
2. 再批量处理 2.5 DTI/dCi 120 的 Bus、Van、Chassis，按 L1/L2/L3、H1/H2/H3 和改款边界拆分。
3. 剩余 Ktype：16466、16467、16468、16470、16471、16488、16489、16490、16491、16492。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/725795/fiat_doblo_1_9_jtd_sx.html?utm_source=chatgpt.com "2001 Fiat Doblo 1.9 JTD SX Specs Review (74 kW ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 1.9 DTI/dCi 车型簇的 4 个 Ktype，新增 6 条 READY 映射。
* Opel Movano A 的 16466、16467 生产起点位于改款前，分别关联 L1H1 Bus 与 Van 外廓。
* Renault Master II 的 16491、16492 覆盖改款前后生产阶段，分别拆分为 `prefl`、`facelift` 分支。改款前标准车长为 4888 mm；改款后 L1H1 为 4899 × 1990 × 2253 mm，规格页另列含后视镜宽度 2359 mm，因此落盘宽度采用不含后视镜的 1990 mm。([Auto-Selection][1])
* 改款前 Bus 与 Van 的高度差异分别落入独立尺寸组；宽度口径通过 Movano 官方手册中车身宽度与含镜宽度的分列数据闭合。([ManualsLib][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* READY 映射：134
* PENDING Ktype：6
* 已确认并引用尺寸组：67
* 本轮首次创建尺寸组：5
* 剩余 Ktype：16468、16470、16471、16488、16489、16490
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16466	16466	MPV	Movano A			EU-OPEL-MOVANO-A-MPV-L1H1-PREFL-01	MEDIUM	改款前L1H1乘用外廓。	READY
16467	16467	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L1H1-PREFL-01	MEDIUM	改款前L1H1货运外廓。	READY
16491_prefl	16491	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-MPV-L1H1-PREFL-01	MEDIUM	输入区间跨越改款；改款前L1H1分支。	READY
16491_facelift	16491	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-L1H1-FACELIFT-01	MEDIUM	输入区间跨越改款；改款后L1H1分支。	READY
16492_prefl	16492	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L1H1-PREFL-01	MEDIUM	输入区间跨越改款；改款前L1H1分支。	READY
16492_facelift	16492	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-L1H1-FACELIFT-01	MEDIUM	输入区间跨越改款；改款后L1H1分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOVANO-A-MPV-L1H1-PREFL-01	4888	1990	2216	Gazoo Opel Movano A Combi dimensions; Opel Movano official owner's manual	https://gazoo.pl/samochody/opel/opel-movano/wymiary/; https://www.manualslib.de/manual/39416/Opel-Movano.html
EU-OPEL-MOVANO-A-VAN-L1H1-PREFL-01	4888	1990	2249	Auto-Selection Opel Movano L1H1 specifications; Opel Movano official owner's manual	https://www.auto-selection.com/fiche-technique/opel/movano-fg/1999/f2800-c1-2-8dti-4456.php; https://www.manualslib.de/manual/39416/Opel-Movano.html
EU-RENAULT-MASTER-II-X70-MPV-L1H1-PREFL-01	4888	1990	2216	Gazoo Opel Movano A equivalent X70 Combi dimensions; Opel Movano official owner's manual	https://gazoo.pl/samochody/opel/opel-movano/wymiary/; https://www.manualslib.de/manual/39416/Opel-Movano.html
EU-RENAULT-MASTER-II-X70-VAN-L1H1-PREFL-01	4888	1990	2249	Auto-Selection Renault Master II L1H1 specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l1h1-3t3-2-2-dci-90ch-generique-5277
EU-RENAULT-MASTER-II-X70-L1H1-FACELIFT-01	4899	1990	2253	Auto-Data Vauxhall Movano X70 1.9 CDTI L1H1 equivalent-body specifications	https://www.auto-data.net/en/vauxhall-movano-swb-facelift-2003-2800-1.9cdti-82hp-l1h1-25668
```

## 下一步优先处理

1. 闭合 16468、16470、16471 的 Movano A 2.5 DTI Bus、Van、Chassis 分支。
2. 同步关联 16488、16489、16490 的 Master II 2.5 dCi 120 共平台外廓。
3. 按 L1/L2/L3、H1/H2/H3 与 Chassis 长度一次建组并批量关联，完成后立即进行机械收尾。

推进信号：CONTINUE

[1]: https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l1h1-3t3-2-2-dci-90ch-generique-5277?utm_source=chatgpt.com "Fiche technique Renault Master Fg année 2001 L1H1 3t3 2.2 dCi 90ch Générique Diesel 90ch"
[2]: https://www.manualslib.de/manual/39416/Opel-Movano.html?utm_source=chatgpt.com "OPEL MOVANO BETRIEBSANLEITUNG Pdf-Herunterladen | ManualsLib"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Movano A 2.5 DTI Bus/Van 与 Master II 2.5 dCi 120 Bus/Van 共 4 个 Ktype，新增 24 条 READY 映射。
* Movano 2.5 DTI 仅落入改款前分支；资料明确列出 L1H1、L2H2 Bus，以及多轴距、多车顶 Van 外廓。输入结束年月为 `-`，未将其扩张解释为改款后车型。([Gazoo][1])
* Master II Bus 按改款前后 L1H1/L2H2 拆分；Van 按改款前后 L1H1、L1H2、L2H2、L2H3、L3H2、L3H3 拆分。改款后官方资料明确给出车身宽度 1990 mm，不含后视镜；含镜宽度另列为 2361 mm。([AutoScout24][2])
* 16471、16490 仍保留待处理：`Pritsche/Fahrgestell` 涵盖单排底盘、双排底盘及平台底盘，当前尚未完成所有早期阶段物理分支的同口径三维闭合。([AutoScout24][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：158
* PENDING Ktype：2
* 已确认并引用尺寸组：85
* 本轮新增 READY Ktype：4
* 本轮新增 READY 映射：24
* 本轮首次创建尺寸组：18
* 剩余 Ktype：16471、16490
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16468_l1h1_prefl	16468	MPV	Movano A			EU-OPEL-MOVANO-A-MPV-L1H1-PREFL-01	MEDIUM	改款前L1H1乘用分支。	READY
16468_l2h2_prefl	16468	MPV	Movano A			EU-OPEL-MOVANO-A-MPV-L2H2-PREFL-01	MEDIUM	改款前L2H2乘用分支。	READY
16470_l1h1_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L1H1-PREFL-01	MEDIUM	改款前L1H1货运分支。	READY
16470_l1h2_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L1H2-PREFL-01	MEDIUM	改款前L1H2货运分支。	READY
16470_l2h2_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L2H2-PREFL-01	MEDIUM	改款前L2H2货运分支。	READY
16470_l2h3_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L2H3-PREFL-01	MEDIUM	改款前L2H3货运分支。	READY
16470_l3h2_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L3H2-PREFL-01	MEDIUM	改款前L3H2货运分支。	READY
16470_l3h3_prefl	16470	Van	Movano A			EU-OPEL-MOVANO-A-VAN-L3H3-PREFL-01	MEDIUM	改款前L3H3货运分支。	READY
16488_l1h1_prefl	16488	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-MPV-L1H1-PREFL-01	MEDIUM	改款前L1H1乘用分支。	READY
16488_l2h2_prefl	16488	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-MPV-L2H2-PREFL-01	MEDIUM	改款前L2H2乘用分支。	READY
16488_l1h1_facelift	16488	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-L1H1-FACELIFT-01	MEDIUM	改款后L1H1乘用分支。	READY
16488_l2h2_facelift	16488	MPV	Master II	X70		EU-RENAULT-MASTER-II-X70-MPV-L2H2-FACELIFT-01	MEDIUM	改款后L2H2乘用分支。	READY
16489_l1h1_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L1H1-PREFL-01	MEDIUM	改款前L1H1货运分支。	READY
16489_l1h2_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L1H2-PREFL-01	MEDIUM	改款前L1H2货运分支。	READY
16489_l2h2_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L2H2-PREFL-01	MEDIUM	改款前L2H2货运分支。	READY
16489_l2h3_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L2H3-PREFL-01	MEDIUM	改款前L2H3货运分支。	READY
16489_l3h2_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L3H2-PREFL-01	MEDIUM	改款前L3H2货运分支。	READY
16489_l3h3_prefl	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L3H3-PREFL-01	MEDIUM	改款前L3H3货运分支。	READY
16489_l1h1_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-L1H1-FACELIFT-01	MEDIUM	改款后L1H1货运分支。	READY
16489_l1h2_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L1H2-FACELIFT-01	MEDIUM	改款后L1H2货运分支。	READY
16489_l2h2_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L2H2-FACELIFT-01	MEDIUM	改款后L2H2货运分支。	READY
16489_l2h3_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L2H3-FACELIFT-01	MEDIUM	改款后L2H3货运分支。	READY
16489_l3h2_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L3H2-FACELIFT-01	MEDIUM	改款后L3H2货运分支。	READY
16489_l3h3_facelift	16489	Van	Master II	X70		EU-RENAULT-MASTER-II-X70-VAN-L3H3-FACELIFT-01	MEDIUM	改款后L3H3货运分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOVANO-A-MPV-L2H2-PREFL-01	5388	1990	2479	Gazoo Opel Movano A dimensions	https://gazoo.pl/samochody/opel/opel-movano/wymiary/
EU-OPEL-MOVANO-A-VAN-L1H2-PREFL-01	4888	1990	2486	Auto-Selection Renault Master X70 L1H2 equivalent-body specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l1h2-3t3-2-2-dci-90ch-generique-5279
EU-OPEL-MOVANO-A-VAN-L2H2-PREFL-01	5388	1990	2486	Auto-Selection Renault Master X70 L2H2 equivalent-body specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l2h2-3t5-2-2-dci-90ch-5267
EU-OPEL-MOVANO-A-VAN-L2H3-PREFL-01	5388	1990	2720	Auto-Selection Renault Trucks Master X70 L2H3 equivalent-body specifications	https://www.auto-selection.com/fiche-technique/renault-trucks/master-fg/2000/t35-l2h3-2-2dci-309498
EU-OPEL-MOVANO-A-VAN-L3H2-PREFL-01	5888	1990	2483	Auto-Selection Renault Master X70 L3H2 equivalent-body specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l3h2-3t5-2-5-dci-115ch-generique-5292
EU-OPEL-MOVANO-A-VAN-L3H3-PREFL-01	5888	1990	2718	Auto-Selection Renault Master X70 L3H3 equivalent-body specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l3h3-3t5-2-5-dci-115ch-5273
EU-RENAULT-MASTER-II-X70-MPV-L2H2-PREFL-01	5388	1990	2479	Gazoo Opel Movano equivalent X70 dimensions	https://gazoo.pl/samochody/opel/opel-movano/wymiary/
EU-RENAULT-MASTER-II-X70-MPV-L2H2-FACELIFT-01	5399	1990	2479	Auto-Selection Renault Master Combi L2H2 2.5 dCi 120 specifications	https://www.auto-selection.com/fiche-technique/renault/master-combi/2003/l2h2-3t5-2-5-dci-120ch-generique-722042
EU-RENAULT-MASTER-II-X70-VAN-L1H2-PREFL-01	4888	1990	2486	Auto-Selection Renault Master L1H2 specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l1h2-3t3-2-2-dci-90ch-generique-5279
EU-RENAULT-MASTER-II-X70-VAN-L2H2-PREFL-01	5388	1990	2486	Auto-Selection Renault Master L2H2 specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l2h2-3t5-2-2-dci-90ch-5267
EU-RENAULT-MASTER-II-X70-VAN-L2H3-PREFL-01	5388	1990	2720	Auto-Selection Renault Trucks Master L2H3 specifications	https://www.auto-selection.com/fiche-technique/renault-trucks/master-fg/2000/t35-l2h3-2-2dci-309498
EU-RENAULT-MASTER-II-X70-VAN-L3H2-PREFL-01	5888	1990	2483	Auto-Selection Renault Master L3H2 2.5 dCi specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l3h2-3t5-2-5-dci-115ch-generique-5292
EU-RENAULT-MASTER-II-X70-VAN-L3H3-PREFL-01	5888	1990	2718	Auto-Selection Renault Master L3H3 2.5 dCi specifications	https://www.auto-selection.com/fiche-technique/renault/master-fg/2001/l3h3-3t5-2-5-dci-115ch-5273
EU-RENAULT-MASTER-II-X70-VAN-L1H2-FACELIFT-01	4899	1990	2496	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-RENAULT-MASTER-II-X70-VAN-L2H2-FACELIFT-01	5399	1990	2486	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-RENAULT-MASTER-II-X70-VAN-L2H3-FACELIFT-01	5399	1990	2717	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-RENAULT-MASTER-II-X70-VAN-L3H2-FACELIFT-01	5899	1990	2484	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-RENAULT-MASTER-II-X70-VAN-L3H3-FACELIFT-01	5899	1990	2716	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
```

## 下一步优先处理

1. 闭合 16471 的 Movano A 2.5 DTI 改款前单排底盘、双排底盘及平台底盘边界。
2. 闭合 16490 的 Master II 2.5 dCi 120 改款前后 L2/L3 单排、双排及平台底盘分支。
3. 两个 Ktype 闭合后立即执行一次机械收尾，并输出两张最终完整 TSV与指定下载链接。

推进信号：CONTINUE

[1]: https://gazoo.pl/samochody/opel/opel-movano/wymiary/ "Wymiary Opel Movano - długość, szerokość, wysokość, rozstaw osi - gazoo.pl"
[2]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/master/master-l1h1-2-5-dci-120-2-8t-autres-diesel-2741/?srsltid=AfmBOoph6TKiIKl29a-J-w_2DHXADZXvypFsWfNdr6_LWoZPOl8Porwj "Renault Master L1H1 2.5 dCi 120 2.8t | Autres | 2003-2006 - Spécifications techniques"
[3]: https://www.autoscout24.fr/voiture/caracteristiques-techniques/renault/master/ "Renault Master - Spécifications techniques | AutoScout24"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已确认 16471、16490 的 Ktype 范围均不是单一底盘：涉及单排底盘、双排底盘和平台底盘，并存在不同轴距、平台车顶及生产阶段分支。
* 官方 Movano 技术资料明确列出短/中/长轴单排底盘、中/长轴双排底盘，以及中/长轴低顶和高顶平台底盘；车身宽度统一为不含后视镜的 1990 mm。
* 16490 覆盖 2001—2010 年，跨越 2003 年外观改款及后续尺寸调整；现有资料中的早期、中期和后期底盘总长、高度不能合并为同一尺寸组。16471 的结束年月为未知，也不能直接扩张到全部后期分支。([B-Parts][1])
* 本轮未创建猜测性派生行或临时尺寸组，两个 Ktype 继续保持待闭合状态。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：158
* PENDING Ktype：2
* 已确认并引用尺寸组：85
* 本轮新增或修改映射：0
* 本轮首次创建或修正尺寸组：0
* 剩余 Ktype：16471、16490
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 将 16490 按 `2001–2003`、`2003–2006`、`2006–2010` 三个尺寸阶段核对，分别闭合单排、双排及平台底盘外廓。
2. 根据 16471 的明确车型代码和发动机适用期，排除不能由未知结束年月支撑的后期分支，仅保留可确认的 Movano A 底盘外廓。
3. 两个 Ktype 闭合后立即执行一次机械检查，并在下一条回复输出两张完整 TSV、指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.b-parts.com/auto-parts/versions/renault-master-ii-platform-chassis-ed-hd-ud-3902-vm?srsltid=AfmBOooAXEE_onnh4NfzEugXpS12T_NxlZ52-n1G19kCUDt7obgLx5Q0&utm_source=chatgpt.com "MASTER II Platform/Chassis (ED/HD/UD) [1997-2013] Parts"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已确认 16471、16490 在 2001–2003 阶段至少覆盖单排底盘、双排底盘、裸底盘及平台驾驶室的 L2/L3 分支；不是可合并为单一尺寸组的车型。([ParuVendu][1])
* 早期资料已取得部分完整外廓，例如裸底盘 L2 为 5301 × 1970 × 1639 mm、L3 为 5801 × 1970 × 1637 mm；但单排及双排页面仍存在宽度口径问题：页面仅列约 2359 mm，而同平台规格将不含后视镜宽度 1990 mm 与含镜宽度约 2361 mm 分列，不能直接把 2359 mm 作为落盘宽度。([ParuVendu][2])
* 当前尚缺部分早期单排、双排和平台分支的同一配置完整三维，未创建猜测性派生映射或拼接尺寸组。
* 机械重计后，当前已引用尺寸组为 88；上一轮显示的 85 是统计少计，不涉及映射或尺寸事实修改。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：158
* PENDING Ktype：2
* 已确认并引用尺寸组：88
* 剩余 Ktype：16471、16490
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅补齐 2001–2003 阶段单排 L2/L3、双排 L2/L3及平台 L2H1/L2H2/L3H1/L3H2 的同配置三维与不含后视镜宽度。
2. 将 16471 限定在其 84 kW DTI 可确认阶段，不因结束年月为 `-` 扩张至后期车型；16490则覆盖已确认的三个生产阶段。
3. 两个 Ktype 闭合后，立即进行一次表头、唯一性、引用和来源完整性检查，并输出最终两张完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.paruvendu.fr/fiches-techniques-utilitaire/renault-master-2003/?utm_source=chatgpt.com "Fiche technique Renault Master année 2003"
[2]: https://www.paruvendu.fr/fiches-techniques-utilitaire/renault-master/cnu-l3-3-5t-2-5-dci-8-cv-diesel/3078746/?utm_source=chatgpt.com "Fiche technique utilitaire Renault Master CNU L3 3.5t 2.5 ..."


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* 已为 16471、16490 闭合改款前后单排底盘、双排底盘及改款后平台驾驶室，共新增 16 条 READY 映射。
* Movano A 与 Master II 属同一 X70 物理车身，三维一致的 Opel/Renault Ktype 共用同一尺寸组，未按品牌重复建组。
* 改款前官方规格确认：单排 L2 为 5358 × 1990 × 2192 mm、单排 L3 为 5858 × 1990 × 2187 mm、双排 L3 为 5858 × 1990 × 2196 mm；1990 mm 为不含后视镜宽度。
* 改款后规格确认：单排 L2/L3、双排 L3，以及平台 L3H1/L3H2 均已闭合；车身宽度 1990 mm，含后视镜宽度另列约 2360 mm。
* 改款前平台驾驶室的高低顶分支仍缺少同一配置完整三维，因此分别保留一条语义明确的 PENDING 派生映射，未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 完全 READY Ktype：98
* PENDING Ktype：2
* READY 映射：174
* PENDING 映射：2
* 已确认并引用尺寸组：96
* 本轮新增 READY 映射：16
* 本轮新增 PENDING 映射：2
* 本轮首次创建尺寸组：8
* 剩余缺口仅为 16471、16490 的改款前平台驾驶室外廓。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16471_singlecab_l2_prefl	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-PREFL-01	MEDIUM	改款前单排L2底盘。	READY
16471_singlecab_l3_prefl	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-PREFL-01	MEDIUM	改款前单排L3底盘。	READY
16471_doublecab_l3_prefl	16471	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-PREFL-01	MEDIUM	改款前双排L3底盘。	READY
16471_platform_prefl	16471	Pickup	Movano A	X70	2		LOW	改款前平台驾驶室存在高低顶候选，完整外廓尚未闭合。	PENDING: 缺少改款前平台驾驶室同一配置完整三维
16471_singlecab_l2_facelift	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-FACELIFT-01	MEDIUM	改款后单排L2底盘。	READY
16471_singlecab_l3_facelift	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-FACELIFT-01	MEDIUM	改款后单排L3底盘。	READY
16471_doublecab_l3_facelift	16471	Pickup	Movano A	X70	4	EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-FACELIFT-01	MEDIUM	改款后双排L3底盘。	READY
16471_platform_l3h1_facelift	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-PLATFORM-L3H1-FACELIFT-01	MEDIUM	改款后平台驾驶室L3H1。	READY
16471_platform_l3h2_facelift	16471	Pickup	Movano A	X70	2	EU-OPEL-MOVANO-A-X70-PLATFORM-L3H2-FACELIFT-01	MEDIUM	改款后平台驾驶室L3H2。	READY
16490_singlecab_l2_prefl	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-PREFL-01	MEDIUM	改款前单排L2共平台底盘。	READY
16490_singlecab_l3_prefl	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-PREFL-01	MEDIUM	改款前单排L3共平台底盘。	READY
16490_doublecab_l3_prefl	16490	Pickup	Master II	X70	4	EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-PREFL-01	MEDIUM	改款前双排L3共平台底盘。	READY
16490_platform_prefl	16490	Pickup	Master II	X70	2		LOW	改款前平台驾驶室存在高低顶候选，完整外廓尚未闭合。	PENDING: 缺少改款前平台驾驶室同一配置完整三维
16490_singlecab_l2_facelift	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-FACELIFT-01	MEDIUM	改款后单排L2共平台底盘。	READY
16490_singlecab_l3_facelift	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-FACELIFT-01	MEDIUM	改款后单排L3共平台底盘。	READY
16490_doublecab_l3_facelift	16490	Pickup	Master II	X70	4	EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-FACELIFT-01	MEDIUM	改款后双排L3共平台底盘。	READY
16490_platform_l3h1_facelift	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-PLATFORM-L3H1-FACELIFT-01	MEDIUM	改款后平台驾驶室L3H1。	READY
16490_platform_l3h2_facelift	16490	Pickup	Master II	X70	2	EU-OPEL-MOVANO-A-X70-PLATFORM-L3H2-FACELIFT-01	MEDIUM	改款后平台驾驶室L3H2。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-PREFL-01	5358	1990	2192	Opel Movano official brochure March 2000	https://www.opel-niedersachsen.de/media/files/Movano-2000-03.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-PREFL-01	5858	1990	2187	Opel Movano official brochure March 2000	https://www.opel-niedersachsen.de/media/files/Movano-2000-03.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-PREFL-01	5858	1990	2196	Opel Movano official brochure March 2000	https://www.opel-niedersachsen.de/media/files/Movano-2000-03.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L2-FACELIFT-01	5369	1990	2198	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-SINGLECAB-L3-FACELIFT-01	5869	1990	2194	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-X70-CHASSIS-DOUBLECAB-L3-FACELIFT-01	5869	1990	2202	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-X70-PLATFORM-L3H1-FACELIFT-01	5813	1990	2189	Renault Master platform cab technical specifications	https://www.caradisiac.com/VUL-Renault-Master-la-fiche-technique-28776.htm
EU-OPEL-MOVANO-A-X70-PLATFORM-L3H2-FACELIFT-01	5813	1990	2438	Renault Master platform cab technical specifications	https://www.caradisiac.com/VUL-Renault-Master-la-fiche-technique-28776.htm
```

## 下一步优先处理

1. 仅查找改款前 X70 平台驾驶室的直接规格页或官方表格。
2. 确认其是否同时存在 H1/H2，以及各自的总长、1990 mm 不含后视镜宽度和总高。
3. 闭合 `16471_platform_prefl`、`16490_platform_prefl` 后，立即执行一次机械收尾并输出两张最终完整 TSV与指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_12601-12700_ktype_dimension_mapping_final.tsv
- all_12601-12700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口

