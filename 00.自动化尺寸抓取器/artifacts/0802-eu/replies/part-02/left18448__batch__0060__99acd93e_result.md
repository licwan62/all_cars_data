# 任务：left18448 第 5901-6000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0060__99acd93e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5901-6000 行

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
left18448.tsv

【当前独立任务】
left18448 第 5901-6000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5901-6000_ktype_dimension_mapping_final.tsv
- left18448_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FORD-SIERRA-I-HATCHBACK-3D-01	4394	1703	1408
EU-FORD-SIERRA-I-HATCHBACK-5D-01	4394	1703	1408
EU-FORD-SIERRA-II-HATCHBACK-3D-FACELIFT-01	4420	1689	1410
EU-FORD-SIERRA-II-HATCHBACK-3D-PREFL-01	4425	1694	1407
EU-FORD-SIERRA-II-HATCHBACK-5D-FACELIFT-01	4420	1689	1410
EU-FORD-SIERRA-II-HATCHBACK-5D-PREFL-01	4425	1694	1407
EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	4501	1698	1407
EU-FORD-SIERRA-II-SEDAN-PREFL-01	4467	1698	1407
EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	4544	1720	1476
EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	4511	1720	1410
EU-FORD-SIERRA-II-WAGON-FACELIFT-01	4544	1720	1488
EU-FORD-SIERRA-II-WAGON-PREFL-01	4511	1720	1428
EU-FORD-SIERRA-I-WAGON-4X4-01	4522	1729	1438
EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	4459	1728	1392
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-3D-01	4459	1725	1378
EU-FORD-SIERRA-I-XR4X4-HATCHBACK-5D-01	4459	1725	1378
EU-FORD-SIERRA-RS-COSWORTH-4X4-SEDAN-01	4494	1698	1376

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Sierra	2.8 Xr4i	Kombi	Heckantrieb	Benzin	Aug 1982	Dec 1986	15590
Ford	Sierra	2.9 4X4	Stufenheck	Allrad	Benzin	Aug 1988	Feb 1993	15022
Ford	Sierra	2.9 4X4	Stufenheck	Allrad	Benzin	Aug 1988	Feb 1993	15023
Ford	Sierra	2.9 4X4	Kombi	Allrad	Benzin	Aug 1988	Feb 1993	15030
Ford	Sierra	2.9 I	Stufenheck	Heckantrieb	Benzin	Aug 1988	Feb 1993	15024
Ford	Sierra	2.9 I	Kombi	Heckantrieb	Benzin	Aug 1988	Feb 1993	15029
Ford	S-Max	1.6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Feb 2011	Dec 2014	143085
Ford	S-Max	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2010	Dec 2014	143086
Ford	S-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Jun 2018	111790
Ford	S-Max	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2010	Dec 2014	59495
Ford	S-Max	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Apr 2023	111791
Ford	S-Max	2.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2010	Dec 2014	143087
Ford	S-Max	2.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Jul 2010	Dec 2014	143088
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	111792
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	111794
Ford	S-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	111796
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Jan 2007	Dec 2014	143089
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2010	Dec 2014	143090
Ford	S-Max	2.0 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2010	Dec 2014	143091
Ford	S-Max	2.0 Tdci 4X4	Großraumlimousine	Allrad	Diesel	Jan 2015	Jun 2018	111795
Ford	S-Max	2.0 Tdci 4X4	Großraumlimousine	Allrad	Diesel	Jan 2015	Jun 2018	111797
Ford	S-Max	2.0 Tdci Bi-turbo	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	111798
Ford	S-Max	2.5 Fhev	Großraumlimousine	Frontantrieb	Benzin/Elektro	Jul 2021	Apr 2023	146681
Ford	Street ka	1.6	Cabriolet	Frontantrieb	Benzin	May 2003	Jul 2005	17114
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	Sep 1976	Jul 1979	6569
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	Jan 1976	Jul 1979	125827
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	Jan 1976	Jul 1979	125828
Ford	Taunus	1.3	Kombi	Heckantrieb	Benzin	Jan 1976	Jul 1979	125829
Ford	Taunus	1.3	Coupe	Heckantrieb	Benzin	Apr 1972	Feb 1976	125830
Ford	Taunus	1.3	Stufenheck	Heckantrieb	Benzin	Jul 1979	Jul 1982	125838
Ford	Taunus	1.5	Kombi	Heckantrieb	Benzin	Nov 1964	Oct 1967	6519
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6521
Ford	Taunus	1.5	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6528
Ford	Taunus	1.5	Kombi	Heckantrieb	Benzin	Sep 1967	Apr 1974	6539
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	Aug 1976	Jul 1979	17638
Ford	Taunus	1.6	Stufenheck	Heckantrieb	Benzin	Jul 1979	Jul 1982	17639
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	Nov 1964	Oct 1967	6520
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6522
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6523
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Dec 1967	Apr 1974	6524
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6529
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6530
Ford	Taunus	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1968	Apr 1974	6531
Ford	Taunus	1.7	Coupe	Heckantrieb	Benzin	Jul 1967	Apr 1974	6534
Ford	Taunus	1.7	Coupe	Heckantrieb	Benzin	Aug 1968	Apr 1974	6535
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	Sep 1967	Apr 1974	6540
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	Jan 1968	Apr 1974	6541
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	Sep 1967	Apr 1974	6542
Ford	Taunus	1.7	Kombi	Heckantrieb	Benzin	Aug 1968	Apr 1974	6543
Ford	Taunus	1.8	Stufenheck	Heckantrieb	Benzin	Dec 1967	Apr 1974	6525
Ford	Taunus	1.8	Stufenheck	Heckantrieb	Benzin	Aug 1968	Apr 1974	6532
Ford	Taunus	1.8	Coupe	Heckantrieb	Benzin	Aug 1968	Apr 1974	6536
Ford	Taunus	1.8	Kombi	Heckantrieb	Benzin	Jan 1968	Apr 1974	6544
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Dec 1967	Apr 1974	6526
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Dec 1967	Apr 1974	6527
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Dec 1967	Apr 1974	6533
Ford	Taunus	2	Coupe	Heckantrieb	Benzin	Dec 1967	Apr 1974	6537
Ford	Taunus	2	Kombi	Heckantrieb	Benzin	Jan 1968	Apr 1974	6545
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Nov 1964	Oct 1968	6546
Ford	Taunus	2	Kombi	Heckantrieb	Benzin	Nov 1964	Oct 1968	6548
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6549
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6550
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6552
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6553
Ford	Taunus	2	Kombi	Heckantrieb	Benzin	Sep 1967	Apr 1974	6556
Ford	Taunus	2	Kombi	Heckantrieb	Benzin	Jul 1967	Apr 1974	6557
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jan 1968	Apr 1974	6559
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6560
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jan 1968	Apr 1974	6562
Ford	Taunus	2	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6563
Ford	Taunus	2	Coupe	Heckantrieb	Benzin	Jul 1967	Apr 1974	6565
Ford	Taunus	2	Kombi	Heckantrieb	Benzin	Jul 1979	Jul 1982	15505
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6551
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6554
Ford	Taunus	2.3	Coupe	Heckantrieb	Benzin	Jul 1967	Apr 1974	6555
Ford	Taunus	2.3	Kombi	Heckantrieb	Benzin	Jan 1968	Apr 1974	6558
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6561
Ford	Taunus	2.3	Stufenheck	Heckantrieb	Benzin	Jul 1967	Apr 1974	6564
Ford	Taunus	2.3	Coupe	Heckantrieb	Benzin	Jul 1967	Apr 1974	6566
Ford	Taunus	2.3	Kombi	Heckantrieb	Benzin	May 1975	Jul 1979	15232
Ford	Taunus	2.3	Kombi	Heckantrieb	Benzin	Jul 1979	Jul 1982	15233
Ford	Taunus	2.5	Stufenheck	Heckantrieb	Benzin	Oct 1969	Apr 1974	6567
Ford	Taunus	2.5	Coupe	Heckantrieb	Benzin	Oct 1969	Apr 1974	6568
Ford	Taunus	1300	Coupe	Heckantrieb	Benzin	Aug 1970	Feb 1976	6572
Ford	Taunus	1300	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6578
Ford	Taunus	1300	Kombi	Heckantrieb	Benzin	Aug 1970	Feb 1976	6582
Ford	Taunus	1600	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6570
Ford	Taunus	1600	Coupe	Heckantrieb	Benzin	Aug 1970	Feb 1976	6573
Ford	Taunus	1600	Coupe	Heckantrieb	Benzin	Aug 1970	Feb 1976	6574
Ford	Taunus	1600	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6579
Ford	Taunus	1600	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6580
Ford	Taunus	1600	Kombi	Heckantrieb	Benzin	Aug 1970	Feb 1976	6583
Ford	Taunus	1600	Stufenheck	Heckantrieb	Benzin	Jan 1974	May 1975	11163
Ford	Taunus	1600	Kombi	Heckantrieb	Benzin	Jan 1974	May 1975	11164
Ford	Taunus	2.0 TS	Stufenheck	Heckantrieb	Benzin	Nov 1964	Oct 1968	6547
Ford	Taunus	2000 V6	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6571
Ford	Taunus	2000 V6	Coupe	Heckantrieb	Benzin	Aug 1970	Feb 1976	6575
Ford	Taunus	2000 V6	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	6581
Ford	Taunus	2300 Gt,gxl	Stufenheck	Heckantrieb	Benzin	Aug 1970	Feb 1976	121991
Ford	Taunus	2300 V6	Coupe	Heckantrieb	Benzin	Aug 1971	Feb 1976	6576


--- Round 1 / 首次发送 ---
## 更新点

* Sierra 现有缓存组已直接复用：XR4i 修正为三门 Hatchback；1988–1993 的 Sedan、Wagon 与 Wagon 4X4 因生产区间跨越既有改款前后尺寸边界，拆分为 `prefl`、`facelift` 派生行，不重复建立尺寸组。XR4i 确为特殊三门 Sierra 车身。([维基百科][1])
* 闭合 S-MAX 三个物理外廓：第一代 WA6 为 `4768×1884×1658`；第二代改款前 CJ 为 `4796×1916×1655`；2019 改款后的 2021 FHEV 采用官方规格表的 `4804×1916×1684`。
* `Kasten/Großraumlimousine` 行属于 S-MAX Van/MPV 的 WA6 五门外廓，未因后舱用途名称重复建组。第一代代码 WA6、第二代代码 CJ 均已核对。([维修手册网站][2])
* StreetKa 已闭合为 RL2 双门 Convertible，尺寸 `3650×1679×1342`。([汽车数据网][3])

## 当前批次进度

* 已覆盖输入 Ktype：24 / 100
* READY 映射行：29
* 尚待处理输入 Ktype：76
* 当前批次已确认尺寸组：11

  * 复用跨批次既有组：7
  * 本轮首次创建：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15590	15590	Hatchback	Sierra I		3	EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	HIGH	输入Kombi修正为XR4i专用三门掀背外廓。	READY
15022_prefl	15022	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15022_facelift	15022	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15023_prefl	15023	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15023_facelift	15023	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15030_prefl	15030	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四驱五门旅行车外廓。	READY
15030_facelift	15030	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四驱五门旅行车外廓。	READY
15024_prefl	15024	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15024_facelift	15024	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15029_prefl	15029	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前五门旅行车外廓。	READY
15029_facelift	15029	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后五门旅行车外廓。	READY
143085	143085	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143086	143086	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111790	111790	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
59495	59495	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH		READY
111791	111791	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
143087	143087	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143088	143088	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111792	111792	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111794	111794	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111796	111796	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
143089	143089	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143090	143090	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143091	143091	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111795	111795	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111797	111797	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111798	111798	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
146681	146681	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-FACELIFT-01	HIGH	2019改款后FHEV五门MPV外廓。	READY
17114	17114	Convertible	StreetKa	RL2	2	EU-FORD-STREETKA-RL2-CONVERTIBLE-01	HIGH		READY
```

Sierra 派生行引用任务提供的既有尺寸组；S-MAX 与 StreetKa 的代码、门数和外廓由上述车型目录及规格来源支撑。([维修手册网站][2])

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658	Ford S-MAX 2011 official brochure	https://xr793.org/wp-content/uploads/2020/09/2011-Ford-S-Max-UK.pdf
EU-FORD-S-MAX-II-MPV-PREFL-01	4796	1916	1655	Ford S-MAX official eBrochure	https://www.cavanaghs.com/wp-content/uploads/2016/11/S_MAX_eBrochure.pdf
EU-FORD-S-MAX-II-MPV-FACELIFT-01	4804	1916	1684	Ford S-MAX 21.5MY official brochure specification table	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Ford-Smax.pdf
EU-FORD-STREETKA-RL2-CONVERTIBLE-01	3650	1679	1342	Auto-Data Ford StreetKa (RL2) 1.6i (95 Hp)	https://www.auto-data.net/en/ford-streetka-rl2-1.6i-95hp-45980
```

S-MAX 第一代尺寸来自官方 brochure 的尺寸表；第二代改款前与改款后分别采用对应 brochure 规格表，而不是宣传页中的简化示意数字。

## 下一步优先处理

1. 先按时间与车身形式聚类 Taunus：1964–1967、1967–1974、1970–1976、1976–1979、1979–1982。
2. 优先闭合重复引用最多的 1967–1974 Sedan、Coupe、Wagon 三个外廓，再批量关联对应 Ktype。
3. 单独核对 1970–1976 与 1976–1979 数据区间重叠是否代表不同 Taunus 代际，避免仅按发动机名称误复用。

推进信号：CONTINUE

[1]: https://en.wikipedia.org/wiki/Ford_Sierra?utm_source=chatgpt.com "Ford Sierra"
[2]: https://workshop-manuals.com/ford/s-max.galaxy_2006.5_03.2006/mechanical_repairs/1_general_information/100_service_information/100-01_identification_codes/description_and_operation/identification_codes/?utm_source=chatgpt.com "Ford Workshop Service and Repair Manuals > S-MAX.Galaxy 2006.5 (03.2006-) > Mechanical Repairs | 1 General Information | 100 Service Information | 100-01 Identification Codes | Description and Operation | Identification Codes"
[3]: https://www.auto-data.net/en/ford-streetka-rl2-1.6i-95hp-45980?utm_source=chatgpt.com "Specs of Ford Streetka (RL2) 1.6i (95 Hp) /2002, 2003, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5901-6000_ktype_dimension_mapping_final.tsv
- left18448_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已按缓存优先模式完成剩余 Taunus Ktype：闭合 P5、P7A、P7B、TC1、TC2、TC3，并按 Sedan、Coupe、Wagon、改款边界及保险杠外廓批量关联。([汽车目录][1])
* 修正 S-MAX Ktype `111791`：生产区间跨越 2019 改款，拆分为 `prefl` 与 `facelift`；FHEV 继续使用独立高度尺寸组。([汽车数据网][2])
* 已完成一次机械收尾：表头、唯一主键、100 个输入 Ktype 覆盖、映射引用闭合、尺寸及来源完整、孤立尺寸组检查均通过。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：149
* PENDING 映射：0
* DIMENSION_GROUP：30
* 复用既有 Sierra 尺寸组：7
* 当前批次首次创建尺寸组：23
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
15590	15590	Hatchback	Sierra I		3	EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	HIGH	输入Kombi修正为XR4i专用三门掀背外廓。	READY
15022_prefl	15022	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15022_facelift	15022	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15023_prefl	15023	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15023_facelift	15023	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15030_prefl	15030	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四驱五门旅行车外廓。	READY
15030_facelift	15030	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四驱五门旅行车外廓。	READY
15024_prefl	15024	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前四门轿车外廓。	READY
15024_facelift	15024	Sedan	Sierra II		4	EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后四门轿车外廓。	READY
15029_prefl	15029	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-PREFL-01	MEDIUM	生产区间跨改款，拆分为改款前五门旅行车外廓。	READY
15029_facelift	15029	Wagon	Sierra II		5	EU-FORD-SIERRA-II-WAGON-FACELIFT-01	MEDIUM	生产区间跨改款，拆分为改款后五门旅行车外廓。	READY
143085	143085	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143086	143086	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111790	111790	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
59495	59495	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH		READY
111791_prefl	111791	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH	生产区间跨2019改款车身边界。	READY
111791_facelift	111791	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-FACELIFT-PETROL-01	HIGH	生产区间跨2019改款车身边界。	READY
143087	143087	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143088	143088	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111792	111792	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111794	111794	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111796	111796	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
143089	143089	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143090	143090	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
143091	143091	MPV	S-MAX I	WA6	5	EU-FORD-S-MAX-I-MPV-01	HIGH	Kasten/Großraumlimousine按WA6五门MPV外廓归并。	READY
111795	111795	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111797	111797	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
111798	111798	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-PREFL-01	HIGH		READY
146681	146681	MPV	S-MAX II	CJ	5	EU-FORD-S-MAX-II-MPV-FACELIFT-HYBRID-01	HIGH	2019改款后FHEV五门MPV外廓。	READY
17114	17114	Convertible	StreetKa	RL2	2	EU-FORD-STREETKA-RL2-CONVERTIBLE-01	HIGH		READY
6569	6569	Sedan	Taunus TC2			EU-FORD-TAUNUS-TC2-SEDAN-01	HIGH		READY
125827	125827	Sedan	Taunus TC2			EU-FORD-TAUNUS-TC2-SEDAN-01	HIGH		READY
125828	125828	Sedan	Taunus TC2			EU-FORD-TAUNUS-TC2-SEDAN-01	HIGH		READY
125829	125829	Wagon	Taunus TC2			EU-FORD-TAUNUS-TC2-WAGON-STANDARD-01	MEDIUM	1.3标准保险杠旅行车外廓。	READY
125830	125830	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
125838	125838	Sedan	Taunus TC3			EU-FORD-TAUNUS-TC3-SEDAN-STANDARD-01	MEDIUM	1.3标准保险杠轿车外廓。	READY
6519	6519	Wagon	Taunus P5			EU-FORD-TAUNUS-P5-WAGON-01	HIGH		READY
6521_p7a	6521	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6521_p7b	6521	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6528_p7a	6528	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6528_p7b	6528	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6539_p7a	6539	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6539_p7b	6539	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
17638	17638	Sedan	Taunus TC2			EU-FORD-TAUNUS-TC2-SEDAN-01	HIGH		READY
17639_standard	17639	Sedan	Taunus TC3			EU-FORD-TAUNUS-TC3-SEDAN-STANDARD-01	MEDIUM	TC3标准保险杠轿车外廓。	READY
17639_longbumper	17639	Sedan	Taunus TC3			EU-FORD-TAUNUS-TC3-SEDAN-LONGBUMPER-01	MEDIUM	TC3长保险杠轿车外廓。	READY
6520	6520	Wagon	Taunus P5			EU-FORD-TAUNUS-P5-WAGON-01	HIGH		READY
6522_p7a	6522	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6522_p7b	6522	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6523_p7a	6523	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6523_p7b	6523	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6524_p7a	6524	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6524_p7b	6524	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6529_p7a	6529	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6529_p7b	6529	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6530_p7a	6530	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6530_p7b	6530	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6531	6531	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	HIGH		READY
6534_p7a	6534	Coupe	Taunus P7A		2	EU-FORD-TAUNUS-P7A-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6534_p7b	6534	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6535	6535	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	HIGH		READY
6540_p7a	6540	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6540_p7b	6540	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6541_p7a	6541	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6541_p7b	6541	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6542_p7a	6542	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6542_p7b	6542	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6543	6543	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	HIGH		READY
6525_p7a	6525	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6525_p7b	6525	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6532	6532	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	HIGH		READY
6536	6536	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	HIGH		READY
6544_p7a	6544	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6544_p7b	6544	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6526_p7a	6526	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6526_p7b	6526	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6527_p7a	6527	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6527_p7b	6527	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6533_p7a	6533	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6533_p7b	6533	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6537_p7a	6537	Coupe	Taunus P7A		2	EU-FORD-TAUNUS-P7A-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6537_p7b	6537	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6545_p7a	6545	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6545_p7b	6545	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6546_p5	6546	Sedan	Taunus P5			EU-FORD-TAUNUS-P5-SEDAN-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6546_p7a	6546	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6548_p5	6548	Wagon	Taunus P5			EU-FORD-TAUNUS-P5-WAGON-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6548_p7a	6548	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6549_p7a	6549	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6549_p7b	6549	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6550_p7a	6550	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6550_p7b	6550	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6552_p7a	6552	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6552_p7b	6552	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6553_p7a	6553	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6553_p7b	6553	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6556_p7a	6556	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6556_p7b	6556	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6557_p7a	6557	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6557_p7b	6557	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6559_p7a	6559	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6559_p7b	6559	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6560_p7a	6560	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6560_p7b	6560	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6562_p7a	6562	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6562_p7b	6562	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6563_p7a	6563	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6563_p7b	6563	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6565_p7a	6565	Coupe	Taunus P7A		2	EU-FORD-TAUNUS-P7A-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6565_p7b	6565	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
15505_standard	15505	Wagon	Taunus TC3			EU-FORD-TAUNUS-TC3-WAGON-STANDARD-01	MEDIUM	TC3标准保险杠旅行车外廓。	READY
15505_longbumper	15505	Wagon	Taunus TC3			EU-FORD-TAUNUS-TC3-WAGON-LONGBUMPER-01	MEDIUM	TC3长保险杠旅行车外廓。	READY
6551_p7a	6551	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6551_p7b	6551	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6554_p7a	6554	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6554_p7b	6554	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6555_p7a	6555	Coupe	Taunus P7A		2	EU-FORD-TAUNUS-P7A-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6555_p7b	6555	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6558_p7a	6558	Wagon	Taunus P7A			EU-FORD-TAUNUS-P7A-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6558_p7b	6558	Wagon	Taunus P7B			EU-FORD-TAUNUS-P7B-WAGON-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6561_p7a	6561	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6561_p7b	6561	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6564_p7a	6564	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6564_p7b	6564	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6566_p7a	6566	Coupe	Taunus P7A		2	EU-FORD-TAUNUS-P7A-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
6566_p7b	6566	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	MEDIUM	生产区间跨P7A/P7B改款车身边界。	READY
15232_tc1	15232	Wagon	Taunus TC1			EU-FORD-TAUNUS-TC1-WAGON-01	MEDIUM	生产区间跨TC1/TC2换代车身边界。	READY
15232_tc2	15232	Wagon	Taunus TC2			EU-FORD-TAUNUS-TC2-WAGON-LONGBUMPER-01	MEDIUM	生产区间跨TC1/TC2换代车身边界；2.3长保险杠外廓。	READY
15233	15233	Wagon	Taunus TC3			EU-FORD-TAUNUS-TC3-WAGON-LONGBUMPER-01	MEDIUM	2.3长保险杠旅行车外廓。	READY
6567	6567	Sedan	Taunus P7B			EU-FORD-TAUNUS-P7B-SEDAN-01	HIGH		READY
6568	6568	Coupe	Taunus P7B		2	EU-FORD-TAUNUS-P7B-COUPE-01	HIGH		READY
6572	6572	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
6578	6578	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6582	6582	Wagon	Taunus TC1			EU-FORD-TAUNUS-TC1-WAGON-01	HIGH		READY
6570	6570	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6573	6573	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
6574	6574	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
6579	6579	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6580	6580	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6583	6583	Wagon	Taunus TC1			EU-FORD-TAUNUS-TC1-WAGON-01	HIGH		READY
11163	11163	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
11164	11164	Wagon	Taunus TC1			EU-FORD-TAUNUS-TC1-WAGON-01	HIGH		READY
6547_p5	6547	Sedan	Taunus P5			EU-FORD-TAUNUS-P5-SEDAN-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6547_p7a	6547	Sedan	Taunus P7A			EU-FORD-TAUNUS-P7A-SEDAN-01	MEDIUM	生产区间跨P5/P7A车身边界。	READY
6571	6571	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6575	6575	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
6581	6581	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
121991	121991	Sedan	Taunus TC1			EU-FORD-TAUNUS-TC1-SEDAN-01	HIGH		READY
6576	6576	Coupe	Taunus TC1		2	EU-FORD-TAUNUS-TC1-COUPE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5901-6000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-SIERRA-I-XR4I-HATCHBACK-3D-01	4459	1728	1392	Automobile-Catalog Ford Sierra XR4i	https://www.automobile-catalog.com/car/1983/30050/ford_sierra_xr4i.html
EU-FORD-SIERRA-II-SEDAN-PREFL-01	4467	1698	1407	Automobile-Catalog Ford Sierra 4-dr 2.0 Ghia	https://www.automobile-catalog.com/car/1989/934010/ford_sierra_4-dr_2_0_ghia.html
EU-FORD-SIERRA-II-SEDAN-FACELIFT-01	4501	1698	1407	Automobile-Catalog Ford Sierra 4-dr 2.9i Ghia	https://www.automobile-catalog.com/car/1992/936170/ford_sierra_4-dr_2_9i_ghia_cat.html
EU-FORD-SIERRA-II-WAGON-4X4-PREFL-01	4511	1720	1410	Automobile-Catalog Ford Sierra Estate 2.9i Ghia 4x4	https://www.automobile-catalog.com/car/1989/934715/ford_sierra_estate_2_9i_ghia_4x4.html
EU-FORD-SIERRA-II-WAGON-4X4-FACELIFT-01	4544	1720	1476	Automobile-Catalog Ford Sierra Estate 2.0i DOHC Ghia 4x4	https://www.automobile-catalog.com/car/1992/935750/ford_sierra_estate_2_0i_dohc_ghia_4x4.html
EU-FORD-SIERRA-II-WAGON-PREFL-01	4511	1720	1428	Auto-Data Ford Sierra Turnier II	https://www.auto-data.net/en/ford-sierra-turnier-ii-generation-1687
EU-FORD-SIERRA-II-WAGON-FACELIFT-01	4544	1720	1488	Automobile-Catalog Ford Sierra Estate 2.0i DOHC Ghia	https://www.automobile-catalog.com/car/1992/935600/ford_sierra_estate_2_0i_dohc_ghia.html
EU-FORD-S-MAX-I-MPV-01	4768	1884	1658	Ford S-MAX 2011 official brochure	https://xr793.org/wp-content/uploads/2020/09/2011-Ford-S-Max-UK.pdf
EU-FORD-S-MAX-II-MPV-PREFL-01	4796	1916	1655	Ford S-MAX official eBrochure	https://www.cavanaghs.com/wp-content/uploads/2016/11/S_MAX_eBrochure.pdf
EU-FORD-S-MAX-II-MPV-FACELIFT-PETROL-01	4804	1916	1655	Auto-Data Ford S-MAX II facelift 1.5 EcoBoost	https://www.auto-data.net/en/ford-s-max-ii-facelift-2019-1.5-ecoboost-165hp-39276
EU-FORD-S-MAX-II-MPV-FACELIFT-HYBRID-01	4804	1916	1684	Ford S-MAX Hybrid 2021 official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2021/02/S-MaxGalaxy/Ford_S-MAX-Hybrid_GALAXY-Hybrid_2021_TechSpecs_EU.pdf
EU-FORD-STREETKA-RL2-CONVERTIBLE-01	3650	1679	1342	Auto-Data Ford StreetKa (RL2) 1.6i	https://www.auto-data.net/en/ford-streetka-rl2-1.6i-95hp-45980
EU-FORD-TAUNUS-TC2-SEDAN-01	4380	1700	1362	Automobile-Catalog Ford Taunus 2.0 S	https://www.automobile-catalog.com/car/1976/920885/ford_taunus_2_0_s_automatic.html
EU-FORD-TAUNUS-TC2-WAGON-STANDARD-01	4440	1700	1366	Automobile-Catalog Ford Taunus Turnier 1.3 L	https://www.automobile-catalog.com/car/1976/921230/ford_taunus_turnier_1_3_l_low_compr_.html
EU-FORD-TAUNUS-TC1-COUPE-01	4267	1708	1341	Automobile-Catalog Ford Taunus 1300 L Coupe	https://www.automobile-catalog.com/car/1971/911990/ford_taunus_1300_l_coupe.html
EU-FORD-TAUNUS-TC3-SEDAN-STANDARD-01	4340	1706	1363	Automobile-Catalog Ford Taunus 1.3	https://www.automobile-catalog.com/car/1980/921815/ford_taunus_1_3.html
EU-FORD-TAUNUS-P5-WAGON-01	4585	1715	1500	Automobile-Catalog Ford Taunus 17M Turnier 1.5L	https://www.automobile-catalog.com/car/1966/900770/ford_taunus_17m_turnier_1_5l.html
EU-FORD-TAUNUS-P7A-SEDAN-01	4663	1756	1494	Automobile-Catalog Ford 17M 1500	https://www.automobile-catalog.com/car/1967/901160/ford_17m_1500_4-speed.html
EU-FORD-TAUNUS-P7B-SEDAN-01	4721	1756	1478	Automobile-Catalog Ford 17M 1700	https://www.automobile-catalog.com/car/1969/901835/ford_17m_1700.html
EU-FORD-TAUNUS-P7A-WAGON-01	4627	1756	1500	Automobile-Catalog Ford 17M Turnier 1700	https://www.automobile-catalog.com/car/1967/901280/ford_17m_turnier_1700.html
EU-FORD-TAUNUS-P7B-WAGON-01	4673	1756	1473	Automobile-Catalog Ford 17M Turnier 1700	https://www.automobile-catalog.com/car/1969/901955/ford_17m_turnier_1700.html
EU-FORD-TAUNUS-TC3-SEDAN-LONGBUMPER-01	4382	1706	1363	Automobile-Catalog Ford Taunus 2.0 GL	https://www.automobile-catalog.com/car/1980/940895/ford_taunus_2_0_gl.html
EU-FORD-TAUNUS-P7A-COUPE-01	4736	1756	1494	Automobile-Catalog Ford 17M Hardtop	https://www.automobile-catalog.com/car/1967/901100/ford_17m_hardtop.html
EU-FORD-TAUNUS-P7B-COUPE-01	4721	1756	1464	Automobile-Catalog Ford 17M Hardtop 1700	https://www.automobile-catalog.com/car/1969/903035/ford_17m_hardtop_1700.html
EU-FORD-TAUNUS-P5-SEDAN-01	4585	1715	1480	Automobile-Catalog Ford Taunus 17M 1.5L	https://www.automobile-catalog.com/car/1966/900695/ford_taunus_17m_1_5l.html
EU-FORD-TAUNUS-TC3-WAGON-STANDARD-01	4440	1712	1355	Automobile-Catalog Ford Taunus Turnier 2.0 V6 L	https://www.automobile-catalog.com/car/1979/922265/ford_taunus_turnier_2_0_v6_l.html
EU-FORD-TAUNUS-TC3-WAGON-LONGBUMPER-01	4481	1712	1355	Automobile-Catalog Ford Taunus Turnier 2.0 GL	https://www.automobile-catalog.com/car/1981/922385/ford_taunus_turnier_2_0_gl.html
EU-FORD-TAUNUS-TC1-WAGON-01	4369	1701	1393	Automobile-Catalog Ford Taunus Turnier 1600 L	https://www.automobile-catalog.com/car/1971/911825/ford_taunus_turnier_1600_l.html
EU-FORD-TAUNUS-TC2-WAGON-LONGBUMPER-01	4480	1700	1366	Automobile-Catalog Ford Taunus Turnier 2.0 V6 L	https://www.automobile-catalog.com/car/1978/921395/ford_taunus_turnier_2_0_v6_l.html
EU-FORD-TAUNUS-TC1-SEDAN-01	4267	1701	1370	Automobile-Catalog Ford Taunus 1300	https://www.automobile-catalog.com/car/1971/911405/ford_taunus_1300.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5901-6000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1966/900695/ford_taunus_17m_1_5l.html?utm_source=chatgpt.com "1966 Ford Taunus 17M 1.5L Specs Review (44 kW / 60 PS / 59 hp) (for Europe )"
[2]: https://www.auto-data.net/en/ford-s-max-ii-facelift-2019-1.5-ecoboost-165hp-39276?utm_source=chatgpt.com "Ford S-MAX II (facelift 2019) 1.5 EcoBoost (165 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（2162 行）
- 累计尺寸组：dimension_groups_final.tsv（527 行）

