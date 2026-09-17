# 任务：all 第 501-600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0006__92f48c96


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 501-600 行

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
all 第 501-600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ASTON-MARTIN-VANTAGE-VH2-GT8-COUPE-01	4540	1915	1250
EU-ASTON-MARTIN-VANTAGE-VH2-ROADSTER-01	4380	1865	1265
EU-AUDI-A3-8V-FACELIFT-CONVERTIBLE-01	4423	1793	1409
EU-AUDI-A3-8V-FACELIFT-HATCHBACK-3D-01	4241	1777	1424
EU-AUDI-A3-8V-FACELIFT-SEDAN-01	4458	1796	1416
EU-AUDI-A3-8V-FACELIFT-SPORTBACK-5D-01	4313	1785	1426
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425
EU-AUDI-A3-8Y-SPORTBACK-5D-01	4343	1816	1449
EU-AUDI-A4-B9-ALLROAD-WAGON-01	4750	1842	1493
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-SEDAN-PREFL-01	4726	1842	1427
EU-AUDI-Q3-8U-FACELIFT-SUV-01	4388	1831	1608
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655
EU-AUDI-Q5-II-FY-PHEV-SUV-01	4682	1893	1652
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635
EU-AUDI-Q5-II-FY-SQ5-SUV-02	4682	1893	1635
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-AUDI-Q5-II-FY-SUV-02	4682	1893	1662
EU-BMW-2-F22-COUPE-01	4432	1774	1418
EU-BMW-2-F22-COUPE-M240-01	4454	1774	1408
EU-BMW-2-F23-CONVERTIBLE-01	4432	1774	1413
EU-BMW-2-F23-CONVERTIBLE-M240-01	4454	1774	1403
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1608
EU-BMW-2-G42-COUPE-01	4537	1838	1390
EU-BMW-4-F32-COUPE-01	4638	1825	1377
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384
EU-BMW-4-F82-COUPE-M4-CS-01	4672	1870	1392
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534
EU-DACIA-SANDERO-II-FACELIFT-HATCHBACK-01	4057	1733	1523
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470
EU-HYUNDAI-I30-III-PD-HATCHBACK-5D-01	4340	1795	1455
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465
EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	4084	1802	1129
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710
EU-NISSAN-X-TRAIL-III-T32-SUV-PREFL-01	4640	1820	1715
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-01	4609	1920	1910
EU-PEUGEOT-EXPERT-III-VAN-COMPACT-HIGH-01	4609	1920	1950
EU-PEUGEOT-EXPERT-III-VAN-LONG-HIGH-01	5309	1920	1940
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-01	4959	1920	1899
EU-PEUGEOT-EXPERT-III-VAN-STANDARD-HIGH-01	4959	1920	1940
EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	4606	1859	1482
EU-RENAULT-TRAFIC-III-X82-PLATFORM-CAB-L2-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H1-01	4999	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L1H2-01	4999	1956	2465
EU-RENAULT-TRAFIC-III-X82-VAN-L2H1-01	5399	1956	1971
EU-RENAULT-TRAFIC-III-X82-VAN-L2H2-01	5399	1956	2465
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1800	1442
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1800	1456
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1448
EU-SKODA-KAROQ-I-NU7-SUV-AWD-01	4382	1841	1607
EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	4382	1841	1603
EU-SKODA-KODIAQ-I-NS7-SUV-PREFL-01	4697	1882	1676
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445
EU-TESLA-MODEL-X-I-SUV-01	5036	1999	1684
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450
EU-VW-ARTEON-I-3H-LIFTBACK-R-01	4866	1871	1460
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	4866	1871	1450
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-R-01	4866	1871	1462
EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	4639	1795	1510
EU-VW-GOLF-VIII-HATCHBACK-GTD-01	4287	1789	1478
EU-VW-GOLF-VIII-HATCHBACK-GTE-01	4287	1789	1484
EU-VW-GOLF-VIII-VARIANT-WAGON-01	4633	1789	1498
EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	4426	1809	1703
EU-VW-TIGUAN-I-5N-SUV-PREFL-01	4427	1809	1686
EU-VW-TIGUAN-II-AD1-SUV-4MOTION-PREFL-01	4486	1839	1673
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	4509	1839	1684
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-FWD-01	4509	1839	1675
EU-VW-TIGUAN-II-AD1-SUV-FWD-PREFL-01	4486	1839	1654

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Rover	2000-3500	2600	Schrägheck	Heckantrieb	Benzin	95	129	Oct 1980	Oct 1986	2024-03-01	144663
Porsche	Cayenne	4.0 Turbo GT AWD	SUV	Allrad	Benzin	471	640	Oct 2020	May 2023	2026-03-01	144667
Seat	Leon	1.5 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	96	131	May 2021	-	2024-03-01	144672
Ford	Transit v363	2.0 Ecoblue	Pritsche/Fahrgestell	Frontantrieb	Diesel	118	160	Jan 2021	-	2024-03-01	144673
Ford	Transit v363	2.0 Ecoblue	Kasten	Frontantrieb	Diesel	118	160	Jan 2021	-	2024-03-01	144674
BMW	Ix	Xdrive 40	SUV	Allrad	Elektro	240	326	Jul 2021	-	2024-03-01	144686
BMW	Ix	Xdrive 50	SUV	Allrad	Elektro	385	523	Jul 2021	-	2024-03-01	144687
BMW	4	I4 Edrive40	Coupe	Heckantrieb	Elektro	250	340	Nov 2021	-	2025-12-01	144688
BMW	4	I4 M50 Xdrive	Coupe	Allrad	Elektro	400	544	Nov 2021	-	2025-12-01	144689
BMW	4	420 I	Coupe	Heckantrieb	Benzin	135	184	Jul 2021	-	2024-03-01	144692
BMW	4	430 I	Coupe	Heckantrieb	Benzin	180	245	Jul 2021	-	2024-03-01	144693
BMW	4	M440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	275	374	Jul 2021	-	2024-03-01	144694
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	140	190	Jul 2021	-	2024-03-01	144695
BMW	4	420 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	140	190	Jul 2021	-	2024-03-01	144696
BMW	2	220 I	Coupe	Heckantrieb	Benzin	135	184	Aug 2021	-	2024-03-01	144697
BMW	2	M240 I Xdrive	Coupe	Allrad	Benzin	275	374	Aug 2021	-	2024-03-01	144698
BMW	2	220 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	140	190	Aug 2021	-	2024-03-01	144700
BMW	4	420 I Xdrive	Coupe	Allrad	Benzin	135	184	Jul 2021	-	2024-03-01	144723
BMW	4	M 440 I Mild-hybrid	Coupe	Heckantrieb	Benzin/Elektro	275	374	Jul 2021	-	2024-03-01	144724
Tesla	Model s	EV AWD	Schrägheck	Allrad	Elektro	493	670	Jan 2021	Apr 2026	2026-06-01	144729
Tesla	Model s	Plaid AWD	Schrägheck	Allrad	Elektro	750	1020	Jan 2021	Apr 2026	2026-06-01	144730
Tesla	Model x	EV AWD	Schrägheck	Allrad	Elektro	493	670	Jan 2021	Apr 2026	2026-06-01	144731
Tesla	Model x	Plaid AWD	Schrägheck	Allrad	Elektro	750	1020	Jan 2021	Apr 2026	2026-06-01	144732
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	124	169	Mar 2021	-	2024-03-01	144737
Skoda	Karoq	2.0 TDI	SUV	Frontantrieb	Diesel	85	116	Nov 2020	-	2024-03-01	144747
Peugeot	5008	1.6 Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Nov 2014	Mar 2017	2026-04-01	144752
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	147	200	Jun 2020	-	2024-03-01	144761
Aston Martin	Vantage	V8	Coupe	Heckantrieb	Benzin	393	534	Mar 2021	-	2024-03-01	144783
Aston Martin	Vantage	V8	Cabriolet	Heckantrieb	Benzin	393	534	Mar 2021	-	2024-03-01	144784
Ferrari	Sf90	Spider Phev 4WD	Cabriolet	Allrad	Benzin/Elektro	735	999	Mar 2021	-	2026-04-01	144791
VW	Arteon	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Sep 2020	Jun 2021	2025-12-01	144801
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	180	245	Sep 2020	-	2024-03-01	144806
VW	Passat alltrack b8 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	147	200	Aug 2020	Mar 2024	2025-02-03	144807
Fiat	Ducato	120 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	88	120	Jul 2021	-	2024-03-01	144808
Fiat	Ducato	140 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	103	140	Jul 2021	-	2024-03-01	144809
Fiat	Ducato	160 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	118	160	Jul 2021	Oct 2023	2024-05-01	144810
Fiat	Ducato	180 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	132	180	Jul 2021	-	2025-06-01	144812
Tesla	Model y	EV	SUV	Heckantrieb	Elektro	220	299	Jul 2021	Jan 2025	2026-03-01	144817
Tesla	Model y	EV Allrad	SUV	Allrad	Elektro	331	450	Jul 2021	Jan 2025	2026-03-01	144818
Mercedes-benz	S-Klasse	S 580 E	Stufenheck	Heckantrieb	Benzin/Elektro	375	510	Jul 2021	-	2024-03-01	144824
Mercedes-benz	S-Klasse	S 580 E	Stufenheck	Heckantrieb	Benzin/Elektro	375	510	Jul 2021	-	2024-03-01	144826
Polestar	Polestar 2	EV	Schrägheck	Frontantrieb	Elektro	165	224	Apr 2021	Dec 2022	2024-03-01	144835
Skoda	Octavia	1.4 TSI	Kombi	Frontantrieb	Benzin	110	150	Jun 2020	-	2024-03-01	144843
Zeekr	1	EV	Schrägheck	Heckantrieb	Elektro	200	272	Apr 2021	-	2024-05-01	144844
Zeekr	1	EV Allrad	Schrägheck	Allrad	Elektro	400	544	Apr 2021	-	2024-05-01	144846
VW	Id.4	Pure Performance	SUV	Heckantrieb	Elektro	125	170	Jan 2021	-	2024-03-01	144856
Peugeot	Expert	2.0 Bluehdi 145	Bus	Frontantrieb	Diesel	106	144	Jul 2021	Apr 2025	2025-12-01	144861
VW	Id.3	PRO	Schrägheck	Heckantrieb	Elektro	107	145	Nov 2020	-	2024-03-01	144862
Peugeot	Expert	E-expert	Bus	Frontantrieb	Elektro	100	136	Sep 2020	Oct 2023	2024-07-01	144863
VW	Id.4	Pure	SUV	Heckantrieb	Elektro	109	148	Jan 2021	-	2024-03-01	144864
VW	Golf viii variant	1.5 TGI	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Sep 2020	-	2024-03-01	144886
VW	Id.4	GTX	SUV	Allrad	Elektro	220	299	May 2021	-	2024-03-01	144887
Hyundai	Tucson	1.6 T-gdi	SUV	Frontantrieb	Benzin	132	179	Jul 2021	-	2026-01-01	144888
Renault	Arkana i	1.3 TCE 140	SUV	Frontantrieb	Benzin/Elektro	103	140	Sep 2020	-	2024-03-01	144894
Renault	Arkana i	1.3 TCE 160	SUV	Frontantrieb	Benzin/Elektro	116	158	Mar 2021	-	2024-03-01	144895
Renault	Arkana i	1.6 E-tech 145	SUV	Frontantrieb	Benzin/Elektro	105	143	Mar 2021	-	2024-03-01	144896
Genesis	G80	2.2 Crdi AWD	Stufenheck	Allrad	Diesel	154	209	Jun 2021	-	2025-06-01	144901
Renault	Trafic iii	2.0 DCI 150	Bus	Frontantrieb	Diesel	110	150	May 2021	-	2024-03-01	144927
Skoda	Octavia	2.0 TDI 4X4	Schrägheck	Allrad	Diesel	110	150	Sep 2020	-	2024-03-01	144928
Audi	A3	40 Tfsi Quattro	Stufenheck	Allrad	Benzin	140	190	Jul 2021	-	2024-03-01	144929
Audi	A3	40 Tfsi Quattro	Schrägheck	Allrad	Benzin	140	190	Jul 2021	-	2024-03-01	144930
Audi	A3	45 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Jul 2021	-	2024-03-01	144931
Audi	A4 b9	S4 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	251	341	Jan 2021	-	2024-03-01	144932
Audi	Q3	45 Tfsi E	SUV	Frontantrieb	Benzin/Elektro	180	245	Nov 2020	-	2024-03-01	144934
Audi	Q3	45 Tfsi E	SUV	Frontantrieb	Benzin/Elektro	180	245	Nov 2020	-	2024-03-01	144935
Genesis	Gv70	2.5 AWD	SUV	Allrad	Benzin	224	304	Apr 2021	-	2024-03-01	144941
Genesis	Gv70	2.2 AWD	SUV	Allrad	Diesel	154	209	Apr 2021	-	2025-06-01	144942
Nissan	Nv300 kombi	2.0 DCI 110	Bus	Frontantrieb	Diesel	81	110	May 2021	-	2024-03-01	144946
Nissan	Nv300 kombi	2.0 DCI 150	Bus	Frontantrieb	Diesel	110	150	May 2021	-	2024-03-01	144947
Volvo	Xc60 ii	B4 Mild-hybrid	SUV	Frontantrieb	Diesel/Elektro	145	197	May 2019	-	2024-03-01	144949
VW	Golf viii	1.4 TSI	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2021	-	2024-05-01	144993
Land Rover	Defender station wagon	P525 4X4	Geländewagen geschlossen	Allrad	Benzin	386	525	May 2021	-	2024-03-01	144996
Hyundai	I30	2.0 N	Schrägheck	Frontantrieb	Benzin	206	280	Mar 2021	-	2024-03-01	145004
Cupra	Leon	2.0 TSI	Schrägheck	Frontantrieb	Benzin	180	245	Jun 2021	-	2024-03-01	145008
Cupra	Leon	2.0 TSI VZ	Schrägheck	Frontantrieb	Benzin	221	300	Jan 2021	-	2025-12-01	145009
Cupra	Leon	2.0 TSI	Kombi	Frontantrieb	Benzin	180	245	Jun 2021	-	2024-03-01	145010
Cupra	Leon	2.0 TSI	Kombi	Frontantrieb	Benzin	221	300	Jun 2021	-	2024-03-01	145011
Cupra	Leon	2.0 TSI 4drive	Kombi	Allrad	Benzin	228	310	Jun 2021	-	2024-03-01	145012
Skoda	Octavia	2.0 TSI 4X4	Schrägheck	Allrad	Benzin	140	190	Jul 2020	-	2024-03-01	145013
Skoda	Kodiaq i	2.0 RS 4X4	SUV	Allrad	Benzin	180	245	Jun 2021	-	2024-05-01	145016
Skoda	Fabia iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2021	-	2024-03-01	145017
Skoda	Fabia iv	1.0 TSI	Schrägheck	Frontantrieb	Benzin	70	95	Jun 2021	-	2024-03-01	145018
Skoda	Fabia iv	1.0 MPI	Schrägheck	Frontantrieb	Benzin	59	80	Jun 2021	-	2024-03-01	145019
Audi	Q5	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	270	367	Jun 2021	-	2024-03-01	145020
Dacia	Sandero	1.0 SCE 65	Schrägheck	Frontantrieb	Benzin	49	67	Jan 2021	-	2024-03-01	145025
Dacia	Sandero	1.0 TCE 100	Schrägheck	Frontantrieb	Benzin	74	101	Jan 2021	-	2024-03-01	145026
Dacia	Sandero	1.0 TCE 100 Eco-g	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jan 2021	-	2024-03-01	145027
Dacia	Sandero	1.0 TCE 90	Schrägheck	Frontantrieb	Benzin	67	91	Jan 2021	-	2024-03-01	145028
Dacia	Sandero	1.0 TCE LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	67	91	Jan 2021	-	2025-06-01	145029
Maserati	Mc 20	3	Coupe	Heckantrieb	Benzin	463	630	Sep 2020	-	2024-03-01	145033
VW	Golf viii	2.0 TSI	Schrägheck	Frontantrieb	Benzin	140	190	Jun 2021	Nov 2024	2025-12-01	145034
VW	Golf viii	2.0 TSI 4motion	Schrägheck	Allrad	Benzin	140	190	Jun 2021	Nov 2024	2025-12-01	145035
VW	Golf viii variant	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Jun 2021	Nov 2024	2025-06-01	145036
Lotus	Exige	3.5 390	Coupe	Heckantrieb	Benzin	296	402	Mar 2021	-	2024-03-01	145037
VW	Golf viii variant	2.0 TSI 4motion	Kombi	Allrad	Benzin	140	190	Jun 2021	Nov 2024	2025-06-01	145038
Lotus	Exige	3.5 420	Coupe	Heckantrieb	Benzin	313	426	Nov 2017	-	2024-03-01	145039
Renault	Trafic iii	2.0 DCI 110	Bus	Frontantrieb	Diesel	81	110	May 2021	-	2024-03-01	145045
Nissan	X-Trail iii	1.3 Dig-t	SUV	Frontantrieb	Benzin	116	158	Jun 2021	-	2024-03-01	145046
VW	Taigo	1.0 TSI	SUV	Frontantrieb	Benzin	70	95	Sep 2021	-	2024-03-01	145048
VW	Taigo	1.0 TSI	SUV	Frontantrieb	Benzin	81	110	Sep 2021	Mar 2024	2025-06-01	145049


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类闭合 Porsche Cayenne Turbo GT、BMW i4/G26、BMW 4 Series G22、Tesla Model S/X 2021 改款以及 Mercedes-Benz W223/V223 等尺寸组；宽度统一采用来源中不含外后视镜的车身宽度。([汽车数据网][1])
* ID.4 Pure 与 GTX 因长度和高度不同分别建组；同时闭合 Tucson IV、Kodiaq RS facelift、Fabia IV、Sandero III、Taigo 等外廓。([汽车数据网][2])
* `144672` 已按标准悬架和 FR 低悬架拆成两个物理分支，不再保留无后缀基础行。
* 本轮直接复用 16 个跨批次既有尺寸组；复用组不在本轮 DIMENSION_GROUP 增量表中重复输出。
* Ford Transit、Fiat Ducato、Peugeot Expert、Renault Trafic/Nissan NV300 等商用车仍需闭合轴距、车长和车顶派生分支，暂不猜测关联。

## 当前批次进度

* READY 映射：65 行，覆盖 64 个输入 Ktype。
* PENDING 映射：36 行，覆盖 36 个输入 Ktype。
* 已确认尺寸组：40 个。
* 本轮新建尺寸组：24 个。
* 跨批次复用尺寸组：16 个。
* 输入 Ktype 覆盖：100/100。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144663	144663	Hatchback	Rover SD1		5		LOW	SD1 2600车型边界已识别，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144667	144667	SUV	Cayenne III Coupe		5	EU-PORSCHE-CAYENNE-III-COUPE-TURBO-GT-SUV-01	HIGH		READY
144672_standard	144672	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架外廓分支。	READY
144672_fr	144672	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架外廓分支。	READY
144673	144673	Pickup	Transit V363	V363			LOW	底盘车覆盖多轴距/驾驶室外廓，分支尚未闭合。	PENDING: 多轴距/驾驶室分支未闭合
144674	144674	Van	Transit V363	V363			LOW	厢式车覆盖多车长与多车顶，L/H分支尚未闭合。	PENDING: 多车长/多车顶分支未闭合
144686	144686	SUV	iX I20	I20	5	EU-BMW-IX-I20-SUV-01	HIGH		READY
144687	144687	SUV	iX I20	I20	5	EU-BMW-IX-I20-SUV-01	HIGH		READY
144688	144688	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26五门Gran Coupé外廓。	READY
144689	144689	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26五门Gran Coupé外廓。	READY
144692	144692	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144693	144693	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144694	144694	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	HIGH	M440i xDrive外廓。	READY
144695	144695	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144696	144696	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144697	144697	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-01	HIGH		READY
144698	144698	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-M240I-XDRIVE-01	HIGH	M240i xDrive外廓。	READY
144700	144700	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-01	HIGH		READY
144723	144723	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144724	144724	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-M440I-RWD-01	HIGH	M440i后驱外廓。	READY
144729	144729	Hatchback	Model S facelift 2021		5	EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	HIGH		READY
144730	144730	Hatchback	Model S facelift 2021		5	EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	HIGH		READY
144731	144731	SUV	Model X facelift 2021		5	EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	HIGH		READY
144732	144732	SUV	Model X facelift 2021		5	EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	HIGH		READY
144737	144737	Wagon	Outback VI BT	BT	5		MEDIUM	来源给出1670–1675 mm高度范围，具体配置边界尚未闭合。	PENDING: 高度配置边界未闭合
144747	144747	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH		READY
144752	144752	MPV	5008 I Phase II		5	EU-PEUGEOT-5008-I-PHASE-II-MPV-01	HIGH		READY
144761	144761	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
144783	144783	Coupe	Vantage 2018 F1 Edition		2	EU-ASTON-MARTIN-VANTAGE-2018-F1-COUPE-01	HIGH	535 hp F1 Edition Coupé外廓。	READY
144784	144784	Convertible	Vantage Roadster 2018 F1 Edition		2	EU-ASTON-MARTIN-VANTAGE-2018-F1-ROADSTER-01	HIGH	535 hp F1 Edition Roadster外廓。	READY
144791	144791	Convertible	SF90 Spider	F173	2	EU-FERRARI-SF90-SPIDER-F173-CONVERTIBLE-01	HIGH		READY
144801	144801	Wagon	Arteon I Shooting Brake facelift	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	HIGH	同三维Shooting Brake外廓，复用既有组。	READY
144806	144806	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
144807	144807	Wagon	Passat B8 Alltrack facelift	3G5	5		MEDIUM	来源给出4780–4888 mm长度范围，标准量产长度边界待闭合。	PENDING: 长度口径范围未闭合
144808	144808	Van	Ducato III facelift 2021	X290			LOW	厢式车覆盖多车长与多车顶，L/H分支尚未闭合。	PENDING: 多车长/多车顶分支未闭合
144809	144809	Van	Ducato III facelift 2021	X290			LOW	厢式车覆盖多车长与多车顶，L/H分支尚未闭合。	PENDING: 多车长/多车顶分支未闭合
144810	144810	Van	Ducato III facelift 2021	X290			LOW	厢式车覆盖多车长与多车顶，L/H分支尚未闭合。	PENDING: 多车长/多车顶分支未闭合
144812	144812	Van	Ducato III facelift 2021	X290			LOW	厢式车覆盖多车长与多车顶，L/H分支尚未闭合。	PENDING: 多车长/多车顶分支未闭合
144817	144817	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-01	HIGH		READY
144818	144818	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-01	HIGH		READY
144824	144824	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-S580E-01	HIGH	标准轴距W223。	READY
144826	144826	Sedan	S-Class Long V223	V223	4	EU-MERCEDES-BENZ-S-CLASS-V223-LWB-SEDAN-S580E-01	HIGH	长轴距V223。	READY
144835	144835	Hatchback	Polestar 2 I		5	EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	HIGH		READY
144843	144843	Wagon	Octavia IV		5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
144844	144844	Hatchback	Zeekr 001 I		5	EU-ZEEKR-001-I-LIFTBACK-01	MEDIUM	早期车型外廓按001初代量产车闭合。	READY
144846	144846	Hatchback	Zeekr 001 I		5	EU-ZEEKR-001-I-LIFTBACK-01	MEDIUM	早期车型外廓按001初代量产车闭合。	READY
144856	144856	SUV	ID.4 I		5	EU-VW-ID4-I-SUV-PURE-01	HIGH		READY
144861	144861	MPV	Expert III Bus		5		LOW	Bus/Combi覆盖Compact、Standard、Long多车长，分支尚未闭合。	PENDING: 多车长分支未闭合
144862	144862	Hatchback	ID.3 I		5		MEDIUM	车型边界已确认，三维直接来源尚未落组。	PENDING: 三维直接来源未闭合
144863	144863	MPV	Expert III e-Bus		5		LOW	Bus/Combi覆盖Compact、Standard、Long多车长，分支尚未闭合。	PENDING: 多车长分支未闭合
144864	144864	SUV	ID.4 I		5	EU-VW-ID4-I-SUV-PURE-01	HIGH		READY
144886	144886	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
144887	144887	SUV	ID.4 GTX I		5	EU-VW-ID4-I-GTX-SUV-01	HIGH	GTX独立外廓高度。	READY
144888	144888	SUV	Tucson IV	NX4	5	EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	HIGH		READY
144894	144894	SUV	Arkana I		5		MEDIUM	车型代际已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144895	144895	SUV	Arkana I		5		MEDIUM	车型代际已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144896	144896	SUV	Arkana I		5		MEDIUM	车型代际已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144901	144901	Sedan	G80 II	RG3	4		MEDIUM	RG3车型边界已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144927	144927	MPV	Trafic III X82 facelift	X82			LOW	Bus覆盖L1/L2等车长分支，尚未闭合。	PENDING: 多车长分支未闭合
144928	144928	Hatchback	Octavia IV		5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
144929	144929	Sedan	A3 8Y	8Y	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
144930	144930	Hatchback	A3 8Y Sportback	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
144931	144931	Hatchback	A3 8Y Sportback	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
144932	144932	Sedan	A4 B9 facelift S4	B9	4		MEDIUM	S4改款外廓与标准A4组不可直接混用，三维待闭合。	PENDING: S4改款三维未闭合
144934	144934	SUV	Q3 II F3	F3	5		MEDIUM	PHEV高度与既有普通Q3组需独立核对。	PENDING: PHEV外廓三维未闭合
144935	144935	SUV	Q3 II F3	F3	5		MEDIUM	PHEV高度与既有普通Q3组需独立核对。	PENDING: PHEV外廓三维未闭合
144941	144941	SUV	GV70 I	JK1	5		MEDIUM	JK1车型边界已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144942	144942	SUV	GV70 I	JK1	5		MEDIUM	JK1车型边界已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
144946	144946	MPV	NV300 Kombi X82	X82			LOW	Kombi覆盖L1/L2等车长分支，尚未闭合。	PENDING: 多车长分支未闭合
144947	144947	MPV	NV300 Kombi X82	X82			LOW	Kombi覆盖L1/L2等车长分支，尚未闭合。	PENDING: 多车长分支未闭合
144949	144949	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
144993	144993	Hatchback	Golf VIII		5		MEDIUM	标准悬架外廓尚未与既有GTD/GTE组区分闭合。	PENDING: 标准外廓三维未闭合
144996	144996	SUV	Defender 110 L663	L663	5		MEDIUM	Ktype已确认Defender 110，含备胎长度与不含镜宽度待闭合。	PENDING: 三维口径未闭合
145004	145004	Hatchback	i30 III PD facelift N	PD	5		MEDIUM	N版前后包围外廓需独立闭合。	PENDING: N版外廓三维未闭合
145008	145008	Hatchback	Cupra Leon IV KL1	KL1	5		MEDIUM	Cupra保险杠外廓不能直接复用Seat组，三维待闭合。	PENDING: Cupra外廓三维未闭合
145009	145009	Hatchback	Cupra Leon IV KL1	KL1	5		MEDIUM	Cupra保险杠外廓不能直接复用Seat组，三维待闭合。	PENDING: Cupra外廓三维未闭合
145010	145010	Wagon	Cupra Leon Sportstourer KL8	KL8	5		MEDIUM	Cupra Sportstourer外廓不能直接复用Seat组，三维待闭合。	PENDING: Cupra外廓三维未闭合
145011	145011	Wagon	Cupra Leon Sportstourer KL8	KL8	5		MEDIUM	Cupra Sportstourer外廓不能直接复用Seat组，三维待闭合。	PENDING: Cupra外廓三维未闭合
145012	145012	Wagon	Cupra Leon Sportstourer KL8	KL8	5		MEDIUM	Cupra Sportstourer外廓不能直接复用Seat组，三维待闭合。	PENDING: Cupra外廓三维未闭合
145013	145013	Hatchback	Octavia IV		5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
145016	145016	SUV	Kodiaq I facelift 2021	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-RS-FACELIFT-01	HIGH	RS改款外廓。	READY
145017	145017	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145018	145018	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145019	145019	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145020	145020	SUV	Q5 II FY facelift PHEV	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH		READY
145025	145025	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145026	145026	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145027	145027	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145028	145028	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145029	145029	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145033	145033	Coupe	MC20 I	M240	2		MEDIUM	MC20车型边界已确认，三维直接来源尚未闭合。	PENDING: 三维直接来源未闭合
145034	145034	Hatchback	Golf VIII		5		MEDIUM	2.0 TSI前驱/4Motion高度外廓尚未闭合。	PENDING: 高度外廓未闭合
145035	145035	Hatchback	Golf VIII		5		MEDIUM	2.0 TSI前驱/4Motion高度外廓尚未闭合。	PENDING: 高度外廓未闭合
145036	145036	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
145037	145037	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	MEDIUM	Exige III固定车身外廓复用既有组。	READY
145038	145038	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
145039	145039	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	MEDIUM	Exige III固定车身外廓复用既有组。	READY
145045	145045	MPV	Trafic III X82 facelift	X82			LOW	Bus覆盖L1/L2等车长分支，尚未闭合。	PENDING: 多车长分支未闭合
145046	145046	SUV	X-Trail III T32 facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
145048	145048	SUV	Taigo I		5	EU-VW-TAIGO-I-SUV-01	HIGH		READY
145049	145049	SUV	Taigo I		5	EU-VW-TAIGO-I-SUV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-CAYENNE-III-COUPE-TURBO-GT-SUV-01	4942	1995	1636	Auto-Data Porsche Cayenne III Coupe Turbo GT	https://www.auto-data.net/en/porsche-cayenne-iii-coupe-turbo-gt-4.0-v8-640hp-tiptronic-s-43791
EU-BMW-IX-I20-SUV-01	4953	1967	1696	Auto-Data BMW iX I20 generation	https://www.auto-data.net/en/bmw-ix-i20-generation-8337
EU-BMW-I4-G26-GRAN-COUPE-01	4783	1852	1448	Auto-Data BMW i4 G26 eDrive40	https://www.auto-data.net/en/bmw-i4-g26-83.9-kwh-340hp-edrive40-43562
EU-BMW-4-G22-COUPE-STANDARD-01	4768	1852	1383	Auto-Data BMW 4 Series G22 420i	https://www.auto-data.net/en/bmw-4-series-coupe-g22-420i-184hp-steptronic-40261
EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	4770	1852	1393	Auto-Data BMW 4 Series G22 M440i xDrive	https://www.auto-data.net/en/bmw-4-series-coupe-g22-m440i-374hp-mild-hybrid-xdrive-steptronic-40263
EU-BMW-4-G22-COUPE-M440I-RWD-01	4768	1852	1386	Auto-Data BMW 4 Series G22 M440i RWD	https://www.auto-data.net/en/bmw-4-series-coupe-g22-m440i-374hp-mild-hybrid-steptronic-43476
EU-BMW-2-G42-COUPE-M240I-XDRIVE-01	4548	1838	1404	Auto-Data BMW 2 Series G42 M240i xDrive	https://www.auto-data.net/en/bmw-2-series-coupe-g42-m240i-374hp-xdrive-steptronic-sport-43835
EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	5021	1987	1431	Auto-Data Tesla Model S facelift 2021 Plaid	https://www.auto-data.net/en/tesla-model-s-facelift-2021-plaid-100-kwh-1020hp-tri-motor-awd-42385
EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	5057	1999	1680	Auto-Data Tesla Model X facelift 2021 Long Range	https://www.auto-data.net/en/tesla-model-x-facelift-2021-long-range-100-kwh-670hp-dual-motor-awd-42386
EU-PEUGEOT-5008-I-PHASE-II-MPV-01	4529	1888	1647	Auto-Data Peugeot 5008 I Phase II BlueHDi	https://www.auto-data.net/en/peugeot-5008-i-phase-ii-2013-1.6-bluehdi-120hp-20969
EU-ASTON-MARTIN-VANTAGE-2018-F1-COUPE-01	4490	1942	1274	Auto-Data Aston Martin Vantage F1 Edition Coupe	https://www.auto-data.net/en/aston-martin-v8-vantage-2018-f1-edition-4.0-v8-535hp-automatic-42548
EU-ASTON-MARTIN-VANTAGE-2018-F1-ROADSTER-01	4490	1942	1274	Auto-Data Aston Martin Vantage F1 Edition Roadster	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-2018-f1-edition-4.0-v8-535hp-automatic-42549
EU-FERRARI-SF90-SPIDER-F173-CONVERTIBLE-01	4704	1973	1191	Auto-Data Ferrari SF90 Spider	https://www.auto-data.net/en/ferrari-sf90-spider-4.0-v8-1000hp-plug-in-hybrid-awd-f1-41753
EU-TESLA-MODEL-Y-I-SUV-01	4751	1921	1624	Auto-Data Tesla Model Y Standard Range	https://www.auto-data.net/en/tesla-model-y-standard-range-60-kwh-299hp-54490
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-S580E-01	5179	1954	1503	Auto-Data Mercedes-Benz S-Class W223 S580e	https://www.auto-data.net/en/mercedes-benz-s-class-w223-s-580e-510hp-plug-in-hybrid-9g-tronic-44006
EU-MERCEDES-BENZ-S-CLASS-V223-LWB-SEDAN-S580E-01	5289	1954	1503	Auto-Data Mercedes-Benz S-Class Long V223 S580e	https://www.auto-data.net/en/mercedes-benz-s-class-long-v223-s-580e-510hp-plug-in-hybrid-9g-tronic-44007
EU-ZEEKR-001-I-LIFTBACK-01	4970	1999	1560	Auto-Data Zeekr 001	https://www.auto-data.net/en/zeekr-001-100-kwh-272hp-single-motor-electric-48808
EU-VW-ID4-I-SUV-PURE-01	4584	1852	1640	Auto-Data Volkswagen ID.4 Pure; Auto-Data Volkswagen ID.4 Pure Performance	https://www.auto-data.net/en/volkswagen-id.4-pure-55-kwh-149hp-43345;https://www.auto-data.net/en/volkswagen-id.4-pure-performance-55-kwh-170hp-45144
EU-VW-ID4-I-GTX-SUV-01	4582	1852	1637	Auto-Data Volkswagen ID.4 GTX	https://www.auto-data.net/en/volkswagen-id.4-gtx-82-kwh-299hp-4motion-43344
EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	4500	1865	1651	Auto-Data Hyundai Tucson IV 1.6 T-GDI 180 FWD	https://www.auto-data.net/en/hyundai-tucson-iv-1.6-t-gdi-180hp-mild-hybrid-42121
EU-SKODA-KODIAQ-I-NS7-SUV-RS-FACELIFT-01	4699	1882	1687	Auto-Data Skoda Kodiaq I facelift RS	https://www.auto-data.net/en/skoda-kodiaq-i-facelift-2021-rs-2.0-tsi-245hp-4x4-dsg-43763
EU-SKODA-FABIA-IV-HATCHBACK-01	4108	1780	1459	Auto-Data Skoda Fabia IV 1.0 TSI	https://www.auto-data.net/en/skoda-fabia-iv-1.0-tsi-110hp-43755
EU-DACIA-SANDERO-III-HATCHBACK-01	4088	1848	1499	Auto-Data Dacia Sandero III 1.0 TCe	https://www.auto-data.net/en/dacia-sandero-iii-1.0-tce-91hp-41829
EU-VW-TAIGO-I-SUV-01	4266	1757	1515	Auto-Data Volkswagen Taigo 1.0 TSI	https://www.auto-data.net/en/volkswagen-taigo-1.0-tsi-95hp-44420
```

## 下一步优先处理

1. 优先一次性闭合 Ford Transit V363、Fiat Ducato X290、Peugeot Expert Bus/e-Bus、Renault Trafic与Nissan NV300的轴距、车长和车顶派生分支。
2. 批量闭合 Arkana I、Genesis G80/GV70、Audi S4/Q3 PHEV、Cupra Leon、Golf VIII Hatchback、Defender 110、i30 N和Maserati MC20。
3. 解决 Subaru Outback 的高度范围、Passat Alltrack 的长度范围及 Rover SD1 的直接三维来源。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/porsche-cayenne-iii-coupe-turbo-gt-4.0-v8-640hp-tiptronic-s-43791 "https://www.auto-data.net/en/porsche-cayenne-iii-coupe-turbo-gt-4.0-v8-640hp-tiptronic-s-43791"
[2]: https://www.auto-data.net/en/volkswagen-id.4-pure-55-kwh-149hp-43345 "Volkswagen ID.4 Pure 55 kWh (149 Hp) | Technical specs, data, battery, electric range, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 24 个 Ktype；其中 Rover SD1 的生产区间跨越 Series 1 与 Series 2，已拆分为 `prefl`、`facelift` 两个物理外廓分支。([汽车目录][1])
* 已闭合 Outback、Passat Alltrack、ID.3、Arkana、Genesis G80/GV70、Audi S4/Q3 PHEV、Golf VIII、Defender 110、i30 N、Cupra Leon 和 MC20 等尺寸组。([斯巴鲁德国][2])
* 剩余 12 个 PENDING 均集中于 Transit、Ducato、Expert、Trafic 和 NV300 的多轴距、多车长或多车顶商用车分支。

## 当前批次进度

* READY 映射：90 行，覆盖 88 个输入 Ktype。
* PENDING 映射：12 行，覆盖 12 个输入 Ktype。
* 已确认尺寸组：56 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144663_prefl	144663	Hatchback	SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-01	MEDIUM	Series 1外廓分支。	READY
144663_facelift	144663	Hatchback	SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	MEDIUM	Series 2改款外廓分支。	READY
144737	144737	Wagon	Outback VI BT	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-01	HIGH		READY
144807	144807	Wagon	Passat B8 Alltrack facelift	3G5	5	EU-VW-PASSAT-B8-ALLTRACK-FACELIFT-WAGON-01	HIGH		READY
144862	144862	Hatchback	ID.3 I		5	EU-VW-ID3-I-HATCHBACK-01	HIGH		READY
144894	144894	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144895	144895	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144896	144896	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144901	144901	Sedan	G80 II	RG3	4	EU-GENESIS-G80-II-RG3-SEDAN-01	HIGH		READY
144932	144932	Sedan	S4 B9 facelift	B9	4	EU-AUDI-S4-B9-FACELIFT-SEDAN-01	HIGH		READY
144934	144934	SUV	Q3 II F3	F3	5	EU-AUDI-Q3-II-F3-PHEV-SUV-01	HIGH		READY
144935	144935	SUV	Q3 II F3	F3	5	EU-AUDI-Q3-II-F3-PHEV-SUV-01	HIGH		READY
144941	144941	SUV	GV70 I	JK1	5	EU-GENESIS-GV70-I-JK1-SUV-01	HIGH		READY
144942	144942	SUV	GV70 I	JK1	5	EU-GENESIS-GV70-I-JK1-SUV-01	HIGH		READY
144993	144993	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
144996	144996	SUV	Defender 110 L663	L663	5	EU-LAND-ROVER-DEFENDER-110-L663-P525-SUV-01	HIGH		READY
145004	145004	Hatchback	i30 III PD facelift N	PD	5	EU-HYUNDAI-I30-III-PD-FACELIFT-N-HATCHBACK-01	HIGH		READY
145008	145008	Hatchback	Cupra Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	HIGH		READY
145009	145009	Hatchback	Cupra Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	HIGH		READY
145010	145010	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145011	145011	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145012	145012	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145033	145033	Coupe	MC20 I	M240	2	EU-MASERATI-MC20-I-M240-COUPE-01	HIGH		READY
145034	145034	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
145035	145035	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ROVER-SD1-SERIES-1-HATCHBACK-01	4698	1768	1382	Automobile-Catalog Rover 2600 Series 1	https://www.automobile-catalog.com/car/1977/37475/rover_2600.html
EU-ROVER-SD1-SERIES-2-HATCHBACK-01	4698	1768	1384	Automobile-Catalog Rover 2600 Series 2	https://www.automobile-catalog.com/car/1986/2996870/rover_2600_vanden_plas.html
EU-SUBARU-OUTBACK-VI-BT-WAGON-01	4870	1875	1675	Subaru Deutschland Outback press specification	https://www.subaru-presse.de/pressemitteilungen/subaru-outback-neudefinition-des-crossovers-langfassung-modelljahr-2022-2
EU-VW-PASSAT-B8-ALLTRACK-FACELIFT-WAGON-01	4780	1853	1527	Auto-Data Passat Alltrack B8 facelift generation	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-facelift-2019-generation-7175
EU-VW-ID3-I-HATCHBACK-01	4261	1809	1568	Auto-Data Volkswagen ID.3 Pro 145	https://www.auto-data.net/en/volkswagen-id.3-pro-62-kwh-145hp-41700
EU-RENAULT-ARKANA-I-SUV-01	4568	1820	1576	Renault global media Arkana dimensions;Carstan Renault Arkana dimensions	https://media.renault.com/the-new-renault-arkana-more-nouvelle-vague-than-ever/?lang=eng;https://carstan.info/dimensions/renault/arkana/13-tce-140-hp-2740
EU-GENESIS-G80-II-RG3-SEDAN-01	4995	1925	1465	Auto-Data Genesis G80 II 2.2 AWD	https://www.auto-data.net/en/genesis-g80-ii-2.2-e-vgt-210hp-awd-automatic-41425
EU-AUDI-S4-B9-FACELIFT-SEDAN-01	4770	1847	1404	Auto-Data Audi S4 B9 facelift TDI	https://www.auto-data.net/en/audi-s4-b9-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47367
EU-AUDI-Q3-II-F3-PHEV-SUV-01	4485	1849	1574	Auto-Data Audi Q3 II F3 45 TFSI e	https://www.auto-data.net/en/audi-q3-ii-f3-45-tfsi-e-245hp-plug-in-hybrid-s-tronic-42115
EU-GENESIS-GV70-I-JK1-SUV-01	4715	1910	1630	Auto-Data Genesis GV70 2.5 AWD;Auto-Data Genesis GV70 2.2 AWD	https://www.auto-data.net/fr/genesis-gv70-2.5-t-gdi-304hp-awd-automatic-41921;https://www.auto-data.net/de/genesis-gv70-2.2-e-vgt-210hp-awd-automatic-41923
EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	4284	1789	1491	Auto-Data Volkswagen Golf VIII standard hatchback	https://www.auto-data.net/en/volkswagen-golf-viii-1.0-tsi-90hp-40806
EU-LAND-ROVER-DEFENDER-110-L663-P525-SUV-01	5018	1996	1967	Land Rover Defender official technical specification;Auto-Data Defender 110 P525	https://www.landrover.com/content/dam/lrdx/pdfs/no/brochures/Defender.pdf;https://www.auto-data.net/en/land-rover-defender-110-l663-5.0-v8-p525-525hp-awd-automatic-42462
EU-HYUNDAI-I30-III-PD-FACELIFT-N-HATCHBACK-01	4340	1795	1419	Auto-Data Hyundai i30 N Performance 280	https://www.auto-data.net/en/hyundai-i30-iii-facelift-2020-n-performance-2.0-t-gdi-280hp-dct-43366
EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	4398	1799	1442	Auto-Data Cupra Leon 245;Auto-Data Cupra Leon 300	https://www.auto-data.net/en/cupra-leon-2.0-tsi-245hp-dsg-45971;https://www.auto-data.net/en/cupra-leon-2.0-tsi-evo-300hp-dsg-42357
EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	4657	1799	1437	Auto-Data Cupra Leon Sportstourer 245;Auto-Data Cupra Leon Sportstourer 300;Auto-Data Cupra Leon Sportstourer 310 4Drive	https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-245hp-dsg-45972;https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-300hp-dsg-43840;https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-310hp-4drive-dsg-43391
EU-MASERATI-MC20-I-M240-COUPE-01	4669	1965	1221	Auto-Data Maserati MC20 3.0 V6	https://www.auto-data.net/en/maserati-mc20-3.0-v6-630hp-dct-41203
```

## 下一步优先处理

1. 一次性闭合 Ford Transit V363 底盘车和厢式车的轴距、车长、车顶及驾驶室派生分支。
2. 闭合 Fiat Ducato X290 的 L1–L4 与 H1–H3 厢式车分支，并批量关联四个 Ktype。
3. 统一处理 Peugeot Expert、Renault Trafic 和 Nissan NV300 的 Compact/L1/L2/Standard/Long 客运车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1977/37475/rover_2600.html?utm_source=chatgpt.com "1977 Rover 2600 Specs Review (101.4 kW / 138 PS / 136 hp) (since October 1977 for Europe )"
[2]: https://www.subaru-presse.de/pressemitteilungen/subaru-outback-neudefinition-des-crossovers-langfassung-modelljahr-2022-2 "Details - SUBARU Deutschland GmbH"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Peugeot Expert III Kombi 的 Standard L2 与 Long L3 两个外廓；BlueHDi 145 和 e-Expert 共用对应长度的尺寸组。2021 年 12 月车型表明确列出两种动力对应的可用长度，并给出不含后视镜宽度。
* 闭合 Renault Trafic III facelift Passenger 的 L1H1 与 L2H1 两个外廓；110 PS 和 150 PS Ktype 批量关联相同尺寸组。
* Nissan NV300 2021 Combi 的官方资料仅给出 `1935–2020 mm` 高度范围，无法落盘单一正整数，继续保留 PENDING。

## 当前批次进度

* READY 映射：98 行，覆盖 92 个输入 Ktype。
* PENDING 映射：8 行，覆盖 8 个输入 Ktype。
* 已确认尺寸组：60 个。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144861_standard	144861	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	HIGH	Standard L2乘用版外廓。	READY
144861_long	144861	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	HIGH	Long L3乘用版外廓。	READY
144863_standard	144863	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	HIGH	Standard L2乘用版外廓。	READY
144863_long	144863	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	HIGH	Long L3乘用版外廓。	READY
144927_swb	144927	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
144927_lwb	144927	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
145045_swb	145045	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
145045_lwb	145045	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	4956	1920	1890	PEUGEOT (e-) Expert Kombi official Austria price list December 2021	https://www.auto-guenther.at/fileadmin/media/download/Preislisten/Peugeot_Expert_Preisliste.pdf
EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	5308	1920	1890	PEUGEOT (e-) Expert Kombi official Austria price list December 2021	https://www.auto-guenther.at/fileadmin/media/download/Preislisten/Peugeot_Expert_Preisliste.pdf
EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	5080	1956	1973	Renault New Trafic Passenger official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20331-NewTraficPassengerBrochureApril2022.pdf
EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	5480	1956	1974	Renault New Trafic Passenger official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20331-NewTraficPassengerBrochureApril2022.pdf
```

## 下一步优先处理

1. 闭合 Fiat Ducato X290 的 L1–L4、H1–H3 可用组合，并批量处理四个 Ktype。
2. 闭合 Ford Transit V363 厢式车与底盘车的轴距、车顶和驾驶室分支。
3. 解决 Nissan NV300 Combi 的具体高度配置边界。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已首次闭合 Fiat Ducato III Series 8 厢式车的 8 个标准物理外廓：L1H1、L1H2、L2H1、L2H2、L3H2、L3H3、L4H2、L4H3。官方资料确认车身宽度统一为 2050 mm，并分别给出各车长和车顶高度。([菲亚特专业][1])
* `144808`、`144809`、`144810`、`144812` 已按上述 8 个尺寸组完整派生并批量关联，不再按发动机重复抓取尺寸。
* 剩余 PENDING 集中于 Ford Transit V363 的底盘车/厢式车分支，以及 Nissan NV300 Kombi 的高度配置边界。

## 当前批次进度

* READY 映射：130 行，覆盖 96 个输入 Ktype。
* PENDING 映射：4 行，覆盖 4 个输入 Ktype。
* 已确认尺寸组：68 个。
* 输入 Ktype 覆盖：100/100。
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144808_l1h1	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144808_l1h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144808_l2h1	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144808_l2h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144808_l3h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144808_l3h3	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144808_l4h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144808_l4h3	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144809_l1h1	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144809_l1h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144809_l2h1	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144809_l2h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144809_l3h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144809_l3h3	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144809_l4h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144809_l4h3	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144810_l1h1	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144810_l1h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144810_l2h1	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144810_l2h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144810_l3h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144810_l3h3	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144810_l4h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144810_l4h3	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144812_l1h1	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144812_l1h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144812_l2h1	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144812_l2h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144812_l3h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144812_l3h3	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144812_l4h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144812_l4h3	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	4963	2050	2254	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	4963	2050	2524	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	5413	2050	2254	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	5413	2050	2539	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	5998	2050	2534	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	5998	2050	2774	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	6363	2050	2539	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	6363	2050	2779	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
```

## 下一步优先处理

1. 闭合 `144673` Ford Transit V363 底盘车的单排/双排驾驶室及轴距外廓。
2. 闭合 `144674` Ford Transit V363 厢式车的 L2/L3/L4 与 H2/H3 分支。
3. 最后解决 `144946`、`144947` Nissan NV300 Kombi 的 L1H1/L2H1高度配置边界。

推进信号：CONTINUE

[1]: https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions?utm_source=chatgpt.com "DIMENSIONS"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 Ford Transit V363 底盘车、原厂平台及前驱厢式车分支，并完成 Nissan NV300 Kombi 的 L1H1、L2H1 分支；尺寸宽度统一为不含后视镜口径。([福特奥地利][1])
* 已完成轻量机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，映射引用全部闭合，长宽高及来源非空，两个指定下载文件已生成。

## 当前批次进度

* 输入 Ktype：100/100 已覆盖
* READY 映射：148 行
* PENDING 映射：0 行
* DIMENSION_GROUP：84 个
* 孤立尺寸组：0 个
* 当前批次已完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
144663_prefl	144663	Hatchback	SD1 Series 1	SD1	5	EU-ROVER-SD1-SERIES-1-HATCHBACK-01	MEDIUM	Series 1外廓分支。	READY
144663_facelift	144663	Hatchback	SD1 Series 2	SD1	5	EU-ROVER-SD1-SERIES-2-HATCHBACK-01	MEDIUM	Series 2改款外廓分支。	READY
144667	144667	SUV	Cayenne III Coupe		5	EU-PORSCHE-CAYENNE-III-COUPE-TURBO-GT-SUV-01	HIGH		READY
144672_standard	144672	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	标准悬架外廓分支。	READY
144672_fr	144672	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架外廓分支。	READY
144673_singlecab_l2_chassis	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L2-FWD-01	HIGH	单排驾驶室L2前驱裸底盘外廓。	READY
144673_singlecab_l2_platform	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L2-FWD-01	HIGH	单排驾驶室L2前驱原厂平台外廓。	READY
144673_singlecab_l3_chassis	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L3-FWD-01	HIGH	单排驾驶室L3前驱裸底盘外廓。	READY
144673_singlecab_l3_platform	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L3-FWD-01	HIGH	单排驾驶室L3前驱原厂平台外廓。	READY
144673_singlecab_l4_chassis	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L4-FWD-01	HIGH	单排驾驶室L4前驱裸底盘外廓。	READY
144673_singlecab_l4_platform	144673	Pickup	Transit V363	V363	2	EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L4-FWD-01	HIGH	单排驾驶室L4前驱原厂平台外廓。	READY
144673_doublecab_l2_chassis	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L2-FWD-01	HIGH	双排驾驶室L2前驱裸底盘外廓。	READY
144673_doublecab_l2_platform	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L2-FWD-01	HIGH	双排驾驶室L2前驱原厂平台外廓。	READY
144673_doublecab_l3_chassis	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L3-FWD-01	HIGH	双排驾驶室L3前驱裸底盘外廓。	READY
144673_doublecab_l3_platform	144673	Pickup	Transit V363	V363	4	EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L3-FWD-01	HIGH	双排驾驶室L3前驱原厂平台外廓。	READY
144674_l2h2	144674	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	HIGH	L2H2前驱厢式车外廓。	READY
144674_l2h3	144674	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L2H3-FWD-01	HIGH	L2H3前驱厢式车外廓。	READY
144674_l3h2	144674	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	HIGH	L3H2前驱厢式车外廓。	READY
144674_l3h3	144674	Van	Transit V363	V363		EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	HIGH	L3H3前驱厢式车外廓。	READY
144686	144686	SUV	iX I20	I20	5	EU-BMW-IX-I20-SUV-01	HIGH		READY
144687	144687	SUV	iX I20	I20	5	EU-BMW-IX-I20-SUV-01	HIGH		READY
144688	144688	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26五门Gran Coupé外廓。	READY
144689	144689	Coupe	i4 G26	G26	5	EU-BMW-I4-G26-GRAN-COUPE-01	HIGH	G26五门Gran Coupé外廓。	READY
144692	144692	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144693	144693	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144694	144694	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	HIGH	M440i xDrive外廓。	READY
144695	144695	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144696	144696	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144697	144697	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-01	HIGH		READY
144698	144698	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-M240I-XDRIVE-01	HIGH	M240i xDrive外廓。	READY
144700	144700	Coupe	2 Series Coupe G42	G42	2	EU-BMW-2-G42-COUPE-01	HIGH		READY
144723	144723	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-STANDARD-01	HIGH		READY
144724	144724	Coupe	4 Series Coupe G22	G22	2	EU-BMW-4-G22-COUPE-M440I-RWD-01	HIGH	M440i后驱外廓。	READY
144729	144729	Hatchback	Model S facelift 2021		5	EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	HIGH		READY
144730	144730	Hatchback	Model S facelift 2021		5	EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	HIGH		READY
144731	144731	SUV	Model X facelift 2021		5	EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	HIGH		READY
144732	144732	SUV	Model X facelift 2021		5	EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	HIGH		READY
144737	144737	Wagon	Outback VI BT	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-01	HIGH		READY
144747	144747	SUV	Karoq I	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	HIGH		READY
144752	144752	MPV	5008 I Phase II		5	EU-PEUGEOT-5008-I-PHASE-II-MPV-01	HIGH		READY
144761	144761	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
144783	144783	Coupe	Vantage 2018 F1 Edition		2	EU-ASTON-MARTIN-VANTAGE-2018-F1-COUPE-01	HIGH	535 hp F1 Edition Coupé外廓。	READY
144784	144784	Convertible	Vantage Roadster 2018 F1 Edition		2	EU-ASTON-MARTIN-VANTAGE-2018-F1-ROADSTER-01	HIGH	535 hp F1 Edition Roadster外廓。	READY
144791	144791	Convertible	SF90 Spider	F173	2	EU-FERRARI-SF90-SPIDER-F173-CONVERTIBLE-01	HIGH		READY
144801	144801	Wagon	Arteon I Shooting Brake facelift	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	HIGH	同三维Shooting Brake外廓，复用既有组。	READY
144806	144806	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	HIGH		READY
144807	144807	Wagon	Passat B8 Alltrack facelift	3G5	5	EU-VW-PASSAT-B8-ALLTRACK-FACELIFT-WAGON-01	HIGH		READY
144808_l1h1	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144808_l1h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144808_l2h1	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144808_l2h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144808_l3h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144808_l3h3	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144808_l4h2	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144808_l4h3	144808	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144809_l1h1	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144809_l1h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144809_l2h1	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144809_l2h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144809_l3h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144809_l3h3	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144809_l4h2	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144809_l4h3	144809	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144810_l1h1	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144810_l1h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144810_l2h1	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144810_l2h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144810_l3h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144810_l3h3	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144810_l4h2	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144810_l4h3	144810	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144812_l1h1	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	HIGH	L1H1厢式车外廓。	READY
144812_l1h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	HIGH	L1H2厢式车外廓。	READY
144812_l2h1	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	HIGH	L2H1厢式车外廓。	READY
144812_l2h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	HIGH	L2H2厢式车外廓。	READY
144812_l3h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	HIGH	L3H2厢式车外廓。	READY
144812_l3h3	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	HIGH	L3H3厢式车外廓。	READY
144812_l4h2	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	HIGH	L4H2加长厢式车外廓。	READY
144812_l4h3	144812	Van	Ducato III Series 8	X290		EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	HIGH	L4H3加长厢式车外廓。	READY
144817	144817	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-01	HIGH		READY
144818	144818	SUV	Model Y I		5	EU-TESLA-MODEL-Y-I-SUV-01	HIGH		READY
144824	144824	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-S580E-01	HIGH	标准轴距W223。	READY
144826	144826	Sedan	S-Class Long V223	V223	4	EU-MERCEDES-BENZ-S-CLASS-V223-LWB-SEDAN-S580E-01	HIGH	长轴距V223。	READY
144835	144835	Hatchback	Polestar 2 I		5	EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	HIGH		READY
144843	144843	Wagon	Octavia IV		5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH		READY
144844	144844	Hatchback	Zeekr 001 I		5	EU-ZEEKR-001-I-LIFTBACK-01	MEDIUM	早期车型外廓按001初代量产车闭合。	READY
144846	144846	Hatchback	Zeekr 001 I		5	EU-ZEEKR-001-I-LIFTBACK-01	MEDIUM	早期车型外廓按001初代量产车闭合。	READY
144856	144856	SUV	ID.4 I		5	EU-VW-ID4-I-SUV-PURE-01	HIGH		READY
144861_standard	144861	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	HIGH	Standard L2乘用版外廓。	READY
144861_long	144861	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	HIGH	Long L3乘用版外廓。	READY
144862	144862	Hatchback	ID.3 I		5	EU-VW-ID3-I-HATCHBACK-01	HIGH		READY
144863_standard	144863	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	HIGH	Standard L2乘用版外廓。	READY
144863_long	144863	MPV	Expert III		5	EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	HIGH	Long L3乘用版外廓。	READY
144864	144864	SUV	ID.4 I		5	EU-VW-ID4-I-SUV-PURE-01	HIGH		READY
144886	144886	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
144887	144887	SUV	ID.4 GTX I		5	EU-VW-ID4-I-GTX-SUV-01	HIGH	GTX独立外廓高度。	READY
144888	144888	SUV	Tucson IV	NX4	5	EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	HIGH		READY
144894	144894	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144895	144895	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144896	144896	SUV	Arkana I		5	EU-RENAULT-ARKANA-I-SUV-01	HIGH		READY
144901	144901	Sedan	G80 II	RG3	4	EU-GENESIS-G80-II-RG3-SEDAN-01	HIGH		READY
144927_swb	144927	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
144927_lwb	144927	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
144928	144928	Hatchback	Octavia IV		5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
144929	144929	Sedan	A3 8Y	8Y	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
144930	144930	Hatchback	A3 8Y Sportback	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
144931	144931	Hatchback	A3 8Y Sportback	8Y	5	EU-AUDI-A3-8Y-SPORTBACK-5D-01	HIGH		READY
144932	144932	Sedan	S4 B9 facelift	B9	4	EU-AUDI-S4-B9-FACELIFT-SEDAN-01	HIGH		READY
144934	144934	SUV	Q3 II F3	F3	5	EU-AUDI-Q3-II-F3-PHEV-SUV-01	HIGH		READY
144935	144935	SUV	Q3 II F3	F3	5	EU-AUDI-Q3-II-F3-PHEV-SUV-01	HIGH		READY
144941	144941	SUV	GV70 I	JK1	5	EU-GENESIS-GV70-I-JK1-SUV-01	HIGH		READY
144942	144942	SUV	GV70 I	JK1	5	EU-GENESIS-GV70-I-JK1-SUV-01	HIGH		READY
144946_swb	144946	MPV	NV300 Kombi X82	X82		EU-NISSAN-NV300-X82-COMBI-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
144946_lwb	144946	MPV	NV300 Kombi X82	X82		EU-NISSAN-NV300-X82-COMBI-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
144947_swb	144947	MPV	NV300 Kombi X82	X82		EU-NISSAN-NV300-X82-COMBI-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
144947_lwb	144947	MPV	NV300 Kombi X82	X82		EU-NISSAN-NV300-X82-COMBI-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
144949	144949	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
144993	144993	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
144996	144996	SUV	Defender 110 L663	L663	5	EU-LAND-ROVER-DEFENDER-110-L663-P525-SUV-01	HIGH		READY
145004	145004	Hatchback	i30 III PD facelift N	PD	5	EU-HYUNDAI-I30-III-PD-FACELIFT-N-HATCHBACK-01	HIGH		READY
145008	145008	Hatchback	Cupra Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	HIGH		READY
145009	145009	Hatchback	Cupra Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	HIGH		READY
145010	145010	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145011	145011	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145012	145012	Wagon	Cupra Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	HIGH		READY
145013	145013	Hatchback	Octavia IV		5	EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	HIGH		READY
145016	145016	SUV	Kodiaq I facelift 2021	NS7	5	EU-SKODA-KODIAQ-I-NS7-SUV-RS-FACELIFT-01	HIGH	RS改款外廓。	READY
145017	145017	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145018	145018	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145019	145019	Hatchback	Fabia IV		5	EU-SKODA-FABIA-IV-HATCHBACK-01	HIGH		READY
145020	145020	SUV	Q5 II FY facelift PHEV	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH		READY
145025	145025	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145026	145026	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145027	145027	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145028	145028	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145029	145029	Hatchback	Sandero III		5	EU-DACIA-SANDERO-III-HATCHBACK-01	HIGH		READY
145033	145033	Coupe	MC20 I	M240	2	EU-MASERATI-MC20-I-M240-COUPE-01	HIGH		READY
145034	145034	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
145035	145035	Hatchback	Golf VIII	CD1	5	EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	MEDIUM	CD1标准外廓。	READY
145036	145036	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
145037	145037	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	MEDIUM	Exige III固定车身外廓复用既有组。	READY
145038	145038	Wagon	Golf VIII Variant		5	EU-VW-GOLF-VIII-VARIANT-WAGON-01	HIGH		READY
145039	145039	Coupe	Exige III		2	EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	MEDIUM	Exige III固定车身外廓复用既有组。	READY
145045_swb	145045	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	HIGH	L1H1短轴乘用版外廓。	READY
145045_lwb	145045	MPV	Trafic III facelift 2021	X82		EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	HIGH	L2H1长轴乘用版外廓。	READY
145046	145046	SUV	X-Trail III T32 facelift	T32	5	EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	HIGH		READY
145048	145048	SUV	Taigo I		5	EU-VW-TAIGO-I-SUV-01	HIGH		READY
145049	145049	SUV	Taigo I		5	EU-VW-TAIGO-I-SUV-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_501-600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ROVER-SD1-SERIES-1-HATCHBACK-01	4698	1768	1382	Automobile-Catalog Rover 2600 Series 1	https://www.automobile-catalog.com/car/1977/37475/rover_2600.html
EU-ROVER-SD1-SERIES-2-HATCHBACK-01	4698	1768	1384	Automobile-Catalog Rover 2600 Series 2	https://www.automobile-catalog.com/car/1986/2996870/rover_2600_vanden_plas.html
EU-PORSCHE-CAYENNE-III-COUPE-TURBO-GT-SUV-01	4942	1995	1636	Auto-Data Porsche Cayenne III Coupe Turbo GT	https://www.auto-data.net/en/porsche-cayenne-iii-coupe-turbo-gt-4.0-v8-640hp-tiptronic-s-43791
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1448	Auto-Data Seat Leon IV Sportstourer	https://www.auto-data.net/en/seat-leon-iv-sportstourer-kl8-generation-7705
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	Auto-Data Seat Leon IV Sportstourer FR	https://www.auto-data.net/en/seat-leon-iv-sportstourer-kl8-generation-7705
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L2-FWD-01	5572	2052	2200	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY;Ford Transit Chassis Cab official UK brochure 25.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L2-FWD-01	5767	2098	2200	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L3-FWD-01	6022	2052	2194	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY;Ford Transit Chassis Cab official UK brochure 25.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L3-FWD-01	6204	2098	2194	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf
EU-FORD-TRANSIT-V363-CHASSIS-SINGLECAB-L4-FWD-01	6579	2052	2195	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY;Ford Transit Chassis Cab official UK brochure 25.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-PLATFORM-SINGLECAB-L4-FWD-01	6797	2098	2195	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L2-FWD-01	5572	2066	2236	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY;Ford Transit Chassis Cab official UK brochure 25.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L2-FWD-01	5767	2098	2236	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf
EU-FORD-TRANSIT-V363-CHASSIS-DOUBLECAB-L3-FWD-01	6022	2066	2230	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY;Ford Transit Chassis Cab official UK brochure 25.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_chassis_25.5MY.pdf
EU-FORD-TRANSIT-V363-PLATFORM-DOUBLECAB-L3-FWD-01	6204	2098	2230	Ford Transit Fahrgestelle und Pritschenwagen official Austria brochure 20.5MY	https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf
EU-FORD-TRANSIT-V363-VAN-L2H2-FWD-01	5531	2059	2533	Ford Transit official German brochure July 2021 archived copy;Ford Transit Van official UK brochure 25.5MY	https://www.konjunkturmotor.de/lima/5.0/ford/pdfs/251-katalog-08-2022.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L2H3-FWD-01	5531	2059	2769	Ford Transit official German brochure July 2021 archived copy;Ford Transit Van official UK brochure 25.5MY	https://www.konjunkturmotor.de/lima/5.0/ford/pdfs/251-katalog-08-2022.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H2-FWD-01	5981	2059	2530	Ford Transit official German brochure July 2021 archived copy;Ford Transit Van official UK brochure 25.5MY	https://www.konjunkturmotor.de/lima/5.0/ford/pdfs/251-katalog-08-2022.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-FORD-TRANSIT-V363-VAN-L3H3-FWD-01	5981	2059	2767	Ford Transit official German brochure July 2021 archived copy;Ford Transit Van official UK brochure 25.5MY	https://www.konjunkturmotor.de/lima/5.0/ford/pdfs/251-katalog-08-2022.pdf;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-transit_van_25.5MY.pdf
EU-BMW-IX-I20-SUV-01	4953	1967	1696	Auto-Data BMW iX I20 generation	https://www.auto-data.net/en/bmw-ix-i20-generation-8337
EU-BMW-I4-G26-GRAN-COUPE-01	4783	1852	1448	Auto-Data BMW i4 G26 eDrive40	https://www.auto-data.net/en/bmw-i4-g26-83.9-kwh-340hp-edrive40-43562
EU-BMW-4-G22-COUPE-STANDARD-01	4768	1852	1383	Auto-Data BMW 4 Series G22 420i	https://www.auto-data.net/en/bmw-4-series-coupe-g22-420i-184hp-steptronic-40261
EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	4770	1852	1393	Auto-Data BMW 4 Series G22 M440i xDrive	https://www.auto-data.net/en/bmw-4-series-coupe-g22-m440i-374hp-mild-hybrid-xdrive-steptronic-40263
EU-BMW-2-G42-COUPE-01	4537	1838	1390	Auto-Data BMW 2 Series Coupe G42	https://www.auto-data.net/en/bmw-2-series-coupe-g42-generation-8560
EU-BMW-2-G42-COUPE-M240I-XDRIVE-01	4548	1838	1404	Auto-Data BMW 2 Series G42 M240i xDrive	https://www.auto-data.net/en/bmw-2-series-coupe-g42-m240i-374hp-xdrive-steptronic-sport-43835
EU-BMW-4-G22-COUPE-M440I-RWD-01	4768	1852	1386	Auto-Data BMW 4 Series G22 M440i RWD	https://www.auto-data.net/en/bmw-4-series-coupe-g22-m440i-374hp-mild-hybrid-steptronic-43476
EU-TESLA-MODEL-S-FACELIFT-2021-HATCHBACK-01	5021	1987	1431	Auto-Data Tesla Model S facelift 2021 Plaid	https://www.auto-data.net/en/tesla-model-s-facelift-2021-plaid-100-kwh-1020hp-tri-motor-awd-42385
EU-TESLA-MODEL-X-FACELIFT-2021-SUV-01	5057	1999	1680	Auto-Data Tesla Model X facelift 2021 Long Range	https://www.auto-data.net/en/tesla-model-x-facelift-2021-long-range-100-kwh-670hp-dual-motor-awd-42386
EU-SUBARU-OUTBACK-VI-BT-WAGON-01	4870	1875	1675	Subaru Deutschland Outback press specification	https://www.subaru-presse.de/pressemitteilungen/subaru-outback-neudefinition-des-crossovers-langfassung-modelljahr-2022-2
EU-SKODA-KAROQ-I-NU7-SUV-FWD-01	4382	1841	1603	Auto-Data Skoda Karoq I 2.0 TDI FWD	https://www.auto-data.net/en/skoda-karoq-generation-5594
EU-PEUGEOT-5008-I-PHASE-II-MPV-01	4529	1888	1647	Auto-Data Peugeot 5008 I Phase II BlueHDi	https://www.auto-data.net/en/peugeot-5008-i-phase-ii-2013-1.6-bluehdi-120hp-20969
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-4MOTION-01	4509	1839	1684	Auto-Data Volkswagen Tiguan II facelift 4MOTION	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-generation-7711
EU-ASTON-MARTIN-VANTAGE-2018-F1-COUPE-01	4490	1942	1274	Auto-Data Aston Martin Vantage F1 Edition Coupe	https://www.auto-data.net/en/aston-martin-v8-vantage-2018-f1-edition-4.0-v8-535hp-automatic-42548
EU-ASTON-MARTIN-VANTAGE-2018-F1-ROADSTER-01	4490	1942	1274	Auto-Data Aston Martin Vantage F1 Edition Roadster	https://www.auto-data.net/en/aston-martin-v8-vantage-roadster-2018-f1-edition-4.0-v8-535hp-automatic-42549
EU-FERRARI-SF90-SPIDER-F173-CONVERTIBLE-01	4704	1973	1191	Auto-Data Ferrari SF90 Spider	https://www.auto-data.net/en/ferrari-sf90-spider-4.0-v8-1000hp-plug-in-hybrid-awd-f1-41753
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	4866	1871	1450	Auto-Data Volkswagen Arteon Shooting Brake facelift	https://www.auto-data.net/en/volkswagen-arteon-shooting-brake-facelift-2020-generation-7708
EU-VW-PASSAT-B8-ALLTRACK-FACELIFT-WAGON-01	4780	1853	1527	Auto-Data Passat Alltrack B8 facelift generation	https://www.auto-data.net/en/volkswagen-passat-alltrack-b8-facelift-2019-generation-7175
EU-FIAT-DUCATO-III-X290-VAN-L1H1-01	4963	2050	2254	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L1H2-01	4963	2050	2524	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L2H1-01	5413	2050	2254	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L2H2-01	5413	2050	2539	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L3H2-01	5998	2050	2534	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L3H3-01	5998	2050	2774	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L4H2-01	6363	2050	2539	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-FIAT-DUCATO-III-X290-VAN-L4H3-01	6363	2050	2779	Fiat Professional New Ducato official dimensions;Fiat Professional Ducato Furgon official price list July 2021	https://www.fiatprofessional.com/ducato-2021-old/new-ducato/dimensions;https://www.fiatprofessional.si/wp-content/uploads/2021/07/Fiat-Professional-DUCATO-FURGON-CENIK-27.07.2021.pdf
EU-TESLA-MODEL-Y-I-SUV-01	4751	1921	1624	Auto-Data Tesla Model Y Standard Range	https://www.auto-data.net/en/tesla-model-y-standard-range-60-kwh-299hp-54490
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-S580E-01	5179	1954	1503	Auto-Data Mercedes-Benz S-Class W223 S580e	https://www.auto-data.net/en/mercedes-benz-s-class-w223-s-580e-510hp-plug-in-hybrid-9g-tronic-44006
EU-MERCEDES-BENZ-S-CLASS-V223-LWB-SEDAN-S580E-01	5289	1954	1503	Auto-Data Mercedes-Benz S-Class Long V223 S580e	https://www.auto-data.net/en/mercedes-benz-s-class-long-v223-s-580e-510hp-plug-in-hybrid-9g-tronic-44007
EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	4606	1859	1482	Auto-Data Polestar 2 I	https://www.auto-data.net/en/polestar-2-generation-7277
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468	Auto-Data Skoda Octavia IV Combi	https://www.auto-data.net/en/skoda-octavia-iv-combi-generation-7150
EU-ZEEKR-001-I-LIFTBACK-01	4970	1999	1560	Auto-Data Zeekr 001	https://www.auto-data.net/en/zeekr-001-100-kwh-272hp-single-motor-electric-48808
EU-VW-ID4-I-SUV-PURE-01	4584	1852	1640	Auto-Data Volkswagen ID.4 Pure; Auto-Data Volkswagen ID.4 Pure Performance	https://www.auto-data.net/en/volkswagen-id.4-pure-55-kwh-149hp-43345;https://www.auto-data.net/en/volkswagen-id.4-pure-performance-55-kwh-170hp-45144
EU-PEUGEOT-EXPERT-III-COMBI-STANDARD-01	4956	1920	1890	PEUGEOT (e-) Expert Kombi official Austria price list December 2021	https://www.auto-guenther.at/fileadmin/media/download/Preislisten/Peugeot_Expert_Preisliste.pdf
EU-PEUGEOT-EXPERT-III-COMBI-LONG-01	5308	1920	1890	PEUGEOT (e-) Expert Kombi official Austria price list December 2021	https://www.auto-guenther.at/fileadmin/media/download/Preislisten/Peugeot_Expert_Preisliste.pdf
EU-VW-ID3-I-HATCHBACK-01	4261	1809	1568	Auto-Data Volkswagen ID.3 Pro 145	https://www.auto-data.net/en/volkswagen-id.3-pro-62-kwh-145hp-41700
EU-VW-GOLF-VIII-VARIANT-WAGON-01	4633	1789	1498	Auto-Data Volkswagen Golf VIII Variant	https://www.auto-data.net/en/volkswagen-golf-viii-variant-generation-7894
EU-VW-ID4-I-GTX-SUV-01	4582	1852	1637	Auto-Data Volkswagen ID.4 GTX	https://www.auto-data.net/en/volkswagen-id.4-gtx-82-kwh-299hp-4motion-43344
EU-HYUNDAI-TUCSON-IV-NX4-SUV-FWD-01	4500	1865	1651	Auto-Data Hyundai Tucson IV 1.6 T-GDI 180 FWD	https://www.auto-data.net/en/hyundai-tucson-iv-1.6-t-gdi-180hp-mild-hybrid-42121
EU-RENAULT-ARKANA-I-SUV-01	4568	1820	1576	Renault global media Arkana dimensions;Carstan Renault Arkana dimensions	https://media.renault.com/the-new-renault-arkana-more-nouvelle-vague-than-ever/?lang=eng;https://carstan.info/dimensions/renault/arkana/13-tce-140-hp-2740
EU-GENESIS-G80-II-RG3-SEDAN-01	4995	1925	1465	Auto-Data Genesis G80 II 2.2 AWD	https://www.auto-data.net/en/genesis-g80-ii-2.2-e-vgt-210hp-awd-automatic-41425
EU-RENAULT-TRAFIC-III-X82-PASSENGER-L1H1-01	5080	1956	1973	Renault New Trafic Passenger official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20331-NewTraficPassengerBrochureApril2022.pdf
EU-RENAULT-TRAFIC-III-X82-PASSENGER-L2H1-01	5480	1956	1974	Renault New Trafic Passenger official brochure April 2022	https://www.press.renault.co.uk/assets/documents/original/20331-NewTraficPassengerBrochureApril2022.pdf
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470	Auto-Data Skoda Octavia IV liftback	https://www.auto-data.net/en/skoda-octavia-iv-generation-7149
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425	Auto-Data Audi A3 Sedan 8Y	https://www.auto-data.net/en/audi-a3-sedan-8y-generation-7686
EU-AUDI-A3-8Y-SPORTBACK-5D-01	4343	1816	1449	Auto-Data Audi A3 Sportback 8Y	https://www.auto-data.net/en/audi-a3-sportback-8y-generation-7565
EU-AUDI-S4-B9-FACELIFT-SEDAN-01	4770	1847	1404	Auto-Data Audi S4 B9 facelift TDI	https://www.auto-data.net/en/audi-s4-b9-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47367
EU-AUDI-Q3-II-F3-PHEV-SUV-01	4485	1849	1574	Auto-Data Audi Q3 II F3 45 TFSI e	https://www.auto-data.net/en/audi-q3-ii-f3-45-tfsi-e-245hp-plug-in-hybrid-s-tronic-42115
EU-GENESIS-GV70-I-JK1-SUV-01	4715	1910	1630	Auto-Data Genesis GV70 2.5 AWD;Auto-Data Genesis GV70 2.2 AWD	https://www.auto-data.net/fr/genesis-gv70-2.5-t-gdi-304hp-awd-automatic-41921;https://www.auto-data.net/de/genesis-gv70-2.2-e-vgt-210hp-awd-automatic-41923
EU-NISSAN-NV300-X82-COMBI-L1H1-01	4999	1956	1971	Nissan NV300 official UK brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-NISSAN-NV300-X82-COMBI-L2H1-01	5399	1956	1971	Nissan NV300 official UK brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Auto-Data Volvo XC60 II	https://www.auto-data.net/en/volvo-xc60-ii-generation-5442
EU-VW-GOLF-VIII-CD1-HATCHBACK-STANDARD-01	4284	1789	1491	Auto-Data Volkswagen Golf VIII standard hatchback	https://www.auto-data.net/en/volkswagen-golf-viii-1.0-tsi-90hp-40806
EU-LAND-ROVER-DEFENDER-110-L663-P525-SUV-01	5018	1996	1967	Land Rover Defender official technical specification;Auto-Data Defender 110 P525	https://www.landrover.com/content/dam/lrdx/pdfs/no/brochures/Defender.pdf;https://www.auto-data.net/en/land-rover-defender-110-l663-5.0-v8-p525-525hp-awd-automatic-42462
EU-HYUNDAI-I30-III-PD-FACELIFT-N-HATCHBACK-01	4340	1795	1419	Auto-Data Hyundai i30 N Performance 280	https://www.auto-data.net/en/hyundai-i30-iii-facelift-2020-n-performance-2.0-t-gdi-280hp-dct-43366
EU-CUPRA-LEON-IV-KL1-HATCHBACK-01	4398	1799	1442	Auto-Data Cupra Leon 245;Auto-Data Cupra Leon 300	https://www.auto-data.net/en/cupra-leon-2.0-tsi-245hp-dsg-45971;https://www.auto-data.net/en/cupra-leon-2.0-tsi-evo-300hp-dsg-42357
EU-CUPRA-LEON-IV-KL8-SPORTSTOURER-01	4657	1799	1437	Auto-Data Cupra Leon Sportstourer 245;Auto-Data Cupra Leon Sportstourer 300;Auto-Data Cupra Leon Sportstourer 310 4Drive	https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-245hp-dsg-45972;https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-300hp-dsg-43840;https://www.auto-data.net/en/cupra-leon-sportstourer-2.0-tsi-310hp-4drive-dsg-43391
EU-SKODA-KODIAQ-I-NS7-SUV-RS-FACELIFT-01	4699	1882	1687	Auto-Data Skoda Kodiaq I facelift RS	https://www.auto-data.net/en/skoda-kodiaq-i-facelift-2021-rs-2.0-tsi-245hp-4x4-dsg-43763
EU-SKODA-FABIA-IV-HATCHBACK-01	4108	1780	1459	Auto-Data Skoda Fabia IV 1.0 TSI	https://www.auto-data.net/en/skoda-fabia-iv-1.0-tsi-110hp-43755
EU-AUDI-Q5-II-FY-PHEV-SUV-01	4682	1893	1652	Auto-Data Audi Q5 II FY facelift 55 TFSI e	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-55-tfsi-e-367hp-quattro-s-tronic-42557
EU-DACIA-SANDERO-III-HATCHBACK-01	4088	1848	1499	Auto-Data Dacia Sandero III 1.0 TCe	https://www.auto-data.net/en/dacia-sandero-iii-1.0-tce-91hp-41829
EU-MASERATI-MC20-I-M240-COUPE-01	4669	1965	1221	Auto-Data Maserati MC20 3.0 V6	https://www.auto-data.net/en/maserati-mc20-3.0-v6-630hp-dct-41203
EU-LOTUS-EXIGE-III-SPORT-380-COUPE-01	4084	1802	1129	Auto-Data Lotus Exige III Sport 380	https://www.auto-data.net/en/lotus-exige-iii-sport-380-3.5-v6-380hp-29121
EU-NISSAN-X-TRAIL-III-T32-SUV-FACELIFT-01	4690	1820	1710	Auto-Data Nissan X-Trail III T32 facelift	https://www.auto-data.net/en/nissan-x-trail-iii-t32-facelift-2017-generation-5307
EU-VW-TAIGO-I-SUV-01	4266	1757	1515	Auto-Data Volkswagen Taigo 1.0 TSI	https://www.auto-data.net/en/volkswagen-taigo-1.0-tsi-95hp-44420
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_501-600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf "https://www.ford.at/content/dam/guxeu/at/de_at/documents/brochures/commercial-vehicles/BRO-ford_transit_fahrgestelle.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_501-600_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_501-600_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2454 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1175 行）

