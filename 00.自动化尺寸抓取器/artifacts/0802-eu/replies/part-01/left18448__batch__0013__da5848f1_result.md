# 任务：left18448 第 1201-1300 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0013__da5848f1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1201-1300 行

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
left18448 第 1201-1300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1201-1300_ktype_dimension_mapping_final.tsv
- left18448_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Audi	A7 sportback	55 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	Jul 2019	-	142514
Audi	A7 sportback	55 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	Feb 2021	-	145611
Audi	A7 sportback	RS7 Mild Hybrid Quattro	Schrägheck	Allrad	Benzin/Elektro	Jan 2023	-	151530
Audi	A7 sportback	RS7 Performance Quattro	Schrägheck	Allrad	Benzin	Nov 2015	Apr 2018	117768
Audi	A7 sportback	RS7 Quattro	Schrägheck	Allrad	Benzin	Oct 2013	Apr 2018	59683
Audi	A7 sportback	S7 Quattro	Schrägheck	Allrad	Benzin	Feb 2012	Mar 2015	11789
Audi	A7 sportback	S7 Quattro	Schrägheck	Allrad	Benzin	Jul 2014	May 2018	107352
Audi	A7 sportback	S7 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	Nov 2020	-	143062
Audi	A8 d2	3.7	Stufenheck	Frontantrieb	Benzin	Jul 1995	Dec 1998	5128
Audi	A8 d2	3.7	Stufenheck	Frontantrieb	Benzin	Nov 1998	Sep 2002	11341
Audi	A8 d2	2.5 TDI	Stufenheck	Frontantrieb	Diesel	Sep 2000	Sep 2002	15612
Audi	A8 d2	2.5 TDI Quattro	Stufenheck	Allrad	Diesel	Jul 1997	Apr 2000	8828
Audi	A8 d2	2.5 TDI Quattro	Stufenheck	Allrad	Diesel	Sep 2000	Sep 2002	15611
Audi	A8 d2	3.3 TDI Quattro	Stufenheck	Allrad	Diesel	Jun 2000	Sep 2002	12101
Audi	A8 d2	3.7 Quattro	Stufenheck	Allrad	Benzin	Jul 1995	Nov 1998	5129
Audi	A8 d2	3.7 Quattro	Stufenheck	Allrad	Benzin	Nov 1998	Sep 2002	10468
Audi	A8 d2	4.2 Quattro	Stufenheck	Allrad	Benzin	Nov 1998	Sep 2002	10467
Audi	A8 d2	4.2 Quattro	Stufenheck	Allrad	Benzin	Feb 1999	Apr 2000	14557
Audi	A8 d2	6.0 W12 Quattro	Stufenheck	Allrad	Benzin	Jan 2001	Sep 2002	15513
Audi	A8 d2	S8 Quattro	Stufenheck	Allrad	Benzin	Jun 1999	Sep 2002	12259
Audi	A8 d3	3	Stufenheck	Frontantrieb	Benzin	Jul 2003	May 2005	17546
Audi	A8 d3	3	Stufenheck	Frontantrieb	Benzin	Jul 2003	May 2006	18763
Audi	A8 d3	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	Aug 2003	Jul 2010	17920
Audi	A8 d3	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	Nov 2003	Jul 2010	18764
Audi	A8 d3	3.2 FSI	Stufenheck	Frontantrieb	Benzin	Jun 2005	Jul 2010	18672
Audi	A8 d3	3.2 FSI Quattro	Stufenheck	Allrad	Benzin	Jun 2005	Jul 2010	18673
Audi	A8 d3	3.7 Quattro	Stufenheck	Allrad	Benzin	Oct 2002	May 2006	16994
Audi	A8 d3	4.0 TDI Quattro	Stufenheck	Allrad	Diesel	May 2003	Jul 2005	17273
Audi	A8 d3	4.2 Quattro	Stufenheck	Allrad	Benzin	Oct 2002	Jul 2010	16888
Audi	A8 d3	4.2 TDI Quattro	Stufenheck	Allrad	Diesel	Jan 2005	Jun 2005	18674
Audi	A8 d3	6.0 W12 Quattro	Stufenheck	Allrad	Benzin	Dec 2003	Jul 2010	17799
Audi	A8 d4	2.0 Tfsi Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Feb 2012	Nov 2015	12156
Audi	A8 d4	2.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Sep 2016	Jan 2018	121994
Audi	A8 d4	2.5 Tfsi	Stufenheck	Frontantrieb	Benzin	Jul 2012	Jun 2016	59075
Audi	A8 d4	3.0 TDI	Stufenheck	Frontantrieb	Diesel	Sep 2011	Sep 2013	10441
Audi	A8 d4	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	Aug 2010	Nov 2015	11148
Audi	A8 d4	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	Oct 2013	Jan 2018	53317
Audi	A8 d4	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	Nov 2012	Jun 2016	59053
Audi	A8 d4	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	May 2015	Jan 2018	115132
Audi	A8 d4	3.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Nov 2011	Jan 2018	12029
Audi	A8 d4	4.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Mar 2012	Dec 2014	12027
Audi	A8 d4	4.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	Oct 2013	Dec 2015	53316
Audi	A8 d4	4.2 TDI Quattro	Stufenheck	Allrad	Diesel	Oct 2013	Jan 2018	53315
Audi	A8 d4	S8 Plus Quattro	Stufenheck	Allrad	Benzin	Nov 2015	Jan 2018	117774
Audi	A8 d4	S8 Quattro	Stufenheck	Allrad	Benzin	Apr 2012	Jan 2018	11831
Audi	A8 d5	60 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	Nov 2021	-	146730
Audi	Allroad c5	2.5 TDI Quattro	Kombi	Allrad	Diesel	May 2000	Aug 2005	14772
Audi	Allroad c5	2.5 TDI Quattro	Kombi	Allrad	Diesel	May 2003	Aug 2005	17306
Audi	Allroad c5	2.7 T Quattro	Kombi	Allrad	Benzin	May 2000	Aug 2005	14775
Audi	Allroad c5	4.2 V8 Quattro	Kombi	Allrad	Benzin	Jul 2002	Aug 2005	16733
Audi	b2	1.6	Coupe	Frontantrieb	Benzin	Jul 1980	Aug 1981	12970
Audi	b2	2	Coupe	Frontantrieb	Benzin	Mar 1986	Apr 1988	10913
Audi	b2	1.8 GT	Coupe	Frontantrieb	Benzin	Aug 1986	Oct 1988	5066
Audi	b2	1.8 GT Quattro	Coupe	Allrad	Benzin	Dec 1984	Oct 1988	17918
Audi	b3	2	Coupe	Frontantrieb	Benzin	Mar 1990	Jul 1990	18446
Audi	b3	2	Coupe	Frontantrieb	Benzin	May 1989	Mar 1990	18447
Audi	b3	1.9 TDI	Cabriolet	Frontantrieb	Diesel	Jun 1995	Aug 2000	5124
Audi	b3	2.0 16 V	Coupe	Frontantrieb	Benzin	Jan 1992	Jul 1992	11910
Audi	b3	2.0 16V	Cabriolet	Frontantrieb	Benzin	Jun 1995	Jul 1996	5123
Audi	b3	2.0 20 V	Coupe	Frontantrieb	Benzin	Aug 1989	Jul 1991	18108
Audi	b3	2.0 20 V Quattro	Coupe	Allrad	Benzin	Aug 1989	Jul 1991	14139
Audi	b3	2.3 20V	Coupe	Frontantrieb	Benzin	Aug 1989	Jul 1991	5067
Audi	E-Tron	GT Quattro	Stufenheck	Allrad	Elektro	Nov 2020	-	145388
Audi	E-Tron	GT Quattro	Stufenheck	Allrad	Elektro	Jun 2025	-	802020
Audi	E-Tron	RS Performance Quattro	Stufenheck	Allrad	Elektro	Jun 2024	-	800129
Audi	E-Tron	RS Quattro	Stufenheck	Allrad	Elektro	Feb 2021	Jul 2024	143492
Audi	E-Tron	RS Quattro	Stufenheck	Allrad	Elektro	Jun 2024	-	800128
Audi	E-Tron	S Quattro	SUV	Allrad	Elektro	Sep 2020	Jul 2023	143011
Audi	E-Tron	S Quattro	Stufenheck	Allrad	Elektro	Jun 2024	-	800127
Audi	Q2	1.0 Tfsi	SUV	Frontantrieb	Benzin	Oct 2016	Oct 2020	119962
Audi	Q2	1.4 Tfsi	SUV	Frontantrieb	Benzin	Jun 2016	-	119960
Audi	Q2	1.6 TDI	SUV	Frontantrieb	Diesel	Jun 2016	Jul 2018	119964
Audi	Q2	2.0 TDI	SUV	Frontantrieb	Diesel	Sep 2016	-	119965
Audi	Q2	2.0 TDI Quattro	SUV	Allrad	Diesel	Sep 2016	-	119966
Audi	Q2	2.0 TDI Quattro	SUV	Allrad	Diesel	Jul 2016	Aug 2018	119967
Audi	Q2	30 TDI	SUV	Frontantrieb	Diesel	Feb 2021	-	144266
Audi	Q2	30 Tfsi	SUV	Frontantrieb	Benzin	Aug 2020	-	142872
Audi	Q2	40 Tfsi Quattro	SUV	Allrad	Benzin	Apr 2021	-	801667
Audi	Q3	1.4 Tfsi	SUV	Frontantrieb	Benzin	Jul 2016	Oct 2018	120595
Audi	Q3	1.4 TSI	SUV	Frontantrieb	Benzin	Oct 2013	Oct 2018	100035
Audi	Q3	1.5 Tfsi	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	162000
Audi	Q3	1.5 Tfsi	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	163195
Audi	Q3	1.5 Tfsi Phev	SUV	Frontantrieb	Benzin/Elektro	Jul 2025	-	162036
Audi	Q3	1.5 Tfsi Phev	SUV	Frontantrieb	Benzin/Elektro	Sep 2025	-	163178
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Sep 2011	Oct 2018	11793
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Sep 2011	Oct 2018	12035
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Jun 2011	Apr 2015	59273
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Nov 2014	Oct 2018	109420
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Mar 2015	Oct 2018	112266
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	May 2015	Oct 2018	113346
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Jul 2025	-	162002
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Nov 2025	-	163196
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Feb 2026	-	163860
Audi	Q3	2.0 TDI	SUV	Frontantrieb	Diesel	Feb 2026	-	163861
Audi	Q3	2.0 TDI Quattro	SUV	Allrad	Diesel	Jun 2011	Oct 2018	11791
Audi	Q3	2.0 TDI Quattro	SUV	Allrad	Diesel	Jun 2011	Apr 2015	12036
Audi	Q3	2.0 TDI Quattro	SUV	Allrad	Diesel	Jan 2012	Oct 2018	14761
Audi	Q3	2.0 TDI Quattro	SUV	Allrad	Diesel	Nov 2014	Oct 2018	109421
Audi	Q3	2.0 TDI Quattro	SUV	Allrad	Diesel	Nov 2014	Oct 2018	109422
Audi	Q3	2.0 Tfsi	SUV	Frontantrieb	Benzin	May 2015	Oct 2018	113345


--- Round 1 / 首次发送 ---
更新点

* 已完成 **Audi A7 C8 普通版、S7 TDI、RS7** 以及 **Audi Q2 改款前/后** 的映射闭合。
* A7 C8 普通版直接复用既有缓存尺寸组；S7、RS7 和两个 Q2 外廓首次建组。Audi 官方资料分别确认 A7 为 4969×1908×1422 mm、S7 为 4980×1908×1417 mm、RS7 为 5009×1950×1424 mm，宽度均为不含后视镜口径。([audi.com][1])
* Q2 改款前为 4191×1794×1508 mm；2020 年改款后长度增至 4208 mm，宽度和高度保持 1794×1508 mm。([汽车数据网][2])

当前批次进度

* 输入 Ktype：100
* READY 映射：13
* PENDING 映射：87
* 当前已关联尺寸组：5
* 本轮首次创建尺寸组：4
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142514	142514	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH	A7第二代标准Sportback外廓。	READY
145611	145611	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH	A7第二代标准Sportback外廓。	READY
151530	151530	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-II-4K8-RS7-HATCHBACK-01	HIGH	RS7宽体及专用外部造型。	READY
143062	143062	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-S7-HATCHBACK-01	HIGH	S7运动悬架及专用外部造型。	READY
119962	119962	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
119960	119960	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	1.4 TFSI属于改款前版本。	READY
119964	119964	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
119965	119965	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	旧式2.0 TDI命名对应改款前版本。	READY
119966	119966	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	旧式2.0 TDI命名对应改款前版本。	READY
119967	119967	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
144266	144266	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
142872	142872	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
801667	801667	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A7-II-4K8-RS7-HATCHBACK-01	5009	1950	1424	Audi MediaCenter RS 7 Sportback technical data	https://www.audi-mediacenter.com/system/production/car_motorizations/1185/file_en/8e06a44da501d26d1aa26806c124c1e4b90d507f/eTD-Audi-RS7-Sportback-TFSI_231027.pdf
EU-AUDI-A7-II-4KA-S7-HATCHBACK-01	4980	1908	1417	Audi MediaCenter S7 Sportback TDI dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-s7-sportback-tdi-1408/download
EU-AUDI-Q2-I-GA-SUV-PREFL-01	4191	1794	1508	Auto-Data Audi Q2 2016-2020 specifications	https://www.auto-data.net/en/audi-q2-generation-4712
EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	4208	1794	1508	Audi MediaCenter Q2 facelift dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-q2-1411/download
```

下一步优先处理

1. 按代际批量闭合 A8 D2、D3、D4、D5，并核对标准轴距与可能的长轴车身边界。
2. 随后处理 A7 C7 的 S7、RS7 改款前后外廓，避免与普通 A7 尺寸组混用。
3. 再处理 Allroad C5、B2/B3 Coupe/Cabriolet、e-tron GT、e-tron S 以及 Q3 8U/FJ。

推进信号：CONTINUE

[1]: https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-a7-sportback-1406/download "A7 Sportback MA Abmessungen 0523"
[2]: https://www.auto-data.net/en/audi-q2-generation-4712?utm_source=chatgpt.com "Audi Q2 | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1201-1300_ktype_dimension_mapping_final.tsv
- left18448_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 闭合 A7 C7 的 S7、RS7/RS7 Performance，新增 2 个尺寸组；同一性能系列内复用对应外廓。
* 闭合 Allroad C5 全部 4 个 Ktype，统一关联官方规格确认的 4810×1852×1551 mm 外廓。
* 闭合 Audi Coupe B2 改款前、改款后，以及 Coupe B3 的 Typ 89、Typ 8B 两个外廓阶段。
* 闭合 Audi Cabriolet 8G 两个 Ktype。Audi 官方资料明确给出 S7、RS7 和 Allroad 的不含后视镜宽度；历史 Coupe/Cabriolet 分支使用直接车型规格页确认。([奥迪新闻中心][1])

当前批次进度

* 输入 Ktype：100
* READY 映射：33
* PENDING 映射：67
* 已确认尺寸组：13
* 本轮新增 READY 映射：20
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117768	117768	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	HIGH	RS7 Performance与RS7共享物理外廓。	READY
59683	59683	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	HIGH	RS7专用外廓。	READY
11789	11789	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	HIGH	S7 Sportback外廓。	READY
107352	107352	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	HIGH	S7改款前后尺寸边界未变化。	READY
14772	14772	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
17306	17306	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
14775	14775	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
16733	16733	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
12970	12970	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	B2改款前短车身。	READY
10913	10913	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	B2改款后加长外廓。	READY
5066	5066	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	B2改款后加长外廓。	READY
17918	17918	Coupe	Coupe B2	85	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	Quattro底盘代码不同但共用改款后外廓。	READY
18446	18446	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
18447	18447	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
5124	5124	Convertible	Cabriolet 8G	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	HIGH		READY
11910	11910	Coupe	Coupe B3	8B	3	EU-AUDI-COUPE-B3-8B-COUPE-FACELIFT-01	HIGH	Typ 8B后期外廓。	READY
5123	5123	Convertible	Cabriolet 8G	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	HIGH		READY
18108	18108	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
14139	14139	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Quattro驱动未改变该车身外廓。	READY
5067	5067	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	5012	1911	1419	Audi Press UK RS 7 Sportback technical data	https://press.audi.co.uk/assets/documents/original/19283-AudiUK00000008RS7SportbackTechnicalData.pdf
EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	4980	1911	1408	Audi Press UK S7 Sportback technical data	https://press.audi.co.uk/assets/documents/original/19221-AudiUK00000035S7SportbackTechnicalData.pdf
EU-AUDI-ALLROAD-C5-4BH-WAGON-01	4810	1852	1551	Audi Press UK allroad quattro 2.5 TDI technical data	https://press.audi.co.uk/assets/documents/original/18362-AudiUK00001044Audiallroadquattro25TDI.pdf
EU-AUDI-COUPE-B2-COUPE-PREFL-01	4349	1682	1350	Auto-Data Audi Coupe B2 specifications	https://www.auto-data.net/en/audi-coupe-model-502
EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	4421	1682	1350	Auto-Data Audi Coupe B2 facelift specifications	https://www.auto-data.net/en/audi-coupe-model-502
EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	4366	1716	1370	Automobile-Catalog 1990 Audi Coupe 2.0 E specifications	https://www.automobile-catalog.com/car/1990/236270/audi_coupe_2_0_e_cat.html
EU-AUDI-COUPE-B3-8B-COUPE-FACELIFT-01	4366	1716	1375	Automobile-Catalog 1992 Audi Coupe 16V specifications	https://www.automobile-catalog.com/car/1992/237290/audi_coupe_16v.html
EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	4366	1716	1379	Automobile-Catalog 1995 Audi Cabriolet 1.9 TDI specifications	https://www.automobile-catalog.com/car/1995/237575/audi_cabriolet_1_9_tdi.html
```

下一步优先处理

1. 按 D2、D3、D4、D5 聚类处理全部 A8 Ktype，优先区分标准轴距、长轴及 S8 高度差异。
2. 处理第一代 Q3 8U，并集中关联改款前、改款后尺寸组。
3. 处理第一代及改款后 e-tron GT、RS e-tron GT、S e-tron GT，以及 e-tron S SUV。

推进信号：CONTINUE

[1]: https://press.audi.co.uk/assets/documents/original/19221-AudiUK00000035S7SportbackTechnicalData.pdf?utm_source=chatgpt.com "Technical Data – Audi S7 Sportback ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1201-1300_ktype_dimension_mapping_final.tsv
- left18448_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
更新点

* 完成 A8 D2 全部 12 个 Ktype：短轴 A8、W12 与 S8 均关联 5034×1880×1438 mm 尺寸组，宽度为不含后视镜口径。([汽车目录][1])
* 完成 A8 D3 全部 11 个 Ktype。前期车身为 5051×1894×1444 mm，单框格栅外廓为 5062×1894×1444 mm；跨越两种外廓的 Ktype `17920`、`18764`、`16888` 已拆分。([汽车目录][2])
* 已检查历史尺寸组索引；后续 Q3 II F3 可直接复用既有尺寸组，仅需补充 Ktype 关联。

当前批次进度

* 输入 Ktype：100
* READY Ktype：56
* READY 映射行：59
* PENDING Ktype：44
* 已确认尺寸组：16
* 本轮新增 READY 映射行：26
* 本轮首次创建尺寸组：3
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
5128	5128	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
11341	11341	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15612	15612	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
8828	8828	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15611	15611	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
12101	12101	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
5129	5129	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
10468	10468	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
10467	10467	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
14557	14557	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15513	15513	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
12259	12259	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
17546	17546	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
18763	18763	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
17920_prefl	17920	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
17920_facelift	17920	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18764_prefl	18764	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
18764_facelift	18764	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18672	18672	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
18673	18673	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
16994	16994	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
17273	17273	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
16888_prefl	16888	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
16888_facelift	16888	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18674	18674	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
17799	17799	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	W12自上市采用5062 mm单框格栅外廓。	READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A8-D2-4D-SEDAN-01	5034	1880	1438	Automobile-Catalog 2001 Audi A8 3.7 Quattro; Automobile-Catalog 2001 Audi A8 6.0 Quattro; Automobile-Catalog 2001 Audi S8	https://www.automobile-catalog.com/car/2001/240575/audi_a8_3_7_quattro_tiptronic.html;https://www.automobile-catalog.com/car/2001/240620/audi_a8_6_0_quattro_tiptronic.html;https://www.automobile-catalog.com/car/2001/240770/audi_s8_tiptronic.html
EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	5051	1894	1444	Automobile-Catalog 2004 Audi A8 4.2 Quattro	https://www.automobile-catalog.com/car/2004/252665/audi_a8_4_2_quattro.html
EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	5062	1894	1444	Automobile-Catalog Audi A8 D3 phase II; Automobile-Catalog 2004 Audi A8 6.0 Quattro	https://www.automobile-catalog.com/make/audi/a8_d3/a8_d3_series_ii/2005.html;https://www.automobile-catalog.com/car/2004/252740/audi_a8_6_0_quattro.html
```

下一步优先处理

1. 闭合 A8 D4 的改款前、改款后及 S8 外廓，并拆分跨越改款边界的 Ktype。
2. 处理 A8 D5 插电混合动力车型。
3. 批量关联 Q3 8U 改款前后车型，再复用 Q3 II F3 缓存并新建第三代 Q3 尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2001/240575/audi_a8_3_7_quattro_tiptronic.html?utm_source=chatgpt.com "2001 Audi A8 3.7 Quattro Tiptronic Specs Review (191 kW / 260 PS / 256 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/2004/252665/audi_a8_4_2_quattro.html?utm_source=chatgpt.com "2004 Audi A8 4.2 Quattro Specs Review (246 kW / 335 PS / 330 hp) (for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1201-1300_ktype_dimension_mapping_final.tsv
- left18448_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
更新点

* 已闭合 A8 D4 标准车身与 S8 的改款前/后分支、A8 D5 改款后短轴车身，以及 Q3 8U 改款前/后分支，共消除 28 个 PENDING Ktype。
* 本轮首次创建 7 个尺寸组；A8 D4 改款后官方图示确认 5135×1949×1460 mm、S8 为 5147×1949×1458 mm，Q3 8U 两阶段长度分别为 4385 mm 与 4388 mm。
* A8 D5 60 TFSI e 的 2021 年 11 月起记录关联改款后 5190×1945×1473 mm 短轴外廓。([audi.com][1])

当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* READY 映射行：100
* PENDING Ktype：16
* 已确认尺寸组：23
* 本轮新增 READY Ktype：28
* 本轮新增 READY 映射行：41
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
12156_prefl	12156	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12156_facelift	12156	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
121994	121994	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
10441	10441	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH		READY
11148_prefl	11148	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
11148_facelift	11148	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
53317	53317	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
59053_prefl	59053	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
59053_facelift	59053	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
115132	115132	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
12029_prefl	12029	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12029_facelift	12029	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
12027_prefl	12027	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12027_facelift	12027	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
53316	53316	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
53315	53315	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
117774	117774	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	HIGH	S8 Plus与改款后S8共享外廓。	READY
11831_prefl	11831	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-PREFL-01	HIGH	S8改款前外廓分支。	READY
11831_facelift	11831	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	HIGH	S8改款后外廓分支。	READY
146730	146730	Sedan	A8 D5	4N	4	EU-AUDI-A8-D5-4N-SEDAN-FACELIFT-01	HIGH		READY
120595	120595	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
100035_prefl	100035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
100035_facelift	100035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
11793_prefl	11793	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
11793_facelift	11793	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
12035_prefl	12035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
12035_facelift	12035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
59273_prefl	59273	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
59273_facelift	59273	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
109420	109420	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
112266	112266	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
113346	113346	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
11791_prefl	11791	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
11791_facelift	11791	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
12036_prefl	12036	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
12036_facelift	12036	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
14761_prefl	14761	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
14761_facelift	14761	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
109421	109421	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
109422	109422	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
113345	113345	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	5137	1949	1460	Auto-Data Audi A8 D4 3.0 TFSI quattro specifications	https://www.auto-data.net/en/audi-a8-d4-4h-3.0-tfsi-v6-333hp-quattro-tiptronic-53561
EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	5135	1949	1460	Audi UK A8 and S8 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf
EU-AUDI-A8-D4-4H-S8-SEDAN-PREFL-01	5146	1949	1458	Auto-Data Audi S8 D4 4.0 TFSI specifications	https://www.auto-data.net/en/audi-s8-d4-4.0-tfsi-v8-520hp-quattro-tiptronic-19144
EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	5147	1949	1458	Audi UK A8 and S8 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf
EU-AUDI-A8-D5-4N-SEDAN-FACELIFT-01	5190	1945	1473	Audi MediaCenter enhanced A8 press release; Auto-Data Audi A8 D5 facelift 60 TFSI e specifications	https://www.audi-mediacenter.com/en/press-releases/sharpened-design-and-innovative-technologies-for-the-flagship-the-enhanced-audi-a8-14358;https://www.auto-data.net/en/audi-a8-d5-facelift-2021-60-tfsi-e-v6-462hp-plug-in-hybrid-quattro-tiptronic-52201
EU-AUDI-Q3-I-8U-SUV-PREFL-01	4385	1831	1608	Automobile-Catalog 2012 Audi Q3 2.0 TFSI quattro specifications	https://www.automobile-catalog.com/car/2012/1586090/audi_q3_2_0_tfsi_quattro_170_s-tronic.html
EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	4388	1831	1608	Audi UK Q3 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/20423-AudiUK00017558AudiQ3PricingandSpecification.pdf
```

下一步优先处理

1. 确认 Ktype `59075` 的 2.5 TFSI 是否限定 A8 L 长轴车身，并闭合其改款前后分支。
2. 集中处理 e-tron GT、RS e-tron GT、S e-tron GT 与 e-tron S SUV 的代际和性能外廓。
3. 最后闭合 2025—2026 年第三代 Q3 的汽油、柴油和 PHEV Ktype。

推进信号：CONTINUE

[1]: https://www.audi-mediacenter.com/en/press-releases/sharpened-design-and-innovative-technologies-for-the-flagship-the-enhanced-audi-a8-14358?utm_source=chatgpt.com "Sharpened design and innovative technologies for the ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1201-1300_ktype_dimension_mapping_final.tsv
- left18448_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 16 个 Ktype：`59075` 按 A8 L 改款前后长轴外廓拆分；e-tron GT、RS、S 及 e-tron S SUV 按实际车身边界分组；第三代 Q3 的汽油、柴油和 PHEV Ktype 统一关联 FJ SUV 尺寸组。([汽车数据网][1])
* 已完成轻量机械检查：表头正确、100 个输入 Ktype 全部覆盖、117 个映射 `id` 唯一、32 个尺寸组唯一、映射引用完全闭合、无孤立尺寸组、三维与来源字段均非空。
* 当前批次已达到 `PENDING=0`。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：117
* PENDING：0
* DIMENSION_GROUP：32
* 映射引用闭合：32/32
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142514	142514	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH	A7第二代标准Sportback外廓。	READY
145611	145611	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-HATCHBACK-01	HIGH	A7第二代标准Sportback外廓。	READY
151530	151530	Hatchback	A7 C8	4K8	5	EU-AUDI-A7-II-4K8-RS7-HATCHBACK-01	HIGH	RS7宽体及专用外部造型。	READY
117768	117768	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	HIGH	RS7 Performance与RS7共享物理外廓。	READY
59683	59683	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	HIGH	RS7专用外廓。	READY
11789	11789	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	HIGH	S7 Sportback外廓。	READY
107352	107352	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	HIGH	S7改款前后尺寸边界未变化。	READY
143062	143062	Hatchback	A7 C8	4KA	5	EU-AUDI-A7-II-4KA-S7-HATCHBACK-01	HIGH	S7运动悬架及专用外部造型。	READY
5128	5128	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
11341	11341	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15612	15612	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
8828	8828	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15611	15611	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
12101	12101	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
5129	5129	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
10468	10468	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
10467	10467	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
14557	14557	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
15513	15513	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
12259	12259	Sedan	A8 D2	4D	4	EU-AUDI-A8-D2-4D-SEDAN-01	HIGH		READY
17546	17546	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
18763	18763	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
17920_prefl	17920	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
17920_facelift	17920	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18764_prefl	18764	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
18764_facelift	18764	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18672	18672	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
18673	18673	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
16994	16994	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
17273	17273	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH		READY
16888_prefl	16888	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	HIGH	D3改款前外廓分支。	READY
16888_facelift	16888	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	D3单框格栅外廓分支。	READY
18674	18674	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH		READY
17799	17799	Sedan	A8 D3	4E	4	EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	HIGH	W12自上市采用5062 mm单框格栅外廓。	READY
12156_prefl	12156	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12156_facelift	12156	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
121994	121994	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
59075_prefl	59075	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-LWB-PREFL-01	HIGH	A8 L改款前长轴外廓分支。	READY
59075_facelift	59075	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-LWB-FACELIFT-01	HIGH	A8 L改款后长轴外廓分支。	READY
10441	10441	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH		READY
11148_prefl	11148	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
11148_facelift	11148	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
53317	53317	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
59053_prefl	59053	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
59053_facelift	59053	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
115132	115132	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
12029_prefl	12029	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12029_facelift	12029	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
12027_prefl	12027	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	HIGH	D4改款前外廓分支。	READY
12027_facelift	12027	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH	D4改款后外廓分支。	READY
53316	53316	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
53315	53315	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	HIGH		READY
117774	117774	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	HIGH	S8 Plus与改款后S8共享外廓。	READY
11831_prefl	11831	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-PREFL-01	HIGH	S8改款前外廓分支。	READY
11831_facelift	11831	Sedan	A8 D4	4H	4	EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	HIGH	S8改款后外廓分支。	READY
146730	146730	Sedan	A8 D5	4N	4	EU-AUDI-A8-D5-4N-SEDAN-FACELIFT-01	HIGH		READY
14772	14772	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
17306	17306	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
14775	14775	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
16733	16733	Wagon	Allroad C5	4BH	5	EU-AUDI-ALLROAD-C5-4BH-WAGON-01	HIGH		READY
12970	12970	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	B2改款前短车身。	READY
10913	10913	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	B2改款后加长外廓。	READY
5066	5066	Coupe	Coupe B2	81	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	B2改款后加长外廓。	READY
17918	17918	Coupe	Coupe B2	85	2	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	Quattro底盘代码不同但共用改款后外廓。	READY
18446	18446	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
18447	18447	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
5124	5124	Convertible	Cabriolet 8G	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	HIGH		READY
11910	11910	Coupe	Coupe B3	8B	3	EU-AUDI-COUPE-B3-8B-COUPE-FACELIFT-01	HIGH	Typ 8B后期外廓。	READY
5123	5123	Convertible	Cabriolet 8G	8G	2	EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	HIGH		READY
18108	18108	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
14139	14139	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Quattro驱动未改变该车身外廓。	READY
5067	5067	Coupe	Coupe B3	89	3	EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	HIGH	Typ 89前期外廓。	READY
145388	145388	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-SEDAN-PREFL-01	HIGH		READY
802020	802020	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-SEDAN-FACELIFT-01	HIGH		READY
800129	800129	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-RS-SEDAN-FACELIFT-01	HIGH	RS e-tron GT performance外廓。	READY
143492	143492	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-RS-SEDAN-PREFL-01	HIGH		READY
800128	800128	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-RS-SEDAN-FACELIFT-01	HIGH		READY
143011	143011	SUV	e-tron I	GE	5	EU-AUDI-E-TRON-I-GE-S-SUV-01	HIGH		READY
800127	800127	Sedan	e-tron GT I	F8	4	EU-AUDI-E-TRON-GT-I-F8-S-SEDAN-FACELIFT-01	HIGH		READY
119962	119962	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
119960	119960	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	1.4 TFSI属于改款前版本。	READY
119964	119964	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
119965	119965	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	旧式2.0 TDI命名对应改款前版本。	READY
119966	119966	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	旧式2.0 TDI命名对应改款前版本。	READY
119967	119967	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-PREFL-01	HIGH	Q2第一代改款前外廓。	READY
144266	144266	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
142872	142872	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
801667	801667	SUV	Q2 I	GA	5	EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	HIGH	Q2第一代2020年改款后外廓。	READY
120595	120595	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
100035_prefl	100035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
100035_facelift	100035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
162000	162000	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
163195	163195	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
162036	162036	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
163178	163178	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
11793_prefl	11793	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
11793_facelift	11793	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
12035_prefl	12035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
12035_facelift	12035	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
59273_prefl	59273	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
59273_facelift	59273	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
109420	109420	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
112266	112266	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
113346	113346	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
162002	162002	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
163196	163196	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
163860	163860	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
163861	163861	SUV	Q3 III	FJ	5	EU-AUDI-Q3-III-FJ-SUV-01	HIGH		READY
11791_prefl	11791	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
11791_facelift	11791	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
12036_prefl	12036	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
12036_facelift	12036	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
14761_prefl	14761	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-PREFL-01	HIGH	8U改款前外廓分支。	READY
14761_facelift	14761	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH	8U改款后外廓分支。	READY
109421	109421	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
109422	109422	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
113345	113345	SUV	Q3 I	8U	5	EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1201-1300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A7-II-4KA-HATCHBACK-01	4969	1908	1422	Audi MediaCenter A7 Sportback dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-a7-sportback-1406/download
EU-AUDI-A7-II-4K8-RS7-HATCHBACK-01	5009	1950	1424	Audi MediaCenter RS 7 Sportback technical data	https://www.audi-mediacenter.com/system/production/car_motorizations/1185/file_en/8e06a44da501d26d1aa26806c124c1e4b90d507f/eTD-Audi-RS7-Sportback-TFSI_231027.pdf
EU-AUDI-A7-C7-4G8-RS7-HATCHBACK-01	5012	1911	1419	Audi Press UK RS 7 Sportback technical data	https://press.audi.co.uk/assets/documents/original/19283-AudiUK00000008RS7SportbackTechnicalData.pdf
EU-AUDI-A7-C7-4G8-S7-HATCHBACK-01	4980	1911	1408	Audi Press UK S7 Sportback technical data	https://press.audi.co.uk/assets/documents/original/19221-AudiUK00000035S7SportbackTechnicalData.pdf
EU-AUDI-A7-II-4KA-S7-HATCHBACK-01	4980	1908	1417	Audi MediaCenter S7 Sportback TDI dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-s7-sportback-tdi-1408/download
EU-AUDI-A8-D2-4D-SEDAN-01	5034	1880	1438	Automobile-Catalog 2001 Audi A8 3.7 Quattro; Automobile-Catalog 2001 Audi A8 6.0 Quattro; Automobile-Catalog 2001 Audi S8	https://www.automobile-catalog.com/car/2001/240575/audi_a8_3_7_quattro_tiptronic.html;https://www.automobile-catalog.com/car/2001/240620/audi_a8_6_0_quattro_tiptronic.html;https://www.automobile-catalog.com/car/2001/240770/audi_s8_tiptronic.html
EU-AUDI-A8-D3-4E-SEDAN-PREFL-01	5051	1894	1444	Automobile-Catalog 2004 Audi A8 4.2 Quattro	https://www.automobile-catalog.com/car/2004/252665/audi_a8_4_2_quattro.html
EU-AUDI-A8-D3-4E-SEDAN-FACELIFT-01	5062	1894	1444	Automobile-Catalog Audi A8 D3 phase II; Automobile-Catalog 2004 Audi A8 6.0 Quattro	https://www.automobile-catalog.com/make/audi/a8_d3/a8_d3_series_ii/2005.html;https://www.automobile-catalog.com/car/2004/252740/audi_a8_6_0_quattro.html
EU-AUDI-A8-D4-4H-SEDAN-PREFL-01	5137	1949	1460	Auto-Data Audi A8 D4 3.0 TFSI quattro specifications	https://www.auto-data.net/en/audi-a8-d4-4h-3.0-tfsi-v6-333hp-quattro-tiptronic-53561
EU-AUDI-A8-D4-4H-SEDAN-FACELIFT-01	5135	1949	1460	Audi UK A8 and S8 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf
EU-AUDI-A8-D4-4H-SEDAN-LWB-PREFL-01	5267	1949	1471	Auto-Data Audi A8L D4 2.5 FSI specifications	https://www.auto-data.net/en/audi-a8l-d4-4h-2.5-fsi-v6-204hp-tiptronic-27135
EU-AUDI-A8-D4-4H-SEDAN-LWB-FACELIFT-01	5265	1949	1471	Auto-Data Audi A8L D4 facelift 3.0 TFSI specifications	https://www.auto-data.net/en/audi-a8l-d4-4h-facelift-2013-3.0-tfsi-v6-310hp-quattro-tiptronic-19141
EU-AUDI-A8-D4-4H-S8-SEDAN-FACELIFT-01	5147	1949	1458	Audi UK A8 and S8 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/19790-AudiUK00016077AudiA8andS8Pricingand.pdf
EU-AUDI-A8-D4-4H-S8-SEDAN-PREFL-01	5146	1949	1458	Auto-Data Audi S8 D4 4.0 TFSI specifications	https://www.auto-data.net/en/audi-s8-d4-4.0-tfsi-v8-520hp-quattro-tiptronic-19144
EU-AUDI-A8-D5-4N-SEDAN-FACELIFT-01	5190	1945	1473	Audi MediaCenter enhanced A8 press release; Auto-Data Audi A8 D5 facelift 60 TFSI e specifications	https://www.audi-mediacenter.com/en/press-releases/sharpened-design-and-innovative-technologies-for-the-flagship-the-enhanced-audi-a8-14358;https://www.auto-data.net/en/audi-a8-d5-facelift-2021-60-tfsi-e-v6-462hp-plug-in-hybrid-quattro-tiptronic-52201
EU-AUDI-ALLROAD-C5-4BH-WAGON-01	4810	1852	1551	Audi Press UK allroad quattro 2.5 TDI technical data	https://press.audi.co.uk/assets/documents/original/18362-AudiUK00001044Audiallroadquattro25TDI.pdf
EU-AUDI-COUPE-B2-COUPE-PREFL-01	4349	1682	1350	Auto-Data Audi Coupe B2 specifications	https://www.auto-data.net/en/audi-coupe-model-502
EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	4421	1682	1350	Auto-Data Audi Coupe B2 facelift specifications	https://www.auto-data.net/en/audi-coupe-model-502
EU-AUDI-COUPE-B3-89-COUPE-PREFL-01	4366	1716	1370	Automobile-Catalog 1990 Audi Coupe 2.0 E specifications	https://www.automobile-catalog.com/car/1990/236270/audi_coupe_2_0_e_cat.html
EU-AUDI-CABRIOLET-8G-CONVERTIBLE-01	4366	1716	1379	Automobile-Catalog 1995 Audi Cabriolet 1.9 TDI specifications	https://www.automobile-catalog.com/car/1995/237575/audi_cabriolet_1_9_tdi.html
EU-AUDI-COUPE-B3-8B-COUPE-FACELIFT-01	4366	1716	1375	Automobile-Catalog 1992 Audi Coupe 16V specifications	https://www.automobile-catalog.com/car/1992/237290/audi_coupe_16v.html
EU-AUDI-E-TRON-GT-I-F8-SEDAN-PREFL-01	4989	1964	1413	Audi Singapore e-tron GT quattro specification sheet	https://s7test3.scene7.com/is/content/audi/nemo/sg/Models/etronGT/Audi%20e-tron%20GT%20-%20Digital%20Spec%20sheet%20%28Feb%2024%29.pdf
EU-AUDI-E-TRON-GT-I-F8-SEDAN-FACELIFT-01	5004	1964	1402	Audi MediaCenter e-tron GT quattro technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1544/file_en/99b3ba2115bf1328f670ae087320f1022152ddcc/eTD-Audi-e-tron-GT-quattro-370kW_260202.pdf
EU-AUDI-E-TRON-GT-I-F8-RS-SEDAN-FACELIFT-01	4997	1964	1394	Audi MediaCenter RS e-tron GT performance technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1392/file_en/91bfc69ec55530e277b5023245b77c1c82772920/eTD-Audi-RS-e-tron-GT-performance-550kW_240725.pdf
EU-AUDI-E-TRON-GT-I-F8-RS-SEDAN-PREFL-01	4989	1964	1414	Audi Singapore RS e-tron GT specification sheet	https://emea-dam.audi.com/adobe/assets/urn:aaid:aem:f18d3834-58ca-4c89-ba91-0dc37841d39b/original/as/Audi_RS_e-tron_GT_Digital_Spec_Sheet_Dec_23_for_Jan_24.pdf
EU-AUDI-E-TRON-I-GE-S-SUV-01	4902	1976	1664	Audi USA 2022 e-tron S Model Line Technical Specifications	https://media.audiusa.com/assets/documents/original/8949-2022etronSetronSSportbackTechSpecs.pdf
EU-AUDI-E-TRON-GT-I-F8-S-SEDAN-FACELIFT-01	5004	1964	1394	Audi MediaCenter S e-tron GT technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1391/file_en/086ccaba000dff5b2356c64762667387000f86a3/eTD-Audi-S-e-tron-GT-435kW_250515.pdf
EU-AUDI-Q2-I-GA-SUV-PREFL-01	4191	1794	1508	Auto-Data Audi Q2 2016-2020 specifications	https://www.auto-data.net/en/audi-q2-generation-4712
EU-AUDI-Q2-I-GA-SUV-FACELIFT-01	4208	1794	1508	Audi MediaCenter Q2 facelift dimensions	https://www.audi-mediacenter.com/de/publikationen/abmessungen/abmessungen-q2-1411/download
EU-AUDI-Q3-I-8U-SUV-FACELIFT-01	4388	1831	1608	Audi UK Q3 Pricing and Specification Guide	https://press.audi.co.uk/assets/documents/original/20423-AudiUK00017558AudiQ3PricingandSpecification.pdf
EU-AUDI-Q3-I-8U-SUV-PREFL-01	4385	1831	1608	Automobile-Catalog 2012 Audi Q3 2.0 TFSI quattro specifications	https://www.automobile-catalog.com/car/2012/1586090/audi_q3_2_0_tfsi_quattro_170_s-tronic.html
EU-AUDI-Q3-III-FJ-SUV-01	4531	1859	1623	Audi MediaCenter Q3 SUV TFSI technical data; Audi MediaCenter Q3 SUV TDI technical data	https://uploads.audi-mediacenter.com/system/production/car_motorizations/1551/file_de/61ce1d412c7c0dcc4d612645bda9190777cefca8/TD-Audi-Q3-SUV-TFSI-S_tronic-110kW_250616.pdf;https://uploads.audi-mediacenter.com/system/production/car_motorizations/1550/file_en/9293f8e1d514537805c8faea19ce68c53a377c97/eTD-Audi-Q3-SUV-TDI-S_tronic-110kW_250616.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1201-1300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/audi-a8l-d4-4h-2.5-fsi-v6-204hp-tiptronic-27135?utm_source=chatgpt.com "Audi A8L (D4, 4H) 2.5 FSI V6 (204 Hp) tiptronic /Sedan 2012"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1548 行）
- 累计尺寸组：dimension_groups_final.tsv（485 行）

