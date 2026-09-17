# 任务：all 第 2501-2600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0026__9c49d03f


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2501-2600 行

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
all 第 2501-2600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920
EU-FORD-FOCUS-III-FACELIFT-HATCHBACK-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-FACELIFT-SEDAN-4D-01	4534	1823	1484
EU-FORD-FOCUS-III-FACELIFT-WAGON-5D-01	4556	1823	1505
EU-FORD-FOCUS-IV-C519-HATCHBACK-5D-01	4378	1825	1471
EU-FORD-FOCUS-IV-C519-WAGON-FACELIFT-01	4672	1825	1497
EU-FORD-FOCUS-IV-C519-WAGON-PREFL-01	4668	1825	1481
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-01	4822	1943	1781
EU-LAND-ROVER-DISCOVERY-I-SUV-01	4521	1793	1928
EU-LAND-ROVER-DISCOVERY-III-L319-VAN-01	4835	1915	1887
EU-LAND-ROVER-DISCOVERY-IV-L319-VAN-01	4829	1915	1887
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-AMG-GT-R190-S-ROADSTER-01	4551	1939	1260
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-PREFL-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-PREFL-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	138	188	Mar 2018	-	2024-03-01	132098
Bentley	Continental	6.0 AWD	Coupe	Allrad	Benzin	434	590	May 2015	Jul 2018	2024-03-01	132107
Bentley	Continental	6.0 Supersports AWD	Coupe	Allrad	Benzin	522	710	Jan 2017	Jul 2018	2024-03-01	132108
Mercedes-benz	A-Klasse	A 220	Schrägheck	Frontantrieb	Benzin	140	190	Jul 2018	-	2024-03-01	132123
Land Rover	Discovery i	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	84	114	Nov 1989	Sep 1990	2024-03-01	132135
Citroën	C3 aircross i	1.5 Bluehdi 100	SUV	Frontantrieb	Diesel	75	102	Aug 2018	-	2025-11-01	132139
Peugeot	5008	1.6 Puretech 180	Großraumlimousine	Frontantrieb	Benzin	133	181	Jul 2018	-	2024-03-01	132146
Peugeot	3008 ii	1.6 Puretech 180	SUV	Frontantrieb	Benzin	133	181	Jul 2018	-	2024-11-01	132147
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	135	184	Jun 2018	-	2024-03-01	132149
Renault	Zoe	ZOE	Schrägheck	Frontantrieb	Elektro	80	109	Aug 2018	-	2024-03-01	132150
Audi	Q8	50 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	210	286	Jul 2018	-	2024-03-01	132151
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	121	165	Jun 2018	-	2024-03-01	132152
BMW	X3	Sdrive 18 D	SUV	Heckantrieb	Diesel	110	150	Apr 2018	Jun 2020	2024-03-01	132153
BMW	X3	Sdrive 18 D	SUV	Heckantrieb	Diesel	100	136	Apr 2018	Jun 2020	2024-03-01	132155
Citroën	Berlingo	1.5 Bluehdi 130	Großraumlimousine	Frontantrieb	Diesel	96	131	Jun 2018	-	2024-03-01	132156
Citroën	Berlingo	1.5 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	75	102	Jun 2018	-	2024-03-01	132157
Citroën	Berlingo	1.2 Puretech 110	Großraumlimousine	Frontantrieb	Benzin	81	110	Jun 2018	-	2024-03-01	132158
Citroën	Spacetourer	1.5 Bluehdi 100	Bus	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	132159
Toyota	Proace verso	1.5 D4D	Bus	Frontantrieb	Diesel	75	102	Jun 2018	Apr 2025	2026-01-01	132160
Renault	Kadjar	1.3 TCE 140	SUV	Frontantrieb	Benzin	103	140	Aug 2018	-	2024-03-01	132161
Renault	Kadjar	1.5 Blue DCI 115	SUV	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	132162
Citroën	Spacetourer	1.5 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Jun 2018	Apr 2025	2026-01-01	132163
Toyota	Proace verso	1.5 D4D	Bus	Frontantrieb	Diesel	88	120	Jun 2018	Apr 2025	2026-01-01	132164
BMW	X3	Xdrive 25 D	SUV	Allrad	Diesel	155	211	Apr 2018	-	2024-03-01	132165
BMW	X3	Xdrive 30 D	SUV	Allrad	Diesel	183	249	Dec 2017	Jun 2020	2024-03-01	132166
VW	Passat b1	1.6	Stufenheck	Frontantrieb	Benzin	55	75	May 1973	Jul 1977	2024-03-01	132176
BMW	X4	Xdrive 20 D	SUV	Allrad	Diesel	120	163	Apr 2018	Mar 2020	2024-03-01	132177
Mercedes-benz	Amg gt	63 4-matic+	Coupe	Allrad	Benzin	430	585	Jul 2018	-	2024-03-01	132178
BMW	X4	Xdrive 25 D	SUV	Allrad	Diesel	155	211	Apr 2018	-	2024-03-01	132179
Mercedes-benz	Amg gt	63 S 4-matic+	Coupe	Allrad	Benzin	470	639	Jul 2018	Jun 2021	2024-03-01	132180
Opel	Grandland	1.5 Turbo D	SUV	Frontantrieb	Diesel	75	102	Jun 2018	Jul 2021	2025-02-03	132183
Opel	Crossland x /	1.5 Turbo D	SUV	Frontantrieb	Diesel	75	102	Jun 2018	-	2024-03-01	132184
Opel	Insignia b grand sport	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	147	200	Jun 2018	-	2024-03-01	132189
Pagani	Zonda roadster	S 7.3	Cabriolet	Heckantrieb	Benzin	408	555	Jun 2003	May 2005	2024-03-01	132190
Opel	Insignia b sports tourer	1.6 Turbo	Kombi	Frontantrieb	Benzin	147	200	Jun 2018	-	2024-03-01	132191
Opel	Astra k	1.0 Turbo	Schrägheck	Frontantrieb	Benzin	66	90	Jun 2018	Aug 2019	2025-12-01	132193
Opel	Astra k sports tourer	1.0 Turbo	Kombi	Frontantrieb	Benzin	66	90	Jun 2018	Aug 2019	2025-12-01	132194
JAC	E-S2	EV	SUV	Frontantrieb	Elektro	85	116	Jun 2022	-	2026-05-01	132213
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	190	258	May 2018	May 2022	2024-03-01	132224
Seat	Ibiza ii	1.8 T 20V Cupra R	Schrägheck	Frontantrieb	Benzin	132	180	Jul 2000	Feb 2002	2024-03-01	132258
Suzuki	Alto k10	1	Schrägheck	Frontantrieb	Benzin	50	68	Oct 2012	Nov 2014	2024-03-01	132259
Jeep	Grand cherokee iv	6.2 I V8 4X4	SUV	Allrad	Benzin	522	710	Sep 2017	-	2024-03-01	132266
VW	Atlas	2.0 TSI 4motion	SUV	Allrad	Benzin	162	220	Dec 2017	-	2024-03-01	132274
Mercedes-benz	Cls	CLS 350 D	Coupe	Heckantrieb	Diesel	210	286	Aug 2018	-	2024-03-01	132276
Mercedes-benz	Cls	CLS 350 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	220	299	Aug 2018	-	2024-03-01	132277
VW	Golf iii van	1.4	Kasten/Schrägheck	Frontantrieb	Benzin	44	60	Aug 1991	May 1996	2024-03-01	132282
VW	Polo	1.9 SDI	Kasten/Kombi	Frontantrieb	Diesel	47	64	Dec 1995	Aug 1999	2024-03-01	132285
VW	Polo	1.7 SDI	Kasten/Kombi	Frontantrieb	Diesel	44	60	Aug 1997	Dec 1999	2024-03-01	132286
VW	Polo	1.4	Kasten/Kombi	Frontantrieb	Benzin	44	60	Aug 1997	Dec 1999	2024-03-01	132287
VW	Polo	1.4	Kasten/Kombi	Frontantrieb	Benzin	55	75	Jun 2000	Sep 2001	2024-03-01	132288
Land Rover	90	2.5 D 4X4	Geländewagen geschlossen	Allrad	Diesel	51	69	Sep 1985	Aug 1990	2024-03-01	132291
Lynk & CO	1	Phev	SUV	Frontantrieb	Benzin/Elektro	192	261	Jul 2018	-	2024-03-01	132297
Citroën	Berlingo	1.5 Bluehdi 75	Großraumlimousine	Frontantrieb	Diesel	56	76	Jun 2018	-	2024-03-01	132298
Audi	Q8	45 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	170	231	Jul 2018	-	2024-03-01	132299
Audi	Q8	SQ8 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	320	435	May 2018	-	2024-03-01	132301
Audi	Q8	55 Tfsi Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	250	340	Feb 2018	-	2024-03-01	132302
Toyota	Yaris	1	Schrägheck	Frontantrieb	Benzin	53	72	Jun 2018	Jun 2020	2024-05-01	132309
Mercedes-benz	E-Klasse	E 350 D	Stufenheck	Heckantrieb	Diesel	210	286	Aug 2018	Jun 2020	2024-03-01	132313
Land Rover	110/127	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	85	116	Jan 1984	Sep 1990	2024-03-01	132314
Mercedes-benz	E-Klasse	E 350 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	220	299	Aug 2018	Oct 2023	2024-03-01	132315
Mercedes-benz	E-Klasse	E 450 4-matic	Stufenheck	Allrad	Benzin	270	367	Aug 2018	Jun 2020	2024-03-01	132316
Mercedes-benz	E-Klasse	E 450 4-matic	Kombi	Allrad	Benzin	270	367	Aug 2018	Jun 2020	2024-03-01	132319
Audi	A6 c8	45 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	170	231	Jul 2018	-	2024-03-01	132320
Audi	A6 c8	50 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	210	286	Feb 2018	-	2024-03-01	132321
Mercedes-benz	E-Klasse	E 350 D	Kombi	Heckantrieb	Diesel	210	286	Aug 2018	Jun 2020	2024-03-01	132322
Audi	A6 c8	55 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	250	340	Feb 2018	-	2024-03-01	132323
Audi	A6 c8 avant	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	170	231	May 2018	-	2024-03-01	132324
Mercedes-benz	E-Klasse	E 400 D 4-matic	Kombi	Allrad	Diesel	250	340	Aug 2018	Oct 2023	2024-03-01	132325
Audi	A6 c8 avant	50 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	210	286	May 2018	-	2024-03-01	132326
Audi	A6 c8 avant	55 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	250	340	May 2018	-	2024-03-01	132327
Audi	A7 sportback	45 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	170	231	Jun 2018	-	2024-03-01	132328
Audi	A6 c8	40 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	150	204	Jul 2018	-	2024-03-01	132329
Audi	A6 c8 avant	40 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	150	204	May 2018	-	2024-03-01	132330
Jeep	Renegade	1.0 T-gdi	SUV	Frontantrieb	Benzin	88	120	Aug 2018	-	2024-03-01	132331
Jeep	Renegade	1.3 T-gdi	SUV	Frontantrieb	Benzin	110	150	Aug 2018	-	2024-03-01	132332
Jeep	Renegade	1.3 T-gdi 4X4	SUV	Allrad	Benzin	132	180	Aug 2018	-	2024-03-01	132333
Audi	A6 c8 avant	40 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	150	204	Jul 2018	-	2024-03-01	132334
Ford	Focus i	1.6	Kasten/Kombi	Frontantrieb	Benzin	74	101	Apr 1999	Mar 2005	2024-03-01	132338
Ford	Focus i	1.8	Kasten/Kombi	Frontantrieb	Benzin	85	116	Apr 1999	Mar 2005	2024-03-01	132339
Land Rover	90	2.5 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	63	86	Sep 1986	Aug 1990	2024-03-01	132340
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	132341
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	85	116	Aug 2018	-	2024-03-01	132342
Ford	Focus i	1.8 Tddi	Kasten/Kombi	Frontantrieb	Diesel	66	90	Aug 1998	Mar 2005	2024-03-01	132343
Ford	Focus i	1.8 Tdci	Kasten/Kombi	Frontantrieb	Diesel	74	101	Aug 2002	Mar 2005	2024-03-01	132344
Ford	Focus i	1.8 Tdci	Kasten/Kombi	Frontantrieb	Diesel	85	116	Aug 2001	Mar 2005	2024-03-01	132345
Ford	Transit courier b460	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	74	100	Apr 2018	Dec 2023	2024-05-01	132356
Ford	Tourneo courier b460	1.5 Ecoblue	Großraumlimousine	Frontantrieb	Diesel	74	100	Apr 2018	Dec 2023	2024-05-01	132357
Nissan	Vanette	2.0 D	Bus	Heckantrieb	Diesel	49	67	Oct 1986	Dec 1995	2024-03-01	132358
Ford	Transit courier b460	1.5 Ecoblue	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	100	Apr 2018	Dec 2023	2024-05-01	132360
Streetscooter	Work	Elektro	Kasten	Frontantrieb	Elektro	48	65	Jan 2015	Jul 2022	2024-03-01	132363
Audi	A6 c8 avant	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	155	211	Jul 2018	-	2024-03-01	132365
Streetscooter	Work	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	48	65	Jan 2015	Jul 2022	2024-03-01	132366
Audi	A6 c8	45 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	155	211	Jul 2018	-	2024-03-01	132367
Streetscooter	Work	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	30	41	Jan 2015	Jul 2022	2024-03-01	132368
VW	Crafter	E-crafter FWD	Kasten	Frontantrieb	Elektro	100	136	Jul 2018	-	2025-04-01	132370
Renault	Master iii	Z.e.	Kasten	Frontantrieb	Elektro	57	77	Mar 2018	Dec 2024	2026-03-01	132371
Renault	Master iii	Z.e.	Pritsche/Fahrgestell	Frontantrieb	Elektro	57	77	Mar 2018	Dec 2024	2026-03-01	132372
Mercedes-benz	E-Klasse	E 400 D 4-matic	Coupe	Allrad	Diesel	250	340	Aug 2018	-	2024-03-01	132374
Mercedes-benz	E-Klasse	E 400 D 4-matic	Cabriolet	Allrad	Diesel	250	340	Aug 2018	-	2024-03-01	132376
Mercedes-benz	E-Klasse	E 450 4-matic	Coupe	Allrad	Benzin	270	367	Aug 2018	-	2024-03-01	132377


--- Round 1 / 首次发送 ---
## 更新点

* 完成 23 个 Ktype 的物理车身映射，其中 18 个直接关联已有缓存尺寸组，未重复抓取尺寸或来源。
* 首次闭合 3 个新尺寸组：

  * Mazda CX-5 II KF：4550 × 1840 × 1675 mm，资料明确车宽不含后视镜。([ND Media Gallery][1])
  * Citroën C3 Aircross I Phase I：4154 × 1756 × 1637 mm，使用 2018 年原厂车型手册存档。([汽车目录档案][2])
  * Renault Zoe I X10：4084 × 1730 × 1562 mm，官方尺寸图同时列出 1730 mm 车身宽和 1945 mm 含后视镜宽。
* Peugeot 5008 的输入车身标签虽为 `Großraumlimousine`，本轮按 5008 II 的实际 SUV 车身边界映射。
* 当前未对 Bentley、PSA 多长度厢式车、老款 Land Rover、Audi A6/Q8 和 Mercedes-Benz E-Class 等尚待聚类车型创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 READY：23
* 尚待处理：77
* 当前引用的已确认尺寸组：16
* 本轮首次新建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132098	132098	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132123	132123	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
132139	132139	SUV	C3 Aircross I Phase I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH		READY
132146	132146	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入车身标签为Großraumlimousine，车型边界按5008 II SUV。	READY
132147	132147	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
132149	132149	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132150	132150	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-01	HIGH		READY
132152	132152	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132153	132153	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132155	132155	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132165	132165	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132166	132166	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132177	132177	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132179	132179	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132183	132183	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH		READY
132184	132184	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
132193	132193	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
132194	132194	Wagon	Astra K Sports Tourer	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
132224	132224	Pickup	Amarok I Facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	3.0 TDI 258仅对应双排驾驶室外廓。	READY
132276	132276	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	四门轿跑车身。	READY
132277	132277	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	四门轿跑车身。	READY
132341	132341	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
132370	132370	Van	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	e-Crafter量产车身对应L3H3。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-CX-5-II-KF-SUV-01	4550	1840	1675	Mazda UK 2020 CX-5 Price and Specification Guide	https://nd-mediagallery2-public-production.s3.amazonaws.com/5763e6971f63626d513e6a8ce49709a9/2020_mazda_cx_5_price_and_spec_apr_20.pdf
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637	Citroën C3 Aircross 2018 UK official brochure (archived copy)	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-C3-Aircross-2018-UK.pdf
EU-RENAULT-ZOE-I-X10-HATCHBACK-01	4084	1730	1562	Renault ZOE Press Kit July 2017	https://www.press.renault.co.uk/assets/documents/original/10706-RenaultZOEPressKitJuly2017.pdf
```

## 下一步优先处理

1. 集中处理 Citroën Berlingo、SpaceTourer、Toyota Proace Verso 和 Renault Master Z.E. 的长度、车顶及驾驶室分支，优先复用已有 M、XL、Compact、L2、L3 尺寸组。
2. 闭合 Bentley Continental GT W12/Supersports Coupe、Audi Q8/SQ8、Mercedes-AMG GT X290 和 Opel Insignia B 的新尺寸组。
3. 核对 Land Rover Discovery I、90、110/127 的门数及 SWB/LWB 派生边界。

推进信号：CONTINUE

[1]: https://nd-mediagallery2-public-production.s3.amazonaws.com/5763e6971f63626d513e6a8ce49709a9/2020_mazda_cx_5_price_and_spec_apr_20.pdf?utm_source=chatgpt.com "2020 MAZDA CX-5"
[2]: https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-C3-Aircross-2018-UK.pdf?utm_source=chatgpt.com "NEW CITROËN C3 AIRCROSS COMPACT SUV"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新建 Audi Q8、Audi A6 C8 Sedan、Audi A7 II Sportback 三个尺寸组。
* 新建 Mercedes-Benz E-Class W213 Sedan、S213 Wagon 两个尺寸组，官方尺寸图明确区分车身宽度 1852 mm 与含后视镜宽度 2065 mm。
* Jeep Grand Cherokee Trackhawk 未复用普通 WK2 尺寸组，按其独立低车身外廓新建尺寸组。([Stellantis Media][1])
* Mercedes-Benz C238 Coupe、A238 Convertible 直接复用既有完整尺寸组，未重复抓取。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：42
* PENDING 映射：58
* 已确认尺寸组：24
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132151	132151	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132266	132266	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-TRACKHAWK-SUV-01	HIGH		READY
132299	132299	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132302	132302	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132313	132313	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132315	132315	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132316	132316	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132319	132319	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132320	132320	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132321	132321	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132322	132322	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132323	132323	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132325	132325	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132328	132328	Hatchback	A7 II	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH		READY
132329	132329	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132367	132367	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132374	132374	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
132376	132376	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH		READY
132377	132377	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705	Audi MediaCenter The new Audi Q8 official press information	https://www.audi-mediacenter.com/system/production/uploaded_files/12201/file/4809115148b90f8e62020bcafe6c2fb60cf1e71f/en_Press_Information_Audi_Q8.pdf?1531131786=&disposition=attachment
EU-JEEP-GRAND-CHEROKEE-IV-WK2-TRACKHAWK-SUV-01	4822	1943	1724	2018 Jeep Grand Cherokee Trackhawk official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2018_JP_GrCherokee_Trackhawk_SP10kge6g0tjfo0bkv87ru3cehu4.pdf
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Mercedes-Benz E-Class Saloon and Estate official brochure archived copy	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	Mercedes-Benz E-Class Saloon and Estate official brochure archived copy	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi MediaCenter The new Audi A6 official model information	https://www.audi-mediacenter.com/en/the-audi-a6-until-2025-the-car-of-many-talents-in-the-business-class-10240/design-10256
EU-AUDI-A7-II-4KA-HATCHBACK-01	4969	1908	1422	Audi MediaCenter Audi A7 Sportback official model information	https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/design-9836
```

## 下一步优先处理

1. 闭合 Audi A6 C8 Avant 的标准车身高度边界，再批量关联全部 Avant Ktype。
2. 拆分 Citroën SpaceTourer、Toyota Proace Verso 的 Compact、Medium、Long 分支，优先关联已有尺寸组。
3. 处理 Citroën Berlingo K9 的 M、XL 分支以及 Renault Master Z.E. 的 Van、Chassis 配置。
4. 集中处理 Bentley Continental Coupe、Mercedes-AMG GT 4-Door、Opel Insignia B 和老款 Land Rover。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/me-en/jeep-archive/press/707-horsepower-2018-jeep-grand-cherokee-trackhawk-the-most-powerful-and-quickest-suv-ever-1?utm_source=chatgpt.com "Middle East - 707-horsepower 2018 Jeep® Grand ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 闭合 Audi A6 C8 Avant 车身组，6 个 Ktype 共用 `4A5` 标准旅行车外廓 4939 × 1886 × 1467 mm；官方尺寸图同时列出不含后视镜宽度 1886 mm、含后视镜宽度 2110 mm。([audi.com][1])
* Citroën 2018 年官方配置表确认：1.5 BlueHDi 100 对应 XS、M；1.5 BlueHDi 120 对应 XS、M、XL。三个长度分别为 4606、4956、5306 mm，宽度均为不含后视镜 1920 mm。([Stellantis Media][2])
* Toyota Proace Verso 1.5 D-4D 102 拆分 Compact、Medium；1.5 D-4D 120 拆分 Compact、Medium、Long。2018 年配置表支持这些发动机与长度分支，Toyota 官方资料给出三种车身尺寸。([Mengelers][3])
* Citroën SpaceTourer 和 Toyota Proace Verso 当前车型尺寸与已有后期尺寸组不同，因此新建 `PREFL` 组，没有覆盖或改写已有组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：52
* READY 映射行：58
* PENDING Ktype：48
* 已确认尺寸组：31
* 本轮新增尺寸组：7
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132159_xs	132159	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS物理外廓。	READY
132159_m	132159	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M物理外廓。	READY
132160_compact	132160	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact物理外廓。	READY
132160_medium	132160	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium物理外廓。	READY
132163_xs	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS物理外廓。	READY
132163_m	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M物理外廓。	READY
132163_xl	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL物理外廓。	READY
132164_compact	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact物理外廓。	READY
132164_medium	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium物理外廓。	READY
132164_long	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	HIGH	Long物理外廓。	READY
132324	132324	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132326	132326	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132327	132327	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132330	132330	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132334	132334	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132365	132365	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	Audi A6 Avant official dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-a6-avant-1400/download
```

## 5. 下一步优先处理

1. 批量闭合 Citroën Berlingo K9 的 M、XL 分支。
2. 处理 Renault Master Z.E. Van 与 Chassis 的长度、车顶及驾驶室组合。
3. 集中处理 Ford Focus I Van、Transit/Tourneo Courier 和 Hyundai i30 Wagon。
4. 再处理 Bentley Continental、Mercedes-AMG GT X290、Opel Insignia B 与老款 Land Rover 的独立外廓。

推进信号：CONTINUE

[1]: https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-a6-avant-1400/download "A6 Avant MA Abmessungen 0523"
[2]: https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF "Copy of 02 2018 SPACETOURER (002).xlsx"
[3]: https://www.mengelers.nl/fileadmin/images/toyota/Brochures/ProAce_Verso_Prijslijst_2018.pdf?utm_source=chatgpt.com "P | Prijzen PROACE SHUTTLE & PROACE VERSO rijzen PROACE SHUTTLE & PROACE VERSO Prijzen PROACE SHUTTLE & PROACE VERSO 1 augustus 2018 1 augustus 2018 |  |  |  |  |  |  |  |  |  |"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Citroën Berlingo III K9 乘用版尺寸分支：BlueHDi 130、BlueHDi 100 和 PureTech 110 拆分为 M、XL；BlueHDi 75 仅关联 M。官方资料确认长度配置及不含后视镜宽度。([Stellantis Media][1])
* 闭合 Renault Kadjar I Facelift，TCe 140 与 Blue dCi 115 共用同一物理外廓。
* Audi SQ8 TDI 使用独立于普通 Q8 的尺寸组，不覆盖既有 Q8 组。
* 闭合 Hyundai i30 III PD Wagon 尺寸组。([现代新闻][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：60
* READY 映射行：69
* PENDING Ktype：40
* 已确认尺寸组：36
* 本轮新增尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132156_m	132156	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132156_xl	132156	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132157_m	132157	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132157_xl	132157	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132158_m	132158	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132158_xl	132158	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132161	132161	SUV	Kadjar I Facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132162	132162	SUV	Kadjar I Facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132298_m	132298	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132301	132301	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SQ8-SUV-01	HIGH		READY
132342	132342	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën Berlingo official technical specifications	https://www.citroen.ua/content/dam/citroen/ukraine/files/ttx/ttx-k9berlingo-vp.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën Berlingo official technical specifications	https://www.citroen.ua/content/dam/citroen/ukraine/files/ttx/ttx-k9berlingo-vp.pdf
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613	Renault KADJAR official eBrochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/car-ebrochures/KADJAR-eBrochure.pdf
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708	Audi SQ8 TDI official technical data	https://press.audi.co.uk/assets/documents/original/2941-AudiSQ8TDITechnicalDataUKOctober2019.pdf
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Hyundai i30 official technical specifications	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/i30_data.preliminary.pdf
```

## 下一步优先处理

1. 闭合 Jeep Renegade 改款版前驱、四驱高度及外廓分支。
2. 集中处理 Ford Transit Courier、Tourneo Courier 与 Focus I Van。
3. 处理 Renault Master Z.E. Van、Chassis 的长度、车顶和驾驶室组合，优先复用已有组。
4. 继续处理 Bentley Continental Coupe、Mercedes-AMG GT、Opel Insignia B 与老款 Land Rover。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/citroen/press/citroen-uk-opens-order-books-for-third-generation-leisure-activity-vehicle-new-citroen-berlingo "CITROËN UK OPENS ORDER BOOKS FOR THIRD-GENERATION LEISURE ACTIVITY VEHICLE – NEW CITROËN BERLINGO | Citroën | Stellantis Media"
[2]: https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/i30_data.preliminary.pdf "i30 data.preliminary"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1. 更新点

* 闭合 Opel Insignia B 两种物理外廓：Grand Sport 为 4897 × 1863 × 1455 mm，Sports Tourer 为 4986 × 1863 × 1514 mm；官方规格图明确 1863 mm 为不含后视镜宽度。
* 闭合 Ford Tourneo Courier B460 五门 MPV：4157 × 1764 × 1741 mm；官方资料明确 1764 mm 为不含后视镜宽度，1741 mm 为不含车顶行李架高度。
* Jeep Renegade 1.0 120 和 1.3 150 已确认均为前驱，官方表列出 4236 × 1805 × 1667 mm，但宽度栏未明确标注是否不含后视镜，本轮不创建尺寸组，继续保留待闭合。([Stellantis Media][1])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：63
* READY 映射行：72
* PENDING Ktype：37
* 已确认尺寸组：39
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132189	132189	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH		READY
132191	132191	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH		READY
132357	132357	MPV	Tourneo Courier I	B460	5	EU-FORD-TOURNEO-COURIER-B460-MPV-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall Insignia Price/Specification Guide MY2018.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/GML_10970043_Insignia_Spec_PG_9_May_2018-1525794507.pdf
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514	Vauxhall Insignia Price/Specification Guide MY2018.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/GML_10970043_Insignia_Spec_PG_9_May_2018-1525794507.pdf
EU-FORD-TOURNEO-COURIER-B460-MPV-01	4157	1764	1741	Ford Tourneo Courier official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Tourneo-Courier.pdf
```

## 5. 下一步优先处理

1. 闭合 Ford Transit Courier B460 的乘用、厢式车边界。
2. 批量处理 Bentley Continental GT W12 与 Supersports Coupe。
3. 处理 Renault Master Z.E. Van、Chassis 的长度和车顶分支。
4. 继续核对 Jeep Renegade 前驱宽度口径及四驱高度分支。
5. 集中处理老款 Land Rover 90、110/127、Discovery I。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/em-en/jeep/press/new-2019-jeep-renegade "New 2019 Jeep® Renegade | Jeep® | Stellantis Media"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 1. 更新点

* Bentley Continental GT II Facelift 6.0 W12 与既有 V8 S 组外廓一致，直接复用既有组；Supersports 因专属保险杠、空气动力学组件及车身高度变化独立建组。([汽车数据网][1])
* Mercedes-AMG GT 63 与 GT 63 S 均为 X290 五门四门轿跑车身，但高度分别为 1442 mm、1447 mm，分别建组。([汽车目录][2])
* Jeep Renegade Facelift 前驱 1.0/1.3 共用 1667 mm 高度组；1.3 4×4 高度为 1684 mm，独立建组。来源同时列出车身宽、折叠后视镜宽和含镜宽，确认 1805 mm 为不含后视镜宽度。([汽车数据网][3])
* Ford Transit Courier B460 的 Kombi 与厢式车长度、宽度相同，但标准高度不同；Ktype `132360` 拆为 Kombi、Van 两条物理分支。([福特媒体][4])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：72
* READY 映射行：82
* PENDING Ktype：28
* 已确认尺寸组：46
* 本轮新增尺寸组：7
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132107	132107	Coupe	Continental GT II Facelift	3W	2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
132108	132108	Coupe	Continental GT II Facelift	3W	2	EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	HIGH	Supersports专属外部套件物理外廓。	READY
132178	132178	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	HIGH	GT 63物理外廓。	READY
132180	132180	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	HIGH	GT 63 S物理外廓。	READY
132331	132331	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	HIGH	前驱物理外廓。	READY
132332	132332	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	HIGH	前驱物理外廓。	READY
132333	132333	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	HIGH	四驱较高物理外廓。	READY
132356	132356	MPV	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	HIGH	Kombi乘用物理外廓。	READY
132360_kombi	132360	MPV	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	HIGH	Kombi物理分支。	READY
132360_van	132360	Van	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	厢式车物理分支。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	4818	1948	1391	Bentley Heritage Collection 2017 Continental Supersports	https://www.bentleymedia.com/it/heritage-collection/2017-continental-supersports-da17uwr
EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	5054	1953	1442	Automobile-Catalog 2019 Mercedes-AMG GT 63 4MATIC+	https://www.automobile-catalog.com/car/2019/2739470/mercedes-amg_gt_63_4matic_plus.html
EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	5054	1953	1447	Automobile-Catalog 2018 Mercedes-AMG GT 63 S 4MATIC+	https://www.automobile-catalog.com/car/2018/2739485/mercedes-amg_gt_63_s_4matic_plus.html
EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	4236	1805	1667	Auto-Data Jeep Renegade Facelift 1.0 T-GDI; Auto-Data Jeep Renegade Facelift 1.3 Turbo DDCT	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.0-t-gdi-120hp-35848;https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.3-turbo-150hp-ddct-39051
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684	Auto-Data Jeep Renegade Facelift 1.3 T-GDI 4x4	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.3-t-gdi-180hp-4x4-automatic-35849
EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	4157	1764	1747	Ford Transit Courier official technical specifications; Coches.net Transit Courier Kombi 2018 specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Courier/TransitCourier_Specifications_EU.pdf;https://www.coches.net/fichas_tecnicas/ford/transit_courier/furgoneta/4-puertas/kombi_15_tdci_71kw_trend_100cv_diesel/74942/773679520190101/
EU-FORD-TRANSIT-COURIER-B460-VAN-01	4157	1764	1770	Ford Transit Courier official technical specifications; ADAC Transit Courier Kastenwagen specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Courier/TransitCourier_Specifications_EU.pdf;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/transit-courier/1generation-facelift/307340/
```

## 5. 下一步优先处理

1. 批量闭合 Ford Focus I 商用旅行车的 5 个 Ktype。
2. 处理 VW Golf III Van、Polo Van 的车身代码和代际分支。
3. 闭合 Toyota Yaris III Facelift、VW Atlas、Lynk & Co 01。
4. 继续处理 Renault Master Z.E.、StreetScooter Work 和老款 Land Rover 多车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bentley-continental-gt-ii-facelift-2015-6.0-w12-590hp-awd-automatic-22838?utm_source=chatgpt.com "Bentley Continental GT II (facelift 2015) 6.0 W12 (590 Hp) AWD Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2019/2739470/mercedes-amg_gt_63_4matic_plus.html?utm_source=chatgpt.com "2019 Mercedes-AMG GT 63 4MATIC+ 4-Door Coupe Specs Review (430 kW / 585 PS / 577 hp) (for Europe )"
[3]: https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.0-t-gdi-120hp-35848 "Jeep Renegade (facelift 2018) 1.0 T-GDI (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Courier/TransitCourier_Specifications_EU.pdf "All-New Ford Transit Courier Delivers Best-in-Class Fuel Economy and Load-Carrying Ability"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 1. 更新点

* 闭合 Pagani Zonda Roadster S 7.3：官方技术页对应 555 hp 版本，确认独立敞篷车外廓。([帕加尼][1])
* 闭合 JAC E-S2：采用 JAC 官方规格中的 4135 × 1750 × 1560 mm 车身尺寸。([jacen.jac.com.cn][2])
* 闭合 VW Golf III 商用厢式掀背车：按 `1H` 三门 Golf III 基础车身建立尺寸组；未与 Variant、Caddy 等不同外廓混用。([volkswagen-newsroom.com][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：75
* READY 映射行：85
* PENDING Ktype：25
* 已确认尺寸组：49
* 本轮新增尺寸组：3
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132190	132190	Convertible	Zonda Roadster S		2	EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	HIGH		READY
132213	132213	SUV	E-S2		5	EU-JAC-E-S2-ELECTRIC-SUV-01	HIGH		READY
132282	132282	Van	Golf III	1H	3	EU-VW-GOLF-III-1H-PANEL-VAN-01	MEDIUM	三门厢式掀背物理外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	4395	2055	1151	Pagani Zonda Roadster official technical data	https://www.pagani.com/it/zonda-roadster/
EU-JAC-E-S2-ELECTRIC-SUV-01	4135	1750	1560	JAC e-S2 official specifications	https://jacen.jac.com.cn/models/e-s2/
EU-VW-GOLF-III-1H-PANEL-VAN-01	4020	1695	1425	Volkswagen Classic Golf III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
```

## 5. 下一步优先处理

1. 批量闭合 Ford Focus I 商用旅行车的 5 个 Ktype。
2. 确认 VW Polo 商用版对应 Hatchback、Variant 或 Caddy 的具体物理分支。
3. 处理 Renault Master Z.E. Van、Chassis 与 StreetScooter Work 多外廓组合。
4. 集中处理 Land Rover 90、110/127、Discovery I 的轴距和门数分支。

推进信号：CONTINUE

[1]: https://www.pagani.com/it/zonda-roadster/ "Zonda Roadster | Pagani"
[2]: https://jacen.jac.com.cn/models/e-s2/?utm_source=chatgpt.com "e-S2"
[3]: https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474?utm_source=chatgpt.com "Vehicle data Golf III profile"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 1. 更新点

* 批量闭合 Ford Focus I `Kasten/Kombi (DNW)` 的 5 个 Ktype；车型目录明确其车身代码为 `DNW`，尺寸按同代 Focus Turnier 商用旅行车外廓统一为 4465 × 1702 × 1532 mm，宽度不含后视镜。([AIC德国汽车零部件][1])
* 闭合 Toyota Yaris III 第二次改款 1.0 VVT-i；官方技术规格确认 3945 × 1695 × 1510 mm。因普通版与已有 GRMN 组的外部版本边界不同，本轮独立建组。
* 闭合 Lynk & Co 01 首代 PHEV；输入功率按该数据库的 256 hp 标法存在换算差异，但生产起始月、PHEV、前驱和车身边界一致，尺寸为 4512 × 1857 × 1673 mm。([汽车数据网][2])
* 闭合 Suzuki Alto 欧洲版 K10B 1.0：3500 × 1600 × 1470 mm，宽度不含后视镜。([汽车目录][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* READY 映射行：93
* PENDING Ktype：17
* 已确认尺寸组：53
* 本轮新增尺寸组：4
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132259	132259	Hatchback	Alto VII	GF	5	EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	HIGH		READY
132297	132297	SUV	01 I		5	EU-LYNK-CO-01-I-PHEV-SUV-01	MEDIUM	首代中国市场PHEV物理外廓。	READY
132309	132309	Hatchback	Yaris III Facelift		5	EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	HIGH	普通版外廓，独立于GRMN版本。	READY
132338	132338	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132339	132339	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132343	132343	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132344	132344	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132345	132345	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	3500	1600	1470	Automobile-Catalog 2012 Suzuki Alto 1.0 Base Europe	https://www.automobile-catalog.com/car/2012/3403685/suzuki_alto_1_0.html
EU-LYNK-CO-01-I-PHEV-SUV-01	4512	1857	1673	Auto-Data Lynk & Co 01 1.5 T3 Plug-in Hybrid 2018-2019	https://www.auto-data.net/en/lynk-co-01-1.5-t3-256hp-plug-in-hybrid-dcth-51531
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510	Toyota Yaris Generation 3 Second Minor Change official press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen3-Yaris-2nd-MC-archive-press-pack.pdf
EU-FORD-FOCUS-I-DNW-VAN-01	4465	1702	1532	AIC Germany Focus I Kasten/Kombi DNW catalogue; Automobile-Catalog Ford Focus Turnier 1.6 16V Trend	https://www.aic-germany.de/en/product-catalogue/3896;https://www.automobile-catalog.com/car/2000/955625/ford_focus_turnier_estate_1_6_16v_trend_zetec.html
```

## 5. 下一步优先处理

1. 处理 VW Polo III `Kasten/Kombi` 的 4 个 Ktype，确认其对应 Variant 商用车还是 Caddy 分支。
2. 闭合 Renault Master Z.E. Van 与 Chassis 的长度、车顶和驾驶室组合，优先复用已有 Master III 组。
3. 处理 StreetScooter Work 厢式车、底盘及平台车分支。
4. 最后集中解决 Land Rover Discovery I、90、110/127、Nissan Vanette、SEAT Ibiza Cupra R、VW Passat B1 和 VW Atlas。

推进信号：CONTINUE

[1]: https://aic-germany.straightup-webstudio.de/en/product-catalogue/5148?utm_source=chatgpt.com "Product catalogue from AIC Germany"
[2]: https://www.auto-data.net/en/lynk-co-01-1.5-t3-256hp-plug-in-hybrid-dcth-51531 "Lynk & Co 01 1.5 T3 (256 Hp) Plug-in Hybrid DCTH | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/2012/3403685/suzuki_alto_1_0.html?utm_source=chatgpt.com "2012 Suzuki Alto 1.0 Base Specs Review (50 kW / 68 PS / 67 hp) (up to June 2012 for Europe export)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 闭合 VW Polo III `Kasten/Kombi (6V5)` 四个 Ktype：前三个使用改款前商用旅行车外廓，2000 年起的 75 PS 版本使用改款后较高车身。车型代码与 Ktype 边界由零件目录确认，尺寸由 Volkswagen 历史资料及车型规格页闭合。([AIC德国汽车零部件][1])
* 闭合 VW Passat B1 Type 32、SEAT Ibiza II Facelift Cupra R 和 VW Atlas/Teramont 2.0 TSI 4Motion。Passat 1.6 对应 1975 年后的加长车身；Atlas 162 kW 四驱版本对应首代 Teramont/Atlas 外廓。([volkswagen-newsroom.com][2])
* StreetScooter Work 的厢式车、Pickup 和 Pure 底盘三种外廓已闭合；两个 `Pritsche/Fahrgestell` Ktype 均拆分为 Pickup 与 Chassis 派生行。官方技术表同时提供总宽及不含后视镜宽度，本表采用后者。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* READY 映射行：105
* PENDING Ktype：7
* 已确认尺寸组：61
* 本轮新增尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132176	132176	Sedan	Passat B1	Type 32	4	EU-VW-PASSAT-B1-TYPE32-SEDAN-01	MEDIUM	1.6版本对应1975年后加长车身边界。	READY
132258	132258	Hatchback	Ibiza II Facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-FACELIFT-CUPRA-R-HATCHBACK-01	HIGH	Cupra R三门物理外廓。	READY
132274	132274	SUV	Atlas I		5	EU-VW-ATLAS-I-SUV-01	HIGH	2.0 TSI 162kW四驱版本对应Teramont/Atlas首代外廓。	READY
132285	132285	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132286	132286	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132287	132287	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132288	132288	Van	Polo III Variant Facelift	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	HIGH	改款后较高商用旅行车外廓。	READY
132363	132363	Van	Work			EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH	Work Box厢式车外廓。	READY
132366_pickup	132366	Pickup	Work			EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pickup平台车物理分支。	READY
132366_chassis	132366	Pickup	Work			EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Pure底盘物理分支。	READY
132368_pickup	132368	Pickup	Work			EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pickup平台车物理分支。	READY
132368_chassis	132368	Pickup	Work			EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Pure底盘物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B1-TYPE32-SEDAN-01	4290	1615	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-SEAT-IBIZA-II-6K1-FACELIFT-CUPRA-R-HATCHBACK-01	3876	1640	1422	Automobile-Catalog 2000 SEAT Ibiza Cupra R	https://www.automobile-catalog.com/car/2000/3070610/seat_ibiza_cupra_r.html
EU-VW-ATLAS-I-SUV-01	5036	1989	1769	Auto-Data Volkswagen Teramont 2.0 TSI 220 4MOTION	https://www.auto-data.net/en/volkswagen-teramont-2.0-tsi-220hp-4motion-automatic-34783
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433	AIC Germany Polo Kasten/Kombi 6V5 catalogue; Auto-Data Volkswagen Polo III Variant 1.7 SDI	https://aic-germany.de/en/product-catalogue/348;https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n-1.7-sdi-60hp-8463
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459	AIC Germany Polo Kasten/Kombi 6V5 catalogue; Auto-Data Volkswagen Polo III Variant Facelift 1.4 16V	https://aic-germany.de/en/product-catalogue/348;https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n2-facelift-1999-1.4-16v-75hp-8460
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PICKUP-01	4741	1814	1859	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	4676	1796	1861	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
```

## 下一步优先处理

1. 闭合 Land Rover Discovery I 3.5、Land Rover 90 2.5 D/TD，以及 `110/127` 的轴距派生分支。
2. 闭合 Nissan Vanette C22 Bus 的普通顶、长车身边界。
3. 拆分 Renault Master Z.E. Van 的长度与车顶组合。
4. 将 Renault Master Z.E. Chassis 的 L2/L3 分支优先关联已有改款前、改款后单排驾驶室尺寸组。

推进信号：CONTINUE

[1]: https://aic-germany.de/en/product-catalogue/348?utm_source=chatgpt.com "Rolling Bearing, suspension strut mount"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535?utm_source=chatgpt.com "Vehicle data Passat B1 profile"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 1. 更新点

* `132135` 对应 1989 年首发三门 Discovery I，直接复用已有 `EU-LAND-ROVER-DISCOVERY-I-SUV-01`，不重复输出尺寸组。该动力 Ktype 的生产区间为 1989 年 11 月至 1990 年 9 月，首发阶段仅有三门车身。([AUTODOC][1])
* `132291` 与 `132340` 均确认对应 `LDV` 三门 Hard Top，普通柴油和涡轮柴油共用 3858 × 1790 × 1972 mm 外廓。([alkatreszek.hu][2])
* 闭合 Nissan Vanette II C22 2.0 D Bus，确认子代码 `ULC22` 及 4360 × 1690 × 1900 mm 外廓。([DENSO][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射行：109
* PENDING Ktype：3
* 已确认尺寸组：63
* 本轮新增尺寸组：2
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132135	132135	SUV	Discovery I	LJ	3	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	首发三门物理外廓。	READY
132291	132291	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	HIGH	三门Hard Top物理外廓。	READY
132340	132340	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	HIGH	三门Hard Top物理外廓。	READY
132358	132358	MPV	Vanette II	ULC22		EU-NISSAN-VANETTE-II-ULC22-BUS-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	3858	1790	1972	Automobile-Catalog 1985 Land-Rover 90 Hard Top 2.5 Diesel; Automobile-Catalog 1988 Land-Rover 90 Hard Top 2.5 Turbo Diesel	https://www.automobile-catalog.com/car/1985/1393730/land-rover_90_hard_top_2_5_diesel.html;https://www.automobile-catalog.com/car/1988/1394315/land-rover_90_hard_top_2_5_turbo_diesel.html
EU-NISSAN-VANETTE-II-ULC22-BUS-01	4360	1690	1900	Truck1 Nissan Vanette Bus C22 2.0 D ULC22 technical specifications	https://www.truck1.eu/blog/nissan-vanette-bus-c22-2-0-d-ulc22-67-hp-tech-specs-t34751
```

## 5. 下一步优先处理

1. 拆分并闭合 `132314` 的 Land Rover 110 与 127 物理外廓边界。
2. 拆分 `132371` Renault Master Z.E. Van 的 L1H1、L1H2、L2H2、L3H2 及改款前后边界。
3. 拆分 `132372` 的 Platform Cab、Chassis Cab、L2/L3 与改款边界，并优先复用已有 Master III 单排底盘尺寸组。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/coil-springs-10213/land-rover/discovery/discovery-i-lj-lg/132135-3-5-4x4?utm_source=chatgpt.com "Land Rover Discovery 1 3.5 4x4 Coil spring - 114 hp Petrol 84 kW 1989 - 1990 27G ▷ AUTODOC"
[2]: https://alkatreszek.hu/termekek/auto_felfuggesztes_kormanyzas/osszekoto_elemek/land_rover/90/90_i_ldv_1984_01_1990_08?utm_source=chatgpt.com "Vásároljon LAND ROVER 90 I (LDV) 1984/01 1990/08 Összekötő elemek autóalkatrészeket - Kovács"
[3]: https://www.denso-am.eu/catalog/pv/132358?utm_source=chatgpt.com "Car parts for NISSAN VANETTE Bus (C22), 2.0 D, 49kW(67ps ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2501-2600_ktype_dimension_mapping_final.tsv
- all_2501-2600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 最后 3 个 Ktype 已闭合：

  * `132314` 按 Land Rover 110 五门封闭车身落盘；`127` 的标准形态为皮卡或改装底盘，不纳入该封闭越野车 Ktype。
  * `132371` 拆分为 Master Z.E. 改款前、改款后的 8 个 Van 长度/车顶分支。
  * `132372` 拆分为 4 个 Platform Cab 分支及 2 个改款后 Chassis Cab 分支。Renault 资料明确列出 Van、Platform Cab 和 Chassis Cab 的对应组合及 2070 mm 不含后视镜宽度。
* 已完成机械检查：固定表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、所有映射引用闭合、三维与来源字段完整、无孤立尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* 最终映射行：124
* PENDING：0
* 最终尺寸组：80
* 映射引用闭合：80 / 80
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
132098	132098	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132107	132107	Coupe	Continental GT II Facelift	3W	2	EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	HIGH		READY
132108	132108	Coupe	Continental GT II Facelift	3W	2	EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	HIGH	Supersports专属外部套件物理外廓。	READY
132123	132123	Hatchback	A-Class W177	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
132135	132135	SUV	Discovery I	LJ	3	EU-LAND-ROVER-DISCOVERY-I-SUV-01	HIGH	首发三门物理外廓。	READY
132139	132139	SUV	C3 Aircross I Phase I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH		READY
132146	132146	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入车身标签为Großraumlimousine，车型边界按5008 II SUV。	READY
132147	132147	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH		READY
132149	132149	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132150	132150	Hatchback	Zoe I	X10	5	EU-RENAULT-ZOE-I-X10-HATCHBACK-01	HIGH		READY
132151	132151	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132152	132152	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-01	HIGH		READY
132153	132153	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132155	132155	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132156_m	132156	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132156_xl	132156	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132157_m	132157	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132157_xl	132157	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132158_m	132158	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132158_xl	132158	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	HIGH	XL物理外廓。	READY
132159_xs	132159	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS物理外廓。	READY
132159_m	132159	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M物理外廓。	READY
132160_compact	132160	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact物理外廓。	READY
132160_medium	132160	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium物理外廓。	READY
132161	132161	SUV	Kadjar I Facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132162	132162	SUV	Kadjar I Facelift		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
132163_xs	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	HIGH	XS物理外廓。	READY
132163_m	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M物理外廓。	READY
132163_xl	132163	MPV	SpaceTourer I			EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL物理外廓。	READY
132164_compact	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	HIGH	Compact物理外廓。	READY
132164_medium	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	HIGH	Medium物理外廓。	READY
132164_long	132164	MPV	Proace Verso II			EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	HIGH	Long物理外廓。	READY
132165	132165	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132166	132166	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	HIGH		READY
132176	132176	Sedan	Passat B1	Type 32	4	EU-VW-PASSAT-B1-TYPE32-SEDAN-01	MEDIUM	1.6版本对应1975年后加长车身边界。	READY
132177	132177	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132178	132178	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	HIGH	GT 63物理外廓。	READY
132179	132179	SUV	X4 G02	G02	5	EU-BMW-X4-G02-SUV-STANDARD-01	HIGH		READY
132180	132180	Coupe	AMG GT 4-Door Coupe	X290	5	EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	HIGH	GT 63 S物理外廓。	READY
132183	132183	SUV	Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH		READY
132184	132184	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
132189	132189	Hatchback	Insignia B		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH		READY
132190	132190	Convertible	Zonda Roadster S		2	EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	HIGH		READY
132191	132191	Wagon	Insignia B		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH		READY
132193	132193	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	HIGH		READY
132194	132194	Wagon	Astra K Sports Tourer	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH		READY
132213	132213	SUV	E-S2		5	EU-JAC-E-S2-ELECTRIC-SUV-01	HIGH		READY
132224	132224	Pickup	Amarok I Facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH	3.0 TDI 258仅对应双排驾驶室外廓。	READY
132258	132258	Hatchback	Ibiza II Facelift	6K1	3	EU-SEAT-IBIZA-II-6K1-FACELIFT-CUPRA-R-HATCHBACK-01	HIGH	Cupra R三门物理外廓。	READY
132259	132259	Hatchback	Alto VII	GF	5	EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	HIGH		READY
132266	132266	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-TRACKHAWK-SUV-01	HIGH		READY
132274	132274	SUV	Atlas I		5	EU-VW-ATLAS-I-SUV-01	HIGH	2.0 TSI 162kW四驱版本对应Teramont/Atlas首代外廓。	READY
132276	132276	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	四门轿跑车身。	READY
132277	132277	Coupe	CLS III	C257	4	EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	HIGH	四门轿跑车身。	READY
132282	132282	Van	Golf III	1H	3	EU-VW-GOLF-III-1H-PANEL-VAN-01	MEDIUM	三门厢式掀背物理外廓。	READY
132285	132285	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132286	132286	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132287	132287	Van	Polo III Variant	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	HIGH	改款前商用旅行车外廓。	READY
132288	132288	Van	Polo III Variant Facelift	6V5	5	EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	HIGH	改款后较高商用旅行车外廓。	READY
132291	132291	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	HIGH	三门Hard Top物理外廓。	READY
132297	132297	SUV	01 I		5	EU-LYNK-CO-01-I-PHEV-SUV-01	MEDIUM	首代中国市场PHEV物理外廓。	READY
132298_m	132298	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	HIGH	M物理外廓。	READY
132299	132299	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132301	132301	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SQ8-SUV-01	HIGH		READY
132302	132302	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
132309	132309	Hatchback	Yaris III Facelift		5	EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	HIGH	普通版外廓，独立于GRMN版本。	READY
132313	132313	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132314	132314	SUV	Land Rover 110	LDH	5	EU-LAND-ROVER-110-I-LDH-STATION-WAGON-SUV-01	MEDIUM	闭合越野车边界对应110五门车身；127标准车身为皮卡或改装底盘。	READY
132315	132315	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132316	132316	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	HIGH		READY
132319	132319	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132320	132320	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132321	132321	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132322	132322	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132323	132323	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132324	132324	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132325	132325	Wagon	E-Class S213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
132326	132326	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132327	132327	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132328	132328	Hatchback	A7 II	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH		READY
132329	132329	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132330	132330	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132331	132331	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	HIGH	前驱物理外廓。	READY
132332	132332	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	HIGH	前驱物理外廓。	READY
132333	132333	SUV	Renegade I Facelift	BU	5	EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	HIGH	四驱较高物理外廓。	READY
132334	132334	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132338	132338	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132339	132339	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132340	132340	SUV	Land Rover 90	LDV	3	EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	HIGH	三门Hard Top物理外廓。	READY
132341	132341	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
132342	132342	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
132343	132343	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132344	132344	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132345	132345	Van	Focus I	DNW	5	EU-FORD-FOCUS-I-DNW-VAN-01	HIGH		READY
132356	132356	MPV	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	HIGH	Kombi乘用物理外廓。	READY
132357	132357	MPV	Tourneo Courier I	B460	5	EU-FORD-TOURNEO-COURIER-B460-MPV-01	HIGH		READY
132358	132358	MPV	Vanette II	ULC22		EU-NISSAN-VANETTE-II-ULC22-BUS-01	HIGH		READY
132360_kombi	132360	MPV	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	HIGH	Kombi物理分支。	READY
132360_van	132360	Van	Transit Courier I Facelift	B460		EU-FORD-TRANSIT-COURIER-B460-VAN-01	HIGH	厢式车物理分支。	READY
132363	132363	Van	Work			EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH	Work Box厢式车外廓。	READY
132365	132365	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH		READY
132366_pickup	132366	Pickup	Work			EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pickup平台车物理分支。	READY
132366_chassis	132366	Pickup	Work			EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Pure底盘物理分支。	READY
132367	132367	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH		READY
132368_pickup	132368	Pickup	Work			EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pickup平台车物理分支。	READY
132368_chassis	132368	Pickup	Work			EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Pure底盘物理分支。	READY
132370	132370	Van	Crafter II	SY		EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	e-Crafter量产车身对应L3H3。	READY
132371_l1h1_prefl	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-PREFL-01	HIGH	L1H1改款前物理外廓。	READY
132371_l1h2_prefl	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-PREFL-01	HIGH	L1H2改款前物理外廓。	READY
132371_l2h2_prefl	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-PREFL-01	HIGH	L2H2改款前物理外廓。	READY
132371_l3h2_prefl	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-PREFL-01	HIGH	L3H2改款前物理外廓。	READY
132371_l1h1_facelift	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-FACELIFT-01	HIGH	L1H1改款后物理外廓。	READY
132371_l1h2_facelift	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-FACELIFT-01	HIGH	L1H2改款后物理外廓。	READY
132371_l2h2_facelift	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-FACELIFT-01	HIGH	L2H2改款后物理外廓。	READY
132371_l3h2_facelift	132371	Van	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	HIGH	L3H2改款后物理外廓。	READY
132372_platform_l2_prefl	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-PREFL-01	HIGH	L2H1改款前平台驾驶室外廓。	READY
132372_platform_l3_prefl	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-PREFL-01	HIGH	L3H1改款前平台驾驶室外廓。	READY
132372_platform_l2_facelift	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-FACELIFT-01	HIGH	L2H1改款后平台驾驶室外廓。	READY
132372_platform_l3_facelift	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-FACELIFT-01	HIGH	L3H1改款后平台驾驶室外廓。	READY
132372_chassis_l2_facelift	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	HIGH	L2改款后单排底盘驾驶室外廓。	READY
132372_chassis_l3_facelift	132372	Pickup	Master III	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	HIGH	L3改款后单排底盘驾驶室外廓。	READY
132374	132374	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
132376	132376	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	HIGH		READY
132377	132377	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2501-2600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-CX-5-II-KF-SUV-01	4550	1840	1675	Mazda UK 2020 CX-5 Price and Specification Guide	https://nd-mediagallery2-public-production.s3.amazonaws.com/5763e6971f63626d513e6a8ce49709a9/2020_mazda_cx_5_price_and_spec_apr_20.pdf
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404	Automobile-Catalog 2015 Bentley Continental GT V8 S	https://www.automobile-catalog.com/car/2015/2043680/bentley_continental_gt_v8_s.html
EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	4818	1948	1391	Bentley Heritage Collection 2017 Continental Supersports	https://www.bentleymedia.com/it/heritage-collection/2017-continental-supersports-da17uwr
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440	AutoZine Mercedes A-Class W177 specifications	https://www.autozine.org/Archive/Mercedes/new/A_W177.html
EU-LAND-ROVER-DISCOVERY-I-SUV-01	4521	1793	1928	ZePerfs Land Rover Discovery I 3.9 V8 specifications	https://zeperfs.com/fiche10971-land-rover-discovery-i-3-9-v8.htm
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637	Citroën C3 Aircross 2018 UK official brochure archived copy	https://autocatalogarchive.com/wp-content/uploads/2018/11/Citroen-C3-Aircross-2018-UK.pdf
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1640	Peugeot 5008 II specifications	https://peugeot.drive.place/5008/ii_res/group_offroad_5d/603632
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Peugeot 3008 SUV technical specification brochure	https://autocatalogarchive.com/wp-content/uploads/2020/02/Peugeot-3008-2019-PH.pdf
EU-RENAULT-ZOE-I-X10-HATCHBACK-01	4084	1730	1562	Renault ZOE Press Kit July 2017	https://www.press.renault.co.uk/assets/documents/original/10706-RenaultZOEPressKitJuly2017.pdf
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705	Audi MediaCenter The new Audi Q8 official press information	https://www.audi-mediacenter.com/system/production/uploaded_files/12201/file/4809115148b90f8e62020bcafe6c2fb60cf1e71f/en_Press_Information_Audi_Q8.pdf?1531131786=&disposition=attachment
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW UK Technical Data X3 xDrive20d/xDrive30d	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0272066EN_GB/397550
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën Berlingo official technical specifications	https://www.citroen.ua/content/dam/citroen/ukraine/files/ttx/ttx-k9berlingo-vp.pdf
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën Berlingo official technical specifications	https://www.citroen.ua/content/dam/citroen/ukraine/files/ttx/ttx-k9berlingo-vp.pdf
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613	Renault KADJAR official eBrochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/car-ebrochures/KADJAR-eBrochure.pdf
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890	Citroën SpaceTourer official price and specification table June 2018	https://www.media.stellantis.com/uploads/psa/attached_files/25/TABELA%2002%202018%20SPACETOURER.PDF
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890	Toyota New Proace Verso official technical specifications	https://media.toyota.co.uk/new-toyota-proace-verso/
EU-VW-PASSAT-B1-TYPE32-SEDAN-01	4290	1615	1360	Volkswagen Newsroom Passat B1 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b1-profile-19535
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621	BMW Group technical data BMW X4 G02	https://www.press.bmwgroup.com/portugal/article/attachment/T0186722PT/419086
EU-MERCEDES-BENZ-AMG-GT-X290-63-COUPE-01	5054	1953	1442	Automobile-Catalog 2019 Mercedes-AMG GT 63 4MATIC+	https://www.automobile-catalog.com/car/2019/2739470/mercedes-amg_gt_63_4matic_plus.html
EU-MERCEDES-BENZ-AMG-GT-X290-63S-COUPE-01	5054	1953	1447	Automobile-Catalog 2018 Mercedes-AMG GT 63 S 4MATIC+	https://www.automobile-catalog.com/car/2018/2739485/mercedes-amg_gt_63_s_4matic_plus.html
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Opel Grandland X official specifications	https://nd-mediagallery2-public-production.s3.amazonaws.com/f52425abdaff90529ba7443030f717c6/12014_58273_opel_grandland_x_my18_spec_sheets_a4l_fc_e_web_1_.pdf
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Opel Crossland X launch specifications	https://www.netcarshow.com/opel/2018-crossland_x/
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall Insignia Price/Specification Guide MY2018.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/GML_10970043_Insignia_Spec_PG_9_May_2018-1525794507.pdf
EU-PAGANI-ZONDA-ROADSTER-S-CONVERTIBLE-01	4395	2055	1151	Pagani Zonda Roadster official technical data	https://www.pagani.com/it/zonda-roadster/
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514	Vauxhall Insignia Price/Specification Guide MY2018.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/GML_10970043_Insignia_Spec_PG_9_May_2018-1525794507.pdf
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485	Automobile-Catalog Opel Astra K specifications	https://www.automobile-catalog.com/car/2017/2532530/opel_astra_1_6_cdti_95.html
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510	Automobile-Catalog Opel Astra K Sports Tourer specifications	https://www.automobile-catalog.com/car/2021/2916665/opel_astra_sports_tourer_1_2_direct_injection_turbo_110.html
EU-JAC-E-S2-ELECTRIC-SUV-01	4135	1750	1560	JAC e-S2 official specifications	https://jacen.jac.com.cn/models/e-s2/
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834	Volkswagen Amarok Double Cab official specifications	https://cms.my.na/assets/documents/p18hpnjf6ckff1g441r1s18u9lr82.pdf
EU-SEAT-IBIZA-II-6K1-FACELIFT-CUPRA-R-HATCHBACK-01	3876	1640	1422	Automobile-Catalog 2000 SEAT Ibiza Cupra R	https://www.automobile-catalog.com/car/2000/3070610/seat_ibiza_cupra_r.html
EU-SUZUKI-ALTO-VII-GF-HATCHBACK-01	3500	1600	1470	Automobile-Catalog 2012 Suzuki Alto 1.0 Base Europe	https://www.automobile-catalog.com/car/2012/3403685/suzuki_alto_1_0.html
EU-JEEP-GRAND-CHEROKEE-IV-WK2-TRACKHAWK-SUV-01	4822	1943	1724	2018 Jeep Grand Cherokee Trackhawk official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2018_JP_GrCherokee_Trackhawk_SP10kge6g0tjfo0bkv87ru3cehu4.pdf
EU-VW-ATLAS-I-SUV-01	5036	1989	1769	Auto-Data Volkswagen Teramont 2.0 TSI 220 4MOTION	https://www.auto-data.net/en/volkswagen-teramont-2.0-tsi-220hp-4motion-automatic-34783
EU-MERCEDES-BENZ-CLS-III-C257-COUPE-01	4988	1890	1435	AutoZine Mercedes-Benz CLS C257 specifications	https://www.autozine.org/Archive/Mercedes/old/CLS_C257.html
EU-VW-GOLF-III-1H-PANEL-VAN-01	4020	1695	1425	Volkswagen Classic Golf III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433	AIC Germany Polo Kasten/Kombi 6V5 catalogue; Auto-Data Volkswagen Polo III Variant 1.7 SDI	https://aic-germany.de/en/product-catalogue/348;https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n-1.7-sdi-60hp-8463
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459	AIC Germany Polo Kasten/Kombi 6V5 catalogue; Auto-Data Volkswagen Polo III Variant Facelift 1.4 16V	https://aic-germany.de/en/product-catalogue/348;https://www.auto-data.net/en/volkswagen-polo-iii-variant-6n2-facelift-1999-1.4-16v-75hp-8460
EU-LAND-ROVER-90-I-LDV-HARD-TOP-SUV-01	3858	1790	1972	Automobile-Catalog Land-Rover 90 Hard Top 2.5 Diesel; Automobile-Catalog Land-Rover 90 Hard Top 2.5 Turbo Diesel	https://www.automobile-catalog.com/car/1985/1393730/land-rover_90_hard_top_2_5_diesel.html;https://www.automobile-catalog.com/car/1988/1394315/land-rover_90_hard_top_2_5_turbo_diesel.html
EU-LYNK-CO-01-I-PHEV-SUV-01	4512	1857	1673	Auto-Data Lynk & Co 01 1.5 T3 Plug-in Hybrid 2018-2019	https://www.auto-data.net/en/lynk-co-01-1.5-t3-256hp-plug-in-hybrid-dcth-51531
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708	Audi SQ8 TDI official technical data	https://press.audi.co.uk/assets/documents/original/2941-AudiSQ8TDITechnicalDataUKOctober2019.pdf
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510	Toyota Yaris Generation 3 Second Minor Change official press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen3-Yaris-2nd-MC-archive-press-pack.pdf
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468	Mercedes-Benz E-Class Saloon and Estate official brochure archived copy	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-LAND-ROVER-110-I-LDH-STATION-WAGON-SUV-01	4445	1790	2035	UltimateSpecs Land Rover 110 V8 1983-1990	https://www.ultimatespecs.com/car-specs/Land-Rover/415/Land-Rover-110-V8.html
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	Mercedes-Benz E-Class Saloon and Estate official brochure archived copy	https://imgcdn.oto.com.sg/brochures/8/178/mercedes-benz-e-class-saloon-518737.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi MediaCenter The new Audi A6 official model information	https://www.audi-mediacenter.com/en/the-audi-a6-until-2025-the-car-of-many-talents-in-the-business-class-10240/design-10256
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	Audi A6 Avant official dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-a6-avant-1400/download
EU-AUDI-A7-II-4KA-HATCHBACK-01	4969	1908	1422	Audi MediaCenter Audi A7 Sportback official model information	https://www.audi-mediacenter.com/en/the-audi-a7-sportback-until-2025-progressive-in-design-and-technology-9831/design-9836
EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	4236	1805	1667	Auto-Data Jeep Renegade Facelift 1.0 T-GDI; Auto-Data Jeep Renegade Facelift 1.3 Turbo DDCT	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.0-t-gdi-120hp-35848;https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.3-turbo-150hp-ddct-39051
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684	Auto-Data Jeep Renegade Facelift 1.3 T-GDI 4x4	https://www.auto-data.net/en/jeep-renegade-facelift-2018-1.3-t-gdi-180hp-4x4-automatic-35849
EU-FORD-FOCUS-I-DNW-VAN-01	4465	1702	1532	AIC Germany Focus I Kasten/Kombi DNW catalogue; Automobile-Catalog Ford Focus Turnier 1.6 16V Trend	https://www.aic-germany.de/en/product-catalogue/3896;https://www.automobile-catalog.com/car/2000/955625/ford_focus_turnier_estate_1_6_16v_trend_zetec.html
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Hyundai i30 official model specification sheet	https://www.hyundai.com/content/dam/hyundai/au/en/models/i30/docs/Hyundai_i30_Model_Specifications_Sheet.pdf
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Hyundai i30 official technical specifications	https://www.hyundai.news/newsroom/dam/eu/press-kits/20200226_i30/i30_data.preliminary.pdf
EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	4157	1764	1747	Ford Transit Courier official technical specifications; Coches.net Transit Courier Kombi 2018 specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Courier/TransitCourier_Specifications_EU.pdf;https://www.coches.net/fichas_tecnicas/ford/transit_courier/furgoneta/4-puertas/kombi_15_tdci_71kw_trend_100cv_diesel/74942/773679520190101/
EU-FORD-TOURNEO-COURIER-B460-MPV-01	4157	1764	1741	Ford Tourneo Courier official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Tourneo-Courier.pdf
EU-NISSAN-VANETTE-II-ULC22-BUS-01	4360	1690	1900	Truck1 Nissan Vanette Bus C22 2.0 D ULC22 technical specifications	https://www.truck1.eu/blog/nissan-vanette-bus-c22-2-0-d-ulc22-67-hp-tech-specs-t34751
EU-FORD-TRANSIT-COURIER-B460-VAN-01	4157	1764	1770	Ford Transit Courier official technical specifications; ADAC Transit Courier Kastenwagen specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Transit%20Courier/TransitCourier_Specifications_EU.pdf;https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/ford/transit-courier/1generation-facelift/307340/
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PICKUP-01	4741	1814	1859	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	4676	1796	1861	StreetScooter Tools on Wheels official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-PREFL-01	5048	2070	2307	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-PREFL-01	5048	2070	2500	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-PREFL-01	5548	2070	2499	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-PREFL-01	6198	2070	2488	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-FACELIFT-01	5075	2070	2303	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-FACELIFT-01	5075	2070	2496	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-FACELIFT-01	5575	2070	2495	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-PREFL-01	5530	2070	2270	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-PREFL-01	6180	2070	2264	Renault Master Z.E. official brochure March 2018	https://www.rapidvans.co.uk/storage/S26BBQy2PoYH2eDyZ85C3TsYiFkLGr-metaUmVuYXVsdCBNYXN0ZXIgWkUgQnJvY2h1cmUucGRm-.pdf
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-FACELIFT-01	5557	2070	2270	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-FACELIFT-01	6207	2070	2264	Renault Trucks Master Z.E. official technical brochure	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265	Renault Master III X62 chassis cab official technical data	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258	Renault Master III X62 chassis cab official technical data	https://www.codica.fr/wp-content/uploads/2017/12/Renault-Trucks-Master-Z.E.-100-%C3%A9lectrique.pdf
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430	Automobile-Catalog 2018 Mercedes-Benz E 300 d Coupe	https://www.automobile-catalog.com/car/2018/2726570/mercedes-benz_e_300_d_coupe.html
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428	Automobile-Catalog 2017 Mercedes-Benz E 300 Cabriolet	https://www.automobile-catalog.com/car/2017/2560385/mercedes-benz_e_300_cabriolet.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2501-2600_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1800 行）
- 累计尺寸组：dimension_groups_final.tsv（906 行）

