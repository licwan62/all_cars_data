# 任务：all 第 3801-3900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0039__63f6ed90


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3801-3900 行

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
all 第 3801-3900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
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
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-CITROEN-ZX-N2-HATCHBACK-16V-01	4085	1718	1375
EU-CITROEN-ZX-N2-HATCHBACK-STD-01	4071	1702	1399
EU-CITROEN-ZX-N2-HATCHBACK-VOLCANE-01	4085	1707	1386
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ40-XJ81-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1377
EU-JAGUAR-XJ-SERIES-III-SEDAN-02	4959	1770	1372
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375
EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457
EU-MAZDA-626-I-CB-SEDAN-4D-01	4305	1660	1370
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1350
EU-MAZDA-626-II-GC-HATCHBACK-5D-02	4430	1690	1365
EU-MAZDA-626-II-GC-SEDAN-4D-01	4430	1690	1395
EU-MAZDA-626-II-GC-SEDAN-4D-02	4430	1690	1410
EU-MAZDA-626-III-GD-COUPE-2D-01	4470	1690	1360
EU-MAZDA-626-III-GD-HATCHBACK-5D-01	4535	1690	1375
EU-MAZDA-626-III-GD-SEDAN-4D-01	4535	1690	1410
EU-MAZDA-626-III-GV-WAGON-5D-01	4610	1690	1430
EU-MAZDA-626-IV-GE-HATCHBACK-5D-01	4695	1750	1390
EU-MAZDA-626-IV-GE-SEDAN-4D-01	4695	1750	1400
EU-MAZDA-6-II-GH-FACELIFT-HATCHBACK-5D-01	4755	1795	1440
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-PREFL-01	3714	1683	1414
EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	3955	1690	1365
EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	4620	1730	1395
EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	4620	1730	1395
EU-MITSUBISHI-LANCER-VIII-CXA-HATCHBACK-5D-01	4585	1760	1515
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-ROVER-100-XP-HATCHBACK-3D-01	3521	1550	1377
EU-ROVER-100-XP-HATCHBACK-5D-01	3521	1550	1377
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400
EU-ROVER-800-R17-COUPE-01	4882	1730	1393
EU-ROVER-800-R17-HATCHBACK-FACELIFT-01	4882	1730	1393
EU-ROVER-800-R17-SEDAN-FACELIFT-01	4882	1730	1393
EU-ROVER-800-XX-HATCHBACK-PREFL-01	4693	1730	1398
EU-ROVER-800-XX-SEDAN-PREFL-01	4693	1730	1398
EU-SAAB-9000-CC-FACELIFT-HATCHBACK-5D-01	4667	1764	1420
EU-SAAB-9000-CC-HATCHBACK-5D-01	4620	1764	1430
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420
EU-SAAB-9000-CS-AERO-HATCHBACK-5D-01	4761	1806	1405
EU-SAAB-9000-CS-HATCHBACK-5D-01	4761	1778	1420
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424
EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	4345	1686	1378
EU-VOLVO-440-K-HATCHBACK-PREFL-01	4312	1676	1379
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435
EU-VOLVO-960-SEDAN-4D-01	4871	1750	1411
EU-VOLVO-960-WAGON-5D-01	4850	1750	1434
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Polo	75 1.6	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1994	Oct 1999	2024-03-01	3932
VW	Polo	45 1.0	Schrägheck	Frontantrieb	Benzin	33	45	Oct 1994	Sep 1996	2024-03-01	3933
VW	Passat b3/b4	1.6	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1994	Aug 1996	2024-03-01	3934
VW	Passat b3/b4 variant	1.6	Kombi	Frontantrieb	Benzin	74	101	Jul 1994	Dec 1995	2024-03-01	3935
VW	Golf iii	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Jul 1995	Aug 1997	2024-03-01	3936
VW	Vento	1.6	Stufenheck	Frontantrieb	Benzin	74	101	Oct 1994	Sep 1998	2024-03-01	3937
VW	Golf iii variant	1.6	Kombi	Frontantrieb	Benzin	74	101	Jul 1994	Apr 1999	2024-03-01	3938
VW	Golf iii	1.6	Cabriolet	Frontantrieb	Benzin	74	101	Oct 1994	Feb 1998	2024-03-01	3939
Mazda	6	2.2 D	Kombi	Frontantrieb	Diesel	95	129	Jan 2010	Jul 2013	2024-03-01	3940
VW	Golf iii	1.9 TDI	Cabriolet	Frontantrieb	Diesel	66	90	Aug 1995	May 1998	2024-03-01	3942
Ford USA	Probe ii	2.0 16V	Coupe	Frontantrieb	Benzin	85	116	Oct 1993	Mar 1998	2024-03-01	3943
Ford USA	Probe ii	2.5 V6 24V	Coupe	Frontantrieb	Benzin	119	162	Oct 1993	Mar 1998	2024-03-01	3944
Mercedes-benz	C-Klasse	C 200	Stufenheck	Heckantrieb	Benzin	100	136	Jan 1994	May 2000	2024-03-01	3945
Mercedes-benz	S-Klasse	Sec/cl 420	Coupe	Heckantrieb	Benzin	205	279	Oct 1994	Feb 1999	2024-03-01	3946
Mercedes-benz	E-Klasse	E 36 AMG	Coupe	Heckantrieb	Benzin	200	272	May 1994	Jun 1997	2024-03-01	3947
Mercedes-benz	E-Klasse	E 36 AMG	Cabriolet	Heckantrieb	Benzin	200	272	May 1994	Mar 1998	2024-03-01	3948
Mercedes-benz	E-Klasse	E 36 T AMG	Kombi	Heckantrieb	Benzin	200	272	May 1994	Jun 1996	2024-03-01	3949
Mercedes-benz	C-Klasse	C 36 AMG	Stufenheck	Heckantrieb	Benzin	206	280	May 1994	May 2000	2024-03-01	3950
Mercedes-benz	G-Klasse	G 320	Geländewagen geschlossen	Allrad	Benzin	155	211	Sep 1994	Dec 1997	2024-03-01	3951
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	120	163	Nov 2011	Apr 2015	2024-03-01	3952
Seat	Cordoba	1.4 I	Stufenheck	Frontantrieb	Benzin	44	60	Jun 1994	Oct 2002	2024-03-01	3953
Seat	Cordoba	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Feb 1993	Oct 2002	2024-03-01	3954
Seat	Cordoba	1.8 I	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1993	Sep 2002	2024-03-01	3955
Seat	Cordoba	2.0 I	Stufenheck	Frontantrieb	Benzin	85	115	Feb 1993	Jun 1999	2024-03-01	3956
Seat	Cordoba	1.9 D	Stufenheck	Frontantrieb	Diesel	50	68	Feb 1993	Aug 1996	2024-03-01	3957
Seat	Cordoba	1.9 TD	Stufenheck	Frontantrieb	Diesel	55	75	Feb 1993	Aug 1996	2024-03-01	3958
Seat	Cordoba	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	95	129	Oct 1993	Aug 1996	2024-03-01	3959
Seat	Ibiza ii	1.4 I	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1993	Feb 2002	2024-03-01	3961
Seat	Ibiza ii	1.8 I 16V	Schrägheck	Frontantrieb	Benzin	95	129	Nov 1993	Aug 1996	2024-03-01	3962
Seat	Toledo	1.6 I	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1993	Mar 1999	2024-03-01	3963
Seat	Toledo	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Nov 1993	Dec 1996	2024-03-01	3964
Seat	Toledo	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	110	150	Nov 1993	Mar 1999	2024-03-01	3965
Saab	900 ii	2.0 I	Coupe	Frontantrieb	Benzin	98	133	Dec 1993	Jul 1994	2024-03-01	3966
Saab	900 ii	2.3 -16	Schrägheck	Frontantrieb	Benzin	110	150	Jul 1993	Feb 1998	2024-03-01	3967
Saab	900 ii	2.5 -24 V6	Schrägheck	Frontantrieb	Benzin	125	170	Jul 1993	Feb 1998	2024-03-01	3968
Saab	900 ii	2.0 -16 Turbo	Schrägheck	Frontantrieb	Benzin	136	185	Jul 1993	Feb 1998	2024-03-01	3969
Saab	900 ii	2.0 I	Schrägheck	Frontantrieb	Benzin	96	131	Aug 1994	Feb 1998	2024-03-01	3970
Saab	900 ii	2.3 -16	Cabriolet	Frontantrieb	Benzin	110	150	Dec 1993	Feb 1998	2024-03-01	3971
Saab	900 ii	2.5 -24 V6	Cabriolet	Frontantrieb	Benzin	125	170	Dec 1993	Feb 1998	2024-03-01	3972
Saab	900 ii	2.0 -16 Turbo	Cabriolet	Frontantrieb	Benzin	136	185	Dec 1993	Feb 1998	2024-03-01	3973
Saab	900 ii	2.0 I	Cabriolet	Frontantrieb	Benzin	96	131	Dec 1993	Feb 1998	2024-03-01	3974
Saab	9000	3.0 -24 V6 Cd/cde	Stufenheck	Frontantrieb	Benzin	155	211	Jul 1994	Dec 1998	2024-03-01	3975
Saab	9000	3.0 -24 V6 Cs/cse	Schrägheck	Frontantrieb	Benzin	155	211	Jul 1994	Dec 1998	2024-03-01	3976
Mercedes-benz	S-Klasse	S 400 Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	205	279	Jan 2009	Dec 2013	2024-03-01	3977
Saab	9000	2.0 -16 CS	Schrägheck	Frontantrieb	Benzin	96	131	Sep 1993	Dec 1998	2024-03-01	3978
Mercedes-benz	C-Klasse	C 250 CGI	Kombi	Heckantrieb	Benzin	150	204	Jul 2009	Aug 2014	2024-03-01	3979
BMW	3	318 D	Kombi	Heckantrieb	Diesel	100	136	Jul 2007	Jun 2012	2024-03-01	3980
Volvo	850	2.4	Stufenheck	Frontantrieb	Benzin	106	144	Aug 1994	Dec 1996	2024-03-01	3981
Volvo	850	2.4	Kombi	Frontantrieb	Benzin	125	170	Sep 1992	Dec 1996	2024-03-01	3982
Volvo	960	2.9	Stufenheck	Heckantrieb	Benzin	150	204	Jul 1994	Dec 1996	2024-03-01	3983
Volvo	960	2.9	Kombi	Heckantrieb	Benzin	150	204	Sep 1994	Dec 1996	2024-03-01	3984
Volvo	960	2.5	Stufenheck	Heckantrieb	Benzin	125	170	Jul 1994	Dec 1996	2024-03-01	3985
Volvo	960	2.5	Kombi	Heckantrieb	Benzin	125	170	Aug 1994	Dec 1996	2024-03-01	3986
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	96	131	Aug 1994	Oct 1998	2024-03-01	3987
Volvo	940	2.3	Stufenheck	Heckantrieb	Benzin	85	116	Aug 1994	Jul 1995	2024-03-01	3988
Volvo	940	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	121	165	Aug 1994	Oct 1998	2024-03-01	3989
Volvo	940	2.4 TD Interc.	Stufenheck	Heckantrieb	Diesel	90	122	Aug 1994	Oct 1998	2024-03-01	3990
Volvo	940	2.3	Kombi	Heckantrieb	Benzin	96	131	Aug 1994	Oct 1998	2024-03-01	3991
Volvo	940	2.3	Kombi	Heckantrieb	Benzin	85	116	Aug 1994	Jul 1995	2024-03-01	3992
Volvo	940	2.3 Turbo	Kombi	Heckantrieb	Benzin	121	165	Aug 1994	Oct 1998	2024-03-01	3993
Volvo	940	2.4 TD Interc.	Kombi	Heckantrieb	Diesel	90	122	Aug 1994	Oct 1998	2024-03-01	3994
Lada	Nova	1500	Kombi	Heckantrieb	Benzin	49	67	Aug 1994	Apr 2012	2024-03-01	3995
Lada	Nova	1700	Kombi	Heckantrieb	Benzin	62	84	Aug 1994	Apr 2012	2024-03-01	3996
Volvo	460	2	Stufenheck	Frontantrieb	Benzin	80	109	Aug 1993	Jul 1996	2024-03-01	3997
Volvo	440	2	Schrägheck	Frontantrieb	Benzin	80	109	Aug 1993	Jul 1996	2024-03-01	3998
Volvo	460	1.9 Turbo-diesel	Stufenheck	Frontantrieb	Diesel	66	90	Jul 1994	Jul 1996	2024-03-01	3999
Volvo	440	1.9 Turbo-diesel	Schrägheck	Frontantrieb	Diesel	66	90	Jul 1994	Dec 1996	2024-03-01	4000
VW	Caddy iii	1.9 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	77	105	Nov 2008	Aug 2010	2024-03-01	4001
Porsche	911	3.6 Carrera	Cabriolet	Heckantrieb	Benzin	200	272	Jul 1994	Aug 1995	2024-03-01	4002
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	200	272	Jul 1994	Aug 1995	2024-03-01	4003
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	200	272	Jul 1994	Aug 1995	2024-03-01	4004
Jaguar	Xjsc convertible	4	Cabriolet	Heckantrieb	Benzin	171	233	Jul 1994	Mar 1996	2024-03-01	4005
Jaguar	Xj	6 Sovereign 4.0	Stufenheck	Heckantrieb	Benzin	177	241	Sep 1994	Jul 1997	2024-03-01	4006
Jaguar	Xj	R Super Charged 4.0	Stufenheck	Heckantrieb	Benzin	235	320	Nov 1994	Jul 1997	2024-03-01	4007
Jaguar	Xj	6 3.2	Stufenheck	Heckantrieb	Benzin	155	211	Nov 1994	Jul 1997	2024-03-01	4008
Jaguar	Xj	12 6.0	Stufenheck	Heckantrieb	Benzin	229	311	Sep 1994	Sep 1997	2024-03-01	4009
Rover	600	620 I	Stufenheck	Frontantrieb	Benzin	85	115	Aug 1993	Jun 1996	2024-03-01	4010
Rover	600	620 SI	Stufenheck	Frontantrieb	Benzin	96	131	Aug 1993	Feb 1999	2024-03-01	4011
Rover	600	623 SI	Stufenheck	Frontantrieb	Benzin	116	158	Aug 1993	Jun 1999	2024-03-01	4012
Rover	800	825 SD	Coupe	Frontantrieb	Diesel	87	118	Sep 1993	Feb 1999	2024-03-01	4013
Rover	200 ii	214	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1993	Dec 1995	2024-03-01	4015
Rover	400	1.6 I	Kombi	Frontantrieb	Benzin	82	112	May 1994	Nov 1998	2024-03-01	4016
Rover	400	1.6 I	Kombi	Frontantrieb	Benzin	90	122	May 1994	Nov 1998	2024-03-01	4017
Rover	400	2.0 I	Kombi	Frontantrieb	Benzin	100	136	May 1994	Nov 1998	2024-03-01	4018
Rover	400	1.8 TD	Kombi	Frontantrieb	Diesel	65	88	Sep 1993	Nov 1998	2024-03-01	4019
Rover	100	111	Cabriolet	Frontantrieb	Benzin	44	60	Apr 1994	Oct 1997	2024-03-01	4020
Mitsubishi	Pajero ii	3.5 V6 24V	Geländewagen geschlossen	Allrad	Benzin	153	208	Jun 1994	Oct 1999	2024-03-01	4021
Mitsubishi	Pajero ii	2.8 TD	Geländewagen geschlossen	Allrad	Diesel	92	125	Jun 1994	Oct 1999	2024-03-01	4022
Mitsubishi	Galant vii	1.8	Stufenheck	Frontantrieb	Benzin	85	116	Feb 1994	Aug 1996	2024-03-01	4023
Mitsubishi	Galant vii	1.8	Schrägheck	Frontantrieb	Benzin	85	116	Feb 1994	Aug 1996	2024-03-01	4024
Mitsubishi	Colt iv	1.6	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1994	Apr 1996	2024-03-01	4025
Mitsubishi	Lancer v	1.6	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1994	Dec 1996	2024-03-01	4026
Mitsubishi	Pajero ii	3.0 V6 24V	Geländewagen geschlossen	Allrad	Benzin	133	181	Jun 1994	May 1997	2024-03-01	4027
Mitsubishi	Pajero ii canvas top	3.0 V6 24V	Geländewagen offen	Allrad	Benzin	133	181	Jun 1994	Apr 2000	2024-03-01	4028
Citroën	Xantia	1.9 Turbo D	Schrägheck	Frontantrieb	Diesel	66	90	May 1993	Apr 2003	2024-03-01	4029
Citroën	Zx	1.9 D	Kombi	Frontantrieb	Diesel	47	64	Oct 1993	Oct 1997	2024-03-01	4030
Citroën	Zx	1.8 I	Kombi	Frontantrieb	Benzin	74	101	Oct 1993	Oct 1997	2024-03-01	4031
Citroën	Zx	1.4 I	Kombi	Frontantrieb	Benzin	55	75	Oct 1993	Oct 1997	2024-03-01	4032
Citroën	Zx	1.9 TD	Kombi	Frontantrieb	Diesel	66	90	Oct 1993	Oct 1997	2024-03-01	4033
Citroën	Zx	1.6 I	Kombi	Frontantrieb	Benzin	65	88	Oct 1993	Oct 1997	2024-03-01	4034


--- Round 1 / 首次发送 ---
## 更新点

* 批量复用跨批次已有尺寸组，完成 VW Golf III、Vento、Polo、Volvo 440/460/850/940/960、Saab 9000、BMW E91、Citroën Xantia、Mitsubishi 等明确映射。
* 新建 Passat B4 Sedan 与 Variant 尺寸组。Volkswagen 官方档案给出的三维分别为 `4605×1720×1430 mm` 和 `4595×1720×1445 mm`。([Volkswagen Newsroom][1])
* 新建 Mercedes-Benz C 36 AMG W202 尺寸组。Mercedes-Benz 官方档案确认型号代码 `202.028`，三维为 `4487×1720×1385 mm`。([marsClassic][2])
* Ford Probe II 暂不建组：Auto-Data 的 ECP 数据为 `4544×1773×1310 mm`，而欧洲版目录为 `4585×1773×1310 mm`，需继续确认输入中的 `Ford USA` 对应市场和保险杠外廓。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 READY Ktype：44
* 已生成 READY 映射行：47
* 尚待闭合 Ktype：56
* 本轮引用尺寸组：32
* 本轮首次新建尺寸组：3
* 复用已有尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3932	3932	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	输入未区分3/5门，按既有6N统一尺寸组关联。	READY
3933	3933	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	输入未区分3/5门，按既有6N统一尺寸组关联。	READY
3934	3934	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH		READY
3935	3935	Wagon	Passat B4	3A	5	EU-VW-PASSAT-B4-WAGON-01	HIGH		READY
3936_3dr	3936	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Ktype未区分门数，按3门物理分支拆分。	READY
3936_5dr	3936	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Ktype未区分门数，按5门物理分支拆分。	READY
3937	3937	Sedan	Vento I	1H2	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
3938	3938	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
3939	3939	Convertible	Golf III Cabrio	1E7	2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
3940	3940	Wagon	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH	129 hp 2.2 D对应GH改款旅行车。	READY
3942	3942	Convertible	Golf III Cabrio	1E7	2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
3950	3950	Sedan	C-Class W202	202.028	4	EU-MERCEDES-BENZ-C-CLASS-W202-C36-AMG-SEDAN-01	HIGH		READY
3952	3952	Convertible	Mini II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	HIGH		READY
3963	3963	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3964	3964	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3965	3965	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3975	3975	Sedan	Saab 9000 CD	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH		READY
3976	3976	Hatchback	Saab 9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH		READY
3978	3978	Hatchback	Saab 9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH		READY
3980_prefl	3980	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	MEDIUM	生产区间跨改款，拆分改款前物理分支。	READY
3980_facelift	3980	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	MEDIUM	生产区间跨改款，拆分改款后物理分支。	READY
3981	3981	Sedan	Volvo 850	854	4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
3983	3983	Sedan	Volvo 960	964	4	EU-VOLVO-960-SEDAN-4D-01	HIGH		READY
3984	3984	Wagon	Volvo 960	965	5	EU-VOLVO-960-WAGON-5D-01	HIGH		READY
3985	3985	Sedan	Volvo 960	964	4	EU-VOLVO-960-SEDAN-4D-01	HIGH		READY
3986	3986	Wagon	Volvo 960	965	5	EU-VOLVO-960-WAGON-5D-01	HIGH		READY
3987	3987	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3988	3988	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3989	3989	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3990	3990	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3991	3991	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3992	3992	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3993	3993	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3994	3994	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3997	3997	Sedan	Volvo 460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
3998	3998	Hatchback	Volvo 440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH		READY
3999	3999	Sedan	Volvo 460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
4000	4000	Hatchback	Volvo 440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH		READY
4003	4003	Coupe	911 (993)	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4005	4005	Convertible	XJS facelift	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
4013	4013	Coupe	Rover 800 R17	R17	2	EU-ROVER-800-R17-COUPE-01	HIGH		READY
4023	4023	Sedan	Galant VII		4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH		READY
4024	4024	Hatchback	Galant VII		5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH		READY
4025	4025	Hatchback	Colt IV	CA0	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH		READY
4026	4026	Sedan	Lancer V		4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
4029_prefl	4029	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	MEDIUM	生产区间跨X1/X2，拆分改款前物理分支。	READY
4029_facelift	4029	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	MEDIUM	生产区间跨X1/X2，拆分改款后物理分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Volkswagen Newsroom Passat B4 official vehicle data	https://www.volkswagen-newsroom.com/de/fahrzeugdaten-passat-b4-steckbrief-19544
EU-VW-PASSAT-B4-WAGON-01	4595	1720	1445	Volkswagen Newsroom Passat B4 official vehicle data	https://www.volkswagen-newsroom.com/de/fahrzeugdaten-passat-b4-steckbrief-19544
EU-MERCEDES-BENZ-C-CLASS-W202-C36-AMG-SEDAN-01	4487	1720	1385	Mercedes-Benz Public Archive C 36 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-36-AMG.xhtml?oid=5528
```

## 下一步优先处理

1. 闭合 Mercedes-Benz W202 C 200、C140 S 420 Coupe，以及 C124/A124/S124 E 36 AMG 三种车身。
2. 处理 Seat Cordoba 与 Ibiza II 跨 `6K/6K1/6K2` 改款、门数分支。
3. 闭合 Saab 900 II Coupe、五门 Hatchback、Convertible 三组。
4. 解决 Ford Probe II 欧洲版与北美版长度冲突。
5. 批量处理 Pajero II SWB/LWB、硬顶/Canvas Top，以及剩余 Rover、Jaguar、Citroën ZX Wagon 等新组。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/de/fahrzeugdaten-passat-b4-steckbrief-19544 "Fahrzeugdaten Passat B4 Steckbrief | Volkswagen Newsroom"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-36-AMG.xhtml?oid=5528 "C 36 AMG"
[3]: https://www.auto-data.net/en/ford-probe-ii-ecp-2.0-16v-118hp-automatic-56310?utm_source=chatgpt.com "Ford Probe II (ECP) 2.0 16V (118 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增/修改 60 条映射，闭合 44 个 Ktype。
* 完成 Mercedes-Benz W202、C140、C124/A124/S124 AMG、W221 与 S204 改款分支。Mercedes-Benz 官方档案明确支持相应车身代码和尺寸边界。([marsClassic][1])
* 完成 Seat Cordoba/Ibiza、Saab 900 II、Volvo 850 Wagon、Lada Nova、VW Caddy III、Porsche 993 Cabriolet、Rover 600/400/100 和 Citroën ZX Break 分组。Caddy 的宽度页面同时列出不含镜宽度与含镜宽度，落盘采用不含镜值；ZX Break 按 Phase I/II 拆分。([汽车数据网][2])
* Ibiza II 的 7 个尺寸组直接复用跨批次缓存，本轮未重复输出尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* PENDING Ktype：12
* READY 映射行：107
* 已确认并被当前映射引用的尺寸组：62
* 本轮首次创建尺寸组：23
* 剩余 PENDING：3943、3944、3951、4006、4007、4008、4009、4015、4021、4022、4027、4028
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3945_presep95	3945	Sedan	C-Class W202	202.020	4	EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-PRESEP95-01	MEDIUM	生产区间跨1995年9月标准车身高度调整，拆分调整前分支。	READY
3945_postsep95	3945	Sedan	C-Class W202	202.020	4	EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-POSTSEP95-01	MEDIUM	生产区间跨1995年9月标准车身高度调整，拆分调整后分支。	READY
3946	3946	Coupe	S-Class C140	140.063	2	EU-MERCEDES-BENZ-S-CLASS-C140-S420-COUPE-01	HIGH		READY
3947	3947	Coupe	E-Class C124	124.052	2	EU-MERCEDES-BENZ-E-CLASS-C124-E36-AMG-COUPE-01	HIGH		READY
3948	3948	Convertible	E-Class A124	124.066	2	EU-MERCEDES-BENZ-E-CLASS-A124-E36-AMG-CONVERTIBLE-01	HIGH		READY
3949	3949	Wagon	E-Class S124	124.092	5	EU-MERCEDES-BENZ-E-CLASS-S124-E36-AMG-WAGON-01	HIGH		READY
3953_prefl	3953	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3953_facelift	3953	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3954_prefl	3954	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3954_facelift	3954	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3955_prefl	3955	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3955_facelift	3955	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3956	3956	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3957	3957	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3958	3958	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3959	3959	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM		READY
3961_3dr_6k	3961	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K三门分支。	READY
3961_3dr_6k1	3961	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K1三门分支。	READY
3961_3dr_6k2	3961	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K2三门分支。	READY
3961_5dr_6k	3961	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K五门分支。	READY
3961_5dr_6k1	3961	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K1五门分支。	READY
3961_5dr_6k2	3961	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K2五门分支。	READY
3962_3dr_6k	3962	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	生产区间覆盖6K与6K1 GT三门外廓，拆分6K分支。	READY
3962_3dr_6k1_gt	3962	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	MEDIUM	生产区间覆盖6K与6K1 GT三门外廓，拆分6K1 GT分支。	READY
3966	3966	Hatchback	Saab 900 II		3	EU-SAAB-900-II-HATCHBACK-3D-01	MEDIUM	输入 Coupe 对应三门 Combi Coupé 外廓。	READY
3967	3967	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3968	3968	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3969	3969	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3970	3970	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3971	3971	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3972	3972	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3973	3973	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3974	3974	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3977	3977	Sedan	S-Class W221	221.095	4	EU-MERCEDES-BENZ-S-CLASS-W221-S400-HYBRID-SEDAN-01	HIGH		READY
3979_prefl	3979	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-PREFL-01	MEDIUM	生产区间跨2011年改款，拆分改款前分支。	READY
3979_facelift	3979	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-FACELIFT-01	MEDIUM	生产区间跨2011年改款，拆分改款后分支。	READY
3982	3982	Wagon	Volvo 850	855	5	EU-VOLVO-850-WAGON-5D-01	MEDIUM		READY
3995	3995	Wagon	Nova (VAZ-2104)	2104	5	EU-LADA-NOVA-2104-WAGON-5D-01	HIGH		READY
3996	3996	Wagon	Nova (VAZ-2104)	2104	5	EU-LADA-NOVA-2104-WAGON-5D-01	HIGH		READY
4001	4001	Van	Caddy III	2K		EU-VW-CADDY-III-2K-VAN-01	MEDIUM	输入同时覆盖 Kasten/Großraumlimousine，按相同外廓归一为 Van。	READY
4002	4002	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4004	4004	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4010	4010	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4011	4011	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4012	4012	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4016	4016	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4017	4017	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4018	4018	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4019	4019	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4020	4020	Convertible	Rover 100	XP	2	EU-ROVER-100-XP-CONVERTIBLE-2D-01	HIGH		READY
4030_phase1	4030	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4030_phase2	4030	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4031_phase1	4031	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4031_phase2	4031	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4032_phase1	4032	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4032_phase2	4032	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4033_phase1	4033	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4033_phase2	4033	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4034_phase1	4034	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4034_phase2	4034	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-PRESEP95-01	4487	1720	1418	Mercedes-Benz Public Archive C 200	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523
EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-POSTSEP95-01	4487	1720	1427	Mercedes-Benz Public Archive C 200	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523
EU-MERCEDES-BENZ-S-CLASS-C140-S420-COUPE-01	5065	1912	1452	Mercedes-Benz Public Archive S 420 Coupe	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-420-Coupe.xhtml?oid=4514
EU-MERCEDES-BENZ-E-CLASS-C124-E36-AMG-COUPE-01	4655	1740	1385	Mercedes-Benz Public Archive E 36 AMG Coupe	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-36-AMG-Coupe.xhtml?oid=4580
EU-MERCEDES-BENZ-E-CLASS-A124-E36-AMG-CONVERTIBLE-01	4655	1740	1383	Mercedes-Benz Archive E 36 AMG Cabriolet	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/E-36-AMG-Cabriolet.xhtml?oid=4646
EU-MERCEDES-BENZ-E-CLASS-S124-E36-AMG-WAGON-01	4765	1740	1468	Mercedes-Benz Public Archive E 36 AMG station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-36-AMG-station-wagon.xhtml?oid=5458
EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	4142	1640	1424	encyCARpedia 1997 SEAT Cordoba 1.6 SE	https://www.encycarpedia.com/seat/97-cordoba-1-6-se-saloon
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424	Auto-Data SEAT Cordoba I facelift	https://www.auto-data.net/en/seat-cordoba-i-facelift-1999-generation-2897
EU-SAAB-900-II-HATCHBACK-3D-01	4637	1711	1436	Auto-Data Saab 900 II Combi Coupe	https://www.auto-data.net/en/saab-900-ii-combi-coupe-generation-2546
EU-SAAB-900-II-HATCHBACK-5D-01	4637	1711	1436	Automobile-Catalog 1994 Saab 900 S/SE	https://www.automobile-catalog.com/car/1994/3031055/saab_900_s_se.html
EU-SAAB-900-II-CONVERTIBLE-2D-01	4637	1711	1435	Auto-Data Saab 900 model specifications	https://www.auto-data.net/en/saab-900-model-1277
EU-MERCEDES-BENZ-S-CLASS-W221-S400-HYBRID-SEDAN-01	5096	1871	1479	Mercedes-Benz Public Archive S 400 HYBRID	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-400-HYBRID-2009---2013.xhtml?oid=191730318
EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-PREFL-01	4596	1770	1459	Automobile-Catalog Mercedes-Benz C 250 CGI T-Modell	https://www.automobile-catalog.com/car/2009/1550690/mercedes-benz_c_250_cgi_blueefficiency_t-modell_automatic.html
EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-FACELIFT-01	4606	1770	1459	Auto Motor und Sport Mercedes C 250 CGI T technical data	https://www.auto-motor-und-sport.de/test/mercedes-c-250-cgi-t-im-test-renovierter-mittelklasse-kombi/technische-daten/
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Volvo Club UK 850 Estate history;Engine in detail Volvo 850 Estate 2.5 20V	https://www.volvoclub.org.uk/history/850est.shtml;https://www.engineindetail.com/pa/volvo-850-estate-wagon-2-5-20v-1994
EU-LADA-NOVA-2104-WAGON-5D-01	4115	1620	1443	Auto-Data Lada 2104 model specifications	https://www.auto-data.net/en/lada-2104-model-1422
EU-VW-CADDY-III-2K-VAN-01	4405	1794	1833	Auto-Data Volkswagen Caddy III 1.9 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-105hp-dpf-4motion-50631
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300	Auto-Data Porsche 911 Cabriolet 993 Carrera 4 3.6	https://www.auto-data.net/en/porsche-911-cabriolet-993-carrera-4-3.6-272hp-6617
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380	Automobile-Catalog Rover 620 i	https://www.automobile-catalog.com/car/1995/3013490/rover_620_i.html
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390	Auto-Data Rover 400 model specifications	https://www.auto-data.net/en/rover-400-model-1228
EU-ROVER-100-XP-CONVERTIBLE-2D-01	3521	1550	1395	Auto-Data Rover 100 model specifications	https://www.auto-data.net/en/rover-100-model-1217
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	4260	1702	1451	Auto-Data Citroen ZX Break N2 Phase I 1.9 D	https://www.auto-data.net/en/citroen-zx-break-n2-phase-i-1.9-d-71hp-15230
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	4260	1705	1457	Auto-Data Citroen ZX Break N2 Phase II 1.9 D	https://www.auto-data.net/en/citroen-zx-break-n2-phase-ii-1.9-d-71hp-15231
```

## 下一步优先处理

1. 合并处理 Jaguar X300/X305/X306 的普通、增压与 V12 外廓：4006、4007、4008、4009。
2. 合并处理 Mitsubishi Pajero II 硬顶 SWB/LWB 与 Canvas Top：3951、4021、4022、4027、4028。
3. 闭合 Ford Probe II 欧洲/北美保险杠长度边界：3943、3944。
4. 闭合 Rover 200 II Ktype 4015 的三门/五门物理分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523 "https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523"
[2]: https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-105hp-dpf-4motion-50631 "https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-105hp-dpf-4motion-50631"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 12 个 Ktype 已全部闭合。
* 完成 Ford Probe II、Mercedes-Benz G 320、Jaguar X300/X305/X306、Rover 200 II，以及 Mitsubishi Pajero II 短轴、长轴和 Canvas Top 分支。
* 已完成固定表头、唯一性、映射引用闭合、尺寸与来源非空、文件名检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：124
* PENDING 映射：0
* DIMENSION_GROUP：73
* 重复 `id`：0
* 重复 `DIMENSION_GROUP_ID`：0
* 缺失映射引用：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3932	3932	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	输入未区分3/5门，按既有6N统一尺寸组关联。	READY
3933	3933	Hatchback	Polo III	6N		EU-VW-POLO-III-6N-HATCHBACK-01	MEDIUM	输入未区分3/5门，按既有6N统一尺寸组关联。	READY
3934	3934	Sedan	Passat B4	3A	4	EU-VW-PASSAT-B4-SEDAN-01	HIGH		READY
3935	3935	Wagon	Passat B4	3A	5	EU-VW-PASSAT-B4-WAGON-01	HIGH		READY
3936_3dr	3936	Hatchback	Golf III	1H1	3	EU-VW-GOLF-III-HATCHBACK-3D-01	MEDIUM	Ktype未区分门数，按3门物理分支拆分。	READY
3936_5dr	3936	Hatchback	Golf III	1H1	5	EU-VW-GOLF-III-HATCHBACK-5D-01	MEDIUM	Ktype未区分门数，按5门物理分支拆分。	READY
3937	3937	Sedan	Vento I	1H2	4	EU-VW-VENTO-I-SEDAN-01	HIGH		READY
3938	3938	Wagon	Golf III Variant	1H5	5	EU-VW-GOLF-III-VARIANT-WAGON-01	HIGH		READY
3939	3939	Convertible	Golf III Cabrio	1E7	2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
3940	3940	Wagon	Mazda 6 II	GH	5	EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	HIGH	129 hp 2.2 D对应GH改款旅行车。	READY
3942	3942	Convertible	Golf III Cabrio	1E7	2	EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	HIGH		READY
3943	3943	Coupe	Probe II	ECP	2	EU-FORD-PROBE-II-ECP-COUPE-2D-2-0-01	HIGH		READY
3944	3944	Coupe	Probe II	ECP	2	EU-FORD-PROBE-II-ECP-GT-COUPE-2D-2-5-01	HIGH		READY
3945_presep95	3945	Sedan	C-Class W202	202.020	4	EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-PRESEP95-01	MEDIUM	生产区间跨1995年9月标准车身高度调整，拆分调整前分支。	READY
3945_postsep95	3945	Sedan	C-Class W202	202.020	4	EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-POSTSEP95-01	MEDIUM	生产区间跨1995年9月标准车身高度调整，拆分调整后分支。	READY
3946	3946	Coupe	S-Class C140	140.063	2	EU-MERCEDES-BENZ-S-CLASS-C140-S420-COUPE-01	HIGH		READY
3947	3947	Coupe	E-Class C124	124.052	2	EU-MERCEDES-BENZ-E-CLASS-C124-E36-AMG-COUPE-01	HIGH		READY
3948	3948	Convertible	E-Class A124	124.066	2	EU-MERCEDES-BENZ-E-CLASS-A124-E36-AMG-CONVERTIBLE-01	HIGH		READY
3949	3949	Wagon	E-Class S124	124.092	5	EU-MERCEDES-BENZ-E-CLASS-S124-E36-AMG-WAGON-01	HIGH		READY
3950	3950	Sedan	C-Class W202	202.028	4	EU-MERCEDES-BENZ-C-CLASS-W202-C36-AMG-SEDAN-01	HIGH		READY
3951_swb	3951	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-3D-SWB-01	MEDIUM	Ktype未区分短轴三门与长轴五门闭合车身，拆分短轴分支。	READY
3951_lwb	3951	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-5D-LWB-01	MEDIUM	Ktype未区分短轴三门与长轴五门闭合车身，拆分长轴分支。	READY
3952	3952	Convertible	Mini II	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	HIGH		READY
3953_prefl	3953	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3953_facelift	3953	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3954_prefl	3954	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3954_facelift	3954	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3955_prefl	3955	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款前分支。	READY
3955_facelift	3955	Sedan	Cordoba I	6K2	4	EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	MEDIUM	生产区间跨1999年改款，拆分改款后分支。	READY
3956	3956	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3957	3957	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3958	3958	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	HIGH		READY
3959	3959	Sedan	Cordoba I	6K	4	EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	MEDIUM		READY
3961_3dr_6k	3961	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K三门分支。	READY
3961_3dr_6k1	3961	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K1三门分支。	READY
3961_3dr_6k2	3961	Hatchback	Ibiza II	6K2	3	EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K2三门分支。	READY
3961_5dr_6k	3961	Hatchback	Ibiza II	6K	5	EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K五门分支。	READY
3961_5dr_6k1	3961	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K1五门分支。	READY
3961_5dr_6k2	3961	Hatchback	Ibiza II	6K2	5	EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	MEDIUM	Ktype跨车身修订且未区分门数，拆分6K2五门分支。	READY
3962_3dr_6k	3962	Hatchback	Ibiza II	6K	3	EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	MEDIUM	生产区间覆盖6K与6K1 GT三门外廓，拆分6K分支。	READY
3962_3dr_6k1_gt	3962	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	MEDIUM	生产区间覆盖6K与6K1 GT三门外廓，拆分6K1 GT分支。	READY
3963	3963	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3964	3964	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3965	3965	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
3966	3966	Hatchback	Saab 900 II		3	EU-SAAB-900-II-HATCHBACK-3D-01	MEDIUM	输入 Coupe 对应三门 Combi Coupé 外廓。	READY
3967	3967	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3968	3968	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3969	3969	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3970	3970	Hatchback	Saab 900 II		5	EU-SAAB-900-II-HATCHBACK-5D-01	HIGH		READY
3971	3971	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3972	3972	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3973	3973	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3974	3974	Convertible	Saab 900 II		2	EU-SAAB-900-II-CONVERTIBLE-2D-01	HIGH		READY
3975	3975	Sedan	Saab 9000 CD	CD	4	EU-SAAB-9000-CD-SEDAN-01	HIGH		READY
3976	3976	Hatchback	Saab 9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH		READY
3977	3977	Sedan	S-Class W221	221.095	4	EU-MERCEDES-BENZ-S-CLASS-W221-S400-HYBRID-SEDAN-01	HIGH		READY
3978	3978	Hatchback	Saab 9000 CS	CS	5	EU-SAAB-9000-CS-HATCHBACK-5D-01	HIGH		READY
3979_prefl	3979	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-PREFL-01	MEDIUM	生产区间跨2011年改款，拆分改款前分支。	READY
3979_facelift	3979	Wagon	C-Class S204	S204	5	EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-FACELIFT-01	MEDIUM	生产区间跨2011年改款，拆分改款后分支。	READY
3980_prefl	3980	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	MEDIUM	生产区间跨改款，拆分改款前物理分支。	READY
3980_facelift	3980	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	MEDIUM	生产区间跨改款，拆分改款后物理分支。	READY
3981	3981	Sedan	Volvo 850	854	4	EU-VOLVO-850-SEDAN-4D-01	HIGH		READY
3982	3982	Wagon	Volvo 850	855	5	EU-VOLVO-850-WAGON-5D-01	MEDIUM		READY
3983	3983	Sedan	Volvo 960	964	4	EU-VOLVO-960-SEDAN-4D-01	HIGH		READY
3984	3984	Wagon	Volvo 960	965	5	EU-VOLVO-960-WAGON-5D-01	HIGH		READY
3985	3985	Sedan	Volvo 960	964	4	EU-VOLVO-960-SEDAN-4D-01	HIGH		READY
3986	3986	Wagon	Volvo 960	965	5	EU-VOLVO-960-WAGON-5D-01	HIGH		READY
3987	3987	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3988	3988	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3989	3989	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3990	3990	Sedan	Volvo 940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
3991	3991	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3992	3992	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3993	3993	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3994	3994	Wagon	Volvo 940	945	5	EU-VOLVO-940-WAGON-5D-01	HIGH		READY
3995	3995	Wagon	Nova (VAZ-2104)	2104	5	EU-LADA-NOVA-2104-WAGON-5D-01	HIGH		READY
3996	3996	Wagon	Nova (VAZ-2104)	2104	5	EU-LADA-NOVA-2104-WAGON-5D-01	HIGH		READY
3997	3997	Sedan	Volvo 460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
3998	3998	Hatchback	Volvo 440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH		READY
3999	3999	Sedan	Volvo 460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
4000	4000	Hatchback	Volvo 440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH		READY
4001	4001	Van	Caddy III	2K		EU-VW-CADDY-III-2K-VAN-01	MEDIUM	输入同时覆盖 Kasten/Großraumlimousine，按相同外廓归一为 Van。	READY
4002	4002	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4003	4003	Coupe	911 (993)	993	2	EU-PORSCHE-911-993-COUPE-CARRERA-01	HIGH		READY
4004	4004	Convertible	911 (993)	993	2	EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	HIGH		READY
4005	4005	Convertible	XJS facelift	XJ27	2	EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	HIGH		READY
4006	4006	Sedan	XJ X300	X300	4	EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	HIGH		READY
4007	4007	Sedan	XJ X300	X306	4	EU-JAGUAR-XJ-X306-XJR-SEDAN-SWB-01	HIGH		READY
4008	4008	Sedan	XJ X300	X300	4	EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	HIGH		READY
4009	4009	Sedan	XJ X300	X305	4	EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	HIGH		READY
4010	4010	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4011	4011	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4012	4012	Sedan	Rover 600	RH	4	EU-ROVER-600-RH-SEDAN-4D-01	HIGH		READY
4013	4013	Coupe	Rover 800 R17	R17	2	EU-ROVER-800-R17-COUPE-01	HIGH		READY
4015_3dr	4015	Hatchback	Rover 200 II	XW	3	EU-ROVER-200-II-XW-HATCHBACK-3D-01	MEDIUM	Ktype未区分三门与五门掀背车身，拆分三门分支。	READY
4015_5dr	4015	Hatchback	Rover 200 II	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	MEDIUM	Ktype未区分三门与五门掀背车身，拆分五门分支。	READY
4016	4016	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4017	4017	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4018	4018	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4019	4019	Wagon	Rover 400 Tourer	XW	5	EU-ROVER-400-XW-TOURER-WAGON-5D-01	HIGH		READY
4020	4020	Convertible	Rover 100	XP	2	EU-ROVER-100-XP-CONVERTIBLE-2D-01	HIGH		READY
4021_3dr	4021	SUV	Pajero II	V2_W	3	EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分三门分支。	READY
4021_5dr	4021	SUV	Pajero II	V4_W	5	EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分五门分支。	READY
4022_3dr	4022	SUV	Pajero II	V2_W	3	EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分三门分支。	READY
4022_5dr	4022	SUV	Pajero II	V4_W	5	EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分五门分支。	READY
4023	4023	Sedan	Galant VII		4	EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	HIGH		READY
4024	4024	Hatchback	Galant VII		5	EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	HIGH		READY
4025	4025	Hatchback	Colt IV	CA0	3	EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	HIGH		READY
4026	4026	Sedan	Lancer V		4	EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	HIGH		READY
4027_3dr	4027	SUV	Pajero II	V2_W	3	EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分三门分支。	READY
4027_5dr	4027	SUV	Pajero II	V4_W	5	EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	MEDIUM	Ktype未区分三门短轴与五门长轴闭合车身，拆分五门分支。	READY
4028	4028	SUV	Pajero II Canvas Top	V23C	3	EU-MITSUBISHI-PAJERO-II-V23C-CANVAS-TOP-SUV-3D-01	HIGH		READY
4029_prefl	4029	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	MEDIUM	生产区间跨X1/X2，拆分改款前物理分支。	READY
4029_facelift	4029	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	MEDIUM	生产区间跨X1/X2，拆分改款后物理分支。	READY
4030_phase1	4030	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4030_phase2	4030	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4031_phase1	4031	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4031_phase2	4031	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4032_phase1	4032	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4032_phase2	4032	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4033_phase1	4033	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4033_phase2	4033	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
4034_phase1	4034	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase I 分支。	READY
4034_phase2	4034	Wagon	ZX N2	N2	5	EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	MEDIUM	生产区间跨 Phase I/II 外廓，拆分 Phase II 分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3801-3900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420	Auto-Data Volkswagen Polo III 6N	https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.3-55hp-8472
EU-VW-PASSAT-B4-SEDAN-01	4605	1720	1430	Volkswagen Newsroom Passat B4 official vehicle data	https://www.volkswagen-newsroom.com/de/fahrzeugdaten-passat-b4-steckbrief-19544
EU-VW-PASSAT-B4-WAGON-01	4595	1720	1445	Volkswagen Newsroom Passat B4 official vehicle data	https://www.volkswagen-newsroom.com/de/fahrzeugdaten-passat-b4-steckbrief-19544
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425	Auto-Data Volkswagen Golf III 1.8 (90 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-1.8-90hp-8719
EU-VW-VENTO-I-SEDAN-01	4380	1695	1415	Auto-Data Volkswagen Vento (1HX0) 1.6 (101 Hp)	https://www.auto-data.net/en/volkswagen-vento-1hx0-1.6-101hp-automatic-8842
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430	Auto-Data Volkswagen Golf III Variant	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400	Auto-Data Volkswagen Golf III Cabrio 1.8 i (75 Hp)	https://www.auto-data.net/en/volkswagen-golf-iii-cabrio-1.8-i-75hp-8751
EU-MAZDA-6-II-GH-FACELIFT-WAGON-5D-01	4785	1795	1490	Auto-Data Mazda 6 II Combi GH facelift 2.2 CD (129 Hp)	https://www.auto-data.net/en/mazda-6-ii-combi-gh-facelift-2010-2.2-cd-129hp-16791
EU-FORD-PROBE-II-ECP-COUPE-2D-2-0-01	4585	1773	1310	Auto-Data Ford Probe II ECP 2.0 16V	https://www.auto-data.net/en/ford-probe-ii-ecp-2.0-16v-115hp-7994
EU-FORD-PROBE-II-ECP-GT-COUPE-2D-2-5-01	4585	1773	1315	Auto-Data Ford Probe II ECP GT 2.5 V6 24V	https://www.auto-data.net/en/ford-probe-ii-ecp-gt-2.5-v6-24v-165hp-7995
EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-PRESEP95-01	4487	1720	1418	Mercedes-Benz Public Archive C 200	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523
EU-MERCEDES-BENZ-C-CLASS-W202-C200-SEDAN-POSTSEP95-01	4487	1720	1427	Mercedes-Benz Public Archive C 200	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-200.xhtml?oid=5523
EU-MERCEDES-BENZ-S-CLASS-C140-S420-COUPE-01	5065	1912	1452	Mercedes-Benz Public Archive S 420 Coupe	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-420-Coupe.xhtml?oid=4514
EU-MERCEDES-BENZ-E-CLASS-C124-E36-AMG-COUPE-01	4655	1740	1385	Mercedes-Benz Public Archive E 36 AMG Coupe	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-36-AMG-Coupe.xhtml?oid=4580
EU-MERCEDES-BENZ-E-CLASS-A124-E36-AMG-CONVERTIBLE-01	4655	1740	1383	Mercedes-Benz Archive E 36 AMG Cabriolet	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/E-36-AMG-Cabriolet.xhtml?oid=4646
EU-MERCEDES-BENZ-E-CLASS-S124-E36-AMG-WAGON-01	4765	1740	1468	Mercedes-Benz Public Archive E 36 AMG station wagon	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-36-AMG-station-wagon.xhtml?oid=5458
EU-MERCEDES-BENZ-C-CLASS-W202-C36-AMG-SEDAN-01	4487	1720	1385	Mercedes-Benz Public Archive C 36 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/C-36-AMG.xhtml?oid=5528
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-3D-SWB-01	4230	1760	1931	Auto-Data Mercedes-Benz G-class W463 G 320 SWB	https://www.auto-data.net/en/mercedes-benz-g-class-w463-g-320-210hp-4matic-automatic-42312
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-5D-LWB-01	4680	1760	1936	Auto-Data Mercedes-Benz G-class Long W463 G 320	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-g-320-210hp-4matic-automatic-42518
EU-MINI-MINI-R57-CONVERTIBLE-FACELIFT-01	3729	1683	1414	Auto-Data Mini Convertible R57 facelift 2011	https://www.auto-data.net/en/mini-convertible-r57-facelift-2011-generation-4509
EU-SEAT-CORDOBA-I-6K-SEDAN-4D-01	4142	1640	1424	encyCARpedia 1997 SEAT Cordoba 1.6 SE	https://www.encycarpedia.com/seat/97-cordoba-1-6-se-saloon
EU-SEAT-CORDOBA-I-6K2-SEDAN-4D-01	4163	1640	1424	Auto-Data SEAT Cordoba I facelift	https://www.auto-data.net/en/seat-cordoba-i-facelift-1999-generation-2897
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390	Automobile-Catalog 1993 Seat Ibiza 1.3i	https://www.automobile-catalog.com/car/1993/3065600/seat_ibiza_1_3i.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Automobile-Catalog 1999 Seat Ibiza 1.4 phase I	https://www.automobile-catalog.com/car/1999/3070025/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422	Automobile-Catalog 1999 Seat Ibiza 1.4 phase II	https://www.automobile-catalog.com/car/1999/3070445/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390	Automobile-Catalog 1993 Seat Ibiza 1.3i	https://www.automobile-catalog.com/car/1993/3065600/seat_ibiza_1_3i.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Automobile-Catalog 1999 Seat Ibiza 1.4 phase I	https://www.automobile-catalog.com/car/1999/3070025/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422	Automobile-Catalog 1999 Seat Ibiza 1.4 phase II	https://www.automobile-catalog.com/car/1999/3070445/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409	Automobile-Catalog 1997 Seat Ibiza GTi 1.6	https://www.automobile-catalog.com/car/1997/3070070/seat_ibiza_gti_1_6.html
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424	Auto-Data Seat Toledo I 1L 1.6	https://www.auto-data.net/en/seat-toledo-i-1l-1.6-72hp-13548
EU-SAAB-900-II-HATCHBACK-3D-01	4637	1711	1436	Auto-Data Saab 900 II Combi Coupe	https://www.auto-data.net/en/saab-900-ii-combi-coupe-generation-2546
EU-SAAB-900-II-HATCHBACK-5D-01	4637	1711	1436	Automobile-Catalog 1994 Saab 900 S/SE	https://www.automobile-catalog.com/car/1994/3031055/saab_900_s_se.html
EU-SAAB-900-II-CONVERTIBLE-2D-01	4637	1711	1435	Auto-Data Saab 900 model specifications	https://www.auto-data.net/en/saab-900-model-1277
EU-SAAB-9000-CD-SEDAN-01	4794	1764	1420	Auto-Data Saab 9000 sedan	https://www.auto-data.net/en/saab-9000-generation-2534
EU-SAAB-9000-CS-HATCHBACK-5D-01	4761	1778	1420	Auto-Data Saab 9000 Hatchback 2.3 16V CSE Eco Power	https://www.auto-data.net/en/saab-9000-hatchback-2.3-16v-cse-eco-power-170hp-11894
EU-MERCEDES-BENZ-S-CLASS-W221-S400-HYBRID-SEDAN-01	5096	1871	1479	Mercedes-Benz Public Archive S 400 HYBRID	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-400-HYBRID-2009---2013.xhtml?oid=191730318
EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-PREFL-01	4596	1770	1459	Automobile-Catalog Mercedes-Benz C 250 CGI T-Modell	https://www.automobile-catalog.com/car/2009/1550690/mercedes-benz_c_250_cgi_blueefficiency_t-modell_automatic.html
EU-MERCEDES-BENZ-C-CLASS-S204-C250-CGI-WAGON-FACELIFT-01	4606	1770	1459	Auto Motor und Sport Mercedes C 250 CGI T technical data	https://www.auto-motor-und-sport.de/test/mercedes-c-250-cgi-t-im-test-renovierter-mittelklasse-kombi/technische-daten/
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data BMW 3 Series Touring E91 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-325i-218hp-9945
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI 325i	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-325i-218hp-17216
EU-VOLVO-850-SEDAN-4D-01	4660	1761	1415	Auto-Data Volvo 850 LS	https://www.auto-data.net/en/volvo-850-ls-generation-1928
EU-VOLVO-850-WAGON-5D-01	4709	1761	1415	Volvo Club UK 850 Estate history;Engine in detail Volvo 850 Estate 2.5 20V	https://www.volvoclub.org.uk/history/850est.shtml;https://www.engineindetail.com/pa/volvo-850-estate-wagon-2-5-20v-1994
EU-VOLVO-960-SEDAN-4D-01	4871	1750	1411	Auto-Data Volvo 960 964	https://www.auto-data.net/en/volvo-960-964-generation-1945
EU-VOLVO-960-WAGON-5D-01	4850	1750	1434	Auto-Data Volvo 960 Kombi 965	https://www.auto-data.net/en/volvo-960-kombi-965-generation-1946
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425	Auto-Data Volvo 940 944	https://www.auto-data.net/en/volvo-940-944-generation-1937
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435	Auto-Data Volvo 940 Combi 945	https://www.auto-data.net/en/volvo-940-combi-945-generation-1938
EU-LADA-NOVA-2104-WAGON-5D-01	4115	1620	1443	Auto-Data Lada 2104 model specifications	https://www.auto-data.net/en/lada-2104-model-1422
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378	Auto-Data Volvo 460 L 464	https://www.auto-data.net/en/volvo-460-l-464-generation-1926
EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	4345	1686	1378	Auto-Data Volvo 440 K 445	https://www.auto-data.net/en/volvo-440-k-model-939
EU-VW-CADDY-III-2K-VAN-01	4405	1794	1833	Auto-Data Volkswagen Caddy III 1.9 TDI 4MOTION	https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-105hp-dpf-4motion-50631
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300	Auto-Data Porsche 911 Cabriolet 993 Carrera 4 3.6	https://www.auto-data.net/en/porsche-911-cabriolet-993-carrera-4-3.6-272hp-6617
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315	Auto-Data Porsche 911 993 Carrera 3.6	https://www.auto-data.net/en/porsche-911-993-carrera-3.6-272hp-6607
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276	Automobile-Catalog 1994 Jaguar XJS 4.0 Convertible automatic catalyst	https://www.automobile-catalog.com/car/1994/1284890/jaguar_xjs_4_0_convertible_automatic_cat.html
EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	5023	1798	1314	Auto-Data Jaguar XJ X300 4.0 Classic Sovereign;Auto-Data Jaguar XJ X300 3.2 Classic;Auto-Data Jaguar XJ X300 6.0 V12 Classic	https://www.auto-data.net/en/jaguar-xj-x300-4.0-24v-classic-sovereign-241hp-automatic-187;https://www.auto-data.net/en/jaguar-xj-x300-3.2-24v-classic-211hp-automatic-24555;https://www.auto-data.net/en/jaguar-xj-x300-6.0-v12-classic-311hp-automatic-191
EU-JAGUAR-XJ-X306-XJR-SEDAN-SWB-01	5023	1798	1303	Auto-Data Jaguar XJ X300 R 4.0 Sport	https://www.auto-data.net/en/jaguar-xj-x300-r-4.0-24v-sport-320hp-automatic-190
EU-ROVER-600-RH-SEDAN-4D-01	4645	1715	1380	Automobile-Catalog Rover 620 i	https://www.automobile-catalog.com/car/1995/3013490/rover_620_i.html
EU-ROVER-800-R17-COUPE-01	4882	1730	1393	Auto-Data Rover 800 Coupe	https://www.auto-data.net/en/rover-800-coupe-generation-2445
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390	Auto-Data Rover 200 XW 214 i	https://www.auto-data.net/en/rover-200-xw-214-i-75hp-11569
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390	Auto-Data Rover 200 XW	https://www.auto-data.net/en/rover-200-xw-generation-2451
EU-ROVER-400-XW-TOURER-WAGON-5D-01	4365	1680	1390	Auto-Data Rover 400 model specifications	https://www.auto-data.net/en/rover-400-model-1228
EU-ROVER-100-XP-CONVERTIBLE-2D-01	3521	1550	1395	Auto-Data Rover 100 model specifications	https://www.auto-data.net/en/rover-100-model-1217
EU-MITSUBISHI-PAJERO-II-V20-METAL-TOP-SUV-3D-01	4145	1785	1845	Auto-Data Mitsubishi Pajero II Metal Top 3.5 V6 24V;Auto-Data Mitsubishi Pajero II Metal Top 2.8 TD GLS	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-3.5-i-v6-24v-208hp-15523;https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-2.8-td-gls-125hp-15520
EU-MITSUBISHI-PAJERO-II-V40-SUV-5D-LWB-01	4725	1785	1900	Auto-Data Mitsubishi Pajero II 3.5 V6 24V;Auto-Data Mitsubishi Pajero II 2.8 TD GLX;Auto-Data Mitsubishi Pajero II 3.0 V6 24V	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.5-i-v6-24v-208hp-15510;https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-2.8-td-glx-125hp-15506;https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-181hp-15507
EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII 1.8	https://www.auto-data.net/en/mitsubishi-galant-vii-2.0-glstd-e57a-90hp-15376
EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	4620	1730	1395	Auto-Data Mitsubishi Galant VII Hatchback 1.8	https://www.auto-data.net/en/mitsubishi-galant-vii-hatchback-1.8-e52a-116hp-15379
EU-MITSUBISHI-COLT-IV-CAO-HATCHBACK-3D-01	3955	1690	1365	Auto-Data Mitsubishi Colt IV CAO 1.6 GLXi	https://www.auto-data.net/en/mitsubishi-colt-iv-cao-1.6-glxi-16v-ca4a-113hp-15764
EU-MITSUBISHI-LANCER-V-SEDAN-4D-01	4275	1690	1385	Auto-Data Mitsubishi Lancer V 1.6 16V CB4A	https://www.auto-data.net/en/mitsubishi-lancer-v-1.6-16v-cb4a-113hp-15667
EU-MITSUBISHI-PAJERO-II-V23C-CANVAS-TOP-SUV-3D-01	4140	1780	1820	UltimateSpecs Mitsubishi Pajero II V20 3.0 V6 Soft Top	https://www.ultimatespecs.com/car-specs/Mitsubishi/7001/Mitsubishi-Pajero-II-%28V20%29-30-V6-Soft-Top-Auto.html
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387	Auto-Data Citroen Xantia X1 1.9 D	https://www.auto-data.net/en/citroen-xantia-x1-1.9-d-69hp-14961
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400	Auto-Data Citroen Xantia X2 2.1 Turbo D12V	https://www.auto-data.net/en/citroen-xantia-x2-2.1-turbo-d12v-109hp-14947
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-I-01	4260	1702	1451	Auto-Data Citroen ZX Break N2 Phase I 1.9 D	https://www.auto-data.net/en/citroen-zx-break-n2-phase-i-1.9-d-71hp-15230
EU-CITROEN-ZX-N2-BREAK-WAGON-PHASE-II-01	4260	1705	1457	Auto-Data Citroen ZX Break N2 Phase II 1.9 D	https://www.auto-data.net/en/citroen-zx-break-n2-phase-ii-1.9-d-71hp-15231
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3801-3900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3801-3900_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3801-3900_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5202 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1533 行）

