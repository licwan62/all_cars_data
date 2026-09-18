# 任务：left18448 第 11001-11100 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0111__c8273e79


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 11001-11100 行

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
left18448 第 11001-11100 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-MG-ZS-HATCHBACK-FACELIFT-01	4386	1696	1386
EU-MG-ZS-HATCHBACK-PREFL-01	4377	1696	1386
EU-MG-ZS-SEDAN-FACELIFT-01	4540	1696	1390
EU-MG-ZS-SEDAN-PREFL-01	4530	1696	1390

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
MG	Zs	1.5 Hybrid+	SUV	Frontantrieb	Benzin/Elektro	Sep 2024	-	800528
MG	Zs	1.5 Vvti	SUV	Frontantrieb	Benzin	Mar 2025	-	801826
MG	Zs	2.0 TD	Stufenheck	Frontantrieb	Diesel	Jan 2004	Apr 2005	18740
MG	Zs	2.0 TD	Stufenheck	Frontantrieb	Diesel	Jan 2004	Apr 2005	18741
MG	Zs	2.0 TD	Schrägheck	Frontantrieb	Diesel	Jan 2004	Oct 2005	18748
MG	Zs	2.0 TD	Schrägheck	Frontantrieb	Diesel	Jan 2004	Oct 2005	18749
MG	Zs	EV	SUV	Frontantrieb	Elektro	Nov 2021	-	147006
MG	Zs	EV	SUV	Frontantrieb	Elektro	Nov 2021	-	147559
MG	Zt	160	Stufenheck	Frontantrieb	Benzin	Jun 2001	Jul 2005	15947
MG	Zt	180	Stufenheck	Frontantrieb	Benzin	Feb 2002	Oct 2005	18744
MG	Zt	190	Stufenheck	Frontantrieb	Benzin	Jun 2001	Jul 2005	15943
MG	Zt	260	Stufenheck	Heckantrieb	Benzin	Oct 2003	Jul 2005	18354
MG	Zt	1.8 16V	Stufenheck	Frontantrieb	Benzin	Jan 2003	Jul 2005	18742
MG	Zt	1.8 T 16V	Stufenheck	Frontantrieb	Benzin	Jan 2003	Jul 2005	18743
MG	Zt	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	Nov 2002	Jul 2005	18621
MG	Zt	2.0 Cdti	Stufenheck	Frontantrieb	Diesel	Jun 2002	Sep 2003	18836
MG	Zt- t	180	Kombi	Frontantrieb	Benzin	Feb 2002	Oct 2005	18747
MG	Zt- t	260	Kombi	Heckantrieb	Benzin	Oct 2003	Jul 2005	18355
MG	Zt- t	1.8 16V	Kombi	Frontantrieb	Benzin	Jan 2003	Jul 2005	18745
MG	Zt- t	1.8 T 16V	Kombi	Frontantrieb	Benzin	Jan 2003	Jul 2005	18746
MG	Zt- t	2.0 Cdti	Kombi	Frontantrieb	Diesel	Nov 2002	Jul 2005	18622
MG	Zt- t	2.0 Cdti	Kombi	Frontantrieb	Diesel	Jun 2002	Jul 2005	18837
M-hero	1	Erev	SUV	Allrad	Benzin/Elektro	Aug 2023	-	156107
M-hero	1	EV Allrad	SUV	Allrad	Elektro	Aug 2023	-	156106
M-hero	2	Phev Allrad	SUV	Allrad	Benzin/Elektro	Aug 2025	-	162325
MIA Electric	Mia	Electric	Kasten/Schrägheck	Heckantrieb	Elektro	Jan 2011	Apr 2014	126388
Micro	Microlino	Microlino	Coupe	Heckantrieb	Elektro	Feb 2022	-	147544
Microcar	F8	0.5	Schrägheck	Frontantrieb	Diesel	Feb 2013	-	125693
Microcar	F8	0.5	Schrägheck	Frontantrieb	Diesel	Jan 2014	-	125694
Mini	Mini	1.5 C	Kombi	Frontantrieb	Benzin/Elektro	Nov 2023	-	156334
Mini	Mini	Cooper	Coupe	Frontantrieb	Benzin	Dec 2010	Apr 2015	11693
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	Nov 2011	Apr 2015	15285
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	Jun 2001	Sep 2006	15890
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	Dec 2008	Jun 2015	16125
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Aug 2010	Oct 2016	16133
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Mar 2010	Jun 2014	17256
Mini	Mini	Cooper	Coupe	Frontantrieb	Benzin	Dec 2010	Apr 2015	17434
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	Nov 2011	Apr 2015	17492
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	Apr 2004	Jul 2008	17817
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Aug 2010	Oct 2016	34923
Mini	Mini	Cooper	Kasten/Kombi	Frontantrieb	Benzin	Dec 2012	Jun 2014	58525
Mini	Mini	Cooper	Coupe	Frontantrieb	Benzin	Apr 2012	Sep 2016	58868
Mini	Mini	Cooper	Coupe	Frontantrieb	Benzin	Apr 2012	Sep 2016	100127
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100572
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Aug 2010	Oct 2016	105656
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	Jul 2014	-	106490
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Jul 2015	Feb 2024	115115
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	Nov 2015	-	117578
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	Oct 2016	-	123350
Mini	Mini	Cooper All4	Coupe	Allrad	Benzin	Jul 2013	Sep 2016	107864
Mini	Mini	Cooper All4	Kombi	Allrad	Benzin	Nov 2012	Oct 2016	108611
Mini	Mini	Cooper All4	Coupe	Allrad	Benzin	Nov 2012	Sep 2016	108618
Mini	Mini	Cooper All4	Kombi	Allrad	Benzin	Nov 2012	Oct 2016	108624
Mini	Mini	Cooper All4	Kombi	Allrad	Benzin	Oct 2016	-	123356
Mini	Mini	Cooper C	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	157882
Mini	Mini	Cooper C	Cabriolet	Frontantrieb	Benzin	Feb 2025	-	800981
Mini	Mini	Cooper C	Schrägheck	Frontantrieb	Benzin	Jul 2024	-	801507
Mini	Mini	Cooper D	Cabriolet	Frontantrieb	Diesel	May 2009	Nov 2013	34917
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Mar 2010	Jun 2014	34919
Mini	Mini	Cooper D	Schrägheck	Frontantrieb	Diesel	Jun 2010	Nov 2013	34920
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Aug 2010	Oct 2016	34924
Mini	Mini	Cooper D	Kasten/Kombi	Frontantrieb	Diesel	Dec 2012	Jun 2014	58527
Mini	Mini	Cooper D	Coupe	Frontantrieb	Diesel	Apr 2012	Sep 2016	58873
Mini	Mini	Cooper D	Schrägheck	Frontantrieb	Diesel	Dec 2013	-	100571
Mini	Mini	Cooper D	Schrägheck	Frontantrieb	Diesel	Jul 2014	-	106480
Mini	Mini	Cooper D	Kasten/Kombi	Frontantrieb	Diesel	Dec 2012	Jun 2014	109038
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Jul 2015	Feb 2024	115117
Mini	Mini	Cooper D	Coupe	Frontantrieb	Diesel	Jul 2012	Sep 2016	115267
Mini	Mini	Cooper D	Cabriolet	Frontantrieb	Diesel	Nov 2015	-	117580
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Oct 2016	-	123362
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Oct 2016	-	123816
Mini	Mini	Cooper D	Kombi	Frontantrieb	Diesel	Dec 2014	Jul 2019	124246
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	Aug 2010	Oct 2016	34926
Mini	Mini	Cooper D All4	Coupe	Allrad	Diesel	Mar 2012	Sep 2016	53236
Mini	Mini	Cooper D All4	Coupe	Allrad	Diesel	Apr 2012	Sep 2016	58881
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	Oct 2016	-	123364
Mini	Mini	Cooper D All4	Kombi	Allrad	Diesel	Oct 2016	-	123820
Mini	Mini	Cooper E	Schrägheck	Frontantrieb	Elektro	Nov 2023	-	156379
Mini	Mini	Cooper S	Coupe	Frontantrieb	Benzin	Dec 2010	Apr 2015	11698
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	Nov 2011	Apr 2015	15286
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Mar 2002	Sep 2006	16600
Mini	Mini	Cooper S	Coupe	Frontantrieb	Benzin	Dec 2010	Apr 2015	17420
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	Jul 2004	Jul 2008	17818
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Jul 2004	Sep 2006	18307
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Aug 2010	Oct 2016	34925
Mini	Mini	Cooper S	Coupe	Frontantrieb	Benzin	Nov 2012	Oct 2016	58870
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Dec 2013	-	100573
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Jul 2014	Oct 2016	106282
Mini	Mini	Cooper S	Coupe	Frontantrieb	Benzin	Jul 2014	Sep 2016	106284
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Jul 2014	-	106497
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Nov 2014	-	115116
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	Nov 2015	-	117579
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Nov 2014	-	121964
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Oct 2016	-	123357
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Oct 2016	-	123815
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	Nov 2014	-	124237
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Sep 2013	-	124256
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	Nov 2014	-	124267
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	Oct 2007	Jun 2015	124760
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	Mar 2024	-	157883


--- Round 1 / 首次发送 ---
## 更新点

* 闭合新一代 MG ZS 汽油版与 Hybrid+ 共用外廓，并新建 `EU-MG-ZS-II-SUV-01`。官方资料给出 4430 × 1818 × 1635 mm，其中宽度为不含后视镜口径。([MG][1])
* 闭合 2021 年末改款 MG ZS EV，两个纯电 Ktype 共用新尺寸组；旧款 2004 MG ZS 三厢、掀背分别复用任务给定的既有改款尺寸组。([MG][2])
* 闭合 M-Hero 1 的 EV/EREV 共用车身、M-Hero 2 M817 车身，以及 Microlino 2.0。([MHERO][3])
* MG ZT/ZT-T 已确认存在 2004 改款前后外廓变化，但不同资料的欧洲尺寸口径尚未完全统一，本轮保留 PENDING，不创建猜测性派生行。
* Mia 输入同时包含厢式与掀背体式，无法从当前 Ktype 唯一确定短轴 Mia 或加长 Mia L/U；Microcar F8 与 F8C 的车型身份及宽度口径存在冲突，暂不建组。

## 当前批次进度

* READY Ktype：12
* PENDING Ktype：17
* 尚未处理 Ktype：71
* 本轮新增尺寸组：5
* 本轮复用既有尺寸组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800528	800528	SUV	ZS II		5	EU-MG-ZS-II-SUV-01	HIGH	同代五门SUV外廓；Hybrid+动力形式不单独拆组。	READY
801826	801826	SUV	ZS II		5	EU-MG-ZS-II-SUV-01	HIGH	同代五门SUV外廓；汽油动力形式不单独拆组。	READY
18740	18740	Sedan	ZS I		4	EU-MG-ZS-SEDAN-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款四门三厢外廓。	READY
18741	18741	Sedan	ZS I		4	EU-MG-ZS-SEDAN-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款四门三厢外廓。	READY
18748	18748	Hatchback	ZS I		5	EU-MG-ZS-HATCHBACK-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款五门掀背外廓。	READY
18749	18749	Hatchback	ZS I		5	EU-MG-ZS-HATCHBACK-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款五门掀背外廓。	READY
147006	147006	SUV	ZS I	ZS11	5	EU-MG-ZS-I-EV-SUV-FACELIFT-01	HIGH	2021年末改款纯电五门SUV外廓。	READY
147559	147559	SUV	ZS I	ZS11	5	EU-MG-ZS-I-EV-SUV-FACELIFT-01	HIGH	2021年末改款纯电五门SUV外廓。	READY
15947	15947	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18744	18744	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
15943	15943	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18354	18354	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18742	18742	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18743	18743	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18621	18621	Sedan	ZT I		4		LOW	Ktype跨2004改款，改款前后外廓分支仍待欧洲口径尺寸闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18836	18836	Sedan	ZT I		4		LOW	改款前轿车外廓已定位，但三维来源口径尚未闭合。	PENDING: 改款前轿车三维来源口径尚未闭合
18747	18747	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18355	18355	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18745	18745	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18746	18746	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18622	18622	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
18837	18837	Wagon	ZT I		5		LOW	Ktype跨2004改款，改款前后旅行车外廓分支待闭合。	PENDING: 需闭合2004改款前后尺寸并拆分物理分支
156107	156107	SUV	917	917	5	EU-M-HERO-1-917-SUV-01	HIGH	917五门SUV；EREV与EV共用车身外廓。	READY
156106	156106	SUV	917	917	5	EU-M-HERO-1-917-SUV-01	HIGH	917五门SUV；EV与EREV共用车身外廓。	READY
162325	162325	SUV	M817	M817	5	EU-M-HERO-2-M817-SUV-01	HIGH	M817五门SUV外廓。	READY
126388	126388	Hatchback/Van	Mia				LOW	输入体式同时包含厢式与掀背；短车身Mia与加长Mia L/U边界无法由Ktype唯一确认。	PENDING: Ktype覆盖的Mia车身长度分支尚未确认
147544	147544	Coupe	Microlino 2.0		1	EU-MICRO-MICROLINO-2-0-COUPE-01	HIGH	Microlino 2.0单前门车身。	READY
125693	125693	Hatchback	F8		3		LOW	F8与F8C命名及车身规格来源冲突，尚未确认不含镜宽度口径。	PENDING: F8物理车身与宽度口径尚未闭合
125694	125694	Hatchback	F8		3		LOW	F8与F8C命名及车身规格来源冲突，尚未确认不含镜宽度口径。	PENDING: F8物理车身与宽度口径尚未闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MG-ZS-II-SUV-01	4430	1818	1635	MG ZS / MG ZS Hybrid+ Owner Manual	https://www.mg.co.uk/sites/default/files/2024-11/MG-ZS-Petrol-Hybrid-Owner-Manual.pdf
EU-MG-ZS-I-EV-SUV-FACELIFT-01	4323	1809	1649	New MG ZS EV Owner Manual	https://www.mg.co.uk/sites/default/files/2021-11/New%20MG%20ZS%20EV%20Owner%20Manual.pdf
EU-M-HERO-1-917-SUV-01	4987	2080	1935	MHERO 1 Official Specifications	https://www.mhero.ch/specifications
EU-M-HERO-2-M817-SUV-01	5100	1998	1899	MHERO II Official GCC Brochure	https://mheroqatar.com/m817/documents/MHERO%20II%20Foldable%20Brochure%20-%20GCC_compressed.pdf
EU-MICRO-MICROLINO-2-0-COUPE-01	2519	1473	1501	Microlino Official Dimensions	https://microlino-car.com/en-it/was-sind-die-dimensionen-des-microlinos
```

## 下一步优先处理

1. 闭合 MG ZT 与 ZT-T 的改款前、改款后四套欧洲尺寸组，并批量拆分跨改款 Ktype。
2. 确认 Mia Ktype 对应短车身还是加长车身，以及 Microcar F8/F8C 的准确物理车身。
3. 按 MINI 车身代码聚类处理 R50/R52/R55/R56/R57/R58/R59/R60/R61、F54/F55/F56/F57/F60、J01/F65/F66/F67/U25。

推进信号：CONTINUE

[1]: https://www.mg.co.uk/sites/default/files/2024-10/MG%20ZS%20Hybrid%20Press%20Pack.pdf?utm_source=chatgpt.com "mg zs hybrid+"
[2]: https://www.mg.co.uk/sites/default/files/2021-11/New%20MG%20ZS%20EV%20Owner%20Manual.pdf?utm_source=chatgpt.com "CONTENTS"
[3]: https://www.mhero.ch/specifications?utm_source=chatgpt.com "MHERO 1 Specifications | Switzerland"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 首次闭合 MINI II 的 R58 Coupé、R59 Roadster 与 R55 Clubvan 共 5 个尺寸组，并批量完成 10 个 Ktype 映射。R58、R59 官方技术表明确列出不含外后视镜宽度；Clubvan 官方资料确认其五门结构及 3961 × 1683 × 1426 mm 外廓。([BMW Group PressClub][1])
* 同一车身下 Cooper 与 Cooper S 因保险杠外廓导致长度、高度不同，分别建立尺寸组；重复动力 Ktype 直接复用，不重复建组。

## 当前批次进度

* READY 映射：22
* PENDING 映射：17
* 尚未处理：61
* 已确认尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
11693	11693	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-01	HIGH	R58 Cooper双门轿跑外廓。	READY
15285	15285	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	HIGH	R59 Cooper双门Roadster外廓。	READY
17434	17434	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-01	HIGH	R58 Cooper双门轿跑外廓。	READY
17492	17492	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	HIGH	R59 Cooper双门Roadster外廓。	READY
58525	58525	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
58527	58527	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
109038	109038	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
11698	11698	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	HIGH	R58 Cooper S双门轿跑外廓。	READY
15286	15286	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-S-01	HIGH	R59 Cooper S双门Roadster外廓。	READY
17420	17420	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	HIGH	R58 Cooper S双门轿跑外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-MINI-II-R58-COUPE-COOPER-01	3728	1683	1378	BMW Group PressClub MINI Coupé R58 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972
EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	3734	1683	1384	BMW Group PressClub MINI Coupé R58 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972
EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	3728	1683	1384	BMW Group PressClub MINI Roadster R59 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0126223EN_GB/189923
EU-MINI-MINI-II-R59-ROADSTER-COOPER-S-01	3734	1683	1390	BMW Group PressClub MINI Roadster R59 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0126223EN_GB/189923
EU-MINI-MINI-II-R55-CLUBVAN-01	3961	1683	1426	BMW Group PressClub MINI Clubvan official release	https://www.press.bmwgroup.com/global/article/detail/T0127665EN/handle-with-care-deliver-in-style%3A-the-mini-clubvan-gets-ready-to-roll-up?language=en
```

## 下一步优先处理

1. 闭合 R50/R53 Hatchback 与 R52 Convertible，批量解决第一代 MINI Ktype。
2. 闭合 R55 Clubman、R56 Hatchback、R57 Convertible 的 Cooper、Cooper D、Cooper S 外廓分支。
3. 随后处理 R60 Countryman与 R61 Paceman，避免将输入中的 `Kombi`、`Coupe` 跨车身代码误合并。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972?utm_source=chatgpt.com "Technical Data - MINI Coupé (R58)"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* R55 Clubman Cooper、Cooper D 与现有 R55 五门外廓尺寸完全一致，直接复用既有 `EU-MINI-MINI-II-R55-CLUBVAN-01`，不重复输出尺寸组。([BMW Group PressClub][1])
* 首次闭合 R60 Countryman 的 Cooper、Cooper ALL4、Cooper D、Cooper D ALL4 共用标准外廓 `4097 × 1789 × 1561 mm`，批量完成 7 个 Ktype。([BMW Group PressClub][2])
* 首次闭合 R61 Paceman 的 Cooper、Cooper ALL4、Cooper D、Cooper D ALL4 共用标准外廓 `4109 × 1786 × 1518 mm`，批量完成 8 个 Ktype。([BMW Group PressClub][3])

## 当前批次进度

* READY 映射：39
* PENDING 映射：17
* 尚未处理：44
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
17256	17256	Wagon	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55五门Clubman物理外廓。	READY
34919	34919	Wagon	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55五门Clubman物理外廓。	READY
16133	16133	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
34923	34923	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
105656	105656	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
34924	34924	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
34926	34926	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
108611	108611	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
108624	108624	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
58868	58868	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
100127	100127	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
58873	58873	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
115267	115267	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
107864	107864	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
108618	108618	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
53236	53236	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
58881	58881	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-MINI-II-R60-COUNTRYMAN-01	4097	1789	1561	BMW Group PressClub MINI Cooper Countryman Technical Specifications; BMW Group PressClub MINI Cooper D Countryman Technical Specifications; BMW Group PressClub MINI Cooper D Countryman ALL4 Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194917; https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194921; https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194922
EU-MINI-MINI-II-R61-PACEMAN-01	4109	1786	1518	BMW Group PressClub MINI Cooper Paceman Technical Specifications; BMW Group PressClub MINI Cooper Paceman ALL4 Technical Specifications; BMW Group PressClub MINI Cooper D Paceman Technical Specifications; BMW Group PressClub MINI Cooper D Paceman ALL4 Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205398; https://www.press.bmwgroup.com/global/article/attachment/T0176406EN/260985; https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205401; https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205402
```

## 下一步优先处理

1. 闭合 R60 Countryman Cooper S 与 R61 Paceman Cooper S 的运动型保险杠外廓。
2. 闭合 R50/R53 Hatchback、R52 Convertible、R56 Hatchback、R57 Convertible。
3. 随后处理 F54/F55/F56/F57/F60 与新一代 J01/F65/F66/F67/U25。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0127583EN/194911 "Microsoft Word - TD_MINI_Cooper_Clubman+Automatik_04_2012.docx"
[2]: https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194917 "Microsoft Word - TD_MINI_Cooper_Countryman+Automatic_04_2012.docx"
[3]: https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205398 "BMW Group PressClub"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 首次闭合 MINI III 的 F55、F56 掀背车尺寸组。F55 Cooper 与 Cooper S 因保险杠外廓造成长度差异，分别建组；F56 同样区分标准版与 Cooper S。([BMW Group PressClub][1])
* 首次闭合 F54 Clubman、F57 Convertible 和 F60 Countryman 尺寸组；同一物理外廓下的汽油、柴油及 ALL4 Ktype 统一复用，不因动力形式重复建组。([BMW Group PressClub][2])
* 本轮新增完成 25 个 Ktype 映射，未重复输出既有尺寸组。

## 当前批次进度

* READY 映射：64
* PENDING 映射：17
* 尚未处理：19
* 已确认尺寸组：22
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
100572	100572	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	HIGH	F56三门掀背标准外廓。	READY
106490	106490	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	HIGH	F55五门掀背标准外廓。	READY
115115	115115	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
117578	117578	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	HIGH	F57双门敞篷标准外廓。	READY
123350	123350	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123356	123356	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
100571	100571	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	HIGH	F56三门掀背标准外廓。	READY
106480	106480	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	HIGH	F55五门掀背标准外廓。	READY
115117	115117	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
117580	117580	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	HIGH	F57双门敞篷标准外廓。	READY
123362	123362	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123816	123816	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
124246	124246	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
123364	123364	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123820	123820	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
100573	100573	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	HIGH	F56三门掀背Cooper S外廓。	READY
106497	106497	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	HIGH	F55五门掀背Cooper S外廓。	READY
115116	115116	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
117579	117579	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57双门敞篷Cooper S外廓。	READY
121964	121964	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	HIGH	F56三门掀背Cooper S外廓。	READY
123357	123357	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123815	123815	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
124237	124237	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
124256	124256	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	HIGH	F55五门掀背Cooper S外廓。	READY
124267	124267	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57双门敞篷Cooper S外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	3821	1727	1414	BMW Group PressClub MINI 3-door Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274782EN/397686
EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	3850	1727	1414	BMW Group PressClub MINI 3-door Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274782EN/397686
EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	3982	1727	1425	BMW Group PressClub MINI Cooper 5-door Technical Specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0222070CS/315002
EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	4005	1727	1425	BMW Group PressClub MINI Cooper S 5-door Technical Specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0222070CS/315004
EU-MINI-MINI-III-F54-CLUBMAN-01	4253	1800	1441	BMW Group PressClub New MINI Clubman Press Kit	https://www.press.bmwgroup.com/global/article/attachment/T0233324EN/384215
EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	3821	1727	1415	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0240023EN_GB/334337
EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	3850	1727	1415	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0240023EN_GB/334337
EU-MINI-MINI-III-F60-COUNTRYMAN-01	4299	1822	1557	BMW Group PressClub MINI Countryman Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0284421EN/414171
```

## 下一步优先处理

1. 闭合剩余 R50/R53 Hatchback、R52 Convertible、R56 Hatchback、R57 Convertible。
2. 闭合 R55/R60/R61 尚未覆盖的 Cooper S 外廓。
3. 处理新一代 J01、F65/F66/F67、U25 后，集中消除 MG ZT/ZT-T、Mia 与 Microcar 的 17 条 PENDING。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/global/article/attachment/T0274782EN/397686?utm_source=chatgpt.com "Technical specifications. MINI One First 3 door."
[2]: https://www.press.bmwgroup.com/global/article/attachment/T0233324EN/384215?utm_source=chatgpt.com "THE NEW MINI CLUBMAN. CONTENTS."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合剩余 19 个未处理 MINI Ktype，覆盖 R50/R52/R53、R56/R57、R60/R61，以及 U25、J01、F65、F66、F67；当前批次已无“尚未处理”行。旧款与新款车身均按官方技术规格中的不含后视镜车宽建组。([BMW Group PressClub][1])
* F66 Cooper C 与 Cooper S 三维完全相同，复用同一尺寸组；R60 Cooper S、R61 Cooper S、R52/R57 Cooper S 因外廓与普通 Cooper 不同，分别新建尺寸组。
* 本轮未修改既有尺寸组，也未重复输出复用组。

## 当前批次进度

* READY 映射：83
* PENDING 映射：17
* 尚未处理：0
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156334	156334	SUV	Countryman III	U25	5	EU-MINI-COUNTRYMAN-III-U25-SUV-01	HIGH	U25五门Countryman外廓。	READY
15890	15890	Hatchback	MINI I	R50	3	EU-MINI-MINI-I-R50-HATCHBACK-COOPER-01	HIGH	R50三门Cooper掀背外廓。	READY
16125	16125	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	HIGH	R57双门Cooper敞篷外廓。	READY
17817	17817	Convertible	MINI I	R52	2	EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-01	HIGH	R52双门Cooper敞篷外廓。	READY
157882	157882	Hatchback	MINI IV	F66	3	EU-MINI-MINI-IV-F66-HATCHBACK-01	HIGH	F66三门Cooper C掀背外廓。	READY
800981	800981	Convertible	MINI IV	F67	2	EU-MINI-MINI-IV-F67-CONVERTIBLE-01	HIGH	F67双门Cooper C敞篷外廓。	READY
801507	801507	Hatchback	MINI IV	F65	5	EU-MINI-MINI-IV-F65-HATCHBACK-01	HIGH	F65五门Cooper C掀背外廓。	READY
34917	34917	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	HIGH	R57双门Cooper D敞篷外廓。	READY
34920	34920	Hatchback	MINI II	R56	3	EU-MINI-MINI-II-R56-HATCHBACK-COOPER-01	HIGH	R56三门Cooper D掀背标准外廓。	READY
156379	156379	Hatchback	MINI V	J01	3	EU-MINI-MINI-V-J01-HATCHBACK-ELECTRIC-01	HIGH	J01三门纯电Cooper E外廓。	READY
16600	16600	Hatchback	MINI I	R53	3	EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	HIGH	R53三门Cooper S掀背外廓。	READY
17818	17818	Convertible	MINI I	R52	2	EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-S-01	HIGH	R52双门Cooper S敞篷外廓。	READY
18307	18307	Hatchback	MINI I	R53	3	EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	HIGH	R53三门Cooper S掀背外廓。	READY
34925	34925	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	HIGH	R60五门Cooper S Countryman外廓。	READY
58870	58870	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	HIGH	R61三门Cooper S Paceman外廓。	READY
106282	106282	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	HIGH	R60五门Cooper S Countryman外廓。	READY
106284	106284	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	HIGH	R61三门Cooper S Paceman外廓。	READY
124760	124760	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-S-01	HIGH	R57双门Cooper S敞篷外廓。	READY
157883	157883	Hatchback	MINI IV	F66	3	EU-MINI-MINI-IV-F66-HATCHBACK-01	HIGH	F66三门Cooper S掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MINI-COUNTRYMAN-III-U25-SUV-01	4444	1843	1661	BMW Group PressClub MINI Countryman C Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448204EN/628460
EU-MINI-MINI-I-R50-HATCHBACK-COOPER-01	3626	1688	1408	BMW Group PressClub MINI Cooper Technical Specifications	https://www.press.bmwgroup.com/china/article/attachment/T0018639ZH_CN/36667
EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	3699	1683	1414	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0031660EN/52392
EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-01	3635	1688	1415	BMW Group PressClub MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0019795EN_GB/38339
EU-MINI-MINI-IV-F66-HATCHBACK-01	3876	1744	1432	BMW Group PressClub MINI Cooper C Technical Specifications; BMW Group PressClub MINI Cooper S Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448167EN/628275;https://www.press.bmwgroup.com/global/article/attachment/T0448167EN/628274
EU-MINI-MINI-IV-F67-CONVERTIBLE-01	3879	1744	1431	BMW Group PressClub New MINI Cooper Convertible	https://www.press.bmwgroup.com/global/article/detail/T0445367EN/always-open%3A-unmistakable-driving-fun-in-the-new-mini-cooper-convertible?language=en
EU-MINI-MINI-IV-F65-HATCHBACK-01	4036	1744	1464	BMW Group PressClub New MINI Cooper 5 Door	https://www.press.bmwgroup.com/global/article/detail/T0442899EN/the-new-mini-cooper-5-door?language=en
EU-MINI-MINI-II-R56-HATCHBACK-COOPER-01	3699	1683	1407	MINI Canada MY2009 R56 Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0036807EN/56874
EU-MINI-MINI-V-J01-HATCHBACK-ELECTRIC-01	3858	1756	1460	BMW Group PressClub MINI Cooper E Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448246EN/628481
EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	3655	1688	1416	BMW Group PressClub MINI Cooper S Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0034246EN/54164
EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-S-01	3655	1688	1415	BMW Group PressClub MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0019795EN_GB/38339
EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	4110	1789	1561	BMW Group PressClub MINI Cooper S Countryman Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082531IT/126085
EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	4114	1786	1518	BMW Group PressClub New MINI Paceman	https://www.press.bmwgroup.com/global/article/detail/T0178003EN/the-new-mini-paceman?language=en
EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0031660EN/52392
```

## 下一步优先处理

1. 集中闭合 MG ZT 与 ZT-T 的改款前、改款后轿车和旅行车外廓，拆分跨改款 Ktype。
2. 闭合 Mia 短车身与 Mia L/U 边界。
3. 闭合 Microcar F8/F8C 车型身份及不含后视镜宽度，消除剩余 17 条 PENDING。

推进信号：CONTINUE

[1]: https://www.press.bmwgroup.com/china/article/attachment/T0018639ZH_CN/36667?utm_source=chatgpt.com "INHALTSVERZEICHNIS"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_11001-11100_ktype_dimension_mapping_final.tsv
- left18448_11001-11100_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 剩余 17 条 `PENDING` 已清零：MG ZT/ZT-T 按改款前后及 V8 特殊外廓拆分；Mia 按短轴乘用、长轴乘用和长轴厢式拆分；Microcar F8 闭合为 F8C 车身。
* 已完成机械检查：100 个输入 Ktype 全部覆盖；115 条映射全部为 `READY`；45 个尺寸组全部被引用，无缺失引用或孤立尺寸组。
* 两张最终 TSV 的固定表头、主键唯一性、引用闭合、三维正整数及来源完整性均已检查。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：115
* PENDING 映射：0
* DIMENSION_GROUP：45
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
800528	800528	SUV	ZS II		5	EU-MG-ZS-II-SUV-01	HIGH	同代五门SUV外廓；Hybrid+动力形式不单独拆组。	READY
801826	801826	SUV	ZS II		5	EU-MG-ZS-II-SUV-01	HIGH	同代五门SUV外廓；汽油动力形式不单独拆组。	READY
18740	18740	Sedan	ZS I		4	EU-MG-ZS-SEDAN-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款四门三厢外廓。	READY
18741	18741	Sedan	ZS I		4	EU-MG-ZS-SEDAN-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款四门三厢外廓。	READY
18748	18748	Hatchback	ZS I		5	EU-MG-ZS-HATCHBACK-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款五门掀背外廓。	READY
18749	18749	Hatchback	ZS I		5	EU-MG-ZS-HATCHBACK-FACELIFT-01	MEDIUM	输入生产阶段对应2004改款五门掀背外廓。	READY
147006	147006	SUV	ZS I	ZS11	5	EU-MG-ZS-I-EV-SUV-FACELIFT-01	HIGH	2021年末改款纯电五门SUV外廓。	READY
147559	147559	SUV	ZS I	ZS11	5	EU-MG-ZS-I-EV-SUV-FACELIFT-01	HIGH	2021年末改款纯电五门SUV外廓。	READY
15947_prefl	15947	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
15947_facelift	15947	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
18744_prefl	18744	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
18744_facelift	18744	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
15943_prefl	15943	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
15943_facelift	15943	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
18354_prefl	18354	Sedan	ZT I	X12	4	EU-MG-ZT-I-SEDAN-PREFL-V8-01	HIGH	X12后驱V8四门轿车改款前外廓。	READY
18354_facelift	18354	Sedan	ZT I	X12	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X12后驱V8四门轿车2004改款外廓。	READY
18742_prefl	18742	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
18742_facelift	18742	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
18743_prefl	18743	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
18743_facelift	18743	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
18621_prefl	18621	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	X10四门轿车改款前外廓。	READY
18621_facelift	18621	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-FACELIFT-01	HIGH	X10四门轿车2004改款外廓。	READY
18836	18836	Sedan	ZT I	X10	4	EU-MG-ZT-I-SEDAN-PREFL-01	HIGH	生产区间仅覆盖改款前X10四门轿车。	READY
18747_prefl	18747	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-PREFL-01	HIGH	X11五门旅行车改款前外廓。	READY
18747_facelift	18747	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X11五门旅行车2004改款外廓。	READY
18355_prefl	18355	Wagon	ZT I	X13	5	EU-MG-ZT-T-I-WAGON-PREFL-V8-01	HIGH	X13后驱V8五门旅行车改款前外廓。	READY
18355_facelift	18355	Wagon	ZT I	X13	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X13后驱V8五门旅行车2004改款外廓。	READY
18745_prefl	18745	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-PREFL-01	HIGH	X11五门旅行车改款前外廓。	READY
18745_facelift	18745	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X11五门旅行车2004改款外廓。	READY
18746_prefl	18746	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-PREFL-01	HIGH	X11五门旅行车改款前外廓。	READY
18746_facelift	18746	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X11五门旅行车2004改款外廓。	READY
18622_prefl	18622	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-PREFL-01	HIGH	X11五门旅行车改款前外廓。	READY
18622_facelift	18622	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X11五门旅行车2004改款外廓。	READY
18837_prefl	18837	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-PREFL-01	HIGH	X11五门旅行车改款前外廓。	READY
18837_facelift	18837	Wagon	ZT I	X11	5	EU-MG-ZT-T-I-WAGON-FACELIFT-01	HIGH	X11五门旅行车2004改款外廓。	READY
156107	156107	SUV	917	917	5	EU-M-HERO-1-917-SUV-01	HIGH	917五门SUV；EREV与EV共用车身外廓。	READY
156106	156106	SUV	917	917	5	EU-M-HERO-1-917-SUV-01	HIGH	917五门SUV；EV与EREV共用车身外廓。	READY
162325	162325	SUV	M817	M817	5	EU-M-HERO-2-M817-SUV-01	HIGH	M817五门SUV外廓。	READY
126388_swb_hatch	126388	Hatchback	Mia			EU-MIA-ELECTRIC-MIA-HATCHBACK-SWB-01	MEDIUM	短轴三座Mia乘用车外廓。	READY
126388_lwb_hatch	126388	Hatchback	Mia L			EU-MIA-ELECTRIC-MIA-LWB-01	MEDIUM	长轴四座Mia L乘用车外廓。	READY
126388_lwb_van	126388	Van	Mia U			EU-MIA-ELECTRIC-MIA-LWB-01	MEDIUM	长轴Mia U厢式车外廓；与Mia L三维相同。	READY
147544	147544	Coupe	Microlino 2.0		1	EU-MICRO-MICROLINO-2-0-COUPE-01	HIGH	Microlino 2.0单前门车身。	READY
125693	125693	Coupe	F8C		3	EU-MICROCAR-F8C-I-COUPE-01	MEDIUM	输入F8对应F8C三门微型轿跑车身。	READY
125694	125694	Coupe	F8C		3	EU-MICROCAR-F8C-I-COUPE-01	MEDIUM	输入F8对应F8C三门微型轿跑车身。	READY
156334	156334	SUV	Countryman III	U25	5	EU-MINI-COUNTRYMAN-III-U25-SUV-01	HIGH	U25五门Countryman外廓。	READY
11693	11693	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-01	HIGH	R58 Cooper双门轿跑外廓。	READY
15285	15285	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	HIGH	R59 Cooper双门Roadster外廓。	READY
15890	15890	Hatchback	MINI I	R50	3	EU-MINI-MINI-I-R50-HATCHBACK-COOPER-01	HIGH	R50三门Cooper掀背外廓。	READY
16125	16125	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	HIGH	R57双门Cooper敞篷外廓。	READY
16133	16133	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
17256	17256	Wagon	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55五门Clubman物理外廓。	READY
17434	17434	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-01	HIGH	R58 Cooper双门轿跑外廓。	READY
17492	17492	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	HIGH	R59 Cooper双门Roadster外廓。	READY
17817	17817	Convertible	MINI I	R52	2	EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-01	HIGH	R52双门Cooper敞篷外廓。	READY
34923	34923	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
58525	58525	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
58868	58868	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
100127	100127	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
100572	100572	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	HIGH	F56三门掀背标准外廓。	READY
105656	105656	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
106490	106490	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	HIGH	F55五门掀背标准外廓。	READY
115115	115115	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
117578	117578	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	HIGH	F57双门敞篷标准外廓。	READY
123350	123350	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
107864	107864	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
108611	108611	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
108618	108618	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
108624	108624	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
123356	123356	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
157882	157882	Hatchback	MINI IV	F66	3	EU-MINI-MINI-IV-F66-HATCHBACK-01	HIGH	F66三门Cooper C掀背外廓。	READY
800981	800981	Convertible	MINI IV	F67	2	EU-MINI-MINI-IV-F67-CONVERTIBLE-01	HIGH	F67双门Cooper C敞篷外廓。	READY
801507	801507	Hatchback	MINI IV	F65	5	EU-MINI-MINI-IV-F65-HATCHBACK-01	HIGH	F65五门Cooper C掀背外廓。	READY
34917	34917	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	HIGH	R57双门Cooper D敞篷外廓。	READY
34919	34919	Wagon	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55五门Clubman物理外廓。	READY
34920	34920	Hatchback	MINI II	R56	3	EU-MINI-MINI-II-R56-HATCHBACK-COOPER-01	HIGH	R56三门Cooper D掀背标准外廓。	READY
34924	34924	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
58527	58527	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
58873	58873	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
100571	100571	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	HIGH	F56三门掀背标准外廓。	READY
106480	106480	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	HIGH	F55五门掀背标准外廓。	READY
109038	109038	Van	MINI II	R55	5	EU-MINI-MINI-II-R55-CLUBVAN-01	HIGH	R55 Clubvan五门厢式外廓。	READY
115117	115117	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
115267	115267	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
117580	117580	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	HIGH	F57双门敞篷标准外廓。	READY
123362	123362	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123816	123816	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
124246	124246	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
34926	34926	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-01	HIGH	R60五门Countryman标准外廓。	READY
53236	53236	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
58881	58881	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-01	HIGH	R61三门Paceman标准外廓。	READY
123364	123364	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123820	123820	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
156379	156379	Hatchback	MINI V	J01	3	EU-MINI-MINI-V-J01-HATCHBACK-ELECTRIC-01	HIGH	J01三门纯电Cooper E外廓。	READY
11698	11698	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	HIGH	R58 Cooper S双门轿跑外廓。	READY
15286	15286	Convertible	MINI II	R59	2	EU-MINI-MINI-II-R59-ROADSTER-COOPER-S-01	HIGH	R59 Cooper S双门Roadster外廓。	READY
16600	16600	Hatchback	MINI I	R53	3	EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	HIGH	R53三门Cooper S掀背外廓。	READY
17420	17420	Coupe	MINI II	R58	2	EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	HIGH	R58 Cooper S双门轿跑外廓。	READY
17818	17818	Convertible	MINI I	R52	2	EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-S-01	HIGH	R52双门Cooper S敞篷外廓。	READY
18307	18307	Hatchback	MINI I	R53	3	EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	HIGH	R53三门Cooper S掀背外廓。	READY
34925	34925	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	HIGH	R60五门Cooper S Countryman外廓。	READY
58870	58870	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	HIGH	R61三门Cooper S Paceman外廓。	READY
100573	100573	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	HIGH	F56三门掀背Cooper S外廓。	READY
106282	106282	SUV	MINI II	R60	5	EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	HIGH	R60五门Cooper S Countryman外廓。	READY
106284	106284	Coupe	MINI II	R61	3	EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	HIGH	R61三门Cooper S Paceman外廓。	READY
106497	106497	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	HIGH	F55五门掀背Cooper S外廓。	READY
115116	115116	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
117579	117579	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57双门敞篷Cooper S外廓。	READY
121964	121964	Hatchback	MINI III	F56	3	EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	HIGH	F56三门掀背Cooper S外廓。	READY
123357	123357	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
123815	123815	SUV	MINI III	F60	5	EU-MINI-MINI-III-F60-COUNTRYMAN-01	HIGH	F60五门Countryman外廓。	READY
124237	124237	Wagon	MINI III	F54	5	EU-MINI-MINI-III-F54-CLUBMAN-01	HIGH	F54五门Clubman外廓。	READY
124256	124256	Hatchback	MINI III	F55	5	EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	HIGH	F55五门掀背Cooper S外廓。	READY
124267	124267	Convertible	MINI III	F57	2	EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57双门敞篷Cooper S外廓。	READY
124760	124760	Convertible	MINI II	R57	2	EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-S-01	HIGH	R57双门Cooper S敞篷外廓。	READY
157883	157883	Hatchback	MINI IV	F66	3	EU-MINI-MINI-IV-F66-HATCHBACK-01	HIGH	F66三门Cooper S掀背外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_11001-11100_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MG-ZS-II-SUV-01	4430	1818	1635	MG ZS / MG ZS Hybrid+ Owner Manual	https://www.mg.co.uk/sites/default/files/2024-11/MG-ZS-Petrol-Hybrid-Owner-Manual.pdf
EU-MG-ZS-SEDAN-FACELIFT-01	4540	1696	1390	Automobile-Catalog 2004 MG ZS 110 Saloon specifications	https://www.automobile-catalog.com/car/2004/1703165/mg_zs_110_saloon.html
EU-MG-ZS-HATCHBACK-FACELIFT-01	4386	1696	1386	Automobile-Catalog 2004 MG ZS TD 5-Door specifications	https://www.automobile-catalog.com/car/2004/1703135/mg_zs_td_hatchback.html
EU-MG-ZS-I-EV-SUV-FACELIFT-01	4323	1809	1649	New MG ZS EV Owner Manual	https://www.mg.co.uk/sites/default/files/2021-11/New%20MG%20ZS%20EV%20Owner%20Manual.pdf
EU-MG-ZT-I-SEDAN-PREFL-01	4740	1780	1410	MG Rover MG ZT/ZT-T official brochure April 2002	https://roverownersclub.com.au/wp-content/uploads/2016/05/MG-ZT-Brochure-MGRA-MGZT-4-02-April-2002-PDF.pdf
EU-MG-ZT-I-SEDAN-FACELIFT-01	4744	1778	1417	Automobile-Catalog 2004 MG ZT CDTi facelift specifications	https://www.automobile-catalog.com/car/2004/1703585/mg_zt_cdti.html
EU-MG-ZT-I-SEDAN-PREFL-V8-01	4747	1778	1417	Automobile-Catalog 2004 MG ZT 260 V8 pre-facelift specifications	https://www.automobile-catalog.com/car/2004/1703825/mg_zt_260_v8.html
EU-MG-ZT-T-I-WAGON-PREFL-01	4792	1780	1430	MG Rover MG ZT/ZT-T official brochure April 2002	https://roverownersclub.com.au/wp-content/uploads/2016/05/MG-ZT-Brochure-MGRA-MGZT-4-02-April-2002-PDF.pdf
EU-MG-ZT-T-I-WAGON-FACELIFT-01	4786	1778	1428	Automobile-Catalog 2004 MG ZT-T CDTi Sports Auto facelift specifications	https://www.automobile-catalog.com/car/2004/1703720/mg_zt-t_cdti_sports_auto.html
EU-MG-ZT-T-I-WAGON-PREFL-V8-01	4792	1778	1428	Automobile-Catalog 2004 MG ZT-T 260 V8 pre-facelift specifications	https://www.automobile-catalog.com/car/2004/1703840/mg_zt-t_260_v8.html
EU-M-HERO-1-917-SUV-01	4987	2080	1935	MHERO 1 Official Specifications	https://www.mhero.ch/specifications
EU-M-HERO-2-M817-SUV-01	5100	1998	1899	MHERO II Official GCC Brochure	https://mheroqatar.com/m817/documents/MHERO%20II%20Foldable%20Brochure%20-%20GCC_compressed.pdf
EU-MIA-ELECTRIC-MIA-HATCHBACK-SWB-01	2870	1640	1550	mia electric official range brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-MIA-ELECTRIC-MIA-LWB-01	3190	1640	1550	mia electric official range brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-MICRO-MICROLINO-2-0-COUPE-01	2519	1473	1501	Microlino Official Dimensions	https://microlino-car.com/en-it/was-sind-die-dimensionen-des-microlinos
EU-MICROCAR-F8C-I-COUPE-01	3000	1500	1455	Microcar F8C official owner manual; Swedish vehicle registration record RMX565	https://www.caen-sud.com/wp-content/uploads/2022/08/MICROCAR-F8C-FR-ES-IT.pdf;https://www.fordonskollen.se/fordon/RMX565
EU-MINI-COUNTRYMAN-III-U25-SUV-01	4444	1843	1661	BMW Group PressClub MINI Countryman C Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448204EN/628460
EU-MINI-MINI-II-R58-COUPE-COOPER-01	3728	1683	1378	BMW Group PressClub MINI Coupé R58 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972
EU-MINI-MINI-II-R59-ROADSTER-COOPER-01	3728	1683	1384	BMW Group PressClub MINI Roadster R59 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0126223EN_GB/189923
EU-MINI-MINI-I-R50-HATCHBACK-COOPER-01	3626	1688	1408	BMW Group PressClub MINI Cooper Technical Specifications	https://www.press.bmwgroup.com/china/article/attachment/T0018639ZH_CN/36667
EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-01	3699	1683	1414	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0031660EN/52392
EU-MINI-MINI-II-R60-COUNTRYMAN-01	4097	1789	1561	BMW Group PressClub MINI Cooper Countryman Technical Specifications; BMW Group PressClub MINI Cooper D Countryman Technical Specifications; BMW Group PressClub MINI Cooper D Countryman ALL4 Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194917;https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194921;https://www.press.bmwgroup.com/global/article/attachment/T0127716EN/194922
EU-MINI-MINI-II-R55-CLUBVAN-01	3961	1683	1426	BMW Group PressClub MINI Clubvan official release	https://www.press.bmwgroup.com/global/article/detail/T0127665EN/handle-with-care-deliver-in-style%3A-the-mini-clubvan-gets-ready-to-roll-up?language=en
EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-01	3635	1688	1415	BMW Group PressClub MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0019795EN_GB/38339
EU-MINI-MINI-II-R61-PACEMAN-01	4109	1786	1518	BMW Group PressClub MINI Cooper Paceman Technical Specifications; BMW Group PressClub MINI Cooper Paceman ALL4 Technical Specifications; BMW Group PressClub MINI Cooper D Paceman Technical Specifications; BMW Group PressClub MINI Cooper D Paceman ALL4 Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205398;https://www.press.bmwgroup.com/global/article/attachment/T0176406EN/260985;https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205401;https://www.press.bmwgroup.com/global/article/attachment/T0135503EN/205402
EU-MINI-MINI-III-F56-HATCHBACK-COOPER-01	3821	1727	1414	BMW Group PressClub MINI 3-door Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274782EN/397686
EU-MINI-MINI-III-F55-HATCHBACK-COOPER-01	3982	1727	1425	BMW Group PressClub MINI Cooper 5-door Technical Specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0222070CS/315002
EU-MINI-MINI-III-F54-CLUBMAN-01	4253	1800	1441	BMW Group PressClub New MINI Clubman Press Kit	https://www.press.bmwgroup.com/global/article/attachment/T0233324EN/384215
EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-01	3821	1727	1415	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0240023EN_GB/334337
EU-MINI-MINI-III-F60-COUNTRYMAN-01	4299	1822	1557	BMW Group PressClub MINI Countryman Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0284421EN/414171
EU-MINI-MINI-IV-F66-HATCHBACK-01	3876	1744	1432	BMW Group PressClub MINI Cooper C Technical Specifications; BMW Group PressClub MINI Cooper S Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448167EN/628275;https://www.press.bmwgroup.com/global/article/attachment/T0448167EN/628274
EU-MINI-MINI-IV-F67-CONVERTIBLE-01	3879	1744	1431	BMW Group PressClub New MINI Cooper Convertible	https://www.press.bmwgroup.com/global/article/detail/T0445367EN/always-open%3A-unmistakable-driving-fun-in-the-new-mini-cooper-convertible?language=en
EU-MINI-MINI-IV-F65-HATCHBACK-01	4036	1744	1464	BMW Group PressClub New MINI Cooper 5 Door	https://www.press.bmwgroup.com/global/article/detail/T0442899EN/the-new-mini-cooper-5-door?language=en
EU-MINI-MINI-II-R56-HATCHBACK-COOPER-01	3699	1683	1407	MINI Canada MY2009 R56 Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0036807EN/56874
EU-MINI-MINI-V-J01-HATCHBACK-ELECTRIC-01	3858	1756	1460	BMW Group PressClub MINI Cooper E Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0448246EN/628481
EU-MINI-MINI-II-R58-COUPE-COOPER-S-01	3734	1683	1384	BMW Group PressClub MINI Coupé R58 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0121814EN_GB/177972
EU-MINI-MINI-II-R59-ROADSTER-COOPER-S-01	3734	1683	1390	BMW Group PressClub MINI Roadster R59 Technical Data	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0126223EN_GB/189923
EU-MINI-MINI-I-R53-HATCHBACK-COOPER-S-01	3655	1688	1416	BMW Group PressClub MINI Cooper S Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0034246EN/54164
EU-MINI-MINI-I-R52-CONVERTIBLE-COOPER-S-01	3655	1688	1415	BMW Group PressClub MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0019795EN_GB/38339
EU-MINI-MINI-II-R60-COUNTRYMAN-COOPER-S-01	4110	1789	1561	BMW Group PressClub MINI Cooper S Countryman Technical Specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0082531IT/126085
EU-MINI-MINI-II-R61-PACEMAN-COOPER-S-01	4114	1786	1518	BMW Group PressClub New MINI Paceman	https://www.press.bmwgroup.com/global/article/detail/T0178003EN/the-new-mini-paceman?language=en
EU-MINI-MINI-III-F56-HATCHBACK-COOPER-S-01	3850	1727	1414	BMW Group PressClub MINI 3-door Technical Specifications	https://www.press.bmwgroup.com/global/article/attachment/T0274782EN/397686
EU-MINI-MINI-III-F55-HATCHBACK-COOPER-S-01	4005	1727	1425	BMW Group PressClub MINI Cooper S 5-door Technical Specifications	https://www.press.bmwgroup.com/czech/article/attachment/T0222070CS/315004
EU-MINI-MINI-III-F57-CONVERTIBLE-COOPER-S-01	3850	1727	1415	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/united-kingdom/article/attachment/T0240023EN_GB/334337
EU-MINI-MINI-II-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414	BMW Group PressClub New MINI Convertible Technical Specifications	https://www.press.bmwgroup.com/canada/article/attachment/T0031660EN/52392
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_11001-11100_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1878 行）
- 累计尺寸组：dimension_groups_final.tsv（529 行）

