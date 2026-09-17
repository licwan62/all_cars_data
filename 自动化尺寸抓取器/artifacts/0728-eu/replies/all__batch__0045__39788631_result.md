# 任务：all 第 4401-4500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0045__39788631


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 4401-4500 行

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
all 第 4401-4500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C4-AVANT-WAGON-01	4797	1783	1440
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340
EU-BMW-8-E31-COUPE-850CSI-01	4780	1855	1330
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-3D-01	4103	1620	1394
EU-HYUNDAI-ACCENT-I-X3-HATCHBACK-5D-01	4103	1620	1394
EU-HYUNDAI-SONATA-NF-FACELIFT-SEDAN-01	4800	1832	1475
EU-MAZDA-E-SERIES-III-SR1-MPV-01	4965	1690	1955
EU-MAZDA-E-SERIES-III-SR2-VAN-01	4690	1690	1960
EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	4390	1690	1960
EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	4690	1690	1960

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Hyundai	Accent	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Oct 1994	Jan 2000	2024-03-01	4541
Hyundai	Accent	1.3	Stufenheck	Frontantrieb	Benzin	55	75	Oct 1994	Jan 2000	2024-03-01	4542
Hyundai	Accent	1.3 I 12V	Stufenheck	Frontantrieb	Benzin	62	84	Oct 1994	Jan 2000	2024-03-01	4543
Hyundai	Accent	1.5 I 12V	Stufenheck	Frontantrieb	Benzin	65	88	Oct 1994	Jan 2000	2024-03-01	4544
Hyundai	Lantra i	1.5 I.e.	Stufenheck	Frontantrieb	Benzin	63	86	Oct 1990	Nov 1995	2024-03-01	4545
Hyundai	Lantra i	1.6 I.e. 16V	Stufenheck	Frontantrieb	Benzin	78	106	Oct 1990	Nov 1995	2024-03-01	4546
Hyundai	Lantra i	1.6 I.e. 16V	Stufenheck	Frontantrieb	Benzin	84	114	Oct 1990	Nov 1995	2024-03-01	4547
Hyundai	Lantra i	1.8 I.e. 16V	Stufenheck	Frontantrieb	Benzin	93	127	Oct 1990	Nov 1995	2024-03-01	4548
Hyundai	Pony	1.3	Schrägheck	Frontantrieb	Benzin	43	58	Oct 1989	Jan 1995	2024-03-01	4549
Hyundai	Pony	1.5	Schrägheck	Frontantrieb	Benzin	53	72	Oct 1989	Jan 1995	2024-03-01	4550
Hyundai	Pony	1.5 I	Schrägheck	Frontantrieb	Benzin	61	83	Oct 1989	Jan 1995	2024-03-01	4551
Hyundai	Pony	1.5 I	Schrägheck	Frontantrieb	Benzin	62	84	Oct 1989	Jan 1995	2024-03-01	4552
Hyundai	Pony	1.5	Stufenheck	Frontantrieb	Benzin	53	72	Jan 1990	Jan 1995	2024-03-01	4553
Hyundai	Pony	1.5 I	Stufenheck	Frontantrieb	Benzin	61	83	Jan 1990	Jan 1995	2024-03-01	4554
Hyundai	S	1.5 I	Coupe	Frontantrieb	Benzin	62	84	Feb 1990	May 1996	2024-03-01	4555
Hyundai	S	1.5 I	Coupe	Frontantrieb	Benzin	65	88	Apr 1992	May 1996	2024-03-01	4556
Hyundai	S	1.5 I Turbo	Coupe	Frontantrieb	Benzin	85	116	Apr 1991	May 1996	2024-03-01	4557
Hyundai	Sonata ii	2.0 I	Stufenheck	Frontantrieb	Benzin	80	109	Jan 1991	Oct 1993	2024-03-01	4558
Hyundai	Sonata ii	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	96	130	Jan 1991	Oct 1993	2024-03-01	4559
Hyundai	Sonata ii	3.0 I V6	Stufenheck	Frontantrieb	Benzin	107	145	Jan 1991	Oct 1993	2024-03-01	4560
Hyundai	Sonata iii	2.0 I	Stufenheck	Frontantrieb	Benzin	77	105	Jun 1994	Aug 1996	2024-03-01	4561
Hyundai	Sonata iii	2.0 I 16V	Stufenheck	Frontantrieb	Benzin	102	139	May 1993	Jun 1998	2024-03-01	4562
Hyundai	Sonata iii	3.0 I V6	Stufenheck	Frontantrieb	Benzin	107	146	May 1993	Jun 1998	2024-03-01	4563
Daewoo	Espero	1.5 16V	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1995	Jun 1999	2024-03-01	4564
Daewoo	Espero	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1995	Sep 1999	2024-03-01	4565
Mazda	E	E2200 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	47	64	Nov 1988	Mar 1997	2024-03-01	4566
Daewoo	Espero	1.8	Stufenheck	Frontantrieb	Benzin	70	95	Feb 1995	Jun 1999	2024-03-01	4567
Daewoo	Espero	2	Stufenheck	Frontantrieb	Benzin	77	105	Feb 1995	Jun 1999	2024-03-01	4568
Daewoo	Nexia	1.5	Schrägheck	Frontantrieb	Benzin	52	71	Feb 1995	Aug 1997	2024-03-01	4569
Daewoo	Nexia	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Feb 1995	Aug 1997	2024-03-01	4570
Daewoo	Nexia	1.5 16V	Schrägheck	Frontantrieb	Benzin	66	90	Feb 1995	Aug 1997	2024-03-01	4571
Daewoo	Nexia	1.5	Stufenheck	Frontantrieb	Benzin	52	71	Feb 1995	Aug 1997	2024-03-01	4572
Daewoo	Nexia	1.5	Stufenheck	Frontantrieb	Benzin	55	75	Feb 1995	Aug 1997	2024-03-01	4573
Daewoo	Nexia	1.5 16V	Stufenheck	Frontantrieb	Benzin	66	90	Feb 1995	Aug 1997	2024-03-01	4574
Daewoo	Tico	0.8	Schrägheck	Frontantrieb	Benzin	35	48	Feb 1995	Dec 2000	2024-03-01	4575
Hyundai	Pony	1.5 I	Stufenheck	Frontantrieb	Benzin	62	84	Jan 1990	Jan 1995	2024-03-01	4576
KIA	Sephia	1.6 I	Stufenheck	Frontantrieb	Benzin	59	80	Sep 1993	Oct 1997	2024-03-01	4577
KIA	Sephia	1.6 I	Schrägheck	Frontantrieb	Benzin	59	80	Jan 1995	Oct 1997	2024-03-01	4578
KIA	Sportage	2.0 I 4WD	SUV	Allrad	Benzin	70	95	Apr 1994	Aug 1999	2024-03-01	4579
KIA	Sportage	2.0 I 16V 4WD	SUV	Allrad	Benzin	94	128	Apr 1994	Aug 2003	2024-03-01	4580
Trabant	P 601	0.6	Stufenheck	Frontantrieb	Benzin	19	26	Mar 1970	Apr 1990	2024-03-01	4581
Trabant	P 601 universal	0.6	Kombi	Frontantrieb	Benzin	19	26	Jan 1966	Apr 1990	2024-03-01	4582
Trabant	P 601 tramp	0.6	Cabriolet	Frontantrieb	Benzin	19	26	Oct 1966	Apr 1990	2024-03-01	4583
Trabant	1.1	1.1	Stufenheck	Frontantrieb	Benzin	30	41	May 1990	Dec 1991	2024-03-01	4584
Trabant	1.1	1.1	Kombi	Frontantrieb	Benzin	30	41	Dec 1990	Dec 1991	2024-03-01	4585
Trabant	1.1	1.1	Cabriolet	Frontantrieb	Benzin	30	41	May 1990	Dec 1991	2024-03-01	4586
Wartburg	353	1	Stufenheck	Frontantrieb	Benzin	33	45	Jun 1966	Apr 1969	2024-03-01	4587
Wartburg	353	1	Stufenheck	Frontantrieb	Benzin	37	50	Feb 1975	Aug 1988	2024-03-01	4588
Wartburg	353	1.3	Stufenheck	Frontantrieb	Benzin	43	58	Sep 1988	May 1991	2024-03-01	4589
Wartburg	353	1	Kombi	Frontantrieb	Benzin	33	45	Oct 1967	Apr 1969	2024-03-01	4590
Wartburg	353	1	Kombi	Frontantrieb	Benzin	37	50	Feb 1975	Jan 1989	2024-03-01	4591
Wartburg	353	1.3	Kombi	Frontantrieb	Benzin	43	58	Feb 1989	May 1991	2024-03-01	4592
Wartburg	353	1	Kombi	Frontantrieb	Benzin	37	50	Apr 1969	Feb 1975	2024-03-01	4593
Wartburg	353	1	Stufenheck	Frontantrieb	Benzin	37	50	Apr 1969	Feb 1975	2024-03-01	4594
Jeep	Cherokee	2.5 I 4X4	Geländewagen geschlossen	Allrad	Benzin	90	122	Dec 1991	Sep 2001	2024-03-01	4595
Jeep	Cherokee	4.0 I	Geländewagen geschlossen	Allrad	Benzin	135	184	Dec 1991	Sep 2001	2024-03-01	4596
Jeep	Cherokee	4.0 I	Geländewagen geschlossen	Allrad	Benzin	136	185	Jan 1988	Sep 2001	2024-03-01	4597
Jeep	Cherokee	2.1 TD	Geländewagen geschlossen	Allrad	Diesel	64	87	Oct 1984	Sep 2001	2024-03-01	4598
Jeep	Cherokee	2.5 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	85	116	Jan 1988	Sep 2001	2024-03-01	4599
Jeep	Grand cherokee i	4.0 I 4X4	Geländewagen geschlossen	Allrad	Benzin	132	180	Jun 1992	Apr 1999	2024-03-01	4600
Jeep	Grand cherokee i	4.0 I 4X4	Geländewagen geschlossen	Allrad	Benzin	135	184	Sep 1991	Apr 1999	2024-03-01	4601
Jeep	Grand cherokee i	5.2 I 4X4	Geländewagen geschlossen	Allrad	Benzin	155	211	Jan 1992	Apr 1999	2024-03-01	4602
Jeep	Grand cherokee i	5.2 I 4X4	Geländewagen geschlossen	Allrad	Benzin	158	215	Sep 1992	Sep 1998	2024-03-01	4603
Chrysler	Voyager ii	2.5 I	Großraumlimousine	Frontantrieb	Benzin	72	98	Jan 1991	Sep 1995	2024-03-01	4604
Mazda	E	E2200 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	52	71	Apr 1997	Jul 1999	2024-03-01	4605
Chrysler	Voyager ii	3.0 I	Großraumlimousine	Frontantrieb	Benzin	108	147	Jan 1991	Sep 1995	2024-03-01	4606
Mazda	E	E2000	Pritsche/Fahrgestell	Heckantrieb	Benzin	71	97	Sep 1999	Sep 2004	2024-03-01	4607
Chrysler	Voyager ii	3.3 I	Großraumlimousine	Frontantrieb	Benzin	110	150	Aug 1990	Sep 1995	2024-03-01	4608
Chrysler	Voyager ii	3.3 I AWD	Großraumlimousine	Allrad	Benzin	110	150	Aug 1990	Sep 1995	2024-03-01	4609
Chrysler	Voyager ii	3.3 I	Großraumlimousine	Frontantrieb	Benzin	120	163	Aug 1990	Sep 1995	2024-03-01	4610
Chrysler	Voyager ii	3.3 I AWD	Großraumlimousine	Allrad	Benzin	120	163	Aug 1990	Sep 1995	2024-03-01	4611
Mazda	E	E2200 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	52	71	Sep 1999	Jul 2004	2024-03-01	4612
Audi	A4 b5	1.6	Stufenheck	Frontantrieb	Benzin	74	100	Nov 1994	Oct 2000	2024-03-01	4613
Audi	A4 b5	1.8	Stufenheck	Frontantrieb	Benzin	92	125	Nov 1994	Nov 2000	2024-03-01	4614
Audi	A4 b5	1.8 T	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1995	Nov 2000	2024-03-01	4615
Audi	A4 b5	2.6	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1995	Nov 2000	2024-03-01	4616
Audi	A4 b5	2.8	Stufenheck	Frontantrieb	Benzin	128	174	Sep 1995	Jul 1997	2024-03-01	4617
Audi	A4 b5	1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Jan 1995	Nov 2000	2024-03-01	4618
Audi	A4 b5	1.8 Quattro	Stufenheck	Allrad	Benzin	92	125	Jan 1995	Nov 2000	2024-03-01	4619
Audi	A4 b5	1.8 T Quattro	Stufenheck	Allrad	Benzin	110	150	Jan 1995	Nov 2000	2024-03-01	4620
Audi	A4 b5	2.6 Quattro	Stufenheck	Allrad	Benzin	110	150	Jan 1995	Nov 2000	2024-03-01	4621
Audi	A4 b5	2.8 Quattro	Stufenheck	Allrad	Benzin	128	174	Jan 1995	Jul 1997	2024-03-01	4622
BMW	3	320 I	Kombi	Heckantrieb	Benzin	110	150	Jan 1995	Apr 1999	2024-03-01	4623
BMW	3	328 I	Kombi	Heckantrieb	Benzin	142	193	Feb 1995	Apr 1999	2024-03-01	4624
BMW	3	318 TDS	Kombi	Heckantrieb	Diesel	66	90	Mar 1995	Apr 1999	2024-03-01	4625
BMW	3	325 TDS	Kombi	Heckantrieb	Diesel	105	143	Mar 1995	Apr 1999	2024-03-01	4626
BMW	3	328 I	Stufenheck	Heckantrieb	Benzin	142	193	Jan 1995	Apr 1998	2024-03-01	4627
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	125	170	May 1995	Nov 1998	2024-03-01	4628
BMW	3	328 I	Coupe	Heckantrieb	Benzin	142	193	Jan 1995	Apr 1999	2024-03-01	4629
BMW	3	328 I	Cabriolet	Heckantrieb	Benzin	142	193	Jan 1995	Nov 1999	2024-03-01	4630
BMW	5	518 I	Stufenheck	Heckantrieb	Benzin	85	115	May 1994	Aug 1995	2024-03-01	4631
BMW	5	518 I	Stufenheck	Heckantrieb	Benzin	83	113	Sep 1989	Apr 1994	2024-03-01	4632
BMW	5	525 TD	Kombi	Heckantrieb	Diesel	85	115	Mar 1993	Jul 1996	2024-03-01	4633
BMW	5	518 I	Kombi	Heckantrieb	Benzin	83	113	Apr 1993	Apr 1994	2024-03-01	4634
BMW	8	840 I	Coupe	Heckantrieb	Benzin	210	286	Mar 1993	Feb 1996	2024-03-01	4635
Audi	A6 c4	2	Stufenheck	Frontantrieb	Benzin	74	100	Jun 1994	Oct 1997	2024-03-01	4636
Audi	A6 c4	2	Stufenheck	Frontantrieb	Benzin	85	115	Jun 1994	Oct 1997	2024-03-01	4637
Audi	A6 c4	2.0 16V	Stufenheck	Frontantrieb	Benzin	103	140	Jun 1994	Oct 1997	2024-03-01	4638
Audi	A6 c4	2.6	Stufenheck	Frontantrieb	Benzin	110	150	Jun 1994	Oct 1997	2024-03-01	4639
Audi	A6 c4	2.8	Stufenheck	Frontantrieb	Benzin	128	174	Jun 1994	Oct 1997	2024-03-01	4640


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Hyundai Accent I、Lantra I、Pony X2、Sonata II/III，以及 Daewoo Espero、Nexia、Tico 的车身聚类和尺寸组闭合。
* Pony X2、Nexia 掀背车型确认存在三门和五门物理分支；由于三门、五门长宽高一致，各自拆分映射 `id`，但复用同一尺寸组。
* Mazda E2200 D 早期 Pritsche/Fahrgestell 直接复用跨批次已有尺寸组，不重复输出尺寸事实。
* 本轮新建尺寸组采用的宽度均为不含后视镜口径。([汽车目录][1])
* Sonata II、Sonata III、Espero 和 Tico 的三维已分别闭合，未把不同代际或车身形式合并。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 READY Ktype：33
* READY 映射行：40
* 尚待处理 Ktype：67
* 本轮首次创建尺寸组：10
* 本轮复用跨批次尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4541	4541	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4542	4542	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4543	4543	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4544	4544	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4545	4545	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4546	4546	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4547	4547	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4548	4548	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4549_3dr	4549	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4549_5dr	4549	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4550_3dr	4550	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4550_5dr	4550	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4551_3dr	4551	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4551_5dr	4551	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4552_3dr	4552	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4552_5dr	4552	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4553	4553	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
4554	4554	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
4558	4558	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4559	4559	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4560	4560	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4561	4561	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4562	4562	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4563	4563	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4564	4564	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4565	4565	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4566	4566	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	HIGH		READY
4567	4567	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4568	4568	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4569_3dr	4569	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4569_5dr	4569	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4570_3dr	4570	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4570_5dr	4570	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4571_3dr	4571	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4571_5dr	4571	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4572	4572	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4573	4573	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4574	4574	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4575	4575	Hatchback	Tico	KLY3	5	EU-DAEWOO-TICO-KLY3-HATCHBACK-5D-01	HIGH		READY
4576	4576	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	4117	1620	1394	Automobile-Catalog 1997 Hyundai Accent 1.3i GLS 4-Dr	https://www.automobile-catalog.com/car/1997/1162970/hyundai_accent_1_3i_gls_4-dr.html
EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	4358	1675	1385	Automobile-Catalog 1992 Hyundai Lantra 1.5i GL	https://www.automobile-catalog.com/car/1992/1158590/hyundai_lantra_1_5i_gl.html
EU-HYUNDAI-PONY-X2-HATCHBACK-01	4104	1603	1361	Automobile-Catalog 1993 Hyundai Pony 1.3 LS 3-Dr;Automobile-Catalog 1993 Hyundai Pony 1.5i GLS 5-Dr	https://www.automobile-catalog.com/car/1993/1159805/hyundai_pony_1_3_ls_3-dr_cat.html;https://www.automobile-catalog.com/car/1993/1160195/hyundai_pony_1_5i_gls_5-dr_cat.html
EU-HYUNDAI-PONY-X2-SEDAN-4D-01	4282	1603	1361	Automobile-Catalog 1991 Hyundai Pony 1.5 LS 4-Dr	https://www.automobile-catalog.com/car/1991/1160045/hyundai_pony_1_5_ls_4-dr_cat.html
EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	4680	1751	1408	Automobile-Catalog 1991 Hyundai Sonata 2.0i GLS	https://www.automobile-catalog.com/car/1991/1160930/hyundai_sonata_2_0i_gls.html
EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	4700	1770	1405	Automobile-Catalog 1993 Hyundai Sonata II 2.0 Gold	https://www.automobile-catalog.com/car/1993/1162055/hyundai_sonata_ii_2_0_gold.html
EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	4615	1718	1388	Automobile-Catalog 1995 Daewoo Espero 1.5	https://www.automobile-catalog.com/car/1995/555380/daewoo_espero_1_5.html
EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	4256	1662	1393	Automobile-Catalog 1995 Daewoo Nexia GTX Hatchback Automatic	https://www.automobile-catalog.com/car/1995/555140/daewoo_nexia_gtx_hatchback_automatic.html
EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	4482	1662	1393	Automobile-Catalog 1995 Daewoo Nexia GLX Sedan	https://www.automobile-catalog.com/car/1995/555170/daewoo_nexia_glx_sedan.html
EU-DAEWOO-TICO-KLY3-HATCHBACK-5D-01	3340	1400	1395	Automobile-Catalog 1995 Daewoo Tico SE	https://www.automobile-catalog.com/car/1995/2056760/daewoo_tico_se.html
```

## 下一步优先处理

1. 先解决 Hyundai S-Coupe 前期型、后期型来源中长宽高口径不一致的问题，确认 Ktype 4555–4557 是否需要按改款拆组。现有来源分别出现 `4215×1640×1328` 与 `4213×1626` 等差异，暂不创建猜测性尺寸组。([汽车数据][3])
2. 集中闭合 KIA Sephia、第一代 Sportage、Trabant P601/1.1 和 Wartburg 353 各车身形式。
3. 随后批量处理 Jeep XJ/ZJ、Chrysler Voyager II，并复用 Mazda E-Series 已有早期/晚期皮卡尺寸组。
4. 最后处理 Audi A4 B5、BMW E36/E34/E31、Audi A6 C4，优先命中跨批次已有 BMW/Audi 尺寸组。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1997/1162970/hyundai_accent_1_3i_gls_4-dr.html?utm_source=chatgpt.com "1997 Hyundai Accent 1.3i GLS 4-Dr Specs Review (62 kW ..."
[2]: https://www.automobile-catalog.com/car/1991/1160930/hyundai_sonata_2_0i_gls.html?utm_source=chatgpt.com "1991 Hyundai Sonata 2.0i GLS Specs Review (73.5 kW ..."
[3]: https://www.auto-data.net/en/hyundai-s-coupe-slc-generation-2964?utm_source=chatgpt.com "Hyundai S-Coupe (SLC) | Technical Specs, Fuel ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增 Hyundai S-Coupe、KIA Sephia、KIA Sportage、Trabant、Wartburg 和 Chrysler Voyager II 尺寸组。
* KIA Sportage Ktype `4580` 按早期车身与后期改款车身拆分。
* Trabant P 601 Sedan 按 1979 年前后长度变化拆分；P 601 Universal 按早期、后期高度变化拆分。
* Mazda E-Series Ktype `4605`、`4607`、`4612` 直接关联已有晚期 Pickup 尺寸组，未重复输出尺寸组。
* 本轮创建的尺寸组宽度均按不含后视镜口径落盘。([汽车数据][1])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 READY Ktype：63
* PENDING Ktype：37
* READY 映射行：73
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4555	4555	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4556	4556	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4557	4557	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4577	4577	Sedan	Sephia I	FA	4	EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	HIGH		READY
4578	4578	Hatchback	Sephia I	FA	5	EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	HIGH		READY
4579	4579	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH		READY
4580_prefl	4580	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH	早期车身物理外廓。	READY
4580_facelift	4580	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	HIGH	后期改款车身物理外廓。	READY
4581_pre79	4581	Sedan	P 601	P601	2	EU-TRABANT-P601-SEDAN-PRE79-01	HIGH	1979年前标准车身长度。	READY
4581_post79	4581	Sedan	P 601	P601	2	EU-TRABANT-P601-SEDAN-POST79-01	HIGH	1979年后短保险杠外廓。	READY
4582_pre72	4582	Wagon	P 601 Universal	P601	3	EU-TRABANT-P601-UNIVERSAL-WAGON-PRE72-01	HIGH	早期Universal车身高度。	READY
4582_post72	4582	Wagon	P 601 Universal	P601	3	EU-TRABANT-P601-UNIVERSAL-WAGON-POST72-01	HIGH	后期Universal车身高度。	READY
4583	4583	Convertible	P 601 Tramp	P601	2	EU-TRABANT-P601-TRAMP-CONVERTIBLE-01	HIGH		READY
4584	4584	Sedan	Trabant 1.1	1.1	2	EU-TRABANT-1-1-SEDAN-2D-01	HIGH		READY
4585	4585	Wagon	Trabant 1.1 Universal	1.1	3	EU-TRABANT-1-1-UNIVERSAL-WAGON-3D-01	HIGH		READY
4586	4586	Convertible	Trabant 1.1 Tramp	1.1	2	EU-TRABANT-1-1-TRAMP-CONVERTIBLE-01	HIGH		READY
4587	4587	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4588	4588	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4589	4589	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4590	4590	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4591	4591	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4592	4592	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4593	4593	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4594	4594	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4604	4604	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4605	4605	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
4606	4606	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4607	4607	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
4608	4608	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4609	4609	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4610	4610	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4611	4611	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4612	4612	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	4215	1640	1328	Auto-Data Hyundai S-Coupe SLC	https://www.auto-data.net/en/hyundai-s-coupe-slc-generation-2964
EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	4280	1692	1390	Automobile-Catalog 1995 Kia Sephia SLX	https://www.automobile-catalog.com/car/1995/1341500/kia_sephia_slx.html
EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	4280	1692	1390	Auto-Data Kia Sephia Hatchback FA	https://www.auto-data.net/en/kia-sephia-hatchback-fa-generation-630
EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	4335	1730	1695	CarsGuide 1997 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/1997
EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	4435	1765	1655	CarsGuide 2001 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/2001
EU-TRABANT-P601-SEDAN-PRE79-01	3555	1505	1440	Automobile-Catalog 1972 Trabant 601	https://www.automobile-catalog.com/car/1972/3545750/trabant_601.html
EU-TRABANT-P601-SEDAN-POST79-01	3510	1505	1440	Automobile-Catalog 1979 Trabant 601	https://www.automobile-catalog.com/car/1979/3545840/trabant_601.html
EU-TRABANT-P601-UNIVERSAL-WAGON-PRE72-01	3560	1510	1437	Automobile-Catalog 1970 Trabant 601 Universal	https://www.automobile-catalog.com/car/1970/3545660/trabant_601_universal.html
EU-TRABANT-P601-UNIVERSAL-WAGON-POST72-01	3560	1510	1470	Automobile-Catalog 1972 Trabant 601 Universal	https://www.automobile-catalog.com/car/1972/3545795/trabant_601_universal.html
EU-TRABANT-P601-TRAMP-CONVERTIBLE-01	3480	1506	1465	Trabant 601 Tramp official brochure archive	https://autocatalogarchive.com/wp-content/uploads/2025/05/Trabant-601-Tramp-1983-INT.pdf
EU-TRABANT-1-1-SEDAN-2D-01	3521	1528	1420	Automobile-Catalog 1990 Trabant 1.1	https://www.automobile-catalog.com/car/1990/3545975/trabant_1_1.html
EU-TRABANT-1-1-UNIVERSAL-WAGON-3D-01	3521	1528	1440	Automobile-Catalog 1990 Trabant 1.1 Universal	https://www.automobile-catalog.com/car/1990/3545990/trabant_1_1_universal.html
EU-TRABANT-1-1-TRAMP-CONVERTIBLE-01	3615	1540	1520	Automobile-Catalog 1990 Trabant 1.1 Tramp	https://www.automobile-catalog.com/car/1990/3546005/trabant_1_1_tramp.html
EU-WARTBURG-353-SEDAN-4D-01	4220	1640	1495	Automobile-Catalog 1975 Wartburg 353	https://www.automobile-catalog.com/car/1975/39965/wartburg_353.html
EU-WARTBURG-353-TOURIST-WAGON-5D-01	4380	1640	1495	Automobile-Catalog 1985 Wartburg 353 W Tourist	https://www.automobile-catalog.com/car/1985/50015/wartburg_353_w_tourist.html
EU-CHRYSLER-VOYAGER-II-ES-MPV-01	4525	1830	1707	Auto-Data Chrysler Voyager II	https://www.auto-data.net/en/chrysler-voyager-ii-generation-8878
```

## 下一步优先处理

1. 闭合 Jeep Cherokee XJ 的门数分支及不同年份外廓变化。
2. 闭合 Jeep Grand Cherokee ZJ 改款前后长度差异。
3. 处理 Audi A4 B5 Sedan，并批量复用 BMW E36、E34、E31 和 Audi A6 C4 已有尺寸组。
4. 完成剩余 37 个 Ktype 后立即执行机械收尾并输出两张完整 TSV。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/hyundai-s-coupe-model-1475?utm_source=chatgpt.com "Hyundai S-Coupe | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已完成剩余 Jeep Cherokee XJ、Grand Cherokee ZJ、Audi A4 B5、BMW E36 Touring 等映射；BMW E36/E34/E31、Audi A6 C4 和 Mazda E-Series 已有尺寸组按缓存直接复用。XJ 按早期、改款前、改款后三种外廓处理，ZJ 按改款前后处理。([汽车目录][1])
* 已完成最终机械检查：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，尺寸及来源字段完整。
* 本批次已无 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* 已覆盖 Ktype：100
* READY 映射：131
* PENDING 映射：0
* DIMENSION_GROUP：42
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
4541	4541	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4542	4542	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4543	4543	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4544	4544	Sedan	Accent I	X3	4	EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	HIGH		READY
4545	4545	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4546	4546	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4547	4547	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4548	4548	Sedan	Lantra I	J1	4	EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	HIGH		READY
4549_3dr	4549	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4549_5dr	4549	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4550_3dr	4550	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4550_5dr	4550	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4551_3dr	4551	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4551_5dr	4551	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4552_3dr	4552	Hatchback	Pony X2	X2	3	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4552_5dr	4552	Hatchback	Pony X2	X2	5	EU-HYUNDAI-PONY-X2-HATCHBACK-01	HIGH	X2五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4553	4553	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
4554	4554	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
4555	4555	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4556	4556	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4557	4557	Coupe	S-Coupe	SLC	2	EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	HIGH		READY
4558	4558	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4559	4559	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4560	4560	Sedan	Sonata II	Y2	4	EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	HIGH		READY
4561	4561	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4562	4562	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4563	4563	Sedan	Sonata III	Y3	4	EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	HIGH		READY
4564	4564	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4565	4565	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4566	4566	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	HIGH		READY
4567	4567	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4568	4568	Sedan	Espero	KLEJ	4	EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	HIGH		READY
4569_3dr	4569	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4569_5dr	4569	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4570_3dr	4570	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4570_5dr	4570	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4571_3dr	4571	Hatchback	Nexia I	KLETN	3	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN三门掀背物理分支；与五门复用同一外廓尺寸组。	READY
4571_5dr	4571	Hatchback	Nexia I	KLETN	5	EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	HIGH	KLETN五门掀背物理分支；与三门复用同一外廓尺寸组。	READY
4572	4572	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4573	4573	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4574	4574	Sedan	Nexia I	KLETN	4	EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	HIGH		READY
4575	4575	Hatchback	Tico	KLY3	5	EU-DAEWOO-TICO-KLY3-HATCHBACK-5D-01	HIGH		READY
4576	4576	Sedan	Pony X2	X2	4	EU-HYUNDAI-PONY-X2-SEDAN-4D-01	HIGH		READY
4577	4577	Sedan	Sephia I	FA	4	EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	HIGH		READY
4578	4578	Hatchback	Sephia I	FA	5	EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	HIGH		READY
4579	4579	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH		READY
4580_prefl	4580	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	HIGH	早期车身物理外廓。	READY
4580_facelift	4580	SUV	Sportage I	JA	5	EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	HIGH	后期改款车身物理外廓。	READY
4581_pre79	4581	Sedan	P 601	P601	2	EU-TRABANT-P601-SEDAN-PRE79-01	HIGH	1979年前标准车身长度。	READY
4581_post79	4581	Sedan	P 601	P601	2	EU-TRABANT-P601-SEDAN-POST79-01	HIGH	1979年后短保险杠外廓。	READY
4582_pre72	4582	Wagon	P 601 Universal	P601	3	EU-TRABANT-P601-UNIVERSAL-WAGON-PRE72-01	HIGH	早期Universal车身高度。	READY
4582_post72	4582	Wagon	P 601 Universal	P601	3	EU-TRABANT-P601-UNIVERSAL-WAGON-POST72-01	HIGH	后期Universal车身高度。	READY
4583	4583	Convertible	P 601 Tramp	P601	2	EU-TRABANT-P601-TRAMP-CONVERTIBLE-01	HIGH		READY
4584	4584	Sedan	Trabant 1.1	1.1	2	EU-TRABANT-1-1-SEDAN-2D-01	HIGH		READY
4585	4585	Wagon	Trabant 1.1 Universal	1.1	3	EU-TRABANT-1-1-UNIVERSAL-WAGON-3D-01	HIGH		READY
4586	4586	Convertible	Trabant 1.1 Tramp	1.1	2	EU-TRABANT-1-1-TRAMP-CONVERTIBLE-01	HIGH		READY
4587	4587	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4588	4588	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4589	4589	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4590	4590	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4591	4591	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4592	4592	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4593	4593	Wagon	Wartburg 353 Tourist	353	5	EU-WARTBURG-353-TOURIST-WAGON-5D-01	HIGH		READY
4594	4594	Sedan	Wartburg 353	353	4	EU-WARTBURG-353-SEDAN-4D-01	HIGH		READY
4595_2dr_prefl	4595	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	2门1991–1996改款前外廓。	READY
4595_2dr_facelift	4595	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	2门1997–2001改款后外廓。	READY
4595_4dr_prefl	4595	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	4门1991–1996改款前外廓。	READY
4595_4dr_facelift	4595	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	4门1997–2001改款后外廓。	READY
4596_2dr_prefl	4596	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	2门1991–1996改款前外廓。	READY
4596_2dr_facelift	4596	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	2门1997–2001改款后外廓。	READY
4596_4dr_prefl	4596	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	4门1991–1996改款前外廓。	READY
4596_4dr_facelift	4596	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	4门1997–2001改款后外廓。	READY
4597_2dr_early	4597	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	HIGH	2门1984–1990早期外廓。	READY
4597_2dr_prefl	4597	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	2门1991–1996改款前外廓。	READY
4597_2dr_facelift	4597	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	2门1997–2001改款后外廓。	READY
4597_4dr_early	4597	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	HIGH	4门1984–1990早期外廓。	READY
4597_4dr_prefl	4597	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	4门1991–1996改款前外廓。	READY
4597_4dr_facelift	4597	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	4门1997–2001改款后外廓。	READY
4598_2dr_early	4598	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	HIGH	2门1984–1990早期外廓。	READY
4598_2dr_prefl	4598	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	2门1991–1996改款前外廓。	READY
4598_4dr_early	4598	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	HIGH	4门1984–1990早期外廓。	READY
4598_4dr_prefl	4598	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	4门1991–1996改款前外廓。	READY
4599_2dr_prefl	4599	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	2门1991–1996改款前外廓。	READY
4599_2dr_facelift	4599	SUV	Cherokee II (XJ)	XJ	2	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	2门1997–2001改款后外廓。	READY
4599_4dr_prefl	4599	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	HIGH	4门1991–1996改款前外廓。	READY
4599_4dr_facelift	4599	SUV	Cherokee II (XJ)	XJ	4	EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	HIGH	4门1997–2001改款后外廓。	READY
4600_prefl	4600	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	HIGH	1992–1995改款前外廓。	READY
4600_facelift	4600	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH	1996–1998改款后外廓。	READY
4601_prefl	4601	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	HIGH	1992–1995改款前外廓。	READY
4601_facelift	4601	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH	1996–1998改款后外廓。	READY
4602_prefl	4602	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	HIGH	1992–1995改款前外廓。	READY
4602_facelift	4602	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH	1996–1998改款后外廓。	READY
4603_prefl	4603	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	HIGH	1992–1995改款前外廓。	READY
4603_facelift	4603	SUV	Grand Cherokee I	ZJ	4	EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	HIGH	1996–1998改款后外廓。	READY
4604	4604	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4605	4605	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
4606	4606	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4607	4607	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
4608	4608	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4609	4609	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4610	4610	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4611	4611	MPV	Voyager II	ES	4	EU-CHRYSLER-VOYAGER-II-ES-MPV-01	HIGH		READY
4612	4612	Pickup	E-Series III	SR	2	EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	HIGH		READY
4613	4613	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4614	4614	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4615	4615	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4616	4616	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4617	4617	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4618	4618	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4619	4619	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4620	4620	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4621	4621	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4622	4622	Sedan	A4 B5	8D2	4	EU-AUDI-A4-B5-SEDAN-4D-01	HIGH		READY
4623	4623	Wagon	3 Series E36	E36/3	5	EU-BMW-3-SERIES-E36-TOURING-5D-01	HIGH		READY
4624	4624	Wagon	3 Series E36	E36/3	5	EU-BMW-3-SERIES-E36-TOURING-5D-01	HIGH		READY
4625	4625	Wagon	3 Series E36	E36/3	5	EU-BMW-3-SERIES-E36-TOURING-5D-01	HIGH		READY
4626	4626	Wagon	3 Series E36	E36/3	5	EU-BMW-3-SERIES-E36-TOURING-5D-01	HIGH		READY
4627	4627	Sedan	3 Series E36	E36/4	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH		READY
4628	4628	Sedan	3 Series E36	E36/4	4	EU-BMW-3-SERIES-E36-SEDAN-01	HIGH		READY
4629	4629	Coupe	3 Series E36	E36/2	2	EU-BMW-3-SERIES-E36-COUPE-01	HIGH		READY
4630	4630	Convertible	3 Series E36	E36/2C	2	EU-BMW-3-E36-CONVERTIBLE-01	HIGH		READY
4631	4631	Sedan	5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
4632	4632	Sedan	5 Series E34	E34	4	EU-BMW-5-E34-SEDAN-01	HIGH		READY
4633	4633	Wagon	5 Series E34	E34/5	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
4634	4634	Wagon	5 Series E34	E34/5	5	EU-BMW-5-E34-WAGON-01	HIGH		READY
4635	4635	Coupe	8 Series E31	E31	2	EU-BMW-8-E31-COUPE-850-01	HIGH		READY
4636	4636	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4637	4637	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4638	4638	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4639	4639	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
4640	4640	Sedan	A6 C4	4A2	4	EU-AUDI-A6-C4-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4401-4500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ACCENT-I-X3-SEDAN-4D-01	4117	1620	1394	Automobile-Catalog 1997 Hyundai Accent 1.3i GLS 4-Dr	https://www.automobile-catalog.com/car/1997/1162970/hyundai_accent_1_3i_gls_4-dr.html
EU-HYUNDAI-LANTRA-I-J1-SEDAN-4D-01	4358	1675	1385	Automobile-Catalog 1992 Hyundai Lantra 1.5i GL	https://www.automobile-catalog.com/car/1992/1158590/hyundai_lantra_1_5i_gl.html
EU-HYUNDAI-PONY-X2-HATCHBACK-01	4104	1603	1361	Automobile-Catalog 1993 Hyundai Pony 1.3 LS 3-Dr;Automobile-Catalog 1993 Hyundai Pony 1.5i GLS 5-Dr	https://www.automobile-catalog.com/car/1993/1159805/hyundai_pony_1_3_ls_3-dr_cat.html;https://www.automobile-catalog.com/car/1993/1160195/hyundai_pony_1_5i_gls_5-dr_cat.html
EU-HYUNDAI-PONY-X2-SEDAN-4D-01	4282	1603	1361	Automobile-Catalog 1991 Hyundai Pony 1.5 LS 4-Dr	https://www.automobile-catalog.com/car/1991/1160045/hyundai_pony_1_5_ls_4-dr_cat.html
EU-HYUNDAI-S-COUPE-SLC-COUPE-2D-01	4215	1640	1328	Auto-Data Hyundai S-Coupe SLC	https://www.auto-data.net/en/hyundai-s-coupe-slc-generation-2964
EU-HYUNDAI-SONATA-II-Y2-SEDAN-FACELIFT-01	4680	1751	1408	Automobile-Catalog 1991 Hyundai Sonata 2.0i GLS	https://www.automobile-catalog.com/car/1991/1160930/hyundai_sonata_2_0i_gls.html
EU-HYUNDAI-SONATA-III-Y3-SEDAN-4D-01	4700	1770	1405	Automobile-Catalog 1993 Hyundai Sonata II 2.0 Gold	https://www.automobile-catalog.com/car/1993/1162055/hyundai_sonata_ii_2_0_gold.html
EU-DAEWOO-ESPERO-KLEJ-SEDAN-4D-01	4615	1718	1388	Automobile-Catalog 1995 Daewoo Espero 1.5	https://www.automobile-catalog.com/car/1995/555380/daewoo_espero_1_5.html
EU-MAZDA-E-SERIES-III-SR-PICKUP-EARLY-01	4390	1690	1960	CarsGuide Mazda E2200 dimensions 1990	https://www.carsguide.com.au/mazda/e2200/car-dimensions/1990
EU-DAEWOO-NEXIA-KLETN-HATCHBACK-01	4256	1662	1393	Automobile-Catalog 1995 Daewoo Nexia GTX Hatchback Automatic	https://www.automobile-catalog.com/car/1995/555140/daewoo_nexia_gtx_hatchback_automatic.html
EU-DAEWOO-NEXIA-KLETN-SEDAN-4D-01	4482	1662	1393	Automobile-Catalog 1995 Daewoo Nexia GLX Sedan	https://www.automobile-catalog.com/car/1995/555170/daewoo_nexia_glx_sedan.html
EU-DAEWOO-TICO-KLY3-HATCHBACK-5D-01	3340	1400	1395	Automobile-Catalog 1995 Daewoo Tico SE	https://www.automobile-catalog.com/car/1995/2056760/daewoo_tico_se.html
EU-KIA-SEPHIA-I-FA-SEDAN-4D-01	4280	1692	1390	Automobile-Catalog 1995 Kia Sephia SLX	https://www.automobile-catalog.com/car/1995/1341500/kia_sephia_slx.html
EU-KIA-SEPHIA-I-FA-HATCHBACK-5D-01	4280	1692	1390	Auto-Data Kia Sephia Hatchback FA	https://www.auto-data.net/en/kia-sephia-hatchback-fa-generation-630
EU-KIA-SPORTAGE-I-JA-SUV-PREFL-01	4335	1730	1695	CarsGuide 1997 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/1997
EU-KIA-SPORTAGE-I-JA-SUV-FACELIFT-01	4435	1765	1655	CarsGuide 2001 Kia Sportage dimensions	https://www.carsguide.com.au/kia/sportage/car-dimensions/2001
EU-TRABANT-P601-SEDAN-PRE79-01	3555	1505	1440	Automobile-Catalog 1972 Trabant 601	https://www.automobile-catalog.com/car/1972/3545750/trabant_601.html
EU-TRABANT-P601-SEDAN-POST79-01	3510	1505	1440	Automobile-Catalog 1979 Trabant 601	https://www.automobile-catalog.com/car/1979/3545840/trabant_601.html
EU-TRABANT-P601-UNIVERSAL-WAGON-PRE72-01	3560	1510	1437	Automobile-Catalog 1970 Trabant 601 Universal	https://www.automobile-catalog.com/car/1970/3545660/trabant_601_universal.html
EU-TRABANT-P601-UNIVERSAL-WAGON-POST72-01	3560	1510	1470	Automobile-Catalog 1972 Trabant 601 Universal	https://www.automobile-catalog.com/car/1972/3545795/trabant_601_universal.html
EU-TRABANT-P601-TRAMP-CONVERTIBLE-01	3480	1506	1465	Trabant 601 Tramp official brochure archive	https://autocatalogarchive.com/wp-content/uploads/2025/05/Trabant-601-Tramp-1983-INT.pdf
EU-TRABANT-1-1-SEDAN-2D-01	3521	1528	1420	Automobile-Catalog 1990 Trabant 1.1	https://www.automobile-catalog.com/car/1990/3545975/trabant_1_1.html
EU-TRABANT-1-1-UNIVERSAL-WAGON-3D-01	3521	1528	1440	Automobile-Catalog 1990 Trabant 1.1 Universal	https://www.automobile-catalog.com/car/1990/3545990/trabant_1_1_universal.html
EU-TRABANT-1-1-TRAMP-CONVERTIBLE-01	3615	1540	1520	Automobile-Catalog 1990 Trabant 1.1 Tramp	https://www.automobile-catalog.com/car/1990/3546005/trabant_1_1_tramp.html
EU-WARTBURG-353-SEDAN-4D-01	4220	1640	1495	Automobile-Catalog 1975 Wartburg 353	https://www.automobile-catalog.com/car/1975/39965/wartburg_353.html
EU-WARTBURG-353-TOURIST-WAGON-5D-01	4380	1640	1495	Automobile-Catalog 1985 Wartburg 353 W Tourist	https://www.automobile-catalog.com/car/1985/50015/wartburg_353_w_tourist.html
EU-JEEP-CHEROKEE-II-XJ-SUV-PREFL-01	4240	1790	1623	Automobile-Catalog 1992 Jeep Cherokee Limited 4.0 High Output	https://www.automobile-catalog.com/car/1992/1313240/jeep_cherokee_limited_4_0_high_output.html
EU-JEEP-CHEROKEE-II-XJ-SUV-FACELIFT-01	4251	1790	1625	Automobile-Catalog 1997 Jeep Cherokee 4.0 Sport	https://www.automobile-catalog.com/car/1997/1575005/jeep_cherokee_4_0_sport.html
EU-JEEP-CHEROKEE-II-XJ-SUV-EARLY-01	4200	1790	1624	Automobile-Catalog 1986 Jeep Cherokee Chief 2-Door 2.5L	https://www.automobile-catalog.com/car/1986/1309070/jeep_cherokee_chief_2-door_2_5l_5-speed.html
EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-PREFL-01	4489	1790	1708	Automobile-Catalog 1994 Jeep Grand Cherokee 4.0 Limited Quadra-Trac	https://www.automobile-catalog.com/car/1994/1320050/jeep_grand_cherokee_4_0_limited_quadra-trac_automatic.html
EU-JEEP-GRAND-CHEROKEE-I-ZJ-SUV-FACELIFT-01	4500	1800	1690	Automobile-Catalog 1997 Jeep Grand Cherokee 4.0 TSi	https://www.automobile-catalog.com/car/1997/1321445/jeep_grand_cherokee_4_0_tsi.html
EU-CHRYSLER-VOYAGER-II-ES-MPV-01	4525	1830	1707	Auto-Data Chrysler Voyager II	https://www.auto-data.net/en/chrysler-voyager-ii-generation-8878
EU-MAZDA-E-SERIES-III-SR-PICKUP-LATE-01	4690	1690	1960	Carsales 1999 Mazda E2000	https://www.carsales.com.au/research/mazda/e2000/1999/no-badge/b277dcac-e679-43b6-94ff-81690b2a1a6d/
EU-AUDI-A4-B5-SEDAN-4D-01	4479	1733	1415	Automobile-Catalog 1997 Audi A4 1.6	https://www.automobile-catalog.com/car/1997/240860/audi_a4_1_6.html
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391	Automobile-Catalog 1996 BMW 320i Touring	https://www.automobile-catalog.com/car/1996/270755/bmw_320i_touring.html
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	CarsGuide 1995 BMW 320i dimensions	https://www.carsguide.com.au/bmw/3-series/320i/car-dimensions/1995
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	Automobile-Catalog 1994 BMW 325i Coupe	https://www.automobile-catalog.com/car/1994/270110/bmw_325i_coupe.html
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348	Automobile-Catalog 1996 BMW 318i Convertible	https://www.automobile-catalog.com/car/1996/271190/bmw_318i_convertible.html
EU-BMW-5-E34-SEDAN-01	4720	1751	1412	Automobile-Catalog 1992 BMW 525i automatic catalyst	https://www.automobile-catalog.com/car/1992/268445/bmw_525i_automatic_cat.html
EU-BMW-5-E34-WAGON-01	4720	1751	1417	Auto-Data BMW 5 Series Touring E34 525td	https://www.auto-data.net/en/bmw-5-series-touring-e34-525td-115hp-9661
EU-BMW-8-E31-COUPE-850-01	4780	1855	1340	Automobile-Catalog 1995 BMW 840 Ci	https://www.automobile-catalog.com/car/1995/269210/bmw_840_ci.html
EU-AUDI-A6-C4-SEDAN-01	4797	1783	1430	Automobile-Catalog 1994 Audi A6	https://www.automobile-catalog.com/car/1994/239030/audi_a6.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4401-4500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1992/1313240/jeep_cherokee_limited_4_0_high_output.html?utm_source=chatgpt.com "1992 Jeep Cherokee Limited 4.0 High Output (aut. 4)"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4401-4500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4401-4500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5958 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1817 行）

