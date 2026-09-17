# 任务：all 第 201-300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0003__14164a4d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 201-300 行

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
all 第 201-300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Ecosport	1.5 Tdci	SUV	Frontantrieb	Diesel	74	100	May 2015	-	2024-03-01	119943
Volvo	V90 ii	T5	Kombi	Frontantrieb	Benzin	187	254	Mar 2016	Dec 2018	2024-05-01	119944
Volvo	V90 ii	T6 AWD	Kombi	Allrad	Benzin	235	320	Mar 2016	Dec 2018	2024-05-01	119945
Volvo	V90 ii	D4	Kombi	Frontantrieb	Diesel	140	190	Mar 2016	Dec 2021	2024-05-01	119946
Volvo	V90 ii	D5 AWD	Kombi	Allrad	Diesel	173	235	Mar 2016	Dec 2021	2024-05-01	119947
Volvo	V90 ii	T8 Plug-in-hybrid AWD	Kombi	Allrad	Benzin/Elektro	299	407	Mar 2016	Dec 2018	2024-03-01	119948
Volvo	S90 ii	T6 AWD	Stufenheck	Allrad	Benzin	235	320	Mar 2016	Dec 2021	2024-05-01	119949
Volvo	S90 ii	D5 AWD	Stufenheck	Allrad	Diesel	173	235	Mar 2016	Dec 2021	2024-05-01	119950
Volvo	S90 ii	D4	Stufenheck	Frontantrieb	Diesel	140	190	Mar 2016	Dec 2021	2024-05-01	119951
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	110	150	Oct 2015	-	2024-03-01	119958
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	132	180	Oct 2015	-	2024-03-01	119959
Audi	Q2	1.4 Tfsi	SUV	Frontantrieb	Benzin	110	150	Jun 2016	-	2024-03-01	119960
Audi	Q2	1.0 Tfsi	SUV	Frontantrieb	Benzin	85	115	Oct 2016	Oct 2020	2024-03-01	119962
Audi	Q2	1.6 TDI	SUV	Frontantrieb	Diesel	85	115	Jun 2016	Jul 2018	2024-03-01	119964
Audi	Q2	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Sep 2016	-	2024-03-01	119965
Audi	Q2	2.0 TDI Quattro	SUV	Allrad	Diesel	110	150	Sep 2016	-	2024-03-01	119966
Audi	Q2	2.0 TDI Quattro	SUV	Allrad	Diesel	140	190	Jul 2016	Aug 2018	2024-03-01	119967
Citroën	C4 picasso ii	1.2 THP 110	Großraumlimousine	Frontantrieb	Benzin	81	110	Apr 2016	-	2024-03-01	119968
Smart	Fortwo	0.9 Brabus	Coupe	Heckantrieb	Benzin	80	109	Jul 2016	-	2024-03-01	119981
Smart	Forfour	0.9 Brabus	Schrägheck	Heckantrieb	Benzin	80	109	Jul 2016	-	2024-03-01	119983
Smart	Fortwo	0.9 Brabus	Cabriolet	Heckantrieb	Benzin	80	109	Jul 2016	-	2024-03-01	119985
Hyundai	Highway van	2.0 Crdi	Kasten/Großraumlimousine	Frontantrieb	Diesel	83	113	Mar 2001	Mar 2004	2024-03-01	120007
Hyundai	Highway van	2.0 Cvvt	Kasten/Großraumlimousine	Frontantrieb	Benzin	104	141	Nov 2003	Mar 2004	2024-03-01	120008
Hyundai	Sonata vi	2.0 Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	110	150	Jan 2011	Jun 2014	2024-03-01	120019
Peugeot	Expert	1.6 Bluehdi 95	Kasten	Frontantrieb	Diesel	70	95	Apr 2016	Dec 2019	2025-12-01	120075
Peugeot	Expert	1.6 Bluehdi 115	Kasten	Frontantrieb	Diesel	85	116	Apr 2016	Dec 2019	2025-12-01	120076
Peugeot	Expert	2.0 Bluehdi 120	Kasten	Frontantrieb	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	120077
Peugeot	Expert	2.0 Bluehdi 150	Kasten	Frontantrieb	Diesel	110	150	Apr 2016	Dec 2022	2026-01-01	120078
Peugeot	Expert	2.0 Bluehdi 180	Kasten	Frontantrieb	Diesel	130	177	Apr 2016	Apr 2025	2025-12-01	120079
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	107	145	May 2016	-	2024-03-01	120080
Abarth	500	1.4	Schrägheck	Frontantrieb	Benzin	121	165	May 2016	-	2024-03-01	120081
Mercedes-benz	C-Klasse	C 180	Cabriolet	Heckantrieb	Benzin	115	156	Jun 2016	Aug 2020	2024-03-01	120121
Mercedes-benz	C-Klasse	C 200	Cabriolet	Heckantrieb	Benzin	135	184	Jun 2016	May 2018	2024-03-01	120122
Mercedes-benz	C-Klasse	C 200 4-matic	Cabriolet	Allrad	Benzin	135	184	Jun 2016	May 2018	2024-03-01	120123
Mercedes-benz	C-Klasse	C 250	Cabriolet	Heckantrieb	Benzin	155	211	Jun 2016	May 2018	2024-03-01	120124
Mercedes-benz	C-Klasse	C 300	Cabriolet	Heckantrieb	Benzin	180	245	Jun 2016	May 2018	2024-03-01	120125
Mercedes-benz	C-Klasse	C 400 4-matic	Cabriolet	Allrad	Benzin	245	333	Jun 2016	Apr 2023	2024-03-01	120126
Mercedes-benz	C-Klasse	AMG C 43 4-matic	Cabriolet	Allrad	Benzin	270	367	Oct 2016	May 2018	2024-03-01	120127
Mercedes-benz	C-Klasse	AMG C 63	Cabriolet	Heckantrieb	Benzin	350	476	Oct 2016	Apr 2023	2024-03-01	120128
Mercedes-benz	C-Klasse	AMG C 63 S	Cabriolet	Heckantrieb	Benzin	375	510	Oct 2016	Apr 2023	2024-03-01	120129
Mercedes-benz	C-Klasse	C 220 D	Cabriolet	Heckantrieb	Diesel	125	170	Jun 2016	May 2018	2024-03-01	120130
Mercedes-benz	C-Klasse	C 220 D 4-matic	Cabriolet	Allrad	Diesel	125	170	Jun 2016	May 2018	2024-03-01	120131
Mercedes-benz	C-Klasse	C 250 D	Cabriolet	Heckantrieb	Diesel	150	204	Jun 2016	May 2018	2024-03-01	120132
Lamborghini	Centenario	6.5 LP 770-4	Coupe	Allrad	Benzin	566	770	Apr 2016	-	2024-03-01	120133
Lamborghini	Aventador	6.5 LP 700-4 SV AWD	Targa	Allrad	Benzin	552	751	Mar 2015	-	2025-06-01	120177
VW	Sharan	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	135	184	May 2016	Jul 2018	2024-03-01	120178
Seat	Alhambra	2.0 TDI 4drive	Großraumlimousine	Allrad	Diesel	135	184	May 2016	Aug 2018	2024-03-01	120179
VW	Golf vii	2.0 GTI Clubsport S	Schrägheck	Frontantrieb	Benzin	228	310	Sep 2016	Mar 2017	2024-03-01	120193
VW	Amarok	3.0 TDI 4motion	Pick-up	Allrad	Diesel	165	224	Jun 2016	May 2022	2024-03-01	120195
Skoda	Octavia	1.0 TSI	Schrägheck	Frontantrieb	Benzin	85	115	May 2016	Oct 2020	2024-03-01	120206
Skoda	Octavia	1.0 TSI	Kombi	Frontantrieb	Benzin	85	115	May 2016	Oct 2020	2024-03-01	120207
VW	Touran	1.6 TDI	Großraumlimousine	Frontantrieb	Diesel	85	115	May 2016	Jul 2019	2025-11-01	120208
VW	Tiguan	1.4 TSI 4motion	SUV	Allrad	Benzin	110	150	May 2016	Mar 2022	2026-07-01	120209
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	85	115	May 2016	Jul 2019	2024-03-01	120210
Mercedes-benz	Sprinter 4,6-T	414 CDI	Kasten	Heckantrieb	Diesel	105	143	May 2016	Dec 2018	2024-03-01	120212
Alfa Romeo	Giulia	2.2 D	Stufenheck	Heckantrieb	Diesel	100	136	Oct 2015	-	2024-03-01	120213
Honda	Jazz ii	1.4 Idsi	Schrägheck	Frontantrieb	Benzin	61	83	Dec 2006	Oct 2008	2024-03-01	120218
Opel	Combo	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Mar 2016	-	2024-03-01	120222
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	135	184	Jul 2016	Jun 2019	2024-03-01	120226
Alfa Romeo	Mito	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	88	120	Apr 2016	Oct 2018	2024-03-01	120228
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	165	224	Oct 2015	Jun 2019	2024-03-01	120229
BMW	1	M 140 I	Schrägheck	Heckantrieb	Benzin	250	340	Oct 2015	Jun 2019	2024-03-01	120235
BMW	1	M 140 I Xdrive	Schrägheck	Allrad	Benzin	250	340	Sep 2015	Jun 2019	2024-03-01	120236
Renault	Trafic iii	1.6 DCI 95	Kasten	Frontantrieb	Diesel	70	95	Jul 2015	-	2024-03-01	120237
Renault	Trafic iii	1.6 DCI 125	Kasten	Frontantrieb	Diesel	92	125	Jul 2015	-	2024-03-01	120239
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	135	184	Jul 2016	Jun 2019	2024-03-01	120240
Renault	Trafic iii	1.6 DCI 145	Kasten	Frontantrieb	Diesel	107	145	Jul 2015	-	2024-03-01	120241
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	165	224	Jul 2016	Jun 2019	2024-03-01	120242
BMW	1	M 140 I	Schrägheck	Heckantrieb	Benzin	250	340	Jul 2016	Jun 2019	2024-03-01	120244
BMW	1	M 140 I Xdrive	Schrägheck	Allrad	Benzin	250	340	Jul 2016	Jun 2019	2024-03-01	120245
BMW	2	220 I	Coupe	Heckantrieb	Benzin	135	184	Sep 2015	Jun 2021	2024-03-01	120246
BMW	2	230 I	Coupe	Heckantrieb	Benzin	185	252	Jul 2016	Jun 2021	2024-03-01	120247
BMW	2	M 240 I	Coupe	Heckantrieb	Benzin	250	340	Sep 2015	Jun 2021	2024-03-01	120248
BMW	2	M 240 I Xdrive	Coupe	Allrad	Benzin	250	340	Sep 2015	Jun 2021	2024-03-01	120249
BMW	2	220 I	Cabriolet	Heckantrieb	Benzin	135	184	Sep 2015	Jun 2021	2024-03-01	120250
BMW	2	230 I	Cabriolet	Heckantrieb	Benzin	185	252	Jul 2016	Jun 2021	2024-03-01	120251
BMW	2	M 240 I	Cabriolet	Heckantrieb	Benzin	250	340	Sep 2015	Jun 2021	2024-03-01	120252
BMW	2	M 240 I Xdrive	Cabriolet	Allrad	Benzin	250	340	Sep 2015	Jun 2021	2024-03-01	120253
Toyota	Proace	1.6 D4D	Kasten	Frontantrieb	Diesel	70	95	Feb 2016	Apr 2020	2025-02-03	120259
Toyota	Proace	1.6 D4D	Kasten	Frontantrieb	Diesel	85	116	Feb 2016	Apr 2020	2025-02-03	120260
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	110	150	Feb 2016	Dec 2022	2026-01-01	120261
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	130	177	Feb 2016	Apr 2025	2026-01-01	120263
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	90	122	Feb 2016	Dec 2022	2026-01-01	120264
BMW	3	330 I	Schrägheck	Heckantrieb	Benzin	185	252	Jul 2016	-	2024-03-01	120265
BMW	3	330 I Xdrive	Schrägheck	Allrad	Benzin	185	252	Jul 2016	-	2024-03-01	120266
BMW	3	340 I	Schrägheck	Heckantrieb	Benzin	240	326	Jul 2016	-	2024-03-01	120267
BMW	3	340 I Xdrive	Schrägheck	Allrad	Benzin	240	326	Jul 2016	-	2024-03-01	120268
Renault	Megane iv	1.6 DCI 165	Schrägheck	Frontantrieb	Diesel	120	163	Nov 2015	-	2024-03-01	120270
Renault	Megane iv grandtour	1.2 TCE 100	Kombi	Frontantrieb	Benzin	74	101	Apr 2016	-	2025-12-01	120272
Renault	Megane iv grandtour	1.2 TCE 130	Kombi	Frontantrieb	Benzin	97	130	Apr 2016	-	2024-03-01	120273
Renault	Megane iv grandtour	1.6 TCE 205	Kombi	Frontantrieb	Benzin	151	205	Apr 2016	-	2024-03-01	120274
Renault	Megane iv grandtour	1.5 DCI 90	Kombi	Frontantrieb	Diesel	66	90	Apr 2016	-	2024-03-01	120275
Renault	Megane iv grandtour	1.5 DCI 110	Kombi	Frontantrieb	Diesel	81	110	Apr 2016	-	2024-03-01	120276
Renault	Megane iv grandtour	1.6 DCI 130	Kombi	Frontantrieb	Diesel	96	130	Apr 2016	-	2024-03-01	120277
Renault	Megane iv grandtour	1.6 DCI 165	Kombi	Frontantrieb	Diesel	120	163	Apr 2016	-	2024-03-01	120279
Mercedes-benz	Glc	250 4-matic	SUV	Allrad	Benzin	155	211	Jun 2016	Apr 2019	2024-03-01	120283
Mercedes-benz	Glc	220 D 4-matic	SUV	Allrad	Diesel	125	170	Jun 2016	Apr 2019	2024-03-01	120285
Mercedes-benz	Glc	250 D 4-matic	SUV	Allrad	Diesel	150	204	Jun 2016	Apr 2019	2024-03-01	120286
BMW	7	M 760 I, LI Xdrive	Stufenheck	Allrad	Benzin	448	610	Dec 2016	Feb 2019	2024-03-01	120288
BMW	7	750 D, LD Xdrive	Stufenheck	Allrad	Diesel	294	400	Jul 2016	Oct 2020	2024-03-01	120295


--- Round 1 / 首次发送 ---
## 更新点

* 首次闭合 6 个尺寸组，新增 11 条 `READY` 映射，覆盖 Volvo V90 II、Alfa Romeo Giulia 952、三种 smart BRABUS 车身及 Abarth 595 2016 改款。
* Volvo 官方尺寸页明确区分 `1879 mm` 车身宽度与 `2019 mm` 含后视镜宽度；Giulia 与 Abarth 资料也分别列出车身宽度和含镜宽度。([沃尔沃汽车][1])
* smart 官方 BRABUS 资料确认三种车身的精确长宽高；对应 Automobile-Catalog 车型页进一步明确宽度为不含后视镜口径。
* 暂未将跨改款 Ktype、混合车身形式或多轴距/多车顶商用车强行关联尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：11
* 待处理输入 Ktype：89
* READY 映射行：11
* PENDING 输入记录：89
* 已确认尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119944	119944	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119945	119945	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119948	119948	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119958	119958	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
119959	119959	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
119981	119981	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH	C453双门硬顶外廓。	READY
119983	119983	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH	W453五门掀背外廓。	READY
119985	119985	Convertible	Fortwo III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-01	HIGH	A453双门敞篷外廓。	READY
120080	120080	Hatchback	595 facelift 2016		3	EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	HIGH	输入500对应2016改款595三门掀背外廓。	READY
120081	120081	Hatchback	595 facelift 2016		3	EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	HIGH	输入500对应2016改款595三门掀背外廓。	READY
120213	120213	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Support V90 2017 Dimensions	https://www.volvocars.com/en-jo/support/car/v90/16w46/article/871e942e897ca77dc0a801511788660a/
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436	Auto-Data Alfa Romeo Giulia (952) 2.2 JTD 180	https://www.auto-data.net/en/alfa-romeo-giulia-952-2.2-jtd-180hp-23735
EU-SMART-FORTWO-III-COUPE-01	2740	1663	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Fortwo Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2017/3155900/smart_fortwo_brabus_twinmatic.html
EU-SMART-FORFOUR-II-HATCHBACK-01	3525	1665	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Forfour Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2017/3155930/smart_forfour_brabus_twinmatic.html
EU-SMART-FORTWO-III-CONVERTIBLE-01	2740	1663	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Fortwo Cabrio Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2016/3155915/smart_fortwo_cabrio_brabus_twinmatic.html
EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	3660	1627	1485	Auto-Data Abarth 595 facelift 2016 1.4 T-Jet 145	https://www.auto-data.net/en/abarth-595-facelift-2016-1.4-t-jet-145hp-automatic-24658
```

## 下一步优先处理

1. 核对 Audi Q2、Volvo V90/S90、Skoda Octavia、VW Tiguan 等跨改款 Ktype，确认是否需要拆分 `prefl` 与 `facelift`。
2. 集中处理 Peugeot Expert、Toyota Proace、Renault Trafic、Mercedes Sprinter、Opel Combo 的长度、轴距和车顶派生分支。
3. 批量闭合 BMW 1/2/3/7、Mercedes C-Class Cabriolet/GLC、Renault Megane 等乘用车聚类。

推进信号：CONTINUE

[1]: https://www.volvocars.com/en-jo/support/car/v90/16w46/article/871e942e897ca77dc0a801511788660a/ "V90 Dimensions | Volvo Support EN-JO"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 复用既有 V90 II 尺寸组，补齐 2 个柴油版 Ktype 映射；本轮未重复输出该尺寸组。
* 首次闭合 Volvo S90 II 与 Audi Q2 GA 前期型尺寸组，共补齐 9 个映射。Volvo 官方资料分别列明 S90 的车身宽度与含后视镜宽度；Q2 前期型按 2016–2020 物理外廓建组。([沃尔沃汽车][1])
* BMW 1 系按 `F20/F21` 门数边界以及普通版、M140i 外部尺寸差异建立 4 个尺寸组，补齐 8 个 Ktype。BMW 官方技术资料确认 F20 为五门、F21 为三门，并显示 M140i 的长度及高度与普通版本不同。([press.bmwgroup.com][2])
* BMW 2 系按 `F22 Coupe/F23 Convertible` 及普通版、M240i 外廓差异建立 4 个尺寸组，补齐 8 个 Ktype。([press.bmwgroup.com][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：38
* PENDING 映射：62
* 已确认尺寸组：16
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119946	119946	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119947	119947	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119949	119949	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119950	119950	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119951	119951	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119960	119960	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119962	119962	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119964	119964	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119965	119965	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119966	119966	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119967	119967	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
120226	120226	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-01	HIGH	F21三门普通外廓。	READY
120229	120229	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-01	HIGH	F21三门普通外廓。	READY
120235	120235	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-M140-01	HIGH	F21三门M140i外廓。	READY
120236	120236	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-M140-01	HIGH	F21三门M140i外廓。	READY
120240	120240	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-01	HIGH	F20五门普通外廓。	READY
120242	120242	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-01	HIGH	F20五门普通外廓。	READY
120244	120244	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-M140-01	HIGH	F20五门M140i外廓。	READY
120245	120245	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-M140-01	HIGH	F20五门M140i外廓。	READY
120246	120246	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-01	HIGH	F22双门普通外廓。	READY
120247	120247	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-01	HIGH	F22双门普通外廓。	READY
120248	120248	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-M240-01	HIGH	F22双门M240i外廓。	READY
120249	120249	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-M240-01	HIGH	F22双门M240i外廓。	READY
120250	120250	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-01	HIGH	F23双门普通敞篷外廓。	READY
120251	120251	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-01	HIGH	F23双门普通敞篷外廓。	READY
120252	120252	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-M240-01	HIGH	F23双门M240i敞篷外廓。	READY
120253	120253	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-M240-01	HIGH	F23双门M240i敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Support S90 Dimensions	https://www.volvocars.com/za/support/car/s90/16w46/article/871e942e897ca77dc0a801511788660a/
EU-AUDI-Q2-GA-SUV-PREFL-01	4191	1794	1508	Auto-Data Audi Q2 2016-2020	https://www.auto-data.net/en/audi-q2-model-2098
EU-BMW-1-F21-HATCHBACK-3D-01	4329	1765	1421	BMW Group PressClub BMW 1 Series 3 Door Hatch specifications	https://www.press.bmwgroup.com/global/article/attachment/T0260190EN/359669
EU-BMW-1-F21-HATCHBACK-3D-M140-01	4324	1765	1411	BMW Group PressClub BMW 1 Series 3 Door Hatch specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286639CS/417968
EU-BMW-1-F20-HATCHBACK-5D-01	4329	1765	1421	BMW Group PressClub BMW 1 Series 5-door technical data	https://www.press.bmwgroup.com/portugal/article/attachment/T0127857PT/416739
EU-BMW-1-F20-HATCHBACK-5D-M140-01	4324	1765	1411	BMW Group PressClub BMW 1 Series 5-door technical data	https://www.press.bmwgroup.com/portugal/article/attachment/T0127857PT/416739
EU-BMW-2-F22-COUPE-01	4432	1774	1418	BMW Group PressClub BMW 2 Series Coupe specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0162084EN/242844
EU-BMW-2-F22-COUPE-M240-01	4454	1774	1408	BMW Group PressClub BMW M240i Coupe specifications	https://www.press.bmwgroup.com/global/article/attachment/T0259974EN/385584
EU-BMW-2-F23-CONVERTIBLE-01	4432	1774	1413	BMW Group PressClub BMW 2 Series Convertible technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395388
EU-BMW-2-F23-CONVERTIBLE-M240-01	4454	1774	1403	BMW Group PressClub BMW M240i Convertible specifications	https://www.press.bmwgroup.com/global/article/attachment/T0260193EN/359688
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz C-Class A205 普通版、AMG C43 与 AMG C63/C63 S 的外廓分组。
2. 处理 Skoda Octavia、VW Touran/Tiguan、Renault Megane IV、Mercedes-Benz GLC 等单一车身聚类。
3. 最后集中拆分 Expert、Proace、Trafic、Sprinter、Combo 等多长度或多车顶商用车。

推进信号：CONTINUE

[1]: https://www.volvocars.com/za/support/car/s90/16w46/article/871e942e897ca77dc0a801511788660a/?utm_source=chatgpt.com "S90 Dimensions | Volvo Support ZA"
[2]: https://www.press.bmwgroup.com/global/article/attachment/T0260190EN/359669?utm_source=chatgpt.com "BMW Group PressClub"
[3]: https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395388?utm_source=chatgpt.com "Technical data 2 Series Convertible LCI (F23LCI) |"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增闭合 20 个输入 Ktype，共产生 22 条 `READY` 映射；其中 C63 与 C63 S 因 Ktype 横跨改款前后且外廓发生变化，分别派生 `prefl`、`facelift` 映射。
* Mercedes-Benz C-Class A205 普通敞篷、C43、C63/C63 S 改款前及改款后外廓已分别建组；改款后的 C63 与 C63 S 三维相同，复用同一尺寸组。
* Mercedes-Benz GLC X253 前期型闭合 1 个尺寸组；Renault Megane IV Grandtour 普通版闭合 1 个尺寸组。Megane GT 205/165 版本暂不并入普通组。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：58
* READY 映射行：60
* PENDING 输入 Ktype：42
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120121	120121	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120122	120122	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120123	120123	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120124	120124	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120125	120125	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120126	120126	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120127	120127	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C43-01	HIGH	A205 AMG C43外廓。	READY
120128_prefl	120128	Convertible	C-Class A205 pre-facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63-PREFL-01	HIGH	C63改款前外廓。	READY
120128_facelift	120128	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	HIGH	C63改款后外廓。	READY
120129_prefl	120129	Convertible	C-Class A205 pre-facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63S-PREFL-01	HIGH	C63 S改款前外廓。	READY
120129_facelift	120129	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	HIGH	C63 S改款后外廓。	READY
120130	120130	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120131	120131	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120132	120132	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120272	120272	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120273	120273	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120275	120275	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120276	120276	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120277	120277	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120283	120283	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
120285	120285	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
120286	120286	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	4686	1810	1409	Mercedes-Benz C-Class Coupe and Cabriolet official brochure	https://mercedes-benz-media.co.uk/assets/documents/original/894-cclasscoupecabrioletbrochure.pdf
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C43-01	4696	1810	1408	Mercedes-Benz USA 2017 AMG C43 Cabriolet specifications; Automobile-Catalog 2017 Mercedes-AMG C43 Cabriolet	https://media.mbusa.com/releases/release-078ed5dd551c4443b3a94488d26022a0-2017-mercedes-amg-c43-cabriolet-specifications; https://www.automobile-catalog.com/car/2017/2407325/mercedes-amg_c_43_4matic_cabriolet.html
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63-PREFL-01	4750	1877	1402	Mercedes-Benz USA 2017 AMG C63 and C63 S Cabriolet specifications	https://media.mbusa.com/releases/release-e1808cbe57354b168ecfb4636128aa8f-2017-mercedes-amg-c63-cabrio-and-c63-s-cabrio-specifications
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63S-PREFL-01	4750	1877	1405	Mercedes-Benz USA 2017 AMG C63 and C63 S Cabriolet specifications	https://media.mbusa.com/releases/release-e1808cbe57354b168ecfb4636128aa8f-2017-mercedes-amg-c63-cabrio-and-c63-s-cabrio-specifications
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	4751	1877	1404	Mercedes-Benz USA MY19 C-Class brochure; Automobile-Catalog 2019 Mercedes-AMG C63 Cabriolet; Automobile-Catalog 2019 Mercedes-AMG C63 S Cabriolet	https://www.mbusa.com/content/dam/mb-nafta/us/brochures/pdf/MY19_C-Class_WebPDF_181212.pdf; https://www.automobile-catalog.com/car/2019/2739365/mercedes-amg_c_63_cabriolet.html; https://www.automobile-catalog.com/car/2019/2739380/mercedes-amg_c_63_s_cabriolet.html
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449	Renault Megane Sport Tourer official press kit; Automobile-Catalog 2016 Renault Megane Grandtour dCi 90	https://www.press.renault.co.uk/assets/documents/original/17939-RE37517MeganeSTPressKitV1.pdf; https://www.automobile-catalog.com/car/2016/2984735/renault_megane_estate_grandtour_energy_dci_90.html
EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	4656	1890	1639	Mercedes-Benz GLC official brochure; Automobile-Catalog 2016 Mercedes-Benz GLC 250 4MATIC	https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-GLC-2016-INT.pdf; https://www.automobile-catalog.com/car/2016/2170805/mercedes-benz_glc_250_4matic.html
```

本轮尺寸组的无后视镜宽度及三维边界由 Mercedes-Benz、Renault 资料和对应车型规格页交叉闭合。([梅赛德斯-奔驰媒体中心][2])

## 下一步优先处理

1. 闭合 Skoda Octavia 掀背/旅行车、VW Golf Clubsport S、Touran、Tiguan、Sharan及 Seat Alhambra。
2. 独立核对 Megane IV GT Hatch 与 Grandtour GT 的悬架高度，避免误复用普通车身组。
3. 处理 Expert、Proace、Trafic、Sprinter、Combo 等多长度、多轴距及多车顶商用车派生分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2019/2170775/mercedes-benz_glc_220_d_4matic.html?utm_source=chatgpt.com "2019 Mercedes-Benz GLC 220 d 4MATIC Specs Review (125 kW / 170 PS / 168 hp) (up to June 2019 for Europe )"
[2]: https://media.mbusa.com/releases/release-078ed5dd551c4443b3a94488d26022a0-2017-mercedes-amg-c43-cabriolet-specifications?utm_source=chatgpt.com "2017 Mercedes-AMG C43 Cabriolet Specifications"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增闭合 16 个输入 Ktype，新增 16 条 `READY` 映射和 12 个尺寸组。
* 已闭合 EcoSport II、Sonata VI YF、BMW F34 Gran Turismo、Megane IV GT 掀背及 Grandtour GT；来源中的 `Width` 与单列含镜宽度区分时，采用不含后视镜口径。([汽车数据网][1])
* 已闭合 Sharan II、Alhambra II、Touran II 和 Honda Jazz I。Sharan 资料明确列出车身宽 `1904 mm`、含镜宽 `2081 mm`；Touran、Alhambra 和 Jazz 的车身边界及门数已确认。([汽车数据网][2])
* 已闭合 MiTo 955 BiFuel、Centenario Coupe 与 Aventador SV Roadster；MiTo 的能源标记差异不改变三门物理外廓，映射置信度保留为 `MEDIUM`。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* READY 映射行：76
* PENDING 输入 Ktype：26
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119943	119943	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	MEDIUM	五门SUV物理外廓。	READY
120019	120019	Sedan	Sonata VI (YF)	YF	4	EU-HYUNDAI-SONATA-VI-YF-SEDAN-01	MEDIUM	YF四门混合动力轿车外廓。	READY
120133	120133	Coupe	Centenario		2	EU-LAMBORGHINI-CENTENARIO-COUPE-01	HIGH	双门Coupe物理外廓。	READY
120177	120177	Convertible	Aventador LP750-4 SV Roadster		2	EU-LAMBORGHINI-AVENTADOR-LP750-SV-ROADSTER-01	MEDIUM	双门可拆卸车顶Roadster外廓。	READY
120178	120178	MPV	Sharan II facelift	7N	5	EU-VOLKSWAGEN-SHARAN-II-MPV-FACELIFT-01	HIGH	7N改款五门MPV外廓。	READY
120179	120179	MPV	Alhambra II facelift	7N	5	EU-SEAT-ALHAMBRA-II-MPV-FACELIFT-01	HIGH	7N改款五门MPV外廓。	READY
120208	120208	MPV	Touran II	5T	5	EU-VOLKSWAGEN-TOURAN-II-MPV-01	HIGH	5T五门MPV外廓。	READY
120218	120218	Hatchback	Jazz I (GD)		5	EU-HONDA-JAZZ-I-GD-HATCHBACK-01	MEDIUM	生产年月与功率对应GD五门外廓。	READY
120228	120228	Hatchback	MiTo 955	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	MEDIUM	955三门BiFuel外廓。	READY
120265	120265	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120266	120266	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120267	120267	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120268	120268	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120270	120270	Hatchback	Megane IV GT	BFB	5	EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	HIGH	BFB五门GT掀背外廓。	READY
120274	120274	Wagon	Megane IV Grandtour GT	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	HIGH	KFB五门GT旅行车外廓。	READY
120279	120279	Wagon	Megane IV Grandtour GT	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	HIGH	KFB五门GT旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Auto-Data Ford EcoSport II 1.5 TDCi	https://www.auto-data.net/en/ford-ecosport-ii-1.5-tdci-95hp-31851
EU-HYUNDAI-SONATA-VI-YF-SEDAN-01	4820	1835	1470	Auto-Data Hyundai Sonata VI YF Hybrid	https://www.auto-data.net/en/hyundai-sonata-vi-yf-2.4-209hp-hybrid-automatic-29665
EU-LAMBORGHINI-CENTENARIO-COUPE-01	4924	2062	1143	Auto-Data Lamborghini Centenario LP 770-4	https://www.auto-data.net/en/lamborghini-centenario-lp-770-4-6.5-v12-770hp-4wd-isr-28863
EU-LAMBORGHINI-AVENTADOR-LP750-SV-ROADSTER-01	4835	2030	1136	Auto-Data Lamborghini Aventador LP 750-4 Superveloce Roadster	https://www.auto-data.net/en/lamborghini-aventador-lp-750-4-superveloce-roadster-6.5-v12-750hp-4wd-22765
EU-VOLKSWAGEN-SHARAN-II-MPV-FACELIFT-01	4854	1904	1720	Auto-Data Volkswagen Sharan II facelift 2.0 TDI	https://www.auto-data.net/en/volkswagen-sharan-ii-facelift-2015-2.0-tdi-184hp-22719
EU-SEAT-ALHAMBRA-II-MPV-FACELIFT-01	4854	1904	1720	Auto-Data Seat Alhambra II 7N facelift 2.0 TDI	https://www.auto-data.net/en/seat-alhambra-ii-7n-facelift-2015-2.0-tdi-184hp-dsg-31108
EU-VOLKSWAGEN-TOURAN-II-MPV-01	4527	1829	1674	Auto-Data Volkswagen Touran II 1.6 TDI	https://www.auto-data.net/en/volkswagen-touran-ii-1.6-tdi-115hp-32222
EU-HONDA-JAZZ-I-GD-HATCHBACK-01	3830	1675	1525	Auto-Data Honda Jazz I 1.4	https://www.auto-data.net/en/honda-jazz-i-1.4-83hp-12141
EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2013 1.4 TP LPG	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2013-1.4-tp-120hp-lpg-24708
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508	Auto-Data BMW 3 Series Gran Turismo F34 LCI 340i	https://www.auto-data.net/en/bmw-3-series-gran-turismo-f34-lci-facelift-2016-340i-326hp-steptronic-24294
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438	Auto-Data Renault Megane IV GT 1.6 Energy dCi	https://www.auto-data.net/en/renault-megane-iv-gt-1.6-energy-dci-163hp-edc-22556
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457	Auto-Data Renault Megane IV Grandtour GT TCe; Auto-Data Renault Megane IV Grandtour GT dCi	https://www.auto-data.net/en/renault-megane-iv-grandtour-gt-1.6-energy-tce-205hp-edc-24656; https://www.auto-data.net/en/renault-megane-iv-grandtour-gt-1.6-energy-dci-165hp-edc-30062
```

## 下一步优先处理

1. 闭合 Golf VII Clubsport S、Octavia 掀背/旅行车、Tiguan II 与 Amarok 的乘用车和皮卡外廓。
2. 集中拆分 Expert、Proace、Trafic、Sprinter、Combo 的轴距、长度、车顶及客货车分支。
3. 最后处理 Hyundai Highway Van、C4 Picasso 可变高度边界及 BMW 7 系标准轴距/长轴派生。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/hyundai-sonata-vi-yf-generation-5500?utm_source=chatgpt.com "Hyundai Sonata VI (YF) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-sharan-ii-facelift-2015-2.0-tdi-184hp-22719 "Volkswagen Sharan II (facelift 2015) 2.0 TDI (184 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/it/alfa-romeo-mito-facelift-2013-1.4-tp-120hp-lpg-24708?utm_source=chatgpt.com "Alfa Romeo MiTo (facelift 2013) 1.4 TP (120 CV) LPG | Scheda Tecnica e consumi, Dimensioni"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Golf VII GTI Clubsport S 与 Amarok I facelift Double Cab，各新增一个尺寸组。Volkswagen 官方资料直接列明 Clubsport S 为三门车型且三维为 `4268 × 1799 × 1442 mm`；Amarok 224 PS Double Cab 的宽度字段与含镜宽度字段分列。([volkswagen-newsroom.com][1])
* Skoda Octavia III 两个 Ktype 均横跨 2017 年改款，因改款前后长度不同，分别拆分掀背与旅行车的 `prefl`、`facelift` 派生映射。([汽车数据网][2])
* 闭合 Tiguan II 前期型 2.0 TDI 115 前驱尺寸组；未将其与高度不同的 4MOTION 外廓合并。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：79
* READY 映射行：83
* PENDING 输入 Ktype：21
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120193	120193	Hatchback	Golf VII GTI Clubsport S		3	EU-VOLKSWAGEN-GOLF-VII-GTI-CLUBSPORT-S-HATCHBACK-01	HIGH	三门Clubsport S物理外廓。	READY
120195	120195	Pickup	Amarok I facelift		4	EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLE-CAB-FACELIFT-01	HIGH	四门Double Cab物理外廓。	READY
120206_prefl	120206	Hatchback	Octavia III pre-facelift	5E	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	5E五门掀背改款前外廓。	READY
120206_facelift	120206	Hatchback	Octavia III facelift	5E	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	5E五门掀背改款后外廓。	READY
120207_prefl	120207	Wagon	Octavia III Combi pre-facelift	5E	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	5E五门旅行车改款前外廓。	READY
120207_facelift	120207	Wagon	Octavia III Combi facelift	5E	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	5E五门旅行车改款后外廓。	READY
120210	120210	SUV	Tiguan II pre-facelift		5	EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-FWD-01	HIGH	前驱五门前期型SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLKSWAGEN-GOLF-VII-GTI-CLUBSPORT-S-HATCHBACK-01	4268	1799	1442	Volkswagen Newsroom Golf VII GTI vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-gti-profile-20033
EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLE-CAB-FACELIFT-01	5254	1954	1834	Auto-Data Volkswagen Amarok I Double Cab facelift 2016 3.0 V6 TDI 224	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-224hp-4motion-automatic-27100
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461	Auto-Data Skoda Octavia III 1.0 TSI 115	https://www.auto-data.net/en/skoda-octavia-iii-1.0-tsi-115hp-25537
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Auto-Data Skoda Octavia III facelift 2017 1.0 TSI 116	https://www.auto-data.net/en/skoda-octavia-iii-facelift-2017-1.0-tsi-116hp-27258
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465	Auto-Data Skoda Octavia III Combi 1.0 TSI 115	https://www.auto-data.net/en/skoda-octavia-iii-combi-1.0-tsi-115hp-25637
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Auto-Data Skoda Octavia III Combi facelift 2017 1.0 TSI 116	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-1.0-tsi-116hp-27401
EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-FWD-01	4486	1839	1654	Auto-Data Volkswagen Tiguan II 2.0 TDI 115 SCR	https://www.auto-data.net/en/volkswagen-tiguan-ii-2.0-tdi-115hp-scr-41632
```

## 下一步优先处理

1. 闭合 BMW 7 G11/G12 标准轴距与长轴距派生分支。
2. 解决 C4 Picasso II 单值高度口径及 Tiguan 1.4 TSI 4MOTION 跨改款边界。
3. 集中拆分 Expert、Proace、Trafic、Sprinter、Combo 与 Highway Van 的长度、轴距、车顶及客货车分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-gti-profile-20033?utm_source=chatgpt.com "Vehicle data Golf VII GTI profile"
[2]: https://www.auto-data.net/en/skoda-octavia-iii-1.0-tsi-115hp-25537 "Skoda Octavia III 1.0 TSI (115 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volkswagen-tiguan-ii-1.4-tsi-150hp-4motion-dsg-28424 "Volkswagen Tiguan II 1.4 TSI (150 Hp) 4MOTION DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Citroën C4 Picasso II facelift 1.2 PureTech 110：该动力版本自 2016 年 5 月起对应改款后五门 MPV，车身宽度明确为不含后视镜口径。([汽车目录][1])
* 闭合 Tiguan II 1.4 TSI 4MOTION：该具体动力组合实际对应 2016–2018 年前期型，未按输入结束日期错误扩展到 facelift；其 4MOTION 高度与此前前驱尺寸组不同，单独建组。([汽车数据网][2])
* 闭合 BMW 7 Series G11/G12 分支：`750 D, LD xDrive` 拆分标准轴距和长轴距；`M760i/M760Li` 实际均对应 G12 长轴车身，因此不创建不存在的 G11 M760 分支。BMW 官方资料确认两种车身分别为 `5098 × 1902 × 1467 mm` 和 `5238 × 1902 × 1479 mm`。([press.bmwgroup.com][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：83
* READY 映射行：88
* PENDING 输入 Ktype：17
* 已确认尺寸组：46
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119968	119968	MPV	C4 Picasso II facelift		5	EU-CITROEN-C4-PICASSO-II-MPV-FACELIFT-01	HIGH	改款后五门短轴C4 Picasso外廓。	READY
120209	120209	SUV	Tiguan II pre-facelift		5	EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-4MOTION-01	HIGH	1.4 TSI 4MOTION前期型外廓。	READY
120288	120288	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	M760i与M760Li市场命名均对应G12长轴外廓。	READY
120295_swb	120295	Sedan	7 Series G11 pre-facelift	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	750d xDrive标准轴距外廓。	READY
120295_lwb	120295	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	750Ld xDrive长轴距外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C4-PICASSO-II-MPV-FACELIFT-01	4438	1826	1610	Automobile-Catalog 2016 Citroen C4 Picasso PureTech 110	https://www.automobile-catalog.com/car/2016/2513135/citroen_c4_picasso_puretech_110.html
EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-4MOTION-01	4486	1839	1673	Auto-Data Volkswagen Tiguan II 1.4 TSI 150 4MOTION ACT	https://www.auto-data.net/en/volkswagen-tiguan-ii-1.4-tsi-150hp-4motion-act-24221
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1467	BMW Group PressClub The new BMW 7 Series; Automobile-Catalog BMW 750d xDrive	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0221565EN_GB/the-new-bmw-7-series?language=en_GB; https://www.automobile-catalog.com/car/2016/2407625/bmw_750d_xdrive.html
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1479	BMW Group PressClub The new BMW 7 Series; BMW M760Li xDrive technical data; Automobile-Catalog BMW 750Ld xDrive	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0221565EN_GB/the-new-bmw-7-series?language=en_GB; https://www.press.bmwgroup.com/global/article/attachment/T0267156EN/377936; https://www.automobile-catalog.com/car/2016/2407640/bmw_750ld_xdrive.html
```

## 下一步优先处理

1. 按共平台尺寸组集中拆分 Peugeot Expert 与 Toyota Proace 的 Compact、Standard、Long 车身。
2. 处理 Renault Trafic III 的 L1/L2 及低顶分支。
3. 最后闭合 Sprinter 4.6-T、Opel Combo、Hyundai Highway Van 的客货车、轴距及车顶边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2016/2513135/citroen_c4_picasso_puretech_110.html?utm_source=chatgpt.com "2016 Citroen C4 Picasso PureTech 110 Specs Review (81 kW / 110 PS / 109 hp) (since May 2016 for Europe )"
[2]: https://www.auto-data.net/en/volkswagen-tiguan-ii-1.4-tsi-150hp-4motion-act-24221 "Volkswagen Tiguan II 1.4 TSI (150 Hp) 4MOTION ACT | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.press.bmwgroup.com/united-kingdom/article/detail/T0221565EN_GB/the-new-bmw-7-series?language=en_GB "The new BMW 7 Series"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 集中闭合 Toyota Proace II 共平台分支，新增 5 个输入 Ktype、14 条派生映射和 5 个尺寸组。
* 2016 年欧洲官方资料确认 Compact、Medium、Long 三种车身及各动力可用边界；量产规格表明确区分 `1920 mm` 不含后视镜宽度与 `2204 mm` 展开后视镜宽度，并确认 2.0 D-4D 120 的 Medium 车身高度增至 `1940 mm`。
* Kasten 与 Bus 在长宽高完全一致的 Compact、Medium 分支复用同一尺寸组；Long 货车与乘用 Bus 因高度不同分别建组。Proace Verso 量产规格确认三种长度的乘用车身高度均为 `1910 mm`。([汽车目录档案][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：88
* READY 映射行：102
* PENDING 输入 Ktype：12
* 已确认尺寸组：51
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120259_compact	120259	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120259_medium	120259	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120259_long	120259	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
120260_compact	120260	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120260_medium	120260	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120261_compact	120261	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120261_medium	120261	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120261_long	120261	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
120263_compact	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴乘用车身外廓。	READY
120263_medium	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距乘用车身外廓。	READY
120263_long	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long长车身乘用外廓。	READY
120264_compact	120264	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120264_medium	120264	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	HIGH	Medium车身2.0 D-4D增高外廓。	READY
120264_long	120264	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910	Toyota Proace 2016 UK official brochure; Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf; https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota Proace 2016 UK official brochure; Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf; https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935	Toyota Proace 2016 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910	Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940	Toyota Proace 2016 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf
```

## 下一步优先处理

1. 复用 Proace 共平台研究结果，集中拆分 Peugeot Expert 的 Compact、Standard、Long 货车分支。
2. 闭合 Renault Trafic III 的 L1/L2 与 H1/H2 组合。
3. 最后处理 Sprinter 4.6-T、Opel Combo、Hyundai Highway Van 的多长度、车顶及客货车边界。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf?utm_source=chatgpt.com "ALL NEW
PROACE"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 闭合 Peugeot Expert III 全部 5 个 Ktype，按动力实际覆盖范围拆分 Compact、Standard、Long 车身，共新增 14 条派生映射和 5 个尺寸组。
* 官方规格表将车身宽度 `1920 mm` 与展开后视镜宽度 `2204 mm` 分列，并区分普通载荷与高载荷悬架高度；2018 车型表确认 95、115、120、150、180 hp 各动力对应的长度版本，2019 车型调整进一步确认 150 hp Compact 版本。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：93
* READY 映射行：116
* PENDING 输入 Ktype：7
* 已确认尺寸组：56
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
120075_compact	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	HIGH	Compact普通载荷货车外廓。	READY
120075_standard	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	HIGH	Standard普通载荷货车外廓。	READY
120075_long	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120076_compact	120076	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	HIGH	Compact普通载荷货车外廓。	READY
120076_standard	120076	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	HIGH	Standard普通载荷货车外廓。	READY
120077_compact	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120077_standard	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120077_long	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120078_compact	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120078_standard	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120078_long	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120079_compact	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120079_standard	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120079_long	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
```

## 下一步优先处理

1. 集中闭合 Renault Trafic III 的 L1H1、L1H2、L2H1、L2H2 分支及各动力可用边界。
2. 处理 Hyundai Highway Van 两个 Ktype 的货车与 MPV 混合车身边界。
3. 最后闭合 Mercedes-Benz Sprinter 4.6-T 与 Opel Combo 的轴距、车顶和客货车分支。

推进信号：CONTINUE


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_201-300_ktype_dimension_mapping_final.tsv
- all_201-300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 最后 7 个待处理 Ktype 已全部闭合。Renault Trafic III 按 L1/L2 与 H1/H2 拆分，95 PS 仅映射低顶分支，125/145 PS 同时覆盖低顶与高顶分支。([雷诺新闻][1])
* Mercedes-Benz Sprinter 4.6-T 414 CDI 按标准轴距、长轴距、加长后悬及普通顶/高顶/超高顶，闭合 7 个物理外廓分支。([C&P租车][2])
* Opel Combo D 按 L1H1、L2H1 拆分，货车与乘用车身在三维相同时复用尺寸组；Hyundai Highway Van 按 Trajet FO 前期型商用车身闭合。([Opel Ireland][3])
* 已完成最终机械检查并生成两个任务指定 TSV 文件。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* READY 映射行：139
* PENDING：0
* DIMENSION_GROUP：70
* `id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用闭合。
* 所有尺寸组均有完整正整数三维、来源和 URL，不存在孤立尺寸组。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
119943	119943	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	MEDIUM	五门SUV物理外廓。	READY
119944	119944	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119945	119945	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119946	119946	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119947	119947	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119948	119948	Wagon	V90 II	235	5	EU-VOLVO-V90-II-WAGON-01	HIGH	235旅行车物理外廓。	READY
119949	119949	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119950	119950	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119951	119951	Sedan	S90 II	234	4	EU-VOLVO-S90-II-SEDAN-01	HIGH	234四门轿车外廓。	READY
119958	119958	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
119959	119959	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
119960	119960	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119962	119962	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119964	119964	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119965	119965	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119966	119966	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119967	119967	SUV	Q2 GA pre-facelift	GA	5	EU-AUDI-Q2-GA-SUV-PREFL-01	HIGH	GA前期型五门外廓。	READY
119968	119968	MPV	C4 Picasso II facelift		5	EU-CITROEN-C4-PICASSO-II-MPV-FACELIFT-01	HIGH	改款后五门短轴C4 Picasso外廓。	READY
119981	119981	Coupe	Fortwo III	C453	2	EU-SMART-FORTWO-III-COUPE-01	HIGH	C453双门硬顶外廓。	READY
119983	119983	Hatchback	Forfour II	W453	5	EU-SMART-FORFOUR-II-HATCHBACK-01	HIGH	W453五门掀背外廓。	READY
119985	119985	Convertible	Fortwo III	A453	2	EU-SMART-FORTWO-III-CONVERTIBLE-01	HIGH	A453双门敞篷外廓。	READY
120007	120007	Van	Highway Van (Trajet FO)	FO	5	EU-HYUNDAI-HIGHWAY-VAN-FO-VAN-PREFL-01	HIGH	Trajet FO前期型商用Van外廓。	READY
120008	120008	Van	Highway Van (Trajet FO)	FO	5	EU-HYUNDAI-HIGHWAY-VAN-FO-VAN-PREFL-01	HIGH	Trajet FO前期型商用Van外廓。	READY
120019	120019	Sedan	Sonata VI (YF)	YF	4	EU-HYUNDAI-SONATA-VI-YF-SEDAN-01	MEDIUM	YF四门混合动力轿车外廓。	READY
120075_compact	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	HIGH	Compact普通载荷货车外廓。	READY
120075_standard	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	HIGH	Standard普通载荷货车外廓。	READY
120075_long	120075	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120076_compact	120076	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	HIGH	Compact普通载荷货车外廓。	READY
120076_standard	120076	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	HIGH	Standard普通载荷货车外廓。	READY
120077_compact	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120077_standard	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120077_long	120077	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120078_compact	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120078_standard	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120078_long	120078	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120079_compact	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	HIGH	Compact高载荷货车外廓。	READY
120079_standard	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	HIGH	Standard高载荷货车外廓。	READY
120079_long	120079	Van	Expert III	K0		EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	HIGH	Long高载荷货车外廓。	READY
120080	120080	Hatchback	595 facelift 2016		3	EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	HIGH	输入500对应2016改款595三门掀背外廓。	READY
120081	120081	Hatchback	595 facelift 2016		3	EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	HIGH	输入500对应2016改款595三门掀背外廓。	READY
120121	120121	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120122	120122	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120123	120123	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120124	120124	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120125	120125	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120126	120126	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120127	120127	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C43-01	HIGH	A205 AMG C43外廓。	READY
120128_prefl	120128	Convertible	C-Class A205 pre-facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63-PREFL-01	HIGH	C63改款前外廓。	READY
120128_facelift	120128	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	HIGH	C63改款后外廓。	READY
120129_prefl	120129	Convertible	C-Class A205 pre-facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63S-PREFL-01	HIGH	C63 S改款前外廓。	READY
120129_facelift	120129	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	HIGH	C63 S改款后外廓。	READY
120130	120130	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120131	120131	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120132	120132	Convertible	C-Class A205	A205	2	EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	HIGH	A205普通敞篷外廓。	READY
120133	120133	Coupe	Centenario		2	EU-LAMBORGHINI-CENTENARIO-COUPE-01	HIGH	双门Coupe物理外廓。	READY
120177	120177	Convertible	Aventador LP750-4 SV Roadster		2	EU-LAMBORGHINI-AVENTADOR-LP750-SV-ROADSTER-01	MEDIUM	双门可拆卸车顶Roadster外廓。	READY
120178	120178	MPV	Sharan II facelift	7N	5	EU-VOLKSWAGEN-SHARAN-II-MPV-FACELIFT-01	HIGH	7N改款五门MPV外廓。	READY
120179	120179	MPV	Alhambra II facelift	7N	5	EU-SEAT-ALHAMBRA-II-MPV-FACELIFT-01	HIGH	7N改款五门MPV外廓。	READY
120193	120193	Hatchback	Golf VII GTI Clubsport S		3	EU-VOLKSWAGEN-GOLF-VII-GTI-CLUBSPORT-S-HATCHBACK-01	HIGH	三门Clubsport S物理外廓。	READY
120195	120195	Pickup	Amarok I facelift		4	EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLE-CAB-FACELIFT-01	HIGH	四门Double Cab物理外廓。	READY
120206_prefl	120206	Hatchback	Octavia III pre-facelift	5E	5	EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	HIGH	5E五门掀背改款前外廓。	READY
120206_facelift	120206	Hatchback	Octavia III facelift	5E	5	EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	HIGH	5E五门掀背改款后外廓。	READY
120207_prefl	120207	Wagon	Octavia III Combi pre-facelift	5E	5	EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	HIGH	5E五门旅行车改款前外廓。	READY
120207_facelift	120207	Wagon	Octavia III Combi facelift	5E	5	EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	HIGH	5E五门旅行车改款后外廓。	READY
120208	120208	MPV	Touran II	5T	5	EU-VOLKSWAGEN-TOURAN-II-MPV-01	HIGH	5T五门MPV外廓。	READY
120209	120209	SUV	Tiguan II pre-facelift		5	EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-4MOTION-01	HIGH	1.4 TSI 4MOTION前期型外廓。	READY
120210	120210	SUV	Tiguan II pre-facelift		5	EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-FWD-01	HIGH	前驱五门前期型SUV外廓。	READY
120212_standard_normal	120212	Van	Sprinter II (906)	906.653		EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-NORMALROOF-01	HIGH	标准轴距普通顶外廓。	READY
120212_standard_high	120212	Van	Sprinter II (906)	906.653		EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-HIGHROOF-01	HIGH	标准轴距高顶外廓。	READY
120212_standard_superhigh	120212	Van	Sprinter II (906)	906.653		EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-SUPERHIGHROOF-01	HIGH	标准轴距超高顶外廓。	READY
120212_long_high	120212	Van	Sprinter II (906)	906.655		EU-MERCEDES-BENZ-SPRINTER-906-VAN-LONG-HIGHROOF-01	HIGH	长轴距高顶外廓。	READY
120212_long_superhigh	120212	Van	Sprinter II (906)	906.655		EU-MERCEDES-BENZ-SPRINTER-906-VAN-LONG-SUPERHIGHROOF-01	HIGH	长轴距超高顶外廓。	READY
120212_extralong_high	120212	Van	Sprinter II (906)	906.657		EU-MERCEDES-BENZ-SPRINTER-906-VAN-EXTRALONG-HIGHROOF-01	HIGH	加长后悬高顶外廓。	READY
120212_extralong_superhigh	120212	Van	Sprinter II (906)	906.657		EU-MERCEDES-BENZ-SPRINTER-906-VAN-EXTRALONG-SUPERHIGHROOF-01	HIGH	加长后悬超高顶外廓。	READY
120213	120213	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH	952四门轿车物理外廓。	READY
120218	120218	Hatchback	Jazz I (GD)		5	EU-HONDA-JAZZ-I-GD-HATCHBACK-01	MEDIUM	生产年月与功率对应GD五门外廓。	READY
120222_van_l1h1	120222	Van	Combo D	X12		EU-OPEL-COMBO-D-X12-BODY-L1H1-01	MEDIUM	L1H1短轴低顶货车外廓。	READY
120222_mpv_l1h1	120222	MPV	Combo D	X12		EU-OPEL-COMBO-D-X12-BODY-L1H1-01	MEDIUM	L1H1短轴低顶乘用车身外廓。	READY
120222_van_l2h1	120222	Van	Combo D	X12		EU-OPEL-COMBO-D-X12-BODY-L2H1-01	MEDIUM	L2H1长轴低顶货车外廓。	READY
120222_mpv_l2h1	120222	MPV	Combo D	X12		EU-OPEL-COMBO-D-X12-BODY-L2H1-01	MEDIUM	L2H1长轴低顶乘用车身外廓。	READY
120226	120226	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-01	HIGH	F21三门普通外廓。	READY
120228	120228	Hatchback	MiTo 955	955	3	EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	MEDIUM	955三门BiFuel外廓。	READY
120229	120229	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-01	HIGH	F21三门普通外廓。	READY
120235	120235	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-M140-01	HIGH	F21三门M140i外廓。	READY
120236	120236	Hatchback	1 Series F21 LCI	F21	3	EU-BMW-1-F21-HATCHBACK-3D-M140-01	HIGH	F21三门M140i外廓。	READY
120237_l1h1	120237	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1短轴低顶货车外廓。	READY
120237_l2h1	120237	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1长轴低顶货车外廓。	READY
120239_l1h1	120239	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1短轴低顶货车外廓。	READY
120239_l2h1	120239	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1长轴低顶货车外廓。	READY
120239_l1h2	120239	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2短轴高顶货车外廓。	READY
120239_l2h2	120239	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2长轴高顶货车外廓。	READY
120240	120240	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-01	HIGH	F20五门普通外廓。	READY
120241_l1h1	120241	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1短轴低顶货车外廓。	READY
120241_l2h1	120241	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1长轴低顶货车外廓。	READY
120241_l1h2	120241	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2短轴高顶货车外廓。	READY
120241_l2h2	120241	Van	Trafic III	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2长轴高顶货车外廓。	READY
120242	120242	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-01	HIGH	F20五门普通外廓。	READY
120244	120244	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-M140-01	HIGH	F20五门M140i外廓。	READY
120245	120245	Hatchback	1 Series F20 LCI	F20	5	EU-BMW-1-F20-HATCHBACK-5D-M140-01	HIGH	F20五门M140i外廓。	READY
120246	120246	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-01	HIGH	F22双门普通外廓。	READY
120247	120247	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-01	HIGH	F22双门普通外廓。	READY
120248	120248	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-M240-01	HIGH	F22双门M240i外廓。	READY
120249	120249	Coupe	2 Series F22	F22	2	EU-BMW-2-F22-COUPE-M240-01	HIGH	F22双门M240i外廓。	READY
120250	120250	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-01	HIGH	F23双门普通敞篷外廓。	READY
120251	120251	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-01	HIGH	F23双门普通敞篷外廓。	READY
120252	120252	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-M240-01	HIGH	F23双门M240i敞篷外廓。	READY
120253	120253	Convertible	2 Series F23	F23	2	EU-BMW-2-F23-CONVERTIBLE-M240-01	HIGH	F23双门M240i敞篷外廓。	READY
120259_compact	120259	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120259_medium	120259	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120259_long	120259	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
120260_compact	120260	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120260_medium	120260	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120261_compact	120261	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120261_medium	120261	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距货车外廓。	READY
120261_long	120261	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
120263_compact	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴乘用车身外廓。	READY
120263_medium	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium标准轴距乘用车身外廓。	READY
120263_long	120263	MPV	Proace II			EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long长车身乘用外廓。	READY
120264_compact	120264	Van	Proace II			EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact短轴货车外廓。	READY
120264_medium	120264	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	HIGH	Medium车身2.0 D-4D增高外廓。	READY
120264_long	120264	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-01	HIGH	Long长车身货车外廓。	READY
120265	120265	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120266	120266	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120267	120267	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120268	120268	Hatchback	3 Series Gran Turismo F34 LCI	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34改款五门Gran Turismo外廓。	READY
120270	120270	Hatchback	Megane IV GT	BFB	5	EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	HIGH	BFB五门GT掀背外廓。	READY
120272	120272	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120273	120273	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120274	120274	Wagon	Megane IV Grandtour GT	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	HIGH	KFB五门GT旅行车外廓。	READY
120275	120275	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120276	120276	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120277	120277	Wagon	Megane IV Grandtour pre-facelift	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH	KFB普通旅行车外廓。	READY
120279	120279	Wagon	Megane IV Grandtour GT	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	HIGH	KFB五门GT旅行车外廓。	READY
120283	120283	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
120285	120285	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
120286	120286	SUV	GLC X253 pre-facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	X253前期型SUV外廓。	READY
120288	120288	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	M760i与M760Li市场命名均对应G12长轴外廓。	READY
120295_swb	120295	Sedan	7 Series G11 pre-facelift	G11	4	EU-BMW-7-G11-SEDAN-PREFL-01	HIGH	750d xDrive标准轴距外廓。	READY
120295_lwb	120295	Sedan	7 Series G12 pre-facelift	G12	4	EU-BMW-7-G12-SEDAN-PREFL-01	HIGH	750Ld xDrive长轴距外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_201-300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Auto-Data Ford EcoSport II 1.5 TDCi	https://www.auto-data.net/en/ford-ecosport-ii-1.5-tdci-95hp-31851
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Support V90 2017 Dimensions	https://www.volvocars.com/en-jo/support/car/v90/16w46/article/871e942e897ca77dc0a801511788660a/
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Support S90 Dimensions	https://www.volvocars.com/za/support/car/s90/16w46/article/871e942e897ca77dc0a801511788660a/
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436	Auto-Data Alfa Romeo Giulia (952) 2.2 JTD 180	https://www.auto-data.net/en/alfa-romeo-giulia-952-2.2-jtd-180hp-23735
EU-AUDI-Q2-GA-SUV-PREFL-01	4191	1794	1508	Auto-Data Audi Q2 2016-2020	https://www.auto-data.net/en/audi-q2-model-2098
EU-CITROEN-C4-PICASSO-II-MPV-FACELIFT-01	4438	1826	1610	Automobile-Catalog 2016 Citroen C4 Picasso PureTech 110	https://www.automobile-catalog.com/car/2016/2513135/citroen_c4_picasso_puretech_110.html
EU-SMART-FORTWO-III-COUPE-01	2740	1663	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Fortwo Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2017/3155900/smart_fortwo_brabus_twinmatic.html
EU-SMART-FORFOUR-II-HATCHBACK-01	3525	1665	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Forfour Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2017/3155930/smart_forfour_brabus_twinmatic.html
EU-SMART-FORTWO-III-CONVERTIBLE-01	2740	1663	1543	smart BRABUS UK brochure; Automobile-Catalog Smart Fortwo Cabrio Brabus	https://xr793.com/wp-content/uploads/2022/12/2016-Smart-Brabus-UK.pdf; https://www.automobile-catalog.com/car/2016/3155915/smart_fortwo_cabrio_brabus_twinmatic.html
EU-HYUNDAI-HIGHWAY-VAN-FO-VAN-PREFL-01	4695	1840	1710	Automobile-Catalog 2001 Hyundai Trajet 2.0 CRDi GLS	https://www.automobile-catalog.com/car/2001/1169555/hyundai_trajet_2_0_crdi_gls.html
EU-HYUNDAI-SONATA-VI-YF-SEDAN-01	4820	1835	1470	Auto-Data Hyundai Sonata VI YF Hybrid	https://www.auto-data.net/en/hyundai-sonata-vi-yf-2.4-209hp-hybrid-automatic-29665
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940	Peugeot Expert UK price and specification brochure October 2018	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2015/04/expert-van-prices-specifications-brochure-october-2018.pdf
EU-ABARTH-595-FACELIFT-2016-HATCHBACK-01	3660	1627	1485	Auto-Data Abarth 595 facelift 2016 1.4 T-Jet 145	https://www.auto-data.net/en/abarth-595-facelift-2016-1.4-t-jet-145hp-automatic-24658
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-01	4686	1810	1409	Mercedes-Benz C-Class Coupe and Cabriolet official brochure	https://mercedes-benz-media.co.uk/assets/documents/original/894-cclasscoupecabrioletbrochure.pdf
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C43-01	4696	1810	1408	Mercedes-Benz USA 2017 AMG C43 Cabriolet specifications; Automobile-Catalog 2017 Mercedes-AMG C43 Cabriolet	https://media.mbusa.com/releases/release-078ed5dd551c4443b3a94488d26022a0-2017-mercedes-amg-c43-cabriolet-specifications; https://www.automobile-catalog.com/car/2017/2407325/mercedes-amg_c_43_4matic_cabriolet.html
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63-PREFL-01	4750	1877	1402	Mercedes-Benz USA 2017 AMG C63 and C63 S Cabriolet specifications	https://media.mbusa.com/releases/release-e1808cbe57354b168ecfb4636128aa8f-2017-mercedes-amg-c63-cabrio-and-c63-s-cabrio-specifications
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-AMG-V8-FACELIFT-01	4751	1877	1404	Mercedes-Benz USA MY19 C-Class brochure; Automobile-Catalog 2019 Mercedes-AMG C63 Cabriolet; Automobile-Catalog 2019 Mercedes-AMG C63 S Cabriolet	https://www.mbusa.com/content/dam/mb-nafta/us/brochures/pdf/MY19_C-Class_WebPDF_181212.pdf; https://www.automobile-catalog.com/car/2019/2739365/mercedes-amg_c_63_cabriolet.html; https://www.automobile-catalog.com/car/2019/2739380/mercedes-amg_c_63_s_cabriolet.html
EU-MERCEDES-BENZ-C-CLASS-A205-CONVERTIBLE-C63S-PREFL-01	4750	1877	1405	Mercedes-Benz USA 2017 AMG C63 and C63 S Cabriolet specifications	https://media.mbusa.com/releases/release-e1808cbe57354b168ecfb4636128aa8f-2017-mercedes-amg-c63-cabrio-and-c63-s-cabrio-specifications
EU-LAMBORGHINI-CENTENARIO-COUPE-01	4924	2062	1143	Auto-Data Lamborghini Centenario LP 770-4	https://www.auto-data.net/en/lamborghini-centenario-lp-770-4-6.5-v12-770hp-4wd-isr-28863
EU-LAMBORGHINI-AVENTADOR-LP750-SV-ROADSTER-01	4835	2030	1136	Auto-Data Lamborghini Aventador LP 750-4 Superveloce Roadster	https://www.auto-data.net/en/lamborghini-aventador-lp-750-4-superveloce-roadster-6.5-v12-750hp-4wd-22765
EU-VOLKSWAGEN-SHARAN-II-MPV-FACELIFT-01	4854	1904	1720	Auto-Data Volkswagen Sharan II facelift 2.0 TDI	https://www.auto-data.net/en/volkswagen-sharan-ii-facelift-2015-2.0-tdi-184hp-22719
EU-SEAT-ALHAMBRA-II-MPV-FACELIFT-01	4854	1904	1720	Auto-Data Seat Alhambra II 7N facelift 2.0 TDI	https://www.auto-data.net/en/seat-alhambra-ii-7n-facelift-2015-2.0-tdi-184hp-dsg-31108
EU-VOLKSWAGEN-GOLF-VII-GTI-CLUBSPORT-S-HATCHBACK-01	4268	1799	1442	Volkswagen Newsroom Golf VII GTI vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-7-gti-profile-20033
EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLE-CAB-FACELIFT-01	5254	1954	1834	Auto-Data Volkswagen Amarok I Double Cab facelift 2016 3.0 V6 TDI 224	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-facelift-2016-3.0-v6-tdi-224hp-4motion-automatic-27100
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461	Auto-Data Skoda Octavia III 1.0 TSI 115	https://www.auto-data.net/en/skoda-octavia-iii-1.0-tsi-115hp-25537
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461	Auto-Data Skoda Octavia III facelift 2017 1.0 TSI 116	https://www.auto-data.net/en/skoda-octavia-iii-facelift-2017-1.0-tsi-116hp-27258
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465	Auto-Data Skoda Octavia III Combi 1.0 TSI 115	https://www.auto-data.net/en/skoda-octavia-iii-combi-1.0-tsi-115hp-25637
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465	Auto-Data Skoda Octavia III Combi facelift 2017 1.0 TSI 116	https://www.auto-data.net/en/skoda-octavia-iii-combi-facelift-2017-1.0-tsi-116hp-27401
EU-VOLKSWAGEN-TOURAN-II-MPV-01	4527	1829	1674	Auto-Data Volkswagen Touran II 1.6 TDI	https://www.auto-data.net/en/volkswagen-touran-ii-1.6-tdi-115hp-32222
EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-4MOTION-01	4486	1839	1673	Auto-Data Volkswagen Tiguan II 1.4 TSI 150 4MOTION ACT	https://www.auto-data.net/en/volkswagen-tiguan-ii-1.4-tsi-150hp-4motion-act-24221
EU-VOLKSWAGEN-TIGUAN-II-SUV-PREFL-FWD-01	4486	1839	1654	Auto-Data Volkswagen Tiguan II 2.0 TDI 115 SCR	https://www.auto-data.net/en/volkswagen-tiguan-ii-2.0-tdi-115hp-scr-41632
EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-NORMALROOF-01	5926	1993	2426	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-HIGHROOF-01	5926	1993	2757	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-STANDARD-SUPERHIGHROOF-01	5926	1993	2980	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-LONG-HIGHROOF-01	6961	1993	2750	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-LONG-SUPERHIGHROOF-01	6961	1993	2968	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-EXTRALONG-HIGHROOF-01	7361	1993	2743	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-MERCEDES-BENZ-SPRINTER-906-VAN-EXTRALONG-SUPERHIGHROOF-01	7361	1993	2960	Mercedes-Benz Sprinter Panel Van 2016 official brochure	https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf
EU-HONDA-JAZZ-I-GD-HATCHBACK-01	3830	1675	1525	Auto-Data Honda Jazz I 1.4	https://www.auto-data.net/en/honda-jazz-i-1.4-83hp-12141
EU-OPEL-COMBO-D-X12-BODY-L1H1-01	4390	1832	1845	Opel Combo MY2016 official owner's manual	https://www.opel.ie/content/dam/opel/ireland/owners/manuals/pdf/combo/om_combo_kta-2730_4-en_eu_my16_ed0515_12_en_gb.pdf
EU-OPEL-COMBO-D-X12-BODY-L2H1-01	4740	1832	1880	Opel Combo MY2016 official owner's manual	https://www.opel.ie/content/dam/opel/ireland/owners/manuals/pdf/combo/om_combo_kta-2730_4-en_eu_my16_ed0515_12_en_gb.pdf
EU-BMW-1-F21-HATCHBACK-3D-01	4329	1765	1421	BMW Group PressClub BMW 1 Series 3 Door Hatch specifications	https://www.press.bmwgroup.com/global/article/attachment/T0260190EN/359669
EU-ALFA-ROMEO-MITO-955-HATCHBACK-01	4063	1720	1446	Auto-Data Alfa Romeo MiTo facelift 2013 1.4 TP LPG	https://www.auto-data.net/en/alfa-romeo-mito-facelift-2013-1.4-tp-120hp-lpg-24708
EU-BMW-1-F21-HATCHBACK-3D-M140-01	4324	1765	1411	BMW Group PressClub BMW 1 Series 3 Door Hatch specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0286639CS/417968
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault Trafic official press kit January 2018	https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault Trafic official press kit January 2018	https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465	Renault Trafic official press kit January 2018	https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465	Renault Trafic official press kit January 2018	https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
EU-BMW-1-F20-HATCHBACK-5D-01	4329	1765	1421	BMW Group PressClub BMW 1 Series 5-door technical data	https://www.press.bmwgroup.com/portugal/article/attachment/T0127857PT/416739
EU-BMW-1-F20-HATCHBACK-5D-M140-01	4324	1765	1411	BMW Group PressClub BMW 1 Series 5-door technical data	https://www.press.bmwgroup.com/portugal/article/attachment/T0127857PT/416739
EU-BMW-2-F22-COUPE-01	4432	1774	1418	BMW Group PressClub BMW 2 Series Coupe specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0162084EN/242844
EU-BMW-2-F22-COUPE-M240-01	4454	1774	1408	BMW Group PressClub BMW M240i Coupe specifications	https://www.press.bmwgroup.com/global/article/attachment/T0259974EN/385584
EU-BMW-2-F23-CONVERTIBLE-01	4432	1774	1413	BMW Group PressClub BMW 2 Series Convertible technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0274992EN_GB/395388
EU-BMW-2-F23-CONVERTIBLE-M240-01	4454	1774	1403	BMW Group PressClub BMW M240i Convertible specifications	https://www.press.bmwgroup.com/global/article/attachment/T0260193EN/359688
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910	Toyota Proace 2016 UK official brochure; Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf; https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota Proace 2016 UK official brochure; Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf; https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935	Toyota Proace 2016 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910	Toyota Proace Verso 2017 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-Verso-2017-UK.pdf
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940	Toyota Proace 2016 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/05/Toyota-Proace-2016-UK-.pdf
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508	Auto-Data BMW 3 Series Gran Turismo F34 LCI 340i	https://www.auto-data.net/en/bmw-3-series-gran-turismo-f34-lci-facelift-2016-340i-326hp-steptronic-24294
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438	Auto-Data Renault Megane IV GT 1.6 Energy dCi	https://www.auto-data.net/en/renault-megane-iv-gt-1.6-energy-dci-163hp-edc-22556
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449	Renault Megane Sport Tourer official press kit; Automobile-Catalog 2016 Renault Megane Grandtour dCi 90	https://www.press.renault.co.uk/assets/documents/original/17939-RE37517MeganeSTPressKitV1.pdf; https://www.automobile-catalog.com/car/2016/2984735/renault_megane_estate_grandtour_energy_dci_90.html
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457	Auto-Data Renault Megane IV Grandtour GT TCe; Auto-Data Renault Megane IV Grandtour GT dCi	https://www.auto-data.net/en/renault-megane-iv-grandtour-gt-1.6-energy-tce-205hp-edc-24656; https://www.auto-data.net/en/renault-megane-iv-grandtour-gt-1.6-energy-dci-165hp-edc-30062
EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	4656	1890	1639	Mercedes-Benz GLC official brochure; Automobile-Catalog 2016 Mercedes-Benz GLC 250 4MATIC	https://autocatalogarchive.com/wp-content/uploads/2017/08/Mercedes-GLC-2016-INT.pdf; https://www.automobile-catalog.com/car/2016/2170805/mercedes-benz_glc_250_4matic.html
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1479	BMW Group PressClub The new BMW 7 Series; BMW M760Li xDrive technical data; Automobile-Catalog BMW 750Ld xDrive	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0221565EN_GB/the-new-bmw-7-series?language=en_GB; https://www.press.bmwgroup.com/global/article/attachment/T0267156EN/377936; https://www.automobile-catalog.com/car/2016/2407640/bmw_750ld_xdrive.html
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1467	BMW Group PressClub The new BMW 7 Series; Automobile-Catalog BMW 750d xDrive	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0221565EN_GB/the-new-bmw-7-series?language=en_GB; https://www.automobile-catalog.com/car/2016/2407625/bmw_750d_xdrive.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_201-300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf "https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf"
[2]: https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf "https://www.cnp.sg/wp-content/uploads/2024/03/Sprinter_KaWa_Katalog_UP_2016_02_ENG_eMB-ilovepdf-compressed.pdf"
[3]: https://www.opel.ie/content/dam/opel/ireland/owners/manuals/pdf/combo/om_combo_kta-2730_4-en_eu_my16_ed0515_12_en_gb.pdf "https://www.opel.ie/content/dam/opel/ireland/owners/manuals/pdf/combo/om_combo_kta-2730_4-en_eu_my16_ed0515_12_en_gb.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_201-300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_201-300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（139 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（70 行）

