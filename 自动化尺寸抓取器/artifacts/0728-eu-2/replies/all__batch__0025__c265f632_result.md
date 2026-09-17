# 任务：all 第 2401-2500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0025__c265f632


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 2401-2500 行

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
all 第 2401-2500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390
EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	4435	1743	1430
EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	4430	1745	1415
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-A4-B8-FACELIFT-SEDAN-01	4701	1826	1427
EU-AUDI-A4-B8-FACELIFT-WAGON-01	4699	1826	1436
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398
EU-BENTLEY-CONTINENTAL-GTC-II-CONVERTIBLE-01	4806	1943	1403
EU-BENTLEY-CONTINENTAL-GT-I-3W-COUPE-SPEED-01	4804	1916	1380
EU-BENTLEY-CONTINENTAL-GT-II-COUPE-01	4806	1943	1404
EU-BENTLEY-CONTINENTAL-R-COUPE-01	5342	1872	1462
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-CHEVROLET-AVEO-KALOS-T200-SEDAN-01	4235	1670	1495
EU-CHEVROLET-AVEO-T255-HATCHBACK-3D-01	3920	1680	1505
EU-CHEVROLET-AVEO-T255-HATCHBACK-5D-01	3920	1680	1505
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783
EU-FIAT-BRAVO-I-HATCHBACK-3D-01	4025	1755	1420
EU-FIAT-BRAVO-II-198-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-BRAVO-II-HATCHBACK-5D-01	4336	1792	1498
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	5681	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	5681	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	5181	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	5181	1932	2125
EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	4831	1932	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	5980	2040	2100
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	5980	2040	2125
EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	5998	2050	2524
EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	5413	2050	2524
EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	4963	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779
EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	5599	2024	2470
EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	5099	2024	2470
EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	5099	2024	2480
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X230-TRUCK-LWB-01	5620	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-MWB-01	5120	2000	2100
EU-FIAT-DUCATO-X230-TRUCK-SWB-01	4770	2000	2100
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154
EU-FIAT-DUCATO-X244-BODY-15-LWB-HIGHROOF-01	5599	2024	2850
EU-FIAT-DUCATO-X244-BODY-15-LWB-MIDROOF-01	5599	2024	2470
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-HIGHROOF-01	5599	2024	2860
EU-FIAT-DUCATO-X244-BODY-MAXI-LWB-MIDROOF-01	5599	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-HIGHROOF-01	5099	2024	2735
EU-FIAT-DUCATO-X244-BODY-MAXI-MWB-LOWROOF-01	5099	2024	2160
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-HIGHROOF-01	4749	2024	2480
EU-FIAT-DUCATO-X244-BODY-MAXI-SWB-LOWROOF-01	4749	2024	2160
EU-FIAT-DUCATO-X244-BODY-MWB-HIGHROOF-01	5099	2024	2725
EU-FIAT-DUCATO-X244-BODY-MWB-LOWROOF-01	5099	2024	2150
EU-FIAT-DUCATO-X244-BODY-SWB-HIGHROOF-01	4749	2024	2470
EU-FIAT-DUCATO-X244-TRUCK-LWB-MAXI-01	5861	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-LWB-STANDARD-01	5861	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-MWB-MAXI-01	5181	2024	2125
EU-FIAT-DUCATO-X244-TRUCK-MWB-STANDARD-01	5181	2024	2100
EU-FIAT-DUCATO-X244-TRUCK-SWB-STANDARD-01	4831	2024	2100
EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	3585	1595	1540
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540
EU-JAGUAR-XJ-XJ40-SEDAN-4D-01	4990	1800	1360
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500
EU-LADA-KALINA-I-SEDAN-4D-01	4040	1700	1500
EU-OPEL-COMBO-TOUR-C-FACELIFT-MPV-5D-01	4322	1684	1801
EU-OPEL-INSIGNIA-A-FACELIFT-HATCHBACK-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513
EU-PEUGEOT-EXPERT-I-BUS-01	4440	1810	1940
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-CHASSIS-CAB-01	5016	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-LWB-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-MPV-SWB-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L1H1-02	4805	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1942
EU-PEUGEOT-EXPERT-II-VAN-L2H1-02	5135	1895	1880
EU-PEUGEOT-EXPERT-II-VAN-L2H2-01	5135	1895	2276
EU-PEUGEOT-EXPERT-I-VAN-01	4440	1810	1940
EU-PEUGEOT-J5-I-VAN-LWB-HIGHROOF-01	5489	1965	2420
EU-PEUGEOT-J5-I-VAN-LWB-LOWROOF-01	5489	1965	2108
EU-PEUGEOT-J5-I-VAN-SWB-HIGHROOF-01	4759	1965	2420
EU-PEUGEOT-J5-I-VAN-SWB-LOWROOF-01	4759	1965	2108
EU-PEUGEOT-PARTNER-II-B9-VAN-L1-01	4380	1810	1834
EU-PEUGEOT-PARTNER-II-B9-VAN-L2-01	4628	1810	1834
EU-PEUGEOT-PARTNER-II-TEPEE-MPV-5D-01	4380	1810	1803
EU-PEUGEOT-PARTNER-I-PHASE-II-VAN-MPV-01	4140	1720	1810
EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	4520	1855	1695
EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	4520	1855	1695
EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	4520	1865	1695
EU-SAAB-900-I-SEDAN-4D-01	4680	1690	1422
EU-SEAT-IBIZA-III-6L-FACELIFT-HATCHBACK-3D-01	3977	1698	1441
EU-SEAT-IBIZA-III-6L-FACELIFT-HATCHBACK-5D-01	3977	1698	1441
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-3D-01	3977	1698	1441
EU-SEAT-IBIZA-III-FACELIFT-HATCHBACK-5D-01	3977	1698	1441
EU-SEAT-IBIZA-III-HATCHBACK-3D-01	3955	1700	1440
EU-SEAT-IBIZA-III-HATCHBACK-5D-01	3955	1700	1440
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680
EU-SUZUKI-SWIFT-III-HATCHBACK-3D-01	3695	1690	1500
EU-SUZUKI-SWIFT-III-HATCHBACK-5D-01	3695	1690	1500
EU-TOYOTA-HIACE-IV-BUS-LWB-01	5240	1800	1995
EU-TOYOTA-HIACE-IV-BUS-SWB-01	4795	1800	2000
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH18-01	4715	1800	1955
EU-TOYOTA-HIACE-IV-XH10-VAN-KLH28-01	5160	1800	1955
EU-VOLVO-V70-III-WAGON-5D-PREFL-01	4823	1861	1547
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Renault	Koleos i	2.0 DCI 4X4	SUV	Allrad	Diesel	110	150	Sep 2008	-	2024-03-01	26654
Renault	Koleos i	2.0 DCI 4X4	SUV	Allrad	Diesel	127	173	Sep 2008	-	2024-03-01	26655
Lada	Priora	1.6	Stufenheck	Frontantrieb	Benzin	72	98	Apr 2007	Jul 2018	2024-03-01	26656
Lada	Priora	1.6	Schrägheck	Frontantrieb	Benzin	72	98	Dec 2008	Dec 2015	2024-03-01	26657
Lada	Kalina	1.6	Kombi	Frontantrieb	Benzin	60	82	Oct 2007	Dec 2013	2024-03-01	26658
Fiat	Fiorino	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	54	73	Nov 2007	-	2024-03-01	26659
Fiat	Fiorino	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Nov 2007	-	2024-03-01	26660
Suzuki	Ignis ii	1.3 4X4	Schrägheck	Allrad	Benzin	69	94	Sep 2003	-	2024-03-01	26661
Mercedes-benz	Slk	350	Cabriolet	Heckantrieb	Benzin	224	305	Jan 2008	Feb 2011	2024-03-01	26662
Mercedes-benz	Slk	200 Kompressor	Cabriolet	Heckantrieb	Benzin	135	184	Jan 2008	Feb 2011	2024-03-01	26663
Ford	Fiesta v van	1.3	Kasten/Schrägheck	Frontantrieb	Benzin	51	69	Oct 2003	Jul 2005	2024-03-01	26669
Ford	Fiesta v van	1.4 Tdci	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Oct 2003	Dec 2010	2024-03-01	26670
Cadillac	Escalade	6.2	SUV	Heckantrieb	Benzin	301	409	Oct 2006	Dec 2014	2024-03-01	26695
Cadillac	Escalade	6.2 AWD	SUV	Allrad	Benzin	301	409	Oct 2006	Dec 2014	2024-03-01	26696
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	125	170	Nov 2011	Dec 2016	2024-03-01	26732
VW	Cc b7	3.6 FSI 4motion	Coupe	Allrad	Benzin	220	300	Nov 2011	Dec 2016	2024-03-01	26739
VW	Cc b7	2.0 TSI	Coupe	Frontantrieb	Benzin	155	210	Nov 2011	Dec 2016	2024-03-01	26740
Opel	Combo tour	1.4 CNG	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	88	120	Feb 2012	-	2024-03-01	26742
VW	Golf vii variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	110	150	Apr 2013	Aug 2020	2024-03-01	26743
VW	Cc b7	2.0 TDI	Coupe	Frontantrieb	Diesel	103	140	Nov 2011	Dec 2016	2024-03-01	26752
VW	Golf vii variant	1.4 TSI	Kombi	Frontantrieb	Benzin	103	140	May 2013	Aug 2020	2024-03-01	26753
Fiat	Ducato	2.0 4X4	Bus	Allrad	Benzin	81	110	May 2002	Jul 2006	2024-03-01	26754
Fiat	Ducato	2.0 4X4	Kasten	Allrad	Benzin	81	110	May 2002	Jul 2006	2024-03-01	26755
VW	Golf vii variant	1.6 TDI 4motion	Kombi	Allrad	Diesel	77	105	May 2013	Mar 2017	2024-03-01	26760
VW	Golf vii variant	1.6 TDI	Kombi	Frontantrieb	Diesel	66	90	May 2013	Jul 2018	2024-03-01	26762
Mercedes-benz	Cla	CLA 250 4-matic	Coupe	Allrad	Benzin	155	211	Jul 2013	Mar 2019	2024-03-01	26765
Cadillac	Escalade	6.0 AWD	SUV	Allrad	Benzin	257	349	Oct 2000	Dec 2006	2026-03-01	26773
Fiat	Ducato	2.0 4X4	Kasten	Allrad	Benzin	80	109	Nov 1994	Apr 2002	2024-03-01	26775
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	127	173	Oct 1987	Sep 1990	2024-03-01	26781
Cadillac	Escalade	6	SUV	Heckantrieb	Benzin	257	349	Jun 2001	Sep 2006	2024-03-01	26785
Mercedes-benz	Cla	CLA 45 AMG 4-matic	Coupe	Allrad	Benzin	265	360	Jul 2013	Mar 2019	2024-03-01	26787
Chevrolet	Tahoe	5.7	SUV	Heckantrieb	Benzin	147	200	Oct 1994	Sep 1995	2024-03-01	26792
Hyundai	I10 i	1.1	Schrägheck	Frontantrieb	Benzin	48	65	Dec 2007	Dec 2013	2024-03-01	26808
Infiniti	Q50	50 Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	268	364	Apr 2013	-	2024-03-01	26815
Bentley	Arnage	6.8	Coupe	Heckantrieb	Benzin	373	507	Sep 2006	-	2024-03-01	26816
Opel	Insignia a	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	120	163	Jul 2013	Mar 2017	2024-03-01	26831
Bentley	Continental	6.0 GTC Speed Allrad	Cabriolet	Allrad	Benzin	448	610	Aug 2007	Apr 2011	2024-03-01	26835
Audi	A4 b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	125	170	Jan 2008	Mar 2012	2024-03-01	26836
Hyundai	Porter	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	73	99	Jul 1994	Apr 2004	2024-03-01	26837
Hyundai	Porter	2.5 TD	Kasten	Heckantrieb	Diesel	57	78	Jul 1994	Apr 2004	2024-03-01	26838
Hyundai	Porter	2.5 TD	Kasten	Heckantrieb	Diesel	73	99	Jul 1994	Apr 2004	2024-03-01	26840
Audi	A4 b8	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	125	170	Jan 2008	Mar 2012	2024-03-01	26847
Audi	A4 b8	2.0 TDI	Stufenheck	Frontantrieb	Diesel	88	120	Jun 2008	Dec 2015	2024-03-01	26848
Audi	A4 b8 avant	2.7 TDI	Kombi	Frontantrieb	Diesel	120	163	Apr 2008	Mar 2012	2026-05-01	26852
Infiniti	Q50	50 Hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	268	364	Apr 2013	-	2024-03-01	26859
VW	Golf vii variant	2.0 TDI	Kombi	Frontantrieb	Diesel	81	110	May 2013	Aug 2020	2024-03-01	26860
Dodge	Ram 2500	5.9 DI	Pick-up	Heckantrieb	Diesel	154	209	Oct 1996	May 2001	2024-03-01	26864
Hyundai	Porter	2.5 TD	Pritsche/Fahrgestell	Heckantrieb	Diesel	57	78	Jul 1994	Apr 2004	2024-03-01	26867
Dodge	Ram 2500	5.9 DI	Pick-up	Heckantrieb	Diesel	172	234	Jan 2002	Dec 2009	2024-03-01	26876
Opel	Insignia a sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	120	163	Jul 2013	Jun 2015	2024-03-01	26883
Mitsubishi	Galant vii	2	Stufenheck	Frontantrieb	Benzin	100	136	Nov 1992	Aug 1996	2024-03-01	26890
Lamborghini	Aventador	6.5 LP 700-4 AWD	Targa	Allrad	Benzin	515	700	Apr 2013	-	2024-03-01	26893
Audi	A4 b8	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	132	180	Jun 2008	Dec 2015	2024-03-01	26911
Audi	A4 b8	2.0 Tfsi	Stufenheck	Frontantrieb	Benzin	155	211	Jun 2008	May 2013	2024-03-01	26912
Audi	A4 b8	2.0 Tfsi Quattro	Stufenheck	Allrad	Benzin	155	211	Jun 2008	Dec 2015	2024-03-01	26913
Audi	A4 b8 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	155	211	Jun 2008	May 2013	2024-03-01	26914
Audi	A4 b8 avant	1.8 Tfsi	Kombi	Frontantrieb	Benzin	88	120	Apr 2008	Dec 2015	2024-03-01	26916
Bentley	Flying spur	6.0 W12	Stufenheck	Allrad	Benzin	460	626	Mar 2013	Oct 2020	2024-03-01	26936
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	120	163	Dec 2006	Mar 2010	2024-03-01	26960
Hyundai	Elantra iv	2.0 Cvvt	Stufenheck	Frontantrieb	Benzin	105	143	Jun 2006	Jun 2011	2024-03-01	26970
VW	Golf vii variant	1.6 TDI	Kombi	Frontantrieb	Diesel	81	110	May 2013	Mar 2017	2024-03-01	26977
BMW	X1	Sdrive 18 I	SUV	Heckantrieb	Benzin	100	136	Mar 2010	Jun 2015	2024-03-01	26980
Mercedes-benz	Sprinter 4-T	414 D 4X4	Kasten	Allrad	Diesel	90	122	May 1997	May 2006	2024-03-01	26984
Mercedes-benz	Sprinter 3-T	310 D 2.9 4X4	Kasten	Allrad	Diesel	75	102	Jun 1997	Apr 2000	2024-03-01	26985
Mercedes-benz	Sprinter classic 3,5-T	311 CDI	Kasten	Heckantrieb	Diesel	80	109	Sep 2013	-	2024-03-01	26988
Hyundai	Porter	2.5 Crdi	Pritsche/Fahrgestell	Heckantrieb	Diesel	103	140	Feb 2003	Apr 2004	2024-03-01	26997
Hyundai	Porter	2.5 Crdi	Kasten	Heckantrieb	Diesel	103	140	Feb 2003	Apr 2004	2024-03-01	26998
Chevrolet	Aveo	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	103	140	Aug 2013	-	2024-03-01	27004
VW	Golf vii variant	1.4 TGI CNG	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	81	110	Sep 2013	Jul 2018	2024-03-01	27009
Shuanghuan	Ceo	2.4 Allrad	SUV	Allrad	Benzin	92	125	Jan 2005	Dec 2011	2024-03-01	27041
Mercedes-benz	G-Klasse	G 55 AMG	Geländewagen geschlossen	Allrad	Benzin	368	500	Aug 2006	Dec 2012	2024-03-01	27063
Saab	900 i	2	Cabriolet	Frontantrieb	Benzin	125	170	Oct 1989	Oct 1993	2024-03-01	27067
Saab	900 i combi coupe	2	Schrägheck	Frontantrieb	Benzin	74	100	Apr 1984	Oct 1991	2024-03-01	27068
Jaguar	Xj	3.6	Coupe	Heckantrieb	Benzin	168	228	Oct 1983	Dec 1989	2024-03-01	27077
Ford	Fiesta ii	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Sep 1983	Sep 1989	2024-03-01	27098
Renault	19 i chamade	1.4	Stufenheck	Frontantrieb	Benzin	58	79	Jun 1989	Aug 1990	2024-03-01	27101
Seat	Ibiza ii	1.4	Schrägheck	Frontantrieb	Benzin	40	54	Dec 1997	Apr 1999	2024-03-01	27115
Suzuki	Swift ii	1.3	Schrägheck	Frontantrieb	Benzin	63	86	Jun 2001	Dec 2003	2024-03-01	27130
Suzuki	Samurai	1.9 D	Geländewagen geschlossen	Heckantrieb	Diesel	46	63	Sep 2000	Dec 2004	2024-03-01	27132
Rover	400	414	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1996	Dec 1997	2024-03-01	27134
Fiat	Bravo i	1.6	Schrägheck	Frontantrieb	Benzin	76	103	Sep 2000	Oct 2001	2024-03-01	27141
Volvo	V40	1.8 Blu-fuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	85	116	Jun 2001	Aug 2003	2024-03-01	27148
Volvo	V70 iii	2.0 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	157	214	Mar 2013	Dec 2015	2024-03-01	27154
Fiat	Ducato	2.5 TD 4X4	Bus	Allrad	Diesel	85	116	Jun 1994	Sep 2001	2024-03-01	27163
Fiat	Ducato	2.5 TD 4X4	Kasten	Allrad	Diesel	68	92	Sep 1986	Sep 1990	2024-03-01	27165
Mazda	323 s iv	1.6	Stufenheck	Frontantrieb	Benzin	64	87	Jun 1989	Mar 1991	2024-03-01	27166
VW	Multivan t5	2.0 TDI	Bus	Frontantrieb	Diesel	84	114	May 2011	Aug 2015	2024-03-01	27168
Peugeot	Partner	1.9 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	50	68	Jun 1996	Dec 1998	2024-03-01	27169
Peugeot	Partner	1.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	66	90	Mar 1997	Aug 2000	2024-03-01	27171
Peugeot	Expert	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	69	94	Oct 2000	Oct 2006	2024-03-01	27173
Peugeot	Expert	2.0 HDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	80	109	Oct 2000	Oct 2006	2024-03-01	27174
Peugeot	J5	2.5 D 4X4	Pritsche/Fahrgestell	Allrad	Diesel	54	73	Sep 1981	Aug 1990	2024-03-01	27175
Peugeot	J5	2.5 DT	Pritsche/Fahrgestell	Frontantrieb	Diesel	70	95	Sep 1981	Aug 1990	2024-03-01	27176
Mercedes-benz	Sprinter 3-T	310 D	Bus	Heckantrieb	Diesel	75	102	Jan 1997	Dec 1999	2024-03-01	27203
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	93	126	Nov 2003	Sep 2005	2024-03-01	27206
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	100	136	Nov 2002	Nov 2004	2024-03-01	27207
Alfa Romeo	156	1.9 JTD	Stufenheck	Frontantrieb	Diesel	110	150	Jul 2004	Sep 2005	2024-03-01	27208
Alfa Romeo	156	2.4 JTD	Stufenheck	Frontantrieb	Diesel	120	163	Jun 2003	Sep 2005	2024-03-01	27209
Renault	Sport spider	2	Cabriolet	Heckantrieb	Benzin	108	147	Dec 1995	Aug 1996	2024-03-01	27215
Toyota	Hiace iv	2.4 D	Kasten	Heckantrieb	Diesel	57	78	Sep 1989	Aug 1995	2024-03-01	27216


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 **41 个 Ktype**，形成 **54 条 READY 映射行**。
* 复用跨批次既有尺寸组 **19 个**，未重复输出其尺寸和来源。
* 首次创建并闭合尺寸组 **8 个**：VW CC、Golf VII Variant、CLA C117 改款前后、Aventador Roadster、Flying Spur II、Elantra IV、V70 III facelift。
* 对跨改款且外廓变化的 Ktype 完成派生拆分，包括 Koleos I、CLA C117、i10 I、A4 B8、Alfa Romeo 156。
* Bentley Flying Spur II 改款前后长宽高一致，因此复用同一尺寸组，未因改款重复建组。新建尺寸组的三维与车身边界由对应 Auto-Data 车型或代际页面闭合。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**41**
* READY 映射行：**54**
* PENDING／尚未闭合 Ktype：**59**
* 当前已引用尺寸组：**27**

  * 复用既有尺寸组：19
  * 本轮新建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26654_phase1	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	HIGH	Phase I外廓。	READY
26654_phase2	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	HIGH	Phase II外廓。	READY
26654_phase3	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	HIGH	Phase III外廓。	READY
26655_phase1	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	HIGH	Phase I外廓。	READY
26655_phase2	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	HIGH	Phase II外廓。	READY
26655_phase3	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	HIGH	Phase III外廓。	READY
26732	26732	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26739	26739	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26740	26740	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26743	26743	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26752	26752	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26753	26753	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26760	26760	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26762	26762	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26765_prefl	26765	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	HIGH	211 hp 4MATIC改款前分支。	READY
26765_facelift	26765	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	HIGH	211 hp 4MATIC改款后分支。	READY
26781	26781	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH		READY
26787	26787	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	MEDIUM	360 hp AMG对应改款前C117；输入结束年月晚于该功率版本。	READY
26808_prefl	26808	Hatchback	i10 I		5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
26808_facelift	26808	Hatchback	i10 I		5	EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	HIGH	改款后外廓。	READY
26831	26831	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH		READY
26835	26835	Convertible	Continental GTC I		2	EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	HIGH		READY
26836	26836	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
26847	26847	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
26848_prefl	26848	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26848_facelift	26848	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26852	26852	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
26860	26860	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	MEDIUM	输入2.0 TDI 110 hp版本名称与代际功率目录存在差异，但物理外廓归入改款前Variant。	READY
26883	26883	Wagon	Insignia A facelift		5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH		READY
26893	26893	Convertible	Aventador LP 700-4 Roadster		2	EU-LAMBORGHINI-AVENTADOR-LP700-4-ROADSTER-CONVERTIBLE-01	HIGH	输入Targa按量产Roadster外廓归一。	READY
26911_prefl	26911	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26911_facelift	26911	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26912_prefl	26912	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26912_facelift	26912	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26913_prefl	26913	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26913_facelift	26913	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26914_prefl	26914	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
26914_facelift	26914	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
26916_prefl	26916	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
26916_facelift	26916	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
26936	26936	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-4D-01	MEDIUM	460 kW W12对应第二代Flying Spur；输入结束年月延伸至换代边界。	READY
26960	26960	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
26970	26970	Sedan	Elantra IV		4	EU-HYUNDAI-ELANTRA-IV-SEDAN-4D-01	HIGH		READY
26977	26977	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
27009	27009	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
27132	27132	SUV	Samurai	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	HIGH		READY
27141	27141	Hatchback	Bravo I		3	EU-FIAT-BRAVO-I-HATCHBACK-3D-01	HIGH		READY
27154	27154	Wagon	V70 III facelift		5	EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	HIGH		READY
27168	27168	MPV	Multivan T5	T5	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
27206	27206	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
27207_prefl	27207	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
27207_facelift	27207	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
27208	27208	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
27209	27209	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CC-I-FACELIFT-COUPE-4D-01	4802	1855	1417	Auto-Data Volkswagen CC I facelift 2.0 TSI	https://www.auto-data.net/en/volkswagen-cc-i-facelift-2012-2.0-tsi-210hp-dsg-18443
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481	Auto-Data Volkswagen Golf VII Variant	https://www.auto-data.net/en/volkswagen-golf-vii-variant-generation-4063
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	4691	1777	1432	Auto-Data Mercedes-Benz CLA Coupe C117	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-generation-4116
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	4640	1777	1432	Auto-Data Mercedes-Benz CLA Coupe C117 facelift	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-facelift-2016-generation-4746
EU-LAMBORGHINI-AVENTADOR-LP700-4-ROADSTER-CONVERTIBLE-01	4780	2030	1136	Auto-Data Lamborghini Aventador LP 700-4 Roadster	https://www.auto-data.net/en/lamborghini-aventador-lp-700-4-roadster-generation-4686
EU-BENTLEY-FLYING-SPUR-II-SEDAN-4D-01	5299	1976	1488	Auto-Data Bentley Flying Spur	https://www.auto-data.net/en/bentley-flying-spur-model-2103
EU-HYUNDAI-ELANTRA-IV-SEDAN-4D-01	4505	1775	1490	Auto-Data Hyundai Elantra IV 2.0 i 16V	https://www.auto-data.net/en/hyundai-elantra-iv-2.0-i-16v-143hp-13900
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547	Auto-Data Volvo V70 III facelift	https://www.auto-data.net/en/volvo-v70-iii-facelift-2013-generation-4522
```

## 下一步优先处理

1. 集中闭合 Fiat Ducato、Hyundai Porter、Mercedes-Benz Sprinter、Dodge Ram 2500、Peugeot Expert/J5 等多轴距、多车顶或多车身商用车。
2. 处理 Priora、Fiorino、Escalade、Tahoe、Q50 等跨改款、门数或车型版本边界尚未闭合的记录。
3. 批量补齐 SLK R171、Ignis II、Galant VII、G-Klasse、Saab 900、旧款 Fiesta、Renault 19、Seat Ibiza II、Suzuki Swift II、Rover 400、Volvo V40、Mazda 323 等乘用车尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-cc-i-facelift-2012-2.0-tsi-210hp-dsg-18443 "Volkswagen CC I (facelift 2012) 2.0 TSI (210 Hp) DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增完成 **16 个 Ktype、21 条 READY 映射**。
* 新建并闭合 **16 个尺寸组**；Tahoe I 的 2 门与 4 门分支直接复用累计缓存，未重复输出尺寸组。
* Priora Hatchback、Q50 与 X1 按改款后三维变化拆分；SLK 200 与 SLK 350 因实际宽高不同分别建组。
* 本轮新建尺寸已按对应直接规格页面核对。([汽车数据网][1])
* Q50、X1、G 55 AMG 与 Saab 900 Cabriolet 的改款、驱动或车身边界已分别闭合。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**57**
* READY 映射行：**75**
* PENDING／尚未闭合 Ktype：**43**
* 当前已引用尺寸组：**45**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26656	26656	Sedan	Priora I	2170	4	EU-LADA-PRIORA-I-2170-SEDAN-01	HIGH		READY
26657_prefl	26657	Hatchback	Priora I	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	HIGH	改款前五门外廓。	READY
26657_facelift	26657	Hatchback	Priora I	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	HIGH	改款后车高变化。	READY
26658	26658	Wagon	Kalina I	1117	5	EU-LADA-KALINA-I-1117-WAGON-01	HIGH		READY
26661	26661	Hatchback	Ignis II	MH	5	EU-SUZUKI-IGNIS-II-MH-HATCHBACK-5D-01	HIGH		READY
26662	26662	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	HIGH	SLK 350外廓。	READY
26663	26663	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	HIGH	SLK 200 Kompressor外廓。	READY
26695	26695	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH	标准轴距SUV。	READY
26696	26696	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH	标准轴距SUV。	READY
26773	26773	SUV	Escalade II		5	EU-CADILLAC-ESCALADE-II-SUV-01	HIGH	标准轴距6.0 AWD SUV。	READY
26785	26785	SUV	Escalade II		5	EU-CADILLAC-ESCALADE-II-SUV-01	MEDIUM	输入驱动字段与6.0量产资料不一致；按标准轴距SUV外廓映射。	READY
26792_2dr	26792	SUV	Tahoe I		2	EU-CHEVROLET-TAHOE-I-SUV-2D-01	MEDIUM	两门物理分支。	READY
26792_4dr	26792	SUV	Tahoe I		4	EU-CHEVROLET-TAHOE-I-SUV-4D-01	MEDIUM	四门物理分支。	READY
26815_prefl	26815	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	HIGH	改款前AWD外廓。	READY
26815_facelift	26815	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	HIGH	改款后AWD外廓。	READY
26859_prefl	26859	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	HIGH	改款前后驱外廓。	READY
26859_facelift	26859	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	HIGH	改款后后驱外廓。	READY
26980_prefl	26980	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	改款前外廓。	READY
26980_facelift	26980	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	改款后车长变化。	READY
27063	27063	SUV	G-Class Long W463 facelift 2007	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-LONG-G55-500-SUV-01	MEDIUM	500 hp版本对应2007改款长轴车身；输入结束年月延伸至后续507 hp版本。	READY
27067	27067	Convertible	900 I Cabriolet		2	EU-SAAB-900-I-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LADA-PRIORA-I-2170-SEDAN-01	4350	1680	1420	Auto-Data Lada Priora I Sedan facelift 1.6	https://www.auto-data.net/en/lada-priora-i-sedan-facelift-2013-1.6-106hp-22344
EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	4210	1680	1420	Drive Place Lada Priora I 5-door Hatchback	https://lada.drive.place/2170/i/group_hatchback_5d/344965
EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	4210	1680	1435	Auto-Data Lada Priora I Hatchback facelift	https://www.auto-data.net/en/lada-priora-i-hatchback-facelift-2013-generation-4632
EU-LADA-KALINA-I-1117-WAGON-01	4040	1700	1500	Encycarpedia Lada Kalina Universal 1117	https://www.encycarpedia.com/lada/07-kalina-universal-1117-estate
EU-SUZUKI-IGNIS-II-MH-HATCHBACK-5D-01	3770	1605	1565	Auto-Data Suzuki Ignis I MH 1.3 4WD	https://www.auto-data.net/en/suzuki-ignis-i-mh-1.3-i-16v-93hp-4wd-16417
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	4107	1788	1298	Auto-Data Mercedes-Benz SLK R171 facelift SLK 350	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-350-v6-305hp-7g-tronic-42051
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	4107	1777	1296	Auto-Data Mercedes-Benz SLK R171 facelift SLK 200 Kompressor	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-200-kompressor-184hp-automatic-41191
EU-CADILLAC-ESCALADE-III-SUV-01	5144	2008	1887	Auto-Data Cadillac Escalade III	https://www.auto-data.net/en/cadillac-escalade-iii-generation-2489
EU-CADILLAC-ESCALADE-II-SUV-01	5052	2004	1885	Auto-Data Cadillac Escalade II 6.0 V8 AWD	https://www.auto-data.net/en/cadillac-escalade-ii-6.0-i-v8-awd-349hp-11729
EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	4783	1824	1443	Auto-Data Infiniti Q50 S 3.5 Hybrid	https://www.auto-data.net/en/infiniti-q50-s-3.5-v6-364hp-hybrid-automatic-18982
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	4810	1820	1445	Auto-Data Infiniti Q50 facelift Hybrid AWD	https://www.auto-data.net/en/infiniti-q50-facelift-2017-3.5-364hp-hybrid-awd-automatic-31420
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	4810	1820	1430	Auto-Data Infiniti Q50 facelift Hybrid RWD	https://www.auto-data.net/en/infiniti-q50-facelift-2017-3.5-364hp-hybrid-automatic-31356
EU-BMW-X1-E84-SUV-PREFL-01	4454	1798	1545	Auto-Data BMW X1 E84	https://www.auto-data.net/en/bmw-x1-e84-generation-1990
EU-BMW-X1-E84-SUV-FACELIFT-01	4477	1798	1545	Auto-Data BMW X1 E84 LCI	https://www.auto-data.net/en/bmw-x1-e84-lci-facelift-2012-generation-3856
EU-MERCEDES-BENZ-G-CLASS-W463-LONG-G55-500-SUV-01	4662	1864	1931	Auto-Data Mercedes-Benz G-Class Long W463 facelift 2007	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2007-generation-7913
EU-SAAB-900-I-CONVERTIBLE-2D-01	4680	1690	1420	Auto-Data Saab 900 I Cabriolet	https://www.auto-data.net/en/saab-900-i-cabriolet-generation-2548
```

## 下一步优先处理

1. 先闭合 Bentley Arnage、Jaguar XJ40、Fiesta II、Renault 19 Chamade、Ibiza II、Swift II、Rover 400、Mazda 323 等乘用车组。
2. 再处理 Fiorino、Combo D、Partner I 和 Expert I 等车身边界相对明确的轻型商用车。
3. 最后集中拆分 Ducato、Porter、Sprinter、Ram 2500、J5 等多轴距、多车顶或多驾驶室记录。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/lada-priora-i-sedan-facelift-2013-1.6-106hp-22344 "Lada Priora I Sedan (facelift 2013) 1.6 (106 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/infiniti-q50-s-3.5-v6-364hp-hybrid-awd-automatic-18983?utm_source=chatgpt.com "Infiniti Q50 S 3.5 V6 (364 Hp) Hybrid AWD Automatic"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增完成 **7 个 Ktype、7 条 READY 映射**。
* 首次创建并闭合 **7 个尺寸组**，无既有尺寸组修正。
* Bentley Arnage T 按实际四门 Sedan 归类，并采用 **1900 mm 不含后视镜宽度**，未误用折叠后视镜宽度。([汽车数据网][1])
* Galant VII、Aveo II、Sceo、XJS、Rover 400 RT 与 Sport Spider 的车身边界及三维已闭合。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**64**
* READY 映射行：**82**
* PENDING／尚未闭合 Ktype：**36**
* 当前已引用尺寸组：**52**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：31
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26816	26816	Sedan	Arnage T		4	EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	HIGH	输入BodyStyle为Coupe；该版本实际为4门Sedan。	READY
26890	26890	Sedan	Galant VII	E55A	4	EU-MITSUBISHI-GALANT-VII-E55A-SEDAN-4D-01	MEDIUM	输入136 hp与目录137 hp为市场计量差异。	READY
27004	27004	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-5D-01	MEDIUM	140 hp地区版本按T300五门外廓。	READY
27041	27041	SUV	Sceo		5	EU-SHUANGHUAN-SCEO-SUV-5D-01	HIGH	CEO/Sceo为同车型命名差异。	READY
27077	27077	Coupe	XJS		2	EU-JAGUAR-XJS-COUPE-2D-01	MEDIUM	输入Model写作Xj；3.6 Coupe对应XJS Coupe。	READY
27134	27134	Hatchback	400 (RT)	RT	5	EU-ROVER-400-RT-HATCHBACK-5D-01	HIGH		READY
27215	27215	Convertible	Sport Spider		2	EU-RENAULT-SPORT-SPIDER-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	5400	1900	1515	Auto-Data Bentley Arnage T 6.8i V8 Biturbo	https://www.auto-data.net/en/bentley-arnage-t-6.8i-v8-biturbo-507hp-automatic-35870
EU-MITSUBISHI-GALANT-VII-E55A-SEDAN-4D-01	4620	1730	1405	Auto-Data Mitsubishi Galant VII	https://www.auto-data.net/en/mitsubishi-galant-vii-generation-3374
EU-CHEVROLET-AVEO-II-T300-HATCHBACK-5D-01	4039	1735	1517	Auto-Data Chevrolet Aveo II Hatchback	https://www.auto-data.net/en/chevrolet-aveo-ii-hatchback-generation-3798
EU-SHUANGHUAN-SCEO-SUV-5D-01	4710	1871	1820	Auto-Data ShuangHuan Sceo 2.4	https://www.auto-data.net/en/shuanghuan-sceo-2.4-125hp-13941
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279	Auto-Data Jaguar XJS Coupe	https://www.auto-data.net/en/jaguar-xjs-coupe-generation-67
EU-ROVER-400-RT-HATCHBACK-5D-01	4320	1700	1390	Auto-Data Rover 400 Hatchback RT 414 i	https://www.auto-data.net/en/rover-400-hatchback-rt-414-i-75hp-17667
EU-RENAULT-SPORT-SPIDER-CONVERTIBLE-2D-01	3795	1830	1250	Auto-Data Renault Sport Spider	https://www.auto-data.net/en/renault-sport-spider-generation-2157
```

## 下一步优先处理

1. 优先闭合 Fiesta II、Renault 19 Chamade、Ibiza II、Swift II、Mazda 323 S IV、Volvo V40 等乘用车。
2. 随后处理 Fiorino、Combo Tour、Partner 等边界相对明确的轻型商用车。
3. 最后集中拆分 Ducato、Porter、Sprinter、Ram 2500、Expert、J5 等多轴距、多车顶或多驾驶室车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bentley-arnage-t-6.8i-v8-biturbo-507hp-automatic-35870 "Bentley Arnage T 6.8i V8 Biturbo (507 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-galant-vii-generation-3374 "Mitsubishi Galant VII | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮新增完成 **9 个 Ktype、10 条 READY 映射**。
* 首次创建并闭合 **8 个尺寸组**，无既有尺寸组修正。
* Fiorino 与 Partner 的货运／乘用版本按共用外部车身处理，未因发动机或内部用途重复建组。([汽车数据网][1])
* Fiesta II、Renault 19 Chamade 与 Ibiza II 的代际和三维已闭合；Ibiza 因三门、五门车身分为两个稳定尺寸组。([汽车数据网][2])
* V40、Mazda 323 S IV 的改款／Sedan 外廓已确认。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**73**
* READY 映射行：**92**
* PENDING／尚未闭合 Ktype：**27**
* 当前已引用尺寸组：**60**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：39
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26659	26659	Van	Fiorino III		5	EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH	货运与乘用版本共用外部车身。	READY
26660	26660	Van	Fiorino III		5	EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH	货运与乘用版本共用外部车身。	READY
27098	27098	Hatchback	Fiesta II (Mk2)	FBD	3	EU-FORD-FIESTA-II-MK2-HATCHBACK-3D-01	HIGH		READY
27101	27101	Sedan	19 I Chamade	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH		READY
27115_3dr	27115	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
27115_5dr	27115	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
27148	27148	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-FACELIFT-01	MEDIUM	2000年后更新外廓。	READY
27166	27166	Sedan	323 S IV	BG	4	EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	MEDIUM	输入87 hp与欧洲目录计量值存在轻微差异。	READY
27169	27169	MPV	Partner I Phase I		5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	MEDIUM	货运与乘用版本共用外部车身。	READY
27171	27171	MPV	Partner I Phase I		5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	MEDIUM	货运与乘用版本共用外部车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-FIORINO-III-VAN-MPV-01	3864	1716	1721	Auto-Data Fiat Fiorino	https://www.auto-data.net/en/fiat-fiorino-model-760
EU-FORD-FIESTA-II-MK2-HATCHBACK-3D-01	3565	1567	1360	Auto-Data Ford Fiesta II 1.3; Classic Car Reviews Ford Fiesta Mk2	https://www.auto-data.net/en/ford-fiesta-ii-mk2-1.3-fbd-69hp-8068; https://www.classiccarreviews.co.uk/review/ford/fiesta-mk2/hatchback-1983-1989/
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412	Auto-Data Renault 19 I Chamade L53	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Automobile-Catalog 1997 Seat Ibiza 1.4	https://www.automobile-catalog.com/car/1997/3070025/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Automobile-Catalog 1997 Seat Ibiza 1.4	https://www.automobile-catalog.com/car/1997/3070025/seat_ibiza_1_4.html
EU-VOLVO-V40-I-VW-WAGON-5D-FACELIFT-01	4516	1720	1425	Auto-Data Volvo V40 Combi VW	https://www.auto-data.net/en/volvo-v40-combi-vw-generation-1967
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375	Automobile-Catalog Mazda 323 1.6 16V GLX Sedan	https://www.automobile-catalog.com/car/1989/1645700/mazda_323_1_6_16v_glx_sedan.html
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870	Auto-Data Peugeot Partner I Phase I 1.9 D	https://www.auto-data.net/en/peugeot-partner-i-phase-i-1.9-d-70hp-42013
```

## 下一步优先处理

1. 闭合 Fiesta V Van、Combo Tour D、Saab 900 Combi Coupe、Swift II 和 Hiace IV。
2. 集中拆分 Ducato、Porter、Sprinter、Ram 2500 的轴距、车顶及车身分支。
3. 最后处理 Expert、J5 的底盘驾驶室边界及尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-fiorino-model-760 "Fiat Fiorino | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/ford-fiesta-ii-mk2-1.3-fbd-69hp-8068 "Ford Fiesta II (Mk2) 1.3 (FBD) (69 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volvo-v40-combi-vw-generation-1967 "Volvo V40 Combi (VW) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮新增完成 **5 个 Ktype、9 条 READY 映射**。
* 首次创建并闭合 **8 个尺寸组**，无既有尺寸组修正。
* Fiesta V Van 按改款前后拆分；Saab 900 I Combi Coupe 同时按门数和改款边界拆分。
* Combo Tour D 使用标准轴距、标准顶乘用版外廓；Swift II 86 hp 对应三门 Hatchback。([Autogidas][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**78**
* READY 映射行：**101**
* PENDING／尚未闭合 Ktype：**22**
* 当前已引用尺寸组：**68**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26669	26669	Van	Fiesta V Van		3	EU-FORD-FIESTA-V-VAN-3D-PREFL-01	HIGH	改款前三门厢式车。	READY
26670_prefl	26670	Van	Fiesta V Van		3	EU-FORD-FIESTA-V-VAN-3D-PREFL-01	HIGH	改款前三门厢式车。	READY
26670_facelift	26670	Van	Fiesta V Van facelift		3	EU-FORD-FIESTA-V-VAN-3D-FACELIFT-01	HIGH	改款后三门厢式车。	READY
26742	26742	MPV	Combo Tour D	X12	5	EU-OPEL-COMBO-TOUR-D-X12-MPV-L1H1-01	HIGH	标准轴距、标准顶乘用版。	READY
27068_3dr_prefl	27068	Hatchback	900 I Combi Coupe		3	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理分支。	READY
27068_5dr_prefl	27068	Hatchback	900 I Combi Coupe		5	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理分支。	READY
27068_3dr_facelift	27068	Hatchback	900 I Combi Coupe facelift		3	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理分支。	READY
27068_5dr_facelift	27068	Hatchback	900 I Combi Coupe facelift		5	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理分支。	READY
27130	27130	Hatchback	Swift II facelift	SF413	3	EU-SUZUKI-SWIFT-II-EA-MA-HATCHBACK-3D-FACELIFT-01	MEDIUM	86 hp三门Hatchback分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-V-VAN-3D-PREFL-01	3917	1683	1467	Ford Fiesta Van brochure	https://manuals.plus/m/7218d31c7755745164911cb2826b7a226d785b6c13d9176ee306d168ced6b2c2
EU-FORD-FIESTA-V-VAN-3D-FACELIFT-01	3918	1683	1468	Autogidas Ford Fiesta V Van 1.4 TDCi	https://autogidas.lt/en/auto-katalogas/ford/fiesta/v-an-1.4-tdci-2006-2008-k65240
EU-OPEL-COMBO-TOUR-D-X12-MPV-L1H1-01	4390	1831	1845	Auto-Data Opel Combo Tour D	https://www.auto-data.net/en/opel-combo-tour-d-generation-4218
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-PREFL-01	4740	1690	1420	Auto-Data Saab 900 I Combi Coupe; CarsGuide Saab 900 1984 dimensions	https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543; https://www.carsguide.com.au/saab/900/car-dimensions/1984
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-PREFL-01	4740	1690	1420	Auto-Data Saab 900 I Combi Coupe; CarsGuide Saab 900 1984 dimensions	https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543; https://www.carsguide.com.au/saab/900/car-dimensions/1984
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I Combi Coupe facelift	https://www.auto-data.net/en/saab-900-model-1277
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I Combi Coupe facelift	https://www.auto-data.net/en/saab-900-model-1277
EU-SUZUKI-SWIFT-II-EA-MA-HATCHBACK-3D-FACELIFT-01	3745	1590	1350	Drive Place Suzuki Swift II three-door; AUTODOC Swift II 1.3 86 hp identification	https://suzuki.drive.place/swift/ii/group_hatchback_3d/271206; https://www.autodoc.parts/spares/suzuki/swift/swift-ii-hatchback-ea-ma/27130-1-3-sf-413
```

## 下一步优先处理

1. 处理 Peugeot Expert I 底盘、J5 底盘和 Toyota Hiace IV Van。
2. 集中拆分 Fiat Ducato X230/X244 Bus、Van 的轴距及车顶分支。
3. 最后处理 Hyundai Porter、Mercedes-Benz Sprinter 和 Dodge Ram 2500 的驾驶室、轴距及车身组合。

推进信号：CONTINUE

[1]: https://autogidas.lt/en/auto-katalogas/ford/fiesta/v-an-1.4-tdci-2006-2008-k65240?utm_source=chatgpt.com "Ford Fiesta V an 1.4 TDCi 2006-2008 | Autocatalog"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮完成 **Ktype 27216**，拆分为 Hiace IV H100 的 **LH102 短轴**与 **LH112 长轴**两个确定物理分支。
* 输入为后轮驱动，因此未创建目录中同时出现的 LH104 四驱分支。
* LH102 与 LH112 的车长和车高不同，分别创建尺寸组，不合并复用。车型目录确认该 Ktype 涵盖 LH102、LH104、LH112，规格资料分别支持短轴与长轴三维。([汽车数据网][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**79**
* READY 映射行：**103**
* PENDING／尚未闭合 Ktype：**21**
* 当前已引用尺寸组：**70**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：49
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
27216_swb	27216	Van	Hiace IV (H100)	LH102		EU-TOYOTA-HIACE-IV-H100-VAN-LH102-SWB-01	MEDIUM	后轮驱动短轴物理分支。	READY
27216_lwb	27216	Van	Hiace IV (H100)	LH112		EU-TOYOTA-HIACE-IV-H100-VAN-LH112-LWB-01	MEDIUM	后轮驱动长轴物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIACE-IV-H100-VAN-LH102-SWB-01	4615	1690	1935	Auto-Data Toyota HiAce IV H100; AUTODOC Toyota Hiace Van H100 2.4 D Ktype identification	https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186; https://www.autodoc.parts/car-parts/battery-10142/toyota/hiace/hiace-iii-box-yh7-lh6-lh7-lh5-yh5-yh6/27216-2-4-d-lh102-lh104-lh112
EU-TOYOTA-HIACE-IV-H100-VAN-LH112-LWB-01	4950	1690	1960	Auto-ABC Toyota Hiace Long 2.4 D; AUTODOC Toyota Hiace Van H100 2.4 D Ktype identification	https://www.auto-abc.eu/Toyota-Hiace/v5444-1992; https://www.autodoc.parts/car-parts/battery-10142/toyota/hiace/hiace-iii-box-yh7-lh6-lh7-lh5-yh5-yh6/27216-2-4-d-lh102-lh104-lh112
```

## 下一步优先处理

1. 闭合 Peugeot Expert I 和 J5 的底盘驾驶室分支。
2. 集中处理 Fiat Ducato X230／X244 的轴距、车顶和 Bus／Van 分支。
3. 最后拆分 Hyundai Porter、Mercedes-Benz Sprinter 与 Dodge Ram 2500 的驾驶室、轴距及车身组合。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186?utm_source=chatgpt.com "Toyota HiAce IV (H100) 2.4 i (132 Hp) /Minivan 1989"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 本轮新增完成 **8 个 Ktype、8 条 READY 映射**。
* 首次创建并闭合 **3 个尺寸组**，无既有尺寸组修正。
* Peugeot Expert I 两个功率版本复用同一底盘驾驶室外廓。
* Hyundai Porter／H100 按 **平台底盘**与**封闭式 Van**分为两个物理尺寸组；发动机功率和 CRDi／TD 差异未重复建组。Expert I 标准短车身规格为 4522 × 1844 × 1919 mm；同期 Porter 平台与 Van 的三维分别闭合为 4750 × 1690 × 1930 mm 和 4790 × 1690 × 1965 mm。([Autogidas][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**87**
* READY 映射行：**111**
* PENDING／尚未闭合 Ktype：**13**
* 当前已引用尺寸组：**73**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：52
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26837	26837	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	平台底盘外廓。	READY
26838	26838	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	封闭式Van外廓。	READY
26840	26840	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	封闭式Van外廓。	READY
26867	26867	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	平台底盘外廓。	READY
26997	26997	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	CRDi版本沿用同期平台底盘外廓。	READY
26998	26998	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	CRDi版本沿用同期封闭式Van外廓。	READY
27173	27173	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	MEDIUM	底盘驾驶室外廓。	READY
27174	27174	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	MEDIUM	底盘驾驶室外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	4750	1690	1930	Truck1 Hyundai Porter 2.5 D Flatbed specifications	https://www.truck1.eu/blog/hyundai-porter-2-5-d-80-hp-tech-specs-t27426
EU-HYUNDAI-PORTER-III-VAN-01	4790	1690	1965	Motoro Hyundai H100 Van 2.5D specifications	https://motoro.ch/en/fiche-technique/hyundai/h-100-van-2-5d
EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	4522	1844	1919	Autogidas Peugeot Expert I 2.0 HDI 220C specifications	https://autogidas.lt/en/auto-katalogas/peugeot/expert/i-2.0-hdi-220c-2004-2006-k51951
```

## 下一步优先处理

1. 集中处理 Fiat Ducato X230／X244 的 Bus、Van、轴距与车顶分支。
2. 处理 Peugeot J5 280L／290L 底盘的短轴、长轴及四驱边界。
3. 最后拆分 Mercedes-Benz Sprinter 与 Dodge Ram 2500 的轴距、车顶、驾驶室和货斗组合。

推进信号：CONTINUE

[1]: https://autogidas.lt/en/auto-katalogas/peugeot/expert/i-2.0-hdi-220c-2004-2006-k51951?utm_source=chatgpt.com "Peugeot Expert I 2.0 HDI 220C 2004-2006 | Autocatalog"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 本轮完成 **Ktype 27165**，确认其为 Fiat Ducato I Typ 280 的 2.5 TD 4×4 Van。
* 按第一代 Ducato 可确认的外廓组合拆分为 **L1H1、L1H2、L2H2** 三个物理分支。
* 三个分支宽度统一为不含后视镜的 **1965 mm**；长度和高度分别按对应轴距／车顶配置建组。([Transit Center][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**88**
* READY 映射行：**114**
* PENDING／尚未闭合 Ktype：**12**
* 当前已引用尺寸组：**76**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
27165_l1h1	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L1H1-01	MEDIUM	短轴低顶物理分支。	READY
27165_l1h2	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L1H2-01	MEDIUM	短轴高顶物理分支。	READY
27165_l2h2	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L2H2-01	MEDIUM	长轴高顶物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
```

## 下一步优先处理

1. 复用累计 X244 尺寸组，闭合 Ktype 26754、26755 的 Bus／Van 分支。
2. 处理 Ducato 230／230L 的 Ktype 26775、27163。
3. 再处理 J5 底盘、Sprinter 与 Ram 2500 的轴距、车顶、驾驶室及货斗分支。

推进信号：CONTINUE

[1]: https://www.transitcenter.uk/fiat-ducato-1-data-specification.php?srsltid=AfmBOoqac3sRiV1901CiJjr1DzVuGBvnZTXbjbxkaBRyp_z23_QuGC9G "Fiat Ducato I - Specifications"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 完成 **Ktype 26754、26755**。
* 两条记录均直接复用累计尺寸组，本轮未重新抓取或重复输出尺寸数据。
* Fiat 技术资料将 2.0 4×4 限定为短轴低顶车身；Bus／Panorama-Combi 对应 Version 11，封闭式 Van 对应 Version 15，因此分别关联既有的 X244 短轴低顶尺寸组。([4CarData][1])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**90**
* READY 映射行：**116**
* PENDING／尚未闭合 Ktype：**10**
* 当前已引用尺寸组：**76**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26754	26754	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	HIGH	Version 11短轴低顶Bus物理外廓。	READY
26755	26755	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	HIGH	Version 15短轴低顶Van物理外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 Ducato X230 Ktype 26775、27163。
2. 处理 Peugeot J5 底盘 Ktype 27175、27176。
3. 最后集中处理 Sprinter Ktype 26984、26985、26988、27203，以及 Ram 2500 Ktype 26864、26876。

推进信号：CONTINUE

[1]: https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000023?utm_source=chatgpt.com "DUCATO 4X4 - Fiat - DUCATO - eLearn - 4CarData"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 本轮完成 **4 个 Ktype、6 条 READY 映射**。
* 首次创建并闭合 **5 个尺寸组**，无既有尺寸组修正。
* Ducato X230 的 2.0 4×4 Van 对应短轴标准顶；2.5 TD 4×4 Bus 拆分为短轴 Panorama 与长轴标准顶两个外廓。([Gazoo][1])
* Peugeot J5 280L 底盘驾驶室确认短轴与长轴外廓；4×4 与前驱短轴三维相同，因此复用同一个短轴尺寸组，不因驱动形式重复建组。([ParuVendu][2])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**94**
* READY 映射行：**122**
* PENDING／尚未闭合 Ktype：**6**
* 当前已引用尺寸组：**81**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：60
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26775	26775	Van	Ducato II	X230		EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶Van外廓。	READY
27163_swb	27163	MPV	Ducato II	X230		EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	MEDIUM	短轴Panorama物理分支。	READY
27163_lwb	27163	MPV	Ducato II	X230		EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	MEDIUM	长轴标准顶物理分支。	READY
27175	27175	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	HIGH	短轴底盘驾驶室。	READY
27176_swb	27176	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	HIGH	短轴底盘驾驶室。	READY
27176_lwb	27176	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-LWB-01	HIGH	长轴底盘驾驶室。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	4655	1998	2150	Gazoo Fiat Ducato dimensions; Motor-Doctor Fiat Ducato 230L 2.0 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://www.motor-doctor.co.uk/fiat/ducato/ducato-box-230l/26775-2-0-4x4
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104	Gazoo Fiat Ducato dimensions; Eibach Fiat Ducato Bus 2.5 TD 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://eibach.ch/en/fiat/ducato-bus-230/25-td-4x4-116-ps-94-01
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150	Gazoo Fiat Ducato dimensions; Eibach Fiat Ducato Bus 2.5 TD 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://eibach.ch/en/fiat/ducato-bus-230/25-td-4x4-116-ps-94-01
EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	4759	1965	1900	ParuVendu Peugeot J5 1400 D short 4x4 chassis cab; ParuVendu Peugeot J5 1400 TBO D short 4x4 chassis cab	https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-d-court-4x4-10-cv-diesel/3056820/; https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-tbo-d-court-4x4-10-cv-diesel/3056821/
EU-PEUGEOT-J5-I-280L-CHASSIS-LWB-01	5489	1965	1900	ParuVendu Peugeot J5 1400 TBO D long chassis cab	https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-tbo-d-long-10-cv-diesel/3056842/
```

## 下一步优先处理

1. 闭合 Mercedes-Benz Sprinter Ktype `26984`、`26985`、`26988`、`27203` 的轴距与车顶分支。
2. 最后处理 Dodge Ram 2500 Ktype `26864`、`26876` 的驾驶室、轴距及货斗组合。

推进信号：CONTINUE

[1]: https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/ "Wymiary Fiat Ducato - długość, szerokość, wysokość, rozstaw osi - gazoo.pl"
[2]: https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot-j5/1400-d-court-4x4-10-cv-diesel/3056820/ "Fiche technique utilitaire Peugeot J5 1400 D COURT (4X4) 1989 (10 CV) 3056820"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 本轮完成 **2 个 Ktype、4 条 READY 映射**。
* `26985` 按 `903.461` 短轴低顶与 `903.462` 中轴低顶拆分；四驱版本对应外廓分别为 `5004 × 1981 × 2362 mm` 和 `5715 × 1981 × 2362 mm`。([Дром][1])
* `26988` 按 `909.632` 与 `909.633` 两个轴距车身拆分；对应三维分别为 `5640 × 1933 × 2595 mm` 和 `6590 × 1933 × 2610 mm`。([Дром][2])
* 本轮首次创建尺寸组 **4 个**，无既有尺寸组修正。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**96**
* READY 映射行：**126**
* PENDING／尚未闭合 Ktype：**4**
* 当前已引用尺寸组：**85**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：64
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26985_l1h1	26985	Van	Sprinter I W903	903.461	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L1H1-4X4-01	MEDIUM	短轴低顶四驱Van物理分支。	READY
26985_l2h1	26985	Van	Sprinter I W903	903.462	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L2H1-4X4-01	MEDIUM	中轴低顶四驱Van物理分支。	READY
26988_l1	26988	Van	Sprinter Classic W909	909.632	4	EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	HIGH	3550 mm轴距Van物理分支。	READY
26988_l2	26988	Van	Sprinter Classic W909	909.633	4	EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	HIGH	4025 mm轴距Van物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L1H1-4X4-01	5004	1981	2362	Drom Mercedes-Benz Sprinter W903 4WD L1H1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/453198/
EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L2H1-4X4-01	5715	1981	2362	Drom Mercedes-Benz Sprinter W903 4WD L2H1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/453200/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	5640	1933	2595	Drom Mercedes-Benz Sprinter Classic 311 CDI L1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270959/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	6590	1933	2610	Drom Mercedes-Benz Sprinter Classic 311 CDI L2	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270974/
```

## 下一步优先处理

1. 闭合 Sprinter `26984` 的 `904.463` 长轴四驱 Van 外廓。
2. 拆分 Sprinter Bus `27203` 的 `903.471`、`903.472`、`903.473` 轴距分支。
3. 最后统一闭合 Ram 2500 `26864`、`26876` 的 Regular Cab、Club／Quad Cab 与长短货斗组合。

推进信号：CONTINUE

[1]: https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/453199/?utm_source=chatgpt.com "Mercedes-Benz Sprinter 312 CDI AT 4WD L1H1 3.5т (01.1995 - 04.2000) - технические характеристики"
[2]: https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/specs/dimensions/?utm_source=chatgpt.com "Размеры Мерседес Спринтер Классик и вес. Какие габариты Mercedes-Benz Sprinter Classic?"


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 完成 **Ktype 26864**，拆分为 Regular Cab 长货斗、Club Cab 短／长货斗、Quad Cab 短／长货斗，共 **5 条 READY 映射**。
* Club Cab 与 Quad Cab 门数不同，因此保留独立映射行；两者相同货斗长度下外廓三维一致，复用同一尺寸组。
* Dodge 1999 官方车型手册确认 2500 2WD 柴油版覆盖上述驾驶室／货斗组合，并直接提供不含后视镜的车身宽度及完整外廓尺寸。
* 本轮首次创建尺寸组 **3 个**，无既有尺寸组修正。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**97**
* READY 映射行：**131**
* PENDING／尚未闭合 Ktype：**3**
* 当前已引用尺寸组：**88**

  * 跨批次复用尺寸组：21
  * 当前批次累计新建尺寸组：67
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26864_regcab_longbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab长货斗物理分支。	READY
26864_clubcab_shortbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Club Cab短货斗物理分支。	READY
26864_clubcab_longbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Club Cab长货斗物理分支。	READY
26864_quadcab_shortbed	26864	Pickup	Ram 2500 II		4	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Quad Cab短货斗物理分支。	READY
26864_quadcab_longbed	26864	Pickup	Ram 2500 II		4	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Quad Cab长货斗物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	5692	2014	1848	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	5695	2014	1847	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	6200	2014	1847	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
```

## 下一步优先处理

1. 闭合 Sprinter `26984` 的 `904.463` 长轴四驱 Van 外廓。
2. 拆分 Sprinter Bus `27203` 的 `903.471`、`903.472`、`903.473` 三个轴距分支。
3. 最后闭合 Ram 2500 `26876` 跨第二代末期与第三代的驾驶室／货斗边界。

推进信号：CONTINUE


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_2401-2500_ktype_dimension_mapping_final.tsv
- all_2401-2500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 最后 3 个 Ktype 已完成：`26984`、`27203`、`26876`。
* 当前批次 **100 个输入 Ktype 全部覆盖**，共形成 **138 条 READY 映射**。
* 最终 DIMENSION_GROUP 表共 **97 个尺寸组**。
* 已完成机械检查：表头正确、`id` 唯一、尺寸组 ID 唯一、映射引用全部闭合、无孤立尺寸组、三维和来源均非空。
* 两个指定 TSV 文件已生成。

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**100**
* READY 映射行：**138**
* PENDING：**0**
* DIMENSION_GROUP：**97**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
26654_phase1	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	HIGH	Phase I外廓。	READY
26654_phase2	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	HIGH	Phase II外廓。	READY
26654_phase3	26654	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	HIGH	Phase III外廓。	READY
26655_phase1	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	HIGH	Phase I外廓。	READY
26655_phase2	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	HIGH	Phase II外廓。	READY
26655_phase3	26655	SUV	Koleos I		5	EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	HIGH	Phase III外廓。	READY
26656	26656	Sedan	Priora I	2170	4	EU-LADA-PRIORA-I-2170-SEDAN-01	HIGH		READY
26657_prefl	26657	Hatchback	Priora I	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	HIGH	改款前五门外廓。	READY
26657_facelift	26657	Hatchback	Priora I	2172	5	EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	HIGH	改款后车高变化。	READY
26658	26658	Wagon	Kalina I	1117	5	EU-LADA-KALINA-I-1117-WAGON-01	HIGH		READY
26659	26659	Van	Fiorino III		5	EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH	货运与乘用版本共用外部车身。	READY
26660	26660	Van	Fiorino III		5	EU-FIAT-FIORINO-III-VAN-MPV-01	HIGH	货运与乘用版本共用外部车身。	READY
26661	26661	Hatchback	Ignis II	MH	5	EU-SUZUKI-IGNIS-II-MH-HATCHBACK-5D-01	HIGH		READY
26662	26662	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	HIGH	SLK 350外廓。	READY
26663	26663	Convertible	SLK R171 facelift	R171	2	EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	HIGH	SLK 200 Kompressor外廓。	READY
26669	26669	Van	Fiesta V Van		3	EU-FORD-FIESTA-V-VAN-3D-PREFL-01	HIGH	改款前三门厢式车。	READY
26670_prefl	26670	Van	Fiesta V Van		3	EU-FORD-FIESTA-V-VAN-3D-PREFL-01	HIGH	改款前三门厢式车。	READY
26670_facelift	26670	Van	Fiesta V Van facelift		3	EU-FORD-FIESTA-V-VAN-3D-FACELIFT-01	HIGH	改款后三门厢式车。	READY
26695	26695	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH	标准轴距SUV。	READY
26696	26696	SUV	Escalade III		5	EU-CADILLAC-ESCALADE-III-SUV-01	HIGH	标准轴距SUV。	READY
26732	26732	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26739	26739	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26740	26740	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26742	26742	MPV	Combo Tour D	X12	5	EU-OPEL-COMBO-TOUR-D-X12-MPV-L1H1-01	HIGH	标准轴距、标准顶乘用版。	READY
26743	26743	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26752	26752	Coupe	CC I facelift		4	EU-VW-CC-I-FACELIFT-COUPE-4D-01	HIGH		READY
26753	26753	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26754	26754	MPV	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	HIGH	Version 11短轴低顶Bus物理外廓。	READY
26755	26755	Van	Ducato II facelift	244		EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	HIGH	Version 15短轴低顶Van物理外廓。	READY
26760	26760	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26762	26762	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26765_prefl	26765	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	HIGH	211 hp 4MATIC改款前分支。	READY
26765_facelift	26765	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	HIGH	211 hp 4MATIC改款后分支。	READY
26773	26773	SUV	Escalade II		5	EU-CADILLAC-ESCALADE-II-SUV-01	HIGH	标准轴距6.0 AWD SUV。	READY
26775	26775	Van	Ducato II	X230		EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	MEDIUM	短轴标准顶Van外廓。	READY
26781	26781	Sedan	Caprice III		4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH		READY
26785	26785	SUV	Escalade II		5	EU-CADILLAC-ESCALADE-II-SUV-01	MEDIUM	输入驱动字段与6.0量产资料不一致；按标准轴距SUV外廓映射。	READY
26787	26787	Coupe	CLA C117	C117	4	EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	MEDIUM	360 hp AMG对应改款前C117；输入结束年月晚于该功率版本。	READY
26792_2dr	26792	SUV	Tahoe I		2	EU-CHEVROLET-TAHOE-I-SUV-2D-01	MEDIUM	两门物理分支。	READY
26792_4dr	26792	SUV	Tahoe I		4	EU-CHEVROLET-TAHOE-I-SUV-4D-01	MEDIUM	四门物理分支。	READY
26808_prefl	26808	Hatchback	i10 I		5	EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	HIGH	改款前外廓。	READY
26808_facelift	26808	Hatchback	i10 I		5	EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	HIGH	改款后外廓。	READY
26815_prefl	26815	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	HIGH	改款前AWD外廓。	READY
26815_facelift	26815	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	HIGH	改款后AWD外廓。	READY
26816	26816	Sedan	Arnage T		4	EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	HIGH	输入BodyStyle为Coupe；该版本实际为4门Sedan。	READY
26831	26831	Sedan	Insignia A facelift		4	EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	HIGH		READY
26835	26835	Convertible	Continental GTC I		2	EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	HIGH		READY
26836	26836	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
26837	26837	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	平台底盘外廓。	READY
26838	26838	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	封闭式Van外廓。	READY
26840	26840	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	封闭式Van外廓。	READY
26847	26847	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH		READY
26848_prefl	26848	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26848_facelift	26848	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26852	26852	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH		READY
26859_prefl	26859	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	HIGH	改款前后驱外廓。	READY
26859_facelift	26859	Sedan	Q50 I	V37	4	EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	HIGH	改款后后驱外廓。	READY
26860	26860	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	MEDIUM	输入2.0 TDI 110 hp版本名称与代际功率目录存在差异，但物理外廓归入改款前Variant。	READY
26864_regcab_longbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	MEDIUM	Regular Cab长货斗物理分支。	READY
26864_clubcab_shortbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Club Cab短货斗物理分支。	READY
26864_clubcab_longbed	26864	Pickup	Ram 2500 II		2	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Club Cab长货斗物理分支。	READY
26864_quadcab_shortbed	26864	Pickup	Ram 2500 II		4	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	MEDIUM	Quad Cab短货斗物理分支。	READY
26864_quadcab_longbed	26864	Pickup	Ram 2500 II		4	EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	MEDIUM	Quad Cab长货斗物理分支。	READY
26867	26867	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	平台底盘外廓。	READY
26876_regcab_longbed	26876	Pickup	Ram 2500 III		2	EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	HIGH	Regular Cab长货斗物理分支。	READY
26876_quadcab_shortbed	26876	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	HIGH	Quad Cab短货斗物理分支。	READY
26876_quadcab_longbed	26876	Pickup	Ram 2500 III		4	EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	HIGH	Quad Cab长货斗物理分支。	READY
26883	26883	Wagon	Insignia A facelift		5	EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	HIGH		READY
26890	26890	Sedan	Galant VII	E55A	4	EU-MITSUBISHI-GALANT-VII-E55A-SEDAN-4D-01	MEDIUM	输入136 hp与目录137 hp为市场计量差异。	READY
26893	26893	Convertible	Aventador LP 700-4 Roadster		2	EU-LAMBORGHINI-AVENTADOR-LP700-4-ROADSTER-CONVERTIBLE-01	HIGH	输入Targa按量产Roadster外廓归一。	READY
26911_prefl	26911	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26911_facelift	26911	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26912_prefl	26912	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26912_facelift	26912	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26913_prefl	26913	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
26913_facelift	26913	Sedan	A4 B8	8K2	4	EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
26914_prefl	26914	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
26914_facelift	26914	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
26916_prefl	26916	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前外廓。	READY
26916_facelift	26916	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后外廓。	READY
26936	26936	Sedan	Flying Spur II		4	EU-BENTLEY-FLYING-SPUR-II-SEDAN-4D-01	MEDIUM	460 kW W12对应第二代Flying Spur；输入结束年月延伸至换代边界。	READY
26960	26960	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH		READY
26970	26970	Sedan	Elantra IV		4	EU-HYUNDAI-ELANTRA-IV-SEDAN-4D-01	HIGH		READY
26977	26977	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
26980_prefl	26980	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-PREFL-01	MEDIUM	改款前外廓。	READY
26980_facelift	26980	SUV	X1 E84	E84	5	EU-BMW-X1-E84-SUV-FACELIFT-01	MEDIUM	改款后车长变化。	READY
26984	26984	Van	Sprinter I W904	904.463	4	EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-L3H2-4X4-01	MEDIUM	4025 mm轴距长轴高顶四驱Van外廓。	READY
26985_l1h1	26985	Van	Sprinter I W903	903.461	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L1H1-4X4-01	MEDIUM	短轴低顶四驱Van物理分支。	READY
26985_l2h1	26985	Van	Sprinter I W903	903.462	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L2H1-4X4-01	MEDIUM	中轴低顶四驱Van物理分支。	READY
26988_l1	26988	Van	Sprinter Classic W909	909.632	4	EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	HIGH	3550 mm轴距Van物理分支。	READY
26988_l2	26988	Van	Sprinter Classic W909	909.633	4	EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	HIGH	4025 mm轴距Van物理分支。	READY
26997	26997	Pickup	Porter III			EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	MEDIUM	CRDi版本沿用同期平台底盘外廓。	READY
26998	26998	Van	Porter III			EU-HYUNDAI-PORTER-III-VAN-01	MEDIUM	CRDi版本沿用同期封闭式Van外廓。	READY
27004	27004	Hatchback	Aveo II	T300	5	EU-CHEVROLET-AVEO-II-T300-HATCHBACK-5D-01	MEDIUM	140 hp地区版本按T300五门外廓。	READY
27009	27009	Wagon	Golf VII Variant		5	EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	HIGH		READY
27041	27041	SUV	Sceo		5	EU-SHUANGHUAN-SCEO-SUV-5D-01	HIGH	CEO/Sceo为同车型命名差异。	READY
27063	27063	SUV	G-Class Long W463 facelift 2007	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-LONG-G55-500-SUV-01	MEDIUM	500 hp版本对应2007改款长轴车身；输入结束年月延伸至后续507 hp版本。	READY
27067	27067	Convertible	900 I Cabriolet		2	EU-SAAB-900-I-CONVERTIBLE-2D-01	HIGH		READY
27068_3dr_prefl	27068	Hatchback	900 I Combi Coupe		3	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-PREFL-01	MEDIUM	改款前三门物理分支。	READY
27068_5dr_prefl	27068	Hatchback	900 I Combi Coupe		5	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-PREFL-01	MEDIUM	改款前五门物理分支。	READY
27068_3dr_facelift	27068	Hatchback	900 I Combi Coupe facelift		3	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-FACELIFT-01	MEDIUM	改款后三门物理分支。	READY
27068_5dr_facelift	27068	Hatchback	900 I Combi Coupe facelift		5	EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-FACELIFT-01	MEDIUM	改款后五门物理分支。	READY
27077	27077	Coupe	XJS		2	EU-JAGUAR-XJS-COUPE-2D-01	MEDIUM	输入Model写作Xj；3.6 Coupe对应XJS Coupe。	READY
27098	27098	Hatchback	Fiesta II (Mk2)	FBD	3	EU-FORD-FIESTA-II-MK2-HATCHBACK-3D-01	HIGH		READY
27101	27101	Sedan	19 I Chamade	L53	4	EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	HIGH		READY
27115_3dr	27115	Hatchback	Ibiza II	6K1	3	EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	MEDIUM	三门物理分支。	READY
27115_5dr	27115	Hatchback	Ibiza II	6K1	5	EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	MEDIUM	五门物理分支。	READY
27130	27130	Hatchback	Swift II facelift	SF413	3	EU-SUZUKI-SWIFT-II-EA-MA-HATCHBACK-3D-FACELIFT-01	MEDIUM	86 hp三门Hatchback分支。	READY
27132	27132	SUV	Samurai	SJ413	3	EU-SUZUKI-SAMURAI-SJ413-SUV-01	HIGH		READY
27134	27134	Hatchback	400 (RT)	RT	5	EU-ROVER-400-RT-HATCHBACK-5D-01	HIGH		READY
27141	27141	Hatchback	Bravo I		3	EU-FIAT-BRAVO-I-HATCHBACK-3D-01	HIGH		READY
27148	27148	Wagon	V40 I	VW	5	EU-VOLVO-V40-I-VW-WAGON-5D-FACELIFT-01	MEDIUM	2000年后更新外廓。	READY
27154	27154	Wagon	V70 III facelift		5	EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	HIGH		READY
27163_swb	27163	MPV	Ducato II	X230		EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	MEDIUM	短轴Panorama物理分支。	READY
27163_lwb	27163	MPV	Ducato II	X230		EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	MEDIUM	长轴标准顶物理分支。	READY
27165_l1h1	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L1H1-01	MEDIUM	短轴低顶物理分支。	READY
27165_l1h2	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L1H2-01	MEDIUM	短轴高顶物理分支。	READY
27165_l2h2	27165	Van	Ducato I	280		EU-FIAT-DUCATO-I-280-VAN-L2H2-01	MEDIUM	长轴高顶物理分支。	READY
27166	27166	Sedan	323 S IV	BG	4	EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	MEDIUM	输入87 hp与欧洲目录计量值存在轻微差异。	READY
27168	27168	MPV	Multivan T5	T5	5	EU-VW-MULTIVAN-T5-MPV-SWB-01	HIGH		READY
27169	27169	MPV	Partner I Phase I		5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	MEDIUM	货运与乘用版本共用外部车身。	READY
27171	27171	MPV	Partner I Phase I		5	EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	MEDIUM	货运与乘用版本共用外部车身。	READY
27173	27173	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	MEDIUM	底盘驾驶室外廓。	READY
27174	27174	Pickup	Expert I	223	2	EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	MEDIUM	底盘驾驶室外廓。	READY
27175	27175	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	HIGH	短轴底盘驾驶室。	READY
27176_swb	27176	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	HIGH	短轴底盘驾驶室。	READY
27176_lwb	27176	Pickup	J5 I	280L	2	EU-PEUGEOT-J5-I-280L-CHASSIS-LWB-01	HIGH	长轴底盘驾驶室。	READY
27203_l1h1	27203	MPV	Sprinter I W903	903.471	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L1H1-01	MEDIUM	短轴标准顶Bus物理分支。	READY
27203_l2h1	27203	MPV	Sprinter I W903	903.472	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L2H1-01	MEDIUM	中轴标准顶Bus物理分支。	READY
27203_l3h2	27203	MPV	Sprinter I W903	903.473	4	EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L3H2-01	MEDIUM	长轴高顶Bus物理分支。	READY
27206	27206	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
27207_prefl	27207	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
27207_facelift	27207	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
27208	27208	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
27209	27209	Sedan	156 (932)	932	4	EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	HIGH		READY
27215	27215	Convertible	Sport Spider		2	EU-RENAULT-SPORT-SPIDER-CONVERTIBLE-2D-01	HIGH		READY
27216_swb	27216	Van	Hiace IV (H100)	LH102		EU-TOYOTA-HIACE-IV-H100-VAN-LH102-SWB-01	MEDIUM	后轮驱动短轴物理分支。	READY
27216_lwb	27216	Van	Hiace IV (H100)	LH112		EU-TOYOTA-HIACE-IV-H100-VAN-LH112-LWB-01	MEDIUM	后轮驱动长轴物理分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_2401-2500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-KOLEOS-I-SUV-PHASE-I-01	4520	1855	1695	Auto-Data Renault Koleos model dimensions	https://www.auto-data.net/en/renault-koleos-model-1050
EU-RENAULT-KOLEOS-I-SUV-PHASE-II-01	4520	1855	1695	Auto-Data Renault Koleos Phase II	https://www.auto-data.net/en/renault-koleos-phase-ii-generation-4296
EU-RENAULT-KOLEOS-I-SUV-PHASE-III-01	4520	1865	1695	Automobile-Catalog 2015 Renault Koleos 2.0 dCi	https://www.automobile-catalog.com/car/2015/2959325/renault_koleos_2_0_dci_150_4x2.html
EU-LADA-PRIORA-I-2170-SEDAN-01	4350	1680	1420	Auto-Data Lada Priora I Sedan facelift 1.6	https://www.auto-data.net/en/lada-priora-i-sedan-facelift-2013-1.6-106hp-22344
EU-LADA-PRIORA-I-2172-HATCHBACK-PREFL-01	4210	1680	1420	Drive Place Lada Priora I 5-door Hatchback	https://lada.drive.place/2170/i/group_hatchback_5d/344965
EU-LADA-PRIORA-I-2172-HATCHBACK-FACELIFT-01	4210	1680	1435	Auto-Data Lada Priora I Hatchback facelift	https://www.auto-data.net/en/lada-priora-i-hatchback-facelift-2013-generation-4632
EU-LADA-KALINA-I-1117-WAGON-01	4040	1700	1500	Encycarpedia Lada Kalina Universal 1117	https://www.encycarpedia.com/lada/07-kalina-universal-1117-estate
EU-FIAT-FIORINO-III-VAN-MPV-01	3864	1716	1721	Auto-Data Fiat Fiorino	https://www.auto-data.net/en/fiat-fiorino-model-760
EU-SUZUKI-IGNIS-II-MH-HATCHBACK-5D-01	3770	1605	1565	Auto-Data Suzuki Ignis I MH 1.3 4WD	https://www.auto-data.net/en/suzuki-ignis-i-mh-1.3-i-16v-93hp-4wd-16417
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK350-01	4107	1788	1298	Auto-Data Mercedes-Benz SLK R171 facelift SLK 350	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-350-v6-305hp-7g-tronic-42051
EU-MERCEDES-BENZ-SLK-R171-FACELIFT-CONVERTIBLE-SLK200-01	4107	1777	1296	Auto-Data Mercedes-Benz SLK R171 facelift SLK 200 Kompressor	https://www.auto-data.net/en/mercedes-benz-slk-r171-facelift-2008-slk-200-kompressor-184hp-automatic-41191
EU-FORD-FIESTA-V-VAN-3D-PREFL-01	3917	1683	1467	Ford Fiesta Van brochure	https://manuals.plus/m/7218d31c7755745164911cb2826b7a226d785b6c13d9176ee306d168ced6b2c2
EU-FORD-FIESTA-V-VAN-3D-FACELIFT-01	3918	1683	1468	Autogidas Ford Fiesta V Van 1.4 TDCi	https://autogidas.lt/en/auto-katalogas/ford/fiesta/v-an-1.4-tdci-2006-2008-k65240
EU-CADILLAC-ESCALADE-III-SUV-01	5144	2008	1887	Auto-Data Cadillac Escalade III	https://www.auto-data.net/en/cadillac-escalade-iii-generation-2489
EU-VW-CC-I-FACELIFT-COUPE-4D-01	4802	1855	1417	Auto-Data Volkswagen CC I facelift 2.0 TSI	https://www.auto-data.net/en/volkswagen-cc-i-facelift-2012-2.0-tsi-210hp-dsg-18443
EU-OPEL-COMBO-TOUR-D-X12-MPV-L1H1-01	4390	1831	1845	Auto-Data Opel Combo Tour D	https://www.auto-data.net/en/opel-combo-tour-d-generation-4218
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481	Auto-Data Volkswagen Golf VII Variant	https://www.auto-data.net/en/volkswagen-golf-vii-variant-generation-4063
EU-FIAT-DUCATO-X244-BODY-11-SWB-LOWROOF-01	4749	2024	2154	Fiat Ducato X244 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-FIAT-DUCATO-X244-BODY-15-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato X244 eLearn vehicle dimensions	https://4cardata.info/elearn/244/2/244000001/244000003/244000000/244000010
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-PREFL-01	4691	1777	1432	Auto-Data Mercedes-Benz CLA Coupe C117	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-generation-4116
EU-MERCEDES-BENZ-CLA-C117-COUPE-4D-FACELIFT-01	4640	1777	1432	Auto-Data Mercedes-Benz CLA Coupe C117 facelift	https://www.auto-data.net/en/mercedes-benz-cla-coupe-c117-facelift-2016-generation-4746
EU-CADILLAC-ESCALADE-II-SUV-01	5052	2004	1885	Auto-Data Cadillac Escalade II 6.0 V8 AWD	https://www.auto-data.net/en/cadillac-escalade-ii-6.0-i-v8-awd-349hp-11729
EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	4655	1998	2150	Gazoo Fiat Ducato dimensions; Motor-Doctor Fiat Ducato 230L 2.0 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://www.motor-doctor.co.uk/fiat/ducato/ducato-box-230l/26775-2-0-4x4
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420	Drom Chevrolet Caprice III dimensions	https://www.drom.ru/catalog/chevrolet/caprice/specs/dimensions/
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839	Automobile-Catalog 1995 Chevrolet Tahoe K1500 2-Door	https://www.automobile-catalog.com/car/1995/483965/chevrolet_tahoe_k1500_2-door_5_7l_v-8_efi_automatic.html
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783	Automobile-Catalog 1995 Chevrolet Tahoe C1500 4-Door	https://www.automobile-catalog.com/car/1995/484010/chevrolet_tahoe_c1500_4-door_5_7l_v-8_efi_automatic.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-PREFL-01	3565	1595	1540	Automobile-Catalog 2008 Hyundai i10 1.1	https://www.automobile-catalog.com/car/2008/1180925/hyundai_i10_1_1_style.html
EU-HYUNDAI-I10-I-HATCHBACK-5D-FACELIFT-01	3585	1595	1540	Auto-Data Hyundai i10 I facelift	https://www.auto-data.net/en/hyundai-i10-i-facelift-2011-generation-5787
EU-INFINITI-Q50-I-V37-SEDAN-PREFL-01	4783	1824	1443	Auto-Data Infiniti Q50 S 3.5 Hybrid	https://www.auto-data.net/en/infiniti-q50-s-3.5-v6-364hp-hybrid-automatic-18982
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-AWD-01	4810	1820	1445	Auto-Data Infiniti Q50 facelift Hybrid AWD	https://www.auto-data.net/en/infiniti-q50-facelift-2017-3.5-364hp-hybrid-awd-automatic-31420
EU-BENTLEY-ARNAGE-T-SEDAN-4D-01	5400	1900	1515	Auto-Data Bentley Arnage T 6.8i V8 Biturbo	https://www.auto-data.net/en/bentley-arnage-t-6.8i-v8-biturbo-507hp-automatic-35870
EU-OPEL-INSIGNIA-A-FACELIFT-SEDAN-01	4842	1858	1498	Automobile-Catalog 2014 Opel Insignia facelift	https://www.automobile-catalog.com/car/2014/2537405/opel_insignia_5d_1_6_sidi_turbo_ecoflex_170.html
EU-BENTLEY-CONTINENTAL-GTC-CONVERTIBLE-01	4807	1918	1398	Auto-Data Bentley Continental GTC	https://www.auto-data.net/en/bentley-continental-gtc-6.0-i-w12-48v-560hp-6754
EU-AUDI-A4-B8-8K2-SEDAN-PREFL-01	4703	1826	1426	Auto-Data Audi A4 B8 8K 2.0 TDI	https://www.auto-data.net/en/audi-a4-b8-8k-2.0-tdi-170hp-4310
EU-HYUNDAI-PORTER-III-PLATFORM-CHASSIS-01	4750	1690	1930	Truck1 Hyundai Porter 2.5 D Flatbed specifications	https://www.truck1.eu/blog/hyundai-porter-2-5-d-80-hp-tech-specs-t27426
EU-HYUNDAI-PORTER-III-VAN-01	4790	1690	1965	Motoro Hyundai H100 Van 2.5D specifications	https://motoro.ch/en/fiche-technique/hyundai/h-100-van-2-5d
EU-AUDI-A4-B8-8K2-SEDAN-FACELIFT-01	4701	1826	1427	Auto-Data Audi A4 B8 8K facelift	https://www.auto-data.net/en/audi-a4-b8-8k-facelift-2011-2.0-tfsi-211hp-26805
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 8K	https://www.auto-data.net/en/audi-a4-avant-b8-8k-2.0-tdi-170hp-4333
EU-INFINITI-Q50-I-V37-SEDAN-FACELIFT-RWD-01	4810	1820	1430	Auto-Data Infiniti Q50 facelift Hybrid RWD	https://www.auto-data.net/en/infiniti-q50-facelift-2017-3.5-364hp-hybrid-automatic-31356
EU-DODGE-RAM-2500-II-PICKUP-REGCAB-LONGBED-01	5692	2014	1848	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-SHORTBED-01	5695	2014	1847	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
EU-DODGE-RAM-2500-II-PICKUP-EXTCAB-LONGBED-01	6200	2014	1847	Dodge Ram Pickup 1999 official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/1999_pickups.pdf
EU-DODGE-RAM-2500-III-PICKUP-REGCAB-LONGBED-01	5834	2029	1875	Dodge 2003 Ram 2500/3500 preliminary specifications	https://www.rockcrawler.com/features/newsshorts/02may/dodge_25003500specs.asp
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-SHORTBED-01	5784	2029	1890	Dodge 2003 Ram 2500/3500 preliminary specifications	https://www.rockcrawler.com/features/newsshorts/02may/dodge_25003500specs.asp
EU-DODGE-RAM-2500-III-PICKUP-QUADCAB-LONGBED-01	6342	2029	1890	Dodge 2003 Ram 2500/3500 preliminary specifications	https://www.rockcrawler.com/features/newsshorts/02may/dodge_25003500specs.asp
EU-OPEL-INSIGNIA-A-FACELIFT-WAGON-5D-01	4913	1858	1513	Automobile-Catalog 2013 Opel Insignia Sports Tourer facelift	https://www.automobile-catalog.com/car/2013/2537795/opel_insignia_sports_tourer_2_0_sidi_turbo_250_4x4_automatic.html
EU-MITSUBISHI-GALANT-VII-E55A-SEDAN-4D-01	4620	1730	1405	Auto-Data Mitsubishi Galant VII	https://www.auto-data.net/en/mitsubishi-galant-vii-generation-3374
EU-LAMBORGHINI-AVENTADOR-LP700-4-ROADSTER-CONVERTIBLE-01	4780	2030	1136	Auto-Data Lamborghini Aventador LP 700-4 Roadster	https://www.auto-data.net/en/lamborghini-aventador-lp-700-4-roadster-generation-4686
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 8K facelift	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-generation-4134
EU-BENTLEY-FLYING-SPUR-II-SEDAN-4D-01	5299	1976	1488	Auto-Data Bentley Flying Spur	https://www.auto-data.net/en/bentley-flying-spur-model-2103
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468	Auto-Data BMW 5 Series E60 LCI 520i	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-520i-170hp-steptronic-28111
EU-HYUNDAI-ELANTRA-IV-SEDAN-4D-01	4505	1775	1490	Auto-Data Hyundai Elantra IV 2.0 i 16V	https://www.auto-data.net/en/hyundai-elantra-iv-2.0-i-16v-143hp-13900
EU-BMW-X1-E84-SUV-PREFL-01	4454	1798	1545	Auto-Data BMW X1 E84	https://www.auto-data.net/en/bmw-x1-e84-generation-1990
EU-BMW-X1-E84-SUV-FACELIFT-01	4477	1798	1545	Auto-Data BMW X1 E84 LCI	https://www.auto-data.net/en/bmw-x1-e84-lci-facelift-2012-generation-3856
EU-MERCEDES-BENZ-SPRINTER-I-W904-VAN-L3H2-4X4-01	6535	1933	2605	Mercedes-Benz Sprinter 414 D 4x4 904.463 identification; CarsGuide Mercedes-Benz Sprinter 2000 dimensions	https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/414-d-4x4-1997-2006-k122369; https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2000
EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L1H1-4X4-01	5004	1981	2362	Drom Mercedes-Benz Sprinter W903 4WD L1H1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/453198/
EU-MERCEDES-BENZ-SPRINTER-I-W903-VAN-L2H1-4X4-01	5715	1981	2362	Drom Mercedes-Benz Sprinter W903 4WD L2H1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter/453200/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L1-01	5640	1933	2595	Drom Mercedes-Benz Sprinter Classic 311 CDI L1	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270959/
EU-MERCEDES-BENZ-SPRINTER-CLASSIC-W909-VAN-L2-01	6590	1933	2610	Drom Mercedes-Benz Sprinter Classic 311 CDI L2	https://www.drom.ru/catalog/lcv/mercedes-benz/sprinter_classic/270974/
EU-CHEVROLET-AVEO-II-T300-HATCHBACK-5D-01	4039	1735	1517	Auto-Data Chevrolet Aveo II Hatchback	https://www.auto-data.net/en/chevrolet-aveo-ii-hatchback-generation-3798
EU-SHUANGHUAN-SCEO-SUV-5D-01	4710	1871	1820	Auto-Data ShuangHuan Sceo 2.4	https://www.auto-data.net/en/shuanghuan-sceo-2.4-125hp-13941
EU-MERCEDES-BENZ-G-CLASS-W463-LONG-G55-500-SUV-01	4662	1864	1931	Auto-Data Mercedes-Benz G-Class Long W463 facelift 2007	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-facelift-2007-generation-7913
EU-SAAB-900-I-CONVERTIBLE-2D-01	4680	1690	1420	Auto-Data Saab 900 I Cabriolet	https://www.auto-data.net/en/saab-900-i-cabriolet-generation-2548
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-PREFL-01	4740	1690	1420	Auto-Data Saab 900 I Combi Coupe; CarsGuide Saab 900 1984 dimensions	https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543; https://www.carsguide.com.au/saab/900/car-dimensions/1984
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-PREFL-01	4740	1690	1420	Auto-Data Saab 900 I Combi Coupe; CarsGuide Saab 900 1984 dimensions	https://www.auto-data.net/en/saab-900-i-combi-coupe-generation-2543; https://www.carsguide.com.au/saab/900/car-dimensions/1984
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-3D-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I Combi Coupe facelift	https://www.auto-data.net/en/saab-900-model-1277
EU-SAAB-900-I-COMBI-COUPE-HATCHBACK-5D-FACELIFT-01	4680	1690	1420	Auto-Data Saab 900 I Combi Coupe facelift	https://www.auto-data.net/en/saab-900-model-1277
EU-JAGUAR-XJS-COUPE-2D-01	4820	1793	1279	Auto-Data Jaguar XJS Coupe	https://www.auto-data.net/en/jaguar-xjs-coupe-generation-67
EU-FORD-FIESTA-II-MK2-HATCHBACK-3D-01	3565	1567	1360	Auto-Data Ford Fiesta II 1.3; Classic Car Reviews Ford Fiesta Mk2	https://www.auto-data.net/en/ford-fiesta-ii-mk2-1.3-fbd-69hp-8068; https://www.classiccarreviews.co.uk/review/ford/fiesta-mk2/hatchback-1983-1989/
EU-RENAULT-19-I-CHAMADE-L53-SEDAN-4D-01	4262	1694	1412	Auto-Data Renault 19 I Chamade L53	https://www.auto-data.net/en/renault-19-i-chamade-l53-generation-2191
EU-SEAT-IBIZA-II-6K1-HATCHBACK-3D-01	3853	1640	1422	Automobile-Catalog 1997 Seat Ibiza 1.4	https://www.automobile-catalog.com/car/1997/3070025/seat_ibiza_1_4.html
EU-SEAT-IBIZA-II-6K1-HATCHBACK-5D-01	3853	1640	1422	Automobile-Catalog 1997 Seat Ibiza 1.4	https://www.automobile-catalog.com/car/1997/3070025/seat_ibiza_1_4.html
EU-SUZUKI-SWIFT-II-EA-MA-HATCHBACK-3D-FACELIFT-01	3745	1590	1350	Drive Place Suzuki Swift II three-door; AUTODOC Swift II 1.3 86 hp identification	https://suzuki.drive.place/swift/ii/group_hatchback_3d/271206; https://www.autodoc.parts/spares/suzuki/swift/swift-ii-hatchback-ea-ma/27130-1-3-sf-413
EU-SUZUKI-SAMURAI-SJ413-SUV-01	3440	1530	1680	Auto-Data Suzuki Samurai SJ	https://www.auto-data.net/en/suzuki-samurai-sj-generation-3690
EU-ROVER-400-RT-HATCHBACK-5D-01	4320	1700	1390	Auto-Data Rover 400 Hatchback RT 414 i	https://www.auto-data.net/en/rover-400-hatchback-rt-414-i-75hp-17667
EU-FIAT-BRAVO-I-HATCHBACK-3D-01	4025	1755	1420	Auto-Data Fiat Bravo 182 1.6 16V	https://www.auto-data.net/en/fiat-bravo-182-1.6-16v-103hp-7184
EU-VOLVO-V40-I-VW-WAGON-5D-FACELIFT-01	4516	1720	1425	Auto-Data Volvo V40 Combi VW	https://www.auto-data.net/en/volvo-v40-combi-vw-generation-1967
EU-VOLVO-V70-III-FACELIFT-WAGON-5D-01	4814	1907	1547	Auto-Data Volvo V70 III facelift	https://www.auto-data.net/en/volvo-v70-iii-facelift-2013-generation-4522
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104	Gazoo Fiat Ducato dimensions; Eibach Fiat Ducato Bus 2.5 TD 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://eibach.ch/en/fiat/ducato-bus-230/25-td-4x4-116-ps-94-01
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150	Gazoo Fiat Ducato dimensions; Eibach Fiat Ducato Bus 2.5 TD 4x4 identification	https://gazoo.pl/samochody/fiat/fiat-ducato/wymiary/; https://eibach.ch/en/fiat/ducato-bus-230/25-td-4x4-116-ps-94-01
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450	Transit Center Fiat Ducato I specifications; AUTODOC Fiat Ducato 280 Van 2.5 TD 4x4 identification; Autogidas Fiat Ducato I 14 specifications	https://www.transitcenter.uk/fiat-ducato-1-data-specification.php; https://www.autodoc.parts/spares/fiat/ducato/ducato-box-280/27165-2-5-td-4x4; https://autogidas.lt/en/auto-katalogas/fiat/ducato/i-14-280.-1987-1990-k17494
EU-MAZDA-323-S-IV-BG-SEDAN-4D-01	4215	1675	1375	Automobile-Catalog Mazda 323 1.6 16V GLX Sedan	https://www.automobile-catalog.com/car/1989/1645700/mazda_323_1_6_16v_glx_sedan.html
EU-VW-MULTIVAN-T5-MPV-SWB-01	4890	1904	1970	Auto-Data Volkswagen Transporter T5 L1H1	https://www.auto-data.net/en/volkswagen-transporter-t5-panel-van-1.9-tdi-86hp-l1h1-49879
EU-PEUGEOT-PARTNER-I-PHASE-I-VAN-MPV-01	4110	1720	1870	Auto-Data Peugeot Partner I Phase I 1.9 D	https://www.auto-data.net/en/peugeot-partner-i-phase-i-1.9-d-70hp-42013
EU-PEUGEOT-EXPERT-I-PLATFORM-CHASSIS-01	4522	1844	1919	Autogidas Peugeot Expert I 2.0 HDI 220C specifications	https://autogidas.lt/en/auto-katalogas/peugeot/expert/i-2.0-hdi-220c-2004-2006-k51951
EU-PEUGEOT-J5-I-280L-CHASSIS-SWB-01	4759	1965	1900	ParuVendu Peugeot J5 1400 D short 4x4 chassis cab; ParuVendu Peugeot J5 1400 TBO D short 4x4 chassis cab	https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-d-court-4x4-10-cv-diesel/3056820/; https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-tbo-d-court-4x4-10-cv-diesel/3056821/
EU-PEUGEOT-J5-I-280L-CHASSIS-LWB-01	5489	1965	1900	ParuVendu Peugeot J5 1400 TBO D long chassis cab	https://www.paruvendu.fr/fiches-techniques-utilitaire/peugeot/j5/1400-tbo-d-long-10-cv-diesel/3056842/
EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L1H1-01	4885	1933	2345	Mercedes-Benz Sprinter 310 D 903.471 identification; Mercedes-Benz Sprinter first-generation dimensions	https://www.autodoc.parts/car-parts/fuel-injection-pump-high-pressure-pump-12903/mercedes-benz/sprinter/sprinter-3-t-bus-903/27203-310-d-903-471-903-472-903-473; https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2000
EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L2H1-01	5585	1933	2345	Mercedes-Benz Sprinter 310 D 903.472 identification; CarsGuide Mercedes-Benz Sprinter 2000 dimensions	https://partsouq.com/en/catalog/genuine/diagram?c=MB201810&number=A0085455426; https://www.carsguide.com.au/mercedes-benz/sprinter/car-dimensions/2000
EU-MERCEDES-BENZ-SPRINTER-I-W903-BUS-L3H2-01	6535	1933	2570	Mercedes-Benz Sprinter 310 D 903.473 identification; Autogidas Mercedes-Benz Sprinter 310 D long body dimensions	https://www.autodoc.parts/car-parts/fuel-injection-pump-high-pressure-pump-12903/mercedes-benz/sprinter/sprinter-3-t-bus-903/27203-310-d-903-471-903-472-903-473; https://autogidas.lt/en/auto-katalogas/mercedes-benz/sprinter/310-d-903.463-1996-2000-k31199
EU-ALFA-ROMEO-156-932-SEDAN-FACELIFT-01	4435	1743	1430	Auto-Data Alfa Romeo 156 932 facelift	https://www.auto-data.net/en/alfa-romeo-156-932-facelift-2003-generation-392
EU-ALFA-ROMEO-156-932-SEDAN-PREFL-01	4430	1745	1415	Auto-Data Alfa Romeo 156 932	https://www.auto-data.net/en/alfa-romeo-156-932-generation-394
EU-RENAULT-SPORT-SPIDER-CONVERTIBLE-2D-01	3795	1830	1250	Auto-Data Renault Sport Spider	https://www.auto-data.net/en/renault-sport-spider-generation-2157
EU-TOYOTA-HIACE-IV-H100-VAN-LH102-SWB-01	4615	1690	1935	Auto-Data Toyota HiAce IV H100; AUTODOC Toyota Hiace Van H100 2.4 D Ktype identification	https://www.auto-data.net/en/toyota-hiace-iv-h100-2.4-i-132hp-3186; https://www.autodoc.parts/car-parts/battery-10142/toyota/hiace/hiace-iii-box-yh7-lh6-lh7-lh5-yh5-yh6/27216-2-4-d-lh102-lh104-lh112
EU-TOYOTA-HIACE-IV-H100-VAN-LH112-LWB-01	4950	1690	1960	Auto-ABC Toyota Hiace Long 2.4 D; AUTODOC Toyota Hiace Van H100 2.4 D Ktype identification	https://www.auto-abc.eu/Toyota-Hiace/v5444-1992; https://www.autodoc.parts/car-parts/battery-10142/toyota/hiace/hiace-iii-box-yh7-lh6-lh7-lh5-yh5-yh6/27216-2-4-d-lh102-lh104-lh112
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_2401-2500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_2401-2500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_2401-2500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3504 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1751 行）

