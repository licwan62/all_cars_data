# 任务：all 第 1-100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0001__1b28569f


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
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776
EU-FIAT-TIPO-356-SEDAN-01	4532	1792	1497
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655
EU-MASERATI-GHIBLI-II-AM336-CUP-COUPE-01	4223	1775	1300
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590
EU-NISSAN-QASHQAI-II-J11-SUV-PREFL-01	4377	1806	1590
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-C-P12-MPV-01	4656	1884	1685
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ssangyong	Korando	2.2 E-xdi 4WD	Kasten/SUV	Allrad	Diesel	131	178	Jul 2015	-	2024-03-01	142959
Ssangyong	Rexton	E-xdi	Kasten/SUV	Heckantrieb	Diesel	133	181	Jul 2017	-	2024-03-01	142960
Ssangyong	Rexton	E-xdi 4WD	Kasten/SUV	Allrad	Diesel	133	181	Jul 2017	-	2024-03-01	142961
Ssangyong	Rexton	Rx270 XDI 4X4	Kasten/SUV	Allrad	Diesel	118	160	Mar 2011	Apr 2013	2024-03-01	142962
Ssangyong	Rexton	Rx270 XDI 4X4	Kasten/SUV	Allrad	Diesel	132	179	Mar 2011	Apr 2013	2024-03-01	142963
Ssangyong	Rexton	E-xdi	Kasten/SUV	Heckantrieb	Diesel	131	178	Jul 2015	-	2024-03-01	142964
Ssangyong	Rexton	E-xdi Allrad	Kasten/SUV	Allrad	Diesel	131	178	Jul 2015	-	2024-03-01	142965
Ssangyong	Rodius ii van	E-xdi	Kasten/SUV	Heckantrieb	Diesel	131	178	Jul 2015	-	2024-03-01	142966
Ssangyong	Rodius ii van	E-xdi 4WD	Kasten/SUV	Allrad	Diesel	131	178	Jul 2015	-	2024-03-01	142967
Ssangyong	Xlv van	E-xgi	Kasten/SUV	Frontantrieb	Benzin	94	128	Dec 2016	-	2024-03-01	142968
Ssangyong	Xlv van	E-xgi Allrad	Kasten/SUV	Allrad	Benzin	94	128	Dec 2016	-	2024-03-01	142969
Ssangyong	Xlv van	E-xdi	Kasten/SUV	Frontantrieb	Diesel	85	116	Dec 2016	-	2024-03-01	142970
Ssangyong	Xlv van	E-xdi Allrad	Kasten/SUV	Allrad	Diesel	85	116	Dec 2016	-	2024-03-01	142971
Toyota	Rav 4 iv van	2.0 Vvti 4WD	Kasten/SUV	Allrad	Benzin	111	151	Dec 2012	Nov 2018	2024-03-01	142972
Toyota	Rav 4 iv van	2.0 Vvti 4WD	Kasten/SUV	Allrad	Benzin	112	152	Dec 2012	Nov 2018	2024-03-01	142973
Toyota	Rav 4 iv van	2.0 D4D	Kasten/SUV	Frontantrieb	Diesel	91	124	Dec 2012	Nov 2018	2024-03-01	142974
Toyota	Rav 4 iv van	D4D 4WD	Kasten/SUV	Allrad	Diesel	91	124	Nov 2013	Nov 2018	2024-03-01	142975
Toyota	Rav 4 iv van	2.0 D4D	Kasten/SUV	Frontantrieb	Diesel	105	143	Oct 2015	Nov 2018	2024-03-01	142976
Toyota	Rav 4 iv van	2.2 D4D 4WD	Kasten/SUV	Allrad	Diesel	110	150	Dec 2012	Nov 2018	2024-03-01	142977
Fiat	Tipo	1.6 Multijet	Schrägheck	Frontantrieb	Diesel	96	131	Nov 2020	-	2024-03-01	142978
Toyota	Rav 4 v van	2.0 Vvti	Kasten/SUV	Frontantrieb	Benzin	129	175	Dec 2018	-	2024-03-01	142979
Toyota	Rav 4 v van	2.0 Vvti AWD	Kasten/SUV	Allrad	Benzin	129	175	Dec 2018	-	2024-03-01	142980
Fiat	Tipo	1.6 Multijet	Kombi	Frontantrieb	Diesel	96	131	Nov 2020	-	2024-03-01	142981
Toyota	Rav 4 v van	2.5 Hybrid	Kasten/SUV	Frontantrieb	Benzin/Elektro	160	218	Dec 2018	-	2024-03-01	142982
Toyota	Rav 4 v van	2.5 Hybrid AWD	Kasten/SUV	Allrad	Benzin/Elektro	163	222	Dec 2018	-	2024-03-01	142983
Toyota	Verso	Vvti	Kasten/Großraumlimousine	Frontantrieb	Benzin	97	132	Apr 2009	Aug 2018	2024-03-01	142989
Toyota	Verso	Vvti	Kasten/Großraumlimousine	Frontantrieb	Benzin	108	147	Apr 2009	Aug 2018	2024-03-01	142990
Hyundai	Santa fe iv	2.2 Crdi Htrac	SUV	Allrad	Diesel	148	201	Nov 2020	-	2024-03-01	142991
Hyundai	Santa fe iv	2.2 Crdi	SUV	Frontantrieb	Diesel	148	201	Nov 2020	-	2024-03-01	142992
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	82	112	Nov 2013	Aug 2018	2024-03-01	142993
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	91	124	Nov 2012	Aug 2018	2024-03-01	142994
Toyota	Verso	D4D	Kasten/Großraumlimousine	Frontantrieb	Diesel	130	177	Apr 2009	Aug 2018	2024-03-01	142995
Volvo	Xc60 i van	D3	Kasten/SUV	Frontantrieb	Diesel	100	136	Sep 2013	Dec 2015	2024-03-01	142996
Volvo	Xc60 i van	D4	Kasten/SUV	Frontantrieb	Diesel	120	163	Sep 2013	Feb 2017	2024-03-01	142997
Volvo	Xc60 i van	D4 AWD	Kasten/SUV	Allrad	Diesel	120	163	Sep 2013	Feb 2017	2024-03-01	142998
Volvo	Xc60 i van	D5 AWD	Kasten/SUV	Allrad	Diesel	158	215	Sep 2013	Feb 2017	2024-03-01	142999
KIA	Sorento iv	1.6 T-gdi Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	195	265	Nov 2020	-	2025-04-01	143001
Nissan	Qashqai ii	1.3 Dig-t	SUV	Frontantrieb	Benzin	116	158	Oct 2020	Apr 2021	2026-06-01	143002
Maserati	Ghibli	3.8 V8	Stufenheck	Heckantrieb	Benzin	427	581	Oct 2020	-	2024-03-01	143003
VW	Sharan	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	110	150	May 2010	Nov 2015	2024-03-01	143004
VW	Sharan	2.0 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	147	200	Dec 2010	Nov 2015	2024-03-01	143005
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	May 2011	Nov 2015	2024-03-01	143006
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	100	136	May 2010	May 2011	2024-03-01	143007
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	May 2010	Nov 2015	2024-03-01	143008
VW	Sharan	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	125	170	Aug 2010	Jan 2013	2024-03-01	143009
Maserati	Quattroporte vi	3.8 V8	Stufenheck	Heckantrieb	Benzin	427	581	Oct 2020	-	2024-03-01	143010
Audi	E-Tron	S Quattro	SUV	Allrad	Elektro	370	503	Sep 2020	Jul 2023	2026-03-01	143011
VW	Sharan	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	85	116	Sep 1996	Jul 2002	2024-03-01	143012
VW	Sharan	2.8 VR6	Kasten/Großraumlimousine	Frontantrieb	Benzin	128	174	Sep 1996	Apr 2000	2024-03-01	143013
VW	Sharan	2.8 VR6	Kasten/Großraumlimousine	Frontantrieb	Benzin	150	204	Aug 2001	May 2003	2024-03-01	143014
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Sep 1996	May 2003	2024-03-01	143015
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	81	110	Sep 1996	May 2003	2024-03-01	143016
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Apr 2000	Mar 2010	2024-03-01	143017
VW	Sharan	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	96	131	Nov 2002	May 2003	2024-03-01	143018
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	90	122	Aug 2010	May 2011	2024-03-01	143019
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	110	150	May 2008	May 2010	2024-03-01	143020
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	118	160	Sep 2012	Jul 2018	2024-03-01	143021
VW	Tiguan	1.4 TSI 4motion	Kasten/SUV	Allrad	Benzin	118	160	Sep 2012	Jul 2018	2024-03-01	143022
BMW	8	840 I	Coupe	Heckantrieb	Benzin	245	333	Nov 2020	-	2024-03-01	143023
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	245	333	Nov 2020	-	2024-03-01	143024
BMW	8	840 I	Cabriolet	Heckantrieb	Benzin	245	333	Nov 2020	-	2024-03-01	143025
BMW	8	840 I Xdrive	Cabriolet	Allrad	Benzin	245	333	Nov 2020	-	2024-03-01	143026
BMW	8	840 I	Coupe	Heckantrieb	Benzin	245	333	Nov 2020	-	2024-03-01	143027
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	245	333	Nov 2020	-	2024-03-01	143028
BMW	X7	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	245	333	Dec 2020	-	2024-03-01	143029
BMW	X6	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	245	333	Dec 2020	Mar 2023	2024-03-01	143030
BMW	X5	Xdrive 40 I Mild-hybrid	SUV	Allrad	Benzin/Elektro	245	333	Dec 2020	Mar 2023	2024-03-01	143031
Opel	Zafira	2	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2026-01-01	143032
Opel	Vivaro c	2	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2026-01-01	143036
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	125	170	Nov 2009	May 2011	2024-03-01	143037
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	147	200	Nov 2009	May 2011	2024-03-01	143038
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	155	211	May 2011	Jul 2018	2024-03-01	143039
VW	Tiguan	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	81	110	May 2010	Jul 2011	2024-03-01	143040
VW	Tiguan	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	103	140	Nov 2009	Jul 2018	2024-03-01	143041
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	103	140	Nov 2007	Jul 2018	2024-03-01	143042
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	125	170	May 2010	May 2013	2024-03-01	143043
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	130	177	Nov 2012	Jul 2018	2024-03-01	143044
VW	Touran	1.2 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	77	105	May 2010	May 2015	2024-03-01	143045
Toyota	Proace	2.0 D4D	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2026-01-01	143046
VW	Touran	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	May 2010	May 2015	2024-03-01	143047
Toyota	Proace verso	2.0 D4D	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2026-01-01	143048
VW	Touran	1.6 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	77	105	May 2010	May 2015	2024-03-01	143049
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	103	140	May 2010	May 2015	2024-03-01	143050
VW	Touran	FSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	85	116	Feb 2003	Nov 2006	2025-06-01	143051
VW	Touran	2.0 Ecofuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	80	109	Feb 2006	Nov 2006	2025-06-01	143052
VW	Touran	2.0 FSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	110	150	May 2004	Jan 2007	2025-06-01	143053
VW	Touran	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	101	Oct 2003	May 2005	2024-03-01	143054
VW	Touran	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	77	105	Aug 2003	Nov 2006	2025-06-01	143055
VW	Touran	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	100	136	Feb 2003	May 2010	2025-06-01	143056
VW	Touareg	3.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	180	245	May 2011	Dec 2014	2024-03-01	143057
Audi	A6 c8	45 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	180	245	Jan 2021	-	2024-03-01	143058
Audi	A6 c8 avant	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	180	245	Jan 2021	-	2024-03-01	143059
Audi	A6 allroad c8	45 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	180	245	Jan 2021	-	2024-03-01	143060
Audi	A7 sportback	45 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	180	245	Jan 2021	-	2024-03-01	143061
Audi	A7 sportback	S7 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	253	344	Nov 2020	-	2024-03-01	143062
Hyundai	Ix35	Crdi 4WD	Kasten/SUV	Allrad	Diesel	100	136	Aug 2009	Dec 2015	2024-03-01	143063
Volvo	Xc90 i van	2.4 D5 AWD	Kasten/SUV	Allrad	Diesel	147	200	Sep 2013	Dec 2014	2024-03-01	143065
Volvo	Xc90 i van	2.4 D4	Kasten/SUV	Frontantrieb	Diesel	120	163	Sep 2013	Dec 2014	2024-03-01	143066
Dodge	Caravan	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	122	166	Oct 1995	Jun 2000	2024-03-01	143071
Dodge	Caravan	3.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	131	178	Oct 1995	Jun 2000	2024-03-01	143072


--- Round 1 / 首次发送 ---
## 更新点

* 复用 4 个已有尺寸组：Fiat Tipo 357 Hatchback、Tipo 358 Wagon、Nissan Qashqai II J11 facelift、Maserati Quattroporte VI M156。
* 首次闭合 Maserati Ghibli Trofeo M157，以及 BMW 8 Series、X7、X6、X5 共 6 个尺寸组。Maserati 官方资料明确区分了含镜与不含镜宽度；BMW 官方技术资料直接支持对应三维。([maserati.com][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：14
* READY 映射：14
* PENDING Ktype：86
* 已确认尺寸组：10，其中复用 4 组、首次创建 6 组
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142978	142978	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH		READY
142981	142981	Wagon	Tipo II	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH		READY
143002	143002	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	J11改款后五门SUV外廓。	READY
143003	143003	Sedan	Ghibli III	M157	4	EU-MASERATI-GHIBLI-III-M157-SEDAN-TROFEO-01	HIGH	M157 Trofeo四门轿车外廓。	READY
143010	143010	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH		READY
143023	143023	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143024	143024	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143025	143025	Convertible	8 Series II	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH	G14两门Convertible外廓。	READY
143026	143026	Convertible	8 Series II	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH	G14两门Convertible外廓。	READY
143027	143027	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143028	143028	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143029	143029	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-PREFL-01	HIGH	G07改款前五门SUV外廓。	READY
143030	143030	SUV	X6 III	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前五门SUV外廓。	READY
143031	143031	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MASERATI-GHIBLI-III-M157-SEDAN-TROFEO-01	4971	1945	1461	Maserati MY21 Ghibli official digital brochure	https://www.maserati.com/content/dam/maserati/regional/gb/Brochures/2021/my21/gh/GB_MY21_GH_Digital_brochure_V5.pdf
EU-BMW-8-G15-COUPE-01	4843	1902	1341	BMW Group PressClub 840i Coupe specifications	https://www.press.bmwgroup.com/global/article/detail/T0305273EN/specifications-of-the-new-bmw-840i-coupe-valid-from-02-2020?forceSitePreference=DESKTOP
EU-BMW-8-G14-CONVERTIBLE-01	4843	1902	1339	BMW Group PressClub 840i Convertible specifications	https://www.press.bmwgroup.com/global/article/detail/T0305274EN/specifications-of-the-new-bmw-840i-convertible-valid-from-02/2020
EU-BMW-X7-G07-SUV-PREFL-01	5151	2000	1805	BMW Group PressClub first-ever BMW X7 specifications	https://www.press.bmwgroup.com/global/article/detail/T0285836EN/the-first-ever-bmw-x7?language=en
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW Group PressClub new BMW X6 technical release	https://www.press.bmwgroup.com/global/article/detail/T0297827EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW Group PressClub all-new BMW X5 technical release	https://www.press.bmwgroup.com/middle-east/article/detail/T0281840EN/the-all-new-bmw-x5%3A-the-prestige-sav-with-the-most-innovative-technologies?language=en
```

## 下一步优先处理

优先按共享外廓聚类闭合 Toyota RAV4 IV/V Van、Toyota Verso、Volvo XC60/XC90 Van 和 SsangYong 商用化 SUV；随后处理 VW Sharan、Tiguan、Touran 中需要拆分改款前后的 Ktype。

推进信号：CONTINUE

[1]: https://www.maserati.com/content/dam/maserati/regional/au/2021/Brochures/my21/gh/Ghibli_Digital_Catalogue_EN_ANZ_FINAL.pdf?utm_source=chatgpt.com "High-powered Luxury | 26"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Toyota RAV4 IV Van、RAV4 V Van 与 Verso 三个车型簇，共新增 **15 个 READY Ktype、24 条 READY 映射、5 个尺寸组**。
* RAV4 IV 跨越 2015 年外廓变更的 Ktype 已拆为 `prefl` 与 `facelift`；2015 年末才开始的 142976 仅关联改款后尺寸组。
* RAV4 V 的汽油、AWD 与混动版本复用同一 XA50 外廓。
* Verso 跨越 2013 年外观更新的 Ktype 拆分为改款前 4440 mm 与改款后 4460 mm 两组；高度统一采用官方标准 16 英寸车轮状态。Toyota 官方资料直接支持上述三维和代际边界。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：29
* PENDING Ktype：71
* READY 映射：38
* 已确认尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142972_prefl	142972	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142972_facelift	142972	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142973_prefl	142973	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142973_facelift	142973	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142974_prefl	142974	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142974_facelift	142974	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142975_prefl	142975	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142975_facelift	142975	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142976	142976	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142977_prefl	142977	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142977_facelift	142977	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142979	142979	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142980	142980	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142982	142982	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142983	142983	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142989_prefl	142989	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142989_facelift	142989	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142990_prefl	142990	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142990_facelift	142990	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142993	142993	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142994_prefl	142994	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2012年末改款前外廓。	READY
142994_facelift	142994	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142995_prefl	142995	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142995_facelift	142995	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	4570	1845	1660	Toyota Canada 2013 RAV4 official specifications	https://media.toyota.ca/content/dam/media-toyota/general/specifications/RAV4_-_Brochure.pdf
EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	4605	1845	1675	Toyota UK RAV4 official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1547121943180511MRAV4TechnicalSpecifications.pdf
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota UK New RAV4 official technical release	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-TOYOTA-VERSO-II-MPV-PREFL-01	4440	1790	1620	Toyota UK World Premiere of the New Toyota Verso	https://media.toyota.co.uk/world-premiere-of-the-new-toyota-verso/
EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	4460	1790	1620	Toyota UK Verso official full release and technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1517399376180122MVersofullrelease.pdf
```

## 下一步优先处理

按共享外廓一次闭合 Volvo XC60 I Van、Volvo XC90 I Van，以及 SsangYong Korando、Rexton、Rodius II Van、XLV Van；随后批量建立对应 Ktype 关联。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 SsangYong Korando、三种 Rexton 外廓、Rodius II 与 XLV，共新增 13 个 READY Ktype、6 个尺寸组。
* 闭合 Volvo XC60 I facelift Van 与 XC90 I Van，共新增 6 个 READY Ktype、2 个尺寸组。
* 驱动形式和发动机差异未重复建组；商用化 Van 版本按对应乘用车物理外廓复用。Volvo XC60 官方尺寸页明确区分车身宽度与含后视镜宽度；SsangYong XLV、Rexton、Rodius 和 Korando 的车型资料支持对应外廓。([沃尔沃汽车][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：48
* PENDING Ktype：52
* READY 映射：57
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142959	142959	SUV	Korando III facelift	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-FACELIFT-01	HIGH	商用化版本沿用五门SUV外廓。	READY
142960	142960	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-Y400-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142961	142961	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-Y400-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142962	142962	SUV	Rexton II	Y250	5	EU-SSANGYONG-REXTON-II-Y250-SUV-01	MEDIUM	RX270 XDI五门SUV外廓。	READY
142963	142963	SUV	Rexton II	Y250	5	EU-SSANGYONG-REXTON-II-Y250-SUV-01	MEDIUM	RX270 XDI五门SUV外廓。	READY
142964	142964	SUV	Rexton W		5	EU-SSANGYONG-REXTON-W-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142965	142965	SUV	Rexton W		5	EU-SSANGYONG-REXTON-W-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142966	142966	MPV	Rodius II	A150	5	EU-SSANGYONG-RODIUS-II-A150-MPV-01	HIGH	商用化版本沿用Rodius II五门MPV外廓。	READY
142967	142967	MPV	Rodius II	A150	5	EU-SSANGYONG-RODIUS-II-A150-MPV-01	HIGH	商用化版本沿用Rodius II五门MPV外廓。	READY
142968	142968	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142969	142969	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142970	142970	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142971	142971	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142996	142996	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142997	142997	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142998	142998	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142999	142999	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
143065	143065	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	MEDIUM	商用化版本沿用末期五门SUV外廓。	READY
143066	143066	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	MEDIUM	商用化版本沿用末期五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SSANGYONG-KORANDO-III-C200-SUV-FACELIFT-01	4410	1830	1710	SsangYong Korando 2016 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2018/05/Ssangyong-Korando-2016-UK.pdf
EU-SSANGYONG-REXTON-II-Y400-SUV-01	4850	1960	1825	SsangYong All New Rexton international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/08/Ssangyong-Rexton-2017-INT.pdf
EU-SSANGYONG-REXTON-II-Y250-SUV-01	4720	1870	1830	VehicleScore SsangYong Rexton dimensions	https://vehiclescore.co.uk/car-dimensions-check/ssangyong/rexton
EU-SSANGYONG-REXTON-W-SUV-01	4755	1900	1840	SsangYong Rexton W UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Ssangyong-Rexton-2015-UK.pdf
EU-SSANGYONG-RODIUS-II-A150-MPV-01	5130	1915	1850	SsangYong Turismo brochure	https://www.bassettsgroup.co.uk/images/user/brochures/turismo-brochure.pdf
EU-SSANGYONG-XLV-I-SUV-01	4440	1798	1635	SsangYong Tivoli XLV MY17 brochure	https://www.leisureworldgroup.com/assets/media/tivoli-xlv-my17-brochure.pdf
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Volvo Cars XC60 official dimensions	https://www.volvocars.com/en-th/support/car/xc60/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-XC90-I-SUV-FACELIFT-01	4807	1936	1784	Car and Driver 2014 Volvo XC90 specifications	https://www.caranddriver.com/volvo/xc90/specs/2014/volvo_xc90_volvo-xc90_2014
```

## 下一步优先处理

优先闭合 Hyundai Santa Fe IV、Kia Sorento IV、Audi e-tron S，以及可直接复用已有组的 Hyundai ix35；随后集中处理 VW Sharan、Tiguan 与 Touran 的改款边界。

推进信号：CONTINUE

[1]: https://www.volvocars.com/en-th/support/car/xc60/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/?utm_source=chatgpt.com "XC60 Dimensions | Volvo Support Thailand"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Hyundai Santa Fe IV facelift 两个柴油 Ktype，前驱与四驱复用同一 `TM` 外廓。
* 闭合 Kia Sorento IV `MQ4` 插电混动版本。
* 闭合 Audi e-tron S `GE` 宽体 SUV；官方技术表明确给出不含后视镜宽度 1976 mm。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：52
* PENDING Ktype：48
* READY 映射：61
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142991	142991	SUV	Santa Fe IV facelift	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
142992	142992	SUV	Santa Fe IV facelift	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
143001	143001	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4五门SUV外廓。	READY
143011	143011	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-S-01	HIGH	S版本宽体五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	4785	1900	1710	Hyundai New SANTA FE official pricing and technical specifications	https://www.hyundai.news/newsroom/dam/eu/uk/20210302_new_santa_fe_prices_specifications/hyundai_new_santa_fe_pricing_spec_tech.pdf
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700	Kia New Sorento official 2020 catalogue	https://www.kia.com/content/dam/kwcms/bn/en/pdf/New-Sorento-e-Catalogue.pdf
EU-AUDI-E-TRON-I-GE-SUV-S-01	4902	1976	1629	Audi e-tron S official technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1083/file_en/a4b2f911d800690ef81f965483c5f47263e07b65/eTD_Audi_e-tron_S_370KW_220530.pdf
```

## 下一步优先处理

优先处理 Hyundai ix35 跨改款边界，确认能否完整复用已有 facelift 组；随后集中闭合 VW Sharan、Tiguan 与 Touran 的代际和改款尺寸组。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 VW Sharan I、Sharan II，共新增 13 个 READY Ktype；跨 `7M8 / 7M9 / 7M6` 车身边界的 Ktype 已拆分。Sharan II 使用 4854 × 1904 × 1720 mm；Sharan I 按 7M8 与后续改款外廓分别建组。
* 闭合 VW Tiguan I 共 12 个 Ktype；跨 2011 改款的记录拆为 `prefl` 与 `facelift`。改款前使用 4427 × 1809 × 1686 mm，改款后使用 4426 × 1809 × 1703 mm。([汽车数据网][1])
* 闭合 VW Touran I 共 10 个 Ktype，按 `1T1 / 1T2 / 1T3` 三个外廓阶段处理。([volkswagen.ie][2])
* Hyundai ix35 Ktype `143063` 直接复用已有 facelift 尺寸组，未重复创建尺寸记录。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：88
* PENDING Ktype：12
* READY 映射：107
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143004	143004	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143005	143005	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143006	143006	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143007	143007	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143008	143008	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143009	143009	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143012_prefl	143012	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143012_facelift	143012	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143013	143013	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143014	143014	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143015_prefl	143015	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143015_facelift	143015	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143016_prefl	143016	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143016_facelift	143016	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143017_7m9	143017	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143017_7m6	143017	MPV	Sharan I	7M6	5	EU-VW-SHARAN-I-7M6-MPV-FACELIFT2-01	HIGH	7M6后期改款物理外廓。	READY
143018	143018	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143019	143019	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143020	143020	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143021	143021	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143022	143022	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143037	143037	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143038	143038	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143039	143039	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143040_prefl	143040	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143040_facelift	143040	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143041_prefl	143041	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143041_facelift	143041	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143042_prefl	143042	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143042_facelift	143042	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143043_prefl	143043	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143043_facelift	143043	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143044	143044	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143045	143045	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143047	143047	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143049	143049	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143050	143050	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143051	143051	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143052	143052	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143053_prefl	143053	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143053_facelift	143053	MPV	Touran I facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	2006年首次改款五门MPV外廓。	READY
143054	143054	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143055	143055	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143056_prefl	143056	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143056_facelift	143056	MPV	Touran I facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	2006年首次改款五门MPV外廓。	READY
143063	143063	SUV	ix35 I facelift	LM	5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SHARAN-II-7N-MPV-PREFL-01	4854	1904	1720	Volkswagen UK Sharan official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/30891/sharan-brochure.pdf
EU-VW-SHARAN-I-7M8-MPV-PREFL-01	4620	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	4634	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-SHARAN-I-7M6-MPV-FACELIFT2-01	4634	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data Volkswagen Tiguan I generation specifications	https://www.auto-data.net/en/volkswagen-tiguan-i-generation-1849
EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	4426	1809	1703	Volkswagen UK New Tiguan official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Tiguan-2011-UK-.pdf
EU-VW-TOURAN-I-1T1-MPV-PREFL-01	4391	1794	1635	Volkswagen Touran 2005 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2005-UK.pdf
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635	Volkswagen Ireland Touran 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/touran-1.html
EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	4397	1794	1634	Volkswagen UK Touran GP official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touran/touran-gp/vw-touran-gp-brochure-aug-2010.pdf
```

## 下一步优先处理

闭合剩余 12 个 Ktype：Opel Zafira/Vivaro C、Toyota Proace/Proace Verso、VW Touareg II、Audi A6 C8/A6 Avant/A6 allroad/A7 Sportback，以及 Dodge Caravan。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-tiguan-i-generation-1849?utm_source=chatgpt.com "Volkswagen Tiguan I | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/touran-1.html?utm_source=chatgpt.com "VW Touran Type 1T (2003–2015) models"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1-100_ktype_dimension_mapping_final.tsv
- all_1-100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 剩余 12 个 Ktype 已全部闭合：Opel Zafira Life、Opel Vivaro C、Toyota Proace/Proace Verso、VW Touareg II、Audi A6/A7/S7 和 Dodge Caravan。
* Opel 与 Toyota 乘用厢式车型按短、中、长三种物理外廓拆分；Toyota Proace 直接复用累计表已有的三个尺寸组。Opel 与 Toyota 资料明确提供对应车长及不含后视镜宽度口径。([汽车尺寸网][1])
* Dodge Caravan 两个发动机 Ktype 复用同一 NS 短轴外廓，其来源明确标注不含后视镜宽度。([Edmunds][2])
* 已完成固定表头、唯一主键、映射引用闭合、尺寸与来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射：127
* PENDING：0
* DIMENSION_GROUP：52
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142959	142959	SUV	Korando III facelift	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-FACELIFT-01	HIGH	商用化版本沿用五门SUV外廓。	READY
142960	142960	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-Y400-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142961	142961	SUV	Rexton II	Y400	5	EU-SSANGYONG-REXTON-II-Y400-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142962	142962	SUV	Rexton II	Y250	5	EU-SSANGYONG-REXTON-II-Y250-SUV-01	MEDIUM	RX270 XDI五门SUV外廓。	READY
142963	142963	SUV	Rexton II	Y250	5	EU-SSANGYONG-REXTON-II-Y250-SUV-01	MEDIUM	RX270 XDI五门SUV外廓。	READY
142964	142964	SUV	Rexton W		5	EU-SSANGYONG-REXTON-W-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142965	142965	SUV	Rexton W		5	EU-SSANGYONG-REXTON-W-SUV-01	HIGH	后驱版本与四驱版本共用外廓。	READY
142966	142966	MPV	Rodius II	A150	5	EU-SSANGYONG-RODIUS-II-A150-MPV-01	HIGH	商用化版本沿用Rodius II五门MPV外廓。	READY
142967	142967	MPV	Rodius II	A150	5	EU-SSANGYONG-RODIUS-II-A150-MPV-01	HIGH	商用化版本沿用Rodius II五门MPV外廓。	READY
142968	142968	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142969	142969	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142970	142970	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142971	142971	SUV	XLV I		5	EU-SSANGYONG-XLV-I-SUV-01	HIGH	商用化版本沿用XLV五门SUV外廓。	READY
142972_prefl	142972	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142972_facelift	142972	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142973_prefl	142973	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142973_facelift	142973	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142974_prefl	142974	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142974_facelift	142974	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142975_prefl	142975	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142975_facelift	142975	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142976	142976	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142977_prefl	142977	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	HIGH	改款前商用Van沿用五门SUV外廓。	READY
142977_facelift	142977	SUV	RAV4 IV	XA40	5	EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	HIGH	改款后商用Van沿用五门SUV外廓。	READY
142978	142978	Hatchback	Tipo II	357	5	EU-FIAT-TIPO-357-HATCHBACK-01	HIGH		READY
142979	142979	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142980	142980	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142981	142981	Wagon	Tipo II	358	5	EU-FIAT-TIPO-358-WAGON-01	HIGH		READY
142982	142982	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142983	142983	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH	商用Van沿用XA50五门SUV外廓。	READY
142989_prefl	142989	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142989_facelift	142989	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142990_prefl	142990	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142990_facelift	142990	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142991	142991	SUV	Santa Fe IV facelift	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
142992	142992	SUV	Santa Fe IV facelift	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
142993	142993	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142994_prefl	142994	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2012年末改款前外廓。	READY
142994_facelift	142994	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142995_prefl	142995	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-PREFL-01	HIGH	2009-2012改款前五门MPV外廓。	READY
142995_facelift	142995	MPV	Verso II		5	EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	HIGH	2013年起改款后五门MPV外廓。	READY
142996	142996	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142997	142997	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142998	142998	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
142999	142999	SUV	XC60 I facelift		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH	商用化版本沿用改款后五门SUV外廓。	READY
143001	143001	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4五门SUV外廓。	READY
143002	143002	SUV	Qashqai II	J11	5	EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	HIGH	J11改款后五门SUV外廓。	READY
143003	143003	Sedan	Ghibli III	M157	4	EU-MASERATI-GHIBLI-III-M157-SEDAN-TROFEO-01	HIGH	M157 Trofeo四门轿车外廓。	READY
143004	143004	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143005	143005	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143006	143006	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143007	143007	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143008	143008	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143009	143009	MPV	Sharan II	7N	5	EU-VW-SHARAN-II-7N-MPV-PREFL-01	HIGH	改款前五门MPV外廓。	READY
143010	143010	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH		READY
143011	143011	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-SUV-S-01	HIGH	S版本宽体五门SUV外廓。	READY
143012_prefl	143012	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143012_facelift	143012	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143013	143013	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143014	143014	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143015_prefl	143015	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143015_facelift	143015	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143016_prefl	143016	MPV	Sharan I	7M8	5	EU-VW-SHARAN-I-7M8-MPV-PREFL-01	HIGH	7M8改款前物理外廓。	READY
143016_facelift	143016	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143017_7m9	143017	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143017_7m6	143017	MPV	Sharan I	7M6	5	EU-VW-SHARAN-I-7M6-MPV-FACELIFT2-01	HIGH	7M6后期改款物理外廓。	READY
143018	143018	MPV	Sharan I	7M9	5	EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	HIGH	7M9首次改款物理外廓。	READY
143019	143019	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143020	143020	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143021	143021	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143022	143022	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143023	143023	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143024	143024	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143025	143025	Convertible	8 Series II	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH	G14两门Convertible外廓。	READY
143026	143026	Convertible	8 Series II	G14	2	EU-BMW-8-G14-CONVERTIBLE-01	HIGH	G14两门Convertible外廓。	READY
143027	143027	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143028	143028	Coupe	8 Series II	G15	2	EU-BMW-8-G15-COUPE-01	HIGH	G15两门Coupe外廓。	READY
143029	143029	SUV	X7 I	G07	5	EU-BMW-X7-G07-SUV-PREFL-01	HIGH	G07改款前五门SUV外廓。	READY
143030	143030	SUV	X6 III	G06	5	EU-BMW-X6-G06-SUV-PREFL-01	HIGH	G06改款前五门SUV外廓。	READY
143031	143031	SUV	X5 IV	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH	G05改款前五门SUV外廓。	READY
143032_s	143032	MPV	Zafira Life I	K0		EU-OPEL-ZAFIRA-LIFE-K0-MPV-S-01	HIGH	K0短车身乘用厢式外廓。	READY
143032_m	143032	MPV	Zafira Life I	K0		EU-OPEL-ZAFIRA-LIFE-K0-MPV-M-01	HIGH	K0中车身乘用厢式外廓。	READY
143032_l	143032	MPV	Zafira Life I	K0		EU-OPEL-ZAFIRA-LIFE-K0-MPV-L-01	HIGH	K0长车身乘用厢式外廓。	READY
143036_s	143036	MPV	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-MPV-S-01	HIGH	K0短车身Combi外廓。	READY
143036_m	143036	MPV	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-MPV-M-01	HIGH	K0中车身Combi外廓。	READY
143036_l	143036	MPV	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-MPV-L-01	HIGH	K0长车身Combi外廓。	READY
143037	143037	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143038	143038	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143039	143039	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143040_prefl	143040	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143040_facelift	143040	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143041_prefl	143041	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143041_facelift	143041	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143042_prefl	143042	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143042_facelift	143042	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143043_prefl	143043	SUV	Tiguan I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFL-01	HIGH	2011改款前五门SUV外廓。	READY
143043_facelift	143043	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143044	143044	SUV	Tiguan I facelift	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH	2011改款后五门SUV外廓。	READY
143045	143045	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143046_compact	143046	MPV	Proace II	K0		EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact乘用Bus外廓。	READY
143046_medium	143046	MPV	Proace II	K0		EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium乘用Bus外廓。	READY
143046_long	143046	MPV	Proace II	K0		EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long乘用Bus外廓。	READY
143047	143047	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143048_compact	143048	MPV	Proace Verso I	K0		EU-TOYOTA-PROACE-II-BODY-COMPACT-01	HIGH	Compact乘用MPV外廓。	READY
143048_medium	143048	MPV	Proace Verso I	K0		EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	HIGH	Medium乘用MPV外廓。	READY
143048_long	143048	MPV	Proace Verso I	K0		EU-TOYOTA-PROACE-II-MPV-LONG-01	HIGH	Long乘用MPV外廓。	READY
143049	143049	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143050	143050	MPV	Touran I facelift II	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	HIGH	2010年第二次改款五门MPV外廓。	READY
143051	143051	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143052	143052	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143053_prefl	143053	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143053_facelift	143053	MPV	Touran I facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	2006年首次改款五门MPV外廓。	READY
143054	143054	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143055	143055	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143056_prefl	143056	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-1T1-MPV-PREFL-01	HIGH	2006改款前五门MPV外廓。	READY
143056_facelift	143056	MPV	Touran I facelift	1T2	5	EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	HIGH	2006年首次改款五门MPV外廓。	READY
143057	143057	SUV	Touareg II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	7P改款前五门SUV外廓。	READY
143058	143058	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	4A2四门Sedan外廓。	READY
143059	143059	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	4A5五门Avant外廓。	READY
143060	143060	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-C8-4AH-WAGON-ALLROAD-01	HIGH	4AH allroad五门Wagon外廓。	READY
143061	143061	Hatchback	A7 Sportback II	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH	4KA五门Sportback外廓。	READY
143062	143062	Hatchback	S7 Sportback II	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-S7-01	HIGH	S7 TDI五门Sportback外廓。	READY
143063	143063	SUV	ix35 I facelift	LM	5	EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	HIGH	改款后五门SUV外廓。	READY
143065	143065	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	MEDIUM	商用化版本沿用末期五门SUV外廓。	READY
143066	143066	SUV	XC90 I facelift		5	EU-VOLVO-XC90-I-SUV-FACELIFT-01	MEDIUM	商用化版本沿用末期五门SUV外廓。	READY
143071	143071	MPV	Caravan III	NS		EU-DODGE-CARAVAN-III-NS-MPV-SWB-01	MEDIUM	NS短轴MPV外廓。	READY
143072	143072	MPV	Caravan III	NS		EU-DODGE-CARAVAN-III-NS-MPV-SWB-01	MEDIUM	NS短轴MPV外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1-100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SSANGYONG-KORANDO-III-C200-SUV-FACELIFT-01	4410	1830	1710	SsangYong Korando 2016 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2018/05/Ssangyong-Korando-2016-UK.pdf
EU-SSANGYONG-REXTON-II-Y400-SUV-01	4850	1960	1825	SsangYong All New Rexton international brochure	https://autocatalogarchive.com/wp-content/uploads/2017/08/Ssangyong-Rexton-2017-INT.pdf
EU-SSANGYONG-REXTON-II-Y250-SUV-01	4720	1870	1830	VehicleScore SsangYong Rexton dimensions	https://vehiclescore.co.uk/car-dimensions-check/ssangyong/rexton
EU-SSANGYONG-REXTON-W-SUV-01	4755	1900	1840	SsangYong Rexton W UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Ssangyong-Rexton-2015-UK.pdf
EU-SSANGYONG-RODIUS-II-A150-MPV-01	5130	1915	1850	SsangYong Turismo brochure	https://www.bassettsgroup.co.uk/images/user/brochures/turismo-brochure.pdf
EU-SSANGYONG-XLV-I-SUV-01	4440	1798	1635	SsangYong Tivoli XLV MY17 brochure	https://www.leisureworldgroup.com/assets/media/tivoli-xlv-my17-brochure.pdf
EU-TOYOTA-RAV4-IV-XA40-SUV-PREFL-01	4570	1845	1660	Toyota Canada 2013 RAV4 official specifications	https://media.toyota.ca/content/dam/media-toyota/general/specifications/RAV4_-_Brochure.pdf
EU-TOYOTA-RAV4-IV-XA40-SUV-FACELIFT-01	4605	1845	1675	Toyota UK RAV4 official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1547121943180511MRAV4TechnicalSpecifications.pdf
EU-FIAT-TIPO-357-HATCHBACK-01	4368	1792	1495	Fiat Tipo Hatchback official dimensions	https://www.fiat-auto.co.jp/tipo-new-without-dynamic/tipo-hatchback-life/dimensions
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota UK New RAV4 official technical release	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-FIAT-TIPO-358-WAGON-01	4571	1792	1514	Fiat Tipo Station Wagon official technical specifications	https://www.media.stellantis.com/uploads/be/BE/2017/Fiat/files/160502_Fiat_Tipo-Station-Wagon-EMEA_Technical-specifications_ENG.pdf
EU-TOYOTA-VERSO-II-MPV-PREFL-01	4440	1790	1620	Toyota UK World Premiere of the New Toyota Verso	https://media.toyota.co.uk/world-premiere-of-the-new-toyota-verso/
EU-TOYOTA-VERSO-II-MPV-FACELIFT-01	4460	1790	1620	Toyota UK Verso official full release and technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/1517399376180122MVersofullrelease.pdf
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	4785	1900	1710	Hyundai New SANTA FE official pricing and technical specifications	https://www.hyundai.news/newsroom/dam/eu/uk/20210302_new_santa_fe_prices_specifications/hyundai_new_santa_fe_pricing_spec_tech.pdf
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Volvo Cars XC60 official dimensions	https://www.volvocars.com/en-th/support/car/xc60/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700	Kia New Sorento official 2020 catalogue	https://www.kia.com/content/dam/kwcms/bn/en/pdf/New-Sorento-e-Catalogue.pdf
EU-NISSAN-QASHQAI-II-J11-SUV-FACELIFT-01	4394	1806	1590	Nissan Qashqai MY18 official brochure	https://i.i-sgcm.com/new_cars/cars/11530/brochures/brochure_20181002044433.pdf
EU-MASERATI-GHIBLI-III-M157-SEDAN-TROFEO-01	4971	1945	1461	Maserati MY21 Ghibli official digital brochure	https://www.maserati.com/content/dam/maserati/regional/gb/Brochures/2021/my21/gh/GB_MY21_GH_Digital_brochure_V5.pdf
EU-VW-SHARAN-II-7N-MPV-PREFL-01	4854	1904	1720	Volkswagen UK Sharan official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/30891/sharan-brochure.pdf
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481	Maserati Quattroporte MY22 official digital catalogue	https://www.maserati.com/content/dam/maserati/international/Brochures/my22/quattroporte/QP_MY22_Digital_Catalogue.pdf
EU-AUDI-E-TRON-I-GE-SUV-S-01	4902	1976	1629	Audi e-tron S official technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1083/file_en/a4b2f911d800690ef81f965483c5f47263e07b65/eTD_Audi_e-tron_S_370KW_220530.pdf
EU-VW-SHARAN-I-7M8-MPV-PREFL-01	4620	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-SHARAN-I-7M9-MPV-FACELIFT-01	4634	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-SHARAN-I-7M6-MPV-FACELIFT2-01	4634	1810	1730	Volkswagen Ireland Sharan 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/sharan-1.html
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4427	1809	1686	Auto-Data Volkswagen Tiguan I generation specifications	https://www.auto-data.net/en/volkswagen-tiguan-i-generation-1849
EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	4426	1809	1703	Volkswagen UK New Tiguan official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Tiguan-2011-UK-.pdf
EU-BMW-8-G15-COUPE-01	4843	1902	1341	BMW Group PressClub 840i Coupe specifications	https://www.press.bmwgroup.com/global/article/detail/T0305273EN/specifications-of-the-new-bmw-840i-coupe-valid-from-02-2020?forceSitePreference=DESKTOP
EU-BMW-8-G14-CONVERTIBLE-01	4843	1902	1339	BMW Group PressClub 840i Convertible specifications	https://www.press.bmwgroup.com/global/article/detail/T0305274EN/specifications-of-the-new-bmw-840i-convertible-valid-from-02/2020
EU-BMW-X7-G07-SUV-PREFL-01	5151	2000	1805	BMW Group PressClub first-ever BMW X7 specifications	https://www.press.bmwgroup.com/global/article/detail/T0285836EN/the-first-ever-bmw-x7?language=en
EU-BMW-X6-G06-SUV-PREFL-01	4935	2004	1696	BMW Group PressClub new BMW X6 technical release	https://www.press.bmwgroup.com/global/article/detail/T0297827EN/the-new-bmw-x6-a-leader-with-broad-shoulders?language=en
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW Group PressClub all-new BMW X5 technical release	https://www.press.bmwgroup.com/middle-east/article/detail/T0281840EN/the-all-new-bmw-x5%3A-the-prestige-sav-with-the-most-innovative-technologies?language=en
EU-OPEL-ZAFIRA-LIFE-K0-MPV-S-01	4606	1920	1905	Automobile Dimension Opel Zafira Life S	https://www.automobiledimension.com/model/opel/zafira-life-s
EU-OPEL-ZAFIRA-LIFE-K0-MPV-M-01	4956	1920	1890	Automobile Dimension Opel Zafira Life M	https://www.automobiledimension.com/model/opel/zafira-life-m
EU-OPEL-ZAFIRA-LIFE-K0-MPV-L-01	5306	1920	1890	Automobile Dimension Opel Zafira Life L	https://www.automobiledimension.com/model/opel/zafira-life-l
EU-OPEL-VIVARO-C-K0-MPV-S-01	4606	1920	1905	Auto-Data Opel Vivaro C Combi specifications; Vauxhall New Vivaro official owner manual	https://www.auto-data.net/en/opel-vivaro-model-2033;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/new-vivaro/new-vivaro-owners-manual-april-2019.pdf
EU-OPEL-VIVARO-C-K0-MPV-M-01	4956	1920	1905	Auto-Data Opel Vivaro C Combi specifications; Vauxhall New Vivaro official owner manual	https://www.auto-data.net/en/opel-vivaro-model-2033;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/new-vivaro/new-vivaro-owners-manual-april-2019.pdf
EU-OPEL-VIVARO-C-K0-MPV-L-01	5306	1920	1890	Auto-Data Opel Vivaro C Combi specifications; Vauxhall New Vivaro official owner manual	https://www.auto-data.net/en/opel-vivaro-model-2033;https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/owners/owners-manuals/new-vivaro/new-vivaro-owners-manual-april-2019.pdf
EU-VW-TOURAN-I-1T3-MPV-FACELIFT2-01	4397	1794	1634	Volkswagen UK Touran GP official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/touran/touran-gp/vw-touran-gp-brochure-aug-2010.pdf
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910	Toyota All New Proace Verso official brochure	https://blog.le-parnass.com/catalogue_pdf/201701_toyota_proace-verso_e.pdf
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910	Toyota All New Proace Verso official brochure	https://blog.le-parnass.com/catalogue_pdf/201701_toyota_proace-verso_e.pdf
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910	Toyota All New Proace Verso official brochure	https://blog.le-parnass.com/catalogue_pdf/201701_toyota_proace-verso_e.pdf
EU-VW-TOURAN-I-1T1-MPV-PREFL-01	4391	1794	1635	Volkswagen Touran 2005 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touran-2005-UK.pdf
EU-VW-TOURAN-I-1T2-MPV-FACELIFT-01	4407	1794	1635	Volkswagen Ireland Touran 1 previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mpv/touran-1.html
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	Volkswagen Touareg 2011 official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/07/VW-Touareg-2011-AU.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Audi A6 Sedan official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-sedan-1403/download
EU-AUDI-A6-C8-4A5-WAGON-01	4939	1886	1494	Audi A6 Avant official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a6-avant-1400/download
EU-AUDI-A6-C8-4AH-WAGON-ALLROAD-01	4951	1902	1497	Audi A6 allroad official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-audi-a6-allroad-1598/download
EU-AUDI-A7-II-4KA-HATCHBACK-01	4969	1908	1422	Audi A7 Sportback official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-a7-sportback-1406/download
EU-AUDI-A7-II-4KA-HATCHBACK-S7-01	4980	1908	1417	Audi S7 Sportback TDI official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-s7-sportback-tdi-1408/download
EU-HYUNDAI-IX35-I-SUV-FACELIFT-01	4410	1820	1655	Hyundai ix35 2015 Ireland brochure	https://autocatalogarchive.com/wp-content/uploads/2016/10/Hyundai-ix35-2015-IE.pdf
EU-VOLVO-XC90-I-SUV-FACELIFT-01	4807	1936	1784	Car and Driver 2014 Volvo XC90 specifications	https://www.caranddriver.com/volvo/xc90/specs/2014/volvo_xc90_volvo-xc90_2014
EU-DODGE-CARAVAN-III-NS-MPV-SWB-01	4732	1920	1740	Edmunds 1996 Dodge Caravan LE specifications	https://www.edmunds.com/dodge/caravan/1996/st-8469/features-specs/
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1-100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobiledimension.com/model/opel/zafira-life-s "https://www.automobiledimension.com/model/opel/zafira-life-s"
[2]: https://www.edmunds.com/dodge/caravan/1996/st-8469/features-specs/ "https://www.edmunds.com/dodge/caravan/1996/st-8469/features-specs/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1-100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1926 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（926 行）

- 尺寸冲突协调：
  - EU-SSANGYONG-XLV-I-SUV-01 -> EU-SSANGYONG-XLV-I-SUV-02：4440x1798x1605 与 4440x1798x1635，创建新尺寸组
