# 任务：all 第 1-100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0001__e8699d96


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1-100 行

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
all 第 1-100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-E-TRON-GE-SUV-01	4901	1935	1632
EU-AUDI-Q3-II-F3-SUV-01	4484	1849	1616
EU-BMW-X3-G01-M40I-SUV-01	4716	1897	1676
EU-CITROEN-BERLINGO-II-B9-ELECTRIC-MPV-01	4380	1810	1822
EU-CITROEN-BERLINGO-II-B9-MULTISPACE-MPV-01	4380	1810	1801
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480
EU-HYUNDAI-TUCSON-I-SUV-01	4325	1795	1680
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1650
EU-PEUGEOT-BOXER-II-250-VAN-L1H1-01	4963	2050	2254
EU-PEUGEOT-BOXER-II-250-VAN-L1H2-01	4963	2050	2522
EU-PEUGEOT-BOXER-II-250-VAN-L2H1-01	5413	2050	2254
EU-PEUGEOT-BOXER-II-250-VAN-L2H2-01	5413	2050	2522
EU-PEUGEOT-BOXER-II-250-VAN-L3H2-01	5998	2050	2522
EU-PEUGEOT-BOXER-II-250-VAN-L3H3-01	5998	2050	2760
EU-PEUGEOT-BOXER-II-250-VAN-L4H2-01	6363	2050	2522
EU-PEUGEOT-BOXER-II-250-VAN-L4H3-01	6363	2050	2760
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	5075	2070	2307
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	5075	2070	2500
EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	5575	2070	2499
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	6225	2070	2488
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	6225	2070	2744
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	5399	1956	1971
EU-TOYOTA-PROACE-II-VERSO-4X4-LONG-01	5309	1920	1940
EU-TOYOTA-PROACE-II-VERSO-4X4-MEDIUM-01	4959	1920	1940
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
EU-VW-GOLF-VIII-CD1-HATCHBACK-01	4284	1789	1456

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
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
Mercedes-benz	Gls	580 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	360	489	Nov 2019	-	2024-03-01	138495
Audi	E-Tron	55 Quattro	SUV	Allrad	Elektro	300	408	Sep 2019	Jul 2023	2026-03-01	138500
Peugeot	Expert	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Sep 2019	Dec 2022	2025-12-01	138504
Peugeot	Traveller	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Sep 2019	Dec 2022	2025-12-01	138505
Mercedes-benz	Gle	GLE 350 D 4-matic	SUV	Allrad	Diesel	200	272	Nov 2019	Mar 2023	2024-03-01	138508
Mercedes-benz	Gle	GLE 400 D 4-matic	SUV	Allrad	Diesel	243	330	Nov 2019	Mar 2023	2024-03-01	138509
Mercedes-benz	Gle	AMG GLE 53 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	320	435	Nov 2019	-	2024-03-01	138510
Citroën	Berlingo	Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Oct 2019	-	2024-03-01	138514
Fiat	Ducato	140 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138535
Fiat	Ducato	160 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138536
Fiat	Ducato	160 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138537
Fiat	Ducato	140 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138538
Fiat	Ducato	140 Multijet 2,3 D	Bus	Frontantrieb	Diesel	103	140	May 2019	-	2024-03-01	138539
Fiat	Ducato	160 Multijet 2,3 D	Bus	Frontantrieb	Diesel	118	160	May 2019	-	2024-03-01	138540
Fiat	Ducato	180 Multijet 2,3 D	Bus	Frontantrieb	Diesel	130	177	May 2019	-	2024-03-01	138541
Mazda	Mx-30	E-skyactiv	SUV	Frontantrieb	Elektro	107	145	May 2020	-	2024-03-01	138574
Mercedes-benz	Gls	AMG 63 4matic+ EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Nov 2019	-	2024-03-01	138594
Mercedes-benz	Gls	Maybach 600 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	410	557	Nov 2019	-	2024-03-01	138595
Mercedes-benz	Gle	AMG GLE 63 EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	420	571	Nov 2019	Mar 2023	2024-03-01	138596
Mercedes-benz	Gle	AMG GLE 63 S EQ Boost 4-matic+	SUV	Allrad	Benzin/Elektro	450	612	Nov 2019	-	2024-03-01	138597
Citroën	Jumper iii	2.2 Bluehdi 120	Kasten	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138598
Citroën	Jumper iii	2.2 Bluehdi 140	Kasten	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138599
Citroën	Jumper iii	2.2 Bluehdi 165	Kasten	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138600
Honda	Civic x	1.6 I-vtec LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	92	125	Jan 2019	Dec 2022	2024-03-01	138601
Citroën	Jumper iii	2.2 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138602
Citroën	Jumper iii	2.2 Bluehdi 140	Bus	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138603
Citroën	Jumper iii	2.2 Bluehdi 165	Bus	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138604
Citroën	Jumper iii	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2025-12-01	138605
Citroën	Jumper iii	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2025-12-01	138606
Citroën	Jumper iii	2.2 Bluehdi 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2025-12-01	138607
Lada	Vesta	1.6	Stufenheck	Frontantrieb	Benzin	83	113	Nov 2019	-	2024-03-01	138623
Lada	Vesta	1.6	Kombi	Frontantrieb	Benzin	83	113	Nov 2019	-	2024-03-01	138624
Citroën	Jumper iii	2.0 Bluehdi 130 4X4	Kasten	Allrad	Diesel	96	130	Nov 2015	Sep 2019	2025-12-01	138629
Citroën	Jumper iii	2.2 HDI 130 4X4	Kasten	Allrad	Diesel	96	130	Jan 2012	May 2016	2025-12-01	138630
Peugeot	Boxer	2.2 Bluehdi 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Aug 2019	Oct 2023	2024-05-01	138631
Peugeot	Boxer	2.2 Bluehdi 165	Pritsche/Fahrgestell	Frontantrieb	Diesel	121	165	Aug 2019	Oct 2023	2024-05-01	138632
Peugeot	Boxer	2.2 Bluehdi 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Aug 2019	Oct 2023	2024-05-01	138639
Renault	Master pro	DCI 120	Kasten	Heckantrieb	Diesel	85	116	Jun 2005	Apr 2010	2024-03-01	138646
Renault	Master pro	DCI 160	Kasten	Heckantrieb	Diesel	115	156	May 2004	Apr 2010	2024-03-01	138649
Renault	Master pro	DCI 130	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	131	Jun 2005	Apr 2010	2024-03-01	138654
Renault	Master pro	DCI 150	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Jun 2005	Apr 2010	2024-03-01	138655
Renault	Trafic iii	1.6 DCI 120	Kasten	Frontantrieb	Diesel	89	121	Jul 2015	-	2024-03-01	138657
Infiniti	Qx50 ii	2.0 AWD	SUV	Allrad	Benzin	197	268	Nov 2017	-	2024-03-01	138664
Lynk & CO	1	HEV	SUV	Frontantrieb	Benzin/Elektro	145	197	Nov 2021	-	2024-03-01	138665
Mercedes-benz	R-Klasse	R 300 4-matic	Großraumlimousine	Allrad	Benzin	170	231	Jul 2009	Dec 2011	2024-03-01	138666
Ford	Kuga iii	2.5 Duratec Plug-in-hybrid	SUV	Frontantrieb	Benzin/Elektro	165	224	Jul 2019	-	2024-03-01	138670
Ford	Kuga iii	2.0 Ecoblue Mhev	SUV	Frontantrieb	Diesel/Elektro	110	150	Jul 2019	-	2024-03-01	138671
Ford	Kuga iii	2.0 Ecoblue 4X4	SUV	Allrad	Diesel	140	190	Jul 2019	-	2024-03-01	138672
Mercedes-benz	Sprinter 4,6-T	411 CDI	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Apr 2016	Dec 2018	2024-03-01	138674
Ford	Kuga iii	1.5 Ecoblue	SUV	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138675
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	88	120	Jul 2019	-	2024-03-01	138676
Opel	Zafira	1.9 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	110	150	Jul 2005	Apr 2015	2024-03-01	138677
Peugeot	208 ii	1.5 Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	131	Sep 2019	-	2024-03-01	138678
Opel	Zafira	1.9 Cdti VAN	Kasten/Großraumlimousine	Frontantrieb	Diesel	88	120	Jul 2005	Apr 2015	2024-03-01	138679
Opel	Zafira	2.2 DGI VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin	110	150	Jul 2005	Dec 2011	2024-03-01	138680
Opel	Zafira	2.0 VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin	147	200	Jul 2005	Dec 2010	2024-03-01	138681
Opel	Zafira	1.6 CNG VAN	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Jul 2005	Apr 2015	2024-03-01	138682
Ford USA	Explorer	3.0 Ecoboost Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	336	457	Jul 2019	-	2024-03-01	138692
BMW	5	530 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	170	231	Jul 2019	Jun 2020	2024-03-01	138694
BMW	5	530 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	170	231	Jul 2019	Jun 2023	2024-03-01	138696
BMW	X3	Xdrive 30 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	215	292	Dec 2019	-	2024-03-01	138698
VW	Golf viii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	138699
VW	Golf viii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2019	-	2024-03-01	138700
VW	Golf viii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	85	116	Aug 2019	-	2024-03-01	138701
VW	Golf viii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Aug 2019	-	2024-03-01	138702
Renault	Clio v	1.0 SCE 65	Schrägheck	Frontantrieb	Benzin	48	65	Nov 2019	-	2026-05-01	138714
Volvo	Xc90 ii	D5 Drive Polestar AWD	SUV	Allrad	Diesel	176	239	Mar 2016	Dec 2021	2024-05-01	138715
Volvo	Xc90 ii	T5 Drive-e Polestar AWD	SUV	Allrad	Benzin	176	239	Oct 2017	Dec 2020	2024-05-01	138716
Volvo	Xc90 ii	T5 Drive-e Polestar AWD	SUV	Allrad	Benzin	192	261	Jan 2017	Dec 2021	2025-06-01	138717
Volvo	Xc40	T5 Polestar AWD	SUV	Allrad	Benzin	183	249	Oct 2017	Sep 2019	2024-03-01	138718
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	140	190	Nov 2019	Jun 2023	2024-03-01	138720
Hyundai	I30	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	80	109	Jan 2009	Nov 2011	2024-03-01	138721
BMW	5	520 D Mild-hybrid	Stufenheck	Heckantrieb	Diesel/Elektro	120	163	Nov 2019	Jun 2023	2024-03-01	138722
BMW	5	520 D Mild-hybrid Xdrive	Stufenheck	Allrad	Diesel/Elektro	140	190	Nov 2019	Jun 2023	2024-03-01	138723
BMW	5	520 D Mild-hybrid	Kombi	Heckantrieb	Diesel/Elektro	140	190	Nov 2019	-	2024-03-01	138724
Hyundai	Tucson	2.0 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	104	141	Jun 2004	Mar 2010	2024-03-01	138725
BMW	5	520 D Mild-hybrid Xdrive	Kombi	Allrad	Diesel/Elektro	140	190	Nov 2019	-	2024-03-01	138726
Hyundai	I30	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	80	109	Nov 2009	Jun 2012	2024-03-01	138727
Hyundai	I10 i	1.1 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	48	65	Jan 2009	Dec 2013	2024-03-01	138740
VW	Passat alltrack b8 variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	206	280	Nov 2018	Mar 2024	2025-02-03	138741
Renault	Megane i kombi van	1.9 D	Kasten/Kombi	Frontantrieb	Diesel	47	64	Feb 2000	Sep 2000	2024-03-01	138746
Renault	Megane i kombi van	1.9 DTI	Kasten/Kombi	Frontantrieb	Diesel	59	80	Apr 2001	Jul 2003	2024-03-01	138749
Renault	Megane i kombi van	1.4	Kasten/Kombi	Frontantrieb	Benzin	70	95	Apr 2001	Jul 2003	2024-03-01	138750
Renault	Megane i kombi van	1.9 DCI	Kasten/Kombi	Frontantrieb	Diesel	75	102	Apr 2001	Jul 2003	2024-03-01	138751
Renault	Megane i kombi van	1.9 DCI	Kasten/Kombi	Frontantrieb	Diesel	77	105	Apr 2001	Jul 2003	2024-03-01	138753


--- Round 1 / 首次发送 ---
## 更新点

* 命中跨批次缓存中的 6 个既有尺寸组。
* 闭合 15 个 Ktype，均为发动机、功率或驱动配置差异，不重新抓取尺寸。
* 本轮未创建或修正尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：15
* PENDING／尚未闭合：85
* READY 映射：15
* 已确认并引用尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138446	138446	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138447	138447	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138449	138449	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138450	138450	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138451	138451	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH		READY
138500	138500	SUV	e-tron GE	GE	5	EU-AUDI-E-TRON-GE-SUV-01	HIGH		READY
138699	138699	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
138700	138700	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
138701	138701	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
138702	138702	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-01	HIGH		READY
138714	138714	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH		READY
138715	138715	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
138716	138716	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
138717	138717	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
138725	138725	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无。本轮 6 个尺寸组全部复用跨批次已有缓存，不重复输出。

## 下一步优先处理

1. 优先闭合单一外廓的乘用车组：Audi A1、A6 allroad C8、Mercedes-Benz GLE/GLS、Mazda MX-30、Ford Kuga III、Peugeot 208 II。
2. 单独核对可能具有性能版外廓差异的 Audi RS Q3、Mercedes-AMG/Maybach GLS 和 AMG GLE。
3. 最后集中处理需要按轴距、车顶、底盘或客车长度拆分的 Ducato、Jumper、Boxer、Master、Sprinter、Proace、Expert、Traveller 和 Trafic。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

- 本轮闭合 8 个 Ktype，新增 8 条 READY 映射。
- 首次创建并闭合 6 个尺寸组。
- Audi A1 三个动力版本复用同一 GB 五门车身尺寸组。
- 上一轮已经引用的 6 个既有尺寸组未重复输出。

## 当前批次进度

- 输入 Ktype：100
- READY Ktype：23
- PENDING Ktype：77
- READY 映射：23
- 已确认并引用尺寸组：12
- 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138405	138405	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138406	138406	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138407	138407	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH		READY
138429	138429	Sedan	Pride I	DA	4	EU-KIA-PRIDE-DA-SEDAN-01	HIGH		READY
138460	138460	SUV	ix35 I facelift	LM	5	EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	HIGH		READY
138490	138490	Van	Astra K	B16	5	EU-OPEL-ASTRA-K-VAN-01	HIGH	五门掀背式货运版外廓。	READY
138574	138574	SUV	MX-30 I	DR	5	EU-MAZDA-MX-30-DR-SUV-01	HIGH		READY
138601	138601	Sedan	Civic X facelift	FC5	4	EU-HONDA-CIVIC-X-FC5-SEDAN-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Audi A1 Sportback official technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/836/file_en/c3f2a4a26d3756035f8e8169b65605e9d8adeb2e/eTD-Audi-A1-Sportback-25-TFSI-70kW_240314.pdf?1710585529=&disposition=attachment
EU-KIA-PRIDE-DA-SEDAN-01	3935	1605	1460	Automobile-Catalog Kia Pride Beta 1.3i	https://www.automobile-catalog.com/car/1998/1340540/kia_pride_beta_1_3i.html
EU-HYUNDAI-IX35-LM-FACELIFT-SUV-01	4410	1820	1665	Hyundai ix35 2014 Owner's Manual	https://www.carmanualsonline.info/hyundai-ix35-2014-owners-manual/?srch=dimensions
EU-OPEL-ASTRA-K-VAN-01	4370	1809	1485	Opel Astra Hatchback and Sports Tourer Price and Specification Guide	https://www.opel.ie/content/dam/opel/ireland/vehicles/astra/pdf/Jan21OpeAstraPriceSpecGuide.pdf
EU-MAZDA-MX-30-DR-SUV-01	4395	1795	1555	Mazda MX-30 official brochure	https://media-assets.mazda.eu/raw/upload/mazdaes/globalassets/pdfs/mazda-mx-30/catalogo_mx-30-2022.pdf
EU-HONDA-CIVIC-X-FC5-SEDAN-FACELIFT-01	4662	1799	1416	Honda Civic Sedan official brochure	https://www.honda.co.nz/assets/Brochures/Web_20YM_Civic_Sedan_2020.pdf
```

## 下一步优先处理

- 优先闭合 Lada Vesta Sedan/Wagon、Infiniti QX50 II、Volvo XC40、Peugeot 208 II、Ford Explorer PHEV 和 Passat Alltrack B8。
- 随后处理需要按改款或性能外廓拆分的 BMW 5、Mercedes-Benz GLE/GLS 和 Ford Kuga III。
- 最后集中处理 Proace、Expert、Traveller、Berlingo、Ducato、Jumper、Boxer、Master、Trafic 与 Sprinter 的多轴距、多车顶或底盘分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: ChatGPT 对话已达到长度上限，需要在新聊天中创建分支

