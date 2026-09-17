# 任务：all 第 4401-4500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0045__d2e305c3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4401-4500 行

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
all 第 4401-4500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIA-952-SEDAN-Q4-01	4643	1860	1450
EU-ALFA-ROMEO-GIULIA-952-SEDAN-RWD-01	4643	1860	1436
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538
EU-CHEVROLET-CORVETTE-C3-COUPE-FACELIFT-01	4704	1753	1219
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-DACIA-LODGY-MPV-01	4498	1751	1679
EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	5248	1956	1953
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L2-AWD-01	5572	2052	2210
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L3-AWD-01	6022	2052	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L1-RWD-SRW-01	5205	2052	2215
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	5572	2052	2194
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-DRW-01	5572	2111	2210
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-RWD-SRW-01	5572	2052	2210
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	6022	2052	2186
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-DRW-01	6022	2111	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-RWD-SRW-01	6022	2052	2202
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	6579	2052	2186
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-DRW-01	6579	2111	2214
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-RWD-SRW-01	6579	2052	2214
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L5-RWD-01	7577	2066	2206
EU-FORD-TRANSIT-V363-VAN-L2H2-AWD-01	5531	2059	2534
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2490
EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	5531	2059	2542
EU-FORD-TRANSIT-V363-VAN-L2H3-01	5531	2059	2781
EU-FORD-TRANSIT-V363-VAN-L2H3-AWD-01	5531	2059	2771
EU-FORD-TRANSIT-V363-VAN-L3H2-AWD-01	5981	2059	2533
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2541
EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	5981	2059	2543
EU-FORD-TRANSIT-V363-VAN-L3H3-AWD-01	5981	2059	2769
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2780
EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	5981	2059	2782
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	6704	2126	2790
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	6704	2059	2790
EU-HYUNDAI-I10-II-HATCHBACK-FACELIFT-01	3665	1660	1500
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-HYUNDAI-I30-PD-HATCHBACK-N-01	4335	1795	1451
EU-HYUNDAI-I30-PD-HATCHBACK-N-PERFORMANCE-01	4335	1795	1447
EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	4410	1820	1655
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A45-HATCHBACK-01	4445	1850	1412
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA45-COUPE-01	4693	1857	1407
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA35-WAGON-01	4695	1834	1405
EU-MERCEDES-BENZ-CLA-X118-AMG-CLA45-WAGON-01	4693	1857	1417
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442
EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	4895	1928	1910
EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	5370	1928	1910
EU-MERCEDES-BENZ-VITO-W447-LONG-01	5140	1928	1910
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432
EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	3879	1762	1420
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-MITSUBISHI-L200-IV-KB9T-DOUBLE-CAB-PICKUP-01	5115	1800	1780
EU-MITSUBISHI-L200-V-CLUB-CAB-PICKUP-01	5195	1785	1775
EU-MITSUBISHI-L200-V-DOUBLE-CAB-PICKUP-01	5205	1785	1775
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	5215	1815	1780
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	5225	1815	1780
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	5305	1815	1780
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812
EU-OPEL-COMBO-E-LIFE-L-MPV-01	4403	1848	1844
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880
EU-OPEL-COMBO-E-LIFE-XL-MPV-02	4753	1848	1849
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460
EU-PEUGEOT-208-II-HATCHBACK-01	4055	1745	1430
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PEUGEOT-PARTNER-ORIGIN-I-M59-01	4137	1724	1810
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-PREFL-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-PREFL-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-FACELIFT-01	5557	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-PREFL-01	5530	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-FACELIFT-01	6207	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-PREFL-01	6180	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-FACELIFT-01	5075	2070	2303
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-PREFL-01	5048	2070	2307
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-FACELIFT-01	5075	2070	2496
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-PREFL-01	5048	2070	2500
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-FACELIFT-01	5575	2070	2495
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-PREFL-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-PREFL-01	6198	2070	2488
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531
EU-TOYOTA-C-HR-I-AX10-SUV-01	4360	1795	1565
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	4609	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	4609	1920	1910
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	4959	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	4959	1920	1899
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	Gla-Klasse	GLA 250 Flex	SUV	Frontantrieb	Benzin/Ethanol	155	211	Jan 2015	Dec 2019	2024-03-01	138001
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	81	110	Jul 2019	Aug 2024	2025-02-03	138017
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Oct 2019	Aug 2024	2025-02-03	138018
VW	Transporter t6	2.0 TDI	Kasten	Frontantrieb	Diesel	146	199	Aug 2019	Aug 2024	2025-11-01	138019
VW	Transporter t6	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	146	199	Aug 2019	Aug 2024	2025-02-03	138020
VW	Transporter t6	2.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	146	199	Aug 2019	Aug 2024	2025-02-03	138021
KIA	Seltos	2.0 MPI	SUV	Frontantrieb	Benzin	110	150	Aug 2019	-	2024-03-01	138023
VW	Caddy iv	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jun 2019	Sep 2020	2024-03-01	138026
Renault	Trafic iii	2.0 DCI 120	Kasten	Frontantrieb	Diesel	88	120	Jun 2019	-	2024-03-01	138027
Renault	Trafic iii	2.0 DCI 170	Kasten	Frontantrieb	Diesel	125	170	Jun 2019	-	2024-03-01	138028
Mercedes-benz	B-Klasse sports tourer	B 200 D 4-matic	Schrägheck	Allrad	Diesel	110	150	Oct 2019	Sep 2021	2024-03-01	138068
Mercedes-benz	B-Klasse sports tourer	B 220 D 4-matic	Schrägheck	Allrad	Diesel	140	190	Oct 2019	-	2024-03-01	138071
Mercedes-benz	A-Klasse	A 200 D 4-matic	Schrägheck	Allrad	Diesel	110	150	Oct 2019	-	2024-03-01	138072
Mercedes-benz	A-Klasse	A 220 D 4-matic	Schrägheck	Allrad	Diesel	140	190	Oct 2019	-	2024-03-01	138073
Opel	Vivaro b	1.6 Cdti	Kasten	Frontantrieb	Diesel	89	121	Mar 2016	Dec 2019	2024-03-01	138074
Mercedes-benz	A-Klasse	A 160 D	Stufenheck	Frontantrieb	Diesel	70	95	Oct 2019	-	2024-03-01	138081
Mercedes-benz	A-Klasse	A 200 D 4-matic	Stufenheck	Allrad	Diesel	110	150	Oct 2019	-	2024-03-01	138082
Mercedes-benz	A-Klasse	A 220 D 4-matic	Stufenheck	Allrad	Diesel	140	190	Oct 2019	-	2024-03-01	138083
VW	Grand california camper	2.0 TDI FWD	Bus	Frontantrieb	Diesel	130	177	Apr 2019	-	2025-04-01	138085
VW	Grand california camper	2.0 TDI 4motion	Bus	Allrad	Diesel	130	177	Apr 2019	-	2024-03-01	138086
Audi	Q8	45 Tfsi Quattro	SUV	Allrad	Benzin	180	245	Oct 2019	-	2024-03-01	138089
Maserati	Levante	3.8 Trofeo Q4	SUV	Allrad	Benzin	427	581	Oct 2019	-	2025-12-01	138092
Mercedes-benz	Vito tourer	110 CDI	Bus	Frontantrieb	Diesel	75	102	Sep 2019	-	2024-03-01	138108
Mercedes-benz	Cla	CLA 200 D 4-matic	Kombi	Allrad	Diesel	110	150	Oct 2019	-	2024-03-01	138109
Mercedes-benz	Cla	CLA 220 D 4-matic	Kombi	Allrad	Diesel	140	190	Oct 2019	-	2024-03-01	138110
Dacia	Lodgy	1.3 TCE 100	Großraumlimousine	Frontantrieb	Benzin	75	102	Jan 2019	-	2024-03-01	138119
Dacia	Duster	1.0 TCE 100 4X4	SUV	Allrad	Benzin	74	101	Jan 2019	-	2025-04-01	138120
Renault	Clio v	1.0 TCE 100	Schrägheck	Frontantrieb	Benzin	74	101	Jun 2019	-	2026-05-01	138121
Renault	Clio v	1.3 TCE 130	Schrägheck	Frontantrieb	Benzin	96	131	Jun 2019	-	2026-05-01	138122
Renault	Clio v	1.5 Blue DCI 85	Schrägheck	Frontantrieb	Diesel	63	86	Jun 2019	-	2026-05-01	138123
Renault	Clio v	1.5 Blue DCI 115	Schrägheck	Frontantrieb	Diesel	85	116	Jun 2019	-	2026-05-01	138124
Renault	Duster	1.5 DCI 110 4X4	SUV	Allrad	Diesel	80	109	Jan 2018	Jul 2024	2025-12-01	138125
Renault	Duster	1.5 DCI 110	SUV	Frontantrieb	Diesel	80	109	Jan 2018	Jul 2024	2025-12-01	138126
BMW	6	630 I Xdrive	Schrägheck	Allrad	Benzin	190	258	Jul 2019	-	2024-03-01	138128
BMW	2	M2 CS	Coupe	Heckantrieb	Benzin	331	450	Nov 2019	Jun 2021	2024-03-01	138130
Mercedes-benz	Vito	110 CDI	Kasten	Frontantrieb	Diesel	75	102	Sep 2019	-	2024-03-01	138131
Mercedes-benz	Vito tourer	114 CDI	Bus	Frontantrieb	Diesel	100	136	Sep 2019	-	2024-03-01	138133
Mercedes-benz	Vito	114 CDI	Kasten	Frontantrieb	Diesel	100	136	Sep 2019	-	2024-03-01	138134
Mercedes-benz	Vito mixto	110 CDI	Kasten	Frontantrieb	Diesel	75	102	Sep 2019	-	2024-03-01	138135
Mercedes-benz	Vito mixto	114 CDI	Kasten	Frontantrieb	Diesel	100	136	Sep 2019	-	2024-03-01	138136
Alfa Romeo	Stelvio	2.9 Q4	SUV	Allrad	Benzin	382	519	Nov 2019	-	2024-03-01	138149
Alfa Romeo	Giulia	2.9	Stufenheck	Heckantrieb	Benzin	382	519	Nov 2019	-	2024-03-01	138152
Opel	Combo	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Sep 2019	-	2024-03-01	138153
Skoda	Kamiq	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2019	-	2024-03-01	138164
Ford	Transit v363	2.0 Ecoblue RWD	Kasten	Heckantrieb	Diesel	136	185	May 2019	-	2024-03-01	138181
Ford	Transit v363	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	136	185	May 2019	-	2024-03-01	138182
Mini	Mini	Cooper SE / Electric	Schrägheck	Frontantrieb	Elektro	75	102	Nov 2019	-	2025-04-01	138184
Toyota	C-Hr	2.0 Hybrid	SUV	Frontantrieb	Benzin/Elektro	135	184	Oct 2019	-	2024-03-01	138191
Mitsubishi	L200	2.2 Di-d	Pick-up	Heckantrieb	Diesel	110	150	Jul 2019	-	2024-03-01	138199
Citroën	C5	1.6 Hybrid 225	SUV	Frontantrieb	Benzin/Elektro	165	224	Apr 2020	-	2024-07-01	138210
Ford	Transit v363	2.0 Ecoblue	Pritsche/Fahrgestell	Frontantrieb	Diesel	136	185	May 2019	-	2024-03-01	138215
Ford	Transit v363	2.0 Ecoblue RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	136	185	May 2019	-	2024-03-01	138216
Porsche	911	3.0 Carrera 4	Coupe	Allrad	Benzin	283	385	Jan 2019	Dec 2024	2026-03-01	138218
Porsche	911	3.0 Carrera 4	Cabriolet	Allrad	Benzin	283	385	Jan 2019	Dec 2024	2026-03-01	138219
Mazda	2	1.5 Skyactiv-g M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	66	90	Aug 2019	-	2024-03-01	138223
Mazda	2	1.5 Skyactiv-g M Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	55	75	Aug 2019	-	2024-03-01	138224
Peugeot	208 i	1.6 E-hdi	Schrägheck	Frontantrieb	Diesel	82	112	Jul 2015	Dec 2019	2024-03-01	138228
Audi	A8 d5	60 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	330	449	Oct 2019	-	2024-03-01	138230
Opel	Movano b	2.3 Cdti FWD	Bus	Frontantrieb	Diesel	132	179	Aug 2019	Dec 2021	2026-03-01	138232
Opel	Movano b	2.3 Cdti FWD	Kasten	Frontantrieb	Diesel	132	179	Aug 2019	Dec 2021	2026-03-01	138233
Opel	Movano b	2.3 Cdti FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	132	179	Aug 2019	Dec 2021	2026-03-01	138234
Audi	Q3	2.5 RS Tfsi Quattro	SUV	Allrad	Benzin	294	400	Oct 2019	-	2025-11-01	138237
Audi	A5	35 TDI	Cabriolet	Frontantrieb	Diesel	120	163	Oct 2019	-	2024-03-01	138240
Renault	Clio v	1.0 SCE 75	Schrägheck	Frontantrieb	Benzin	53	72	Jun 2019	-	2026-05-01	138242
Audi	A4 allroad b9	50 TDI Quattro	Kombi	Allrad	Diesel	210	286	Nov 2019	-	2024-03-01	138272
Audi	Q7	55 Tfsi Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	250	340	Jul 2019	-	2024-03-01	138273
Audi	A7 sportback	RS7 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	441	600	Oct 2019	-	2025-11-01	138274
Audi	A6 c8 avant	RS6 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	441	600	Sep 2019	-	2025-11-01	138275
Fiat	Talento	2.0 Ecojet	Kasten	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138286
Fiat	Talento	2.0 Ecojet	Kasten	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138287
Fiat	Talento	2.0 Ecojet	Kasten	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138288
Fiat	Talento	2.0 Ecojet	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138289
Fiat	Talento	2.0 Ecojet	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138291
Fiat	Talento	2.0 Ecojet	Bus	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138292
Fiat	Talento	2.0 Ecojet	Bus	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138294
Chevrolet	Corvette	5.7 Z06	Coupe	Heckantrieb	Benzin	287	390	Oct 2000	Mar 2004	2024-03-01	138300
Chevrolet	Cruze	1.6	Stufenheck	Frontantrieb	Benzin	86	117	Dec 2012	-	2024-03-01	138319
Hyundai	I10 i	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	57	78	Jan 2010	Dec 2013	2024-03-01	138333
Citroën	Berlingo	1.6 HDI 92	Kasten/Großraumlimousine	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2010	2024-03-01	138351
Peugeot	Partner	1.6 HDI 92	Kasten/Großraumlimousine	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2010	2024-03-01	138352
Citroën	Berlingo	1.6 HDI 92	Großraumlimousine	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2010	2024-03-01	138353
Peugeot	Partner	1.6 HDI 92	Großraumlimousine	Frontantrieb	Diesel	68	92	Nov 2009	Dec 2010	2024-03-01	138354
Hyundai	I30	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	73	99	Jan 2013	Dec 2014	2024-07-01	138356
Hyundai	I30	1.4 MPI	Kasten/Kombi	Frontantrieb	Benzin	74	101	May 2015	May 2017	2025-02-03	138357
Hyundai	I30	1.4 MPI	Kasten/Schrägheck	Frontantrieb	Benzin	74	101	May 2015	May 2017	2025-02-03	138360
Audi	A1	25 Tfsi	Schrägheck	Frontantrieb	Benzin	70	95	Jul 2019	Jun 2022	2024-03-01	138405
Audi	A1	30 Tfsi	Schrägheck	Frontantrieb	Benzin	85	116	Jul 2019	Jun 2022	2024-03-01	138406
Audi	A1	35 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2019	Jun 2022	2024-03-01	138407
Audi	A6 allroad c8	55 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	250	340	Nov 2019	-	2024-03-01	138414
KIA	Pride	1.3	Stufenheck	Frontantrieb	Benzin	47	64	Oct 1996	May 2001	2024-03-01	138429
Audi	Q3	35 Tfsi	SUV	Frontantrieb	Benzin	110	150	Sep 2019	-	2024-03-01	138446
Audi	Q3	45 Tfsi Quattro	SUV	Allrad	Benzin	169	230	Jun 2019	-	2024-03-01	138447
Audi	Q3	35 TDI	SUV	Frontantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	138449
Audi	Q3	35 TDI Quattro	SUV	Allrad	Diesel	110	150	Sep 2019	-	2024-03-01	138450
Audi	Q3	40 TDI Quattro	SUV	Allrad	Diesel	140	190	Jul 2019	-	2024-03-01	138451
Audi	Q3	2.5 RS Tfsi Quattro	SUV	Allrad	Benzin	294	400	Oct 2019	-	2025-11-01	138452
Hyundai	Ix35	2.0 4WD	SUV	Allrad	Benzin	113	154	Sep 2014	Dec 2015	2024-03-01	138460
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	90	122	Nov 2019	Dec 2022	2026-01-01	138488
Opel	Astra k	1.6 Cdti	Kasten/Schrägheck	Frontantrieb	Diesel	100	136	Apr 2018	Aug 2019	2025-12-01	138490
Renault	Master iii	2.3 DCI 180 FWD	Pritsche/Fahrgestell	Frontantrieb	Diesel	132	179	Jul 2019	Dec 2024	2026-03-01	138493


--- Round 1 / 首次发送 ---
## 更新点

* 首轮完成 100 个 Ktype 的初始映射：**READY 50，PENDING 50**。
* READY 行共引用 **33 个尺寸组**：直接复用跨批次缓存 26 个，首次创建 7 个。
* 首次闭合 GLA X156、B-Class W247、Clio V Phase 1、BMW M2 CS、Audi RS Q3、RS7 Sportback、RS6 Avant 尺寸组。GLA、B-Class 与 Clio 的宽度均采用不含后视镜口径；BMW 与 Audi 特殊性能车型依据技术资料或官方尺寸图建立独立组。 ([汽车目录][1])
* Levante Trofeo 的 5003 × 1968 × 1679 mm 与已有 Levante I 尺寸组一致，因此直接复用，未重复建组。 ([Stellantis Media][2])
* 商用车通用 Ktype 暂不猜测轴距、车顶、驾驶室或 SRW/DRW 分支，保持 PENDING 且不填写尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：50
* PENDING 映射：50
* 当前已引用尺寸组：33
* 本轮首次创建尺寸组：7
* 本轮复用既有尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138001	138001	SUV	GLA I	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
138017	138017	Pickup	Transporter T6.1	T6.1			LOW	轴距、驾驶室及底盘分支未闭合	PENDING: 轴距、驾驶室及底盘分支未闭合
138018	138018	Pickup	Transporter T6.1	T6.1			LOW	轴距、驾驶室及底盘分支未闭合	PENDING: 轴距、驾驶室及底盘分支未闭合
138019	138019	Van	Transporter T6.1	T6.1			LOW	轴距与车顶高度分支未闭合	PENDING: 轴距与车顶高度分支未闭合
138020	138020	Pickup	Transporter T6.1	T6.1			LOW	轴距、驾驶室及底盘分支未闭合	PENDING: 轴距、驾驶室及底盘分支未闭合
138021	138021	Pickup	Transporter T6.1	T6.1			LOW	轴距、驾驶室及4Motion底盘分支未闭合	PENDING: 轴距、驾驶室及4Motion底盘分支未闭合
138023	138023	SUV	Seltos I		5	EU-KIA-SELTOS-I-SUV-4WD-01	MEDIUM	前驱与四驱共用车身外廓。	READY
138026	138026	Van	Caddy IV	2K			LOW	Van/MPV及SWB/LWB分支未闭合	PENDING: Van/MPV及SWB/LWB分支未闭合
138027	138027	Van	Trafic III	X82			LOW	L1/L2与H1/H2分支尚未按Ktype闭合	PENDING: L1/L2与H1/H2分支尚未按Ktype闭合
138028	138028	Van	Trafic III	X82			LOW	L1/L2与H1/H2分支尚未按Ktype闭合	PENDING: L1/L2与H1/H2分支尚未按Ktype闭合
138068	138068	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
138071	138071	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
138072	138072	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
138073	138073	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
138074	138074	Van	Vivaro B	X82			LOW	L1/L2与H1/H2分支尚未按Ktype闭合	PENDING: L1/L2与H1/H2分支尚未按Ktype闭合
138081	138081	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138082	138082	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138083	138083	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138085	138085	MPV	Grand California I				LOW	Grand California 600/680分支未闭合	PENDING: Grand California 600/680分支未闭合
138086	138086	MPV	Grand California I				LOW	Grand California 600/680及4Motion边界未闭合	PENDING: Grand California 600/680及4Motion边界未闭合
138089	138089	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
138092	138092	SUV	Levante I		5	EU-MASERATI-LEVANTE-I-SUV-01	MEDIUM	Trofeo沿用Levante I车身外廓。	READY
138108	138108	MPV	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138109	138109	Wagon	CLA II	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
138110	138110	Wagon	CLA II	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
138119	138119	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
138120	138120	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH		READY
138121	138121	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138122	138122	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138123	138123	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138124	138124	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138125	138125	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	MEDIUM	Renault与Dacia版本共用Duster II四驱外廓。	READY
138126	138126	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	MEDIUM	Renault与Dacia版本共用Duster II前驱外廓。	READY
138128	138128	Hatchback	6 Series Gran Turismo	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
138130	138130	Coupe	M2	F87	2	EU-BMW-2-F87-M2-CS-COUPE-01	HIGH		READY
138131	138131	Van	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138133	138133	MPV	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138134	138134	Van	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138135	138135	Van	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138136	138136	Van	Vito III	W447			LOW	Compact/Long/Extra-long分支未闭合	PENDING: Compact/Long/Extra-long分支未闭合
138149	138149	SUV	Stelvio I	949	5		LOW	Quadrifoglio专属外廓的不含镜宽度尚未闭合	PENDING: Quadrifoglio专属外廓的不含镜宽度尚未闭合
138152	138152	Sedan	Giulia	952	4		LOW	Quadrifoglio专属外廓的不含镜宽度尚未闭合	PENDING: Quadrifoglio专属外廓的不含镜宽度尚未闭合
138153	138153	Van	Combo E	K9			LOW	Van/MPV与M/XL分支未闭合	PENDING: Van/MPV与M/XL分支未闭合
138164	138164	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
138181	138181	Van	Transit V363	V363			LOW	RWD的L/H、SRW/DRW分支未闭合	PENDING: RWD的L/H、SRW/DRW分支未闭合
138182	138182	Van	Transit V363	V363			LOW	FWD的L/H分支未闭合	PENDING: FWD的L/H分支未闭合
138184	138184	Hatchback	Mini III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	HIGH		READY
138191	138191	SUV	C-HR I	AX10	5	EU-TOYOTA-C-HR-I-AX10-SUV-01	HIGH		READY
138199	138199	Pickup	L200 V Facelift				LOW	Club Cab/Double Cab及后保险杠分支未闭合	PENDING: Club Cab/Double Cab及后保险杠分支未闭合
138210	138210	SUV	C5 Aircross I	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
138215	138215	Pickup	Transit V363	V363			LOW	FWD底盘的轴距与驾驶室分支未闭合	PENDING: FWD底盘的轴距与驾驶室分支未闭合
138216	138216	Pickup	Transit V363	V363			LOW	RWD底盘的轴距、驾驶室及SRW/DRW分支未闭合	PENDING: RWD底盘的轴距、驾驶室及SRW/DRW分支未闭合
138218	138218	Coupe	911 VIII	992	2	EU-PORSCHE-911-992-CARRERA-COUPE-01	HIGH	Carrera 4与Carrera共用992标准车身外廓。	READY
138219	138219	Convertible	911 VIII	992	2	EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	HIGH	Carrera 4与Carrera共用992标准敞篷外廓。	READY
138223	138223	Hatchback	Mazda2 III	DJ	5		LOW	欧规Mazda2高度配置冲突未闭合	PENDING: 欧规Mazda2高度配置冲突未闭合
138224	138224	Hatchback	Mazda2 III	DJ	5		LOW	欧规Mazda2高度配置冲突未闭合	PENDING: 欧规Mazda2高度配置冲突未闭合
138228	138228	Hatchback	208 I Facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH		READY
138230	138230	Sedan	A8 IV	D5	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
138232	138232	MPV	Movano B	X62			LOW	Bus的L/H分支未闭合	PENDING: Bus的L/H分支未闭合
138233	138233	Van	Movano B	X62			LOW	Van的L/H分支未闭合	PENDING: Van的L/H分支未闭合
138234	138234	Pickup	Movano B	X62			LOW	底盘轴距与驾驶室分支未闭合	PENDING: 底盘轴距与驾驶室分支未闭合
138237	138237	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	HIGH		READY
138240	138240	Convertible	A5 II Facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
138242	138242	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138272	138272	Wagon	A4 allroad B9	B9	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
138273	138273	SUV	Q7 II Facelift	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH		READY
138274	138274	Hatchback	A7 II	C8	5	EU-AUDI-A7-C8-RS7-SPORTBACK-01	HIGH		READY
138275	138275	Wagon	A6 V	C8	5	EU-AUDI-A6-C8-RS6-AVANT-01	HIGH		READY
138286	138286	Van	Talento II	X82			LOW	L1/L2与H1/H2分支未闭合	PENDING: L1/L2与H1/H2分支未闭合
138287	138287	Van	Talento II	X82			LOW	L1/L2与H1/H2分支未闭合	PENDING: L1/L2与H1/H2分支未闭合
138288	138288	Van	Talento II	X82			LOW	L1/L2与H1/H2分支未闭合	PENDING: L1/L2与H1/H2分支未闭合
138289	138289	Pickup	Talento II	X82			LOW	平台底盘轴距分支未闭合	PENDING: 平台底盘轴距分支未闭合
138291	138291	Pickup	Talento II	X82			LOW	平台底盘轴距分支未闭合	PENDING: 平台底盘轴距分支未闭合
138292	138292	MPV	Talento II	X82			LOW	乘用Bus的L1/L2分支未闭合	PENDING: 乘用Bus的L1/L2分支未闭合
138294	138294	MPV	Talento II	X82			LOW	乘用Bus的L1/L2分支未闭合	PENDING: 乘用Bus的L1/L2分支未闭合
138300	138300	Coupe	Corvette C5	C5	2		LOW	C5 Z06三维及不含镜宽度来源未闭合	PENDING: C5 Z06三维及不含镜宽度来源未闭合
138319	138319	Sedan	Cruze I	J300	4		LOW	Cruze I市场与改款外廓尚未闭合	PENDING: Cruze I市场与改款外廓尚未闭合
138333	138333	Hatchback	i10 I Facelift	PA	5		LOW	i10 I改款外廓三维未闭合	PENDING: i10 I改款外廓三维未闭合
138351	138351	Van	Berlingo II	B9			LOW	Van/MPV及高度分支未闭合	PENDING: Van/MPV及高度分支未闭合
138352	138352	Van	Partner II	B9			LOW	Van/MPV及高度分支未闭合	PENDING: Van/MPV及高度分支未闭合
138353	138353	MPV	Berlingo II	B9			LOW	MPV标准/Outdoor高度分支未闭合	PENDING: MPV标准/Outdoor高度分支未闭合
138354	138354	MPV	Partner II	B9			LOW	MPV标准/Outdoor高度分支未闭合	PENDING: MPV标准/Outdoor高度分支未闭合
138356	138356	Hatchback	i30 II	GD	5		LOW	i30 II掀背外廓三维未闭合	PENDING: i30 II掀背外廓三维未闭合
138357	138357	Wagon	i30 II	GD	5		LOW	i30 II旅行车商用外廓三维未闭合	PENDING: i30 II旅行车商用外廓三维未闭合
138360	138360	Hatchback	i30 II	GD	5		LOW	i30 II掀背商用外廓三维未闭合	PENDING: i30 II掀背商用外廓三维未闭合
138405	138405	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138406	138406	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138407	138407	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138414	138414	Wagon	A6 allroad IV	C8	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
138429	138429	Sedan	Pride I		4		LOW	Pride轿车代际与三维来源未闭合	PENDING: Pride轿车代际与三维来源未闭合
138446	138446	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138447	138447	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138449	138449	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138450	138450	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138451	138451	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138452	138452	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	HIGH		READY
138460	138460	SUV	ix35 Facelift	LM	5	EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	HIGH		READY
138488	138488	MPV	Proace II	MDZ4			LOW	Proace Verso Medium/Long分支未闭合	PENDING: Proace Verso Medium/Long分支未闭合
138490	138490	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	MEDIUM	Kasten/Schrägheck沿用Astra K五门外廓。	READY
138493	138493	Pickup	Master III Facelift	X62			LOW	L2/L3及单排/双排驾驶室分支未闭合	PENDING: L2/L3及单排/双排驾驶室分支未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494	Automobile-Catalog 2017 Mercedes-Benz GLA 250	https://www.automobile-catalog.com/car/2017/2025710/mercedes-benz_gla_250.html
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247;Automobile-Catalog Mercedes-Benz B 200 d W247	https://www.auto-data.net/en/mercedes-benz-b-class-model-1363;https://www.automobile-catalog.com/car/2019/2795615/mercedes-benz_b_200_d_8g-dct.html
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault Clio V Phase 1 dimensions	https://www.renault.mu/cars/NouvelleCLIObjaPh1/dimensionsandspecifications.html
EU-BMW-2-F87-M2-CS-COUPE-01	4461	1871	1414	BMW M2 CS technical data	https://www.press.bmwgroup.com/global/article/attachment/T0302261EN/441458
EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	4506	1851	1602	Audi RS Q3 dimension drawing	https://www.audi.com/en/publications/dimensions/dimensions-rs-q3-1433/download
EU-AUDI-A7-C8-RS7-SPORTBACK-01	5009	1950	1424	Audi RS 7 Sportback dimension drawing 09/2019	https://www.audi.com/en/publications/dimensions/dimensions-rs-7-sportback-1432/download
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460	Audi RS 6 Avant dimension drawing 08/2019	https://www.audi.com/en/publications/dimensions/dimensions-rs-6-avant-1431/download
```

## 下一步优先处理

1. 利用现有 X82、W447、K9、V363、X62 缓存，优先拆解 Trafic、Vivaro、Vito、Talento、Combo、Transit、Movano、Master 的轴距、车顶和驾驶室分支。
2. 闭合 Transporter T6.1、Caddy IV、Grand California 的 SWB/LWB、600/680、Van/MPV 与底盘分支。
3. 处理 Alfa Romeo Quadrifoglio、Mazda2、Corvette C5 Z06、Cruze、i10、i30、Pride 等剩余乘用车型尺寸组。
4. 最后处理 Berlingo/Partner、L200 和 Proace 的多外廓派生行，避免为同一物理车身重复建组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2017/2025710/mercedes-benz_gla_250.html?utm_source=chatgpt.com "2017 Mercedes-Benz GLA 250 Specs Review (155 kW ..."
[2]: https://www.media.stellantis.com/us-en/maserati/press/maserati-levante-my19-press-kit-2?utm_source=chatgpt.com "Maserati Levante MY19 Press Kit | Maserati | Stellantis Media"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 将 `138074` 拆分为 Vivaro B 的 L1H1、L1H2、L2H1、L2H2 四个确定物理分支；官方尺寸图明确给出不含后视镜宽度 1956 mm。由于长度与现有 Trafic 缓存相差 1 mm，本轮新建 Opel 专属尺寸组，未覆盖既有组。
* 将 Grand California 前驱 `138085` 拆分为 600、680；四驱 `138086` 闭合为 680 分支，并首次建立两套尺寸组。
* `138108`、`138131`、`138133`、`138134` 按 Compact、Long、Extra-long 拆分，直接复用已有 W447 三个尺寸组。
* 闭合 7 个 Fiat Talento Ktype：低顶和平台底盘复用现有 X82 缓存，仅首次创建 L1H2、L2H2 两个高顶尺寸组。
* `138488` 拆分为 Proace Verso Medium、Long，直接复用现有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：65
* PENDING Ktype：35
* READY 映射行：87
* PENDING 映射行：35
* 当前映射总行数：122
* 当前已引用尺寸组：49
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138074_l1h1	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138074_l1h2	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138074_l2h1	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138074_l2h2	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138085_600	138085	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-600-01	HIGH	600物理分支。	READY
138085_680	138085	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	HIGH	680物理分支。	READY
138086_680	138086	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	HIGH	680 4Motion物理分支。	READY
138108_compact	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138108_long	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138108_extralong	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138131_compact	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138131_long	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138131_extralong	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138133_compact	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138133_long	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138133_extralong	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138134_compact	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138134_long	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138134_extralong	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138286_l1h1	138286	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138286_l2h1	138286	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138287_l1h1	138287	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138287_l1h2	138287	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138287_l2h1	138287	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138287_l2h2	138287	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138288_l1h1	138288	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138288_l1h2	138288	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138288_l2h1	138288	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138288_l2h2	138288	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138289	138289	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	HIGH	L2平台底盘物理分支。	READY
138291	138291	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	HIGH	L2平台底盘物理分支。	READY
138292_l1h1	138292	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138292_l2h1	138292	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138294_l1h1	138294	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138294_l2h1	138294	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138488_medium	138488	MPV	Proace II	MDZ4		EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium物理分支。	READY
138488_long	138488	MPV	Proace II	MDZ4		EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	4998	1956	1971	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	4998	1956	2465	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	5398	1956	1971	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	5398	1956	2465	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-VW-GRAND-CALIFORNIA-I-MPV-600-01	5986	2040	2971	Volkswagen Grand California 600 official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/grand-california/GrandCalifornia-600.pdf
EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	6836	2040	2839	Volkswagen Grand California 680 official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/grand-california/GrandCalifornia-680.pdf
EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	4999	1956	2493	Fiat Talento official technical data	https://www.media.stellantis.com/uploads/de/model-document/201209_tdfiattalento-5fd115a4383d6.pdf
EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	5399	1956	2490	Fiat Talento official technical data	https://www.media.stellantis.com/uploads/de/model-document/201209_tdfiattalento-5fd115a4383d6.pdf
```

## 下一步优先处理

1. 闭合 Transporter T6.1、Caddy IV、Vito Mixto、Combo E 的轴距、车顶和用途分支。
2. 集中处理 Transit V363、Movano B、Master III 的 L/H、驾驶室及 SRW/DRW 分支。
3. 补齐 Alfa Romeo Quadrifoglio、Mazda2、Corvette C5 Z06、Cruze、i10、i30、Pride 等乘用车型。
4. 最后处理 L200、Berlingo/Partner 多用途车身分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮消除 13 个 PENDING Ktype：Trafic III、Vito Mixto、Transit Van、L200、Mazda2、Partner II 和 i30 II。
* Trafic、Vito、Transit、L200、Partner 共复用 23 个既有尺寸组，未重复输出尺寸事实或来源。
* Mazda2 两个动力 Ktype 共用新尺寸组；官方 2020 规格给出 4070 × 1695 × 1515 mm，并明确宽度不含后视镜。
* i30 II Facelift 的 Hatchback 与 Wagon 分别建立尺寸组；官方尺寸图给出 4300/4485 × 1780 × 1470/1500 mm。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：78
* PENDING Ktype：22
* READY 映射行：124
* PENDING 映射行：22
* 当前映射总行数：146
* 当前已引用尺寸组：68
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138027_l1h1	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138027_l1h2	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138027_l2h1	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138027_l2h2	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138028_l1h1	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138028_l1h2	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138028_l2h1	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138028_l2h2	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138135_compact	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138135_long	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138135_extralong	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138136_compact	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138136_long	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138136_extralong	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138181_l2h2	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	HIGH	L2H2 RWD物理分支。	READY
138181_l2h3	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	HIGH	L2H3 RWD物理分支。	READY
138181_l3h2	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	HIGH	L3H2 RWD物理分支。	READY
138181_l3h3	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	HIGH	L3H3 RWD物理分支。	READY
138181_l4h3_srw	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	HIGH	L4H3 RWD SRW物理分支。	READY
138181_l4h3_drw	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	HIGH	L4H3 RWD DRW物理分支。	READY
138182_l2h2	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	HIGH	L2H2 FWD物理分支。	READY
138182_l2h3	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	HIGH	L2H3 FWD物理分支。	READY
138182_l3h2	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	HIGH	L3H2 FWD物理分支。	READY
138182_l3h3	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	HIGH	L3H3 FWD物理分支。	READY
138199_clubcab	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	HIGH	Club Cab物理分支。	READY
138199_doublecab_standard	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	HIGH	Double Cab标准后保险杠分支。	READY
138199_doublecab_stepbumper	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	HIGH	Double Cab踏步后保险杠分支。	READY
138223	138223	Hatchback	Mazda2 III Facelift	DJ	5	EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	HIGH		READY
138224	138224	Hatchback	Mazda2 III Facelift	DJ	5	EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	HIGH		READY
138352_van_l1	138352	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	HIGH	L1 Van物理分支。	READY
138352_van_l2	138352	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	HIGH	L2 Van物理分支。	READY
138352_mpv_standard	138352	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	标准高度MPV分支。	READY
138352_mpv_outdoor	138352	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor高度MPV分支。	READY
138354_mpv_standard	138354	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	标准高度MPV分支。	READY
138354_mpv_outdoor	138354	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor高度MPV分支。	READY
138357	138357	Wagon	i30 II Facelift	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	HIGH	Kasten/Kombi沿用五门Wagon外廓。	READY
138360	138360	Hatchback	i30 II Facelift	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck沿用五门Hatchback外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	4070	1695	1515	Mazda UK 2020 Mazda2 Price and Specification Guide	https://uk.cdn.mazda.media/c6bcf7e1072a457780b0ff1e9379bfc0/8445b5bc950340dd9b0c7e2021c9fec5.pdf
EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	4485	1780	1500	Hyundai Motor Europe New i30 official brochure	https://www.hyundai.ie/assets/car/i30-face-lift/files/hyundai-i30-12-pager.pdf
EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	4300	1780	1470	Hyundai Motor Europe New i30 official brochure	https://www.hyundai.ie/assets/car/i30-face-lift/files/hyundai-i30-12-pager.pdf
```

## 下一步优先处理

1. 闭合 Transporter T6.1、Caddy IV、Combo E 的轴距、车顶及 Van/MPV 分支。
2. 处理 Transit、Movano、Master 的平台底盘、驾驶室与 SRW/DRW 分支。
3. 补齐 Giulia/Stelvio Quadrifoglio、Corvette C5 Z06、Cruze、i10、i30 前期型和 Pride。
4. 最后闭合 Citroën Berlingo B9 的 Van/MPV 高度分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Alfa Romeo Stelvio/Giulia Quadrifoglio 两个专属宽体外廓，并分别建立独立尺寸组。([Stellantis Media][1])
* 将 Hyundai i10 I 按改款前、改款后拆成两个物理分支；同时闭合 i30 II 改款前 Hatchback。([汽车数据网][2])
* 闭合 Corvette C5 Z06 与 Chevrolet Cruze I Facelift 尺寸组。([Edmunds][3])
* 基于 X62 已确认配置，批量闭合 Movano B Facelift Van、Movano底盘及 Master III Facelift 底盘分支；单排底盘复用既有组，仅新增缺失的 Van 与双排底盘尺寸组。([Manuals+][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* PENDING Ktype：13
* READY 映射行：145
* PENDING 映射行：13
* 当前映射总行数：158
* 当前已引用尺寸组：85
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138149	138149	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-QUADRIFOGLIO-01	HIGH		READY
138152	138152	Sedan	Giulia	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-QUADRIFOGLIO-01	HIGH		READY
138233_l1h1	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L1H1-FWD-FACELIFT-01	MEDIUM	L1H1前驱物理分支。	READY
138233_l1h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L1H2-FWD-FACELIFT-01	MEDIUM	L1H2前驱物理分支。	READY
138233_l2h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L2H2-FWD-FACELIFT-01	MEDIUM	L2H2前驱物理分支。	READY
138233_l2h3	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L2H3-FWD-FACELIFT-01	MEDIUM	L2H3前驱物理分支。	READY
138233_l3h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	MEDIUM	L3H2前驱物理分支。	READY
138233_l3h3	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H3-FWD-FACELIFT-01	MEDIUM	L3H3前驱物理分支。	READY
138234_scab_l2	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	MEDIUM	L2单排驾驶室物理分支。	READY
138234_scab_l3	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	MEDIUM	L3单排驾驶室物理分支。	READY
138234_dcab_l2	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	MEDIUM	L2双排驾驶室物理分支。	READY
138234_dcab_l3	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	MEDIUM	L3双排驾驶室物理分支。	READY
138300	138300	Coupe	Corvette C5	C5	2	EU-CHEVROLET-CORVETTE-C5-Z06-COUPE-01	HIGH		READY
138319	138319	Sedan	Cruze I Facelift	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-FACELIFT-01	MEDIUM	2013改款轿车外廓。	READY
138333_prefl	138333	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
138333_facelift	138333	Hatchback	i10 I Facelift	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
138356	138356	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	HIGH		READY
138493_scab_l2	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	HIGH	L2单排驾驶室物理分支。	READY
138493_scab_l3	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	HIGH	L3单排驾驶室物理分支。	READY
138493_dcab_l2	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	HIGH	L2双排驾驶室物理分支。	READY
138493_dcab_l3	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	HIGH	L3双排驾驶室物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-STELVIO-949-SUV-QUADRIFOGLIO-01	4702	1955	1681	Alfa Romeo Stelvio Quadrifoglio official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-new-alfa-romeo-stelvio-quadrifoglio-1
EU-ALFA-ROMEO-GIULIA-952-SEDAN-QUADRIFOGLIO-01	4639	1874	1433	Auto-Data Alfa Romeo Giulia Quadrifoglio	https://www.auto-data.net/en/alfa-romeo-giulia-952-quadrifoglio-2.9-v6-biturbo-510hp-automatic-36547
EU-OPEL-MOVANO-B-X62-VAN-L1H1-FWD-FACELIFT-01	5075	2070	2307	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L1H2-FWD-FACELIFT-01	5075	2070	2500	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L2H2-FWD-FACELIFT-01	5575	2070	2499	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L2H3-FWD-FACELIFT-01	5575	2070	2749	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	6225	2070	2488	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L3H3-FWD-FACELIFT-01	6225	2070	2744	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2272	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2263	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-CHEVROLET-CORVETTE-C5-Z06-COUPE-01	4564	1869	1212	Edmunds 2004 Chevrolet Corvette Z06 specifications	https://www.edmunds.com/chevrolet/corvette/2004/coupe/st-100274087/features-specs/
EU-CHEVROLET-CRUZE-I-J300-SEDAN-FACELIFT-01	4603	1797	1477	Auto-Data Chevrolet Cruze Sedan Facelift 2013	https://www.auto-data.net/en/chevrolet-cruze-sedan-facelift-2013-generation-4230
EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.2	https://www.auto-data.net/en/hyundai-i10-i-1.2-78hp-13881
EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I Facelift 2011	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787
EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	4300	1780	1470	Auto-Data Hyundai i30 II 1.4	https://www.auto-data.net/en/hyundai-i30-ii-1.4-100hp-18534
```

## 下一步优先处理

1. Transporter T6.1 的五个 Van、平台底盘及 4Motion 物理分支。
2. Caddy IV、Combo E 与 Berlingo B9 的 Van/MPV、轴距和高度分支。
3. Transit V363 平台底盘与 Movano B Bus 分支。
4. Kia Pride Sedan 历史车型尺寸组。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-new-alfa-romeo-stelvio-quadrifoglio-1?utm_source=chatgpt.com "THE NEW ALFA ROMEO STELVIO QUADRIFOGLIO"
[2]: https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787 "Hyundai i10 I (facelift 2011) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.edmunds.com/chevrolet/corvette/2004/coupe/st-100274087/features-specs/ "Used 2004 Chevrolet Corvette Coupe Z06 Specs & Features | Edmunds"
[4]: https://manuals.plus/m/7176f791cec58966c57c221ac6417767d7d86b071318cbbebca9b9f049c69a14 "manuals.plus"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Transporter T6.1 的 5 个 Ktype：厢式车拆为 SWB 低顶、LWB 低顶、LWB 高顶；平台车拆为 SWB 单排、LWB 单排、LWB 双排。官方尺寸图确认厢式车三种外廓及平台车单排、双排外廓。
* 闭合 Caddy IV 的 Van SWB/LWB 与 MPV SWB/LWB；Van 两个分支首次建组，MPV 分支复用现有组。官方 2019 规格明确 Van 的不含后视镜宽度及两种长度、高度。
* 闭合 Berlingo B9 的 Van、MPV 分支，全部复用现有 Partner II B9 同外廓尺寸组。
* 闭合 Kia Pride Beta 四门 Sedan，首次建立尺寸组。
* 本轮未处理已闭合尺寸组的三维或来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* PENDING Ktype：4
* 本轮消除 PENDING：9
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138017_scab_swb	138017	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138017_scab_lwb	138017	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138017_dcab_lwb	138017	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138018_scab_swb	138018	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138018_scab_lwb	138018	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138018_dcab_lwb	138018	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138019_swb_lowroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	SWB低顶物理分支。	READY
138019_lwb_lowroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	LWB低顶物理分支。	READY
138019_lwb_highroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶物理分支。	READY
138020_scab_swb	138020	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138020_scab_lwb	138020	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138020_dcab_lwb	138020	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138021_scab_swb	138021	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138021_scab_lwb	138021	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138021_dcab_lwb	138021	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138026_van_swb	138026	Van	Caddy IV	2K		EU-VW-CADDY-IV-VAN-SWB-01	HIGH	SWB Van物理分支。	READY
138026_van_lwb	138026	Van	Caddy IV	2K		EU-VW-CADDY-IV-VAN-LWB-01	HIGH	LWB Van物理分支。	READY
138026_mpv_swb	138026	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	HIGH	SWB MPV物理分支。	READY
138026_mpv_lwb	138026	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-LWB-01	HIGH	LWB MPV物理分支。	READY
138351_van_l1	138351	Van	Berlingo II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1 Van物理分支。	READY
138351_van_l2	138351	Van	Berlingo II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2 Van物理分支。	READY
138351_mpv_standard	138351	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度MPV物理分支。	READY
138351_mpv_outdoor	138351	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor高度MPV物理分支。	READY
138353_standard	138353	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度MPV物理分支。	READY
138353_outdoor	138353	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor高度MPV物理分支。	READY
138429	138429	Sedan	Pride I Beta		4	EU-KIA-PRIDE-I-BETA-SEDAN-01	MEDIUM	四门Beta Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	5100	1994	1948	Volkswagen Transporter 6.1 Pritschenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-EK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	5500	1994	1948	Volkswagen Transporter 6.1 Pritschenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-EK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	5500	1994	1960	Volkswagen Transporter 6.1 Doppelkabine official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-DK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-HIGHROOF-01	5304	1904	2477	Volkswagen Transporter 6.1 Kastenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf
EU-VW-CADDY-IV-VAN-SWB-01	4408	1793	1823	Volkswagen Caddy Panel Van MY2020 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-VW-CADDY-IV-VAN-LWB-01	4878	1793	1836	Volkswagen Caddy Panel Van MY2020 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-KIA-PRIDE-I-BETA-SEDAN-01	3935	1605	1460	Automobile-Catalog Kia Pride Beta 1.3i specifications	https://www.automobile-catalog.com/car/1999/1340540/kia_pride_beta_1_3i.html
```

## 下一步优先处理

1. 闭合 `138153` Combo E 的 Van M/XL 与 Life MPV 分支。
2. 闭合 `138215`、`138216` Transit V363 平台底盘的驾驶室、轴距及 SRW/DRW 分支。
3. 闭合 `138232` Movano B Bus 的 L/H 分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* `138153` 已拆分为 Combo E 的 Van M、Van XL、Life M、Life XL 四个物理分支，全部直接复用现有尺寸组。
* `138232` 已闭合为 Movano B Facelift L3H2 Bus，复用现有 L3H2 FWD Facelift 车身尺寸组。
* `138216` 已闭合为 Transit V363 L3 双排驾驶室 RWD 的 SRW、DRW 两个分支；2019 年型目录确认 185PS RWD 双排 L3 配置，尺寸采用 Ford Transit Chassis Cab 官方尺寸表。([Scribd][1])
* `138215` 仍保持 PENDING：已核对的 2019 年型目录没有闭合 185PS FWD 底盘对应的轴距和驾驶室范围，不能依据其他功率版本直接派生。([Scribd][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* 本轮消除 PENDING：3
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138153_van_m	138153	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	HIGH	M轴距Van物理分支。	READY
138153_van_xl	138153	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	HIGH	XL轴距Van物理分支。	READY
138153_mpv_m	138153	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	HIGH	M轴距Life MPV物理分支。	READY
138153_mpv_xl	138153	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	HIGH	XL轴距Life MPV物理分支。	READY
138215	138215	Pickup	Transit V363	V363			LOW	185PS FWD底盘的轴距与驾驶室适用范围未闭合。	PENDING: 185PS FWD底盘适用分支未闭合
138216_dcab_l3_srw	138216	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-SRW-01	HIGH	L3双排驾驶室RWD SRW物理分支。	READY
138216_dcab_l3_drw	138216	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-DRW-01	HIGH	L3双排驾驶室RWD DRW物理分支。	READY
138232_l3h2	138232	MPV	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	MEDIUM	L3H2 Bus物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-SRW-01	6022	2066	2218	Ford Transit Chassis Cab official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_chassis.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-DRW-01	6022	2111	2218	Ford Transit Chassis Cab official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_chassis.pdf
```

## 下一步优先处理

1. 仅处理 `138215`：核对欧洲市场 2019–2024 Transit V363 185PS FWD 平台底盘的正式型谱，确认其轴距和单排/双排驾驶室边界。
2. 闭合后立即进行一次机械收尾并输出两张最终完整 TSV、两个指定 sandbox 下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/421054714/PL-Transit-Chassis-Cab-pdf "Customer Ordering Guide and Price List: Transit Chassis Cab | PDF | Truck | Value Added Tax"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后一个 PENDING Ktype `138215` 已闭合为 Transit V363 前驱底盘的单排 L2/L3/L4、双排 L2/L3 五个物理分支。Ford 资料明确列出 185 PS 发动机适用于 Single Cab 与 Double Cab，并分别提供单排和双排底盘尺寸。([AnyRent Storage][1])
* 已完成一次机械收尾：固定表头、`id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用闭合、尺寸与来源非空、无孤立尺寸组。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：183
* 最终尺寸组：109
* 映射缺失引用：0
* 孤立尺寸组：0
* 机械校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138001	138001	SUV	GLA I	X156	5	EU-MERCEDES-BENZ-GLA-X156-SUV-01	HIGH		READY
138017_scab_swb	138017	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138017_scab_lwb	138017	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138017_dcab_lwb	138017	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138018_scab_swb	138018	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138018_scab_lwb	138018	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138018_dcab_lwb	138018	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138019_swb_lowroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	HIGH	SWB低顶物理分支。	READY
138019_lwb_lowroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	HIGH	LWB低顶物理分支。	READY
138019_lwb_highroof	138019	Van	Transporter T6.1	T6.1		EU-VW-TRANSPORTER-T6-1-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶物理分支。	READY
138020_scab_swb	138020	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138020_scab_lwb	138020	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138020_dcab_lwb	138020	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138021_scab_swb	138021	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	HIGH	SWB单排驾驶室物理分支。	READY
138021_scab_lwb	138021	Pickup	Transporter T6.1	T6.1	2	EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	HIGH	LWB单排驾驶室物理分支。	READY
138021_dcab_lwb	138021	Pickup	Transporter T6.1	T6.1	4	EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	HIGH	LWB双排驾驶室物理分支。	READY
138023	138023	SUV	Seltos I		5	EU-KIA-SELTOS-I-SUV-4WD-01	MEDIUM	前驱与四驱共用车身外廓。	READY
138026_van_swb	138026	Van	Caddy IV	2K		EU-VW-CADDY-IV-VAN-SWB-01	HIGH	SWB Van物理分支。	READY
138026_van_lwb	138026	Van	Caddy IV	2K		EU-VW-CADDY-IV-VAN-LWB-01	HIGH	LWB Van物理分支。	READY
138026_mpv_swb	138026	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-SWB-01	HIGH	SWB MPV物理分支。	READY
138026_mpv_lwb	138026	MPV	Caddy IV	2K	5	EU-VW-CADDY-IV-MPV-LWB-01	HIGH	LWB MPV物理分支。	READY
138027_l1h1	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138027_l1h2	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138027_l2h1	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138027_l2h2	138027	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138028_l1h1	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138028_l1h2	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138028_l2h1	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138028_l2h2	138028	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138068	138068	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
138071	138071	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
138072	138072	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
138073	138073	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
138074_l1h1	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138074_l1h2	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138074_l2h1	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138074_l2h2	138074	Van	Vivaro B	X82		EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138081	138081	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138082	138082	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138083	138083	Sedan	A-Class IV	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	HIGH		READY
138085_600	138085	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-600-01	HIGH	600物理分支。	READY
138085_680	138085	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	HIGH	680物理分支。	READY
138086_680	138086	MPV	Grand California I			EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	HIGH	680 4Motion物理分支。	READY
138089	138089	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH		READY
138092	138092	SUV	Levante I		5	EU-MASERATI-LEVANTE-I-SUV-01	MEDIUM	Trofeo沿用Levante I车身外廓。	READY
138108_compact	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138108_long	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138108_extralong	138108	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138109	138109	Wagon	CLA II	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
138110	138110	Wagon	CLA II	X118	5	EU-MERCEDES-BENZ-CLA-X118-WAGON-01	HIGH		READY
138119	138119	MPV	Lodgy I		5	EU-DACIA-LODGY-MPV-01	HIGH		READY
138120	138120	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	HIGH		READY
138121	138121	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138122	138122	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138123	138123	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138124	138124	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138125	138125	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X4-01	MEDIUM	Renault与Dacia版本共用Duster II四驱外廓。	READY
138126	138126	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	MEDIUM	Renault与Dacia版本共用Duster II前驱外廓。	READY
138128	138128	Hatchback	6 Series Gran Turismo	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
138130	138130	Coupe	M2	F87	2	EU-BMW-2-F87-M2-CS-COUPE-01	HIGH		READY
138131_compact	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138131_long	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138131_extralong	138131	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138133_compact	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138133_long	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138133_extralong	138133	MPV	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138134_compact	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138134_long	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138134_extralong	138134	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138135_compact	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138135_long	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138135_extralong	138135	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138136_compact	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	HIGH	Compact物理分支。	READY
138136_long	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-LONG-01	HIGH	Long物理分支。	READY
138136_extralong	138136	Van	Vito III	W447		EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	HIGH	Extra-long物理分支。	READY
138149	138149	SUV	Stelvio I	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-QUADRIFOGLIO-01	HIGH		READY
138152	138152	Sedan	Giulia	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-QUADRIFOGLIO-01	HIGH		READY
138153_van_m	138153	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	HIGH	M轴距Van物理分支。	READY
138153_van_xl	138153	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	HIGH	XL轴距Van物理分支。	READY
138153_mpv_m	138153	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	HIGH	M轴距Life MPV物理分支。	READY
138153_mpv_xl	138153	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	HIGH	XL轴距Life MPV物理分支。	READY
138164	138164	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
138181_l2h2	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	HIGH	L2H2 RWD物理分支。	READY
138181_l2h3	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	HIGH	L2H3 RWD物理分支。	READY
138181_l3h2	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	HIGH	L3H2 RWD物理分支。	READY
138181_l3h3	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	HIGH	L3H3 RWD物理分支。	READY
138181_l4h3_srw	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	HIGH	L4H3 RWD SRW物理分支。	READY
138181_l4h3_drw	138181	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	HIGH	L4H3 RWD DRW物理分支。	READY
138182_l2h2	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	HIGH	L2H2 FWD物理分支。	READY
138182_l2h3	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-01	HIGH	L2H3 FWD物理分支。	READY
138182_l3h2	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	HIGH	L3H2 FWD物理分支。	READY
138182_l3h3	138182	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	HIGH	L3H3 FWD物理分支。	READY
138184	138184	Hatchback	Mini III	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	HIGH		READY
138191	138191	SUV	C-HR I	AX10	5	EU-TOYOTA-C-HR-I-AX10-SUV-01	HIGH		READY
138199_clubcab	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	HIGH	Club Cab物理分支。	READY
138199_doublecab_standard	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	HIGH	Double Cab标准后保险杠分支。	READY
138199_doublecab_stepbumper	138199	Pickup	L200 V Facelift			EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	HIGH	Double Cab踏步后保险杠分支。	READY
138210	138210	SUV	C5 Aircross I	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
138215_scab_l2	138215	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	HIGH	L2单排驾驶室FWD物理分支。	READY
138215_scab_l3	138215	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	HIGH	L3单排驾驶室FWD物理分支。	READY
138215_scab_l4	138215	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	HIGH	L4单排驾驶室FWD物理分支。	READY
138215_dcab_l2	138215	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L2-FWD-01	HIGH	L2双排驾驶室FWD物理分支。	READY
138215_dcab_l3	138215	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-FWD-01	HIGH	L3双排驾驶室FWD物理分支。	READY
138216_dcab_l3_srw	138216	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-SRW-01	HIGH	L3双排驾驶室RWD SRW物理分支。	READY
138216_dcab_l3_drw	138216	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-DRW-01	HIGH	L3双排驾驶室RWD DRW物理分支。	READY
138218	138218	Coupe	911 VIII	992	2	EU-PORSCHE-911-992-CARRERA-COUPE-01	HIGH	Carrera 4与Carrera共用992标准车身外廓。	READY
138219	138219	Convertible	911 VIII	992	2	EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	HIGH	Carrera 4与Carrera共用992标准敞篷外廓。	READY
138223	138223	Hatchback	Mazda2 III Facelift	DJ	5	EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	HIGH		READY
138224	138224	Hatchback	Mazda2 III Facelift	DJ	5	EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	HIGH		READY
138228	138228	Hatchback	208 I Facelift	A9	5	EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	HIGH		READY
138230	138230	Sedan	A8 IV	D5	4	EU-AUDI-A8-D5-SEDAN-01	HIGH		READY
138232_l3h2	138232	MPV	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	MEDIUM	L3H2 Bus物理分支。	READY
138233_l1h1	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L1H1-FWD-FACELIFT-01	MEDIUM	L1H1前驱物理分支。	READY
138233_l1h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L1H2-FWD-FACELIFT-01	MEDIUM	L1H2前驱物理分支。	READY
138233_l2h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L2H2-FWD-FACELIFT-01	MEDIUM	L2H2前驱物理分支。	READY
138233_l2h3	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L2H3-FWD-FACELIFT-01	MEDIUM	L2H3前驱物理分支。	READY
138233_l3h2	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	MEDIUM	L3H2前驱物理分支。	READY
138233_l3h3	138233	Van	Movano B Facelift	X62		EU-OPEL-MOVANO-B-X62-VAN-L3H3-FWD-FACELIFT-01	MEDIUM	L3H3前驱物理分支。	READY
138234_scab_l2	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	MEDIUM	L2单排驾驶室物理分支。	READY
138234_scab_l3	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	MEDIUM	L3单排驾驶室物理分支。	READY
138234_dcab_l2	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	MEDIUM	L2双排驾驶室物理分支。	READY
138234_dcab_l3	138234	Pickup	Movano B Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	MEDIUM	L3双排驾驶室物理分支。	READY
138237	138237	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	HIGH		READY
138240	138240	Convertible	A5 II Facelift	F5	2	EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	HIGH		READY
138242	138242	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138272	138272	Wagon	A4 allroad B9	B9	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
138273	138273	SUV	Q7 II Facelift	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH		READY
138274	138274	Hatchback	A7 II	C8	5	EU-AUDI-A7-C8-RS7-SPORTBACK-01	HIGH		READY
138275	138275	Wagon	A6 V	C8	5	EU-AUDI-A6-C8-RS6-AVANT-01	HIGH		READY
138286_l1h1	138286	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138286_l2h1	138286	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138287_l1h1	138287	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138287_l1h2	138287	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138287_l2h1	138287	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138287_l2h2	138287	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138288_l1h1	138288	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138288_l1h2	138288	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	HIGH	L1H2物理分支。	READY
138288_l2h1	138288	Van	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138288_l2h2	138288	Van	Talento II	X82		EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	HIGH	L2H2物理分支。	READY
138289	138289	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	HIGH	L2平台底盘物理分支。	READY
138291	138291	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	HIGH	L2平台底盘物理分支。	READY
138292_l1h1	138292	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138292_l2h1	138292	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138294_l1h1	138294	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1物理分支。	READY
138294_l2h1	138294	MPV	Talento II	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1物理分支。	READY
138300	138300	Coupe	Corvette C5	C5	2	EU-CHEVROLET-CORVETTE-C5-Z06-COUPE-01	HIGH		READY
138319	138319	Sedan	Cruze I Facelift	J300	4	EU-CHEVROLET-CRUZE-I-J300-SEDAN-FACELIFT-01	MEDIUM	2013改款轿车外廓。	READY
138333_prefl	138333	Hatchback	i10 I	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	HIGH	改款前物理外廓。	READY
138333_facelift	138333	Hatchback	i10 I Facelift	PA	5	EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	HIGH	改款后物理外廓。	READY
138351_van_l1	138351	Van	Berlingo II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	L1 Van物理分支。	READY
138351_van_l2	138351	Van	Berlingo II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	MEDIUM	L2 Van物理分支。	READY
138351_mpv_standard	138351	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度MPV物理分支。	READY
138351_mpv_outdoor	138351	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor高度MPV物理分支。	READY
138352_van_l1	138352	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	HIGH	L1 Van物理分支。	READY
138352_van_l2	138352	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	HIGH	L2 Van物理分支。	READY
138352_mpv_standard	138352	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	标准高度MPV分支。	READY
138352_mpv_outdoor	138352	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor高度MPV分支。	READY
138353_standard	138353	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	MEDIUM	标准高度MPV物理分支。	READY
138353_outdoor	138353	MPV	Berlingo II	B9	5	EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	MEDIUM	Outdoor高度MPV物理分支。	READY
138354_mpv_standard	138354	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	HIGH	标准高度MPV分支。	READY
138354_mpv_outdoor	138354	MPV	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	HIGH	Outdoor高度MPV分支。	READY
138356	138356	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	HIGH		READY
138357	138357	Wagon	i30 II Facelift	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	HIGH	Kasten/Kombi沿用五门Wagon外廓。	READY
138360	138360	Hatchback	i30 II Facelift	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	HIGH	Kasten/Schrägheck沿用五门Hatchback外廓。	READY
138405	138405	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138406	138406	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138407	138407	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138414	138414	Wagon	A6 allroad IV	C8	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH		READY
138429	138429	Sedan	Pride I Beta		4	EU-KIA-PRIDE-I-BETA-SEDAN-01	MEDIUM	四门Beta Sedan外廓。	READY
138446	138446	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138447	138447	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138449	138449	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138450	138450	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138451	138451	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138452	138452	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	HIGH		READY
138460	138460	SUV	ix35 Facelift	LM	5	EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	HIGH		READY
138488_medium	138488	MPV	Proace II	MDZ4		EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	HIGH	Medium物理分支。	READY
138488_long	138488	MPV	Proace II	MDZ4		EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	HIGH	Long物理分支。	READY
138490	138490	Hatchback	Astra K	B16	5	EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	MEDIUM	Kasten/Schrägheck沿用Astra K五门外廓。	READY
138493_scab_l2	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	HIGH	L2单排驾驶室物理分支。	READY
138493_scab_l3	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	HIGH	L3单排驾驶室物理分支。	READY
138493_dcab_l2	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	HIGH	L2双排驾驶室物理分支。	READY
138493_dcab_l3	138493	Pickup	Master III Facelift	X62		EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	HIGH	L3双排驾驶室物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4401-4500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLA-X156-SUV-01	4417	1804	1494	Automobile-Catalog 2017 Mercedes-Benz GLA 250	https://www.automobile-catalog.com/car/2017/2025710/mercedes-benz_gla_250.html
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-SWB-01	5100	1994	1948	Volkswagen Transporter 6.1 Pritschenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-EK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-PICKUP-SCAB-LWB-01	5500	1994	1948	Volkswagen Transporter 6.1 Pritschenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-EK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-PICKUP-DCAB-LWB-01	5500	1994	1960	Volkswagen Transporter 6.1 Doppelkabine official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-DK-Pritsche-PrEco.pdf
EU-VW-TRANSPORTER-T6-1-VAN-SWB-LOWROOF-4MOTION-01	4904	1904	1990	Volkswagen Transporter 6.1 Kastenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-LOWROOF-4MOTION-01	5304	1904	1990	Volkswagen Transporter 6.1 Kastenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf
EU-VW-TRANSPORTER-T6-1-VAN-LWB-HIGHROOF-01	5304	1904	2477	Volkswagen Transporter 6.1 Kastenwagen official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/transporter/Transporter-6-1-Kastenwagen-KaEcoProfi.pdf
EU-KIA-SELTOS-I-SUV-4WD-01	4375	1800	1620	Kia India Seltos dimensions	https://www.kia.com/content/dam/kia2/in/en/content/seltos-manual/topics/chapter9_1.html
EU-VW-CADDY-IV-VAN-SWB-01	4408	1793	1823	Volkswagen Caddy Panel Van MY2020 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-VW-CADDY-IV-VAN-LWB-01	4878	1793	1836	Volkswagen Caddy Panel Van MY2020 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Caddy Crew Bus official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/december/caddy-crew-bus-online-brochure.pdf
EU-VW-CADDY-IV-MPV-LWB-01	4878	1793	1831	Volkswagen Caddy Crew Bus official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2020/december/caddy-crew-bus-online-brochure.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault Trafic official brochure	https://renault.com.cy/wp-content/uploads/2023/05/RENAULT_TRAFIC_26x20.5_LR.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465	Renault Trafic official brochure	https://renault.com.cy/wp-content/uploads/2023/05/RENAULT_TRAFIC_26x20.5_LR.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault Trafic official brochure	https://renault.com.cy/wp-content/uploads/2023/05/RENAULT_TRAFIC_26x20.5_LR.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465	Renault Trafic official brochure	https://renault.com.cy/wp-content/uploads/2023/05/RENAULT_TRAFIC_26x20.5_LR.pdf
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247	https://www.auto-data.net/en/mercedes-benz-b-class-w247-generation-6764
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440	Auto-Data Mercedes-Benz A-Class W177 A 200 4MATIC	https://www.auto-data.net/en/mercedes-benz-a-class-w177-a-200-163hp-4matic-8g-dct-43726
EU-OPEL-VIVARO-B-X82-VAN-L1H1-01	4998	1956	1971	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L1H2-01	4998	1956	2465	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H1-01	5398	1956	1971	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-OPEL-VIVARO-B-X82-VAN-L2H2-01	5398	1956	2465	Vauxhall Vivaro official brochure September 2015	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_Sept_2015.pdf
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446	Mercedes-Benz A-Class Sedan V177 official brochure	https://www.inghamdriven.nz/mercedes-benz/wp-content/uploads/sites/17/2021/01/a-class-V177-brochure-NZ.pdf
EU-VW-GRAND-CALIFORNIA-I-MPV-600-01	5986	2040	2971	Volkswagen Grand California 600 official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/grand-california/GrandCalifornia-600.pdf
EU-VW-GRAND-CALIFORNIA-I-MPV-680-01	6836	2040	2839	Volkswagen Grand California 680 official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/grand-california/GrandCalifornia-680.pdf
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705	Auto-Data Audi Q8 4M 50 TDI quattro	https://www.auto-data.net/en/audi-q8-4m-50-tdi-v6-286hp-quattro-mild-hybrid-tiptronic-33263
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679	Maserati Levante MY19 official press kit	https://www.media.stellantis.com/us-en/maserati/press/maserati-levante-my19-press-kit-2
EU-MERCEDES-BENZ-VITO-W447-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Tourer official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-LONG-01	5140	1928	1910	Mercedes-Benz Vito Tourer official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-VITO-W447-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Tourer official brochure	https://www.ciceley.com/wp-content/uploads/2024/01/001126-Vito-Tourer-Brochure.pdf
EU-MERCEDES-BENZ-CLA-X118-WAGON-01	4688	1830	1442	Mercedes-Benz CLA Shooting Brake X118 official media release	https://media.mercedes-benz.com/article/f38dfb3b-a7ec-489f-845a-0c88fdaef6fa
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Auto-Data Dacia Lodgy	https://www.auto-data.net/en/dacia-lodgy-generation-3959
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682	Dacia Duster official brochure	https://cdn.group.renault.com/dac/gb/transversal-assets/brochures/model-brochures/Duster-Commercial-eBrochure.pdf.asset.pdf/e61a666a85.pdf
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	Renault Clio V Phase 1 dimensions	https://www.renault.mu/cars/NouvelleCLIObjaPh1/dimensionsandspecifications.html
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	Dacia Duster official brochure	https://cdn.group.renault.com/dac/gb/transversal-assets/brochures/model-brochures/Duster-Commercial-eBrochure.pdf.asset.pdf/e61a666a85.pdf
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	Auto-Data BMW 6 Series Gran Turismo G32 640i	https://www.auto-data.net/en/bmw-6-series-gran-turismo-g32-640i-340hp-steptronic-30562
EU-BMW-2-F87-M2-CS-COUPE-01	4461	1871	1414	BMW M2 CS technical data	https://www.press.bmwgroup.com/global/article/attachment/T0302261EN/441458
EU-ALFA-ROMEO-STELVIO-949-SUV-QUADRIFOGLIO-01	4702	1955	1681	Alfa Romeo Stelvio Quadrifoglio official technical specifications	https://www.media.stellantis.com/uk-en/alfa-romeo/press/the-new-alfa-romeo-stelvio-quadrifoglio-1
EU-ALFA-ROMEO-GIULIA-952-SEDAN-QUADRIFOGLIO-01	4639	1874	1433	Auto-Data Alfa Romeo Giulia Quadrifoglio	https://www.auto-data.net/en/alfa-romeo-giulia-952-quadrifoglio-2.9-v6-biturbo-510hp-automatic-36547
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796	Auto-Data Opel Combo E	https://www.auto-data.net/en/opel-combo-model-238
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812	Auto-Data Opel Combo E	https://www.auto-data.net/en/opel-combo-model-238
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841	Auto-Data Opel Combo E	https://www.auto-data.net/en/opel-combo-model-238
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880	Auto-Data Opel Combo E	https://www.auto-data.net/en/opel-combo-model-238
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531	Auto-Data Skoda Kamiq 1.5 TSI	https://www.auto-data.net/en/skoda-kamiq-1.5-tsi-150hp-36958
EU-FORD-TRANSIT-V363-VAN-L2H2-RWD-01	5531	2059	2542	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L2H3-01	5531	2059	2781	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-RWD-01	5981	2059	2543	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-RWD-01	5981	2059	2782	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-SRW-01	6704	2059	2790	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L4H3-RWD-DRW-01	6704	2126	2790	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2490	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2541	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2780	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432	Auto-Data MINI Electric Cooper SE F56	https://www.auto-data.net/en/mini-electric-cooper-se-f56-generation-7282
EU-TOYOTA-C-HR-I-AX10-SUV-01	4360	1795	1565	Toyota C-HR official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/190107M-CHR-Tech-Spec.pdf
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-CLUBCAB-01	5215	1815	1780	Mitsubishi L200 official brochure	https://www.mitsubishi-motors.co.uk/content/dam/mitsubishi-motors-gb/pdfs/brochures/l200/L200-Brochure.pdf
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STANDARD-01	5225	1815	1780	Mitsubishi L200 official brochure	https://www.mitsubishi-motors.co.uk/content/dam/mitsubishi-motors-gb/pdfs/brochures/l200/L200-Brochure.pdf
EU-MITSUBISHI-L200-V-FACELIFT-PICKUP-DOUBLECAB-STEPBUMPER-01	5305	1815	1780	Mitsubishi L200 official brochure	https://www.mitsubishi-motors.co.uk/content/dam/mitsubishi-motors-gb/pdfs/brochures/l200/L200-Brochure.pdf
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670	Auto-Data Citroen C5 Aircross	https://www.auto-data.net/en/citroen-c5-aircross-generation-6455
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L2-FWD-01	5572	2052	2194	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L3-FWD-01	6022	2052	2186	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLE-CAB-L4-FWD-01	6579	2052	2186	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L2-FWD-01	5572	2066	2214	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-FWD-01	6022	2066	2203	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-SRW-01	6022	2066	2218	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLE-CAB-L3-RWD-DRW-01	6022	2111	2218	Ford Transit Chassis Cab official brochure	https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298	Porsche 911 Carrera official model specifications	https://www.porsche.com/uk/models/911/carrera-models/911-carrera/
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297	Porsche 911 Carrera Cabriolet official model specifications	https://www.porsche.com/uk/models/911/carrera-models/911-carrera-cabriolet/
EU-MAZDA-MAZDA2-III-DJ-HATCHBACK-FACELIFT-01	4070	1695	1515	Mazda UK 2020 Mazda2 Price and Specification Guide	https://uk.cdn.mazda.media/c6bcf7e1072a457780b0ff1e9379bfc0/8445b5bc950340dd9b0c7e2021c9fec5.pdf
EU-PEUGEOT-208-I-A9-HATCHBACK-5D-FACELIFT-01	3973	1739	1460	Auto-Data Peugeot 208 I Facelift	https://www.auto-data.net/en/peugeot-208-i-phase-ii-2015-generation-4719
EU-AUDI-A8-D5-SEDAN-01	5172	1945	1473	Auto-Data Audi A8 D5	https://www.auto-data.net/en/audi-a8-d5-generation-5907
EU-OPEL-MOVANO-B-X62-VAN-L3H2-FWD-FACELIFT-01	6225	2070	2488	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L1H1-FWD-FACELIFT-01	5075	2070	2307	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L1H2-FWD-FACELIFT-01	5075	2070	2500	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L2H2-FWD-FACELIFT-01	5575	2070	2499	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L2H3-FWD-FACELIFT-01	5575	2070	2749	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-OPEL-MOVANO-B-X62-VAN-L3H3-FWD-FACELIFT-01	6225	2070	2744	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2272	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2263	Renault Master official brochure	https://cdn.group.renault.com/ren/ie/transversal-assets/brochures/vans-ebrochures/MASTER-eBrochure.pdf.asset.pdf/6aefa469ee.pdf
EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	4506	1851	1602	Audi RS Q3 official dimension drawing	https://www.audi.com/en/publications/dimensions/dimensions-rs-q3-1433/download
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384	Auto-Data Audi A5 Cabriolet F5 Facelift	https://www.auto-data.net/en/audi-a5-cabriolet-f5-facelift-2019-generation-7341
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493	Audi UK A4 allroad official press release	https://press.audi.co.uk/releases/397
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1741	Auto-Data Audi Q7 4M Facelift	https://www.auto-data.net/en/audi-q7-4m-facelift-2019-generation-7329
EU-AUDI-A7-C8-RS7-SPORTBACK-01	5009	1950	1424	Audi RS 7 Sportback official dimension drawing 09/2019	https://www.audi.com/en/publications/dimensions/dimensions-rs-7-sportback-1432/download
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460	Audi RS 6 Avant official dimension drawing 08/2019	https://www.audi.com/en/publications/dimensions/dimensions-rs-6-avant-1431/download
EU-FIAT-TALENTO-II-X82-VAN-L1H2-01	4999	1956	2493	Fiat Talento official technical data	https://www.media.stellantis.com/uploads/de/model-document/201209_tdfiattalento-5fd115a4383d6.pdf
EU-FIAT-TALENTO-II-X82-VAN-L2H2-01	5399	1956	2490	Fiat Talento official technical data	https://www.media.stellantis.com/uploads/de/model-document/201209_tdfiattalento-5fd115a4383d6.pdf
EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	5248	1956	1953	Fiat Talento official technical data	https://www.media.stellantis.com/uploads/de/model-document/201209_tdfiattalento-5fd115a4383d6.pdf
EU-CHEVROLET-CORVETTE-C5-Z06-COUPE-01	4564	1869	1212	Edmunds 2004 Chevrolet Corvette Z06 specifications	https://www.edmunds.com/chevrolet/corvette/2004/coupe/st-100274087/features-specs/
EU-CHEVROLET-CRUZE-I-J300-SEDAN-FACELIFT-01	4603	1797	1477	Auto-Data Chevrolet Cruze Sedan Facelift 2013	https://www.auto-data.net/en/chevrolet-cruze-sedan-facelift-2013-generation-4230
EU-HYUNDAI-I10-I-PA-HATCHBACK-PREFL-01	3565	1595	1540	Auto-Data Hyundai i10 I 1.2	https://www.auto-data.net/en/hyundai-i10-i-1.2-78hp-13881
EU-HYUNDAI-I10-I-PA-HATCHBACK-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I Facelift 2011	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828	Peugeot Partner II official technical guide	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/partner/partner-van-price-and-spec-guide.pdf
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834	Peugeot Partner II official technical guide	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/partner/partner-van-price-and-spec-guide.pdf
EU-PEUGEOT-PARTNER-II-B9-MPV-STANDARD-01	4380	1810	1801	Peugeot Partner II official technical guide	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/partner/partner-van-price-and-spec-guide.pdf
EU-PEUGEOT-PARTNER-II-B9-MPV-OUTDOOR-01	4380	1810	1862	Peugeot Partner II official technical guide	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/brochures/partner/partner-van-price-and-spec-guide.pdf
EU-HYUNDAI-I30-II-GD-HATCHBACK-PREFL-01	4300	1780	1470	Auto-Data Hyundai i30 II 1.4	https://www.auto-data.net/en/hyundai-i30-ii-1.4-100hp-18534
EU-HYUNDAI-I30-II-GD-WAGON-FACELIFT-01	4485	1780	1500	Hyundai Motor Europe New i30 official brochure	https://www.hyundai.ie/assets/car/i30-face-lift/files/hyundai-i30-12-pager.pdf
EU-HYUNDAI-I30-II-GD-HATCHBACK-FACELIFT-01	4300	1780	1470	Hyundai Motor Europe New i30 official brochure	https://www.hyundai.ie/assets/car/i30-face-lift/files/hyundai-i30-12-pager.pdf
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Auto-Data Audi A1 GB	https://www.auto-data.net/en/audi-a1-sportback-gb-generation-6385
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497	Audi A6 allroad quattro official technical data	https://www.audi-mediacenter.com/en/audi-a6-allroad-quattro-11958/technical-data
EU-KIA-PRIDE-I-BETA-SEDAN-01	3935	1605	1460	Automobile-Catalog Kia Pride Beta 1.3i specifications	https://www.automobile-catalog.com/car/1999/1340540/kia_pride_beta_1_3i.html
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Auto-Data Audi Q3 F3	https://www.auto-data.net/en/audi-q3-f3-generation-6379
EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	4410	1820	1655	Auto-Data Hyundai ix35 Facelift	https://www.auto-data.net/en/hyundai-ix35-facelift-2013-generation-4192
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910	Toyota Proace Verso official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/211214M-Proace-Verso-Tech-Spec.pdf
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910	Toyota Proace Verso official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/211214M-Proace-Verso-Tech-Spec.pdf
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485	Auto-Data Opel Astra K CNG	https://www.auto-data.net/en/opel-astra-k-1.6-ecotec-cng-110hp-34112
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4401-4500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf "https://anyrent-storage.s3.eu-west-3.amazonaws.com/ecomobile2934329863/media/uploaded-files/catalogotransitchassis-cabine161221.pdf"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（4328 行）
- 累计尺寸组：dimension_groups_final.tsv（1729 行）

