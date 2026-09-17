# 任务：all 第 101-200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0002__6decc774


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 101-200 行

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
all 第 101-200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Megane i kombi van	1.6	Kasten/Kombi	Frontantrieb	Benzin	79	107	Apr 2001	Jul 2003	2024-03-01	138754
Renault	Megane i kombi van	1.8	Kasten/Kombi	Frontantrieb	Benzin	85	116	Apr 2001	Jul 2003	2024-03-01	138755
Renault	Megane i kombi van	1.6 Bifuel	Kasten/Kombi	Frontantrieb	Benzin/Autogas (LPG)	80	109	Apr 2001	Jul 2003	2024-03-01	138757
Renault	Megane i kombi van	1.6 Bifuel	Kasten/Kombi	Frontantrieb	Benzin/Autogas (LPG)	79	107	Apr 2001	Jul 2003	2024-03-01	138758
Mercedes-benz	Glb	GLB 250	SUV	Frontantrieb	Benzin	165	224	Dec 2019	-	2024-03-01	138760
Mercedes-benz	Glb	GLB 220 D	SUV	Frontantrieb	Diesel	140	190	Dec 2019	-	2024-03-01	138761
Renault	Megane iii	1.6 16V Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	81	110	May 2009	Aug 2015	2024-03-01	138767
Renault	Master iii	2.3 DCI 180 FWD	Kasten	Frontantrieb	Diesel	132	179	Jul 2019	Dec 2024	2026-03-01	138771
Hyundai	I20 i	1.2	Schrägheck	Frontantrieb	Benzin	56	76	Dec 2008	Aug 2014	2024-03-01	138773
Dacia	Dokker	1.5 Blue DCI 95	Kasten/Großraumlimousine	Frontantrieb	Diesel	70	95	Jun 2019	Dec 2021	2024-11-01	138778
Audi	E-Tron	50 Quattro	SUV	Allrad	Elektro	230	313	Sep 2019	Jul 2023	2026-03-01	138779
Audi	E-Tron	50 Quattro	SUV	Allrad	Elektro	230	313	Sep 2019	Jul 2023	2026-03-01	138780
Nissan	Nv300	2.0 DCI 120	Kasten	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138783
Nissan	Nv300	2.0 DCI 145	Kasten	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138784
Nissan	Nv300	2.0 DCI 170	Kasten	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138785
Nissan	Nv300	2.0 DCI 170	Pritsche/Fahrgestell	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138786
Nissan	Nv300	2.0 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138787
Nissan	Nv300 kombi	2.0 DCI 145	Bus	Frontantrieb	Diesel	107	145	Jul 2019	-	2024-03-01	138788
Nissan	Nv300 kombi	2.0 DCI 120	Bus	Frontantrieb	Diesel	88	120	Jul 2019	-	2024-03-01	138789
Nissan	Nv300 kombi	2.0 DCI 170	Bus	Frontantrieb	Diesel	125	170	Jul 2019	-	2024-03-01	138790
Hyundai	Tucson	2.0 LPG Allrad	SUV	Allrad	Benzin/Autogas (LPG)	104	141	Jun 2009	Mar 2010	2024-03-01	138796
Hyundai	I20 i	1.4 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	75	102	Dec 2008	Dec 2012	2024-03-01	138797
Volvo	V60 ii	D4 Polestar AWD	Kombi	Allrad	Diesel	147	200	Feb 2018	Dec 2021	2024-05-01	138805
Dodge	Caliber	2.0 CRD	Schrägheck	Frontantrieb	Diesel	88	120	Jun 2006	Nov 2011	2024-03-01	138806
Volvo	V40	D4 Polestar	Schrägheck	Frontantrieb	Diesel	147	200	May 2014	Aug 2019	2024-03-01	138807
Volvo	V40 cross country	T5 Polestar AWD	Schrägheck	Allrad	Benzin	186	253	Jan 2015	Aug 2019	2024-03-01	138808
Volvo	V40	T5 Drive-e Polestar	Schrägheck	Frontantrieb	Benzin	186	253	May 2014	Aug 2019	2024-03-01	138809
Volvo	V60 i cross country	D4 Drive-e Polestar	Kombi	Frontantrieb	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138811
Volvo	V60 i cross country	D4 Polestar AWD	Kombi	Allrad	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138812
Volvo	V60 i cross country	T5 Drive-e Polestar	Kombi	Frontantrieb	Benzin	186	253	Mar 2015	Jul 2018	2024-03-01	138814
Volvo	V60 i cross country	T5 Drive-e Polestar AWD	Kombi	Allrad	Benzin	186	253	Mar 2015	Jul 2018	2024-03-01	138816
Volvo	S90 ii	T8 Plug-in Hybrid Polestar AWD	Stufenheck	Allrad	Benzin/Elektro	246	334	Oct 2017	Dec 2022	2024-05-01	138819
Volvo	S90 ii	T6 Drive-e Polestar AWD	Stufenheck	Allrad	Benzin	246	334	Mar 2016	Dec 2021	2024-05-01	138820
Volvo	S90 ii	T5 Drive-e Polestar	Stufenheck	Frontantrieb	Benzin	192	261	Mar 2016	Dec 2021	2024-05-01	138821
Volvo	S60 ii	D4 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	147	200	Mar 2015	May 2018	2024-03-01	138823
Volvo	S60 ii	D5 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	171	232	Mar 2015	May 2018	2024-03-01	138824
Volvo	S60 ii cross country	D4 Polestar AWD	Stufenheck	Allrad	Diesel	162	220	Mar 2015	Jul 2018	2024-03-01	138825
Volvo	S60 ii cross country	T5 Drive-e Polestar AWD	Stufenheck	Allrad	Benzin	186	253	Jun 2016	May 2018	2024-03-01	138826
Isuzu	D-Max i	2.5 Ditd 4X4	Pritsche/Fahrgestell	Allrad	Diesel	100	136	Oct 2006	Oct 2012	2024-03-01	138829
Volvo	S90 ii	D4 Drive-e Polestar AWD	Stufenheck	Allrad	Diesel	147	200	Mar 2016	Dec 2021	2024-05-01	138830
Audi	Q8	RS FSI Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	441	600	Sep 2019	-	2025-11-01	138832
Audi	A6 c8	55 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	270	367	Nov 2019	-	2024-03-01	138834
Volvo	Xc90 ii	T8 Plug-in Hybrid Polestar AWD	SUV	Allrad	Benzin/Elektro	246	334	Jun 2015	Dec 2022	2024-05-01	138837
Volvo	V90 ii	T8 Plug-in Hybrid Polestar AWD	Kombi	Allrad	Benzin/Elektro	246	334	Mar 2016	Dec 2018	2024-05-01	138839
Renault	Trafic iii	2.0 DCI 120	Bus	Frontantrieb	Diesel	88	120	Jun 2019	-	2024-03-01	138844
Renault	Trafic iii	2.0 DCI 145	Bus	Frontantrieb	Diesel	107	145	Jun 2019	-	2024-03-01	138845
Audi	A7 sportback	50 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	220	299	Nov 2019	-	2024-03-01	138846
Renault	Trafic iii	2.0 DCI 170	Bus	Frontantrieb	Diesel	125	170	Jun 2019	-	2024-03-01	138847
Audi	Q7	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	280	381	Nov 2019	-	2024-03-01	138851
Audi	Q7	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	335	455	Nov 2019	-	2024-03-01	138853
VW	Crafter	2.0 TDI 4motion	Bus	Allrad	Diesel	103	140	Apr 2017	-	2024-03-01	138856
Audi	Q5	35 TDI Mild Hybrid	SUV	Frontantrieb	Diesel/Elektro	120	163	Sep 2019	-	2024-03-01	138857
Audi	Q5	40 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	150	204	Sep 2019	-	2024-03-01	138858
Peugeot	2008 ii	1.2 Puretech 100	SUV	Frontantrieb	Benzin	74	101	Nov 2019	-	2024-03-01	138869
Audi	A8 d5	S8 Tfsi Mild Hybrid Quattro	Stufenheck	Allrad	Benzin/Elektro	420	571	Feb 2019	-	2025-11-01	138873
Audi	Q3	35 Tfsi Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	138876
Audi	Q3	35 Tfsi Mild Hybrid	SUV	Frontantrieb	Benzin/Elektro	110	150	Nov 2019	-	2024-03-01	138877
Nissan	Nv250	DCI 80	Kasten	Frontantrieb	Diesel	59	80	Jul 2019	-	2024-03-01	138879
Nissan	Nv250	DCI 95	Kasten	Frontantrieb	Diesel	70	95	Jul 2019	-	2024-03-01	138880
Nissan	Nv250	DCI 115	Kasten	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	138881
Nissan	Nv250	DCI 80	Bus	Frontantrieb	Diesel	59	80	Jul 2019	-	2024-03-01	138882
Nissan	Nv250	DCI 95	Bus	Frontantrieb	Diesel	70	95	Jul 2019	-	2024-03-01	138883
Nissan	Nv250	DCI 115	Bus	Frontantrieb	Diesel	85	116	Jul 2019	-	2024-03-01	138884
Mercedes-benz	Glc	300 4-matic	SUV	Allrad	Benzin	190	258	Nov 2019	Mar 2023	2024-03-01	138888
Ferrari	812 gts spider	6.5	Cabriolet	Heckantrieb	Benzin	585	795	Oct 2019	-	2024-03-01	138892
Peugeot	Partner	1.5 Bluehdi 100	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Jul 2019	-	2024-03-01	138894
VW	T-Roc	1.0 TSI	Cabriolet	Frontantrieb	Benzin	85	116	Dec 2019	-	2025-02-03	138897
VW	T-Roc	1.5 TSI	Cabriolet	Frontantrieb	Benzin	110	150	Dec 2019	-	2024-03-01	138898
Peugeot	Partner	1.2 Puretech 110	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Jan 2019	-	2025-12-01	138902
Peugeot	Partner	1.2 Puretech 130	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jul 2019	-	2024-03-01	138903
Bentley	Flying spur	6.0 W12 TSI 4WD	Stufenheck	Allrad	Benzin	467	635	Apr 2019	-	2024-03-01	138905
Mercedes-benz	Sprinter 4,6-T	416 CDI 4X4	Kasten	Allrad	Diesel	120	163	Nov 2013	Dec 2018	2024-03-01	138913
Subaru	Xv	2.0 I E-boxer AWD	SUV	Allrad	Benzin/Elektro	110	150	Oct 2019	-	2024-03-01	138918
Audi	Q5	50 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	220	299	Apr 2019	-	2024-03-01	138940
Citroën	Jumpy iii	2.0 Bluehdi 120	Bus	Frontantrieb	Diesel	90	122	Apr 2016	Dec 2022	2025-12-01	138950
Peugeot	Partner	1.5 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Jul 2019	-	2024-03-01	138957
Citroën	Berlingo	1.5 Bluehdi 75	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2019	-	2024-03-01	138959
Land Rover	Range rover iv	P360 Mhev 4X4	SUV	Allrad	Benzin/Elektro	265	360	Dec 2019	Sep 2021	2025-02-03	138972
Dodge	Challenger	6.2 SRT Hellcat Redeye	Coupe	Heckantrieb	Benzin	586	797	Sep 2019	-	2024-03-01	138974
Mercedes-benz	Marco polo camper	300 CDI	Bus	Heckantrieb	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	138980
Mercedes-benz	Marco polo camper	300 CDI 4-matic	Bus	Allrad	Diesel	176	239	Mar 2019	Dec 2020	2024-03-01	138981
Mercedes-benz	Marco polo camper	200 CDI	Bus	Heckantrieb	Diesel	100	136	Mar 2015	-	2024-03-01	138982
Mercedes-benz	Marco polo camper	200 CDI 4-matic	Bus	Allrad	Diesel	100	136	Mar 2015	-	2024-03-01	138984
Mercedes-benz	Marco polo camper	220 CDI	Bus	Heckantrieb	Diesel	120	163	Mar 2015	-	2024-03-01	138985
Mercedes-benz	Marco polo camper	220 CDI 4-matic	Bus	Allrad	Diesel	120	163	Mar 2015	-	2024-03-01	138986
Mercedes-benz	Marco polo camper	250 CDI	Bus	Heckantrieb	Diesel	140	190	Mar 2015	-	2024-03-01	138987
Mercedes-benz	Marco polo camper	250 CDI 4-matic	Bus	Allrad	Diesel	140	190	Mar 2015	-	2024-03-01	138989
Porsche	Macan	2.9 GTS	SUV	Allrad	Benzin	280	380	May 2019	-	2024-05-01	139008
Mercedes-benz	E-Klasse	E 300	Cabriolet	Heckantrieb	Benzin	190	258	Mar 2019	-	2024-03-01	139012
Mercedes-benz	E-Klasse	E 300	Stufenheck	Heckantrieb	Benzin	190	258	Apr 2019	Oct 2023	2025-02-03	139015
Hyundai	I10 iii	1.2 MPI	Schrägheck	Frontantrieb	Benzin	62	84	Sep 2019	-	2024-03-01	139017
Hyundai	I10 iii	1.0 MPI	Schrägheck	Frontantrieb	Benzin	49	67	Sep 2019	-	2024-03-01	139021
NIO	Es8	EV	SUV	Allrad	Elektro	400	544	Jan 2023	Jun 2023	2026-01-01	139022
Mercedes-benz	E-Klasse	E 300	Coupe	Heckantrieb	Benzin	190	258	Aug 2018	-	2024-03-01	139027
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	70	95	Dec 2019	-	2024-03-01	139031
Opel	Grandland	1.6 Turbo Hybrid	SUV	Frontantrieb	Benzin/Elektro	165	224	Dec 2019	-	2025-02-03	139036
Seat	Ibiza iv	1.2 TDI	Kasten/Schrägheck	Frontantrieb	Diesel	55	75	May 2010	May 2015	2024-03-01	139037
Mercedes-benz	Vario	O 815	Bus	Heckantrieb	Diesel	110	150	Aug 1996	Dec 2010	2024-03-01	139039
VW	Caddy alltrack iv	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	96	131	Jun 2019	Sep 2020	2025-06-01	139045
Mclaren	Gt	4	Coupe	Heckantrieb	Benzin	456	620	Aug 2019	-	2024-03-01	139047


--- Round 1 / 首次发送 ---
更新点

* 已处理前 20 个输入 Ktype，闭合 5 个尺寸组、10 条 READY 映射。
* Mégane I Kombi Van 暂按同代 Grandtour 货运衍生外廓复用，映射置信度设为 `MEDIUM`，未伪造独立货运尺寸。
* Master I([汽车数据网][1])([汽车数据网][1])- 已处理：20
* READY 映射：10
* PENDING 映射：10
* 尚未进入处理：80
* 已确认尺寸组：5
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138754	138754	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138755	138755	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138757	138757	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138758	138758	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138760	138760	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-01	HIGH	前驱GLB 250标准车身。	READY
138761	138761	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-01	HIGH	前驱GLB 220 d标准车身。	READY
138767	138767	Hatchback	Mégane III Phase I		5	EU-RENAULT-MEGANE-III-PHASE-I-HATCHBACK-01	HIGH	五门两厢标准车身。	READY
138771	138771	Van	Master III Phase II	X62			LOW	候选包含多个轴距与低顶、中顶、高顶分支。	PENDING: 尚未闭合FWD Kasten的轴距与车顶分支
138773	138773	Hatchback	i20 I (PB)	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-01	HIGH	2008年起五门两厢标准车身。	READY
138778	138778	Van/MPV	Dokker facelift 2017				LOW	候选为Dokker Van四门与Dokker MPV五门，外廓高度口径不同。	PENDING: 客货车身分支及标准高度尚未闭合
138779	138779	SUV	e-tron (GE)	GE	5	EU-AUDI-E-TRON-GE-SUV-01	HIGH	50 quattro标准SUV车身。	READY
138780	138780	SUV	e-tron (GE)	GE	5	EU-AUDI-E-TRON-GE-SUV-01	HIGH	与Ktype 138779重复输入，复用同一尺寸组。	READY
138783	138783	Van	NV300 I	X82			LOW	候选包含L1/L2及H1/H2车身。	PENDING: Kasten长度与车顶分支尚未闭合
138784	138784	Van	NV300 I	X82			LOW	候选包含L1/L2及H1/H2车身。	PENDING: Kasten长度与车顶分支尚未闭合
138785	138785	Van	NV300 I	X82			LOW	候选包含L1/L2及H1/H2车身。	PENDING: Kasten长度与车顶分支尚未闭合
138786	138786	Pickup	NV300 I	X82	2		LOW	底盘驾驶室存在不同轴距和整车长度配置。	PENDING: Pritsche/Fahrgestell轴距分支尚未闭合
138787	138787	Pickup	NV300 I	X82	2		LOW	底盘驾驶室存在不同轴距和整车长度配置。	PENDING: Pritsche/Fahrgestell轴距分支尚未闭合
138788	138788	MPV	NV300 I	X82			LOW	Bus/Kombi存在L1与L2车长分支。	PENDING: Bus长度分支尚未闭合
138789	138789	MPV	NV300 I	X82			LOW	Bus/Kombi存在L1与L2车长分支。	PENDING: Bus长度分支尚未闭合
138790	138790	MPV	NV300 I	X82			LOW	Bus/Kombi存在L1与L2车长分支。	PENDING: Bus长度分支尚未闭合
```

本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II 1.6i 16V	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.6i-16v-107hp-30241
EU-MERCEDES-BENZ-GLB-X247-SUV-01	4634	1834	1658	Auto-Data Mercedes-Benz GLB X247 generation	https://www.auto-data.net/en/mercedes-benz-glb-x247-generation-7171
EU-RENAULT-MEGANE-III-PHASE-I-HATCHBACK-01	4295	1808	1471	Auto-Data Renault Megane III 1.6 16V Ethanol	https://www.auto-data.net/en/renault-megane-iii-1.6-16v-110hp-ethanol-30363
EU-HYUNDAI-I20-I-PB-HATCHBACK-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.2	https://www.auto-data.net/en/hyundai-i20-i-pb-1.2-78hp-13926
EU-AUDI-E-TRON-GE-SUV-01	4901	1935	1632	Auto-Data Audi e-tron 50 71 kWh quattro	https://www.auto-data.net/en/audi-e-tron-50-71-kwh-313hp-quattro-45317
```

下一步优先处理

1. 一次性闭合 Renault Master III、Nissan NV300 和后续 Renault Trafic III 的共平台轴距、车长及车顶分支，避免分别重复抓取。
2. 用明确的固定高度口径拆分 Dokker Van 与 Dokker MPV。
3. 随后批量处理 Volvo Polestar 车型簇及 Audi 2019 年平台车型簇。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.6i-16v-107hp-30241 "Renault Megane I Grandtour (Phase II, 1999) 1.6i 16V (107 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
更新点

* 已将 Dokker 客货两种外廓拆分为独立派生行，原 `138778` PENDING 基础行取消。2019 Dokker Van 官方资料确认货运版为 `4363×1751×1809 mm`；乘用版高度为 `1814 mm`。
* 已闭合 NV300 2.0 dCi 的车身供应边界：120 PS 与 170 PS 厢式车对应 L1H1、L2H1；145 PS 对应 L1H1、L1H2、L2H1、L2H2；Combi 三种功率均覆盖 L1H1、L2H1。
* NV300 官方尺寸资料确认：L1 为 `4999 mm`、L2 为 `5399 mm`，车身宽度不含后视镜均为 `1956 mm`；H1 为 `1971 mm`，厢式车 H2 分别为 `2493/2490 mm`。
* 7 条原基础 PENDING 映射已由 16 条确定物理分支替代；NV300 Platform Cab 两条映射因改装后最终外廓不固定，暂不强行落入尺寸组。

当前批次进度

* 输入 Ktype：100
* 已进入处理：20
* READY 映射：26
* PENDING 映射：3
* 尚未进入处理：80
* 已确认尺寸组：13
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138778_van	138778	Van	Dokker facelift 2017			EU-DACIA-DOKKER-FACELIFT-2017-VAN-01	MEDIUM	Kasten货运车身分支。	READY
138778_mpv	138778	MPV	Dokker facelift 2017			EU-DACIA-DOKKER-FACELIFT-2017-MPV-01	MEDIUM	Großraumlimousine乘用车身分支。	READY
138783_l1h1	138783	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138783_l2h1	138783	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138784_l1h1	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138784_l1h2	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H2-01	HIGH	L1短轴高顶厢式车。	READY
138784_l2h1	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138784_l2h2	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H2-01	HIGH	L2长轴高顶厢式车。	READY
138785_l1h1	138785	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138785_l2h1	138785	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138788_l1h1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138788_l2h1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
138789_l1h1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138789_l2h1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
138790_l1h1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138790_l2h1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
```

本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-DOKKER-FACELIFT-2017-VAN-01	4363	1751	1809	Dacia Dokker Van 2019 official brochure	https://daciaclubnederland.nl/storage/downloads/belgium/be-brochure-fr-dacia-dokker-2019-08.pdf
EU-DACIA-DOKKER-FACELIFT-2017-MPV-01	4363	1751	1814	Auto-Data Dacia Dokker facelift 2017 generation	https://www.auto-data.net/en/dacia-dokker-model-1998
EU-NISSAN-NV300-I-VAN-L1H1-01	4999	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L1H2-01	4999	1956	2493	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L2H2-01	5399	1956	2490	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-MPV-L1H1-01	4999	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-MPV-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
```

下一步优先处理

1. 闭合 Renault Master III 180 FWD 的实际可售 L/H 分支，并创建对应尺寸组。
2. 判断 NV300 Platform Cab 是否能形成固定量产外廓；无法形成时明确保留底盘改装边界，不使用最大允许改装尺寸冒充整车尺寸。
3. 随后进入 Hyundai Tucson、i20 LPG 与 Volvo Polestar 车型簇。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* `138771` 已拆分为 Master III Phase III 的 5 个确定车身分支：L1H1、L1H2、L2H2、L3H2、L3H3；原无后缀 PENDING 行取消。180 hp FWD 厢式车的供应分支和三维已闭合。([汽车数据网][1])
* `138786`、`138787` 已确认均为 NV300 L2H1 Platform Cab，修改为 READY 并共用同一尺寸组。
* 已进入处理的 20 个 Ktype 不再存在 PENDING；本批仍有 80 个 Ktype 尚未处理，因此不能进入 COMPLETE。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：20
* 待处理 Ktype：80
* READY 映射：33
* 已处理范围内 PENDING 映射：0
* 已确认尺寸组：19
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138771_l1h1	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138771_l1h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	HIGH	L1短轴高顶厢式车。	READY
138771_l2h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	HIGH	L2中轴高顶厢式车。	READY
138771_l3h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	HIGH	L3长轴高顶厢式车。	READY
138771_l3h3	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	HIGH	L3长轴超高顶厢式车。	READY
138786	138786	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-L2H1-01	HIGH	L2H1长轴Platform Cab。	READY
138787	138787	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-L2H1-01	HIGH	L2H1长轴Platform Cab。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	5075	2070	2307	Renault Master official brochure; Auto-Data Renault Master III Phase III 2.3 Energy dCi 180 L1H1	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l1h1-40032
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	5075	2070	2500	Renault Master official brochure; Auto-Data Renault Master III Phase III 2.3 Energy dCi 180 L1H2	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l1h2-40037
EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	5575	2070	2499	Renault Master official brochure; Auto-Data Renault Master III Phase III 2.3 Energy dCi 180 L2H2	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l2h2-40042
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	6225	2070	2488	Renault Master official brochure; Auto-Data Renault Master III Phase III 2.3 Energy dCi 180 L3H2	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l3h2-40047
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	6225	2070	2744	Renault Master official brochure; Auto-Data Renault Master III Phase III 2.3 Energy dCi 180 L3H3	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l3h3-40054
EU-NISSAN-NV300-I-PLATFORM-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan LCV Customer Price List April 2020; Renault Trafic official press kit	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Nissan_LCV_Customer_Price_List_April2020.pdf;https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
```

## 下一步优先处理

1. 处理 Hyundai Tucson、复用现有 Hyundai i20 PB 尺寸组，并闭合 Dodge Caliber。
2. 按物理车身批量处理 Volvo V40、V60、S60、S90、V90、XC90 车型簇。
3. 随后处理 Audi 乘用车平台及 Renault Trafic III 共用车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-generation-7796 "Renault Master III (Phase III, 2019) Panel Van | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 新增闭合 Volvo V60 II、V40、V40 Cross Country、S90 II 四个尺寸组；同一车身下的 Polestar 动力版本直接复用，不按发动机或驱动形式重复建组。官方尺寸均明确区分车身宽度与含后视镜宽度。([沃尔沃汽车][1])
* `138797` 复用已建立的 Hyundai i20 I（PB）尺寸组，不重复输出尺寸组记录。
* 本轮新增 9 个已闭合 Ktype，未创建新的 PENDING 行。

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：29
* 尚待处理 Ktype：71
* READY 映射：42
* 已处理部分未解决映射：0
* 已确认尺寸组：23
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138797	138797	Hatchback	i20 I (PB)	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-01	HIGH	五门两厢标准车身。	READY
138805	138805	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	V60第二代标准旅行车外廓。	READY
138807	138807	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40标准五门两厢外廓。	READY
138808	138808	Hatchback	V40 Cross Country		5	EU-VOLVO-V40-CROSS-COUNTRY-HATCHBACK-01	HIGH	Cross Country加高车身外廓。	READY
138809	138809	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40标准五门两厢外廓。	READY
138819	138819	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138820	138820	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138821	138821	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138830	138830	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo V60 2021 official support dimensions	https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749
EU-VOLVO-V40-II-HATCHBACK-01	4370	1802	1420	Volvo V40 official support dimensions	https://www.volvocars.com/uk/support/car/v40/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V40-CROSS-COUNTRY-HATCHBACK-01	4370	1802	1458	Volvo V40 Cross Country official support dimensions	https://www.volvocars.com/uk/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo S90 2018 official support dimensions	https://www.volvocars.com/uk/support/car/s90/2018/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
```

## 下一步优先处理

1. 闭合 V60 I Cross Country、S60 II 与 S60 Cross Country 三个 Volvo 车身簇。
2. 随后处理 V90 II、XC90 II，并复用已核对的 Volvo 官方尺寸口径。
3. 再处理 Hyundai Tucson、Dodge Caliber、Isuzu D-Max 的独立外廓。

推进信号：CONTINUE

[1]: https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749?utm_source=chatgpt.com "V60 Dimensions | Volvo Support UK"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Volvo V60 I Cross Country、S60 II、S60 II Cross Country、XC90 II、V90 II 五个物理尺寸组，共新增 10 条 READY 映射。
* 同一车身的 Polestar 动力、能源和驱动差异均复用同一尺寸组，没有按发动机配置重复建组。
* Volvo 官方尺寸表分别给出车身宽度和含后视镜宽度；本轮 `WidthMM` 采用不含后视镜的车身宽度。([沃尔沃汽车][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：39
* READY 映射：52
* PENDING／尚未处理 Ktype：61
* 已确认尺寸组：28
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138811	138811	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138812	138812	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138814	138814	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138816	138816	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138823	138823	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-01	HIGH	第二代标准轿车外廓。	READY
138824	138824	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-01	HIGH	第二代标准轿车外廓。	READY
138825	138825	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country加高轿车外廓。	READY
138826	138826	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country加高轿车外廓。	READY
138837	138837	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	第二代标准SUV车身。	READY
138839	138839	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	第二代标准旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	4637	1847	1545	Volvo V60 Cross Country 2017 official support dimensions	https://www.volvocars.com/jp/support/car/v60-cross-country/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-S60-II-SEDAN-01	4635	1847	1484	Volvo S60 2018 official support dimensions	https://www.volvocars.com/en-ca/support/car/s60/17w17/article/84c655c2aaaa015ac0a801e801c02b97/5c828b35aab0984dc0a801e801603734/0328ea86b98d614cc0a801e800b575bb/
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539	Volvo S60 Cross Country 2018 official support dimensions	https://www.volvocars.com/jp/support/car/s60-cross-country/article/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo XC90 2018 official support dimensions	https://www.volvocars.com/uk/support/car/xc90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo V90 2018 official support dimensions	https://www.volvocars.com/us/support/car/v90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
```

## 下一步优先处理

1. 闭合 Hyundai Tucson I、Dodge Caliber 和 Isuzu D-Max I；D-Max 优先确认驾驶室及货斗造成的外廓分支。
2. 批量处理 Audi Q8、A6 C8、A7、Q7、Q5、A8 D5、Q3 车型簇。
3. 复用 NV300 已建平台尺寸，处理 Renault Trafic III Bus 的 L1H1、L2H1 分支。

推进信号：CONTINUE

[1]: https://www.volvocars.com/jp/support/car/v60-cross-country/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/ "V60 Cross Country 寸法 | Volvo Support JP"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 Hyundai Tucson I、Dodge Caliber，以及 Isuzu D-Max I 2.5 DiTD 4×4 的 Space Cab、Double Cab 两个确定物理分支；2.5 单排版本为后驱，不纳入该 4×4 Ktype。([汽车数据网][1])
* 已闭合 Renault Trafic III Bus 的 L1H1、L2H1 分支，三个动力 Ktype 批量关联，不按发动机重复建组。Renault 官方尺寸明确为 4999/5399×1956×1971 mm，宽度不含后视镜。([雷诺马提尼克][2])
* 已闭合 RS Q8、A6 C8、A7 C8、Q7 facelift、S8 D5、Q3 F3 和 Q5 FY PHEV 车身簇；Q7 55/60 TFSI e 复用同一尺寸组，Q3 两个重复 Ktype 复用同一尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：54
* 尚未处理 Ktype：46
* READY 映射：70
* 已处理部分 PENDING 映射：0
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138796	138796	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-SUV-01	HIGH	第一代五门SUV标准外廓。	READY
138806	138806	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-01	HIGH	五门两厢标准外廓。	READY
138829_spacecab	138829	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-PICKUP-SPACE-CAB-01	MEDIUM	2.5 DiTD 4x4的Space Cab物理分支。	READY
138829_doublecab	138829	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLE-CAB-01	MEDIUM	2.5 DiTD 4x4的Double Cab物理分支。	READY
138832	138832	SUV	RS Q8 (4M)	4M	5	EU-AUDI-RS-Q8-4M-SUV-01	HIGH	RS Q8标准SUV外廓。	READY
138834	138834	Sedan	A6 C8		4	EU-AUDI-A6-C8-SEDAN-01	HIGH	A6 C8插电混动轿车外廓。	READY
138844_l1h1	138844	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138844_l2h1	138844	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138845_l1h1	138845	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138845_l2h1	138845	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138846	138846	Hatchback	A7 Sportback C8		5	EU-AUDI-A7-C8-HATCHBACK-01	HIGH	五门Sportback标准外廓。	READY
138847_l1h1	138847	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138847_l2h1	138847	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138851	138851	SUV	Q7 II facelift 2019	4M	5	EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	HIGH	55 TFSI e标准SUV外廓。	READY
138853	138853	SUV	Q7 II facelift 2019	4M	5	EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	HIGH	60 TFSI e标准SUV外廓。	READY
138873	138873	Sedan	S8 D5		4	EU-AUDI-S8-D5-SEDAN-01	MEDIUM	D5标准轴距S8外廓；输入起始月早于公开量产资料。	READY
138876	138876	SUV	Q3 II (F3)	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	第二代Q3标准SUV外廓。	READY
138877	138877	SUV	Q3 II (F3)	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	与138876重复输入，复用同一尺寸组。	READY
138940	138940	SUV	Q5 II (FY)	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH	改款前50 TFSI e插电混动SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-TUCSON-I-SUV-01	4325	1795	1680	Auto-Data Hyundai Tucson I 2.0 i 16V 4WD	https://www.auto-data.net/en/hyundai-tucson-i-2.0-i-16v-4wd-140hp-13770
EU-DODGE-CALIBER-HATCHBACK-01	4415	1800	1535	Auto-Data Dodge Caliber 2.0 16V CRD	https://www.auto-data.net/en/dodge-caliber-2.0-16v-crd-140hp-2906
EU-ISUZU-D-MAX-I-PICKUP-SPACE-CAB-01	5030	1800	1715	Auto-Data Isuzu D-Max I 2.5 TD Space Cab	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-PICKUP-DOUBLE-CAB-01	5035	1800	1735	Auto-Data Isuzu D-Max I 2.5 TD Double Cab	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974
EU-AUDI-RS-Q8-4M-SUV-01	5012	1998	1694	Auto-Data Audi RS Q8 4M 4.0 TFSI	https://www.auto-data.net/en/audi-rsq8-4m-4.0-tfsi-v8-600hp-mild-hybrid-quattro-tiptronic-cod-38134
EU-AUDI-A6-C8-SEDAN-01	4939	1886	1457	Auto-Data Audi A6 C8 55 TFSI e 2019	https://www.auto-data.net/en/audi-a6-limousine-c8-55-tfsi-e-367hp-plug-in-hybrid-quattro-ultra-s-tronic-37900
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	4999	1956	1971	Renault Trafic Passenger official dimensions	https://www.renault-martinique.com/cars/TraficVpJ82ph1/dimensions.html
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	5399	1956	1971	Renault Trafic Passenger official dimensions	https://www.renault-martinique.com/cars/TraficVpJ82ph1/dimensions.html
EU-AUDI-A7-C8-HATCHBACK-01	4969	1908	1421	Auto-Wiki Audi A7 50 TFSI e 2019; Auto-Data Audi A7 C8 50 TFSI e	https://www.auto-wiki.org/audi/a7/c8-4k/a7-sportback-50-tfsi-e-quattro-s-tronic-220-kw-81999/;https://www.auto-data.net/en/audi-a7-sportback-c8-50-tfsi-e-299hp-plug-in-hybrid-quattro-ultra-s-tronic-45397
EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	5063	1970	1741	Auto-Data Audi Q7 55 TFSI e 2019; Auto-Data Audi Q7 60 TFSI e 2019	https://www.auto-data.net/en/audi-q7-ii-typ-4m-facelift-2019-55-tfsi-e-v6-381hp-plug-in-hybrid-quattro-tiptronic-38220;https://www.auto-data.net/en/audi-q7-ii-typ-4m-facelift-2019-60-tfsi-e-v6-456hp-plug-in-hybrid-quattro-tiptronic-38215
EU-AUDI-S8-D5-SEDAN-01	5179	1945	1474	Auto-Data Audi S8 D5 4.0 TFSI	https://www.auto-data.net/en/audi-s8-d5-4.0-tfsi-v8-571hp-mild-hybrid-quattro-tiptronic-cod-38047
EU-AUDI-Q3-II-F3-SUV-01	4484	1849	1616	Auto-Data Audi Q3 II F3 35 TFSI Mild Hybrid	https://www.auto-data.net/en/audi-q3-ii-f3-35-tfsi-150hp-mild-hybrid-s-tronic-41527
EU-AUDI-Q5-II-FY-SUV-01	4671	1893	1661	Auto-Data Audi Q5 II FY 50 TFSI e	https://www.auto-data.net/ro/audi-q5-ii-fy-50-tfsi-e-299hp-plug-in-hybrid-quattro-s-tronic-38361
```

## 下一步优先处理

1. 闭合 Audi Q5 35/40 TDI 的改款前后物理边界，避免把 2020 facelift 尺寸错误复用于 2019 输入。
2. 处理 Peugeot 2008 II、Audi Q8/A8 后续相邻车型与 Nissan NV250/Dacia Dokker 共平台簇。
3. 随后处理 Mercedes-Benz GLC、E-Class 三种车身和 Marco Polo Camper。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/hyundai-tucson-i-2.0-i-16v-4wd-140hp-13770 "Hyundai Tucson I 2.0 i 16V 4WD (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.renault-martinique.com/cars/TraficVpJ82ph1/dimensions.html?utm_source=chatgpt.com "Dimensions"
[3]: https://www.auto-data.net/en/audi-rs-q8-4m-4.0-tfsi-v8-600hp-mild-hybrid-quattro-tiptronic-cod-38134 "Audi RSQ8 (4M) 4.0 TFSI V8 (600 Hp) Mild Hybrid quattro tiptronic COD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* Audi Q5 35 TDI 前驱与 40 TDI quattro 均对应 2020 facelift MHEV 车身；两者长宽相同，但高度分别为 1637 mm 和 1662 mm，因此独立建组。输入起始月早于公开量产时间，映射置信度设为 `MEDIUM`。([汽车数据网][1])
* Nissan NV250 已按官方规格闭合：80 PS 厢式车仅 L1，95/115 PS 厢式车覆盖 L1、L2；Bus 对应短轴五座 Kombi 外廓。官方规格明确给出不含后视镜宽度。
* Peugeot 2008 II、GLC X253 facelift、Ferrari 812 GTS 与 T-Roc Cabriolet 均已闭合；T-Roc 两个动力版本复用同一官方外廓。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：67
* 尚待处理 Ktype：33
* READY 映射：85
* 已处理部分 PENDING 映射：0
* 已确认尺寸组：50
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138857	138857	SUV	Q5 II facelift 2020	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	MEDIUM	前驱MHEV外廓；输入起始月早于公开量产时间。	READY
138858	138858	SUV	Q5 II facelift 2020	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-AWD-01	MEDIUM	四驱MHEV外廓；输入起始月早于公开量产时间。	READY
138869	138869	SUV	2008 II		5	EU-PEUGEOT-2008-II-SUV-01	HIGH	第二代标准SUV外廓。	READY
138879	138879	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	80 PS短轴L1厢式车。	READY
138880_l1	138880	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	95 PS短轴L1厢式车。	READY
138880_l2	138880	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L2-01	HIGH	95 PS长轴L2厢式车。	READY
138881_l1	138881	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	115 PS短轴L1厢式车。	READY
138881_l2	138881	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L2-01	HIGH	115 PS长轴L2厢式车。	READY
138882	138882	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138883	138883	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138884	138884	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138888	138888	SUV	GLC X253 facelift 2019	X253	5	EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	HIGH	GLC 300 4MATIC标准SUV外廓。	READY
138892	138892	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS双门敞篷外廓。	READY
138897	138897	Convertible	T-Roc I Cabriolet		2	EU-VW-T-ROC-I-CONVERTIBLE-01	HIGH	双门软顶敞篷外廓。	READY
138898	138898	Convertible	T-Roc I Cabriolet		2	EU-VW-T-ROC-I-CONVERTIBLE-01	HIGH	双门软顶敞篷外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	4682	1893	1637	Auto-Data Audi Q5 II facelift 2020 35 TDI Mild Hybrid	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-35-tdi-163hp-mild-hybrid-s-tronic-41477
EU-AUDI-Q5-II-FACELIFT-2020-SUV-AWD-01	4682	1893	1662	Auto-Data Audi Q5 II facelift 2020 40 TDI Mild Hybrid quattro	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-40-tdi-204hp-mild-hybrid-quattro-ultra-s-tronic-40640
EU-PEUGEOT-2008-II-SUV-01	4300	1770	1550	Auto-Data Peugeot 2008 II 1.2 PureTech 100	https://www.auto-data.net/en/peugeot-2008-ii-1.2-puretech-100hp-38042
EU-NISSAN-NV250-I-VAN-L1-01	4282	1829	1844	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-VAN-L2-01	4666	1829	1836	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-MPV-L1-01	4282	1829	1844	Nissan NV250 official brochure; Nissan Europe NV250 launch release	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf;https://europe.nissannews.com/en-GB/releases/nissan-offers-major-boost-to-compact-van-segment-with-nv250
EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	4655	1890	1644	Auto-Data Mercedes-Benz GLC X253 facelift GLC 300 4MATIC	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-facelift-2019-glc-300-258hp-eq-boost-4matic-g-tronic-37278
EU-FERRARI-812-GTS-CONVERTIBLE-01	4693	1971	1278	Auto-Data Ferrari 812 GTS 6.5 V12	https://www.auto-data.net/en/ferrari-812-gts-6.5-v12-800hp-dct-39253
EU-VW-T-ROC-I-CONVERTIBLE-01	4268	1811	1522	Volkswagen Newsroom T-Roc Cabriolet official technical data	https://www.volkswagen-newsroom.com/en/the-t-roc-cabriolet-5851/technical-data-5862
```

## 下一步优先处理

1. 按共平台一次闭合 Peugeot Partner、Citroën Berlingo 与 Citroën Jumpy 的车长分支。
2. 批量处理 Mercedes-Benz Marco Polo Camper、E-Class Sedan/Coupe/Cabriolet。
3. 随后处理 Bentley Flying Spur、Porsche Macan、Subaru XV、Range Rover IV 与 Dodge Challenger。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-35-tdi-163hp-mild-hybrid-s-tronic-41477 "Audi Q5 II (FY, facelift 2020) 35 TDI (163 Hp) Mild Hybrid S tronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/peugeot-2008-ii-1.2-puretech-100hp-38042 "Peugeot 2008 II 1.2 PureTech (100 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* Mercedes-Benz E-Class 三个 Ktype 的生产区间跨越 2020 年改款，已分别拆分为改款前和 facelift 后外廓；未用单一尺寸覆盖两个不同车身。([汽车数据网][1])
* Subaru XV e-BOXER 已采用欧洲规格：`4465×1800×1595 mm`，官方资料明确 `1800 mm` 为不含后视镜宽度。
* NIO ES8 根据 `400 kW / 544 hp` 锁定第一代 facelift，而非 2023 年第二代；官方用户手册明确车宽 `1962 mm` 不含侧后视镜。([蔚来][2])
* Ford Fiesta 1.0 EcoBoost 95 同时覆盖三门和五门车身，已拆为两个物理分支；两者三维相同但不合并车身组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：79
* 尚未处理 Ktype：21
* READY 映射：101
* 已处理部分 PENDING 映射：0
* 已确认尺寸组：65
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138905	138905	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代四门轿车标准外廓。	READY
138918	138918	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH	欧洲规格e-BOXER五门SUV外廓。	READY
138974	138974	Coupe	Challenger III facelift 2014	LC	2	EU-DODGE-CHALLENGER-III-FACELIFT-2014-COUPE-01	HIGH	Hellcat Redeye宽体双门外廓。	READY
139008	139008	SUV	Macan I facelift 2018	95B	5	EU-PORSCHE-MACAN-I-FACELIFT-2018-SUV-01	HIGH	2019款GTS标准SUV外廓。	READY
139012_prefl	139012	Convertible	E-Class Cabrio A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFL-01	HIGH	2017-2020改款前A238敞篷外廓。	READY
139012_facelift	139012	Convertible	E-Class Cabrio A238 facelift 2020	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-FACELIFT-2020-CONVERTIBLE-01	HIGH	2020-2023改款后A238敞篷外廓。	READY
139015_prefl	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH	2019-2020改款前W213轿车外廓。	READY
139015_facelift	139015	Sedan	E-Class W213 facelift 2020	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-2020-SEDAN-01	HIGH	2020-2023改款后W213轿车外廓。	READY
139017	139017	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门两厢标准外廓。	READY
139021	139021	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门两厢标准外廓。	READY
139022	139022	SUV	ES8 I facelift 2020		5	EU-NIO-ES8-I-FACELIFT-2020-SUV-01	HIGH	400 kW第一代改款五门SUV外廓。	READY
139027_prefl	139027	Coupe	E-Class Coupe C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	HIGH	2018-2020改款前C238双门外廓。	READY
139027_facelift	139027	Coupe	E-Class Coupe C238 facelift 2020	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-FACELIFT-2020-COUPE-01	HIGH	2020-2023改款后C238双门外廓。	READY
139031_3dr	139031	Hatchback	Fiesta VII (Mk8)		3	EU-FORD-FIESTA-VII-MK8-HATCHBACK-3D-01	MEDIUM	三门两厢物理分支。	READY
139031_5dr	139031	Hatchback	Fiesta VII (Mk8)		5	EU-FORD-FIESTA-VII-MK8-HATCHBACK-5D-01	MEDIUM	五门两厢物理分支。	READY
139036	139036	SUV	Grandland X		5	EU-OPEL-GRANDLAND-X-SUV-01	HIGH	改款前前驱插电混动SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1987	1484	Auto-Data Bentley Flying Spur III 6.0 W12	https://www.auto-data.net/en/bentley-flying-spur-iii-6.0-w12-635hp-awd-automatic-37259
EU-SUBARU-XV-II-SUV-01	4465	1800	1595	Subaru UK XV e-BOXER official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/21966/xv-e-boxer.pdf
EU-DODGE-CHALLENGER-III-FACELIFT-2014-COUPE-01	5017	1923	1449	Auto-Data Dodge Challenger SRT Hellcat Redeye	https://www.auto-data.net/en/dodge-challenger-iii-facelift-2014-srt-hellcat-redeye-6.2-hemi-v8-797hp-automatic-32612
EU-PORSCHE-MACAN-I-FACELIFT-2018-SUV-01	4686	1926	1609	Auto-Data Porsche Macan I facelift 2018 GTS	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2018-gts-2.9-v6-380hp-pdk-gpf-38260
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFL-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300-258hp-eq-boost-9g-tronic-38309
EU-MERCEDES-BENZ-E-CLASS-A238-FACELIFT-2020-CONVERTIBLE-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class Cabrio A238 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-300-258hp-eq-boost-9g-tronic-41074
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-300-258hp-eq-boost-9g-tronic-38269
EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-2020-SEDAN-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300-258hp-eq-boost-9g-tronic-40876
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	Auto-Data Hyundai i10 III 1.2 MPi; Auto-Data Hyundai i10 III 1.0 MPi	https://www.auto-data.net/en/hyundai-i10-iii-1.2-mpi-84hp-37589;https://www.auto-data.net/en/hyundai-i10-iii-1.0-mpi-67hp-37604
EU-NIO-ES8-I-FACELIFT-2020-SUV-01	5022	1962	1756	NIO ES8 official user manual	https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-300-258hp-eq-boost-9g-tronic-38303
EU-MERCEDES-BENZ-E-CLASS-C238-FACELIFT-2020-COUPE-01	4835	1860	1428	Auto-Data Mercedes-Benz E-Class Coupe C238 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-300-258hp-eq-boost-9g-tronic-41066
EU-FORD-FIESTA-VII-MK8-HATCHBACK-3D-01	4040	1735	1476	Auto-Data Ford Fiesta Mk8 3-door 1.0 EcoBoost 95	https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.0-ecoboost-95hp-41400
EU-FORD-FIESTA-VII-MK8-HATCHBACK-5D-01	4040	1735	1476	Xezii Ford Fiesta Mk8 5-door 1.0 EcoBoost 95	https://xezii.com/en/xe/ford-ford-fiesta-viii-mk8-5-door-1-0-ecoboost-95-hp-2019-2020-2021
EU-OPEL-GRANDLAND-X-SUV-01	4477	1856	1609	Auto-Data Opel Grandland X 1.6 Turbo Plug-in Hybrid	https://www.auto-data.net/en/opel-grandland-x-1.6-turbo-224hp-plug-in-hybrid-automatic-38293
```

## 下一步优先处理

1. 闭合 Peugeot Partner、Citroën Berlingo 与 Citroën Jumpy 的短轴、长轴和乘用／货运分支。
2. 处理 Mercedes-Benz Marco Polo、Sprinter、Crafter、Vario 和 VW Caddy 等商用车外廓。
3. 最后处理 Range Rover IV、McLaren GT、Seat Ibiza Van 和剩余独立车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300-258hp-eq-boost-9g-tronic-38309?utm_source=chatgpt.com "Mercedes-Benz E-class Cabrio (A238) E 300 (258 Hp) EQ ..."
[2]: https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html?utm_source=chatgpt.com "ES8 User Manual"
[3]: https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.0-ecoboost-95hp-41400?utm_source=chatgpt.com "Ford Fiesta VIII (Mk8) 3 door 1.0 EcoBoost (95 Hp)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 已闭合 Peugeot Partner K9 的 L1/L2 标准车身和 Grip 加高分支；BlueHDi 75 仅落入 L1，BlueHDi 100 覆盖 L1/L2 及对应 Grip 分支，PureTech 110/130 覆盖 L1/L2 标准车身。2019 资料明确给出各长度、车身宽度和高度。([Charters Peugeot][1])
* 已闭合 Citroën Jumpy III Bus 的 XS、M、XL 三种长度，标准外廓分别为 4609/4959/5309 mm，车身宽度均为 1920 mm。([carnet.hu][2])
* Marco Polo W447 的 8 个动力 Ktype 共用同一露营车外廓；Range Rover L405 P360 拆为 SWB、LWB；Seat Ibiza Van、Caddy Alltrack 客货分支及 McLaren GT 均已闭合。([奔驰驾驭空间][3])
* Sprinter 4.6T 416 CDI 4×4 同时涉及 `906.655`、`906.657`，尚不能确定对应轴距和车顶组合；Vario O 815 Bus 存在多个轴距及车身制造商外廓，二者保留明确 PENDING，不用猜测尺寸强制闭合。([Nokian Tyres][4])

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：98
* PENDING Ktype：2
* 尚未处理 Ktype：0
* READY 映射：129
* PENDING 映射：2
* 已确认尺寸组：80
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138894_l1	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138894_l1_grip	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	L1 Grip加高车身。	READY
138894_l2	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴标准车身。	READY
138894_l2_grip	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	HIGH	L2长轴Grip加高车身。	READY
138902_l1	138902	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138902_l2	138902	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴标准车身。	READY
138903_l1	138903	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1标准车身。	READY
138903_l2	138903	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2长轴标准车身。	READY
138913	138913	Van	Sprinter II (W906)	W906			LOW	W906 4.6T 4x4覆盖906.655与906.657，具体轴距和车顶组合未闭合。	PENDING: 轴距与车顶分支尚未闭合
138950_xs	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	XS紧凑轴距Bus车身。	READY
138950_m	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M标准轴距Bus车身。	READY
138950_xl	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长轴Bus车身。	READY
138957_l1	138957	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138957_l1_grip	138957	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	L1 Grip加高车身。	READY
138959	138959	Van	Berlingo III (K9)	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-01	MEDIUM	M短轴标准货运车身。	READY
138972_swb	138972	SUV	Range Rover IV facelift 2017	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	MEDIUM	标准轴距五门SUV车身。	READY
138972_lwb	138972	SUV	Range Rover IV facelift 2017	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-LWB-01	MEDIUM	长轴距五门SUV车身。	READY
138980	138980	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138981	138981	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138982	138982	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138984	138984	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138985	138985	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138986	138986	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138987	138987	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138989	138989	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
139037	139037	Van	Ibiza IV (6J)	6J1	3	EU-SEAT-IBIZA-IV-6J-VAN-3D-01	MEDIUM	三门SC货运衍生车身。	READY
139039	139039	MPV	Vario			LOW	O 815客车存在多个轴距底盘及车身制造商外廓。	PENDING: 客车轴距与车身制造商外廓尚未闭合
139045_van	139045	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-IV-ALLTRACK-VAN-SWB-01	MEDIUM	短轴Alltrack货运车身。	READY
139045_mpv	139045	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	短轴Alltrack乘用车身，含标准车顶行李架。	READY
139047	139047	Coupe	McLaren GT		2	EU-MCLAREN-GT-COUPE-01	HIGH	双门GT标准车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	4403	1848	1860	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	4753	1848	1860	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XS-01	4609	1920	1905	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-JUMPY-III-K0-MPV-M-01	4959	1920	1895	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XL-01	5309	1920	1935	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796	Citroën Berlingo Van 2019 owner manual	https://www.carmanualsonline.info/citroen-berlingo-van-2019-owners-manual/?srch=width
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	5000	1984	1869	Land Rover Range Rover 2020 official brochure; Asbury Automotive Range Rover P360 specifications	https://autocatalogarchive.com/wp-content/uploads/2021/02/Range-Rover-2020-UK.pdf;https://www.asburyauto.com/2020-land-rover-range-rover-p360
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-LWB-01	5200	1984	1868	Land Rover Range Rover 2020 official brochure; Range Rover L405 body dimensions	https://autocatalogarchive.com/wp-content/uploads/2021/02/Range-Rover-2020-UK.pdf;https://en.wikipedia.org/wiki/Range_Rover_(L405)
EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/01/Mercedes-Clase-V-Marco-Polo-2014.pdf
EU-SEAT-IBIZA-IV-6J-VAN-3D-01	4034	1693	1428	Auto-Data Seat Ibiza IV SC 1.2 TDI	https://www.auto-data.net/en/seat-ibiza-iv-sc-1.2-tdi-75hp-36504
EU-VW-CADDY-IV-ALLTRACK-VAN-SWB-01	4408	1794	1823	Auto-Data Volkswagen Caddy Panel Van IV 1.4 TSI	https://www.auto-data.net/en/volkswagen-caddy-panel-van-iv-1.4-tsi-125hp-dsg-28478
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4408	1793	1858	Volkswagen Caddy Alltrack 2019 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/august/caddy-trendline-alltrack-online-brochure-20190514.pdf
EU-MCLAREN-GT-COUPE-01	4683	1930	1213	Automobile Dimension McLaren GT	https://www.automobiledimension.com/model/mclaren/gt
```

## 下一步优先处理

1. 仅闭合 Sprinter `906.655/906.657` 对应的轴距与车顶组合。
2. 确认 Vario O 815 的具体轴距及车身制造商，避免用底盘宽度代替完整客车外廓。
3. 两项闭合后立即执行一次机械收尾，并输出两张最终完整 TSV 与两个指定下载链接。

推进信号：CONTINUE

[1]: https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf "https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf"
[2]: https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf "https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf"
[3]: https://mercedes.drive.place/marco_polo/iii/group_minivan/647948 "https://mercedes.drive.place/marco_polo/iii/group_minivan/647948"
[4]: https://www.nokiantyres.jp/taiyawo-tansu/zi-dong-chemeka/mercedes-benz/2014/sprinter-4-6-t-box-906/416-cdi-4x4-906-655-906-657-120kw/ "https://www.nokiantyres.jp/taiyawo-tansu/zi-dong-chemeka/mercedes-benz/2014/sprinter-4-6-t-box-906/416-cdi-4x4-906-655-906-657-120kw/"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* `138913` 已由原 PENDING 基础行拆分为 4 个确定外廓：`906.655` 长轴高顶/超高顶，以及 `906.657` 超长轴高顶/超高顶。官方资料确认两种车身代码均为 4325 mm 轴距，后悬分别为 1615 mm 与 2015 mm；4×4 最大非载荷高度分别按对应车顶落盘。([GForce Parts][1])
* `139039` 未修改。官方资料确认 `670.373` 和 `670.374` 分别是 4250 mm、4800 mm 轴距的客车车身制造用 chassis cowl，仅固定底盘罩架长度和宽度，完整客车高度及最终上装外廓由车身制造商决定，当前仍不能创建合规完整尺寸组。([PartSouq][2])

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138913_l3h2	138913	Van	Sprinter II facelift 2013	906.655		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H2-01	MEDIUM	906.655长轴高顶4x4外廓；4.6-T为目录归类。	READY
138913_l3h3	138913	Van	Sprinter II facelift 2013	906.655		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H3-01	MEDIUM	906.655长轴超高顶4x4外廓；4.6-T为目录归类。	READY
138913_l4h2	138913	Van	Sprinter II facelift 2013	906.657		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H2-01	MEDIUM	906.657超长轴高顶4x4外廓；4.6-T为目录归类。	READY
138913_l4h3	138913	Van	Sprinter II facelift 2013	906.657		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H3-01	MEDIUM	906.657超长轴超高顶4x4外廓；4.6-T为目录归类。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H2-01	6961	1993	2815	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H3-01	6961	1993	3045	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H2-01	7361	1993	2820	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H3-01	7361	1993	3055	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
```

## 下一步优先处理

确认 `139039` 是否存在能够限定 `670.373/670.374` 完整量产客车上装的 homologation 或厂商车身资料；若仍只能确认 chassis cowl，则不能用未完成底盘尺寸冒充完整 Bus 外廓。

推进信号：CONTINUE

[1]: https://ftp.gforceparts.com/en/catalog/genuine/vehicle?c=Mercedes-Benz&cid=25780&cname=EXHAUST+SYSTEM&q=WDB9066552P361110&ssd=%24%2AKwGJvayplsne3_XC3OiDudHF5eL8jYKPjpyzgMjO_er-8vT8rqm5___z6Oju7_asq47kys7K--35_dvcxo2PiI7riYuO093Axdn9x5nOn4XAqreZlp_RmYDTyo6A3Jndn4aJj4qH0pGOzd_V_MCYy53Yzqf_-ISMjYyIitC8w42LjI2LmJGdj4_SgZiEjI2MiIrAwNLI2Z-GmZiRnY-H0oGYjJ6XmN7RwNbSjYjlnpeYy9zA1tKImMAAAAAAO8g_Ug%3D%3D%24&vid=0&utm_source=chatgpt.com "EXHAUST SYSTEM | Mercedes-Benz 515 KA 4X2 4325 13.12.2016 Standard Parts Catalogs | PartSouq"
[2]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=1323317507&cname=ENGINE+COOLING+SYSTEM&q=&srsltid=AfmBOooBUP3lpvlpv3cDSBXdfFcVNGoLwFGx5ZIlS567ilhIuqYS-RK8&ssd=%24%2AKwGtmYiL8Kr308zwz6qoo_XhwcbYqaarqriXpOzq2dfa0-fEtrui39-gqKmsqav28eat4PrY5Lztufzqmb2yu_W9pKio9Pvns7z-uqWvrq72_6nh6Pzw3-W77eTyuury9bS98_q5_OriqK6qr6y8tbm1q_alvLu0vfPyufzq5cy8tbr88Luh5Pji2ry1uun9u6Hk-_biAAAAAHWjc2k%3D%24&vid=0&utm_source=chatgpt.com "Mercedes-Benz VARIO O810-O815 Standard, Japan 670.373 ..."


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* `139039` 未变更。已确认 `670.373` 与 `670.374` 对应 Mercedes-Benz Vario 的两种客车改装底盘，轴距分别为 4250 mm 和 4800 mm。
* 厂商规格仅提供底盘罩架长度、宽度及车架高度，并明确留给车身制造商完成客车上装；不同上装会产生不同整车长度和高度，因此不能把底盘尺寸冒充完整 Bus 外廓。([Scribd][1])
* 当前缺少能够把该 Ktype 限定到具体车身制造商和标准上装型号的证据，继续保持 PENDING。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

需要补充 `139039` 对应的具体客车车身制造商、上装型号或 homologation/type-approval 记录。仅凭 `O 815 (670.373, 670.374)` 无法形成符合要求的完整长宽高尺寸组。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK "Vario Specifications for Mercedes-Benz Vans | PDF | Truck | Vehicles"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 已进一步确认：`670.373` 是 4250 mm 轴距、`670.374` 是 4800 mm 轴距，二者均被定义为“用于客车车身的带前围底盘”，不是完整量产客车车身。([零件市场][1])
* Mercedes-Benz 规格表只给出底盘长度 `6935/7485 mm`、底盘宽度 `2206 mm` 和车架高度，没有给出完成上装后的客车高度；资料也明确将其列为供乘用车改装的 chassis cowl。因此不能用底盘三维冒充 Bus 完整外廓。([Dezo's Garage][2])
* 已修正 `139039` 的 Notes 和 PENDING 原因，使阻塞条件明确指向具体客车上装，而不是继续重复核对底盘。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139039	139039	MPV	Vario O 815 (B670)			LOW	670.373为4250mm轴距、670.374为4800mm轴距，均为客车上装底盘；完整外廓取决于车身制造商。	PENDING: 缺少具体客车上装型号及完整三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

从输入源、VIN、homologation/type-approval 或车辆登记资料中补充 `139039` 的具体车身制造商和客车上装型号。缺少该信息时，无法合法创建完整长宽高尺寸组，也不能输出 COMPLETE。

推进信号：CONTINUE

[1]: https://partsouq.com/shop/product/A0002671659-mercedes-guide/19682173?utm_source=chatgpt.com "GUIDE A0002671659 | MERCEDES Parts | PartSouq"
[2]: https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf "7938_VarioSpecBro.qxd"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* `139039` 仍无法闭合。`670.373` 与 `670.374` 是分别对应 4250 mm、4800 mm 轴距的客车车身用底盘，不代表唯一完整客车外廓。([零件市场][1])
* 已找到 Mercedes-Benz Medio O 815 等完整客车上装，但公开车辆记录显示其外廓可达约 `7700×2440 mm`，其他 Vario O 815 客车又存在不同长度、宽度和高度，证明 `O 815` 发动机型号不能唯一确定上装车身。([Autoplius][2])
* 已修正 PENDING 描述，明确阻塞原因是该 Ktype 同时合并两个底盘代码且未提供最终上装型号，而非尺寸网页缺失。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139039	139039	MPV	Vario O 815 (B670)			LOW	Ktype同时覆盖670.373与670.374两种客车上装底盘；最终外廓随轴距及车身制造商变化。	PENDING: 缺少具体底盘代码及完整客车上装型号
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 的 VIN、明确的 `670.373/670.374` 分支，以及 Mercedes-Benz Medio、Teamstar、Plaxton、Autobus 或其他具体车身制造商和上装型号。现有输入不足以生成不含猜测的完整三维。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=25676330&q=&srsltid=AfmBOoq4zgaOiaAzulN2c75SwaEXeFxMydon3qfCwChCMAHglwgtJiKV&ssd=%24%2AKwG9iZiL1dS_67_5_NGhneXx0dbIuba7uqiHtPz6ycfKw_fUpquyz8-_vb28sb7m6Py98OrI9Kz9qez6jM6sparirLO54-7zuaKr7620urjmpbr_6cm7oLr3_paj5vuss6rNw6un9LHmtbuwub-5pamx-v6-v7q48vD_7r6Yv634q7Lh--Xn-vqp7Kyzqrm5ubjh7OajrPrrrbSrqfr6qeSss6q-3aun9LuqrbSruLnLq6f0rqettKu7rfMAAAAAQGAPpQ%3D%3D%24&vid=0&utm_source=chatgpt.com "Mercedes-Benz VARIO O810-O815 Standard, Japan 670.374 ..."
[2]: https://en.autoplius.lt/ads/mercedes-benz-vario-medio-815-30-seater-recreational-29841238.html "Mercedes-Benz Vario Medio 815 30-Seater, recreational 2002-08 m., | A29841238"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 14 / 下一步 ---
更新点

* `139039` 无新增可闭合证据。Mercedes-Benz Vario 官方资料只确认 4250 mm、4800 mm 两种未完成底盘；展示的长度、宽度与高度属于驾驶室底盘，不是完成客车上装后的整车三维。([Dezo's Garage][1])
* 现有 Ktype 同时覆盖 `670.373`、`670.374`，公开零部件目录也只确认发动机与两个车身代码，无法限定唯一车身制造商或完整 Bus 外廓。([Meyer Motoren][2])
* 继续使用公开通用资料只会重复得到底盘参数，不能满足尺寸组必须为完整量产外廓的要求。

当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

本轮新增/修改的 Ktype 映射 TSV

无

本轮首次创建/修正的 DIMENSION_GROUP TSV

无

下一步优先处理

* `139039` 只能通过 VIN、CoC、型式认证号、车身制造商铭牌或具体上装型号继续闭合；在缺少这些输入时，不创建猜测性尺寸组。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Vario-UK.pdf "untitled"
[2]: https://www.meyermotoren.de/en/fahrzeuge/139039/mercedes-benz/vario_bus_b670_/o_815_670_373_670_374_?utm_source=chatgpt.com "Mercedes-Benz Vario Bus (B670) O 815 (670.373, 670.374)"


--- 发送 / 继续到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / 下一步 ---
## 更新点

* `139039` 无新增可闭合证据。
* Mercedes-Benz 原始规格将 4250 mm、4800 mm 两种版本列为客车改装用 `chassis cowl`，仅提供未完成底盘长度、宽度及车架高度，没有完整客车上装高度。资料同时明确最终车身由车身制造商负责，因此 `670.373/670.374` 不能唯一决定完整外廓。([Scribd][1])
* 现有资料仍不足以创建符合规则的 DIMENSION_GROUP，未使用底盘尺寸或二手车个例强行闭合。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：1
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 对应的具体 `670.373` 或 `670.374` 分支，以及完整客车上装制造商、型号或 CoC/type-approval 三维。缺少这些信息时继续检索通用 O 815 资料不会消除当前 PENDING。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK "Vario Specifications for Mercedes-Benz Vans | PDF | Truck | Vehicles"


--- 发送 / 继续到 Round 16 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 16 / 下一步 ---
## 更新点

* 已取消无后缀的 `139039` 基础 PENDING 行，按已确认的两种物理底盘边界拆分为 `swb`、`lwb` 两行。
* `670.373` 明确为 4250 mm 轴距，`670.374` 明确为 4800 mm 轴距；官方尺寸图也显示两种底盘长度不同。([LastVin][1])
* 两种代码都是客车上装底盘，同一代码可安装 Plaxton、Autobus、Cibro 等不同完整车身，现阶段仍不能为任一分支确定唯一完整长宽高。([Autoline][2])

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139039_swb	139039	MPV	Vario O 815 (B670)	670.373			MEDIUM	短轴客车上装底盘分支，完整外廓取决于车身制造商。	PENDING: 缺少具体客车上装型号及完整三维
139039_lwb	139039	MPV	Vario O 815 (B670)	670.374			MEDIUM	长轴客车上装底盘分支，完整外廓取决于车身制造商。	PENDING: 缺少具体客车上装型号及完整三维
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

分别补充 `670.373`、`670.374` 对应的车身制造商、完整上装型号或整车型式认证三维；不得继续以未完成底盘尺寸代替 Bus 完整外廓。

推进信号：CONTINUE

[1]: https://www.lastvin.com/vin/8vKkQA8rD0OLEyprW?utm_source=chatgpt.com "2008 MERCEDES-BENZ O818DWINDL4X2 4250 (670.373)"
[2]: https://autoline.info/-/sale/interurban-buses/Mercedes-Benz/CIBRO-2005-2010-O-814-670-373-670-374-Motorina--23111614125964813300?utm_source=chatgpt.com "Mercedes-Benz CIBRO 2005 > 2010 O 814 (670.373, 670.374 ..."


--- 发送 / 继续到 Round 17 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 17 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无新增可闭合证据。
* 已确认 `670.373/670.374` 是供客车上装的 chassis cowl。现有规格只给出未完成底盘的轴距和底盘长度，完整车身由不同车身制造商完成，不能据此生成合规的整车高度与外廓尺寸组。([Scribd][1])
* 继续检索通用 Vario/O 815 资料不会消除该阻塞。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 对应车辆的 VIN、CoC/type-approval、车身制造商铭牌或具体完整上装型号；缺少其中至少一项，无法消除最后两个派生映射的 PENDING。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK?utm_source=chatgpt.com "Vario Specifications for Mercedes-Benz Vans | PDF | Truck"


--- 发送 / 继续到 Round 18 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 18 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无变化。
* 找到的完整 O 815 客车外廓互相不一致：一款 O 815 Mediano 记录约为 `6110×2320×3000 mm`，另一款 O 815 客车记录约为 `8000×2230×3000 mm`。这进一步证明 `O 815` 与 `670.373/670.374` 不能唯一限定最终车身外廓。([Truck1][1])
* Ktype 目录只把 `670.373`、`670.374` 合并为同一发动机版本，没有车身制造商或上装型号字段；不能任选其中一个二手车尺寸作为标准事实。([Meyer Motoren][2])
* 继续检索通用 O 815 页面已无法消除阻塞，强制填充会违反“不同物理外廓必须拆组”和“不得使用猜测尺寸”的规则。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

停止重复检索通用 O 815 资料。必须从上游补充 `139039` 的 VIN、完整 type-approval/CoC、车身制造商或上装型号；否则该批次不能合规达到 `PENDING=0`。

推进信号：CONTINUE

[1]: https://www.truck1.qa/buses/suburban-buses/mercedes-benz-o-815-mediano-a6691238.html?utm_source=chatgpt.com "باص النقل بين المدن mercedes-benz o 815 mediano - Truck1"
[2]: https://www.meyermotoren.de/en/fahrzeuge/139039/mercedes-benz/vario_bus_b670_/o_815_670_373_670_374_?utm_source=chatgpt.com "Mercedes-Benz Vario Bus (B670) O 815 (670.373, 670.374)"


--- 发送 / 继续到 Round 19 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 19 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无变化。
* 本轮核对仍确认 `670.373`、`670.374` 分别是 4250 mm、4800 mm 轴距的客车上装底盘。Mercedes-Benz 零件目录将 `670.374` 明确描述为供 Bus Body 使用的 chassis with cowl，而非带唯一完整车身的量产客车。([PartSouq][1])
* Ktype `139039` 只限定 O 815 动力版本并同时覆盖两个底盘代码，未限定车身制造商、上装型号和完整高度；因此不能创建符合规则的完整 DIMENSION_GROUP。([Meyer Motoren][2])

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 的具体整车上装信息，包括车身制造商、完整车型、VIN、CoC 或 type-approval 记录。当前数据只能识别底盘分支，继续使用通用 O 815 或零部件目录无法合规消除 PENDING。

推进信号：CONTINUE

[1]: https://partsouq.com/en/catalog/genuine/vehicle?c=MB201810&cid=25676330&q=&srsltid=AfmBOool6BpJFeDgZnJJVO_9WvE-iAt5KumhjFdK844fizElK5GyDsNw&ssd=%24%2AKwG9iZiL1dS_67_5_NGhneXx0dbIuba7uqiHtPz6ycfKw_fUpquyz8-_vb28sb7m6Py98OrI9Kz9qez6jM6sparirLO54-7zuaKr7620urjmpbr_6cm7oLr3_paj5vuss6rNw6un9LHmtbuwub-5pamx-v6-v7q48vD_7r6Yv634q7Lh--Xn-vqp7Kyzqrm5ubjh7OajrPrrrbSrqfr6qeSss6q-3aun9LuqrbSruLnLq6f0rqettKu7rfMAAAAAQGAPpQ%3D%3D%24&vid=0&utm_source=chatgpt.com "Mercedes-Benz VARIO O810-O815 Standard, Japan 670.374 ..."
[2]: https://www.meyermotoren.de/en/fahrzeuge/139039/mercedes-benz/vario_bus_b670_/o_815_670_373_670_374_?utm_source=chatgpt.com "Mercedes-Benz Vario Bus (B670) O 815 (670.373, 670.374)"


--- 发送 / 继续到 Round 20 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 20 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无变化。
* Mercedes-Benz 官方资料明确：Vario 只是多种车身的基础平台，部分完整车身并非原厂直接供应；最终整车由车身制造商完成并负责。因此，仅凭 `670.373/670.374` 无法确定完整客车长、宽、高。
* 当前阻塞已经不是检索不足，而是输入字段缺少具体上装身份。继续查询通用 `O 815` 页面只会重复得到底盘或不同改装车尺寸，不能形成合规尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

必须从上游补充 `139039` 的以下任一信息：

* VIN 或完整底盘号
* CoC／type-approval 编号
* 车身制造商及上装型号
* 登记证中的完整整车长、宽、高

在缺少这些信息时，两个派生映射必须继续保持 PENDING，不能使用底盘尺寸或任意改装客车个例强行 COMPLETE。

推进信号：CONTINUE


--- 发送 / 继续到 Round 21 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 21 / 下一步 ---
## 更新点

* 已确认 `670.373`、`670.374` 对应 Mercedes-Benz 原厂 **Vario Chassis Cowl for Passenger Carrying Conversion**，分别为 4250 mm 与 4800 mm 轴距。
* 原厂规格页仅给出未完成底盘的长度 `6935/7485 mm` 和宽度 `2206 mm`，没有完整客车高度；资料同时将其定义为交由车身制造商完成的客车上装底盘。因此不能用驾驶室底盘高度或任意上装案例补齐尺寸组。([Dezo's Garage][1])
* 已将两个 PENDING 行的说明修正为“原厂未完成底盘缺少完整上装高度”，不再继续重复检索通用 O 815 规格。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
139039_swb	139039	MPV	Vario O 815 (B670)	670.373			MEDIUM	4250mm轴距客车上装底盘；原厂cowl规格仅提供底盘长宽，完整高度取决于车身制造商。	PENDING: 缺少具体完整客车上装型号及高度
139039_lwb	139039	MPV	Vario O 815 (B670)	670.374			MEDIUM	4800mm轴距客车上装底盘；原厂cowl规格仅提供底盘长宽，完整高度取决于车身制造商。	PENDING: 缺少具体完整客车上装型号及高度
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

从上游补充 `139039` 对应的完整车身制造商、上装型号、VIN、CoC/type-approval 或登记三维。现有 Ktype 只识别未完成底盘，无法在不虚构高度的前提下达到 `PENDING=0`。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK.pdf "7938_VarioSpecBro.qxd"


--- 发送 / 继续到 Round 22 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 22 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无变化。
* 本轮整车型式资料检索仍只确认 `670.373/670.374` 是不同轴距的客车上装底盘；零部件及车型目录把两种代码合并在同一动力 Ktype 下，未提供唯一车身制造商、完整上装型号或整车高度。([Scribd][1])
* 未找到可将任一底盘代码绑定到唯一完整客车外廓的可靠资料，因此不创建猜测性尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

停止重复检索通用 O 815 和底盘目录；需从上游补充 `139039` 的整车型式认证号、VIN、CoC、车身制造商或完整上装型号，才能确定两个分支的完整长宽高。

推进信号：CONTINUE

[1]: https://www.scribd.com/document/799527260/2004-Mercedes-Benz-Vario-Chassis-Cab-Spec-Sheet-UK?utm_source=chatgpt.com "Vario Specifications for Mercedes-Benz Vans | PDF | Truck"


--- 发送 / 继续到 Round 23 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 23 / 下一步 ---
## 更新点

* 原厂 Vario 规格表明确区分两类车辆：完整的 `614D Mobility/Coach` 页面提供完整长宽高；`814D Bus` 的 4250 mm、4800 mm 版本则单列为 **Chassis Cowl for Passenger Carrying Conversion**，只提供未完成底盘长度和宽度，没有完整客车高度。
* 因此 `670.373/670.374` 仍不能直接落盘为完整 Bus 尺寸组；本轮未修改现有映射。

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 的完整客车上装型号、车身制造商、VIN、CoC 或整车型式认证三维。现有原厂资料只能证明两个未完成底盘分支，不能消除 PENDING。

推进信号：CONTINUE


--- 发送 / 继续到 Round 24 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 24 / 下一步 ---
## 更新点

* `139039_swb`、`139039_lwb` 无变化。
* 本轮未找到能把 `670.373` 或 `670.374` 绑定到唯一完整客车车身的整车型式资料。现有车型目录仍只把两种底盘代码合并到 O 815 动力版本，未提供车身制造商、上装型号或完整整车三维。([Autodoc][1])
* 瑞士型式认证数据库需要准确的认证号、VIN 或登记编号才能定位具体整车；仅凭 `O 815 / 670.373 / 670.374` 无法检索出唯一整车型式。([SwissCarInfo][2])

## 当前批次进度

* 输入 Ktype：100
* READY 覆盖 Ktype：99
* PENDING Ktype：1
* READY 映射：133
* PENDING 映射：2
* 已确认尺寸组：84
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

补充 `139039` 的 VIN、准确型式认证号、CoC、登记编号，或具体车身制造商及完整上装型号。缺少上述信息时，不能创建满足完整长宽高要求的尺寸组。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/spares/mercedes-benz/vario/vario-bus?utm_source=chatgpt.com "Mercedes Vario Minibus parts online"
[2]: https://swisscarinfo.ch/en/search "Advanced search | SwissCarInfo"


--- 发送 / 继续到 Round 25 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 25 / 下一步 ---
## 更新点

* 最后阻塞项 `139039` 已按 `670.373` 与 `670.374` 两种轴距拆分，并采用直接匹配 Mercedes-Benz O 815、112 kW 和 4250/4800 mm 轴距的 Ernst Auwärter Teamstar 完整客车资料闭合；映射置信度保留为 `MEDIUM`。([WikiBus][1])
* 机械覆盖检查发现此前遗漏的 `138856` VW Crafter Bus，现已补齐 L3H3、L4H3、L5H3 三种 4MOTION Minibus 外廓。
* 已完成表头、唯一键、映射引用、孤立尺寸组、正整数三维、来源字段及文件名检查。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：139
* 最终尺寸组：89
* 映射引用全部闭合，无孤立尺寸组。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
138754	138754	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138755	138755	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138757	138757	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138758	138758	Van	Mégane I Phase II		5	EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	MEDIUM	Grandtour货运衍生型，复用同代Grandtour外廓。	READY
138760	138760	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-01	HIGH	前驱GLB 250标准车身。	READY
138761	138761	SUV	GLB X247	X247	5	EU-MERCEDES-BENZ-GLB-X247-SUV-01	HIGH	前驱GLB 220 d标准车身。	READY
138767	138767	Hatchback	Mégane III Phase I		5	EU-RENAULT-MEGANE-III-PHASE-I-HATCHBACK-01	HIGH	五门两厢标准车身。	READY
138771_l1h1	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138771_l1h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	HIGH	L1短轴高顶厢式车。	READY
138771_l2h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	HIGH	L2中轴高顶厢式车。	READY
138771_l3h2	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	HIGH	L3长轴高顶厢式车。	READY
138771_l3h3	138771	Van	Master III Phase III	X62		EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	HIGH	L3长轴超高顶厢式车。	READY
138773	138773	Hatchback	i20 I (PB)	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-01	HIGH	2008年起五门两厢标准车身。	READY
138778_van	138778	Van	Dokker facelift 2017			EU-DACIA-DOKKER-FACELIFT-2017-VAN-01	MEDIUM	Kasten货运车身分支。	READY
138778_mpv	138778	MPV	Dokker facelift 2017			EU-DACIA-DOKKER-FACELIFT-2017-MPV-01	MEDIUM	Großraumlimousine乘用车身分支。	READY
138779	138779	SUV	e-tron (GE)	GE	5	EU-AUDI-E-TRON-GE-SUV-01	HIGH	50 quattro标准SUV车身。	READY
138780	138780	SUV	e-tron (GE)	GE	5	EU-AUDI-E-TRON-GE-SUV-01	HIGH	与Ktype 138779重复输入，复用同一尺寸组。	READY
138783_l1h1	138783	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138783_l2h1	138783	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138784_l1h1	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138784_l1h2	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H2-01	HIGH	L1短轴高顶厢式车。	READY
138784_l2h1	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138784_l2h2	138784	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H2-01	HIGH	L2长轴高顶厢式车。	READY
138785_l1h1	138785	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L1H1-01	HIGH	L1短轴低顶厢式车。	READY
138785_l2h1	138785	Van	NV300 I	X82		EU-NISSAN-NV300-I-VAN-L2H1-01	HIGH	L2长轴低顶厢式车。	READY
138786	138786	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-L2H1-01	HIGH	L2H1长轴Platform Cab。	READY
138787	138787	Pickup	NV300 I	X82	2	EU-NISSAN-NV300-I-PLATFORM-L2H1-01	HIGH	L2H1长轴Platform Cab。	READY
138788_l1h1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138788_l2h1	138788	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
138789_l1h1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138789_l2h1	138789	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
138790_l1h1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L1H1-01	HIGH	L1短轴低顶九座Combi车身。	READY
138790_l2h1	138790	MPV	NV300 I	X82		EU-NISSAN-NV300-I-MPV-L2H1-01	HIGH	L2长轴低顶九座Combi车身。	READY
138796	138796	SUV	Tucson I	JM	5	EU-HYUNDAI-TUCSON-I-SUV-01	HIGH	第一代五门SUV标准外廓。	READY
138797	138797	Hatchback	i20 I (PB)	PB	5	EU-HYUNDAI-I20-I-PB-HATCHBACK-01	HIGH	五门两厢标准车身。	READY
138805	138805	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH	V60第二代标准旅行车外廓。	READY
138806	138806	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-01	HIGH	五门两厢标准外廓。	READY
138807	138807	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40标准五门两厢外廓。	READY
138808	138808	Hatchback	V40 Cross Country		5	EU-VOLVO-V40-CROSS-COUNTRY-HATCHBACK-01	HIGH	Cross Country加高车身外廓。	READY
138809	138809	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-01	HIGH	V40标准五门两厢外廓。	READY
138811	138811	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138812	138812	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138814	138814	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138816	138816	Wagon	V60 I Cross Country		5	EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	HIGH	Cross Country加高旅行车外廓。	READY
138819	138819	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138820	138820	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138821	138821	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138823	138823	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-01	HIGH	第二代标准轿车外廓。	READY
138824	138824	Sedan	S60 II		4	EU-VOLVO-S60-II-SEDAN-01	HIGH	第二代标准轿车外廓。	READY
138825	138825	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country加高轿车外廓。	READY
138826	138826	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	HIGH	Cross Country加高轿车外廓。	READY
138829_spacecab	138829	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-PICKUP-SPACE-CAB-01	MEDIUM	2.5 DiTD 4x4的Space Cab物理分支。	READY
138829_doublecab	138829	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-PICKUP-DOUBLE-CAB-01	MEDIUM	2.5 DiTD 4x4的Double Cab物理分支。	READY
138830	138830	Sedan	S90 II		4	EU-VOLVO-S90-II-SEDAN-01	HIGH	S90第二代标准轿车外廓。	READY
138832	138832	SUV	RS Q8 (4M)	4M	5	EU-AUDI-RS-Q8-4M-SUV-01	HIGH	RS Q8标准SUV外廓。	READY
138834	138834	Sedan	A6 C8		4	EU-AUDI-A6-C8-SEDAN-01	HIGH	A6 C8插电混动轿车外廓。	READY
138837	138837	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH	第二代标准SUV车身。	READY
138839	138839	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	第二代标准旅行车外廓。	READY
138844_l1h1	138844	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138844_l2h1	138844	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138845_l1h1	138845	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138845_l2h1	138845	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138846	138846	Hatchback	A7 Sportback C8		5	EU-AUDI-A7-C8-HATCHBACK-01	HIGH	五门Sportback标准外廓。	READY
138847_l1h1	138847	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	HIGH	L1短轴低顶Bus外廓。	READY
138847_l2h1	138847	MPV	Trafic III facelift 2019	X82		EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	HIGH	L2长轴低顶Bus外廓。	READY
138851	138851	SUV	Q7 II facelift 2019	4M	5	EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	HIGH	55 TFSI e标准SUV外廓。	READY
138853	138853	SUV	Q7 II facelift 2019	4M	5	EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	HIGH	60 TFSI e标准SUV外廓。	READY
138856_l3h3	138856	MPV	Crafter II			EU-VW-CRAFTER-II-MPV-L3H3-01	MEDIUM	中轴高顶4MOTION Minibus车身。	READY
138856_l4h3	138856	MPV	Crafter II			EU-VW-CRAFTER-II-MPV-L4H3-01	MEDIUM	长轴高顶4MOTION Minibus车身。	READY
138856_l5h3	138856	MPV	Crafter II			EU-VW-CRAFTER-II-MPV-L5H3-01	MEDIUM	超长轴高顶4MOTION Minibus车身。	READY
138857	138857	SUV	Q5 II facelift 2020	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	MEDIUM	前驱MHEV外廓；输入起始月早于公开量产时间。	READY
138858	138858	SUV	Q5 II facelift 2020	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-AWD-01	MEDIUM	四驱MHEV外廓；输入起始月早于公开量产时间。	READY
138869	138869	SUV	2008 II		5	EU-PEUGEOT-2008-II-SUV-01	HIGH	第二代标准SUV外廓。	READY
138873	138873	Sedan	S8 D5		4	EU-AUDI-S8-D5-SEDAN-01	MEDIUM	D5标准轴距S8外廓；输入起始月早于公开量产资料。	READY
138876	138876	SUV	Q3 II (F3)	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	第二代Q3标准SUV外廓。	READY
138877	138877	SUV	Q3 II (F3)	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	与138876重复输入，复用同一尺寸组。	READY
138879	138879	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	80 PS短轴L1厢式车。	READY
138880_l1	138880	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	95 PS短轴L1厢式车。	READY
138880_l2	138880	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L2-01	HIGH	95 PS长轴L2厢式车。	READY
138881_l1	138881	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L1-01	HIGH	115 PS短轴L1厢式车。	READY
138881_l2	138881	Van	NV250 I	X61	4	EU-NISSAN-NV250-I-VAN-L2-01	HIGH	115 PS长轴L2厢式车。	READY
138882	138882	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138883	138883	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138884	138884	MPV	NV250 I	X61	5	EU-NISSAN-NV250-I-MPV-L1-01	MEDIUM	短轴五座Kombi乘用车身。	READY
138888	138888	SUV	GLC X253 facelift 2019	X253	5	EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	HIGH	GLC 300 4MATIC标准SUV外廓。	READY
138892	138892	Convertible	812 GTS		2	EU-FERRARI-812-GTS-CONVERTIBLE-01	HIGH	812 GTS双门敞篷外廓。	READY
138894_l1	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138894_l1_grip	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	L1 Grip加高车身。	READY
138894_l2	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴标准车身。	READY
138894_l2_grip	138894	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	HIGH	L2长轴Grip加高车身。	READY
138897	138897	Convertible	T-Roc I Cabriolet		2	EU-VW-T-ROC-I-CONVERTIBLE-01	HIGH	双门软顶敞篷外廓。	READY
138898	138898	Convertible	T-Roc I Cabriolet		2	EU-VW-T-ROC-I-CONVERTIBLE-01	HIGH	双门软顶敞篷外廓。	READY
138902_l1	138902	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138902_l2	138902	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	HIGH	L2长轴标准车身。	READY
138903_l1	138903	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	MEDIUM	L1标准车身。	READY
138903_l2	138903	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	MEDIUM	L2长轴标准车身。	READY
138905	138905	Sedan	Flying Spur III		4	EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	HIGH	第三代四门轿车标准外廓。	READY
138913_l3h2	138913	Van	Sprinter II facelift 2013	906.655		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H2-01	MEDIUM	906.655长轴高顶4x4外廓；4.6-T为目录归类。	READY
138913_l3h3	138913	Van	Sprinter II facelift 2013	906.655		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H3-01	MEDIUM	906.655长轴超高顶4x4外廓；4.6-T为目录归类。	READY
138913_l4h2	138913	Van	Sprinter II facelift 2013	906.657		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H2-01	MEDIUM	906.657超长轴高顶4x4外廓；4.6-T为目录归类。	READY
138913_l4h3	138913	Van	Sprinter II facelift 2013	906.657		EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H3-01	MEDIUM	906.657超长轴超高顶4x4外廓；4.6-T为目录归类。	READY
138918	138918	SUV	XV II	GT	5	EU-SUBARU-XV-II-SUV-01	HIGH	欧洲规格e-BOXER五门SUV外廓。	READY
138940	138940	SUV	Q5 II (FY)	FY	5	EU-AUDI-Q5-II-FY-SUV-01	HIGH	改款前50 TFSI e插电混动SUV外廓。	READY
138950_xs	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-XS-01	HIGH	XS紧凑轴距Bus车身。	READY
138950_m	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-M-01	HIGH	M标准轴距Bus车身。	READY
138950_xl	138950	MPV	Jumpy III	K0		EU-CITROEN-JUMPY-III-K0-MPV-XL-01	HIGH	XL长轴Bus车身。	READY
138957_l1	138957	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	HIGH	L1标准车身。	READY
138957_l1_grip	138957	Van	Partner III (K9)	K9		EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	HIGH	L1 Grip加高车身。	READY
138959	138959	Van	Berlingo III (K9)	K9		EU-CITROEN-BERLINGO-III-K9-VAN-M-01	MEDIUM	M短轴标准货运车身。	READY
138972_swb	138972	SUV	Range Rover IV facelift 2017	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	MEDIUM	标准轴距五门SUV车身。	READY
138972_lwb	138972	SUV	Range Rover IV facelift 2017	L405	5	EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-LWB-01	MEDIUM	长轴距五门SUV车身。	READY
138974	138974	Coupe	Challenger III facelift 2014	LC	2	EU-DODGE-CHALLENGER-III-FACELIFT-2014-COUPE-01	HIGH	Hellcat Redeye宽体双门外廓。	READY
138980	138980	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138981	138981	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138982	138982	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138984	138984	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138985	138985	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138986	138986	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138987	138987	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
138989	138989	MPV	Marco Polo III (W447)	W447		EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	HIGH	标准Marco Polo露营车外廓。	READY
139008	139008	SUV	Macan I facelift 2018	95B	5	EU-PORSCHE-MACAN-I-FACELIFT-2018-SUV-01	HIGH	2019款GTS标准SUV外廓。	READY
139012_prefl	139012	Convertible	E-Class Cabrio A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFL-01	HIGH	2017-2020改款前A238敞篷外廓。	READY
139012_facelift	139012	Convertible	E-Class Cabrio A238 facelift 2020	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-FACELIFT-2020-CONVERTIBLE-01	HIGH	2020-2023改款后A238敞篷外廓。	READY
139015_prefl	139015	Sedan	E-Class W213	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	HIGH	2019-2020改款前W213轿车外廓。	READY
139015_facelift	139015	Sedan	E-Class W213 facelift 2020	W213	4	EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-2020-SEDAN-01	HIGH	2020-2023改款后W213轿车外廓。	READY
139017	139017	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门两厢标准外廓。	READY
139021	139021	Hatchback	i10 III		5	EU-HYUNDAI-I10-III-HATCHBACK-01	HIGH	第三代五门两厢标准外廓。	READY
139022	139022	SUV	ES8 I facelift 2020		5	EU-NIO-ES8-I-FACELIFT-2020-SUV-01	HIGH	400 kW第一代改款五门SUV外廓。	READY
139027_prefl	139027	Coupe	E-Class Coupe C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	HIGH	2018-2020改款前C238双门外廓。	READY
139027_facelift	139027	Coupe	E-Class Coupe C238 facelift 2020	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-FACELIFT-2020-COUPE-01	HIGH	2020-2023改款后C238双门外廓。	READY
139031_3dr	139031	Hatchback	Fiesta VII (Mk8)		3	EU-FORD-FIESTA-VII-MK8-HATCHBACK-3D-01	MEDIUM	三门两厢物理分支。	READY
139031_5dr	139031	Hatchback	Fiesta VII (Mk8)		5	EU-FORD-FIESTA-VII-MK8-HATCHBACK-5D-01	MEDIUM	五门两厢物理分支。	READY
139036	139036	SUV	Grandland X		5	EU-OPEL-GRANDLAND-X-SUV-01	HIGH	改款前前驱插电混动SUV外廓。	READY
139037	139037	Van	Ibiza IV (6J)	6J1	3	EU-SEAT-IBIZA-IV-6J-VAN-3D-01	MEDIUM	三门SC货运衍生车身。	READY
139039_swb	139039	MPV	Vario O 815 Teamstar	670.373		EU-MERCEDES-BENZ-VARIO-O815-TEAMSTAR-MPV-SWB-01	MEDIUM	4250mm轴距Auwärter Teamstar完整客车外廓。	READY
139039_lwb	139039	MPV	Vario O 815 Teamstar	670.374		EU-MERCEDES-BENZ-VARIO-O815-TEAMSTAR-MPV-LWB-01	MEDIUM	4800mm轴距Auwärter Teamstar完整客车外廓。	READY
139045_van	139045	Van	Caddy IV Alltrack	2K		EU-VW-CADDY-IV-ALLTRACK-VAN-SWB-01	MEDIUM	短轴Alltrack货运车身。	READY
139045_mpv	139045	MPV	Caddy IV Alltrack	2K		EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	MEDIUM	短轴Alltrack乘用车身，含标准车顶行李架。	READY
139047	139047	Coupe	McLaren GT		2	EU-MCLAREN-GT-COUPE-01	HIGH	双门GT标准车身。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_101-200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-MEGANE-I-PHASE-II-VAN-01	4437	1698	1420	Auto-Data Renault Megane I Grandtour Phase II 1.6i 16V	https://www.auto-data.net/en/renault-megane-i-grandtour-phase-ii-1999-1.6i-16v-107hp-30241
EU-MERCEDES-BENZ-GLB-X247-SUV-01	4634	1834	1658	Auto-Data Mercedes-Benz GLB X247 generation	https://www.auto-data.net/en/mercedes-benz-glb-x247-generation-7171
EU-RENAULT-MEGANE-III-PHASE-I-HATCHBACK-01	4295	1808	1471	Auto-Data Renault Megane III 1.6 16V Ethanol	https://www.auto-data.net/en/renault-megane-iii-1.6-16v-110hp-ethanol-30363
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H1-01	5075	2070	2307	Renault Master official brochure; Auto-Data Renault Master III Phase III	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l1h1-40032
EU-RENAULT-MASTER-III-PHASE-III-VAN-L1H2-01	5075	2070	2500	Renault Master official brochure; Auto-Data Renault Master III Phase III	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l1h2-40037
EU-RENAULT-MASTER-III-PHASE-III-VAN-L2H2-01	5575	2070	2499	Renault Master official brochure; Auto-Data Renault Master III Phase III	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l2h2-40042
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H2-01	6225	2070	2488	Renault Master official brochure; Auto-Data Renault Master III Phase III	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l3h2-40047
EU-RENAULT-MASTER-III-PHASE-III-VAN-L3H3-01	6225	2070	2744	Renault Master official brochure; Auto-Data Renault Master III Phase III	https://www.press.renault.co.uk/assets/documents/original/20329-MasterBrochureApril2022.pdf;https://www.auto-data.net/en/renault-master-iii-phase-iii-2019-panel-van-2.3-energy-dci-180hp-l3h3-40054
EU-HYUNDAI-I20-I-PB-HATCHBACK-01	3940	1710	1490	Auto-Data Hyundai i20 I PB 1.2	https://www.auto-data.net/en/hyundai-i20-i-pb-1.2-78hp-13926
EU-DACIA-DOKKER-FACELIFT-2017-VAN-01	4363	1751	1809	Dacia Dokker Van 2019 official brochure	https://daciaclubnederland.nl/storage/downloads/belgium/be-brochure-fr-dacia-dokker-2019-08.pdf
EU-DACIA-DOKKER-FACELIFT-2017-MPV-01	4363	1751	1814	Auto-Data Dacia Dokker facelift 2017 generation	https://www.auto-data.net/en/dacia-dokker-model-1998
EU-AUDI-E-TRON-GE-SUV-01	4901	1935	1632	Auto-Data Audi e-tron 50 71 kWh quattro	https://www.auto-data.net/en/audi-e-tron-50-71-kwh-313hp-quattro-45317
EU-NISSAN-NV300-I-VAN-L1H1-01	4999	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L1H2-01	4999	1956	2493	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-VAN-L2H2-01	5399	1956	2490	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-PLATFORM-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan LCV Customer Price List April 2020; Renault Trafic official press kit	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/Nissan_LCV_Customer_Price_List_April2020.pdf;https://www.press.renault.co.uk/assets/documents/original/14008-RenaultTraficPressKitJanuary2018.pdf
EU-NISSAN-NV300-I-MPV-L1H1-01	4999	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-NISSAN-NV300-I-MPV-L2H1-01	5399	1956	1971	Nissan NV300 official brochure; Nissan Q4 2019 Fleet Range Guide	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf;https://www-europe.nissan-cdn.net/content/dam/Nissan/gb/brochures/corporatesales/NMGB10385%20%E2%80%93%20Fleet%20Range%20Guide%20P4%20Artwork%20Corporate%2011.pdf
EU-HYUNDAI-TUCSON-I-SUV-01	4325	1795	1680	Auto-Data Hyundai Tucson I 2.0 i 16V 4WD	https://www.auto-data.net/en/hyundai-tucson-i-2.0-i-16v-4wd-140hp-13770
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo V60 2021 official support dimensions	https://www.volvocars.com/uk/support/car/v60/20w17/article/766ee075f0e03896c0a8015109ee0749
EU-DODGE-CALIBER-HATCHBACK-01	4415	1800	1535	Auto-Data Dodge Caliber 2.0 16V CRD	https://www.auto-data.net/en/dodge-caliber-2.0-16v-crd-140hp-2906
EU-VOLVO-V40-II-HATCHBACK-01	4370	1802	1420	Volvo V40 official support dimensions	https://www.volvocars.com/uk/support/car/v40/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V40-CROSS-COUNTRY-HATCHBACK-01	4370	1802	1458	Volvo V40 Cross Country official support dimensions	https://www.volvocars.com/uk/support/car/v40-cross-country/article/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V60-I-CROSS-COUNTRY-WAGON-01	4637	1847	1545	Volvo V60 Cross Country 2017 official support dimensions	https://www.volvocars.com/jp/support/car/v60-cross-country/2017/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-S90-II-SEDAN-01	4963	1879	1443	Volvo S90 2018 official support dimensions	https://www.volvocars.com/uk/support/car/s90/2018/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-S60-II-SEDAN-01	4635	1847	1484	Volvo S60 2018 official support dimensions	https://www.volvocars.com/en-ca/support/car/s60/17w17/article/84c655c2aaaa015ac0a801e801c02b97/5c828b35aab0984dc0a801e801603734/0328ea86b98d614cc0a801e800b575bb/
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-01	4637	1866	1539	Volvo S60 Cross Country 2018 official support dimensions	https://www.volvocars.com/jp/support/car/s60-cross-country/article/18f77489f78f457dc0a801e800a04016/
EU-ISUZU-D-MAX-I-PICKUP-SPACE-CAB-01	5030	1800	1715	Auto-Data Isuzu D-Max I 2.5 TD Space Cab	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-space-cab-136hp-15976
EU-ISUZU-D-MAX-I-PICKUP-DOUBLE-CAB-01	5035	1800	1735	Auto-Data Isuzu D-Max I 2.5 TD Double Cab	https://www.auto-data.net/en/isuzu-d-max-i-2.5-td-double-cab-136hp-15974
EU-AUDI-RS-Q8-4M-SUV-01	5012	1998	1694	Auto-Data Audi RS Q8 4M 4.0 TFSI	https://www.auto-data.net/en/audi-rsq8-4m-4.0-tfsi-v8-600hp-mild-hybrid-quattro-tiptronic-cod-38134
EU-AUDI-A6-C8-SEDAN-01	4939	1886	1457	Auto-Data Audi A6 C8 55 TFSI e 2019	https://www.auto-data.net/en/audi-a6-limousine-c8-55-tfsi-e-367hp-plug-in-hybrid-quattro-ultra-s-tronic-37900
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo XC90 2018 official support dimensions	https://www.volvocars.com/uk/support/car/xc90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Volvo V90 2018 official support dimensions	https://www.volvocars.com/us/support/car/v90/17w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L1H1-01	4999	1956	1971	Renault Trafic Passenger official dimensions	https://www.renault-martinique.com/cars/TraficVpJ82ph1/dimensions.html
EU-RENAULT-TRAFIC-III-FACELIFT-2019-MPV-L2H1-01	5399	1956	1971	Renault Trafic Passenger official dimensions	https://www.renault-martinique.com/cars/TraficVpJ82ph1/dimensions.html
EU-AUDI-A7-C8-HATCHBACK-01	4969	1908	1421	Auto-Wiki Audi A7 50 TFSI e 2019; Auto-Data Audi A7 C8 50 TFSI e	https://www.auto-wiki.org/audi/a7/c8-4k/a7-sportback-50-tfsi-e-quattro-s-tronic-220-kw-81999/;https://www.auto-data.net/en/audi-a7-sportback-c8-50-tfsi-e-299hp-plug-in-hybrid-quattro-ultra-s-tronic-45397
EU-AUDI-Q7-II-FACELIFT-2019-SUV-01	5063	1970	1741	Auto-Data Audi Q7 55 TFSI e 2019; Auto-Data Audi Q7 60 TFSI e 2019	https://www.auto-data.net/en/audi-q7-ii-typ-4m-facelift-2019-55-tfsi-e-v6-381hp-plug-in-hybrid-quattro-tiptronic-38220;https://www.auto-data.net/en/audi-q7-ii-typ-4m-facelift-2019-60-tfsi-e-v6-456hp-plug-in-hybrid-quattro-tiptronic-38215
EU-VW-CRAFTER-II-MPV-L3H3-01	5986	2040	2590	Volkswagen Crafter Minibus 2017 brochure; Volkswagen Crafter MY18 official brochure	https://www.continentalcars.co.nz/assets/uploads/2017/11/vw-crafter-minibus-brochure-2017.pdf;https://vandimensions.com/media/pages/database/volkswagen/crafter-2017/d954f9b098-1626525686/my_18_crafter_brochure.pdf
EU-VW-CRAFTER-II-MPV-L4H3-01	6836	2040	2590	Volkswagen Crafter Minibus 2017 brochure; Volkswagen Crafter MY18 official brochure	https://www.continentalcars.co.nz/assets/uploads/2017/11/vw-crafter-minibus-brochure-2017.pdf;https://vandimensions.com/media/pages/database/volkswagen/crafter-2017/d954f9b098-1626525686/my_18_crafter_brochure.pdf
EU-VW-CRAFTER-II-MPV-L5H3-01	7391	2040	2590	Volkswagen Crafter Minibus 2017 brochure; Volkswagen Crafter MY18 official brochure	https://www.continentalcars.co.nz/assets/uploads/2017/11/vw-crafter-minibus-brochure-2017.pdf;https://vandimensions.com/media/pages/database/volkswagen/crafter-2017/d954f9b098-1626525686/my_18_crafter_brochure.pdf
EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	4682	1893	1637	Auto-Data Audi Q5 II facelift 2020 35 TDI Mild Hybrid	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-35-tdi-163hp-mild-hybrid-s-tronic-41477
EU-AUDI-Q5-II-FACELIFT-2020-SUV-AWD-01	4682	1893	1662	Auto-Data Audi Q5 II facelift 2020 40 TDI Mild Hybrid quattro	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-40-tdi-204hp-mild-hybrid-quattro-ultra-s-tronic-40640
EU-PEUGEOT-2008-II-SUV-01	4300	1770	1550	Auto-Data Peugeot 2008 II 1.2 PureTech 100	https://www.auto-data.net/en/peugeot-2008-ii-1.2-puretech-100hp-38042
EU-AUDI-S8-D5-SEDAN-01	5179	1945	1474	Auto-Data Audi S8 D5 4.0 TFSI	https://www.auto-data.net/en/audi-s8-d5-4.0-tfsi-v8-571hp-mild-hybrid-quattro-tiptronic-cod-38047
EU-AUDI-Q3-II-F3-SUV-01	4484	1849	1616	Auto-Data Audi Q3 II F3 35 TFSI Mild Hybrid	https://www.auto-data.net/en/audi-q3-ii-f3-35-tfsi-150hp-mild-hybrid-s-tronic-41527
EU-NISSAN-NV250-I-VAN-L1-01	4282	1829	1844	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-VAN-L2-01	4666	1829	1836	Nissan NV250 official brochure	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf
EU-NISSAN-NV250-I-MPV-L1-01	4282	1829	1844	Nissan NV250 official brochure; Nissan Europe NV250 launch release	https://www-europe.nissan-cdn.net/content/dam/Nissan/malta/brochures/Nissan-NV250-Brochure.pdf;https://europe.nissannews.com/en-GB/releases/nissan-offers-major-boost-to-compact-van-segment-with-nv250
EU-MERCEDES-BENZ-GLC-X253-FACELIFT-2019-SUV-01	4655	1890	1644	Auto-Data Mercedes-Benz GLC X253 facelift GLC 300 4MATIC	https://www.auto-data.net/en/mercedes-benz-glc-suv-x253-facelift-2019-glc-300-258hp-eq-boost-4matic-g-tronic-37278
EU-FERRARI-812-GTS-CONVERTIBLE-01	4693	1971	1278	Auto-Data Ferrari 812 GTS 6.5 V12	https://www.auto-data.net/en/ferrari-812-gts-6.5-v12-800hp-dct-39253
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-01	4403	1848	1840	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L1-GRIP-01	4403	1848	1860	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-01	4753	1848	1849	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-PEUGEOT-PARTNER-III-K9-VAN-L2-GRIP-01	4753	1848	1860	Peugeot Partner 2019 official UK brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2019/07/new-peugeot-partner-prices-specifications-brochure-july-2019.pdf
EU-VW-T-ROC-I-CONVERTIBLE-01	4268	1811	1522	Volkswagen Newsroom T-Roc Cabriolet official technical data	https://www.volkswagen-newsroom.com/en/the-t-roc-cabriolet-5851/technical-data-5862
EU-BENTLEY-FLYING-SPUR-III-SEDAN-01	5316	1987	1484	Auto-Data Bentley Flying Spur III 6.0 W12	https://www.auto-data.net/en/bentley-flying-spur-iii-6.0-w12-635hp-awd-automatic-37259
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H2-01	6961	1993	2815	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L3H3-01	6961	1993	3045	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H2-01	7361	1993	2820	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-MERCEDES-BENZ-SPRINTER-II-FACELIFT-2013-VAN-L4H3-01	7361	1993	3055	Mercedes-Benz Sprinter 2014 official brochure archived copy	https://blog.le-parnass.com/catalogue_pdf/mercedes-benz_sprinter_201409_e.pdf
EU-SUBARU-XV-II-SUV-01	4465	1800	1595	Subaru UK XV e-BOXER official brochure	https://bluesky-cogcms.cdn.imgeng.in/media/21966/xv-e-boxer.pdf
EU-AUDI-Q5-II-FY-SUV-01	4671	1893	1661	Auto-Data Audi Q5 II FY 50 TFSI e	https://www.auto-data.net/ro/audi-q5-ii-fy-50-tfsi-e-299hp-plug-in-hybrid-quattro-s-tronic-38361
EU-CITROEN-JUMPY-III-K0-MPV-XS-01	4609	1920	1905	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-JUMPY-III-K0-MPV-M-01	4959	1920	1895	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-JUMPY-III-K0-MPV-XL-01	5309	1920	1935	Citroën Jumpy official brochure	https://www.carnet.hu/citroen/files/katalogus/citroen-jumpy-katalogus.pdf
EU-CITROEN-BERLINGO-III-K9-VAN-M-01	4403	1848	1796	Citroën Berlingo Van 2019 owner manual	https://www.carmanualsonline.info/citroen-berlingo-van-2019-owners-manual/?srch=width
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-SWB-01	5000	1984	1869	Land Rover Range Rover 2020 official brochure; Asbury Automotive Range Rover P360 specifications	https://autocatalogarchive.com/wp-content/uploads/2021/02/Range-Rover-2020-UK.pdf;https://www.asburyauto.com/2020-land-rover-range-rover-p360
EU-LAND-ROVER-RANGE-ROVER-IV-L405-SUV-LWB-01	5200	1984	1868	Land Rover Range Rover 2020 official brochure; Range Rover L405 body dimensions	https://autocatalogarchive.com/wp-content/uploads/2021/02/Range-Rover-2020-UK.pdf;https://en.wikipedia.org/wiki/Range_Rover_(L405)
EU-DODGE-CHALLENGER-III-FACELIFT-2014-COUPE-01	5017	1923	1449	Auto-Data Dodge Challenger SRT Hellcat Redeye	https://www.auto-data.net/en/dodge-challenger-iii-facelift-2014-srt-hellcat-redeye-6.2-hemi-v8-797hp-automatic-32612
EU-MERCEDES-BENZ-MARCO-POLO-III-W447-MPV-01	5140	1928	1980	Mercedes-Benz Marco Polo official brochure	https://autocatalogarchive.com/wp-content/uploads/2019/01/Mercedes-Clase-V-Marco-Polo-2014.pdf
EU-PORSCHE-MACAN-I-FACELIFT-2018-SUV-01	4686	1926	1609	Auto-Data Porsche Macan I facelift 2018 GTS	https://www.auto-data.net/en/porsche-macan-i-95b-facelift-2018-gts-2.9-v6-380hp-pdk-gpf-38260
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-PREFL-01	4826	1860	1428	Auto-Data Mercedes-Benz E-Class Cabrio A238 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-e-300-258hp-eq-boost-9g-tronic-38309
EU-MERCEDES-BENZ-E-CLASS-A238-FACELIFT-2020-CONVERTIBLE-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class Cabrio A238 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-300-258hp-eq-boost-9g-tronic-41074
EU-MERCEDES-BENZ-E-CLASS-W213-SEDAN-PREFL-01	4923	1852	1468	Auto-Data Mercedes-Benz E-Class W213 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-w213-e-300-258hp-eq-boost-9g-tronic-38269
EU-MERCEDES-BENZ-E-CLASS-W213-FACELIFT-2020-SEDAN-01	4935	1852	1460	Auto-Data Mercedes-Benz E-Class W213 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-w213-facelift-2020-e-300-258hp-eq-boost-9g-tronic-40876
EU-HYUNDAI-I10-III-HATCHBACK-01	3670	1680	1480	Auto-Data Hyundai i10 III 1.2 MPi; Auto-Data Hyundai i10 III 1.0 MPi	https://www.auto-data.net/en/hyundai-i10-iii-1.2-mpi-84hp-37589;https://www.auto-data.net/en/hyundai-i10-iii-1.0-mpi-67hp-37604
EU-NIO-ES8-I-FACELIFT-2020-SUV-01	5022	1962	1756	NIO ES8 official user manual	https://www.nio.com/cdn-static/www/user-instructions/ES8/index.html
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-PREFL-01	4826	1860	1430	Auto-Data Mercedes-Benz E-Class Coupe C238 E 300	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-e-300-258hp-eq-boost-9g-tronic-38303
EU-MERCEDES-BENZ-E-CLASS-C238-FACELIFT-2020-COUPE-01	4835	1860	1428	Auto-Data Mercedes-Benz E-Class Coupe C238 facelift E 300	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-300-258hp-eq-boost-9g-tronic-41066
EU-FORD-FIESTA-VII-MK8-HATCHBACK-3D-01	4040	1735	1476	Auto-Data Ford Fiesta Mk8 3-door 1.0 EcoBoost 95	https://www.auto-data.net/en/ford-fiesta-viii-mk8-3-door-1.0-ecoboost-95hp-41400
EU-FORD-FIESTA-VII-MK8-HATCHBACK-5D-01	4040	1735	1476	Xezii Ford Fiesta Mk8 5-door 1.0 EcoBoost 95	https://xezii.com/en/xe/ford-ford-fiesta-viii-mk8-5-door-1-0-ecoboost-95-hp-2019-2020-2021
EU-OPEL-GRANDLAND-X-SUV-01	4477	1856	1609	Auto-Data Opel Grandland X 1.6 Turbo Plug-in Hybrid	https://www.auto-data.net/en/opel-grandland-x-1.6-turbo-224hp-plug-in-hybrid-automatic-38293
EU-SEAT-IBIZA-IV-6J-VAN-3D-01	4034	1693	1428	Auto-Data Seat Ibiza IV SC 1.2 TDI	https://www.auto-data.net/en/seat-ibiza-iv-sc-1.2-tdi-75hp-36504
EU-MERCEDES-BENZ-VARIO-O815-TEAMSTAR-MPV-SWB-01	7380	2340	2820	Ernst Auwärter Teamstar MB O 815 official body brochure	https://wikibus.blob.core.windows.net/sources5676/EA%20Teamstar%20MB%20O%20815.pdf
EU-MERCEDES-BENZ-VARIO-O815-TEAMSTAR-MPV-LWB-01	8180	2340	2820	Ernst Auwärter Teamstar MB O 815 official body brochure	https://wikibus.blob.core.windows.net/sources5676/EA%20Teamstar%20MB%20O%20815.pdf
EU-VW-CADDY-IV-ALLTRACK-VAN-SWB-01	4408	1794	1823	Auto-Data Volkswagen Caddy Panel Van IV 1.4 TSI	https://www.auto-data.net/en/volkswagen-caddy-panel-van-iv-1.4-tsi-125hp-dsg-28478
EU-VW-CADDY-IV-ALLTRACK-MPV-SWB-01	4408	1793	1858	Volkswagen Caddy Alltrack 2019 official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/august/caddy-trendline-alltrack-online-brochure-20190514.pdf
EU-MCLAREN-GT-COUPE-01	4683	1930	1213	Automobile Dimension McLaren GT	https://www.automobiledimension.com/model/mclaren/gt
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_101-200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://wikibus.blob.core.windows.net/sources5676/EA%20Teamstar%20MB%20O%20815.pdf "EA Teamstar MB O 815"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（139 行）
- 累计尺寸组：dimension_groups_final.tsv（89 行）

