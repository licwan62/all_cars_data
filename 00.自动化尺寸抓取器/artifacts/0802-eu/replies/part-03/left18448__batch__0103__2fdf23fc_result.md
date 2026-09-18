# 任务：left18448 第 10201-10300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0103__2fdf23fc


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 10201-10300 行

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
left18448 第 10201-10300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MERCEDES-BENZ-GLE-I-W166-AMG43-SUV-01	4816	1926	1762
EU-MERCEDES-BENZ-GLE-I-W166-AMG63-SUV-01	4852	1970	1762
EU-MERCEDES-BENZ-GLE-I-W166-AMG63S-SUV-01	4852	1970	1760
EU-MERCEDES-BENZ-GLE-I-W166-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-AMG53-HYBRID-SUV-FACELIFT-01	4937	2018	1782
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	Gle	GLE 580 4-matic	SUV	Allrad	Benzin/Elektro	Aug 2023	-	155913
Mercedes-benz	Glk-Klasse	200	SUV	Heckantrieb	Benzin	Aug 2013	Jun 2015	53273
Mercedes-benz	Glk-Klasse	250	SUV	Heckantrieb	Benzin	Aug 2013	Jun 2015	53271
Mercedes-benz	Glk-Klasse	350	SUV	Heckantrieb	Benzin	Apr 2009	Jun 2015	11389
Mercedes-benz	Glk-Klasse	200 CDI	SUV	Heckantrieb	Diesel	Jul 2010	Jun 2015	34997
Mercedes-benz	Glk-Klasse	200 CDI	SUV	Heckantrieb	Diesel	Dec 2013	Jun 2015	100917
Mercedes-benz	Glk-Klasse	220 CDI	SUV	Heckantrieb	Diesel	Dec 2008	Jun 2015	34995
Mercedes-benz	Glk-Klasse	220 CDI 4-matic	SUV	Allrad	Diesel	Dec 2008	Jun 2015	34996
Mercedes-benz	Glk-Klasse	300 4-matic	SUV	Allrad	Benzin	Sep 2009	Jun 2015	116216
Mercedes-benz	Glk-Klasse	350 4-matic	SUV	Allrad	Benzin	Jun 2008	Jun 2015	11391
Mercedes-benz	Glk-Klasse	350 CDI 4-matic	SUV	Allrad	Diesel	Feb 2010	Jun 2015	11392
Mercedes-benz	Glk-Klasse	350 CDI 4-matic	SUV	Allrad	Diesel	Jul 2012	Jun 2015	55378
Mercedes-benz	Gl-Klasse	GL 350 CDI / Bluetec 4-matic	SUV	Allrad	Diesel	Jul 2012	Oct 2015	58741
Mercedes-benz	Gl-Klasse	GL 350 CDI 4-matic	SUV	Allrad	Diesel	Oct 2010	Aug 2012	12338
Mercedes-benz	Gl-Klasse	GL 400 4-matic	SUV	Allrad	Benzin	Aug 2013	Oct 2015	53272
Mercedes-benz	Gl-Klasse	GL 500 4-matic	SUV	Allrad	Benzin	Jul 2012	Oct 2015	58742
Mercedes-benz	Gl-Klasse	GL 63 AMG 4-matic	SUV	Allrad	Benzin	Jul 2012	Oct 2015	58743
Mercedes-benz	Gl-Klasse	GL 63 AMG 4-matic	SUV	Allrad	Benzin	Jul 2012	Oct 2015	125940
Mercedes-benz	Gls	350 D 4-matic	SUV	Allrad	Diesel	Nov 2015	Apr 2019	117400
Mercedes-benz	Gls	350 D Mild Hybrid 4-matic	SUV	Allrad	Diesel/Elektro	May 2023	-	154489
Mercedes-benz	Gls	400 4-matic	SUV	Allrad	Benzin	Nov 2015	Apr 2019	117401
Mercedes-benz	Gls	450 D Mild-hybrid 4-matic	SUV	Allrad	Diesel/Elektro	Apr 2023	-	154533
Mercedes-benz	Gls	450 Mild Hybrid 4-matic	SUV	Allrad	Benzin/Elektro	Apr 2023	-	154534
Mercedes-benz	Gls	500 4-matic	SUV	Allrad	Benzin	Nov 2015	Apr 2019	117402
Mercedes-benz	Gls	580 4-matic	SUV	Allrad	Benzin/Elektro	Aug 2023	-	156034
Mercedes-benz	Gls	AMG 63 4-matic	SUV	Allrad	Benzin	Nov 2015	Apr 2019	117404
Mercedes-benz	Gullwing	300 SL	Coupe	Heckantrieb	Benzin	Sep 1954	May 1957	14977
Mercedes-benz	Heckflosse	300 SE	Stufenheck	Heckantrieb	Benzin	Feb 1961	Feb 1964	11713
Mercedes-benz	Heckflosse	300 SE	Stufenheck	Heckantrieb	Benzin	Feb 1964	Jul 1965	11714
Mercedes-benz	Marco polo camper	300 CDI	Bus	Heckantrieb	Diesel	Jan 2021	-	143280
Mercedes-benz	Marco polo camper	300 CDI 4-matic	Bus	Allrad	Diesel	Jan 2021	-	143281
Mercedes-benz	Mb	D	Kasten	Frontantrieb	Diesel	Feb 1988	May 1992	8757
Mercedes-benz	Mb	D	Kasten	Frontantrieb	Diesel	Dec 1990	Feb 1996	8797
Mercedes-benz	M-Klasse	ML 250 CDI / Bluetec 4-matic	SUV	Allrad	Diesel	Jun 2011	Dec 2015	12309
Mercedes-benz	M-Klasse	ML 270 CDI	SUV	Allrad	Diesel	Dec 1999	Jun 2005	13163
Mercedes-benz	M-Klasse	ML 280 CDI 4-matic	SUV	Allrad	Diesel	Jul 2005	Jul 2009	18593
Mercedes-benz	M-Klasse	ML 300 4-matic	SUV	Allrad	Benzin	Aug 2012	Feb 2015	105764
Mercedes-benz	M-Klasse	ML 320 CDI 4-matic	SUV	Allrad	Diesel	Jul 2005	Jul 2009	18594
Mercedes-benz	M-Klasse	ML 320 CDI 4-matic	SUV	Allrad	Diesel	Jul 2005	Jul 2011	128534
Mercedes-benz	M-Klasse	ML 350	SUV	Allrad	Benzin	Aug 2002	Jun 2005	17108
Mercedes-benz	M-Klasse	ML 350	SUV	Allrad	Benzin	Feb 2003	Jun 2005	17274
Mercedes-benz	M-Klasse	ML 350 4-matic	SUV	Allrad	Benzin	Jun 2011	Dec 2015	12311
Mercedes-benz	M-Klasse	ML 350 4-matic	SUV	Allrad	Benzin	Feb 2005	Dec 2011	18591
Mercedes-benz	M-Klasse	ML 350 Bluetec 4-matic	SUV	Allrad	Diesel	Jun 2011	Feb 2015	12310
Mercedes-benz	M-Klasse	ML 400 4-matic	SUV	Allrad	Benzin	Aug 2013	Feb 2015	53264
Mercedes-benz	M-Klasse	ML 400 CDI	SUV	Allrad	Diesel	Sep 2001	Jun 2005	16149
Mercedes-benz	M-Klasse	ML 430	SUV	Allrad	Benzin	Feb 1998	Jun 2005	10504
Mercedes-benz	M-Klasse	ML 500	SUV	Allrad	Benzin	Sep 2001	Jun 2005	16150
Mercedes-benz	M-Klasse	ML 500 4-matic	SUV	Allrad	Benzin	Jul 2005	Dec 2011	18592
Mercedes-benz	M-Klasse	ML 55 AMG	SUV	Allrad	Benzin	Feb 2000	Jun 2005	13164
Mercedes-benz	M-Klasse	ML 63 AMG 4-matic	SUV	Allrad	Benzin	Nov 2011	Feb 2015	17011
Mercedes-benz	M-Klasse	ML 63 AMG 4-matic	SUV	Allrad	Benzin	Nov 2011	Feb 2015	18370
Mercedes-benz	Ponton	219	Stufenheck	Heckantrieb	Benzin	Mar 1956	Jul 1957	107655
Mercedes-benz	Ponton	219	Stufenheck	Heckantrieb	Benzin	Aug 1957	Jul 1959	107656
Mercedes-benz	Pullmann	600	Stufenheck	Heckantrieb	Benzin	Sep 1964	Jan 1979	11122
Mercedes-benz	R-Klasse	R 320 CDI 4-matic	Großraumlimousine	Allrad	Diesel	Jan 2006	Jul 2010	19056
Mercedes-benz	R-Klasse	R 320 CDI 4-matic	Großraumlimousine	Allrad	Diesel	Jan 2006	Dec 2012	55884
Mercedes-benz	R-Klasse	R 350 4-matic	Großraumlimousine	Allrad	Benzin	Jul 2005	Dec 2012	19054
Mercedes-benz	R-Klasse	R 500 4-matic	Großraumlimousine	Allrad	Benzin	Aug 2005	Dec 2014	19055
Mercedes-benz	S-Klasse	280 S	Stufenheck	Heckantrieb	Benzin	Sep 1972	Jul 1980	45694
Mercedes-benz	S-Klasse	280 SE, SEL	Stufenheck	Heckantrieb	Benzin	Aug 1972	Jan 1976	151673
Mercedes-benz	S-Klasse	300 SDL	Stufenheck	Heckantrieb	Diesel	Sep 1985	Dec 1986	116790
Mercedes-benz	S-Klasse	420 SEC	Coupe	Heckantrieb	Benzin	Sep 1986	Jun 1991	125937
Mercedes-benz	S-Klasse	500 SEC	Coupe	Heckantrieb	Benzin	Aug 1980	Aug 1985	57285
Mercedes-benz	S-Klasse	AMG S 63	Cabriolet	Heckantrieb	Benzin	Feb 2016	Oct 2017	119796
Mercedes-benz	S-Klasse	AMG S 63 4-matic	Cabriolet	Allrad	Benzin	Dec 2015	Oct 2017	117886
Mercedes-benz	S-Klasse	AMG S 63 4-matic+	Stufenheck	Allrad	Benzin	May 2017	Jul 2020	127331
Mercedes-benz	S-Klasse	AMG S 65	Cabriolet	Heckantrieb	Benzin	Apr 2016	May 2019	119042
Mercedes-benz	S-Klasse	CL 500	Coupe	Heckantrieb	Benzin	Mar 1999	Mar 2006	11459
Mercedes-benz	S-Klasse	CL 55 AMG	Coupe	Heckantrieb	Benzin	Oct 1999	Mar 2006	14596
Mercedes-benz	S-Klasse	CL 55 AMG Kompressor	Coupe	Heckantrieb	Benzin	Jun 2002	Mar 2006	16977
Mercedes-benz	S-Klasse	CL 600	Coupe	Heckantrieb	Benzin	Mar 1999	Mar 2006	11460
Mercedes-benz	S-Klasse	CL 600	Coupe	Heckantrieb	Benzin	Sep 2002	Mar 2006	16961
Mercedes-benz	S-Klasse	CL 63 AMG	Coupe	Heckantrieb	Benzin	Jan 2010	Dec 2013	14919
Mercedes-benz	S-Klasse	CL 65 AMG	Coupe	Heckantrieb	Benzin	Sep 2003	Mar 2006	17390
Mercedes-benz	S-Klasse	S 280	Stufenheck	Heckantrieb	Benzin	Oct 1998	Aug 2005	10302
Mercedes-benz	S-Klasse	S 280	Stufenheck	Heckantrieb	Benzin	Aug 2006	Dec 2013	56741
Mercedes-benz	S-Klasse	S 300	Stufenheck	Heckantrieb	Benzin	Aug 2006	Dec 2013	56742
Mercedes-benz	S-Klasse	S 300 Bluetec Hybrid / H	Stufenheck	Heckantrieb	Diesel/Elektro	Feb 2014	May 2017	100753
Mercedes-benz	S-Klasse	S 320	Stufenheck	Heckantrieb	Benzin	May 2014	Jul 2020	106363
Mercedes-benz	S-Klasse	S 320 CDI	Stufenheck	Heckantrieb	Diesel	Aug 1999	Sep 2002	14578
Mercedes-benz	S-Klasse	S 320 CDI	Stufenheck	Heckantrieb	Diesel	Sep 2002	Aug 2005	17047
Mercedes-benz	S-Klasse	S 320 CDI	Stufenheck	Heckantrieb	Diesel	Oct 2005	Dec 2013	54953
Mercedes-benz	S-Klasse	S 320 CDI 4-matic	Stufenheck	Allrad	Diesel	Oct 2005	Dec 2013	56750
Mercedes-benz	S-Klasse	S 350	Stufenheck	Heckantrieb	Benzin	Oct 2005	Dec 2013	18960
Mercedes-benz	S-Klasse	S 350 4-matic	Stufenheck	Allrad	Benzin	Jun 2003	Aug 2005	17470
Mercedes-benz	S-Klasse	S 350 Bluetec / D	Stufenheck	Heckantrieb	Diesel	May 2013	May 2017	59008
Mercedes-benz	S-Klasse	S 350 Bluetec / D 4-matic	Stufenheck	Allrad	Diesel	Feb 2014	May 2017	100754
Mercedes-benz	S-Klasse	S 350 Bluetec 4-matic	Stufenheck	Allrad	Diesel	Feb 2014	May 2017	100762
Mercedes-benz	S-Klasse	S 350 CDI	Stufenheck	Heckantrieb	Diesel	Jun 2009	Dec 2013	14029
Mercedes-benz	S-Klasse	S 350 CDI	Stufenheck	Heckantrieb	Diesel	Jun 2009	Dec 2013	56156
Mercedes-benz	S-Klasse	S 350 CDI 4-matic	Stufenheck	Allrad	Diesel	Jan 2009	Dec 2010	123503
Mercedes-benz	S-Klasse	S 350 D	Stufenheck	Heckantrieb	Diesel	Jul 2017	Jul 2020	128017
Mercedes-benz	S-Klasse	S 350 D	Stufenheck	Heckantrieb	Diesel	Sep 2020	-	143387
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	May 2017	Jul 2020	127328
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	Sep 2020	-	143388
Mercedes-benz	S-Klasse	S 350 D Mild Hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	Jun 2023	-	154545
Mercedes-benz	S-Klasse	S 350 D Mild Hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	May 2023	-	154546
Mercedes-benz	S-Klasse	S 350 D Mild Hybrid 4-matic	Stufenheck	Allrad	Diesel/Elektro	Jun 2023	-	154548
Mercedes-benz	S-Klasse	S 350 D Mild Hybrid 4-matic	Stufenheck	Allrad	Diesel/Elektro	May 2023	-	154549


--- Round 1 / 首次发送 ---
## 更新点

* 新建 GLE II V167 2023 facelift 常规 SUV 尺寸组。其三维为 `4924×1947×1797 mm`，与累计索引中高度为 `1772 mm` 的既有组不一致，因此未覆盖或复用原组。([德国汽车俱乐部][1])
* 闭合 GLK I X204 facelift 常规车身，统一关联 `4536×1840×1669 mm` 尺寸组；跨越改款日期的 GLK Ktype 暂未落盘。([汽车目录][2])
* 闭合 GL II X166 常规车身与 AMG 63 宽体车身；AMG 63 因保险杠和宽体外廓不同独立建组。([德国汽车俱乐部][3])
* 闭合 GLS I X166 常规车身、AMG 63 宽体车身，以及 GLS II X167 2023 facelift 常规车身。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：18
* PENDING Ktype：82
* 本轮首次确认尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
155913	155913	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-FACELIFT-01	HIGH	V167 2023 facelift常规SUV外廓。	READY
53273	53273	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
53271	53271	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
100917	100917	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
55378	55378	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
58741	58741	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
53272	53272	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
58742	58742	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
58743	58743	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	HIGH	X166 AMG 63宽体外廓。	READY
125940	125940	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	HIGH	X166 AMG 63宽体外廓。	READY
117400	117400	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
154489	154489	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117401	117401	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
154533	154533	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
154534	154534	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117402	117402	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
156034	156034	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117404	117404	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-AMG63-SUV-01	HIGH	X166 facelift AMG 63宽体外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-II-V167-SUV-FACELIFT-01	4924	1947	1797	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gle/167-facelift/329234/
EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	4536	1840	1669	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1782125/mercedes-benz_glk_200_cdi_blueefficiency.html
EU-MERCEDES-BENZ-GL-II-X166-SUV-01	5120	1934	1850	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gl-klasse/166/233384/
EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	5146	1982	1850	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1782095/mercedes-benz_gl_63_amg_4matic.html
EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	5130	1934	1850	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gls-x166-generation-4650
EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	5209	1956	1823	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gls/167-facelift/328135/
EU-MERCEDES-BENZ-GLS-I-X166-AMG63-SUV-01	5162	1982	1850	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2230910/mercedes-amg_gls_63_4matic_coupe.html
```

## 下一步优先处理

1. 闭合 GLK X204 pre-facelift，并拆分生产区间横跨 2012 facelift 的 Ktype。
2. 处理 GL X164、M-Class W163/W164/W166，优先批量复用同代常规与 AMG 尺寸组。
3. 随后处理 R-Class、S-Class及历史车型的轴距、车身形式和改款分支。

推进信号：CONTINUE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gle/167-facelift/329234/?utm_source=chatgpt.com "Mercedes-Benz GLE 580 Advanced Plus 4MATIC 9G-TRONIC (08/23 - 02/24): Technische Daten, Bilder, Preise | ADAC"
[2]: https://www.automobile-catalog.com/car/2013/1782125/mercedes-benz_glk_200_cdi_blueefficiency.html?utm_source=chatgpt.com "2013 Mercedes-Benz GLK 200 CDI Specs Review (105 kW ..."
[3]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gl-klasse/166/233384/?utm_source=chatgpt.com "Mercedes-Benz GL 350 CDI BlueTEC 4MATIC 7G-TRONIC PLUS (07/12 - 11/15): Technische Daten, Bilder, Preise | ADAC"
[4]: https://www.auto-data.net/en/mercedes-benz-gls-x166-generation-4650?utm_source=chatgpt.com "Mercedes-Benz GLS (X166) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 GLK X204 改款前后分支、GL X164 facelift，以及 M-Class W164 改款前后和 W166 常规/AMG 63 外廓。
* 本轮覆盖 20 个原 PENDING Ktype，新增 32 条 READY 映射；其中跨 2008 年 W164 facelift 或 2012 年 X204 facelift 的 Ktype 均拆成稳定派生行。
* 首次创建 6 个尺寸组；已闭合的 GLK facelift 组直接复用，不重复输出。GLK、GL 和 M-Class 的代际、改款边界及三维由 Mercedes-Benz 历史资料和规格页交叉闭合。([marsClassic][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：38
* READY 映射行：50
* PENDING Ktype：62
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11389_prefl	11389	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11389_facelift	11389	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
34997_prefl	34997	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34997_facelift	34997	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
34995_prefl	34995	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34995_facelift	34995	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
34996_prefl	34996	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34996_facelift	34996	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
116216_prefl	116216	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
116216_facelift	116216	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
11391_prefl	11391	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11391_facelift	11391	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
11392_prefl	11392	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11392_facelift	11392	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
12338	12338	SUV	GL I	X164	5	EU-MERCEDES-BENZ-GL-I-X164-SUV-FACELIFT-01	HIGH	X164 facelift常规SUV外廓。	READY
12309	12309	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18593_prefl	18593	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18593_facelift	18593	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
105764	105764	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18594_prefl	18594	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18594_facelift	18594	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
128534_prefl	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
128534_facelift	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
12311	12311	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18591_prefl	18591	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18591_facelift	18591	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
12310	12310	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
53264	53264	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18592_prefl	18592	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18592_facelift	18592	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
17011	17011	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	HIGH	W166 AMG 63宽体外廓。	READY
18370	18370	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	HIGH	W166 AMG 63宽体外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	4525	1840	1689	Mercedes-Benz Public Archive; Automoli	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GLK-350-CDI-4MATIC-2010---2012.xhtml?oid=189873149;https://www.automoli.com/gb/vehicles/mercedes-benz/glk/glk-x204-2744/
EU-MERCEDES-BENZ-GL-I-X164-SUV-FACELIFT-01	5099	1920	1840	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GL-350-CDI-4MATIC-BlueEFFICIENCY-2010---2012.xhtml?oid=191486615
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	4780	1911	1815	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-4MATIC-2005---2008.xhtml?oid=191401379
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	4781	1911	1815	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-4MATIC-2008---2011.xhtml?oid=191414618
EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	4804	1926	1796	Mercedes-Benz Public Archive; EncyCARpedia	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-BlueTEC-4MATIC-2011---2015.xhtml?oid=192703094;https://www.encycarpedia.com/mercedes/11-ml-350-bluetec-4matic-suv
EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	4817	1940	1762	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/ML-63-AMG-2012---2015-ab-ca-052013-ML-63-AMG-4MATIC.xhtml?oid=192703101
```

## 下一步优先处理

1. 闭合 M-Class W163 改款前、改款后及 ML 55 AMG 独立外廓。
2. 处理 R-Class W251/V251 的短轴与长轴分支。
3. 随后处理 Gullwing、Heckflosse、Ponton、Pullman 和 S-Class 历史车身。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GLK-350-CDI-4MATIC-2010---2012.xhtml?oid=189873149&utm_source=chatgpt.com "GLK 350 CDI 4MATIC, 2010 - 2012"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 M-Class I W163 的改款前常规车身、改款后常规车身及 ML 430 改款前外廓。([marsClassic][1])
* 完成 6 个 Ktype，新增 7 条 READY 映射；跨 2001 年改款的 ML 270 CDI 拆分为 `prefl` 与 `facelift`。
* ML 55 AMG 的最大车宽来源仍存在实质冲突，本轮未创建尺寸组或输出猜测性映射。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：44
* READY 映射行：57
* PENDING Ktype：56
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13163_prefl	13163	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-PREFL-01	HIGH	跨2001改款拆分；改款前常规外廓。	READY
13163_facelift	13163	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	跨2001改款拆分；改款后常规外廓。	READY
17108	17108	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
17274	17274	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
16149	16149	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
10504	10504	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML430-SUV-PREFL-01	HIGH	ML 430改款前外廓。	READY
16150	16150	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-PREFL-01	4587	1833	1820	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-270-CDI.xhtml?oid=4810
EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	4638	1840	1820	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-270-CDI.xhtml?oid=4814
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML430-SUV-PREFL-01	4587	1833	1802	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-430.xhtml?oid=4809
```

## 下一步优先处理

1. 解决 ML 55 AMG 不含后视镜最大车宽冲突，闭合改款前后 AMG 外廓。
2. 处理 R-Class W251/V251 的短轴、长轴及 2010 facelift 分支。
3. 批量处理 Gullwing、Heckflosse、Ponton、Pullman 等历史车型。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-270-CDI.xhtml?oid=4810 "ML 270 CDI"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 ML 55 AMG W163 改款前后外廓；改款后车宽由 `1833 mm` 变为 `1840 mm`，因此拆分两个尺寸组。([marsClassic][1])
* 闭合 300 SL W198、Heckflosse 300 SE W112，以及 Ponton 219 W105 的 1957 年前后长度分支。([marsClassic][2])
* 闭合 S-Class W116 短轴/长轴、W126 300 SDL 长轴，以及 C126 500 SEC 改款前和 420 SEC 改款后车身。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：55
* READY 映射行：70
* PENDING Ktype：45
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13164_prefl	13164	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-PREFL-01	HIGH	跨2001改款拆分；改款前AMG外廓。	READY
13164_facelift	13164	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-FACELIFT-01	HIGH	跨2001改款拆分；改款后AMG外廓。	READY
14977	14977	Coupe	300 SL W198	W198	2	EU-MERCEDES-BENZ-300-SL-W198-COUPE-01	HIGH	W198 Gullwing双门车身。	READY
11713	11713	Sedan	Heckflosse 300 SE	W112	4	EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	HIGH	W112标准轴距四门车身。	READY
11714	11714	Sedan	Heckflosse 300 SE	W112	4	EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	HIGH	W112标准轴距四门车身。	READY
107655	107655	Sedan	Ponton 219	W105	4	EU-MERCEDES-BENZ-PONTON-W105-SEDAN-PREFL-01	HIGH	1957年8月外观调整前车身。	READY
107656	107656	Sedan	Ponton 219	W105	4	EU-MERCEDES-BENZ-PONTON-W105-SEDAN-FACELIFT-01	HIGH	1957年8月外观调整后车身。	READY
45694	45694	Sedan	S-Class W116	W116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	HIGH	W116标准轴距四门车身。	READY
151673_se	151673	Sedan	S-Class W116	W116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	HIGH	输入同时覆盖280 SE与280 SEL；标准轴距分支。	READY
151673_sel	151673	Sedan	S-Class W116	V116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-LWB-01	HIGH	输入同时覆盖280 SE与280 SEL；长轴距分支。	READY
116790	116790	Sedan	S-Class W126	V126	4	EU-MERCEDES-BENZ-S-CLASS-W126-SEDAN-LWB-01	HIGH	北美300 SDL长轴距车身。	READY
125937	125937	Coupe	S-Class Coupe C126	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	HIGH	C126 1985改款后双门车身。	READY
57285	57285	Coupe	S-Class Coupe C126	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-PREFL-01	HIGH	C126 1985改款前双门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-PREFL-01	4635	1833	1804	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-55-AMG.xhtml?oid=4812
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-FACELIFT-01	4635	1840	1804	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-55-AMG.xhtml?oid=4818
EU-MERCEDES-BENZ-300-SL-W198-COUPE-01	4520	1790	1300	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SL.xhtml?oid=4699
EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	4875	1795	1455	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SE.xhtml?oid=4893
EU-MERCEDES-BENZ-PONTON-W105-SEDAN-PREFL-01	4650	1740	1560	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/219.xhtml?oid=4883
EU-MERCEDES-BENZ-PONTON-W105-SEDAN-FACELIFT-01	4680	1740	1560	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/219.xhtml?oid=4883
EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	4960	1870	1425	Mercedes-Benz Public Archive 280 S; Mercedes-Benz Public Archive 280 SE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-S--W-116-V-28-1972---1980.xhtml?oid=4869;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SE.xhtml?oid=4863
EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-LWB-01	5060	1870	1430	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SEL.xhtml?oid=4868
EU-MERCEDES-BENZ-S-CLASS-W126-SEDAN-LWB-01	5285	1820	1441	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SDL-Turbodiesel.xhtml?oid=4991
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	4935	1828	1407	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/420-SEC.xhtml?oid=4550
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-PREFL-01	4910	1828	1406	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEC.xhtml?oid=4545
```

## 下一步优先处理

1. 闭合 R-Class W251/V251 的短轴、长轴及 2010 facelift 分支。
2. 处理 Marco Polo W447 与 MB 100/MB D 厢式车。
3. 批量闭合 C215、C216、W220 与 W221 S-Class 车型簇。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-55-AMG.xhtml?oid=4812 "ML 55 AMG"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SL.xhtml?oid=4699 "300 SL"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-S--W-116-V-28-1972---1980.xhtml?ls=L2VuL2luc3RhbmNlL2tvLzMwMC1ELnhodG1sP29pZD01MDk1JnJlbElkPTEwMDEmcmVzdWx0SW5mb1R5cGVJZD0xNzUmZnJvbU9pZD01MDk1JmZyb21JbmZvVHlwZUlkPTIxNTU%21&oid=4869&rs=7&utm_source=chatgpt.com "280 S"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 S-Class C215 Coupe 车型簇；CL 500、CL 55 AMG、CL 55 AMG Kompressor、CL 600 与 CL 65 AMG 均复用 `4993×1857×1398 mm` 尺寸组。([marsClassic][1])
* 闭合 S-Class W220 短轴轿车的改款前、改款后及 facelift 4MATIC 高度分支：改款前为 `5038×1855×1444 mm`，改款后后驱为 `5043×1855×1444 mm`，改款后 4MATIC 为 `5043×1855×1449 mm`。([marsClassic][2])
* Ktype `10302` 的生产区间跨越 2002 年改款，拆分为 `prefl` 与 `facelift` 两条映射。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* READY 映射行：81
* PENDING Ktype：35
* 已确认尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11459	11459	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门车身；动力及改款版本三维外廓一致。	READY
14596	14596	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门AMG车身；三维外廓与标准C215一致。	READY
16977	16977	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门Kompressor AMG车身。	READY
11460	11460	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门V12车身。	READY
16961	16961	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215改款后双门V12车身。	READY
17390	17390	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215 CL 65 AMG双门车身。	READY
10302_prefl	10302	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	HIGH	输入区间跨2002改款；改款前短轴车身。	READY
10302_facelift	10302	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	HIGH	输入区间跨2002改款；改款后短轴车身。	READY
14578	14578	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	HIGH	W220改款前短轴车身。	READY
17047	17047	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	HIGH	W220改款后短轴车身。	READY
17470	17470	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	W220改款后4MATIC高度分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	4993	1857	1398	Mercedes-Benz Public Archive CL 500; Mercedes-Benz Public Archive CL 55 AMG; Mercedes-Benz Public Archive CL 65 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-500.xhtml?oid=4509;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-55-AMG.xhtml?oid=4511;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-65-AMG.xhtml?oid=2461783
EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	5038	1855	1444	Mercedes-Benz Public Archive S 320 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI.xhtml?oid=4960
EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	5043	1855	1444	Mercedes-Benz Public Archive S 320 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI--W-220-DE-32-LA-2002---2005.xhtml?oid=2461742
EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	5043	1855	1449	Mercedes-Benz Public Archive S 350 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-4MATIC.xhtml?oid=2461750
```

## 下一步优先处理

1. 闭合 W221 改款前、改款后及短轴/长轴分支。
2. 处理 C216 CL 63 AMG 和 W222/V222 S-Class 车型簇。
3. 随后处理 R-Class 的 SWB/LWB、2007 小改款及 2010 facelift 分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-500.xhtml?oid=4509 "CL 500"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI.xhtml?oid=4960 "S 320 CDI"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 S-Class W221/V221 改款前后四种稳定外廓：短轴改款前、长轴改款前、短轴 facelift、长轴 facelift。改款前短轴/长轴分别为 `5076/5206×1871×1473 mm`；facelift 后车长分别增至 `5096/5226 mm`，高度为 `1479 mm`。([marsClassic][1])
* 完成 8 个 Ktype，新增 14 条 READY 映射；跨 2009 年 facelift 的生产区间均拆分为 `prefl` 与 `facelift`。
* S 280/S 300 按官方记录限定为 V221 长轴车身；其余未标注长轴的本批版本关联 W221 短轴车身。([marsClassic][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：73
* READY 映射行：95
* PENDING Ktype：27
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56741_prefl	56741	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56741_facelift	56741	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56742_prefl	56742	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56742_facelift	56742	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
54953_prefl	54953	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
54953_facelift	54953	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
56750_prefl	56750	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴4MATIC；跨2009 facelift拆分。	READY
56750_facelift	56750	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴4MATIC；跨2009 facelift拆分。	READY
18960_prefl	18960	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
18960_facelift	18960	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
14029	14029	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	W221 facelift短轴车身。	READY
56156	56156	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	W221 facelift短轴车身。	READY
123503_prefl	123503	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴4MATIC；生产区间跨2009 facelift。	READY
123503_facelift	123503	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴4MATIC；生产区间跨2009 facelift。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	5206	1871	1473	Mercedes-Benz Public Archive S 320 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI-long-wheelbase-2006---2009-from-122008-S-320-CDI-BlueEFFICIENCY-long-wheelbase.xhtml?oid=191730141
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Mercedes-Benz Public Archive 221 series facelift; AutoData1 S-Class Long W221 facelift	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889;https://www.autodata1.com/en/car/mercedes-benz/s-class/s-class-long-w221-facelift-2009-s-450-v8-340-hp-4matic-g-tronic
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	5076	1871	1473	Mercedes-Benz Public Archive S 420 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-420-CDI-2006---2009.xhtml?oid=191730146
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Mercedes-Benz Public Archive S 350 CDI BlueEFFICIENCY	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-CDI-BlueEFFICIENCY-2009---2010.xhtml?oid=191730295
```

## 下一步优先处理

1. 闭合 C216 CL 63 AMG 改款前后高度冲突。
2. 批量处理 W222/V222 的短轴、长轴、4MATIC、AMG 与 2017 facelift 分支。
3. 处理 W223/V223 Mild Hybrid 车型以及 A217 S 63/S 65 Cabriolet。
4. 最后处理 R-Class、Marco Polo、MB 厢式车和 Pullman 600。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-420-CDI-2006---2009.xhtml?oid=191730146&utm_source=chatgpt.com "S 420 CDI, 2006 - 2009"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2005---2009.xhtml?oid=453322&utm_source=chatgpt.com "221 series S-Class Saloons, 2005 - 2009"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 R-Class I 的 W251 短轴、V251 长轴、2007 外观更新及 2010 facelift 分支；Ktype `19056`、`19054` 明确同时覆盖 W251/V251，Ktype `19055` 对应 251.075/251.175 两种轴距。([AUTODOC][1])
* 闭合 C216 facelift CL 63 AMG，三维为 `5106×1871×1425 mm`。([marsClassic][2])
* 闭合 W100 600 Pullman 四门、六门映射；两种车门结构复用相同 `6240×1950×1500 mm` 外廓尺寸组。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* READY 映射行：110
* PENDING Ktype：22
* 已确认尺寸组：43
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11122_4dr	11122	Sedan	600 Pullman W100	W100	4	EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	HIGH	W100 Pullman四门豪华轿车分支。	READY
11122_6dr	11122	Sedan	600 Pullman W100	W100	6	EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	HIGH	W100 Pullman六门豪华轿车分支。	READY
19056_swb_pre07	19056	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	W251短轴；2007年外观更新前。	READY
19056_swb_07	19056	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	HIGH	W251短轴；2007年外观更新后。	READY
19056_lwb_pre07	19056	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	V251长轴；2007年外观更新前。	READY
19056_lwb_07	19056	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	V251长轴；2007年外观更新后。	READY
19054_swb_pre07	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	W251短轴；2007年外观更新前。	READY
19054_swb_07	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	HIGH	W251短轴；2007年外观更新后。	READY
19054_swb_facelift10	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-FACELIFT-2010-01	HIGH	W251短轴；2010 facelift外廓。	READY
19054_lwb_pre07	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	V251长轴；2007年外观更新前。	READY
19054_lwb_07	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	V251长轴；2007年外观更新后。	READY
19054_lwb_facelift10	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	HIGH	V251长轴；2010 facelift外廓。	READY
19055_swb	19055	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	251.075短轴R 500车身。	READY
19055_lwb	19055	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	251.175长轴R 500车身。	READY
14919	14919	Coupe	S-Class Coupe C216	C216	2	EU-MERCEDES-BENZ-S-CLASS-C216-COUPE-FACELIFT-01	HIGH	C216 2010 facelift CL 63 AMG双门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	6240	1950	1500	Mercedes-Benz Public Archive 600 Pullman four-door; Mercedes-Benz Public Archive 600 Pullman six-door	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-Pullman-limousine-4-doors.xhtml?oid=5058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-Pullman-limousine-6-doors.xhtml?oid=5060
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	4922	1922	1659	Automobile-Catalog 2006 Mercedes-Benz R 320 CDI 4MATIC	https://www.automobile-catalog.com/car/2006/1558580/mercedes-benz_r_320_cdi_4matic__dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	4938	1922	1661	Automobile-Catalog 2007 Mercedes-Benz R 320 CDI 4MATIC	https://www.automobile-catalog.com/car/2007/1558685/mercedes-benz_r_320_cdi_4matic__dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	5157	1922	1661	Automobile-Catalog 2006 Mercedes-Benz R 320 CDI 4MATIC LWB	https://www.automobile-catalog.com/car/2006/1558535/mercedes-benz_r_320_cdi_4matic_lwb_dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	5173	1922	1663	Automobile-Catalog 2007 Mercedes-Benz R 320 CDI 4MATIC LWB	https://www.automobile-catalog.com/car/2007/1558745/mercedes-benz_r_320_cdi_4matic_lwb_dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-FACELIFT-2010-01	4922	1922	1676	Automobile-Catalog 2011 Mercedes-Benz R 350 4MATIC	https://www.automobile-catalog.com/car/2011/1559255/mercedes-benz_r_350_4matic.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	5157	1922	1677	Automobile-Catalog 2011 Mercedes-Benz R 350 4MATIC LWB	https://www.automobile-catalog.com/car/2011/1559270/mercedes-benz_r_350_4matic_lwb.html
EU-MERCEDES-BENZ-S-CLASS-C216-COUPE-FACELIFT-01	5106	1871	1425	Mercedes-Benz Public Archive CL 63 AMG 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-63-AMG-2010---2014.xhtml?oid=191251467
```

## 下一步优先处理

1. 闭合 A217 S 63/S 65 Cabriolet 的改款前后分支。
2. 批量处理 W222/V222 的常规、4MATIC、AMG 和 2017 facelift 外廓。
3. 处理 W223/V223 的短轴、长轴及 2023 Mild Hybrid 重复 Ktype。
4. 最后处理 Marco Polo W447、MB 厢式车和 R 320 BlueTEC 251.125 市场分支。

推进信号：CONTINUE

[1]: https://www.autodoc.fi/autonosat/aanitorvi-10420/mercedes-benz/r-klasse/r-sarja-w251-v251/19056-r-320-cdi-4-matic-251-022-251-122?utm_source=chatgpt.com "Mercedes W251 R 320 CDI 3.0 4-matic Äänitorvi"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-63-AMG-2010---2014.xhtml?oid=191251467 "CL 63 AMG, 2010 - 2014"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-Pullman-limousine-6-doors.xhtml?oid=5060 "600 Pullman limousine (6 doors)"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 W222/V222 改款前常规短轴、长轴车身，以及 2017 facelift 后常规短轴、长轴车身；覆盖 S 300 BlueTEC Hybrid、S 320、S 350 BlueTEC/d 与 4MATIC 版本。Ktype 对应的底盘范围已确认包含 W222/V222 双轴距或指定单一长轴分支。([Cromax][1])
* 闭合 V222 facelift AMG S 63 4MATIC+ 长轴宽体外廓，以及 W223/V223 短轴、长轴常规外廓。W223/V223 的驱动方式和 2023 Mild Hybrid 更新不改变相应轴距车身尺寸。([汽车数据网][2])
* 本轮完成 14 个原 PENDING Ktype，新增 19 条 READY 映射和 7 个尺寸组。尺寸组分别按 W222/V222 轴距与改款、V222 AMG 外廓、W223/V223 轴距建立。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* READY 映射行：129
* PENDING Ktype：8
* 已确认尺寸组：50
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127331	127331	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-AMG63-SEDAN-LWB-FACELIFT-01	HIGH	V222 facelift AMG S 63长轴外廓。	READY
100753_swb	100753	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 300 BlueTEC Hybrid短轴分支。	READY
100753_lwb	100753	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 300 BlueTEC Hybrid长轴分支。	READY
106363	106363	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	222.162长轴车身。	READY
59008_swb	59008	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 350 BlueTEC短轴分支。	READY
59008_lwb	59008	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 350 BlueTEC长轴分支。	READY
100754_swb	100754	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 350 BlueTEC 4MATIC短轴分支。	READY
100754_lwb	100754	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 350 BlueTEC 4MATIC长轴分支。	READY
100762	100762	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	222.133长轴4MATIC车身。	READY
128017_swb	128017	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	HIGH	2017 facelift短轴分支。	READY
128017_lwb	128017	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	HIGH	2017 facelift长轴分支。	READY
143387	143387	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.130长轴后驱车身。	READY
127328_swb	127328	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	HIGH	2017 facelift短轴4MATIC分支。	READY
127328_lwb	127328	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	HIGH	2017 facelift长轴4MATIC分支。	READY
143388	143388	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.131长轴4MATIC车身。	READY
154545	154545	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	HIGH	223.020短轴Mild Hybrid车身。	READY
154546	154546	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.120长轴Mild Hybrid车身。	READY
154548	154548	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	HIGH	223.021短轴Mild Hybrid 4MATIC车身。	READY
154549	154549	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.121长轴Mild Hybrid 4MATIC车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W222-AMG63-SEDAN-LWB-FACELIFT-01	5287	1915	1499	Auto-Data Mercedes-Benz S-Class Long V222 AMG S 63 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-amg-s-63-v8-585hp-4matic-amg-speedshift-mct-18915
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	5116	1899	1496	Auto-Data Mercedes-Benz S-Class W222 S 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-s-class-w222-s-350-bluetec-258hp-7g-tronic-18881
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	5246	1899	1494	Auto-Data Mercedes-Benz S-Class Long V222 S 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-s-350-bluetec-v6-258hp-7g-tronic-plus-18920
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	5125	1899	1498	Auto-Data Mercedes-Benz S-Class W222 facelift S 350d	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-350d-286hp-g-tronic-31873
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	5255	1899	1496	Auto-Data Mercedes-Benz S-Class Long V222 facelift S 350d	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-facelift-2017-s-350d-286hp-g-tronic-31735
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	5179	1954	1503	ADAC Mercedes-Benz S 350 d W223	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/223/339761/
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	5289	1954	1503	ADAC Mercedes-Benz S 350 d lang V223	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/223/339769/
```

## 下一步优先处理

1. 闭合 A217 AMG S 63、S 63 4MATIC 与 S 65 Cabriolet 的改款前后外廓。
2. 确认 R-Class Ktype `55884` 的 251.125 单一轴距和改款边界。
3. 处理 Marco Polo W447 的后驱/4MATIC车高，以及 MB 100 D 厢式车两个 Ktype 的轴距和车顶分支。

推进信号：CONTINUE

[1]: https://cromax.hu/adatlap/2447760-mercedes-benz-s-class-2013-2018-w222-v222-x222-pollen-szuro-utaster-levego?utm_source=chatgpt.com "Mercedes-Benz S-CLASS 2013-2018 (W222, V222, X222) pollen szűrő utastér levegő"
[2]: https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-amg-s-63-v8-585hp-4matic-amg-speedshift-mct-18915?utm_source=chatgpt.com "Mercedes-Benz S-class Long (V222) AMG S 63 V8 (585 ..."
[3]: https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-s-350-bluetec-v6-258hp-4matic-7g-tronic-plus-18921?utm_source=chatgpt.com "Mercedes-Benz S-class Long (V222) S 350 BlueTEC V6 (258 Hp) 4MATIC 7G-TRONIC PLUS | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 A217 AMG Cabriolet 改款前外廓，并将跨越 2017 年 facelift 的 S 65 Ktype 拆分为改款前、改款后两条映射；改款前后车长分别为 `5044 mm` 和 `5051 mm`，车宽均为不含后视镜 `1913 mm`。([汽车目录][1])
* Ktype `55884` 已确认对应 `251.125`，按 V251 长轴车身关联三个现有缓存阶段，不重复输出既有 R-Class 尺寸组。([Alufelgen Sportfahrwerke und mehr][2])
* 闭合 Marco Polo W447 300 CDI 后驱与 4MATIC；两者外廓均为 `5140×1928×1980 mm`，复用同一尺寸组。([车辆引擎详情][3])
* MB 100 D 两个 Ktype 同时覆盖 `631.332` 短轴与 `631.342` 长轴，且生产区间跨越 1991 年前脸改款；改款前后的精确长宽高组合尚未完全闭合，本轮继续保留 PENDING。([PartSouq][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射行：138
* PENDING Ktype：2
* 已确认尺寸组：53
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119796	119796	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	A217改款前AMG Cabriolet外廓。	READY
117886	117886	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	A217改款前AMG Cabriolet 4MATIC外廓。	READY
119042_prefl	119042	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	生产区间跨2017 facelift；改款前S 65 Cabriolet。	READY
119042_facelift	119042	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-FACELIFT-01	HIGH	生产区间跨2017 facelift；改款后S 65 Cabriolet。	READY
143280	143280	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH	W447 Marco Polo后驱露营车外廓。	READY
143281	143281	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH	W447 Marco Polo 4MATIC露营车外廓。	READY
55884_lwb_pre07	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	251.125长轴；2007年外观更新前。	READY
55884_lwb_07	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	251.125长轴；2007年外观更新后。	READY
55884_lwb_facelift10	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	HIGH	251.125长轴；2010 facelift外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	5044	1913	1428	Automobile-Catalog 2016 Mercedes-Benz S 63 AMG Cabriolet; Automobile-Catalog 2016 Mercedes-Benz S 65 AMG Cabriolet	https://www.automobile-catalog.com/car/2016/2296010/mercedes-benz_s_63_amg_cabriolet.html;https://www.automobile-catalog.com/car/2016/2296040/mercedes-benz_s_65_amg_cabriolet.html
EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-FACELIFT-01	5051	1913	1428	Automobile-Catalog 2018 Mercedes-AMG S Cabriolet A217 phase II; Moniteur Automobile Mercedes-AMG S 65 Cabriolet	https://www.automobile-catalog.com/make/mercedes-amg/c-217_amg/a217_amg_2/2018.html;https://www.moniteurautomobile.be/modele-intitule-annee--mercedes--classe-s-cabriolet--2019/specifications-techniques-dimensions--59917--mercedes-classe-s-cabriolet-mercedes-amg-s-65-2p-ca-2019.html
EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	5140	1928	1980	EngineInDetail Marco Polo 300 d 2021; EngineInDetail Marco Polo 300 d 4MATIC 2021	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-9g-tronic-2021;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2021
```

## 下一步优先处理

1. 闭合 MB 100 D `631.332` 短轴与 `631.342` 长轴的改款前、改款后三维。
2. 同时处理 Ktype `8757` 与 `8797`，避免重复抓取相同 W631 物理分支。
3. 两个 Ktype 闭合后立即汇总最终完整两表并生成指定下载文件。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2016/2296040/mercedes-benz_s_65_amg_cabriolet.html?utm_source=chatgpt.com "2016 Mercedes-Benz S 65 AMG Cabriolet Specs Review (463 kW / 630 PS / 621 hp) (since mid-year 2016 for Europe )"
[2]: https://www.jms-fahrzeugteile.com/en/cat/index/sCategory/1386892?utm_source=chatgpt.com "W251, V251 | JMS Fahrzeugteile"
[3]: https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2021?utm_source=chatgpt.com "Mercedes-Benz Marco Polo 300 d 4MATIC 9G-TRONIC 2021 - Specs, Review & Tests"
[4]: https://partsouq.com/ru/catalog/genuine/vehicle?c=MB201810&cid=1379730773&cname=%D0%AD%D0%9B%D0%95%D0%9A%D0%A2%D0%A0.+%D0%9E%D0%91%D0%9E%D0%A0%D0%A3%D0%94%D0%9E%D0%92%D0%90%D0%9D%D0%98%D0%95&q=VSA63134213145473&ssd=%24%2AKwGCtqecwYKO0sbfw96M39rO7un3homEhZeEu8uTwpWKk_uWxcWWkouHhIeIgZjLgNmKgoaAh4LLyp-Ck_DKlMGSi5TiuqbNg4CFg4KAhYXd0s-HgpSbktzVltPFzYOAhYOCk5qWmoTZipOUm5Lc3ZbTxcqSnZTU3pOMltzXuJKdlMHTk4yW2sWGAAAAAKecoVA%3D%24&vid=0&utm_source=chatgpt.com "FH - Body | Mercedes-Benz MB100D Standard 3 Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10201-10300_ktype_dimension_mapping_final.tsv
- left18448_10201-10300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 MB 100 D W631 的 `631.332` 短轴与 `631.342` 长轴，并分别拆分改款前、改款后四个物理外廓；Ktype `8757`、`8797` 共用对应尺寸组。([MB100 архив][1])
* 已完成最终机械校验：两表列数正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、所有引用闭合、无孤立尺寸组、三维和来源字段完整。
* 已生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：146
* PENDING：0
* DIMENSION_GROUP：57
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
155913	155913	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-FACELIFT-01	HIGH	V167 2023 facelift常规SUV外廓。	READY
53273	53273	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
53271	53271	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
11389_prefl	11389	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11389_facelift	11389	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
34997_prefl	34997	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34997_facelift	34997	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
100917	100917	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
34995_prefl	34995	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34995_facelift	34995	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
34996_prefl	34996	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
34996_facelift	34996	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
116216_prefl	116216	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
116216_facelift	116216	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
11391_prefl	11391	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11391_facelift	11391	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
11392_prefl	11392	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	HIGH	跨2012改款拆分；改款前外廓。	READY
11392_facelift	11392	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	跨2012改款拆分；改款后外廓。	READY
55378	55378	SUV	GLK I	X204	5	EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	HIGH	X204 facelift外廓。	READY
58741	58741	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
12338	12338	SUV	GL I	X164	5	EU-MERCEDES-BENZ-GL-I-X164-SUV-FACELIFT-01	HIGH	X164 facelift常规SUV外廓。	READY
53272	53272	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
58742	58742	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-SUV-01	HIGH	X166常规车身外廓。	READY
58743	58743	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	HIGH	X166 AMG 63宽体外廓。	READY
125940	125940	SUV	GL II	X166	5	EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	HIGH	X166 AMG 63宽体外廓。	READY
117400	117400	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
154489	154489	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117401	117401	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
154533	154533	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
154534	154534	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117402	117402	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	HIGH	X166 facelift常规车身外廓。	READY
156034	156034	SUV	GLS II	X167	5	EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	HIGH	X167 2023 facelift常规SUV外廓。	READY
117404	117404	SUV	GLS I	X166	5	EU-MERCEDES-BENZ-GLS-I-X166-AMG63-SUV-01	HIGH	X166 facelift AMG 63宽体外廓。	READY
14977	14977	Coupe	300 SL W198	W198	2	EU-MERCEDES-BENZ-300-SL-W198-COUPE-01	HIGH	W198 Gullwing双门车身。	READY
11713	11713	Sedan	Heckflosse 300 SE	W112	4	EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	HIGH	W112标准轴距四门车身。	READY
11714	11714	Sedan	Heckflosse 300 SE	W112	4	EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	HIGH	W112标准轴距四门车身。	READY
143280	143280	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH	W447 Marco Polo后驱露营车外廓。	READY
143281	143281	MPV	Marco Polo W447	W447	4	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH	W447 Marco Polo 4MATIC露营车外廓。	READY
8757_swb_prefl	8757	Van	MB 100 W631	631.332	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-PREFL-01	MEDIUM	631.332短轴；前脸改款前外廓。	READY
8757_swb_facelift	8757	Van	MB 100 W631	631.332	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-FACELIFT-01	MEDIUM	631.332短轴；前脸改款后外廓。	READY
8757_lwb_prefl	8757	Van	MB 100 W631	631.342	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-PREFL-01	MEDIUM	631.342长轴；前脸改款前外廓。	READY
8757_lwb_facelift	8757	Van	MB 100 W631	631.342	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-FACELIFT-01	MEDIUM	631.342长轴；前脸改款后外廓。	READY
8797_swb_prefl	8797	Van	MB 100 W631	631.332	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-PREFL-01	MEDIUM	631.332短轴；前脸改款前外廓。	READY
8797_swb_facelift	8797	Van	MB 100 W631	631.332	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-FACELIFT-01	MEDIUM	631.332短轴；前脸改款后外廓。	READY
8797_lwb_prefl	8797	Van	MB 100 W631	631.342	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-PREFL-01	MEDIUM	631.342长轴；前脸改款前外廓。	READY
8797_lwb_facelift	8797	Van	MB 100 W631	631.342	4	EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-FACELIFT-01	MEDIUM	631.342长轴；前脸改款后外廓。	READY
12309	12309	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
13163_prefl	13163	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-PREFL-01	HIGH	跨2001改款拆分；改款前常规外廓。	READY
13163_facelift	13163	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	跨2001改款拆分；改款后常规外廓。	READY
18593_prefl	18593	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18593_facelift	18593	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
105764	105764	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18594_prefl	18594	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18594_facelift	18594	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
128534_prefl	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
128534_facelift	128534	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
17108	17108	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
17274	17274	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
12311	12311	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
18591_prefl	18591	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18591_facelift	18591	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
12310	12310	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
53264	53264	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	HIGH	W166常规SUV外廓。	READY
16149	16149	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
10504	10504	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML430-SUV-PREFL-01	HIGH	ML 430改款前外廓。	READY
16150	16150	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	HIGH	W163改款后常规外廓。	READY
18592_prefl	18592	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	HIGH	跨2008改款拆分；改款前外廓。	READY
18592_facelift	18592	SUV	M-Class II	W164	5	EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	HIGH	跨2008改款拆分；改款后外廓。	READY
13164_prefl	13164	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-PREFL-01	HIGH	跨2001改款拆分；改款前AMG外廓。	READY
13164_facelift	13164	SUV	M-Class I	W163	5	EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-FACELIFT-01	HIGH	跨2001改款拆分；改款后AMG外廓。	READY
17011	17011	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	HIGH	W166 AMG 63宽体外廓。	READY
18370	18370	SUV	M-Class III	W166	5	EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	HIGH	W166 AMG 63宽体外廓。	READY
107655	107655	Sedan	Ponton 219	W105	4	EU-MERCEDES-BENZ-PONTON-W105-SEDAN-PREFL-01	HIGH	1957年8月外观调整前车身。	READY
107656	107656	Sedan	Ponton 219	W105	4	EU-MERCEDES-BENZ-PONTON-W105-SEDAN-FACELIFT-01	HIGH	1957年8月外观调整后车身。	READY
11122_4dr	11122	Sedan	600 Pullman W100	W100	4	EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	HIGH	W100 Pullman四门豪华轿车分支。	READY
11122_6dr	11122	Sedan	600 Pullman W100	W100	6	EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	HIGH	W100 Pullman六门豪华轿车分支。	READY
19056_swb_pre07	19056	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	W251短轴；2007年外观更新前。	READY
19056_swb_07	19056	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	HIGH	W251短轴；2007年外观更新后。	READY
19056_lwb_pre07	19056	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	V251长轴；2007年外观更新前。	READY
19056_lwb_07	19056	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	V251长轴；2007年外观更新后。	READY
55884_lwb_pre07	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	251.125长轴；2007年外观更新前。	READY
55884_lwb_07	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	251.125长轴；2007年外观更新后。	READY
55884_lwb_facelift10	55884	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	HIGH	251.125长轴；2010 facelift外廓。	READY
19054_swb_pre07	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	W251短轴；2007年外观更新前。	READY
19054_swb_07	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	HIGH	W251短轴；2007年外观更新后。	READY
19054_swb_facelift10	19054	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-FACELIFT-2010-01	HIGH	W251短轴；2010 facelift外廓。	READY
19054_lwb_pre07	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	V251长轴；2007年外观更新前。	READY
19054_lwb_07	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	HIGH	V251长轴；2007年外观更新后。	READY
19054_lwb_facelift10	19054	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	HIGH	V251长轴；2010 facelift外廓。	READY
19055_swb	19055	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	HIGH	251.075短轴R 500车身。	READY
19055_lwb	19055	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	HIGH	251.175长轴R 500车身。	READY
45694	45694	Sedan	S-Class W116	W116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	HIGH	W116标准轴距四门车身。	READY
151673_se	151673	Sedan	S-Class W116	W116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	HIGH	输入同时覆盖280 SE与280 SEL；标准轴距分支。	READY
151673_sel	151673	Sedan	S-Class W116	V116	4	EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-LWB-01	HIGH	输入同时覆盖280 SE与280 SEL；长轴距分支。	READY
116790	116790	Sedan	S-Class W126	V126	4	EU-MERCEDES-BENZ-S-CLASS-W126-SEDAN-LWB-01	HIGH	北美300 SDL长轴距车身。	READY
125937	125937	Coupe	S-Class Coupe C126	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	HIGH	C126 1985改款后双门车身。	READY
57285	57285	Coupe	S-Class Coupe C126	C126	2	EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-PREFL-01	HIGH	C126 1985改款前双门车身。	READY
119796	119796	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	A217改款前AMG Cabriolet外廓。	READY
117886	117886	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	A217改款前AMG Cabriolet 4MATIC外廓。	READY
127331	127331	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-AMG63-SEDAN-LWB-FACELIFT-01	HIGH	V222 facelift AMG S 63长轴外廓。	READY
119042_prefl	119042	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	HIGH	生产区间跨2017 facelift；改款前S 65 Cabriolet。	READY
119042_facelift	119042	Convertible	S-Class Cabriolet A217	A217	2	EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-FACELIFT-01	HIGH	生产区间跨2017 facelift；改款后S 65 Cabriolet。	READY
11459	11459	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门车身；动力及改款版本三维外廓一致。	READY
14596	14596	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门AMG车身；三维外廓与标准C215一致。	READY
16977	16977	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门Kompressor AMG车身。	READY
11460	11460	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215双门V12车身。	READY
16961	16961	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215改款后双门V12车身。	READY
14919	14919	Coupe	S-Class Coupe C216	C216	2	EU-MERCEDES-BENZ-S-CLASS-C216-COUPE-FACELIFT-01	HIGH	C216 2010 facelift CL 63 AMG双门车身。	READY
17390	17390	Coupe	S-Class Coupe C215	C215	2	EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	HIGH	C215 CL 65 AMG双门车身。	READY
10302_prefl	10302	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	HIGH	输入区间跨2002改款；改款前短轴车身。	READY
10302_facelift	10302	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	HIGH	输入区间跨2002改款；改款后短轴车身。	READY
56741_prefl	56741	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56741_facelift	56741	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56742_prefl	56742	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
56742_facelift	56742	Sedan	S-Class W221	V221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	HIGH	长轴车身；跨2009 facelift拆分。	READY
100753_swb	100753	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 300 BlueTEC Hybrid短轴分支。	READY
100753_lwb	100753	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 300 BlueTEC Hybrid长轴分支。	READY
106363	106363	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	222.162长轴车身。	READY
14578	14578	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	HIGH	W220改款前短轴车身。	READY
17047	17047	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	HIGH	W220改款后短轴车身。	READY
54953_prefl	54953	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
54953_facelift	54953	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
56750_prefl	56750	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴4MATIC；跨2009 facelift拆分。	READY
56750_facelift	56750	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴4MATIC；跨2009 facelift拆分。	READY
18960_prefl	18960	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
18960_facelift	18960	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴车身；跨2009 facelift拆分。	READY
17470	17470	Sedan	S-Class W220	W220	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	W220改款后4MATIC高度分支。	READY
59008_swb	59008	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 350 BlueTEC短轴分支。	READY
59008_lwb	59008	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 350 BlueTEC长轴分支。	READY
100754_swb	100754	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	HIGH	S 350 BlueTEC 4MATIC短轴分支。	READY
100754_lwb	100754	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	S 350 BlueTEC 4MATIC长轴分支。	READY
100762	100762	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	HIGH	222.133长轴4MATIC车身。	READY
14029	14029	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	W221 facelift短轴车身。	READY
56156	56156	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	W221 facelift短轴车身。	READY
123503_prefl	123503	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	短轴4MATIC；生产区间跨2009 facelift。	READY
123503_facelift	123503	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	HIGH	短轴4MATIC；生产区间跨2009 facelift。	READY
128017_swb	128017	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	HIGH	2017 facelift短轴分支。	READY
128017_lwb	128017	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	HIGH	2017 facelift长轴分支。	READY
143387	143387	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.130长轴后驱车身。	READY
127328_swb	127328	Sedan	S-Class W222	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	HIGH	2017 facelift短轴4MATIC分支。	READY
127328_lwb	127328	Sedan	S-Class W222	V222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	HIGH	2017 facelift长轴4MATIC分支。	READY
143388	143388	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.131长轴4MATIC车身。	READY
154545	154545	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	HIGH	223.020短轴Mild Hybrid车身。	READY
154546	154546	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.120长轴Mild Hybrid车身。	READY
154548	154548	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	HIGH	223.021短轴Mild Hybrid 4MATIC车身。	READY
154549	154549	Sedan	S-Class W223	V223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	HIGH	223.121长轴Mild Hybrid 4MATIC车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_10201-10300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-II-V167-SUV-FACELIFT-01	4924	1947	1797	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gle/167-facelift/329234/
EU-MERCEDES-BENZ-GLK-I-X204-SUV-FACELIFT-01	4536	1840	1669	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1782125/mercedes-benz_glk_200_cdi_blueefficiency.html
EU-MERCEDES-BENZ-GLK-I-X204-SUV-PREFL-01	4525	1840	1689	Mercedes-Benz Public Archive; Automoli	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GLK-350-CDI-4MATIC-2010---2012.xhtml?oid=189873149;https://www.automoli.com/gb/vehicles/mercedes-benz/glk/glk-x204-2744/
EU-MERCEDES-BENZ-GL-II-X166-SUV-01	5120	1934	1850	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gl-klasse/166/233384/
EU-MERCEDES-BENZ-GL-I-X164-SUV-FACELIFT-01	5099	1920	1840	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/GL-350-CDI-4MATIC-BlueEFFICIENCY-2010---2012.xhtml?oid=191486615
EU-MERCEDES-BENZ-GL-II-X166-AMG63-SUV-01	5146	1982	1850	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/1782095/mercedes-benz_gl_63_amg_4matic.html
EU-MERCEDES-BENZ-GLS-I-X166-SUV-01	5130	1934	1850	Auto-Data	https://www.auto-data.net/en/mercedes-benz-gls-x166-generation-4650
EU-MERCEDES-BENZ-GLS-II-X167-SUV-FACELIFT-01	5209	1956	1823	ADAC Autokatalog	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/gls/167-facelift/328135/
EU-MERCEDES-BENZ-GLS-I-X166-AMG63-SUV-01	5162	1982	1850	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2230910/mercedes-amg_gls_63_4matic_coupe.html
EU-MERCEDES-BENZ-300-SL-W198-COUPE-01	4520	1790	1300	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SL.xhtml?oid=4699
EU-MERCEDES-BENZ-HECKFLOSSE-W112-SEDAN-01	4875	1795	1455	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SE.xhtml?oid=4893
EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	5140	1928	1980	EngineInDetail Marco Polo 300 d 2021; EngineInDetail Marco Polo 300 d 4MATIC 2021	https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-9g-tronic-2021;https://www.engineindetail.com/pa/mercedes-benz-marco-polo-300-d-4matic-9g-tronic-2021
EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-PREFL-01	4657	1845	2045	Mercedes-Benz Public Archive 1987 MB 100 D press kit; MB100 Archiv Kutter-Maße	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/print/Presseinformation-September-1987.xhtml?ls=L2RlL2luc3RhbmNlL3BpY3R1cmUueGh0bWw_b2lkPTExMDI0OQ%21%21&oid=182624921&rs=1;https://archiv.mb100.de/index.php/Kutter-Ma%C3%9Fe
EU-MERCEDES-BENZ-MB-100-W631-VAN-SWB-FACELIFT-01	4616	1845	2033	Mercedes-Benz Public Archive 1987 MB 100 D press kit; MB100 Archiv Kutter-Maße; Drom MB100 W631 dimensions	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/print/Presseinformation-September-1987.xhtml?ls=L2RlL2luc3RhbmNlL3BpY3R1cmUueGh0bWw_b2lkPTExMDI0OQ%21%21&oid=182624921&rs=1;https://archiv.mb100.de/index.php/Kutter-Ma%C3%9Fe;https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-PREFL-01	4922	1845	2033	Mercedes-Benz Public Archive 1987 MB 100 D press kit; MB100 Archiv Kutter-Maße	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/print/Presseinformation-September-1987.xhtml?ls=L2RlL2luc3RhbmNlL3BpY3R1cmUueGh0bWw_b2lkPTExMDI0OQ%21%21&oid=182624921&rs=1;https://archiv.mb100.de/index.php/Kutter-Ma%C3%9Fe
EU-MERCEDES-BENZ-MB-100-W631-VAN-LWB-FACELIFT-01	5066	1845	2033	Mercedes-Benz Public Archive 1987 MB 100 D press kit; MB100 Archiv Kutter-Maße; Drom MB100 W631 dimensions	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/print/Presseinformation-September-1987.xhtml?ls=L2RlL2luc3RhbmNlL3BpY3R1cmUueGh0bWw_b2lkPTExMDI0OQ%21%21&oid=182624921&rs=1;https://archiv.mb100.de/index.php/Kutter-Ma%C3%9Fe;https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-MERCEDES-BENZ-M-CLASS-III-W166-SUV-01	4804	1926	1796	Mercedes-Benz Public Archive; EncyCARpedia	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-BlueTEC-4MATIC-2011---2015.xhtml?oid=192703094;https://www.encycarpedia.com/mercedes/11-ml-350-bluetec-4matic-suv
EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-PREFL-01	4587	1833	1820	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-270-CDI.xhtml?oid=4810
EU-MERCEDES-BENZ-M-CLASS-I-W163-SUV-FACELIFT-01	4638	1840	1820	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-270-CDI.xhtml?oid=4814
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-PREFL-01	4780	1911	1815	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-4MATIC-2005---2008.xhtml?oid=191401379
EU-MERCEDES-BENZ-M-CLASS-II-W164-SUV-FACELIFT-01	4781	1911	1815	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-4MATIC-2008---2011.xhtml?oid=191414618
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML430-SUV-PREFL-01	4587	1833	1802	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-430.xhtml?oid=4809
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-PREFL-01	4635	1833	1804	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-55-AMG.xhtml?oid=4812
EU-MERCEDES-BENZ-M-CLASS-I-W163-ML55-AMG-SUV-FACELIFT-01	4635	1840	1804	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-55-AMG.xhtml?oid=4818
EU-MERCEDES-BENZ-M-CLASS-III-W166-AMG63-SUV-01	4817	1940	1762	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/ML-63-AMG-2012---2015-ab-ca-052013-ML-63-AMG-4MATIC.xhtml?oid=192703101
EU-MERCEDES-BENZ-PONTON-W105-SEDAN-PREFL-01	4650	1740	1560	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/219.xhtml?oid=4883
EU-MERCEDES-BENZ-PONTON-W105-SEDAN-FACELIFT-01	4680	1740	1560	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/219.xhtml?oid=4883
EU-MERCEDES-BENZ-600-W100-PULLMAN-SEDAN-01	6240	1950	1500	Mercedes-Benz Public Archive 600 Pullman four-door; Mercedes-Benz Public Archive 600 Pullman six-door	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-Pullman-limousine-4-doors.xhtml?oid=5058;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-Pullman-limousine-6-doors.xhtml?oid=5060
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-PRE07-01	4922	1922	1659	Automobile-Catalog 2006 Mercedes-Benz R 320 CDI 4MATIC	https://www.automobile-catalog.com/car/2006/1558580/mercedes-benz_r_320_cdi_4matic__dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-2007-01	4938	1922	1661	Automobile-Catalog 2007 Mercedes-Benz R 320 CDI 4MATIC	https://www.automobile-catalog.com/car/2007/1558685/mercedes-benz_r_320_cdi_4matic__dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-PRE07-01	5157	1922	1661	Automobile-Catalog 2006 Mercedes-Benz R 320 CDI 4MATIC LWB	https://www.automobile-catalog.com/car/2006/1558535/mercedes-benz_r_320_cdi_4matic_lwb_dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-2007-01	5173	1922	1663	Automobile-Catalog 2007 Mercedes-Benz R 320 CDI 4MATIC LWB	https://www.automobile-catalog.com/car/2007/1558745/mercedes-benz_r_320_cdi_4matic_lwb_dpf.html
EU-MERCEDES-BENZ-R-CLASS-I-V251-MPV-LWB-FACELIFT-2010-01	5157	1922	1677	Automobile-Catalog 2011 Mercedes-Benz R 350 4MATIC LWB	https://www.automobile-catalog.com/car/2011/1559270/mercedes-benz_r_350_4matic_lwb.html
EU-MERCEDES-BENZ-R-CLASS-I-W251-MPV-SWB-FACELIFT-2010-01	4922	1922	1676	Automobile-Catalog 2011 Mercedes-Benz R 350 4MATIC	https://www.automobile-catalog.com/car/2011/1559255/mercedes-benz_r_350_4matic.html
EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-SWB-01	4960	1870	1425	Mercedes-Benz Public Archive 280 S; Mercedes-Benz Public Archive 280 SE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-S--W-116-V-28-1972---1980.xhtml?oid=4869;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SE.xhtml?oid=4863
EU-MERCEDES-BENZ-S-CLASS-W116-SEDAN-LWB-01	5060	1870	1430	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-SEL.xhtml?oid=4868
EU-MERCEDES-BENZ-S-CLASS-W126-SEDAN-LWB-01	5285	1820	1441	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-SDL-Turbodiesel.xhtml?oid=4991
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-FACELIFT-01	4935	1828	1407	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/420-SEC.xhtml?oid=4550
EU-MERCEDES-BENZ-S-CLASS-C126-COUPE-PREFL-01	4910	1828	1406	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEC.xhtml?oid=4545
EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-PREFL-01	5044	1913	1428	Automobile-Catalog 2016 Mercedes-Benz S 63 AMG Cabriolet; Automobile-Catalog 2016 Mercedes-Benz S 65 AMG Cabriolet	https://www.automobile-catalog.com/car/2016/2296010/mercedes-benz_s_63_amg_cabriolet.html;https://www.automobile-catalog.com/car/2016/2296040/mercedes-benz_s_65_amg_cabriolet.html
EU-MERCEDES-BENZ-S-CLASS-W222-AMG63-SEDAN-LWB-FACELIFT-01	5287	1915	1499	Auto-Data Mercedes-Benz S-Class Long V222 AMG S 63 4MATIC	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-amg-s-63-v8-585hp-4matic-amg-speedshift-mct-18915
EU-MERCEDES-BENZ-S-CLASS-A217-AMG-CABRIOLET-FACELIFT-01	5051	1913	1428	Automobile-Catalog 2018 Mercedes-AMG S Cabriolet A217 phase II; Moniteur Automobile Mercedes-AMG S 65 Cabriolet	https://www.automobile-catalog.com/make/mercedes-amg/c-217_amg/a217_amg_2/2018.html;https://www.moniteurautomobile.be/modele-intitule-annee--mercedes--classe-s-cabriolet--2019/specifications-techniques-dimensions--59917--mercedes-classe-s-cabriolet-mercedes-amg-s-65-2p-ca-2019.html
EU-MERCEDES-BENZ-S-CLASS-C215-COUPE-01	4993	1857	1398	Mercedes-Benz Public Archive CL 500; Mercedes-Benz Public Archive CL 55 AMG; Mercedes-Benz Public Archive CL 65 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-500.xhtml?oid=4509;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-55-AMG.xhtml?oid=4511;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-65-AMG.xhtml?oid=2461783
EU-MERCEDES-BENZ-S-CLASS-C216-COUPE-FACELIFT-01	5106	1871	1425	Mercedes-Benz Public Archive CL 63 AMG 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/CL-63-AMG-2010---2014.xhtml?oid=191251467
EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-PREFL-01	5038	1855	1444	Mercedes-Benz Public Archive S 320 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI.xhtml?oid=4960
EU-MERCEDES-BENZ-S-CLASS-W220-SEDAN-FACELIFT-01	5043	1855	1444	Mercedes-Benz Public Archive S 320 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI--W-220-DE-32-LA-2002---2005.xhtml?oid=2461742
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	5206	1871	1473	Mercedes-Benz Public Archive S 320 CDI long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-320-CDI-long-wheelbase-2006---2009-from-122008-S-320-CDI-BlueEFFICIENCY-long-wheelbase.xhtml?oid=191730141
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Mercedes-Benz Public Archive 221 series facelift; AutoData1 S-Class Long W221 facelift	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/221-series-S-Class-Saloons-2009---2013.xhtml?oid=6016889;https://www.autodata1.com/en/car/mercedes-benz/s-class/s-class-long-w221-facelift-2009-s-450-v8-340-hp-4matic-g-tronic
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-PREFL-01	5116	1899	1496	Auto-Data Mercedes-Benz S-Class W222 S 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-s-class-w222-s-350-bluetec-258hp-7g-tronic-18881
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-PREFL-01	5246	1899	1494	Auto-Data Mercedes-Benz S-Class Long V222 S 350 BlueTEC	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-s-350-bluetec-v6-258hp-7g-tronic-plus-18920
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	5076	1871	1473	Mercedes-Benz Public Archive S 420 CDI	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-420-CDI-2006---2009.xhtml?oid=191730146
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Mercedes-Benz Public Archive S 350 CDI BlueEFFICIENCY	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-CDI-BlueEFFICIENCY-2009---2010.xhtml?oid=191730295
EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	5043	1855	1449	Mercedes-Benz Public Archive S 350 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-4MATIC.xhtml?oid=2461750
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-SWB-FACELIFT-01	5125	1899	1498	Auto-Data Mercedes-Benz S-Class W222 facelift S 350d	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-350d-286hp-g-tronic-31873
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-LWB-FACELIFT-01	5255	1899	1496	Auto-Data Mercedes-Benz S-Class Long V222 facelift S 350d	https://www.auto-data.net/en/mercedes-benz-s-class-long-v222-facelift-2017-s-350d-286hp-g-tronic-31735
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-LWB-01	5289	1954	1503	ADAC Mercedes-Benz S 350 d lang V223	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/223/339769/
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-SWB-01	5179	1954	1503	ADAC Mercedes-Benz S 350 d W223	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/223/339761/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_10201-10300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://archiv.mb100.de/index.php/Kutter-Ma%C3%9Fe?utm_source=chatgpt.com "Kutter-Maße"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1136 行）
- 累计尺寸组：dimension_groups_final.tsv（325 行）

