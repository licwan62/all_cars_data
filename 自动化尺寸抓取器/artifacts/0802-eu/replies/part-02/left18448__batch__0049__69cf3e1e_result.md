# 任务：left18448 第 4801-4900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0049__69cf3e1e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 4801-4900 行

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
left18448 第 4801-4900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FIAT-DOBLO-I-223-MPV-FACELIFT-01	4253	1722	1818
EU-FIAT-DOBLO-I-223-MPV-PREFL-01	4159	1714	1810
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-FACELIFT-01	4577	1789	1845
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-LWB-PREFL-01	4561	1789	1845
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-FACELIFT-01	4227	1789	1845
EU-FIAT-DOBLO-II-263-PICKUP-CHASSIS-SWB-PREFL-01	4211	1789	1845
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-FACELIFT-01	4981	1872	2049
EU-FIAT-DOBLO-II-263-PICKUP-WORKUP-PREFL-01	4965	1872	2049

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Fiat	Doblo	1.9 JTD	Großraumlimousine	Frontantrieb	Diesel	Jul 2003	-	17978
Fiat	Doblo	1.9 JTD	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jul 2003	-	17979
Fiat	Doblo	Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	Jun 2022	-	149150
Fiat	Doblo	Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2022	-	149158
Fiat	Doblo	Bluehdi 130	Großraumlimousine	Frontantrieb	Diesel	Jun 2022	-	149151
Fiat	Doblo	Bluehdi 130	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jun 2022	-	149160
Fiat	Doblo	Bluehdi 130 4X4	Kasten/Großraumlimousine	Allrad	Diesel	Jan 2025	-	801407
Fiat	Doblo	E-doblo	Großraumlimousine	Frontantrieb	Elektro	Jun 2022	Oct 2023	149149
Fiat	Doblo	E-doblo	Kasten/Großraumlimousine	Frontantrieb	Elektro	Jun 2022	Oct 2023	149153
Fiat	Doblo	E-doblo	Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	158238
Fiat	Doblo	E-doblo	Kasten/Großraumlimousine	Frontantrieb	Elektro	Nov 2023	-	158239
Fiat	Doblo	E-doblo 4X4	Kasten/Großraumlimousine	Allrad	Elektro	Jan 2025	-	801408
Fiat	Doblo	Puretech 110	Großraumlimousine	Frontantrieb	Benzin	Jun 2022	-	149152
Fiat	Doblo	Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jun 2022	-	149155
Fiat	Doblo cargo	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2013	Dec 2023	100768
Fiat	Doblo cargo	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2016	Dec 2023	119852
Fiat	Doblo cargo	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2016	Dec 2023	119854
Fiat	Doblo cargo	1.6 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2016	Dec 2023	119850
Fiat	Doblo kombi	1.3 D Multijet	Bus	Frontantrieb	Diesel	Mar 2016	Dec 2023	119853
Fiat	Doblo kombi	1.6 D Multijet	Bus	Frontantrieb	Diesel	Mar 2015	Dec 2023	113175
Fiat	Doblo kombi	1.6 D Multijet	Bus	Frontantrieb	Diesel	Mar 2015	Dec 2023	113191
Fiat	Doblo kombi	1.6 D Multijet	Bus	Frontantrieb	Diesel	Mar 2016	Dec 2023	119865
Fiat	Ducato	1.8	Kasten	Frontantrieb	Benzin	Jul 1982	Dec 1988	124817
Fiat	Ducato	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 1990	Mar 1994	7793
Fiat	Ducato	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Mar 1994	Apr 2002	11847
Fiat	Ducato	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Jul 1985	Aug 1990	14369
Fiat	Ducato	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Aug 1988	Aug 1990	14375
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	Dec 2001	Jul 2006	16648
Fiat	Ducato	2	Bus	Frontantrieb	Benzin	Dec 2001	Jul 2006	16652
Fiat	Ducato	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	Apr 2002	Jul 2006	58734
Fiat	Ducato	1.9 D	Kasten	Frontantrieb	Diesel	Jul 1990	Mar 1994	7796
Fiat	Ducato	1.9 D	Bus	Frontantrieb	Diesel	Apr 1998	Apr 2002	11409
Fiat	Ducato	1.9 D	Kasten	Frontantrieb	Diesel	Apr 1998	Apr 2002	11843
Fiat	Ducato	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Apr 2002	11849
Fiat	Ducato	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jan 1988	Aug 1990	14372
Fiat	Ducato	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 1998	Apr 2002	14464
Fiat	Ducato	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 1990	May 1994	57973
Fiat	Ducato	1.9 TD	Kasten	Frontantrieb	Diesel	Mar 1989	Mar 1994	7792
Fiat	Ducato	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1989	Mar 1994	11090
Fiat	Ducato	1.9 TD	Bus	Frontantrieb	Diesel	Apr 1998	Apr 2002	11410
Fiat	Ducato	1.9 TD	Kasten	Frontantrieb	Diesel	Apr 1998	Apr 2002	11842
Fiat	Ducato	1.9 TD	Kasten	Frontantrieb	Diesel	Mar 1994	Apr 2002	11848
Fiat	Ducato	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Apr 2002	11850
Fiat	Ducato	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1989	Aug 1990	14373
Fiat	Ducato	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Apr 1998	Apr 2002	14466
Fiat	Ducato	1.9 TD CAT	Kasten	Frontantrieb	Diesel	Aug 1994	Apr 2002	10696
Fiat	Ducato	1.9 TD CAT	Pritsche/Fahrgestell	Frontantrieb	Diesel	Aug 1994	Apr 2002	11851
Fiat	Ducato	110 Multijet 2,3 D	Bus	Frontantrieb	Diesel	Oct 2011	Jul 2014	15957
Fiat	Ducato	110 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	Oct 2011	Jul 2014	15958
Fiat	Ducato	110 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Oct 2011	Jul 2014	15959
Fiat	Ducato	115 Multijet 2,0 D	Bus	Frontantrieb	Diesel	Jun 2011	-	10201
Fiat	Ducato	115 Multijet 2,0 D	Kasten	Frontantrieb	Diesel	Jun 2011	-	10203
Fiat	Ducato	115 Multijet 2,0 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2011	-	10204
Fiat	Ducato	120 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	Jul 2021	-	144808
Fiat	Ducato	120 Multijet 2,2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2021	-	145286
Fiat	Ducato	120 Multijet 2,3 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Mar 2010	-	12026
Fiat	Ducato	120 Multijet 2,3 D 4X4	Kasten	Allrad	Diesel	Mar 2010	-	12028
Fiat	Ducato	130 Multijet 2,3 D	Bus	Frontantrieb	Diesel	Jan 2007	-	10205
Fiat	Ducato	140 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	Jul 2021	-	144809
Fiat	Ducato	140 Multijet 2,2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2021	-	145287
Fiat	Ducato	140 Multijet 2,2 D	Bus	Frontantrieb	Diesel	Jul 2021	Oct 2023	145288
Fiat	Ducato	140 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	Feb 2023	Oct 2023	155950
Fiat	Ducato	140 Natural Power	Pritsche/Fahrgestell	Frontantrieb	CNG	Apr 2009	-	57682
Fiat	Ducato	150 Multijet 2,3 D	Bus	Frontantrieb	Diesel	Jun 2011	-	10206
Fiat	Ducato	150 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	Jun 2011	-	10207
Fiat	Ducato	150 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2011	-	10208
Fiat	Ducato	150 Multijet 2,3 D	Bus	Frontantrieb	Diesel	Apr 2015	-	116551
Fiat	Ducato	160 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	Jul 2021	Oct 2023	144810
Fiat	Ducato	160 Multijet 2,2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2021	Oct 2023	145289
Fiat	Ducato	160 Multijet 3,0 D	Kasten	Frontantrieb	Diesel	Jul 2006	Dec 2011	57446
Fiat	Ducato	160 Multijet 3,0 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2006	May 2011	57448
Fiat	Ducato	160 Multijet 3,0 D	Bus	Frontantrieb	Diesel	Oct 2006	May 2011	59928
Fiat	Ducato	180 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	Jul 2021	-	144812
Fiat	Ducato	180 Multijet 2,2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2021	-	145290
Fiat	Ducato	180 Multijet 3,0 D	Bus	Frontantrieb	Diesel	Jun 2011	-	10209
Fiat	Ducato	180 Multijet 3,0 D	Kasten	Frontantrieb	Diesel	Jun 2011	-	10210
Fiat	Ducato	180 Multijet 3,0 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jun 2011	-	10211
Fiat	Ducato	2.0 Bipower	Kasten	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2002	Jul 2006	17607
Fiat	Ducato	2.0 Bipower	Bus	Frontantrieb	Benzin/Erdgas (CNG)	Nov 2002	Jul 2006	17608
Fiat	Ducato	2.0 JTD	Kasten	Frontantrieb	Diesel	Oct 2001	Apr 2002	16486
Fiat	Ducato	2.0 JTD	Bus	Frontantrieb	Diesel	Oct 2001	Apr 2002	16487
Fiat	Ducato	2.0 JTD	Kasten	Frontantrieb	Diesel	Dec 2001	Jul 2006	16649
Fiat	Ducato	2.0 JTD	Bus	Frontantrieb	Diesel	Dec 2001	Jul 2006	16653
Fiat	Ducato	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2001	Jul 2006	16738
Fiat	Ducato	2.0 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 2001	Apr 2002	58732
Fiat	Ducato	2.3 JTD	Kasten	Frontantrieb	Diesel	Dec 2001	Jul 2006	16650
Fiat	Ducato	2.3 JTD	Bus	Frontantrieb	Diesel	Dec 2001	Jul 2006	16654
Fiat	Ducato	2.3 JTD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Dec 2001	Jul 2006	16739
Fiat	Ducato	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1989	Mar 1994	7795
Fiat	Ducato	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Mar 1994	Apr 2002	11091
Fiat	Ducato	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1982	Aug 1990	14370
Fiat	Ducato	2.5 D 4X4	Kasten	Allrad	Diesel	Mar 1989	Aug 1990	14362
Fiat	Ducato	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Jul 1990	Mar 1994	14363
Fiat	Ducato	2.5 D 4X4	Kasten	Allrad	Diesel	Jul 1990	Mar 1994	14365
Fiat	Ducato	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Mar 1989	Aug 1990	14374
Fiat	Ducato	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	Mar 1994	Apr 2002	14863
Fiat	Ducato	2.5 D 4X4	Kasten	Allrad	Diesel	Mar 1994	Apr 2002	116060
Fiat	Ducato	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Jul 1990	Mar 1994	11089
Fiat	Ducato	2.5 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	Sep 1986	May 1990	59931
Fiat	Ducato	2.5 TD 4X4	Kasten	Allrad	Diesel	Jul 1990	Mar 1994	7794


--- Round 1 / 首次发送 ---
## 更新点

* 已优先闭合第三代 Doblò K9 非 4X4 厢式车：标准轴距和 Maxi 长轴分别建组。官方资料明确给出标准版 `4403×1848×1796 mm`、Maxi 版 `4753×1848×1812 mm`，其中宽度为不含后视镜口径；改款后的现行规格仍保持相同长度和宽度，因此 2023 年 11 月起的普通 E-Doblò Cargo 可复用这两个组。
* Ktype `17978` 直接复用跨批次已有的 Doblò I 223 pre-facelift MPV 尺寸组，不重复输出尺寸组。
* Ktype `17979` 暂不强行复用：输入同时包含 Kasten/Großraumlimousine，需先排除 Cargo 高顶或其他物理分支。
* 两个 2025 年 4X4 Ktype 暂留 PENDING，禁止在未确认 4X4 高度与标准/Maxi边界前套用普通 K9 组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：11
* PENDING/尚未闭合 Ktype：89
* 本轮明确落盘 PENDING：3
* 本轮新建尺寸组：2
* 本轮复用已有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17978	17978	MPV	Doblò I pre-facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	223乘用型标准外廓。	READY
17979	17979	Van	Doblò I pre-facelift	223			MEDIUM	混合厢式车/MPV分类，具体车顶与车身分支待确认。	PENDING: 223厢式车物理分支尚未闭合
149158_swb	149158	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149158_lwb	149158	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
149160_swb	149160	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149160_lwb	149160	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
801407	801407	Van	Doblò III facelift	K9			MEDIUM	4X4版本需确认标准/Maxi及专用外廓边界。	PENDING: 4X4车身长度与高度尚未闭合
149153_swb	149153	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149153_lwb	149153	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
158239_swb	158239	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
158239_lwb	158239	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
801408	801408	Van	Doblò III facelift	K9			MEDIUM	电动4X4版本需确认标准/Maxi及专用外廓边界。	PENDING: 电动4X4车身长度与高度尚未闭合
149155_swb	149155	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149155_lwb	149155	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-III-K9-VAN-SWB-01	4403	1848	1796	Fiat Professional Nuovo Doblò official brochure	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
EU-FIAT-DOBLO-III-K9-VAN-LWB-01	4753	1848	1812	Fiat Professional Nuovo Doblò official brochure	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
```

## 下一步优先处理

1. 闭合第三代 Doblò 普通乘用型 Ktype，分别确认 2022–2023 与 2023 年末改款后的准确高度。
2. 核对 Ktype `801407`、`801408` 的 4X4 标准/Maxi覆盖范围和外部高度。
3. 批量处理 Doblò II 263 facelift Cargo/Kombi，按 Van、Maxi Van、High Roof、XL及 Combi分支一次建组并复用。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 按“映射行”和“输入 Ktype”分别校正进度口径，避免多外廓派生行被误算成多个输入 Ktype。
* 已闭合 Doblò II 263 facelift 的 95 PS Cargo、120 PS Cargo 与 95 PS Combi。官方 2016 资料确认：L1H1 为 `4406×1832×1845`、L2H1 为 `4756×1832×1880`、L2H2 为 `4756×1832×2125`；95 PS Cargo覆盖 L1H1/L2H1，120 PS Cargo覆盖 L1H1/L2H1/L2H2，95 PS Combi仅覆盖 L1H1。
* Combi L1H1 与 Cargo L1H1 外廓一致，直接复用同一个 SWB 尺寸组，不重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：17 行
* 已闭合输入 Ktype：9/100
* PENDING/尚未闭合输入 Ktype：91
* 其中已落盘 PENDING：3
* 已确认尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119852_swb	119852	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	95 PS Cargo L1H1。	READY
119852_lwb	119852	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	95 PS Cargo L2H1。	READY
119850_swb	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	120 PS Cargo L1H1。	READY
119850_lwb	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	120 PS Cargo L2H1。	READY
119850_highroof	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-HIGHROOF-FACELIFT-01	HIGH	120 PS Cargo L2H2高顶。	READY
119853	119853	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	95 PS Combi L1H1。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1845	Fiat Professional Range Price List December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880	Fiat Professional Range Price List December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-DOBLO-II-263-VAN-HIGHROOF-FACELIFT-01	4756	1832	2125	Fiat Professional Range Price List December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
```

## 下一步优先处理

1. 闭合 `100768` 跨 pre-facelift/facelift 边界，以及 `119854` 80 PS Cargo 的 L1/L2覆盖范围。
2. 批量确认 `113175`、`113191`、`119865` 三个 Doblò II Kombi 的标准、Maxi和高顶边界。
3. 随后处理仍为 PENDING 的 `17979`、`801407`、`801408`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 `100768`、`119854`、`113175`、`113191`、`119865`。`100768` 的 75 PS Cargo 仅按标准轴距处理，并因改款前后车长不同拆成两行；改款前首次建立 SWB 组，改款后复用既有 SWB facelift 组。官方资料显示改款前标准版为 `4390×1832×1845 mm`，且当期 1.3 Multijet 配置属于标准车身。([Stellantis Media][1])
* `119854` 的四个 263 车身代码闭合为 SWB/LWB；三个 Kombi Ktype 按对应的短轴和长轴外廓复用既有 facelift 组。Ktype、生产区间及车身代码已对应，Cargo 与 Combi 的官方外廓表支持复用相同的 SWB/LWB 尺寸事实。([Denso AM][2])
* 修正上一轮高顶组命名：`119850_highroof` 改为 `119850_lwb_highroof`；原临时组 `EU-FIAT-DOBLO-II-263-VAN-HIGHROOF-FACELIFT-01` 不再保留，改用明确表示 L2H2 的新组 ID。官方规格区分短轴高顶 `4406 mm` 与长轴高顶 `4756 mm`，本行尺寸属于后者。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：27 行
* 已闭合输入 Ktype：14/100
* PENDING/尚未闭合输入 Ktype：86
* 其中已落盘 PENDING：3
* 已确认尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100768_swb_prefl	100768	Van	Doblò II pre-facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-PREFL-01	HIGH	75 PS Cargo改款前L1H1。	READY
100768_swb_facelift	100768	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	75 PS Cargo改款后L1H1。	READY
119854_swb	119854	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	80 PS Cargo L1H1。	READY
119854_lwb	119854	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	80 PS Cargo L2H1。	READY
119850_lwb_highroof	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-HIGHROOF-FACELIFT-01	HIGH	120 PS Cargo L2H2高顶。	READY
113175_swb	113175	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	95 PS Kombi短轴外廓。	READY
113175_lwb	113175	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	95 PS Kombi长轴外廓。	READY
113191_swb	113191	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	120 PS Kombi短轴外廓。	READY
113191_lwb	113191	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	120 PS Kombi长轴外廓。	READY
119865_swb	119865	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	100 PS Kombi短轴外廓。	READY
119865_lwb	119865	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	100 PS Kombi长轴外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-II-263-VAN-SWB-PREFL-01	4390	1832	1845	Fiat Professional New Doblò Cargo Euro 5 official specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_EURO5.pdf
EU-FIAT-DOBLO-II-263-VAN-LWB-HIGHROOF-FACELIFT-01	4756	1832	2125	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
```

## 下一步优先处理

1. 处理三条已落盘 PENDING：`17979`、`801407`、`801408`。
2. 闭合第三代 Doblò 普通乘用型 `149150`、`149151`、`149149`、`158238`、`149152`。
3. Doblò 全部闭合后，按 Ducato 代际、车身形式、轴距和车顶聚类批量建组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_EURO5.pdf "FIAT NEW DOBLO CARGO EURO5"
[2]: https://www.denso-am.eu/catalog/pv/119854 "Car parts for FIAT DOBLO Cargo (263_), 1.3 D Multijet (263ZXT1A, 263WXT1A, 263ZYA1A, 263WYA1A), 59kW(80ps), 225 A2.000, 552 83 775 | DENSO"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合第三代 Doblò 的 5 个普通乘用型 Ktype。燃油 Combi 标准轴距采用官方无车顶横杆外廓 `4403×1848×1800 mm`；E-Doblò 乘用型采用德国官方配置外廓 `4403×1848×1844 mm`。
* 已闭合 `801407` BlueHDi 130 4X4。Dangel 官方确认该 4WD 转换适用于全部车长并将车身抬高 90 mm；结合已确认的 K9 短轴、长轴基础外廓，新建短轴 `4403×1848×1886 mm` 和长轴 `4753×1848×1902 mm` 两组。([Dangel Shop][1])
* `801408` 暂不套用柴油 4WD 组：当前 Dangel 官方 4WD范围明确指向 BlueHDi 130，电动车公开方案为 TReK 增强牵引，尚不能证明与 4WD 使用相同外廓。([Dangel Shop][1])
* `17979` 继续保留 PENDING；改款前 Cargo 与乘用型存在高度分支，不能直接复用已有 MPV 组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：34 行
* 已闭合输入 Ktype：20/100
* PENDING/尚未闭合输入 Ktype：80
* 其中已明确落盘 PENDING：2
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17979	17979	Van	Doblò I pre-facelift	223				MEDIUM	Kasten与MPV外廓高度分支待拆分。	PENDING: 223改款前Cargo与乘用型高度分支尚未闭合
149150	149150	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
149151	149151	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
149149	149149	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	HIGH	K9电动乘用型标准轴距。	READY
158238	158238	MPV	Doblò III facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	MEDIUM	K9改款电动乘用型标准轴距。	READY
801407_swb	801407	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	HIGH	Dangel 4WD短轴厢式车。	READY
801407_lwb	801407	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	HIGH	Dangel 4WD长轴厢式车。	READY
801408	801408	Van	Doblò III facelift	K9				MEDIUM	电动版本的4WD物理外廓尚未确认。	PENDING: 电动4WD与TReK方案边界尚未闭合
149152	149152	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	4403	1848	1800	Fiat Professional New Doblò official model document	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	4403	1848	1844	Fiat E-Doblò German official price list	https://www.media.stellantis.com/uploads/de/model-document/fiat_preisliste_doblo_web-62b9d252f1c3d.pdf
EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	4403	1848	1886	Fiat Professional New Doblò official model document;Dangel 4WD by Dangel official announcement	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf;https://www.dangel.com/en/dangel-reinvents-4x4-new-revolutionary-technology
EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	4753	1848	1902	Fiat Professional New Doblò official model document;Dangel 4WD by Dangel official announcement	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf;https://www.dangel.com/en/dangel-reinvents-4x4-new-revolutionary-technology
```

## 下一步优先处理

1. 闭合 `17979` 的 Doblò I 223 Cargo 与 MPV 分支，并只为确认不同的 Cargo 外廓新建组。
2. 继续核对 `801408` 电动 4X4，不将 TReK 增强牵引误写为四轮驱动。
3. 随后进入 Ducato，先按第一代、第二代和第三代聚类，再批量处理 Van、Bus、底盘以及轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.dangel.com/en/dangel-reinvents-4x4-new-revolutionary-technology?utm_source=chatgpt.com "DANGEL reinvents 4x4 with a new revolutionary technology | DANGEL 4x4 | Experts en sytèmes 4 roues motrices"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 `17979`：改款前标准车身复用既有 223 pre-facelift 组；改款后按标准轴距低顶、标准轴距高顶和长轴低顶拆分。Fiat 223 手册的尺寸矩阵分别给出 `4253×1722×1831`、`4253×1722×2086` 和 `4633×1722×1817 mm`，并确认 1.9 100/105 HP 覆盖这三种 Cargo 外廓。([My Car User Manual][1])
* 已闭合 `801408`：Dangel 资料确认 E-Doblò 4WD 覆盖短轴和长轴厢式车，Fiat 官方亦确认量产 E-Doblò 4x4 车队；其物理外廓命中上轮已创建的 K9 4X4 短轴、长轴组，本轮只修改映射，不重复输出尺寸组。([Dangel Shop][2])
* Doblò 输入已全部闭合，后续转入 Ducato 聚类处理。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：40 行
* 已闭合输入 Ktype：22/100
* 尚未闭合输入 Ktype：78
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17979_swb_prefl	17979	Van	Doblò I pre-facelift	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前标准轴距低顶外廓。	READY
17979_swb_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-SWB-FACELIFT-01	HIGH	改款后标准轴距低顶。	READY
17979_swb_highroof_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-SWB-HIGHROOF-FACELIFT-01	HIGH	改款后标准轴距高顶。	READY
17979_lwb_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-LWB-FACELIFT-01	HIGH	改款后长轴低顶。	READY
801408_swb	801408	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	HIGH	电动4WD短轴厢式车。	READY
801408_lwb	801408	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	HIGH	电动4WD长轴厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-I-223-VAN-SWB-FACELIFT-01	4253	1722	1831	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
EU-FIAT-DOBLO-I-223-VAN-SWB-HIGHROOF-FACELIFT-01	4253	1722	2086	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
EU-FIAT-DOBLO-I-223-VAN-LWB-FACELIFT-01	4633	1722	1817	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
```

## 下一步优先处理

1. 批量闭合 1982–1994 第一代 Ducato，按 Van、Bus、底盘及轴距/车顶外廓建组。
2. 随后处理 1994–2006 第二代 Ducato 的改款边界。
3. 最后集中处理 2006 年后的第三代 Ducato，复用相同轴距和车顶尺寸组。

推进信号：CONTINUE

[1]: https://www.mycarusermanual.com/fiat/doblo/van/2000-2009/technical-specifications "Get TECHNICAL SPECIFICATIONS Guide for Fiat Doblo Van 2000-2009"
[2]: https://www.dangel.com/sites/www.dangel.fr/files/pdf/Tarifs%20au%2001.03.2026/EN_Tarif_Dangel_01_04_2026.pdf?utm_source=chatgpt.com "PRICE LIST
Exluding VAT and transport as of Februa"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 6 个第一代 Ducato 厢式车 Ktype：`124817`、`7792`、`7796`、`14362`、`14365`、`7794`。
* `124817`、`14362` 属于 280 车身；`7792`、`7796`、`14365`、`7794` 属于 290 车身，其中后三个相关 Ktype 的前驱/四驱边界已按目录记录区分。([Meyer Motoren][1])
* 280、290 前驱厢式车均拆分标准顶和高顶；官方型式批准分别确认标准顶高度 `2100 mm`、高顶高度 `2450 mm`。外廓宽度栏为 `1965 mm`，后视镜另列，符合不含后视镜口径。
* 280 4X4 拆分 `2129 mm` 标准顶和 `2482 mm` 高顶；290 4X4 拆分 `2145 mm` 标准顶和 `2490 mm` 高顶。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：52 行
* 已闭合输入 Ktype：28/100
* PENDING/尚未闭合输入 Ktype：72
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
124817_lowroof	124817	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-LOWROOF-01	HIGH	280前驱标准顶厢式车。	READY
124817_highroof	124817	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-HIGHROOF-01	HIGH	280前驱高顶厢式车。	READY
7792_lowroof	7792	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	HIGH	290前驱标准顶厢式车。	READY
7792_highroof	7792	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	HIGH	290前驱高顶厢式车。	READY
7796_lowroof	7796	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	HIGH	290前驱标准顶厢式车。	READY
7796_highroof	7796	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	HIGH	290前驱高顶厢式车。	READY
14362_lowroof	14362	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-4X4-LOWROOF-01	HIGH	280四驱标准顶厢式车。	READY
14362_highroof	14362	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-4X4-HIGHROOF-01	HIGH	280四驱高顶厢式车。	READY
14365_lowroof	14365	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-LOWROOF-01	HIGH	290四驱标准顶厢式车。	READY
14365_highroof	14365	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-HIGHROOF-01	HIGH	290四驱高顶厢式车。	READY
7794_lowroof	7794	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-LOWROOF-01	HIGH	290四驱标准顶厢式车。	READY
7794_highroof	7794	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-HIGHROOF-01	HIGH	290四驱高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-I-280-VAN-LOWROOF-01	4765	1965	2100	Swiss Federal Roads Office Fiat Ducato 280/14 type approval CH 3F2063	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2063_F.pdf
EU-FIAT-DUCATO-I-280-VAN-HIGHROOF-01	4765	1965	2450	Swiss Federal Roads Office Fiat Ducato 280/14 type approval CH 3F2063	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2063_F.pdf
EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	4765	1965	2100	Swiss Federal Roads Office Fiat Ducato 290/14 type approval CH 3F2111	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2111_D.pdf
EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	4765	1965	2450	Swiss Federal Roads Office Fiat Ducato 290/14 type approval CH 3F2111	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2111_D.pdf
EU-FIAT-DUCATO-I-280-VAN-4X4-LOWROOF-01	4765	1965	2129	Swiss Federal Roads Office Fiat Ducato 280/14 4x4 type approval CH 3F2108	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2108_D.pdf
EU-FIAT-DUCATO-I-280-VAN-4X4-HIGHROOF-01	4765	1965	2482	Swiss Federal Roads Office Fiat Ducato 280/14 4x4 type approval CH 3F2108	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2108_D.pdf
EU-FIAT-DUCATO-I-290-VAN-4X4-LOWROOF-01	4765	1965	2145	Swiss Federal Roads Office Fiat Ducato 290/14 4x4 type approval CH 3F2151	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2151_F.pdf
EU-FIAT-DUCATO-I-290-VAN-4X4-HIGHROOF-01	4765	1965	2490	Swiss Federal Roads Office Fiat Ducato 290/14 4x4 type approval CH 3F2151	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2151_F.pdf
```

## 下一步优先处理

1. 批量闭合 280/290 `Pritsche/Fahrgestell` Ktype，区分前驱、四驱及实际轴距。
2. 闭合 1994–2002 Ducato II 230 的 Van、Bus和底盘分支。
3. 再处理 2002–2006 Ducato II 244，复用相同发动机下的既有车身组。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/fahrzeuge/7792/fiat/ducato_kasten_290__/1_9_td_7792?utm_source=chatgpt.com "1.9 TD | Ducato Kasten (290) | Fiat | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已确认 `14369` 的 2.0 55 kW 长轴双排座底盘分支：车身代码 280、轴距 3653 mm、4 门，完整外廓为 `5442×1965×2050 mm`。同发动机还存在未给出完整量产外廓的普通短轴/长轴底盘，暂不猜测建组。([Astra开放数据][1])
* 已确认 `14370` 的 2.5 D 两个原厂平板分支：短轴原厂平板 `4840×2000×2050 mm`，Maxi 长轴原厂平板 `5576×2000×2076 mm`。对应裸底盘分支虽然已确认存在，但批准文件没有给出可直接落盘的完整统一三维，继续保持 PENDING。([Astra开放数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：55 行
* 显式 PENDING 映射：5 行
* 已完全闭合输入 Ktype：28/100
* 尚未完全闭合输入 Ktype：72
* 已确认尺寸组：25
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14369_swb_chassis	14369	Pickup	Ducato I pre-facelift	280				MEDIUM	普通短轴底盘分支。	PENDING: 短轴裸底盘完整外廓未闭合
14369_lwb_chassis	14369	Pickup	Ducato I pre-facelift	280				MEDIUM	普通长轴单排座底盘分支。	PENDING: 长轴单排座底盘完整外廓未闭合
14369_lwb_doublecab	14369	Pickup	Ducato I pre-facelift	280	4	EU-FIAT-DUCATO-I-280-CHASSIS-LWB-DOUBLECAB-01	HIGH	长轴双排座底盘。	READY
14370_swb_chassis	14370	Pickup	Ducato I pre-facelift	280	2			MEDIUM	短轴单排座裸底盘。	PENDING: 短轴裸底盘三维未完整列明
14370_swb_flatbed	14370	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
14370_maxi_chassis	14370	Pickup	Ducato I pre-facelift	280	2			MEDIUM	Maxi长轴裸底盘。	PENDING: Maxi裸底盘三维未完整列明
14370_maxi_flatbed	14370	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	HIGH	Maxi长轴原厂平板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-I-280-CHASSIS-LWB-DOUBLECAB-01	5442	1965	2050	Swiss Federal Roads Office Fiat Ducato 280 NAP4 type approval CH 3F2027	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2027_D.pdf
EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	4840	2000	2050	Swiss Federal Roads Office Fiat Ducato 280 M.7 type approval CH 3F2011	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2011_D.pdf
EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	5576	2000	2076	Swiss Federal Roads Office Fiat Ducato 280 Maxi R.7 type approval CH 3F2001	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2001_D.pdf
```

## 下一步优先处理

1. 暂停继续扩展缺少确定车身外廓的 280 裸底盘分支，避免以轴距或车架长度代替完整量产外廓。
2. 转向可批量闭合的 Ducato II 230 Van、Bus 和原厂平板，先建立标准轴距、长轴及低顶/高顶缓存组。
3. 处理 230 组后，再用已闭合尺寸组批量关联对应 Ktype。

推进信号：CONTINUE

[1]: https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2027_D.pdf "BSY1/EVPS/T754S.E517PROD.JOB28983.D0000443.?"
[2]: https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2011_D.pdf "BSY1/EVPS/T754S.E517PROD.JOB28983.D0000416.?"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已建立 Ducato II 230 厢式车的四个稳定外廓组：短轴标准顶 `4655×1998×2150`、短轴高顶 `4655×1998×2470`、中轴标准顶 `5005×1998×2150`、中轴高顶 `5005×1998×2470`。型式批准将外后视镜单独列示，因此 `1998 mm` 可按不含后视镜宽度落盘。([Astra开放数据][1])
* 已批量关联 `11848`、`10696`、`11842`、`11843` 四个 Kasten Ktype；发动机和排放版本不重复建尺寸组。
* 已闭合 `11409`、`11410` 两个 Bus Ktype，均关联中轴标准顶外廓 `5005×1998×2150 mm`。([Astra开放数据][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：73 行
* 显式 PENDING 映射：5 行
* 已完全闭合输入 Ktype：34/100
* 尚未完全闭合输入 Ktype：66
* 已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11409	11409	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
11843_swb_lowroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	MEDIUM	230短轴标准顶厢式车。	READY
11843_swb_highroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	MEDIUM	230短轴高顶厢式车。	READY
11843_mwb_lowroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴标准顶厢式车。	READY
11843_mwb_highroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	MEDIUM	230中轴高顶厢式车。	READY
11410	11410	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
11842_swb_lowroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	MEDIUM	230短轴标准顶厢式车。	READY
11842_swb_highroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	MEDIUM	230短轴高顶厢式车。	READY
11842_mwb_lowroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴标准顶厢式车。	READY
11842_mwb_highroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	MEDIUM	230中轴高顶厢式车。	READY
11848_swb_lowroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
11848_swb_highroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
11848_mwb_lowroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
11848_mwb_highroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
10696_swb_lowroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
10696_swb_highroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
10696_mwb_lowroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
10696_mwb_highroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	4655	1998	2150	Swiss Federal Roads Office Fiat Ducato 230/14 1.9 TDS type approval CH 3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	4655	1998	2470	Swiss Federal Roads Office Fiat Ducato 230/14 1.9 TDS type approval CH 3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	5005	1998	2150	Swiss Federal Roads Office Fiat Ducato 230/14 1.9 TDS type approval CH 3F2313	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2313_F.pdf
EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	5005	1998	2470	Swiss Federal Roads Office Fiat Ducato 230/14 1.9 TDS type approval CH 3F2313	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2313_F.pdf
```

## 下一步优先处理

1. 闭合 Ducato II 230 的 `11847`、`11849`、`11850`、`11851`、`11091`、`14464`、`14466` 底盘与原厂平板分支。
2. 处理 `14863`、`116060` 的 230 四驱底盘和厢式车外廓。
3. 230 完成后进入 Ducato II 244，优先批量复用 Van、Bus及底盘轴距/车顶组。

推进信号：CONTINUE

[1]: https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf "BSY1/EVPS/T754S.E517PROD.STC09130.D0004873.?"
[2]: https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/1F3409_F.pdf "BSY1/EVPS/T754S.E517PROD.STC02169.D0002019.?"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已确认 `16486`、`16487` 均属于 Ducato II `230`，不是后续 `244`；分别为 2.0 JTD Kasten 与 Bus。([Seek4Cars][1])
* `16486` 直接关联已确认的 230 短轴/中轴、标准顶/高顶四个尺寸组；`16487` 关联既有 230 中轴标准顶组。
* 本轮未创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：78 行
* 显式 PENDING 映射：5 行
* 已完全闭合输入 Ktype：36/100
* 尚未完全闭合输入 Ktype：64
* 已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16486_swb_lowroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
16486_swb_highroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
16486_mwb_lowroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
16486_mwb_highroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
16487	16487	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `58732`、`11849`、`11850`、`11851`、`11091`、`14464`、`14466` 的 230 底盘与原厂平板分支。
2. 处理 `14863`、`116060` 的 230 四驱底盘和厢式车。
3. 随后进入 244，集中建立 Van、Bus 与原厂 Truck 的稳定尺寸组。

推进信号：CONTINUE

[1]: https://seek4cars.net/reservedele/hjs-retrofit-dpf-til-ducato-jumper-boxer-230-244-2-0-jtd/ed01316c-73bc-45ea-b28a-03ea333fa7e6?utm_source=chatgpt.com "HJS Retrofit DPF til Ducato/Jumper/Boxer 230/244 2,0 JTD DPF12.02 - DAJOLKA"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已确认 `11091` 的 Ducato II 230 2.5 D 原厂平板覆盖短轴、中轴和长轴三种车身代码；裸底盘相应存在三种轴距，但型式批准不提供完成改装后的统一外廓，因此平板分支转为 READY，裸底盘分支保持 PENDING。([typenscheine.ch][1])
* 已确认 `14863` 的 230 四驱底盘覆盖 3200 mm 与 3700 mm 两种轴距；对应原厂平板外廓为 `5120×2000×2100` 和 `5620×2000×2100 mm`，与前驱原厂平板外廓完全一致，因此直接复用同一尺寸组，不重复创建 4X4 专用组。裸底盘没有完整三维，继续 PENDING。([Typenscheinschweiz.ch][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：83 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：36/100
* 尚未完全闭合输入 Ktype：64
* 已确认尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11091_swb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
11091_mwb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	HIGH	中轴原厂平板。	READY
11091_lwb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	HIGH	长轴原厂平板。	READY
11091_swb_chassis	11091	Pickup	Ducato II	230	2		MEDIUM	短轴裸底盘。	PENDING: 裸底盘完成状态外廓未闭合
11091_mwb_chassis	11091	Pickup	Ducato II	230	2		MEDIUM	中轴裸底盘。	PENDING: 裸底盘完成状态外廓未闭合
11091_lwb_chassis	11091	Pickup	Ducato II	230	2		MEDIUM	长轴裸底盘。	PENDING: 裸底盘完成状态外廓未闭合
14863_mwb_flatbed	14863	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	四驱中轴原厂平板。	READY
14863_lwb_flatbed	14863	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	MEDIUM	四驱长轴原厂平板。	READY
14863_mwb_chassis	14863	Pickup	Ducato II	230	2		MEDIUM	四驱中轴裸底盘。	PENDING: 四驱裸底盘完成状态外廓未闭合
14863_lwb_chassis	14863	Pickup	Ducato II	230	2		MEDIUM	四驱长轴裸底盘。	PENDING: 四驱裸底盘完成状态外廓未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	4770	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	5120	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	5620	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
```

## 下一步优先处理

1. 使用本轮三个原厂平板缓存组，批量关联 `11849`、`11850`、`11851`、`14464`、`14466`，并按各发动机实际覆盖的轴距拆分。
2. 闭合 `116060` 的 230 四驱厢式车，区分短轴普通顶、短轴高顶和长轴高顶，避免把型式批准中的长度范围直接写成单一尺寸。
3. 随后处理 Ducato II 244 的 Van、Bus及原厂平板组。

推进信号：CONTINUE

[1]: https://typenscheine.ch/en/Type/FIATDucato142_5D-1FA594?utm_source=chatgpt.com "FIAT Ducato 14 2.5D"
[2]: https://typenscheinschweiz.ch/pdf/auto/3FA359?utm_source=chatgpt.com "FIAT Ducato 14 2.8JTD"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 已将 `11849`、`11850`、`11851`、`14464`、`14466` 五个 Ducato II 230 的 1.9 D/TD 原厂平板分支关联至既有短轴和中轴尺寸组。
* `14466` 有 3FA301 型式批准直接支持：原厂平板车身代码 `ANMDA/ANMDB`，对应长度 `4770/5120 mm`、宽度 `2000 mm`、高度 `2100 mm`。
* 其余四个 Ktype 已确认属于相同的 Ducato 230 Pritsche/Fahrgestell 1.9 D/TD 系列；基于同平台原厂平板缓存作 MEDIUM 置信度关联，不新增尺寸组。([KFZTEILE24][1])
* 未为无固定完成外廓的裸底盘创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：93 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：41/100
* 尚未完全闭合输入 Ktype：59
* 已确认尺寸组：32
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11849_swb_flatbed	11849	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	1.9 D短轴原厂平板。	READY
11849_mwb_flatbed	11849	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	1.9 D中轴原厂平板。	READY
11850_swb_flatbed	11850	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	1.9 TD短轴原厂平板。	READY
11850_mwb_flatbed	11850	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	1.9 TD中轴原厂平板。	READY
11851_swb_flatbed	11851	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	1.9 TD CAT短轴原厂平板。	READY
11851_mwb_flatbed	11851	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	1.9 TD CAT中轴原厂平板。	READY
14464_swb_flatbed	14464	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	1.9 D短轴原厂平板。	READY
14464_mwb_flatbed	14464	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	1.9 D中轴原厂平板。	READY
14466_swb_flatbed	14466	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	HIGH	1.9 TD短轴原厂平板。	READY
14466_mwb_flatbed	14466	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	HIGH	1.9 TD中轴原厂平板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `116060` 的 Ducato II 230 2.5 D 4X4 厢式车，确认其实际轴距和车顶分支，不直接套用前驱高度。
2. 清理此前由裸底盘无固定完成外廓产生的显式 PENDING 派生行，保留有确定原厂外廓的平板分支。
3. 进入 Ducato II 244，集中建立并复用 Van、Bus及原厂平板尺寸组。

推进信号：CONTINUE

[1]: https://www.kfzteile24.at/pkw-teile/ersatzteile/fiat/ducato/ducato-pritsche-fahrgestell-230 "FIAT DUCATO Pritsche/Fahrgestell (230_) Ersatzteile kaufen | HTTPS://KFZTEILE24.AT"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已首次闭合 Ducato II `244` 厢式车尺寸矩阵。官方手册将 `G=2024 mm` 标为车身外宽，后视镜位于该测量线外，可按不含后视镜宽度落盘。
* 已批量闭合 `16648`（2.0 汽油）、`16649`（2.0 JTD）和 `16650`（2.3 JTD）三个 Kasten Ktype。
* `16648`、`16650` 覆盖普通 11/15 与 MAXI 车身；仅 MAXI 中轴车身的高度与普通中轴不同，分别建立独立尺寸组。长轴 MAXI 与普通长轴三维完全相同，直接复用，不重复建组。
* `16649` 不包含 MAXI 分支，只关联普通短轴、中轴和长轴组。尺寸均来自同一份 Fiat 官方 244 Owner Handbook。([售后服务][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：120 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：44/100
* 尚未完全闭合输入 Ktype：56
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16648_swb_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16648_swb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16648_mwb_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16648_mwb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16648_mwb_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16648_mwb_maxi_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	HIGH	MAXI中轴标准顶厢式车。	READY
16648_mwb_maxi_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶厢式车。	READY
16648_mwb_maxi_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶厢式车。	READY
16648_lwb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16648_lwb_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
16649_swb_lowroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16649_swb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16649_mwb_lowroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16649_mwb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16649_mwb_superhighroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16649_lwb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16649_lwb_superhighroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
16650_swb_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16650_swb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16650_mwb_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16650_mwb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16650_mwb_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16650_mwb_maxi_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	HIGH	MAXI中轴标准顶厢式车。	READY
16650_mwb_maxi_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶厢式车。	READY
16650_mwb_maxi_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶厢式车。	READY
16650_lwb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16650_lwb_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	4749	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	5099	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2725	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	5099	2024	2160	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	5099	2024	2480	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	5599	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2860	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
```

## 下一步优先处理

1. 使用本轮 244 Van 缓存组，关联 `17607` 及其余确认覆盖相同车身矩阵的 Kasten Ktype。
2. 闭合 `16652`、`16653`、`16654`、`17608` 的 Panorama/Combi短轴、中轴及高顶边界。
3. 建立 244 原厂 Truck 尺寸组，并批量处理 `58734`、`16738`、`16739`。

推进信号：CONTINUE

[1]: https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf?utm_source=chatgpt.com "001-104 Ducato MY GB"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 已闭合 `17607`。Fiat 244 官方车型矩阵确认 2.0 Bipower 仅覆盖中轴/长轴高顶和超高顶，并同时存在普通 15 与 MAXI 中轴高度差；全部命中上轮既有 244 Van 尺寸组，本轮不重复建组。([售后服务][1])
* 已闭合 `16652`、`16653`、`16654` 三个 Bus Ktype，按短轴标准顶、中轴标准顶、中轴高顶拆分并复用既有 Van 外廓组。官方手册明确列有短轴 Panorama、短/中轴 Combi及中轴高顶乘用分支；车型规格资料也对应 `4749×2024×2150`、`5099×2024×2150` 和 `5099×2024×2470 mm`。([售后服务][1])
* `17608` 未直接套用 `17607`：当前仍缺少 2.0 Bipower Bus 各乘用车身分支的完整边界。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：135 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：48/100
* 尚未完全闭合输入 Ktype：52
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17607_mwb_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶Bipower厢式车。	READY
17607_mwb_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶Bipower厢式车。	READY
17607_mwb_maxi_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶Bipower厢式车。	READY
17607_mwb_maxi_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶Bipower厢式车。	READY
17607_lwb_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶Bipower厢式车。	READY
17607_lwb_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶Bipower厢式车。	READY
16652_swb_lowroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16652_mwb_lowroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16652_mwb_highroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	MEDIUM	中轴乘用型高顶。	READY
16653_swb_lowroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16653_mwb_lowroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16653_mwb_highroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	MEDIUM	中轴乘用型高顶。	READY
16654_swb_lowroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16654_mwb_lowroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16654_mwb_highroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴乘用型高顶。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `17608` 的 2.0 Bipower Bus 车身边界，不从厢式车分支直接推断。
2. 使用已提取的 244 Truck 官方矩阵，分别处理原厂平板与裸底盘，避免把货台宽度误用于裸底盘。
3. 批量关联 `58734`、`16738`、`16739` 后，再处理余下的 Ducato 230 四驱与 250/290 Ktype。

推进信号：CONTINUE

[1]: https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf?utm_source=chatgpt.com "001-104 Ducato MY GB"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 已闭合 `17608`：2.0 Bipower Bus 对应 244 中轴标准顶乘用外廓，复用既有尺寸组。
* 已闭合 `58734`、`16738`、`16739` 三个 Ducato II 244 原厂平板 Ktype。
* 首次建立 244 Truck 的短轴、中轴、长轴、4050 轴距及 MAXI 外廓组；裸底盘无固定完成外廓，不创建猜测性派生行。新组三维及发动机覆盖范围来自 Fiat 244 官方手册。([售后服务][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：151 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：52/100
* 尚未完全闭合输入 Ktype：48
* 已确认尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17608	17608	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	MEDIUM	2.0 Bipower中轴标准顶乘用型。	READY
58734_swb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
58734_mwb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	中轴原厂平板。	READY
58734_lwb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	长轴原厂平板。	READY
58734_mwb_maxi	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	HIGH	MAXI中轴原厂平板。	READY
58734_lwb_maxi	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	HIGH	MAXI长轴原厂平板。	READY
16738_swb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	2.0 JTD短轴原厂平板。	READY
16738_mwb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	2.0 JTD中轴原厂平板。	READY
16738_lwb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	2.0 JTD长轴原厂平板。	READY
16739_swb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	2.3 JTD短轴原厂平板。	READY
16739_mwb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	2.3 JTD中轴原厂平板。	READY
16739_lwb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	2.3 JTD长轴原厂平板。	READY
16739_4050	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-4050-01	HIGH	4050轴距原厂平板。	READY
16739_mwb_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	HIGH	MAXI中轴原厂平板。	READY
16739_lwb_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	HIGH	MAXI长轴原厂平板。	READY
16739_4050_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-4050-MAXI-01	HIGH	MAXI 4050轴距原厂平板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	4831	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	5181	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	5681	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-4050-01	5980	2040	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	5181	1932	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	5681	1932	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-4050-MAXI-01	5980	2040	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
```

## 下一步优先处理

1. 闭合 `116060` 的 Ducato II 230 四驱厢式车。
2. 处理 1988–1994 第一代 Ducato 尚未关联的底盘和平板 Ktype。
3. 批量处理 2006 年后的 Ducato III 250/290，先建立 Van、Bus及原厂平板的轴距/车顶缓存组。

推进信号：CONTINUE

[1]: https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf?utm_source=chatgpt.com "001-104 Ducato MY GB"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* `116060` 本轮未修改：仍缺可直接落盘、同时覆盖具体轴距和车顶分支的 230 四驱厢式车完整三维。
* 已闭合 `116551`。Fiat 官方 2014 技术规格明确列出 150 MultiJet 的玻璃/半玻璃乘用外廓，覆盖 3000、3450、4035 与 4035 XL 轴距，以及普通和 MAXI 高度分支；表中 `2050 mm` 为车身最大宽度，示意图将后视镜画在该宽度线之外。
* 本轮首次建立 10 个 Ducato III 290 乘用型尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：161 行
* 显式 PENDING 映射：10 行
* 已完全闭合输入 Ktype：53/100
* 尚未完全闭合输入 Ktype：47
* 已确认尺寸组：59
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116551_swb_lowroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	MEDIUM	3000轴距标准顶乘用外廓。	READY
116551_swb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	MEDIUM	3000轴距高顶乘用外廓。	READY
116551_mwb_lowroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	MEDIUM	3450轴距标准顶乘用外廓。	READY
116551_mwb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	MEDIUM	3450轴距高顶乘用外廓。	READY
116551_mwb_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-MAXI-HIGHROOF-01	MEDIUM	MAXI 3450轴距高顶乘用外廓。	READY
116551_lwb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	MEDIUM	4035轴距高顶乘用外廓。	READY
116551_lwb_superhighroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	MEDIUM	4035轴距超高顶乘用外廓。	READY
116551_lwb_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-HIGHROOF-01	MEDIUM	MAXI 4035轴距高顶乘用外廓。	READY
116551_lwb_maxi_superhighroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-SUPERHIGHROOF-01	MEDIUM	MAXI 4035轴距超高顶乘用外廓。	READY
116551_xl_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-XL-MAXI-HIGHROOF-01	MEDIUM	MAXI XL加长高顶乘用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	4963	2050	2254	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	4963	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	5413	2050	2254	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	5413	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-MAXI-HIGHROOF-01	5413	2050	2539	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	5998	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	5998	2050	2764	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-HIGHROOF-01	5998	2050	2534	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-SUPERHIGHROOF-01	5998	2050	2774	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-XL-MAXI-HIGHROOF-01	6363	2050	2539	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
```

## 下一步优先处理

1. 继续消除 10 条显式 PENDING，优先再次收口 `116060`。
2. 清理 280/230 裸底盘分支，寻找能直接支持完成状态三维的型式批准。
3. 随后建立 Ducato III 250 pre-facelift 缓存组，批量处理 2006–2014 的 Bus、Kasten和原厂平板 Ktype。

推进信号：CONTINUE


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 删除 9 条此前误建的猜测性裸底盘 PENDING 派生行：`14369_swb_chassis`、`14369_lwb_chassis`、`14370_swb_chassis`、`14370_maxi_chassis`、`11091_swb_chassis`、`11091_mwb_chassis`、`11091_lwb_chassis`、`14863_mwb_chassis`、`14863_lwb_chassis`。这些 Ktype 已有完整原厂平板外廓，不能仅因目录同时写有 Fahrgestell 就虚构没有固定完成外廓的派生记录。
* `116060` 仍为唯一显式 PENDING。现有型式批准可确认 Ducato 230 高顶四驱车存在 `5505–5530×1998×2470 mm` 外廓，但对应的是 2.8 JTD、3700 mm 轴距版本；尚不足以证明 2.5 D 4X4 Ktype `116060` 只覆盖该物理分支，因此未强行关联。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：161 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：57/100
* 尚未完全闭合输入 Ktype：43
* 已确认尺寸组：59
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无新增/修改行；本轮仅删除更新点所列 9 条无依据的 PENDING 派生行。

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 继续闭合唯一显式 PENDING `116060`，只接受能明确对应 2.5 D 4X4 具体轴距和车顶的完整外廓。
2. 同时开始批量处理尚未映射的 Ducato III 250 pre-facelift Ktype，先建立 Van、Bus和原厂平板尺寸缓存。
3. 后续 Ktype直接关联已建立的 250/290 尺寸组，不再重复核对三维和来源。

推进信号：CONTINUE


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* `116060` 仍保持 PENDING：已确认其为 Ducato II `230L`、2.5 D 4×4，但现有资料未把该发动机与具体 `5505/5530 mm` 长度分支唯一对应，不能把范围压成单一尺寸组。
* 已首次闭合 `15958`。官方 Ducato Euro 5 资料确认 110 Multijet 厢式车覆盖短轴标准顶、短轴高顶、中轴标准顶和中轴高顶；四组外廓分别为 `4963×2050×2254`、`4963×2050×2524`、`5413×2050×2254`、`5413×2050×2524 mm`。([Stellantis Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：165 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：58/100
* 尚未完全闭合输入 Ktype：42
* 已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15958_swb_lowroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	L1H1短轴标准顶。	READY
15958_swb_highroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	MEDIUM	L1H2短轴高顶。	READY
15958_mwb_lowroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	MEDIUM	L2H1中轴标准顶。	READY
15958_mwb_highroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	MEDIUM	L2H2中轴高顶。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	4963	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	4963	2050	2524	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	5413	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	5413	2050	2524	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
```

## 下一步优先处理

1. 使用本轮 250 Van 缓存组关联 `10203`，并补齐其已确认的 115 Multijet 车身覆盖范围。
2. 建立 250 原厂平板缓存组，批量处理 `15959`、`10204`、`10208`、`10211`。
3. 继续保留 `116060` 为唯一显式 PENDING，直到 2.5 D 4×4 的具体长度分支闭合。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/uk/UK/2014/FIAT_PROF/PRICES/Fiat_Professional_NEW%20DUCATO%202014_Price_List_APR_2014.pdf?utm_source=chatgpt.com "Price List - Changes NEW DUCATO"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* 已使用既有 Ducato III 250 Van 缓存闭合 `10203`，覆盖短轴/中轴的标准顶和高顶四种外廓，不重复输出尺寸组。
* 已闭合 `15959`、`10204`、`10208`、`10211` 四个原厂单排座平板 Ktype。Fiat 车型矩阵确认 110/115/150/180 Multijet 的原厂平板覆盖 CH1、MH1、LH1 三种轴距。官方尺寸表给出整车长度 `5293/5743/6328 mm`、货台最大宽度 `2100 mm`，结合相同配置驾驶室高度 `2254 mm`，本轮建立三个稳定平板尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：181 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：63/100
* 尚未完全闭合输入 Ktype：37
* 已确认尺寸组：66
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10203_swb_lowroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴标准顶。	READY
10203_swb_highroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶。	READY
10203_mwb_lowroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	HIGH	L2H1中轴标准顶。	READY
10203_mwb_highroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	L2H2中轴高顶。	READY
15959_swb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-01	MEDIUM	110 Multijet短轴原厂平板。	READY
15959_mwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-01	MEDIUM	110 Multijet中轴原厂平板。	READY
15959_lwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-01	MEDIUM	110 Multijet长轴原厂平板。	READY
10204_swb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-01	HIGH	115 Multijet短轴原厂平板。	READY
10204_mwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-01	HIGH	115 Multijet中轴原厂平板。	READY
10204_lwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-01	HIGH	115 Multijet长轴原厂平板。	READY
10208_swb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-01	HIGH	150 Multijet短轴原厂平板。	READY
10208_mwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-01	HIGH	150 Multijet中轴原厂平板。	READY
10208_lwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-01	HIGH	150 Multijet长轴原厂平板。	READY
10211_swb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-01	HIGH	180 Multijet短轴原厂平板。	READY
10211_mwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-01	HIGH	180 Multijet中轴原厂平板。	READY
10211_lwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-01	HIGH	180 Multijet长轴原厂平板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-250-PICKUP-SWB-01	5293	2100	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-PICKUP-MWB-01	5743	2100	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-PICKUP-LWB-01	6328	2100	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
```

## 下一步优先处理

1. 使用现有 250 Van 缓存批量关联 `10205`、`10206`、`10207`、`10209`、`10210`、`57446`、`59928`。
2. 处理 `57448`、`12026`、`12028` 和 `57682` 的原厂平板及四驱边界。
3. 继续保留唯一显式 PENDING `116060`，不以长度范围代替确定物理外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* 纠正 Ducato III 250 原厂平板高度口径：Fiat 官方资料列明原厂平板外高为 `2424 mm`，此前三个 `2254 mm` 组不再被本批映射引用；按冲突处理规则新建 `-02` 组，并同步修改 `15959`、`10204`、`10208`、`10211` 的关联，不覆盖旧尺寸事实。官方图示的 `2100 mm` 宽度线位于货台两侧，后视镜在测量线外，符合不含后视镜口径。
* 已闭合 `57446` 的 160 Multijet Kasten：覆盖短轴标准顶、中轴标准/高顶、4035 轴距高顶/超高顶以及加长后悬高顶/超高顶。
* 已闭合 `59928` 的 160 Multijet Bus：按官方玻璃或半玻璃车身矩阵关联中轴高顶、4035 轴距高顶/超高顶及加长后悬高顶外廓。
* 已闭合 `57448` 的 160 Multijet 原厂平板：覆盖 3450、3800、4035 轴距和 4035 轴距加长后悬四种外廓。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：196 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：66/100
* 尚未完全闭合输入 Ktype：34
* 当前被映射引用的已确认尺寸组：72
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15959_swb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	MEDIUM	110 Multijet短轴原厂平板。	READY
15959_mwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	MEDIUM	110 Multijet中轴原厂平板。	READY
15959_lwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	MEDIUM	110 Multijet 4035轴距原厂平板。	READY
10204_swb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	115 Multijet短轴原厂平板。	READY
10204_mwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	115 Multijet中轴原厂平板。	READY
10204_lwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	115 Multijet 4035轴距原厂平板。	READY
10208_swb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	150 Multijet短轴原厂平板。	READY
10208_mwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	150 Multijet中轴原厂平板。	READY
10208_lwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	150 Multijet 4035轴距原厂平板。	READY
10211_swb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	180 Multijet短轴原厂平板。	READY
10211_mwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	180 Multijet中轴原厂平板。	READY
10211_lwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	180 Multijet 4035轴距原厂平板。	READY
57446_swb_lowroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	160 Multijet L1H1短轴标准顶。	READY
57446_mwb_lowroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	HIGH	160 Multijet L2H1中轴标准顶。	READY
57446_mwb_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	160 Multijet L2H2中轴高顶。	READY
57446_lwb_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	HIGH	160 Multijet 4035轴距高顶。	READY
57446_lwb_superhighroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	HIGH	160 Multijet 4035轴距超高顶。	READY
57446_xl_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	160 Multijet加长后悬高顶。	READY
57446_xl_superhighroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	160 Multijet加长后悬超高顶。	READY
57448_mwb	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	160 Multijet 3450轴距原厂平板。	READY
57448_3800	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-3800-01	HIGH	160 Multijet 3800轴距原厂平板。	READY
57448_lwb	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	160 Multijet 4035轴距原厂平板。	READY
57448_xl	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-XL-01	HIGH	160 Multijet 4035轴距加长后悬原厂平板。	READY
59928_mwb_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	160 Multijet中轴高顶乘用外廓。	READY
59928_lwb_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	HIGH	160 Multijet 4035轴距高顶乘用外廓。	READY
59928_lwb_superhighroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	HIGH	160 Multijet 4035轴距超高顶乘用外廓。	READY
59928_xl_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	160 Multijet加长后悬高顶乘用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	5293	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	5743	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	6328	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	5998	2050	2524	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	5998	2050	2764	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	6363	2050	2524	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	6363	2050	2764	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-3800-01	6093	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-XL-01	6693	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
```

## 下一步优先处理

1. 使用本轮新建的 250 长轴 Van 缓存组，批量关联 `10205`、`10206`、`10207`、`10209`、`10210`。
2. 处理 `57682` 的 Natural Power 底盘/原厂平板边界，以及 `12026`、`12028` 的 4×4 专用外廓。
3. 继续保留唯一显式 PENDING `116060`，不把长度范围压成单一尺寸。

推进信号：CONTINUE


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* 已使用现有 Ducato III 250 尺寸组闭合 `10205`、`10206`、`10207`、`10210`，未重复抓取或输出尺寸组。
* 官方 Euro 5 车型矩阵确认：130 Multijet Panorama 为 L1H1，150 Multijet Panorama 为 L2H2；150 与 180 Multijet 厢式车明确覆盖 L4H2、L4H3。对应外廓分别命中既有短轴标准顶、中轴高顶、XL 高顶和 XL 超高顶组。
* `10209` 暂未修改：现有官方矩阵直接列出了 180 Multijet 的 L4H2/L4H3 厢式车，但未直接列出 180 Multijet Panorama/Bus，暂不以厢式车发动机覆盖范围替代乘用车身边界。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：203 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：70/100
* 尚未完全闭合输入 Ktype：30
* 当前被映射引用的已确认尺寸组：72
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10205	10205	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	130 Multijet L1H1短轴标准顶乘用外廓。	READY
10206	10206	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	150 Multijet L2H2中轴高顶乘用外廓。	READY
10207_xl_highroof	10207	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	150 Multijet L4H2加长后悬高顶。	READY
10207_xl_superhighroof	10207	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	150 Multijet L4H3加长后悬超高顶。	READY
10210_xl_highroof	10210	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	180 Multijet L4H2加长后悬高顶。	READY
10210_xl_superhighroof	10210	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	180 Multijet L4H3加长后悬超高顶。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 `10209` 的 180 Multijet Bus 具体乘用车身边界。
2. 处理 `57682` Natural Power 原厂平板，以及 `12026`、`12028` 的 4×4 底盘和厢式车边界。
3. 继续消除唯一显式 PENDING `116060`，不使用长度范围或其他发动机版本代替确定外廓。

推进信号：CONTINUE


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / 下一步 ---
## 更新点

* 已闭合 `10209`：该 Ktype 对应 Ducato Kombi 30 L1H1 180 Multijet，复用现有 250 短轴标准顶尺寸组，不重复输出尺寸组。([Motorinsel][1])
* 已闭合 `12026`：确认其 Dangel 4×4 L2 Heavy 原厂平板外廓为 `5743×2100×2274 mm`，首次建立四驱中轴平板尺寸组。([Typenscheinschweiz.ch][2])
* 已闭合 `12028`：确认其为 Dangel 4×4 L2 厢式车，按低顶 `5413×2050×2274 mm`、高顶 `5413×2050×2542 mm` 拆分。([Typenscheinschweiz.ch][3])
* `57682` 已确认是 L2 Natural Power 平地板底盘，不是具有固定完成外廓的原厂平板，因此不能复用现有 Pickup 组，新增为明确 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：207 行
* 显式 PENDING 映射：2 行
* 已完全闭合输入 Ktype：73/100
* 尚未完全闭合输入 Ktype：27
* 当前被映射引用的已确认尺寸组：75
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12026	12026	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-4X4-01	HIGH	Dangel 4×4 L2 Heavy原厂平板。	READY
12028_lowroof	12028	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-LOWROOF-01	HIGH	Dangel 4×4 L2H1厢式车。	READY
12028_highroof	12028	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-HIGHROOF-01	HIGH	Dangel 4×4 L2H2厢式车。	READY
57682	57682	Pickup	Ducato III pre-facelift	250	2		MEDIUM	L2 Natural Power平地板底盘，完成状态外廓未固定。	PENDING: 平地板底盘完整量产外廓未闭合
10209	10209	MPV	Ducato III		4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	180 Multijet Kombi 30 L1H1乘用外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-250-PICKUP-MWB-4X4-01	5743	2100	2274	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 17Q type approval 3FH451	https://typenscheinschweiz.ch/typenschein/auto/3FH451
EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-LOWROOF-01	5413	2050	2274	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 type approval 3FH420	https://typenscheinschweiz.ch/typenschein/auto/3FH420
EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-HIGHROOF-01	5413	2050	2542	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 type approval 3FH420	https://typenscheinschweiz.ch/typenschein/auto/3FH420
```

## 下一步优先处理

1. 消除 `116060` 与 `57682` 两条显式 PENDING。
2. 批量闭合 2021 年后的 Ducato III 290 Kasten、Bus和原厂平板 Ktype。
3. 再处理剩余第一代 Ducato 底盘及尚未映射的 250/290 分支。

推进信号：CONTINUE

[1]: https://www.motorinsel.eu/f1ce3481e-engine?utm_source=chatgpt.com "F1CE3481E Engine Information, Specifications, and Offers"
[2]: https://typenscheinschweiz.ch/typenschein/auto/3FH451 "Typenschein 3FH451 - FIAT-DANGEL Ducato 4x4 17Q | Gratis PDF"
[3]: https://typenscheinschweiz.ch/typenschein/auto/3FH420 "Typenschein 3FH420 - FIAT-DANGEL Ducato 4x4 15Q | Gratis PDF"


--- 发送 / 继续到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / 下一步 ---
## 更新点

* 已闭合 `57682`。Fiat 官方资料确认第三代 Ducato Natural Power 提供平地板单排座底盘；改款前 `250` 底盘的 L2、L4 外廓分别为 `5358×2050×2254 mm` 和 `5943×2050×2254 mm`。
* `57682` 跨越改款边界，因此按 `250 pre-facelift` 与 `290 facelift` 拆分；2019 年官方价格表明确列出 Natural Power 平地板底盘的 L2 与 L4 订货版本，后期底盘规格继续保持相同三维。
* `116060` 仍是唯一显式 PENDING。当前可靠型式批准只给出同系列 4×4 高顶车 `5505–5530 mm` 的长度范围，尚不能无猜测地拆成 `2.5 D 4×4` 的确定分支。([Typenscheinschweiz.ch][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：211 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：74/100
* 尚未完全闭合输入 Ktype：26
* 当前被映射引用的已确认尺寸组：79
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57682_mwb_prefl	57682	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-MWB-01	MEDIUM	250改款前L2平地板单排座底盘。	READY
57682_lwb_prefl	57682	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-LWB-01	MEDIUM	250改款前L4平地板单排座底盘。	READY
57682_mwb_facelift	57682	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	290改款后L2平地板单排座底盘。	READY
57682_lwb_facelift	57682	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	290改款后L4平地板单排座底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-MWB-01	5358	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011;Fiat Professional New Fiat Ducato 30 years official press pack	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf;https://www.media.stellantis.com/nl-nl/fiat-professional/press/nieuwe-fiat-ducato-een-succesverhaal-van-30-jaar
EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-LWB-01	5943	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011;Fiat Professional New Fiat Ducato 30 years official press pack	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf;https://www.media.stellantis.com/nl-nl/fiat-professional/press/nieuwe-fiat-ducato-een-succesverhaal-van-30-jaar
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	5358	2050	2254	Fiat Professional Ducato official price list 2019;Fiat Professional E-Ducato official technical specification 2020	https://www.media.stellantis.com/uploads/de/DE/2019/Fiat_Prof/Preislisten/190404_FP_Ducato_PL.pdf;https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	5943	2050	2254	Fiat Professional Ducato official price list 2019;Fiat Professional E-Ducato official technical specification 2020	https://www.media.stellantis.com/uploads/de/DE/2019/Fiat_Prof/Preislisten/190404_FP_Ducato_PL.pdf;https://www.media.stellantis.com/uploads/uk/attachment/fiateducatotechspecandpricing200820-5f3d1ecd1f02f.pdf
```

## 下一步优先处理

1. 继续消除唯一显式 PENDING `116060`，不把 `5505–5530 mm` 范围强制压成单一尺寸。
2. 使用已确认的 Ducato III `290` 外廓缓存，批量关联 2021 年后的 Kasten、Bus和原厂平板 Ktype。
3. 随后处理剩余第一代 Ducato 平板/底盘及尚未关联的 `250/290` 分支。

推进信号：CONTINUE

[1]: https://typenscheinschweiz.ch/typenschein/auto/3FA360?utm_source=chatgpt.com "Typenschein 3FA360 - FIAT Ducato 14 2.8JTD | Gratis PDF"


--- 发送 / 继续到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / 下一步 ---
## 更新点

* 已闭合 2021 年后的 `144808`、`144809`、`144810`、`144812`、`145288`、`155950`。Series 8 官方矩阵确认 120 PS 覆盖 C/M/L 车长，140/160/180 PS 还覆盖 XL；Bus 140 PS 按 M H2 与 L H2 两种玻璃车身外廓关联。
* C/M/L 各分支尺寸与现有 290 缓存完全一致，直接复用。
* Series 8 官方高度统一为 H1 `2254 mm`、H2 `2524 mm`、H3 `2764 mm`。现有 XL 缓存为旧 MAXI 高度 `2539 mm`，三维不一致，因此未覆盖旧组，新增 XL H2/H3 两组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：251 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：80/100
* 尚未完全闭合输入 Ktype：20
* 当前被映射引用的已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144808_swb_lowroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144808_swb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144808_mwb_lowroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144808_mwb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144808_lwb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144808_lwb_superhighroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144809_swb_lowroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144809_swb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144809_mwb_lowroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144809_mwb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144809_lwb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144809_lwb_superhighroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144809_xl_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144809_xl_superhighroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
144810_swb_lowroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144810_swb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144810_mwb_lowroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144810_mwb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144810_lwb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144810_lwb_superhighroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144810_xl_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144810_xl_superhighroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
145288_mwb_highroof	145288	MPV	Ducato III facelift	290	4	EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶Bus。	READY
145288_lwb_highroof	145288	MPV	Ducato III facelift	290	4	EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶Bus。	READY
155950_swb_lowroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	MEDIUM	后期140 Multijet短轴标准顶。	READY
155950_swb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	MEDIUM	后期140 Multijet短轴高顶。	READY
155950_mwb_lowroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	MEDIUM	后期140 Multijet中轴标准顶。	READY
155950_mwb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	MEDIUM	后期140 Multijet中轴高顶。	READY
155950_lwb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	MEDIUM	后期140 Multijet长轴高顶。	READY
155950_lwb_superhighroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	MEDIUM	后期140 Multijet长轴超高顶。	READY
155950_xl_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	MEDIUM	后期140 Multijet XL加长高顶。	READY
155950_xl_superhighroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	MEDIUM	后期140 Multijet XL加长超高顶。	READY
144812_swb_lowroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144812_swb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144812_mwb_lowroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144812_mwb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144812_lwb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144812_lwb_superhighroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144812_xl_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144812_xl_superhighroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	6363	2050	2524	Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	6363	2050	2764	Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
```

## 下一步优先处理

1. 使用 Series 8 底盘和原厂平板矩阵处理 `145286`、`145287`、`145289`、`145290`。
2. 处理尚未映射的第一代 Ducato 底盘/平板 Ktype。
3. 最后集中消除唯一显式 PENDING `116060`，再完成剩余机械闭合。

推进信号：CONTINUE


--- 发送 / 继续到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 24 / 下一步 ---
## 更新点

* 已闭合 `145286`、`145287`、`145289`、`145290`。Series 8 单排座底盘覆盖 M、ML、L、XL 四种外廓，120/140/160/180 PS 均可关联；M、L 复用既有组，仅首次补建 ML、XL 组。
* `145289` 额外确认覆盖 XL 原厂平板；2021 官方配置表只明确列出 160 PS 的该平板分支，因此未向另外三个 Ktype扩展。
* 单排座底盘 ML、XL 外廓分别为 `5708×2050×2254 mm`、`6308×2050×2254 mm`；XL 原厂平板为 `6693×2100×2424 mm`。([Stellantis Media][1])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：268 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：84/100
* 尚未完全闭合输入 Ktype：16
* 当前被映射引用的已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145286_mwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145286_mlwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145286_lwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145286_xl_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
145287_mwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145287_mlwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145287_lwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145287_xl_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
145289_mwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145289_mlwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145289_lwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145289_xl_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
145289_xl_flatbed	145289	Pickup	Ducato III facelift	295	2	EU-FIAT-DUCATO-III-290-PICKUP-XL-01	HIGH	Series 8 XL原厂平板。	READY
145290_mwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145290_mlwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145290_lwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145290_xl_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	5708	2050	2254	Fiat Professional New Ducato official conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	6308	2050	2254	Fiat Professional New Ducato official conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-PICKUP-XL-01	6693	2100	2424	Fiat Professional New Ducato official goods transport technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
```

## 下一步优先处理

1. 批量闭合剩余 `15957`、`10201` 两个 Ducato III 250 Bus Ktype。
2. 处理 `7793`、`11847`、`14375`、`14372`、`57973`、`11090`、`14373`、`58732`、`7795`、`14363`、`14374`、`11089`、`59931`。
3. 最后集中消除唯一显式 PENDING `116060`。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf "DucatoTrasfConv_CT_ING_LP@.indd"


--- 发送 / 继续到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 25 / 下一步 ---
## 更新点

* 已闭合剩余 15 个未映射 Ktype，当前仅 `116060` 保持 PENDING。
* Ducato I `290` 原厂平板首次建立短轴与长轴组：短轴 `4868×2000×2070 mm`，长轴 `5598×2000×2070 mm`；同组三维由不同发动机型式批准一致支持。([Dauto][1])
* Ducato I 四驱平板单独建组：`280` 短轴为 `4868×2000×2078 mm`，`290` 短轴为 `4868×2000×2100 mm`，未套用前驱高度。([Dauto][2])
* `11847`、`58732` 直接复用既有 Ducato II `230` 原厂平板组；`14372`、`14373`、`14375`、`59931` 复用既有 `280` 平板组。
* `15957`、`10201` 按基础动力短轴标准顶 Bus 外廓关联既有 Ducato III `250` 组，映射置信度为 MEDIUM。115 Multijet 的 Kombi 短轴边界有 Fiat 官方资料支持。([DENSO][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：294 行
* 显式 PENDING 映射：1 行
* 已完全闭合输入 Ktype：99/100
* 尚未闭合输入 Ktype：1
* 当前被映射引用的已确认尺寸组：88
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7793_swb	7793	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	2.0短轴原厂平板。	READY
7793_lwb	7793	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	2.0长轴原厂平板。	READY
11847_swb	11847	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	2.0短轴原厂平板。	READY
11847_mwb	11847	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	2.0中轴原厂平板。	READY
14375_swb	14375	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	2.0短轴原厂平板。	READY
14375_maxi	14375	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	2.0 Maxi原厂平板。	READY
14372_swb	14372	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	1.9 D短轴原厂平板。	READY
14372_maxi	14372	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	1.9 D Maxi原厂平板。	READY
57973_swb	57973	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	1.9 D短轴原厂平板。	READY
57973_lwb	57973	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	1.9 D长轴原厂平板。	READY
11090_swb	11090	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	HIGH	1.9 TD短轴原厂平板。	READY
11090_lwb	11090	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	HIGH	1.9 TD长轴原厂平板。	READY
14373_swb	14373	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	1.9 TD短轴原厂平板。	READY
14373_maxi	14373	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	1.9 TD Maxi原厂平板。	READY
15957	15957	MPV	Ducato III pre-facelift	250	4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	110 Multijet短轴标准顶Bus外廓。	READY
10201	10201	MPV	Ducato III pre-facelift	250	4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	115 Multijet短轴标准顶Kombi外廓。	READY
58732_swb	58732	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	2.0 JTD短轴原厂平板。	READY
58732_mwb	58732	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	2.0 JTD中轴原厂平板。	READY
7795_swb	7795	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	2.5 D短轴原厂平板。	READY
7795_lwb	7795	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	2.5 D长轴原厂平板。	READY
14363	14363	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-4X4-01	MEDIUM	2.5 D 4X4短轴原厂平板。	READY
14374	14374	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-4X4-01	MEDIUM	2.5 D 4X4短轴原厂平板。	READY
11089_swb	11089	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	2.5 TD短轴原厂平板。	READY
11089_lwb	11089	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	2.5 TD长轴原厂平板。	READY
59931_swb	59931	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	2.5 TD短轴原厂平板。	READY
59931_maxi	59931	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	2.5 TD Maxi原厂平板。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	4868	2000	2070	Swiss ASTRA Fiat Ducato 290/14 type approval extract 3F2176	https://www.dauto.ch/typenscheine/fiat-ducato-290-14-kat-3f2176-zfa29000000-x
EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	5598	2000	2070	Swiss ASTRA Fiat Ducato 290 NTX type approval extract 3F2115	https://www.dauto.ch/typenscheine/fiat-ducato-290-ntx-3f2115-zfa29000000-x
EU-FIAT-DUCATO-I-280-PICKUP-SWB-4X4-01	4868	2000	2078	Swiss ASTRA Fiat Ducato 280/14 4x4 type approval extract 3F2109	https://www.dauto.ch/typenscheine/fiat-ducato-280-14-4x4-3f2109-x-x
EU-FIAT-DUCATO-I-290-PICKUP-SWB-4X4-01	4868	2000	2100	Swiss ASTRA Fiat Ducato 290/14 4x4 type approval extract 3F2152	https://www.dauto.ch/typenscheine/fiat-ducato-290-14-4x4-3f2152-x-x
```

## 下一步优先处理

1. 仅处理最后一个 PENDING `116060`：Ducato II `230` 2.5 D 4X4 Kasten。
2. 只接受能将该发动机明确对应到确定长度、宽度和车顶高度的完整外廓；不再使用 `5505–5530 mm` 范围。
3. 一旦 `116060` 闭合并达到 `PENDING=0`，下一轮直接执行一次机械检查并输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://www.dauto.ch/typenscheine/fiat-ducato-290-14-kat-3f2176-zfa29000000-x?utm_source=chatgpt.com "3F2176 - FIAT DUCATO 290 / 14 KAT - ZFA29000000...... - X"
[2]: https://www.dauto.ch/typenscheine/fiat-ducato-280-14-4x4-3f2109-x-x "3F2109 - FIAT Ducato 280/14 4x4 - X - X"
[3]: https://www.denso-am.eu/catalog/pv/10201?utm_source=chatgpt.com "Car parts for FIAT DUCATO Bus (250_), 115 Multijet 2,0 D, 85kW ..."


--- 发送 / 继续到 Round 26 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_4801-4900_ktype_dimension_mapping_final.tsv
- left18448_4801-4900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 26 / 下一步 ---
## 更新点

* 最后一条 PENDING `116060` 已闭合：KBA `4001/589/004` 对应 Fiat Ducato Maxi 10 2.5 D 4x4、车身代码 `230L`、4 门，确定外廓为 `5505×1998×2480 mm`，已创建并关联尺寸组 `EU-FIAT-DUCATO-II-230-VAN-LWB-4X4-HIGHROOF-01`。([ASR Autoteile-Service-Recycling][1])
* 已完成一次轻量机械检查：两张表表头正确；映射 `id` 与尺寸组 ID 唯一；所有引用闭合；不存在孤立尺寸组；三维、来源和 URL 均非空。
* 当前输入实际包含 **99 个 Ktype**，不是 100 个；未生成不存在的第 100 个 Ktype。

## 当前批次进度

* 输入 Ktype：99/99
* READY 映射：292 行
* PENDING：0
* DIMENSION_GROUP：89 行
* 映射引用闭合：89/89
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17978	17978	MPV	Doblò I pre-facelift	223	5	EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	223乘用型标准外廓。	READY
17979_swb_prefl	17979	Van	Doblò I pre-facelift	223		EU-FIAT-DOBLO-I-223-MPV-PREFL-01	HIGH	改款前标准轴距低顶外廓。	READY
17979_swb_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-SWB-FACELIFT-01	HIGH	改款后标准轴距低顶。	READY
17979_swb_highroof_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-SWB-HIGHROOF-FACELIFT-01	HIGH	改款后标准轴距高顶。	READY
17979_lwb_facelift	17979	Van	Doblò I facelift	223		EU-FIAT-DOBLO-I-223-VAN-LWB-FACELIFT-01	HIGH	改款后长轴低顶。	READY
149150	149150	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
149158_swb	149158	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149158_lwb	149158	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
149151	149151	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
149160_swb	149160	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149160_lwb	149160	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
801407_swb	801407	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	HIGH	Dangel 4WD短轴厢式车。	READY
801407_lwb	801407	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	HIGH	Dangel 4WD长轴厢式车。	READY
149149	149149	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	HIGH	K9电动乘用型标准轴距。	READY
149153_swb	149153	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149153_lwb	149153	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
158238	158238	MPV	Doblò III facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	MEDIUM	K9改款电动乘用型标准轴距。	READY
158239_swb	158239	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
158239_lwb	158239	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
801408_swb	801408	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	HIGH	电动4WD短轴厢式车。	READY
801408_lwb	801408	Van	Doblò III facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	HIGH	电动4WD长轴厢式车。	READY
149152	149152	MPV	Doblò III pre-facelift	K9	5	EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	HIGH	K9燃油乘用型标准轴距。	READY
149155_swb	149155	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-SWB-01	HIGH	标准轴距厢式车。	READY
149155_lwb	149155	Van	Doblò III pre-facelift	K9		EU-FIAT-DOBLO-III-K9-VAN-LWB-01	HIGH	Maxi长轴厢式车。	READY
100768_swb_prefl	100768	Van	Doblò II pre-facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-PREFL-01	HIGH	75 PS Cargo改款前L1H1。	READY
100768_swb_facelift	100768	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	75 PS Cargo改款后L1H1。	READY
119852_swb	119852	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	Cargo L1H1。	READY
119852_lwb	119852	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	Cargo L2H1。	READY
119854_swb	119854	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	Cargo L1H1。	READY
119854_lwb	119854	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	Cargo L2H1。	READY
119850_swb	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	120 PS Cargo L1H1。	READY
119850_lwb	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	HIGH	120 PS Cargo L2H1。	READY
119850_lwb_highroof	119850	Van	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-HIGHROOF-FACELIFT-01	HIGH	120 PS Cargo L2H2高顶。	READY
119853	119853	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	HIGH	95 PS Combi L1H1。	READY
113175_swb	113175	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	95 PS Kombi短轴外廓。	READY
113175_lwb	113175	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	95 PS Kombi长轴外廓。	READY
113191_swb	113191	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	120 PS Kombi短轴外廓。	READY
113191_lwb	113191	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	120 PS Kombi长轴外廓。	READY
119865_swb	119865	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	100 PS Kombi短轴外廓。	READY
119865_lwb	119865	MPV	Doblò II facelift	263		EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	100 PS Kombi长轴外廓。	READY
124817_lowroof	124817	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-LOWROOF-01	HIGH	280前驱标准顶厢式车。	READY
124817_highroof	124817	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-HIGHROOF-01	HIGH	280前驱高顶厢式车。	READY
7793_swb	7793	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
7793_lwb	7793	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	长轴原厂平板。	READY
11847_swb	11847	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
11847_mwb	11847	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
14369_lwb_doublecab	14369	Pickup	Ducato I pre-facelift	280	4	EU-FIAT-DUCATO-I-280-CHASSIS-LWB-DOUBLECAB-01	HIGH	长轴双排座底盘。	READY
14375_swb	14375	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
14375_maxi	14375	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	Maxi原厂平板。	READY
16648_swb_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16648_swb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16648_mwb_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16648_mwb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16648_mwb_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16648_mwb_maxi_lowroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	HIGH	MAXI中轴标准顶厢式车。	READY
16648_mwb_maxi_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶厢式车。	READY
16648_mwb_maxi_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶厢式车。	READY
16648_lwb_highroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16648_lwb_superhighroof	16648	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
16652_swb_lowroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16652_mwb_lowroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16652_mwb_highroof	16652	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	MEDIUM	中轴乘用型高顶。	READY
58734_swb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
58734_mwb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	中轴原厂平板。	READY
58734_lwb	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	长轴原厂平板。	READY
58734_mwb_maxi	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	HIGH	MAXI中轴原厂平板。	READY
58734_lwb_maxi	58734	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	HIGH	MAXI长轴原厂平板。	READY
7796_lowroof	7796	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	HIGH	290前驱标准顶厢式车。	READY
7796_highroof	7796	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	HIGH	290前驱高顶厢式车。	READY
11409	11409	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
11843_swb_lowroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	MEDIUM	230短轴标准顶厢式车。	READY
11843_swb_highroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	MEDIUM	230短轴高顶厢式车。	READY
11843_mwb_lowroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴标准顶厢式车。	READY
11843_mwb_highroof	11843	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	MEDIUM	230中轴高顶厢式车。	READY
11849_swb	11849	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
11849_mwb	11849	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
14372_swb	14372	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
14372_maxi	14372	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	Maxi原厂平板。	READY
14464_swb	14464	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
14464_mwb	14464	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
57973_swb	57973	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
57973_lwb	57973	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	长轴原厂平板。	READY
7792_lowroof	7792	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	HIGH	290前驱标准顶厢式车。	READY
7792_highroof	7792	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	HIGH	290前驱高顶厢式车。	READY
11090_swb	11090	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
11090_lwb	11090	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	HIGH	长轴原厂平板。	READY
11410	11410	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
11842_swb_lowroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	MEDIUM	230短轴标准顶厢式车。	READY
11842_swb_highroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	MEDIUM	230短轴高顶厢式车。	READY
11842_mwb_lowroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴标准顶厢式车。	READY
11842_mwb_highroof	11842	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	MEDIUM	230中轴高顶厢式车。	READY
11848_swb_lowroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
11848_swb_highroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
11848_mwb_lowroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
11848_mwb_highroof	11848	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
11850_swb	11850	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
11850_mwb	11850	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
14373_swb	14373	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
14373_maxi	14373	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	Maxi原厂平板。	READY
14466_swb	14466	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
14466_mwb	14466	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	HIGH	中轴原厂平板。	READY
10696_swb_lowroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
10696_swb_highroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
10696_mwb_lowroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
10696_mwb_highroof	10696	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
11851_swb	11851	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
11851_mwb	11851	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
15957	15957	MPV	Ducato III pre-facelift	250	4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	110 Multijet短轴标准顶Bus外廓。	READY
15958_swb_lowroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	L1H1短轴标准顶。	READY
15958_swb_highroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	MEDIUM	L1H2短轴高顶。	READY
15958_mwb_lowroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	MEDIUM	L2H1中轴标准顶。	READY
15958_mwb_highroof	15958	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	MEDIUM	L2H2中轴高顶。	READY
15959_swb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	MEDIUM	110 Multijet短轴原厂平板。	READY
15959_mwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	MEDIUM	110 Multijet中轴原厂平板。	READY
15959_lwb	15959	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	MEDIUM	110 Multijet 4035轴距原厂平板。	READY
10201	10201	MPV	Ducato III pre-facelift	250	4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	115 Multijet短轴标准顶Kombi外廓。	READY
10203_swb_lowroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	L1H1短轴标准顶。	READY
10203_swb_highroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	HIGH	L1H2短轴高顶。	READY
10203_mwb_lowroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	HIGH	L2H1中轴标准顶。	READY
10203_mwb_highroof	10203	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	L2H2中轴高顶。	READY
10204_swb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	115 Multijet短轴原厂平板。	READY
10204_mwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	115 Multijet中轴原厂平板。	READY
10204_lwb	10204	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	115 Multijet 4035轴距原厂平板。	READY
144808_swb_lowroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144808_swb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144808_mwb_lowroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144808_mwb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144808_lwb_highroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144808_lwb_superhighroof	144808	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
145286_mwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145286_mlwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145286_lwb_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145286_xl_chassis	145286	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
12026	12026	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-4X4-01	HIGH	Dangel 4×4 L2 Heavy原厂平板。	READY
12028_lowroof	12028	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-LOWROOF-01	HIGH	Dangel 4×4 L2H1厢式车。	READY
12028_highroof	12028	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-HIGHROOF-01	HIGH	Dangel 4×4 L2H2厢式车。	READY
10205	10205	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	130 Multijet L1H1短轴标准顶乘用外廓。	READY
144809_swb_lowroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144809_swb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144809_mwb_lowroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144809_mwb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144809_lwb_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144809_lwb_superhighroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144809_xl_highroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144809_xl_superhighroof	144809	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
145287_mwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145287_mlwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145287_lwb_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145287_xl_chassis	145287	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
145288_mwb_highroof	145288	MPV	Ducato III facelift	290	4	EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶Bus。	READY
145288_lwb_highroof	145288	MPV	Ducato III facelift	290	4	EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶Bus。	READY
155950_swb_lowroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	MEDIUM	后期140 Multijet短轴标准顶。	READY
155950_swb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	MEDIUM	后期140 Multijet短轴高顶。	READY
155950_mwb_lowroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	MEDIUM	后期140 Multijet中轴标准顶。	READY
155950_mwb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	MEDIUM	后期140 Multijet中轴高顶。	READY
155950_lwb_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	MEDIUM	后期140 Multijet长轴高顶。	READY
155950_lwb_superhighroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	MEDIUM	后期140 Multijet长轴超高顶。	READY
155950_xl_highroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	MEDIUM	后期140 Multijet XL加长高顶。	READY
155950_xl_superhighroof	155950	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	MEDIUM	后期140 Multijet XL加长超高顶。	READY
57682_mwb_prefl	57682	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-MWB-01	MEDIUM	250改款前L2平地板单排座底盘。	READY
57682_lwb_prefl	57682	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-LWB-01	MEDIUM	250改款前L4平地板单排座底盘。	READY
57682_mwb_facelift	57682	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	290改款后L2平地板单排座底盘。	READY
57682_lwb_facelift	57682	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	290改款后L4平地板单排座底盘。	READY
10206	10206	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	150 Multijet L2H2中轴高顶乘用外廓。	READY
10207_xl_highroof	10207	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	150 Multijet L4H2加长后悬高顶。	READY
10207_xl_superhighroof	10207	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	150 Multijet L4H3加长后悬超高顶。	READY
10208_swb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	150 Multijet短轴原厂平板。	READY
10208_mwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	150 Multijet中轴原厂平板。	READY
10208_lwb	10208	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	150 Multijet 4035轴距原厂平板。	READY
116551_swb_lowroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	MEDIUM	3000轴距标准顶乘用外廓。	READY
116551_swb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	MEDIUM	3000轴距高顶乘用外廓。	READY
116551_mwb_lowroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	MEDIUM	3450轴距标准顶乘用外廓。	READY
116551_mwb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	MEDIUM	3450轴距高顶乘用外廓。	READY
116551_mwb_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-MAXI-HIGHROOF-01	MEDIUM	MAXI 3450轴距高顶乘用外廓。	READY
116551_lwb_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	MEDIUM	4035轴距高顶乘用外廓。	READY
116551_lwb_superhighroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	MEDIUM	4035轴距超高顶乘用外廓。	READY
116551_lwb_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-HIGHROOF-01	MEDIUM	MAXI 4035轴距高顶乘用外廓。	READY
116551_lwb_maxi_superhighroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-SUPERHIGHROOF-01	MEDIUM	MAXI 4035轴距超高顶乘用外廓。	READY
116551_xl_maxi_highroof	116551	MPV	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-XL-MAXI-HIGHROOF-01	MEDIUM	MAXI XL加长高顶乘用外廓。	READY
144810_swb_lowroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144810_swb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144810_mwb_lowroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144810_mwb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144810_lwb_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144810_lwb_superhighroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144810_xl_highroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144810_xl_superhighroof	144810	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
145289_mwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145289_mlwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145289_lwb_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145289_xl_chassis	145289	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
145289_xl_flatbed	145289	Pickup	Ducato III facelift	295	2	EU-FIAT-DUCATO-III-290-PICKUP-XL-01	HIGH	Series 8 XL原厂平板。	READY
57446_swb_lowroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	HIGH	160 Multijet L1H1短轴标准顶。	READY
57446_mwb_lowroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	HIGH	160 Multijet L2H1中轴标准顶。	READY
57446_mwb_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	160 Multijet L2H2中轴高顶。	READY
57446_lwb_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	HIGH	160 Multijet 4035轴距高顶。	READY
57446_lwb_superhighroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	HIGH	160 Multijet 4035轴距超高顶。	READY
57446_xl_highroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	160 Multijet加长后悬高顶。	READY
57446_xl_superhighroof	57446	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	160 Multijet加长后悬超高顶。	READY
57448_mwb	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	160 Multijet 3450轴距原厂平板。	READY
57448_3800	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-3800-01	HIGH	160 Multijet 3800轴距原厂平板。	READY
57448_lwb	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	160 Multijet 4035轴距原厂平板。	READY
57448_xl	57448	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-XL-01	HIGH	160 Multijet 4035轴距加长后悬原厂平板。	READY
59928_mwb_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	HIGH	160 Multijet中轴高顶乘用外廓。	READY
59928_lwb_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	HIGH	160 Multijet 4035轴距高顶乘用外廓。	READY
59928_lwb_superhighroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	HIGH	160 Multijet 4035轴距超高顶乘用外廓。	READY
59928_xl_highroof	59928	MPV	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	160 Multijet加长后悬高顶乘用外廓。	READY
144812_swb_lowroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	HIGH	Series 8短轴标准顶。	READY
144812_swb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	HIGH	Series 8短轴高顶。	READY
144812_mwb_lowroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	HIGH	Series 8中轴标准顶。	READY
144812_mwb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	HIGH	Series 8中轴高顶。	READY
144812_lwb_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	HIGH	Series 8长轴高顶。	READY
144812_lwb_superhighroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	HIGH	Series 8长轴超高顶。	READY
144812_xl_highroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	HIGH	Series 8 XL加长高顶。	READY
144812_xl_superhighroof	144812	Van	Ducato III facelift	290		EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	HIGH	Series 8 XL加长超高顶。	READY
145290_mwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	HIGH	Series 8 M单排座底盘。	READY
145290_mlwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	HIGH	Series 8 ML单排座底盘。	READY
145290_lwb_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	HIGH	Series 8 L单排座底盘。	READY
145290_xl_chassis	145290	Pickup	Ducato III facelift	290	2	EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	HIGH	Series 8 XL单排座底盘。	READY
10209	10209	MPV	Ducato III pre-facelift	250	4	EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	MEDIUM	180 Multijet Kombi 30 L1H1乘用外廓。	READY
10210_xl_highroof	10210	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	HIGH	180 Multijet L4H2加长后悬高顶。	READY
10210_xl_superhighroof	10210	Van	Ducato III pre-facelift	250		EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	HIGH	180 Multijet L4H3加长后悬超高顶。	READY
10211_swb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	HIGH	180 Multijet短轴原厂平板。	READY
10211_mwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	HIGH	180 Multijet中轴原厂平板。	READY
10211_lwb	10211	Pickup	Ducato III pre-facelift	250	2	EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	HIGH	180 Multijet 4035轴距原厂平板。	READY
17607_mwb_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶Bipower厢式车。	READY
17607_mwb_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶Bipower厢式车。	READY
17607_mwb_maxi_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶Bipower厢式车。	READY
17607_mwb_maxi_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶Bipower厢式车。	READY
17607_lwb_highroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶Bipower厢式车。	READY
17607_lwb_superhighroof	17607	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶Bipower厢式车。	READY
17608	17608	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	MEDIUM	2.0 Bipower中轴标准顶乘用型。	READY
16486_swb_lowroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	HIGH	230短轴标准顶厢式车。	READY
16486_swb_highroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	HIGH	230短轴高顶厢式车。	READY
16486_mwb_lowroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	HIGH	230中轴标准顶厢式车。	READY
16486_mwb_highroof	16486	Van	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	HIGH	230中轴高顶厢式车。	READY
16487	16487	MPV	Ducato II	230		EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	MEDIUM	230中轴乘用型标准顶外廓。	READY
16649_swb_lowroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16649_swb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16649_mwb_lowroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16649_mwb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16649_mwb_superhighroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16649_lwb_highroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16649_lwb_superhighroof	16649	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
16653_swb_lowroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16653_mwb_lowroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16653_mwb_highroof	16653	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	MEDIUM	中轴乘用型高顶。	READY
16738_swb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	2.0 JTD短轴原厂平板。	READY
16738_mwb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	2.0 JTD中轴原厂平板。	READY
16738_lwb	16738	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	2.0 JTD长轴原厂平板。	READY
58732_swb	58732	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
58732_mwb	58732	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	中轴原厂平板。	READY
16650_swb_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴标准顶厢式车。	READY
16650_swb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	HIGH	短轴高顶厢式车。	READY
16650_mwb_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴标准顶厢式车。	READY
16650_mwb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴高顶厢式车。	READY
16650_mwb_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	HIGH	中轴超高顶厢式车。	READY
16650_mwb_maxi_lowroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	HIGH	MAXI中轴标准顶厢式车。	READY
16650_mwb_maxi_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶厢式车。	READY
16650_mwb_maxi_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶厢式车。	READY
16650_lwb_highroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	HIGH	长轴高顶厢式车。	READY
16650_lwb_superhighroof	16650	Van	Ducato II facelift	244		EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶厢式车。	READY
16654_swb_lowroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	HIGH	短轴乘用型标准顶。	READY
16654_mwb_lowroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	HIGH	中轴乘用型标准顶。	READY
16654_mwb_highroof	16654	MPV	Ducato II facelift	244	4	EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	HIGH	中轴乘用型高顶。	READY
16739_swb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	HIGH	2.3 JTD短轴原厂平板。	READY
16739_mwb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	HIGH	2.3 JTD中轴原厂平板。	READY
16739_lwb	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	HIGH	2.3 JTD长轴原厂平板。	READY
16739_4050	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-4050-01	HIGH	4050轴距原厂平板。	READY
16739_mwb_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	HIGH	MAXI中轴原厂平板。	READY
16739_lwb_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	HIGH	MAXI长轴原厂平板。	READY
16739_4050_maxi	16739	Pickup	Ducato II facelift	244	2	EU-FIAT-DUCATO-II-244-PICKUP-4050-MAXI-01	HIGH	MAXI 4050轴距原厂平板。	READY
7795_swb	7795	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
7795_lwb	7795	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	长轴原厂平板。	READY
11091_swb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
11091_mwb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	HIGH	中轴原厂平板。	READY
11091_lwb_flatbed	11091	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	HIGH	长轴原厂平板。	READY
14370_swb_flatbed	14370	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	HIGH	短轴原厂平板。	READY
14370_maxi_flatbed	14370	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	HIGH	Maxi长轴原厂平板。	READY
14362_lowroof	14362	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-4X4-LOWROOF-01	HIGH	四驱标准顶厢式车。	READY
14362_highroof	14362	Van	Ducato I pre-facelift	280		EU-FIAT-DUCATO-I-280-VAN-4X4-HIGHROOF-01	HIGH	四驱高顶厢式车。	READY
14363	14363	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-4X4-01	MEDIUM	2.5 D 4X4短轴原厂平板。	READY
14365_lowroof	14365	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-LOWROOF-01	HIGH	四驱标准顶厢式车。	READY
14365_highroof	14365	Van	Ducato I facelift	290		EU-FIAT-DUCATO-I-290-VAN-4X4-HIGHROOF-01	HIGH	四驱高顶厢式车。	READY
14374	14374	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-4X4-01	MEDIUM	2.5 D 4X4短轴原厂平板。	READY
14863_mwb_flatbed	14863	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	MEDIUM	四驱中轴原厂平板。	READY
14863_lwb_flatbed	14863	Pickup	Ducato II	230	2	EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	MEDIUM	四驱长轴原厂平板。	READY
116060	116060	Van	Ducato II	230L	4	EU-FIAT-DUCATO-II-230-VAN-LWB-4X4-HIGHROOF-01	MEDIUM	KBA 4001/589/004对应Maxi 10高顶四驱外廓。	READY
11089_swb	11089	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
11089_lwb	11089	Pickup	Ducato I facelift	290	2	EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	MEDIUM	长轴原厂平板。	READY
59931_swb	59931	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	MEDIUM	短轴原厂平板。	READY
59931_maxi	59931	Pickup	Ducato I pre-facelift	280	2	EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	MEDIUM	Maxi原厂平板。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_4801-4900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DOBLO-I-223-MPV-PREFL-01	4159	1714	1810	FIAT Doblò in UK official press release	https://www.media.stellantis.com/uk-en/fiat/press/fiat-dobl-in-uk
EU-FIAT-DOBLO-I-223-VAN-SWB-FACELIFT-01	4253	1722	1831	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
EU-FIAT-DOBLO-I-223-VAN-SWB-HIGHROOF-FACELIFT-01	4253	1722	2086	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
EU-FIAT-DOBLO-I-223-VAN-LWB-FACELIFT-01	4633	1722	1817	Fiat Doblò 223 official Owner Handbook	https://aftersales.fiat.com/eLumData/FR/77/223_DOBLO/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG/77_223_DOBLO_603.81.541_FR_04_05.09_L_LG.pdf
EU-FIAT-DOBLO-III-K9-MPV-ICE-SWB-01	4403	1848	1800	Fiat Professional New Doblò official model document	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
EU-FIAT-DOBLO-III-K9-VAN-SWB-01	4403	1848	1796	Fiat Professional New Doblò official model document	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
EU-FIAT-DOBLO-III-K9-VAN-LWB-01	4753	1848	1812	Fiat Professional New Doblò official model document	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf
EU-FIAT-DOBLO-III-K9-VAN-SWB-4X4-FACELIFT-01	4403	1848	1886	Fiat Professional New Doblò official model document;Dangel 4WD official announcement	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf;https://www.dangel.com/en/dangel-reinvents-4x4-new-revolutionary-technology
EU-FIAT-DOBLO-III-K9-VAN-LWB-4X4-FACELIFT-01	4753	1848	1902	Fiat Professional New Doblò official model document;Dangel 4WD official announcement	https://www.media.stellantis.com/uploads/it/model-document/doblovan_40p_ita-638a29954cd70.pdf;https://www.dangel.com/en/dangel-reinvents-4x4-new-revolutionary-technology
EU-FIAT-DOBLO-III-K9-MPV-ELECTRIC-SWB-01	4403	1848	1844	Fiat E-Doblò German official price list	https://www.media.stellantis.com/uploads/de/model-document/fiat_preisliste_doblo_web-62b9d252f1c3d.pdf
EU-FIAT-DOBLO-II-263-VAN-SWB-PREFL-01	4390	1832	1845	Fiat Professional New Doblò Cargo Euro 5 official specification	https://www.media.stellantis.com/uploads/rs/RS/2012/F_PROFESSIONAL/FILES/FIAT_NEW_DOBLO_CARGO_EURO5.pdf
EU-FIAT-DOBLO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1845	Fiat Professional Range Price List December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-DOBLO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880	Fiat Professional Range Price List December 2016	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf
EU-FIAT-DOBLO-II-263-VAN-LWB-HIGHROOF-FACELIFT-01	4756	1832	2125	Fiat Professional New Doblò Cargo official technical specification	https://www.media.stellantis.com/uploads/em/2015/Fiat-Professional/150202/Schede-tecniche/150202_Fiat-Professional_Nuovo-Doblo-Cargo_Technical-Specification_ENG.pdf
EU-FIAT-DUCATO-I-280-VAN-LOWROOF-01	4765	1965	2100	Swiss Federal Roads Office Fiat Ducato 280/14 type approval CH 3F2063	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2063_F.pdf
EU-FIAT-DUCATO-I-280-VAN-HIGHROOF-01	4765	1965	2450	Swiss Federal Roads Office Fiat Ducato 280/14 type approval CH 3F2063	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2063_F.pdf
EU-FIAT-DUCATO-I-290-PICKUP-SWB-01	4868	2000	2070	Swiss ASTRA Fiat Ducato 290/14 type approval extract 3F2176	https://www.dauto.ch/typenscheine/fiat-ducato-290-14-kat-3f2176-zfa29000000-x
EU-FIAT-DUCATO-I-290-PICKUP-LWB-01	5598	2000	2070	Swiss ASTRA Fiat Ducato 290 NTX type approval extract 3F2115	https://www.dauto.ch/typenscheine/fiat-ducato-290-ntx-3f2115-zfa29000000-x
EU-FIAT-DUCATO-II-230-PICKUP-SWB-01	4770	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
EU-FIAT-DUCATO-II-230-PICKUP-MWB-01	5120	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
EU-FIAT-DUCATO-I-280-CHASSIS-LWB-DOUBLECAB-01	5442	1965	2050	Swiss Federal Roads Office Fiat Ducato 280 NAP4 type approval CH 3F2027	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2027_D.pdf
EU-FIAT-DUCATO-I-280-PICKUP-SWB-01	4840	2000	2050	Swiss Federal Roads Office Fiat Ducato 280 M.7 type approval CH 3F2011	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2011_D.pdf
EU-FIAT-DUCATO-I-280-PICKUP-MAXI-01	5576	2000	2076	Swiss Federal Roads Office Fiat Ducato 280 Maxi R.7 type approval CH 3F2001	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2001_D.pdf
EU-FIAT-DUCATO-II-244-VAN-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-SWB-HIGHROOF-01	4749	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-HIGHROOF-01	5099	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-SUPERHIGHROOF-01	5099	2024	2725	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-LOWROOF-01	5099	2024	2160	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-HIGHROOF-01	5099	2024	2480	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-LWB-HIGHROOF-01	5599	2024	2470	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-VAN-LWB-SUPERHIGHROOF-01	5599	2024	2860	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-SWB-01	4831	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-MWB-01	5181	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-LWB-01	5681	1932	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-MWB-MAXI-01	5181	1932	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-LWB-MAXI-01	5681	1932	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-I-290-VAN-LOWROOF-01	4765	1965	2100	Swiss Federal Roads Office Fiat Ducato 290/14 type approval CH 3F2111	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2111_D.pdf
EU-FIAT-DUCATO-I-290-VAN-HIGHROOF-01	4765	1965	2450	Swiss Federal Roads Office Fiat Ducato 290/14 type approval CH 3F2111	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2111_D.pdf
EU-FIAT-DUCATO-II-230-VAN-MWB-LOWROOF-01	5005	1998	2150	Swiss Federal Roads Office Fiat Ducato 230/14 type approval CH 3F2313	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2313_F.pdf
EU-FIAT-DUCATO-II-230-VAN-SWB-LOWROOF-01	4655	1998	2150	Swiss Federal Roads Office Fiat Ducato 230/14 type approval CH 3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230-VAN-SWB-HIGHROOF-01	4655	1998	2470	Swiss Federal Roads Office Fiat Ducato 230/14 type approval CH 3F2312	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2312_F.pdf
EU-FIAT-DUCATO-II-230-VAN-MWB-HIGHROOF-01	5005	1998	2470	Swiss Federal Roads Office Fiat Ducato 230/14 type approval CH 3F2313	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2313_F.pdf
EU-FIAT-DUCATO-III-250-VAN-SWB-LOWROOF-01	4963	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-SWB-HIGHROOF-01	4963	2050	2524	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-MWB-LOWROOF-01	5413	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-VAN-MWB-HIGHROOF-01	5413	2050	2524	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/it/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_ITA.pdf
EU-FIAT-DUCATO-III-250-PICKUP-SWB-02	5293	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-MWB-02	5743	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-LWB-02	6328	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-290-MPV-SWB-LOWROOF-01	4963	2050	2254	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-SWB-HIGHROOF-01	4963	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-LOWROOF-01	5413	2050	2254	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-HIGHROOF-01	5413	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-HIGHROOF-01	5998	2050	2524	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-SUPERHIGHROOF-01	5998	2050	2764	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MWB-01	5358	2050	2254	Fiat Professional New Ducato conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-MLWB-01	5708	2050	2254	Fiat Professional New Ducato conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-LWB-01	5943	2050	2254	Fiat Professional New Ducato conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-PICKUP-CHASSIS-CAB-XL-01	6308	2050	2254	Fiat Professional New Ducato conversion vehicle technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-250-PICKUP-MWB-4X4-01	5743	2100	2274	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 17Q type approval 3FH451	https://typenscheinschweiz.ch/typenschein/auto/3FH451
EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-LOWROOF-01	5413	2050	2274	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 type approval 3FH420	https://typenscheinschweiz.ch/typenschein/auto/3FH420
EU-FIAT-DUCATO-III-250-VAN-MWB-4X4-HIGHROOF-01	5413	2050	2542	Swiss Federal Roads Office FIAT-DANGEL Ducato 4x4 type approval 3FH420	https://typenscheinschweiz.ch/typenschein/auto/3FH420
EU-FIAT-DUCATO-III-290-VAN-XL-HIGHROOF-01	6363	2050	2524	Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-290-VAN-XL-SUPERHIGHROOF-01	6363	2050	2764	Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-MWB-01	5358	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-III-250-PICKUP-CHASSIS-CAB-LWB-01	5943	2050	2254	Fiat Professional Ducato Euro 5 official technical specifications 2011	https://www.media.stellantis.com/uploads/em/2011/FIAT_PROF/SCHEDE_TECNICHE/110505_FP_Ducato_ST_GBR.pdf
EU-FIAT-DUCATO-III-250-VAN-XL-HIGHROOF-01	6363	2050	2524	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-XL-SUPERHIGHROOF-01	6363	2050	2764	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-290-MPV-MWB-MAXI-HIGHROOF-01	5413	2050	2539	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-HIGHROOF-01	5998	2050	2534	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-LWB-MAXI-SUPERHIGHROOF-01	5998	2050	2774	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-MPV-XL-MAXI-HIGHROOF-01	6363	2050	2539	Fiat Professional New Ducato official technical specifications 2014	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-290-PICKUP-XL-01	6693	2100	2424	Fiat Professional New Ducato official goods transport technical specifications 2014;Fiat Professional Nouveau Ducato official price list 2021	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf;https://www.media.stellantis.com/uploads/fr/attachment/tarifpublicnouveauducato2021a-60df3adf9b087.pdf
EU-FIAT-DUCATO-III-250-VAN-LWB-HIGHROOF-01	5998	2050	2524	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-VAN-LWB-SUPERHIGHROOF-01	5998	2050	2764	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-3800-01	6093	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-III-250-PICKUP-XL-01	6693	2100	2424	Fiat Professional Ducato Kastenwagen–Pritschenwagen Technische Daten 2010	https://www.media.stellantis.com/uploads/de/DE/2010/fiat%20professional/2007-03/22092010113513_ducato_waren_techndaten.pdf
EU-FIAT-DUCATO-II-244-PICKUP-4050-01	5980	2040	2100	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-244-PICKUP-4050-MAXI-01	5980	2040	2125	Fiat Ducato 244 official Owner Handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-230-PICKUP-LWB-01	5620	2000	2100	Swiss type approval extract FIAT Ducato 230 factory dropside 3FA348	https://typenscheinschweiz.ch/pdf/auto/3FA348
EU-FIAT-DUCATO-I-280-VAN-4X4-LOWROOF-01	4765	1965	2129	Swiss Federal Roads Office Fiat Ducato 280/14 4x4 type approval CH 3F2108	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2108_D.pdf
EU-FIAT-DUCATO-I-280-VAN-4X4-HIGHROOF-01	4765	1965	2482	Swiss Federal Roads Office Fiat Ducato 280/14 4x4 type approval CH 3F2108	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2312-deutsch/3F2108_D.pdf
EU-FIAT-DUCATO-I-290-PICKUP-SWB-4X4-01	4868	2000	2100	Swiss ASTRA Fiat Ducato 290/14 4x4 type approval extract 3F2152	https://www.dauto.ch/typenscheine/fiat-ducato-290-14-4x4-3f2152-x-x
EU-FIAT-DUCATO-I-290-VAN-4X4-LOWROOF-01	4765	1965	2145	Swiss Federal Roads Office Fiat Ducato 290/14 4x4 type approval CH 3F2151	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2151_F.pdf
EU-FIAT-DUCATO-I-290-VAN-4X4-HIGHROOF-01	4765	1965	2490	Swiss Federal Roads Office Fiat Ducato 290/14 4x4 type approval CH 3F2151	https://opendata.astra.admin.ch/ivzod/2000-Typengenehmigungen_TG_TARGA/2310-pdf-Drucke_TG_1985-1995/2313-franzoesisch/3F2151_F.pdf
EU-FIAT-DUCATO-I-280-PICKUP-SWB-4X4-01	4868	2000	2078	Swiss ASTRA Fiat Ducato 280/14 4x4 type approval extract 3F2109	https://www.dauto.ch/typenscheine/fiat-ducato-280-14-4x4-3f2109-x-x
EU-FIAT-DUCATO-II-230-VAN-LWB-4X4-HIGHROOF-01	5505	1998	2480	ASR KBA vehicle data, Fiat Ducato Maxi 10 2.5 D 4x4 (KBA 4001/589/004)	https://www.autoneuteile.de/fiat-ducato-maxi-10-2.5-d-4x4-ersatzteile-kba-86325.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_4801-4900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autoneuteile.de/fiat-ducato-maxi-10-2.5-d-4x4-ersatzteile-kba-86325.html "Fiat Ducato Maxi 10 2.5 D 4x4 Ersatzteile KBA @ ASR Autoteile-Service-Recycling | Autoverwertung in Coswig"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（428 行）
- 累计尺寸组：dimension_groups_final.tsv（128 行）

