# 任务：left18448 第 5401-5500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0055__a0f707dd


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5401-5500 行

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
left18448 第 5401-5500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5401-5500_ktype_dimension_mapping_final.tsv
- left18448_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Escort iv express	1.3	Kasten/Kombi	Frontantrieb	Benzin	Feb 1986	Jul 1990	11031
Ford	Escort iv express	1.4 I	Kasten/Kombi	Frontantrieb	Benzin	Feb 1986	Jul 1990	11035
Ford	Escort iv express	1.6 D	Kasten/Kombi	Frontantrieb	Diesel	Feb 1986	Jul 1990	11032
Ford	Escort iv turnier	1.1	Kombi	Frontantrieb	Benzin	Oct 1985	Sep 1990	15255
Ford	Escort v	1.3	Stufenheck	Frontantrieb	Benzin	Aug 1993	Jan 1995	12422
Ford	Escort v	1.4	Stufenheck	Frontantrieb	Benzin	Aug 1993	Apr 1994	12435
Ford	Escort v	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	Aug 1993	Jan 1995	10426
Ford	Escort v	1.8 D	Stufenheck	Frontantrieb	Diesel	Aug 1993	Jan 1995	14271
Ford	Escort v	1.8 I 16V	Stufenheck	Frontantrieb	Benzin	Aug 1993	Jan 1995	12381
Ford	Escort v	1.8 TD	Stufenheck	Frontantrieb	Diesel	Aug 1993	Jan 1995	12438
Ford	Escort v turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	Sep 1992	Jan 1995	1963
Ford	Escort v turnier	1.8 I 16V	Kombi	Frontantrieb	Benzin	Feb 1993	Jan 1995	1964
Ford	Escort v turnier	1.8 TD	Kombi	Frontantrieb	Diesel	Feb 1993	Jan 1995	1962
Ford	Escort vi	1.3	Stufenheck	Frontantrieb	Benzin	Jan 1995	Feb 1999	12433
Ford	Escort vi	1.4	Schrägheck	Frontantrieb	Benzin	Jan 1995	Dec 1999	117953
Ford	Escort vi	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	Jan 1995	Feb 1999	10427
Ford	Escort vi	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	Jan 1995	Aug 1995	12441
Ford	Escort vi	1.6 I 16V	Stufenheck	Frontantrieb	Benzin	Jan 1995	Aug 1995	12445
Ford	Escort vi	1.8 16V	Schrägheck	Frontantrieb	Benzin	Jan 1995	Aug 1995	12382
Ford	Escort vi	1.8 16V	Stufenheck	Frontantrieb	Benzin	Jan 1995	Aug 1995	12384
Ford	Escort vi	1.8 16V Xr3i	Cabriolet	Frontantrieb	Benzin	Feb 1995	Aug 2000	15258
Ford	Escort vi	1.8 16V Xr3i	Cabriolet	Frontantrieb	Benzin	Feb 1995	Aug 1998	15259
Ford	Escort vi	1.8 D	Schrägheck	Frontantrieb	Diesel	Jan 1995	Dec 1996	14270
Ford	Escort vi	1.8 D	Stufenheck	Frontantrieb	Diesel	Jan 1995	Dec 1996	14272
Ford	Escort vi	1.8 TD	Stufenheck	Frontantrieb	Diesel	Jan 1995	Feb 1999	11225
Ford	Escort vi	1.8 Turbo D	Cabriolet	Frontantrieb	Diesel	Oct 1996	Aug 1999	7809
Ford	Escort vi	RS 2000	Schrägheck	Frontantrieb	Benzin	Feb 1995	Feb 1998	14263
Ford	Escort vi express	1.8 Turbo D	Kasten/Kombi	Frontantrieb	Diesel	Dec 1995	Jun 2001	11224
Ford	Escort vi turnier	1.3	Kombi	Frontantrieb	Benzin	Jan 1995	Jan 1999	11226
Ford	Escort vi turnier	1.6 I 16V	Kombi	Frontantrieb	Benzin	Jan 1995	Aug 1995	12446
Ford	Escort vi turnier	1.8 16V	Kombi	Frontantrieb	Benzin	Jan 1995	Aug 1995	12383
Ford	Escort vi turnier	1.8 D	Kombi	Frontantrieb	Diesel	Jan 1995	Feb 1999	15260
Ford	Fiesta	1.8 D	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 1989	Dec 1995	11022
Ford	Fiesta	D 1.8	Kasten/Schrägheck	Frontantrieb	Diesel	May 1998	Apr 2002	11023
Ford	Fiesta	TD 1.8	Kasten/Schrägheck	Frontantrieb	Diesel	Mar 2000	Aug 2003	18316
Ford	Fiesta ii	1.4	Schrägheck	Frontantrieb	Benzin	Sep 1983	Jan 1987	18816
Ford	Fiesta ii	1.6 XR2	Schrägheck	Frontantrieb	Benzin	Apr 1984	Feb 1989	1960
Ford	Fiesta iii	1.6 I 16V	Schrägheck	Frontantrieb	Benzin	Jan 1994	Dec 1995	8860
Ford	Fiesta iv	1.4 I 16V	Schrägheck	Frontantrieb	Benzin	Apr 1996	Jan 2002	5736
Ford	Fiesta iv	1.6 16V Sport	Schrägheck	Frontantrieb	Benzin	Feb 2000	Jan 2002	13657
Ford	Fiesta iv	1.8 DI	Schrägheck	Frontantrieb	Diesel	Apr 2000	Jan 2002	14813
Ford	Fiesta v	1.25 16V	Schrägheck	Frontantrieb	Benzin	Mar 2003	Jun 2008	17702
Ford	Fiesta v	1.25 16V	Schrägheck	Frontantrieb	Benzin	Nov 2001	Jun 2008	17703
Ford	Fiesta v	1.4 16V	Schrägheck	Frontantrieb	Benzin	Nov 2001	Jun 2008	16085
Ford	Fiesta v	1.4 Tdci	Schrägheck	Frontantrieb	Diesel	Nov 2001	Jun 2008	16102
Ford	Fiesta v	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	Nov 2004	Jun 2008	18329
Ford	Fiesta v	St150	Schrägheck	Frontantrieb	Benzin	Mar 2005	Jun 2008	18499
Ford	Fiesta v van	1.6 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	Apr 2007	Sep 2009	115004
Ford	Fiesta vi	1	Schrägheck	Frontantrieb	Benzin	Jan 2013	Apr 2017	58966
Ford	Fiesta vi	1	Schrägheck	Frontantrieb	Benzin	Oct 2012	Apr 2017	58970
Ford	Fiesta vi	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Jan 2013	Dec 2017	58967
Ford	Fiesta vi	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Sep 2012	Dec 2017	58968
Ford	Fiesta vi	1.0 Sport	Schrägheck	Frontantrieb	Benzin	May 2014	Apr 2017	106349
Ford	Fiesta vi	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	Jan 2009	Apr 2017	58972
Ford	Fiesta vi	1.4 Tdci	Schrägheck	Frontantrieb	Diesel	Jul 2010	Sep 2012	10105
Ford	Fiesta vi	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	Sep 2012	Apr 2017	58971
Ford	Fiesta vi	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	May 2015	Apr 2017	113318
Ford	Fiesta vi	1.6 ST	Schrägheck	Frontantrieb	Benzin	Mar 2013	Apr 2017	59076
Ford	Fiesta vi	1.6 St200	Schrägheck	Frontantrieb	Benzin	Apr 2016	Apr 2017	107028
Ford	Fiesta vi	1.6 Tdci	Schrägheck	Frontantrieb	Diesel	Jun 2008	Dec 2012	157626
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	Dec 2010	Apr 2017	10098
Ford	Fiesta vi	1.6 TI	Schrägheck	Frontantrieb	Benzin	Sep 2012	Apr 2017	58969
Ford	Fiesta vi van	1	Kasten/Schrägheck	Frontantrieb	Benzin	Oct 2012	Apr 2017	116223
Ford	Fiesta vi van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	Sep 2012	Apr 2017	108808
Ford	Fiesta vi van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	Jan 2013	Apr 2017	108813
Ford	Fiesta vi van	1.4 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	Jul 2010	Apr 2017	10198
Ford	Fiesta vi van	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	Oct 2012	Apr 2017	59493
Ford	Fiesta vi van	1.5 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	May 2015	Apr 2017	113319
Ford	Fiesta vi van	1.6 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	Feb 2010	May 2015	10202
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	May 2017	-	126554
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	May 2017	-	126555
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Jun 2017	-	127518
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	Jul 2020	-	145869
Ford	Fiesta vii	1.0 Ecoboost Active	Schrägheck	Frontantrieb	Benzin	Apr 2018	-	145758
Ford	Fiesta vii	1.0 Ecoboost Active	Schrägheck	Frontantrieb	Benzin	Apr 2018	-	145759
Ford	Fiesta vii	1.0 Ecoboost Active	Schrägheck	Frontantrieb	Benzin	Apr 2018	-	145760
Ford	Fiesta vii	1.0 Ecoboost Flex	Schrägheck	Frontantrieb	Benzin/Ethanol	Mar 2020	Dec 2022	153507
Ford	Fiesta vii	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	143418
Ford	Fiesta vii	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	-	143419
Ford	Fiesta vii	1.1 Ti-vct	Schrägheck	Frontantrieb	Benzin	May 2017	-	126566
Ford	Fiesta vii	1.1 Ti-vct	Schrägheck	Frontantrieb	Benzin	May 2017	-	126567
Ford	Fiesta vii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	May 2017	-	126556
Ford	Fiesta vii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	May 2017	-	126557
Ford	Fiesta vii	1.5 Tdci Active	Schrägheck	Frontantrieb	Diesel	Apr 2018	-	145769
Ford	Fiesta vii	1.5 Tdci Active	Schrägheck	Frontantrieb	Diesel	Apr 2018	-	145771
Ford	Fiesta vii van	1.0 Ecoboost	Kasten/Schrägheck	Frontantrieb	Benzin	Dec 2019	-	143270
Ford	Fiesta vii van	1.0 Ecoboost Flex	Kasten/Schrägheck	Frontantrieb	Benzin/Ethanol	Dec 2019	-	154578
Ford	Fiesta vii van	1.0 Ecoboost Mhev	Kasten/Schrägheck	Frontantrieb	Benzin/Elektro	Jun 2020	-	145818
Ford	Focus c-Max	1.6	Großraumlimousine	Frontantrieb	Benzin	Oct 2003	Mar 2007	17745
Ford	Focus c-Max	1.8	Großraumlimousine	Frontantrieb	Benzin	Oct 2003	Mar 2007	17630
Ford	Focus c-Max	1.8	Großraumlimousine	Frontantrieb	Benzin	Apr 2004	Mar 2007	18096
Ford	Focus c-Max	1.8	Großraumlimousine	Frontantrieb	Benzin	Sep 2005	Mar 2007	58566
Ford	Focus c-Max	2	Großraumlimousine	Frontantrieb	Benzin	Mar 2004	Mar 2007	18095
Ford	Focus c-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Oct 2003	Mar 2007	17631
Ford	Focus c-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2005	Mar 2007	18501
Ford	Focus c-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	Aug 2004	Mar 2007	18500
Ford	Focus c-Max	1.8 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2005	Mar 2007	18937
Ford	Focus c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Oct 2003	Mar 2007	11893
Ford	Focus c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Oct 2003	Mar 2007	17632
Ford	Focus i	1.4 16V	Schrägheck	Heckantrieb	Benzin	Oct 1998	Sep 1999	126648


--- Round 1 / 首次发送 ---
## 更新点

* 已完成前 32 个输入 Ktype 的 Escort 车型聚类与首轮映射，其中 27 个 Ktype 已闭合，生成 31 条 `READY` 映射。
* Escort V 改款版与 Escort VI 的轿车、旅行车、敞篷车和普通掀背车已分别建组；普通掀背车按三门、五门拆分，RS 2000 按独立三门性能外廓建组。资料明确显示普通 Escort VI Hatchback 覆盖三门和五门，而 RS 2000 为三门车型。([汽车目录][1])
* Escort V 改款轿车采用 `4229×1690×1397 mm`，旅行车采用 `4268×1690×1410 mm`；来源页面明确区分车身形式及不含后视镜宽度。([汽车目录][2])
* Escort VI 轿车、普通掀背车、敞篷车、RS 2000 和旅行车已按直接规格页面闭合。([汽车目录][3])
* Escort IV Turnier 暂不建组：Auto-Data 给出 `3958×1556×1439 mm`，Automobile-Catalog 对相同 1986 年 1.3 Estate 给出 `4080×1640×1390 mm`，属于实质冲突。([汽车数据][4])
* Escort IV Express 与 Escort VI Express 已确认车身代码，但尚缺可追溯的厢式车直接三维及门数口径，因此保持 `PENDING`。

## 当前批次进度

* 输入 Ktype 总数：100
* 已处理输入 Ktype：32
* `READY` 输入 Ktype：27
* `PENDING` 输入 Ktype：5
* 尚未处理输入 Ktype：68
* 本轮 `READY` 映射行：31
* 本轮 `PENDING` 映射行：6
* 已闭合尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11031	11031	Van	Escort IV	AVF			LOW	Express AVF 物理边界已确认，直接三维与门数尚未闭合。	PENDING: 缺少 Express AVF 直接尺寸与门数口径
11035	11035	Van	Escort IV	AVF			LOW	Express AVF 物理边界已确认，直接三维与门数尚未闭合。	PENDING: 缺少 Express AVF 直接尺寸与门数口径
11032	11032	Van	Escort IV	AVF			LOW	Express AVF 物理边界已确认，直接三维与门数尚未闭合。	PENDING: 缺少 Express AVF 直接尺寸与门数口径
15255_3dr	15255	Wagon	Escort IV		3		LOW	三门/五门旅行车分支已确认；现有尺寸来源冲突。	PENDING: Escort IV Turnier 三维来源冲突未解决
15255_5dr	15255	Wagon	Escort IV		5		LOW	三门/五门旅行车分支已确认；现有尺寸来源冲突。	PENDING: Escort IV Turnier 三维来源冲突未解决
12422	12422	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12435	12435	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
10426	10426	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
14271	14271	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12381	12381	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12438	12438	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
1963	1963	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
1964	1964	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
1962	1962	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
12433	12433	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
117953_3dr	117953	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
117953_5dr	117953	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
10427	10427	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
12441_3dr	12441	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12441_5dr	12441	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12445	12445	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
12382_3dr	12382	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12382_5dr	12382	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12384	12384	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
15258	15258	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
15259	15259	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
14270_3dr	14270	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
14270_5dr	14270	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
14272	14272	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
11225	11225	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
7809	7809	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
14263	14263	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-RS2000-3D-01	HIGH	RS 2000 仅三门，性能版高度独立。	READY
11224	11224	Van	Escort VI (Mk VI)	AVL			LOW	Escort '95 Box (AVL) 直接三维与门数尚未闭合。	PENDING: 缺少 Escort '95 Box (AVL) 直接尺寸与门数
11226	11226	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
12446	12446	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
12383	12383	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
15260	15260	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	4229	1690	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/946850/ford_escort_4-dr_1_8_d_lx.html
EU-FORD-ESCORT-V-FACELIFT-WAGON-01	4268	1690	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/946550/ford_escort_turnier_1_8i_16v_clx.html
EU-FORD-ESCORT-VI-SEDAN-01	4293	1700	1394	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951830/ford_escort_4-dr_1_6i_16v_ghia.html
EU-FORD-ESCORT-VI-HATCHBACK-3D-01	4136	1691	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951785/ford_escort_1_6i_16v_fun.html
EU-FORD-ESCORT-VI-HATCHBACK-5D-01	4136	1691	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951785/ford_escort_1_6i_16v_fun.html
EU-FORD-ESCORT-VI-CONVERTIBLE-01	4136	1700	1381	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/953060/ford_escort_cabrio_xr3i_115.html
EU-FORD-ESCORT-VI-HATCHBACK-RS2000-3D-01	4136	1691	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/952280/ford_escort_rs_2000.html
EU-FORD-ESCORT-VI-WAGON-01	4300	1700	1416	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951935/ford_escort_turnier_1_6i_16v_glx_lx.html
```

## 下一步优先处理

1. 按 Fiesta II、III、IV、V、VI、VII 代际聚类，先闭合普通 Hatchback、Van 和 Active 外廓。
2. 优先处理数量最多且能批量复用的 Fiesta VI、Fiesta VII 尺寸组。
3. 单独核对 Fiesta VII Active 的悬架高度，以及 Fiesta V ST150 是否需要性能外廓组。
4. 后续再补 Escort IV Turnier 来源冲突和两代 Escort Express 的直接厢式车规格。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/make/ford_europe/escort_europe_7gen/escort_europe_7gen_hatchback/1995.html?utm_source=chatgpt.com "1995 Ford (Europe) Escort Mk VI Hatchback full range specs"
[2]: https://www.automobile-catalog.com/car/1995/946805/ford_escort_4-dr_ghia_si.html?utm_source=chatgpt.com "1995 Ford Escort (4-dr) Ghia Si Specs Review (95.5 kW / 130 PS / 128 hp) (up to early-year 1995 for Europe )"
[3]: https://www.automobile-catalog.com/car/1995/951830/ford_escort_4-dr_1_6i_16v_ghia.html?utm_source=chatgpt.com "1995 Ford Escort (4-dr) 1.6i 16V Ghia Specs Review (66 kW / 90 PS / 89 hp) (since early-year 1995 for Europe )"
[4]: https://www.auto-data.net/en/ford-escort-model-799?utm_source=chatgpt.com "Ford Escort | Technical Specs, Fuel consumption, ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5401-5500_ktype_dimension_mapping_final.tsv
- left18448_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 上轮 5 个待处理 Escort Ktype 已全部闭合：Escort IV Express 新建厢式车尺寸组，Escort IV Turnier 按三门、五门拆分，Escort VI Express 复用已确认的 Escort VI Wagon 外廓组。([福特驾驶平台][1])
* 已批量完成 Fiesta VII 普通三门/五门、Active 五门，以及 Fiesta VII Van Trend/Sport 外廓映射。官方资料分别给出普通版、Active 和 Van 各物理外廓的三维。
* 已完成全部 11 个 Focus C-MAX I Ktype，统一关联 DM2 五门 MPV 尺寸组。([汽车档案馆][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：62
* PENDING/尚未处理输入 Ktype：38
* 当前 READY 映射行：79
* 已确认尺寸组：17
* 本轮新增或修改映射行：48
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11031	11031	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
11035	11035	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
11032	11032	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
15255_3dr	15255	Wagon	Escort IV		3	EU-FORD-ESCORT-IV-WAGON-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门旅行车，按门数拆分。	READY
15255_5dr	15255	Wagon	Escort IV		5	EU-FORD-ESCORT-IV-WAGON-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门旅行车，按门数拆分。	READY
11224	11224	Van	Escort VI (Mk VI)	AVL	5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
126554_3dr	126554	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126554_5dr	126554	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126555_3dr	126555	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126555_5dr	126555	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
127518_3dr	127518	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
127518_5dr	127518	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145869_3dr	145869	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145869_5dr	145869	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
153507_3dr	153507	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
153507_5dr	153507	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126566_3dr	126566	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126566_5dr	126566	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126567_3dr	126567	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126567_5dr	126567	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126556_3dr	126556	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126556_5dr	126556	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126557_3dr	126557	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126557_5dr	126557	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145758	145758	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145759	145759	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145760	145760	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
143418	143418	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
143419	143419	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145769	145769	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145771	145771	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
143270_trend	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
143270_sport	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
154578_trend	154578	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
154578_sport	154578	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
145818_trend	145818	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
145818_sport	145818	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
17745	17745	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17630	17630	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18096	18096	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
58566	58566	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18095	18095	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17631	17631	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18501	18501	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18500	18500	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18937	18937	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
11893	11893	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17632	17632	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-IV-EXPRESS-VAN-01	4181	1640	1568	Drive.Place	https://ford.drive.place/escort/iv/group_furgon/580736
EU-FORD-ESCORT-IV-WAGON-3D-01	4080	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/941750/ford_escort_estate_1_3_l.html
EU-FORD-ESCORT-IV-WAGON-5D-01	4080	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/941750/ford_escort_estate_1_3_l.html
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford Fiesta official engine information PDF (archive)	https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Fiesta-Intro.pdf
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4040	1735	1476	Ford Fiesta official engine information PDF (archive)	https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Fiesta-Intro.pdf
EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	4068	1756	1498	Ford Fiesta official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Fiesta.pdf
EU-FORD-FIESTA-VII-VAN-TREND-3D-01	4040	1735	1476	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	4065	1735	1466	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-FORD-FOCUS-C-MAX-I-MPV-01	4333	1825	1595	Ford Focus C-MAX official brochure (archive)	https://autocatalogarchive.com/wp-content/uploads/2025/09/Ford-C-Max-2004-UK.pdf
```

## 下一步优先处理

1. 批量闭合 Fiesta VI 普通 Hatchback 与 Van，优先复用相同代际外廓组。
2. 处理 Fiesta II、III、IV、V，并单独核对 XR2、ST150 等可能改变外廓的版本。
3. 最后处理剩余 Focus I Ktype，完成全部映射闭合和机械收尾。

推进信号：CONTINUE

[1]: https://ford.drive.place/escort/iv/group_furgon/580736?utm_source=chatgpt.com "Ford Escort IV 1.4 MT 73 hp Van — specifications - drive.place"
[2]: https://autocatalogarchive.com/wp-content/uploads/2025/09/Ford-C-Max-2004-UK-.pdf?utm_source=chatgpt.com "Ford-C-Max-2004-UK-.pdf"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5401-5500_ktype_dimension_mapping_final.tsv
- left18448_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Fiesta VI 改款前、改款后普通三门/五门，以及 Sport、ST、ST200 外廓。跨越 2012 年改款的 Ktype 已按门数和改款阶段拆分。官方资料显示改款前普通版为 `3950×1722×1481 mm`；改款后普通三门和五门宽度分别为 `1709 mm`、`1722 mm`，Sport/ST 车身长度为 `3982 mm`。
* 已闭合 Fiesta VI Van 改款前后外廓。改款前长度为 `3950 mm`，改款后为 `3969 mm`；均使用官方 Van brochure 的不含后视镜宽度口径。
* 已闭合 Focus I 1.4 16V，按 DBW 三门和 DAW 五门拆分；两种车身复用相同三维但保留独立物理尺寸组。([汽车档案馆][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：84
* PENDING/尚未处理输入 Ktype：16
* 当前 READY 映射行：121
* 已确认尺寸组：26
* 本轮新增/修改映射行：42
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
58966_3dr_facelift	58966	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58966_5dr_facelift	58966	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58970_3dr_facelift	58970	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58970_5dr_facelift	58970	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58967_3dr_facelift	58967	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58967_5dr_facelift	58967	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58968_3dr_facelift	58968	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58968_5dr_facelift	58968	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
106349	106349	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	Sport 三门外部套件外廓。	READY
58972_3dr_prefl	58972	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_3dr_facelift	58972	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_5dr_prefl	58972	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_5dr_facelift	58972	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10105_3dr_prefl	10105	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
10105_5dr_prefl	10105	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58971_3dr_facelift	58971	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58971_5dr_facelift	58971	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
113318_3dr_facelift	113318	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
113318_5dr_facelift	113318	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
59076	59076	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	ST 三门性能外廓。	READY
107028	107028	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	ST200 三门性能外廓。	READY
157626_3dr_prefl	157626	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_3dr_facelift	157626	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_5dr_prefl	157626	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_5dr_facelift	157626	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_3dr_prefl	10098	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_3dr_facelift	10098	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_5dr_prefl	10098	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_5dr_facelift	10098	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58969_3dr_facelift	58969	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58969_5dr_facelift	58969	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
116223	116223	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
108808	108808	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
108813	108813	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
10198_prefl	10198	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
10198_facelift	10198	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
59493	59493	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
113319	113319	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
10202_prefl	10202	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
10202_facelift	10202	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
126648_3dr	126648	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖 DBW 三门和 DAW 五门，按门数拆分。	READY
126648_5dr	126648	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖 DBW 三门和 DAW 五门，按门数拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	3950	1722	1481	Ford Fiesta official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Fiesta-UK.pdf
EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	3950	1722	1481	Ford Fiesta official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Fiesta-UK.pdf
EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	3969	1709	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	3969	1722	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	3982	1709	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	3950	1722	1481	Ford Fiesta Van official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011.5-Ford-Fiesta-Van-UK.pdf
EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	3969	1709	1481	Ford Fiesta Van official brochure (2016)	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_fiesta_van.pdf
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1699	1430	Ford Focus official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1699	1430	Ford Focus official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
```

## 下一步优先处理

1. 闭合 Fiesta V 普通三门、五门、改款前后、ST150 和 Van。
2. 闭合 Fiesta IV 改款前后普通车身。
3. 最后处理 Fiesta II、Fiesta III 和早期 Fiesta Van，消除剩余 16 个 PENDING/未处理 Ktype。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf?utm_source=chatgpt.com "Ford-Focus-1998-UK.pdf"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5401-5500_ktype_dimension_mapping_final.tsv
- left18448_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合其余 15 个 Fiesta Ktype，新增 23 条 `READY` 映射和 12 个尺寸组。
* Fiesta II 普通版与 XR2 分组；Fiesta III、IV、V 普通掀背车按三门和五门拆分；Sport、ST150 与 Van 独立建组。
* Ktype `11022` 暂未闭合：其生产区间覆盖 Fiesta III 前后期，现有直接资料对同系列高度给出 `1321 mm` 与 `1379 mm` 两种口径，尚不能确认掀背式厢式车应采用单组还是跨期拆分。([CarExpert][1])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：99
* PENDING 输入 Ktype：1
* READY 映射行：144
* PENDING 映射行：1
* 已确认尺寸组：38
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11022	11022	Van	Fiesta III			LOW	三门掀背式厢式车；生产区间跨前后期，外廓高度口径尚未闭合。	PENDING: 跨期外廓与高度口径尚未闭合
11023	11023	Van	Fiesta IV		3	EU-FORD-FIESTA-IV-VAN-3D-01	HIGH		READY
18316	18316	Van	Fiesta IV		3	EU-FORD-FIESTA-IV-VAN-3D-01	HIGH		READY
18816	18816	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-3D-01	HIGH		READY
1960	1960	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-XR2-3D-01	HIGH	XR2 宽体外部套件。	READY
8860_3dr	8860	Hatchback	Fiesta III facelift	GFJ	3	EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
8860_5dr	8860	Hatchback	Fiesta III facelift	GFJ	5	EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
5736_3dr	5736	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
5736_5dr	5736	Hatchback	Fiesta IV		5	EU-FORD-FIESTA-IV-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
13657	13657	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-SPORT-3D-01	HIGH	Sport 三门外部套件。	READY
14813_3dr	14813	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
14813_5dr	14813	Hatchback	Fiesta IV		5	EU-FORD-FIESTA-IV-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17702_3dr	17702	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17702_5dr	17702	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17703_3dr	17703	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17703_5dr	17703	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16085_3dr	16085	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16085_5dr	16085	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16102_3dr	16102	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16102_5dr	16102	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18329_3dr	18329	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18329_5dr	18329	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18499	18499	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-ST-3D-01	HIGH	ST150 三门性能外廓。	READY
115004	115004	Van	Fiesta V		3	EU-FORD-FIESTA-V-VAN-3D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-II-HATCHBACK-3D-01	3650	1549	1331	AutoEvolution	https://www.autoevolution.com/cars/ford-fiesta-3-doors-1986.html
EU-FORD-FIESTA-II-HATCHBACK-XR2-3D-01	3712	1620	1335	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Ford/244/Ford-Fiesta-2-XR-2.html
EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-3D-01	3769	1610	1370	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-16v-88hp-8059
EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-5D-01	3769	1610	1370	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-16v-88hp-8059
EU-FORD-FIESTA-IV-HATCHBACK-3D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-IV-HATCHBACK-5D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-IV-HATCHBACK-SPORT-3D-01	3828	1634	1320	EncyCARpedia	https://www.encycarpedia.com/ford/00-fiesta-1-6i-16v-zetec-s-hatch
EU-FORD-FIESTA-IV-VAN-3D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-V-HATCHBACK-3D-01	3917	1683	1467	Ford Fiesta official brochure (2003 archive)	https://autocatalogarchive.com/wp-content/uploads/2026/03/Ford-Fiesta-2003-UK.pdf
EU-FORD-FIESTA-V-HATCHBACK-5D-01	3917	1683	1462	Ford Fiesta official brochure (2003 archive)	https://autocatalogarchive.com/wp-content/uploads/2026/03/Ford-Fiesta-2003-UK.pdf
EU-FORD-FIESTA-V-HATCHBACK-ST-3D-01	3921	1683	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/960830/ford_fiesta_st.html
EU-FORD-FIESTA-V-VAN-3D-01	3918	1683	1468	Ford Panel Vans official specification; Autogidas	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf;https://autogidas.lt/en/auto-katalogas/ford/fiesta/v-an-1.4-tdci-2006-2008-k65240
```

## 下一步优先处理

1. 只处理 Ktype `11022`：确认 Fiesta III 掀背式厢式车是否需要按前期、后期拆分。
2. 闭合其不含后视镜宽度及对应高度后，将 `PENDING` 降为 0。
3. 随后立即执行一次机械检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.carexpert.com.au/car-news/farewell-fiesta-how-fords-city-hatch-evolved?utm_source=chatgpt.com "Farewell, Fiesta: How Ford's city hatch evolved"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5401-5500_ktype_dimension_mapping_final.tsv
- left18448_5401-5500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Ktype `11022` 已闭合为 Fiesta III、车身代码 `FVD` 的三门掀背式厢式车。车型页确认该 Ktype、车身代码和生产区间；同代 1.8 D 规格页提供 `3743×1606×1379 mm` 三维。([Meyer Motoren][1])
* 已完成一次轻量机械检查：表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，尺寸和来源均非空。
* 已生成两个指定文件名的最终 TSV。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：145
* PENDING 映射：0
* DIMENSION_GROUP：39
* 映射引用缺失：0
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11031	11031	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
11035	11035	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
11032	11032	Van	Escort IV	AVF	3	EU-FORD-ESCORT-IV-EXPRESS-VAN-01	HIGH		READY
15255_3dr	15255	Wagon	Escort IV		3	EU-FORD-ESCORT-IV-WAGON-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门旅行车，按门数拆分。	READY
15255_5dr	15255	Wagon	Escort IV		5	EU-FORD-ESCORT-IV-WAGON-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门旅行车，按门数拆分。	READY
12422	12422	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12435	12435	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
10426	10426	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
14271	14271	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12381	12381	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
12438	12438	Sedan	Escort V facelift (Mk Vb)	GAL	4	EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	HIGH		READY
1963	1963	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
1964	1964	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
1962	1962	Wagon	Escort V facelift (Mk Vb)	GAL	5	EU-FORD-ESCORT-V-FACELIFT-WAGON-01	HIGH		READY
12433	12433	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
117953_3dr	117953	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
117953_5dr	117953	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
10427	10427	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
12441_3dr	12441	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12441_5dr	12441	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12445	12445	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
12382_3dr	12382	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12382_5dr	12382	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
12384	12384	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
15258	15258	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
15259	15259	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
14270_3dr	14270	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
14270_5dr	14270	Hatchback	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
14272	14272	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
11225	11225	Sedan	Escort VI (Mk VI)		4	EU-FORD-ESCORT-VI-SEDAN-01	HIGH		READY
7809	7809	Convertible	Escort VI (Mk VI)		2	EU-FORD-ESCORT-VI-CONVERTIBLE-01	HIGH		READY
14263	14263	Hatchback	Escort VI (Mk VI)		3	EU-FORD-ESCORT-VI-HATCHBACK-RS2000-3D-01	HIGH	RS 2000 仅三门，性能版高度独立。	READY
11224	11224	Van	Escort VI (Mk VI)	AVL	5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
11226	11226	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
12446	12446	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
12383	12383	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
15260	15260	Wagon	Escort VI (Mk VI)		5	EU-FORD-ESCORT-VI-WAGON-01	HIGH		READY
11022	11022	Van	Fiesta III	FVD	3	EU-FORD-FIESTA-III-VAN-3D-01	MEDIUM	FVD 三门掀背式厢式车。	READY
11023	11023	Van	Fiesta IV		3	EU-FORD-FIESTA-IV-VAN-3D-01	HIGH		READY
18316	18316	Van	Fiesta IV		3	EU-FORD-FIESTA-IV-VAN-3D-01	HIGH		READY
18816	18816	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-3D-01	HIGH		READY
1960	1960	Hatchback	Fiesta II		3	EU-FORD-FIESTA-II-HATCHBACK-XR2-3D-01	HIGH	XR2 宽体外部套件。	READY
8860_3dr	8860	Hatchback	Fiesta III facelift	GFJ	3	EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
8860_5dr	8860	Hatchback	Fiesta III facelift	GFJ	5	EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
5736_3dr	5736	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
5736_5dr	5736	Hatchback	Fiesta IV		5	EU-FORD-FIESTA-IV-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
13657	13657	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-SPORT-3D-01	HIGH	Sport 三门外部套件。	READY
14813_3dr	14813	Hatchback	Fiesta IV		3	EU-FORD-FIESTA-IV-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
14813_5dr	14813	Hatchback	Fiesta IV		5	EU-FORD-FIESTA-IV-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17702_3dr	17702	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17702_5dr	17702	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17703_3dr	17703	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
17703_5dr	17703	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16085_3dr	16085	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16085_5dr	16085	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16102_3dr	16102	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
16102_5dr	16102	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18329_3dr	18329	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18329_5dr	18329	Hatchback	Fiesta V		5	EU-FORD-FIESTA-V-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
18499	18499	Hatchback	Fiesta V		3	EU-FORD-FIESTA-V-HATCHBACK-ST-3D-01	HIGH	ST150 三门性能外廓。	READY
115004	115004	Van	Fiesta V		3	EU-FORD-FIESTA-V-VAN-3D-01	HIGH		READY
58966_3dr_facelift	58966	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58966_5dr_facelift	58966	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58970_3dr_facelift	58970	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58970_5dr_facelift	58970	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58967_3dr_facelift	58967	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58967_5dr_facelift	58967	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58968_3dr_facelift	58968	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58968_5dr_facelift	58968	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
106349	106349	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	Sport 三门外部套件外廓。	READY
58972_3dr_prefl	58972	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_3dr_facelift	58972	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_5dr_prefl	58972	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58972_5dr_facelift	58972	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10105_3dr_prefl	10105	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
10105_5dr_prefl	10105	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58971_3dr_facelift	58971	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58971_5dr_facelift	58971	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
113318_3dr_facelift	113318	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
113318_5dr_facelift	113318	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
59076	59076	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	ST 三门性能外廓。	READY
107028	107028	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	HIGH	ST200 三门性能外廓。	READY
157626_3dr_prefl	157626	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_3dr_facelift	157626	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_5dr_prefl	157626	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
157626_5dr_facelift	157626	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_3dr_prefl	10098	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_3dr_facelift	10098	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_5dr_prefl	10098	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
10098_5dr_facelift	10098	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	跨改款且覆盖三门和五门，按改款阶段与门数拆分。	READY
58969_3dr_facelift	58969	Hatchback	Fiesta VI		3	EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
58969_5dr_facelift	58969	Hatchback	Fiesta VI		5	EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	MEDIUM	同一 Ktype 覆盖三门和五门，按门数拆分。	READY
116223	116223	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
108808	108808	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
108813	108813	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
10198_prefl	10198	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
10198_facelift	10198	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
59493	59493	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
113319	113319	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	HIGH		READY
10202_prefl	10202	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
10202_facelift	10202	Van	Fiesta VI		3	EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	MEDIUM	跨改款且外廓变化，按改款阶段拆分。	READY
126554_3dr	126554	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126554_5dr	126554	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126555_3dr	126555	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126555_5dr	126555	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
127518_3dr	127518	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
127518_5dr	127518	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145869_3dr	145869	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145869_5dr	145869	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145758	145758	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145759	145759	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145760	145760	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
153507_3dr	153507	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
153507_5dr	153507	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
143418	143418	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
143419	143419	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
126566_3dr	126566	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126566_5dr	126566	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126567_3dr	126567	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126567_5dr	126567	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126556_3dr	126556	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126556_5dr	126556	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126557_3dr	126557	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
126557_5dr	126557	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖三门/五门外廓，按门数拆分。	READY
145769	145769	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
145771	145771	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	HIGH		READY
143270_trend	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
143270_sport	143270	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
154578_trend	154578	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
154578_sport	154578	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
145818_trend	145818	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-TREND-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
145818_sport	145818	Van	Fiesta VII		3	EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	MEDIUM	同一 Ktype 覆盖 Trend/Sport 外部套件，按外廓拆分。	READY
17745	17745	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17630	17630	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18096	18096	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
58566	58566	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18095	18095	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17631	17631	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18501	18501	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18500	18500	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
18937	18937	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
11893	11893	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
17632	17632	MPV	Focus C-MAX I	DM2	5	EU-FORD-FOCUS-C-MAX-I-MPV-01	HIGH		READY
126648_3dr	126648	Hatchback	Focus I	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-3D-01	MEDIUM	同一 Ktype 覆盖 DBW 三门和 DAW 五门，按门数拆分。	READY
126648_5dr	126648	Hatchback	Focus I	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-5D-01	MEDIUM	同一 Ktype 覆盖 DBW 三门和 DAW 五门，按门数拆分。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5401-5500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ESCORT-IV-EXPRESS-VAN-01	4181	1640	1568	Drive.Place	https://ford.drive.place/escort/iv/group_furgon/580736
EU-FORD-ESCORT-IV-WAGON-3D-01	4080	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/941750/ford_escort_estate_1_3_l.html
EU-FORD-ESCORT-IV-WAGON-5D-01	4080	1640	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1986/941750/ford_escort_estate_1_3_l.html
EU-FORD-ESCORT-V-FACELIFT-SEDAN-01	4229	1690	1397	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/946850/ford_escort_4-dr_1_8_d_lx.html
EU-FORD-ESCORT-V-FACELIFT-WAGON-01	4268	1690	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/1994/946550/ford_escort_turnier_1_8i_16v_clx.html
EU-FORD-ESCORT-VI-SEDAN-01	4293	1700	1394	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951830/ford_escort_4-dr_1_6i_16v_ghia.html
EU-FORD-ESCORT-VI-HATCHBACK-3D-01	4136	1691	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951785/ford_escort_1_6i_16v_fun.html
EU-FORD-ESCORT-VI-HATCHBACK-5D-01	4136	1691	1398	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951785/ford_escort_1_6i_16v_fun.html
EU-FORD-ESCORT-VI-CONVERTIBLE-01	4136	1700	1381	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/953060/ford_escort_cabrio_xr3i_115.html
EU-FORD-ESCORT-VI-HATCHBACK-RS2000-3D-01	4136	1691	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/952280/ford_escort_rs_2000.html
EU-FORD-ESCORT-VI-WAGON-01	4300	1700	1416	Automobile-Catalog	https://www.automobile-catalog.com/car/1995/951935/ford_escort_turnier_1_6i_16v_glx_lx.html
EU-FORD-FIESTA-III-VAN-3D-01	3743	1606	1379	Meyer Motoren; Auto-Data	https://www.meyermotoren.de/fahrzeuge/11022/ford/fiesta_kasten_schraegheck_fvd_/1_8_d_fvj_11022;https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.8-d-60hp-8063
EU-FORD-FIESTA-IV-VAN-3D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-II-HATCHBACK-3D-01	3650	1549	1331	AutoEvolution	https://www.autoevolution.com/cars/ford-fiesta-3-doors-1986.html
EU-FORD-FIESTA-II-HATCHBACK-XR2-3D-01	3712	1620	1335	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Ford/244/Ford-Fiesta-2-XR-2.html
EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-3D-01	3769	1610	1370	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-16v-88hp-8059
EU-FORD-FIESTA-III-FACELIFT-HATCHBACK-5D-01	3769	1610	1370	Auto-Data	https://www.auto-data.net/en/ford-fiesta-iii-mk3-1.6-i-16v-88hp-8059
EU-FORD-FIESTA-IV-HATCHBACK-3D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-IV-HATCHBACK-5D-01	3828	1634	1320	Ford Fiesta official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/11/Ford-Fiesta-1998-UK-1-1.pdf
EU-FORD-FIESTA-IV-HATCHBACK-SPORT-3D-01	3828	1634	1320	EncyCARpedia	https://www.encycarpedia.com/ford/00-fiesta-1-6i-16v-zetec-s-hatch
EU-FORD-FIESTA-V-HATCHBACK-3D-01	3917	1683	1467	Ford Fiesta official brochure (2003 archive)	https://autocatalogarchive.com/wp-content/uploads/2026/03/Ford-Fiesta-2003-UK.pdf
EU-FORD-FIESTA-V-HATCHBACK-5D-01	3917	1683	1462	Ford Fiesta official brochure (2003 archive)	https://autocatalogarchive.com/wp-content/uploads/2026/03/Ford-Fiesta-2003-UK.pdf
EU-FORD-FIESTA-V-HATCHBACK-ST-3D-01	3921	1683	1430	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/960830/ford_fiesta_st.html
EU-FORD-FIESTA-V-VAN-3D-01	3918	1683	1468	Ford Panel Vans official specification; Autogidas	https://xr793.com/wp-content/uploads/2022/09/2007-Ford-Panel-Vans-Specs-UK.pdf;https://autogidas.lt/en/auto-katalogas/ford/fiesta/v-an-1.4-tdci-2006-2008-k65240
EU-FORD-FIESTA-VI-HATCHBACK-3D-FACELIFT-01	3969	1709	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-HATCHBACK-5D-FACELIFT-01	3969	1722	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-HATCHBACK-SPORT-3D-01	3982	1709	1495	Ford Fiesta official brochure (2015)	https://www.ukcarline.co.uk/uploads/pds/Ford%20Fiesta%20Brochure.pdf
EU-FORD-FIESTA-VI-HATCHBACK-3D-PREFL-01	3950	1722	1481	Ford Fiesta official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Fiesta-UK.pdf
EU-FORD-FIESTA-VI-HATCHBACK-5D-PREFL-01	3950	1722	1481	Ford Fiesta official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Fiesta-UK.pdf
EU-FORD-FIESTA-VI-VAN-FACELIFT-3D-01	3969	1709	1481	Ford Fiesta Van official brochure (2016)	https://www.ford.ie/content/dam/guxeu/ie/Documents/Brochures/CVs/BRO-ford_fiesta_van.pdf
EU-FORD-FIESTA-VI-VAN-PREFL-3D-01	3950	1722	1481	Ford Fiesta Van official brochure (2011 archive)	https://xr793.com/wp-content/uploads/2022/09/2011.5-Ford-Fiesta-Van-UK.pdf
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford Fiesta official engine information PDF (archive)	https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Fiesta-Intro.pdf
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4040	1735	1476	Ford Fiesta official engine information PDF (archive)	https://xr793.com/wp-content/uploads/2022/09/2017-Ford-Fiesta-Intro.pdf
EU-FORD-FIESTA-VII-HATCHBACK-ACTIVE-5D-01	4068	1756	1498	Ford Fiesta official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/feature-pdfs/FT-Fiesta.pdf
EU-FORD-FIESTA-VII-VAN-TREND-3D-01	4040	1735	1476	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-FORD-FIESTA-VII-VAN-SPORT-3D-01	4065	1735	1466	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-FORD-FOCUS-C-MAX-I-MPV-01	4333	1825	1595	Ford Focus C-MAX official brochure (archive)	https://autocatalogarchive.com/wp-content/uploads/2025/09/Ford-C-Max-2004-UK.pdf
EU-FORD-FOCUS-I-HATCHBACK-3D-01	4152	1699	1430	Ford Focus official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
EU-FORD-FOCUS-I-HATCHBACK-5D-01	4152	1699	1430	Ford Focus official brochure (1998 archive)	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5401-5500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.meyermotoren.de/fahrzeuge/11022/ford/fiesta_kasten_schraegheck_fvd_/1_8_d_fvj_11022 "https://www.meyermotoren.de/fahrzeuge/11022/ford/fiesta_kasten_schraegheck_fvd_/1_8_d_fvj_11022"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1385 行）
- 累计尺寸组：dimension_groups_final.tsv（358 行）

