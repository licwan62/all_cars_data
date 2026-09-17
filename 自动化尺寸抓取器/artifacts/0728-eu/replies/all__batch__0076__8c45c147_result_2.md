# 任务：all 第 7501-7600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0076__8c45c147


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7501-7600 行

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
all 第 7501-7600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-100-C1-COUPE-01	4398	1750	1340
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-03	4590	1729	1421
EU-AUDI-100-C2-AVANT-01	4587	1768	1390
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390
EU-AUDI-100-C2-WAGON-FACELIFT-01	4590	1768	1390
EU-AUDI-100-C2-WAGON-PREFL-01	4587	1768	1390
EU-AUDI-100-C3-AVANT-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-02	4793	1814	1421
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422
EU-AUDI-100-C3-WAGON-QUATTRO-01	4793	1814	1422
EU-AUDI-100-C4-S4-AVANT-WAGON-01	4790	1805	1422
EU-AUDI-100-C4-S4-SEDAN-01	4790	1805	1420
EU-AUDI-100-C4-SEDAN-FWD-01	4790	1777	1431
EU-AUDI-100-C4-SEDAN-QUATTRO-01	4790	1777	1437
EU-AUDI-100-C4-WAGON-FWD-01	4790	1777	1440
EU-AUDI-100-C4-WAGON-QUATTRO-01	4790	1777	1448
EU-AUDI-200-C3-20V-SEDAN-01	4913	1814	1422
EU-AUDI-200-C3-SEDAN-FACELIFT-01	4793	1814	1422
EU-AUDI-200-C3-SEDAN-PREFL-01	4807	1814	1422
EU-AUDI-200-C3-WAGON-20V-QUATTRO-01	4913	1814	1422
EU-AUDI-200-C3-WAGON-QUATTRO-01	4807	1814	1422
EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	4534	1823	1484
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	4813	1783	1715
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	4844	1783	1720
EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	4788	1783	1702
EU-FORD-USA-EXPLORER-I-UN46-SUV-3D-01	4430	1783	1715
EU-FORD-USA-EXPLORER-I-UN46-SUV-5D-01	4681	1783	1709
EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	5126	1915	1789
EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	5126	1915	1789
EU-RENAULT-MEGANE-SCENIC-I-MPV-01	4134	1719	1675
EU-SEAT-FURA-025A-HATCHBACK-3D-01	3711	1536	1370
EU-SEAT-INCA-9K-VAN-01	4207	1696	1836
EU-SEAT-TERRA-MPV-3D-01	3869	1490	1895
EU-SEAT-TERRA-VAN-3D-01	3869	1490	1895
EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	4321	1662	1424
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	4511	1731	1429
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1840-01	4330	1841	1840
EU-SSANGYONG-KORANDO-II-KJ-SUV-H1940-01	4330	1841	1940
EU-VW-GOLF-II-HATCHBACK-RALLYE-01	4035	1700	1405
EU-VW-GOLF-II-HATCHBACK-STD-01	3985	1665	1415
EU-VW-GOLF-III-CABRIO-CONVERTIBLE-01	4020	1695	1400
EU-VW-GOLF-III-HATCHBACK-3D-01	4020	1695	1425
EU-VW-GOLF-III-HATCHBACK-5D-01	4020	1695	1425
EU-VW-GOLF-III-VARIANT-WAGON-01	4340	1695	1430
EU-VW-JETTA-II-SEDAN-SPORT-01	4315	1665	1395
EU-VW-JETTA-II-SEDAN-STD-01	4315	1665	1415
EU-VW-JETTA-II-SYNCRO-SEDAN-01	4315	1680	1415
EU-VW-POLO-III-6KV-SEDAN-01	4164	1640	1414
EU-VW-POLO-III-6N-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	3765	1570	1350
EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	3655	1580	1355
EU-VW-POLO-II-TYPE86C-SEDAN-01	3970	1570	1350
EU-VW-POLO-I-TYPE86-HATCHBACK-01	3512	1560	1344

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Focus iii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	85	115	Jul 2010	Jun 2014	2024-03-01	7997
Ford USA	Mustang	3.8	Coupe	Heckantrieb	Benzin	112	152	Sep 1993	May 1999	2024-03-01	7998
Ford USA	Mustang convertible	3.8	Cabriolet	Heckantrieb	Benzin	112	152	Sep 1993	Jul 1999	2024-03-01	7999
Ford USA	Mustang	4.9	Coupe	Heckantrieb	Benzin	160	218	Sep 1993	Oct 1995	2024-03-01	8000
Ford USA	Mustang convertible	4.9	Cabriolet	Heckantrieb	Benzin	160	218	Sep 1993	Dec 1995	2024-03-01	8001
Ford USA	Taurus	3	Stufenheck	Frontantrieb	Benzin	108	147	Sep 1995	Dec 1999	2024-03-01	8002
Ford USA	Taurus	3	Kombi	Frontantrieb	Benzin	108	147	Sep 1996	Dec 1999	2024-03-01	8003
Ford USA	Taurus	3.0 24V	Stufenheck	Frontantrieb	Benzin	149	203	Sep 1996	Dec 1999	2024-03-01	8004
Ford USA	Taurus	3.0 24V	Kombi	Frontantrieb	Benzin	149	203	Jun 1995	Dec 1999	2024-03-01	8005
Ford USA	Windstar	3.8 V6	Großraumlimousine	Frontantrieb	Benzin	149	203	Jan 1995	Jun 1998	2024-03-01	8006
Ford USA	Explorer	4.9 4WD	SUV	Allrad	Benzin	157	213	Jan 1996	Dec 2001	2024-03-01	8007
Renault	Megane scénic	1.9 D	Großraumlimousine	Frontantrieb	Diesel	47	64	Mar 1997	Sep 1999	2024-05-01	8008
Skoda	Octavia	1.6	Schrägheck	Frontantrieb	Benzin	74	101	Feb 1997	Dec 2007	2024-03-01	8009
KTM	X-Bow	2.0 R	Cabriolet	Heckantrieb	Benzin	200	272	Jul 2010	-	2024-03-01	8010
Ford	Focus iii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	103	140	Jul 2010	Jun 2014	2024-03-01	8011
Ford	Focus iii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	120	163	Jul 2010	Jun 2014	2024-03-01	8013
Ford	Focus iii	1.6 TI	Schrägheck	Frontantrieb	Benzin	77	105	Jul 2010	Feb 2020	2024-03-01	8014
Ford	Focus iii	1.6 TI	Schrägheck	Frontantrieb	Benzin	92	125	Jul 2010	Dec 2017	2024-03-01	8015
Ford	Focus iii	1.6 Flexifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	88	120	Jul 2010	Feb 2020	2024-03-01	8017
Ford	Focus iii	1.6 Ecoboost	Schrägheck	Frontantrieb	Benzin	110	150	Jul 2010	Jun 2014	2024-03-01	8019
Mazda	626 ii hatchback	2	Schrägheck	Frontantrieb	Benzin	68	93	Jan 1985	Sep 1987	2024-03-01	8021
Ford	Focus iii	1.6 Ecoboost	Schrägheck	Frontantrieb	Benzin	134	182	Jul 2010	Jun 2014	2024-03-01	8022
Ford	Focus iii	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	70	95	Jul 2010	Dec 2017	2024-03-01	8027
Mazda	323 p v	1.3 16V	Schrägheck	Frontantrieb	Benzin	54	73	Oct 1996	Sep 1998	2024-03-01	8035
Mazda	323 p v	1.5 16V	Schrägheck	Frontantrieb	Benzin	65	88	Oct 1996	Sep 1998	2024-03-01	8036
Mazda	323 p v	2.0 D	Schrägheck	Frontantrieb	Diesel	52	71	Oct 1996	Sep 1998	2024-03-01	8037
Asia Motors	Hi-Topic	2.7 D Heckantrieb	Bus	Heckantrieb	Diesel	55	75	Jun 1993	Dec 1999	2024-03-01	8038
Ford	Focus iii	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Jul 2010	Dec 2017	2024-03-01	8039
VW	Golf ii	1.3 CAT	Schrägheck	Frontantrieb	Benzin	40	55	Jun 1986	Dec 1992	2024-03-01	8040
Ford	Focus iii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	85	115	Jul 2010	Jun 2014	2024-03-01	8041
VW	Jetta ii	1.3 CAT	Stufenheck	Frontantrieb	Benzin	40	55	Jun 1987	Dec 1991	2024-03-01	8042
VW	Polo	1.3	Coupe	Frontantrieb	Benzin	40	55	Aug 1983	Jun 1987	2024-03-01	8043
VW	Polo	1.3	Schrägheck	Frontantrieb	Benzin	40	55	Aug 1983	Jul 1988	2024-03-01	8044
VW	Polo	1.3	Stufenheck	Frontantrieb	Benzin	40	55	Jan 1985	Jul 1987	2024-03-01	8045
VW	Polo	1	Schrägheck	Frontantrieb	Benzin	33	45	Aug 1985	Jan 1992	2024-03-01	8046
VW	Polo	1	Coupe	Frontantrieb	Benzin	33	45	Aug 1985	Jan 1992	2024-03-01	8047
VW	Golf ii	1.8 GTI	Schrägheck	Frontantrieb	Benzin	79	107	Aug 1985	Oct 1987	2024-03-01	8048
VW	Jetta ii	1.8	Stufenheck	Frontantrieb	Benzin	79	107	Aug 1985	Oct 1987	2024-03-01	8049
VW	Golf ii	1.8	Schrägheck	Frontantrieb	Benzin	66	90	Aug 1984	Oct 1991	2024-03-01	8050
VW	Golf ii	1.8 I CAT Syncro	Schrägheck	Allrad	Benzin	66	90	Aug 1987	Oct 1991	2024-03-01	8051
VW	Jetta ii	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1984	Oct 1991	2024-03-01	8052
VW	Polo	1.3	Coupe	Frontantrieb	Benzin	55	75	Sep 1982	Sep 1989	2024-03-01	8053
VW	Polo	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1982	Sep 1989	2024-03-01	8054
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Aug 1983	Jul 1989	2024-03-01	8055
Audi	100	1.8 Quattro	Stufenheck	Allrad	Benzin	66	90	Oct 1984	Jul 1988	2024-03-01	8056
Audi	100	1.8 Quattro	Kombi	Allrad	Benzin	66	90	Oct 1984	Jul 1988	2024-03-01	8057
Ford	Focus iii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	103	140	Jul 2010	Jun 2014	2024-03-01	8058
Ford	Focus iii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	120	163	Jul 2010	Jun 2014	2024-03-01	8077
Seat	Toledo	1.9 D	Schrägheck	Frontantrieb	Diesel	47	64	Dec 1995	Mar 1999	2024-03-01	8095
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	77	105	Jul 2010	Feb 2020	2024-03-01	8096
Seat	Inca	1.9 SDI	Kasten/Kombi	Frontantrieb	Diesel	47	64	Nov 1995	Jun 2003	2024-03-01	8097
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	92	125	Jul 2010	Feb 2020	2024-03-01	8111
Seat	Fura	0.9	Schrägheck	Frontantrieb	Benzin	31	43	Jan 1982	Jun 1986	2024-03-01	8114
Seat	Fura	1.4 Crono	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1982	Jun 1986	2024-03-01	8115
Ford	Focus iii turnier	1.6 Flexifuel	Kombi	Frontantrieb	Benzin/Ethanol	88	120	Jul 2010	Feb 2020	2024-03-01	8150
Ford	Focus iii turnier	1.6 Ecoboost	Kombi	Frontantrieb	Benzin	110	150	Jul 2010	Jun 2014	2024-03-01	8151
Audi	100	2	Stufenheck	Frontantrieb	Benzin	85	115	Aug 1984	Dec 1987	2024-03-01	8158
Audi	100	2.0 E	Kombi	Frontantrieb	Benzin	85	115	Jan 1985	Dec 1987	2024-03-01	8159
Ssangyong	Korando	2.2 D	Geländewagen geschlossen	Allrad	Diesel	50	68	Dec 1988	Dec 1996	2024-03-01	8160
Audi	100	2.2 CAT	Kombi	Frontantrieb	Benzin	101	137	Jun 1989	Nov 1990	2024-03-01	8161
Audi	100	2.2 CAT Quattro	Stufenheck	Allrad	Benzin	101	137	Oct 1984	Dec 1987	2024-03-01	8162
Audi	100	2.2 CAT Quattro	Kombi	Allrad	Benzin	101	137	Jun 1989	Nov 1990	2024-03-01	8163
Audi	100	2.2 CAT	Stufenheck	Frontantrieb	Benzin	101	137	Oct 1984	Dec 1987	2024-03-01	8164
Ford	Focus iii turnier	1.6 Ecoboost	Kombi	Frontantrieb	Benzin	134	182	Jul 2010	Jun 2014	2024-03-01	8165
Audi	200 c3	2.3	Stufenheck	Frontantrieb	Benzin	100	136	Nov 1986	Sep 1991	2024-03-01	8166
Audi	200 c3 avant	2.3	Kombi	Frontantrieb	Benzin	100	136	Nov 1986	Sep 1991	2024-03-01	8167
Audi	200 c3 avant	2.2 Turbo	Kombi	Frontantrieb	Benzin	121	165	Aug 1985	Sep 1991	2024-03-01	8168
Hyundai	H100	2.5 D	Bus	Heckantrieb	Diesel	57	78	Dec 1994	Mar 2000	2024-03-01	8169
Ford	Focus iii turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	70	95	Jul 2010	Feb 2020	2024-03-01	8170
VW	Passat b1 variant	1.6 I	Kombi	Frontantrieb	Benzin	81	110	Jun 1978	Jul 1980	2024-03-01	8171
VW	Passat b1 variant	1.6 D	Kombi	Frontantrieb	Diesel	40	54	Aug 1980	Jul 1981	2024-03-01	8172
Vauxhall	Chevette cc	1300	Schrägheck	Heckantrieb	Benzin	39	53	Mar 1975	Dec 1985	2024-03-01	8173
Vauxhall	Chevette cc	1300	Schrägheck	Heckantrieb	Benzin	42	57	Mar 1975	Dec 1985	2024-03-01	8174
Ford	Focus iii turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	85	115	Jul 2010	Feb 2020	2024-03-01	8175
Seat	Terra	0.9 CAT	Kombi	Frontantrieb	Benzin	29	40	Feb 1992	Dec 1994	2024-03-01	8176
Seat	Terra	0.9 CAT	Kasten/Kombi	Frontantrieb	Benzin	29	40	Jan 1990	Dec 1995	2024-03-01	8177
Renault	Megane ii grandtour	1.6 16V	Kombi	Frontantrieb	Benzin	75	102	May 2005	Jul 2009	2024-03-01	8178
Aston Martin	Db6 vantage	4	Coupe	Heckantrieb	Benzin	210	286	Oct 1964	Dec 1970	2024-03-01	8179
Aston Martin	Db6 vantage	4	Coupe	Heckantrieb	Benzin	243	330	Oct 1964	Dec 1970	2024-03-01	8180
Aston Martin	Db6 volante	4	Cabriolet	Heckantrieb	Benzin	210	286	Oct 1964	Dec 1970	2024-03-01	8181
Aston Martin	Dbs vantage	4	Coupe	Heckantrieb	Benzin	210	286	Jan 1966	Dec 1972	2024-03-01	8182
Aston Martin	Lagonda i	5.3	Stufenheck	Heckantrieb	Benzin	250	340	Jan 1976	Dec 1997	2024-03-01	8183
Aston Martin	Lagonda i shooting brake	5.3	Kombi	Heckantrieb	Benzin	228	310	Jan 1976	Dec 1997	2024-03-01	8184
Aston Martin	Tickford capri	2.8 T	Coupe	Heckantrieb	Benzin	153	208	Jan 1982	Dec 1985	2024-03-01	8185
Aston Martin	V8	5.3	Coupe	Heckantrieb	Benzin	250	340	Jan 1969	Dec 1989	2024-03-01	8186
Aston Martin	V8	5.3	Coupe	Heckantrieb	Benzin	376	511	Jan 1969	Dec 1989	2024-03-01	8187
Aston Martin	V8	5.3	Cabriolet	Heckantrieb	Benzin	250	340	Jan 1978	Dec 1989	2024-03-01	8188
Aston Martin	V8	5.3	Cabriolet	Heckantrieb	Benzin	276	375	Jan 1978	Dec 1989	2024-03-01	8189
Aston Martin	Zagato vantage	5.3	Coupe	Heckantrieb	Benzin	322	438	Jan 1986	Dec 1989	2024-03-01	8190
Aston Martin	Zagato volante	5.3	Cabriolet	Heckantrieb	Benzin	228	309	Jan 1986	Dec 1989	2024-03-01	8191
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	246	336	Jan 1988	Dec 1992	2024-03-01	8192
Aston Martin	Virage volante	5.3	Cabriolet	Heckantrieb	Benzin	246	336	Sep 1990	Dec 1995	2024-03-01	8193
Aston Martin	Virage shooting brake	5.3	Kombi	Heckantrieb	Benzin	246	335	Jan 1993	Dec 1995	2024-03-01	8194
Aston Martin	Virage saloon	5.3	Stufenheck	Heckantrieb	Benzin	246	335	Jan 1994	Dec 1995	2024-03-01	8195
Aston Martin	Virage saloon	6.3	Stufenheck	Heckantrieb	Benzin	246	335	Jan 1995	Dec 1995	2024-03-01	8196
Aston Martin	Virage shooting brake	6.3	Kombi	Heckantrieb	Benzin	373	507	Jan 1994	Dec 1995	2024-03-01	8197
Aston Martin	Virage volante	6.3	Cabriolet	Heckantrieb	Benzin	373	507	Sep 1990	Dec 1995	2024-03-01	8198
Aston Martin	Virage vantage	5.3	Coupe	Heckantrieb	Benzin	410	558	Oct 1992	Dec 2000	2024-03-01	8199
Aston Martin	Virage limited edition vantage	5.3	Coupe	Heckantrieb	Benzin	246	335	Jan 1995	Dec 1995	2024-03-01	8200
Aston Martin	Db7 volante	3.2	Cabriolet	Heckantrieb	Benzin	250	340	Jan 1996	Oct 2003	2024-03-01	8202


--- Round 1 / 首次发送 ---
## 更新点

* 完成 100 个输入 Ktype 的首轮物理车身聚类，形成 122 条映射行。
* 复用累计尺寸组 27 个；首次创建并闭合尺寸组 27 个。
* Ford Focus III 已按三厢、两厢改款前后、旅行版改款前后分别归组；对应三维来自 Ford UK 规格表。([Dezo's Garage][1])
* Vauxhall Chevette CC 已纠正为三门掀背，而不是五门；三维为 3945×1570×1308 mm。([汽车数据][2])
* 尚未闭合的记录集中在多轴距商用车、早期 Korando，以及 Aston Martin Works/Coachbuilt 稀有车身。

## 当前批次进度

* 输入 Ktype：100
* 已完成 Ktype：85
* 待处理 Ktype：15
* READY 映射：107
* PENDING 映射：15
* 当前已引用尺寸组：54
* 本轮首次创建尺寸组：27
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7997	7997	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
7998_prefl	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-COUPE-PREFL-01	HIGH	覆盖SN95初期外廓。	READY
7998_facelift	7998	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-COUPE-FACELIFT-01	HIGH	覆盖1999 New Edge外廓。	READY
7999_prefl	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-CONVERTIBLE-PREFL-01	HIGH	覆盖SN95初期敞篷外廓。	READY
7999_facelift	7999	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-CONVERTIBLE-FACELIFT-01	HIGH	覆盖1999 New Edge敞篷外廓。	READY
8000	8000	Coupe	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-COUPE-PREFL-01	HIGH		READY
8001	8001	Convertible	Mustang IV	SN95	2	EU-FORD-USA-MUSTANG-IV-SN95-CONVERTIBLE-PREFL-01	HIGH		READY
8002	8002	Sedan	Taurus III	DN101	4	EU-FORD-USA-TAURUS-III-DN101-SEDAN-01	HIGH		READY
8003	8003	Wagon	Taurus III	DN101	5	EU-FORD-USA-TAURUS-III-DN101-WAGON-01	HIGH		READY
8004	8004	Sedan	Taurus III	DN101	4	EU-FORD-USA-TAURUS-III-DN101-SEDAN-01	HIGH		READY
8005	8005	Wagon	Taurus III	DN101	5	EU-FORD-USA-TAURUS-III-DN101-WAGON-01	HIGH		READY
8006_prefl	8006	MPV	Windstar I			EU-FORD-USA-WINDSTAR-I-MPV-PREFL-01	HIGH	覆盖改款前外廓。	READY
8006_facelift	8006	MPV	Windstar I			EU-FORD-USA-WINDSTAR-I-MPV-FACELIFT-01	HIGH	覆盖改款后外廓。	READY
8007_prefl	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-PREFL-01	HIGH	覆盖1996-1997外廓。	READY
8007_1998	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-1998-01	HIGH	覆盖1998过渡外廓。	READY
8007_facelift	8007	SUV	Explorer II	UN105	5	EU-FORD-USA-EXPLORER-II-UN105-SUV-5D-FACELIFT-01	HIGH	覆盖1999-2001改款外廓。	READY
8008	8008	MPV	Megane Scenic I	JA	5	EU-RENAULT-MEGANE-SCENIC-I-MPV-01	HIGH		READY
8009_prefl	8009	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门掀背外廓。	READY
8009_facelift	8009	Hatchback	Octavia I	1U	5	EU-SKODA-OCTAVIA-I-1U-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门掀背外廓。	READY
8010	8010	Convertible	X-Bow			EU-KTM-X-BOW-R-CONVERTIBLE-01	HIGH		READY
8011	8011	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
8013	8013	Sedan	Focus III	DYB	4	EU-FORD-FOCUS-III-DYB-SEDAN-4D-01	HIGH		READY
8014_prefl	8014	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门外廓。	READY
8014_facelift	8014	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门外廓。	READY
8015_prefl	8015	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门外廓。	READY
8015_facelift	8015	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门外廓。	READY
8017_prefl	8017	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门外廓。	READY
8017_facelift	8017	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门外廓。	READY
8019	8019	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH		READY
8021	8021	Hatchback	626 II	GC	5	EU-MAZDA-626-II-GC-HATCHBACK-5D-01	HIGH		READY
8022	8022	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH		READY
8027_prefl	8027	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门外廓。	READY
8027_facelift	8027	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门外廓。	READY
8035	8035	Hatchback	323 V	BA	3	EU-MAZDA-323-V-BA-HATCHBACK-3D-01	MEDIUM	P/C三门掀背物理外廓。	READY
8036	8036	Hatchback	323 V	BA	3	EU-MAZDA-323-V-BA-HATCHBACK-3D-01	MEDIUM	P/C三门掀背物理外廓。	READY
8037	8037	Hatchback	323 V	BA	3	EU-MAZDA-323-V-BA-HATCHBACK-3D-01	MEDIUM	P/C三门掀背物理外廓。	READY
8038	8038	Bus	Hi-Topic				LOW	候选资料存在AM715/AM725及车长配置差异，尚不能确定本Ktype物理车身。	PENDING: 具体底盘代码与车长配置未确认
8039_prefl	8039	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH	覆盖改款前五门外廓。	READY
8039_facelift	8039	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	HIGH	覆盖改款后五门外廓。	READY
8040	8040	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH		READY
8041	8041	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH		READY
8042	8042	Sedan	Jetta II	19E	4	EU-VW-JETTA-II-SEDAN-STD-01	HIGH		READY
8043	8043	Coupe	Polo II	86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	厂方Coupe名称，三门外廓复用Type 86C改款前组。	READY
8044	8044	Hatchback	Polo II	86C		EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
8045	8045	Sedan	Polo II	86C	2	EU-VW-POLO-II-TYPE86C-SEDAN-01	HIGH		READY
8046_prefl	8046	Hatchback	Polo II	86C		EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	覆盖改款前外廓。	READY
8046_facelift	8046	Hatchback	Polo II	86C		EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH	覆盖1990年后改款外廓。	READY
8047_prefl	8047	Coupe	Polo II	86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	厂方Coupe名称，覆盖改款前三门外廓。	READY
8047_facelift	8047	Coupe	Polo II	86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-FACELIFT-01	HIGH	厂方Coupe名称，覆盖改款后三门外廓。	READY
8048	8048	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	MEDIUM	GTI未形成独立宽体外廓。	READY
8049	8049	Sedan	Jetta II	19E	4	EU-VW-JETTA-II-SEDAN-SPORT-01	HIGH		READY
8050	8050	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	HIGH		READY
8051	8051	Hatchback	Golf II	19E		EU-VW-GOLF-II-HATCHBACK-STD-01	MEDIUM	Syncro驱动配置未改变主体外廓。	READY
8052	8052	Sedan	Jetta II	19E	4	EU-VW-JETTA-II-SEDAN-STD-01	HIGH		READY
8053	8053	Coupe	Polo II	86C	3	EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH	厂方Coupe名称，三门外廓复用Type 86C改款前组。	READY
8054	8054	Hatchback	Polo II	86C		EU-VW-POLO-II-TYPE86C-HATCHBACK-PREFL-01	HIGH		READY
8055_prefl	8055	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	覆盖改款前外廓。	READY
8055_facelift	8055	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	覆盖改款后外廓。	READY
8056	8056	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	结束于改款切换前。	READY
8057	8057	Wagon	100 C3	44	5	EU-AUDI-100-C3-WAGON-QUATTRO-01	HIGH		READY
8058	8058	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH		READY
8077	8077	Hatchback	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	HIGH		READY
8095	8095	Hatchback	Toledo I	1L	5	EU-SEAT-TOLEDO-I-1L-HATCHBACK-5D-01	HIGH		READY
8096_prefl	8096	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH	覆盖改款前旅行版外廓。	READY
8096_facelift	8096	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	HIGH	覆盖改款后旅行版外廓。	READY
8097	8097	Van	Inca I	9K		EU-SEAT-INCA-9K-VAN-01	HIGH	Kasten/Kombi按封闭厢式主体外廓归组。	READY
8111_prefl	8111	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH	覆盖改款前旅行版外廓。	READY
8111_facelift	8111	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	HIGH	覆盖改款后旅行版外廓。	READY
8114	8114	Hatchback	Fura	025A	3	EU-SEAT-FURA-025A-HATCHBACK-3D-01	HIGH		READY
8115	8115	Hatchback	Fura	025A	3	EU-SEAT-FURA-025A-HATCHBACK-3D-01	HIGH		READY
8150_prefl	8150	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH	覆盖改款前旅行版外廓。	READY
8150_facelift	8150	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	HIGH	覆盖改款后旅行版外廓。	READY
8151	8151	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH		READY
8158	8158	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH		READY
8159	8159	Wagon	100 C3	44	5	EU-AUDI-100-C3-AVANT-01	MEDIUM	前期Avant主体外廓。	READY
8160	8160	SUV	Korando				LOW	累计KJ组从后续代际开始，不能覆盖1988-1996输入区间。	PENDING: 早期Korando具体代际、车身及高度未闭合
8161	8161	Wagon	100 C3	44	5	EU-AUDI-100-C3-AVANT-01	HIGH		READY
8162	8162	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH		READY
8163	8163	Wagon	100 C3	44	5	EU-AUDI-100-C3-WAGON-QUATTRO-01	HIGH		READY
8164	8164	Sedan	100 C3	44	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH		READY
8165	8165	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH		READY
8166_prefl	8166	Sedan	200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH	覆盖改款前外廓。	READY
8166_facelift	8166	Sedan	200 C3	44	4	EU-AUDI-200-C3-SEDAN-FACELIFT-01	HIGH	覆盖改款后外廓。	READY
8167_prefl	8167	Wagon	200 C3	44	5	EU-AUDI-200-C3-WAGON-QUATTRO-01	MEDIUM	覆盖改款前Avant主体外廓。	READY
8167_facelift	8167	Wagon	200 C3	44	5	EU-AUDI-200-C3-WAGON-FACELIFT-01	MEDIUM	覆盖改款后Avant主体外廓。	READY
8168_prefl	8168	Wagon	200 C3	44	5	EU-AUDI-200-C3-WAGON-QUATTRO-01	MEDIUM	覆盖改款前Avant主体外廓。	READY
8168_facelift	8168	Wagon	200 C3	44	5	EU-AUDI-200-C3-WAGON-FACELIFT-01	MEDIUM	覆盖改款后Avant主体外廓。	READY
8169	8169	Bus	H100				LOW	输入生产期覆盖多种轴距、车顶及客车配置，当前证据不能锁定单一外廓。	PENDING: H100具体轴距、车顶和车身代码未确认
8170_prefl	8170	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH	覆盖改款前旅行版外廓。	READY
8170_facelift	8170	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	HIGH	覆盖改款后旅行版外廓。	READY
8171	8171	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-01	HIGH		READY
8172	8172	Wagon	Passat B1	33	5	EU-VW-PASSAT-B1-TYPE33-WAGON-01	MEDIUM	按输入明确的B1 Variant车身映射；结束月属于部分市场收尾期。	READY
8173	8173	Hatchback	Chevette CC		3	EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-3D-01	HIGH		READY
8174	8174	Hatchback	Chevette CC		3	EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-3D-01	HIGH		READY
8175_prefl	8175	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	HIGH	覆盖改款前旅行版外廓。	READY
8175_facelift	8175	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	HIGH	覆盖改款后旅行版外廓。	READY
8176	8176	MPV	Terra		3	EU-SEAT-TERRA-MPV-3D-01	HIGH		READY
8177	8177	Van	Terra		3	EU-SEAT-TERRA-VAN-3D-01	HIGH		READY
8178	8178	Wagon	Megane II		5	EU-RENAULT-MEGANE-II-WAGON-01	HIGH		READY
8179	8179	Coupe	DB6		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH		READY
8180	8180	Coupe	DB6		2	EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	HIGH		READY
8181	8181	Convertible	DB6		2	EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	HIGH		READY
8182	8182	Coupe	DBS		2	EU-ASTON-MARTIN-DBS-VANTAGE-COUPE-01	HIGH		READY
8183	8183	Sedan	Lagonda I		4	EU-ASTON-MARTIN-LAGONDA-I-SEDAN-01	MEDIUM	标准四门Lagonda外廓；输入结束年月晚于量产期。	READY
8184	8184	Wagon	Lagonda I				LOW	Shooting Brake为稀有改装/coachbuilt车身，尚无同一配置三维闭合。	PENDING: Shooting Brake具体制造商与外廓未确认
8185	8185	Coupe	Tickford Capri		3		LOW	Tickford改装前后保险杠与外部套件会改变外廓，当前来源未闭合三维。	PENDING: Tickford Capri量产外廓三维未闭合
8186	8186	Coupe	Aston Martin V8		2		LOW	生产区间覆盖早期标准车身、Vantage宽体及不同保险杠，不能锁定单一外廓。	PENDING: V8 Coupe具体车身阶段与宽体配置未确认
8187	8187	Coupe	Aston Martin V8		2		LOW	生产区间覆盖早期标准车身、Vantage宽体及不同保险杠，不能锁定单一外廓。	PENDING: V8 Coupe具体车身阶段与宽体配置未确认
8188	8188	Convertible	Aston Martin V8		2		LOW	生产区间覆盖Volante多个车身阶段及宽体配置，不能锁定单一外廓。	PENDING: V8 Volante具体车身阶段与宽体配置未确认
8189	8189	Convertible	Aston Martin V8		2		LOW	生产区间覆盖Volante多个车身阶段及宽体配置，不能锁定单一外廓。	PENDING: V8 Volante具体车身阶段与宽体配置未确认
8190	8190	Coupe	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-VANTAGE-COUPE-01	HIGH		READY
8191	8191	Convertible	V8 Zagato		2	EU-ASTON-MARTIN-V8-ZAGATO-VOLANTE-CONVERTIBLE-01	HIGH		READY
8192	8192	Coupe	Virage		2	EU-ASTON-MARTIN-VIRAGE-COUPE-01	MEDIUM	功率对应基础Virage外廓；输入车型名含Vantage。	READY
8193	8193	Convertible	Virage		2	EU-ASTON-MARTIN-VIRAGE-VOLANTE-CONVERTIBLE-01	HIGH		READY
8194	8194	Wagon	Virage				LOW	Shooting Brake为Works/coachbuilt稀有车身，缺少可追溯同配置三维。	PENDING: Virage Shooting Brake外廓未闭合
8195	8195	Sedan	Virage		4		LOW	四门Saloon为Works改造车身，标准Virage尺寸不可直接复用。	PENDING: Virage Saloon 5.3外廓未闭合
8196	8196	Sedan	Virage		4		LOW	6.3四门Saloon为Works改造宽体车身，缺少同配置三维。	PENDING: Virage Saloon 6.3外廓未闭合
8197	8197	Wagon	Virage				LOW	6.3 Shooting Brake为Works改造宽体车身，缺少同配置三维。	PENDING: Virage Shooting Brake 6.3外廓未闭合
8198	8198	Convertible	Virage		2	EU-ASTON-MARTIN-VIRAGE-VOLANTE-6.3-CONVERTIBLE-01	MEDIUM	按6.3宽体Volante外廓映射；输入功率与公开版本存在差异。	READY
8199	8199	Coupe	V8 Vantage V550		2	EU-ASTON-MARTIN-V8-VANTAGE-V550-COUPE-01	HIGH		READY
8200	8200	Coupe	Virage Limited Edition		2		LOW	输入功率与公开Limited Edition规格不一致，且高度资料未闭合。	PENDING: Limited Edition具体版本与完整三维未确认
8202	8202	Convertible	DB7		2		LOW	DB7 Volante公开来源对长度和高度存在配置口径冲突。	PENDING: DB7 Volante同一配置三维冲突未解决
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-USA-MUSTANG-IV-SN95-COUPE-PREFL-01	4610	1824	1344	Automobile-Catalog 1994 Ford Mustang Coupe 3.8L V6	https://www.automobile-catalog.com/car/1994/885155/ford_mustang_coupe_3_8l_v-6.html
EU-FORD-USA-MUSTANG-IV-SN95-COUPE-FACELIFT-01	4653	1857	1349	Automobile-Catalog 1999 Ford Mustang Coupe 3.8L V6	https://www.automobile-catalog.com/car/1999/885845/ford_mustang_coupe_3_8l_v-6.html
EU-FORD-USA-MUSTANG-IV-SN95-CONVERTIBLE-PREFL-01	4610	1824	1351	Automobile-Catalog 1995 Ford Mustang Convertible 3.8L V6	https://www.automobile-catalog.com/car/1995/885320/ford_mustang_convertible_3_8l_v-6_automatic.html
EU-FORD-USA-MUSTANG-IV-SN95-CONVERTIBLE-FACELIFT-01	4653	1857	1351	Automobile-Catalog 1999 Ford Mustang Convertible 3.8L V6	https://www.automobile-catalog.com/car/1999/885830/ford_mustang_convertible_3_8l_v-6_automatic.html
EU-FORD-USA-TAURUS-III-DN101-SEDAN-01	5016	1854	1400	Automobile-Catalog 1996 Ford Taurus GL Sedan 3.0L V6	https://www.automobile-catalog.com/car/1996/886730/ford_taurus_gl_sedan_3_0l_v-6.html
EU-FORD-USA-TAURUS-III-DN101-WAGON-01	5070	1854	1463	Automobile-Catalog 1996 Ford Taurus LX Wagon 3.0L 24V V6	https://www.automobile-catalog.com/car/1996/886775/ford_taurus_lx_wagon_3_0l_24v_v-6.html
EU-KTM-X-BOW-R-CONVERTIBLE-01	3738	1915	1202	KTM X-BOW R global brochure	https://www.simplysportscars.com/wp-content/uploads/2021/05/KTM-X-BOW-R-Brochure-Global-Version.pdf
EU-FORD-FOCUS-III-DYB-HATCHBACK-PREFL-01	4358	1823	1461	Ford Focus 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf
EU-FORD-FOCUS-III-DYB-HATCHBACK-FACELIFT-01	4360	1823	1469	Ford Focus 2015 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Focus-UK.pdf
EU-MAZDA-626-II-GC-HATCHBACK-5D-01	4430	1690	1365	Automobile-Catalog 1985 Mazda 626 2.0i GLX 5-door	https://www.automobile-catalog.com/car/1985/1626680/mazda_626_2_0i_glx_5-door_cat.html
EU-MAZDA-323-V-BA-HATCHBACK-3D-01	4035	1710	1405	Automobile-Catalog 1996 Mazda 323 C 1.5	https://www.automobile-catalog.com/car/1996/1659125/mazda_323_c_1_5.html
EU-FORD-FOCUS-III-DYB-WAGON-PREFL-01	4556	1823	1482	Ford Focus 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf
EU-FORD-FOCUS-III-DYB-WAGON-FACELIFT-01	4560	1823	1492	Ford Focus 2015 UK official brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Focus-UK.pdf
EU-AUDI-200-C3-WAGON-FACELIFT-01	4793	1814	1421	Automobile-Catalog 1989 Audi 200 Avant Turbo Quattro	https://www.automobile-catalog.com/car/1989/234110/audi_200_avant_turbo_quattro_cat.html
EU-VW-PASSAT-B1-TYPE33-WAGON-01	4265	1615	1360	Automobile-Catalog 1979 Volkswagen Passat Variant 1600 S	https://www.automobile-catalog.com/car/1979/42680/volkswagen_passat_variant_1600_s.html
EU-VAUXHALL-CHEVETTE-CC-HATCHBACK-3D-01	3945	1570	1308	Auto-Data Vauxhall Chevette CC 1300	https://www.auto-data.net/en/vauxhall-chevette-cc-1300-58hp-6068
EU-RENAULT-MEGANE-II-WAGON-01	4500	1777	1467	Automobile-Catalog 2003 Renault Megane Wagon Grandtour 1.6 16V	https://www.automobile-catalog.com/car/2003/2954030/renault_megane_wagon_grandtour_1_6_16v.html
EU-ASTON-MARTIN-DB6-VANTAGE-COUPE-01	4623	1676	1384	Automobile-Catalog 1966 Aston Martin DB6 Vantage	https://www.automobile-catalog.com/car/1966/34715/aston_martin_db6_vantage.html
EU-ASTON-MARTIN-DB6-VOLANTE-CONVERTIBLE-01	4623	1676	1359	Automobile-Catalog 1967 Aston Martin DB6 Volante	https://www.automobile-catalog.com/car/1967/74060/aston_martin_db6_volante.html
EU-ASTON-MARTIN-DBS-VANTAGE-COUPE-01	4585	1829	1327	Automobile-Catalog 1969 Aston Martin DBS Vantage	https://www.automobile-catalog.com/car/1969/74195/aston_martin_dbs_vantage.html
EU-ASTON-MARTIN-LAGONDA-I-SEDAN-01	5283	1816	1302	Aston Martin Lagonda official past models	https://www.astonmartin.com/en/models/past-models/lagonda
EU-ASTON-MARTIN-V8-ZAGATO-VANTAGE-COUPE-01	4390	1860	1295	Automobile-Catalog 1987 Aston Martin Vantage Zagato	https://www.automobile-catalog.com/car/1987/53795/aston_martin_vantage_zagato.html
EU-ASTON-MARTIN-V8-ZAGATO-VOLANTE-CONVERTIBLE-01	4480	1860	1300	Automobile-Catalog 1988 Aston Martin Volante Zagato	https://www.automobile-catalog.com/car/1988/54935/aston_martin_volante_zagato.html
EU-ASTON-MARTIN-VIRAGE-COUPE-01	4745	1856	1320	Automobile-Catalog 1989 Aston Martin Virage	https://www.automobile-catalog.com/car/1989/227630/aston_martin_virage.html
EU-ASTON-MARTIN-VIRAGE-VOLANTE-CONVERTIBLE-01	4745	1856	1320	Automobile-Catalog 1993 Aston Martin Virage Volante	https://www.automobile-catalog.com/car/1993/227795/aston_martin_virage_volante.html
EU-ASTON-MARTIN-VIRAGE-VOLANTE-6.3-CONVERTIBLE-01	4745	1905	1320	Automobile-Catalog 1992 Aston Martin Virage Volante 6.3	https://www.automobile-catalog.com/car/1992/228020/aston_martin_virage_volante_6_3.html
EU-ASTON-MARTIN-V8-VANTAGE-V550-COUPE-01	4745	1924	1330	Automobile-Catalog 1997 Aston Martin V8 Vantage	https://www.automobile-catalog.com/car/1997/228335/aston_martin_v8_vantage.html
```

## 下一步优先处理

1. 优先拆解 Ktype 8186–8189 的 Aston Martin V8 标准车身、Vantage 宽体及保险杠阶段。
2. 核对 Ktype 8194–8197 的 Virage Shooting Brake、Saloon 和 6.3 Works 改装外廓。
3. 闭合 Ktype 8038、8160、8169 的底盘代码、轴距和车顶配置。
4. 解决 Ktype 8200 的版本功率冲突及 Ktype 8202 的 DB7 Volante 三维来源冲突。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf "https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf"
[2]: https://www.auto-data.net/en/vauxhall-chevette-cc-1300-53hp-6067?utm_source=chatgpt.com "Vauxhall Chevette CC 1300 (53 Hp) /Hatchback 1975"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: 对话分支失败（已尝试 3 次）: 没有找到最后一条用户消息的【在新聊天中分支】入口


--- 脚本异常 ---
异常: ChatGPT 页面显示未登录


--- 发送 / checkpoint 续跑到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 对话分支 / Round 3 ---
触发原因：ChatGPT 对话长度上限
父对话：https://chatgpt.com/c/6a6c3880-67a8-83ee-a436-1c372fa60a6f
新分支：https://chatgpt.com/c/6a6efb33-4d48-83e8-ba11-81d7c64d1249

--- Round 3 / checkpoint 续跑 ---
### 1) 更新点

* 继续处理唯一阻塞项 `Ktype 131410 Caterham AeroSeven`。
* 已确认其为采用独立全覆盖碳纤维车身的 AeroSeven Concept；公开的厂商新闻稿规格页未提供可闭合的整车长、宽、高，不能直接套用普通 Seven 或 CSR 尺寸。([NetCarShow.com][1])
* 本轮未创建不可靠尺寸组，状态保持 `PENDING`。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅继续查找 `131410 Caterham AeroSeven` 可追溯且宽度口径明确的完整三维数据。
* 不重新核对其余 74 个既有尺寸组。

推进信号：CONTINUE

[1]: https://www.netcarshow.com/caterham/2013-aeroseven_concept/ "Caterham AeroSeven Concept (2013) - pictures, information & specs"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / checkpoint 续跑 ---
### 1) 更新点

* 排除 `3718×1876×1120 mm`：该组尺寸实际属于 **VUHL 05**，并非 Caterham AeroSeven，不能入表。([Automoli][1])
* AeroSeven 厂商新闻稿确认其采用更新后的 **Seven CSR 平台、全覆盖碳纤维车身**，但技术规格未公布整车长宽高，因此仍不能直接复用普通 Seven/CSR 尺寸组。([NetCarShow.com][2])
* `131410` 保持 `PENDING`，未创建推测尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	独立全覆盖碳纤维概念车外廓；已排除误配的VUHL 05尺寸，不能套用普通Seven或CSR尺寸组。	PENDING: 尚未找到可追溯的完整长宽高
```

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅查找 `131410 Caterham AeroSeven` 的馆藏测量记录、设计档案或可追溯实车三维。
* 不再重复检查普通新闻稿、CSR 平台尺寸或已排除的 VUHL 05 数据。

推进信号：CONTINUE

[1]: https://www.automoli.com/gb/vehicles/vuhl/05/05-5964/?utm_source=chatgpt.com "VUHL 05 - Vehicle specifications"
[2]: https://www.netcarshow.com/caterham/2013-aeroseven_concept/ "Caterham AeroSeven Concept (2013) - pictures, information & specs"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / checkpoint 续跑 ---
### 1) 更新点

* 已核对英国汽车博物馆的 `2013 Caterham AeroSeven` 官方馆藏记录；其 `Dimensions` 字段仅显示 `(l), (w), (h)`，没有任何数值。([英国汽车博物馆][1])
* Caterham 原始发布稿确认该车使用 Seven CSR 平台的更新解释，但采用全新碳纤维完整车身及新的翻滚结构，全文未公布整车长、宽、高，仍不能直接复用 CSR 外廓尺寸。([autoevolution][2])
* `131410` 继续保持 `PENDING`；本轮未创建推测尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	厂商发布稿及英国汽车博物馆馆藏记录均未公布完整长宽高；独立全覆盖碳纤维车身不能直接复用Seven CSR外廓尺寸。	PENDING: 尚缺可追溯的完整长宽高
```

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅继续寻找 `131410 Caterham AeroSeven` 的厂商设计档案或馆藏实物测量记录。
* 不重新核对其余 `74` 个既有尺寸组，也不以 CSR 平台尺寸推定概念车外廓。

推进信号：CONTINUE

[1]: https://www.britishmotormuseum.co.uk/online-collections/details-page?row_id=173385509735 "Online Collections - Details Page"
[2]: https://www.autoevolution.com/pdf/news_attachements/caterham-aeroseven-concept-officially-unveiled-videophoto-gallery-67354.pdf "Untitled"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / checkpoint 续跑 ---
### 1) 更新点

* 已用 AeroSeven 官方正侧面、俯视和正面媒体图，结合其 CSR 平台已确认的 `2305 mm` 轴距进行比例测算，得到约 `3440 × 1660 × 1110 mm` 的外廓参考值。AeroSeven 官方资料确认其采用更新的 CSR 平台及独立全覆盖碳纤维车身。([NetCarShow.com][1])
* 该结果属于图片比例测算，并非厂商公布值或馆藏实测值，暂不足以建立正式尺寸组；`131410` 继续保持 `PENDING`。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	官方正投影视图按CSR平台2305mm轴距缩放，外廓参考约3440×1660×1110mm；属于图片测算，尚未作为正式三维入库。	PENDING: 缺少可直接引用或实测的完整长宽高
```

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅查找英国汽车博物馆馆藏车辆的实物测量记录、Caterham 设计档案或型式认证资料，以确认 `131410` 的完整三维。
* 不重新核对其余 `74` 个既有尺寸组。

推进信号：CONTINUE

[1]: https://www.netcarshow.com/caterham/2013-aeroseven_concept/ "Caterham AeroSeven Concept (2013) - pictures, information & specs"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / checkpoint 续跑 ---
### 1) 更新点

* 找到 AeroSeven 的正投影蓝图及三维模型资料；页面声明依据官方参考和真实车辆尺寸制作，但公开页面未披露可直接引用的长、宽、高数值。([3DModels Store][1])
* Caterham 官方手册仅能确认 CSR 平台尺寸为 `3300 × 1685 × 1015 mm`（无顶篷高度）及 `2315 mm` 轴距；AeroSeven 采用独立全覆盖碳纤维车身，仍不足以直接把 CSR 外廓写入尺寸组。([Caterham Cars][2])
* `131410` 保持 `PENDING`，未创建推定尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	正投影蓝图及三维模型页面称依据真实尺寸制作，但公开页未披露数值；CSR官方尺寸仅作平台参考，不直接套用独立全覆盖车身。	PENDING: 尚缺可直接引用的完整长宽高
```

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅提取 AeroSeven 蓝图、三维模型元数据或馆藏测量档案中的数值化外廓。
* 不重新核对其余 `74` 个既有尺寸组。

推进信号：CONTINUE

[1]: https://3dmodels.org/blueprints/caterham-aeroseven-2013-vector/ "Caterham AeroSeven 2014 Vector Blueprint - 3DModels.org"
[2]: https://caterhamcars.com/assets/Documents/Owner-Downloads/Owners%20Handbook%20All%20Models_2024_ED1.4.pdf?utm_source=chatgpt.com "OWNERS HANDBOOK"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / checkpoint 续跑 ---
### 1) 更新点

* 找到 `h3dA71335` AeroSeven 三维模型及 `h3dA334787` 正投影蓝图记录；资料明确表示模型依据公开尺寸、蓝图依据官方参考和真实车辆尺寸制作，但公开页面仍未披露可直接引用的长、宽、高或模型包围盒数值。([3DModels Store][1])
* 现有资料仅进一步确认 AeroSeven 比 CSR 外廓更大，不能据此直接套用 CSR 的 `3300 × 1685 × 1015 mm`。([汽车选择][2])
* `131410` 继续保持 `PENDING`，本轮未创建推定尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	三维模型及正投影蓝图声明依据真实车辆尺寸制作，但公开页面未披露长宽高或模型包围盒；资料同时表明其外廓较CSR更大，不直接复用CSR尺寸。	PENDING: 尚缺可直接引用的完整长宽高
```

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅提取 `h3dA71335` 模型文件元数据、模型包围盒或原始正投影文件中的数值比例。
* 若仍无数值，转查 Caterham 原始媒体资产、设计档案和英国汽车博物馆馆藏测量附件；不重复核对其他 `74` 个尺寸组。

推进信号：CONTINUE

[1]: https://3dmodels.org/3d-models/caterham-aeroseven-2013/?utm_source=chatgpt.com "Caterham AeroSeven 2014 3D model - Download Sports car on 3DModels.org"
[2]: https://www.whichcar.com.au/news/caterham-aeroseven-concept-revealed?utm_source=chatgpt.com "Caterham AeroSeven concept revealed!"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / checkpoint 续跑 ---
### 1) 更新点

* 找到名为 `Caterham AeroSeven '13 specs.png` 的规格附件记录，但当前索引仅显示附件名称和文件大小，未暴露可核验的长、宽、高数值，暂不能据此创建尺寸组。([TdU Drive Time][1])
* 英国汽车博物馆确认馆藏该辆 `2013 Caterham AeroSeven`，但公开记录仍未提供数值化三维；现有蓝图和三维模型页面同样未公开尺寸或模型包围盒。([英国汽车博物馆][2])
* `131410` 继续保持 `PENDING`，本轮未创建推定尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅尝试提取 `Caterham AeroSeven '13 specs.png` 附件及博物馆馆藏附件中的数值化三维。
* 不重新核对其余 `74` 个尺寸组，不采用普通 CSR 或通用零件目录尺寸代替 AeroSeven 独立车身尺寸。

推进信号：CONTINUE

[1]: https://tdudrivetime.com/viewtopic.php?start=2380&t=374&utm_source=chatgpt.com "The Perfect Car List For a Game - Page 239 - Tdudrivetime"
[2]: https://www.britishmotormuseum.co.uk/online-collections?utm_source=chatgpt.com "Online Collections"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / checkpoint 续跑 ---
### 1) 更新点

* 核对 Caterham 原始技术规格转录页：规格仅包含动力、悬架、制动、轮胎等项目，未公布整车长、宽、高。([NetCarShow.com][1])
* Ultimatecarpage 的 AeroSeven 独立规格页在 `Dimensions` 下也仅列 `600 kg` 重量、轮圈和轮胎规格，没有外廓三维。([Ultimate Car Page][2])
* `131410` 仍无法建立字段完整且可追溯的尺寸组，继续保持 `PENDING`。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅继续查找 `131410 Caterham AeroSeven` 的馆藏实车测量、原始 CAD 包围盒或设计档案中的数值化完整三维。
* 不重新核对其余 `74` 个既有尺寸组，不以 CSR 平台尺寸代替 AeroSeven 独立车身外廓。

推进信号：CONTINUE

[1]: https://www.netcarshow.com/caterham/2013-aeroseven_concept/?utm_source=chatgpt.com "Caterham AeroSeven Concept (2013) - pictures, information & specs"
[2]: https://www.ultimatecarpage.com/spec/5675/Caterham-AeroSeven-Concept.html?utm_source=chatgpt.com "2014 Caterham AeroSeven Concept Specifications - Ultimatecarpage.com"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / checkpoint 续跑 ---
### 1) 更新点

* 已继续核对 AeroSeven 专用规格附件、独立车型数据库及正投影资料。
* `Caterham AeroSeven '13 specs.png` 附件记录可以确认存在，但当前公开索引未暴露附件内的数值内容。([TDU Drive Time][1])
* 3DModels 的 AeroSeven 正投影明确说明依据官方参考及真实车辆尺寸制作，但公开页面仍未列出可直接引用的长、宽、高。([3DModels Store][2])
* Automobile-Catalog、Carfolio 等本轮检索结果仅返回普通 Seven、宽体 Seven 或 CSR 相关车型，没有 AeroSeven 独立外廓三维，不能替代。([汽车目录][3])
* `131410` 继续保持 `PENDING`，未建立推定尺寸组。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 已研究 Ktype：`100/100`
* READY Ktype：`99`
* PENDING Ktype：`1`
* READY 映射行：`119`
* PENDING 映射行：`1`
* DIMENSION_GROUP：`74`
* 剩余阻塞：`131410`

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 仅继续提取 `Caterham AeroSeven '13 specs.png` 原始附件或网页存档中的数值。
* 若附件仍不可读取，则查找 AeroSeven CAD/三维模型包围盒元数据；不重新核对其他 `74` 个尺寸组。

推进信号：CONTINUE

[1]: https://tdudrivetime.com/viewtopic.php?start=2380&t=374&utm_source=chatgpt.com "The Perfect Car List For a Game - Page 239 - Tdudrivetime"
[2]: https://3dmodels.org/blueprints/caterham-aeroseven-2013-vector/ "Caterham AeroSeven 2014 Vector Blueprint - 3DModels.org"
[3]: https://www.automobile-catalog.com/car/2026/3172415/caterham_seven_600.html?utm_source=chatgpt.com "2026 Caterham Seven 170 Specs Review (62.6 kW / 85 PS / 84 hp) (for Europe )"


--- 发送 / 无数据收尾 / Round 12 ---
立即停止检索，直接输出当前已积累的两张最终完整 TSV（Ktype 映射 TSV 和 DIMENSION_GROUP TSV），保留仍有 PENDING 的条目原样输出，不要继续检索或补全。必须包含两个 sandbox 下载链接，并以"推进信号：COMPLETE"结束。


--- Round 12 / checkpoint 续跑 ---
已停止检索，并按当前**可精确恢复的数据**强制封存。需要说明：此前进度中提到的 `119` 条 READY 映射和 `74` 个尺寸组未作为完整表持久化到当前可访问文件，因此不能在不编造数据的情况下还原；以下保留目前能够原样恢复的 `PENDING` 条目。

## Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
131410	131410	Convertible	AeroSeven Concept	AE	2		LOW	三维模型及正投影蓝图声明依据真实车辆尺寸制作，但公开页面未披露长宽高或模型包围盒；资料同时表明其外廓较CSR更大，不直接复用CSR尺寸。	PENDING: 尚缺可直接引用的完整长宽高
```

## DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
```

## 下载文件

* [all_7501-7600_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/all_7501-7600_ktype_dimension_mapping_final.tsv)
* [all_7501-7600_dimension_groups_final.tsv](sandbox:/mnt/data/all_7501-7600_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 发送 / 完成信号纠偏 / Round 13 ---
你刚才给了完成信号，但当前回复缺少完整 Ktype 映射 TSV、完整 DIMENSION_GROUP TSV，存在未引用/缺失/不完整的尺寸组，或仍有数据缺失。请补齐所有必需表；未完成时输出“推进信号：CONTINUE”，确认全部表完整且映射闭合后才输出“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / checkpoint 续跑 ---
### 1) 更新点

* 撤销上一轮错误的 `COMPLETE` 判定。
* 已检查当前 sandbox、文件库、Google Drive 及相关 GitHub 仓库，仅能精确恢复 `131410` 这一条 PENDING 映射；此前累计的 `119` 条 READY 映射正文和 `74` 个 DIMENSION_GROUP 正文均未找到可用检查点。
* 现有两个 `final.tsv` 文件分别只有 `1` 条映射和 `0` 个尺寸组，不能视为最终完整表。
* 在缺少原始行正文的情况下不能推测或重新编造。每个 Ktype 和尺寸组都必须有完整、真实的数据才能入库。

### 2) 当前批次进度

* 输入 Ktype：`100`
* 历史检查点记录：

  * READY Ktype：`99`
  * PENDING Ktype：`1`
  * READY 映射行：`119`
  * PENDING 映射行：`1`
  * DIMENSION_GROUP：`74`
* 当前可精确恢复：

  * Ktype 映射：`1/120`
  * DIMENSION_GROUP：`0/74`
* 唯一已恢复条目：`131410 Caterham AeroSeven`
* 当前表不完整、映射无法闭合，不满足 COMPLETE 条件。

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 恢复缺失的 `119` 条 READY 映射原文。
* 恢复缺失的 `74` 个 DIMENSION_GROUP 原文及对应来源 URL。
* 恢复完成后仅执行一次机械校验：固定表头、唯一性、引用闭合、三维及来源非空、文件名与下载链接准确。

推进信号：CONTINUE


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / checkpoint 续跑 ---
### 1) 更新点

* 已完成当前会话、sandbox、文件库及连接存储中的缓存恢复检查。
* 未恢复到此前累计的 `119` 条 READY 映射正文和 `74` 个 DIMENSION_GROUP 正文；当前只能精确恢复 `131410 Caterham AeroSeven` 的 PENDING 映射。
* 无法确认的 Ktype 必须保留 PENDING、不得填写临时尺寸组 ID，因此本轮不伪造缺失数据。

### 2) 当前批次进度

* 批次：`all 第 7501-7600 行`
* 历史检查点：

  * 已研究 Ktype：`100/100`
  * READY Ktype：`99`
  * PENDING Ktype：`1`
  * READY 映射行：`119`
  * PENDING 映射行：`1`
  * DIMENSION_GROUP：`74`
* 当前可精确恢复：

  * Ktype 映射：`1/120`
  * DIMENSION_GROUP：`0/74`
* 剩余 PENDING：`131410`
* 当前完整表缺失，映射引用无法校验闭合。

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 优先恢复缺失的 `119` 条 READY 映射和 `74` 个 DIMENSION_GROUP 原始正文。
* 恢复后核对尺寸组引用闭合，再继续处理唯一 PENDING 项 `131410 Caterham AeroSeven`。
* 在两张完整表恢复并通过唯一性、引用闭合及字段完整校验前，不生成最终下载文件。

推进信号：CONTINUE


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7501-7600_ktype_dimension_mapping_final.tsv
- all_7501-7600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / checkpoint 续跑 ---
### 1) 更新点

* 已恢复一份包含 `39` 条 `DIMENSION_GROUP_ID + 长宽高` 的跨批次缓存索引。
* 该索引缺少 `DimensionSource`、`SourceURL`，且未包含 Ktype 映射关系，暂不能写入固定六字段的正式 DIMENSION_GROUP 表。
* 未恢复其余 READY 映射正文；本轮不编造缺失字段、不生成不完整尺寸组。

### 2) 当前批次进度

* 历史检查点：

  * 输入 Ktype：`100/100`
  * READY Ktype：`99`
  * PENDING Ktype：`1`
  * READY 映射行：`119`
  * PENDING 映射行：`1`
  * DIMENSION_GROUP：`74`
* 当前精确恢复状态：

  * 完整 Ktype 映射：`1/120`
  * 完整六字段 DIMENSION_GROUP：`0/74`
  * 部分恢复尺寸索引：`39` 条，仅有 ID 和三维
* 剩余 PENDING：`131410 Caterham AeroSeven`
* 当前两张表仍不完整，无法执行引用闭合校验。

### 3) 本轮新增/修改的 Ktype 映射 TSV

无

### 4) 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

### 5) 下一步优先处理

* 优先恢复 `119` 条 READY 映射原文及其引用关系。
* 为已恢复的 `39` 条尺寸索引补回原有 `DimensionSource` 和 `SourceURL`，并继续恢复剩余 `35` 个尺寸组。
* 完整表恢复后，再处理唯一 PENDING 项 `131410`；在映射闭合和尺寸组字段完整前不得 COMPLETE。

推进信号：CONTINUE

