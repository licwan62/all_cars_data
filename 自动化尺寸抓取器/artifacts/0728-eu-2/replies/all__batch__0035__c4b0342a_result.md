# 任务：all 第 3401-3500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0035__c4b0342a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3401-3500 行

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
all 第 3401-3500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-159-939-SPORTWAGON-WAGON-01	4660	1828	1417
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422
EU-ALFA-ROMEO-159-Q4-SEDAN-4D-01	4660	1828	1452
EU-ALFA-ROMEO-159-Q4-SPORTWAGON-WAGON-5D-01	4660	1828	1452
EU-ALFA-ROMEO-159-SEDAN-01	4660	1828	1422
EU-ALFA-ROMEO-159-SEDAN-02	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-01	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-16IN-01	4660	1828	1417
EU-ALFA-ROMEO-159-SPORTWAGON-WAGON-17IN-01	4660	1828	1422
EU-ASTON-MARTIN-VANQUISH-I-COUPE-01	4665	1923	1318
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421
EU-BMW-1-SERIES-E82-COUPE-2D-01	4360	1748	1423
EU-BMW-1-SERIES-E88-CONVERTIBLE-2D-01	4360	1748	1411
EU-CADILLAC-CTS-II-SEDAN-4D-01	4866	1842	1472
EU-CHRYSLER-SEBRING-I-COUPE-01	4760	1770	1296
EU-CHRYSLER-SEBRING-III-JS-CONVERTIBLE-2D-01	4922	1816	1485
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4842	1808	1498
EU-CHRYSLER-SEBRING-JR-SEDAN-4D-01	4843	1793	1394
EU-FIAT-DUCATO-I-280-VAN-L1H1-01	4760	1965	2100
EU-FIAT-DUCATO-I-280-VAN-L1H2-01	4760	1965	2419
EU-FIAT-DUCATO-I-280-VAN-L2H2-01	5495	1965	2450
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
EU-FIAT-DUCATO-II-X230-BUS-LWB-STANDARD-01	5005	1998	2150
EU-FIAT-DUCATO-II-X230-BUS-SWB-PANORAMA-01	4655	1998	2104
EU-FIAT-DUCATO-II-X230-VAN-SWB-LOWROOF-01	4655	1998	2150
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
EU-FIAT-SIENA-ALBEA-I-SEDAN-01	4186	1703	1489
EU-FORD-FOCUS-II-CONVERTIBLE-01	4509	1834	1448
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497
EU-FORD-FOCUS-II-ST-HATCHBACK-3D-01	4362	1840	1447
EU-FORD-FOCUS-II-ST-HATCHBACK-5D-01	4362	1840	1447
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501
EU-FORD-TRANSIT-CONNECT-I-VAN-LWB-HIGHROOF-01	4525	1795	1982
EU-FORD-TRANSIT-CONNECT-I-VAN-SWB-LOWROOF-01	4278	1795	1824
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-HIGHROOF-01	5651	1974	2524
EU-FORD-TRANSIT-MK6-VAN-FWD-LWB-MEDROOF-01	5651	1974	2303
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-HIGHROOF-01	5201	1974	2529
EU-FORD-TRANSIT-MK6-VAN-FWD-MWB-MEDROOF-01	5201	1974	2309
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-LOWROOF-01	4834	1974	1974
EU-FORD-TRANSIT-MK6-VAN-FWD-SWB-MEDROOF-01	4834	1974	2313
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-01	6403	2008	2380
EU-FORD-TRANSIT-MK7-BUS-JUMBO-RWD-DRW-MEDROOF-02	6474	2084	2380
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	6390	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	6002	1974	2031
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	5552	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	6390	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	6002	1974	2025
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	5552	1974	2030
EU-FORD-TRANSIT-MK7-MINIBUS-LWB-MEDROOF-AWD-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-15SEAT-LWB-MEDROOF-01	5680	1974	2393
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-HIGHROOF-01	6403	2084	2624
EU-FORD-TRANSIT-MK7-MPV-MINIBUS-17SEAT-JUMBO-MEDROOF-01	6403	2084	2380
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-DRW-HIGHROOF-01	6403	2008	2624
EU-FORD-TRANSIT-MK7-VAN-JUMBO-RWD-SRW-HIGHROOF-01	6403	1974	2624
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-HIGHROOF-01	5680	1974	2590
EU-FORD-TRANSIT-MK7-VAN-LWB-FWD-MEDROOF-01	5680	1974	2381
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-HIGHROOF-01	5680	1974	2606
EU-FORD-TRANSIT-MK7-VAN-LWB-RWD-MEDROOF-01	5680	1974	2394
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-HIGHROOF-01	5230	1974	2594
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-LOWROOF-01	5230	1974	2047
EU-FORD-TRANSIT-MK7-VAN-MWB-FWD-MEDROOF-01	5230	1974	2363
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-HIGHROOF-01	5230	1974	2611
EU-FORD-TRANSIT-MK7-VAN-MWB-RWD-MEDROOF-01	5230	1974	2397
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-01	6403	2084	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-DRW-02	6474	2084	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-01	6403	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-JUMBO-HIGHROOF-SRW-02	6474	1974	2629
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-01	5680	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-HIGHROOF-02	5751	1974	2619
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-01	5680	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-LWB-MEDROOF-02	5751	1974	2403
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-HIGHROOF-01	5230	1974	2620
EU-FORD-TRANSIT-MK7-VAN-RWD-MWB-MEDROOF-01	5230	1974	2390
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-LOWROOF-01	4863	1974	2089
EU-FORD-TRANSIT-MK7-VAN-RWD-SWB-MEDROOF-01	4863	1974	2405
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-LOWROOF-01	4863	1974	2070
EU-FORD-TRANSIT-MK7-VAN-SWB-FWD-MEDROOF-01	4863	1974	2385
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-LOWROOF-01	4863	1974	2083
EU-FORD-TRANSIT-MK7-VAN-SWB-RWD-MEDROOF-01	4863	1974	2398
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679
EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-01	5035	1800	1735
EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	5035	1800	1735
EU-ISUZU-D-MAX-I-PICKUP-DOUBLECAB-4X4-01	5035	1800	1735
EU-ISUZU-D-MAX-I-PICKUP-SINGLECAB-4X4-01	5030	1720	1635
EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-01	5030	1800	1715
EU-ISUZU-D-MAX-I-PICKUP-SPACECAB-02	5155	1800	1730
EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-01	4910	1800	1720
EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	5030	1720	1635
EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-01	5035	1800	1735
EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	5030	1800	1715
EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	4480	1820	1810
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	4480	1820	1810
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-FACELIFT-01	4450	1818	1800
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-PREFL-01	4460	1800	1785
EU-MITSUBISHI-LANCER-VIII-CY0-SEDAN-4D-01	4570	1760	1490
EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	4476	1759	1411
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	4290	1753	1435
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	4290	1753	1415
EU-OPEL-ASTRA-H-GTC-HATCHBACK-FACELIFT-01	4290	1753	1405
EU-OPEL-ASTRA-H-GTC-HATCHBACK-PREFL-01	4290	1753	1415
EU-OPEL-ASTRA-H-HATCHBACK-3D-01	4290	1753	1415
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1467
EU-OPEL-ASTRA-H-HATCHBACK-5D-02	4249	1753	1460
EU-OPEL-ASTRA-H-HATCHBACK-GTC-01	4290	1753	1435
EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	4290	1753	1435
EU-OPEL-ASTRA-H-TWINTOP-CONVERTIBLE-01	4476	1759	1411
EU-OPEL-ASTRA-H-WAGON-01	4515	1753	1500
EU-OPEL-ASTRA-H-WAGON-L35-01	4515	1753	1500
EU-PORSCHE-911-997-CARRERA-4-CONVERTIBLE-01	4427	1852	1310
EU-PORSCHE-911-997-CARRERA-4S-CONVERTIBLE-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-AWD-WIDEBODY-01	4427	1852	1300
EU-PORSCHE-911-997-COUPE-GT3-01	4445	1808	1280
EU-PORSCHE-911-997-COUPE-RWD-01	4427	1808	1300
EU-PORSCHE-911-997-GT2-COUPE-01	4469	1852	1285
EU-PORSCHE-911-997-TURBO-CONVERTIBLE-01	4450	1852	1300
EU-PORSCHE-911-997-TURBO-COUPE-01	4450	1852	1300
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-I-01	3709	1616	1395
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	3709	1625	1395
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-I-01	3709	1616	1395
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	3709	1625	1395
EU-RENAULT-CLIO-II-HATCHBACK-01	3773	1639	1417
EU-RENAULT-CLIO-III-GRANDTOUR-WAGON-5D-01	4202	1707	1497
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-3D-02	3986	1719	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1707	1495
EU-RENAULT-CLIO-III-HATCHBACK-5D-02	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-3D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-I-HATCHBACK-5D-01	3986	1719	1495
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-3D-01	4032	1720	1497
EU-RENAULT-CLIO-III-PHASE-II-HATCHBACK-5D-01	4032	1720	1497
EU-RENAULT-CLIO-III-RS-HATCHBACK-3D-01	3991	1768	1477
EU-RENAULT-CLIO-II-PHASE-III-VAN-01	3811	1639	1417
EU-SAAB-9-3-II-CONVERTIBLE-FACELIFT-01	4647	1780	1437
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496
EU-SAAB-9-3-II-SEDAN-01	4635	1762	1466
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576
EU-SEAT-ALTEA-FREETRACK-I-5P-MPV-4X4-01	4493	1788	1622
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576
EU-SEAT-ALTEA-I-MPV-FR-PREFL-01	4325	1768	1568
EU-SEAT-ALTEA-XL-I-MPV-5D-01	4467	1768	1581
EU-SEAT-LEON-I-1M-HATCHBACK-01	4184	1742	1439
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FACELIFT-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-FR-01	4323	1768	1458
EU-SEAT-LEON-II-HATCHBACK-PREFL-01	4315	1768	1458
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454
EU-SKODA-OCTAVIA-I-1U2-HATCHBACK-FACELIFT-01	4507	1731	1431
EU-SKODA-OCTAVIA-I-1U5-WAGON-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-II-1Z5-WAGON-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z5-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-HATCHBACK-RS-PREFL-01	4578	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468
EU-SKODA-OCTAVIA-II-WAGON-RS-FACELIFT-01	4599	1769	1451
EU-SKODA-OCTAVIA-II-WAGON-RS-PREFL-01	4572	1769	1468
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2008-SUV-01	4150	1870	1695
EU-SUZUKI-GRAND-VITARA-II-3D-FACELIFT-2012-SUV-01	4035	1810	1695
EU-SUZUKI-GRAND-VITARA-II-3D-PREFL-SUV-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-5D-SUV-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	3905	1695	1685
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	3905	1780	1740
EU-SUZUKI-GRAND-VITARA-I-XL7-HT-SUV-5D-01	4760	1780	1740
EU-TOYOTA-COROLLA-E100-SEDAN-4D-01	4270	1685	1380
EU-TOYOTA-COROLLA-E120-SEDAN-01	4375	1710	1470
EU-TOYOTA-COROLLA-E90-SEDAN-GTI-01	4195	1655	1360
EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	4200	1710	1440
EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	4370	1770	1625
EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	4360	1770	1620
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1865
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1855
EU-VOLVO-240-P244-SEDAN-4D-01	4785	1707	1427
EU-VOLVO-240-P245-WAGON-5D-01	4785	1707	1460
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604
EU-VW-POLO-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-FACELIFT-HATCHBACK-3D-02	3916	1650	1459
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-01	3897	1650	1465
EU-VW-POLO-IV-FACELIFT-HATCHBACK-5D-02	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mitsubishi	Lancer v	EVO III	Stufenheck	Allrad	Benzin	198	269	Aug 1995	Jul 1996	2024-03-01	30404
Ford	Focus ii	2.0 Tdci	Schrägheck	Frontantrieb	Diesel	81	110	Feb 2008	Jul 2011	2024-03-01	30405
Ford	Focus ii	2.0 Tdci	Stufenheck	Frontantrieb	Diesel	81	110	Feb 2008	Jul 2011	2024-03-01	30406
Ford	Focus ii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	81	110	Feb 2008	Jul 2011	2024-03-01	30407
Suzuki	Sx4 / classic	1.6 Ddis	Schrägheck	Frontantrieb	Diesel	66	90	Apr 2007	-	2024-03-01	30408
Renault	Laguna i grandtour	2	Kombi	Frontantrieb	Benzin	84	114	Oct 1998	Jan 2001	2024-03-01	30409
Land Rover	Range rover i	2.4 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	83	113	Apr 1986	Jul 1994	2024-03-01	30410
Landwind (jmc)	Cv9	2	Großraumlimousine	Frontantrieb	Benzin	102	139	May 2006	Dec 2008	2024-03-01	30415
Ford	Transit tourneo	2.2 Tdci	Bus	Frontantrieb	Diesel	85	115	Oct 2008	Aug 2014	2024-03-01	30417
Ford	Transit	2.2 Tdci	Kasten	Frontantrieb	Diesel	85	115	Oct 2008	Aug 2014	2024-03-01	30418
Ford	Transit	2.2 Tdci	Bus	Frontantrieb	Diesel	85	115	Oct 2008	Aug 2014	2024-03-01	30419
Ford	Transit	2.2 Tdci	Pritsche/Fahrgestell	Frontantrieb	Diesel	85	115	Oct 2008	Aug 2014	2024-03-01	30420
Alfa Romeo	159	3.2 JTS	Stufenheck	Frontantrieb	Benzin	191	260	Jan 2008	Nov 2011	2024-03-01	30421
Alfa Romeo	159	3.2 JTS	Kombi	Frontantrieb	Benzin	191	260	Feb 2008	Nov 2011	2024-03-01	30422
VW	Polo	54 1.4	Stufenheck	Frontantrieb	Benzin	40	54	Jan 1998	Aug 1999	2024-03-01	30423
Porsche	911	3.6 Carrera 4	Coupe	Allrad	Benzin	254	345	Jun 2008	Dec 2012	2024-03-01	30424
Porsche	911	3.6 Carrera 4	Cabriolet	Allrad	Benzin	254	345	Jun 2008	Dec 2012	2024-03-01	30425
Porsche	911	3.8 Carrera 4S	Cabriolet	Allrad	Benzin	283	385	Jun 2008	Dec 2012	2024-03-01	30426
Porsche	911	3.6 Carrera 4	Targa	Allrad	Benzin	239	325	Jul 2006	Dec 2008	2024-03-01	30427
Porsche	911	3.8 Carrera 4S	Targa	Allrad	Benzin	261	355	Jul 2006	Dec 2008	2024-03-01	30428
Mazda	626 iii	2.2 12V 4WD	Stufenheck	Allrad	Benzin	85	115	Jan 1990	May 1992	2024-03-01	30429
Renault	Clio i	Electric	Schrägheck	Frontantrieb	Elektro	21	30	May 1996	Feb 1998	2026-05-01	30431
Subaru	Legacy iv station wagon	2.5 I AWD	Kombi	Allrad	Benzin	127	173	Jan 2008	Dec 2009	2024-03-01	30432
Saab	9-3	2.8 Turbo V6 XWD	Kombi	Allrad	Benzin	206	280	May 2008	Dec 2011	2024-03-01	30433
Saab	9-3	2.8 Turbo V6 XWD	Stufenheck	Allrad	Benzin	206	280	May 2008	Dec 2011	2024-03-01	30434
Subaru	Legacy iv station wagon	2.0 D AWD	Kombi	Allrad	Diesel	110	150	Feb 2008	Dec 2009	2024-03-01	30435
Subaru	Justy iv	1	Schrägheck	Frontantrieb	Benzin	51	69	Jan 2007	-	2024-03-01	30436
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	63	85	Aug 2011	Feb 2020	2024-03-01	30437
Ford	Focus iii turnier	1.0 Ecoboost	Kombi	Frontantrieb	Benzin	74	100	Feb 2012	Feb 2020	2024-03-01	30438
Ford	Focus iii turnier	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	88	120	Feb 2012	Feb 2020	2024-03-01	30439
Skoda	Octavia	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Jan 2008	Jun 2013	2024-03-01	30441
Skoda	Octavia	1.6 Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	75	102	Jan 2008	Jun 2013	2024-03-01	30442
Seat	Altea	1.6 Multifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	75	102	Oct 2006	Nov 2010	2024-03-01	30446
Toyota	Land cruiser 200	4.5 D4-d	Geländewagen geschlossen	Allrad	Diesel	195	265	Sep 2007	-	2024-03-01	30453
Toyota	Land cruiser prado	3.0 D	Geländewagen geschlossen	Allrad	Diesel	92	125	Sep 2002	Jul 2009	2024-03-01	30469
Volvo	Xc70 ii	T6 AWD	Kombi	Allrad	Benzin	210	286	Jan 2008	Dec 2016	2024-03-01	30470
Fiat	Siena	1.4	Stufenheck	Frontantrieb	Benzin	57	77	Jan 2007	Dec 2009	2024-03-01	30471
Fiat	Ducato	130 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	96	131	Aug 2006	-	2024-03-01	30473
Opel	Astra h	1.6	Stufenheck	Frontantrieb	Benzin	85	116	Sep 2008	Jun 2010	2026-04-01	30474
Opel	Omega a caravan	3.0 24V Omega 3000	Kombi	Heckantrieb	Benzin	150	204	Sep 1988	Apr 1994	2024-03-01	30475
Chrysler	Le baron	3.0 I V6	Coupe	Frontantrieb	Benzin	105	143	Jan 1990	Dec 1993	2024-03-01	30476
Ford	Focus iii turnier	1.0 Ecoboost	Kombi	Frontantrieb	Benzin	92	125	Feb 2012	Feb 2020	2024-03-01	30487
Lamborghini	Diablo	6	Coupe	Heckantrieb	Benzin	434	590	Apr 2000	Aug 2003	2024-03-01	30495
BMW	1	120 I	Schrägheck	Heckantrieb	Benzin	115	156	Mar 2007	Dec 2011	2024-03-01	30506
Isuzu	D-Max i	2.5 Ditd	Pick-up	Heckantrieb	Diesel	100	136	Oct 2006	Jun 2012	2024-03-01	30514
Cadillac	Cts	3.6	Stufenheck	Heckantrieb	Benzin	196	266	Jan 2008	Dec 2010	2024-03-01	30524
Ford USA	Windstar	3.8	Großraumlimousine	Frontantrieb	Benzin	149	203	Feb 1999	Dec 2003	2024-03-01	30539
Isuzu	Elf	5.2 DI	Pritsche/Fahrgestell	Heckantrieb	Diesel	110	150	Oct 2003	-	2025-06-01	30556
Aston Martin	Vanquish	6	Cabriolet	Heckantrieb	Benzin	421	573	Sep 2013	-	2025-11-01	30565
Seat	Leon	1.4 TSI	Kombi	Frontantrieb	Benzin	90	122	Sep 2012	Jun 2015	2024-03-01	30569
Ford	Focus iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	100	136	Jul 2010	Jun 2014	2024-03-01	30637
Suzuki	Grand vitara i	2.0 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	63	86	Apr 2000	Sep 2005	2024-03-01	30638
Nissan	Sunny	2	Stufenheck	Frontantrieb	Benzin	92	125	Sep 1997	Dec 1999	2024-03-01	30661
Toyota	Aurion	3.5	Stufenheck	Frontantrieb	Benzin	200	272	Mar 2006	Sep 2011	2024-03-01	30685
Chrysler	Sebring	2.0 VVT	Stufenheck	Frontantrieb	Benzin	115	156	Jul 2007	Dec 2010	2024-03-01	30688
Volvo	240	2.8	Stufenheck	Heckantrieb	Benzin	114	155	Oct 1982	Sep 1984	2024-03-01	30690
Audi	A4 b8 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	120	163	Aug 2008	Dec 2015	2024-03-01	30691
Ssangyong	Actyon	2.0 XDI 4WD	Pick-up	Allrad	Diesel	104	141	Apr 2007	-	2025-12-01	30692
Audi	Q7	6.0 TDI Quattro	SUV	Allrad	Diesel	368	500	Sep 2008	May 2014	2024-03-01	30693
Fiat	Dino	2	Coupe	Heckantrieb	Benzin	118	160	Jan 1967	Dec 1968	2024-03-01	30694
Fiat	Dino	2.4	Coupe	Heckantrieb	Benzin	132	180	Jan 1969	Dec 1972	2024-03-01	30695
Fiat	Dino spider	2	Cabriolet	Heckantrieb	Benzin	118	160	Jul 1966	Dec 1968	2024-03-01	30696
Fiat	Dino spider	2.4	Cabriolet	Heckantrieb	Benzin	132	180	Jan 1969	Dec 1972	2024-03-01	30697
Lancia	Aurelia berlina	1.8	Stufenheck	Heckantrieb	Benzin	41	56	Jan 1950	Dec 1953	2024-03-01	30698
Lancia	Aurelia berlina	2	Stufenheck	Heckantrieb	Benzin	47	64	Jan 1952	Dec 1953	2024-03-01	30699
Lancia	Aurelia berlina	2	Stufenheck	Heckantrieb	Benzin	51	70	Jan 1951	Dec 1953	2024-03-01	30700
Lancia	Aurelia berlina	2	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1952	Dec 1953	2024-03-01	30701
Lancia	Aurelia berlina	2.3	Stufenheck	Heckantrieb	Benzin	64	87	Jan 1954	Dec 1955	2024-03-01	30702
Lancia	Aurelia	2	Coupe	Heckantrieb	Benzin	59	80	Jan 1951	Dec 1953	2024-03-01	30703
Lancia	Aurelia	2.5	Coupe	Heckantrieb	Benzin	87	118	Jan 1953	Dec 1958	2024-03-01	30704
Lancia	Aurelia spider	2.5	Cabriolet	Heckantrieb	Benzin	87	118	Jan 1954	Dec 1955	2024-03-01	30705
Lancia	Aurelia	2.5	Cabriolet	Heckantrieb	Benzin	81	110	Jan 1956	Dec 1958	2024-03-01	30706
Lancia	Flaminia berlina	2.5	Stufenheck	Heckantrieb	Benzin	75	102	Jan 1957	Dec 1960	2024-03-01	30707
Lancia	Flaminia berlina	2.5	Stufenheck	Heckantrieb	Benzin	81	110	Dec 1961	Dec 1962	2024-03-01	30708
Lancia	Flaminia berlina	2.8	Stufenheck	Heckantrieb	Benzin	95	129	Aug 1963	Dec 1970	2024-03-01	30709
Lancia	Flaminia	2.5	Coupe	Heckantrieb	Benzin	88	119	Jan 1959	Dec 1961	2024-03-01	30710
Lancia	Flaminia	2.5	Coupe	Heckantrieb	Benzin	94	128	Aug 1962	Dec 1962	2024-03-01	30711
Lancia	Flaminia	2.8	Coupe	Heckantrieb	Benzin	103	140	Sep 1963	Dec 1967	2024-03-01	30712
Lancia	Flaminia gt	2.5	Coupe	Heckantrieb	Benzin	88	119	Jan 1959	Dec 1961	2024-03-01	30713
Lancia	Flaminia gt	2.5	Coupe	Heckantrieb	Benzin	103	140	Jan 1962	Dec 1963	2024-03-01	30714
Toyota	Corolla	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	93	126	Nov 2006	Jul 2014	2024-03-01	30715
Toyota	Corolla	1.6 Dual Vvti	Stufenheck	Frontantrieb	Benzin	91	124	Jan 2007	Jul 2014	2024-03-01	30716
Lancia	Flavia berlina	1.5	Stufenheck	Frontantrieb	Benzin	57	78	Nov 1960	Nov 1963	2024-03-01	30717
Lancia	Flavia berlina	1.5	Stufenheck	Frontantrieb	Benzin	59	80	Nov 1963	Dec 1966	2024-03-01	30718
Subaru	Outback	2.0 D AWD	Kombi	Allrad	Diesel	110	150	Sep 2008	Sep 2009	2024-03-01	30719
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	127	173	Sep 2008	Sep 2009	2024-03-01	30720
KIA	Shuma i	1.6	Schrägheck	Frontantrieb	Benzin	75	101	Jan 2001	Dec 2001	2024-05-01	30722
Lancia	Flavia berlina	1.8	Stufenheck	Frontantrieb	Benzin	68	92	Aug 1963	Dec 1966	2024-03-01	30723
Lancia	Flavia berlina	1.8 I	Stufenheck	Frontantrieb	Benzin	75	102	Nov 1965	Dec 1966	2024-03-01	30724
Lancia	Flavia	1.5	Coupe	Frontantrieb	Benzin	66	90	Jan 1961	Dec 1964	2024-03-01	30725
Lancia	Flavia	1.8	Coupe	Frontantrieb	Benzin	68	92	Aug 1963	Dec 1968	2024-03-01	30726
Lancia	Flavia	1.8 I	Coupe	Frontantrieb	Benzin	75	102	Aug 1965	Apr 1968	2024-03-01	30727
Lancia	Flavia	2	Coupe	Frontantrieb	Benzin	96	131	Apr 1969	Dec 1971	2024-03-01	30728
Lancia	Flavia	2.0 I	Coupe	Frontantrieb	Benzin	103	140	Jan 1970	Dec 1971	2024-03-01	30729
Lancia	Flavia	2	Coupe	Frontantrieb	Benzin	85	115	May 1971	Dec 1973	2024-03-01	30730
Lancia	Flavia berlina	1.5	Stufenheck	Frontantrieb	Benzin	62	84	May 1967	Dec 1970	2024-03-01	30731
Lancia	Flavia berlina	1.8	Stufenheck	Frontantrieb	Benzin	71	96	May 1967	Dec 1970	2024-03-01	30732
Lancia	Flavia berlina	1.8 I	Stufenheck	Frontantrieb	Benzin	79	107	May 1967	Dec 1969	2024-03-01	30733
Lancia	Flavia berlina	2	Stufenheck	Frontantrieb	Benzin	96	131	Jun 1969	Dec 1970	2024-03-01	30734
Lancia	Flavia berlina	2	Stufenheck	Frontantrieb	Benzin	103	140	Aug 1969	Dec 1970	2024-03-01	30736


--- Round 1 / 首次发送 ---
## 更新点

* 复用跨批次已有尺寸组，完成 Focus II、Transit、Alfa Romeo 159、Saab 9-3、Octavia II、Altea、Prado J120、Ducato III、A4 B8、Q7 4L 等映射。
* 首次闭合 Focus III Turnier 改款前后两个尺寸组。Ford 资料分别支持改款前 `4556×1823×1482 mm`、改款后 `4560×1823×1492 mm`。
* 首次闭合 Subaru Legacy IV facelift Wagon 与 Outback III Wagon 尺寸组。Legacy 两种动力页面均给出 `4795×1730×1475 mm`；Outback III 2.5i 页面给出 `4730×1770×1545 mm`。([汽车数据][1])
* 暂未把 Porsche 997.2 的 Ktype 30424–30426 指向已有 `4427 mm` 组。997.2 Carrera 4S Cabriolet 资料显示长度为 `4435 mm`，存在实质冲突，后续必须另建下一序号尺寸组，不能覆盖缓存。([autoevolution][2])
* Fiat Siena 30471 暂不复用已有 Siena/Albea 组，尚未确认其 2007–2009 车身与缓存组完全相同。

## 当前批次进度

* READY 映射：53 行
* 已覆盖输入 Ktype：32 / 100
* 待处理输入 Ktype：68
* 已确认尺寸组：44

  * 复用已有组：40
  * 本轮首次创建：4
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30405	30405	Hatchback	Focus II facelift			EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH		READY
30406	30406	Sedan	Focus II facelift		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH		READY
30407	30407	Wagon	Focus II facelift		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
30410_3dr	30410	SUV	Range Rover I		3	EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	HIGH	三门物理分支。	READY
30410_5dr	30410	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	五门物理分支。	READY
30417	30417	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	MEDIUM		READY
30418_swb_lowroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	MEDIUM	SWB低顶分支。	READY
30418_swb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	MEDIUM	SWB中顶分支。	READY
30418_mwb_lowroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	MEDIUM	MWB低顶分支。	READY
30418_mwb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	MEDIUM	MWB中顶分支。	READY
30418_mwb_highroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	MEDIUM	MWB高顶分支。	READY
30418_lwb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	MEDIUM	LWB中顶分支。	READY
30418_lwb_highroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	MEDIUM	LWB高顶分支。	READY
30421	30421	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
30422	30422	Wagon	159	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
30432	30432	Wagon	Legacy IV facelift	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH		READY
30433	30433	Wagon	9-3 II facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH		READY
30434	30434	Sedan	9-3 II facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH		READY
30435	30435	Wagon	Legacy IV facelift	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH		READY
30437_prefl	30437	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30437_facelift	30437	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30438_prefl	30438	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30438_facelift	30438	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30439_prefl	30439	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30439_facelift	30439	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30441_prefl	30441	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30441_facelift	30441	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30442_prefl	30442	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30442_facelift	30442	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30446_prefl	30446	MPV	Altea I	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	改款前物理外廓。	READY
30446_facelift	30446	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	改款后物理外廓。	READY
30469_3dr	30469	SUV	Land Cruiser Prado J120		3	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	HIGH	三门短轴物理分支。	READY
30469_5dr	30469	SUV	Land Cruiser Prado J120		5	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	HIGH	五门长轴物理分支。	READY
30470	30470	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
30473_swb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-SWB-01	MEDIUM	SWB底盘分支。	READY
30473_mwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-MWB-01	MEDIUM	MWB底盘分支。	READY
30473_mlwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	MEDIUM	加长MWB底盘分支。	READY
30473_lwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-LWB-01	MEDIUM	LWB底盘分支。	READY
30473_xlwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	MEDIUM	XLWB底盘分支。	READY
30487_prefl	30487	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30487_facelift	30487	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30524	30524	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
30539	30539	MPV	Windstar II		5	EU-FORD-USA-WINDSTAR-II-MPV-01	HIGH		READY
30569	30569	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
30637	30637	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH		READY
30688	30688	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
30690	30690	Sedan	240	P244	4	EU-VOLVO-240-P244-SEDAN-4D-01	HIGH		READY
30691_prefl	30691	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前物理外廓。	READY
30691_facelift	30691	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后物理外廓。	READY
30693_prefl	30693	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30693_facelift	30693	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30719	30719	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
30720	30720	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475	Auto-Data Legacy IV 2.5i;Auto-Data Legacy IV 2.0D	https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-2.5i-173hp-awd-34106;https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-2.0d-150hp-awd-34101
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482	Ford Focus 2011 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492	Ford Focus 2015 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Focus-UK.pdf
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545	Auto-Data Outback III 2.5i	https://www.auto-data.net/en/subaru-outback-iii-bl-bp-2.5i-173hp-awd-16146
```

## 下一步优先处理

1. 处理 Porsche 997.2 Ktype 30424–30426，按 `4435 mm` 外廓创建下一可用序号，禁止覆盖现有 `4427 mm` 缓存组。
2. 闭合 Transit Bus 30419 与 Pritsche/Fahrgestell 30420 的轴距、车顶及底盘分支。
3. 核对 D-Max 30514、Grand Vitara 30638 的驾驶室、门数及宽体边界。
4. 按车身系列批量处理 Fiat Dino 与 Lancia Aurelia、Flaminia、Flavia 经典车型，避免逐发动机重复抓取。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-2.5i-173hp-awd-34106 "Subaru Legacy IV Station Wagon (facelift 2006) 2.5i (173 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.autoevolution.com/cars/porsche-911-carrera-4s-cabriolet-997-2008.html?utm_source=chatgpt.com "PORSCHE 911 Carrera 4S Cabriolet (997) (2008-2012) ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新建 Mitsubishi Lancer Evolution III、Suzuki SX4 I、Subaru Justy IV 与 Opel Astra H Sedan 尺寸组，并完成对应 Ktype 映射。([汽车数据][1])
* Porsche 997 改款后 Carrera 4、Carrera 4S 与改款前 Targa 4、Targa 4S 已按实际车身形式和高度分别建组；未覆盖或改写已有 Porsche 缓存组。([汽车数据][2])
* Renault Clio I Electric 按 Phase II 的三门、五门分支复用已有尺寸组。
* Toyota Land Cruiser 200 根据官方规格拆分 KDSS 与 AHC 两种悬架高度，长度和宽度一致，高度分别为 1910 mm 与 1865 mm。

## 当前批次进度

* READY 映射：66 行
* 已覆盖输入 Ktype：43 / 100
* 待处理输入 Ktype：57
* 已确认尺寸组：55
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30404	30404	Sedan	Lancer Evolution III	CE9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-III-CE9A-SEDAN-4D-01	HIGH		READY
30408	30408	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-5D-01	HIGH		READY
30424	30424	Coupe	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	HIGH	改款后Carrera 4宽体Coupe。	READY
30425	30425	Convertible	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	HIGH	改款后Carrera 4宽体敞篷车。	READY
30426	30426	Convertible	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	HIGH	改款后Carrera 4S宽体敞篷车。	READY
30427	30427	Targa	911 (997)	997	2	EU-PORSCHE-911-997-TARGA-4-01	HIGH	Targa 4物理外廓。	READY
30428	30428	Targa	911 (997)	997	2	EU-PORSCHE-911-997-TARGA-4S-01	HIGH	Targa 4S物理外廓。	READY
30431_3dr	30431	Hatchback	Clio I Phase II		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	MEDIUM	三门物理分支。	READY
30431_5dr	30431	Hatchback	Clio I Phase II		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	五门物理分支。	READY
30436	30436	Hatchback	Justy IV		5	EU-SUBARU-JUSTY-IV-HATCHBACK-5D-01	HIGH		READY
30453_kdss	30453	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-200-J200-SUV-KDSS-01	MEDIUM	KDSS悬架高度分支。	READY
30453_ahc	30453	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-200-J200-SUV-AHC-01	MEDIUM	AHC悬架高度分支。	READY
30474	30474	Sedan	Astra H		4	EU-OPEL-ASTRA-H-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-EVOLUTION-III-CE9A-SEDAN-4D-01	4310	1695	1420	Auto-Data Mitsubishi Lancer Evolution III	https://www.auto-data.net/en/mitsubishi-lancer-evolution-model-2861
EU-SUZUKI-SX4-I-HATCHBACK-5D-01	4100	1730	1565	Auto-Data Suzuki SX4 I 1.6 DDiS	https://www.auto-data.net/en/suzuki-sx4-i-1.6-l-ddis-90hp-16571
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310	Auto-Data Porsche 911 997 facelift Carrera 4	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-4-3.6-345hp-36759
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera 4	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-4-3.6-345hp-36739
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera 4S	https://www.auto-data.net/de/porsche-911-cabriolet-997-facelift-2008-carrera-4s-3.8-385hp-36741
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310	Auto-Data Porsche 911 Targa 997 Targa 4	https://www.auto-data.net/en/porsche-911-targa-997-targa-4-3.6-325hp-36753
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300	Auto-Data Porsche 911 Targa 997 Targa 4S	https://www.auto-data.net/en/porsche-911-targa-997-targa-4s-3.8-355hp-36755
EU-SUBARU-JUSTY-IV-HATCHBACK-5D-01	3610	1665	1540	Auto-Data Subaru Justy IV	https://www.auto-data.net/en/subaru-justy-iv-generation-3599
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-KDSS-01	4950	1970	1910	Toyota Land Cruiser V8 official brochure	https://toyotasverigebroschyr.com/webbroschyr/bilbroschyr/lan_v8_bb_web.pdf
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-AHC-01	4950	1970	1865	Toyota Land Cruiser V8 official brochure	https://toyotasverigebroschyr.com/webbroschyr/bilbroschyr/lan_v8_bb_web.pdf
EU-OPEL-ASTRA-H-SEDAN-4D-01	4587	1753	1458	Auto-Data Opel Astra H Sedan 1.6i	https://www.auto-data.net/en/opel-astra-h-sedan-1.6i-16v-115hp-2340
```

## 下一步优先处理

1. 批量闭合 Transit Bus 与 Pritsche/Fahrgestell 的轴距、车顶及驾驶室分支。
2. 处理 D-Max、Grand Vitara、Actyon Pickup 与 Isuzu Elf 的驾驶室和车身边界。
3. 按共用物理车身聚类处理 Fiat Dino、Lancia Aurelia、Flaminia 与 Flavia，避免按发动机重复建组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-lancer-evolution-model-2861?utm_source=chatgpt.com "Specs for all generations of Mitsubishi Lancer Evolution"
[2]: https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-4-3.6-345hp-36759 "Porsche 911 (997, facelift 2008) Carrera 4 3.6 (345 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Fiat Dino 四个物理分支：2000/2400 Coupé 与 2000/2400 Spider。两次排量升级伴随可测外廓变化，分别建组，不因车型名称相同而合并。([汽车目录][1])
* 闭合 Lancia Aurelia 九个 Ktype。B10、B21、B22 共用标准 Berlina 外廓；64 HP 的 B15 是明显加长礼宾车，独立建组；B12、B20 2.0、B20 2.5、B24 Spider 和 B24 Convertible 分别建组。([汽车目录][2])
* 闭合 Lancia Flaminia 八个 Ktype，按 Berlina、Pininfarina Coupé、Touring GT 三种物理车身批量复用尺寸组。([汽车目录][3])

## 当前批次进度

* READY 映射：87 行
* 已覆盖输入 Ktype：64 / 100
* PENDING 输入 Ktype：36
* 已确认尺寸组：69
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30694	30694	Coupe	Dino 2000		2	EU-FIAT-DINO-2000-COUPE-2D-01	HIGH		READY
30695	30695	Coupe	Dino 2400		2	EU-FIAT-DINO-2400-COUPE-2D-01	HIGH		READY
30696	30696	Convertible	Dino 2000 Spider		2	EU-FIAT-DINO-2000-SPIDER-2D-01	HIGH		READY
30697	30697	Convertible	Dino 2400 Spider		2	EU-FIAT-DINO-2400-SPIDER-2D-01	HIGH		READY
30698	30698	Sedan	Aurelia I	B10	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30699	30699	Sedan	Aurelia I	B15	4	EU-LANCIA-AURELIA-I-B15-LONG-BERLINA-4D-01	HIGH	B15长轴礼宾车外廓。	READY
30700	30700	Sedan	Aurelia I	B21	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30701	30701	Sedan	Aurelia I	B22	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30702	30702	Sedan	Aurelia II	B12	4	EU-LANCIA-AURELIA-II-B12-BERLINA-4D-01	HIGH		READY
30703	30703	Coupe	Aurelia B20 II	B20	2	EU-LANCIA-AURELIA-B20-II-COUPE-2D-01	MEDIUM	80 PS对应B20第二系列外廓。	READY
30704	30704	Coupe	Aurelia B20 2500	B20	2	EU-LANCIA-AURELIA-B20-2500-COUPE-2D-01	HIGH		READY
30705	30705	Convertible	Aurelia B24 Spider	B24	2	EU-LANCIA-AURELIA-B24-SPIDER-2D-01	HIGH	Spider物理外廓。	READY
30706	30706	Convertible	Aurelia B24 Convertible	B24	2	EU-LANCIA-AURELIA-B24-CONVERTIBLE-2D-01	HIGH	Convertible物理外廓。	READY
30707	30707	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30708	30708	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30709	30709	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30710	30710	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30711	30711	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30712	30712	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30713	30713	Coupe	Flaminia GT Touring		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	HIGH		READY
30714	30714	Coupe	Flaminia GT Touring		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-DINO-2000-COUPE-2D-01	4510	1700	1290	Automobile-Catalog Fiat Dino Coupe 1967	https://www.automobile-catalog.com/car/1967/710660/fiat_dino_coupe.html
EU-FIAT-DINO-2400-COUPE-2D-01	4507	1696	1315	Automobile-Catalog Fiat Dino Coupe 1969	https://www.automobile-catalog.com/car/1969/710690/fiat_dino_coupe.html
EU-FIAT-DINO-2000-SPIDER-2D-01	4110	1710	1270	Automobile-Catalog Fiat Dino Spider 1967	https://www.automobile-catalog.com/car/1967/710645/fiat_dino_spider.html
EU-FIAT-DINO-2400-SPIDER-2D-01	4134	1710	1270	Automobile-Catalog Fiat Dino Spider 1969	https://www.automobile-catalog.com/car/1969/710675/fiat_dino_spider.html
EU-LANCIA-AURELIA-I-BERLINA-4D-01	4420	1560	1500	Automobile-Catalog Lancia Aurelia B10;Automobile-Catalog Lancia Aurelia B21;Automobile-Catalog Lancia Aurelia B22	https://www.automobile-catalog.com/car/1950/1373645/lancia_aurelia_b10.html;https://www.automobile-catalog.com/car/1951/1373675/lancia_aurelia_b21.html;https://www.automobile-catalog.com/car/1952/1373915/lancia_aurelia_b22.html
EU-LANCIA-AURELIA-I-B15-LONG-BERLINA-4D-01	4810	1595	1555	Automobile-Catalog Lancia Aurelia B15	https://www.automobile-catalog.com/car/1952/1373900/lancia_aurelia_b15.html
EU-LANCIA-AURELIA-II-B12-BERLINA-4D-01	4485	1560	1505	Automobile-Catalog Lancia Aurelia B12	https://www.automobile-catalog.com/car/1954/1373930/lancia_aurelia_b12.html
EU-LANCIA-AURELIA-B20-II-COUPE-2D-01	4290	1540	1360	Automobile-Catalog Lancia Aurelia B20 GT second series	https://www.automobile-catalog.com/car/1952/1373945/lancia_aurelia_b20_gt_2a_serie.html
EU-LANCIA-AURELIA-B20-2500-COUPE-2D-01	4370	1550	1360	Automobile-Catalog Lancia Aurelia B20 GT 2500	https://www.automobile-catalog.com/car/1954/1373975/lancia_aurelia_b20_gt_2500_4a_serie.html
EU-LANCIA-AURELIA-B24-SPIDER-2D-01	4200	1550	1300	Automobile-Catalog Lancia Aurelia B24 Spider	https://www.automobile-catalog.com/car/1954/1374020/lancia_aurelia_b24_spider.html
EU-LANCIA-AURELIA-B24-CONVERTIBLE-2D-01	4230	1555	1305	Automobile-Catalog Lancia Aurelia B24 Convertible	https://www.automobile-catalog.com/car/1956/1374035/lancia_aurelia_b24_america_convertible_2a_serie.html
EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	4855	1750	1480	Automobile-Catalog Lancia Flaminia Berlina	https://www.automobile-catalog.com/car/1957/1374530/lancia_flaminia_berlina.html
EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	4680	1740	1420	Automobile-Catalog Lancia Flaminia Coupe 3B;Automobile-Catalog Lancia Flaminia Coupe 3B 2.8	https://www.automobile-catalog.com/car/1962/1374695/lancia_flaminia_coupe_3b.html;https://www.automobile-catalog.com/car/1965/1374770/lancia_flaminia_coupe_3b_2_8.html
EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	4500	1680	1305	Automobile-Catalog Lancia Flaminia GT Touring;Automobile-Catalog Lancia Flaminia GT 3C Touring	https://www.automobile-catalog.com/car/1959/1374620/lancia_flaminia_gt_touring.html;https://www.automobile-catalog.com/car/1963/1374710/lancia_flaminia_gt_3c_touring.html
```

## 下一步优先处理

1. 批量闭合 Lancia Flavia Berlina 与 Coupé 的前期、后期物理外廓。
2. 处理 Transit Bus、Transit Pritsche/Fahrgestell 的轴距与车顶分支。
3. 处理 D-Max、Grand Vitara、Actyon Pickup、Isuzu Elf 的驾驶室和底盘边界。
4. 补齐剩余普通乘用车：Laguna I Grandtour、Polo Sedan、Mazda 626 III、Omega A Caravan、BMW E81、Legacy/Outback、Corolla E150 等。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1967/710660/fiat_dino_coupe.html?utm_source=chatgpt.com "1967 Fiat Dino Coupe Specs Review (118 kW / 160 PS ..."
[2]: https://www.automobile-catalog.com/car/1952/1373915/lancia_aurelia_b22.html?utm_source=chatgpt.com "1952 Lancia Aurelia B22 Specs Review (66 kW / 90 PS / 89 hp) (since mid-year 1952 for Europe )"
[3]: https://www.automobile-catalog.com/car/1962/1374695/lancia_flaminia_coupe_3b.html?utm_source=chatgpt.com "1962 Lancia Flaminia Coupe 3b Specs Review (94 kW ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 Lancia Flavia 全系列 15 个 Ktype，按早期 Berlina、后期 Berlina、早期 Pininfarina Coupé、Flavia 2000 Coupé、Lancia 2000 Coupé 五种外廓批量建组。([汽车目录][1])
* 完成 Laguna I Grandtour、Landwind CV9、Polo III Classic、Fiat Siena 178、Lamborghini Diablo VT 6.0 的尺寸组和映射。([汽车目录][2])
* Ktype 30506 已确认对应 BMW E81 三门 Hatchback，直接复用已有尺寸组。([Alufelgen Sportfahrwerke und mehr][3])

## 当前批次进度

* READY 映射：108 行
* 已覆盖输入 Ktype：85 / 100
* PENDING 输入 Ktype：15
* 已确认尺寸组：79
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30409	30409	Wagon	Laguna I Phase II	K56	5	EU-RENAULT-LAGUNA-I-PHASE-II-GRANDTOUR-WAGON-5D-01	HIGH		READY
30415	30415	MPV	CV9 I		5	EU-LANDWIND-CV9-I-MPV-5D-01	HIGH		READY
30423	30423	Sedan	Polo III Classic	6V2	4	EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	HIGH		READY
30471	30471	Sedan	Siena I facelift	178	4	EU-FIAT-SIENA-178-FACELIFT-SEDAN-4D-01	HIGH		READY
30495	30495	Coupe	Diablo VT 6.0		2	EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	HIGH		READY
30506	30506	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
30717	30717	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30718	30718	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30723	30723	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30724	30724	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30725	30725	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30726	30726	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30727	30727	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30728	30728	Coupe	Flavia 2000 Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	HIGH		READY
30729	30729	Coupe	Flavia 2000 Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	HIGH		READY
30730	30730	Coupe	2000 Coupe		2	EU-LANCIA-2000-COUPE-2D-01	HIGH	后期更名车型物理外廓。	READY
30731	30731	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30732	30732	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30733	30733	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30734	30734	Sedan	Flavia 2000 Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30736	30736	Sedan	Flavia 2000 Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-LAGUNA-I-PHASE-II-GRANDTOUR-WAGON-5D-01	4628	1752	1448	Automobile-Catalog Renault Laguna Wagon 2.0 8V	https://www.automobile-catalog.com/car/1998/2946080/renault_laguna_wagon_2_0_8v.html
EU-LANDWIND-CV9-I-MPV-5D-01	4410	1768	1640	Drive.Place Landwind Fashion CV9 I	https://landwind.drive.place/cv9/i/group_compactvan/405281
EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	4140	1640	1410	Volkswagen Newsroom Polo III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-3-profile-19149
EU-FIAT-SIENA-178-FACELIFT-SEDAN-4D-01	4135	1634	1453	Automobile-Catalog Fiat Siena ELX 1.4	https://www.automobile-catalog.com/car/2007/734840/fiat_siena_elx_1_4.html
EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	4470	2040	1105	Autoevolution Lamborghini Diablo VT 6.0	https://www.autoevolution.com/cars/lamborghini-diablo-vt-60-2000.html
EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	4580	1610	1510	Automobile-Catalog Lancia Flavia Berlina 1962;Automobile-Catalog Lancia Flavia Berlina 1.8 1966	https://www.automobile-catalog.com/car/1962/1375175/lancia_flavia_berlina.html;https://www.automobile-catalog.com/car/1966/1376345/lancia_flavia_berlina_1_8_carburatore.html
EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	4485	1610	1350	Automobile-Catalog Lancia Flavia Coupe Pininfarina 1962;Automobile-Catalog Lancia Flavia Coupe 1.8 Iniezione 1966	https://www.automobile-catalog.com/car/1962/1375190/lancia_flavia_coupe_pininfarina.html;https://www.automobile-catalog.com/car/1966/1375400/lancia_flavia_coupe_pininfarina_1_8_iniezione.html
EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	4540	1605	1330	Automobile-Catalog Lancia Flavia Coupe 2000 Iniezione	https://www.automobile-catalog.com/car/1970/1375565/lancia_flavia_coupe_2000_iniezione.html
EU-LANCIA-2000-COUPE-2D-01	4555	1605	1330	Automobile-Catalog Lancia 2000 Coupe	https://www.automobile-catalog.com/car/1971/1376390/lancia_2000_coupe.html
EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	4580	1610	1500	Automobile-Catalog Lancia Flavia 1800 Iniezione;Automobile-Catalog Lancia Flavia 2000 Iniezione	https://www.automobile-catalog.com/car/1970/1375475/lancia_flavia_1800_iniezione.html;https://www.automobile-catalog.com/car/1970/1375505/lancia_flavia_2000_iniezione.html
```

## 下一步优先处理

1. 闭合 Transit Bus 30419 与 Transit Pritsche/Fahrgestell 30420 的全部轴距和车顶分支。
2. 闭合 D-Max 30514、Grand Vitara 30638、Actyon Sports 30692 的驾驶室及车身边界。
3. 处理 Mazda 626、Omega A Caravan、Chrysler Le Baron、Isuzu Elf、Vanquish Volante、Nissan Sunny、Toyota Aurion、Corolla E150 与 Kia Shuma。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1962/1375175/lancia_flavia_berlina.html?utm_source=chatgpt.com "1962 Lancia Flavia Berlina Specs Review (57.5 kW / 78 PS / 77 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1998/2946080/renault_laguna_wagon_2_0_8v.html?utm_source=chatgpt.com "1998 Renault Laguna Wagon 2.0 8V Specs Review (83.5 kW / 114 PS / 112 hp) (since April 1998 for Europe )"
[3]: https://www.jms-fahrzeugteile.com/en/brake-technology/ebc-brake-discsbrake-pads/ebc-standard-bremsbelaege-fuer/bmw/1/vavornefront/1152673/ebc-blackstuff-pads-dp1578-4793-fits-for-bmw-1-e81?utm_source=chatgpt.com "EBC Blackstuff pads DP1578(4793) fits for BMW 1 E81 | JMS Fahrzeugteile"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮新增 16 条 READY 映射，覆盖 12 个 Ktype。
* 首次创建 12 个尺寸组；D-Max 三种驾驶室分支直接复用累计表已有尺寸组。
* Omega A Caravan 按改款前后拆分；Grand Vitara I 按三门、五门拆分。三门实测三维与累计 `...3D-NARROW-01` 不一致，因此未覆盖旧组，按规则新建 `...3D-NARROW-02`。
* 当前只剩 `30420`、`30556`、`30661` 三个 Ktype 未闭合。

## 当前批次进度

* READY 映射：124 行
* 已覆盖输入 Ktype：97 / 100
* PENDING 输入 Ktype：3
* 已确认尺寸组：91
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30419	30419	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MINIBUS-MWB-FWD-MEDROOF-01	HIGH		READY
30429	30429	Sedan	626 III facelift	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-4WD-01	HIGH		READY
30475_prefl	30475	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30475_facelift	30475	Wagon	Omega A facelift		5	EU-OPEL-OMEGA-A-CARAVAN-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30476	30476	Coupe	LeBaron III	J	2	EU-CHRYSLER-LEBARON-III-J-COUPE-2D-01	MEDIUM		READY
30514_singlecab	30514	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	MEDIUM	单排驾驶室物理分支。	READY
30514_spacecab	30514	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	MEDIUM	加长驾驶室物理分支。	READY
30514_doublecab	30514	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	MEDIUM	双排驾驶室物理分支。	READY
30565	30565	Convertible	Vanquish II		2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-2D-01	HIGH	Volante敞篷物理外廓。	READY
30638_3dr	30638	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-02	HIGH	三门窄体物理分支。	READY
30638_5dr	30638	SUV	Grand Vitara I		5	EU-SUZUKI-GRAND-VITARA-I-SUV-5D-01	HIGH	五门物理分支。	READY
30685	30685	Sedan	Aurion I	XV40	4	EU-TOYOTA-AURION-I-XV40-SEDAN-4D-01	HIGH		READY
30692	30692	Pickup	Actyon Sports I		4	EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-4D-01	HIGH		READY
30715	30715	Sedan	Corolla X	E150	4	EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	HIGH		READY
30716	30716	Sedan	Corolla X	E150	4	EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	HIGH		READY
30722	30722	Hatchback	Shuma I		5	EU-KIA-SHUMA-I-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-TRANSIT-MK7-MINIBUS-MWB-FWD-MEDROOF-01	5230	1974	2363	Ford People Movers 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-People-Movers-UK.pdf
EU-MAZDA-626-III-GD-SEDAN-4D-4WD-01	4515	1690	1395	CarsGuide Mazda 626 1991 dimensions;Automobile-Catalog Mazda 626 2.2i GLX 4WD	https://www.carsguide.com.au/mazda/626/car-dimensions/1991;https://www.automobile-catalog.com/car/1991/1637060/mazda_626_2_2i_glx_4wd_cat.html
EU-OPEL-OMEGA-A-CARAVAN-WAGON-PREFL-01	4742	1772	1530	Automobile-Catalog Opel Omega Caravan 24V 1990	https://www.automobile-catalog.com/car/1990/2467325/opel_omega_caravan_24v_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-WAGON-FACELIFT-01	4768	1760	1530	Automobile-Catalog Opel Omega Caravan 24V 1991	https://www.automobile-catalog.com/car/1991/2468195/opel_omega_caravan_24v.html
EU-CHRYSLER-LEBARON-III-J-COUPE-2D-01	4696	1740	1295	Edmunds 1990 Chrysler LeBaron GT;Auto-Data Chrysler Le Baron Coupe 3.0 V6	https://www.edmunds.com/chrysler/le-baron/1990/st-10469/features-specs/;https://www.auto-data.net/en/chrysler-le-baron-coupe-3.0-i-v6-136hp-14702
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-2D-01	4728	1912	1294	Aston Martin Vanquish brochure;Automobile Dimension Vanquish Volante	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-Vanquish-2013.pdf;https://www.automobiledimension.com/model/aston-martin/vanquish-volante
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-02	3865	1695	1685	Auto-Data Suzuki Grand Vitara 2.0 TD 3-door	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-2.0-td-3-dr-87hp-16596
EU-SUZUKI-GRAND-VITARA-I-SUV-5D-01	4195	1780	1685	Auto-Data Suzuki Grand Vitara 2.0 TD 5-door	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-2.0-td-5-dr-87hp-16597
EU-TOYOTA-AURION-I-XV40-SEDAN-4D-01	4825	1820	1470	Auto-Data Toyota Aurion I XV40 3.5 V6;CarsGuide Toyota Aurion 2006 dimensions	https://www.auto-data.net/en/toyota-aurion-i-xv40-3.5-v6-277hp-automatic-3460;https://www.carsguide.com.au/toyota/aurion/car-dimensions/2006
EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-4D-01	4965	1900	1755	Auto-Data SsangYong Actyon Sports 2.0 XDi	https://www.auto-data.net/en/ssangyong-actyon-sports-2.0xdi-141hp-15989
EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	4540	1760	1470	Toyota Europe all-new Corolla press release;Auto-Data Toyota Corolla X E140/E150 1.6 VVT-i	https://newsroom.toyota.eu/all-new-corolla-setting-new-standards-in-its-class/;https://www.auto-data.net/en/toyota-corolla-x-e140-e150-1.6-i-16v-vvt-i-124hp-mmt-3298
EU-KIA-SHUMA-I-HATCHBACK-5D-01	4510	1720	1420	UltimateSpecs Kia Shuma I 1.6	https://www.ultimatespecs.com/car-specs/Kia/4305/Kia-Shuma-I-16-.html
```

## 下一步优先处理

1. `30420`：确认 Transit Mk7 前驱底盘驾驶室实际覆盖的轴距及单排、双排边界。
2. `30556`：确认 Isuzu Elf 5.2 DI 对应的 N-Series 代际、标准/宽体驾驶室及轴距范围。
3. `30661`：根据 1997–1999、2.0 125 HP 组合锁定 Nissan Sunny 的具体市场代际与车身代码。

推进信号：CONTINUE


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* `30420` 已确认对应 Transit Mk7 前驱 Pritsche/Fahrgestell。按单排/双排、SWB/MWB/LWB/EF 及标准/加长后车架拆成 13 个物理分支，全部复用累计表已有尺寸组，未重新抓取或重复建组。该 Ktype 的车型目录边界为 Transit Platform/Chassis、2.2 TDCi FWD、85 kW、2008–2014。([Market-Auto][1])
* `30661` 已根据 1997–1999 年生产区间修正为 Sunny B14 四门 Sedan，而非目录中时间不相符的 N16 标签；同代 B14 Sedan 的标准外廓为 `4295×1690×1385 mm`。([汽车目录][2])
* `30556` 已缩小到 Isuzu Elf/N-Series 5.2 DI 的 NKR8/NKQ8 目录范围。官方 NQR 450 资料确认中轴、长轴两种宽驾驶室外廓，但尚未证明 Ktype 是否同时包含 NKR8 窄驾驶室，暂不强行闭合。([AUTODOC 英国][3])

## 当前批次进度

* READY 映射：138 行
* 已覆盖输入 Ktype：99 / 100
* PENDING 输入 Ktype：1
* 已确认尺寸组：92
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30420_swb_singlecab	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	MEDIUM	SWB单排驾驶室分支。	READY
30420_mwb_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	MWB单排标准后车架分支。	READY
30420_mwb_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	MEDIUM	MWB单排加长后车架分支。	READY
30420_lwb_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	MEDIUM	LWB单排标准后车架分支。	READY
30420_lwb_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	MEDIUM	LWB单排加长后车架分支。	READY
30420_ef_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	EF单排标准后车架分支。	READY
30420_ef_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	MEDIUM	EF单排加长后车架分支。	READY
30420_mwb_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	MEDIUM	MWB双排标准后车架分支。	READY
30420_mwb_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	MEDIUM	MWB双排加长后车架分支。	READY
30420_lwb_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	LWB双排标准后车架分支。	READY
30420_lwb_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	MEDIUM	LWB双排加长后车架分支。	READY
30420_ef_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	MEDIUM	EF双排标准后车架分支。	READY
30420_ef_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	MEDIUM	EF双排加长后车架分支。	READY
30661	30661	Sedan	Sunny B14	B14	4	EU-NISSAN-SUNNY-B14-SEDAN-4D-01	MEDIUM	生产区间对应B14四门物理车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-SUNNY-B14-SEDAN-4D-01	4295	1690	1385	Automobile-Catalog Nissan Sunny B14 1997 Sedan	https://www.automobile-catalog.com/car/1997/2260025/nissan_sunny_1500_super_saloon.html
```

## 下一步优先处理

确认 `30556` 的 Ktype 是否仅覆盖 NQR/NKQ8 宽驾驶室中轴、长轴，或同时覆盖 NKR8 窄驾驶室。闭合后立即进入机械收尾并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://market-auto.fr/producto/denckermann-186-k300066?utm_source=chatgpt.com "Central clutch, clutch Ford TRANSIT TOURNEO Bus 1490012 ..."
[2]: https://www.automobile-catalog.com/make/nissan/sunny_8gen_b14/sunny_8gen_2_sedan/1997.html?utm_source=chatgpt.com "1997 Nissan Sunny 8gen/II Sedan 2WD (B14) full range specs"
[3]: https://www.autodoc.co.uk/car-parts/mounting-kit-charger-15070/isuzu/elf/elf-platform-chassis-nkr8-nkq8/30556-5-2-di?utm_source=chatgpt.com "ISUZU Elf Platform / Chassis (NKR8_, NKQ8_) 5.2 Di Mounting ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3401-3500_ktype_dimension_mapping_final.tsv
- all_3401-3500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 最后一个待处理 Ktype `30556` 已闭合为 `NKR81` 窄体驾驶室与 `NKQ81` 宽体驾驶室两个底盘分支。车型目录将 5.2 ([AUTODOC 英国][1])([autodoc.co.uk][1])turn857093search6turn835828view1
* 已完成机械检查：表头列数正确、140 个映射 `id` 唯一、113 个尺寸组 ID 唯一、全部引用闭合、无孤立尺寸组、尺寸和来源字段均非空。
* 已生成两个任务指定文件。

## 当前批次进度

* 输入 Ktype：100 / 100 已覆盖
* READY 映射：140
* PENDING 映射：0
* DIMENSION_GROUP：113
* 状态：完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
30404	30404	Sedan	Lancer Evolution III	CE9A	4	EU-MITSUBISHI-LANCER-EVOLUTION-III-CE9A-SEDAN-4D-01	HIGH		READY
30405	30405	Hatchback	Focus II facelift			EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH		READY
30406	30406	Sedan	Focus II facelift		4	EU-FORD-FOCUS-II-SEDAN-01	HIGH		READY
30407	30407	Wagon	Focus II facelift		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH		READY
30408	30408	Hatchback	SX4 I		5	EU-SUZUKI-SX4-I-HATCHBACK-5D-01	HIGH		READY
30409	30409	Wagon	Laguna I Phase II	K56	5	EU-RENAULT-LAGUNA-I-PHASE-II-GRANDTOUR-WAGON-5D-01	HIGH		READY
30410_3dr	30410	SUV	Range Rover I		3	EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	HIGH	三门物理分支。	READY
30410_5dr	30410	SUV	Range Rover I		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	HIGH	五门物理分支。	READY
30415	30415	MPV	CV9 I		5	EU-LANDWIND-CV9-I-MPV-5D-01	HIGH		READY
30417	30417	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	MEDIUM		READY
30418_swb_lowroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	MEDIUM	SWB低顶分支。	READY
30418_swb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	MEDIUM	SWB中顶分支。	READY
30418_mwb_lowroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	MEDIUM	MWB低顶分支。	READY
30418_mwb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	MEDIUM	MWB中顶分支。	READY
30418_mwb_highroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	MEDIUM	MWB高顶分支。	READY
30418_lwb_medroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	MEDIUM	LWB中顶分支。	READY
30418_lwb_highroof	30418	Van	Transit Mk7			EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	MEDIUM	LWB高顶分支。	READY
30419	30419	MPV	Transit Mk7			EU-FORD-TRANSIT-MK7-MINIBUS-MWB-FWD-MEDROOF-01	HIGH		READY
30420_swb_singlecab	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	MEDIUM	SWB单排驾驶室分支。	READY
30420_mwb_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	MEDIUM	MWB单排标准后车架分支。	READY
30420_mwb_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	MEDIUM	MWB单排加长后车架分支。	READY
30420_lwb_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	MEDIUM	LWB单排标准后车架分支。	READY
30420_lwb_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	MEDIUM	LWB单排加长后车架分支。	READY
30420_ef_singlecab_stdframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	MEDIUM	EF单排标准后车架分支。	READY
30420_ef_singlecab_extframe	30420	Pickup	Transit Mk7		2	EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	MEDIUM	EF单排加长后车架分支。	READY
30420_mwb_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	MEDIUM	MWB双排标准后车架分支。	READY
30420_mwb_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	MEDIUM	MWB双排加长后车架分支。	READY
30420_lwb_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	MEDIUM	LWB双排标准后车架分支。	READY
30420_lwb_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	MEDIUM	LWB双排加长后车架分支。	READY
30420_ef_doublecab_stdframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	MEDIUM	EF双排标准后车架分支。	READY
30420_ef_doublecab_extframe	30420	Pickup	Transit Mk7		4	EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	MEDIUM	EF双排加长后车架分支。	READY
30421	30421	Sedan	159	939	4	EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	HIGH		READY
30422	30422	Wagon	159	939	5	EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	HIGH		READY
30423	30423	Sedan	Polo III Classic	6V2	4	EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	HIGH		READY
30424	30424	Coupe	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	HIGH	改款后Carrera 4宽体Coupe。	READY
30425	30425	Convertible	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	HIGH	改款后Carrera 4宽体敞篷车。	READY
30426	30426	Convertible	911 (997) facelift	997	2	EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	HIGH	改款后Carrera 4S宽体敞篷车。	READY
30427	30427	Targa	911 (997)	997	2	EU-PORSCHE-911-997-TARGA-4-01	HIGH	Targa 4物理外廓。	READY
30428	30428	Targa	911 (997)	997	2	EU-PORSCHE-911-997-TARGA-4S-01	HIGH	Targa 4S物理外廓。	READY
30429	30429	Sedan	626 III facelift	GD	4	EU-MAZDA-626-III-GD-SEDAN-4D-4WD-01	HIGH		READY
30431_3dr	30431	Hatchback	Clio I Phase II		3	EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	MEDIUM	三门物理分支。	READY
30431_5dr	30431	Hatchback	Clio I Phase II		5	EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	MEDIUM	五门物理分支。	READY
30432	30432	Wagon	Legacy IV facelift	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH		READY
30433	30433	Wagon	9-3 II facelift	YS3F	5	EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	HIGH		READY
30434	30434	Sedan	9-3 II facelift	YS3F	4	EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	HIGH		READY
30435	30435	Wagon	Legacy IV facelift	BP	5	EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	HIGH		READY
30436	30436	Hatchback	Justy IV		5	EU-SUBARU-JUSTY-IV-HATCHBACK-5D-01	HIGH		READY
30437_prefl	30437	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30437_facelift	30437	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30438_prefl	30438	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30438_facelift	30438	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30439_prefl	30439	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30439_facelift	30439	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30441_prefl	30441	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30441_facelift	30441	Hatchback	Octavia II facelift	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30442_prefl	30442	Wagon	Octavia II	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30442_facelift	30442	Wagon	Octavia II facelift	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30446_prefl	30446	MPV	Altea I	5P1	5	EU-SEAT-ALTEA-I-MPV-5D-01	HIGH	改款前物理外廓。	READY
30446_facelift	30446	MPV	Altea I facelift	5P1	5	EU-SEAT-ALTEA-I-MPV-FACELIFT-01	HIGH	改款后物理外廓。	READY
30453_kdss	30453	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-200-J200-SUV-KDSS-01	MEDIUM	KDSS悬架高度分支。	READY
30453_ahc	30453	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-200-J200-SUV-AHC-01	MEDIUM	AHC悬架高度分支。	READY
30469_3dr	30469	SUV	Land Cruiser Prado J120		3	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	HIGH	三门短轴物理分支。	READY
30469_5dr	30469	SUV	Land Cruiser Prado J120		5	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	HIGH	五门长轴物理分支。	READY
30470	30470	Wagon	XC70 II		5	EU-VOLVO-XC70-II-WAGON-5D-01	HIGH		READY
30471	30471	Sedan	Siena I facelift	178	4	EU-FIAT-SIENA-178-FACELIFT-SEDAN-4D-01	HIGH		READY
30473_swb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-SWB-01	MEDIUM	SWB底盘分支。	READY
30473_mwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-MWB-01	MEDIUM	MWB底盘分支。	READY
30473_mlwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	MEDIUM	加长MWB底盘分支。	READY
30473_lwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-LWB-01	MEDIUM	LWB底盘分支。	READY
30473_xlwb	30473	Pickup	Ducato III	X250		EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	MEDIUM	XLWB底盘分支。	READY
30474	30474	Sedan	Astra H		4	EU-OPEL-ASTRA-H-SEDAN-4D-01	HIGH		READY
30475_prefl	30475	Wagon	Omega A		5	EU-OPEL-OMEGA-A-CARAVAN-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30475_facelift	30475	Wagon	Omega A facelift		5	EU-OPEL-OMEGA-A-CARAVAN-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30476	30476	Coupe	LeBaron III	J	2	EU-CHRYSLER-LEBARON-III-J-COUPE-2D-01	MEDIUM		READY
30487_prefl	30487	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
30487_facelift	30487	Wagon	Focus III facelift	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
30495	30495	Coupe	Diablo VT 6.0		2	EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	HIGH		READY
30506	30506	Hatchback	1 Series E81	E81	3	EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	HIGH		READY
30514_singlecab	30514	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	MEDIUM	单排驾驶室物理分支。	READY
30514_spacecab	30514	Pickup	D-Max I		2	EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	MEDIUM	加长驾驶室物理分支。	READY
30514_doublecab	30514	Pickup	D-Max I		4	EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	MEDIUM	双排驾驶室物理分支。	READY
30524	30524	Sedan	CTS II		4	EU-CADILLAC-CTS-II-SEDAN-4D-01	HIGH		READY
30539	30539	MPV	Windstar II		5	EU-FORD-USA-WINDSTAR-II-MPV-01	HIGH		READY
30556_nkr81_narrow	30556	Pickup	Elf V	NKR81	2	EU-ISUZU-ELF-V-NKR81-CHASSIS-NARROWCAB-01	MEDIUM	NKR81窄体驾驶室底盘分支。	READY
30556_nkq81_wide	30556	Pickup	Elf V	NKQ81	2	EU-ISUZU-ELF-V-NKQ81-CHASSIS-WIDECAB-01	MEDIUM	NKQ81宽体驾驶室底盘分支。	READY
30565	30565	Convertible	Vanquish II		2	EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-2D-01	HIGH	Volante敞篷物理外廓。	READY
30569	30569	Wagon	Leon III ST	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	HIGH		READY
30637	30637	Wagon	Focus III	DYB	5	EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	HIGH		READY
30638_3dr	30638	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-02	HIGH	三门窄体物理分支。	READY
30638_5dr	30638	SUV	Grand Vitara I		5	EU-SUZUKI-GRAND-VITARA-I-SUV-5D-01	HIGH	五门物理分支。	READY
30661	30661	Sedan	Sunny B14	B14	4	EU-NISSAN-SUNNY-B14-SEDAN-4D-01	MEDIUM	生产区间对应B14四门物理车身。	READY
30685	30685	Sedan	Aurion I	XV40	4	EU-TOYOTA-AURION-I-XV40-SEDAN-4D-01	HIGH		READY
30688	30688	Sedan	Sebring III	JS	4	EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	HIGH		READY
30690	30690	Sedan	240	P244	4	EU-VOLVO-240-P244-SEDAN-4D-01	HIGH		READY
30691_prefl	30691	Wagon	A4 B8	8K5	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	改款前物理外廓。	READY
30691_facelift	30691	Wagon	A4 B8 facelift	8K5	5	EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	HIGH	改款后物理外廓。	READY
30692	30692	Pickup	Actyon Sports I		4	EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-4D-01	HIGH		READY
30693_prefl	30693	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
30693_facelift	30693	SUV	Q7 I facelift	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	改款后物理外廓。	READY
30694	30694	Coupe	Dino 2000		2	EU-FIAT-DINO-2000-COUPE-2D-01	HIGH		READY
30695	30695	Coupe	Dino 2400		2	EU-FIAT-DINO-2400-COUPE-2D-01	HIGH		READY
30696	30696	Convertible	Dino 2000 Spider		2	EU-FIAT-DINO-2000-SPIDER-2D-01	HIGH		READY
30697	30697	Convertible	Dino 2400 Spider		2	EU-FIAT-DINO-2400-SPIDER-2D-01	HIGH		READY
30698	30698	Sedan	Aurelia I	B10	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30699	30699	Sedan	Aurelia I	B15	4	EU-LANCIA-AURELIA-I-B15-LONG-BERLINA-4D-01	HIGH	B15长轴礼宾车外廓。	READY
30700	30700	Sedan	Aurelia I	B21	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30701	30701	Sedan	Aurelia I	B22	4	EU-LANCIA-AURELIA-I-BERLINA-4D-01	HIGH		READY
30702	30702	Sedan	Aurelia II	B12	4	EU-LANCIA-AURELIA-II-B12-BERLINA-4D-01	HIGH		READY
30703	30703	Coupe	Aurelia B20 II	B20	2	EU-LANCIA-AURELIA-B20-II-COUPE-2D-01	MEDIUM	80 PS对应B20第二系列外廓。	READY
30704	30704	Coupe	Aurelia B20 2500	B20	2	EU-LANCIA-AURELIA-B20-2500-COUPE-2D-01	HIGH		READY
30705	30705	Convertible	Aurelia B24 Spider	B24	2	EU-LANCIA-AURELIA-B24-SPIDER-2D-01	HIGH	Spider物理外廓。	READY
30706	30706	Convertible	Aurelia B24 Convertible	B24	2	EU-LANCIA-AURELIA-B24-CONVERTIBLE-2D-01	HIGH	Convertible物理外廓。	READY
30707	30707	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30708	30708	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30709	30709	Sedan	Flaminia Berlina		4	EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	HIGH		READY
30710	30710	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30711	30711	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30712	30712	Coupe	Flaminia Pininfarina Coupe		2	EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	HIGH		READY
30713	30713	Coupe	Flaminia GT Touring		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	HIGH		READY
30714	30714	Coupe	Flaminia GT Touring		2	EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	HIGH		READY
30715	30715	Sedan	Corolla X	E150	4	EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	HIGH		READY
30716	30716	Sedan	Corolla X	E150	4	EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	HIGH		READY
30717	30717	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30718	30718	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30719	30719	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
30720	30720	Wagon	Outback III	BP	5	EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	HIGH		READY
30722	30722	Hatchback	Shuma I		5	EU-KIA-SHUMA-I-HATCHBACK-5D-01	HIGH		READY
30723	30723	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30724	30724	Sedan	Flavia I Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	HIGH		READY
30725	30725	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30726	30726	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30727	30727	Coupe	Flavia I Pininfarina Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	HIGH		READY
30728	30728	Coupe	Flavia 2000 Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	HIGH		READY
30729	30729	Coupe	Flavia 2000 Coupe		2	EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	HIGH		READY
30730	30730	Coupe	2000 Coupe		2	EU-LANCIA-2000-COUPE-2D-01	HIGH	后期更名车型物理外廓。	READY
30731	30731	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30732	30732	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30733	30733	Sedan	Flavia I Berlina facelift		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30734	30734	Sedan	Flavia 2000 Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
30736	30736	Sedan	Flavia 2000 Berlina		4	EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3401-3500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-EVOLUTION-III-CE9A-SEDAN-4D-01	4310	1695	1420	Auto-Data Mitsubishi Lancer Evolution III	https://www.auto-data.net/en/mitsubishi-lancer-evolution-model-2861
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500	Auto-Data Ford Focus II Hatchback	https://www.auto-data.net/en/ford-focus-ii-hatchback-generation-1645
EU-FORD-FOCUS-II-SEDAN-01	4488	1840	1497	Auto-Data Ford Focus II Sedan	https://www.auto-data.net/en/ford-focus-ii-sedan-generation-1646
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503	Ford Focus 2008 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2008-Ford-Focus-UK.pdf
EU-SUZUKI-SX4-I-HATCHBACK-5D-01	4100	1730	1565	Auto-Data Suzuki SX4 I 1.6 DDiS	https://www.auto-data.net/en/suzuki-sx4-i-1.6-l-ddis-90hp-16571
EU-RENAULT-LAGUNA-I-PHASE-II-GRANDTOUR-WAGON-5D-01	4628	1752	1448	Automobile-Catalog Renault Laguna Wagon 2.0 8V	https://www.automobile-catalog.com/car/1998/2946080/renault_laguna_wagon_2_0_8v.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-3D-01	4480	1820	1810	Range Rover Classic 1994 brochure	https://autocatalogarchive.com/wp-content/uploads/2022/05/Range-Rover-1994-AU.pdf
EU-LAND-ROVER-RANGE-ROVER-I-SUV-5D-01	4480	1820	1810	Range Rover Classic 1994 brochure	https://autocatalogarchive.com/wp-content/uploads/2022/05/Range-Rover-1994-AU.pdf
EU-LANDWIND-CV9-I-MPV-5D-01	4410	1768	1640	Drive.Place Landwind Fashion CV9 I	https://landwind.drive.place/cv9/i/group_compactvan/405281
EU-FORD-TRANSIT-MK7-MPV-TOURNEO-SWB-LOWROOF-01	4863	1974	2070	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-LOWROOF-01	4863	1974	2067	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-SWB-MEDROOF-01	4863	1974	2383	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-LOWROOF-01	5230	1974	2056	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-MEDROOF-01	5230	1974	2371	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-MWB-HIGHROOF-01	5230	1974	2601	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-MEDROOF-01	5680	1974	2384	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-VAN-FWD-LWB-HIGHROOF-01	5680	1974	2599	Ford Transit 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-Transit-UK.pdf
EU-FORD-TRANSIT-MK7-MINIBUS-MWB-FWD-MEDROOF-01	5230	1974	2363	Ford People Movers 2009 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2009-Ford-People-Movers-UK.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-SWB-01	5114	1974	2020	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-MWB-02	5552	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-01	5931	1974	2031	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-LWB-02	6002	1974	2031	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-01	6319	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-CAB-EF-02	6390	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-01	5481	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-MWB-02	5552	1974	2030	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-01	5931	1974	2025	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-LWB-02	6002	1974	2025	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-01	6319	1974	2025	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-FORD-TRANSIT-MK7-CHASSIS-DOUBLE-CAB-EF-02	6390	1974	2025	Ford Transit Chassis Cab and Conversions brochure	https://globalvans.co.uk/avm/images/vans/FOTB/Ford%20Transit%20Chassis%20Cab%20and%20Conversions%20Brochure.pdf
EU-ALFA-ROMEO-159-FWD-SEDAN-4D-01	4660	1828	1422	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-ALFA-ROMEO-159-FWD-SPORTWAGON-WAGON-5D-01	4660	1828	1422	Alfa Romeo 159 official technical specifications	https://www.media.stellantis.com/uploads/uk/UK/2011/ALFA_ROMEO/SPECIFICATIONS/159_sportwagon_specs.pdf
EU-VW-POLO-III-6V2-CLASSIC-SEDAN-4D-01	4140	1640	1410	Volkswagen Newsroom Polo III vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-polo-3-profile-19149
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-COUPE-01	4435	1852	1310	Auto-Data Porsche 911 997 facelift Carrera 4	https://www.auto-data.net/en/porsche-911-997-facelift-2008-carrera-4-3.6-345hp-36759
EU-PORSCHE-911-997-FACELIFT-CARRERA-4-CONVERTIBLE-01	4435	1852	1310	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera 4	https://www.auto-data.net/en/porsche-911-cabriolet-997-facelift-2008-carrera-4-3.6-345hp-36739
EU-PORSCHE-911-997-FACELIFT-CARRERA-4S-CONVERTIBLE-01	4435	1852	1300	Auto-Data Porsche 911 Cabriolet 997 facelift Carrera 4S	https://www.auto-data.net/de/porsche-911-cabriolet-997-facelift-2008-carrera-4s-3.8-385hp-36741
EU-PORSCHE-911-997-TARGA-4-01	4427	1852	1310	Auto-Data Porsche 911 Targa 997 Targa 4	https://www.auto-data.net/en/porsche-911-targa-997-targa-4-3.6-325hp-36753
EU-PORSCHE-911-997-TARGA-4S-01	4427	1852	1300	Auto-Data Porsche 911 Targa 997 Targa 4S	https://www.auto-data.net/en/porsche-911-targa-997-targa-4s-3.8-355hp-36755
EU-MAZDA-626-III-GD-SEDAN-4D-4WD-01	4515	1690	1395	CarsGuide Mazda 626 1991 dimensions;Automobile-Catalog Mazda 626 2.2i GLX 4WD	https://www.carsguide.com.au/mazda/626/car-dimensions/1991;https://www.automobile-catalog.com/car/1991/1637060/mazda_626_2_2i_glx_4wd_cat.html
EU-RENAULT-CLIO-I-HATCHBACK-3D-PHASE-II-01	3709	1625	1395	Automobile-Catalog Renault Clio first generation	https://www.automobile-catalog.com/model/renault/clio_1gen.html
EU-RENAULT-CLIO-I-HATCHBACK-5D-PHASE-II-01	3709	1625	1395	Automobile-Catalog Renault Clio first generation	https://www.automobile-catalog.com/model/renault/clio_1gen.html
EU-SUBARU-LEGACY-IV-BP-WAGON-FACELIFT-01	4795	1730	1475	Auto-Data Legacy IV 2.5i;Auto-Data Legacy IV 2.0D	https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-2.5i-173hp-awd-34106;https://www.auto-data.net/en/subaru-legacy-iv-station-wagon-facelift-2006-2.0d-150hp-awd-34101
EU-SAAB-9-3-II-FACELIFT-WAGON-5D-01	4670	1762	1496	Saab 9-3 2008 brochure	https://www.auto-brochures.com/makes/Saab/9-3/Saab_int%209-3_2008.pdf
EU-SAAB-9-3-II-FACELIFT-SEDAN-4D-01	4647	1762	1450	Saab 9-3 2008 brochure	https://www.auto-brochures.com/makes/Saab/9-3/Saab_int%209-3_2008.pdf
EU-SUBARU-JUSTY-IV-HATCHBACK-5D-01	3610	1665	1540	Auto-Data Subaru Justy IV	https://www.auto-data.net/en/subaru-justy-iv-generation-3599
EU-FORD-FOCUS-III-TURNIER-WAGON-PREFL-01	4556	1823	1482	Ford Focus 2011 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2011-Ford-Focus-UK.pdf
EU-FORD-FOCUS-III-TURNIER-WAGON-FACELIFT-01	4560	1823	1492	Ford Focus 2015 UK brochure	https://xr793.com/wp-content/uploads/2022/09/2015-Ford-Focus-UK.pdf
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462	Skoda Octavia 2008 owner's manual	https://www.carmanualsonline.info/skoda-octavia-2008-2-g-1z-owner-s-manual/?srch=dimensions
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Skoda Octavia 2008 owner's manual	https://www.carmanualsonline.info/skoda-octavia-2008-2-g-1z-owner-s-manual/?srch=dimensions
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468	Skoda Octavia 2008 owner's manual	https://www.carmanualsonline.info/skoda-octavia-2008-2-g-1z-owner-s-manual/?srch=dimensions
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462	Skoda Octavia 2008 owner's manual	https://www.carmanualsonline.info/skoda-octavia-2008-2-g-1z-owner-s-manual/?srch=dimensions
EU-SEAT-ALTEA-I-MPV-5D-01	4280	1768	1568	SEAT Altea 2008 owner's manual technical data	https://www.carmanualsonline.info/seat-altea-2008-owner-s-manual
EU-SEAT-ALTEA-I-MPV-FACELIFT-01	4282	1768	1576	SEAT Altea 2008 owner's manual technical data	https://www.carmanualsonline.info/seat-altea-2008-owner-s-manual
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-KDSS-01	4950	1970	1910	Toyota Land Cruiser V8 official brochure	https://toyotasverigebroschyr.com/webbroschyr/bilbroschyr/lan_v8_bb_web.pdf
EU-TOYOTA-LAND-CRUISER-200-J200-SUV-AHC-01	4950	1970	1865	Toyota Land Cruiser V8 official brochure	https://toyotasverigebroschyr.com/webbroschyr/bilbroschyr/lan_v8_bb_web.pdf
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1865	Toyota 75 Years vehicle specification Land Cruiser Prado 120	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014203/index.html
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1855	Toyota 75 Years vehicle specification Land Cruiser Prado 120	https://www.toyota-global.com/company/history_of_toyota/75years/vehicle_lineage/car/id60014203/index.html
EU-VOLVO-XC70-II-WAGON-5D-01	4838	1861	1604	Volvo XC70 model year 2008 specifications	https://www.volvoclub.org.uk/press/volvo2008/cd/models/2008_XC70/specifications.htm
EU-FIAT-SIENA-178-FACELIFT-SEDAN-4D-01	4135	1634	1453	Automobile-Catalog Fiat Siena ELX 1.4	https://www.automobile-catalog.com/car/2007/734840/fiat_siena_elx_1_4.html
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254	Fiat Ducato X250 official technical brochure	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROFESSIONAL/SPECIFICATIONS/Ducato_technical_data.pdf
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254	Fiat Ducato X250 official technical brochure	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROFESSIONAL/SPECIFICATIONS/Ducato_technical_data.pdf
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254	Fiat Ducato X250 official technical brochure	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROFESSIONAL/SPECIFICATIONS/Ducato_technical_data.pdf
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254	Fiat Ducato X250 official technical brochure	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROFESSIONAL/SPECIFICATIONS/Ducato_technical_data.pdf
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254	Fiat Ducato X250 official technical brochure	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROFESSIONAL/SPECIFICATIONS/Ducato_technical_data.pdf
EU-OPEL-ASTRA-H-SEDAN-4D-01	4587	1753	1458	Auto-Data Opel Astra H Sedan 1.6i	https://www.auto-data.net/en/opel-astra-h-sedan-1.6i-16v-115hp-2340
EU-OPEL-OMEGA-A-CARAVAN-WAGON-PREFL-01	4742	1772	1530	Automobile-Catalog Opel Omega Caravan 24V 1990	https://www.automobile-catalog.com/car/1990/2467325/opel_omega_caravan_24v_automatic.html
EU-OPEL-OMEGA-A-CARAVAN-WAGON-FACELIFT-01	4768	1760	1530	Automobile-Catalog Opel Omega Caravan 24V 1991	https://www.automobile-catalog.com/car/1991/2468195/opel_omega_caravan_24v.html
EU-CHRYSLER-LEBARON-III-J-COUPE-2D-01	4696	1740	1295	Edmunds 1990 Chrysler LeBaron GT;Auto-Data Chrysler Le Baron Coupe 3.0 V6	https://www.edmunds.com/chrysler/le-baron/1990/st-10469/features-specs/;https://www.auto-data.net/en/chrysler-le-baron-coupe-3.0-i-v6-136hp-14702
EU-LAMBORGHINI-DIABLO-VT-6-0-COUPE-2D-01	4470	2040	1105	Autoevolution Lamborghini Diablo VT 6.0	https://www.autoevolution.com/cars/lamborghini-diablo-vt-60-2000.html
EU-BMW-1-SERIES-E81-HATCHBACK-3D-01	4239	1748	1421	Auto-Data BMW 1 Series E81/E87 facelift dimensions	https://www.auto-data.net/en/bmw-1-series-hatchback-5dr-e87-lci-facelift-2007-120i-170hp-9818
EU-ISUZU-D-MAX-I-SINGLE-CAB-PICKUP-2D-01	5030	1720	1635	Isuzu D-Max first-generation specifications	https://www.auto-data.net/en/isuzu-d-max-i-generation-2532
EU-ISUZU-D-MAX-I-SPACE-CAB-PICKUP-2D-01	5030	1800	1715	Isuzu D-Max first-generation specifications	https://www.auto-data.net/en/isuzu-d-max-i-generation-2532
EU-ISUZU-D-MAX-I-DOUBLE-CAB-PICKUP-4D-01	5035	1800	1735	Isuzu D-Max first-generation specifications	https://www.auto-data.net/en/isuzu-d-max-i-generation-2532
EU-CADILLAC-CTS-II-SEDAN-4D-01	4866	1842	1472	Auto-Data Cadillac CTS II	https://www.auto-data.net/en/cadillac-cts-ii-generation-2481
EU-FORD-USA-WINDSTAR-II-MPV-01	5103	1946	1679	Auto-Data Ford Windstar II 3.8 V6	https://www.auto-data.net/en/ford-windstar-ii-3.8-v6-200hp-automatic-8189
EU-ISUZU-ELF-V-NKR81-CHASSIS-NARROWCAB-01	4680	1690	1980	AUTODOC Isuzu Elf 5.2 Di Ktype 30556;JIKO Trading Isuzu Elf PB-NKR81A	https://www.autodoc.co.uk/car-parts/mounting-kit-charger-15070/isuzu/elf/elf-platform-chassis-nkr8-nkq8/30556-5-2-di;https://jikotrading.jp/isuzu-elf-cargo-pb-nkr81a/
EU-ISUZU-ELF-V-NKQ81-CHASSIS-WIDECAB-01	5985	1995	2265	AUTODOC Isuzu Elf 5.2 Di Ktype 30556;Isuzu N-Series official brochure 2011	https://www.autodoc.co.uk/car-parts/mounting-kit-charger-15070/isuzu/elf/elf-platform-chassis-nkr8-nkq8/30556-5-2-di;https://fuzionisuzu.co.za/wp-content/uploads/site/vehicles/download-isuzu-trucks-nseries-brochure-2.pdf
EU-ASTON-MARTIN-VANQUISH-II-VOLANTE-CONVERTIBLE-2D-01	4728	1912	1294	Aston Martin Vanquish brochure;Automobile Dimension Vanquish Volante	https://autocatalogarchive.com/wp-content/uploads/2016/07/Aston-Martin-Vanquish-2013.pdf;https://www.automobiledimension.com/model/aston-martin/vanquish-volante
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data SEAT Leon III ST	https://www.auto-data.net/en/seat-leon-model-1459
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-02	3865	1695	1685	Auto-Data Suzuki Grand Vitara 2.0 TD 3-door	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-2.0-td-3-dr-87hp-16596
EU-SUZUKI-GRAND-VITARA-I-SUV-5D-01	4195	1780	1685	Auto-Data Suzuki Grand Vitara 2.0 TD 5-door	https://www.auto-data.net/en/suzuki-grand-vitara-ft-gt-2.0-td-5-dr-87hp-16597
EU-NISSAN-SUNNY-B14-SEDAN-4D-01	4295	1690	1385	Automobile-Catalog Nissan Sunny B14 1997 Sedan	https://www.automobile-catalog.com/car/1997/2260025/nissan_sunny_1500_super_saloon.html
EU-TOYOTA-AURION-I-XV40-SEDAN-4D-01	4825	1820	1470	Auto-Data Toyota Aurion I XV40 3.5 V6;CarsGuide Toyota Aurion 2006 dimensions	https://www.auto-data.net/en/toyota-aurion-i-xv40-3.5-v6-277hp-automatic-3460;https://www.carsguide.com.au/toyota/aurion/car-dimensions/2006
EU-CHRYSLER-SEBRING-III-JS-SEDAN-4D-01	4842	1808	1498	Auto-Data Chrysler Sebring Sedan JS	https://www.auto-data.net/en/chrysler-sebring-sedan-js-generation-3271
EU-VOLVO-240-P244-SEDAN-4D-01	4785	1707	1427	Volvo 240 model specifications	https://www.volvoclub.org.uk/press/volvo1984/240.shtml
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 2.0 TDI	https://www.auto-data.net/en/audi-a4-avant-b8-8k-2.0-tdi-143hp-4330
EU-AUDI-A4-B8-AVANT-FACELIFT-WAGON-8K5-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 facelift	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-generation-4134
EU-SSANGYONG-ACTYON-SPORTS-I-PICKUP-4D-01	4965	1900	1755	Auto-Data SsangYong Actyon Sports 2.0 XDi	https://www.auto-data.net/en/ssangyong-actyon-sports-2.0xdi-141hp-15989
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737	Auto-Data Audi Q7 4L	https://www.auto-data.net/en/audi-q7-4l-generation-190
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737	Auto-Data Audi Q7 4L facelift	https://www.auto-data.net/en/audi-q7-4l-facelift-2009-generation-4229
EU-FIAT-DINO-2000-COUPE-2D-01	4510	1700	1290	Automobile-Catalog Fiat Dino Coupe 1967	https://www.automobile-catalog.com/car/1967/710660/fiat_dino_coupe.html
EU-FIAT-DINO-2400-COUPE-2D-01	4507	1696	1315	Automobile-Catalog Fiat Dino Coupe 1969	https://www.automobile-catalog.com/car/1969/710690/fiat_dino_coupe.html
EU-FIAT-DINO-2000-SPIDER-2D-01	4110	1710	1270	Automobile-Catalog Fiat Dino Spider 1967	https://www.automobile-catalog.com/car/1967/710645/fiat_dino_spider.html
EU-FIAT-DINO-2400-SPIDER-2D-01	4134	1710	1270	Automobile-Catalog Fiat Dino Spider 1969	https://www.automobile-catalog.com/car/1969/710675/fiat_dino_spider.html
EU-LANCIA-AURELIA-I-BERLINA-4D-01	4420	1560	1500	Automobile-Catalog Lancia Aurelia B10;Automobile-Catalog Lancia Aurelia B21;Automobile-Catalog Lancia Aurelia B22	https://www.automobile-catalog.com/car/1950/1373645/lancia_aurelia_b10.html;https://www.automobile-catalog.com/car/1951/1373675/lancia_aurelia_b21.html;https://www.automobile-catalog.com/car/1952/1373915/lancia_aurelia_b22.html
EU-LANCIA-AURELIA-I-B15-LONG-BERLINA-4D-01	4810	1595	1555	Automobile-Catalog Lancia Aurelia B15	https://www.automobile-catalog.com/car/1952/1373900/lancia_aurelia_b15.html
EU-LANCIA-AURELIA-II-B12-BERLINA-4D-01	4485	1560	1505	Automobile-Catalog Lancia Aurelia B12	https://www.automobile-catalog.com/car/1954/1373930/lancia_aurelia_b12.html
EU-LANCIA-AURELIA-B20-II-COUPE-2D-01	4290	1540	1360	Automobile-Catalog Lancia Aurelia B20 GT second series	https://www.automobile-catalog.com/car/1952/1373945/lancia_aurelia_b20_gt_2a_serie.html
EU-LANCIA-AURELIA-B20-2500-COUPE-2D-01	4370	1550	1360	Automobile-Catalog Lancia Aurelia B20 GT 2500	https://www.automobile-catalog.com/car/1954/1373975/lancia_aurelia_b20_gt_2500_4a_serie.html
EU-LANCIA-AURELIA-B24-SPIDER-2D-01	4200	1550	1300	Automobile-Catalog Lancia Aurelia B24 Spider	https://www.automobile-catalog.com/car/1954/1374020/lancia_aurelia_b24_spider.html
EU-LANCIA-AURELIA-B24-CONVERTIBLE-2D-01	4230	1555	1305	Automobile-Catalog Lancia Aurelia B24 Convertible	https://www.automobile-catalog.com/car/1956/1374035/lancia_aurelia_b24_america_convertible_2a_serie.html
EU-LANCIA-FLAMINIA-BERLINA-SEDAN-4D-01	4855	1750	1480	Automobile-Catalog Lancia Flaminia Berlina	https://www.automobile-catalog.com/car/1957/1374530/lancia_flaminia_berlina.html
EU-LANCIA-FLAMINIA-PININFARINA-COUPE-2D-01	4680	1740	1420	Automobile-Catalog Lancia Flaminia Coupe 3B;Automobile-Catalog Lancia Flaminia Coupe 3B 2.8	https://www.automobile-catalog.com/car/1962/1374695/lancia_flaminia_coupe_3b.html;https://www.automobile-catalog.com/car/1965/1374770/lancia_flaminia_coupe_3b_2_8.html
EU-LANCIA-FLAMINIA-TOURING-GT-COUPE-2D-01	4500	1680	1305	Automobile-Catalog Lancia Flaminia GT Touring;Automobile-Catalog Lancia Flaminia GT 3C Touring	https://www.automobile-catalog.com/car/1959/1374620/lancia_flaminia_gt_touring.html;https://www.automobile-catalog.com/car/1963/1374710/lancia_flaminia_gt_3c_touring.html
EU-TOYOTA-COROLLA-X-E150-SEDAN-4D-01	4540	1760	1470	Toyota Europe all-new Corolla press release;Auto-Data Toyota Corolla X E140/E150 1.6 VVT-i	https://newsroom.toyota.eu/all-new-corolla-setting-new-standards-in-its-class/;https://www.auto-data.net/en/toyota-corolla-x-e140-e150-1.6-i-16v-vvt-i-124hp-mmt-3298
EU-LANCIA-FLAVIA-I-BERLINA-EARLY-01	4580	1610	1510	Automobile-Catalog Lancia Flavia Berlina 1962;Automobile-Catalog Lancia Flavia Berlina 1.8 1966	https://www.automobile-catalog.com/car/1962/1375175/lancia_flavia_berlina.html;https://www.automobile-catalog.com/car/1966/1376345/lancia_flavia_berlina_1_8_carburatore.html
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545	Auto-Data Outback III 2.5i	https://www.auto-data.net/en/subaru-outback-iii-bl-bp-2.5i-173hp-awd-16146
EU-KIA-SHUMA-I-HATCHBACK-5D-01	4510	1720	1420	UltimateSpecs Kia Shuma I 1.6	https://www.ultimatespecs.com/car-specs/Kia/4305/Kia-Shuma-I-16-.html
EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-01	4485	1610	1350	Automobile-Catalog Lancia Flavia Coupe Pininfarina 1962;Automobile-Catalog Lancia Flavia Coupe 1.8 Iniezione 1966	https://www.automobile-catalog.com/car/1962/1375190/lancia_flavia_coupe_pininfarina.html;https://www.automobile-catalog.com/car/1966/1375400/lancia_flavia_coupe_pininfarina_1_8_iniezione.html
EU-LANCIA-FLAVIA-I-PININFARINA-COUPE-2000-01	4540	1605	1330	Automobile-Catalog Lancia Flavia Coupe 2000 Iniezione	https://www.automobile-catalog.com/car/1970/1375565/lancia_flavia_coupe_2000_iniezione.html
EU-LANCIA-2000-COUPE-2D-01	4555	1605	1330	Automobile-Catalog Lancia 2000 Coupe	https://www.automobile-catalog.com/car/1971/1376390/lancia_2000_coupe.html
EU-LANCIA-FLAVIA-I-BERLINA-LATE-01	4580	1610	1500	Automobile-Catalog Lancia Flavia 1800 Iniezione;Automobile-Catalog Lancia Flavia 2000 Iniezione	https://www.automobile-catalog.com/car/1970/1375475/lancia_flavia_1800_iniezione.html;https://www.automobile-catalog.com/car/1970/1375505/lancia_flavia_2000_iniezione.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3401-3500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.autodoc.co.uk/car-parts/mounting-kit-charger-15070/isuzu/elf/elf-platform-chassis-nkr8-nkq8/30556-5-2-di?utm_source=chatgpt.com "ISUZU Elf Platform / Chassis (NKR8_, NKQ8_) 5.2 Di Mounting ..."


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3401-3500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3401-3500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（4281 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2022 行）

