# 任务：all 第 1501-1600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0016__16580b4d


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1501-1600 行

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
all 第 1501-1600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	4728	1912	1294
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-AUDI-R8-II-4S-SPYDER-01	4426	1940	1244
EU-BMW-2-F22-COUPE-01	4432	1774	1418
EU-BMW-2-F22-COUPE-M240-01	4454	1774	1408
EU-BMW-2-F23-CONVERTIBLE-01	4432	1774	1413
EU-BMW-2-F23-CONVERTIBLE-M240-01	4454	1774	1403
EU-BMW-4-F32-COUPE-01	4638	1825	1377
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498
EU-BMW-502-SEDAN-01	4730	1780	1530
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275
EU-BMW-6-E24-COUPE-FACELIFT-01	4815	1725	1365
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538
EU-BMW-X3-F25-FACELIFT-SUV-01	4657	1881	1661
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-SR-01	4570	1800	1440
EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	4731	1936	1652
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1416
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457
EU-JAGUAR-XF-II-X260-SPORTBRAKE-WAGON-01	4955	1880	1496
EU-LADA-NOVA-2105-SEDAN-01	4130	1620	1446
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-SUV-5D-01	4370	1900	1635
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	4803	2032	1665
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	4544	1939	1287
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	4551	2007	1284
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	4544	1939	1259
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	4551	2007	1260
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-01	3850	1727	1415
EU-MINI-MINI-R55-CLUBMAN-WAGON-01	3961	1683	1426
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R61-PACEMAN-COUPE-01	4114	1786	1518
EU-OPEL-COMBO-D-X12-BODY-L1H1-01	4390	1832	1845
EU-OPEL-COMBO-D-X12-BODY-L2H1-01	4740	1832	1880
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601
EU-VOLVO-V60-I-FACELIFT-POLESTAR-WAGON-01	4668	1866	1484
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	6	630 D Xdrive	Schrägheck	Allrad	Diesel	195	265	Jun 2017	Jun 2020	2024-03-01	127830
BMW	X3	Xdrive M40 I	SUV	Allrad	Benzin	265	360	Aug 2017	-	2024-03-01	127852
BMW	X3	Xdrive 20 D	SUV	Allrad	Diesel	140	190	Aug 2017	Mar 2020	2024-03-01	127854
BMW	X3	Xdrive 30 D	SUV	Allrad	Diesel	195	265	Aug 2017	Jun 2020	2024-03-01	127855
BMW	X3	Xdrive 30 I	SUV	Allrad	Benzin	185	252	Aug 2017	-	2024-03-01	127856
BMW	X3	Xdrive 20 I	SUV	Allrad	Benzin	135	184	Dec 2017	-	2024-03-01	127857
BMW	X1	Sdrive 18 I	SUV	Frontantrieb	Benzin	103	140	Jul 2017	Jun 2022	2024-03-01	127858
BMW	4	M4 CS	Coupe	Heckantrieb	Benzin	338	460	Jul 2017	Jun 2019	2024-03-01	127860
Mini	Mini	ONE	Kombi	Frontantrieb	Benzin	75	102	Jul 2017	-	2024-03-01	127861
Mini	Mini	ONE D	Kombi	Frontantrieb	Diesel	85	116	Jul 2017	-	2024-03-01	127864
Toyota	Hilux iv	2.4 D	Pick-up	Heckantrieb	Diesel	55	75	Sep 1984	Jul 1988	2024-03-01	127891
BMW	4	420 I	Cabriolet	Heckantrieb	Benzin	120	163	Mar 2016	Jul 2020	2024-03-01	127901
Ssangyong	Kyron	2.3 4X4	SUV	Allrad	Benzin	110	150	Nov 2006	Dec 2014	2024-03-01	127902
Seat	Ateca	2.0 TSI 4drive	SUV	Allrad	Benzin	140	190	May 2017	-	2024-03-01	127905
BMW	4	420 I	Coupe	Heckantrieb	Benzin	120	163	Mar 2016	Jun 2020	2024-03-01	127908
BMW	4	420 I	Coupe	Heckantrieb	Benzin	120	163	Mar 2016	May 2021	2024-03-01	127909
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	120	163	Mar 2016	May 2021	2024-03-01	127911
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	120	163	Mar 2016	Jun 2020	2024-03-01	127912
Audi	A3	1.5 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	May 2017	Dec 2017	2024-03-01	127924
Audi	A3	1.5 Tfsi	Schrägheck	Frontantrieb	Benzin	110	150	May 2017	Oct 2018	2024-03-01	127927
Audi	A3	1.5 Tfsi	Stufenheck	Frontantrieb	Benzin	110	150	May 2017	Oct 2018	2024-03-01	127928
Audi	A3	1.5 Tfsi	Cabriolet	Frontantrieb	Benzin	110	150	May 2017	Oct 2018	2024-03-01	127929
Skoda	Fabia iii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Aug 2014	Jun 2021	2024-03-01	127941
Skoda	Fabia iii	1.0 TSI	Kombi	Frontantrieb	Benzin	70	95	Aug 2014	Dec 2022	2024-03-01	127942
Renault	Koleos ii	2.0 DCI 175	SUV	Frontantrieb	Diesel	130	177	Apr 2016	-	2024-03-01	127965
Lada	1200-1600	1.3 2106	Stufenheck	Heckantrieb	Benzin	49	67	Apr 1976	Dec 2005	2024-03-01	127969
Lada	Nova	1.6	Stufenheck	Heckantrieb	Benzin	57	77	Oct 1986	May 1994	2024-03-01	127970
Lada	Kalina	1.6 Sport	Schrägheck	Frontantrieb	Benzin	87	118	Jun 2013	Dec 2013	2024-03-01	127972
Jaguar	E-Pace	2.0 P200 AWD	SUV	Allrad	Benzin	183	249	Sep 2017	-	2024-03-01	127973
Jaguar	E-Pace	2.0 AWD	SUV	Allrad	Benzin	221	300	Sep 2017	-	2024-03-01	127974
Jaguar	E-Pace	2.0 D150	SUV	Frontantrieb	Diesel	110	150	Sep 2017	-	2024-03-01	127975
Jaguar	E-Pace	2.0 D150 AWD	SUV	Allrad	Diesel	110	150	Sep 2017	-	2024-03-01	127976
Jaguar	E-Pace	2.0 D180 AWD	SUV	Allrad	Diesel	132	179	Sep 2017	-	2024-03-01	127977
Jaguar	E-Pace	2.0 D240 AWD	SUV	Allrad	Diesel	177	241	Sep 2017	-	2024-03-01	127978
BMW	5	M 550 D Xdrive	Kombi	Allrad	Diesel	294	400	Jul 2017	-	2024-03-01	127983
BMW	5	540 D Xdrive	Kombi	Allrad	Diesel	235	320	Jul 2017	Jun 2020	2024-03-01	127984
BMW	5	525 D	Kombi	Heckantrieb	Diesel	170	231	Jul 2017	Jun 2019	2024-03-01	127985
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	140	190	Jul 2017	-	2024-03-01	127986
BMW	5	530 I Xdrive	Kombi	Allrad	Benzin	185	252	Jul 2017	Jun 2020	2024-03-01	127987
Jaguar	F-Pace	2.0 TI4 AWD	SUV	Allrad	Benzin	221	300	Jun 2017	-	2024-03-01	127990
Jaguar	Xe	2.0 AWD	Stufenheck	Allrad	Benzin	221	300	Jun 2017	-	2024-03-01	127991
Jaguar	Xe	5.0 SVO Project 8	Stufenheck	Allrad	Benzin	441	600	Mar 2018	-	2024-03-01	127992
Jaguar	Xf ii	2.0 AWD	Stufenheck	Allrad	Benzin	221	300	Sep 2017	-	2024-03-01	127993
Land Rover	Range rover velar	2.0 P300 SI4 4X4	SUV	Allrad	Benzin	221	300	Mar 2017	-	2024-03-01	127995
Hyundai	Elantra vi	2	Stufenheck	Frontantrieb	Benzin	112	152	Oct 2015	Dec 2020	2024-05-01	128002
Lada	1200-1500	1.3 1300	Kombi	Heckantrieb	Benzin	51	69	Oct 1974	Oct 1979	2024-03-01	128009
Mercedes-benz	S-Klasse	S 650 Maybach	Stufenheck	Heckantrieb	Benzin	463	630	Jul 2017	Jul 2020	2024-03-01	128014
Mercedes-benz	S-Klasse	S 560 Maybach	Stufenheck	Heckantrieb	Benzin	345	469	Jul 2017	Jul 2020	2024-03-01	128015
Mercedes-benz	S-Klasse	S 400 D	Stufenheck	Heckantrieb	Diesel	250	340	Jul 2017	Jul 2020	2024-03-01	128016
Mercedes-benz	S-Klasse	S 350 D	Stufenheck	Heckantrieb	Diesel	210	286	Jul 2017	Jul 2020	2024-03-01	128017
BMW	5	520 I	Kombi	Heckantrieb	Benzin	135	184	Jul 2017	Jun 2020	2024-03-01	128020
Subaru	Xv	2.0 I AWD	SUV	Allrad	Benzin	115	156	Apr 2017	-	2024-03-01	128023
Mercedes-benz	E-Klasse	E 350 D 4-matic	Stufenheck	Allrad	Diesel	190	258	Jun 2017	May 2018	2024-03-01	128024
Mitsubishi	Pajero iv	3.2 4WD	SUV	Allrad	Diesel	141	192	Oct 2016	-	2024-03-01	128025
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	170	231	Jul 2017	Jun 2019	2024-03-01	128026
BMW	5	540 D Xdrive	Stufenheck	Allrad	Diesel	235	320	Jul 2017	Jun 2020	2024-03-01	128029
Hyundai	Kona	1.6 T-gdi	SUV	Frontantrieb	Benzin	130	177	Jul 2017	Dec 2020	2024-05-01	128030
Mercedes-benz	Amg gt	GT C	Coupe	Heckantrieb	Benzin	410	557	Mar 2017	Dec 2021	2024-03-01	128046
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Jan 2017	Feb 2020	2024-03-01	128047
Audi	A5	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	110	150	May 2017	Feb 2020	2024-03-01	128048
Audi	A5	2.0 TDI	Coupe	Frontantrieb	Diesel	110	150	May 2017	Feb 2020	2024-03-01	128049
Opel	Combo tour	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	59	80	Mar 2015	-	2024-03-01	128056
Opel	Combo	1.3 Cdti	Kasten/Großraumlimousine	Frontantrieb	Diesel	59	80	Feb 2012	-	2024-03-01	128057
Volvo	V60 i	T5	Kombi	Frontantrieb	Benzin	162	220	Jan 2014	Dec 2017	2024-03-01	128084
Volvo	V60 i	2.0 T	Kombi	Frontantrieb	Benzin	132	180	Jan 2014	Jul 2018	2024-03-01	128085
Mercedes-benz	S-Klasse	S 560	Stufenheck	Heckantrieb	Benzin	345	469	Jul 2017	Jul 2020	2024-03-01	128089
BMW	5	M 550 D Xdrive	Stufenheck	Allrad	Diesel	294	400	Jun 2017	Jun 2020	2024-03-01	128090
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	135	184	Jul 2017	-	2024-03-01	128091
Hyundai	Solaris	1.6	Stufenheck	Frontantrieb	Benzin	90	122	Jan 2017	-	2024-03-01	128106
BMW	2	218 I	Großraumlimousine	Frontantrieb	Benzin	103	140	Apr 2017	-	2024-03-01	128113
Volvo	Xc60 ii	T5	SUV	Frontantrieb	Benzin	187	254	Mar 2017	-	2024-03-01	128114
Lotus	3	3.5 Road	Cabriolet	Heckantrieb	Benzin	306	416	Feb 2016	-	2024-03-01	128117
Aston Martin	Vanquish	S 6.0	Coupe	Heckantrieb	Benzin	444	604	Nov 2016	-	2025-11-01	128126
Aston Martin	Vanquish	S 6.0	Cabriolet	Heckantrieb	Benzin	444	604	Nov 2016	-	2025-11-01	128127
Toyota	Prius	1.8 Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	90	122	Jan 2016	Dec 2022	2024-05-01	128130
Donkervoort	D8	Gto-s Performance Pack	Cabriolet	Heckantrieb	Benzin	265	360	Jan 2017	-	2024-03-01	128132
Citroën	C3 aircross i	1.6 Bluehdi 100	SUV	Frontantrieb	Diesel	73	99	Jul 2017	Aug 2018	2025-11-01	128133
Citroën	C3 aircross i	1.6 Bluehdi 120	SUV	Frontantrieb	Diesel	88	120	Jul 2017	May 2018	2025-11-01	128134
Citroën	C3 aircross i	1.2 Puretech 82	SUV	Frontantrieb	Benzin	60	82	Jun 2017	-	2025-11-01	128135
Citroën	C3 aircross i	1.2 Puretech 110	SUV	Frontantrieb	Benzin	81	110	Jun 2017	-	2025-11-01	128136
Skoda	Fabia iii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Aug 2014	Jun 2021	2024-03-01	128141
Skoda	Fabia iii	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Aug 2014	Dec 2022	2024-03-01	128142
Rolls-royce	Dawn	V12	Cabriolet	Heckantrieb	Benzin	442	601	Jul 2017	-	2024-03-01	128144
Land Rover	Range rover evoque	2.0 D 4X4	Cabriolet	Allrad	Diesel	177	241	Aug 2017	Dec 2019	2024-03-01	128145
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	125	170	Jul 2017	Jun 2023	2024-03-01	128146
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	449	610	May 2017	-	2024-03-01	128150
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	120	163	Jul 2017	Jun 2020	2024-03-01	128151
BMW	5	520 I	Kombi	Heckantrieb	Benzin	120	163	Jul 2017	Jun 2020	2024-03-01	128152
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	155	211	Jul 2017	Jun 2019	2024-03-01	128153
BMW	5	525 D	Kombi	Heckantrieb	Diesel	155	211	Jul 2017	Jun 2019	2024-03-01	128154
BMW	X3	Xdrive 20 D	SUV	Allrad	Diesel	120	163	Aug 2017	Mar 2020	2024-03-01	128155
Seat	Toledo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	May 2017	Apr 2019	2024-03-01	128156
Seat	Toledo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	May 2017	Apr 2019	2024-03-01	128157
Ferrari	812 superfast	6.5	Coupe	Heckantrieb	Benzin	588	800	Mar 2017	-	2024-03-01	128158
VW	Arteon	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	140	190	May 2017	-	2025-12-01	128179
VW	Arteon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	140	190	May 2017	-	2025-12-01	128180
VW	Arteon	2.0 TSI	Schrägheck	Frontantrieb	Benzin	140	190	May 2017	Jun 2021	2025-12-01	128181
BMW	5	M5	Stufenheck	Allrad	Benzin	441	600	Sep 2017	Jun 2023	2024-03-01	128183
Citroën	C3 aircross i	1.2 Puretech 130	SUV	Frontantrieb	Benzin	96	131	Jul 2017	-	2025-11-01	128184
Citroën	C3 aircross i	1.6 Bluehdi 115	SUV	Frontantrieb	Diesel	85	115	Jun 2017	May 2018	2025-11-01	128185


--- Round 1 / 首次发送 ---
更新点

* 完成 BMW X3 G01 标准外廓与 M40i 专属外廓拆分；官方资料分别确认标准版 `4708×1891×1676`、M40i `4716×1897×1676`，宽度字段与含镜宽度分列。([BMW Group PressClub][1])
* Ktype `127858` 覆盖 BMW X1 F48 改款前后两个不同长度外廓，已派生为 `prefl` 和 `facelift`；官方资料确认长度由 4439 mm 变为 4447 mm。
* 新建 BMW M4 CS、F33 Convertible、G30/G31 M550d 专属尺寸组；M4 CS 和 F33 三维由 BMW 官方资料闭合，M550d Sedan 由 ADAC 闭合。([BMW Group PressClub][2])
* 历史桥接样本中的 M550d Touring 记录用于闭合对应 ADAC 直链和尺寸组。
* 其余已确认车型直接引用跨批次已有尺寸组，本轮不重复输出这些既有组。

当前批次进度

* 已覆盖输入 Ktype：46 / 100
* READY 映射行：47
* PENDING / 尚待处理输入 Ktype：54
* 本轮新建尺寸组：8
* 本轮引用既有尺寸组：20
* 当前映射累计引用尺寸组：28
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127830	127830	Hatchback	6 Series G32	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127852	127852	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-M40I-01	HIGH	M40i专属外廓。	READY
127854	127854	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127855	127855	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127856	127856	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127857	127857	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127858_prefl	127858	SUV	X1 F48	F48	5	EU-BMW-X1-F48-SUV-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
127858_facelift	127858	SUV	X1 F48	F48	5	EU-BMW-X1-F48-SUV-FACELIFT-01	HIGH	Ktype覆盖2019年改款后外廓。	READY
127860	127860	Coupe	M4 F82	F82	2	EU-BMW-4-F82-COUPE-M4-CS-01	HIGH	M4 CS专属外廓。	READY
127861	127861	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH		READY
127864	127864	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH		READY
127901	127901	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
127908	127908	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127909	127909	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127911	127911	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127912	127912	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127924	127924	Hatchback	A3 8V facelift	8V1	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH		READY
127927	127927	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH		READY
127928	127928	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
127929	127929	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
127965	127965	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127970	127970	Sedan	Nova 2105	2105	4	EU-LADA-NOVA-2105-SEDAN-01	HIGH		READY
127983	127983	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-M550D-01	HIGH	M550d专属前后保险杠外廓。	READY
127984	127984	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127985	127985	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127986	127986	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127987	127987	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127990	127990	SUV	F-Pace X761	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
127991	127991	Sedan	XE X760	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
127993	127993	Sedan	XF II X260	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
127995	127995	SUV	Range Rover Velar L560	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH		READY
128020	128020	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128026	128026	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128029	128029	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128047	128047	Hatchback	A5 II F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
128048	128048	Hatchback	A5 II F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
128049	128049	Coupe	A5 II F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
128090	128090	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-M550D-01	HIGH	M550d专属前后保险杠外廓。	READY
128091	128091	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128114	128114	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
128132	128132	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH		READY
128150	128150	Convertible	R8 II 4S	4S	2	EU-AUDI-R8-II-4S-SPYDER-01	HIGH		READY
128151	128151	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128152	128152	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128153	128153	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128154	128154	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128155	128155	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-X3-G01-SUV-M40I-01	4716	1897	1676	BMW X3 M40i official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0272141EN/389222
EU-BMW-X3-G01-SUV-STANDARD-01	4708	1891	1676	BMW X3 UK technical data; BMW X3 LCI official specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0272066EN_GB/397550;https://www.press.bmwgroup.com/global/article/attachment/T0329598EN/476186
EU-BMW-X1-F48-SUV-PREFL-01	4439	1821	1598	BMW X1 official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0286555EN/419620
EU-BMW-X1-F48-SUV-FACELIFT-01	4447	1821	1598	BMW X1 facelift official specifications	https://www.press.bmwgroup.com/india/article/attachment/T0308396EN/450185
EU-BMW-4-F82-COUPE-M4-CS-01	4672	1870	1392	BMW M4 CS BMW Group PressClub	https://www.press.bmwgroup.com/usa/article/detail/T0269939EN_US/the-first-ever-bmw-m4-cs%3A-sporting-appeal-high-performance-for-the-road-and-track-proven-dynamics?language=en_US
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384	BMW 4 Series Convertible UK technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0171272EN_GB/264232
EU-BMW-5-G31-WAGON-M550D-01	4962	1868	1488	ADAC BMW M550d Touring xDrive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/g30-g31-f90/301108/
EU-BMW-5-G30-SEDAN-M550D-01	4962	1868	1467	ADAC BMW M550d xDrive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/g30-g31-f90/277244/
```

下一步优先处理

1. 处理 Mercedes-Benz S-Class W222、Maybach X222 和 E-Class W213 的标准轴距、长轴及改款边界。
2. 处理 Toyota Hilux IV、Mitsubishi Pajero IV、Opel Combo D 的皮卡、三门/五门及 L1/L2 多外廓分支。
3. 核对 Jaguar Project 8、BMW M5 F90、AMG GT C、Vanquish S、Rolls-Royce Dawn 等特殊外部套件。
4. 闭合 Fabia III Hatchback/Wagon、C3 Aircross、Kona、Prius Plug-in、Ferrari 812、Arteon 等剩余常规尺寸组。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/asia/article/attachment/T0272141EN/389222 "Microsoft Word - 20170613_The_new_BMW_X3_Specifications_EN_V1.doc"
[2]: https://www.press.bmwgroup.com/usa/article/detail/T0269939EN_US/the-first-ever-bmw-m4-cs%3A-sporting-appeal-high-performance-for-the-road-and-track-proven-dynamics?language=en_US "The First Ever BMW M4 CS: Sporting Appeal, High Performance for the Road and Track-Proven Dynamics."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 17 个 Ktype 映射：Jaguar E-Pace 6 个动力版本共用 X540 标准车身组；XE Project 8 因专属宽体外廓独立建组。([捷豹媒体中心][1])
* Skoda Fabia III 已按 Hatchback 与 Wagon 两种物理外廓拆组，同车身不同功率 Ktype 直接复用。([汽车数据网][2])
* 闭合 Subaru XV II、Volvo V60 I facelift 标准 Wagon、Seat Toledo IV NH Liftback 尺寸组。([汽车数据网][3])
* Seat Ateca Ktype `127905` 直接关联已有改款前尺寸组，本轮不重复输出该尺寸组。([汽车数据网][4])

## 当前批次进度

* 已覆盖输入 Ktype：63 / 100
* READY 映射：64 行
* PENDING / 尚待处理输入 Ktype：37
* 当前累计引用尺寸组：36
* 本轮首次创建尺寸组：7
* 本轮复用已有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127905	127905	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
127941	127941	Hatchback	Fabia III		5	EU-SKODA-FABIA-III-HATCHBACK-01	HIGH		READY
127942	127942	Wagon	Fabia III		5	EU-SKODA-FABIA-III-WAGON-01	HIGH		READY
127973	127973	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127974	127974	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127975	127975	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127976	127976	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127977	127977	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127978	127978	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127992	127992	Sedan	XE X760	X760	4	EU-JAGUAR-XE-X760-SEDAN-PROJECT-8-01	HIGH	Project 8专属宽体外廓。	READY
128023	128023	SUV	XV II		5	EU-SUBARU-XV-II-SUV-01	HIGH		READY
128084	128084	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	HIGH		READY
128085	128085	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	HIGH		READY
128141	128141	Hatchback	Fabia III		5	EU-SKODA-FABIA-III-HATCHBACK-01	HIGH		READY
128142	128142	Wagon	Fabia III		5	EU-SKODA-FABIA-III-WAGON-01	HIGH		READY
128156	128156	Hatchback	Toledo IV	NH	5	EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	HIGH	五门掀背式三厢外廓。	READY
128157	128157	Hatchback	Toledo IV	NH	5	EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	HIGH	五门掀背式三厢外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-FABIA-III-HATCHBACK-01	3992	1732	1467	Auto-Data Skoda Fabia III	https://www.auto-data.net/en/skoda-fabia-iii-1.0-75hp-20397
EU-SKODA-FABIA-III-WAGON-01	4257	1732	1467	Auto-Data Skoda Fabia III Combi	https://www.auto-data.net/en/skoda-fabia-iii-combi-1.0-tsi-110hp-32102
EU-JAGUAR-E-PACE-X540-SUV-01	4395	1900	1649	Jaguar E-PACE official launch; Automobile Dimension Jaguar E-PACE; Auto-Data Jaguar E-Pace	https://media.jaguar.com/en-gb/news/2017/07/jaguar-e-pace-compact-performance-suv-sports-car-looks;https://www.automobiledimension.com/model/jaguar/e-pace;https://www.auto-data.net/en/jaguar-e-pace-2.0-d150-150hp-awd-30503
EU-JAGUAR-XE-X760-SEDAN-PROJECT-8-01	4713	1954	1436	Jaguar XE SV Project 8 technical press kit	https://media.jaguar.com/en-us/news/2017/06/technical-press-kit-jaguar-xe-sv-project-8
EU-SUBARU-XV-II-SUV-01	4465	1800	1615	Auto-Data Subaru XV II	https://www.auto-data.net/en/subaru-xv-ii-2.0i-156hp-awd-lineartronic-31509
EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	4635	1865	1484	Auto-Data Volvo V60 I facelift	https://www.auto-data.net/en/volvo-v60-i-facelift-2013-2.0-t5-245hp-geartronic-21747
EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	4482	1706	1461	Auto-Data Seat Toledo IV NH 1.0 TSI	https://www.auto-data.net/en/seat-toledo-iv-nh-1.0-tsi-95hp-33952
```

## 下一步优先处理

1. Mercedes-Benz S-Class W222/X222 与 E-Class W213 的标准轴距、长轴和 Maybach 外廓边界。
2. Toyota Hilux IV、Opel Combo D 的驾驶室、货斗及 L1/L2 多外廓拆分。
3. AMG GT C、BMW M5 F90、Ferrari 812、Vanquish S、Dawn、Evoque Convertible 等特殊外部版本。
4. 解决 C3 Aircross I 宽度来源冲突，以及 BMW `128113` 属于 F45 或 F46 的车身边界。
5. 处理剩余 Lada、Kyron、Pajero、Kona、Prius Plug-in 和 Arteon 聚类。

推进信号：CONTINUE

[1]: https://media.jaguar.com/en-gb/news/2017/07/jaguar-e-pace-compact-performance-suv-sports-car-looks "JAGUAR E-PACE – THE COMPACT PERFORMANCE SUV WITH SPORTS CAR LOOKS | Jaguar 2024 Media Newsroom"
[2]: https://www.auto-data.net/en/skoda-fabia-iii-1.0-75hp-20397 "Skoda Fabia III 1.0 (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/subaru-xv-ii-2.0i-156hp-awd-lineartronic-31509 "Subaru XV II 2.0i (156 Hp) AWD Lineartronic | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/seat-ateca-i-2.0-tsi-190hp-4drive-dsg-30579 "Seat Ateca I 2.0 TSI (190 Hp) 4Drive DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Kyron、Lada 2106、Kalina Sport、Lada 2102 Wagon、Elantra AD、Kona OS、Solaris II 等标准外廓。([汽车数据网][1])
* C3 Aircross I 的 6 个 Ktype 共用同一改款前尺寸组；来源明确区分车身宽度、折叠后视镜宽度和含镜宽度。([汽车数据网][2])
* Range Rover Evoque Convertible 按两门敞篷车身独立建组，宽度采用不含后视镜的 1900 mm。([汽车目录档案][3])
* BMW `128146`、三个 Arteon Ktype 均跨越物理尺寸发生变化的改款节点，已拆分为 `prefl` 与 `facelift`，直接关联已有尺寸组。
* 闭合 Rolls-Royce Dawn 与 Ferrari 812 Superfast 尺寸组。([汽车数据网][4])

## 当前批次进度

* 已覆盖输入 Ktype：83 / 100
* READY 映射：88 行
* PENDING / 尚待处理输入 Ktype：17
* 当前累计引用尺寸组：49
* 本轮新增映射：24 行
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127902	127902	SUV	Kyron I facelift	DJ	5	EU-SSANGYONG-KYRON-I-SUV-FACELIFT-01	HIGH		READY
127969	127969	Sedan	2106	2106	4	EU-LADA-2106-SEDAN-01	HIGH		READY
127972	127972	Hatchback	Kalina II	2192	5	EU-LADA-KALINA-II-2192-HATCHBACK-SPORT-01	HIGH	Sport专属保险杠和离地高度外廓。	READY
128002	128002	Sedan	Elantra VI AD	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	HIGH	标准版外廓，不复用SR组。	READY
128009	128009	Wagon	2102	2102	5	EU-LADA-2102-WAGON-01	HIGH		READY
128030	128030	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128106	128106	Sedan	Solaris II		4	EU-HYUNDAI-SOLARIS-II-SEDAN-01	HIGH		READY
128133	128133	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128134	128134	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128135	128135	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128136	128136	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128144	128144	Convertible	Dawn		2	EU-ROLLS-ROYCE-DAWN-CONVERTIBLE-01	HIGH		READY
128145	128145	Convertible	Range Rover Evoque I facelift	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	HIGH	两门敞篷物理外廓。	READY
128146_prefl	128146	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
128146_facelift	128146	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	Ktype覆盖2020年改款后外廓。	READY
128158	128158	Coupe	812 Superfast	F152M	2	EU-FERRARI-812-SUPERFAST-COUPE-01	HIGH		READY
128179_prefl	128179	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128179_facelift	128179	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128180_prefl	128180	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128180_facelift	128180	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128181_prefl	128181	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128181_facelift	128181	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128184	128184	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128185	128185	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SSANGYONG-KYRON-I-SUV-FACELIFT-01	4660	1880	1755	Auto-Data SsangYong Kyron facelift 2.3i	https://www.auto-data.net/en/ssangyong-kyron-facelift-2007-2.3i-16v-150hp-16020
EU-LADA-2106-SEDAN-01	4166	1611	1440	Auto-Data Lada 2106	https://www.auto-data.net/en/lada-2106-generation-2794
EU-LADA-KALINA-II-2192-HATCHBACK-SPORT-01	3943	1700	1450	Auto-Data Lada Kalina II Sport	https://www.auto-data.net/en/lada-kalina-ii-hatchback-2192-sport-1.6-118hp-22351
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	4569	1801	1435	Auto-Data Hyundai Elantra VI AD	https://www.auto-data.net/en/hyundai-elantra-vi-ad-2.0-149hp-automatic-32726
EU-LADA-2102-WAGON-01	4059	1611	1458	Auto-Data Lada 2102	https://www.auto-data.net/en/lada-2102-model-1412
EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	4165	1801	1565	Auto-Data Hyundai Kona I	https://www.auto-data.net/en/hyundai-kona-i-1.6-t-gdi-177hp-automatic-32742
EU-HYUNDAI-SOLARIS-II-SEDAN-01	4405	1729	1469	Auto-Data Hyundai Solaris II Sedan	https://www.auto-data.net/en/hyundai-solaris-ii-sedan-1.6-mpi-123hp-automatic-30960
EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	4154	1756	1637	Auto-Data Citroen C3 Aircross I Phase I	https://www.auto-data.net/en/citroen-c3-aircross-i-phase-i-2017-1.2-puretech-110hp-39047
EU-ROLLS-ROYCE-DAWN-CONVERTIBLE-01	5285	1947	1502	Auto-Data Rolls-Royce Dawn	https://www.auto-data.net/en/rolls-royce-dawn-generation-4946
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	4370	1900	1609	Range Rover Evoque Convertible brochure; Automobile Dimension Evoque Convertible	https://autocatalogarchive.com/wp-content/uploads/2017/05/Range-Rover-Evoque-Convertible-2015-UK.pdf;https://www.automobiledimension.com/model/land-rover/range-rover-evoque-convertible
EU-FERRARI-812-SUPERFAST-COUPE-01	4657	1971	1276	Ferrari 812 Superfast official specifications	https://www.ferrari.com/en-EN/auto/812-superfast
```

## 下一步优先处理

1. Mercedes-Benz S-Class W222/X222、Maybach 和 E-Class W213 的轴距及外廓边界。
2. Toyota Hilux IV 的驾驶室、轴距和货斗物理分支。
3. Opel Combo D/Combo Tour 的 L1、L2 及 Van/MPV 派生关系。
4. Mitsubishi Pajero IV 的三门、五门边界。
5. AMG GT C、BMW M5 F90、BMW 218i F45/F46、Lotus 3-Eleven、Vanquish S Coupe/Volante、Prius Plug-in 的剩余特殊外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ssangyong-kyron-facelift-2007-2.3i-16v-150hp-16020 "SsangYong Kyron (facelift 2007) 2.3i 16V (150 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/citroen-c3-aircross-i-phase-i-2017-1.2-puretech-110hp-39047?utm_source=chatgpt.com "Citroen C3 Aircross I (Phase I, 2017) 1.2 PureTech (110 Hp)"
[3]: https://autocatalogarchive.com/wp-content/uploads/2017/05/Range-Rover-Evoque-Convertible-2015-UK.pdf?utm_source=chatgpt.com "RANGE ROVER EVOQUE"
[4]: https://www.auto-data.net/en/rolls-royce-dawn-model-2136?utm_source=chatgpt.com "Rolls-Royce Dawn | Technical Specs, Fuel consumption ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Mercedes-Benz Maybach S-Class X222、S-Class W222 与 E-Class W213 三个尺寸组；相同车身的动力版本直接复用。([汽车数据网][1])
* Mitsubishi Pajero IV Ktype `128025` 已按三门短轴和五门长轴拆分。([汽车数据网][2])
* Opel Combo Tour 已按 L1/L2 新建乘用车尺寸组；Combo Cargo 直接复用已有 L1/L2 货运尺寸组。官方资料分别列明长度、车身宽度与高度。([摩托资产][3])
* 闭合 AMG GT C、BMW 218i Gran Tourer、Lotus 3-Eleven Road、Vanquish S Coupe、Prius Plug-in；Vanquish S Volante复用既有尺寸组。([汽车目录][4])
* BMW M5 F90 Ktype `128183` 跨越改款尺寸变化，已拆分为改款前和改款后两行。([汽车数据网][5])
* 当前仅剩 Toyota Hilux IV Ktype `127891` 的 LN51/LN56 物理分支尚未闭合。

## 当前批次进度

* 已覆盖输入 Ktype：99 / 100
* READY 映射：108 行
* PENDING / 尚待处理输入 Ktype：1
* 当前累计引用尺寸组：66
* 本轮新增映射：20 行
* 本轮首次创建尺寸组：14
* 本轮复用既有尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
128014	128014	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	HIGH		READY
128015	128015	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	HIGH		READY
128016	128016	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128017	128017	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128024	128024	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH		READY
128025_3dr	128025	SUV	Pajero IV facelift	V8_W	3	EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-3D-01	HIGH	Ktype覆盖三门短轴外廓。	READY
128025_5dr	128025	SUV	Pajero IV facelift	V9_W	5	EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-5D-01	HIGH	Ktype覆盖五门长轴外廓。	READY
128046	128046	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTC-01	HIGH	GT C宽体外廓。	READY
128056_l1	128056	MPV	Combo D X12		5	EU-OPEL-COMBO-D-X12-TOUR-L1H1-01	HIGH	L1乘用车外廓。	READY
128056_l2	128056	MPV	Combo D X12		5	EU-OPEL-COMBO-D-X12-TOUR-L2H1-01	HIGH	L2乘用车外廓。	READY
128057_l1	128057	Van	Combo D X12	B05		EU-OPEL-COMBO-D-X12-BODY-L1H1-01	HIGH	L1货运车身外廓。	READY
128057_l2	128057	Van	Combo D X12	B05		EU-OPEL-COMBO-D-X12-BODY-L2H1-01	HIGH	L2货运车身外廓。	READY
128089	128089	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128113	128113	MPV	2 Series Gran Tourer F46 facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	HIGH		READY
128117	128117	Convertible	3-Eleven		2	EU-LOTUS-3-ELEVEN-ROAD-CONVERTIBLE-01	HIGH	开放式Road版本。	READY
128126	128126	Coupe	Vanquish II S		2	EU-ASTON-MARTIN-VANQUISH-II-S-COUPE-01	HIGH		READY
128127	128127	Convertible	Vanquish II S Volante		2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	HIGH		READY
128130	128130	Hatchback	Prius IV XW50	XW50	5	EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	HIGH		READY
128183_prefl	128183	Sedan	M5 F90	F90	4	EU-BMW-M5-F90-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
128183_facelift	128183	Sedan	M5 F90 facelift	F90	4	EU-BMW-M5-F90-SEDAN-FACELIFT-01	HIGH	Ktype覆盖2020年改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	5462	1899	1498	Auto-Data Mercedes-Benz Maybach S-class X222 facelift	https://www.auto-data.net/en/mercedes-benz-maybach-s-class-x222-facelift-2017-s-560-v8-469hp-g-tronic-30685
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	5141	1905	1498	Auto-Data Mercedes-Benz S-class W222 facelift	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-400d-340hp-g-tronic-31874
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-class W213 E 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-350d-v6-258hp-4matic-9g-tronic-32288
EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV facelift 3-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-facelift-2015-3.2-di-dc-190hp-4x4-automatic-32224
EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-5D-01	4900	1875	1890	Auto-Data Mitsubishi Pajero IV facelift 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-facelift-2015-3.2-di-dc-190hp-l-4x4-automatic-32458
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTC-01	4551	2007	1284	Automobile-Catalog Mercedes-AMG GT C	https://www.automobile-catalog.com/car/2017/2727245/mercedes-amg_gt_c.html
EU-OPEL-COMBO-D-X12-TOUR-L1H1-01	4390	1831	1845	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-OPEL-COMBO-D-X12-TOUR-L2H1-01	4740	1831	1880	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1608	Auto-Data BMW 2 Series Gran Tourer F46 LCI	https://www.auto-data.net/en/bmw-2-series-gran-tourer-f46-lci-facelift-2018-218i-140hp-32477
EU-LOTUS-3-ELEVEN-ROAD-CONVERTIBLE-01	4080	1800	1100	Automobile-Catalog Lotus 3-Eleven Road; Auto-Data Lotus 3-Eleven Road	https://www.automobile-catalog.com/car/2016/2408480/lotus_3-eleven_road.html;https://www.auto-data.net/en/lotus-3-eleven-road-3.5-v6-416hp-24299
EU-ASTON-MARTIN-VANQUISH-II-S-COUPE-01	4728	1912	1294	EncyCARpedia Aston Martin Vanquish S	https://www.encycarpedia.com/aston-martin/16-vanquish-s-coupe
EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	4645	1760	1470	Auto-Data Toyota Prius IV XW50 Plug-in Hybrid	https://www.auto-data.net/en/toyota-prius-iv-xw50-1.8-122hp-plug-in-hybrid-e-cvt-44139
EU-BMW-M5-F90-SEDAN-PREFL-01	4966	1903	1473	Auto-Data BMW M5 F90	https://www.auto-data.net/en/bmw-m5-f90-generation-5548
EU-BMW-M5-F90-SEDAN-FACELIFT-01	4983	1903	1473	Auto-Data BMW M5 F90 LCI	https://www.auto-data.net/en/bmw-m5-f90-lci-facelift-2020-4.4-v8-600hp-xdrive-steptronic-40539
```

## 下一步优先处理

1. 仅处理 Ktype `127891`：确认 Toyota Hilux IV 2.4 D 对应的 LN51、LN56 驾驶室、轴距及货斗物理分支。
2. 闭合各分支同一配置的长宽高，并确认宽度为不含后视镜口径。
3. 完成后立即执行一次机械收尾并输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-400d-340hp-g-tronic-31874 "Mercedes-Benz S-class (W222, facelift 2017) S 400d (340 Hp) G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-pajero-iv-facelift-2015-3.2-di-dc-190hp-4x4-automatic-32224 "Mitsubishi Pajero IV (facelift 2015) 3.2 DI-DC (190 Hp) 4x4 Automatic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf "Opel Media Information"
[4]: https://www.automobile-catalog.com/car/2017/2727245/mercedes-amg_gt_c.html?utm_source=chatgpt.com "2017 Mercedes-AMG GT C Specs Review (410 kW / 558 PS / 550 hp) (since mid-year 2017 for Europe North America worldwide)"
[5]: https://www.auto-data.net/en/bmw-m5-f90-lci-facelift-2020-4.4-v8-600hp-xdrive-steptronic-40539?utm_source=chatgpt.com "Specs of BMW M5 (F90 LCI, facelift 2020) 4.4 V8 (600 Hp) ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1501-1600_ktype_dimension_mapping_final.tsv
- all_1501-1600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后一个阻塞项 Ktype `127891` 已按 Toyota Hilux IV 的 `LN51` 标准轴距车身与 `LN56` 长轴车身拆分，并分别建立尺寸组。车型目录确认该 Ktype 同时覆盖 LN51、LN56；LN56 资料明确为两门长车身，尺寸 `4690×1620×1565 mm`。([DENSO][1])
* 已完成轻量机械收尾：表头正确、110 个 `id` 唯一、69 个 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、尺寸及来源字段完整。
* 当前批次 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：110 行
* PENDING 映射：0
* DIMENSION_GROUP：69 个
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
127830	127830	Hatchback	6 Series G32	G32	5	EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	HIGH		READY
127852	127852	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-M40I-01	HIGH	M40i专属外廓。	READY
127854	127854	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127855	127855	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127856	127856	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127857	127857	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
127858_prefl	127858	SUV	X1 F48	F48	5	EU-BMW-X1-F48-SUV-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
127858_facelift	127858	SUV	X1 F48	F48	5	EU-BMW-X1-F48-SUV-FACELIFT-01	HIGH	Ktype覆盖2019年改款后外廓。	READY
127860	127860	Coupe	M4 F82	F82	2	EU-BMW-4-F82-COUPE-M4-CS-01	HIGH	M4 CS专属外廓。	READY
127861	127861	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH		READY
127864	127864	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-WAGON-01	HIGH		READY
127891_swb	127891	Pickup	Hilux IV N50	LN51	2	EU-TOYOTA-HILUX-IV-N50-PICKUP-LN51-SWB-01	MEDIUM	LN51标准轴距单排驾驶室外廓。	READY
127891_lwb	127891	Pickup	Hilux IV N60	LN56	2	EU-TOYOTA-HILUX-IV-N60-PICKUP-LN56-LWB-01	MEDIUM	LN56长轴单排驾驶室外廓。	READY
127901	127901	Convertible	4 Series F33	F33	2	EU-BMW-4-F33-CONVERTIBLE-01	HIGH		READY
127902	127902	SUV	Kyron I facelift	DJ	5	EU-SSANGYONG-KYRON-I-SUV-FACELIFT-01	HIGH		READY
127905	127905	SUV	Ateca I		5	EU-SEAT-ATECA-I-SUV-PREFL-01	HIGH		READY
127908	127908	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127909	127909	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127911	127911	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127912	127912	Coupe	4 Series F32	F32	2	EU-BMW-4-F32-COUPE-01	HIGH		READY
127924	127924	Hatchback	A3 8V facelift	8V1	3	EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	HIGH		READY
127927	127927	Hatchback	A3 8V facelift	8VA	5	EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	HIGH		READY
127928	127928	Sedan	A3 8V facelift	8VS	4	EU-AUDI-A3-8V-FACELIFT-SEDAN-01	HIGH		READY
127929	127929	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
127941	127941	Hatchback	Fabia III		5	EU-SKODA-FABIA-III-HATCHBACK-01	HIGH		READY
127942	127942	Wagon	Fabia III		5	EU-SKODA-FABIA-III-WAGON-01	HIGH		READY
127965	127965	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127969	127969	Sedan	2106	2106	4	EU-LADA-2106-SEDAN-01	HIGH		READY
127970	127970	Sedan	Nova 2105	2105	4	EU-LADA-NOVA-2105-SEDAN-01	HIGH		READY
127972	127972	Hatchback	Kalina II	2192	5	EU-LADA-KALINA-II-2192-HATCHBACK-SPORT-01	HIGH	Sport专属保险杠和离地高度外廓。	READY
127973	127973	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127974	127974	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127975	127975	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127976	127976	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127977	127977	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127978	127978	SUV	E-Pace X540	X540	5	EU-JAGUAR-E-PACE-X540-SUV-01	HIGH		READY
127983	127983	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-M550D-01	HIGH	M550d专属前后保险杠外廓。	READY
127984	127984	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127985	127985	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127986	127986	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127987	127987	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
127990	127990	SUV	F-Pace X761	X761	5	EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	HIGH		READY
127991	127991	Sedan	XE X760	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
127992	127992	Sedan	XE X760	X760	4	EU-JAGUAR-XE-X760-SEDAN-PROJECT-8-01	HIGH	Project 8专属宽体外廓。	READY
127993	127993	Sedan	XF II X260	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
127995	127995	SUV	Range Rover Velar L560	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH		READY
128002	128002	Sedan	Elantra VI AD	AD	4	EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	HIGH	标准版外廓，不复用SR组。	READY
128009	128009	Wagon	2102	2102	5	EU-LADA-2102-WAGON-01	HIGH		READY
128014	128014	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	HIGH		READY
128015	128015	Sedan	Maybach S-Class X222 facelift	X222	4	EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	HIGH		READY
128016	128016	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128017	128017	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128020	128020	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128023	128023	SUV	XV II		5	EU-SUBARU-XV-II-SUV-01	HIGH		READY
128024	128024	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH		READY
128025_3dr	128025	SUV	Pajero IV facelift	V8_W	3	EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-3D-01	HIGH	Ktype覆盖三门短轴外廓。	READY
128025_5dr	128025	SUV	Pajero IV facelift	V9_W	5	EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-5D-01	HIGH	Ktype覆盖五门长轴外廓。	READY
128026	128026	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128029	128029	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128030	128030	SUV	Kona I	OS	5	EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	HIGH		READY
128046	128046	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTC-01	HIGH	GT C宽体外廓。	READY
128047	128047	Hatchback	A5 II F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
128048	128048	Hatchback	A5 II F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
128049	128049	Coupe	A5 II F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
128056_l1	128056	MPV	Combo D X12		5	EU-OPEL-COMBO-D-X12-TOUR-L1H1-01	HIGH	L1乘用车外廓。	READY
128056_l2	128056	MPV	Combo D X12		5	EU-OPEL-COMBO-D-X12-TOUR-L2H1-01	HIGH	L2乘用车外廓。	READY
128057_l1	128057	Van	Combo D X12	B05		EU-OPEL-COMBO-D-X12-BODY-L1H1-01	HIGH	L1货运车身外廓。	READY
128057_l2	128057	Van	Combo D X12	B05		EU-OPEL-COMBO-D-X12-BODY-L2H1-01	HIGH	L2货运车身外廓。	READY
128084	128084	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	HIGH		READY
128085	128085	Wagon	V60 I facelift		5	EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	HIGH		READY
128089	128089	Sedan	S-Class W222 facelift	W222	4	EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	HIGH		READY
128090	128090	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-M550D-01	HIGH	M550d专属前后保险杠外廓。	READY
128091	128091	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128106	128106	Sedan	Solaris II		4	EU-HYUNDAI-SOLARIS-II-SEDAN-01	HIGH		READY
128113	128113	MPV	2 Series Gran Tourer F46 facelift	F46	5	EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	HIGH		READY
128114	128114	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
128117	128117	Convertible	3-Eleven		2	EU-LOTUS-3-ELEVEN-ROAD-CONVERTIBLE-01	HIGH	开放式Road版本。	READY
128126	128126	Coupe	Vanquish II S		2	EU-ASTON-MARTIN-VANQUISH-II-S-COUPE-01	HIGH		READY
128127	128127	Convertible	Vanquish II S Volante		2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	HIGH		READY
128130	128130	Hatchback	Prius IV XW50	XW50	5	EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	HIGH		READY
128132	128132	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH		READY
128133	128133	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128134	128134	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128135	128135	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128136	128136	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128141	128141	Hatchback	Fabia III		5	EU-SKODA-FABIA-III-HATCHBACK-01	HIGH		READY
128142	128142	Wagon	Fabia III		5	EU-SKODA-FABIA-III-WAGON-01	HIGH		READY
128144	128144	Convertible	Dawn		2	EU-ROLLS-ROYCE-DAWN-CONVERTIBLE-01	HIGH		READY
128145	128145	Convertible	Range Rover Evoque I facelift	L538	2	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	HIGH	两门敞篷物理外廓。	READY
128146_prefl	128146	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
128146_facelift	128146	Sedan	5 Series G30 facelift	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-01	HIGH	Ktype覆盖2020年改款后外廓。	READY
128150	128150	Convertible	R8 II 4S	4S	2	EU-AUDI-R8-II-4S-SPYDER-01	HIGH		READY
128151	128151	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128152	128152	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128153	128153	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH		READY
128154	128154	Wagon	5 Series G31	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH		READY
128155	128155	SUV	X3 G01	G01	5	EU-BMW-X3-G01-SUV-STANDARD-01	HIGH		READY
128156	128156	Hatchback	Toledo IV	NH	5	EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	HIGH	五门掀背式三厢外廓。	READY
128157	128157	Hatchback	Toledo IV	NH	5	EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	HIGH	五门掀背式三厢外廓。	READY
128158	128158	Coupe	812 Superfast	F152M	2	EU-FERRARI-812-SUPERFAST-COUPE-01	HIGH		READY
128179_prefl	128179	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128179_facelift	128179	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128180_prefl	128180	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128180_facelift	128180	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128181_prefl	128181	Hatchback	Arteon I 3H	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	Ktype覆盖改款前Liftback外廓。	READY
128181_facelift	128181	Hatchback	Arteon I 3H facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	Ktype覆盖2020年改款后Liftback外廓。	READY
128183_prefl	128183	Sedan	M5 F90	F90	4	EU-BMW-M5-F90-SEDAN-PREFL-01	HIGH	Ktype覆盖改款前外廓。	READY
128183_facelift	128183	Sedan	M5 F90 facelift	F90	4	EU-BMW-M5-F90-SEDAN-FACELIFT-01	HIGH	Ktype覆盖2020年改款后外廓。	READY
128184	128184	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
128185	128185	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1501-1600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-6-G32-GRAN-TURISMO-HATCHBACK-01	5091	1902	1538	BMW 6 Series Gran Turismo official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0271742EN/388196
EU-BMW-X3-G01-SUV-M40I-01	4716	1897	1676	BMW X3 M40i official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0272141EN/389222
EU-BMW-X3-G01-SUV-STANDARD-01	4708	1891	1676	BMW X3 UK technical data; BMW X3 LCI official specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0272066EN_GB/397550;https://www.press.bmwgroup.com/global/article/attachment/T0329598EN/476186
EU-BMW-X1-F48-SUV-PREFL-01	4439	1821	1598	BMW X1 official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0286555EN/419620
EU-BMW-X1-F48-SUV-FACELIFT-01	4447	1821	1598	BMW X1 facelift official specifications	https://www.press.bmwgroup.com/india/article/attachment/T0308396EN/450185
EU-BMW-4-F82-COUPE-M4-CS-01	4672	1870	1392	BMW M4 CS BMW Group PressClub	https://www.press.bmwgroup.com/usa/article/detail/T0269939EN_US/the-first-ever-bmw-m4-cs%3A-sporting-appeal-high-performance-for-the-road-and-track-proven-dynamics?language=en_US
EU-MINI-MINI-F54-WAGON-01	4253	1800	1441	MINI Clubman official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252423EN/353092
EU-TOYOTA-HILUX-IV-N50-PICKUP-LN51-SWB-01	4455	1620	1535	CarsGuide Toyota HiLux 1987 dimensions	https://www.carsguide.com.au/toyota/hilux/car-dimensions/1987
EU-TOYOTA-HILUX-IV-N60-PICKUP-LN56-LWB-01	4690	1620	1565	Drom Toyota Hilux N-LN56 specifications	https://www.drom.ru/catalog/toyota/frame/n-ln56/
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384	BMW 4 Series Convertible UK technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0171272EN_GB/264232
EU-SSANGYONG-KYRON-I-SUV-FACELIFT-01	4660	1880	1755	Auto-Data SsangYong Kyron facelift 2.3i	https://www.auto-data.net/en/ssangyong-kyron-facelift-2007-2.3i-16v-150hp-16020
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601	SEAT Ateca official specifications brochure	https://www.seat.com/content/dam/public/seat-website/car-shopping-tools/brochure-download/brochures/ateca/cars-specs-brochure-KH7-NA-december-2018.pdf
EU-BMW-4-F32-COUPE-01	4638	1825	1377	BMW 4 Series Coupe official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252345EN/348118
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424	Auto-Data Audi A3 8V facelift	https://www.auto-data.net/en/audi-a3-8v-facelift-2016-1.5-tfsi-150hp-32145
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426	Audi A3 Sportback official technical data	https://i.i-sgcm.com/new_cars/cars/11330/brochures/brochure_20180906061018.pdf
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416	Audi A3 Sedan official specification sheet	https://i.i-sgcm.com/new_cars/cars/11451/brochures/brochure_20170104095525.pdf
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409	Audi A3 Cabriolet official dimensions	https://press.audi.co.uk/assets/documents/original/11386-AudiUK00001700AudiA3andS3Cabriolet.pdf
EU-SKODA-FABIA-III-HATCHBACK-01	3992	1732	1467	Auto-Data Skoda Fabia III	https://www.auto-data.net/en/skoda-fabia-iii-1.0-75hp-20397
EU-SKODA-FABIA-III-WAGON-01	4257	1732	1467	Auto-Data Skoda Fabia III Combi	https://www.auto-data.net/en/skoda-fabia-iii-combi-1.0-tsi-110hp-32102
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos official brochure	https://www.renault.qa/CountriesData/Qatar_EN/images/brochures/EN/Koleos-brochure-EN.pdf
EU-LADA-2106-SEDAN-01	4166	1611	1440	Auto-Data Lada 2106	https://www.auto-data.net/en/lada-2106-generation-2794
EU-LADA-NOVA-2105-SEDAN-01	4130	1620	1446	Auto-Data Lada 2105	https://www.auto-data.net/en/lada-2105-generation-2864
EU-LADA-KALINA-II-2192-HATCHBACK-SPORT-01	3943	1700	1450	Auto-Data Lada Kalina II Sport	https://www.auto-data.net/en/lada-kalina-ii-hatchback-2192-sport-1.6-118hp-22351
EU-JAGUAR-E-PACE-X540-SUV-01	4395	1900	1649	Jaguar E-PACE official launch; Automobile Dimension Jaguar E-PACE; Auto-Data Jaguar E-Pace	https://media.jaguar.com/en-gb/news/2017/07/jaguar-e-pace-compact-performance-suv-sports-car-looks;https://www.automobiledimension.com/model/jaguar/e-pace;https://www.auto-data.net/en/jaguar-e-pace-2.0-d150-150hp-awd-30503
EU-BMW-5-G31-WAGON-M550D-01	4962	1868	1488	ADAC BMW M550d Touring xDrive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/g30-g31-f90/301108/
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498	BMW 5 Series Touring official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0267496EN/384775
EU-JAGUAR-F-PACE-X761-SUV-PREFL-01	4731	1936	1652	Jaguar F-PACE official brochure	https://www.jaguar.com/content/dam/jdx/pdfs/uk/JGGL-FPAC17-PRT0520_F_PACE_17MY_MB_GEE%20UPDATE_V3.pdf
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1416	Jaguar XE official launch specifications	https://archive.jaguar.com/news/2014/09/world-premiere-jaguar-xe-londons-earls-court
EU-JAGUAR-XE-X760-SEDAN-PROJECT-8-01	4713	1954	1436	Jaguar XE SV Project 8 technical press kit	https://media.jaguar.com/en-us/news/2017/06/technical-press-kit-jaguar-xe-sv-project-8
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457	Jaguar XF official technical specifications	https://media.production.jlrms.com/download_archives/a26ddd69-f8b6-48df-a835-53d4dc54f510/jaguar-xf-2017-my-te.zip?VersionId=V0D_Eb2YCbJCzMhgFNgBDvB5N7TzoGE9
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	4803	2032	1665	Range Rover Velar official specifications	https://i.i-sgcm.com/new_cars/cars/12179/brochures/brochure_20170929112157.pdf
EU-HYUNDAI-ELANTRA-VI-AD-SEDAN-STANDARD-01	4569	1801	1435	Auto-Data Hyundai Elantra VI AD	https://www.auto-data.net/en/hyundai-elantra-vi-ad-2.0-149hp-automatic-32726
EU-LADA-2102-WAGON-01	4059	1611	1458	Auto-Data Lada 2102	https://www.auto-data.net/en/lada-2102-model-1412
EU-MERCEDES-BENZ-MAYBACH-S-CLASS-X222-SEDAN-FACELIFT-01	5462	1899	1498	Auto-Data Mercedes-Benz Maybach S-class X222 facelift	https://www.auto-data.net/en/mercedes-benz-maybach-s-class-x222-facelift-2017-s-560-v8-469hp-g-tronic-30685
EU-MERCEDES-BENZ-S-CLASS-W222-SEDAN-FACELIFT-01	5141	1905	1498	Auto-Data Mercedes-Benz S-class W222 facelift	https://www.auto-data.net/en/mercedes-benz-s-class-w222-facelift-2017-s-400d-340hp-g-tronic-31874
EU-SUBARU-XV-II-SUV-01	4465	1800	1615	Auto-Data Subaru XV II	https://www.auto-data.net/en/subaru-xv-ii-2.0i-156hp-awd-lineartronic-31509
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-class W213 E 350d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-350d-v6-258hp-4matic-9g-tronic-32288
EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV facelift 3-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-facelift-2015-3.2-di-dc-190hp-4x4-automatic-32224
EU-MITSUBISHI-PAJERO-IV-FACELIFT-SUV-5D-01	4900	1875	1890	Auto-Data Mitsubishi Pajero IV facelift 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-facelift-2015-3.2-di-dc-190hp-l-4x4-automatic-32458
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	Automobile-Catalog BMW 520i G30	https://www.automobile-catalog.com/car/2017/2547755/bmw_520i.html
EU-HYUNDAI-KONA-I-OS-SUV-PREFL-01	4165	1801	1565	Auto-Data Hyundai Kona I	https://www.auto-data.net/en/hyundai-kona-i-1.6-t-gdi-177hp-automatic-32742
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTC-01	4551	2007	1284	Automobile-Catalog Mercedes-AMG GT C	https://www.automobile-catalog.com/car/2017/2727245/mercedes-amg_gt_c.html
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi A5 Sportback official technical data	https://press.audi.co.uk/assets/documents/original/16287-AudiUK00017563AudiA5andS5Sportback.pdf
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Audi A5 Coupe official dimensions	https://press.audi.co.uk/assets/documents/original/16061-AudiUK00019927AudiA5andS5Coup%C3%A9Sportback.pdf
EU-OPEL-COMBO-D-X12-TOUR-L1H1-01	4390	1831	1845	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-OPEL-COMBO-D-X12-TOUR-L2H1-01	4740	1831	1880	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-OPEL-COMBO-D-X12-BODY-L1H1-01	4390	1832	1845	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-OPEL-COMBO-D-X12-BODY-L2H1-01	4740	1832	1880	Opel Combo official technical sheet	https://asset.moto.it/pricelist/auto/05b01e2f4c2cabc8d9f3c2b961a96199/scheda-tecnica_combo_2012.pdf
EU-VOLVO-V60-I-FACELIFT-WAGON-STANDARD-01	4635	1865	1484	Auto-Data Volvo V60 I facelift	https://www.auto-data.net/en/volvo-v60-i-facelift-2013-2.0-t5-245hp-geartronic-21747
EU-BMW-5-G30-SEDAN-M550D-01	4962	1868	1467	ADAC BMW M550d xDrive	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/5er-reihe/g30-g31-f90/277244/
EU-HYUNDAI-SOLARIS-II-SEDAN-01	4405	1729	1469	Auto-Data Hyundai Solaris II Sedan	https://www.auto-data.net/en/hyundai-solaris-ii-sedan-1.6-mpi-123hp-automatic-30960
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1608	Auto-Data BMW 2 Series Gran Tourer F46 LCI	https://www.auto-data.net/en/bmw-2-series-gran-tourer-f46-lci-facelift-2018-218i-140hp-32477
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo XC60 official dimensions	https://www.volvocars.com/uk/support/car/xc60/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-LOTUS-3-ELEVEN-ROAD-CONVERTIBLE-01	4080	1800	1100	Automobile-Catalog Lotus 3-Eleven Road; Auto-Data Lotus 3-Eleven Road	https://www.automobile-catalog.com/car/2016/2408480/lotus_3-eleven_road.html;https://www.auto-data.net/en/lotus-3-eleven-road-3.5-v6-416hp-24299
EU-ASTON-MARTIN-VANQUISH-II-S-COUPE-01	4728	1912	1294	EncyCARpedia Aston Martin Vanquish S	https://www.encycarpedia.com/aston-martin/16-vanquish-s-coupe
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	4728	1912	1294	Aston Martin Vanquish Volante official brochure	https://astonmartins.com/wp-content/uploads/2013/05/Aston-Martin_Vanquish_Volante_brochure.pdf
EU-TOYOTA-PRIUS-IV-XW50-PLUG-IN-HATCHBACK-01	4645	1760	1470	Auto-Data Toyota Prius IV XW50 Plug-in Hybrid	https://www.auto-data.net/en/toyota-prius-iv-xw50-1.8-122hp-plug-in-hybrid-e-cvt-44139
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140	Donkervoort D8 GTO official specifications	https://www.donkervoort.com/en/models/heritage/donkervoort-d8-gto/
EU-CITROEN-C3-AIRCROSS-I-SUV-PREFL-01	4154	1756	1637	Auto-Data Citroen C3 Aircross I Phase I	https://www.auto-data.net/en/citroen-c3-aircross-i-phase-i-2017-1.2-puretech-110hp-39047
EU-ROLLS-ROYCE-DAWN-CONVERTIBLE-01	5285	1947	1502	Auto-Data Rolls-Royce Dawn	https://www.auto-data.net/en/rolls-royce-dawn-generation-4946
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-I-L538-CONVERTIBLE-01	4370	1900	1609	Range Rover Evoque Convertible brochure; Automobile Dimension Evoque Convertible	https://autocatalogarchive.com/wp-content/uploads/2017/05/Range-Rover-Evoque-Convertible-2015-UK.pdf;https://www.automobiledimension.com/model/land-rover/range-rover-evoque-convertible
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479	BMW 5 Series Sedan facelift official specifications	https://www.press.bmwgroup.com/asia/article/attachment/T0308949EN/451369
EU-AUDI-R8-II-4S-SPYDER-01	4426	1940	1244	Audi R8 Spyder official technical data	https://press.audi.co.uk/assets/documents/original/26274-AudiUK00017613AudiR8SpyderV10540PS.pdf
EU-SEAT-TOLEDO-IV-NH-LIFTBACK-01	4482	1706	1461	Auto-Data Seat Toledo IV NH 1.0 TSI	https://www.auto-data.net/en/seat-toledo-iv-nh-1.0-tsi-95hp-33952
EU-FERRARI-812-SUPERFAST-COUPE-01	4657	1971	1276	Ferrari 812 Superfast official specifications	https://www.ferrari.com/en-EN/auto/812-superfast
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450	Volkswagen Arteon official brochure	https://i.i-sgcm.com/new_cars/cars/12225/brochures/brochure_20180104122923.pdf
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460	Auto-Data Volkswagen Arteon facelift	https://www.auto-data.net/en/volkswagen-arteon-model-2207
EU-BMW-M5-F90-SEDAN-PREFL-01	4966	1903	1473	Auto-Data BMW M5 F90	https://www.auto-data.net/en/bmw-m5-f90-generation-5548
EU-BMW-M5-F90-SEDAN-FACELIFT-01	4983	1903	1473	Auto-Data BMW M5 F90 LCI	https://www.auto-data.net/en/bmw-m5-f90-lci-facelift-2020-4.4-v8-600hp-xdrive-steptronic-40539
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1501-1600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.denso-am.eu/catalog/pv/127891?utm_source=chatgpt.com "TOYOTA HILUX 1984 - Search by vehicle parts - denso-am.eu"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1501-1600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1501-1600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1682 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（828 行）

