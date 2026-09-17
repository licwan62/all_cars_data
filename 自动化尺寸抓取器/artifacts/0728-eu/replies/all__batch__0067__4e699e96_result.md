# 任务：all 第 6601-6700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0067__4e699e96


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6601-6700 行

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
all 第 6601-6700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6601-6700_ktype_dimension_mapping_final.tsv
- all_6601-6700_dimension_groups_final.tsv
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
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
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
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-BMW-7-E23-SEDAN-01	4860	1800	1430
EU-BMW-7-E32-SEDAN-LWB-01	5025	1845	1400
EU-BMW-7-E32-SEDAN-SWB-01	4910	1845	1411
EU-BMW-7-E32-SEDAN-SWB-V12-01	4910	1845	1400
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-GLAS-GOGGOMOBIL-TS-COUPE-2D-01	3035	1370	1235
EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	2900	1280	1310
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385
EU-OPEL-ASCONA-C-SEDAN-01	4366	1668	1395
EU-OPEL-ASCONA-C-SEDAN-H1385-01	4366	1668	1385
EU-OPEL-ASCONA-C-SEDAN-H1395-01	4366	1668	1395
EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	3652	1542	1365
EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	3622	1532	1365
EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	3652	1542	1365
EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	3622	1532	1365
EU-OPEL-CORSA-A-SEDAN-2D-01	3955	1540	1360
EU-OPEL-CORSA-A-SEDAN-4D-01	3955	1540	1360
EU-TALBOT-HORIZON-HATCHBACK-01	3960	1680	1410
EU-TALBOT-MURENA-COUPE-01	4070	1752	1220
EU-TALBOT-SAMBA-CONVERTIBLE-01	3506	1528	1362
EU-TALBOT-SAMBA-HATCHBACK-01	3506	1528	1362
EU-TALBOT-TAGORA-SEDAN-01	4628	1810	1444
EU-VW-PASSAT-B7-VARIANT-WAGON-01	4771	1820	1508

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Glas	Goggomobil	T 300	Stufenheck	Heckantrieb	Benzin	11	15	Jun 1957	Apr 1967	2024-03-01	7031
Glas	Goggomobil	T 250	Stufenheck	Heckantrieb	Benzin	10	14	Jun 1957	Dec 1969	2024-03-01	7032
VW	Passat b7 variant	3.6 FSI 4motion	Kombi	Allrad	Benzin	220	300	Jan 2011	Dec 2014	2024-03-01	7033
Glas	Goggomobil	T 400	Stufenheck	Heckantrieb	Benzin	14	19	Jul 1957	May 1960	2024-03-01	7034
Glas	Isar	T 700	Stufenheck	Heckantrieb	Benzin	22	30	Aug 1958	Apr 1961	2024-03-01	7035
Glas	Isar	T 600	Stufenheck	Heckantrieb	Benzin	14	19	Aug 1958	Apr 1961	2024-03-01	7036
Glas	Isar	K 700	Kombi	Heckantrieb	Benzin	22	30	Sep 1959	Mar 1963	2024-03-01	7037
Glas	Isar	600 C-63	Stufenheck	Heckantrieb	Benzin	14	19	Apr 1960	Apr 1967	2024-03-01	7038
Talbot	1307-1510	Simca 1307 1.3	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1975	Jan 1980	2024-03-01	7039
Talbot	1307-1510	Simca 1307 1.3	Schrägheck	Frontantrieb	Benzin	50	68	Jul 1975	Jan 1980	2024-03-01	7040
Talbot	1307-1510	Simca 1307 1.3s	Schrägheck	Frontantrieb	Benzin	60	82	Jul 1975	Dec 1978	2024-03-01	7041
Think	City	Electric	Schrägheck	Frontantrieb	Elektro	28	38	Sep 2010	-	2024-03-01	7042
Nissan	Micra iv	1.2	Schrägheck	Frontantrieb	Benzin	59	80	May 2010	Sep 2015	2024-03-01	7043
Talbot	1307-1510	Simca 1510 1.4	Schrägheck	Frontantrieb	Benzin	51	69	Jan 1980	Apr 1984	2024-03-01	7044
Talbot	1307-1510	Simca 1510 1.4	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1980	Apr 1981	2024-03-01	7045
Talbot	1307-1510	Simca 1510 1.4	Schrägheck	Frontantrieb	Benzin	63	86	Jan 1980	Apr 1981	2024-03-01	7046
Talbot	1307-1510	Simca 1510 1.6	Schrägheck	Frontantrieb	Benzin	54	73	Nov 1980	Dec 1983	2024-03-01	7047
Opel	Ascona c cc	2.0 I CAT	Schrägheck	Frontantrieb	Benzin	85	116	Sep 1986	Aug 1988	2024-03-01	7048
BMW	3	M3 EVO I 2.3	Stufenheck	Heckantrieb	Benzin	162	220	Oct 1988	Oct 1990	2024-03-01	7049
Nissan	Micra iv	1.2 Dig-s	Schrägheck	Frontantrieb	Benzin	72	98	Mar 2011	Oct 2015	2024-05-01	7050
Opel	Kapitän	P 2.6	Stufenheck	Heckantrieb	Benzin	66	90	May 1958	Dec 1963	2024-03-01	7051
Opel	Olympia rekord	1.5	Stufenheck	Heckantrieb	Benzin	29	39	Mar 1953	Dec 1955	2024-03-01	7052
Opel	Olympia rekord	1.5	Stufenheck	Heckantrieb	Benzin	33	45	Jan 1956	Dec 1960	2024-03-01	7053
Opel	Olympia rekord	1.5	Stufenheck	Heckantrieb	Benzin	37	50	Jan 1960	Dec 1963	2024-03-01	7054
Opel	Rekord a	1500	Stufenheck	Heckantrieb	Benzin	40	54	Feb 1963	Dec 1965	2024-03-01	7055
Opel	Rekord a	1700	Stufenheck	Heckantrieb	Benzin	44	60	Feb 1963	Dec 1965	2024-03-01	7056
Opel	Rekord b	1.5	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1965	Aug 1966	2024-03-01	7057
BMW	M1	3.5	Coupe	Heckantrieb	Benzin	204	278	May 1979	May 1983	2024-03-01	7058
BMW	5	M5	Stufenheck	Heckantrieb	Benzin	210	286	Aug 1985	Dec 1987	2024-03-01	7059
Opel	Olympia rekord caravan	1.5	Kombi	Heckantrieb	Benzin	37	50	Jul 1957	Dec 1960	2024-03-01	7060
Opel	Ascona c cc	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1987	Aug 1988	2024-03-01	7061
Opel	Ascona c cc	1.6 I CAT	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1988	2024-03-01	7062
Opel	Ascona c	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1987	Aug 1988	2024-03-01	7063
Opel	Ascona c	1.6 I CAT	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1988	2024-03-01	7064
Opel	Ascona c	2.0 I CAT	Stufenheck	Frontantrieb	Benzin	85	116	Sep 1986	Aug 1988	2024-03-01	7065
BMW	5	M535 I	Stufenheck	Heckantrieb	Benzin	160	218	Apr 1980	May 1981	2024-03-01	7066
KIA	Picanto ii	1	Schrägheck	Frontantrieb	Benzin	51	69	May 2011	Mar 2017	2024-03-01	7067
KIA	Picanto ii	1.0 Bi-fuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	82	May 2011	Oct 2014	2024-03-01	7068
BMW	5	525 TD	Stufenheck	Heckantrieb	Diesel	85	115	Mar 1993	Aug 1995	2024-03-01	7069
BMW	7	735 I	Stufenheck	Heckantrieb	Benzin	141	192	Apr 1985	Aug 1986	2024-03-01	7070
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	120	163	Mar 2010	Nov 2013	2024-03-01	7071
KIA	Picanto ii	1.2	Schrägheck	Frontantrieb	Benzin	63	85	Sep 2011	Mar 2017	2024-03-01	7072
Talbot	1307-1510	Simca 1510 1.6	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1978	Jan 1980	2024-03-01	7073
Talbot	Tagora	2.6	Stufenheck	Heckantrieb	Benzin	122	166	Aug 1981	Oct 1983	2024-03-01	7074
Talbot	Tagora	2.3 Turbo Diesel	Stufenheck	Heckantrieb	Diesel	59	80	Aug 1981	Dec 1987	2024-03-01	7075
Volvo	S40 ii	D3	Stufenheck	Frontantrieb	Diesel	110	150	Oct 2010	Dec 2012	2024-03-01	7076
Talbot	Simca sim'4	0.8	Stufenheck	Heckantrieb	Benzin	24	33	Oct 1968	Dec 1972	2024-03-01	7077
Volvo	S40 ii	D4	Stufenheck	Frontantrieb	Diesel	130	177	Oct 2010	Dec 2012	2024-03-01	7078
Volvo	S40 ii	D2	Stufenheck	Frontantrieb	Diesel	84	115	Oct 2010	Dec 2012	2024-03-01	7079
Talbot	Simca 1000	0.9	Stufenheck	Heckantrieb	Benzin	29	39	Oct 1961	Sep 1975	2024-03-01	7080
Talbot	Simca 1000	0.9 Gl,gls	Stufenheck	Heckantrieb	Benzin	32	44	Oct 1961	May 1972	2024-03-01	7081
Talbot	Simca 1000	1.1 Spezial	Stufenheck	Heckantrieb	Benzin	39	53	Oct 1968	Sep 1975	2024-03-01	7083
Talbot	Simca 1000	0.9 Ls,gl	Stufenheck	Heckantrieb	Benzin	32	44	Oct 1970	Sep 1975	2024-03-01	7084
Talbot	Simca 1000	1.3 Spezial	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1974	Sep 1977	2024-03-01	7085
Talbot	Simca 1000	1005 Ls,gls	Stufenheck	Heckantrieb	Benzin	29	39	Oct 1976	Jul 1978	2024-03-01	7086
Talbot	Simca 1000	1006 Sr,gls	Stufenheck	Heckantrieb	Benzin	40	54	Oct 1976	Jul 1978	2024-03-01	7087
Talbot	Simca 1000	1.1 Rallye	Stufenheck	Heckantrieb	Benzin	39	53	Oct 1970	Sep 1972	2024-03-01	7088
Talbot	Simca 1000	1.3 Rallye 1	Stufenheck	Heckantrieb	Benzin	44	60	Oct 1972	Sep 1977	2024-03-01	7089
Talbot	Simca 1000	1.3 Rallye 2	Stufenheck	Heckantrieb	Benzin	60	82	Sep 1972	Sep 1976	2024-03-01	7090
Talbot	Simca 1000	1.3 Rallye 2	Stufenheck	Heckantrieb	Benzin	63	86	Oct 1976	Sep 1977	2024-03-01	7092
Talbot	Simca 1000	1.3 Rallye 3	Stufenheck	Heckantrieb	Benzin	76	103	Jan 1978	Dec 1978	2024-03-01	7093
Talbot	Samba	1.4	Schrägheck	Frontantrieb	Benzin	44	60	Jun 1983	Oct 1986	2024-03-01	7094
Talbot	Samba	1.4 Rallye	Schrägheck	Frontantrieb	Benzin	58	79	Jan 1983	Oct 1986	2024-03-01	7095
Talbot	Samba	1.2 Rallye	Schrägheck	Frontantrieb	Benzin	65	88	Jan 1983	Oct 1986	2024-03-01	7096
Talbot	Murena	2.1 S	Coupe	Heckantrieb	Benzin	103	140	Apr 1983	Jan 1985	2024-03-01	7097
Talbot	Murena	1.6	Coupe	Heckantrieb	Benzin	66	90	Aug 1981	Jan 1985	2024-03-01	7098
Opel	Corsa a cc	1.2 I	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1989	Mar 1993	2024-03-01	7100
Opel	Corsa a cc	1.2 N	Schrägheck	Frontantrieb	Benzin	38	52	Jan 1990	Mar 1993	2024-03-01	7101
Opel	Corsa a cc	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1985	Oct 1989	2024-03-01	7102
Opel	Corsa a cc	1.6 GSI CAT	Schrägheck	Frontantrieb	Benzin	74	101	Feb 1992	Mar 1993	2024-03-01	7103
Opel	Corsa a tr	1.5 D	Stufenheck	Frontantrieb	Diesel	37	50	Oct 1987	Nov 1992	2024-03-01	7104
Opel	Corsa a	1	Kasten/Schrägheck	Frontantrieb	Benzin	33	45	Feb 1986	Apr 1989	2024-03-01	7105
Talbot	Horizon	1.3	Schrägheck	Frontantrieb	Benzin	50	68	Feb 1978	Jan 1980	2024-03-01	7106
Talbot	Simca 1100	1.1 Ls,gls	Schrägheck	Frontantrieb	Benzin	41	56	Oct 1968	May 1972	2024-03-01	7107
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	82	112	Jan 1958	Dec 1961	2024-03-01	7108
Talbot	Simca 1100	1.1 Ls,gls	Schrägheck	Frontantrieb	Benzin	44	60	Oct 1968	May 1976	2024-03-01	7109
Talbot	Simca 1100	0.9 LS	Schrägheck	Frontantrieb	Benzin	35	48	Oct 1970	May 1972	2024-03-01	7110
Talbot	Simca 1100	1.2 Spezial	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1971	Sep 1977	2024-03-01	7111
Talbot	Simca 1100	1.3 Spezial TI	Schrägheck	Frontantrieb	Benzin	60	82	Oct 1972	Sep 1977	2024-03-01	7112
Talbot	Simca 1100	1.1 Ls,gls	Schrägheck	Frontantrieb	Benzin	40	54	Nov 1973	Sep 1977	2024-03-01	7113
Talbot	Simca 1100	0.9 LE	Schrägheck	Frontantrieb	Benzin	35	47	Oct 1976	Jan 1980	2024-03-01	7115
Renault	Latitude	2.0 DCI 150	Stufenheck	Frontantrieb	Diesel	110	150	Feb 2011	-	2024-03-01	7116
Talbot	Simca 1100	1.1 Le,lx,gls,es	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1976	Jan 1980	2024-03-01	7117
Talbot	Simca 1100	1.1 Le,lx,gls,es	Schrägheck	Frontantrieb	Benzin	43	58	Oct 1976	Jan 1980	2024-03-01	7118
Opel	Corsa a	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	33	45	Feb 1986	Apr 1989	2024-03-01	7119
Opel	Corsa a	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	40	54	Feb 1986	Apr 1989	2024-03-01	7120
Opel	Corsa a	1.3	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Feb 1986	Apr 1989	2024-03-01	7121
Opel	Corsa a	1.3	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Feb 1986	Apr 1989	2024-03-01	7122
Opel	Corsa a	1.5 D	Kasten/Schrägheck	Frontantrieb	Diesel	37	50	Jun 1987	Apr 1989	2024-03-01	7123
Talbot	Simca 1100 break/tourisme	1.1	Kombi	Frontantrieb	Benzin	41	56	Oct 1968	May 1972	2024-03-01	7124
Talbot	Simca 1100 break/tourisme	1.1	Kombi	Frontantrieb	Benzin	44	60	Oct 1970	May 1972	2024-03-01	7125
Talbot	Simca 1100 break/tourisme	1.3 Spezial	Kombi	Frontantrieb	Benzin	55	75	Jul 1974	Nov 1976	2024-03-01	7126
Talbot	Simca 1100 break/tourisme	1.1	Kombi	Frontantrieb	Benzin	44	60	Oct 1976	Sep 1979	2024-03-01	7127
Talbot	Simca 1100 break/tourisme	1.1	Kombi	Frontantrieb	Benzin	37	50	Oct 1976	Jan 1980	2024-03-01	7128
Talbot	Simca 1200 s	1.2	Coupe	Heckantrieb	Benzin	59	80	Oct 1968	Mar 1972	2024-03-01	7129
Talbot	Simca 1200 s	1.2	Coupe	Heckantrieb	Benzin	63	86	Oct 1970	Mar 1972	2024-03-01	7130
Talbot	Simca 1300	1.3	Stufenheck	Heckantrieb	Benzin	38	52	Aug 1963	Feb 1968	2024-03-01	7131
Talbot	Simca 1301	1.3 Ls,gl,gls	Stufenheck	Heckantrieb	Benzin	40	54	Aug 1966	Jul 1972	2024-03-01	7132
Talbot	Simca 1301	1.3 LS	Stufenheck	Heckantrieb	Benzin	44	60	Aug 1966	Jul 1972	2024-03-01	7133
Talbot	Simca 1301 tourisme	1.3	Kombi	Heckantrieb	Benzin	40	54	Aug 1966	Jul 1972	2024-03-01	7134


--- Round 1 / 首次发送 ---
## 更新点

* 复用跨批次缓存中的 11 个既有尺寸组，包括 Goggomobil T、Passat B7 Variant、Ascona C、BMW E12/E23/E34、Tagora、Samba、Murena 与 Horizon；本轮不重复输出这些尺寸组。
* Glas Isar T 600/T 700 的输入生产期跨越 1960 年外廓调整，按改款前后拆分；K 700 旅行车单独建组。([汽车目录][1])
* 新建 Simca 1307、Talbot 1510、THINK City、BMW E30 M3、BMW E28 M5、Kia Picanto II、Volvo S40 II 和 Renault Latitude 尺寸组。([汽车目录][2])
* Ktype 7049 的 `EVO I` 名称、220 hp 和输入日期存在版本命名偏差，但能够闭合到 E30 M3 两门物理外廓，暂以 `MEDIUM` 落盘。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：42
* READY 映射行：44
* 待处理输入 Ktype：58
* 当前已引用尺寸组：22
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7031	7031	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7032	7032	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7033	7033	Wagon	Passat B7		5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH		READY
7034	7034	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7035_prefl	7035	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-PREFL-01	HIGH	跨1960年8月外廓改款，拆分改款前。	READY
7035_facelift	7035	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	跨1960年8月外廓改款，拆分改款后。	READY
7036_prefl	7036	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-PREFL-01	HIGH	跨1960年8月外廓改款，拆分改款前。	READY
7036_facelift	7036	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	跨1960年8月外廓改款，拆分改款后。	READY
7037	7037	Wagon	Isar		3	EU-GLAS-ISAR-K-WAGON-3D-01	HIGH		READY
7039	7039	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7040	7040	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7041	7041	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7042	7042	Hatchback	THINK City		3	EU-THINK-CITY-HATCHBACK-3D-01	HIGH		READY
7044	7044	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7045	7045	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7046	7046	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7047	7047	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7048	7048	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7049	7049	Sedan	M3 E30	E30/2S	2	EU-BMW-M3-E30-SEDAN-2D-01	MEDIUM	输入EVO I/日期与220 hp官方命名存在偏差；按E30 M3两门外廓闭合。	READY
7059	7059	Sedan	M5 E28	E28S	4	EU-BMW-5-E28-M5-SEDAN-4D-01	HIGH		READY
7061	7061	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7062	7062	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7063	7063	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7064	7064	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7065	7065	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7066	7066	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
7067	7067	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7068	7068	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7069	7069	Sedan	5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
7070	7070	Sedan	7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
7072	7072	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7073	7073	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	MEDIUM	输入生产期跨1307/1510更名节点；按VariantName的1510五门外廓映射。	READY
7074	7074	Sedan	Tagora		4	EU-TALBOT-TAGORA-SEDAN-01	HIGH		READY
7075	7075	Sedan	Tagora		4	EU-TALBOT-TAGORA-SEDAN-01	HIGH		READY
7076	7076	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7078	7078	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7079	7079	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7094	7094	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7095	7095	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7096	7096	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7097	7097	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	HIGH		READY
7098	7098	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	HIGH		READY
7106	7106	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
7116	7116	Sedan	Latitude		4	EU-RENAULT-LATITUDE-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GLAS-ISAR-T-SEDAN-PREFL-01	3430	1470	1380	Automobile-Catalog 1958 Glas Isar T 700	https://www.automobile-catalog.com/car/1958/1017230/glas_isar_t_700.html
EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	3455	1470	1380	GLAS Automobilclub International;Automobile-Catalog 1960 Glas Isar T 700	https://www.glasclub.de/index.php/de/glas-fahrzeuge/26-glas-isar;https://www.automobile-catalog.com/car/1960/1017245/glas_isar_t_700.html
EU-GLAS-ISAR-K-WAGON-3D-01	3430	1470	1390	GLAS Automobilclub International;Automobile-Catalog 1960 Glas Isar K 700	https://www.glasclub.de/index.php/de/glas-fahrzeuge/26-glas-isar;https://www.automobile-catalog.com/car/1960/1017335/glas_isar_k_700.html
EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	4245	1680	1400	Automobile-Catalog 1975 Simca 1307 S	https://www.automobile-catalog.com/car/1975/28220/simca_1307_s.html
EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	4318	1680	1390	Automobile-Catalog 1980 Talbot 1510 1.3 LS	https://www.automobile-catalog.com/car/1980/3113795/talbot_1510_1_3_ls.html
EU-THINK-CITY-HATCHBACK-3D-01	3143	1658	1596	THINK City 2010 brochure	https://www.slideshare.net/slideshow/think-city-2010-englishweb/5299968
EU-BMW-M3-E30-SEDAN-2D-01	4345	1680	1370	Automobile-Catalog 1988 BMW M3 Evolution	https://www.automobile-catalog.com/car/1988/31205/bmw_m3_evolution.html
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400	BMW M E28 M5 heritage;Automobile-Catalog 1986 BMW M5	https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m5-e28.html;https://www.automobile-catalog.com/car/1986/52160/bmw_m5.html
EU-KIA-PICANTO-II-HATCHBACK-5D-01	3595	1595	1480	Kia Europe New Picanto press kit	https://press.kia.com/content/dam/kiapress/EU/download-files/Picanto-2011/New-Kia-Picanto.doc
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454	Volvo Cars Media UK S40 technical specifications	https://www.volvocars.com/uk/media/press-releases/464B5AA57533575D/
EU-RENAULT-LATITUDE-SEDAN-4D-01	4897	1832	1483	Auto-Data Renault Latitude	https://www.auto-data.net/en/renault-latitude-model-1932
```

## 下一步优先处理

1. 集中闭合 Opel Olympia Rekord、Rekord A/B、Kapitän及其 Caravan，统一区分年代改款和轿车/旅行车外廓。
2. 批量处理 Simca 1000、1100、1100 Break、1200 S、1300/1301 家族，避免按发动机重复建组。
3. 解决 Nissan Micra IV 高度资料冲突，以及 Mini Cooper S 的发动机功率、生产日期与 R53/R56 代际冲突。
4. 最后处理 Corsa A CC、TR 与 Kasten 的门数、改款和厢式车物理边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1958/1017230/glas_isar_t_700.html?utm_source=chatgpt.com "1958 Glas Isar T 700 Specs Review (22 kW / 30 PS / 30 hp) (since August 1958 for Europe North America )"
[2]: https://www.automobile-catalog.com/car/1975/28220/simca_1307_s.html?utm_source=chatgpt.com "1975 Simca 1307 S Specs Review (60.4 kW / 82 PS / 81 hp) (since September 1975 for Europe )"
[3]: https://www.automobile-catalog.com/car/1988/31205/bmw_m3_evolution.html?utm_source=chatgpt.com "1988 BMW M3 Evolution Specs Review (162 kW / 220 PS / 217 hp) (for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6601-6700_ktype_dimension_mapping_final.tsv
- all_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增闭合 26 个输入 Ktype，完成 Glas Isar C-63、Opel Kapitän P2、BMW M1、Simca 1000 系列和 Opel Corsa A 相关映射。
* Simca 1000 普通车身、1976 年后改款车身、1005 LS 短保险杠外廓和 Rallye 3 宽体分别建组；跨 1976 年外廓更新的 Rallye 1、Rallye 2 Ktype 已拆分。([汽车目录][1])
* Corsa A CC 按三门/五门及 1990 年 9 月前后改款拆分，并直接复用跨批次已有尺寸组；Kasten 直接复用改款前三门外壳尺寸组，本轮不重复输出其尺寸。([汽车目录][2])
* Kapitän P 2.6 的 90 PS 版本闭合到 P2；输入开始日期早于 P2 上市日期，因此映射置信度采用 `MEDIUM`。BMW M1 闭合到 E26 两门车身。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：68
* READY 映射行：81
* PENDING 输入 Ktype：32
* 当前已引用尺寸组：34
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7038	7038	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	C-63对应改款后两门外廓。	READY
7051	7051	Sedan	Kapitän P2	P2	4	EU-OPEL-KAPITAN-P2-SEDAN-4D-01	MEDIUM	2.6升90PS版本确定为P2；输入开始日期早于P2正式投产。	READY
7058	7058	Coupe	M1 E26	E26	2	EU-BMW-M1-E26-COUPE-2D-01	HIGH		READY
7077	7077	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH	Sim'4使用Simca 1000标准四门外壳。	READY
7080	7080	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7081	7081	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7083	7083	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7084	7084	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7086	7086	Sedan	Simca 1005		4	EU-TALBOT-SIMCA-1005-LS-SEDAN-4D-01	HIGH	1005 LS改款外廓。	READY
7087	7087	Sedan	Simca 1006		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	HIGH	1006 SR改款外廓。	READY
7088	7088	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH	1.1 Rallye未改变标准四门外廓。	READY
7089_prefl	7089	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	MEDIUM	生产期跨1976年外廓更新；改款前Rallye 1。	READY
7089_facelift	7089	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨1976年外廓更新；改款后Rallye 1。	READY
7090_prefl	7090	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	MEDIUM	生产期跨1976年外廓更新；改款前Rallye 2。	READY
7090_facelift	7090	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨1976年外廓更新；改款后Rallye 2。	READY
7092	7092	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	HIGH	改款后Rallye 2外廓。	READY
7093	7093	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-RALLYE3-SEDAN-4D-01	HIGH	Rallye 3宽体外廓。	READY
7100_3dr_prefl	7100	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理分支。	READY
7100_3dr_facelift	7100	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门1990年改款物理分支。	READY
7100_5dr_prefl	7100	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理分支。	READY
7100_5dr_facelift	7100	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门1990年改款物理分支。	READY
7101_3dr_prefl	7101	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理分支。	READY
7101_3dr_facelift	7101	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门1990年改款物理分支。	READY
7101_5dr_prefl	7101	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理分支。	READY
7101_5dr_facelift	7101	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门1990年改款物理分支。	READY
7102_3dr	7102	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理分支。	READY
7102_5dr	7102	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理分支。	READY
7103_3dr	7103	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理分支。	READY
7103_5dr	7103	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理分支。	READY
7104_2dr	7104	Sedan	Corsa A		2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	TR两门轿车物理分支。	READY
7104_4dr	7104	Sedan	Corsa A		4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	TR四门轿车物理分支。	READY
7105	7105	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7119	7119	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7120	7120	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7121	7121	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7122	7122	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7123	7123	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-KAPITAN-P2-SEDAN-4D-01	4831	1812	1456	Automobile-Catalog 1959 Opel Kapitan P2 2.6	https://www.automobile-catalog.com/car/1959/2410415/opel_kapitan.html
EU-BMW-M1-E26-COUPE-2D-01	4360	1824	1140	Auto-Data BMW M1 E26 3.5	https://www.auto-data.net/en/bmw-m1-e26-3.5-277hp-44012
EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	3797	1485	1390	Automobile-Catalog 1970 Simca 1000 GLS	https://www.automobile-catalog.com/car/1970/3107000/simca_1000_gls.html
EU-TALBOT-SIMCA-1005-LS-SEDAN-4D-01	3808	1485	1395	Automobile-Catalog 1977 Simca 1005 LS	https://www.automobile-catalog.com/car/1977/39305/simca_1005_ls.html
EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	3811	1485	1395	Automobile-Catalog 1976 Simca 1006 SR	https://www.automobile-catalog.com/car/1976/3107390/simca_1006_sr.html
EU-TALBOT-SIMCA-1000-RALLYE3-SEDAN-4D-01	3850	1560	1390	Automobile-Catalog 1978 Simca Rallye 3	https://www.automobile-catalog.com/car/1978/39980/simca_rallye_3.html
```

## 下一步优先处理

1. 闭合 Opel Olympia Rekord、Rekord P1/P2、Rekord A/B 和 Caravan，重点拆分跨代、门数及轿车/旅行车外廓。
2. 批量闭合 Simca 1100 Hatchback、1100 Break、1200 S、1300/1301 轿车与旅行车。
3. 处理 Nissan Micra IV、Mini Cooper S 和 Alfa Romeo 2000 Spider 的代际或版本边界。
4. 最后解决 Ktype 7085 跨多个 Simca 1000 后期前脸阶段的尺寸边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1970/3107000/simca_1000_gls.html?utm_source=chatgpt.com "Detailed specs review of 1970 Simca 1000 GLS model for Europe"
[2]: https://www.automobile-catalog.com/car/1990/2457875/opel_corsa_gl_1_2.html?utm_source=chatgpt.com "1990 Opel Corsa GL 1.2 Specs Review (38 kW / 52 PS / 51 hp) (since September 1990 for Europe export)"
[3]: https://www.automobile-catalog.com/car/1959/2410415/opel_kapitan.html?utm_source=chatgpt.com "1959 Opel Kapitan Specs Review (66 kW / 90 PS / 89 hp) (since August 1959 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6601-6700_ktype_dimension_mapping_final.tsv
- all_6601-6700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 32 个输入 Ktype 已完成闭合。
* 当前批次 100 个输入 Ktype 全部覆盖，共生成 131 条 READY 映射。
* 最终引用 57 个尺寸组；既有尺寸组按缓存复用，新建尺寸组仅保留首次确认的三维与来源。
* 已完成机械检查：表头列数正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、无孤立尺寸组、尺寸及来源均非空。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：131
* PENDING：0
* DIMENSION_GROUP：57
* 数据阶段及机械收尾均已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7031	7031	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7032	7032	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7033	7033	Wagon	Passat B7		5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH		READY
7034	7034	Sedan	Goggomobil T		2	EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	HIGH		READY
7035_prefl	7035	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-PREFL-01	HIGH	跨1960年8月外廓改款，拆分改款前。	READY
7035_facelift	7035	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	跨1960年8月外廓改款，拆分改款后。	READY
7036_prefl	7036	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-PREFL-01	HIGH	跨1960年8月外廓改款，拆分改款前。	READY
7036_facelift	7036	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	跨1960年8月外廓改款，拆分改款后。	READY
7037	7037	Wagon	Isar		3	EU-GLAS-ISAR-K-WAGON-3D-01	HIGH		READY
7038	7038	Sedan	Isar		2	EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	HIGH	C-63对应改款后两门外廓。	READY
7039	7039	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7040	7040	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7041	7041	Hatchback	Simca 1307		5	EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	HIGH		READY
7042	7042	Hatchback	THINK City		3	EU-THINK-CITY-HATCHBACK-3D-01	HIGH		READY
7043_prefl	7043	Hatchback	Micra IV	K13	5	EU-NISSAN-MICRA-K13-HATCHBACK-5D-PREFL-01	HIGH	生产期跨2013年外廓改款，拆分改款前。	READY
7043_facelift	7043	Hatchback	Micra IV	K13	5	EU-NISSAN-MICRA-K13-HATCHBACK-5D-FACELIFT-01	HIGH	生产期跨2013年外廓改款，拆分改款后。	READY
7044	7044	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7045	7045	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7046	7046	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7047	7047	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	HIGH		READY
7048	7048	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7049	7049	Sedan	M3 E30	E30/2S	2	EU-BMW-M3-E30-SEDAN-2D-01	MEDIUM	输入EVO I/日期与220 hp官方命名存在偏差；按E30 M3两门外廓闭合。	READY
7050_prefl	7050	Hatchback	Micra IV	K13	5	EU-NISSAN-MICRA-K13-HATCHBACK-5D-PREFL-01	HIGH	生产期跨2013年外廓改款，拆分改款前。	READY
7050_facelift	7050	Hatchback	Micra IV	K13	5	EU-NISSAN-MICRA-K13-HATCHBACK-5D-FACELIFT-01	HIGH	生产期跨2013年外廓改款，拆分改款后。	READY
7051	7051	Sedan	Kapitän P2	P2	4	EU-OPEL-KAPITAN-P2-SEDAN-4D-01	MEDIUM	2.6升90PS版本确定为P2；输入开始日期早于P2正式投产。	READY
7052	7052	Sedan	Olympia Rekord		2	EU-OPEL-OLYMPIA-REKORD-SEDAN-2D-01	HIGH		READY
7053_2dr	7053	Sedan	Rekord P1	P1	2	EU-OPEL-REKORD-P1-SEDAN-2D-01	MEDIUM	输入日期范围宽；按45PS P1两门分支。	READY
7053_4dr	7053	Sedan	Rekord P1	P1	4	EU-OPEL-REKORD-P1-SEDAN-4D-01	MEDIUM	输入日期范围宽；按45PS P1四门分支。	READY
7054_2dr	7054	Sedan	Rekord P2	P2	2	EU-OPEL-REKORD-P2-SEDAN-2D-01	MEDIUM	50PS版本覆盖P2两门分支。	READY
7054_4dr	7054	Sedan	Rekord P2	P2	4	EU-OPEL-REKORD-P2-SEDAN-4D-01	MEDIUM	50PS版本覆盖P2四门分支。	READY
7055_2dr	7055	Sedan	Rekord A	A	2	EU-OPEL-REKORD-A-SEDAN-2D-01	MEDIUM	两门轿车物理分支。	READY
7055_4dr	7055	Sedan	Rekord A	A	4	EU-OPEL-REKORD-A-SEDAN-4D-01	MEDIUM	四门轿车物理分支。	READY
7056_2dr	7056	Sedan	Rekord A	A	2	EU-OPEL-REKORD-A-SEDAN-2D-01	MEDIUM	两门轿车物理分支。	READY
7056_4dr	7056	Sedan	Rekord A	A	4	EU-OPEL-REKORD-A-SEDAN-4D-01	MEDIUM	四门轿车物理分支。	READY
7057_2dr	7057	Sedan	Rekord B	B	2	EU-OPEL-REKORD-B-SEDAN-2D-01	MEDIUM	两门轿车物理分支。	READY
7057_4dr	7057	Sedan	Rekord B	B	4	EU-OPEL-REKORD-B-SEDAN-4D-01	MEDIUM	四门轿车物理分支。	READY
7058	7058	Coupe	M1 E26	E26	2	EU-BMW-M1-E26-COUPE-2D-01	HIGH		READY
7059	7059	Sedan	M5 E28	E28S	4	EU-BMW-5-E28-M5-SEDAN-4D-01	HIGH		READY
7060_p1	7060	Wagon	Rekord P1	P1	3	EU-OPEL-REKORD-P1-CARAVAN-3D-01	MEDIUM	生产期跨P1/P2；P1 Caravan分支。	READY
7060_p2	7060	Wagon	Rekord P2	P2	3	EU-OPEL-REKORD-P2-CARAVAN-3D-01	MEDIUM	生产期跨P1/P2；P2 Caravan分支。	READY
7061	7061	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7062	7062	Hatchback	Ascona C		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
7063	7063	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7064	7064	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7065	7065	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
7066	7066	Sedan	5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
7067	7067	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7068	7068	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7069	7069	Sedan	5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
7070	7070	Sedan	7 Series E23	E23	4	EU-BMW-7-E23-SEDAN-01	HIGH		READY
7071	7071	Hatchback	Mini R53	R53	3	EU-MINI-MINI-R53-HATCHBACK-3D-01	MEDIUM	120kW/163PS对应R53；输入生产日期与版本年代不一致。	READY
7072	7072	Hatchback	Picanto II	TA	5	EU-KIA-PICANTO-II-HATCHBACK-5D-01	HIGH		READY
7073	7073	Hatchback	Talbot 1510		5	EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	MEDIUM	输入生产期跨1307/1510更名节点；按VariantName的1510五门外廓映射。	READY
7074	7074	Sedan	Tagora		4	EU-TALBOT-TAGORA-SEDAN-01	HIGH		READY
7075	7075	Sedan	Tagora		4	EU-TALBOT-TAGORA-SEDAN-01	HIGH		READY
7076	7076	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7077	7077	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH	Sim'4使用Simca 1000标准四门外壳。	READY
7078	7078	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7079	7079	Sedan	S40 II		4	EU-VOLVO-S40-II-SEDAN-4D-01	HIGH		READY
7080	7080	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7081	7081	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7083	7083	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7084	7084	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH		READY
7085_prefl	7085	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	MEDIUM	生产期跨1976年外廓更新；改款前分支。	READY
7085_facelift	7085	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨1976年外廓更新；改款后分支。	READY
7086	7086	Sedan	Simca 1005		4	EU-TALBOT-SIMCA-1005-LS-SEDAN-4D-01	HIGH	1005 LS改款外廓。	READY
7087	7087	Sedan	Simca 1006		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	HIGH	1006 SR改款外廓。	READY
7088	7088	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	HIGH	1.1 Rallye未改变标准四门外廓。	READY
7089_prefl	7089	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	MEDIUM	生产期跨1976年外廓更新；改款前Rallye 1。	READY
7089_facelift	7089	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨1976年外廓更新；改款后Rallye 1。	READY
7090_prefl	7090	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	MEDIUM	生产期跨1976年外廓更新；改款前Rallye 2。	READY
7090_facelift	7090	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	MEDIUM	生产期跨1976年外廓更新；改款后Rallye 2。	READY
7092	7092	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	HIGH	改款后Rallye 2外廓。	READY
7093	7093	Sedan	Simca 1000		4	EU-TALBOT-SIMCA-1000-RALLYE3-SEDAN-4D-01	HIGH	Rallye 3宽体外廓。	READY
7094	7094	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7095	7095	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7096	7096	Hatchback	Samba		3	EU-TALBOT-SAMBA-HATCHBACK-01	HIGH		READY
7097	7097	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	HIGH		READY
7098	7098	Coupe	Murena		3	EU-TALBOT-MURENA-COUPE-01	HIGH		READY
7100_3dr_prefl	7100	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理分支。	READY
7100_3dr_facelift	7100	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门1990年改款物理分支。	READY
7100_5dr_prefl	7100	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理分支。	READY
7100_5dr_facelift	7100	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门1990年改款物理分支。	READY
7101_3dr_prefl	7101	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前物理分支。	READY
7101_3dr_facelift	7101	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门1990年改款物理分支。	READY
7101_5dr_prefl	7101	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前物理分支。	READY
7101_5dr_facelift	7101	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门1990年改款物理分支。	READY
7102_3dr	7102	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理分支。	READY
7102_5dr	7102	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理分支。	READY
7103_3dr	7103	Hatchback	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理分支。	READY
7103_5dr	7103	Hatchback	Corsa A		5	EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理分支。	READY
7104_2dr	7104	Sedan	Corsa A		2	EU-OPEL-CORSA-A-SEDAN-2D-01	MEDIUM	TR两门轿车物理分支。	READY
7104_4dr	7104	Sedan	Corsa A		4	EU-OPEL-CORSA-A-SEDAN-4D-01	MEDIUM	TR四门轿车物理分支。	READY
7105	7105	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7106	7106	Hatchback	Horizon		5	EU-TALBOT-HORIZON-HATCHBACK-01	HIGH		READY
7107_3dr	7107	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7107_5dr	7107	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7108	7108	Convertible	Alfa Romeo 2000 Spider	102.04	2	EU-ALFA-ROMEO-2000-TIPO102-CONVERTIBLE-2D-01	HIGH		READY
7109_3dr	7109	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7109_5dr	7109	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7110_3dr	7110	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7110_5dr	7110	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7111_3dr	7111	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7111_5dr	7111	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7112_3dr	7112	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	TI三门物理分支。	READY
7112_5dr	7112	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	TI五门物理分支。	READY
7113_3dr	7113	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7113_5dr	7113	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7115_3dr	7115	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7115_5dr	7115	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7116	7116	Sedan	Latitude		4	EU-RENAULT-LATITUDE-SEDAN-4D-01	HIGH		READY
7117_3dr	7117	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7117_5dr	7117	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7118_3dr	7118	Hatchback	Simca 1100		3	EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
7118_5dr	7118	Hatchback	Simca 1100		5	EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
7119	7119	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7120	7120	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7121	7121	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7122	7122	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7123	7123	Van	Corsa A		3	EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	HIGH	三门厢式版沿用改款前三门外壳。	READY
7124	7124	Wagon	Simca 1100 Break		5	EU-TALBOT-SIMCA-1100-BREAK-WAGON-PREFL-01	HIGH		READY
7125	7125	Wagon	Simca 1100 Break		5	EU-TALBOT-SIMCA-1100-BREAK-WAGON-PREFL-01	HIGH		READY
7126	7126	Wagon	Simca 1100 Break		5	EU-TALBOT-SIMCA-1100-BREAK-WAGON-FACELIFT-01	HIGH		READY
7127	7127	Wagon	Simca 1100 Break		5	EU-TALBOT-SIMCA-1100-BREAK-WAGON-FACELIFT-01	HIGH		READY
7128	7128	Wagon	Simca 1100 Break		5	EU-TALBOT-SIMCA-1100-BREAK-WAGON-FACELIFT-01	HIGH		READY
7129	7129	Coupe	Simca 1200 S		2	EU-TALBOT-SIMCA-1200-S-COUPE-2D-01	HIGH		READY
7130	7130	Coupe	Simca 1200 S		2	EU-TALBOT-SIMCA-1200-S-COUPE-2D-01	HIGH		READY
7131	7131	Sedan	Simca 1300		4	EU-TALBOT-SIMCA-1300-SEDAN-4D-01	HIGH		READY
7132	7132	Sedan	Simca 1301		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7133	7133	Sedan	Simca 1301		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7134	7134	Wagon	Simca 1301		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6601-6700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GLAS-GOGGOMOBIL-T-SEDAN-2D-01	2900	1280	1310	Automobile-Catalog 1958 Goggomobil T 250	https://www.automobile-catalog.com/car/1958/1017065/goggomobil_t_250.html
EU-VW-PASSAT-B7-VARIANT-WAGON-01	4771	1820	1508	Auto-Data Volkswagen Passat Variant B7	https://www.auto-data.net/en/volkswagen-passat-variant-b7-1.6-tdi-105hp-bluemotion-44157
EU-GLAS-ISAR-T-SEDAN-PREFL-01	3430	1470	1380	Automobile-Catalog 1958 Glas Isar T 700	https://www.automobile-catalog.com/car/1958/1017230/glas_isar_t_700.html
EU-GLAS-ISAR-T-SEDAN-FACELIFT-01	3455	1470	1380	GLAS Automobilclub International;Automobile-Catalog 1960 Glas Isar T 700	https://www.glasclub.de/index.php/de/glas-fahrzeuge/26-glas-isar;https://www.automobile-catalog.com/car/1960/1017245/glas_isar_t_700.html
EU-GLAS-ISAR-K-WAGON-3D-01	3430	1470	1390	GLAS Automobilclub International;Automobile-Catalog 1960 Glas Isar K 700	https://www.glasclub.de/index.php/de/glas-fahrzeuge/26-glas-isar;https://www.automobile-catalog.com/car/1960/1017335/glas_isar_k_700.html
EU-TALBOT-SIMCA-1307-HATCHBACK-5D-01	4245	1680	1400	Automobile-Catalog 1975 Simca 1307 S	https://www.automobile-catalog.com/car/1975/28220/simca_1307_s.html
EU-THINK-CITY-HATCHBACK-3D-01	3143	1658	1596	THINK City 2010 brochure	https://www.slideshare.net/slideshow/think-city-2010-englishweb/5299968
EU-NISSAN-MICRA-K13-HATCHBACK-5D-PREFL-01	3780	1665	1515	Nissan Micra 2014 sales brochure;ADAC Nissan Micra 1.2 DIG-S	https://www.onlymanuals.com/nissan/micra/nissan_micra_sales_brochure_2014_2014_2;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/nissan/micra/k13/229194/
EU-NISSAN-MICRA-K13-HATCHBACK-5D-FACELIFT-01	3825	1665	1520	Automobile-Catalog 2014 Nissan Micra 1.2 DIG-S	https://www.automobile-catalog.com/car/2014/2200205/nissan_micra_1_2_dig-s.html
EU-TALBOT-SIMCA-1510-HATCHBACK-5D-01	4318	1680	1390	Automobile-Catalog 1980 Talbot 1510 1.3 LS	https://www.automobile-catalog.com/car/1980/3113795/talbot_1510_1_3_ls.html
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385	Auto-Data Opel Ascona C CC	https://www.auto-data.net/en/opel-ascona-c-cc-generation-520
EU-BMW-M3-E30-SEDAN-2D-01	4345	1680	1370	Automobile-Catalog 1988 BMW M3 Evolution	https://www.automobile-catalog.com/car/1988/31205/bmw_m3_evolution.html
EU-OPEL-KAPITAN-P2-SEDAN-4D-01	4831	1812	1456	Automobile-Catalog 1959 Opel Kapitan P2 2.6	https://www.automobile-catalog.com/car/1959/2410415/opel_kapitan.html
EU-OPEL-OLYMPIA-REKORD-SEDAN-2D-01	4240	1625	1550	Automobile-Catalog 1953 Opel Olympia Rekord Limousine	https://www.automobile-catalog.com/car/1953/2410475/opel_olympia_rekord_limousine.html
EU-OPEL-REKORD-P1-SEDAN-2D-01	4433	1616	1490	Automobile-Catalog 1958 Opel Olympia Rekord	https://www.automobile-catalog.com/car/1958/2410805/opel_olympia_rekord.html
EU-OPEL-REKORD-P1-SEDAN-4D-01	4433	1616	1490	Automobile-Catalog 1959 Opel Olympia Rekord 1.5L 4d	https://www.automobile-catalog.com/car/1959/2410880/opel_olympia_rekord_1_5l_4d.html
EU-OPEL-REKORD-P2-SEDAN-2D-01	4515	1632	1485	Automobile-Catalog 1962 Opel Rekord 1500 2d	https://www.automobile-catalog.com/car/1962/2411000/opel_rekord_1500_2d.html
EU-OPEL-REKORD-P2-SEDAN-4D-01	4515	1632	1478	Automobile-Catalog 1961 Opel Rekord 1500 4d	https://www.automobile-catalog.com/car/1961/2411030/opel_rekord_1500_4d.html
EU-OPEL-REKORD-A-SEDAN-2D-01	4512	1696	1465	Automobile-Catalog 1964 Opel Rekord 1500 2d	https://www.automobile-catalog.com/car/1964/2411540/opel_rekord_1500_2d_4gang.html
EU-OPEL-REKORD-A-SEDAN-4D-01	4512	1696	1465	Automobile-Catalog 1964 Opel Rekord 1700 4d	https://www.automobile-catalog.com/car/1964/2411585/opel_rekord_1700_4d_3gang.html
EU-OPEL-REKORD-B-SEDAN-2D-01	4529	1690	1440	Automobile-Catalog 1965 Opel Rekord 1500 2d	https://www.automobile-catalog.com/car/1965/2411765/opel_rekord_1500_2d_3gang.html
EU-OPEL-REKORD-B-SEDAN-4D-01	4529	1690	1440	Automobile-Catalog 1965 Opel Rekord 1500 4d	https://www.automobile-catalog.com/car/1965/2412005/opel_rekord_1500_4d_3gang.html
EU-BMW-M1-E26-COUPE-2D-01	4360	1824	1140	Auto-Data BMW M1 E26 3.5	https://www.auto-data.net/en/bmw-m1-e26-3.5-277hp-44012
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400	BMW M E28 M5 heritage;Automobile-Catalog 1986 BMW M5	https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m5-e28.html;https://www.automobile-catalog.com/car/1986/52160/bmw_m5.html
EU-OPEL-REKORD-P1-CARAVAN-3D-01	4432	1615	1600	Automobile-Catalog 1958 Opel Caravan	https://www.automobile-catalog.com/car/1958/2411330/opel_caravan.html
EU-OPEL-REKORD-P2-CARAVAN-3D-01	4515	1632	1516	Automobile-Catalog 1961 Opel Caravan 1500	https://www.automobile-catalog.com/car/1961/2411060/opel_caravan_1500.html
EU-OPEL-ASCONA-C-SEDAN-01	4366	1668	1395	Auto-Data Opel Ascona C	https://www.auto-data.net/en/opel-ascona-c-generation-519
EU-BMW-5-E12-SEDAN-01	4620	1690	1425	Auto-Data BMW 5 Series E12 facelift	https://www.auto-data.net/en/bmw-5-series-e12-facelift-1976-generation-5333
EU-KIA-PICANTO-II-HATCHBACK-5D-01	3595	1595	1480	Kia Europe New Picanto press kit	https://press.kia.com/content/dam/kiapress/EU/download-files/Picanto-2011/New-Kia-Picanto.doc
EU-BMW-5-E34-SEDAN-01	4720	1751	1412	Auto-Data BMW 5 Series E34 525i 24V	https://www.auto-data.net/en/bmw-5-series-e34-525i-24v-192hp-9672
EU-BMW-7-E23-SEDAN-01	4860	1800	1430	Auto-Data BMW 7 Series E23 facelift	https://www.auto-data.net/en/bmw-7-series-e23-facelift-1983-generation-5378
EU-MINI-MINI-R53-HATCHBACK-3D-01	3655	1688	1416	Automobile-Catalog 2004 Mini Cooper S	https://www.automobile-catalog.com/car/2004/1752185/mini_cooper_s.html
EU-TALBOT-TAGORA-SEDAN-01	4628	1810	1444	Automobile-Catalog 1981 Talbot Tagora SX;Automobile-Catalog 1981 Talbot Tagora DT	https://www.automobile-catalog.com/car/1981/26615/talbot_tagora_sx.html;https://www.automobile-catalog.com/car/1981/59450/talbot_tagora_dt.html
EU-VOLVO-S40-II-SEDAN-4D-01	4476	1770	1454	Volvo Cars Media UK S40 technical specifications	https://www.volvocars.com/uk/media/press-releases/464B5AA57533575D/
EU-TALBOT-SIMCA-1000-SEDAN-4D-STANDARD-01	3797	1485	1390	Automobile-Catalog 1970 Simca 1000 GLS	https://www.automobile-catalog.com/car/1970/3107000/simca_1000_gls.html
EU-TALBOT-SIMCA-1000-SEDAN-4D-FACELIFT-01	3811	1485	1395	Automobile-Catalog 1976 Simca 1006 SR	https://www.automobile-catalog.com/car/1976/3107390/simca_1006_sr.html
EU-TALBOT-SIMCA-1005-LS-SEDAN-4D-01	3808	1485	1395	Automobile-Catalog 1977 Simca 1005 LS	https://www.automobile-catalog.com/car/1977/39305/simca_1005_ls.html
EU-TALBOT-SIMCA-1000-RALLYE3-SEDAN-4D-01	3850	1560	1390	Automobile-Catalog 1978 Simca Rallye 3	https://www.automobile-catalog.com/car/1978/39980/simca_rallye_3.html
EU-TALBOT-SAMBA-HATCHBACK-01	3506	1528	1362	Automobile-Catalog 1983 Talbot Samba 1.4 GLS	https://www.automobile-catalog.com/car/1983/55535/talbot_samba_1_4_gls.html
EU-TALBOT-MURENA-COUPE-01	4070	1752	1220	Automobile-Catalog 1980 Talbot-Matra Murena 1.6	https://www.automobile-catalog.com/car/1980/25805/talbot_matra_murena_1_6-litre.html
EU-OPEL-CORSA-A-HATCHBACK-3D-PREFL-01	3622	1532	1365	Auto-Data Opel Corsa A	https://www.auto-data.net/en/opel-corsa-model-248
EU-OPEL-CORSA-A-HATCHBACK-3D-FACELIFT-01	3652	1542	1365	Auto-Data Opel Corsa A facelift 1990	https://www.auto-data.net/en/opel-corsa-model-248
EU-OPEL-CORSA-A-HATCHBACK-5D-PREFL-01	3622	1532	1365	Auto-Data Opel Corsa A	https://www.auto-data.net/en/opel-corsa-model-248
EU-OPEL-CORSA-A-HATCHBACK-5D-FACELIFT-01	3652	1542	1365	Auto-Data Opel Corsa A facelift 1990	https://www.auto-data.net/en/opel-corsa-model-248
EU-OPEL-CORSA-A-SEDAN-2D-01	3955	1540	1360	Auto-Data Opel Corsa A Sedan	https://www.auto-data.net/en/opel-corsa-model-248
EU-OPEL-CORSA-A-SEDAN-4D-01	3955	1540	1360	Auto-Data Opel Corsa A Sedan	https://www.auto-data.net/en/opel-corsa-model-248
EU-TALBOT-HORIZON-HATCHBACK-01	3960	1680	1410	Automobile-Catalog 1979 Talbot Horizon 1.3 GLS	https://www.automobile-catalog.com/car/1979/3116390/talbot_horizon_1_3_gls.html
EU-TALBOT-SIMCA-1100-HATCHBACK-3D-01	3920	1588	1458	Automobile-Catalog 1969 Simca 1100 LS	https://www.automobile-catalog.com/car/1969/3109220/simca_1100_ls.html
EU-TALBOT-SIMCA-1100-HATCHBACK-5D-01	3920	1588	1458	Automobile-Catalog 1969 Simca 1100 LS	https://www.automobile-catalog.com/car/1969/3109220/simca_1100_ls.html
EU-ALFA-ROMEO-2000-TIPO102-CONVERTIBLE-2D-01	4500	1660	1330	Automobile-Catalog 1958 Alfa Romeo 2000 Spider	https://www.automobile-catalog.com/car/1958/213845/alfa_romeo_2000_spider.html
EU-RENAULT-LATITUDE-SEDAN-4D-01	4897	1832	1483	Auto-Data Renault Latitude	https://www.auto-data.net/en/renault-latitude-model-1932
EU-TALBOT-SIMCA-1100-BREAK-WAGON-PREFL-01	3920	1588	1472	Automobile-Catalog 1969 Simca 1100 Break LS	https://www.automobile-catalog.com/car/1969/3109310/simca_1100_break_ls.html
EU-TALBOT-SIMCA-1100-BREAK-WAGON-FACELIFT-01	3929	1588	1472	Automobile-Catalog 1974 Simca 1100 Break LS	https://www.automobile-catalog.com/car/1974/3109655/simca_1100_break_ls.html
EU-TALBOT-SIMCA-1200-S-COUPE-2D-01	3997	1525	1270	Automobile-Catalog 1969 Simca 1200 S Coupe	https://www.automobile-catalog.com/car/1969/3109565/simca_1200_s_coupe.html
EU-TALBOT-SIMCA-1300-SEDAN-4D-01	4246	1580	1400	Automobile-Catalog 1964 Simca 1300	https://www.automobile-catalog.com/car/1964/3107600/simca_1300.html
EU-TALBOT-SIMCA-1301-SEDAN-4D-01	4457	1580	1400	Automobile-Catalog 1969 Simca 1301 LS	https://www.automobile-catalog.com/car/1969/3108215/simca_1301_ls.html
EU-TALBOT-SIMCA-1301-WAGON-5D-01	4315	1580	1420	Automobile-Catalog 1972 Simca 1301 Break Special	https://www.automobile-catalog.com/car/1972/3108665/simca_1301_break_special.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6601-6700_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6601-6700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6601-6700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8426 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2621 行）

