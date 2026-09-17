# 任务：all 第 7001-7100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0071__c17a7546


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 7001-7100 行

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
all 第 7001-7100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-M5-SEDAN-4D-01	4620	1700	1400
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-FIAT-131-PANORAMA-WAGON-5D-S3-01	4264	1650	1400
EU-FIAT-131-S1-MIRAFIORI-SEDAN-2D-STD-01	4238	1632	1400
EU-FIAT-131-S1-MIRAFIORI-SEDAN-4D-STD-01	4238	1632	1400
EU-FIAT-131-S2-MIRAFIORI-SEDAN-2D-STD-01	4264	1651	1381
EU-FIAT-131-S2-MIRAFIORI-SEDAN-4D-STD-01	4264	1651	1381
EU-FIAT-131-S2-SEDAN-2D-RACING-01	4231	1663	1400
EU-FIAT-131-S2-SUPERMIRAFIORI-SEDAN-4D-01	4231	1651	1381
EU-FIAT-131-S3-MIRAFIORI-CL-SEDAN-4D-01	4264	1645	1411
EU-FIAT-131-S3-SEDAN-2D-MIRAFIORI-01	4264	1650	1400
EU-FIAT-131-S3-SUPERMIRAFIORI-SEDAN-4D-01	4231	1645	1405
EU-FIAT-500-110-SEDAN-01	2970	1320	1325
EU-FIAT-500-120-GIARDINIERA-WAGON-01	3185	1323	1354
EU-FIAT-500-312-CONVERTIBLE-01	3550	1650	1490
EU-FIAT-500-312-HATCHBACK-01	3546	1627	1488
EU-FIAT-500-A-TOPOLINO-SEDAN-01	3215	1275	1375
EU-FIAT-500-B-TOPOLINO-SEDAN-01	3210	1273	1375
EU-FIAT-500-C-TOPOLINO-SEDAN-01	3245	1273	1377
EU-FIAT-FIORINO-III-CARGO-PREFL-VAN-01	3864	1716	1721
EU-FIAT-FIORINO-III-COMBI-PREFL-MPV-01	3959	1716	1721
EU-FIAT-FIORINO-III-FACELIFT-CARGO-COMBI-01	3957	1716	1721
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904
EU-FIAT-FIORINO-I-VAN-01	3635	1690	1810
EU-FIAT-RITMO-138A-CABRIOLET-01	4014	1650	1400
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-105TC-01	3937	1688	1390
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	3937	1650	1400
EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	3937	1650	1400
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-105TC-01	4014	1663	1390
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-ABARTH130TC-01	4014	1663	1363
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	4014	1650	1405
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	4014	1650	1405
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1407-01	4014	1650	1407
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-ABARTH130TC-01	3993	1663	1390
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-TD-H1410-01	3993	1650	1410
EU-FIAT-TIPO-160-HATCHBACK-3D-H1445-01	3958	1700	1445
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450
EU-FIAT-TIPO-160-HATCHBACK-5D-H1445-01	3958	1700	1445
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-TURBO-01	3689	1558	1405
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-DIESEL-H1432-01	3644	1555	1432
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-LOWTRIM-01	3644	1548	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-STD-01	3644	1555	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBO-01	3644	1560	1370
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-DIESEL-H1432-01	3644	1555	1432
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-LOWTRIM-01	3644	1548	1425
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-STD-01	3644	1555	1425
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330
EU-HONDA-LEGEND-I-COUPE-2D-01	4770	1745	1320
EU-HONDA-LEGEND-II-COUPE-2D-01	4945	1810	1375
EU-HONDA-LEGEND-III-KA9-SEDAN-01	4995	1820	1430
EU-HONDA-LEGEND-II-SEDAN-4D-01	4955	1810	1405
EU-HONDA-LEGEND-I-SEDAN-4D-01	4775	1745	1375
EU-HONDA-PRELUDE-I-COUPE-2D-01	4090	1635	1290
EU-HONDA-PRELUDE-II-COUPE-2D-01	4295	1690	1295
EU-HONDA-PRELUDE-II-COUPE-2D-FACELIFT-01	4375	1690	1295
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295
EU-HONDA-PRELUDE-IV-COUPE-2D-01	4440	1765	1290
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-FACELIFT-01	4516	1723	1460
EU-MERCEDES-BENZ-C-KLASSE-S202-WAGON-PREFL-01	4487	1720	1460
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-FACELIFT-01	4516	1723	1427
EU-MERCEDES-BENZ-C-KLASSE-W202-SEDAN-PREFL-01	4487	1720	1414
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	4937	1881	1418
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	4940	1881	1416
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-FACELIFT-01	5066	1845	2033
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-PREFL-01	4922	1809	2035
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-FACELIFT-01	4616	1845	2033
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-PREFL-01	4472	1809	2045
EU-MITSUBISHI-GALANT-VII-HATCHBACK-5D-01	4620	1730	1395
EU-MITSUBISHI-GALANT-VII-SEDAN-4D-01	4620	1730	1395
EU-MOSKVICH-2140-SEDAN-4D-01	4250	1550	1480
EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	4107	1613	1250
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310
EU-PORSCHE-911-964-CONVERTIBLE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-01	4250	1652	1320
EU-PORSCHE-911-964-COUPE-CARRERA-01	4250	1652	1310
EU-PORSCHE-911-964-COUPE-RS-01	4250	1650	1310
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310
EU-PORSCHE-911-993-CONVERTIBLE-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-01	4260	1735	1315
EU-PORSCHE-911-993-COUPE-CARRERA-02	4245	1735	1300
EU-PORSCHE-911-993-COUPE-CARRERA-RS-01	4245	1735	1270
EU-PORSCHE-911-993-COUPE-GT2-01	4245	1855	1270
EU-PORSCHE-911-993-COUPE-TURBO-01	4245	1795	1285
EU-PORSCHE-911-993-TARGA-CARRERA-01	4245	1735	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-CONVERTIBLE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-997-2-COUPE-CARRERA-S-01	4435	1808	1300
EU-PORSCHE-911-997-2-COUPE-GT2-RS-01	4469	1852	1285
EU-PORSCHE-911-997-2-COUPE-GTS-01	4435	1852	1300
EU-PORSCHE-911-997-2-COUPE-TURBO-01	4450	1852	1300
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320
EU-PORSCHE-911-G-SERIES-CONVERTIBLE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-COUPE-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SERIES-SPEEDSTER-NARROW-01	4291	1652	1200
EU-PORSCHE-911-G-SERIES-SPEEDSTER-TURBOLOOK-01	4291	1775	1200
EU-PORSCHE-911-G-SERIES-TARGA-NARROW-01	4291	1610	1320
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320
EU-PORSCHE-911-G-SPEEDSTER-NARROW-01	4250	1652	1280
EU-PORSCHE-911-G-SPEEDSTER-WIDE-01	4291	1775	1280
EU-PORSCHE-914-TARGA-01	3985	1650	1230
EU-PORSCHE-924-COUPE-3D-EARLY-01	4212	1685	1270
EU-PORSCHE-924-S-COUPE-3D-01	4212	1685	1275
EU-PORSCHE-928-COUPE-EARLY-01	4447	1836	1313
EU-PORSCHE-928-COUPE-GTS-01	4523	1890	1282
EU-PORSCHE-928-COUPE-S300-01	4450	1840	1280
EU-PORSCHE-928-COUPE-S310-01	4447	1836	1282
EU-PORSCHE-928-COUPE-S4-GT-01	4520	1836	1282
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE1-01	4498	1714	1400
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	4510	1722	1385
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Moskvich	2140	1.5	Stufenheck	Heckantrieb	Benzin	55	75	Jul 1978	Nov 1983	2024-03-01	7465
Ford	Transit	2	Kasten	Heckantrieb	Benzin	57	78	Sep 1985	Sep 1992	2024-03-01	7466
Ford	Transit	2.5 D	Kasten	Heckantrieb	Diesel	50	68	Jan 1986	Sep 1991	2024-03-01	7467
Ford	Transit	2.0 I	Kasten	Heckantrieb	Benzin	72	98	Sep 1991	Jun 1994	2024-03-01	7468
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	51	70	May 1991	Jun 1994	2024-03-01	7469
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	59	80	May 1991	Jun 1994	2024-03-01	7470
Ford	Transit	2.5 TD	Kasten	Heckantrieb	Diesel	74	101	May 1991	Jun 1994	2024-03-01	7471
Fiat	Tipo	1.8 I.e.	Schrägheck	Frontantrieb	Benzin	77	105	Oct 1990	Jun 1993	2024-03-01	7472
Fiat	Tipo	1.6	Schrägheck	Frontantrieb	Benzin	61	83	Jan 1988	Oct 1991	2024-03-01	7473
Fiat	Tipo	1.1	Schrägheck	Frontantrieb	Benzin	41	56	Jan 1988	Oct 1991	2024-03-01	7474
Mercedes-benz	Cls	CLS 63 AMG	Coupe	Heckantrieb	Benzin	386	525	Jan 2011	Dec 2017	2024-03-01	7475
Ford	Transit	2.5 DI	Kasten	Heckantrieb	Diesel	63	85	Oct 1992	Jun 1994	2024-03-01	7476
Fiat	Tipo	1.7 D	Schrägheck	Frontantrieb	Diesel	43	58	Jan 1988	Oct 1994	2024-03-01	7477
Mercedes-benz	Cls	CLS 500	Coupe	Heckantrieb	Benzin	300	408	Feb 2011	Dec 2017	2024-03-01	7478
Ford	Econovan	1.4	Bus	Heckantrieb	Benzin	48	65	Mar 1986	Mar 1992	2024-03-01	7479
Ford	Econovan	2.0 D	Bus	Heckantrieb	Diesel	41	56	Mar 1986	Mar 1992	2024-03-01	7480
Ford	Transit	1.6	Kasten	Heckantrieb	Benzin	48	65	Nov 1977	Oct 1986	2024-03-01	7481
Ford	Transit	2	Kasten	Heckantrieb	Benzin	57	78	Nov 1977	Oct 1986	2024-03-01	7482
Ford	Transit	2.4 D	Kasten	Heckantrieb	Diesel	46	62	Jan 1978	Dec 1985	2024-08-01	7483
Honda	N600 iii	600	Schrägheck	Frontantrieb	Benzin	31	42	May 1968	Aug 1974	2024-03-01	7484
Honda	Civic i hatchback	1200	Schrägheck	Frontantrieb	Benzin	40	54	Jul 1972	Feb 1977	2024-03-01	7485
Honda	Civic i hatchback	1200	Schrägheck	Frontantrieb	Benzin	40	54	Mar 1977	Dec 1980	2024-03-01	7486
Mitsubishi	Galant vi	2.0 GTI 16V 4X4	Schrägheck	Allrad	Benzin	106	144	Jul 1989	Dec 1992	2024-03-01	7487
Honda	Civic iv hatchback	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Oct 1987	Dec 1989	2024-03-01	7488
Honda	Legend i	2.5 I	Stufenheck	Frontantrieb	Benzin	127	173	Feb 1987	Jun 1988	2024-03-01	7489
Honda	Prelude	2	Coupe	Frontantrieb	Benzin	84	114	Aug 1987	Jan 1992	2026-01-01	7490
Mercedes-benz	Sprinter 5-T	513 CDI 4X4	Pritsche/Fahrgestell	Allrad	Diesel	95	129	May 2011	Dec 2016	2024-03-01	7491
Fiat	1100-1900	1100	Stufenheck	Heckantrieb	Benzin	29	39	Jul 1953	Jun 1961	2024-03-01	7492
Fiat	1100-1900	1200	Stufenheck	Heckantrieb	Benzin	38	52	Feb 1959	Mar 1962	2024-03-01	7493
Fiat	1100-1900	1300	Stufenheck	Heckantrieb	Benzin	45	61	Nov 1961	Feb 1967	2024-03-01	7494
Fiat	1100-1900	1500	Stufenheck	Heckantrieb	Benzin	49	67	Nov 1961	Mar 1969	2024-03-01	7495
Fiat	1100-1900	1500	Stufenheck	Heckantrieb	Benzin	55	75	Nov 1964	Oct 1968	2024-03-01	7496
Fiat	1500-2300	2300	Stufenheck	Heckantrieb	Benzin	75	102	Jul 1962	Mar 1969	2024-03-01	7497
Renault	21	1.7	Kombi	Frontantrieb	Benzin	54	73	Jun 1986	Dec 1989	2024-03-01	7498
Renault	21	1.7	Kombi	Frontantrieb	Benzin	64	87	Jun 1987	Apr 1989	2024-03-01	7499
Pininfarina	Spidereuropa	2000	Cabriolet	Heckantrieb	Benzin	77	105	Mar 1982	Sep 1985	2024-03-01	7500
Fiat	125	1.6	Stufenheck	Heckantrieb	Benzin	74	100	Oct 1968	Oct 1973	2024-03-01	7501
Fiat	125	1.6	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1967	Mar 1974	2024-03-01	7502
Mercedes-benz	Slk	250	Cabriolet	Heckantrieb	Benzin	150	204	Feb 2011	-	2024-03-01	7503
Fiat	131	1.6 CL	Kombi	Heckantrieb	Benzin	55	75	Mar 1975	Dec 1978	2024-03-01	7504
Fiat	131	1.3 Mirafiori	Kombi	Heckantrieb	Benzin	40	54	Mar 1975	Dec 1978	2024-03-01	7505
Mercedes-benz	C-Klasse	C 180 CDI	Stufenheck	Heckantrieb	Diesel	88	120	Apr 2010	Mar 2014	2024-03-01	7507
Fiat	1500	1.5	Cabriolet	Heckantrieb	Benzin	55	75	Jun 1964	Oct 1967	2024-03-01	7509
Fiat	1500	1.5	Cabriolet	Heckantrieb	Benzin	49	67	Jun 1964	Oct 1967	2024-03-01	7510
Fiat	500	0.6	Stufenheck	Heckantrieb	Benzin	13	18	Aug 1968	Jan 1976	2024-03-01	7511
Fiat	600	0.6	Stufenheck	Heckantrieb	Benzin	15	20	Mar 1955	May 1961	2024-03-01	7512
Fiat	600	0.8	Stufenheck	Heckantrieb	Benzin	17	23	Oct 1960	Feb 1971	2024-03-01	7513
Fiat	850	0.8	Cabriolet	Heckantrieb	Benzin	36	49	Oct 1965	Oct 1968	2024-03-01	7514
Fiat	850	0.8	Stufenheck	Heckantrieb	Benzin	27	37	Jul 1964	Oct 1972	2024-03-01	7515
Fiat	850	0.8	Stufenheck	Heckantrieb	Benzin	25	34	Jul 1964	Oct 1972	2024-03-01	7516
Fiat	850	0.8 Special	Stufenheck	Heckantrieb	Benzin	35	48	Mar 1968	Oct 1972	2024-03-01	7517
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	100	136	Nov 2009	Mar 2014	2024-03-01	7518
Mercedes-benz	C-Klasse	C 250 CDI 4-matic	Stufenheck	Allrad	Diesel	150	204	Jan 2011	Jan 2014	2024-03-01	7519
Mercedes-benz	C-Klasse	C 300 CDI 4-matic	Stufenheck	Allrad	Diesel	170	231	Jan 2011	Jan 2014	2024-03-01	7520
Fiat	Jagst	770	Stufenheck	Heckantrieb	Benzin	17	23	Mar 1968	Feb 1971	2024-03-01	7521
Mercedes-benz	C-Klasse	C 350	Stufenheck	Heckantrieb	Benzin	225	306	Jan 2011	Jan 2014	2024-03-01	7522
Mercedes-benz	Mb	2.4 D	Bus	Frontantrieb	Diesel	41	56	Dec 1990	Dec 1994	2026-07-01	7523
Fiat	Ritmo	1.5	Schrägheck	Frontantrieb	Benzin	55	75	Jan 1978	Dec 1988	2024-03-01	7524
Renault	21	2.0 Turbo	Stufenheck	Frontantrieb	Benzin	119	162	Feb 1990	Oct 1992	2024-03-01	7525
Renault	21	2.0 Turbo 4X4	Stufenheck	Allrad	Benzin	119	162	Feb 1990	Oct 1992	2024-03-01	7526
Renault	21	2	Stufenheck	Frontantrieb	Benzin	99	135	Feb 1990	Jun 1994	2024-03-01	7527
Renault	21	2	Kombi	Frontantrieb	Benzin	99	135	Jun 1990	Feb 1994	2024-03-01	7528
Fiat	Uno	70 TD 1.4	Schrägheck	Frontantrieb	Diesel	52	71	Oct 1986	Oct 1990	2024-03-01	7529
Porsche	911	2.0 E	Targa	Heckantrieb	Benzin	103	140	Sep 1968	Feb 1972	2024-03-01	7530
Porsche	911	2.0 T	Targa	Heckantrieb	Benzin	81	110	Jun 1967	Feb 1972	2024-03-01	7531
Porsche	911	2.2 E	Targa	Heckantrieb	Benzin	114	155	Sep 1969	Feb 1972	2024-03-01	7532
Porsche	911	2.0 T	Coupe	Heckantrieb	Benzin	81	110	Aug 1968	Feb 1972	2024-03-01	7533
Renault	21	2.2 4X4	Kombi	Allrad	Benzin	79	107	Jun 1986	Dec 1993	2024-03-01	7534
Porsche	914	/6 2.0	Targa	Heckantrieb	Benzin	81	110	Nov 1969	Dec 1973	2024-03-01	7535
Porsche	911	2.0 L	Targa	Heckantrieb	Benzin	96	131	Jan 1967	Nov 1968	2024-03-01	7536
Porsche	911	2.0 S	Targa	Heckantrieb	Benzin	118	160	Jul 1966	Nov 1968	2024-03-01	7537
Porsche	911	2.2 S	Targa	Heckantrieb	Benzin	132	180	Sep 1969	Feb 1972	2024-03-01	7538
Mercedes-benz	C-Klasse	C 350 4-matic	Stufenheck	Allrad	Benzin	225	306	Jan 2011	Jan 2014	2024-03-01	7539
Porsche	911	2.3 S	Coupe	Heckantrieb	Benzin	140	190	Aug 1971	Aug 1973	2024-03-01	7540
Porsche	911	2.3 E	Coupe	Heckantrieb	Benzin	121	165	Aug 1971	Dec 1973	2024-03-01	7542
BMW	5	M 550 D Xdrive	Stufenheck	Allrad	Diesel	280	381	Mar 2012	Oct 2016	2024-03-01	7543
Porsche	911	2.3 E	Targa	Heckantrieb	Benzin	121	165	Aug 1971	Dec 1973	2024-03-01	7544
Porsche	911	2.7 SC Carrera RS	Coupe	Heckantrieb	Benzin	154	209	Aug 1972	Jan 1979	2024-03-01	7545
Porsche	911	2.7 SC Carrera RS	Targa	Heckantrieb	Benzin	154	209	Aug 1972	Jan 1979	2024-03-01	7546
Porsche	911	2.7 S Carrera	Coupe	Heckantrieb	Benzin	129	175	Aug 1973	Jan 1976	2024-03-01	7547
Porsche	911	2.7 S	Targa	Heckantrieb	Benzin	129	175	Aug 1973	Jan 1976	2024-03-01	7548
Porsche	911	3.0 SC Carrera	Coupe	Heckantrieb	Benzin	154	209	Mar 1974	Oct 1983	2024-03-01	7549
Porsche	924	2.0 Turbo	Coupe	Heckantrieb	Benzin	130	177	Jun 1980	Oct 1986	2024-03-01	7550
Porsche	924	2.0 Carrera GT	Coupe	Heckantrieb	Benzin	154	209	Jun 1980	Oct 1986	2024-03-01	7551
Porsche	911	3.2 SC Carrera	Coupe	Heckantrieb	Benzin	152	207	Feb 1984	Jun 1987	2024-03-01	7552
Porsche	928	5.0 S	Coupe	Heckantrieb	Benzin	212	288	Sep 1985	Dec 1986	2024-03-01	7553
Porsche	911	3.3 Turbo	Targa	Heckantrieb	Benzin	221	301	Sep 1986	Nov 1990	2024-03-01	7554
Porsche	911	3.3 Turbo	Coupe	Heckantrieb	Benzin	243	330	Sep 1986	Nov 1990	2024-03-01	7555
Porsche	959	2.8	Coupe	Allrad	Benzin	330	450	Jan 1986	Apr 1991	2024-03-01	7556
Porsche	911	3.3 Turbo S	Coupe	Heckantrieb	Benzin	261	355	Jun 1991	Dec 1992	2024-03-01	7557
Renault	21	1.7	Stufenheck	Frontantrieb	Benzin	64	87	Jun 1987	Apr 1989	2024-03-01	7558
Renault	21	2.2 4X4	Stufenheck	Allrad	Benzin	79	107	Jul 1990	Feb 1994	2024-03-01	7559
Fiat	Fiorino	60 1.1	Kasten/Großraumlimousine	Frontantrieb	Benzin	40	54	May 1988	Dec 1993	2024-03-01	7560
Renault	21	2.0 4X4	Stufenheck	Allrad	Benzin	99	135	Dec 1989	Feb 1994	2024-03-01	7561
Fiat	Fiorino	70 I.e. 1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	49	67	May 1994	May 2001	2024-03-01	7562
Fiat	Fiorino	75 I.e. 1.5	Kasten/Großraumlimousine	Frontantrieb	Benzin	55	75	May 1988	Dec 1993	2024-03-01	7563
Fiat	Fiorino	60 1.7 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	44	60	May 1988	May 2000	2024-03-01	7564
Fiat	Fiorino	60 1.7 D	Kasten/Großraumlimousine	Frontantrieb	Diesel	42	57	May 1988	Oct 1996	2024-03-01	7565
Renault	21	2.2 4X4	Schrägheck	Allrad	Benzin	79	107	Jul 1990	Jun 1994	2024-03-01	7566
Renault	21	2.0 4X4	Schrägheck	Allrad	Benzin	99	135	Sep 1990	Oct 1992	2024-03-01	7567


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓聚类完成首轮缓存关联，40 个 Ktype 已闭合，生成 49 条 READY 映射。
* 复用跨批次已有尺寸组 23 个，包括 Moskvich 2140、Mercedes-Benz CLS C218、Honda Civic/Legend/Prelude、Renault 21、Porsche 911/914/924、Fiat 500/Fiorino 等。
* 新建并闭合 Mercedes-Benz C-Class W204 改款前、改款后两个尺寸组。资料分别给出车身宽度与含后视镜宽度，因此落盘的 1770 mm 可确认是不含后视镜口径。([汽车数据网][1])
* 对生产区间跨越真实外廓变化的 CLS C218、C-Class W204 和 Porsche 911 F-Series Ktype 创建了稳定派生行，没有保留无后缀基础行。
* 暂未创建 SLK R172 尺寸组：现有资料存在 1301/1303 mm 高度差异，需要先确认 SLK 250 具体变速箱及标准配置边界。([汽车数据网][2])
* Fiat Tipo 现有资料同时出现 1445/1450 mm，并且部分页面未明确具体门数，暂不猜测关联现有四个 Tipo 尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：40
* PENDING Ktype：60
* READY 映射行：49
* 已引用尺寸组：25
* 复用已有尺寸组：23
* 本轮首次创建尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7465	7465	Sedan	Moskvich 2140	2140	4	EU-MOSKVICH-2140-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7475_prefl	7475	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	生产区间跨越2014年改款，拆分改款前外廓。	READY
7475_facelift	7475	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	生产区间跨越2014年改款，拆分改款后外廓。	READY
7478_prefl	7478	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	生产区间跨越2014年改款，拆分改款前外廓。	READY
7478_facelift	7478	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	生产区间跨越2014年改款，拆分改款后外廓。	READY
7488	7488	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
7489	7489	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7490	7490	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	第三代双门轿跑外廓。	READY
7498	7498	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7499	7499	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7500	7500	Convertible	Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	DS双门敞篷外廓。	READY
7507_prefl	7507	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	生产区间跨越2011年改款，拆分改款前外廓。	READY
7507_facelift	7507	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	生产区间跨越2011年改款，拆分改款后外廓。	READY
7511	7511	Sedan	Fiat 500 110	110F	2	EU-FIAT-500-110-SEDAN-01	HIGH	110F两门轿车外廓。	READY
7518_prefl	7518	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	生产区间跨越2011年改款，拆分改款前外廓。	READY
7518_facelift	7518	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	生产区间跨越2011年改款，拆分改款后外廓。	READY
7519_prefl	7519	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	C 250 CDI 4MATIC生产边界覆盖改款前车身。	READY
7519_facelift	7519	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	C 250 CDI 4MATIC生产边界覆盖改款后车身。	READY
7520_prefl	7520	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	C 300 CDI 4MATIC生产边界覆盖改款前车身。	READY
7520_facelift	7520	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	C 300 CDI 4MATIC生产边界覆盖改款后车身。	READY
7522	7522	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	225 kW C 350对应2011年改款后车身。	READY
7525	7525	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	第二阶段Turbo四门轿车外廓。	READY
7526	7526	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	第二阶段Turbo 4X4四门轿车外廓。	READY
7527	7527	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段四门轿车外廓。	READY
7528	7528	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7532	7532	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	HIGH	2.2升F系列Targa外廓。	READY
7534	7534	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48 4X4五门旅行车外廓。	READY
7535	7535	Targa	Porsche 914	914	2	EU-PORSCHE-914-TARGA-01	HIGH	914/6双门Targa外廓。	READY
7538	7538	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	HIGH	2.2升F系列Targa外廓。	READY
7539	7539	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	225 kW C 350 4MATIC对应2011年改款后车身。	READY
7540_preaug72	7540	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	MEDIUM	输入2.3 S按1972年车型边界归入2.4系列改款前外廓。	READY
7540_postaug72	7540	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	MEDIUM	输入2.3 S按1972年车型边界归入2.4系列改款后外廓。	READY
7542_preaug72	7542	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款前外廓。	READY
7542_postaug72	7542	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款后外廓。	READY
7544_preaug72	7544	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款前Targa外廓。	READY
7544_postaug72	7544	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款后Targa外廓。	READY
7550	7550	Coupe	Porsche 924	924	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	早期924三门轿跑外廓。	READY
7555	7555	Coupe	911 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体双门轿跑外廓。	READY
7557	7557	Coupe	911 964	964	2	EU-PORSCHE-911-964-COUPE-TURBO-01	HIGH	964 Turbo宽体双门轿跑外廓。	READY
7558	7558	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	第一阶段四门轿车外廓。	READY
7559	7559	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段4X4四门轿车外廓。	READY
7560	7560	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7561	7561	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段4X4四门轿车外廓。	READY
7562	7562	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7563	7563	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7564	7564	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7565	7565	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7566	7566	Hatchback	Renault 21	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
7567	7567	Hatchback	Renault 21	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48 4X4五门掀背外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-200-cdi-136hp-12540
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w204-facelift-2011-c-350-blueefficiency-v6-306hp-7g-tronic-plus-17357
```

## 下一步优先处理

1. 优先闭合 Ford Transit Kasten 的 MK2、VE6 不同轴距及不同车顶分支，并确认 7466–7471、7476、7481–7483 是否需要派生。
2. 批量处理早期 Fiat 1100/1200/1300/1500/2300、Fiat 125、600/850、1500 Cabriolet 等共享外廓簇。
3. 核对 Honda N600、Civic I 前后期、Mitsubishi Galant VI Hatchback，以及 Porsche 959、924 Carrera GT 和 911 特殊版本。
4. 单独解决 Fiat Tipo 门数与 1445/1450 mm 高度对应关系、SLK R172 高度冲突，以及 Sprinter 5-T 513 CDI 4X4 底盘长度边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-200-cdi-136hp-12540?utm_source=chatgpt.com "Mercedes-Benz C-class (W204) C 200 CDI (136 Hp)"
[2]: https://www.auto-data.net/en/mercedes-benz-slk-r172-slk-250-204hp-7g-tronic-plus-53840 "Mercedes-Benz SLK (R172) SLK 250 (204 Hp) 7G-TRONIC PLUS | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/fiat-tipo-160-1.1-160.aa-56hp-7066?utm_source=chatgpt.com "Fiat Tipo (160) 1.1 (160.AA) (56 Hp) /Hatchback 1988 - 1991"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增或修改 37 条映射，覆盖 28 个 Ktype。
* 已闭合 Fiat Tipo 门数分支、Honda N600/Civic I 前后期、Fiat 125/1500/850 等乘用车外廓。([汽车数据网][1])
* 新建 Mercedes-Benz SLK R172、BMW F10 M550d、Porsche 924 Carrera GT、930 Turbo Targa 和 Porsche 959 等尺寸组。([汽车数据网][2])
* Mercedes-Benz MB100、Fiat Ritmo、Porsche 911 G-Series 与 928 S 仅关联既有缓存尺寸组，未重复输出尺寸事实。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：68
* PENDING Ktype：32
* READY 映射行：86
* 已引用尺寸组：52
* 本轮首次创建尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7472	7472	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7473	7473	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7474	7474	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门掀背外廓。	READY
7477_3dr	7477	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	后期三门掀背外廓。	READY
7477_5dr	7477	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7484	7484	Hatchback	N600 III	N600	2	EU-HONDA-N600-III-HATCHBACK-2D-01	HIGH	两门掀背外廓。	READY
7485	7485	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背外廓。	READY
7486	7486	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背外廓。	READY
7501	7501	Sedan	Fiat 125	125	4	EU-FIAT-125-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7502	7502	Sedan	Fiat 125	125	4	EU-FIAT-125-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7503	7503	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	双门硬顶敞篷外廓。	READY
7509	7509	Convertible	Fiat 1500 Cabriolet		2	EU-FIAT-1500-CABRIOLET-2D-01	HIGH	双门敞篷外廓。	READY
7510	7510	Convertible	Fiat 1500 Cabriolet		2	EU-FIAT-1500-CABRIOLET-2D-01	HIGH	双门敞篷外廓。	READY
7514	7514	Convertible	Fiat 850 Spider	100GS	2	EU-FIAT-850-SPIDER-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
7515	7515	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7516	7516	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7517	7517	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	Special两门轿车外廓。	READY
7523_swb_prefl	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-PREFL-01	MEDIUM	短轴距改款前客车外廓。	READY
7523_swb_facelift	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-FACELIFT-01	MEDIUM	短轴距改款后客车外廓。	READY
7523_lwb_prefl	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-PREFL-01	MEDIUM	长轴距改款前客车外廓。	READY
7523_lwb_facelift	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-FACELIFT-01	MEDIUM	长轴距改款后客车外廓。	READY
7524_s1_3dr	7524	Hatchback	Ritmo 138A S1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	MEDIUM	S1三门掀背外廓。	READY
7524_s1_5dr	7524	Hatchback	Ritmo 138A S1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	MEDIUM	S1五门掀背外廓。	READY
7524_s2_3dr	7524	Hatchback	Ritmo 138A S2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	MEDIUM	S2三门掀背外廓。	READY
7524_s2_5dr	7524	Hatchback	Ritmo 138A S2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	MEDIUM	S2五门掀背外廓。	READY
7524_s3_3dr	7524	Hatchback	Ritmo 138A S3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	MEDIUM	S3三门掀背外廓。	READY
7524_s3_5dr	7524	Hatchback	Ritmo 138A S3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	S3五门掀背外廓。	READY
7530	7530	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	长轴距F系列双门Targa外廓。	READY
7543	7543	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	HIGH	M550d xDrive四门轿车外廓。	READY
7547	7547	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	MEDIUM	Carrera宽体双门轿跑外廓。	READY
7548	7548	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	MEDIUM	Carrera宽体双门Targa外廓。	READY
7549	7549	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	SC Carrera宽体双门轿跑外廓。	READY
7551	7551	Coupe	Porsche 924	937	3	EU-PORSCHE-924-CARRERA-GT-COUPE-3D-01	HIGH	Carrera GT宽体三门轿跑外廓。	READY
7552	7552	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	3.2 Carrera宽体双门轿跑外廓。	READY
7553	7553	Coupe	Porsche 928 S	928	3	EU-PORSCHE-928-COUPE-S310-01	MEDIUM	前期928 S三门轿跑外廓。	READY
7554	7554	Targa	911 G Series	930	2	EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	HIGH	930 Turbo宽体双门Targa外廓。	READY
7556	7556	Coupe	Porsche 959	959	2	EU-PORSCHE-959-COUPE-2D-01	HIGH	959双门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-N600-III-HATCHBACK-2D-01	3100	1320	1325	Automobile-Catalog Honda N600	https://www.automobile-catalog.com/car/1970/1082015/honda_n_600.html
EU-HONDA-CIVIC-I-HATCHBACK-3D-PREFL-01	3545	1505	1330	Automobile-Catalog Honda Civic 1200 Hatchback	https://www.automobile-catalog.com/car/1973/1085975/honda_civic_1200_hatchback.html
EU-HONDA-CIVIC-I-HATCHBACK-3D-FACELIFT-01	3560	1505	1325	Automobile-Catalog Honda Civic 1200 Hatchback	https://www.automobile-catalog.com/car/1978/1086095/honda_civic_1200_hatchback.html
EU-FIAT-125-SEDAN-4D-01	4223	1611	1440	Automobile-Catalog Fiat 125; Automobile-Catalog Fiat 125 Special	https://www.automobile-catalog.com/car/1968/710705/fiat_125.html;https://www.automobile-catalog.com/car/1968/38630/fiat_125_special.html
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301	Auto-Data; Mercedes-Benz SLK250 UK press specification	https://www.auto-data.net/en/mercedes-benz-slk-r172-slk-250-204hp-18890;https://www.netcarshow.com/mercedes-benz/2012-slk250_uk-version/
EU-FIAT-1500-CABRIOLET-2D-01	4085	1520	1290	Automobile-Catalog Fiat 1500 Cabriolet 1964; Automobile-Catalog Fiat 1500 Cabriolet 1965	https://www.automobile-catalog.com/car/1964/709010/fiat_1500_cabriolet_spider.html;https://www.automobile-catalog.com/car/1965/709070/fiat_1500_cabriolet_spider.html
EU-FIAT-850-SPIDER-CONVERTIBLE-2D-01	3780	1500	1220	Automobile-Catalog Fiat 850 Spider	https://www.automobile-catalog.com/car/1967/709625/fiat_850_spider.html
EU-FIAT-850-SEDAN-2D-01	3575	1425	1385	Automobile-Catalog Fiat 850 Super; Automobile-Catalog Fiat 850 Special	https://www.automobile-catalog.com/car/1968/709595/fiat_850_super.html;https://www.automobile-catalog.com/car/1969/709655/fiat_850_special.html
EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	4910	1860	1454	Auto-Data BMW F10 M550d; Auto-Data BMW F10 LCI M550d	https://www.auto-data.net/en/bmw-5-series-sedan-f10-m550d-381hp-xdrive-steptronic-17754;https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-m550d-381hp-xdrive-steptronic-19969
EU-PORSCHE-924-CARRERA-GT-COUPE-3D-01	4323	1727	1270	UltimateSpecs; Carfolio	https://www.ultimatespecs.com/car-specs/Porsche/16787/Porsche-924-Carrera-GT.html;https://www.carfolio.com/porsche-924-carrera-gt-23089
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310	Automobile-Catalog Porsche 911 Turbo Targa	https://www.automobile-catalog.com/car/1987/2682530/porsche_911_turbo_targa.html
EU-PORSCHE-959-COUPE-2D-01	4260	1840	1280	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/porsche-959-2.8-450hp-awd-6701;https://www.automobile-catalog.com/car/1987/57470/porsche_959.html
```

## 下一步优先处理

1. 闭合 Ford Transit Kasten 7466–7471、7476、7481–7483 的轴距、车顶及改款分支。
2. 处理 Ford Econovan 7479–7480、Mitsubishi Galant VI 7487 和 Sprinter 5-T 7491。
3. 批量闭合 Fiat 1100/1200/1300/1500/2300、Fiat 600/Jagst 及 Fiat 131 Wagon。
4. 处理 Porsche 911 早期短轴距、Carrera RS、928 与剩余特殊版本。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-tipo-160-1.1-160.aa-56hp-7066?utm_source=chatgpt.com "Fiat Tipo (160) 1.1 (160.AA) (56 Hp) /Hatchback 1988 - 1991"
[2]: https://www.auto-data.net/en/mercedes-benz-slk-r172-slk-250-204hp-18890?utm_source=chatgpt.com "Specs of Mercedes-Benz SLK (R172) SLK 250 (204 Hp) / ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮新增 28 条 READY 映射，覆盖 18 个 Ktype。
* 已闭合 Fiat 1100/1200、1300/1500、2300、131 Wagon、600/600D、Jagst 770 等早期 Fiat 外廓分支。([汽车目录][1])
* 已闭合 Mitsubishi Galant VI GTI 4X4、Fiat Uno Turbo D 前后期门数分支，以及 Porsche 911 早期短轴 Targa、Carrera RS Coupe。([Tunel.az][2])
* Transit、Econovan、Sprinter 底盘分支及异常的 Carrera RS Targa 仍未闭合。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：86
* PENDING Ktype：14
* READY 映射行：114
* 已引用尺寸组：72
* 本轮首次创建尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7487	7487	Hatchback	Galant VI	E30	5	EU-MITSUBISHI-GALANT-VI-E30-HATCHBACK-GTI4X4-01	MEDIUM	GTI 4X4五门掀背外廓。	READY
7492_s1	7492	Sedan	Fiat 1100 103 S1	103	4	EU-FIAT-1100-103-S1-SEDAN-4D-01	HIGH	第一阶段四门轿车外廓。	READY
7492_s2	7492	Sedan	Fiat 1100 103 S2	103	4	EU-FIAT-1100-103-S2-SEDAN-4D-01	HIGH	第二阶段四门轿车外廓。	READY
7492_s3	7492	Sedan	Fiat 1100 103 S3	103	4	EU-FIAT-1100-103-S3-SEDAN-4D-01	HIGH	第三阶段四门轿车外廓。	READY
7493_early	7493	Sedan	Fiat 1200 103 S3	103	4	EU-FIAT-1200-103-S3-SEDAN-EARLY-01	HIGH	早期四门轿车外廓。	READY
7493_late	7493	Sedan	Fiat 1200 103 S3	103	4	EU-FIAT-1200-103-S3-SEDAN-LATE-01	HIGH	后期四门轿车外廓。	READY
7494_prefl	7494	Sedan	Fiat 1300	Type 116	4	EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
7494_facelift	7494	Sedan	Fiat 1300	Type 116	4	EU-FIAT-1300-TYPE116-SEDAN-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
7495	7495	Sedan	Fiat 1500	Type 115	4	EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	HIGH	初期四门轿车外廓。	READY
7496	7496	Sedan	Fiat 1500 C	Type 115	4	EU-FIAT-1500C-TYPE115-SEDAN-01	HIGH	1500 C四门轿车外廓。	READY
7497	7497	Sedan	Fiat 2300	Type 114	4	EU-FIAT-2300-TYPE114-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7504	7504	Wagon	Fiat 131 S1	131	5	EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	HIGH	S1五门旅行车外廓。	READY
7505	7505	Wagon	Fiat 131 S1	131	5	EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	HIGH	S1五门旅行车外廓。	READY
7512_early	7512	Sedan	Fiat 600	100	2	EU-FIAT-600-100-SEDAN-2D-EARLY-01	HIGH	早期短车身外廓。	READY
7512_late	7512	Sedan	Fiat 600	100	2	EU-FIAT-600-100-SEDAN-2D-LATE-01	HIGH	后期长车身外廓。	READY
7513_short	7513	Sedan	Fiat 600 D	100D	2	EU-FIAT-600-100D-SEDAN-2D-SHORT-01	MEDIUM	短车身外廓分支。	READY
7513_long	7513	Sedan	Fiat 600 D	100D	2	EU-FIAT-600-100D-SEDAN-2D-LONG-01	MEDIUM	长车身外廓分支。	READY
7521	7521	Sedan	Jagst 770	100	2	EU-FIAT-JAGST-770-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7529_3dr_prefl	7529	Hatchback	Uno 146A	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBODIESEL-01	HIGH	改款前三门Turbo D外廓。	READY
7529_5dr_prefl	7529	Hatchback	Uno 146A	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-TURBODIESEL-01	HIGH	改款前五门Turbo D外廓。	READY
7529_3dr_facelift	7529	Hatchback	Uno 146A	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后三门外廓。	READY
7529_5dr_facelift	7529	Hatchback	Uno 146A	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	1989改款后五门外廓。	READY
7531_swb	7531	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	早期短轴Targa外廓。	READY
7531_lwb	7531	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	后期长轴Targa外廓。	READY
7533	7533	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	MEDIUM	长轴双门轿跑外廓。	READY
7536	7536	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	短轴Targa外廓。	READY
7537	7537	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	短轴Targa外廓。	READY
7545	7545	Coupe	911 Carrera RS	911	2	EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	HIGH	Carrera RS宽体双门轿跑外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-GALANT-VI-E30-HATCHBACK-GTI4X4-01	4530	1715	1395	Auto-Data; Tunel.az	https://www.auto-data.net/en/mitsubishi-galant-vi-hatchback-2.0-gti-16v-4x4-144hp-15392;https://tunel.az/en/catalog/mitsubishi/galant/mitsubishi-galant-vi-hatchback/833889ba-ee75-41c4-8b7f-9653a94c4394
EU-FIAT-1100-103-S1-SEDAN-4D-01	3775	1458	1485	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1953/708125/fiat_1100.html
EU-FIAT-1100-103-S2-SEDAN-4D-01	3780	1458	1485	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1957/708185/fiat_1100.html
EU-FIAT-1100-103-S3-SEDAN-4D-01	3920	1458	1490	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1959/708305/fiat_1100.html
EU-FIAT-1200-103-S3-SEDAN-EARLY-01	3920	1458	1468	Automobile-Catalog Fiat 1200 Gran Luce	https://www.automobile-catalog.com/car/1959/708335/fiat_1200_gran_luce.html
EU-FIAT-1200-103-S3-SEDAN-LATE-01	3963	1458	1470	Automobile-Catalog Fiat 1200 Gran Luce	https://www.automobile-catalog.com/car/1959/708380/fiat_1200_gran_luce.html
EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	4030	1545	1420	Automobile-Catalog Fiat 1300; Automobile-Catalog Fiat 1500	https://www.automobile-catalog.com/car/1962/709460/fiat_1300.html;https://www.automobile-catalog.com/car/1962/709490/fiat_1500.html
EU-FIAT-1300-TYPE116-SEDAN-FACELIFT-01	4030	1545	1440	Automobile-Catalog Fiat 1300 Berlina	https://www.automobile-catalog.com/car/1964/709520/fiat_1300_berlina.html
EU-FIAT-1500C-TYPE115-SEDAN-01	4130	1545	1440	Automobile-Catalog Fiat 1500C Berlina	https://www.automobile-catalog.com/car/1964/709535/fiat_1500_berlina.html
EU-FIAT-2300-TYPE114-SEDAN-4D-01	4485	1620	1470	Automobile-Catalog Fiat 2300 Berlina	https://www.automobile-catalog.com/car/1963/709235/fiat_2300.html
EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	4238	1632	1410	Automobile-Catalog Fiat 131 Mirafiori Familiare	https://www.automobile-catalog.com/car/1975/712355/fiat_131_mirafiori_familiare_1600.html
EU-FIAT-600-100-SEDAN-2D-EARLY-01	3215	1380	1405	Automobile-Catalog Fiat 600	https://www.automobile-catalog.com/car/1955/708545/fiat_600.html
EU-FIAT-600-100-SEDAN-2D-LATE-01	3315	1380	1405	Automobile-Catalog Fiat 600	https://www.automobile-catalog.com/car/1959/1759760/fiat_600_sunroof.html
EU-FIAT-600-100D-SEDAN-2D-SHORT-01	3295	1380	1405	Automobile-Catalog Fiat 600D	https://www.automobile-catalog.com/car/1960/708635/fiat_600d.html
EU-FIAT-600-100D-SEDAN-2D-LONG-01	3340	1380	1405	Automobile-Catalog Fiat 600D	https://www.automobile-catalog.com/car/1966/1759700/fiat_600d.html
EU-FIAT-JAGST-770-SEDAN-2D-01	3298	1378	1405	Automobile-Catalog NSU-Fiat Jagst 770	https://www.automobile-catalog.com/car/1962/2058440/nsu-fiat_jagst_770.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBODIESEL-01	3644	1560	1420	Automobile-Catalog Fiat Uno Turbo D	https://www.automobile-catalog.com/car/1987/53465/fiat_uno_turbo_d.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-TURBODIESEL-01	3644	1560	1420	Automobile-Catalog Fiat Uno Turbo D	https://www.automobile-catalog.com/car/1987/53465/fiat_uno_turbo_d.html
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320	Automobile-Catalog Porsche 911 T/L/S Targa	https://www.automobile-catalog.com/car/1968/2588945/porsche_911_t_targa.html;https://www.automobile-catalog.com/car/1967/2588990/porsche_911_l_targa.html;https://www.automobile-catalog.com/car/1967/2589020/porsche_911_s_targa.html
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320	Automobile-Catalog Porsche 911 Carrera RS	https://www.automobile-catalog.com/car/1972/2591255/porsche_911_carrera_rs.html
```

## 下一步优先处理

1. 利用现有 Transit MK2、VE6 与 VE6 Facelift 缓存组，闭合 7466–7471、7476、7481–7483 的轴距、车顶和改款派生关系。
2. 闭合 Ford Econovan 7479–7480 的标准顶、高顶及轴距分支。
3. 闭合 Mercedes-Benz Sprinter 5-T 7491 的驾驶室、轴距和底盘长度分支。
4. 单独处理 7546 的 Carrera RS 名称与 Targa 车身冲突。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1955/708125/fiat_1100.html?utm_source=chatgpt.com "Detailed specs review of 1955 Fiat 1100 model for Europe"
[2]: https://tunel.az/en/catalog/mitsubishi/galant/mitsubishi-galant-vi-hatchback/833889ba-ee75-41c4-8b7f-9653a94c4394?srsltid=AfmBOoq9gq9zlsYJlw0F5GyN2RNxUpQhL8fneffXaDRFrO4__dgtow2K&utm_source=chatgpt.com "Mitsubishi Galant VI Hatchback (1987-1992)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已按 Transit Mk2、Mk3、Mk4 的代际变化及短轴/长轴/车顶分支，将 7466–7471、7476、7481–7483 关联到现有缓存尺寸组；本轮未重复抓取或输出这些尺寸组。各代车身分支与生产阶段边界已闭合。([Transit Center Ford Transit Spare Parts][1])
* 7546 的 `Carrera RS Targa` 名称存在版本与车身结构冲突，本轮按明确的 Targa 车身和宽体边界关联现有 G-Series Targa 尺寸组，保留 MEDIUM 置信度。
* 7479、7480 已确认属于欧洲 Econovan KBA/KCA Bus，但尚缺可直接支持该欧洲配置完整三维及无镜宽度的可靠来源。([AM Car Parts][2])
* 7491 已确认是 Sprinter 5-T B906 513 CDI 4x4 Pritsche/Fahrgestell；现有资料仍不足以区分该 5 吨四驱底盘的全部轴距和外部高度分支。([ebay.com][3])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：97
* PENDING Ktype：3
* READY 映射行：168
* 已引用尺寸组：81
* 本轮首次创建或修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7466_mk2_swb_lowroof	7466	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7466_mk2_lwb_highroof	7466	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7466_mk3_swb_lowroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7466_mk3_lwb_midroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7466_mk3_xlwb_highroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7466_mk4_swb_lowroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7466_mk4_swb_midroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7466_mk4_lwb_midroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7466_mk4_lwb_highroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7467_swb_lowroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7467_lwb_midroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7467_xlwb_highroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长轴高顶物理外廓。	READY
7468_swb_lowroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7468_swb_midroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理外廓。	READY
7468_lwb_midroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7468_lwb_highroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7469_mk3_swb_lowroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7469_mk3_lwb_midroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7469_mk3_xlwb_highroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7469_mk4_swb_lowroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7469_mk4_swb_midroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7469_mk4_lwb_midroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7469_mk4_lwb_highroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7470_mk3_swb_lowroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7470_mk3_lwb_midroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7470_mk3_xlwb_highroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7470_mk4_swb_lowroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7470_mk4_swb_midroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7470_mk4_lwb_midroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7470_mk4_lwb_highroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7471_mk3_swb_lowroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7471_mk3_lwb_midroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7471_mk3_xlwb_highroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7471_mk4_swb_lowroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7471_mk4_swb_midroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7471_mk4_lwb_midroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7471_mk4_lwb_highroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7476_swb_lowroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7476_swb_midroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理外廓。	READY
7476_lwb_midroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7476_lwb_highroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7481_mk2_swb_lowroof	7481	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7481_mk2_lwb_highroof	7481	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7481_mk3_swb_lowroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7481_mk3_lwb_midroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7481_mk3_xlwb_highroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7482_mk2_swb_lowroof	7482	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7482_mk2_lwb_highroof	7482	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7482_mk3_swb_lowroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7482_mk3_lwb_midroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7482_mk3_xlwb_highroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7483_swb_lowroof	7483	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7483_lwb_highroof	7483	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7546	7546	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	MEDIUM	输入版本名含Carrera RS冲突；按Targa车身边界归入宽体分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 闭合 7479、7480 的欧洲 Econovan KBA/KCA Bus 三维，并确认是否存在不同轴距或车顶派生。
2. 闭合 7491 的 Sprinter 5-T B906 513 CDI 4x4 驾驶室、轴距及底盘外廓分支。
3. 三个阻塞 Ktype 完成后立即执行一次机械闭合检查并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.transitcenter.uk/transit-mk2-data-specification.php?srsltid=AfmBOopsCzmg_cRdhYf5qWNPGgxXZd46wG4Y-H_TO8hTCGjdG3pAHxJH "FORD TRANSIT MK2 - SPECIFICATIONS"
[2]: https://www.amcarparts.co.uk/mintex/789778-brake-pad-set-mintex-mdb1346-for-ford-ford-asia-oceania-kia-more-5028740002509?utm_source=chatgpt.com "Buy Brake Pad Set MDB1346 for FORD, FORD, KIA"
[3]: https://www.ebay.com/itm/317709587011?utm_source=chatgpt.com "Power Steering Rack & Pinion 22-3044 For Dodge Mercedes ..."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Ford Econovan 7479、7480。两者属于同一 KBA/KCA 客车外廓，统一关联新尺寸组 `EU-FORD-ECONOVAN-II-BUS-01`。
* Ford 官方资料及规格数据库均支持该外廓为 `4030 × 1630 × 1820 mm`；1630 mm 为车身宽度，不含后视镜。([互联网档案馆][1])
* Mercedes-Benz Sprinter 7491 已确认同时覆盖 `906.153`、`906.155`、`906.253`、`906.255` 四个单排/双排及不同轴距底盘代码，但尚未取得能够分别闭合四个物理分支、且宽度口径明确的完整三维，因此继续保留为唯一阻塞项。([Auto Doc][2])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：170
* 已确认尺寸组：82
* 本轮首次创建尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7479	7479	MPV	Econovan II		4	EU-FORD-ECONOVAN-II-BUS-01	MEDIUM	KBA/KCA四门客车外廓。	READY
7480	7480	MPV	Econovan II		4	EU-FORD-ECONOVAN-II-BUS-01	MEDIUM	KBA/KCA四门客车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-ECONOVAN-II-BUS-01	4030	1630	1820	Ford Australia Econovan official brochure; Drive.Place Ford Econovan II specifications	https://ia601208.us.archive.org/8/items/March1985FordEconovanBrochureAustralia/March_1985_Ford_Econovan_brochure_Australia.pdf;https://ford.drive.place/econovan/ii/group_minivan/722249
```

## 下一步优先处理

1. 仅处理 Ktype `7491`：分别闭合 Sprinter 5-T B906 的 `906.153`、`906.155`、`906.253`、`906.255` 单排/双排及中轴/长轴底盘外廓。
2. 取得各分支完整三维和明确无镜宽度后，将 `PENDING` 降至 0，并在下一轮直接输出两张最终完整 TSV、指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://ia601208.us.archive.org/8/items/March1985FordEconovanBrochureAustralia/March_1985_Ford_Econovan_brochure_Australia.pdf?utm_source=chatgpt.com "convert-jpg-to-pdf.net"
[2]: https://www.auto-doc.ie/car-parts/drive-shaft-10162/mercedes-benz/sprinter/sprinter-5-t-platform-chassis-906/7491-513-cdi-4x4-906-155-906-253-906-255-906-153?utm_source=chatgpt.com "MERCEDES-BENZ Sprinter 5-T Platform/Chassis (W906) 513 CDI 4x4 Drive shaft - 129 hp Diesel 95 kW 2011 - 2016 OM 651.957 ▷ AUTODOC"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_7001-7100_ktype_dimension_mapping_final.tsv
- all_7001-7100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 最后一个阻塞 Ktype `7491` 已按 `906.153`、`906.253`、`906.155`、`906.255` 拆分为 3665 mm 与 4325 mm 轴距下的单排、双排驾驶室四个物理分支。
* Sprinter 资料明确区分 1993 mm 不含后视镜车身宽度与 2426 mm 含后视镜宽度，并给出四驱车型高度增量；本轮新建四个完整尺寸组。([LastVin][1])
* 已完成轻量机械校验：映射表严格 10 列、尺寸组表严格 6 列；所有主键唯一，引用全部闭合，无孤立尺寸组、无缺失尺寸或来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终映射行：174
* 最终尺寸组：89
* 唯一 `id`：174
* 唯一 `DIMENSION_GROUP_ID`：89
* 全部映射状态：`READY`
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7465	7465	Sedan	Moskvich 2140	2140	4	EU-MOSKVICH-2140-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7466_mk2_swb_lowroof	7466	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7466_mk2_lwb_highroof	7466	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7466_mk3_swb_lowroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7466_mk3_lwb_midroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7466_mk3_xlwb_highroof	7466	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7466_mk4_swb_lowroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7466_mk4_swb_midroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7466_mk4_lwb_midroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7466_mk4_lwb_highroof	7466	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7467_swb_lowroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7467_lwb_midroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7467_xlwb_highroof	7467	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	加长轴高顶物理外廓。	READY
7468_swb_lowroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7468_swb_midroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理外廓。	READY
7468_lwb_midroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7468_lwb_highroof	7468	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7469_mk3_swb_lowroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7469_mk3_lwb_midroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7469_mk3_xlwb_highroof	7469	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7469_mk4_swb_lowroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7469_mk4_swb_midroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7469_mk4_lwb_midroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7469_mk4_lwb_highroof	7469	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7470_mk3_swb_lowroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7470_mk3_lwb_midroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7470_mk3_xlwb_highroof	7470	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7470_mk4_swb_lowroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7470_mk4_swb_midroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7470_mk4_lwb_midroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7470_mk4_lwb_highroof	7470	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7471_mk3_swb_lowroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7471_mk3_lwb_midroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7471_mk3_xlwb_highroof	7471	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7471_mk4_swb_lowroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	Mk4短轴低顶物理外廓。	READY
7471_mk4_swb_midroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	Mk4短轴中顶物理外廓。	READY
7471_mk4_lwb_midroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	Mk4长轴中顶物理外廓。	READY
7471_mk4_lwb_highroof	7471	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	Mk4长轴高顶物理外廓。	READY
7472	7472	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7473	7473	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7474	7474	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	HIGH	五门掀背外廓。	READY
7475_prefl	7475	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	生产区间跨越2014年改款，拆分改款前外廓。	READY
7475_facelift	7475	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	生产区间跨越2014年改款，拆分改款后外廓。	READY
7476_swb_lowroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7476_swb_midroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	MEDIUM	短轴中顶物理外廓。	READY
7476_lwb_midroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	MEDIUM	长轴中顶物理外廓。	READY
7476_lwb_highroof	7476	Van	Ford Transit Mk4	VE6		EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7477_3dr	7477	Hatchback	Tipo 160	160	3	EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	MEDIUM	后期三门掀背外廓。	READY
7477_5dr	7477	Hatchback	Tipo 160	160	5	EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	MEDIUM	五门掀背外廓。	READY
7478_prefl	7478	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	生产区间跨越2014年改款，拆分改款前外廓。	READY
7478_facelift	7478	Coupe	CLS C218	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	生产区间跨越2014年改款，拆分改款后外廓。	READY
7479	7479	MPV	Econovan II		4	EU-FORD-ECONOVAN-II-BUS-01	MEDIUM	KBA/KCA四门客车外廓。	READY
7480	7480	MPV	Econovan II		4	EU-FORD-ECONOVAN-II-BUS-01	MEDIUM	KBA/KCA四门客车外廓。	READY
7481_mk2_swb_lowroof	7481	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7481_mk2_lwb_highroof	7481	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7481_mk3_swb_lowroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7481_mk3_lwb_midroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7481_mk3_xlwb_highroof	7481	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7482_mk2_swb_lowroof	7482	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	Mk2短轴低顶物理外廓。	READY
7482_mk2_lwb_highroof	7482	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	Mk2长轴高顶物理外廓。	READY
7482_mk3_swb_lowroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	MEDIUM	Mk3短轴低顶物理外廓。	READY
7482_mk3_lwb_midroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	MEDIUM	Mk3长轴中顶物理外廓。	READY
7482_mk3_xlwb_highroof	7482	Van	Ford Transit Mk3	VE6		EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	MEDIUM	Mk3加长轴高顶物理外廓。	READY
7483_swb_lowroof	7483	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴低顶物理外廓。	READY
7483_lwb_highroof	7483	Van	Ford Transit Mk2			EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴高顶物理外廓。	READY
7484	7484	Hatchback	N600 III	N600	2	EU-HONDA-N600-III-HATCHBACK-2D-01	HIGH	两门掀背外廓。	READY
7485	7485	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-HATCHBACK-3D-PREFL-01	HIGH	改款前三门掀背外廓。	READY
7486	7486	Hatchback	Civic I	SB1	3	EU-HONDA-CIVIC-I-HATCHBACK-3D-FACELIFT-01	HIGH	改款后三门掀背外廓。	READY
7487	7487	Hatchback	Galant VI	E30	5	EU-MITSUBISHI-GALANT-VI-E30-HATCHBACK-GTI4X4-01	MEDIUM	GTI 4X4五门掀背外廓。	READY
7488	7488	Hatchback	Civic IV		3	EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	HIGH	三门掀背外廓。	READY
7489	7489	Sedan	Legend I		4	EU-HONDA-LEGEND-I-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7490	7490	Coupe	Prelude III	BA4	2	EU-HONDA-PRELUDE-III-COUPE-2D-01	HIGH	第三代双门轿跑外廓。	READY
7491_swb_singlecab	7491	Pickup	Sprinter W906	906.153	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-4X4-01	MEDIUM	906.153短轴单排驾驶室底盘。	READY
7491_swb_crewcab	7491	Pickup	Sprinter W906	906.253	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-MWB-4X4-01	MEDIUM	906.253短轴双排驾驶室底盘。	READY
7491_lwb_singlecab	7491	Pickup	Sprinter W906	906.155	2	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-4X4-01	MEDIUM	906.155长轴单排驾驶室底盘。	READY
7491_lwb_crewcab	7491	Pickup	Sprinter W906	906.255	4	EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-LWB-4X4-01	MEDIUM	906.255长轴双排驾驶室底盘。	READY
7492_s1	7492	Sedan	Fiat 1100 103 S1	103	4	EU-FIAT-1100-103-S1-SEDAN-4D-01	HIGH	第一阶段四门轿车外廓。	READY
7492_s2	7492	Sedan	Fiat 1100 103 S2	103	4	EU-FIAT-1100-103-S2-SEDAN-4D-01	HIGH	第二阶段四门轿车外廓。	READY
7492_s3	7492	Sedan	Fiat 1100 103 S3	103	4	EU-FIAT-1100-103-S3-SEDAN-4D-01	HIGH	第三阶段四门轿车外廓。	READY
7493_early	7493	Sedan	Fiat 1200 103 S3	103	4	EU-FIAT-1200-103-S3-SEDAN-EARLY-01	HIGH	早期四门轿车外廓。	READY
7493_late	7493	Sedan	Fiat 1200 103 S3	103	4	EU-FIAT-1200-103-S3-SEDAN-LATE-01	HIGH	后期四门轿车外廓。	READY
7494_prefl	7494	Sedan	Fiat 1300	Type 116	4	EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	HIGH	改款前四门轿车外廓。	READY
7494_facelift	7494	Sedan	Fiat 1300	Type 116	4	EU-FIAT-1300-TYPE116-SEDAN-FACELIFT-01	HIGH	改款后四门轿车外廓。	READY
7495	7495	Sedan	Fiat 1500	Type 115	4	EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	HIGH	初期四门轿车外廓。	READY
7496	7496	Sedan	Fiat 1500 C	Type 115	4	EU-FIAT-1500C-TYPE115-SEDAN-01	HIGH	1500 C四门轿车外廓。	READY
7497	7497	Sedan	Fiat 2300	Type 114	4	EU-FIAT-2300-TYPE114-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7498	7498	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7499	7499	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7500	7500	Convertible	Spidereuropa	DS	2	EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	HIGH	DS双门敞篷外廓。	READY
7501	7501	Sedan	Fiat 125	125	4	EU-FIAT-125-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7502	7502	Sedan	Fiat 125	125	4	EU-FIAT-125-SEDAN-4D-01	HIGH	四门轿车外廓。	READY
7503	7503	Convertible	SLK R172	R172	2	EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	HIGH	双门硬顶敞篷外廓。	READY
7504	7504	Wagon	Fiat 131 S1	131	5	EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	HIGH	S1五门旅行车外廓。	READY
7505	7505	Wagon	Fiat 131 S1	131	5	EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	HIGH	S1五门旅行车外廓。	READY
7507_prefl	7507	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	生产区间跨越2011年改款，拆分改款前外廓。	READY
7507_facelift	7507	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	生产区间跨越2011年改款，拆分改款后外廓。	READY
7509	7509	Convertible	Fiat 1500 Cabriolet		2	EU-FIAT-1500-CABRIOLET-2D-01	HIGH	双门敞篷外廓。	READY
7510	7510	Convertible	Fiat 1500 Cabriolet		2	EU-FIAT-1500-CABRIOLET-2D-01	HIGH	双门敞篷外廓。	READY
7511	7511	Sedan	Fiat 500 110	110F	2	EU-FIAT-500-110-SEDAN-01	HIGH	110F两门轿车外廓。	READY
7512_early	7512	Sedan	Fiat 600	100	2	EU-FIAT-600-100-SEDAN-2D-EARLY-01	HIGH	早期短车身外廓。	READY
7512_late	7512	Sedan	Fiat 600	100	2	EU-FIAT-600-100-SEDAN-2D-LATE-01	HIGH	后期长车身外廓。	READY
7513_short	7513	Sedan	Fiat 600 D	100D	2	EU-FIAT-600-100D-SEDAN-2D-SHORT-01	MEDIUM	短车身外廓分支。	READY
7513_long	7513	Sedan	Fiat 600 D	100D	2	EU-FIAT-600-100D-SEDAN-2D-LONG-01	MEDIUM	长车身外廓分支。	READY
7514	7514	Convertible	Fiat 850 Spider	100GS	2	EU-FIAT-850-SPIDER-CONVERTIBLE-2D-01	HIGH	双门敞篷外廓。	READY
7515	7515	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7516	7516	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7517	7517	Sedan	Fiat 850	100G	2	EU-FIAT-850-SEDAN-2D-01	HIGH	Special两门轿车外廓。	READY
7518_prefl	7518	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	生产区间跨越2011年改款，拆分改款前外廓。	READY
7518_facelift	7518	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	生产区间跨越2011年改款，拆分改款后外廓。	READY
7519_prefl	7519	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	C 250 CDI 4MATIC生产边界覆盖改款前车身。	READY
7519_facelift	7519	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	C 250 CDI 4MATIC生产边界覆盖改款后车身。	READY
7520_prefl	7520	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	HIGH	C 300 CDI 4MATIC生产边界覆盖改款前车身。	READY
7520_facelift	7520	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	C 300 CDI 4MATIC生产边界覆盖改款后车身。	READY
7521	7521	Sedan	Jagst 770	100	2	EU-FIAT-JAGST-770-SEDAN-2D-01	HIGH	两门轿车外廓。	READY
7522	7522	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	225 kW C 350对应2011年改款后车身。	READY
7523_swb_prefl	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-PREFL-01	MEDIUM	短轴距改款前客车外廓。	READY
7523_swb_facelift	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-FACELIFT-01	MEDIUM	短轴距改款后客车外廓。	READY
7523_lwb_prefl	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-PREFL-01	MEDIUM	长轴距改款前客车外廓。	READY
7523_lwb_facelift	7523	MPV	MB100 W631	W631		EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-FACELIFT-01	MEDIUM	长轴距改款后客车外廓。	READY
7524_s1_3dr	7524	Hatchback	Ritmo 138A S1	138A	3	EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	MEDIUM	S1三门掀背外廓。	READY
7524_s1_5dr	7524	Hatchback	Ritmo 138A S1	138A	5	EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	MEDIUM	S1五门掀背外廓。	READY
7524_s2_3dr	7524	Hatchback	Ritmo 138A S2	138A	3	EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	MEDIUM	S2三门掀背外廓。	READY
7524_s2_5dr	7524	Hatchback	Ritmo 138A S2	138A	5	EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	MEDIUM	S2五门掀背外廓。	READY
7524_s3_3dr	7524	Hatchback	Ritmo 138A S3	138A	3	EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	MEDIUM	S3三门掀背外廓。	READY
7524_s3_5dr	7524	Hatchback	Ritmo 138A S3	138A	5	EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	MEDIUM	S3五门掀背外廓。	READY
7525	7525	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	第二阶段Turbo四门轿车外廓。	READY
7526	7526	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	HIGH	第二阶段Turbo 4X4四门轿车外廓。	READY
7527	7527	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段四门轿车外廓。	READY
7528	7528	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48五门旅行车外廓。	READY
7529_3dr_prefl	7529	Hatchback	Uno 146A	146A	3	EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBODIESEL-01	HIGH	改款前三门Turbo D外廓。	READY
7529_5dr_prefl	7529	Hatchback	Uno 146A	146A	5	EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-TURBODIESEL-01	HIGH	改款前五门Turbo D外廓。	READY
7529_3dr_facelift	7529	Hatchback	Uno 146A	146A	3	EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	HIGH	1989改款后三门外廓。	READY
7529_5dr_facelift	7529	Hatchback	Uno 146A	146A	5	EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	HIGH	1989改款后五门外廓。	READY
7530	7530	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	长轴距F系列双门Targa外廓。	READY
7531_swb	7531	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	早期短轴Targa外廓。	READY
7531_lwb	7531	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	MEDIUM	后期长轴Targa外廓。	READY
7532	7532	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	HIGH	2.2升F系列Targa外廓。	READY
7533	7533	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	MEDIUM	长轴双门轿跑外廓。	READY
7534	7534	Wagon	Renault 21	K48	5	EU-RENAULT-21-K48-WAGON-01	HIGH	K48 4X4五门旅行车外廓。	READY
7535	7535	Targa	Porsche 914	914	2	EU-PORSCHE-914-TARGA-01	HIGH	914/6双门Targa外廓。	READY
7536	7536	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	短轴Targa外廓。	READY
7537	7537	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	HIGH	短轴Targa外廓。	READY
7538	7538	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	HIGH	2.2升F系列Targa外廓。	READY
7539	7539	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	HIGH	225 kW C 350 4MATIC对应2011年改款后车身。	READY
7540_preaug72	7540	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	MEDIUM	输入2.3 S按1972年车型边界归入2.4系列改款前外廓。	READY
7540_postaug72	7540	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	MEDIUM	输入2.3 S按1972年车型边界归入2.4系列改款后外廓。	READY
7542_preaug72	7542	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款前外廓。	READY
7542_postaug72	7542	Coupe	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款后外廓。	READY
7543	7543	Sedan	5 Series F10	F10	4	EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	HIGH	M550d xDrive四门轿车外廓。	READY
7544_preaug72	7544	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款前Targa外廓。	READY
7544_postaug72	7544	Targa	911 F Series	911	2	EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	MEDIUM	输入2.3 E按1972年车型边界归入2.4系列改款后Targa外廓。	READY
7545	7545	Coupe	911 Carrera RS	911	2	EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	HIGH	Carrera RS宽体双门轿跑外廓。	READY
7546	7546	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	MEDIUM	输入版本名含Carrera RS冲突；按Targa车身边界归入宽体分支。	READY
7547	7547	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	MEDIUM	Carrera宽体双门轿跑外廓。	READY
7548	7548	Targa	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	MEDIUM	Carrera宽体双门Targa外廓。	READY
7549	7549	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	SC Carrera宽体双门轿跑外廓。	READY
7550	7550	Coupe	Porsche 924	924	3	EU-PORSCHE-924-COUPE-3D-EARLY-01	HIGH	早期924三门轿跑外廓。	READY
7551	7551	Coupe	Porsche 924	937	3	EU-PORSCHE-924-CARRERA-GT-COUPE-3D-01	HIGH	Carrera GT宽体三门轿跑外廓。	READY
7552	7552	Coupe	911 G Series	911	2	EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	HIGH	3.2 Carrera宽体双门轿跑外廓。	READY
7553	7553	Coupe	Porsche 928 S	928	3	EU-PORSCHE-928-COUPE-S310-01	MEDIUM	前期928 S三门轿跑外廓。	READY
7554	7554	Targa	911 G Series	930	2	EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	HIGH	930 Turbo宽体双门Targa外廓。	READY
7555	7555	Coupe	911 930	930	2	EU-PORSCHE-911-930-TURBO-COUPE-01	HIGH	930 Turbo宽体双门轿跑外廓。	READY
7556	7556	Coupe	Porsche 959	959	2	EU-PORSCHE-959-COUPE-2D-01	HIGH	959双门轿跑外廓。	READY
7557	7557	Coupe	911 964	964	2	EU-PORSCHE-911-964-COUPE-TURBO-01	HIGH	964 Turbo宽体双门轿跑外廓。	READY
7558	7558	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE1-01	HIGH	第一阶段四门轿车外廓。	READY
7559	7559	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段4X4四门轿车外廓。	READY
7560	7560	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7561	7561	Sedan	Renault 21	B48	4	EU-RENAULT-21-B48-SEDAN-PHASE2-01	HIGH	第二阶段4X4四门轿车外廓。	READY
7562	7562	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7563	7563	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7564	7564	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7565	7565	Van	Fiorino II	146		EU-FIAT-FIORINO-II-VAN-01	HIGH	Kasten/Großraumlimousine共用Fiorino II外廓。	READY
7566	7566	Hatchback	Renault 21	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48五门掀背外廓。	READY
7567	7567	Hatchback	Renault 21	L48	5	EU-RENAULT-21-L48-HATCHBACK-01	HIGH	L48 4X4五门掀背外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_7001-7100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MOSKVICH-2140-SEDAN-4D-01	4250	1550	1480	Auto-Data Moskvich 2140 1.5	https://www.auto-data.net/en/moskvich-2140-1.5-75hp-15860
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020	Transit Center Ford Transit Mk2 technical data	https://www.transitcenter.uk/transit-mk2-data-specification.php
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143	Transit Center Ford Transit Mk2 technical data	https://www.transitcenter.uk/transit-mk2-data-specification.php
EU-FORD-TRANSIT-VE6-SWB-LOWROOF-01	4606	1974	1974	Transit Center Ford Transit Mk3 technical data	https://www.transitcenter.uk/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-LWB-MIDROOF-01	5358	1974	2653	Transit Center Ford Transit Mk3 technical data	https://www.transitcenter.uk/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-XLWB-HIGHROOF-01	5368	1974	2653	Transit Center Ford Transit Mk3 technical data	https://www.transitcenter.uk/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-LOWROOF-01	4642	1974	2012	Transit Center Ford Transit Mk4 technical data	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-SWB-MIDROOF-01	4642	1974	2130	Transit Center Ford Transit Mk4 technical data	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-MIDROOF-01	5403	1974	2192	Transit Center Ford Transit Mk4 technical data	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FORD-TRANSIT-VE6-FACELIFT-LWB-HIGHROOF-01	5403	1974	2603	Transit Center Ford Transit Mk4 technical data	https://www.transitcenter.uk/transit-mk4-data-specification.php
EU-FIAT-TIPO-160-HATCHBACK-5D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160 1.1	https://www.auto-data.net/en/fiat-tipo-160-1.1-160.aa-56hp-7066
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	4940	1881	1416	Auto-Data Mercedes-Benz CLS C218 CLS 500	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-cls-500-v8-408hp-7g-tronic-plus-17361
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	4937	1881	1418	Auto-Data Mercedes-Benz CLS C218 facelift CLS 500	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-cls-500-v8-408hp-9g-tronic-20857
EU-FIAT-TIPO-160-HATCHBACK-3D-H1450-01	3958	1700	1450	Auto-Data Fiat Tipo 160	https://www.auto-data.net/en/fiat-tipo-160-generation-1606
EU-FORD-ECONOVAN-II-BUS-01	4030	1630	1820	Ford Australia Econovan official brochure; Drive.Place Ford Econovan II specifications	https://ia601208.us.archive.org/8/items/March1985FordEconovanBrochureAustralia/March_1985_Ford_Econovan_brochure_Australia.pdf;https://ford.drive.place/econovan/ii/group_minivan/722249
EU-HONDA-N600-III-HATCHBACK-2D-01	3100	1320	1325	Automobile-Catalog Honda N600	https://www.automobile-catalog.com/car/1970/1082015/honda_n_600.html
EU-HONDA-CIVIC-I-HATCHBACK-3D-PREFL-01	3545	1505	1330	Automobile-Catalog Honda Civic 1200 Hatchback	https://www.automobile-catalog.com/car/1973/1085975/honda_civic_1200_hatchback.html
EU-HONDA-CIVIC-I-HATCHBACK-3D-FACELIFT-01	3560	1505	1325	Automobile-Catalog Honda Civic 1200 Hatchback	https://www.automobile-catalog.com/car/1978/1086095/honda_civic_1200_hatchback.html
EU-MITSUBISHI-GALANT-VI-E30-HATCHBACK-GTI4X4-01	4530	1715	1395	Auto-Data; Tunel.az	https://www.auto-data.net/en/mitsubishi-galant-vi-hatchback-2.0-gti-16v-4x4-144hp-15392;https://tunel.az/en/catalog/mitsubishi/galant/mitsubishi-galant-vi-hatchback/833889ba-ee75-41c4-8b7f-9653a94c4394
EU-HONDA-CIVIC-IV-HATCHBACK-3D-01	3991	1686	1330	Auto-Data Honda Civic IV Hatchback 1.3	https://www.auto-data.net/en/honda-civic-iv-hatchback-1.3-75hp-12283
EU-HONDA-LEGEND-I-SEDAN-4D-01	4775	1745	1375	CarSpecsGuru Honda Legend I dimensions	https://www.carspecsguru.com/honda/legend/3842/5850/modification-41082
EU-HONDA-PRELUDE-III-COUPE-2D-01	4460	1695	1295	Auto-Data Honda Prelude III BA4	https://www.auto-data.net/en/honda-prelude-iii-ba-2.0-ex-ba4-114hp-12202
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-MWB-4X4-01	5870	1993	2435	Mercedes-Benz Sprinter Cab Chassis Technical Data; Mercedes-Benz Sprinter 2011 UK brochure	https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08;https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-MWB-4X4-01	5870	1993	2445	Mercedes-Benz Sprinter Cab Chassis Technical Data; Mercedes-Benz Sprinter 2011 UK brochure	https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08;https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-SINGLECAB-LWB-4X4-01	6845	1993	2480	Mercedes-Benz Sprinter Cab Chassis Technical Data; Mercedes-Benz Sprinter 2011 UK brochure	https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08;https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf
EU-MERCEDES-BENZ-SPRINTER-W906-CHASSIS-CREWCAB-LWB-4X4-01	6845	1993	2500	Mercedes-Benz Sprinter Cab Chassis Technical Data; Mercedes-Benz Sprinter 2011 UK brochure	https://www.scribd.com/document/872528872/A4-Sprinter-Cab-Chassis-Spec-Sheet-Jan-08;https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf
EU-FIAT-1100-103-S1-SEDAN-4D-01	3775	1458	1485	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1953/708125/fiat_1100.html
EU-FIAT-1100-103-S2-SEDAN-4D-01	3780	1458	1485	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1957/708185/fiat_1100.html
EU-FIAT-1100-103-S3-SEDAN-4D-01	3920	1458	1490	Automobile-Catalog Fiat 1100	https://www.automobile-catalog.com/car/1959/708305/fiat_1100.html
EU-FIAT-1200-103-S3-SEDAN-EARLY-01	3920	1458	1468	Automobile-Catalog Fiat 1200 Gran Luce	https://www.automobile-catalog.com/car/1959/708335/fiat_1200_gran_luce.html
EU-FIAT-1200-103-S3-SEDAN-LATE-01	3963	1458	1470	Automobile-Catalog Fiat 1200 Gran Luce	https://www.automobile-catalog.com/car/1959/708380/fiat_1200_gran_luce.html
EU-FIAT-1300-1500-TYPE116-115-SEDAN-PREFL-01	4030	1545	1420	Automobile-Catalog Fiat 1300; Automobile-Catalog Fiat 1500	https://www.automobile-catalog.com/car/1962/709460/fiat_1300.html;https://www.automobile-catalog.com/car/1962/709490/fiat_1500.html
EU-FIAT-1300-TYPE116-SEDAN-FACELIFT-01	4030	1545	1440	Automobile-Catalog Fiat 1300 Berlina	https://www.automobile-catalog.com/car/1964/709520/fiat_1300_berlina.html
EU-FIAT-1500C-TYPE115-SEDAN-01	4130	1545	1440	Automobile-Catalog Fiat 1500C Berlina	https://www.automobile-catalog.com/car/1964/709535/fiat_1500_berlina.html
EU-FIAT-2300-TYPE114-SEDAN-4D-01	4485	1620	1470	Automobile-Catalog Fiat 2300 Berlina	https://www.automobile-catalog.com/car/1963/709235/fiat_2300.html
EU-RENAULT-21-K48-WAGON-01	4693	1726	1450	Auto-Data Renault 21 Combi K48	https://www.auto-data.net/en/renault-21-combi-k48-1.7-i-75hp-10379
EU-PININFARINA-SPIDEREUROPA-DS-CONVERTIBLE-01	4107	1613	1250	Automobile-Catalog Pininfarina Spidereuropa	https://www.automobile-catalog.com/car/1984/712190/fiat_pinifarina_spidereuropa.html
EU-FIAT-125-SEDAN-4D-01	4223	1611	1440	Automobile-Catalog Fiat 125; Automobile-Catalog Fiat 125 Special	https://www.automobile-catalog.com/car/1968/710705/fiat_125.html;https://www.automobile-catalog.com/car/1968/38630/fiat_125_special.html
EU-MERCEDES-BENZ-SLK-R172-CONVERTIBLE-2D-01	4134	1810	1301	Auto-Data; Mercedes-Benz SLK250 UK press specification	https://www.auto-data.net/en/mercedes-benz-slk-r172-slk-250-204hp-18890;https://www.netcarshow.com/mercedes-benz/2012-slk250_uk-version/
EU-FIAT-131-S1-MIRAFIORI-WAGON-5D-01	4238	1632	1410	Automobile-Catalog Fiat 131 Mirafiori Familiare	https://www.automobile-catalog.com/car/1975/712355/fiat_131_mirafiori_familiare_1600.html
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-PREFL-01	4581	1770	1447	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-200-cdi-136hp-12540
EU-MERCEDES-BENZ-C-KLASSE-W204-SEDAN-FACELIFT-01	4591	1770	1447	Auto-Data	https://www.auto-data.net/en/mercedes-benz-c-class-w204-facelift-2011-c-350-blueefficiency-v6-306hp-7g-tronic-plus-17357
EU-FIAT-1500-CABRIOLET-2D-01	4085	1520	1290	Automobile-Catalog Fiat 1500 Cabriolet 1964; Automobile-Catalog Fiat 1500 Cabriolet 1965	https://www.automobile-catalog.com/car/1964/709010/fiat_1500_cabriolet_spider.html;https://www.automobile-catalog.com/car/1965/709070/fiat_1500_cabriolet_spider.html
EU-FIAT-500-110-SEDAN-01	2970	1320	1325	Auto-Data Fiat 500 Nuova	https://www.auto-data.net/en/fiat-500-nuova-0.6-18hp-7274
EU-FIAT-600-100-SEDAN-2D-EARLY-01	3215	1380	1405	Automobile-Catalog Fiat 600	https://www.automobile-catalog.com/car/1955/708545/fiat_600.html
EU-FIAT-600-100-SEDAN-2D-LATE-01	3315	1380	1405	Automobile-Catalog Fiat 600	https://www.automobile-catalog.com/car/1959/1759760/fiat_600_sunroof.html
EU-FIAT-600-100D-SEDAN-2D-SHORT-01	3295	1380	1405	Automobile-Catalog Fiat 600D	https://www.automobile-catalog.com/car/1960/708635/fiat_600d.html
EU-FIAT-600-100D-SEDAN-2D-LONG-01	3340	1380	1405	Automobile-Catalog Fiat 600D	https://www.automobile-catalog.com/car/1966/1759700/fiat_600d.html
EU-FIAT-850-SPIDER-CONVERTIBLE-2D-01	3780	1500	1220	Automobile-Catalog Fiat 850 Spider	https://www.automobile-catalog.com/car/1967/709625/fiat_850_spider.html
EU-FIAT-850-SEDAN-2D-01	3575	1425	1385	Automobile-Catalog Fiat 850 Super; Automobile-Catalog Fiat 850 Special	https://www.automobile-catalog.com/car/1968/709595/fiat_850_super.html;https://www.automobile-catalog.com/car/1969/709655/fiat_850_special.html
EU-FIAT-JAGST-770-SEDAN-2D-01	3298	1378	1405	Automobile-Catalog NSU-Fiat Jagst 770	https://www.automobile-catalog.com/car/1962/2058440/nsu-fiat_jagst_770.html
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-PREFL-01	4472	1809	2045	Drom Mercedes-Benz MB100 W631 dimensions	https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-MERCEDES-BENZ-MB100-W631-BUS-SWB-FACELIFT-01	4616	1845	2033	Drom Mercedes-Benz MB100 W631 dimensions	https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-PREFL-01	4922	1809	2035	Drom Mercedes-Benz MB100 W631 dimensions	https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-MERCEDES-BENZ-MB100-W631-BUS-LWB-FACELIFT-01	5066	1845	2033	Drom Mercedes-Benz MB100 W631 dimensions	https://www.drom.ru/catalog/lcv/mercedes-benz/mb100/specs/dimensions/
EU-FIAT-RITMO-138A-S1-HATCHBACK-3D-STD-01	3937	1650	1400	Auto-Data Fiat Ritmo I 138A	https://www.auto-data.net/en/fiat-ritmo-i-138a-generation-1612
EU-FIAT-RITMO-138A-S1-HATCHBACK-5D-STD-01	3937	1650	1400	Auto-Data Fiat Ritmo I 138A	https://www.auto-data.net/en/fiat-ritmo-i-138a-generation-1612
EU-FIAT-RITMO-138A-S2-HATCHBACK-3D-H1405-01	4014	1650	1405	Auto-Data Fiat Ritmo I 138A facelift	https://www.auto-data.net/en/fiat-ritmo-i-138a-facelift-1982-generation-1613
EU-FIAT-RITMO-138A-S2-HATCHBACK-5D-H1405-01	4014	1650	1405	Auto-Data Fiat Ritmo I 138A facelift	https://www.auto-data.net/en/fiat-ritmo-i-138a-facelift-1982-generation-1613
EU-FIAT-RITMO-138A-S3-HATCHBACK-3D-STD-01	3993	1650	1418	Auto-Data Fiat Ritmo I 138A facelift	https://www.auto-data.net/en/fiat-ritmo-i-138a-facelift-1982-generation-1613
EU-FIAT-RITMO-138A-S3-HATCHBACK-5D-H1418-01	3993	1650	1418	Auto-Data Fiat Ritmo I 138A facelift	https://www.auto-data.net/en/fiat-ritmo-i-138a-facelift-1982-generation-1613
EU-RENAULT-21-B48-TURBO-SEDAN-PHASE2-01	4510	1722	1385	Automobile-Catalog Renault 21 2.0 Turbo phase 2	https://www.automobile-catalog.com/make/renault/21/21_4d_phase_2/1991.html
EU-RENAULT-21-B48-SEDAN-PHASE2-01	4530	1730	1415	Auto-Data Renault 21 B48	https://www.auto-data.net/en/renault-21-b48-generation-2126
EU-FIAT-UNO-146A-HATCHBACK-PREFL-3D-TURBODIESEL-01	3644	1560	1420	Automobile-Catalog Fiat Uno Turbo D	https://www.automobile-catalog.com/car/1987/53465/fiat_uno_turbo_d.html
EU-FIAT-UNO-146A-HATCHBACK-PREFL-5D-TURBODIESEL-01	3644	1560	1420	Automobile-Catalog Fiat Uno Turbo D	https://www.automobile-catalog.com/car/1987/53465/fiat_uno_turbo_d.html
EU-FIAT-UNO-146A-HATCHBACK-FL1989-3D-STD-01	3689	1558	1420	Auto-Data Fiat Uno 146A facelift	https://www.auto-data.net/en/fiat-uno-model-774
EU-FIAT-UNO-146A-HATCHBACK-FL1989-5D-STD-01	3689	1558	1420	Auto-Data Fiat Uno 146A facelift	https://www.auto-data.net/en/fiat-uno-model-774
EU-PORSCHE-911-F-SERIES-2-2-TARGA-01	4163	1610	1320	Automobile-Catalog Porsche 911 2.2 Targa	https://www.automobile-catalog.com/make/porsche/911/911_2_targa/1971.html
EU-PORSCHE-911-F-SERIES-2-0-SWB-TARGA-01	4163	1610	1320	Automobile-Catalog Porsche 911 T/L/S Targa	https://www.automobile-catalog.com/car/1968/2588945/porsche_911_t_targa.html;https://www.automobile-catalog.com/car/1967/2588990/porsche_911_l_targa.html;https://www.automobile-catalog.com/car/1967/2589020/porsche_911_s_targa.html
EU-PORSCHE-911-F-SERIES-2-2-COUPE-01	4163	1610	1320	Automobile-Catalog Porsche 911 2.2 Coupe	https://www.automobile-catalog.com/make/porsche/911/911_2_coupe/1971.html
EU-PORSCHE-914-TARGA-01	3985	1650	1230	Automobile-Catalog Porsche 914	https://www.automobile-catalog.com/make/porsche/914/914/1973.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 2.4 Coupe pre-August 1972	https://www.automobile-catalog.com/car/1972/2590265/porsche_911_e_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-COUPE-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 2.4 Coupe post-August 1972	https://www.automobile-catalog.com/car/1972/2590790/porsche_911_e_coupe.html
EU-BMW-5-F10-M550D-XDRIVE-SEDAN-01	4910	1860	1454	Auto-Data BMW F10 M550d; Auto-Data BMW F10 LCI M550d	https://www.auto-data.net/en/bmw-5-series-sedan-f10-m550d-381hp-xdrive-steptronic-17754;https://www.auto-data.net/en/bmw-5-series-sedan-f10-lci-facelift-2013-m550d-381hp-xdrive-steptronic-19969
EU-PORSCHE-911-F-SERIES-2-4-TARGA-PRE-AUG72-01	4147	1610	1320	Automobile-Catalog Porsche 911 2.4 Targa pre-August 1972	https://www.automobile-catalog.com/car/1972/2590520/porsche_911_e_coupe.html
EU-PORSCHE-911-F-SERIES-2-4-TARGA-POST-AUG72-01	4127	1610	1320	Automobile-Catalog Porsche 911 2.4 Targa post-August 1972	https://www.automobile-catalog.com/make/porsche/911/911_2_targa/1973.html
EU-PORSCHE-911-F-SERIES-CARRERA-RS-COUPE-01	4102	1652	1320	Automobile-Catalog Porsche 911 Carrera RS	https://www.automobile-catalog.com/car/1972/2591255/porsche_911_carrera_rs.html
EU-PORSCHE-911-G-SERIES-TARGA-WIDE-01	4291	1652	1320	Auto-Data Porsche 911 G Series Carrera body	https://www.auto-data.net/en/porsche-911-model-724
EU-PORSCHE-911-G-SERIES-COUPE-WIDE-01	4291	1652	1320	Auto-Data Porsche 911 Coupe G 3.2 Carrera	https://www.auto-data.net/en/porsche-911-coupe-g-3.2-carrera-231hp-6652
EU-PORSCHE-924-COUPE-3D-EARLY-01	4212	1685	1270	Auto-Data Porsche 924 2.0 Turbo	https://www.auto-data.net/en/porsche-924-2.0-turbo-177hp-6697
EU-PORSCHE-924-CARRERA-GT-COUPE-3D-01	4323	1727	1270	UltimateSpecs; Carfolio	https://www.ultimatespecs.com/car-specs/Porsche/16787/Porsche-924-Carrera-GT.html;https://www.carfolio.com/porsche-924-carrera-gt-23089
EU-PORSCHE-928-COUPE-S310-01	4447	1836	1282	Auto-Data Porsche 928 4.7 S	https://www.auto-data.net/en/porsche-928-4.7-s-v8-310hp-6734
EU-PORSCHE-911-G-SERIES-TARGA-TURBO-01	4291	1775	1310	Automobile-Catalog Porsche 911 Turbo Targa	https://www.automobile-catalog.com/car/1987/2682530/porsche_911_turbo_targa.html
EU-PORSCHE-911-930-TURBO-COUPE-01	4291	1775	1310	Automobile-Catalog Porsche 911 Turbo 930	https://www.automobile-catalog.com/make/porsche/911/911_turbo_930/1987.html
EU-PORSCHE-959-COUPE-2D-01	4260	1840	1280	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/porsche-959-2.8-450hp-awd-6701;https://www.automobile-catalog.com/car/1987/57470/porsche_959.html
EU-PORSCHE-911-964-COUPE-TURBO-01	4250	1775	1310	Auto-Data Porsche 911 964 Turbo 3.3	https://www.auto-data.net/en/porsche-911-964-turbo-3.3-320hp-6624
EU-RENAULT-21-B48-SEDAN-PHASE1-01	4462	1714	1414	Automobile-Catalog Renault 21 phase 1 sedan	https://www.automobile-catalog.com/make/renault/21/21_4d_phase_1/1988.html
EU-FIAT-FIORINO-II-VAN-01	4159	1622	1904	Auto-Data Fiat Fiorino 147	https://www.auto-data.net/en/fiat-fiorino-147-1.7-diesel-57hp-6961
EU-RENAULT-21-L48-HATCHBACK-01	4460	1730	1415	Auto-Data Renault 21 Hatchback L48	https://www.auto-data.net/en/renault-21-hatchback-l48-generation-2128
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_7001-7100_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.lastvin.com/vin/GXrlL29NgwrAxwoJW "https://www.lastvin.com/vin/GXrlL29NgwrAxwoJW"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_7001-7100_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_7001-7100_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8973 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2784 行）

