# 任务：all 第 3801-3900 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0039__76afc231


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3801-3900 行

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
all 第 3801-3900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E92-COUPE-FACELIFT-01	4612	1782	1395
EU-BMW-3-E92-COUPE-PREFL-01	4580	1782	1395
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F80-M3-CS-SEDAN-01	4671	1877	1424
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339
EU-BMW-8-G14-M850I-CONVERTIBLE-01	4851	1902	1345
EU-BMW-8-G15-840D-COUPE-01	4843	1902	1341
EU-BMW-8-G15-M850I-COUPE-01	4851	1902	1346
EU-BMW-X5-F15-SUV-01	4886	1938	1762
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670
EU-CITROEN-C5-I-DE-WAGON-FACELIFT-01	4839	1780	1555
EU-CITROEN-C5-I-DE-WAGON-PREFL-01	4756	1770	1516
EU-CITROEN-C5-II-RD-SEDAN-01	4779	1860	1451
EU-DACIA-LODGY-MPV-01	4498	1751	1679
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-KIA-CEED-I-ED-HATCHBACK-FACELIFT-01	4235	1790	1480
EU-KIA-CEED-I-ED-HATCHBACK-PREFL-01	4235	1790	1480
EU-KIA-CEED-I-ED-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-ED-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-I-WAGON-FACELIFT-01	4470	1790	1525
EU-KIA-CEED-I-WAGON-PREFL-01	4470	1790	1490
EU-KIA-CEED-II-HATCHBACK-01	4310	1780	1470
EU-KIA-CEED-II-JD-VAN-FACELIFT-01	4505	1780	1485
EU-KIA-CEED-II-WAGON-01	4505	1780	1485
EU-KIA-CEED-III-CD-HATCHBACK-01	4310	1800	1447
EU-KIA-CEED-III-CD-HATCHBACK-GT-01	4325	1800	1442
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-02	5000	1983	1836
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-PREFL-01	4999	1983	1836
EU-MERCEDES-BENZ-A-KLASSE-V177-AMG-A35-SEDAN-01	4558	1797	1411
EU-MERCEDES-BENZ-A-KLASSE-V177-SEDAN-PREFL-01	4549	1796	1446
EU-MERCEDES-BENZ-A-KLASSE-W177-AMG-A35-HATCHBACK-01	4436	1796	1405
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440
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
EU-MERCEDES-BENZ-S-KLASSE-A217-AMG-S63-CONVERTIBLE-FACELIFT-01	5052	1913	1422
EU-MERCEDES-BENZ-S-KLASSE-C217-AMG-S63-COUPE-FACELIFT-01	5051	1913	1424
EU-MERCEDES-BENZ-S-KLASSE-W221-S350CDI-SEDAN-FACELIFT-SWB-01	5096	1871	1479
EU-MERCEDES-BENZ-S-KLASSE-W222-S350D-SEDAN-FACELIFT-SWB-01	5125	1905	1493
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420
EU-RENAULT-TWINGO-I-HATCHBACK-01	3433	1630	1423
EU-RENAULT-TWINGO-III-X07-HATCHBACK-PREFL-01	3595	1646	1554
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039
EU-STREETSCOOTER-WORK-PICKUP-01	4741	1814	1859
EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	4676	1796	1861
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Focus iv turnier	2.3 ST Ecoboost	Kombi	Frontantrieb	Benzin	206	280	Apr 2019	Nov 2025	2026-02-01	136165
Ford	Kuga ii	2.0 Ecoboost 4X4	SUV	Allrad	Benzin	169	230	Mar 2019	Dec 2019	2024-05-01	136166
Ford	Mondeo v turnier	2.0 Hybrid Ivct	Kombi	Frontantrieb	Benzin/Elektro	138	188	Jan 2019	Mar 2022	2026-04-01	136167
KIA	Ceed	1.6	Kombi	Frontantrieb	Benzin	94	128	May 2018	-	2024-03-01	136172
KIA	Proceed	1.6 T-gdi	Kombi	Frontantrieb	Benzin	147	200	Oct 2018	-	2024-03-01	136173
KIA	Soul iii	1.6 MPI	Schrägheck	Frontantrieb	Benzin	91	124	Jan 2019	-	2024-03-01	136174
KIA	Soul iii	1.6 T-gdi	Schrägheck	Frontantrieb	Benzin	147	200	Jan 2019	-	2024-03-01	136175
Hyundai	Tucson	2.0 Cvvt	SUV	Frontantrieb	Benzin	110	150	Jun 2015	Sep 2020	2024-03-01	136176
Mercedes-benz	Eqc	EQC 400 4-matic	SUV	Allrad	Elektro	300	408	May 2019	Jul 2023	2024-03-01	136178
Mercedes-benz	Glc	300 D 4-matic	SUV	Allrad	Diesel	180	245	Apr 2019	Mar 2023	2024-03-01	136181
Mercedes-benz	Glc	300 D 4-matic	SUV	Allrad	Diesel	180	245	Apr 2019	Jun 2022	2024-03-01	136184
Mercedes-benz	B-Klasse sports tourer	B 200	Schrägheck	Frontantrieb	Benzin	110	150	Jan 2019	-	2024-03-01	136185
Mercedes-benz	Glc	200 EQ Boost	SUV	Heckantrieb	Benzin/Elektro	145	197	Apr 2019	Mar 2023	2024-03-01	136194
Mercedes-benz	Glc	200 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	145	197	Apr 2019	Mar 2023	2024-03-01	136195
Mercedes-benz	Glc	200 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	145	197	Apr 2019	Jun 2022	2024-03-01	136197
Mercedes-benz	Glc	200 EQ Boost	SUV	Heckantrieb	Benzin/Elektro	145	197	Apr 2019	Jun 2022	2024-03-01	136198
Ford	Kuga ii	1.5 Ecoboost 4X4	SUV	Allrad	Benzin	110	150	Jul 2016	Dec 2019	2024-05-01	136199
Mercedes-benz	Glc	300 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	190	258	Apr 2019	Mar 2023	2024-03-01	136200
Mercedes-benz	Glc	300 EQ Boost 4-matic	SUV	Allrad	Benzin/Elektro	190	258	Apr 2019	Jun 2022	2024-03-01	136201
Dacia	Lodgy	1.3 TCE 130	Großraumlimousine	Frontantrieb	Benzin	96	131	Jan 2019	-	2024-03-01	136202
Renault	Twingo	1.0 SCE 65	Schrägheck	Heckantrieb	Benzin	48	65	Mar 2019	Jul 2024	2026-05-01	136203
Renault	Twingo	1.0 SCE 75	Schrägheck	Heckantrieb	Benzin	54	73	Mar 2019	Jan 2021	2026-05-01	136204
Mitsubishi	Eclipse cross	2.2 DID 4WD	SUV	Allrad	Diesel	109	148	Mar 2019	-	2024-03-01	136205
Volvo	V60 ii	T6 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	250	340	Mar 2019	Dec 2022	2024-05-01	136206
Volvo	Xc40	T3	SUV	Frontantrieb	Benzin	120	163	Mar 2019	Dec 2022	2024-05-01	136207
Ford	Ecosport	2.0 Ti-vct 4X4	SUV	Allrad	Benzin	110	150	Oct 2018	-	2024-03-01	136228
Subaru	Levorg	2.0 AWD	Kombi	Allrad	Benzin	110	150	Jan 2019	-	2024-03-01	136236
Mini	Mini	John Cooper Works	Kombi	Allrad	Benzin	225	306	Jul 2019	-	2024-03-01	136257
Mini	Mini	John Cooper Works All4	Kombi	Allrad	Benzin	225	306	Jul 2019	-	2024-03-01	136258
Skoda	Karoq	2.0 TSI 4X4	SUV	Allrad	Benzin	140	190	Nov 2018	-	2025-06-01	136264
Audi	Q5	50 TDI Quattro	SUV	Allrad	Diesel	210	286	Mar 2019	Nov 2020	2024-03-01	136266
Audi	A4 allroad b9	2.0 Tfsi Mild Hybrid Quattro	Kombi	Allrad	Benzin/Elektro	185	252	Nov 2018	Oct 2019	2024-03-01	136267
Mercedes-benz	Marco polo camper	200 CDI	Bus	Heckantrieb	Diesel	100	136	Mar 2019	-	2024-03-01	136268
Mercedes-benz	Marco polo camper	200 CDI 4-matic	Bus	Allrad	Diesel	100	136	Mar 2019	-	2024-03-01	136269
Mercedes-benz	Marco polo camper	220 CDI	Bus	Heckantrieb	Diesel	120	163	Mar 2019	-	2024-03-01	136270
Mercedes-benz	Marco polo camper	220 CDI 4-matic	Bus	Allrad	Diesel	120	163	Mar 2019	-	2024-03-01	136271
Mercedes-benz	Marco polo camper	250 CDI	Bus	Heckantrieb	Diesel	140	190	Mar 2019	-	2024-03-01	136272
Mercedes-benz	Marco polo camper	250 CDI 4-matic	Bus	Allrad	Diesel	140	190	Mar 2019	-	2024-03-01	136273
Streetscooter	Work	Elektro	Kasten	Frontantrieb	Elektro	39	53	May 2018	Jul 2022	2024-03-01	136274
Streetscooter	Work	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	39	53	May 2018	Jul 2022	2024-03-01	136275
Streetscooter	Work l	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	39	53	May 2019	Jul 2022	2024-03-01	136276
Streetscooter	Work l	Elektro	Kasten	Frontantrieb	Elektro	39	53	May 2019	Jul 2022	2024-03-01	136277
Volvo	V60 ii	T8 Plug-in Hybrid Polestar AWD	Kombi	Allrad	Benzin/Elektro	298	405	May 2019	Dec 2022	2024-05-01	136278
Mercedes-benz	Marco polo camper	160 CDI	Bus	Frontantrieb	Diesel	65	88	Mar 2015	-	2024-03-01	136279
Mercedes-benz	Marco polo camper	180 CDI	Bus	Frontantrieb	Diesel	84	114	Mar 2015	-	2024-03-01	136280
Citroën	C5	1.6 THP 165	SUV	Frontantrieb	Benzin	121	165	May 2019	-	2024-07-01	136281
BMW	1	118 I	Schrägheck	Frontantrieb	Benzin	103	140	Jul 2019	-	2024-03-01	136290
BMW	1	M 135 I Xdrive	Schrägheck	Allrad	Benzin	225	306	Jul 2019	-	2024-03-01	136291
BMW	1	116 D	Schrägheck	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	136292
BMW	1	118 D	Schrägheck	Frontantrieb	Diesel	110	150	Jul 2019	-	2024-03-01	136293
BMW	1	120 D Xdrive	Schrägheck	Allrad	Diesel	140	190	Jul 2019	-	2024-03-01	136294
BMW	3	320 I Xdrive	Stufenheck	Allrad	Benzin	135	184	Jul 2019	-	2024-03-01	136302
BMW	3	330 I Xdrive	Stufenheck	Allrad	Benzin	190	258	Nov 2018	-	2024-03-01	136303
BMW	3	330 D Xdrive	Stufenheck	Allrad	Diesel	195	265	Jul 2019	-	2024-03-01	136304
BMW	5	M 550 I Xdrive	Stufenheck	Allrad	Benzin	390	530	Jul 2019	Jun 2023	2024-03-01	136305
BMW	8	840 I	Coupe	Heckantrieb	Benzin	250	340	Jul 2019	-	2024-05-01	136306
BMW	8	840 I Xdrive	Coupe	Allrad	Benzin	250	340	Jul 2019	Oct 2020	2024-03-01	136307
BMW	8	840 I	Cabriolet	Heckantrieb	Benzin	250	340	Jul 2019	-	2024-05-01	136308
BMW	8	840 I Xdrive	Cabriolet	Allrad	Benzin	250	340	Jul 2019	Oct 2020	2024-03-01	136309
BMW	X5	Xdrive 25 D	SUV	Allrad	Diesel	170	231	Aug 2019	Mar 2023	2024-03-01	136310
Peugeot	508 ii	1.6 THP 150	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2018	-	2024-03-01	136311
Volvo	S60 iii	T5	Stufenheck	Frontantrieb	Benzin	184	250	Feb 2019	Dec 2021	2024-05-01	136333
Volvo	S60 iii	T4	Stufenheck	Frontantrieb	Benzin	140	190	Feb 2019	Dec 2021	2024-05-01	136334
Volvo	S60 iii	T8 Twin Engine AWD	Stufenheck	Allrad	Benzin/Elektro	287	390	Feb 2019	Dec 2022	2024-05-01	136335
Toyota	Rav 4 v	2.0 Vvti AWD	SUV	Allrad	Benzin	127	173	Feb 2019	-	2024-03-01	136344
Volvo	S60 iii	T6 Twin Engine AWD	Stufenheck	Allrad	Benzin/Elektro	250	340	Feb 2019	Dec 2022	2024-05-01	136345
Volvo	S60 iii	T8 Twin Engine Polestar AWD	Stufenheck	Allrad	Benzin/Elektro	298	405	Feb 2019	-	2024-03-01	136346
Mercedes-benz	A-Klasse	A 160 D	Schrägheck	Frontantrieb	Diesel	70	95	May 2019	-	2024-03-01	136347
Mercedes-benz	B-Klasse sports tourer	B 160 D	Schrägheck	Frontantrieb	Diesel	70	95	May 2019	-	2024-03-01	136348
Mercedes-benz	C-Klasse	C 300 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	190	258	May 2019	May 2021	2024-03-01	136350
Mercedes-benz	C-Klasse	C 300 EQ Boost 4-matic	Stufenheck	Allrad	Benzin/Elektro	190	258	May 2019	May 2021	2024-03-01	136351
Mercedes-benz	C-Klasse	C 300 EQ Boost	Kombi	Heckantrieb	Benzin/Elektro	190	258	May 2019	Feb 2021	2024-03-01	136352
Mercedes-benz	C-Klasse	C 300 EQ Boost 4-matic	Kombi	Allrad	Benzin/Elektro	190	258	May 2019	Feb 2021	2024-03-01	136353
Mercedes-benz	C-Klasse	C 300 EQ Boost	Coupe	Heckantrieb	Benzin/Elektro	190	258	May 2019	Apr 2023	2024-03-01	136357
Mercedes-benz	C-Klasse	C 300 EQ Boost	Cabriolet	Heckantrieb	Benzin/Elektro	190	258	May 2019	Apr 2023	2024-03-01	136358
Volvo	V60 ii	T4	Kombi	Frontantrieb	Benzin	140	190	May 2019	-	2024-03-01	136359
Land Rover	Range rover iv	3.0 P400 Mhev 4X4	SUV	Allrad	Benzin/Elektro	294	400	May 2019	Sep 2021	2025-02-03	136362
Volvo	Xc90 ii	B5 Mild-hybrid AWD	SUV	Allrad	Diesel/Elektro	173	235	Apr 2019	-	2024-03-01	136364
Volvo	Xc60 ii	B5 Mild-hybrid AWD	SUV	Allrad	Diesel/Elektro	173	235	Apr 2019	-	2024-03-01	136366
KIA	Soul iii	E-soul	Schrägheck	Frontantrieb	Elektro	100	136	Jan 2019	-	2024-03-01	136367
BMW	8	M8	Coupe	Allrad	Benzin	441	600	Jul 2019	-	2024-03-01	136369
BMW	8	M8 Competition	Coupe	Allrad	Benzin	460	625	Jul 2019	-	2024-03-01	136370
BMW	8	M8	Cabriolet	Allrad	Benzin	441	600	Jul 2019	-	2024-03-01	136371
BMW	8	M8 Competition	Cabriolet	Allrad	Benzin	460	625	Jul 2019	-	2024-03-01	136372
BMW	X1	Xdrive 25 E Plug-in-hybrid	SUV	Allrad	Benzin/Elektro	162	220	Mar 2020	Jun 2022	2024-03-01	136374
VW	Passat b8	2.0 TSI	Stufenheck	Frontantrieb	Benzin	140	190	Nov 2018	Mar 2024	2025-02-03	136375
VW	Passat b8 variant	2.0 TSI	Kombi	Frontantrieb	Benzin	140	190	Nov 2018	Mar 2024	2025-02-03	136376
Mercedes-benz	S-Klasse	S 500 4-matic	Stufenheck	Allrad	Benzin	320	435	Sep 2013	May 2017	2024-03-01	136377
Volvo	Xc60 ii	B4 Mild-hybrid AWD	SUV	Allrad	Diesel/Elektro	145	197	Apr 2019	-	2024-03-01	136378
Volvo	S90 ii	T6 Drive-e Polestar AWD	Stufenheck	Allrad	Benzin	240	326	Oct 2017	Dec 2021	2024-05-01	136379
Volvo	S90 ii	T5 Drive-e Polestar	Stufenheck	Frontantrieb	Benzin	186	253	Oct 2017	Dec 2021	2024-05-01	136380
Volvo	S90 ii	D4 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	147	200	Mar 2016	Dec 2021	2024-05-01	136381
Volvo	V60 ii	T5 AWD	Kombi	Allrad	Benzin	184	250	Sep 2018	Dec 2021	2024-05-01	136382
Volvo	V90 ii	T8 Plug-in Hybrid Polestar AWD	Kombi	Allrad	Benzin/Elektro	233	317	May 2018	Dec 2022	2024-05-01	136383
Volvo	V90 ii	T6 Polestar AWD	Kombi	Allrad	Benzin	240	326	Oct 2017	Dec 2021	2024-05-01	136384
Volvo	V90 ii cross country	T5 Polestar AWD	Kombi	Allrad	Benzin	186	253	Oct 2017	-	2024-03-01	136385
Volvo	S60 iii	T5 AWD	Stufenheck	Allrad	Benzin	184	250	Feb 2019	-	2024-03-01	136386
Volvo	V60 ii	T6 Drive-e Polestar AWD	Kombi	Allrad	Benzin	240	326	Feb 2018	Dec 2021	2026-07-01	136387
Toyota	Hiace vi	2.8	Bus	Heckantrieb	Diesel	120	163	May 2019	-	2024-03-01	136388
Audi	A6 allroad c8	50 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	210	286	Nov 2018	-	2024-03-01	136391


--- Round 1 / 首次发送 ---
## 更新点

* 首轮完成 100 个输入 Ktype 的映射建档；确认 `136275` 需拆分为 Pritsche 与 Fahrgestell，`136375`、`136376` 需按改款前后拆分。([汽车数据][1])2019 facelift。Ford、Mercedes-Benz 与 Auto-Data 资料分别确认了对应物理边界和不含后视镜宽度。([汽车数据][1])([汽车数据][1])3
* 其余已确认车型采用缓存优先模式，直接关联跨批次既有尺寸组，未重复输出既有尺寸组来源。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：103
* READY 映射：65
* PENDING 映射：38
* 已全部 READY 的输入 Ktype：62
* 仍含 PENDING 的输入 Ktype：38
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136165	136165	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-ST-01	HIGH	ST Turnier 五门物理外廓。	READY
136166	136166	SUV	Kuga II (facelift)	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH	2019 改款外廓。	READY
136167	136167	Wagon	Mondeo V (facelift)	CD391	5	EU-FORD-MONDEO-V-WAGON-FACELIFT-01	HIGH	改款 Hybrid Turnier 五门外廓。	READY
136172	136172	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
136173	136173	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH		READY
136174	136174	Hatchback	Soul III	SK3	5		LOW	候选为 Soul III 汽油五门外廓。	PENDING: 汽油版与既有 e-Soul 尺寸组的高度/外饰边界尚未闭合。
136175	136175	Hatchback	Soul III	SK3	5		LOW	候选为 Soul III 汽油五门外廓。	PENDING: 汽油版与既有 e-Soul 尺寸组的高度/外饰边界尚未闭合。
136176	136176	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136178	136178	SUV	EQC	N293	5	EU-MERCEDES-BENZ-EQC-N293-SUV-01	HIGH		READY
136181	136181	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136184	136184	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136185	136185	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136194	136194	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136195	136195	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136197	136197	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136198	136198	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136199	136199	SUV	Kuga II	DM2	5		LOW	候选为 Kuga II 改款前后外廓。	PENDING: 2016 年中生产边界可能跨改款，需确认是否拆分 prefl/facelift。
136200	136200	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136201	136201	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136202	136202	MPV	Lodgy	J92	5	EU-DACIA-LODGY-MPV-01	HIGH		READY
136203	136203	Hatchback	Twingo III (facelift)	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136204	136204	Hatchback	Twingo III (facelift)	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136205	136205	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
136206	136206	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136207	136207	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136228	136228	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH		READY
136236	136236	Wagon	Levorg I (facelift)	VM	5		LOW	候选为 Levorg I 改款五门旅行车。	PENDING: 2.0 AWD 对应市场版三维及不含镜宽度尚未闭合。
136257	136257	Wagon	MINI Clubman II (facelift)	F54	5		LOW	候选为 F54 JCW 改款外廓。	PENDING: 306 PS JCW Clubman 改款外廓与既有 F54 普通组不同，需新建组。
136258	136258	Wagon	MINI Clubman II (facelift)	F54	5		LOW	候选为 F54 JCW 改款外廓。	PENDING: 306 PS JCW Clubman 改款外廓与既有 F54 普通组不同，需新建组。
136264	136264	SUV	Karoq I (pre-facelift)	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	MEDIUM	按 2018 起始版本映射至改款前外廓。	READY
136266	136266	SUV	Q5 II (pre-facelift)	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
136267	136267	Wagon	A4 allroad B9		5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
136268	136268	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136269	136269	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136270	136270	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136271	136271	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136272	136272	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136273	136273	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136274	136274	Van	StreetScooter Work		2	EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH		READY
136275_pickup	136275	Pickup	StreetScooter Work		2	EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pritsche 分支。	READY
136275_chassis	136275	Chassis Cab	StreetScooter Work		2	EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Fahrgestell 分支。	READY
136276	136276	Chassis Cab	StreetScooter Work L		2		LOW	需确认并拆分长轴 Pritsche 与 Fahrgestell。	PENDING: Work L 的 Pritsche/Fahrgestell 两个外廓尚未分别闭合。
136277	136277	Van	StreetScooter Work L		2		LOW	候选为 Work L 长轴箱式车。	PENDING: Work L 箱式车三维及不含镜宽度尚未闭合。
136278	136278	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136279	136279	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136280	136280	MPV	Marco Polo III	W447			LOW	候选为 W447 露营车外廓。	PENDING: Marco Polo/Marco Polo Activity 的车长、车顶高度及驱动版本边界尚未闭合。
136281	136281	SUV	C5 Aircross I (pre-facelift)	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
136290	136290	Hatchback	1 Series III	F40	5		LOW	候选为 BMW F40 五门掀背。	PENDING: F40 五门外廓尚未创建完整尺寸组。
136291	136291	Hatchback	1 Series III	F40	5		LOW	候选为 BMW F40 五门掀背。	PENDING: F40 五门外廓尚未创建完整尺寸组。
136292	136292	Hatchback	1 Series III	F40	5		LOW	候选为 BMW F40 五门掀背。	PENDING: F40 五门外廓尚未创建完整尺寸组。
136293	136293	Hatchback	1 Series III	F40	5		LOW	候选为 BMW F40 五门掀背。	PENDING: F40 五门外廓尚未创建完整尺寸组。
136294	136294	Hatchback	1 Series III	F40	5		LOW	候选为 BMW F40 五门掀背。	PENDING: F40 五门外廓尚未创建完整尺寸组。
136302	136302	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136303	136303	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136304	136304	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136305	136305	Sedan	5 Series VII	G30	4		LOW	候选为 G30 M550i 改款前后外廓。	PENDING: M550i 生产期跨 G30 改款，需确认是否拆分 prefl/facelift。
136306	136306	Coupe	8 Series II	G15	2	EU-BMW-8-G15-840D-COUPE-01	MEDIUM	840i 与已确认 840d 共用 G15 标准外廓。	READY
136307	136307	Coupe	8 Series II	G15	2	EU-BMW-8-G15-840D-COUPE-01	MEDIUM	840i 与已确认 840d 共用 G15 标准外廓。	READY
136308	136308	Convertible	8 Series II	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	MEDIUM	840i 与已确认 840d 共用 G14 标准外廓。	READY
136309	136309	Convertible	8 Series II	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	MEDIUM	840i 与已确认 840d 共用 G14 标准外廓。	READY
136310	136310	SUV	X5 IV (pre-facelift)	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
136311	136311	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门 fastback 外廓。	READY
136333	136333	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136334	136334	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136335	136335	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136344	136344	SUV	RAV4 V	XA50	5		LOW	候选为 XA50 五门 SUV。	PENDING: RAV4 V 2.0 AWD 欧洲版三维及不含镜宽度尚未闭合。
136345	136345	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136346	136346	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136347	136347	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
136348	136348	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136350	136350	Sedan	C-Class IV (facelift)	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136351	136351	Sedan	C-Class IV (facelift)	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136352	136352	Wagon	C-Class IV (facelift)	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136353	136353	Wagon	C-Class IV (facelift)	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136357	136357	Coupe	C-Class IV (facelift)	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
136358	136358	Convertible	C-Class IV (facelift)	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
136359	136359	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136362	136362	SUV	Range Rover IV (facelift)	L405	5		LOW	候选为 L405 改款标准轴距外廓。	PENDING: P400 MHEV 对应 1836/1869 mm 高度分支尚未确认。
136364	136364	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136366	136366	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136367	136367	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	HIGH		READY
136369	136369	Coupe	M8 I	F92	2		LOW	M8 与 M8 Competition 共用候选车身。	PENDING: F92 M8 外廓尚未创建完整尺寸组。
136370	136370	Coupe	M8 I	F92	2		LOW	M8 与 M8 Competition 共用候选车身。	PENDING: F92 M8 外廓尚未创建完整尺寸组。
136371	136371	Convertible	M8 I	F91	2		LOW	M8 与 M8 Competition 共用候选车身。	PENDING: F91 M8 Cabriolet 外廓尚未创建完整尺寸组。
136372	136372	Convertible	M8 I	F91	2		LOW	M8 与 M8 Competition 共用候选车身。	PENDING: F91 M8 Cabriolet 外廓尚未创建完整尺寸组。
136374	136374	SUV	X1 II (facelift)	F48	5		LOW	候选为 F48 改款五门 SUV。	PENDING: xDrive25e 改款 PHEV 外廓尚未创建完整尺寸组。
136375_prefl	136375	Sedan	Passat B8 (pre-facelift)	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	生产期覆盖改款前分支。	READY
136375_facelift	136375	Sedan	Passat B8 (facelift)	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	生产期覆盖改款后分支。	READY
136376_prefl	136376	Wagon	Passat B8 Variant (pre-facelift)	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	HIGH	生产期覆盖改款前分支。	READY
136376_facelift	136376	Wagon	Passat B8 Variant (facelift)	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	生产期覆盖改款后分支。	READY
136377	136377	Sedan	S-Class VI	W222	4		LOW	候选为 W222 改款前短轴/长轴分支。	PENDING: S 500 4MATIC 是否同时覆盖 SWB/LWB 尚未确认。
136378	136378	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136379	136379	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136380	136380	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136381	136381	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136382	136382	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136383	136383	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
136384	136384	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
136385	136385	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH		READY
136386	136386	Sedan	S60 III		4		LOW	候选为 S60 III 四门轿车。	PENDING: S60 III 三维及不含镜宽度尚未创建完整尺寸组。
136387	136387	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136388	136388	MPV	HiAce VI	H300			LOW	需确认是否拆分 SWB/LWB 与标准顶/高顶。	PENDING: H300 Bus 2.8 的轴距/车顶/车宽分支尚未闭合。
136391	136391	Wagon	A6 allroad C8		5		LOW	候选为 C8 allroad 五门旅行车。	PENDING: A6 allroad C8 50 TDI 三维及不含镜宽度尚未创建完整尺寸组。
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-IV-WAGON-ST-01	4668	1825	1492	Auto-Data Ford Focus IV Wagon ST 2.3 EcoBoost	https://www.auto-data.net/en/ford-focus-iv-wagon-st-2.3-ecoboost-280hp-37683
EU-FORD-MONDEO-V-WAGON-FACELIFT-01	4867	1852	1501	Ford Mondeo official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-MERCEDES-BENZ-EQC-N293-SUV-01	4762	1884	1624	Auto-Data Mercedes-Benz EQC N293 EQC 400 4MATIC	https://www.auto-data.net/en/mercedes-benz-eqc-n293-eqc-400-85-kwh-408hp-4matic-34406
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247 B 200	https://www.auto-data.net/en/mercedes-benz-b-class-w247-b-200-163hp-dct-35003
EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	3615	1646	1541	Auto-Data Renault Twingo III facelift 2019	https://www.auto-data.net/en/renault-twingo-iii-facelift-2019-generation-6847
```

## 下一步优先处理

1. 集中闭合可批量消除多行 PENDING 的共享车身：BMW F40、Volvo S60 III、Marco Polo W447。
2. 创建 MINI F54 JCW、BMW F91/F92 M8、BMW F48 xDrive25e、Toyota RAV4 XA50、Audi A6 allroad C8 尺寸组。
3. 解决 Kuga II、BMW G30 M550i、W222 S 500、Range Rover L405 的改款、轴距或高度分支。
4. 最后处理 StreetScooter Work L 与 Toyota HiAce H300 的多轴距、多车顶拆分。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-focus-iv-wagon-st-2.3-ecoboost-280hp-37683 "Ford Focus IV Wagon ST 2.3 EcoBoost (280 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 批量关闭 BMW F40、Volvo S60 III、Kia Soul III 汽油版、Subaru Levorg、Marco Polo W447、BMW M8、BMW X1 xDrive25e、Toyota RAV4 与 HiAce Commuter 等共享车身映射；本轮首次创建 15 个尺寸组。对应尺寸均按不含后视镜宽度落盘，逐组来源见下方 `DimensionSource` 与 `SourceURL`。([Kia Australia][1])
* `136276` 已拆为 Work L Pritsche 与 Fahrgestell 两个物理分支，并与 `136277` 的 Work L 箱式车分别建组；三种外廓尺寸不同。
* `136377` 已拆为 W222 标准轴距与 V222 长轴距分支；MINI F54 JCW、BMW G30 M550i 和 Range Rover L405 P400 MHEV 直接复用跨批次既有尺寸组，未重复输出尺寸事实。([汽车目录][2])
* 剩余阻塞仅为 `136199` Ford Kuga 的功率/驱动组合冲突，以及 `136391` Audi A6 allroad 的可变悬架高度口径。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：105
* READY 映射：103
* PENDING 映射：2
* 已全部 READY 的输入 Ktype：98
* 仍含 PENDING 的输入 Ktype：2
* 本轮首次创建尺寸组：15
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136174	136174	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	HIGH		READY
136175	136175	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	HIGH		READY
136236	136236	Wagon	Levorg I (facelift)	VM	5	EU-SUBARU-LEVORG-I-VM-WAGON-FACELIFT-01	HIGH		READY
136257	136257	Wagon	MINI Clubman II (facelift)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH		READY
136258	136258	Wagon	MINI Clubman II (facelift)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH		READY
136268	136268	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136269	136269	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136270	136270	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136271	136271	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136272	136272	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136273	136273	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136276_pickup	136276	Pickup	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-PICKUP-01	HIGH	Pritsche 分支。	READY
136276_chassis	136276	Chassis Cab	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-PURE-CHASSIS-01	HIGH	Fahrgestell 分支。	READY
136277	136277	Van	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-BOX-VAN-01	HIGH		READY
136279	136279	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136280	136280	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136290	136290	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136291	136291	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136292	136292	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136293	136293	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136294	136294	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136305	136305	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-M550I-01	HIGH		READY
136333	136333	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136334	136334	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136335	136335	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136344	136344	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
136345	136345	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136346	136346	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136362	136362	SUV	Range Rover IV (facelift)	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH		READY
136369	136369	Coupe	M8 I	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
136370	136370	Coupe	M8 I	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
136371	136371	Convertible	M8 I	F91	2	EU-BMW-8-F91-M8-CONVERTIBLE-01	HIGH		READY
136372	136372	Convertible	M8 I	F91	2	EU-BMW-8-F91-M8-CONVERTIBLE-01	HIGH		READY
136374	136374	SUV	X1 II (facelift)	F48	5	EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	HIGH		READY
136377_swb	136377	Sedan	S-Class VI (pre-facelift)	W222	4	EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	HIGH	标准轴距分支。	READY
136377_lwb	136377	Sedan	S-Class VI (pre-facelift)	V222	4	EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	HIGH	长轴距分支。	READY
136386	136386	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136388	136388	MPV	HiAce VI	H300	4	EU-TOYOTA-HIACE-VI-H300-COMMUTER-MPV-01	HIGH	Commuter 长车身高顶分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	4195	1800	1600	Kia Global Soul specifications	https://www.kia.com/nmc/en/showroom/soul/specification.html
EU-SUBARU-LEVORG-I-VM-WAGON-FACELIFT-01	4690	1780	1490	Subaru Levorg MJ2019 official brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/Levorg/Levorg_MJ2019_PTA.pdf?hsLang=de
EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo ACTIVITY brochure	https://s3-ap-southeast-2.amazonaws.com/assets.i-motor.com.au/trucks/mercendes-benz-vans/pdfs/marco-polo/productBrochure.pdf
EU-STREETSCOOTER-WORK-L-PICKUP-01	5840	1814	1859	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-L-PURE-CHASSIS-01	5784	1796	1867	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-L-BOX-VAN-01	5784	1925	2347	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	BMW 1 Series official brochure	https://www.bmw.co.za/content/dam/bmw/marketZA/bmw_co_za/Documents/brochures/bmw-1-series-brochure-2022.pdf.asset.1650352306018.pdf
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Volvo S60 2019 technical specifications	https://www.volvoclub.org.uk/pdf/s60/s60_2019_techspecs.pdf
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota RAV4 technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220203M-RAV4-Tech-Spec.pdf
EU-BMW-8-F92-M8-COUPE-01	4867	1907	1362	BMW M8 Coupe official technical data	https://www.press.bmwgroup.com/netherlands/article/attachment/T0296706NL/431799
EU-BMW-8-F91-M8-CONVERTIBLE-01	4867	1907	1353	BMW M8 Convertible official technical data	https://www.press.bmwgroup.com/netherlands/article/attachment/T0296706NL/431800
EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	4447	1821	1582	BMW X1 xDrive25e official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0304339ES/444467
EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	5116	1899	1496	Automobile-Catalog Mercedes-Benz S 500 4MATIC	https://www.automobile-catalog.com/car/2014/1929530/mercedes-benz_s_500_4matic.html
EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	5246	1899	1494	Automobile-Catalog Mercedes-Benz S 500 4MATIC Lang	https://www.automobile-catalog.com/car/2014/1929545/mercedes-benz_s_500_4matic_lang.html
EU-TOYOTA-HIACE-VI-H300-COMMUTER-MPV-01	5915	1950	2280	CarExpert 2019 Toyota HiAce Commuter specifications	https://www.carexpert.com.au/toyota/hiace/2019-commuter-2-8l-bus-rwd-diesel-automatic-jo8gwkfo20190418
```

## 下一步优先处理

1. 核对 `136199`：输入中的 `1.5 EcoBoost 110 kW / 150 PS / 4X4` 与已查到的 Kuga II 发动机—驱动组合不一致，并确认是否需要拆分改款前后外廓。
2. 核对 `136391`：A6 allroad C8 已确认长度和不含镜宽度，但资料给出空气悬架高度范围 `1497–1542 mm`，需确定符合落盘口径的标准状态单一高度。
3. 两项关闭后直接进行一次机械收尾并输出完整两表及指定下载链接。

推进信号：CONTINUE

[1]: https://www.kia.com/nmc/en/showroom/soul/specification.html "Kia Soul Specs | 5 Seater SUV | Kia Global"
[2]: https://www.automobile-catalog.com/car/2014/1929530/mercedes-benz_s_500_4matic.html?utm_source=chatgpt.com "2014 Mercedes-Benz S 500 4MATIC Specs Review ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3801-3900_ktype_dimension_mapping_final.tsv
- all_3801-3900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 最后两个阻塞项已关闭。`136199` 按 Kuga II facelift 物理外廓关联既有尺寸组；Ford 官方资料确认该车身为 `4531 × 1838 × 1703 mm`，同时显示 150 PS 汽油版为前驱、AWD 汽油版为 182 PS，因此保留输入动力/驱动组合不一致说明并采用 `MEDIUM` 映射置信度。([福特媒体][1])
* `136391` 建立 A6 allroad C8 标准行驶状态尺寸组 `4951 × 1902 × 1497 mm`。([Audi Press][2])
* 已完成机械检查：表头正确、105 个 `id` 唯一、61 个尺寸组唯一、全部引用闭合、无孤立尺寸组、尺寸与来源字段完整。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：105
* READY 映射：105
* PENDING 映射：0
* DIMENSION_GROUP：61
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
136165	136165	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-ST-01	HIGH	ST Turnier 五门物理外廓。	READY
136166	136166	SUV	Kuga II (facelift)	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	HIGH	2019 改款外廓。	READY
136167	136167	Wagon	Mondeo V (facelift)	CD391	5	EU-FORD-MONDEO-V-WAGON-FACELIFT-01	HIGH	改款 Hybrid Turnier 五门外廓。	READY
136172	136172	Wagon	Ceed III	CD	5	EU-KIA-CEED-III-CD-WAGON-01	HIGH		READY
136173	136173	Wagon	ProCeed III	CD	5	EU-KIA-PROCEED-III-CD-WAGON-01	HIGH		READY
136174	136174	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	HIGH		READY
136175	136175	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	HIGH		READY
136176	136176	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH		READY
136178	136178	SUV	EQC	N293	5	EU-MERCEDES-BENZ-EQC-N293-SUV-01	HIGH		READY
136181	136181	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136184	136184	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136185	136185	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136194	136194	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136195	136195	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136197	136197	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136198	136198	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136199	136199	SUV	Kuga II (facelift)	DM2	5	EU-FORD-KUGA-II-FACELIFT-SUV-01	MEDIUM	输入发动机/驱动组合与资料版本不一致；物理车身按改款外廓归并。	READY
136200	136200	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136201	136201	SUV	GLC	X253	5	EU-MERCEDES-BENZ-GLC-X253-SUV-01	HIGH		READY
136202	136202	MPV	Lodgy	J92	5	EU-DACIA-LODGY-MPV-01	HIGH		READY
136203	136203	Hatchback	Twingo III (facelift)	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136204	136204	Hatchback	Twingo III (facelift)	X07	5	EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	HIGH		READY
136205	136205	SUV	Eclipse Cross I	GK1W	5	EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	HIGH		READY
136206	136206	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136207	136207	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
136228	136228	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH		READY
136236	136236	Wagon	Levorg I (facelift)	VM	5	EU-SUBARU-LEVORG-I-VM-WAGON-FACELIFT-01	HIGH		READY
136257	136257	Wagon	MINI Clubman II (facelift)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH		READY
136258	136258	Wagon	MINI Clubman II (facelift)	F54	5	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH		READY
136264	136264	SUV	Karoq I (pre-facelift)	NU7	5	EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	MEDIUM	按 2018 起始版本映射至改款前外廓。	READY
136266	136266	SUV	Q5 II (pre-facelift)	FY	5	EU-AUDI-Q5-FY-SUV-PREFL-01	HIGH		READY
136267	136267	Wagon	A4 allroad B9		5	EU-AUDI-A4-ALLROAD-B9-WAGON-01	HIGH		READY
136268	136268	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136269	136269	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136270	136270	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136271	136271	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136272	136272	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136273	136273	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136274	136274	Van	StreetScooter Work		2	EU-STREETSCOOTER-WORK-BOX-VAN-01	HIGH		READY
136275_pickup	136275	Pickup	StreetScooter Work		2	EU-STREETSCOOTER-WORK-PICKUP-01	HIGH	Pritsche 分支。	READY
136275_chassis	136275	Chassis Cab	StreetScooter Work		2	EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	HIGH	Fahrgestell 分支。	READY
136276_pickup	136276	Pickup	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-PICKUP-01	HIGH	Pritsche 分支。	READY
136276_chassis	136276	Chassis Cab	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-PURE-CHASSIS-01	HIGH	Fahrgestell 分支。	READY
136277	136277	Van	StreetScooter Work L		2	EU-STREETSCOOTER-WORK-L-BOX-VAN-01	HIGH		READY
136278	136278	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136279	136279	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136280	136280	MPV	Marco Polo III	W447	5	EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	HIGH		READY
136281	136281	SUV	C5 Aircross I (pre-facelift)	C84	5	EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	HIGH		READY
136290	136290	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136291	136291	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136292	136292	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136293	136293	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136294	136294	Hatchback	1 Series III	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH		READY
136302	136302	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136303	136303	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136304	136304	Sedan	3 Series VII (pre-facelift)	G20	4	EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	HIGH		READY
136305	136305	Sedan	5 Series VII	G30	4	EU-BMW-5-G30-SEDAN-M550I-01	HIGH		READY
136306	136306	Coupe	8 Series II	G15	2	EU-BMW-8-G15-840D-COUPE-01	MEDIUM	840i 与已确认 840d 共用 G15 标准外廓。	READY
136307	136307	Coupe	8 Series II	G15	2	EU-BMW-8-G15-840D-COUPE-01	MEDIUM	840i 与已确认 840d 共用 G15 标准外廓。	READY
136308	136308	Convertible	8 Series II	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	MEDIUM	840i 与已确认 840d 共用 G14 标准外廓。	READY
136309	136309	Convertible	8 Series II	G14	2	EU-BMW-8-G14-840D-CONVERTIBLE-01	MEDIUM	840i 与已确认 840d 共用 G14 标准外廓。	READY
136310	136310	SUV	X5 IV (pre-facelift)	G05	5	EU-BMW-X5-G05-SUV-PREFL-01	HIGH		READY
136311	136311	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-FASTBACK-01	HIGH	五门 fastback 外廓。	READY
136333	136333	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136334	136334	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136335	136335	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136344	136344	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-XA50-SUV-01	HIGH		READY
136345	136345	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136346	136346	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136347	136347	Hatchback	A-Class IV	W177	5	EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	HIGH		READY
136348	136348	MPV	B-Class III	W247	5	EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	HIGH		READY
136350	136350	Sedan	C-Class IV (facelift)	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136351	136351	Sedan	C-Class IV (facelift)	W205	4	EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	HIGH		READY
136352	136352	Wagon	C-Class IV (facelift)	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136353	136353	Wagon	C-Class IV (facelift)	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH		READY
136357	136357	Coupe	C-Class IV (facelift)	C205	2	EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	HIGH		READY
136358	136358	Convertible	C-Class IV (facelift)	A205	2	EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	HIGH		READY
136359	136359	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136362	136362	SUV	Range Rover IV (facelift)	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	HIGH		READY
136364	136364	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
136366	136366	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136367	136367	Hatchback	Soul III	SK3	5	EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	HIGH		READY
136369	136369	Coupe	M8 I	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
136370	136370	Coupe	M8 I	F92	2	EU-BMW-8-F92-M8-COUPE-01	HIGH		READY
136371	136371	Convertible	M8 I	F91	2	EU-BMW-8-F91-M8-CONVERTIBLE-01	HIGH		READY
136372	136372	Convertible	M8 I	F91	2	EU-BMW-8-F91-M8-CONVERTIBLE-01	HIGH		READY
136374	136374	SUV	X1 II (facelift)	F48	5	EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	HIGH		READY
136375_prefl	136375	Sedan	Passat B8 (pre-facelift)	3G2	4	EU-VW-PASSAT-B8-SEDAN-PREFL-01	HIGH	生产期覆盖改款前分支。	READY
136375_facelift	136375	Sedan	Passat B8 (facelift)	3G2	4	EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	HIGH	生产期覆盖改款后分支。	READY
136376_prefl	136376	Wagon	Passat B8 Variant (pre-facelift)	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	HIGH	生产期覆盖改款前分支。	READY
136376_facelift	136376	Wagon	Passat B8 Variant (facelift)	3G5	5	EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	HIGH	生产期覆盖改款后分支。	READY
136377_swb	136377	Sedan	S-Class VI (pre-facelift)	W222	4	EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	HIGH	标准轴距分支。	READY
136377_lwb	136377	Sedan	S-Class VI (pre-facelift)	V222	4	EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	HIGH	长轴距分支。	READY
136378	136378	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
136379	136379	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136380	136380	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136381	136381	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH		READY
136382	136382	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136383	136383	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
136384	136384	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH		READY
136385	136385	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH		READY
136386	136386	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
136387	136387	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
136388	136388	MPV	HiAce VI	H300	4	EU-TOYOTA-HIACE-VI-H300-COMMUTER-MPV-01	HIGH	Commuter 长车身高顶分支。	READY
136391	136391	Wagon	A6 allroad C8	4AH	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH	标准行驶高度分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3801-3900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-IV-WAGON-ST-01	4668	1825	1492	Auto-Data Ford Focus IV Wagon ST 2.3 EcoBoost	https://www.auto-data.net/en/ford-focus-iv-wagon-st-2.3-ecoboost-280hp-37683
EU-FORD-KUGA-II-FACELIFT-SUV-01	4531	1838	1703	Ford Kuga official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/FordKuga_TechnicalSpecifications_EU.pdf
EU-FORD-MONDEO-V-WAGON-FACELIFT-01	4867	1852	1501	Ford Mondeo official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Mondeo/FordMondeo_TechnicalSpecifications_EU.pdf
EU-KIA-CEED-III-CD-WAGON-01	4600	1800	1465	Kia Ceed Sportswagon official specifications	https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/All-New%20Ceed%20Sportswagon/specification/ceed-family-specification.pdf
EU-KIA-PROCEED-III-CD-WAGON-01	4605	1800	1422	Kia ProCeed official press kit	https://press.kia.com/es/es/home/notas-de-prensa/press-kits/2018/proceed.html
EU-KIA-SOUL-III-SK3-HATCHBACK-PETROL-01	4195	1800	1600	Kia Global Soul specifications	https://www.kia.com/nmc/en/showroom/soul/specification.html
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	Auto-Data Hyundai Tucson III specifications	https://www.auto-data.net/en/hyundai-tucson-iii-1.6-t-gdi-177hp-24693
EU-MERCEDES-BENZ-EQC-N293-SUV-01	4762	1884	1624	Auto-Data Mercedes-Benz EQC N293 EQC 400 4MATIC	https://www.auto-data.net/en/mercedes-benz-eqc-n293-eqc-400-85-kwh-408hp-4matic-34406
EU-MERCEDES-BENZ-GLC-X253-SUV-01	4656	1890	1639	Australian Car.Reviews Mercedes-Benz GLC X253	https://australiancar.reviews/review-mercedes-benz-x253-glc-2015-22/
EU-MERCEDES-BENZ-B-KLASSE-W247-MPV-01	4419	1796	1562	Auto-Data Mercedes-Benz B-Class W247 B 200	https://www.auto-data.net/en/mercedes-benz-b-class-w247-b-200-163hp-dct-35003
EU-DACIA-LODGY-MPV-01	4498	1751	1679	Dacia Lodgy official price and specification guide	https://cdn.group.renault.com/dac/ch/dacia-new-cars/pricelists/Dacia_Lodgy_PL_d.pdf
EU-RENAULT-TWINGO-III-X07-HATCHBACK-FACELIFT-01	3615	1646	1541	Auto-Data Renault Twingo III facelift 2019	https://www.auto-data.net/en/renault-twingo-iii-facelift-2019-generation-6847
EU-MITSUBISHI-ECLIPSE-CROSS-I-GK1W-SUV-01	4405	1805	1685	Mitsubishi Eclipse Cross official brochure	https://www.mitsubishi-motors.com.hk/uploads/file_1569567674.pdf
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo V60 official support dimensions	https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo XC40 official support dimensions	https://www.volvocars.com/uk/support/car/xc40/article/766ee075f0e03896c0a8015109ee0749/
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	Ford EcoSport official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/EcoSport/EcoSportSpecifications_EU.pdf
EU-SUBARU-LEVORG-I-VM-WAGON-FACELIFT-01	4690	1780	1490	Subaru Levorg MJ2019 official brochure	https://www.subaru.de/hubfs/Service%20und%20Zubeh%C3%B6r/Prospektarchiv/Levorg/Levorg_MJ2019_PTA.pdf?hsLang=de
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441	MINI Clubman official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252423EN/353092
EU-SKODA-KAROQ-I-NU7-SUV-PREFL-01	4382	1841	1603	Skoda Karoq official technical data	https://cdn.skoda-storyboard.com/2017/07/TD-KAROQ-en-1.pdf
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659	Audi Q5 official dimensions	https://www.audi.com/en/publications/dimensions/dimensions-q5-1417
EU-AUDI-A4-ALLROAD-B9-WAGON-01	4750	1842	1493	ADAC Audi A4 allroad 2.0 TFSI quattro specifications	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a4/b9-facelift-2/330893/
EU-MERCEDES-BENZ-MARCO-POLO-W447-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo ACTIVITY brochure	https://s3-ap-southeast-2.amazonaws.com/assets.i-motor.com.au/trucks/mercendes-benz-vans/pdfs/marco-polo/productBrochure.pdf
EU-STREETSCOOTER-WORK-BOX-VAN-01	4709	1925	2039	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PICKUP-01	4741	1814	1859	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-PURE-CHASSIS-01	4676	1796	1861	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-L-PICKUP-01	5840	1814	1859	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-L-PURE-CHASSIS-01	5784	1796	1867	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-STREETSCOOTER-WORK-L-BOX-VAN-01	5784	1925	2347	StreetScooter WORK and WORK L official brochure	https://www.streetscooter.com/wp-content/uploads/2019/01/StreetScooter-Brochure-EN-Web.pdf
EU-CITROEN-C5-AIRCROSS-I-C84-SUV-PREFL-01	4500	1859	1670	Citroën C5 Aircross official specification sheet	https://www.citroen.com.au/content/dam/citroen/australia/home/models/c5-aircross-suv/C5A.pdf
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	BMW 1 Series official brochure	https://www.bmw.co.za/content/dam/bmw/marketZA/bmw_co_za/Documents/brochures/bmw-1-series-brochure-2022.pdf.asset.1650352306018.pdf
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445	BMW 3 Series G20 official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0299451EN/specifications-of-the-all-new-bmw-3-series-sedan-valid-from-03/2019
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467	BMW M550i xDrive official technical data	https://www.press.bmwgroup.com/deutschland/article/attachment/T0268194DE/609785
EU-BMW-8-G15-840D-COUPE-01	4843	1902	1341	BMW 8 Series Coupe official press information	https://www.press.bmwgroup.com/global/article/detail/T0281744EN/the-all-new-bmw-8-series-coupe
EU-BMW-8-G14-840D-CONVERTIBLE-01	4843	1902	1339	BMW 8 Series Convertible official technical data	https://www.press.bmwgroup.com/switzerland/article/attachment/T0286523DE/417790
EU-BMW-X5-G05-SUV-PREFL-01	4922	2004	1745	BMW X5 official technical data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0281830EN_GB/419908
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404	Peugeot 508 official dimensions	https://www.peugeot.co.uk/content/peugeot/worldwide/uk/en/index/models/508-fastback.html
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1431	Volvo S60 2019 technical specifications	https://www.volvoclub.org.uk/pdf/s60/s60_2019_techspecs.pdf
EU-TOYOTA-RAV4-V-XA50-SUV-01	4600	1855	1685	Toyota RAV4 technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/220203M-RAV4-Tech-Spec.pdf
EU-MERCEDES-BENZ-A-KLASSE-W177-HATCHBACK-01	4419	1796	1440	Mercedes-Benz A-Class official press information	https://presse.mercedes-benz.at/news-die-neue-mercedes-benz-a-klasse-mercedes-benz-oesterreich?id=65202&imageid=195042&l=deutsch&menueid=0
EU-MERCEDES-BENZ-C-KLASSE-W205-SEDAN-FACELIFT-01	4686	1810	1442	Auto-Data Mercedes-Benz C-Class W205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-w205-facelift-2018-generation-6152
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	Auto-Data Mercedes-Benz C-Class S205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-generation-6153
EU-MERCEDES-BENZ-C-KLASSE-C205-COUPE-FACELIFT-01	4686	1810	1405	Auto-Data Mercedes-Benz C-Class C205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-coupe-c205-facelift-2018-c-300-258hp-eq-boost-9g-tronic-33195
EU-MERCEDES-BENZ-C-KLASSE-A205-CONVERTIBLE-FACELIFT-01	4686	1810	1409	Auto-Data Mercedes-Benz C-Class A205 facelift	https://www.auto-data.net/en/mercedes-benz-c-class-cabriolet-a205-facelift-2018-c-300-258hp-eq-boost-4matic-9g-tronic-52495
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-FACELIFT-01	5000	1983	1869	Land Rover full-line official catalogue	https://www.landrover.co.jp/content/dam/lrdx/pdfs/jp/20MY_LAND_ROVER_FullLineCatalog_1910.pdf
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo XC90 official support dimensions	https://www.volvocars.com/uk/support/car/xc90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo XC60 official support dimensions	https://www.volvocars.com/uk/support/car/xc60/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-KIA-SOUL-III-SK3-E-SOUL-HATCHBACK-01	4195	1800	1605	Kia e-Soul official brochure	https://www.kia.com/content/dam/kwcms/kme/ie/en/assets/contents/utilty/brochure/model-brochures/e-Soul-Brochure-2020.pdf
EU-BMW-8-F92-M8-COUPE-01	4867	1907	1362	BMW M8 Coupe official technical data	https://www.press.bmwgroup.com/netherlands/article/attachment/T0296706NL/431799
EU-BMW-8-F91-M8-CONVERTIBLE-01	4867	1907	1353	BMW M8 Convertible official technical data	https://www.press.bmwgroup.com/netherlands/article/attachment/T0296706NL/431800
EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	4447	1821	1582	BMW X1 xDrive25e official technical data	https://www.press.bmwgroup.com/spain/article/attachment/T0304339ES/444467
EU-VW-PASSAT-B8-SEDAN-PREFL-01	4767	1832	1456	Volkswagen Passat B8 official previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mid-size-class/passat-b8.html
EU-VW-PASSAT-B8-SEDAN-FACELIFT-01	4775	1832	1483	Automoli Volkswagen Passat B8 facelift specifications	https://www.automoli.com/en/vehicles/volkswagen/passat/passat-b8-facelift-2019-7177/
EU-VW-PASSAT-B8-VARIANT-WAGON-PREFL-01	4767	1832	1477	Volkswagen Passat B8 official previous-model specifications	https://www.volkswagen.ie/en/owners-and-services/previous-models/mid-size-class/passat-b8.html
EU-VW-PASSAT-B8-VARIANT-WAGON-FACELIFT-01	4773	1832	1516	Auto-Data Volkswagen Passat Variant B8 facelift	https://www.auto-data.net/en/volkswagen-passat-variant-b8-facelift-2019-generation-7176
EU-MERCEDES-BENZ-S-KLASSE-W222-S500-4MATIC-SEDAN-PREFL-SWB-01	5116	1899	1496	Automobile-Catalog Mercedes-Benz S 500 4MATIC	https://www.automobile-catalog.com/car/2014/1929530/mercedes-benz_s_500_4matic.html
EU-MERCEDES-BENZ-S-KLASSE-V222-S500-4MATIC-SEDAN-PREFL-LWB-01	5246	1899	1494	Automobile-Catalog Mercedes-Benz S 500 4MATIC Lang	https://www.automobile-catalog.com/car/2014/1929545/mercedes-benz_s_500_4matic_lang.html
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo S90 official support dimensions	https://www.volvocars.com/en-eg/support/car/s90/19w17/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo V90 official support dimensions	https://www.volvocars.com/jp/support/car/v90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	Volvo V90 Cross Country official support dimensions	https://www.volvocars.com/en-eg/support/car/v90-cross-country/16w46/article/871e942e897ca77dc0a801511788660a/
EU-TOYOTA-HIACE-VI-H300-COMMUTER-MPV-01	5915	1950	2280	CarExpert 2019 Toyota HiAce Commuter specifications	https://www.carexpert.com.au/toyota/hiace/2019-commuter-2-8l-bus-rwd-diesel-automatic-jo8gwkfo20190418
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497	Audi A6 allroad 50 TDI official technical data	https://press.audi.co.uk/assets/documents/original/16947-AudiA6allroad50TDIquattrotiptronicUKTechnicalDataJuly2021.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3801-3900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://media.ford.com/content/dam/fordmedia/Europe/documents/productReleases/Kuga/FordKuga_TechnicalSpecifications_EU.pdf "Ford Kuga Technical Specs PDF"
[2]: https://press.audi.co.uk/assets/documents/original/16947-AudiA6allroad50TDIquattrotiptronicUKTechnicalDataJuly2021.pdf?utm_source=chatgpt.com "Technical Data"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3427 行）
- 累计尺寸组：dimension_groups_final.tsv（1515 行）

