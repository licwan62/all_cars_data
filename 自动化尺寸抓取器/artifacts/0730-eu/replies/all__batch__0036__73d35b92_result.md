# 任务：all 第 3501-3600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0036__73d35b92


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
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-Q2-GA-SUV-01	4191	1794	1508
EU-AUDI-R8-4S-RWS-COUPE-01	4426	1940	1240
EU-AUDI-R8-4S-RWS-SPYDER-CONVERTIBLE-01	4426	1940	1245
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-CHEVROLET-CAPTIVA-I-FACELIFT-SUV-01	4673	1849	1727
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-DACIA-LODGY-MPV-01	4498	1751	1679
EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-VAN-FACELIFT-01	4450	1740	1640
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-FACELIFT-01	4382	1825	1471
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-KIA-CERATO-IV-BD-SEDAN-01	4640	1800	1450
EU-KIA-OPTIMA-III-TF-SEDAN-01	4845	1830	1455
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-OPTIMA-JF-WAGON-01	4855	1860	1470
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400
EU-LADA-VESTA-I-SEDAN-01	4410	1764	1497
EU-LADA-VESTA-I-SW-CROSS-WAGON-01	4424	1785	1537
EU-LADA-VESTA-I-SW-WAGON-01	4410	1764	1512
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-PREFL-01	4803	1930	1665
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-G-KLASSE-W460-CONVERTIBLE-SWB-01	4145	1700	2000
EU-MERCEDES-BENZ-G-KLASSE-W463-CONVERTIBLE-SWB-01	4185	1690	1967
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	4696	1923	1624
EU-PORSCHE-MACAN-95B-TURBO-PERFORMANCE-SUV-01	4691	1933	1600
EU-RENAULT-CLIO-IV-GRANDTOUR-PHASE-II-WAGON-01	4267	1732	1475
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-RS-HATCHBACK-01	4372	1874	1435
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457
EU-RENAULT-TALISMAN-I-SEDAN-01	4849	1868	1456
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603
EU-SKODA-KODIAQ-I-RS-SUV-PREFL-01	4699	1882	1686
EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	4697	1882	1661
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-V-6R-VAN-3D-PREFL-01	3970	1682	1484
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Talisman	2.0 Blue DCI 200	Kombi	Frontantrieb	Diesel	147	200	Jan 2019	Mar 2022	2024-03-01	135073
Audi	A6 c8	45 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	180	245	Aug 2018	-	2024-03-01	135106
BMW	X4	Xdrive M40 I	SUV	Allrad	Benzin	265	360	Apr 2018	-	2024-03-01	135107
Audi	A6 c8	45 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	180	245	Aug 2018	-	2024-03-01	135108
Audi	A6 c8 avant	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	180	245	Aug 2018	-	2024-03-01	135112
Audi	A6 c8 avant	45 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	180	245	Aug 2018	-	2024-03-01	135113
VW	Crafter	2.0 TDI RWD	Kasten	Heckantrieb	Diesel	80	109	May 2017	Jun 2024	2024-05-01	135117
VW	Crafter	2.0 TDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	80	109	Nov 2016	Jun 2024	2024-05-01	135129
Audi	A1	25 Tfsi	Schrägheck	Frontantrieb	Benzin	70	95	Nov 2018	-	2024-03-01	135143
Audi	A1	35 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2018	-	2024-03-01	135144
Audi	A1	40 Tfsi	Schrägheck	Frontantrieb	Benzin	147	200	Sep 2018	-	2024-03-01	135145
VW	Sharan	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	130	177	Jul 2018	Oct 2020	2024-03-01	135146
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	169	230	Sep 2018	Jul 2020	2024-03-01	135157
Land Rover	Range rover iv	2.0 P400e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	297	404	Oct 2017	Sep 2021	2025-02-03	135158
VW	Polo	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Oct 2018	Aug 2021	2024-03-01	135159
KIA	Cerato iv	1.6 TCI	Stufenheck	Frontantrieb	Diesel	100	136	Nov 2018	-	2024-03-01	135160
Land Rover	Range rover sport ii	2.0 P400e Phev 4X4	SUV	Allrad	Benzin/Elektro	297	404	Oct 2017	Mar 2022	2025-02-03	135161
Porsche	911	3.0 Carrera S	Coupe	Heckantrieb	Benzin	331	450	Jan 2019	Dec 2024	2026-03-01	135162
Porsche	911	3.0 Carrera 4 S	Coupe	Allrad	Benzin	331	450	Jan 2019	Dec 2024	2026-03-01	135165
Porsche	911	3.0 Carrera S	Cabriolet	Heckantrieb	Benzin	331	450	Jan 2019	Dec 2024	2026-03-01	135166
Porsche	911	3.0 Carrera 4 S	Cabriolet	Allrad	Benzin	331	450	Jan 2019	Dec 2024	2026-03-01	135167
Audi	Q2	SQ2 Tfsi Quattro	SUV	Allrad	Benzin	221	300	Aug 2018	-	2024-03-01	135168
Audi	A5	35 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Aug 2018	-	2024-03-01	135169
Audi	A5	45 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	Feb 2020	2024-03-01	135170
Audi	A5	45 Tfsi Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	Dec 2019	2024-03-01	135171
Audi	A5	45 Tfsi Mild Hybrid Quattro	Cabriolet	Allrad	Benzin/Elektro	180	245	Jul 2018	-	2026-07-01	135172
Audi	A5	45 Tfsi Mild Hybrid	Coupe	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	Aug 2020	2024-03-01	135173
Audi	A5	45 Tfsi Mild Hybrid Quattro	Coupe	Allrad	Benzin/Elektro	180	245	Jul 2018	Aug 2020	2024-03-01	135174
Audi	A4 b9	45 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	Nov 2019	2024-03-01	135175
Audi	A4 b9	45 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	180	245	Jul 2018	Aug 2020	2026-07-01	135176
Audi	A4 b9 avant	45 Tfsi Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	180	245	Jul 2018	Oct 2019	2024-03-01	135177
Audi	A4 b9 avant	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	180	245	Jul 2018	Aug 2020	2026-07-01	135178
Mercedes-benz	G-Klasse	G 350 D 4-matic	Geländewagen geschlossen	Allrad	Diesel	210	286	Jan 2019	Nov 2022	2024-03-01	135197
Lada	Vesta	1.8 Sport	Stufenheck	Frontantrieb	Benzin	107	145	Feb 2019	-	2024-03-01	135254
MPM Motors	Erelis	1.2 T	Coupe	Frontantrieb	Benzin	96	131	Nov 2018	-	2024-03-01	135255
Renault	Megane iv	1.8 Blue DCI 150	Schrägheck	Frontantrieb	Diesel	110	150	Feb 2019	-	2024-03-01	135256
Renault	Megane iv grandtour	1.8 Blue DCI 150	Kombi	Frontantrieb	Diesel	110	150	Feb 2019	-	2024-03-01	135257
Renault	Megane iv	1.5 Blue DCI 95	Stufenheck	Frontantrieb	Diesel	70	95	Feb 2019	-	2024-03-01	135260
Renault	Megane iv	1.5 Blue DCI 115	Stufenheck	Frontantrieb	Diesel	85	115	Feb 2019	-	2024-03-01	135261
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	70	95	Aug 2018	-	2024-03-01	135269
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	100	136	Aug 2018	-	2024-03-01	135270
KIA	Stinger	3.3 T-gdi	Schrägheck	Heckantrieb	Benzin	269	366	Jul 2018	Dec 2023	2026-04-01	135272
Porsche	Macan	3.0 S	SUV	Allrad	Benzin	260	354	May 2018	-	2024-03-01	135274
Audi	A5	35 Tfsi Mild Hybrid	Coupe	Frontantrieb	Benzin/Elektro	110	150	Feb 2019	-	2024-03-01	135275
Dacia	Lodgy	1.5 Blue DCI 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	135282
Dacia	Lodgy	1.5 Blue DCI 95	Großraumlimousine	Frontantrieb	Diesel	70	95	Aug 2018	-	2024-03-01	135283
Renault	Megane iv	1.3 TCE 160	Schrägheck	Frontantrieb	Benzin	117	159	Nov 2018	-	2024-03-01	135288
Dacia	Logan	1.5 Blue DCI 95	Kombi	Frontantrieb	Diesel	70	95	Oct 2018	-	2024-03-01	135289
Dacia	Dokker	1.5 Blue DCI 95	Großraumlimousine	Frontantrieb	Diesel	70	95	Dec 2018	Dec 2021	2024-11-01	135290
Dacia	Duster	1.3 TCE 130	SUV	Frontantrieb	Benzin	96	131	Jan 2019	-	2024-03-01	135291
Dacia	Duster	1.3 TCE 150	SUV	Frontantrieb	Benzin	110	150	Jan 2019	-	2024-03-01	135292
Chevrolet	Silverado 1500 crew cab pickup	6.2 4WD	Pick-up	Allrad	Benzin	313	426	Aug 2018	-	2025-11-01	135306
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	94	128	Aug 2018	-	2024-03-01	135309
KIA	Optima	2.0 T-gdi	Stufenheck	Frontantrieb	Benzin	175	238	Jun 2018	Dec 2019	2024-03-01	135310
Skoda	Karoq	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Jul 2017	-	2024-03-01	135315
Skoda	Kodiaq i	2.0 TSI 4X4	SUV	Allrad	Benzin	140	190	Feb 2019	-	2024-05-01	135316
Skoda	Octavia	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	140	190	Feb 2019	Oct 2020	2024-03-01	135317
Skoda	Octavia	2.0 TSI 4X4	Kombi	Allrad	Benzin	140	190	Feb 2019	Oct 2020	2024-03-01	135318
Mercedes-benz	B-Klasse sports tourer	B 220 4-matic	Schrägheck	Allrad	Benzin	140	190	Jan 2019	-	2024-03-01	135320
Mercedes-benz	B-Klasse sports tourer	B 250	Schrägheck	Frontantrieb	Benzin	165	224	Jan 2019	-	2024-03-01	135323
Mercedes-benz	B-Klasse sports tourer	B 250 4-matic	Schrägheck	Allrad	Benzin	165	224	Jan 2019	-	2024-03-01	135324
Land Rover	Range rover velar	5.0 Scv8 4X4	SUV	Allrad	Benzin	405	551	Jan 2019	-	2024-03-01	135328
Renault	Clio iv	1.5 DCI	Schrägheck	Frontantrieb	Diesel	63	86	Nov 2012	Aug 2021	2026-05-01	135334
Peugeot	Partner tepee	Électrique	Großraumlimousine	Frontantrieb	Elektro	49	67	Jun 2013	-	2024-03-01	135338
KIA	Soul iii	E-soul	Schrägheck	Frontantrieb	Elektro	150	204	Jan 2019	-	2024-03-01	135339
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	456	620	Sep 2018	-	2024-03-01	135340
Skoda	Scala	1.0 TSI	Schrägheck	Frontantrieb	Benzin	85	116	Feb 2019	-	2024-03-01	135341
Skoda	Scala	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Feb 2019	-	2024-03-01	135342
Skoda	Scala	1.6 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Feb 2019	-	2024-03-01	135343
Toyota	Yaris	1.5 Vvti	Kasten/Schrägheck	Frontantrieb	Benzin	82	111	Mar 2017	Jun 2020	2024-05-01	135345
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	456	620	Sep 2018	-	2024-03-01	135347
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	419	570	Sep 2018	-	2024-03-01	135348
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	419	570	Sep 2018	-	2024-03-01	135349
Audi	A5	RS5 Tfsi Quattro	Schrägheck	Allrad	Benzin	331	450	Jun 2018	-	2025-11-01	135352
BMW	X3	M	SUV	Allrad	Benzin	353	480	Mar 2019	-	2024-03-01	135353
BMW	X3	M Competition	SUV	Allrad	Benzin	375	510	Mar 2019	-	2024-03-01	135354
BMW	X4	M	SUV	Allrad	Benzin	353	480	Mar 2019	-	2024-03-01	135355
BMW	X4	M Competition	SUV	Allrad	Benzin	375	510	Mar 2019	-	2024-03-01	135356
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	140	190	Sep 2018	Nov 2022	2025-12-01	135357
VW	Touran	1.0 TSI	Großraumlimousine	Frontantrieb	Benzin	85	116	Dec 2018	Jul 2019	2025-11-01	135359
KIA	K9 ii	3.3 GDI	Stufenheck	Heckantrieb	Benzin	183	249	Feb 2019	-	2024-03-01	135361
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	190	258	Feb 2019	Oct 2023	2024-08-01	135362
KIA	K9 ii	3.3 GDI AWD	Stufenheck	Allrad	Benzin	183	249	Feb 2019	-	2024-03-01	135364
VW	Golf vii variant	1.5 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Dec 2018	Aug 2020	2024-03-01	135365
KIA	K9 ii	5.0 GDI AWD	Stufenheck	Allrad	Benzin	304	413	Mar 2018	-	2024-03-01	135366
Ford	Mondeo v	2.0 Ecoblue	Schrägheck	Frontantrieb	Diesel	88	120	Jan 2019	Mar 2022	2026-04-01	135367
Ford	Mondeo v	2.0 Ecoblue	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2019	Mar 2022	2026-04-01	135369
Ford	Mondeo v	2.0 Ecoblue	Schrägheck	Frontantrieb	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	135370
Ford	Mondeo v	2.0 Ecoblue 4X4	Schrägheck	Allrad	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	135371
Ford	Mondeo v turnier	2.0 Ecoblue	Kombi	Frontantrieb	Diesel	88	120	Jan 2019	Mar 2022	2026-04-01	135372
Ford	Mondeo v turnier	2.0 Ecoblue	Kombi	Frontantrieb	Diesel	110	150	Jan 2019	Mar 2022	2026-04-01	135373
Ford	Mondeo v turnier	2.0 Ecoblue	Kombi	Frontantrieb	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	135374
Ford	Mondeo v turnier	2.0 Ecoblue 4X4	Kombi	Allrad	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	135375
Renault	Megane iv grandtour	1.3 TCE 160	Kombi	Frontantrieb	Benzin	117	159	Jul 2018	-	2024-03-01	135394
Chevrolet	Captiva	2.4	SUV	Frontantrieb	Benzin	100	136	Jan 2007	-	2024-03-01	135425
Austin	Allegro i	1.3	Stufenheck	Frontantrieb	Benzin	43	58	Dec 1979	Dec 1984	2024-03-01	135458
Ford	Focus iv	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	74	101	Nov 2018	Nov 2025	2026-02-01	135550
Ford	Focus iv	1.0 Ecoboost	Stufenheck	Frontantrieb	Benzin	92	125	Nov 2018	Nov 2025	2026-02-01	135552
Ford	Focus iv	1.5 Ecoboost	Stufenheck	Frontantrieb	Benzin	110	150	Nov 2018	Nov 2025	2026-02-01	135557
Ford	Focus iv	1.5 Ecoblue	Stufenheck	Frontantrieb	Diesel	70	95	Nov 2018	Nov 2025	2026-02-01	135558


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类处理本批 100 个 Ktype，优先复用跨批次既有尺寸组。
* 已将跨越明确改款边界的 `135334` 和 4 个 Focus Ktype 拆分为稳定派生行，不保留无后缀基础行。
* 本轮首次闭合 13 个尺寸组，包括避免错误复用。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：105
* READY 映射：80
* PENDING 映射：25
* 已完全 READY 的 Ktype：75
* 尚有 PENDING 的 Ktype：25
* READY 映射当前引用尺寸组：49
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135073	135073	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
135106	135106	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
135107	135107	SUV	X4 G02	G02	5	EU-BMW-X4-G02-M40I-SUV-01	HIGH		READY
135108	135108	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
135112	135112	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
135113	135113	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
135117	135117	Van	Crafter II				LOW	需确认该Ktype覆盖的车长与车顶分支。	PENDING: 长度/车顶分支未闭合
135129	135129	Pickup	Crafter II				LOW	需确认单排/双排驾驶室及底盘长度分支。	PENDING: 驾驶室/长度分支未闭合
135143	135143	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135144	135144	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135145	135145	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135146	135146	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-FACELIFT-01	HIGH		READY
135157	135157	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH		READY
135158	135158	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	MEDIUM	P400e标准轴距外廓。	READY
135159	135159	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH		READY
135160	135160	Sedan	Cerato IV	BD	4	EU-KIA-CERATO-IV-BD-SEDAN-01	HIGH		READY
135161	135161	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH		READY
135162	135162	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-COUPE-01	HIGH		READY
135165	135165	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-COUPE-01	HIGH		READY
135166	135166	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	HIGH		READY
135167	135167	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	HIGH		READY
135168	135168	SUV	Q2 GA	GA	5		MEDIUM	SQ2外廓与普通Q2不同，候选新尺寸组待闭合。	PENDING: SQ2三维未闭合
135169	135169	Hatchback	A5 F5	F5A	5		MEDIUM	需确认该Ktype是否仅覆盖改款前Sportback。	PENDING: 改款边界未闭合
135170	135170	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前Sportback外廓。	READY
135171	135171	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	MEDIUM	改款前Cabriolet外廓。	READY
135172	135172	Convertible	A5 F5	F57	2		MEDIUM	需确认该Ktype是否跨越改款外廓。	PENDING: 改款边界未闭合
135173	135173	Coupe	A5 F5	F53	2		MEDIUM	需确认该Ktype是否跨越改款外廓。	PENDING: 改款边界未闭合
135174	135174	Coupe	A5 F5	F53	2		MEDIUM	需确认该Ktype是否跨越改款外廓。	PENDING: 改款边界未闭合
135175	135175	Sedan	A4 B9	8W2	4		MEDIUM	需确认该Ktype的改款前后物理边界。	PENDING: 改款边界未闭合
135176	135176	Sedan	A4 B9	8W2	4		MEDIUM	需确认该Ktype的改款前后物理边界。	PENDING: 改款边界未闭合
135177	135177	Wagon	A4 B9	8W5	5		MEDIUM	需确认该Ktype的改款前后物理边界。	PENDING: 改款边界未闭合
135178	135178	Wagon	A4 B9	8W5	5		MEDIUM	需确认该Ktype的改款前后物理边界。	PENDING: 改款边界未闭合
135197	135197	SUV	G-Class W463 II	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	MEDIUM	封闭式五门车身。	READY
135254	135254	Sedan	Vesta I		4		MEDIUM	Sport版保险杠与车高需独立闭合。	PENDING: Sport外廓三维未闭合
135255	135255	Coupe	Erelis		2		LOW	小众车型车身代码及不含镜宽度待核对。	PENDING: 三维与车身代码未闭合
135256	135256	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
135257	135257	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
135260	135260	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
135261	135261	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
135269	135269	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
135270	135270	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
135272	135272	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
135274	135274	SUV	Macan 95B	95B	5		MEDIUM	需确认Macan S与既有facelift base组三维完全一致。	PENDING: Macan S与既有facelift base组外廓边界待确认
135275	135275	Coupe	A5 F5	F53	2		MEDIUM	需确认该Ktype是否仅覆盖改款前Coupe。	PENDING: 改款边界未闭合
135282	135282	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
135283	135283	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
135288	135288	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
135289	135289	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
135290	135290	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
135291	135291	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
135292	135292	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
135306	135306	Pickup	Silverado 1500 IV	T1XX	4		LOW	Crew Cab货斗长度分支尚未确认。	PENDING: CAB/BED外廓未闭合
135309	135309	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
135310	135310	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
135315	135315	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	HIGH		READY
135316	135316	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH		READY
135317	135317	Hatchback	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH		READY
135318	135318	Wagon	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
135320	135320	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135323	135323	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135324	135324	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135328	135328	SUV	Range Rover Velar	L560	5		MEDIUM	SVAutobiography Dynamic专属保险杠/高度待闭合。	PENDING: 特殊外部套件三维未闭合
135334_prefl	135334	Hatchback	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	HIGH	Ktype覆盖改款前外廓。	READY
135334_facelift	135334	Hatchback	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	Ktype覆盖改款后外廓。	READY
135338	135338	MPV	Partner II	B9	5		LOW	电动Tepee标准车身三维与宽度口径待闭合。	PENDING: 三维未闭合
135339	135339	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	HIGH		READY
135340	135340	Convertible	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	HIGH		READY
135341	135341	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135342	135342	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135343	135343	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135345	135345	Van	Yaris III	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH		READY
135347	135347	Coupe	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	HIGH		READY
135348	135348	Coupe	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	HIGH		READY
135349	135349	Convertible	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	HIGH		READY
135352	135352	Hatchback	RS5 F5	F5	5		MEDIUM	RS5 Sportback宽体外廓待独立闭合。	PENDING: 宽体三维未闭合
135353	135353	SUV	X3 M F97	F97	5	EU-BMW-X3-F97-M-SUV-01	HIGH		READY
135354	135354	SUV	X3 M F97	F97	5	EU-BMW-X3-F97-M-COMPETITION-SUV-01	HIGH		READY
135355	135355	SUV	X4 M F98	F98	5	EU-BMW-X4-F98-M-SUV-01	HIGH		READY
135356	135356	SUV	X4 M F98	F98	5	EU-BMW-X4-F98-M-COMPETITION-SUV-01	HIGH		READY
135357	135357	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH		READY
135359	135359	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH		READY
135361	135361	Sedan	K9 II	RJ	4		LOW	K9 II欧洲外廓与不含镜宽度待闭合。	PENDING: 三维未闭合
135362	135362	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
135364	135364	Sedan	K9 II	RJ	4		LOW	K9 II欧洲外廓与不含镜宽度待闭合。	PENDING: 三维未闭合
135365	135365	Wagon	Golf VII	5G	5		MEDIUM	Variant TGI车高与标准Variant外廓待闭合。	PENDING: 三维未闭合
135366	135366	Sedan	K9 II	RJ	4		LOW	K9 II欧洲外廓与不含镜宽度待闭合。	PENDING: 三维未闭合
135367	135367	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135369	135369	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135370	135370	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135371	135371	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135372	135372	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135373	135373	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135374	135374	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135375	135375	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135394	135394	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
135425	135425	SUV	Captiva I	C100	5		LOW	Ktype可能跨越改款，改款前外廓尚未闭合。	PENDING: 改款分支未闭合
135458	135458	Sedan	Allegro		4		LOW	输入代际名与1979-1984生产期冲突，需先确认Series边界。	PENDING: 代际与三维未闭合
135550_prefl	135550	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135550_facelift	135550	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135552_prefl	135552	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135552_facelift	135552	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135557_prefl	135557	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135557_facelift	135557	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135558_prefl	135558	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135558_facelift	135558	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SHARAN-II-7N-MPV-FACELIFT-01	4854	1904	1720	Volkswagen UK Sharan brochure November 2018	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/sharan/sharan-fl/vw_sharan_brochure_nov_2018.pdf
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300	Porsche 2020 911 Carrera S and Carrera 4S technical data	https://newsroom.porsche.com/dam/jcr%3Ad5712d5c-b376-41d9-8201-09731162e143/2020_911_Carrera_S_and_911_Carrera_4S_US_specifications.pdf
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299	Porsche 2020 911 Carrera S Cabriolet and Carrera 4S Cabriolet technical data	https://newsroom.porsche.com/dam/jcr%3A1bb7bc77-6925-4e3c-ab03-0fc6065260fb/PCNA19_0038_us.pdf
EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	4825	1931	1969	Automobile-Catalog 2019 Mercedes-Benz G 350 d	https://www.automobile-catalog.com/car/2019/2875145/mercedes-benz_g_350_d.html
EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	4419	1796	1562	Automobile-Catalog 2019 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2019/2967260/mercedes-benz_b_220_4matic.html
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605	Kia Europe e-Soul 2019 press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/e-Soul/Kia%20e-Soul%20-%202019%20-%20Final%20-%205%20Apr%202019.doc
EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	4429	1940	1242	Audi MediaCenter R8 Spyder V10 performance quattro dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-r8-spyder-performance-1449/download
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471	ŠKODA SCALA petrol/diesel technical specifications	https://cdn.skoda-storyboard.com/2019/04/TD-SCALA-petrol-diesel-en.pdf
EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	4429	1940	1236	Audi MediaCenter R8 Coupé V10 performance quattro dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-r8-coupe-performance-1448/download
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667	BMW Group Specifications The new BMW X3 M	https://www.press.bmwgroup.com/france/article/attachment/T0291683FR/424502
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669	BMW Group Specifications The new BMW X3 M	https://www.press.bmwgroup.com/france/article/attachment/T0291683FR/424502
EU-BMW-X4-F98-M-SUV-01	4758	1927	1618	BMW Group Specifications The new BMW X4 M	https://www.press.bmwgroup.com/belux/article/attachment/T0291892FR/424631
EU-BMW-X4-F98-M-COMPETITION-SUV-01	4758	1927	1620	BMW Group Specifications The new BMW X4 M	https://www.press.bmwgroup.com/belux/article/attachment/T0291892FR/424631
```

## 下一步优先处理

1. 集中闭合 Audi A4/A5 改款边界，并同时处理 SQ2、RS5 Sportback、Macan S 和 Velar SVAutobiography Dynamic。
2. 按配置矩阵处理 Crafter 厢式车/底盘驾驶室，以及 Silverado Crew Cab 的货斗长度分支。
3. 补齐 Partner Electric、Vesta Sport、Erelis、K9 II、Golf Variant TGI、Captiva 与 Allegro 的三维和不含后视镜宽度口径。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮消除 21 个 Ktype 的 PENDING，其中 9 个跨越明确改款边界的 Ktype 拆分为 `prefl`、`facelift` 两条派生映射。Audi A4、A5 改款前后外廓已分别关联既有组或新建组。
* 首次创建并闭合 11 个尺寸组；Macan S 复用已有 `EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01`，A5 改款组及 A4 改款前组直接复用缓存。
* Vesta Sport、K9 II、Golf Variant TGI、Captiva 改款前等尺寸已闭合。
* 当前仅剩 4 个 PENDING：`135117`、`135129`、`135306`、`135352`。Crafter 输入功率与第二代公开发动机序列不一致；RS5 Sportback 的高度来源存在 `1387 mm` 与 `1399 mm` 冲突，暂不创建尺寸组。([维基百科][1])

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：114
* READY 映射：110
* PENDING 映射：4
* 已完全 READY 的 Ktype：96
* 尚有 PENDING 的 Ktype：4
* READY 映射当前引用尺寸组：67
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135168	135168	SUV	Q2 GA	GA	5	EU-AUDI-SQ2-GA-SUV-PREFL-01	HIGH		READY
135169_prefl	135169	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135169_facelift	135169	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135172_prefl	135172	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135172_facelift	135172	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135173_prefl	135173	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135173_facelift	135173	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135174_prefl	135174	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135174_facelift	135174	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135175_prefl	135175	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135175_facelift	135175	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135176_prefl	135176	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135176_facelift	135176	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135177_prefl	135177	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135177_facelift	135177	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135178_prefl	135178	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135178_facelift	135178	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135254	135254	Sedan	Vesta I		4	EU-LADA-VESTA-I-SPORT-SEDAN-01	HIGH		READY
135255	135255	Coupe	Erelis		4	EU-MPM-MOTORS-ERELIS-COUPE-01	MEDIUM	四门Coupe外廓。	READY
135274	135274	SUV	Macan 95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	HIGH		READY
135275_prefl	135275	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135275_facelift	135275	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135328	135328	SUV	Range Rover Velar	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SVAUTOBIOGRAPHY-DYNAMIC-SUV-01	HIGH		READY
135338	135338	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	MEDIUM		READY
135361	135361	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135364	135364	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135365	135365	Wagon	Golf VII	5G	5	EU-VW-GOLF-VII-5G-VARIANT-TGI-WAGON-01	HIGH		READY
135366	135366	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135425	135425	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	HIGH		READY
135458	135458	Sedan	Allegro III	ADO67	4	EU-AUSTIN-ALLEGRO-III-ADO67-SEDAN-01	MEDIUM	输入结束月晚于车型实际停产期，按Allegro III 1.3外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-SQ2-GA-SUV-PREFL-01	4210	1802	1495	Auto-Data Audi SQ2 2.0 TFSI quattro	https://www.auto-data.net/en/audi-sq2-2.0-tfsi-300hp-quattro-s-tronic-35095
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431	Audi MediaCenter The Audi A4 Major Upgrade for the Bestseller	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460	Audi MediaCenter The Audi A4 Major Upgrade for the Bestseller	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-LADA-VESTA-I-SPORT-SEDAN-01	4420	1774	1478	LADA Vesta Sport official technical specifications	https://minsk-lada.by/upload/iblock/600/%D0%A2%D0%B5%D1%85%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5%20%D1%85%D0%B0%D1%80%D0%B0%D0%BA%D1%82%D0%B5%D1%80%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B8%20-%20LADA%20Vesta%20Sport%20-%20LADA.pdf
EU-MPM-MOTORS-ERELIS-COUPE-01	4684	1860	1383	Carfolio 2018 MPM Erelis 1.2T	https://www.carfolio.com/mpm-erelis-1.2t-564707
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SVAUTOBIOGRAPHY-DYNAMIC-SUV-01	4806	1940	1665	Automobile-Catalog 2019 Range Rover Velar SVAutobiography Dynamic Edition	https://www.automobile-catalog.com/car/2019/2875910/range_rover_velar_svautobiography_dynamic_edition.html
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862	Peugeot Partner Tepee handbook; Auto-Data Peugeot Partner II Tepee Electric	https://www.kemwel.com/peugeot-fleet/documents/partner.pdf; https://www.auto-data.net/en/peugeot-partner-ii-tepee-phase-iii-2015-22.5-kwh-67hp-electric-32794
EU-KIA-K9-II-RJ-SEDAN-01	5120	1915	1490	Kia K900 official specifications	https://kiairaqnim.com/en/showroom/k900/specification.html
EU-VW-GOLF-VII-5G-VARIANT-TGI-WAGON-01	4567	1799	1496	Auto-Data Volkswagen Golf VII Variant 1.5 TGI	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.5-tgi-130hp-dsg-37258
EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Captiva 2.4 2WD	https://www.automobile-catalog.com/car/2007/559970/chevrolet_captiva_2_4_2wd_ls_5-pers_.html
EU-AUSTIN-ALLEGRO-III-ADO67-SEDAN-01	3908	1613	1393	Automobile-Catalog 1980 Austin Allegro 1.3 L	https://www.automobile-catalog.com/car/1980/256595/austin_allegro_1_3_l.html
```

## 下一步优先处理

1. 确认 `135117`、`135129` 的实际 Crafter 动力版本，并据此确定厢式车车长/车顶及底盘驾驶室分支。
2. 确认 `135306` Silverado 1500 Crew Cab 对应的货斗长度，避免猜测性创建派生行。
3. 解决 `135352` RS5 Sportback 的高度来源冲突及改款边界。

推进信号：CONTINUE

[1]: https://de.wikipedia.org/wiki/VW_Crafter?utm_source=chatgpt.com "VW Crafter"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3501-3600_ktype_dimension_mapping_final.tsv
- all_3501-3600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合最后 4 个 PENDING Ktype。Crafter 厢式车按车长与车顶拆为 6 个物理分支，底盘驾驶室复用 5 个既有稳定尺寸组。
* Silverado 1500 Crew Cab 已确认同时覆盖短货斗和标准货斗，拆分为两个物理外廓。([汽车目录][1])
* RS5 Sportback 已按 Audi 官方三维 `4783 × 1866 × 1387 mm` 建组；改款前后未产生需拆分的三维差异。
* 已完成机械校验：固定表头、主键唯一、映射引用闭合、尺寸与来源非空、无孤立尺寸组、两个指定文件均已生成。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：124
* READY 映射：124
* PENDING 映射：0
* 最终尺寸组：81
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 最终产物校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135073	135073	Wagon	Talisman I		5	EU-RENAULT-TALISMAN-I-WAGON-01	HIGH		READY
135106	135106	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
135107	135107	SUV	X4 G02	G02	5	EU-BMW-X4-G02-M40I-SUV-01	HIGH		READY
135108	135108	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
135112	135112	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
135113	135113	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
135117_l3h2	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	中轴距低顶物理外廓。	READY
135117_l3h3	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	中轴距高顶物理外廓。	READY
135117_l4h3	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	长轴距高顶物理外廓。	READY
135117_l4h4	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	HIGH	长轴距超高顶物理外廓。	READY
135117_l5h3	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	HIGH	加长轴距高顶物理外廓。	READY
135117_l5h4	135117	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	HIGH	加长轴距超高顶物理外廓。	READY
135129_scab_l3	135129	Pickup	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	HIGH	单排驾驶室中轴距底盘外廓。	READY
135129_scab_l4	135129	Pickup	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	HIGH	单排驾驶室长轴距底盘外廓。	READY
135129_scab_l5	135129	Pickup	Crafter II		2	EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	HIGH	单排驾驶室加长轴距底盘外廓。	READY
135129_dcab_l3	135129	Pickup	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	HIGH	双排驾驶室中轴距底盘外廓。	READY
135129_dcab_l4	135129	Pickup	Crafter II		4	EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	HIGH	双排驾驶室长轴距底盘外廓。	READY
135143	135143	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135144	135144	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135145	135145	Hatchback	A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
135146	135146	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-FACELIFT-01	HIGH		READY
135157	135157	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH		READY
135158	135158	SUV	Range Rover IV	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	MEDIUM	P400e标准轴距外廓。	READY
135159	135159	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH		READY
135160	135160	Sedan	Cerato IV	BD	4	EU-KIA-CERATO-IV-BD-SEDAN-01	HIGH		READY
135161	135161	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH		READY
135162	135162	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-COUPE-01	HIGH		READY
135165	135165	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-COUPE-01	HIGH		READY
135166	135166	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	HIGH		READY
135167	135167	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	HIGH		READY
135168	135168	SUV	Q2 GA	GA	5	EU-AUDI-SQ2-GA-SUV-PREFL-01	HIGH		READY
135169_prefl	135169	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135169_facelift	135169	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135170	135170	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	改款前Sportback外廓。	READY
135171	135171	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	MEDIUM	改款前Cabriolet外廓。	READY
135172_prefl	135172	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-PREFL-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135172_facelift	135172	Convertible	A5 F5	F57	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135173_prefl	135173	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135173_facelift	135173	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135174_prefl	135174	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135174_facelift	135174	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135175_prefl	135175	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135175_facelift	135175	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135176_prefl	135176	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135176_facelift	135176	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135177_prefl	135177	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135177_facelift	135177	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135178_prefl	135178	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135178_facelift	135178	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135197	135197	SUV	G-Class W463 II	W463	5	EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	MEDIUM	封闭式五门车身。	READY
135254	135254	Sedan	Vesta I		4	EU-LADA-VESTA-I-SPORT-SEDAN-01	HIGH		READY
135255	135255	Coupe	Erelis		4	EU-MPM-MOTORS-ERELIS-COUPE-01	MEDIUM	四门Coupe外廓。	READY
135256	135256	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
135257	135257	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
135260	135260	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
135261	135261	Sedan	Megane IV		4	EU-RENAULT-MEGANE-IV-SEDAN-01	HIGH		READY
135269	135269	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
135270	135270	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
135272	135272	Hatchback	Stinger I	CK	5	EU-KIA-STINGER-I-LIFTBACK-01	HIGH		READY
135274	135274	SUV	Macan 95B	95B	5	EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	HIGH		READY
135275_prefl	135275	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	Ktype跨越改款，改款前外廓。	READY
135275_facelift	135275	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-FACELIFT-01	HIGH	Ktype跨越改款，改款后外廓。	READY
135282	135282	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
135283	135283	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
135288	135288	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
135289	135289	Wagon	Logan II		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH		READY
135290	135290	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
135291	135291	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
135292	135292	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH		READY
135306_shortbed	135306	Pickup	Silverado 1500 IV	T1XX	4	EU-CHEVROLET-SILVERADO-1500-IV-T1XX-CREW-CAB-SHORT-BED-4WD-01	HIGH	Crew Cab短货斗物理外廓。	READY
135306_standardbed	135306	Pickup	Silverado 1500 IV	T1XX	4	EU-CHEVROLET-SILVERADO-1500-IV-T1XX-CREW-CAB-STANDARD-BED-4WD-01	HIGH	Crew Cab标准货斗物理外廓。	READY
135309	135309	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
135310	135310	Sedan	Optima IV	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
135315	135315	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	HIGH		READY
135316	135316	SUV	Kodiaq I	NS7	5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH		READY
135317	135317	Hatchback	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	HIGH		READY
135318	135318	Wagon	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
135320	135320	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135323	135323	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135324	135324	Hatchback	B-Class W247	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	MEDIUM	Sports Tourer五门外廓。	READY
135328	135328	SUV	Range Rover Velar	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SVAUTOBIOGRAPHY-DYNAMIC-SUV-01	HIGH		READY
135334_prefl	135334	Hatchback	Clio IV Phase I	X98	5	EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	HIGH	Ktype覆盖改款前外廓。	READY
135334_facelift	135334	Hatchback	Clio IV Phase II	X98	5	EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	HIGH	Ktype覆盖改款后外廓。	READY
135338	135338	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	MEDIUM		READY
135339	135339	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	HIGH		READY
135340	135340	Convertible	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	HIGH		READY
135341	135341	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135342	135342	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135343	135343	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH		READY
135345	135345	Van	Yaris III	XP130	3	EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	HIGH		READY
135347	135347	Coupe	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	HIGH		READY
135348	135348	Coupe	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	HIGH		READY
135349	135349	Convertible	R8 4S facelift	4S	2	EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	HIGH		READY
135352	135352	Hatchback	RS5 F5	F5A	5	EU-AUDI-RS5-F5-SPORTBACK-01	HIGH		READY
135353	135353	SUV	X3 M F97	F97	5	EU-BMW-X3-F97-M-SUV-01	HIGH		READY
135354	135354	SUV	X3 M F97	F97	5	EU-BMW-X3-F97-M-COMPETITION-SUV-01	HIGH		READY
135355	135355	SUV	X4 M F98	F98	5	EU-BMW-X4-F98-M-SUV-01	HIGH		READY
135356	135356	SUV	X4 M F98	F98	5	EU-BMW-X4-F98-M-COMPETITION-SUV-01	HIGH		READY
135357	135357	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH		READY
135359	135359	MPV	Touran II	5T	5	EU-VW-TOURAN-II-5T-MPV-01	HIGH		READY
135361	135361	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135362	135362	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
135364	135364	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135365	135365	Wagon	Golf VII	5G	5	EU-VW-GOLF-VII-5G-VARIANT-TGI-WAGON-01	HIGH		READY
135366	135366	Sedan	K9 II	RJ	4	EU-KIA-K9-II-RJ-SEDAN-01	HIGH		READY
135367	135367	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135369	135369	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135370	135370	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135371	135371	Hatchback	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	HIGH		READY
135372	135372	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135373	135373	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135374	135374	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135375	135375	Wagon	Mondeo V	CD391	5	EU-FORD-MONDEO-V-CD391-WAGON-01	HIGH		READY
135394	135394	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-WAGON-01	HIGH		READY
135425	135425	SUV	Captiva I	C100	5	EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	HIGH		READY
135458	135458	Sedan	Allegro III	ADO67	4	EU-AUSTIN-ALLEGRO-III-ADO67-SEDAN-01	MEDIUM	输入结束月晚于车型实际停产期，按Allegro III 1.3外廓。	READY
135550_prefl	135550	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135550_facelift	135550	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135552_prefl	135552	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135552_facelift	135552	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135557_prefl	135557	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135557_facelift	135557	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
135558_prefl	135558	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
135558_facelift	135558	Sedan	Focus IV	C519	4	EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	HIGH	Ktype覆盖改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3501-3600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-TALISMAN-I-WAGON-01	4865	1870	1465	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621	BMW Group Specifications BMW X4 M40i	https://www.press.bmwgroup.com/global/article/attachment/T0281798EN/410795
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Commercial Vehicles Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Audi MediaCenter A1 Sportback dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-a1-sportback-1382/download
EU-VW-SHARAN-II-7N-MPV-FACELIFT-01	4854	1904	1720	Volkswagen UK Sharan brochure November 2018	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/sharan/sharan-fl/vw_sharan_brochure_nov_2018.pdf
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673	Volkswagen UK Tiguan official brochure April 2017	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/tiguan/tiguan-nf/vw-tiguan-nf-brochure-apr-2017.pdf
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-KIA-CERATO-IV-BD-SEDAN-01	4640	1800	1450	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300	Porsche 2020 911 Carrera S and Carrera 4S technical data	https://newsroom.porsche.com/dam/jcr%3Ad5712d5c-b376-41d9-8201-09731162e143/2020_911_Carrera_S_and_911_Carrera_4S_US_specifications.pdf
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299	Porsche 2020 911 Carrera S Cabriolet and Carrera 4S Cabriolet technical data	https://newsroom.porsche.com/dam/jcr%3A1bb7bc77-6925-4e3c-ab03-0fc6065260fb/PCNA19_0038_us.pdf
EU-AUDI-SQ2-GA-SUV-PREFL-01	4210	1802	1495	Auto-Data Audi SQ2 2.0 TFSI quattro	https://www.auto-data.net/en/audi-sq2-2.0-tfsi-300hp-quattro-s-tronic-35095
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431	Audi MediaCenter The Audi A4 Major Upgrade for the Bestseller	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460	Audi MediaCenter The Audi A4 Major Upgrade for the Bestseller	https://www.audi-mediacenter.com/en/the-audi-a4-major-upgrade-for-the-bestseller-11884/download
EU-MERCEDES-BENZ-G-KLASSE-W463-II-SUV-01	4825	1931	1969	Automobile-Catalog 2019 Mercedes-Benz G 350 d	https://www.automobile-catalog.com/car/2019/2875145/mercedes-benz_g_350_d.html
EU-LADA-VESTA-I-SPORT-SEDAN-01	4420	1774	1478	LADA Vesta Sport official technical specifications	https://minsk-lada.by/upload/iblock/600/%D0%A2%D0%B5%D1%85%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5%20%D1%85%D0%B0%D1%80%D0%B0%D0%BA%D1%82%D0%B5%D1%80%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B8%20-%20LADA%20Vesta%20Sport%20-%20LADA.pdf
EU-MPM-MOTORS-ERELIS-COUPE-01	4684	1860	1383	Carfolio 2018 MPM Erelis 1.2T	https://www.carfolio.com/mpm-erelis-1.2t-564707
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-IV-WAGON-01	4626	1814	1457	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-KIA-STINGER-I-LIFTBACK-01	4830	1870	1400	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-PORSCHE-MACAN-95B-SUV-FACELIFT-BASE-01	4696	1923	1624	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-CHEVROLET-SILVERADO-1500-IV-T1XX-CREW-CAB-SHORT-BED-4WD-01	5885	2063	1918	Automobile-Catalog 2019 Chevrolet Silverado 1500 Crew Cab 4x4 Short Box 6.2L	https://www.automobile-catalog.com/car/2019/3074600/chevrolet_silverado_1500_crew_cab_4x4_short_box_6_2-liter_v-8.html
EU-CHEVROLET-SILVERADO-1500-IV-T1XX-CREW-CAB-STANDARD-BED-4WD-01	6127	2063	1915	Edmunds 2019 Chevrolet Silverado 1500 Crew Cab Standard Bed 4WD specifications	https://www.edmunds.com/chevrolet/silverado-1500/2019/st-401765114/features-specs/
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-B-KLASSE-W247-HATCHBACK-01	4419	1796	1562	Automobile-Catalog 2019 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2019/2967260/mercedes-benz_b_220_4matic.html
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SVAUTOBIOGRAPHY-DYNAMIC-SUV-01	4806	1940	1665	Automobile-Catalog 2019 Range Rover Velar SVAutobiography Dynamic Edition	https://www.automobile-catalog.com/car/2019/2875910/range_rover_velar_svautobiography_dynamic_edition.html
EU-RENAULT-CLIO-IV-PHASE-I-HATCHBACK-01	4062	1732	1448	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-RENAULT-CLIO-IV-PHASE-II-HATCHBACK-01	4062	1731	1448	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862	Peugeot Partner Tepee handbook; Auto-Data Peugeot Partner II Tepee Electric	https://www.kemwel.com/peugeot-fleet/documents/partner.pdf; https://www.auto-data.net/en/peugeot-partner-ii-tepee-phase-iii-2015-22.5-kwh-67hp-electric-32794
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605	Kia Europe e-Soul 2019 press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/e-Soul/Kia%20e-Soul%20-%202019%20-%20Final%20-%205%20Apr%202019.doc
EU-AUDI-R8-4S-FACELIFT-SPYDER-QUATTRO-01	4429	1940	1242	Audi MediaCenter R8 Spyder V10 performance quattro dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-r8-spyder-performance-1449/download
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471	ŠKODA SCALA petrol/diesel technical specifications	https://cdn.skoda-storyboard.com/2019/04/TD-SCALA-petrol-diesel-en.pdf
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-AUDI-R8-4S-FACELIFT-COUPE-QUATTRO-01	4429	1940	1236	Audi MediaCenter R8 Coupé V10 performance quattro dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-r8-coupe-performance-1448/download
EU-AUDI-RS5-F5-SPORTBACK-01	4783	1866	1387	Audi official RS 5 Sportback dimensions	https://www.audi.com/en/publications/dimensions/dimensions-rs-5-sportback-1430/download
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667	BMW Group Specifications The new BMW X3 M	https://www.press.bmwgroup.com/france/article/attachment/T0291683FR/424502
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669	BMW Group Specifications The new BMW X3 M	https://www.press.bmwgroup.com/france/article/attachment/T0291683FR/424502
EU-BMW-X4-F98-M-SUV-01	4758	1927	1618	BMW Group Specifications The new BMW X4 M	https://www.press.bmwgroup.com/belux/article/attachment/T0291892FR/424631
EU-BMW-X4-F98-M-COMPETITION-SUV-01	4758	1927	1620	BMW Group Specifications The new BMW X4 M	https://www.press.bmwgroup.com/belux/article/attachment/T0291892FR/424631
EU-VW-TOURAN-II-5T-MPV-01	4527	1829	1659	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-KIA-K9-II-RJ-SEDAN-01	5120	1915	1490	Kia K900 official specifications	https://kiairaqnim.com/en/showroom/k900/specification.html
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-VW-GOLF-VII-5G-VARIANT-TGI-WAGON-01	4567	1799	1496	Auto-Data Volkswagen Golf VII Variant 1.5 TGI	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.5-tgi-130hp-dsg-37258
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-CHEVROLET-CAPTIVA-I-C100-SUV-PREFL-01	4635	1850	1720	Automobile-Catalog 2007 Chevrolet Captiva 2.4 2WD	https://www.automobile-catalog.com/car/2007/559970/chevrolet_captiva_2_4_2wd_ls_5-pers_.html
EU-AUSTIN-ALLEGRO-III-ADO67-SEDAN-01	3908	1613	1393	Automobile-Catalog 1980 Austin Allegro 1.3 L	https://www.automobile-catalog.com/car/1980/256595/austin_allegro_1_3_l.html
EU-FORD-FOCUS-IV-C519-SEDAN-PREFL-01	4647	1825	1471	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
EU-FORD-FOCUS-IV-C519-SEDAN-FACELIFT-01	4651	1825	1452	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_3501-3600_cross_batch_dimension_index_source.txt
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3501-3600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2019/3074600/chevrolet_silverado_1500_crew_cab_4x4_short_box_6_2-liter_v-8.html?utm_source=chatgpt.com "Chevrolet Silverado 1500 Crew Cab 4x4 Short Box 6.2-liter ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3038 行）
- 累计尺寸组：dimension_groups_final.tsv（1415 行）

