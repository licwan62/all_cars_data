# 任务：left18448 第 11401-11500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0115__a12a2e8f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11401-11500 行

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
left18448 第 11401-11500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	4695	1810	1680
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	4655	1800	1680

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Mitsubishi	Outlander iii	2	SUV	Frontantrieb	Benzin	Aug 2012	Dec 2022	56336
Mitsubishi	Outlander iii	2.0 4WD	SUV	Allrad	Benzin	Oct 2012	Dec 2022	56333
Mitsubishi	Outlander iii	2.0 4WD	SUV	Allrad	Benzin	Aug 2012	Dec 2022	56337
Mitsubishi	Outlander iii	2.0 Hybrid 4WD	SUV	Allrad	Benzin/Elektro	Jan 2014	Dec 2021	111463
Mitsubishi	Outlander iii	2.2 Di-d	SUV	Frontantrieb	Diesel	Aug 2012	Dec 2022	56338
Mitsubishi	Outlander iii	2.2 Di-d 4WD	SUV	Allrad	Diesel	Aug 2012	Dec 2022	56339
Mitsubishi	Outlander iii	2.4 4WD	SUV	Allrad	Benzin	Oct 2012	Dec 2022	126681
Mitsubishi	Outlander iii	2.4 Hybrid 4WD	SUV	Allrad	Benzin/Elektro	Sep 2019	Dec 2022	153413
Mitsubishi	Outlander iii	3.0 4WD	SUV	Allrad	Benzin	Mar 2014	Dec 2022	126682
Mitsubishi	Outlander iii	3.0 4WD	SUV	Allrad	Benzin	Oct 2012	Dec 2022	126684
Mitsubishi	Outlander iii	3.0 GT 4WD	SUV	Allrad	Benzin	Aug 2012	Dec 2022	107375
Mitsubishi	Outlander iii	Plug-in Hybrid	SUV	Allrad	Benzin/Elektro	Sep 2017	Dec 2021	146352
Mitsubishi	Outlander iii van	Di-d 4WD	Kasten/SUV	Allrad	Diesel	Apr 2013	-	142852
Mitsubishi	Outlander iii van	Hybrid 4WD	Kasten/SUV	Allrad	Benzin/Elektro	Sep 2018	-	142855
Mitsubishi	Outlander iv	2.5	SUV	Frontantrieb	Benzin	Jun 2021	-	144430
Mitsubishi	Outlander iv	2.4 Hybrid Allrad	SUV	Allrad	Benzin/Elektro	May 2022	-	147478
Mitsubishi	Outlander iv	2.4 Hybrid Allrad	SUV	Allrad	Benzin/Elektro	Sep 2022	-	153319
Mitsubishi	Outlander iv	2.4 Hybrid Allrad	SUV	Allrad	Benzin/Elektro	Jan 2025	-	801358
Mitsubishi	Outlander iv	2.5 Allrad	SUV	Allrad	Benzin	Jun 2021	-	144431
Mitsubishi	Pajero classic	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Jul 2001	-	16915
Mitsubishi	Pajero i	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Apr 1987	Dec 1991	3385
Mitsubishi	Pajero i	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Nov 1989	Nov 1990	3386
Mitsubishi	Pajero i	3.0 V6	Geländewagen geschlossen	Allrad	Benzin	Nov 1988	Nov 1990	3388
Mitsubishi	Pajero i canvas top	2.6	Geländewagen offen	Allrad	Benzin	Jan 1983	Nov 1990	3382
Mitsubishi	Pajero i canvas top	2.3 TD	Geländewagen offen	Allrad	Diesel	Dec 1982	Apr 1986	3383
Mitsubishi	Pajero i canvas top	2.5 TD	Geländewagen offen	Allrad	Diesel	May 1986	Oct 1989	3384
Mitsubishi	Pajero i canvas top	2.5 TD	Geländewagen offen	Allrad	Diesel	Nov 1989	Nov 1990	3387
Mitsubishi	Pajero ii	2.5 TD 4WD	Geländewagen geschlossen	Allrad	Diesel	Dec 1990	Oct 1999	3414
Mitsubishi	Pajero ii	2.8 D	Geländewagen geschlossen	Allrad	Diesel	Nov 1993	Oct 1999	101121
Mitsubishi	Pajero ii	3.0 V6 24V	Geländewagen geschlossen	Allrad	Benzin	Jun 1997	Oct 1999	15261
Mitsubishi	Pajero ii	3.0 V6 4WD	Geländewagen geschlossen	Allrad	Benzin	Dec 1990	Dec 1997	3415
Mitsubishi	Pajero ii	3.2 DID 4WD	Geländewagen geschlossen	Allrad	Diesel	Apr 2000	Sep 2007	52852
Mitsubishi	Pajero ii	3.5 V6 24V	Geländewagen geschlossen	Allrad	Benzin	Jul 1997	Oct 1999	11860
Mitsubishi	Pajero ii canvas top	2.5 TD 4WD	Geländewagen offen	Allrad	Diesel	Dec 1990	Apr 2000	3413
Mitsubishi	Pajero ii canvas top	3.0 V6	Geländewagen offen	Allrad	Benzin	Dec 1990	Dec 1995	3416
Mitsubishi	Pajero iii	3.5	Geländewagen geschlossen	Allrad	Benzin	Apr 2000	Jan 2007	57183
Mitsubishi	Pajero iii	2.5 TDI	Geländewagen geschlossen	Allrad	Diesel	Apr 2000	Dec 2006	59058
Mitsubishi	Pajero iii	2.5 TDI	Geländewagen geschlossen	Allrad	Diesel	Sep 2001	Dec 2006	59059
Mitsubishi	Pajero iii	3.2 Di-d	Geländewagen geschlossen	Allrad	Diesel	Apr 2000	Dec 2006	57184
Mitsubishi	Pajero iii	3.2 Di-d	Geländewagen geschlossen	Allrad	Diesel	Apr 2000	Oct 2006	57188
Mitsubishi	Pajero iii canvas top	3.2 Di-d	Geländewagen offen	Allrad	Diesel	Apr 2000	Dec 2006	14688
Mitsubishi	Pajero iii canvas top	3.2 Di-d	Geländewagen offen	Allrad	Diesel	Oct 2001	Dec 2006	16455
Mitsubishi	Pajero iii canvas top	3.5 V6 GDI	Geländewagen offen	Allrad	Benzin	Apr 2000	Dec 2006	14687
Mitsubishi	Pajero iv	3.0 4WD	SUV	Allrad	Benzin	Feb 2007	-	10492
Mitsubishi	Pajero iv	3.2 4WD	SUV	Allrad	Diesel	Oct 2016	-	128025
Mitsubishi	Pajero iv	3.2 Di-d 4WD	SUV	Allrad	Diesel	Feb 2007	-	10491
Mitsubishi	Pajero iv van	3.2 Di-d	Kasten/Geländewagen geschlossen	Allrad	Diesel	Nov 2006	-	12480
Mitsubishi	Pajero iv van	3.2 Di-d 4WD	Kasten/Geländewagen geschlossen	Allrad	Diesel	Feb 2007	-	118544
Mitsubishi	Pajero iv van	3.2 TD 4WD	Kasten/Geländewagen geschlossen	Allrad	Diesel	Jan 2010	-	12484
Mitsubishi	Pajero pinin i	1.8	Geländewagen geschlossen	Allrad	Benzin	Nov 2001	Jun 2007	16506
Mitsubishi	Pajero pinin i	1.8 GDI	Geländewagen geschlossen	Allrad	Benzin	Oct 1999	Oct 2001	13863
Mitsubishi	Pajero pinin i	2.0 GDI	Geländewagen geschlossen	Allrad	Benzin	Oct 2000	Jun 2007	15481
Mitsubishi	Pajero sport i	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Jul 2002	-	16886
Mitsubishi	Pajero sport i	2.5 TD	Geländewagen geschlossen	Allrad	Diesel	Aug 2003	-	17754
Mitsubishi	Pajero sport i	2.5 Tdic	Geländewagen geschlossen	Allrad	Diesel	Nov 1998	-	10682
Mitsubishi	Pajero sport i	3.0 V6	Geländewagen geschlossen	Allrad	Benzin	Nov 1998	Oct 2000	10681
Mitsubishi	Pajero sport i	3.0 V6	Geländewagen geschlossen	Allrad	Benzin	Jun 2000	-	18476
Mitsubishi	Pajero sport ii	3.0 4WD	Geländewagen geschlossen	Allrad	Benzin	Sep 2008	-	59042
Mitsubishi	Pajero sport iii	2.4 Di-d 4X4	Geländewagen geschlossen	Allrad	Diesel	Aug 2015	-	116340
Mitsubishi	Proudia/dignity	3.5	Stufenheck	Frontantrieb	Benzin	Oct 1999	May 2001	14710
Mitsubishi	Proudia/dignity	4.5	Stufenheck	Frontantrieb	Benzin	Oct 1999	May 2001	14711
Mitsubishi	Santamo	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	May 1999	Dec 2004	11514
Mitsubishi	Santamo	2.0 16V 4WD	Großraumlimousine	Allrad	Benzin	May 1999	Dec 2004	11515
Mitsubishi	Sapporo i	2	Coupe	Heckantrieb	Benzin	Apr 1978	Jul 1980	3359
Mitsubishi	Sapporo i	2	Coupe	Heckantrieb	Benzin	Apr 1978	Jul 1980	3360
Mitsubishi	Sapporo i	2	Coupe	Heckantrieb	Benzin	Jan 1979	Jul 1980	3361
Mitsubishi	Sapporo i	1.6 SL, GL	Coupe	Heckantrieb	Benzin	Apr 1978	Jul 1980	3358
Mitsubishi	Sapporo ii	1.6 GLX	Coupe	Heckantrieb	Benzin	Aug 1980	Sep 1984	3362
Mitsubishi	Sapporo ii	2.0 GSL	Coupe	Heckantrieb	Benzin	Aug 1980	Aug 1983	3363
Mitsubishi	Sapporo ii	2.0 GSR	Coupe	Heckantrieb	Benzin	Aug 1980	Sep 1984	3364
Mitsubishi	Sapporo ii	2.0 Turbo ECI	Coupe	Heckantrieb	Benzin	Aug 1982	Aug 1983	3365
Mitsubishi	Sapporo iii	2.4	Coupe	Frontantrieb	Benzin	Jun 1987	Aug 1990	3366
Mitsubishi	Sigma	3.0 V6	Stufenheck	Frontantrieb	Benzin	Dec 1990	Jul 1996	3417
Mitsubishi	Space runner	1.8	Großraumlimousine	Frontantrieb	Benzin	Jun 1996	Aug 1999	10924
Mitsubishi	Space runner	2	Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Aug 2002	13881
Mitsubishi	Space runner	2	Großraumlimousine	Frontantrieb	Benzin	May 2000	Aug 2002	54971
Mitsubishi	Space runner	1.8 4WD	Großraumlimousine	Allrad	Benzin	Jun 1996	Aug 1999	10925
Mitsubishi	Space runner	2.0 16V	Großraumlimousine	Frontantrieb	Benzin	Mar 1993	Dec 1997	11861
Mitsubishi	Space runner	2.4 GDI	Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Jan 2003	13880
Mitsubishi	Space runner	2.4 GDI	Großraumlimousine	Frontantrieb	Benzin	Aug 1999	Aug 2002	54972
Mitsubishi	Space star	1.3 16V	Großraumlimousine	Frontantrieb	Benzin	Jun 1998	Dec 2004	10939
Mitsubishi	Space star	1.3 16V	Großraumlimousine	Frontantrieb	Benzin	Dec 1998	Dec 2004	14442
Mitsubishi	Space star	1.3 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2000	Dec 2004	16177
Mitsubishi	Space star	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	Jan 2001	Dec 2004	16443
Mitsubishi	Space star	1.8 GDI	Großraumlimousine	Frontantrieb	Benzin	Jun 1998	Dec 2004	11379
Mitsubishi	Space star	1.8 GDI	Großraumlimousine	Frontantrieb	Benzin	Jun 1998	Dec 2004	15501
Mitsubishi	Space star	1.8 MPI	Großraumlimousine	Frontantrieb	Benzin	Oct 2002	Dec 2004	16891
Mitsubishi	Space star	1.9 Di-d	Großraumlimousine	Frontantrieb	Diesel	Feb 2001	Dec 2004	15369
Mitsubishi	Space star	1.9 Di-d	Großraumlimousine	Frontantrieb	Diesel	Oct 2002	Dec 2004	16890
Mitsubishi	Space star vi	1	Schrägheck	Frontantrieb	Benzin	May 2012	-	56018
Mitsubishi	Space star vi	1.2	Schrägheck	Frontantrieb	Benzin	Oct 2012	-	57508
Mitsubishi	Space star vi	1.2	Schrägheck	Frontantrieb	Benzin	Aug 2020	-	143733
Mitsubishi	Space star vi	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Aug 2020	-	151926
Mitsubishi	Space wagon	2	Großraumlimousine	Frontantrieb	Benzin	Oct 1998	Dec 2004	16779
Mitsubishi	Space wagon	1.8 GLX	Großraumlimousine	Frontantrieb	Benzin	Jan 1984	Dec 1988	3375
Mitsubishi	Space wagon	1.8 TD	Großraumlimousine	Frontantrieb	Diesel	Jun 1986	Apr 1991	3381
Mitsubishi	Space wagon	2.0 4WD	Großraumlimousine	Allrad	Benzin	Mar 1985	Apr 1991	3380
Mitsubishi	Space wagon	2.0 GLX	Großraumlimousine	Frontantrieb	Benzin	Jun 1986	May 1988	3376
Mitsubishi	Space wagon	2.0 GLX 4WD	Großraumlimousine	Allrad	Benzin	Jun 1986	May 1988	3377
Mitsubishi	Space wagon	2.0 Glxi	Großraumlimousine	Frontantrieb	Benzin	Jun 1988	Apr 1991	3378


--- Round 1 / 首次发送 ---
## 更新点

* 完成 Outlander III 车型簇处理，共覆盖 **14 个输入 Ktype、25 条派生映射**。
* 对生产区间跨越 2015 年外观改款的 Ktype，拆分为 `prefl` 与 `facelift` 两个稳定物理分支。
* 全部直接复用已有尺寸组：

  * `EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01`
  * `EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01`
* 已确认常规车型采用 GF 系列车身，2.0 PHEV 为 GG2W；Outlander III Van 的柴油车型为 GF6W，2.4 Hybrid Van 为 GG3W。无唯一明确车身代码的 Ktype 保持 `BodyCode` 为空，不写组合代码。([AUTODOC][1])
* 改款前 Outlander III 官方三维为 4655×1800×1680 mm；本轮不重复输出已缓存的尺寸组。([三菱汽车][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：14
* READY 映射行：25
* PENDING Ktype：86
* 已确认尺寸组：2，均复用跨批次缓存
* 本批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56336_prefl	56336	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56336_facelift	56336	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
56333_prefl	56333	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
56333_facelift	56333	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
56337_prefl	56337	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56337_facelift	56337	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
111463_prefl	111463	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前PHEV外廓。	READY
111463_facelift	111463	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后PHEV外廓。	READY
56338_prefl	56338	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56338_facelift	56338	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
56339_prefl	56339	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56339_facelift	56339	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
126681_prefl	126681	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126681_facelift	126681	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
153413	153413	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	2019年后2.4 Hybrid，仅改款后外廓。	READY
126682_prefl	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126682_facelift	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
126684_prefl	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126684_facelift	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
107375_prefl	107375	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前GT外廓。	READY
107375_facelift	107375	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后GT外廓。	READY
146352	146352	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	2017年后Plug-in Hybrid，仅改款后外廓。	READY
142852_prefl	142852	Van	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	商用Van与同代SUV共用外廓；改款前分支。	READY
142852_facelift	142852	Van	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	商用Van与同代SUV共用外廓；改款后分支。	READY
142855	142855	Van	Outlander III	GG3W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	商用Hybrid Van与改款后SUV共用外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Outlander IV 的普通汽油、PHEV及2025年改款尺寸边界。
2. 按 SWB/LWB、封闭式/Canvas Top 聚类处理 Pajero I、II、III、IV。
3. 优先确认各 Pajero Ktype对应的门数和单一车身代码，避免把短轴与长轴错误合并。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/battery-10142/mitsubishi/outlander/outlander-iii-gg-w-gf-w-zj/56333-2-0-4wd-gf7w-gf2w?utm_source=chatgpt.com "Mitsubishi Outlander 3 2.0 4WD Battery (146 hp Petrol 4B11)"
[2]: https://www.mitsubishi-motors.com/en/brand/motorsports/ev_phev/axcr/2014/?utm_source=chatgpt.com "2014 Asia Cross Country Rally | Electric Vehicle Motor Sports"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Outlander IV 的 5 个 Ktype，共新增 10 条派生映射。官方救援资料确认汽油版车身代码为 `GM4W`，PHEV 为 `GN0W`。
* 2021–2024 年车型按官方规格中的 `1740 mm` 与 `1745 mm` 两种车高拆分为 `lowroof`、`highroof` 两个物理外廓。([三菱汽车][1])
* 2025 年欧洲改款车型按德国官方资料中的 `1746 mm` 与 `1750 mm` 两种车高拆分；未改写既有尺寸组。([三菱汽车新闻][2])
* 本轮首次创建 4 个 Outlander IV 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：19
* READY 映射行：35
* PENDING Ktype：81
* 已确认尺寸组：6

  * 复用既有组：2
  * 本轮新建组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144430_lowroof	144430	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GM4W低车顶物理外廓。	READY
144430_highroof	144430	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GM4W高车顶物理外廓。	READY
147478_lowroof	147478	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GN0W低车顶物理外廓。	READY
147478_highroof	147478	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GN0W高车顶物理外廓。	READY
153319_lowroof	153319	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GN0W低车顶物理外廓。	READY
153319_highroof	153319	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GN0W高车顶物理外廓。	READY
801358_lowroof	801358	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-LOWROOF-01	HIGH	2025年欧洲改款低车顶物理外廓。	READY
801358_highroof	801358	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-HIGHROOF-01	HIGH	2025年欧洲改款高车顶物理外廓。	READY
144431_lowroof	144431	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GM4W低车顶物理外廓。	READY
144431_highroof	144431	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GM4W高车顶物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	4710	1862	1740	Mitsubishi Motors Australia 23MY Outlander brochure	https://www.mitsubishi-motors.com.au/content/dam/mmal/pdfs/vehicle-brochures/23MY%20Outlander%20Brochure.pdf
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	4710	1862	1745	Mitsubishi Motors Australia 23MY Outlander brochure	https://www.mitsubishi-motors.com.au/content/dam/mmal/pdfs/vehicle-brochures/23MY%20Outlander%20Brochure.pdf
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-LOWROOF-01	4719	1862	1746	Mitsubishi Motors Deutschland Outlander press information	https://presse.mitsubishi-motors.de/pm/hochwertig-und-innovativ-neuer-mitsubishi-outlander-kommt-nach-deutschland
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-HIGHROOF-01	4719	1862	1750	Mitsubishi Motors Deutschland Outlander press information	https://presse.mitsubishi-motors.de/pm/hochwertig-und-innovativ-neuer-mitsubishi-outlander-kommt-nach-deutschland
```

## 下一步优先处理

1. 闭合 Pajero I 的 `L04G/L14G`、短轴/长轴及封闭式车顶边界。
2. 处理 Pajero I Canvas Top，并与封闭式短轴车身分组。
3. 随后集中处理 Pajero II、Pajero Classic 的短轴、长轴和 Canvas Top 分支。

推进信号：CONTINUE

[1]: https://www.mitsubishi-motors.com.au/content/dam/mmal/pdfs/vehicle-brochures/23MY%20Outlander%20Brochure.pdf?utm_source=chatgpt.com "LIVE OUTLANDISH"
[2]: https://presse.mitsubishi-motors.de/pm/hochwertig-und-innovativ-neuer-mitsubishi-outlander-kommt-nach-deutschland?utm_source=chatgpt.com "NEUER MITSUBISHI OUTLANDER KOMMT NACH ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Pajero I 封闭式与 Canvas Top 车型簇，共处理 **7 个 Ktype、新增10条 READY 映射**。
* 封闭式 Ktype `3385`、`3386`、`3388` 均覆盖三门短轴和五门长轴外廓，已按单一车身代码拆分；Mitsubishi维修资料也将 `L141G` 两门车身与 `L146G` 四门车身分别列示。
* Canvas Top 的4个 Ktype 均确认属于三门开放式短轴外廓，复用同一新建尺寸组。([AutoData][1])
* 本轮首次创建3个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：26
* READY 映射行：45
* PENDING Ktype：74
* 已确认尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3385_3dr	3385	SUV	Pajero I	L044G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L044G三门短轴封闭式外廓。	READY
3385_5dr	3385	SUV	Pajero I	L049G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L049G五门长轴封闭式外廓。	READY
3386_3dr	3386	SUV	Pajero I	L044G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L044G三门短轴封闭式外廓。	READY
3386_5dr	3386	SUV	Pajero I	L049G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L049G五门长轴封闭式外廓。	READY
3388_3dr	3388	SUV	Pajero I	L141G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L141G三门短轴封闭式外廓。	READY
3388_5dr	3388	SUV	Pajero I	L146G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L146G五门长轴封闭式外廓。	READY
3382	3382	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3383	3383	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3384	3384	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3387	3387	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-I-SUV-3D-01	3995	1680	1850	CarSpecsGuru Mitsubishi Pajero I 3-door specifications	https://www.carspecsguru.com/mitsubishi/pajero/4337/6534/modification-46077
EU-MITSUBISHI-PAJERO-I-SUV-5D-01	4650	1680	1890	AutoData24 Mitsubishi Pajero I 5-door specifications	https://autodata24.com/mitsubishi/pajero/pajero-i-l04_gl14_g/25-td-l044gl049g-87-hp/details
EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	3995	1679	1849	AutoData24 Mitsubishi Pajero I Canvas Top specifications	https://autodata24.com/mitsubishi/pajero/pajero-i-canvas-top-l04_g/25-td-l044gl049g-95-hp/details
```

## 下一步优先处理

1. 集中闭合 Pajero II 封闭式三门短轴、五门长轴与 Canvas Top 分支。
2. 同步处理与 Pajero II 共用平台边界的 Pajero Classic。
3. 随后处理 Pajero III 封闭式和 Canvas Top，优先消除可能跨短轴、长轴的 Ktype。

推进信号：CONTINUE

[1]: https://autodata24.com/mitsubishi/pajero/pajero-i-canvas-top-l04_g/25-td-l044gl049g-95-hp/details?utm_source=chatgpt.com "2.5 TD (L044G,L049G) (95 Hp) technical specifications and ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Sapporo I 的4个 Ktype：1.6 对应 `A121`，2.0 对应 `A123`，均关联双门 Coupe 同一物理外廓。([汽车目录][1])
* 闭合 Sapporo II 的4个 Ktype：`A161A`、`A164A` 与 `A164` 的发动机差异不改变外廓，统一关联同一尺寸组。([汽车数据网][2])
* 闭合 Sigma 3.0 V6 Ktype `3417`，确认 `F16A` 四门 Sedan 外廓。([汽车数据网][3])
* Sapporo III `3366` 的现有资料存在三维冲突，本轮未创建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：35
* READY 映射行：54
* PENDING Ktype：65
* 已确认尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3359	3359	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3360	3360	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3361	3361	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3358	3358	Coupe	Sapporo I	A121	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A121双门Coupe外廓。	READY
3362	3362	Coupe	Sapporo II	A161A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A161A双门Coupe外廓。	READY
3363	3363	Coupe	Sapporo II	A164A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164A双门Coupe外廓。	READY
3364	3364	Coupe	Sapporo II	A164A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164A双门Coupe外廓。	READY
3365	3365	Coupe	Sapporo II	A164	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164双门Coupe外廓。	READY
3417	3417	Sedan	Sigma I	F16A	4	EU-MITSUBISHI-SIGMA-I-SEDAN-4D-01	HIGH	F16A四门Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	4430	1675	1345	Automobile-Catalog 1978 Mitsubishi Sapporo 2000 GSL	https://www.automobile-catalog.com/car/1978/36065/mitsubishi_sapporo_2000_gsl.html
EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	4525	1675	1350	Automobile-Catalog 1984 Mitsubishi Sapporo 2000 GLS	https://www.automobile-catalog.com/car/1984/1909310/mitsubishi_sapporo_2000_gls_automatic.html
EU-MITSUBISHI-SIGMA-I-SEDAN-4D-01	4750	1775	1435	Auto-Data Mitsubishi Sigma F16A 3.0 V6	https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-177hp-15430
```

## 下一步优先处理

1. 闭合 Pajero II 与 Pajero Classic 的短轴、长轴、宽体和 Canvas Top 边界。
2. 集中处理 Pajero III、Pajero IV 及对应 Van/Canvas Top。
3. 重新核对 Sapporo III 的同市场同配置三维冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1978/36065/mitsubishi_sapporo_2000_gsl.html?utm_source=chatgpt.com "1978 Mitsubishi Sapporo 2000 GSL automatic (aut. 3)"
[2]: https://www.auto-data.net/en/mitsubishi-sapporo-ii-a16-a-generation-3483?utm_source=chatgpt.com "Mitsubishi Sapporo II (A16_A) | Technical Specs, Fuel ..."
[3]: https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-177hp-15430?utm_source=chatgpt.com "Mitsubishi Sigma (F16A) 3.0 V6 (177 Hp) /Sedan 1990"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Space Runner II 的 4 个 Ktype。工厂维修手册确认 `N63W` 为 2.0、`N64W` 为 2.4 GDI，车身形式为三门，三维为 4290×1695×1650 mm；带车顶行李架时高度为 1680 mm。([手册库][1])
* 闭合 2000 年后边界明确的 5 个 Space Star I Ktype。按 2003 年外观改款及有无车顶行李架拆分为四个尺寸组。工厂手册确认改款前长度 4030 mm、改款后长度 4050 mm，宽度均为 1715 mm，高度为 1515/1555 mm。([手册库][2])
* 1998 年开始的早期 Space Star Ktype 暂未处理：早期工厂资料存在 1695/1700 mm 与后期资料 1715 mm 的宽度边界差异，需单独闭合。([手册库][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：44
* READY 映射行：78
* PENDING Ktype：56
* 已确认尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
13881_lowroof	13881	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N63W三门低车顶外廓。	READY
13881_highroof	13881	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N63W三门带车顶行李架外廓。	READY
54971_lowroof	54971	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N63W三门低车顶外廓。	READY
54971_highroof	54971	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N63W三门带车顶行李架外廓。	READY
13880_lowroof	13880	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N64W三门低车顶外廓。	READY
13880_highroof	13880	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N64W三门带车顶行李架外廓。	READY
54972_lowroof	54972	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N64W三门低车顶外廓。	READY
54972_highroof	54972	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N64W三门带车顶行李架外廓。	READY
16177_prefl_lowroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
16177_prefl_highroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
16177_facelift_lowroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16177_facelift_highroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
16443_prefl_lowroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
16443_prefl_highroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
16443_facelift_lowroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16443_facelift_highroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
16891_lowroof	16891	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16891_highroof	16891	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
15369_prefl_lowroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
15369_prefl_highroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
15369_facelift_lowroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
15369_facelift_highroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
16890_lowroof	16890	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16890_highroof	16890	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	4290	1695	1650	Mitsubishi Motors Space Runner 1999 factory workshop manual	https://www.manualslib.com/manual/1556151/Mitsubishi-Motors-Space-Runner-1999.html
EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	4290	1695	1680	Mitsubishi Motors Space Runner 1999 factory workshop manual	https://www.manualslib.com/manual/1556151/Mitsubishi-Motors-Space-Runner-1999.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	4030	1715	1515	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	4030	1715	1555	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	4050	1715	1515	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	4050	1715	1555	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
```

## 下一步优先处理

1. 闭合剩余4个早期 Space Star Ktype 的 1695/1700/1715 mm 宽度边界。
2. 处理 Space Runner I 的前后改款、两驱/四驱及行李架高度分支。
3. 随后处理 Pajero III、Pajero IV 及 Van/Canvas Top 车型簇。

推进信号：CONTINUE

[1]: https://www.manualslib.com/manual/1556151/Mitsubishi-Motors-Space-Runner-1999.html "MITSUBISHI MOTORS SPACE RUNNER 1999 AUTOMOBILE WORKSHOP MANUAL SUPPLEMENT | ManualsLib"
[2]: https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html "MITSUBISHI SPACE STAR MANUAL Pdf Download | ManualsLib"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合剩余 4 个早期 Space Star I Ktype，共新增 **32 条 READY 派生映射**。
* Mitsubishi 工厂维修资料确认早期车身存在四种外廓组合：无侧防护饰条时宽度为 1695 mm、带侧防护饰条时为 1700 mm；普通车顶高度为 1515 mm、带车顶行李架时为 1555 mm。([手册库][1])
* 本轮首次创建 4 个早期尺寸组；2000 年后 1715 mm 宽体与 2003 年改款尺寸均直接复用前轮已建立的 4 个尺寸组，不重复输出。工厂资料同时确认 Space Star 为五门车身，1.3 对应 `DG1A`、1.8 GDI 对应 `DG5A`。([手册库][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：48
* READY 映射行：110
* PENDING Ktype：52
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10939_early_nomoulding_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
10939_early_nomoulding_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
10939_early_sidemoulding_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
10939_early_sidemoulding_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
10939_prefl_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
10939_prefl_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
10939_facelift_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
10939_facelift_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
14442_early_nomoulding_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
14442_early_nomoulding_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
14442_early_sidemoulding_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
14442_early_sidemoulding_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
14442_prefl_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
14442_prefl_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
14442_facelift_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
14442_facelift_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
11379_early_nomoulding_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
11379_early_nomoulding_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
11379_early_sidemoulding_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
11379_early_sidemoulding_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
11379_prefl_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
11379_prefl_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
11379_facelift_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
11379_facelift_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
15501_early_nomoulding_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
15501_early_nomoulding_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
15501_early_sidemoulding_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
15501_early_sidemoulding_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
15501_prefl_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
15501_prefl_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
15501_facelift_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
15501_facelift_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	4030	1695	1515	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	4030	1695	1555	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	4030	1700	1515	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	4030	1700	1555	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
```

## 下一步优先处理

1. 闭合 Space Runner I 的 `N11W`、`N13W`、`N21W` 两驱/四驱与改款边界。
2. 处理 Space Star VI 的 2012 初期、2020 改款与可能的车高分支。
3. 随后集中处理 Pajero III、Pajero IV 和对应 Van/Canvas Top 车型簇。

推进信号：CONTINUE

[1]: https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18 "Major Specifications - Mitsubishi Space Star Manual [Page 18] | ManualsLib"
[2]: https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html "MITSUBISHI SPACE STAR MANUAL Pdf Download | ManualsLib"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Space Runner I 的 3 个 Ktype，确认 `N11W`、`N21W`、`N13W` 均为四门 MPV；`N11W` 使用 1640 mm 车高，`N21W` 与 `N13W` 使用 1665 mm 车高，共首次创建 2 个尺寸组。([www.valeoservice.com][1])
* 闭合 Space Star VI 的 4 个 Ktype，按 2012 初期、2015 首次改款和 2019 二次改款拆分为 3 个稳定外廓；2020 年开始的 Ktype 直接关联二次改款组。([汽车数据网][2])
* 本轮新增 11 条 READY 映射，首次创建 5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：55
* READY 映射行：121
* PENDING Ktype：45
* 已确认尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10924	10924	MPV	Space Runner I	N11W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-01	HIGH	N11W四门标准高度外廓。	READY
10925	10925	MPV	Space Runner I	N21W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	HIGH	N21W四门较高外廓。	READY
11861	11861	MPV	Space Runner I	N13W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	HIGH	N13W四门较高外廓。	READY
56018_prefl	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	HIGH	2012初期五门外廓。	READY
56018_facelift_2015	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	HIGH	2015首次改款五门外廓。	READY
56018_facelift_2019	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2019二次改款五门外廓。	READY
57508_prefl	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	HIGH	2012初期五门外廓。	READY
57508_facelift_2015	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	HIGH	2015首次改款五门外廓。	READY
57508_facelift_2019	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2019二次改款五门外廓。	READY
143733	143733	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2020年后五门外廓。	READY
151926	151926	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2020年后LPG五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-01	4270	1695	1640	Automobile-Catalog 1997 Mitsubishi Space Runner Colours	https://www.automobile-catalog.com/car/1997/1971500/mitsubishi_space_runner_colours_automatic.html
EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	4270	1695	1665	Automobile-Catalog 1997 Mitsubishi Space Runner 4x4 Cool; Auto-Data Mitsubishi Space Runner 2.0 16V	https://www.automobile-catalog.com/car/1997/1971545/mitsubishi_space_runner_4x4_cool.html; https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-2.0-16v-133hp-15540
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	3710	1665	1490	Auto-Data Mitsubishi Space Star 1.2 2012	https://www.auto-data.net/en/mitsubishi-space-star-2012-1.2-80hp-19774
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	3795	1665	1505	Mitsubishi Motors Space Star 2016 Ireland brochure	https://autocatalogarchive.com/wp-content/uploads/2018/06/Mitsubishi-Space-Star-2016-IE.pdf
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	3845	1665	1505	Mitsubishi Motors Space Star 2020 Czech brochure	https://autocatalogarchive.com/wp-content/uploads/2021/09/Mitsubishi-Space-Star-2020-CZ.pdf
```

## 下一步优先处理

1. 闭合 Pajero III 封闭式三门短轴、五门长轴及 Canvas Top 分支。
2. 处理 Pajero IV、Pajero IV Van 的三门与五门外廓。
3. 随后处理 Pajero Pinin、Pajero Sport I–III。

推进信号：CONTINUE

[1]: https://www.valeoservice.com/en-com/techassist/vehicle/P-10924?country=MA&utm_source=chatgpt.com "Parts MITSUBISHI SPACE RUNNER MPV (N1_W, N2_W)"
[2]: https://www.auto-data.net/en/mitsubishi-space-star-2012-1.2-80hp-19774?utm_source=chatgpt.com "Mitsubishi Space Star (2012) 1.2 (80 Hp) /MPV 2013 - 2015"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Proudia/Dignity 车型簇。Ktype `14710` 对应 `S32A` Proudia；Ktype `14711` 同时覆盖标准轴距 `S33A` Proudia 与加长轴距 `S43A` Dignity，已拆成两个物理分支。Mitsubishi 官方历史资料确认 Proudia 为 5050×1870×1475 mm，Dignity 车身加长至 5335 mm。([滚动商店][1])
* 闭合 Santamo 两驱与四驱 Ktype，二者均为 `UG` 四门 MPV，复用同一外廓尺寸组 4515×1695×1620 mm。([Spiegler][2])
* 闭合 Sapporo III Ktype `3366`，确认 `E16A` 四门硬顶 Coupe 外廓，采用欧洲版直接规格 4660×1690×1370 mm。([汽车目录][3])
* 本轮新增 6 条 READY 映射、4 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：60
* READY 映射行：127
* PENDING Ktype：40
* 已确认尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14710	14710	Sedan	Proudia I	S32A	4	EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	HIGH	S32A标准轴距四门Sedan外廓。	READY
14711_proudia	14711	Sedan	Proudia I	S33A	4	EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	HIGH	S33A标准轴距四门Sedan外廓。	READY
14711_dignity	14711	Sedan	Dignity I	S43A	4	EU-MITSUBISHI-DIGNITY-I-SEDAN-4D-LWB-01	HIGH	S43A加长轴距四门豪华Sedan外廓。	READY
11514	11514	MPV	Santamo I	UG	4	EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	HIGH	UG前驱四门MPV外廓。	READY
11515	11515	MPV	Santamo I	UG	4	EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	HIGH	UG四驱四门MPV外廓。	READY
3366	3366	Coupe	Sapporo III	E16A	4	EU-MITSUBISHI-SAPPORO-III-COUPE-4D-01	HIGH	E16A四门硬顶Coupe外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	5050	1870	1475	Mitsubishi Motors Car History	https://www.mitsubishi-motors.com/en/company/history/car/
EU-MITSUBISHI-DIGNITY-I-SEDAN-4D-LWB-01	5335	1870	1485	Mitsubishi Motors Car History; Goo-net Mitsubishi Dignity catalog	https://www.mitsubishi-motors.com/en/company/history/car/; https://www.goo-net.com/catalog/MITSUBISHI/DIGNITY/4007160/
EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	4515	1695	1620	Auto-Data Mitsubishi Santamo 2.0 i 16V; Auto-Data Mitsubishi Santamo 2.0 i 16V AWD	https://www.auto-data.net/en/mitsubishi-santamo-2.0-i-16v-139hp-15790; https://www.auto-data.net/en/mitsubishi-santamo-2.0-i-16v-awd-139hp-15791
EU-MITSUBISHI-SAPPORO-III-COUPE-4D-01	4660	1690	1370	Automobile-Catalog 1987 Mitsubishi Sapporo automatic catalyst	https://www.automobile-catalog.com/car/1987/59900/mitsubishi_sapporo_automatic_cat.html
```

## 下一步优先处理

1. 闭合 Pajero III 三门短轴、五门长轴及 Canvas Top 分支。
2. 处理 Pajero IV 与 Pajero IV Van 的三门、五门外廓。
3. 集中处理 Pajero Pinin、Pajero Sport I–III。
4. 最后闭合 Space Wagon 各代剩余 Ktype。

推进信号：CONTINUE

[1]: https://shop.rolling.hu/index.php/catalog/SCHAEFFLER/mitsubishi-proudiadignity-s4-a-s3-a-35-s32a?utm_source=chatgpt.com "MITSUBISHI PROUDIA/DIGNITY (S4_A, S3_A) 3.5 (S32A) Part list - Rolling Kft. webshop"
[2]: https://spiegler.de/en/product/mitsubishi-santamo-2-0-16v-102-kw-139-ps-1999-2004/?utm_source=chatgpt.com "Stahlflex-Bremsleitung für Mitsubishi Santamo | 2.0 16V | 1999-2004 - Spiegler.de"
[3]: https://www.automobile-catalog.com/car/1987/59900/mitsubishi_sapporo_automatic_cat.html?utm_source=chatgpt.com "1987 Mitsubishi Sapporo automatic catalyst Specs Review (91 kW / 124 PS / 122 hp) (since September 1987 for Europe )"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 Space Wagon I 的 6 个 Ktype。前驱 `D05V/D09W/D04W` 共用 4295×1640×1525 mm 外廓；四驱 `D08W` 的早期外廓为 4445×1640×1580 mm，1988 年后高度变为 1575 mm，因此跨期 Ktype `3380` 拆分为 `prefl/facelift`。([汽车目录][1])
* 闭合 Space Wagon III Ktype `16779`，确认 `N83W` 五门 MPV。现有规格分别对应无车顶行李架 1650 mm 和带行李架 1690 mm 两种高度，拆分为 `lowroof/highroof` 两个物理分支。([www.valeoservice.com][2])
* 本轮新增 9 条 READY 映射、首次创建 5 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：67
* READY 映射行：136
* PENDING Ktype：33
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16779_lowroof	16779	MPV	Space Wagon III	N83W	5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	五门无车顶行李架外廓。	READY
16779_highroof	16779	MPV	Space Wagon III	N83W	5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	五门带车顶行李架外廓。	READY
3375	3375	MPV	Space Wagon I	D05V	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D05V五门前驱外廓。	READY
3381	3381	MPV	Space Wagon I	D09W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D09W五门前驱外廓。	READY
3380_prefl	3380	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	HIGH	D08W早期五门四驱外廓。	READY
3380_facelift	3380	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	HIGH	D08W后期五门四驱外廓。	READY
3376	3376	MPV	Space Wagon I	D04W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D04W五门前驱外廓。	READY
3377	3377	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	HIGH	D08W早期五门四驱外廓。	READY
3378	3378	MPV	Space Wagon I	D04W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D04W五门前驱外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	4600	1775	1650	Carfolio 2002 Mitsubishi Space Wagon 2000 GLX	https://www.carfolio.com/mitsubishi-space-wagon-2000-glx-97625
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	4600	1775	1690	Auto-Data Mitsubishi Space Wagon III 2.0 i 16V	https://www.auto-data.net/en/mitsubishi-space-wagon-iii-2.0-i-16v-133hp-15589
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	4295	1640	1525	Automobile-Catalog 1991 Space Wagon 1800 TD GLX; Automobile-Catalog 1989 Space Wagon 2000 GLXi	https://www.automobile-catalog.com/car/1991/1928780/mitsubishi_space_wagon_1800_td_glx.html; https://www.automobile-catalog.com/car/1989/1928735/mitsubishi_space_wagon_2000_glxi_cat.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	4445	1640	1580	Automobile-Catalog 1988 Space Wagon 2000 GLX 4WD	https://www.automobile-catalog.com/car/1988/51665/mitsubishi_space_wagon_2_0_4wd.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	4445	1640	1575	Automobile-Catalog 1990 Space Wagon 2000 GLXi 4WD	https://www.automobile-catalog.com/car/1990/1928825/mitsubishi_space_wagon_2000_glxi_4wd.html
```

## 下一步优先处理

1. 闭合 Pajero Pinin 的三门短轴、五门长轴与车顶行李架高度分支。
2. 集中处理 Pajero Sport I、II、III 的代际和改款外廓。
3. 随后处理 Pajero III、IV 及对应 Van/Canvas Top 剩余 Ktype。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1991/1928780/mitsubishi_space_wagon_1800_td_glx.html?utm_source=chatgpt.com "1991 Mitsubishi Space Wagon 1800 TD GLX Specs Review (55 kW / 75 PS / 74 hp) (up to mid-year 1991 for Europe )"
[2]: https://www.valeoservice.com/en-com/techassist/vehicle/P-16779?country=MA&utm_source=chatgpt.com "Parts MITSUBISHI SPACE WAGON (N9_W, N8_W)"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 闭合 Pajero Pinin I 的 3 个 Ktype，按三门短轴 `H66W/H67W` 与五门长轴 `H76W/H77W` 拆分。两种车身宽度、高度相同，长度分别为 3735 mm 和 4035 mm。([www.slideshare.net][1])
* 闭合 Pajero Sport I 的 5 个 Ktype；2.5 TD 对应 `K94W`，3.0 V6 对应 `K96W`，均为五门相同外廓。([汽车数据网][2])
* 闭合 Pajero Sport II Ktype `59042`，确认欧洲四驱 3.0 车型代码 `KH6W`。([PartSouq][3])
* 闭合 Pajero Sport III Ktype `116340`，按 2019 年改款前后长度和高度变化拆分为两条映射；车身代码均为 `KS1W`。([PartSouq][4])
* 本轮新增 15 条 READY 映射、6 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：77
* READY 映射行：151
* PENDING Ktype：23
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
16506_3dr	16506	SUV	Pajero Pinin I	H66W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H66W三门短轴外廓。	READY
16506_5dr	16506	SUV	Pajero Pinin I	H76W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H76W五门长轴外廓。	READY
13863_3dr	13863	SUV	Pajero Pinin I	H66W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H66W三门短轴外廓。	READY
13863_5dr	13863	SUV	Pajero Pinin I	H76W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H76W五门长轴外廓。	READY
15481_3dr	15481	SUV	Pajero Pinin I	H67W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H67W三门短轴外廓。	READY
15481_5dr	15481	SUV	Pajero Pinin I	H77W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H77W五门长轴外廓。	READY
16886	16886	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
17754	17754	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
10682	10682	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
10681	10681	SUV	Pajero Sport I	K96W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K96W五门外廓。	READY
18476	18476	SUV	Pajero Sport I	K96W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K96W五门外廓。	READY
59042	59042	SUV	Pajero Sport II	KH6W	5	EU-MITSUBISHI-PAJERO-SPORT-II-SUV-5D-01	HIGH	KH6W五门四驱外廓。	READY
116340_prefl	116340	SUV	Pajero Sport III	KS1W	5	EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-PREFL-01	HIGH	2019改款前五门外廓。	READY
116340_facelift	116340	SUV	Pajero Sport III	KS1W	5	EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-FACELIFT-01	HIGH	2019改款后五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	3735	1695	1735	Automobile-Catalog 2005 Mitsubishi Pajero Pinin 1.8 MPI 3door	https://www.automobile-catalog.com/car/2005/2013860/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_3door.html
EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	4035	1695	1735	Automobile-Catalog 2005 Mitsubishi Pajero Pinin 1.8 MPI 5door	https://www.automobile-catalog.com/car/2005/2013890/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_5door.html
EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	4610	1775	1735	Auto-Data Mitsubishi Pajero Sport I K90 2.5 TD	https://www.auto-data.net/en/mitsubishi-pajero-sport-i-k90-2.5-td-99hp-15489
EU-MITSUBISHI-PAJERO-SPORT-II-SUV-5D-01	4695	1815	1800	Automobile-Catalog 2009 Mitsubishi Pajero Sport 3.2 TD	https://www.automobile-catalog.com/car/2009/2014040/mitsubishi_pajero_sport_3_2_td_automatic.html
EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-PREFL-01	4785	1815	1805	Mitsubishi Motors New Zealand 2019 Pajero Sport brochure	https://baycitymitsubishi.co.nz/wp-content/uploads/2019/12/2019-Mitsubishi-Pajero-Sport-Brochure.pdf
EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-FACELIFT-01	4825	1815	1835	Mitsubishi Motors Australia 2021 Pajero Sport brochure	https://xr793.com/wp-content/uploads/2023/04/2021-Mitsubishi-Pajero-Sport-AUS.pdf
```

## 下一步优先处理

1. 闭合 Pajero III 三门短轴、五门长轴及 Canvas Top。
2. 处理 Pajero IV 与 Pajero IV Van 的三门、五门和改款边界。
3. 处理 Pajero II、Pajero Classic 与 Canvas Top。
4. 完成剩余少量未处理车型并消除全部 PENDING。

推进信号：CONTINUE

[1]: https://www.slideshare.net/slideshow/2003-mitsubishi-pajero-pinin-service-repair-manual-118465944/118465944?utm_source=chatgpt.com "2003 Mitsubishi Pajero Pinin Service Repair Manual | PDF"
[2]: https://www.auto-data.net/en/mitsubishi-pajero-sport-i-k90-2.5-td-99hp-15489?utm_source=chatgpt.com "Mitsubishi Pajero Sport I (K90) 2.5 TD (99 Hp)"
[3]: https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MN136829&ssd=%24%2AKwE2AhMBMHddVEpRTFMCIG56Wl1DMj0wMSMlKmxFeSFtJzhuKD8jKCdhIT4nQTZtYB0xNTZHJikgbX9pbU9NNFQmKSBjMXF1anBub3kAAAAAO45YFA%3D%3D%24&utm_source=chatgpt.com "Body | Mitsubishi PAJERO/MONTERO SPORT Europe (EUROPE) KH6W | Parts Catalogs | PartSouq"
[4]: https://partsouq.com/en/catalog/genuine/vehicle?c=Mitsubishi&cid=3&cname=Body&q=Z8TGUKS10JM011741&ssd=%24%2AKwFNeWhHRy06IDUcKTV0aRUBISY4SUZLSlh3RAwKOS46NjA4am19Ozs3LCwqKzJob0ogDgoOPyRBL2F9fyxPSTIyTkhKERwFAR05A10KW0EEchZTXBpaRU0EBVBNXD8FWxFdRFshHnxzKjUqSU80NEsXGQNLT1tUXR1bQQRrAk89PU0tTD1ZCgpZXURbMyxPLlkKClcTXENaOCs0PXZkdSVcBAAAAADsRUxE%24&vid=0&utm_source=chatgpt.com "Body | Mitsubishi PAJERO SPORT Europe (EUROPE) KS1W Parts Catalogs | PartSouq"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 闭合 Pajero III 封闭式车型的 5 个 Ktype，新增 8 条 READY 映射。
* `57183` 覆盖 `V65W` 三门和 `V75W` 五门宽体；`57188` 覆盖 `V68W` 三门和 `V78W` 五门；`59059` 覆盖 `V64W` 三门和 `V74W` 五门，均按物理外廓拆分。([Allopneus][1])
* `59058` 仅关联 `V64W` 三门；`57184` 仅关联 `V68W` 三门，不创建无证据的五门派生行。([AUTODOC][2])
* 首次创建 5 个 Pajero III 封闭式尺寸组。三门/五门及窄体/宽体三维分别闭合，2.5 TD 五门的 4620×1885×1850 mm 外廓单独建组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：82
* READY 映射行：159
* PENDING Ktype：18
* 已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57183_3dr	57183	SUV	Pajero III	V65W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	HIGH	V65W三门宽体外廓。	READY
57183_5dr	57183	SUV	Pajero III	V75W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	HIGH	V75W五门长轴宽体外廓。	READY
59058	59058	SUV	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V64W三门外廓。	READY
59059_3dr	59059	SUV	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V64W三门外廓。	READY
59059_5dr	59059	SUV	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-02	HIGH	V74W五门长轴外廓。	READY
57184	57184	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门外廓。	READY
57188_3dr	57188	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门外廓。	READY
57188_5dr	57188	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	4260	1845	1845	Auto-Data Mitsubishi Pajero III 3.2 DI-D 5 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.2-di-d-165hp-5-seat-automatic-24528
EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	4775	1845	1855	Auto-Data Mitsubishi Pajero III 3.2 DI-D 7 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.2-di-d-165hp-7-seat-automatic-24527
EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	4280	1875	1845	Auto-Data Mitsubishi Pajero III 3.5 V6 GDI 5 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.5-v6-gdi-202hp-5-seat-15496
EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	4795	1875	1855	Auto-Data Mitsubishi Pajero III 3.5 V6 GDI 7 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.5-v6-gdi-202hp-7-seat-15497
EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-02	4620	1885	1850	Auto-Data Mitsubishi Pajero III 2.5 TD 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iii-2.5-td-5-dr-115hp-15493
```

## 下一步优先处理

1. 闭合 Pajero III Canvas Top 的 3 个 Ktype，确认其实际短轴车身代码与开放式车身三维。
2. 处理 Pajero IV 与 Pajero IV Van 的三门、五门及改款高度边界。
3. 最后闭合 Pajero II、Pajero II Canvas Top 与 Pajero Classic。

推进信号：CONTINUE

[1]: https://www.allopneus.com/vehicule/mitsubishi/pajero/pajero-iii?utm_source=chatgpt.com "Pneu MITSUBISHI PAJERO III : Pression et dimensions des pneus - Allopneus.com"
[2]: https://www.autodoc.parts/car-parts/radiator-parts-10203/mitsubishi/pajero-shogun/pajero-iii-v7-w-v6-w/59058-2-5-tdi-v64w?utm_source=chatgpt.com "Radiator Mitsubishi Pajero V60 2.5 TDi 99 hp Diesel 73 kW ..."
[3]: https://www.auto-data.net/en/mitsubishi-pajero-iii-2.5-td-3-dr-115hp-15492?utm_source=chatgpt.com "Mitsubishi Pajero III 2.5 TD (3 dr) (115 Hp) /SUV 2000 - 2006"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 闭合 Pajero IV 的 3 个 Ktype：`10492` 覆盖 `V83W` 三门与 `V93W` 五门；`10491` 覆盖 `V88W` 三门与 `V98W` 五门；`128025` 仅对应 `V98W` 五门。([托佩尔扎特尔][1])
* Mitsubishi 官方规格确认三门长度 4385 mm、五门长度 4900 mm；标准宽体为 1875 mm，GLX 窄体包为 1845 mm；车顶行李架使车高增加 30 mm。因此按门数、窄体/宽体及有无车顶行李架拆分为 8 个稳定尺寸组。([哈布尔汽车][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：85
* READY 映射行：179
* PENDING Ktype：15
* 已确认尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10492_3dr_narrow_lowroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	HIGH	V83W三门窄体无车顶行李架外廓。	READY
10492_3dr_narrow_highroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	HIGH	V83W三门窄体带车顶行李架外廓。	READY
10492_3dr_wide_lowroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V83W三门宽体无车顶行李架外廓。	READY
10492_3dr_wide_highroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	HIGH	V83W三门宽体带车顶行李架外廓。	READY
10492_5dr_narrow_lowroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	HIGH	V93W五门窄体无车顶行李架外廓。	READY
10492_5dr_narrow_highroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	HIGH	V93W五门窄体带车顶行李架外廓。	READY
10492_5dr_wide_lowroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V93W五门宽体无车顶行李架外廓。	READY
10492_5dr_wide_highroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V93W五门宽体带车顶行李架外廓。	READY
128025_5dr_narrow_lowroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	MEDIUM	V98W五门窄体无车顶行李架外廓。	READY
128025_5dr_narrow_highroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	MEDIUM	V98W五门窄体带车顶行李架外廓。	READY
128025_5dr_wide_lowroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98W五门宽体无车顶行李架外廓。	READY
128025_5dr_wide_highroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V98W五门宽体带车顶行李架外廓。	READY
10491_3dr_narrow_lowroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	HIGH	V88W三门窄体无车顶行李架外廓。	READY
10491_3dr_narrow_highroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	HIGH	V88W三门窄体带车顶行李架外廓。	READY
10491_3dr_wide_lowroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V88W三门宽体无车顶行李架外廓。	READY
10491_3dr_wide_highroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	HIGH	V88W三门宽体带车顶行李架外廓。	READY
10491_5dr_narrow_lowroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	HIGH	V98W五门窄体无车顶行李架外廓。	READY
10491_5dr_narrow_highroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	HIGH	V98W五门窄体带车顶行李架外廓。	READY
10491_5dr_wide_lowroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98W五门宽体无车顶行李架外廓。	READY
10491_5dr_wide_highroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V98W五门宽体带车顶行李架外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	4385	1845	1850	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	4385	1845	1880	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	4385	1875	1850	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	4385	1875	1880	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	4900	1845	1870	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	4900	1845	1900	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	4900	1875	1870	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	4900	1875	1900	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
```

## 下一步优先处理

1. 将 Pajero IV Van 的 `12480`、`118544`、`12484` 关联至已闭合的三门/五门 Pajero IV 外廓。
2. 闭合 Pajero III Canvas Top 的 `14688`、`16455`、`14687`。
3. 最后处理 Pajero II、Pajero II Canvas Top 与 Pajero Classic，消除剩余 PENDING。

推进信号：CONTINUE

[1]: https://www.topersatzteile.de/autoteile/horn-fanfare/10420/mitsubishi-pajero-iv-v8-w-v9-w/10492-3-0-4wd-v83w-v93w?utm_source=chatgpt.com "Hupe MITSUBISHI Pajero IV (V80) 3.0 4WD (V83W, V93W) 178 ..."
[2]: https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf "18MY_RC_PAJERO_GCC_En.pdf"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 1. 更新点

* 完成 Pajero III Canvas Top 的 3 个 Ktype。相关目录实际指向 `V65W/V75W`、`V68W/V78W` 车身代码，因此分别关联已闭合的 Pajero III 三门、五门尺寸组，不新建重复尺寸组。([KMoto Shop][1])
* 完成 Pajero IV Van 的 3 个 Ktype。确认覆盖 `V88V/V98V` 或 `V88W/V98W` 三门、五门商用版本，关联现有 Pajero IV 宽体无行李架尺寸组。([Nokian Tyres][2])
* 本轮新增 12 条 READY 映射，全部复用现有尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射行：191
* PENDING Ktype：9
* 已确认尺寸组：55
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
14688_3dr	14688	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门车身分支。	READY
14688_5dr	14688	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴车身分支。	READY
16455_3dr	16455	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门车身分支。	READY
16455_5dr	16455	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴车身分支。	READY
14687_3dr	14687	SUV	Pajero III	V65W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	HIGH	V65W三门宽体车身分支。	READY
14687_5dr	14687	SUV	Pajero III	V75W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	HIGH	V75W五门长轴宽体车身分支。	READY
12480_3dr	12480	Van	Pajero IV Van	V88V	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	MEDIUM	V88V三门商用车身。	READY
12480_5dr	12480	Van	Pajero IV Van	V98V	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	MEDIUM	V98V五门商用车身。	READY
118544_3dr	118544	Van	Pajero IV Van	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	MEDIUM	V88W三门商用车身。	READY
118544_5dr	118544	Van	Pajero IV Van	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	MEDIUM	V98W五门商用车身。	READY
12484_3dr	12484	Van	Pajero IV Van	V88V	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V88V三门商用车身。	READY
12484_5dr	12484	Van	Pajero IV Van	V98V	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98V五门商用车身。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 闭合 Pajero II 的 `V24W/V26W/V23W/V25W` 三门和 `V46W/V43W/V45W` 五门外廓。
2. 闭合 Pajero II Canvas Top 的 `V24C`、`V23C` 开放式三门外廓。
3. 将 Pajero Classic `V24W` 关联到最终确认的 Pajero II 三门尺寸组。
4. 处理 Ktype `52852` 的 `V68W/V78W` 代际归属并复用 Pajero III尺寸组，消除剩余全部 PENDING。

推进信号：CONTINUE

[1]: https://www.kmotorshop.com/en/article-list/list/car/16455?utm_source=chatgpt.com "MITSUBISHI PAJERO III Canvas Top (V6_W, V7_W) 3.2 DI-D ..."
[2]: https://www.nokiantyres.jp/taiyawo-tansu/zi-dong-chemeka/mitsubishi/2016/pajero-iv-van-v90-v80/3-2-td-4wd-v88v-v98v-147kw/?utm_source=chatgpt.com "2016 Mitsubishi PAJERO IV Van (V90, V80) 3.2 TD 4WD ..."


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11401-11500_ktype_dimension_mapping_final.tsv
- left18448_11401-11500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
## 更新点

* 闭合最后 9 个 Ktype：Pajero Classic、Pajero II 封闭式、Pajero II Canvas Top，以及实际归属 Pajero III 的 Ktype `52852`。
* Pajero II 的 `V23/V24/V25/V26/V43/V44/V45/V46`、Canvas Top 的 `V23C/V24C`，以及 Ktype `52852` 的 `V68W/V78W` 物理分支均已建立闭合映射；短轴/长轴、窄体/宽体、前后期和开放式车身分别使用对应尺寸组。([car.avtoelektronika63.ru][1])
* 已完成轻量机械检查：两张表表头正确，`id` 和 `DIMENSION_GROUP_ID` 唯一，全部引用闭合，尺寸、来源及 URL 非空，无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：205
* PENDING Ktype：0
* DIMENSION_GROUP：63
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
56336_prefl	56336	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56336_facelift	56336	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
56333_prefl	56333	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
56333_facelift	56333	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
56337_prefl	56337	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56337_facelift	56337	SUV	Outlander III	GF7W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
111463_prefl	111463	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前PHEV外廓。	READY
111463_facelift	111463	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后PHEV外廓。	READY
56338_prefl	56338	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56338_facelift	56338	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
56339_prefl	56339	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	HIGH	Ktype跨越Outlander III改款；改款前外廓。	READY
56339_facelift	56339	SUV	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	Ktype跨越Outlander III改款；改款后外廓。	READY
126681_prefl	126681	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126681_facelift	126681	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
153413	153413	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	2019年后2.4 Hybrid，仅改款后外廓。	READY
126682_prefl	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126682_facelift	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
126684_prefl	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前外廓。	READY
126684_facelift	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后外廓。	READY
107375_prefl	107375	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	Ktype跨越Outlander III改款；改款前GT外廓。	READY
107375_facelift	107375	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	Ktype跨越Outlander III改款；改款后GT外廓。	READY
146352	146352	SUV	Outlander III	GG2W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	2017年后Plug-in Hybrid，仅改款后外廓。	READY
142852_prefl	142852	Van	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	MEDIUM	商用Van与同代SUV共用外廓；改款前分支。	READY
142852_facelift	142852	Van	Outlander III	GF6W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	MEDIUM	商用Van与同代SUV共用外廓；改款后分支。	READY
142855	142855	Van	Outlander III	GG3W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	HIGH	商用Hybrid Van与改款后SUV共用外廓。	READY
144430_lowroof	144430	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GM4W低车顶物理外廓。	READY
144430_highroof	144430	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GM4W高车顶物理外廓。	READY
147478_lowroof	147478	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GN0W低车顶物理外廓。	READY
147478_highroof	147478	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GN0W高车顶物理外廓。	READY
153319_lowroof	153319	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GN0W低车顶物理外廓。	READY
153319_highroof	153319	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GN0W高车顶物理外廓。	READY
801358_lowroof	801358	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-LOWROOF-01	HIGH	2025年欧洲改款低车顶物理外廓。	READY
801358_highroof	801358	SUV	Outlander IV	GN0W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-HIGHROOF-01	HIGH	2025年欧洲改款高车顶物理外廓。	READY
144431_lowroof	144431	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	HIGH	GM4W低车顶物理外廓。	READY
144431_highroof	144431	SUV	Outlander IV	GM4W	5	EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	HIGH	GM4W高车顶物理外廓。	READY
16915	16915	SUV	Pajero Classic	V24W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-NARROW-01	HIGH	V24W三门短轴封闭式外廓。	READY
3385_3dr	3385	SUV	Pajero I	L044G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L044G三门短轴封闭式外廓。	READY
3385_5dr	3385	SUV	Pajero I	L049G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L049G五门长轴封闭式外廓。	READY
3386_3dr	3386	SUV	Pajero I	L044G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L044G三门短轴封闭式外廓。	READY
3386_5dr	3386	SUV	Pajero I	L049G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L049G五门长轴封闭式外廓。	READY
3388_3dr	3388	SUV	Pajero I	L141G	3	EU-MITSUBISHI-PAJERO-I-SUV-3D-01	HIGH	L141G三门短轴封闭式外廓。	READY
3388_5dr	3388	SUV	Pajero I	L146G	5	EU-MITSUBISHI-PAJERO-I-SUV-5D-01	HIGH	L146G五门长轴封闭式外廓。	READY
3382	3382	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3383	3383	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3384	3384	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3387	3387	Convertible	Pajero I Canvas Top		3	EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	HIGH	三门Canvas Top短轴外廓。	READY
3414_3dr	3414	SUV	Pajero II	V24W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-NARROW-01	HIGH	V24W三门短轴封闭式外廓。	READY
3414_5dr	3414	SUV	Pajero II	V44W	5	EU-MITSUBISHI-PAJERO-II-SUV-5D-NARROW-01	HIGH	V44W五门长轴封闭式外廓。	READY
101121_3dr	101121	SUV	Pajero II	V26W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-LATE-01	HIGH	V26W三门宽体封闭式外廓。	READY
101121_5dr	101121	SUV	Pajero II	V46W	5	EU-MITSUBISHI-PAJERO-II-SUV-5D-NARROW-02	HIGH	V46W五门长轴封闭式外廓。	READY
15261_3dr	15261	SUV	Pajero II	V23W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-LATE-01	HIGH	V23W三门宽体封闭式外廓。	READY
15261_5dr	15261	SUV	Pajero II	V43W	5	EU-MITSUBISHI-PAJERO-II-SUV-5D-WIDE-LATE-01	HIGH	V43W五门长轴宽体外廓。	READY
3415_3dr	3415	SUV	Pajero II	V23W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-EARLY-01	HIGH	V23W三门早期宽体外廓。	READY
3415_5dr	3415	SUV	Pajero II	V43W	5	EU-MITSUBISHI-PAJERO-II-SUV-5D-WIDE-EARLY-01	HIGH	V43W五门早期长轴宽体外廓。	READY
52852_3dr	52852	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	TecDoc车型归属Pajero III；V68W三门外廓。	READY
52852_5dr	52852	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	TecDoc车型归属Pajero III；V78W五门外廓。	READY
11860_3dr	11860	SUV	Pajero II	V25W	3	EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-LATE-01	HIGH	V25W三门宽体封闭式外廓。	READY
11860_5dr	11860	SUV	Pajero II	V45W	5	EU-MITSUBISHI-PAJERO-II-SUV-5D-WIDE-LATE-01	HIGH	V45W五门长轴宽体外廓。	READY
3413	3413	Convertible	Pajero II Canvas Top	V24C	3	EU-MITSUBISHI-PAJERO-II-CONVERTIBLE-3D-01	HIGH	V24C三门短轴开放式外廓。	READY
3416	3416	Convertible	Pajero II Canvas Top	V23C	3	EU-MITSUBISHI-PAJERO-II-CONVERTIBLE-3D-01	HIGH	V23C三门短轴开放式外廓。	READY
57183_3dr	57183	SUV	Pajero III	V65W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	HIGH	V65W三门宽体外廓。	READY
57183_5dr	57183	SUV	Pajero III	V75W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	HIGH	V75W五门长轴宽体外廓。	READY
59058	59058	SUV	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V64W三门外廓。	READY
59059_3dr	59059	SUV	Pajero III	V64W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V64W三门外廓。	READY
59059_5dr	59059	SUV	Pajero III	V74W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-02	HIGH	V74W五门长轴外廓。	READY
57184	57184	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门外廓。	READY
57188_3dr	57188	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门外廓。	READY
57188_5dr	57188	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴外廓。	READY
14688_3dr	14688	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门车身分支。	READY
14688_5dr	14688	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴车身分支。	READY
16455_3dr	16455	SUV	Pajero III	V68W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	HIGH	V68W三门车身分支。	READY
16455_5dr	16455	SUV	Pajero III	V78W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	HIGH	V78W五门长轴车身分支。	READY
14687_3dr	14687	SUV	Pajero III	V65W	3	EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	HIGH	V65W三门宽体车身分支。	READY
14687_5dr	14687	SUV	Pajero III	V75W	5	EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	HIGH	V75W五门长轴宽体车身分支。	READY
10492_3dr_narrow_lowroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	HIGH	V83W三门窄体无车顶行李架外廓。	READY
10492_3dr_narrow_highroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	HIGH	V83W三门窄体带车顶行李架外廓。	READY
10492_3dr_wide_lowroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V83W三门宽体无车顶行李架外廓。	READY
10492_3dr_wide_highroof	10492	SUV	Pajero IV	V83W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	HIGH	V83W三门宽体带车顶行李架外廓。	READY
10492_5dr_narrow_lowroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	HIGH	V93W五门窄体无车顶行李架外廓。	READY
10492_5dr_narrow_highroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	HIGH	V93W五门窄体带车顶行李架外廓。	READY
10492_5dr_wide_lowroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V93W五门宽体无车顶行李架外廓。	READY
10492_5dr_wide_highroof	10492	SUV	Pajero IV	V93W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V93W五门宽体带车顶行李架外廓。	READY
128025_5dr_narrow_lowroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	MEDIUM	V98W五门窄体无车顶行李架外廓。	READY
128025_5dr_narrow_highroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	MEDIUM	V98W五门窄体带车顶行李架外廓。	READY
128025_5dr_wide_lowroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98W五门宽体无车顶行李架外廓。	READY
128025_5dr_wide_highroof	128025	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V98W五门宽体带车顶行李架外廓。	READY
10491_3dr_narrow_lowroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	HIGH	V88W三门窄体无车顶行李架外廓。	READY
10491_3dr_narrow_highroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	HIGH	V88W三门窄体带车顶行李架外廓。	READY
10491_3dr_wide_lowroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V88W三门宽体无车顶行李架外廓。	READY
10491_3dr_wide_highroof	10491	SUV	Pajero IV	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	HIGH	V88W三门宽体带车顶行李架外廓。	READY
10491_5dr_narrow_lowroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	HIGH	V98W五门窄体无车顶行李架外廓。	READY
10491_5dr_narrow_highroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	HIGH	V98W五门窄体带车顶行李架外廓。	READY
10491_5dr_wide_lowroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98W五门宽体无车顶行李架外廓。	READY
10491_5dr_wide_highroof	10491	SUV	Pajero IV	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	HIGH	V98W五门宽体带车顶行李架外廓。	READY
12480_3dr	12480	Van	Pajero IV Van	V88V	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	MEDIUM	V88V三门商用车身。	READY
12480_5dr	12480	Van	Pajero IV Van	V98V	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	MEDIUM	V98V五门商用车身。	READY
118544_3dr	118544	Van	Pajero IV Van	V88W	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	MEDIUM	V88W三门商用车身。	READY
118544_5dr	118544	Van	Pajero IV Van	V98W	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	MEDIUM	V98W五门商用车身。	READY
12484_3dr	12484	Van	Pajero IV Van	V88V	3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	HIGH	V88V三门商用车身。	READY
12484_5dr	12484	Van	Pajero IV Van	V98V	5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	HIGH	V98V五门商用车身。	READY
16506_3dr	16506	SUV	Pajero Pinin I	H66W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H66W三门短轴外廓。	READY
16506_5dr	16506	SUV	Pajero Pinin I	H76W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H76W五门长轴外廓。	READY
13863_3dr	13863	SUV	Pajero Pinin I	H66W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H66W三门短轴外廓。	READY
13863_5dr	13863	SUV	Pajero Pinin I	H76W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H76W五门长轴外廓。	READY
15481_3dr	15481	SUV	Pajero Pinin I	H67W	3	EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	HIGH	H67W三门短轴外廓。	READY
15481_5dr	15481	SUV	Pajero Pinin I	H77W	5	EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	HIGH	H77W五门长轴外廓。	READY
16886	16886	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
17754	17754	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
10682	10682	SUV	Pajero Sport I	K94W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K94W五门外廓。	READY
10681	10681	SUV	Pajero Sport I	K96W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K96W五门外廓。	READY
18476	18476	SUV	Pajero Sport I	K96W	5	EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	HIGH	K96W五门外廓。	READY
59042	59042	SUV	Pajero Sport II	KH6W	5	EU-MITSUBISHI-PAJERO-SPORT-II-SUV-5D-01	HIGH	KH6W五门四驱外廓。	READY
116340_prefl	116340	SUV	Pajero Sport III	KS1W	5	EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-PREFL-01	HIGH	2019改款前五门外廓。	READY
116340_facelift	116340	SUV	Pajero Sport III	KS1W	5	EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-FACELIFT-01	HIGH	2019改款后五门外廓。	READY
14710	14710	Sedan	Proudia I	S32A	4	EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	HIGH	S32A标准轴距四门Sedan外廓。	READY
14711_proudia	14711	Sedan	Proudia I	S33A	4	EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	HIGH	S33A标准轴距四门Sedan外廓。	READY
14711_dignity	14711	Sedan	Dignity I	S43A	4	EU-MITSUBISHI-DIGNITY-I-SEDAN-4D-LWB-01	HIGH	S43A加长轴距四门豪华Sedan外廓。	READY
11514	11514	MPV	Santamo I	UG	4	EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	HIGH	UG前驱四门MPV外廓。	READY
11515	11515	MPV	Santamo I	UG	4	EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	HIGH	UG四驱四门MPV外廓。	READY
3359	3359	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3360	3360	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3361	3361	Coupe	Sapporo I	A123	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A123双门Coupe外廓。	READY
3358	3358	Coupe	Sapporo I	A121	2	EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	HIGH	A121双门Coupe外廓。	READY
3362	3362	Coupe	Sapporo II	A161A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A161A双门Coupe外廓。	READY
3363	3363	Coupe	Sapporo II	A164A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164A双门Coupe外廓。	READY
3364	3364	Coupe	Sapporo II	A164A	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164A双门Coupe外廓。	READY
3365	3365	Coupe	Sapporo II	A164	2	EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	HIGH	A164双门Coupe外廓。	READY
3366	3366	Coupe	Sapporo III	E16A	4	EU-MITSUBISHI-SAPPORO-III-COUPE-4D-01	HIGH	E16A四门硬顶Coupe外廓。	READY
3417	3417	Sedan	Sigma I	F16A	4	EU-MITSUBISHI-SIGMA-I-SEDAN-4D-01	HIGH	F16A四门Sedan外廓。	READY
10924	10924	MPV	Space Runner I	N11W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-01	HIGH	N11W四门标准高度外廓。	READY
13881_lowroof	13881	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N63W三门低车顶外廓。	READY
13881_highroof	13881	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N63W三门带车顶行李架外廓。	READY
54971_lowroof	54971	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N63W三门低车顶外廓。	READY
54971_highroof	54971	MPV	Space Runner II	N63W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N63W三门带车顶行李架外廓。	READY
10925	10925	MPV	Space Runner I	N21W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	HIGH	N21W四门较高外廓。	READY
11861	11861	MPV	Space Runner I	N13W	4	EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	HIGH	N13W四门较高外廓。	READY
13880_lowroof	13880	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N64W三门低车顶外廓。	READY
13880_highroof	13880	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N64W三门带车顶行李架外廓。	READY
54972_lowroof	54972	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	HIGH	N64W三门低车顶外廓。	READY
54972_highroof	54972	MPV	Space Runner II	N64W	3	EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	HIGH	N64W三门带车顶行李架外廓。	READY
10939_early_nomoulding_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
10939_early_nomoulding_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
10939_early_sidemoulding_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
10939_early_sidemoulding_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
10939_prefl_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
10939_prefl_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
10939_facelift_lowroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
10939_facelift_highroof	10939	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
14442_early_nomoulding_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
14442_early_nomoulding_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
14442_early_sidemoulding_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
14442_early_sidemoulding_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
14442_prefl_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
14442_prefl_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
14442_facelift_lowroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
14442_facelift_highroof	14442	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
16177_prefl_lowroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
16177_prefl_highroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
16177_facelift_lowroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16177_facelift_highroof	16177	MPV	Space Star I	DG1A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
16443_prefl_lowroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
16443_prefl_highroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
16443_facelift_lowroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16443_facelift_highroof	16443	MPV	Space Star I	DG3A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
11379_early_nomoulding_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
11379_early_nomoulding_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
11379_early_sidemoulding_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
11379_early_sidemoulding_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
11379_prefl_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
11379_prefl_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
11379_facelift_lowroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
11379_facelift_highroof	11379	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
15501_early_nomoulding_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	HIGH	早期无侧防护饰条低车顶外廓。	READY
15501_early_nomoulding_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	HIGH	早期无侧防护饰条带车顶行李架外廓。	READY
15501_early_sidemoulding_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	HIGH	早期带侧防护饰条低车顶外廓。	READY
15501_early_sidemoulding_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	HIGH	早期带侧防护饰条及车顶行李架外廓。	READY
15501_prefl_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前1715毫米宽体低车顶外廓。	READY
15501_prefl_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前1715毫米宽体带车顶行李架外廓。	READY
15501_facelift_lowroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款低车顶外廓。	READY
15501_facelift_highroof	15501	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款带车顶行李架外廓。	READY
16891_lowroof	16891	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16891_highroof	16891	MPV	Space Star I	DG5A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
15369_prefl_lowroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	HIGH	改款前五门低车顶外廓。	READY
15369_prefl_highroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	HIGH	改款前五门带车顶行李架外廓。	READY
15369_facelift_lowroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
15369_facelift_highroof	15369	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
16890_lowroof	16890	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	HIGH	2003改款五门低车顶外廓。	READY
16890_highroof	16890	MPV	Space Star I	DG4A	5	EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	HIGH	2003改款五门带车顶行李架外廓。	READY
56018_prefl	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	HIGH	2012初期五门外廓。	READY
56018_facelift_2015	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	HIGH	2015首次改款五门外廓。	READY
56018_facelift_2019	56018	Hatchback	Space Star VI	A05A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2019二次改款五门外廓。	READY
57508_prefl	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	HIGH	2012初期五门外廓。	READY
57508_facelift_2015	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	HIGH	2015首次改款五门外廓。	READY
57508_facelift_2019	57508	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2019二次改款五门外廓。	READY
143733	143733	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2020年后五门外廓。	READY
151926	151926	Hatchback	Space Star VI	A03A	5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	HIGH	2020年后LPG五门外廓。	READY
16779_lowroof	16779	MPV	Space Wagon III	N83W	5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	HIGH	五门无车顶行李架外廓。	READY
16779_highroof	16779	MPV	Space Wagon III	N83W	5	EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	HIGH	五门带车顶行李架外廓。	READY
3375	3375	MPV	Space Wagon I	D05V	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D05V五门前驱外廓。	READY
3381	3381	MPV	Space Wagon I	D09W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D09W五门前驱外廓。	READY
3380_prefl	3380	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	HIGH	D08W早期五门四驱外廓。	READY
3380_facelift	3380	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	HIGH	D08W后期五门四驱外廓。	READY
3376	3376	MPV	Space Wagon I	D04W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D04W五门前驱外廓。	READY
3377	3377	MPV	Space Wagon I	D08W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	HIGH	D08W早期五门四驱外廓。	READY
3378	3378	MPV	Space Wagon I	D04W	5	EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	HIGH	D04W五门前驱外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_11401-11500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-PREFL-01	4655	1800	1680	Mitsubishi Motors Outlander PHEV AXCR 2014 technical specifications	https://www.mitsubishi-motors.com/en/brand/motorsports/ev_phev/axcr/2014/
EU-MITSUBISHI-OUTLANDER-III-SUV-5D-FACELIFT-01	4695	1810	1680	Mitsubishi Motors Outlander official specifications	https://www.mitsubishi-motors.com/en/products/outlander/
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-LOWROOF-01	4710	1862	1740	Mitsubishi Motors Australia 23MY Outlander brochure	https://www.mitsubishi-motors.com.au/content/dam/mmal/pdfs/vehicle-brochures/23MY%20Outlander%20Brochure.pdf
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-PREFL-HIGHROOF-01	4710	1862	1745	Mitsubishi Motors Australia 23MY Outlander brochure	https://www.mitsubishi-motors.com.au/content/dam/mmal/pdfs/vehicle-brochures/23MY%20Outlander%20Brochure.pdf
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-LOWROOF-01	4719	1862	1746	Mitsubishi Motors Deutschland Outlander press information	https://presse.mitsubishi-motors.de/pm/hochwertig-und-innovativ-neuer-mitsubishi-outlander-kommt-nach-deutschland
EU-MITSUBISHI-OUTLANDER-IV-SUV-5D-FACELIFT-HIGHROOF-01	4719	1862	1750	Mitsubishi Motors Deutschland Outlander press information	https://presse.mitsubishi-motors.de/pm/hochwertig-und-innovativ-neuer-mitsubishi-outlander-kommt-nach-deutschland
EU-MITSUBISHI-PAJERO-II-SUV-3D-NARROW-01	4075	1695	1805	Auto-Data Mitsubishi Pajero II Metal Top 2.5 TD GL	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-2.5-td-gl-99hp-15519
EU-MITSUBISHI-PAJERO-I-SUV-3D-01	3995	1680	1850	CarSpecsGuru Mitsubishi Pajero I 3-door specifications	https://www.carspecsguru.com/mitsubishi/pajero/4337/6534/modification-46077
EU-MITSUBISHI-PAJERO-I-SUV-5D-01	4650	1680	1890	AutoData24 Mitsubishi Pajero I 5-door specifications	https://autodata24.com/mitsubishi/pajero/pajero-i-l04_gl14_g/25-td-l044gl049g-87-hp/details
EU-MITSUBISHI-PAJERO-I-CONVERTIBLE-3D-01	3995	1679	1849	AutoData24 Mitsubishi Pajero I Canvas Top specifications	https://autodata24.com/mitsubishi/pajero/pajero-i-canvas-top-l04_g/25-td-l044gl049g-95-hp/details
EU-MITSUBISHI-PAJERO-II-SUV-5D-NARROW-01	4655	1695	1855	Auto-Data Mitsubishi Pajero II 2.5 TD GL	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-2.5-td-gl-99hp-15505
EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-LATE-01	4145	1785	1845	Auto-Data Mitsubishi Pajero II Metal Top 3.5 V6 24V GLS	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-3.5-i-v6-24v-gls-194hp-15525
EU-MITSUBISHI-PAJERO-II-SUV-5D-NARROW-02	4700	1695	1855	Auto-Data Mitsubishi Pajero II 2.8 TD GLX	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-2.8-td-glx-125hp-15506
EU-MITSUBISHI-PAJERO-II-SUV-5D-WIDE-LATE-01	4725	1775	1900	Auto-Data Mitsubishi Pajero II 3.0 V6 24V GLS	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-24v-gls-177hp-15508
EU-MITSUBISHI-PAJERO-II-SUV-3D-WIDE-EARLY-01	4145	1785	1815	Auto-Data Mitsubishi Pajero II Metal Top 3.0 V6 GLS	https://www.auto-data.net/en/mitsubishi-pajero-ii-metal-top-v2-w-v4-w-3.0-i-v6-24v-gls-150hp-automatic-24515
EU-MITSUBISHI-PAJERO-II-SUV-5D-WIDE-EARLY-01	4725	1785	1865	Auto-Data Mitsubishi Pajero II 3.0 V6 GLS	https://www.auto-data.net/en/mitsubishi-pajero-ii-v2-w-v4-w-3.0-i-v6-gls-150hp-automatic-24517
EU-MITSUBISHI-PAJERO-III-SUV-3D-NARROW-01	4260	1845	1845	Auto-Data Mitsubishi Pajero III 3.2 DI-D 5 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.2-di-d-165hp-5-seat-automatic-24528
EU-MITSUBISHI-PAJERO-III-SUV-5D-NARROW-01	4775	1845	1855	Auto-Data Mitsubishi Pajero III 3.2 DI-D 7 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.2-di-d-165hp-7-seat-automatic-24527
EU-MITSUBISHI-PAJERO-II-CONVERTIBLE-3D-01	4140	1780	1820	UltimateSpecs Mitsubishi Pajero II 3.0 V6 Soft Top	https://www.ultimatespecs.com/car-specs/Mitsubishi/7001/Mitsubishi-Pajero-II-%28V20%29-30-V6-Soft-Top-Auto.html
EU-MITSUBISHI-PAJERO-III-SUV-3D-WIDE-01	4280	1875	1845	Auto-Data Mitsubishi Pajero III 3.5 V6 GDI 5 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.5-v6-gdi-202hp-5-seat-15496
EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-01	4795	1875	1855	Auto-Data Mitsubishi Pajero III 3.5 V6 GDI 7 Seat	https://www.auto-data.net/en/mitsubishi-pajero-iii-3.5-v6-gdi-202hp-7-seat-15497
EU-MITSUBISHI-PAJERO-III-SUV-5D-WIDE-02	4620	1885	1850	Auto-Data Mitsubishi Pajero III 2.5 TD 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iii-2.5-td-5-dr-115hp-15493
EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-LOWROOF-01	4385	1845	1850	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-NARROW-HIGHROOF-01	4385	1845	1880	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-LOWROOF-01	4385	1875	1850	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-3D-WIDE-HIGHROOF-01	4385	1875	1880	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-LOWROOF-01	4900	1845	1870	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-NARROW-HIGHROOF-01	4900	1845	1900	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-LOWROOF-01	4900	1875	1870	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-IV-SUV-5D-WIDE-HIGHROOF-01	4900	1875	1900	Mitsubishi Motors Pajero official brochure	https://habtoormotors.com/mitsubishi/wp-content/themes/mitsubishi/brochures/pajero_updated.pdf
EU-MITSUBISHI-PAJERO-PININ-I-SUV-3D-01	3735	1695	1735	Automobile-Catalog 2005 Mitsubishi Pajero Pinin 1.8 MPI 3door	https://www.automobile-catalog.com/car/2005/2013860/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_3door.html
EU-MITSUBISHI-PAJERO-PININ-I-SUV-5D-01	4035	1695	1735	Automobile-Catalog 2005 Mitsubishi Pajero Pinin 1.8 MPI 5door	https://www.automobile-catalog.com/car/2005/2013890/mitsubishi_pajero_pinin_shogun_pinin_1_8_mpi_5door.html
EU-MITSUBISHI-PAJERO-SPORT-I-SUV-5D-01	4610	1775	1735	Auto-Data Mitsubishi Pajero Sport I K90 2.5 TD	https://www.auto-data.net/en/mitsubishi-pajero-sport-i-k90-2.5-td-99hp-15489
EU-MITSUBISHI-PAJERO-SPORT-II-SUV-5D-01	4695	1815	1800	Automobile-Catalog 2009 Mitsubishi Pajero Sport 3.2 TD	https://www.automobile-catalog.com/car/2009/2014040/mitsubishi_pajero_sport_3_2_td_automatic.html
EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-PREFL-01	4785	1815	1805	Mitsubishi Motors New Zealand 2019 Pajero Sport brochure	https://baycitymitsubishi.co.nz/wp-content/uploads/2019/12/2019-Mitsubishi-Pajero-Sport-Brochure.pdf
EU-MITSUBISHI-PAJERO-SPORT-III-SUV-5D-FACELIFT-01	4825	1815	1835	Mitsubishi Motors Australia 2021 Pajero Sport brochure	https://xr793.com/wp-content/uploads/2023/04/2021-Mitsubishi-Pajero-Sport-AUS.pdf
EU-MITSUBISHI-PROUDIA-I-SEDAN-4D-01	5050	1870	1475	Mitsubishi Motors Car History	https://www.mitsubishi-motors.com/en/company/history/car/
EU-MITSUBISHI-DIGNITY-I-SEDAN-4D-LWB-01	5335	1870	1485	Mitsubishi Motors Car History; Goo-net Mitsubishi Dignity catalog	https://www.mitsubishi-motors.com/en/company/history/car/; https://www.goo-net.com/catalog/MITSUBISHI/DIGNITY/4007160/
EU-MITSUBISHI-SANTAMO-I-MPV-4D-01	4515	1695	1620	Auto-Data Mitsubishi Santamo 2.0 i 16V; Auto-Data Mitsubishi Santamo 2.0 i 16V AWD	https://www.auto-data.net/en/mitsubishi-santamo-2.0-i-16v-139hp-15790; https://www.auto-data.net/en/mitsubishi-santamo-2.0-i-16v-awd-139hp-15791
EU-MITSUBISHI-SAPPORO-I-COUPE-2D-01	4430	1675	1345	Automobile-Catalog 1978 Mitsubishi Sapporo 2000 GSL	https://www.automobile-catalog.com/car/1978/36065/mitsubishi_sapporo_2000_gsl.html
EU-MITSUBISHI-SAPPORO-II-COUPE-2D-01	4525	1675	1350	Automobile-Catalog 1984 Mitsubishi Sapporo 2000 GLS	https://www.automobile-catalog.com/car/1984/1909310/mitsubishi_sapporo_2000_gls_automatic.html
EU-MITSUBISHI-SAPPORO-III-COUPE-4D-01	4660	1690	1370	Automobile-Catalog 1987 Mitsubishi Sapporo automatic catalyst	https://www.automobile-catalog.com/car/1987/59900/mitsubishi_sapporo_automatic_cat.html
EU-MITSUBISHI-SIGMA-I-SEDAN-4D-01	4750	1775	1435	Auto-Data Mitsubishi Sigma F16A 3.0 V6	https://www.auto-data.net/en/mitsubishi-sigma-f16a-3.0-v6-177hp-15430
EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-01	4270	1695	1640	Automobile-Catalog 1997 Mitsubishi Space Runner Colours	https://www.automobile-catalog.com/car/1997/1971500/mitsubishi_space_runner_colours_automatic.html
EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-LOWROOF-01	4290	1695	1650	Mitsubishi Motors Space Runner 1999 factory workshop manual	https://www.manualslib.com/manual/1556151/Mitsubishi-Motors-Space-Runner-1999.html
EU-MITSUBISHI-SPACE-RUNNER-II-MPV-3D-HIGHROOF-01	4290	1695	1680	Mitsubishi Motors Space Runner 1999 factory workshop manual	https://www.manualslib.com/manual/1556151/Mitsubishi-Motors-Space-Runner-1999.html
EU-MITSUBISHI-SPACE-RUNNER-I-MPV-4D-02	4270	1695	1665	Automobile-Catalog 1997 Mitsubishi Space Runner 4x4 Cool; Auto-Data Mitsubishi Space Runner 2.0 16V	https://www.automobile-catalog.com/car/1997/1971545/mitsubishi_space_runner_4x4_cool.html; https://www.auto-data.net/en/mitsubishi-space-runner-n1-w-n2-w-2.0-16v-133hp-15540
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-LOWROOF-01	4030	1695	1515	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-NOMOULDING-HIGHROOF-01	4030	1695	1555	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-LOWROOF-01	4030	1700	1515	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-EARLY-SIDEMOULDING-HIGHROOF-01	4030	1700	1555	Mitsubishi Motors Space Star 1999 factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html?page=18
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-LOWROOF-01	4030	1715	1515	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-PREFL-HIGHROOF-01	4030	1715	1555	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-LOWROOF-01	4050	1715	1515	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-I-MPV-5D-FACELIFT-HIGHROOF-01	4050	1715	1555	Mitsubishi Motors Space Star factory workshop manual	https://www.manualslib.com/manual/2100615/Mitsubishi-Space-Star.html
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-PREFL-01	3710	1665	1490	Auto-Data Mitsubishi Space Star 1.2 2012	https://www.auto-data.net/en/mitsubishi-space-star-2012-1.2-80hp-19774
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2015-01	3795	1665	1505	Mitsubishi Motors Space Star 2016 Ireland brochure	https://autocatalogarchive.com/wp-content/uploads/2018/06/Mitsubishi-Space-Star-2016-IE.pdf
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-5D-FACELIFT-2019-01	3845	1665	1505	Mitsubishi Motors Space Star 2020 Czech brochure	https://autocatalogarchive.com/wp-content/uploads/2021/09/Mitsubishi-Space-Star-2020-CZ.pdf
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-LOWROOF-01	4600	1775	1650	Carfolio 2002 Mitsubishi Space Wagon 2000 GLX	https://www.carfolio.com/mitsubishi-space-wagon-2000-glx-97625
EU-MITSUBISHI-SPACE-WAGON-III-MPV-5D-HIGHROOF-01	4600	1775	1690	Auto-Data Mitsubishi Space Wagon III 2.0 i 16V	https://www.auto-data.net/en/mitsubishi-space-wagon-iii-2.0-i-16v-133hp-15589
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-FWD-01	4295	1640	1525	Automobile-Catalog 1991 Space Wagon 1800 TD GLX; Automobile-Catalog 1989 Space Wagon 2000 GLXi	https://www.automobile-catalog.com/car/1991/1928780/mitsubishi_space_wagon_1800_td_glx.html; https://www.automobile-catalog.com/car/1989/1928735/mitsubishi_space_wagon_2000_glxi_cat.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-PREFL-01	4445	1640	1580	Automobile-Catalog 1988 Space Wagon 2000 GLX 4WD	https://www.automobile-catalog.com/car/1988/51665/mitsubishi_space_wagon_2_0_4wd.html
EU-MITSUBISHI-SPACE-WAGON-I-MPV-5D-4WD-FACELIFT-01	4445	1640	1575	Automobile-Catalog 1990 Space Wagon 2000 GLXi 4WD	https://www.automobile-catalog.com/car/1990/1928825/mitsubishi_space_wagon_2000_glxi_4wd.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_11401-11500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://car.avtoelektronika63.ru/originalnye-zapchasti-mitsubishi-pajero/ "https://car.avtoelektronika63.ru/originalnye-zapchasti-mitsubishi-pajero/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2473 行）
- 累计尺寸组：dimension_groups_final.tsv（722 行）

