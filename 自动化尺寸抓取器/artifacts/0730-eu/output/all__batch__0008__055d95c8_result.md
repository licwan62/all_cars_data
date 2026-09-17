# 任务：all 第 701-800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0008__055d95c8


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 701-800 行

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
all 第 701-800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F20-HATCHBACK-5D-01	4329	1765	1421
EU-BMW-1-F20-HATCHBACK-5D-M140-01	4324	1765	1411
EU-BMW-1-F21-HATCHBACK-3D-01	4329	1765	1421
EU-BMW-1-F21-HATCHBACK-3D-M140-01	4324	1765	1411
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-7-E38-SEDAN-LWB-01	5124	1862	1425
EU-BMW-7-E38-SEDAN-SWB-01	4984	1862	1435
EU-BMW-7-E65-SEDAN-PREFL-01	5029	1902	1492
EU-BMW-7-G11-SEDAN-PREFL-01	5098	1902	1467
EU-BMW-7-G12-SEDAN-PREFL-01	5238	1902	1479
EU-BMW-X3-F25-FACELIFT-SUV-01	4657	1881	1661
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776
EU-CITROEN-C3-III-HATCHBACK-PREFL-01	3996	1749	1474
EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	4784	1916	1381
EU-KIA-OPTIMA-JF-SEDAN-01	4855	1860	1465
EU-KIA-OPTIMA-JF-SPORTSWAGON-01	4855	1860	1470
EU-KIA-OPTIMA-JF-SPORTSWAGON-GT-01	4855	1860	1460
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H1-01	5048	2070	2307
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L1H2-01	5048	2070	2500
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H2-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L2H3-01	5548	2070	2749
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H2-01	6198	2070	2488
EU-RENAULT-MASTER-III-X62-PHASE-II-VAN-L3H3-01	6198	2070	2744
EU-VOLVO-760-765-WAGON-FACELIFT-01	4790	1760	1435
EU-VOLVO-760-765-WAGON-PREFL-01	4800	1750	1435

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Volvo	V50	2.0 CDI	Kombi	Frontantrieb	Diesel	98	133	Dec 2003	Dec 2006	2024-03-01	122902
Volvo	S40 ii	2.0 CDI	Stufenheck	Frontantrieb	Diesel	98	133	Jul 2005	Dec 2006	2024-03-01	122903
Volvo	760	2.8	Kombi	Heckantrieb	Benzin	112	152	Sep 1986	Oct 1988	2024-03-01	122905
Volvo	V70 ii	2.4 CDI	Kombi	Frontantrieb	Diesel	90	122	Jul 2005	Dec 2008	2024-03-01	122906
Volvo	S40 ii	2.4 CDI	Stufenheck	Frontantrieb	Diesel	120	163	Mar 2007	Dec 2010	2024-03-01	122907
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	138	188	Sep 1977	Dec 1978	2024-03-01	122920
Renault	Grand scénic iii	1.6 E85	Großraumlimousine	Frontantrieb	Benzin/Ethanol	81	110	Feb 2009	Sep 2016	2024-05-01	122937
Renault	Scénic iii	1.6 16V Bifuel	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	81	110	Feb 2009	Sep 2016	2024-05-01	122938
Renault	Scénic iii	1.6 16V Bifuel	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	79	107	Apr 2012	Dec 2013	2024-03-01	122943
Renault	Grand scénic iii	1.6 16V Bifuel	Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	79	107	Apr 2012	Sep 2016	2024-05-01	122944
KIA	Optima	2.0 GDI Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	151	205	Sep 2016	Dec 2019	2024-03-01	122966
Citroën	C3 iii	1.2 VTI 82	Schrägheck	Frontantrieb	Benzin	60	82	Jul 2016	-	2025-06-01	122967
Citroën	C3 iii	1.2 THP 110	Schrägheck	Frontantrieb	Benzin	81	110	Jul 2016	-	2025-06-01	122968
Opel	Astra h family	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	81	110	Jan 2009	May 2014	2026-04-01	122969
Citroën	C3 iii	1.6 Bluehdi 75	Schrägheck	Frontantrieb	Diesel	55	75	Jul 2016	May 2018	2025-06-01	122970
Opel	Astra h family	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	92	125	Jan 2009	May 2014	2026-04-01	122972
Citroën	C3 iii	1.6 Bluehdi 100	Schrägheck	Frontantrieb	Diesel	73	99	Jul 2016	May 2018	2025-06-01	122973
Ford	Transit v363	2.0 Ecoblue 4X4	Pritsche/Fahrgestell	Allrad	Diesel	96	130	Jan 2017	-	2024-03-01	123031
Ford	Transit v363	2.0 Ecoblue 4X4	Pritsche/Fahrgestell	Allrad	Diesel	125	170	Jan 2017	Jun 2024	2024-11-01	123032
Ford	Transit v363	2.0 Ecoblue 4X4	Kasten	Allrad	Diesel	96	130	Jan 2017	-	2024-03-01	123043
Ford	Transit v363	2.0 Ecoblue 4X4	Kasten	Allrad	Diesel	125	170	Jan 2017	Jun 2024	2024-11-01	123044
Opel	Astra h family	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Jan 2009	May 2014	2026-04-01	123045
Opel	Astra h family	1.6	Stufenheck	Frontantrieb	Benzin	85	116	Jan 2009	May 2014	2024-03-01	123046
Opel	Astra h family	1.7 Cdti	Stufenheck	Frontantrieb	Diesel	92	125	Jan 2009	May 2014	2026-04-01	123047
Opel	Astra h family caravan	1.6	Kombi	Frontantrieb	Benzin	85	116	Jan 2009	May 2014	2026-04-01	123048
Opel	Astra h family caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	81	110	Jan 2009	May 2014	2026-04-01	123049
Opel	Astra h family caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	92	125	Jan 2009	May 2014	2026-04-01	123050
Infiniti	Qx30	2.0 AWD	SUV	Allrad	Benzin	155	211	Sep 2016	-	2024-03-01	123060
Audi	A5	2.0 Tfsi	Coupe	Frontantrieb	Benzin	185	252	Nov 2016	Feb 2020	2024-03-01	123095
Audi	A5	2.0 TDI Quattro	Coupe	Allrad	Diesel	140	190	Oct 2016	Dec 2019	2026-07-01	123096
Audi	A5	2.0 Tfsi	Coupe	Frontantrieb	Benzin	140	190	Sep 2016	Feb 2020	2026-07-01	123100
Audi	A5	3.0 TDI	Coupe	Frontantrieb	Diesel	160	218	Nov 2016	Aug 2018	2024-03-01	123107
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	320	435	Dec 2014	-	2024-03-01	123108
Audi	A5	2.0 Tfsi Quattro	Coupe	Allrad	Benzin	183	249	Jun 2016	Feb 2020	2024-03-01	123109
Audi	A5	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	185	252	Nov 2016	Feb 2020	2024-03-01	123111
Audi	A5	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	185	252	Sep 2016	-	2024-03-01	123112
Audi	A5	S5 Tfsi Quattro	Schrägheck	Allrad	Benzin	260	354	Sep 2016	-	2025-11-01	123113
Audi	A5	2.0 TDI	Schrägheck	Frontantrieb	Diesel	140	190	Sep 2016	Apr 2020	2026-07-01	123114
Audi	A5	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	140	190	Oct 2016	Feb 2020	2026-07-01	123115
Audi	A5	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	160	218	Sep 2016	Aug 2018	2026-07-01	123116
Audi	A5	2.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	183	249	Sep 2016	Feb 2020	2024-03-01	123117
Nissan	Nt400 cabstar	35.13	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	130	Sep 2016	-	2024-03-01	123145
Nissan	Nt400 cabstar	35.15, 45.15	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Sep 2016	-	2024-03-01	123146
BMW	1	135 I	Coupe	Heckantrieb	Benzin	240	326	Oct 2007	Oct 2013	2024-03-01	123155
BMW	3	335 I Xdrive	Stufenheck	Allrad	Benzin	240	326	May 2008	Oct 2011	2024-03-01	123156
BMW	3	335 XI	Stufenheck	Allrad	Benzin	240	326	Sep 2006	Jun 2008	2024-03-01	123157
Mini	Mini	Cooper SD	Schrägheck	Frontantrieb	Diesel	120	163	Jun 2014	-	2024-03-01	123158
BMW	3	320 D	Cabriolet	Heckantrieb	Diesel	147	200	Mar 2010	Oct 2013	2024-03-01	123159
BMW	3	320 D	Cabriolet	Heckantrieb	Diesel	145	197	Sep 2007	Feb 2010	2024-03-01	123160
BMW	3	320 D	Coupe	Heckantrieb	Diesel	147	200	Mar 2010	Jun 2013	2024-03-01	123161
BMW	3	320 D	Coupe	Heckantrieb	Diesel	145	197	Sep 2006	Feb 2010	2024-03-01	123162
BMW	3	320 D Xdrive	Coupe	Allrad	Diesel	147	200	Mar 2010	Jun 2013	2024-03-01	123163
BMW	3	320 D Xdrive	Coupe	Allrad	Diesel	145	197	Sep 2008	Feb 2010	2024-03-01	123165
BMW	3	320 D Xdrive	Coupe	Allrad	Diesel	120	163	Sep 2008	Jun 2013	2024-03-01	123166
BMW	3	323 I	Coupe	Heckantrieb	Benzin	140	190	Apr 2006	Feb 2012	2024-03-01	123168
BMW	3	335 I	Coupe	Heckantrieb	Benzin	240	326	Jun 2006	Jun 2013	2024-03-01	123171
BMW	3	335 I Xdrive	Coupe	Allrad	Benzin	240	326	Nov 2008	Jun 2013	2024-03-01	123175
BMW	3	335 XI	Coupe	Allrad	Benzin	240	326	Mar 2007	Feb 2010	2024-03-01	123176
Nissan	Primastar	1.9 DCI 80	Pritsche/Fahrgestell	Frontantrieb	Diesel	60	82	Jul 2002	Aug 2006	2024-03-01	123181
Nissan	Primastar	2.5 DCI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	99	135	Jul 2002	Aug 2006	2024-03-01	123182
BMW	3	320 D	Kombi	Heckantrieb	Diesel	147	200	Mar 2010	May 2012	2024-03-01	123184
BMW	3	320 D	Kombi	Heckantrieb	Diesel	145	197	Feb 2007	Feb 2010	2024-03-01	123185
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	147	200	Mar 2010	May 2012	2024-03-01	123187
BMW	3	320 D Xdrive	Kombi	Allrad	Diesel	145	197	Feb 2008	Feb 2010	2024-03-01	123188
BMW	3	320 I	Kombi	Heckantrieb	Benzin	120	163	Feb 2007	May 2012	2024-03-01	123190
BMW	3	335 XI	Kombi	Allrad	Benzin	240	326	Mar 2007	Aug 2008	2024-03-01	123191
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	147	200	Jun 2010	Jun 2014	2024-03-01	123192
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	147	200	Jan 2013	Jun 2014	2024-03-01	123193
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	100	136	Jan 2013	Jun 2014	2024-03-01	123194
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	100	136	Jan 2013	Jun 2014	2024-03-01	123195
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	155	211	Oct 2013	Oct 2016	2024-03-01	123196
BMW	5	520 D Xdrive	Stufenheck	Allrad	Diesel	155	211	Oct 2013	Oct 2016	2024-03-01	123197
BMW	5	520 D	Kombi	Heckantrieb	Diesel	155	211	Jul 2014	Feb 2017	2024-03-01	123198
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	155	211	Jul 2014	Feb 2017	2024-03-01	123199
BMW	5	520 D	Kombi	Heckantrieb	Diesel	147	200	Jun 2010	Jun 2014	2024-03-01	123200
BMW	5	520 D Xdrive	Kombi	Allrad	Diesel	147	200	Jul 2013	Jun 2014	2024-03-01	123201
BMW	7	730 D Xdrive	Stufenheck	Allrad	Diesel	155	211	Nov 2011	May 2015	2024-03-01	123202
BMW	X3	3.0 D	SUV	Allrad	Diesel	155	211	Sep 2005	Aug 2008	2024-03-01	123206
BMW	X5	Xdrive 30 D	SUV	Allrad	Diesel	210	286	Aug 2013	Jul 2018	2024-03-01	123211
Toyota	Highlander	3.5 AWD	SUV	Allrad	Benzin	183	249	Sep 2014	Nov 2016	2024-05-01	123224
Renault	Master iii	2.3 DCI 130 RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	96	130	Jul 2015	Dec 2020	2026-03-01	123227
Citroën	C3 ii	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	54	73	Jul 2010	Sep 2016	2024-07-01	123273
Toyota	Land cruiser prado	3.0 D-4d	Geländewagen geschlossen	Allrad	Diesel	150	204	Aug 2006	Jul 2009	2024-03-01	123308
Land Rover	Discovery v	3.0 TD6 4X4	SUV	Allrad	Diesel	190	258	Sep 2016	-	2024-03-01	123313
Land Rover	Discovery v	3.0 D 4X4	SUV	Allrad	Diesel	183	249	Sep 2016	-	2024-03-01	123314
VW	Golf ii van	1.8 I	Kasten/Schrägheck	Frontantrieb	Benzin	66	90	Aug 1987	Jul 1991	2024-03-01	123319
Land Rover	Discovery v	3.0 D 4X4	SUV	Allrad	Diesel	155	211	Sep 2016	-	2024-03-01	123321
Land Rover	Discovery v	3.0 Scv6 4X4	SUV	Allrad	Benzin	250	340	Sep 2016	-	2024-03-01	123323
VW	Golf iv van	1.9 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	May 2000	Sep 2002	2024-03-01	123324
VW	Golf iv van	1.9 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	96	130	Apr 2001	May 2004	2024-03-01	123325
Chevrolet	Express standard cargo van	5.3	Kasten	Heckantrieb	Benzin	224	305	Sep 2008	Dec 2009	2024-03-01	123332
BMW	5	530 I	Stufenheck	Heckantrieb	Benzin	185	252	Sep 2016	Jun 2020	2024-03-01	123333
BMW	5	530 I Xdrive	Stufenheck	Allrad	Benzin	185	252	Sep 2016	Jun 2020	2024-03-01	123334
Genesis	G90/g90l	3.3 T GDI	Stufenheck	Heckantrieb	Benzin	272	370	Sep 2016	-	2024-03-01	123335
Genesis	G90/g90l	3.3 T GDI AWD	Stufenheck	Allrad	Benzin	272	370	Sep 2016	-	2024-03-01	123336
Genesis	G90/g90l	5.0 GDI	Stufenheck	Heckantrieb	Benzin	304	413	Sep 2016	-	2024-03-01	123337
Genesis	G90/g90l	5.0 GDI AWD	Stufenheck	Allrad	Benzin	304	413	Feb 2016	-	2024-03-01	123338
BMW	5	540 I	Stufenheck	Heckantrieb	Benzin	250	340	Sep 2016	Jun 2020	2024-03-01	123340
BMW	5	540 I Xdrive	Stufenheck	Allrad	Benzin	250	340	Sep 2016	Jun 2020	2024-03-01	123342
BMW	5	M 550 I Xdrive	Stufenheck	Allrad	Benzin	340	462	Mar 2017	Jun 2019	2024-03-01	123344


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类完成首轮映射，覆盖全部 100 个输入 Ktype；相同外廓直接复用尺寸组，跨改款且三维变化的 Ktype 已拆分为稳定派生行。
* Scénic III、Grand Scénic III 的 Phase I、Phase II 已分别闭合；Phase III 因确定高度或不含后视镜宽度口径尚未闭合，暂保留 PENDING。([汽车数据网][1])
* 本轮新建了 A5 Sportback F5、BMW E92、F10、F11、F01、X3 E83、X5 F15、Genesis G90 标准轴距/长轴距等尺寸组；普通 BMW G30 与 M550i 因外廓尺寸不同分别建组。([汽车数据网][2])
* 已复用累计表中的 Volvo 760、Kia Optima JF、Citroën C3 III、Audi A5 F5 Coupé、Mustang S550、BMW E82/E90/E91/E93、MINI F56 等既有尺寸组，没有重复建组或改写既有尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* Ktype 映射行：120
* READY 映射：97
* PENDING 映射：23
* 已完全闭合 Ktype：77 / 100
* 含待定分支 Ktype：23 / 100
* 已确认并引用尺寸组：42

  * 本轮首次创建：29
  * 复用跨批次既有组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122902	122902	Wagon	V50	MW	5	EU-VOLVO-V50-MW-WAGON-01	HIGH		READY
122903	122903	Sedan	S40 II	MS	4	EU-VOLVO-S40-II-SEDAN-01	HIGH		READY
122905	122905	Wagon	760	765	5	EU-VOLVO-760-765-WAGON-FACELIFT-01	HIGH		READY
122906	122906	Wagon	V70 II facelift		5	EU-VOLVO-V70-II-WAGON-FACELIFT-01	HIGH		READY
122907	122907	Sedan	S40 II facelift	MS	4	EU-VOLVO-S40-II-SEDAN-01	HIGH	改款未改变本组三维外廓。	READY
122920	122920	Coupe	Corvette C3 facelift	C3	2	EU-CHEVROLET-CORVETTE-C3-COUPE-FACELIFT-01	HIGH		READY
122937_phase1	122937	MPV	Grand Scénic III Phase I		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-I-01	HIGH	Phase I外廓。	READY
122937_phase2	122937	MPV	Grand Scénic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-II-01	HIGH	Phase II外廓。	READY
122937_phase3	122937	MPV	Grand Scénic III Phase III		5		LOW	Phase III高度存在配置范围且宽度仅见折叠后视镜口径。	PENDING: Phase III高度和不含后视镜宽度未闭合
122938_phase1	122938	MPV	Scénic III Phase I		5	EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	HIGH	Phase I外廓。	READY
122938_phase2	122938	MPV	Scénic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-01	HIGH	Phase II外廓。	READY
122938_phase3	122938	MPV	Scénic III Phase III		5		LOW	Phase III直接规格页缺少确定高度。	PENDING: Phase III高度未闭合
122943_phase2	122943	MPV	Scénic III Phase II		5	EU-RENAULT-SCENIC-III-MPV-PHASE-II-01	HIGH	Phase II外廓。	READY
122943_phase3	122943	MPV	Scénic III Phase III		5		LOW	Phase III直接规格页缺少确定高度。	PENDING: Phase III高度未闭合
122944_phase2	122944	MPV	Grand Scénic III Phase II		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-II-01	HIGH	Phase II外廓。	READY
122944_phase3	122944	MPV	Grand Scénic III Phase III		5		LOW	Phase III高度存在配置范围且宽度仅见折叠后视镜口径。	PENDING: Phase III高度和不含后视镜宽度未闭合
122966	122966	Sedan	Optima JF	JF	4	EU-KIA-OPTIMA-JF-SEDAN-01	HIGH		READY
122967	122967	Hatchback	C3 III	B618	5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	MEDIUM	结束月未知；按该动力版本对应前期外廓。	READY
122968	122968	Hatchback	C3 III	B618	5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	MEDIUM	结束月未知；按该动力版本对应前期外廓。	READY
122969	122969	Sedan	Astra H Sedan	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH		READY
122970	122970	Hatchback	C3 III	B618	5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
122972	122972	Hatchback	Astra H facelift	L48	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-FACELIFT-01	HIGH		READY
122973	122973	Hatchback	C3 III	B618	5	EU-CITROEN-C3-III-HATCHBACK-PREFL-01	HIGH		READY
123031	123031	Pickup	Transit V363	V363			LOW	底盘驾驶室轴距及单双排未由输入确定。	PENDING: 底盘轴距和驾驶室分支未确定
123032	123032	Pickup	Transit V363	V363			LOW	底盘驾驶室轴距及单双排未由输入确定。	PENDING: 底盘轴距和驾驶室分支未确定
123043	123043	Van	Transit V363	V363			LOW	厢式车L/H轴距与车顶组合未由输入确定。	PENDING: 厢式车长度和车顶分支未确定
123044	123044	Van	Transit V363	V363			LOW	厢式车L/H轴距与车顶组合未由输入确定。	PENDING: 厢式车长度和车顶分支未确定
123045	123045	Hatchback	Astra H facelift	L48	5	EU-OPEL-ASTRA-H-HATCHBACK-5D-FACELIFT-01	HIGH		READY
123046	123046	Sedan	Astra H Sedan	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH		READY
123047	123047	Sedan	Astra H Sedan	L69	4	EU-OPEL-ASTRA-H-SEDAN-01	HIGH		READY
123048	123048	Wagon	Astra H Caravan facelift	L35	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH		READY
123049	123049	Wagon	Astra H Caravan facelift	L35	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH		READY
123050	123050	Wagon	Astra H Caravan facelift	L35	5	EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	HIGH		READY
123060	123060	SUV	QX30	H15	5	EU-INFINITI-QX30-H15-SUV-01	HIGH		READY
123095	123095	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
123096	123096	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
123100	123100	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
123107	123107	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
123108	123108	Coupe	Mustang S550	S550	2	EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	MEDIUM	结束月未知；435 hp版本对应改款前外廓。	READY
123109	123109	Coupe	A5 F5		2	EU-AUDI-A5-F5-COUPE-01	HIGH		READY
123111	123111	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
123112	123112	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	MEDIUM	结束月未知；按该动力版本对应F5改款前外廓。	READY
123113	123113	Hatchback	S5 Sportback F5		5		LOW	规格页高度为配置范围，无法落单一高度。	PENDING: S5 Sportback高度配置未确定
123114	123114	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
123115	123115	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
123116	123116	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
123117	123117	Hatchback	A5 Sportback F5		5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH		READY
123145	123145	Pickup	NT400 Cabstar	F24			LOW	轴距、驾驶室和吨位外廓分支未由输入唯一确定。	PENDING: 轴距和驾驶室分支未确定
123146	123146	Pickup	NT400 Cabstar	F24			LOW	轴距、驾驶室和吨位外廓分支未由输入唯一确定。	PENDING: 轴距和驾驶室分支未确定
123155	123155	Coupe	1 Series E82	E82	2	EU-BMW-1-E82-COUPE-01	HIGH		READY
123156_prefl	123156	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH	Ktype跨越E90改款边界。	READY
123156_facelift	123156	Sedan	3 Series E90 LCI	E90	4	EU-BMW-3-E90-SEDAN-FACELIFT-01	HIGH	Ktype跨越E90改款边界。	READY
123157	123157	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-PREFL-01	HIGH		READY
123158	123158	Hatchback	MINI F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	HIGH		READY
123159	123159	Convertible	3 Series E93 LCI	E93	2	EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	HIGH		READY
123160	123160	Convertible	3 Series E93	E93	2	EU-BMW-3-E93-CONVERTIBLE-PREFL-01	HIGH		READY
123161	123161	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
123162	123162	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH		READY
123163	123163	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH		READY
123165	123165	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH		READY
123166_prefl	123166	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	Ktype跨越E92改款边界。	READY
123166_facelift	123166	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	Ktype跨越E92改款边界。	READY
123168_prefl	123168	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	Ktype跨越E92改款边界。	READY
123168_facelift	123168	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	Ktype跨越E92改款边界。	READY
123171_prefl	123171	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	Ktype跨越E92改款边界。	READY
123171_facelift	123171	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	Ktype跨越E92改款边界。	READY
123175_prefl	123175	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH	Ktype跨越E92改款边界。	READY
123175_facelift	123175	Coupe	3 Series E92 LCI	E92	2	EU-BMW-3-E92-COUPE-FACELIFT-01	HIGH	Ktype跨越E92改款边界。	READY
123176	123176	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-PREFL-01	HIGH		READY
123181	123181	Pickup	Primastar I	X83			LOW	底盘驾驶室轴距及驾驶室形式未由输入确定。	PENDING: 底盘轴距和驾驶室分支未确定
123182	123182	Pickup	Primastar I	X83			LOW	底盘驾驶室轴距及驾驶室形式未由输入确定。	PENDING: 底盘轴距和驾驶室分支未确定
123184	123184	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
123185	123185	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH		READY
123187	123187	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH		READY
123188_prefl	123188	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	Ktype跨越E91改款边界。	READY
123188_facelift	123188	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	Ktype跨越E91改款边界。	READY
123190_prefl	123190	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH	Ktype跨越E91改款边界。	READY
123190_facelift	123190	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-E91-WAGON-FACELIFT-01	HIGH	Ktype跨越E91改款边界。	READY
123191	123191	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-PREFL-01	HIGH		READY
123192_prefl	123192	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	Ktype跨越F10改款边界。	READY
123192_facelift	123192	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	Ktype跨越F10改款边界。	READY
123193_prefl	123193	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	Ktype跨越F10改款边界。	READY
123193_facelift	123193	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	Ktype跨越F10改款边界。	READY
123194_prefl	123194	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	Ktype跨越F10改款边界。	READY
123194_facelift	123194	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	Ktype跨越F10改款边界。	READY
123195_prefl	123195	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-SEDAN-PREFL-01	HIGH	Ktype跨越F10改款边界。	READY
123195_facelift	123195	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH	Ktype跨越F10改款边界。	READY
123196	123196	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
123197	123197	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-F10-SEDAN-FACELIFT-01	HIGH		READY
123198	123198	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH	改款前后本组三维外廓一致。	READY
123199	123199	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH	改款前后本组三维外廓一致。	READY
123200	123200	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH	改款前后本组三维外廓一致。	READY
123201	123201	Wagon	5 Series F11	F11	5	EU-BMW-5-F11-WAGON-01	HIGH	改款前后本组三维外廓一致。	READY
123202_prefl	123202	Sedan	7 Series F01	F01	4	EU-BMW-7-F01-SEDAN-PREFL-01	MEDIUM	Ktype跨越F01改款边界；输入功率口径与目录标称不同。	READY
123202_facelift	123202	Sedan	7 Series F01 LCI	F01	4	EU-BMW-7-F01-SEDAN-FACELIFT-01	MEDIUM	Ktype跨越F01改款边界；输入功率口径与目录标称不同。	READY
123206	123206	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-01	HIGH	改款前后本组三维外廓一致。	READY
123211	123211	SUV	X5 F15	F15	5	EU-BMW-X5-F15-SUV-01	HIGH		READY
123224	123224	SUV	Highlander III	XU50	5	EU-TOYOTA-HIGHLANDER-XU50-SUV-PREFL-01	HIGH		READY
123227	123227	Pickup	Master III Phase II	X62			LOW	RWD底盘存在L2/L3及单双排分支，输入未唯一确定。	PENDING: 底盘轴距和驾驶室分支未确定
123273_phase1	123273	Hatchback	C3 II Phase I	A51	5	EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	HIGH	Ktype跨越2013改款边界。	READY
123273_phase2	123273	Hatchback	C3 II Phase II	A51	5	EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	HIGH	Ktype跨越2013改款边界。	READY
123308	123308	SUV	Land Cruiser Prado J120	J120			LOW	输入未确认三门/五门，且两种外廓不同。	PENDING: 三门和五门分支未确定
123313	123313	SUV	Discovery V	L462	5		LOW	现有规格仅明确折叠后视镜宽度，且高度存在悬架/配置差异。	PENDING: 不含后视镜宽度和确定高度未闭合
123314	123314	SUV	Discovery V	L462	5		LOW	现有规格仅明确折叠后视镜宽度，且高度存在悬架/配置差异。	PENDING: 不含后视镜宽度和确定高度未闭合
123319	123319	Van	Golf II Van	19E			LOW	商用封闭式车身门数与具体外廓分支未确认。	PENDING: Van门数和外廓分支未确定
123321	123321	SUV	Discovery V	L462	5		LOW	现有规格仅明确折叠后视镜宽度，且高度存在悬架/配置差异。	PENDING: 不含后视镜宽度和确定高度未闭合
123323	123323	SUV	Discovery V	L462	5		LOW	现有规格仅明确折叠后视镜宽度，且高度存在悬架/配置差异。	PENDING: 不含后视镜宽度和确定高度未闭合
123324	123324	Van	Golf IV Van	1J			LOW	商用封闭式车身门数与具体外廓分支未确认。	PENDING: Van门数和外廓分支未确定
123325	123325	Van	Golf IV Van	1J			LOW	商用封闭式车身门数与具体外廓分支未确认。	PENDING: Van门数和外廓分支未确定
123332	123332	Van	Express I facelift	GMT610			LOW	Standard cargo van的轴距、载重级别与车顶高度未唯一确定。	PENDING: 轴距和车顶分支未确定
123333	123333	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH		READY
123334	123334	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH		READY
123335	123335	Sedan	G90/EQ900 I	HI	4	EU-GENESIS-G90-HI-SEDAN-SWB-01	HIGH	3.3T仅对应标准轴距外廓。	READY
123336	123336	Sedan	G90/EQ900 I	HI	4	EU-GENESIS-G90-HI-SEDAN-SWB-01	HIGH	3.3T仅对应标准轴距外廓。	READY
123337	123337	Sedan	G90/EQ900 I	HI	4	EU-GENESIS-G90-HI-SEDAN-SWB-01	MEDIUM	G90L仅见5.0 AWD；RWD记录映射标准轴距外廓。	READY
123338_swb	123338	Sedan	G90/EQ900 I	HI	4	EU-GENESIS-G90-HI-SEDAN-SWB-01	HIGH	5.0 AWD覆盖标准轴距分支。	READY
123338_lwb	123338	Sedan	G90/EQ900L I	HI	4	EU-GENESIS-G90-HI-SEDAN-LWB-01	HIGH	5.0 AWD覆盖长轴距分支。	READY
123340	123340	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH		READY
123342	123342	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-01	HIGH		READY
123344	123344	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-M550I-01	HIGH	M550i外廓独立于普通G30。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V50-MW-WAGON-01	4514	1770	1452	Auto-Data.net	https://www.auto-data.net/en/volvo-v50-2.0-d-136hp-9578
EU-VOLVO-S40-II-SEDAN-01	4476	1770	1454	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/volvo-s40-ii-generation-1971;https://www.auto-data.net/en/volvo-s40-ii-facelift-2007-generation-5009
EU-VOLVO-V70-II-WAGON-FACELIFT-01	4710	1804	1465	Auto-Data.net	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4d-126hp-42645
EU-CHEVROLET-CORVETTE-C3-COUPE-FACELIFT-01	4704	1753	1219	Auto-Data.net	https://www.auto-data.net/en/chevrolet-corvette-coupe-c3-facelift-1978-5.7-v8-190hp-42574
EU-RENAULT-SCENIC-III-MPV-PHASE-I-01	4343	1845	1624	Auto-Data.net	https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.6-16v-110hp-ethanol-39512
EU-RENAULT-SCENIC-III-MPV-PHASE-II-01	4366	1845	1640	Auto-Data.net	https://www.auto-data.net/en/renault-scenic-iii-phase-ii-collection-2012-1.6-16v-110hp-17458
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-I-01	4560	1845	1675	Auto-Data.net	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-i-1.6-16v-110hp-ethanol-39521
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-II-01	4573	1845	1645	Auto-Data.net	https://www.auto-data.net/en/renault-grand-scenic-iii-phase-ii-collection-2012-1.6-dci-energy-130hp-start-stop-17461
EU-OPEL-ASTRA-H-SEDAN-01	4587	1753	1458	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-sedan-1.7-cdti-110hp-16952
EU-OPEL-ASTRA-H-HATCHBACK-5D-FACELIFT-01	4249	1753	1460	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.7-cdti-ecotec-125hp-16954
EU-OPEL-ASTRA-H-WAGON-FACELIFT-01	4515	1753	1500	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.7-cdti-ecotec-125hp-16955
EU-INFINITI-QX30-H15-SUV-01	4425	1815	1530	Auto-Data.net	https://www.auto-data.net/en/infiniti-qx30-2.0t-211hp-awd-dct-32074
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Auto-Data.net	https://www.auto-data.net/en/audi-a5-sportback-f5-2.0-tfsi-252hp-s-tronic-26238
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-320d-177hp-9951
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-320d-184hp-17231
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-sedan-f10-520d-184hp-17268
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-520d-184hp-28226
EU-BMW-5-F11-WAGON-01	4907	1860	1462	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-touring-f11-520d-184hp-17283;https://www.auto-data.net/en/bmw-5-series-touring-f11-lci-facelift-2013-520d-184hp-28033
EU-BMW-7-F01-SEDAN-PREFL-01	5072	1902	1479	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-f01-generation-1983
EU-BMW-7-F01-SEDAN-FACELIFT-01	5079	1902	1471	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-f01-lci-facelift-2012-730d-258hp-xdrive-steptronic-17770
EU-BMW-X3-E83-SUV-01	4569	1853	1674	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/bmw-x3-e83-3.0d-218hp-33624;https://www.auto-data.net/en/bmw-x3-e83-facelift-2006-3.0d-218hp-9783
EU-BMW-X5-F15-SUV-01	4886	1938	1762	Auto-Data.net	https://www.auto-data.net/en/bmw-x5-f15-30d-258hp-xdrive-steptronic-18605
EU-TOYOTA-HIGHLANDER-XU50-SUV-PREFL-01	4865	1925	1730	Auto-Data.net	https://www.auto-data.net/en/toyota-highlander-iii-3.5-v6-249hp-4x4-automatic-30508
EU-CITROEN-C3-II-HATCHBACK-PHASE-I-01	3941	1728	1524	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-ii-phase-i-2009-1.4i-73hp-15082
EU-CITROEN-C3-II-HATCHBACK-PHASE-II-01	3941	1728	1538	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-ii-phase-ii-2013-1.2-puretech-82hp-21039
EU-BMW-5-G30-SEDAN-01	4936	1868	1466	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-sedan-g30-530i-252hp-steptronic-26321
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467	Auto-Data.net	https://www.auto-data.net/en/bmw-5-series-sedan-g30-m550i-462hp-xdrive-steptronic-27327
EU-GENESIS-G90-HI-SEDAN-SWB-01	5205	1915	1495	Auto-Data.net	https://www.auto-data.net/en/genesis-g90-eq900-i-3.3t-gdi-v6-370hp-automatic-25230
EU-GENESIS-G90-HI-SEDAN-LWB-01	5495	1915	1505	Auto-Data.net	https://www.auto-data.net/en/genesis-g90-eq900l-i-5.0-gdi-v8-425hp-awd-automatic-25144
```

## 下一步优先处理

1. 闭合 Scénic III／Grand Scénic III Phase III 的确定高度与车身宽度口径，并确认 S5 Sportback F5 的单一高度配置。
2. 按车型族集中拆分 Transit V363、NT400 Cabstar、Primastar X83、Master X62 与 Chevrolet Express 的轴距、驾驶室、车顶和载重分支。
3. 确认 Prado J120 三门/五门边界、Golf II/IV Van 的商用车身分支，以及 Discovery V 的不含后视镜宽度和确定高度。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.6-16v-110hp-16740 "https://www.auto-data.net/en/renault-scenic-iii-phase-i-1.6-16v-110hp-16740"
[2]: https://www.auto-data.net/en/audi-a5-sportback-f5-2.0-tfsi-252hp-s-tronic-26238 "https://www.auto-data.net/en/audi-a5-sportback-f5-2.0-tfsi-252hp-s-tronic-26238"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合 Scénic III／Grand Scénic III Phase III，分别建立标准版与 Grand 版尺寸组，宽度均采用不含后视镜口径。([汽车目录][1])
* 已闭合 S5 Sportback F5 的 354 hp 改款前外廓，并独立于普通 A5 Sportback 建组。([汽车目录][2])
* `123227` 已按缓存中的 Master III Phase II RWD 底盘尺寸组拆分为单排/双排及 L2/L3 四条 READY 映射，未重复输出既有尺寸组。
* 已闭合 Discovery V L462 的柴油与汽油 Ktype，共用同一尺寸组。([汽车目录][3])
* 已闭合 Chevrolet Express 标准轴距 Cargo Van；英寸规格已统一换算为毫米。([Edmunds][4])

## 当前批次进度

* 输入 Ktype：100
* Ktype 映射行：123
* READY 映射：111
* PENDING 映射：12
* 已完全闭合 Ktype：88 / 100
* 已确认并引用尺寸组：51

  * 本批次累计新建：34
  * 跨批次缓存复用：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
122937_phase3	122937	MPV	Grand Scénic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-III-01	HIGH	Phase III外廓。	READY
122938_phase3	122938	MPV	Scénic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-III-01	HIGH	Phase III外廓。	READY
122943_phase3	122943	MPV	Scénic III Phase III		5	EU-RENAULT-SCENIC-III-MPV-PHASE-III-01	HIGH	Phase III外廓。	READY
122944_phase3	122944	MPV	Grand Scénic III Phase III		5	EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-III-01	HIGH	Phase III外廓。	READY
123113	123113	Hatchback	S5 Sportback F5		5	EU-AUDI-S5-F5-SPORTBACK-01	HIGH		READY
123227_scab_l2	123227	Pickup	Master III Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	HIGH	单排L2底盘外廓。	READY
123227_scab_l3	123227	Pickup	Master III Phase II	X62	2	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	HIGH	单排L3底盘外廓。	READY
123227_dcab_l2	123227	Pickup	Master III Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	HIGH	双排L2底盘外廓。	READY
123227_dcab_l3	123227	Pickup	Master III Phase II	X62	4	EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	HIGH	双排L3底盘外廓。	READY
123313	123313	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
123314	123314	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
123321	123321	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
123323	123323	SUV	Discovery V	L462	5	EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	HIGH		READY
123332	123332	Van	Express I facelift	GMT610		EU-CHEVROLET-EXPRESS-GMT610-CARGO-SWB-01	HIGH	标准轴距货运外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-GRAND-SCENIC-III-MPV-PHASE-III-01	4573	1845	1645	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2982305/renault_grand_scenic_1_6_16v_110_5_passenger.html
EU-RENAULT-SCENIC-III-MPV-PHASE-III-01	4366	1845	1640	Automobile-Catalog	https://www.automobile-catalog.com/car/2013/2982140/renault_scenic_1_6_16v_110.html
EU-AUDI-S5-F5-SPORTBACK-01	4752	1843	1384	Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2503370/audi_s5_sportback.html
EU-LAND-ROVER-DISCOVERY-V-L462-SUV-01	4970	2000	1846	Automobile-Catalog;Automobile-Catalog	https://www.automobile-catalog.com/car/2017/2521460/land-rover_discovery_tdv6_4wd.html;https://www.automobile-catalog.com/car/2017/2521475/land-rover_discovery_si6_4wd.html
EU-CHEVROLET-EXPRESS-GMT610-CARGO-SWB-01	5692	2017	2073	Edmunds	https://www.edmunds.com/chevrolet/express-cargo/2009/st-101068006/features-specs/
```

## 下一步优先处理

1. 集中拆分 Ford Transit V363 4×4 底盘与厢式车的轴距、单双排和车顶分支。
2. 闭合 Nissan NT400 Cabstar 与 Primastar 底盘的轴距及驾驶室分支。
3. 处理 Prado J120 三门/五门，以及 Golf II Van、Golf IV Van 的商用车身边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2013/2982140/renault_scenic_1_6_16v_110.html?utm_source=chatgpt.com "2013 Renault Scenic 1.6 16V 110 Specs Review (81 kW / 110 PS / 109 hp) (since June 2013 for Europe )"
[2]: https://www.automobile-catalog.com/car/2017/2503370/audi_s5_sportback.html?utm_source=chatgpt.com "2017 Audi S5 Sportback Specs Review (260 kW / 354 PS / ..."
[3]: https://www.automobile-catalog.com/car/2017/2521475/land-rover_discovery_si6_4wd.html?utm_source=chatgpt.com "2017 Land-Rover Discovery Si6 340 4WD Specs Review (250 kW / 340 PS / 335 hp) (since Spring 2017 for Asia )"
[4]: https://www.edmunds.com/chevrolet/express-cargo/2009/st-101068006/features-specs/ "Used 2009 Chevrolet Express Cargo 1500 Specs & Features | Edmunds"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* NT400 Cabstar 已按官方车型可用性拆分：`35.13` 覆盖单排 SWB/MWB/LWB；`35.15` 为单排 LWB；`45.15` 覆盖单排 MWB/LWB。相同的 35 系列 LWB 外廓复用同一尺寸组。([日产][1])
* Prado Ktype `123308` 已确认对应五门 `KDJ120`，不再保留三门候选分支。([meyermotoren.de][2])
* Golf IV Van 两个 Ktype 已确认均为三门封闭式商用车身；因对应配置的确定车高不同，分别建立低车高和高车高尺寸组。([Alkatrészek][3])

## 当前批次进度

* 输入 Ktype：100
* Ktype 映射行：127
* READY 映射：120
* PENDING 映射：7
* 已完全闭合 Ktype：93 / 100
* 已确认并引用尺寸组：59

  * 本批次累计新建：42
  * 跨批次缓存复用：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123145_swb	123145	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-SWB-01	HIGH	单排短轴底盘外廓。	READY
123145_mwb	123145	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-MWB-01	HIGH	单排中轴底盘外廓。	READY
123145_lwb	123145	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-LWB-01	HIGH	单排长轴底盘外廓。	READY
123146_35t_lwb	123146	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-LWB-01	HIGH	35.15单排长轴底盘外廓。	READY
123146_45t_mwb	123146	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-45T-MWB-01	HIGH	45.15单排中轴底盘外廓。	READY
123146_45t_lwb	123146	Pickup	NT400 Cabstar	F24	2	EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-45T-LWB-01	HIGH	45.15单排长轴底盘外廓。	READY
123308	123308	SUV	Land Cruiser Prado J120	KDJ120	5	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	HIGH	五门KDJ120外廓。	READY
123324	123324	Van	Golf IV Van	1J1	3	EU-VW-GOLF-IV-1J1-VAN-3D-LOW-01	MEDIUM	三门封闭式商用车身，低车高外廓。	READY
123325	123325	Van	Golf IV Van	1J1	3	EU-VW-GOLF-IV-1J1-VAN-3D-HIGH-01	MEDIUM	三门封闭式商用车身，高车高外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-SWB-01	6183	1848	2093	Nissan NT400 Cabstar official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf
EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-MWB-01	6883	1848	2093	Nissan NT400 Cabstar official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf
EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-LWB-01	7683	1848	2093	Nissan NT400 Cabstar official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf
EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-45T-MWB-01	6883	1848	2110	Nissan NT400 Cabstar official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf
EU-NISSAN-NT400-CABSTAR-F24-CHASSIS-SCAB-45T-LWB-01	7683	1848	2110	Nissan NT400 Cabstar official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1865	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-prado-j120-3.0-d-4d-173hp-4wd-3697
EU-VW-GOLF-IV-1J1-VAN-3D-LOW-01	4149	1735	1439	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-90hp-8673
EU-VW-GOLF-IV-1J1-VAN-3D-HIGH-01	4149	1735	1444	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-130hp-8671
```

## 下一步优先处理

1. 集中闭合 Transit V363 的两个底盘 Ktype 与两个厢式车 Ktype，拆分确定的轴距、驾驶室和车顶分支。
2. 闭合 Primastar X83 两个底盘 Ktype 的单排/双排及轴距边界。
3. 最后确认 Golf II Van Ktype `123319` 在大保险杠改款前后的商用外廓边界。

推进信号：CONTINUE

[1]: https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf "https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NT400_UK.pdf"
[2]: https://www.meyermotoren.de/en/fahrzeuge/123308/toyota/land_cruiser_prado_j12_/3_0_d-4d_kdj120_123308 "https://www.meyermotoren.de/en/fahrzeuge/123308/toyota/land_cruiser_prado_j12_/3_0_d-4d_kdj120_123308"
[3]: https://alkatreszek.hu/termekek/karosszeria/javito_lemez/vw/golf/golf_iv_van_1j1_1997_10_2004_05 "https://alkatreszek.hu/termekek/karosszeria/javito_lemez/vw/golf/golf_iv_van_1j1_1997_10_2004_05"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Ford Transit V363 4×4 底盘：两个 Ktype 均拆分为单排 L2、L3 AWD 分支，并复用相同的两个尺寸组。Ford 官方资料确认 AWD 适用于对应 L2/L3 350 系列底盘。([福特爱尔兰][1])
* 已闭合 Transit V363 4×4 厢式车：两个动力 Ktype 均拆分为 L2H2、L2H3、L3H2、L3H3 四种外廓；高度按官方表中的最大量产外部高度落盘。([福特英国][2])
* 已闭合 Golf II Van `123319`，确认为三门封闭式商用车身；三维为 `3985 × 1665 × 1415 mm`，宽度为不含后视镜口径。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* Ktype 映射行：135
* READY 映射：133
* PENDING 映射：2
* 已完全闭合 Ktype：98 / 100
* 已确认并引用尺寸组：66

  * 本批次累计新建：49
  * 跨批次缓存复用：17
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
123031_scab_l2	123031	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L2-AWD-01	HIGH	单排L2 AWD底盘外廓。	READY
123031_scab_l3	123031	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L3-AWD-01	HIGH	单排L3 AWD底盘外廓。	READY
123032_scab_l2	123032	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L2-AWD-01	HIGH	单排L2 AWD底盘外廓。	READY
123032_scab_l3	123032	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L3-AWD-01	HIGH	单排L3 AWD底盘外廓。	READY
123043_l2h2	123043	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-AWD-01	HIGH	L2H2 AWD厢式外廓。	READY
123043_l2h3	123043	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-AWD-01	HIGH	L2H3 AWD厢式外廓。	READY
123043_l3h2	123043	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-AWD-01	HIGH	L3H2 AWD厢式外廓。	READY
123043_l3h3	123043	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-AWD-01	HIGH	L3H3 AWD厢式外廓。	READY
123044_l2h2	123044	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-AWD-01	HIGH	L2H2 AWD厢式外廓。	READY
123044_l2h3	123044	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-AWD-01	HIGH	L2H3 AWD厢式外廓。	READY
123044_l3h2	123044	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-AWD-01	HIGH	L3H2 AWD厢式外廓。	READY
123044_l3h3	123044	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-AWD-01	HIGH	L3H3 AWD厢式外廓。	READY
123319	123319	Van	Golf II	19E	3	EU-VW-GOLF-II-19E-VAN-3D-01	MEDIUM	三门封闭式商用车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L2-AWD-01	5572	2052	2210	Ford Transit Chassis Cab official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_chassis.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SCAB-L3-AWD-01	6022	2052	2202	Ford Transit Chassis Cab official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_chassis.pdf
EU-FORD-TRANSIT-V363-VAN-L2H2-AWD-01	5531	2059	2534	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L2H3-AWD-01	5531	2059	2771	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-AWD-01	5981	2059	2533	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-AWD-01	5981	2059	2769	Ford Transit Van official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-VW-GOLF-II-19E-VAN-3D-01	3985	1665	1415	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/41450/volkswagen_golf_1_8_gl.html
```

## 下一步优先处理

1. 仅剩 Nissan Primastar X83 的 `123181`、`123182`：确认平台底盘的 SWB/LWB 可用性，以及未安装后部改装车厢时的完整外部长度和高度；现有资料主要支持厢式车尺寸，尚不足以直接作为平台底盘尺寸事实落盘。

推进信号：CONTINUE

[1]: https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_transit_chassis.pdf?utm_source=chatgpt.com "TRANSIT CHASSIS CABS"
[2]: https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf?utm_source=chatgpt.com "TRANSIT"
[3]: https://www.automobile-catalog.com/car/1988/41450/volkswagen_golf_1_8_gl.html?utm_source=chatgpt.com "1988 Volkswagen Golf 1.8 GL Specs Review (66 kW / 90 PS / 89 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（542 行）
- 累计尺寸组：dimension_groups_final.tsv（283 行）

