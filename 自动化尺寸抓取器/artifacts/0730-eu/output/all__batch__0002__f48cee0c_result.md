# 任务：all 第 101-200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0002__f48cee0c


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 101-200 行

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
all 第 101-200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	4624	1859	1634
EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	4626	1904	1686
EU-JEEP-CHEROKEE-XJ-SUV-5D-01	4200	1720	1621
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685
EU-OPEL-ZAFIRA-LIFE-K0-MPV-L-01	5306	1920	1890
EU-OPEL-ZAFIRA-LIFE-K0-MPV-M-01	4956	1920	1890
EU-OPEL-ZAFIRA-LIFE-K0-MPV-S-01	4606	1920	1905
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	4084	1730	1562
EU-TOYOTA-C-HR-I-SUV-01	4360	1795	1565
EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	4645	1760	1470

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Dodge	Journey	2.0 CRD	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	Jun 2008	Dec 2011	2024-03-01	143073
Dodge	Journey	2.4 VVT	Kasten/Großraumlimousine	Frontantrieb	Benzin	125	170	Jan 2009	Dec 2012	2024-03-01	143074
Dodge	Journey	2.7 Flexfuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	136	185	Jan 2009	Dec 2011	2024-03-01	143075
Dodge	Journey	3.6 Flexfuel Allrad	Kasten/Großraumlimousine	Allrad	Benzin/Ethanol	211	287	Jan 2011	-	2024-03-01	143076
Dodge	Nitro	4.0 4WD	Kasten/SUV	Allrad	Benzin	191	260	Sep 2006	Dec 2011	2024-03-01	143078
Dodge	Nitro	2.8 CRD	Kasten/SUV	Heckantrieb	Diesel	130	177	Jun 2007	Dec 2011	2024-03-01	143079
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Sep 2000	Mar 2002	2024-03-01	143080
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	May 2004	Jun 2010	2024-03-01	143081
Fiat	Multipla	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	Apr 2002	Jun 2010	2024-03-01	143082
Fiat	Multipla	Bipower	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	76	103	Oct 2001	Jun 2010	2024-03-01	143083
Fiat	Multipla	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	76	103	Sep 2000	Jun 2010	2024-03-01	143084
Ford	S-Max	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	118	160	Feb 2011	Dec 2014	2024-03-01	143085
Ford	S-Max	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	107	145	Mar 2010	Dec 2014	2024-03-01	143086
Ford	S-Max	2.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	149	203	Mar 2010	Dec 2014	2024-03-01	143087
Ford	S-Max	2.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	176	239	Jul 2010	Dec 2014	2024-03-01	143088
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Jan 2007	Dec 2014	2024-03-01	143089
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	Mar 2010	Dec 2014	2024-03-01	143090
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	120	163	Mar 2010	Dec 2014	2024-03-01	143091
Audi	A4 b7	1.8 T	Cabriolet	Frontantrieb	Benzin	120	163	Jan 2006	Mar 2009	2024-03-01	143095
Audi	A4 b7	S4 Quattro	Cabriolet	Allrad	Benzin	253	344	Nov 2005	Mar 2009	2024-03-01	143097
Jeep	Cherokee	3.2 4X4	Kasten/SUV	Allrad	Benzin	200	272	Aug 2015	-	2024-03-01	143099
Jeep	Cherokee	2.0 CRD	Kasten/SUV	Frontantrieb	Diesel	103	140	Apr 2014	Aug 2018	2024-03-01	143100
Jeep	Cherokee	2.2 CRD	Kasten/SUV	Allrad	Diesel	136	185	Aug 2015	Aug 2018	2024-03-01	143101
Jeep	Cherokee	2.2 CRD	Kasten/SUV	Allrad	Diesel	147	200	Aug 2015	Aug 2018	2024-03-01	143102
Jeep	Commander	5.7 Hemi V8 4X4	Kasten/SUV	Allrad	Benzin	240	326	Sep 2005	Dec 2010	2024-03-01	143107
Jeep	Commander	3.0 CRD 4X4	Kasten/SUV	Allrad	Diesel	160	218	Sep 2005	Dec 2010	2024-03-01	143108
Mazda	Rx-4	1.3	Coupe	Heckantrieb	Benzin	85	116	Sep 1973	Dec 1976	2024-03-01	143109
Jeep	Grand cherokee van	V6 VVT	Kasten/SUV	Allrad	Benzin	210	286	Jul 2013	-	2024-03-01	143110
Jeep	Grand cherokee van	5.7 Hemi 4X4	Kasten/SUV	Allrad	Benzin	259	352	Jul 2013	-	2024-03-01	143111
Jeep	Grand cherokee van	3.0 CRD	Kasten/SUV	Allrad	Diesel	140	190	Jan 2017	-	2024-03-01	143113
Jeep	Grand cherokee van	3.0 CRD	Kasten/SUV	Allrad	Diesel	184	250	Jul 2013	-	2024-03-01	143114
Jeep	Renegade van	1.4	Kasten/SUV	Frontantrieb	Benzin	103	140	Jul 2014	-	2024-03-01	143117
Jeep	Renegade van	1.4 4X4	Kasten/SUV	Allrad	Benzin	125	170	Jul 2014	-	2024-03-01	143118
Jeep	Renegade van	1.6 E-torq	Kasten/SUV	Frontantrieb	Benzin	81	110	Jul 2014	Sep 2018	2024-03-01	143119
KIA	Sportage van	2.0 4WD	Kasten/SUV	Allrad	Benzin	70	95	Jun 1995	Nov 1998	2024-03-01	143131
KIA	Sportage van	2.0 TDI 4WD	Kasten/SUV	Allrad	Diesel	61	83	Oct 1997	Aug 2003	2024-03-01	143132
KIA	Sportage ii van	2.0 Crdi	Kasten/SUV	Frontantrieb	Diesel	110	150	Sep 2008	May 2010	2024-03-01	143133
KIA	Sportage ii van	2.0 Crdi 4WD	Kasten/SUV	Allrad	Diesel	110	150	Sep 2008	May 2010	2024-03-01	143134
Nissan	Qashqai i van	1.6 Cvtc	Kasten/SUV	Frontantrieb	Benzin	86	117	Mar 2013	Apr 2014	2025-06-01	143135
Nissan	Qashqai i van	2	Kasten/SUV	Frontantrieb	Benzin	104	141	Mar 2013	Apr 2014	2025-06-01	143136
Nissan	Qashqai i van	2.0 Allrad	Kasten/SUV	Allrad	Benzin	104	141	Mar 2013	Apr 2014	2025-06-01	143137
Nissan	Qashqai i van	1.5 DCI	Kasten/SUV	Frontantrieb	Diesel	81	110	Mar 2013	Apr 2014	2025-06-01	143138
Nissan	Qashqai i van	1.6 DCI	Kasten/SUV	Frontantrieb	Diesel	96	131	Mar 2013	Apr 2014	2025-06-01	143139
Nissan	Qashqai i van	1.6 DCI Allrad	Kasten/SUV	Allrad	Diesel	96	131	Mar 2013	Apr 2014	2025-06-01	143140
Nissan	Qashqai i van	2.0 DCI Allrad	Kasten/SUV	Allrad	Diesel	110	150	Mar 2013	Apr 2014	2025-06-01	143141
Audi	Q5	45 Tfsi Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	195	265	Nov 2020	-	2024-03-01	143152
Audi	Q5	40 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	150	204	Nov 2020	-	2024-03-01	143155
Opel	Meriva b van	1.4 Ecotec	Kasten/Großraumlimousine	Frontantrieb	Benzin	74	101	Jan 2013	Mar 2017	2024-03-01	143156
Opel	Meriva b van	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jan 2013	Nov 2014	2024-03-01	143157
Opel	Meriva b van	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jan 2014	Jan 2017	2024-03-01	143158
Opel	Meriva b van	1.6 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Mar 2014	Mar 2017	2024-03-01	143159
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	101	Jan 2013	Jan 2017	2024-03-01	143160
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Jan 2013	Oct 2013	2024-03-01	143161
Opel	Meriva b van	1.7 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Jan 2013	Oct 2013	2024-03-01	143162
Audi	Q5	50 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	210	286	Feb 2021	-	2025-06-01	143163
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Jan 2013	Oct 2014	2025-12-01	143165
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Jan 2012	Oct 2014	2025-12-01	143166
Opel	Zafira	2.0 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	121	165	Jan 2013	Oct 2014	2025-12-01	143167
Renault	Scénic i van	1.9	Kasten/Großraumlimousine	Frontantrieb	Diesel	47	64	Sep 1999	Feb 2001	2024-03-01	143168
Renault	Scénic i van	1.9 DTI	Kasten/Großraumlimousine	Frontantrieb	Diesel	72	98	Sep 1999	Apr 2001	2024-03-01	143169
Renault	Scénic iii van	1.6 VVT	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jan 2013	Sep 2016	2024-05-01	143170
Renault	Scénic iii van	1.4 TCE	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jan 2013	Sep 2016	2024-05-01	143171
Renault	Scénic iii van	1.5 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jan 2013	Sep 2016	2024-05-01	143172
Renault	Scénic iii van	1.5 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Apr 2009	Sep 2016	2024-05-01	143173
Renault	Scénic iii van	1.6 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Jan 2013	Sep 2016	2024-05-01	143175
Renault	Scénic iii van	1.9 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Jan 2013	Sep 2016	2024-05-01	143176
Toyota	Prius	1.8 Hybrid	Kasten/Großraumlimousine	Frontantrieb	Benzin/Elektro	100	136	Nov 2014	-	2024-03-01	143177
Toyota	C-Hr	1.8 Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	90	122	Oct 2016	-	2024-03-01	143178
Renault	Megane scénic van	1.9 DT	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Jan 1997	Sep 1999	2024-05-01	143179
Renault	Megane scénic van	1.9 DTI	Kasten/Großraumlimousine	Frontantrieb	Diesel	72	98	Apr 1997	Sep 1999	2024-05-01	143180
Renault	Espace ii van	2.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	79	107	Jun 1992	Oct 1996	2024-03-01	143181
Renault	Espace ii van	2.1 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	65	88	Jun 1992	Oct 1996	2024-03-01	143182
Nissan	Murano ii van	3.5 Cvtc 4X4	Kasten/SUV	Allrad	Benzin	188	256	Mar 2013	Sep 2014	2024-03-01	143183
Nissan	Murano ii van	2.5 DCI 4X4	Kasten/SUV	Allrad	Diesel	140	190	Mar 2013	Sep 2014	2024-03-01	143184
Nissan	Pathfinder iii van	2.5 DCI 4X4	Kasten/SUV	Allrad	Diesel	140	190	Mar 2013	Aug 2014	2024-03-01	143186
Nissan	Pathfinder iii van	3.0 DCI 4X4	Kasten/SUV	Allrad	Diesel	170	231	Mar 2013	Aug 2014	2024-03-01	143187
Nissan	Serena	1.6	Kasten/Großraumlimousine	Heckantrieb	Benzin	71	97	Feb 1993	Jun 2001	2024-03-01	143190
Nissan	Serena	1.6	Kasten/Großraumlimousine	Heckantrieb	Benzin	75	102	Sep 1994	Jun 1999	2024-03-01	143191
Nissan	Serena	2	Kasten/Großraumlimousine	Heckantrieb	Diesel	49	67	Jul 1992	Sep 1994	2024-03-01	143192
Nissan	Serena	2.3	Kasten/Großraumlimousine	Heckantrieb	Diesel	55	75	Oct 1994	Sep 2001	2024-03-01	143193
Renault	Zoe	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	65	88	Apr 2019	-	2024-03-01	143197
Renault	Zoe	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	68	92	Apr 2019	-	2024-03-01	143198
Renault	Zoe	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	80	109	Apr 2019	-	2024-03-01	143199
Renault	Zoe	Electric	Kasten/Schrägheck	Frontantrieb	Elektro	100	136	Oct 2019	-	2024-03-01	143200
Mitsubishi	Space wagon van	1.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	66	90	Jun 1986	Dec 1988	2024-03-01	143202
Mitsubishi	Space wagon van	1.8 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 1983	Sep 1987	2024-03-01	143203
KIA	Sorento i van	2.5 Crdi 4WD	Kasten/SUV	Allrad	Diesel	103	140	Aug 2005	Oct 2006	2024-03-01	143204
Volvo	Xc70 ii van	2.0 D4	Kasten/Kombi	Frontantrieb	Diesel	120	163	Sep 2013	Dec 2016	2024-03-01	143205
Volvo	Xc70 ii van	2.4 D4 AWD	Kasten/Kombi	Allrad	Diesel	120	163	Sep 2013	Apr 2016	2024-03-01	143206
Volvo	Xc70 ii van	2.4 D5 AWD	Kasten/Kombi	Allrad	Diesel	158	215	Sep 2013	Dec 2016	2024-03-01	143207
Chrysler	Voyager iii van	2.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	111	151	Jan 1995	Mar 2001	2024-03-01	143208
Chrysler	Voyager iii van	3.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	116	158	Jan 1995	Mar 2001	2024-03-01	143209
Chrysler	Voyager iii van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	122	166	Oct 1995	Sep 1997	2024-03-01	143210
Chrysler	Voyager iii van	3.8 AWD	Kasten/Großraumlimousine	Allrad	Benzin	131	178	Oct 1997	Mar 2001	2024-03-01	143211
Chrysler	Voyager iii van	2.5 TD	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Jan 1995	Mar 2001	2024-03-01	143212
Pontiac	Trans sport van	2.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	101	137	Jun 1993	Aug 1995	2024-03-01	143213
Pontiac	Trans sport van	3.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	90	122	Aug 1989	Oct 1996	2024-03-01	143214
Pontiac	Trans sport van	3.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	104	141	Aug 1989	Oct 1996	2024-03-01	143215
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	112	152	Jul 1989	Mar 1997	2024-03-01	143216
Pontiac	Trans sport van	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	123	167	Jul 1989	Mar 1997	2024-03-01	143217


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理外廓聚类，已闭合 Multipla 改款前/后、S-Max 改款前/后、A4 B7 Cabriolet、Zoe 2019 改款后等尺寸组。Fiat 官方资料支持改款后 Multipla 的 4090×1870×1690 mm；Ford 官方资料明确 S-Max 宽度为不含后视镜 1884 mm；Zoe 改款后车身宽度为 1787 mm，而不是改款前的 1730 mm。([Le Parnass][1])
* 复用现有 Cherokee KL 标准车身、Q5 II FY、Zafira C P12、C-HR I、Zoe 改款前共5个缓存尺寸组，未重复输出尺寸事实。
* Dodge Journey 改款前资料存在不含镜宽度冲突；Nitro 同配置高度资料存在冲突，因此没有强行建组。([汽车目录][2])
* Cherokee 3.2及200 PS版本尚不能仅凭输入字段排除 Trailhawk 外廓，保留 PENDING；2.0前驱及185 PS版本先关联标准车身组。Ktype检索能确认这些编号对应 Cherokee Van KL，但没有提供足以闭合全部外观配置的级别字段。([meyermotoren.de][3])

## 当前批次进度

* 输入 Ktype：100个
* 已处理：36个 Ktype
* READY：32行映射，覆盖28个 Ktype
* PENDING：8行映射
* 尚未处理：64个 Ktype
* 已引用尺寸组：12个，其中本轮新建7个、复用既有组5个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143073	143073	MPV	Journey I (JC)	JC	5		LOW	改款前车身候选组的宽度事实尚未闭合。	PENDING: 同代不含镜宽度来源冲突
143074	143074	MPV	Journey I (JC)	JC	5		LOW	生产区间及改款边界需与宽度冲突一并解决。	PENDING: 同代不含镜宽度来源冲突
143075	143075	MPV	Journey I (JC)	JC	5		LOW	改款前车身候选组的宽度事实尚未闭合。	PENDING: 同代不含镜宽度来源冲突
143076	143076	MPV	Journey I (JC) facelift	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	MEDIUM	2010改款后的3.6 AWD车身分支。	READY
143078	143078	SUV	Nitro (KA)	KA	5		LOW	4.0版本的标准车高与R/T外观配置边界未闭合。	PENDING: 同配置高度来源冲突
143079	143079	SUV	Nitro (KA)	KA	5		LOW	2.8 CRD不同资料所示车高不一致。	PENDING: 同配置高度来源冲突
143080	143080	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	HIGH	2004改款前外廓。	READY
143081	143081	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	HIGH	2004改款后外廓。	READY
143082	143082	MPV	Multipla I (186)	186	5		LOW	120 PS版本的输入起始时间与改款资料不一致。	PENDING: 120 PS版本与2004改款边界未闭合
143083_prefl	143083	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143083_facelift	143083	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143084_prefl	143084	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143084_facelift	143084	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143085	143085	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143086	143086	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143087	143087	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143088	143088	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143089_prefl	143089	MPV	S-Max I (WA6)	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2010改款；本行为改款前外廓。	READY
143089_facelift	143089	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2010改款；本行为改款后外廓。	READY
143090	143090	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143091	143091	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143095	143095	Convertible	A4 B7 Cabriolet	8H	2	EU-AUDI-A4-B7-8H-CONVERTIBLE-01	HIGH		READY
143097	143097	Convertible	A4 B7 Cabriolet	8HE	2	EU-AUDI-A4-B7-8H-CONVERTIBLE-01	HIGH	S4 Cabriolet与同代A4 Cabriolet共用外廓尺寸组。	READY
143099	143099	SUV	Cherokee V (KL)	KL	5		LOW	3.2 4X4未提供可区分标准车身与Trailhawk的配置边界。	PENDING: 标准车身与Trailhawk分支未区分
143100	143100	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	HIGH	前驱标准车身分支。	READY
143101	143101	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	185 PS标准车身分支。	READY
143102	143102	SUV	Cherokee V (KL) pre-facelift	KL	5		LOW	200 PS 4X4未提供可区分标准车身与Trailhawk的配置边界。	PENDING: 标准车身与Trailhawk分支未区分
143152	143152	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH	标准Q5外廓。	READY
143155	143155	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH	标准Q5外廓。	READY
143163	143163	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH	标准Q5外廓。	READY
143165	143165	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143166	143166	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143167	143167	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143178	143178	SUV	C-HR I (AX10)	AX10	5	EU-TOYOTA-C-HR-I-SUV-01	HIGH		READY
143197	143197	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH	2019改款前外廓。	READY
143198	143198	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH	2019改款前外廓。	READY
143199_prefl	143199	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	MEDIUM	80 kW版本跨2019外观改款；本行为改款前外廓。	READY
143199_facelift	143199	Hatchback	Zoe I (X10) facelift	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	MEDIUM	80 kW版本跨2019外观改款；本行为改款后外廓。	READY
143200	143200	Hatchback	Zoe I (X10) facelift	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	HIGH	100 kW R135改款后外廓。	READY
```

Multipla、S-Max、A4 Cabriolet及Zoe的门数、代际分支和外廓边界由对应车型规格与官方资料共同支持。([汽车目录][4])

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	4887	1834	1692	Auto-Data	https://www.auto-data.net/en/dodge-journey-facelift-2010-3.6-v6-283hp-automatic-47972
EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	3994	1871	1695	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/723560/fiat_multipla_jtd_110_elx.html
EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	4090	1870	1690	Fiat Multipla official brochure	https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf
EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	4768	1884	1658	Ford S-MAX official brochure	https://xr793.org/wp-content/uploads/2020/09/2011-Ford-S-Max-UK.pdf
EU-FORD-S-MAX-I-WA6-MPV-PREFL-01	4768	1884	1658	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/977060/ford_s-max_2_0_edge.html
EU-AUDI-A4-B7-8H-CONVERTIBLE-01	4573	1777	1391	Auto-Data;Automobile-Catalog	https://www.auto-data.net/en/audi-a4-cabriolet-b7-8h-1.8-t-163hp-4289;https://www.automobile-catalog.com/car/2006/249020/audi_s4_cabriolet.html
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	4087	1787	1562	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2984435/renault_zoe_r135.html
```

上述新建组的宽度均按不含外后视镜口径落盘；Fiat和Ford资料中的尺寸表已进行页面级核对。([汽车数据网][5])

## 下一步优先处理

1. 先闭合 Commander、Grand Cherokee WK2、Renegade BU、Sportage各代、Qashqai J10等可批量复用的SUV尺寸组。
2. 随后集中处理 Scénic各代、Espace、Murano、Pathfinder、Serena等MPV/SUV组；Journey、Nitro及Cherokee配置冲突只针对具体阻塞点继续核对，不重复抓取已闭合组。

推进信号：CONTINUE

[1]: https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf "https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf"
[2]: https://www.automobile-catalog.com/car/2008/691640/dodge_journey_se_2_0l_crd.html?utm_source=chatgpt.com "2008 Dodge Journey SE 2.0L CRD Specs Review (103 kW / 140 PS / 138 hp) (since mid-year 2008 for Europe )"
[3]: https://www.meyermotoren.de/en/fahrzeuge/143102/jeep/cherokee_5_van_kl_/2_2_crd "https://www.meyermotoren.de/en/fahrzeuge/143102/jeep/cherokee_5_van_kl_/2_2_crd"
[4]: https://www.automobile-catalog.com/car/2001/723560/fiat_multipla_jtd_110_elx.html "https://www.automobile-catalog.com/car/2001/723560/fiat_multipla_jtd_110_elx.html"
[5]: https://www.auto-data.net/en/dodge-journey-facelift-2010-3.6-v6-283hp-automatic-47972 "https://www.auto-data.net/en/dodge-journey-facelift-2010-3.6-v6-283hp-automatic-47972"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新闭合 Commander XK、Grand Cherokee WK2 facelift、Sportage II facelift、Qashqai J10 facelift、Meriva B 改款前后、Scénic I/III 和 Prius III 共 **10 个尺寸组**。
* Meriva B 跨 2014 改款的 Ktype 已按 `4288 mm` 与 `4300 mm` 两种外廓拆分；Scénic III 跨代内改款的 Ktype 已按 Phase I 与 Phase II/III 两组拆分。
* 本轮未重复输出或重新核验上一轮已经闭合的尺寸组。
* Sportage I 暂未落盘：欧洲资料对改款前后长度、宽度及备胎计入口径存在冲突，留到阻塞点专项处理。Commander、Grand Cherokee、Qashqai、Meriva、Scénic 和 Prius 的尺寸边界已有直接规格页支持。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：66
* READY 覆盖：58 个 Ktype，65 行映射
* PENDING：8 个 Ktype，8 行映射
* 尚未处理：34 个 Ktype
* 已确认尺寸组：22 个
* 本轮首次创建尺寸组：10 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143107	143107	SUV	Commander I (XK)	XK	5	EU-JEEP-COMMANDER-I-XK-SUV-01	HIGH		READY
143108	143108	SUV	Commander I (XK)	XK	5	EU-JEEP-COMMANDER-I-XK-SUV-01	HIGH		READY
143110	143110	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143111	143111	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143113	143113	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143114	143114	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143133	143133	SUV	Sportage II facelift	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	HIGH		READY
143134	143134	SUV	Sportage II facelift	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	HIGH		READY
143135	143135	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143136	143136	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143137	143137	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143138	143138	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143139	143139	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143140	143140	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143141	143141	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143156_prefl	143156	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143156_facelift	143156	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143157_prefl	143157	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143157_facelift	143157	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143158	143158	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	HIGH		READY
143159	143159	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	HIGH		READY
143161	143161	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	HIGH		READY
143162	143162	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	HIGH		READY
143168	143168	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	HIGH		READY
143169	143169	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	HIGH		READY
143170	143170	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143171	143171	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143172	143172	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143173_prefl	143173	MPV	Scénic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	MEDIUM	Ktype生产区间覆盖Phase I；本行为早期外廓。	READY
143173_facelift	143173	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	MEDIUM	Ktype生产区间覆盖Phase II/III；本行为后期外廓。	READY
143175	143175	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143176	143176	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	MEDIUM		READY
143177	143177	Hatchback	Prius III (XW30)	ZVW30	5	EU-TOYOTA-PRIUS-III-XW30-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JEEP-COMMANDER-I-XK-SUV-01	4787	1899	1826	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/1327730/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4828	1943	1802	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/1894985/jeep_grand_cherokee_limited_awd_3_0_crd_v-6_250hp.html
EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	4350	1800	1730	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1358705/kia_sportage_2_0_crdi_vgt_lx_4wd_dpf.html
EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	4330	1780	1615	Auto-Data	https://www.auto-data.net/en/nissan-qashqai-i-j10-facelift-2010-generation-3812
EU-OPEL-MERIVA-B-MPV-PREFL-01	4288	1812	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2539400/opel_meriva_1_7_cdti_110.html
EU-OPEL-MERIVA-B-MPV-FACELIFT-01	4300	1812	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2539670/opel_meriva_1_4_100.html
EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	4169	1719	1675	Auto-Data	https://www.auto-data.net/en/renault-scenic-i-phase-ii-1.8-16v-116hp-10458
EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	4344	1845	1637	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/2981315/renault_scenic_1_5_dci_110_fap.html
EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	4366	1845	1640	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2982230/renault_scenic_1_5_energy_dci_110.html
EU-TOYOTA-PRIUS-III-XW30-HATCHBACK-01	4480	1745	1490	Auto-Data	https://www.auto-data.net/en/toyota-prius-iii-zvw30-generation-890
```

## 下一步优先处理

1. 优先消除现有8条 PENDING：Journey宽度冲突、Nitro高度冲突、Multipla 120 PS改款边界、Cherokee标准车身与Trailhawk边界。
2. 随后处理尚未落盘的 Renegade、RX-4、Sportage I、Murano、Pathfinder、Serena、Space Wagon、Sorento、XC70、Voyager和Trans Sport；已闭合尺寸组不再重新抓取。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2006/1327730/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html?utm_source=chatgpt.com "2006 Jeep Commander 3.0 CRD Limited Quadra-Drive II ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 原有 8 条显式 PENDING 已全部消除。Journey 按欧洲 2.0 CRD 资料采用不含后视镜宽度 `1834 mm`，跨 2011 改款的 Ktype 拆为改款前、后两行。([汽车目录][1])
* Nitro 的冲突源于北美与欧洲市场尺寸口径不同；本批输入为欧洲车型，4.0 与 2.8 CRD 统一采用欧洲外廓 `4584×1856×1773 mm`。([汽车目录][2])
* Cherokee 3.2 及 2.2 CRD 200 PS 均拆出标准 4×4 与 Trailhawk 外廓分支，并复用累计表已有两个尺寸组。Jeep 官方资料确认普通 4×4 与 Active Drive Lock/Trailhawk 的车宽、底盘及外部配置不同。
* 新闭合 Renegade FWD、Renegade 4×4、Mégane Scénic I Phase I 三类外廓；Renegade 官方规格明确 FWD 与 4×4 车高分别为 65.5、66.5 英寸。

## 当前批次进度

* 输入 Ktype：100
* 已建立映射：71 个 Ktype，共 83 行 READY 映射
* 待闭合：29 个 Ktype，均为尚未建立映射的车型
* 已确认尺寸组：27 个
* 本轮首次创建尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143073	143073	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	HIGH	改款前外廓。	READY
143074_prefl	143074	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2011改款；本行为改款前外廓。	READY
143074_facelift	143074	MPV	Journey I (JC) facelift	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2011改款；本行为改款后外廓。	READY
143075	143075	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	HIGH	改款前外廓。	READY
143078	143078	SUV	Nitro (KA)	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH	欧洲市场外廓。	READY
143079	143079	SUV	Nitro (KA)	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH	欧洲市场外廓。	READY
143082_prefl	143082	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143082_facelift	143082	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143099_standard	143099	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	标准4×4外廓分支。	READY
143099_trailhawk	143099	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk外廓分支。	READY
143102_standard	143102	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	标准4×4外廓分支。	READY
143102_trailhawk	143102	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk外廓分支。	READY
143117	143117	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	前驱外廓。	READY
143118	143118	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	HIGH	四驱车高分支。	READY
143119	143119	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	前驱外廓。	READY
143160_prefl	143160	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143160_facelift	143160	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143179	143179	MPV	Mégane Scénic I Phase I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	HIGH		READY
143180	143180	MPV	Mégane Scénic I Phase I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	4888	1834	1691	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691640/dodge_journey_se_2_0l_crd.html
EU-DODGE-NITRO-KA-SUV-STANDARD-01	4584	1856	1773	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691445/dodge_nitro_sxt_2_8_crd_automatic.html
EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	4232	1803	1664	Jeep Renegade official buyer's guide	https://www.jeep.com/assets/pdf/renegade_spec.pdf
EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	4232	1803	1689	Jeep Renegade official buyer's guide	https://www.jeep.com/assets/pdf/renegade_spec.pdf
EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	4134	1719	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2947400/renault_megane_scenic_1_6e_proactive.html
```

## 下一步优先处理

优先批量闭合 Espace II、Murano II、Pathfinder III、Serena、Space Wagon、Sorento I 和 XC70 II；随后处理 Voyager III、Trans Sport、RX-4 与 Sportage I 的跨改款外廓。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2008/691640/dodge_journey_se_2_0l_crd.html?utm_source=chatgpt.com "2008 Dodge Journey SE 2.0L CRD (man. 6)"
[2]: https://www.automobile-catalog.com/car/2011/691385/dodge_nitro_rt_4_0l_v-6_automatic.html?utm_source=chatgpt.com "2011 Dodge Nitro R/T 4.0L V-6 automatic (aut. 5)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已完成剩余车型组闭合及机械收尾。
* 最终检查时发现现有 `EU-AUDI-Q5-II-FY-SUV-01` 的三维与 2020 改款车型不一致，因此没有覆盖缓存，新增 `EU-AUDI-Q5-II-FY-SUV-02`，三维为 `4682×1893×1662 mm`。([汽车数据][1])
* Ktype `143178` 覆盖 C-HR 改款前后两种外廓，已拆分为 `4360×1795×1555 mm` 和 `4390×1795×1555 mm` 两组，未错误复用已有高度为 1565 mm 的缓存组。([丰田欧洲新闻中心][2])
* Ktype `143109` 覆盖 RX-4 Phase I 与 Phase II，已按长度 `4320 mm`、`4405 mm` 拆分，两组宽度均为不含后视镜的 `1665 mm`。([汽车目录][3])
* 已确认映射表和尺寸组表列数、主键唯一性、引用闭合、来源非空及文件名全部合格。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：114 行，覆盖全部 100 个 Ktype
* PENDING：0
* DIMENSION_GROUP：44 个
* 孤立尺寸组：0
* 未闭合引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143073	143073	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	HIGH	改款前外廓。	READY
143074_prefl	143074	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2011改款；本行为改款前外廓。	READY
143074_facelift	143074	MPV	Journey I (JC) facelift	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2011改款；本行为改款后外廓。	READY
143075	143075	MPV	Journey I (JC)	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	HIGH	改款前外廓。	READY
143076	143076	MPV	Journey I (JC) facelift	JC	5	EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	MEDIUM	2011改款后的3.6 AWD车身分支。	READY
143078	143078	SUV	Nitro (KA)	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH	欧洲市场外廓。	READY
143079	143079	SUV	Nitro (KA)	KA	5	EU-DODGE-NITRO-KA-SUV-STANDARD-01	HIGH	欧洲市场外廓。	READY
143080	143080	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	HIGH	2004改款前外廓。	READY
143081	143081	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	HIGH	2004改款后外廓。	READY
143082_prefl	143082	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143082_facelift	143082	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143083_prefl	143083	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143083_facelift	143083	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143084_prefl	143084	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款前外廓。	READY
143084_facelift	143084	MPV	Multipla I (186)	186	5	EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2004改款；本行为改款后外廓。	READY
143085	143085	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143086	143086	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143087	143087	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143088	143088	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143089_prefl	143089	MPV	S-Max I (WA6)	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2010改款；本行为改款前外廓。	READY
143089_facelift	143089	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2010改款；本行为改款后外廓。	READY
143090	143090	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143091	143091	MPV	S-Max I (WA6) facelift	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	HIGH	2010改款后外廓。	READY
143095	143095	Convertible	A4 B7 Cabriolet	8H	2	EU-AUDI-A4-B7-8H-CONVERTIBLE-01	HIGH		READY
143097	143097	Convertible	A4 B7 Cabriolet	8HE	2	EU-AUDI-A4-B7-8H-CONVERTIBLE-01	HIGH	S4 Cabriolet与同代A4 Cabriolet共用外廓尺寸组。	READY
143099_standard	143099	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	标准4×4外廓分支。	READY
143099_trailhawk	143099	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk外廓分支。	READY
143100	143100	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	HIGH	前驱标准车身分支。	READY
143101	143101	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	185 PS标准车身分支。	READY
143102_standard	143102	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	MEDIUM	标准4×4外廓分支。	READY
143102_trailhawk	143102	SUV	Cherokee V (KL) pre-facelift	KL	5	EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	MEDIUM	Trailhawk外廓分支。	READY
143107	143107	SUV	Commander I (XK)	XK	5	EU-JEEP-COMMANDER-I-XK-SUV-01	HIGH		READY
143108	143108	SUV	Commander I (XK)	XK	5	EU-JEEP-COMMANDER-I-XK-SUV-01	HIGH		READY
143109_prefl	143109	Coupe	RX-4 Phase I		2	EU-MAZDA-RX-4-PHASE-I-COUPE-01	MEDIUM	Ktype生产区间跨1975年外观变更；本行为Phase I两门Hardtop外廓。	READY
143109_facelift	143109	Coupe	RX-4 Phase II		2	EU-MAZDA-RX-4-PHASE-II-COUPE-01	MEDIUM	Ktype生产区间跨1975年外观变更；本行为Phase II两门Hardtop外廓。	READY
143110	143110	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143111	143111	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143113	143113	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143114	143114	SUV	Grand Cherokee IV (WK2) facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	HIGH		READY
143117	143117	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	前驱外廓。	READY
143118	143118	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	HIGH	四驱车高分支。	READY
143119	143119	SUV	Renegade I (BU)	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	前驱外廓。	READY
143131	143131	SUV	Sportage I (K00)	K00	5	EU-KIA-SPORTAGE-I-K00-SUV-EARLY-01	HIGH	早期五门标准车身。	READY
143132	143132	SUV	Sportage I (K00)	K00	5	EU-KIA-SPORTAGE-I-K00-SUV-TD-WAGON-01	HIGH	TD Wagon长车身外廓。	READY
143133	143133	SUV	Sportage II facelift	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	HIGH		READY
143134	143134	SUV	Sportage II facelift	KM	5	EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	HIGH		READY
143135	143135	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143136	143136	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143137	143137	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143138	143138	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143139	143139	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143140	143140	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143141	143141	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	MEDIUM	五门J10标准外廓。	READY
143152	143152	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-02	HIGH	2020改款后标准Q5外廓。	READY
143155	143155	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-02	HIGH	2020改款后标准Q5外廓。	READY
143156_prefl	143156	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143156_facelift	143156	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143157_prefl	143157	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143157_facelift	143157	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143158	143158	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	HIGH		READY
143159	143159	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	HIGH		READY
143160_prefl	143160	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款前外廓。	READY
143160_facelift	143160	MPV	Meriva B facelift		5	EU-OPEL-MERIVA-B-MPV-FACELIFT-01	MEDIUM	Ktype生产区间跨2014改款；本行为改款后外廓。	READY
143161	143161	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	HIGH		READY
143162	143162	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-PREFL-01	HIGH		READY
143163	143163	SUV	Q5 II (FY) facelift	FY	5	EU-AUDI-Q5-II-FY-SUV-02	HIGH	2020改款后标准Q5外廓。	READY
143165	143165	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143166	143166	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143167	143167	MPV	Zafira C (P12)	P12	5	EU-OPEL-ZAFIRA-C-P12-MPV-01	HIGH		READY
143168	143168	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	HIGH		READY
143169	143169	MPV	Scénic I Phase II		5	EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	HIGH		READY
143170	143170	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143171	143171	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143172	143172	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143173_prefl	143173	MPV	Scénic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	MEDIUM	Ktype生产区间覆盖Phase I；本行为早期外廓。	READY
143173_facelift	143173	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	MEDIUM	Ktype生产区间覆盖Phase II/III；本行为后期外廓。	READY
143175	143175	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	HIGH		READY
143176	143176	MPV	Scénic III Phase II/III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	MEDIUM		READY
143177	143177	Hatchback	Prius III (XW30)	ZVW30	5	EU-TOYOTA-PRIUS-III-XW30-HATCHBACK-01	HIGH		READY
143178_prefl	143178	SUV	C-HR I (AX10)	AX10	5	EU-TOYOTA-C-HR-I-SUV-02	MEDIUM	Ktype生产区间覆盖改款前1.8 Hybrid外廓。	READY
143178_facelift	143178	SUV	C-HR I (AX10) facelift	AX10	5	EU-TOYOTA-C-HR-I-SUV-03	MEDIUM	Ktype生产区间覆盖2020改款后1.8 Hybrid外廓。	READY
143179	143179	MPV	Mégane Scénic I Phase I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	HIGH		READY
143180	143180	MPV	Mégane Scénic I Phase I		5	EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	HIGH		READY
143181	143181	MPV	Espace II (J63)	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-01	HIGH		READY
143182	143182	MPV	Espace II (J63)	J63	5	EU-RENAULT-ESPACE-II-J63-MPV-01	HIGH		READY
143183	143183	SUV	Murano II (Z51) facelift	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-FACELIFT-01	HIGH		READY
143184	143184	SUV	Murano II (Z51) facelift	Z51	5	EU-NISSAN-MURANO-II-Z51-SUV-FACELIFT-01	HIGH		READY
143186	143186	SUV	Pathfinder III (R51) facelift	R51	5	EU-NISSAN-PATHFINDER-III-R51-SUV-FACELIFT-2.5DCI-01	HIGH	2.5 dCi认证车高分支。	READY
143187	143187	SUV	Pathfinder III (R51) facelift	R51	5	EU-NISSAN-PATHFINDER-III-R51-SUV-FACELIFT-3.0DCI-01	HIGH	3.0 dCi认证车高分支。	READY
143190	143190	MPV	Serena (C23M)	C23M	4	EU-NISSAN-SERENA-C23M-MPV-PETROL-01	HIGH	1.6汽油车身外廓。	READY
143191	143191	MPV	Serena (C23M)	C23M	4	EU-NISSAN-SERENA-C23M-MPV-PETROL-01	MEDIUM	同代1.6汽油车身外廓。	READY
143192	143192	MPV	Serena (C23M)	C23M	4	EU-NISSAN-SERENA-C23M-MPV-DIESEL-01	MEDIUM	同代柴油车身外廓。	READY
143193	143193	MPV	Serena (C23M)	C23M	4	EU-NISSAN-SERENA-C23M-MPV-DIESEL-01	HIGH	2.3柴油车身外廓。	READY
143197	143197	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH	2019改款前外廓。	READY
143198	143198	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	HIGH	2019改款前外廓。	READY
143199_prefl	143199	Hatchback	Zoe I (X10)	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	MEDIUM	80 kW版本跨2019外观改款；本行为改款前外廓。	READY
143199_facelift	143199	Hatchback	Zoe I (X10) facelift	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	MEDIUM	80 kW版本跨2019外观改款；本行为改款后外廓。	READY
143200	143200	Hatchback	Zoe I (X10) facelift	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	HIGH	100 kW R135改款后外廓。	READY
143202	143202	MPV	Space Wagon I (D00)	D05V	5	EU-MITSUBISHI-SPACE-WAGON-I-D00-MPV-FWD-01	HIGH		READY
143203	143203	MPV	Space Wagon I (D00)	D09W	5	EU-MITSUBISHI-SPACE-WAGON-I-D00-MPV-FWD-01	MEDIUM	D09W柴油版本与同代前驱车身共用外廓。	READY
143204	143204	SUV	Sorento I (BL)	BL	5	EU-KIA-SORENTO-I-BL-SUV-PREFL-01	HIGH		READY
143205	143205	Wagon	XC70 II facelift	P24	5	EU-VOLVO-XC70-II-P24-WAGON-FACELIFT-01	HIGH		READY
143206	143206	Wagon	XC70 II facelift	P24	5	EU-VOLVO-XC70-II-P24-WAGON-FACELIFT-01	HIGH		READY
143207	143207	Wagon	XC70 II facelift	P24	5	EU-VOLVO-XC70-II-P24-WAGON-FACELIFT-01	HIGH		READY
143208	143208	MPV	Voyager III (GS)	GS	5	EU-CHRYSLER-VOYAGER-III-GS-MPV-01	HIGH		READY
143209	143209	MPV	Voyager III (GS)	GS	5	EU-CHRYSLER-VOYAGER-III-GS-MPV-01	HIGH		READY
143210	143210	MPV	Voyager III (GS)	GS	5	EU-CHRYSLER-VOYAGER-III-GS-MPV-01	HIGH		READY
143211	143211	MPV	Voyager III (GS)	GS	5	EU-CHRYSLER-VOYAGER-III-GS-MPV-01	HIGH		READY
143212	143212	MPV	Voyager III (GS)	GS	5	EU-CHRYSLER-VOYAGER-III-GS-MPV-01	HIGH		READY
143213	143213	MPV	Trans Sport I (GMT199)	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	HIGH	欧洲规格车身外廓。	READY
143214	143214	MPV	Trans Sport I (GMT199)	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	MEDIUM	欧洲规格3.1车身外廓。	READY
143215	143215	MPV	Trans Sport I (GMT199)	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	MEDIUM	欧洲规格3.1车身外廓。	READY
143216	143216	MPV	Trans Sport I (GMT199)	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	HIGH	欧洲规格车身外廓。	READY
143217	143217	MPV	Trans Sport I (GMT199)	GMT199	4	EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	HIGH	欧洲规格车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_101-200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-JOURNEY-I-JC-MPV-PREFL-01	4888	1834	1691	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691640/dodge_journey_se_2_0l_crd.html
EU-DODGE-JOURNEY-I-JC-MPV-FACELIFT-01	4887	1834	1692	Auto-Data	https://www.auto-data.net/en/dodge-journey-facelift-2010-3.6-v6-283hp-automatic-47972
EU-DODGE-NITRO-KA-SUV-STANDARD-01	4584	1856	1773	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691445/dodge_nitro_sxt_2_8_crd_automatic.html
EU-FIAT-MULTIPLA-I-186-MPV-PREFL-01	3994	1871	1695	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/723560/fiat_multipla_jtd_110_elx.html
EU-FIAT-MULTIPLA-I-186-MPV-FACELIFT-01	4090	1870	1690	Fiat Multipla official brochure	https://blog.le-parnass.com/catalogue_pdf/fiat_multipla.pdf
EU-FORD-S-MAX-I-WA6-MPV-FACELIFT-01	4768	1884	1658	Ford S-MAX official brochure	https://xr793.org/wp-content/uploads/2020/09/2011-Ford-S-Max-UK.pdf
EU-FORD-S-MAX-I-WA6-MPV-PREFL-01	4768	1884	1658	Automobile-Catalog	https://www.automobile-catalog.com/car/2007/977060/ford_s-max_2_0_edge.html
EU-AUDI-A4-B7-8H-CONVERTIBLE-01	4573	1777	1391	Auto-Data;Automobile-Catalog	https://www.auto-data.net/en/audi-a4-cabriolet-b7-8h-1.8-t-163hp-4289;https://www.automobile-catalog.com/car/2006/249020/audi_s4_cabriolet.html
EU-JEEP-CHEROKEE-V-KL-SUV-STANDARD-01	4624	1859	1634	Jeep Cherokee official specifications	https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Jeep/Cherokee/CN_2015_JP_Cherokee_SP.pdf
EU-JEEP-CHEROKEE-V-KL-SUV-TRAILHAWK-01	4626	1904	1686	Jeep Cherokee official specifications	https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Jeep/Cherokee/CN_2015_JP_Cherokee_SP.pdf
EU-JEEP-COMMANDER-I-XK-SUV-01	4787	1899	1826	Automobile-Catalog	https://www.automobile-catalog.com/car/2006/1327730/jeep_commander_3_0_crd_limited_quadra-drive_ii_dpf.html
EU-MAZDA-RX-4-PHASE-I-COUPE-01	4320	1665	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/1616795/mazda_rx-4_hardtop_5-speed.html
EU-MAZDA-RX-4-PHASE-II-COUPE-01	4405	1665	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1978/1617515/mazda_rx-4_hardtop_5-speed.html
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-01	4828	1943	1802	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/1894985/jeep_grand_cherokee_limited_awd_3_0_crd_v-6_250hp.html
EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	4232	1803	1664	Jeep Renegade official buyer's guide	https://www.jeep.com/assets/pdf/renegade_spec.pdf
EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	4232	1803	1689	Jeep Renegade official buyer's guide	https://www.jeep.com/assets/pdf/renegade_spec.pdf
EU-KIA-SPORTAGE-I-K00-SUV-EARLY-01	4245	1730	1650	Auto-Data	https://www.auto-data.net/en/kia-sportage-k00-2.0-i-95hp-2725
EU-KIA-SPORTAGE-I-K00-SUV-TD-WAGON-01	4435	1764	1695	Auto-Data	https://www.auto-data.net/en/kia-sportage-i-2.0-td-wagon-83hp-2740
EU-KIA-SPORTAGE-II-KM-SUV-FACELIFT-01	4350	1800	1730	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1358705/kia_sportage_2_0_crdi_vgt_lx_4wd_dpf.html
EU-NISSAN-QASHQAI-I-J10-SUV-FACELIFT-01	4330	1780	1615	Auto-Data	https://www.auto-data.net/en/nissan-qashqai-i-j10-facelift-2010-generation-3812
EU-AUDI-Q5-II-FY-SUV-02	4682	1893	1662	Auto-Data	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-generation-7841
EU-OPEL-MERIVA-B-MPV-PREFL-01	4288	1812	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2539400/opel_meriva_1_7_cdti_110.html
EU-OPEL-MERIVA-B-MPV-FACELIFT-01	4300	1812	1615	Automobile-Catalog	https://www.automobile-catalog.com/car/2014/2539670/opel_meriva_1_4_100.html
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685	Auto-Data	https://www.auto-data.net/fr/opel-zafira-tourer-c-2.0-cdti-ecotec-165hp-19573
EU-RENAULT-SCENIC-I-MPV-PHASE-II-01	4169	1719	1675	Auto-Data	https://www.auto-data.net/en/renault-scenic-i-phase-ii-1.8-16v-116hp-10458
EU-RENAULT-SCENIC-III-MPV-PHASE-II-III-01	4366	1845	1640	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2982230/renault_scenic_1_5_energy_dci_110.html
EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	4344	1845	1637	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/2981315/renault_scenic_1_5_dci_110_fap.html
EU-TOYOTA-PRIUS-III-XW30-HATCHBACK-01	4480	1745	1490	Auto-Data	https://www.auto-data.net/en/toyota-prius-iii-zvw30-generation-890
EU-TOYOTA-C-HR-I-SUV-02	4360	1795	1555	Toyota Europe official newsroom	https://newsroom.toyota.eu/2016-toyota-c-hr/
EU-TOYOTA-C-HR-I-SUV-03	4390	1795	1555	Toyota C-HR official UK brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-archive/c-hr/c-hr-oct-22.pdf
EU-RENAULT-MEGANE-SCENIC-I-MPV-PHASE-I-01	4134	1719	1600	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/2947400/renault_megane_scenic_1_6e_proactive.html
EU-RENAULT-ESPACE-II-J63-MPV-01	4429	1795	1693	Auto-Data	https://www.auto-data.net/en/renault-espace-ii-j63-2.2i-107hp-10510
EU-NISSAN-MURANO-II-Z51-SUV-FACELIFT-01	4860	1885	1720	Auto-Data	https://www.auto-data.net/en/nissan-murano-ii-z51-facelift-2010-2.5-dci-190hp-4wd-automatic-19089
EU-NISSAN-PATHFINDER-III-R51-SUV-FACELIFT-2.5DCI-01	4813	1848	1858	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-iii-facelift-2010-2.5-dci-190hp-17041
EU-NISSAN-PATHFINDER-III-R51-SUV-FACELIFT-3.0DCI-01	4813	1848	1846	Auto-Data	https://www.auto-data.net/en/nissan-pathfinder-iii-facelift-2010-3.0-v6-231hp-17042
EU-NISSAN-SERENA-C23M-MPV-PETROL-01	4315	1710	1840	Auto-Data	https://www.auto-data.net/en/nissan-serena-c23m-1.6-16v-97hp-936
EU-NISSAN-SERENA-C23M-MPV-DIESEL-01	4315	1710	1835	Auto-Data	https://www.auto-data.net/en/nissan-serena-c23m-2.3-d-75hp-941
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-PREFL-01	4084	1730	1562	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2984360/renault_zoe_q90.html
EU-RENAULT-ZOE-I-X10-HATCHBACK-5D-FACELIFT-01	4087	1787	1562	Automobile-Catalog	https://www.automobile-catalog.com/car/2019/2984435/renault_zoe_r135.html
EU-MITSUBISHI-SPACE-WAGON-I-D00-MPV-FWD-01	4295	1640	1525	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/48920/mitsubishi_space_wagon_1_8_glx.html
EU-KIA-SORENTO-I-BL-SUV-PREFL-01	4567	1857	1730	Auto-Data	https://www.auto-data.net/en/kia-sorento-i-2.5-dcr-140hp-2664
EU-VOLVO-XC70-II-P24-WAGON-FACELIFT-01	4838	1870	1604	Auto-Data	https://www.auto-data.net/en/volvo-xc70-ii-facelift-2013-2.0-d4-163hp-19789
EU-CHRYSLER-VOYAGER-III-GS-MPV-01	4733	1950	1740	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/519845/chrysler_voyager_2_4.html
EU-PONTIAC-TRANS-SPORT-I-GMT199-MPV-EU-01	4946	1886	1670	Automobile-Catalog;Automobile-Catalog	https://www.automobile-catalog.com/car/1993/2855795/pontiac_trans_sport_2_3_16v.html;https://www.automobile-catalog.com/car/1992/2855810/pontiac_trans_sport_3_8_v6.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_101-200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-45-tfsi-265hp-mild-hybrid-quattro-ultra-s-tronic-41077 "https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-45-tfsi-265hp-mild-hybrid-quattro-ultra-s-tronic-41077"
[2]: https://newsroom.toyota.eu/2016-toyota-c-hr/ "https://newsroom.toyota.eu/2016-toyota-c-hr/"
[3]: https://www.automobile-catalog.com/car/1974/1616795/mazda_rx-4_hardtop_5-speed.html "https://www.automobile-catalog.com/car/1974/1616795/mazda_rx-4_hardtop_5-speed.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_101-200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_101-200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2040 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（966 行）

