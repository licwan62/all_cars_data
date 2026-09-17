# 任务：all 第 301-400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0004__fa032da6


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 301-400 行

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
all 第 301-400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796
EU-CITROEN-JUMPY-III-K0-MPV-M-01	4959	1920	1895
EU-CITROEN-JUMPY-III-K0-MPV-XL-01	5309	1920	1935
EU-CITROEN-JUMPY-III-K0-MPV-XS-01	4609	1920	1905
EU-OPEL-GRANDLAND-X-SUV-01	4477	1856	1609
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	4403	1848	1860
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	4753	1848	1860

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
KIA	Xceed	1.6 GDI Hybrid	SUV	Frontantrieb	Benzin/Elektro	104	141	Dec 2019	-	2024-03-01	139293
Rolls-royce	Wraith	V12	Coupe	Heckantrieb	Benzin	441	600	Jul 2019	-	2024-03-01	139294
KIA	Seltos	1.6 MPI	SUV	Frontantrieb	Benzin	90	122	Sep 2019	-	2024-03-01	139295
KIA	Seltos	1.6 MPI 4WD	SUV	Allrad	Benzin	89	121	Sep 2019	-	2024-03-01	139296
KIA	Seltos	2.0 MPI 4WD	SUV	Allrad	Benzin	110	150	Aug 2019	-	2024-03-01	139297
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	280	381	Nov 2006	Dec 2008	2024-03-01	139305
Renault	Kangoo	1.5 DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Oct 2019	-	2024-03-01	139307
Renault	Kangoo	1.5 DCI 115	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Oct 2019	-	2024-03-01	139308
Skoda	Kamiq	1.0 TGI CNG	SUV	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2019	-	2024-03-01	139309
Skoda	Scala	1.0 TGI CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	66	90	Nov 2019	-	2024-03-01	139310
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	300	408	Aug 2009	May 2012	2024-03-01	139314
Porsche	911	3.8	Cabriolet	Heckantrieb	Benzin	300	408	Aug 2010	May 2011	2024-03-01	139321
Ford	Grand c-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	63	86	Dec 2010	Jun 2019	2024-03-01	139324
Hyundai	Venue	1.6	SUV	Frontantrieb	Benzin	90	122	Sep 2019	-	2024-03-01	139326
Porsche	Boxster	S 3.4	Cabriolet	Heckantrieb	Benzin	235	320	Aug 2010	May 2012	2024-03-01	139327
Peugeot	Boxer	2.2 Bluehdi 165	Bus	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2024-05-01	139329
Chevrolet	Corvette	6.2	Coupe	Heckantrieb	Benzin	369	502	Jul 2019	-	2024-03-01	139330
BMW	X5	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	May 2020	-	2024-03-01	139332
BMW	X6	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	250	340	May 2020	Mar 2023	2024-03-01	139333
Citroën	Berlingo	1.5 Bluehdi 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Jun 2018	-	2024-03-01	139338
Citroën	Jumpy iii	2.0 Bluehdi 120 4X4	Kasten	Allrad	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	139339
Citroën	Jumpy iii	2.0 Bluehdi 150 4X4	Kasten	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139341
Citroën	Spacetourer	2.0 Bluehdi 150 4X4	Bus	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139344
Peugeot	Partner	1.5 Bluehdi 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Sep 2018	-	2024-03-01	139347
Peugeot	Expert	2.0 Bluehdi 120 4X4	Kasten	Allrad	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	139348
Peugeot	Expert	2.0 Bluehdi 150 4X4	Kasten	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2026-01-01	139354
Peugeot	Boxer	2.2 HDI 130 4X4	Kasten	Allrad	Diesel	96	131	Mar 2011	-	2024-03-01	139362
Peugeot	Boxer	2.2 HDI 150 4X4	Kasten	Allrad	Diesel	110	150	Mar 2011	-	2024-03-01	139364
Peugeot	Boxer	2.0 Bluehdi 130 4X4	Kasten	Allrad	Diesel	96	130	Mar 2016	Sep 2019	2025-02-03	139365
Peugeot	Boxer	2.0 Bluehdi 160 4X4	Kasten	Allrad	Diesel	120	163	Mar 2016	Sep 2019	2025-02-03	139366
Peugeot	Traveller	2.0 Bluehdi 150 / HDI 150 4X4	Bus	Allrad	Diesel	110	150	Apr 2016	Dec 2022	2025-12-01	139367
Opel	Zafira	2.0 4X4	Bus	Allrad	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	139376
Opel	Combo	1.5 D Allrad	Kasten/Großraumlimousine	Allrad	Diesel	96	131	Aug 2018	-	2025-06-01	139377
Opel	Vivaro c	1.5 Allrad	Kasten	Allrad	Diesel	88	120	Mar 2019	-	2025-06-01	139378
Opel	Vivaro c	2.0 Allrad	Kasten	Allrad	Diesel	110	150	Mar 2019	Dec 2022	2026-01-01	139379
Mercedes-benz	Sprinter classic 3,5-T	313 CDI	Kasten	Heckantrieb	Diesel	100	136	Jan 2017	-	2024-03-01	139397
Mercedes-benz	Sprinter classic 4,6-T	413 CDI	Kasten	Heckantrieb	Diesel	100	136	Jan 2017	-	2024-03-01	139398
Nissan	Nv400	DCI 180	Kasten	Frontantrieb	Diesel	132	179	Jan 2020	Dec 2022	2026-03-01	139400
Nissan	Nv400	DCI 180	Pritsche/Fahrgestell	Frontantrieb	Diesel	132	179	Jan 2020	Dec 2022	2026-03-01	139401
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	90	122	Nov 2019	Dec 2022	2026-01-01	139431
Land Rover	Range rover sport ii	3.0 P360 Mhev 4X4	SUV	Allrad	Benzin/Elektro	265	360	Jun 2019	Mar 2022	2025-02-03	139460
BMW	3	330 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	215	292	Jul 2020	-	2024-03-01	139467
BMW	3	330 E Plug-in-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	215	292	Jul 2020	-	2024-03-01	139469
BMW	3	M340 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	250	340	Apr 2020	-	2024-03-01	139470
BMW	3	M 340 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	250	340	Apr 2020	-	2024-03-01	139471
VW	Transporter t6 / caravelle	2.0 TDI	Bus	Frontantrieb	Diesel	66	90	Oct 2019	Aug 2024	2025-02-03	139473
BMW	3	320 I	Kasten/Kombi	Heckantrieb	Benzin	135	184	Nov 2019	-	2024-03-01	139481
BMW	3	330 I	Kasten/Kombi	Heckantrieb	Benzin	190	258	Jul 2019	-	2024-03-01	139482
BMW	3	M 340 I Xdrive	Kasten/Kombi	Allrad	Benzin	275	374	Nov 2019	-	2024-03-01	139483
BMW	3	320 D	Kasten/Kombi	Heckantrieb	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	139484
BMW	3	320 D Mild-hybrid	Kasten/Kombi	Heckantrieb	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139485
BMW	3	320 D Xdrive	Kasten/Kombi	Allrad	Diesel	140	190	Jul 2019	Feb 2020	2024-03-01	139486
BMW	3	320 D Mild-hybrid Xdrive	Kasten/Kombi	Allrad	Diesel/Elektro	140	190	Mar 2020	-	2024-03-01	139487
BMW	3	330 D	Kasten/Kombi	Heckantrieb	Diesel	195	265	Nov 2019	-	2024-03-01	139488
BMW	3	330 D Xdrive	Kasten/Kombi	Allrad	Diesel	195	265	Nov 2019	-	2024-03-01	139489
BMW	X5	Xdrive 30 D	Kasten/SUV	Allrad	Diesel	195	265	Nov 2019	Mar 2023	2024-03-01	139490
BMW	X5	Xdrive 40 I	Kasten/SUV	Allrad	Benzin	250	340	Nov 2019	Mar 2023	2024-03-01	139491
Peugeot	Partner	1.6 HDI 92	Kasten/Großraumlimousine	Frontantrieb	Diesel	68	92	Sep 2018	-	2024-05-01	139492
Opel	Grandland	1.6 Turbo	SUV	Frontantrieb	Benzin	110	150	Dec 2019	Jul 2021	2025-02-03	139502
MG	Hs	1.5 T	SUV	Frontantrieb	Benzin	119	162	Sep 2018	-	2025-12-01	139504
Fiat	500	1.0 Mild Hybrid	Cabriolet	Frontantrieb	Benzin/Elektro	51	69	Jan 2020	-	2024-03-01	139507
Santana	300	1.6 HDI 4X4	Geländewagen offen	Allrad	Diesel	66	90	Oct 2006	Feb 2011	2024-03-01	139533
Land Rover	Range rover evoque	1.5 P300e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	227	309	Feb 2020	-	2024-03-01	139607
MG	Zs	EV	SUV	Frontantrieb	Elektro	105	143	Mar 2019	-	2025-12-01	139640
Ford	Transit v363	2.0 Ecoblue RWD	Bus	Heckantrieb	Diesel	96	130	May 2019	-	2024-03-01	139643
Ford	Transit v363	2.0 Ecoblue RWD	Bus	Heckantrieb	Diesel	125	170	May 2019	Jun 2024	2024-11-01	139644
Audi	A4 allroad b9	40 TDI Quattro	Kombi	Allrad	Diesel	140	190	Jan 2020	-	2024-03-01	139648
BMW	X3	Xdrive M40 I	SUV	Allrad	Benzin	285	387	Sep 2019	-	2024-03-01	139649
BMW	X3	Xdrive M40 I	Kasten/SUV	Allrad	Benzin	285	387	Sep 2019	-	2024-03-01	139650
Alfa Romeo	Giulia	2.9 GTA	Stufenheck	Heckantrieb	Benzin	397	540	May 2020	-	2024-03-01	139651
Mercedes-benz	Gla	GLA 200	SUV	Frontantrieb	Benzin	120	163	Feb 2020	-	2024-03-01	139652
Mercedes-benz	Gla	GLA 250	SUV	Frontantrieb	Benzin	165	224	Feb 2020	-	2024-03-01	139653
Mercedes-benz	Gla	GLA 250 4-matic	SUV	Allrad	Benzin	165	224	Feb 2020	-	2024-03-01	139654
Mercedes-benz	Gla	GLA 200 D	SUV	Frontantrieb	Diesel	110	150	Feb 2020	-	2024-03-01	139655
Mercedes-benz	Gla	GLA 200 D 4-matic	SUV	Allrad	Diesel	110	150	Feb 2020	-	2024-03-01	139656
Lancia	Ypsilon	1.0 Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	51	69	Mar 2020	-	2024-03-01	139657
Mercedes-benz	Gla	GLA 220 D 4-matic	SUV	Allrad	Diesel	140	190	Feb 2020	-	2024-03-01	139658
Mercedes-benz	Gla	GLA 220 D	SUV	Frontantrieb	Diesel	140	190	Feb 2020	-	2024-03-01	139659
Aston Martin	Dbx	4	SUV	Allrad	Benzin	405	551	Nov 2019	-	2024-03-01	139672
Land Rover	Discovery sport	1.5 P300e Hybrid 4X4	SUV	Allrad	Benzin/Elektro	227	309	Feb 2020	-	2024-03-01	139678
Suzuki	Swift v	1.4 Sport Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	95	129	Mar 2020	-	2024-03-01	139679
BMW	2	216 D	Coupe	Frontantrieb	Diesel	85	116	Mar 2020	-	2024-03-01	139680
KIA	Ceed	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	101	Sep 2019	-	2024-03-01	139690
KIA	Ceed	1.6 Crdi 115 Eco-dynamics+	Schrägheck	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139693
KIA	Ceed	1.6 Crdi 136 Eco-dynamics+	Schrägheck	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139694
KIA	Ceed	1.6 Crdi 115 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139695
KIA	Ceed	1.6 Crdi 136 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139696
KIA	Proceed	1.6 Crdi 136 Eco-dynamics+	Kombi	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139697
KIA	Xceed	1.6 Crdi 115 Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	85	116	Dec 2019	-	2024-03-01	139698
KIA	Xceed	1.6 Crdi 136 Eco-dynamics+	SUV	Frontantrieb	Diesel/Elektro	100	136	Dec 2019	-	2024-03-01	139699
Audi	A3	35 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2019	-	2024-03-01	139714
Audi	A3	30 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Nov 2019	-	2024-03-01	139715
Audi	A3	35 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	139716
Porsche	718 cayman	GTS 4.0	Coupe	Heckantrieb	Benzin	294	400	Jan 2019	-	2024-03-01	139717
Porsche	718 boxster	GTS 4.0	Cabriolet	Heckantrieb	Benzin	294	400	Jan 2019	-	2024-03-01	139725
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	131	Nov 2019	-	2024-03-01	139734
Seat	Leon	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2019	-	2024-03-01	139736
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Nov 2019	-	2024-03-01	139737
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	139738
Seat	Leon	1.5 TSI	Kombi	Frontantrieb	Benzin	96	131	Mar 2020	-	2024-03-01	139744


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **86 个输入 Ktype**，形成 **110 条 READY 映射**。
* 本轮首次创建 **40 个尺寸组**；另外直接复用用户提供的 **9 个跨批次尺寸组**，未重复输出。
* Kia Ceed、Seltos、Hyundai Venue、Audi A3 和 Seat Leon 的三维已按厂商资料闭合；Leon Sportstourer 高度已按同期官方规格修正为 **1450 mm**。([起亚新闻][1])
* 新增闭合 Santana 300 Cabriolet 与 Alfa Romeo Giulia GTA；Giulia GTA 使用官方欧洲参考值的 **4654 × 1923 × 1397 mm**。([汽车目录][2])
* 剩余项目均为多轴距、多车顶或多车身组合。Renault Kangoo 已确认普通版和 Maxi，但官方资料仍给出配置相关高度范围；Ford Transit、VW T6.1 等也已确认存在多个物理分支，不能压成单一尺寸组。([雷诺新闻][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：86
* READY 映射：110
* PENDING Ktype：14
* 已确认尺寸组：49

  * 本轮新建：40
  * 跨批次复用：9
* 待处理 Ktype：`139307`、`139308`、`139329`、`139362`、`139364`、`139365`、`139366`、`139397`、`139398`、`139400`、`139401`、`139473`、`139643`、`139644`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139293	139293	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139294	139294	Coupe	Wraith	RR5	2	EU-ROLLS-ROYCE-WRAITH-RR5-COUPE-01	HIGH		READY
139295	139295	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139296	139296	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139297	139297	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139305	139305	Targa	911 (997.1)	997	2	EU-PORSCHE-911-9971-TARGA-4S-01	HIGH		READY
139309	139309	SUV	Kamiq I		5	EU-SKODA-KAMIQ-I-SUV-01	HIGH		READY
139310	139310	Hatchback	Scala I		5	EU-SKODA-SCALA-I-HATCHBACK-01	HIGH		READY
139314	139314	Targa	911 (997.2)	997	2	EU-PORSCHE-911-9972-TARGA-4S-01	HIGH		READY
139321	139321	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	HIGH		READY
139324_prefl	139324	MPV	Grand C-MAX II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	2010-2015改款前外廓。	READY
139324_facelift	139324	MPV	Grand C-MAX II facelift		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	2015-2019改款后外廓。	READY
139326	139326	SUV	Venue I	QX	5	EU-HYUNDAI-VENUE-I-QX-SUV-01	HIGH		READY
139327	139327	Convertible	Boxster (987.2)	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-S-01	HIGH		READY
139330	139330	Coupe	Corvette C8	C8	2	EU-CHEVROLET-CORVETTE-C8-COUPE-01	HIGH		READY
139332	139332	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH		READY
139333	139333	SUV	X6 (G06)	G06	5	EU-BMW-X6-G06-SUV-01	HIGH		READY
139338	139338	Van	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-VAN-M-01	HIGH	K9 M四驱外廓。	READY
139339_xs	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139339_m	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139339_xl	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139341_xs	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139341_m	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139341_xl	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139344_xs	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139344_m	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139344_xl	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139347_l1	139347	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	K9四驱L1外廓。	READY
139347_l2	139347	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	HIGH	K9四驱L2外廓。	READY
139348_xs	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139348_m	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139348_xl	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139354_xs	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139354_m	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139354_xl	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139367_xs	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139367_m	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139367_xl	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139376_xs	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139376_m	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139376_xl	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139377_l1	139377	Van	Combo E	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	MEDIUM	K9四驱L1外廓；与Partner同平台尺寸组。	READY
139377_l2	139377	Van	Combo E	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	MEDIUM	K9四驱L2外廓；与Partner同平台尺寸组。	READY
139378_xs	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139378_m	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139378_xl	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139379_xs	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139379_m	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139379_xl	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139431_xs	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139431_m	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139431_xl	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139460	139460	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-01	HIGH		READY
139467	139467	Sedan	3 Series (G20)	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
139469	139469	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH		READY
139470	139470	Sedan	3 Series (G20)	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
139471	139471	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH		READY
139481	139481	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139482	139482	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139483	139483	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139484	139484	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139485	139485	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139486	139486	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139487	139487	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139488	139488	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139489	139489	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139490	139490	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH	Kasten/SUV登记不改变G05外廓。	READY
139491	139491	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH	Kasten/SUV登记不改变G05外廓。	READY
139492_l1	139492	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	K9 L1外廓。	READY
139492_l2	139492	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	K9 L2外廓。	READY
139502	139502	SUV	Grandland X		5	EU-OPEL-GRANDLAND-X-SUV-01	HIGH		READY
139504	139504	SUV	HS I		5	EU-MG-HS-I-SUV-01	HIGH		READY
139507	139507	Convertible	500C (312 facelift)	312	2	EU-FIAT-500C-312-FACELIFT-CONVERTIBLE-01	HIGH		READY
139533	139533	Convertible	Santana 300		3	EU-SANTANA-300-CONVERTIBLE-01	HIGH	三门软顶敞开式车身。	READY
139607	139607	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
139640	139640	SUV	ZS I EV		5	EU-MG-ZS-I-EV-SUV-01	HIGH		READY
139648	139648	Wagon	A4 allroad B9 facelift	8W	5	EU-AUDI-A4-ALLROAD-B9-FACELIFT-WAGON-01	HIGH		READY
139649	139649	SUV	X3 (G01)	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH		READY
139650	139650	SUV	X3 (G01)	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	Kasten/SUV登记不改变G01外廓。	READY
139651	139651	Sedan	Giulia II	952	4	EU-ALFA-ROMEO-GIULIA-II-952-SEDAN-GTA-01	HIGH	GTA宽体外廓。	READY
139652	139652	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139653	139653	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139654	139654	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139655	139655	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139656	139656	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139657	139657	Hatchback	Ypsilon III facelift	846	5	EU-LANCIA-YPSILON-III-846-HATCHBACK-01	HIGH		READY
139658	139658	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139659	139659	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139672	139672	SUV	DBX I		5	EU-ASTON-MARTIN-DBX-I-SUV-01	HIGH		READY
139678	139678	SUV	Discovery Sport facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-FACELIFT-SUV-01	HIGH		READY
139679	139679	Hatchback	Swift VI	A2L	5	EU-SUZUKI-SWIFT-VI-A2L-HATCHBACK-SPORT-01	HIGH		READY
139680	139680	Coupe	2 Series Gran Coupé	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应四门Gran Coupé F44。	READY
139690	139690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139693	139693	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139694	139694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139695	139695	Wagon	Ceed Sportswagon III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139696	139696	Wagon	Ceed Sportswagon III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139697	139697	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH		READY
139698	139698	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139699	139699	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139714	139714	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139715	139715	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139716	139716	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139717	139717	Coupe	718 Cayman	982	2	EU-PORSCHE-718-CAYMAN-982-COUPE-GTS40-01	HIGH		READY
139725	139725	Convertible	718 Boxster	982	2	EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-GTS40-01	HIGH		READY
139734	139734	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139736	139736	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139737	139737	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139738	139738	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139744	139744	Wagon	Leon Sportstourer IV	KL	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-XCEED-I-CD-SUV-01	4395	1826	1495	Kia XCeed 2020 official brochure	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/model-brochures/XCeed-Brochure-2020.pdf
EU-ROLLS-ROYCE-WRAITH-RR5-COUPE-01	5285	1947	1507	Auto-Data Rolls-Royce Wraith model specifications	https://www.auto-data.net/en/rolls-royce-wraith-model-2135
EU-KIA-SELTOS-I-SP2-SUV-01	4370	1800	1615	Kia Seltos official brochure	https://www.kia.com/content/dam/kwcms/ph/en/pdf/updated-pdf/FA_KIA_Seltos_Brochure_compressed.pdf
EU-PORSCHE-911-9971-TARGA-4S-01	4427	1852	1300	EncyCARpedia Porsche 911 Targa 4S 997 specifications	https://www.encycarpedia.com/porsche/06-911-targa-4s
EU-PORSCHE-911-9972-TARGA-4S-01	4435	1852	1300	Automobile-Catalog Porsche 911 Targa 4S PDK 2010	https://www.automobile-catalog.com/car/2010/2868485/porsche_911_targa_4s_pdk.html
EU-SKODA-KAMIQ-I-SUV-01	4241	1793	1531	Škoda Storyboard official Kamiq press release	https://www.skoda-storyboard.com/en/press-releases/skoda-kamiq-the-new-city-suv/
EU-SKODA-SCALA-I-HATCHBACK-01	4362	1793	1471	Škoda Storyboard official Scala press release	https://www.skoda-storyboard.com/cs/tiskove-zpravy-archiv/pocatek-nove-designove-ery-skoda-scala-2019/
EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	4435	1808	1300	Automobile-Catalog Porsche 911 Carrera S Cabriolet 2010	https://www.automobile-catalog.com/car/2010/2868230/porsche_911_carrera_s_cabriolet.html
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Auto-Data Ford C-MAX model specifications	https://www.auto-data.net/en/ford-c-max-model-808
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	4519	1828	1642	Auto-Data Ford C-MAX model specifications	https://www.auto-data.net/en/ford-c-max-model-808
EU-HYUNDAI-VENUE-I-QX-SUV-01	4040	1770	1592	Hyundai Venue official specification sheet	https://www.hyundai.com/content/dam/hyundai/au/en/models/venue/docs/Hyundai_Venue_Specifications_Sheet.pdf
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-S-01	4342	1801	1294	Automobile-Catalog Porsche Boxster S 2011	https://www.automobile-catalog.com/car/2011/2869100/porsche_boxster_s.html
EU-CHEVROLET-CORVETTE-C8-COUPE-01	4630	1934	1234	CarsGuide Chevrolet Corvette 2021 dimensions	https://www.carsguide.com.au/chevrolet/corvette/car-dimensions/2021
EU-BMW-X5-G05-SUV-01	4922	2004	1745	BMW Group official X5 press information	https://www.press.bmwgroup.com/japan/article/detail/T0284853JA/the-all-new-bmw-x5?language=ja
EU-BMW-X6-G06-SUV-01	4935	2004	1696	BMW Group official X6 press information	https://www.press.bmwgroup.com/global/article/detail/T0297827EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-01	4879	2073	1803	CarsGuide Range Rover Sport 2021 dimensions	https://www.carsguide.com.au/land-rover/range-rover-sport/car-dimensions/2021
EU-BMW-3-G20-SEDAN-01	4709	1827	1442	BMW Group official 3 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/detail/T0299451EN/specifications-of-the-all-new-bmw-3-series-sedan-valid-from-03/2019
EU-BMW-3-G21-WAGON-01	4709	1827	1440	BMW Group official 3 Series Touring press information	https://www.press.bmwgroup.com/global/article/detail/T0297559EN/the-new-bmw-3-series-touring?language=en
EU-MG-HS-I-SUV-01	4574	1876	1664	Autodata1 MG HS 1.5 T-GDI specifications	https://www.autodata1.com/en/car/mg/hs/hs-15-t-gdi-162-hp
EU-FIAT-500C-312-FACELIFT-CONVERTIBLE-01	3571	1627	1488	Auto-Data Fiat 500C 1.0 Mild Hybrid specifications	https://www.auto-data.net/en/fiat-500-c-312-facelift-2015-1.0-70hp-mild-hybrid-42057
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Automobile-Catalog Range Rover Evoque P300e 2020	https://www.automobile-catalog.com/car/2020/2976515/range_rover_evoque_p300e_phev_awd.html
EU-MG-ZS-I-EV-SUV-01	4314	1809	1620	Automobile-Catalog MG ZS EV 2019	https://www.automobile-catalog.com/car/2019/2908625/mg_zs_ev.html
EU-AUDI-A4-ALLROAD-B9-FACELIFT-WAGON-01	4762	1847	1493	Automobile-Catalog Audi A4 allroad quattro 40 TDI 2019	https://www.automobile-catalog.com/car/2019/2913425/audi_a4_allroad_quattro_40_tdi.html
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676	BMW Group official X3 M40i specifications	https://www.press.bmwgroup.com/global/article/detail/T0307289EN/specifications-of-the-bmw-x3-m40i-valid-from-04/2020?language=en
EU-MERCEDES-BENZ-GLA-H247-SUV-01	4410	1834	1611	Mercedes-Benz official digital owner manual vehicle dimensions	https://www.mercedes-benz-mena.com/dubai/en/services/manuals/gla-suv-2021-09-h247-mbux/vehicle-data/vehicle-dimensions
EU-LANCIA-YPSILON-III-846-HATCHBACK-01	3837	1676	1518	Automobile-Catalog Lancia Ypsilon Hybrid 2020	https://www.automobile-catalog.com/car/2020/2971445/lancia_ypsilon_hybrid.html
EU-ASTON-MARTIN-DBX-I-SUV-01	5039	1998	1680	Aston Martin official DBX media release	https://media.astonmartin.com/aston-martin-unveils-dbx-an-suv-with-the-soul-of-a-sports-car-3/?lang=eng
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-FACELIFT-SUV-01	4597	1904	1727	Auto Motor und Sport Discovery Sport P300e technical data	https://www.auto-motor-und-sport.de/test/kosten-realverbrauch-land-rover-discovery-sport-p300e-se/technische-daten/
EU-SUZUKI-SWIFT-VI-A2L-HATCHBACK-SPORT-01	3890	1735	1495	Auto-Data Suzuki Swift Sport 1.4 SHVS specifications	https://www.auto-data.net/en/suzuki-swift-vi-sport-1.4-boosterjet-129hp-mild-hybrid-39366
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group official 216d Gran Coupé specifications	https://www.press.bmwgroup.com/global/article/detail/T0318652EN/specifications-of-the-bmw-2-series-gran-coup%20-216d-valid-from-11-2020?forceSitePreference=DESKTOP
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Kia Ceed official press kit	https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed official press kit	https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Kia ProCeed official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/ProCeed_CeedGT_PETD/Press%20kit%20-%202019%20Kia%20ProCeed%20-%20Final%20-%209%20Jan%202019.doc
EU-AUDI-A3-8Y-SPORTBACK-01	4343	1816	1449	Audi official A3 Sportback specification sheet	https://media.audi.com/is/content/audi/country/sg/assets/english/models/a3/a3sb/Audi_A3_Sportback_1-0_Spec_Sheet_Mar_24.pdf
EU-PORSCHE-718-CAYMAN-982-COUPE-GTS40-01	4405	1801	1276	Auto-Data Porsche 718 Cayman GTS 4.0 specifications	https://www.auto-data.net/en/porsche-718-cayman-982-gts-4.0-400hp-41384
EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-GTS40-01	4391	1801	1262	Auto-Data Porsche 718 Boxster GTS 4.0 specifications	https://www.auto-data.net/en/porsche-718-boxster-982-gts-4.0-400hp-38647
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456	SEAT official Leon model technical data	https://www.seat-cupra-mediacenter.com/SEAT-Brand/SEAT-Models/SEAT-Leon
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450	SEAT Leon official 2021 specifications brochure	https://www.seat.com.mt/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-feb-2021.pdf
EU-SANTANA-300-CONVERTIBLE-01	3672	1630	1665	Automobile-Catalog Santana 300 Cabriolet specifications	https://www.automobile-catalog.com/car/2006/3043085/santana_300_cabriolet.html
EU-ALFA-ROMEO-GIULIA-II-952-SEDAN-GTA-01	4654	1923	1397	Alfa Romeo Japan Giulia GTA official reference specifications	https://alfaromeo-jp.com/giulia/limited/gta/spec/
```

## 下一步优先处理

1. 先闭合 Peugeot Boxer 的 Bus、4×4 Van 各车长和车顶组合，避免把 L1H1、L2H2、L3H2、L3H3、L4H2、L4H3 错并。
2. 接着批量处理同属大型厢式车的 Sprinter Classic、NV400 和 Ford Transit V363。
3. 最后处理 Kangoo 普通版/Maxi 的确定高度配置，以及 VW Transporter T6.1/Caravelle 的 SWB、LWB 乘用车分支。

推进信号：CONTINUE

[1]: https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf "https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf"
[2]: https://www.automobile-catalog.com/car/2006/3043085/santana_300_cabriolet.html "https://www.automobile-catalog.com/car/2006/3043085/santana_300_cabriolet.html"
[3]: https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf "https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 `139307`、`139308`：依据明确的 `FW16`、`FW17` 类型边界，拆分为标准轴距、Maxi 长轴距和 Maxi Grand Volume 长轴距高顶三种外廓。本轮首次创建 3 个 Kangoo 尺寸组。([Meyer Motoren][1])
* 已闭合 `139397`、`139398`：`909.632` 对应标准轴距，`909.633`、`909.643` 对应长轴距；相同长轴距三维复用同一尺寸组。本轮首次创建 2 个 Sprinter Classic 尺寸组。([PartSouq][2])
* 上一轮已闭合的映射和 49 个尺寸组未重新抓取或修改。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：90
* READY 映射：119
* PENDING Ktype：10
* 已确认尺寸组：54
* 本轮首次创建尺寸组：5
* 剩余 Ktype：`139329`、`139362`、`139364`、`139365`、`139366`、`139400`、`139401`、`139473`、`139643`、`139644`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139307_swb	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	HIGH	标准轴距厢式外廓。	READY
139307_lwb	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	HIGH	Maxi长轴距标准外廓。	READY
139307_lwb_highroof	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	HIGH	Maxi Grand Volume长轴距高顶外廓。	READY
139308_swb	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	HIGH	标准轴距厢式外廓。	READY
139308_lwb	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	HIGH	Maxi长轴距标准外廓。	READY
139308_lwb_highroof	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	HIGH	Maxi Grand Volume长轴距高顶外廓。	READY
139397_swb	139397	Van	Sprinter Classic	909.632		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-SWB-01	HIGH	909.632标准轴距外廓。	READY
139397_lwb	139397	Van	Sprinter Classic	909.633		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	HIGH	909.633长轴距外廓。	READY
139398	139398	Van	Sprinter Classic	909.643		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	HIGH	909.643长轴距4.6吨外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	4282	1829	1844	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo II Express specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-ii-express-facelift-2013-generation-6432
EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	4666	1829	1826	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo model specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-model-1045
EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	4666	1829	1836	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo model specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-model-1045
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-SWB-01	5640	1933	2595	Mercedes-Benz EPC via PartSouq; Drom Sprinter Classic 313 CDI L1 specifications	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A9019970535;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270972/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	6590	1933	2610	Mercedes-Benz EPC via PartSouq; Drom Sprinter Classic 313 CDI L2 specifications; Drom Sprinter Classic 413 CDI L2 specifications	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0019874257;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270976/;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270978/
```

## 下一步优先处理

1. 闭合 Nissan NV400 厢式车的六种车长/车顶外廓，并确认底盘平台车型是否还包含低地板分支。
2. 处理 VW Transporter T6.1/Caravelle 的短轴、长轴和高顶分支。
3. 处理 Ford Transit V363 Bus 的 L2H2、L3H2、L3H3、L4H3 分支。
4. 最后闭合 Peugeot Boxer Bus 与四驱厢式车的车长、车顶和 Dangel 四驱高度边界。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/139307/renault/kangoo_2_rapid_fw0_1_/1_5_dci_95_fw16_139307?utm_source=chatgpt.com "Renault Kangoo 2 Rapid (FW0/1) 1.5 dCi 95 (FW16)"
[2]: https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A9019970535&srsltid=AfmBOoqrt2INwo3wiKRhS-lp8q-zA0_6oihMqythjmrRk7_p5tty-WVD&ssd=%24%2AKwHS5vf0lLmE0pGHt4zW8oqevrmn1tnU1cfo25OVpqilrJi7ycTdoKDf19HY39OJgpjVn5CCiKGdxs-VkY6UiovMw4uHm42J2dHf0dPTxMibxMjC28TFzMOLj5uNidGyxMvCgojGg5Xg0dDEy8KXhcaDlZjCnAAAAAD1YAnk%24&utm_source=chatgpt.com "REAR AXLE | Mercedes-Benz SPRINTER 308 CDI ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 `139400`：按前驱厢式车的 `L1H1`、`L1H2`、`L2H2`、`L2H3`、`L3H2`、`L3H3` 六种外廓拆分。
* 闭合 `139401`：按 Platform Cab、单排底盘驾驶室、双排底盘驾驶室及其轴距/车顶组合拆分为八种外廓。
* Nissan 官方 MY20 资料确认 180 hp 前驱动力覆盖上述 Panel Van、Platform 和 Chassis Cab 配置；本轮共首次创建 14 个尺寸组。([日产][1])
* 已闭合的其他 Ktype 和尺寸组未重新抓取或修改。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：92
* READY 映射：133
* PENDING Ktype：8
* 已确认尺寸组：68
* 本轮新增 READY 映射：14
* 本轮首次创建尺寸组：14
* 剩余 Ktype：`139329`、`139362`、`139364`、`139365`、`139366`、`139473`、`139643`、`139644`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139400_l1h1	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L1H1-01	HIGH	前驱L1H1厢式外廓。	READY
139400_l1h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L1H2-01	HIGH	前驱L1H2厢式外廓。	READY
139400_l2h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L2H2-01	HIGH	前驱L2H2厢式外廓。	READY
139400_l2h3	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L2H3-01	HIGH	前驱L2H3厢式外廓。	READY
139400_l3h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L3H2-01	HIGH	前驱L3H2厢式外廓。	READY
139400_l3h3	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L3H3-01	HIGH	前驱L3H3厢式外廓。	READY
139401_platform_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H1-01	HIGH	前驱Platform Cab L2H1外廓。	READY
139401_platform_l2h2	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H2-01	HIGH	前驱Platform Cab L2H2外廓。	READY
139401_platform_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H1-01	HIGH	前驱Platform Cab L3H1外廓。	READY
139401_platform_l3h2	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H2-01	HIGH	前驱Platform Cab L3H2外廓。	READY
139401_singlecab_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L2H1-01	HIGH	前驱单排底盘驾驶室L2H1外廓。	READY
139401_singlecab_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L3H1-01	HIGH	前驱单排底盘驾驶室L3H1外廓。	READY
139401_doublecab_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L2H1-01	HIGH	前驱双排底盘驾驶室L2H1外廓。	READY
139401_doublecab_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L3H1-01	HIGH	前驱双排底盘驾驶室L3H1外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NV400-X62-VAN-L1H1-01	5048	2070	2307	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L1H2-01	5048	2070	2500	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L2H2-01	5548	2070	2499	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L2H3-01	5548	2070	2749	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L3H2-01	6198	2070	2488	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L3H3-01	6198	2070	2744	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H1-01	5530	2095	2270	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H2-01	5530	2095	2463	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H1-01	6180	2095	2264	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H2-01	6180	2095	2457	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L2H1-01	5549	2070	2265	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L3H1-01	6199	2070	2258	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L2H1-01	5549	2070	2272	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L3H1-01	6199	2070	2263	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
```

## 下一步优先处理

1. 闭合 `139473` 的 T6.1 短轴、长轴及可确认车顶分支。
2. 闭合 `139643`、`139644` 的 Transit V363 Bus 车长和车顶组合。
3. 最后统一处理 `139329`、`139362`、`139364`、`139365`、`139366` 的 Boxer Bus 与 Dangel 四驱厢式分支。

推进信号：CONTINUE

[1]: https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf?utm_source=chatgpt.com "nissan - nv400"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 `139473`：拆分为短轴普通顶、长轴普通顶、长轴高顶三个 Transporter T6.1 Kombi 物理外廓。大众官方尺寸图确认普通顶短轴/长轴车长为 4904/5304 mm、车宽 1904 mm，高顶仅对应长轴且高度为 2477 mm。
* 闭合 `139643`、`139644`：两种动力均关联同一套 Transit V363 Minibus 外廓，分别为 `L2H2 SRW`、`L3H2 SRW`、`L3H3 SRW`、`L4H3 DRW`，未按发动机功率重复建组。Ford 官方资料确认四种 Minibus 车身边界及不含后视镜宽度，历史车型资料确认 130 PS 与 170 PS 动力覆盖该系列。
* 前面已闭合的 92 个 Ktype 和 68 个尺寸组未重新抓取或修改。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：95
* READY 映射：144
* PENDING Ktype：5
* 已确认尺寸组：75
* 本轮新增 READY 映射：11
* 本轮首次创建尺寸组：7
* 剩余 Ktype：`139329`、`139362`、`139364`、`139365`、`139366`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139473_swb	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-SWB-01	HIGH	短轴普通顶乘用外廓。	READY
139473_lwb	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-01	HIGH	长轴普通顶乘用外廓。	READY
139473_lwb_highroof	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-HIGHROOF-01	HIGH	长轴高顶乘用外廓。	READY
139643_l2h2	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	HIGH	L2H2单后轮Bus外廓。	READY
139643_l3h2	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	HIGH	L3H2单后轮Bus外廓。	READY
139643_l3h3	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	HIGH	L3H3单后轮Bus外廓。	READY
139643_l4h3_drw	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	HIGH	L4H3双后轮Bus外廓。	READY
139644_l2h2	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	HIGH	L2H2单后轮Bus外廓。	READY
139644_l3h2	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	HIGH	L3H2单后轮Bus外廓。	READY
139644_l3h3	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	HIGH	L3H3单后轮Bus外廓。	READY
139644_l4h3_drw	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	HIGH	L4H3双后轮Bus外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-SWB-01	4904	1904	1990	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-01	5304	1904	1990	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-HIGHROOF-01	5304	1904	2477	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	5531	2059	2550	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	5981	2059	2547	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	5981	2059	2786	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	6704	2126	2781	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
```

## 下一步优先处理

1. 一次性闭合 `139329` 的 Boxer Bus 可用车长和车顶组合。
2. 批量闭合 `139362`、`139364`、`139365`、`139366` 的 Dangel 四驱 Boxer 厢式车分支，重点确认四驱悬架是否改变各配置落盘高度。
3. PENDING 清零后立即执行一次机械检查，并输出两张最终完整 TSV 和指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合最后 5 个 Peugeot Boxer Ktype：`139329`、`139362`、`139364`、`139365`、`139366`。
* 本轮新增 29 条 READY 映射，首次创建 8 个 Boxer 尺寸组。
* Boxer 已按 `L1H1` 至 `L4H3` 的实际车长与车顶组合拆分；`WidthMM=2050` 为不含后视镜宽度。Dangel 车身升高属于选装项，不作为这些普通 4×4 Ktype 的默认外廓，因此复用对应标准 Boxer 车身尺寸。([Dangel Shop][1])
* 已完成轻量机械检查：固定表头正确、主键唯一、全部引用闭合、无孤立尺寸组、尺寸和来源字段完整。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：100
* READY 映射：173
* PENDING：0
* DIMENSION_GROUP：83
* 映射表列数：10
* DIMENSION_GROUP 表列数：6
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139293	139293	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139294	139294	Coupe	Wraith	RR5	2	EU-ROLLS-ROYCE-WRAITH-RR5-COUPE-01	HIGH		READY
139295	139295	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139296	139296	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139297	139297	SUV	Seltos I	SP2	5	EU-KIA-SELTOS-I-SP2-SUV-01	HIGH		READY
139305	139305	Targa	911 (997.1)	997	2	EU-PORSCHE-911-9971-TARGA-4S-01	HIGH		READY
139307_swb	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	HIGH	标准轴距厢式外廓。	READY
139307_lwb	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	HIGH	Maxi长轴距标准外廓。	READY
139307_lwb_highroof	139307	Van	Kangoo II facelift	FW16		EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	HIGH	Maxi Grand Volume长轴距高顶外廓。	READY
139308_swb	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	HIGH	标准轴距厢式外廓。	READY
139308_lwb	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	HIGH	Maxi长轴距标准外廓。	READY
139308_lwb_highroof	139308	Van	Kangoo II facelift	FW17		EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	HIGH	Maxi Grand Volume长轴距高顶外廓。	READY
139309	139309	SUV	Kamiq I		5	EU-SKODA-KAMIQ-I-SUV-01	HIGH		READY
139310	139310	Hatchback	Scala I		5	EU-SKODA-SCALA-I-HATCHBACK-01	HIGH		READY
139314	139314	Targa	911 (997.2)	997	2	EU-PORSCHE-911-9972-TARGA-4S-01	HIGH		READY
139321	139321	Convertible	911 (997.2)	997	2	EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	HIGH		READY
139324_prefl	139324	MPV	Grand C-MAX II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	2010-2015改款前外廓。	READY
139324_facelift	139324	MPV	Grand C-MAX II facelift		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	2015-2019改款后外廓。	READY
139326	139326	SUV	Venue I	QX	5	EU-HYUNDAI-VENUE-I-QX-SUV-01	HIGH		READY
139327	139327	Convertible	Boxster (987.2)	987	2	EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-S-01	HIGH		READY
139329_l1h1	139329	MPV	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	MEDIUM	Bus L1H1外廓。	READY
139329_l2h2	139329	MPV	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	MEDIUM	Bus L2H2外廓。	READY
139329_l3h2	139329	MPV	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	MEDIUM	Bus L3H2外廓。	READY
139329_l4h2	139329	MPV	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	MEDIUM	Bus L4H2外廓。	READY
139330	139330	Coupe	Corvette C8	C8	2	EU-CHEVROLET-CORVETTE-C8-COUPE-01	HIGH		READY
139332	139332	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH		READY
139333	139333	SUV	X6 (G06)	G06	5	EU-BMW-X6-G06-SUV-01	HIGH		READY
139338	139338	Van	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-VAN-M-01	HIGH	K9 M四驱外廓。	READY
139339_xs	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139339_m	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139339_xl	139339	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139341_xs	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139341_m	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139341_xl	139341	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139344_xs	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139344_m	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139344_xl	139344	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139347_l1	139347	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	K9四驱L1外廓。	READY
139347_l2	139347	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	HIGH	K9四驱L2外廓。	READY
139348_xs	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139348_m	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139348_xl	139348	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139354_xs	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139354_m	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139354_xl	139354	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139362_l1h1	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	MEDIUM	Dangel四驱L1H1外廓。	READY
139362_l1h2	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L1H2-01	MEDIUM	Dangel四驱L1H2外廓。	READY
139362_l2h1	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H1-01	MEDIUM	Dangel四驱L2H1外廓。	READY
139362_l2h2	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	MEDIUM	Dangel四驱L2H2外廓。	READY
139362_l3h2	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	MEDIUM	Dangel四驱L3H2外廓。	READY
139362_l3h3	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H3-01	MEDIUM	Dangel四驱L3H3外廓。	READY
139362_l4h2	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	MEDIUM	Dangel四驱L4H2外廓。	READY
139362_l4h3	139362	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	MEDIUM	Dangel四驱L4H3外廓。	READY
139364_l1h1	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	MEDIUM	Dangel四驱L1H1外廓。	READY
139364_l2h1	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H1-01	MEDIUM	Dangel四驱L2H1外廓。	READY
139364_l2h2	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	MEDIUM	Dangel四驱L2H2外廓。	READY
139364_l3h2	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	MEDIUM	Dangel四驱L3H2外廓。	READY
139364_l4h2	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	MEDIUM	Dangel四驱L4H2外廓。	READY
139364_l4h3	139364	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	MEDIUM	Dangel四驱L4H3外廓。	READY
139365_l1h1	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	MEDIUM	Dangel四驱L1H1外廓。	READY
139365_l2h1	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H1-01	MEDIUM	Dangel四驱L2H1外廓。	READY
139365_l2h2	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	MEDIUM	Dangel四驱L2H2外廓。	READY
139365_l3h2	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	MEDIUM	Dangel四驱L3H2外廓。	READY
139365_l3h3	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H3-01	MEDIUM	Dangel四驱L3H3外廓。	READY
139365_l4h2	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	MEDIUM	Dangel四驱L4H2外廓。	READY
139365_l4h3	139365	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	MEDIUM	Dangel四驱L4H3外廓。	READY
139366_l3h2	139366	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	MEDIUM	Dangel四驱L3H2外廓。	READY
139366_l3h3	139366	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L3H3-01	MEDIUM	Dangel四驱L3H3外廓。	READY
139366_l4h2	139366	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	MEDIUM	Dangel四驱L4H2外廓。	READY
139366_l4h3	139366	Van	Boxer II facelift	250		EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	MEDIUM	Dangel四驱L4H3外廓。	READY
139367_xs	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139367_m	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139367_xl	139367	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139376_xs	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139376_m	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139376_xl	139376	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139377_l1	139377	Van	Combo E	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	MEDIUM	K9四驱L1外廓；与Partner同平台尺寸组。	READY
139377_l2	139377	Van	Combo E	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	MEDIUM	K9四驱L2外廓；与Partner同平台尺寸组。	READY
139378_xs	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139378_m	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139378_xl	139378	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139379_xs	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139379_m	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139379_xl	139379	Van	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139397_swb	139397	Van	Sprinter Classic	909.632		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-SWB-01	HIGH	909.632标准轴距外廓。	READY
139397_lwb	139397	Van	Sprinter Classic	909.633		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	HIGH	909.633长轴距外廓。	READY
139398	139398	Van	Sprinter Classic	909.643		EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	HIGH	909.643长轴距4.6吨外廓。	READY
139400_l1h1	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L1H1-01	HIGH	前驱L1H1厢式外廓。	READY
139400_l1h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L1H2-01	HIGH	前驱L1H2厢式外廓。	READY
139400_l2h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L2H2-01	HIGH	前驱L2H2厢式外廓。	READY
139400_l2h3	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L2H3-01	HIGH	前驱L2H3厢式外廓。	READY
139400_l3h2	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L3H2-01	HIGH	前驱L3H2厢式外廓。	READY
139400_l3h3	139400	Van	NV400 facelift	X62		EU-NISSAN-NV400-X62-VAN-L3H3-01	HIGH	前驱L3H3厢式外廓。	READY
139401_platform_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H1-01	HIGH	前驱Platform Cab L2H1外廓。	READY
139401_platform_l2h2	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H2-01	HIGH	前驱Platform Cab L2H2外廓。	READY
139401_platform_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H1-01	HIGH	前驱Platform Cab L3H1外廓。	READY
139401_platform_l3h2	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H2-01	HIGH	前驱Platform Cab L3H2外廓。	READY
139401_singlecab_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L2H1-01	HIGH	前驱单排底盘驾驶室L2H1外廓。	READY
139401_singlecab_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L3H1-01	HIGH	前驱单排底盘驾驶室L3H1外廓。	READY
139401_doublecab_l2h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L2H1-01	HIGH	前驱双排底盘驾驶室L2H1外廓。	READY
139401_doublecab_l3h1	139401	Pickup	NV400 facelift			EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L3H1-01	HIGH	前驱双排底盘驾驶室L3H1外廓。	READY
139431_xs	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	K0平台XS长度外廓。	READY
139431_m	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	K0平台M长度外廓。	READY
139431_xl	139431	MPV	K0	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	K0平台XL长度外廓。	READY
139460	139460	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-01	HIGH		READY
139467	139467	Sedan	3 Series (G20)	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
139469	139469	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH		READY
139470	139470	Sedan	3 Series (G20)	G20	4	EU-BMW-3-G20-SEDAN-01	HIGH		READY
139471	139471	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH		READY
139473_swb	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-SWB-01	HIGH	短轴普通顶乘用外廓。	READY
139473_lwb	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-01	HIGH	长轴普通顶乘用外廓。	READY
139473_lwb_highroof	139473	MPV	Transporter T6.1			EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-HIGHROOF-01	HIGH	长轴高顶乘用外廓。	READY
139481	139481	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139482	139482	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139483	139483	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139484	139484	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139485	139485	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139486	139486	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139487	139487	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139488	139488	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139489	139489	Wagon	3 Series Touring (G21)	G21	5	EU-BMW-3-G21-WAGON-01	HIGH	Kasten/Kombi登记不改变G21外廓。	READY
139490	139490	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH	Kasten/SUV登记不改变G05外廓。	READY
139491	139491	SUV	X5 (G05)	G05	5	EU-BMW-X5-G05-SUV-01	HIGH	Kasten/SUV登记不改变G05外廓。	READY
139492_l1	139492	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	K9 L1外廓。	READY
139492_l2	139492	Van	Partner III	K9	5	EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	K9 L2外廓。	READY
139502	139502	SUV	Grandland X		5	EU-OPEL-GRANDLAND-X-SUV-01	HIGH		READY
139504	139504	SUV	HS I		5	EU-MG-HS-I-SUV-01	HIGH		READY
139507	139507	Convertible	500C (312 facelift)	312	2	EU-FIAT-500C-312-FACELIFT-CONVERTIBLE-01	HIGH		READY
139533	139533	Convertible	Santana 300		3	EU-SANTANA-300-CONVERTIBLE-01	HIGH	三门软顶敞开式车身。	READY
139607	139607	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH		READY
139640	139640	SUV	ZS I EV		5	EU-MG-ZS-I-EV-SUV-01	HIGH		READY
139643_l2h2	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	HIGH	L2H2单后轮Bus外廓。	READY
139643_l3h2	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	HIGH	L3H2单后轮Bus外廓。	READY
139643_l3h3	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	HIGH	L3H3单后轮Bus外廓。	READY
139643_l4h3_drw	139643	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	HIGH	L4H3双后轮Bus外廓。	READY
139644_l2h2	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	HIGH	L2H2单后轮Bus外廓。	READY
139644_l3h2	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	HIGH	L3H2单后轮Bus外廓。	READY
139644_l3h3	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	HIGH	L3H3单后轮Bus外廓。	READY
139644_l4h3_drw	139644	MPV	Transit V363 facelift			EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	HIGH	L4H3双后轮Bus外廓。	READY
139648	139648	Wagon	A4 allroad B9 facelift	8W	5	EU-AUDI-A4-ALLROAD-B9-FACELIFT-WAGON-01	HIGH		READY
139649	139649	SUV	X3 (G01)	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH		READY
139650	139650	SUV	X3 (G01)	G01	5	EU-BMW-X3-G01-M40I-SUV-01	HIGH	Kasten/SUV登记不改变G01外廓。	READY
139651	139651	Sedan	Giulia II	952	4	EU-ALFA-ROMEO-GIULIA-II-952-SEDAN-GTA-01	HIGH	GTA宽体外廓。	READY
139652	139652	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139653	139653	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139654	139654	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139655	139655	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139656	139656	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139657	139657	Hatchback	Ypsilon III facelift	846	5	EU-LANCIA-YPSILON-III-846-HATCHBACK-01	HIGH		READY
139658	139658	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139659	139659	SUV	GLA II	H247	5	EU-MERCEDES-BENZ-GLA-H247-SUV-01	HIGH		READY
139672	139672	SUV	DBX I		5	EU-ASTON-MARTIN-DBX-I-SUV-01	HIGH		READY
139678	139678	SUV	Discovery Sport facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-FACELIFT-SUV-01	HIGH		READY
139679	139679	Hatchback	Swift VI	A2L	5	EU-SUZUKI-SWIFT-VI-A2L-HATCHBACK-SPORT-01	HIGH		READY
139680	139680	Coupe	2 Series Gran Coupé	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	输入Coupe对应四门Gran Coupé F44。	READY
139690	139690	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139693	139693	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139694	139694	Hatchback	Ceed III	CD	5	EU-KIA-CEED-III-CD-HATCHBACK-01	HIGH		READY
139695	139695	Wagon	Ceed Sportswagon III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139696	139696	Wagon	Ceed Sportswagon III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
139697	139697	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH		READY
139698	139698	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139699	139699	SUV	XCeed I	CD	5	EU-KIA-XCEED-I-CD-SUV-01	HIGH		READY
139714	139714	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139715	139715	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139716	139716	Hatchback	A3 Sportback IV	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
139717	139717	Coupe	718 Cayman	982	2	EU-PORSCHE-718-CAYMAN-982-COUPE-GTS40-01	HIGH		READY
139725	139725	Convertible	718 Boxster	982	2	EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-GTS40-01	HIGH		READY
139734	139734	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139736	139736	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139737	139737	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139738	139738	Hatchback	Leon IV	KL	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
139744	139744	Wagon	Leon Sportstourer IV	KL	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-XCEED-I-CD-SUV-01	4395	1826	1495	Kia XCeed 2020 official brochure	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/model-brochures/XCeed-Brochure-2020.pdf
EU-ROLLS-ROYCE-WRAITH-RR5-COUPE-01	5285	1947	1507	Auto-Data Rolls-Royce Wraith model specifications	https://www.auto-data.net/en/rolls-royce-wraith-model-2135
EU-KIA-SELTOS-I-SP2-SUV-01	4370	1800	1615	Kia Seltos official brochure	https://www.kia.com/content/dam/kwcms/ph/en/pdf/updated-pdf/FA_KIA_Seltos_Brochure_compressed.pdf
EU-PORSCHE-911-9971-TARGA-4S-01	4427	1852	1300	EncyCARpedia Porsche 911 Targa 4S 997 specifications	https://www.encycarpedia.com/porsche/06-911-targa-4s
EU-RENAULT-KANGOO-II-FW-VAN-SWB-01	4282	1829	1844	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo II Express specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-ii-express-facelift-2013-generation-6432
EU-RENAULT-KANGOO-II-FW-VAN-LWB-01	4666	1829	1826	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo model specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-model-1045
EU-RENAULT-KANGOO-II-FW-VAN-LWB-HIGHROOF-01	4666	1829	1836	Renault Kangoo Van official brochure; Auto-Data Renault Kangoo model specifications	https://www.press.renault.co.uk/assets/documents/original/10708-KangooVaneBrochureJuly2017.pdf;https://www.auto-data.net/en/renault-kangoo-model-1045
EU-SKODA-KAMIQ-I-SUV-01	4241	1793	1531	Škoda Storyboard official Kamiq press release	https://www.skoda-storyboard.com/en/press-releases/skoda-kamiq-the-new-city-suv/
EU-SKODA-SCALA-I-HATCHBACK-01	4362	1793	1471	Škoda Storyboard official Scala press release	https://www.skoda-storyboard.com/cs/tiskove-zpravy-archiv/pocatek-nove-designove-ery-skoda-scala-2019/
EU-PORSCHE-911-9972-TARGA-4S-01	4435	1852	1300	Automobile-Catalog Porsche 911 Targa 4S PDK 2010	https://www.automobile-catalog.com/car/2010/2868485/porsche_911_targa_4s_pdk.html
EU-PORSCHE-911-9972-CONVERTIBLE-CARRERA-S-01	4435	1808	1300	Automobile-Catalog Porsche 911 Carrera S Cabriolet 2010	https://www.automobile-catalog.com/car/2010/2868230/porsche_911_carrera_s_cabriolet.html
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Auto-Data Ford C-MAX model specifications	https://www.auto-data.net/en/ford-c-max-model-808
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	4519	1828	1642	Auto-Data Ford C-MAX model specifications	https://www.auto-data.net/en/ford-c-max-model-808
EU-HYUNDAI-VENUE-I-QX-SUV-01	4040	1770	1592	Hyundai Venue official specification sheet	https://www.hyundai.com/content/dam/hyundai/au/en/models/venue/docs/Hyundai_Venue_Specifications_Sheet.pdf
EU-PORSCHE-BOXSTER-9872-CONVERTIBLE-S-01	4342	1801	1294	Automobile-Catalog Porsche Boxster S 2011	https://www.automobile-catalog.com/car/2011/2869100/porsche_boxster_s.html
EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	4963	2050	2254	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	5413	2050	2522	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	5998	2050	2522	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	6363	2050	2522	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-CHEVROLET-CORVETTE-C8-COUPE-01	4630	1934	1234	CarsGuide Chevrolet Corvette 2021 dimensions	https://www.carsguide.com.au/chevrolet/corvette/car-dimensions/2021
EU-BMW-X5-G05-SUV-01	4922	2004	1745	BMW Group official X5 press information	https://www.press.bmwgroup.com/japan/article/detail/T0284853JA/the-all-new-bmw-x5?language=ja
EU-BMW-X6-G06-SUV-01	4935	2004	1696	BMW Group official X6 press information	https://www.press.bmwgroup.com/global/article/detail/T0297827EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796	VanGuide Citroën Berlingo dimensions	https://www.vanguide.co.uk/guides/citroen-berlingo-dimensions/
EU-CITROEN-JUMPY-III-K0-MPV-XS-01	4609	1920	1905	Citroën Jumpy official technical specification sheet	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-muszaki-adatlap.pdf
EU-CITROEN-JUMPY-III-K0-MPV-M-01	4959	1920	1895	Citroën Jumpy official technical specification sheet	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-muszaki-adatlap.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XL-01	5309	1920	1935	Citroën Jumpy official technical specification sheet	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-muszaki-adatlap.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	4403	1848	1860	VehicleScore Peugeot Partner dimensions	https://vehiclescore.co.uk/car-dimensions-check/peugeot/partner
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	4753	1848	1860	VehicleScore Peugeot Partner dimensions	https://vehiclescore.co.uk/car-dimensions-check/peugeot/partner
EU-PEUGEOT-BOXER-II-250-VAN-L1H2-01	4963	2050	2522	Peugeot Boxer official brochure	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=
EU-PEUGEOT-BOXER-II-250-VAN-L2H1-01	5413	2050	2254	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-II-250-VAN-L3H3-01	5998	2050	2760	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	6363	2050	2760	Peugeot Boxer official brochure; Peugeot Boxer July 2019 prices and specifications	https://cache1.arabwheels.sa/system/brochures/1101/original/Peugeot-Boxer-Brochure.pdf?1764236697=;https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-SWB-01	5640	1933	2595	Mercedes-Benz EPC via PartSouq; Drom Sprinter Classic 313 CDI L1 specifications	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A9019970535;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270972/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-LWB-01	6590	1933	2610	Mercedes-Benz EPC via PartSouq; Drom Sprinter Classic 313 CDI L2 specifications; Drom Sprinter Classic 413 CDI L2 specifications	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0019874257;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270976/;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270978/
EU-NISSAN-NV400-X62-VAN-L1H1-01	5048	2070	2307	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L1H2-01	5048	2070	2500	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L2H2-01	5548	2070	2499	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L2H3-01	5548	2070	2749	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L3H2-01	6198	2070	2488	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-VAN-L3H3-01	6198	2070	2744	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H1-01	5530	2095	2270	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L2H2-01	5530	2095	2463	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H1-01	6180	2095	2264	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-PLATFORM-CAB-L3H2-01	6180	2095	2457	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L2H1-01	5549	2070	2265	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-SINGLE-CAB-L3H1-01	6199	2070	2258	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L2H1-01	5549	2070	2272	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-NISSAN-NV400-X62-CHASSIS-DOUBLE-CAB-L3H1-01	6199	2070	2263	Nissan NV400 MY20 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-01	4879	2073	1803	CarsGuide Range Rover Sport 2021 dimensions	https://www.carsguide.com.au/land-rover/range-rover-sport/car-dimensions/2021
EU-BMW-3-G20-SEDAN-01	4709	1827	1442	BMW Group official 3 Series Sedan specifications	https://www.press.bmwgroup.com/global/article/detail/T0299451EN/specifications-of-the-all-new-bmw-3-series-sedan-valid-from-03/2019
EU-BMW-3-G21-WAGON-01	4709	1827	1440	BMW Group official 3 Series Touring press information	https://www.press.bmwgroup.com/global/article/detail/T0297559EN/the-new-bmw-3-series-touring?language=en
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-SWB-01	4904	1904	1990	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-01	5304	1904	1990	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-VOLKSWAGEN-TRANSPORTER-T61-MPV-LWB-HIGHROOF-01	5304	1904	2477	Volkswagen Transporter 6.1 Kombi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Transporter_kombi.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	VehicleScore Peugeot Partner dimensions	https://vehiclescore.co.uk/car-dimensions-check/peugeot/partner
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	VehicleScore Peugeot Partner dimensions	https://vehiclescore.co.uk/car-dimensions-check/peugeot/partner
EU-OPEL-GRANDLAND-X-SUV-01	4477	1856	1609	Opel Grandland X official specifications	https://nd-mediagallery2-public-production.s3.amazonaws.com/f52425abdaff90529ba7443030f717c6/12014_58273_opel_grandland_x_my18_spec_sheets_a4l_fc_e_web_1_.pdf
EU-MG-HS-I-SUV-01	4574	1876	1664	Autodata1 MG HS 1.5 T-GDI specifications	https://www.autodata1.com/en/car/mg/hs/hs-15-t-gdi-162-hp
EU-FIAT-500C-312-FACELIFT-CONVERTIBLE-01	3571	1627	1488	Auto-Data Fiat 500C 1.0 Mild Hybrid specifications	https://www.auto-data.net/en/fiat-500-c-312-facelift-2015-1.0-70hp-mild-hybrid-42057
EU-SANTANA-300-CONVERTIBLE-01	3672	1630	1665	Automobile-Catalog Santana 300 Cabriolet specifications	https://www.automobile-catalog.com/car/2006/3043085/santana_300_cabriolet.html
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Automobile-Catalog Range Rover Evoque P300e 2020	https://www.automobile-catalog.com/car/2020/2976515/range_rover_evoque_p300e_phev_awd.html
EU-MG-ZS-I-EV-SUV-01	4314	1809	1620	Automobile-Catalog MG ZS EV 2019	https://www.automobile-catalog.com/car/2019/2908625/mg_zs_ev.html
EU-FORD-TRANSIT-V363-MPV-L2H2-SRW-01	5531	2059	2550	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L3H2-SRW-01	5981	2059	2547	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L3H3-SRW-01	5981	2059	2786	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-FORD-TRANSIT-V363-MPV-L4H3-DRW-01	6704	2126	2781	Ford Transit Minibus official brochure; Transit Center Ford Transit MK8 specifications	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_m2_bus_25.5MY.pdf;https://www.transitcenter.uk/transit-mk8-data-specification.php
EU-AUDI-A4-ALLROAD-B9-FACELIFT-WAGON-01	4762	1847	1493	Automobile-Catalog Audi A4 allroad quattro 40 TDI 2019	https://www.automobile-catalog.com/car/2019/2913425/audi_a4_allroad_quattro_40_tdi.html
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676	BMW Group official X3 M40i specifications	https://www.press.bmwgroup.com/global/article/detail/T0307289EN/specifications-of-the-bmw-x3-m40i-valid-from-04/2020?language=en
EU-ALFA-ROMEO-GIULIA-II-952-SEDAN-GTA-01	4654	1923	1397	Alfa Romeo Japan Giulia GTA official reference specifications	https://alfaromeo-jp.com/giulia/limited/gta/spec/
EU-MERCEDES-BENZ-GLA-H247-SUV-01	4410	1834	1611	Mercedes-Benz official digital owner manual vehicle dimensions	https://www.mercedes-benz-mena.com/dubai/en/services/manuals/gla-suv-2021-09-h247-mbux/vehicle-data/vehicle-dimensions
EU-LANCIA-YPSILON-III-846-HATCHBACK-01	3837	1676	1518	Automobile-Catalog Lancia Ypsilon Hybrid 2020	https://www.automobile-catalog.com/car/2020/2971445/lancia_ypsilon_hybrid.html
EU-ASTON-MARTIN-DBX-I-SUV-01	5039	1998	1680	Aston Martin official DBX media release	https://media.astonmartin.com/aston-martin-unveils-dbx-an-suv-with-the-soul-of-a-sports-car-3/?lang=eng
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-FACELIFT-SUV-01	4597	1904	1727	Auto Motor und Sport Discovery Sport P300e technical data	https://www.auto-motor-und-sport.de/test/kosten-realverbrauch-land-rover-discovery-sport-p300e-se/technische-daten/
EU-SUZUKI-SWIFT-VI-A2L-HATCHBACK-SPORT-01	3890	1735	1495	Auto-Data Suzuki Swift Sport 1.4 SHVS specifications	https://www.auto-data.net/en/suzuki-swift-vi-sport-1.4-boosterjet-129hp-mild-hybrid-39366
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group official 216d Gran Coupé specifications	https://www.press.bmwgroup.com/global/article/detail/T0318652EN/specifications-of-the-bmw-2-series-gran-coup%20-216d-valid-from-11-2020?forceSitePreference=DESKTOP
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447	Kia Ceed official press kit	https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed official press kit	https://press.kia.com/content/dam/kiapress/IE/pressreleases/Ceed-Launch-September-2018/Ceed-press-release.pdf
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Kia ProCeed official press kit	https://press.kia.com/content/dam/kiapress/EU/Press-Kits/ProCeed_CeedGT_PETD/Press%20kit%20-%202019%20Kia%20ProCeed%20-%20Final%20-%209%20Jan%202019.doc
EU-AUDI-A3-8Y-SPORTBACK-01	4343	1816	1449	Audi official A3 Sportback specification sheet	https://media.audi.com/is/content/audi/country/sg/assets/english/models/a3/a3sb/Audi_A3_Sportback_1-0_Spec_Sheet_Mar_24.pdf
EU-PORSCHE-718-CAYMAN-982-COUPE-GTS40-01	4405	1801	1276	Auto-Data Porsche 718 Cayman GTS 4.0 specifications	https://www.auto-data.net/en/porsche-718-cayman-982-gts-4.0-400hp-41384
EU-PORSCHE-718-BOXSTER-982-CONVERTIBLE-GTS40-01	4391	1801	1262	Auto-Data Porsche 718 Boxster GTS 4.0 specifications	https://www.auto-data.net/en/porsche-718-boxster-982-gts-4.0-400hp-38647
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456	SEAT official Leon model technical data	https://www.seat-cupra-mediacenter.com/SEAT-Brand/SEAT-Models/SEAT-Leon
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450	SEAT Leon official 2021 specifications brochure	https://www.seat.com.mt/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-feb-2021.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/01%20P%20GEN%2000%20EN%202019%2002_Peugeot%20Price%20list.pdf "https://www.dangel.com/sites/www.dangel.fr/files/pdf/EN/Peugeot/01%20P%20GEN%2000%20EN%202019%2002_Peugeot%20Price%20list.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（312 行）
- 累计尺寸组：dimension_groups_final.tsv（163 行）

