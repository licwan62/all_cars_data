# 任务：all 第 1301-1400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0014__37414895


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1301-1400 行

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
all 第 1301-1400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-33-907-SPORTWAGON-4X4-01	4200	1614	1375
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436
EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	4120	1630	1290
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	4540	1915	1250
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-340-SEDAN-01	4600	1765	1630
EU-DACIA-LOGAN-I-MCV-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1539
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4346	1733	1517
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	4482	1923	1308
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618
EU-KIA-SOUL-II-HATCHBACK-NO-ROOF-BARS-01	4140	1800	1593
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-GTR-01	4551	2007	1284
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-01	4544	1939	1259
EU-MERCEDES-BENZ-AMG-GT-I-R190-ROADSTER-GTC-01	4551	2007	1260
EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	4695	1810	1710
EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	4655	1800	1680
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455
EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-3D-01	3973	1739	1460
EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-5D-01	3973	1739	1460
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mitsubishi	Outlander iii	3.0 4WD	SUV	Allrad	Benzin	169	230	Mar 2014	Dec 2022	2025-06-01	126682
Mitsubishi	Outlander iii	3.0 4WD	SUV	Allrad	Benzin	165	224	Oct 2012	Dec 2022	2025-06-01	126684
Peugeot	208 i	1.2 VTI 68 / Puretech 68	Schrägheck	Frontantrieb	Benzin	50	68	Aug 2016	Dec 2019	2024-03-01	126685
Alfa Romeo	Giulia	2.2 D Q4	Stufenheck	Allrad	Diesel	132	180	Apr 2017	-	2024-03-01	126711
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	110	150	Feb 2012	Feb 2017	2024-03-01	126724
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	110	150	Feb 2012	Feb 2017	2024-03-01	126725
Jaguar	Xe	2.0 D AWD	Stufenheck	Allrad	Diesel	177	241	Feb 2017	-	2024-03-01	126745
Jaguar	Xe	2	Stufenheck	Heckantrieb	Benzin	184	250	Feb 2017	-	2024-03-01	126746
Jaguar	Xe	2.0 AWD	Stufenheck	Allrad	Benzin	184	250	Feb 2017	-	2024-03-01	126747
Jaguar	Xe	3.0 S	Stufenheck	Heckantrieb	Benzin	280	381	Feb 2017	-	2024-03-01	126748
Jaguar	Xf ii	2.0 D	Stufenheck	Heckantrieb	Diesel	177	241	Mar 2017	-	2024-03-01	126749
Jaguar	Xf ii	2.0 D AWD	Stufenheck	Allrad	Diesel	177	241	Mar 2017	-	2024-03-01	126750
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	147	200	Mar 2017	-	2024-03-01	126751
Jaguar	Xf ii	2	Stufenheck	Heckantrieb	Benzin	184	250	Mar 2017	-	2024-03-01	126752
Jaguar	Xf ii	2.0 AWD	Stufenheck	Allrad	Benzin	184	250	Mar 2017	-	2024-03-01	126753
Mercedes-benz	Amg gt	GT	Coupe	Heckantrieb	Benzin	350	476	Jan 2017	Dec 2021	2024-03-01	126755
Mercedes-benz	Amg gt	GT S	Coupe	Heckantrieb	Benzin	384	522	Jan 2017	May 2020	2024-03-01	126756
Mercedes-benz	E-Klasse	E 220 D 4-matic	Coupe	Allrad	Diesel	143	194	Mar 2017	-	2024-03-01	126757
Mazda	Rx-8	1.3	Coupe	Heckantrieb	Benzin	151	205	Apr 2008	Jun 2012	2024-03-01	126774
Honda	Jazz iv	1.5	Schrägheck	Frontantrieb	Benzin	96	130	Sep 2017	-	2024-03-01	126827
VW	Arteon	2.0 TSI 4motion	Schrägheck	Allrad	Benzin	206	280	Apr 2017	-	2024-03-01	126829
VW	Arteon	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	176	240	Mar 2017	Jul 2020	2024-03-01	126831
VW	Golf vii	1.5 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Apr 2017	Aug 2020	2024-03-01	126840
VW	Golf vii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Apr 2017	Aug 2020	2024-03-01	126844
Audi	A3	1.6 TDI	Cabriolet	Frontantrieb	Diesel	85	115	Apr 2017	Oct 2020	2024-03-01	126845
Ssangyong	Tivoli	1.6 XDI 160	SUV	Frontantrieb	Diesel	83	113	Apr 2015	-	2024-03-01	126863
Ford	Mondeo iv	2.2 Tdci	Stufenheck	Frontantrieb	Diesel	147	200	Oct 2010	Jan 2015	2024-03-01	126874
Audi	A3	RS3 Quattro	Schrägheck	Allrad	Benzin	294	400	Apr 2017	Oct 2020	2024-03-01	126875
Audi	A3	RS3 Quattro	Stufenheck	Allrad	Benzin	294	400	Apr 2017	Oct 2020	2024-03-01	126876
Ford	Mondeo iv	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	100	136	Aug 2008	Dec 2014	2024-03-01	126877
Audi	A5	RS5 Tfsi Quattro	Coupe	Allrad	Benzin	331	450	Apr 2017	-	2025-11-01	126881
Hyundai	I30	1.4 MPI	Schrägheck	Frontantrieb	Benzin	74	100	Nov 2016	Dec 2020	2024-07-01	126883
Honda	Civic x	1.5 Vtec	Stufenheck	Frontantrieb	Benzin	134	182	Aug 2016	Dec 2022	2024-03-01	126886
Jaguar	F-Type	2.0 TI4	Coupe	Heckantrieb	Benzin	221	300	Jul 2017	-	2024-03-01	126887
Jaguar	F-Type	2.0 TI4	Cabriolet	Heckantrieb	Benzin	221	300	Jul 2017	-	2024-03-01	126888
Toyota	Yaris	1.5	Schrägheck	Frontantrieb	Benzin	82	112	Mar 2017	Jun 2020	2024-05-01	126889
Porsche	Panamera	3.0 4	Kombi	Allrad	Benzin	243	330	May 2017	Dec 2020	2026-02-01	126894
Porsche	Panamera	2.9 4 E-hybrid	Kombi	Allrad	Benzin/Elektro	340	462	May 2017	Dec 2023	2024-08-01	126896
Porsche	Panamera	2.9 4S	Kombi	Allrad	Benzin	324	440	May 2017	Dec 2023	2024-08-01	126897
Porsche	Panamera	4.0 Turbo	Kombi	Allrad	Benzin	404	550	May 2017	Dec 2023	2024-08-01	126898
Porsche	Panamera	4.0 S 4 Diesel	Kombi	Allrad	Diesel	310	422	May 2017	Dec 2023	2024-08-01	126899
Porsche	Panamera	4.0 Turbo S E-hybrid	Schrägheck	Allrad	Benzin/Elektro	500	680	May 2017	Dec 2023	2024-08-01	126908
Nissan	Juke	1.6 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	85	116	Jan 2012	Dec 2019	2024-03-01	126913
Suzuki	Swift v	1	Schrägheck	Frontantrieb	Benzin	82	111	Apr 2017	-	2025-06-01	126919
Suzuki	Swift v	1.0 Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	82	111	Apr 2017	-	2025-06-01	126920
Suzuki	Swift v	1.2	Schrägheck	Frontantrieb	Benzin	66	90	Apr 2017	-	2024-03-01	126921
Suzuki	Swift v	1.2 Shvs	Schrägheck	Frontantrieb	Benzin/Elektro	66	90	Apr 2017	-	2024-03-01	126922
Suzuki	Swift v	1.2 Shvs Allgrip	Schrägheck	Allrad	Benzin/Elektro	66	90	Apr 2017	-	2024-03-01	126923
Suzuki	Swift v	1.2 Allgrip	Schrägheck	Allrad	Benzin	66	90	Apr 2017	-	2024-03-01	126924
Jeep	Grand cherokee iv	5.7 4X4	SUV	Allrad	Benzin	268	364	Jan 2011	-	2024-03-01	126953
Alfa Romeo	Stelvio	2.2 D	SUV	Heckantrieb	Diesel	132	180	Dec 2016	-	2024-03-01	126958
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	148	201	Dec 2016	-	2024-03-01	126959
Nissan	Micra v	1	Schrägheck	Frontantrieb	Benzin	52	71	Dec 2016	-	2024-03-01	126960
Aston Martin	Vanquish	6	Cabriolet	Heckantrieb	Benzin	424	576	May 2014	-	2025-11-01	126963
Opel	Ampera-E	Ev150	Schrägheck	Frontantrieb	Elektro	150	204	May 2017	Mar 2019	2024-03-01	126998
Citroën	C4 ii	1.6	Stufenheck	Frontantrieb	Benzin	88	120	Jan 2013	-	2024-03-01	127022
VW	Arteon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	110	150	Mar 2017	-	2024-03-01	127056
Mazda	Cx-5	2	SUV	Frontantrieb	Benzin	121	165	May 2017	-	2024-03-01	127057
Mazda	Cx-5	2.0 AWD	SUV	Allrad	Benzin	118	160	May 2017	-	2024-03-01	127058
Mazda	Cx-5	2.5 AWD	SUV	Allrad	Benzin	143	194	May 2017	-	2024-03-01	127059
Mazda	Cx-5	2.2 D	SUV	Frontantrieb	Diesel	110	150	May 2017	Dec 2024	2026-03-01	127060
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	110	150	May 2017	Dec 2024	2026-03-01	127061
Mazda	Cx-5	2.2 D AWD	SUV	Allrad	Diesel	129	175	May 2017	Feb 2018	2024-03-01	127062
KIA	Picanto iii	1	Schrägheck	Frontantrieb	Benzin	49	67	Mar 2017	-	2024-03-01	127065
KIA	Picanto iii	1.2	Schrägheck	Frontantrieb	Benzin	62	84	Mar 2017	-	2024-03-01	127066
KIA	Soul ii	EV Electric	Schrägheck	Frontantrieb	Elektro	26	36	Mar 2017	Nov 2018	2025-11-01	127078
Renault	Koleos ii	1.6 DCI 130	SUV	Frontantrieb	Diesel	96	130	Apr 2016	-	2024-03-01	127084
Renault	Koleos ii	2.0 DCI 175 4WD	SUV	Allrad	Diesel	130	177	Apr 2016	-	2024-03-01	127085
Lotus	Exige	3.5 380	Coupe	Heckantrieb	Benzin	280	380	Nov 2016	-	2024-03-01	127092
BMW	3	M3 2.3	Cabriolet	Heckantrieb	Benzin	147	200	Jun 1988	Jul 1989	2024-03-01	127095
Alfa Romeo	Spider	2	Cabriolet	Heckantrieb	Benzin	89	120	Sep 1989	Dec 1990	2024-03-01	127108
Aston Martin	Vantage	4.3	Cabriolet	Heckantrieb	Benzin	298	405	Jan 2008	Dec 2010	2024-03-01	127111
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	243	330	Jan 1991	Dec 1992	2024-03-01	127112
Toyota	Land cruiser prado	4.0 V6 Vvt-i	Geländewagen geschlossen	Allrad	Benzin	207	282	Jan 2003	Jul 2009	2024-03-01	127122
Dacia	Logan	1.0 SCE 75	Stufenheck	Frontantrieb	Benzin	54	73	Jan 2017	-	2024-03-01	127127
Mazda	Cx-9	2.5 T AWD	SUV	Allrad	Benzin	170	231	Jun 2016	-	2024-03-01	127129
Subaru	Impreza	2.0 I AWD	Schrägheck	Allrad	Benzin	115	156	Oct 2016	-	2024-03-01	127130
KIA	Sportage iii	2.0 Cvvt	SUV	Frontantrieb	Benzin	113	154	Nov 2014	Dec 2015	2024-03-01	127157
Alfa Romeo	33	1.3	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1983	Jun 1990	2024-03-01	127183
Alfa Romeo	Spider	1600	Cabriolet	Heckantrieb	Benzin	75	102	Jan 1980	Dec 1989	2024-03-01	127184
Alfa Romeo	Spider	2000	Cabriolet	Heckantrieb	Benzin	94	128	Jan 1975	Dec 1986	2024-03-01	127185
Alfa Romeo	Alfasud	1.3	Coupe	Frontantrieb	Benzin	58	79	May 1978	Dec 1979	2024-03-01	127188
Mclaren	720s	4	Coupe	Heckantrieb	Benzin	527	720	Mar 2017	-	2024-03-01	127199
Honda	Nsx ii	3.5 Hybrid	Coupe	Allrad	Benzin/Elektro	427	581	Jun 2016	-	2024-03-01	127200
Renault	Trafic iii	1.6 DCI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Jun 2014	-	2024-03-01	127205
Renault	Trafic iii	1.6 DCI 140	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Jun 2014	-	2024-03-01	127206
Seat	Ibiza v	1.0 MPI	Schrägheck	Frontantrieb	Benzin	55	75	Jan 2017	-	2025-12-01	127208
Seat	Ibiza v	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Jan 2017	-	2024-03-01	127209
Seat	Ibiza v	1.0 TSI	Schrägheck	Frontantrieb	Benzin	85	116	Jan 2017	-	2025-06-01	127210
Hyundai	Santa fé iii	2.0 Crdi 4WD	SUV	Allrad	Diesel	136	185	Sep 2012	Aug 2018	2024-05-01	127211
Seat	Ibiza v	1.6 SRE	Schrägheck	Frontantrieb	Benzin	81	110	May 2017	-	2025-12-01	127213
Renault	Megane iv grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	84	115	Apr 2016	-	2024-03-01	127217
Aixam	Crossline	0.6	Schrägheck	Frontantrieb	Diesel	11	15	Jan 2012	Dec 2016	2024-03-01	127221
ARO	Spartana pick up	1,2 AWD	Geländewagen offen	Allrad	Benzin	40	54	Jan 1997	Dec 2003	2024-03-01	127222
Fiat	500x	1.4 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	88	120	Mar 2017	Sep 2018	2024-03-01	127239
Austin	Montego	2	Stufenheck	Frontantrieb	Benzin	76	103	Jan 1988	Dec 1993	2024-03-01	127241
Austin	Allegro i	1.3	Stufenheck	Frontantrieb	Benzin	41	56	Feb 1973	Dec 1975	2024-03-01	127242
Austin	Allegro i	1.5	Stufenheck	Frontantrieb	Benzin	51	69	Feb 1973	Dec 1979	2024-03-01	127243
Austin	Allegro i	1.3	Kombi	Frontantrieb	Benzin	46	63	Jan 1981	Dec 1983	2024-03-01	127244
Austin-healey	3000 mk.i	2.9	Cabriolet	Heckantrieb	Benzin	97	132	Jan 1959	Dec 1961	2024-03-01	127249


--- Round 1 / 首次发送 ---
## 更新点

* 已按缓存优先完成 **31/100 个输入 Ktype**，形成 **34 条 READY 映射**。
* 复用跨批次既有尺寸组 16 个，包括 Outlander III 前期/改款、208 I 三门/五门、Giulia、A3 Cabriolet、Mondeo IV、i30、F-Type、Stelvio、Micra、Golf Variant、Impreza、Trafic 与 Megane Grandtour。
* 本轮首次闭合 4 个尺寸组：Mazda CX-5 KE、Jaguar XE X760、Jaguar XF X260、Volkswagen Arteon 3H 改款前。Mazda brochure 明确列出 4555/1840/1710 mm；Jaguar 官方资料分别明确 XE 与 XF 的不含后视镜宽度；Arteon 页面同时区分车身宽度与含镜宽度。
* Outlander III 两个跨改款 Ktype 已拆为前期与改款后分支；Peugeot 208 I 未区分门数的 Ktype 已拆为三门和五门分支。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：31
* READY 映射：34
* PENDING/未处理输入 Ktype：69
* 已确认尺寸组：20

  * 复用既有组：16
  * 本轮新建组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126682_prefl	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	HIGH	生产区间跨越外观改款，拆分改款前物理外廓。	READY
126682_facelift	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	HIGH	生产区间跨越外观改款，拆分改款后物理外廓。	READY
126684_prefl	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	HIGH	生产区间跨越外观改款，拆分改款前物理外廓。	READY
126684_facelift	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	HIGH	生产区间跨越外观改款，拆分改款后物理外廓。	READY
126685_3dr	126685	Hatchback	208 I facelift	CA	3	EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按改款期三门物理分支拆分。	READY
126685_5dr	126685	Hatchback	208 I facelift	CC	5	EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按改款期五门物理分支拆分。	READY
126711	126711	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
126724	126724	SUV	CX-5 I	KE	5	EU-MAZDA-CX-5-I-KE-SUV-01	HIGH		READY
126725	126725	SUV	CX-5 I	KE	5	EU-MAZDA-CX-5-I-KE-SUV-01	HIGH		READY
126745	126745	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126746	126746	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126747	126747	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126748	126748	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126749	126749	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126750	126750	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126751	126751	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126752	126752	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126753	126753	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126829	126829	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	280 PS 4MOTION 分支属于改款前外廓。	READY
126831	126831	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH		READY
126844	126844	Wagon	Golf VII Variant facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
126845	126845	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
126874	126874	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
126877	126877	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
126883	126883	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
126887	126887	Coupe	F-Type X152 facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH		READY
126888	126888	Convertible	F-Type X152 facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
126958	126958	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126959	126959	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126960	126960	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
127130	127130	Hatchback	Impreza V	GT	5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	HIGH		READY
127205	127205	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	MEDIUM	X82平台驾驶室按L2物理外廓关联。	READY
127206	127206	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	MEDIUM	X82平台驾驶室按L2物理外廓关联。	READY
127217	127217	Wagon	Megane IV Grandtour	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-CX-5-I-KE-SUV-01	4555	1840	1710	Mazda CX-5 major specifications brochure	https://i.i-sgcm.com/new_cars/cars/11144/brochures/brochure_20160926043521.pdf
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1416	Jaguar XE official media technical specifications	https://media.jaguar.com/news/2015/11/jaguar-xe-gains-all-wheel-drive-next-generation-infotainment-system-and-apple-watch
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457	Jaguar XF official media technical specifications	https://media.jaguar.com/en-gb/news/2016/01/jaguar-launches-new-xf-all-wheel-drive-uk
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450	Auto-Data Volkswagen Arteon 2.0 TSI 280 4MOTION	https://www.auto-data.net/en/volkswagen-arteon-2.0-tsi-280hp-4motion-dsg-28870
```

## 下一步优先处理

1. 批量闭合 Mazda CX-5 II KF、Suzuki Swift V、Kia Picanto III、Seat Ibiza V 等重复 Ktype 较多的现代车身簇。
2. 核对 AMG GT 2017 改款、Audi RS3/RS5、Porsche Panamera Sport Turismo 与 Liftback 的宽体和高度差异。
3. 处理 Alfa Romeo Spider 各系列、Austin Allegro/Montego、Aston Martin、Aixam、ARO 等历史车型簇。
4. 对产品结束月为 `-` 且可能跨改款的 E-Class C238、Arteon 150 PS 等记录先确认物理分支边界，再建立映射。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 30 条 READY 映射，覆盖 30 个输入 Ktype。
* 首次创建 15 个尺寸组。
* 复用 Golf VII facelift Hatchback、Panamera II Liftback、Soul II facelift 3 个既有尺寸组。
* Panamera Sport Turismo 按普通车身与 Turbo 高度差异拆分；Swift 按前驱与 AllGrip 高度差异拆分。
* CX-5 II 本轮先闭合生产区间明确止于 2018 年的改款前分支；跨 2021 改款记录暂不提前关联。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：61
* READY 映射：64
* PENDING/尚未闭合输入 Ktype：39
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126755	126755	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	HIGH	标准车身外廓。	READY
126756	126756	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	HIGH	标准车身外廓。	READY
126827	126827	Hatchback	Jazz III facelift	GK5	5	EU-HONDA-JAZZ-III-GK5-HATCHBACK-FACELIFT-01	HIGH		READY
126840	126840	Hatchback	Golf VII facelift	5G	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
126863	126863	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
126875	126875	Hatchback	RS3 8V facelift	8VA	5	EU-AUDI-RS3-8V-FACELIFT-SPORTBACK-01	HIGH	RS专属宽体外廓。	READY
126876	126876	Sedan	RS3 8V facelift	8VS	4	EU-AUDI-RS3-8V-FACELIFT-SEDAN-01	HIGH	RS专属宽体外廓。	READY
126886	126886	Sedan	Civic X Sedan	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH		READY
126889	126889	Hatchback	Yaris III facelift	XP130	5	EU-TOYOTA-YARIS-III-XP130-HATCHBACK-FACELIFT-01	HIGH		READY
126894	126894	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126896	126896	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126897	126897	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126898	126898	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo车身高度分支。	READY
126899	126899	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126908	126908	Liftback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH		READY
126913	126913	SUV	Juke I	F15	5	EU-NISSAN-JUKE-I-F15-SUV-01	HIGH		READY
126919	126919	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126920	126920	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126921	126921	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126922	126922	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126923	126923	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	HIGH	AllGrip高度分支。	READY
126924	126924	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	HIGH	AllGrip高度分支。	READY
127062	127062	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间止于首次外观改款前。	READY
127065	127065	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
127066	127066	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
127078	127078	Hatchback	Soul II facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH		READY
127208	127208	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127209	127209	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127210	127210	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127213	127213	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	4544	1939	1287	Auto-Data Mercedes-Benz AMG GT C190 facelift	https://www.auto-data.net/en/mercedes-benz-amg-gt-c190-facelift-2017-4.0-v8-476hp-dct-28423
EU-HONDA-JAZZ-III-GK5-HATCHBACK-FACELIFT-01	4051	1694	1525	Auto-Data Honda Jazz III facelift 1.5 i-VTEC	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.5-i-vtec-130hp-32645
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590	Auto-Data SsangYong Tivoli 1.6 VGT	https://www.auto-data.net/en/ssangyong-tivoli-1.6-vgt-115hp-22445
EU-AUDI-RS3-8V-FACELIFT-SPORTBACK-01	4335	1800	1411	Auto-Data Audi RS3 Sportback 8VA facelift	https://www.auto-data.net/en/audi-rs3-sportback-8va-facelift-2017-2.5-tfsi-400hp-quattro-s-tronic-27853
EU-AUDI-RS3-8V-FACELIFT-SEDAN-01	4479	1802	1397	Auto-Data Audi RS3 Sedan 8V facelift	https://www.auto-data.net/en/audi-rs3-sedan-8v-facelift-2017-2.5-tfsi-400hp-quattro-s-tronic-27838
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416	Auto-Data Honda Civic X Sedan 1.5 VTEC	https://www.auto-data.net/en/honda-civic-x-sedan-1.5-vtec-182hp-turbo-29689
EU-TOYOTA-YARIS-III-XP130-HATCHBACK-FACELIFT-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 1.5 Dual VVT-iE	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.5-dual-vvt-ie-111hp-29031
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	5049	1937	1428	Auto-Data Porsche Panamera G2 Sport Turismo 4	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-4-3.0-v6-330hp-pdk-30548
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432	Auto-Data Porsche Panamera G2 Sport Turismo Turbo	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-turbo-4.0-v8-550hp-pdk-30430
EU-NISSAN-JUKE-I-F15-SUV-01	4135	1765	1570	Auto-Data Nissan Juke I 1.6 16V	https://www.auto-data.net/en/nissan-juke-i-1.6-16v-117hp-17069
EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	3840	1735	1495	Suzuki Swift official brochure	https://www.levoissuzuki.co.uk/media/other/50094132/10053835swiftbrochure-ilovepdf-compressed.pdf
EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	3840	1735	1520	Suzuki Swift official brochure	https://www.levoissuzuki.co.uk/media/other/50094132/10053835swiftbrochure-ilovepdf-compressed.pdf
EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	4550	1840	1680	Auto-Data Mazda CX-5 II 2.2 SKYACTIV-D	https://www.auto-data.net/en/mazda-cx-5-ii-2.2-skyactiv-d-150hp-29986
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485	Auto-Data Kia Picanto III 1.0	https://www.auto-data.net/en/kia-picanto-iii-1.0-67hp-29111
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	Auto-Data Seat Ibiza V 1.0 MPI	https://www.auto-data.net/en/seat-ibiza-v-1.0-mpi-75hp-start-stop-29532
```

## 下一步优先处理

1. 闭合 CX-5 II 跨 2021 改款 Ktype，并区分改款前后的宽度变化。
2. 处理 E-Class C238、RS5 F5、Arteon 150 PS 等可能跨外观改款的记录。
3. 批量闭合 Koleos II、Grand Cherokee IV、Kia Sportage III、Santa Fe III 与 Land Cruiser Prado。
4. 随后处理 Aston Martin、Lotus、McLaren、Honda NSX 及 Alfa Romeo/Austin 等历史车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 新增闭合 14 个输入 Ktype，共新增 20 条 READY 映射。
* E-Class C238 与 CX-5 II 的生产区间跨越尺寸发生变化的改款节点，已分别拆为改款前、改款后物理分支。C238 的长度由 4826 mm 变为 4835 mm；CX-5 改款后官方资料明确为 4575 × 1845 mm，并注明宽度不含后视镜。([汽车数据网][1])
* RS5 F5 使用 Audi 技术资料中的 4723 × 1866 × 1372 mm，其中 1866 mm 明确为不含后视镜宽度。
* Ampera-e、Koleos II、CX-9 II、Exige Sport 380、720S 与 NSX II 的尺寸组已首次闭合；Koleos brochure 明确区分含镜与不含镜宽度，CX-9 官方手册列出 5075 mm 长、1969 mm 宽和 1747 mm 高。([汽车手册在线][2])

## 2. 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：75
* READY 映射：84
* PENDING/尚未闭合输入 Ktype：25
* 已确认尺寸组：45
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126757_prefl	126757	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	HIGH	生产区间跨越2020年改款，拆分改款前物理外廓。	READY
126757_facelift	126757	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	HIGH	生产区间跨越2020年改款，拆分改款后物理外廓。	READY
126881	126881	Coupe	RS5 F5	F5	2	EU-AUDI-RS5-F5-COUPE-01	HIGH	RS宽体双门外廓。	READY
126998	126998	Hatchback	Ampera-e		5	EU-OPEL-AMPERA-E-HATCHBACK-01	HIGH		READY
127057_prefl	127057	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127057_facelift	127057	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127058_prefl	127058	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127058_facelift	127058	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127059_prefl	127059	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127059_facelift	127059	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127060_prefl	127060	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127060_facelift	127060	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127061_prefl	127061	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127061_facelift	127061	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127084	127084	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127085	127085	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127092	127092	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	HIGH	Sport 380外廓。	READY
127129	127129	SUV	CX-9 II	TC	5	EU-MAZDA-CX-9-II-TC-SUV-01	HIGH		READY
127199	127199	Coupe	720S	P14	2	EU-MCLAREN-720S-P14-COUPE-01	HIGH		READY
127200	127200	Coupe	NSX II	NC1	2	EU-HONDA-NSX-II-NC1-COUPE-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	4826	1860	1430	Auto-Data Mercedes-Benz E 220d 4MATIC C238	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E 220d 4MATIC C238 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-220d-194hp-4matic-9g-tronic-41062
EU-AUDI-RS5-F5-COUPE-01	4723	1866	1372	Audi RS 5 Coupe official technical data	https://media.audi.com/is/content/audi/nemo/ee/Mudelikataloogid/tehniline_info/Audi_RS_5_Coupe_2_9_TFSI.pdf
EU-OPEL-AMPERA-E-HATCHBACK-01	4164	1765	1594	Opel Ampera-e owner's manual technical data	https://www.carmanualsonline.info/opel-ampera-e-2018-5-owner-s-manual-2/?srch=dimensions
EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	4575	1845	1680	Mazda CX-5 2022 official price and specification guide, 19-inch configuration	https://media-assets.mazda.eu/raw/upload//mazdauk/contentassets/59f47a618d1d45f48d950987160eb455/mz402-cx-5-ps-sept22-v7web.pdf?rnd=4ae037
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos official brochure	https://www.renault.qa/CountriesData/Qatar_EN/images/brochures/EN/Koleos-brochure-EN.pdf
EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	4084	1802	1129	Auto-Data Lotus Exige III S Coupe	https://www.auto-data.net/en/lotus-exige-iii-s-coupe-generation-4418
EU-MAZDA-CX-9-II-TC-SUV-01	5075	1969	1747	Mazda CX-9 official owner's manual	https://owners-manual.mazda.com/gen/en/cx-9/cx-9_8hb9eo18g/contents/10020109.html
EU-MCLAREN-720S-P14-COUPE-01	4543	1930	1196	Auto-Data McLaren 720S	https://www.auto-data.net/en/mclaren-720s-generation-5492
EU-HONDA-NSX-II-NC1-COUPE-01	4487	1920	1204	Auto-Data Honda NSX II Coupe	https://www.auto-data.net/en/honda-nsx-ii-coupe-generation-5953
```

## 5. 下一步优先处理

1. 闭合 Grand Cherokee IV、Land Cruiser Prado、Santa Fe III、Sportage III 与 Fiat 500X。
2. 处理 Aston Martin Vanquish/Vantage/Virage、BMW M3 E30 Cabriolet 与 Alfa Romeo Spider/33/Alfasud。
3. 最后处理 Aixam Crossline、ARO Spartana、Austin Montego/Allegro 与 Austin-Healey 3000 等历史或小众车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748 "Mercedes-Benz E-class Coupe (C238) E 220d (194 Hp) 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.carmanualsonline.info/opel-ampera-e-2018-5-owner-s-manual-2/?srch=dimensions&utm_source=chatgpt.com "dimensions OPEL AMPERA E 2018.5 Owner's Manual (273 Pages)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 新增闭合 **13 个输入 Ktype**，新增 **16 条 READY 映射**和 **15 个尺寸组**。
* Jeep Grand Cherokee IV、Volkswagen Arteon 与 Hyundai Santa Fe III 的输入生产区间跨越已确认的外观改款，已拆成改款前后派生行；既有 Arteon 改款前尺寸组直接复用。Jeep 两阶段的车宽分别为 1938 mm 和 1943 mm，Arteon 改款后为 4866 × 1871 × 1460 mm。([汽车数据网][1])
* Logan II facelift、Sportage III facelift、Santa Fe III 两阶段以及 Fiat 500X LPG 的尺寸组已闭合。([汽车数据网][2])
* C4 L 当前来源的高度为 1498–1508 mm 区间，无法形成唯一正整数高度，本轮不创建尺寸组。([汽车数据网][3])

## 2. 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：88
* READY 映射：100
* PENDING/尚未闭合输入 Ktype：12
* 已确认尺寸组：60
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126774	126774	Coupe	RX-8 facelift	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	HIGH		READY
126953_prefl	126953	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	HIGH	生产区间跨越2013年改款，拆分改款前外廓。	READY
126953_facelift	126953	SUV	Grand Cherokee IV facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-2013-01	HIGH	生产区间跨越2013年改款，拆分改款后外廓。	READY
126963	126963	Convertible	Vanquish II	VH310	2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	HIGH		READY
127056_prefl	127056	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	生产区间跨越2020年改款，拆分改款前外廓。	READY
127056_facelift	127056	Liftback	Arteon I facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	生产区间跨越2020年改款，拆分改款后外廓。	READY
127095	127095	Convertible	3 Series E30 M3	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
127108	127108	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-SERIES-4-CONVERTIBLE-01	HIGH		READY
127111	127111	Convertible	V8 Vantage	VH2	2	EU-ASTON-MARTIN-VANTAGE-VH2-ROADSTER-01	HIGH		READY
127112	127112	Coupe	Virage I		2	EU-ASTON-MARTIN-VIRAGE-I-COUPE-01	HIGH		READY
127122	127122	SUV	Land Cruiser Prado J120	GRJ125	3	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	HIGH	GRJ125短轴三门外廓。	READY
127127	127127	Sedan	Logan II facelift		4	EU-DACIA-LOGAN-II-SEDAN-FACELIFT-01	HIGH		READY
127157	127157	SUV	Sportage III facelift	SL	5	EU-KIA-SPORTAGE-III-SUV-FACELIFT-01	HIGH		READY
127211_prefl	127211	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-PREFL-01	HIGH	生产区间跨越2015年改款，拆分改款前外廓。	READY
127211_facelift	127211	SUV	Santa Fe III facelift	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-FACELIFT-01	HIGH	生产区间跨越2015年改款，拆分改款后外廓。	READY
127239	127239	SUV	500X I	334	5	EU-FIAT-500X-I-SUV-PREFL-01	HIGH		READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	4470	1770	1340	Automobile-Catalog Mazda RX-8 2008	https://www.automobile-catalog.com/car/2008/1678535/mazda_rx-8.html
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4822	1938	1761	Auto-Data Jeep Grand Cherokee IV WK2 5.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-5.7-v8-364hp-4x4-automatic-31161
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-2013-01	4822	1943	1761	Auto-Data Jeep Grand Cherokee IV WK2 facelift 2013 5.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-facelift-2013-5.7-v8-364hp-4x4-automatic-31180
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	4728	1912	1294	Aston Martin Vanquish Volante official brochure	https://astonmartins.com/wp-content/uploads/2013/05/Aston-Martin_Vanquish_Volante_brochure.pdf
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460	Auto-Data Volkswagen Arteon facelift 2.0 TDI	https://www.auto-data.net/en/volkswagen-arteon-facelift-2020-2.0-tdi-150hp-scr-dsg-40771
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370	Automobile-Catalog BMW M3 Cabrio E30	https://www.automobile-catalog.com/car/1988/63095/bmw_m3_cabrio.html
EU-ALFA-ROMEO-SPIDER-115-SERIES-4-CONVERTIBLE-01	4267	1626	1295	UltimateSpecs Alfa Romeo Spider Series 4 2000 Injection	https://www.ultimatespecs.com/car-specs/Alfa-Romeo/16538/Alfa-Romeo-Spider-Series-4-2000-Injection.html
EU-ASTON-MARTIN-VANTAGE-VH2-ROADSTER-01	4380	1865	1265	Aston Martin V8 Vantage official brochure	https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_V8_Vantage_4_7_brochure.pdf
EU-ASTON-MARTIN-VIRAGE-I-COUPE-01	4745	1856	1320	Automobile-Catalog Aston Martin Virage 1991	https://www.automobile-catalog.com/car/1991/227690/aston_martin_virage.html
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1870	Toyota 75 Years Vehicle Lineage Land Cruiser Prado three-door	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014203/
EU-DACIA-LOGAN-II-SEDAN-FACELIFT-01	4358	1733	1517	Auto-Data Dacia Logan II facelift 1.0	https://www.auto-data.net/en/dacia-logan-ii-facelift-2016-1.0-12v-73hp-27619
EU-KIA-SPORTAGE-III-SUV-FACELIFT-01	4440	1855	1635	Auto-Data Kia Sportage III facelift	https://www.auto-data.net/en/kia-sportage-iii-facelift-2014-1.7-crdi-116hp-19009
EU-HYUNDAI-SANTA-FE-III-DM-SUV-PREFL-01	4690	1880	1680	Auto-Data Hyundai Santa Fe III DM	https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-2.0-crdi-150hp-4wd-18584
EU-HYUNDAI-SANTA-FE-III-DM-SUV-FACELIFT-01	4690	1880	1680	Auto-Data Hyundai Santa Fe III DM facelift	https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-facelift-2015-2.0-crdi-150hp-4wd-24772
EU-FIAT-500X-I-SUV-PREFL-01	4248	1796	1600	Auto-Data Fiat 500X 1.4 EasyPower LPG	https://www.auto-data.net/en/fiat-500x-1.4-easypower-120hp-lpg-30105
```

## 5. 下一步优先处理

1. 解决 `127022` Citroën C4 L 的唯一高度配置。
2. 批量闭合 `127183`、`127184`、`127185`、`127188` 的 Alfa Romeo 历史车身。
3. 处理 `127241`–`127244` Austin、`127249` Austin-Healey。
4. 最后处理 `127221` Aixam Crossline 与 `127222` ARO Spartana Pick-up。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-5.7-v8-364hp-4x4-automatic-31161 "Jeep Grand Cherokee IV (WK2) 5.7 V8 (364 Hp) 4x4 Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/dacia-logan-ii-facelift-2016-1.0-12v-73hp-27619 "Dacia Logan II (facelift 2016) 1.0 12V (73 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/citroen-c4-l-sedan-phase-i-2012-1.6-vti-16v-120hp-automatic-27754 "Citroen C4 L Sedan (Phase I, 2012) 1.6 VTi 16V (120 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 剩余 12 个输入 Ktype 已全部闭合，新增 17 条 READY 映射和 17 个首次创建或补齐的尺寸组。
* Alfa Romeo 33、Spider、Austin Montego 和 Austin Allegro 的跨代际或跨改款生产区间已拆分为稳定物理分支。Alfa 33 的 905 与 907A 外廓分别为 4015×1612×1340 mm 和 4075×1614×1350 mm；Spider Series 3 使用 4245×1630×1290 mm。([汽车数据网][1])
* ARO Spartana、Alfasud Sprint、Austin-Healey 3000 Mk I 与 Montego 两阶段外廓均已闭合，宽度采用不含后视镜口径。([汽车目录][2])
* 已完成机械检查：映射表严格 10 列、尺寸组表严格 6 列；117 个 `id` 唯一；77 个尺寸组唯一；所有映射引用闭合；无孤立尺寸组；无空尺寸或空来源。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：117
* PENDING 映射：0
* 已确认尺寸组：77
* 映射引用闭合：117/117
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126682_prefl	126682	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	HIGH	生产区间跨越外观改款，拆分改款前物理外廓。	READY
126682_facelift	126682	SUV	Outlander III facelift		5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	HIGH	生产区间跨越外观改款，拆分改款后物理外廓。	READY
126684_prefl	126684	SUV	Outlander III		5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	HIGH	生产区间跨越外观改款，拆分改款前物理外廓。	READY
126684_facelift	126684	SUV	Outlander III facelift		5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	HIGH	生产区间跨越外观改款，拆分改款后物理外廓。	READY
126685_3dr	126685	Hatchback	208 I facelift	CA	3	EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按改款期三门物理分支拆分。	READY
126685_5dr	126685	Hatchback	208 I facelift	CC	5	EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按改款期五门物理分支拆分。	READY
126711	126711	Sedan	Giulia 952	952	4	EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	HIGH		READY
126724	126724	SUV	CX-5 I	KE	5	EU-MAZDA-CX-5-I-KE-SUV-01	HIGH		READY
126725	126725	SUV	CX-5 I	KE	5	EU-MAZDA-CX-5-I-KE-SUV-01	HIGH		READY
126745	126745	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126746	126746	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126747	126747	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126748	126748	Sedan	XE	X760	4	EU-JAGUAR-XE-X760-SEDAN-01	HIGH		READY
126749	126749	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126750	126750	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126751	126751	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126752	126752	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126753	126753	Sedan	XF II	X260	4	EU-JAGUAR-XF-II-X260-SEDAN-01	HIGH		READY
126755	126755	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	HIGH	标准车身外廓。	READY
126756	126756	Coupe	AMG GT I facelift	C190	2	EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	HIGH	标准车身外廓。	READY
126757_prefl	126757	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	HIGH	生产区间跨越2020年改款，拆分改款前物理外廓。	READY
126757_facelift	126757	Coupe	E-Class C238 facelift	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	HIGH	生产区间跨越2020年改款，拆分改款后物理外廓。	READY
126774	126774	Coupe	RX-8 facelift	SE3P	4	EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	HIGH		READY
126827	126827	Hatchback	Jazz III facelift	GK5	5	EU-HONDA-JAZZ-III-GK5-HATCHBACK-FACELIFT-01	HIGH		READY
126829	126829	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	280 PS 4MOTION 分支属于改款前外廓。	READY
126831	126831	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH		READY
126840	126840	Hatchback	Golf VII facelift	5G	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH		READY
126844	126844	Wagon	Golf VII Variant facelift		5	EU-VW-GOLF-VII-VARIANT-FACELIFT-01	HIGH		READY
126845	126845	Convertible	A3 8V facelift	8V7	2	EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	HIGH		READY
126863	126863	SUV	Tivoli I	X100	5	EU-SSANGYONG-TIVOLI-I-X100-SUV-01	HIGH		READY
126874	126874	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
126875	126875	Hatchback	RS3 8V facelift	8VA	5	EU-AUDI-RS3-8V-FACELIFT-SPORTBACK-01	HIGH	RS专属宽体外廓。	READY
126876	126876	Sedan	RS3 8V facelift	8VS	4	EU-AUDI-RS3-8V-FACELIFT-SEDAN-01	HIGH	RS专属宽体外廓。	READY
126877	126877	Sedan	Mondeo IV facelift	BA7	4	EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	HIGH		READY
126881	126881	Coupe	RS5 F5	F5	2	EU-AUDI-RS5-F5-COUPE-01	HIGH	RS宽体双门外廓。	READY
126883	126883	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	HIGH		READY
126886	126886	Sedan	Civic X Sedan	FC	4	EU-HONDA-CIVIC-X-FC-SEDAN-01	HIGH		READY
126887	126887	Coupe	F-Type X152 facelift	X152	2	EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	HIGH		READY
126888	126888	Convertible	F-Type X152 facelift	X152	2	EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	HIGH		READY
126889	126889	Hatchback	Yaris III facelift	XP130	5	EU-TOYOTA-YARIS-III-XP130-HATCHBACK-FACELIFT-01	HIGH		READY
126894	126894	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126896	126896	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126897	126897	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126898	126898	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo车身高度分支。	READY
126899	126899	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	HIGH		READY
126908	126908	Liftback	Panamera II	971	5	EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	HIGH		READY
126913	126913	SUV	Juke I	F15	5	EU-NISSAN-JUKE-I-F15-SUV-01	HIGH		READY
126919	126919	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126920	126920	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126921	126921	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126922	126922	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	HIGH		READY
126923	126923	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	HIGH	AllGrip高度分支。	READY
126924	126924	Hatchback	Swift V	A2L	5	EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	HIGH	AllGrip高度分支。	READY
126953_prefl	126953	SUV	Grand Cherokee IV	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	HIGH	生产区间跨越2013年改款，拆分改款前外廓。	READY
126953_facelift	126953	SUV	Grand Cherokee IV facelift	WK2	5	EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-2013-01	HIGH	生产区间跨越2013年改款，拆分改款后外廓。	READY
126958	126958	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126959	126959	SUV	Stelvio 949	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH		READY
126960	126960	Hatchback	Micra V	K14	5	EU-NISSAN-MICRA-V-K14-HATCHBACK-01	HIGH		READY
126963	126963	Convertible	Vanquish II	VH310	2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	HIGH		READY
126998	126998	Hatchback	Ampera-e		5	EU-OPEL-AMPERA-E-HATCHBACK-01	HIGH		READY
127022	127022	Sedan	C4 L Phase I	B7	4	EU-CITROEN-C4-L-PHASE-I-SEDAN-01	MEDIUM	标准车身高度配置。	READY
127056_prefl	127056	Liftback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	HIGH	生产区间跨越2020年改款，拆分改款前外廓。	READY
127056_facelift	127056	Liftback	Arteon I facelift	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	生产区间跨越2020年改款，拆分改款后外廓。	READY
127057_prefl	127057	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127057_facelift	127057	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127058_prefl	127058	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127058_facelift	127058	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127059_prefl	127059	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127059_facelift	127059	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127060_prefl	127060	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127060_facelift	127060	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127061_prefl	127061	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间跨越2021年改款，拆分改款前物理外廓。	READY
127061_facelift	127061	SUV	CX-5 II facelift	KF	5	EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	HIGH	生产区间跨越2021年改款，拆分改款后物理外廓。	READY
127062	127062	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH	生产区间止于首次外观改款前。	READY
127065	127065	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
127066	127066	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH		READY
127078	127078	Hatchback	Soul II facelift	PS	5	EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	HIGH		READY
127084	127084	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127085	127085	SUV	Koleos II		5	EU-RENAULT-KOLEOS-II-SUV-01	HIGH		READY
127092	127092	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	HIGH	Sport 380外廓。	READY
127095	127095	Convertible	3 Series E30 M3	E30	2	EU-BMW-3-E30-M3-CONVERTIBLE-01	HIGH		READY
127108	127108	Convertible	Spider Series 4	115	2	EU-ALFA-ROMEO-SPIDER-115-SERIES-4-CONVERTIBLE-01	HIGH		READY
127111	127111	Convertible	V8 Vantage	VH2	2	EU-ASTON-MARTIN-VANTAGE-VH2-ROADSTER-01	HIGH		READY
127112	127112	Coupe	Virage I		2	EU-ASTON-MARTIN-VIRAGE-I-COUPE-01	HIGH		READY
127122	127122	SUV	Land Cruiser Prado J120	GRJ125	3	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	HIGH	GRJ125短轴三门外廓。	READY
127127	127127	Sedan	Logan II facelift		4	EU-DACIA-LOGAN-II-SEDAN-FACELIFT-01	HIGH		READY
127129	127129	SUV	CX-9 II	TC	5	EU-MAZDA-CX-9-II-TC-SUV-01	HIGH		READY
127130	127130	Hatchback	Impreza V	GT	5	EU-SUBARU-IMPREZA-V-HATCHBACK-01	HIGH		READY
127157	127157	SUV	Sportage III facelift	SL	5	EU-KIA-SPORTAGE-III-SUV-FACELIFT-01	HIGH		READY
127183_905	127183	Hatchback	33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	HIGH	生产区间跨越1990年换代，拆分905外廓。	READY
127183_907a	127183	Hatchback	33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	HIGH	生产区间跨越1990年换代，拆分907A外廓。	READY
127184_series2	127184	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	HIGH	生产区间跨越Series 2与Series 3，拆分Series 2外廓。	READY
127184_series3	127184	Convertible	Spider Series 3	115	2	EU-ALFA-ROMEO-SPIDER-115-SERIES-3-CONVERTIBLE-01	HIGH	生产区间跨越Series 2与Series 3，拆分Series 3外廓。	READY
127185_series2	127185	Convertible	Spider Series 2	115	2	EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	HIGH	生产区间跨越Series 2与Series 3，拆分Series 2外廓。	READY
127185_series3	127185	Convertible	Spider Series 3	115	2	EU-ALFA-ROMEO-SPIDER-115-SERIES-3-CONVERTIBLE-01	HIGH	生产区间跨越Series 2与Series 3，拆分Series 3外廓。	READY
127188	127188	Coupe	Alfasud Sprint	902A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-902A-COUPE-01	HIGH		READY
127199	127199	Coupe	720S	P14	2	EU-MCLAREN-720S-P14-COUPE-01	HIGH		READY
127200	127200	Coupe	NSX II	NC1	2	EU-HONDA-NSX-II-NC1-COUPE-01	HIGH		READY
127205	127205	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	MEDIUM	X82平台驾驶室按L2物理外廓关联。	READY
127206	127206	Pickup	Trafic III	X82	2	EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	MEDIUM	X82平台驾驶室按L2物理外廓关联。	READY
127208	127208	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127209	127209	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127210	127210	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127211_prefl	127211	SUV	Santa Fe III	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-PREFL-01	HIGH	生产区间跨越2015年改款，拆分改款前外廓。	READY
127211_facelift	127211	SUV	Santa Fe III facelift	DM	5	EU-HYUNDAI-SANTA-FE-III-DM-SUV-FACELIFT-01	HIGH	生产区间跨越2015年改款，拆分改款后外廓。	READY
127213	127213	Hatchback	Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH		READY
127217	127217	Wagon	Megane IV Grandtour	KFB	5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH		READY
127221	127221	Hatchback	Crossline S8	S8	3	EU-AIXAM-CROSSLINE-S8-HATCHBACK-01	MEDIUM	S8时期Crossline外廓。	READY
127222	127222	Pickup	Spartana		2	EU-ARO-SPARTANA-PICKUP-01	MEDIUM	开放式双门Spartana Pick-up外廓。	READY
127239	127239	SUV	500X I	334	5	EU-FIAT-500X-I-SUV-PREFL-01	HIGH		READY
127241_prefl	127241	Sedan	Montego I	LM11	4	EU-AUSTIN-MONTEGO-I-SEDAN-PREFL-01	HIGH	生产区间跨越1988年改款，拆分改款前外廓。	READY
127241_facelift	127241	Sedan	Montego I facelift	LM11	4	EU-AUSTIN-MONTEGO-I-SEDAN-FACELIFT-01	HIGH	生产区间跨越1988年改款，拆分改款后外廓。	READY
127242	127242	Sedan	Allegro I	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH		READY
127243_early	127243	Sedan	Allegro I	ADO67	4	EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	HIGH	生产区间跨越Series 3外观更新，拆分早期外廓。	READY
127243_series3	127243	Sedan	Allegro Series 3	ADO67	4	EU-AUSTIN-ALLEGRO-ADO67-SEDAN-SERIES-3-01	HIGH	生产区间跨越Series 3外观更新，拆分Series 3外廓。	READY
127244	127244	Wagon	Allegro Series 3	ADO67	5	EU-AUSTIN-ALLEGRO-ADO67-WAGON-SERIES-3-01	HIGH		READY
127249	127249	Convertible	Austin-Healey 3000 Mk I		2	EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	HIGH	BN7与BT7共享外廓，车身代码留空。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1301-1400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	4655	1800	1680	Auto-Data Mitsubishi Outlander III 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-outlander-iii-2.0-mivec-150hp-2wd-automatic-17693
EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	4695	1810	1710	Auto-Data Mitsubishi Outlander III facelift 2.0 MIVEC	https://www.auto-data.net/en/mitsubishi-outlander-iii-facelift-2015-2.0-mivec-150hp-4wd-automatic-22198
EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-3D-01	3973	1739	1460	Auto-Data Peugeot 208 I Phase II 1.2 PureTech	https://www.auto-data.net/en/peugeot-208-i-phase-ii-2015-1.2-puretech-68hp-32398
EU-PEUGEOT-208-I-FACELIFT-HATCHBACK-5D-01	3973	1739	1460	Auto-Data Peugeot 208 I Phase II 1.2 PureTech	https://www.auto-data.net/en/peugeot-208-i-phase-ii-2015-1.2-puretech-68hp-32398
EU-ALFA-ROMEO-GIULIA-952-SEDAN-01	4643	1860	1436	Auto-Data Alfa Romeo Giulia 952 2.2 JTD	https://www.auto-data.net/en/alfa-romeo-giulia-952-2.2-jtd-180hp-automatic-23688
EU-MAZDA-CX-5-I-KE-SUV-01	4555	1840	1710	Mazda CX-5 major specifications brochure	https://i.i-sgcm.com/new_cars/cars/11144/brochures/brochure_20160926043521.pdf
EU-JAGUAR-XE-X760-SEDAN-01	4672	1850	1416	Jaguar XE official media technical specifications	https://media.jaguar.com/news/2015/11/jaguar-xe-gains-all-wheel-drive-next-generation-infotainment-system-and-apple-watch
EU-JAGUAR-XF-II-X260-SEDAN-01	4954	1880	1457	Jaguar XF official media technical specifications	https://media.jaguar.com/en-gb/news/2016/01/jaguar-launches-new-xf-all-wheel-drive-uk
EU-MERCEDES-BENZ-AMG-GT-I-C190-COUPE-FACELIFT-STANDARD-01	4544	1939	1287	Auto-Data Mercedes-Benz AMG GT C190 facelift	https://www.auto-data.net/en/mercedes-benz-amg-gt-c190-facelift-2017-4.0-v8-476hp-dct-28423
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	4826	1860	1430	Auto-Data Mercedes-Benz E 220d 4MATIC C238	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-220d-194hp-4matic-9g-tronic-31748
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E 220d 4MATIC C238 facelift	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-220d-194hp-4matic-9g-tronic-41062
EU-MAZDA-RX-8-SE3P-COUPE-FACELIFT-01	4470	1770	1340	Automobile-Catalog Mazda RX-8 2008	https://www.automobile-catalog.com/car/2008/1678535/mazda_rx-8.html
EU-HONDA-JAZZ-III-GK5-HATCHBACK-FACELIFT-01	4051	1694	1525	Auto-Data Honda Jazz III facelift 1.5 i-VTEC	https://www.auto-data.net/en/honda-jazz-iii-facelift-2017-1.5-i-vtec-130hp-32645
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450	Auto-Data Volkswagen Arteon 2.0 TSI 280 4MOTION	https://www.auto-data.net/en/volkswagen-arteon-2.0-tsi-280hp-4motion-dsg-28870
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Auto-Data Volkswagen Golf VII 5-door facelift	https://www.auto-data.net/en/volkswagen-golf-vii-5-door-facelift-2017-1.5-tsi-act-150hp-36005
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515	Auto-Data Volkswagen Golf VII Variant facelift	https://www.auto-data.net/en/volkswagen-golf-vii-variant-facelift-2017-1.5-tsi-act-150hp-36016
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409	Auto-Data Audi A3 Cabriolet 8V facelift	https://www.auto-data.net/en/audi-a3-cabriolet-8v-facelift-2016-1.6-tdi-110hp-23997
EU-SSANGYONG-TIVOLI-I-X100-SUV-01	4202	1798	1590	Auto-Data SsangYong Tivoli 1.6 VGT	https://www.auto-data.net/en/ssangyong-tivoli-1.6-vgt-115hp-22445
EU-FORD-MONDEO-IV-FACELIFT-SEDAN-01	4850	1886	1500	Auto-Data Ford Mondeo model specifications	https://www.auto-data.net/en/ford-mondeo-model-806
EU-AUDI-RS3-8V-FACELIFT-SPORTBACK-01	4335	1800	1411	Auto-Data Audi RS3 Sportback 8VA facelift	https://www.auto-data.net/en/audi-rs3-sportback-8va-facelift-2017-2.5-tfsi-400hp-quattro-s-tronic-27853
EU-AUDI-RS3-8V-FACELIFT-SEDAN-01	4479	1802	1397	Auto-Data Audi RS3 Sedan 8V facelift	https://www.auto-data.net/en/audi-rs3-sedan-8v-facelift-2017-2.5-tfsi-400hp-quattro-s-tronic-27838
EU-AUDI-RS5-F5-COUPE-01	4723	1866	1372	Audi RS 5 Coupe official technical data	https://media.audi.com/is/content/audi/nemo/ee/Mudelikataloogid/tehniline_info/Audi_RS_5_Coupe_2_9_TFSI.pdf
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455	Auto-Data Hyundai i30 III 1.4 MPi	https://www.auto-data.net/en/hyundai-i30-iii-1.4-mpi-100hp-25880
EU-HONDA-CIVIC-X-FC-SEDAN-01	4648	1799	1416	Auto-Data Honda Civic X Sedan 1.5 VTEC	https://www.auto-data.net/en/honda-civic-x-sedan-1.5-vtec-182hp-turbo-29689
EU-JAGUAR-F-TYPE-X152-COUPE-FACELIFT-01	4482	1923	1311	Auto-Data Jaguar F-Type Coupe facelift P300	https://www.auto-data.net/en/jaguar-f-type-coupe-facelift-2017-p300-300hp-automatic-36570
EU-JAGUAR-F-TYPE-X152-CONVERTIBLE-FACELIFT-01	4482	1923	1308	Auto-Data Jaguar F-Type Convertible facelift P380	https://www.auto-data.net/en/jaguar-f-type-convertible-facelift-2017-p380-v6-380hp-automatic-36652
EU-TOYOTA-YARIS-III-XP130-HATCHBACK-FACELIFT-01	3945	1695	1510	Auto-Data Toyota Yaris III facelift 1.5 Dual VVT-iE	https://www.auto-data.net/en/toyota-yaris-iii-facelift-2017-1.5-dual-vvt-ie-111hp-29031
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-STANDARD-01	5049	1937	1428	Auto-Data Porsche Panamera G2 Sport Turismo 4	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-4-3.0-v6-330hp-pdk-30548
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432	Auto-Data Porsche Panamera G2 Sport Turismo Turbo	https://www.auto-data.net/en/porsche-panamera-g2-sport-turismo-turbo-4.0-v8-550hp-pdk-30430
EU-PORSCHE-PANAMERA-II-971-LIFTBACK-01	5049	1937	1423	Porsche Panamera II technical specifications	https://www.auto-data.net/en/porsche-panamera-g2-generation-5189
EU-NISSAN-JUKE-I-F15-SUV-01	4135	1765	1570	Auto-Data Nissan Juke I 1.6 16V	https://www.auto-data.net/en/nissan-juke-i-1.6-16v-117hp-17069
EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-FWD-01	3840	1735	1495	Suzuki Swift official brochure	https://www.levoissuzuki.co.uk/media/other/50094132/10053835swiftbrochure-ilovepdf-compressed.pdf
EU-SUZUKI-SWIFT-V-A2L-HATCHBACK-ALLGRIP-01	3840	1735	1520	Suzuki Swift official brochure	https://www.levoissuzuki.co.uk/media/other/50094132/10053835swiftbrochure-ilovepdf-compressed.pdf
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-PREFL-01	4822	1938	1761	Auto-Data Jeep Grand Cherokee IV WK2 5.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-5.7-v8-364hp-4x4-automatic-31161
EU-JEEP-GRAND-CHEROKEE-IV-WK2-SUV-FACELIFT-2013-01	4822	1943	1761	Auto-Data Jeep Grand Cherokee IV WK2 facelift 2013 5.7 V8	https://www.auto-data.net/en/jeep-grand-cherokee-iv-wk2-facelift-2013-5.7-v8-364hp-4x4-automatic-31180
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Auto-Data Alfa Romeo Stelvio 949 2.2d	https://www.auto-data.net/en/alfa-romeo-stelvio-949-2.2d-180hp-awd-automatic-32432
EU-NISSAN-MICRA-V-K14-HATCHBACK-01	3999	1743	1455	Auto-Data Nissan Micra K14 1.0	https://www.auto-data.net/en/nissan-micra-k14-1.0-73hp-27408
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-01	4728	1912	1294	Aston Martin Vanquish Volante official brochure	https://astonmartins.com/wp-content/uploads/2013/05/Aston-Martin_Vanquish_Volante_brochure.pdf
EU-OPEL-AMPERA-E-HATCHBACK-01	4164	1765	1594	Opel Ampera-e owner's manual technical data	https://www.carmanualsonline.info/opel-ampera-e-2018-5-owner-s-manual-2/?srch=dimensions
EU-CITROEN-C4-L-PHASE-I-SEDAN-01	4621	1779	1498	Auto-Data Citroen C4 L Sedan Phase I 1.6 VTi standard-height configuration	https://www.auto-data.net/en/citroen-c4-l-sedan-phase-i-2012-1.6-vti-16v-120hp-automatic-27754
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460	Auto-Data Volkswagen Arteon facelift 2.0 TDI	https://www.auto-data.net/en/volkswagen-arteon-facelift-2020-2.0-tdi-150hp-scr-dsg-40771
EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	4550	1840	1680	Auto-Data Mazda CX-5 II 2.2 SKYACTIV-D	https://www.auto-data.net/en/mazda-cx-5-ii-2.2-skyactiv-d-150hp-29986
EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	4575	1845	1680	Mazda CX-5 2022 official price and specification guide, 19-inch configuration	https://media-assets.mazda.eu/raw/upload//mazdauk/contentassets/59f47a618d1d45f48d950987160eb455/mz402-cx-5-ps-sept22-v7web.pdf?rnd=4ae037
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485	Auto-Data Kia Picanto III 1.0	https://www.auto-data.net/en/kia-picanto-iii-1.0-67hp-29111
EU-KIA-SOUL-II-FACELIFT-HATCHBACK-01	4140	1800	1618	Auto-Data Kia Soul II facelift 1.6 T-GDI	https://www.auto-data.net/en/kia-soul-ii-facelift-2016-1.6-t-gdi-204hp-dct-23895
EU-RENAULT-KOLEOS-II-SUV-01	4673	1843	1678	Renault Koleos official brochure	https://www.renault.qa/CountriesData/Qatar_EN/images/brochures/EN/Koleos-brochure-EN.pdf
EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	4084	1802	1129	Auto-Data Lotus Exige III S Coupe	https://www.auto-data.net/en/lotus-exige-iii-s-coupe-generation-4418
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370	Automobile-Catalog BMW M3 Cabrio E30	https://www.automobile-catalog.com/car/1988/63095/bmw_m3_cabrio.html
EU-ALFA-ROMEO-SPIDER-115-SERIES-4-CONVERTIBLE-01	4267	1626	1295	UltimateSpecs Alfa Romeo Spider Series 4 2000 Injection	https://www.ultimatespecs.com/car-specs/Alfa-Romeo/16538/Alfa-Romeo-Spider-Series-4-2000-Injection.html
EU-ASTON-MARTIN-VANTAGE-VH2-ROADSTER-01	4380	1865	1265	Aston Martin V8 Vantage official brochure	https://astonmartins.com/wp-content/uploads/2013/01/Aston-Martin_V8_Vantage_4_7_brochure.pdf
EU-ASTON-MARTIN-VIRAGE-I-COUPE-01	4745	1856	1320	Automobile-Catalog Aston Martin Virage 1991	https://www.automobile-catalog.com/car/1991/227690/aston_martin_virage.html
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1870	Toyota 75 Years Vehicle Lineage Land Cruiser Prado three-door	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014203/
EU-DACIA-LOGAN-II-SEDAN-FACELIFT-01	4358	1733	1517	Auto-Data Dacia Logan II facelift 1.0	https://www.auto-data.net/en/dacia-logan-ii-facelift-2016-1.0-12v-73hp-27619
EU-MAZDA-CX-9-II-TC-SUV-01	5075	1969	1747	Mazda CX-9 official owner's manual	https://owners-manual.mazda.com/gen/en/cx-9/cx-9_8hb9eo18g/contents/10020109.html
EU-SUBARU-IMPREZA-V-HATCHBACK-01	4460	1775	1480	Auto-Data Subaru Impreza V Hatchback 2.0i AWD	https://www.auto-data.net/en/subaru-impreza-v-hatchback-2.0i-156hp-awd-lineartronic-32130
EU-KIA-SPORTAGE-III-SUV-FACELIFT-01	4440	1855	1635	Auto-Data Kia Sportage III facelift	https://www.auto-data.net/en/kia-sportage-iii-facelift-2014-1.7-crdi-116hp-19009
EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	Auto-Data Alfa Romeo 33 905 1.5	https://www.auto-data.net/en/alfa-romeo-33-905-1.5-84hp-4x4-1406
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Automobile-Catalog Alfa Romeo 33 1.3 V 1990	https://www.automobile-catalog.com/car/1990/216710/alfa_romeo_33_1_3_v.html
EU-ALFA-ROMEO-SPIDER-105-SERIES-2-CONVERTIBLE-01	4120	1630	1290	Automobile-Catalog Alfa Romeo Spider Series 2	https://www.automobile-catalog.com/make/alfa_romeo/spider_alfa_romeo/spider_serie_2/1980.html
EU-ALFA-ROMEO-SPIDER-115-SERIES-3-CONVERTIBLE-01	4245	1630	1290	Automobile-Catalog Alfa Romeo Spider Series 3 1.6	https://www.automobile-catalog.com/car/1983/214295/alfa_romeo_spider_1_6.html
EU-ALFA-ROMEO-ALFASUD-SPRINT-902A-COUPE-01	4019	1610	1305	Automobile-Catalog Alfa Romeo Alfasud Sprint 1.3	https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html
EU-MCLAREN-720S-P14-COUPE-01	4543	1930	1196	Auto-Data McLaren 720S	https://www.auto-data.net/en/mclaren-720s-generation-5492
EU-HONDA-NSX-II-NC1-COUPE-01	4487	1920	1204	Auto-Data Honda NSX II Coupe	https://www.auto-data.net/en/honda-nsx-ii-coupe-generation-5953
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971	Renault Trafic III X82 L2 technical dimensions	https://www.auto-data.net/en/renault-trafic-iii-generation-4314
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	Auto-Data Seat Ibiza V 1.0 MPI	https://www.auto-data.net/en/seat-ibiza-v-1.0-mpi-75hp-start-stop-29532
EU-HYUNDAI-SANTA-FE-III-DM-SUV-PREFL-01	4690	1880	1680	Auto-Data Hyundai Santa Fe III DM	https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-2.0-crdi-150hp-4wd-18584
EU-HYUNDAI-SANTA-FE-III-DM-SUV-FACELIFT-01	4690	1880	1680	Auto-Data Hyundai Santa Fe III DM facelift	https://www.auto-data.net/en/hyundai-santa-fe-iii-dm-facelift-2015-2.0-crdi-150hp-4wd-24772
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449	Auto-Data Renault Megane IV Grandtour 1.5 Blue dCi	https://www.auto-data.net/en/renault-megane-iv-grandtour-1.5-blue-dci-115hp-35501
EU-AIXAM-CROSSLINE-S8-HATCHBACK-01	2990	1500	1540	1000PS Aixam Crossline 2016 technical data	https://www.1000ps.com/en-gb/model/6359/aixam-crossline/2016
EU-ARO-SPARTANA-PICKUP-01	3680	1640	1660	Automobile-Catalog ARO Spartana 1997	https://www.automobile-catalog.com/car/1997/1763930/aro_spartana.html
EU-FIAT-500X-I-SUV-PREFL-01	4248	1796	1600	Auto-Data Fiat 500X 1.4 EasyPower LPG	https://www.auto-data.net/en/fiat-500x-1.4-easypower-120hp-lpg-30105
EU-AUSTIN-MONTEGO-I-SEDAN-PREFL-01	4468	1710	1420	Automobile-Catalog Austin Montego phase I Sedan 1988	https://www.automobile-catalog.com/make/austin/montego/montego_sedan_austin/1988.html
EU-AUSTIN-MONTEGO-I-SEDAN-FACELIFT-01	4465	1710	1420	Automobile-Catalog Austin Montego phase II Sedan 1988	https://www.automobile-catalog.com/make/austin/montego/montego_sedan_2/1988.html
EU-AUSTIN-ALLEGRO-I-ADO67-SEDAN-EARLY-01	3855	1613	1397	Carfolio Austin Allegro 1300	https://www.carfolio.com/austin-allegro-1300-53097
EU-AUSTIN-ALLEGRO-ADO67-SEDAN-SERIES-3-01	3908	1613	1397	Automobile-Catalog Austin Allegro Series 3 Saloon	https://www.automobile-catalog.com/make/austin/allegro/allegro_serie_3_saloon/1979.html
EU-AUSTIN-ALLEGRO-ADO67-WAGON-SERIES-3-01	3995	1630	1440	Automobile-Catalog Austin Allegro Series 3 Estate	https://www.automobile-catalog.com/make/austin/allegro/allegro_serie_3_wagon/1981.html
EU-AUSTIN-HEALEY-3000-MK-I-CONVERTIBLE-01	4001	1524	1250	Automobile-Catalog Austin-Healey 3000 Mk I	https://www.automobile-catalog.com/car/1959/258755/austin-healey_3000_22_overdrive.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1301-1400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/alfa-romeo-33-905-1.5-84hp-4x4-1406 "https://www.auto-data.net/en/alfa-romeo-33-905-1.5-84hp-4x4-1406"
[2]: https://www.automobile-catalog.com/car/1997/1763930/aro_spartana.html "https://www.automobile-catalog.com/car/1997/1763930/aro_spartana.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1301-1400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1301-1400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1449 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（723 行）

