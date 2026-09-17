# 任务：all 第 4101-4200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0042__a92c77b9


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4101-4200 行

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
all 第 4101-4200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-01	4762	1847	1460
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-2018-01	4738	1842	1435
EU-AUDI-A4-B9-SEDAN-01	4726	1842	1427
EU-AUDI-A4-B9-SEDAN-FACELIFT-01	4762	1847	1431
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-X7-G07-SUV-01	5151	2000	1805
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
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
EU-FORD-MONDEO-V-CD391-HATCHBACK-5D-01	4871	1852	1482
EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	4871	1852	1482
EU-FORD-MONDEO-V-CD391-WAGON-01	4867	1852	1501
EU-FORD-MONDEO-V-WAGON-FACELIFT-01	4867	1852	1501
EU-FORD-USA-MUSTANG-S550-ECOBOOST-COUPE-PREFL-01	4784	1916	1381
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-CONVERTIBLE-01	4789	1916	1387
EU-FORD-USA-MUSTANG-S550-FACELIFT-ECOBOOST-COUPE-01	4789	1916	1373
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382
EU-FORD-USA-MUSTANG-S550-GT-COUPE-PREFL-01	4784	1916	1381
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
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
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639
EU-OPEL-COMBO-D-TOUR-MPV-01	4390	1831	1845
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590
EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	4753	1848	1882
EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	4403	1848	1878
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469
EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	4861	1864	1468
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477
EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	4856	1864	1477
EU-SSANGYONG-MUSSO-Q200-PICKUP-01	5095	1950	1870
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940
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
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
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
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Opel	Combo	1.2	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Feb 2019	-	2024-03-01	136868
Peugeot	Boxer	2.2 Bluehdi 140	Bus	Frontantrieb	Diesel	103	140	Jul 2019	Oct 2023	2024-05-01	136872
Toyota	Proace	1.5 D4D	Bus	Frontantrieb	Diesel	88	120	Aug 2018	Apr 2025	2026-01-01	136878
VW	Amarok	3.0 TDI 4motion	Pritsche/Fahrgestell	Allrad	Diesel	150	204	Jun 2016	Aug 2020	2024-03-01	136903
VW	Golf iv van	1.9 TDI 4motion	Kasten/Schrägheck	Allrad	Diesel	85	116	Jan 2000	Apr 2001	2024-03-01	136915
Opel	Crossland x /	1.2	SUV	Frontantrieb	Benzin	61	83	Jul 2019	-	2024-03-01	136916
Mercedes-benz	C-Klasse	C 300 CDI 4-matic	Kombi	Allrad	Diesel	170	231	Jun 2011	Aug 2014	2024-03-01	136917
VW	Golf iv van	1.9 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	81	110	Oct 1997	May 2004	2024-03-01	136918
VW	Golf iv van	1.9 SDI	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Nov 1998	May 2004	2024-03-01	136921
VW	Golf van iii variant	1.4	Kasten/Kombi	Frontantrieb	Benzin	44	60	May 1993	Jul 1995	2024-03-01	136927
VW	Golf iii van	1.9 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	66	90	Aug 1991	Sep 1997	2024-03-01	136928
VW	Golf van iii variant	1.8	Kasten/Kombi	Frontantrieb	Benzin	55	75	Jul 1993	Feb 1999	2024-03-01	136929
VW	Golf iii van	1.8	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Aug 1991	Jul 1995	2024-03-01	136931
VW	Golf van iii variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	66	90	Aug 1993	Dec 1999	2024-03-01	136934
VW	Golf van iii variant	1.9	Kasten/Kombi	Frontantrieb	Diesel	47	64	Aug 1993	Feb 1999	2024-03-01	136938
VW	Golf van iii variant	1.9 TDI	Kasten/Kombi	Frontantrieb	Diesel	81	110	May 1996	Feb 1999	2024-03-01	136939
VW	Golf van iii variant	1.8	Kasten/Kombi	Frontantrieb	Benzin	66	90	Aug 1993	Dec 1999	2024-03-01	136941
VW	Transporter t5	2.0 CNG	Pritsche/Fahrgestell	Frontantrieb	Benzin/Erdgas (CNG)	85	115	Nov 2003	May 2011	2024-03-01	136949
VW	Transporter t5	2.0 CNG	Bus	Frontantrieb	Benzin/Erdgas (CNG)	85	115	Jan 2006	Aug 2015	2024-03-01	136950
Toyota	Proace	1.5 D4D	Bus	Frontantrieb	Diesel	75	102	Aug 2018	Apr 2025	2026-01-01	136952
Renault	Trafic iii	2.0 DCI 145	Kasten	Frontantrieb	Diesel	107	145	Jun 2019	-	2024-03-01	136956
Opel	Corsa f	Corsa-e	Schrägheck	Frontantrieb	Elektro	100	136	Jul 2019	-	2024-03-01	136963
Ssangyong	Korando	1.5 E-xgdi	SUV	Frontantrieb	Benzin	120	163	Feb 2019	-	2024-03-01	136964
Ssangyong	Korando	1.5 E-xgdi 4WD	SUV	Allrad	Benzin	120	163	Feb 2019	-	2024-03-01	136965
Ssangyong	Korando	1.6 E-xdi	SUV	Frontantrieb	Diesel	100	136	Feb 2019	-	2024-03-01	136966
Ssangyong	Korando	1.6 E-xdi 4WD	SUV	Allrad	Diesel	100	136	Feb 2019	-	2024-03-01	136967
Ssangyong	Musso	2.2 E-xdi	Pick-up	Heckantrieb	Diesel	133	181	Jan 2019	-	2024-03-01	136992
Ssangyong	Musso	2.2 E-xdi 4WD	Pick-up	Allrad	Diesel	133	181	Jan 2019	-	2024-03-01	136993
Volvo	Xc90 ii	T8 Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	233	317	Jan 2019	Dec 2022	2024-05-01	136994
Volvo	Xc90 ii	D5 Polestar AWD	SUV	Allrad	Diesel	177	240	Oct 2018	Dec 2021	2024-05-01	136995
Volvo	Xc60 ii	D5 Polestar AWD	SUV	Allrad	Diesel	177	240	Oct 2018	Mar 2020	2025-06-01	136996
VW	Crafter	2.0 TDI 4motion	Bus	Allrad	Diesel	130	177	Mar 2017	-	2024-03-01	137004
Mercedes-benz	Sprinter 3-T	211 CDI RWD	Pritsche/Fahrgestell	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	137007
Mercedes-benz	Glc	AMG 43 4-matic	SUV	Allrad	Benzin	287	390	Aug 2019	Jun 2022	2024-03-01	137008
Mercedes-benz	Glc	AMG 43 4-matic	SUV	Allrad	Benzin	287	390	Aug 2019	Mar 2023	2024-03-01	137009
Mercedes-benz	Sprinter 3,5-T	316 NGT	Bus	Heckantrieb	Benzin/Erdgas (CNG)	115	156	Mar 2009	Dec 2018	2024-03-01	137021
Jeep	Gladiator	3.6 VVT	Pick-up	Allrad	Benzin	213	290	Apr 2019	-	2024-03-01	137022
Mercedes-benz	C-Klasse	C 300 EQ Boost 4-matic	Coupe	Allrad	Benzin/Elektro	190	258	May 2019	Apr 2023	2024-03-01	137026
Mercedes-benz	C-Klasse	C 300 EQ Boost 4-matic	Cabriolet	Allrad	Benzin/Elektro	190	258	May 2019	Apr 2023	2024-03-01	137029
Peugeot	Boxer	2.2 Bluehdi 120	Kasten	Frontantrieb	Diesel	88	120	Jul 2019	Oct 2023	2024-05-01	137031
Peugeot	Boxer	2.2 Bluehdi 140	Kasten	Frontantrieb	Diesel	103	140	Jul 2019	Oct 2023	2024-05-01	137032
Peugeot	Boxer	2.2 Bluehdi 165	Kasten	Frontantrieb	Diesel	121	165	Jul 2019	Oct 2023	2024-05-01	137033
Peugeot	Boxer	2.2 Bluehdi 120	Bus	Frontantrieb	Diesel	88	120	Jul 2019	Oct 2023	2024-05-01	137035
Bentley	Bentayga	3.0 Hybrid	SUV	Allrad	Benzin/Elektro	330	449	Jan 2019	-	2024-03-01	137036
BMW	X7	Xdrive M 50 I	SUV	Allrad	Benzin	390	530	Jul 2019	-	2024-03-01	137037
VW	Touareg	4.0 V8 TDI 4motion	SUV	Allrad	Diesel	310	421	Jun 2019	Nov 2021	2024-03-01	137038
Mazda	3	2.0 Skyactiv-g	Schrägheck	Frontantrieb	Benzin	110	150	Nov 2018	-	2024-03-01	137040
Maserati	Levante	3.8 GTS Q4	SUV	Allrad	Benzin	390	530	Aug 2019	-	2024-03-01	137042
Peugeot	Rifter	1.2 Puretech 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	137043
Mazda	Cx-30	Skyactiv-g M Hybrid	SUV	Frontantrieb	Benzin/Elektro	90	122	Jul 2019	-	2024-03-01	137046
Mazda	Cx-30	Skyactiv-g M Hybrid AWD	SUV	Allrad	Benzin/Elektro	90	122	Jul 2019	-	2024-03-01	137047
Mazda	Cx-30	Skyactiv-x M Hybrid	SUV	Frontantrieb	Benzin/Elektro	132	179	Jul 2019	-	2024-03-01	137048
Mazda	Cx-30	Skyactiv-x M Hybrid AWD	SUV	Allrad	Benzin/Elektro	132	179	Jul 2019	-	2024-03-01	137049
Mazda	Cx-30	1.8 Skyactiv-d	SUV	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	137050
Mazda	Cx-30	1.8 Skyactiv-d AWD	SUV	Allrad	Diesel	85	116	Jul 2019	-	2024-03-01	137051
Skoda	Kamiq	1.0 TSI	SUV	Frontantrieb	Benzin	70	95	Jul 2019	-	2024-03-01	137056
Skoda	Kamiq	1.0 TSI	SUV	Frontantrieb	Benzin	85	116	Jul 2019	-	2025-06-01	137058
Skoda	Kamiq	1.6 TDI	SUV	Frontantrieb	Diesel	85	115	Jul 2019	-	2024-03-01	137059
Porsche	718 cayman	4.0 GT4	Coupe	Heckantrieb	Benzin	309	420	Jul 2019	-	2024-03-01	137060
Volvo	V90 ii	T5 Polestar	Kombi	Frontantrieb	Benzin	186	253	Oct 2017	Mar 2020	2025-06-01	137061
Volvo	S90 ii	T4 Polestar	Stufenheck	Frontantrieb	Benzin	155	210	Jun 2019	Dec 2021	2024-05-01	137062
Volvo	S90 ii	D5 Polestar AWD	Stufenheck	Allrad	Diesel	177	240	Mar 2016	Nov 2021	2025-06-01	137063
Volvo	V90 ii	T4 Polestar	Kombi	Frontantrieb	Benzin	155	210	Jun 2019	Dec 2021	2024-05-01	137085
Volvo	V90 ii	D4 Polestar	Kombi	Frontantrieb	Diesel	147	200	Oct 2016	Dec 2021	2024-05-01	137086
Audi	A4 b9 avant	S4 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	255	347	May 2019	-	2024-03-01	137088
Audi	A4 b9	S4 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	255	347	May 2019	-	2024-03-01	137089
Audi	A4 b9	35 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	120	163	Mar 2019	-	2024-03-01	137090
Citroën	Jumpy iii	1.6 Bluehdi 90	Kasten	Frontantrieb	Diesel	66	90	Sep 2018	-	2024-03-01	137091
Audi	Q5	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	270	367	Aug 2019	-	2024-03-01	137093
Peugeot	Rifter	1.6 Bluehdi 100	Großraumlimousine	Frontantrieb	Diesel	73	99	Sep 2018	-	2024-03-01	137096
Peugeot	Rifter	1.6 HDI 75 / Bluehdi 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2018	-	2024-03-01	137097
Peugeot	Rifter	1.6 HDI 92	Großraumlimousine	Frontantrieb	Diesel	68	92	Sep 2018	-	2024-03-01	137101
Citroën	Berlingo	1.2 Puretech 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	137107
BMW	1	118 D	Schrägheck	Frontantrieb	Diesel	100	136	Jul 2019	-	2024-03-01	137109
Land Rover	Discovery sport	2.0 D150 Mhev 4X4	SUV	Allrad	Diesel/Elektro	110	150	May 2019	-	2024-03-01	137110
Land Rover	Discovery sport	2.0 D180 Mhev 4X4	SUV	Allrad	Diesel/Elektro	132	179	May 2019	-	2024-03-01	137111
Land Rover	Discovery sport	2.0 D240 Mhev 4X4	SUV	Allrad	Diesel/Elektro	177	241	May 2019	-	2024-03-01	137112
Land Rover	Discovery sport	2.0 P200 Mhev 4X4	SUV	Allrad	Benzin/Elektro	147	200	May 2019	-	2024-03-01	137113
Land Rover	Discovery sport	2.0 P250 Mhev 4X4	SUV	Allrad	Benzin/Elektro	184	250	May 2019	-	2024-03-01	137114
Beijing	X3	1.5	SUV	Frontantrieb	Benzin	85	116	Jul 2019	-	2024-03-01	137118
Skoda	Superb iii	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Jul 2019	Jun 2024	2025-06-01	137129
Ford	Mondeo v	2.0 Ecoblue	Stufenheck	Frontantrieb	Diesel	88	120	Jan 2019	Mar 2022	2026-04-01	137130
Skoda	Superb iii	2.0 TSI	Schrägheck	Frontantrieb	Benzin	140	190	Jul 2019	Jun 2024	2025-06-01	137131
Porsche	718 boxster spyder	4	Cabriolet	Heckantrieb	Benzin	309	420	Jul 2019	-	2024-03-01	137133
Ford	Mondeo v	2.0 Ecoblue	Stufenheck	Frontantrieb	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	137134
Ford	Mondeo v	2.0 Ecoblue 4X4	Stufenheck	Allrad	Diesel	140	190	Jan 2019	Mar 2022	2026-04-01	137136
Ford	Mondeo v	1.5 Ecoboost	Stufenheck	Frontantrieb	Benzin	121	165	Jan 2019	Mar 2022	2026-04-01	137137
Volvo	Xc60 ii	D4 Polestar	SUV	Frontantrieb	Diesel	147	200	Dec 2018	Jun 2020	2025-06-01	137140
Ford USA	Mustang	5.0 V8	Coupe	Heckantrieb	Benzin	324	440	Jun 2019	Apr 2023	2024-05-01	137144
Ford USA	Mustang convertible	5.0 V8	Cabriolet	Heckantrieb	Benzin	324	440	Jun 2019	Apr 2023	2024-05-01	137145
Porsche	911	4	Cabriolet	Heckantrieb	Benzin	375	510	Jun 2018	Dec 2020	2024-03-01	137146
Porsche	911	3.0 Carrera	Coupe	Heckantrieb	Benzin	283	385	Jan 2019	Dec 2024	2026-03-01	137161
Porsche	911	3.0 Carrera	Cabriolet	Heckantrieb	Benzin	283	385	Jan 2019	Dec 2024	2026-03-01	137163
Mercedes-benz	Glc	400 D 4-matic	SUV	Allrad	Diesel	243	330	Aug 2019	Mar 2023	2024-03-01	137165
Mercedes-benz	Glc	400 D 4-matic	SUV	Allrad	Diesel	243	330	Aug 2019	Jun 2022	2024-03-01	137167
Fiat	Talento	1.6 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	89	121	Jun 2016	-	2024-03-01	137169
BMW	2	218 I	Coupe	Frontantrieb	Benzin	103	140	Nov 2019	-	2024-03-01	137170
BMW	2	M 235 I Xdrive	Coupe	Allrad	Benzin	225	306	Nov 2019	-	2024-03-01	137172
BMW	2	220 D	Coupe	Frontantrieb	Diesel	140	190	Nov 2019	-	2024-03-01	137173
Mercedes-benz	Cabriolet	220 SEB	Cabriolet	Heckantrieb	Benzin	88	120	Sep 1961	Aug 1965	2024-03-01	137175


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 100 个输入 Ktype 的首轮物理外廓聚类，优先复用跨批次缓存尺寸组。
* 本轮新建并闭合 15 个尺寸组，覆盖 Golf III/IV 商用版、Corsa F、Korando C300、CX-30、Kamiq、Discovery Sport facelift、BMW F44、Porsche 718/911 及 Mercedes-Benz W111。Porsche 相关三维已按官方技术资料核对，其他新建组的直接来源均已落入下方 `SourceURL`。
* 多轴距、多车顶商用车暂不建立猜测性派生行；保留基础 Ktype 并标记具体 PENDING 原因。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：86
* READY 映射行：102
* PENDING Ktype／映射行：14
* 已引用尺寸组：58

  * 本轮首次创建：15
  * 跨批次缓存复用：43
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136868_van_m	136868	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M短轴货运外廓。	READY
136868_van_xl	136868	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL长轴货运外廓。	READY
136868_mpv_m	136868	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M短轴乘用外廓。	READY
136868_mpv_xl	136868	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL长轴乘用外廓。	READY
136872	136872	MPV	Boxer III facelift	250			LOW	候选含多种车长、车顶及客车座舱外廓。	PENDING: 需闭合Bus车型的长度和车顶分支
136878_compact	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	MEDIUM	Compact车长分支。	READY
136878_medium	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	MEDIUM	Medium车长分支。	READY
136878_long	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	MEDIUM	Long车长分支。	READY
136903	136903	Pickup	Amarok I facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH		READY
136915	136915	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136916	136916	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
136917	136917	Wagon	C-Class W204 facelift	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH		READY
136918	136918	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136921	136921	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136927	136927	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136928	136928	Van	Golf III	1H1	3	EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136929	136929	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136931	136931	Van	Golf III	1H1	3	EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136934	136934	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136938	136938	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136939	136939	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136941	136941	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136949	136949	Pickup	Transporter T5				LOW	候选含单排、双排及不同轴距底盘外廓。	PENDING: 需闭合CNG底盘驾驶室分支
136950	136950	MPV	Transporter T5	7H			LOW	候选含短轴和长轴Bus外廓。	PENDING: 需闭合Bus轴距分支
136952_compact	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	MEDIUM	Compact车长分支。	READY
136952_medium	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	MEDIUM	Medium车长分支。	READY
136952_long	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	MEDIUM	Long车长分支。	READY
136956	136956	Van	Trafic III	X82			LOW	候选含L1/L2及H1/H2厢式外廓。	PENDING: 需闭合车长和车顶分支
136963	136963	Hatchback	Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
136964	136964	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136965	136965	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136966	136966	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136967	136967	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136992	136992	Pickup	Musso Q200	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH		READY
136993	136993	Pickup	Musso Q200	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH		READY
136994	136994	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136995	136995	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136996	136996	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
137004	137004	MPV	Crafter II				LOW	候选含多种车长和车顶的4Motion Bus外廓。	PENDING: 需闭合Bus车长和车顶分支
137007	137007	Pickup	Sprinter VS30	907			LOW	候选含单排、双排及多种轴距底盘外廓。	PENDING: 需闭合3-T底盘驾驶室分支
137008	137008	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH		READY
137009	137009	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH		READY
137021	137021	MPV	Sprinter W906	906			LOW	候选含多种轴距和车顶Bus外廓。	PENDING: 需闭合316 NGT Bus分支
137022	137022	Pickup	Gladiator JT	JT	4		MEDIUM	候选外廓受车顶和悬架配置影响。	PENDING: 需确认欧洲3.6 VVT标准外廓
137026	137026	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
137029	137029	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
137031	137031	Van	Boxer III facelift	250			LOW	候选含L1-L4及不同车顶厢式外廓。	PENDING: 需闭合厢式车长和车顶分支
137032	137032	Van	Boxer III facelift	250			LOW	候选含L1-L4及不同车顶厢式外廓。	PENDING: 需闭合厢式车长和车顶分支
137033	137033	Van	Boxer III facelift	250			LOW	候选含L1-L4及不同车顶厢式外廓。	PENDING: 需闭合厢式车长和车顶分支
137035	137035	MPV	Boxer III facelift	250			LOW	候选含多种车长、车顶及客车座舱外廓。	PENDING: 需闭合Bus车型的长度和车顶分支
137036	137036	SUV	Bentayga I		5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
137037	137037	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
137038	137038	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
137040	137040	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
137042	137042	SUV	Levante I		5	EU-MASERATI-LEVANTE-I-SUV-01	HIGH		READY
137043_standard	137043	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137043_long	137043	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	Long车长分支。	READY
137046	137046	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137047	137047	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137048	137048	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137049	137049	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137050	137050	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137051	137051	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137056	137056	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137058	137058	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137059	137059	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137060	137060	Coupe	718 Cayman	982	2	EU-PORSCHE-718-982-CAYMAN-GT4-COUPE-01	HIGH	GT4外廓。	READY
137061	137061	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137062	137062	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
137063	137063	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
137085	137085	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137086	137086	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137088	137088	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	S4 TDI facelift外廓。	READY
137089	137089	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	HIGH	S4 TDI facelift外廓。	READY
137090	137090	Sedan	A4 B9 2018 update	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	MEDIUM	2018款外观更新后的外廓。	READY
137091_xs_low	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS低顶外廓。	READY
137091_xs_high	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS高顶外廓。	READY
137091_m_low	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M低顶外廓。	READY
137091_m_high	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M高顶外廓。	READY
137091_xl	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL外廓。	READY
137093	137093	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
137096_standard	137096	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137096_long	137096	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	Long车长分支。	READY
137097_standard	137097	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137097_long	137097	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	Long车长分支。	READY
137101_standard	137101	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137101_long	137101	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	Long车长分支。	READY
137107_m	137107	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	M车长分支。	READY
137107_xl	137107	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	XL车长分支。	READY
137109	137109	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
137110	137110	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137111	137111	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137112	137112	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137113	137113	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137114	137114	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137118	137118	SUV	Beijing X3		5		LOW	候选车型资料尚未闭合不含后视镜宽度。	PENDING: 需确认代际代码及完整三维
137129	137129	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH		READY
137130	137130	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137131	137131	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH		READY
137133	137133	Convertible	718 Spyder	982	2	EU-PORSCHE-718-982-SPYDER-CONVERTIBLE-01	HIGH	Spyder外廓。	READY
137134	137134	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137136	137136	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137137	137137	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137140	137140	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
137144	137144	Coupe	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH	GT外廓。	READY
137145	137145	Convertible	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	HIGH	GT外廓。	READY
137146	137146	Convertible	911 991.2	991.2	2	EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	HIGH	375 kW的4.0版本对应Speedster外廓。	READY
137161	137161	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-COUPE-01	HIGH	Carrera基础版外廓。	READY
137163	137163	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	HIGH	Carrera基础版外廓。	READY
137165	137165	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
137167	137167	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
137169	137169	Pickup	Talento II	X82			LOW	候选含不同轴距及驾驶室底盘外廓。	PENDING: 需闭合Pritsche/Fahrgestell分支
137170	137170	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137172	137172	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137173	137173	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137175	137175	Convertible	W111	111.023	2	EU-MERCEDES-BENZ-W111-220-SEB-CABRIOLET-01	HIGH	220 SEb Cabriolet外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	4149	1735	1439	Volkswagen Golf IV press pack; Auto-Data Golf IV 1.9 TDI 4motion	https://www.vwaudiforum.co.uk/forum/images/textdocuments/Golf_GTI%20Press%20pack.pdf;https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-115hp-4motion-8675
EU-VW-GOLF-III-1H5-VAN-WAGON-01	4340	1695	1430	Auto-Data Golf III Variant; Volkswagen Newsroom Golf III Variant	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880;https://www.volkswagen-newsroom.com/en/golf-3-variant-19931999-19519
EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	4020	1695	1425	Volkswagen Newsroom Golf III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433	Opel Stellantis Media Corsa launch	https://www.media.stellantis.com/pt-pt/opel/press/nova-geracao-opel-corsa-chega-a-portugal
EU-SSANGYONG-KORANDO-C300-SUV-01	4450	1870	1620	KGM Finland Korando MY2020 technical data; GoAuto Korando technical report	https://www.kgm-auto.fi/wp-content/uploads/2020/01/KORANDO-2020-TEKNISET-TIEDOT-2020-1.pdf;https://www.goauto.com.au/future-models/ssangyong/geneva-show-ssangyong-details-new-korando-suv/2019-03-06/77912.html
EU-MAZDA-CX-30-DM-SUV-01	4395	1795	1540	Mazda CX-30 official price and specification guide	https://media-assets.mazda.eu/raw/upload/mazdach/globalassets/pdfs2/1---pricelists/fr/2023-06/pl_cx-30_230501_pdf_20303_2401_f5.pdf?rnd=49c81d
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531	Škoda Storyboard KAMIQ launch	https://www.skoda-storyboard.com/en/press-releases/skoda-kamiq-the-new-city-suv/
EU-PORSCHE-718-982-CAYMAN-GT4-COUPE-01	4456	1801	1269	Porsche 718 Cayman GT4 official technical data	https://newsroom.porsche.com/dam/jcr%3A9d46f6de-fbb6-42d8-b474-7295ec4e7e96/PAG_718_Cayman_GT4_EN.pdf
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	4597	2069	1727	Land Rover Discovery Sport official brochure	https://www.landrover.com/content/dam/lrdx/pdfs/xi/brochures/Land-Rover-Discovery-Sport-Brochure-1L5502310000BXXEN03P.pdf
EU-PORSCHE-718-982-SPYDER-CONVERTIBLE-01	4430	1801	1258	Porsche 718 Spyder official technical data	https://newsroom.porsche.com/dam/jcr%3A8cd0b4f4-fe57-4a2f-aa76-ff0185a0164c/PAG_718_Spyder_EN.pdf
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250	Porsche 911 Speedster official infographic	https://newsroom.porsche.com/dam/jcr%3Aaa72c9d1-2b18-48d7-8538-fea6944cddc2/PORSCHE_Infografic_911_Speedster_EN.pdf
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298	Porsche 911 Carrera official technical data	https://newsroom.porsche.com/dam/jcr%3A5f3af6f6-7e71-41c1-85ed-51f215261b42/PAG_911Carrera_EN.pdf
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297	Porsche 911 Carrera Cabriolet official technical data	https://newsroom.porsche.com/dam/jcr%3A8ef847b3-4a91-4111-b2e6-1656ce3e045a/PAG_911CarreraCabriolet_EN.pdf
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group PressClub 2 Series Gran Coupé launch	https://www.press.bmwgroup.com/global/article/detail/T0301580EN/the-first-ever-bmw-2-series-gran-coupe?language=en
EU-MERCEDES-BENZ-W111-220-SEB-CABRIOLET-01	4880	1845	1445	Mercedes-Benz Public Archive 220 SEb Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-SEb-Cabriolet.xhtml?oid=4628
```

## 下一步优先处理

1. 批量闭合 Peugeot Boxer 的 Bus 与 Van 车长／车顶矩阵，同时解决 Ktype `136872`、`137031`、`137032`、`137033`、`137035`。
2. 闭合 Transporter T5、Trafic III、Crafter II、Sprinter 和 Talento 的轴距、车顶与驾驶室分支。
3. 补齐 Gladiator JT 欧洲标准外廓及 Beijing X3 的可追溯不含后视镜宽度。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮仅处理上一轮 PENDING；既有 READY 映射和缓存尺寸组未重复抓取、未重复输出。
* 已闭合 Peugeot Boxer 120/140 的对应外廓矩阵、Renault Trafic III 2.0 dCi 145 的四种车长/车顶组合、Beijing X3，以及 Fiat Talento L2 Platform Cab。Boxer 资料明确列出发动机对应配置及不含后视镜宽度；Trafic 官方资料明确列出 145 车型的 L1H1、L1H2、L2H1、L2H2 分支。([Charters Citroen][1])
* Ktype `137169` 的 Talento Platform Cab 长度和高度来自 Fiat 官方车型行，宽度使用同一 X82 平台驾驶室的官方 Renault Platform Cab 数据闭合。
* 本轮将 7 个 Ktype 从 PENDING 转为 READY，新建 13 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：93
* PENDING Ktype：7
* READY 映射行：117
* PENDING 映射行：7
* 当前映射总行数：124
* 已确认并引用尺寸组：71
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136872	136872	MPV	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2 Window Van外廓。	READY
136956_l1h1	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1外廓。	READY
136956_l1h2	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2外廓。	READY
136956_l2h1	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1外廓。	READY
136956_l2h2	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2外廓。	READY
137031	137031	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1外廓。	READY
137032_l2h1	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1外廓。	READY
137032_l2h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2外廓。	READY
137032_l3h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2外廓。	READY
137032_l3h3	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3外廓。	READY
137032_l4h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2外廓。	READY
137032_l4h3	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3外廓。	READY
137035	137035	MPV	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Window Van外廓。	READY
137118	137118	SUV	Beijing X3 I		5	EU-BEIJING-X3-I-SUV-01	MEDIUM	第二代X3/X35车身。	READY
137169	137169	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	MEDIUM	L2 Platform Cab外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	5413	2050	2254	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-BEIJING-X3-I-SUV-01	4325	1830	1640	BAIC Global X35 official model page	https://www.baicglobal.com/models/21
EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	5248	1956	1953	Fiat Professional Range price list December 2016; Renault Trafic Van brochure July 2017	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
```

## 下一步优先处理

1. 闭合 VW Transporter T5 CNG 的底盘驾驶室及 Bus 轴距分支：`136949`、`136950`。
2. 批量闭合 Crafter II、Sprinter VS30/W906 的 Bus、底盘驾驶室车长和车顶组合：`137004`、`137007`、`137021`。
3. 确认 Boxer BlueHDi 165 实际适配的厢式车配置矩阵：`137033`。
4. 闭合 Gladiator JT 的硬顶、软顶及特殊悬架高度分支：`137022`。

推进信号：CONTINUE

[1]: https://d1amhj1m505d5v.cloudfront.net/wp-content/uploads/sites/15/2020/07/peugeot-boxer-van-price-specifications-brochure-july-2020.pdf "PEUGEOT Boxer MY D0 MPC Effective 1st July 2020 BLACK TEXT (WLTP fluctuations included).xlsx"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮将 6 个 Ktype 从 PENDING 转为 READY，仅剩 `137004` 尚未闭合。
* 已闭合 Transporter T5 底盘驾驶室与 Bus 的轴距/车顶分支，共新建 7 个尺寸组。([Allegro][1])
* 已闭合 Sprinter VS30 单排底盘 L2/L3、Sprinter W906 `906.733` Bus，以及 Gladiator JT 的标准悬架/Rubicon与软硬顶分支，共新建 7 个尺寸组。([JMS Fahrzeugteile][2])
* Boxer BlueHDi 165 已关联上一轮创建的 6 个既有尺寸组，本轮未重复输出这些尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：137
* PENDING 映射行：1
* 当前映射总行数：138
* 已确认并引用尺寸组：85
* 本轮首次创建尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136949_scab	136949	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-SCAB-LWB-01	MEDIUM	单排驾驶室长轴底盘外廓。	READY
136949_dcab	136949	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-CHASSIS-DCAB-LWB-01	MEDIUM	双排驾驶室长轴底盘外廓。	READY
136950_swb_lowroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
136950_swb_mediumroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶Bus外廓。	READY
136950_lwb_lowroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus外廓。	READY
136950_lwb_mediumroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
136950_lwb_highroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
137007_l2	137007	Pickup	Sprinter VS30	907.221	2	EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L2-01	MEDIUM	L2单排驾驶室底盘外廓。	READY
137007_l3	137007	Pickup	Sprinter VS30	907.223	2	EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L3-01	MEDIUM	L3单排驾驶室底盘外廓。	READY
137021	137021	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-906733-BUS-01	HIGH	906.733中轴Bus外廓。	READY
137022_hardtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-HARDTOP-01	HIGH	标准悬架硬顶外廓。	READY
137022_softtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-SOFTTOP-01	HIGH	标准悬架软顶外廓。	READY
137022_rubicon_hardtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-HARDTOP-01	HIGH	Rubicon悬架硬顶外廓。	READY
137022_rubicon_softtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-SOFTTOP-01	HIGH	Rubicon悬架软顶外廓。	READY
137033_l2h1	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1外廓。	READY
137033_l2h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2外廓。	READY
137033_l3h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2外廓。	READY
137033_l3h3	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3外廓。	READY
137033_l4h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2外廓。	READY
137033_l4h3	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T5-CHASSIS-SCAB-LWB-01	5292	1904	1949	Volkswagen T5.II Transporter specifications brochure	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-CHASSIS-DCAB-LWB-01	5292	1904	1963	Volkswagen T5.II Transporter specifications brochure	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-BUS-SWB-LOWROOF-01	4892	1904	1990	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-SWB-MEDIUMROOF-01	4892	1904	2176	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-LOWROOF-01	5292	1904	1990	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-MEDIUMROOF-01	5292	1904	2176	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-HIGHROOF-01	5292	1904	2476	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L2-01	5886	2020	2288	Mercedes-Benz Sprinter chassis brochure; Mercedes-Benz Sprinter technical data	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf;https://www.mercedesbenzvans.co.nz/static/pdfs/sprinter-panel.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L3-01	6696	2020	2280	Mercedes-Benz Sprinter chassis brochure; Mercedes-Benz Sprinter technical data	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf;https://www.mercedesbenzvans.co.nz/static/pdfs/sprinter-panel.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-906733-BUS-01	5910	1993	2415	Mercedes-Benz Sprinter Traveliner brochure; AutoScout24 Sprinter 316 NGT technical data	https://xr793.com/wp-content/uploads/2022/12/2009-Mercedes-Benz-Sprinter-Traveliner-UK.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/sprinter/316-ngt-sprinter-906-733-monovalent-2010-2018-kombi-benzin-gas/
EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-HARDTOP-01	5539	1875	1857	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-SOFTTOP-01	5539	1875	1907	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-HARDTOP-01	5539	1875	1882	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-SOFTTOP-01	5539	1875	1933	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
```

## 下一步优先处理

1. 仅处理 Ktype `137004`：闭合 Crafter II `SYI/SYJ`、130 kW 4Motion Bus 的准确车长和车顶分支。
2. 闭合后立即执行一次机械检查；若 PENDING 归零，下一轮直接输出两张最终完整 TSV、两个指定下载链接和 `COMPLETE`。

推进信号：CONTINUE

[1]: https://allegro.pl/produkt/vika-11031831601-waz-wentylacja-skrzyni-korbowej-74f91ca7-6f58-4e3b-8e49-446cf0565dfe?utm_source=chatgpt.com "Vika 11031831601 Wąż, wentylacja skrzyni korbowej • Cena, Opinie - Allegro"
[2]: https://www.jms-fahrzeugteile.de/Motor-Getriebetechnik/DTE-BoostrPro/MERCEDES-BENZ/SPRINTER/SPRINTER-3-t-Pritsche-Fahrgestell-9/DTE-BoostPro-passend-fuer-MERCEDES-BENZ-SPRINTER-3-t-Pritsche-Fahrgestell-910-907-2018%3A%3A2170830.html?utm_source=chatgpt.com "DTE BoostPro passend für MERCEDES-BENZ SPRINTER 3-t Pritsche/Fahrgestell (910, 907) 2018-..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4101-4200_ktype_dimension_mapping_final.tsv
- all_4101-4200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 最后一个 PENDING Ktype `137004` 已闭合，分别关联既有 Crafter II L3H2、L3H3 和 L4H3 尺寸组。
* 本轮未新建或修改尺寸组。
* 已完成机械检查：表头正确、140 个 `id` 唯一、88 个尺寸组唯一、全部映射引用闭合、无孤立尺寸组、尺寸与来源字段完整。
* 当前批次达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：140
* PENDING 映射：0
* DIMENSION_GROUP：88
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136868_van_m	136868	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-M-01	MEDIUM	M短轴货运外廓。	READY
136868_van_xl	136868	Van	Combo E	K9		EU-OPEL-COMBO-E-K9-VAN-XL-01	MEDIUM	XL长轴货运外廓。	READY
136868_mpv_m	136868	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-M-MPV-01	MEDIUM	M短轴乘用外廓。	READY
136868_mpv_xl	136868	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-LIFE-XL-MPV-01	MEDIUM	XL长轴乘用外廓。	READY
136872	136872	MPV	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2 Window Van外廓。	READY
136878_compact	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	MEDIUM	Compact车长分支。	READY
136878_medium	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	MEDIUM	Medium车长分支。	READY
136878_long	136878	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	MEDIUM	Long车长分支。	READY
136903	136903	Pickup	Amarok I facelift	2H	4	EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	HIGH		READY
136915	136915	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136916	136916	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH		READY
136917	136917	Wagon	C-Class W204 facelift	S204	5	EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	HIGH		READY
136918	136918	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136921	136921	Van	Golf IV	1J1	3	EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136927	136927	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136928	136928	Van	Golf III	1H1	3	EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136929	136929	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136931	136931	Van	Golf III	1H1	3	EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	MEDIUM	三门厢式掀背外廓。	READY
136934	136934	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136938	136938	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136939	136939	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136941	136941	Van	Golf III Variant	1H5	5	EU-VW-GOLF-III-1H5-VAN-WAGON-01	MEDIUM	五门厢式旅行车外廓。	READY
136949_scab	136949	Pickup	Transporter T5		2	EU-VW-TRANSPORTER-T5-CHASSIS-SCAB-LWB-01	MEDIUM	单排驾驶室长轴底盘外廓。	READY
136949_dcab	136949	Pickup	Transporter T5		4	EU-VW-TRANSPORTER-T5-CHASSIS-DCAB-LWB-01	MEDIUM	双排驾驶室长轴底盘外廓。	READY
136950_swb_lowroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶Bus外廓。	READY
136950_swb_mediumroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-SWB-MEDIUMROOF-01	MEDIUM	短轴中顶Bus外廓。	READY
136950_lwb_lowroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-LOWROOF-01	MEDIUM	长轴低顶Bus外廓。	READY
136950_lwb_mediumroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-MEDIUMROOF-01	MEDIUM	长轴中顶Bus外廓。	READY
136950_lwb_highroof	136950	MPV	Transporter T5			EU-VW-TRANSPORTER-T5-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶Bus外廓。	READY
136952_compact	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	MEDIUM	Compact车长分支。	READY
136952_medium	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	MEDIUM	Medium车长分支。	READY
136952_long	136952	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	MEDIUM	Long车长分支。	READY
136956_l1h1	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	HIGH	L1H1外廓。	READY
136956_l1h2	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	HIGH	L1H2外廓。	READY
136956_l2h1	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	HIGH	L2H1外廓。	READY
136956_l2h2	136956	Van	Trafic III facelift	X82		EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	HIGH	L2H2外廓。	READY
136963	136963	Hatchback	Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH		READY
136964	136964	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136965	136965	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136966	136966	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136967	136967	SUV	Korando C300	C300	5	EU-SSANGYONG-KORANDO-C300-SUV-01	HIGH		READY
136992	136992	Pickup	Musso Q200	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH		READY
136993	136993	Pickup	Musso Q200	Q200	4	EU-SSANGYONG-MUSSO-Q200-PICKUP-01	HIGH		READY
136994	136994	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136995	136995	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136996	136996	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
137004_mwb_lowroof	137004	MPV	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	HIGH	中轴普通顶Bus外廓。	READY
137004_mwb_highroof	137004	MPV	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	HIGH	中轴高顶Bus外廓。	READY
137004_lwb_highroof	137004	MPV	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	HIGH	长轴高顶Bus外廓。	READY
137007_l2	137007	Pickup	Sprinter VS30	907.221	2	EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L2-01	MEDIUM	L2单排驾驶室底盘外廓。	READY
137007_l3	137007	Pickup	Sprinter VS30	907.223	2	EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L3-01	MEDIUM	L3单排驾驶室底盘外廓。	READY
137008	137008	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH		READY
137009	137009	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	HIGH		READY
137021	137021	MPV	Sprinter W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-906733-BUS-01	HIGH	906.733中轴Bus外廓。	READY
137022_hardtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-HARDTOP-01	HIGH	标准悬架硬顶外廓。	READY
137022_softtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-SOFTTOP-01	HIGH	标准悬架软顶外廓。	READY
137022_rubicon_hardtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-HARDTOP-01	HIGH	Rubicon悬架硬顶外廓。	READY
137022_rubicon_softtop	137022	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-SOFTTOP-01	HIGH	Rubicon悬架软顶外廓。	READY
137026	137026	Coupe	C-Class C205 facelift	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
137029	137029	Convertible	C-Class A205 facelift	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
137031	137031	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1外廓。	READY
137032_l2h1	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1外廓。	READY
137032_l2h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2外廓。	READY
137032_l3h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2外廓。	READY
137032_l3h3	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3外廓。	READY
137032_l4h2	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2外廓。	READY
137032_l4h3	137032	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3外廓。	READY
137033_l2h1	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	HIGH	L2H1外廓。	READY
137033_l2h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	HIGH	L2H2外廓。	READY
137033_l3h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	HIGH	L3H2外廓。	READY
137033_l3h3	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	HIGH	L3H3外廓。	READY
137033_l4h2	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	HIGH	L4H2外廓。	READY
137033_l4h3	137033	Van	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	HIGH	L4H3外廓。	READY
137035	137035	MPV	Boxer III facelift	250		EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	HIGH	L1H1 Window Van外廓。	READY
137036	137036	SUV	Bentayga I		5	EU-BENTLEY-BENTAYGA-I-SUV-01	HIGH		READY
137037	137037	SUV	X7 G07	G07	5	EU-BMW-X7-G07-SUV-01	HIGH		READY
137038	137038	SUV	Touareg III	CR	5	EU-VW-TOUAREG-III-CR-SUV-01	HIGH		READY
137040	137040	Hatchback	Mazda 3 IV	BP	5	EU-MAZDA-3-IV-BP-HATCHBACK-01	HIGH		READY
137042	137042	SUV	Levante I		5	EU-MASERATI-LEVANTE-I-SUV-01	HIGH		READY
137043_standard	137043	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137043_long	137043	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	长车长分支。	READY
137046	137046	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137047	137047	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137048	137048	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137049	137049	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137050	137050	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137051	137051	SUV	CX-30 I	DM	5	EU-MAZDA-CX-30-DM-SUV-01	HIGH		READY
137056	137056	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137058	137058	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137059	137059	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH		READY
137060	137060	Coupe	718 Cayman	982	2	EU-PORSCHE-718-982-CAYMAN-GT4-COUPE-01	HIGH	GT4外廓。	READY
137061	137061	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137062	137062	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
137063	137063	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
137085	137085	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137086	137086	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
137088	137088	Wagon	A4 B9 facelift	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	HIGH	S4 TDI facelift外廓。	READY
137089	137089	Sedan	A4 B9 facelift	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-02	HIGH	S4 TDI facelift外廓。	READY
137090	137090	Sedan	A4 B9 2018 update	8W2	4	EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	MEDIUM	2018款外观更新后的外廓。	READY
137091_xs_low	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	MEDIUM	XS低顶外廓。	READY
137091_xs_high	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	MEDIUM	XS高顶外廓。	READY
137091_m_low	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-LOW-01	MEDIUM	M低顶外廓。	READY
137091_m_high	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	MEDIUM	M高顶外廓。	READY
137091_xl	137091	Van	Jumpy III	K0		EU-CITROEN-JUMPY-III-VAN-XL-01	MEDIUM	XL外廓。	READY
137093	137093	SUV	Q5 FY	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
137096_standard	137096	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137096_long	137096	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	长车长分支。	READY
137097_standard	137097	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137097_long	137097	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	长车长分支。	READY
137101_standard	137101	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	MEDIUM	Standard车长分支。	READY
137101_long	137101	MPV	Rifter I	K9	5	EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	MEDIUM	长车长分支。	READY
137107_m	137107	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-M-01	MEDIUM	M车长分支。	READY
137107_xl	137107	MPV	Berlingo III	K9	5	EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	MEDIUM	XL车长分支。	READY
137109	137109	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
137110	137110	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137111	137111	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137112	137112	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137113	137113	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137114	137114	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	HIGH		READY
137118	137118	SUV	Beijing X3 I		5	EU-BEIJING-X3-I-SUV-01	MEDIUM	第二代X3/X35车身。	READY
137129	137129	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH		READY
137130	137130	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137131	137131	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH		READY
137133	137133	Convertible	718 Spyder	982	2	EU-PORSCHE-718-982-SPYDER-CONVERTIBLE-01	HIGH	Spyder外廓。	READY
137134	137134	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137136	137136	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137137	137137	Sedan	Mondeo V facelift	CD391	4	EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	HIGH		READY
137140	137140	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
137144	137144	Coupe	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	HIGH	GT外廓。	READY
137145	137145	Convertible	Mustang S550 facelift	S550	2	EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	HIGH	GT外廓。	READY
137146	137146	Convertible	911 991.2	991.2	2	EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	HIGH	375 kW的4.0版本对应Speedster外廓。	READY
137161	137161	Coupe	911 992	992	2	EU-PORSCHE-911-992-CARRERA-COUPE-01	HIGH	Carrera基础版外廓。	READY
137163	137163	Convertible	911 992	992	2	EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	HIGH	Carrera基础版外廓。	READY
137165	137165	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
137167	137167	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
137169	137169	Pickup	Talento II	X82		EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	MEDIUM	L2 Platform Cab外廓。	READY
137170	137170	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137172	137172	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137173	137173	Coupe	2 Series Gran Coupe	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	四门Gran Coupe外廓。	READY
137175	137175	Convertible	W111	111.023	2	EU-MERCEDES-BENZ-W111-220-SEB-CABRIOLET-01	HIGH	220 SEb Cabriolet外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4101-4200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-COMBO-E-K9-VAN-M-01	4403	1848	1796	Opel Combo official press kit	https://www.media.stellantis.com/em-en/opel/press/press-kit-everyday-heroes-in-top-form-the-new-opel-combo-life-and-combo
EU-OPEL-COMBO-E-K9-VAN-XL-01	4753	1848	1812	Opel Combo official press kit	https://www.media.stellantis.com/em-en/opel/press/press-kit-everyday-heroes-in-top-form-the-new-opel-combo-life-and-combo
EU-OPEL-COMBO-E-LIFE-M-MPV-01	4403	1848	1841	Opel Combo official press kit	https://www.media.stellantis.com/em-en/opel/press/press-kit-everyday-heroes-in-top-form-the-new-opel-combo-life-and-combo
EU-OPEL-COMBO-E-LIFE-XL-MPV-01	4753	1848	1880	Opel Combo official press kit	https://www.media.stellantis.com/em-en/opel/press/press-kit-everyday-heroes-in-top-form-the-new-opel-combo-life-and-combo
EU-PEUGEOT-BOXER-III-FACELIFT-L3H2-01	5998	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905	Toyota Proace Verso official product document	https://t1-cms.images.toyota-europe.com/toyotaone/eses/Proace-Verso-configuracion-asientos_tcm-1014-1679401.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890	Toyota Proace Verso official product document	https://t1-cms.images.toyota-europe.com/toyotaone/eses/Proace-Verso-configuracion-asientos_tcm-1014-1679401.pdf
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890	Toyota Proace Verso official product document	https://t1-cms.images.toyota-europe.com/toyotaone/eses/Proace-Verso-configuracion-asientos_tcm-1014-1679401.pdf
EU-VW-AMAROK-I-FACELIFT-DOUBLE-CAB-PICKUP-01	5254	1954	1834	Volkswagen Newsroom Amarok I model archive	https://www.volkswagen-newsroom.com/en/amarok-20102022-19646
EU-VW-GOLF-IV-1J1-VAN-HATCHBACK-01	4149	1735	1439	Volkswagen Golf IV press pack; Auto-Data Golf IV 1.9 TDI 4motion	https://www.vwaudiforum.co.uk/forum/images/textdocuments/Golf_GTI%20Press%20pack.pdf;https://www.auto-data.net/en/volkswagen-golf-iv-1.9-tdi-115hp-4motion-8675
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Opel Crossland X official press material	https://www.media.stellantis.com/em-en/opel/press/stylish-for-the-city-with-suv-coolness
EU-MERCEDES-BENZ-C-KLASSE-S204-WAGON-FACELIFT-01	4606	1770	1459	Mercedes-Benz C-Class official brochure	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-C-Class-UK.pdf
EU-VW-GOLF-III-1H5-VAN-WAGON-01	4340	1695	1430	Auto-Data Golf III Variant; Volkswagen Newsroom Golf III Variant	https://www.auto-data.net/en/volkswagen-golf-iii-variant-generation-1880;https://www.volkswagen-newsroom.com/en/golf-3-variant-19931999-19519
EU-VW-GOLF-III-1H1-VAN-HATCHBACK-01	4020	1695	1425	Volkswagen Newsroom Golf III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-golf-3-profile-19474
EU-VW-TRANSPORTER-T5-CHASSIS-SCAB-LWB-01	5292	1904	1949	Volkswagen T5.II Transporter specifications brochure	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-CHASSIS-DCAB-LWB-01	5292	1904	1963	Volkswagen T5.II Transporter specifications brochure	https://vandimensions.com/media/pages/database/volkswagen/transporter-t5/d326887c85-1626523397/volkswagen_transporter_t5ii_specifications_201403.pdf
EU-VW-TRANSPORTER-T5-BUS-SWB-LOWROOF-01	4892	1904	1990	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-SWB-MEDIUMROOF-01	4892	1904	2176	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-LOWROOF-01	5292	1904	1990	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-MEDIUMROOF-01	5292	1904	2176	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-VW-TRANSPORTER-T5-BUS-LWB-HIGHROOF-01	5292	1904	2476	Volkswagen Transporter vans brochure January 2014	https://blog.le-parnass.com/catalogue_pdf/vw_transporter_vans2014.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465	Renault New Trafic press kit November 2019; Renault Trafic Van brochure July 2017	https://www.press.renault.co.uk/assets/documents/original/17073-RenaultTraficPressKitNovember2019.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433	Opel Stellantis Media Corsa launch	https://www.media.stellantis.com/pt-pt/opel/press/nova-geracao-opel-corsa-chega-a-portugal
EU-SSANGYONG-KORANDO-C300-SUV-01	4450	1870	1620	KGM Finland Korando MY2020 technical data; GoAuto Korando technical report	https://www.kgm-auto.fi/wp-content/uploads/2020/01/KORANDO-2020-TEKNISET-TIEDOT-2020-1.pdf;https://www.goauto.com.au/future-models/ssangyong/geneva-show-ssangyong-details-new-korando-suv/2019-03-06/77912.html
EU-SSANGYONG-MUSSO-Q200-PICKUP-01	5095	1950	1870	KGM Musso Q200 technical specification	https://www.kgm-auto.fi/wp-content/uploads/2019/01/MUSSO-2019-TEKNISET-TIEDOT.pdf
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo Cars official technical specifications	https://www.media.volvocars.com/global/en-gb/models
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars official technical specifications	https://www.media.volvocars.com/global/en-gb/models
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter official catalogue 2017	https://www.tarnow-stegbauer.de/fileadmin/Redaktion/Nutzfahrzeuge/Crafter/VWN-CR-Katalog-KW1017.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter official catalogue 2017	https://www.tarnow-stegbauer.de/fileadmin/Redaktion/Nutzfahrzeuge/Crafter/VWN-CR-Katalog-KW1017.pdf
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Crafter official catalogue 2017	https://www.tarnow-stegbauer.de/fileadmin/Redaktion/Nutzfahrzeuge/Crafter/VWN-CR-Katalog-KW1017.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L2-01	5886	2020	2288	Mercedes-Benz Sprinter chassis brochure; Mercedes-Benz Sprinter technical data	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf;https://www.mercedesbenzvans.co.nz/static/pdfs/sprinter-panel.pdf
EU-MERCEDES-BENZ-SPRINTER-VS30-907-CHASSIS-SCAB-L3-01	6696	2020	2280	Mercedes-Benz Sprinter chassis brochure; Mercedes-Benz Sprinter technical data	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf;https://www.mercedesbenzvans.co.nz/static/pdfs/sprinter-panel.pdf
EU-MERCEDES-BENZ-GLC-X253-AMG-43-SUV-01	4656	1890	1639	Mercedes-Benz official model technical data	https://media.mercedes-benz.com/
EU-MERCEDES-BENZ-SPRINTER-W906-906733-BUS-01	5910	1993	2415	Mercedes-Benz Sprinter Traveliner brochure; AutoScout24 Sprinter 316 NGT technical data	https://xr793.com/wp-content/uploads/2022/12/2009-Mercedes-Benz-Sprinter-Traveliner-UK.pdf;https://www.autoscout24.de/auto/technische-daten/mercedes-benz/sprinter/316-ngt-sprinter-906-733-monovalent-2010-2018-kombi-benzin-gas/
EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-HARDTOP-01	5539	1875	1857	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-STANDARD-SOFTTOP-01	5539	1875	1907	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-HARDTOP-01	5539	1875	1882	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-JEEP-GLADIATOR-JT-PICKUP-RUBICON-SOFTTOP-01	5539	1875	1933	FCA Canada 2020 Jeep Gladiator specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/CN_2020_JP_Gladiator_Specificationsgj6i3ri6qsmjtkrqufrco5r3vp.pdf
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Mercedes-Benz official model technical data	https://media.mercedes-benz.com/
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Mercedes-Benz official model technical data	https://media.mercedes-benz.com/
EU-PEUGEOT-BOXER-III-FACELIFT-L1H1-01	4963	2050	2254	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H1-01	5413	2050	2254	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L2H2-01	5413	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L3H3-01	5998	2050	2760	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H2-01	6363	2050	2522	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-BOXER-III-FACELIFT-L4H3-01	6363	2050	2760	Peugeot Boxer prices and specifications brochure July 2019	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/peugeot-boxer-prices-specifications-brochure-july-2019.pdf
EU-BENTLEY-BENTAYGA-I-SUV-01	5140	1998	1742	Bentley Bentayga official product specification	https://www.bentleymedia.com/en/models/bentayga
EU-BMW-X7-G07-SUV-01	5151	2000	1805	BMW Group PressClub X7 technical specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0285996EN_GB/428163
EU-VW-TOUAREG-III-CR-SUV-01	4878	1984	1702	Volkswagen Newsroom Touareg exterior dimensions	https://www.volkswagen-newsroom.com/en/leading-the-way-the-new-touareg-2405/exterior-design-tailor-made-for-freedom-2416
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435	Mazda3 official specifications	https://uk.mazda-press.com/models/mazda3/
EU-MASERATI-LEVANTE-I-SUV-01	5003	1968	1679	Maserati Levante official technical specifications	https://www.maserati.com/global/en/models/levante
EU-PEUGEOT-RIFTER-I-K9-MPV-STANDARD-01	4403	1848	1878	Peugeot Rifter official press material	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-rifter-action
EU-PEUGEOT-RIFTER-I-K9-MPV-LONG-01	4753	1848	1882	Peugeot Rifter official press material	https://www.media.stellantis.com/em-en/peugeot/press/new-peugeot-rifter-action
EU-MAZDA-CX-30-DM-SUV-01	4395	1795	1540	Mazda CX-30 official price and specification guide	https://media-assets.mazda.eu/raw/upload/mazdach/globalassets/pdfs2/1---pricelists/fr/2023-06/pl_cx-30_230501_pdf_20303_2401_f5.pdf?rnd=49c81d
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531	Škoda Storyboard KAMIQ launch	https://www.skoda-storyboard.com/en/press-releases/skoda-kamiq-the-new-city-suv/
EU-PORSCHE-718-982-CAYMAN-GT4-COUPE-01	4456	1801	1269	Porsche 718 Cayman GT4 official technical data	https://newsroom.porsche.com/dam/jcr%3A9d46f6de-fbb6-42d8-b474-7295ec4e7e96/PAG_718_Cayman_GT4_EN.pdf
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo Cars official technical specifications	https://www.media.volvocars.com/global/en-gb/models
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo Cars official technical specifications	https://www.media.volvocars.com/global/en-gb/models
EU-AUDI-A4-B9-AVANT-WAGON-FACELIFT-02	4762	1847	1435	Audi A4 official catalogue and technical data	https://media.audi.com/is/content/audi/nemo/mu/Catalog/A4_Digitalkatalog_18_2019_01_NEFZ.pdf
EU-AUDI-A4-B9-SEDAN-FACELIFT-02	4762	1847	1428	Audi A4 official catalogue and technical data	https://media.audi.com/is/content/audi/nemo/mu/Catalog/A4_Digitalkatalog_18_2019_01_NEFZ.pdf
EU-AUDI-A4-B9-SEDAN-FACELIFT-2018-01	4738	1842	1428	Audi A4 official catalogue and technical data	https://media.audi.com/is/content/audi/nemo/mu/Catalog/A4_Digitalkatalog_18_2019_01_NEFZ.pdf
EU-CITROEN-JUMPY-III-VAN-XS-LOW-01	4609	1920	1910	Citroën Jumpy official technical brochure	https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumpy
EU-CITROEN-JUMPY-III-VAN-XS-HIGH-01	4609	1920	1950	Citroën Jumpy official technical brochure	https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumpy
EU-CITROEN-JUMPY-III-VAN-M-LOW-01	4959	1920	1899	Citroën Jumpy official technical brochure	https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumpy
EU-CITROEN-JUMPY-III-VAN-M-HIGH-01	4959	1920	1935	Citroën Jumpy official technical brochure	https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumpy
EU-CITROEN-JUMPY-III-VAN-XL-01	5309	1920	1940	Citroën Jumpy official technical brochure	https://www.media.stellantis.com/em-en/citroen/press/new-citroen-jumpy
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Audi Q5 official technical data	https://www.audi-mediacenter.com/en/audi-q5-31
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844	Citroën Berlingo official press kit	https://www.media.stellantis.com/em-en/citroen/press/citroen-reveals-the-3rd-generation-of-berlingo-citroen-s-full-dna-and-enhanced-intelligence-for-even-more-practicality-and-comfort
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849	Citroën Berlingo official press kit	https://www.media.stellantis.com/em-en/citroen/press/citroen-reveals-the-3rd-generation-of-berlingo-citroen-s-full-dna-and-enhanced-intelligence-for-even-more-practicality-and-comfort
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	BMW Group PressClub 1 Series specifications	https://www.press.bmwgroup.com/global/article/detail/T0297558EN/specifications-of-the-all-new-bmw-1-series-valid-from-05/2019?language=en
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	4597	2069	1727	Land Rover Discovery Sport official brochure	https://www.landrover.com/content/dam/lrdx/pdfs/xi/brochures/Land-Rover-Discovery-Sport-Brochure-1L5502310000BXXEN03P.pdf
EU-BEIJING-X3-I-SUV-01	4325	1830	1640	BAIC Global X35 official model page	https://www.baicglobal.com/models/21
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477	Škoda Superb facelift official press kit	https://www.skoda-storyboard.com/en/press-kits/skoda-iv-press-kit/stylish-visual-accents-and-new-technologies-first-skoda-to-feature-full-led-matrix-headlights/
EU-FORD-MONDEO-V-CD391-SEDAN-FACELIFT-01	4871	1852	1482	Ford Mondeo official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469	Škoda Superb facelift official press kit	https://www.skoda-storyboard.com/en/press-kits/skoda-iv-press-kit/stylish-visual-accents-and-new-technologies-first-skoda-to-feature-full-led-matrix-headlights/
EU-PORSCHE-718-982-SPYDER-CONVERTIBLE-01	4430	1801	1258	Porsche 718 Spyder official technical data	https://newsroom.porsche.com/dam/jcr%3A8cd0b4f4-fe57-4a2f-aa76-ff0185a0164c/PAG_718_Spyder_EN.pdf
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-COUPE-01	4789	1916	1382	Ford Mustang official technical specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2019/mustang/2019-mustang-techspecs.pdf
EU-FORD-USA-MUSTANG-S550-FACELIFT-GT-CONVERTIBLE-01	4789	1916	1396	Ford Mustang official technical specifications	https://media.ford.com/content/dam/fordmedia/North%20America/US/product/2019/mustang/2019-mustang-techspecs.pdf
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250	Porsche 911 Speedster official infographic	https://newsroom.porsche.com/dam/jcr%3Aaa72c9d1-2b18-48d7-8538-fea6944cddc2/PORSCHE_Infografic_911_Speedster_EN.pdf
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298	Porsche 911 Carrera official technical data	https://newsroom.porsche.com/dam/jcr%3A5f3af6f6-7e71-41c1-85ed-51f215261b42/PAG_911Carrera_EN.pdf
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297	Porsche 911 Carrera Cabriolet official technical data	https://newsroom.porsche.com/dam/jcr%3A8ef847b3-4a91-4111-b2e6-1656ce3e045a/PAG_911CarreraCabriolet_EN.pdf
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639	Mercedes-Benz official model technical data	https://media.mercedes-benz.com/
EU-FIAT-TALENTO-II-X82-PLATFORM-CAB-L2-01	5248	1956	1953	Fiat Professional Range price list December 2016; Renault Trafic Van brochure July 2017	https://www.media.stellantis.com/uploads/uk/UK/2016/FIAT_Professional/Price_Lists/Fiat_Professional_Range_Price_List_DEC_2016.pdf;https://www.press.renault.co.uk/assets/documents/original/10722-TraficVaneBrochureJuly2017.pdf
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW Group PressClub 2 Series Gran Coupé launch	https://www.press.bmwgroup.com/global/article/detail/T0301580EN/the-first-ever-bmw-2-series-gran-coupe?language=en
EU-MERCEDES-BENZ-W111-220-SEB-CABRIOLET-01	4880	1845	1445	Mercedes-Benz Public Archive 220 SEb Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-SEb-Cabriolet.xhtml?oid=4628
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4101-4200_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3803 行）
- 累计尺寸组：dimension_groups_final.tsv（1614 行）

