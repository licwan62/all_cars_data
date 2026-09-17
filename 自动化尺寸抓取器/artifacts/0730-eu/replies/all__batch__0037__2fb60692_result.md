# 任务：all 第 3601-3700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0037__2fb60692


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3601-3700 行

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
all 第 3601-3700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	4818	1948	1391
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X3-E83-SUV-01	4569	1853	1674
EU-BMW-X3-F97-M-COMPETITION-SUV-01	4726	1897	1669
EU-BMW-X3-F97-M-SUV-01	4726	1897	1667
EU-BMW-X3-G01-SUV-01	4708	1891	1676
EU-CITROEN-C3-III-HATCHBACK-PREFL-01	3996	1749	1474
EU-CITROEN-JUMPY-III-COMBI-M-01	4956	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XL-01	5306	1920	1890
EU-CITROEN-JUMPY-III-COMBI-XS-01	4606	1920	1905
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-M-01	4983	1920	1895
EU-CITROEN-JUMPY-III-FACELIFT-COMBI-XL-01	5333	1920	1935
EU-CITROEN-JUMPY-III-FACELIFT-VAN-M-01	4981	1920	1904
EU-CITROEN-JUMPY-III-FACELIFT-VAN-XL-01	5331	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814
EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-VAN-FACELIFT-01	4450	1740	1640
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501
EU-FORD-TRANSIT-COURIER-B460-KOMBI-MPV-01	4157	1764	1747
EU-FORD-TRANSIT-COURIER-B460-VAN-01	4157	1764	1770
EU-FORD-TRANSIT-TOURNEO-MK6-BUS-SWB-LOWROOF-01	4863	1974	1989
EU-FORD-TRANSIT-TOURNEO-MK7-BUS-SWB-LOWROOF-01	4863	1974	2089
EU-FORD-TRANSIT-V184-VAN-LWB-HIGHROOF-01	5651	1974	2678
EU-FORD-TRANSIT-V184-VAN-LWB-MIDROOF-01	5651	1974	2354
EU-FORD-TRANSIT-V184-VAN-MWB-HIGHROOF-01	5201	1974	2674
EU-FORD-TRANSIT-V184-VAN-MWB-MIDROOF-01	5201	1974	2353
EU-FORD-TRANSIT-V184-VAN-SWB-LOWROOF-01	4834	1974	2033
EU-FORD-TRANSIT-V184-VAN-SWB-MIDROOF-01	4834	1974	2368
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
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-CREW-01	6090	1996	2290
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-LWB-01	6509	1996	2275
EU-IVECO-DAILY-V-NATURALPOWER-35C-CHASSIS-CAB-SWB-01	5899	1996	2280
EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-LWB-01	6509	1996	2220
EU-IVECO-DAILY-V-NATURALPOWER-35S-CHASSIS-CAB-SWB-01	5899	1996	2225
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-CREW-01	7358	1996	2280
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-LWB-01	7358	1996	2265
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-MWB-01	6538	1996	2275
EU-IVECO-DAILY-V-NATURALPOWER-50C-CHASSIS-CAB-SWB-01	5928	1996	2280
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-CREW-01	7358	2060	2345
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-LWB-01	7358	2060	2325
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-MWB-01	6538	2060	2330
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-SWB-01	5928	2060	2335
EU-IVECO-DAILY-V-NATURALPOWER-HEAVY-CHASSIS-CAB-XLWB-01	8223	2060	2320
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-70C-01	7012	1996	3025
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-HIGH-DRW-01	7012	1996	2930
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-DRW-01	7012	1996	2745
EU-IVECO-DAILY-V-NATURALPOWER-VAN-LWB-MID-SRW-01	7012	1996	2670
EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-DRW-01	5997	1996	2745
EU-IVECO-DAILY-V-NATURALPOWER-VAN-MWB-MID-SRW-01	5977	1996	2640
EU-IVECO-DAILY-V-NATURALPOWER-VAN-SWB-LOW-SRW-01	5477	1996	2270
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-ACTIVE-DRIVE-II-01	4623	1859	1707
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605
EU-LAMBORGHINI-AVENTADOR-S-ROADSTER-01	4797	2030	1136
EU-LAMBORGHINI-AVENTADOR-SVJ-COUPE-01	4943	2098	1136
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-LOTUS-EXIGE-SERIES-3-CUP-430-COUPE-01	4084	1802	1129
EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	4084	1802	1129
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-COUPE-01	4084	1802	1129
EU-LOTUS-EXIGE-SERIES-3-SPORT-410-ROADSTER-01	4084	1802	1129
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
EU-MERCEDES-BENZ-C-KLASSE-A205-AMG-C43-CONVERTIBLE-FACELIFT-01	4693	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409
EU-MERCEDES-BENZ-C-KLASSE-C205-AMG-C43-COUPE-FACELIFT-01	4693	1810	1402
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-PREFL-01	4596	1770	1459
EU-MERCEDES-BENZ-C-KLASSE-S205-AMG-C43-WAGON-FACELIFT-01	4714	1810	1440
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457
EU-MERCEDES-BENZ-C-KLASSE-W205-AMG-C43-SEDAN-FACELIFT-01	4699	1810	1429
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442
EU-MERCEDES-BENZ-CLA-C117-FACELIFT-COUPE-01	4640	1777	1432
EU-MERCEDES-BENZ-CLA-X117-FACELIFT-WAGON-01	4640	1777	1435
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590
EU-OPEL-MOKKA-X-J13-SUV-01	4275	1781	1658
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819
EU-PEUGEOT-PARTNER-II-B9-TEPEE-ELECTRIC-MPV-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-OUTDOOR-01	4380	1810	1862
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-FACELIFT-MPV-01	4384	1810	1801
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613
EU-RENAULT-KANGOO-II-X61-PHASE-II-VAN-STANDARD-01	4282	1829	1805
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443
EU-TOYOTA-COROLLA-VIII-E110-WAGON-01	4240	1710	1610
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	4609	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	4959	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890
EU-VW-ATLAS-I-SUV-01	5036	1989	1769
EU-VW-GOLF-VII-5G-VARIANT-TGI-WAGON-01	4567	1799	1496
EU-VW-GOLF-VII-5G1-VAN-3D-GTI-PREFL-01	4268	1799	1442
EU-VW-GOLF-VII-5G1-VAN-3D-PREFL-01	4255	1799	1452
EU-VW-GOLF-VII-AUV-VARIANT-VAN-4MOTION-PREFL-01	4562	1799	1515
EU-VW-GOLF-VII-AUV-VARIANT-VAN-PREFL-01	4562	1799	1481
EU-VW-GOLF-VII-HATCHBACK-TGI-01	4258	1799	1492
EU-VW-T-CROSS-I-C1-SUV-PREFL-01	4108	1760	1584
EU-VW-T-ROC-I-SUV-01	4234	1819	1573
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Focus iv turnier	1.5 Ti-vct	Kombi	Frontantrieb	Benzin	90	122	Sep 2018	Nov 2025	2026-02-01	135563
Ford	Mondeo v	2.0 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	138	188	Jan 2019	Mar 2022	2026-04-01	135573
Audi	Q5	45 Tfsi Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	180	245	Dec 2018	-	2024-03-01	135591
Citroën	Jumpy ii	1.6 HDI 90 16V	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jun 2007	Mar 2016	2024-03-01	135593
Citroën	Jumpy ii	1.6 HDI 90 8V	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Jun 2007	Mar 2016	2024-03-01	135594
Mercedes-benz	Sprinter 5-T	516	Kasten	Heckantrieb	Benzin	115	156	Mar 2009	Dec 2018	2024-03-01	135597
Peugeot	Partner	1.6 Bluehdi 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	73	100	Apr 2015	-	2024-03-01	135598
Toyota	Proace	2.0 D4D	Pritsche/Fahrgestell	Frontantrieb	Diesel	90	122	Feb 2016	Dec 2022	2026-01-01	135599
Seat	Leon	2.0 TSI 4drive	Kombi	Allrad	Benzin	140	190	Sep 2018	Aug 2020	2024-03-01	135605
Piaggio	Porter	1.3	Bus	Heckantrieb	Benzin	61	83	Nov 2015	-	2024-03-01	135606
Ford	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	157	213	Sep 2018	-	2024-03-01	135616
Nissan	Qashqai ii	1.7 DCI	SUV	Frontantrieb	Diesel	110	150	Jan 2019	Sep 2020	2026-06-01	135617
Nissan	Micra v	1.0 Dig-t 117	Schrägheck	Frontantrieb	Benzin	86	117	Feb 2019	-	2024-03-01	135619
Nissan	Qashqai ii	1.7 DCI ALL Mode 4x4-i	SUV	Allrad	Diesel	110	150	Jan 2019	Sep 2020	2026-06-01	135620
Skoda	Octavia	1.5 TSI G-tec	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	96	130	Jan 2019	Oct 2020	2024-03-01	135621
VW	Golf vii	2.0 GTI TCR	Schrägheck	Frontantrieb	Benzin	213	290	Nov 2018	Aug 2020	2024-03-01	135622
Mercedes-benz	E-Klasse	E 400 D	Kombi	Heckantrieb	Diesel	250	340	Feb 2019	Jun 2020	2024-03-01	135626
Giotti Victoria	Gladiator	LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	59	80	Jan 2010	-	2024-03-01	135627
Peugeot	Partner	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	48	65	Oct 2005	Dec 2010	2024-03-01	135634
Peugeot	Partner	1.6 HDI 75	Pritsche/Fahrgestell	Frontantrieb	Diesel	55	75	Feb 2006	Jul 2008	2024-03-01	135635
VW	Touareg	2.0 Tfsi 4motion	SUV	Allrad	Benzin	183	249	May 2018	Nov 2023	2024-03-01	135636
Land Rover	Discovery sport	2.0 SI4 Flex 4X4	SUV	Allrad	Benzin/Ethanol	177	241	Dec 2018	-	2024-03-01	135637
Lotus	Exige	3.5 380	Cabriolet	Heckantrieb	Benzin	279	379	Nov 2016	-	2024-03-01	135638
Lamborghini	Aventador	6.5 LP 720-4 AWD	Targa	Allrad	Benzin	530	721	Apr 2013	-	2024-03-01	135639
VW	Atlas	3.6 FSI 4motion	SUV	Allrad	Benzin	183	249	Jan 2019	-	2024-03-01	135640
Peugeot	Partner	1.8	Pritsche/Fahrgestell	Frontantrieb	Benzin	66	90	Mar 1997	Aug 2000	2024-03-01	135642
Dacia	Logan	1.5 Blue DCI 95	Stufenheck	Frontantrieb	Diesel	70	95	May 2018	-	2024-03-01	135643
VW	Tiguan	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Sep 2018	-	2024-03-01	135644
Ford	Transit	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	55	75	Aug 1994	Mar 2000	2024-03-01	135645
Renault	Twingo	0.9 TCE 90 LPG	Schrägheck	Heckantrieb	Benzin/Autogas (LPG)	66	90	Aug 2018	Apr 2019	2026-05-01	135646
Iveco	Daily v	55s17w 4X4	Pritsche/Fahrgestell	Allrad	Diesel	125	170	Sep 2011	Feb 2014	2024-03-01	135648
Toyota	Corolla	1.6 Vvti	Stufenheck	Frontantrieb	Benzin	97	132	Jan 2019	-	2024-03-01	135652
Toyota	Rav 4 v	2.0 Vvti	SUV	Frontantrieb	Benzin	127	173	Dec 2018	-	2024-03-01	135655
Bentley	Continental	6.0 AWD	Cabriolet	Allrad	Benzin	467	635	Dec 2018	-	2024-03-01	135656
Audi	A5	45 Tfsi Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	180	245	Feb 2019	Aug 2020	2026-07-01	135657
Jeep	Cherokee	2.0 T-gdi	SUV	Allrad	Benzin	200	272	Sep 2018	-	2024-03-01	135666
Audi	A4 b9	50 TDI Quattro	Stufenheck	Allrad	Diesel	210	286	Jul 2018	Aug 2020	2026-07-01	135680
Audi	A4 b9 avant	50 TDI Quattro	Kombi	Allrad	Diesel	210	286	Jul 2018	Oct 2019	2026-07-01	135681
Audi	A4 allroad b9	3.0 TDI Quattro	Kombi	Allrad	Diesel	210	286	Jul 2018	Oct 2019	2024-03-01	135682
Audi	A4 allroad b9	45 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	180	245	Jul 2018	-	2024-03-01	135689
Toyota	Corolla	2.0 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	132	180	Feb 2019	-	2024-03-01	135690
Mercedes-benz	Sprinter 4,6-T	414 CDI 4X4	Kasten	Allrad	Diesel	105	143	May 2016	Dec 2018	2024-03-01	135691
Mercedes-benz	Cla	CLA 180	Coupe	Frontantrieb	Benzin	100	136	Mar 2019	-	2024-03-01	135692
Mercedes-benz	Cla	CLA 200	Coupe	Frontantrieb	Benzin	120	163	Mar 2019	-	2024-03-01	135693
Mercedes-benz	Cla	CLA 220	Coupe	Frontantrieb	Benzin	140	190	Mar 2019	-	2024-03-01	135694
Mercedes-benz	Cla	CLA 220 4-matic	Coupe	Allrad	Benzin	140	190	Mar 2019	-	2024-03-01	135695
Mercedes-benz	Cla	CLA 250	Coupe	Frontantrieb	Benzin	165	224	Mar 2019	-	2024-03-01	135696
Mercedes-benz	Cla	CLA 250 4-matic	Coupe	Allrad	Benzin	165	224	Mar 2019	-	2024-03-01	135697
Mercedes-benz	Cla	CLA 180 D	Coupe	Frontantrieb	Diesel	85	116	Mar 2019	-	2024-03-01	135698
Toyota	Corolla	1.2	Kombi	Frontantrieb	Benzin	85	116	Feb 2019	-	2024-03-01	135700
Tata	Aria	2.2 DI AWD	Großraumlimousine	Allrad	Diesel	103	140	Oct 2010	-	2024-03-01	135701
Toyota	Corolla	2.0 Hybrid	Kombi	Frontantrieb	Benzin/Elektro	132	180	Feb 2019	-	2024-03-01	135704
Mercedes-benz	Citan tourer	108 CDI	Großraumlimousine	Frontantrieb	Diesel	59	80	Feb 2019	Aug 2021	2024-03-01	135707
BMW	X3	Xdrive 30 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	215	292	Dec 2019	-	2024-03-01	135708
Mercedes-benz	Citan tourer	109 CDI	Großraumlimousine	Frontantrieb	Diesel	70	95	Feb 2019	Aug 2021	2024-03-01	135709
Mercedes-benz	Citan tourer	111 CDI	Großraumlimousine	Frontantrieb	Diesel	85	116	Feb 2019	Aug 2021	2024-03-01	135710
Audi	A7 sportback	40 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	150	204	Sep 2018	-	2024-03-01	135719
VW	T-Roc	1.5 TSI 4motion	SUV	Allrad	Benzin	110	150	May 2018	Nov 2019	2024-03-01	135725
BMW	5	M535 I	Stufenheck	Heckantrieb	Benzin	160	218	Jan 1985	Dec 1987	2024-03-01	135728
Seat	Leon	1.6 TDI 4drive	Kombi	Allrad	Diesel	85	115	Jul 2018	Aug 2020	2024-03-01	135729
Opel	Mokka	1.6 Cdti 4X4	SUV	Allrad	Diesel	81	110	Mar 2018	Dec 2019	2025-06-01	135731
Audi	A4 b9	45 TDI Quattro	Stufenheck	Allrad	Diesel	170	231	Jul 2018	-	2024-03-01	135733
Audi	A4 b9 avant	45 TDI Quattro	Kombi	Allrad	Diesel	170	231	Jul 2018	-	2024-03-01	135734
Audi	A5	45 TDI Quattro	Schrägheck	Allrad	Diesel	170	231	Jul 2018	-	2026-07-01	135735
Audi	A5	45 TDI Quattro	Coupe	Allrad	Diesel	170	231	Jul 2018	Nov 2020	2026-07-01	135736
Audi	A3	30 G-tron	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Nov 2018	Oct 2020	2024-03-01	135737
Audi	Q5	45 TDI Quattro	SUV	Allrad	Diesel	170	231	Aug 2018	Nov 2020	2024-03-01	135743
Peugeot	Partner	1.6 HDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	82	111	Aug 2010	-	2024-03-01	135744
Porsche	Panamera	2.9 4	Schrägheck	Allrad	Benzin	243	330	May 2016	Dec 2023	2024-08-01	135745
Porsche	Panamera	2.9 4	Kombi	Allrad	Benzin	243	330	May 2017	Dec 2023	2024-08-01	135746
Mercedes-benz	Sprinter 3,5-T	314 CDI Allrad	Kasten	Allrad	Diesel	105	143	Jan 2019	Dec 2021	2024-08-01	135748
Mercedes-benz	Sprinter 3,5-T	316 CDI Allrad	Kasten	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	135749
Mercedes-benz	Sprinter 3,5-T	319 CDI Allrad	Kasten	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	135750
Mercedes-benz	Sprinter 5-T	516 CDI Allrad	Kasten	Allrad	Diesel	120	163	Jan 2019	Dec 2021	2024-08-01	135751
Mercedes-benz	Sprinter 5-T	519 CDI Allrad	Kasten	Allrad	Diesel	140	190	Jan 2019	Dec 2021	2024-07-01	135752
Lamborghini	Aventador	6.5 LP 770-4 SVJ AWD	Targa	Allrad	Benzin	566	770	Mar 2019	-	2024-03-01	135801
Citroën	C3 iii	1.2 VTI 82 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	60	82	Jul 2016	-	2025-06-01	135806
Ford	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	96	131	Mar 2019	-	2025-06-01	135808
Citroën	C3 iii	1.2 Puretech 82 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	61	83	May 2018	-	2025-06-01	135809
Ford	Ranger	2.0 Ecoblue 4X4	Pick-up	Allrad	Diesel	125	170	Mar 2019	-	2024-03-01	135810
GMC	Sierra	6.0 CNG 4WD	Pick-up	Allrad	Benzin/Erdgas (CNG)	224	305	Sep 2001	Dec 2005	2024-03-01	135842
KIA	Soul iii	2.0 MPI	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2019	-	2024-03-01	135911
BMW	3	318 D	Stufenheck	Heckantrieb	Diesel	100	136	Mar 2019	Mar 2020	2024-03-01	135917
BMW	3	330 D	Stufenheck	Heckantrieb	Diesel	195	265	Mar 2019	-	2024-03-01	135919
BMW	3	320 I 1.6	Stufenheck	Heckantrieb	Benzin	125	170	Mar 2019	-	2024-03-01	135921
Land Rover	Range rover sport ii	3.0 P400 Mhev 4X4	SUV	Allrad	Benzin/Elektro	294	400	Feb 2019	Mar 2022	2025-02-03	135923
Toyota	Supra	3.0 GR	Coupe	Heckantrieb	Benzin	250	340	Mar 2019	-	2024-03-01	135932
Audi	Q5	SQ5 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	255	347	Feb 2019	Sep 2020	2024-03-01	135933
Mercedes-benz	Gle	AMG GLE 53 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	320	435	Apr 2019	-	2024-03-01	135943
VW	T-Cross	1.6 TDI	SUV	Frontantrieb	Diesel	70	95	Dec 2018	-	2024-03-01	135944
Mercedes-benz	A-Klasse	AMG A 35 4-matic	Stufenheck	Allrad	Benzin	225	306	Mar 2019	-	2024-03-01	135945
Mercedes-benz	Cla	AMG CLA 35 4-matic	Coupe	Allrad	Benzin	225	306	Apr 2019	-	2024-03-01	135946
Mercedes-benz	C-Klasse	C 300 4-matic	Stufenheck	Allrad	Benzin	190	258	May 2018	May 2021	2024-03-01	135948
Tesla	Model 3	EV AWD	Stufenheck	Allrad	Elektro	258	351	Jun 2018	-	2024-03-01	135951
Tesla	Model 3	EV Performance AWD	Stufenheck	Allrad	Elektro	340	462	Jun 2018	-	2024-03-01	135952
Renault	Kadjar	1.7 Blue DCI 150 4WD	SUV	Allrad	Diesel	110	150	Aug 2018	-	2024-03-01	135953
Renault	Kangoo	1.5 DCI 80	Großraumlimousine	Frontantrieb	Diesel	59	80	Mar 2019	-	2024-03-01	135954
Renault	Kangoo	1.5 DCI 115	Großraumlimousine	Frontantrieb	Diesel	85	115	Mar 2019	-	2024-03-01	135955
Dacia	Dokker	1.3 TCE 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Mar 2019	Dec 2021	2024-11-01	135957
Mercedes-benz	Amg gt roadster	GT R	Cabriolet	Heckantrieb	Benzin	430	585	Apr 2019	Dec 2020	2024-03-01	135958


--- Round 1 / 首次发送 ---
## 更新点

* 已完成缓存优先聚类，71 个输入 Ktype 已闭合为 72 条 READY 映射；`135744` 按 Van 与 MPV 两种物理分支拆分。
* 本轮首次创建 19 个尺寸组，覆盖 Focus Turnier、Mondeo Sedan、Discovery Sport、Twingo、Corolla Sedan/Touring Sports、RAV4、Continental GTC、CLA C118、Citan Tourer、A7、BMW E28 M535i、Panamera Sport Turismo、Supra、SQ5、GLE 53、AMG A35 Sedan、AMG CLA 35 和 AMG GT R Roadster。相关尺寸已按不含后视镜宽度落盘。([汽车目录][1])
* AMG CLA 35 的 `4695 × 1834 × 1404 mm` 已由 Mercedes-AMG 手册明确给出，其中宽度注明为不含外后视镜。
* 剩余项主要集中在商用底盘的轴距/车顶组合、Ranger 与 Sierra 的 CAB/BED、Partner 混合车身，以及少数乘用车市场规格冲突。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：71
* READY 映射：72
* PENDING Ktype／映射：29
* 当前已引用尺寸组：52
* 本轮首次创建尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135563	135563	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-01	HIGH		READY
135573	135573	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH	2019 facelift sedan exterior.	READY
135591	135591	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
135593	135593	Chassis Cab	Jumpy II				LOW	平台/轴距分支尚未闭合。	PENDING: 需确认平台驾驶室轴距与外廓分支
135594	135594	Chassis Cab	Jumpy II				LOW	平台/轴距分支尚未闭合。	PENDING: 需确认平台驾驶室轴距与外廓分支
135597	135597	Van	Sprinter II	W906			LOW	候选涉及多车长和多车顶。	PENDING: 需拆分W906车长与车顶组合
135598	135598	Chassis Cab	Partner II	B9			LOW	平台驾驶室外廓尚未闭合。	PENDING: 需确认B9平台驾驶室尺寸
135599	135599	Chassis Cab	Proace II	MDZ4			LOW	平台驾驶室车长分支尚未闭合。	PENDING: 需确认平台驾驶室轴距与车长
135605	135605	Wagon	Leon III	5F	5		LOW	4Drive旅行版高度边界待核对。	PENDING: 需确认4Drive旅行版高度
135606	135606	MPV	Porter				LOW	Bus车身代码及外廓未闭合。	PENDING: 需确认Porter Bus具体车身
135616	135616	Pickup	Ranger III	T6			LOW	驾驶室和货斗分支未确认。	PENDING: 需确认CAB/BED与特殊外观版本
135617	135617	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH		READY
135619	135619	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
135620	135620	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH		READY
135621	135621	Wagon	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
135622	135622	Hatchback	Golf VII	5G1	5		LOW	GTI TCR外廓资料存在市场口径冲突。	PENDING: 需解决GTI TCR三维冲突
135626	135626	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
135627	135627	Chassis Cab	Gladiator				LOW	底盘轴距及驾驶室边界未闭合。	PENDING: 需确认Giotti Gladiator底盘配置
135634	135634	Van/MPV	Partner I	M59			LOW	输入同时覆盖Kasten与Großraumlimousine，分支尚未闭合。	PENDING: 需拆分Van与MPV物理分支
135635	135635	Chassis Cab	Partner I			EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH		READY
135636	135636	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
135637	135637	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	HIGH		READY
135638	135638	Convertible	Exige Series 3	Type 111	2	EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	MEDIUM	3.5 380 Roadster shares confirmed Series 3 roadster exterior.	READY
135639	135639	Convertible	Aventador I	LB834	2		LOW	LP 720-4 Roadster特殊保险杠外廓未闭合。	PENDING: 需确认LP720-4 Roadster三维
135640	135640	SUV	Atlas I		5	EU-VW-ATLAS-I-SUV-01	HIGH		READY
135642	135642	Chassis Cab	Partner I			EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH		READY
135643	135643	Sedan	Logan II	L52	4		LOW	facelift sedan三维尚未完成同配置核对。	PENDING: 需闭合Logan II facelift sedan尺寸
135644	135644	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-FWD-01	HIGH		READY
135645	135645	Chassis Cab	Transit				LOW	1994-2000底盘存在轴距与驾驶室分支。	PENDING: 需拆分Transit底盘轴距/驾驶室
135646	135646	Hatchback	Twingo III	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	HIGH		READY
135648	135648	Chassis Cab	Daily V				LOW	55S17W 4x4轴距及驾驶室分支未闭合。	PENDING: 需确认Daily 4x4底盘配置
135652	135652	Sedan	Corolla XII	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH		READY
135655	135655	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-FWD-01	HIGH		READY
135656	135656	Convertible	Continental GTC III		2	EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	HIGH		READY
135657	135657	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
135666	135666	SUV	Cherokee KL	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	MEDIUM	未见Active Drive II专属高度特征，映射标准facelift外廓。	READY
135680	135680	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
135681	135681	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
135682	135682	Wagon	A4 allroad B9	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
135689	135689	Wagon	A4 allroad B9	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
135690	135690	Hatchback	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	HIGH		READY
135691	135691	Van	Sprinter II	W906			LOW	4x4 Kasten存在多车长和多车顶。	PENDING: 需拆分W906 4x4车长与车顶
135692	135692	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135693	135693	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135694	135694	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135695	135695	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135696	135696	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135697	135697	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135698	135698	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135700	135700	Wagon	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	HIGH		READY
135701	135701	MPV	Aria I		5		LOW	市场版本与车顶/外部附件口径未闭合。	PENDING: 需确认Tata Aria欧规外廓
135704	135704	Wagon	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	HIGH		READY
135707	135707	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135708	135708	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	MEDIUM	插混动力未改变已确认G01标准外廓。	READY
135709	135709	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135710	135710	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135719	135719	Hatchback	A7 Sportback II	4K8	5	EU-AUDI-A7-4K8-SPORTBACK-01	HIGH		READY
135725	135725	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
135728	135728	Sedan	5 Series E28	E28	4	EU-BMW-5-E28-M535I-SEDAN-01	HIGH	M-Technic exterior branch.	READY
135729	135729	Wagon	Leon III	5F	5		LOW	4Drive柴油旅行版高度边界待核对。	PENDING: 需确认4Drive旅行版高度
135731	135731	SUV	Mokka X	J13	5	EU-OPEL-MOKKA-X-J13-SUV-01	HIGH		READY
135733	135733	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
135734	135734	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
135735	135735	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
135736	135736	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
135737	135737	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
135743	135743	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
135744_van	135744	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	Kasten分支。	READY
135744_mpv	135744	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	MEDIUM	Großraumlimousine分支。	READY
135745	135745	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
135746	135746	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	HIGH		READY
135748	135748	Van	Sprinter III	W907			LOW	AWD Kasten存在多车长和多车顶。	PENDING: 需拆分W907 AWD车长与车顶
135749	135749	Van	Sprinter III	W907			LOW	AWD Kasten存在多车长和多车顶。	PENDING: 需拆分W907 AWD车长与车顶
135750	135750	Van	Sprinter III	W907			LOW	AWD Kasten存在多车长和多车顶。	PENDING: 需拆分W907 AWD车长与车顶
135751	135751	Van	Sprinter III	W907			LOW	AWD Kasten存在多车长和多车顶。	PENDING: 需拆分W907 AWD车长与车顶
135752	135752	Van	Sprinter III	W907			LOW	AWD Kasten存在多车长和多车顶。	PENDING: 需拆分W907 AWD车长与车顶
135801	135801	Convertible	Aventador I	LB834	2		LOW	SVJ Roadster外廓尚未完成同配置核对。	PENDING: 需确认SVJ Roadster三维
135806	135806	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
135808	135808	Pickup	Ranger III	T6			LOW	驾驶室和货斗分支未确认。	PENDING: 需确认CAB/BED
135809	135809	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
135810	135810	Pickup	Ranger III	T6			LOW	驾驶室和货斗分支未确认。	PENDING: 需确认CAB/BED
135842	135842	Pickup	Sierra GMT800	GMT800			LOW	CNG 4WD对应吨级、驾驶室和货斗未闭合。	PENDING: 需确认Sierra吨级/CAB/BED
135911	135911	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	MEDIUM	汽油版与e-Soul共享已确认SK3外壳尺寸。	READY
135917	135917	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135919	135919	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135921	135921	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135923	135923	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH		READY
135932	135932	Coupe	Supra V	A90	3	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
135933	135933	SUV	SQ5 FY	FY	5	EU-AUDI-SQ5-FY-SUV-PREFL-01	HIGH		READY
135943	135943	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	HIGH	AMG GLE 53 exterior branch.	READY
135944	135944	SUV	T-Cross I	C1	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
135945	135945	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	HIGH	AMG A35 exterior branch.	READY
135946	135946	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	HIGH	AMG CLA 35 exterior branch.	READY
135948	135948	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
135951	135951	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
135952	135952	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
135953	135953	SUV	Kadjar I		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
135954	135954	MPV	Kangoo II	X61	5		LOW	乘用版高度存在市场差异。	PENDING: 需确认欧规MPV高度
135955	135955	MPV	Kangoo II	X61	5		LOW	乘用版高度存在市场差异。	PENDING: 需确认欧规MPV高度
135957	135957	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
135958	135958	Convertible	AMG GT Roadster	R190	2	EU-MERCEDES-BENZ-AMG-GT-R190-GT-R-ROADSTER-01	HIGH	GT R wide-body Roadster exterior.	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-IV-C519-WAGON-01	4668	1825	1459	Automobile-Catalog Ford Focus Turnier 1.5	https://www.automobile-catalog.com/car/2019/2740520/ford_focus_turnier_1_5_ecoblue_120.html
EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	4871	1852	1482	CarsGuide 2019 Ford Mondeo dimensions	https://www.carsguide.com.au/ford/mondeo/car-dimensions/2019
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724	CarExpert 2018 Land Rover Discovery Sport dimensions	https://www.carexpert.com.au/land-rover/discovery-sport/2018/exterior-and-dimensions
EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	3595	1646	1554	Renault Malta Twingo dimensions	https://renault.com.mt/cars/Twingo/dimensions.html
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435	CarsGuide 2019 Toyota Corolla dimensions	https://www.carsguide.com.au/toyota/corolla/car-dimensions/2019
EU-TOYOTA-RAV4-V-XA50-SUV-FWD-01	4600	1855	1685	Toyota certified used vehicle catalog RAV4 X	https://toyota.jp/ucar/catalog/brand-TOYOTA/car-RAV4/201904/10120928/
EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	4850	1954	1399	Bentley Newsroom; Neofiliac Bentley Continental GTC 3 specifications	https://www.bentleymedia.com/en/heritage-collection/2019-continental-gtc-dk19vdy;https://neofiliac.com/product/7619/bentley-continental-gtc-3
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439	CarSized Mercedes-Benz CLA C118 dimensions	https://www.carsized.com/en/cars/mercedes-benz-cla-2019-sedan/
EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	4653	1790	1445	Automobile Dimension Toyota Corolla Touring Sports	https://www.automobiledimension.com/model/toyota/corolla-touring-sports
EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	4321	1829	1809	Auto-Data Mercedes-Benz Citan Tourer Long W415	https://www.auto-data.net/en/mercedes-benz-citan-tourer-long-w415-generation-8250
EU-AUDI-A7-4K8-SPORTBACK-01	4969	1908	1422	ADAC Audi A7 Sportback 4K dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a7/4k/287904/
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397	UltimateSpecs BMW E28 M535i	https://www.ultimatespecs.com/car-specs/BMW/1270/BMW-E28-5-Series-M535i.html
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	5049	1937	1428	Wired Porsche Panamera Sport Turismo	https://www.wired.com/story/porsche-sport-turismo-geneva-motor-show
EU-TOYOTA-SUPRA-V-A90-COUPE-01	4380	1865	1290	Toyota Europe GR Supra press information	https://newsroom.toyota.eu/2019-the-new-toyota-gr-supra/
EU-AUDI-SQ5-FY-SUV-PREFL-01	4671	1893	1635	Audi Japan Press Center SQ5	https://www.audi-press.jp/press-releases/2017/b7rqqm0000000s4g.html
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782	Carsales Mercedes-Benz GLE53 AMG 2019 specifications	https://www.carsales.com.au/research/mercedes-benz/gle-class/2019/gle53-amg/b146db55-4076-4ad3-821d-389dcfc2d3cf/
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411	Automobile-Catalog Mercedes-AMG A35 Sedan	https://www.automobile-catalog.com/car/2019/2875130/mercedes-amg_a_35_4matic_limousine_sedan.html
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404	Mercedes-AMG CLA operator manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ca/pdf/mercedes-amg-cla-supplement-september-2019-1.pdf
EU-MERCEDES-BENZ-AMG-GT-R190-GT-R-ROADSTER-01	4551	2007	1260	Automobile-Catalog Mercedes-AMG GT R Roadster	https://www.automobile-catalog.com/car/2019/2874965/mercedes-amg_gt_r_roadster.html
```

## 下一步优先处理

1. 集中处理 Sprinter W906/W907、Jumpy、Proace、Partner、Transit 和 Daily 的轴距、车长及车顶组合。
2. 批量闭合 Ranger 三个 Ktype 与 Sierra GMT800 的 CAB/BED、吨级和特殊外观分支。
3. 处理 Leon 4Drive 高度、Golf GTI TCR 冲突、Partner I Van/MPV、Kangoo MPV、Logan、Aventador 和剩余小众车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2019/2740520/ford_focus_turnier_1_5_ecoblue_120.html?utm_source=chatgpt.com "2019 Ford Focus Turnier 1.5 EcoBlue (120) Specs Review ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* `135605`、`135729` 已关联既有 `EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01`，本轮不重复输出该尺寸组。SEAT 官方尺寸页确认 Leon Sportourer ST 的标准外廓边界。([SEAT][1])
* `135954`、`135955` 的车型适用范围同时包含 Kangoo 与 Grand Kangoo，现分别拆成标准轴距和长轴距分支，并首次创建两个 MPV 尺寸组。([Market-Auto][2])
* 已闭合 Golf GTI TCR、Logan II Sedan、Tata Aria、Aventador SVJ Roadster 四个首次尺寸组。([VW Press][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* READY 映射：82
* PENDING Ktype／映射：21
* 当前已引用尺寸组：59
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135605	135605	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
135622	135622	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-5G1-GTI-TCR-HATCHBACK-01	HIGH	GTI TCR专属外廓。	READY
135643	135643	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	2016年后改款外廓。	READY
135701	135701	MPV	Aria I		5	EU-TATA-ARIA-I-MPV-01	HIGH		READY
135729	135729	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
135801	135801	Convertible	Aventador I	LB834	2	EU-LAMBORGHINI-AVENTADOR-SVJ-ROADSTER-01	HIGH	SVJ Roadster宽体空气动力外廓。	READY
135954_swb	135954	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	HIGH	Kangoo标准轴距分支。	READY
135954_lwb	135954	MPV	Grand Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	HIGH	Grand Kangoo长轴距分支。	READY
135955_swb	135955	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	HIGH	Kangoo标准轴距分支。	READY
135955_lwb	135955	MPV	Grand Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	HIGH	Grand Kangoo长轴距分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VII-5G1-GTI-TCR-HATCHBACK-01	4268	1790	1482	Volkswagen UK Golf GTI TCR official press kit	https://www.vwpress.co.uk/press-kits/979
EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	4358	1733	1517	Dacia Logan official brochure	https://dacia.abcmotors.ee/upload/Brochures/Dacia-LOGAN-brochure.pdf
EU-TATA-ARIA-I-MPV-01	4780	1895	1780	Tata Motors Aria official specifications	https://www.tatamotors.com.gh/en/product/cars-utility-vehicles/utility-vehicles/tata-aria/
EU-LAMBORGHINI-AVENTADOR-SVJ-ROADSTER-01	4943	2098	1136	Lamborghini Aventador SVJ Roadster media information	https://autoinfo.jp/release/190304_Aventador_SVJ_Roadster.pdf
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801	Renault Kangoo official dimensions	https://www.renault.ps/en/cars/kangoo/dimensions.html
EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	4666	1829	1802	Renault Kangoo official dimensions	https://www.renault.ps/en/cars/kangoo/dimensions.html
```

## 下一步优先处理

1. 按共用车身代码集中拆分 Sprinter W906/W907 的车长、车顶和四驱分支。
2. 闭合 Jumpy、Proace、Partner、Transit 与 Daily 的底盘驾驶室轴距分支。
3. 最后处理 Ranger 三个 Ktype、Sierra GMT800、Piaggio Porter 和 Giotti Gladiator 的驾驶室或车身配置。

推进信号：CONTINUE

[1]: https://www.seat.com/content/dam/public/seat-website/myco/2028/car-shopping-tools/brochure-download/brochures/leon/other-shoppingtools-brochure-leon-specs-final-may-2019.pdf "SEAT Leon Brochure Download Specs"
[2]: https://market-auto.es/producto/topran-301-702-863?srsltid=AfmBOorbOpXg4tItISFObAvPIo8bB0Uv44xtcJTx4lh_v8JafahfnJVp&utm_source=chatgpt.com "Muelle espiral, airbag Renault KANGOO / GRAND KANGOO II 7701 ..."
[3]: https://www.vwpress.co.uk/press-kits/979?utm_source=chatgpt.com "Golf GTI TCR Mk VII 2019 | Official Media Site NEWSROOM"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Partner II B9 平台驾驶室；`135634` 按 Partner I Phase II 的 Kasten 与 Großraumlimousine 两种物理车身拆分，其中 Van 分支复用既有尺寸组，MPV 分支首次建组。([手册库][1])
* 已闭合 Piaggio Porter Bus 与 Giotti Victoria Gladiator 底盘驾驶室；Gladiator 的车型边界由对应 LPG 底盘记录确认，三维采用 Giotti Victoria 技术资料。([Дром][2])
* 已闭合 Aventador LP 720-4 50 Anniversario Roadster 专属外廓。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射：88
* PENDING Ktype／映射：16
* 当前已引用尺寸组：64
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135598	135598	Chassis Cab	Partner II	B9	2	EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	HIGH		READY
135606	135606	MPV	Porter II		5	EU-PIAGGIO-PORTER-II-BUS-01	HIGH		READY
135627	135627	Chassis Cab	Gladiator		2	EU-GIOTTI-VICTORIA-GLADIATOR-CHASSIS-CAB-01	HIGH		READY
135634_van	135634	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	MEDIUM	Kasten分支。	READY
135634_mpv	135634	MPV	Partner I	M59	5	EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	HIGH	Großraumlimousine分支。	READY
135639	135639	Convertible	Aventador I	LB834	2	EU-LAMBORGHINI-AVENTADOR-LP720-4-50-ANNIVERSARIO-ROADSTER-01	HIGH	LP720-4 50 Anniversario Roadster专属外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822	Peugeot Partner owner manual	https://www.manualslib.com/manual/2362932/Peugeot-Partner.html?page=138
EU-PIAGGIO-PORTER-II-BUS-01	3400	1395	1870	Zoomcar Piaggio Porter II 1.3 Multitech glazed van	https://zoomcar.fr/fiche-technique-utilitaire/piaggio/porter-ii-1-3-16v-multitech-fourgon-vitre-NAT169693.html
EU-GIOTTI-VICTORIA-GLADIATOR-CHASSIS-CAB-01	3915	1560	1770	Giotti Victoria Gladiator technical sheet; Autodíly PEMA vehicle index	https://www.repettomacchine.com/wp-content/uploads/2018/12/Giotti-Victoria.pdf;https://www.autodily-pema.cz/autodily/giotti-victoria/gladiator-valnik-podvozek/lpg-59kw
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II 1.4	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.4-75hp-5623
EU-LAMBORGHINI-AVENTADOR-LP720-4-50-ANNIVERSARIO-ROADSTER-01	4834	2030	1136	Automobile-Catalog Lamborghini Aventador LP720-4 50 Anniversario Roadster	https://www.automobile-catalog.com/car/2014/2455820/lamborghini_aventador_lp720-4_50_anniversario_roadster.html
```

## 下一步优先处理

1. 集中拆分 Sprinter W906／W907 的车长、车顶和四驱组合。
2. 闭合 Jumpy、Proace、Transit 与 Daily 的平台驾驶室轴距分支。
3. 最后处理 Ranger 三个 Ktype 与 Sierra GMT800 的 CAB／BED、吨级及外廓分支。

推进信号：CONTINUE

[1]: https://www.manualslib.com/manual/2362932/Peugeot-Partner.html?utm_source=chatgpt.com "PEUGEOT PARTNER USER MANUAL Pdf Download"
[2]: https://www.drom.ru/catalog/piaggio/porter/290228/?utm_source=chatgpt.com "Piaggio Porter 1.3 MT Multitech Base (11.2015 - н.в.) - технические характеристики"
[3]: https://www.automobile-catalog.com/car/2014/2455820/lamborghini_aventador_lp720-4_50_anniversario_roadster.html?utm_source=chatgpt.com "Lamborghini Aventador LP720-4 50 Anniversario Roadster ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 `135593`、`135594`：Citroën Jumpy II 平台驾驶室统一关联 L2 物理外廓；官方规格表明确给出平台驾驶室长 5016 mm、无后视镜宽 1895 mm、高 1942 mm。
* 已闭合 `135599`：Toyota Proace II 的 2.0D 120 平台驾驶室限定为 Medium 车身；Toyota 官方资料确认该车身长 4959 mm、无后视镜宽 1920 mm，2.0D 120 对应高度 1940 mm。([丰田媒体][1])
* 本轮首次创建 2 个尺寸组，未重复输出既有尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：87
* READY 映射：91
* PENDING Ktype／映射：13
* 当前已引用尺寸组：66
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135593	135593	Chassis Cab	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	MEDIUM		READY
135594	135594	Chassis Cab	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	MEDIUM		READY
135599	135599	Chassis Cab	Proace II	MDZ4	2	EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	5016	1895	1942	Citroën Dispatch official brochure	https://xr793.com/wp-content/uploads/2022/09/2013-Citroen-Dispatch-UK.pdf
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940	Toyota Proace Van official press release	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162741210223MProaceFullRelease.pdf
```

## 下一步优先处理

1. 集中拆分 Sprinter W906／W907 四驱 Kasten 的有效车长和车顶组合。
2. 闭合 Ranger 三个 Ktype 与 Sierra GMT800 的驾驶室、货斗及吨级分支。
3. 处理 Transit 1994–2000 平台底盘和 Daily V 55S17W 4×4 底盘配置。

推进信号：CONTINUE

[1]: https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162741210223MProaceFullRelease.pdf "Microsoft Word - 210223M - Proace full release"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 `135749`、`135750`、`135751`、`135752`。官方车型程序确认 316 CDI、319 CDI、516 CDI、519 CDI AWD Kasten 均提供 L2H2 与 L3H2 两种物理分支。
* 两种 AWD 外廓分别为 L2H2 `5932 × 2020 × 2785 mm`、L3H2 `6967 × 2020 × 2778 mm`；宽度采用官方尺寸图中的不含后视镜车身宽度 2020 mm。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：91
* READY 映射：99
* PENDING Ktype／映射：9
* 当前已引用尺寸组：68
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135749_l2h2	135749	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135749_l3h2	135749	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135750_l2h2	135750	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135750_l3h2	135750	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135751_l2h2	135751	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135751_l3h2	135751	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135752_l2h2	135752	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135752_l3h2	135752	Van	Sprinter III	W907		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	5932	2020	2785	Mercedes-Benz Sprinter official panel van price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	6967	2020	2778	Mercedes-Benz Sprinter official panel van price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
```

## 下一步优先处理

1. 闭合 `135748` 的 Sprinter 314 CDI AWD 有效车长分支，以及 `135691` 的 W906 414 CDI 4×4 分支。
2. 处理 `135597` 的 W906 5-T 516 Kasten 多车长／多车顶组合。
3. 最后集中处理 Ranger、Sierra、Transit 底盘和 Daily 55S17W 4×4。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已根据 Ktype 对应的明确车身代码纠正 W907 四驱 Kasten 分支：`135748`、`135749`、`135750` 均覆盖 `907.633 / 907.635 / 907.637`；`135751`、`135752` 均覆盖 `907.653 / 907.655 / 907.657`，因此补齐上一轮遗漏的 L4H2 分支。([Meyer Motoren][1])
* `135748` 已消除 PENDING，三个分支分别复用既有 3.5t L2H2、L3H2 尺寸组，并首次创建 L4H2 尺寸组。
* `135751`、`135752` 已从 3.5t 尺寸组纠正至独立的 5t L2H2、L3H2、L4H2 尺寸组；5t 四驱车身高度与 3.5t 版本不同，不能继续共组。官方车型程序确认 A2/A3/A4 车长边界及四驱适用性，规格表用于闭合各吨级四驱高度。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* READY 映射：106
* PENDING Ktype／映射：8
* 当前已引用尺寸组：72
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135748_l2h2	135748	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135748_l3h2	135748	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135748_l4h2	135748	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135749_l2h2	135749	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135749_l3h2	135749	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135749_l4h2	135749	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135750_l2h2	135750	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135750_l3h2	135750	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135750_l4h2	135750	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135751_l2h2	135751	Van	Sprinter III	907.653		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	HIGH	5t L2H2 AWD分支。	READY
135751_l3h2	135751	Van	Sprinter III	907.655		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	HIGH	5t L3H2 AWD分支。	READY
135751_l4h2	135751	Van	Sprinter III	907.657		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	HIGH	5t L4H2 AWD分支。	READY
135752_l2h2	135752	Van	Sprinter III	907.653		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	HIGH	5t L2H2 AWD分支。	READY
135752_l3h2	135752	Van	Sprinter III	907.655		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	HIGH	5t L3H2 AWD分支。	READY
135752_l4h2	135752	Van	Sprinter III	907.657		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	HIGH	5t L4H2 AWD分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	7367	2020	2773	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Sprinter-Preisliste-0320.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	5932	2020	2775	Mercedes-Benz Sprinter official AWD price list; Drom Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	6967	2020	2771	Mercedes-Benz Sprinter official AWD price list; Drom Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	7367	2020	2769	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Sprinter-Preisliste-0320.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
```

## 下一步优先处理

1. 闭合 `135691` 的 W906 `906.653 / 906.655 / 906.657` 四驱 Kasten 分支。
2. 处理 `135597` 的 W906 5t 516 汽油 Kasten 车长和车顶组合。
3. 集中处理 Ranger、Sierra、Transit 底盘与 Daily 55S17W 4×4。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/135748/mercedes-benz/sprinter_3_5t_kasten_b907_b910_/314_cdi_4x4_907_633_907_635_907_637_135748?utm_source=chatgpt.com "314 CDI 4x4 (907.633, 907.635, 907.637) | Sprinter 3,5t Kasten (B907, B910) | Mercedes-Benz | Manufacturers | Meyer Motoren"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合三个 Ranger Ktype。`135808` 拆为 Regular Cab 与 Double Cab；`135810` 拆为 Regular Cab、Super Cab 标准版/ Limited、Double Cab 标准版/ Limited；`135616` 拆为 Double Cab Limited、Wildtrak 与 Raptor。Ford 官方车型程序明确了 130 PS、170 PS、213 PS 对应的驾驶室和配置范围。([福特英国][1])
* 标准车身的车长和高度采用 21.75MY 官方规格，车身宽度采用 Ford 官方资料中明确标注的不含后视镜宽度 1860 mm；Raptor 官方规格明确为 `5363 × 2028 × 1873 mm`，其中 2028 mm 标注为不含侧后视镜。([福特英国][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：95
* READY 映射：116
* PENDING Ktype／映射：5
* 当前已引用尺寸组：79
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135616_doublecab_limited	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited分支。	READY
135616_doublecab_wildtrak	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	HIGH	Double Cab Wildtrak分支。	READY
135616_doublecab_raptor	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-RAPTOR-01	HIGH	Double Cab Raptor宽体分支。	READY
135808_regularcab	135808	Pickup	Ranger III	TKE	2	EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	HIGH	Regular Cab分支。	READY
135808_doublecab	135808	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab XL分支。	READY
135810_regularcab	135810	Pickup	Ranger III	TKE	2	EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	HIGH	Regular Cab分支。	READY
135810_supercab_standard	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-STANDARD-01	HIGH	Super Cab XL/XLT分支。	READY
135810_supercab_limited	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-LIMITED-01	HIGH	Super Cab Limited分支。	READY
135810_doublecab_standard	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab XL/XLT分支。	READY
135810_doublecab_limited	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	5282	1860	1800	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-STANDARD-01	5282	1860	1804	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	5282	1860	1815	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-LIMITED-01	5359	1860	1810	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	5359	1860	1821	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	5359	1860	1848	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-RAPTOR-01	5363	2028	1873	Ford Indonesia Ranger Raptor official brochure	https://ford.co.id/wp-content/uploads/2022/06/E-Brochure_Raptor.pdf
```

## 下一步优先处理

1. 闭合 `135691` 的 Sprinter W906 414 CDI 4×4 Kasten 车长和车顶分支。
2. 闭合 `135597` 的 Sprinter W906 5-T 516 汽油 Kasten 组合。
3. 最后处理 `135645` Transit 底盘、`135648` Daily 55S17W 4×4 底盘和 `135842` Sierra GMT800 的吨级/CAB/BED 分支。

[1]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf "Ranger 21.75MY V1 GBR_en_EBRO.pdf"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合 `135691`：按 `906.653 / 906.655 / 906.657` 拆为 L2H1、L3H2、L4H2 三个四驱 Kasten 分支。W906 四驱车型程序对应中轴标准顶、长轴高顶和超长轴高顶三种外廓。([Dezo's Garage][1])
* 已闭合 `135597`：该汽油 516 Kasten 对应 `906.655` 长轴车身，拆为 L3H2 与 L3H3 两种车顶；L3H2 与 `135691` 复用同一物理尺寸组。([AK24配件][2])
* 本轮首次创建 4 个 W906 尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* READY 映射：121
* PENDING Ktype／映射：3
* 当前已引用尺寸组：83
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135597_l3h2	135597	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	HIGH	L3H2长轴高顶分支。	READY
135597_l3h3	135597	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H3-01	HIGH	L3H3长轴超高顶分支。	READY
135691_l2h1	135691	Van	Sprinter II	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L2H1-01	HIGH	L2H1四驱分支。	READY
135691_l3h2	135691	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	HIGH	L3H2四驱分支。	READY
135691_l4h2	135691	Van	Sprinter II	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L4H2-01	HIGH	L4H2四驱分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L2H1-01	5926	1993	2510	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	6961	1993	2815	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H3-01	6961	1993	3045	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L4H2-01	7361	1993	2820	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
```

## 下一步优先处理

1. 闭合 `135645` Transit 1994–2000 平台驾驶室的轴距与驾驶室分支。
2. 闭合 `135648` Daily V 55S17W 4×4 底盘驾驶室分支。
3. 最后处理 `135842` Sierra GMT800 的吨级、CAB 与 BED 分支。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf?utm_source=chatgpt.com "Sprinter Price List October 2017"
[2]: https://www.ak24parts.com/en/spareparts/135597/sprinter-5-t-van-b906-516-1-8?srsltid=AfmBOoqwcFvhB57jOhqGYrQ1dLF3wjuiSHX5E7YCu2oej4jetPDHNVGs&utm_source=chatgpt.com "MERCEDES-BENZ SPRINTER 5-t Van (B906)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 `135648`。Iveco 官方技术规格确认 Daily V `55S17W 4x4` 底盘驾驶室提供 3050 mm 与 3400 mm 两种轴距，对应两套不同外廓，因此拆为 SWB、MWB 两个派生映射。规格分别为 `4921 × 2016 × 2644 mm` 和 `5432 × 2016 × 2634 mm`；2016 mm 为最大驾驶室车身宽度，不含外后视镜。([Yumpu][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：98
* READY 映射：123
* PENDING Ktype／映射：2
* 当前已引用尺寸组：85
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135648_swb	135648	Chassis Cab	Daily V	55S17W	2	EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-SWB-01	HIGH	3050 mm轴距底盘驾驶室分支。	READY
135648_mwb	135648	Chassis Cab	Daily V	55S17W	2	EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-MWB-01	HIGH	3400 mm轴距底盘驾驶室分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-SWB-01	4921	2016	2644	Iveco Daily 55S17W 4x4 Chassis Cab official technical specification	https://www.yumpu.com/en/document/view/227908/daily-55s17w-4x4-chassis-cabpmd
EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-MWB-01	5432	2016	2634	Iveco Daily 55S17W 4x4 Chassis Cab official technical specification	https://www.yumpu.com/en/document/view/227908/daily-55s17w-4x4-chassis-cabpmd
```

## 下一步优先处理

1. 闭合 `135645` Ford Transit VE83 平台驾驶室的 2835 mm 与 3570 mm 轴距外廓分支。
2. 最后闭合 `135842` GMC Sierra GMT800 的吨级、驾驶室与货斗组合；完成后立即进行一次机械检查并输出两张最终完整 TSV 及指定下载链接。

推进信号：CONTINUE

[1]: https://www.yumpu.com/en/document/view/227908/daily-55s17w-4x4-chassis-cabpmd "Daily 55S17W 4x4 Chassis Cab.pmd"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3601-3700_ktype_dimension_mapping_final.tsv
- all_3601-3700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合 `135645`：Ford Transit VE83 平台驾驶室拆分为 2835 mm 轴距 SWB 与 3570 mm 轴距 LWB 两种外廓。对应尺寸分别为 `4616 × 1974 × 2024 mm` 和 `5376 × 1974 × 2026 mm`。([DENSO][1])
* 已闭合 `135842`：该 Ktype 对应 GMC Sierra 2500HD GMT800 Extended Cab 6.0 CNG 4WD，覆盖 6.5-ft short bed 与 8-ft long bed，分别建立独立尺寸组。([LakiNet][2])
* 已完成机械检查：表头固定、127 个 `id` 唯一、90 个尺寸组唯一、全部映射引用闭合、无孤立尺寸组、三维和来源均非空、PENDING=0。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：127
* PENDING：0
* DIMENSION_GROUP：90
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
135563	135563	Wagon	Focus IV	C519	5	EU-FORD-FOCUS-IV-C519-WAGON-01	HIGH		READY
135573	135573	Sedan	Mondeo V	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH	2019 facelift sedan exterior.	READY
135591	135591	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
135593	135593	Chassis Cab	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	MEDIUM		READY
135594	135594	Chassis Cab	Jumpy II		2	EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	MEDIUM		READY
135597_l3h2	135597	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	HIGH	L3H2长轴高顶分支。	READY
135597_l3h3	135597	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H3-01	HIGH	L3H3长轴超高顶分支。	READY
135598	135598	Chassis Cab	Partner II	B9	2	EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	HIGH		READY
135599	135599	Chassis Cab	Proace II	MDZ4	2	EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	HIGH		READY
135605	135605	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
135606	135606	MPV	Porter II		5	EU-PIAGGIO-PORTER-II-BUS-01	HIGH		READY
135616_doublecab_limited	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited分支。	READY
135616_doublecab_wildtrak	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	HIGH	Double Cab Wildtrak分支。	READY
135616_doublecab_raptor	135616	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-RAPTOR-01	HIGH	Double Cab Raptor宽体分支。	READY
135617	135617	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH		READY
135619	135619	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
135620	135620	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH		READY
135621	135621	Wagon	Octavia III	5E	5	EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	HIGH		READY
135622	135622	Hatchback	Golf VII	5G1	5	EU-VW-GOLF-VII-5G1-GTI-TCR-HATCHBACK-01	HIGH	GTI TCR专属外廓。	READY
135626	135626	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH		READY
135627	135627	Chassis Cab	Gladiator		2	EU-GIOTTI-VICTORIA-GLADIATOR-CHASSIS-CAB-01	HIGH		READY
135634_van	135634	Van	Partner I	M59		EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	MEDIUM	Kasten分支。	READY
135634_mpv	135634	MPV	Partner I	M59	5	EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	HIGH	Großraumlimousine分支。	READY
135635	135635	Chassis Cab	Partner I			EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH		READY
135636	135636	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
135637	135637	SUV	Discovery Sport I	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	HIGH		READY
135638	135638	Convertible	Exige Series 3	Type 111	2	EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	MEDIUM	3.5 380 Roadster shares confirmed Series 3 roadster exterior.	READY
135639	135639	Convertible	Aventador I	LB834	2	EU-LAMBORGHINI-AVENTADOR-LP720-4-50-ANNIVERSARIO-ROADSTER-01	HIGH	LP720-4 50 Anniversario Roadster专属外廓。	READY
135640	135640	SUV	Atlas I		5	EU-VW-ATLAS-I-SUV-01	HIGH		READY
135642	135642	Chassis Cab	Partner I			EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	HIGH		READY
135643	135643	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	2016年后改款外廓。	READY
135644	135644	SUV	Tiguan II	AD1	5	EU-VW-TIGUAN-II-SUV-FWD-01	HIGH		READY
135645_swb	135645	Chassis Cab	Transit Mk5	EME	2	EU-FORD-TRANSIT-VE83-CHASSIS-CAB-SWB-01	HIGH	2835 mm轴距底盘驾驶室分支。	READY
135645_lwb	135645	Chassis Cab	Transit Mk5	ENE	2	EU-FORD-TRANSIT-VE83-CHASSIS-CAB-LWB-01	HIGH	3570 mm轴距底盘驾驶室分支。	READY
135646	135646	Hatchback	Twingo III	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	HIGH		READY
135648_swb	135648	Chassis Cab	Daily V	55S17W	2	EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-SWB-01	HIGH	3050 mm轴距底盘驾驶室分支。	READY
135648_mwb	135648	Chassis Cab	Daily V	55S17W	2	EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-MWB-01	HIGH	3400 mm轴距底盘驾驶室分支。	READY
135652	135652	Sedan	Corolla XII	E210	4	EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	HIGH		READY
135655	135655	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-FWD-01	HIGH		READY
135656	135656	Convertible	Continental GTC III		2	EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	HIGH		READY
135657	135657	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
135666	135666	SUV	Cherokee KL	KL	5	EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	MEDIUM	未见Active Drive II专属高度特征，映射标准facelift外廓。	READY
135680	135680	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
135681	135681	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
135682	135682	Wagon	A4 allroad B9	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
135689	135689	Wagon	A4 allroad B9	8WH	5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
135690	135690	Hatchback	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	HIGH		READY
135691_l2h1	135691	Van	Sprinter II	906.653		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L2H1-01	HIGH	L2H1四驱分支。	READY
135691_l3h2	135691	Van	Sprinter II	906.655		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	HIGH	L3H2四驱分支。	READY
135691_l4h2	135691	Van	Sprinter II	906.657		EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L4H2-01	HIGH	L4H2四驱分支。	READY
135692	135692	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135693	135693	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135694	135694	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135695	135695	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135696	135696	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135697	135697	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135698	135698	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-COUPE-01	HIGH		READY
135700	135700	Wagon	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	HIGH		READY
135701	135701	MPV	Aria I		5	EU-TATA-ARIA-I-MPV-01	HIGH		READY
135704	135704	Wagon	Corolla XII	E210	5	EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	HIGH		READY
135707	135707	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135708	135708	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-01	MEDIUM	插混动力未改变已确认G01标准外廓。	READY
135709	135709	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135710	135710	MPV	Citan I	W415	5	EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	HIGH		READY
135719	135719	Hatchback	A7 Sportback II	4K8	5	EU-AUDI-A7-4K8-SPORTBACK-01	HIGH		READY
135725	135725	SUV	T-Roc I		5	EU-VW-T-ROC-I-SUV-01	HIGH		READY
135728	135728	Sedan	5 Series E28	E28	4	EU-BMW-5-E28-M535I-SEDAN-01	HIGH	M-Technic exterior branch.	READY
135729	135729	Wagon	Leon III	5F	5	EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	HIGH		READY
135731	135731	SUV	Mokka X	J13	5	EU-OPEL-MOKKA-X-J13-SUV-01	HIGH		READY
135733	135733	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-01	HIGH		READY
135734	135734	Wagon	A4 B9	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH		READY
135735	135735	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
135736	135736	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
135737	135737	Hatchback	A3 8V	8VA	5	EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	HIGH		READY
135743	135743	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
135744_van	135744	Van	Partner II	B9		EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	MEDIUM	Kasten分支。	READY
135744_mpv	135744	MPV	Partner II	B9	5	EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	MEDIUM	Großraumlimousine分支。	READY
135745	135745	Hatchback	Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH		READY
135746	135746	Wagon	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	HIGH		READY
135748_l2h2	135748	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135748_l3h2	135748	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135748_l4h2	135748	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135749_l2h2	135749	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135749_l3h2	135749	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135749_l4h2	135749	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135750_l2h2	135750	Van	Sprinter III	907.633		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	HIGH	L2H2 AWD分支。	READY
135750_l3h2	135750	Van	Sprinter III	907.635		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	HIGH	L3H2 AWD分支。	READY
135750_l4h2	135750	Van	Sprinter III	907.637		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	HIGH	L4H2 AWD分支。	READY
135751_l2h2	135751	Van	Sprinter III	907.653		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	HIGH	5t L2H2 AWD分支。	READY
135751_l3h2	135751	Van	Sprinter III	907.655		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	HIGH	5t L3H2 AWD分支。	READY
135751_l4h2	135751	Van	Sprinter III	907.657		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	HIGH	5t L4H2 AWD分支。	READY
135752_l2h2	135752	Van	Sprinter III	907.653		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	HIGH	5t L2H2 AWD分支。	READY
135752_l3h2	135752	Van	Sprinter III	907.655		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	HIGH	5t L3H2 AWD分支。	READY
135752_l4h2	135752	Van	Sprinter III	907.657		EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	HIGH	5t L4H2 AWD分支。	READY
135801	135801	Convertible	Aventador I	LB834	2	EU-LAMBORGHINI-AVENTADOR-SVJ-ROADSTER-01	HIGH	SVJ Roadster宽体空气动力外廓。	READY
135806	135806	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
135808_regularcab	135808	Pickup	Ranger III	TKE	2	EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	HIGH	Regular Cab分支。	READY
135808_doublecab	135808	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab XL分支。	READY
135809	135809	Hatchback	C3 III		5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
135810_regularcab	135810	Pickup	Ranger III	TKE	2	EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	HIGH	Regular Cab分支。	READY
135810_supercab_standard	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-STANDARD-01	HIGH	Super Cab XL/XLT分支。	READY
135810_supercab_limited	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-LIMITED-01	HIGH	Super Cab Limited分支。	READY
135810_doublecab_standard	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab XL/XLT分支。	READY
135810_doublecab_limited	135810	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited分支。	READY
135842_shortbed	135842	Pickup	Sierra 2500HD GMT800	GMT800	4	EU-GMC-SIERRA-2500HD-GMT800-PICKUP-EXTENDED-CAB-SHORT-BED-01	HIGH	Extended Cab 6.5-ft short-bed分支。	READY
135842_longbed	135842	Pickup	Sierra 2500HD GMT800	GMT800	4	EU-GMC-SIERRA-2500HD-GMT800-PICKUP-EXTENDED-CAB-LONG-BED-01	HIGH	Extended Cab 8-ft long-bed分支。	READY
135911	135911	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	MEDIUM	汽油版与e-Soul共享已确认SK3外壳尺寸。	READY
135917	135917	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135919	135919	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135921	135921	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH		READY
135923	135923	SUV	Range Rover Sport II	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH		READY
135932	135932	Coupe	Supra V	A90	3	EU-TOYOTA-SUPRA-V-A90-COUPE-01	HIGH		READY
135933	135933	SUV	SQ5 FY	FY	5	EU-AUDI-SQ5-FY-SUV-PREFL-01	HIGH		READY
135943	135943	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	HIGH	AMG GLE 53 exterior branch.	READY
135944	135944	SUV	T-Cross I	C1	5	EU-VW-T-CROSS-I-C1-SUV-PREFL-01	HIGH		READY
135945	135945	Sedan	A-Class V177	V177	4	EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	HIGH	AMG A35 exterior branch.	READY
135946	135946	Coupe	CLA II	C118	4	EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	HIGH	AMG CLA 35 exterior branch.	READY
135948	135948	Sedan	C-Class W205	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
135951	135951	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
135952	135952	Sedan	Model 3 I		4	EU-TESLA-MODEL-3-I-SEDAN-01	HIGH		READY
135953	135953	SUV	Kadjar I		5	EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	HIGH		READY
135954_swb	135954	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	HIGH	Kangoo标准轴距分支。	READY
135954_lwb	135954	MPV	Grand Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	HIGH	Grand Kangoo长轴距分支。	READY
135955_swb	135955	MPV	Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	HIGH	Kangoo标准轴距分支。	READY
135955_lwb	135955	MPV	Grand Kangoo II		5	EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	HIGH	Grand Kangoo长轴距分支。	READY
135957	135957	MPV	Dokker I		5	EU-DACIA-DOKKER-I-MPV-01	HIGH		READY
135958	135958	Convertible	AMG GT Roadster	R190	2	EU-MERCEDES-BENZ-AMG-GT-R190-GT-R-ROADSTER-01	HIGH	GT R wide-body Roadster exterior.	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3601-3700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-IV-C519-WAGON-01	4668	1825	1459	Automobile-Catalog Ford Focus Turnier 1.5	https://www.automobile-catalog.com/car/2019/2740520/ford_focus_turnier_1_5_ecoblue_120.html
EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	4871	1852	1482	CarsGuide 2019 Ford Mondeo dimensions	https://www.carsguide.com.au/ford/mondeo/car-dimensions/2019
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Audi Q5 official technical data	https://www.audi-mediacenter.com/en/audi-q5-14815
EU-CITROEN-JUMPY-II-PLATFORM-CAB-L2-01	5016	1895	1942	Citroën Dispatch official brochure	https://xr793.com/wp-content/uploads/2022/09/2013-Citroen-Dispatch-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H2-01	6961	1993	2815	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L3H3-01	6961	1993	3045	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-PEUGEOT-PARTNER-II-B9-PLATFORM-CAB-01	4237	1810	1822	Peugeot Partner owner manual	https://www.manualslib.com/manual/2362932/Peugeot-Partner.html?page=138
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940	Toyota Proace Van official press release	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162741210223MProaceFullRelease.pdf
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454	SEAT Leon official specification brochure	https://www.seat.com/content/dam/public/seat-website/myco/2028/car-shopping-tools/brochure-download/brochures/leon/other-shoppingtools-brochure-leon-specs-final-may-2019.pdf
EU-PIAGGIO-PORTER-II-BUS-01	3400	1395	1870	Zoomcar Piaggio Porter II 1.3 Multitech glazed van	https://zoomcar.fr/fiche-technique-utilitaire/piaggio/porter-ii-1-3-16v-multitech-fourgon-vitre-NAT169693.html
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	5359	1860	1821	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	5359	1860	1848	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-RAPTOR-01	5363	2028	1873	Ford Indonesia Ranger Raptor official brochure	https://ford.co.id/wp-content/uploads/2022/06/E-Brochure_Raptor.pdf
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Auto-Data Nissan Qashqai II J11 facelift	https://www.auto-data.net/en/nissan-qashqai-ii-j11-facelift-2017-generation-5451
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	Auto-Data Nissan Micra V K14	https://www.auto-data.net/en/nissan-micra-v-k14-generation-5275
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465	Auto-Data Skoda Octavia III Combi facelift	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-generation-5346
EU-VW-GOLF-VII-5G1-GTI-TCR-HATCHBACK-01	4268	1790	1482	Volkswagen UK Golf GTI TCR official press kit	https://www.vwpress.co.uk/press-kits/979
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class T-Modell S213	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-generation-5172
EU-GIOTTI-VICTORIA-GLADIATOR-CHASSIS-CAB-01	3915	1560	1770	Giotti Victoria Gladiator technical sheet; Autodíly PEMA vehicle index	https://www.repettomacchine.com/wp-content/uploads/2018/12/Giotti-Victoria.pdf;https://www.autodily-pema.cz/autodily/giotti-victoria/gladiator-valnik-podvozek/lpg-59kw
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-01	4137	1720	1810	Auto-Data Peugeot Partner I Phase II	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-generation-5620
EU-PEUGEOT-PARTNER-I-PHASE-II-MPV-01	4140	1720	1810	Auto-Data Peugeot Partner I Phase II 1.4	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-2002-1.4-75hp-5623
EU-PEUGEOT-PARTNER-I-PLATFORM-CAB-01	4137	1724	1819	Peugeot Partner platform cab technical data	https://www.auto-data.net/en/peugeot-partner-i-phase-ii-generation-5620
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Touareg official model information	https://www.volkswagen-newsroom.com/en/touareg-5613
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724	CarExpert 2018 Land Rover Discovery Sport dimensions	https://www.carexpert.com.au/land-rover/discovery-sport/2018/exterior-and-dimensions
EU-LOTUS-EXIGE-SERIES-3-S-ROADSTER-CONVERTIBLE-01	4084	1802	1129	UltimateSpecs Lotus Exige S Roadster	https://www.ultimatespecs.com/car-specs/Lotus/107746/Lotus-Exige-S-Roadster.html
EU-LAMBORGHINI-AVENTADOR-LP720-4-50-ANNIVERSARIO-ROADSTER-01	4834	2030	1136	Automobile-Catalog Lamborghini Aventador LP720-4 50 Anniversario Roadster	https://www.automobile-catalog.com/car/2014/2455820/lamborghini_aventador_lp720-4_50_anniversario_roadster.html
EU-VW-ATLAS-I-SUV-01	5036	1989	1769	Volkswagen 2019 Atlas official press kit	https://media.vw.com/en-us/press-kits/2019-atlas-press-kit
EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	4358	1733	1517	Dacia Logan official brochure	https://dacia.abcmotors.ee/upload/Brochures/Dacia-LOGAN-brochure.pdf
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654	Volkswagen Tiguan official model information	https://www.volkswagen-newsroom.com/en/tiguan-3625
EU-FORD-TRANSIT-VE83-CHASSIS-CAB-SWB-01	4616	1974	2024	CarsGuide Ford Transit 1996 dimensions	https://www.carsguide.com.au/ford/transit/car-dimensions/1996
EU-FORD-TRANSIT-VE83-CHASSIS-CAB-LWB-01	5376	1974	2026	CarExpert Ford Transit 1996 chassis cab specifications	https://www.carexpert.co.nz/ford/transit/1996-2-5l-chassis-cab-rwd-diesel-manual-jjo8f8os19970501
EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	3595	1646	1554	Renault Malta Twingo dimensions	https://renault.com.mt/cars/Twingo/dimensions.html
EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-SWB-01	4921	2016	2644	Iveco Daily 55S17W 4x4 Chassis Cab official technical specification	https://www.yumpu.com/en/document/view/227908/daily-55s17w-4x4-chassis-cabpmd
EU-IVECO-DAILY-V-55S17W-CHASSIS-CAB-MWB-01	5432	2016	2634	Iveco Daily 55S17W 4x4 Chassis Cab official technical specification	https://www.yumpu.com/en/document/view/227908/daily-55s17w-4x4-chassis-cabpmd
EU-TOYOTA-COROLLA-XII-E210-SEDAN-01	4630	1780	1435	CarsGuide 2019 Toyota Corolla dimensions	https://www.carsguide.com.au/toyota/corolla/car-dimensions/2019
EU-TOYOTA-RAV4-V-XA50-SUV-FWD-01	4600	1855	1685	Toyota certified used vehicle catalog RAV4 X	https://toyota.jp/ucar/catalog/brand-TOYOTA/car-RAV4/201904/10120928/
EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	4850	1954	1399	Bentley Newsroom; Neofiliac Bentley Continental GTC 3 specifications	https://www.bentleymedia.com/en/heritage-collection/2019-continental-gtc-dk19vdy;https://neofiliac.com/product/7619/bentley-continental-gtc-3
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi A5 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a5-sportback-14935
EU-JEEP-CHEROKEE-KL-FACELIFT-SUV-STANDARD-01	4623	1859	1683	Auto-Data Jeep Cherokee V KL facelift	https://www.auto-data.net/en/jeep-cherokee-v-kl-facelift-2018-generation-6021
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427	Audi A4 Sedan official technical data	https://www.audi-mediacenter.com/en/audi-a4-sedan-14943
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	Audi A4 Avant official technical data	https://www.audi-mediacenter.com/en/audi-a4-avant-14944
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493	Audi A4 allroad quattro official technical data	https://www.audi-mediacenter.com/en/audi-a4-allroad-quattro-14945
EU-TOYOTA-COROLLA-XII-E210-HATCHBACK-01	4370	1790	1435	Toyota Corolla Hatchback official press information	https://newsroom.toyota.eu/2019-corolla-hatchback-and-touring-sports/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L2H1-01	5926	1993	2510	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W906-VAN-L4H2-01	7361	1993	2820	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://xr793.com/wp-content/uploads/2022/12/2017-Mercedes-Benz-Sprinter-Price-List-UK.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-CLA-C118-COUPE-01	4688	1830	1439	CarSized Mercedes-Benz CLA C118 dimensions	https://www.carsized.com/en/cars/mercedes-benz-cla-2019-sedan/
EU-TOYOTA-COROLLA-XII-E210-TOURING-SPORTS-WAGON-01	4653	1790	1445	Automobile Dimension Toyota Corolla Touring Sports	https://www.automobiledimension.com/model/toyota/corolla-touring-sports
EU-TATA-ARIA-I-MPV-01	4780	1895	1780	Tata Motors Aria official specifications	https://www.tatamotors.com.gh/en/product/cars-utility-vehicles/utility-vehicles/tata-aria/
EU-MERCEDES-BENZ-CITAN-W415-TOURER-LONG-MPV-01	4321	1829	1809	Auto-Data Mercedes-Benz Citan Tourer Long W415	https://www.auto-data.net/en/mercedes-benz-citan-tourer-long-w415-generation-8250
EU-BMW-X3-G01-SUV-01	4708	1891	1676	BMW Group PressClub X3 G01	https://www.press.bmwgroup.com/global/article/detail/T0268062EN/the-new-bmw-x3
EU-AUDI-A7-4K8-SPORTBACK-01	4969	1908	1422	ADAC Audi A7 Sportback 4K dimensions	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a7/4k/287904/
EU-VW-T-ROC-I-SUV-01	4234	1819	1573	Volkswagen T-Roc official model information	https://www.volkswagen-newsroom.com/en/t-roc-3163
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397	UltimateSpecs BMW E28 M535i	https://www.ultimatespecs.com/car-specs/BMW/1270/BMW-E28-5-Series-M535i.html
EU-OPEL-MOKKA-X-J13-SUV-01	4275	1781	1658	Auto-Data Opel Mokka X	https://www.auto-data.net/en/opel-mokka-x-generation-5310
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Audi A5 Coupé official technical data	https://www.audi-mediacenter.com/en/audi-a5-coupe-14934
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426	Audi A3 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a3-sportback-14152
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1828	Auto-Data Peugeot Partner II B9 Van	https://www.auto-data.net/en/peugeot-partner-ii-generation-2917
EU-PEUGEOT-PARTNER-II-B9-TEPEE-STANDARD-01	4380	1810	1801	Auto-Data Peugeot Partner II Tepee	https://www.auto-data.net/en/peugeot-partner-ii-tepee-generation-2918
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423	Porsche Panamera official model information	https://newsroom.porsche.com/en/products/porsche-panamera.html
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	5049	1937	1428	Wired Porsche Panamera Sport Turismo	https://www.wired.com/story/porsche-sport-turismo-geneva-motor-show
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L2H2-AWD-01	5932	2020	2785	Mercedes-Benz Sprinter official panel van price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L3H2-AWD-01	6967	2020	2778	Mercedes-Benz Sprinter official panel van price list	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-L4H2-AWD-01	7367	2020	2773	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Sprinter-Preisliste-0320.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L2H2-AWD-01	5932	2020	2775	Mercedes-Benz Sprinter official AWD price list; Drom Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L3H2-AWD-01	6967	2020	2771	Mercedes-Benz Sprinter official AWD price list; Drom Mercedes-Benz Sprinter dimensions	https://bluesky-cogcms.cdn.imgeng.in/media/87151/62686-mb-vans-sprinter-panel-crew-van-awd-price-list-aw-0221sml.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-MERCEDES-BENZ-SPRINTER-W907-VAN-5T-L4H2-AWD-01	7367	2020	2769	Mercedes-Benz Sprinter official price list; Drom Mercedes-Benz Sprinter dimensions	https://www.schade.de/fileadmin/docs/SCHADE/Neuwagen/Nfz/MB/Sprinter-Preisliste-0320.pdf;https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/specs/dimensions/
EU-LAMBORGHINI-AVENTADOR-SVJ-ROADSTER-01	4943	2098	1136	Lamborghini Aventador SVJ Roadster media information	https://autoinfo.jp/release/190304_Aventador_SVJ_Roadster.pdf
EU-CITROEN-C3-III-HATCHBACK-PREFL-01	3996	1749	1474	Auto-Data Citroën C3 III	https://www.auto-data.net/en/citroen-c3-iii-generation-5257
EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	5282	1860	1800	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	5282	1860	1815	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-STANDARD-01	5282	1860	1804	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-LIMITED-01	5359	1860	1810	Ford Ranger official brochure 21.75MY; Ford Ranger official brochure MY2017	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-New_Ranger.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ranger.pdf
EU-GMC-SIERRA-2500HD-GMT800-PICKUP-EXTENDED-CAB-SHORT-BED-01	5784	2024	1935	Edmunds 2005 GMC Sierra 2500HD Extended Cab Work Truck specifications	https://www.edmunds.com/gmc/sierra-2500hd/2005/st-100396457/features-specs/
EU-GMC-SIERRA-2500HD-GMT800-PICKUP-EXTENDED-CAB-LONG-BED-01	6264	2024	1935	Edmunds 2005 GMC Sierra 2500HD Extended Cab specifications	https://www.edmunds.com/gmc/sierra-2500hd/2005/extended-cab/st-100396462/features-specs/
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605	Kia e-Soul official specifications	https://www.kia.com/uk/new-cars/e-soul/specification/
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	BMW Group PressClub 3 Series G20	https://www.press.bmwgroup.com/global/article/detail/T0296452EN/the-all-new-bmw-3-series-sedan
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Land Rover Range Rover Sport technical specifications	https://media.landrover.com/en-us/download/33861
EU-TOYOTA-SUPRA-V-A90-COUPE-01	4380	1865	1290	Toyota Europe GR Supra press information	https://newsroom.toyota.eu/2019-the-new-toyota-gr-supra/
EU-AUDI-SQ5-FY-SUV-PREFL-01	4671	1893	1635	Audi Japan Press Center SQ5	https://www.audi-press.jp/press-releases/2017/b7rqqm0000000s4g.html
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782	Carsales Mercedes-Benz GLE53 AMG 2019 specifications	https://www.carsales.com.au/research/mercedes-benz/gle-class/2019/gle53-amg/b146db55-4076-4ad3-821d-389dcfc2d3cf/
EU-VW-T-CROSS-I-C1-SUV-PREFL-01	4108	1760	1584	Volkswagen T-Cross official model information	https://www.volkswagen-newsroom.com/en/t-cross-4870
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411	Automobile-Catalog Mercedes-AMG A35 Sedan	https://www.automobile-catalog.com/car/2019/2875130/mercedes-amg_a_35_4matic_limousine_sedan.html
EU-MERCEDES-BENZ-CLA-C118-AMG-CLA35-COUPE-01	4695	1834	1404	Mercedes-AMG CLA operator manual supplement	https://static.oneweb.mercedes-benz.com/css-oom-assets/en-ca/pdf/mercedes-amg-cla-supplement-september-2019-1.pdf
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data Mercedes-Benz C-Class W205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-generation-5884
EU-TESLA-MODEL-3-I-SEDAN-01	4694	1849	1443	Tesla Model 3 official specifications	https://www.tesla.com/ownersmanual/model3/en_us/GUID-E414862C-CFA1-4A0B-9548-BE21C32CAA58.html
EU-RENAULT-KADJAR-I-FACELIFT-SUV-01	4489	1836	1613	Renault Kadjar official brochure	https://cdn.group.renault.com/ren/gb/transversal-assets/brochures/renault-kadjar-brochure.pdf
EU-RENAULT-KANGOO-II-X61-MPV-SWB-01	4282	1829	1801	Renault Kangoo official dimensions	https://www.renault.ps/en/cars/kangoo/dimensions.html
EU-RENAULT-KANGOO-II-X61-MPV-LWB-01	4666	1829	1802	Renault Kangoo official dimensions	https://www.renault.ps/en/cars/kangoo/dimensions.html
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Auto-Data Dacia Dokker	https://www.auto-data.net/en/dacia-dokker-generation-3726
EU-MERCEDES-BENZ-AMG-GT-R190-GT-R-ROADSTER-01	4551	2007	1260	Automobile-Catalog Mercedes-AMG GT R Roadster	https://www.automobile-catalog.com/car/2019/2874965/mercedes-amg_gt_r_roadster.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3601-3700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.denso-am.eu/catalog/pv/135645 "Car parts for FORD TRANSIT Platform/Chassis (E_ _), 2.5 TD, 55kW(75ps), 4HA, 4HD | DENSO"
[2]: https://lakinet.ee/tecdoc/articles/en/p/39/14264/135842/ "Passenger cars • GMC • SIERRA 2500 HD Extended Cab Pickup • SIERRA 2500 HD Extended Cab Pickup 6.0 CNG 4WD (LQ4(364CUV8)) (09.2001 - 12.2005) - LakiNet"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3165 行）
- 累计尺寸组：dimension_groups_final.tsv（1470 行）

