# 任务：left18448 第 5701-5800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0058__5ce4e54a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5701-5800 行

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
left18448 第 5701-5800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5701-5800_ktype_dimension_mapping_final.tsv
- left18448_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Grand c-Max van	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108784
Ford	Grand c-Max van	1.6 TI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Dec 2014	142764
Ford	Grand c-Max van	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108786
Ford	Grand c-Max van	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Feb 2011	Jun 2019	108788
Ford	Grand c-Max van	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108789
Ford	Grand c-Max van	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113301
Ford	Grand c-Max van	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113302
Ford	Gt	5.4	Coupe	Heckantrieb	Benzin	Jun 2003	Dec 2006	18094
Ford	Gt	3.5 Ecoboost V6	Coupe	Heckantrieb	Benzin	Sep 2016	-	126569
Ford	Gt	3.5 Ecoboost V6	Coupe	Heckantrieb	Benzin	Apr 2021	-	146756
Ford	Gt	3.5 Ecoboost V6	Coupe	Heckantrieb	Benzin	Jan 2020	-	154611
Ford	Ka	1.3 I	Schrägheck	Frontantrieb	Benzin	Jun 1998	Nov 2008	12059
Ford	Ka	1.3 I	Kasten/Schrägheck	Frontantrieb	Benzin	May 2002	May 2005	12469
Ford	Ka	1.3 I Rocam	Schrägheck	Frontantrieb	Benzin	Aug 2002	Nov 2008	17177
Ford	Ka	1.6 I	Schrägheck	Frontantrieb	Benzin	Feb 2001	Nov 2008	17305
Ford	Ka+ iii	1.2	Schrägheck	Frontantrieb	Benzin	Jun 2016	Dec 2020	120503
Ford	Ka+ iii	1.2	Stufenheck	Frontantrieb	Benzin	Jun 2016	Dec 2020	128525
Ford	Ka+ iii	1.2 Ti-vct	Schrägheck	Frontantrieb	Benzin	Jun 2016	Dec 2020	120504
Ford	Kuga i van	2.5	Kasten/SUV	Allrad	Benzin	Feb 2008	Nov 2012	142778
Ford	Kuga i van	Tdci	Kasten/SUV	Frontantrieb	Diesel	Mar 2010	Nov 2012	142781
Ford	Kuga i van	Tdci 4X4	Kasten/SUV	Allrad	Diesel	Mar 2010	Nov 2012	142782
Ford	Kuga i van	Tdci 4X4	Kasten/SUV	Allrad	Diesel	Mar 2010	Nov 2012	142783
Ford	Kuga ii	2.5	SUV	Frontantrieb	Benzin	Jan 2014	Dec 2019	117484
Ford	Kuga ii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	Sep 2014	Jun 2019	107967
Ford	Kuga ii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	Jan 2016	Jun 2019	118023
Ford	Kuga ii	1.5 Ecoboost 4X4	SUV	Allrad	Benzin	Sep 2014	Jun 2018	107968
Ford	Kuga ii	1.5 Ecoboost E85	SUV	Frontantrieb	Ethanol	Feb 2019	Nov 2019	143449
Ford	Kuga ii	1.6 Ecoboost	SUV	Frontantrieb	Benzin	Mar 2013	Sep 2014	58546
Ford	Kuga ii	1.6 Ecoboost 4X4	SUV	Allrad	Benzin	Mar 2013	Sep 2014	58547
Ford	Kuga ii	1.6 Ecoboost 4X4	SUV	Allrad	Benzin	Mar 2013	Sep 2014	108072
Ford	Kuga ii	2.0 Tdci	SUV	Frontantrieb	Diesel	Mar 2013	Sep 2014	58548
Ford	Kuga ii	2.0 Tdci	SUV	Frontantrieb	Diesel	Mar 2013	Dec 2019	106502
Ford	Kuga ii	2.0 Tdci	SUV	Frontantrieb	Diesel	Sep 2014	Jun 2019	107969
Ford	Kuga ii	2.0 Tdci	SUV	Frontantrieb	Diesel	Sep 2014	Jun 2019	107970
Ford	Kuga ii	2.0 Tdci	SUV	Frontantrieb	Diesel	Mar 2013	Dec 2019	113633
Ford	Kuga ii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Mar 2013	Sep 2014	58549
Ford	Kuga ii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Mar 2013	Sep 2014	58550
Ford	Kuga ii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Mar 2013	Dec 2019	106503
Ford	Kuga ii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Sep 2014	Jun 2019	107971
Ford	Kuga ii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Sep 2014	Jun 2019	107972
Ford	Kuga ii van	1.5 Ecoboost 4X4	Kasten/SUV	Allrad	Benzin	Sep 2014	Dec 2019	108769
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	Jul 2019	-	143793
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	Sep 2019	-	143819
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	Oct 2024	-	801443
Ford	Kuga iii	2.0 Ecoblue 4X4	SUV	Allrad	Diesel	Feb 2021	-	144146
Ford	Kuga iii	2.0 Tdci	SUV	Frontantrieb	Diesel	Nov 2022	-	151947
Ford	Kuga iii	2.0 Tdci 4X4	SUV	Allrad	Diesel	Nov 2022	-	151948
Ford	Kuga iii	2.5 Duratec Fhev	SUV	Frontantrieb	Benzin/Elektro	Jan 2024	-	157592
Ford	Kuga iii	2.5 Duratec Fhev 4X4	SUV	Allrad	Benzin/Elektro	Jan 2024	-	157593
Ford	Kuga iii	2.5 Duratec Phev	SUV	Frontantrieb	Benzin/Elektro	Jan 2024	-	157594
Ford	Kuga iii	2.5 Duratec Plug-in-hybrid 4X4	SUV	Allrad	Benzin/Elektro	Jul 2019	-	154744
Ford	Kuga iii	2.5 Fhev	SUV	Frontantrieb	Benzin/Elektro	Jan 2021	-	143548
Ford	Kuga iii	2.5 Fhev 4X4	SUV	Allrad	Benzin/Elektro	Jan 2021	-	143547
Ford	Kuga iii	2.5 Hybrid Flex	SUV	Frontantrieb	Benzin/Ethanol/Elektro	Jun 2023	-	155319
Ford	Maverick	2.0 16V	SUV	Allrad	Benzin	Feb 2001	-	14852
Ford	Maverick	2.0 16V FWD	SUV	Frontantrieb	Benzin	Feb 2001	-	125811
Ford	Maverick	2.3 16V	SUV	Allrad	Benzin	Mar 2004	-	17959
Ford	Maverick	3.0 V6 24V	SUV	Allrad	Benzin	Feb 2001	-	14851
Ford	Maverick	3.0 V6 24V	SUV	Allrad	Benzin	Mar 2004	-	17960
Ford	Maverick	3.0 V6 24V FWD	SUV	Frontantrieb	Benzin	Feb 2001	-	125812
Ford	Mondeo i	1.8 I 16V 4X4	Schrägheck	Allrad	Benzin	Feb 1993	Aug 1996	15280
Ford	Mondeo i	2.0 I 16V 4X4	Schrägheck	Allrad	Benzin	Apr 1993	Aug 1996	106758
Ford	Mondeo i turnier	1.8 I 16V 4X4	Kombi	Allrad	Benzin	Apr 1993	Aug 1996	15281
Ford	Mondeo i turnier	2.0 I 16V 4X4	Kombi	Allrad	Benzin	Apr 1993	Aug 1996	15282
Ford	Mondeo ii	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	May 1998	Sep 2000	10236
Ford	Mondeo ii	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	May 1998	Sep 2000	10237
Ford	Mondeo ii	2.5 24V	Schrägheck	Frontantrieb	Benzin	Jun 2000	Sep 2000	15438
Ford	Mondeo ii	2.5 24V	Stufenheck	Frontantrieb	Benzin	Jun 2000	Sep 2000	15439
Ford	Mondeo ii	2.5 ST 200	Schrägheck	Frontantrieb	Benzin	May 1999	Sep 2000	11765
Ford	Mondeo ii	2.5 ST 200	Stufenheck	Frontantrieb	Benzin	May 1999	Sep 2000	11766
Ford	Mondeo ii turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	May 1998	Sep 2000	10238
Ford	Mondeo ii turnier	2.5 24V	Kombi	Frontantrieb	Benzin	Oct 1999	Sep 2000	15440
Ford	Mondeo ii turnier	2.5 ST 200	Kombi	Frontantrieb	Benzin	May 1999	Sep 2000	11767
Ford	Mondeo iii	1.8 16V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15442
Ford	Mondeo iii	1.8 16V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15443
Ford	Mondeo iii	1.8 16V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15482
Ford	Mondeo iii	1.8 16V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15484
Ford	Mondeo iii	1.8 SCI	Schrägheck	Frontantrieb	Benzin	Jun 2003	Mar 2007	17612
Ford	Mondeo iii	1.8 SCI	Stufenheck	Frontantrieb	Benzin	Jun 2003	Mar 2007	17614
Ford	Mondeo iii	2.0 16V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15444
Ford	Mondeo iii	2.0 16V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15486
Ford	Mondeo iii	2.0 16V DI / Tddi / Tdci	Stufenheck	Frontantrieb	Diesel	Oct 2000	Mar 2007	15446
Ford	Mondeo iii	2.0 16V DI / Tddi / Tdci	Schrägheck	Frontantrieb	Diesel	Oct 2000	Mar 2007	15490
Ford	Mondeo iii	2.0 16V Tddi / Tdci	Stufenheck	Frontantrieb	Diesel	Oct 2000	Mar 2007	15447
Ford	Mondeo iii	2.0 16V Tddi / Tdci	Schrägheck	Frontantrieb	Diesel	Oct 2000	Mar 2007	15492
Ford	Mondeo iii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	Oct 2001	Mar 2007	16452
Ford	Mondeo iii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	Oct 2001	Mar 2007	16453
Ford	Mondeo iii	2.2 Tdci	Schrägheck	Frontantrieb	Diesel	Sep 2004	Mar 2007	18269
Ford	Mondeo iii	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	Sep 2004	Mar 2007	18270
Ford	Mondeo iii	2.5 V6	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	39219
Ford	Mondeo iii	2.5 V6 24V	Stufenheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15445
Ford	Mondeo iii	2.5 V6 24V	Schrägheck	Frontantrieb	Benzin	Oct 2000	Mar 2007	15488
Ford	Mondeo iii	3.0 V6 24V	Schrägheck	Frontantrieb	Benzin	Sep 2004	Mar 2007	18272
Ford	Mondeo iii	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	Sep 2004	Mar 2007	18273
Ford	Mondeo iii	St220	Schrägheck	Frontantrieb	Benzin	Apr 2002	Mar 2007	16632
Ford	Mondeo iii	St220	Stufenheck	Frontantrieb	Benzin	Apr 2002	Mar 2007	16633
Ford	Mondeo iii turnier	1.8 16V	Kombi	Frontantrieb	Benzin	Oct 2000	Mar 2007	15483
Ford	Mondeo iii turnier	1.8 16V	Kombi	Frontantrieb	Benzin	Oct 2000	Mar 2007	15485
Ford	Mondeo iii turnier	1.8 SCI	Kombi	Frontantrieb	Benzin	Jun 2003	Mar 2007	17613
Ford	Mondeo iii turnier	2.0 16V	Kombi	Frontantrieb	Benzin	Oct 2000	Mar 2007	15487


--- Round 1 / 首次发送 ---
## 更新点

* 完成 **Grand C-Max、Ford GT、Kuga II** 三个车型簇的首次尺寸组建档，共覆盖 30 个输入 Ktype。
* Grand C-Max 按改款前后拆为两套外廓：改款前 `4520×1828×1684 mm`，改款后 `4519×1828×1642 mm`；跨越改款周期的 Ktype 已拆分派生行。([汽车档案馆][1])
* Ford GT 第一代确认为 `4643×1953×1125 mm`；第二代采用欧洲官方技术规格 `4779×2003×1109 mm`。([Scribd][2])
* Kuga II 的 2013—2019 标准五门车身统一复用 `4524×1838×1689 mm`。2014 与 2017 官方资料均显示标准车身尺寸一致；带独立造型套件的加长数据未用于本批普通发动机版本。([Dezo's Garage][3])
* 发动机、燃料和两驱/四驱差异未重复创建尺寸组。

## 当前批次进度

* 输入 Ktype：100 个
* 已覆盖输入 Ktype：30 个
* 本轮 READY 映射：34 行
* 已落盘 PENDING 映射：0 行
* 尚待处理输入 Ktype：70 个
* 已确认尺寸组：5 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108784_prefl	108784	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108784_facelift	108784	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
142764	142764	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	改款前 Grand C-Max 五门外廓。	READY
108786_prefl	108786	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108786_facelift	108786	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
108788_prefl	108788	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108788_facelift	108788	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
108789_prefl	108789	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108789_facelift	108789	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
113301	113301	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	改款后 Grand C-Max 五门外廓。	READY
113302	113302	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	改款后 Grand C-Max 五门外廓。	READY
18094	18094	Coupe	GT I		2	EU-FORD-GT-I-COUPE-2D-01	HIGH		READY
126569	126569	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
146756	146756	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
154611	154611	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
117484	117484	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107967	107967	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
118023	118023	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107968	107968	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
143449	143449	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58546	58546	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58547	58547	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
108072	108072	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58548	58548	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
106502	106502	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107969	107969	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107970	107970	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
113633	113633	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58549	58549	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58550	58550	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
106503	106503	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107971	107971	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107972	107972	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
108769	108769	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH	Kasten/SUV 货运衍生型沿用 Kuga II 五门外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Ford C-MAX + Grand C-MAX 2011 brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	4519	1828	1642	Ford C-MAX + Grand C-MAX official brochure; Automobile-Catalog	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf;https://www.automobile-catalog.com/car/2015/2140595/ford_grand_c-max_1_5_tdci_120.html
EU-FORD-GT-I-COUPE-2D-01	4643	1953	1125	Ford GT 2005 specifications; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/09/Ford-GT-2005-USA.pdf;https://www.automobile-catalog.com/car/2005/894440/ford_gt.html
EU-FORD-GT-II-COUPE-2D-01	4779	2003	1109	Ford GT EU technical specifications	https://fordmediacenter.nl/wp-content/uploads/2017/05/gt_technical_specs_EU.pdf
EU-FORD-KUGA-II-DM2-SUV-5D-01	4524	1838	1689	Ford Kuga 2014 official brochure; Ford Kuga 2017 official brochure	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Kuga-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Kuga-UK.pdf
```

## 下一步优先处理

1. 按尺寸组集中处理 Kuga I 与 Kuga III，并核对 Kuga III 2024 改款是否发生外廓变化。
2. 处理 Ka、Ka+ 的 Hatchback、Sedan 和商用衍生边界。
3. 按 Hatchback、Sedan、Wagon 聚类处理 Mondeo I、II、III，避免按发动机重复抓取。
4. 最后处理 Maverick 的欧洲代际及前驱/四驱是否共用外廓。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf?utm_source=chatgpt.com "FORD C-MAX + FORD GRAND C-MAX"
[2]: https://www.scribd.com/document/317522621/Ford-US-GT-2006-pdf?utm_source=chatgpt.com "2005-2006 Ford GT Specifications | PDF | Wheeled Vehicles"
[3]: https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Kuga-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Kuga-UK.pdf"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5701-5800_ktype_dimension_mapping_final.tsv
- left18448_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新建 **Ka+ III** 三个尺寸组：改款前五门掀背、改款后五门掀背和 TK 四门轿车。两条生产周期跨越改款的 Hatchback Ktype 已拆分为 `prefl`、`facelift` 派生行。官方资料显示改款前为 `3929×1695×1524 mm`，改款后标准车型为 `3941×1743×1524 mm`。
* Ka+ III Sedan Ktype `128525` 对应 TK/FK 四门车型，本轮采用 Ford Aspire 官方资料确认的 `3995×1695×1525 mm` 外廓。([DENSO][1])
* 新建 **Kuga I 五门 SUV** 尺寸组，4 个 `Kasten/SUV` Ktype 直接复用。官方手册确认车长及不含后视镜宽度，规格库补齐标准无车顶行李架高度。

## 当前批次进度

* 输入 Ktype：100 个
* 已完成输入 Ktype：37 个
* READY 映射：43 行
* 待处理输入 Ktype：63 个
* 已确认尺寸组：9 个
* 本轮新增 PENDING 映射：0 行
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120503_prefl	120503	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
120503_facelift	120503	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
128525	128525	Sedan	Ka+ III	TK	4	EU-FORD-KA-PLUS-III-SEDAN-4D-01	HIGH	TK四门短车身轿车外廓。	READY
120504_prefl	120504	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
120504_facelift	120504	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
142778	142778	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142781	142781	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142782	142782	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142783	142783	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	3929	1695	1524	Ford KA+ preliminary technical specifications	https://fordmediacenter.nl/wp-content/uploads/2016/06/FordKaPlus_EU.pdf
EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	3941	1743	1524	Ford KA+ official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_KA_Plus.pdf
EU-FORD-KA-PLUS-III-SEDAN-4D-01	3995	1695	1525	Ford Aspire official brochure	https://images.cardekho.com/brochures/files/Ford-Aspire/1.5-TDCi-Trend/Ford-Aspire-Brochure.pdf
EU-FORD-KUGA-I-SUV-5D-01	4443	1842	1677	Ford Kuga 2008 official brochure; Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Kuga-UK.pdf;https://www.automobile-catalog.com/car/2008/979430/ford_kuga_2_0_tdci_trend_2x4.html
```

## 下一步优先处理

1. 闭合 Ford Ka RB 普通 Hatchback、Ka Van 与可能存在特殊保险杠外廓的 1.6 版本。
2. 按改款边界处理 Kuga III，集中确认改款前、2024 改款及不同外观套件是否需要拆组。
3. 解决 Maverick 改款前后尺寸来源冲突。
4. 按 Hatchback、Sedan、Wagon 聚类处理 Mondeo I、II、III。

推进信号：CONTINUE

[1]: https://www.denso-am.eu/catalog/pv/128525?utm_source=chatgpt.com "Car parts for FORD KA+ III Saloon (TK, FK), 1.2 ... - denso-am.eu"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5701-5800_ktype_dimension_mapping_final.tsv
- left18448_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Ford Ka I 车型簇，新增标准 Ka/Ka Van 与 SportKa 两个尺寸组。
* Ford 官方手册确认标准 Ka 最大外廓为 `3620×1639×1413 mm`，SportKa 最大外廓为 `3649×1656×1431 mm`；宽度均明确不含外后视镜。([福特服务内容][1])
* Ktype `17305` 对应 RB 车身的 1.6i 95 PS 版本，并按 SportKa 外廓建组；其余三个 Ktype 复用标准 Ka 外廓。([JMS Fahrzeugteile][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：41
* PENDING／待处理输入 Ktype：59
* READY 映射：47 行
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12059	12059	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH		READY
12469	12469	Van	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH	Ka Van货运衍生型沿用标准三门外廓。	READY
17177	17177	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH		READY
17305	17305	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-SPORT-HATCHBACK-3D-01	MEDIUM	1.6i版本对应SportKa外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-KA-I-RB-HATCHBACK-3D-01	3620	1639	1413	Ford Ka official owner's handbook	https://www.fordservicecontent.com/Ford_Content/Catalog/owner_information/Ford_Ka_owners_guide.pdf
EU-FORD-KA-I-RB-SPORT-HATCHBACK-3D-01	3649	1656	1431	Ford Ka official owner's handbook	https://www.fordservicecontent.com/Ford_Content/Catalog/owner_information/Ford_Ka_owners_guide.pdf
```

## 下一步优先处理

1. 闭合 Maverick II 改款前后外廓冲突，并批量关联六个 Ktype。
2. 按 Kuga III 改款前、2024 改款及 Titanium／ST-Line／Active 外廓边界建组。
3. 按 Hatchback、Sedan、Wagon 聚类处理 Mondeo I、II、III。

推进信号：CONTINUE

[1]: https://www.fordservicecontent.com/Ford_Content/Catalog/owner_information/Ford_Ka_owners_guide.pdf "Untitled"
[2]: https://www.jms-fahrzeugteile.de/Bremsentechnik/EBC-Bremscheiben-Belaege/EBC-Standard-Bremsbelaege-fuer/Ford/KA/VA-vorne-front/EBC-Blackstuff-Bremsbelaege-DP132013599-passend-fuer-Ford-KA-RB%3A%3A1042249.html?utm_source=chatgpt.com "EBC Blackstuff Bremsbeläge DP1320(13599) passend für Ford KA RB"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5701-5800_ktype_dimension_mapping_final.tsv
- left18448_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 **Kuga III** 13 个 Ktype，按物理外廓建立改款前标准车身、改款前 PHEV 和 2024 改款标准车身三个尺寸组。改款前标准车身为 `4614×1883×1678 mm`，PHEV 为 `4614×1883×1675 mm`；2024 改款 Titanium 基准外廓为 `4604×1882×1679 mm`。([露营与越野][1])
* 闭合 **Maverick II** 6 个 Ktype，按 2001—2004 改款前和 2004—2007 改款后拆为两个尺寸组。改款前为 `4415×1825×1770 mm`，改款后为 `4441×1825×1762 mm`。([汽车目录][2])
* 发动机、燃料以及前驱/四驱差异未单独重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：60
* PENDING／待处理输入 Ktype：40
* READY 映射：66 行
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143793	143793	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
143819	143819	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
801443	801443	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
144146	144146	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
151947	151947	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
151948	151948	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
157592	157592	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
157593	157593	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
157594	157594	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
154744	154744	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PHEV-01	MEDIUM	输入为PHEV 4X4；外廓按PHEV车身。	READY
143548	143548	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
143547	143547	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
155319	155319	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
14852	14852	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
125811	125811	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
17959	17959	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-FACELIFT-01	HIGH	改款后五门外廓。	READY
14851	14851	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
17960	17960	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-FACELIFT-01	HIGH	改款后五门外廓。	READY
125812	125812	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-KUGA-III-DFK-SUV-PREFL-01	4614	1883	1678	Ford Kuga 2020 technical specifications	https://fordmediacenter.nl/wp-content/uploads/2020/04/Kuga_NL_TechSpecs.docx
EU-FORD-KUGA-III-DFK-SUV-PHEV-01	4614	1883	1675	Ford Kuga 2020 technical specifications	https://fordmediacenter.nl/wp-content/uploads/2020/04/Kuga_NL_TechSpecs.docx
EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	4604	1882	1679	Ford 2024 Kuga technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewKuga/NEW_KUGA_techspec_240111.pdf
EU-FORD-MAVERICK-II-SUV-PREFL-01	4415	1825	1770	Automobile-Catalog Ford Maverick 2001 specifications	https://www.automobile-catalog.com/car/2001/980180/ford_maverick_2_0_16v.html
EU-FORD-MAVERICK-II-SUV-FACELIFT-01	4441	1825	1762	Automobile-Catalog Ford Maverick 2004 specifications	https://www.automobile-catalog.com/car/2004/980225/ford_maverick_2_3l_16v.html
```

## 下一步优先处理

1. 闭合 Mondeo I 的 Hatchback 与 Wagon 两个改款前外廓。
2. 闭合 Mondeo II 的 Hatchback、Sedan、Wagon，并单独判断 ST200 外观套件是否改变最大长度。
3. 闭合 Mondeo III 的 Hatchback、Sedan、Wagon及 ST220 运动外廓，批量关联剩余 40 个 Ktype。

推进信号：CONTINUE

[1]: https://www.automag.co.il/wp-content/uploads/2020/03/Kuga_Euro_TechSpec.pdf "Ford Kuga Specifications"
[2]: https://www.automobile-catalog.com/car/2001/980195/ford_maverick_3_0l_v-6_limited.html?utm_source=chatgpt.com "2001 Ford Maverick 3.0L V-6 Limited Specs Review (145 kW / 197 PS / 194 hp) (since April 2001 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5701-5800_ktype_dimension_mapping_final.tsv
- left18448_5701-5800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成剩余 40 个 Mondeo I、II、III Ktype，新增 10 个尺寸组。Mondeo I、II 按 Hatchback、Sedan、Wagon 物理车身拆分；Mondeo III 另将车身高度不同的 ST220 与普通版本分组。([汽车目录][1])
* Mondeo III 普通四门、五门及 Wagon 采用 Ford 规格表；ST220 四门、五门采用其独立的 1415 mm 车高记录。([Dezo's Garage][2])
* 已完成固定表头、唯一主键、引用闭合、正整数尺寸、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：106 行，覆盖全部 100 个输入 Ktype
* PENDING：0
* DIMENSION_GROUP：26
* 孤立尺寸组：0
* 未闭合映射引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
108784_prefl	108784	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108784_facelift	108784	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
142764	142764	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	改款前 Grand C-Max 五门外廓。	READY
108786_prefl	108786	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108786_facelift	108786	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
108788_prefl	108788	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108788_facelift	108788	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
108789_prefl	108789	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
108789_facelift	108789	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
113301	113301	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	改款后 Grand C-Max 五门外廓。	READY
113302	113302	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	改款后 Grand C-Max 五门外廓。	READY
18094	18094	Coupe	GT I		2	EU-FORD-GT-I-COUPE-2D-01	HIGH		READY
126569	126569	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
146756	146756	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
154611	154611	Coupe	GT II		2	EU-FORD-GT-II-COUPE-2D-01	HIGH		READY
12059	12059	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH		READY
12469	12469	Van	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH	Ka Van货运衍生型沿用标准三门外廓。	READY
17177	17177	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-HATCHBACK-3D-01	HIGH		READY
17305	17305	Hatchback	Ka I	RB	3	EU-FORD-KA-I-RB-SPORT-HATCHBACK-3D-01	MEDIUM	1.6i版本对应SportKa外廓。	READY
120503_prefl	120503	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
120503_facelift	120503	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
128525	128525	Sedan	Ka+ III	TK	4	EU-FORD-KA-PLUS-III-SEDAN-4D-01	HIGH	TK四门短车身轿车外廓。	READY
120504_prefl	120504	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	HIGH	跨改款生产期，拆分为改款前外廓。	READY
120504_facelift	120504	Hatchback	Ka+ III	UK	5	EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	HIGH	跨改款生产期，拆分为改款后外廓。	READY
142778	142778	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142781	142781	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142782	142782	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
142783	142783	SUV	Kuga I		5	EU-FORD-KUGA-I-SUV-5D-01	HIGH	Kasten/SUV货运衍生型沿用Kuga I五门外廓。	READY
117484	117484	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107967	107967	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
118023	118023	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107968	107968	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
143449	143449	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58546	58546	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58547	58547	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
108072	108072	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58548	58548	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
106502	106502	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107969	107969	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107970	107970	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
113633	113633	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58549	58549	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
58550	58550	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
106503	106503	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107971	107971	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
107972	107972	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH		READY
108769	108769	SUV	Kuga II	DM2	5	EU-FORD-KUGA-II-DM2-SUV-5D-01	HIGH	Kasten/SUV 货运衍生型沿用 Kuga II 五门外廓。	READY
143793	143793	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
143819	143819	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
801443	801443	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
144146	144146	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
151947	151947	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
151948	151948	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
157592	157592	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
157593	157593	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
157594	157594	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	HIGH	2024改款标准外廓。	READY
154744	154744	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PHEV-01	MEDIUM	输入为PHEV 4X4；外廓按PHEV车身。	READY
143548	143548	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
143547	143547	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
155319	155319	SUV	Kuga III	DFK	5	EU-FORD-KUGA-III-DFK-SUV-PREFL-01	HIGH		READY
14852	14852	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
125811	125811	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
17959	17959	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-FACELIFT-01	HIGH	改款后五门外廓。	READY
14851	14851	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
17960	17960	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-FACELIFT-01	HIGH	改款后五门外廓。	READY
125812	125812	SUV	Maverick II		5	EU-FORD-MAVERICK-II-SUV-PREFL-01	HIGH	改款前五门外廓。	READY
15280	15280	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-GBP-HATCHBACK-5D-01	HIGH		READY
106758	106758	Hatchback	Mondeo I	GBP	5	EU-FORD-MONDEO-I-GBP-HATCHBACK-5D-01	HIGH		READY
15281	15281	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-5D-01	HIGH		READY
15282	15282	Wagon	Mondeo I	BNP	5	EU-FORD-MONDEO-I-BNP-WAGON-5D-01	HIGH		READY
10236	10236	Hatchback	Mondeo II	BAP	5	EU-FORD-MONDEO-II-BAP-HATCHBACK-5D-01	HIGH		READY
10237	10237	Sedan	Mondeo II	BFP	4	EU-FORD-MONDEO-II-BFP-SEDAN-4D-01	HIGH		READY
15438	15438	Hatchback	Mondeo II	BAP	5	EU-FORD-MONDEO-II-BAP-HATCHBACK-5D-01	HIGH		READY
15439	15439	Sedan	Mondeo II	BFP	4	EU-FORD-MONDEO-II-BFP-SEDAN-4D-01	HIGH		READY
11765	11765	Hatchback	Mondeo II	BAP	5	EU-FORD-MONDEO-II-BAP-HATCHBACK-5D-01	HIGH		READY
11766	11766	Sedan	Mondeo II	BFP	4	EU-FORD-MONDEO-II-BFP-SEDAN-4D-01	HIGH		READY
10238	10238	Wagon	Mondeo II	BNP	5	EU-FORD-MONDEO-II-BNP-WAGON-5D-01	HIGH		READY
15440	15440	Wagon	Mondeo II	BNP	5	EU-FORD-MONDEO-II-BNP-WAGON-5D-01	HIGH		READY
11767	11767	Wagon	Mondeo II	BNP	5	EU-FORD-MONDEO-II-BNP-WAGON-5D-01	HIGH		READY
15442	15442	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15443	15443	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15482	15482	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
15484	15484	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
17612	17612	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
17614	17614	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15444	15444	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15486	15486	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
15446	15446	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15490	15490	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
15447	15447	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15492	15492	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
16452	16452	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
16453	16453	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
18269	18269	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
18270	18270	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
39219	39219	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15445	15445	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
15488	15488	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
18272	18272	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	HIGH		READY
18273	18273	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	HIGH		READY
16632	16632	Hatchback	Mondeo III	B5Y	5	EU-FORD-MONDEO-III-B5Y-ST220-HATCHBACK-5D-01	HIGH		READY
16633	16633	Sedan	Mondeo III	B4Y	4	EU-FORD-MONDEO-III-B4Y-ST220-SEDAN-4D-01	HIGH		READY
15483	15483	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-BWY-WAGON-5D-01	HIGH		READY
15485	15485	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-BWY-WAGON-5D-01	HIGH		READY
17613	17613	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-BWY-WAGON-5D-01	HIGH		READY
15487	15487	Wagon	Mondeo III	BWY	5	EU-FORD-MONDEO-III-BWY-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5701-5800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Ford C-MAX + Grand C-MAX 2011 brochure; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	4519	1828	1642	Ford C-MAX + Grand C-MAX official brochure; Automobile-Catalog	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf;https://www.automobile-catalog.com/car/2015/2140595/ford_grand_c-max_1_5_tdci_120.html
EU-FORD-GT-I-COUPE-2D-01	4643	1953	1125	Ford GT 2005 specifications; Automobile-Catalog	https://autocatalogarchive.com/wp-content/uploads/2016/09/Ford-GT-2005-USA.pdf;https://www.automobile-catalog.com/car/2005/894440/ford_gt.html
EU-FORD-GT-II-COUPE-2D-01	4779	2003	1109	Ford GT EU technical specifications	https://fordmediacenter.nl/wp-content/uploads/2017/05/gt_technical_specs_EU.pdf
EU-FORD-KA-I-RB-HATCHBACK-3D-01	3620	1639	1413	Ford Ka official owner's handbook	https://www.fordservicecontent.com/Ford_Content/Catalog/owner_information/Ford_Ka_owners_guide.pdf
EU-FORD-KA-I-RB-SPORT-HATCHBACK-3D-01	3649	1656	1431	Ford Ka official owner's handbook	https://www.fordservicecontent.com/Ford_Content/Catalog/owner_information/Ford_Ka_owners_guide.pdf
EU-FORD-KA-PLUS-III-HATCHBACK-PREFL-01	3929	1695	1524	Ford KA+ preliminary technical specifications	https://fordmediacenter.nl/wp-content/uploads/2016/06/FordKaPlus_EU.pdf
EU-FORD-KA-PLUS-III-HATCHBACK-FACELIFT-01	3941	1743	1524	Ford KA+ official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_KA_Plus.pdf
EU-FORD-KA-PLUS-III-SEDAN-4D-01	3995	1695	1525	Ford Aspire official brochure	https://images.cardekho.com/brochures/files/Ford-Aspire/1.5-TDCi-Trend/Ford-Aspire-Brochure.pdf
EU-FORD-KUGA-I-SUV-5D-01	4443	1842	1677	Ford Kuga 2008 official brochure; Automobile-Catalog	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Kuga-UK.pdf;https://www.automobile-catalog.com/car/2008/979430/ford_kuga_2_0_tdci_trend_2x4.html
EU-FORD-KUGA-II-DM2-SUV-5D-01	4524	1838	1689	Ford Kuga 2014 official brochure; Ford Kuga 2017 official brochure	https://xr793.com/wp-content/uploads/2022/09/2014-Ford-Kuga-UK.pdf;https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Kuga-UK.pdf
EU-FORD-KUGA-III-DFK-SUV-PREFL-01	4614	1883	1678	Ford Kuga 2020 technical specifications	https://fordmediacenter.nl/wp-content/uploads/2020/04/Kuga_NL_TechSpecs.docx
EU-FORD-KUGA-III-DFK-SUV-FACELIFT-01	4604	1882	1679	Ford 2024 Kuga technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2024/01/NewKuga/NEW_KUGA_techspec_240111.pdf
EU-FORD-KUGA-III-DFK-SUV-PHEV-01	4614	1883	1675	Ford Kuga 2020 technical specifications	https://fordmediacenter.nl/wp-content/uploads/2020/04/Kuga_NL_TechSpecs.docx
EU-FORD-MAVERICK-II-SUV-PREFL-01	4415	1825	1770	Automobile-Catalog Ford Maverick 2001 specifications	https://www.automobile-catalog.com/car/2001/980180/ford_maverick_2_0_16v.html
EU-FORD-MAVERICK-II-SUV-FACELIFT-01	4441	1825	1762	Automobile-Catalog Ford Maverick 2004 specifications	https://www.automobile-catalog.com/car/2004/980225/ford_maverick_2_3l_16v.html
EU-FORD-MONDEO-I-GBP-HATCHBACK-5D-01	4481	1747	1424	Automobile-Catalog Ford Mondeo 1993 5-door specifications	https://www.automobile-catalog.com/car/1993/947555/ford_mondeo_5-dr_2_0i_16v_ghia.html
EU-FORD-MONDEO-I-BNP-WAGON-5D-01	4631	1745	1442	Automobile-Catalog Ford Mondeo 1996 estate specifications	https://www.automobile-catalog.com/car/1996/947765/ford_mondeo_turnier_estate_1_6i_16v_glx.html
EU-FORD-MONDEO-II-BAP-HATCHBACK-5D-01	4556	1749	1372	Ford Mondeo 1998 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-II-BFP-SEDAN-4D-01	4556	1749	1372	Ford Mondeo 1998 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-II-BNP-WAGON-5D-01	4671	1749	1391	Ford Mondeo 1998 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2026/02/Ford-Mondeo-1998-UK-.pdf
EU-FORD-MONDEO-III-B4Y-SEDAN-4D-01	4731	1812	1429	Ford Mondeo 2005 official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf
EU-FORD-MONDEO-III-B5Y-HATCHBACK-5D-01	4731	1812	1429	Ford Mondeo 2005 official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf
EU-FORD-MONDEO-III-B5Y-ST220-HATCHBACK-5D-01	4731	1812	1415	Automobile-Catalog Ford Mondeo ST220 5-door specifications	https://www.automobile-catalog.com/car/2002/971120/ford_mondeo_5-dr_st_220.html
EU-FORD-MONDEO-III-B4Y-ST220-SEDAN-4D-01	4731	1812	1415	Automobile-Catalog Ford Mondeo ST220 4-door specifications	https://www.automobile-catalog.com/car/2002/971105/ford_mondeo_4-dr_st_220.html
EU-FORD-MONDEO-III-BWY-WAGON-5D-01	4804	1812	1441	Ford Mondeo 2005 official brochure	https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5701-5800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1993/947555/ford_mondeo_5-dr_2_0i_16v_ghia.html?utm_source=chatgpt.com "1993 Ford Mondeo (5-dr) 2.0i 16V Ghia Specs Review (100 kW / 136 PS / 134 hp) (since mid-year 1993 for Europe )"
[2]: https://xr793.com/wp-content/uploads/2022/09/2005-Ford-Mondeo-SPG-UK.pdf "untitled"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1825 行）
- 累计尺寸组：dimension_groups_final.tsv（434 行）

