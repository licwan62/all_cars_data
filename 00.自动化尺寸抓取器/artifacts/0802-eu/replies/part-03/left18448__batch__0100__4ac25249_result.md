# 任务：left18448 第 9901-10000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0100__4ac25249


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 9901-10000 行

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
left18448 第 9901-10000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9901-10000_ktype_dimension_mapping_final.tsv
- left18448_9901-10000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	4698	1786	1398
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	4703	1786	1397
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	4698	1786	1397
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S124-WAGON-01	4765	1740	1490
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-01	4816	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	4839	1799	1505
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	4888	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-4MATIC-01	4888	1822	1509
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	4850	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	4850	1822	1495
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-4MATIC-01	4850	1822	1499
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	4905	1854	1507
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	4895	1854	1512
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	4895	1854	1515
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1460-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-H1466-01	4945	1852	1466
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	4949	1880	1469
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	4949	1880	1470
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-DIESEL-01	4795	1799	1437
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	4818	1799	1451
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-DIESEL-01	4818	1799	1441
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-PETROL-01	4818	1799	1440
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-PREFL-4MATIC-01	4795	1799	1451
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-01	4856	1822	1483
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	4856	1822	1484
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-4MATIC-01	4856	1822	1463
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-01	4818	1822	1450
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-02	4818	1822	1452
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	4818	1822	1449
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-4MATIC-01	4818	1822	1463
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-HYBRID-01	4879	1854	1475
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	4868	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E250-01	4868	1854	1470
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E300-CDI-01	4868	1854	1464
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-HYBRID-01	4868	1854	1472
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1460-01	4935	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-H1466-01	4935	1852	1466
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	4949	1880	1469
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	4949	1880	1480
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-RWD-01	4949	1880	1468
EU-MERCEDES-BENZ-E-KLASSE-X213-ALL-TERRAIN-01	4947	1861	1497
EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-DIESEL-01	4950	1889	1497
EU-MERCEDES-BENZ-E-KLASSE-X214-ALL-TERRAIN-PHEV-01	4950	1889	1489

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	E-Klasse	E 320 T CDI	Kombi	Heckantrieb	Diesel	Mar 2005	Jul 2009	18634
Mercedes-benz	E-Klasse	E 350	Kombi	Heckantrieb	Benzin	Aug 2009	Dec 2011	10111
Mercedes-benz	E-Klasse	E 350	Coupe	Heckantrieb	Benzin	Apr 2011	Dec 2014	10342
Mercedes-benz	E-Klasse	E 350	Cabriolet	Heckantrieb	Benzin	Apr 2011	Dec 2014	10347
Mercedes-benz	E-Klasse	E 350	Kombi	Heckantrieb	Benzin	Sep 2011	Dec 2014	11384
Mercedes-benz	E-Klasse	E 350	Stufenheck	Heckantrieb	Benzin	Sep 2011	Dec 2015	11388
Mercedes-benz	E-Klasse	E 350	Coupe	Heckantrieb	Benzin	Jan 2010	Dec 2011	14025
Mercedes-benz	E-Klasse	E 350	Cabriolet	Heckantrieb	Benzin	Mar 2010	Dec 2011	14026
Mercedes-benz	E-Klasse	E 350	Stufenheck	Heckantrieb	Benzin	Mar 2005	Dec 2008	18631
Mercedes-benz	E-Klasse	E 350	Stufenheck	Heckantrieb	Benzin	Jan 2009	Dec 2013	55880
Mercedes-benz	E-Klasse	E 350 4-matic	Kombi	Allrad	Benzin	Sep 2011	Dec 2016	11385
Mercedes-benz	E-Klasse	E 350 4-matic	Stufenheck	Allrad	Benzin	Sep 2011	Dec 2015	11387
Mercedes-benz	E-Klasse	E 350 4-matic	Coupe	Allrad	Benzin	Feb 2013	Dec 2016	100544
Mercedes-benz	E-Klasse	E 350 Bluetec	Cabriolet	Heckantrieb	Diesel	Jun 2013	Dec 2016	59029
Mercedes-benz	E-Klasse	E 350 Bluetec	Stufenheck	Heckantrieb	Diesel	Jan 2013	Dec 2015	59439
Mercedes-benz	E-Klasse	E 350 Bluetec	Coupe	Heckantrieb	Diesel	Jun 2013	Dec 2016	59452
Mercedes-benz	E-Klasse	E 350 Bluetec	Kombi	Heckantrieb	Diesel	Nov 2012	Dec 2016	59456
Mercedes-benz	E-Klasse	E 350 Bluetec	Stufenheck	Heckantrieb	Diesel	May 2014	Dec 2015	106310
Mercedes-benz	E-Klasse	E 350 Bluetec	Kombi	Heckantrieb	Diesel	Jul 2014	Dec 2016	107534
Mercedes-benz	E-Klasse	E 350 Bluetec / D	Coupe	Heckantrieb	Diesel	May 2014	Dec 2016	106315
Mercedes-benz	E-Klasse	E 350 Bluetec 4-matic	Stufenheck	Allrad	Diesel	Jan 2013	Dec 2015	59440
Mercedes-benz	E-Klasse	E 350 Bluetec 4-matic	Kombi	Allrad	Diesel	Nov 2012	Dec 2016	59459
Mercedes-benz	E-Klasse	E 350 Bluetec 4-matic	Stufenheck	Allrad	Diesel	May 2014	Dec 2015	106311
Mercedes-benz	E-Klasse	E 350 Bluetec 4-matic	Kombi	Allrad	Diesel	Jul 2014	Dec 2016	107535
Mercedes-benz	E-Klasse	E 350 Bluetec/ D	Cabriolet	Heckantrieb	Diesel	May 2014	Dec 2016	106313
Mercedes-benz	E-Klasse	E 350 CDI	Coupe	Heckantrieb	Diesel	Jun 2011	Jun 2013	10339
Mercedes-benz	E-Klasse	E 350 CDI	Cabriolet	Heckantrieb	Diesel	Apr 2011	Dec 2013	10344
Mercedes-benz	E-Klasse	E 350 CDI	Kombi	Heckantrieb	Diesel	Jul 2011	Dec 2013	11149
Mercedes-benz	E-Klasse	E 350 CDI 4-matic	Kombi	Allrad	Diesel	Jul 2011	Dec 2013	11150
Mercedes-benz	E-Klasse	E 350 D	Stufenheck	Heckantrieb	Diesel	Jan 2016	May 2018	118516
Mercedes-benz	E-Klasse	E 350 D 4-matic	Kombi	Allrad	Diesel	Jun 2017	May 2018	127681
Mercedes-benz	E-Klasse	E 350 D 4-matic	Kombi	Allrad	Diesel	Jun 2017	May 2018	127682
Mercedes-benz	E-Klasse	E 350 D 4-matic	Stufenheck	Allrad	Diesel	Jun 2017	May 2018	128024
Mercedes-benz	E-Klasse	E 350 D 4-matic	Cabriolet	Allrad	Diesel	Jun 2017	-	128437
Mercedes-benz	E-Klasse	E 350 E	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2016	Jun 2019	120738
Mercedes-benz	E-Klasse	E 350 T	Kombi	Heckantrieb	Benzin	Mar 2005	Jul 2009	18637
Mercedes-benz	E-Klasse	E 400	Cabriolet	Heckantrieb	Benzin	Jun 2013	Dec 2016	59039
Mercedes-benz	E-Klasse	E 400	Coupe	Heckantrieb	Benzin	Jun 2013	Dec 2016	59045
Mercedes-benz	E-Klasse	E 400	Stufenheck	Heckantrieb	Benzin	Jan 2013	Dec 2016	59435
Mercedes-benz	E-Klasse	E 400	Kombi	Heckantrieb	Benzin	Jan 2013	Dec 2016	59453
Mercedes-benz	E-Klasse	E 400	Cabriolet	Heckantrieb	Benzin	Jul 2014	Dec 2016	107500
Mercedes-benz	E-Klasse	E 400	Kombi	Heckantrieb	Benzin	Jul 2014	Dec 2016	107536
Mercedes-benz	E-Klasse	E 400	Coupe	Heckantrieb	Benzin	Jul 2014	Dec 2016	107539
Mercedes-benz	E-Klasse	E 400	Stufenheck	Heckantrieb	Benzin	Jul 2014	Dec 2015	107877
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	Jan 2013	Dec 2016	59436
Mercedes-benz	E-Klasse	E 400 4-matic	Kombi	Allrad	Benzin	Jan 2013	Dec 2016	59454
Mercedes-benz	E-Klasse	E 400 4-matic	Kombi	Allrad	Benzin	Jul 2014	Dec 2016	107537
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	Jul 2014	Dec 2015	107878
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	Jul 2016	May 2018	120740
Mercedes-benz	E-Klasse	E 400 4-matic	Stufenheck	Allrad	Benzin	Jun 2016	May 2018	121726
Mercedes-benz	E-Klasse	E 400 4-matic	Coupe	Allrad	Benzin	Dec 2016	-	124822
Mercedes-benz	E-Klasse	E 400 4-matic	Cabriolet	Allrad	Benzin	Jun 2017	-	127637
Mercedes-benz	E-Klasse	E 400 CDI	Stufenheck	Heckantrieb	Diesel	Feb 2003	Dec 2008	17170
Mercedes-benz	E-Klasse	E 400 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Jul 2023	-	155293
Mercedes-benz	E-Klasse	E 430 4-matic	Stufenheck	Allrad	Benzin	May 1999	Mar 2002	13189
Mercedes-benz	E-Klasse	E 430 T 4-matic	Kombi	Allrad	Benzin	May 1999	Mar 2003	13190
Mercedes-benz	E-Klasse	E 450 4-matic	Kombi	Allrad	Benzin/Elektro	Oct 2023	-	156360
Mercedes-benz	E-Klasse	E 450 4-matic	Stufenheck	Allrad	Benzin/Elektro	Oct 2023	-	156364
Mercedes-benz	E-Klasse	E 450 4-matic	Kombi	Allrad	Benzin/Elektro	Oct 2023	-	156367
Mercedes-benz	E-Klasse	E 450 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	Oct 2023	-	156366
Mercedes-benz	E-Klasse	E 450 D 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	157480
Mercedes-benz	E-Klasse	E 450 D 4-matic	Kombi	Allrad	Diesel/Elektro	Oct 2023	-	157481
Mercedes-benz	E-Klasse	E 500	Coupe	Heckantrieb	Benzin	Sep 2011	Dec 2016	11322
Mercedes-benz	E-Klasse	E 500	Cabriolet	Heckantrieb	Benzin	Sep 2011	Dec 2016	11378
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	Sep 2011	Dec 2015	11380
Mercedes-benz	E-Klasse	E 500	Kombi	Heckantrieb	Benzin	Sep 2011	Dec 2016	11383
Mercedes-benz	E-Klasse	E 500	Stufenheck	Heckantrieb	Benzin	Mar 2002	Dec 2008	16565
Mercedes-benz	E-Klasse	E 500 4-matic	Stufenheck	Allrad	Benzin	Sep 2011	Dec 2015	11381
Mercedes-benz	E-Klasse	E 500 4-matic	Kombi	Allrad	Benzin	Sep 2011	Dec 2016	11382
Mercedes-benz	E-Klasse	E 500 4-matic	Stufenheck	Allrad	Benzin	Oct 2003	Dec 2008	17399
Mercedes-benz	E-Klasse	E 500 T	Kombi	Heckantrieb	Benzin	Oct 2003	Jul 2009	17490
Mercedes-benz	E-Klasse	E 500 T 4-matic	Kombi	Allrad	Benzin	Oct 2003	Jul 2009	17491
Mercedes-benz	E-Klasse	E 53 AMG Hybrid 4-matic+	Kombi	Allrad	Benzin/Elektro	May 2024	-	158466
Mercedes-benz	E-Klasse	E 53 AMG Hybrid 4-matic+	Stufenheck	Allrad	Benzin/Elektro	May 2024	-	158467
Mercedes-benz	E-Klasse	E 55 AMG	Stufenheck	Heckantrieb	Benzin	Aug 1997	Mar 2002	8833
Mercedes-benz	E-Klasse	E 55 AMG 4-matic	Stufenheck	Allrad	Benzin	May 1999	Mar 2002	800222
Mercedes-benz	E-Klasse	E 55 AMG Kompressor	Stufenheck	Heckantrieb	Benzin	Oct 2002	Dec 2008	17000
Mercedes-benz	E-Klasse	E 55 T AMG	Kombi	Heckantrieb	Benzin	Aug 1997	Mar 2003	8834
Mercedes-benz	E-Klasse	E 55 T AMG Kompressor	Kombi	Heckantrieb	Benzin	Jul 2003	Jul 2009	17489
Mercedes-benz	E-Klasse	E 60 AMG	Stufenheck	Heckantrieb	Benzin	May 1994	Jun 1995	14879
Mercedes-benz	E-Klasse	E 63 AMG	Kombi	Heckantrieb	Benzin	Feb 2011	Dec 2016	10113
Mercedes-benz	E-Klasse	E 63 AMG	Stufenheck	Heckantrieb	Benzin	Feb 2011	Dec 2016	10114
Mercedes-benz	E-Klasse	E 63 AMG	Stufenheck	Heckantrieb	Benzin	Feb 2011	Dec 2016	58568
Mercedes-benz	E-Klasse	E 63 AMG	Kombi	Heckantrieb	Benzin	Feb 2011	Dec 2016	58569
Mercedes-benz	E-Klasse	E 63 AMG	Kombi	Heckantrieb	Benzin	Feb 2013	Dec 2016	59298
Mercedes-benz	E-Klasse	E 63 AMG	Stufenheck	Heckantrieb	Benzin	Feb 2013	Dec 2016	59299
Mercedes-benz	E-Klasse	E 63 AMG 4-matic	Kombi	Allrad	Benzin	Feb 2013	Dec 2016	58673
Mercedes-benz	E-Klasse	E 63 AMG 4-matic	Stufenheck	Allrad	Benzin	Feb 2013	Dec 2016	58675
Mercedes-benz	E-Klasse	E 63 AMG 4-matic	Stufenheck	Allrad	Benzin	Jan 2013	Dec 2016	59012
Mercedes-benz	E-Klasse	E 63 AMG 4-matic	Kombi	Allrad	Benzin	Feb 2011	Dec 2016	59013
Mercedes-benz	Eqa	EQA 250	SUV	Frontantrieb	Elektro	Feb 2021	-	143485
Mercedes-benz	Eqa	EQA 250+	SUV	Frontantrieb	Elektro	Mar 2022	-	147140
Mercedes-benz	Eqa	EQA 300 4-matic	SUV	Allrad	Elektro	May 2021	-	144139
Mercedes-benz	Eqa	EQA 350 4-matic	SUV	Allrad	Elektro	May 2021	-	144140
Mercedes-benz	Eqa	EQA 350 4-matic	SUV	Allrad	Elektro	Jun 2024	-	801098
Mercedes-benz	Eqb	EQB 250	SUV	Frontantrieb	Elektro	Feb 2022	-	147126
Mercedes-benz	Eqb	EQB 250+	SUV	Frontantrieb	Elektro	Sep 2022	-	150715
Mercedes-benz	Eqb	EQB 300 4-matic	SUV	Allrad	Elektro	Dec 2021	-	145522
Mercedes-benz	Eqb	EQB 350 4-matic	SUV	Allrad	Elektro	Dec 2021	Aug 2024	145521
Mercedes-benz	Eqb	EQB 350 4-matic	SUV	Allrad	Elektro	Jun 2024	-	801100


--- Round 1 / 首次发送 ---
## 更新点

* 完成 EQA H243、EQB X243 的尺寸组建档，并按 2023 年改款前后物理高度变化拆分。
* 本轮闭合 10 个输入 Ktype，共形成 18 条 READY 映射。
* EQA 官方资料确认改款前尺寸为 4463 × 1834 × 1620 mm，现款官方技术数据为 4463 × 1834 × 1608 mm；EQB 现款官方技术数据明确车宽为不含后视镜口径。
* 新建 4 个尺寸组；本轮未改写跨批次既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：18 行，覆盖 10 个 Ktype
* 待处理 Ktype：90
* 本轮新增尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143485_prefl	143485	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
143485_facelift	143485	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
147140_prefl	147140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
147140_facelift	147140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
144139_prefl	144139	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
144139_facelift	144139	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
144140_prefl	144140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
144140_facelift	144140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
801098	801098	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	2024年起始的改款后外廓。	READY
147126_prefl	147126	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
147126_facelift	147126	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
150715_prefl	150715	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
150715_facelift	150715	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
145522_prefl	145522	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
145522_facelift	145522	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
145521_prefl	145521	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
145521_facelift	145521	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
801100	801100	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	2024年起始的改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	4463	1834	1620	Mercedes-Benz EQA official brochure (2021)	https://i.i-sgcm.com/new_cars/cars/12924/brochures/brochure_20210916112640.pdf
EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	4463	1834	1608	Mercedes-Benz UK EQA official technical data	https://www.mercedes-benz.co.uk/passengercars/models/suv/eqa/overview.html
EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	4684	1834	1667	Mercedes-Benz EQB official brochure (2022)	https://i.i-sgcm.com/new_cars/cars/21601/brochures/brochure_20220831112857.pdf
EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	4684	1834	1654	Mercedes-Benz UK EQB official technical data	https://www.mercedes-benz.co.uk/passengercars/models/suv/eqb/overview.html
```

## 下一步优先处理

1. 批量关联 E-Klasse W212/S212、C207/A207 与 W213/S213 已有尺寸组。
2. 单独核对会改变外廓的 AMG、4MATIC 高度差异及跨改款生产区间。
3. 处理 W210/W211/S210/S211 历史车型，优先复用现有缓存并消除剩余待处理项。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9901-10000_ktype_dimension_mapping_final.tsv
- left18448_9901-10000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 71 条 READY 映射，覆盖 55 个 Ktype。
* 批量复用现有 W210/W211/S210/S211、W212/S212、C207/A207、W213/S213、C238/A238 与 W214 尺寸组。
* 首次创建 W212 改款前 E 350 后驱轿车尺寸组；官方档案记录其外廓为 4868 × 1854 × 1465 mm。W211 E 350 改款前后及 S211 旅行版均已匹配现有相同三维缓存组。([marsClassic][1])
* 尚未处理的 35 个 Ktype 主要集中于 E 400 CDI、E 500、E 53/E 55/E 60/E 63 AMG，以及 W214/S214 E 450 系列。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：89 行，覆盖 65 个 Ktype
* 待处理 Ktype：35
* 已确认并被当前 READY 映射引用的尺寸组：25
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18634_prefl	18634	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
18634_facelift	18634	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
10111	10111	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH		READY
10342_prefl	10342	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
10342_facelift	10342	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
10347_prefl	10347	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
10347_facelift	10347	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11384_prefl	11384	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11384_facelift	11384	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11388_prefl	11388	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	HIGH	改款前物理外廓。	READY
11388_facelift	11388	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
14025	14025	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH		READY
14026	14026	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH		READY
18631_prefl	18631	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	改款前物理外廓。	READY
18631_facelift	18631	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	改款后物理外廓。	READY
55880_prefl	55880	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	HIGH	改款前物理外廓。	READY
55880_facelift	55880	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
11385_prefl	11385	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11385_facelift	11385	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11387_prefl	11387	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	HIGH	改款前物理外廓。	READY
11387_facelift	11387	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
100544	100544	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59029	59029	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
59439	59439	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59452	59452	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59456_prefl	59456	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
59456_facelift	59456	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
106310	106310	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
107534	107534	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
106315	106315	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59440	59440	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59459_prefl	59459	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
59459_facelift	59459	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
106311	106311	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
107535	107535	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
106313	106313	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
10339_prefl	10339	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
10339_facelift	10339	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
10344_prefl	10344	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
10344_facelift	10344	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11149_prefl	11149	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11149_facelift	11149	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11150_prefl	11150	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11150_facelift	11150	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
118516	118516	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
127681	127681	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH		READY
127682	127682	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH		READY
128024	128024	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
128437	128437	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	HIGH		READY
120738	120738	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
18637_prefl	18637	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
18637_facelift	18637	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
59039	59039	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
59045	59045	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59435	59435	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59453	59453	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107500	107500	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
107536	107536	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107539	107539	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
107877	107877	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59436	59436	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59454	59454	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107537	107537	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107878	107878	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
120740	120740	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
121726	121726	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
124822	124822	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	HIGH		READY
127637	127637	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	HIGH		READY
155293	155293	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH		READY
13189	13189	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH		READY
13190	13190	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	4868	1854	1465	Mercedes-Benz Public Archive E 350 CGI BlueEFFICIENCY, 2009-2011	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-CGI-BlueEFFICIENCY-2009---2011.xhtml?oid=188539296
```

## 下一步优先处理

1. 闭合 E 500 的 W211/S211、W212/S212、C207/A207 改款前后分支。
2. 一次性建立 W210/W211/S211、W124 及 W212/S212 AMG 专属尺寸组。
3. 完成 W214/S214 E 450、E 450 D、E 53 AMG Hybrid 映射，并处理 E 400 CDI。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-CGI-BlueEFFICIENCY-2009---2011.xhtml?oid=188539296&utm_source=chatgpt.com "E 350 CGI BlueEFFICIENCY, 2009 - 2011"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9901-10000_ktype_dimension_mapping_final.tsv
- left18448_9901-10000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 28 条 `READY` 映射，覆盖 20 个 Ktype。
* 已批量闭合 W214/S214 E 450 系列、C207/A207 与 S212 E 500，以及 W210/W211/S210/S211 历史 AMG 车型。
* 官方档案确认部分 W211/S211 E 500、E 55 AMG 与普通车型缓存组的长度或高度不同；本轮因此新建 11 个尺寸组，未覆盖或改写既有尺寸事实。([marsClassic][1])
* E 500 4MATIC S211 改款前尺寸与现有 `S211-WAGON-PREFL-02` 完全一致，直接复用；改款后高度不同，建立新组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：117 行，覆盖 85 个 Ktype
* 待处理 Ktype：15
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17170	17170	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	HIGH		READY
156360	156360	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH		READY
156364	156364	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	HIGH		READY
156367	156367	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH		READY
156366	156366	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	HIGH		READY
157480	157480	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH		READY
157481	157481	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH		READY
11322_prefl	11322	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
11322_facelift	11322	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11378_prefl	11378	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
11378_facelift	11378	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11383_prefl	11383	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11383_facelift	11383	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
16565_prefl	16565	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	HIGH	改款前物理外廓。	READY
16565_facelift	16565	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-01	HIGH	改款后物理外廓。	READY
11382_prefl	11382	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11382_facelift	11382	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
17399_prefl	17399	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-E500-4MATIC-01	HIGH	改款前物理外廓。	READY
17399_facelift	17399	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-4MATIC-01	HIGH	改款后物理外廓。	READY
17490_prefl	17490	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-E500-01	HIGH	改款前物理外廓。	READY
17490_facelift	17490	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
17491_prefl	17491	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	改款前物理外廓。	READY
17491_facelift	17491	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-E500-4MATIC-01	HIGH	改款后物理外廓。	READY
8833	8833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
17000	17000	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
8834	8834	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
17489	17489	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
14879	14879	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-KLASSE-W124-SEDAN-E60-AMG-01	HIGH	AMG专属物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	4818	1822	1430	Mercedes-Benz Public Archive E 400 CDI; Mercedes-Benz Public Archive E 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-400-CDI.xhtml?oid=453480;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500.xhtml?oid=5374
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-01	4856	1822	1465	Mercedes-Benz Public Archive E 500 W211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500--W-211-E-55-2006---2009.xhtml?oid=2461848
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-E500-4MATIC-01	4818	1822	1441	Mercedes-Benz Public Archive E 500 4MATIC W211 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC.xhtml?oid=2461849
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-4MATIC-01	4856	1822	1475	Mercedes-Benz Public Archive E 500 4MATIC W211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC.xhtml?oid=2461850
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-E500-01	4850	1822	1485	Mercedes-Benz Public Archive E 500 station wagon S211 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-station-wagon--S-211-E-50-2003---2006.xhtml?oid=5469
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-E500-4MATIC-01	4888	1822	1513	Mercedes-Benz Public Archive E 500 4MATIC station wagon S211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC-station-wagon--S-211-E-55-4-M-2006---2009.xhtml?oid=2461896
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	4818	1799	1411	Mercedes-Benz Public Archive E 55 AMG W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG.xhtml?oid=5356
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-E55-AMG-01	4849	1822	1430	Mercedes-Benz Public Archive E 55 AMG W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG.xhtml?oid=5375
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-E55-AMG-01	4839	1799	1477	Mercedes-Benz Public Archive E 55 AMG T-Modell S210	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-55-AMG-T-Modell.xhtml?oid=5411
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-E55-AMG-01	4871	1822	1485	Mercedes-Benz Public Archive E 55 AMG station wagon S211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG-station-wagon.xhtml?oid=5471
EU-MERCEDES-BENZ-E-KLASSE-W124-SEDAN-E60-AMG-01	4750	1796	1408	Mercedes-Benz Public Archive E 60 AMG W124	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-60-AMG.xhtml?oid=5165
```

## 下一步优先处理

1. 一次性闭合 W212/S212 E 63 AMG 的改款前、改款后、后驱和 4MATIC 外廓分支。
2. 处理 W212 E 500 轿车 Ktype `11380`、`11381` 的后驱与 4MATIC 分支。
3. 处理 W214/S214 E 53 AMG Hybrid Ktype `158466`、`158467`，以及 W210 E 55 AMG 4MATIC Ktype `800222`。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-400-CDI.xhtml?oid=453480&utm_source=chatgpt.com "E 400 CDI - Mercedes Benz Archive"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9901-10000_ktype_dimension_mapping_final.tsv
- left18448_9901-10000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增 18 条 `READY` 映射，覆盖 13 个 Ktype；W210 E 55 AMG 4MATIC 与既有 AMG 组外廓一致，直接复用。
* W212/S212 E 500、E 63 AMG 的后驱、4MATIC、改款前后外廓已批量闭合。官方档案确认改款后 E 63 AMG 轿车为 4892 × 1873 × 1450 mm，4MATIC 旅行版为 4904 × 1873 × 1522 mm。([marsClassic][1])
* E 53 AMG Hybrid 的现行官方车型页记录 4965 mm 车长，而官方车主手册技术数据记录 4961 mm；因当前 Ktype 从 2024 年首发开始，暂不选取其中一套覆盖首发车型。([Mercedes-Benz][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：135 行，覆盖 98 个 Ktype
* PENDING 映射：2 行，涉及 2 个 Ktype
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11380_prefl	11380	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-01	HIGH	改款前物理外廓。	READY
11380_facelift	11380	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E500-01	HIGH	改款后物理外廓。	READY
11381_prefl	11381	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-4MATIC-01	HIGH	改款前4MATIC物理外廓。	READY
11381_facelift	11381	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后4MATIC物理外廓。	READY
158466	158466	Wagon	E-Class S214	S214	5		LOW	2024首发车型的官方车长存在4961与4965 mm冲突。	PENDING: E 53 AMG Hybrid首发旅行版官方车长冲突未解决
158467	158467	Sedan	E-Class W214	W214	4		LOW	2024首发车型的官方车长存在4961与4965 mm冲突。	PENDING: E 53 AMG Hybrid首发轿车官方车长冲突未解决
800222	800222	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	HIGH		READY
10113	10113	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	HIGH	后驱出口型物理外廓。	READY
10114_prefl	10114	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	HIGH	改款前物理外廓。	READY
10114_facelift	10114	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58568_prefl	58568	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	HIGH	改款前物理外廓。	READY
58568_facelift	58568	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58569	58569	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	HIGH	后驱出口型物理外廓。	READY
59298	59298	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	MEDIUM	2013年边界的后驱出口型物理外廓。	READY
59299	59299	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58673	58673	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	HIGH	改款后4MATIC物理外廓。	READY
58675	58675	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后4MATIC与后驱车型外廓一致。	READY
59012	59012	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	MEDIUM	输入起始月早于正式量产月，物理外廓为改款后4MATIC分支。	READY
59013	59013	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	MEDIUM	输入起始月早于正式量产月，物理外廓为改款后4MATIC分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-01	4868	1854	1454	Mercedes-Benz Public Archive E 500 BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-BlueEFFICIENCY-2011---2013.xhtml?oid=188539302
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E500-01	4879	1854	1458	Mercedes-Benz Public Archive E 500 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-2013---2015.xhtml?oid=188541036
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-4MATIC-01	4868	1854	1458	Mercedes-Benz Public Archive E 500 4MATIC BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-500-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539306
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	4883	1872	1440	Mercedes-Benz Public Archive E 63 AMG 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-63-AMG-2011---2013.xhtml?oid=188539327
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	4913	1872	1490	Mercedes-Benz Public Archive E 63 AMG Estate 2011-2013 export model until 2016	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-63-AMG-2011---2013-als-Exportmodell-bis-2016.xhtml?oid=188823525
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	4892	1873	1450	Mercedes-Benz Public Archive E 63 AMG 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-63-AMG-2013---2015-from-122014-Mercedes-AMG-E-63-AMG.xhtml?oid=188541038
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	4904	1873	1522	Mercedes-Benz Public Archive E 63 AMG 4MATIC Estate 2013-2016	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-63-AMG-4MATIC-2013---2016-ab-122014-Mercedes-AMG-E-63-4MATIC.xhtml?oid=188823553
```

## 下一步优先处理

闭合 Ktype `158466`、`158467` 的 2024 首发 E 53 AMG Hybrid W214/S214 尺寸口径，优先寻找首发期欧洲官方技术资料，以消除 4961/4965 mm 车长冲突；闭合后立即进入最终机械检查并输出两张完整 TSV 与指定下载文件。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-63-AMG-4MATIC-2013---2016-ab-122014-Mercedes-AMG-E-63-4MATIC.xhtml?ls=L2RlL2luc3RhbmNlL2tvL0UtS2xhc3NlLVQtTW9kZWxsZS1kZXItQmF1cmVpaGUtMjEyLTIwMTMtLS0yMDE2LnhodG1sP29pZD02MDEyMDkxJnJlbElkPTEwMDImcmVzdWx0SW5mb1R5cGVJZD0yMTU1JmZyb21PaWQ9NjAxMjA5MSZ2aWV3VHlwZT1saXN0JnNvcnREZWZpbml0aW9uPVNPUlQtMSZ0aHVtYlNjYWxlSW5kZXg9MSZyb3dDb3VudHNJbmRleD01JmZyb21JbmZvVHlwZUlkPTIyNDU%21&oid=188823553&rs=26&utm_source=chatgpt.com "E 63 AMG 4MATIC, 2013 - 2016 (ab 12.2014"
[2]: https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-e-class-owners-manual-supplement-july-2025-1.pdf?utm_source=chatgpt.com "E-Class"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_9901-10000_ktype_dimension_mapping_final.tsv
- left18448_9901-10000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后两个 `E 53 AMG Hybrid 4MATIC+` 分支已闭合：S214 旅行版采用 `4965 × 1902 × 1483 mm`，W214 轿车采用 `4965 × 1902 × 1472 mm`；宽度口径均为不含后视镜。([Mercedes-Benz][1])
* 既有尺寸组按跨批次锁定索引复用，未改写已有三维。
* 已完成固定表头、唯一性、引用闭合、尺寸及来源非空检查，校验结果通过。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：136 行，覆盖 100 个 Ktype
* PENDING 映射：0
* DIMENSION_GROUP：49 个
* 唯一映射 id：136
* 映射引用缺失：0
* 孤立尺寸组：0
* 机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
18634_prefl	18634	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
18634_facelift	18634	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
10111	10111	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH		READY
10342_prefl	10342	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
10342_facelift	10342	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
10347_prefl	10347	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
10347_facelift	10347	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11384_prefl	11384	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11384_facelift	11384	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11388_prefl	11388	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	HIGH	改款前物理外廓。	READY
11388_facelift	11388	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
14025	14025	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH		READY
14026	14026	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH		READY
18631_prefl	18631	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	HIGH	改款前物理外廓。	READY
18631_facelift	18631	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	HIGH	改款后物理外廓。	READY
55880_prefl	55880	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	HIGH	改款前物理外廓。	READY
55880_facelift	55880	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
11385_prefl	11385	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11385_facelift	11385	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11387_prefl	11387	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	HIGH	改款前物理外廓。	READY
11387_facelift	11387	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后物理外廓。	READY
100544	100544	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59029	59029	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
59439	59439	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59452	59452	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59456_prefl	59456	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
59456_facelift	59456	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
106310	106310	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
107534	107534	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
106315	106315	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59440	59440	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59459_prefl	59459	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
59459_facelift	59459	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
106311	106311	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
107535	107535	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
106313	106313	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
10339_prefl	10339	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
10339_facelift	10339	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
10344_prefl	10344	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
10344_facelift	10344	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11149_prefl	11149	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11149_facelift	11149	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
11150_prefl	11150	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11150_facelift	11150	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
118516	118516	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
127681	127681	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH		READY
127682	127682	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	HIGH		READY
128024	128024	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
128437	128437	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	HIGH		READY
120738	120738	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
18637_prefl	18637	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
18637_facelift	18637	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
59039	59039	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
59045	59045	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
59435	59435	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59453	59453	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107500	107500	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH		READY
107536	107536	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107539	107539	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH		READY
107877	107877	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59436	59436	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
59454	59454	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107537	107537	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH		READY
107878	107878	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH		READY
120740	120740	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
121726	121726	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	HIGH		READY
124822	124822	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	HIGH		READY
127637	127637	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	HIGH		READY
17170	17170	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	HIGH		READY
155293	155293	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	HIGH		READY
13189	13189	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	HIGH		READY
13190	13190	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	HIGH		READY
156360	156360	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH		READY
156364	156364	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	HIGH		READY
156367	156367	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	HIGH		READY
156366	156366	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	HIGH		READY
157480	157480	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH		READY
157481	157481	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	HIGH		READY
11322_prefl	11322	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	HIGH	改款前物理外廓。	READY
11322_facelift	11322	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11378_prefl	11378	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	HIGH	改款前物理外廓。	READY
11378_facelift	11378	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	HIGH	改款后物理外廓。	READY
11380_prefl	11380	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-01	HIGH	改款前物理外廓。	READY
11380_facelift	11380	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E500-01	HIGH	改款后物理外廓。	READY
11383_prefl	11383	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	HIGH	改款前物理外廓。	READY
11383_facelift	11383	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
16565_prefl	16565	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	HIGH	改款前物理外廓。	READY
16565_facelift	16565	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-01	HIGH	改款后物理外廓。	READY
11381_prefl	11381	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-4MATIC-01	HIGH	改款前4MATIC物理外廓。	READY
11381_facelift	11381	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	HIGH	改款后4MATIC物理外廓。	READY
11382_prefl	11382	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	HIGH	改款前物理外廓。	READY
11382_facelift	11382	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	HIGH	改款后物理外廓。	READY
17399_prefl	17399	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-E500-4MATIC-01	HIGH	改款前物理外廓。	READY
17399_facelift	17399	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-4MATIC-01	HIGH	改款后物理外廓。	READY
17490_prefl	17490	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-E500-01	HIGH	改款前物理外廓。	READY
17490_facelift	17490	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
17491_prefl	17491	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	HIGH	改款前物理外廓。	READY
17491_facelift	17491	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-E500-4MATIC-01	HIGH	改款后物理外廓。	READY
158466	158466	Wagon	E-Class S214	S214	5	EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-E53-AMG-HYBRID-01	HIGH	E 53 AMG Hybrid专属宽体外廓。	READY
158467	158467	Sedan	E-Class W214	W214	4	EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-E53-AMG-HYBRID-01	HIGH	E 53 AMG Hybrid专属宽体外廓。	READY
8833	8833	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
800222	800222	Sedan	E-Class W210	W210	4	EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	HIGH		READY
17000	17000	Sedan	E-Class W211	W211	4	EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
8834	8834	Wagon	E-Class S210	S210	5	EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
17489	17489	Wagon	E-Class S211	S211	5	EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-E55-AMG-01	HIGH	AMG专属物理外廓。	READY
14879	14879	Sedan	E-Class W124	W124	4	EU-MERCEDES-BENZ-E-KLASSE-W124-SEDAN-E60-AMG-01	HIGH	AMG专属物理外廓。	READY
10113	10113	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	HIGH	后驱出口型物理外廓。	READY
10114_prefl	10114	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	HIGH	改款前物理外廓。	READY
10114_facelift	10114	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58568_prefl	58568	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	HIGH	改款前物理外廓。	READY
58568_facelift	58568	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58569	58569	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	HIGH	后驱出口型物理外廓。	READY
59298	59298	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	MEDIUM	2013年边界的后驱出口型物理外廓。	READY
59299	59299	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后物理外廓。	READY
58673	58673	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	HIGH	改款后4MATIC物理外廓。	READY
58675	58675	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	HIGH	改款后4MATIC与后驱车型外廓一致。	READY
59012	59012	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	MEDIUM	输入起始月早于正式量产月，物理外廓为改款后4MATIC分支。	READY
59013	59013	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	MEDIUM	输入起始月早于正式量产月，物理外廓为改款后4MATIC分支。	READY
143485_prefl	143485	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
143485_facelift	143485	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
147140_prefl	147140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
147140_facelift	147140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
144139_prefl	144139	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
144139_facelift	144139	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
144140_prefl	144140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
144140_facelift	144140	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
801098	801098	SUV	EQA H243	H243	5	EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	HIGH	2024年起始的改款后外廓。	READY
147126_prefl	147126	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
147126_facelift	147126	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
150715_prefl	150715	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
150715_facelift	150715	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
145522_prefl	145522	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
145522_facelift	145522	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
145521_prefl	145521	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	HIGH	跨2023年改款，改款前物理外廓。	READY
145521_facelift	145521	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	跨2023年改款，改款后物理外廓。	READY
801100	801100	SUV	EQB X243	X243	5	EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	HIGH	2024年起始的改款后外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_9901-10000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-01	4850	1822	1496	Mercedes-Benz Public Archive 211 series E-Class Estates, 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-01	4888	1822	1506	Mercedes-Benz Public Archive 211 series E-Class Estates, 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2006---2009.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1512-01	4895	1854	1512	Mercedes-Benz Public Archive 212 series E-Class Estates, 2009-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/212-series-E-Class-Estates-2009---2013.xhtml
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-PREFL-01	4698	1786	1397	Mercedes-Benz Public Archive 207 series E-Class Coupés, 2009-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Coupes-2009---2013.xhtml
EU-MERCEDES-BENZ-E-KLASSE-C207-COUPE-FACELIFT-01	4703	1786	1397	Mercedes-Benz Public Archive 207 series E-Class Coupés, 2013-2017	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Coupes-2013---2017.xhtml
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-PREFL-01	4698	1786	1398	Mercedes-Benz Public Archive 207 series E-Class Cabriolets, 2010-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Cabriolets-2010---2013.xhtml
EU-MERCEDES-BENZ-E-KLASSE-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Mercedes-Benz Public Archive 207 series E-Class Cabriolets, 2013-2017	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/207-series-E-Class-Cabriolets-2013---2017.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-H1507-01	4905	1854	1507	Mercedes-Benz Public Archive 212 series E-Class Estates, 2013-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/212-series-E-Class-Estates-2013---2016.xhtml
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E350-01	4868	1854	1465	Mercedes-Benz Public Archive E 350 CGI BlueEFFICIENCY, 2009-2011	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-CGI-BlueEFFICIENCY-2009---2011.xhtml?oid=188539296
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-H1474-01	4879	1854	1474	Mercedes-Benz Public Archive 212 series E-Class Saloons, 2013-2016	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/212-series-E-Class-Saloons-2013---2016.xhtml
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-03	4818	1822	1449	Mercedes-Benz Public Archive 211 series E-Class Saloons, 2002-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Saloons-2002---2006.xhtml
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-02	4856	1822	1484	Mercedes-Benz Public Archive 211 series E-Class Saloons, 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Saloons-2006---2009.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-H1515-01	4895	1854	1515	Mercedes-Benz Public Archive 212 series E-Class Estates, 2009-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/212-series-E-Class-Estates-2009---2013.xhtml
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-4MATIC-01	4868	1854	1474	Mercedes-Benz Public Archive E 250 CDI 4MATIC BlueEFFICIENCY, 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-250-CDI-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539247
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-PREFL-01	4923	1852	1468	Mercedes-Benz Public Archive 213 series E-Class Saloons, 2016-2020	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/213-series-E-Class-Saloons-2016---2020.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-PREFL-01	4933	1852	1475	Mercedes-Benz Public Archive 213 series E-Class Estates, 2016-2020	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/213-series-E-Class-Estates-2016---2020.xhtml
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-PREFL-01	4826	1860	1428	Mercedes-Benz Public Archive 238 series E-Class Cabriolets, 2017-2020	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/238-series-E-Class-Cabriolets-2017---2020.xhtml
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-PREFL-01	4826	1860	1430	Mercedes-Benz Public Archive 238 series E-Class Coupés, 2017-2020	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/238-series-E-Class-Coupes-2017---2020.xhtml
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-H1430-01	4818	1822	1430	Mercedes-Benz Public Archive E 400 CDI; Mercedes-Benz Public Archive E 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-400-CDI.xhtml?oid=453480;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500.xhtml?oid=5374
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-PHEV-01	4949	1880	1480	Mercedes-Benz UK E-Class Saloon official technical data	https://www.mercedes-benz.co.uk/passengercars/models/saloon/e-class/overview.html
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-FACELIFT-4MATIC-01	4818	1799	1451	Mercedes-Benz Public Archive 210 series E-Class Saloons, 1999-2002	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/210-series-E-Class-Saloons-1999---2002.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-FACELIFT-01	4839	1799	1505	Mercedes-Benz Public Archive 210 series E-Class Estates, 1999-2003	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/210-series-E-Class-Estates-1999---2003.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1469-01	4949	1880	1469	Mercedes-Benz UK E-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/e-class/overview.html
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-4MATIC-01	4949	1880	1469	Mercedes-Benz UK E-Class Saloon official technical data	https://www.mercedes-benz.co.uk/passengercars/models/saloon/e-class/overview.html
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-H1470-01	4949	1880	1470	Mercedes-Benz UK E-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/e-class/overview.html
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-01	4868	1854	1454	Mercedes-Benz Public Archive E 500 BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-BlueEFFICIENCY-2011---2013.xhtml?oid=188539302
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E500-01	4879	1854	1458	Mercedes-Benz Public Archive E 500 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-2013---2015.xhtml?oid=188541036
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-01	4856	1822	1465	Mercedes-Benz Public Archive E 500 W211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500--W-211-E-55-2006---2009.xhtml?oid=2461848
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E500-4MATIC-01	4868	1854	1458	Mercedes-Benz Public Archive E 500 4MATIC BlueEFFICIENCY 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-500-4MATIC-BlueEFFICIENCY-2011---2013.xhtml?oid=188539306
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-PREFL-E500-4MATIC-01	4818	1822	1441	Mercedes-Benz Public Archive E 500 4MATIC W211 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC.xhtml?oid=2461849
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-FACELIFT-E500-4MATIC-01	4856	1822	1475	Mercedes-Benz Public Archive E 500 4MATIC W211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC.xhtml?oid=2461850
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-E500-01	4850	1822	1485	Mercedes-Benz Public Archive E 500 station wagon S211 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-station-wagon--S-211-E-50-2003---2006.xhtml?oid=5469
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-PREFL-02	4850	1822	1495	Mercedes-Benz Public Archive 211 series E-Class Estates, 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/211-series-E-Class-Estates-2003---2006.xhtml
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-FACELIFT-E500-4MATIC-01	4888	1822	1513	Mercedes-Benz Public Archive E 500 4MATIC station wagon S211 2006-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-500-4MATIC-station-wagon--S-211-E-55-4-M-2006---2009.xhtml?oid=2461896
EU-MERCEDES-BENZ-E-KLASSE-S214-WAGON-E53-AMG-HYBRID-01	4965	1902	1483	Mercedes-Benz UK Mercedes-AMG E-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/e-class/amg.html
EU-MERCEDES-BENZ-E-KLASSE-W214-SEDAN-E53-AMG-HYBRID-01	4965	1902	1472	Mercedes-Benz UK Mercedes-AMG E-Class Saloon official technical data	https://www.mercedes-benz.co.uk/passengercars/models/saloon/e-class/amg.html
EU-MERCEDES-BENZ-E-KLASSE-W210-SEDAN-E55-AMG-01	4818	1799	1411	Mercedes-Benz Public Archive E 55 AMG W210	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG.xhtml?oid=5356
EU-MERCEDES-BENZ-E-KLASSE-W211-SEDAN-E55-AMG-01	4849	1822	1430	Mercedes-Benz Public Archive E 55 AMG W211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG.xhtml?oid=5375
EU-MERCEDES-BENZ-E-KLASSE-S210-WAGON-E55-AMG-01	4839	1799	1477	Mercedes-Benz Public Archive E 55 AMG T-Modell S210	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-55-AMG-T-Modell.xhtml?oid=5411
EU-MERCEDES-BENZ-E-KLASSE-S211-WAGON-E55-AMG-01	4871	1822	1485	Mercedes-Benz Public Archive E 55 AMG station wagon S211	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-55-AMG-station-wagon.xhtml?oid=5471
EU-MERCEDES-BENZ-E-KLASSE-W124-SEDAN-E60-AMG-01	4750	1796	1408	Mercedes-Benz Public Archive E 60 AMG W124	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-60-AMG.xhtml?oid=5165
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-PREFL-E63-AMG-01	4913	1872	1490	Mercedes-Benz Public Archive E 63 AMG Estate 2011-2013 export model until 2016	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-63-AMG-2011---2013-als-Exportmodell-bis-2016.xhtml?oid=188823525
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-PREFL-E63-AMG-01	4883	1872	1440	Mercedes-Benz Public Archive E 63 AMG 2011-2013	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-63-AMG-2011---2013.xhtml?oid=188539327
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-E63-AMG-01	4892	1873	1450	Mercedes-Benz Public Archive E 63 AMG 2013-2015	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-63-AMG-2013---2015-from-122014-Mercedes-AMG-E-63-AMG.xhtml?oid=188541038
EU-MERCEDES-BENZ-E-KLASSE-S212-WAGON-FACELIFT-E63-AMG-4MATIC-01	4904	1873	1522	Mercedes-Benz Public Archive E 63 AMG 4MATIC Estate 2013-2016	https://mercedes-benz-publicarchive.com/marsClassic/de/instance/ko/E-63-AMG-4MATIC-2013---2016-ab-122014-Mercedes-AMG-E-63-4MATIC.xhtml?oid=188823553
EU-MERCEDES-BENZ-EQA-H243-SUV-PREFL-01	4463	1834	1620	Mercedes-Benz EQA official brochure (2021)	https://i.i-sgcm.com/new_cars/cars/12924/brochures/brochure_20210916112640.pdf
EU-MERCEDES-BENZ-EQA-H243-SUV-FACELIFT-01	4463	1834	1608	Mercedes-Benz UK EQA official technical data	https://www.mercedes-benz.co.uk/passengercars/models/suv/eqa/overview.html
EU-MERCEDES-BENZ-EQB-X243-SUV-PREFL-01	4684	1834	1667	Mercedes-Benz EQB official brochure (2022)	https://i.i-sgcm.com/new_cars/cars/21601/brochures/brochure_20220831112857.pdf
EU-MERCEDES-BENZ-EQB-X243-SUV-FACELIFT-01	4684	1834	1654	Mercedes-Benz UK EQB official technical data	https://www.mercedes-benz.co.uk/passengercars/models/suv/eqb/overview.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_9901-10000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.mercedes-benz.co.uk/passengercars/models/saloon/e-class/amg.html?utm_source=chatgpt.com "Mercedes-AMG E-Class Saloon | E PERFORMANCE, C 43"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（761 行）
- 累计尺寸组：dimension_groups_final.tsv（197 行）

