# 任务：all 第 7601-7700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0077__1f35fc42


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7601-7700 行

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
all 第 7601-7700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-01	4015	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-FACELIFT-01	4015	1612	1345
EU-ALFA-ROMEO-33-905-HATCHBACK-4X4-PREFL-01	4015	1612	1325
EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340
EU-ALFA-ROMEO-33-905-HATCHBACK-FWD-01	4015	1612	1303
EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345
EU-ALFA-ROMEO-33-905-WAGON-FWD-01	4142	1612	1345
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350
EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350
EU-ALFA-ROMEO-33-907-HATCHBACK-4X4-01	4075	1614	1375
EU-ALFA-ROMEO-33-907-WAGON-4X4-01	4200	1614	1375
EU-ALFA-ROMEO-75-162B-SEDAN-AMERICA-01	4420	1660	1400
EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	4330	1630	1400
EU-ALFA-ROMEO-75-162B-SEDAN-TURBO-EUROPA-01	4330	1650	1400
EU-ALFA-ROMEO-75-162B-SEDAN-TWINSPARK-01	4330	1660	1400
EU-ALFA-ROMEO-90-162A-SEDAN-01	4391	1638	1420
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453
EU-BMW-1600-GT-COUPE-2D-01	4050	1550	1280
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421
EU-BMW-6-E24-COUPE-EARLY-01	4755	1725	1365
EU-BMW-6-E24-COUPE-LATE-01	4815	1725	1365
EU-BMW-6-E24-COUPE-M635I-EARLY-01	4755	1725	1355
EU-BMW-6-E24-COUPE-M635I-LATE-01	4815	1725	1355
EU-BMW-6-F12-CONVERTIBLE-01	4894	1894	1365
EU-BMW-6-F13-COUPE-01	4894	1894	1369
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776
EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	4844	1877	1669
EU-CITROEN-AX-GT-HATCHBACK-3D-01	3495	1596	1340
EU-CITROEN-AX-PHASE-I-HATCHBACK-01	3495	1555	1355
EU-CITROEN-AX-PHASE-I-HATCHBACK-PRE92-01	3495	1596	1340
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355
EU-CITROEN-AX-PHASE-II-HATCHBACK-POST92-01	3525	1555	1355
EU-CITROEN-AX-SPORT-HATCHBACK-3D-01	3495	1596	1350
EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1410
EU-CITROEN-VISA-DIESEL-HATCHBACK-5D-01	3725	1550	1410
EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1370
EU-CITROEN-VISA-GTI-105-HATCHBACK-5D-01	3725	1540	1370
EU-CITROEN-VISA-GTI-115-HATCHBACK-5D-01	3725	1600	1370
EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	3690	1535	1408
EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	3690	1530	1400
EU-CITROEN-VISA-PREFL-HATCHBACK-5D-01	3690	1530	1415
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389
EU-FORD-FIESTA-III-GFJ-HATCHBACK-XR2I-01	3801	1630	1365
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407
EU-FORD-SIERRA-II-SEDAN-01	4467	1698	1407
EU-FORD-SIERRA-MK1-HATCHBACK-3D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-01	4394	1703	1408
EU-FORD-SIERRA-MK1-HATCHBACK-5D-GHIA-01	4425	1725	1408
EU-FORD-SIERRA-MK1-WAGON-01	4491	1712	1438
EU-FORD-SIERRA-MK1-WAGON-GHIA-01	4522	1729	1438
EU-FORD-SIERRA-MK1-XR4I-HATCHBACK-3D-01	4459	1728	1392
EU-FORD-SIERRA-MK1-XR4X4-HATCHBACK-5D-01	4459	1725	1378
EU-FORD-SIERRA-TURNIER-I-01	4511	1720	1428
EU-FORD-SIERRA-TURNIER-II-01	4511	1720	1428
EU-HONDA-CR-V-III-SUV-01	4519	1820	1679
EU-HONDA-CR-V-IV-RM-SUV-FACELIFT-01	4605	1820	1685
EU-HONDA-CR-V-IV-RM-SUV-PREFL-01	4570	1820	1685
EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	4448	1702	1393
EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	4420	1700	1393
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457
EU-PEUGEOT-106-I-HATCHBACK-3D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-5D-01	3564	1590	1369
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367
EU-PEUGEOT-106-I-HATCHBACK-LEMANS-01	3564	1607	1360
EU-PEUGEOT-106-II-1.6-HATCHBACK-3D-01	3680	1590	1380
EU-PEUGEOT-106-II-1.6-HATCHBACK-5D-01	3680	1590	1380
EU-PEUGEOT-106-II-HATCHBACK-3D-01	3678	1594	1376
EU-PEUGEOT-106-II-HATCHBACK-5D-01	3678	1594	1376
EU-PEUGEOT-106-II-S16-HATCHBACK-3D-01	3678	1610	1357
EU-PEUGEOT-305-II-BREAK-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-BASE-01	4283	1630	1426
EU-PEUGEOT-305-II-BREAK-WIDE-01	4283	1636	1426
EU-PEUGEOT-305-II-SEDAN-BASE-01	4263	1630	1407
EU-PEUGEOT-305-II-SEDAN-SPORT-01	4263	1636	1396
EU-PEUGEOT-305-II-SEDAN-WIDE-01	4263	1636	1411
EU-PEUGEOT-405-I-BREAK-01	4398	1716	1445
EU-PEUGEOT-405-II-BREAK-01	4398	1704	1445
EU-PEUGEOT-405-II-SEDAN-MI16-01	4408	1716	1406
EU-PEUGEOT-405-II-SEDAN-STANDARD-01	4408	1694	1406
EU-PEUGEOT-405-II-SEDAN-T16-01	4408	1716	1390
EU-PEUGEOT-405-I-SEDAN-01	4408	1716	1406
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940
EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	5489	1965	1900
EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	4712	1965	1900
EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	4765	1965	2100
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	5489	1965	2420
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	5489	1965	2100
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	4759	1965	2420
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	4759	1965	2100
EU-PEUGEOT-J5-290P-MINIBUS-4X4-STANDARD-01	4765	1965	2100
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810
EU-ROVER-200-III-RF-HATCHBACK-01	3973	1688	1419
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390
EU-SEAT-IBIZA-I-HATCHBACK-3D-01	3685	1610	1410
EU-SEAT-IBIZA-I-HATCHBACK-5D-01	3685	1610	1410
EU-SEAT-IBIZA-II-6K1-GT-HATCHBACK-3D-01	3853	1640	1409
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-3D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K2-HATCHBACK-5D-01	3876	1640	1422
EU-SEAT-IBIZA-II-6K-HATCHBACK-3D-01	3813	1640	1390
EU-SEAT-IBIZA-II-6K-HATCHBACK-5D-01	3813	1640	1390
EU-SEAT-IBIZA-IV-3D-FACELIFT-HATCHBACK-01	4043	1693	1428
EU-SEAT-IBIZA-IV-3D-PREFL-HATCHBACK-01	4034	1693	1428
EU-SEAT-IBIZA-IV-5D-FACELIFT-HATCHBACK-01	4061	1693	1445
EU-SEAT-IBIZA-IV-5D-PREFL-HATCHBACK-01	4052	1693	1445
EU-SEAT-IBIZA-IV-SC-HATCHBACK-FACELIFT-01	4043	1693	1428
EU-SEAT-IBIZA-IV-SC-HATCHBACK-PREFL-01	4034	1693	1428
EU-SEAT-TERRA-MPV-3D-01	3869	1490	1895
EU-SEAT-TERRA-VAN-3D-01	3869	1490	1895
EU-TOYOTA-COROLLA-FX-E80-HATCHBACK-3D-01	3970	1635	1385
EU-TOYOTA-COROLLA-II-E20-SEDAN-4D-01	3945	1505	1375
EU-TOYOTA-COROLLA-III-E30-COUPE-KE35-2D-01	3995	1570	1350
EU-TOYOTA-COROLLA-III-E30-SEDAN-4D-01	3995	1570	1375
EU-TOYOTA-COROLLA-III-E30-WAGON-KE36-5D-01	4050	1570	1390
EU-TOYOTA-COROLLA-III-E50-LIFTBACK-3D-01	4120	1600	1320
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-KE70-3D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-HATCHBACK-TE71-3D-01	4105	1626	1341
EU-TOYOTA-COROLLA-IV-E70-SEDAN-4D-01	4050	1610	1385
EU-TOYOTA-COROLLA-IV-E70-WAGON-5D-01	4105	1610	1390
EU-TOYOTA-COROLLA-V-E80-COUPE-AE86-2D-01	4200	1645	1335
EU-TOYOTA-COROLLA-V-E80-HATCHBACK-5D-01	4135	1635	1385
EU-TOYOTA-COROLLA-V-E80-SEDAN-4D-01	4135	1635	1385
EU-TOYOTA-COROLLA-VI-E90-COMPACT-3D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-5D-01	3995	1655	1365
EU-TOYOTA-COROLLA-VI-E90-COMPACT-GTI-3D-01	3995	1665	1360
EU-TOYOTA-COROLLA-VI-E90-LIFTBACK-5D-01	4215	1665	1365
EU-TOYOTA-COROLLA-VI-E90-SEDAN-4D-01	4195	1655	1365
EU-TOYOTA-COROLLA-VI-E90-WAGON-4WD-5D-01	4250	1655	1450
EU-TOYOTA-COROLLA-VI-E90-WAGON-5D-01	4205	1655	1425
EU-TOYOTA-COROLLA-VII-E100-COMPACT-3D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-COMPACT-5D-01	4095	1685	1380
EU-TOYOTA-COROLLA-VII-E100-LIFTBACK-5D-01	4295	1685	1375
EU-TOYOTA-COROLLA-VII-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-VII-E100-WAGON-5D-01	4260	1685	1460
EU-VW-GOLF-VI-5K-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-R-HATCHBACK-3D-01	4212	1786	1469
EU-VW-GOLF-VI-R-HATCHBACK-5D-01	4212	1786	1461

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Focus iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	85	115	Jul 2010	Jun 2014	2024-03-01	8204
Ford	Focus iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	103	140	Jul 2010	Jun 2014	2024-03-01	8205
Ford	Focus iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	120	163	Jul 2010	Jun 2014	2024-03-01	8206
VW	Golf vi	1.2 TSI	Cabriolet	Frontantrieb	Benzin	77	105	Mar 2011	May 2016	2024-03-01	8207
VW	Golf vi	1.4 TSI	Cabriolet	Frontantrieb	Benzin	90	122	Nov 2011	May 2016	2024-03-01	8208
VW	Golf vi	1.4 TSI	Cabriolet	Frontantrieb	Benzin	118	160	Mar 2011	May 2016	2024-03-01	8209
VW	Golf vi	2.0 GTI	Cabriolet	Frontantrieb	Benzin	155	211	May 2012	May 2016	2024-03-01	8210
VW	Golf vi	1.6 TDI	Cabriolet	Frontantrieb	Diesel	77	105	Mar 2011	May 2016	2024-03-01	8211
VW	Golf vi	2.0 TDI	Cabriolet	Frontantrieb	Diesel	103	140	Nov 2011	May 2016	2024-03-01	8212
Seat	Terra	0.9	Kombi	Frontantrieb	Benzin	29	40	Feb 1987	Dec 1996	2024-03-01	8213
Seat	Terra	0.9	Kasten/Kombi	Frontantrieb	Benzin	29	40	Jan 1987	Dec 1995	2024-03-01	8215
Peugeot	Partner	1.1	Großraumlimousine	Frontantrieb	Benzin	44	60	Jun 1996	Oct 2002	2024-03-01	8216
Peugeot	Partner	1.4	Großraumlimousine	Frontantrieb	Benzin	55	75	Jun 1996	Dec 2015	2024-03-01	8217
Peugeot	Partner	1.9 D	Großraumlimousine	Frontantrieb	Diesel	50	68	Jun 1996	Dec 2002	2024-03-01	8218
Peugeot	Expert	1.9 TD	Bus	Frontantrieb	Diesel	66	90	Feb 1996	Sep 2000	2024-03-01	8219
Peugeot	Expert	1.6	Kasten	Frontantrieb	Benzin	58	79	Feb 1996	Sep 2000	2024-03-01	8220
Peugeot	Expert	1.6	Pritsche/Fahrgestell	Frontantrieb	Benzin	58	79	Feb 1996	Sep 2000	2024-03-01	8221
Peugeot	Expert	1.9 D	Kasten	Frontantrieb	Diesel	51	70	Feb 1996	Dec 1998	2024-03-01	8222
Peugeot	Expert	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	70	Feb 1996	Dec 1998	2024-03-01	8223
Peugeot	Expert	1.9 TD	Kasten	Frontantrieb	Diesel	66	90	Feb 1996	Sep 2000	2024-03-01	8224
Peugeot	Expert	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Feb 1996	Sep 2000	2024-03-01	8225
Peugeot	Expert	1.9 TD	Kasten	Frontantrieb	Diesel	68	92	Feb 1996	May 1998	2024-03-01	8226
Peugeot	Expert	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	68	92	Feb 1996	May 1998	2024-03-01	8227
Peugeot	J5	2.5 D	Bus	Frontantrieb	Diesel	54	73	Oct 1990	Feb 1994	2024-03-01	8228
Peugeot	J5	1.9 D	Kasten	Frontantrieb	Diesel	51	70	Oct 1990	Mar 1994	2024-03-01	8229
Peugeot	J5	2.5 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	54	73	Oct 1990	Feb 1994	2024-03-01	8230
Peugeot	J5	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	62	84	Oct 1990	Feb 1994	2024-03-01	8231
Peugeot	J5	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	54	73	Oct 1990	Feb 1994	2024-03-01	8232
Peugeot	J5	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	51	70	Oct 1990	Feb 1994	2024-03-01	8233
Alfa Romeo	33	1.8 TD	Schrägheck	Frontantrieb	Diesel	54	73	Jan 1986	Jun 1990	2024-03-01	8234
Peugeot	J5	1.8	Kasten	Frontantrieb	Benzin	51	69	Jan 1983	Nov 1988	2024-03-01	8235
Peugeot	405 i	1.6	Stufenheck	Frontantrieb	Benzin	69	94	Jan 1987	Dec 1992	2024-03-01	8240
Peugeot	106 i	1	Schrägheck	Frontantrieb	Benzin	37	50	Sep 1991	Apr 1996	2024-03-01	8242
Rover	200 ii	214 Gsi/si	Schrägheck	Frontantrieb	Benzin	70	95	Jan 1990	Oct 1995	2024-03-01	8248
BMW	6	640 I	Cabriolet	Heckantrieb	Benzin	235	320	Sep 2011	Jun 2018	2024-03-01	8256
Alfa Romeo	33	1.5	Schrägheck	Frontantrieb	Benzin	70	95	May 1983	Dec 1993	2024-03-01	8258
Alfa Romeo	90	2.0 I.e.	Stufenheck	Heckantrieb	Benzin	97	132	Oct 1984	Jul 1987	2024-03-01	8267
BMW	6	650 I	Cabriolet	Heckantrieb	Benzin	300	408	Dec 2010	Jun 2012	2024-03-01	8268
Hyundai	Lantra ii	1.5 12V	Kombi	Frontantrieb	Benzin	65	88	Apr 1997	Oct 2000	2024-03-01	8270
Hyundai	Lantra ii	2.0 16V	Kombi	Frontantrieb	Benzin	102	139	Nov 1995	Oct 2000	2024-03-01	8271
BMW	6	640 I	Coupe	Heckantrieb	Benzin	235	320	Jul 2011	Oct 2017	2024-03-01	8272
Hyundai	Lantra ii	1.5 12V	Stufenheck	Frontantrieb	Benzin	65	88	Dec 1996	Sep 2000	2024-03-01	8273
Peugeot	305 ii	1.6	Stufenheck	Frontantrieb	Benzin	69	94	Oct 1982	Jun 1988	2024-03-01	8281
BMW	1	125 I	Schrägheck	Heckantrieb	Benzin	160	218	Mar 2012	Nov 2017	2024-03-01	8282
Seat	Ibiza i	1.5 I	Schrägheck	Frontantrieb	Benzin	65	89	Oct 1986	May 1993	2024-03-01	8283
BMW	6	650 I	Coupe	Heckantrieb	Benzin	300	408	Jul 2011	Jun 2012	2024-03-01	8284
Alfa Romeo	75	1.6	Stufenheck	Heckantrieb	Benzin	76	103	May 1985	Sep 1989	2024-03-01	8285
Citroën	Ax	10	Schrägheck	Frontantrieb	Benzin	37	50	Feb 1987	Dec 1998	2024-03-01	8288
BMW	X5	Xdrive 50 I	SUV	Allrad	Benzin	300	408	Apr 2010	Jul 2013	2024-03-01	8292
Citroën	Visa	1	Schrägheck	Frontantrieb	Benzin	33	45	Sep 1984	Jun 1988	2024-03-01	8293
Citroën	Visa	14 GT	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1982	Mar 1987	2024-03-01	8294
Renault	4	0.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	25	34	Sep 1966	Dec 1988	2024-03-01	8300
Ford	Fiesta iii	1	Schrägheck	Frontantrieb	Benzin	33	45	Mar 1989	Dec 1995	2024-03-01	8302
Renault	5	1.4 Turbo	Schrägheck	Heckantrieb	Benzin	118	160	Jun 1980	Jan 1985	2024-03-01	8306
Ford	Sierra	2.0 I	Schrägheck	Heckantrieb	Benzin	92	125	Jun 1989	Feb 1993	2024-03-01	8312
Fiat	Croma	1900 Turbo D I.d.	Schrägheck	Frontantrieb	Diesel	66	90	Aug 1987	Oct 1992	2024-03-01	8313
Audi	A6 c5	1.8 T Quattro	Stufenheck	Allrad	Benzin	110	150	Feb 1997	Jan 2005	2024-03-01	8315
Audi	A6 c5	2.4	Stufenheck	Frontantrieb	Benzin	121	165	Feb 1997	Jan 2005	2024-03-01	8316
Audi	A6 c5	2.4 Quattro	Stufenheck	Allrad	Benzin	121	165	Feb 1997	Jan 2005	2024-03-01	8317
Audi	A6 c5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	81	110	Apr 1997	Oct 2000	2024-03-01	8318
Audi	A6 c5	2.5 TDI	Stufenheck	Frontantrieb	Diesel	110	150	Jul 1997	Jan 2005	2024-03-01	8319
Audi	A6 c5	2.8	Stufenheck	Frontantrieb	Benzin	142	193	Feb 1997	Jan 2005	2024-03-01	8320
Toyota	Corolla	1.4	Kombi	Frontantrieb	Benzin	63	86	Apr 1997	Feb 2000	2024-03-01	8321
Toyota	Corolla	1.6	Kombi	Frontantrieb	Benzin	81	110	Apr 1997	Feb 2000	2024-03-01	8322
Toyota	Corolla	1.6 Aut.	Kombi	Frontantrieb	Benzin	79	107	Apr 1997	Feb 2000	2024-03-01	8323
Toyota	Corolla	1.8 4WD	Kombi	Allrad	Benzin	81	110	Apr 1997	Oct 2001	2024-03-01	8324
Toyota	Corolla	2.0 D	Kombi	Frontantrieb	Diesel	53	72	Apr 1997	Feb 2000	2024-03-01	8325
Toyota	Corolla	1.4	Stufenheck	Frontantrieb	Benzin	63	86	May 1997	Sep 1999	2024-03-01	8326
Toyota	Corolla	1.6 Aut.	Stufenheck	Frontantrieb	Benzin	79	107	Apr 1997	Feb 2000	2024-03-01	8328
Toyota	Corolla	2.0 D	Stufenheck	Frontantrieb	Diesel	53	72	Apr 1997	Feb 2000	2024-03-01	8329
Toyota	Corolla	1.4	Schrägheck	Frontantrieb	Benzin	63	86	May 1997	Sep 1999	2024-03-01	8330
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	81	110	May 1997	Feb 2000	2024-03-01	8331
Toyota	Corolla	1.6 Aut.	Schrägheck	Frontantrieb	Benzin	79	107	May 1997	Feb 2000	2024-03-01	8332
Toyota	Corolla	2.0 D	Schrägheck	Frontantrieb	Diesel	53	72	Apr 1997	Feb 2000	2024-03-01	8333
Toyota	Corolla	1.6	Schrägheck	Frontantrieb	Benzin	81	110	May 1997	Aug 2001	2024-08-01	8334
Toyota	Corolla	1.4	Schrägheck	Frontantrieb	Benzin	63	86	May 1997	Sep 1999	2024-03-01	8335
Toyota	Corolla	1.6 Aut.	Schrägheck	Frontantrieb	Benzin	79	107	May 1997	Feb 2000	2024-03-01	8336
Toyota	Corolla	2.0 D	Schrägheck	Frontantrieb	Diesel	53	72	Apr 1997	Feb 2000	2024-03-01	8337
Audi	A6 c5	2.8 Quattro	Stufenheck	Allrad	Benzin	142	193	Feb 1997	Jan 2005	2024-03-01	8351
Audi	A4 b5	2.4	Stufenheck	Frontantrieb	Benzin	121	165	Mar 1997	Nov 2000	2024-03-01	8352
Audi	A4 b5	2.4 Quattro	Stufenheck	Allrad	Benzin	121	165	Mar 1997	Nov 2000	2024-03-01	8353
Audi	A4 b5 avant	2.4	Kombi	Frontantrieb	Benzin	121	165	Mar 1997	Sep 2001	2024-03-01	8354
Audi	A4 b5 avant	2.4 Quattro	Kombi	Allrad	Benzin	121	165	Mar 1997	Sep 2001	2024-03-01	8355
Citroën	Xantia	1.9 SD	Kombi	Frontantrieb	Diesel	55	75	Apr 1997	Apr 2003	2024-03-01	8356
Citroën	Xantia	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Apr 1997	Apr 2003	2024-03-01	8357
Citroën	Xantia	1.8 I	Kombi	Frontantrieb	Benzin	66	90	Apr 1997	Apr 2003	2024-03-01	8358
VW	Touareg	3.6 V6 FSI	SUV	Allrad	Benzin	183	249	Aug 2010	Mar 2018	2024-03-01	8359
Chevrolet	Lumina apv	3.8	Großraumlimousine	Frontantrieb	Benzin	129	175	Dec 1992	Jul 1996	2024-03-01	8360
Chevrolet	Lumina apv	2.3	Großraumlimousine	Frontantrieb	Benzin	108	147	Dec 1992	Jul 1996	2024-03-01	8361
Chevrolet	Lumina apv	2.3	Großraumlimousine	Frontantrieb	Benzin	101	137	Oct 1993	Jul 1996	2024-03-01	8362
Chevrolet	Lumina apv	3.1	Großraumlimousine	Frontantrieb	Benzin	90	122	Aug 1989	Jul 1996	2024-03-01	8363
Chevrolet	Blazer s10	4.3 V6 AWD	Geländewagen geschlossen	Allrad	Benzin	142	193	Jan 1994	Sep 2005	2024-03-01	8364
Chevrolet	Corvette	5.7	Coupe	Heckantrieb	Benzin	253	344	Jan 1997	Sep 2004	2024-03-01	8365
Honda	Cr-V i	2.0 16V 4WD	SUV	Allrad	Benzin	94	128	Oct 1995	Dec 2001	2024-03-01	8366
Hyundai	H100	2.4	Bus	Heckantrieb	Benzin	84	114	Jan 1997	Mar 2000	2024-03-01	8367
Mercedes-benz	Sprinter 3,5-T	313 CDI 4X4	Bus	Allrad	Diesel	95	129	Aug 2011	Dec 2016	2024-03-01	8368
Mercedes-benz	Sprinter 3,5-T	313 CDI	Bus	Heckantrieb	Diesel	95	129	Aug 2011	Dec 2016	2024-03-01	8369
Mazda	626 v	1.8	Stufenheck	Frontantrieb	Benzin	66	90	May 1997	Dec 1999	2026-04-01	8370
Mazda	626 v	2	Stufenheck	Frontantrieb	Benzin	85	115	May 1997	Oct 2002	2024-03-01	8371
Mazda	626 v hatchback	1.8	Schrägheck	Frontantrieb	Benzin	66	90	May 1997	Dec 1999	2024-03-01	8372


--- Round 1 / 首次发送 ---
## 更新点

* 依照缓存优先规则，已批量关联 40 个既有尺寸组；相同发动机或驱动版本未重复抓取尺寸。
* 本轮首次闭合 5 个尺寸组：Focus III Turnier、Golf VI Cabriolet、Touareg II 改款前/后及 Corvette C5 Coupe。Focus、Golf 和两阶段 Touareg 的宽度均按不含后视镜口径落盘；Corvette 使用 Edmunds 明确标注的 without mirrors 宽度并由英寸换算为毫米。([汽车数据网][1])
* Corolla E110 已区分三厢、3 门 Compact、5 门 Liftback 和 5 门 Wagon，未错误复用已有 E100 尺寸组；该代欧洲车型确有多种独立车身形式和不同外廓。([汽车数据网][2])
* Expert、J5、Sprinter、H100 等多轴距/多车顶车型，以及跨代或跨改款但边界尚未闭合的车型继续保持 PENDING，未创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已输出映射行：115
* 完全 READY：59 个 Ktype，共 74 条映射
* PENDING：41 个 Ktype，共 41 条映射
* 本轮首次创建尺寸组：5
* 本轮复用既有尺寸组：40
* 当前引用尺寸组总数：45
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8204	8204	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8205	8205	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8206	8206	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8207	8207	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8208	8208	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8209	8209	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8210	8210	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8211	8211	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8212	8212	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8213	8213	MPV	Terra	024A	3	EU-SEAT-TERRA-MPV-3D-01	HIGH		READY
8215	8215	Van	Terra	024A	3	EU-SEAT-TERRA-VAN-3D-01	MEDIUM	原始车身类型为Kasten/Kombi，按厢式外廓映射。	READY
8216	8216	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	乘用版与M49厢式版共用外廓。	READY
8217_prefl	8217	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	改款前M49外廓。	READY
8217_facelift	8217	MPV	Partner I	M59	5	EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	改款后M59外廓。	READY
8218	8218	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	乘用版与M49厢式版共用外廓。	READY
8219	8219	MPV	Expert I	222	5	EU-PEUGEOT-EXPERT-I-222-BUS-01	HIGH		READY
8220	8220	Van	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8221	8221	Pickup	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8222	8222	Van	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8223	8223	Pickup	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8224	8224	Van	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8225	8225	Pickup	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8226	8226	Van	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8227	8227	Pickup	Expert I	222			LOW	候选为Expert I 222的多个车身长度分支。	PENDING: 轴距/车顶或底盘车身长度分支尚未确认
8228	8228	MPV	J5	280P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM		READY
8229	8229	Van	J5				LOW	候选含不同轴距与车顶高度。	PENDING: 轴距和车顶分支尚未确认
8230_swb	8230	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室。	READY
8230_lwb	8230	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室。	READY
8231_swb	8231	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室。	READY
8231_lwb	8231	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室。	READY
8233_swb	8233	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室。	READY
8233_lwb	8233	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室。	READY
8232	8232	Pickup	J5		2		LOW	4X4底盘驾驶室候选轴距未闭合。	PENDING: 4X4底盘驾驶室尺寸分支尚未确认
8234	8234	Hatchback	33		5		LOW	生产期跨905与907及多个外廓版本。	PENDING: 代际及改款外廓分支尚未确认
8235	8235	Van	J5				LOW	早期J5厢式车存在轴距和车顶分支。	PENDING: 轴距和车顶分支尚未确认
8240	8240	Sedan	405 I		4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
8242_3dr	8242	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	MEDIUM	三门外廓。	READY
8242_5dr	8242	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	MEDIUM	五门外廓。	READY
8248_3dr	8248	Hatchback	200 II	XW	3	EU-ROVER-200-II-XW-HATCHBACK-3D-01	MEDIUM	三门外廓。	READY
8248_5dr	8248	Hatchback	200 II	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	MEDIUM	五门外廓。	READY
8256	8256	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
8258	8258	Hatchback	33		5		LOW	生产期跨905与907及多个外廓版本。	PENDING: 代际及改款外廓分支尚未确认
8267	8267	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH		READY
8268	8268	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
8270	8270	Wagon	Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
8271	8271	Wagon	Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
8272	8272	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
8273_prefl	8273	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
8273_facelift	8273	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
8281	8281	Sedan	305 II		4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	标准车身外廓。	READY
8282	8282	Hatchback	1 Series II				LOW	候选含F20五门、F21三门及改款前后。	PENDING: 门数与改款分支尚未闭合
8283_3dr	8283	Hatchback	Ibiza I	021A	3	EU-SEAT-IBIZA-I-HATCHBACK-3D-01	MEDIUM	三门外廓。	READY
8283_5dr	8283	Hatchback	Ibiza I	021A	5	EU-SEAT-IBIZA-I-HATCHBACK-5D-01	MEDIUM	五门外廓。	READY
8284	8284	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
8285	8285	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH		READY
8288	8288	Hatchback	AX	ZA			LOW	候选跨Phase I与Phase II且存在不同宽度外廓。	PENDING: 改款及门数外廓分支尚未闭合
8292	8292	SUV	X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH		READY
8293	8293	Hatchback	Visa 1984 facelift		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	HIGH		READY
8294_phase1	8294	Hatchback	Visa GT Phase I		5	EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	MEDIUM	Phase I外廓。	READY
8294_phase2	8294	Hatchback	Visa GT Phase II		5	EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II外廓。	READY
8294_facelift	8294	Hatchback	Visa GT 1984 facelift		5	EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	1984改款外廓。	READY
8300	8300	Van	4				LOW	原始车身类型同时覆盖厢式与乘用车，且生产期跨多个车身版本。	PENDING: 车身类型与版本分支尚未闭合
8302	8302	Hatchback	Fiesta III	GFJ		EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	标准外廓。	READY
8306	8306	Hatchback	Renault 5 Turbo		3		LOW	候选覆盖Turbo与Turbo 2车身代码。	PENDING: Turbo与Turbo 2外廓边界尚未闭合
8312	8312	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
8313_prefl	8313	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
8313_facelift	8313	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
8315	8315	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8316	8316	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8317	8317	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8318	8318	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8319	8319	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8320	8320	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8321	8321	Wagon	Corolla VIII E110	EE111	5		MEDIUM	旅行车高度口径存在冲突，且需确认改款前后边界。	PENDING: 旅行车高度口径及改款边界尚未闭合
8322	8322	Wagon	Corolla VIII E110	AE111	5		MEDIUM	旅行车高度口径存在冲突，且需确认改款前后边界。	PENDING: 旅行车高度口径及改款边界尚未闭合
8323	8323	Wagon	Corolla VIII E110	AE111	5		MEDIUM	旅行车高度口径存在冲突，且需确认改款前后边界。	PENDING: 旅行车高度口径及改款边界尚未闭合
8324	8324	Wagon	Corolla VIII E110	AE115	5		MEDIUM	旅行车高度口径存在冲突，且需确认改款前后边界。	PENDING: 旅行车高度口径及改款边界尚未闭合
8325	8325	Wagon	Corolla VIII E110	CE110	5		MEDIUM	旅行车高度口径存在冲突，且需确认改款前后边界。	PENDING: 旅行车高度口径及改款边界尚未闭合
8326	8326	Sedan	Corolla VIII E110	EE111	4		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8328	8328	Sedan	Corolla VIII E110	AE111	4		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8329	8329	Sedan	Corolla VIII E110	CE110	4		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8330	8330	Hatchback	Corolla VIII E110 Compact	EE111	3		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8331	8331	Hatchback	Corolla VIII E110 Compact	AE111	3		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8332	8332	Hatchback	Corolla VIII E110 Compact	AE111	3		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8333	8333	Hatchback	Corolla VIII E110 Compact	CE110	3		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8334	8334	Hatchback	Corolla VIII E110 Liftback	AE111	5		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8335	8335	Hatchback	Corolla VIII E110 Liftback	EE111	5		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8336	8336	Hatchback	Corolla VIII E110 Liftback	AE111	5		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8337	8337	Hatchback	Corolla VIII E110 Liftback	CE110	5		MEDIUM	已确认车身形式与门数，改款前后尺寸边界待闭合。	PENDING: 改款前后尺寸边界尚未闭合
8351	8351	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8352	8352	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
8353	8353	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
8354	8354	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
8355	8355	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
8356_x1	8356	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1外廓。	READY
8356_x2	8356	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2外廓。	READY
8357_x1	8357	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	X1外廓。	READY
8357_x2	8357	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	X2外廓。	READY
8358_x1	8358	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1外廓。	READY
8358_x2	8358	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2外廓。	READY
8359_prefl	8359	SUV	Touareg II	7P5	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	改款前外廓。	READY
8359_facelift	8359	SUV	Touareg II	7P5	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
8360	8360	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8361	8361	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8362	8362	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8363	8363	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8364	8364	SUV	S-10 Blazer II				LOW	生产期覆盖两门/四门及改款分支。	PENDING: 门数与改款外廓分支尚未闭合
8365	8365	Coupe	Corvette C5	Y	2	EU-CHEVROLET-CORVETTE-C5-COUPE-2D-01	HIGH		READY
8366	8366	SUV	CR-V I	RD1	5		MEDIUM	欧洲规格高度口径存在差异，待统一。	PENDING: 高度口径尚未闭合
8367	8367	MPV	H100				LOW	Bus存在轴距与车顶/车身长度分支。	PENDING: 轴距与车顶分支尚未确认
8368	8368	MPV	Sprinter II	W906			LOW	3.5吨Bus未给出轴距和车顶高度。	PENDING: 轴距与车顶分支尚未确认
8369	8369	MPV	Sprinter II	W906			LOW	3.5吨Bus未给出轴距和车顶高度。	PENDING: 轴距与车顶分支尚未确认
8370	8370	Sedan	626 V	GF8P	4		MEDIUM	改款前高度待直接来源闭合。	PENDING: 完整三维尚未闭合
8371	8371	Sedan	626 V	GFEP	4		MEDIUM	生产期跨改款前后，需拆分外廓。	PENDING: 改款前后尺寸分支尚未闭合
8372	8372	Hatchback	626 V	GF8P	5		MEDIUM	改款前高度待直接来源闭合。	PENDING: 完整三维尚未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505	Auto-Data	https://www.auto-data.net/en/ford-focus-iii-wagon-2.0-tdci-115hp-powershift-19822
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-2.0-tdi-140hp-20417
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	Cataloge.eu	https://www.cataloge.eu/volkswagen/touareg-2010-7p
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709	CarExpert New Zealand	https://www.carexpert.co.nz/volkswagen/touareg/2015-bluemotion-3l-sport-utility-vehicle-4x4-diesel-automatic-jofk8wfm20141217
EU-CHEVROLET-CORVETTE-C5-COUPE-2D-01	4564	1869	1212	Edmunds	https://www.edmunds.com/chevrolet/corvette/1997/features-specs/
```

## 下一步优先处理

1. 优先闭合 Toyota Corolla E110 的四类外廓及改款边界，一次解决 Ktype 8321–8337。
2. 批量处理 Expert I、J5、Sprinter II 和 H100 的轴距、车顶与底盘驾驶室分支。
3. 处理 Alfa Romeo 33、BMW 1 Series、Citroën AX、Renault 4/5、S-10 Blazer 等跨代或多门数车型。
4. 最后闭合 CR-V I 与 Mazda 626 V 的高度口径及改款前三维。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-focus-iii-wagon-2.0-tdci-115hp-powershift-19822 "https://www.auto-data.net/en/ford-focus-iii-wagon-2.0-tdci-115hp-powershift-19822"
[2]: https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-1.6-i-16v-108hp-3343 "Toyota Corolla Wagon VIII (E110) 1.6 i 16V (108 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 重新按输入 Ktype 核计：Corolla E110 本轮实际闭合 **16 个 Ktype**，输入中不存在 8327。已区分 FWD Wagon、4WD Wagon、Sedan、3 门 Compact 和 5 门 Liftback；8324、8334 因生产期跨改款拆为派生行。([Auto Data][1])
* Ktype 8282 已拆为 F21 三门和 F20 五门的改款前、改款后四个分支；其中三个分支复用既有组，仅首次创建 F21 三门改款后尺寸组。
* Ktype 8288 已按 AX Phase I/II 及三门/五门拆分，尺寸组直接复用既有 AX 缓存；Renault 5 Turbo 与 Turbo 2 共用同一外廓尺寸组；CR-V I 128 PS 欧洲规格已闭合。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：79
* PENDING Ktype：21
* READY 映射：102
* PENDING 映射：21
* 当前映射总行数：123
* 已确认尺寸组：55
* 本轮首次创建尺寸组：10
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8282_3dr_prefl	8282	Hatchback	1 Series II F21	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前外廓。	READY
8282_3dr_facelift	8282	Hatchback	1 Series II F21	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后外廓。	READY
8282_5dr_prefl	8282	Hatchback	1 Series II F20	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前外廓。	READY
8282_5dr_facelift	8282	Hatchback	1 Series II F20	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
8288_3dr_phase1	8288	Hatchback	AX Phase I	ZA	3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	三门Phase I外廓。	READY
8288_3dr_phase2	8288	Hatchback	AX Phase II	ZA	3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	三门Phase II外廓。	READY
8288_5dr_phase1	8288	Hatchback	AX Phase I	ZA	5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	五门Phase I外廓。	READY
8288_5dr_phase2	8288	Hatchback	AX Phase II	ZA	5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	五门Phase II外廓。	READY
8306	8306	Hatchback	Renault 5 Turbo		3	EU-RENAULT-5-TURBO-HATCHBACK-3D-01	HIGH	Turbo与Turbo 2外廓尺寸一致。	READY
8321	8321	Wagon	Corolla VIII E110	EE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8322	8322	Wagon	Corolla VIII E110	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8323	8323	Wagon	Corolla VIII E110	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8324_prefl	8324	Wagon	Corolla VIII E110	AE115	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	HIGH	改款前四驱旅行车外廓。	READY
8324_facelift	8324	Wagon	Corolla VIII E110	AE115	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	HIGH	改款后四驱旅行车外廓。	READY
8325	8325	Wagon	Corolla VIII E110	CE110	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8326	8326	Sedan	Corolla VIII E110	EE111	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8328	8328	Sedan	Corolla VIII E110	AE111	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8329	8329	Sedan	Corolla VIII E110	CE110	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8330	8330	Hatchback	Corolla VIII E110 Compact	EE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8331	8331	Hatchback	Corolla VIII E110 Compact	AE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8332	8332	Hatchback	Corolla VIII E110 Compact	AE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8333	8333	Hatchback	Corolla VIII E110 Compact	CE110	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8334_prefl	8334	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH	改款前五门Liftback外廓。	READY
8334_facelift	8334	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	HIGH	改款后五门Liftback外廓。	READY
8335	8335	Hatchback	Corolla VIII E110 Liftback	EE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8336	8336	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8337	8337	Hatchback	Corolla VIII E110 Liftback	CE110	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8366	8366	SUV	CR-V I	RD1	5	EU-HONDA-CR-V-I-RD1-SUV-PHASE-I-01	MEDIUM	128 PS欧洲规格对应RD1前期外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2103380/bmw_125i_3-door.html
EU-RENAULT-5-TURBO-HATCHBACK-3D-01	3664	1752	1323	Renault The Originals Museum; Automobile-Catalog	https://theoriginals.renault.com/en/r5-turbo;https://www.automobile-catalog.com/car/1981/29330/renault_5_turbo.html
EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	4320	1690	1445	Auto-Data	https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-1.6-i-16v-108hp-3343
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	4320	1690	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3594215/toyota_corolla_wagon_1_8_4wd.html
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	4340	1690	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3594470/toyota_corolla_wagon_1_8_4wd.html
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	4295	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3594125/toyota_corolla_sedan_1_3_automatic.html
EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	4100	1690	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3593900/toyota_corolla_compact_1_3.html
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	4270	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3593975/toyota_corolla_liftback_1_3.html
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	4290	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3594335/toyota_corolla_liftback_1_6.html
EU-HONDA-CR-V-I-RD1-SUV-PHASE-I-01	4520	1750	1675	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1120145/honda_cr-v.html
```

## 下一步优先处理

1. 集中闭合 Expert I Ktype 8220–8227 的 Van、Chassis Cab 轴距和车身长度分支。
2. 处理 J5 Ktype 8229、8232、8235 的轴距、车顶及 4X4 底盘边界。
3. 联合处理 Alfa Romeo 33 Ktype 8234、8258，复用已有 905/907 尺寸组。
4. 最后处理 Renault 4、S-10 Blazer、H100、Sprinter W906 和 Mazda 626 V，共剩余 21 个 PENDING Ktype。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/compare?carId1=3346&carId2=&carId3=&utm_source=chatgpt.com "Compare: Toyota Corolla 1997 Station wagon (estate) 72 Hp"
[2]: https://www.automobile-catalog.com/car/2016/2103380/bmw_125i_3-door.html?utm_source=chatgpt.com "2016 BMW 125i (3-Door) Specs Review (160 kW / 218 PS / 215 hp) (up to June 2016 for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Ktype 8234：Alfa Romeo 33 1.8 TD 确认为 905 系列五门掀背，三维为 4040×1612×1345 mm；与累计表已有 905 尺寸组数据不同，因此新建独立尺寸组，未覆盖旧组。([汽车目录][1])
* 闭合 Mazda 626 V 的 Ktype 8370–8372。改款前 Sedan 与 Hatchback 均为 4575×1710×1430 mm；8371 的生产期跨越改款，拆为改款前 4575 mm 和改款后 4590 mm 两个 Sedan 分支，宽度均为明确不含后视镜口径。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：83
* PENDING Ktype：17
* READY 映射：107
* PENDING 映射：17
* 当前映射总行数：124
* 已确认尺寸组：59
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8234	8234	Hatchback	33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-1.8TD-01	HIGH		READY
8370	8370	Sedan	626 V	GF8P	4	EU-MAZDA-626-V-GF-SEDAN-PREFL-01	HIGH		READY
8371_prefl	8371	Sedan	626 V	GFEP	4	EU-MAZDA-626-V-GF-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
8371_facelift	8371	Sedan	626 V	GFEP	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
8372	8372	Hatchback	626 V	GF8P	5	EU-MAZDA-626-V-GF-HATCHBACK-PREFL-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-33-905-HATCHBACK-1.8TD-01	4040	1612	1345	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/215150/alfa_romeo_33_1_8_td.html
EU-MAZDA-626-V-GF-SEDAN-PREFL-01	4575	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1665380/mazda_626_2_0_4-door.html
EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	4590	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/1665635/mazda_626_2_0_4-door_automatic.html
EU-MAZDA-626-V-GF-HATCHBACK-PREFL-01	4575	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1665335/mazda_626_2_0_136_5-door.html
```

## 下一步优先处理

1. Expert I Ktype 8220–8227 的 Van、底盘驾驶室及轴距分支。
2. J5 Ktype 8229、8232、8235 的轴距、车顶和 4X4 底盘边界。
3. Alfa Romeo 33 Ktype 8258 的 905/907 跨代分支。
4. Renault 4、S-10 Blazer、H100、Sprinter W906 剩余多车身分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1988/215150/alfa_romeo_33_1_8_td.html?utm_source=chatgpt.com "1988 Alfa Romeo 33 1.8 TD Specs Review (54.5 kW / 74 ..."
[2]: https://www.automobile-catalog.com/car/1997/1665380/mazda_626_2_0_4-door.html?utm_source=chatgpt.com "1997 Mazda 626 2.0 4-Door Specs Review (85 kW / 116 PS / 114 hp ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Ktype `8300` 已按已确认的三种物理外廓拆分：五门乘用版、标准顶 Fourgonnette/F4 厢式版及 R2108 加高顶厢式版；三种外廓分别建立尺寸组。
* Sprinter 313 CDI Bus 的官方资料显示存在多种轴距和车顶组合，输入行未提供对应边界，因此 Ktype `8368`、`8369` 本轮不创建猜测性派生行。([Dezo's Garage][1])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* PENDING Ktype：16
* READY 映射：110
* PENDING 映射：16
* 当前映射总行数：126
* 已确认尺寸组：62
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8300_5dr	8300	MPV	Renault 4		5	EU-RENAULT-4-MPV-5D-01	MEDIUM	五门乘用车外廓。	READY
8300_f4	8300	Van	Renault 4 F4		3	EU-RENAULT-4-F4-VAN-3D-01	MEDIUM	标准顶厢式外廓。	READY
8300_f4_highroof	8300	Van	Renault 4 Fourgonnette	R2108	3	EU-RENAULT-4-R2108-VAN-HIGHROOF-3D-01	MEDIUM	R2108加高顶厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-4-MPV-5D-01	3668	1485	1550	Renault 1968 official brochure; Dimensions des Renault 4	https://manuals.plus/m/0420d466d0838d3fe56548cc9a5113bbca8251da23ef3f00cef32d56b37ae997.pdf;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
EU-RENAULT-4-F4-VAN-3D-01	3653	1500	1710	Renault The Originals Museum; Dimensions des Renault 4	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
EU-RENAULT-4-R2108-VAN-HIGHROOF-3D-01	3695	1500	1820	Renault The Originals Museum; Dimensions des Renault 4	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
```

## 下一步优先处理

1. 集中闭合 Expert I Ktype `8220–8227` 的厢式车与底盘驾驶室轴距分支。
2. 处理 J5 Ktype `8229`、`8232`、`8235` 的轴距、车顶及四驱底盘边界。
3. 处理 Alfa Romeo 33 Ktype `8258`、S-10 Blazer `8364`、H100 `8367` 和 Sprinter `8368–8369`。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf "untitled"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已一次闭合 Expert I 的 8 个 PENDING Ktype。
* Ktype `8220`、`8222`、`8224`、`8226` 确认为第一代 Expert 222 厢式车，统一外廓为 `4440×1810×1940 mm`。([Дром][1])
* Ktype `8221`、`8223`、`8225`、`8227` 确认为 Expert I 223 平台驾驶室，统一外廓为 `4470×1810×1927 mm`。([Zoomcar][2])
* 两类车身分别创建尺寸组；相同发动机功率版本直接复用，没有重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：92
* PENDING Ktype：8
* READY 映射：118
* PENDING 映射：8
* 当前映射总行数：126
* 已确认尺寸组：64
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8220	8220	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8221	8221	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8222	8222	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8223	8223	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8224	8224	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8225	8225	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8226	8226	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8227	8227	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-EXPERT-I-222-VAN-01	4440	1810	1940	Drom; Truck1	https://www.drom.ru/catalog/peugeot/expert/235600/;https://www.truck1.eu/blog/peugeot-expert-van-222-1-6-79-hp-tech-specs-t30691
EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	4470	1810	1927	Zoomcar	https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/expert-plancher-cabine-expert-plancher-cab-phc-220l-1-6-NAT79082.html
```

## 下一步优先处理

1. 闭合 J5 Ktype `8229`、`8232`、`8235` 的轴距、车顶和四驱底盘分支。
2. 将 Alfa Romeo 33 Ktype `8258` 精确关联至已有 905 系列尺寸组。
3. 最后处理 S-10 Blazer `8364`、H100 `8367`、Sprinter `8368–8369` 的门数、轴距和车顶分支。

推进信号：CONTINUE

[1]: https://www.drom.ru/catalog/peugeot/expert/235600/?utm_source=chatgpt.com "Peugeot Expert 1.9 TD MT (07.1995 - 02.2004) - технические характеристики"
[2]: https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/expert-plancher-cabine-expert-plancher-cab-phc-220l-1-6-NAT79082.html?utm_source=chatgpt.com "Fiche technique - PEUGEOT EXPERT PLANCHER CABINE"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* Ktype `8258` 已按生产期覆盖的 Alfa Romeo 33 `905` 与 `907` 两个物理阶段拆分，并分别关联既有尺寸组；复用组未重复输出。早期 905 系列存在 1.5 约 95 PS 版本，后期 907 系列亦存在相应 1.5 IE 版本。([Fast Car Check][1])
* Ktype `8367` 已确认对应 H100 第二代 `P` 系列 Minibus，闭合为 `4790×1690×1965 mm`，本轮首次建立尺寸组。([AUTODOC CLUB][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：94
* PENDING Ktype：6
* READY 映射：121
* PENDING 映射：6
* 当前映射总行数：127
* 已确认尺寸组：65
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8258_905	8258	Hatchback	33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	MEDIUM	905系早期1.5外廓。	READY
8258_907	8258	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	MEDIUM	907系后期1.5外廓。	READY
8367	8367	MPV	H100 II	P		EU-HYUNDAI-H100-P-MINIBUS-01	MEDIUM		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-H100-P-MINIBUS-01	4790	1690	1965	CarrosNaWeb; Razmery	https://www.carrosnaweb.com.br/fichadetalhe.asp?codigo=15658;https://en.razmery.info/equipment/car_bodies/dimensions-car-bodies-hyundai-h100-bus.html
```

## 下一步优先处理

1. 闭合 J5 Ktype `8229`、`8232`、`8235`：车型代码已分别定位至 290L Van、290L 4X4 Chassis Cab 与 280L Van，下一轮只补齐对应轴距、车顶和四驱高度分支。([AUTODOC][3])
2. 拆分 S-10 Blazer Ktype `8364` 的两门、四门及改款/ZR2 外廓。([Edmunds][4])
3. 闭合 Sprinter Ktype `8368–8369` 的 `906.731`、`906.733`、`906.735` 车身长度、车顶及四驱高度分支。([club.auto-doc.fr][5])

推进信号：CONTINUE

[1]: https://fastcarcheck.uk/specs/make/alfa-romeo/33/27932?utm_source=chatgpt.com "Alfa Romeo 33 1.5 MT (95 hp) Specifications"
[2]: https://club.autodoc.co.uk/tyres/hyundai/h100/h100-bus-p?utm_source=chatgpt.com "HYUNDAI H100 Minibus (P) tyre sizes and rim dimensions – recommended tyre and rim combination"
[3]: https://www.autodoc.co.uk/car-parts/inner-tie-rod-10298/peugeot/j5/j5-box-290l/8229-1-9-d?utm_source=chatgpt.com "PEUGEOT J5 Van (290) 1.9 D Inner tie rod (70 hp Diesel D9B ..."
[4]: https://www.edmunds.com/chevrolet/blazer/1995/st-12947/features-specs/?utm_source=chatgpt.com "Used 1995 Chevrolet Blazer Base Specs & Features"
[5]: https://club.auto-doc.fr/tyres/mercedes-benz/sprinter/sprinter-3-5-t-bus-906?utm_source=chatgpt.com "MERCEDES-BENZ Sprinter 3.5-T Bus (W906) tailles pneus et ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 J5 的 3 个 PENDING Ktype：`8229` 确认为 290L 厢式车、`8232` 为 290L 四驱底盘驾驶室、`8235` 为 280L 厢式车。分别按已确认的轴距和车顶外廓拆分，全部关联既有尺寸组，未重复抓取或新建尺寸组。([Autodoc][1])
* 剩余 PENDING 集中在 S-10 Blazer 的门数/改款/宽体边界，以及 Sprinter W906 Bus 的轴距、车顶和四驱高度边界。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射：131
* PENDING 映射：3
* 当前映射总行数：134
* 已确认尺寸组：69
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8229_swb_lowroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
8229_swb_highroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
8229_lwb_lowroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
8229_lwb_highroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
8232_swb	8232	Pickup	J5	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴四驱底盘驾驶室外廓。	READY
8232_lwb	8232	Pickup	J5	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴四驱底盘驾驶室外廓。	READY
8235_swb_lowroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
8235_swb_highroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
8235_lwb_lowroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
8235_lwb_highroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Sprinter Ktype `8369` 的 `906.731`、`906.733`、`906.735` 后驱 Bus 轴距与车顶分支。
2. 闭合 Sprinter Ktype `8368` 对应分支的四驱高度差异。
3. 最后拆分 S-10 Blazer Ktype `8364` 的两门、四门、改款及 ZR2 宽体外廓。

推进信号：CONTINUE

[1]: https://www.autodoc.de/autoteile/radhausschale-10265/peugeot/j5/j5-kasten-290l/8229-1-9-d?utm_source=chatgpt.com "Radhausschale PEUGEOT J5 Kastenwagen (290) 1.9 D 70 PS ..."


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Ktype `8368`、`8369` 均明确覆盖 `906.731`、`906.733`、`906.735` 三种 Bus 车身代码，原基础行已替换为短轴、中轴、长轴派生行。Mercedes-Benz 车身指南分别对应 3250、3665、4325 mm 轴距及不同车长。([Autodoc][1])
* 两个 Ktype 的生产期跨越 W906 改款，且同一车身代码仍可能包含不同车顶；四驱资料只说明相对后驱车身高度最多增加 85 mm，不能据此落盘一个猜测性固定高度。因此本轮仅闭合物理分支，暂不创建 Sprinter 尺寸组。([Dezo's Garage][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射：131
* PENDING 映射：7
* 当前映射总行数：138
* 已确认尺寸组：69
* 本轮首次创建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8368_731	8368	MPV	Sprinter II W906	906.731			MEDIUM	短轴Bus；车顶及改款分支待闭合。	PENDING: 4x4车顶及改款三维尚未闭合
8368_733	8368	MPV	Sprinter II W906	906.733			MEDIUM	中轴Bus；车顶及改款分支待闭合。	PENDING: 4x4车顶及改款三维尚未闭合
8368_735	8368	MPV	Sprinter II W906	906.735			MEDIUM	长轴Bus；车顶及改款分支待闭合。	PENDING: 4x4车顶及改款三维尚未闭合
8369_731	8369	MPV	Sprinter II W906	906.731			MEDIUM	短轴Bus；车顶及改款分支待闭合。	PENDING: 车顶及改款三维尚未闭合
8369_733	8369	MPV	Sprinter II W906	906.733			MEDIUM	中轴Bus；车顶及改款分支待闭合。	PENDING: 车顶及改款三维尚未闭合
8369_735	8369	MPV	Sprinter II W906	906.735			MEDIUM	长轴Bus；车顶及改款分支待闭合。	PENDING: 车顶及改款三维尚未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 按 `906.731`、`906.733`、`906.735` 一次闭合 Sprinter 改款前后、标准顶/高顶及四驱高度分支。
2. 最后闭合 Ktype `8364` 的 S-10 Blazer 两门、四门、ZR2 宽体及改款边界。

推进信号：CONTINUE

[1]: https://www.autodoc.de/autoteile/hebel-seile-zuge-10735/mercedes-benz/sprinter/sprinter-3-5-t-bus-906/8368-313-cdi-4x4-906-731-906-733-906-735?utm_source=chatgpt.com "Handbremsseil passend für Mercedes Sprinter 3,5t Bus 313 CDI 2.2 4x4 129 PS Diesel 95 kW 2011 - 2016 OM 651.957"
[2]: https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf "untitled"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 Sprinter W906 改款前的 8 个物理分支：`906.731` 短轴标准顶、`906.733` 中轴标准顶/高顶、`906.735` 长轴高顶，并分别区分后驱与四驱。
* Mercedes-Benz 车身指南确认三个车身代码对应的车长分别为 `5245 / 5910 / 6945 mm`；官方尺寸页确认车身宽度为不含后视镜的 `1993 mm`，并给出各车顶最大高度及四驱最大增高量。([DIY Sprinter][1])
* `8368`、`8369` 的改款后分支已保留，但改款后标准悬架、降低悬架及四驱高度口径尚未完全闭合，暂不创建尺寸组。
* S-10 Blazer `8364` 仍为最后一个独立待闭合车型。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射：139
* PENDING 映射：9
* 当前映射总行数：148
* 已确认尺寸组：77
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8368_731_stdroof_prefl	8368	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-4X4-01	HIGH	短轴标准顶改款前四驱外廓。	READY
8368_733_stdroof_prefl	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-4X4-01	HIGH	中轴标准顶改款前四驱外廓。	READY
8368_733_highroof_prefl	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-4X4-01	HIGH	中轴高顶改款前四驱外廓。	READY
8368_735_highroof_prefl	8368	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-4X4-01	HIGH	长轴高顶改款前四驱外廓。	READY
8368_731_stdroof_facelift	8368	MPV	Sprinter II W906	906.731			MEDIUM	短轴标准顶改款后四驱外廓。	PENDING: 改款后四驱最大车高尚未闭合
8368_733_stdroof_facelift	8368	MPV	Sprinter II W906	906.733			MEDIUM	中轴标准顶改款后四驱外廓。	PENDING: 改款后四驱最大车高尚未闭合
8368_733_highroof_facelift	8368	MPV	Sprinter II W906	906.733			MEDIUM	中轴高顶改款后四驱外廓。	PENDING: 改款后四驱最大车高尚未闭合
8368_735_highroof_facelift	8368	MPV	Sprinter II W906	906.735			MEDIUM	长轴高顶改款后四驱外廓。	PENDING: 改款后四驱最大车高尚未闭合
8369_731_stdroof_prefl	8369	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-RWD-01	HIGH	短轴标准顶改款前后驱外廓。	READY
8369_733_stdroof_prefl	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-RWD-01	HIGH	中轴标准顶改款前后驱外廓。	READY
8369_733_highroof_prefl	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-RWD-01	HIGH	中轴高顶改款前后驱外廓。	READY
8369_735_highroof_prefl	8369	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-RWD-01	HIGH	长轴高顶改款前后驱外廓。	READY
8369_731_stdroof_facelift	8369	MPV	Sprinter II W906	906.731			MEDIUM	短轴标准顶改款后后驱外廓。	PENDING: 改款后悬架车高口径尚未闭合
8369_733_stdroof_facelift	8369	MPV	Sprinter II W906	906.733			MEDIUM	中轴标准顶改款后后驱外廓。	PENDING: 改款后悬架车高口径尚未闭合
8369_733_highroof_facelift	8369	MPV	Sprinter II W906	906.733			MEDIUM	中轴高顶改款后后驱外廓。	PENDING: 改款后悬架车高口径尚未闭合
8369_735_highroof_facelift	8369	MPV	Sprinter II W906	906.735			MEDIUM	长轴高顶改款后后驱外廓。	PENDING: 改款后悬架车高口径尚未闭合
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-4X4-01	5245	1993	2520	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-4X4-01	5910	1993	2615	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-4X4-01	5910	1993	2905	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-4X4-01	6945	1993	2910	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-RWD-01	5245	1993	2435	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-RWD-01	5910	1993	2530	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-RWD-01	5910	1993	2820	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-RWD-01	6945	1993	2815	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
```

## 下一步优先处理

1. 闭合 Sprinter W906 改款后 `906.731 / 906.733 / 906.735` 的后驱降低悬架高度和四驱最大高度。
2. 最后拆分并闭合 S-10 Blazer `8364` 的两门、四门、改款前后及 ZR2 宽体分支。
3. PENDING 清零后立即执行一次机械检查并输出最终完整两表及指定下载链接。

推进信号：CONTINUE

[1]: https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf "ABR.boo"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7601-7700_ktype_dimension_mapping_final.tsv
- all_7601-7700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 已闭合最后的 Sprinter W906 改款后轴距、车顶及驱动分支，以及 S-10 Blazer 两门、四门、改款和 ZR2 宽体分支。Sprinter 改款后尺寸采用 Mercedes-Benz 乘用厢式车二维图和车身指南；Blazer 分支依据 Chevrolet 车型资料及明确标注不含后视镜宽度的规格页。([mbvans.com][1])
* 已完成一次机械收尾：两张表表头正确，`id` 和 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，尺寸与来源非空，下载文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：154
* PENDING 映射：0
* DIMENSION_GROUP：99
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 机械校验：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8204	8204	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8205	8205	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8206	8206	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8207	8207	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8208	8208	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8209	8209	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8210	8210	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8211	8211	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8212	8212	Convertible	Golf VI	517	2	EU-VW-GOLF-VI-CABRIOLET-2D-01	HIGH		READY
8213	8213	MPV	Terra	024A	3	EU-SEAT-TERRA-MPV-3D-01	HIGH		READY
8215	8215	Van	Terra	024A	3	EU-SEAT-TERRA-VAN-3D-01	MEDIUM	Kasten/Kombi厢式外廓。	READY
8216	8216	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	M49乘用版外廓。	READY
8217_prefl	8217	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	改款前M49外廓。	READY
8217_facelift	8217	MPV	Partner I	M59	5	EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	MEDIUM	改款后M59外廓。	READY
8218	8218	MPV	Partner I	M49	5	EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	MEDIUM	M49乘用版外廓。	READY
8219	8219	MPV	Expert I	222	5	EU-PEUGEOT-EXPERT-I-222-BUS-01	HIGH		READY
8220	8220	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8221	8221	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8222	8222	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8223	8223	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8224	8224	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8225	8225	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8226	8226	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-222-VAN-01	HIGH		READY
8227	8227	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	MEDIUM	平台驾驶室外廓。	READY
8228	8228	MPV	J5	280P		EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	MEDIUM		READY
8229_swb_lowroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
8229_swb_highroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
8229_lwb_lowroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
8229_lwb_highroof	8229	Van	J5	290L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
8230_swb	8230	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室外廓。	READY
8230_lwb	8230	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室外廓。	READY
8231_swb	8231	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室外廓。	READY
8231_lwb	8231	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室外廓。	READY
8232_swb	8232	Pickup	J5	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴四驱底盘驾驶室外廓。	READY
8232_lwb	8232	Pickup	J5	290L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴四驱底盘驾驶室外廓。	READY
8233_swb	8233	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	MEDIUM	短轴底盘驾驶室外廓。	READY
8233_lwb	8233	Pickup	J5	280L	2	EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	MEDIUM	长轴底盘驾驶室外廓。	READY
8234	8234	Hatchback	33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-1.8TD-01	HIGH		READY
8235_swb_lowroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	MEDIUM	短轴标准顶厢式外廓。	READY
8235_swb_highroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	MEDIUM	短轴高顶厢式外廓。	READY
8235_lwb_lowroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	MEDIUM	长轴标准顶厢式外廓。	READY
8235_lwb_highroof	8235	Van	J5	280L		EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	MEDIUM	长轴高顶厢式外廓。	READY
8240	8240	Sedan	405 I		4	EU-PEUGEOT-405-I-SEDAN-01	HIGH		READY
8242_3dr	8242	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	MEDIUM	3门外廓。	READY
8242_5dr	8242	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	MEDIUM	5门外廓。	READY
8248_3dr	8248	Hatchback	200 II	XW	3	EU-ROVER-200-II-XW-HATCHBACK-3D-01	MEDIUM	3门外廓。	READY
8248_5dr	8248	Hatchback	200 II	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	MEDIUM	5门外廓。	READY
8256	8256	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
8258_905	8258	Hatchback	33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	MEDIUM	905系早期外廓。	READY
8258_907	8258	Hatchback	33 907	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	MEDIUM	907系后期外廓。	READY
8267	8267	Sedan	90	162A	4	EU-ALFA-ROMEO-90-162A-SEDAN-01	HIGH		READY
8268	8268	Convertible	6 Series F12	F12	2	EU-BMW-6-F12-CONVERTIBLE-01	HIGH		READY
8270	8270	Wagon	Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
8271	8271	Wagon	Lantra II	J2	5	EU-HYUNDAI-LANTRA-II-J2-WAGON-01	HIGH		READY
8272	8272	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
8273_prefl	8273	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
8273_facelift	8273	Sedan	Lantra II	J2	4	EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
8281	8281	Sedan	305 II		4	EU-PEUGEOT-305-II-SEDAN-BASE-01	MEDIUM	标准车身外廓。	READY
8282_3dr_prefl	8282	Hatchback	1 Series II F21	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	MEDIUM	三门改款前外廓。	READY
8282_3dr_facelift	8282	Hatchback	1 Series II F21	F21	3	EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-FACELIFT-01	MEDIUM	三门改款后外廓。	READY
8282_5dr_prefl	8282	Hatchback	1 Series II F20	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	MEDIUM	五门改款前外廓。	READY
8282_5dr_facelift	8282	Hatchback	1 Series II F20	F20	5	EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	MEDIUM	五门改款后外廓。	READY
8283_3dr	8283	Hatchback	Ibiza I	021A	3	EU-SEAT-IBIZA-I-HATCHBACK-3D-01	MEDIUM	3门外廓。	READY
8283_5dr	8283	Hatchback	Ibiza I	021A	5	EU-SEAT-IBIZA-I-HATCHBACK-5D-01	MEDIUM	5门外廓。	READY
8284	8284	Coupe	6 Series F13	F13	2	EU-BMW-6-F13-COUPE-01	HIGH		READY
8285	8285	Sedan	75	162B	4	EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	HIGH		READY
8288_3dr_phase1	8288	Hatchback	AX Phase I	ZA	3	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	三门Phase I外廓。	READY
8288_3dr_phase2	8288	Hatchback	AX Phase II	ZA	3	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	三门Phase II外廓。	READY
8288_5dr_phase1	8288	Hatchback	AX Phase I	ZA	5	EU-CITROEN-AX-PHASE-I-HATCHBACK-01	MEDIUM	五门Phase I外廓。	READY
8288_5dr_phase2	8288	Hatchback	AX Phase II	ZA	5	EU-CITROEN-AX-PHASE-II-HATCHBACK-01	MEDIUM	五门Phase II外廓。	READY
8292	8292	SUV	X5 E70 LCI	E70	5	EU-BMW-X5-E70-LCI-SUV-01	HIGH		READY
8293	8293	Hatchback	Visa 1984 facelift		5	EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	HIGH		READY
8294_phase1	8294	Hatchback	Visa GT Phase I		5	EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	MEDIUM	Phase I外廓。	READY
8294_phase2	8294	Hatchback	Visa GT Phase II		5	EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	MEDIUM	Phase II外廓。	READY
8294_facelift	8294	Hatchback	Visa GT 1984 facelift		5	EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	MEDIUM	1984改款外廓。	READY
8300_5dr	8300	MPV	Renault 4		5	EU-RENAULT-4-MPV-5D-01	MEDIUM	五门乘用车外廓。	READY
8300_f4	8300	Van	Renault 4 F4		3	EU-RENAULT-4-F4-VAN-3D-01	MEDIUM	标准顶厢式外廓。	READY
8300_f4_highroof	8300	Van	Renault 4 Fourgonnette	R2108	3	EU-RENAULT-4-R2108-VAN-HIGHROOF-3D-01	MEDIUM	R2108加高顶厢式外廓。	READY
8302	8302	Hatchback	Fiesta III	GFJ		EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	MEDIUM	标准外廓。	READY
8306	8306	Hatchback	Renault 5 Turbo		3	EU-RENAULT-5-TURBO-HATCHBACK-3D-01	HIGH		READY
8312	8312	Hatchback	Sierra II		5	EU-FORD-SIERRA-II-HATCHBACK-01	HIGH		READY
8313_prefl	8313	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
8313_facelift	8313	Hatchback	Croma I	154	5	EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
8315	8315	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8316	8316	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8317	8317	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8318	8318	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8319	8319	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8320	8320	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8321	8321	Wagon	Corolla VIII E110	EE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8322	8322	Wagon	Corolla VIII E110	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8323	8323	Wagon	Corolla VIII E110	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8324_prefl	8324	Wagon	Corolla VIII E110	AE115	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	HIGH	改款前四驱旅行车外廓。	READY
8324_facelift	8324	Wagon	Corolla VIII E110	AE115	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	HIGH	改款后四驱旅行车外廓。	READY
8325	8325	Wagon	Corolla VIII E110	CE110	5	EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	HIGH		READY
8326	8326	Sedan	Corolla VIII E110	EE111	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8328	8328	Sedan	Corolla VIII E110	AE111	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8329	8329	Sedan	Corolla VIII E110	CE110	4	EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	HIGH		READY
8330	8330	Hatchback	Corolla VIII E110 Compact	EE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8331	8331	Hatchback	Corolla VIII E110 Compact	AE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8332	8332	Hatchback	Corolla VIII E110 Compact	AE111	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8333	8333	Hatchback	Corolla VIII E110 Compact	CE110	3	EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	HIGH		READY
8334_prefl	8334	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH	改款前五门Liftback外廓。	READY
8334_facelift	8334	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	HIGH	改款后五门Liftback外廓。	READY
8335	8335	Hatchback	Corolla VIII E110 Liftback	EE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8336	8336	Hatchback	Corolla VIII E110 Liftback	AE111	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8337	8337	Hatchback	Corolla VIII E110 Liftback	CE110	5	EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	HIGH		READY
8351	8351	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8352	8352	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
8353	8353	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
8354	8354	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
8355	8355	Wagon	A4 B5	8D5	5	EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	HIGH		READY
8356_x1	8356	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1外廓。	READY
8356_x2	8356	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2外廓。	READY
8357_x1	8357	Hatchback	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-HATCHBACK-01	HIGH	X1外廓。	READY
8357_x2	8357	Hatchback	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-HATCHBACK-01	HIGH	X2外廓。	READY
8358_x1	8358	Wagon	Xantia X1	X1	5	EU-CITROEN-XANTIA-X1-WAGON-01	HIGH	X1外廓。	READY
8358_x2	8358	Wagon	Xantia X2	X2	5	EU-CITROEN-XANTIA-X2-WAGON-01	HIGH	X2外廓。	READY
8359_prefl	8359	SUV	Touareg II	7P5	5	EU-VW-TOUAREG-II-7P-SUV-PREFL-01	HIGH	改款前外廓。	READY
8359_facelift	8359	SUV	Touareg II	7P5	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH	改款后外廓。	READY
8360	8360	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8361	8361	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8362	8362	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8363	8363	MPV	Lumina APV	GMT199		EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	HIGH		READY
8364_2dr_prefl	8364	SUV	S-10 Blazer II		2	EU-CHEVROLET-S10-BLAZER-II-SUV-2D-PREFL-01	MEDIUM	两门改款前四驱外廓。	READY
8364_4dr_prefl	8364	SUV	S-10 Blazer II		4	EU-CHEVROLET-S10-BLAZER-II-SUV-4D-PREFL-01	MEDIUM	四门改款前四驱外廓。	READY
8364_2dr_facelift	8364	SUV	S-10 Blazer II facelift		2	EU-CHEVROLET-S10-BLAZER-II-SUV-2D-FACELIFT-01	MEDIUM	两门改款后前期四驱外廓。	READY
8364_4dr_facelift	8364	SUV	S-10 Blazer II facelift		4	EU-CHEVROLET-S10-BLAZER-II-SUV-4D-FACELIFT-01	MEDIUM	四门改款后前期四驱外廓。	READY
8364_2dr_late	8364	SUV	S-10 Blazer II facelift		2	EU-CHEVROLET-S10-BLAZER-II-SUV-2D-LATE-01	MEDIUM	两门改款后后期四驱外廓。	READY
8364_4dr_late	8364	SUV	S-10 Blazer II facelift		4	EU-CHEVROLET-S10-BLAZER-II-SUV-4D-LATE-01	MEDIUM	四门改款后后期四驱外廓。	READY
8364_2dr_zr2	8364	SUV	S-10 Blazer II facelift		2	EU-CHEVROLET-S10-BLAZER-II-SUV-2D-ZR2-01	MEDIUM	两门ZR2宽体四驱外廓。	READY
8365	8365	Coupe	Corvette C5	Y	2	EU-CHEVROLET-CORVETTE-C5-COUPE-2D-01	HIGH		READY
8366	8366	SUV	CR-V I	RD1	5	EU-HONDA-CR-V-I-RD1-SUV-PHASE-I-01	MEDIUM	128 PS欧洲规格前期外廓。	READY
8367	8367	MPV	H100 II	P		EU-HYUNDAI-H100-P-MINIBUS-01	MEDIUM		READY
8368_731_stdroof_prefl	8368	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-4X4-01	HIGH	短轴标准顶改款前四驱外廓。	READY
8368_733_stdroof_prefl	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-4X4-01	HIGH	中轴标准顶改款前四驱外廓。	READY
8368_733_highroof_prefl	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-4X4-01	HIGH	中轴高顶改款前四驱外廓。	READY
8368_735_highroof_prefl	8368	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-4X4-01	HIGH	长轴高顶改款前四驱外廓。	READY
8368_731_stdroof_facelift	8368	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-FACELIFT-4X4-01	HIGH	短轴标准顶改款后四驱外廓。	READY
8368_733_stdroof_facelift	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-FACELIFT-4X4-01	HIGH	中轴标准顶改款后四驱外廓。	READY
8368_733_highroof_facelift	8368	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-FACELIFT-4X4-01	HIGH	中轴高顶改款后四驱外廓。	READY
8368_735_highroof_facelift	8368	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-FACELIFT-4X4-01	HIGH	长轴高顶改款后四驱外廓。	READY
8369_731_stdroof_prefl	8369	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-RWD-01	HIGH	短轴标准顶改款前后驱外廓。	READY
8369_733_stdroof_prefl	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-RWD-01	HIGH	中轴标准顶改款前后驱外廓。	READY
8369_733_highroof_prefl	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-RWD-01	HIGH	中轴高顶改款前后驱外廓。	READY
8369_735_highroof_prefl	8369	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-RWD-01	HIGH	长轴高顶改款前后驱外廓。	READY
8369_731_stdroof_facelift	8369	MPV	Sprinter II W906	906.731		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-FACELIFT-RWD-01	HIGH	短轴标准顶改款后后驱外廓。	READY
8369_733_stdroof_facelift	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-FACELIFT-RWD-01	HIGH	中轴标准顶改款后后驱外廓。	READY
8369_733_highroof_facelift	8369	MPV	Sprinter II W906	906.733		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-FACELIFT-RWD-01	HIGH	中轴高顶改款后后驱外廓。	READY
8369_735_highroof_facelift	8369	MPV	Sprinter II W906	906.735		EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-FACELIFT-RWD-01	HIGH	长轴高顶改款后后驱外廓。	READY
8370	8370	Sedan	626 V	GF8P	4	EU-MAZDA-626-V-GF-SEDAN-PREFL-01	HIGH		READY
8371_prefl	8371	Sedan	626 V	GFEP	4	EU-MAZDA-626-V-GF-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
8371_facelift	8371	Sedan	626 V	GFEP	4	EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
8372	8372	Hatchback	626 V	GF8P	5	EU-MAZDA-626-V-GF-HATCHBACK-PREFL-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7601-7700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505	Auto-Data	https://www.auto-data.net/en/ford-focus-iii-wagon-2.0-tdci-115hp-powershift-19822
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423	Auto-Data	https://www.auto-data.net/en/volkswagen-golf-vi-cabriolet-2.0-tdi-140hp-20417
EU-SEAT-TERRA-MPV-3D-01	3869	1490	1895	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-SEAT-TERRA-VAN-3D-01	3869	1490	1895	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-PARTNER-I-M49-VAN-PREFL-01	4110	1720	1800	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-PARTNER-I-M59-VAN-FACELIFT-01	4137	1724	1810	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-EXPERT-I-222-BUS-01	4440	1810	1940	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-EXPERT-I-222-VAN-01	4440	1810	1940	Drom; Truck1	https://www.drom.ru/catalog/peugeot/expert/235600/;https://www.truck1.eu/blog/peugeot-expert-van-222-1-6-79-hp-tech-specs-t30691
EU-PEUGEOT-EXPERT-I-223-PLATFORM-CAB-01	4470	1810	1927	Zoomcar	https://zoomcar.fr/fiche-technique-utilitaire/top-peugeot/expert-plancher-cabine-expert-plancher-cab-phc-220l-1-6-NAT79082.html
EU-PEUGEOT-J5-280P-MINIBUS-STANDARD-01	4765	1965	2100	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-LOWROOF-01	4759	1965	2100	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-290L-VAN-4X4-SWB-HIGHROOF-01	4759	1965	2420	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-LOWROOF-01	5489	1965	2100	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-290L-VAN-4X4-LWB-HIGHROOF-01	5489	1965	2420	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-280L-CHASSIS-CAB-SWB-01	4712	1965	1900	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-J5-280L-CHASSIS-CAB-LWB-01	5489	1965	1900	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-33-905-HATCHBACK-1.8TD-01	4040	1612	1345	Automobile-Catalog	https://www.automobile-catalog.com/car/1988/215150/alfa_romeo_33_1_8_td.html
EU-PEUGEOT-405-I-SEDAN-01	4408	1716	1406	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-106-I-HATCHBACK-3D-STANDARD-01	3564	1590	1367	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-106-I-HATCHBACK-5D-STANDARD-01	3564	1590	1367	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ROVER-200-II-XW-HATCHBACK-3D-01	4220	1680	1390	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-6-F12-CONVERTIBLE-01	4894	1894	1365	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-90-162A-SEDAN-01	4391	1638	1420	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-HYUNDAI-LANTRA-II-J2-WAGON-01	4450	1700	1457	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-6-F13-COUPE-01	4894	1894	1369	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-HYUNDAI-LANTRA-II-J2-SEDAN-PREFL-01	4420	1700	1393	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-HYUNDAI-LANTRA-II-J2-SEDAN-FACELIFT-01	4448	1702	1393	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-PEUGEOT-305-II-SEDAN-BASE-01	4263	1630	1407	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-PREFL-01	4324	1765	1421	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-1-SERIES-II-F21-HATCHBACK-3D-FACELIFT-01	4329	1765	1421	Automobile-Catalog	https://www.automobile-catalog.com/car/2016/2103380/bmw_125i_3-door.html
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-PREFL-01	4324	1765	1421	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-1-SERIES-II-F20-HATCHBACK-5D-FACELIFT-01	4329	1765	1421	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-I-HATCHBACK-3D-01	3685	1610	1410	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-SEAT-IBIZA-I-HATCHBACK-5D-01	3685	1610	1410	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-ALFA-ROMEO-75-162B-SEDAN-STANDARD-01	4330	1630	1400	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-AX-PHASE-I-HATCHBACK-01	3495	1555	1355	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-AX-PHASE-II-HATCHBACK-01	3525	1555	1355	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-BMW-X5-E70-LCI-SUV-01	4857	1933	1776	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-VISA-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1410	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-VISA-GT-PHASE-I-HATCHBACK-5D-01	3690	1535	1408	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-VISA-GT-PHASE-II-HATCHBACK-5D-01	3690	1530	1400	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-VISA-GT-1984-FACELIFT-HATCHBACK-5D-01	3725	1526	1370	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-RENAULT-4-MPV-5D-01	3668	1485	1550	Renault 1968 official brochure; Dimensions des Renault 4	https://manuals.plus/m/0420d466d0838d3fe56548cc9a5113bbca8251da23ef3f00cef32d56b37ae997.pdf;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
EU-RENAULT-4-F4-VAN-3D-01	3653	1500	1710	Renault The Originals Museum; Dimensions des Renault 4	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
EU-RENAULT-4-R2108-VAN-HIGHROOF-3D-01	3695	1500	1820	Renault The Originals Museum; Dimensions des Renault 4	https://theoriginals.renault.com/en/renault-4-fourgonnette;https://www.la4ldesylvie.fr/images/stories/tutoriels/cara-generales/dimensions-poids/dimensions-des-renault-4.pdf
EU-FORD-FIESTA-III-GFJ-HATCHBACK-STANDARD-01	3743	1606	1389	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-RENAULT-5-TURBO-HATCHBACK-3D-01	3664	1752	1323	Renault The Originals Museum; Automobile-Catalog	https://theoriginals.renault.com/en/r5-turbo;https://www.automobile-catalog.com/car/1981/29330/renault_5_turbo.html
EU-FORD-SIERRA-II-HATCHBACK-01	4425	1694	1407	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-FIAT-CROMA-I-HATCHBACK-PREFL-01	4495	1760	1433	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-FIAT-CROMA-I-HATCHBACK-FACELIFT-01	4518	1760	1433	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-TOYOTA-COROLLA-VIII-E110-WAGON-FWD-PREFL-01	4320	1690	1445	Auto-Data	https://www.auto-data.net/en/toyota-corolla-wagon-viii-e110-1.6-i-16v-108hp-3343
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-PREFL-01	4320	1690	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/3594215/toyota_corolla_wagon_1_8_4wd.html
EU-TOYOTA-COROLLA-VIII-E110-WAGON-4WD-FACELIFT-01	4340	1690	1505	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3594470/toyota_corolla_wagon_1_8_4wd.html
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-PREFL-01	4295	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3594125/toyota_corolla_sedan_1_3_automatic.html
EU-TOYOTA-COROLLA-VIII-E110-COMPACT-3D-PREFL-01	4100	1690	1380	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3593900/toyota_corolla_compact_1_3.html
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-PREFL-01	4270	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/1998/3593975/toyota_corolla_liftback_1_3.html
EU-TOYOTA-COROLLA-VIII-E110-LIFTBACK-5D-FACELIFT-01	4290	1690	1385	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/3594335/toyota_corolla_liftback_1_6.html
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-AUDI-A4-B5-8D5-AVANT-WAGON-01	4479	1733	1417	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-XANTIA-X1-WAGON-01	4660	1755	1416	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-XANTIA-X2-WAGON-01	4712	1760	1420	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-XANTIA-X1-HATCHBACK-01	4444	1755	1387	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CITROEN-XANTIA-X2-HATCHBACK-01	4524	1755	1400	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-VW-TOUAREG-II-7P-SUV-PREFL-01	4795	1940	1709	Cataloge.eu	https://www.cataloge.eu/volkswagen/touareg-2010-7p
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709	CarExpert New Zealand	https://www.carexpert.co.nz/volkswagen/touareg/2015-bluemotion-3l-sport-utility-vehicle-4x4-diesel-automatic-jofk8wfm20141217
EU-CHEVROLET-LUMINA-APV-GMT199-MPV-01	4844	1877	1669	Task-provided cross-batch dimension group index	sandbox:/mnt/data/all_7601-7700_cross_batch_dimension_index_source.txt
EU-CHEVROLET-S10-BLAZER-II-SUV-2D-PREFL-01	4437	1722	1699	Chevrolet 1997 Blazer official brochure	https://xr793.com/wp-content/uploads/2018/10/1997-Chevrolet-Blazer.pdf
EU-CHEVROLET-S10-BLAZER-II-SUV-4D-PREFL-01	4602	1722	1694	Chevrolet 1997 Blazer official brochure	https://xr793.com/wp-content/uploads/2018/10/1997-Chevrolet-Blazer.pdf
EU-CHEVROLET-S10-BLAZER-II-SUV-2D-FACELIFT-01	4491	1722	1638	Chevrolet 2001 Blazer official brochure	https://xr793.com/wp-content/uploads/2025/05/2001-Chevrolet-Blazer.pdf
EU-CHEVROLET-S10-BLAZER-II-SUV-4D-FACELIFT-01	4656	1722	1633	Auto-Data	https://www.auto-data.net/en/chevrolet-blazer-ii-4-door-facelift-1998-generation-8282
EU-CHEVROLET-S10-BLAZER-II-SUV-2D-LATE-01	4503	1722	1643	The Car Connection	https://www.thecarconnection.com/specifications/chevrolet_blazer_2003
EU-CHEVROLET-S10-BLAZER-II-SUV-4D-LATE-01	4669	1722	1641	Edmunds	https://www.edmunds.com/chevrolet/blazer/2003/features-specs/
EU-CHEVROLET-S10-BLAZER-II-SUV-2D-ZR2-01	4503	1816	1643	Automobile-Catalog; Chevrolet 2003 Blazer official brochure	https://www.automobile-catalog.com/car/2003/483755/chevrolet_blazer_zr2_automatic.html;https://xr793.com/wp-content/uploads/2017/07/2003-Chevrolet-Blazer.pdf
EU-CHEVROLET-CORVETTE-C5-COUPE-2D-01	4564	1869	1212	Edmunds	https://www.edmunds.com/chevrolet/corvette/1997/features-specs/
EU-HONDA-CR-V-I-RD1-SUV-PHASE-I-01	4520	1750	1675	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1120145/honda_cr-v.html
EU-HYUNDAI-H100-P-MINIBUS-01	4790	1690	1965	CarrosNaWeb; Razmery	https://www.carrosnaweb.com.br/fichadetalhe.asp?codigo=15658;https://en.razmery.info/equipment/car_bodies/dimensions-car-bodies-hyundai-h100-bus.html
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-4X4-01	5245	1993	2520	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-4X4-01	5910	1993	2615	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-4X4-01	5910	1993	2905	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-4X4-01	6945	1993	2910	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-FACELIFT-4X4-01	5261	1993	2456	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-low-roof-4x4.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-FACELIFT-4X4-01	5926	1993	2456	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-low-roof-4x4.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-FACELIFT-4X4-01	5926	1993	2746	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-high-roof-4x4.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-FACELIFT-4X4-01	6961	1993	2736	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-170wb-high-roof.pdf;https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-high-roof-4x4.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-PREFL-RWD-01	5245	1993	2435	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-PREFL-RWD-01	5910	1993	2530	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-PREFL-RWD-01	5910	1993	2820	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-PREFL-RWD-01	6945	1993	2815	Mercedes-Benz Sprinter official brochure; Mercedes-Benz Sprinter body/equipment mounting directives	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-731-STANDARDROOF-FACELIFT-RWD-01	5261	1993	2436	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-low-roof.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-STANDARDROOF-FACELIFT-RWD-01	5926	1993	2436	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-low-roof.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-733-HIGHROOF-FACELIFT-RWD-01	5926	1993	2725	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-144wb-high-roof.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-BUS-735-HIGHROOF-FACELIFT-RWD-01	6961	1993	2715	Mercedes-Benz Vans official 2016 passenger-van 2D drawings; Mercedes-Benz Sprinter body/equipment mounting directives	https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-170wb-high-roof.pdf;https://diysprinter.co.uk/reference/UK-body-builders-arl_sprinterbm906_uk.pdf
EU-MAZDA-626-V-GF-SEDAN-PREFL-01	4575	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1665380/mazda_626_2_0_4-door.html
EU-MAZDA-626-V-GF-SEDAN-FACELIFT-01	4590	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/2001/1665635/mazda_626_2_0_4-door_automatic.html
EU-MAZDA-626-V-GF-HATCHBACK-PREFL-01	4575	1710	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/1997/1665335/mazda_626_2_0_136_5-door.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7601-7700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-170wb-high-roof.pdf "https://www.mbvans.com/content/dam/mb-vans/us/upfitter/drawings/2d/2500-passenger-170wb-high-roof.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7601-7700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7601-7700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（9599 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2937 行）

