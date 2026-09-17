# 任务：all 第 2801-2900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0029__aa15c83f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2801-2900 行

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
all 第 2801-2900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-CABRIOLET-2D-01	4238	1765	1424
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423
EU-AUDI-A3-II-HATCHBACK-5D-PREFL-01	4286	1765	1423
EU-AUDI-A4-B7-8E-AVANT-WAGON-5D-01	4586	1772	1427
EU-AUDI-A4-B7-CONVERTIBLE-01	4573	1777	1391
EU-AUDI-A4-B7-CONVERTIBLE-02	4570	1780	1390
EU-AUDI-A4-B7-SEDAN-01	4586	1772	1427
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-01	4586	1772	1427
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453
EU-AUDI-A4-B7-WAGON-5D-02	4586	1772	1427
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	3718	1595	1390
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-01	3718	1595	1360
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-5D-01	3718	1595	1368
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	5651	1974	2524
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	5651	1974	2303
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	5201	1974	2529
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	5201	1974	2309
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	4834	1974	1974
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	4834	1974	2313
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	6403	2084	2624
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	6403	2084	2380
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	6403	2008	2624
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	6403	1974	2624
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	5680	1974	2590
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	5680	1974	2381
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	5680	1974	2606
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	5680	1974	2394
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	5230	1974	2594
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	5230	1974	2047
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	5230	1974	2611
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	5230	1974	2397
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	6403	2084	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465
EU-MAZDA-626-V-GF-SEDAN-01	4575	1710	1430
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-03	4765	1795	1440
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430
EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	4748	1901	1902
EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	5223	1901	1900
EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	4993	1901	1902
EU-OPEL-COMBO-C-FACELIFT-MPV-01	4322	1684	1801
EU-OPEL-COMBO-C-FACELIFT-VAN-01	4322	1684	1801
EU-OPEL-COMBO-C-MPV-5D-01	4332	1684	1801
EU-OPEL-COMBO-C-TOUR-MPV-01	4322	1684	1801
EU-OPEL-COMBO-C-VAN-01	4322	1684	1801
EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	4322	1684	1801
EU-OPEL-COMBO-TOUR-D-X12-MPV-L1H1-01	4390	1831	1845
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-PEUGEOT-407-COUPE-2D-01	4815	1868	1399
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468
EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	3695	1690	1500
EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	3695	1690	1500
EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	4582	1820	1400
EU-VOLVO-C70-II-FACELIFT-CONVERTIBLE-2D-01	4615	1836	1400
EU-VOLVO-C70-II-PREFL-CONVERTIBLE-2D-01	4582	1820	1457
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949
EU-VW-TRANSPORTER-T5-CHASSIS-DOUBLE-CAB-LWB-01	5292	1904	1949
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963
EU-VW-TRANSPORTER-T5-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-MPV-LWB-HIGHROOF-01	5290	1904	2460
EU-VW-TRANSPORTER-T5-MPV-LWB-LOWROOF-01	5290	1904	1959
EU-VW-TRANSPORTER-T5-MPV-LWB-MIDROOF-01	5290	1904	2160
EU-VW-TRANSPORTER-T5-MPV-SWB-LOWROOF-01	4890	1904	1959
EU-VW-TRANSPORTER-T5-MPV-SWB-MIDROOF-01	4890	1904	2160
EU-VW-TRANSPORTER-T5-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-SWB-MEDROOF-01	4890	1904	2170
EU-VW-TRANSPORTER-T5-VAN-LWB-HIGHROOF-01	5290	1904	2470
EU-VW-TRANSPORTER-T5-VAN-LWB-LOWROOF-01	5290	1904	1969
EU-VW-TRANSPORTER-T5-VAN-LWB-MEDROOF-01	5290	1904	2170
EU-VW-TRANSPORTER-T5-VAN-SWB-LOWROOF-01	4890	1904	1969
EU-VW-TRANSPORTER-T5-VAN-SWB-MEDROOF-01	4890	1904	2170

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Autobianchi	Bianchina	0.5	Coupe	Heckantrieb	Benzin	13	18	Jan 1960	Dec 1962	2024-03-01	28109
Autobianchi	Bianchina	0.5	Kombi	Heckantrieb	Benzin	16	22	Jan 1960	Dec 1969	2024-03-01	28110
Autobianchi	Primula berlina	1.2	Stufenheck	Frontantrieb	Benzin	43	59	Jan 1964	Dec 1967	2024-03-01	28111
Autobianchi	Primula berlina	1.2	Stufenheck	Frontantrieb	Benzin	48	65	Jan 1968	Dec 1970	2024-03-01	28112
Autobianchi	Primula	1.2	Coupe	Frontantrieb	Benzin	48	65	Jan 1964	Dec 1967	2024-03-01	28113
Autobianchi	Primula	1.4	Coupe	Frontantrieb	Benzin	55	75	Jan 1968	Dec 1970	2024-03-01	28114
Fiat	1100-1900	1400 A	Stufenheck	Heckantrieb	Benzin	37	50	Jan 1954	Dec 1955	2024-03-01	28115
Fiat	1100-1900	1400 B	Stufenheck	Heckantrieb	Benzin	43	58	Jan 1956	Dec 1958	2024-03-01	28116
Fiat	1100-1900	1900 A	Stufenheck	Heckantrieb	Benzin	51	70	Jan 1954	Dec 1959	2024-03-01	28117
Fiat	1100-1900	1900 B	Stufenheck	Heckantrieb	Benzin	59	80	Jan 1956	Dec 1958	2024-03-01	28118
Fiat	1900	1900 B	Coupe	Heckantrieb	Benzin	59	80	Jan 1956	Dec 1958	2024-03-01	28119
KIA	Pro cee'd	1.4 Cvvt	Schrägheck	Frontantrieb	Benzin	66	90	Jun 2010	Sep 2012	2024-03-01	28120
Subaru	Xv	1.6 I AWD	SUV	Allrad	Benzin	84	114	Mar 2012	Dec 2017	2025-06-01	28121
Subaru	Xv	2.0 I AWD	SUV	Allrad	Benzin	110	150	Mar 2012	Dec 2017	2025-06-01	28125
Innocenti	Regent	1.3	Schrägheck	Frontantrieb	Benzin	46	63	Jan 1974	Dec 1975	2024-03-01	28128
Innocenti	Regent	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1974	Dec 1975	2024-03-01	28129
Seat	Ibiza iv sc	1.2	Schrägheck	Frontantrieb	Benzin	51	70	Jul 2008	May 2015	2025-06-01	28130
Seat	Ibiza iv sc	1.4	Schrägheck	Frontantrieb	Benzin	63	85	Jul 2008	May 2015	2025-06-01	28131
Seat	Ibiza iv sc	1.4 TDI	Schrägheck	Frontantrieb	Diesel	59	80	Jul 2008	Jun 2010	2025-06-01	28132
Seat	Ibiza iv sc	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2008	Jun 2010	2025-06-01	28133
Lancia	Delta iii	1.4	Schrägheck	Frontantrieb	Benzin	88	120	Sep 2008	Aug 2014	2024-03-01	28134
Lancia	Delta iii	1.4	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2008	Aug 2014	2024-03-01	28135
Lancia	Delta iii	1.6 D Multijet	Schrägheck	Frontantrieb	Diesel	88	120	Sep 2008	Aug 2014	2024-03-01	28136
Lancia	Delta iii	1.9 D Multijet	Schrägheck	Frontantrieb	Diesel	140	190	Jan 2009	Aug 2014	2024-03-01	28137
Lancia	Delta iii	2.0 D Multijet	Schrägheck	Frontantrieb	Diesel	121	165	Sep 2008	Aug 2014	2024-03-01	28138
Lancia	Delta iii	1.8	Schrägheck	Frontantrieb	Benzin	147	200	Jan 2009	Aug 2014	2024-03-01	28139
Peugeot	407	2.0 HDI	Stufenheck	Frontantrieb	Diesel	103	140	Jun 2009	Dec 2010	2024-03-01	28140
Peugeot	407	2.0 HDI	Kombi	Frontantrieb	Diesel	103	140	Aug 2008	Dec 2010	2024-03-01	28141
Lancia	Appia berlina	1.1	Stufenheck	Heckantrieb	Benzin	35	48	Mar 1959	Dec 1961	2024-03-01	28142
Lancia	Appia	1.1	Kombi	Heckantrieb	Benzin	35	48	Mar 1959	Dec 1961	2024-03-01	28143
Volvo	C70 ii	2.0 D	Cabriolet	Frontantrieb	Diesel	100	136	Jan 2008	Oct 2009	2024-03-01	28144
Volvo	Xc70 ii	2.4 D / D4 AWD	Kombi	Allrad	Diesel	120	163	Aug 2007	Apr 2016	2024-03-01	28145
Opel	Combo	1.6 CNG 16V	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	71	97	Apr 2005	-	2024-03-01	28147
Opel	Combo tour	1.6 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	71	97	Apr 2005	Jan 2011	2024-03-01	28148
Suzuki	Swift iii	1.3 Ddis	Schrägheck	Frontantrieb	Diesel	55	75	Aug 2005	Dec 2011	2024-05-01	28149
Mazda	6	1.8 MZR	Kombi	Frontantrieb	Benzin	88	120	Feb 2008	Jul 2013	2024-03-01	28150
Mazda	6	2.0 MZR	Kombi	Frontantrieb	Benzin	108	147	Dec 2007	Jul 2013	2024-03-01	28151
Mazda	6	2.0 Mzr-cd	Kombi	Frontantrieb	Diesel	103	140	Dec 2007	Dec 2010	2024-03-01	28152
Mazda	6	2.5 MZR	Kombi	Frontantrieb	Benzin	125	170	Feb 2008	Jul 2013	2024-03-01	28153
Mercedes-benz	Vito	109 CDI 4X4	Bus	Allrad	Diesel	70	95	Sep 2007	Aug 2014	2024-03-01	28154
Mercedes-benz	Vito / mixto	111 CDI	Kasten	Heckantrieb	Diesel	85	116	Sep 2007	Aug 2014	2025-12-01	28155
Mercedes-benz	Vito / mixto	120 CDI	Kasten	Heckantrieb	Diesel	150	204	Mar 2006	Aug 2014	2025-12-01	28156
Mercedes-benz	Vito / mixto	111 CDI 4X4	Kasten	Allrad	Diesel	80	109	Sep 2007	Aug 2014	2025-12-01	28157
Mercedes-benz	Vito / mixto	115 CDI 4X4	Kasten	Allrad	Diesel	110	150	Jul 2006	Aug 2014	2025-12-01	28158
Mercedes-benz	Vito / mixto	126	Kasten	Heckantrieb	Benzin	190	258	Sep 2007	Aug 2014	2025-12-01	28159
Mercedes-benz	Vito	126	Bus	Heckantrieb	Benzin	190	258	Sep 2007	-	2024-03-01	28160
Mercedes-benz	Vito	111 CDI 4X4	Bus	Allrad	Diesel	80	109	Sep 2007	Aug 2014	2024-03-01	28161
Mercedes-benz	Vito	111 CDI	Bus	Heckantrieb	Diesel	85	116	Sep 2007	-	2024-03-01	28162
Mercedes-benz	Vito	115 CDI 4X4	Bus	Allrad	Diesel	110	150	Sep 2007	Aug 2014	2024-03-01	28163
Mercedes-benz	Vito	120 CDI	Bus	Heckantrieb	Diesel	150	204	Jul 2006	-	2024-03-01	28164
Audi	A4 b7	2.7 TDI	Stufenheck	Frontantrieb	Diesel	120	163	Nov 2005	Jun 2008	2024-03-01	28165
VW	Golf v variant	2.0 TDI	Kombi	Frontantrieb	Diesel	100	136	Jun 2007	Jul 2009	2024-03-01	28167
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	176	240	Nov 2007	May 2010	2024-03-01	28168
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	188	256	Feb 2007	Aug 2012	2024-03-01	28169
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	100	136	Nov 2006	Mar 2009	2024-03-01	28170
Seat	Altea	2.0 TDI 4X4	Großraumlimousine	Allrad	Diesel	103	140	Jun 2007	Nov 2010	2024-05-01	28171
Seat	Leon	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2007	Dec 2010	2024-03-01	28172
Seat	Leon	1.4 TSI	Schrägheck	Frontantrieb	Benzin	92	125	Nov 2007	Dec 2012	2024-03-01	28173
Seat	Leon	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Jun 2007	Dec 2012	2024-03-01	28174
Skoda	Fabia ii combi	1.2	Kombi	Frontantrieb	Benzin	44	60	Oct 2007	Nov 2014	2024-03-01	28175
Ford	Transit	3.2 Tdci	Bus	Heckantrieb	Diesel	147	200	Feb 2008	Aug 2014	2024-03-01	28176
Ford	Transit	3.2 Tdci RWD	Kasten	Heckantrieb	Diesel	147	200	Sep 2007	Aug 2014	2024-03-01	28177
Ford	Transit	3.2 Tdci RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	147	200	Sep 2007	Aug 2014	2024-03-01	28178
Dodge	Journey	2.0 CRD	Großraumlimousine	Frontantrieb	Diesel	103	140	Jun 2008	-	2024-03-01	28179
Dodge	Nitro	2.8 CRD 4WD	SUV	Allrad	Diesel	130	177	Jun 2007	Dec 2012	2024-03-01	28180
Dodge	Nitro	2.8 CRD	SUV	Heckantrieb	Diesel	130	177	Jun 2007	Dec 2012	2024-03-01	28181
Jeep	Wrangler iii	3.8	Geländewagen offen	Allrad	Benzin	146	199	Apr 2007	-	2024-03-01	28182
Jeep	Wrangler iii	2.8 CRD	Geländewagen offen	Allrad	Diesel	130	177	Apr 2007	-	2024-03-01	28183
Citroën	Saxo	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1996	Jun 2003	2024-03-01	28184
Citroën	Saxo	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Feb 2001	Apr 2004	2024-03-01	28185
Citroën	Saxo	1.6	Schrägheck	Frontantrieb	Benzin	88	120	Feb 1996	Apr 2004	2024-03-01	28186
Morgan	Aeromax	4.4	Coupe	Heckantrieb	Benzin	245	333	Mar 2007	Aug 2009	2024-03-01	28190
Lexus	Ls	460	Stufenheck	Heckantrieb	Benzin	255	347	Aug 2006	-	2024-03-01	28197
Citroën	C3 picasso	1.4 VTI 95	Großraumlimousine	Frontantrieb	Benzin	70	95	Dec 2008	Dec 2015	2024-08-01	28198
Citroën	C3 picasso	1.6 VTI 120	Großraumlimousine	Frontantrieb	Benzin	88	120	Feb 2009	Jul 2015	2024-08-01	28199
Citroën	C3 picasso	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	80	109	Feb 2009	Dec 2010	2024-08-01	28200
Peugeot	308 cc	1.6 16V	Cabriolet	Frontantrieb	Benzin	110	150	Jun 2009	Dec 2014	2024-03-01	28201
Peugeot	308 cc	2.0 HDI	Cabriolet	Frontantrieb	Diesel	103	140	Apr 2009	Dec 2012	2024-03-01	28202
Skoda	Octavia	1.8 TSI	Schrägheck	Frontantrieb	Benzin	118	160	Jun 2007	Apr 2013	2024-03-01	28203
Skoda	Octavia	1.8 TSI	Kombi	Frontantrieb	Benzin	118	160	Jun 2007	Apr 2013	2024-03-01	28204
Mercedes-benz	S-Klasse	CL 500 4-matic	Coupe	Allrad	Benzin	285	388	Feb 2008	Dec 2013	2024-03-01	28205
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	Feb 2004	May 2010	2024-03-01	28206
Skoda	Octavia	2.0 TDI 16V	Kombi	Frontantrieb	Diesel	100	136	Feb 2004	May 2010	2024-03-01	28207
Mercedes-benz	Glk-Klasse	280 4-matic	SUV	Allrad	Benzin	170	231	Jun 2008	Jun 2009	2024-03-01	28208
Mercedes-benz	Glk-Klasse	350 4-matic	SUV	Allrad	Benzin	200	272	Jun 2008	Apr 2011	2024-03-01	28209
Mercedes-benz	Glk-Klasse	320 CDI 4-matic	SUV	Allrad	Diesel	165	224	Jun 2008	Jun 2015	2024-03-01	28210
VW	Multivan t5	1.9 TDI	Bus	Frontantrieb	Diesel	62	84	Jan 2006	Nov 2009	2024-03-01	28211
VW	Multivan t5	2.5 TDI	Bus	Frontantrieb	Diesel	120	163	Nov 2003	Nov 2009	2024-03-01	28212
VW	Transporter t5	2.5 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	128	174	Apr 2004	Nov 2009	2024-03-01	28213
Opel	Insignia a	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Jul 2008	Mar 2017	2024-03-01	28214
Opel	Insignia a	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Jul 2008	Mar 2017	2024-03-01	28215
Opel	Insignia a	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	162	220	Jul 2008	Mar 2017	2024-03-01	28216
Opel	Insignia a	2.8 V6 Turbo 4X4	Schrägheck	Allrad	Benzin	191	260	Jul 2008	Mar 2017	2024-03-01	28217
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Jul 2008	Mar 2017	2024-03-01	28218
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	96	131	Jul 2008	Mar 2017	2024-03-01	28219
Opel	Insignia a	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	118	160	Jul 2008	Mar 2017	2024-03-01	28220
Opel	Insignia a	1.6	Stufenheck	Frontantrieb	Benzin	85	116	Jul 2008	Mar 2017	2024-03-01	28221
Opel	Insignia a	1.8	Stufenheck	Frontantrieb	Benzin	103	140	Jul 2008	Mar 2017	2024-03-01	28222
Opel	Insignia a	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	162	220	Jul 2008	Mar 2017	2024-03-01	28223
Opel	Insignia a	2.8 V6 Turbo 4X4	Stufenheck	Allrad	Benzin	191	260	Jul 2008	Mar 2017	2024-03-01	28224


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **58 个输入 Ktype**，生成 **70 条 READY 映射**；首次创建 **15 个尺寸组**，复用跨批次既有尺寸组 **21 个**。
* `Ibiza IV SC` 不能整段共用：改款前为 4072 mm，2012 改款后为 4043 mm，已按 `prefl/facelift` 拆分；`Delta III 844` 改款前后外廓三维一致，因此维持一个稳定尺寸组。([汽车数据网][1])
* `Mazda 6 II GH Wagon` 的不同版本存在 4765 mm 与 4785 mm 两种已确认外廓，不能因为同代同车身而强行合组。([汽车数据网][2])
* `GLK X204` 的 GLK 280/320 CDI 与 GLK 350 存在 3 mm 长度差，已建立两个尺寸组。([汽车数据网][3])
* `Insignia A` 输入结束日期虽延伸至 2017，但本批所列 115/140/220/260 hp 及早期 CDTI 动力实际对应 2013 改款前车身，不能机械拆出不存在的 facelift 映射。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：58
* READY 映射行：70
* PENDING 输入 Ktype：42
* 当前已引用并闭合尺寸组：36

  * 本轮首次创建：15
  * 跨批次缓存复用：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28120	28120	Hatchback	Pro Cee'd I	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-01	HIGH		READY
28121	28121	SUV	Subaru XV I	GP	5	EU-SUBARU-XV-I-GP-SUV-5D-01	HIGH		READY
28125	28125	SUV	Subaru XV I	GP	5	EU-SUBARU-XV-I-GP-SUV-5D-01	HIGH		READY
28130_prefl	28130	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2012改款，改款前外廓。	READY
28130_facelift	28130	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2012改款，改款后外廓。	READY
28131_prefl	28131	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2012改款，改款前外廓。	READY
28131_facelift	28131	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2012改款，改款后外廓。	READY
28132	28132	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH		READY
28133	28133	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH		READY
28134	28134	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28135	28135	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28136	28136	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28137	28137	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28138	28138	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28139	28139	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28140	28140	Sedan	407 I		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH		READY
28141	28141	Wagon	407 I		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH		READY
28145	28145	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
28147_van	28147	Van	Combo C Facelift			EU-OPEL-COMBO-C-FACELIFT-VAN-01	MEDIUM	输入BodyStyle同时包含货厢与乘用车身；本行为货厢车分支。	READY
28147_mpv	28147	MPV	Combo C Facelift			EU-OPEL-COMBO-C-FACELIFT-MPV-01	MEDIUM	输入BodyStyle同时包含货厢与乘用车身；本行为乘用车分支。	READY
28148	28148	MPV	Combo C Facelift		5	EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	HIGH		READY
28150	28150	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-01	HIGH		READY
28151	28151	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH		READY
28152	28152	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH		READY
28153	28153	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-01	HIGH		READY
28165	28165	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
28167	28167	Wagon	Golf V	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
28168	28168	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH		READY
28169_prefl	28169	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28169_facelift	28169	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28170	28170	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH		READY
28172_prefl	28172	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28172_facelift	28172	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28173_prefl	28173	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28173_facelift	28173	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28174_prefl	28174	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28174_facelift	28174	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28175_prefl	28175	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH	Ktype生产区间跨越2010改款，改款前外廓。	READY
28175_facelift	28175	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH	Ktype生产区间跨越2010改款，改款后外廓。	READY
28197	28197	Sedan	LS XF40	XF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH		READY
28198	28198	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28199	28199	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28200	28200	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28201	28201	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
28202	28202	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
28203_prefl	28203	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28203_facelift	28203	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28204_prefl	28204	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28204_facelift	28204	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28205	28205	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-2D-01	HIGH		READY
28206_prefl	28206	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28206_facelift	28206	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28207_prefl	28207	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28207_facelift	28207	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28208	28208	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	HIGH		READY
28209	28209	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-02	HIGH		READY
28210	28210	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	HIGH		READY
28211	28211	MPV	Multivan T5			EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
28212	28212	MPV	Multivan T5			EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
28214	28214	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28215	28215	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28216	28216	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28217	28217	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28218	28218	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28219	28219	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28220	28220	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28221	28221	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28222	28222	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28223	28223	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28224	28224	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-01	4250	1790	1450	Auto-Data.net	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
EU-SUBARU-XV-I-GP-SUV-5D-01	4450	1780	1615	Auto-Data.net	https://www.auto-data.net/en/subaru-xv-i-generation-3943
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428	Auto-Data.net	https://www.auto-data.net/en/seat-ibiza-iv-sc-generation-2905
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428	Auto-Data.net	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.2-12v-70hp-19332
EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	4520	1797	1499	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/lancia-delta-iii-844-generation-1175; https://www.auto-data.net/en/lancia-delta-iii-844-facelift-2011-generation-8690
EU-MAZDA-6-II-GH-WAGON-5D-01	4765	1795	1490	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-combi-gh-1.8-120hp-16787
EU-MAZDA-6-II-GH-WAGON-5D-02	4785	1795	1490	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-combi-gh-2.0-147hp-44565
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498	Auto-Data.net	https://www.auto-data.net/en/skoda-fabia-ii-combi-facelift-2010-1.2-mpi-60hp-20326
EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	4078	1766	1669	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-picasso-phase-i-2008-generation-3322
EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	4440	1817	1427	Auto-Data.net	https://www.auto-data.net/en/peugeot-308-cc-i-phase-i-2008-1.6-16v-thp-150hp-5363
EU-MERCEDES-BENZ-CL-C216-COUPE-2D-01	5065	1871	1418	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-cl-c216-cl-500-v8-388hp-4matic-7g-tronic-12708
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	4528	1840	1689	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-glk-x204-glk-280-v6-231hp-4matic-7g-tronic-12723
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-02	4525	1840	1689	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-glk-x204-glk-350-v6-272hp-4matic-7g-tronic-12725
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498	Auto-Data.net	https://www.auto-data.net/en/opel-insignia-hatchback-a-generation-492
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data.net	https://www.auto-data.net/en/opel-insignia-sedan-a-2.8-v6-turbo-260hp-4x4-1806
```

## 下一步优先处理

1. 集中闭合 `Mercedes-Benz Vito/Vito Mixto W639` 的 Compact、Long、Extra-long 以及 Bus/Van 分支，覆盖 Ktype 28154–28164。
2. 处理 `Ford Transit MK7` 的 Bus、Van、Chassis Cab 长度、车顶和后轮配置，以及 `Transporter T5` Fahrgestell 的高度冲突。
3. 核对 Autobianchi、Fiat 1400/1900、Innocenti Regent、Lancia Appia 等历史车型的正式车身边界及可追溯三维。
4. 解决剩余高歧义项：Volvo C70 缓存高度冲突、Swift III 门数、Altea 4X4/Freetrack 边界、Saxo 门数与 Phase、Wrangler JK 两门/四门、Dodge、Morgan。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/seat-ibiza-iv-sc-generation-2905 "Seat Ibiza IV SC | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mazda-6-ii-combi-gh-2.0-147hp-44565 "Mazda 6 II Combi (GH) 2.0 (147 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mercedes-benz-glk-x204-glk-280-v6-231hp-4matic-7g-tronic-12723 "Mercedes-Benz GLK (X204) GLK 280 V6 (231 Hp) 4MATIC 7G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/opel-insignia-hatchback-a-generation-492 "Opel Insignia Hatchback (A) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 **31 个 Ktype**，新增 **46 条 READY 映射**。Bianchina Panoramica 按第二、第三系列外廓拆分；Fiat 1400/1900 按 A、B 车身及 Gran Luce Coupe 分组。([automobile-catalog.com][1])
* Saxo Phase II 三门车身确认宽度为 **1620 mm**，与已有同系列 `1595 mm` 尺寸组冲突，因此未覆盖缓存，另建 `EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02`。([汽车数据网][2])
* 已闭合 Vito W639 非 4×4、非 126 的 Van/Bus 长度和车顶分支；4×4 与 126 版本继续保留待处理。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：89
* READY 映射行：116
* PENDING 输入 Ktype：11
* 已确认并引用尺寸组：68
* 本轮首次创建尺寸组：25
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28109	28109	Coupe	Bianchina 2a Serie		2	EU-AUTOBIANCHI-BIANCHINA-2A-COUPE-2D-01	HIGH		READY
28110_series2	28110	Wagon	Bianchina 2a Serie		3	EU-AUTOBIANCHI-BIANCHINA-2A-PANORAMICA-WAGON-3D-01	HIGH	1960至1962年第二系列Panoramica外廓。	READY
28110_series3	28110	Wagon	Bianchina 3a Serie		3	EU-AUTOBIANCHI-BIANCHINA-3A-PANORAMICA-WAGON-3D-01	HIGH	1962年后第三系列Panoramica外廓。	READY
28111	28111	Sedan	Primula Berlina			EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	MEDIUM	二门与四门berlina外廓一致；Ktype未区分门数。	READY
28112	28112	Sedan	Primula Berlina			EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	MEDIUM	二门与四门berlina外廓一致；Ktype未区分门数。	READY
28113	28113	Coupe	Primula Coupe		2	EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	HIGH		READY
28114	28114	Coupe	Primula Coupe S		2	EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	HIGH		READY
28115	28115	Sedan	1400-1900 A	101	4	EU-FIAT-1400-1900-A-SEDAN-4D-01	HIGH		READY
28116	28116	Sedan	1400 B	101	4	EU-FIAT-1400-B-SEDAN-4D-01	HIGH		READY
28117	28117	Sedan	1400-1900 A	101	4	EU-FIAT-1400-1900-A-SEDAN-4D-01	HIGH	1400 A与1900 A共用同一物理车身。	READY
28118	28118	Sedan	1900 B	101	4	EU-FIAT-1900-B-SEDAN-4D-01	HIGH		READY
28119	28119	Coupe	1900 B Gran Luce	101	2	EU-FIAT-1900-B-GRAN-LUCE-COUPE-2D-01	HIGH		READY
28128	28128	Sedan	Regent		4	EU-INNOCENTI-REGENT-SEDAN-4D-01	HIGH	输入Schrägheck对应四门fastback berlina车身。	READY
28129	28129	Sedan	Regent		4	EU-INNOCENTI-REGENT-SEDAN-4D-01	HIGH	输入Schrägheck对应四门fastback berlina车身。	READY
28142	28142	Sedan	Appia III Serie		4	EU-LANCIA-APPIA-III-SERIE-SEDAN-4D-01	HIGH		READY
28143	28143	Wagon	Appia III Serie Giardinetta		3	EU-LANCIA-APPIA-III-SERIE-GIARDINETTA-WAGON-3D-01	HIGH		READY
28144	28144	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH		READY
28149_3dr	28149	Hatchback	Swift III		3	EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门车身。	READY
28149_5dr	28149	Hatchback	Swift III		5	EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门车身。	READY
28155_compact	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact标准顶车身。	READY
28155_long_lowroof	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28155_long_highroof	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶车身。	READY
28155_extralong	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long标准顶车身。	READY
28156_compact	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	MEDIUM	Compact标准顶车身。	READY
28156_long	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	MEDIUM	Long标准顶车身。	READY
28156_extralong	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	MEDIUM	Extra-long标准顶车身。	READY
28162_compact	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact乘用车身。	READY
28162_long	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long乘用车身。	READY
28162_extralong	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long乘用车身。	READY
28164_compact	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	MEDIUM	Compact乘用车身。	READY
28164_long	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	MEDIUM	Long乘用车身。	READY
28164_extralong	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	MEDIUM	Extra-long乘用车身。	READY
28171	28171	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	四驱版本对应Freetrack增高宽体外廓。	READY
28179	28179	MPV	Journey I		5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH		READY
28180	28180	SUV	Nitro I	KA	5	EU-DODGE-NITRO-I-KA-SUV-5D-01	HIGH		READY
28181	28181	SUV	Nitro I	KA	5	EU-DODGE-NITRO-I-KA-SUV-5D-01	HIGH		READY
28182_2dr	28182	SUV	Wrangler III	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-01	HIGH	短轴双门开放式车身。	READY
28182_4dr	28182	SUV	Wrangler III Unlimited	JK	4	EU-JEEP-WRANGLER-III-JK-SUV-4D-01	HIGH	长轴四门Unlimited开放式车身。	READY
28183_2dr	28183	SUV	Wrangler III	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-02	HIGH	短轴双门柴油车身高度配置。	READY
28183_4dr	28183	SUV	Wrangler III Unlimited	JK	4	EU-JEEP-WRANGLER-III-JK-SUV-4D-01	HIGH	长轴四门Unlimited开放式车身。	READY
28184_3dr	28184	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	Phase I三门车身。	READY
28184_5dr	28184	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	HIGH	Phase I五门车身。	READY
28185	28185	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	HIGH		READY
28186_prefl	28186	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	1999改款前三门外廓。	READY
28186_facelift	28186	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	HIGH	1999改款后三门外廓。	READY
28190	28190	Coupe	Aeromax		2	EU-MORGAN-AEROMAX-COUPE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-BIANCHINA-2A-COUPE-2D-01	2985	1340	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/258935/autobianchi_bianchina.html
EU-AUTOBIANCHI-BIANCHINA-2A-PANORAMICA-WAGON-3D-01	3227	1350	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/258980/autobianchi_bianchina_panoramica.html
EU-AUTOBIANCHI-BIANCHINA-3A-PANORAMICA-WAGON-3D-01	3225	1340	1330	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/259040/autobianchi_bianchina_panoramica.html
EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	3785	1580	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/1767545/autobianchi_primula_65_c_4-porte.html
EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	3715	1580	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/259220/autobianchi_primula_coupe_s.html
EU-FIAT-1400-1900-A-SEDAN-4D-01	4305	1655	1550	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/707930/fiat_1400a.html
EU-FIAT-1400-B-SEDAN-4D-01	4325	1655	1575	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/707990/fiat_1400b.html
EU-FIAT-1900-B-SEDAN-4D-01	4325	1655	1590	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/708005/fiat_1900b.html
EU-FIAT-1900-B-GRAN-LUCE-COUPE-2D-01	4325	1655	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/708035/fiat_1900b_gran_luce.html
EU-INNOCENTI-REGENT-SEDAN-4D-01	3853	1613	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/1242125/innocenti_regent_1300_l.html
EU-LANCIA-APPIA-III-SERIE-SEDAN-4D-01	4010	1485	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/1374155/lancia_appia_sedan.html
EU-LANCIA-APPIA-III-SERIE-GIARDINETTA-WAGON-3D-01	4075	1540	1485	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/1374485/lancia_appia_giardinietta_viotti.html
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	4748	1901	1902	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	4993	1901	1902	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/149235/Mercedes-Benz-Vito-2004-Van-L2-109-CDI-.html
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	5223	1901	1900	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622	Auto-Data.net	https://www.auto-data.net/en/seat-altea-freetrack-generation-2914
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691700/dodge_journey_rt_2_0l_crd.html
EU-DODGE-NITRO-I-KA-SUV-5D-01	4584	1856	1773	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691430/dodge_nitro_sxt_2_8_crd.html
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sport-3.8i-v6-196hp-4x4-31684
EU-JEEP-WRANGLER-III-JK-SUV-4D-01	4751	1877	1834	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-unlimited-jk-3.8i-v6-12v-196hp-4x4-automatic-1178
EU-JEEP-WRANGLER-III-JK-SUV-2D-02	4223	1873	1816	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sport-2.8-crdi-174hp-4x4-31687
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-5-door-generation-8654
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	3718	1620	1360	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.6-98hp-15206
EU-MORGAN-AEROMAX-COUPE-2D-01	4120	1770	1200	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2039360/morgan_aeromax.html
```

## 下一步优先处理

1. 闭合 Ktype `28154`、`28157`、`28158`、`28159`、`28160`、`28161`、`28163` 的 Vito W639 4×4 与 126 Van/Bus 分支。
2. 将 `28176`、`28177`、`28178` 对应到已有 Transit MK7 的 Bus、Van、Chassis Cab 长度、车顶及后轮配置。
3. 解决 `28213` Transporter T5 4Motion Fahrgestell 的单排/双排驾驶室与高度边界。
4. 剩余 11 个 Ktype 闭合后，直接执行一次机械检查并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1960/258935/autobianchi_bianchina.html "https://www.automobile-catalog.com/car/1960/258935/autobianchi_bianchina.html"
[2]: https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.6-16v-118hp-44805 "https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.6-16v-118hp-44805"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮按明确的 W639 车身代码闭合 Ktype `28154`、`28157`、`28158`、`28161`、`28163`，新增 **12 条 READY 映射**，全部关联既有尺寸组。([JMS Fahrzeugteile][1])
* `28159`、`28160` 的 Vito 126 资料存在 1872–1875 mm 高度记录，与普通 W639 缓存的 1900–1902 mm 不一致，本轮不强行复用。([coches.net][2])
* 本轮未首次创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：94
* READY 映射行：128
* PENDING 输入 Ktype：6
* 已确认并引用尺寸组：68
* 剩余 PENDING：`28159`、`28160`、`28176`、`28177`、`28178`、`28213`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28154	28154	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28157_compact	28157	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28157_long	28157	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28157_extralong	28157	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28158_compact	28158	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28158_long	28158	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28158_extralong	28158	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28161_compact	28161	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28161_long	28161	MPV	Vito W639	639.703		EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long车身。	READY
28161_extralong	28161	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long车身。	READY
28163_compact	28163	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28163_extralong	28163	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `28159`、`28160` 的 Vito 126 Compact、Long、Extra-long 分支，并处理普通车身与改款后长度、高度差异。
2. 确认 `28176`、`28177`、`28178` 的 Transit 3.2 TDCi 实际覆盖范围，避免遗漏 Minibus、Jumbo、SRW/DRW、车顶及驾驶室分支。([Ford Service Content][3])
3. 解决 `28213` Transporter T5 4Motion Fahrgestell 的单排/双排驾驶室边界及 5290/5292 mm 记录差异。([storage.customized-solution.com][4])

推进信号：CONTINUE

[1]: https://www.jms-fahrzeugteile.de/Motor-Getriebetechnik/DTE-BoostrPro/MERCEDES-BENZ/VITO/VITO-Bus-W639-2003/DTE-BoostrPro-passend-fuer-MERCEDES-BENZ-VITO-Bus-W639-2003%3A%3A2171107.html?utm_source=chatgpt.com "DTE BoostrPro passend für MERCEDES-BENZ VITO Bus (W639) 2003-..."
[2]: https://www.coches.net/fichas_tecnicas/mercedes-benz/vito/industriales/4-puertas/126_vito_l_compacta_258cv_gasolina/23281/58074820080101/?utm_source=chatgpt.com "MERCEDES-BENZ VITO 126 Vito L Compacta 258 cv de 2008"
[3]: https://www.fordservicecontent.com/Ford_Content/catalog/owner_guides/ENUSA_CG3527_TRN_og_200802.pdf?utm_source=chatgpt.com "Feel the difference FordTransit Owner's handbook"
[4]: https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Transporter/Transporter_2003-2009/2008-09_ABR_T5_EN.pdf?utm_source=chatgpt.com "Body builder guidelines Transporter T5"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 `28159`、`28160`：Vito 126 的 Van 与 Bus 均按已确认的 W639 Compact、Long、Extra-long 车身代码关联现有尺寸组，未重复抓取尺寸。([Allegro][1])
* 闭合 `28213`：Transporter T5 Fahrgestell 按单排与双排驾驶室拆分，复用现有 5292 mm 长轴尺寸组。([storage.customized-solution.com][2])
* Transit 3.2 TDCi 的 Bus、Van、Chassis Ktype 仍覆盖多个长度、车顶及 SRW/DRW 组合，暂不创建猜测性派生行。([eBay][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* READY 映射行：136
* PENDING 输入 Ktype：3
* 已确认并引用尺寸组：68
* 剩余 PENDING：`28176`、`28177`、`28178`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28159_compact	28159	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28159_long	28159	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28159_extralong	28159	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28160_compact	28160	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact乘用车身。	READY
28160_long	28160	MPV	Vito W639	639.703		EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long乘用车身。	READY
28160_extralong	28160	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long乘用车身。	READY
28213_singlecab	28213	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	MEDIUM	长轴单排驾驶室。	READY
28213_doublecab	28213	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `28176` Transit Bus 的 SWB、LWB、Jumbo、座位数及 SRW/DRW 分支。
2. 闭合 `28177` Transit Van 的轴距、车顶和单后轮/双后轮组合。
3. 闭合 `28178` Transit Chassis 的单排/双排驾驶室及 SWB、MWB、LWB、EF 分支。
4. 三项完成后立即进行一次机械检查，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://allegro.cz/produkt/lizarte-01-56-2120-servorizeni-hrebenove-rizeni-c378b273-b83f-4d76-97e7-9b5be344c4ba?srsltid=AfmBOop3IfY_pyD9G1g2TUrChCt-CWhp6P5fxrvMTHBkn-YSm31_Ojyq&utm_source=chatgpt.com "VIKA 6394601200 - Převodka řízení"
[2]: https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Transporter/Transporter_2003-2009/2008-09_ABR_T5_EN.pdf?utm_source=chatgpt.com "Body builder guidelines Transporter T5"
[3]: https://www.ebay.com/itm/287272438390?utm_source=chatgpt.com "KILEN Federnpaket 622052 für FORD TRANSIT Bus TDCi 4x4 ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2801-2900_ktype_dimension_mapping_final.tsv
- all_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后 3 个 Transit Ktype 已闭合。Ford 官方资料确认了 3.2L 200PS 的 LWB、Jumbo Van 可用范围和专属加长前悬尺寸；People Movers 资料确认 17 座 Jumbo Bus 的不含后视镜宽度及中顶高度；Chassis Cab 资料确认 3.2L 对应的 MWB、LWB、EF 单排与双排车身边界。([xr793.com][1])
* 当前证据所得 3.2L 车身长度或宽度与已有同系列尺寸组不同，因此使用下一序号建立 11 个新尺寸组，没有改写历史尺寸事实。
* 已完成机械检查：表头固定、147 个 `id` 唯一、81 个尺寸组唯一、映射引用全部闭合、无孤立尺寸组、三维和来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：147
* PENDING：0
* DIMENSION_GROUP：81
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
28109	28109	Coupe	Bianchina 2a Serie		2	EU-AUTOBIANCHI-BIANCHINA-2A-COUPE-2D-01	HIGH		READY
28110_series2	28110	Wagon	Bianchina 2a Serie		3	EU-AUTOBIANCHI-BIANCHINA-2A-PANORAMICA-WAGON-3D-01	HIGH	1960至1962年第二系列Panoramica外廓。	READY
28110_series3	28110	Wagon	Bianchina 3a Serie		3	EU-AUTOBIANCHI-BIANCHINA-3A-PANORAMICA-WAGON-3D-01	HIGH	1962年后第三系列Panoramica外廓。	READY
28111	28111	Sedan	Primula Berlina			EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	MEDIUM	二门与四门berlina外廓一致；Ktype未区分门数。	READY
28112	28112	Sedan	Primula Berlina			EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	MEDIUM	二门与四门berlina外廓一致；Ktype未区分门数。	READY
28113	28113	Coupe	Primula Coupe		2	EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	HIGH		READY
28114	28114	Coupe	Primula Coupe S		2	EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	HIGH		READY
28115	28115	Sedan	1400-1900 A	101	4	EU-FIAT-1400-1900-A-SEDAN-4D-01	HIGH		READY
28116	28116	Sedan	1400 B	101	4	EU-FIAT-1400-B-SEDAN-4D-01	HIGH		READY
28117	28117	Sedan	1400-1900 A	101	4	EU-FIAT-1400-1900-A-SEDAN-4D-01	HIGH	1400 A与1900 A共用同一物理车身。	READY
28118	28118	Sedan	1900 B	101	4	EU-FIAT-1900-B-SEDAN-4D-01	HIGH		READY
28119	28119	Coupe	1900 B Gran Luce	101	2	EU-FIAT-1900-B-GRAN-LUCE-COUPE-2D-01	HIGH		READY
28120	28120	Hatchback	Pro Cee'd I	ED	3	EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-01	HIGH		READY
28121	28121	SUV	Subaru XV I	GP	5	EU-SUBARU-XV-I-GP-SUV-5D-01	HIGH		READY
28125	28125	SUV	Subaru XV I	GP	5	EU-SUBARU-XV-I-GP-SUV-5D-01	HIGH		READY
28128	28128	Sedan	Regent		4	EU-INNOCENTI-REGENT-SEDAN-4D-01	HIGH	输入Schrägheck对应四门fastback berlina车身。	READY
28129	28129	Sedan	Regent		4	EU-INNOCENTI-REGENT-SEDAN-4D-01	HIGH	输入Schrägheck对应四门fastback berlina车身。	READY
28130_prefl	28130	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2012改款，改款前外廓。	READY
28130_facelift	28130	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2012改款，改款后外廓。	READY
28131_prefl	28131	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2012改款，改款前外廓。	READY
28131_facelift	28131	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2012改款，改款后外廓。	READY
28132	28132	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH		READY
28133	28133	Hatchback	Ibiza IV SC	6J	3	EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	HIGH		READY
28134	28134	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28135	28135	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28136	28136	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28137	28137	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28138	28138	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28139	28139	Hatchback	Delta III	844	5	EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	HIGH		READY
28140	28140	Sedan	407 I		4	EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	HIGH		READY
28141	28141	Wagon	407 I		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	HIGH		READY
28142	28142	Sedan	Appia III Serie		4	EU-LANCIA-APPIA-III-SERIE-SEDAN-4D-01	HIGH		READY
28143	28143	Wagon	Appia III Serie Giardinetta		3	EU-LANCIA-APPIA-III-SERIE-GIARDINETTA-WAGON-3D-01	HIGH		READY
28144	28144	Convertible	C70 II		2	EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	HIGH		READY
28145	28145	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
28147_van	28147	Van	Combo C Facelift			EU-OPEL-COMBO-C-FACELIFT-VAN-01	MEDIUM	输入BodyStyle同时包含货厢与乘用车身；本行为货厢车分支。	READY
28147_mpv	28147	MPV	Combo C Facelift			EU-OPEL-COMBO-C-FACELIFT-MPV-01	MEDIUM	输入BodyStyle同时包含货厢与乘用车身；本行为乘用车分支。	READY
28148	28148	MPV	Combo C Facelift		5	EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	HIGH		READY
28149_3dr	28149	Hatchback	Swift III		3	EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	HIGH	同一Ktype覆盖三门车身。	READY
28149_5dr	28149	Hatchback	Swift III		5	EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	HIGH	同一Ktype覆盖五门车身。	READY
28150	28150	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-01	HIGH		READY
28151	28151	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH		READY
28152	28152	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH		READY
28153	28153	Wagon	Mazda6 II	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-01	HIGH		READY
28154	28154	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28155_compact	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact标准顶车身。	READY
28155_long_lowroof	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28155_long_highroof	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	HIGH	Long高顶车身。	READY
28155_extralong	28155	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long标准顶车身。	READY
28156_compact	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	MEDIUM	Compact标准顶车身。	READY
28156_long	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	MEDIUM	Long标准顶车身。	READY
28156_extralong	28156	Van	Vito W639			EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	MEDIUM	Extra-long标准顶车身。	READY
28157_compact	28157	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28157_long	28157	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28157_extralong	28157	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28158_compact	28158	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28158_long	28158	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28158_extralong	28158	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28159_compact	28159	Van	Vito W639	639.601		EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	HIGH	Compact车身。	READY
28159_long	28159	Van	Vito W639	639.603		EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	HIGH	Long标准顶车身。	READY
28159_extralong	28159	Van	Vito W639	639.605		EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	HIGH	Extra-long车身。	READY
28160_compact	28160	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact乘用车身。	READY
28160_long	28160	MPV	Vito W639	639.703		EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long乘用车身。	READY
28160_extralong	28160	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long乘用车身。	READY
28161_compact	28161	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28161_long	28161	MPV	Vito W639	639.703		EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long车身。	READY
28161_extralong	28161	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long车身。	READY
28162_compact	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact乘用车身。	READY
28162_long	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	HIGH	Long乘用车身。	READY
28162_extralong	28162	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long乘用车身。	READY
28163_compact	28163	MPV	Vito W639	639.701		EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	HIGH	Compact车身。	READY
28163_extralong	28163	MPV	Vito W639	639.705		EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	HIGH	Extra-long车身。	READY
28164_compact	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	MEDIUM	Compact乘用车身。	READY
28164_long	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	MEDIUM	Long乘用车身。	READY
28164_extralong	28164	MPV	Vito W639			EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	MEDIUM	Extra-long乘用车身。	READY
28165	28165	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
28167	28167	Wagon	Golf V	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
28168	28168	SUV	Touareg I	7L	5	EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	HIGH		READY
28169_prefl	28169	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28169_facelift	28169	Hatchback	A3 II	8P	3	EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28170	28170	MPV	Altea I	5P	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH		READY
28171	28171	MPV	Altea Freetrack I	5P	5	EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	HIGH	四驱版本对应Freetrack增高宽体外廓。	READY
28172_prefl	28172	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28172_facelift	28172	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28173_prefl	28173	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28173_facelift	28173	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28174_prefl	28174	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-PREFL-01	HIGH	Ktype生产区间跨越2009改款，改款前外廓。	READY
28174_facelift	28174	Hatchback	Leon II	1P	5	EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	HIGH	Ktype生产区间跨越2009改款，改款后外廓。	READY
28175_prefl	28175	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	HIGH	Ktype生产区间跨越2010改款，改款前外廓。	READY
28175_facelift	28175	Wagon	Fabia II	5J	5	EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	HIGH	Ktype生产区间跨越2010改款，改款后外廓。	READY
28176	28176	MPV	Transit MK7			EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-02	MEDIUM	Jumbo双后轮中顶Bus车身。	READY
28177_lwb_medroof	28177	Van	Transit MK7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-02	HIGH	LWB中顶车身。	READY
28177_lwb_highroof	28177	Van	Transit MK7			EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-02	HIGH	LWB高顶车身。	READY
28177_jumbo_srw_highroof	28177	Van	Transit MK7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-02	HIGH	Jumbo单后轮高顶车身。	READY
28177_jumbo_drw_highroof	28177	Van	Transit MK7			EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-02	HIGH	Jumbo双后轮高顶车身。	READY
28178_singlecab_mwb	28178	Pickup	Transit MK7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	HIGH	中轴单排驾驶室。	READY
28178_singlecab_lwb	28178	Pickup	Transit MK7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	HIGH	长轴单排驾驶室。	READY
28178_singlecab_ef	28178	Pickup	Transit MK7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	HIGH	加长车架单排驾驶室。	READY
28178_doublecab_mwb	28178	Pickup	Transit MK7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	HIGH	中轴双排驾驶室。	READY
28178_doublecab_lwb	28178	Pickup	Transit MK7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	HIGH	长轴双排驾驶室。	READY
28178_doublecab_ef	28178	Pickup	Transit MK7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	HIGH	加长车架双排驾驶室。	READY
28179	28179	MPV	Journey I		5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH		READY
28180	28180	SUV	Nitro I	KA	5	EU-DODGE-NITRO-I-KA-SUV-5D-01	HIGH		READY
28181	28181	SUV	Nitro I	KA	5	EU-DODGE-NITRO-I-KA-SUV-5D-01	HIGH		READY
28182_2dr	28182	SUV	Wrangler III	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-01	HIGH	短轴双门开放式车身。	READY
28182_4dr	28182	SUV	Wrangler III Unlimited	JK	4	EU-JEEP-WRANGLER-III-JK-SUV-4D-01	HIGH	长轴四门Unlimited开放式车身。	READY
28183_2dr	28183	SUV	Wrangler III	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-02	HIGH	短轴双门柴油车身高度配置。	READY
28183_4dr	28183	SUV	Wrangler III Unlimited	JK	4	EU-JEEP-WRANGLER-III-JK-SUV-4D-01	HIGH	长轴四门Unlimited开放式车身。	READY
28184_3dr	28184	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	Phase I三门车身。	READY
28184_5dr	28184	Hatchback	Saxo Phase I		5	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	HIGH	Phase I五门车身。	READY
28185	28185	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	HIGH		READY
28186_prefl	28186	Hatchback	Saxo Phase I		3	EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	HIGH	1999改款前三门外廓。	READY
28186_facelift	28186	Hatchback	Saxo Phase II		3	EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	HIGH	1999改款后三门外廓。	READY
28190	28190	Coupe	Aeromax		2	EU-MORGAN-AEROMAX-COUPE-2D-01	HIGH		READY
28197	28197	Sedan	LS XF40	XF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH		READY
28198	28198	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28199	28199	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28200	28200	MPV	C3 Picasso I		5	EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	HIGH		READY
28201	28201	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
28202	28202	Convertible	308 CC I		2	EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	HIGH		READY
28203_prefl	28203	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28203_facelift	28203	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28204_prefl	28204	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28204_facelift	28204	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28205	28205	Coupe	CL C216	C216	2	EU-MERCEDES-BENZ-CL-C216-COUPE-2D-01	HIGH		READY
28206_prefl	28206	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28206_facelift	28206	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28207_prefl	28207	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	Ktype生产区间跨越2008改款，改款前外廓。	READY
28207_facelift	28207	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	Ktype生产区间跨越2008改款，改款后外廓。	READY
28208	28208	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	HIGH		READY
28209	28209	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-02	HIGH		READY
28210	28210	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	HIGH		READY
28211	28211	MPV	Multivan T5			EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
28212	28212	MPV	Multivan T5			EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
28213_singlecab	28213	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	MEDIUM	长轴单排驾驶室。	READY
28213_doublecab	28213	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	MEDIUM	长轴双排驾驶室。	READY
28214	28214	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28215	28215	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28216	28216	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28217	28217	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28218	28218	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28219	28219	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28220	28220	Hatchback	Insignia A		5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28221	28221	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28222	28222	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28223	28223	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
28224	28224	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	HIGH	该动力版本仅对应2013改款前车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2801-2900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUTOBIANCHI-BIANCHINA-2A-COUPE-2D-01	2985	1340	1320	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/258935/autobianchi_bianchina.html
EU-AUTOBIANCHI-BIANCHINA-2A-PANORAMICA-WAGON-3D-01	3227	1350	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/258980/autobianchi_bianchina_panoramica.html
EU-AUTOBIANCHI-BIANCHINA-3A-PANORAMICA-WAGON-3D-01	3225	1340	1330	Automobile-Catalog	https://www.automobile-catalog.com/car/1962/259040/autobianchi_bianchina_panoramica.html
EU-AUTOBIANCHI-PRIMULA-BERLINA-SEDAN-01	3785	1580	1400	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/1767545/autobianchi_primula_65_c_4-porte.html
EU-AUTOBIANCHI-PRIMULA-COUPE-2D-01	3715	1580	1350	Automobile-Catalog	https://www.automobile-catalog.com/car/1968/259220/autobianchi_primula_coupe_s.html
EU-FIAT-1400-1900-A-SEDAN-4D-01	4305	1655	1550	Automobile-Catalog	https://www.automobile-catalog.com/car/1954/707930/fiat_1400a.html
EU-FIAT-1400-B-SEDAN-4D-01	4325	1655	1575	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/707990/fiat_1400b.html
EU-FIAT-1900-B-SEDAN-4D-01	4325	1655	1590	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/708005/fiat_1900b.html
EU-FIAT-1900-B-GRAN-LUCE-COUPE-2D-01	4325	1655	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/1956/708035/fiat_1900b_gran_luce.html
EU-KIA-PRO-CEED-I-ED-HATCHBACK-3D-01	4250	1790	1450	Auto-Data.net	https://www.auto-data.net/en/kia-pro-ceed-i-facelift-2011-1.4-16v-90hp-17079
EU-SUBARU-XV-I-GP-SUV-5D-01	4450	1780	1615	Auto-Data.net	https://www.auto-data.net/en/subaru-xv-i-generation-3943
EU-INNOCENTI-REGENT-SEDAN-4D-01	3853	1613	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/1242125/innocenti_regent_1300_l.html
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-PREFL-01	4072	1693	1428	Auto-Data.net	https://www.auto-data.net/en/seat-ibiza-iv-sc-generation-2905
EU-SEAT-IBIZA-IV-6J-HATCHBACK-3D-FACELIFT-01	4043	1693	1428	Auto-Data.net	https://www.auto-data.net/en/seat-ibiza-iv-sc-facelift-2012-1.2-12v-70hp-19332
EU-LANCIA-DELTA-III-844-HATCHBACK-5D-01	4520	1797	1499	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/lancia-delta-iii-844-generation-1175; https://www.auto-data.net/en/lancia-delta-iii-844-facelift-2011-generation-8690
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442	Auto-Data.net	https://www.auto-data.net/en/peugeot-407-phase-ii-2008-generation-11258
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460	Auto-Data.net	https://www.auto-data.net/en/peugeot-407-model-574
EU-LANCIA-APPIA-III-SERIE-SEDAN-4D-01	4010	1485	1405	Automobile-Catalog	https://www.automobile-catalog.com/car/1959/1374155/lancia_appia_sedan.html
EU-LANCIA-APPIA-III-SERIE-GIARDINETTA-WAGON-3D-01	4075	1540	1485	Automobile-Catalog	https://www.automobile-catalog.com/car/1960/1374485/lancia_appia_giardinietta_viotti.html
EU-VOLVO-C70-II-CONVERTIBLE-PREFL-01	4582	1820	1400	Auto-Data.net	https://www.auto-data.net/en/volvo-c70-coupe-cabrio-ii-2.4-d5-180hp-17206
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604	Auto-Data.net	https://www.auto-data.net/en/volvo-xc70-ii-2.4-d5-205hp-awd-geartronic-17158
EU-OPEL-COMBO-C-FACELIFT-VAN-01	4322	1684	1801	Auto-Data.net	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.6-cng-97hp-ecotec-43674
EU-OPEL-COMBO-C-FACELIFT-MPV-01	4322	1684	1801	Auto-Data.net	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.6-cng-97hp-ecotec-43674
EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	4322	1684	1801	Auto-Data.net	https://www.auto-data.net/en/opel-combo-tour-c-facelift-2003-1.6-cng-97hp-ecotec-43674
EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	3695	1690	1500	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/suzuki-swift-iii-1.3-ddis-75hp-16251; https://www.auto-data.net/en/suzuki-swift-iii-generation-1225
EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	3695	1690	1500	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/suzuki-swift-iii-1.3-ddis-75hp-16251; https://www.auto-data.net/en/suzuki-swift-iii-generation-1225
EU-MAZDA-6-II-GH-WAGON-5D-01	4765	1795	1490	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-combi-gh-1.8-120hp-16787
EU-MAZDA-6-II-GH-WAGON-5D-02	4785	1795	1490	Auto-Data.net	https://www.auto-data.net/en/mazda-6-ii-combi-gh-2.0-147hp-44565
EU-MERCEDES-BENZ-VITO-W639-MPV-COMPACT-01	4748	1901	1902	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-COMPACT-01	4748	1901	1902	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-LOWROOF-01	4993	1901	1902	Mercedes-Benz Vito Van/Crew Cab official specification sheet; UltimateSpecs	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf; https://www.ultimatespecs.com/car-specs/Mercedes-Benz/149235/Mercedes-Benz-Vito-2004-Van-L2-109-CDI-.html
EU-MERCEDES-BENZ-VITO-W639-VAN-LONG-HIGHROOF-01	4993	1901	2329	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-VAN-EXTRALONG-01	5223	1901	1900	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-MPV-LONG-01	4993	1901	1902	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-MERCEDES-BENZ-VITO-W639-MPV-EXTRALONG-01	5223	1901	1900	Mercedes-Benz Vito Van/Crew Cab official specification sheet	https://xr793.com/wp-content/uploads/2023/10/2008-Mercedes-Benz-Vito-Van-Crew-Cab-Spec-Sheet-AUS.pdf
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-170hp-dpf-26475
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-variant-generation-2910
EU-VW-TOUAREG-I-7L-SUV-FACELIFT-01	4754	1928	1726	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touareg-i-7l-facelift-2006-3.0-tdi-v6-240hp-tiptronic-51664
EU-AUDI-A3-II-HATCHBACK-3D-PREFL-01	4214	1765	1421	Auto-Data.net	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-170hp-27109
EU-AUDI-A3-II-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data.net	https://www.auto-data.net/en/audi-a3-8p-facelift-2008-2.0-tfsi-200hp-4197
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	Auto-Data.net	https://www.auto-data.net/en/seat-altea-5p-2.0-tdi-140hp-13583
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622	Auto-Data.net	https://www.auto-data.net/en/seat-altea-freetrack-generation-2914
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458	Auto-Data.net	https://www.auto-data.net/en/seat-leon-model-1459
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458	Auto-Data.net	https://www.auto-data.net/en/seat-leon-ii-1p-facelift-2009-generation-9017
EU-SKODA-FABIA-II-COMBI-PREFL-WAGON-5D-01	4239	1642	1498	Auto-Data.net	https://www.auto-data.net/en/skoda-fabia-ii-combi-generation-3090
EU-SKODA-FABIA-II-COMBI-FACELIFT-WAGON-5D-01	4247	1642	1498	Auto-Data.net	https://www.auto-data.net/en/skoda-fabia-ii-combi-facelift-2010-1.2-mpi-60hp-20326
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-02	6474	2084	2380	Ford People Movers 2009 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-People-Movers-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-02	5751	1974	2403	Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-02	5751	1974	2619	Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-02	6474	1974	2629	Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-02	6474	2084	2629	Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	5552	1974	2030	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	6002	1974	2031	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	6390	1974	2030	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	5552	1974	2030	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	6002	1974	2025	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	6390	1974	2025	Ford Transit Chassis Cabs 2008 official brochure; Ford Transit Chassis Cabs 2010 official brochure; Ford Transit 2009 official brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2010-Ford-Chassis-Cabs-UK.pdf; https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691700/dodge_journey_rt_2_0l_crd.html
EU-DODGE-NITRO-I-KA-SUV-5D-01	4584	1856	1773	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/691430/dodge_nitro_sxt_2_8_crd.html
EU-JEEP-WRANGLER-III-JK-SUV-2D-01	4223	1873	1800	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sport-3.8i-v6-196hp-4x4-31684
EU-JEEP-WRANGLER-III-JK-SUV-4D-01	4751	1877	1834	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-unlimited-jk-3.8i-v6-12v-196hp-4x4-automatic-1178
EU-JEEP-WRANGLER-III-JK-SUV-2D-02	4223	1873	1816	Auto-Data.net	https://www.auto-data.net/en/jeep-wrangler-iii-jk-sport-2.8-crdi-174hp-4x4-31687
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-3D-ELECTRIC-01	3718	1595	1390	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-3-door-12-kwh-27hp-46431
EU-CITROEN-SAXO-PHASE-I-HATCHBACK-5D-01	3718	1595	1390	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-phase-i-1996-5-door-generation-8654
EU-CITROEN-SAXO-PHASE-II-HATCHBACK-3D-02	3718	1620	1360	Auto-Data.net	https://www.auto-data.net/en/citroen-saxo-phase-ii-1999-3-door-1.6-98hp-15206
EU-MORGAN-AEROMAX-COUPE-2D-01	4120	1770	1200	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/2039360/morgan_aeromax.html
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465	Auto-Data.net	https://www.auto-data.net/en/lexus-ls-iv-460-v8-381hp-super-ect-5880
EU-CITROEN-C3-PICASSO-I-PHASE-I-MPV-5D-01	4078	1766	1669	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-picasso-phase-i-2008-generation-3322
EU-PEUGEOT-308-CC-I-PHASE-I-CONVERTIBLE-2D-01	4440	1817	1427	Auto-Data.net	https://www.auto-data.net/en/peugeot-308-cc-i-phase-i-2008-1.6-16v-thp-150hp-5363
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-generation-3096
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-facelift-2009-generation-3094
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-generation-3097
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-generation-3095
EU-MERCEDES-BENZ-CL-C216-COUPE-2D-01	5065	1871	1418	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-cl-c216-cl-500-v8-388hp-4matic-7g-tronic-12708
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-01	4528	1840	1689	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-glk-x204-glk-280-v6-231hp-4matic-7g-tronic-12723
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-02	4525	1840	1689	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-glk-x204-glk-350-v6-272hp-4matic-7g-tronic-12725
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Auto-Data.net	https://www.auto-data.net/en/volkswagen-multivan-t5-1.9-tdi-105hp-46997
EU-VW-TRANSPORTER-T5-CHASSIS-CAB-LWB-02	5292	1904	1949	Volkswagen Transporter T5 body builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Transporter/Transporter_2003-2009/2008-09_ABR_T5_EN.pdf
EU-VW-TRANSPORTER-T5-DOUBLE-CAB-LWB-01	5292	1904	1963	Volkswagen Transporter T5 body builder guidelines	https://storage.customized-solution.com/csp-public/content/Technische-Informationen/Transporter/Transporter_2003-2009/2008-09_ABR_T5_EN.pdf
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498	Auto-Data.net	https://www.auto-data.net/en/opel-insignia-hatchback-a-generation-492
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data.net	https://www.auto-data.net/en/opel-insignia-sedan-a-2.8-v6-turbo-260hp-4x4-1806
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2801-2900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2801-2900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2801-2900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3651 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1802 行）

