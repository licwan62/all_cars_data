# 任务：all 第 5601-5700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0057__215a9d2a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 5601-5700 行

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
all 第 5601-5700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5601-5700_ktype_dimension_mapping_final.tsv
- all_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409
EU-AUDI-A3-8V-CABRIOLET-FACELIFT-01	4423	1793	1409
EU-AUDI-A3-8V-SEDAN-FACELIFT-01	4458	1796	1416
EU-AUDI-A3-8V-SPORTBACK-FACELIFT-01	4313	1785	1426
EU-AUDI-A3-8Y-SEDAN-PREFL-01	4495	1816	1425
EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	4343	1816	1449
EU-AUDI-A5-F5-CABRIOLET-FACELIFT-01	4697	1846	1384
EU-AUDI-A5-F5-CABRIOLET-PREFL-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-COUPE-FACELIFT-01	4697	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497
EU-AUDI-Q5-FY-SUV-PREFL-01	4663	1893	1659
EU-AUDI-Q8-I-4MN-RS-Q8-SUV-01	5012	1998	1694
EU-AUDI-Q8-I-4MN-SQ8-SUV-01	5006	1995	1708
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555
EU-BMW-2-F45-ACTIVE-TOURER-MPV-PREFL-01	4342	1800	1555
EU-BMW-2-F46-GRAN-TOURER-MPV-FACELIFT-01	4568	1800	1641
EU-BMW-2-F46-GRAN-TOURER-MPV-PREFL-01	4556	1800	1641
EU-BMW-2-F87-M2-COMPETITION-COUPE-01	4461	1854	1410
EU-BMW-2-F87-M2-CS-COUPE-01	4461	1871	1414
EU-BMW-5-E28-M535I-SEDAN-01	4620	1700	1397
EU-BMW-5-E60-SEDAN-FACELIFT-01	4841	1846	1468
EU-BMW-5-E60-SEDAN-PREFL-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-01	4907	1860	1462
EU-BMW-5-F90-M5-SEDAN-COMPETITION-01	4966	1903	1469
EU-BMW-5-G30-520D-MHEV-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-520D-MHEV-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483
EU-BMW-5-G30-530E-SEDAN-PREFL-01	4936	1868	1483
EU-BMW-5-G30-545E-XDRIVE-SEDAN-FACELIFT-01	4936	1868	1483
EU-BMW-5-G30-SEDAN-01	4936	1868	1466
EU-BMW-5-G30-SEDAN-M550I-01	4962	1868	1467
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-XDRIVE-01	4942	1868	1498
EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	4447	1821	1598
EU-BMW-X1-F48-SDRIVE20D-SUV-PREFL-01	4439	1821	1598
EU-BMW-X1-F48-XDRIVE25E-SUV-FACELIFT-01	4447	1821	1582
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637
EU-CITROEN-C3-AIRCROSS-II-VAN-01	4154	1756	1597
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525
EU-DS-DS3-CROSSBACK-I-SUV-01	4118	1791	1534
EU-DS-DS5-FACELIFT-HATCHBACK-01	4530	1871	1504
EU-DS-DS7-CROSSBACK-I-SUV-01	4573	1895	1620
EU-DS-DS7-CROSSBACK-I-SUV-PREFL-01	4573	1895	1620
EU-FORD-PUMA-II-SUV-STANDARD-01	4186	1805	1536
EU-FORD-PUMA-II-SUV-STLINE-01	4207	1805	1537
EU-FORD-PUMA-II-SUV-TITANIUM-01	4186	1805	1537
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	5359	1860	1821
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-RAPTOR-01	5363	2028	1873
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	5282	1860	1815
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	5359	1860	1848
EU-FORD-RANGER-III-TKE-PICKUP-REGULAR-CAB-01	5282	1860	1800
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-LIMITED-01	5359	1860	1810
EU-FORD-RANGER-III-TKE-PICKUP-SUPER-CAB-STANDARD-01	5282	1860	1804
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485
EU-LADA-LARGUS-I-F90-CNG-VAN-01	4470	1750	1650
EU-LADA-LARGUS-I-R90-CNG-WAGON-01	4470	1750	1670
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645
EU-LEXUS-NX-I-PREFL-SUV-01	4630	1845	1645
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414
EU-MINI-MINI-F56-HATCHBACK-COOPER-SE-01	3850	1727	1432
EU-MINI-MINI-F56-HATCHBACK-JCW-GP-01	3879	1762	1420
EU-MINI-MINI-F56-HATCHBACK-ONE-01	3821	1727	1414
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415
EU-MINI-MINI-F57-CONVERTIBLE-ONE-01	3821	1727	1415
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-01	3958	1683	1432
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-PREFL-01	3714	1683	1414
EU-MINI-MINI-R58-COUPE-COOPER-01	3728	1683	1378
EU-MINI-MINI-R58-COUPE-COOPER-S-01	3734	1683	1384
EU-OPEL-MOKKA-B-ELECTRIC-SUV-01	4151	1791	1532
EU-OPEL-MOKKA-X-J13-SUV-01	4275	1781	1658
EU-PEUGEOT-508-II-R8-FASTBACK-01	4750	1847	1404
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420
EU-PORSCHE-PANAMERA-971-HATCHBACK-01	5049	1937	1423
EU-PORSCHE-PANAMERA-971-TURBO-HATCHBACK-01	5049	1937	1427
EU-PORSCHE-PANAMERA-II-971-GTS-HATCHBACK-01	5053	1937	1417
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-4-01	5049	1937	1428
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-HATCHBACK-5D-PREFL-01	4263	1816	1459
EU-SEAT-LEON-III-5F-ST-CUPRA-300-4DRIVE-WAGON-01	4548	1816	1431
EU-SEAT-LEON-III-5F-ST-WAGON-FACELIFT-01	4549	1816	1454
EU-SEAT-LEON-III-5F-ST-WAGON-PREFL-01	4535	1816	1451
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1799	1442
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450
EU-SEAT-TARRACO-I-KN2-SUV-01	4735	1839	1674
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531
EU-SKODA-OCTAVIA-I-1U5-COMBI-FACELIFT-01	4513	1731	1457
EU-SKODA-OCTAVIA-III-5E-FACELIFT-HATCHBACK-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-5E-FACELIFT-WAGON-01	4667	1814	1465
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469
EU-SKODA-SUPERB-III-3V3-HATCHBACK-PREFL-01	4861	1864	1468
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477
EU-SKODA-SUPERB-III-3V5-WAGON-PREFL-01	4856	1864	1477
EU-SUBARU-OUTBACK-III-BP-WAGON-FACELIFT-01	4730	1770	1545
EU-SUBARU-OUTBACK-IV-BR-WAGON-FACELIFT-01	4790	1820	1605
EU-SUBARU-OUTBACK-IV-BR-WAGON-PREFL-01	4775	1820	1605
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
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652
EU-VW-GOLF-VIII-CD-VARIANT-WAGON-01	4633	1789	1498
EU-VW-GOLF-VIII-GTI-HATCHBACK-01	4287	1789	1478
EU-VW-GOLF-VIII-HATCHBACK-01	4284	1789	1456
EU-VW-POLO-III-6V5-PANEL-VAN-FACELIFT-01	4137	1640	1459
EU-VW-POLO-III-6V5-PANEL-VAN-PREFL-01	4137	1640	1433
EU-VW-POLO-IV-9N3-HATCHBACK-3D-01	3916	1650	1467
EU-VW-POLO-IV-9N3-HATCHBACK-5D-01	3916	1650	1467
EU-VW-POLO-V-602-SEDAN-FACELIFT-01	4390	1699	1467
EU-VW-POLO-V-6R-VAN-3D-PREFL-01	3970	1682	1484
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-01	4067	1751	1438
EU-VW-POLO-VI-HATCHBACK-TGI-01	4053	1751	1446
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461
EU-VW-TIGUAN-II-SUV-AWD-01	4486	1839	1673
EU-VW-TIGUAN-II-SUV-FWD-01	4486	1839	1654
EU-VW-UP-I-FACELIFT-E-UP-HATCHBACK-01	3600	1645	1492
EU-VW-UP-I-FACELIFT-GTI-HATCHBACK-01	3600	1641	1504

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	5	530 E Plug-in-hybrid	Kombi	Heckantrieb	Benzin/Elektro	200	272	Nov 2020	-	2024-03-01	142152
BMW	5	530 E Plug-in-hybrid Xdrive	Stufenheck	Allrad	Benzin/Elektro	200	272	Jul 2020	Jun 2023	2024-03-01	142153
BMW	5	530 E Plug-in-hybrid Xdrive	Kombi	Allrad	Benzin/Elektro	200	272	Nov 2020	-	2024-03-01	142155
BMW	X1	Sdrive 20 I	SUV	Frontantrieb	Benzin	131	178	Nov 2020	Jun 2022	2024-03-01	142156
BMW	X1	Xdrive 20 I	SUV	Allrad	Benzin	131	178	Nov 2020	Jun 2022	2024-03-01	142157
BMW	2	220 I	Großraumlimousine	Frontantrieb	Benzin	131	178	Nov 2020	Oct 2021	2024-03-01	142158
BMW	2	225 XE Plug-in-hybrid	Großraumlimousine	Allrad	Benzin/Elektro	162	220	Nov 2020	Oct 2021	2024-03-01	142160
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142161
Mini	Mini	Cooper S All4	Kombi	Allrad	Benzin	131	178	Nov 2020	-	2024-03-01	142162
BMW	1	128 TI	Schrägheck	Frontantrieb	Benzin	180	245	Nov 2020	-	2024-03-01	142173
DS	Ds	1.6 Puretech 225	Stufenheck	Frontantrieb	Benzin	165	224	Sep 2020	Aug 2022	2025-12-01	142175
Citroën	C4 iii	1.2 Puretech 130	Schrägheck	Frontantrieb	Benzin	96	131	Oct 2020	-	2025-12-01	142176
Citroën	C4 iii	1.5 Bluehdi 130	Schrägheck	Frontantrieb	Diesel	96	131	Oct 2020	-	2024-03-01	142177
Ford	Puma	1.5 ST Ecoboost	SUV	Frontantrieb	Benzin	147	200	Nov 2020	-	2024-03-01	142178
Dacia	Spring	EV	Schrägheck	Frontantrieb	Elektro	33	45	Oct 2020	-	2024-03-01	142185
VW	Polo	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Jul 2020	-	2024-03-01	142189
Hyundai	I20 iii	1.2	Schrägheck	Frontantrieb	Benzin	62	84	Aug 2020	-	2024-03-01	142190
Hyundai	I20 iii	1.0 T-gdi	Schrägheck	Frontantrieb	Benzin	74	101	Aug 2020	-	2024-03-01	142191
KIA	Picanto iii	1.2 MPI	Schrägheck	Frontantrieb	Benzin	62	84	Jul 2020	-	2024-03-01	142192
Peugeot	508 ii	PSE Hybrid4 360	Schrägheck	Allrad	Benzin/Elektro	265	360	Jan 2021	-	2024-03-01	142195
Peugeot	508 sw ii	PSE Hybrid4 360	Kombi	Allrad	Benzin/Elektro	265	360	Jan 2021	-	2024-03-01	142197
Audi	Q5	50 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	210	286	Jun 2020	-	2024-03-01	142198
Seat	Leon	1.4 TSI E-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	150	204	May 2020	-	2024-03-01	142222
Seat	Leon	1.4 TSI E-hybrid	Kombi	Frontantrieb	Benzin/Elektro	150	204	May 2020	-	2024-03-01	142223
Seat	Leon	1.5 TGI CNG	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Aug 2020	-	2024-03-01	142224
Skoda	Enyaq iv	50	SUV	Heckantrieb	Elektro	109	148	Oct 2020	-	2024-03-01	142228
Skoda	Enyaq iv	60	SUV	Heckantrieb	Elektro	132	179	Oct 2020	-	2024-03-01	142229
Skoda	Enyaq iv	80	SUV	Heckantrieb	Elektro	150	204	Oct 2020	-	2024-03-01	142230
Lexus	Nx	300h	SUV	Frontantrieb	Benzin/Elektro	145	197	Nov 2014	-	2024-03-01	142231
Seat	Arona	1.0 TSI	SUV	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	142232
Skoda	Octavia	2.0 TSI RS	Schrägheck	Frontantrieb	Benzin	180	245	Mar 2020	-	2024-03-01	142233
Skoda	Octavia	1.4 TSI RS IV	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Jun 2020	-	2024-03-01	142234
Skoda	Octavia	1.5 TSI G-tec	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Jun 2020	-	2024-03-01	142236
Subaru	Outback	2.5 AWD	Kombi	Allrad	Benzin	129	175	Jul 2020	-	2024-07-01	142237
Skoda	Octavia	2.0 TSI RS	Kombi	Frontantrieb	Benzin	180	245	Mar 2020	-	2024-03-01	142238
Skoda	Octavia	1.4 TSI RS IV	Kombi	Frontantrieb	Benzin/Elektro	180	245	Jun 2020	-	2024-03-01	142240
Skoda	Octavia	1.0 TSI E-tec	Kombi	Frontantrieb	Benzin/Elektro	81	110	Jun 2020	-	2024-03-01	142241
Skoda	Octavia	1.0 TSI E-tec	Schrägheck	Frontantrieb	Benzin/Elektro	81	110	Jun 2020	-	2024-03-01	142242
Skoda	Superb iii	2.0 TDI 4X4	Kombi	Allrad	Diesel	147	200	Sep 2020	Jun 2024	2025-06-01	142250
VW	Id.4	Performance	SUV	Heckantrieb	Elektro	150	204	May 2020	-	2024-03-01	142253
VW	Up!	1	Schrägheck	Frontantrieb	Benzin	48	65	Aug 2020	Nov 2023	2024-11-01	142255
Audi	Q5	45 Tfsi Mild Hybrid Quattro	SUV	Allrad	Benzin/Elektro	195	265	Aug 2020	-	2024-03-01	142256
Audi	A3	30 G-tron	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	96	131	Jul 2020	-	2024-03-01	142257
Audi	A5	50 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	210	286	Aug 2020	-	2024-03-01	142258
Porsche	Panamera	4.0 GTS	Kombi	Allrad	Benzin	353	480	Aug 2020	Dec 2023	2024-08-01	142261
Porsche	Panamera	4.0 Turbo S	Kombi	Allrad	Benzin	463	630	Aug 2020	Dec 2023	2024-08-01	142262
Hyundai	I20 iii	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	74	101	Aug 2020	-	2024-03-01	142263
Hyundai	I20 iii	1.0 T-gdi Hybrid 48V	Schrägheck	Frontantrieb	Benzin/Elektro	88	120	Aug 2020	-	2024-03-01	142264
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	90	122	Jul 2020	Apr 2024	2025-06-01	142270
Cupra	Formentor	2.0 TSI 4drive	SUV	Allrad	Benzin	228	310	Jul 2020	-	2024-03-01	142277
Cupra	Leon	1.4 E-hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Sep 2020	-	2025-02-03	142280
Cupra	Leon	E-hybrid	Kombi	Frontantrieb	Benzin/Elektro	180	245	Sep 2020	-	2024-03-01	142281
Lada	Largus	1.6	Kombi	Frontantrieb	Benzin	62	84	Mar 2012	-	2024-03-01	142288
Lada	Largus	1.6	Kombi	Frontantrieb	Benzin	64	87	Apr 2016	Mar 2021	2024-03-01	142289
Lada	Largus	1.6 CNG	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	69	94	Nov 2018	-	2024-03-01	142290
Lada	Largus	1.6	Kombi	Frontantrieb	Benzin	77	105	Mar 2012	-	2024-03-01	142291
Land Rover	110/127	2.3 4X4	Geländewagen geschlossen	Allrad	Benzin	52	71	Jun 1984	Aug 1987	2024-03-01	142293
VW	Golf viii	2.0 GTI Clubsport	Schrägheck	Frontantrieb	Benzin	221	300	Oct 2020	-	2024-03-01	142300
Suzuki	Across	2.5 Hybrid	SUV	Allrad	Benzin/Elektro	225	306	Jun 2020	-	2024-03-01	142342
Toyota	Proace	Electric	Kasten	Frontantrieb	Elektro	100	136	Sep 2020	Dec 2023	2024-08-01	142396
Skoda	Superb iii	2.0 TDI	Schrägheck	Frontantrieb	Diesel	147	200	Sep 2020	Jun 2024	2025-06-01	142397
Skoda	Superb iii	2.0 TDI	Kombi	Frontantrieb	Diesel	147	200	Sep 2020	Jun 2024	2025-06-01	142398
Opel	Mokka	1.2	SUV	Frontantrieb	Benzin	74	101	Oct 2020	-	2024-03-01	142410
Opel	Mokka	1.2	SUV	Frontantrieb	Benzin	96	131	Oct 2020	-	2024-03-01	142411
Ford	Ranger	3.2 Tdci 4X4	Pick-up	Allrad	Diesel	147	200	Apr 2011	-	2025-11-01	142415
Audi	A1	30 Tfsi	Schrägheck	Frontantrieb	Benzin	81	110	Sep 2020	Jun 2022	2024-03-01	142418
Audi	A3	40 Tfsie	Schrägheck	Frontantrieb	Benzin/Elektro	150	204	Jun 2020	-	2024-03-01	142419
Citroën	C3 aircross i	1.5 Bluehdi 110	SUV	Frontantrieb	Diesel	81	110	Oct 2020	-	2025-11-01	142421
Audi	A3	30 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	81	110	Jun 2020	-	2024-03-01	142422
Audi	A3	30 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	81	110	Jun 2020	-	2024-03-01	142423
Audi	A3	S3 Tfsi Quattro	Stufenheck	Allrad	Benzin	228	310	Jun 2020	-	2025-11-01	142424
Audi	A3	S3 Tfsi Quattro	Schrägheck	Allrad	Benzin	228	310	Jun 2020	-	2025-11-01	142425
Audi	A6 allroad c8	40 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	150	204	Sep 2020	-	2024-03-01	142426
Audi	Q8	55 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	280	381	Oct 2020	-	2024-03-01	142432
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142433
Audi	Q8	60 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	340	462	Oct 2020	-	2024-03-01	142435
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142437
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142438
Skoda	Kamiq	1.0 TSI	SUV	Frontantrieb	Benzin	81	110	Aug 2020	-	2024-03-01	142440
Skoda	Scala	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Aug 2020	-	2024-03-01	142441
VW	Caddy v	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	75	102	Sep 2020	-	2025-11-01	142442
VW	Caddy v	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	90	122	Sep 2020	-	2025-11-01	142443
VW	Caddy v	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2020	-	2025-11-01	142444
VW	Caddy v	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	75	102	Sep 2020	-	2025-11-01	142445
VW	Caddy v	2.0 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	90	122	Sep 2020	-	2025-11-01	142446
BMW	1	118 I	Schrägheck	Frontantrieb	Benzin	100	136	Nov 2020	-	2024-03-01	142450
Seat	Tarraco	2.0 TDI 4drive	SUV	Allrad	Diesel	147	200	Jul 2020	May 2024	2025-06-01	142456
Cupra	Formentor	1.5 TSI	SUV	Frontantrieb	Benzin	110	150	Nov 2020	-	2024-03-01	142458
Fiat	500e	Elektro 3+1	Schrägheck	Frontantrieb	Elektro	87	118	Oct 2020	-	2024-03-01	142459
Skoda	Octavia	2.0 TDI RS 4X4	Kombi	Allrad	Diesel	147	200	Jul 2020	-	2024-03-01	142460
Fiat	500e	Elektro	Schrägheck	Frontantrieb	Elektro	70	95	Oct 2020	-	2024-03-01	142461
Skoda	Octavia	2.0 TDI RS	Kombi	Frontantrieb	Diesel	147	200	Jul 2020	-	2024-03-01	142462
Skoda	Octavia	2.0 TDI RS 4X4	Schrägheck	Allrad	Diesel	147	200	Jul 2020	-	2024-03-01	142463
Skoda	Octavia	2.0 TDI RS	Schrägheck	Frontantrieb	Diesel	147	200	Jul 2020	-	2024-03-01	142464
Volvo	Xc40	Recharge AWD	SUV	Allrad	Elektro	300	408	Nov 2020	-	2024-03-01	142465
Fiat	500e	Elektro	Cabriolet	Frontantrieb	Elektro	70	95	Oct 2020	-	2024-03-01	142467
Fiat	500e	Elektro	Cabriolet	Frontantrieb	Elektro	87	118	Oct 2020	-	2024-03-01	142468
BMW	2	220 I	Coupe	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142469
BMW	2	218 I	Coupe	Frontantrieb	Benzin	100	136	Nov 2020	-	2024-03-01	142470
BMW	2	220 I	Großraumlimousine	Frontantrieb	Benzin	131	178	Nov 2020	-	2024-03-01	142471


--- Round 1 / 首次发送 ---
## 更新点

* 已完成本批 100 个输入 Ktype 的首轮映射，`142231` 根据其覆盖 2014–2021 年第一代 Lexus NX 的边界，拆分为改款前、改款后两个物理外廓行。([ALCAR HERINGRAD GMBH][1])
* 本轮复用已有尺寸组 36 个，首次创建并闭合尺寸组 23 个；Octavia RS/RS iV、Audi S3、Opel Mokka 汽油版和 Fiat 500e 等专组均已按直接规格闭合。([斯柯达故事板][2])
* 精确 Ktype 交叉结果已确认 `142433=MINI F56 三门`、`142437=MINI F55 五门`；Caddy 五个 Ktype 已定位到乘用 MPV 与厢式车系列，但轴距和单一车身代码仍待闭合。([eBay UK][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：88，覆盖已闭合 Ktype 87 个
* PENDING 映射行：13，涉及 Ktype 13 个
* 当前引用尺寸组：59 个
* 本轮首次创建尺寸组：23 个
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142152	142152	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI Touring；动力差异不改变外廓。	READY
142153	142153	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive 仍属同一轿车外廓。	READY
142155	142155	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI Touring；xDrive 不改变外廓。	READY
142156	142156	SUV	X1 F48 LCI	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	HIGH	F48 LCI 标准车身；动力差异不改变外廓。	READY
142157	142157	SUV	X1 F48 LCI	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	HIGH	F48 LCI 标准车身；驱动形式不改变外廓。	READY
142158	142158	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer。	READY
142160	142160	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer；插混不改变外廓。	READY
142161	142161	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman 外廓。	READY
142162	142162	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman；ALL4 不改变外廓。	READY
142173	142173	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	F40 五门掀背外廓。	READY
142175	142175	Sedan	DS 9 I		4	EU-DS-DS9-I-SEDAN-01	HIGH	DS 9 四门轿车外廓。	READY
142176	142176	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41 五门掀背外廓。	READY
142177	142177	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41 五门掀背外廓。	READY
142178	142178	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-ST-01	HIGH	ST 专属保险杠与车身高度，单独建组。	READY
142185	142185	Hatchback	Spring I	DBG	5	EU-DACIA-SPRING-I-DBG-HATCHBACK-01	HIGH	Spring I 五门电动掀背外廓。	READY
142189	142189	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1 五门 TSI 标准外廓。	READY
142190	142190	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	BC3 五门掀背外廓。	READY
142191	142191	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	BC3 五门掀背外廓。	READY
142192	142192	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH	JA 五门掀背外廓。	READY
142195	142195	Hatchback	508 II	R8	5		MEDIUM	PSE Fastback 专属外廓与既有普通 Fastback 组三维存在冲突，待闭合专组。	PENDING: PSE Fastback 三维冲突未解决
142197	142197	Wagon	508 II SW	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH	PSE SW 外廓与既有 508 II Wagon 组一致。	READY
142198	142198	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-FY-SUV-FACELIFT-01	HIGH	FY 改款后 Q5 标准 SUV 外廓。	READY
142222	142222	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	未标注 FR，关联标准车身高度组。	READY
142223	142223	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	未标注 FR，关联标准 Sportstourer 组。	READY
142224	142224	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	TGI 动力不改变 KL1 标准外廓。	READY
142228	142228	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142229	142229	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142230	142230	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142231_prefl	142231	SUV	NX I	AZ10	5	EU-LEXUS-NX-I-PREFL-SUV-01	HIGH	Ktype 覆盖第一代 NX；改款前物理外廓。	READY
142231_facelift	142231	SUV	NX I	AZ10	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	Ktype 覆盖第一代 NX；改款后物理外廓。	READY
142232	142232	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH	KJ7 五门 SUV 外廓。	READY
142233	142233	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 掀背专属车身高度。	READY
142234	142234	Hatchback	Octavia IV RS iV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-IV-HATCHBACK-01	HIGH	RS iV 掀背因插混离地与高度差异单独建组。	READY
142236	142236	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX 标准五门掀背外廓。	READY
142237	142237	Wagon	Outback V	BS	5		MEDIUM	Jul 2020 欧洲市场代际与改款边界待直接来源确认。	PENDING: 代际边界及三维未闭合
142238	142238	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS Combi 专属车身高度。	READY
142240	142240	Wagon	Octavia IV RS iV	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-IV-WAGON-01	HIGH	RS iV Combi 因插混离地与高度差异单独建组。	READY
142241	142241	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH	NX 标准 Combi 外廓。	READY
142242	142242	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX 标准五门掀背外廓。	READY
142250	142250	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	3V5 改款后 Combi 外廓。	READY
142253	142253	SUV	ID.4 I	E21	5	EU-VW-ID4-I-E21-SUV-RWD-01	HIGH	E21 后驱 Performance 标准外廓。	READY
142255	142255	Hatchback	up! I facelift				LOW	汽油版普通 up!；既有索引仅含 e-up!/GTI，门数及标准高度组待确认。	PENDING: 门数及标准汽油版尺寸组未闭合
142256	142256	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-FY-SUV-FACELIFT-01	HIGH	FY 改款后 Q5 标准 SUV 外廓。	READY
142257	142257	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142258	142258	Hatchback	A5 F5 Sportback facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门掀背改款后外廓。	READY
142261	142261	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	HIGH	GTS Sport Turismo 专属高度。	READY
142262	142262	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo S Sport Turismo 专属高度。	READY
142263	142263	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	48V 动力不改变 BC3 外廓。	READY
142264	142264	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	48V 动力不改变 BC3 外廓。	READY
142270	142270	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-FACELIFT-01	HIGH	AD1 改款后前驱标准 SUV 外廓。	READY
142277	142277	SUV	Formentor I	KM7	5	EU-CUPRA-FORMENTOR-I-KM7-SUV-VZ310-01	HIGH	VZ 310 4Drive 专属保险杠与车身高度。	READY
142280	142280	Hatchback	CUPRA Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-EHYBRID-HATCHBACK-01	HIGH	CUPRA e-Hybrid 五门掀背外廓。	READY
142281	142281	Wagon	CUPRA Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-EHYBRID-WAGON-01	HIGH	CUPRA e-Hybrid Sportstourer 外廓。	READY
142288	142288	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；汽油动力不改变外廓。	READY
142289	142289	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；发动机差异不改变外廓。	READY
142290	142290	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 CNG Wagon 外廓。	READY
142291	142291	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；发动机差异不改变外廓。	READY
142293	142293	SUV	Land Rover 110/127				LOW	输入型号同时覆盖 110/127；已知存在不同轴距与外廓，待确认具体分支后拆行。	PENDING: 110/127 分支及三维未闭合
142300	142300	Hatchback	Golf VIII GTI Clubsport	CD1	5		MEDIUM	Clubsport 专属外廓与高度需和既有普通 GTI 组直接核对。	PENDING: Clubsport 专组三维未闭合
142342	142342	SUV	Across I		5	EU-SUZUKI-ACROSS-I-SUV-01	HIGH	Across I 五门插混 SUV 外廓。	READY
142396	142396	Van	Proace II	MDZ4			LOW	Electric Van 存在 Compact/Medium/Long 车长分支；待确认该 Ktype 覆盖边界后拆行。	PENDING: 多车长分支未闭合
142397	142397	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	3V3 改款后掀背外廓。	READY
142398	142398	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	3V5 改款后 Combi 外廓。	READY
142410	142410	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GASOLINE-SUV-01	HIGH	汽油版高度与累计 Electric 组不同，按冲突规则新建组。	READY
142411	142411	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GASOLINE-SUV-01	HIGH	汽油版高度与累计 Electric 组不同，按冲突规则新建组。	READY
142415	142415	Pickup	Ranger III	TKE			MEDIUM	精确 Ktype 已确认 TKE 3.2 TDCi 4x4，但 cab/bed 分支未闭合。	PENDING: cab/bed 物理分支未闭合
142418	142418	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	GB 五门 Sportback 外廓。	READY
142419	142419	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142421	142421	SUV	C3 Aircross I facelift		5		MEDIUM	2021 外观改款组三维与不含镜宽度待直接来源闭合。	PENDING: 改款组三维未闭合
142422	142422	Sedan	A3 8Y Sedan	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH	8Y 四门 Sedan 改款前标准外廓。	READY
142423	142423	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142424	142424	Sedan	S3 8Y Sedan	8YS	4	EU-AUDI-A3-8Y-S3-SEDAN-PREFL-01	HIGH	S3 Sedan 专属长度与高度。	READY
142425	142425	Hatchback	S3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-S3-SPORTBACK-PREFL-01	HIGH	S3 Sportback 专属长度与高度。	READY
142426	142426	Wagon	A6 allroad C8	4K	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH	C8 allroad Wagon 外廓。	READY
142432	142432	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH	4MN 标准 Q8 外廓；PHEV 动力不改变外廓。	READY
142433	142433	Hatchback	MINI Hatch F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	HIGH	精确 Ktype 对应 F56 三门。	READY
142435	142435	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH	4MN 标准 Q8 外廓；PHEV 动力不改变外廓。	READY
142437	142437	Hatchback	MINI Hatch F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH	精确 Ktype 对应 F55 五门；Cooper S 与既有 F55 外廓一致。	READY
142438	142438	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57 双门敞篷外廓。	READY
142440	142440	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH	NW4 五门 SUV 外廓。	READY
142441	142441	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH	NW1 五门掀背外廓。	READY
142442	142442	MPV	Caddy V				LOW	精确 Ktype 属 Caddy V MPV（SBB/SBJ 系列）；SWB/LWB 与单一车身代码未闭合。	PENDING: 轴距及单一车身代码未闭合
142443	142443	MPV	Caddy V				LOW	精确 Ktype 属 Caddy V MPV（SBB/SBJ 系列）；SWB/LWB 与单一车身代码未闭合。	PENDING: 轴距及单一车身代码未闭合
142444	142444	Van	Caddy V				LOW	精确 Ktype 属 Caddy V Box Body/MPV（SBA/SBH 系列）；SWB/LWB 与单一车身代码未闭合。	PENDING: 轴距及单一车身代码未闭合
142445	142445	Van	Caddy V				LOW	精确 Ktype 属 Caddy V Box Body/MPV（SBA/SBH 系列）；SWB/LWB 与单一车身代码未闭合。	PENDING: 轴距及单一车身代码未闭合
142446	142446	Van	Caddy V				LOW	精确 Ktype 属 Caddy V Box Body/MPV（SBA/SBH 系列）；SWB/LWB 与单一车身代码未闭合。	PENDING: 轴距及单一车身代码未闭合
142450	142450	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	F40 五门掀背外廓。	READY
142456	142456	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH	KN2 五门 SUV 外廓。	READY
142458	142458	SUV	Formentor I	KM7	5	EU-CUPRA-FORMENTOR-I-KM7-SUV-15TSI-01	HIGH	1.5 TSI 前驱标准外廓。	READY
142459	142459	Hatchback	500e I	332	4	EU-FIAT-500E-I-332-HATCHBACK-3PLUS1-01	HIGH	3+1 非对称附加后门，单独物理车身分支。	READY
142460	142460	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS 4x4 Combi 与 RS Combi 外廓一致。	READY
142461	142461	Hatchback	500e I	332	3	EU-FIAT-500E-I-332-HATCHBACK-3D-01	HIGH	标准三门 Hatchback 外廓。	READY
142462	142462	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS Combi 专属车身高度。	READY
142463	142463	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 4x4 掀背与 RS 掀背外廓一致。	READY
142464	142464	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 掀背专属车身高度。	READY
142465	142465	SUV	XC40 I	536	5	EU-VOLVO-XC40-I-SUV-01	HIGH	Recharge AWD 动力不改变 XC40 标准外廓。	READY
142467	142467	Convertible	500e I Cabrio	332	2	EU-FIAT-500E-I-332-CONVERTIBLE-01	HIGH	双门 Cabrio 外廓。	READY
142468	142468	Convertible	500e I Cabrio	332	2	EU-FIAT-500E-I-332-CONVERTIBLE-01	HIGH	电池功率差异不改变 Cabrio 外廓。	READY
142469	142469	Coupe	2 Series Gran Coupe F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱四门 Gran Coupé，对应 F44。	READY
142470	142470	Coupe	2 Series Gran Coupe F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱四门 Gran Coupé，对应 F44。	READY
142471	142471	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DS-DS9-I-SEDAN-01	4934	1855	1460	DS Automobiles DS 9 official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds9pricesandspecs-6172ca39a3822.pdf
EU-FORD-PUMA-II-SUV-ST-01	4226	1805	1533	Ford Puma ST official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2020/09/Puma-ST/documents/Ford_Puma-ST_2020_ProvisionalTechSpec_200922.pdf
EU-DACIA-SPRING-I-DBG-HATCHBACK-01	3734	1579	1516	Dacia Spring official brochure	https://cdn.group.renault.com/dac/pt/catalogos/spring/catalogo_spring_motorizacoes.pdf
EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	4040	1775	1450	Hyundai Motor Europe all-new i20 technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20201012_all-new_i20/20201001_Technical_Data_i20_v2_clean.pdf
EU-AUDI-Q5-FY-SUV-FACELIFT-01	4682	1893	1662	Audi Q5 official technical data	https://press.audi.co.uk/assets/documents/original/1890-AudiQ540TDIquattroStronicUKTechnicalDataNovember2020.pdf
EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	4649	1879	1616	ŠKODA ENYAQ iV official technical specifications	https://cdn.skoda-storyboard.com/2021/03/TD-ENYAQ-iV-EN.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	4702	1829	1457	ŠKODA OCTAVIA RS official technical specifications	https://cdn.skoda-storyboard.com/2020/11/TD-OCTAVIA-RS-en.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-IV-HATCHBACK-01	4702	1829	1476	ŠKODA OCTAVIA RS iV official technical specifications	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-RS-iV-en.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	4702	1829	1455	ŠKODA OCTAVIA COMBI RS official technical specifications	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-COMBI-RS-en.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-IV-WAGON-01	4702	1829	1474	ŠKODA OCTAVIA COMBI RS iV official technical specifications	https://cdn.skoda-storyboard.com/2020/09/TD-OCTAVIA-COMBI-RS-iV-en.pdf
EU-VW-ID4-I-E21-SUV-RWD-01	4584	1852	1634	Volkswagen ID.4 official technical data	https://www.volkswagen-newsroom.com/en/the-id4-from-volkswagen-15712/technical-data-of-the-id4-15724
EU-VW-TIGUAN-II-AD1-SUV-FWD-FACELIFT-01	4509	1839	1675	Volkswagen New Tiguan official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/new-tiguan/vw_tiguan_brochure_dec_2020.pdf
EU-CUPRA-FORMENTOR-I-KM7-SUV-VZ310-01	4450	1839	1511	CUPRA Formentor official technical data	https://www.cupraofficial.mt/cars/cupra-range/formentor
EU-CUPRA-LEON-IV-KL1-EHYBRID-HATCHBACK-01	4398	1799	1467	CUPRA Leon official press kit	https://www.seat-cupra-mediacenter.com/CUPRA-Brand/presskits/CUPRA-Leon-Dinamic/Chassis
EU-CUPRA-LEON-IV-KL8-EHYBRID-WAGON-01	4657	1799	1463	CUPRA Leon Sportstourer official technical data	https://www.seat-cupra-mediacenter.com/content/dam/seat-media-center/models-all-brands/cupra-models/cupra-leon-sportstourer/technical-data/Technical_Data_CUPRA_Leon_Sportstourer.pdf
EU-SUZUKI-ACROSS-I-SUV-01	4635	1855	1690	Suzuki ACROSS official technical data	https://www.suzuki.at/presse/auto/pressemeldungen/across/2022/2022_12_22_ACROSS%20Minor%20Change%202022/Suzuki%20ACROSS_Technische%20Daten_Dez22.pdf
EU-OPEL-MOKKA-B-GASOLINE-SUV-01	4151	1791	1531	Opel Mokka official price and specification guide	https://www.opel.ie/content/dam/opel/ireland/brochure-library/brochures/passenger-cars/WebMokkaPriceEquipGuide.pdf
EU-AUDI-A3-8Y-S3-SEDAN-PREFL-01	4504	1816	1415	Audi S3 Sedan official technical data	https://uploads.audi-mediacenter.com/system/production/uploaded_files/17325/file/7997db0b7ad899a8c650ee29584d1d8953804c45/etd_Audi_S3_Sedan.pdf
EU-AUDI-A3-8Y-S3-SPORTBACK-PREFL-01	4351	1816	1438	Audi S3 Sportback official technical data	https://www.audi-mediacenter.com/system/production/uploaded_files/17318/file/7334d9a7986e08895ccb6ee8a490f603249ede05/td_Audi_S3_Sportback_228_kW.pdf?1598606430=&disposition=attachment
EU-CUPRA-FORMENTOR-I-KM7-SUV-15TSI-01	4446	1839	1520	CUPRA Formentor official technical data	https://www.cupraofficial.mt/cars/cupra-range/formentor
EU-FIAT-500E-I-332-HATCHBACK-3PLUS1-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
EU-FIAT-500E-I-332-HATCHBACK-3D-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
EU-FIAT-500E-I-332-CONVERTIBLE-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
```

## 下一步优先处理

1. 优先闭合 Caddy V、Proace Electric、Ranger 和 Land Rover 110/127 的轴距、驾驶室或车长分支，可一次消除 8 条 PENDING。
2. 随后处理 Peugeot 508 PSE Fastback、Golf GTI Clubsport、普通汽油 up! 和 C3 Aircross facelift 的专属尺寸组。
3. 最后确认 `142237` Subaru Outback 在 2020 年欧洲市场的代际边界及对应三维。

推进信号：CONTINUE

[1]: https://alcar.azurewebsites.net/media/in5ca0qs/sparewheels-fitment-list-members-gedeelte.xlsx "https://alcar.azurewebsites.net/media/in5ca0qs/sparewheels-fitment-list-members-gedeelte.xlsx"
[2]: https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-RS-iV-en.pdf "https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-RS-iV-en.pdf"
[3]: https://www.ebay.co.uk/itm/257649716051?hash=item3bfd1eab53%3Ag%3AWtgAAeSw8KNqakjt&itmmeta=01KYQX076GG996K4CB8KKZQDS2&itmprp=enc%3AAQALAAAA4DKQclQvzFwZQpmMrsO4LuqvcBS8hI6fflyVrFTs7zi27ql8q6VxJAySe4SiWW8pcPDNPxWpDOTXlVLdWdEEIlDEjjrWpTmItDz7W5UocY887yILA0lRTo8w5JEoCjITmNxIo2EXMtjhbfjE6Q22kUnoQEofV1CwWyX%2Fn6T4L2TDabGLFKRBGilVdwQN2KUQSmR2IfaXIwuacS3y6JW4tCIMQ592%2FlQvqyICgUNOqZPi6tSt1kXRv2Fb82jgsgrSkOBjS1KwN7KWSEQf9kmN384NLpmBvlSOxaSHMkMAugP7%7Ctkp%3ABk9SR7DzgP31Zw&utm_source=chatgpt.com "MINI Cooper S Sport 2021 28k Manual FSH CarPlay Full Service ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5601-5700_ktype_dimension_mapping_final.tsv
- all_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已将 `142442–142446` 按官方车身代码拆分为标准轴距与 Maxi 长轴距分支：乘用版对应 `SBB/SBJ`，厢式版对应 `SBA/SBH`；五个基础 PENDING 行已由十个派生 READY 行替换。([AIC德国汽车部件][1])
* 已闭合 `142195` Peugeot 508 PSE Fastback 专属尺寸组。([标致英国][2])
* 已闭合 `142300` Golf VIII GTI Clubsport 专属外廓尺寸组。

## 当前批次进度

* READY 映射：100
* PENDING 映射：6
* 映射总行数：106
* 已确认尺寸组：65
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142195	142195	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-PSE-FASTBACK-01	HIGH	PSE Fastback专属外廓。	READY
142300	142300	Hatchback	Golf VIII	CD	5	EU-VW-GOLF-VIII-CD-GTI-CLUBSPORT-HATCHBACK-01	HIGH	Clubsport专属保险杠、扰流件及车身高度。	READY
142442_swb	142442	MPV	Caddy V	SBB	5	EU-VW-CADDY-V-SBB-MPV-SWB-01	HIGH	标准轴距乘用车身分支。	READY
142442_lwb	142442	MPV	Caddy V	SBJ	5	EU-VW-CADDY-V-SBJ-MPV-LWB-01	HIGH	Maxi长轴距乘用车身分支。	READY
142443_swb	142443	MPV	Caddy V	SBB	5	EU-VW-CADDY-V-SBB-MPV-SWB-01	HIGH	标准轴距乘用车身分支。	READY
142443_lwb	142443	MPV	Caddy V	SBJ	5	EU-VW-CADDY-V-SBJ-MPV-LWB-01	HIGH	Maxi长轴距乘用车身分支。	READY
142444_swb	142444	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142444_lwb	142444	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
142445_swb	142445	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142445_lwb	142445	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
142446_swb	142446	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142446_lwb	142446	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-508-II-R8-PSE-FASTBACK-01	4750	1859	1410	Peugeot 508 PSE official model page	https://www.peugeot.it/gamma-modelli/nuova-508-peugeot-sport-engineered.html
EU-VW-GOLF-VIII-CD-GTI-CLUBSPORT-HATCHBACK-01	4295	1789	1465	ADAC vehicle catalogue; Volkswagen Golf GTI Clubsport official media information	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/vw/golf/viii/316714/;https://www.volkswagen-newsroom.com/en/press-releases/the-new-golf-gti-clubsport-world-premiere-of-the-300-ps-flagship-gti-model-6496/download
EU-VW-CADDY-V-SBB-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy Life official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-life/caddy_life-brochure.pdf
EU-VW-CADDY-V-SBJ-MPV-LWB-01	4853	1855	1800	Volkswagen Caddy Life official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-life/caddy_life-brochure.pdf
EU-VW-CADDY-V-SBA-VAN-SWB-01	4500	1855	1856	Volkswagen Caddy Cargo official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-cargo/caddy-cargo-brochure.pdf
EU-VW-CADDY-V-SBH-VAN-LWB-01	4853	1855	1860	Volkswagen Caddy Cargo official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-cargo/caddy-cargo-brochure.pdf
```

## 下一步优先处理

1. 优先闭合 `142396` Proace Electric 的 Compact、Medium、Long 车长分支。
2. 集中处理 `142415` Ranger 驾驶室分支和 `142293` Land Rover 110/127 轴距分支。
3. 最后处理 `142237` Outback、`142255` up! 和 `142421` C3 Aircross facelift。

推进信号：CONTINUE

[1]: https://aic-germany.de/en/product-catalogue/14293?utm_source=chatgpt.com "Combination Rear Light"
[2]: https://www.peugeot.co.uk/content/peugeot/worldwide/uk/en/index/models/508-peugeot-sport-engineered.html?utm_source=chatgpt.com "Peugeot 508 PSE PLUG-IN-HYBRID | Peugeot UK"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5601-5700_ktype_dimension_mapping_final.tsv
- all_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 `142396` Proace Electric 的 Compact、Medium、Long 三个车长分支；Compact、Medium 复用既有尺寸组，仅首次创建 Long FWD 尺寸组。([丰田欧洲新闻中心][1])
* 已闭合 `142415` Ranger 3.2 TDCi Double Cab 的标准、Limited、Wildtrak 外廓分支，全部复用既有尺寸组。
* 已闭合 `142237` Outback VI BT 的两种官方车高分支；闭合 `142255` 汽油版 up! 三门/五门分支；`142421` 确认为第一代 C3 Aircross 并复用既有组。([AUTODOC][2])
* 当前仅剩 `142293` Land Rover 110/127 的两个轴距物理分支尚未闭合。

## 当前批次进度

* READY 映射：111
* PENDING 映射：1
* 映射总行数：112
* 已确认尺寸组：69
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142237_1670h	142237	Wagon	Outback VI	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-1670H-01	HIGH	官方规格中的1670 mm车高物理分支。	READY
142237_1675h	142237	Wagon	Outback VI	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-1675H-01	HIGH	官方规格中的1675 mm车高物理分支。	READY
142255_3dr	142255	Hatchback	up! I facelift		3	EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	HIGH	三门汽油版物理分支。	READY
142255_5dr	142255	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	HIGH	五门汽油版物理分支。	READY
142396_compact	142396	Van	Proace II			EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	HIGH	Compact电动厢式车分支。	READY
142396_medium	142396	Van	Proace II			EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	HIGH	Medium电动厢式车分支。	READY
142396_long	142396	Van	Proace II			EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-FWD-01	HIGH	Long电动厢式车分支。	READY
142415_standard	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab标准外廓分支。	READY
142415_limited	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited外廓分支。	READY
142415_wildtrak	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	HIGH	Double Cab Wildtrak外廓分支。	READY
142421	142421	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH	第一代2R/2C车身系列。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SUBARU-OUTBACK-VI-BT-WAGON-1670H-01	4870	1875	1670	Subaru Europe Outback official specifications	https://www.subaru.eu/docs/default-source/media-documents-gallery/spec-sheets/24outback_spec_ec.pdf
EU-SUBARU-OUTBACK-VI-BT-WAGON-1675H-01	4870	1875	1675	Subaru Europe Outback official specifications	https://www.subaru.eu/docs/default-source/media-documents-gallery/spec-sheets/24outback_spec_ec.pdf
EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	3600	1641	1504	UltimateSpecs Volkswagen up! facelift 1.0 65HP	https://www.ultimatespecs.com/car-specs/Volkswagen/121290/Volkswagen-Up%21-2017-5-doors-10-65HP.html
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-FWD-01	5309	1920	1940	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
```

## 下一步优先处理

1. 仅处理 `142293`：分别闭合 Land Rover 110 与 127 封闭式车身的准确长宽高及直接来源。
2. 该项闭合后即达到 `PENDING=0`，下一轮直接进行一次机械检查并输出两张最终完整 TSV、两个指定下载链接及 `推进信号：COMPLETE`。

推进信号：CONTINUE

[1]: https://newsroom.toyota.eu/toyota-further-expands-electric-line-up-choice-with-new-proace-and-proace-verso-electric/ "Toyota further expands electric line-up choice with new PROACE and PROACE Verso Electric"
[2]: https://www.autodoc.hu/jarmu-alkatreszek/fekbetet-10130/subaru/outback/outback/142237-2-5-awd?utm_source=chatgpt.com "SUBARU Outback VI (BT) 2.5 AWD Fékbetét (175 LE Benzin )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_5601-5700_ktype_dimension_mapping_final.tsv
- all_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已将最后一个 `142293` 闭合为 `110 Station Wagon` 与 `127 Crew Cab` 两个物理分支；One Two Seven 为 127 英寸轴距、四门 crew-cab 车型，110 Station Wagon 的三维也已闭合。([汽车目录][1])
* 已完成轻量机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、引用全部闭合、尺寸及来源字段非空、无孤立尺寸组。
* 已创建两个指定文件名的最终 TSV。

## 当前批次进度

* 输入 Ktype：100
* 最终映射行：113
* READY 映射：113
* PENDING 映射：0
* 最终尺寸组：77

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
142152	142152	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI Touring；动力差异不改变外廓。	READY
142153	142153	Sedan	5 Series G30 LCI	G30	4	EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	HIGH	G30 LCI xDrive 仍属同一轿车外廓。	READY
142155	142155	Wagon	5 Series G31 LCI	G31	5	EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	HIGH	G31 LCI Touring；xDrive 不改变外廓。	READY
142156	142156	SUV	X1 F48 LCI	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	HIGH	F48 LCI 标准车身；动力差异不改变外廓。	READY
142157	142157	SUV	X1 F48 LCI	F48	5	EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	HIGH	F48 LCI 标准车身；驱动形式不改变外廓。	READY
142158	142158	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer。	READY
142160	142160	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer；插混不改变外廓。	READY
142161	142161	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman 外廓。	READY
142162	142162	Wagon	MINI Clubman F54	F54	6	EU-MINI-MINI-F54-CLUBMAN-WAGON-01	HIGH	F54 Clubman；ALL4 不改变外廓。	READY
142173	142173	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	F40 五门掀背外廓。	READY
142175	142175	Sedan	DS 9 I		4	EU-DS-DS9-I-SEDAN-01	HIGH	DS 9 四门轿车外廓。	READY
142176	142176	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41 五门掀背外廓。	READY
142177	142177	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41 五门掀背外廓。	READY
142178	142178	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-ST-01	HIGH	ST 专属保险杠与车身高度，单独建组。	READY
142185	142185	Hatchback	Spring I	DBG	5	EU-DACIA-SPRING-I-DBG-HATCHBACK-01	HIGH	Spring I 五门电动掀背外廓。	READY
142189	142189	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-HATCHBACK-TSI-01	HIGH	AW1 五门 TSI 标准外廓。	READY
142190	142190	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	BC3 五门掀背外廓。	READY
142191	142191	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	BC3 五门掀背外廓。	READY
142192	142192	Hatchback	Picanto III	JA	5	EU-KIA-PICANTO-III-JA-HATCHBACK-01	HIGH	JA 五门掀背外廓。	READY
142195	142195	Hatchback	508 II	R8	5	EU-PEUGEOT-508-II-R8-PSE-FASTBACK-01	HIGH	PSE Fastback专属外廓。	READY
142197	142197	Wagon	508 II SW	R8	5	EU-PEUGEOT-508-II-WAGON-01	HIGH	PSE SW 外廓与既有 508 II Wagon 组一致。	READY
142198	142198	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-FY-SUV-FACELIFT-01	HIGH	FY 改款后 Q5 标准 SUV 外廓。	READY
142222	142222	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	未标注 FR，关联标准车身高度组。	READY
142223	142223	Wagon	Leon IV Sportstourer	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	未标注 FR，关联标准 Sportstourer 组。	READY
142224	142224	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	TGI 动力不改变 KL1 标准外廓。	READY
142228	142228	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142229	142229	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142230	142230	SUV	Enyaq iV I	5AZ	5	EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	HIGH	Enyaq iV 标准 SUV 外廓。	READY
142231_prefl	142231	SUV	NX I	AZ10	5	EU-LEXUS-NX-I-PREFL-SUV-01	HIGH	Ktype 覆盖第一代 NX；改款前物理外廓。	READY
142231_facelift	142231	SUV	NX I	AZ10	5	EU-LEXUS-NX-I-FACELIFT-SUV-01	HIGH	Ktype 覆盖第一代 NX；改款后物理外廓。	READY
142232	142232	SUV	Arona I	KJ7	5	EU-SEAT-ARONA-I-KJ7-SUV-01	HIGH	KJ7 五门 SUV 外廓。	READY
142233	142233	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 掀背专属车身高度。	READY
142234	142234	Hatchback	Octavia IV RS iV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-IV-HATCHBACK-01	HIGH	RS iV 掀背因插混离地与高度差异单独建组。	READY
142236	142236	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX 标准五门掀背外廓。	READY
142237_1670h	142237	Wagon	Outback VI	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-1670H-01	HIGH	官方规格中的1670 mm车高物理分支。	READY
142237_1675h	142237	Wagon	Outback VI	BT	5	EU-SUBARU-OUTBACK-VI-BT-WAGON-1675H-01	HIGH	官方规格中的1675 mm车高物理分支。	READY
142238	142238	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS Combi 专属车身高度。	READY
142240	142240	Wagon	Octavia IV RS iV	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-IV-WAGON-01	HIGH	RS iV Combi 因插混离地与高度差异单独建组。	READY
142241	142241	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-NX-WAGON-01	HIGH	NX 标准 Combi 外廓。	READY
142242	142242	Hatchback	Octavia IV	NX3	5	EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	HIGH	NX 标准五门掀背外廓。	READY
142250	142250	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	3V5 改款后 Combi 外廓。	READY
142253	142253	SUV	ID.4 I	E21	5	EU-VW-ID4-I-E21-SUV-RWD-01	HIGH	E21 后驱 Performance 标准外廓。	READY
142255_3dr	142255	Hatchback	up! I facelift		3	EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	HIGH	三门汽油版物理分支。	READY
142255_5dr	142255	Hatchback	up! I facelift		5	EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	HIGH	五门汽油版物理分支。	READY
142256	142256	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-FY-SUV-FACELIFT-01	HIGH	FY 改款后 Q5 标准 SUV 外廓。	READY
142257	142257	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142258	142258	Hatchback	A5 F5 Sportback facelift	F5	5	EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	HIGH	Sportback 五门掀背改款后外廓。	READY
142261	142261	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	HIGH	GTS Sport Turismo 专属高度。	READY
142262	142262	Wagon	Panamera II Sport Turismo	971	5	EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	HIGH	Turbo S Sport Turismo 专属高度。	READY
142263	142263	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	48V 动力不改变 BC3 外廓。	READY
142264	142264	Hatchback	i20 III	BC3	5	EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	HIGH	48V 动力不改变 BC3 外廓。	READY
142270	142270	SUV	Tiguan II facelift	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FWD-FACELIFT-01	HIGH	AD1 改款后前驱标准 SUV 外廓。	READY
142277	142277	SUV	Formentor I	KM7	5	EU-CUPRA-FORMENTOR-I-KM7-SUV-VZ310-01	HIGH	VZ 310 4Drive 专属保险杠与车身高度。	READY
142280	142280	Hatchback	CUPRA Leon IV	KL1	5	EU-CUPRA-LEON-IV-KL1-EHYBRID-HATCHBACK-01	HIGH	CUPRA e-Hybrid 五门掀背外廓。	READY
142281	142281	Wagon	CUPRA Leon IV Sportstourer	KL8	5	EU-CUPRA-LEON-IV-KL8-EHYBRID-WAGON-01	HIGH	CUPRA e-Hybrid Sportstourer 外廓。	READY
142288	142288	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；汽油动力不改变外廓。	READY
142289	142289	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；发动机差异不改变外廓。	READY
142290	142290	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 CNG Wagon 外廓。	READY
142291	142291	Wagon	Largus I	R90	5	EU-LADA-LARGUS-I-R90-CNG-WAGON-01	HIGH	R90 Wagon；发动机差异不改变外廓。	READY
142293_110	142293	SUV	Land Rover One Ten	LDH	5	EU-LAND-ROVER-110-LDH-SUV-01	HIGH	110 Station Wagon物理分支。	READY
142293_127	142293	Pickup	Land Rover One Two Seven	LDH	4	EU-LAND-ROVER-127-LDH-PICKUP-CREW-CAB-01	HIGH	127 Crew Cab物理分支。	READY
142300	142300	Hatchback	Golf VIII	CD	5	EU-VW-GOLF-VIII-CD-GTI-CLUBSPORT-HATCHBACK-01	HIGH	Clubsport专属保险杠、扰流件及车身高度。	READY
142342	142342	SUV	Across I		5	EU-SUZUKI-ACROSS-I-SUV-01	HIGH	Across I 五门插混 SUV 外廓。	READY
142396_compact	142396	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	HIGH	Compact电动厢式车分支。	READY
142396_medium	142396	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	HIGH	Medium电动厢式车分支。	READY
142396_long	142396	Van	Proace II	MDZ4		EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-FWD-01	HIGH	Long电动厢式车分支。	READY
142397	142397	Hatchback	Superb III facelift	3V3	5	EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	HIGH	3V3 改款后掀背外廓。	READY
142398	142398	Wagon	Superb III facelift	3V5	5	EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	HIGH	3V5 改款后 Combi 外廓。	READY
142410	142410	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GASOLINE-SUV-01	HIGH	汽油版高度与累计 Electric 组不同，按冲突规则新建组。	READY
142411	142411	SUV	Mokka B		5	EU-OPEL-MOKKA-B-GASOLINE-SUV-01	HIGH	汽油版高度与累计 Electric 组不同，按冲突规则新建组。	READY
142415_standard	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	HIGH	Double Cab标准外廓分支。	READY
142415_limited	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	HIGH	Double Cab Limited外廓分支。	READY
142415_wildtrak	142415	Pickup	Ranger III	TKE	4	EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	HIGH	Double Cab Wildtrak外廓分支。	READY
142418	142418	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	GB 五门 Sportback 外廓。	READY
142419	142419	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142421	142421	SUV	C3 Aircross I		5	EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	HIGH	第一代2R/2C车身系列。	READY
142422	142422	Sedan	A3 8Y Sedan	8YS	4	EU-AUDI-A3-8Y-SEDAN-PREFL-01	HIGH	8Y 四门 Sedan 改款前标准外廓。	READY
142423	142423	Hatchback	A3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	HIGH	8Y Sportback 改款前标准外廓。	READY
142424	142424	Sedan	S3 8Y Sedan	8YS	4	EU-AUDI-A3-8Y-S3-SEDAN-PREFL-01	HIGH	S3 Sedan 专属长度与高度。	READY
142425	142425	Hatchback	S3 8Y Sportback	8YA	5	EU-AUDI-A3-8Y-S3-SPORTBACK-PREFL-01	HIGH	S3 Sportback 专属长度与高度。	READY
142426	142426	Wagon	A6 allroad C8	4K	5	EU-AUDI-A6-ALLROAD-C8-WAGON-01	HIGH	C8 allroad Wagon 外廓。	READY
142432	142432	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH	4MN 标准 Q8 外廓；PHEV 动力不改变外廓。	READY
142433	142433	Hatchback	MINI Hatch F56	F56	3	EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	HIGH	精确 Ktype 对应 F56 三门。	READY
142435	142435	SUV	Q8 I	4MN	5	EU-AUDI-Q8-I-4MN-SUV-01	HIGH	4MN 标准 Q8 外廓；PHEV 动力不改变外廓。	READY
142437	142437	Hatchback	MINI Hatch F55	F55	5	EU-MINI-MINI-F55-HATCHBACK-ONE-01	HIGH	精确 Ktype 对应 F55 五门；Cooper S 与既有 F55 外廓一致。	READY
142438	142438	Convertible	MINI Convertible F57	F57	2	EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	HIGH	F57 双门敞篷外廓。	READY
142440	142440	SUV	Kamiq I	NW4	5	EU-SKODA-KAMIQ-NW4-SUV-01	HIGH	NW4 五门 SUV 外廓。	READY
142441	142441	Hatchback	Scala I	NW1	5	EU-SKODA-SCALA-I-NW1-HATCHBACK-01	HIGH	NW1 五门掀背外廓。	READY
142442_swb	142442	MPV	Caddy V	SBB	5	EU-VW-CADDY-V-SBB-MPV-SWB-01	HIGH	标准轴距乘用车身分支。	READY
142442_lwb	142442	MPV	Caddy V	SBJ	5	EU-VW-CADDY-V-SBJ-MPV-LWB-01	HIGH	Maxi长轴距乘用车身分支。	READY
142443_swb	142443	MPV	Caddy V	SBB	5	EU-VW-CADDY-V-SBB-MPV-SWB-01	HIGH	标准轴距乘用车身分支。	READY
142443_lwb	142443	MPV	Caddy V	SBJ	5	EU-VW-CADDY-V-SBJ-MPV-LWB-01	HIGH	Maxi长轴距乘用车身分支。	READY
142444_swb	142444	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142444_lwb	142444	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
142445_swb	142445	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142445_lwb	142445	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
142446_swb	142446	Van	Caddy V	SBA		EU-VW-CADDY-V-SBA-VAN-SWB-01	HIGH	标准轴距厢式车身分支。	READY
142446_lwb	142446	Van	Caddy V	SBH		EU-VW-CADDY-V-SBH-VAN-LWB-01	HIGH	Maxi长轴距厢式车身分支。	READY
142450	142450	Hatchback	1 Series F40	F40	5	EU-BMW-1-F40-HATCHBACK-01	HIGH	F40 五门掀背外廓。	READY
142456	142456	SUV	Tarraco I	KN2	5	EU-SEAT-TARRACO-I-KN2-SUV-01	HIGH	KN2 五门 SUV 外廓。	READY
142458	142458	SUV	Formentor I	KM7	5	EU-CUPRA-FORMENTOR-I-KM7-SUV-15TSI-01	HIGH	1.5 TSI 前驱标准外廓。	READY
142459	142459	Hatchback	500e I	332	4	EU-FIAT-500E-I-332-HATCHBACK-3PLUS1-01	HIGH	3+1 非对称附加后门，单独物理车身分支。	READY
142460	142460	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS 4x4 Combi 与 RS Combi 外廓一致。	READY
142461	142461	Hatchback	500e I	332	3	EU-FIAT-500E-I-332-HATCHBACK-3D-01	HIGH	标准三门 Hatchback 外廓。	READY
142462	142462	Wagon	Octavia IV RS	NX5	5	EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	HIGH	RS Combi 专属车身高度。	READY
142463	142463	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 4x4 掀背与 RS 掀背外廓一致。	READY
142464	142464	Hatchback	Octavia IV RS	NX3	5	EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	HIGH	RS 掀背专属车身高度。	READY
142465	142465	SUV	XC40 I	536	5	EU-VOLVO-XC40-I-SUV-01	HIGH	Recharge AWD 动力不改变 XC40 标准外廓。	READY
142467	142467	Convertible	500e I Cabrio	332	2	EU-FIAT-500E-I-332-CONVERTIBLE-01	HIGH	双门 Cabrio 外廓。	READY
142468	142468	Convertible	500e I Cabrio	332	2	EU-FIAT-500E-I-332-CONVERTIBLE-01	HIGH	电池功率差异不改变 Cabrio 外廓。	READY
142469	142469	Coupe	2 Series Gran Coupe F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱四门 Gran Coupé，对应 F44。	READY
142470	142470	Coupe	2 Series Gran Coupe F44	F44	4	EU-BMW-2-F44-GRAN-COUPE-01	HIGH	前驱四门 Gran Coupé，对应 F44。	READY
142471	142471	MPV	2 Series Active Tourer F45 LCI	F45	5	EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	HIGH	F45 LCI 五门 Active Tourer。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_5601-5700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G31-520D-MHEV-WAGON-FACELIFT-01	4963	1868	1498	BMW 5 Series Touring official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318750EN/463132
EU-BMW-5-G30-530E-SEDAN-FACELIFT-01	4963	1868	1483	BMW 5 Series Sedan official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0318749EN/463130
EU-BMW-X1-F48-SDRIVE20D-SUV-FACELIFT-01	4447	1821	1598	BMW X1 official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0298480EN/the-new-bmw-x1
EU-BMW-2-F45-ACTIVE-TOURER-MPV-FACELIFT-01	4354	1800	1555	BMW 2 Series Active Tourer official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0277653EN/the-new-bmw-2-series-active-tourer
EU-MINI-MINI-F54-CLUBMAN-WAGON-01	4253	1800	1441	MINI Clubman official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0252423EN/353092
EU-BMW-1-F40-HATCHBACK-01	4319	1799	1434	BMW 1 Series official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0295725EN/the-all-new-bmw-1-series
EU-DS-DS9-I-SEDAN-01	4934	1855	1460	DS Automobiles DS 9 official price and specification guide	https://www.media.stellantis.com/uploads/uk/model-pricelist/ds9pricesandspecs-6172ca39a3822.pdf
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Citroën C4 official specification guide	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/models/new-c4-and-e-c4/brochure/citroen-c4-e-c4-price-specification-guide.pdf
EU-FORD-PUMA-II-SUV-ST-01	4226	1805	1533	Ford Puma ST official technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2020/09/Puma-ST/documents/Ford_Puma-ST_2020_ProvisionalTechSpec_200922.pdf
EU-DACIA-SPRING-I-DBG-HATCHBACK-01	3734	1579	1516	Dacia Spring official brochure	https://cdn.group.renault.com/dac/pt/catalogos/spring/catalogo_spring_motorizacoes.pdf
EU-VW-POLO-VI-HATCHBACK-TSI-01	4053	1751	1461	Volkswagen Polo official brochure	https://www.volkswagen.co.uk/assets/common/pdf/brochures/polo-brochure.pdf
EU-HYUNDAI-I20-III-BC3-HATCHBACK-01	4040	1775	1450	Hyundai Motor Europe all-new i20 technical data	https://www.hyundai.news/newsroom/dam/eu/press-kits/20201012_all-new_i20/20201001_Technical_Data_i20_v2_clean.pdf
EU-KIA-PICANTO-III-JA-HATCHBACK-01	3595	1595	1485	Kia Picanto official specification	https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/picanto/specification/picanto-specification.pdf
EU-PEUGEOT-508-II-R8-PSE-FASTBACK-01	4750	1859	1410	Peugeot 508 PSE official model page	https://www.peugeot.it/gamma-modelli/nuova-508-peugeot-sport-engineered.html
EU-PEUGEOT-508-II-WAGON-01	4778	1859	1420	Peugeot 508 SW official specification guide	https://www.peugeot.co.uk/content/dam/peugeot/uk/b2c/documentation/price-list/508-price-list.pdf
EU-AUDI-Q5-FY-SUV-FACELIFT-01	4682	1893	1662	Audi Q5 official technical data	https://press.audi.co.uk/assets/documents/original/1890-AudiQ540TDIquattroStronicUKTechnicalDataNovember2020.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1799	1456	SEAT Leon official technical data	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2020/The-all-new-SEAT-Leon
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1450	SEAT Leon Sportstourer official technical data	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2020/The-all-new-SEAT-Leon
EU-SKODA-ENYAQ-IV-I-5AZ-SUV-01	4649	1879	1616	ŠKODA ENYAQ iV official technical specifications	https://cdn.skoda-storyboard.com/2021/03/TD-ENYAQ-iV-EN.pdf
EU-LEXUS-NX-I-PREFL-SUV-01	4630	1845	1645	Lexus NX official launch specifications	https://newsroom.lexus.eu/2014-lexus-nx-technical-specifications/
EU-LEXUS-NX-I-FACELIFT-SUV-01	4640	1845	1645	Lexus NX official facelift specifications	https://newsroom.lexus.eu/2017-lexus-nx-technical-specifications/
EU-SEAT-ARONA-I-KJ7-SUV-01	4138	1780	1552	SEAT Arona official technical data	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2017/the-new-seat-arona
EU-SKODA-OCTAVIA-IV-NX-RS-HATCHBACK-01	4702	1829	1457	ŠKODA OCTAVIA RS official technical specifications	https://cdn.skoda-storyboard.com/2020/11/TD-OCTAVIA-RS-en.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-IV-HATCHBACK-01	4702	1829	1476	ŠKODA OCTAVIA RS iV official technical specifications	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-RS-iV-en.pdf
EU-SKODA-OCTAVIA-IV-NX-HATCHBACK-01	4689	1829	1470	ŠKODA OCTAVIA official technical specifications	https://cdn.skoda-storyboard.com/2019/11/TD-OCTAVIA-en.pdf
EU-SUBARU-OUTBACK-VI-BT-WAGON-1670H-01	4870	1875	1670	Subaru Europe Outback official specifications	https://www.subaru.eu/docs/default-source/media-documents-gallery/spec-sheets/24outback_spec_ec.pdf
EU-SUBARU-OUTBACK-VI-BT-WAGON-1675H-01	4870	1875	1675	Subaru Europe Outback official specifications	https://www.subaru.eu/docs/default-source/media-documents-gallery/spec-sheets/24outback_spec_ec.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-WAGON-01	4702	1829	1455	ŠKODA OCTAVIA COMBI RS official technical specifications	https://cdn.skoda-storyboard.com/2020/07/TD-OCTAVIA-COMBI-RS-en.pdf
EU-SKODA-OCTAVIA-IV-NX-RS-IV-WAGON-01	4702	1829	1474	ŠKODA OCTAVIA COMBI RS iV official technical specifications	https://cdn.skoda-storyboard.com/2020/09/TD-OCTAVIA-COMBI-RS-iV-en.pdf
EU-SKODA-OCTAVIA-IV-NX-WAGON-01	4689	1829	1468	ŠKODA OCTAVIA COMBI official technical specifications	https://cdn.skoda-storyboard.com/2019/11/TD-OCTAVIA-COMBI-en.pdf
EU-SKODA-SUPERB-III-3V5-WAGON-FACELIFT-01	4862	1864	1477	ŠKODA SUPERB COMBI facelift official technical specifications	https://cdn.skoda-storyboard.com/2019/05/TD-SUPERB-COMBI-en.pdf
EU-VW-ID4-I-E21-SUV-RWD-01	4584	1852	1634	Volkswagen ID.4 official technical data	https://www.volkswagen-newsroom.com/en/the-id4-from-volkswagen-15712/technical-data-of-the-id4-15724
EU-VW-UP-I-FACELIFT-PETROL-HATCHBACK-01	3600	1641	1504	UltimateSpecs Volkswagen up! facelift 1.0 65HP	https://www.ultimatespecs.com/car-specs/Volkswagen/121290/Volkswagen-Up%21-2017-5-doors-10-65HP.html
EU-AUDI-A3-8Y-SPORTBACK-PREFL-01	4343	1816	1449	Audi A3 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a3-sportback-12558
EU-AUDI-A5-F5-SPORTBACK-FACELIFT-01	4757	1843	1398	Audi A5 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a5-sportback-2019-12353
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-GTS-01	5053	1937	1422	Porsche Panamera GTS Sport Turismo official technical data	https://newsroom.porsche.com/en/products/porsche-panamera-gts-sport-turismo-technical-data-16336.html
EU-PORSCHE-PANAMERA-II-971-SPORT-TURISMO-TURBO-01	5049	1937	1432	Porsche Panamera Turbo S Sport Turismo official technical data	https://newsroom.porsche.com/en/2020/products/porsche-panamera-turbo-s-e-hybrid-sport-turismo-technical-data-22404.html
EU-VW-TIGUAN-II-AD1-SUV-FWD-FACELIFT-01	4509	1839	1675	Volkswagen New Tiguan official brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/new-tiguan/vw_tiguan_brochure_dec_2020.pdf
EU-CUPRA-FORMENTOR-I-KM7-SUV-VZ310-01	4450	1839	1511	CUPRA Formentor official technical data	https://www.cupraofficial.mt/cars/cupra-range/formentor
EU-CUPRA-LEON-IV-KL1-EHYBRID-HATCHBACK-01	4398	1799	1467	CUPRA Leon official press kit	https://www.seat-cupra-mediacenter.com/CUPRA-Brand/presskits/CUPRA-Leon-Dinamic/Chassis
EU-CUPRA-LEON-IV-KL8-EHYBRID-WAGON-01	4657	1799	1463	CUPRA Leon Sportstourer official technical data	https://www.seat-cupra-mediacenter.com/content/dam/seat-media-center/models-all-brands/cupra-models/cupra-leon-sportstourer/technical-data/Technical_Data_CUPRA_Leon_Sportstourer.pdf
EU-LADA-LARGUS-I-R90-CNG-WAGON-01	4470	1750	1670	LADA Largus CNG official specifications	https://www.lada.ru/cars/largus/universal
EU-LAND-ROVER-110-LDH-SUV-01	4580	1790	2035	Automobile-Catalog Land-Rover 110 Station Wagon 2.5 Diesel	https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html
EU-LAND-ROVER-127-LDH-PICKUP-CREW-CAB-01	5170	1790	2021	Land Rover Defender UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Defender-2010-UK-.pdf
EU-VW-GOLF-VIII-CD-GTI-CLUBSPORT-HATCHBACK-01	4295	1789	1465	ADAC vehicle catalogue; Volkswagen Golf GTI Clubsport official media information	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/vw/golf/viii/316714/;https://www.volkswagen-newsroom.com/en/press-releases/the-new-golf-gti-clubsport-world-premiere-of-the-300-ps-flagship-gti-model-6496/download
EU-SUZUKI-ACROSS-I-SUV-01	4635	1855	1690	Suzuki ACROSS official technical data	https://www.suzuki.at/presse/auto/pressemeldungen/across/2022/2022_12_22_ACROSS%20Minor%20Change%202022/Suzuki%20ACROSS_Technische%20Daten_Dez22.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-COMPACT-FWD-01	4609	1920	1910	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-MEDIUM-FWD-01	4959	1920	1899	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-TOYOTA-PROACE-II-MDZ4-VAN-LONG-FWD-01	5309	1920	1940	Toyota Proace Van official technical specifications	https://media.toyota.co.uk/wp-content/uploads/sites/5/2021/03/1614162746210223MProaceTechSpec.pdf
EU-SKODA-SUPERB-III-3V3-HATCHBACK-FACELIFT-01	4869	1864	1469	ŠKODA SUPERB facelift official technical specifications	https://cdn.skoda-storyboard.com/2019/05/TD-SUPERB-en.pdf
EU-OPEL-MOKKA-B-GASOLINE-SUV-01	4151	1791	1531	Opel Mokka official price and specification guide	https://www.opel.ie/content/dam/opel/ireland/brochure-library/brochures/passenger-cars/WebMokkaPriceEquipGuide.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-STANDARD-01	5282	1860	1815	Ford Ranger official price and specification guide	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-LIMITED-01	5359	1860	1821	Ford Ranger official price and specification guide	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Ranger.pdf
EU-FORD-RANGER-III-TKE-PICKUP-DOUBLE-CAB-WILDTRAK-01	5359	1860	1848	Ford Ranger official price and specification guide	https://www.ford.co.uk/content/dam/guxeu/uk/documents/price-list/commercial-vehicles/PL-Ranger.pdf
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Audi A1 Sportback official technical data	https://www.audi-mediacenter.com/en/audi-a1-sportback-2018-11184
EU-CITROEN-C3-AIRCROSS-I-PHASE-I-SUV-01	4154	1756	1637	Citroën C3 Aircross official specification guide	https://www.citroen.co.uk/content/dam/citroen/uk/b2c/models/c3-aircross-suv/brochure/c3-aircross-price-and-specification-guide.pdf
EU-AUDI-A3-8Y-SEDAN-PREFL-01	4495	1816	1425	Audi A3 Sedan official technical data	https://www.audi-mediacenter.com/en/audi-a3-sedan-2020-12735
EU-AUDI-A3-8Y-S3-SEDAN-PREFL-01	4504	1816	1415	Audi S3 Sedan official technical data	https://uploads.audi-mediacenter.com/system/production/uploaded_files/17325/file/7997db0b7ad899a8c650ee29584d1d8953804c45/etd_Audi_S3_Sedan.pdf
EU-AUDI-A3-8Y-S3-SPORTBACK-PREFL-01	4351	1816	1438	Audi S3 Sportback official technical data	https://www.audi-mediacenter.com/system/production/uploaded_files/17318/file/7334d9a7986e08895ccb6ee8a490f603249ede05/td_Audi_S3_Sportback_228_kW.pdf?1598606430=&disposition=attachment
EU-AUDI-A6-ALLROAD-C8-WAGON-01	4951	1902	1497	Audi A6 allroad quattro official technical data	https://www.audi-mediacenter.com/en/audi-a6-allroad-quattro-2019-11816
EU-AUDI-Q8-I-4MN-SUV-01	4986	1995	1705	Audi Q8 official technical data	https://www.audi-mediacenter.com/en/audi-q8-2018-10454
EU-MINI-MINI-F56-HATCHBACK-COOPER-S-01	3850	1727	1414	MINI Hatch official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0280835EN/the-new-mini-3-door-the-new-mini-5-door-the-new-mini-convertible
EU-MINI-MINI-F55-HATCHBACK-ONE-01	3982	1727	1425	MINI 5-door Hatch official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0280835EN/the-new-mini-3-door-the-new-mini-5-door-the-new-mini-convertible
EU-MINI-MINI-F57-CONVERTIBLE-COOPER-S-01	3821	1727	1415	MINI Convertible official technical specifications	https://www.press.bmwgroup.com/global/article/detail/T0280835EN/the-new-mini-3-door-the-new-mini-5-door-the-new-mini-convertible
EU-SKODA-KAMIQ-NW4-SUV-01	4241	1793	1531	ŠKODA KAMIQ official technical specifications	https://cdn.skoda-storyboard.com/2019/02/TD-KAMIQ-en.pdf
EU-SKODA-SCALA-I-NW1-HATCHBACK-01	4362	1793	1471	ŠKODA SCALA official technical specifications	https://cdn.skoda-storyboard.com/2018/12/TD-SCALA-en.pdf
EU-VW-CADDY-V-SBB-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy Life official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-life/caddy_life-brochure.pdf
EU-VW-CADDY-V-SBJ-MPV-LWB-01	4853	1855	1800	Volkswagen Caddy Life official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-life/caddy_life-brochure.pdf
EU-VW-CADDY-V-SBA-VAN-SWB-01	4500	1855	1856	Volkswagen Caddy Cargo official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-cargo/caddy-cargo-brochure.pdf
EU-VW-CADDY-V-SBH-VAN-LWB-01	4853	1855	1860	Volkswagen Caddy Cargo official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/caddy-cargo/caddy-cargo-brochure.pdf
EU-SEAT-TARRACO-I-KN2-SUV-01	4735	1839	1674	SEAT Tarraco official technical data	https://www.seat-mediacenter.com/newspage/allnews/modelrange/2018/the-new-seat-tarraco
EU-CUPRA-FORMENTOR-I-KM7-SUV-15TSI-01	4446	1839	1520	CUPRA Formentor official technical data	https://www.cupraofficial.mt/cars/cupra-range/formentor
EU-FIAT-500E-I-332-HATCHBACK-3PLUS1-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
EU-FIAT-500E-I-332-HATCHBACK-3D-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
EU-VOLVO-XC40-I-SUV-01	4425	1863	1652	Volvo XC40 official specifications	https://www.media.volvocars.com/global/en-gb/models/xc40/2021/specifications
EU-FIAT-500E-I-332-CONVERTIBLE-01	3632	1683	1527	Fiat 500e official technical data	https://www.fiat.co.uk/models/fiat-500-electric/technical-data
EU-BMW-2-F44-GRAN-COUPE-01	4526	1800	1420	BMW 2 Series Gran Coupé official specifications	https://www.press.bmwgroup.com/global/article/attachment/T0309526EN/452536
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_5601-5700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html "https://www.automobile-catalog.com/car/1985/1393385/land-rover_110_station_wagon_2_5_diesel.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（6018 行）
- 累计尺寸组：dimension_groups_final.tsv（2189 行）

