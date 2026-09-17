# 任务：all 第 5801-5900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0059__a1d768eb


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5801-5900 行

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
all 第 5801-5900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5801-5900_ktype_dimension_mapping_final.tsv
- all_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-PORSCHE-914-TARGA-01	3985	1650	1230
EU-VOLVO-140-SEDAN-01	4640	1730	1440
EU-VOLVO-240-SEDAN-DIESEL-01	4890	1707	1430
EU-VOLVO-240-SEDAN-EARLY-01	4897	1707	1435
EU-VOLVO-240-SEDAN-LATE-01	4785	1707	1427
EU-VOLVO-240-SEDAN-MID-01	4890	1707	1430
EU-VOLVO-240-WAGON-DIESEL-01	4780	1710	1460
EU-VOLVO-240-WAGON-EARLY-01	4898	1710	1460
EU-VOLVO-240-WAGON-LATE-01	4785	1707	1427
EU-VOLVO-260-SEDAN-EARLY-01	4897	1707	1435
EU-VOLVO-260-SEDAN-FACELIFT-01	4890	1707	1430
EU-VOLVO-66-SEDAN-2D-01	3900	1540	1380
EU-VW-412-WAGON-L-01	4583	1675	1475
EU-VW-412-WAGON-STD-01	4555	1675	1475
EU-VW-DERBY-II-TYPE87-SEDAN-01	3975	1600	1355
EU-VW-DERBY-I-TYPE87-SEDAN-FACELIFT-01	3915	1560	1352
EU-VW-DERBY-I-TYPE87-SEDAN-PREFL-01	3836	1560	1352
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-JETTA-II-SEDAN-SPORT-01	4315	1665	1395
EU-VW-JETTA-II-SEDAN-STD-01	4315	1665	1415
EU-VW-JETTA-II-SYNCRO-SEDAN-01	4315	1680	1415
EU-VW-JETTA-I-SEDAN-01	4190	1610	1410
EU-VW-KAEFER-1302-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-1303-CONVERTIBLE-01	4080	1585	1500
EU-VW-KAEFER-1303-SEDAN-01	4080	1585	1500
EU-VW-KAEFER-TYPE113-1600-01	4060	1550	1500
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500
EU-VW-KAEFER-TYPE15-POST67-01	4030	1550	1500
EU-VW-KAEFER-TYPE15-STD-01	4070	1540	1500
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	4140	1634	1330
EU-VW-KARMANN-GHIA-TYPE14-COUPE-01	4140	1634	1330
EU-VW-PASSAT-B1-HATCHBACK-POST75-01	4290	1615	1360
EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	4190	1600	1360
EU-VW-PASSAT-B2-HATCHBACK-01	4335	1685	1385
EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	4530	1710	1385
EU-VW-PASSAT-B2-VARIANT-WAGON-01	4545	1695	1385
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-SCIROCCO-I-COUPE-3D-01	3885	1624	1309
EU-VW-SCIROCCO-I-COUPE-STD-01	3855	1625	1310
EU-VW-SCIROCCO-II-COUPE-3D-01	4050	1645	1280
EU-VW-TARO-PICKUP-2WD-01	4725	1650	1550
EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	4280	1750	1940
EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	4505	1720	1960
EU-VW-TRANSPORTER-T2-MPV-PREFL-01	4420	1765	1960
EU-VW-TRANSPORTER-T3-BUS-RWD-01	4600	1845	1950
EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	4600	1845	1990
EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-01	4600	1865	2020
EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	4600	1845	1950
EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	4570	1870	1925
EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	4570	1870	1930
EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	4636	2000	1930
EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	4570	1845	2365
EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	4570	1845	1965
EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	4570	1845	1990
EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	4570	1865	2020

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Karmann ghia	1500	Cabriolet	Heckantrieb	Benzin	29	39	Jul 1964	Jul 1974	2024-03-01	6190
VW	Kaefer	1300 1.3	Stufenheck	Heckantrieb	Benzin	27	37	Aug 1965	Jul 1970	2024-03-01	6192
VW	Kaefer	1302 1.3	Stufenheck	Heckantrieb	Benzin	29	39	Aug 1970	Jul 1975	2024-03-01	6193
VW	Kaefer	1302 1.6	Stufenheck	Heckantrieb	Benzin	35	48	Jul 1971	Jul 1974	2024-03-01	6194
Porsche	914	1.8	Targa	Heckantrieb	Benzin	63	86	Aug 1973	Feb 1976	2024-03-01	6195
VW	412	1.8 E,le	Kombi	Heckantrieb	Benzin	55	75	Jul 1973	Mar 1975	2024-03-01	6196
VW	412	1.8 E,le	Kombi	Heckantrieb	Benzin	63	86	Jul 1973	Mar 1975	2024-03-01	6197
VW	411,412	1.7	Stufenheck	Heckantrieb	Benzin	50	68	Jul 1968	Aug 1973	2024-03-01	6198
VW	411,412	1.7	Stufenheck	Heckantrieb	Benzin	59	80	Sep 1969	Aug 1973	2024-03-01	6199
VW	411,412	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Jul 1973	Mar 1975	2024-03-01	6200
VW	411,412	1.8	Stufenheck	Heckantrieb	Benzin	63	86	Jul 1973	Mar 1975	2024-03-01	6201
Volvo	P 121	1.6	Stufenheck	Heckantrieb	Benzin	44	60	May 1959	Sep 1966	2024-03-01	6202
Volvo	P 121	1.8	Stufenheck	Heckantrieb	Benzin	50	68	May 1959	Sep 1966	2024-03-01	6203
Volvo	P 121	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Feb 1967	May 1971	2024-03-01	6204
Volvo	P 121	2	Stufenheck	Heckantrieb	Benzin	60	82	Nov 1968	May 1971	2024-03-01	6206
Volvo	P 122 s amazon	1.6	Stufenheck	Heckantrieb	Benzin	61	83	May 1959	Sep 1966	2024-03-01	6207
Volvo	P 122 s amazon	1.8	Stufenheck	Heckantrieb	Benzin	59	80	May 1959	Jul 1967	2024-03-01	6208
Volvo	P 122 s amazon	1.8	Stufenheck	Heckantrieb	Benzin	63	86	Sep 1966	May 1971	2024-03-01	6209
Volvo	P 122 s amazon	1.8	Stufenheck	Heckantrieb	Benzin	76	103	Sep 1966	May 1971	2024-03-01	6210
Volvo	P 122 s amazon	1.8	Stufenheck	Heckantrieb	Benzin	66	90	Feb 1967	May 1971	2024-03-01	6211
Volvo	P 122 s amazon	2	Stufenheck	Heckantrieb	Benzin	74	101	Nov 1968	May 1971	2024-03-01	6212
Volvo	66	DL 1.1	Kombi	Heckantrieb	Benzin	33	45	Oct 1975	Nov 1979	2024-03-01	6213
Volvo	66	GL 1.3	Kombi	Heckantrieb	Benzin	42	57	Oct 1975	Nov 1979	2024-03-01	6214
Volvo	140	1.8 S	Stufenheck	Heckantrieb	Benzin	74	101	Jul 1967	Jan 1972	2024-03-01	6216
Volvo	140	2	Stufenheck	Heckantrieb	Benzin	91	124	Sep 1970	Apr 1975	2024-03-01	6217
Volvo	140	2.0 S	Stufenheck	Heckantrieb	Benzin	74	101	Nov 1968	Sep 1972	2024-03-01	6218
Volvo	140	2.0 S	Stufenheck	Heckantrieb	Benzin	85	116	Sep 1972	Aug 1975	2024-03-01	6219
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	71	97	Sep 1978	Aug 1983	2024-03-01	6220
Volvo	240	2.3	Stufenheck	Heckantrieb	Benzin	98	133	Aug 1984	Dec 1989	2024-03-01	6221
Volvo	240	2	Kombi	Heckantrieb	Benzin	60	82	Aug 1974	Jul 1975	2024-03-01	6222
Volvo	240	2	Kombi	Heckantrieb	Benzin	71	97	Aug 1980	Dec 1984	2024-03-01	6223
Volvo	240	2.1	Kombi	Heckantrieb	Benzin	71	97	Aug 1974	Jul 1975	2024-03-01	6224
Volvo	240	2	Kombi	Heckantrieb	Benzin	66	90	Aug 1976	Jan 1982	2024-03-01	6225
Volvo	260	2.7	Stufenheck	Heckantrieb	Benzin	92	125	Aug 1976	Jul 1982	2024-03-01	6227
Volvo	260	2.8	Stufenheck	Heckantrieb	Benzin	95	129	Aug 1980	Jul 1982	2024-03-01	6228
VW	15,001,600	1.6 L	Stufenheck	Heckantrieb	Benzin	37	50	Jul 1964	Jul 1973	2024-03-01	6229
VW	15,001,600	1.5 L	Schrägheck	Heckantrieb	Benzin	33	45	Jul 1968	Jul 1973	2024-03-01	6230
VW	15,001,600	1.5 S	Kombi	Heckantrieb	Benzin	40	54	Aug 1963	Jul 1965	2024-03-01	6232
Volvo	260	2.8	Stufenheck	Heckantrieb	Benzin	114	155	Aug 1980	Jul 1982	2024-03-01	6233
VW	Polo	0.9	Schrägheck	Frontantrieb	Benzin	29	39	Oct 1981	Dec 1981	2024-05-01	6234
VW	Derby	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1982	Dec 1984	2024-03-01	6235
VW	Jetta i	1.8	Stufenheck	Frontantrieb	Benzin	82	112	Aug 1982	Feb 1984	2024-03-01	6236
Volvo	140	2.0 S	Kombi	Heckantrieb	Benzin	74	101	Aug 1972	Jul 1974	2024-03-01	6237
VW	Golf iii	Citystromer	Schrägheck	Frontantrieb	Elektro	20	27	Nov 1994	Aug 1997	2024-03-01	6238
Volvo	140	2.0 S	Kombi	Heckantrieb	Benzin	60	82	Aug 1968	Jul 1974	2024-03-01	6239
Volvo	140	2.0 S	Kombi	Heckantrieb	Benzin	85	116	Sep 1973	Feb 1975	2024-03-01	6240
Volvo	140	2.0 S	Kombi	Heckantrieb	Benzin	73	100	Aug 1972	Jul 1973	2024-03-01	6241
Volvo	140	2.0 S	Kombi	Heckantrieb	Benzin	91	124	Aug 1972	Jul 1973	2024-03-01	6242
VW	Passat b1	1.5	Schrägheck	Frontantrieb	Benzin	63	86	May 1973	Dec 1975	2024-03-01	6243
VW	Passat b1	1.3	Schrägheck	Frontantrieb	Benzin	44	60	May 1973	Jan 1978	2024-03-01	6244
VW	Passat b1 variant	1.5	Kombi	Frontantrieb	Benzin	63	86	Oct 1973	Dec 1975	2024-03-01	6245
VW	Passat b1 variant	1.3	Kombi	Frontantrieb	Benzin	44	60	Oct 1973	Jan 1978	2024-03-01	6246
Volvo	164	2.9	Stufenheck	Heckantrieb	Benzin	118	160	Aug 1972	Jul 1974	2024-03-01	6247
Volvo	164	2.9 E	Stufenheck	Heckantrieb	Benzin	96	131	Aug 1968	Jul 1973	2024-03-01	6248
VW	Passat b2	1.6 TD	Schrägheck	Frontantrieb	Diesel	59	80	Aug 1988	Jul 1989	2024-03-01	6249
VW	Passat b2	1.8	Stufenheck	Frontantrieb	Benzin	64	87	May 1986	Mar 1988	2024-03-01	6250
VW	Passat b2	1.6	Stufenheck	Frontantrieb	Benzin	51	70	Aug 1986	Mar 1988	2024-03-01	6251
Volvo	P 1800	1.8 S	Coupe	Heckantrieb	Benzin	71	97	Apr 1962	May 1970	2024-03-01	6252
Volvo	C30	D2	Schrägheck	Frontantrieb	Diesel	84	115	Oct 2010	Dec 2012	2024-03-01	6253
Volvo	P 1800	1.8	Coupe	Heckantrieb	Benzin	76	103	Apr 1962	May 1970	2024-03-01	6254
Volvo	P 1800	1.8	Coupe	Heckantrieb	Benzin	66	90	Apr 1962	May 1970	2024-03-01	6255
Volvo	P 1800	2.0 ES	Coupe	Heckantrieb	Benzin	91	124	Aug 1969	Nov 1973	2024-03-01	6256
Volvo	P 2200	1.8	Kombi	Heckantrieb	Benzin	50	68	Sep 1964	Aug 1967	2024-03-01	6257
Volvo	P 2200	1.8	Kombi	Heckantrieb	Benzin	59	80	Sep 1964	Aug 1967	2024-03-01	6258
Volvo	P 2200	1.8	Kombi	Heckantrieb	Benzin	63	86	Sep 1964	Aug 1967	2024-03-01	6259
VW	Passat b2 variant	1.8	Kombi	Frontantrieb	Benzin	82	112	Dec 1983	Mar 1988	2024-03-01	6260
VW	Passat b2 variant	2.0 Syncro	Kombi	Allrad	Benzin	85	116	May 1984	Mar 1988	2024-03-01	6261
VW	Passat b3/b4	1.8 16V	Stufenheck	Frontantrieb	Benzin	100	136	Apr 1988	Dec 1989	2024-03-01	6262
VW	Passat b3/b4 variant	1.8 16V	Kombi	Frontantrieb	Benzin	100	136	Apr 1988	Dec 1989	2024-03-01	6263
VW	Scirocco	1.5	Coupe	Frontantrieb	Benzin	63	86	Feb 1974	Dec 1977	2024-03-01	6264
VW	Scirocco	1.5	Coupe	Frontantrieb	Benzin	55	75	Feb 1974	Aug 1975	2024-03-01	6265
VW	Taro	2.4 D 4X4	Pick-up	Allrad	Diesel	58	79	Jul 1994	Mar 1997	2024-03-01	6266
VW	Transporter t3	2	Kasten	Heckantrieb	Benzin	51	69	May 1979	Apr 1986	2024-03-01	6267
Volvo	C30	D3	Schrägheck	Frontantrieb	Diesel	110	150	Oct 2010	Dec 2012	2024-03-01	6268
Volvo	C30	D4	Schrägheck	Frontantrieb	Diesel	130	177	Oct 2010	Dec 2012	2024-03-01	6269
Volvo	C70 ii	D3	Cabriolet	Frontantrieb	Diesel	110	150	Oct 2010	Jun 2013	2024-03-01	6270
Volvo	C70 ii	D4	Cabriolet	Frontantrieb	Diesel	130	177	Oct 2010	Jun 2013	2024-03-01	6271
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	60	82	Aug 1974	Jul 1976	2024-03-01	6272
Volvo	240	2	Stufenheck	Heckantrieb	Benzin	76	103	Aug 1984	Jul 1985	2024-03-01	6273
Volvo	S80 ii	T4	Stufenheck	Frontantrieb	Benzin	132	180	Oct 2010	Apr 2014	2024-03-01	6274
Volvo	240	2.7 Glt6	Stufenheck	Heckantrieb	Benzin	104	141	Aug 1979	Jul 1980	2024-03-01	6275
Volvo	140	2	Stufenheck	Heckantrieb	Benzin	70	95	Aug 1971	Jul 1972	2024-03-01	6276
Volvo	140	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Aug 1966	Jul 1968	2024-03-01	6277
Volvo	S80 ii	T5	Stufenheck	Frontantrieb	Benzin	177	241	Oct 2010	Dec 2016	2024-03-01	6278
Volvo	S80 ii	T6 AWD	Stufenheck	Allrad	Benzin	224	305	Oct 2010	Dec 2015	2024-05-01	6279
Volvo	260	2.7	Coupe	Heckantrieb	Benzin	103	140	Aug 1977	Jul 1978	2024-03-01	6283
Volvo	260	2.7	Kombi	Heckantrieb	Benzin	109	148	Oct 1978	Jul 1982	2024-03-01	6284
Volvo	260	2.7	Kombi	Heckantrieb	Benzin	103	140	Jul 1975	Jul 1982	2024-03-01	6285
Volvo	260	2.7	Kombi	Heckantrieb	Benzin	92	125	Aug 1975	Jul 1977	2024-03-01	6286
Volvo	260	2.8	Kombi	Heckantrieb	Benzin	114	155	Aug 1980	Jul 1982	2024-03-01	6287
VW	Transporter t1	1.1	Bus	Heckantrieb	Benzin	18	24	Jan 1950	Dec 1962	2024-03-01	6288
VW	Transporter t1	1.2	Bus	Heckantrieb	Benzin	25	34	Nov 1962	Aug 1966	2024-03-01	6289
VW	Transporter t1	1.5	Bus	Heckantrieb	Benzin	31	42	Nov 1962	Aug 1966	2024-03-01	6290
VW	Transporter t1	1.5	Bus	Heckantrieb	Benzin	32	44	Jul 1966	Jul 1967	2024-03-01	6291
VW	Transporter t1	1.6	Bus	Heckantrieb	Benzin	35	48	Jun 1966	Jul 1967	2024-03-01	6292
VW	Transporter t1	1.2	Kasten	Heckantrieb	Benzin	25	34	Jan 1950	Mar 1962	2024-03-01	6293
VW	Transporter t1	1.2	Kasten	Heckantrieb	Benzin	25	34	Feb 1962	Jul 1967	2024-03-01	6294
VW	Transporter t2	1.7	Bus	Heckantrieb	Benzin	49	66	Aug 1971	Oct 1973	2024-03-01	6295
VW	Transporter t2	1.6	Kasten	Heckantrieb	Benzin	37	50	Aug 1970	Jul 1979	2024-03-01	6296
VW	Transporter t2	1.7	Kasten	Heckantrieb	Benzin	49	67	Aug 1971	Dec 1973	2024-03-01	6297


--- Round 1 / 首次发送 ---
## 更新点

* 完成 Volkswagen Type 3、Passat B1 Variant、Passat B2 Variant、Passat B3 等车身尺寸组闭合；其中 B2 Variant 官方三维与累计缓存不同，因此新建 `-02` 组，未覆盖旧组。([Volkswagen Newsroom][1])
* 完成 Volvo Amazon P120/P130/P220、Volvo 66 Wagon、140 系列 Sedan、164、C30、C70 II 和 S80 II 两次改款外廓。([kfz-tech.de][2])
* 完成 Transporter T1 三个年代外廓及 T2 改款前后 Van 外廓；继续复用已存在的 T1 Kasten、T2 Bus 和 T3 Van 尺寸组。([fahrzeugseiten.de][3])
* Volvo 145 的宽度资料存在 `1710/1735 mm` 冲突，未强行创建尺寸组。([CarsGuide][4])

## 当前批次进度

* 输入 Ktype：100
* 已完全 READY 的 Ktype：67
* READY 映射行：95
* PENDING Ktype／映射行：33
* 当前已引用尺寸组：46
* 本轮首次创建尺寸组：27
* 复用已有尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6190	6190	Convertible	Karmann Ghia Type 14	Type14	2	EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	HIGH	Type 14 two-door convertible.	READY
6192_pre67	6192	Sedan	Volkswagen Beetle Type 1	Type11	2	EU-VW-KAEFER-TYPE11-STD-01	MEDIUM	Ktype production span crosses the 1967 exterior-length boundary; pre-1967 branch.	READY
6192_post67	6192	Sedan	Volkswagen Beetle Type 1	Type11	2	EU-VW-KAEFER-TYPE11-POST67-01	MEDIUM	Ktype production span crosses the 1967 exterior-length boundary; post-1967 branch.	READY
6193	6193	Sedan	Volkswagen Beetle 1302	Type11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH	1302 sedan body.	READY
6194	6194	Sedan	Volkswagen Beetle 1302	Type11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH	1302 sedan body.	READY
6195	6195	Targa	Porsche 914	914	2	EU-PORSCHE-914-TARGA-01	HIGH	914 Targa body.	READY
6196_std	6196	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-STD-01	MEDIUM	Input does not isolate standard versus L exterior; standard body branch.	READY
6196_l	6196	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-L-01	MEDIUM	Input does not isolate standard versus L exterior; L body branch.	READY
6197_std	6197	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-STD-01	MEDIUM	Input does not isolate standard versus L exterior; standard body branch.	READY
6197_l	6197	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-L-01	MEDIUM	Input does not isolate standard versus L exterior; L body branch.	READY
6198	6198	Sedan	Volkswagen 411/412				LOW	Input combines 411/412 and does not isolate 2-door/4-door or standard/L exterior.	PENDING: generation, door count and trim-length branch unresolved
6199	6199	Sedan	Volkswagen 411/412				LOW	Input combines 411/412 and does not isolate 2-door/4-door or standard/L exterior.	PENDING: generation, door count and trim-length branch unresolved
6200	6200	Sedan	Volkswagen 411/412				LOW	Input combines 411/412 and does not isolate 2-door/4-door or standard/L exterior.	PENDING: generation, door count and trim-length branch unresolved
6201	6201	Sedan	Volkswagen 411/412				LOW	Input combines 411/412 and does not isolate 2-door/4-door or standard/L exterior.	PENDING: generation, door count and trim-length branch unresolved
6202_2dr	6202	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P121 designation overlaps the two-door P130 during this Ktype period.	READY
6202_4dr	6202	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P121 designation overlaps the four-door P120 during this Ktype period.	READY
6203_2dr	6203	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P121 designation overlaps the two-door P130 during this Ktype period.	READY
6203_4dr	6203	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P121 designation overlaps the four-door P120 during this Ktype period.	READY
6204	6204	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P121 two-door Amazon body.	READY
6206	6206	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P121 two-door Amazon body.	READY
6207_2dr	6207	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P122S designation overlaps the two-door P130 during this Ktype period.	READY
6207_4dr	6207	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P122S designation overlaps the four-door P120 during this Ktype period.	READY
6208_2dr	6208	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P122S designation overlaps the two-door P130 during this Ktype period.	READY
6208_4dr	6208	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P122S designation overlaps the four-door P120 during this Ktype period.	READY
6209	6209	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P122S two-door Amazon body.	READY
6210	6210	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P122S two-door Amazon body.	READY
6211	6211	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P122S two-door Amazon body.	READY
6212	6212	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P122S two-door Amazon body.	READY
6213	6213	Wagon	Volvo 66	66	3	EU-VOLVO-66-WAGON-3D-01	HIGH	Three-door estate body.	READY
6214	6214	Wagon	Volvo 66	66	3	EU-VOLVO-66-WAGON-3D-01	HIGH	Three-door estate body.	READY
6216_2dr	6216	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6216_4dr	6216	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6217_2dr	6217	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6217_4dr	6217	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6218_2dr	6218	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6218_4dr	6218	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6219_2dr	6219	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6219_4dr	6219	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6220	6220	Sedan	Volvo 240 Series				LOW	Ktype does not isolate 242/244 or the applicable early/mid/late exterior-length group.	PENDING: door count and year-specific 240 exterior branch unresolved
6221	6221	Sedan	Volvo 240 Series				LOW	Ktype does not isolate 242/244 or the applicable early/mid/late exterior-length group.	PENDING: door count and year-specific 240 exterior branch unresolved
6222	6222	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	Early 245 wagon body.	READY
6223	6223	Wagon	Volvo 240 Series	245	5		LOW	Applicable mid/late wagon exterior group is not yet closed against production dates.	PENDING: year-specific 245 exterior branch unresolved
6224	6224	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	Early 245 wagon body.	READY
6225	6225	Wagon	Volvo 240 Series	245	5		LOW	Applicable mid/late wagon exterior group is not yet closed against production dates.	PENDING: year-specific 245 exterior branch unresolved
6227	6227	Sedan	Volvo 260 Series	264	4		LOW	Existing cached 260 dimensions conflict with later secondary specifications; no overwrite made.	PENDING: 260 sedan dimension-source conflict unresolved
6228	6228	Sedan	Volvo 260 Series	264	4		LOW	Existing cached 260 dimensions conflict with later secondary specifications; no overwrite made.	PENDING: 260 sedan dimension-source conflict unresolved
6229_pre69	6229	Sedan	Volkswagen Type 3	Type31	2	EU-VW-TYPE3-TYPE31-SEDAN-PRE69-01	HIGH	Type 3 notchback before the 1969 exterior revision.	READY
6229_post69	6229	Sedan	Volkswagen Type 3	Type31	2	EU-VW-TYPE3-TYPE31-SEDAN-POST69-01	HIGH	Type 3 notchback after the 1969 exterior revision.	READY
6230	6230	Hatchback	Volkswagen Type 3	Type31	3	EU-VW-TYPE3-TYPE31-HATCHBACK-TL-01	HIGH	Type 3 TL fastback/hatchback body.	READY
6232	6232	Wagon	Volkswagen Type 3	Type31	3	EU-VW-TYPE3-TYPE31-WAGON-PRE69-01	HIGH	Early Type 3 Variant body.	READY
6233	6233	Sedan	Volvo 260 Series	264	4		LOW	Existing cached 260 dimensions conflict with later secondary specifications; no overwrite made.	PENDING: 260 sedan dimension-source conflict unresolved
6234	6234	Hatchback	Volkswagen Polo II	Type86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	Early Polo II three-door hatchback.	READY
6235	6235	Sedan	Volkswagen Derby II	Type87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH	Derby II two-door sedan.	READY
6236	6236	Sedan	Volkswagen Jetta I	Type16			LOW	Jetta I was sold as both two-door and four-door; the Ktype does not isolate the body.	PENDING: 2-door versus 4-door body unresolved
6237	6237	Wagon	Volvo 140 Series	145	5		LOW	Body style and length are confirmed, but credible sources conflict on body width (1710/1735 mm).	PENDING: Volvo 145 width-source conflict unresolved
6238	6238	Hatchback	Volkswagen Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	CityStromer production body matched to the five-door Golf III shell.	READY
6239	6239	Wagon	Volvo 140 Series	145	5		LOW	Body style and length are confirmed, but credible sources conflict on body width (1710/1735 mm).	PENDING: Volvo 145 width-source conflict unresolved
6240	6240	Wagon	Volvo 140 Series	145	5		LOW	Body style and length are confirmed, but credible sources conflict on body width (1710/1735 mm).	PENDING: Volvo 145 width-source conflict unresolved
6241	6241	Wagon	Volvo 140 Series	145	5		LOW	Body style and length are confirmed, but credible sources conflict on body width (1710/1735 mm).	PENDING: Volvo 145 width-source conflict unresolved
6242	6242	Wagon	Volvo 140 Series	145	5		LOW	Body style and length are confirmed, but credible sources conflict on body width (1710/1735 mm).	PENDING: Volvo 145 width-source conflict unresolved
6243	6243	Hatchback	Volkswagen Passat B1	Type32			LOW	Ktype spans the pre-/post-1975 length change and does not isolate 3-door/5-door body.	PENDING: door count and facelift-length branch unresolved
6244	6244	Hatchback	Volkswagen Passat B1	Type32			LOW	Ktype spans the pre-/post-1975 length change and does not isolate 3-door/5-door body.	PENDING: door count and facelift-length branch unresolved
6245_pre75	6245	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	HIGH	Variant body before the 1975 exterior-length revision.	READY
6245_post75	6245	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	HIGH	Variant body after the 1975 exterior-length revision.	READY
6246_pre75	6246	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	HIGH	Variant body before the 1975 exterior-length revision.	READY
6246_post75	6246	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	HIGH	Variant body after the 1975 exterior-length revision.	READY
6247	6247	Sedan	Volvo 164	164	4	EU-VOLVO-164-SEDAN-4D-01	HIGH	Four-door Volvo 164 body.	READY
6248	6248	Sedan	Volvo 164	164	4	EU-VOLVO-164-SEDAN-4D-01	HIGH	Four-door Volvo 164 body.	READY
6249	6249	Hatchback	Volkswagen Passat B2	Type32B			LOW	Passat B2 hatchback was offered with different door counts; this Ktype does not isolate one.	PENDING: 3-door versus 5-door body unresolved
6250	6250	Sedan	Volkswagen Passat B2	Type32B	4	EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	HIGH	Facelift B2 notchback body.	READY
6251	6251	Sedan	Volkswagen Passat B2	Type32B	4	EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	HIGH	Facelift B2 notchback body.	READY
6252	6252	Coupe	Volvo P1800	P1800	2		LOW	Length is confirmed, but a single traceable source for complete same-configuration L/W/H is still missing.	PENDING: complete P1800 three-dimensional source unresolved
6253	6253	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6254	6254	Coupe	Volvo P1800	P1800	2		LOW	Length is confirmed, but a single traceable source for complete same-configuration L/W/H is still missing.	PENDING: complete P1800 three-dimensional source unresolved
6255	6255	Coupe	Volvo P1800	P1800	2		LOW	Length is confirmed, but a single traceable source for complete same-configuration L/W/H is still missing.	PENDING: complete P1800 three-dimensional source unresolved
6256	6256	Wagon	Volvo 1800 ES	P1800ES	3		LOW	ES shooting-brake body identified; complete same-source L/W/H still not closed.	PENDING: complete 1800 ES three-dimensional source unresolved
6257	6257	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6258	6258	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6259	6259	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6260	6260	Wagon	Volkswagen Passat B2 Variant	Type32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-02	HIGH	Official B2 Variant body; new group retained because official dimensions differ from cached group.	READY
6261	6261	Wagon	Volkswagen Passat B2 Variant	Type32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-02	HIGH	Official B2 Variant body; new group retained because official dimensions differ from cached group.	READY
6262	6262	Sedan	Volkswagen Passat B3	35i	4	EU-VW-PASSAT-B3-35I-SEDAN-01	HIGH	B3 four-door sedan body.	READY
6263	6263	Wagon	Volkswagen Passat B3	35i	5	EU-VW-PASSAT-B3-35I-WAGON-01	HIGH	B3 five-door Variant body.	READY
6264_prefl	6264	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	Pre-facelift Type 53 exterior.	READY
6264_facelift	6264	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	1977 facelift Type 53 exterior with longer bumpers.	READY
6265	6265	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	Pre-facelift Type 53 exterior.	READY
6266	6266	Pickup	Volkswagen Taro	Type7A	2		LOW	Exact 79 hp 4x4 derivative identified, but the available direct page does not expose complete L/W/H; indirect press data still requires closure.	PENDING: direct complete 4x4 dimension source unresolved
6267_lowroof	6267	Van	Volkswagen Transporter T3	T3	4	EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Generic Kasten Ktype includes the standard/low-roof shell.	READY
6267_highroof	6267	Van	Volkswagen Transporter T3	T3	4	EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Generic Kasten Ktype includes the factory high-roof shell.	READY
6268	6268	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6269	6269	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6270	6270	Convertible	Volvo C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	Facelift C70 II retractable-hardtop body.	READY
6271	6271	Convertible	Volvo C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	Facelift C70 II retractable-hardtop body.	READY
6272	6272	Sedan	Volvo 240 Series				LOW	Ktype does not isolate 242/244 and the exact early/late exterior-length boundary.	PENDING: door count and year-specific 240 exterior branch unresolved
6273	6273	Sedan	Volvo 240 Series				LOW	Ktype does not isolate 242/244 and the exact early/late exterior-length boundary.	PENDING: door count and year-specific 240 exterior branch unresolved
6274_pre13	6274	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	2011 facelift body before the 2013 exterior revision.	READY
6274_facelift13	6274	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	2013 exterior revision.	READY
6275	6275	Sedan	Volvo 260 Series				LOW	Variant name references GLT6 but the Ktype does not reliably isolate 242/244/264 physical body.	PENDING: model and door-count branch unresolved
6276_2dr	6276	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6276_4dr	6276	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6277_2dr	6277	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Generic 140 sedan Ktype includes the two-door 142 body.	READY
6277_4dr	6277	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Generic 140 sedan Ktype includes the four-door 144 body.	READY
6278_pre13	6278	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	2011 facelift body before the 2013 exterior revision.	READY
6278_facelift13	6278	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	2013 exterior revision.	READY
6279_pre13	6279	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	2011 facelift body before the 2013 exterior revision.	READY
6279_facelift13	6279	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	2013 exterior revision.	READY
6283	6283	Coupe	Volvo 262C	262C	2		LOW	262C body identified, but complete same-source dimensions and exact early production boundary remain unresolved.	PENDING: complete 262C dimension source unresolved
6284	6284	Wagon	Volvo 260 Series	265	5		LOW	Available 265 specifications conflict with cached 260-family dimensions; no existing group was overwritten.	PENDING: 265 dimension-source conflict unresolved
6285	6285	Wagon	Volvo 260 Series	265	5		LOW	Available 265 specifications conflict with cached 260-family dimensions; no existing group was overwritten.	PENDING: 265 dimension-source conflict unresolved
6286	6286	Wagon	Volvo 260 Series	265	5		LOW	Available 265 specifications conflict with cached 260-family dimensions; no existing group was overwritten.	PENDING: 265 dimension-source conflict unresolved
6287	6287	Wagon	Volvo 260 Series	265	5		LOW	Available 265 specifications conflict with cached 260-family dimensions; no existing group was overwritten.	PENDING: 265 dimension-source conflict unresolved
6288_pre55	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-PRE55-01	HIGH	T1 bus before the 1955 body revision.	READY
6288_1955_57	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-1955-57-01	HIGH	T1 bus 1955-1957 body.	READY
6288_post58	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	T1 bus from the 1958 body revision.	READY
6289	6289	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6290	6290	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6291	6291	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6292	6292	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6293_pre55	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-PRE55-01	HIGH	T1 panel van before the 1955 body revision.	READY
6293_1955_57	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-1955-57-01	HIGH	T1 panel van 1955-1957 body.	READY
6293_post58	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	T1 panel van from the 1958 body revision.	READY
6294	6294	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	Post-1958 T1 panel-van body.	READY
6295_prefl	6295	MPV	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-MPV-PREFL-01	HIGH	T2 bus before the 1972/73 facelift body revision.	READY
6295_facelift	6295	MPV	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2 bus after the facelift body revision.	READY
6296_prefl	6296	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-PREFL-01	HIGH	T2 panel van before the facelift body revision.	READY
6296_facelift	6296	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH	T2 panel van after the facelift body revision.	READY
6297_prefl	6297	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-PREFL-01	HIGH	T2 panel van before the facelift body revision.	READY
6297_facelift	6297	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH	T2 panel van after the facelift body revision.	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-AMAZON-P130-SEDAN-2D-01	4450	1620	1505	Volvo Cars P130 heritage; kfz-tech Volvo Amazon technical data	https://www.volvocars.com/en-om/cars/legacy-models/p130-amazon-2-d/;https://www.kfz-tech.de/Engl/Hersteller/Volvo/VolvoAmazon.htm
EU-VOLVO-AMAZON-P120-SEDAN-4D-01	4450	1620	1505	Volvo Cars P120 heritage; kfz-tech Volvo Amazon technical data	https://www.volvocars.com/intl/media/press-releases/CBB96F1726C30DB4/;https://www.kfz-tech.de/Engl/Hersteller/Volvo/VolvoAmazon.htm
EU-VOLVO-66-WAGON-3D-01	3900	1540	1380	Volvo Cars Volvo 66 heritage; Auto-Data Volvo 66 model dimensions	https://www.volvocars.com/sg/cars/legacy-models/66/;https://www.auto-data.net/en/volvo-66-model-925
EU-VOLVO-140-142-SEDAN-2D-01	4640	1730	1440	Volvo Cars 142 heritage; CarsGuide 1968 Volvo 142 dimensions	https://www.volvocars.com/sg/cars/legacy-models/142/;https://www.carsguide.com.au/volvo/142/car-dimensions/1968
EU-VOLVO-140-144-SEDAN-4D-01	4640	1730	1440	CarsGuide 1967 Volvo 144 dimensions	https://www.carsguide.com.au/volvo/144/car-dimensions/1967
EU-VW-TYPE3-TYPE31-SEDAN-PRE69-01	4225	1605	1475	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-SEDAN-POST69-01	4340	1640	1470	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-HATCHBACK-TL-01	4225	1640	1475	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-WAGON-PRE69-01	4225	1605	1465	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	4190	1600	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	4290	1615	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VOLVO-164-SEDAN-4D-01	4714	1730	1440	Volvo Owners Club Volvo 164 technical facts	https://www.volvoclub.org.uk/history/164.shtml
EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	4266	1782	1447	Auto-Data Volvo C30 facelift D2 specifications	https://www.auto-data.net/en/volvo-c30-facelift-2010-1.6-d2-114hp-17536
EU-VOLVO-AMAZON-P220-WAGON-5D-01	4490	1620	1505	Volvo Cars P220 heritage; Volvo Owners Club P220 technical facts	https://www.volvocars.com/intl/media/press-releases/F4F10263D9F47544/;https://www.volvoclub.org.uk/history/p220.shtml
EU-VW-PASSAT-B2-VARIANT-WAGON-02	4540	1685	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B3-35I-SEDAN-01	4570	1705	1450	Volkswagen Newsroom Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B3-35I-WAGON-01	4570	1705	1450	Volkswagen Newsroom Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400	Auto-Data Volvo C70 II facelift D3 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-facelift-2009-2.0-d3-150hp-17545
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II facelift 2011 T4 specifications	https://www.auto-data.net/en/volvo-s80-ii-facelift-2011-1.6-t4-180hp-17565
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493	Volvo Support S80 dimensions	https://www.volvocars.com/en-ca/support/car/s80/article/0328ea86b98d614cc0a801e800b575bb//
EU-VW-TRANSPORTER-T1-MPV-PRE55-01	4100	1700	1900	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-MPV-1955-57-01	4190	1725	1940	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-MPV-POST58-01	4280	1750	1940	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-KASTEN-PRE55-01	4100	1700	1900	Fahrzeugseiten VW Bulli T1 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html
EU-VW-TRANSPORTER-T1-KASTEN-1955-57-01	4190	1725	1940	Fahrzeugseiten VW Bulli T1 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html
EU-VW-TRANSPORTER-T2-VAN-PREFL-01	4420	1765	1955	Fahrzeugseiten VW Bulli T2 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Kasten/bulli_t2_kasten.html
EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	4505	1720	1960	Fahrzeugseiten VW Bulli T2 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Kasten/bulli_t2_kasten.html
```

## 下一步优先处理

1. 先闭合 Volvo 240、260、262C、265 的门数、年代边界和与累计尺寸组的来源冲突。
2. 再处理 Volkswagen 411/412、Jetta I、Passat B1/B2 Hatchback 的门数及标准版／L 版分支。
3. 最后补齐 Volvo P1800／1800 ES、Volvo 145 和 Taro 4×4 的完整同配置三维来源。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664 "Vehicle data Type 3 1500/1600 profile | Volkswagen Newsroom"
[2]: https://www.kfz-tech.de/Engl/Hersteller/Volvo/VolvoAmazon.htm "www.kfz-tech.de"
[3]: https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html "Fahrzeugseiten.de - Nutzfahrzeuge - VW Bulli T1 Bus und Kombi"
[4]: https://www.carsguide.com.au/volvo/145/car-dimensions?utm_source=chatgpt.com "Volvo 145 Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5801-5900_ktype_dimension_mapping_final.tsv
- all_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Volkswagen 411/412 Sedan 的 2 门、4 门及标准版/L 版物理分支，并按 Volkswagen 官方规格创建四个尺寸组。([Volkswagen Newsroom][1])
* 已闭合 Volvo 240/260 年代分支、Volvo 145 年度宽度差异、P1800、1800 ES、262C 与 265 Wagon；Volvo 265 采用欧洲官方 1979 年车型手册规格。([汽车目录][2])
* 已闭合 Passat B2 1.6 TD 80 hp 改款五门 Hatchback。([auto-data.net][3])
* 当前仅剩 Ktype `6266`。精确版本身份已确认，但完整三维目前仍仅见于车主手册转述或 KBA 聚合页，尚未取得满足要求的直接规格来源，因此继续保持 PENDING。([auto-data.net][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：159
* PENDING 映射行：1
* 已确认尺寸组：58
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6198_2dr_std	6198	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 2-door branch.	READY
6198_2dr_l	6198	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 2-door branch.	READY
6198_4dr_std	6198	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 4-door branch.	READY
6198_4dr_l	6198	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 4-door branch.	READY
6199_411_2dr_std	6199	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 2-door branch.	READY
6199_411_2dr_l	6199	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 2-door branch.	READY
6199_411_4dr_std	6199	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 4-door branch.	READY
6199_411_4dr_l	6199	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 4-door branch.	READY
6199_412_2dr_std	6199	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6199_412_2dr_l	6199	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6199_412_4dr_std	6199	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6199_412_4dr_l	6199	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6200_2dr_std	6200	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6200_2dr_l	6200	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6200_4dr_std	6200	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6200_4dr_l	6200	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6201_2dr_std	6201	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6201_2dr_l	6201	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6201_4dr_std	6201	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6201_4dr_l	6201	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6220_2dr_mid	6220	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	242 mid-period exterior branch.	READY
6220_2dr_late	6220	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-LATE-01	MEDIUM	242 late-period exterior branch.	READY
6220_4dr_mid	6220	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	244 mid-period exterior branch.	READY
6220_4dr_late	6220	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	MEDIUM	244 late-period exterior branch.	READY
6221	6221	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	HIGH	Late-period 244 four-door body.	READY
6223	6223	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-LATE-01	HIGH	Late-period 245 wagon body.	READY
6225_early	6225	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	245 early-period exterior branch.	READY
6225_late	6225	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-LATE-01	MEDIUM	245 late-period exterior branch.	READY
6227_early	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-EARLY-01	MEDIUM	264 early-period exterior branch.	READY
6227_facelift	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-FACELIFT-01	MEDIUM	264 facelift-period exterior branch.	READY
6227_late	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	MEDIUM	264 late-period exterior branch.	READY
6228	6228	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	HIGH	Late-period 264 four-door body.	READY
6233	6233	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	HIGH	Late-period 264 four-door body.	READY
6236_2dr	6236	Sedan	Volkswagen Jetta I	Type16	2	EU-VW-JETTA-I-SEDAN-01	MEDIUM	Jetta I 2-door body.	READY
6236_4dr	6236	Sedan	Volkswagen Jetta I	Type16	4	EU-VW-JETTA-I-SEDAN-01	MEDIUM	Jetta I 4-door body.	READY
6237	6237	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6239_early	6239	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-EARLY-01	MEDIUM	145 early-period exterior branch.	READY
6239_late	6239	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	MEDIUM	145 late-period exterior branch.	READY
6240	6240	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6241	6241	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6242	6242	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6243_3dr_pre75	6243	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	3-door pre75 exterior branch.	READY
6243_3dr_post75	6243	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	3-door post75 exterior branch.	READY
6243_5dr_pre75	6243	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	5-door pre75 exterior branch.	READY
6243_5dr_post75	6243	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	5-door post75 exterior branch.	READY
6244_3dr_pre75	6244	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	3-door pre75 exterior branch.	READY
6244_3dr_post75	6244	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	3-door post75 exterior branch.	READY
6244_5dr_pre75	6244	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	5-door pre75 exterior branch.	READY
6244_5dr_post75	6244	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	5-door post75 exterior branch.	READY
6249	6249	Hatchback	Volkswagen Passat B2	Type32B	5	EU-VW-PASSAT-B2-HATCHBACK-FACELIFT-01	HIGH	Facelift five-door hatchback body.	READY
6252	6252	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6254	6254	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6255	6255	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6256	6256	Wagon	Volvo 1800 ES	P1800ES	3	EU-VOLVO-1800ES-WAGON-3D-01	HIGH	1800 ES three-door shooting-brake body.	READY
6272_2dr	6272	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-EARLY-01	MEDIUM	Early 242 2-door body.	READY
6272_4dr	6272	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-EARLY-01	MEDIUM	Early 244 4-door body.	READY
6273	6273	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	HIGH	Late-period 244 four-door body.	READY
6275_2dr	6275	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	GLT6 242 2-door body.	READY
6275_4dr	6275	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	GLT6 244 4-door body.	READY
6283	6283	Coupe	Volvo 262C	262C	2	EU-VOLVO-262C-COUPE-EARLY-01	MEDIUM	Early 262C two-door coupe body.	READY
6284	6284	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6285	6285	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6286	6286	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6287	6287	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-411-SEDAN-STD-01	4525	1635	1485	Volkswagen Newsroom Volkswagen 411 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658
EU-VW-411-SEDAN-L-01	4553	1650	1485	Volkswagen Newsroom Volkswagen 411 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658
EU-VW-412-SEDAN-STD-01	4555	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-412-SEDAN-L-01	4583	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VOLVO-260-SEDAN-LATE-01	4785	1707	1427	Automobile-Catalog 1981 Volvo 264 Europe specifications	https://www.automobile-catalog.com/car/1981/45950/volvo_264.html
EU-VOLVO-145-WAGON-EARLY-01	4640	1730	1450	Volvo Cars Volvo 145 heritage; CarsGuide 1968 Volvo 145 dimensions	https://www.volvocars.com/sg/cars/legacy-models/145/;https://www.carsguide.com.au/volvo/145/car-dimensions/1968
EU-VOLVO-145-WAGON-LATE-01	4640	1735	1450	Volvo Cars Volvo 145 heritage; CarsGuide Volvo 145 dimensions by year	https://www.volvocars.com/sg/cars/legacy-models/145/;https://www.carsguide.com.au/volvo/145/car-dimensions
EU-VW-PASSAT-B2-HATCHBACK-FACELIFT-01	4435	1685	1385	Auto-Data Volkswagen Passat B2 1.6 TD 80 Hp	https://www.auto-data.net/en/volkswagen-passat-b2-1.6-td-80hp-9002
EU-VOLVO-P1800-COUPE-2D-01	4400	1700	1285	Auto-Data Volvo 1800 model dimensions	https://www.auto-data.net/en/volvo-1800-model-2899
EU-VOLVO-1800ES-WAGON-3D-01	4384	1699	1280	Volvo 1800E and 1800ES official brochure 1971	https://bin.yhdistysavain.fi/1597125/T30HEdKdWxnnunNQ6Ld60cPtag/P1800ES-Brochure-1971.pdf
EU-VOLVO-262C-COUPE-EARLY-01	4880	1710	1360	Automobile-Catalog 1977 Volvo 262 C Europe specifications	https://www.automobile-catalog.com/car/1977/40085/volvo_262_c.html
EU-VOLVO-265-WAGON-01	4880	1710	1460	Volvo 1979 Range official brochure	https://www.volvoclub.org.uk/pdf/brochures/Volvo1979.pdf
```

## 下一步优先处理

1. 仅处理 Ktype `6266`：寻找 Volkswagen Taro 1994 年技术手册、车主手册或同等级直接规格资料，确认 4×4 XtraCab 的完整三维及不含后视镜宽度。
2. 闭合后不再展开其他车型检索，立即执行表头、唯一键、引用闭合和文件链接机械检查，并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658 "https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658"
[2]: https://www.automobile-catalog.com/car/1981/45950/volvo_264.html "https://www.automobile-catalog.com/car/1981/45950/volvo_264.html"
[3]: https://www.auto-data.net/en/volkswagen-passat-b2-1.6-td-80hp-9002 "https://www.auto-data.net/en/volkswagen-passat-b2-1.6-td-80hp-9002"
[4]: https://www.auto-data.net/en/volkswagen-taro-2.4-d-79hp-4x4-9166 "https://www.auto-data.net/en/volkswagen-taro-2.4-d-79hp-4x4-9166"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5801-5900_ktype_dimension_mapping_final.tsv
- all_5801-5900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已将 Ktype `6266` 闭合为 2 座单排、5 座两门加长驾驶室和 5 座四门驾驶室三个映射分支；后两个分支复用同一尺寸组。瑞士 FEDRO 型式认证记录分别给出 `3VD101` 的 `4720×1650×1745 mm` 和 `3VD102` 的 `4720×1690×1735 mm`。([motoro.ch][1])
* 已完成最终机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有引用闭合，长宽高及来源均非空，指定下载文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：162
* PENDING 映射：0
* 完整尺寸组：69
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6190	6190	Convertible	Karmann Ghia Type 14	Type14	2	EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	HIGH	Type 14 two-door convertible.	READY
6192_pre67	6192	Sedan	Volkswagen Beetle Type 1	Type11	2	EU-VW-KAEFER-TYPE11-STD-01	MEDIUM	Pre-August-1967 Type 11 exterior branch.	READY
6192_post67	6192	Sedan	Volkswagen Beetle Type 1	Type11	2	EU-VW-KAEFER-TYPE11-POST67-01	MEDIUM	Post-August-1967 Type 11 exterior branch.	READY
6193	6193	Sedan	Volkswagen Beetle 1302	Type11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH	1302 sedan body.	READY
6194	6194	Sedan	Volkswagen Beetle 1302	Type11	2	EU-VW-KAEFER-1302-SEDAN-01	HIGH	1302 sedan body.	READY
6195	6195	Targa	Porsche 914	914	2	EU-PORSCHE-914-TARGA-01	HIGH	914 Targa body.	READY
6196_std	6196	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-STD-01	MEDIUM	Standard exterior branch.	READY
6196_l	6196	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-L-01	MEDIUM	L exterior branch.	READY
6197_std	6197	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-STD-01	MEDIUM	Standard exterior branch.	READY
6197_l	6197	Wagon	Volkswagen 412	Type412	3	EU-VW-412-WAGON-L-01	MEDIUM	L exterior branch.	READY
6198_2dr_std	6198	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 2-door branch.	READY
6198_2dr_l	6198	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 2-door branch.	READY
6198_4dr_std	6198	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 4-door branch.	READY
6198_4dr_l	6198	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 4-door branch.	READY
6199_411_2dr_std	6199	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 2-door branch.	READY
6199_411_2dr_l	6199	Sedan	Volkswagen 411	Type411	2	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 2-door branch.	READY
6199_411_4dr_std	6199	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-STD-01	MEDIUM	411 standard-body 4-door branch.	READY
6199_411_4dr_l	6199	Sedan	Volkswagen 411	Type411	4	EU-VW-411-SEDAN-L-01	MEDIUM	411 L-body 4-door branch.	READY
6199_412_2dr_std	6199	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6199_412_2dr_l	6199	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6199_412_4dr_std	6199	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6199_412_4dr_l	6199	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6200_2dr_std	6200	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6200_2dr_l	6200	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6200_4dr_std	6200	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6200_4dr_l	6200	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6201_2dr_std	6201	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 2-door branch.	READY
6201_2dr_l	6201	Sedan	Volkswagen 412	Type412	2	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 2-door branch.	READY
6201_4dr_std	6201	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-STD-01	MEDIUM	412 standard-body 4-door branch.	READY
6201_4dr_l	6201	Sedan	Volkswagen 412	Type412	4	EU-VW-412-SEDAN-L-01	MEDIUM	412 L-body 4-door branch.	READY
6202_2dr	6202	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P130 two-door Amazon branch.	READY
6202_4dr	6202	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P120 four-door Amazon branch.	READY
6203_2dr	6203	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P130 two-door Amazon branch.	READY
6203_4dr	6203	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P120 four-door Amazon branch.	READY
6204	6204	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6206	6206	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6207_2dr	6207	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P130 two-door Amazon branch.	READY
6207_4dr	6207	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P120 four-door Amazon branch.	READY
6208_2dr	6208	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	MEDIUM	P130 two-door Amazon branch.	READY
6208_4dr	6208	Sedan	Volvo Amazon	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-4D-01	MEDIUM	P120 four-door Amazon branch.	READY
6209	6209	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6210	6210	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6211	6211	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6212	6212	Sedan	Volvo Amazon	P130	2	EU-VOLVO-AMAZON-P130-SEDAN-2D-01	HIGH	Late P130 two-door Amazon body.	READY
6213	6213	Wagon	Volvo 66	66	3	EU-VOLVO-66-WAGON-3D-01	HIGH	Three-door estate body.	READY
6214	6214	Wagon	Volvo 66	66	3	EU-VOLVO-66-WAGON-3D-01	HIGH	Three-door estate body.	READY
6216_2dr	6216	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6216_4dr	6216	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6217_2dr	6217	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6217_4dr	6217	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6218_2dr	6218	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6218_4dr	6218	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6219_2dr	6219	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6219_4dr	6219	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6220_2dr_mid	6220	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	242 mid-period exterior branch.	READY
6220_2dr_late	6220	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-LATE-01	MEDIUM	242 late-period exterior branch.	READY
6220_4dr_mid	6220	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	244 mid-period exterior branch.	READY
6220_4dr_late	6220	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	MEDIUM	244 late-period exterior branch.	READY
6221	6221	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	HIGH	Late-period 244 four-door body.	READY
6222	6222	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	Early 245 wagon body.	READY
6223	6223	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-LATE-01	HIGH	Late-period 245 wagon body.	READY
6224	6224	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	Early 245 wagon body.	READY
6225_early	6225	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-EARLY-01	MEDIUM	Early-period 245 exterior branch.	READY
6225_late	6225	Wagon	Volvo 240 Series	245	5	EU-VOLVO-240-WAGON-LATE-01	MEDIUM	Late-period 245 exterior branch.	READY
6227_early	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-EARLY-01	MEDIUM	264 early-period exterior branch.	READY
6227_facelift	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-FACELIFT-01	MEDIUM	264 facelift-period exterior branch.	READY
6227_late	6227	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	MEDIUM	264 late-period exterior branch.	READY
6228	6228	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	HIGH	Late-period 264 four-door body.	READY
6229_pre69	6229	Sedan	Volkswagen Type 3	Type31	2	EU-VW-TYPE3-TYPE31-SEDAN-PRE69-01	HIGH	Type 3 notchback before the 1969 exterior revision.	READY
6229_post69	6229	Sedan	Volkswagen Type 3	Type31	2	EU-VW-TYPE3-TYPE31-SEDAN-POST69-01	HIGH	Type 3 notchback after the 1969 exterior revision.	READY
6230	6230	Hatchback	Volkswagen Type 3	Type31	3	EU-VW-TYPE3-TYPE31-HATCHBACK-TL-01	HIGH	Type 3 TL fastback body.	READY
6232	6232	Wagon	Volkswagen Type 3	Type31	3	EU-VW-TYPE3-TYPE31-WAGON-PRE69-01	HIGH	Early Type 3 Variant body.	READY
6233	6233	Sedan	Volvo 260 Series	264	4	EU-VOLVO-260-SEDAN-LATE-01	HIGH	Late-period 264 four-door body.	READY
6234	6234	Hatchback	Volkswagen Polo II	Type86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	Early Polo II three-door hatchback.	READY
6235	6235	Sedan	Volkswagen Derby II	Type87	2	EU-VW-DERBY-II-TYPE87-SEDAN-01	HIGH	Derby II two-door sedan.	READY
6236_2dr	6236	Sedan	Volkswagen Jetta I	Type16	2	EU-VW-JETTA-I-SEDAN-01	MEDIUM	Jetta I two-door body.	READY
6236_4dr	6236	Sedan	Volkswagen Jetta I	Type16	4	EU-VW-JETTA-I-SEDAN-01	MEDIUM	Jetta I four-door body.	READY
6237	6237	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6238	6238	Hatchback	Volkswagen Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	CityStromer five-door Golf III shell.	READY
6239_early	6239	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-EARLY-01	MEDIUM	145 early-period exterior branch.	READY
6239_late	6239	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	MEDIUM	145 late-period exterior branch.	READY
6240	6240	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6241	6241	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6242	6242	Wagon	Volvo 140 Series	145	5	EU-VOLVO-145-WAGON-LATE-01	HIGH	Later 145 five-door wagon body.	READY
6243_3dr_pre75	6243	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	3-door pre-1975 exterior branch.	READY
6243_3dr_post75	6243	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	3-door post-1975 exterior branch.	READY
6243_5dr_pre75	6243	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	5-door pre-1975 exterior branch.	READY
6243_5dr_post75	6243	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	5-door post-1975 exterior branch.	READY
6244_3dr_pre75	6244	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	3-door pre-1975 exterior branch.	READY
6244_3dr_post75	6244	Hatchback	Volkswagen Passat B1	Type32	3	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	3-door post-1975 exterior branch.	READY
6244_5dr_pre75	6244	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	MEDIUM	5-door pre-1975 exterior branch.	READY
6244_5dr_post75	6244	Hatchback	Volkswagen Passat B1	Type32	5	EU-VW-PASSAT-B1-HATCHBACK-POST75-01	MEDIUM	5-door post-1975 exterior branch.	READY
6245_pre75	6245	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	HIGH	Variant body before the 1975 exterior revision.	READY
6245_post75	6245	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	HIGH	Variant body after the 1975 exterior revision.	READY
6246_pre75	6246	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	HIGH	Variant body before the 1975 exterior revision.	READY
6246_post75	6246	Wagon	Volkswagen Passat B1 Variant	Type33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	HIGH	Variant body after the 1975 exterior revision.	READY
6247	6247	Sedan	Volvo 164	164	4	EU-VOLVO-164-SEDAN-4D-01	HIGH	Four-door Volvo 164 body.	READY
6248	6248	Sedan	Volvo 164	164	4	EU-VOLVO-164-SEDAN-4D-01	HIGH	Four-door Volvo 164 body.	READY
6249	6249	Hatchback	Volkswagen Passat B2	Type32B	5	EU-VW-PASSAT-B2-HATCHBACK-FACELIFT-01	HIGH	Facelift five-door hatchback body.	READY
6250	6250	Sedan	Volkswagen Passat B2	Type32B	4	EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	HIGH	Facelift B2 notchback body.	READY
6251	6251	Sedan	Volkswagen Passat B2	Type32B	4	EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	HIGH	Facelift B2 notchback body.	READY
6252	6252	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6253	6253	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6254	6254	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6255	6255	Coupe	Volvo P1800	P1800	2	EU-VOLVO-P1800-COUPE-2D-01	HIGH	P1800 two-door coupe body.	READY
6256	6256	Wagon	Volvo 1800 ES	P1800ES	3	EU-VOLVO-1800ES-WAGON-3D-01	HIGH	1800 ES three-door shooting-brake body.	READY
6257	6257	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6258	6258	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6259	6259	Wagon	Volvo Amazon	P220	5	EU-VOLVO-AMAZON-P220-WAGON-5D-01	HIGH	P220 Amazon estate body.	READY
6260	6260	Wagon	Volkswagen Passat B2 Variant	Type32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-02	HIGH	B2 Variant wagon body.	READY
6261	6261	Wagon	Volkswagen Passat B2 Variant	Type32B	5	EU-VW-PASSAT-B2-VARIANT-WAGON-02	HIGH	B2 Variant wagon body.	READY
6262	6262	Sedan	Volkswagen Passat B3	35i	4	EU-VW-PASSAT-B3-35I-SEDAN-01	HIGH	B3 four-door sedan body.	READY
6263	6263	Wagon	Volkswagen Passat B3	35i	5	EU-VW-PASSAT-B3-35I-WAGON-01	HIGH	B3 five-door Variant body.	READY
6264_prefl	6264	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	Pre-facelift Type 53 exterior.	READY
6264_facelift	6264	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-3D-01	HIGH	Longer-bumper Type 53 exterior.	READY
6265	6265	Coupe	Volkswagen Scirocco I	Type53	3	EU-VW-SCIROCCO-I-COUPE-STD-01	HIGH	Pre-facelift Type 53 exterior.	READY
6266_singlecab	6266	Pickup	Volkswagen Taro	Type7A	2	EU-VW-TARO-PICKUP-4X4-79HP-2SEAT-01	MEDIUM	Two-seat 4x4 single-cab approval branch.	READY
6266_xtracab	6266	Pickup	Volkswagen Taro	Type7A	2	EU-VW-TARO-PICKUP-4X4-79HP-5SEAT-01	MEDIUM	Five-seat 4x4 two-door extended-cab approval branch.	READY
6266_doublecab	6266	Pickup	Volkswagen Taro	Type7A	4	EU-VW-TARO-PICKUP-4X4-79HP-5SEAT-01	MEDIUM	Five-seat 4x4 four-door cab approval branch.	READY
6267_lowroof	6267	Van	Volkswagen Transporter T3	T3	4	EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Standard/low-roof panel-van branch.	READY
6267_highroof	6267	Van	Volkswagen Transporter T3	T3	4	EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Factory high-roof panel-van branch.	READY
6268	6268	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6269	6269	Hatchback	Volvo C30 I facelift		3	EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	HIGH	Facelift C30 three-door body.	READY
6270	6270	Convertible	Volvo C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	Facelift C70 II retractable-hardtop body.	READY
6271	6271	Convertible	Volvo C70 II facelift		2	EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	HIGH	Facelift C70 II retractable-hardtop body.	READY
6272_2dr	6272	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-EARLY-01	MEDIUM	Early 242 two-door body.	READY
6272_4dr	6272	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-EARLY-01	MEDIUM	Early 244 four-door body.	READY
6273	6273	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-LATE-01	HIGH	Late-period 244 four-door body.	READY
6274_pre13	6274	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	Applicable exterior revision branch.	READY
6274_facelift13	6274	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	Applicable exterior revision branch.	READY
6275_2dr	6275	Sedan	Volvo 240 Series	242	2	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	GLT6 242 two-door body.	READY
6275_4dr	6275	Sedan	Volvo 240 Series	244	4	EU-VOLVO-240-SEDAN-MID-01	MEDIUM	GLT6 244 four-door body.	READY
6276_2dr	6276	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6276_4dr	6276	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6277_2dr	6277	Sedan	Volvo 140 Series	142	2	EU-VOLVO-140-142-SEDAN-2D-01	MEDIUM	Two-door 142 branch.	READY
6277_4dr	6277	Sedan	Volvo 140 Series	144	4	EU-VOLVO-140-144-SEDAN-4D-01	MEDIUM	Four-door 144 branch.	READY
6278_pre13	6278	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	Pre-2013 exterior revision branch.	READY
6278_facelift13	6278	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	2013 exterior revision branch.	READY
6279_pre13	6279	Sedan	Volvo S80 II facelift		4	EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	HIGH	Pre-2013 exterior revision branch.	READY
6279_facelift13	6279	Sedan	Volvo S80 II facelift 2013		4	EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	HIGH	2013 exterior revision branch.	READY
6283	6283	Coupe	Volvo 262C	262C	2	EU-VOLVO-262C-COUPE-EARLY-01	MEDIUM	Early 262C two-door coupe body.	READY
6284	6284	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6285	6285	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6286	6286	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6287	6287	Wagon	Volvo 260 Series	265	5	EU-VOLVO-265-WAGON-01	HIGH	Volvo 265 five-door wagon body.	READY
6288_pre55	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-PRE55-01	HIGH	T1 bus before the 1955 body revision.	READY
6288_1955_57	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-1955-57-01	HIGH	T1 bus 1955–1957 body.	READY
6288_post58	6288	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	T1 bus from the 1958 body revision.	READY
6289	6289	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6290	6290	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6291	6291	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6292	6292	MPV	Volkswagen Transporter T1	T1	3	EU-VW-TRANSPORTER-T1-MPV-POST58-01	HIGH	Post-1958 T1 bus body.	READY
6293_pre55	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-PRE55-01	HIGH	T1 panel van before the 1955 body revision.	READY
6293_1955_57	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-1955-57-01	HIGH	T1 panel van 1955–1957 body.	READY
6293_post58	6293	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	T1 panel van from the 1958 body revision.	READY
6294	6294	Van	Volkswagen Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	HIGH	Post-1958 T1 panel-van body.	READY
6295_prefl	6295	MPV	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-MPV-PREFL-01	HIGH	T2 bus before the facelift body revision.	READY
6295_facelift	6295	MPV	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	HIGH	T2 bus after the facelift body revision.	READY
6296_prefl	6296	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-PREFL-01	HIGH	T2 panel van before the facelift body revision.	READY
6296_facelift	6296	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH	T2 panel van after the facelift body revision.	READY
6297_prefl	6297	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-PREFL-01	HIGH	T2 panel van before the facelift body revision.	READY
6297_facelift	6297	Van	Volkswagen Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH	T2 panel van after the facelift body revision.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5801-5900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-KARMANN-GHIA-TYPE14-CONVERTIBLE-01	4140	1634	1330	Volkswagen Newsroom Karmann Ghia Type 14 Cabriolet vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-karmann-ghia-typ-14-cabriolet-profile-19634
EU-VW-KAEFER-TYPE11-STD-01	4070	1540	1500	Volkswagen Newsroom Beetle 1300 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1300-profile-19591
EU-VW-KAEFER-TYPE11-POST67-01	4030	1550	1500	Volkswagen Newsroom Beetle 1500 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1500-profile-19600
EU-VW-KAEFER-1302-SEDAN-01	4080	1585	1500	Volkswagen Newsroom Beetle 1302 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-1302-profile-19594
EU-PORSCHE-914-TARGA-01	3985	1650	1230	Volkswagen Newsroom VW-Porsche 914 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-vw-porsche-914-profile-19673
EU-VW-412-WAGON-STD-01	4555	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-412-WAGON-L-01	4583	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-411-SEDAN-STD-01	4525	1635	1485	Volkswagen Newsroom Volkswagen 411 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658
EU-VW-411-SEDAN-L-01	4553	1650	1485	Volkswagen Newsroom Volkswagen 411 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-411-profile-19658
EU-VW-412-SEDAN-STD-01	4555	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VW-412-SEDAN-L-01	4583	1675	1475	Volkswagen Newsroom Volkswagen 412 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-volkswagen-412-profile-19661
EU-VOLVO-AMAZON-P130-SEDAN-2D-01	4450	1620	1505	Volvo Cars P130 heritage; kfz-tech Volvo Amazon technical data	https://www.volvocars.com/en-om/cars/legacy-models/p130-amazon-2-d/;https://www.kfz-tech.de/Engl/Hersteller/Volvo/VolvoAmazon.htm
EU-VOLVO-AMAZON-P120-SEDAN-4D-01	4450	1620	1505	Volvo Cars P120 heritage; kfz-tech Volvo Amazon technical data	https://www.volvocars.com/intl/media/press-releases/CBB96F1726C30DB4/;https://www.kfz-tech.de/Engl/Hersteller/Volvo/VolvoAmazon.htm
EU-VOLVO-66-WAGON-3D-01	3900	1540	1380	Volvo Cars Volvo 66 heritage; Auto-Data Volvo 66 model dimensions	https://www.volvocars.com/sg/cars/legacy-models/66/;https://www.auto-data.net/en/volvo-66-model-925
EU-VOLVO-140-142-SEDAN-2D-01	4640	1730	1440	Volvo Cars 142 heritage; CarsGuide 1968 Volvo 142 dimensions	https://www.volvocars.com/sg/cars/legacy-models/142/;https://www.carsguide.com.au/volvo/142/car-dimensions/1968
EU-VOLVO-140-144-SEDAN-4D-01	4640	1730	1440	CarsGuide 1967 Volvo 144 dimensions	https://www.carsguide.com.au/volvo/144/car-dimensions/1967
EU-VOLVO-240-SEDAN-MID-01	4890	1707	1430	Automobile-Catalog 1979 Volvo 244 GL Europe specifications	https://www.automobile-catalog.com/car/1979/34760/volvo_244_gl.html
EU-VOLVO-240-SEDAN-LATE-01	4785	1707	1427	Automobile-Catalog 1985 Volvo 244 Turbo Europe specifications	https://www.automobile-catalog.com/car/1985/45905/volvo_244_turbo.html
EU-VOLVO-240-WAGON-EARLY-01	4898	1710	1460	AutoTrader Volvo 245 dimensions by year	https://www.autotrader.com.au/volvo/245/dimensions
EU-VOLVO-240-WAGON-LATE-01	4785	1707	1427	Automobile-Catalog 1981 Volvo 245 GL Europe specifications	https://www.automobile-catalog.com/car/1981/45935/volvo_245_gl.html
EU-VOLVO-260-SEDAN-EARLY-01	4897	1707	1435	Automobile-Catalog 1975 Volvo 264 DL Europe specifications	https://www.automobile-catalog.com/car/1975/34520/volvo_264_dl.html
EU-VOLVO-260-SEDAN-FACELIFT-01	4890	1707	1430	Automobile-Catalog 1979 Volvo 264 GLE Europe specifications	https://www.automobile-catalog.com/car/1979/34775/volvo_264_gle.html
EU-VOLVO-260-SEDAN-LATE-01	4785	1707	1427	Automobile-Catalog 1981 Volvo 264 Europe specifications	https://www.automobile-catalog.com/car/1981/45950/volvo_264.html
EU-VW-TYPE3-TYPE31-SEDAN-PRE69-01	4225	1605	1475	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-SEDAN-POST69-01	4340	1640	1470	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-HATCHBACK-TL-01	4225	1640	1475	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-TYPE3-TYPE31-WAGON-PRE69-01	4225	1605	1465	Volkswagen Newsroom Type 3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-type-3-15001600-profile-19664
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355	Volkswagen Newsroom Polo II vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-2-profile-19144
EU-VW-DERBY-II-TYPE87-SEDAN-01	3975	1600	1355	Volkswagen Newsroom Derby vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-JETTA-I-SEDAN-01	4190	1610	1410	Volkswagen Newsroom Jetta I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-jetta-1-profile-19641
EU-VOLVO-145-WAGON-LATE-01	4640	1735	1450	Volvo Cars Volvo 145 heritage; CarsGuide Volvo 145 dimensions by year	https://www.volvocars.com/sg/cars/legacy-models/145/;https://www.carsguide.com.au/volvo/145/car-dimensions
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Volkswagen Newsroom Golf III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
EU-VOLVO-145-WAGON-EARLY-01	4640	1730	1450	Volvo Cars Volvo 145 heritage; CarsGuide 1968 Volvo 145 dimensions	https://www.volvocars.com/sg/cars/legacy-models/145/;https://www.carsguide.com.au/volvo/145/car-dimensions/1968
EU-VW-PASSAT-B1-HATCHBACK-PRE75-01	4190	1600	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-HATCHBACK-POST75-01	4290	1615	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-TYPE33-WAGON-PRE75-01	4190	1600	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VW-PASSAT-B1-TYPE33-WAGON-POST75-01	4290	1615	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-VOLVO-164-SEDAN-4D-01	4714	1730	1440	Volvo Owners Club Volvo 164 technical facts	https://www.volvoclub.org.uk/history/164.shtml
EU-VW-PASSAT-B2-HATCHBACK-FACELIFT-01	4435	1685	1385	Auto-Data Volkswagen Passat B2 1.6 TD 80 Hp	https://www.auto-data.net/en/volkswagen-passat-b2-1.6-td-80hp-9002
EU-VW-PASSAT-B2-NOTCHBACK-FACELIFT-01	4530	1710	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VOLVO-P1800-COUPE-2D-01	4400	1700	1285	Auto-Data Volvo 1800 model dimensions	https://www.auto-data.net/en/volvo-1800-model-2899
EU-VOLVO-C30-I-FACELIFT-HATCHBACK-3D-01	4266	1782	1447	Auto-Data Volvo C30 facelift D2 specifications	https://www.auto-data.net/en/volvo-c30-facelift-2010-1.6-d2-114hp-17536
EU-VOLVO-1800ES-WAGON-3D-01	4384	1699	1280	Volvo 1800E and 1800ES official brochure 1971	https://bin.yhdistysavain.fi/1597125/T30HEdKdWxnnunNQ6Ld60cPtag/P1800ES-Brochure-1971.pdf
EU-VOLVO-AMAZON-P220-WAGON-5D-01	4490	1620	1505	Volvo Cars P220 heritage; Volvo Owners Club P220 technical facts	https://www.volvocars.com/intl/media/press-releases/F4F10263D9F47544/;https://www.volvoclub.org.uk/history/p220.shtml
EU-VW-PASSAT-B2-VARIANT-WAGON-02	4540	1685	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VW-PASSAT-B3-35I-SEDAN-01	4570	1705	1450	Volkswagen Newsroom Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-PASSAT-B3-35I-WAGON-01	4570	1705	1450	Volkswagen Newsroom Passat B3 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b3-profile-19541
EU-VW-SCIROCCO-I-COUPE-STD-01	3855	1625	1310	Volkswagen Newsroom Scirocco I vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-scirocco-1-profile-19648
EU-VW-SCIROCCO-I-COUPE-3D-01	3885	1624	1309	Automobile-Catalog 1979 Volkswagen Scirocco 1300 Europe specifications	https://www.automobile-catalog.com/car/1979/42650/volkswagen_scirocco_1300.html
EU-VW-TARO-PICKUP-4X4-79HP-2SEAT-01	4720	1650	1745	Swiss FEDRO type approval 3VD101 via Motoro	https://motoro.ch/en/fiche-technique/vw/taro-4x4
EU-VW-TARO-PICKUP-4X4-79HP-5SEAT-01	4720	1690	1735	Swiss FEDRO type approval 3VD102 via Motoro	https://motoro.ch/en/fiche-technique/vw/taro-4x4
EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	4570	1845	1965	Fahrzeugseiten VW Transporter T3 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T3_Kasten/bulli_t3_kasten.html
EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	4570	1845	2365	Fahrzeugseiten VW Transporter T3 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T3_Kasten/bulli_t3_kasten.html
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400	Auto-Data Volvo C70 II facelift D3 specifications	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-facelift-2009-2.0-d3-150hp-17545
EU-VOLVO-240-SEDAN-EARLY-01	4897	1707	1435	Automobile-Catalog 1976 Volvo 244 L Europe specifications	https://www.automobile-catalog.com/car/1976/34400/volvo_244_l.html
EU-VOLVO-S80-II-FACELIFT-2011-SEDAN-4D-01	4851	1861	1493	Auto-Data Volvo S80 II facelift 2011 T4 specifications	https://www.auto-data.net/en/volvo-s80-ii-facelift-2011-1.6-t4-180hp-17565
EU-VOLVO-S80-II-FACELIFT-2013-SEDAN-4D-01	4854	1861	1493	Volvo Support S80 dimensions	https://www.volvocars.com/en-ca/support/car/s80/article/0328ea86b98d614cc0a801e800b575bb/
EU-VOLVO-262C-COUPE-EARLY-01	4880	1710	1360	Automobile-Catalog 1977 Volvo 262 C Europe specifications	https://www.automobile-catalog.com/car/1977/40085/volvo_262_c.html
EU-VOLVO-265-WAGON-01	4880	1710	1460	Volvo 1979 Range official brochure	https://www.volvoclub.org.uk/pdf/brochures/Volvo1979.pdf
EU-VW-TRANSPORTER-T1-MPV-PRE55-01	4100	1700	1900	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-MPV-1955-57-01	4190	1725	1940	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-MPV-POST58-01	4280	1750	1940	Fahrzeugseiten VW Bulli T1 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Bus/bulli_t1_bus.html
EU-VW-TRANSPORTER-T1-KASTEN-PRE55-01	4100	1700	1900	Fahrzeugseiten VW Bulli T1 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html
EU-VW-TRANSPORTER-T1-KASTEN-1955-57-01	4190	1725	1940	Fahrzeugseiten VW Bulli T1 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html
EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	4280	1750	1940	Fahrzeugseiten VW Bulli T1 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T1_Kasten/bulli_t1_kasten.html
EU-VW-TRANSPORTER-T2-MPV-PREFL-01	4420	1765	1960	Fahrzeugseiten VW Bulli T2 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Bus/bulli_t2_bus.html
EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	4505	1720	1960	Fahrzeugseiten VW Bulli T2 Bus/Kombi technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Bus/bulli_t2_bus.html
EU-VW-TRANSPORTER-T2-VAN-PREFL-01	4420	1765	1955	Fahrzeugseiten VW Bulli T2 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Kasten/bulli_t2_kasten.html
EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	4505	1720	1960	Fahrzeugseiten VW Bulli T2 Kastenwagen technical data	https://www.fahrzeugseiten.de/Nutzfahrzeuge/VW/Bulli_T2_Kasten/bulli_t2_kasten.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5801-5900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://motoro.ch/en/fiche-technique/vw/taro-4x4 "motoro.ch"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5801-5900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5801-5900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7439 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2308 行）

- 尺寸冲突协调：
  - EU-VW-PASSAT-B3-35I-SEDAN-01 -> EU-VW-PASSAT-B3-35I-SEDAN-02：4575x1705x1430 与 4570x1705x1450，创建新尺寸组
