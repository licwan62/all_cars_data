# 任务：left18448 第 2801-2900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0029__f530c13f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 2801-2900 行

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
left18448.tsv

【当前独立任务】
left18448 第 2801-2900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2801-2900_ktype_dimension_mapping_final.tsv
- left18448_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-X4-F26-SUV-M40I-01	4671	1901	1624
EU-BMW-X4-F26-SUV-STANDARD-01	4671	1881	1624

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
BMW	X4	Xdrive 20 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	107471
BMW	X4	Xdrive 20 I	SUV	Allrad	Benzin	Apr 2014	Mar 2018	101046
BMW	X4	Xdrive 20 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Aug 2021	-	145801
BMW	X4	Xdrive 28 I	SUV	Allrad	Benzin	Apr 2014	Mar 2018	101047
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	101050
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	116657
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	119043
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	Apr 2015	Mar 2018	119046
BMW	X4	Xdrive 30 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	121618
BMW	X4	Xdrive 30 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Jul 2021	-	145800
BMW	X4	Xdrive 35 D	SUV	Allrad	Diesel	Apr 2014	Mar 2018	101051
BMW	X4	Xdrive 35 I	SUV	Allrad	Benzin	Apr 2014	Mar 2018	101048
BMW	X4	Xdrive M40 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Aug 2021	-	146538
BMW	X5	3.0 3.0d	SUV	Allrad	Diesel	Feb 2007	Sep 2008	34969
BMW	X5	3.0 D	SUV	Allrad	Diesel	Apr 2001	Sep 2003	13043
BMW	X5	3.0 D	SUV	Allrad	Diesel	Oct 2003	Sep 2006	17625
BMW	X5	3.0 D	SUV	Allrad	Diesel	Oct 2003	Sep 2006	34968
BMW	X5	3.0 I	SUV	Allrad	Benzin	Apr 2000	Oct 2006	17176
BMW	X5	4.4 I	SUV	Allrad	Benzin	Jan 2000	Sep 2003	13042
BMW	X5	4.4 I	SUV	Allrad	Benzin	Oct 2003	Oct 2006	17624
BMW	X5	4.8 IS	SUV	Allrad	Benzin	Apr 2004	Sep 2006	18044
BMW	X5	M	SUV	Allrad	Benzin	Dec 2014	Jul 2018	108622
BMW	X5	M 50 D	SUV	Allrad	Diesel	Aug 2011	Jun 2013	55985
BMW	X5	M Competition Mild Hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	153714
BMW	X5	Sdrive 25 D	SUV	Heckantrieb	Diesel	Dec 2013	Jul 2015	100269
BMW	X5	Sdrive 25 D	SUV	Heckantrieb	Diesel	Aug 2015	Jul 2018	113459
BMW	X5	Sdrive 25 D	SUV	Heckantrieb	Diesel	Dec 2013	Jul 2018	116713
BMW	X5	Xdrive 25 D	SUV	Allrad	Diesel	Dec 2013	Jul 2015	100270
BMW	X5	Xdrive 25 D	SUV	Allrad	Diesel	Aug 2015	Jul 2018	113460
BMW	X5	Xdrive 25 D	SUV	Allrad	Diesel	Dec 2013	Jul 2018	116714
BMW	X5	Xdrive 28 I	SUV	Allrad	Benzin	Jun 2015	Jul 2018	116836
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	Oct 2008	Jul 2013	59334
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	Aug 2013	Jul 2018	108608
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	Dec 2013	Jul 2018	117397
BMW	X5	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Apr 2023	-	152806
BMW	X5	Xdrive 35 I	SUV	Allrad	Benzin	Feb 2012	Jun 2013	52207
BMW	X5	Xdrive 35 I	SUV	Allrad	Benzin	Dec 2013	Jul 2018	100268
BMW	X5	Xdrive 35 I	SUV	Allrad	Benzin	Dec 2013	Jul 2018	107919
BMW	X5	Xdrive 40 D	SUV	Allrad	Diesel	Dec 2013	Jul 2018	100271
BMW	X5	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Jun 2023	-	154729
BMW	X5	Xdrive 40 I	SUV	Allrad	Benzin	Jan 2012	Jun 2013	120501
BMW	X5	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Dec 2020	Mar 2023	143031
BMW	X5	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152807
BMW	X5	Xdrive 40E	SUV	Allrad	Benzin/Elektro	Aug 2015	Jul 2018	113842
BMW	X5	Xdrive 40E	SUV	Allrad	Benzin/Elektro	Aug 2015	Jul 2018	116697
BMW	X5	Xdrive 50 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152808
BMW	X5	Xdrive M60 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152813
BMW	X6	Activehybrid	SUV	Allrad	Benzin/Elektro	Jan 2009	Oct 2011	5756
BMW	X6	M	SUV	Allrad	Benzin	Dec 2014	Jul 2019	108623
BMW	X6	M 50 D	SUV	Allrad	Diesel	Aug 2011	Jun 2014	55986
BMW	X6	M 50 D	SUV	Allrad	Diesel	Aug 2014	Jul 2019	106410
BMW	X6	M Competition	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152817
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	Aug 2014	Jul 2019	106408
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	Aug 2014	Jul 2019	107472
BMW	X6	Xdrive 30 D	SUV	Allrad	Diesel	Aug 2014	Jul 2019	112267
BMW	X6	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Apr 2023	-	152814
BMW	X6	Xdrive 30 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Apr 2023	-	154727
BMW	X6	Xdrive 35 I	SUV	Allrad	Benzin	Jun 2007	Mar 2010	53100
BMW	X6	Xdrive 35 I	SUV	Allrad	Benzin	Aug 2012	Jun 2014	55254
BMW	X6	Xdrive 35 I	SUV	Allrad	Benzin	Aug 2014	Jul 2019	108002
BMW	X6	Xdrive 35 I	SUV	Allrad	Benzin	Aug 2014	Jul 2019	112268
BMW	X6	Xdrive 40 D	SUV	Allrad	Diesel	Dec 2014	Jul 2019	108255
BMW	X6	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Jun 2023	-	154728
BMW	X6	Xdrive 40 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152816
BMW	X6	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Dec 2020	Mar 2023	143030
BMW	X6	Xdrive 50 I	SUV	Allrad	Benzin	Oct 2007	Jun 2014	52831
BMW	X6	Xdrive 50 I	SUV	Allrad	Benzin	Aug 2014	Jul 2019	106409
BMW	X6	Xdrive M 60 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Apr 2023	-	152819
BMW	X7	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Jul 2022	-	148040
BMW	X7	Xdrive 40 D Mild-hybrid	SUV	Allrad	Diesel/Elektro	Apr 2023	-	154731
BMW	X7	Xdrive 40 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Jul 2022	-	148360
BMW	X7	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	Dec 2020	-	143029
BMW	X7	Xdrive M 60 I Mild Hybrid	SUV	Allrad	Benzin/Elektro	Jul 2022	-	148039
BMW	Xm	50E Allrad	SUV	Allrad	Benzin/Elektro	Sep 2023	-	156033
BMW	Xm	Label Allrad	SUV	Allrad	Benzin/Elektro	Aug 2023	-	154723
BMW	Xm	XM Allrad	SUV	Allrad	Benzin/Elektro	Dec 2022	-	151349
BMW	Z3	2.8 I	Coupe	Heckantrieb	Benzin	Jan 1998	May 2000	8829
BMW	Z3	3.0 I	Coupe	Heckantrieb	Benzin	Jun 2000	Jun 2003	14925
BMW	Z3	M	Coupe	Heckantrieb	Benzin	Jun 2001	Jun 2003	16073
BMW	Z3	M 3.2	Coupe	Heckantrieb	Benzin	Feb 1998	Jun 2000	35801
BMW	Z3 roadster	1.8 I	Cabriolet	Heckantrieb	Benzin	Oct 1995	Oct 1998	5110
BMW	Z3 roadster	1.9 I	Cabriolet	Heckantrieb	Benzin	Nov 1995	Mar 1999	5109
BMW	Z3 roadster	1.9 I	Cabriolet	Heckantrieb	Benzin	Jul 1998	Jan 2003	10228
BMW	Z3 roadster	1.9 I	Cabriolet	Heckantrieb	Benzin	Jan 1999	Jan 2003	11367
BMW	Z3 roadster	2.0 I	Cabriolet	Heckantrieb	Benzin	Apr 1999	Jan 2003	11299
BMW	Z3 roadster	2.2 I	Cabriolet	Heckantrieb	Benzin	Oct 2000	Jun 2002	15167
BMW	Z3 roadster	2.2 I	Cabriolet	Heckantrieb	Benzin	Aug 2000	Jan 2003	121971
BMW	Z3 roadster	3.0 I	Cabriolet	Heckantrieb	Benzin	Jun 2000	Jan 2003	14924
BMW	Z3 roadster	M 3.2	Cabriolet	Heckantrieb	Benzin	Jun 2001	Jan 2003	16072
BMW	Z3 roadster	M 3.2	Cabriolet	Heckantrieb	Benzin	Feb 1998	Jun 2000	35796
BMW	Z4 roadster	2.0 I	Cabriolet	Heckantrieb	Benzin	Mar 2005	Feb 2009	18561
BMW	Z4 roadster	2.2 I	Cabriolet	Heckantrieb	Benzin	Oct 2003	Oct 2005	17830
BMW	Z4 roadster	2.5 I	Cabriolet	Heckantrieb	Benzin	Dec 2002	Dec 2005	16829
BMW	Z4 roadster	2.5 SI	Cabriolet	Heckantrieb	Benzin	Sep 2005	Feb 2009	126072
BMW	Z4 roadster	3.0 I	Cabriolet	Heckantrieb	Benzin	Dec 2002	Dec 2005	16828
BMW	Z4 roadster	Sdrive 18 I	Cabriolet	Heckantrieb	Benzin	Apr 2013	Aug 2016	58751
BMW	Z4 roadster	Sdrive 20 I	Cabriolet	Heckantrieb	Benzin	Sep 2011	Aug 2016	11889
BMW	Z4 roadster	Sdrive 20 I	Cabriolet	Heckantrieb	Benzin	Sep 2011	Aug 2016	116678
BMW	Z4 roadster	Sdrive 28 I	Cabriolet	Heckantrieb	Benzin	Sep 2011	Aug 2016	11890
BMW	Z4 roadster	Sdrive 35 IS	Cabriolet	Heckantrieb	Benzin	Mar 2010	Aug 2016	34986


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 X4 全部 13 个 Ktype：F26 标准车型复用跨批次既有组；G02 的 xDrive20i、xDrive30i、M40i 均闭合至同一套 `4752×1918×1621 mm` 外廓，不因动力版本重复建组。
* 已完成除 E53 外的 27 个 X5 Ktype，闭合 E70 标准、E70 M50d、F15、F85、G05 改款前、G05 改款标准、G05 改款 50e、F95 M Competition 共 8 个 X5 尺寸组。E70 M50d 的 `2010 mm` 宽体与普通 E70 的 `1933 mm` 外廓分开建组。
* 本轮合计复用 1 个既有尺寸组，新建 9 个尺寸组。

## 当前批次进度

* READY 映射：40
* PENDING/尚待闭合输入：60
* 已确认尺寸组：10

  * 跨批次复用：1
  * 本轮新建：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
107471	107471	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101046	101046	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
145801	145801	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
101047	101047	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101050	101050	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
116657	116657	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
119043	119043	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
119046	119046	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
121618	121618	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
145800	145800	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
101051	101051	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101048	101048	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
146538	146538	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
34969	34969	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
108622	108622	SUV	X5 F85	F85	5	EU-BMW-X5-F85-SUV-M-01	HIGH	F85 M外廓。	READY
55985	55985	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-M50D-01	HIGH	E70 M50d宽体外廓。	READY
153714	153714	SUV	X5 F95	F95	5	EU-BMW-X5-F95-SUV-M-COMPETITION-01	HIGH	F95 M Competition改款外廓。	READY
100269	100269	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
113459	113459	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116713	116713	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
100270	100270	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
113460	113460	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116714	116714	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116836	116836	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
59334	59334	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
108608	108608	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
117397	117397	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
152806	152806	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
52207	52207	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
100268	100268	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
107919	107919	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
100271	100271	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
154729	154729	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
120501	120501	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
143031	143031	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前外廓。	READY
152807	152807	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
113842	113842	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116697	116697	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
152808	152808	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-50E-01	HIGH	G05改款xDrive50e高度分支。	READY
152813	152813	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款M60i标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	BMW X4 official technical specifications, valid 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329599EN/476188
EU-BMW-X5-E70-SUV-STANDARD-01	4854	1933	1776	BMW X5 xDrive30d/xDrive40d official specifications, valid 09/2011	https://www.press.bmwgroup.com/global/article/attachment/T0122149EN/177871
EU-BMW-X5-E70-SUV-M50D-01	4857	2010	1766	BMW X5 M50d official specifications, valid 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124400EN/207833
EU-BMW-X5-F15-SUV-STANDARD-01	4886	1938	1762	BMW X5 2013 official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591
EU-BMW-X5-F85-SUV-M-01	4880	1985	1754	BMW X5 M official technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0259568EN/424166
EU-BMW-X5-F95-SUV-M-COMPETITION-01	4948	2015	1762	BMW X5 M Competition official technical data	https://www.bmw.co.uk/en/all-models/m-models/bmw-x5-m/bmw-x5m-technical-data.html
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 xDrive30d official specifications, valid 08/2020	https://www.press.bmwgroup.com/global/article/attachment/T0309613EN/452651
EU-BMW-X5-G05-SUV-FACELIFT-01	4935	2004	1765	BMW X5 official technical specifications, valid 02/2023	https://www.press.bmwgroup.com/global/article/attachment/T0408159EN/649226
EU-BMW-X5-G05-SUV-FACELIFT-50E-01	4935	2004	1755	BMW X5 xDrive50e official technical specifications, valid 02/2023	https://www.press.bmwgroup.com/global/article/attachment/T0408159EN/649226
```

## 下一步优先处理

1. 闭合 X5 E53 的普通 3.0、V8/4.8is 以及改款前后高度边界。
2. 按 E71、F16、F86、G06、F96 聚类处理全部 X6 Ktype。
3. 随后处理 X7 G07 改款边界、XM G09，以及 Z3/Z4 的 Coupe、Roadster 和 M 外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2801-2900_ktype_dimension_mapping_final.tsv
- left18448_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合全部 X6 输入。E71 改款前、改款后和 E72 ActiveHybrid 分别使用 `1690`、`1699`、`1697 mm` 高度；跨越改款周期的 Ktype `52831` 拆分为两个物理分支。([宝马集团新闻][1])
* 已建立 F16 标准外廓与 F86 M 低顶外廓；分别为 `4909×1989×1702` 和 `4909×1989×1689 mm`。([宝马集团新闻][2])
* 已闭合 G06 改款前、G06 改款后及 F96 M Competition。G06 改款后普通车型与 M60i 复用同一 `4960×2004×1700 mm` 尺寸组。([宝马集团新闻][3])

## 当前批次进度

* 已闭合输入 Ktype：61 / 100
* READY 映射行：62
* PENDING 输入：39
* 已确认尺寸组：18

  * 上轮累计：10
  * 本轮首次创建：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5756	5756	SUV	X6 E72	E72	5	EU-BMW-X6-E72-SUV-ACTIVEHYBRID-01	HIGH	E72 ActiveHybrid专属外廓。	READY
108623	108623	SUV	X6 M F86	F86	5	EU-BMW-X6-F86-SUV-M-01	HIGH	F86 M低顶外廓。	READY
55986	55986	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH		READY
106410	106410	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152817	152817	SUV	X6 M F96	F96	5	EU-BMW-X6-F96-SUV-M-COMPETITION-01	HIGH	F96 M Competition改款外廓。	READY
106408	106408	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
107472	107472	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
112267	112267	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152814	152814	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
154727	154727	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
53100	53100	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	E71改款前外廓。	READY
55254	55254	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	E71改款后外廓。	READY
108002	108002	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
112268	112268	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
108255	108255	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
154728	154728	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
152816	152816	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
143030	143030	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前外廓。	READY
52831_prefl	52831	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	Ktype覆盖E71改款前外廓。	READY
52831_facelift	52831	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	Ktype覆盖E71改款后外廓。	READY
106409	106409	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152819	152819	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款M60i外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X6-E72-SUV-ACTIVEHYBRID-01	4877	1983	1697	BMW ActiveHybrid X6 official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0038993EN/59979
EU-BMW-X6-F86-SUV-M-01	4909	1989	1689	BMW X6 M official technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0259568EN/424166
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699	BMW X6 xDrive35i and xDrive50i official specifications, valid 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124596EN/207899
EU-BMW-X6-F16-SUV-STANDARD-01	4909	1989	1702	BMW 15 years of BMW X models official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591
EU-BMW-X6-F96-SUV-M-COMPETITION-01	4948	2019	1695	BMW X6 M Competition official specifications	https://www.press.bmwgroup.com/canada/article/detail/T0409475EN/the-new-bmw-x5-m-competition-and-the-new-bmw-x6-m-competition?language=en
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690	BMW X6 official technical specifications, 03/2008	https://www.press.bmwgroup.com/global/article/attachment/T0074093EN/110912
EU-BMW-X6-G06-SUV-FACELIFT-01	4960	2004	1700	BMW X6 official technical specifications, 02/2023	https://www.press.bmwgroup.com/france/article/attachment/T0408501FR/573646
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW The new BMW X6 official press kit	https://www.press.bmwgroup.com/asia/article/detail/T0298164EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
```

## 下一步优先处理

1. 闭合 X5 E53 六缸、V8 与 4.8is 的高度分支。
2. 处理 X7 G07 改款前后、XM G09。
3. 按 Z3 Coupe、Z3 Roadster、Z4 E85、Z4 E89 聚类完成剩余跑车映射。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0074093EN/110912?utm_source=chatgpt.com "The BMW X6."
[2]: https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591 "BMW Group PressClub"
[3]: https://www.press.bmwgroup.com/asia/article/detail/T0298164EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en&utm_source=chatgpt.com "The new BMW X6. A leader with broad shoulders."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_2801-2900_ktype_dimension_mapping_final.tsv
- left18448_2801-2900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合剩余 X5 E53、X7 G07、XM G09、Z3 与 Z4 映射；其中 X7 按改款前后、Z3 Roadster 按窄体/宽体及 M 外廓、Z4 E89 按标准与 sDrive35is 外廓分别建组。
* 已完成轻量机械检查：两张表表头正确，`id` 和 `DIMENSION_GROUP_ID` 唯一，全部映射引用闭合，所有尺寸组均被引用，三维与来源字段完整。
* 已创建两个任务指定文件。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射行：103
* PENDING：0
* DIMENSION_GROUP：31
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
107471	107471	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101046	101046	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
145801	145801	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
101047	101047	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101050	101050	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
116657	116657	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
119043	119043	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
119046	119046	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
121618	121618	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
145800	145800	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
101051	101051	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
101048	101048	SUV	X4 F26	F26	5	EU-BMW-X4-F26-SUV-STANDARD-01	HIGH		READY
146538	146538	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
34969	34969	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
13043	13043	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-SIX-CYLINDER-01	HIGH		READY
17625	17625	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-SIX-CYLINDER-01	HIGH		READY
34968	34968	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-SIX-CYLINDER-01	HIGH		READY
17176	17176	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-SIX-CYLINDER-01	HIGH		READY
13042	13042	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-V8-01	HIGH		READY
17624	17624	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-V8-01	HIGH		READY
18044	18044	SUV	X5 E53	E53	5	EU-BMW-X5-E53-SUV-V8-01	HIGH		READY
108622	108622	SUV	X5 F85	F85	5	EU-BMW-X5-F85-SUV-M-01	HIGH	F85 M外廓。	READY
55985	55985	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-M50D-01	HIGH	E70 M50d宽体外廓。	READY
153714	153714	SUV	X5 F95	F95	5	EU-BMW-X5-F95-SUV-M-COMPETITION-01	HIGH	F95 M Competition改款外廓。	READY
100269	100269	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
113459	113459	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116713	116713	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
100270	100270	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
113460	113460	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116714	116714	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116836	116836	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
59334	59334	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
108608	108608	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
117397	117397	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
152806	152806	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
52207	52207	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
100268	100268	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
107919	107919	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
100271	100271	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
154729	154729	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
120501	120501	SUV	X5 E70	E70	5	EU-BMW-X5-E70-SUV-STANDARD-01	HIGH		READY
143031	143031	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前外廓。	READY
152807	152807	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款标准外廓。	READY
113842	113842	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
116697	116697	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-STANDARD-01	HIGH		READY
152808	152808	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-50E-01	HIGH	G05改款xDrive50e高度分支。	READY
152813	152813	SUV	X5 G05	G05	5	EU-BMW-X5-G05-SUV-FACELIFT-01	HIGH	G05改款M60i标准外廓。	READY
5756	5756	SUV	X6 E72	E72	5	EU-BMW-X6-E72-SUV-ACTIVEHYBRID-01	HIGH	E72 ActiveHybrid专属外廓。	READY
108623	108623	SUV	X6 M F86	F86	5	EU-BMW-X6-F86-SUV-M-01	HIGH	F86 M低顶外廓。	READY
55986	55986	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH		READY
106410	106410	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152817	152817	SUV	X6 M F96	F96	5	EU-BMW-X6-F96-SUV-M-COMPETITION-01	HIGH	F96 M Competition改款外廓。	READY
106408	106408	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
107472	107472	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
112267	112267	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152814	152814	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
154727	154727	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
53100	53100	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	E71改款前外廓。	READY
55254	55254	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	E71改款后外廓。	READY
108002	108002	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
112268	112268	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
108255	108255	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
154728	154728	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
152816	152816	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款外廓。	READY
143030	143030	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前外廓。	READY
52831_prefl	52831	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	Ktype覆盖E71改款前外廓。	READY
52831_facelift	52831	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	Ktype覆盖E71改款后外廓。	READY
106409	106409	SUV	X6 F16	F16	5	EU-BMW-X6-F16-SUV-STANDARD-01	HIGH		READY
152819	152819	SUV	X6 G06	G06	5	EU-BMW-X6-G06-SUV-FACELIFT-01	HIGH	G06改款M60i外廓。	READY
148040	148040	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-FACELIFT-01	HIGH	G07改款外廓。	READY
154731	154731	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-FACELIFT-01	HIGH	G07改款外廓。	READY
148360	148360	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-FACELIFT-01	HIGH	G07改款外廓。	READY
143029	143029	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-PREFL-01	HIGH	G07改款前外廓。	READY
148039	148039	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-FACELIFT-01	HIGH	G07改款M60i外廓。	READY
156033	156033	SUV	XM G09	G09	5	EU-BMW-XM-G09-SUV-STANDARD-01	HIGH		READY
154723	154723	SUV	XM G09	G09	5	EU-BMW-XM-G09-SUV-STANDARD-01	HIGH		READY
151349	151349	SUV	XM G09	G09	5	EU-BMW-XM-G09-SUV-STANDARD-01	HIGH		READY
8829	8829	Coupe	Z3 Coupe	E36/8	2	EU-BMW-Z3-E36-8-COUPE-STANDARD-01	HIGH		READY
14925	14925	Coupe	Z3 Coupe	E36/8	2	EU-BMW-Z3-E36-8-COUPE-STANDARD-01	HIGH		READY
16073	16073	Coupe	Z3 M Coupe	E36/8	2	EU-BMW-Z3-E36-8-COUPE-M-01	HIGH	M Coupe低顶外廓。	READY
35801	35801	Coupe	Z3 M Coupe	E36/8	2	EU-BMW-Z3-E36-8-COUPE-M-01	HIGH	M Coupe低顶外廓。	READY
5110	5110	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-PREFL-NARROW-01	HIGH	改款前窄体Roadster外廓。	READY
5109	5109	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-PREFL-NARROW-01	HIGH	改款前窄体Roadster外廓。	READY
10228_prefl	10228	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-PREFL-NARROW-01	HIGH	Ktype覆盖改款前窄体外廓。	READY
10228_facelift	10228	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH	Ktype覆盖改款后宽体外廓。	READY
11367_prefl	11367	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-PREFL-NARROW-01	HIGH	Ktype覆盖改款前窄体外廓。	READY
11367_facelift	11367	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH	Ktype覆盖改款后宽体外廓。	READY
11299	11299	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH		READY
15167	15167	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH		READY
121971	121971	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH		READY
14924	14924	Convertible	Z3 Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	HIGH		READY
16072	16072	Convertible	Z3 M Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-M-01	HIGH	M Roadster专属外廓。	READY
35796	35796	Convertible	Z3 M Roadster	E36/7	2	EU-BMW-Z3-E36-7-CONVERTIBLE-M-01	HIGH	M Roadster专属外廓。	READY
18561	18561	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	HIGH		READY
17830	17830	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	HIGH		READY
16829	16829	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	HIGH		READY
126072	126072	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	HIGH		READY
16828	16828	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	HIGH		READY
58751	58751	Convertible	Z4 E89	E89	2	EU-BMW-Z4-E89-CONVERTIBLE-STANDARD-01	HIGH		READY
11889	11889	Convertible	Z4 E89	E89	2	EU-BMW-Z4-E89-CONVERTIBLE-STANDARD-01	HIGH		READY
116678	116678	Convertible	Z4 E89	E89	2	EU-BMW-Z4-E89-CONVERTIBLE-STANDARD-01	HIGH		READY
11890	11890	Convertible	Z4 E89	E89	2	EU-BMW-Z4-E89-CONVERTIBLE-STANDARD-01	HIGH		READY
34986	34986	Convertible	Z4 E89	E89	2	EU-BMW-Z4-E89-CONVERTIBLE-35IS-01	HIGH	sDrive35is低车身外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_2801-2900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X4-F26-SUV-STANDARD-01	4671	1881	1624	BMW 15 years of BMW X models official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	BMW X4 official technical specifications, valid 03/2021	https://www.press.bmwgroup.com/global/article/attachment/T0329599EN/476188
EU-BMW-X5-E70-SUV-STANDARD-01	4854	1933	1776	BMW X5 xDrive30d/xDrive40d official specifications, valid 09/2011	https://www.press.bmwgroup.com/global/article/attachment/T0122149EN/177871
EU-BMW-X5-E53-SUV-SIX-CYLINDER-01	4667	1872	1715	BMW 2002 X5 Series specifications; BMW 2006 X5 Series technical specifications	https://www.press.bmwgroup.com/usa/article/attachment/T0022132EN_US/41413;https://www.press.bmwgroup.com/usa/article/attachment/T0019119EN_US/37445
EU-BMW-X5-E53-SUV-V8-01	4667	1872	1707	BMW 2002 X5 Series specifications; BMW 2006 X5 Series technical specifications	https://www.press.bmwgroup.com/usa/article/attachment/T0022132EN_US/41413;https://www.press.bmwgroup.com/usa/article/attachment/T0019119EN_US/37445
EU-BMW-X5-F85-SUV-M-01	4880	1985	1754	BMW X5 M official technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0259568EN/424166
EU-BMW-X5-E70-SUV-M50D-01	4857	2010	1766	BMW X5 M50d official specifications, valid 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124400EN/207833
EU-BMW-X5-F95-SUV-M-COMPETITION-01	4948	2015	1762	BMW X5 M Competition official technical data	https://www.bmw.co.uk/en/all-models/m-models/bmw-x5-m/bmw-x5m-technical-data.html
EU-BMW-X5-F15-SUV-STANDARD-01	4886	1938	1762	BMW X5 2013 official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591
EU-BMW-X5-G05-SUV-FACELIFT-01	4935	2004	1765	BMW X5 official technical specifications, valid 02/2023	https://www.press.bmwgroup.com/global/article/attachment/T0408159EN/649226
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 xDrive30d official specifications, valid 08/2020	https://www.press.bmwgroup.com/global/article/attachment/T0309613EN/452651
EU-BMW-X5-G05-SUV-FACELIFT-50E-01	4935	2004	1755	BMW X5 xDrive50e official technical specifications, valid 02/2023	https://www.press.bmwgroup.com/global/article/attachment/T0408159EN/649226
EU-BMW-X6-E72-SUV-ACTIVEHYBRID-01	4877	1983	1697	BMW ActiveHybrid X6 official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0038993EN/59979
EU-BMW-X6-F86-SUV-M-01	4909	1989	1689	BMW X6 M official technical specifications	https://www.press.bmwgroup.com/india/article/attachment/T0259568EN/424166
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699	BMW X6 xDrive35i and xDrive50i official specifications, valid 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124596EN/207899
EU-BMW-X6-F16-SUV-STANDARD-01	4909	1989	1702	BMW 15 years of BMW X models official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0195402EN/284591
EU-BMW-X6-F96-SUV-M-COMPETITION-01	4948	2019	1695	BMW X6 M Competition official specifications	https://www.press.bmwgroup.com/canada/article/detail/T0409475EN/the-new-bmw-x5-m-competition-and-the-new-bmw-x6-m-competition?language=en
EU-BMW-X6-G06-SUV-FACELIFT-01	4960	2004	1700	BMW X6 official technical specifications, valid 02/2023	https://www.press.bmwgroup.com/france/article/attachment/T0408501FR/573646
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690	BMW X6 official technical specifications, 03/2008	https://www.press.bmwgroup.com/global/article/attachment/T0074093EN/110912
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW The new BMW X6 official press kit	https://www.press.bmwgroup.com/asia/article/detail/T0298164EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
EU-BMW-X7-G07-SUV-FACELIFT-01	5181	2000	1835	BMW X7 official technical specifications, valid 04/2022	https://www.press.bmwgroup.com/global/article/attachment/T0378353EN/555263
EU-BMW-X7-G07-SUV-PREFL-01	5151	2000	1805	BMW X7 xDrive40d official specifications, valid 08/2020	https://www.press.bmwgroup.com/global/article/attachment/T0309530EN/452542
EU-BMW-XM-G09-SUV-STANDARD-01	5110	2005	1755	BMW XM official technical specifications, 09/2022	https://www.press.bmwgroup.com/global/article/attachment/T0403971EN/572783
EU-BMW-Z3-E36-8-COUPE-STANDARD-01	4026	1740	1306	BMW 2001 Z3 Series specifications	https://www.press.bmwgroup.com/usa/article/attachment/T0021978EN_US/41275
EU-BMW-Z3-E36-8-COUPE-M-01	4025	1740	1280	BMW Z3 owner's manual, 07/1998	https://www.manualslib.de/manual/1195789/Bmw-Z3-Roadster-1-8-1998.html
EU-BMW-Z3-E36-7-CONVERTIBLE-PREFL-NARROW-01	4025	1692	1293	BMW Z3 owner's manual, 02/1998	https://www.adkusters.dsmynas.com/Website%20mynas/BMW%20Z3%20handleidingen/Ownersmanual%20Z3%201998%20Duits.pdf
EU-BMW-Z3-E36-7-CONVERTIBLE-FACELIFT-01	4049	1740	1293	BMW 2001 Z3 Series specifications	https://www.press.bmwgroup.com/usa/article/attachment/T0021978EN_US/41275
EU-BMW-Z3-E36-7-CONVERTIBLE-M-01	4025	1740	1266	BMW Z3 owner's manual, 07/1998	https://www.manualslib.de/manual/1195789/Bmw-Z3-Roadster-1-8-1998.html
EU-BMW-Z4-E85-CONVERTIBLE-STANDARD-01	4091	1781	1299	BMW Z4 Roadster official technical specifications	https://www.press.bmwgroup.com/china/article/attachment/T0018685ZH_CN/36711
EU-BMW-Z4-E89-CONVERTIBLE-STANDARD-01	4239	1790	1291	BMW Z4 official technical specifications, 04/2013	https://www.press.bmwgroup.com/global/article/attachment/T0139857EN/213510
EU-BMW-Z4-E89-CONVERTIBLE-35IS-01	4244	1790	1284	BMW Z4 sDrive35is official technical specifications, 04/2013	https://www.press.bmwgroup.com/global/article/attachment/T0139857EN/213510
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_2801-2900_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3391 行）
- 累计尺寸组：dimension_groups_final.tsv（872 行）

