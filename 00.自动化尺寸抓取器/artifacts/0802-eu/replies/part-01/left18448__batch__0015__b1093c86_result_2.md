# 任务：left18448 第 1401-1500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0015__b1093c86


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 1401-1500 行

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
left18448 第 1401-1500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_1401-1500_ktype_dimension_mapping_final.tsv
- left18448_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-Q5-I-8R-SUV-FACELIFT-01	4629	1898	1655
EU-AUDI-Q5-I-8R-SUV-PREFL-01	4629	1880	1653
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635
EU-AUDI-Q5-II-FY-SQ5-SUV-FACELIFT-01	4682	1893	1635
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-AUDI-Q5-II-FY-SUV-FACELIFT-01	4682	1893	1662
EU-AUDI-Q5-II-FYT-SPORTBACK-01	4689	1893	1660
EU-AUDI-Q5-II-FYT-SQ5-SPORTBACK-01	4689	1893	1633
EU-AUDI-Q5-III-GUB-SUV-01	4717	1900	1647
EU-AUDI-Q5-III-GUN-SPORTBACK-01	4717	1900	1642

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Audi	Q5	SQ5 TDI Quattro	SUV	Allrad	Diesel	Apr 2015	May 2017	112293
Audi	Q5	SQ5 TDI Quattro	SUV	Allrad	Diesel	Nov 2015	May 2017	117689
Audi	Q5	SQ5 Tfsi Quattro	SUV	Allrad	Benzin	May 2013	May 2017	100066
Audi	Q5	SQ5 Tfsi Quattro	SUV	Allrad	Benzin	Nov 2016	-	125184
Audi	Q5	SQ5 Tfsi Quattro	SUV	Allrad	Benzin/Elektro	Jan 2025	-	159653
Audi	Q5	SQ5 Tfsi Quattro	SUV	Allrad	Benzin/Elektro	Jan 2025	-	160304
Audi	Q6 e-Tron	E-tron	SUV	Heckantrieb	Elektro	Aug 2024	-	800504
Audi	Q6 e-Tron	E-tron	SUV	Heckantrieb	Elektro	Aug 2024	-	801101
Audi	Q6 e-Tron	E-tron Quattro	SUV	Allrad	Elektro	Apr 2024	-	158148
Audi	Q6 e-Tron	E-tron Quattro	SUV	Allrad	Elektro	Apr 2024	-	801261
Audi	Q6 e-Tron	Performance	SUV	Heckantrieb	Elektro	Jun 2024	-	159203
Audi	Q6 e-Tron	SQ6 E-tron Quattro	SUV	Allrad	Elektro	Apr 2024	-	158149
Audi	Q6 e-Tron sportback	83	SUV	Heckantrieb	Elektro	Dec 2024	-	159986
Audi	Q6 e-Tron sportback	83	SUV	Heckantrieb	Elektro	Dec 2024	-	801716
Audi	Q6 e-Tron sportback	100 Quattro	SUV	Allrad	Elektro	Dec 2024	-	159987
Audi	Q6 e-Tron sportback	100 Quattro	SUV	Allrad	Elektro	Dec 2024	-	801721
Audi	Q6 e-Tron sportback	E-tron Quattro	SUV	Allrad	Elektro	May 2025	-	803330
Audi	Q6 e-Tron sportback	Performance	SUV	Heckantrieb	Elektro	Dec 2024	-	159985
Audi	Q6 e-Tron sportback	Performance	SUV	Heckantrieb	Elektro	Dec 2024	-	801717
Audi	Q6 e-Tron sportback	SQ6 E-tron Quattro	SUV	Allrad	Elektro	Dec 2024	-	801722
Audi	Q6 e-Tron sportback	SQ6 Quattro	SUV	Allrad	Elektro	Dec 2024	-	159988
Audi	Q7	2.0 Tfsi Quattro	SUV	Allrad	Benzin	Aug 2015	-	116623
Audi	Q7	3.0 45 TDI Mild Hybrid Quattro	Kasten/SUV	Allrad	Diesel/Elektro	Jul 2018	Dec 2019	142566
Audi	Q7	3.0 50 TDI Mild Hybrid Quattro	Kasten/SUV	Allrad	Diesel/Elektro	Jul 2018	Dec 2019	142573
Audi	Q7	3.0 TDI E-tron Quattro	SUV	Allrad	Diesel/Elektro	Aug 2015	Dec 2019	117760
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	May 2011	Aug 2015	10442
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Mar 2006	May 2008	19016
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	May 2010	Aug 2015	34967
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Jan 2015	Dec 2019	113153
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Jun 2015	Dec 2019	113404
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Jun 2015	Dec 2019	116263
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Aug 2015	Dec 2019	117122
Audi	Q7	3.0 TDI Quattro	SUV	Allrad	Diesel	Aug 2015	Dec 2019	117857
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Nov 2010	Aug 2015	142550
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Mar 2006	May 2010	142551
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Aug 2015	Dec 2019	142552
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Mar 2006	May 2008	142567
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Nov 2007	May 2012	142568
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	May 2011	Aug 2015	142569
Audi	Q7	3.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Jan 2015	Dec 2019	142570
Audi	Q7	3.0 Tfsi Quattro	SUV	Allrad	Benzin	May 2011	Aug 2015	12086
Audi	Q7	3.0 Tfsi Quattro	SUV	Allrad	Benzin	May 2010	Aug 2015	34965
Audi	Q7	3.0 Tfsi Quattro	SUV	Allrad	Benzin	May 2010	Aug 2015	34966
Audi	Q7	3.0 Tfsi Quattro	SUV	Allrad	Benzin	Jan 2015	Dec 2019	113152
Audi	Q7	3.0 Tfsi Quattro	Kasten/SUV	Allrad	Benzin	May 2010	Aug 2015	142574
Audi	Q7	3.6 FSI Quattro	Kasten/SUV	Allrad	Benzin	Aug 2006	May 2010	142575
Audi	Q7	4.0 SQ7 TDI Quattro	Kasten/SUV	Allrad	Diesel	Apr 2016	-	142576
Audi	Q7	4.2 FSI Quattro	SUV	Allrad	Benzin	Mar 2006	May 2010	19012
Audi	Q7	4.2 FSI Quattro	Kasten/SUV	Allrad	Benzin	Aug 2006	May 2010	142579
Audi	Q7	4.2 TDI Quattro	Kasten/SUV	Allrad	Diesel	Mar 2007	Jun 2009	142577
Audi	Q7	4.2 TDI Quattro	Kasten/SUV	Allrad	Diesel	Mar 2007	Aug 2015	142578
Audi	Q7	45 TDI Quattro	SUV	Allrad	Diesel	Jul 2019	-	145258
Audi	Q7	45 Tfsi Quattro	SUV	Allrad	Benzin	Nov 2022	-	151085
Audi	Q7	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158706
Audi	Q7	6.0 TDI Quattro	Kasten/SUV	Allrad	Diesel	Sep 2008	May 2014	142580
Audi	Q7	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	Oct 2020	-	151993
Audi	Q7	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158707
Audi	Q7	SQ7 TDI Quattro	SUV	Allrad	Diesel	Apr 2016	-	120590
Audi	Q8	45 Tfsi Quattro	SUV	Allrad	Benzin	Apr 2023	-	153685
Audi	Q8	50 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	151158
Audi	Q8	50 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	151159
Audi	Q8	55 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	150791
Audi	Q8	55 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	150792
Audi	Q8	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158661
Audi	Q8	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	Apr 2024	-	158688
Audi	Q8	RS Performance Quattro	SUV	Allrad	Benzin/Elektro	Jul 2024	-	800176
Audi	Q8	SQ8 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	150793
Audi	Q8	SQ8 Quattro	SUV	Allrad	Elektro	Nov 2022	Mar 2025	150794
Audi	Quattro	2.1 20V Turbo	Coupe	Allrad	Benzin	May 1984	Jul 1987	8861
Audi	Quattro	2.2 20V Turbo	Coupe	Allrad	Benzin	Aug 1989	Jul 1991	5081
Audi	Quattro	2.2 Turbo	Coupe	Allrad	Benzin	Aug 1987	Jul 1989	5071
Audi	R8	5.2 FSI	Cabriolet	Allrad	Benzin	Jul 2012	Jul 2015	143409
Audi	R8	5.2 FSI	Cabriolet	Allrad	Benzin	Jul 2012	Jul 2015	143428
Audi	R8	5.2 FSI	Coupe	Heckantrieb	Benzin	Jun 2021	-	145500
Audi	R8	5.2 FSI	Cabriolet	Heckantrieb	Benzin	Jun 2021	-	145501
Audi	R8	5.2 FSI Plus Quattro	Coupe	Allrad	Benzin	Jul 2015	-	115740
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	Nov 2010	Jul 2015	11141
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	Nov 2011	Jul 2015	12005
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	May 2012	Jul 2015	14762
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	Jul 2014	Jul 2015	106384
Audi	R8	5.2 FSI Quattro	Coupe	Allrad	Benzin	Jul 2015	-	115738
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	May 2016	Nov 2021	120716
Audi	R8	5.2 FSI Quattro	Cabriolet	Allrad	Benzin	May 2017	-	128150
Audi	R8	5.2 GT	Coupe	Heckantrieb	Benzin	Nov 2022	Apr 2024	800258
Audi	Super 90	1.8	Stufenheck	Frontantrieb	Benzin	Sep 1966	Aug 1971	14313
Audi	Tt	1.8 T	Cabriolet	Frontantrieb	Benzin	Oct 1999	Jun 2006	11342
Audi	Tt	1.8 T	Cabriolet	Frontantrieb	Benzin	Jan 2001	Jun 2006	15656
Audi	Tt	1.8 T	Coupe	Frontantrieb	Benzin	Sep 2002	Jun 2006	17143
Audi	Tt	1.8 T	Coupe	Frontantrieb	Benzin	Sep 2005	Jun 2006	18942
Audi	Tt	1.8 T	Coupe	Frontantrieb	Benzin	Sep 2005	Jun 2006	18944
Audi	Tt	1.8 T	Cabriolet	Frontantrieb	Benzin	Sep 2005	Jun 2006	18945
Audi	Tt	1.8 T Quattro	Cabriolet	Allrad	Benzin	Feb 2000	Jun 2006	11343
Audi	Tt	1.8 T Quattro	Cabriolet	Allrad	Benzin	Oct 1999	Jun 2006	11344
Audi	Tt	1.8 T Quattro	Coupe	Allrad	Benzin	Mar 2005	Jun 2006	18526
Audi	Tt	1.8 T Quattro	Coupe	Allrad	Benzin	Sep 2005	Jun 2006	18943
Audi	Tt	1.8 T Quattro	Cabriolet	Allrad	Benzin	Sep 2005	Jun 2006	18946
Audi	Tt	1.8 Tfsi	Coupe	Frontantrieb	Benzin	Jul 2015	Aug 2018	115102
Audi	Tt	1.8 Tfsi	Cabriolet	Frontantrieb	Benzin	Jul 2015	Aug 2018	115103
Audi	Tt	2.0 TDI	Coupe	Frontantrieb	Diesel	Jul 2014	-	106601
Audi	Tt	2.0 TDI	Cabriolet	Frontantrieb	Diesel	Nov 2014	-	108398


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批次 100 个输入 Ktype 的物理外廓聚类与映射。
* `120716` 的生产区间跨越 R8 II 2019 年外廓改款，拆分为 `120716_prefl` 与 `120716_facelift` 两条映射；改款后 Spyder 官方三维为 4429 × 1940 × 1242 mm。([audi.com][1])
* Q6 e-tron SUV 与 Sportback 分组；Q8 燃油版、Q8 e-tron、SQ8 e-tron 和 RS Q8 performance 均保持独立物理尺寸组。RS Q8 performance 官方尺寸图确认 5022 × 2007 × 1699 mm。([Audi Mediacenter][2])
* 已完成固定表头、唯一键、映射引用闭合、正整数三维、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：101
* PENDING 映射：0
* 已确认尺寸组：29
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复：0
* 孤立尺寸组：0
* 未闭合映射引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
112293	112293	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SQ5-SUV-01	HIGH		READY
117689	117689	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SQ5-SUV-01	HIGH		READY
100066	100066	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SQ5-SUV-01	HIGH		READY
125184	125184	SUV	Q5 I	8R	5	EU-AUDI-Q5-I-8R-SQ5-SUV-01	HIGH		READY
159653	159653	SUV	Q5 III	GUB	5	EU-AUDI-Q5-III-GUB-SUV-01	HIGH		READY
160304	160304	SUV	Q5 III	GUB	5	EU-AUDI-Q5-III-GUB-SUV-01	HIGH		READY
800504	800504	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
801101	801101	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
158148	158148	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
801261	801261	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
159203	159203	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
158149	158149	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SUV-01	HIGH		READY
159986	159986	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
801716	801716	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
159987	159987	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
801721	801721	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
803330	803330	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
159985	159985	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
801717	801717	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
801722	801722	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
159988	159988	SUV	Q6 e-tron I		5	EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	HIGH	Sportback 车顶外廓。	READY
116623	116623	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
142566	142566	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142573	142573	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
117760	117760	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
10442	10442	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
19016	19016	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
34967	34967	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
113153	113153	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
113404	113404	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
116263	116263	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
117122	117122	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
117857	117857	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
142550	142550	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142551	142551	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142552	142552	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142567	142567	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142568	142568	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142569	142569	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142570	142570	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
12086	12086	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
34965	34965	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
34966	34966	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
113152	113152	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-PREFL-01	HIGH		READY
142574	142574	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142575	142575	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142576	142576	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SQ7-SUV-PREFL-01	HIGH	Kasten/SUV 输入归入 SQ7 外廓。	READY
19012	19012	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH		READY
142579	142579	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142577	142577	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
142578	142578	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-SUV-01	HIGH	Kasten/SUV 输入归入同代 Q7 外廓。	READY
145258	145258	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH		READY
151085	151085	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH		READY
158706	158706	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT2-01	HIGH		READY
142580	142580	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-4L-V12-SUV-01	MEDIUM	V12 专属外观与悬架外廓。	READY
151993	151993	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	HIGH		READY
158707	158707	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SUV-FACELIFT2-01	HIGH		READY
120590	120590	SUV	Q7 II	4M	5	EU-AUDI-Q7-II-4M-SQ7-SUV-PREFL-01	HIGH		READY
153685	153685	SUV	Q8 I	F1	5	EU-AUDI-Q8-I-F1-SUV-PREFL-01	HIGH		READY
151158	151158	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SUV-01	HIGH	Q8 e-tron 电动车身。	READY
151159	151159	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SUV-01	HIGH	Q8 e-tron 电动车身。	READY
150791	150791	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SUV-01	HIGH	Q8 e-tron 电动车身。	READY
150792	150792	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SUV-01	HIGH	Q8 e-tron 电动车身。	READY
158661	158661	SUV	Q8 I	F1	5	EU-AUDI-Q8-I-F1-SUV-FACELIFT-PHEV-01	HIGH		READY
158688	158688	SUV	Q8 I	F1	5	EU-AUDI-Q8-I-F1-SUV-FACELIFT-PHEV-01	HIGH		READY
800176	800176	SUV	Q8 I	F1	5	EU-AUDI-Q8-I-F1-RS-PERFORMANCE-SUV-01	HIGH	RS performance 宽体外廓。	READY
150793	150793	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SQ8-SUV-01	HIGH	SQ8 e-tron 宽体外廓。	READY
150794	150794	SUV	Q8 e-tron I	GE	5	EU-AUDI-Q8-E-TRON-I-GE-SQ8-SUV-01	HIGH	SQ8 e-tron 宽体外廓。	READY
8861	8861	Coupe	Quattro B2	85	2	EU-AUDI-QUATTRO-B2-85-COUPE-01	HIGH		READY
5081	5081	Coupe	Quattro B2	85	2	EU-AUDI-QUATTRO-B2-85-COUPE-01	HIGH		READY
5071	5071	Coupe	Quattro B2	85	2	EU-AUDI-QUATTRO-B2-85-COUPE-01	HIGH		READY
143409	143409	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-SPYDER-V10-01	HIGH		READY
143428	143428	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-SPYDER-V10-01	HIGH		READY
145500	145500	Coupe	R8 II	4S	2	EU-AUDI-R8-II-4S-COUPE-FACELIFT-01	HIGH		READY
145501	145501	Convertible	R8 II	4S	2	EU-AUDI-R8-II-4S-SPYDER-FACELIFT-01	HIGH		READY
115740	115740	Coupe	R8 II	4S	2	EU-AUDI-R8-II-4S-COUPE-PREFL-01	HIGH		READY
11141	11141	Coupe	R8 I	42	2	EU-AUDI-R8-I-42-COUPE-V10-01	HIGH		READY
12005	12005	Convertible	R8 I	42	2	EU-AUDI-R8-I-42-SPYDER-V10-01	HIGH		READY
14762	14762	Coupe	R8 I	42	2	EU-AUDI-R8-I-42-COUPE-V10-01	HIGH		READY
106384	106384	Coupe	R8 I	42	2	EU-AUDI-R8-I-42-COUPE-V10-01	HIGH		READY
115738	115738	Coupe	R8 II	4S	2	EU-AUDI-R8-II-4S-COUPE-PREFL-01	HIGH		READY
120716_prefl	120716	Convertible	R8 II	4S	2	EU-AUDI-R8-II-4S-SPYDER-PREFL-01	MEDIUM	生产区间跨越 2019 改款，按外廓拆分。	READY
120716_facelift	120716	Convertible	R8 II	4S	2	EU-AUDI-R8-II-4S-SPYDER-FACELIFT-01	MEDIUM	生产区间跨越 2019 改款，按外廓拆分。	READY
128150	128150	Convertible	R8 II	4S	2	EU-AUDI-R8-II-4S-SPYDER-PREFL-01	HIGH		READY
800258	800258	Coupe	R8 II	4S	2	EU-AUDI-R8-II-4S-COUPE-FACELIFT-01	HIGH		READY
14313	14313	Sedan	Super 90	F103		EU-AUDI-SUPER-90-F103-SEDAN-01	MEDIUM	Ktype 未区分 2/4 门；两者共享三维，Doors 留空。	READY
11342	11342	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-FWD-01	HIGH		READY
15656	15656	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-FWD-01	HIGH		READY
17143	17143	Coupe	TT I	8N	2	EU-AUDI-TT-I-8N-COUPE-FWD-01	HIGH		READY
18942	18942	Coupe	TT I	8N	2	EU-AUDI-TT-I-8N-COUPE-FWD-01	HIGH		READY
18944	18944	Coupe	TT I	8N	2	EU-AUDI-TT-I-8N-COUPE-FWD-01	HIGH		READY
18945	18945	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-FWD-01	HIGH		READY
11343	11343	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	HIGH		READY
11344	11344	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	HIGH		READY
18526	18526	Coupe	TT I	8N	2	EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	HIGH		READY
18943	18943	Coupe	TT I	8N	2	EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	HIGH		READY
18946	18946	Convertible	TT I	8N	2	EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	HIGH		READY
115102	115102	Coupe	TT III	8S	2	EU-AUDI-TT-III-8S-COUPE-01	HIGH		READY
115103	115103	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH		READY
106601	106601	Coupe	TT III	8S	2	EU-AUDI-TT-III-8S-COUPE-01	HIGH		READY
108398	108398	Convertible	TT III	8S	2	EU-AUDI-TT-III-8S-ROADSTER-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_1401-1500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q5-I-8R-SQ5-SUV-01	4644	1911	1624	Audi UK SQ5 TDI plus technical data	https://press.audi.co.uk/assets/documents/original/21339-AudiUK00016124AudiSQ5TDIplus340PS.pdf
EU-AUDI-Q5-III-GUB-SUV-01	4717	1900	1647	Automobile Dimensions Audi Q5	https://www.automobiledimension.com/model/audi/q5
EU-AUDI-Q6-E-TRON-I-SUV-01	4771	1939	1648	Audi MediaCenter Q6 e-tron official press information	https://www.audi-mediacenter.com/en/the-audi-q6-e-tron-electric-mobility-on-a-new-level-15929/the-new-audi-q6-e-tron-experience-vorsprung-durch-technik-15930
EU-AUDI-Q6-E-TRON-I-SPORTBACK-01	4771	1965	1665	Audi MediaCenter Q6 Sportback e-tron official press release	https://www.audi-mediacenter.com/en/press-releases/exciting-design-and-longest-range-in-the-model-family-the-new-audi-q6-sportback-e-tron-16295
EU-AUDI-Q7-II-4M-SUV-PREFL-01	5052	1968	1741	Audi UK Q7 3.0 TDI quattro technical data	https://press.audi.co.uk/assets/documents/original/21929-AudiUK00016118AudiQ730TDIquattro.pdf
EU-AUDI-Q7-I-4L-SUV-01	5086	1983	1737	Audi UK Q7 3.0 TDI quattro technical data	https://press.audi.co.uk/assets/documents/original/21722-AudiUK00000879Q730TDIquattrotechdata.pdf
EU-AUDI-Q7-II-4M-SQ7-SUV-PREFL-01	5069	1968	1741	Audi UK SQ7 TDI technical data	https://press.audi.co.uk/assets/documents/original/22075-AudiUK00016128AudiSQ7TDI40litre.pdf
EU-AUDI-Q7-II-4M-SUV-FACELIFT-01	5063	1970	1740	Audi UK Q7 50 TDI quattro technical data October 2019	https://press.audi.co.uk/assets/documents/original/7057-AudiQ750TDIquattrotiptronicTechnicalDataUKOctober2019.pdf
EU-AUDI-Q7-II-4M-SUV-FACELIFT2-01	5072	1970	1748	Audi MediaCenter revised Q7 official press release	https://www.audi-mediacenter.com/en/press-releases/strong-in-design-comfort-and-technologythe-revised-audi-q7-15849
EU-AUDI-Q7-I-4L-V12-SUV-01	5063	2000	1697	Automobile-Catalog Audi Q7 V12 TDI; EncyCARpedia Audi Q7 V12 TDI	https://www.automobile-catalog.com/car/2008/1192460/audi_q7_v12_tdi_quattro.html;https://www.encycarpedia.com/audi/09-q7-v12-tdi-suv
EU-AUDI-Q8-I-F1-SUV-PREFL-01	4986	1995	1705	Automobile-Catalog Audi Q8 45 TDI 2023	https://www.automobile-catalog.com/car/2023/2979965/audi_q8_45_tdi_quattro.html
EU-AUDI-Q8-E-TRON-I-GE-SUV-01	4915	1937	1633	Audi MediaCenter Q8 e-tron official facts	https://www.audi-mediacenter.com/en/the-audi-q8-e-tron-until-2025-15069/the-facts-15071
EU-AUDI-Q8-I-F1-SUV-FACELIFT-PHEV-01	4992	1995	1717	Automobile-Catalog Audi Q8 55 TFSI e 2024	https://www.automobile-catalog.com/car/2024/3343520/audi_q8_suv_55_tfsi_e_quattro.html
EU-AUDI-Q8-I-F1-RS-PERFORMANCE-SUV-01	5022	2007	1699	Audi Norway RS Q8 performance official price and specification guide	https://media.audi.com/is/content/audi/country/no/assets/prislister/Prisliste-Audi-RS-Q8.pdf
EU-AUDI-Q8-E-TRON-I-GE-SQ8-SUV-01	4915	1976	1631	Audi MediaCenter Q8 e-tron official facts	https://www.audi-mediacenter.com/en/the-audi-q8-e-tron-until-2025-15069/the-facts-15071
EU-AUDI-QUATTRO-B2-85-COUPE-01	4404	1723	1344	Audi UK quattro brochure excerpt	https://press.audi.co.uk/assets/documents/original/28155-AudiUK00026353Audiquattrobrochureexcerpt.pdf
EU-AUDI-R8-I-42-SPYDER-V10-01	4440	1904	1244	Audi UK R8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/24231-AudiUK00001684AudiR8PricingandSpecification.pdf
EU-AUDI-R8-II-4S-COUPE-FACELIFT-01	4429	1940	1236	Audi UK R8 Coupe V10 RWD technical data July 2021	https://press.audi.co.uk/assets/documents/original/16970-AudiR8CoupeV10RWDStronicUKTechnicalDataJuly2021.pdf
EU-AUDI-R8-II-4S-SPYDER-FACELIFT-01	4429	1940	1242	Audi R8 Spyder V10 performance RWD official technical data	https://www.audi.com/system/production/car_motorizations/1326/file_en/f2481a78151e2a6496424fd169fdc2fbfe10498b/eTD_Audi_R8_Spyder_V10performance_RWD_419_kW_230113.pdf?1698163997=&disposition=attachment
EU-AUDI-R8-II-4S-COUPE-PREFL-01	4426	1940	1240	Audi UK R8 V10 plus Coupe technical data	https://press.audi.co.uk/assets/documents/original/25790-AudiUKAudiR8V10plusCoupe610.pdf
EU-AUDI-R8-I-42-COUPE-V10-01	4440	1929	1252	Audi UK R8 pricing and specification guide	https://press.audi.co.uk/assets/documents/original/24231-AudiUK00001684AudiR8PricingandSpecification.pdf
EU-AUDI-R8-II-4S-SPYDER-PREFL-01	4426	1940	1244	Audi UK R8 Spyder V10 technical data	https://press.audi.co.uk/assets/documents/original/26274-AudiUK00017613AudiR8SpyderV10540PS.pdf
EU-AUDI-SUPER-90-F103-SEDAN-01	4380	1626	1451	Automobile-Catalog Audi Super 90	https://www.automobile-catalog.com/car/1966/74330/audi_super_90.html
EU-AUDI-TT-I-8N-ROADSTER-FWD-01	4041	1764	1349	Audi UK TT Roadster 1.8 T 150PS technical data	https://press.audi.co.uk/assets/documents/original/22740-AudiUK00001067AudiTTRoadster18T150PS.pdf
EU-AUDI-TT-I-8N-COUPE-FWD-01	4041	1764	1346	Audi UK TT Coupe technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-AUDI-TT-I-8N-ROADSTER-QUATTRO-01	4041	1764	1348	Audi UK TT Roadster 1.8 T quattro technical data	https://press.audi.co.uk/assets/documents/original/22263-AudiUK00001054AudiTTRoadster225PSGerman.pdf
EU-AUDI-TT-I-8N-COUPE-QUATTRO-01	4041	1764	1345	Audi UK TT Coupe technical data	https://press.audi.co.uk/assets/documents/original/22250-AudiUK00000887TechnicalDataAudiTTCoup%C3%A9.pdf
EU-AUDI-TT-III-8S-COUPE-01	4177	1832	1353	Audi UK TT Coupe technical data	https://press.audi.co.uk/assets/documents/original/22721-AudiUK00000450AudiTTCoupeTechnicalData.pdf
EU-AUDI-TT-III-8S-ROADSTER-01	4177	1832	1355	Audi UK TT Roadster technical data	https://press.audi.co.uk/assets/documents/original/22926-AudiUK00000396.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_1401-1500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.audi.com/system/production/car_motorizations/1326/file_en/f2481a78151e2a6496424fd169fdc2fbfe10498b/eTD_Audi_R8_Spyder_V10performance_RWD_419_kW_230113.pdf?1698163997=&disposition=attachment&utm_source=chatgpt.com "eTD_Audi_R8_Spyder_V10perfo..."
[2]: https://uploads.audi-mediacenter.com/system/production/car_motorizations/1413/file_en/3a7285ef671eace91d1804b282586e43764f37da/eTD-Audi-Q6-Sportback-e-tron-quattro-285kW_241120.pdf?1732178370=&disposition=attachment "eTD-Audi-Q6-Sportback-e-tron-quattro-285kW_241120"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1751 行）
- 累计尺寸组：dimension_groups_final.tsv（528 行）

