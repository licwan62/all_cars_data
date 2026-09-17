# 任务：left18448 第 6801-6900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0069__802bc892


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6801-6900 行

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
left18448 第 6801-6900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6801-6900_ktype_dimension_mapping_final.tsv
- left18448_6801-6900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Hyundai	I30	1.4	Kombi	Frontantrieb	Benzin	Oct 2007	Jun 2012	10609
Hyundai	I30	1.4	Kombi	Frontantrieb	Benzin	Jun 2012	Dec 2015	56798
Hyundai	I30	1.4	Coupe	Frontantrieb	Benzin	May 2013	Dec 2014	59318
Hyundai	I30	1.4	Kombi	Frontantrieb	Benzin	Jan 2014	May 2017	109978
Hyundai	I30	1.4	Schrägheck	Frontantrieb	Benzin	Dec 2014	Dec 2016	111078
Hyundai	I30	1.4	Coupe	Frontantrieb	Benzin	Dec 2014	-	117970
Hyundai	I30	1.6	Schrägheck	Frontantrieb	Benzin	Dec 2011	Dec 2015	55786
Hyundai	I30	1.6	Kombi	Frontantrieb	Benzin	Jun 2012	-	56799
Hyundai	I30	1.6	Kombi	Frontantrieb	Benzin	Jun 2012	Dec 2015	56804
Hyundai	I30	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Nov 2016	-	124834
Hyundai	I30	1.0 T-gdi	Kombi	Frontantrieb	Benzin	Mar 2017	-	127357
Hyundai	I30	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	May 2024	-	159195
Hyundai	I30	1.0 T-gdi	Kombi	Frontantrieb	Benzin	May 2024	-	159196
Hyundai	I30	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	Jan 2026	-	802827
Hyundai	I30	1.0 T-gdi	Kombi	Frontantrieb	Benzin	Jan 2026	-	802830
Hyundai	I30	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	Aug 2024	-	801491
Hyundai	I30	1.0 T-gdi Hybrid 48V	Kombi	Frontantrieb	Benzin/Elektro	Apr 2025	-	801952
Hyundai	I30	1.4 Crdi	Kombi	Frontantrieb	Diesel	Jun 2012	May 2017	56801
Hyundai	I30	1.4 Crdi	Coupe	Frontantrieb	Diesel	May 2013	May 2017	59320
Hyundai	I30	1.4 MPI	Schrägheck	Frontantrieb	Benzin	Nov 2016	Dec 2020	126883
Hyundai	I30	1.4 MPI	Kombi	Frontantrieb	Benzin	Mar 2017	Dec 2020	128291
Hyundai	I30	1.4 T-gdi	Schrägheck	Frontantrieb	Benzin	Nov 2016	Dec 2020	124836
Hyundai	I30	1.4 T-gdi	Kombi	Frontantrieb	Benzin	Mar 2017	Dec 2020	127358
Hyundai	I30	1.5 DPI	Kombi	Frontantrieb	Benzin	Apr 2024	-	800065
Hyundai	I30	1.5 DPI	Schrägheck	Frontantrieb	Benzin	Apr 2024	-	800066
Hyundai	I30	1.5 DPI	Schrägheck	Frontantrieb	Benzin	Apr 2024	-	800067
Hyundai	I30	1.5 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	May 2024	-	159197
Hyundai	I30	1.5 T-gdi Hybrid 48V	Kombi	Frontantrieb	Benzin/Elektro	May 2024	-	159198
Hyundai	I30	1.5 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	May 2024	-	801341
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Jan 2010	Nov 2011	11146
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Jan 2010	Jun 2012	11147
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Dec 2011	Dec 2015	55571
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Jun 2012	Dec 2015	56802
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Jun 2012	-	56803
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Dec 2011	Dec 2016	56806
Hyundai	I30	1.6 Crdi	Coupe	Frontantrieb	Diesel	May 2013	-	59321
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Jun 2012	-	109979
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2011	Dec 2016	111071
Hyundai	I30	1.6 Crdi	Coupe	Frontantrieb	Diesel	May 2013	-	117964
Hyundai	I30	1.6 Crdi	Coupe	Frontantrieb	Diesel	Dec 2014	-	117967
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2016	-	124833
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2016	-	124837
Hyundai	I30	1.6 Crdi	Schrägheck	Frontantrieb	Diesel	Nov 2016	-	124839
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Mar 2017	-	127359
Hyundai	I30	1.6 Crdi	Kombi	Frontantrieb	Diesel	Mar 2017	-	127360
Hyundai	I30	1.6 GDI	Kombi	Frontantrieb	Benzin	Jun 2012	-	56800
Hyundai	I30	1.6 GDI	Coupe	Frontantrieb	Benzin	May 2013	-	59319
Hyundai	I30	1.6 MPI	Coupe	Frontantrieb	Benzin	May 2013	-	124009
Hyundai	I30	1.6 T-gdi	Schrägheck	Frontantrieb	Benzin	Jan 2015	-	109980
Hyundai	I30	1.6 T-gdi	Coupe	Frontantrieb	Benzin	Jan 2015	-	111156
Hyundai	I30	1.6 T-gdi	Kasten/Schrägheck	Frontantrieb	Benzin	May 2015	-	801331
Hyundai	I30	1.6 T-gdi	Schrägheck	Frontantrieb	Benzin	Feb 2026	-	802828
Hyundai	I30	1.6 T-gdi	Kombi	Frontantrieb	Benzin	Feb 2026	-	802829
Hyundai	I30	2.0 Crdi	Schrägheck	Frontantrieb	Diesel	Oct 2007	Nov 2011	58603
Hyundai	I30	2.0 Crdi	Kombi	Frontantrieb	Diesel	Oct 2008	Jun 2012	58604
Hyundai	I30	2.0 N	Schrägheck	Frontantrieb	Benzin	Mar 2021	-	145004
Hyundai	I30	2.0 N	Schrägheck	Frontantrieb	Benzin	Mar 2021	-	145789
Hyundai	I40 i	1.6 GDI	Stufenheck	Frontantrieb	Benzin	Mar 2012	May 2019	55572
Hyundai	I40 i	1.7 Crdi	Stufenheck	Frontantrieb	Diesel	Mar 2012	May 2019	55574
Hyundai	I40 i	1.7 Crdi	Stufenheck	Frontantrieb	Diesel	Mar 2012	May 2019	55575
Hyundai	I40 i	1.7 Crdi	Stufenheck	Frontantrieb	Diesel	Jan 2015	May 2019	115229
Hyundai	I40 i	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	Oct 2012	May 2019	117569
Hyundai	I40 i	2.0 GDI	Stufenheck	Frontantrieb	Benzin	Mar 2012	May 2019	55573
Hyundai	I40 i	2.0 GDI	Stufenheck	Frontantrieb	Benzin	Dec 2014	May 2019	111080
Hyundai	I40 i cw	1.6 GDI	Kombi	Frontantrieb	Benzin	Jul 2011	May 2019	10618
Hyundai	I40 i cw	1.7 Crdi	Kombi	Frontantrieb	Diesel	Jul 2011	May 2019	10622
Hyundai	I40 i cw	1.7 Crdi	Kombi	Frontantrieb	Diesel	Jul 2011	May 2019	10623
Hyundai	I40 i cw	1.7 Crdi	Kombi	Frontantrieb	Diesel	Jan 2015	May 2019	113136
Hyundai	I40 i cw	2.0 Cvvt	Kombi	Frontantrieb	Benzin	Oct 2012	May 2019	117570
Hyundai	I40 i cw	2.0 GDI	Kombi	Frontantrieb	Benzin	Jul 2011	May 2019	10620
Hyundai	I40 i cw	2.0 GDI	Kombi	Frontantrieb	Benzin	Dec 2014	May 2019	115231
Hyundai	ii	1.6 16V	Coupe	Frontantrieb	Benzin	Mar 2002	Aug 2009	18843
Hyundai	ii	1.6 16V	Coupe	Frontantrieb	Benzin	Mar 2002	Aug 2009	18844
Hyundai	ii	2.0 GLS	Coupe	Frontantrieb	Benzin	Feb 2003	Aug 2009	17266
Hyundai	Inster	EV	Schrägheck	Frontantrieb	Elektro	Sep 2024	-	800768
Hyundai	Inster	EV	Schrägheck	Frontantrieb	Elektro	Sep 2024	-	800769
Hyundai	Ioniq	1.6 GDI Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2016	Jul 2022	120519
Hyundai	Ioniq	1.6 GDI Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	Mar 2016	Jul 2022	145292
Hyundai	Ioniq	Electric	Schrägheck	Frontantrieb	Elektro	Mar 2016	Aug 2019	120520
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	May 2021	-	144143
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	May 2021	-	144144
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	May 2021	-	145667
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	Oct 2022	-	151124
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	Oct 2022	-	151126
Hyundai	Ioniq	EV	SUV	Heckantrieb	Elektro	Feb 2025	-	161409
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	Jul 2023	-	801318
Hyundai	Ioniq	EV	Schrägheck	Heckantrieb	Elektro	Dec 2025	-	802832
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	May 2021	-	144141
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	May 2021	-	144142
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	May 2021	-	145668
Hyundai	Ioniq	EV Allrad	Schrägheck	Allrad	Elektro	Oct 2022	-	151129
Hyundai	Ioniq	EV Htrac I	SUV	Allrad	Elektro	Feb 2025	-	161410
Hyundai	Ioniq	EV Htrac I	SUV	Allrad	Elektro	Feb 2025	-	162084
Hyundai	Ioniq	EV Htrac I	SUV	Allrad	Elektro	Feb 2025	-	162087
Hyundai	Ioniq	EV Htrac II	SUV	Allrad	Elektro	Feb 2025	-	161411
Hyundai	Ioniq	EV Htrac II	SUV	Allrad	Elektro	Feb 2025	-	162085
Hyundai	Ioniq	EV Htrac II	SUV	Allrad	Elektro	Feb 2025	-	162086
Hyundai	Ioniq	N Allrad	Schrägheck	Allrad	Elektro	Nov 2023	-	156940
Hyundai	Ioniq	N EV Allrad	Schrägheck	Allrad	Elektro	Oct 2025	-	802730
Hyundai	Ix20	1.4 Crdi	Schrägheck	Frontantrieb	Diesel	Jun 2011	Jul 2019	10604


--- Round 1 / 首次发送 ---
## 更新点

* 完成 100 个输入 Ktype 的物理车身聚类，形成 113 条完整映射。
* 修正关键边界：`145004` 对应 i30 N 五门掀背，`145789` 对应 i30 Fastback N；两者分别采用 `4340×1795×1445 mm` 和 `4455×1795×1419 mm`，不得共用尺寸组。([汽车配件24][1])
* Ioniq 9 资料中的车型代码为 `ME/ME1` 组合；因单行禁止填写组合 BodyCode，本表保留为空，没有任意选择其中一个代码。([AK24配件][2])
* 已完成固定表头、唯一 ID、引用闭合、正整数三维、来源非空及文件名检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：113
* PENDING 映射：0
* 已确认尺寸组：28
* 孤立尺寸组：0
* 未闭合引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10609_prefl	10609	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
10609_facelift	10609	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
56798	56798	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
59318	59318	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
109978	109978	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
111078	111078	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
117970	117970	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
55786	55786	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
56799	56799	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
56804	56804	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
124834	124834	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
127357	127357	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
159195	159195	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1455-01	HIGH		READY
159196	159196	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	HIGH		READY
802827	802827	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1465-01	MEDIUM	按该年款动力对应的已确认高车高外廓关联。	READY
802830	802830	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	MEDIUM	按该年款动力对应的已确认旅行版外廓关联。	READY
801491	801491	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1455-01	MEDIUM	按该年款动力对应的已确认低车高外廓关联。	READY
801952	801952	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	MEDIUM	按该年款动力对应的已确认旅行版外廓关联。	READY
56801	56801	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
59320	59320	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
126883	126883	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
128291	128291	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
124836	124836	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
127358	127358	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
800065	800065	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	HIGH		READY
800066	800066	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1465-01	HIGH		READY
800067	800067	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1465-01	HIGH		READY
159197	159197	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1455-01	HIGH		READY
159198	159198	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	HIGH		READY
801341	801341	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1455-01	HIGH		READY
11146	11146	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	HIGH		READY
11147	11147	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	HIGH		READY
55571	55571	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
56802	56802	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
56803	56803	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
56806	56806	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
59321	59321	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
109979	109979	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
111071	111071	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
117964	117964	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
117967	117967	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
124833	124833	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
124837	124837	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
124839	124839	Hatchback	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-HATCHBACK-01	HIGH		READY
127359	127359	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
127360	127360	Wagon	i30 III	PD	5	EU-HYUNDAI-I30-III-PD-WAGON-01	HIGH		READY
56800	56800	Wagon	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-WAGON-01	HIGH		READY
59319	59319	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
124009	124009	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
109980	109980	Hatchback	i30 II	GD	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	HIGH		READY
111156	111156	Coupe	i30 II	GD	3	EU-HYUNDAI-I30-II-GD-COUPE-01	HIGH		READY
801331	801331	Van	i30 II	GDE	5	EU-HYUNDAI-I30-II-GD-HATCHBACK-01	MEDIUM	GDE 五门厢式掀背外廓，与 GD 掀背尺寸组共用。	READY
802828	802828	Hatchback	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1465-01	MEDIUM	按该年款动力对应的已确认高车高外廓关联。	READY
802829	802829	Wagon	i30 III facelift 2024	PD	5	EU-HYUNDAI-I30-III-FL2024-WAGON-01	MEDIUM	按该年款动力对应的已确认旅行版外廓关联。	READY
58603	58603	Hatchback	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	HIGH		READY
58604	58604	Wagon	i30 I	FD	5	EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	HIGH		READY
145004	145004	Hatchback	i30 III N	PD	5	EU-HYUNDAI-I30-III-N-PD-HATCHBACK-01	HIGH	2021 i30 N Performance Package 掀背外廓。	READY
145789	145789	Fastback	i30 III N Fastback	PDE	5	EU-HYUNDAI-I30-III-N-PDE-FASTBACK-01	HIGH	Ktype 对应五门 Fastback N，而非普通掀背外廓。	READY
55572_prefl	55572	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
55572_facelift	55572	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
55574_prefl	55574	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
55574_facelift	55574	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
55575_prefl	55575	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
55575_facelift	55575	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
115229	115229	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH		READY
117569_prefl	117569	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
117569_facelift	117569	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
55573_prefl	55573	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
55573_facelift	55573	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
111080	111080	Sedan	i40	VF	4	EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	HIGH		READY
10618_prefl	10618	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
10618_facelift	10618	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
10622_prefl	10622	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
10622_facelift	10622	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
10623_prefl	10623	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
10623_facelift	10623	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
113136	113136	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH		READY
117570_prefl	117570	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
117570_facelift	117570	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
10620_prefl	10620	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
10620_facelift	10620	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
115231	115231	Wagon	i40	VF	5	EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	HIGH		READY
18843	18843	Coupe	Coupe II	GK	3	EU-HYUNDAI-COUPE-II-GK-COUPE-01	HIGH		READY
18844	18844	Coupe	Coupe II	GK	3	EU-HYUNDAI-COUPE-II-GK-COUPE-01	HIGH		READY
17266	17266	Coupe	Coupe II	GK	3	EU-HYUNDAI-COUPE-II-GK-COUPE-01	HIGH		READY
800768	800768	Hatchback	Inster	AX1	5	EU-HYUNDAI-INSTER-AX1-HATCHBACK-H1575-01	HIGH		READY
800769_h1575	800769	Hatchback	Inster	AX1	5	EU-HYUNDAI-INSTER-AX1-HATCHBACK-H1575-01	HIGH	Long Range 的 INSTER 01 标准车高外廓。	READY
800769_h1610	800769	Hatchback	Inster	AX1	5	EU-HYUNDAI-INSTER-AX1-HATCHBACK-H1610-01	HIGH	Long Range 的 INSTER 02 17 英寸高车身外廓。	READY
120519	120519	Hatchback	Ioniq (AE)	AE	5	EU-HYUNDAI-IONIQ-AE-HATCHBACK-01	HIGH		READY
145292	145292	Hatchback	Ioniq (AE)	AE	5	EU-HYUNDAI-IONIQ-AE-HATCHBACK-01	HIGH		READY
120520	120520	Hatchback	Ioniq (AE)	AE	5	EU-HYUNDAI-IONIQ-AE-HATCHBACK-01	HIGH		READY
144143	144143	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
144144	144144	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
145667	145667	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
151124	151124	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
151126	151126	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
161409	161409	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
801318	801318	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
802832	802832	SUV	Ioniq 5 facelift 2024	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-FACELIFT-01	MEDIUM	按 2024 改款 Ioniq 5 外廓关联。	READY
144141	144141	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
144142	144142	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
145668	145668	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
151129	151129	SUV	Ioniq 5	NE	5	EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	HIGH	输入掀背标签按 Ioniq 5 跨界 SUV 车身归一。	READY
161410	161410	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
162084	162084	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
162087	162087	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
161411	161411	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
162085	162085	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
162086	162086	SUV	Ioniq 9		5	EU-HYUNDAI-IONIQ-9-SUV-01	HIGH		READY
156940	156940	SUV	Ioniq 5 N	NE	5	EU-HYUNDAI-IONIQ-5-N-NE-SUV-01	HIGH		READY
802730	802730	SUV	Ioniq 5 N	NE	5	EU-HYUNDAI-IONIQ-5-N-NE-SUV-01	MEDIUM		READY
10604_prefl	10604	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-PREFL-01	HIGH	改款前物理外廓。	READY
10604_facelift	10604	MPV	ix20	JC	5	EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	HIGH	改款后物理外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6801-6900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-I30-I-FD-WAGON-PREFL-01	4475	1775	1565	Hyundai Motor official i30 FD cw heritage	https://www.hyundai.com/kr/ko/brand/brandstory/heritage/2000-i30-fd-cw
EU-HYUNDAI-I30-I-FD-WAGON-FACELIFT-01	4500	1775	1565	Auto-Data Hyundai i30 I CW facelift 2010	https://www.auto-data.net/en/hyundai-i30-i-cw-facelift-2010-generation-5725
EU-HYUNDAI-I30-II-GD-WAGON-01	4485	1780	1500	Auto-Data Hyundai i30 II CW 1.4 MPI	https://www.auto-data.net/en/hyundai-i30-ii-cw-1.4-mpi-100hp-18545
EU-HYUNDAI-I30-II-GD-COUPE-01	4300	1780	1470	Auto-Data Hyundai i30 II Coupe	https://www.auto-data.net/en/hyundai-i30-ii-coupe-generation-4092
EU-HYUNDAI-I30-II-GD-HATCHBACK-01	4300	1780	1470	Auto-Data Hyundai i30 II	https://www.auto-data.net/en/hyundai-i30-ii-generation-4090
EU-HYUNDAI-I30-III-PD-HATCHBACK-01	4340	1795	1455	Auto-Data Hyundai i30 III	https://www.auto-data.net/en/hyundai-i30-iii-generation-5152
EU-HYUNDAI-I30-III-PD-WAGON-01	4585	1795	1465	Auto-Data Hyundai i30 III CW 1.4 MPI	https://www.auto-data.net/en/hyundai-i30-iii-cw-1.4-100hp-30226
EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1455-01	4340	1795	1455	Auto-Data Hyundai i30 III facelift 2024 1.0 T-GDI; Auto-Data Hyundai i30 III facelift 2024 1.5 T-GDI MHEV	https://www.auto-data.net/en/hyundai-i30-iii-facelift-2024-1.0-t-gdi-100hp-53164;https://www.auto-data.net/en/hyundai-i30-iii-facelift-2024-1.5-t-gdi-140hp-mild-hybrid-53166
EU-HYUNDAI-I30-III-FL2024-WAGON-01	4585	1795	1475	Auto-Data Hyundai i30 III CW facelift 2024 1.0 T-GDI; Auto-Data Hyundai i30 III CW facelift 2024 1.5 T-GDI MHEV	https://www.auto-data.net/en/hyundai-i30-iii-cw-facelift-2024-1.0-t-gdi-100hp-53180;https://www.auto-data.net/en/hyundai-i30-iii-cw-facelift-2024-1.5-t-gdi-140hp-mild-hybrid-53182
EU-HYUNDAI-I30-III-FL2024-HATCHBACK-H1465-01	4340	1795	1465	Auto-Data Hyundai i30 III facelift 2024 1.5 MPI; Auto-Data Hyundai i30 III facelift 2024 1.0 T-GDI 115	https://www.auto-data.net/en/hyundai-i30-iii-facelift-2024-1.5-mpi-96hp-55682;https://www.auto-data.net/en/hyundai-i30-iii-facelift-2024-1.0-t-gdi-115hp-56177
EU-HYUNDAI-I30-I-FD-HATCHBACK-FACELIFT-01	4280	1775	1480	Auto-Data Hyundai i30 I facelift 2010	https://www.auto-data.net/en/hyundai-i30-i-facelift-2010-generation-5724
EU-HYUNDAI-I30-I-FD-HATCHBACK-PREFL-01	4245	1775	1480	Hyundai Motor official i30 FD heritage	https://www.hyundai.com/kr/ko/brand/heritage/model/i30-history/2007-i30-fd
EU-HYUNDAI-I30-III-N-PD-HATCHBACK-01	4340	1795	1445	Hyundai Motor Europe i30 N technical specifications	https://www.hyundai.news/newsroom/dam/eu/models/20210528_i30_n_production_line/hyundai-i30-n-0521-technical-specifications.pdf
EU-HYUNDAI-I30-III-N-PDE-FASTBACK-01	4455	1795	1419	Hyundai Motor Europe i30 N technical specifications	https://www.hyundai.news/newsroom/dam/eu/models/20210528_i30_n_production_line/hyundai-i30-n-0521-technical-specifications.pdf
EU-HYUNDAI-I40-VF-SEDAN-PREFL-01	4770	1815	1470	Auto-Data Hyundai i40 Sedan	https://www.auto-data.net/en/hyundai-i40-sedan-generation-4095
EU-HYUNDAI-I40-VF-SEDAN-FACELIFT-01	4775	1815	1470	Auto-Data Hyundai i40 Sedan facelift 2015	https://www.auto-data.net/en/hyundai-i40-sedan-facelift-2015-generation-4647
EU-HYUNDAI-I40-VF-WAGON-PREFL-01	4815	1815	1470	Auto-Data Hyundai i40 Combi	https://www.auto-data.net/en/hyundai-i40-combi-generation-4094
EU-HYUNDAI-I40-VF-WAGON-FACELIFT-01	4775	1815	1470	Auto-Data Hyundai i40 Combi facelift 2015	https://www.auto-data.net/en/hyundai-i40-combi-facelift-2015-1.7-crdi-141hp-22496
EU-HYUNDAI-COUPE-II-GK-COUPE-01	4395	1760	1330	Auto-Data Hyundai Coupe II GK	https://www.auto-data.net/en/hyundai-coupe-ii-gk-generation-2991
EU-HYUNDAI-INSTER-AX1-HATCHBACK-H1575-01	3825	1610	1575	Hyundai Motor UK all-new INSTER pricing and specification	https://www.hyundai.news/newsroom/dam/uk/models/20241003_all_new_inster_pricing_and_specification/20241003_all-new-inster-pricing-and-specification.pdf
EU-HYUNDAI-INSTER-AX1-HATCHBACK-H1610-01	3825	1610	1610	Hyundai Motor UK all-new INSTER pricing and specification	https://www.hyundai.news/newsroom/dam/uk/models/20241003_all_new_inster_pricing_and_specification/20241003_all-new-inster-pricing-and-specification.pdf
EU-HYUNDAI-IONIQ-AE-HATCHBACK-01	4470	1820	1450	Hyundai Motor UK New IONIQ official specifications	https://www.hyundai.news/uk/articles/press-releases/new-ioniq-hyundais-revolutionary-eco-friendly-model.html
EU-HYUNDAI-IONIQ-5-NE-SUV-PREFL-01	4635	1890	1605	Hyundai Motor UK IONIQ 5 model year 2023 specifications	https://www.hyundai.news/newsroom/dam/uk/models/20220422_ioniq_5_product_enhancements_2023_model_year/hyundai-ioniq-5-product-enhancements-2023-specs.pdf
EU-HYUNDAI-IONIQ-9-SUV-01	5060	1980	1790	Hyundai Motor UK IONIQ 9 pricing specifications and technology	https://www.hyundai.news/newsroom/dam/uk/models/20250714_ioniq_9_pricing_specs_tech/hyundai-uk-ioniq-9-pricing-specs-tech-0725.pdf
EU-HYUNDAI-IONIQ-5-NE-SUV-FACELIFT-01	4655	1890	1605	Auto-Data Hyundai Ioniq 5 facelift 2024 Standard Range	https://www.auto-data.net/en/hyundai-ioniq-5-facelift-2024-standard-range-63-kwh-170hp-electric-52314
EU-HYUNDAI-IONIQ-5-N-NE-SUV-01	4715	1940	1585	Hyundai Motor Europe IONIQ 5 N technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20240325_ioniq_5_n/hyundai-ioniq-5-n-technical-data-0324.pdf
EU-HYUNDAI-IX20-JC-MPV-PREFL-01	4100	1765	1600	Automobile-Catalog Hyundai ix20 1.6 Style 2011	https://www.automobile-catalog.com/car/2011/1606640/hyundai_ix20_1_6_style.html
EU-HYUNDAI-IX20-JC-MPV-FACELIFT-01	4115	1765	1600	Hyundai Motor Europe ix20 technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20150315_ix20/20150320_technical_data_ix20.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6801-6900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-onderdelen24.nl/hyundai/i30-pde/145004/10420/claxon-meertonige-hoorn "https://www.auto-onderdelen24.nl/hyundai/i30-pde/145004/10420/claxon-meertonige-hoorn"
[2]: https://www.ak24parts.com/en/hyundai-spareparts/161409/ioniq-9-me-me1-ev?srsltid=AfmBOooIJbX18dr7JgyPSIQq7cuw90EN6DLUf2Ul66m8KGSermJSIDya "https://www.ak24parts.com/en/hyundai-spareparts/161409/ioniq-9-me-me1-ev?srsltid=AfmBOooIJbX18dr7JgyPSIQq7cuw90EN6DLUf2Ul66m8KGSermJSIDya"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3933 行）
- 累计尺寸组：dimension_groups_final.tsv（1086 行）

