# 任务：all 第 3501-3600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0036__e8cfd79d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3501-3600 行

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
all 第 3501-3600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
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
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410
EU-BMW-3-SERIES-E90-SEDAN-01	4520	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395
EU-BMW-3-SERIES-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-SERIES-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-SERIES-E93-CONVERTIBLE-2D-PREFL-01	4580	1782	1384
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479
EU-CITROEN-C5-I-PHASE-I-HATCHBACK-5D-01	4618	1770	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-01	4745	1780	1476
EU-CITROEN-C5-I-PHASE-II-HATCHBACK-02	4750	1770	1480
EU-CITROEN-C5-I-PHASE-II-WAGON-01	4839	1780	1511
EU-CITROEN-C5-I-PHASE-I-WAGON-5D-01	4760	1770	1520
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420
EU-FIAT-PANDA-II-169-NATURAL-POWER-HATCHBACK-5D-01	3538	1589	1576
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522
EU-FORD-FIESTA-VII-MK7-SEDAN-4D-01	4409	1722	1473
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	3585	1595	1540
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475
EU-MAZDA-626-III-GD-SEDAN-4D-4WD-01	4515	1690	1395
EU-MAZDA-626-V-GF-SEDAN-01	4575	1710	1430
EU-MAZDA-6-II-GH-HATCHBACK-01	4735	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440
EU-MAZDA-6-II-GH-HATCHBACK-03	4765	1795	1440
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440
EU-MAZDA-6-II-GH-WAGON-5D-01	4765	1795	1490
EU-MAZDA-6-II-GH-WAGON-5D-02	4785	1795	1490
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704
EU-OPEL-ANTARA-A-SUV-02	4575	1850	1704
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-OPEL-MOVANO-A-BUS-L1H1-01	4899	1990	2253
EU-OPEL-MOVANO-A-BUS-L2H2-01	5399	1990	2493
EU-OPEL-MOVANO-A-BUS-L3H3-01	5899	1990	2720
EU-OPEL-MOVANO-A-VAN-L1H1-01	4899	1990	2253
EU-OPEL-MOVANO-A-VAN-L1H2-01	4899	1990	2496
EU-OPEL-MOVANO-A-VAN-L2H2-01	5399	1990	2493
EU-OPEL-MOVANO-A-VAN-L3H2-01	5899	1990	2490
EU-OPEL-MOVANO-A-VAN-L3H3-01	5899	1990	2720
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-LWB-01	5869	1990	2195
EU-OPEL-MOVANO-A-X70-CHASSIS-CAB-MWB-01	5369	1990	2200
EU-OPEL-MOVANO-A-X70-CREW-CAB-LWB-01	5869	1990	2203
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-B-MPV-OPC-01	4467	1801	1645
EU-OPEL-ZAFIRA-B-MPV-PREFL-01	4467	1801	1645
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564
EU-PEUGEOT-407-COUPE-2D-01	4815	1868	1399
EU-PEUGEOT-407-I-SEDAN-FACELIFT-01	4691	1811	1442
EU-PEUGEOT-407-I-SEDAN-PREFL-01	4676	1811	1447
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486
EU-PEUGEOT-407-PHASE-II-SEDAN-01	4691	1811	1455
EU-PEUGEOT-407-PHASE-I-SEDAN-01	4676	1811	1455
EU-PEUGEOT-407-SW-PHASE-I-WAGON-01	4763	1811	1486
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466
EU-SUBARU-FORESTER-II-FACELIFT-SUV-01	4450	1735	1590
EU-SUBARU-FORESTER-II-SUV-01	4450	1735	1590
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475
EU-SUBARU-LEGACY-IV-WAGON-01	4720	1730	1470
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695
EU-SUZUKI-GRAND-VITARA-II-3D-PREFL-SUV-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695
EU-SUZUKI-SX4-I-HATCHBACK-2WD-01	4100	1730	1565
EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	4140	1755	1620
EU-SUZUKI-SX4-I-HATCHBACK-5D-01	4100	1730	1565
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575
EU-TOYOTA-AVENSIS-II-HATCHBACK-5D-01	4630	1760	1480
EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	4645	1760	1485
EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	4630	1760	1480
EU-TOYOTA-AVENSIS-II-SEDAN-4D-01	4630	1760	1480
EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	4645	1760	1485
EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	4630	1760	1480
EU-TOYOTA-AVENSIS-II-WAGON-5D-01	4715	1760	1525
EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	4715	1760	1525
EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	4700	1760	1525
EU-TOYOTA-YARIS-BELTA-SCP92-SEDAN-4D-01	4300	1690	1460
EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	3785	1695	1530
EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	3750	1695	1530
EU-TOYOTA-YARIS-II-HATCHBACK-SR18-01	3800	1695	1530
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-3D-FACELIFT-01	3660	1660	1500
EU-TOYOTA-YARIS-I-XP10-HATCHBACK-5D-FACELIFT-01	3660	1660	1470

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Lancia	Flavia berlina	2	Stufenheck	Frontantrieb	Benzin	85	115	May 1971	Dec 1974	2024-03-01	30737
Audi	A3	1.8 Tfsi Quattro	Schrägheck	Allrad	Benzin	118	160	Jul 2008	Aug 2012	2024-03-01	30738
Audi	A3	1.8 Tfsi Quattro	Schrägheck	Allrad	Benzin	118	160	Jul 2008	Mar 2013	2024-03-01	30739
Audi	Q5	3.2 FSI Quattro	SUV	Allrad	Benzin	199	270	Nov 2008	Dec 2012	2024-03-01	30740
Lancia	Fulvia berlina	1.1	Stufenheck	Frontantrieb	Benzin	52	71	Nov 1964	Dec 1969	2024-03-01	30741
Lancia	Fulvia berlina	1.2	Stufenheck	Frontantrieb	Benzin	64	87	Feb 1967	Dec 1969	2024-03-01	30742
Lancia	Fulvia berlina	1.2	Stufenheck	Frontantrieb	Benzin	64	87	Dec 1969	Dec 1970	2024-03-01	30743
Lancia	Fulvia berlina	1.3	Stufenheck	Frontantrieb	Benzin	70	95	Dec 1969	Dec 1970	2024-03-01	30744
Lancia	Fulvia berlina	1.2	Stufenheck	Frontantrieb	Benzin	58	79	Aug 1970	Dec 1972	2024-03-01	30745
Lancia	Fulvia berlina	1.3	Stufenheck	Frontantrieb	Benzin	62	84	Aug 1970	Dec 1972	2024-03-01	30746
Lancia	Fulvia	1.2	Coupe	Frontantrieb	Benzin	59	80	Apr 1965	Dec 1969	2024-03-01	30747
Lancia	Fulvia	1.2	Coupe	Frontantrieb	Benzin	65	88	Mar 1966	Dec 1967	2024-03-01	30748
Lancia	Fulvia	1.3	Coupe	Frontantrieb	Benzin	70	95	Feb 1967	Dec 1969	2024-03-01	30749
Lancia	Fulvia	1.3	Coupe	Frontantrieb	Benzin	74	101	Mar 1967	Dec 1969	2024-03-01	30750
Lancia	Fulvia	1.3	Coupe	Frontantrieb	Benzin	76	103	Dec 1968	Dec 1970	2024-03-01	30751
Lancia	Fulvia	1.6	Coupe	Frontantrieb	Benzin	96	130	Jun 1969	Dec 1970	2024-03-01	30752
Lancia	Fulvia	1.3	Coupe	Frontantrieb	Benzin	66	90	Aug 1970	Dec 1976	2024-03-01	30753
Lancia	Fulvia	1.6	Coupe	Frontantrieb	Benzin	84	114	Aug 1970	Dec 1973	2024-03-01	30754
Fiat	Panda	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	55	75	Jun 2006	Aug 2013	2024-03-01	30755
Iveco	Massif station wagon	3.0 HPI	Geländewagen geschlossen	Allrad	Diesel	107	146	Oct 2008	Feb 2011	2024-03-01	30756
Iveco	Massif station wagon	3.0 HPT	Geländewagen geschlossen	Allrad	Diesel	130	176	Oct 2008	Feb 2011	2024-03-01	30757
Iveco	Massif single cab	3.0 HPI	Pritsche/Fahrgestell	Allrad	Diesel	107	146	Oct 2008	Feb 2011	2024-03-01	30758
Iveco	Massif single cab	3.0 HPT	Pritsche/Fahrgestell	Allrad	Diesel	130	176	Oct 2008	Feb 2011	2024-03-01	30759
Iveco	Massif	3.0 HPI	Pick-up	Allrad	Diesel	107	146	Oct 2008	Feb 2011	2024-03-01	30760
Iveco	Massif	3.0 HPT	Pick-up	Allrad	Diesel	130	176	Oct 2008	Feb 2011	2024-03-01	30761
Opel	Antara a	2.0 Cdti	SUV	Frontantrieb	Diesel	93	127	Sep 2008	Dec 2011	2024-03-01	30762
Opel	Antara a	2.4	SUV	Frontantrieb	Benzin	103	140	Sep 2008	Dec 2011	2024-03-01	30763
Porsche	Cayenne	3.0 TDI	SUV	Allrad	Diesel	176	240	Feb 2009	Sep 2010	2024-03-01	30764
Opel	Zafira	1.6 CNG Turbo	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	110	150	Apr 2010	Apr 2015	2024-03-01	30765
Suzuki	Sx4 s-Cross	1.6 Ddis Allgrip	Schrägheck	Allrad	Diesel	88	120	Aug 2013	Jun 2022	2025-06-01	30795
Citroën	Evasion	2.0 HDI 16V	Großraumlimousine	Frontantrieb	Diesel	80	109	Sep 1999	Jul 2002	2024-03-01	30812
Mazda	2	1.6 Mz-cd	Schrägheck	Frontantrieb	Diesel	66	90	Oct 2008	Jun 2015	2024-03-01	30813
Subaru	Forester	2.0 AWD	SUV	Allrad	Benzin	110	150	Jan 2008	Sep 2013	2024-03-01	30814
Subaru	Forester	2.0 D AWD	SUV	Allrad	Diesel	108	147	Sep 2008	Sep 2013	2024-03-01	30815
Subaru	Forester	2.5 AWD	SUV	Allrad	Benzin	169	230	Jun 2008	Sep 2013	2024-03-01	30816
Subaru	Legacy iv station wagon	2.0 R AWD	Kombi	Allrad	Benzin	110	150	Sep 2007	Dec 2009	2024-03-01	30817
Subaru	Legacy iv	2.0 R AWD	Stufenheck	Allrad	Benzin	110	150	Sep 2007	Dec 2009	2024-03-01	30818
Subaru	Legacy iv	2.0 D AWD	Stufenheck	Allrad	Diesel	110	150	Feb 2008	Dec 2009	2024-03-01	30819
Subaru	Legacy iv	2.5 I AWD	Stufenheck	Allrad	Benzin	127	173	Sep 2007	Dec 2009	2024-03-01	30820
Peugeot	3008 i	1.6 VTI	Großraumlimousine	Frontantrieb	Benzin	88	120	Jun 2009	Aug 2016	2024-11-01	30821
Peugeot	3008 i	1.6 THP	Großraumlimousine	Frontantrieb	Benzin	110	150	Jun 2009	Aug 2016	2024-11-01	30822
Peugeot	3008 i	1.6 HDI	Großraumlimousine	Frontantrieb	Diesel	80	109	Jun 2009	Aug 2016	2024-11-01	30823
Peugeot	3008 i	2.0 HDI 150 / Bluehdi 150	Großraumlimousine	Frontantrieb	Diesel	110	150	Jun 2009	Aug 2016	2024-11-01	30824
Nissan	Bluebird	1.6	Stufenheck	Heckantrieb	Benzin	60	82	Apr 1972	Apr 1977	2024-03-01	30828
Opel	Movano a	2.5 Cdti	Bus	Frontantrieb	Diesel	74	101	Sep 2007	-	2024-03-01	30833
Ford	Focus ii	1.8	Schrägheck	Frontantrieb	Benzin	92	125	Mar 2006	Sep 2012	2024-03-01	30834
Ford	Focus ii	1.8	Stufenheck	Frontantrieb	Benzin	92	125	Mar 2006	Sep 2012	2024-03-01	30835
Ford	Focus ii turnier	1.8	Kombi	Frontantrieb	Benzin	92	125	Mar 2006	Sep 2012	2024-03-01	30836
Ford	Focus ii	2.5 RS	Schrägheck	Frontantrieb	Benzin	224	305	Jan 2009	Jul 2011	2024-03-01	30837
Porsche	944	2.5 Turbo	Cabriolet	Heckantrieb	Benzin	184	250	Nov 1990	Jul 1991	2024-03-01	30838
Ford	Ka	1.2	Schrägheck	Frontantrieb	Benzin	51	69	Oct 2008	May 2016	2024-03-01	30839
Ford	Ka	1.3 Tdci	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2008	May 2016	2024-03-01	30840
Ford	Fiesta vi	1.4 Tdci	Schrägheck	Frontantrieb	Diesel	50	68	Aug 2008	Sep 2012	2024-03-01	30841
Hyundai	I10 i	1.2	Schrägheck	Frontantrieb	Benzin	57	78	Nov 2008	Dec 2011	2024-03-01	30842
Mercedes-benz	B-Klasse sports tourer	B 170 NGT	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	85	116	Apr 2008	Nov 2011	2024-03-01	30843
Saab	9-3	2.0 T XWD	Kombi	Allrad	Benzin	154	209	Jun 2008	Feb 2015	2024-03-01	30844
Toyota	Yaris	1.33 Vvt-i	Schrägheck	Frontantrieb	Benzin	74	100	Nov 2008	Dec 2011	2024-03-01	30845
Peugeot	308 i	1.6 16V	Schrägheck	Frontantrieb	Benzin	103	140	Sep 2007	Oct 2014	2024-03-01	30846
Peugeot	308 sw i	2.0 Bioflex	Kombi	Frontantrieb	Benzin/Ethanol	103	140	Jan 2008	Dec 2011	2024-03-01	30847
Peugeot	407	2.0 Bioflex	Kombi	Frontantrieb	Benzin/Ethanol	103	140	Jan 2008	Dec 2010	2024-03-01	30848
Citroën	C5	2.0 16V Bioflex	Kombi	Frontantrieb	Benzin/Ethanol	103	140	Feb 2008	Jun 2010	2024-07-01	30849
Citroën	C5	2.0 16V Bioflex	Stufenheck	Frontantrieb	Benzin/Ethanol	103	140	Feb 2008	Dec 2012	2024-07-01	30850
Dodge	Caliber	2.4 Turbo	Schrägheck	Frontantrieb	Benzin	217	295	Dec 2007	-	2024-03-01	30851
Dodge	Journey	2.7 Flexfuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	136	185	Jan 2009	Dec 2011	2024-03-01	30852
Dodge	Journey	2.4	Großraumlimousine	Frontantrieb	Benzin	125	170	Jan 2009	-	2024-03-01	30853
Suzuki	Sx4	1.6	Stufenheck	Frontantrieb	Benzin	79	107	Oct 2007	-	2024-03-01	30854
Suzuki	Sx4 / classic	2.0 4X4	Schrägheck	Allrad	Benzin	107	146	Jun 2006	-	2024-03-01	30857
Suzuki	Grand vitara ii	3.2 Allrad	Geländewagen geschlossen	Allrad	Benzin	171	233	Jan 2009	Feb 2015	2024-03-01	30861
Suzuki	Grand vitara ii	2.4 Allrad	Geländewagen geschlossen	Allrad	Benzin	124	169	Jan 2009	-	2024-03-01	30862
BMW	3	330 D	Cabriolet	Heckantrieb	Diesel	180	245	Jan 2009	Sep 2013	2024-03-01	30863
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	180	245	Sep 2008	Oct 2011	2024-03-01	30864
BMW	3	330 D	Kombi	Heckantrieb	Diesel	180	245	Feb 2008	May 2012	2024-03-01	30865
BMW	3	330 D	Coupe	Heckantrieb	Diesel	180	245	Jan 2009	Jun 2013	2024-03-01	30866
BMW	3	330 XD	Coupe	Allrad	Diesel	180	245	Mar 2008	Feb 2010	2024-03-01	30867
BMW	3	330 D Xdrive	Stufenheck	Allrad	Diesel	180	245	Sep 2008	Oct 2011	2024-03-01	30868
BMW	3	330 D Xdrive	Kombi	Allrad	Diesel	180	245	Jan 2009	Jun 2012	2024-03-01	30869
Mercedes-benz	C-Klasse	C 250 CDI	Stufenheck	Heckantrieb	Diesel	150	204	Aug 2008	Jan 2014	2024-03-01	30870
Toyota	Avensis	1.6 Vvt-i	Stufenheck	Frontantrieb	Benzin	97	132	Nov 2008	Oct 2018	2024-03-01	30874
Toyota	Avensis	1.8 Vvt-i	Stufenheck	Frontantrieb	Benzin	108	147	Nov 2008	Oct 2018	2024-03-01	30875
Toyota	Avensis	2.0 Vvt-i	Stufenheck	Frontantrieb	Benzin	112	152	Nov 2008	Oct 2018	2024-03-01	30876
Toyota	Avensis	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	93	126	Nov 2008	Oct 2011	2026-04-01	30877
Toyota	Avensis	2.2 D-4d	Stufenheck	Frontantrieb	Diesel	110	150	Nov 2008	Oct 2018	2024-03-01	30878
Toyota	Avensis	2.2 D-4d	Stufenheck	Frontantrieb	Diesel	130	177	Nov 2008	Oct 2018	2024-03-01	30879
Toyota	Avensis	1.6 Vvt-i	Kombi	Frontantrieb	Benzin	97	132	Nov 2008	Oct 2018	2024-03-01	30880
Toyota	Avensis	1.8 Vvt-i	Kombi	Frontantrieb	Benzin	108	147	Nov 2008	Oct 2018	2024-03-01	30881
Toyota	Avensis	2.0 Vvt-i	Kombi	Frontantrieb	Benzin	112	152	Nov 2008	Oct 2018	2024-03-01	30882
Toyota	Avensis	2.0 D-4d	Kombi	Frontantrieb	Diesel	93	126	Nov 2008	Oct 2018	2024-03-01	30883
Toyota	Avensis	2.2 D-4d	Kombi	Frontantrieb	Diesel	110	150	Nov 2008	Oct 2018	2024-03-01	30884
Toyota	Avensis	2.2 D-4d	Kombi	Frontantrieb	Diesel	130	177	Nov 2008	Oct 2018	2024-03-01	30885
Opel	Insignia a	2.0 Turbo 4X4	Stufenheck	Allrad	Benzin	162	220	Jul 2008	Mar 2017	2024-03-01	30886
Opel	Insignia a sports tourer	2.0 Turbo 4X4	Kombi	Allrad	Benzin	162	220	Jul 2008	Jun 2011	2024-03-01	30887
Mazda	6	2.2 Mzr-cd	Stufenheck	Frontantrieb	Diesel	92	125	Jan 2009	Dec 2012	2024-03-01	30888
Mazda	6	2.2 Mzr-cd	Stufenheck	Frontantrieb	Diesel	120	163	Jan 2009	Dec 2012	2024-03-01	30889
Mazda	6	2.2 Mzr-cd	Stufenheck	Frontantrieb	Diesel	136	185	Jan 2009	Dec 2012	2024-03-01	30890
Mazda	6	2.2 Mzr-cd	Schrägheck	Frontantrieb	Diesel	136	185	Jan 2009	Dec 2012	2024-03-01	30891
Mazda	6	2.2 Mzr-cd	Schrägheck	Frontantrieb	Diesel	120	163	Jan 2009	Dec 2012	2024-03-01	30892
Mazda	6	2.2 Mzr-cd	Schrägheck	Frontantrieb	Diesel	92	125	Jan 2009	Dec 2012	2024-03-01	30893
Mazda	6	2.2 Mzr-cd	Kombi	Frontantrieb	Diesel	92	125	Jan 2009	Dec 2010	2024-03-01	30894
Mazda	6	2.2 Mzr-cd	Kombi	Frontantrieb	Diesel	120	163	Aug 2008	Jul 2013	2024-03-01	30895
Mazda	6	2.2 Mzr-cd	Kombi	Frontantrieb	Diesel	136	185	Aug 2008	Dec 2011	2024-03-01	30896


--- Round 1 / 首次发送 ---
## 更新点

* 完成前 30 个 Ktype 的物理外廓映射，共形成 33 条 READY 映射。
* `30754` 不能粗暴合并：Fulvia 1600 HF 标准车身与 Lusso 的长度分别为 3935 mm、3975 mm，已拆为两个稳定派生 id。([汽车目录][1])
* `30756`、`30757` 按 Iveco 官方资料拆分三门短轴和五门长轴 Station Wagon；Pickup 与 Chassis Cab 也分别建组。([Iveco][2])
* Lancia 2000 Berlina 高度采用 1460 mm；该数值获得 Carfolio 与同期规格资料支持，没有采用存在冲突的 1440 mm 聚合值。([Carfolio][3])
* Audi Q5 与 Fiat Panda 新组均已确认不含后视镜宽度。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 READY Ktype：30
* READY 映射：33
* 待处理 Ktype：70
* 当前已引用尺寸组：21

  * 本轮首次创建：15
  * 复用跨批次已有组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30737	30737	Sedan	Lancia 2000	820.210	4	EU-LANCIA-2000-TIPO-820-SEDAN-4D-01	HIGH	输入名称为Flavia berlina；该Ktype对应Lancia 2000 Berlina。	READY
30738	30738	Hatchback	A3 II (8P)	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	8P1三门改款车身。	READY
30739	30739	Hatchback	A3 II (8P)	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	8PA Sportback五门改款车身。	READY
30740	30740	SUV	Q5 I (8R)	8R	5	EU-AUDI-Q5-8R-SUV-5D-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
30741	30741	Sedan	Fulvia Berlina Series I	818.100	4	EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	HIGH	Series I 2C Berlina外廓。	READY
30742	30742	Sedan	Fulvia Berlina Series I	818.310	4	EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	HIGH	Series I GTE Berlina外廓。	READY
30743	30743	Sedan	Fulvia Berlina Series II		4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II Berlina外廓。	READY
30744	30744	Sedan	Fulvia Berlina Series II	818.610	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II Berlina外廓。	READY
30745	30745	Sedan	Fulvia Berlina Series II	818.694	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II 1.2 Berlina外廓。	READY
30746	30746	Sedan	Fulvia Berlina Series II	818.612	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II 1.3 Berlina外廓。	READY
30747	30747	Coupe	Fulvia Coupe Series I	818.130	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Series I标准Coupe外廓。	READY
30748	30748	Coupe	Fulvia Coupe Series I	818.140	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	HIGH	Series I轻量HF短车身外廓。	READY
30749	30749	Coupe	Fulvia Coupe Series I	818.330	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Rallye 1.3标准Coupe外廓。	READY
30750	30750	Coupe	Fulvia Coupe Series I	818.340	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	HIGH	Rallye 1.3 HF短车身外廓。	READY
30751	30751	Coupe	Fulvia Coupe Series I	818.360	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Rallye 1.3 S Series I标准外廓。	READY
30752	30752	Coupe	Fulvia Coupe Series I	818.540	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-1600-HF-2D-01	HIGH	1600 HF Variante 1016宽轮拱外廓。	READY
30753	30753	Coupe	Fulvia Coupe Series II	818.630	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-13S-2D-01	HIGH	Series II 1.3 S外廓；后续Coupe 3三维相同。	READY
30754_standard	30754	Coupe	Fulvia Coupe Series II	818.740	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-2D-01	HIGH	Series II 1600 HF无Lusso加长保险杠外廓。	READY
30754_lusso	30754	Coupe	Fulvia Coupe Series II	818.740	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-LUSSO-2D-01	HIGH	1600 HF Lusso带保险杠外廓，长度不同。	READY
30755	30755	Hatchback	Panda II (169)	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	HIGH	标准五门柴油版外廓。	READY
30756_3dr	30756	SUV	Massif		3	EU-IVECO-MASSIF-STATION-WAGON-3D-01	MEDIUM	Station Wagon覆盖三门短轴物理外廓。	READY
30756_5dr	30756	SUV	Massif		5	EU-IVECO-MASSIF-STATION-WAGON-5D-01	MEDIUM	Station Wagon覆盖五门长轴物理外廓。	READY
30757_3dr	30757	SUV	Massif		3	EU-IVECO-MASSIF-STATION-WAGON-3D-01	MEDIUM	Station Wagon覆盖三门短轴物理外廓。	READY
30757_5dr	30757	SUV	Massif		5	EU-IVECO-MASSIF-STATION-WAGON-5D-01	MEDIUM	Station Wagon覆盖五门长轴物理外廓。	READY
30758	30758	Pickup	Massif		2	EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	HIGH	Single Cab对应chassis-cab物理外廓。	READY
30759	30759	Pickup	Massif		2	EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	HIGH	Single Cab对应chassis-cab物理外廓。	READY
30760	30760	Pickup	Massif		2	EU-IVECO-MASSIF-PICKUP-2D-01	HIGH	两门一体式货斗Pickup外廓。	READY
30761	30761	Pickup	Massif		2	EU-IVECO-MASSIF-PICKUP-2D-01	HIGH	两门一体式货斗Pickup外廓。	READY
30762	30762	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	改款前五门SUV外廓。	READY
30763	30763	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	改款前五门SUV外廓。	READY
30764	30764	SUV	Cayenne I Facelift (957)	957	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH	957标准车身，不属于GTS或Turbo S外廓。	READY
30765	30765	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH	Zafira B改款后CNG标准外廓。	READY
30795	30795	Hatchback	SX4 S-Cross I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH	AllGrip不改变该代标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-2000-TIPO-820-SEDAN-4D-01	4620	1610	1460	Carfolio Lancia 2000 Berlina specifications	https://www.carfolio.com/lancia-2000-berlina-337832
EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	4110	1555	1400	Automobile-Catalog 1968 Lancia Fulvia 2C Berlina	https://www.automobile-catalog.com/car/1968/1375970/lancia_fulvia_2c_berlina.html
EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	4155	1555	1400	Automobile-Catalog 1970 Lancia Fulvia Berlina	https://www.automobile-catalog.com/car/1970/1376120/lancia_fulvia_berlina.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	3975	1555	1300	Automobile-Catalog 1965 Lancia Fulvia Coupe	https://www.automobile-catalog.com/car/1965/1375685/lancia_fulvia_coupe.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	3935	1555	1300	Automobile-Catalog 1966 Lancia Fulvia Coupe HF	https://www.automobile-catalog.com/car/1966/1375700/lancia_fulvia_coupe_hf.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-1600-HF-2D-01	3935	1570	1330	Automobile-Catalog Lancia Fulvia Coupe 1.6 HF Variante 1016	https://www.automobile-catalog.com/car/1968/1376270/lancia_fulvia_coupe_1_6_hf_variante_1016.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-13S-2D-01	3975	1555	1320	Automobile-Catalog 1971 Lancia Fulvia Coupe Rallye 1.3 S	https://www.automobile-catalog.com/car/1971/1376135/lancia_fulvia_coupe_rallye_1_3_s.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-2D-01	3935	1570	1330	Automobile-Catalog 1973 Lancia Fulvia Coupe 1600 HF	https://www.automobile-catalog.com/car/1973/1376150/lancia_fulvia_coupe_1600_hf.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-LUSSO-2D-01	3975	1570	1330	Automobile-Catalog 1972 Lancia Fulvia Coupe 1600 HF Lusso	https://www.automobile-catalog.com/car/1972/1376210/lancia_fulvia_coupe_1600_hf_lusso.html
EU-AUDI-Q5-8R-SUV-5D-PREFL-01	4629	1880	1653	Automobile-Catalog 2009 Audi Q5 3.2 FSI quattro	https://www.automobile-catalog.com/car/2009/1192040/audi_q5_3_2_fsi_quattro_s-tronic.html
EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	3538	1589	1540	Automobile-Catalog 2006 Fiat Panda 1.3 Multijet 16V Dynamic DPF	https://www.automobile-catalog.com/car/2006/726875/fiat_panda_1_3_multijet_16v_dynamic_dpf.html
EU-IVECO-MASSIF-STATION-WAGON-3D-01	4248	1750	2050	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-STATION-WAGON-5D-01	4720	1750	2050	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	4445	1750	2000	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-PICKUP-2D-01	4548	1750	2000	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
```

## 下一步优先处理

1. 集中闭合 `30812–30824`：Citroën Evasion、Mazda 2、Subaru Forester/Legacy、Peugeot 3008。
2. Subaru Forester 需先排除 SH 与上一代 SG 的生产日期重叠，不能直接套用现有 Forester II 组。
3. 随后处理 `30828–30854`，优先解决 Movano Bus 的轴距/车顶派生和 Focus II 跨改款拆分。
4. 已有尺寸组继续直接复用，不重复抓取三维和来源。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1973/1376150/lancia_fulvia_coupe_1600_hf.html?utm_source=chatgpt.com "1973 Lancia Fulvia Coupe 1600 HF Specs Review (84 kW / 114 PS / 113 hp) (up to mid-year 1973 for Europe )"
[2]: https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx "Massif in detail"
[3]: https://www.carfolio.com/lancia-2000-berlina-337832?utm_source=chatgpt.com "1971 Lancia 2000 Berlina: detailed specifications ..."
[4]: https://www.automobile-catalog.com/car/2009/1192040/audi_q5_3_2_fsi_quattro_s-tronic.html?utm_source=chatgpt.com "2009 Audi Q5 3.2 FSI Quattro S-Tronic (d-cl. 7)"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 新增完成 `30812–30854` 范围内的 36 个 Ktype，共形成 43 条 READY 映射。
* Mazda 2、Focus II、407 SW 按改款前后拆分；Movano Bus 按现有 `L1H1/L2H2/L3H3` 缓存组拆分，未重复输出尺寸来源。
* 新建 Evasion、Forester SH、Legacy BL、3008 I 四个尺寸组。Forester SH 的欧洲版汽油、柴油及 2.5 XT 外廓一致，均为 `4560×1780×1675 mm`。([汽车目录][1])
* Focus RS、Bluebird 610、944 Turbo Cabriolet、Ka II 均使用独立外廓，没有套用普通车型缓存。([汽车目录档案][2])
* B 170 NGT 采用奔驰官方档案中的专用高度 `1624 mm`，没有套用普通 W245 的较低车高。([marsClassic][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：66
* READY 映射：76
* PENDING／待处理 Ktype：34
* 已确认尺寸组：54
* 本轮首次创建尺寸组：11
* 本轮直接复用既有尺寸组：22
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30812	30812	MPV	Evasion I Phase II		5	EU-CITROEN-EVASION-I-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV外廓。	READY
30813_prefl	30813	Hatchback	Mazda2 II (DE)	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	MEDIUM	生产期覆盖改款前五门外廓。	READY
30813_facelift	30813	Hatchback	Mazda2 II (DE)	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	MEDIUM	生产期覆盖改款后五门外廓。	READY
30814	30814	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30815	30815	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30816	30816	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30817	30817	Wagon	Legacy IV	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH	BP旅行版改款外廓。	READY
30818	30818	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30819	30819	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30820	30820	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30821	30821	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30822	30822	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30823	30823	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30824	30824	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30828	30828	Sedan	Bluebird IV	610	4	EU-NISSAN-BLUEBIRD-610-SEDAN-4D-01	HIGH	610系列四门轿车外廓。	READY
30833_l1h1	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	MEDIUM	Bus覆盖L1H1物理分支。	READY
30833_l2h2	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	MEDIUM	Bus覆盖L2H2物理分支。	READY
30833_l3h3	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	MEDIUM	Bus覆盖L3H3物理分支。	READY
30834_prefl	30834	Hatchback	Focus II			EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	MEDIUM	生产期覆盖改款前掀背外廓。	READY
30834_facelift	30834	Hatchback	Focus II			EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	生产期覆盖改款后掀背外廓。	READY
30835	30835	Sedan	Focus II		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH	四门轿车外廓。	READY
30836_prefl	30836	Wagon	Focus II		5	EU-FORD-FOCUS-II-WAGON-PREFL-01	MEDIUM	生产期覆盖改款前旅行版外廓。	READY
30836_facelift	30836	Wagon	Focus II		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	MEDIUM	生产期覆盖改款后旅行版外廓。	READY
30837	30837	Hatchback	Focus II RS		3	EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	HIGH	RS宽体三门外廓。	READY
30838	30838	Convertible	944 Turbo	951	2	EU-PORSCHE-944-951-TURBO-CONVERTIBLE-2D-01	HIGH	限量Turbo Cabriolet外廓。	READY
30839	30839	Hatchback	Ka II	RU8	3	EU-FORD-KA-II-RU8-HATCHBACK-3D-01	HIGH	第二代三门掀背外廓。	READY
30840	30840	Hatchback	Ka II	RU8	3	EU-FORD-KA-II-RU8-HATCHBACK-3D-01	HIGH	第二代三门掀背外廓。	READY
30841_3dr	30841	Hatchback	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	该Ktype覆盖三门物理分支。	READY
30841_5dr	30841	Hatchback	Fiesta VII	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	该Ktype覆盖五门物理分支；三维相同。	READY
30842	30842	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	第一代改款前五门外廓。	READY
30843	30843	Hatchback	B-Class Sports Tourer	245.233	5	EU-MERCEDES-BENZ-B-CLASS-W245-NGT-HATCHBACK-5D-01	HIGH	NGT车型专用车高外廓。	READY
30844	30844	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款后SportCombi外廓。	READY
30845	30845	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	1.33车型对应改款后五门外廓。	READY
30846	30846	Hatchback	308 I		5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH	第一代五门掀背外廓。	READY
30847	30847	Wagon	308 SW I		5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH	第一代Phase I旅行版外廓。	READY
30848_prefl	30848	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	MEDIUM	生产期覆盖改款前旅行版外廓。	READY
30848_facelift	30848	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	MEDIUM	生产期覆盖改款后旅行版外廓。	READY
30849	30849	Wagon	C5 II (X7)	RW	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH	X7 Tourer五门外廓。	READY
30850	30850	Sedan	C5 II (X7)	RD	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	X7四门轿车外廓。	READY
30851	30851	Hatchback	Caliber	PM	5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH	SRT-4动力不改变该车身外廓组。	READY
30852	30852	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH	第一代五门MPV外廓。	READY
30853	30853	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH	第一代五门MPV外廓。	READY
30854	30854	Sedan	SX4 I	GY	4	EU-SUZUKI-SX4-I-SEDAN-4D-01	HIGH	欧洲版四门轿车外廓。	READY
```

## 4. 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-EVASION-I-PHASE-II-MPV-5D-01	4454	1812	1710	Automobile-Catalog Citroën Evasion Phase II specifications	https://www.automobile-catalog.com/car/2001/2613410/citroen_evasion_2_1_hdi_x.html
EU-SUBARU-FORESTER-III-SH-SUV-5D-01	4560	1780	1675	Automobile-Catalog 2009 Subaru Forester 2.0 X AWD Europe specifications	https://www.automobile-catalog.com/car/2009/3292085/subaru_forester_2_0_x_awd.html
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425	Automobile-Catalog Subaru Legacy IV sedan specifications	https://www.automobile-catalog.com/car/2004/3263075/subaru_legacy_2_5_i.html
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628	Automobile-Catalog Peugeot 3008 I specifications	https://www.automobile-catalog.com/car/2011/2626700/peugeot_3008_1_6_hdi_fap_112_110.html
EU-NISSAN-BLUEBIRD-610-SEDAN-4D-01	4215	1600	1405	Nissan Global Heritage Datsun Bluebird U 1600GL	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/bluebird_u_1600gl.html
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484	Ford Focus RS official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/04/Ford-Focus-RS-2008-UK.pdf
EU-PORSCHE-944-951-TURBO-CONVERTIBLE-2D-01	4230	1735	1275	Porsche 944 Turbo Cabriolet factory technical data	https://www.no-speedlimit.it/Porsche_Werkfoto_1991_944.html
EU-FORD-KA-II-RU8-HATCHBACK-3D-01	3620	1658	1505	Ford Ka official brochure	https://www.bluelightcars.co.uk/wp-content/uploads/Ford-Brochure-KA.pdf
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481	Automobile-Catalog Ford Fiesta 1.4 TDCi Europe specifications	https://www.automobile-catalog.com/car/2009/979970/ford_fiesta_1_4_tdci_style.html
EU-MERCEDES-BENZ-B-CLASS-W245-NGT-HATCHBACK-5D-01	4273	1777	1624	Mercedes-Benz Public Archive B 170 NGT BlueEFFICIENCY	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/B-170-NGT-BlueEFFICIENCY-2008---2009.xhtml?oid=192213159
EU-SUZUKI-SX4-I-SEDAN-4D-01	4490	1730	1545	Automobile-Catalog 2008 Suzuki SX4 Sedan 1.6 VVT Europe specifications	https://www.automobile-catalog.com/car/2008/3408965/suzuki_sx4_sedan_1_6_vvt_2wd.html
```

## 5. 下一步优先处理

1. 处理 `30857–30870`：优先复用 SX4、Grand Vitara II 和 BMW E9x 缓存，只首次创建 Mercedes-Benz C-Class W204 改款前后尺寸组。
2. 处理 `30874–30885`：按 Toyota Avensis T27 的 2008 原版、2012 改款和 2015 二次改款核对 Sedan 与 Wagon 外廓。
3. 处理 `30886–30896`：复用 Insignia A 与 Mazda 6 GH 缓存，并只拆分确有尺寸变化的改款分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/2613410/citroen_evasion_2_1_hdi_x.html?utm_source=chatgpt.com "2001 Citroen Evasion 2.0 HDi X Specs Review (80 kW ..."
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/04/Ford-Focus-RS-2008-UK.pdf?utm_source=chatgpt.com "Ford-Focus-RS-2008-UK.pdf"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/B-170-NGT-BlueEFFICIENCY-2008---2009.xhtml?oid=192213159 "B 170 NGT BlueEFFICIENCY, 2008 - 2009"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 34 个 Ktype 已全部闭合；本轮首次创建 W204 Sedan 改款前后及 Avensis T27 Sedan/Wagon 三阶段共 8 个尺寸组，其余均按累计缓存直接复用。
* 已完成轻量机械检查：两张表表头固定、133 个 `id` 唯一、78 个 `DIMENSION_GROUP_ID` 唯一、全部映射引用闭合、尺寸及来源非空。
* 当前批次已达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：133
* PENDING 映射：0
* 最终尺寸组：78
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30737	30737	Sedan	Lancia 2000	820.210	4	EU-LANCIA-2000-TIPO-820-SEDAN-4D-01	HIGH	输入名称为Flavia berlina；该Ktype对应Lancia 2000 Berlina。	READY
30738	30738	Hatchback	A3 II (8P)	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	8P1三门改款车身。	READY
30739	30739	Hatchback	A3 II (8P)	8PA	5	EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	HIGH	8PA Sportback五门改款车身。	READY
30740	30740	SUV	Q5 I (8R)	8R	5	EU-AUDI-Q5-8R-SUV-5D-PREFL-01	HIGH	8R改款前标准SUV外廓。	READY
30741	30741	Sedan	Fulvia Berlina Series I	818.100	4	EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	HIGH	Series I 2C Berlina外廓。	READY
30742	30742	Sedan	Fulvia Berlina Series I	818.310	4	EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	HIGH	Series I GTE Berlina外廓。	READY
30743	30743	Sedan	Fulvia Berlina Series II		4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II Berlina外廓。	READY
30744	30744	Sedan	Fulvia Berlina Series II	818.610	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II Berlina外廓。	READY
30745	30745	Sedan	Fulvia Berlina Series II	818.694	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II 1.2 Berlina外廓。	READY
30746	30746	Sedan	Fulvia Berlina Series II	818.612	4	EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	HIGH	Series II 1.3 Berlina外廓。	READY
30747	30747	Coupe	Fulvia Coupe Series I	818.130	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Series I标准Coupe外廓。	READY
30748	30748	Coupe	Fulvia Coupe Series I	818.140	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	HIGH	Series I轻量HF短车身外廓。	READY
30749	30749	Coupe	Fulvia Coupe Series I	818.330	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Rallye 1.3标准Coupe外廓。	READY
30750	30750	Coupe	Fulvia Coupe Series I	818.340	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	HIGH	Rallye 1.3 HF短车身外廓。	READY
30751	30751	Coupe	Fulvia Coupe Series I	818.360	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	HIGH	Rallye 1.3 S Series I标准外廓。	READY
30752	30752	Coupe	Fulvia Coupe Series I	818.540	2	EU-LANCIA-FULVIA-COUPE-SERIES-I-1600-HF-2D-01	HIGH	1600 HF Variante 1016宽轮拱外廓。	READY
30753	30753	Coupe	Fulvia Coupe Series II	818.630	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-13S-2D-01	HIGH	Series II 1.3 S外廓；后续Coupe 3三维相同。	READY
30754_standard	30754	Coupe	Fulvia Coupe Series II	818.740	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-2D-01	HIGH	Series II 1600 HF无Lusso加长保险杠外廓。	READY
30754_lusso	30754	Coupe	Fulvia Coupe Series II	818.740	2	EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-LUSSO-2D-01	HIGH	1600 HF Lusso带保险杠外廓，长度不同。	READY
30755	30755	Hatchback	Panda II (169)	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	HIGH	标准五门柴油版外廓。	READY
30756_3dr	30756	SUV	Massif		3	EU-IVECO-MASSIF-STATION-WAGON-3D-01	MEDIUM	Station Wagon覆盖三门短轴物理外廓。	READY
30756_5dr	30756	SUV	Massif		5	EU-IVECO-MASSIF-STATION-WAGON-5D-01	MEDIUM	Station Wagon覆盖五门长轴物理外廓。	READY
30757_3dr	30757	SUV	Massif		3	EU-IVECO-MASSIF-STATION-WAGON-3D-01	MEDIUM	Station Wagon覆盖三门短轴物理外廓。	READY
30757_5dr	30757	SUV	Massif		5	EU-IVECO-MASSIF-STATION-WAGON-5D-01	MEDIUM	Station Wagon覆盖五门长轴物理外廓。	READY
30758	30758	Pickup	Massif		2	EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	HIGH	Single Cab对应chassis-cab物理外廓。	READY
30759	30759	Pickup	Massif		2	EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	HIGH	Single Cab对应chassis-cab物理外廓。	READY
30760	30760	Pickup	Massif		2	EU-IVECO-MASSIF-PICKUP-2D-01	HIGH	两门一体式货斗Pickup外廓。	READY
30761	30761	Pickup	Massif		2	EU-IVECO-MASSIF-PICKUP-2D-01	HIGH	两门一体式货斗Pickup外廓。	READY
30762	30762	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	改款前五门SUV外廓。	READY
30763	30763	SUV	Antara A	L07	5	EU-OPEL-ANTARA-A-SUV-01	HIGH	改款前五门SUV外廓。	READY
30764	30764	SUV	Cayenne I Facelift (957)	957	5	EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	HIGH	957标准车身，不属于GTS或Turbo S外廓。	READY
30765	30765	MPV	Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	HIGH	Zafira B改款后CNG标准外廓。	READY
30795	30795	Hatchback	SX4 S-Cross I	JY	5	EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	HIGH	AllGrip不改变该代标准外廓。	READY
30812	30812	MPV	Evasion I Phase II		5	EU-CITROEN-EVASION-I-PHASE-II-MPV-5D-01	HIGH	Phase II五门MPV外廓。	READY
30813_prefl	30813	Hatchback	Mazda2 II (DE)	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	MEDIUM	生产期覆盖改款前五门外廓。	READY
30813_facelift	30813	Hatchback	Mazda2 II (DE)	DE	5	EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	MEDIUM	生产期覆盖改款后五门外廓。	READY
30814	30814	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30815	30815	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30816	30816	SUV	Forester III	SH	5	EU-SUBARU-FORESTER-III-SH-SUV-5D-01	HIGH	SH代五门SUV外廓。	READY
30817	30817	Wagon	Legacy IV	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH	BP旅行版改款外廓。	READY
30818	30818	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30819	30819	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30820	30820	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	HIGH	BL轿车改款外廓。	READY
30821	30821	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30822	30822	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30823	30823	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30824	30824	MPV	3008 I	T84	5	EU-PEUGEOT-3008-I-T84-MPV-5D-01	HIGH	第一代五门跨界MPV外廓。	READY
30828	30828	Sedan	Bluebird IV	610	4	EU-NISSAN-BLUEBIRD-610-SEDAN-4D-01	HIGH	610系列四门轿车外廓。	READY
30833_l1h1	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L1H1-01	MEDIUM	Bus覆盖L1H1物理分支。	READY
30833_l2h2	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L2H2-01	MEDIUM	Bus覆盖L2H2物理分支。	READY
30833_l3h3	30833	MPV	Movano A	X70		EU-OPEL-MOVANO-A-BUS-L3H3-01	MEDIUM	Bus覆盖L3H3物理分支。	READY
30834_prefl	30834	Hatchback	Focus II			EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	MEDIUM	生产期覆盖改款前掀背外廓。	READY
30834_facelift	30834	Hatchback	Focus II			EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	MEDIUM	生产期覆盖改款后掀背外廓。	READY
30835	30835	Sedan	Focus II		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH	四门轿车外廓。	READY
30836_prefl	30836	Wagon	Focus II		5	EU-FORD-FOCUS-II-WAGON-PREFL-01	MEDIUM	生产期覆盖改款前旅行版外廓。	READY
30836_facelift	30836	Wagon	Focus II		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	MEDIUM	生产期覆盖改款后旅行版外廓。	READY
30837	30837	Hatchback	Focus II RS		3	EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	HIGH	RS宽体三门外廓。	READY
30838	30838	Convertible	944 Turbo	951	2	EU-PORSCHE-944-951-TURBO-CONVERTIBLE-2D-01	HIGH	限量Turbo Cabriolet外廓。	READY
30839	30839	Hatchback	Ka II	RU8	3	EU-FORD-KA-II-RU8-HATCHBACK-3D-01	HIGH	第二代三门掀背外廓。	READY
30840	30840	Hatchback	Ka II	RU8	3	EU-FORD-KA-II-RU8-HATCHBACK-3D-01	HIGH	第二代三门掀背外廓。	READY
30841_3dr	30841	Hatchback	Fiesta VII	CB1	3	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	该Ktype覆盖三门物理分支。	READY
30841_5dr	30841	Hatchback	Fiesta VII	CB1	5	EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	MEDIUM	该Ktype覆盖五门物理分支；三维相同。	READY
30842	30842	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	第一代改款前五门外廓。	READY
30843	30843	Hatchback	B-Class Sports Tourer	245.233	5	EU-MERCEDES-BENZ-B-CLASS-W245-NGT-HATCHBACK-5D-01	HIGH	NGT车型专用车高外廓。	READY
30844	30844	Wagon	9-3 II	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH	改款后SportCombi外廓。	READY
30845	30845	Hatchback	Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	1.33车型对应改款后五门外廓。	READY
30846	30846	Hatchback	308 I		5	EU-PEUGEOT-308-I-HATCHBACK-5D-01	HIGH	第一代五门掀背外廓。	READY
30847	30847	Wagon	308 SW I		5	EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	HIGH	第一代Phase I旅行版外廓。	READY
30848_prefl	30848	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	MEDIUM	生产期覆盖改款前旅行版外廓。	READY
30848_facelift	30848	Wagon	407 I SW		5	EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	MEDIUM	生产期覆盖改款后旅行版外廓。	READY
30849	30849	Wagon	C5 II (X7)	RW	5	EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	HIGH	X7 Tourer五门外廓。	READY
30850	30850	Sedan	C5 II (X7)	RD	4	EU-CITROEN-C5-II-X7-SEDAN-4D-01	HIGH	X7四门轿车外廓。	READY
30851	30851	Hatchback	Caliber	PM	5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH	SRT-4动力不改变该车身外廓组。	READY
30852	30852	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH	第一代五门MPV外廓。	READY
30853	30853	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH	第一代五门MPV外廓。	READY
30854	30854	Sedan	SX4 I	GY	4	EU-SUZUKI-SX4-I-SEDAN-4D-01	HIGH	欧洲版四门轿车外廓。	READY
30857	30857	Hatchback	SX4 I	GY	5	EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	HIGH	四驱五门掀背外廓。	READY
30861	30861	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	HIGH	3.2发动机仅对应五门外廓。	READY
30862_3dr_facelift_2008	30862	SUV	Grand Vitara II	JT	3	EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	MEDIUM	三门2008改款外廓。	READY
30862_3dr_facelift_2012	30862	SUV	Grand Vitara II	JT	3	EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	MEDIUM	三门2012改款外廓。	READY
30862_5dr	30862	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	MEDIUM	五门标准外廓。	READY
30863_prefl	30863	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	MEDIUM	生产期覆盖改款前敞篷外廓。	READY
30863_facelift	30863	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	MEDIUM	生产期覆盖改款后敞篷外廓。	READY
30864	30864	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	E90改款后四门外廓。	READY
30865	30865	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	180 kW车型对应E91改款后外廓。	READY
30866_prefl	30866	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	MEDIUM	生产期覆盖改款前Coupe外廓。	READY
30866_facelift	30866	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	MEDIUM	生产期覆盖改款后Coupe外廓。	READY
30867	30867	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	截止时间位于E92改款前。	READY
30868	30868	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	E90改款后四门xDrive外廓。	READY
30869	30869	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	E91改款后五门xDrive外廓。	READY
30870_prefl	30870	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	MEDIUM	生产期覆盖W204改款前外廓。	READY
30870_facelift	30870	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-FACELIFT-01	MEDIUM	生产期覆盖W204改款后外廓。	READY
30874_prefl	30874	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	MEDIUM	第三代初期四门外廓。	READY
30874_facelift_2012	30874	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	MEDIUM	2012改款四门外廓。	READY
30874_facelift_2015	30874	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2015-01	MEDIUM	2015改款四门外廓。	READY
30875_prefl	30875	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	MEDIUM	第三代初期四门外廓。	READY
30875_facelift_2012	30875	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	MEDIUM	2012改款四门外廓。	READY
30875_facelift_2015	30875	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2015-01	MEDIUM	2015改款四门外廓。	READY
30876_prefl	30876	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	MEDIUM	第三代初期四门外廓。	READY
30876_facelift_2012	30876	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	MEDIUM	2012改款四门外廓。	READY
30876_facelift_2015	30876	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2015-01	MEDIUM	2015改款四门外廓。	READY
30877	30877	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	HIGH	结束时间位于2012改款前。	READY
30878_prefl	30878	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	MEDIUM	第三代初期四门外廓。	READY
30878_facelift_2012	30878	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	MEDIUM	2.2柴油覆盖2012改款外廓。	READY
30879_prefl	30879	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	MEDIUM	第三代初期四门外廓。	READY
30879_facelift_2012	30879	Sedan	Avensis III (T27)	T27	4	EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	MEDIUM	2.2柴油覆盖2012改款外廓。	READY
30880_prefl	30880	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30880_facelift_2012	30880	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2012改款旅行版外廓。	READY
30880_facelift_2015	30880	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2015-01	MEDIUM	2015改款旅行版外廓。	READY
30881_prefl	30881	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30881_facelift_2012	30881	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2012改款旅行版外廓。	READY
30881_facelift_2015	30881	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2015-01	MEDIUM	2015改款旅行版外廓。	READY
30882_prefl	30882	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30882_facelift_2012	30882	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2012改款旅行版外廓。	READY
30882_facelift_2015	30882	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2015-01	MEDIUM	2015改款旅行版外廓。	READY
30883_prefl	30883	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30883_facelift_2012	30883	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2.0柴油覆盖2012改款外廓。	READY
30884_prefl	30884	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30884_facelift_2012	30884	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2.2柴油覆盖2012改款外廓。	READY
30885_prefl	30885	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	MEDIUM	第三代初期旅行版外廓。	READY
30885_facelift_2012	30885	Wagon	Avensis III (T27)	T27	5	EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	MEDIUM	2.2柴油覆盖2012改款外廓。	READY
30886_prefl	30886	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	MEDIUM	生产期覆盖改款前四门外廓。	READY
30886_facelift	30886	Sedan	Insignia A		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	MEDIUM	生产期覆盖改款后四门外廓。	READY
30887	30887	Wagon	Insignia A Sports Tourer		5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	HIGH	结束时间位于改款前。	READY
30888	30888	Sedan	Mazda6 II (GH)	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车标准外廓。	READY
30889	30889	Sedan	Mazda6 II (GH)	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车标准外廓。	READY
30890	30890	Sedan	Mazda6 II (GH)	GH	4	EU-MAZDA-6-II-GH-SEDAN-01	HIGH	GH四门轿车标准外廓。	READY
30891	30891	Hatchback	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	HIGH	GH五门掀背欧洲外廓。	READY
30892	30892	Hatchback	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	HIGH	GH五门掀背欧洲外廓。	READY
30893	30893	Hatchback	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-HATCHBACK-02	HIGH	GH五门掀背欧洲外廓。	READY
30894	30894	Wagon	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH	GH五门旅行版欧洲外廓。	READY
30895	30895	Wagon	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH	GH五门旅行版欧洲外廓。	READY
30896	30896	Wagon	Mazda6 II (GH)	GH	5	EU-MAZDA-6-II-GH-WAGON-5D-02	HIGH	GH五门旅行版欧洲外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3501-3600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LANCIA-2000-TIPO-820-SEDAN-4D-01	4620	1610	1460	Carfolio Lancia 2000 Berlina specifications	https://www.carfolio.com/lancia-2000-berlina-337832
EU-AUDI-A3-8P-HATCHBACK-3D-FACELIFT-01	4238	1765	1421	Auto-Data Audi A3 model specifications	https://www.auto-data.net/en/audi-a3-model-496
EU-AUDI-A3-II-HATCHBACK-5D-FACELIFT-01	4292	1765	1423	Auto-Data Audi A3 model specifications	https://www.auto-data.net/en/audi-a3-model-496
EU-AUDI-Q5-8R-SUV-5D-PREFL-01	4629	1880	1653	Automobile-Catalog 2009 Audi Q5 3.2 FSI quattro	https://www.automobile-catalog.com/car/2009/1192040/audi_q5_3_2_fsi_quattro_s-tronic.html
EU-LANCIA-FULVIA-SERIES-I-SEDAN-4D-01	4110	1555	1400	Automobile-Catalog 1968 Lancia Fulvia 2C Berlina	https://www.automobile-catalog.com/car/1968/1375970/lancia_fulvia_2c_berlina.html
EU-LANCIA-FULVIA-SERIES-II-SEDAN-4D-01	4155	1555	1400	Automobile-Catalog 1970 Lancia Fulvia Berlina	https://www.automobile-catalog.com/car/1970/1376120/lancia_fulvia_berlina.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-STANDARD-2D-01	3975	1555	1300	Automobile-Catalog 1965 Lancia Fulvia Coupe	https://www.automobile-catalog.com/car/1965/1375685/lancia_fulvia_coupe.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-HF-2D-01	3935	1555	1300	Automobile-Catalog 1966 Lancia Fulvia Coupe HF	https://www.automobile-catalog.com/car/1966/1375700/lancia_fulvia_coupe_hf.html
EU-LANCIA-FULVIA-COUPE-SERIES-I-1600-HF-2D-01	3935	1570	1330	Automobile-Catalog Lancia Fulvia Coupe 1.6 HF Variante 1016	https://www.automobile-catalog.com/car/1968/1376270/lancia_fulvia_coupe_1_6_hf_variante_1016.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-13S-2D-01	3975	1555	1320	Automobile-Catalog 1971 Lancia Fulvia Coupe Rallye 1.3 S	https://www.automobile-catalog.com/car/1971/1376135/lancia_fulvia_coupe_rallye_1_3_s.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-2D-01	3935	1570	1330	Automobile-Catalog 1973 Lancia Fulvia Coupe 1600 HF	https://www.automobile-catalog.com/car/1973/1376150/lancia_fulvia_coupe_1600_hf.html
EU-LANCIA-FULVIA-COUPE-SERIES-II-1600-HF-LUSSO-2D-01	3975	1570	1330	Automobile-Catalog 1972 Lancia Fulvia Coupe 1600 HF Lusso	https://www.automobile-catalog.com/car/1972/1376210/lancia_fulvia_coupe_1600_hf_lusso.html
EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	3538	1589	1540	Automobile-Catalog 2006 Fiat Panda 1.3 Multijet 16V Dynamic DPF	https://www.automobile-catalog.com/car/2006/726875/fiat_panda_1_3_multijet_16v_dynamic_dpf.html
EU-IVECO-MASSIF-STATION-WAGON-3D-01	4248	1750	2050	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-STATION-WAGON-5D-01	4720	1750	2050	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-CHASSIS-CAB-2D-01	4445	1750	2000	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-IVECO-MASSIF-PICKUP-2D-01	4548	1750	2000	Iveco Massif official press kit technical specifications	https://www.iveco.com/en-us/press-room/kit/pages/massif_in_detail.aspx
EU-OPEL-ANTARA-A-SUV-01	4576	1850	1704	Vauxhall Antara official brochure April 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/antara/Antara_April_2008.pdf
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699	Automobile-Catalog Porsche Cayenne S Tiptronic S specifications	https://www.automobile-catalog.com/car/2009/2869490/porsche_cayenne_s_tiptronic_s.html
EU-OPEL-ZAFIRA-B-MPV-FACELIFT-01	4467	1801	1635	Opel Zafira B vehicle specifications	https://opel.drive.place/zafira/b_res/group_compactvan/220370
EU-SUZUKI-SX4-S-CROSS-I-HATCHBACK-01	4300	1765	1575	Auto-Data Suzuki SX4 S-Cross 1.6 DDiS ALLGRIP specifications	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-1.6-ddis-120hp-allgrip-19222
EU-CITROEN-EVASION-I-PHASE-II-MPV-5D-01	4454	1812	1710	Automobile-Catalog Citroën Evasion Phase II specifications	https://www.automobile-catalog.com/car/2001/2613410/citroen_evasion_2_1_hdi_x.html
EU-MAZDA-2-DE-HATCHBACK-5D-PREFL-01	3900	1695	1475	Automoli Mazda 2 II DE specifications	https://www.automoli.com/en/vehicles/mazda/2/2-ii-de-2425/
EU-MAZDA-2-DE-HATCHBACK-5D-FACELIFT-01	3920	1695	1475	VehicleSizes Mazda 2 II DE facelift dimensions	https://www.vehiclesizes.com/cars/mazda/2/2-ii-de-facelift-2010-hatchback/
EU-SUBARU-FORESTER-III-SH-SUV-5D-01	4560	1780	1675	Automobile-Catalog 2009 Subaru Forester 2.0 X AWD Europe specifications	https://www.automobile-catalog.com/car/2009/3292085/subaru_forester_2_0_x_awd.html
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475	Auto-Data Subaru Legacy model specifications	https://www.auto-data.net/en/subaru-legacy-model-1844
EU-SUBARU-LEGACY-IV-BL-SEDAN-FACELIFT-4D-01	4665	1730	1425	Automobile-Catalog Subaru Legacy IV sedan specifications	https://www.automobile-catalog.com/car/2004/3263075/subaru_legacy_2_5_i.html
EU-PEUGEOT-3008-I-T84-MPV-5D-01	4365	1837	1628	Automobile-Catalog Peugeot 3008 I specifications	https://www.automobile-catalog.com/car/2011/2626700/peugeot_3008_1_6_hdi_fap_112_110.html
EU-NISSAN-BLUEBIRD-610-SEDAN-4D-01	4215	1600	1405	Nissan Global Heritage Datsun Bluebird U 1600GL	https://www.nissan-global.com/EN/HERITAGE_COLLECTION/bluebird_u_1600gl.html
EU-OPEL-MOVANO-A-BUS-L1H1-01	4899	1990	2253	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-BUS-L2H2-01	5399	1990	2493	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-OPEL-MOVANO-A-BUS-L3H3-01	5899	1990	2720	Vauxhall Movano official brochure December 2008	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/movano/Movano_Dec_2008.pdf
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497	Auto-Data Ford Focus model specifications	https://www.auto-data.net/en/ford-focus-model-795
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500	Auto-Data Ford Focus model specifications	https://www.auto-data.net/en/ford-focus-model-795
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497	Auto-Data Ford Focus model specifications	https://www.auto-data.net/en/ford-focus-model-795
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501	Auto-Data Ford Focus model specifications	https://www.auto-data.net/en/ford-focus-model-795
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503	Auto-Data Ford Focus model specifications	https://www.auto-data.net/en/ford-focus-model-795
EU-FORD-FOCUS-II-RS-HATCHBACK-3D-01	4402	1842	1484	Ford Focus RS official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/04/Ford-Focus-RS-2008-UK.pdf
EU-PORSCHE-944-951-TURBO-CONVERTIBLE-2D-01	4230	1735	1275	Porsche 944 Turbo Cabriolet factory technical data	https://www.no-speedlimit.it/Porsche_Werkfoto_1991_944.html
EU-FORD-KA-II-RU8-HATCHBACK-3D-01	3620	1658	1505	Ford Ka official brochure	https://www.bluelightcars.co.uk/wp-content/uploads/Ford-Brochure-KA.pdf
EU-FORD-FIESTA-VII-CB1-HATCHBACK-01	3950	1709	1481	Automobile-Catalog Ford Fiesta 1.4 TDCi Europe specifications	https://www.automobile-catalog.com/car/2009/979970/ford_fiesta_1_4_tdci_style.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.2 specifications	https://www.auto-data.net/en/hyundai-i10-i-1.2-78hp-13881
EU-MERCEDES-BENZ-B-CLASS-W245-NGT-HATCHBACK-5D-01	4273	1777	1624	Mercedes-Benz Public Archive B 170 NGT BlueEFFICIENCY	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/B-170-NGT-BlueEFFICIENCY-2008---2009.xhtml?oid=192213159
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496	Auto-Data Saab 9-3 Sport Combi II facelift specifications	https://www.auto-data.net/en/saab-9-3-sport-combi-ii-facelift-2007-2.8t-v6-280hp-42457
EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	3785	1695	1530	Auto-Data Toyota Yaris II generation specifications	https://www.auto-data.net/en/toyota-yaris-ii-generation-1051
EU-PEUGEOT-308-I-HATCHBACK-5D-01	4276	1815	1498	Auto-Data Peugeot 308 I Phase I specifications	https://www.auto-data.net/en/peugeot-308-i-phase-i-2007-1.6-16v-thp-175hp-42012
EU-PEUGEOT-308-SW-I-PHASE-I-WAGON-5D-01	4500	1815	1564	Auto-Data Peugeot 308 SW I Phase I specifications	https://www.auto-data.net/en/peugeot-308-sw-i-phase-i-2008-generation-1238
EU-PEUGEOT-407-I-SW-WAGON-PREFL-01	4763	1811	1486	Auto-Data Peugeot 407 SW Phase I specifications	https://www.auto-data.net/en/peugeot-407-sw-phase-i-2004-generation-1239
EU-PEUGEOT-407-I-SW-WAGON-FACELIFT-01	4763	1811	1460	Auto-Data Peugeot 407 SW Phase II specifications	https://www.auto-data.net/en/peugeot-407-sw-phase-ii-2008-generation-11259
EU-CITROEN-C5-II-X7-TOURER-WAGON-5D-01	4829	1860	1479	CarsGuide Citroën C5 Tourer dimensions	https://www.carsguide.com.au/citroen/c5/car-dimensions/2012?id=CJTM0YkT
EU-CITROEN-C5-II-X7-SEDAN-4D-01	4779	1860	1451	AutomobileDimension Citroën C5 dimensions	https://www.automobiledimension.com/model/citroen/c5
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535	Automobile-Catalog 2008 Dodge Caliber Europe specifications	https://www.automobile-catalog.com/car/2008/690890/dodge_caliber_s_1_8l.html
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691	Automobile-Catalog 2009 Dodge Journey SE Europe specifications	https://www.automobile-catalog.com/car/2009/691565/dodge_journey_se_2_4l.html
EU-SUZUKI-SX4-I-SEDAN-4D-01	4490	1730	1545	Automobile-Catalog 2008 Suzuki SX4 Sedan 1.6 VVT Europe specifications	https://www.automobile-catalog.com/car/2008/3408965/suzuki_sx4_sedan_1_6_vvt_2wd.html
EU-SUZUKI-SX4-I-HATCHBACK-4X4-01	4140	1755	1620	Auto-Data Suzuki SX4 model specifications	https://www.auto-data.net/en/suzuki-sx4-model-1911
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695	Auto-Data Suzuki Grand Vitara model specifications	https://www.auto-data.net/en/suzuki-grand-vitara-model-1445
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695	Auto-Data Suzuki Grand Vitara model specifications	https://www.auto-data.net/en/suzuki-grand-vitara-model-1445
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695	Auto-Data Suzuki Grand Vitara model specifications	https://www.auto-data.net/en/suzuki-grand-vitara-model-1445
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4588	1782	1384	Auto-Data BMW 3 Series model specifications	https://www.auto-data.net/en/bmw-3-series-model-953
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384	Auto-Data BMW 3 Series E93 LCI specifications	https://www.auto-data.net/en/bmw-3-series-convertible-e93-lci-facelift-2010-325i-218hp-steptronic-20755
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	Auto-Data BMW 3 Series E90 LCI specifications	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-330i-272hp-xdrive-steptronic-27561
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series E91 LCI specifications	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-318d-143hp-27580
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	Auto-Data BMW 3 Series model specifications	https://www.auto-data.net/en/bmw-3-series-model-953
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data BMW 3 Series E92 LCI specifications	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-320d-184hp-xdrive-steptronic-20724
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01	4581	1770	1444	Automobile-Catalog 2009 Mercedes-Benz C 250 CDI BlueEFFICIENCY	https://www.automobile-catalog.com/car/2009/1550765/mercedes-benz_c_250_cdi_blueefficiency.html
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-FACELIFT-01	4591	1770	1447	Automobile-Catalog 2012 Mercedes-Benz C 250 CDI BlueEFFICIENCY	https://www.automobile-catalog.com/car/2012/1551575/mercedes-benz_c_250_cdi_blueefficiency_7g-tronic.html
EU-TOYOTA-AVENSIS-III-T27-SEDAN-PREFL-01	4695	1810	1480	Toyota Avensis official brochure 2009	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Avensis-2009-UK.pdf
EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2012-01	4710	1810	1480	Automoli Toyota Avensis III facelift 2012 sedan specifications	https://www.automoli.com/en/vehicles/toyota/avensis/avensis-iii-facelift-2012-4083/
EU-TOYOTA-AVENSIS-III-T27-SEDAN-FACELIFT-2015-01	4750	1810	1480	Toyota UK Media new Toyota Avensis 2015 specifications	https://media.toyota.co.uk/new-toyota-avensis/
EU-TOYOTA-AVENSIS-III-T27-WAGON-PREFL-01	4765	1810	1480	Toyota Avensis official brochure 2009	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Avensis-2009-UK.pdf
EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2012-01	4780	1810	1480	Automoli Toyota Avensis III wagon facelift 2012 specifications	https://www.automoli.com/en/vehicles/toyota/avensis/avensis-iii-wagon-facelift-2012-4084/
EU-TOYOTA-AVENSIS-III-T27-WAGON-FACELIFT-2015-01	4820	1810	1480	Toyota UK Media new Toyota Avensis 2015 specifications	https://media.toyota.co.uk/new-toyota-avensis/
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data Opel Insignia model specifications	https://www.auto-data.net/en/opel-insignia-model-1408
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	Auto-Data Opel Insignia model specifications	https://www.auto-data.net/en/opel-insignia-model-1408
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520	Auto-Data Opel Insignia model specifications	https://www.auto-data.net/en/opel-insignia-model-1408
EU-MAZDA-6-II-GH-SEDAN-01	4755	1795	1440	Mazda6 official brochure 2008	https://autocatalogarchive.com/wp-content/uploads/2017/04/Mazda-6-2008-UK.pdf
EU-MAZDA-6-II-GH-HATCHBACK-02	4755	1795	1440	Mazda6 official brochure 2008	https://autocatalogarchive.com/wp-content/uploads/2017/04/Mazda-6-2008-UK.pdf
EU-MAZDA-6-II-GH-WAGON-5D-02	4785	1795	1490	Mazda6 official brochure 2008	https://autocatalogarchive.com/wp-content/uploads/2017/04/Mazda-6-2008-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3501-3600_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3501-3600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3501-3600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4414 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2056 行）

- 尺寸冲突协调：
  - EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-01 -> EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-4D-PREFL-02：4581x1770x1447 与 4581x1770x1444，创建新尺寸组
