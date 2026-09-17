# 任务：all 第 5401-5500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0055__49ff9e71


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5401-5500 行

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
all 第 5401-5500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5401-5500_ktype_dimension_mapping_final.tsv
- all_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-E-TRON-I-GE-SUV-01	4901	1935	1629
EU-AUDI-Q3-II-F3-RS-Q3-SUV-01	4506	1851	1602
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-XDRIVE-FACELIFT-01	4633	1811	1434
EU-BMW-3-F31-WAGON-XDRIVE-PREFL-01	4624	1811	1434
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-330E-SEDAN-RWD-PREFL-01	4709	1827	1444
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X4-F98-M-COMPETITION-SUV-01	4758	1927	1620
EU-BMW-X4-F98-M-SUV-01	4758	1927	1618
EU-BMW-X4-G02-M40D-SUV-01	4752	1938	1621
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621
EU-BMW-X4-G02-SUV-STANDARD-01	4752	1918	1621
EU-CITROEN-SPACETOURER-I-MPV-M-01	4959	1920	1920
EU-CITROEN-SPACETOURER-I-MPV-XL-01	5309	1920	1920
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XS-01	4606	1920	1905
EU-DACIA-DOKKER-I-F67-VAN-01	4363	1751	1809
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814
EU-FIAT-500X-I-FACELIFT-AWD-SUV-01	4269	1796	1607
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450
EU-KIA-RIO-IV-YB-SEDAN-PREFL-01	4384	1725	1450
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-01	4597	2069	1727
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	4597	1904	1727
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-PREFL-01	4599	2069	1724
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-PREFL-01	4850	1983	1780
EU-MAZDA-3-II-BL-FACELIFT-SEDAN-01	4580	1755	1470
EU-MAZDA-3-IV-BP-HATCHBACK-01	4460	1795	1435
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440
EU-MAZDA-323-BA-SEDAN-01	4340	1710	1420
EU-MAZDA-MX-30-I-SUV-01	4395	1795	1570
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
EU-MERCEDES-BENZ-E-KLASSE-A238-AMG-E53-CONVERTIBLE-01	4848	1860	1425
EU-MERCEDES-BENZ-E-KLASSE-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-A238-E300D-CONVERTIBLE-01	4826	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C124-COUPE-PHASE-I-01	4655	1740	1394
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E200-4MATIC-01	4945	1852	1461
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	4945	1852	1476
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	4945	1852	1467
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	4935	1852	1481
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-FACELIFT-01	4954	2018	1720
EU-MERCEDES-BENZ-GLE-C167-AMG-GLE63-COUPE-PREFL-01	4961	2018	1720
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	4947	2018	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	4947	2018	1785
EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	5052	1913	1422
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424
EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	5246	1899	1494
EU-MERCEDES-BENZ-S-KLASSE-V222-S560E-SEDAN-FACELIFT-LWB-01	5255	1905	1503
EU-MERCEDES-BENZ-S-KLASSE-W109-300SEL-SEDAN-01	5000	1810	1415
EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	5096	1871	1479
EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	5125	1905	1493
EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	5116	1899	1496
EU-NISSAN-NV400-I-FWD-CHASSIS-DOUBLE-L3H1-01	6199	2070	2263
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L2H1-01	5549	2070	2265
EU-NISSAN-NV400-I-FWD-CHASSIS-SINGLE-L3H1-01	6199	2070	2258
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307
EU-NISSAN-NV400-I-FWD-VAN-L1H2-01	5048	2070	2500
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499
EU-NISSAN-NV400-I-FWD-VAN-L2H3-01	5548	2070	2749
EU-NISSAN-NV400-I-FWD-VAN-L3H2-01	6198	2070	2488
EU-NISSAN-NV400-I-FWD-VAN-L3H3-01	6198	2070	2744
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-DRW-01	5643	2070	2283
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L2H1-SRW-01	5643	2070	2284
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-DRW-01	6193	2070	2283
EU-NISSAN-NV400-I-RWD-CHASSIS-SINGLE-L3H1-SRW-01	6293	2070	2276
EU-NISSAN-NV400-I-RWD-VAN-L3H2-DRW-01	6198	2070	2549
EU-NISSAN-NV400-I-RWD-VAN-L3H2-SRW-01	6198	2070	2527
EU-NISSAN-NV400-I-RWD-VAN-L3H3-DRW-01	6198	2070	2815
EU-NISSAN-NV400-I-RWD-VAN-L3H3-SRW-01	6198	2070	2786
EU-OPEL-ASTRA-K-HATCHBACK-CNG-01	4370	1809	1485
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609
EU-OPEL-ZAFIRA-A-T98-MPV-FACELIFT-01	4317	1742	1684
EU-OPEL-ZAFIRA-A-T98-MPV-PREFL-01	4317	1742	1684
EU-OPEL-ZAFIRA-B-A05-MPV-FACELIFT-01	4467	1801	1635
EU-OPEL-ZAFIRA-B-A05-MPV-PREFL-01	4467	1801	1635
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905
EU-OPEL-ZAFIRA-TOURER-C-P12-MPV-FACELIFT-01	4666	1884	1660
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300
EU-PORSCHE-911-992-TARGA-4-01	4519	1852	1297
EU-PORSCHE-911-992-TARGA-4S-01	4519	1852	1299
EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	4535	1900	1301
EU-PORSCHE-911-992-TURBO-S-COUPE-01	4535	1900	1303
EU-PORSCHE-911-997-1-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-2-TARGA-4S-01	4435	1852	1300
EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	4929	1983	1676
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	5049	1937	1428
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603
EU-SKODA-KODIAQ-I-RS-SUV-PREFL-01	4699	1882	1686
EU-SKODA-KODIAQ-I-SUV-FACELIFT-01	4697	1882	1661
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039
EU-STREETSCOOTER-WORK-L-BOX-VAN-01	5784	1925	2347
EU-STREETSCOOTER-WORK-L-PICKUP-01	5840	1814	1859
EU-STREETSCOOTER-WORK-L-PURE-CHASSIS-01	5784	1796	1867
EU-STREETSCOOTER-WORK-PICKUP-01	4741	1814	1859
EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	4676	1796	1861
EU-TOYOTA-HIGHLANDER-XU50-SUV-PREFL-01	4865	1925	1730
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-FACELIFT-01	3640	1660	1500
EU-TOYOTA-YARIS-I-XP10-VAN-HATCHBACK-3D-PREFL-01	3615	1660	1500
EU-TOYOTA-YARIS-III-FACELIFT-GRMN-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-FACELIFT-HATCHBACK-01	3945	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-FACELIFT-01	3950	1695	1510
EU-TOYOTA-YARIS-III-XP130-VAN-3D-PREFL-01	3885	1695	1510
EU-TOYOTA-YARIS-IV-XP210-GR-HATCHBACK-3D-01	3995	1805	1455
EU-TOYOTA-YARIS-IV-XP210-HATCHBACK-01	3940	1745	1500
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	4866	1871	1462
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A5	40 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	150	204	Sep 2020	-	2024-03-01	141630
VW	Derby	1.1	Stufenheck	Frontantrieb	Benzin	38	52	Feb 1977	Sep 1981	2024-03-01	141631
Hyundai	Terracan	2.5 TD 4WD	Kasten/SUV	Allrad	Diesel	74	101	Dec 2001	Dec 2006	2024-03-01	141653
Hyundai	Terracan	2.9 Crdi 4WD	Kasten/SUV	Allrad	Diesel	110	150	Nov 2001	Dec 2006	2024-03-01	141655
Hyundai	Terracan	2.9 Crdi 4WD	Kasten/SUV	Allrad	Diesel	120	163	Nov 2003	Dec 2006	2024-03-01	141657
Toyota	Yaris	1.5	SUV	Frontantrieb	Benzin	92	125	Sep 2020	-	2024-03-01	141660
Citroën	Spacetourer	2.0 Bluehdi 145	Bus	Frontantrieb	Diesel	106	144	Sep 2020	Apr 2025	2025-12-01	141676
Citroën	Spacetourer	Ë-spacetourer	Bus	Frontantrieb	Elektro	100	136	Sep 2020	Oct 2023	2024-07-01	141677
Nissan	Nv400	DCI 180	Bus	Frontantrieb	Diesel	132	179	Jan 2020	Dec 2022	2026-03-01	141684
Ligier	Pulse 3 threewheeler	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	3	4	Jan 2018	-	2024-03-01	141702
VW	Arteon	2.0 TDI 4motion	Kombi	Allrad	Diesel	147	200	Sep 2020	-	2024-03-01	141710
Fiat	500x	1	SUV	Frontantrieb	Benzin	84	114	Jun 2018	-	2024-03-01	141711
Porsche	Panamera	2.9	Schrägheck	Heckantrieb	Benzin	243	330	Apr 2019	Dec 2023	2024-08-01	141712
Porsche	Cayenne	4.0 GTS AWD	SUV	Allrad	Benzin	338	460	May 2017	May 2023	2026-03-01	141721
Porsche	911	3.8 Turbo	Coupe	Allrad	Benzin	427	581	Mar 2020	May 2025	2026-03-01	141723
Porsche	911	3.8 Turbo	Cabriolet	Allrad	Benzin	427	581	Mar 2020	May 2024	2024-08-01	141724
Porsche	Panamera	4.0 GTS	Schrägheck	Allrad	Benzin	353	480	Aug 2020	Dec 2023	2024-08-01	141729
Porsche	Panamera	4.0 Turbo S	Schrägheck	Allrad	Benzin	463	630	Aug 2020	Dec 2023	2024-08-01	141730
BMW	5	545 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	290	394	Nov 2020	Jun 2023	2024-03-01	141737
Streetscooter	Work	Electric	Kasten	Frontantrieb	Elektro	51	69	Mar 2020	Jul 2022	2024-03-01	141738
Streetscooter	Work xl	Electric	Pritsche/Fahrgestell	Frontantrieb	Elektro	90	122	Nov 2018	Jul 2022	2024-03-01	141739
Volvo	S60 iii	T5 Polestar AWD	Stufenheck	Allrad	Benzin	186	253	Jul 2019	Dec 2021	2024-05-01	141756
Isuzu	D-Max iii	1.9 DDI	Pick-up	Heckantrieb	Diesel	110	150	Nov 2019	-	2024-03-01	141767
VW	Golf viii	2.0 GTI	Schrägheck	Frontantrieb	Benzin	180	245	Aug 2020	-	2024-03-01	141769
Opel	Astra k	1.5 Crdi	Kasten/Kombi	Frontantrieb	Diesel	77	105	Aug 2019	Sep 2021	2025-12-01	141772
Opel	Astra k	1	Kasten/Kombi	Frontantrieb	Benzin	77	105	May 2018	Aug 2019	2025-12-01	141773
Opel	Astra k	1.4	Kasten/Kombi	Frontantrieb	Benzin	110	150	Jun 2018	Sep 2021	2025-12-01	141774
Mercedes-benz	S-Klasse	S 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	270	367	Oct 2020	-	2024-03-01	141776
Mercedes-benz	S-Klasse	S 500 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	320	435	Sep 2020	-	2024-03-01	141777
Mercedes-benz	S-Klasse	S 350 D	Stufenheck	Heckantrieb	Diesel	210	286	Sep 2020	Jun 2023	2024-03-01	141778
Mercedes-benz	S-Klasse	S 350 D 4-matic	Stufenheck	Allrad	Diesel	210	286	Sep 2020	Jun 2023	2024-03-01	141779
Mercedes-benz	S-Klasse	S 400 D 4-matic	Stufenheck	Allrad	Diesel	243	330	Sep 2020	-	2024-03-01	141780
Mercedes-benz	Gle	GLE 350 E 4-matic	SUV	Allrad	Benzin/Elektro	245	333	Jun 2020	Mar 2023	2024-03-01	141792
BMW	3	M3	Stufenheck	Heckantrieb	Benzin	353	480	Nov 2020	-	2024-03-01	141793
BMW	3	M3 Competition	Stufenheck	Heckantrieb	Benzin	375	510	Nov 2020	-	2024-03-01	141794
BMW	4	M4	Coupe	Heckantrieb	Benzin	353	480	Nov 2020	-	2024-03-01	141795
BMW	4	M4 Competition	Coupe	Heckantrieb	Benzin	375	510	Nov 2020	-	2024-03-01	141796
Mercedes-benz	Gle	GLE 350 E 4-matic	SUV	Allrad	Benzin/Elektro	245	333	Jun 2020	Mar 2023	2024-03-01	141797
Opel	Corsa f	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Jul 2019	-	2024-03-01	141798
Opel	Corsa f	1.5	Kasten/Schrägheck	Frontantrieb	Diesel	75	102	Jul 2019	-	2024-03-01	141799
Opel	Crossland x van	1.2	Kasten/SUV	Frontantrieb	Benzin	61	83	Jul 2019	-	2024-03-01	141800
Opel	Crossland x van	1.5	Kasten/SUV	Frontantrieb	Diesel	75	102	Jun 2018	-	2024-03-01	141801
BMW	X4	Xdrive M40 I	SUV	Allrad	Benzin	285	387	Sep 2019	-	2024-03-01	141802
Opel	Crossland x van	1.2	Kasten/SUV	Frontantrieb	Benzin	81	110	Jul 2018	-	2025-04-01	141803
Opel	Grandland	1.5	Kasten/SUV	Frontantrieb	Diesel	96	131	Apr 2018	Jul 2021	2025-02-03	141804
Opel	Grandland	1.2	Kasten/SUV	Frontantrieb	Benzin	96	131	Apr 2018	Jul 2021	2025-02-03	141805
Opel	Grandland	2.0 Cdti	Kasten/SUV	Frontantrieb	Diesel	130	177	Nov 2017	Jul 2021	2025-02-03	141806
Toyota	Highlander	3.5 Vvti AWD	SUV	Allrad	Benzin	183	249	Dec 2019	-	2024-03-01	141807
Mazda	3	2.0 Skyactiv-g M Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	110	150	Jul 2020	-	2024-03-01	141808
Toyota	Highlander	2.5 Hybrid AWD	SUV	Allrad	Benzin/Elektro	181	246	Dec 2019	-	2024-03-01	141810
Mercedes-benz	C-Klasse	C 200 4-matic	Stufenheck	Allrad	Benzin	150	204	Aug 2019	May 2021	2024-03-01	141811
Rolls-royce	Ghost ii	V12	Stufenheck	Allrad	Benzin	420	571	Aug 2020	-	2024-03-01	141812
Rolls-royce	Ghost ii extended wheelbase	V12	Stufenheck	Allrad	Benzin	420	571	Aug 2020	-	2024-03-01	141813
Skoda	Kodiaq i	2.0 TDI 4X4	SUV	Allrad	Diesel	130	177	Apr 2017	-	2024-05-01	141826
Skoda	Karoq	1.4 TSI	SUV	Frontantrieb	Benzin	110	150	Jul 2017	-	2024-03-01	141828
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	105	143	Jun 2020	-	2024-03-01	141829
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	105	143	Jun 2020	-	2024-03-01	141830
Mercedes-benz	E-Klasse	E 450 EQ Boost	Kombi	Allrad	Benzin/Elektro	270	367	Aug 2020	Aug 2023	2024-03-01	141836
Seat	Ibiza v	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	141844
VW	Kaefer	1200 L 1.6	Stufenheck	Heckantrieb	Benzin	37	50	Aug 1975	Dec 1977	2024-03-01	141845
Mercedes-benz	E-Klasse	E 300 DE 4-matic	Kombi	Allrad	Diesel/Elektro	225	306	Aug 2020	Aug 2023	2024-03-01	141846
Dacia	Dokker	1.6 LPG	Kasten/Großraumlimousine	Frontantrieb	Benzin/Autogas (LPG)	80	109	Aug 2018	Dec 2021	2024-11-01	141848
VW	Golf viii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	110	150	Aug 2020	-	2024-03-01	141854
VW	Golf viii variant	1.5 TSI	Kombi	Frontantrieb	Benzin	96	131	Aug 2020	-	2024-03-01	141855
VW	Golf viii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Aug 2020	-	2024-03-01	141856
VW	Golf viii variant	1.0 TSI	Kombi	Frontantrieb	Benzin	66	90	Aug 2020	-	2024-03-01	141857
VW	Golf viii variant	2.0 TDI	Kombi	Frontantrieb	Diesel	85	116	Aug 2020	-	2024-03-01	141859
VW	Golf viii variant	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Aug 2020	-	2024-03-01	141860
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	147	200	Jul 2020	Apr 2024	2025-06-01	141863
KIA	Stonic	1.0 T-gdi Eco-dynamics+	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Jul 2020	Dec 2025	2026-07-01	141864
KIA	Rio iv	1.2 Cvvt	Schrägheck	Frontantrieb	Benzin	62	84	May 2020	-	2024-03-01	141865
Opel	Kapitän	2.8 S	Stufenheck	Heckantrieb	Benzin	107	145	Aug 1968	Dec 1971	2024-03-01	141866
Opel	Kapitän	2.8	Stufenheck	Heckantrieb	Benzin	97	132	Aug 1968	Dec 1971	2024-03-01	141867
Opel	Senator	2.3 Comprex D	Stufenheck	Heckantrieb	Diesel	70	95	Nov 1984	Aug 1987	2024-03-01	141868
Audi	A1	30 Tfsi	Schrägheck	Frontantrieb	Benzin	81	110	Sep 2020	-	2024-03-01	141869
Audi	E-Tron	S Quattro	SUV	Allrad	Elektro	370	503	Sep 2020	Jul 2023	2026-03-01	141871
Opel	Kadett c	1.0 S	Coupe	Heckantrieb	Benzin	35	48	Sep 1973	Aug 1975	2024-03-01	141873
Opel	Zafira	E Life	Bus	Frontantrieb	Elektro	100	136	Sep 2020	-	2024-03-01	141874
Audi	Q3	40 TDI Quattro	SUV	Allrad	Diesel	147	200	Sep 2020	-	2024-03-01	141876
Mercedes-benz	E-Klasse	E 300 E 4-matic	Stufenheck	Allrad	Benzin/Elektro	235	320	Jul 2020	Oct 2023	2024-03-01	141881
Mercedes-benz	E-Klasse	E 450 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	270	367	Jul 2020	Oct 2023	2024-03-01	141882
Mazda	Mx-30	E-skyactiv	SUV	Frontantrieb	Elektro	105	143	May 2020	-	2024-03-01	141883
Land Rover	Range rover iv	D300 Mhev 4X4	SUV	Allrad	Diesel/Elektro	221	300	Jul 2020	Sep 2021	2025-02-03	141900
Land Rover	Range rover iv	D350 Mhev 4X4	SUV	Allrad	Diesel/Elektro	258	351	Jul 2020	Sep 2021	2025-02-03	141901
Land Rover	Range rover sport ii	3.0 D300 Mhev 4X4	SUV	Allrad	Diesel/Elektro	221	300	Jul 2020	Mar 2022	2025-02-03	141902
Land Rover	Range rover sport ii	3.0 D350 Mhev 4X4	SUV	Allrad	Diesel/Elektro	258	351	Jul 2020	Mar 2022	2025-02-03	141903
Land Rover	Range rover evoque	2.0 D165 Mhev 4X4	SUV	Allrad	Diesel/Elektro	120	163	Jul 2020	-	2024-03-01	141905
Land Rover	Range rover evoque	2.0 D200 Mhev 4X4	SUV	Allrad	Diesel/Elektro	150	204	Jul 2020	-	2024-03-01	141906
Land Rover	Discovery sport	2.0 D165 Mhev 4X4	SUV	Allrad	Diesel/Elektro	120	163	Jul 2020	-	2024-03-01	141907
Land Rover	Discovery sport	2.0 D200 Mhev 4X4	SUV	Allrad	Diesel/Elektro	150	204	Jul 2020	-	2024-03-01	141908
Land Rover	Discovery sport	2.0 P290 Mhev 4X4	SUV	Allrad	Benzin/Elektro	213	290	Jul 2020	-	2024-03-01	141909
Land Rover	Defender station wagon	D250 Mhev 4X4	Geländewagen geschlossen	Allrad	Diesel/Elektro	183	249	Sep 2020	-	2024-03-01	141911
Land Rover	Defender station wagon	D300 Mhev 4X4	Geländewagen geschlossen	Allrad	Diesel/Elektro	221	300	Sep 2020	-	2024-03-01	141912
Land Rover	Defender van	3.0 D250 Mhev 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel/Elektro	183	249	Sep 2020	-	2024-03-01	141914
Land Rover	Defender van	3.0 D300 Mhev 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel/Elektro	221	300	Sep 2020	-	2024-03-01	141915
Land Rover	Defender station wagon	P400e Hybrid 4X4	Geländewagen geschlossen	Allrad	Benzin/Elektro	297	404	Sep 2020	-	2024-03-01	141917
Karma	Revero	2.0 Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	301	409	Sep 2017	-	2025-02-03	141920
Goupil	G4l	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	10	14	Jan 2018	-	2024-03-01	141921
Goupil	G6	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	33	45	Jul 2020	-	2024-03-01	141922
BMW	1	128 TI	Schrägheck	Frontantrieb	Benzin	195	265	Nov 2020	-	2024-03-01	141923


--- Round 1 / 首次发送 ---
## 更新点

* 按缓存优先模式完成首轮聚类：新增 `READY` 映射 63 行，覆盖 60 个输入 Ktype；其中 Dacia Dokker 拆分为 Van/MPV 两种外廓，Opel Zafira Life 拆分为 S/M/L 三种长度。
* 直接复用跨批次已确认尺寸组 41 个，本轮未重复输出其尺寸和来源。
* 首次闭合 5 个尺寸组：Toyota Yaris Cross、Golf VIII GTI、BMW G80 M3、BMW G82 M4、Golf VIII Variant。Toyota、BMW 和 Volkswagen 官方资料分别确认了对应三维；Golf Variant 高度采用包含原厂车顶行李架的最大外部高度 1498 mm。([Toyota Media Site][1])

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：60
* READY 映射：63
* PENDING 输入 Ktype：40
* 当前已引用尺寸组：46
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141630	141630	Hatchback	Audi A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门 Sportback 改款外廓。	READY
141660	141660	SUV	Toyota Yaris Cross I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-XP210-SUV-FWD-01	HIGH	前驱五门 SUV 外廓。	READY
141710	141710	Wagon	Volkswagen Arteon I facelift	3H9	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	Shooting Brake 旅行车外廓。	READY
141712	141712	Hatchback	Porsche Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH	标准轴距五门掀背外廓。	READY
141721	141721	SUV	Porsche Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	HIGH	GTS 专属外廓。	READY
141723	141723	Coupe	Porsche 911 992	992	2	EU-PORSCHE-911-992-TURBO-S-COUPE-01	HIGH	Turbo 与已缓存 Turbo S 共用宽体双门硬顶外廓。	READY
141724	141724	Convertible	Porsche 911 992	992	2	EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	HIGH	Turbo 与已缓存 Turbo S 共用宽体敞篷外廓。	READY
141729	141729	Hatchback	Porsche Panamera II facelift	971	5	EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	HIGH	GTS 改款五门掀背外廓。	READY
141730	141730	Hatchback	Porsche Panamera II facelift	971	5	EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	HIGH	Turbo S 与缓存 Turbo 宽体五门外廓一致。	READY
141738	141738	Van	StreetScooter Work			EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH	标准 Work 箱式车外廓。	READY
141756	141756	Sedan	Volvo S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	四门轿车外廓。	READY
141769	141769	Hatchback	Volkswagen Golf VIII	CD	5	EU-VW-GOLF-VIII-GTI-HATCHBACK-01	HIGH	GTI 专属前后保险杠外廓。	READY
141772	141772	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141773	141773	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141774	141774	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141793	141793	Sedan	BMW M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-RWD-01	HIGH	后驱四门 M3 外廓。	READY
141794	141794	Sedan	BMW M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-RWD-01	HIGH	后驱四门 M3 外廓。	READY
141795	141795	Coupe	BMW M4 G82	G82	2	EU-BMW-4-G82-M4-COUPE-RWD-01	HIGH	后驱双门 M4 外廓。	READY
141796	141796	Coupe	BMW M4 G82	G82	2	EU-BMW-4-G82-M4-COUPE-RWD-01	HIGH	后驱双门 M4 外廓。	READY
141798	141798	Van	Opel Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH	五门掀背车身的商用厢式版本，外廓复用。	READY
141799	141799	Van	Opel Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH	五门掀背车身的商用厢式版本，外廓复用。	READY
141802	141802	SUV	BMW X4 II	G02	5	EU-BMW-X4-G02-M40I-SUV-01	HIGH	M40i 专属外廓。	READY
141804	141804	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141805	141805	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141806	141806	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141808	141808	Sedan	Mazda3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	四门轿车外廓。	READY
141811	141811	Sedan	Mercedes-Benz C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
141826	141826	SUV	Skoda Kodiaq I pre-facelift	NS7	5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH	普通版改款前 SUV 外廓。	READY
141828	141828	SUV	Skoda Karoq I pre-facelift	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	HIGH	改款前 SUV 外廓。	READY
141829	141829	Wagon	Skoda Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH	五门旅行车外廓。	READY
141830	141830	Hatchback	Skoda Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141836	141836	Wagon	Mercedes-Benz E-Class W213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	HIGH	E 450 4MATIC 改款旅行车外廓。	READY
141844	141844	Hatchback	SEAT Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141846	141846	Wagon	Mercedes-Benz E-Class W213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	HIGH	E 300 de 4MATIC 与缓存插混旅行车外廓一致。	READY
141848_van	141848	Van	Dacia Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	同一 Ktype 覆盖货运厢式车分支。	READY
141848_mpv	141848	MPV	Dacia Dokker I			EU-DACIA-DOKKER-I-MPV-01	HIGH	同一 Ktype 覆盖乘用 MPV 分支。	READY
141854	141854	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141855	141855	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141856	141856	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141857	141857	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141859	141859	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141860	141860	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141863	141863	SUV	Volkswagen Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH	四驱 SUV 外廓。	READY
141864	141864	Hatchback	Kia Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	五门跨界车外廓。	READY
141865	141865	Hatchback	Kia Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141869	141869	Hatchback	Audi A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141874_s	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	同一 Ktype 覆盖 S 短轴乘用分支。	READY
141874_m	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	同一 Ktype 覆盖 M 中轴乘用分支。	READY
141874_l	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	同一 Ktype 覆盖 L 长轴乘用分支。	READY
141876	141876	SUV	Audi Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	普通 Q3 SUV 外廓。	READY
141881	141881	Sedan	Mercedes-Benz E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	HIGH	E 300 e 4MATIC 与缓存四驱插混轿车外廓一致。	READY
141882	141882	Sedan	Mercedes-Benz E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
141883	141883	SUV	Mazda MX-30 I	DR	5	EU-MAZDA-MX-30-I-SUV-01	HIGH	五门 SUV 外廓。	READY
141900	141900	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	标准车顶改款 SUV 外廓。	READY
141901	141901	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	标准车顶改款 SUV 外廓。	READY
141902	141902	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款 SUV 外廓。	READY
141903	141903	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款 SUV 外廓。	READY
141905	141905	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	五门 SUV 外廓。	READY
141906	141906	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	五门 SUV 外廓。	READY
141907	141907	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141908	141908	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141909	141909	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141923	141923	Hatchback	BMW 1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	五门掀背外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-YARIS-CROSS-I-XP210-SUV-FWD-01	4180	1765	1595	Toyota UK Media Yaris Cross launch press release	https://media.toyota.co.uk/all-new-yaris-cross-extends-toyotas-market-leading-hybrid-electric-suv-line-up/
EU-VW-GOLF-VIII-GTI-HATCHBACK-01	4287	1789	1478	Volkswagen South Africa Golf GTI and R Specifications	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/brochures/pv/2023-pv-mobile-brochure/golf_specsheet.pdf
EU-BMW-3-G80-M3-SEDAN-RWD-01	4794	1903	1433	BMW Group Media Information BMW M3 Sedan Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0316649EN/476823
EU-BMW-4-G82-M4-COUPE-RWD-01	4794	1887	1393	BMW Group Media Information BMW M4 Coupe Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0316649EN/476824
EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	4633	1789	1498	Volkswagen Newsroom Golf Variant design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-variant-and-golf-alltrack-international-media-drive-6540/design-and-dimensions-6543
```

## 下一步优先处理

1. 集中闭合 Mercedes-Benz W223 S-Class 的 SWB/LWB 分支，以及 Land Rover Defender 90/110、Station Wagon/Van 分支。
2. 处理 Citroën SpaceTourer、Nissan NV400 Bus 和 Isuzu D-Max III 的多轴距、多车身外廓。
3. 再处理 Hyundai Terracan、VW Derby/Käfer、Opel Kapitän/Senator/Kadett C 等历史车型，以及 Ligier、Goupil、Karma、StreetScooter Work XL 等低频车型。

推进信号：CONTINUE

[1]: https://media.toyota.co.uk/all-new-yaris-cross-extends-toyotas-market-leading-hybrid-electric-suv-line-up/?utm_source=chatgpt.com "All-new Yaris Cross Extends Toyota's Market-leading Hybrid ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5401-5500_ktype_dimension_mapping_final.tsv
- all_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 `READY` 映射 30 行，覆盖 19 个 Ktype。Citroën SpaceTourer 与 Fiat 500X 直接关联已有尺寸组，未重复输出其三维和来源。
* 首次闭合 BMW 545e、Mercedes-Benz GLE 350e、Opel Crossland X、Toyota Highlander、Rolls-Royce Ghost、Audi e-tron S 共 7 类、7 个尺寸组。
* Land Rover Defender 按实际物理外廓拆分为 90/110，以及钢簧/空气悬架共 4 个尺寸组；D250、D300 Station Wagon 覆盖 90 与 110，Hard Top 商用版限定 110，P400e 限定 110 空气悬架。

## 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：79
* READY 映射：93
* PENDING 输入 Ktype：21
* 当前已引用尺寸组：57
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141676_m	141676	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中轴乘用分支。	READY
141676_xl	141676	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长轴乘用分支。	READY
141677_m	141677	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中轴纯电乘用分支。	READY
141677_xl	141677	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长轴纯电乘用分支。	READY
141711_urban	141711	SUV	Fiat 500X I facelift	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	Urban前驱外廓。	READY
141711_cross	141711	SUV	Fiat 500X I facelift	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	Cross前驱外廓。	READY
141737	141737	Sedan	BMW 5 Series G30 facelift	G30	4	EU-BMW-5-G30-545E-XDRIVE-SEDAN-FACELIFT-01	HIGH	545e xDrive四门插混轿车外廓。	READY
141792	141792	SUV	Mercedes-Benz GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	HIGH	GLE 350 e插混SUV外廓。	READY
141797	141797	SUV	Mercedes-Benz GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	HIGH	GLE 350 e插混SUV外廓。	READY
141800	141800	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141801	141801	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141803	141803	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141807	141807	SUV	Toyota Highlander IV	XU70	5	EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	HIGH	五门SUV外廓。	READY
141810	141810	SUV	Toyota Highlander IV	XU70	5	EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	HIGH	五门SUV外廓。	READY
141812	141812	Sedan	Rolls-Royce Ghost II		4	EU-ROLLS-ROYCE-GHOST-II-SEDAN-SWB-01	HIGH	标准轴距四门轿车外廓。	READY
141813	141813	Sedan	Rolls-Royce Ghost II		4	EU-ROLLS-ROYCE-GHOST-II-SEDAN-LWB-01	HIGH	Extended长轴四门轿车外廓。	READY
141871	141871	SUV	Audi e-tron S I	GE	5	EU-AUDI-E-TRON-S-I-GE-SUV-01	HIGH	S车型宽体五门SUV外廓。	READY
141911_90_coil	141911	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	HIGH	D250三门90钢簧分支。	READY
141911_90_air	141911	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	HIGH	D250三门90空气悬架分支。	READY
141911_110_coil	141911	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D250五门110钢簧分支。	READY
141911_110_air	141911	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D250五门110空气悬架分支。	READY
141912_90_coil	141912	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	HIGH	D300三门90钢簧分支。	READY
141912_90_air	141912	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	HIGH	D300三门90空气悬架分支。	READY
141912_110_coil	141912	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D300五门110钢簧分支。	READY
141912_110_air	141912	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D300五门110空气悬架分支。	READY
141914_110_coil	141914	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D250 110 Hard Top钢簧分支。	READY
141914_110_air	141914	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D250 110 Hard Top空气悬架分支。	READY
141915_110_coil	141915	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D300 110 Hard Top钢簧分支。	READY
141915_110_air	141915	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D300 110 Hard Top空气悬架分支。	READY
141917	141917	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	P400e仅对应五门110空气悬架分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-545E-XDRIVE-SEDAN-FACELIFT-01	4936	1868	1483	BMW Group Media Information BMW 545e xDrive Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0317777EN/461549
EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	4924	1947	1795	Auto-Data Mercedes-Benz GLE SUV V167 GLE 350e	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350e-333hp-plug-in-hybrid-4matic-9g-tronic-46008
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1605	Vauxhall Crossland X Price and Specification Guide MY2020.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/crossland/price-guides/Crossland_X_Spec_ePG_2_September_2020_Library-1602148545.pdf
EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	4966	1930	1755	Toyota Highlander UK brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-downloads/highlander.pdf
EU-ROLLS-ROYCE-GHOST-II-SEDAN-SWB-01	5546	1978	1571	Carsales Rolls-Royce Ghost 2021 specifications	https://www.carsales.com.au/research/rolls-royce/ghost/2021/
EU-ROLLS-ROYCE-GHOST-II-SEDAN-LWB-01	5716	1978	1571	Carsales Rolls-Royce Ghost 2021 specifications	https://www.carsales.com.au/research/rolls-royce/ghost/2021/
EU-AUDI-E-TRON-S-I-GE-SUV-01	4902	1976	1629	Automobile-Catalog 2021 Audi e-tron S specifications	https://www.automobile-catalog.com/car/2021/3006470/audi_e-tron_s.html
EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	4583	1996	1974	Land Rover Media 22MY Defender 90 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_90_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	4583	1996	1969	Land Rover Media 22MY Defender 90 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_90_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	5018	1996	1972	Land Rover Media 22MY Defender 110 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_110_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	5018	1996	1967	Land Rover Media 22MY Defender 110 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_110_TECH_DATA_22MY_250221.pdf
```

## 下一步优先处理

1. 闭合 Mercedes-Benz W223 S-Class 的标准轴距、长轴距及动力版本边界。
2. 处理 Nissan NV400 Bus、Isuzu D-Max III 和 StreetScooter Work XL 的轴距、驾驶室或车身分支。
3. 集中处理 VW Derby/Käfer、Hyundai Terracan、Opel Kapitän/Senator/Kadett C 等历史车型。
4. 最后处理 Ligier Pulse 3、Karma Revero、Goupil G4L/G6 等低频车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5401-5500_ktype_dimension_mapping_final.tsv
- all_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 本轮新增 `READY` 映射 19 行，完成 13 个输入 Ktype。
* Mercedes-Benz S-Class 5 个 Ktype 均按标准轴距 `W223`、长轴距 `V223` 拆分；两种车身宽度和高度一致，长度分别为 5179 mm、5289 mm。([mercedes-benz-mena.com][1])
* Volkswagen Derby 按官方资料确认的 1979 年车长变化拆成两个物理分支；Käfer 1200 L 1.6 采用 Volkswagen Classic 的 Type 11 1600 外廓。([Volkswagen Newsroom][2])
* 同时闭合 Hyundai Terracan、Opel Senator A2 Comprex、Opel Kadett C Coupé 和 Karma Revero 尺寸组。([汽车数据网][3])

## 2. 当前批次进度

* 输入 Ktype：100
* 已完成输入 Ktype：92
* READY 映射：112
* PENDING 输入 Ktype：8
* 当前已引用尺寸组：66
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141631_pre79	141631	Sedan	Volkswagen Derby I		2	EU-VW-DERBY-I-SEDAN-PRE1979-01	HIGH	1977至1978年短车身分支。	READY
141631_from79	141631	Sedan	Volkswagen Derby I		2	EU-VW-DERBY-I-SEDAN-FROM1979-01	HIGH	1979年起加长车身分支。	READY
141653	141653	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141655	141655	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141657	141657	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141776_swb	141776	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141776_lwb	141776	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141777_swb	141777	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141777_lwb	141777	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141778_swb	141778	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141778_lwb	141778	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141779_swb	141779	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141779_lwb	141779	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141780_swb	141780	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141780_lwb	141780	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141845	141845	Sedan	Volkswagen Beetle Type 1	Type 11	2	EU-VW-KAEFER-TYPE11-SEDAN-1600-01	HIGH	Type 11双门1600外廓。	READY
141868	141868	Sedan	Opel Senator A2		4	EU-OPEL-SENATOR-A2-SEDAN-COMPREX-01	HIGH	Comprex柴油四门轿车外廓。	READY
141873	141873	Coupe	Opel Kadett C		2	EU-OPEL-KADETT-C-COUPE-01	HIGH	双门Coupe外廓。	READY
141920	141920	Sedan	Karma Revero I		4	EU-KARMA-REVERO-I-SEDAN-01	HIGH	四门插电式混合动力轿车外廓。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-DERBY-I-SEDAN-PRE1979-01	3836	1560	1352	Volkswagen Classic Derby vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-I-SEDAN-FROM1979-01	3915	1560	1352	Volkswagen Classic Derby vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-HYUNDAI-TERRACAN-I-SUV-01	4710	1860	1795	Auto-Data Hyundai Terracan generation specifications	https://www.auto-data.net/en/hyundai-terracan-generation-3002
EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	5179	1954	1503	Mercedes-Benz S-Class Saloon W223 Owner's Manual vehicle dimensions	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/s-class-saloon-2024-03-w223-mbux/vehicle-data/vehicle-dimensions
EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	5289	1954	1503	Mercedes-Benz S-Class Saloon Long V223 Owner's Manual vehicle dimensions	https://www.mercedes-benz.com.sg/passengercars/services/manuals.html/s-class-saloon-long-2024-09-v223-mbux/vehicle-data/vehicle-dimensions
EU-VW-KAEFER-TYPE11-SEDAN-1600-01	4060	1550	1500	Volkswagen Classic Beetle 1200/1200L profile; Volkswagen Classic Beetle 1600/1600i profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-12001200l-profile-19585;https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-16001600i-profile-19604
EU-OPEL-SENATOR-A2-SEDAN-COMPREX-01	4839	1722	1415	Auto-Data Opel Senator A2 2.3 Comprex D specifications	https://www.auto-data.net/en/opel-senator-a-facelift-1982-2.3-comprex-d-95hp-26931
EU-OPEL-KADETT-C-COUPE-01	4127	1580	1340	Automoli Opel Kadett C Coupe vehicle specifications	https://www.automoli.com/en/vehicles/opel/kadett/kadett-c-coupe-512/
EU-KARMA-REVERO-I-SEDAN-01	4999	1984	1331	J.D. Power 2018 Karma Revero specifications	https://www.jdpower.com/cars/2018/karma/revero/4-door-sedan/specs
```

## 5. 下一步优先处理

1. 闭合 Nissan NV400 Bus 的轴距和车顶组合。
2. 确认 Isuzu D-Max III 后驱版本对应的驾驶室分支。
3. 处理 Opel Kapitän 跨 KAD A/B 的物理外廓边界。
4. 最后处理 Ligier Pulse 3、StreetScooter Work XL、Goupil G4L 和 G6。

推进信号：CONTINUE

[1]: https://www.mercedes-benz-mena.com/iraq/en/services/manuals/s-class-saloon-2024-03-w223-mbux/vehicle-data/vehicle-dimensions?utm_source=chatgpt.com "S-Class Saloon March 2024 W223 MBUX | Owner's Manual"
[2]: https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687?utm_source=chatgpt.com "Vehicle data Derby profile"
[3]: https://www.auto-data.net/en/hyundai-terracan-generation-3002 "Hyundai Terracan | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5401-5500_ktype_dimension_mapping_final.tsv
- all_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 6 个输入 Ktype：Nissan NV400 Bus、Ligier Pulse 3、StreetScooter Work XL、两款 Opel Kapitän B 和 Goupil G6。
* Nissan NV400 Combi 确认为 `L1H1`、`L2H2` 两种前驱外廓，直接复用现有 NV400 尺寸组；未重复输出尺寸组。([日产][1])
* 首次创建 Ligier Pulse 3、StreetScooter Work XL、Opel Kapitän B、Goupil G6 共 4 个尺寸组。
* Isuzu D-Max 的 110 kW 后驱单排资料存在低底盘和高底盘两套外廓；Goupil G4 L 的输入同时包含平台与底盘语义，暂不创建猜测性派生行或尺寸组。([Nsb Motors][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：98
* PENDING 输入 Ktype：2
* READY 映射：119
* PENDING 映射：2
* 已确认尺寸组：70
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141684_l1h1	141684	MPV	Nissan NV400 I facelift			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1前驱Combi乘用分支。	READY
141684_l2h2	141684	MPV	Nissan NV400 I facelift			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2前驱Combi乘用分支。	READY
141702	141702	Pickup	Ligier Pulse 3			EU-LIGIER-PULSE-3-THREEWHEELER-PICKUP-01	HIGH	三轮开放式电动载货外廓。	READY
141739	141739	Van	StreetScooter Work XL			EU-STREETSCOOTER-WORK-XL-BOX-VAN-01	HIGH	DHL专用箱式配送车外廓。	READY
141767	141767	Pickup	Isuzu D-Max III	RG	2		LOW	后驱单排车型；110 kW资料同时存在低底盘与高底盘外廓。	PENDING: 当前Ktype对应低底盘或高底盘分支未确认
141866	141866	Sedan	Opel Kapitän B		4	EU-OPEL-KAPITAEN-B-SEDAN-01	HIGH	2.8 S四门轿车外廓。	READY
141867	141867	Sedan	Opel Kapitän B		4	EU-OPEL-KAPITAEN-B-SEDAN-01	HIGH	2.8四门轿车外廓。	READY
141921	141921	Chassis	Goupil G4 L		2		LOW	Pritsche/Fahrgestell可能覆盖裸底盘与成品平台两种总长。	PENDING: 裸底盘与成品平台物理分支尚未闭合
141922	141922	Chassis	Goupil G6		2	EU-GOUPIL-G6-PURE-CHASSIS-01	HIGH	三座驾驶室纯底盘外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LIGIER-PULSE-3-THREEWHEELER-PICKUP-01	2280	800	1149	Ligier Professional Pulse 3 technical characteristics	https://www.ligier.at/wp-content/uploads/sites/19/2023/08/2023.06.22-FICHE-EQUIPEMENT-PULSE-3-EN.pdf
EU-STREETSCOOTER-WORK-XL-BOX-VAN-01	7000	2140	2850	Deutsche Post DHL Group StreetScooter WORK XL Facts & Figures	https://group.dhl.com/content/dam/deutschepostdhl/en/media-center/media-relations/documents/2019/fact-sheet-streetscooter-work-xl-en.pdf
EU-OPEL-KAPITAEN-B-SEDAN-01	4907	1852	1450	Automobile-Catalog 1969 Opel Kapitan 2800 S; Automobile-Catalog 1970 Opel Kapitan 2800	https://www.automobile-catalog.com/car/1969/2417075/opel_kapitan_2800_s.html;https://www.automobile-catalog.com/car/1970/2417045/opel_kapitan_2800.html
EU-GOUPIL-G6-PURE-CHASSIS-01	4796	1704	1921	Goupil G6 official brochure	https://hafog.dk/wp-content/uploads/files/393362_Goupil%20Brochure%20G6%20eng.pdf
```

## 下一步优先处理

1. 确认 Ktype `141767` 是否只对应后驱低底盘单排，或同时覆盖高底盘单排；若同时覆盖则创建两个派生映射。
2. 确认 Ktype `141921` 对应 Goupil G4 L 裸底盘还是带平台/货斗成品外廓，并闭合最终总长。

推进信号：CONTINUE

[1]: https://www-europe.nissan-cdn.net/content/dam/Nissan/ireland/Brochures/NV400%20MY20%20112020.pdf?utm_source=chatgpt.com "nissan - nv400"
[2]: https://nsbmotors.co.za/ISUZU/ISUZU_D-MAX_RG_SINGLE-CAB_BAKKIE_SPECIFICATIONS_150722.pdf "D-MAX_RG_SINGLE-CAB_SPEC-BOOKLET_A4_11Jul2022.indd"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5401-5500_ktype_dimension_mapping_final.tsv
- all_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 最后两个 `PENDING` 已闭合：Ktype `141767` 拆分为 D-Max III 后驱单排 Standard 与 L 两种外廓；Ktype `141921` 关联 Goupil G4 L 长轴底盘/平台外廓。([Nsb Motors][1])
* 已完成固定表头、主键唯一性、100 个输入 Ktype 覆盖、映射引用闭合、尺寸及来源非空检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：122
* PENDING 映射：0
* DIMENSION_GROUP：79
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 长宽高及来源完整：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
141630	141630	Hatchback	Audi A5 F5 facelift	F5A	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	五门 Sportback 改款外廓。	READY
141631_pre79	141631	Sedan	Volkswagen Derby I		2	EU-VW-DERBY-I-SEDAN-PRE1979-01	HIGH	1977至1978年短车身分支。	READY
141631_from79	141631	Sedan	Volkswagen Derby I		2	EU-VW-DERBY-I-SEDAN-FROM1979-01	HIGH	1979年起加长车身分支。	READY
141653	141653	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141655	141655	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141657	141657	SUV	Hyundai Terracan I		5	EU-HYUNDAI-TERRACAN-I-SUV-01	HIGH	五门SUV外廓。	READY
141660	141660	SUV	Toyota Yaris Cross I	XP210	5	EU-TOYOTA-YARIS-CROSS-I-XP210-SUV-FWD-01	HIGH	前驱五门 SUV 外廓。	READY
141676_m	141676	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中轴乘用分支。	READY
141676_xl	141676	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长轴乘用分支。	READY
141677_m	141677	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	HIGH	M中轴纯电乘用分支。	READY
141677_xl	141677	MPV	Citroën SpaceTourer I pre-facelift	K0	5	EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	HIGH	XL长轴纯电乘用分支。	READY
141684_l1h1	141684	MPV	Nissan NV400 I facelift			EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	HIGH	L1H1前驱Combi乘用分支。	READY
141684_l2h2	141684	MPV	Nissan NV400 I facelift			EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	HIGH	L2H2前驱Combi乘用分支。	READY
141702	141702	Pickup	Ligier Pulse 3			EU-LIGIER-PULSE-3-THREEWHEELER-PICKUP-01	HIGH	三轮开放式电动载货外廓。	READY
141710	141710	Wagon	Volkswagen Arteon I facelift	3H9	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	HIGH	Shooting Brake 旅行车外廓。	READY
141711_urban	141711	SUV	Fiat 500X I facelift	334	5	EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	HIGH	Urban前驱外廓。	READY
141711_cross	141711	SUV	Fiat 500X I facelift	334	5	EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	HIGH	Cross前驱外廓。	READY
141712	141712	Hatchback	Porsche Panamera II	971	5	EU-PORSCHE-PANAMERA-971-HATCHBACK-01	HIGH	标准轴距五门掀背外廓。	READY
141721	141721	SUV	Porsche Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	HIGH	GTS 专属外廓。	READY
141723	141723	Coupe	Porsche 911 992	992	2	EU-PORSCHE-911-992-TURBO-S-COUPE-01	HIGH	Turbo 与已缓存 Turbo S 共用宽体双门硬顶外廓。	READY
141724	141724	Convertible	Porsche 911 992	992	2	EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	HIGH	Turbo 与已缓存 Turbo S 共用宽体敞篷外廓。	READY
141729	141729	Hatchback	Porsche Panamera II facelift	971	5	EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	HIGH	GTS 改款五门掀背外廓。	READY
141730	141730	Hatchback	Porsche Panamera II facelift	971	5	EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	HIGH	Turbo S 与缓存 Turbo 宽体五门外廓一致。	READY
141737	141737	Sedan	BMW 5 Series G30 facelift	G30	4	EU-BMW-5-G30-545E-XDRIVE-SEDAN-FACELIFT-01	HIGH	545e xDrive四门插混轿车外廓。	READY
141738	141738	Van	StreetScooter Work			EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH	标准 Work 箱式车外廓。	READY
141739	141739	Van	StreetScooter Work XL			EU-STREETSCOOTER-WORK-XL-BOX-VAN-01	HIGH	DHL专用箱式配送车外廓。	READY
141756	141756	Sedan	Volvo S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH	四门轿车外廓。	READY
141767_standard	141767	Pickup	Isuzu D-Max III	RG	2	EU-ISUZU-D-MAX-III-RG-SINGLE-CAB-STANDARD-01	HIGH	Standard后驱单排外廓。	READY
141767_l	141767	Pickup	Isuzu D-Max III	RG	2	EU-ISUZU-D-MAX-III-RG-SINGLE-CAB-L-01	HIGH	L后驱单排外廓。	READY
141769	141769	Hatchback	Volkswagen Golf VIII	CD	5	EU-VW-GOLF-VIII-GTI-HATCHBACK-01	HIGH	GTI 专属前后保险杠外廓。	READY
141772	141772	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141773	141773	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141774	141774	Van	Opel Astra K	B16	5	EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	HIGH	Sports Tourer 车身的商用厢式版本，外廓复用。	READY
141776_swb	141776	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141776_lwb	141776	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141777_swb	141777	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141777_lwb	141777	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141778_swb	141778	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141778_lwb	141778	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141779_swb	141779	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141779_lwb	141779	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141780_swb	141780	Sedan	Mercedes-Benz S-Class W223	W223	4	EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	HIGH	标准轴距W223分支。	READY
141780_lwb	141780	Sedan	Mercedes-Benz S-Class W223	V223	4	EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	HIGH	长轴距V223分支。	READY
141792	141792	SUV	Mercedes-Benz GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	HIGH	GLE 350 e插混SUV外廓。	READY
141793	141793	Sedan	BMW M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-RWD-01	HIGH	后驱四门 M3 外廓。	READY
141794	141794	Sedan	BMW M3 G80	G80	4	EU-BMW-3-G80-M3-SEDAN-RWD-01	HIGH	后驱四门 M3 外廓。	READY
141795	141795	Coupe	BMW M4 G82	G82	2	EU-BMW-4-G82-M4-COUPE-RWD-01	HIGH	后驱双门 M4 外廓。	READY
141796	141796	Coupe	BMW M4 G82	G82	2	EU-BMW-4-G82-M4-COUPE-RWD-01	HIGH	后驱双门 M4 外廓。	READY
141797	141797	SUV	Mercedes-Benz GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	HIGH	GLE 350 e插混SUV外廓。	READY
141798	141798	Van	Opel Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH	五门掀背车身的商用厢式版本，外廓复用。	READY
141799	141799	Van	Opel Corsa F	P2JO	5	EU-OPEL-CORSA-F-HATCHBACK-01	HIGH	五门掀背车身的商用厢式版本，外廓复用。	READY
141800	141800	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141801	141801	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141802	141802	SUV	BMW X4 II	G02	5	EU-BMW-X4-G02-M40I-SUV-01	HIGH	M40i 专属外廓。	READY
141803	141803	Van	Opel Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X SUV车身的商用厢式版本。	READY
141804	141804	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141805	141805	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141806	141806	Van	Opel Grandland X	A18	5	EU-OPEL-GRANDLAND-X-A18-SUV-01	HIGH	Grandland X SUV 车身的商用厢式版本，外廓复用。	READY
141807	141807	SUV	Toyota Highlander IV	XU70	5	EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	HIGH	五门SUV外廓。	READY
141808	141808	Sedan	Mazda3 IV	BP	4	EU-MAZDA-3-IV-BP-SEDAN-01	HIGH	四门轿车外廓。	READY
141810	141810	SUV	Toyota Highlander IV	XU70	5	EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	HIGH	五门SUV外廓。	READY
141811	141811	Sedan	Mercedes-Benz C-Class W205 facelift	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
141812	141812	Sedan	Rolls-Royce Ghost II		4	EU-ROLLS-ROYCE-GHOST-II-SEDAN-SWB-01	HIGH	标准轴距四门轿车外廓。	READY
141813	141813	Sedan	Rolls-Royce Ghost II		4	EU-ROLLS-ROYCE-GHOST-II-SEDAN-LWB-01	HIGH	Extended长轴四门轿车外廓。	READY
141826	141826	SUV	Skoda Kodiaq I pre-facelift	NS7	5	EU-SKODA-KODIAQ-I-SUV-PREFL-01	HIGH	普通版改款前 SUV 外廓。	READY
141828	141828	SUV	Skoda Karoq I pre-facelift	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	HIGH	改款前 SUV 外廓。	READY
141829	141829	Wagon	Skoda Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH	五门旅行车外廓。	READY
141830	141830	Hatchback	Skoda Octavia IV	NX	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141836	141836	Wagon	Mercedes-Benz E-Class W213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	HIGH	E 450 4MATIC 改款旅行车外廓。	READY
141844	141844	Hatchback	SEAT Ibiza V	KJ1	5	EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141845	141845	Sedan	Volkswagen Beetle Type 1	Type 11	2	EU-VW-KAEFER-TYPE11-SEDAN-1600-01	HIGH	Type 11双门1600外廓。	READY
141846	141846	Wagon	Mercedes-Benz E-Class W213 facelift	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	HIGH	E 300 de 4MATIC 与缓存插混旅行车外廓一致。	READY
141848_van	141848	Van	Dacia Dokker I	F67		EU-DACIA-DOKKER-I-F67-VAN-01	HIGH	同一 Ktype 覆盖货运厢式车分支。	READY
141848_mpv	141848	MPV	Dacia Dokker I			EU-DACIA-DOKKER-I-MPV-01	HIGH	同一 Ktype 覆盖乘用 MPV 分支。	READY
141854	141854	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141855	141855	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141856	141856	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141857	141857	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141859	141859	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141860	141860	Wagon	Volkswagen Golf VIII Variant	CD	5	EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	HIGH	标准前驱五门旅行车外廓。	READY
141863	141863	SUV	Volkswagen Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-SUV-AWD-01	HIGH	四驱 SUV 外廓。	READY
141864	141864	Hatchback	Kia Stonic I	YB	5	EU-KIA-STONIC-I-YB-SUV-01	HIGH	五门跨界车外廓。	READY
141865	141865	Hatchback	Kia Rio IV	YB	5	EU-KIA-RIO-IV-YB-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141866	141866	Sedan	Opel Kapitän B		4	EU-OPEL-KAPITAEN-B-SEDAN-01	HIGH	2.8 S四门轿车外廓。	READY
141867	141867	Sedan	Opel Kapitän B		4	EU-OPEL-KAPITAEN-B-SEDAN-01	HIGH	2.8四门轿车外廓。	READY
141868	141868	Sedan	Opel Senator A2		4	EU-OPEL-SENATOR-A2-SEDAN-COMPREX-01	HIGH	Comprex柴油四门轿车外廓。	READY
141869	141869	Hatchback	Audi A1 GB	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	五门掀背外廓。	READY
141871	141871	SUV	Audi e-tron S I	GE	5	EU-AUDI-E-TRON-S-I-GE-SUV-01	HIGH	S车型宽体五门SUV外廓。	READY
141873	141873	Coupe	Opel Kadett C		2	EU-OPEL-KADETT-C-COUPE-01	HIGH	双门Coupe外廓。	READY
141874_s	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	HIGH	同一 Ktype 覆盖 S 短轴乘用分支。	READY
141874_m	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	HIGH	同一 Ktype 覆盖 M 中轴乘用分支。	READY
141874_l	141874	MPV	Opel Zafira Life I		5	EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	HIGH	同一 Ktype 覆盖 L 长轴乘用分支。	READY
141876	141876	SUV	Audi Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	普通 Q3 SUV 外廓。	READY
141881	141881	Sedan	Mercedes-Benz E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	HIGH	E 300 e 4MATIC 与缓存四驱插混轿车外廓一致。	READY
141882	141882	Sedan	Mercedes-Benz E-Class W213 facelift	W213	4	EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	HIGH	改款四门轿车外廓。	READY
141883	141883	SUV	Mazda MX-30 I	DR	5	EU-MAZDA-MX-30-I-SUV-01	HIGH	五门 SUV 外廓。	READY
141900	141900	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	标准车顶改款 SUV 外廓。	READY
141901	141901	SUV	Range Rover IV facelift	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	HIGH	标准车顶改款 SUV 外廓。	READY
141902	141902	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款 SUV 外廓。	READY
141903	141903	SUV	Range Rover Sport II facelift	L494	5	EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	HIGH	改款 SUV 外廓。	READY
141905	141905	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	五门 SUV 外廓。	READY
141906	141906	SUV	Range Rover Evoque II	L551	5	EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	HIGH	五门 SUV 外廓。	READY
141907	141907	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141908	141908	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141909	141909	SUV	Discovery Sport I facelift	L550	5	EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	HIGH	不含后视镜宽度口径的改款 SUV 外廓。	READY
141911_90_coil	141911	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	HIGH	D250三门90钢簧分支。	READY
141911_90_air	141911	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	HIGH	D250三门90空气悬架分支。	READY
141911_110_coil	141911	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D250五门110钢簧分支。	READY
141911_110_air	141911	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D250五门110空气悬架分支。	READY
141912_90_coil	141912	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	HIGH	D300三门90钢簧分支。	READY
141912_90_air	141912	SUV	Land Rover Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	HIGH	D300三门90空气悬架分支。	READY
141912_110_coil	141912	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D300五门110钢簧分支。	READY
141912_110_air	141912	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D300五门110空气悬架分支。	READY
141914_110_coil	141914	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D250 110 Hard Top钢簧分支。	READY
141914_110_air	141914	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D250 110 Hard Top空气悬架分支。	READY
141915_110_coil	141915	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	HIGH	D300 110 Hard Top钢簧分支。	READY
141915_110_air	141915	Van	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	D300 110 Hard Top空气悬架分支。	READY
141917	141917	SUV	Land Rover Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	HIGH	P400e仅对应五门110空气悬架分支。	READY
141920	141920	Sedan	Karma Revero I		4	EU-KARMA-REVERO-I-SEDAN-01	HIGH	四门插电式混合动力轿车外廓。	READY
141921	141921	Chassis	Goupil G4 L		2	EU-GOUPIL-G4-L-CHASSIS-PICKUP-01	HIGH	长轴版底盘/平台外廓。	READY
141922	141922	Chassis	Goupil G6		2	EU-GOUPIL-G6-PURE-CHASSIS-01	HIGH	三座驾驶室纯底盘外廓。	READY
141923	141923	Hatchback	BMW 1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	五门掀背外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5401-5500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-VW-DERBY-I-SEDAN-PRE1979-01	3836	1560	1352	Volkswagen Classic Derby vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-VW-DERBY-I-SEDAN-FROM1979-01	3915	1560	1352	Volkswagen Classic Derby vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-derby-profile-19687
EU-HYUNDAI-TERRACAN-I-SUV-01	4710	1860	1795	Auto-Data Hyundai Terracan generation specifications	https://www.auto-data.net/en/hyundai-terracan-generation-3002
EU-TOYOTA-YARIS-CROSS-I-XP210-SUV-FWD-01	4180	1765	1595	Toyota UK Media Yaris Cross launch press release	https://media.toyota.co.uk/all-new-yaris-cross-extends-toyotas-market-leading-hybrid-electric-suv-line-up/
EU-CITROEN-SPACETOURER-I-PREFL-MPV-M-01	4956	1920	1890	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-CITROEN-SPACETOURER-I-PREFL-MPV-XL-01	5306	1920	1890	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-NISSAN-NV400-I-FWD-VAN-L1H1-01	5048	2070	2307	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-NISSAN-NV400-I-FWD-VAN-L2H2-01	5548	2070	2499	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LIGIER-PULSE-3-THREEWHEELER-PICKUP-01	2280	800	1149	Ligier Professional Pulse 3 technical characteristics	https://www.ligier.at/wp-content/uploads/sites/19/2023/08/2023.06.22-FICHE-EQUIPEMENT-PULSE-3-EN.pdf
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-01	4866	1871	1462	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-FIAT-500X-I-FACELIFT-FWD-URBAN-SUV-01	4264	1796	1595	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-FIAT-500X-I-FACELIFT-FWD-CROSS-SUV-01	4269	1796	1603	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-CAYENNE-III-9YA-GTS-SUV-01	4929	1983	1676	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-911-992-TURBO-S-COUPE-01	4535	1900	1303	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	4535	1900	1301	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-BMW-5-G30-545E-XDRIVE-SEDAN-FACELIFT-01	4936	1868	1483	BMW Group Media Information BMW 545e xDrive Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0317777EN/461549
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-STREETSCOOTER-WORK-XL-BOX-VAN-01	7000	2140	2850	Deutsche Post DHL Group StreetScooter WORK XL Facts & Figures	https://group.dhl.com/content/dam/deutschepostdhl/en/media-center/media-relations/documents/2019/fact-sheet-streetscooter-work-xl-en.pdf
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-ISUZU-D-MAX-III-RG-SINGLE-CAB-STANDARD-01	5230	1870	1765	Isuzu D-Max RG Single Cab specifications	https://nsbmotors.co.za/ISUZU/ISUZU_D-MAX_RG_SINGLE-CAB_BAKKIE_SPECIFICATIONS_150722.pdf
EU-ISUZU-D-MAX-III-RG-SINGLE-CAB-L-01	5325	1870	1780	Isuzu D-Max RG Single Cab specifications	https://nsbmotors.co.za/ISUZU/ISUZU_D-MAX_RG_SINGLE-CAB_BAKKIE_SPECIFICATIONS_150722.pdf
EU-VW-GOLF-VIII-GTI-HATCHBACK-01	4287	1789	1478	Volkswagen South Africa Golf GTI and R Specifications	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/brochures/pv/2023-pv-mobile-brochure/golf_specsheet.pdf
EU-OPEL-ASTRA-K-SPORTS-TOURER-WAGON-CNG-01	4702	1809	1510	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-S-KLASSE-W223-SEDAN-SWB-01	5179	1954	1503	Mercedes-Benz S-Class Saloon W223 Owner's Manual vehicle dimensions	https://www.mercedes-benz-mena.com/iraq/en/services/manuals/s-class-saloon-2024-03-w223-mbux/vehicle-data/vehicle-dimensions
EU-MERCEDES-BENZ-S-KLASSE-V223-SEDAN-LWB-01	5289	1954	1503	Mercedes-Benz S-Class Saloon Long V223 Owner's Manual vehicle dimensions	https://www.mercedes-benz.com.sg/passengercars/services/manuals.html/s-class-saloon-long-2024-09-v223-mbux/vehicle-data/vehicle-dimensions
EU-MERCEDES-BENZ-GLE-II-V167-GLE350E-SUV-01	4924	1947	1795	Auto-Data Mercedes-Benz GLE SUV V167 GLE 350e	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350e-333hp-plug-in-hybrid-4matic-9g-tronic-46008
EU-BMW-3-G80-M3-SEDAN-RWD-01	4794	1903	1433	BMW Group Media Information BMW M3 Sedan Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0316649EN/476823
EU-BMW-4-G82-M4-COUPE-RWD-01	4794	1887	1393	BMW Group Media Information BMW M4 Coupe Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0316649EN/476824
EU-OPEL-CORSA-F-HATCHBACK-01	4060	1765	1433	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1605	Vauxhall Crossland X Price and Specification Guide MY2020.5	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/crossland/price-guides/Crossland_X_Spec_ePG_2_September_2020_Library-1602148545.pdf
EU-BMW-X4-G02-M40I-SUV-01	4733	1938	1621	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-OPEL-GRANDLAND-X-A18-SUV-01	4477	1856	1609	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-TOYOTA-HIGHLANDER-IV-XU70-SUV-01	4966	1930	1755	Toyota Highlander UK brochure	https://www.toyota.co.uk/content/dam/toyota/nmsc/united-kingdom/brochure-downloads/highlander.pdf
EU-MAZDA-3-IV-BP-SEDAN-01	4660	1795	1440	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-ROLLS-ROYCE-GHOST-II-SEDAN-SWB-01	5546	1978	1571	Carsales Rolls-Royce Ghost 2021 specifications	https://www.carsales.com.au/research/rolls-royce/ghost/2021/
EU-ROLLS-ROYCE-GHOST-II-SEDAN-LWB-01	5716	1978	1571	Carsales Rolls-Royce Ghost 2021 specifications	https://www.carsales.com.au/research/rolls-royce/ghost/2021/
EU-SKODA-KODIAQ-I-SUV-PREFL-01	4697	1882	1655	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E450-4MATIC-01	4945	1852	1467	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-V-KJ1-HATCHBACK-01	4059	1780	1444	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-VW-KAEFER-TYPE11-SEDAN-1600-01	4060	1550	1500	Volkswagen Classic Beetle 1200/1200L profile; Volkswagen Classic Beetle 1600/1600i profile	https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-12001200l-profile-19585;https://www.volkswagen-newsroom.com/en/vehicle-data-beetle-kaefer-16001600i-profile-19604
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-E300E-01	4945	1852	1476	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-DACIA-DOKKER-I-F67-VAN-01	4363	1751	1809	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-DACIA-DOKKER-I-MPV-01	4363	1751	1814	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	4633	1789	1498	Volkswagen Newsroom Golf Variant design and dimensions	https://www.volkswagen-newsroom.com/en/the-new-golf-variant-and-golf-alltrack-international-media-drive-6540/design-and-dimensions-6543
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-KIA-STONIC-I-YB-SUV-01	4140	1760	1520	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-KIA-RIO-IV-YB-HATCHBACK-01	4065	1725	1450	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-OPEL-KAPITAEN-B-SEDAN-01	4907	1852	1450	Automobile-Catalog 1969 Opel Kapitan 2800 S; Automobile-Catalog 1970 Opel Kapitan 2800	https://www.automobile-catalog.com/car/1969/2417075/opel_kapitan_2800_s.html;https://www.automobile-catalog.com/car/1970/2417045/opel_kapitan_2800.html
EU-OPEL-SENATOR-A2-SEDAN-COMPREX-01	4839	1722	1415	Auto-Data Opel Senator A2 2.3 Comprex D specifications	https://www.auto-data.net/en/opel-senator-a-facelift-1982-2.3-comprex-d-95hp-26931
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-AUDI-E-TRON-S-I-GE-SUV-01	4902	1976	1629	Automobile-Catalog 2021 Audi e-tron S specifications	https://www.automobile-catalog.com/car/2021/3006470/audi_e-tron_s.html
EU-OPEL-KADETT-C-COUPE-01	4127	1580	1340	Automoli Opel Kadett C Coupe vehicle specifications	https://www.automoli.com/en/vehicles/opel/kadett/kadett-c-coupe-512/
EU-OPEL-ZAFIRA-LIFE-I-MPV-S-01	4606	1920	1905	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-OPEL-ZAFIRA-LIFE-I-MPV-M-01	4956	1920	1890	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-OPEL-ZAFIRA-LIFE-I-MPV-L-01	5306	1920	1890	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-E-KLASSE-W213-E300DE-4MATIC-SEDAN-FACELIFT-01	4935	1852	1481	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-MAZDA-MX-30-I-SUV-01	4395	1795	1570	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-RANGE-ROVER-SPORT-II-L494-SUV-FACELIFT-01	4879	1983	1780	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-RANGE-ROVER-EVOQUE-II-L551-SUV-01	4371	1904	1649	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-DISCOVERY-SPORT-I-L550-SUV-FACELIFT-02	4597	1904	1727	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-COIL-01	4583	1996	1974	Land Rover Media 22MY Defender 90 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_90_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-90-AIR-01	4583	1996	1969	Land Rover Media 22MY Defender 90 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_90_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-COIL-01	5018	1996	1972	Land Rover Media 22MY Defender 110 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_110_TECH_DATA_22MY_250221.pdf
EU-LAND-ROVER-DEFENDER-II-L663-SUV-110-AIR-01	5018	1996	1967	Land Rover Media 22MY Defender 110 Technical Data	https://jlrnewsroom.media/wp-content/uploads/2021/02/LR_DEF_110_TECH_DATA_22MY_250221.pdf
EU-KARMA-REVERO-I-SEDAN-01	4999	1984	1331	J.D. Power 2018 Karma Revero specifications	https://www.jdpower.com/cars/2018/karma/revero/4-door-sedan/specs
EU-GOUPIL-G4-L-CHASSIS-PICKUP-01	4130	1200	1893	Goupil G4 long-version dimensions	https://grau-maquinaria.com/goupil_g4.htm
EU-GOUPIL-G6-PURE-CHASSIS-01	4796	1704	1921	Goupil G6 official brochure	https://hafog.dk/wp-content/uploads/files/393362_Goupil%20Brochure%20G6%20eng.pdf
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	Task-provided locked cross-batch DIMENSION_GROUP index	sandbox:/mnt/data/all_5401-5500_cross_batch_dimension_index_source.txt
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5401-5500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://nsbmotors.co.za/ISUZU/ISUZU_D-MAX_RG_SINGLE-CAB_BAKKIE_SPECIFICATIONS_150722.pdf "D-MAX_RG_SINGLE-CAB_SPEC-BOOKLET_A4_11Jul2022.indd"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5791 行）
- 累计尺寸组：dimension_groups_final.tsv（2104 行）

- 尺寸冲突协调：
  - EU-OPEL-CROSSLAND-X-P17-SUV-01 -> EU-OPEL-CROSSLAND-X-P17-SUV-02：4212x1765x1590 与 4212x1765x1605，创建新尺寸组
