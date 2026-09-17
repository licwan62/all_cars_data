# 任务：all 第 601-700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0007__9f69cc92


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 601-700 行

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
all 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425
EU-AUDI-A3-8Y-SPORTBACK-5D-01	4343	1816	1449
EU-CITROEN-JUMPY-III-BUS-M-01	4959	1920	1890
EU-CITROEN-JUMPY-III-BUS-XL-01	5309	1920	1890
EU-CITROEN-JUMPY-III-BUS-XS-01	4609	1920	1905
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1695
EU-DS-DS3-CROSSBACK-I-HATCHBACK-01	4118	1791	1534
EU-FERRARI-812-SUPERFAST-COUPE-01	4657	1971	1276
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	4418	1835	1836
EU-FORD-TRANSIT-CONNECT-V408-DCIV-L2-01	4818	1835	1839
EU-FORD-TRANSIT-CONNECT-V408-KOMBI-L2-01	4818	1835	1840
EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	4418	1835	1861
EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	4818	1835	1861
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L2-FWD-01	5572	2066	2236
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L3-FWD-01	6022	2066	2230
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L2-FWD-01	5572	2052	2200
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L3-FWD-01	6022	2052	2194
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L4-FWD-01	6579	2052	2195
EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L2-FWD-01	5767	2098	2236
EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L3-FWD-01	6204	2098	2230
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L2-FWD-01	5767	2098	2200
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L3-FWD-01	6204	2098	2194
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L4-FWD-01	6797	2098	2195
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2533
EU-FORD-TRANSIT-V363-VAN-L2H3-FWD-01	5531	2059	2769
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2530
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2767
EU-GENESIS-GV70-I-JK1-SUV-01	4715	1910	1630
EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	4500	1865	1651
EU-MAZDA-CX-5-I-KE-SUV-01	4555	1840	1710
EU-MAZDA-CX-5-II-KF-SUV-FACELIFT-01	4575	1845	1680
EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	4550	1840	1680
EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	4656	1890	1639
EU-OPEL-VIVARO-C-K0-MPV-L-01	5306	1920	1890
EU-OPEL-VIVARO-C-K0-MPV-M-01	4956	1920	1905
EU-OPEL-VIVARO-C-K0-MPV-S-01	4606	1920	1905
EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	5308	1920	1890
EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	4956	1920	1890
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940
EU-PORSCHE-911-991-2-CARRERA-4-GTS-CONVERTIBLE-AWD-01	4528	1852	1293
EU-PORSCHE-911-991-2-CARRERA-4-GTS-COUPE-AWD-01	4528	1852	1299
EU-PORSCHE-911-991-2-CARRERA-GTS-CONVERTIBLE-RWD-01	4528	1852	1291
EU-PORSCHE-911-991-2-CARRERA-GTS-COUPE-RWD-01	4528	1852	1297
EU-PORSCHE-911-991-2-TARGA-4-GTS-01	4528	1852	1291
EU-PORSCHE-911-991-2-TURBO-S-EXCLUSIVE-COUPE-AWD-01	4507	1880	1297
EU-PORSCHE-CAYENNE-III-COUPE-TURBO-GT-SUV-01	4942	1995	1636
EU-RENAULT-KADJAR-I-SUV-PREFL-01	4449	1836	1613
EU-RENAULT-KANGOO-II-K61-MPV-FACELIFT-01	4282	1829	1839
EU-RENAULT-KANGOO-II-K61-MPV-PREFL-01	4213	1829	1839
EU-RENAULT-MEGANE-IV-GRANDTOUR-GT-WAGON-01	4626	1814	1457
EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	4626	1814	1449
EU-RENAULT-MEGANE-IV-GT-HATCHBACK-01	4359	1814	1438
EU-RENAULT-MEGANE-IV-HATCHBACK-01	4359	1814	1447
EU-RENAULT-MEGANE-IV-SEDAN-01	4632	1814	1443
EU-SKODA-FABIA-IV-HATCHBACK-01	4108	1780	1459
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468
EU-TOYOTA-PROACE-II-BODY-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-II-BODY-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-II-VAN-LONG-01	5309	1920	1935
EU-TOYOTA-PROACE-II-VAN-MEDIUM-01	4959	1920	1899
EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	4959	1920	1940
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-TAIGO-I-SUV-01	4266	1757	1515

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Taigo	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Sep 2021	-	2024-03-01	145050
Cupra	Born	58	Schrägheck	Heckantrieb	Elektro	150	204	Aug 2021	-	2024-03-01	145053
Cupra	Born	45	Schrägheck	Heckantrieb	Elektro	110	150	Aug 2021	-	2024-03-01	145055
Cupra	Born	58 E-boost	Schrägheck	Heckantrieb	Elektro	170	231	Aug 2021	May 2024	2025-11-01	145056
Cupra	Born	77 E-boost	Schrägheck	Heckantrieb	Elektro	170	231	Aug 2021	-	2024-03-01	145057
Mazda	Cx-30	E-skyactiv-x M Hybrid AWD	SUV	Allrad	Benzin/Elektro	137	186	Jun 2021	-	2024-03-01	145068
Mazda	Cx-30	E-skyactiv-x M Hybrid	SUV	Frontantrieb	Benzin/Elektro	137	186	Jun 2021	-	2024-03-01	145069
Peugeot	308 sw iii	Puretech 130	Kombi	Frontantrieb	Benzin	96	131	Jul 2021	-	2024-03-01	145071
Peugeot	308 sw iii	Puretech 110	Kombi	Frontantrieb	Benzin	81	110	Jul 2021	-	2024-03-01	145072
Peugeot	308 sw iii	Bluehdi 130	Kombi	Frontantrieb	Diesel	96	131	Jul 2021	-	2024-03-01	145073
Peugeot	308 sw iii	Hybrid 180	Kombi	Frontantrieb	Benzin/Elektro	133	181	Jul 2021	-	2024-03-01	145075
Peugeot	308 sw iii	Hybrid 225	Kombi	Frontantrieb	Benzin/Elektro	165	224	Jul 2021	-	2024-03-01	145077
DS	Ds	E-tense 360 4X4	Stufenheck	Allrad	Benzin/Elektro	265	360	Jun 2021	Aug 2024	2025-12-01	145080
Volvo	Xc60 ii	T6 Plug-in Hybrid AWD	SUV	Allrad	Benzin/Elektro	250	340	Apr 2021	-	2024-03-01	145081
Audi	Q4 e-Tron	45 Quattro	SUV	Allrad	Elektro	195	265	Jun 2021	-	2025-11-01	145083
Audi	Q4 e-Tron sportback	35	SUV	Heckantrieb	Elektro	125	170	Jun 2021	-	2025-11-01	145085
Audi	Q4 e-Tron sportback	40	SUV	Heckantrieb	Elektro	150	204	Jun 2021	-	2025-11-01	145086
Audi	Q4 e-Tron sportback	50 Quattro	SUV	Allrad	Elektro	220	299	Jun 2021	-	2025-11-01	145087
Audi	A3	RS3 Tfsi Quattro	Stufenheck	Allrad	Benzin	294	400	Jul 2021	-	2025-11-01	145088
Audi	A3	RS3 Tfsi Quattro	Schrägheck	Allrad	Benzin	294	400	Jul 2021	-	2025-11-01	145089
Mercedes-benz	Sprinter 4-T tourer	411 CDI	Bus	Heckantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	145090
Mercedes-benz	Sprinter 4-T tourer	419 CDI	Bus	Heckantrieb	Diesel	140	190	Feb 2018	Dec 2021	2024-07-01	145091
Volvo	S60 iii	B6 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	220	299	Apr 2021	Dec 2022	2024-05-01	145093
Volvo	S90 ii	B5 Mild Hybrid AWD	Stufenheck	Allrad	Diesel/Elektro	173	235	Dec 2020	-	2025-06-01	145094
Porsche	Cayenne	4.0 Turbo S E-hybrid AWD	SUV	Allrad	Benzin/Elektro	500	680	May 2017	May 2023	2026-03-01	145106
Porsche	911	4 GTS	Targa	Allrad	Benzin	353	480	Jan 2021	Dec 2024	2026-03-01	145108
Porsche	911	3.0 Carrera 4 GTS	Cabriolet	Allrad	Benzin	353	480	Jan 2021	Dec 2024	2026-03-01	145113
Porsche	911	3.0 Carrera GTS	Cabriolet	Heckantrieb	Benzin	353	480	Jan 2021	May 2024	2024-08-01	145114
Porsche	911	3.0 Carrera 4 GTS	Coupe	Allrad	Benzin	353	480	Jan 2021	Dec 2024	2026-03-01	145115
Porsche	911	3.0 Carrera GTS	Coupe	Heckantrieb	Benzin	353	480	Jan 2021	Dec 2024	2026-03-01	145116
Mercedes-benz	Eqs	EQS 450+	Schrägheck	Heckantrieb	Elektro	245	333	Aug 2021	-	2024-03-01	145121
Mercedes-benz	Eqs	EQS 580 4-matic	Schrägheck	Allrad	Elektro	385	523	Aug 2021	-	2024-03-01	145122
Hyundai	Bayon	1.2 MPI	SUV	Frontantrieb	Benzin	62	84	May 2021	-	2024-03-01	145123
RAM	1500 crew cab pickup	6.2 TRX	Pick-up	Allrad	Benzin	523	711	Sep 2020	-	2024-03-01	145125
Mercedes-benz	Viano	CDI 2.2	Bus	Heckantrieb	Diesel	70	95	Sep 2010	-	2024-03-01	145126
Hyundai	Bayon	1.0 T-gdi	SUV	Frontantrieb	Benzin	74	101	May 2021	-	2024-03-01	145128
Hyundai	Bayon	1.0 T-gdi 48v-hybrid	SUV	Frontantrieb	Benzin/Elektro	74	101	May 2021	-	2024-03-01	145129
Porsche	Taycan	4	Kombi	Allrad	Elektro	350	476	May 2020	Dec 2023	2024-07-01	145130
Hyundai	Bayon	1.0 T-gdi 48v-hybrid	SUV	Frontantrieb	Benzin/Elektro	88	120	May 2021	-	2024-03-01	145131
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel/Elektro	120	163	Jul 2021	-	2024-03-01	145132
Mercedes-benz	C-Klasse	C 220 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	147	200	Jul 2021	-	2024-03-01	145133
Mercedes-benz	C-Klasse	C 300 D 4-matic	Stufenheck	Allrad	Diesel/Elektro	195	265	Jul 2021	-	2024-03-01	145134
Opel	Vivaro c	2	Kasten	Frontantrieb	Diesel	106	144	Aug 2021	Apr 2025	2026-01-01	145135
Peugeot	Expert	2.0 Bluehdi 145	Kasten	Frontantrieb	Diesel	106	144	Aug 2021	Apr 2025	2025-12-01	145137
Porsche	Taycan	4S Performance Battery Plus	Kombi	Allrad	Elektro	420	571	May 2020	Dec 2023	2024-07-01	145139
Porsche	Taycan	Turbo	Kombi	Allrad	Elektro	500	680	May 2020	Dec 2023	2024-07-01	145140
Porsche	Taycan	Turbo S	Kombi	Allrad	Elektro	560	761	May 2020	Dec 2023	2024-07-01	145141
Opel	Combo e tour / life	Combo-e	Großraumlimousine	Frontantrieb	Elektro	100	136	Jun 2021	Oct 2023	2024-05-01	145145
Porsche	Taycan	4S Performance Battery Plus	Stufenheck	Allrad	Elektro	420	571	May 2019	Dec 2023	2024-07-01	145147
MG	Mg 5	EV	Kombi	Frontantrieb	Elektro	115	156	Oct 2020	-	2024-03-01	145148
Mercedes-benz	C-Klasse	C 220 D 4-matic	Kombi	Allrad	Diesel/Elektro	147	200	Mar 2021	-	2024-03-01	145149
Mercedes-benz	C-Klasse	C 200 D	Kombi	Heckantrieb	Diesel/Elektro	120	163	Jul 2021	-	2024-03-01	145150
Mercedes-benz	C-Klasse	C 180	Kombi	Heckantrieb	Benzin/Elektro	125	170	Mar 2021	-	2024-03-01	145151
Ford	Transit connect v408	1.0 Flexifuel	Kasten/Großraumlimousine	Frontantrieb	Benzin/Ethanol	74	100	May 2021	-	2024-03-01	145154
Renault	Espace v	2.0 Blue DCI 190	Großraumlimousine	Frontantrieb	Diesel	139	189	Jan 2021	Mar 2023	2024-05-01	145155
Volvo	V60 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Diesel/Elektro	145	197	Mar 2020	-	2024-03-01	145168
Volvo	V60 ii cross country	B4 Mild-hybrid AWD	Kombi	Allrad	Diesel/Elektro	145	197	Oct 2020	-	2024-03-01	145169
Mercedes-benz	Glc	300 E 4-matic	SUV	Allrad	Benzin/Elektro	235	320	Nov 2019	Mar 2023	2024-03-01	145177
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	270	367	Jul 2021	-	2024-03-01	145181
Hyundai	Staria	2.2 Crdi	Kasten	Frontantrieb	Diesel	130	177	Jan 2021	-	2024-03-01	145185
Lotus	Elise	Sport 240	Cabriolet	Heckantrieb	Benzin	179	243	Jan 2021	-	2024-03-01	145186
Citroën	Jumpy iii	2.0 Bluehdi 145	Kasten	Frontantrieb	Diesel	106	144	Aug 2021	Apr 2025	2025-12-01	145194
Toyota	Proace	2.0 D4D	Kasten	Frontantrieb	Diesel	106	144	Aug 2021	Apr 2025	2026-01-01	145196
Skoda	Octavia	1.4 TSI IV	Schrägheck	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	145197
Skoda	Octavia	1.4 TSI IV	Kombi	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	145198
Renault	Megane iv	1.6 E-tech 160	Schrägheck	Frontantrieb	Benzin/Elektro	118	160	Jul 2021	-	2024-03-01	145204
Renault	Talisman	2.0 Blue DCI 190	Kombi	Frontantrieb	Diesel	139	189	Jul 2021	Mar 2022	2024-03-01	145208
Renault	Talisman	1.3 TCE 160	Kombi	Frontantrieb	Benzin	116	158	Jul 2021	Mar 2022	2024-03-01	145209
Renault	Talisman	2.0 Blue DCI 190	Stufenheck	Frontantrieb	Diesel	139	189	Jul 2021	Mar 2022	2024-03-01	145210
Renault	Talisman	1.3 TCE 160	Stufenheck	Frontantrieb	Benzin	116	158	Jul 2021	Mar 2022	2024-03-01	145211
Renault	Kadjar	1.3 TCE 160	SUV	Frontantrieb	Benzin	116	158	Jul 2021	-	2024-03-01	145212
Renault	Megane iv grandtour	1.0 TCE 115	Kombi	Frontantrieb	Benzin	84	114	Jul 2021	-	2024-03-01	145213
Renault	Express	1.3 TCE 100	Kasten/Großraumlimousine	Frontantrieb	Benzin	75	102	May 2021	-	2024-03-01	145220
Renault	Express	1.5 Blue DCI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	May 2021	-	2024-03-01	145221
Renault	Express	1.5 Blue DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	May 2021	-	2024-03-01	145222
Hyundai	Tucson	1.6 T-gdi	SUV	Frontantrieb	Benzin	110	150	May 2021	-	2024-03-01	145223
Renault	Kangoo	TCE 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2021	-	2024-03-01	145224
Renault	Kangoo	TCE 100	Großraumlimousine	Frontantrieb	Benzin	75	102	Jul 2021	-	2024-03-01	145225
Renault	Kangoo	Blue DCI 95	Großraumlimousine	Frontantrieb	Diesel	70	95	Jul 2021	-	2024-03-01	145226
Dacia	Duster	1.0 TCE 90	SUV	Frontantrieb	Benzin	67	91	May 2021	-	2024-03-01	145234
Mazda	Cx-5	2.2 Skyactiv-d	SUV	Frontantrieb	Diesel	135	184	Feb 2021	-	2024-03-01	145235
Porsche	Macan	2	SUV	Allrad	Benzin	195	265	May 2018	-	2024-03-01	145236
Skoda	Fabia iv	1.0 MPI	Schrägheck	Frontantrieb	Benzin	48	65	Aug 2021	-	2024-03-01	145238
Renault	Megane iv	1.3 TCE 160	Schrägheck	Frontantrieb	Benzin	116	158	Aug 2020	-	2024-03-01	145240
Renault	Kangoo	1.5 Blue DCI 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jun 2021	-	2024-03-01	145242
Renault	Kangoo	1.5 Blue DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jun 2021	-	2024-03-01	145243
Renault	Kangoo	1.5 Blue DCI 115	Kasten/Großraumlimousine	Frontantrieb	Diesel	85	116	Jun 2021	-	2024-03-01	145244
Renault	Kangoo	1.3 TCE 100	Kasten/Großraumlimousine	Frontantrieb	Benzin	75	102	Jun 2021	-	2024-03-01	145245
Renault	Kangoo	1.3 TCE 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jun 2021	-	2024-03-01	145246
Ford	Transit	2.2 Tdci RWD	Bus	Heckantrieb	Diesel	114	155	Oct 2011	Aug 2014	2024-03-01	145254
Renault	Kangoo	Blue DCI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Jul 2021	-	2024-03-01	145256
Ferrari	812 superfast	Competizione	Coupe	Heckantrieb	Benzin	610	830	May 2021	-	2025-06-01	145257
Audi	Q7	45 TDI Quattro	SUV	Allrad	Diesel	183	249	Jul 2019	-	2024-03-01	145258
Toyota	Proace city	Electric	Kasten/Großraumlimousine	Frontantrieb	Elektro	100	136	Jul 2021	Feb 2024	2024-07-01	145261
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	70	95	Aug 2021	-	2025-02-03	145263
Genesis	Gv70	2.2	SUV	Heckantrieb	Diesel	154	209	Apr 2021	-	2025-06-01	145264
BYD	Dolphin	EV	Schrägheck	Frontantrieb	Elektro	130	177	Aug 2021	-	2025-02-03	145265
Genesis	G70	2.0 T-gdi	Stufenheck	Heckantrieb	Benzin	145	197	Jun 2021	-	2024-03-01	145266
Genesis	G70	2.0 T-gdi Htrac	Stufenheck	Allrad	Benzin	145	197	Jun 2021	-	2024-03-01	145267
Toyota	Proace city verso	Electric	Großraumlimousine	Frontantrieb	Elektro	100	136	Jul 2021	Feb 2024	2024-07-01	145268


--- Round 1 / 首次发送 ---
更新点

* 闭合 CUPRA Born、Mazda CX-30、Peugeot 308 SW III、DS 9 四个车型簇，新建 4 个尺寸组。Born 的 1809 mm 宽度另以明确区分含镜宽度的规格资料确认；DS 9 官方规格同时列出车身宽度和折叠/展开后视镜宽度。([CUPRA][1])
* 闭合 Audi Q4 e-tron SUV、Q4 Sportback、RS 3 Sedan、RS 3 Sportback及 Hyundai Bayon，新建 5 个尺寸组；SUV/Sportback和RS 3普通A3外廓分别建组，未错误复用已有普通A3尺寸。
* 复用跨批次索引中的 Taigo、XC60、S60、S90、Octavia IV、Megane IV、Tucson IV、CX-5 KF、Fabia IV和GV70等12个既有尺寸组，没有重复输出既有组三维。

当前批次进度

* READY Ktype：35 / 100。
* READY 映射：35。
* 待处理/PENDING Ktype：65。
* 当前已引用尺寸组：21，其中本轮新建9组、复用既有12组。
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145050	145050	SUV	Taigo I		5	EU-VW-TAIGO-I-SUV-01	HIGH		READY
145053	145053	Hatchback	Born I		5	EU-CUPRA-BORN-I-HATCHBACK-01	HIGH		READY
145055	145055	Hatchback	Born I		5	EU-CUPRA-BORN-I-HATCHBACK-01	HIGH		READY
145056	145056	Hatchback	Born I		5	EU-CUPRA-BORN-I-HATCHBACK-01	HIGH		READY
145057	145057	Hatchback	Born I		5	EU-CUPRA-BORN-I-HATCHBACK-01	HIGH		READY
145068	145068	SUV	CX-30 I		5	EU-MAZDA-CX-30-I-SUV-01	HIGH		READY
145069	145069	SUV	CX-30 I		5	EU-MAZDA-CX-30-I-SUV-01	HIGH		READY
145071	145071	Wagon	308 III		5	EU-PEUGEOT-308-III-WAGON-01	HIGH		READY
145072	145072	Wagon	308 III		5	EU-PEUGEOT-308-III-WAGON-01	HIGH		READY
145073	145073	Wagon	308 III		5	EU-PEUGEOT-308-III-WAGON-01	HIGH		READY
145075	145075	Wagon	308 III		5	EU-PEUGEOT-308-III-WAGON-01	HIGH		READY
145077	145077	Wagon	308 III		5	EU-PEUGEOT-308-III-WAGON-01	HIGH		READY
145080	145080	Sedan	DS 9 I		4	EU-DS-DS9-I-SEDAN-01	HIGH	输入Model“Ds”对应DS 9 E-TENSE 360。	READY
145081	145081	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
145083	145083	SUV	Q4 e-tron I		5	EU-AUDI-Q4-E-TRON-I-SUV-01	HIGH		READY
145085	145085	SUV	Q4 e-tron I		5	EU-AUDI-Q4-E-TRON-I-SPORTBACK-01	HIGH	Sportback外廓。	READY
145086	145086	SUV	Q4 e-tron I		5	EU-AUDI-Q4-E-TRON-I-SPORTBACK-01	HIGH	Sportback外廓。	READY
145087	145087	SUV	Q4 e-tron I		5	EU-AUDI-Q4-E-TRON-I-SPORTBACK-01	HIGH	Sportback外廓。	READY
145088	145088	Sedan	A3 8Y		4	EU-AUDI-A3-8Y-RS3-SEDAN-01	HIGH	RS 3 Sedan宽体外廓。	READY
145089	145089	Hatchback	A3 8Y		5	EU-AUDI-A3-8Y-RS3-SPORTBACK-5D-01	HIGH	RS 3 Sportback宽体外廓。	READY
145093	145093	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
145094	145094	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
145123	145123	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-01	HIGH		READY
145128	145128	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-01	HIGH		READY
145129	145129	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-01	HIGH		READY
145131	145131	SUV	Bayon I		5	EU-HYUNDAI-BAYON-I-SUV-01	HIGH		READY
145197	145197	Hatchback	Octavia IV		5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
145198	145198	Wagon	Octavia IV		5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
145204	145204	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
145213	145213	Wagon	Megane IV		5	EU-RENAULT-MEGANE-IV-GRANDTOUR-WAGON-01	HIGH		READY
145223	145223	SUV	Tucson IV	NX4	5	EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	HIGH		READY
145235	145235	SUV	CX-5 II	KF	5	EU-MAZDA-CX-5-II-KF-SUV-PREFL-01	HIGH		READY
145238	145238	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145240	145240	Hatchback	Megane IV		5	EU-RENAULT-MEGANE-IV-HATCHBACK-01	HIGH		READY
145264	145264	SUV	GV70 I	JK1	5	EU-GENESIS-GV70-I-JK1-SUV-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CUPRA-BORN-I-HATCHBACK-01	4322	1809	1540	CUPRA Born official FAQ	https://www.cupraofficial.com/faqs/cupra-vehicles/cupra-born
EU-MAZDA-CX-30-I-SUV-01	4395	1795	1540	Mazda UK CX-30 specifications	https://www.mazda.co.uk/cars/mazda-cx-30/specs-and-compare/
EU-PEUGEOT-308-III-WAGON-01	4636	1852	1442	Peugeot UK New 308 SW dimensions	https://www.peugeot.co.uk/content/peugeot/worldwide/uk/en/index/models/new-308-sw.html
EU-DS-DS9-I-SEDAN-01	4934	1855	1460	DS 9 Price & Specification Guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds9pricesandspecs-6172ca39a3822.pdf
EU-AUDI-Q4-E-TRON-I-SUV-01	4588	1865	1632	Audi UK Q4 e-tron 40 Technical Data	https://press.audi.co.uk/assets/documents/original/16959-AudiQ440etronUKTechnicalDataMay2021.pdf
EU-AUDI-Q4-E-TRON-I-SPORTBACK-01	4588	1865	1614	Audi UK Q4 e-tron Sportback 40 Technical Data	https://press.audi.co.uk/assets/documents/original/28632-AudiQ4etronSportback40UKTechnicalDataJanuary2022.pdf
EU-AUDI-A3-8Y-RS3-SEDAN-01	4542	1851	1412	Audi UK RS 3 Saloon Technical Data	https://press.audi.co.uk/assets/documents/original/23941-AudiRS3Saloon400PSUKTechnicalDataOctober2021.pdf
EU-AUDI-A3-8Y-RS3-SPORTBACK-5D-01	4389	1851	1436	Audi UK RS 3 Sportback Technical Data	https://press.audi.co.uk/assets/documents/original/23942-AudiRS3Sportback400PSUKTechnicalDataOctober2021.pdf
EU-HYUNDAI-BAYON-I-SUV-01	4180	1775	1500	Hyundai BAYON Technical Specifications	https://dmassets.hyundai.com/is/content/hyundaiautoever/BAYON_Tech_Specpdf
```

下一步优先处理

1. 集中核对 Sprinter Tourer、Viano、Transit Bus，以及 Vivaro/Expert/Jumpy/Proace等商用车的长度、车顶和轴距分支。
2. 闭合 Porsche 911 992.1、Cayenne、Macan及不同 Taycan 车身外廓。
3. 批量处理 Mercedes C-Class、EQS、S-Class及剩余 Volvo、Renault、Hyundai、Toyota车型簇。

推进信号：CONTINUE

[1]: https://www.cupraofficial.com/faqs/cupra-vehicles/cupra-born?utm_source=chatgpt.com "CUPRA Born: Performance & Features"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 闭合 EQS、C-Class W206/S206、Taycan J1、812 Competizione及 Genesis G70 共16个新增 Ktype；另直接复用 GLC X253 facelift、Kadjar I facelift两个既有尺寸组。
* Taycan Cross Turismo按已确认高度差异拆为普通外廓与Turbo外廓；其余动力版本不重复建组。官方资料支持本轮新增尺寸组的三维及不含后视镜宽度。([Mercedes-Benz][1])

当前批次进度

* READY Ktype：53 / 100
* READY 映射：53
* PENDING Ktype：47
* 当前已引用尺寸组：31
* 本轮首次创建尺寸组：8
* 本轮新增引用的既有尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145121	145121	Hatchback	EQS I	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
145122	145122	Hatchback	EQS I	V297	5	EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	HIGH		READY
145130	145130	Wagon	Taycan I	J1	5	EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-01	HIGH	Cross Turismo外廓。	READY
145132	145132	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH		READY
145133	145133	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH		READY
145134	145134	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH		READY
145139	145139	Wagon	Taycan I	J1	5	EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-01	HIGH	Cross Turismo外廓。	READY
145140	145140	Wagon	Taycan I	J1	5	EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-TURBO-01	HIGH	Turbo车型高度边界。	READY
145141	145141	Wagon	Taycan I	J1	5	EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-01	HIGH	Cross Turismo外廓。	READY
145147	145147	Sedan	Taycan I	J1	4	EU-PORSCHE-TAYCAN-J1-SEDAN-01	HIGH		READY
145149	145149	Wagon	C-Class W206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH		READY
145150	145150	Wagon	C-Class W206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH		READY
145151	145151	Wagon	C-Class W206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH		READY
145177	145177	SUV	GLC X253 facelift	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-PREFL-01	HIGH	2019年改款动力版本沿用缓存外廓组。	READY
145212	145212	SUV	Kadjar I facelift		5	EU-RENAULT-KADJAR-I-SUV-PREFL-01	HIGH	2021动力版本沿用缓存外廓组。	READY
145257	145257	Coupe	812 Competizione		2	EU-FERRARI-812-COMPETIZIONE-COUPE-01	HIGH	Competizione外廓不同于812 Superfast。	READY
145266	145266	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH		READY
145267	145267	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-EQS-V297-HATCHBACK-01	5216	1926	1512	Mercedes-Benz EQS official vehicle details	https://tax.mercedes-benz.co.uk/details/?derivative=EQS+450PLUSSIGN+AMG+Line+Premium+360hp+265kW+Auto&derivative_extra=&make=Mercedes-Benz&model=EQS
EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-01	4974	1964	1409	Porsche Taycan Cross Turismo official press kit	https://newsroom.porsche.com/dam/jcr%3A45d11b14-60b6-47ef-bf12-adef0623bad4/PM_Taycan_CT_EN.pdf
EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	4751	1820	1437	Mercedes-Benz C-Class Saloon official brochure	https://www.mercedes-benz-mena.com/static/pdfs/c-klasse-w206-epaper-24-2-02-eng.pdf
EU-PORSCHE-TAYCAN-J1-CROSS-TURISMO-TURBO-01	4974	1964	1412	Porsche Taycan Cross Turismo official press kit	https://newsroom.porsche.com/dam/jcr%3A45d11b14-60b6-47ef-bf12-adef0623bad4/PM_Taycan_CT_EN.pdf
EU-PORSCHE-TAYCAN-J1-SEDAN-01	4963	1966	1379	Porsche Taycan 4S with Performance Battery Plus technical data	https://newsroom.porsche.com/dam/jcr%3A08184bb9-d8af-44e5-9dba-019dfafce609/PAG_TD_Taycan4S_withPerformancebatteryPlus_EN.pdf
EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	4751	1820	1455	Mercedes-Benz C-Class Estate official specifications	https://www.mercedes-benz.co.uk/passengercars/models/estate/c-class/overview.html
EU-FERRARI-812-COMPETIZIONE-COUPE-01	4696	1971	1276	Ferrari 812 Competizione official technical specifications	https://www.ferrari.com/en-EN/corporate/articles/812-competizione-and-812-competizione-a-two-interpretations-of-ferraris-racing-soul
EU-GENESIS-G70-I-FACELIFT-SEDAN-01	4685	1850	1400	Genesis G70 official European price list	https://org-eu.genesis.com/content/dam/genesis-web-eu/site/document/ch/pricelist/Genesis_G70_Pricelist_CH_English.pdf
```

下一步优先处理

1. 批量闭合 Vivaro、Expert、Jumpy、Proace及Transit Connect的车长、车顶和车身形式分支，优先复用现有商用车尺寸组。
2. 处理 Sprinter Tourer、Viano、Transit Bus等仍需确认轴距和车顶边界的多外廓Ktype。
3. 闭合剩余 Porsche 911、Cayenne、Macan及 Renault Kangoo、Express、Talisman车型簇。

推进信号：CONTINUE

[1]: https://tax.mercedes-benz.co.uk/details/?derivative=EQS+450PLUSSIGN+AMG+Line+Premium+360hp+265kW+Auto&derivative_extra=&make=Mercedes-Benz&model=EQS&utm_source=chatgpt.com "EQS EQS 450+ AMG Line Premium 360hp 265kW Auto Vehicle details | Mercedes-Benz"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 闭合 Porsche Cayenne Turbo S E-Hybrid、911 992.1 GTS 三种车身、MG5 EV、Renault Espace V/Talisman、Volvo V60/V60 Cross Country、Mercedes-Benz S-Class W223、Hyundai Staria Van、Lotus Elise Sport 240，共新增 18 个 READY Ktype；Dacia Duster 直接复用已有尺寸组。
* 本轮首次创建 13 个尺寸组；动力、驱动形式相同外廓均批量关联，没有重复建组。

当前批次进度

* READY Ktype：71 / 100
* READY 映射：71
* PENDING Ktype：29
* 当前已引用尺寸组：45
* 本轮首次创建尺寸组：13
* 本轮新增引用的既有尺寸组：1
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145106	145106	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-TURBO-S-E-HYBRID-SUV-01	HIGH		READY
145108	145108	Targa	911 992.1	992	2	EU-PORSCHE-911-992-1-GTS-TARGA-01	HIGH	Targa车顶外廓。	READY
145113	145113	Convertible	911 992.1	992	2	EU-PORSCHE-911-992-1-GTS-CONVERTIBLE-01	HIGH	Cabriolet外廓。	READY
145114	145114	Convertible	911 992.1	992	2	EU-PORSCHE-911-992-1-GTS-CONVERTIBLE-01	HIGH	Cabriolet外廓。	READY
145115	145115	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-GTS-COUPE-01	HIGH	Coupe外廓。	READY
145116	145116	Coupe	911 992.1	992	2	EU-PORSCHE-911-992-1-GTS-COUPE-01	HIGH	Coupe外廓。	READY
145148	145148	Wagon	MG5 EV I		5	EU-MG-MG5-EV-I-WAGON-01	HIGH		READY
145155	145155	MPV	Espace V facelift		5	EU-RENAULT-ESPACE-V-FACELIFT-MPV-01	HIGH		READY
145168	145168	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
145169	145169	Wagon	V60 II Cross Country		5	EU-VOLVO-V60-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country增高及外扩外廓。	READY
145181	145181	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	HIGH		READY
145185	145185	Van	Staria I		5	EU-HYUNDAI-STARIA-I-VAN-01	HIGH		READY
145186	145186	Convertible	Elise III		2	EU-LOTUS-ELISE-III-SPORT-240-CONVERTIBLE-01	HIGH		READY
145208	145208	Wagon	Talisman I facelift		5	EU-RENAULT-TALISMAN-I-FACELIFT-WAGON-01	HIGH		READY
145209	145209	Wagon	Talisman I facelift		5	EU-RENAULT-TALISMAN-I-FACELIFT-WAGON-01	HIGH		READY
145210	145210	Sedan	Talisman I facelift		4	EU-RENAULT-TALISMAN-I-FACELIFT-SEDAN-01	HIGH		READY
145211	145211	Sedan	Talisman I facelift		4	EU-RENAULT-TALISMAN-I-FACELIFT-SEDAN-01	HIGH		READY
145234	145234	SUV	Duster I facelift		5	EU-DACIA-DUSTER-I-FACELIFT-SUV-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-CAYENNE-III-TURBO-S-E-HYBRID-SUV-01	4926	1983	1673	Porsche Cayenne Turbo S E-Hybrid official technical data	https://newsroom.porsche.com/dam/jcr%3A1a25285e-17ea-4127-8ad8-d9302fa04fa2/PAG_Cayenne_Turbo_S_E-Hybrid_EN.pdf
EU-PORSCHE-911-992-1-GTS-TARGA-01	4533	1852	1299	Porsche 911 GTS official press kit;Porsche Finder 911 Targa 4 GTS MY24	https://newsroom.porsche.com/dam/jcr%3A51ff1da3-7997-4859-9bc8-b44c8994d149/PAG-911-GTS-EN.pdf;https://finder.porsche.com/gb/en-GB/details/porsche-911-targa-4-gts-my24-preowned-449G89
EU-PORSCHE-911-992-1-GTS-CONVERTIBLE-01	4533	1852	1300	Porsche 911 GTS official press kit;Porsche Finder 911 Carrera GTS Cabriolet MY24	https://newsroom.porsche.com/dam/jcr%3A51ff1da3-7997-4859-9bc8-b44c8994d149/PAG-911-GTS-EN.pdf;https://finder.porsche.com/gb/en-GB/details/porsche-911-carrera-gts-cabriolet-my24-preowned-G78OEQ
EU-PORSCHE-911-992-1-GTS-COUPE-01	4533	1852	1301	Porsche 911 Carrera GTS official technical data	https://newsroom.porsche.com/dam/jcr%3A4d2ef307-026f-4090-9b8d-7f6e67c674a3/PAG_911-Carrera-GTS_PDK_TD_EN.pdf
EU-MG-MG5-EV-I-WAGON-01	4544	1818	1543	MG5 EV Long Range official owner manual	https://www.mg.co.uk/sites/default/files/2022-01/MG5%20EV%20Long%20Range%20Owner%20Manual.pdf
EU-RENAULT-ESPACE-V-FACELIFT-MPV-01	4857	1888	1677	Renault Espace official brochure	https://cdn.group.renault.com/ren/es/modelos/nuevo-espace/catalogo/catalogo_espace.pdf
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo V60 official dimensions	https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V60-II-CROSS-COUNTRY-WAGON-01	4784	1893	1504	Volvo V60 Cross Country official dimensions	https://www.volvocars.com/en-ca/support/car/v60-cross-country/21w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	5179	1954	1503	Mercedes-Benz S-Class official brochure	https://www.mercedes-benz-mena.com/static/pdfs/s-klasse-w223-epaper-24-1-02-eng.pdf
EU-HYUNDAI-STARIA-I-VAN-01	5253	1997	2000	Hyundai STARIA Load official specification	https://www.hyundai.com/content/dam/hyundai/au/en/models/staria-load/2021/docs/STARIA-Load_2-seat_Spec-Table_Nov_2021.pdf
EU-LOTUS-ELISE-III-SPORT-240-CONVERTIBLE-01	3800	1720	1130	Lotus Elise Sport 240 Final Edition official specifications	https://www.lotus-cars.jp/news/wp-content/uploads/2021/02/FINAL_EDITION_PRICE_2021.2.8.pdf
EU-RENAULT-TALISMAN-I-FACELIFT-WAGON-01	4865	1870	1465	Renault Talisman Grandtour official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Neuer_Talisman_Grandtour_PL_f.pdf
EU-RENAULT-TALISMAN-I-FACELIFT-SEDAN-01	4849	1868	1456	Renault Talisman official price list	https://cdn.group.renault.com/ren/ch/renault-new-cars/pricelists/Renault_Talisman_PL_f.pdf
```

下一步优先处理

1. 集中拆分 Sprinter Tourer、Viano、Transit Bus的轴距与车顶分支。
2. 批量闭合 Vivaro、Expert、Jumpy、Proace及Transit Connect现有商用车尺寸组关联。
3. 处理 Combo-e、Kangoo、Express、Proace City混合车身，以及剩余 RAM TRX、Macan、Q7、BYD Dolphin。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 闭合 RAM 1500 TRX、Porsche Macan、Audi Q7、Opel Combo-e Life、Toyota Proace City/Verso Electric及 BYD Dolphin，共处理 8 个 Ktype；因长度或外观套件差异形成 12 条映射和 12 个新尺寸组。
* BYD Dolphin 70 kW覆盖 4070 mm与4125 mm两种外廓，130 kW Knight外观套件长度为4150 mm，因此未将三个外廓错误合并。([InsideEVs][1])

当前批次进度

* READY Ktype：79 / 100
* READY 映射：83
* PENDING Ktype：21
* 当前已引用尺寸组：57
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145125	145125	Pickup	Ram 1500 DT	DT	4	EU-RAM-1500-DT-TRX-CREW-CAB-PICKUP-01	HIGH	TRX宽体Crew Cab外廓。	READY
145145_standard	145145	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-K9-MPV-STANDARD-01	MEDIUM	输入未标车长；标准轴距外廓。	READY
145145_xl	145145	MPV	Combo E	K9	5	EU-OPEL-COMBO-E-K9-MPV-XL-01	MEDIUM	输入未标车长；XL长轴距外廓。	READY
145236	145236	SUV	Macan I facelift	95B	5	EU-PORSCHE-MACAN-I-95B-SUV-FACELIFT-01	HIGH		READY
145258	145258	SUV	Q7 II facelift	4M	5	EU-AUDI-Q7-II-4M-FACELIFT-SUV-01	HIGH		READY
145261_swb	145261	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	MEDIUM	输入未标车长；SWB厢式外廓。	READY
145261_lwb	145261	Van	Proace City I	K9		EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	MEDIUM	输入未标车长；LWB厢式外廓。	READY
145263_short	145263	Hatchback	Dolphin I	EA1	5	EU-BYD-DOLPHIN-I-HATCHBACK-SHORT-01	MEDIUM	70kW、30.7kWh短外廓。	READY
145263_standard	145263	Hatchback	Dolphin I	EA1	5	EU-BYD-DOLPHIN-I-HATCHBACK-STANDARD-01	MEDIUM	70kW、44.9kWh标准外廓。	READY
145265	145265	Hatchback	Dolphin I	EA1	5	EU-BYD-DOLPHIN-I-HATCHBACK-KNIGHT-01	MEDIUM	130kW Knight外观套件外廓。	READY
145268_swb	145268	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	MEDIUM	输入未标车长；SWB乘用外廓。	READY
145268_lwb	145268	MPV	Proace City Verso I	K9	5	EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	MEDIUM	输入未标车长；LWB乘用外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RAM-1500-DT-TRX-CREW-CAB-PICKUP-01	5916	2235	2055	RAM 2021 Ram 1500 TRX official specifications	https://s3.amazonaws.com/chryslermedia.iconicweb.com/mediasite/specs/2021_RAM_1500_TRX_Specificationsncds40e91jnt64taolkbbpi9eq.pdf
EU-OPEL-COMBO-E-K9-MPV-STANDARD-01	4403	1848	1841	Opel Combo-e Life official launch information;Opel Combo official owner's manual	https://www.media.stellantis.com/be-nl/opel/press/elektrische-alledaagse-held-nieuwe-opel-combo-e-life;https://public-servicebox.opel.com/OVddb/OV/en_GB/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOBSE2111-en_16_online.pdf
EU-OPEL-COMBO-E-K9-MPV-XL-01	4753	1848	1880	Opel Combo-e Life official launch information;Opel Combo official owner's manual	https://www.media.stellantis.com/be-nl/opel/press/elektrische-alledaagse-held-nieuwe-opel-combo-e-life;https://public-servicebox.opel.com/OVddb/OV/en_GB/Combo_E/2019_2025/2021_11/manual_user/ID-OCBEOBSE2111-en_16_online.pdf
EU-PORSCHE-MACAN-I-95B-SUV-FACELIFT-01	4726	1922	1621	Porsche Macan official technical data	https://newsroom.porsche.com/dam/jcr%3Ab47ff7c0-5982-4f32-8831-b3eda1ad486e/PAG_Macan_TD_EN.pdf
EU-AUDI-Q7-II-4M-FACELIFT-SUV-01	5063	1970	1741	Audi Q7 official dimensions sheet	https://www.audi.com/en/publications/dimensions/dimensions-q7-1446/download
EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	4403	1848	1880	Toyota Proace City official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614163030210223MProaceCityTechSpec.pdf
EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	4753	1848	1880	Toyota Proace City official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614163030210223MProaceCityTechSpec.pdf
EU-BYD-DOLPHIN-I-HATCHBACK-SHORT-01	4070	1770	1570	InsideEVs BYD Dolphin launch specifications	https://insideevs.com/news/529696/byd-dolphin-chengdu-auto-show/
EU-BYD-DOLPHIN-I-HATCHBACK-STANDARD-01	4125	1770	1570	InsideEVs BYD Dolphin launch specifications	https://insideevs.com/news/529696/byd-dolphin-chengdu-auto-show/
EU-BYD-DOLPHIN-I-HATCHBACK-KNIGHT-01	4150	1770	1570	InsideEVs BYD Dolphin launch specifications	https://insideevs.com/news/529696/byd-dolphin-chengdu-auto-show/
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	4403	1848	1800	Toyota Europe Proace City official press release	https://newsroom.toyota.eu/download/699868/pproace-city-759820.pdf
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	4753	1848	1812	Toyota Europe Proace City official press release	https://newsroom.toyota.eu/download/699868/pproace-city-759820.pdf
```

下一步优先处理

1. 拆分 Sprinter Tourer、Viano及Transit Bus的轴距、车长和车顶分支。
2. 复用或补齐 Vivaro、Expert、Jumpy、Proace现有中型厢式车尺寸组。
3. 集中闭合 Renault Express、Kangoo及Transit Connect的Van、MPV和长短轴边界。

推进信号：CONTINUE

[1]: https://insideevs.com/news/529696/byd-dolphin-chengdu-auto-show/ "BYD Launches Dolphin At The Chengdu Auto Show"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
更新点

* 闭合 Renault Express、Kangoo III 与 Ford Transit Connect V408 共 13 个 Ktype。Express 按输入中的 Van/MPV 合并边界拆分；Kangoo 混合车身 Ktype 同样拆为 Van 与 MPV。官方尺寸资料明确区分 Express Van、五座 Express 和 Kangoo Van，Kangoo III 乘用版尺寸由 Auto-Data 对应代际记录补齐。
* Transit Connect 1.0 版本闭合为 L1 Van、L2 Van 与 L1 Double Cab-in-Van 三个已存在外廓分支，直接复用跨批次尺寸组；未重复创建尺寸组。Ford 资料列明该发动机适用于 Van 与 Double Cab-in-Van，并分别列出 L1/L2 外廓。

当前批次进度

* READY Ktype：92 / 100
* READY 映射：106
* PENDING Ktype：8
* 当前已引用尺寸组：64
* 本轮首次创建尺寸组：4
* 本轮新增引用的既有尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145154_van_l1	145154	Van	Transit Connect V408	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L1-01	MEDIUM	L1厢式外廓。	READY
145154_van_l2	145154	Van	Transit Connect V408	V408		EU-FORD-TRANSIT-CONNECT-V408-VAN-L2-01	MEDIUM	L2厢式外廓。	READY
145154_dciv_l1	145154	Van	Transit Connect V408	V408		EU-FORD-TRANSIT-CONNECT-V408-DCIV-L1-01	MEDIUM	L1 Double Cab-in-Van外廓。	READY
145220_van	145220	Van	Express I			EU-RENAULT-EXPRESS-I-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145220_mpv	145220	MPV	Express I		5	EU-RENAULT-EXPRESS-I-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145221_van	145221	Van	Express I			EU-RENAULT-EXPRESS-I-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145221_mpv	145221	MPV	Express I		5	EU-RENAULT-EXPRESS-I-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145222_van	145222	Van	Express I			EU-RENAULT-EXPRESS-I-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145222_mpv	145222	MPV	Express I		5	EU-RENAULT-EXPRESS-I-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145224	145224	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	HIGH		READY
145225	145225	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	HIGH		READY
145226	145226	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	HIGH		READY
145242_van	145242	Van	Kangoo III			EU-RENAULT-KANGOO-III-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145242_mpv	145242	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145243_van	145243	Van	Kangoo III			EU-RENAULT-KANGOO-III-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145243_mpv	145243	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145244_van	145244	Van	Kangoo III			EU-RENAULT-KANGOO-III-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145244_mpv	145244	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145245_van	145245	Van	Kangoo III			EU-RENAULT-KANGOO-III-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145245_mpv	145245	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145246_van	145246	Van	Kangoo III			EU-RENAULT-KANGOO-III-VAN-01	MEDIUM	输入BodyStyle合并；Van分支。	READY
145246_mpv	145246	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	MEDIUM	输入BodyStyle合并；MPV分支。	READY
145256	145256	MPV	Kangoo III		5	EU-RENAULT-KANGOO-III-MPV-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-EXPRESS-I-VAN-01	4393	1775	1811	Renault Express Van official brochure	https://cdn.group.renault.com/ren/ch/renault-new-cars/brochures/Renault_Express_Van_BR_f.pdf
EU-RENAULT-EXPRESS-I-MPV-01	4394	1775	1804	Renault Express official brochure	https://cdn.group.renault.com/ren/ma/brochure/E-Brochure%20EXPRESS-V2-24.pdf.asset.pdf/1a9c2d3f1d.pdf
EU-RENAULT-KANGOO-III-VAN-01	4486	1919	1864	Renault Kangoo Van and Express Van official brochure	https://cdn.group.renault.com/ren/fr/pro/brochures/Brochure_Kangoo_Van_Express_Van.pdf.asset.pdf/3d5335877a.pdf
EU-RENAULT-KANGOO-III-MPV-01	4486	1919	1838	Auto-Data Renault Kangoo III specifications	https://www.auto-data.net/en/renault-kangoo-model-1045
```

下一步优先处理

1. 闭合 Opel Vivaro、Peugeot Expert、Citroën Jumpy及Toyota Proace四个中型厢式车 Ktype，优先复用现有长短轴和车顶尺寸组。
2. 集中拆分 Mercedes-Benz Sprinter Tourer、Viano与Ford Transit Bus的轴距、车长和车顶分支。
3. 剩余待处理 Ktype：145090、145091、145126、145135、145137、145194、145196、145254。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
更新点

* 闭合 Opel Vivaro C 2.0 145、Peugeot Expert BlueHDi 145、Citroën Jumpy III BlueHDi 145，共 3 个 Ktype、6 条物理分支。
* Vivaro 2.0 145 的 3100 kg Panel Van 同时覆盖 4959 mm 与 5309 mm 两种长度，分别采用对应增载悬架高度；新建 2 个尺寸组。
* Expert 145 的 Standard、Long 均直接命中已有 1400 kg 高度尺寸组，不重复输出尺寸事实。
* Jumpy 145 覆盖 M 与 XL，均为增载外廓；新建 2 个尺寸组。

当前批次进度

* READY Ktype：95 / 100
* READY 映射：112
* PENDING Ktype：5
* 当前已引用尺寸组：70
* 本轮首次创建尺寸组：4
* 本轮新增引用的既有尺寸组：2
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145135_m	145135	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-M-3100-01	MEDIUM	输入未标车长；M增载Panel Van外廓。	READY
145135_l	145135	Van	Vivaro C	K0		EU-OPEL-VIVARO-C-K0-VAN-L-3100-01	MEDIUM	输入未标车长；L增载Panel Van外廓。	READY
145137_standard	145137	Van	Expert III			EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	MEDIUM	输入未标车长；Standard 1400kg Panel Van外廓。	READY
145137_long	145137	Van	Expert III			EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	MEDIUM	输入未标车长；Long 1400kg Panel Van外廓。	READY
145194_m	145194	Van	Jumpy III			EU-CITROEN-JUMPY-III-VAN-M-3100-01	MEDIUM	输入未标车长；M增载Van外廓。	READY
145194_xl	145194	Van	Jumpy III			EU-CITROEN-JUMPY-III-VAN-XL-3100-01	MEDIUM	输入未标车长；XL增载Van外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-C-K0-VAN-M-3100-01	4959	1920	1904	Vauxhall Vivaro Model Year 2022B official Price and Specification Guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/vivaro/price-guides/Vivaro_Spec_ePG_13_May_2022_Library.pdf
EU-OPEL-VIVARO-C-K0-VAN-L-3100-01	5309	1920	1935	Vauxhall Vivaro Model Year 2022B official Price and Specification Guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Vans/vivaro/price-guides/Vivaro_Spec_ePG_13_May_2022_Library.pdf
EU-CITROEN-JUMPY-III-VAN-M-3100-01	4959	1920	1930	Citroën Jumpy February 2022 Technical Specifications	https://www.citroenlaspalmas.com/admin/upload/628-ct-jumpy-febrero-2022.pdf
EU-CITROEN-JUMPY-III-VAN-XL-3100-01	5309	1920	1935	Citroën Jumpy February 2022 Technical Specifications	https://www.citroenlaspalmas.com/admin/upload/628-ct-jumpy-febrero-2022.pdf
```

下一步优先处理

1. 先解决 Toyota Proace 2.0 D-4D 145 的市场高度差异，确认应命中既有 Medium/Long 组还是为冲突尺寸组还是为冲突尺寸创建后续序号。
2. 集中拆分 Sprinter 4-T Tourer 411/419 CDI的车长和车顶分支。
3. 闭合 Viano CDI 2.2与Transit 2.2 TDCi RWD Bus的多车长、多车顶外廓。
4. 剩余 Ktype：145090、145091、145126、145196、145254。

推进信号：ONTINUE


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 闭合 Ktype `145126`。该 70 kW Viano 对应 `639.711` 与 `639.713` 两个明确车身代码，分别映射 Compact 与 Long；三维采用 Mercedes-Benz 官方档案中相同车身代码的外廓数据。([Autodoc24][1])
* 闭合 Ktype `145196`。Toyota 官方资料确认 106 kW 的 `2.0D 140` 覆盖 Medium 与 Long Van，宽度均为不含后视镜的 1920 mm。Medium 复用现有高车身组；Long 官方高度为 1940 mm，与既有 `LONG-01` 的 1935 mm 冲突，因此未覆盖旧组，创建 `LONG-02`。([Toyota Media Site][2])

## 当前批次进度

* READY Ktype：97 / 100
* READY 映射：116
* PENDING Ktype：3
* 当前已引用尺寸组：73
* 本轮首次创建尺寸组：3
* 本轮新增引用的既有尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145126_compact	145126	MPV	Viano W639 facelift	639.711	4	EU-MERCEDES-BENZ-VIANO-W639-FACELIFT-MPV-COMPACT-01	HIGH	639.711 Compact外廓。	READY
145126_long	145126	MPV	Viano W639 facelift	639.713	4	EU-MERCEDES-BENZ-VIANO-W639-FACELIFT-MPV-LONG-01	HIGH	639.713 Long外廓。	READY
145196_medium	145196	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-MEDIUM-HIGH-01	MEDIUM	输入未标车长；Medium 2.0D 140 Panel Van外廓。	READY
145196_long	145196	Van	Proace II			EU-TOYOTA-PROACE-II-VAN-LONG-02	MEDIUM	输入未标车长；Long 2.0D 140 Panel Van外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-VIANO-W639-FACELIFT-MPV-COMPACT-01	4763	1901	1875	Mercedes-Benz Public Archive Viano CDI 2.2 compact 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-compact-2010---2014.xhtml?oid=193897440
EU-MERCEDES-BENZ-VIANO-W639-FACELIFT-MPV-LONG-01	5008	1901	1875	Mercedes-Benz Public Archive Viano CDI 2.2 long 2010-2014	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Viano-CDI-22-long-2010---2014.xhtml?oid=193897441
EU-TOYOTA-PROACE-II-VAN-LONG-02	5309	1920	1940	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220801M-Proace-Press-Pack.pdf
```

## 下一步优先处理

1. 确认 Sprinter Tourer `145090`、`145091` 的 `907.741/907.743/907.745` 车长与低顶、高顶适用边界。
2. 确认 Transit Minibus `145254` 的 155 PS 动力实际覆盖哪些 MWB、LWB及加长高顶分支。
3. 三个剩余 Ktype 闭合后立即执行一次机械检查，并在下一条回复输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/clutch-master-cylinder-10161/mercedes-benz/viano/viano-w639/145126-cdi-2-2-639-711-639-713?utm_source=chatgpt.com "Clutch master cylinder Mercedes Viano W639 CDI 2.2 95 hp Diesel ..."
[2]: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220801M-Proace-Press-Pack.pdf "Microsoft Word - 220801M - Proace full release"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

