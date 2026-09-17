# 任务：all 第 4101-4200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0042__5b5805fe


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4101-4200 行

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
all 第 4101-4200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-R8-I-COUPE-V8-PREFL-01	4431	1904	1252
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	5039	1902	1491
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	5039	1902	1491
EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	5179	1902	1484
EU-BMW-7-SERIES-F01-SEDAN-SWB-01	5072	1902	1479
EU-BMW-7-SERIES-F02-SEDAN-LWB-01	5212	1902	1479
EU-BMW-X1-E84-SUV-FACELIFT-01	4477	1798	1545
EU-BMW-X1-E84-SUV-PREFL-01	4454	1798	1545
EU-DODGE-AVENGER-JS-SEDAN-01	4850	1843	1497
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691
EU-DODGE-NITRO-I-KA-SUV-5D-01	4584	1856	1773
EU-FIAT-PUNTO-2012-HATCHBACK-01	4065	1687	1490
EU-LADA-KALINA-I-1117-WAGON-01	4040	1700	1500
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500
EU-LADA-KALINA-I-SEDAN-4D-01	4040	1700	1500
EU-LADA-PRIORA-I-2170-SEDAN-01	4350	1680	1420
EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	4210	1680	1435
EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	4210	1680	1420
EU-LEXUS-RX-II-SUV-350-AWD-01	4740	1845	1705
EU-LEXUS-RX-I-XU10-SUV-01	4580	1815	1660
EU-MAZDA-CX-7-ER-SUV-5D-01	4680	1870	1645
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-01	4329	1801	1292
EU-PORSCHE-CAYENNE-955-TURBO-S-SUV-01	4786	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-GTS-01	4795	1928	1675
EU-PORSCHE-CAYENNE-957-SUV-STANDARD-01	4798	1928	1699
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696
EU-PORSCHE-CAYMAN-987C-COUPE-01	4341	1801	1305
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
KIA	Sorento ii	2.4 Cvvt	SUV	Frontantrieb	Benzin	128	174	Nov 2009	Dec 2015	2024-03-01	32045
KIA	Sorento ii	2.4 Cvvt 4WD	SUV	Allrad	Benzin	128	174	Nov 2009	Dec 2015	2024-03-01	32046
KIA	Sorento ii	2.2 Crdi	SUV	Frontantrieb	Diesel	145	197	Nov 2009	Dec 2015	2024-03-01	32047
KIA	Sorento ii	2.2 Crdi 4WD	SUV	Allrad	Diesel	145	197	Nov 2009	Dec 2015	2024-03-01	32048
Land Rover	Discovery iv	3.0 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	180	245	Sep 2009	Dec 2018	2024-03-01	32050
Land Rover	Range rover iii	5.0 4X4	Geländewagen geschlossen	Allrad	Benzin	375	510	Sep 2009	Aug 2012	2024-03-01	32051
Land Rover	Range rover sport i	5.0 4X4	SUV	Allrad	Benzin	375	510	Sep 2009	Mar 2013	2024-03-01	32052
Land Rover	Range rover sport i	3.0 D 4X4	SUV	Allrad	Diesel	180	245	Sep 2009	Mar 2013	2024-03-01	32053
Lada	Niva	1.7 LPG	Geländewagen geschlossen	Allrad	Benzin/Autogas (LPG)	57	78	Sep 2002	Dec 2015	2024-03-01	32054
Lada	Priora	1.6 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	71	96	Mar 2009	Sep 2016	2024-03-01	32055
Lada	Priora	1.6 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	71	96	Dec 2008	Dec 2013	2024-03-01	32056
Lada	Kalina	1.4 16V LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	65	88	Nov 2008	Dec 2013	2024-03-01	32057
Lada	Kalina	1.4 16V LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	65	88	Nov 2008	Dec 2013	2024-03-01	32058
Lada	Kalina	1.4 16V LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	65	88	Nov 2008	Dec 2013	2024-03-01	32059
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	386	525	Apr 2009	Jul 2015	2024-03-01	32060
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	386	525	Feb 2010	Jul 2015	2024-03-01	32062
VW	Golf vi	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	Oct 2008	Nov 2012	2024-03-01	32063
Porsche	Panamera	4.8 S	Schrägheck	Heckantrieb	Benzin	294	400	Sep 2009	Jul 2013	2024-03-01	32064
Porsche	Panamera	4.8 4S	Schrägheck	Allrad	Benzin	294	400	Sep 2009	Jul 2013	2024-03-01	32065
Porsche	Panamera	4.8 Turbo	Schrägheck	Allrad	Benzin	368	500	Sep 2009	Jul 2013	2024-03-01	32066
Renault	7	1	Stufenheck	Frontantrieb	Benzin	37	50	Mar 1975	Dec 1982	2024-03-01	32067
Porsche	Boxster	2.9	Cabriolet	Heckantrieb	Benzin	188	255	Jun 2009	Mar 2012	2024-03-01	32068
Opel	Insignia a	2.8 V6 Turbo OPC 4X4	Schrägheck	Allrad	Benzin	239	325	Jul 2009	Mar 2017	2024-03-01	32069
Opel	Insignia a	2.8 V6 Turbo OPC 4X4	Stufenheck	Allrad	Benzin	239	325	Jul 2009	Mar 2017	2024-03-01	32070
Opel	Insignia a sports tourer	2.8 V6 Turbo OPC 4X4	Kombi	Allrad	Benzin	239	325	Jul 2009	Mar 2017	2024-03-01	32071
Suzuki	Sx4 / classic	1.6 VVT	Schrägheck	Frontantrieb	Benzin	88	120	Jul 2009	-	2024-03-01	32072
Suzuki	Sx4 / classic	1.6 VVT 4X4	Schrägheck	Allrad	Benzin	88	120	Jul 2009	-	2024-03-01	32073
Suzuki	Sx4 / classic	2.0 Ddis	Schrägheck	Frontantrieb	Diesel	99	135	Jul 2009	-	2024-03-01	32074
Porsche	Cayman	2.9	Coupe	Heckantrieb	Benzin	195	265	Feb 2009	Dec 2012	2024-03-01	32075
Suzuki	Sx4 / classic	2.0 Ddis 4X4	Schrägheck	Allrad	Diesel	99	135	Jul 2009	-	2024-03-01	32076
Porsche	Cayman	S 3.4	Coupe	Heckantrieb	Benzin	235	320	Feb 2009	Jun 2013	2024-03-01	32077
Land Rover	Defender station wagon	2.5 D 4X4	Geländewagen geschlossen	Allrad	Diesel	51	69	Sep 1990	Jul 1994	2024-03-01	32080
Land Rover	Defender cabrio	2.5 D 4X4	Geländewagen offen	Allrad	Diesel	51	69	Sep 1990	Jul 1994	2024-03-01	32081
Porsche	Cayenne	Turbo S 4.8	SUV	Allrad	Benzin	404	550	Aug 2008	Sep 2010	2024-03-01	32082
Porsche	Cayenne	Turbo S 4.8	SUV	Allrad	Benzin	397	540	Feb 2007	Sep 2010	2024-03-01	32084
Opel	Astra j	1.4	Schrägheck	Frontantrieb	Benzin	64	87	Dec 2009	Oct 2015	2024-03-01	32085
Opel	Astra j	1.4	Schrägheck	Frontantrieb	Benzin	74	100	Dec 2009	Oct 2015	2024-03-01	32086
Opel	Astra j	1.6	Schrägheck	Frontantrieb	Benzin	85	115	Dec 2009	Oct 2015	2024-03-01	32087
Opel	Astra j	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	103	140	Dec 2009	Oct 2015	2024-03-01	32088
Opel	Astra j	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Dec 2009	Oct 2015	2024-03-01	32089
Opel	Astra j	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	70	95	Dec 2009	Oct 2015	2024-03-01	32090
Opel	Astra j	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Sep 2009	Oct 2015	2024-03-01	32091
Opel	Astra j	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	92	125	Dec 2009	Oct 2015	2024-03-01	32092
Opel	Astra j	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	118	160	Sep 2009	Oct 2015	2024-03-01	32093
Dodge	Journey	3.5	Großraumlimousine	Frontantrieb	Benzin	173	235	Jun 2008	Dec 2010	2024-03-01	32097
Dodge	Journey	3.5 AWD	Großraumlimousine	Allrad	Benzin	173	235	Jun 2008	Dec 2010	2024-03-01	32098
Dodge	Journey	2.4 Eco+	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	125	170	Jun 2008	-	2024-03-01	32101
BMW	7	750 I, LI Xdrive	Stufenheck	Allrad	Benzin	300	408	Sep 2009	Jun 2012	2024-03-01	32103
BMW	7	760 I, LI	Stufenheck	Heckantrieb	Benzin	400	544	Sep 2009	Dec 2015	2024-03-01	32104
BMW	7	740 D	Stufenheck	Heckantrieb	Diesel	225	306	Sep 2009	Jun 2012	2024-03-01	32105
BMW	5	535 I	Schrägheck	Heckantrieb	Benzin	225	306	Jan 2009	Feb 2017	2024-03-01	32106
BMW	5	550 I	Schrägheck	Heckantrieb	Benzin	300	408	Aug 2009	Jun 2012	2024-03-01	32107
BMW	5	530 D	Schrägheck	Heckantrieb	Diesel	180	245	Aug 2009	Jun 2012	2024-03-01	32108
Alpina	B7	Biturbo	Stufenheck	Heckantrieb	Benzin	373	507	Mar 2009	Jun 2012	2024-03-01	32109
Mazda	Cx-7	2.3 MZR Disi Turbo AWD	SUV	Allrad	Benzin	191	260	Jun 2009	Mar 2013	2024-03-01	32110
Mazda	Cx-7	2.2 Mzr-cd AWD	SUV	Allrad	Diesel	127	173	Jul 2009	Mar 2013	2024-03-01	32111
BMW	X1	Xdrive 28 I	SUV	Allrad	Benzin	190	258	Sep 2009	Aug 2011	2024-03-01	32112
BMW	X1	Sdrive 18 D	SUV	Heckantrieb	Diesel	105	143	Dec 2009	Jun 2015	2024-03-01	32113
BMW	X1	Xdrive 18 D	SUV	Allrad	Diesel	105	143	Oct 2009	Jun 2015	2024-03-01	32114
BMW	X1	Xdrive 20 D	SUV	Allrad	Diesel	130	177	Sep 2009	Jun 2012	2024-03-01	32115
BMW	X1	Sdrive 20 D	SUV	Heckantrieb	Diesel	130	177	Oct 2009	Jun 2015	2024-03-01	32116
BMW	X1	Xdrive 23 D	SUV	Allrad	Diesel	150	204	Oct 2009	Jun 2015	2024-03-01	32117
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	151	205	Jul 2009	Jun 2011	2024-03-01	32118
Volvo	Xc60 i	2.4 D	SUV	Frontantrieb	Diesel	129	175	Apr 2009	Dec 2010	2024-03-01	32119
Volvo	Xc60 i	3.2 AWD	SUV	Allrad	Benzin	175	238	Jul 2009	Dec 2010	2024-03-01	32120
Subaru	Outback	2.0 D AWD	Kombi	Allrad	Diesel	110	150	Sep 2009	-	2024-03-01	32121
Subaru	Outback	2.5 I AWD	Kombi	Allrad	Benzin	123	167	Sep 2009	-	2024-03-01	32122
Subaru	Outback	3.6 R AWD	Kombi	Allrad	Benzin	191	260	Sep 2009	-	2024-03-01	32123
Subaru	Legacy v	2.0 I AWD	Stufenheck	Allrad	Benzin	110	150	Sep 2009	Dec 2014	2024-03-01	32124
Subaru	Legacy v	2.5 I AWD	Stufenheck	Allrad	Benzin	123	167	Sep 2009	Dec 2014	2024-03-01	32125
Subaru	Legacy v	2.0 D AWD	Stufenheck	Allrad	Diesel	110	150	Sep 2009	Dec 2014	2024-03-01	32126
Subaru	Legacy v station wagon	2.0 D AWD	Kombi	Allrad	Diesel	110	150	Sep 2009	Dec 2014	2024-03-01	32127
Subaru	Legacy v station wagon	2.0 I AWD	Kombi	Allrad	Benzin	110	150	Sep 2009	Dec 2014	2024-03-01	32128
Subaru	Legacy v station wagon	2.5 I AWD	Kombi	Allrad	Benzin	123	167	Sep 2009	Dec 2014	2024-03-01	32129
Tesla	Roadster	Electric	Cabriolet	Heckantrieb	Elektro	185	252	Mar 2008	-	2024-03-01	32131
Dodge	Avenger	2.4	Stufenheck	Frontantrieb	Benzin	125	170	Jun 2007	Dec 2014	2024-03-01	32139
Dodge	Avenger	2.4	Stufenheck	Frontantrieb	Benzin	129	175	Jun 2007	Dec 2014	2024-03-01	32140
Dodge	Nitro	3.7 V6 4WD	SUV	Allrad	Benzin	151	205	Jun 2007	Dec 2012	2024-03-01	32141
VW	Scirocco	2.0 TSI	Coupe	Frontantrieb	Benzin	155	210	Nov 2009	Nov 2017	2024-03-01	32159
VW	Eos	2.0 TSI	Cabriolet	Frontantrieb	Benzin	155	210	Nov 2009	Aug 2015	2024-03-01	32160
Mercedes-benz	E-Klasse	E 200 CDI / Bluetec	Stufenheck	Heckantrieb	Diesel	100	136	Jan 2009	Dec 2015	2024-03-01	32161
Mercedes-benz	E-Klasse	E 200 CGI	Stufenheck	Heckantrieb	Benzin	135	184	Aug 2009	Dec 2015	2024-03-01	32162
Mercedes-benz	Gl-Klasse	GL 350 CDI 4-matic	SUV	Allrad	Diesel	165	224	May 2009	Aug 2012	2024-03-01	32163
Mercedes-benz	Gl-Klasse	GL 450 CDI 4-matic	SUV	Allrad	Diesel	225	306	May 2009	Aug 2012	2024-03-01	32164
Mercedes-benz	M-Klasse	ML 300 CDI 4-matic	SUV	Allrad	Diesel	140	190	Jul 2009	Dec 2011	2024-03-01	32165
Mercedes-benz	M-Klasse	ML 350 CDI 4-matic	SUV	Allrad	Diesel	165	224	Jul 2009	Dec 2011	2024-03-01	32166
Mercedes-benz	M-Klasse	ML 350 CDI 4-matic	SUV	Allrad	Diesel	155	211	Sep 2009	Dec 2011	2024-03-01	32167
Mercedes-benz	M-Klasse	ML 450 CDI 4-matic	SUV	Allrad	Diesel	225	306	Sep 2009	Dec 2011	2024-03-01	32168
BMW	1	118 D	Schrägheck	Heckantrieb	Diesel	100	136	Sep 2006	Dec 2011	2024-03-01	32172
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	120	163	Mar 2007	Dec 2011	2024-03-01	32173
BMW	1	120 I	Cabriolet	Heckantrieb	Benzin	120	163	Mar 2008	Dec 2013	2024-03-01	32174
BMW	1	120 D	Cabriolet	Heckantrieb	Diesel	120	163	Mar 2008	Dec 2013	2024-03-01	32175
BMW	1	118 D	Cabriolet	Heckantrieb	Diesel	100	136	Sep 2008	Dec 2013	2024-03-01	32176
BMW	1	120 D	Coupe	Heckantrieb	Diesel	120	163	Sep 2007	Oct 2013	2024-03-01	32177
Lexus	Rx	350 AWD	SUV	Allrad	Benzin	204	277	Dec 2008	Aug 2015	2024-03-01	32194
Fiat	Punto	1.2	Schrägheck	Frontantrieb	Benzin	48	65	Oct 2009	Feb 2012	2024-03-01	32247
Fiat	Punto	1.4	Schrägheck	Frontantrieb	Benzin	57	77	Oct 2009	Feb 2012	2024-03-01	32248
Fiat	Punto	1.4 16V	Schrägheck	Frontantrieb	Benzin	77	105	Oct 2009	Feb 2012	2024-03-01	32249
Fiat	Punto	1.4 16V	Schrägheck	Frontantrieb	Benzin	99	135	Oct 2009	Feb 2012	2024-03-01	32250
Fiat	Punto	1.3 D Multijet	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2009	Feb 2012	2024-03-01	32251


--- Round 1 / 首次发送 ---
## 更新点

* 已完成全部 100 个输入 Ktype，按改款、门数、长短轴、悬架高度和特殊外廓拆分为 145 条映射。
* Dodge Journey 改款后采用官方规格中的标准车高 1693 mm，未误用包含车顶行李架的 1765 mm。([FCA Press Kit][1])
* Audi R8 V10 Coupe 已按改款前后不同长宽拆分；Kalina 1117、1118、1119 的三维已按车型分别闭合。([汽车数据][2])
* 已完成固定表头、唯一主键、引用闭合、正整数三维、来源非空和孤立组检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：145
* PENDING 映射：0
* DIMENSION_GROUP：76
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
32045_prefl	32045	SUV	Sorento II	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32045_facelift	32045	SUV	Sorento II facelift	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32046_prefl	32046	SUV	Sorento II	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32046_facelift	32046	SUV	Sorento II facelift	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32047_prefl	32047	SUV	Sorento II	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32047_facelift	32047	SUV	Sorento II facelift	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32048_prefl	32048	SUV	Sorento II	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32048_facelift	32048	SUV	Sorento II facelift	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32050	32050	SUV	Discovery IV	L319	5	EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	HIGH		READY
32051	32051	SUV	Range Rover III facelift	L322	5	EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-FACELIFT-01	HIGH		READY
32052	32052	SUV	Range Rover Sport I facelift	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	HIGH		READY
32053	32053	SUV	Range Rover Sport I facelift	L320	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	HIGH		READY
32054_prefl	32054	SUV	Niva	21214	3	EU-LADA-NIVA-21214-SUV-PREFL-01	MEDIUM	该Ktype跨越2009年外廓改款边界，按改款前外廓拆分。	READY
32054_facelift	32054	SUV	Niva facelift	21214	3	EU-LADA-NIVA-21214-SUV-FACELIFT-01	MEDIUM	该Ktype跨越2009年外廓改款边界，按改款后外廓拆分。	READY
32055	32055	Sedan	Priora I	2170	4	EU-LADA-PRIORA-I-2170-SEDAN-01	HIGH		READY
32056_prefl	32056	Hatchback	Priora I	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32056_facelift	32056	Hatchback	Priora I facelift	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32057	32057	Wagon	Kalina I	1117	5	EU-LADA-KALINA-I-1117-WAGON-01	HIGH		READY
32058	32058	Sedan	Kalina I	1118	4	EU-LADA-KALINA-I-SEDAN-4D-01	HIGH		READY
32059	32059	Hatchback	Kalina I	1119	5	EU-LADA-KALINA-I-HATCHBACK-5D-01	HIGH		READY
32060_prefl	32060	Coupe	R8 I	42	2	EU-AUDI-R8-I-42-COUPE-V10-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32060_facelift	32060	Coupe	R8 I facelift	42	2	EU-AUDI-R8-I-42-COUPE-V10-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32062_prefl	32062	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V10-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32062_facelift	32062	Convertible	R8 I facelift	42	2	EU-AUDI-R8-I-42-CONVERTIBLE-V10-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32063_3dr	32063	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32063_5dr	32063	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
32064	32064	Hatchback	Panamera G1	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
32065	32065	Hatchback	Panamera G1	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
32066	32066	Hatchback	Panamera G1	970	5	EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	HIGH		READY
32067	32067	Sedan	Renault 7		4	EU-RENAULT-7-SEDAN-4D-01	MEDIUM	车身代码未获可靠证据，按已确认四门轿车外廓映射。	READY
32068	32068	Convertible	Boxster 987 facelift	987	2	EU-PORSCHE-BOXSTER-987-CONVERTIBLE-FACELIFT-01	HIGH		READY
32069_prefl	32069	Hatchback	Insignia A	G09	5	EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32069_facelift	32069	Hatchback	Insignia A facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32070_prefl	32070	Sedan	Insignia A	G09	4	EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32070_facelift	32070	Sedan	Insignia A facelift	G09	4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32071_prefl	32071	Wagon	Insignia A	G09	5	EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32071_facelift	32071	Wagon	Insignia A facelift	G09	5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32072	32072	Hatchback	SX4 I facelift	GY	5	EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-FWD-01	HIGH		READY
32073	32073	Hatchback	SX4 I facelift	GY	5	EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-AWD-01	HIGH	四驱悬架高度形成独立外廓。	READY
32074	32074	Hatchback	SX4 I facelift	GY	5	EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-FWD-01	HIGH		READY
32075	32075	Coupe	Cayman 987C facelift	987C	2	EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-BASE-01	HIGH		READY
32076	32076	Hatchback	SX4 I facelift	GY	5	EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-AWD-01	HIGH	四驱悬架高度形成独立外廓。	READY
32077	32077	Coupe	Cayman 987C facelift	987C	2	EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-S-01	HIGH	S版车高与2.9版不同，独立映射。	READY
32080_swb	32080	SUV	Defender	L316	3	EU-LAND-ROVER-DEFENDER-L316-SUV-90-SWB-01	HIGH	该Ktype覆盖90与110轴距，按90短轴Station Wagon拆分。	READY
32080_lwb	32080	SUV	Defender	L316	5	EU-LAND-ROVER-DEFENDER-L316-SUV-110-LWB-01	HIGH	该Ktype覆盖90与110轴距，按110长轴Station Wagon拆分。	READY
32081	32081	Convertible	Defender	L316	2	EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SWB-01	HIGH	开放式90短轴车身。	READY
32082	32082	SUV	Cayenne 957	957	5	EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	HIGH		READY
32084	32084	SUV	Cayenne 957	957	5	EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	HIGH		READY
32085	32085	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32086	32086	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32087	32087	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32088	32088	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32089	32089	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32090	32090	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32091	32091	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32092	32092	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32093	32093	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	HIGH		READY
32097	32097	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH		READY
32098	32098	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	HIGH		READY
32101_prefl	32101	MPV	Journey I	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32101_facelift	32101	MPV	Journey I facelift	JC	5	EU-DODGE-JOURNEY-I-MPV-5D-FACELIFT-02	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32103_swb	32103	Sedan	7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH	VariantName同时覆盖750i与750Li，按短轴F01拆分。	READY
32103_lwb	32103	Sedan	7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	HIGH	VariantName同时覆盖750i与750Li，按长轴F02拆分。	READY
32104_swb_prefl	32104	Sedan	7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	MEDIUM	该Ktype覆盖短轴/长轴及改款前后，按短轴改款前外廓拆分。	READY
32104_lwb_prefl	32104	Sedan	7 Series F02	F02	4	EU-BMW-7-SERIES-F02-SEDAN-LWB-01	MEDIUM	该Ktype覆盖短轴/长轴及改款前后，按长轴改款前外廓拆分。	READY
32104_swb_facelift	32104	Sedan	7 Series F01 LCI	F01	4	EU-BMW-7-SERIES-F01-LCI-SEDAN-SWB-01	MEDIUM	该Ktype覆盖短轴/长轴及改款前后，按短轴改款后外廓拆分。	READY
32104_lwb_facelift	32104	Sedan	7 Series F02 LCI	F02	4	EU-BMW-7-SERIES-F02-LCI-SEDAN-LWB-01	MEDIUM	该Ktype覆盖短轴/长轴及改款前后，按长轴改款后外廓拆分。	READY
32105	32105	Sedan	7 Series F01	F01	4	EU-BMW-7-SERIES-F01-SEDAN-SWB-01	HIGH		READY
32106_prefl	32106	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32106_facelift	32106	Hatchback	5 Series Gran Turismo F07 LCI	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32107	32107	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
32108	32108	Hatchback	5 Series Gran Turismo F07	F07	5	EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	HIGH		READY
32109_swb	32109	Sedan	B7 F01	F01	4	EU-ALPINA-B7-F01-SEDAN-SWB-01	HIGH	B7 BiTurbo同时覆盖短轴与长轴，按短轴F01拆分。	READY
32109_lwb	32109	Sedan	B7 F02	F02	4	EU-ALPINA-B7-F02-SEDAN-LWB-01	HIGH	B7 BiTurbo同时覆盖短轴与长轴，按长轴F02拆分。	READY
32110	32110	SUV	CX-7 I facelift	ER	5	EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	HIGH		READY
32111	32111	SUV	CX-7 I facelift	ER	5	EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	HIGH		READY
32112	32112	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	HIGH		READY
32113_prefl	32113	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32113_facelift	32113	SUV	X1 E84 facelift	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32114_prefl	32114	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32114_facelift	32114	SUV	X1 E84 facelift	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32115	32115	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	HIGH		READY
32116_prefl	32116	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32116_facelift	32116	SUV	X1 E84 facelift	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32117_prefl	32117	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32117_facelift	32117	SUV	X1 E84 facelift	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32118	32118	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	厂商车身代码未在采用来源中明确。	READY
32119	32119	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	厂商车身代码未在采用来源中明确。	READY
32120	32120	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-5D-01	HIGH	厂商车身代码未在采用来源中明确。	READY
32121_prefl	32121	Wagon	Outback IV	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32121_facelift	32121	Wagon	Outback IV facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32122_prefl	32122	Wagon	Outback IV	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32122_facelift	32122	Wagon	Outback IV facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32123_prefl	32123	Wagon	Outback IV	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32123_facelift	32123	Wagon	Outback IV facelift	BR	5	EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32124_prefl	32124	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32124_facelift	32124	Sedan	Legacy V facelift	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32125_prefl	32125	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32125_facelift	32125	Sedan	Legacy V facelift	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32126_prefl	32126	Sedan	Legacy V	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32126_facelift	32126	Sedan	Legacy V facelift	BM	4	EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32127_prefl	32127	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32127_facelift	32127	Wagon	Legacy V facelift	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32128_prefl	32128	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32128_facelift	32128	Wagon	Legacy V facelift	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32129_prefl	32129	Wagon	Legacy V	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32129_facelift	32129	Wagon	Legacy V facelift	BR	5	EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32131	32131	Convertible	Roadster I		2	EU-TESLA-ROADSTER-I-CONVERTIBLE-2D-01	HIGH	厂商车身代码未在采用来源中明确。	READY
32139_prefl	32139	Sedan	Avenger JS	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32139_facelift	32139	Sedan	Avenger JS facelift	JS	4	EU-DODGE-AVENGER-JS-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32140_prefl	32140	Sedan	Avenger JS	JS	4	EU-DODGE-AVENGER-JS-SEDAN-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32140_facelift	32140	Sedan	Avenger JS facelift	JS	4	EU-DODGE-AVENGER-JS-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32141	32141	SUV	Nitro I	KA	5	EU-DODGE-NITRO-I-KA-SUV-5D-01	HIGH		READY
32159_prefl	32159	Coupe	Scirocco III	13	3	EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32159_facelift	32159	Coupe	Scirocco III facelift	13	3	EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32160_prefl	32160	Convertible	Eos I	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32160_facelift	32160	Convertible	Eos I facelift	1F7	2	EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32161_prefl	32161	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32161_facelift	32161	Sedan	E-Class W212 facelift	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32162_prefl	32162	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32162_facelift	32162	Sedan	E-Class W212 facelift	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32163	32163	SUV	GL-Class X164 facelift	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH		READY
32164	32164	SUV	GL-Class X164 facelift	X164	5	EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	HIGH		READY
32165	32165	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH		READY
32166	32166	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH		READY
32167	32167	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH		READY
32168	32168	SUV	M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	HIGH		READY
32172	32172	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
32173	32173	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
32174	32174	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
32175	32175	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
32176	32176	Convertible	1 Series E88	E88	2	EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	HIGH		READY
32177	32177	Coupe	1 Series E82	E82	2	EU-BMW-1-SERIES-E82-COUPE-2D-01	HIGH		READY
32194_prefl	32194	SUV	RX III	AL10	5	EU-LEXUS-RX-III-AL10-SUV-PREFL-01	MEDIUM	该Ktype跨越改款边界，按改款前外廓拆分。	READY
32194_facelift	32194	SUV	RX III facelift	AL10	5	EU-LEXUS-RX-III-AL10-SUV-FACELIFT-01	MEDIUM	该Ktype跨越改款边界，按改款后外廓拆分。	READY
32247_3dr	32247	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32247_5dr	32247	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
32248_3dr	32248	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32248_5dr	32248	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
32249_3dr	32249	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32249_5dr	32249	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
32250_3dr	32250	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32250_5dr	32250	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
32251_3dr	32251	Hatchback	Punto Evo	199	3	EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门车身，按三门外廓拆分。	READY
32251_5dr	32251	Hatchback	Punto Evo	199	5	EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门车身，按五门外廓拆分。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4101-4200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SORENTO-II-XM-SUV-PREFL-01	4685	1885	1755	Auto-Data	https://www.auto-data.net/en/kia-sorento-ii-2.4-16v-mpi-174hp-4wd-automatic-17867
EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	4685	1885	1745	Auto-Data	https://www.auto-data.net/en/kia-sorento-ii-facelift-2012-2.2d-16v-crdi-197hp-4wd-18996
EU-LAND-ROVER-DISCOVERY-IV-L319-SUV-5D-01	4829	1915	1887	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1405955/land_rover_discovery_4_3_0_tdv6_hse.html
EU-LAND-ROVER-RANGE-ROVER-III-L322-SUV-FACELIFT-01	4972	1956	1865	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1404500/range_rover_5_0_v8_vouge.html
EU-LAND-ROVER-RANGE-ROVER-SPORT-I-L320-SUV-FACELIFT-01	4783	1928	1789	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/1405145/range_rover_sport_5_0_supercharged_hse.html
EU-LADA-NIVA-21214-SUV-PREFL-01	3720	1680	1640	AvtoVAZ official archive	https://www.vaz.ru/v2121.htm
EU-LADA-NIVA-21214-SUV-FACELIFT-01	3740	1680	1640	Auto-Data	https://www.auto-data.net/en/lada-niva-3-door-facelift-2009-1.7i-81hp-4x4-43253
EU-LADA-PRIORA-I-2170-SEDAN-01	4350	1680	1420	Auto-Data	https://www.auto-data.net/en/lada-priora-i-sedan-facelift-2013-1.6-98hp-22348
EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	4210	1680	1420	Auto-Data	https://www.auto-data.net/en/lada-priora-model-1421
EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	4210	1680	1435	Auto-Data	https://www.auto-data.net/en/lada-priora-i-hatchback-facelift-2013-1.6-98hp-22352
EU-LADA-KALINA-I-1117-WAGON-01	4040	1700	1500	Lada Kalina official brochure	https://ladawiki.de/images/e/e1/Kalina_2008.pdf
EU-LADA-KALINA-I-SEDAN-4D-01	4040	1700	1500	Lada Kalina official brochure	https://ladawiki.de/images/e/e1/Kalina_2008.pdf
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500	Lada Kalina official brochure	https://ladawiki.de/images/e/e1/Kalina_2008.pdf
EU-AUDI-R8-I-42-COUPE-V10-PREFL-01	4434	1930	1252	Auto-Data	https://www.auto-data.net/en/audi-r8-coupe-42-5.2-fsi-v10-525hp-quattro-r-tronic-4256
EU-AUDI-R8-I-42-COUPE-V10-FACELIFT-01	4440	1929	1252	Auto-Data	https://www.auto-data.net/en/audi-r8-coupe-42-facelift-2012-5.2-fsi-v10-525hp-quattro-27158
EU-AUDI-R8-I-42-CONVERTIBLE-V10-PREFL-01	4434	1904	1244	Auto-Data	https://www.auto-data.net/en/audi-r8-spyder-42-5.2-fsi-v10-525hp-quattro-19189
EU-AUDI-R8-I-42-CONVERTIBLE-V10-FACELIFT-01	4440	1929	1244	Auto-Data	https://www.auto-data.net/en/audi-r8-spyder-42-facelift-2012-5.2-fsi-v10-525hp-quattro-27176
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-2.0-tdi-140hp-8610
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-2.0-tdi-140hp-41250
EU-PORSCHE-PANAMERA-970-HATCHBACK-5D-01	4970	1913	1418	Auto-Data	https://www.auto-data.net/en/porsche-panamera-g1-4s-4.8-v8-400hp-pdk-6728
EU-RENAULT-7-SEDAN-4D-01	3890	1525	1410	Auta5P; Losange Magazine	https://auta5p.eu/lang/en/katalog/auto.php?idf=Renault-7-TL-12720; https://www.losangemagazine.com/losange-magazine-issue-22-summer-2023/renault-siete-7-tl-1977-1980
EU-PORSCHE-BOXSTER-987-CONVERTIBLE-FACELIFT-01	4342	1801	1292	Auto-Data	https://www.auto-data.net/en/porsche-boxster-987-facelift-2009-2.9-255hp-40880
EU-OPEL-INSIGNIA-A-PREFL-HATCHBACK-01	4830	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-hatchback-a-opc-2.8-v6-turbo-325hp-4x4-1791
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-hatchback-a-facelift-2013-opc-2.8-v6-325hp-awd-turbo-ecotec-19617
EU-OPEL-INSIGNIA-A-PREFL-SEDAN-01	4830	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-sedan-a-opc-2.8-v6-turbo-325hp-4x4-1808
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	Auto-Data	https://www.auto-data.net/en/opel-insignia-sedan-a-facelift-2013-opc-2.8-v6-325hp-awd-turbo-ecotec-19593
EU-OPEL-INSIGNIA-A-PREFL-WAGON-5D-01	4908	1856	1520	Auto-Data	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-opc-2.8-v6-turbo-325hp-4x4-16688
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513	Auto-Data	https://www.auto-data.net/en/opel-insignia-sports-tourer-a-facelift-2013-opc-2.8-v6-325hp-awd-turbo-ecotec-automatic-19665
EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-FWD-01	4255	1755	1605	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-facelift-2009-1.6-vvt-120hp-17138
EU-SUZUKI-SX4-I-GY-HATCHBACK-5D-AWD-01	4255	1755	1620	Auto-Data	https://www.auto-data.net/en/suzuki-sx4-i-facelift-2009-1.6-vvt-120hp-i-awd-17139
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-BASE-01	4347	1801	1304	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-facelift-2009-2.9-265hp-40905
EU-PORSCHE-CAYMAN-987C-COUPE-FACELIFT-S-01	4347	1801	1306	Auto-Data	https://www.auto-data.net/en/porsche-cayman-987c-facelift-2009-s-3.4-320hp-40903
EU-LAND-ROVER-DEFENDER-L316-SUV-90-SWB-01	3883	1790	1963	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1394990/land-rover_defender_90_station_wagon_diesel.html
EU-LAND-ROVER-DEFENDER-L316-SUV-110-LWB-01	4599	1790	2035	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1394720/land-rover_defender_110_station_wagon_diesel.html
EU-LAND-ROVER-DEFENDER-L316-CONVERTIBLE-90-SWB-01	3722	1790	1965	Automobile-Catalog	https://www.automobile-catalog.com/car/1990/1394930/land-rover_defender_90_soft_top_diesel.html
EU-PORSCHE-CAYENNE-957-SUV-TURBO-S-01	4795	1928	1696	Auto-Data	https://www.auto-data.net/en/porsche-cayenne-955-facelift-2007-turbo-s-4.8-v8-550hp-awd-tiptronic-s-6721
EU-OPEL-ASTRA-J-P10-HATCHBACK-5D-01	4419	1814	1510	Auto-Data	https://www.auto-data.net/en/opel-astra-j-1.4-87hp-ecoflex-26012
EU-DODGE-JOURNEY-I-MPV-5D-01	4888	1834	1691	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/691625/dodge_journey_rt_2_7l_v-6_automatic.html
EU-DODGE-JOURNEY-I-MPV-5D-FACELIFT-02	4888	1835	1693	FCA 2015 Dodge Journey Canadian Specifications	https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Dodge/Journey/CN_2015_DG_Journey_SP.pdf
EU-BMW-7-SERIES-F01-SEDAN-SWB-01	5072	1902	1479	Auto-Data	https://www.auto-data.net/en/bmw-7-series-f01-740d-306hp-17305
EU-BMW-7-SERIES-F02-SEDAN-LWB-01	5212	1902	1479	Auto-Data	https://www.auto-data.net/en/bmw-7-series-long-f02-760li-544hp-steptronic-17303
EU-BMW-7-SERIES-F01-LCI-SEDAN-SWB-01	5079	1902	1471	Auto-Data	https://www.auto-data.net/en/bmw-7-series-f01-lci-facelift-2012-760i-544hp-steptronic-17767
EU-BMW-7-SERIES-F02-LCI-SEDAN-LWB-01	5219	1902	1471	Auto-Data	https://www.auto-data.net/en/bmw-7-series-long-f02-lci-facelift-2012-760li-544hp-steptronic-17768
EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	4998	1901	1559	Auto-Data	https://www.auto-data.net/en/bmw-5-series-gran-turismo-f07-535i-306hp-steptronic-17257
EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	5004	1901	1559	Auto-Data	https://www.auto-data.net/en/bmw-5-series-gran-turismo-f07-lci-facelift-2013-535i-306hp-steptronic-19995
EU-ALPINA-B7-F01-SEDAN-SWB-01	5087	1902	1478	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1186130/alpina_b7_biturbo.html
EU-ALPINA-B7-F02-SEDAN-LWB-01	5227	1902	1484	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1186160/alpina_b7_biturbo_l.html
EU-MAZDA-CX-7-ER-SUV-FACELIFT-02	4700	1870	1645	Auto-Data	https://www.auto-data.net/en/mazda-cx-7-facelift-2009-2.2-mzr-cd-173hp-awd-17513
EU-BMW-X1-E84-SUV-PREFL-01	4454	1798	1545	Auto-Data	https://www.auto-data.net/en/bmw-x1-e84-28i-258hp-xdrive-steptronic-9776
EU-BMW-X1-E84-SUV-FACELIFT-01	4477	1798	1545	Auto-Data	https://www.auto-data.net/en/bmw-x1-e84-lci-facelift-2012-18d-143hp-xdrive-17788
EU-VOLVO-XC60-I-SUV-5D-01	4627	1891	1713	Auto-Data	https://www.auto-data.net/en/volvo-xc60-i-2.4-d5-205hp-awd-geartronic-17163
EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	4775	1820	1605	Auto-Data	https://www.auto-data.net/en/subaru-outback-iv-br-bm-2.5i-167hp-awd-16141
EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	4790	1820	1605	Auto-Data	https://www.auto-data.net/en/subaru-outback-iv-br-bm-facelift-2013-2.5i-173hp-awd-lineartronic-22367
EU-SUBARU-LEGACY-V-BM-SEDAN-PREFL-01	4735	1780	1505	Auto-Data	https://www.auto-data.net/en/subaru-legacy-v-2.0i-150hp-awd-17912
EU-SUBARU-LEGACY-V-BM-SEDAN-FACELIFT-01	4745	1821	1506	Auto-Data	https://www.auto-data.net/en/subaru-legacy-v-facelift-2012-2.0-150hp-awd-22375
EU-SUBARU-LEGACY-V-BR-WAGON-PREFL-01	4775	1780	1535	Auto-Data	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-2.0d-150hp-awd-17954
EU-SUBARU-LEGACY-V-BR-WAGON-FACELIFT-01	4790	1780	1535	Auto-Data	https://www.auto-data.net/en/subaru-legacy-v-station-wagon-facelift-2012-2.0d-150hp-awd-22369
EU-TESLA-ROADSTER-I-CONVERTIBLE-2D-01	3946	1719	1127	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/3421640/tesla_roadster.html
EU-DODGE-AVENGER-JS-SEDAN-01	4850	1843	1497	Auto-Data	https://www.auto-data.net/en/dodge-avenger-sedan-2.4-16v-170hp-automatic-2881
EU-DODGE-AVENGER-JS-SEDAN-FACELIFT-01	4892	1850	1483	Auto-Data	https://www.auto-data.net/en/dodge-avenger-sedan-facelift-2010-2.4-173hp-automatic-51162
EU-DODGE-NITRO-I-KA-SUV-5D-01	4584	1856	1773	Auto-Data	https://www.auto-data.net/en/dodge-nitro-3.7-i-v6-12v-4wd-213hp-2932
EU-VW-SCIROCCO-III-13-COUPE-PREFL-01	4256	1810	1404	Auto-Data	https://www.auto-data.net/en/volkswagen-scirocco-iii-2.0-tsi-210hp-44226
EU-VW-SCIROCCO-III-13-COUPE-FACELIFT-01	4256	1810	1406	Auto-Data	https://www.auto-data.net/en/volkswagen-scirocco-iii-facelift-2014-2.0-tsi-180hp-20403
EU-VW-EOS-1F7-CONVERTIBLE-2D-PREFL-01	4407	1791	1443	Auto-Data	https://www.auto-data.net/en/volkswagen-eos-2.0-tsi-210hp-44196
EU-VW-EOS-1F7-CONVERTIBLE-2D-FACELIFT-01	4423	1791	1444	Auto-Data	https://www.auto-data.net/en/volkswagen-eos-facelift-2010-2.0-tsi-210hp-20466
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	4868	1854	1464	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-200-cdi-blueefficiency-136hp-17364
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-FACELIFT-01	4879	1854	1474	Auto-Data	https://www.auto-data.net/en/mercedes-benz-e-class-w212-facelift-2013-e-200-cdi-136hp-18716
EU-MERCEDES-BENZ-GL-X164-SUV-FACELIFT-01	5099	1920	1840	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gl-x164-facelift-2009-gl-350-cdi-224hp-blueefficiency-4matic-g-tronic-27823
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-FACELIFT-01	4781	1911	1815	Auto-Data	https://www.auto-data.net/en/mercedes-benz-m-class-w164-facelift-2008-ml-350-cdi-v6-224hp-4matic-7g-tronic-44884
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data	https://www.auto-data.net/en/bmw-1-series-hatchback-3dr-e81-118d-143hp-17245
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411	Auto-Data	https://www.auto-data.net/en/bmw-1-series-convertible-e88-120i-170hp-9829
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423	Auto-Data	https://www.auto-data.net/en/bmw-1-series-coupe-e82-120d-177hp-9835
EU-LEXUS-RX-III-AL10-SUV-PREFL-01	4740	1885	1725	Auto-Data	https://www.auto-data.net/en/lexus-rx-iii-350-4wd-277hp-5887
EU-LEXUS-RX-III-AL10-SUV-FACELIFT-01	4770	1885	1685	Auto-Data	https://www.auto-data.net/en/lexus-rx-iii-facelift-2012-350-277hp-awd-automatic-21315
EU-FIAT-PUNTO-EVO-199-HATCHBACK-3D-01	4065	1687	1490	Fiat official press release	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-punto-evo-evolution-of-the-species
EU-FIAT-PUNTO-EVO-199-HATCHBACK-5D-01	4065	1687	1490	Fiat official press release	https://www.media.stellantis.com/uk-en/fiat/press/new-fiat-punto-evo-evolution-of-the-species
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4101-4200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Dodge/Journey/CN_2015_DG_Journey_SP.pdf "https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Dodge/Journey/CN_2015_DG_Journey_SP.pdf"
[2]: https://www.auto-data.net/en/audi-r8-coupe-42-5.2-fsi-v10-525hp-quattro-r-tronic-4256 "https://www.auto-data.net/en/audi-r8-coupe-42-5.2-fsi-v10-525hp-quattro-r-tronic-4256"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4101-4200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4101-4200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4836 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2167 行）

- 尺寸冲突协调：
  - EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01 -> EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-02：4868x1854x1470 与 4868x1854x1464，创建新尺寸组
