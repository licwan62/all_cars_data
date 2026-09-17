# 任务：left18448 第 10301-10400 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0104__91d576d5


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 10301-10400 行

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
left18448 第 10301-10400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mercedes-benz	S-Klasse	S 350, S 350 L	Stufenheck	Heckantrieb	Benzin	Sep 2002	Aug 2005	16962
Mercedes-benz	S-Klasse	S 400	Stufenheck	Heckantrieb	Benzin	Mar 2014	May 2017	116218
Mercedes-benz	S-Klasse	S 400 4-matic	Stufenheck	Allrad	Benzin	Nov 2014	May 2017	108759
Mercedes-benz	S-Klasse	S 400 4-matic	Coupe	Allrad	Benzin	Oct 2015	Jul 2020	116951
Mercedes-benz	S-Klasse	S 400 CDI	Stufenheck	Heckantrieb	Diesel	Jun 2000	Aug 2005	14726
Mercedes-benz	S-Klasse	S 400 CDI	Stufenheck	Heckantrieb	Diesel	Jun 2003	Aug 2005	17555
Mercedes-benz	S-Klasse	S 400 D	Stufenheck	Heckantrieb	Diesel	Jul 2017	Jul 2020	128016
Mercedes-benz	S-Klasse	S 400 D 4-matic	Stufenheck	Allrad	Diesel	May 2017	Jul 2020	127329
Mercedes-benz	S-Klasse	S 400 D 4-matic	Stufenheck	Allrad	Diesel	Sep 2020	-	143389
Mercedes-benz	S-Klasse	S 400 Hybrid / H	Stufenheck	Heckantrieb	Benzin/Elektro	May 2013	May 2017	59009
Mercedes-benz	S-Klasse	S 400 Maybach 4-matic	Stufenheck	Allrad	Benzin	Jan 2015	May 2017	109972
Mercedes-benz	S-Klasse	S 430 4-matic	Stufenheck	Allrad	Benzin	Sep 2002	Aug 2005	16964
Mercedes-benz	S-Klasse	S 450	Stufenheck	Heckantrieb	Benzin	Feb 2017	Jul 2020	127739
Mercedes-benz	S-Klasse	S 450 4-matic	Stufenheck	Allrad	Benzin	Feb 2017	Jul 2020	127736
Mercedes-benz	S-Klasse	S 450 CDI	Stufenheck	Heckantrieb	Diesel	Jan 2009	Dec 2013	128514
Mercedes-benz	S-Klasse	S 450 D Mild Hybrid 4-matic	Stufenheck	Allrad	Diesel/Elektro	May 2023	-	154552
Mercedes-benz	S-Klasse	S 450 D Mild Hybrid 4-matic	Stufenheck	Allrad	Diesel/Elektro	May 2023	-	154553
Mercedes-benz	S-Klasse	S 450 E	Stufenheck	Heckantrieb	Benzin/Elektro	May 2022	-	147716
Mercedes-benz	S-Klasse	S 450 E	Stufenheck	Heckantrieb	Benzin/Elektro	May 2022	-	147717
Mercedes-benz	S-Klasse	S 450 E	Stufenheck	Heckantrieb	Benzin/Elektro	Mar 2026	-	803070
Mercedes-benz	S-Klasse	S 450 E	Stufenheck	Heckantrieb	Benzin/Elektro	Mar 2026	-	803071
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2017	Jul 2020	128462
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2021	-	143798
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2021	-	145181
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Jul 2017	Jul 2020	128463
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Oct 2020	-	143385
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Sep 2022	-	151475
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Sep 2022	-	151477
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	Oct 2005	Dec 2013	18961
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	May 2013	May 2017	59010
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	Jul 2013	May 2017	100330
Mercedes-benz	S-Klasse	S 500	Coupe	Heckantrieb	Benzin	Nov 2014	Oct 2017	108762
Mercedes-benz	S-Klasse	S 500	Cabriolet	Heckantrieb	Benzin	Dec 2015	Oct 2017	117885
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	Oct 1998	Dec 2003	128572
Mercedes-benz	S-Klasse	S 500 4-matic	Stufenheck	Allrad	Benzin	Sep 2002	Aug 2005	16976
Mercedes-benz	S-Klasse	S 500 4-matic	Coupe	Allrad	Benzin	Apr 2014	Oct 2017	101052
Mercedes-benz	S-Klasse	S 500 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2017	Jul 2020	128464
Mercedes-benz	S-Klasse	S 500 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Sep 2020	-	143384
Mercedes-benz	S-Klasse	S 500 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Sep 2022	-	151476
Mercedes-benz	S-Klasse	S 500 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Sep 2022	-	151479
Mercedes-benz	S-Klasse	S 500 Hybrid / E	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2014	May 2017	107475
Mercedes-benz	S-Klasse	S 500 Maybach	Stufenheck	Heckantrieb	Benzin	Dec 2014	May 2017	109486
Mercedes-benz	S-Klasse	S 500 Maybach 4-matic	Stufenheck	Allrad	Benzin	Apr 2015	May 2017	115808
Mercedes-benz	S-Klasse	S 55 AMG	Stufenheck	Heckantrieb	Benzin	Apr 1999	Aug 2005	12099
Mercedes-benz	S-Klasse	S 55 AMG Kompressor	Stufenheck	Heckantrieb	Benzin	Jun 2002	Aug 2005	16963
Mercedes-benz	S-Klasse	S 560	Stufenheck	Heckantrieb	Benzin	Jul 2017	Jul 2020	128089
Mercedes-benz	S-Klasse	S 560 4-matic	Stufenheck	Allrad	Benzin	May 2017	Jul 2020	127330
Mercedes-benz	S-Klasse	S 560 Maybach	Stufenheck	Heckantrieb	Benzin	Jul 2017	Jul 2020	128015
Mercedes-benz	S-Klasse	S 560 Maybach 4-matic	Stufenheck	Allrad	Benzin	Jul 2017	Jul 2020	127332
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	May 2021	-	144367
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	May 2021	-	144368
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	Mar 2026	-	803075
Mercedes-benz	S-Klasse	S 580 4-matic	Stufenheck	Allrad	Benzin/Elektro	Mar 2026	-	803076
Mercedes-benz	S-Klasse	S 580 E	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2021	-	144824
Mercedes-benz	S-Klasse	S 580 E	Stufenheck	Heckantrieb	Benzin/Elektro	Jul 2021	-	144826
Mercedes-benz	S-Klasse	S 580 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Nov 2021	-	147325
Mercedes-benz	S-Klasse	S 580 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Jul 2021	-	148043
Mercedes-benz	S-Klasse	S 580 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Mar 2026	-	803073
Mercedes-benz	S-Klasse	S 580 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	Mar 2026	-	803074
Mercedes-benz	S-Klasse	S 580 E Maybach 4-matic	Stufenheck	Allrad	Benzin/Elektro	Apr 2023	-	153771
Mercedes-benz	S-Klasse	S 580 Maybach EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	Aug 2021	-	145297
Mercedes-benz	S-Klasse	S 600	Stufenheck	Heckantrieb	Benzin	Feb 2014	Jul 2020	100755
Mercedes-benz	S-Klasse	S 600 Maybach	Stufenheck	Heckantrieb	Benzin	Dec 2014	Nov 2018	109488
Mercedes-benz	S-Klasse	S 600, S 600 L	Stufenheck	Heckantrieb	Benzin	Jan 2000	Aug 2005	14579
Mercedes-benz	S-Klasse	S 600, S 600 L	Stufenheck	Heckantrieb	Benzin	Sep 2002	Aug 2005	16960
Mercedes-benz	S-Klasse	S 63 AMG	Stufenheck	Heckantrieb	Benzin	May 2013	May 2017	11105
Mercedes-benz	S-Klasse	S 63 AMG	Coupe	Heckantrieb	Benzin	Jul 2014	Oct 2017	107476
Mercedes-benz	S-Klasse	S 63 AMG 4-matic	Stufenheck	Allrad	Benzin	May 2013	May 2017	11106
Mercedes-benz	S-Klasse	S 63 AMG 4-matic	Coupe	Allrad	Benzin	Apr 2014	Oct 2017	101059
Mercedes-benz	S-Klasse	S 63 AMG Hybrid 4-matic	Stufenheck	Allrad	Benzin/Elektro	May 2023	-	154538
Mercedes-benz	S-Klasse	S 65 AMG	Stufenheck	Heckantrieb	Benzin	Feb 2014	Nov 2019	100756
Mercedes-benz	S-Klasse	S 65 AMG	Coupe	Heckantrieb	Benzin	Jul 2014	May 2019	107477
Mercedes-benz	S-Klasse	S 65 Amg, S 65 AMG L	Stufenheck	Heckantrieb	Benzin	Mar 2004	Aug 2005	18030
Mercedes-benz	S-Klasse	S 650 Maybach	Stufenheck	Heckantrieb	Benzin	Jul 2017	Jul 2020	128014
Mercedes-benz	S-Klasse	S 650 Maybach	Stufenheck	Heckantrieb	Benzin	Mar 2019	Jul 2020	147532
Mercedes-benz	S-Klasse	S 680 Maybach 4-matic	Stufenheck	Allrad	Benzin	May 2021	-	144221
Mercedes-benz	S-Klasse	S 680 Maybach 4-matic	Stufenheck	Allrad	Benzin/Elektro	May 2026	-	803435
Mercedes-benz	Sl	350	Cabriolet	Heckantrieb	Benzin	Mar 2003	Jan 2012	17091
Mercedes-benz	Sl	350	Cabriolet	Heckantrieb	Benzin	Feb 2012	Apr 2014	17120
Mercedes-benz	Sl	400	Cabriolet	Heckantrieb	Benzin	Apr 2014	Mar 2016	105578
Mercedes-benz	Sl	400	Cabriolet	Heckantrieb	Benzin	Jan 2016	Apr 2020	118798
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	Oct 2001	Jan 2012	16129
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	Apr 2015	Apr 2020	112346
Mercedes-benz	Sl	600	Cabriolet	Heckantrieb	Benzin	Apr 2003	Jan 2012	17193
Mercedes-benz	Sl	350 SL	Cabriolet	Heckantrieb	Benzin	May 1971	Dec 1976	125938
Mercedes-benz	Sl	43 AMG	Cabriolet	Heckantrieb	Benzin/Elektro	May 2022	-	147679
Mercedes-benz	Sl	43 AMG	Cabriolet	Heckantrieb	Benzin/Elektro	May 2024	-	158735
Mercedes-benz	Sl	55 AMG	Cabriolet	Heckantrieb	Benzin	Mar 2000	Oct 2001	14941
Mercedes-benz	Sl	55 AMG 4-matic+	Cabriolet	Allrad	Benzin	Mar 2022	-	147274
Mercedes-benz	Sl	55 AMG Kompressor	Cabriolet	Heckantrieb	Benzin	Jun 2002	Jan 2012	16876
Mercedes-benz	Sl	560 SL	Cabriolet	Heckantrieb	Benzin	Sep 1985	Dec 1989	58478
Mercedes-benz	Sl	63 AMG	Cabriolet	Heckantrieb	Benzin	Jan 2012	May 2019	17265
Mercedes-benz	Sl	63 AMG	Cabriolet	Heckantrieb	Benzin	Apr 2014	May 2019	101064
Mercedes-benz	Sl	63 AMG 4-matic+	Cabriolet	Allrad	Benzin	Mar 2022	-	147198
Mercedes-benz	Sl	63 AMG S E Performance 4-matic+	Cabriolet	Allrad	Benzin/Elektro	Mar 2024	-	158099
Mercedes-benz	Sl	65 AMG	Cabriolet	Heckantrieb	Benzin	Mar 2004	Jan 2012	17391
Mercedes-benz	Sl	65 AMG	Cabriolet	Heckantrieb	Benzin	May 2012	Jun 2018	59082
Mercedes-benz	Sl	680 Maybach 4-matic+	Cabriolet	Allrad	Benzin	Nov 2024	-	801283
Mercedes-benz	Sl	SL 73 AMG	Cabriolet	Heckantrieb	Benzin	Jan 1999	Dec 2001	15996
Mercedes-benz	Slc	180	Cabriolet	Heckantrieb	Benzin	Jan 2016	-	118113


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 W223/V223/Z223 车型簇，共新增 30 条 READY 映射；标准轴距、长轴距、Mercedes-Maybach、AMG S 63，以及 2026 改款外廓均分别归组。
* 复用既有 W223 标准轴距组 `5179 × 1954 × 1503 mm` 和 V223 长轴距组 `5289 × 1954 × 1503 mm`。官方资料明确给出了不含后视镜宽度。
* 首次建立改款前 Z223 Maybach 与 V223 AMG S 63 组；前者为 `5469 × 1921 × 1510 mm`，后者为 `5336 × 1921 × 1515 mm`。([梅赛德斯-奔驰媒体][1])
* 2026 改款后的标准轴距、长轴距和 Maybach 分别为 `5194 × 1921 × 1503 mm`、`5304 × 1921 × 1503 mm` 和 `5484 × 1921 × 1510 mm`，均使用官方页面明确标示的不含后视镜宽度。([Mercedes-Benz][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：30
* PENDING／尚待处理输入 Ktype：70
* 已确认尺寸组：7

  * 复用历史尺寸组：2
  * 本轮首次建立尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143389	143389	Sedan	S-Class W223	223.133	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
154552	154552	Sedan	S-Class W223	223.023	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
154553	154553	Sedan	S-Class W223	223.123	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
147716	147716	Sedan	S-Class W223	223.066	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
147717	147717	Sedan	S-Class W223	223.166	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
803070	803070	Sedan	S-Class W223	223.067	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
803071	803071	Sedan	S-Class W223	223.167	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
143798	143798	Sedan	S-Class W223	223.160	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
145181	145181	Sedan	S-Class W223	223.060	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
143385	143385	Sedan	S-Class W223	223.161	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
151475	151475	Sedan	S-Class W223	223.061	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
151477	151477	Sedan	S-Class W223	223.161	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
143384	143384	Sedan	S-Class W223	223.163	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
151476	151476	Sedan	S-Class W223	223.063	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
151479	151479	Sedan	S-Class W223	223.163	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
144367	144367	Sedan	S-Class W223	223.176	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
144368	144368	Sedan	S-Class W223	223.076	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
803075	803075	Sedan	S-Class W223	223.177	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
803076	803076	Sedan	S-Class W223	223.077	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
144824	144824	Sedan	S-Class W223	223.068	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
144826	144826	Sedan	S-Class W223	223.168	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
147325	147325	Sedan	S-Class W223	223.069	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
148043	148043	Sedan	S-Class W223	223.169	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
803073	803073	Sedan	S-Class W223	223.070	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
803074	803074	Sedan	S-Class W223	223.170	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
153771	153771	Sedan	S-Class W223	223.969	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
145297	145297	Sedan	S-Class W223	223.976	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
154538	154538	Sedan	S-Class W223	223.182	4	EU-MERCEDES-BENZ-S-KLASSE-V223-AMG-S63-SEDAN-01	HIGH	V223 长轴距 AMG 专属外廓。	READY
144221	144221	Sedan	S-Class W223	223.979	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
803435	803435	Sedan	S-Class W223	223.978	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-FACELIFT-01	HIGH	2026 改款 Z223 Maybach 加长车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

以下仅包含首次建立的 5 个尺寸组；已复用的 W223 SWB 和 V223 LWB 两组不重复输出。

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	5469	1921	1510	Mercedes-Benz Media Mercedes-Maybach S 680 technical data	https://media.mercedes-benz.pl/mercedes-maybach-v12-edition--tam-gdzie-dziedzictwo-spotyka-sie-z-wyrafinowanym-wzornictwem-i-autentycznym-kunsztem/
EU-MERCEDES-BENZ-S-KLASSE-V223-AMG-S63-SEDAN-01	5336	1921	1515	Mercedes-Benz Mercedes-AMG S-Class official owner's manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-s-class-owners-manual-supplement-february-2025-1.pdf
EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	5194	1921	1503	Mercedes-Benz Germany S-Class official technical data	https://www.mercedes-benz.de/passengercars/models/saloon/s-class/overview.html
EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	5304	1921	1503	Mercedes-Benz UK S-Class Saloon Long official technical data	https://www.mercedes-benz.co.uk/passengercars/models/saloon/s-class/overview.html
EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-FACELIFT-01	5484	1921	1510	Mercedes-Benz Germany Mercedes-Maybach S-Class official technical data	https://www.mercedes-benz.de/passengercars/models/saloon-long/mercedes-maybach-s-class/overview.html
```

## 下一步优先处理

1. 闭合 W220、W221、W222 的标准轴距、长轴距、Maybach 和 AMG 分支。
2. 处理 C217 Coupe 与 A217 Cabriolet，避免将相近年份但不同车身结构误并。
3. 最后集中处理 SL 的 R107、R129、R230、R231、R232，以及 SLC R172，并优先复用已有缓存组。

推进信号：CONTINUE

[1]: https://media.mercedes-benz.pl/mercedes-maybach-v12-edition--tam-gdzie-dziedzictwo-spotyka-sie-z-wyrafinowanym-wzornictwem-i-autentycznym-kunsztem/ "Mercedes-Maybach V12 Edition – tam, gdzie dziedzictwo spotyka się z wyrafinowanym wzornictwem i autentycznym kunsztem"
[2]: https://www.mercedes-benz.de/passengercars/models/saloon/s-class/overview.html?srsltid=AfmBOoo_gzkQslH5aX_jOpm0qoUBzk8CHh-TQEi8AMN8aMYr1Ryhbbqc "S-Klasse Limousine | Preise & Spezifikationen | Mercedes-Benz"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合改款前 W222/V222 的标准轴距、长轴距及 AMG 外廓；对同时覆盖 `222.0xx` 与 `222.1xx` 的 Ktype 拆分为 `swb`、`lwb` 派生行。车型代码边界已按对应 Ktype 核对。([梅尔摩托车][1])
* W222/V222 普通车身及 AMG 车身的长宽高已在尺寸组层一次闭合；官方图示区分标准轴距、长轴距，并明确方括号尺寸属于 Mercedes-AMG，宽度不含后视镜。
* 已闭合改款前 X222 Maybach、C217 普通 Coupe、C217 S 63 AMG Coupe 和 A217 Cabriolet；发动机及驱动差异未重复建组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：47
* READY 映射行：53
* PENDING 输入 Ktype：53
* 已确认尺寸组：15
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
116218	116218	Sedan	S-Class W222	222.165	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距车身。	READY
108759_swb	108759	Sedan	S-Class W222	222.067	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
108759_lwb	108759	Sedan	S-Class W222	222.167	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
116951	116951	Coupe	S-Class C217	217.364	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
59009_swb	59009	Sedan	S-Class W222	222.057	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
59009_lwb	59009	Sedan	S-Class W222	222.157	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
109972	109972	Sedan	S-Class W222	222.967	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
59010_swb	59010	Sedan	S-Class W222	222.082	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
59010_lwb	59010	Sedan	S-Class W222	222.182	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
100330_swb	100330	Sedan	S-Class W222	222.082	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
100330_lwb	100330	Sedan	S-Class W222	222.182	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
108762	108762	Coupe	S-Class C217	217.382	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
117885	117885	Convertible	S-Class A217	217.482	2	EU-MERCEDES-BENZ-S-KLASSE-A217-CONVERTIBLE-01	HIGH	A217敞篷车身。	READY
101052	101052	Coupe	S-Class C217	217.385	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
107475	107475	Sedan	S-Class W222	222.163	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距车身。	READY
109486	109486	Sedan	S-Class W222	222.982	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
115808	115808	Sedan	S-Class W222	222.985	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
11105_swb	11105	Sedan	S-Class W222	222.077	4	EU-MERCEDES-BENZ-S-KLASSE-W222-AMG-SEDAN-SWB-01	HIGH	W222 AMG标准轴距分支。	READY
11105_lwb	11105	Sedan	S-Class W222	222.177	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	HIGH	V222 AMG长轴距分支。	READY
107476	107476	Coupe	S-Class C217	217.377	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 S 63 AMG专属外廓。	READY
11106	11106	Sedan	S-Class W222	222.178	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	HIGH	V222 AMG长轴距车身。	READY
101059	101059	Coupe	S-Class C217	217.378	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 S 63 AMG专属外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	5246	1899	1496	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	5116	1899	1496	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	5027	1899	1411	Automobile-Catalog 2015 Mercedes-Benz S 500 4MATIC Coupe specifications	https://www.automobile-catalog.com/car/2015/2064380/mercedes-benz_s_500_4matic_coupe.html
EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	5453	1899	1498	Automobile-Catalog 2015 Mercedes-Maybach S 500 specifications	https://www.automobile-catalog.com/car/2015/2094275/mercedes-maybach_s_500.html
EU-MERCEDES-BENZ-S-KLASSE-A217-CONVERTIBLE-01	5027	1899	1417	Automobile-Catalog 2016 Mercedes-Benz S 500 Cabriolet specifications	https://www.automobile-catalog.com/car/2016/2295995/mercedes-benz_s_500_cabriolet.html
EU-MERCEDES-BENZ-S-KLASSE-W222-AMG-SEDAN-SWB-01	5157	1914	1501	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	5287	1914	1501	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	5044	1913	1422	Automobile-Catalog 2014 Mercedes-Benz S 63 AMG Coupe specifications	https://www.automobile-catalog.com/car/2014/2070710/mercedes-benz_s_63_amg_coupe.html
```

## 下一步优先处理

1. 闭合跨越改款周期的 W222、X222 与 C217 Ktype，按改款前后实际外廓拆分，避免误用单一尺寸组。
2. 批量处理 W220、W221 的标准轴距、长轴距和 AMG 分支。
3. 随后闭合 SL 的 R107、R129、R230、R231、R232，以及 SLC R172。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/116218/mercedes-benz/s-klasse_w222_v222_x222_/s_400_222_165_116218?utm_source=chatgpt.com "S 400 (222.165) | S-Klasse (W222, V222, X222) | Mercedes-Benz | Manufacturers | Meyer Motoren"
[2]: https://www.automobile-catalog.com/car/2015/2094290/mercedes-maybach_s_600.html?utm_source=chatgpt.com "2015 Mercedes-Maybach S 600 Specs Review (390 kW / 530 PS / 523 hp) (since February 2015 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 W220/V220 的 11 个输入 Ktype，并按标准轴距、长轴距、改款前后及 Pullman 物理分支拆分；`220.875`、`220.878` 保留为 Pullman 分支。([Motostacja][1])
* W220 4MATIC 未并入普通车身高度组。SWB 复用既有 4MATIC 缓存组；LWB 首次建立 `5163 × 1855 × 1449 mm` 尺寸组。([Motostacja][2])
* 闭合 W221/V221 的 Ktype `128514`、`18961`，均按标准轴距／长轴距及改款前／改款后拆分。([梅尔摩托车][3])
* 本轮新增 READY 输入 Ktype 13 个、READY 映射行 33 行；复用历史尺寸组 10 个，首次建立尺寸组 1 个。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：60
* PENDING 输入 Ktype：40
* READY 映射行：86
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16962_swb	16962	Sedan	S-Class W220	220.067	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.067标准轴距车身。	READY
16962_lwb	16962	Sedan	S-Class W220	220.167	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.167长轴距车身。	READY
14726_swb_prefl	14726	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.028标准轴距改款前外廓。	READY
14726_swb_facelift	14726	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.028标准轴距改款后外廓。	READY
14726_lwb_prefl	14726	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.128长轴距改款前外廓。	READY
14726_lwb_facelift	14726	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.128长轴距改款后外廓。	READY
17555_swb	17555	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.028标准轴距改款后车身。	READY
17555_lwb	17555	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.128长轴距改款后车身。	READY
16964_swb	16964	Sedan	S-Class W220	220.083	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	220.083标准轴距4MATIC车身。	READY
16964_lwb	16964	Sedan	S-Class W220	220.183	4	EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	HIGH	220.183长轴距4MATIC车身。	READY
128514_swb_prefl	128514	Sedan	S-Class W221	221.028	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	221.028标准轴距改款前外廓。	READY
128514_swb_facelift	128514	Sedan	S-Class W221	221.028	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	221.028标准轴距改款后外廓。	READY
128514_lwb_prefl	128514	Sedan	S-Class W221	221.128	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	221.128长轴距改款前外廓。	READY
128514_lwb_facelift	128514	Sedan	S-Class W221	221.128	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	221.128长轴距改款后外廓。	READY
18961_swb_prefl	18961	Sedan	S-Class W221	221.071	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	221.071标准轴距改款前外廓。	READY
18961_swb_facelift	18961	Sedan	S-Class W221	221.071	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	221.071标准轴距改款后外廓。	READY
18961_lwb_prefl	18961	Sedan	S-Class W221	221.171	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	221.171长轴距改款前外廓。	READY
18961_lwb_facelift	18961	Sedan	S-Class W221	221.171	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	221.171长轴距改款后外廓。	READY
128572_swb_prefl	128572	Sedan	S-Class W220	220.075	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.075标准轴距改款前外廓。	READY
128572_swb_facelift	128572	Sedan	S-Class W220	220.075	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.075标准轴距改款后外廓。	READY
128572_lwb_prefl	128572	Sedan	S-Class W220	220.175	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.175长轴距改款前外廓。	READY
128572_lwb_facelift	128572	Sedan	S-Class W220	220.175	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.175长轴距改款后外廓。	READY
128572_pullman	128572	Sedan	S-Class W220	220.875	4	EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	HIGH	220.875 Pullman加长车身。	READY
16976_swb	16976	Sedan	S-Class W220	220.084	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	220.084标准轴距4MATIC车身。	READY
16976_lwb	16976	Sedan	S-Class W220	220.184	4	EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	HIGH	220.184长轴距4MATIC车身。	READY
12099_swb	12099	Sedan	S-Class W220	220.073	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.073标准轴距AMG车身。	READY
12099_lwb	12099	Sedan	S-Class W220	220.173	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.173长轴距AMG车身。	READY
16963_swb	16963	Sedan	S-Class W220	220.074	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.074标准轴距AMG改款后车身。	READY
16963_lwb	16963	Sedan	S-Class W220	220.174	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.174长轴距AMG改款后车身。	READY
14579_lwb	14579	Sedan	S-Class W220	220.178	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.178长轴距车身。	READY
14579_pullman	14579	Sedan	S-Class W220	220.878	4	EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	HIGH	220.878 Pullman加长车身。	READY
16960	16960	Sedan	S-Class W220	220.176	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.176长轴距改款后车身。	READY
18030	18030	Sedan	S-Class W220	220.179	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.179长轴距AMG改款后车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	5163	1855	1449	Mercedes-Benz Public Archive S 500 4MATIC long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-4MATIC-long-wheelbase.xhtml?oid=2461759
```

## 下一步优先处理

1. 闭合剩余 17 个 W222/V222/X222/C217 改款及 AMG、Maybach Ktype。
2. 随后批量处理 SL R107、R129、R230、R231、R232 与 SLC R172 的剩余 23 个 Ktype。
3. 达到 PENDING=0 后立即执行一次机械闭合检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://motostacja.com/oe/71-10487/?utm_source=chatgpt.com "Kody OEM 71-10487 Motoryzacja 🚗 Motostacja.pl Części, Oleje, Chemia ✅"
[2]: https://motostacja.com/oe/2283701/?utm_source=chatgpt.com "Kody OEM 2283701 Motoryzacja 🚗 Motostacja.pl Części, Oleje, Chemia ✅"
[3]: https://www.meyermotoren.de/fahrzeuge/18961/mercedes-benz/s-klasse_w221_v221_/s_500_221_071_221_171_18961?utm_source=chatgpt.com "S 500 (221.071, 221.171) | S-Klasse (W221, V221) | Mercedes-Benz | Herstellerübersicht | Meyer Motoren"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合剩余 17 个 S-Class Ktype。W222/V222 普通轿车按标准轴距与长轴距拆分；跨越 2017 年改款的 S 600、S 65 AMG、Mercedes-Maybach S 600 和 S 65 AMG Coupe 按改款前后外廓拆分。车型代码分别对应 `222.0xx`、`222.1xx`、`222.9xx` 与 `217.379`。([梅尔摩托车][1])
* 普通 W222/V222 改款组、X222 Maybach 改款组、S 65 AMG 改款前后组和 C217 AMG 改款组已在尺寸组层一次闭合。宽度均采用不含外后视镜口径。([德国汽车俱乐部][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：77
* PENDING 输入 Ktype：23
* READY 映射行：116
* 已确认尺寸组：32
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128016_swb	128016	Sedan	S-Class W222	222.034	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128016_lwb	128016	Sedan	S-Class W222	222.134	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127329_swb	127329	Sedan	S-Class W222	222.035	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127329_lwb	127329	Sedan	S-Class W222	222.135	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127739_swb	127739	Sedan	S-Class W222	222.066	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127739_lwb	127739	Sedan	S-Class W222	222.166	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127736_swb	127736	Sedan	S-Class W222	222.064	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127736_lwb	127736	Sedan	S-Class W222	222.164	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128462_swb	128462	Sedan	S-Class W222	222.058	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128462_lwb	128462	Sedan	S-Class W222	222.158	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128463_swb	128463	Sedan	S-Class W222	222.059	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128463_lwb	128463	Sedan	S-Class W222	222.159	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128464_swb	128464	Sedan	S-Class W222	222.060	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128464_lwb	128464	Sedan	S-Class W222	222.160	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128089_swb	128089	Sedan	S-Class W222	222.083	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128089_lwb	128089	Sedan	S-Class W222	222.183	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127330_swb	127330	Sedan	S-Class W222	222.086	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127330_lwb	127330	Sedan	S-Class W222	222.186	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128015	128015	Sedan	S-Class W222	222.983	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
127332	127332	Sedan	S-Class W222	222.986	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
100755_prefl	100755	Sedan	S-Class W222	222.176	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距改款前外廓。	READY
100755_facelift	100755	Sedan	S-Class W222	222.176	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后外廓。	READY
109488_prefl	109488	Sedan	S-Class W222	222.976	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach改款前外廓。	READY
109488_facelift	109488	Sedan	S-Class W222	222.976	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后外廓。	READY
100756_prefl	100756	Sedan	S-Class W222	222.179	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-PREFL-01	HIGH	V222 S 65 AMG改款前外廓。	READY
100756_facelift	100756	Sedan	S-Class W222	222.179	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-FACELIFT-01	HIGH	V222 S 65 AMG改款后外廓。	READY
107477_prefl	107477	Coupe	S-Class C217	217.379	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 AMG Coupe改款前外廓。	READY
107477_facelift	107477	Coupe	S-Class C217	217.379	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-COUPE-FACELIFT-01	HIGH	C217 AMG Coupe改款后外廓。	READY
128014	128014	Sedan	S-Class W222	222.980	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
147532	147532	Sedan	S-Class W222	222.980	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	5125	1899	1496	ADAC Mercedes-Benz S 400 d W222 facelift technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/217-222-facelift/281406/
EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	5255	1899	1494	EncyCARpedia Mercedes-Benz S 560 L V222 specifications	https://www.encycarpedia.com/mercedes/17-s-560-l-limo
EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	5462	1899	1498	CarExpert 2018 Mercedes-Maybach S-Class specifications	https://www.carexpert.co.nz/mercedes-benz/s-class/2018-maybach-6l-sedan-rwd-petrol-automatic-jokafsma20190218
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-PREFL-01	5293	1914	1501	Mercedes-Benz S 65 L AMG official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/01/Mercedes-Clase-S-65-AMG-2014-CN.pdf
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-FACELIFT-01	5305	1915	1500	Mercedes-AMG S 65 Long catalogue specifications	https://www.goo-net.com/catalog/MERCEDES_AMG/SCLASS/10114057/
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-COUPE-FACELIFT-01	5051	1913	1424	Automobile-Catalog 2018 Mercedes-AMG S 65 Coupe specifications	https://www.automobile-catalog.com/car/2018/2603045/mercedes-amg_s_65_coupe.html
```

## 下一步优先处理

1. 闭合 R107 与 R129 的 4 个历史 SL Ktype。
2. 按两次外观改款批量闭合 R230 的 7 个 Ktype。
3. 闭合 R231、R232 与 SLC R172 的剩余 12 个 Ktype；清零后立即输出最终完整两表与指定下载链接。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/128016/mercedes-benz/s-klasse_w222_v222_x222_/s_400_d_222_034_222_134_128016?utm_source=chatgpt.com "S 400 d (222.034, 222.134) | S-Klasse (W222, V222, X222) | Mercedes-Benz | Manufacturers | Meyer Motoren"
[2]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/217-222-facelift/281406/ "Mercedes-Benz S 400 d 9G-TRONIC (07/17 - 05/18): Technische Daten, Bilder, Preise | ADAC"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 已闭合 R107、R129、R231、R232 和 R172/SLC 共 18 个输入 Ktype；R107 560 SL、R129 AMG 车型分别使用独立外廓，不与同代普通车型合并。([marsClassic][1])
* R231 按改款前后及普通车身／AMG 外廓拆分。改款前普通车身采用官方资料的 `4617 × 1877 × 1315 mm`；改款后普通车身采用 `4631 × 1877 × 1315 mm`。([哈托诺汽车][2])
* R232 普通 AMG 外廓采用 `4705 × 1915 × 1359 mm`；S 63 E Performance 因高度不同独立建组；Mercedes-Maybach SL 680 使用独立 Maybach 外廓组。([奔驰媒体][3])
* 当前仅剩 5 个跨越多次外观阶段的 R230 Ktype 尚未闭合。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：95
* PENDING 输入 Ktype：5
* READY 映射行：138
* 已确认尺寸组：44
* 本轮首次创建尺寸组：12
* 剩余 PENDING：`17091`、`16129`、`17193`、`16876`、`17391`
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
125938	125938	Convertible	SL R107	107.043	2	EU-MERCEDES-BENZ-SL-R107-350-CONVERTIBLE-01	HIGH	R107 350 SL车身。	READY
147679	147679	Convertible	SL R232	232.450	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 43车身。	READY
158735	158735	Convertible	SL R232	232.450	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 43车身。	READY
14941	14941	Convertible	SL R129	129.068	2	EU-MERCEDES-BENZ-SL-R129-AMG-SL55-CONVERTIBLE-01	HIGH	R129 SL 55 AMG外廓。	READY
147274	147274	Convertible	SL R232	232.480	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 55车身。	READY
58478	58478	Convertible	SL R107	107.048	2	EU-MERCEDES-BENZ-SL-R107-560-CONVERTIBLE-01	HIGH	R107 560 SL加长保险杠外廓。	READY
17120	17120	Convertible	SL R231	231.457	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前外廓。	READY
105578	105578	Convertible	SL R231	231.465	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前外廓。	READY
118798	118798	Convertible	SL R231	231.466	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	HIGH	R231普通车身改款后外廓。	READY
112346_prefl	112346	Convertible	SL R231	231.473	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前分支。	READY
112346_facelift	112346	Convertible	SL R231	231.473	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	HIGH	R231普通车身改款后分支。	READY
17265_prefl	17265	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
17265_facelift	17265	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
101064_prefl	101064	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
101064_facelift	101064	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
147198	147198	Convertible	SL R232	232.481	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 63车身。	READY
158099	158099	Convertible	SL R232	232.482	2	EU-MERCEDES-BENZ-SL-R232-AMG-S63-E-PERFORMANCE-CONVERTIBLE-01	HIGH	R232 S 63 E Performance专属高度外廓。	READY
59082_prefl	59082	Convertible	SL R231	231.479	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
59082_facelift	59082	Convertible	SL R231	231.479	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
801283	801283	Convertible	SL R232	232.981	2	EU-MERCEDES-BENZ-SL-R232-MAYBACH-CONVERTIBLE-01	HIGH	R232 Mercedes-Maybach专属外廓。	READY
15996	15996	Convertible	SL R129	129.076	2	EU-MERCEDES-BENZ-SL-R129-AMG-SL73-CONVERTIBLE-01	HIGH	R129 SL 73 AMG外廓。	READY
118113	118113	Convertible	SLC R172	172.431	2	EU-MERCEDES-BENZ-SLC-R172-CONVERTIBLE-FACELIFT-01	HIGH	R172改款后SLC车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SL-R107-350-CONVERTIBLE-01	4390	1790	1300	Mercedes-Benz Public Archive 350 SL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-SL.xhtml?oid=4670
EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	4705	1915	1359	Mercedes-Benz USA 2022 Mercedes-AMG SL Roadster Quick Reference Guide	https://media.mbusa.com/releases/release-35650297d856e41f18a057160c026a6e-2022-mercedes-amg-sl-roadster-quick-reference-guide
EU-MERCEDES-BENZ-SL-R129-AMG-SL55-CONVERTIBLE-01	4499	1812	1300	Mercedes-Benz Public Archive SL 55 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-55-AMG.xhtml?oid=4733
EU-MERCEDES-BENZ-SL-R107-560-CONVERTIBLE-01	4580	1790	1307	Mercedes-Benz Public Archive 560 SL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/560-SL.xhtml?oid=4673
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	4617	1877	1315	Mercedes-Benz SL-Class R231 official brochure	https://www.hartonomotor.com/content/media_library/retailer/product/pc/all-class-brochures/SL-Class_R231_0613.pdf
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	4631	1877	1315	Mercedes-Benz UK SL Roadster official range guide	https://mercedes-benz-media.co.uk/assets/documents/original/7089-the_new_sl_ebrochure.pdf
EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	4633	1948	1300	Mercedes-Benz USA 2014 SL63 and SL65 AMG specifications	https://media.mbusa.com/releases/release-cd2f9a50d2bf422d8c734d4b2da18cc2-2014-sl63-sl65-amg-specifications
EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	4642	1877	1300	Mercedes-Benz USA 2017 Mercedes-AMG SL63 specifications	https://media.mbusa.com/releases/release-72244a6dc7d04f8e8f63653b15a14972-2017-mercedes-amg-sl63-specifications
EU-MERCEDES-BENZ-SL-R232-AMG-S63-E-PERFORMANCE-CONVERTIBLE-01	4705	1915	1354	Mercedes-Benz USA 2024 Mercedes-AMG SL 63 S E Performance Quick Reference Guide	https://media.mbusa.com/releases/release-1d2ba082ef32b72d00f8f4d0181074fc-2024-mercedes-amg-sl-63-s-e-performance-quick-reference-guide
EU-MERCEDES-BENZ-SL-R232-MAYBACH-CONVERTIBLE-01	4697	1915	1358	Mercedes-Benz USA Mercedes-Maybach SL 680 specifications; Mercedes-Benz Hong Kong Mercedes-Maybach SL 680 technical data	https://media.mbusa.com/releases/release-3ad2516a590aa0d3d707ab97b20146d0-the-new-mercedes-maybach-sl-680-monogram-series;https://www.mercedes-benz.com.hk/en/passengercars/models/cabriolet-roadster/mercedes-maybach-sl/overview.html
EU-MERCEDES-BENZ-SL-R129-AMG-SL73-CONVERTIBLE-01	4499	1812	1296	Mercedes-Benz Public Archive SL 73 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-73-AMG.xhtml?oid=4734
EU-MERCEDES-BENZ-SLC-R172-CONVERTIBLE-FACELIFT-01	4134	1810	1301	Mercedes-Benz UK SLK and SLC R172 official range guide	https://mercedes-benz-media.co.uk/assets/documents/original/28034-slkclassbrochure2012.pdf
```

## 5. 下一步优先处理

1. 一次性闭合 R230 普通车身的初期、2006 改款和 2008 改款尺寸组。
2. 单独处理 SL 55 AMG、SL 65 AMG 的 AMG 外廓，避免将普通车身高度或宽度错误复用。
3. 完成 `17091`、`16129`、`17193`、`16876`、`17391` 后立即执行机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/560-SL.xhtml?oid=4673&utm_source=chatgpt.com "560 SL - Mercedes Benz Archive"
[2]: https://www.hartonomotor.com/content/media_library/retailer/product/pc/all-class-brochures/SL-Class_R231_0613.pdf?utm_source=chatgpt.com "The SL-Class ."
[3]: https://media.mbusa.com/releases/release-35650297d856e41f18a057160c026a6e-2022-mercedes-amg-sl-roadster-quick-reference-guide?utm_source=chatgpt.com "2022 Mercedes-AMG SL Roadster Quick Reference Guide"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_10301-10400_ktype_dimension_mapping_final.tsv
- left18448_10301-10400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后 5 个 R230 Ktype 已闭合：`17091`、`16129`、`17193`、`16876`、`17391`。
* 已按初期、第一次改款、第二次改款的实际外廓拆分对应派生映射。
* 已完成轻量机械检查：表头正确、`id` 唯一、尺寸组唯一、100 个输入 Ktype 全部覆盖、映射引用闭合、尺寸与来源完整。
* 当前批次无 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：151
* PENDING：0
* DIMENSION_GROUP：58
* 映射引用闭合：是
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16962_swb	16962	Sedan	S-Class W220	220.067	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.067标准轴距车身。	READY
16962_lwb	16962	Sedan	S-Class W220	220.167	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.167长轴距车身。	READY
116218	116218	Sedan	S-Class W222	222.165	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距车身。	READY
108759_swb	108759	Sedan	S-Class W222	222.067	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
108759_lwb	108759	Sedan	S-Class W222	222.167	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
116951	116951	Coupe	S-Class C217	217.364	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
14726_swb_prefl	14726	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.028标准轴距改款前外廓。	READY
14726_swb_facelift	14726	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.028标准轴距改款后外廓。	READY
14726_lwb_prefl	14726	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.128长轴距改款前外廓。	READY
14726_lwb_facelift	14726	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.128长轴距改款后外廓。	READY
17555_swb	17555	Sedan	S-Class W220	220.028	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.028标准轴距改款后车身。	READY
17555_lwb	17555	Sedan	S-Class W220	220.128	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.128长轴距改款后车身。	READY
128016_swb	128016	Sedan	S-Class W222	222.034	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128016_lwb	128016	Sedan	S-Class W222	222.134	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127329_swb	127329	Sedan	S-Class W222	222.035	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127329_lwb	127329	Sedan	S-Class W222	222.135	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
143389	143389	Sedan	S-Class W223	223.133	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
59009_swb	59009	Sedan	S-Class W222	222.057	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
59009_lwb	59009	Sedan	S-Class W222	222.157	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
109972	109972	Sedan	S-Class W222	222.967	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
16964_swb	16964	Sedan	S-Class W220	220.083	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	220.083标准轴距4MATIC车身。	READY
16964_lwb	16964	Sedan	S-Class W220	220.183	4	EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	HIGH	220.183长轴距4MATIC车身。	READY
127739_swb	127739	Sedan	S-Class W222	222.066	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127739_lwb	127739	Sedan	S-Class W222	222.166	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127736_swb	127736	Sedan	S-Class W222	222.064	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127736_lwb	127736	Sedan	S-Class W222	222.164	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128514_swb_prefl	128514	Sedan	S-Class W221	221.028	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	221.028标准轴距改款前外廓。	READY
128514_swb_facelift	128514	Sedan	S-Class W221	221.028	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	221.028标准轴距改款后外廓。	READY
128514_lwb_prefl	128514	Sedan	S-Class W221	221.128	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	221.128长轴距改款前外廓。	READY
128514_lwb_facelift	128514	Sedan	S-Class W221	221.128	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	221.128长轴距改款后外廓。	READY
154552	154552	Sedan	S-Class W223	223.023	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
154553	154553	Sedan	S-Class W223	223.123	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
147716	147716	Sedan	S-Class W223	223.066	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
147717	147717	Sedan	S-Class W223	223.166	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
803070	803070	Sedan	S-Class W223	223.067	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
803071	803071	Sedan	S-Class W223	223.167	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
128462_swb	128462	Sedan	S-Class W222	222.058	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128462_lwb	128462	Sedan	S-Class W222	222.158	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
143798	143798	Sedan	S-Class W223	223.160	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
145181	145181	Sedan	S-Class W223	223.060	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
128463_swb	128463	Sedan	S-Class W222	222.059	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128463_lwb	128463	Sedan	S-Class W222	222.159	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
143385	143385	Sedan	S-Class W223	223.161	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
151475	151475	Sedan	S-Class W223	223.061	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
151477	151477	Sedan	S-Class W223	223.161	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
18961_swb_prefl	18961	Sedan	S-Class W221	221.071	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	HIGH	221.071标准轴距改款前外廓。	READY
18961_swb_facelift	18961	Sedan	S-Class W221	221.071	4	EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	HIGH	221.071标准轴距改款后外廓。	READY
18961_lwb_prefl	18961	Sedan	S-Class W221	221.171	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	HIGH	221.171长轴距改款前外廓。	READY
18961_lwb_facelift	18961	Sedan	S-Class W221	221.171	4	EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	HIGH	221.171长轴距改款后外廓。	READY
59010_swb	59010	Sedan	S-Class W222	222.082	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
59010_lwb	59010	Sedan	S-Class W222	222.182	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
100330_swb	100330	Sedan	S-Class W222	222.082	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	HIGH	W222标准轴距分支。	READY
100330_lwb	100330	Sedan	S-Class W222	222.182	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距分支。	READY
108762	108762	Coupe	S-Class C217	217.382	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
117885	117885	Convertible	S-Class A217	217.482	2	EU-MERCEDES-BENZ-S-KLASSE-A217-CONVERTIBLE-01	HIGH	A217敞篷车身。	READY
128572_swb_prefl	128572	Sedan	S-Class W220	220.075	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.075标准轴距改款前外廓。	READY
128572_swb_facelift	128572	Sedan	S-Class W220	220.075	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.075标准轴距改款后外廓。	READY
128572_lwb_prefl	128572	Sedan	S-Class W220	220.175	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.175长轴距改款前外廓。	READY
128572_lwb_facelift	128572	Sedan	S-Class W220	220.175	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.175长轴距改款后外廓。	READY
128572_pullman	128572	Sedan	S-Class W220	220.875	4	EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	HIGH	220.875 Pullman加长车身。	READY
16976_swb	16976	Sedan	S-Class W220	220.084	4	EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	HIGH	220.084标准轴距4MATIC车身。	READY
16976_lwb	16976	Sedan	S-Class W220	220.184	4	EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	HIGH	220.184长轴距4MATIC车身。	READY
101052	101052	Coupe	S-Class C217	217.385	2	EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	HIGH	C217普通双门外廓。	READY
128464_swb	128464	Sedan	S-Class W222	222.060	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128464_lwb	128464	Sedan	S-Class W222	222.160	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
143384	143384	Sedan	S-Class W223	223.163	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
151476	151476	Sedan	S-Class W223	223.063	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
151479	151479	Sedan	S-Class W223	223.163	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
107475	107475	Sedan	S-Class W222	222.163	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距车身。	READY
109486	109486	Sedan	S-Class W222	222.982	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
115808	115808	Sedan	S-Class W222	222.985	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach加长车身。	READY
12099_swb	12099	Sedan	S-Class W220	220.073	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	HIGH	220.073标准轴距AMG车身。	READY
12099_lwb	12099	Sedan	S-Class W220	220.173	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.173长轴距AMG车身。	READY
16963_swb	16963	Sedan	S-Class W220	220.074	4	EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	HIGH	220.074标准轴距AMG改款后车身。	READY
16963_lwb	16963	Sedan	S-Class W220	220.174	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.174长轴距AMG改款后车身。	READY
128089_swb	128089	Sedan	S-Class W222	222.083	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
128089_lwb	128089	Sedan	S-Class W222	222.183	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
127330_swb	127330	Sedan	S-Class W222	222.086	4	EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	HIGH	W222标准轴距改款后车身。	READY
127330_lwb	127330	Sedan	S-Class W222	222.186	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后车身。	READY
128015	128015	Sedan	S-Class W222	222.983	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
127332	127332	Sedan	S-Class W222	222.986	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
144367	144367	Sedan	S-Class W223	223.176	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
144368	144368	Sedan	S-Class W223	223.076	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
803075	803075	Sedan	S-Class W223	223.177	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
803076	803076	Sedan	S-Class W223	223.077	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
144824	144824	Sedan	S-Class W223	223.068	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
144826	144826	Sedan	S-Class W223	223.168	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
147325	147325	Sedan	S-Class W223	223.069	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	223.0xx 标准轴距车身。	READY
148043	148043	Sedan	S-Class W223	223.169	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	223.1xx 长轴距车身。	READY
803073	803073	Sedan	S-Class W223	223.070	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	HIGH	2026 改款 223.0xx 标准轴距车身。	READY
803074	803074	Sedan	S-Class W223	223.170	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	HIGH	2026 改款 223.1xx 长轴距车身。	READY
153771	153771	Sedan	S-Class W223	223.969	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
145297	145297	Sedan	S-Class W223	223.976	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
100755_prefl	100755	Sedan	S-Class W222	222.176	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	HIGH	V222长轴距改款前外廓。	READY
100755_facelift	100755	Sedan	S-Class W222	222.176	4	EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	HIGH	V222长轴距改款后外廓。	READY
109488_prefl	109488	Sedan	S-Class W222	222.976	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	HIGH	X222 Maybach改款前外廓。	READY
109488_facelift	109488	Sedan	S-Class W222	222.976	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后外廓。	READY
14579_lwb	14579	Sedan	S-Class W220	220.178	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	HIGH	220.178长轴距车身。	READY
14579_pullman	14579	Sedan	S-Class W220	220.878	4	EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	HIGH	220.878 Pullman加长车身。	READY
16960	16960	Sedan	S-Class W220	220.176	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.176长轴距改款后车身。	READY
11105_swb	11105	Sedan	S-Class W222	222.077	4	EU-MERCEDES-BENZ-S-KLASSE-W222-AMG-SEDAN-SWB-01	HIGH	W222 AMG标准轴距分支。	READY
11105_lwb	11105	Sedan	S-Class W222	222.177	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	HIGH	V222 AMG长轴距分支。	READY
107476	107476	Coupe	S-Class C217	217.377	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 S 63 AMG专属外廓。	READY
11106	11106	Sedan	S-Class W222	222.178	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	HIGH	V222 AMG长轴距车身。	READY
101059	101059	Coupe	S-Class C217	217.378	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 S 63 AMG专属外廓。	READY
154538	154538	Sedan	S-Class W223	223.182	4	EU-MERCEDES-BENZ-S-KLASSE-V223-AMG-S63-SEDAN-01	HIGH	V223 长轴距 AMG 专属外廓。	READY
100756_prefl	100756	Sedan	S-Class W222	222.179	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-PREFL-01	HIGH	V222 S 65 AMG改款前外廓。	READY
100756_facelift	100756	Sedan	S-Class W222	222.179	4	EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-FACELIFT-01	HIGH	V222 S 65 AMG改款后外廓。	READY
107477_prefl	107477	Coupe	S-Class C217	217.379	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	HIGH	C217 AMG Coupe改款前外廓。	READY
107477_facelift	107477	Coupe	S-Class C217	217.379	2	EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-COUPE-FACELIFT-01	HIGH	C217 AMG Coupe改款后外廓。	READY
18030	18030	Sedan	S-Class W220	220.179	4	EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	HIGH	220.179长轴距AMG改款后车身。	READY
128014	128014	Sedan	S-Class W222	222.980	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
147532	147532	Sedan	S-Class W222	222.980	4	EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	HIGH	X222 Maybach改款后加长车身。	READY
144221	144221	Sedan	S-Class W223	223.979	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	HIGH	Z223 Maybach 加长车身。	READY
803435	803435	Sedan	S-Class W223	223.978	4	EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-FACELIFT-01	HIGH	2026 改款 Z223 Maybach 加长车身。	READY
17091_prefl	17091	Convertible	SL R230	230.467	2	EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-PREFL-01	HIGH	R230 SL 350初期外廓。	READY
17091_facelift1	17091	Convertible	SL R230	230.456	2	EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-FACELIFT1-01	HIGH	R230 SL 350第一次改款外廓。	READY
17091_facelift2	17091	Convertible	SL R230	230.458	2	EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-FACELIFT2-01	HIGH	R230 SL 350第二次改款外廓。	READY
17120	17120	Convertible	SL R231	231.457	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前外廓。	READY
105578	105578	Convertible	SL R231	231.465	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前外廓。	READY
118798	118798	Convertible	SL R231	231.466	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	HIGH	R231普通车身改款后外廓。	READY
16129_prefl	16129	Convertible	SL R230	230.475	2	EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-PREFL-01	HIGH	R230 SL 500初期外廓。	READY
16129_facelift1	16129	Convertible	SL R230	230.471	2	EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-FACELIFT1-01	HIGH	R230 SL 500第一次改款外廓。	READY
16129_facelift2	16129	Convertible	SL R230	230.471	2	EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-FACELIFT2-01	HIGH	R230 SL 500第二次改款外廓。	READY
112346_prefl	112346	Convertible	SL R231	231.473	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	HIGH	R231普通车身改款前分支。	READY
112346_facelift	112346	Convertible	SL R231	231.473	2	EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	HIGH	R231普通车身改款后分支。	READY
17193_prefl	17193	Convertible	SL R230	230.476	2	EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-PREFL-01	HIGH	R230 SL 600初期外廓。	READY
17193_facelift1	17193	Convertible	SL R230	230.477	2	EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-FACELIFT1-01	HIGH	R230 SL 600第一次改款外廓。	READY
17193_facelift2	17193	Convertible	SL R230	230.477	2	EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-FACELIFT2-01	HIGH	R230 SL 600第二次改款外廓。	READY
125938	125938	Convertible	SL R107	107.043	2	EU-MERCEDES-BENZ-SL-R107-350-CONVERTIBLE-01	HIGH	R107 350 SL车身。	READY
147679	147679	Convertible	SL R232	232.450	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 43车身。	READY
158735	158735	Convertible	SL R232	232.450	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 43车身。	READY
14941	14941	Convertible	SL R129	129.068	2	EU-MERCEDES-BENZ-SL-R129-AMG-SL55-CONVERTIBLE-01	HIGH	R129 SL 55 AMG外廓。	READY
147274	147274	Convertible	SL R232	232.480	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 55车身。	READY
16876_prefl	16876	Convertible	SL R230	230.474	2	EU-MERCEDES-BENZ-SL-R230-SL55-AMG-CONVERTIBLE-PREFL-01	HIGH	R230 SL 55 AMG初期外廓。	READY
16876_facelift1	16876	Convertible	SL R230	230.472	2	EU-MERCEDES-BENZ-SL-R230-SL55-AMG-CONVERTIBLE-FACELIFT1-01	HIGH	R230 SL 55 AMG第一次改款外廓。	READY
58478	58478	Convertible	SL R107	107.048	2	EU-MERCEDES-BENZ-SL-R107-560-CONVERTIBLE-01	HIGH	R107 560 SL加长保险杠外廓。	READY
17265_prefl	17265	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
17265_facelift	17265	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
101064_prefl	101064	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
101064_facelift	101064	Convertible	SL R231	231.474	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
147198	147198	Convertible	SL R232	232.481	2	EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	HIGH	R232 AMG SL 63车身。	READY
158099	158099	Convertible	SL R232	232.482	2	EU-MERCEDES-BENZ-SL-R232-AMG-S63-E-PERFORMANCE-CONVERTIBLE-01	HIGH	R232 S 63 E Performance专属高度外廓。	READY
17391_prefl	17391	Convertible	SL R230	230.479	2	EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-PREFL-01	HIGH	R230 SL 65 AMG初期外廓。	READY
17391_facelift1	17391	Convertible	SL R230	230.479	2	EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-FACELIFT1-01	HIGH	R230 SL 65 AMG第一次改款外廓。	READY
17391_facelift2	17391	Convertible	SL R230	230.479	2	EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-FACELIFT2-01	HIGH	R230 SL 65 AMG第二次改款外廓。	READY
59082_prefl	59082	Convertible	SL R231	231.479	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	HIGH	R231 AMG改款前分支。	READY
59082_facelift	59082	Convertible	SL R231	231.479	2	EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	HIGH	R231 AMG改款后分支。	READY
801283	801283	Convertible	SL R232	232.981	2	EU-MERCEDES-BENZ-SL-R232-MAYBACH-CONVERTIBLE-01	HIGH	R232 Mercedes-Maybach专属外廓。	READY
15996	15996	Convertible	SL R129	129.076	2	EU-MERCEDES-BENZ-SL-R129-AMG-SL73-CONVERTIBLE-01	HIGH	R129 SL 73 AMG外廓。	READY
118113	118113	Convertible	SLC R172	172.431	2	EU-MERCEDES-BENZ-SLC-R172-CONVERTIBLE-FACELIFT-01	HIGH	R172改款后SLC车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_10301-10400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-FACELIFT-01	5043	1855	1444	Mercedes-Benz Public Archive S 350 W220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350.xhtml?oid=2461748
EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-FACELIFT-01	5163	1855	1444	Mercedes-Benz Public Archive S 350 long wheelbase V220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-350-long-wheelbase--V-220-E-37-2002---2005.xhtml?oid=2461749
EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-01	5246	1899	1496	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-01	5116	1899	1496	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-C217-COUPE-01	5027	1899	1411	Automobile-Catalog 2015 Mercedes-Benz S 500 4MATIC Coupe specifications	https://www.automobile-catalog.com/car/2015/2064380/mercedes-benz_s_500_4matic_coupe.html
EU-MERCEDES-BENZ-S-CLASS-IV-W220-SEDAN-PREFL-01	5038	1855	1444	Mercedes-Benz Public Archive S 55 AMG W220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-55-AMG.xhtml?oid=4968
EU-MERCEDES-BENZ-S-CLASS-IV-V220-SEDAN-LWB-PREFL-01	5158	1855	1444	Mercedes-Benz Public Archive S 500 long wheelbase V220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-long-wheelbase.xhtml?oid=4961
EU-MERCEDES-BENZ-S-KLASSE-W222-SEDAN-SWB-FACELIFT-01	5125	1899	1496	ADAC Mercedes-Benz S 400 d W222 facelift technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mercedes-benz/s-klasse/217-222-facelift/281406/
EU-MERCEDES-BENZ-S-KLASSE-V222-SEDAN-LWB-FACELIFT-01	5255	1899	1494	EncyCARpedia Mercedes-Benz S 560 L V222 specifications	https://www.encycarpedia.com/mercedes/17-s-560-l-limo
EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	5289	1954	1503	Mercedes-Benz S-Class W223 official brochure	https://www.mercedes-benz-mena.com/static/pdfs/s-klasse-w223-epaper-24-1-02-eng.pdf
EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-01	5453	1899	1498	Automobile-Catalog 2015 Mercedes-Maybach S 500 specifications	https://www.automobile-catalog.com/car/2015/2094275/mercedes-maybach_s_500.html
EU-MERCEDES-BENZ-S-CLASS-W220-4MATIC-SEDAN-FACELIFT-01	5043	1855	1449	Mercedes-Benz Public Archive S 500 4MATIC W220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-4MATIC.xhtml
EU-MERCEDES-BENZ-S-CLASS-V220-4MATIC-SEDAN-LWB-FACELIFT-01	5163	1855	1449	Mercedes-Benz Public Archive S 500 4MATIC long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-4MATIC-long-wheelbase.xhtml?oid=2461759
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-PREFL-01	5076	1871	1473	Mercedes-Benz Public Archive S 500 W221, 2005-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-2005---2009.xhtml
EU-MERCEDES-BENZ-S-CLASS-V-W221-SEDAN-FACELIFT-01	5096	1871	1479	Mercedes-Benz Public Archive S 500 W221, 2009-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-2009---2010-for-export-only-until-2011.xhtml
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-LWB-PREFL-01	5206	1871	1473	Mercedes-Benz Public Archive S 500 long wheelbase V221, 2005-2009	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-long-wheelbase-2005---2009.xhtml?oid=191730162
EU-MERCEDES-BENZ-S-CLASS-V-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Mercedes-Benz Public Archive S 500 long wheelbase V221, 2009-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-long-wheelbase-2009---2010-for-export-only-until-2011.xhtml?oid=191730325
EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	5179	1954	1503	Mercedes-Benz S-Class W223 official brochure	https://www.mercedes-benz-mena.com/static/pdfs/s-klasse-w223-epaper-24-1-02-eng.pdf
EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-FACELIFT-01	5194	1921	1503	Mercedes-Benz Germany S-Class official technical data	https://www.mercedes-benz.de/passengercars/models/saloon/s-class/overview.html
EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-FACELIFT-01	5304	1921	1503	Mercedes-Benz UK S-Class Saloon Long official technical data	https://www.mercedes-benz.co.uk/passengercars/models/saloon/s-class/overview.html
EU-MERCEDES-BENZ-S-KLASSE-A217-CONVERTIBLE-01	5027	1899	1417	Automobile-Catalog 2016 Mercedes-Benz S 500 Cabriolet specifications	https://www.automobile-catalog.com/car/2016/2295995/mercedes-benz_s_500_cabriolet.html
EU-MERCEDES-BENZ-S-CLASS-IV-VV220-PULLMAN-SEDAN-01	6158	1855	1462	Mercedes-Benz Public Archive S 500 Pullman VV220	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/S-500-Pullman.xhtml?oid=4970
EU-MERCEDES-BENZ-S-KLASSE-X222-MAYBACH-SEDAN-FACELIFT-01	5462	1899	1498	CarExpert 2018 Mercedes-Maybach S-Class specifications	https://www.carexpert.co.nz/mercedes-benz/s-class/2018-maybach-6l-sedan-rwd-petrol-automatic-jokafsma20190218
EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-01	5469	1921	1510	Mercedes-Benz Media Mercedes-Maybach S 680 technical data	https://media.mercedes-benz.pl/mercedes-maybach-v12-edition--tam-gdzie-dziedzictwo-spotyka-sie-z-wyrafinowanym-wzornictwem-i-autentycznym-kunsztem/
EU-MERCEDES-BENZ-S-KLASSE-W222-AMG-SEDAN-SWB-01	5157	1914	1501	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-SEDAN-LWB-01	5287	1914	1501	Mercedes-Benz UK S-Class Saloon official range guide	https://www.mercedesonlease.co.uk/wp-content/uploads/2017/04/s-class.pdf
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-01	5044	1913	1422	Automobile-Catalog 2014 Mercedes-Benz S 63 AMG Coupe specifications	https://www.automobile-catalog.com/car/2014/2070710/mercedes-benz_s_63_amg_coupe.html
EU-MERCEDES-BENZ-S-KLASSE-V223-AMG-S63-SEDAN-01	5336	1921	1515	Mercedes-Benz Mercedes-AMG S-Class official owner's manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ab/pdf/mercedes-amg-s-class-owners-manual-supplement-february-2025-1.pdf
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-PREFL-01	5293	1914	1501	Mercedes-Benz S 65 L AMG official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/01/Mercedes-Clase-S-65-AMG-2014-CN.pdf
EU-MERCEDES-BENZ-S-KLASSE-V222-AMG-S65-SEDAN-FACELIFT-01	5305	1915	1500	Mercedes-AMG S 65 Long catalogue specifications	https://www.goo-net.com/catalog/MERCEDES_AMG/SCLASS/10114057/
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-COUPE-FACELIFT-01	5051	1913	1424	Automobile-Catalog 2018 Mercedes-AMG S 65 Coupe specifications	https://www.automobile-catalog.com/car/2018/2603045/mercedes-amg_s_65_coupe.html
EU-MERCEDES-BENZ-S-KLASSE-Z223-MAYBACH-SEDAN-FACELIFT-01	5484	1921	1510	Mercedes-Benz Germany Mercedes-Maybach S-Class official technical data	https://www.mercedes-benz.de/passengercars/models/saloon-long/mercedes-maybach-s-class/overview.html
EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-PREFL-01	4535	1827	1317	Mercedes-Benz Public Archive SL 350 R230, 2002-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-350.xhtml?oid=2461793
EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-FACELIFT1-01	4532	1827	1317	Mercedes-Benz Public Archive SL 350 R230, 2006-2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-350.xhtml?oid=2461794
EU-MERCEDES-BENZ-SL-R230-SL350-CONVERTIBLE-FACELIFT2-01	4562	1820	1317	Mercedes-Benz Public Archive SL 350 R230, 2008-2011	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-350-2008---2011.xhtml?oid=188078627
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-PREFL-01	4617	1877	1315	Mercedes-Benz SL-Class R231 official brochure	https://www.hartonomotor.com/content/media_library/retailer/product/pc/all-class-brochures/SL-Class_R231_0613.pdf
EU-MERCEDES-BENZ-SL-R231-CONVERTIBLE-FACELIFT-01	4631	1877	1315	Mercedes-Benz UK SL Roadster official range guide	https://mercedes-benz-media.co.uk/assets/documents/original/7089-the_new_sl_ebrochure.pdf
EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-PREFL-01	4535	1815	1298	Mercedes-Benz Public Archive SL 500 R230, 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-500.xhtml?oid=4736
EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-FACELIFT1-01	4532	1827	1298	Mercedes-Benz Public Archive SL 500 R230, 2006-2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-500.xhtml?oid=2461795
EU-MERCEDES-BENZ-SL-R230-SL500-CONVERTIBLE-FACELIFT2-01	4562	1820	1298	Mercedes-Benz Public Archive SL 500 R230, 2008-2011	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-500-2008---2011.xhtml?oid=188078628
EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-PREFL-01	4535	1827	1298	Mercedes-Benz Public Archive SL 600 R230, 2003-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-600.xhtml?oid=2461798
EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-FACELIFT1-01	4532	1827	1298	Mercedes-Benz Public Archive SL 600 R230, 2006-2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-600.xhtml?oid=2461799
EU-MERCEDES-BENZ-SL-R230-SL600-CONVERTIBLE-FACELIFT2-01	4562	1820	1298	Mercedes-Benz Public Archive SL 600 R230, 2008-2011	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-600-2008---2011.xhtml?oid=188078629
EU-MERCEDES-BENZ-SL-R107-350-CONVERTIBLE-01	4390	1790	1300	Mercedes-Benz Public Archive 350 SL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/350-SL.xhtml?oid=4670
EU-MERCEDES-BENZ-SL-R232-AMG-CONVERTIBLE-01	4705	1915	1359	Mercedes-Benz USA 2022 Mercedes-AMG SL Roadster Quick Reference Guide	https://media.mbusa.com/releases/release-35650297d856e41f18a057160c026a6e-2022-mercedes-amg-sl-roadster-quick-reference-guide
EU-MERCEDES-BENZ-SL-R129-AMG-SL55-CONVERTIBLE-01	4499	1812	1300	Mercedes-Benz Public Archive SL 55 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-55-AMG.xhtml?oid=4733
EU-MERCEDES-BENZ-SL-R230-SL55-AMG-CONVERTIBLE-PREFL-01	4535	1815	1295	Mercedes-Benz Public Archive SL 55 AMG R230, 2001-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-55-AMG-with-performance-package.xhtml?oid=4738
EU-MERCEDES-BENZ-SL-R230-SL55-AMG-CONVERTIBLE-FACELIFT1-01	4535	1827	1295	Mercedes-Benz Public Archive SL 55 AMG R230, 2006-2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-55-AMG-with-performance-package.xhtml?oid=2461806
EU-MERCEDES-BENZ-SL-R107-560-CONVERTIBLE-01	4580	1790	1307	Mercedes-Benz Public Archive 560 SL	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/560-SL.xhtml?oid=4673
EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-PREFL-01	4633	1948	1300	Mercedes-Benz USA 2014 SL63 and SL65 AMG specifications	https://media.mbusa.com/releases/release-cd2f9a50d2bf422d8c734d4b2da18cc2-2014-sl63-sl65-amg-specifications
EU-MERCEDES-BENZ-SL-R231-AMG-CONVERTIBLE-FACELIFT-01	4642	1877	1300	Mercedes-Benz USA 2017 Mercedes-AMG SL63 specifications	https://media.mbusa.com/releases/release-72244a6dc7d04f8e8f63653b15a14972-2017-mercedes-amg-sl63-specifications
EU-MERCEDES-BENZ-SL-R232-AMG-S63-E-PERFORMANCE-CONVERTIBLE-01	4705	1915	1354	Mercedes-Benz USA 2024 Mercedes-AMG SL 63 S E Performance Quick Reference Guide	https://media.mbusa.com/releases/release-1d2ba082ef32b72d00f8f4d0181074fc-2024-mercedes-amg-sl-63-s-e-performance-quick-reference-guide
EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-PREFL-01	4535	1815	1298	Mercedes-Benz Public Archive SL 65 AMG R230, 2004-2006	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-65-AMG.xhtml?oid=2461807
EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-FACELIFT1-01	4535	1827	1298	Mercedes-Benz Public Archive SL 65 AMG R230, 2006-2008	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-65-AMG--R-230-E-60-LA-2006---2008.xhtml?oid=2461808
EU-MERCEDES-BENZ-SL-R230-SL65-AMG-CONVERTIBLE-FACELIFT2-01	4605	1820	1298	Mercedes-Benz Public Archive SL 65 AMG R230, 2008-2010	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-65-AMG-2008---2010.xhtml?oid=188078631
EU-MERCEDES-BENZ-SL-R232-MAYBACH-CONVERTIBLE-01	4697	1915	1358	Mercedes-Benz USA Mercedes-Maybach SL 680 specifications; Mercedes-Benz Hong Kong Mercedes-Maybach SL 680 technical data	https://media.mbusa.com/releases/release-3ad2516a590aa0d3d707ab97b20146d0-the-new-mercedes-maybach-sl-680-monogram-series;https://www.mercedes-benz.com.hk/en/passengercars/models/cabriolet-roadster/mercedes-maybach-sl/overview.html
EU-MERCEDES-BENZ-SL-R129-AMG-SL73-CONVERTIBLE-01	4499	1812	1296	Mercedes-Benz Public Archive SL 73 AMG	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SL-73-AMG.xhtml?oid=4734
EU-MERCEDES-BENZ-SLC-R172-CONVERTIBLE-FACELIFT-01	4134	1810	1301	Mercedes-Benz UK SLK and SLC R172 official range guide	https://mercedes-benz-media.co.uk/assets/documents/original/28034-slkclassbrochure2012.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_10301-10400_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1287 行）
- 累计尺寸组：dimension_groups_final.tsv（380 行）

