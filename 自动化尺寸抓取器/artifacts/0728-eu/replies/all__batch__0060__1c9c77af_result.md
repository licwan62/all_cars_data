# 任务：all 第 5901-6000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0060__1c9c77af


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5901-6000 行

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
all 第 5901-6000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5901-6000_ktype_dimension_mapping_final.tsv
- all_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-CITROEN-NEMO-MULTISPACE-MPV-01	3959	1716	1721
EU-CITROEN-NEMO-PANEL-VAN-01	3864	1716	1721
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330
EU-FORD-CAPRI-II-COUPE-01	4286	1695	1295
EU-FORD-CAPRI-III-COUPE-01	4440	1700	1350
EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	4833	1817	1462
EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	4838	1817	1462
EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	4833	1817	1511
EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	4838	1817	1510
EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	4345	1686	1378
EU-VOLVO-440-K-HATCHBACK-PREFL-01	4312	1676	1379
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435
EU-VOLVO-760-SEDAN-FACELIFT-01	4790	1760	1410
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410
EU-VOLVO-760-WAGON-FACELIFT-01	4790	1760	1435
EU-VOLVO-760-WAGON-PREFL-01	4800	1750	1435
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425
EU-VOLVO-940-WAGON-5D-01	4871	1750	1435
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425
EU-VW-TRANSPORTER-T1-KASTEN-1955-57-01	4190	1725	1940
EU-VW-TRANSPORTER-T1-KASTEN-PRE55-01	4100	1700	1900
EU-VW-TRANSPORTER-T1-KASTEN-STANDARDROOF-01	4280	1750	1940
EU-VW-TRANSPORTER-T1-MPV-1955-57-01	4190	1725	1940
EU-VW-TRANSPORTER-T1-MPV-POST58-01	4280	1750	1940
EU-VW-TRANSPORTER-T1-MPV-PRE55-01	4100	1700	1900
EU-VW-TRANSPORTER-T2-MPV-FACELIFT-01	4505	1720	1960
EU-VW-TRANSPORTER-T2-MPV-PREFL-01	4420	1765	1960
EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	4505	1720	1960
EU-VW-TRANSPORTER-T2-VAN-PREFL-01	4420	1765	1955
EU-VW-TRANSPORTER-T3-BUS-RWD-01	4600	1845	1950
EU-VW-TRANSPORTER-T3-BUS-SYNCRO14-01	4600	1845	1990
EU-VW-TRANSPORTER-T3-BUS-SYNCRO16-01	4600	1865	2020
EU-VW-TRANSPORTER-T3-MPV-STANDARD-01	4600	1845	1950
EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	4570	1870	1925
EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	4570	1870	1930
EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	4636	2000	1930
EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	4570	1845	2365
EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	4570	1845	1965
EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	4570	1845	1990
EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	4570	1865	2020
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-LWB-01	5189	1840	1940
EU-VW-TRANSPORTER-T4-BUS-FACELIFT-SWB-01	4789	1840	1940
EU-VW-TRANSPORTER-T4-BUS-PREFL-LWB-01	5055	1840	1940
EU-VW-TRANSPORTER-T4-BUS-PREFL-SWB-01	4655	1840	1940
EU-VW-TRANSPORTER-T4-MPV-LWB-FACELIFT-01	5189	1840	1940
EU-VW-TRANSPORTER-T4-MPV-LWB-PREFL-01	5055	1840	1940
EU-VW-TRANSPORTER-T4-MPV-SWB-FACELIFT-01	4789	1840	1940
EU-VW-TRANSPORTER-T4-MPV-SWB-PREFL-01	4655	1840	1940

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
VW	Transporter t2	2	Kasten	Heckantrieb	Benzin	51	69	Aug 1976	Jul 1979	2024-03-01	6298
VW	Transporter t3	1.6	Kasten	Heckantrieb	Benzin	37	50	May 1979	Dec 1982	2024-03-01	6299
KIA	Sorento ii	2.0 Crdi	SUV	Frontantrieb	Diesel	110	150	Nov 2010	Dec 2015	2024-03-01	6300
VW	Transporter t3	1.9	Kasten	Heckantrieb	Benzin	57	78	Oct 1982	Jul 1992	2024-03-01	6301
KIA	Sorento ii	2.0 Crdi 4WD	SUV	Allrad	Diesel	110	150	Nov 2010	Dec 2015	2024-03-01	6302
VW	Transporter t3	1.6 TD	Kasten	Heckantrieb	Diesel	51	69	Oct 1984	Jul 1992	2024-03-01	6303
VW	Transporter t3	1.7 D	Kasten	Heckantrieb	Diesel	42	57	Aug 1984	Jul 1992	2024-03-01	6304
VW	Transporter t3	1.9 Syncro	Kasten	Allrad	Benzin	57	78	Nov 1984	Jul 1992	2024-03-01	6305
Skoda	Superb ii	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	147	200	May 2010	May 2015	2024-03-01	6306
VW	Transporter t3	2.1 Syncro	Kasten	Allrad	Benzin	82	112	Mar 1986	Jul 1992	2024-03-01	6307
VW	Transporter t3	1.6 TD Syncro	Kasten	Allrad	Diesel	51	69	Mar 1986	Jul 1992	2024-03-01	6308
VW	Transporter t3	2.1	Pritsche/Fahrgestell	Heckantrieb	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	6309
VW	Transporter t3	1.9 Syncro	Pritsche/Fahrgestell	Allrad	Benzin	57	78	Dec 1984	Jul 1992	2024-03-01	6310
VW	Transporter t3	2.1 Syncro	Pritsche/Fahrgestell	Allrad	Benzin	70	95	Aug 1985	Jul 1992	2024-03-01	6311
VW	Transporter t3	2.1 Syncro	Pritsche/Fahrgestell	Allrad	Benzin	82	112	Mar 1986	Jul 1992	2024-03-01	6312
VW	Transporter t3	1.6 TD Syncro	Pritsche/Fahrgestell	Allrad	Diesel	51	69	Mar 1986	Jul 1992	2024-03-01	6313
Skoda	Superb ii	1.6 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Sep 2010	May 2015	2024-03-01	6314
VW	Transporter t4	2	Kasten	Frontantrieb	Benzin	62	84	Jul 1990	Apr 2003	2024-03-01	6315
VW	Transporter t4	2.5	Kasten	Frontantrieb	Benzin	81	110	Nov 1990	Apr 2003	2024-03-01	6316
VW	Transporter t4	1.9 D	Kasten	Frontantrieb	Diesel	45	61	Jul 1990	Dec 1995	2024-03-01	6317
VW	Transporter t4	1.9 TD	Kasten	Frontantrieb	Diesel	50	68	Oct 1992	Apr 2003	2024-03-01	6318
VW	Transporter t4	2.4 D	Kasten	Frontantrieb	Diesel	57	78	Jul 1990	Apr 1998	2024-03-01	6319
VW	Transporter t4	2.5 Syncro	Kasten	Allrad	Benzin	81	110	Nov 1992	Nov 2001	2024-03-01	6320
VW	Transporter t4	2.4 D Syncro	Kasten	Allrad	Diesel	57	78	Oct 1992	Sep 1998	2024-03-01	6321
VW	Transporter t4	1.9 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	45	61	Jul 1990	Dec 1995	2024-03-01	6322
VW	Transporter t4	1.9 TD	Pritsche/Fahrgestell	Frontantrieb	Diesel	50	68	Oct 1992	Apr 2003	2024-03-01	6323
VW	Transporter t4	2.4 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	57	78	Sep 1990	Apr 1998	2024-03-01	6324
VW	Transporter t1	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	32	44	Jun 1966	Oct 1970	2024-03-01	6325
Skoda	Superb ii	2.0 Tfsi	Kombi	Frontantrieb	Benzin	147	200	May 2010	May 2015	2024-03-01	6326
Volvo	340-360	2	Stufenheck	Heckantrieb	Benzin	87	118	Aug 1984	Jul 1986	2024-03-01	6337
Volvo	340-360	2	Stufenheck	Heckantrieb	Benzin	82	112	Aug 1986	Jul 1988	2024-03-01	6338
Skoda	Superb ii	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Sep 2010	May 2015	2024-03-01	6339
Volvo	340-360	2	Stufenheck	Heckantrieb	Benzin	80	109	Aug 1988	Jul 1989	2024-03-01	6340
Volvo	340-360	2	Stufenheck	Heckantrieb	Benzin	81	110	Aug 1987	Jul 1988	2024-03-01	6341
VW	Transporter t3	1.6 D	Kasten	Heckantrieb	Diesel	37	50	Jan 1981	Jul 1987	2024-03-01	6342
Skoda	Yeti	1.6 TDI	SUV	Frontantrieb	Diesel	77	105	Nov 2010	May 2015	2024-03-01	6345
Ssangyong	Korando	2.0 E-xdi	SUV	Frontantrieb	Diesel	129	175	Nov 2010	-	2024-03-01	6346
Ssangyong	Korando	2.0 E-xdi 4WD	SUV	Allrad	Diesel	129	175	Nov 2010	-	2024-03-01	6347
Citroën	Ds4	1.6 VTI 120	Schrägheck	Frontantrieb	Benzin	88	120	Apr 2011	Jul 2015	2024-03-01	6348
Citroën	Ds4	1.6 THP 155	Schrägheck	Frontantrieb	Benzin	115	156	Apr 2011	Jul 2015	2024-03-01	6349
Volvo	460	1.7 Turbo	Stufenheck	Frontantrieb	Benzin	90	122	Jan 1991	Jul 1996	2024-03-01	6350
Volvo	440	1.7 Turbo	Schrägheck	Frontantrieb	Benzin	90	122	Jan 1991	Dec 1996	2024-03-01	6351
Volvo	Pv 544	1.6	Schrägheck	Heckantrieb	Benzin	44	60	Aug 1961	Jul 1966	2024-03-01	6352
Volvo	Pv 544	1.6	Schrägheck	Heckantrieb	Benzin	61	83	Aug 1961	Jul 1967	2024-03-01	6353
Volvo	Pv 544	1.8	Schrägheck	Heckantrieb	Benzin	59	80	Aug 1961	Jul 1967	2024-03-01	6354
Volvo	Pv 544	1.8	Schrägheck	Heckantrieb	Benzin	50	68	Aug 1961	Jul 1967	2024-03-01	6355
Volvo	940	2.4 Turbo Diesel	Stufenheck	Heckantrieb	Diesel	80	109	Aug 1990	Dec 1994	2024-03-01	6356
Volvo	S40 i	2	Stufenheck	Frontantrieb	Benzin	103	140	Jul 1995	Aug 1999	2024-03-01	6357
Volvo	V40	2	Kombi	Frontantrieb	Benzin	103	140	Jul 1995	Aug 1999	2024-03-01	6358
VW	Lt 28-35 i	2	Kasten	Heckantrieb	Benzin	55	75	Apr 1975	Sep 1983	2024-03-01	6359
Citroën	Ds4	1.6 THP 200	Schrägheck	Frontantrieb	Benzin	147	200	Apr 2011	Jul 2015	2024-03-01	6360
VW	Lt 28-35 i	2.4	Kasten	Heckantrieb	Benzin	66	90	Dec 1982	Jul 1992	2024-03-01	6361
VW	Lt 28-35 i	2.4 D	Kasten	Heckantrieb	Diesel	55	75	Jan 1979	Jul 1992	2024-03-01	6362
VW	Lt 28-35 i	2.4 TD	Kasten	Heckantrieb	Diesel	68	92	Aug 1988	Aug 1992	2024-03-01	6363
VW	Lt 28-35 i	2.4 TD	Kasten	Heckantrieb	Diesel	70	95	Jun 1992	May 1996	2024-03-01	6364
VW	Lt 28-35 i	2.4 TD	Kasten	Heckantrieb	Diesel	75	102	Feb 1986	Aug 1992	2024-03-01	6365
VW	Lt 28-35 i	2.4 D	Kasten	Heckantrieb	Diesel	51	69	Jul 1990	May 1996	2024-03-01	6366
VW	Transporter t3	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	51	69	May 1979	Apr 1986	2024-03-01	6367
VW	Lt 28-35 i	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	55	75	Apr 1975	Sep 1983	2024-03-01	6368
VW	Lt 28-35 i	2.4 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	68	92	Aug 1990	Aug 1992	2024-03-01	6369
VW	Lt 28-35 i	2.4 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	51	69	Aug 1990	Jun 1996	2024-03-01	6370
Citroën	Ds4	1.6 HDI 110	Schrägheck	Frontantrieb	Diesel	82	112	Apr 2011	Jul 2015	2024-03-01	6371
Volvo	940	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	140	190	Aug 1991	Jul 1993	2024-03-01	6372
Volvo	P 210 duett	1.8	Kombi	Heckantrieb	Benzin	55	75	Aug 1961	Jul 1967	2024-03-01	6376
Citroën	Ds4	2.0 HDI 165	Schrägheck	Frontantrieb	Diesel	120	163	Apr 2011	Jul 2015	2024-03-01	6377
Volvo	P 122 s amazon	1.8	Kombi	Heckantrieb	Benzin	59	80	Aug 1961	Jul 1967	2024-03-01	6378
Volvo	780	2.9	Coupe	Heckantrieb	Benzin	115	156	Aug 1986	Jul 1987	2024-03-01	6379
Volvo	780	2.9	Coupe	Heckantrieb	Benzin	108	147	Aug 1987	Jul 1990	2024-03-01	6380
Jeep	Wrangler iii	2.8 CRD	Geländewagen offen	Allrad	Diesel	147	200	Nov 2010	-	2024-03-01	6381
Citroën	Nemo	1.3 HDI 75	Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2010	-	2024-03-01	6382
Volvo	740	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	115	156	Aug 1986	Jul 1989	2024-03-01	6383
Volvo	740	2.3	Stufenheck	Heckantrieb	Benzin	86	117	Oct 1984	Jul 1988	2024-03-01	6385
Volvo	740	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	121	165	Aug 1989	Jul 1990	2024-03-01	6388
Volvo	740	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	140	190	Aug 1989	Jul 1990	2024-03-01	6389
Volvo	760	2.8	Stufenheck	Heckantrieb	Benzin	108	147	Aug 1986	Jul 1990	2024-03-01	6390
Alpina	D5	Biturbo	Kombi	Heckantrieb	Diesel	257	350	Sep 2011	Dec 2016	2024-03-01	6391
Volvo	760	2.3 Turbo	Stufenheck	Heckantrieb	Benzin	127	173	Aug 1982	Jul 1984	2024-03-01	6392
BMW	1500-2000	1500	Stufenheck	Heckantrieb	Benzin	59	80	Oct 1962	Jul 1966	2024-03-01	6393
BMW	1500-2000	1500	Stufenheck	Heckantrieb	Benzin	59	80	Sep 1963	Jul 1966	2024-03-01	6394
BMW	1500-2000	1600	Stufenheck	Heckantrieb	Benzin	61	83	Apr 1964	Apr 1968	2024-03-01	6395
BMW	1600	1.6	Coupe	Heckantrieb	Benzin	77	105	Oct 1967	May 1969	2024-03-01	6396
Smart	Fortwo	Electric Drive	Coupe	Heckantrieb	Elektro	20	27	Dec 2010	Dec 2012	2024-03-01	6397
BMW	1502-2002	1600 TI	Stufenheck	Heckantrieb	Benzin	77	105	Sep 1967	Nov 1969	2024-03-01	6398
BMW	1500-2000	1800	Stufenheck	Heckantrieb	Benzin	66	90	Aug 1963	Sep 1969	2024-03-01	6399
BMW	1500-2000	1800	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1969	Sep 1971	2024-03-01	6400
BMW	1500-2000	1800 TI	Stufenheck	Heckantrieb	Benzin	81	110	Oct 1963	Apr 1968	2024-03-01	6401
BMW	1500-2000	1800 TI	Stufenheck	Heckantrieb	Benzin	96	131	Oct 1963	Apr 1968	2024-03-01	6402
BMW	1500-2000	2000	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1970	Nov 1972	2024-03-01	6403
Smart	Fortwo cabrio	Electric Drive	Cabriolet	Heckantrieb	Elektro	20	27	Dec 2010	Dec 2012	2024-03-01	6404
BMW	1500-2000	2000 TII	Stufenheck	Heckantrieb	Benzin	96	131	Dec 1969	Jul 1972	2024-03-01	6405
BMW	1500-2000	2000 TI / Tilux	Stufenheck	Heckantrieb	Benzin	88	120	Jan 1966	Jul 1972	2024-03-01	6406
BMW	V8	2.6	Coupe	Heckantrieb	Benzin	81	110	Oct 1958	Nov 1961	2024-03-01	6407
BMW	V8	2600	Coupe	Heckantrieb	Benzin	81	110	Sep 1961	Dec 1964	2024-03-01	6408
BMW	V8	3.2	Coupe	Heckantrieb	Benzin	88	120	Nov 1958	Nov 1961	2024-03-01	6409
BMW	V8	3.2 Super	Coupe	Heckantrieb	Benzin	103	140	Nov 1958	Nov 1961	2024-03-01	6410
BMW	V8	3200 L	Coupe	Heckantrieb	Benzin	103	140	Sep 1961	Dec 1964	2024-03-01	6411
BMW	V8	3200 S	Coupe	Heckantrieb	Benzin	118	160	Sep 1961	Dec 1964	2024-03-01	6412
BMW	V8	3200 CS	Coupe	Heckantrieb	Benzin	118	160	Jul 1962	Jul 1966	2024-03-01	6413
BMW	503	3.2	Cabriolet	Heckantrieb	Benzin	103	140	Jan 1957	May 1961	2024-03-01	6414
Ford	Capri	1300	Coupe	Heckantrieb	Benzin	37	50	Dec 1968	Dec 1972	2025-02-03	6415


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 **36 个 Ktype** 的物理外廓映射，共新增 **48 行 READY 映射**。
* 直接复用跨批次已有尺寸组 **18 个**，未重复抓取或输出既有尺寸事实。
* 首次创建并闭合 **7 个尺寸组**：

  * Škoda Yeti 5L 改款前、改款后；
  * SsangYong Korando III C200；
  * Citroën DS4 I；
  * Volvo 780 Coupe；
  * Smart Fortwo II 451 Coupe、Cabriolet。
* Yeti 改款前后长度分别确认为 4223 mm 和 4222 mm，宽度和高度均为 1793 mm、1691 mm。
* DS4 采用官方历史 brochure 的 4275 × 1810 × 1523 mm；Korando C200、Smart ED2 和 Volvo 780 的尺寸组也已完成来源闭合。([ManualZilla][1])

## 当前批次进度

* 输入 Ktype：**100**
* 已完成 Ktype：**36**
* READY 映射行：**48**
* PENDING Ktype：**64**
* 当前已引用尺寸组：**25**

  * 复用已有组：18
  * 本轮首次建组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6298	6298	Van	Transporter T2			EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH		READY
6299_lowroof	6299	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6299_highroof	6299	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6301_lowroof	6301	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6301_highroof	6301	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6303_lowroof	6303	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6303_highroof	6303	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6304_lowroof	6304	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6304_highroof	6304	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6306_prefl	6306	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6306_facelift	6306	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6314_prefl	6314	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6314_facelift	6314	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6326_prefl	6326	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6326_facelift	6326	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6339_prefl	6339	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6339_facelift	6339	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6342_lowroof	6342	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6342_highroof	6342	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6345_prefl	6345	SUV	Yeti (5L)	5L	5	EU-SKODA-YETI-5L-SUV-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6345_facelift	6345	SUV	Yeti (5L)	5L	5	EU-SKODA-YETI-5L-SUV-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6346	6346	SUV	Korando III (C200)	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-01	HIGH		READY
6347	6347	SUV	Korando III (C200)	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-01	HIGH		READY
6348	6348	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6349	6349	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6350	6350	Sedan	460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
6351_prefl	6351	Hatchback	440	K	5	EU-VOLVO-440-K-HATCHBACK-PREFL-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6351_facelift	6351	Hatchback	440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6356	6356	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
6357	6357	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
6358	6358	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
6360	6360	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6371	6371	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6372	6372	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
6377	6377	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6379	6379	Coupe	780	780	2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
6380	6380	Coupe	780	780	2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
6382	6382	MPV	Nemo I			EU-CITROEN-NEMO-MULTISPACE-MPV-01	HIGH		READY
6383	6383	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6385	6385	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6388	6388	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6389	6389	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6390_prefl	6390	Sedan	760	764	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6390_facelift	6390	Sedan	760	764	4	EU-VOLVO-760-SEDAN-FACELIFT-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6392	6392	Sedan	760	764	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH		READY
6397	6397	Coupe	Fortwo II (451)	C451	2	EU-SMART-FORTWO-II-C451-COUPE-01	HIGH		READY
6404	6404	Convertible	Fortwo II (451)	A451	2	EU-SMART-FORTWO-II-A451-CONVERTIBLE-01	HIGH		READY
6415	6415	Coupe	Capri I		2	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SKODA-YETI-5L-SUV-PREFL-01	4223	1793	1691	Škoda Auto Annual Report 2009	https://cdn.skoda-storyboard.com/2016/05/skoda-auto-annual-report-2009.pdf
EU-SKODA-YETI-5L-SUV-FACELIFT-01	4222	1793	1691	ŠKODA YETI technical data	https://cdn.skoda-storyboard.com/2016/12/TD_YETI_en.pdf
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/ssangyong-korando-iii-c-generation-4641;https://www.automobile-catalog.com/car/2011/3167075/ssangyong_korando_e-xdi_200_175_4wd.html
EU-CITROEN-DS4-I-HATCHBACK-01	4275	1810	1523	Citroën DS 4 official brochure (archived)	https://manualzilla.com/doc/7061150/citroen-ds-4-brochure
EU-VOLVO-780-COUPE-2D-01	4794	1750	1400	Volvo Cars 780 heritage; Volvo Owners Club UK 780 technical specifications	https://www.volvocars.com/en-vn/cars/legacy-models/780/;https://www.volvoclub.org.uk/780specs.shtml
EU-SMART-FORTWO-II-C451-COUPE-01	2695	1559	1542	Automobile-Catalog Smart Fortwo ED2	https://www.automobile-catalog.com/car/2010/3155720/smart_fortwo_ed_ed2.html
EU-SMART-FORTWO-II-A451-CONVERTIBLE-01	2695	1559	1542	CarsGuide Smart Fortwo dimensions 2010	https://www.carsguide.com.au/smart/fortwo/car-dimensions/2010
```

## 下一步优先处理

1. 优先消除 Transporter 复杂分支：

   * T3 Syncro 14 英寸与 16 英寸底盘；
   * T3 单排、双排及宽货台 Pritsche；
   * T4 SWB/LWB、改款前后、车顶和 Pritsche 分支。
2. 闭合 Kia Sorento II 改款前后高度差异，以及 Jeep Wrangler III 两门/四门边界。
3. 批量处理 VW LT 28-35 I 的轴距、车顶和底盘分支。
4. 再处理 Volvo PV544、Duett、Amazon及经典 BMW 1500-2000、V8、503 等首次尺寸组。

推进信号：CONTINUE

[1]: https://manualzilla.com/doc/7061150/citroen-ds-4-brochure "CITROEN DS 4 Brochure"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5901-6000_ktype_dimension_mapping_final.tsv
- all_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增 **40 个 Ktype、55 行 READY 映射**。
* Transporter T3 的 Syncro 14/16 英寸底盘及单排、双排、宽货台分支，均直接复用已有尺寸组，未重复输出尺寸和来源。
* 首次创建并闭合 **12 个尺寸组**，覆盖 Volvo 360、PV544、P210 Duett、P220 Amazon、Alpina D5 F11 及多款经典 BMW。Volvo 车型的车身形式和三维已按车型资料分别闭合。([汽车目录][1])
* BMW Neue Klasse、02 Series、1600 GT、501/502 V8、3200 CS 和 503 Cabriolet 已按不同物理车身独立建组。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：**100**
* 已完成 Ktype：**76**
* READY 映射行：**103**
* PENDING Ktype：**24**
* 当前已引用尺寸组：**42**
* 本轮首次创建尺寸组：**12**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6305_syncro14	6305	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6305_syncro16	6305	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6307_syncro14	6307	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6307_syncro16	6307	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6308_syncro14	6308	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6308_syncro16	6308	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6309_singlecab	6309	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6309_doublecab	6309	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6309_widebed	6309	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_singlecab	6310	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_doublecab	6310	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_widebed	6310	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_singlecab	6311	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_doublecab	6311	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_widebed	6311	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_singlecab	6312	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_doublecab	6312	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_widebed	6312	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_singlecab	6313	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_doublecab	6313	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_widebed	6313	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6337	6337	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6338	6338	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6340	6340	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6341	6341	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6352	6352	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6353	6353	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6354	6354	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6355	6355	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6367_singlecab	6367	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6367_doublecab	6367	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6367_widebed	6367	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6376	6376	Wagon	P210 Duett	P210		EU-VOLVO-P210-DUETT-WAGON-3D-01	HIGH		READY
6378	6378	Wagon	P220 Amazon Estate	P220	5	EU-VOLVO-P220-AMAZON-WAGON-5D-01	HIGH		READY
6391	6391	Wagon	D5 Bi-Turbo F11	F11	5	EU-ALPINA-D5-F11-WAGON-01	HIGH		READY
6393	6393	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6394	6394	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6395	6395	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6396	6396	Coupe	1600 GT		2	EU-BMW-1600-GT-COUPE-2D-01	HIGH		READY
6398	6398	Sedan	02 Series		2	EU-BMW-02-SERIES-SEDAN-2D-01	HIGH	两门三厢车身。	READY
6399	6399	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6400	6400	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6401	6401	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6402	6402	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6403	6403	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6405	6405	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6406	6406	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6407	6407	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6408	6408	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6409	6409	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6410	6410	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6411	6411	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6412	6412	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6413	6413	Coupe	3200 CS		2	EU-BMW-3200-CS-COUPE-2D-01	HIGH		READY
6414	6414	Convertible	503		2	EU-BMW-503-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-360-SEDAN-4D-01	4415	1660	1392	Automobile-Catalog 1984 Volvo 360; Volvo Cars 360 Sedan heritage	https://www.automobile-catalog.com/car/1984/30590/volvo_360.html;https://www.volvocars.com/en-vn/cars/legacy-models/360-sedan/
EU-VOLVO-PV544-SEDAN-2D-01	4450	1590	1560	Toyota Automobile Museum Volvo PV544; Volvo Cars PV544 heritage	https://toyota-automobile-museum.jp/en/archives/car-database/detail.html?id=22948;https://www.volvocars.com/en-ca/cars/legacy-models/pv544/
EU-VOLVO-P210-DUETT-WAGON-3D-01	4410	1610	1710	Carspector 1967 Volvo P210 Duett; Volvo Cars P210 Duett heritage	https://carspector.com/car/volvo/057751/;https://www.volvocars.com/us/cars/legacy-models/p210-duett/
EU-VOLVO-P220-AMAZON-WAGON-5D-01	4490	1620	1505	Volvo Owners Club UK P220 Amazon Estate; Volvo Cars P220 Amazon Estate heritage	https://www.volvoclub.org.uk/history/p220.shtml;https://www.volvocars.com/my/cars/legacy-models/p220-amazon-estate/
EU-ALPINA-D5-F11-WAGON-01	4913	1860	1453	Auto-Data Alpina D5 Touring F11; Automobile-Catalog Alpina 5 F11 Touring	https://www.auto-data.net/en/alpina-d5-touring-f11-3.0-350hp-biturbo-18323;https://www.automobile-catalog.com/make/alpina/5-series_f10_alpina/5-series_f11_alpina_1_touring/2014.html
EU-BMW-NEUE-KLASSE-SEDAN-4D-01	4500	1710	1450	Automobile-Catalog 1963 BMW 1500	https://www.automobile-catalog.com/car/1963/77255/bmw_1500.html
EU-BMW-NEUE-KLASSE-SEDAN-4D-02	4500	1710	1445	Automobile-Catalog 1970 BMW 2000 Tii	https://www.automobile-catalog.com/car/1970/77420/bmw_2000_tii.html
EU-BMW-1600-GT-COUPE-2D-01	4050	1550	1280	Automobile-Catalog 1967 BMW 1600 GT	https://www.automobile-catalog.com/car/1967/262625/bmw_1600_gt.html
EU-BMW-02-SERIES-SEDAN-2D-01	4230	1590	1410	Automobile-Catalog 1968 BMW 1600 Ti	https://www.automobile-catalog.com/car/1968/76595/bmw_1600_ti.html
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530	ADAC BMW 501 2.6; Automobile-Catalog 1962 BMW 3200 S	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/501-502/1generation/346428/;https://www.automobile-catalog.com/car/1962/262295/bmw_3200_s.html
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460	Automobile-Catalog 1963 BMW 3200 CS	https://www.automobile-catalog.com/car/1963/1448840/bmw_3200_cs_2__serie.html
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430	Automobile-Catalog 1957 BMW 503 Cabriolet	https://www.automobile-catalog.com/car/1957/262340/bmw_503_cabriolet.html
```

## 下一步优先处理

1. 闭合 Kia Sorento II 前驱、四驱及生产期内改款外廓。
2. 批量处理 Transporter T4 Kasten 与 Pritsche 的 SWB/LWB、改款前后和车顶分支。
3. 处理 Transporter T1 Pritsche 物理配置。
4. 集中闭合 VW LT 28-35 I 的轴距、普通顶/高顶及底盘驾驶室分支。
5. 最后确认 Jeep Wrangler III 开放式车身的两门、四门边界。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1984/30590/volvo_360.html?utm_source=chatgpt.com "1984 Volvo 360 Specs Review (68 kW / 92 PS / 91 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1963/77255/bmw_1500.html?utm_source=chatgpt.com "1963 BMW 1500 (man. 4) (model for Europe North America ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5901-6000_ktype_dimension_mapping_final.tsv
- all_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Kia Sorento II 2.0 CRDi 前驱、四驱记录，按 2012 年改款前后拆分；相同驱动版本复用同一物理尺寸组。改款前为 4685 × 1885 × 1710 mm，改款后为 4685 × 1885 × 1745 mm。
* 完成 Jeep Wrangler III 2.8 CRD 开放式车身，按两门/四门及官方软顶高度上下边界拆分。官方欧洲规格明确给出不含后视镜宽度。([Stellantis Media][1])
* 本轮新增 **3 个已完成 Ktype、8 行 READY 映射、6 个尺寸组**。

## 当前批次进度

* 输入 Ktype：**100**
* 已完成 Ktype：**79**
* READY 映射行：**111**
* PENDING Ktype：**21**
* 当前已引用尺寸组：**48**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6300_prefl	6300	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6300_facelift	6300	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6302_prefl	6302	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6302_facelift	6302	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6381_2dr_softtop_low	6381	SUV	Wrangler III (JK)	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-LOW-01	HIGH	开放式两门软顶，按官方高度上下边界拆分。	READY
6381_2dr_softtop_high	6381	SUV	Wrangler III (JK)	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-HIGH-01	HIGH	开放式两门软顶，按官方高度上下边界拆分。	READY
6381_4dr_softtop_low	6381	SUV	Wrangler III (JK)	JKU	4	EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-LOW-01	HIGH	开放式四门Unlimited软顶，按官方高度上下边界拆分。	READY
6381_4dr_softtop_high	6381	SUV	Wrangler III (JK)	JKU	4	EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-HIGH-01	HIGH	开放式四门Unlimited软顶，按官方高度上下边界拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-SORENTO-II-XM-SUV-PREFL-01	4685	1885	1710	Kia Motors Sorento official brochure; Automobile-Catalog 2011 Kia Sorento-R 2.0 E-VGT 2WD	https://kia.co.tt/home/assets/sorentodownloads/sorento.pdf;https://www.automobile-catalog.com/car/2011/1365230/kia_sorento-r_2_0_e-vgt_limited_2wd.html
EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	4685	1885	1745	Automobile-Catalog 2014 Kia Sorento-R 2.0 2WD; Auto-Data Kia Sorento II facelift 2.0D CRDi 4WD	https://www.automobile-catalog.com/car/2014/1773590/kia_sorento-r_2_0_2wd.html;https://www.auto-data.net/en/kia-sorento-ii-facelift-2012-2.0d-16v-crdi-150hp-4wd-18995
EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-LOW-01	4223	1873	1825	2011 Jeep Wrangler European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_Wrangler_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-HIGH-01	4223	1873	1865	2011 Jeep Wrangler European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_Wrangler_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-LOW-01	4751	1877	1825	2011 Jeep Wrangler Unlimited European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_WranglerUnlimited_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-HIGH-01	4751	1877	1865	2011 Jeep Wrangler Unlimited European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_WranglerUnlimited_ST_ENG.pdf
```

## 下一步优先处理

1. 集中闭合 Transporter T4 Kasten 的改款前后、SWB/LWB 和普通顶/高顶分支。
2. 处理 Transporter T4 Pritsche/Fahrgestell 的单排、双排及轴距边界。
3. 闭合 Transporter T1 Pritsche 跨 T1/T2 生产期的代际边界。
4. 最后批量处理 VW LT 28-35 I 的短/长轴、普通顶/高顶及底盘驾驶室分支。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_Wrangler_ST_ENG.pdf "110411_J_Jeep_ENG"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5901-6000_ktype_dimension_mapping_final.tsv
- all_5901-6000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合剩余 **21 个 Ktype**，完成 Transporter T4、Transporter T1/T2 Pritsche 及 Volkswagen LT I 的轴距、车顶、驾驶室和底盘分支。
* 本轮新增 **120 行 READY 映射**、**31 个尺寸组**。T4 与 LT I 各分支均按对应技术尺寸资料建立，后续相同 Ktype 直接复用。([汽车手册在线][1])
* 已机械修正 LT I 映射中组合式 `BodyCode`，无明确单一代码的行统一留空。
* 两张最终表已完成唯一性、字段完整性、引用闭合及下载文件检查。

## 当前批次进度

* 输入 Ktype：**100**
* 已覆盖 Ktype：**100**
* READY 映射行：**231**
* PENDING：**0**
* DIMENSION_GROUP：**79**
* 缺失映射引用：**0**
* 孤立尺寸组：**0**
* `id` 重复：**0**
* `DIMENSION_GROUP_ID` 重复：**0**

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6298	6298	Van	Transporter T2			EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	HIGH		READY
6299_lowroof	6299	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6299_highroof	6299	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6300_prefl	6300	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6300_facelift	6300	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6301_lowroof	6301	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6301_highroof	6301	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6302_prefl	6302	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-PREFL-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6302_facelift	6302	SUV	Sorento II (XM)	XM	5	EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	HIGH	生产期跨2012年改款，按改款前后外廓拆分。	READY
6303_lowroof	6303	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6303_highroof	6303	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6304_lowroof	6304	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6304_highroof	6304	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6305_syncro14	6305	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6305_syncro16	6305	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6306_prefl	6306	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6306_facelift	6306	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6307_syncro14	6307	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6307_syncro16	6307	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6308_syncro14	6308	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6308_syncro16	6308	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	MEDIUM	Syncro按14英寸与16英寸底盘外廓拆分。	READY
6309_singlecab	6309	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6309_doublecab	6309	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6309_widebed	6309	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_singlecab	6310	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_doublecab	6310	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6310_widebed	6310	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_singlecab	6311	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_doublecab	6311	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6311_widebed	6311	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_singlecab	6312	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_doublecab	6312	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6312_widebed	6312	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_singlecab	6313	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_doublecab	6313	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6313_widebed	6313	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6314_prefl	6314	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6314_facelift	6314	Hatchback	Superb II (3T)	3T4	5	EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6315_prefl_swb_lowroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6315_prefl_lwb_lowroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6315_prefl_lwb_highroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6315_facelift_swb_lowroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6315_facelift_lwb_lowroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6315_facelift_lwb_highroof	6315	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_prefl_swb_lowroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_prefl_lwb_lowroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_prefl_lwb_highroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_facelift_swb_lowroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_facelift_lwb_lowroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6316_facelift_lwb_highroof	6316	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6317_prefl_swb_lowroof	6317	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6317_prefl_lwb_lowroof	6317	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6317_prefl_lwb_highroof	6317	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_prefl_swb_lowroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_prefl_lwb_lowroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_prefl_lwb_highroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_facelift_swb_lowroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_facelift_lwb_lowroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6318_facelift_lwb_highroof	6318	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_prefl_swb_lowroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_prefl_lwb_lowroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_prefl_lwb_highroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_facelift_swb_lowroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_facelift_lwb_lowroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6319_facelift_lwb_highroof	6319	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_prefl_swb_lowroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_prefl_lwb_lowroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_prefl_lwb_highroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_facelift_swb_lowroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_facelift_lwb_lowroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6320_facelift_lwb_highroof	6320	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_prefl_swb_lowroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_prefl_lwb_lowroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_prefl_lwb_highroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_facelift_swb_lowroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_facelift_lwb_lowroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6321_facelift_lwb_highroof	6321	Van	Transporter T4	70		EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	HIGH	Kasten按1996年前后尺寸资料、轴距和车顶外廓拆分。	READY
6322_prefl_swb_singlecab	6322	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6322_prefl_lwb_singlecab	6322	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6322_prefl_lwb_doublecab	6322	Pickup	Transporter T4	70	4	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6323_prefl_swb_singlecab	6323	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6323_prefl_lwb_singlecab	6323	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6323_prefl_lwb_doublecab	6323	Pickup	Transporter T4	70	4	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6323_facelift_lwb_singlecab	6323	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6323_facelift_lwb_doublecab	6323	Pickup	Transporter T4	70	4	EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6324_prefl_swb_singlecab	6324	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6324_prefl_lwb_singlecab	6324	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6324_prefl_lwb_doublecab	6324	Pickup	Transporter T4	70	4	EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6324_facelift_lwb_singlecab	6324	Pickup	Transporter T4	70	2	EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6324_facelift_lwb_doublecab	6324	Pickup	Transporter T4	70	4	EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按1996年前后尺寸资料、轴距和驾驶室外廓拆分。	READY
6325_t1_singlecab	6325	Pickup	Transporter T1	T1	2	EU-VW-TRANSPORTER-T1-PICKUP-SINGLECAB-01	MEDIUM	生产期跨T1/T2边界，并按单排与双排驾驶室拆分。	READY
6325_t1_doublecab	6325	Pickup	Transporter T1	T1	4	EU-VW-TRANSPORTER-T1-PICKUP-DOUBLECAB-01	MEDIUM	生产期跨T1/T2边界，并按单排与双排驾驶室拆分。	READY
6325_t2_prefl_singlecab	6325	Pickup	Transporter T2	T2	2	EU-VW-TRANSPORTER-T2-PICKUP-PREFL-SINGLECAB-01	MEDIUM	生产期跨T1/T2边界，并按单排与双排驾驶室拆分。	READY
6325_t2_prefl_doublecab	6325	Pickup	Transporter T2	T2	4	EU-VW-TRANSPORTER-T2-PICKUP-PREFL-DOUBLECAB-01	MEDIUM	生产期跨T1/T2边界，并按单排与双排驾驶室拆分。	READY
6326_prefl	6326	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6326_facelift	6326	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6337	6337	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6338	6338	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6339_prefl	6339	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6339_facelift	6339	Wagon	Superb II (3T)	3T5	5	EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6340	6340	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6341	6341	Sedan	360 Sedan		4	EU-VOLVO-360-SEDAN-4D-01	HIGH		READY
6342_lowroof	6342	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6342_highroof	6342	Van	Transporter T3			EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	MEDIUM	Kasten按普通顶/高顶物理外廓拆分。	READY
6345_prefl	6345	SUV	Yeti (5L)	5L	5	EU-SKODA-YETI-5L-SUV-PREFL-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6345_facelift	6345	SUV	Yeti (5L)	5L	5	EU-SKODA-YETI-5L-SUV-FACELIFT-01	HIGH	生产期跨2013改款，按改款前/后外廓拆分。	READY
6346	6346	SUV	Korando III (C200)	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-01	HIGH		READY
6347	6347	SUV	Korando III (C200)	C200	5	EU-SSANGYONG-KORANDO-III-C200-SUV-01	HIGH		READY
6348	6348	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6349	6349	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6350	6350	Sedan	460	L	4	EU-VOLVO-460-L-SEDAN-4D-01	HIGH		READY
6351_prefl	6351	Hatchback	440	K	5	EU-VOLVO-440-K-HATCHBACK-PREFL-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6351_facelift	6351	Hatchback	440	K	5	EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6352	6352	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6353	6353	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6354	6354	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6355	6355	Sedan	PV544	PV544	2	EU-VOLVO-PV544-SEDAN-2D-01	HIGH	可靠资料确认该车型为两门轿车，修正输入Schrägheck分类。	READY
6356	6356	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
6357	6357	Sedan	S40 I	VS	4	EU-VOLVO-S40-I-VS-SEDAN-4D-01	HIGH		READY
6358	6358	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-01	HIGH		READY
6359_swb_lowroof	6359	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6359_lwb_lowroof	6359	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6359_swb_highroof	6359	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6359_lwb_highroof	6359	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6360	6360	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6361_swb_lowroof	6361	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6361_lwb_lowroof	6361	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6361_swb_highroof	6361	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6361_lwb_highroof	6361	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6362_swb_lowroof	6362	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6362_lwb_lowroof	6362	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6362_swb_highroof	6362	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6362_lwb_highroof	6362	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6363_swb_lowroof	6363	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6363_lwb_lowroof	6363	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6363_swb_highroof	6363	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6363_lwb_highroof	6363	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6364_swb_lowroof	6364	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6364_lwb_lowroof	6364	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6364_swb_highroof	6364	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6364_lwb_highroof	6364	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6365_swb_lowroof	6365	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6365_lwb_lowroof	6365	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6365_swb_highroof	6365	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6365_lwb_highroof	6365	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6366_swb_lowroof	6366	Van	LT I			EU-VW-LT-I-VAN-SWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6366_lwb_lowroof	6366	Van	LT I			EU-VW-LT-I-VAN-LWB-LOWROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6366_swb_highroof	6366	Van	LT I			EU-VW-LT-I-VAN-SWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6366_lwb_highroof	6366	Van	LT I			EU-VW-LT-I-VAN-LWB-HIGHROOF-01	HIGH	Kasten按短/长轴与普通顶/高顶外廓拆分。	READY
6367_singlecab	6367	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6367_doublecab	6367	Pickup	Transporter T3		4	EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6367_widebed	6367	Pickup	Transporter T3		2	EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	MEDIUM	Pritsche/Fahrgestell按单排、双排和宽货台外廓拆分。	READY
6368_swb_singlecab_2105	6368	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_swb_singlecab_2110	6368	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_singlecab_2105	6368	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_singlecab_2110	6368	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_doublecab_2140	6368	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_doublecab_2085	6368	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_swb_chassis_2040	6368	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_swb_chassis_2050	6368	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_chassis_2040	6368	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_chassis_2050	6368	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_chassis_doublecab_2040	6368	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6368_lwb_chassis_doublecab_2050	6368	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_swb_singlecab_2105	6369	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_swb_singlecab_2110	6369	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_singlecab_2105	6369	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_singlecab_2110	6369	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_doublecab_2140	6369	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_doublecab_2085	6369	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_swb_chassis_2040	6369	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_swb_chassis_2050	6369	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_chassis_2040	6369	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_chassis_2050	6369	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_chassis_doublecab_2040	6369	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6369_lwb_chassis_doublecab_2050	6369	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_swb_singlecab_2105	6370	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_swb_singlecab_2110	6370	Pickup	LT I		2	EU-VW-LT-I-PICKUP-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_singlecab_2105	6370	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_singlecab_2110	6370	Pickup	LT I		2	EU-VW-LT-I-PICKUP-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_doublecab_2140	6370	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_doublecab_2085	6370	Pickup	LT I		4	EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_swb_chassis_2040	6370	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_swb_chassis_2050	6370	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_chassis_2040	6370	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_chassis_2050	6370	Pickup	LT I		2	EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_chassis_doublecab_2040	6370	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-01	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6370_lwb_chassis_doublecab_2050	6370	Pickup	LT I		4	EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-02	HIGH	Pritsche/Fahrgestell按轴距、驾驶室及LT28/31与LT35外廓拆分。	READY
6371	6371	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6372	6372	Sedan	940	944	4	EU-VOLVO-940-SEDAN-4D-01	HIGH		READY
6376	6376	Wagon	P210 Duett	P210		EU-VOLVO-P210-DUETT-WAGON-3D-01	HIGH		READY
6377	6377	Hatchback	DS4 I		5	EU-CITROEN-DS4-I-HATCHBACK-01	HIGH		READY
6378	6378	Wagon	P220 Amazon Estate	P220	5	EU-VOLVO-P220-AMAZON-WAGON-5D-01	HIGH		READY
6379	6379	Coupe	780	780	2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
6380	6380	Coupe	780	780	2	EU-VOLVO-780-COUPE-2D-01	HIGH		READY
6381_2dr_softtop_low	6381	SUV	Wrangler III (JK)	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-LOW-01	HIGH	开放式两门软顶，按官方高度上下边界拆分。	READY
6381_2dr_softtop_high	6381	SUV	Wrangler III (JK)	JK	2	EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-HIGH-01	HIGH	开放式两门软顶，按官方高度上下边界拆分。	READY
6381_4dr_softtop_low	6381	SUV	Wrangler III (JK)	JKU	4	EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-LOW-01	HIGH	开放式四门Unlimited软顶，按官方高度上下边界拆分。	READY
6381_4dr_softtop_high	6381	SUV	Wrangler III (JK)	JKU	4	EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-HIGH-01	HIGH	开放式四门Unlimited软顶，按官方高度上下边界拆分。	READY
6382	6382	MPV	Nemo I			EU-CITROEN-NEMO-MULTISPACE-MPV-01	HIGH		READY
6383	6383	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6385	6385	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6388	6388	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6389	6389	Sedan	740	744	4	EU-VOLVO-740-SEDAN-4D-01	HIGH		READY
6390_prefl	6390	Sedan	760	764	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6390_facelift	6390	Sedan	760	764	4	EU-VOLVO-760-SEDAN-FACELIFT-01	HIGH	生产期跨改款，按改款前/后外廓拆分。	READY
6391	6391	Wagon	D5 Bi-Turbo F11	F11	5	EU-ALPINA-D5-F11-WAGON-01	HIGH		READY
6392	6392	Sedan	760	764	4	EU-VOLVO-760-SEDAN-PREFL-01	HIGH		READY
6393	6393	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6394	6394	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6395	6395	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6396	6396	Coupe	1600 GT		2	EU-BMW-1600-GT-COUPE-2D-01	HIGH		READY
6397	6397	Coupe	Fortwo II (451)	C451	2	EU-SMART-FORTWO-II-C451-COUPE-01	HIGH		READY
6398	6398	Sedan	02 Series		2	EU-BMW-02-SERIES-SEDAN-2D-01	HIGH	两门三厢车身。	READY
6399	6399	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6400	6400	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6401	6401	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6402	6402	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-01	HIGH		READY
6403	6403	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6404	6404	Convertible	Fortwo II (451)	A451	2	EU-SMART-FORTWO-II-A451-CONVERTIBLE-01	HIGH		READY
6405	6405	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6406	6406	Sedan	Neue Klasse		4	EU-BMW-NEUE-KLASSE-SEDAN-4D-02	HIGH	2000系列按确认的较低车身高度独立建组。	READY
6407	6407	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6408	6408	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6409	6409	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6410	6410	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6411	6411	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6412	6412	Sedan	501/502 V8		4	EU-BMW-501-502-V8-SEDAN-4D-01	HIGH	可靠资料确认该记录对应501/502系四门V8轿车，修正输入Coupe分类。	READY
6413	6413	Coupe	3200 CS		2	EU-BMW-3200-CS-COUPE-2D-01	HIGH		READY
6414	6414	Convertible	503		2	EU-BMW-503-CONVERTIBLE-2D-01	HIGH		READY
6415	6415	Coupe	Capri I		2	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5901-6000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-TRANSPORTER-T2-VAN-FACELIFT-01	4505	1720	1960	Volkswagen T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T3-VAN-RWD-LOWROOF-01	4570	1845	1965	Volkswagen Transporter T3 instruction manual	https://westfaliat3.info/July_1985_VW_T25_Instruction_Manual_WestfaliaT3WM.pdf
EU-VW-TRANSPORTER-T3-VAN-RWD-HIGHROOF-01	4570	1845	2365	Volkswagen Transporter T3 instruction manual	https://westfaliat3.info/July_1985_VW_T25_Instruction_Manual_WestfaliaT3WM.pdf
EU-KIA-SORENTO-II-XM-SUV-PREFL-01	4685	1885	1710	Kia Motors Sorento official brochure; Automobile-Catalog 2011 Kia Sorento-R 2.0 E-VGT 2WD	https://kia.co.tt/home/assets/sorentodownloads/sorento.pdf;https://www.automobile-catalog.com/car/2011/1365230/kia_sorento-r_2_0_e-vgt_limited_2wd.html
EU-KIA-SORENTO-II-XM-SUV-FACELIFT-01	4685	1885	1745	Automobile-Catalog 2014 Kia Sorento-R 2.0 2WD; Auto-Data Kia Sorento II facelift 2.0D CRDi 4WD	https://www.automobile-catalog.com/car/2014/1773590/kia_sorento-r_2_0_2wd.html;https://www.auto-data.net/en/kia-sorento-ii-facelift-2012-2.0d-16v-crdi-150hp-4wd-18995
EU-VW-TRANSPORTER-T3-VAN-SYNCRO14-01	4570	1845	1990	Volkswagen Transporter T3 instruction manual	https://www.type17.net/type17_infos/doc/t3/Owner_Manual_WM_07_87_EN.pdf
EU-VW-TRANSPORTER-T3-VAN-SYNCRO16-01	4570	1865	2020	VW T3 Syncro 16 technical parameters	https://www.syncro.cz/historie-t3-a-syncra-16/technicke-parametry/
EU-SKODA-SUPERB-II-3T-LIFTBACK-PREFL-01	4838	1817	1462	Auto-Data Škoda Superb II	https://www.auto-data.net/en/skoda-superb-ii-generation-1825
EU-SKODA-SUPERB-II-3T-LIFTBACK-FACELIFT-01	4833	1817	1462	Auto-Data Škoda Superb II facelift	https://www.auto-data.net/en/skoda-superb-ii-facelift-2013-generation-4232
EU-VW-TRANSPORTER-T3-PICKUP-SINGLECAB-01	4570	1870	1930	Volkswagen Transporter T3 instruction manual	https://westfaliat3.info/July_1985_VW_T25_Instruction_Manual_WestfaliaT3WM.pdf
EU-VW-TRANSPORTER-T3-PICKUP-DOUBLECAB-01	4570	1870	1925	Volkswagen Transporter T3 instruction manual	https://westfaliat3.info/July_1985_VW_T25_Instruction_Manual_WestfaliaT3WM.pdf
EU-VW-TRANSPORTER-T3-PICKUP-WIDEBED-01	4636	2000	1930	Volkswagen Transporter T3 instruction manual	https://westfaliat3.info/July_1985_VW_T25_Instruction_Manual_WestfaliaT3WM.pdf
EU-VW-TRANSPORTER-T4-VAN-PREFL-SWB-LOWROOF-01	4655	1840	1940	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-LOWROOF-01	5055	1840	1940	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-VAN-PREFL-LWB-HIGHROOF-01	5055	1840	2400	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-VAN-FACELIFT-SWB-LOWROOF-01	4707	1840	1940	Volkswagen Transporter T4 technical dimensions	https://vandimensions.com/media/pages/database/volkswagen/transporter-t4/c97936329b-1626780378/vw_t4_dimensions.pdf
EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-LOWROOF-01	5107	1840	1940	Volkswagen Transporter T4 technical dimensions	https://vandimensions.com/media/pages/database/volkswagen/transporter-t4/c97936329b-1626780378/vw_t4_dimensions.pdf
EU-VW-TRANSPORTER-T4-VAN-FACELIFT-LWB-HIGHROOF-01	5107	1840	2430	Volkswagen Transporter T4 technical dimensions	https://vandimensions.com/media/pages/database/volkswagen/transporter-t4/c97936329b-1626780378/vw_t4_dimensions.pdf
EU-VW-TRANSPORTER-T4-PICKUP-PREFL-SWB-SINGLECAB-01	4845	1970	1910	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-SINGLECAB-01	5245	1970	1910	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-PICKUP-PREFL-LWB-DOUBLECAB-01	5245	1970	1920	1992 Volkswagen Transporter T4 owners manual	https://autohomes.vwt4camper.info/Aug_1992_VW_T4_Owners_ManualWM.pdf
EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-SINGLECAB-01	5271	1970	1910	Volkswagen Transporter T4 technical dimensions	https://vandimensions.com/media/pages/database/volkswagen/transporter-t4/c97936329b-1626780378/vw_t4_dimensions.pdf
EU-VW-TRANSPORTER-T4-PICKUP-FACELIFT-LWB-DOUBLECAB-01	5271	1970	1920	Volkswagen Transporter T4 technical dimensions	https://vandimensions.com/media/pages/database/volkswagen/transporter-t4/c97936329b-1626780378/vw_t4_dimensions.pdf
EU-VW-TRANSPORTER-T1-PICKUP-SINGLECAB-01	4280	1750	1920	VW T1 technical data; Volkswagen T1 Transporter brochure	https://de.wikipedia.org/wiki/VW_T1;https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-T1-Transporter-1965-AU.pdf
EU-VW-TRANSPORTER-T1-PICKUP-DOUBLECAB-01	4280	1750	1920	VW T1 technical data; Volkswagen T1 Transporter brochure	https://de.wikipedia.org/wiki/VW_T1;https://autocatalogarchive.com/wp-content/uploads/2019/06/VW-T1-Transporter-1965-AU.pdf
EU-VW-TRANSPORTER-T2-PICKUP-PREFL-SINGLECAB-01	4420	1765	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-VW-TRANSPORTER-T2-PICKUP-PREFL-DOUBLECAB-01	4420	1765	1960	VW T2 technical data	https://de.wikipedia.org/wiki/VW_T2
EU-SKODA-SUPERB-II-3T-WAGON-PREFL-01	4838	1817	1510	Auto-Data Škoda Superb II Combi	https://www.auto-data.net/en/skoda-superb-ii-combi-generation-1827
EU-SKODA-SUPERB-II-3T-WAGON-FACELIFT-01	4833	1817	1511	Auto-Data Škoda Superb II Combi facelift	https://www.auto-data.net/en/skoda-superb-ii-combi-facelift-2013-generation-4233
EU-VOLVO-360-SEDAN-4D-01	4415	1660	1392	Automobile-Catalog 1984 Volvo 360; Volvo Cars 360 Sedan heritage	https://www.automobile-catalog.com/car/1984/30590/volvo_360.html;https://www.volvocars.com/en-vn/cars/legacy-models/360-sedan/
EU-SKODA-YETI-5L-SUV-PREFL-01	4223	1793	1691	Škoda Auto Annual Report 2009	https://cdn.skoda-storyboard.com/2016/05/skoda-auto-annual-report-2009.pdf
EU-SKODA-YETI-5L-SUV-FACELIFT-01	4222	1793	1691	ŠKODA YETI technical data	https://cdn.skoda-storyboard.com/2016/12/TD_YETI_en.pdf
EU-SSANGYONG-KORANDO-III-C200-SUV-01	4410	1830	1675	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/ssangyong-korando-iii-c-generation-4641;https://www.automobile-catalog.com/car/2011/3167075/ssangyong_korando_e-xdi_200_175_4wd.html
EU-CITROEN-DS4-I-HATCHBACK-01	4275	1810	1523	Citroën DS 4 official brochure (archived)	https://manualzilla.com/doc/7061150/citroen-ds-4-brochure
EU-VOLVO-460-L-SEDAN-4D-01	4435	1686	1378	Volvo Cars 460 heritage	https://www.volvocars.com/intl/cars/legacy-models/460/
EU-VOLVO-440-K-HATCHBACK-PREFL-01	4312	1676	1379	Volvo Cars 440 heritage; Automobile-Catalog Volvo 440	https://www.volvocars.com/intl/cars/legacy-models/440/;https://www.automobile-catalog.com/model/volvo/440.html
EU-VOLVO-440-K-HATCHBACK-FACELIFT-01	4345	1686	1378	Volvo Cars 440 heritage; Automobile-Catalog Volvo 440	https://www.volvocars.com/intl/cars/legacy-models/440/;https://www.automobile-catalog.com/model/volvo/440.html
EU-VOLVO-PV544-SEDAN-2D-01	4450	1590	1560	Toyota Automobile Museum Volvo PV544; Volvo Cars PV544 heritage	https://toyota-automobile-museum.jp/en/archives/car-database/detail.html?id=22948;https://www.volvocars.com/en-ca/cars/legacy-models/pv544/
EU-VOLVO-940-SEDAN-4D-01	4871	1750	1425	Volvo Cars 940 heritage	https://www.volvocars.com/intl/cars/legacy-models/940/
EU-VOLVO-S40-I-VS-SEDAN-4D-01	4516	1720	1422	Volvo Cars S40 heritage	https://www.volvocars.com/intl/cars/legacy-models/s40/
EU-VOLVO-V40-I-VW-WAGON-5D-01	4516	1720	1425	Volvo Cars V40 heritage	https://www.volvocars.com/intl/cars/legacy-models/v40/
EU-VW-LT-I-VAN-SWB-LOWROOF-01	4855	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-VAN-LWB-LOWROOF-01	5305	2040	2160	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-VAN-SWB-HIGHROOF-01	4855	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-VAN-LWB-HIGHROOF-01	5305	2040	2570	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-SWB-SINGLECAB-01	4875	2140	2105	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-SWB-SINGLECAB-02	4875	2140	2110	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-LWB-SINGLECAB-01	5630	2140	2105	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-LWB-SINGLECAB-02	5630	2140	2110	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-01	5330	2140	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-PICKUP-LWB-DOUBLECAB-02	5330	2140	2085	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-01	4795	2040	2110	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-SWB-SINGLECAB-02	4795	2050	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-01	5245	2040	2110	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-LWB-SINGLECAB-02	5245	2050	2115	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-01	5245	2040	2140	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VW-LT-I-CHASSIS-LWB-DOUBLECAB-02	5245	2050	2085	Volkswagen LT Technical Data and Equipment	https://www.thesamba.com/vw/archives/lit/lt_tech_specs/LTtechspecs.pdf
EU-VOLVO-P210-DUETT-WAGON-3D-01	4410	1610	1710	Carspector 1967 Volvo P210 Duett; Volvo Cars P210 Duett heritage	https://carspector.com/car/volvo/057751/;https://www.volvocars.com/us/cars/legacy-models/p210-duett/
EU-VOLVO-P220-AMAZON-WAGON-5D-01	4490	1620	1505	Volvo Owners Club UK P220 Amazon Estate; Volvo Cars P220 Amazon Estate heritage	https://www.volvoclub.org.uk/history/p220.shtml;https://www.volvocars.com/my/cars/legacy-models/p220-amazon-estate/
EU-VOLVO-780-COUPE-2D-01	4794	1750	1400	Volvo Cars 780 heritage; Volvo Owners Club UK 780 technical specifications	https://www.volvocars.com/en-vn/cars/legacy-models/780/;https://www.volvoclub.org.uk/780specs.shtml
EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-LOW-01	4223	1873	1825	2011 Jeep Wrangler European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_Wrangler_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JK-SUV-2D-SOFTTOP-HIGH-01	4223	1873	1865	2011 Jeep Wrangler European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_Wrangler_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-LOW-01	4751	1877	1825	2011 Jeep Wrangler Unlimited European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_WranglerUnlimited_ST_ENG.pdf
EU-JEEP-WRANGLER-III-JKU-SUV-4D-SOFTTOP-HIGH-01	4751	1877	1865	2011 Jeep Wrangler Unlimited European technical specifications	https://www.media.stellantis.com/uploads/em/2011/JEEP/SCHEDE_TECNICHE/110411_J_WranglerUnlimited_ST_ENG.pdf
EU-CITROEN-NEMO-MULTISPACE-MPV-01	3959	1716	1721	Auto-Data Citroën Nemo Combi	https://www.auto-data.net/en/citroen-nemo-combi-generation-4784
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430	Volvo Cars 740 heritage	https://www.volvocars.com/intl/cars/legacy-models/740/
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410	Volvo Cars 760 heritage; Automobile-Catalog Volvo 760	https://www.volvocars.com/intl/cars/legacy-models/760/;https://www.automobile-catalog.com/model/volvo/760.html
EU-VOLVO-760-SEDAN-FACELIFT-01	4790	1760	1410	Volvo Cars 760 heritage; Automobile-Catalog Volvo 760	https://www.volvocars.com/intl/cars/legacy-models/760/;https://www.automobile-catalog.com/model/volvo/760.html
EU-ALPINA-D5-F11-WAGON-01	4913	1860	1453	Auto-Data Alpina D5 Touring F11; Automobile-Catalog Alpina 5 F11 Touring	https://www.auto-data.net/en/alpina-d5-touring-f11-3.0-350hp-biturbo-18323;https://www.automobile-catalog.com/make/alpina/5-series_f10_alpina/5-series_f11_alpina_1_touring/2014.html
EU-BMW-NEUE-KLASSE-SEDAN-4D-01	4500	1710	1450	Automobile-Catalog 1963 BMW 1500	https://www.automobile-catalog.com/car/1963/77255/bmw_1500.html
EU-BMW-1600-GT-COUPE-2D-01	4050	1550	1280	Automobile-Catalog 1967 BMW 1600 GT	https://www.automobile-catalog.com/car/1967/262625/bmw_1600_gt.html
EU-SMART-FORTWO-II-C451-COUPE-01	2695	1559	1542	Automobile-Catalog Smart Fortwo ED2	https://www.automobile-catalog.com/car/2010/3155720/smart_fortwo_ed_ed2.html
EU-BMW-02-SERIES-SEDAN-2D-01	4230	1590	1410	Automobile-Catalog 1968 BMW 1600 Ti	https://www.automobile-catalog.com/car/1968/76595/bmw_1600_ti.html
EU-BMW-NEUE-KLASSE-SEDAN-4D-02	4500	1710	1445	Automobile-Catalog 1970 BMW 2000 Tii	https://www.automobile-catalog.com/car/1970/77420/bmw_2000_tii.html
EU-SMART-FORTWO-II-A451-CONVERTIBLE-01	2695	1559	1542	CarsGuide Smart Fortwo dimensions 2010	https://www.carsguide.com.au/smart/fortwo/car-dimensions/2010
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530	ADAC BMW 501 2.6; Automobile-Catalog 1962 BMW 3200 S	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/bmw/501-502/1generation/346428/;https://www.automobile-catalog.com/car/1962/262295/bmw_3200_s.html
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460	Automobile-Catalog 1963 BMW 3200 CS	https://www.automobile-catalog.com/car/1963/1448840/bmw_3200_cs_2__serie.html
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430	Automobile-Catalog 1957 BMW 503 Cabriolet	https://www.automobile-catalog.com/car/1957/262340/bmw_503_cabriolet.html
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330	Automobile-Catalog Ford Capri Mk I	https://www.automobile-catalog.com/model/ford_europe/capri_mk_i.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5901-6000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carmanualsonline.info/volkswagen-transporter-1992-t4-4-g-owners-manual/?srch=suspension "https://www.carmanualsonline.info/volkswagen-transporter-1992-t4-4-g-owners-manual/?srch=suspension"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_5901-6000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_5901-6000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（7670 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2364 行）

- 尺寸冲突协调：
  - EU-VOLVO-360-SEDAN-4D-01 -> EU-VOLVO-360-SEDAN-4D-02：4300x1660x1392 与 4415x1660x1392，创建新尺寸组
