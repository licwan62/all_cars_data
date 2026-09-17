# 任务：all 第 4901-5000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0050__4e28c4d4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4901-5000 行

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
all 第 4901-5000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALPINA-B3-G21-TOURING-PREFL-01	4719	1827	1438
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467
EU-AUDI-A6-C8-RS6-AVANT-01	4995	1951	1460
EU-BENTLEY-CONTINENTAL-GT-II-FACELIFT-SUPERSPORTS-COUPE-01	4818	1948	1391
EU-BENTLEY-CONTINENTAL-GT-II-V8S-COUPE-01	4806	1944	1404
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-CONVERTIBLE-01	4806	1944	1403
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SPEED-CONVERTIBLE-01	4806	1944	1393
EU-BENTLEY-CONTINENTAL-GTC-II-FACELIFT-SUPERSPORTS-CONVERTIBLE-01	4818	1947	1390
EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	4850	1954	1399
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
EU-BMW-3-G20-M340D-XDRIVE-SEDAN-01	4713	1827	1440
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435
EU-BMW-3-G20-SEDAN-XDRIVE-PREFL-01	4709	1827	1445
EU-BMW-3-G21-330E-WAGON-RWD-01	4709	1827	1442
EU-BMW-3-G21-M340I-XDRIVE-WAGON-01	4713	1827	1440
EU-BMW-3-G21-WAGON-RWD-01	4709	1827	1440
EU-BMW-3-G21-WAGON-XDRIVE-01	4709	1827	1445
EU-CITROEN-BERLINGO-II-B9-PLATFORM-CAB-01	4237	1810	1822
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852
EU-CITROEN-BERLINGO-III-K9-MPV-M-01	4403	1848	1844
EU-CITROEN-BERLINGO-III-K9-MPV-XL-01	4753	1848	1849
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1840
EU-CITROEN-BERLINGO-III-K9-VAN-M-4X4-01	4403	1848	1860
EU-CITROEN-BERLINGO-III-K9-VAN-XL-01	4753	1848	1849
EU-CITROEN-BERLINGO-III-K9-VAN-XL-4X4-01	4753	1848	1860
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1625
EU-DACIA-DUSTER-I-SUV-4X2-PREFL-01	4315	1822	1625
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693
EU-DACIA-DUSTER-II-SUV-4X4-01	4341	1804	1682
EU-DACIA-LOGAN-I-MCV-WAGON-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4247	1740	1534
EU-DACIA-LOGAN-I-VAN-FACELIFT-01	4450	1740	1640
EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	4358	1733	1517
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534
EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	4069	1733	1519
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480
EU-HYUNDAI-TUCSON-I-JM-SUV-2WD-01	4325	1795	1680
EU-HYUNDAI-TUCSON-I-JM-SUV-4WD-01	4325	1795	1720
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655
EU-JEEP-COMPASS-I-MK49-SUV-PREFL-AWD-01	4405	1810	1630
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684
EU-JEEP-RENEGADE-I-FACELIFT-FWD-SUV-01	4236	1805	1667
EU-JEEP-RENEGADE-I-PREFL-FWD-SUV-01	4236	1805	1667
EU-LEXUS-ES-VII-XZ10-SEDAN-01	4975	1865	1445
EU-LEXUS-LC-I-Z100-COUPE-01	4770	1920	1345
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450
EU-LEXUS-RX-IV-SUV-01	4890	1895	1690
EU-LEXUS-UX-I-ZA10-SUV-01	4495	1840	1540
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
EU-MERCEDES-BENZ-E-KLASSE-C238-AMG-E53-COUPE-01	4848	1860	1427
EU-MERCEDES-BENZ-E-KLASSE-C238-COUPE-FACELIFT-01	4835	1860	1428
EU-MERCEDES-BENZ-E-KLASSE-C238-E300D-COUPE-01	4826	1860	1430
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-FACELIFT-01	4945	1852	1460
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-FACELIFT-01	5634	1822	1506
EU-MERCEDES-BENZ-E-KLASSE-VF211-CHASSIS-PREFL-01	5596	1822	1496
EU-MERCEDES-BENZ-E-KLASSE-W212-SEDAN-FACELIFT-01	4879	1854	1474
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-01	4923	1852	1468
EU-MERCEDES-BENZ-E-KLASSE-W213-SEDAN-FACELIFT-01	4935	1852	1460
EU-MERCEDES-BENZ-GLE-I-SUV-01	4819	1935	1796
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE53-SUV-01	4937	2015	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-FACELIFT-01	4947	2018	1782
EU-MERCEDES-BENZ-GLE-V167-AMG-GLE63-SUV-PREFL-01	4947	2018	1785
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514
EU-PIAGGIO-PORTER-II-BUS-01	3400	1395	1870
EU-PORSCHE-911-991-2-CARRERA-T-COUPE-RWD-01	4527	1808	1285
EU-PORSCHE-911-991-2-GT2-RS-COUPE-RWD-01	4549	1880	1297
EU-PORSCHE-911-991-2-GT3-COUPE-RWD-01	4562	1852	1271
EU-PORSCHE-911-991-2-GT3-RS-COUPE-RWD-01	4557	1880	1297
EU-PORSCHE-911-991-2-SPEEDSTER-CONVERTIBLE-01	4562	1852	1250
EU-PORSCHE-911-992-CARRERA-CABRIOLET-01	4519	1852	1297
EU-PORSCHE-911-992-CARRERA-COUPE-01	4519	1852	1298
EU-PORSCHE-911-992-CARRERA-S-CABRIOLET-01	4519	1852	1299
EU-PORSCHE-911-992-CARRERA-S-COUPE-01	4519	1852	1300
EU-PORSCHE-911-997-1-TARGA-4S-01	4427	1852	1300
EU-PORSCHE-911-997-2-CARRERA-GTS-CONVERTIBLE-01	4435	1852	1300
EU-PORSCHE-911-997-2-TARGA-4S-01	4435	1852	1300
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696
EU-RENAULT-CAPTUR-II-HJB-SUV-01	4227	1797	1576
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2272
EU-RENAULT-MASTER-III-X62-CHASSIS-DOUBLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2263
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-FACELIFT-01	5670	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L2-FWD-PREFL-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-FACELIFT-01	6320	2070	2258
EU-RENAULT-MASTER-III-X62-CHASSIS-SINGLE-CAB-L3-FWD-PREFL-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L2-01	5643	2070	2273
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-DCAB-L3-01	6293	2070	2272
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L2-01	5643	2070	2265
EU-RENAULT-MASTER-III-X62-PHASE-II-CHASSIS-SCAB-L3-01	6293	2070	2258
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-FACELIFT-01	5557	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L2H1-PREFL-01	5530	2070	2270
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-FACELIFT-01	6207	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-PLATFORM-CAB-L3H1-PREFL-01	6180	2070	2264
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-FACELIFT-01	5075	2070	2303
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H1-PREFL-01	5048	2070	2307
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-FACELIFT-01	5075	2070	2496
EU-RENAULT-MASTER-III-X62-ZE-VAN-L1H2-PREFL-01	5048	2070	2500
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-FACELIFT-01	5575	2070	2495
EU-RENAULT-MASTER-III-X62-ZE-VAN-L2H2-PREFL-01	5548	2070	2499
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-PREFL-01	6198	2070	2488
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1799	1442
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-NARROW-01	3700	1660	1595
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	3700	1690	1595
EU-SUZUKI-VITARA-I-SUV-3D-01	3632	1630	1662
EU-SUZUKI-VITARA-I-SUV-5D-01	4030	1635	1700
EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	4175	1775	1610
EU-TOYOTA-PROACE-CITY-I-K9-VAN-LWB-01	4753	1848	1812
EU-TOYOTA-PROACE-CITY-I-K9-VAN-SWB-01	4403	1848	1880
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-LWB-01	4753	1848	1810
EU-TOYOTA-PROACE-CITY-VERSO-I-K9-MPV-SWB-01	4403	1848	1800
EU-TOYOTA-PROACE-II-MDZ4-PLATFORM-CAB-MEDIUM-01	4959	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-4X4-01	4609	1920	1940
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	4609	1920	1910
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-4X4-01	4959	1920	1950
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	4959	1920	1899
EU-TOYOTA-PROACE-VERSO-II-MPV-COMPACT-01	4609	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-LONG-01	5309	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPV-MEDIUM-01	4959	1920	1910
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-COMPACT-01	4606	1920	1905
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-LONG-01	5308	1920	1890
EU-TOYOTA-PROACE-VERSO-II-PREFL-MPV-MEDIUM-01	4956	1920	1890
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Volvo	V90 ii	B5 Mild-hybrid	Kombi	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	139800
Volvo	V90 ii	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139801
Volvo	V90 ii cross country	B5 Mild Hybrid AWD	Kombi	Allrad	Benzin/Elektro	184	250	Mar 2020	-	2025-06-01	139802
Porsche	911	3.8 Turbo S	Coupe	Allrad	Benzin	478	650	Mar 2020	May 2025	2026-03-01	139813
Porsche	911	3.8 Turbo S	Cabriolet	Allrad	Benzin	478	650	Mar 2020	May 2024	2024-08-01	139814
Ford	Ecosport	1.5 Ecoblue Tdci	SUV	Frontantrieb	Diesel	74	100	Nov 2017	-	2024-03-01	139824
Bentley	Continental	4.0 V8 AWD	Cabriolet	Allrad	Benzin	404	549	Jun 2019	-	2024-03-01	139829
Bentley	Continental	4.0 V8 AWD	Coupe	Allrad	Benzin	404	549	Jun 2019	-	2025-02-03	139830
Hyundai	I10 iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	100	Feb 2020	-	2024-03-01	139834
Hyundai	Elantra vii	1.6	Stufenheck	Frontantrieb	Benzin	90	123	Mar 2020	-	2024-03-01	139857
Volvo	V90 ii	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	256	348	Mar 2020	-	2024-03-01	139880
Volvo	Xc60 ii	B6 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	139881
Citroën	Berlingo	Electric	Großraumlimousine	Frontantrieb	Elektro	49	67	Sep 2017	Dec 2018	2026-05-01	139908
Mercedes-benz	Sprinter 4-T tourer	414 CDI	Bus	Heckantrieb	Diesel	105	143	Sep 2019	Dec 2021	2024-08-01	139926
Land Rover	Defender van	2.0 P300 SI4 4X4	Kasten/Geländewagen geschlossen	Allrad	Benzin	221	300	Feb 2020	-	2024-03-01	139927
Land Rover	Defender van	3.0 P400 I6 Mhev 4X4	Kasten/Geländewagen geschlossen	Allrad	Benzin/Elektro	294	400	Feb 2020	-	2024-03-01	139928
Land Rover	Defender van	2.0 D200 SD4 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel	147	200	Feb 2020	-	2024-03-01	139929
Land Rover	Defender van	2.0 D240 SD4 4X4	Kasten/Geländewagen geschlossen	Allrad	Diesel	177	241	Feb 2020	-	2024-03-01	139930
Citroën	Berlingo	Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jan 2018	Dec 2018	2026-05-01	139939
VW	Golf viii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	66	90	Feb 2020	-	2024-03-01	140003
VW	Golf viii	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Feb 2020	-	2024-03-01	140004
BMW	3	316 D	Stufenheck	Heckantrieb	Diesel	90	122	Mar 2020	-	2024-03-01	140024
Opel	Insignia b grand sport	1.5 Cdti	Schrägheck	Frontantrieb	Diesel	90	122	Feb 2020	-	2024-03-01	140030
Opel	Insignia b sports tourer	1.5 Cdti	Kombi	Frontantrieb	Diesel	90	122	Feb 2020	-	2024-03-01	140031
Suzuki	Ignis iii	1.2 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	61	83	Apr 2020	-	2024-03-01	140066
Suzuki	Ignis iii	1.2 Hybrid Allgrip	Schrägheck	Allrad	Benzin/Elektro	61	83	Apr 2020	-	2024-03-01	140067
Mclaren	765lt	4	Coupe	Heckantrieb	Benzin	563	765	Mar 2020	-	2024-03-01	140071
Mclaren	Speedtail	4.0 Hybrid	Coupe	Heckantrieb	Benzin/Elektro	787	1070	Dec 2019	-	2024-05-01	140074
Ferrari	Roma	3.9	Coupe	Heckantrieb	Benzin	456	620	Apr 2020	-	2024-03-01	140095
Toyota	Rav 4 v	2.5 Hybrid AWD	SUV	Allrad	Benzin/Elektro	163	222	Dec 2018	-	2024-03-01	140099
Seat	Leon	1.5 Etsi	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	140109
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	339	461	Jan 2019	May 2023	2026-03-01	140119
Porsche	Cayenne	3.0 E-hybrid AWD	SUV	Allrad	Benzin/Elektro	340	462	May 2017	May 2023	2026-03-01	140120
Seat	Leon	1.5 Etsi	Kombi	Frontantrieb	Benzin/Elektro	110	150	Mar 2020	-	2024-03-01	140121
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	110	150	Apr 2020	-	2024-03-01	140122
Morgan	Plus four	2	Cabriolet	Heckantrieb	Benzin	190	258	Mar 2020	-	2024-03-01	140123
Morgan	Plus six	3	Cabriolet	Heckantrieb	Benzin	250	340	Mar 2019	-	2024-03-01	140124
Renault	Master iii	2.3 DCI 180 FWD	Bus	Frontantrieb	Diesel	132	179	Jul 2019	Dec 2024	2026-03-01	140210
Hyundai	Tucson	2.0 Allrad	SUV	Allrad	Benzin	114	155	Jun 2015	Sep 2020	2024-03-01	140308
Mercedes-benz	Sprinter 3,5-T	Esprinter 312	Kasten	Frontantrieb	Elektro	85	116	Feb 2020	Dec 2023	2025-12-01	140321
Piaggio	Porter	1.3 LPG	Bus	Heckantrieb	Benzin/Autogas (LPG)	61	83	Nov 2015	-	2024-03-01	140328
Lexus	Es	300h	Stufenheck	Frontantrieb	Benzin/Elektro	160	218	Jul 2018	-	2024-03-01	140357
Lexus	Lc	500h	Coupe	Heckantrieb	Benzin/Elektro	264	359	May 2017	-	2025-06-01	140360
Lexus	Rx	450h	SUV	Frontantrieb	Benzin/Elektro	220	299	Mar 2009	Sep 2015	2025-12-01	140361
Lexus	Rx	450h AWD	SUV	Allrad	Benzin/Elektro	220	299	Mar 2009	Sep 2015	2025-12-01	140362
Lexus	Ls	500h AWD	Stufenheck	Allrad	Benzin/Elektro	264	359	Nov 2017	-	2024-03-01	140365
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	128	174	Apr 2020	-	2024-03-01	140366
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	128	174	Apr 2020	-	2024-03-01	140367
Lexus	Ux	300e	SUV	Frontantrieb	Elektro	150	204	Apr 2020	-	2024-03-01	140369
Opel	Insignia b grand sport	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	107	145	Apr 2020	-	2024-03-01	140375
Opel	Insignia b grand sport	2	Schrägheck	Frontantrieb	Benzin	147	200	Apr 2020	-	2024-03-01	140376
Opel	Insignia b grand sport	2.0 GSI 4X4	Schrägheck	Allrad	Benzin	169	230	Apr 2020	-	2024-03-01	140377
Opel	Insignia b sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	128	174	Apr 2020	-	2024-03-01	140378
Opel	Insignia b sports tourer	2	Kombi	Frontantrieb	Benzin	147	200	Apr 2020	-	2024-03-01	140379
Opel	Insignia b sports tourer	2.0 4X4	Kombi	Allrad	Benzin	169	230	Apr 2020	-	2024-03-01	140380
E.go	Life	60	Schrägheck	Heckantrieb	Elektro	57	77	Apr 2019	-	2024-03-01	140382
Toyota	Proace	2.0 D4D 4X4	Bus	Allrad	Diesel	110	150	Apr 2018	Dec 2022	2026-01-01	140383
Alpina	B3	Biturbo Allrad	Stufenheck	Allrad	Benzin	340	462	Sep 2019	Dec 2025	2026-06-01	140384
Dacia	Sandero	1.0 TCE 100	Schrägheck	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140386
Dacia	Sandero	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140387
Dacia	Duster	1.0 LPG	SUV	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jan 2019	-	2024-03-01	140388
Dacia	Logan	1.0 TCE 100	Stufenheck	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140389
Dacia	Logan	1.0 LPG	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140390
Dacia	Logan	1.0 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	74	101	Nov 2019	-	2024-03-01	140391
Dacia	Logan	1.0 TCE 100	Kombi	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	140392
Audi	A6 c8 avant	30 TDI Mild Hybrid	Kombi	Frontantrieb	Diesel/Elektro	100	136	Jan 2019	-	2024-03-01	140393
Audi	A6 c8	30 TDI Mild Hybrid	Stufenheck	Frontantrieb	Diesel/Elektro	100	136	Jan 2019	-	2024-03-01	140394
Mercedes-benz	Sprinter 4-T	411 CDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Feb 2018	Dec 2021	2024-08-01	140395
Xpeng	P7	EV	Stufenheck	Heckantrieb	Elektro	196	266	Apr 2020	-	2024-03-01	140398
Xpeng	P7	EV Allrad	Stufenheck	Allrad	Elektro	316	430	Apr 2020	-	2026-04-01	140399
Jeep	Renegade	1.3 Phev 4XE	SUV	Allrad	Benzin/Elektro	177	240	Aug 2020	-	2024-03-01	140402
Jeep	Compass	1.3 Hybrid 4X4	SUV	Allrad	Benzin/Elektro	177	240	Apr 2020	-	2024-03-01	140403
Renault	Clio v	1.0 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jun 2019	-	2026-05-01	140404
Renault	Captur ii	LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	74	101	Jan 2020	-	2024-03-01	140405
Mercedes-benz	Vito tourer	124 CDI	Bus	Heckantrieb	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140406
Mercedes-benz	Vito tourer	124 CDI 4-matic	Bus	Allrad	Diesel	176	239	Apr 2020	-	2025-02-03	140408
Mercedes-benz	Vito mixto	124 CDI	Kasten	Heckantrieb	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140412
Mercedes-benz	Vito mixto	124 CDI 4-matic	Kasten	Allrad	Diesel	176	239	Apr 2020	Dec 2020	2024-03-01	140413
Suzuki	Sx4 s-Cross	1.4 Hybrid	Schrägheck	Allrad	Benzin/Elektro	95	129	Aug 2019	Jun 2022	2025-06-01	140414
Suzuki	Sx4 s-Cross	1.4 Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	95	129	Aug 2019	Jun 2022	2025-06-01	140416
Suzuki	Vitara	1.4 Hybrid	SUV	Allrad	Benzin/Elektro	95	129	Jul 2019	-	2024-03-01	140419
Suzuki	Vitara	1.4 Hybrid	SUV	Frontantrieb	Benzin/Elektro	95	129	Jul 2019	-	2024-03-01	140420
Ligier	Js50	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140426
Ligier	Js50	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140427
Microcar	M.go	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140428
Microcar	M.go	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140429
Mercedes-benz	Gle	GLE 350 DE 4-matic	SUV	Allrad	Diesel/Elektro	235	320	Mar 2020	Mar 2023	2024-03-01	140436
Mercedes-benz	E-Klasse	E 300 DE	Kombi	Heckantrieb	Diesel/Elektro	225	306	Oct 2018	Oct 2023	2024-03-01	140437
Mercedes-benz	C-Klasse	C 300 E	Kombi	Heckantrieb	Benzin/Elektro	235	320	Jul 2019	Feb 2021	2024-03-01	140438
Mercedes-benz	C-Klasse	C 300 DE	Kombi	Heckantrieb	Diesel/Elektro	225	306	May 2019	Feb 2021	2024-03-01	140439
BMW	4	M 440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	285	387	Jul 2020	-	2024-03-01	140440
Honda	Jazz v	1.5 Ehev	Schrägheck	Frontantrieb	Benzin/Elektro	80	109	Feb 2020	-	2024-03-01	140441
BMW	4	420 I	Coupe	Heckantrieb	Benzin	135	184	Jul 2020	-	2024-03-01	140442
BMW	4	430 I	Coupe	Heckantrieb	Benzin	190	258	Jul 2020	-	2024-03-01	140443
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	190	258	Jul 2020	-	2025-06-01	140444
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140445
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	120	163	Jul 2020	-	2024-03-01	140446
BMW	4	420 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140448
Seat	Leon	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Mar 2020	-	2024-03-01	140449
Seat	Leon	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Mar 2020	-	2024-03-01	140450


--- Round 1 / 首次发送 ---
## 更新点

* 复用跨批次已有尺寸组 **32 个**，闭合 **50 条** Ktype 映射。
* 首次创建尺寸组 **9 个**，新增闭合 **12 条** Ktype 映射，包括 Porsche 911 Turbo S、Ferrari Roma、Toyota RAV4 V、Morgan Plus Four/Plus Six 和 BMW 4 Series G22。
* Porsche 官方规格明确给出不含后视镜宽度；Toyota、Morgan、Ferrari 与 BMW 新尺寸组均使用厂商规格资料闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：62
* PENDING 映射：38
* 已确认并被引用尺寸组：41
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139800	139800	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139801	139801	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139802	139802	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country 外廓。	READY
139813	139813	Coupe	911 992	992	2	EU-PORSCHE-911-992-TURBO-S-COUPE-01	HIGH	Turbo S Coupé 标准 PASM 外廓。	READY
139814	139814	Convertible	911 992	992	2	EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	HIGH	Turbo S Cabriolet 标准 PASM 外廓。	READY
139824	139824	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	第二代 SUV 外廓。	READY
139829	139829	Convertible	Continental GTC III		2	EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	HIGH	第三代 GTC 外廓。	READY
139834	139834	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门外廓。	READY
139880	139880	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139881	139881	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 SUV 外廓。	READY
139908	139908	MPV	Berlingo II Phase III	B9	5	EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	HIGH	B9 乘用 MPV 外廓。	READY
140003	140003	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	第八代五门外廓。	READY
140004	140004	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	第八代五门外廓。	READY
140024	140024	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20 后驱改款前外廓。	READY
140030	140030	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140031	140031	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 外廓。	READY
140066	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	欧洲宽体外廓。	READY
140067	140067	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	欧洲宽体外廓。	READY
140095	140095	Coupe	Roma I		2	EU-FERRARI-ROMA-I-COUPE-01	HIGH	Roma 双门硬顶外廓。	READY
140099	140099	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-SUV-01	HIGH	第五代 Hybrid AWD 外廓。	READY
140119	140119	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代 9YA 外廓。	READY
140120	140120	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代 9YA 外廓。	READY
140123	140123	Convertible	Plus Four I		2	EU-MORGAN-PLUS-FOUR-I-CONVERTIBLE-01	HIGH	Plus Four 双门敞篷外廓。	READY
140124	140124	Convertible	Plus Six I		2	EU-MORGAN-PLUS-SIX-I-CONVERTIBLE-01	HIGH	Plus Six 双门敞篷外廓。	READY
140308	140308	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH	TL 代 SUV 外廓。	READY
140328	140328	MPV	Porter II			EU-PIAGGIO-PORTER-II-BUS-01	HIGH	Bus 乘用外廓。	READY
140357	140357	Sedan	ES VII	XZ10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH	XZ10 四门外廓。	READY
140360	140360	Coupe	LC I	Z100	2	EU-LEXUS-LC-I-Z100-COUPE-01	HIGH	Z100 双门外廓。	READY
140365	140365	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50 四门外廓。	READY
140366	140366	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140367	140367	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140369	140369	SUV	UX I	ZA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH	ZA10 SUV 外廓。	READY
140375	140375	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140376	140376	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140377	140377	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门外廓。	READY
140378	140378	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 外廓。	READY
140379	140379	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 外廓。	READY
140380	140380	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 外廓。	READY
140386	140386	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH	B8 改款五门外廓。	READY
140387	140387	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH	B8 改款五门外廓。	READY
140388	140388	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	第二代前驱外廓。	READY
140389	140389	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	L8 改款四门外廓。	READY
140390	140390	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	L8 改款四门外廓。	READY
140391	140391	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代 MCV 外廓。	READY
140392	140392	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代 MCV 外廓。	READY
140393	140393	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH	4A5 Avant 外廓。	READY
140394	140394	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	4A2 四门外廓。	READY
140402	140402	SUV	Renegade I Facelift		5	EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	HIGH	改款 AWD 外廓。	READY
140404	140404	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	第五代五门外廓。	READY
140405	140405	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH	输入 Schrägheck 按车型资料归一为 SUV。	READY
140419	140419	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	LY 改款 SUV 外廓。	READY
140420	140420	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	LY 改款 SUV 外廓。	READY
140436	140436	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 SUV 外廓。	READY
140437	140437	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	S213 改款前旅行车外廓。	READY
140438	140438	Wagon	C-Class W205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205 改款旅行车外廓。	READY
140439	140439	Wagon	C-Class W205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205 改款旅行车外廓。	READY
140440	140440	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	HIGH	M440i xDrive 专属外廓。	READY
140442	140442	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22 后驱 Coupé 外廓。	READY
140443	140443	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22 后驱 Coupé 外廓。	READY
140445	140445	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22 后驱 Coupé 外廓。	READY
140446	140446	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22 后驱 Coupé 外廓。	READY
140448	140448	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive Coupé 外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PORSCHE-911-992-TURBO-S-COUPE-01	4535	1900	1303	Porsche Newsroom U.S. 2021 911 Turbo S technical specifications	https://newsroom.porsche.com/dam/jcr%3A887d7189-958d-4946-a189-e170e87b13e7/U.S.%20Technical%20Specifications%202021%20911%20Turbo%20S%20Coupe%20and%20Cabriolet.pdf
EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	4535	1900	1301	Porsche Newsroom U.S. 2021 911 Turbo S technical specifications	https://newsroom.porsche.com/dam/jcr%3A887d7189-958d-4946-a189-e170e87b13e7/U.S.%20Technical%20Specifications%202021%20911%20Turbo%20S%20Coupe%20and%20Cabriolet.pdf
EU-FERRARI-ROMA-I-COUPE-01	4656	1974	1301	Ferrari official Ferrari Roma specifications	https://www.ferrari.com/de-DE/auto/ferrari-roma
EU-TOYOTA-RAV4-V-SUV-01	4600	1855	1685	Toyota UK Media The New Toyota RAV4	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-MORGAN-PLUS-FOUR-I-CONVERTIBLE-01	3830	1650	1250	Morgan Motor Company Plus Four technical specification	https://morgan-motor.com/models/plus/plus-four/
EU-MORGAN-PLUS-SIX-I-CONVERTIBLE-01	3890	1756	1220	Morgan Motor Company Plus Six technical specification	https://morgan-motor.com/models/past-models/plus-six/
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
```

## 下一步优先处理

1. 闭合 Sprinter、Master、Vito、Proace 的轴距、车顶和乘用/货运分支。
2. 处理 Defender Van 与 Berlingo 混合车身字段的具体外廓边界。
3. 批量核对 Bentley Continental GT、McLaren、Xpeng、e.GO、Ligier、Microcar 等尚无缓存车型。
4. 消除 Seat Leon 不同悬架高度、Lexus RX 代际、Alpina B3 Sedan、BMW 430i xDrive 等剩余映射歧义。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 **12 个**原 PENDING Ktype，新增 **17 条** READY 映射；其中 5 个 SEAT Leon Ktype 按标准悬架与 FR 低悬架外廓拆分。
* 新建并闭合 Hyundai Elantra VII CN7、XPENG P7 I、Suzuki SX4 S-Cross II Facelift、Honda Jazz IV 四个尺寸组。
* Ktype 资料确认 Elantra 为 CN7、Suzuki 为 JY、BMW 430i xDrive 为 G22；Honda 140441 同时覆盖 GR3/GR6，但两者未形成不同外廓，因此不创建重复尺寸组。([AIC 德国汽车零部件][1])
* 四个新尺寸组分别由 Hyundai 2020 官方规格、XPENG 2020 官方配置、Honda 官方新闻资料和 Auto-Data 车型规格闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：74
* READY 映射行：79
* PENDING 输入 Ktype：26
* 已确认且被当前批次引用的尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139857	139857	Sedan	Elantra VII	CN7	4	EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	HIGH	CN7四门轿车外廓。	READY
140109_standard	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	MEDIUM	标准悬架五门外廓。	READY
140109_fr	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	MEDIUM	FR低悬架五门外廓。	READY
140121_standard	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140121_fr	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
140122_standard	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140122_fr	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
140398	140398	Sedan	P7 I		4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代后驱四门外廓。	READY
140399	140399	Sedan	P7 I		4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代四驱四门外廓。	READY
140414	140414	SUV	SX4 S-Cross II Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	HIGH	ALLGRIP五门SUV外廓。	READY
140416	140416	SUV	SX4 S-Cross II Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	HIGH	前驱五门SUV外廓。	READY
140441	140441	Hatchback	Jazz IV		5	EU-HONDA-JAZZ-IV-GR-HATCHBACK-01	HIGH	GR3与GR6共用五门外廓。	READY
140444	140444	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive双门外廓。	READY
140449_standard	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	MEDIUM	标准悬架五门外廓。	READY
140449_fr	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	MEDIUM	FR低悬架五门外廓。	READY
140450_standard	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140450_fr	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	4675	1825	1430	Hyundai Motor Company 2020 Elantra official e-brochure	https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/brochure/product/elantra-2020/elantra-2020_ebrochure.pdf
EU-XPENG-P7-I-SEDAN-01	4880	1896	1450	XPENG official 2020 P7 specification	https://www.xiaopeng.com/content/3489.html
EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	4300	1785	1580	Auto-Data Suzuki SX4 S-Cross II Facelift 1.4 Mild Hybrid	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-facelift-2016-1.4-boosterjet-129hp-mild-hybrid-45126
EU-HONDA-JAZZ-IV-GR-HATCHBACK-01	4044	1694	1526	Honda Europe 2020 Jazz official press kit	https://hondanews.eu/eu/en/cars/media/pressreleases/303367/2020-honda-jazz-and-jazz-crosstar-1
```

## 下一步优先处理

优先闭合 Sprinter、Master、Vito、Proace 的轴距和车顶分支；随后处理 Defender Van、McLaren、e.GO、Ligier、Microcar 及 Bentley Continental GT 等剩余新外廓。

推进信号：CONTINUE

[1]: https://www.aic-germany.de/en/product-catalogue/7665?utm_source=chatgpt.com "Product catalogue from AIC Germany"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Bentley Continental GT V8、McLaren Speedtail、Lexus RX III、e.GO Life、Alpina B3 G20、Jeep Compass 4xe 等单一外廓映射。相关尺寸均采用不含后视镜宽度口径。([Auto Express][1])
* Toyota Proace 4×4 Bus 按 Medium、Long 两种长度派生，直接复用已有 `MPY4` 尺寸组，不重复输出尺寸来源。
* Ligier JS50 的输入未限定标准车身或 Long 车身，两个 Ktype 均拆为 `standard`、`long`；两种外廓分别为 2850 mm 和 3000 mm 长。([汽车数据网][2])
* Microcar M.Go 两个 Ktype 仅为不同发动机排量，复用同一外廓尺寸组。([Alkatreszek][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：86
* READY 映射行：94
* PENDING 输入 Ktype：14
* 已确认且被当前批次引用的尺寸组：60
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139830	139830	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-V8-COUPE-01	HIGH	第三代V8双门硬顶外廓。	READY
140074	140074	Coupe	Speedtail		2	EU-MCLAREN-SPEEDTAIL-COUPE-01	HIGH	Speedtail三座双门外廓。	READY
140361	140361	SUV	RX III	GYL10	5	EU-LEXUS-RX-III-AL10-SUV-01	HIGH	前驱混合动力外廓。	READY
140362	140362	SUV	RX III	GYL15	5	EU-LEXUS-RX-III-AL10-SUV-01	HIGH	四驱混合动力外廓。	READY
140382	140382	Hatchback	Life I		3	EU-EGO-LIFE-I-HATCHBACK-01	HIGH	Life 60三门外廓。	READY
140383_medium	140383	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	HIGH	Medium四驱乘用车身。	READY
140383_long	140383	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	HIGH	Long四驱乘用车身。	READY
140384	140384	Sedan	B3 G20	G20	4	EU-ALPINA-B3-G20-SEDAN-PREFL-01	HIGH	G20改款前四门外廓。	READY
140403	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-PREFL-4XE-SUV-01	HIGH	MP改款前4xe外廓。	READY
140426_standard	140426	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	MEDIUM	输入未限定标准或Long车身；标准外廓。	READY
140426_long	140426	Hatchback	JS50 I Facelift Long		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	MEDIUM	输入未限定标准或Long车身；Long外廓。	READY
140427_standard	140427	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	MEDIUM	输入未限定标准或Long车身；标准外廓。	READY
140427_long	140427	Hatchback	JS50 I Facelift Long		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	MEDIUM	输入未限定标准或Long车身；Long外廓。	READY
140428	140428	Hatchback	M.Go		2	EU-MICROCAR-MGO-HATCHBACK-01	HIGH	498cc发动机不改变外廓。	READY
140429	140429	Hatchback	M.Go		2	EU-MICROCAR-MGO-HATCHBACK-01	HIGH	480cc发动机不改变外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-CONTINENTAL-GT-III-V8-COUPE-01	4850	1966	1405	Auto Express Bentley Continental GT V8 specifications	https://www.autoexpress.co.uk/bentley/continental-gt/prices-specs/95310/4.0-v8-mulliner-edition-2dr-auto
EU-MCLAREN-SPEEDTAIL-COUPE-01	5137	2000	1120	Auto-Data McLaren Speedtail specification	https://www.auto-data.net/en/mclaren-speedtail-4.0-v8-1070hp-plug-in-hybrid-48991
EU-LEXUS-RX-III-AL10-SUV-01	4770	1885	1685	Automobile-Catalog 2010 Lexus RX 450h FWD; Automobile-Catalog 2010 Lexus RX 450h SE-L	https://www.automobile-catalog.com/car/2010/1429025/lexus_rx_450h_fwd.html;https://www.automobile-catalog.com/car/2010/1429085/lexus_rx_450h_se-l.html
EU-EGO-LIFE-I-HATCHBACK-01	3348	1700	1567	Auto-Data e.GO Life 60 specification	https://www.auto-data.net/en/e.go-life-life-60-23.9-kwh-82hp-electric-33900
EU-ALPINA-B3-G20-SEDAN-PREFL-01	4719	1827	1440	Automobile-Catalog 2020 BMW Alpina B3 Limousine Allrad	https://www.automobile-catalog.com/car/2020/2980565/alpina_b3_limousine_allrad.html
EU-JEEP-COMPASS-II-MP-PREFL-4XE-SUV-01	4394	1819	1649	Auto-Data Jeep Compass II MP 4xe specification	https://www.auto-data.net/en/jeep-compass-ii-mp-1.3-240hp-plug-in-hybrid-4xe-automatic-41516
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	2850	1500	1466	Auto-Data Ligier JS50 I Facelift DCI specification	https://www.auto-data.net/en/ligier-js50-i-facelift-2017-0.5-dci-8hp-cvt-54653
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	3000	1500	1466	Auto-Data Ligier JS50 I Facelift Long DCI specification	https://www.auto-data.net/en/ligier-js50-i-facelift-2017-long-0.5-dci-8hp-cvt-54651
EU-MICROCAR-MGO-HATCHBACK-01	2999	1500	1560	AutoCentrum Microcar M.Go 0.5 Diesel technical data	https://www.autocentrum.pl/dane-techniczne/microcar/mgo/hatchback/silnik-diesla-0.5-8km-od-2020/
```

## 下一步优先处理

优先闭合剩余 14 个 Ktype：Sprinter Tourer/eSprinter/Chassis、Defender Van 90/110 分支、Berlingo 混合车身、McLaren 765LT、Master Bus，以及 Vito Tourer/Mixto 的 Compact/Long/Extra-long 分支。

推进信号：CONTINUE

[1]: https://www.autoexpress.co.uk/bentley/continental-gt/prices-specs/95310/4.0-v8-mulliner-edition-2dr-auto?utm_source=chatgpt.com "Bentley Continental GT Coupe 4.0 V8 Mulliner Edition 2dr Auto | Auto Express"
[2]: https://www.auto-data.net/en/ligier-js50-i-facelift-2017-long-0.5-dci-8hp-cvt-54651 "Ligier JS50 I (facelift 2017) Long 0.5 DCI (8 Hp) CVT | Technical specs, data, fuel consumption, Dimensions"
[3]: https://alkatreszek.hu/termekek/auto_felfuggesztes_kormanyzas/szervo_olaj_tartaly/microcar/mgo?utm_source=chatgpt.com "Vásároljon MICROCAR autóalkatrészeket - Kovács"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 7 个原 PENDING Ktype，新增 15 条 READY 映射。
* Vito Tourer 与 Mixto 的 4 个 Ktype 均覆盖 `447.701`、`447.703`、`447.705`，按 L1、L2、L3 三种车长派生，并按相同物理外廓复用三组尺寸。官方尺寸资料分别支持 4895、5140、5370 mm 车长及 1928 mm 不含后视镜宽度。
* eSprinter 312 已确定为 `910.633` 的 L2H2 前驱厢式车；McLaren 765LT 使用 4600 mm 精确车长、1159 mm 高度，并由 McLaren 技术资料确认 76 英寸不含后视镜宽度，换算为 1930 mm。([Meyer Motoren][1])
* Berlingo Ktype `139939` 确认为 B9 Box Body/MPV 合并车型标识；因本次确认的 4380×1810×1801 mm 与已有尺寸组不同，按规则新建独立尺寸组，不覆盖累计事实。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：93
* READY 映射行：109
* PENDING 输入 Ktype：7
* 已确认且被当前批次引用的尺寸组：66
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139939	139939	Van	Berlingo II Phase III	B9		EU-CITROEN-BERLINGO-II-B9-BOX-MPV-01	MEDIUM	TecDoc为Box Body/MPV合并车身标识。	READY
140071	140071	Coupe	765LT		2	EU-MCLAREN-765LT-COUPE-01	HIGH	765LT Coupé外廓。	READY
140321	140321	Van	eSprinter I	910.633		EU-MERCEDES-BENZ-ESPRINTER-I-910-L2H2-VAN-01	HIGH	L2H2前驱电动厢式外廓。	READY
140406_l1	140406	MPV	Vito W447 Facelift	447.701	5	EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact乘用外廓。	READY
140406_l2	140406	MPV	Vito W447 Facelift	447.703	5	EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long乘用外廓。	READY
140406_l3	140406	MPV	Vito W447 Facelift	447.705	5	EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long乘用外廓。	READY
140408_l1	140408	MPV	Vito W447 Facelift	447.701	5	EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact乘用外廓。	READY
140408_l2	140408	MPV	Vito W447 Facelift	447.703	5	EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long乘用外廓。	READY
140408_l3	140408	MPV	Vito W447 Facelift	447.705	5	EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long乘用外廓。	READY
140412_l1	140412	Van	Vito W447 Facelift	447.701		EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact Mixto外廓。	READY
140412_l2	140412	Van	Vito W447 Facelift	447.703		EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long Mixto外廓。	READY
140412_l3	140412	Van	Vito W447 Facelift	447.705		EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long Mixto外廓。	READY
140413_l1	140413	Van	Vito W447 Facelift	447.701		EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact Mixto外廓。	READY
140413_l2	140413	Van	Vito W447 Facelift	447.703		EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long Mixto外廓。	READY
140413_l3	140413	Van	Vito W447 Facelift	447.705		EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long Mixto外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-BERLINGO-II-B9-BOX-MPV-01	4380	1810	1801	Automobile-Catalog 2018 Citroen Berlingo Multispace PureTech 110	https://www.automobile-catalog.com/car/2018/2560235/citroen_berlingo_multispace_puretech_110.html
EU-MCLAREN-765LT-COUPE-01	4600	1930	1159	McLaren 765LT Features and Options Guide; McLaren Automotive 765LT technical specification	https://dealer18342.dealeron.com/static/dealer-18342/Brochures/McLaren_765LT_Features_and_Options_Guide_Version_3_EN.pdf;https://cars.mclaren.press/assets/documents/original/12697-LightermorepowerfulevenmoreengaginganduniquelyMcLarenthenew765LTUS.pdf
EU-MERCEDES-BENZ-ESPRINTER-I-910-L2H2-VAN-01	5932	2020	2687	Mercedes-Benz eSprinter Panel Van price list, March 2021	https://bluesky-cogcms.cdn.imgeng.in/media/kcvoxrcl/mb-esprinter-electric-mar21.pdf
EU-MERCEDES-BENZ-VITO-W447-L1-01	4895	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-L2-01	5140	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-L3-01	5370	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
```

## 下一步优先处理

1. 按 `907.741/907.743/907.745` 闭合 Sprinter Tourer 的车长与车顶派生。
2. 按 Defender 90/110 Hard Top 闭合 Ktype `139927`—`139930`。
3. 闭合 Renault Master Bus 的 L/H 分支及 Sprinter `910.141/910.143` 底盘车分支。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/140321/mercedes-benz/sprinter_3_5t_kasten_b907_b910_/esprinter_312_910_633_140321 "eSprinter 312 (910.633) | Sprinter 3,5t Kasten (B907, B910) | Mercedes-Benz | Manufacturers | Meyer Motoren"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Ktype `140210`。`JV04` 对应 Renault Master III Bus 2.3 dCi 180 FWD；其 L3H2 改款车身外廓与已有尺寸组 `EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01` 一致，因此直接复用，不重复输出尺寸组。官方资料确认该外廓为 6225 × 2070 × 2488 mm，宽度不含后视镜。([autodoc24.fr][1])
* 其余 6 个 Ktype 仍涉及 Sprinter 多长度/车顶组合及 Defender 90/110 外廓分支，本轮未创建猜测性映射。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：94
* READY 映射行：110
* PENDING 输入 Ktype：6
* 已确认且被当前批次引用的尺寸组：67
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140210	140210	MPV	Master III Phase III	JV04	5	EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	HIGH	L3H2前驱客运车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Sprinter Tourer `139926` 的 `907.741/907.743/907.745` 长度与车顶分支。
2. 闭合 Sprinter Chassis `140395` 的 `910.141/910.143` 分支。
3. 确认 Defender Van `139927`—`139930` 对 90/110 Hard Top 及悬架高度分支的覆盖关系。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/track-rod-end-10703/renault/master/master-iii-bus-jv/140210-2-3-dci-180-fwd-jv04 "Track rod end Renault Master III Minibus 2.3 dCi FWD 179 hp Diesel 132 kW 2020 - 2026 M9T 716"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Defender Van Ktype `139927`—`139930`。四个 Ktype 均覆盖 Defender 90 与 Defender 110，按 90 螺旋弹簧、90 空气悬架、110 三种物理外廓拆分。([AUTODOC][1])
* 采用 Land Rover 2020 官方技术规格：90 车身宽度（不含后视镜）为 1996 mm，车长含原厂外挂备胎为 4583 mm，高度分别为 1974/1969 mm；110 为 5018 × 1996 × 1967 mm。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：98
* READY 映射行：122
* PENDING 输入 Ktype：2
* 已确认且被当前批次引用的尺寸组：70
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139927_90_coil	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139927_90_air	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139927_110	139927	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139928_90_coil	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139928_90_air	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139928_110	139928	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139929_90_coil	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139929_90_air	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139929_110	139929	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139930_90_coil	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139930_90_air	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139930_110	139930	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	4583	1996	1974	Jaguar Land Rover 2020 Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	4583	1996	1969	Jaguar Land Rover 2020 Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	5018	1996	1967	Jaguar Land Rover 2020 Defender 110 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
```

## 下一步优先处理

1. 闭合 Sprinter Tourer Ktype `139926` 的 `907.741`、`907.743`、`907.745` 长度及车顶分支。
2. 闭合 Sprinter Chassis Ktype `140395` 的 `910.141`、`910.143` 前驱单排底盘分支。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/tie-rod-74815/land-rover/defender/defender-van-l663/139929-2-0-d200-sd4-4x4?utm_source=chatgpt.com "LAND ROVER Defender Van (L663) 2.0 D200 SD4 4x4 Tie rod"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4901-5000_ktype_dimension_mapping_final.tsv
- all_4901-5000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后两个 PENDING Ktype 已闭合：`139926` 拆分为 Sprinter Tourer L1/L2/L3 × 标准顶/高顶六个物理分支；`140395` 拆分为 `910.141` L1 与 `910.143` L2 两个前驱单排底盘分支。
* Mercedes-Benz Tourer 技术图给出 5267、5932、6967 mm 三种车长以及 2360、2633 mm 两种高度；Sprinter 底盘资料确认 L2 FWD 为 5986 × 2020 × 2292 mm，车身代码资料分别将 `910.141`、`910.143` 对应到 3259、3924 mm 轴距。
* 已完成固定表头、唯一键、引用闭合、正整数三维、来源非空及下载文件检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：130
* PENDING：0
* 当前批次引用尺寸组：78
* `id` 重复：0
* `DIMENSION_GROUP_ID` 重复定义：0
* 缺失映射引用：0
* 孤立尺寸组：0
* 机械校验：PASS

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139800	139800	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139801	139801	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139802	139802	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country外廓。	READY
139813	139813	Coupe	911 992	992	2	EU-PORSCHE-911-992-TURBO-S-COUPE-01	HIGH	Turbo S Coupé标准PASM外廓。	READY
139814	139814	Convertible	911 992	992	2	EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	HIGH	Turbo S Cabriolet标准PASM外廓。	READY
139824	139824	SUV	EcoSport II		5	EU-FORD-ECOSPORT-II-SUV-01	HIGH	第二代SUV外廓。	READY
139829	139829	Convertible	Continental GTC III		2	EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	HIGH	第三代GTC外廓。	READY
139830	139830	Coupe	Continental GT III		2	EU-BENTLEY-CONTINENTAL-GT-III-V8-COUPE-01	HIGH	第三代V8双门硬顶外廓。	READY
139834	139834	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门外廓。	READY
139857	139857	Sedan	Elantra VII	CN7	4	EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	HIGH	CN7四门轿车外廓。	READY
139880	139880	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	标准旅行车外廓。	READY
139881	139881	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代SUV外廓。	READY
139908	139908	MPV	Berlingo II Phase III	B9	5	EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	HIGH	B9乘用MPV外廓。	READY
139926_l1h1	139926	MPV	Sprinter III	907.741		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	HIGH	907.741 L1标准顶客运车身。	READY
139926_l1h2	139926	MPV	Sprinter III	907.741		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H2-01	HIGH	907.741 L1高顶客运车身。	READY
139926_l2h1	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	HIGH	907.743 L2标准顶客运车身。	READY
139926_l2h2	139926	MPV	Sprinter III	907.743		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	HIGH	907.743 L2高顶客运车身。	READY
139926_l3h1	139926	MPV	Sprinter III	907.745		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H1-01	HIGH	907.745 L3标准顶客运车身。	READY
139926_l3h2	139926	MPV	Sprinter III	907.745		EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	HIGH	907.745 L3高顶客运车身。	READY
139927_90_coil	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139927_90_air	139927	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139927_110	139927	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139928_90_coil	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139928_90_air	139928	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139928_110	139928	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139929_90_coil	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139929_90_air	139929	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139929_110	139929	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139930_90_coil	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	HIGH	90三门车身，螺旋弹簧悬架。	READY
139930_90_air	139930	Van	Defender L663	L663	3	EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	HIGH	90三门车身，空气悬架。	READY
139930_110	139930	Van	Defender L663	L663	5	EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	HIGH	110五门车身。	READY
139939	139939	Van	Berlingo II Phase III	B9		EU-CITROEN-BERLINGO-II-B9-BOX-MPV-01	MEDIUM	TecDoc为Box Body/MPV合并车身标识。	READY
140003	140003	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	第八代五门外廓。	READY
140004	140004	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-01	HIGH	第八代五门外廓。	READY
140024	140024	Sedan	3 Series G20	G20	4	EU-BMW-3-G20-SEDAN-RWD-PREFL-01	HIGH	G20后驱改款前外廓。	READY
140030	140030	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140031	140031	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer外廓。	READY
140066	140066	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	欧洲宽体外廓。	READY
140067	140067	Hatchback	Ignis III	MF	5	EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	HIGH	欧洲宽体外廓。	READY
140071	140071	Coupe	765LT		2	EU-MCLAREN-765LT-COUPE-01	HIGH	765LT Coupé外廓。	READY
140074	140074	Coupe	Speedtail		2	EU-MCLAREN-SPEEDTAIL-COUPE-01	HIGH	Speedtail三座双门外廓。	READY
140095	140095	Coupe	Roma I		2	EU-FERRARI-ROMA-I-COUPE-01	HIGH	Roma双门硬顶外廓。	READY
140099	140099	SUV	RAV4 V	XA50	5	EU-TOYOTA-RAV4-V-SUV-01	HIGH	第五代Hybrid AWD外廓。	READY
140109_standard	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	MEDIUM	标准悬架五门外廓。	READY
140109_fr	140109	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	MEDIUM	FR低悬架五门外廓。	READY
140119	140119	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA外廓。	READY
140120	140120	SUV	Cayenne III	9YA	5	EU-PORSCHE-CAYENNE-III-9YA-SUV-01	HIGH	第三代9YA外廓。	READY
140121_standard	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140121_fr	140121	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
140122_standard	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140122_fr	140122	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
140123	140123	Convertible	Plus Four I		2	EU-MORGAN-PLUS-FOUR-I-CONVERTIBLE-01	HIGH	Plus Four双门敞篷外廓。	READY
140124	140124	Convertible	Plus Six I		2	EU-MORGAN-PLUS-SIX-I-CONVERTIBLE-01	HIGH	Plus Six双门敞篷外廓。	READY
140210	140210	MPV	Master III Phase III	JV04	5	EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	HIGH	L3H2前驱客运车身。	READY
140308	140308	SUV	Tucson III	TL	5	EU-HYUNDAI-TUCSON-III-TL-SUV-01	HIGH	TL代SUV外廓。	READY
140321	140321	Van	eSprinter I	910.633		EU-MERCEDES-BENZ-ESPRINTER-I-910-L2H2-VAN-01	HIGH	L2H2前驱电动厢式外廓。	READY
140328	140328	MPV	Porter II			EU-PIAGGIO-PORTER-II-BUS-01	HIGH	Bus乘用外廓。	READY
140357	140357	Sedan	ES VII	XZ10	4	EU-LEXUS-ES-VII-XZ10-SEDAN-01	HIGH	XZ10四门外廓。	READY
140360	140360	Coupe	LC I	Z100	2	EU-LEXUS-LC-I-Z100-COUPE-01	HIGH	Z100双门外廓。	READY
140361	140361	SUV	RX III	GYL10	5	EU-LEXUS-RX-III-AL10-SUV-01	HIGH	前驱混合动力外廓。	READY
140362	140362	SUV	RX III	GYL15	5	EU-LEXUS-RX-III-AL10-SUV-01	HIGH	四驱混合动力外廓。	READY
140365	140365	Sedan	LS V	XF50	4	EU-LEXUS-LS-V-XF50-SEDAN-01	HIGH	XF50四门外廓。	READY
140366	140366	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140367	140367	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140369	140369	SUV	UX I	ZA10	5	EU-LEXUS-UX-I-ZA10-SUV-01	HIGH	ZA10 SUV外廓。	READY
140375	140375	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140376	140376	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140377	140377	Hatchback	Insignia B Grand Sport		5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门外廓。	READY
140378	140378	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer外廓。	READY
140379	140379	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer外廓。	READY
140380	140380	Wagon	Insignia B Sports Tourer		5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer外廓。	READY
140382	140382	Hatchback	Life I		3	EU-EGO-LIFE-I-HATCHBACK-01	HIGH	Life 60三门外廓。	READY
140383_medium	140383	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	HIGH	Medium四驱乘用车身。	READY
140383_long	140383	MPV	Proace Verso II	MPY4	5	EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	HIGH	Long四驱乘用车身。	READY
140384	140384	Sedan	B3 G20	G20	4	EU-ALPINA-B3-G20-SEDAN-PREFL-01	HIGH	G20改款前四门外廓。	READY
140386	140386	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH	B8改款五门外廓。	READY
140387	140387	Hatchback	Sandero II	B8	5	EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	HIGH	B8改款五门外廓。	READY
140388	140388	SUV	Duster II		5	EU-DACIA-DUSTER-II-SUV-4X2-01	HIGH	第二代前驱外廓。	READY
140389	140389	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	L8改款四门外廓。	READY
140390	140390	Sedan	Logan II	L8	4	EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	HIGH	L8改款四门外廓。	READY
140391	140391	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代MCV外廓。	READY
140392	140392	Wagon	Logan II MCV		5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代MCV外廓。	READY
140393	140393	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-AVANT-01	HIGH	4A5 Avant外廓。	READY
140394	140394	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	4A2四门外廓。	READY
140395_l1	140395	Pickup	Sprinter III	910.141	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SCAB-L1-FWD-01	HIGH	910.141 L1前驱单排底盘。	READY
140395_l2	140395	Pickup	Sprinter III	910.143	2	EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SCAB-L2-FWD-01	HIGH	910.143 L2前驱单排底盘。	READY
140398	140398	Sedan	P7 I		4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代后驱四门外廓。	READY
140399	140399	Sedan	P7 I		4	EU-XPENG-P7-I-SEDAN-01	HIGH	初代四驱四门外廓。	READY
140402	140402	SUV	Renegade I Facelift		5	EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	HIGH	改款AWD外廓。	READY
140403	140403	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-PREFL-4XE-SUV-01	HIGH	MP改款前4xe外廓。	READY
140404	140404	Hatchback	Clio V		5	EU-RENAULT-CLIO-V-HATCHBACK-01	HIGH	第五代五门外廓。	READY
140405	140405	SUV	Captur II	HJB	5	EU-RENAULT-CAPTUR-II-HJB-SUV-01	HIGH	输入Schrägheck按车型资料归一为SUV。	READY
140406_l1	140406	MPV	Vito W447 Facelift	447.701	5	EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact乘用外廓。	READY
140406_l2	140406	MPV	Vito W447 Facelift	447.703	5	EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long乘用外廓。	READY
140406_l3	140406	MPV	Vito W447 Facelift	447.705	5	EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long乘用外廓。	READY
140408_l1	140408	MPV	Vito W447 Facelift	447.701	5	EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact乘用外廓。	READY
140408_l2	140408	MPV	Vito W447 Facelift	447.703	5	EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long乘用外廓。	READY
140408_l3	140408	MPV	Vito W447 Facelift	447.705	5	EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long乘用外廓。	READY
140412_l1	140412	Van	Vito W447 Facelift	447.701		EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact Mixto外廓。	READY
140412_l2	140412	Van	Vito W447 Facelift	447.703		EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long Mixto外廓。	READY
140412_l3	140412	Van	Vito W447 Facelift	447.705		EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long Mixto外廓。	READY
140413_l1	140413	Van	Vito W447 Facelift	447.701		EU-MERCEDES-BENZ-VITO-W447-L1-01	HIGH	L1/Compact Mixto外廓。	READY
140413_l2	140413	Van	Vito W447 Facelift	447.703		EU-MERCEDES-BENZ-VITO-W447-L2-01	HIGH	L2/Long Mixto外廓。	READY
140413_l3	140413	Van	Vito W447 Facelift	447.705		EU-MERCEDES-BENZ-VITO-W447-L3-01	HIGH	L3/Extra-long Mixto外廓。	READY
140414	140414	SUV	SX4 S-Cross II Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	HIGH	ALLGRIP五门SUV外廓。	READY
140416	140416	SUV	SX4 S-Cross II Facelift	JY	5	EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	HIGH	前驱五门SUV外廓。	READY
140419	140419	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	LY改款SUV外廓。	READY
140420	140420	SUV	Vitara IV	LY	5	EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	HIGH	LY改款SUV外廓。	READY
140426_standard	140426	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	MEDIUM	输入未限定标准或Long车身；标准外廓。	READY
140426_long	140426	Hatchback	JS50 I Facelift Long		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	MEDIUM	输入未限定标准或Long车身；Long外廓。	READY
140427_standard	140427	Hatchback	JS50 I Facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	MEDIUM	输入未限定标准或Long车身；标准外廓。	READY
140427_long	140427	Hatchback	JS50 I Facelift Long		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	MEDIUM	输入未限定标准或Long车身；Long外廓。	READY
140428	140428	Hatchback	M.Go		2	EU-MICROCAR-MGO-HATCHBACK-01	HIGH	498cc发动机不改变外廓。	READY
140429	140429	Hatchback	M.Go		2	EU-MICROCAR-MGO-HATCHBACK-01	HIGH	480cc发动机不改变外廓。	READY
140436	140436	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	HIGH	V167 SUV外廓。	READY
140437	140437	Wagon	E-Class W213	S213	5	EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	HIGH	S213改款前旅行车外廓。	READY
140438	140438	Wagon	C-Class W205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款旅行车外廓。	READY
140439	140439	Wagon	C-Class W205	S205	5	EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	HIGH	S205改款旅行车外廓。	READY
140440	140440	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	HIGH	M440i xDrive专属外廓。	READY
140441	140441	Hatchback	Jazz IV		5	EU-HONDA-JAZZ-IV-GR-HATCHBACK-01	HIGH	GR3与GR6共用五门外廓。	READY
140442	140442	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22后驱Coupé外廓。	READY
140443	140443	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22后驱Coupé外廓。	READY
140444	140444	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive双门外廓。	READY
140445	140445	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22后驱Coupé外廓。	READY
140446	140446	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-RWD-01	HIGH	G22后驱Coupé外廓。	READY
140448	140448	Coupe	4 Series G22	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	G22 xDrive Coupé外廓。	READY
140449_standard	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	MEDIUM	标准悬架五门外廓。	READY
140449_fr	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	MEDIUM	FR低悬架五门外廓。	READY
140450_standard	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	MEDIUM	标准悬架旅行车外廓。	READY
140450_fr	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	MEDIUM	FR低悬架旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4901-5000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-PORSCHE-911-992-TURBO-S-COUPE-01	4535	1900	1303	Porsche Newsroom U.S. 2021 911 Turbo S technical specifications	https://newsroom.porsche.com/dam/jcr%3A887d7189-958d-4946-a189-e170e87b13e7/U.S.%20Technical%20Specifications%202021%20911%20Turbo%20S%20Coupe%20and%20Cabriolet.pdf
EU-PORSCHE-911-992-TURBO-S-CABRIOLET-01	4535	1900	1301	Porsche Newsroom U.S. 2021 911 Turbo S technical specifications	https://newsroom.porsche.com/dam/jcr%3A887d7189-958d-4946-a189-e170e87b13e7/U.S.%20Technical%20Specifications%202021%20911%20Turbo%20S%20Coupe%20and%20Cabriolet.pdf
EU-FORD-ECOSPORT-II-SUV-01	4273	1765	1650	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-BENTLEY-CONTINENTAL-GTC-III-CONVERTIBLE-01	4850	1954	1399	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-BENTLEY-CONTINENTAL-GT-III-V8-COUPE-01	4850	1966	1405	Auto Express Bentley Continental GT V8 specifications	https://www.autoexpress.co.uk/bentley/continental-gt/prices-specs/95310/4.0-v8-mulliner-edition-2dr-auto
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-HYUNDAI-ELANTRA-VII-CN7-SEDAN-01	4675	1825	1430	Hyundai Motor Company 2020 Elantra official e-brochure	https://www.hyundai.com/content/dam/hyundai/template_en/en/data/marketing/brochure/product/elantra-2020/elantra-2020_ebrochure.pdf
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-CITROEN-BERLINGO-II-PHASE-III-MPV-01	4384	1810	1852	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H1-01	5267	2020	2360	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L1H2-01	5267	2020	2633	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H1-01	5932	2020	2360	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L2H2-01	5932	2020	2633	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H1-01	6967	2020	2360	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W907-TOURER-L3H2-01	6967	2020	2633	Mercedes-Benz New Sprinter 2018 Tourer technical data; Mercedes-Benz Sprinter Chassis Cab body-width diagram	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_new_sprinter_model_information_price_list2018_e.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-LAND-ROVER-DEFENDER-L663-90-VAN-COIL-01	4583	1996	1974	Jaguar Land Rover 2020 Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-90-VAN-AIR-01	4583	1996	1969	Jaguar Land Rover 2020 Defender 90 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-90.pdf
EU-LAND-ROVER-DEFENDER-L663-110-VAN-01	5018	1996	1967	Jaguar Land Rover 2020 Defender 110 official technical specifications	https://jlrnewsroom.media/wp-content/uploads/2019/09/20MY-Defender-Tech-Spec-110.pdf
EU-CITROEN-BERLINGO-II-B9-BOX-MPV-01	4380	1810	1801	Automobile-Catalog 2018 Citroen Berlingo Multispace PureTech 110	https://www.automobile-catalog.com/car/2018/2560235/citroen_berlingo_multispace_puretech_110.html
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-BMW-3-G20-SEDAN-RWD-PREFL-01	4709	1827	1435	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1514	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-SUZUKI-IGNIS-III-MF-HATCHBACK-WIDEBODY-01	3700	1690	1595	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MCLAREN-765LT-COUPE-01	4600	1930	1159	McLaren 765LT Features and Options Guide; McLaren Automotive 765LT technical specification	https://dealer18342.dealeron.com/static/dealer-18342/Brochures/McLaren_765LT_Features_and_Options_Guide_Version_3_EN.pdf;https://cars.mclaren.press/assets/documents/original/12697-LightermorepowerfulevenmoreengaginganduniquelyMcLarenthenew765LTUS.pdf
EU-MCLAREN-SPEEDTAIL-COUPE-01	5137	2000	1120	Auto-Data McLaren Speedtail specification	https://www.auto-data.net/en/mclaren-speedtail-4.0-v8-1070hp-plug-in-hybrid-48991
EU-FERRARI-ROMA-I-COUPE-01	4656	1974	1301	Ferrari official Ferrari Roma specifications	https://www.ferrari.com/de-DE/auto/ferrari-roma
EU-TOYOTA-RAV4-V-SUV-01	4600	1855	1685	Toyota UK Media The New Toyota RAV4	https://media.toyota.co.uk/the-new-toyota-rav4/
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1799	1442	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-PORSCHE-CAYENNE-III-9YA-SUV-01	4918	1983	1696	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MORGAN-PLUS-FOUR-I-CONVERTIBLE-01	3830	1650	1250	Morgan Motor Company Plus Four technical specification	https://morgan-motor.com/models/plus/plus-four/
EU-MORGAN-PLUS-SIX-I-CONVERTIBLE-01	3890	1756	1220	Morgan Motor Company Plus Six technical specification	https://morgan-motor.com/models/past-models/plus-six/
EU-RENAULT-MASTER-III-X62-ZE-VAN-L3H2-FACELIFT-01	6225	2070	2488	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-HYUNDAI-TUCSON-III-TL-SUV-01	4475	1850	1655	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-ESPRINTER-I-910-L2H2-VAN-01	5932	2020	2687	Mercedes-Benz eSprinter Panel Van price list, March 2021	https://bluesky-cogcms.cdn.imgeng.in/media/kcvoxrcl/mb-esprinter-electric-mar21.pdf
EU-PIAGGIO-PORTER-II-BUS-01	3400	1395	1870	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-LEXUS-ES-VII-XZ10-SEDAN-01	4975	1865	1445	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-LEXUS-LC-I-Z100-COUPE-01	4770	1920	1345	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-LEXUS-RX-III-AL10-SUV-01	4770	1885	1685	Automobile-Catalog 2010 Lexus RX 450h FWD; Automobile-Catalog 2010 Lexus RX 450h SE-L	https://www.automobile-catalog.com/car/2010/1429025/lexus_rx_450h_fwd.html;https://www.automobile-catalog.com/car/2010/1429085/lexus_rx_450h_se-l.html
EU-LEXUS-LS-V-XF50-SEDAN-01	5235	1900	1450	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-LEXUS-UX-I-ZA10-SUV-01	4495	1840	1540	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-EGO-LIFE-I-HATCHBACK-01	3348	1700	1567	Auto-Data e.GO Life 60 specification	https://www.auto-data.net/en/e.go-life-life-60-23.9-kwh-82hp-electric-33900
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-MEDIUM-4X4-01	4959	1920	1940	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-TOYOTA-PROACE-VERSO-II-MPY4-MPV-LONG-4X4-01	5309	1920	1950	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-ALPINA-B3-G20-SEDAN-PREFL-01	4719	1827	1440	Automobile-Catalog 2020 BMW Alpina B3 Limousine Allrad	https://www.automobile-catalog.com/car/2020/2980565/alpina_b3_limousine_allrad.html
EU-DACIA-SANDERO-II-B8-HATCHBACK-FACELIFT-01	4069	1733	1519	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-DACIA-DUSTER-II-SUV-4X2-01	4341	1804	1693	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-DACIA-LOGAN-II-L8-SEDAN-FACELIFT-01	4358	1733	1517	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1550	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-AUDI-A6-C8-4A5-AVANT-01	4939	1886	1467	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SCAB-L1-FWD-01	5321	2020	2292	Mercedes-Benz Sprinter BR 910 bodybuilder guideline; Mercedes-Benz Sprinter Chassis Cab dimensions	https://bb-portal.mercedes-benz-vans.com/api/katalog/v1.0/de/catalogs/ar2/vehicle-classes/40/downloads?filenames%5B%5D=_INT%2Fde%2FARL_Sprinter_BR_910_AeJ2025_1a_20250205_de_mS.pdf;https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-MERCEDES-BENZ-SPRINTER-III-W910-CHASSIS-SCAB-L2-FWD-01	5986	2020	2292	Mercedes-Benz Sprinter Chassis Cab dimensions	https://www.ciceley.com/wp-content/uploads/2023/07/sprinter-chassis-cab.pdf
EU-XPENG-P7-I-SEDAN-01	4880	1896	1450	XPENG official 2020 P7 specification	https://www.xiaopeng.com/content/3489.html
EU-JEEP-RENEGADE-I-FACELIFT-AWD-SUV-01	4236	1805	1684	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-JEEP-COMPASS-II-MP-PREFL-4XE-SUV-01	4394	1819	1649	Auto-Data Jeep Compass II MP 4xe specification	https://www.auto-data.net/en/jeep-compass-ii-mp-1.3-240hp-plug-in-hybrid-4xe-automatic-41516
EU-RENAULT-CLIO-V-HATCHBACK-01	4050	1798	1440	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-RENAULT-CAPTUR-II-HJB-SUV-01	4227	1797	1576	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-VITO-W447-L1-01	4895	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-L2-01	5140	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-MERCEDES-BENZ-VITO-W447-L3-01	5370	1928	1910	Mercedes-Benz Vito Tourer price list, June 2020	https://xr793.com/wp-content/uploads/2022/12/2020-Mercedes-Benz-Vito-Tourer-Price-List-UK.pdf
EU-SUZUKI-SX4-S-CROSS-II-FACELIFT-SUV-01	4300	1785	1580	Auto-Data Suzuki SX4 S-Cross II Facelift 1.4 Mild Hybrid	https://www.auto-data.net/en/suzuki-sx4-s-cross-ii-facelift-2016-1.4-boosterjet-129hp-mild-hybrid-45126
EU-SUZUKI-VITARA-IV-LY-SUV-FACELIFT-01	4175	1775	1610	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-STANDARD-01	2850	1500	1466	Auto-Data Ligier JS50 I Facelift DCI specification	https://www.auto-data.net/en/ligier-js50-i-facelift-2017-0.5-dci-8hp-cvt-54653
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-LONG-01	3000	1500	1466	Auto-Data Ligier JS50 I Facelift Long DCI specification	https://www.auto-data.net/en/ligier-js50-i-facelift-2017-long-0.5-dci-8hp-cvt-54651
EU-MICROCAR-MGO-HATCHBACK-01	2999	1500	1560	AutoCentrum Microcar M.Go 0.5 Diesel technical data	https://www.autocentrum.pl/dane-techniczne/microcar/mgo/hatchback/silnik-diesla-0.5-8km-od-2020/
EU-MERCEDES-BENZ-GLE-II-V167-SUV-01	4924	1947	1772	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-E-KLASSE-S213-WAGON-01	4933	1852	1475	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-MERCEDES-BENZ-C-KLASSE-S205-WAGON-FACELIFT-01	4702	1810	1457	任务提供的跨批次锁定尺寸组索引	sandbox:/mnt/data/all_4901-5000_cross_batch_dimension_index_source.txt
EU-BMW-4-G22-M440I-XDRIVE-COUPE-01	4770	1852	1393	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-HONDA-JAZZ-IV-GR-HATCHBACK-01	4044	1694	1526	Honda Europe 2020 Jazz official press kit	https://hondanews.eu/eu/en/cars/media/pressreleases/303367/2020-honda-jazz-and-jazz-crosstar-1
EU-BMW-4-G22-COUPE-RWD-01	4768	1852	1383	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group Press technical specifications, new BMW 4 Series Coupé	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4901-5000_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5166 行）
- 累计尺寸组：dimension_groups_final.tsv（1928 行）

