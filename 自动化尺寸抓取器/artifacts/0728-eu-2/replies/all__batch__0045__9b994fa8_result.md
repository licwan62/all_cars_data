# 任务：all 第 4401-4500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0045__9b994fa8


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
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468
EU-BMW-5-SERIES-E61-WAGON-01	4843	1846	1491
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491
EU-BMW-5-SERIES-F07-GT-HATCHBACK-FACELIFT-01	5004	1901	1559
EU-BMW-5-SERIES-F07-GT-HATCHBACK-PREFL-01	4998	1901	1559
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	5039	1902	1491
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	5039	1902	1491
EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	5179	1902	1484
EU-BMW-7-SERIES-F01-LCI-SEDAN-SWB-01	5079	1902	1471
EU-BMW-7-SERIES-F01-SEDAN-SWB-01	5072	1902	1479
EU-BMW-7-SERIES-F02-LCI-SEDAN-LWB-01	5219	1902	1471
EU-BMW-7-SERIES-F02-SEDAN-LWB-01	5212	1902	1479
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201
EU-CHEVROLET-CORVETTE-C4-COUPE-01	4534	1796	1176
EU-CHEVROLET-CORVETTE-C6-CONVERTIBLE-01	4435	1844	1246
EU-CHEVROLET-CORVETTE-C6-COUPE-Z06-01	4460	1928	1237
EU-CHEVROLET-CORVETTE-C6-COUPE-ZR1-01	4475	1928	1237
EU-CHEVROLET-SPARK-II-HATCHBACK-01	3495	1495	1485
EU-CHEVROLET-SPARK-M150-HATCHBACK-01	3495	1495	1485
EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	5143	1954	1750
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464
EU-FIAT-PANDA-I-141A-VAN-3D-4X4-01	3435	1500	1485
EU-FIAT-PANDA-I-141A-VAN-3D-FWD-01	3408	1494	1420
EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	3538	1589	1540
EU-FIAT-PANDA-II-169-NATURAL-POWER-HATCHBACK-5D-01	3538	1589	1576
EU-FIAT-PANDA-II-HATCHBACK-100HP-01	3578	1606	1522
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416
EU-MINI-MINI-R52-CONVERTIBLE-01	3660	1690	1420
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415
EU-MINI-MINI-R53-HATCHBACK-JCW-3D-01	3655	1688	1427
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775
EU-PEUGEOT-206-PHASE-I-HATCHBACK-01	3835	1652	1426
EU-PEUGEOT-206-PHASE-II-HATCHBACK-01	3822	1652	1425
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452
EU-RENAULT-LAGUNA-II-FACELIFT-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-GRANDTOUR-FACELIFT-WAGON-01	4695	1772	1443
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443
EU-RENAULT-LAGUNA-III-COUPE-2D-01	4643	1811	1400
EU-RENAULT-LAGUNA-III-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443
EU-VW-GOLF-V-1K5-WAGON-01	4556	1781	1504
EU-VW-GOLF-V-HATCHBACK-01	4204	1759	1485
EU-VW-GOLF-V-HATCHBACK-3D-01	4204	1759	1485
EU-VW-GOLF-V-HATCHBACK-5D-01	4204	1759	1485
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480
EU-VW-GOLF-VI-CABRIOLET-2D-01	4246	1782	1423
EU-VW-GOLF-VII-VARIANT-WAGON-5D-PREFL-01	4575	1799	1481
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504
EU-VW-GOLF-V-PLUS-MPV-01	4206	1759	1580
EU-VW-GOLF-V-PLUS-MPV-5D-01	4206	1759	1580
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-R36-SEDAN-01	4806	1820	1447
EU-VW-PASSAT-B6-R36-WAGON-01	4820	1820	1456
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472
EU-VW-PASSAT-B6-VARIANT-WAGON-01	4774	1820	1517
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	E-Klasse	E 250 CDI / Bluetec / D	Cabriolet	Heckantrieb	Diesel	150	204	Jan 2010	Dec 2016	2024-03-01	32947
Mercedes-benz	E-Klasse	E 350 CDI	Cabriolet	Heckantrieb	Diesel	170	231	Jan 2010	Dec 2011	2024-03-01	32948
Mercedes-benz	E-Klasse	E 200 CGI	Cabriolet	Heckantrieb	Benzin	135	184	Jan 2010	Dec 2016	2024-03-01	32949
Mercedes-benz	E-Klasse	E 250 CGI	Cabriolet	Heckantrieb	Benzin	150	204	Jan 2010	Dec 2016	2024-03-01	32950
Mercedes-benz	E-Klasse	E 350 CGI	Cabriolet	Heckantrieb	Benzin	215	292	Jan 2010	Dec 2014	2024-03-01	32951
Mercedes-benz	E-Klasse	E 500	Cabriolet	Heckantrieb	Benzin	285	388	Jan 2010	Dec 2011	2024-03-01	32952
Renault	Fluence	1.5 DCI	Stufenheck	Frontantrieb	Diesel	63	86	Feb 2010	-	2024-03-01	32953
Renault	Fluence	1.5 DCI	Stufenheck	Frontantrieb	Diesel	78	106	Feb 2010	-	2024-03-01	32954
Mercedes-benz	E-Klasse	E 220 CDI / D	Coupe	Heckantrieb	Diesel	125	170	Jan 2010	Dec 2016	2024-03-01	32955
Mercedes-benz	E-Klasse	E 200 CGI	Coupe	Heckantrieb	Benzin	135	184	Jan 2010	Dec 2016	2024-03-01	32956
Citroën	C-Zero	C-zero	Schrägheck	Heckantrieb	Elektro	47	64	Oct 2010	-	2024-03-01	32966
Citroën	C4 picasso i	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	110	150	Jul 2008	Aug 2013	2024-03-01	32969
Citroën	C6	3.0 HDI	Stufenheck	Frontantrieb	Diesel	177	241	Apr 2009	Dec 2012	2024-03-01	32970
Peugeot	206	1.4 HDI ECO 70	Stufenheck	Frontantrieb	Diesel	50	68	Sep 2008	-	2024-03-01	32971
VW	Passat b6 variant	1.8 TSI	Kombi	Frontantrieb	Benzin	112	152	Nov 2009	Nov 2010	2024-03-01	32974
VW	Passat b6	1.8 TSI	Stufenheck	Frontantrieb	Benzin	112	152	Nov 2009	Jul 2010	2024-03-01	32978
Nissan	Kubistar	1.2	Kasten	Frontantrieb	Benzin	44	60	Aug 2003	-	2024-03-01	32981
Nissan	Kubistar	1.2 16V	Kasten	Frontantrieb	Benzin	55	75	Apr 2006	-	2024-03-01	32982
Nissan	Kubistar	1.6 16V	Kasten	Frontantrieb	Benzin	70	95	Aug 2003	Oct 2009	2024-03-01	32984
Nissan	Kubistar	1.5 DCI	Kasten	Frontantrieb	Diesel	48	65	Aug 2003	-	2024-03-01	32986
Nissan	Kubistar	1.5 DCI	Kasten	Frontantrieb	Diesel	60	82	Aug 2003	Oct 2009	2024-03-01	32987
Mercedes-benz	Sls amg	6.2	Coupe	Heckantrieb	Benzin	420	571	Mar 2010	-	2024-03-01	32991
Renault	Sandero/stepway i	1.4	Schrägheck	Frontantrieb	Benzin	55	75	Feb 2009	Jul 2013	2025-12-01	32992
Renault	Sandero/stepway i	1.6	Schrägheck	Frontantrieb	Benzin	64	87	Feb 2009	Oct 2012	2025-12-01	32993
BMW	7	732 I	Stufenheck	Heckantrieb	Benzin	145	197	Sep 1979	Aug 1986	2024-03-01	33000
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	150	204	Jun 2009	Aug 2011	2024-03-01	33006
BMW	5	528 I	Stufenheck	Heckantrieb	Benzin	190	258	Mar 2010	Aug 2011	2024-03-01	33007
BMW	5	535 I	Stufenheck	Heckantrieb	Benzin	225	306	Jan 2010	Oct 2016	2024-03-01	33008
BMW	5	550 I	Stufenheck	Heckantrieb	Benzin	300	408	Mar 2010	Dec 2013	2026-04-01	33009
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	135	184	Jun 2010	Jun 2014	2024-03-01	33010
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	150	204	Mar 2010	Aug 2011	2024-03-01	33011
BMW	5	530 D	Stufenheck	Heckantrieb	Diesel	180	245	Jan 2010	Aug 2011	2024-03-01	33012
Lexus	Ls	460 AWD	Stufenheck	Allrad	Benzin	270	367	Oct 2008	-	2025-06-01	33013
Tazzari	Zero	Electric	Stufenheck	Heckantrieb	Elektro	15	20	Jan 2010	Dec 2016	2024-03-01	33015
Chevrolet	Spark	1	Schrägheck	Frontantrieb	Benzin	50	68	Mar 2010	-	2024-03-01	33016
Chevrolet	Spark	1.2	Schrägheck	Frontantrieb	Benzin	60	82	Mar 2010	-	2024-03-01	33017
Mercedes-benz	124	300 Ce-24	Coupe	Heckantrieb	Benzin	170	231	Sep 1989	Dec 1992	2024-03-01	33018
Mercedes-benz	124	300 E-24	Stufenheck	Heckantrieb	Benzin	170	231	Sep 1988	Aug 1992	2024-03-01	33019
Mercedes-benz	124	300 Ce-24	Cabriolet	Heckantrieb	Benzin	170	231	Apr 1992	Jun 1993	2024-03-01	33021
Aston Martin	Rapide	6	Schrägheck	Heckantrieb	Benzin	350	476	Mar 2010	Sep 2013	2024-03-01	33022
Mercedes-benz	Glk-Klasse	350 CDI 4-matic	SUV	Allrad	Diesel	165	224	Jul 2009	Jan 2010	2024-03-01	33023
VW	Golf vi	1.6 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Feb 2009	Nov 2012	2024-03-01	33030
VW	Golf vi variant	1.6 TDI	Kombi	Frontantrieb	Diesel	66	90	Dec 2009	Jul 2013	2024-03-01	33031
Dacia	Duster	1.6 16V	SUV	Frontantrieb	Benzin	77	105	Apr 2010	Jan 2018	2024-03-01	33039
Dacia	Duster	1.6 16V 4X4	SUV	Allrad	Benzin	77	105	Jun 2010	Jan 2018	2024-03-01	33040
Dacia	Duster	1.5 DCI	SUV	Frontantrieb	Diesel	63	86	Apr 2010	Jan 2018	2024-03-01	33041
Dacia	Duster	1.5 DCI	SUV	Frontantrieb	Diesel	79	107	Jun 2010	Jan 2018	2024-03-01	33042
Ferrari	458	4.5	Coupe	Heckantrieb	Benzin	419	570	Dec 2009	-	2024-03-01	33044
Mercedes-benz	M-Klasse	ML 300 CDI 4-matic	SUV	Allrad	Diesel	150	204	Feb 2010	Dec 2011	2024-03-01	33045
Mercedes-benz	M-Klasse	ML 350 CDI 4-matic	SUV	Allrad	Diesel	170	231	Feb 2010	Dec 2011	2024-03-01	33046
VW	Golf v	1.6 Multifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	75	102	Oct 2007	Nov 2008	2024-03-01	33047
VW	Golf v variant	1.6 Multifuel	Kombi	Frontantrieb	Benzin/Ethanol	75	102	Nov 2007	Jul 2009	2024-03-01	33048
VW	Jetta iii	1.6 Multifuel	Stufenheck	Frontantrieb	Benzin/Ethanol	75	102	Jan 2008	Oct 2010	2024-03-01	33049
Mercedes-benz	E-Klasse	E 350 CDI 4-matic	Stufenheck	Allrad	Diesel	170	231	Sep 2009	Aug 2011	2024-03-01	33050
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	55	75	Mar 2010	Nov 2013	2024-03-01	33051
Mini	Mini	ONE	Schrägheck	Frontantrieb	Benzin	72	98	Mar 2010	Nov 2013	2024-03-01	33052
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	90	122	Sep 2009	Nov 2013	2024-03-01	33053
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	135	184	Mar 2010	Nov 2013	2024-03-01	33054
Mercedes-benz	E-Klasse	E 350 Bluetec	Kombi	Heckantrieb	Diesel	155	211	Nov 2009	Dec 2013	2024-03-01	33055
Mini	Mini	ONE D	Schrägheck	Frontantrieb	Diesel	66	90	Jun 2009	Jul 2010	2024-03-01	33056
VW	Lupo i	1	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1998	May 2000	2024-03-01	33057
Seat	Arosa	1	Schrägheck	Frontantrieb	Benzin	37	50	Oct 1998	Jan 2001	2024-03-01	33058
Opel	Meriva b	1.4	Großraumlimousine	Frontantrieb	Benzin	74	100	Jun 2010	Mar 2017	2024-03-01	33059
Opel	Meriva b	1.4	Großraumlimousine	Frontantrieb	Benzin	88	120	Jun 2010	Mar 2017	2024-03-01	33060
Opel	Meriva b	1.4	Großraumlimousine	Frontantrieb	Benzin	103	140	Jun 2010	Mar 2017	2024-03-01	33061
Opel	Meriva b	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	74	100	Jun 2010	Jan 2017	2024-03-01	33062
Mercedes-benz	Gl-Klasse	GL 320 CDI / 350 Bluetec 4-matic	SUV	Allrad	Diesel	155	211	Dec 2009	Aug 2012	2024-03-01	33063
Wiesmann	Gt	4.0 S	Coupe	Heckantrieb	Benzin	309	420	Mar 2010	-	2024-03-01	33064
Wiesmann	Gt	4.8	Coupe	Heckantrieb	Benzin	270	367	Sep 2003	-	2024-03-01	33065
Wiesmann	Gt	5	Coupe	Heckantrieb	Benzin	373	507	Sep 2007	-	2024-03-01	33066
Wiesmann	Mf4 roadster	4.8	Cabriolet	Heckantrieb	Benzin	270	367	Mar 2009	-	2024-03-01	33067
Wiesmann	Mf4 roadster	4.0 S	Cabriolet	Heckantrieb	Benzin	309	420	Mar 2009	-	2024-03-01	33068
Wiesmann	Mf5 roadster	5	Cabriolet	Heckantrieb	Benzin	373	507	Sep 2009	-	2024-03-01	33069
Fiat	Panda	1.2 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	44	60	Apr 2009	-	2024-03-01	33070
Mini	Mini	ONE	Kombi	Frontantrieb	Benzin	72	98	Mar 2010	Jun 2014	2024-03-01	33074
Mini	Mini	Cooper	Kombi	Frontantrieb	Benzin	90	122	Mar 2010	Jun 2014	2024-03-01	33075
Mini	Mini	Cooper S	Kombi	Frontantrieb	Benzin	135	184	Mar 2010	Jun 2014	2024-03-01	33076
Mini	Mini	ONE	Cabriolet	Frontantrieb	Benzin	72	98	Sep 2009	Jun 2015	2024-03-01	33077
Mini	Mini	Cooper	Cabriolet	Frontantrieb	Benzin	90	122	Mar 2010	Jun 2015	2024-03-01	33078
Mini	Mini	Cooper S	Cabriolet	Frontantrieb	Benzin	135	184	Feb 2010	Jun 2015	2024-03-01	33079
Audi	80	1.7	Kombi	Frontantrieb	Benzin	59	80	Sep 1966	Aug 1968	2024-03-01	33081
Mazda	Cx-9	3.5	SUV	Frontantrieb	Benzin	193	263	Sep 2006	Dec 2007	2024-03-01	33084
Mazda	Cx-9	3.7 AWD	SUV	Allrad	Benzin	204	277	Jan 2007	-	2024-03-01	33085
Mazda	Cx-9	3.7	SUV	Frontantrieb	Benzin	204	277	Jan 2007	-	2024-03-01	33086
Mazda	Cx-9	3.5 AWD	SUV	Allrad	Benzin	193	263	Jan 2007	-	2024-03-01	33087
Renault	Laguna ii	1.8 16V	Schrägheck	Frontantrieb	Benzin	86	117	Mar 2001	May 2005	2024-03-01	33091
Chrysler	Grand voyager v	2.8 CRD	Großraumlimousine	Frontantrieb	Diesel	120	163	Oct 2007	-	2024-03-01	33092
Renault	Laguna ii grandtour	1.8 16V	Kombi	Frontantrieb	Benzin	86	117	Mar 2001	May 2005	2024-03-01	33093
Chevrolet	Corvette	6.2	Coupe	Heckantrieb	Benzin	321	437	Feb 2008	Aug 2013	2024-03-01	33094
Citroën	Traction avant	1.9	Schrägheck	Frontantrieb	Benzin	43	58	Mar 1950	Apr 1956	2024-03-01	33095
Chrysler	Neon	2.0 16V	Stufenheck	Frontantrieb	Benzin	97	131	Oct 2002	Dec 2006	2024-03-01	33096
Renault	Wind	1.2	Cabriolet	Frontantrieb	Benzin	74	101	Jul 2010	May 2011	2025-12-01	33123
Renault	Wind	1.6	Cabriolet	Frontantrieb	Benzin	98	133	Jul 2010	Aug 2013	2025-12-01	33124
Renault	Megane cc	1.4 TCE	Cabriolet	Frontantrieb	Benzin	96	131	Jun 2010	Aug 2015	2024-03-01	33125
Renault	Megane cc	1.5 DCI	Cabriolet	Frontantrieb	Diesel	81	110	Jun 2010	Aug 2015	2024-03-01	33126
Renault	Megane cc	1.9 DCI	Cabriolet	Frontantrieb	Diesel	96	131	Jun 2010	Aug 2015	2024-03-01	33127
Renault	Megane cc	2.0 DCI	Cabriolet	Frontantrieb	Diesel	118	160	Jun 2010	Aug 2015	2024-03-01	33128
Mitsubishi	L200	2.5 Di-d	Pick-up	Heckantrieb	Diesel	94	128	Apr 2010	Dec 2015	2024-03-01	33129
Mitsubishi	L200	2.5 Di-d 4WD	Pick-up	Allrad	Diesel	131	178	Apr 2010	Dec 2015	2024-03-01	33130
Hyundai	Ix35	2	SUV	Frontantrieb	Benzin	120	163	Jan 2010	Jul 2013	2024-03-01	33131


--- Round 1 / 首次发送 ---
## 更新点

* 闭合 39 个输入 Ktype，共形成 46 条 READY 映射；同发动机、燃料或功率差异不重复建组。
* Dacia Duster I 的生产区间跨越 2013 改款，改款前后车宽分别为 1822 mm 和 1821 mm，因此四个 Ktype 均拆([汽车数据网][1])
* Golf V、Golf VI 未指定门数的两厢车型按三门、五门拆分，并直接复用已有尺寸组。
* 首次创建 C-Zero、SLS AMG、Spark III、Ferrari 458 Italia、W164 M-Class、S212 Wagon、Meriva B、Wind、Mégane III CC、Corvette C6 Coupe、ix35 等尺寸组。Mercedes-Benz 组优先采用官方档案，其他组使用明确区分车身宽度和含镜宽度的规格页面。([marsClassic][2])ype 未区分后悬架配置，按累计表中已存在的钢簧和空气悬架两种高度分支复用，不重复输出尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：39 / 100
* READY 映射行：46
* 待处理输入 Ktype：61
* 当前已引用尺寸组：31
* 本轮首次创建尺寸组：13
* 本轮复用已有尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
32966	32966	Hatchback	C-Zero		5	EU-CITROEN-C-ZERO-HATCHBACK-5D-01	HIGH		READY
32969_coil	32969	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一发动机 Ktype 未区分后悬架配置，按已确认高度分支拆分。	READY
32969_airsusp	32969	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一发动机 Ktype 未区分后悬架配置，按已确认高度分支拆分。	READY
32970	32970	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH		READY
32971	32971	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
32974	32974	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH		READY
32978	32978	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH		READY
32991	32991	Coupe	SLS AMG	C197	2	EU-MERCEDES-BENZ-SLS-AMG-C197-COUPE-01	HIGH		READY
33016	33016	Hatchback	Spark III	M300	5	EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	HIGH		READY
33017	33017	Hatchback	Spark III	M300	5	EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	HIGH		READY
33030_3dr	33030	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	输入未区分门数，覆盖三门外廓。	READY
33030_5dr	33030	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	输入未区分门数，覆盖五门外廓。	READY
33031	33031	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
33039_prefl	33039	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33039_facelift	33039	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33040_prefl	33040	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33040_facelift	33040	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33041_prefl	33041	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33041_facelift	33041	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33042_prefl	33042	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33042_facelift	33042	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33044	33044	Coupe	458 Italia	F142	2	EU-FERRARI-458-ITALIA-F142-COUPE-01	HIGH		READY
33045	33045	SUV	M-Class W164 Facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	HIGH		READY
33046	33046	SUV	M-Class W164 Facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	HIGH		READY
33047_3dr	33047	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	输入未区分门数，覆盖三门外廓。	READY
33047_5dr	33047	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	输入未区分门数，覆盖五门外廓。	READY
33048	33048	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
33049	33049	Sedan	Jetta III	1K2	4	EU-VW-JETTA-III-1K2-SEDAN-4D-01	HIGH		READY
33055	33055	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
33056	33056	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH		READY
33059	33059	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33060	33060	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33061	33061	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33062	33062	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33070	33070	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	HIGH		READY
33091	33091	Hatchback	Laguna II Phase I		5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	HIGH		READY
33092	33092	MPV	Grand Voyager V	RT	5	EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	HIGH		READY
33093	33093	Wagon	Laguna II Grandtour Phase I		5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	HIGH		READY
33094	33094	Coupe	Corvette C6	C6	3	EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	HIGH		READY
33123	33123	Convertible	Wind I	E33	2	EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	HIGH		READY
33124	33124	Convertible	Wind I	E33	2	EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	HIGH		READY
33125	33125	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33126	33126	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33127	33127	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33128	33128	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33131	33131	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CITROEN-C-ZERO-HATCHBACK-5D-01	3480	1475	1610	Auto-Data.net Citroën C-Zero model specifications	https://www.auto-data.net/en/citroen-c-zero-model-2051
EU-MERCEDES-BENZ-SLS-AMG-C197-COUPE-01	4638	1939	1262	Mercedes-Benz Public Archive SLS AMG GT Coupé	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLS-AMG-GT-Coup-2012---2014.xhtml?oid=192608217
EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	3640	1597	1522	Auto-Data.net Chevrolet Spark III 1.0 16V	https://www.auto-data.net/en/chevrolet-spark-iii-1.0-16v-68hp-16922
EU-DACIA-DUSTER-I-SUV-PREFL-01	4315	1822	1625	Auto-Data.net Dacia Duster 1.5 dCi 4x2	https://www.auto-data.net/en/dacia-duster-1.5-dci-86hp-4x2-57153
EU-DACIA-DUSTER-I-SUV-FACELIFT-01	4315	1821	1625	Auto-Data.net Dacia Duster facelift 2013 1.6	https://www.auto-data.net/en/dacia-duster-facelift-2013-1.6-105hp-19702
EU-FERRARI-458-ITALIA-F142-COUPE-01	4527	1937	1213	Auto-Data.net Ferrari 458 Italia 4.5 V8	https://www.auto-data.net/en/ferrari-458-italia-4.5-v8-570hp-18350
EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	4781	1911	1815	Mercedes-Benz Public Archive ML 300 CDI 4MATIC BlueEFFICIENCY; Mercedes-Benz Public Archive ML 350 CDI 4MATIC	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-300-CDI-4MATIC-BlueEFFICIENCY-2010---2011.xhtml?oid=191414613;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-350-CDI-4MATIC-2010---2011.xhtml?oid=191414615
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	4895	1854	1515	Mercedes-Benz Public Archive E 350 CDI BlueEFFICIENCY Estate	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-CDI-BlueEFFICIENCY-2010---2013.xhtml?oid=188823505
EU-OPEL-MERIVA-B-MPV-5D-01	4288	1812	1615	Auto-Data.net Opel Meriva B specifications	https://www.auto-data.net/en/opel-meriva-b-1.3-cdti-75hp-17003
EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	3833	1689	1381	Auto-Data.net Renault Wind 1.2 TCe	https://www.auto-data.net/en/renault-wind-1.2-tce-101hp-33940
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	4485	1811	1434	Auto-Data.net Renault Mégane III CC generation	https://www.auto-data.net/en/renault-megane-iii-cc-generation-3773
EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	4435	1844	1244	Automobile-Catalog 2008 Corvette C6 Coupe Europe	https://www.automobile-catalog.com/car/2008/479585/corvette_c6_coupe_6-speed.html
EU-HYUNDAI-IX35-LM-SUV-5D-01	4410	1820	1660	Auto-Data.net Hyundai ix35 2.0 CVVT	https://www.auto-data.net/en/hyundai-ix35-2.0-cvvt-163hp-18179
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz E-Class C207/A207 的 Coupe、Cabriolet 改款前后边界，以及 W212 4MATIC Sedan。
2. 处理 BMW F10 跨 LCI 的 535i、550i、520d，并复核 523i、528i、525d、530d 的改款前单一外廓。
3. 处理 MINI R55/R56/R57 改款分支，避免错误复用当前已有的改款前尺寸组。
4. 处理 Kubistar、Sandero/Stepway、Wiesmann、Mazda CX-9、Mitsubishi L200 等存在车身版本或资料稀缺问题的组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/dacia-duster-1.5-dci-86hp-4x2-57153 "Dacia Duster 1.5 dCi (86 Hp) 4x2 | Technical specs, data, fuel consumption, Dimensions"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLS-AMG-GT-Coup-2012---2014.xhtml?oid=192608217&utm_source=chatgpt.com "SLS AMG GT Coupé, 2012 - 2014"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 37 个此前待处理 Ktype，新增 54 条 READY 映射。
* 修正 Ktype `33056`：原无后缀基础行已撤销，改为 `33056_prefl` 与 `33056_facelift` 两个外廓分支。
* 完成 Mercedes-Benz E-Class A207/C207、BMW F10、MINI R55/R56/R57 等跨改款车型拆分。
* 新建并闭合 26 个尺寸组；Lexus LS XF40、MINI R56/R57 已有尺寸组直接复用，未重复输出来源。

## 当前批次进度

* READY 输入 Ktype：76 / 100
* PENDING 输入 Ktype：24
* READY 映射行：101
* 已确认尺寸组：57
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
32947_prefl	32947	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32947_facelift	32947	Convertible	E-Class A207 Facelift	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32948	32948	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32949_prefl	32949	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32949_facelift	32949	Convertible	E-Class A207 Facelift	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32950	32950	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	150 kW E 250 CGI 对应改款前版本。	READY
32951	32951	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32952	32952	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32953	32953	Sedan	Fluence I	L38	4	EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	HIGH		READY
32954	32954	Sedan	Fluence I	L38	4	EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	HIGH		READY
32955_prefl	32955	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32955_facelift	32955	Coupe	E-Class C207 Facelift	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32956_prefl	32956	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32956_facelift	32956	Coupe	E-Class C207 Facelift	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33000	33000	Sedan	7 Series E23	E23	4	EU-BMW-7-SERIES-E23-SEDAN-4D-01	HIGH		READY
33006	33006	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33007	33007	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33008_prefl	33008	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33008_lci	33008	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-LCI-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33009	33009	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	300 kW 550i 对应改款前动力版本。	READY
33010_prefl	33010	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33010_lci	33010	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-LCI-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33011	33011	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33012	33012	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33013	33013	Sedan	LS XF40	XF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH		READY
33018	33018	Coupe	124 Series	C124	2	EU-MERCEDES-BENZ-124-C124-COUPE-2D-01	HIGH		READY
33019	33019	Sedan	124 Series	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	HIGH		READY
33021	33021	Convertible	124 Series	A124	2	EU-MERCEDES-BENZ-124-A124-CONVERTIBLE-2D-01	HIGH		READY
33023	33023	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-PREFL-01	HIGH		READY
33050	33050	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-PREFL-01	HIGH		READY
33051_prefl	33051	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33051_facelift	33051	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33052_prefl	33052	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33052_facelift	33052	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33053_prefl	33053	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33053_facelift	33053	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33054_prefl	33054	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33054_facelift	33054	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33056_prefl	33056	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	撤销原无后缀基础行；生产区间跨 2010 外观改款。	READY
33056_facelift	33056	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	撤销原无后缀基础行；生产区间跨 2010 外观改款。	READY
33057	33057	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
33058_prefl	33058	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-3D-PREFL-01	HIGH	生产区间跨 2000 改款，按外廓长度拆分。	READY
33058_facelift	33058	Hatchback	Arosa I Facelift	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2000 改款，按外廓长度拆分。	READY
33063	33063	SUV	GL X164 Facelift	X164	5	EU-MERCEDES-BENZ-GL-X164-FACELIFT-SUV-5D-01	HIGH		READY
33074_prefl	33074	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33074_facelift	33074	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33075_prefl	33075	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33075_facelift	33075	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33076_prefl	33076	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度和高度拆分。	READY
33076_facelift	33076	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度和高度拆分。	READY
33077_prefl	33077	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33077_facelift	33077	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33078_prefl	33078	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33078_facelift	33078	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33079_prefl	33079	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33079_facelift	33079	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	4698	1786	1402	Auto-Data.net Mercedes-Benz E-Class Cabrio A207 generation	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-generation-3862
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Auto-Data.net Mercedes-Benz E-Class Cabrio A207 facelift generation	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-facelift-2013-generation-4119
EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	4618	1809	1479	Cataloge.eu Renault Fluence 2010	https://www.cataloge.eu/renault/fluence-2010
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	4698	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 E 200 CGI	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-e-200-cgi-blueefficiency-184hp-17394
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 facelift generation	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-generation-3863
EU-BMW-7-SERIES-E23-SEDAN-4D-01	4860	1800	1430	Auto-Data.net BMW 7 Series E23 732i	https://www.auto-data.net/en/bmw-7-series-e23-732i-197hp-9756
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	Automobile-Catalog 2010 BMW 523i Steptronic	https://www.automobile-catalog.com/car/2010/1198220/bmw_523i_steptronic.html
EU-BMW-5-SERIES-F10-SEDAN-LCI-01	4907	1860	1464	Carfolio 2013 BMW 535i xDrive	https://www.carfolio.com/bmw-535i-xdrive-337062
EU-MERCEDES-BENZ-124-C124-COUPE-2D-01	4655	1740	1394	Mercedes-Benz Public Archive 300 CE-24	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-CE-24.xhtml?oid=4600
EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	4740	1740	1428	Mercedes-Benz Public Archive 300 E-24	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-E-24.xhtml?oid=5298
EU-MERCEDES-BENZ-124-A124-CONVERTIBLE-2D-01	4655	1740	1391	Mercedes-Benz Public Archive 300 CE-24 Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-CE-24-Cabriolet.xhtml?oid=4640
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-PREFL-01	4528	1840	1689	Carfolio Mercedes-Benz GLK 350 4MATIC	https://www.carfolio.com/mercedes-benz-glk-350-4matic-176253
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-PREFL-01	4868	1854	1470	Auto-Data.net Mercedes-Benz E-Class W212 E 350 CDI 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-350-cdi-blueefficiency-v6-231hp-4matic-7g-tronic-17369
EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	3723	1683	1407	Automobile-Catalog 2010 MINI One facelift	https://www.automobile-catalog.com/car/2010/1754510/mini_one.html
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	3714	1683	1407	Automobile-Catalog 2010 MINI Cooper S	https://www.automobile-catalog.com/car/2010/1753520/mini_cooper_s.html
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	3729	1683	1407	Automobile-Catalog 2010 MINI Cooper S facelift	https://www.automobile-catalog.com/car/2010/1754660/mini_cooper_s.html
EU-VW-LUPO-I-6X-HATCHBACK-3D-01	3530	1640	1460	AutoEvolution Volkswagen Lupo 1998	https://www.autoevolution.com/cars/volkswagen-lupo-1998.html
EU-SEAT-AROSA-I-6H-HATCHBACK-3D-PREFL-01	3536	1639	1460	Automobile-Catalog 1998 SEAT Arosa 1.0	https://www.automobile-catalog.com/car/1998/3070955/seat_arosa_1_0.html
EU-SEAT-AROSA-I-6H-HATCHBACK-3D-FACELIFT-01	3551	1639	1460	Automobile-Catalog 2001 SEAT Arosa 1.0	https://www.automobile-catalog.com/car/2001/3071015/seat_arosa_1_0.html
EU-MERCEDES-BENZ-GL-X164-FACELIFT-SUV-5D-01	5099	1920	1840	Auto-Data.net Mercedes-Benz GL X164 facelift GL 350 CDI BlueTEC	https://www.auto-data.net/en/mercedes-benz-gl-x164-facelift-2009-gl-350-cdi-bluetec-211hp-4matic-g-tronic-27877
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	3937	1683	1426	Automobile-Catalog 2010 MINI Cooper Clubman	https://www.automobile-catalog.com/car/2010/1753175/mini_cooper_clubman.html
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	3961	1683	1426	Automobile-Catalog 2010 MINI Cooper Clubman facelift	https://www.automobile-catalog.com/car/2010/1754750/mini_cooper_clubman.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	3958	1683	1432	Automobile-Catalog 2010 MINI Cooper S Clubman	https://www.automobile-catalog.com/car/2010/1753625/mini_cooper_s_clubman.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	3961	1683	1432	Automobile-Catalog 2010 MINI Cooper S Clubman facelift	https://www.automobile-catalog.com/car/2010/1754840/mini_cooper_s_clubman.html
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	3723	1683	1414	Automobile-Catalog 2010 MINI Cooper Convertible facelift	https://www.automobile-catalog.com/car/2010/1754915/mini_cooper_convertible.html
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414	Automobile-Catalog 2010 MINI Cooper S Convertible facelift	https://www.automobile-catalog.com/car/2010/1755020/mini_cooper_s_convertible_automatic.html
```

## 下一步优先处理

1. 解决 Nissan Kubistar 不同资料中的车高及厢式车配置边界冲突。
2. 拆分 Sandero/Stepway、Mazda CX-9 和 Mitsubishi L200 的实际车身分支。
3. 闭合 Tazzari Zero、Aston Martin Rapide、Wiesmann、Audi 80 F103 Wagon、Traction Avant 和 Chrysler Neon 等资料稀缺车型。

推进信号：CONTINUE


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_4401-4500_ktype_dimension_mapping_final.tsv
- all_4401-4500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 剩余 24 个 Ktype 已全部闭合。
* 已完成一次轻量机械检查：表头固定、`id` 与 `DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源字段非空。
* 当前批次没有 `PENDING`，进入最终完整快照。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：130
* PENDING：0
* DIMENSION_GROUP：76
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
32947_prefl	32947	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32947_facelift	32947	Convertible	E-Class A207 Facelift	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32948	32948	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32949_prefl	32949	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32949_facelift	32949	Convertible	E-Class A207 Facelift	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度和高度拆分。	READY
32950	32950	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH	150 kW E 250 CGI 对应改款前版本。	READY
32951	32951	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32952	32952	Convertible	E-Class A207	A207	2	EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	HIGH		READY
32953	32953	Sedan	Fluence I	L38	4	EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	HIGH		READY
32954	32954	Sedan	Fluence I	L38	4	EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	HIGH		READY
32955_prefl	32955	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32955_facelift	32955	Coupe	E-Class C207 Facelift	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32956_prefl	32956	Coupe	E-Class C207	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32956_facelift	32956	Coupe	E-Class C207 Facelift	C207	2	EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
32966	32966	Hatchback	C-Zero		5	EU-CITROEN-C-ZERO-HATCHBACK-5D-01	HIGH		READY
32969_coil	32969	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	MEDIUM	同一 Ktype 未区分后悬架配置，按钢簧外廓分支。	READY
32969_airsusp	32969	MPV	C4 Picasso I	UD	5	EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	MEDIUM	同一 Ktype 未区分后悬架配置，按空气悬架外廓分支。	READY
32970	32970	Sedan	C6 I		4	EU-CITROEN-C6-I-SEDAN-01	HIGH		READY
32971	32971	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
32974	32974	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-3C5-WAGON-01	HIGH		READY
32978	32978	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-3C2-SEDAN-01	HIGH		READY
32981	32981	Van	Kubistar I	X76		EU-NISSAN-KUBISTAR-I-X76-VAN-01	MEDIUM	厢式车外廓统一，门数资料未稳定落盘。	READY
32982	32982	Van	Kubistar I	X76		EU-NISSAN-KUBISTAR-I-X76-VAN-01	MEDIUM	厢式车外廓统一，门数资料未稳定落盘。	READY
32984	32984	Van	Kubistar I	X76		EU-NISSAN-KUBISTAR-I-X76-VAN-01	MEDIUM	厢式车外廓统一，门数资料未稳定落盘。	READY
32986	32986	Van	Kubistar I	X76		EU-NISSAN-KUBISTAR-I-X76-VAN-01	MEDIUM	厢式车外廓统一，门数资料未稳定落盘。	READY
32987	32987	Van	Kubistar I	X76		EU-NISSAN-KUBISTAR-I-X76-VAN-01	MEDIUM	厢式车外廓统一，门数资料未稳定落盘。	READY
32991	32991	Coupe	SLS AMG	C197	2	EU-MERCEDES-BENZ-SLS-AMG-C197-COUPE-01	HIGH		READY
32992	32992	Hatchback	Sandero I	BS	5	EU-RENAULT-SANDERO-I-BS-HATCHBACK-5D-01	HIGH		READY
32993_hatchback	32993	Hatchback	Sandero I	BS	5	EU-RENAULT-SANDERO-I-BS-HATCHBACK-5D-01	MEDIUM	同一 Ktype 车系覆盖标准 Sandero 与 Stepway 外廓。	READY
32993_stepway	32993	SUV	Sandero I Stepway	BS	5	EU-RENAULT-SANDERO-I-STEPWAY-BS-SUV-5D-01	MEDIUM	同一 Ktype 车系覆盖标准 Sandero 与 Stepway 外廓。	READY
33000	33000	Sedan	7 Series E23	E23	4	EU-BMW-7-SERIES-E23-SEDAN-4D-01	HIGH		READY
33006	33006	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33007	33007	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33008_prefl	33008	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33008_lci	33008	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-LCI-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33009	33009	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	300 kW 550i 对应改款前动力版本。	READY
33010_prefl	33010	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33010_lci	33010	Sedan	5 Series F10 LCI	F10	4	EU-BMW-5-SERIES-F10-SEDAN-LCI-01	HIGH	生产区间跨 2013 改款，按外廓长度拆分。	READY
33011	33011	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33012	33012	Sedan	5 Series F10	F10	4	EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	HIGH		READY
33013	33013	Sedan	LS XF40	XF40	4	EU-LEXUS-LS-XF40-SEDAN-SWB-01	HIGH		READY
33015	33015	Hatchback	Zero		2	EU-TAZZARI-ZERO-HATCHBACK-2D-01	MEDIUM	输入车身形式修正为双门城市型掀背外廓。	READY
33016	33016	Hatchback	Spark III	M300	5	EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	HIGH		READY
33017	33017	Hatchback	Spark III	M300	5	EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	HIGH		READY
33018	33018	Coupe	124 Series	C124	2	EU-MERCEDES-BENZ-124-C124-COUPE-2D-01	HIGH		READY
33019	33019	Sedan	124 Series	W124	4	EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	HIGH		READY
33021	33021	Convertible	124 Series	A124	2	EU-MERCEDES-BENZ-124-A124-CONVERTIBLE-2D-01	HIGH		READY
33022	33022	Hatchback	Rapide I		5	EU-ASTON-MARTIN-RAPIDE-I-HATCHBACK-5D-01	HIGH		READY
33023	33023	SUV	GLK X204	X204	5	EU-MERCEDES-BENZ-GLK-X204-SUV-5D-PREFL-01	HIGH		READY
33030_3dr	33030	Hatchback	Golf VI	5K1	3	EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	HIGH	输入未区分门数，覆盖三门外廓。	READY
33030_5dr	33030	Hatchback	Golf VI	5K1	5	EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	HIGH	输入未区分门数，覆盖五门外廓。	READY
33031	33031	Wagon	Golf VI Variant	AJ5	5	EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	HIGH		READY
33039_prefl	33039	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33039_facelift	33039	SUV	Duster I Facelift	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33040_prefl	33040	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33040_facelift	33040	SUV	Duster I Facelift	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33041_prefl	33041	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33041_facelift	33041	SUV	Duster I Facelift	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33042_prefl	33042	SUV	Duster I	HS	5	EU-DACIA-DUSTER-I-SUV-PREFL-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33042_facelift	33042	SUV	Duster I Facelift	HS	5	EU-DACIA-DUSTER-I-SUV-FACELIFT-01	HIGH	生产区间跨 2013 改款，按外廓宽度拆分。	READY
33044	33044	Coupe	458 Italia	F142	2	EU-FERRARI-458-ITALIA-F142-COUPE-01	HIGH		READY
33045	33045	SUV	M-Class W164 Facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	HIGH		READY
33046	33046	SUV	M-Class W164 Facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	HIGH		READY
33047_3dr	33047	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	输入未区分门数，覆盖三门外廓。	READY
33047_5dr	33047	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	输入未区分门数，覆盖五门外廓。	READY
33048	33048	Wagon	Golf V Variant	1K5	5	EU-VW-GOLF-V-VARIANT-WAGON-5D-01	HIGH		READY
33049	33049	Sedan	Jetta V	1K2	4	EU-VW-JETTA-III-1K2-SEDAN-4D-01	HIGH		READY
33050	33050	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-PREFL-01	HIGH		READY
33051_prefl	33051	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33051_facelift	33051	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33052_prefl	33052	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33052_facelift	33052	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33053_prefl	33053	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33053_facelift	33053	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33054_prefl	33054	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33054_facelift	33054	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33055	33055	Wagon	E-Class S212	S212	5	EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	HIGH		READY
33056_prefl	33056	Hatchback	MINI R56	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33056_facelift	33056	Hatchback	MINI R56 Facelift	R56	3	EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33057	33057	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
33058_prefl	33058	Hatchback	Arosa I	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-3D-PREFL-01	HIGH	生产区间跨 2000 改款，按外廓长度拆分。	READY
33058_facelift	33058	Hatchback	Arosa I Facelift	6H	3	EU-SEAT-AROSA-I-6H-HATCHBACK-3D-FACELIFT-01	HIGH	生产区间跨 2000 改款，按外廓长度拆分。	READY
33059	33059	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33060	33060	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33061	33061	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33062	33062	MPV	Meriva B		5	EU-OPEL-MERIVA-B-MPV-5D-01	HIGH		READY
33063	33063	SUV	GL X164 Facelift	X164	5	EU-MERCEDES-BENZ-GL-X164-FACELIFT-SUV-5D-01	HIGH		READY
33064	33064	Coupe	GT MF4-S	MF4	2	EU-WIESMANN-GT-MF4-COUPE-2D-01	HIGH		READY
33065	33065	Coupe	GT MF4	MF4	2	EU-WIESMANN-GT-MF4-COUPE-2D-01	HIGH		READY
33066	33066	Coupe	GT MF5	MF5	2	EU-WIESMANN-GT-MF5-COUPE-2D-01	HIGH		READY
33067	33067	Convertible	Roadster MF4	MF4	2	EU-WIESMANN-ROADSTER-MF4-CONVERTIBLE-2D-01	HIGH		READY
33068	33068	Convertible	Roadster MF4-S	MF4	2	EU-WIESMANN-ROADSTER-MF4-CONVERTIBLE-2D-01	HIGH		READY
33069	33069	Convertible	Roadster MF5	MF5	2	EU-WIESMANN-ROADSTER-MF5-CONVERTIBLE-2D-01	HIGH		READY
33070	33070	Hatchback	Panda II	169	5	EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	HIGH		READY
33074_prefl	33074	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33074_facelift	33074	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33075_prefl	33075	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33075_facelift	33075	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33076_prefl	33076	Wagon	MINI Clubman R55	R55	3	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	HIGH	生产区间跨 2010 外观改款，按外廓长度和高度拆分。	READY
33076_facelift	33076	Wagon	MINI Clubman R55 Facelift	R55	3	EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度和高度拆分。	READY
33077_prefl	33077	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33077_facelift	33077	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33078_prefl	33078	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33078_facelift	33078	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33079_prefl	33079	Convertible	MINI Convertible R57	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33079_facelift	33079	Convertible	MINI Convertible R57 Facelift	R57	2	EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	HIGH	生产区间跨 2010 外观改款，按外廓长度拆分。	READY
33081	33081	Wagon	Audi F103	F103	3	EU-AUDI-80-F103-VARIANT-WAGON-3D-01	HIGH		READY
33084	33084	SUV	CX-9 I	TB	5	EU-MAZDA-CX-9-I-TB-SUV-PREFL-01	HIGH		READY
33085_prefl	33085	SUV	CX-9 I	TB	5	EU-MAZDA-CX-9-I-TB-SUV-PREFL-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33085_facelift2010	33085	SUV	CX-9 I Facelift 2010	TB	5	EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2010-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33085_facelift2013	33085	SUV	CX-9 I Facelift 2013	TB	5	EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2013-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33086_prefl	33086	SUV	CX-9 I	TB	5	EU-MAZDA-CX-9-I-TB-SUV-PREFL-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33086_facelift2010	33086	SUV	CX-9 I Facelift 2010	TB	5	EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2010-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33086_facelift2013	33086	SUV	CX-9 I Facelift 2013	TB	5	EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2013-01	MEDIUM	3.7 Ktype 范围覆盖改款前及两次外廓改款。	READY
33087	33087	SUV	CX-9 I	TB	5	EU-MAZDA-CX-9-I-TB-SUV-PREFL-01	MEDIUM	3.5 发动机仅对应首发外廓。	READY
33091	33091	Hatchback	Laguna II Phase I		5	EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	HIGH		READY
33092	33092	MPV	Grand Voyager V	RT	5	EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	HIGH		READY
33093	33093	Wagon	Laguna II Grandtour Phase I		5	EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	HIGH		READY
33094	33094	Coupe	Corvette C6	C6	3	EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	HIGH		READY
33095	33095	Sedan	Traction Avant 11B	11B	4	EU-CITROEN-TRACTION-AVANT-11B-NORMALE-SEDAN-4D-01	MEDIUM	输入车身形式修正为 11B Normale 四门轿车外廓。	READY
33096	33096	Sedan	Neon II	PL	4	EU-CHRYSLER-NEON-II-PL-SEDAN-4D-01	HIGH		READY
33123	33123	Convertible	Wind I	E33	2	EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	HIGH		READY
33124	33124	Convertible	Wind I	E33	2	EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	HIGH		READY
33125	33125	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33126	33126	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33127	33127	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33128	33128	Convertible	Mégane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	HIGH		READY
33129	33129	Pickup	L200 IV Facelift	KA4T	4	EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	HIGH	KA4T 两驱双排驾驶室与已确认双排外廓共组。	READY
33130	33130	Pickup	L200 IV Facelift	KB4T	4	EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	HIGH		READY
33131	33131	SUV	ix35	LM	5	EU-HYUNDAI-IX35-LM-SUV-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_4401-4500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-PREFL-01	4698	1786	1402	Auto-Data.net Mercedes-Benz E-Class Cabrio A207 generation	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-generation-3862
EU-MERCEDES-BENZ-E-CLASS-A207-CONVERTIBLE-FACELIFT-01	4703	1786	1398	Auto-Data.net Mercedes-Benz E-Class Cabrio A207 facelift generation	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a207-facelift-2013-generation-4119
EU-RENAULT-FLUENCE-I-L38-SEDAN-4D-01	4618	1809	1479	Cataloge.eu Renault Fluence 2010	https://www.cataloge.eu/renault/fluence-2010
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-PREFL-01	4698	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 E 200 CGI	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-e-200-cgi-blueefficiency-184hp-17394
EU-MERCEDES-BENZ-E-CLASS-C207-COUPE-FACELIFT-01	4703	1786	1397	Auto-Data.net Mercedes-Benz E-Class Coupe C207 facelift generation	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c207-facelift-2013-generation-3863
EU-CITROEN-C-ZERO-HATCHBACK-5D-01	3480	1475	1610	Auto-Data.net Citroën C-Zero model specifications	https://www.auto-data.net/en/citroen-c-zero-model-2051
EU-CITROEN-C4-PICASSO-I-UD-MPV-COIL-01	4470	1830	1680	Drive.place Citroën C4 Picasso I specifications	https://citroen.drive.place/c4_picasso/i/group_compactvan/58376
EU-CITROEN-C4-PICASSO-I-UD-MPV-AIRSUSP-01	4470	1830	1660	AVAuto Citroën C4 Picasso Exclusive specifications	https://www.avauto.fr/fiches_techniques/fiche-citroen-c4_picasso-1.6_hdi_110_exclusive-2012-55551.html
EU-CITROEN-C6-I-SEDAN-01	4908	1860	1464	Auto-Data.net Citroën C6 I 3.0 HDi	https://www.auto-data.net/en/citroen-c6-i-3.0-hdi-biturbo-v6-241hp-automatic-28076
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452	Auto-Data.net Peugeot 206 Sedan 1.4	https://www.auto-data.net/en/peugeot-206-sedan-1.4-75hp-5244
EU-VW-PASSAT-B6-3C5-WAGON-01	4774	1820	1517	Auto-Data.net Volkswagen Passat Variant B6 1.8 TSI	https://www.auto-data.net/en/volkswagen-passat-variant-b6-1.8-tsi-160hp-dsg-8893
EU-VW-PASSAT-B6-3C2-SEDAN-01	4765	1820	1472	Auto-Data.net Volkswagen Passat B6 1.8 TSI	https://www.auto-data.net/en/volkswagen-passat-b6-1.8-tsi-160hp-dsg-41959
EU-NISSAN-KUBISTAR-I-X76-VAN-01	4035	1672	1825	Anchor Vans Nissan Kubistar specifications	https://www.anchorvans.co.uk/specifications/kubistar
EU-MERCEDES-BENZ-SLS-AMG-C197-COUPE-01	4638	1939	1262	Mercedes-Benz Public Archive SLS AMG GT Coupé	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/SLS-AMG-GT-Coup-2012---2014.xhtml?oid=192608217
EU-RENAULT-SANDERO-I-BS-HATCHBACK-5D-01	4020	1746	1534	Auto-Data.net Dacia Sandero I 1.4 MPI	https://www.auto-data.net/en/dacia-sandero-i-1.4-mpi-75hp-46116
EU-RENAULT-SANDERO-I-STEPWAY-BS-SUV-5D-01	4024	1753	1590	Auto-Data.net Dacia Sandero I Stepway 1.6 8V	https://www.auto-data.net/en/dacia-sandero-i-stepway-1.6-8v-87hp-46139
EU-BMW-7-SERIES-E23-SEDAN-4D-01	4860	1800	1430	Auto-Data.net BMW 7 Series E23 732i	https://www.auto-data.net/en/bmw-7-series-e23-732i-197hp-9756
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464	Automobile-Catalog 2010 BMW 523i Steptronic	https://www.automobile-catalog.com/car/2010/1198220/bmw_523i_steptronic.html
EU-BMW-5-SERIES-F10-SEDAN-LCI-01	4907	1860	1464	Carfolio 2013 BMW 535i xDrive	https://www.carfolio.com/bmw-535i-xdrive-337062
EU-LEXUS-LS-XF40-SEDAN-SWB-01	5030	1875	1465	Auto-Data.net Lexus LS model specifications	https://www.auto-data.net/en/lexus-ls-model-650
EU-TAZZARI-ZERO-HATCHBACK-2D-01	2880	1560	1425	MotorAge Tazzari Zero specifications	https://www.motorage.it/2009/12/articolo-310/
EU-CHEVROLET-SPARK-III-M300-HATCHBACK-5D-01	3640	1597	1522	Auto-Data.net Chevrolet Spark III 1.0 16V	https://www.auto-data.net/en/chevrolet-spark-iii-1.0-16v-68hp-16922
EU-MERCEDES-BENZ-124-C124-COUPE-2D-01	4655	1740	1394	Mercedes-Benz Public Archive 300 CE-24	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-CE-24.xhtml?oid=4600
EU-MERCEDES-BENZ-124-W124-SEDAN-4D-01	4740	1740	1428	Mercedes-Benz Public Archive 300 E-24	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-E-24.xhtml?oid=5298
EU-MERCEDES-BENZ-124-A124-CONVERTIBLE-2D-01	4655	1740	1391	Mercedes-Benz Public Archive 300 CE-24 Cabriolet	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-CE-24-Cabriolet.xhtml?oid=4640
EU-ASTON-MARTIN-RAPIDE-I-HATCHBACK-5D-01	5019	1929	1360	Automobile-Catalog 2010 Aston Martin Rapide	https://www.automobile-catalog.com/car/2010/1186340/aston_martin_rapide.html
EU-MERCEDES-BENZ-GLK-X204-SUV-5D-PREFL-01	4528	1840	1689	Carfolio Mercedes-Benz GLK 350 4MATIC	https://www.carfolio.com/mercedes-benz-glk-350-4matic-176253
EU-VW-GOLF-VI-5K1-HATCHBACK-3D-01	4199	1779	1479	Auto-Data.net Volkswagen Golf VI 3-door	https://www.auto-data.net/en/volkswagen-golf-vi-3-door-2.0-tdi-140hp-dsg-8611
EU-VW-GOLF-VI-5K1-HATCHBACK-5D-01	4199	1786	1480	Auto-Data.net Volkswagen Golf VI 5-door	https://www.auto-data.net/en/volkswagen-golf-vi-5-door-1.2-tsi-105hp-dsg-41235
EU-VW-GOLF-VI-VARIANT-AJ5-WAGON-5D-01	4534	1781	1504	Auto-Data.net Volkswagen Golf VI Variant generation	https://www.auto-data.net/en/volkswagen-golf-vi-variant-generation-3784
EU-DACIA-DUSTER-I-SUV-PREFL-01	4315	1822	1625	Auto-Data.net Dacia Duster 1.5 dCi 4x2	https://www.auto-data.net/en/dacia-duster-1.5-dci-86hp-4x2-57153
EU-DACIA-DUSTER-I-SUV-FACELIFT-01	4315	1821	1625	Auto-Data.net Dacia Duster facelift 2013 1.6	https://www.auto-data.net/en/dacia-duster-facelift-2013-1.6-105hp-19702
EU-FERRARI-458-ITALIA-F142-COUPE-01	4527	1937	1213	Auto-Data.net Ferrari 458 Italia 4.5 V8	https://www.auto-data.net/en/ferrari-458-italia-4.5-v8-570hp-18350
EU-MERCEDES-BENZ-M-CLASS-W164-FACELIFT-SUV-5D-01	4781	1911	1815	Mercedes-Benz Public Archive ML 300 CDI 4MATIC BlueEFFICIENCY	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-300-CDI-4MATIC-BlueEFFICIENCY-2010---2011.xhtml?oid=191414613
EU-VW-GOLF-V-HATCHBACK-3D-01	4204	1759	1485	Auto-Data.net Volkswagen Golf V 3-door	https://www.auto-data.net/en/volkswagen-golf-v-3-door-1.4-tsi-140hp-dsg-51681
EU-VW-GOLF-V-HATCHBACK-5D-01	4204	1759	1485	Auto-Data.net Volkswagen Golf V 5-door	https://www.auto-data.net/en/volkswagen-golf-v-5-door-1.6-102hp-51656
EU-VW-GOLF-V-VARIANT-WAGON-5D-01	4556	1781	1504	Auto-Data.net Volkswagen Golf V Variant 1.6	https://www.auto-data.net/en/volkswagen-golf-v-variant-1.6-102hp-8643
EU-VW-JETTA-III-1K2-SEDAN-4D-01	4554	1781	1459	Auto-Data.net Volkswagen Jetta V generation	https://www.auto-data.net/en/volkswagen-jetta-v-generation-1910
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-4MATIC-PREFL-01	4868	1854	1470	Auto-Data.net Mercedes-Benz E-Class W212 E 350 CDI 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-350-cdi-blueefficiency-v6-231hp-4matic-7g-tronic-17369
EU-MINI-MINI-R56-HATCHBACK-3D-01	3699	1683	1407	Auto-Data.net MINI Hatch R56 Cooper	https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327
EU-MINI-MINI-R56-HATCHBACK-3D-FACELIFT-01	3723	1683	1407	Automobile-Catalog 2010 MINI One facelift	https://www.automobile-catalog.com/car/2010/1754510/mini_one.html
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-PREFL-01	3714	1683	1407	Auto-Data.net MINI Hatch R56 Cooper S	https://www.auto-data.net/en/mini-hatch-r56-cooper-s-1.6-i-16v-turbo-175hp-15328
EU-MINI-MINI-R56-HATCHBACK-COOPER-S-3D-FACELIFT-01	3729	1683	1407	Automobile-Catalog 2010 MINI Cooper S facelift	https://www.automobile-catalog.com/car/2010/1754660/mini_cooper_s.html
EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01	4895	1854	1515	Mercedes-Benz Public Archive E 350 CDI BlueEFFICIENCY Estate	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/E-350-CDI-BlueEFFICIENCY-2010---2013.xhtml?oid=188823505
EU-VW-LUPO-I-6X-HATCHBACK-3D-01	3530	1640	1460	AutoEvolution Volkswagen Lupo 1998	https://www.autoevolution.com/cars/volkswagen-lupo-1998.html
EU-SEAT-AROSA-I-6H-HATCHBACK-3D-PREFL-01	3536	1639	1460	Automobile-Catalog 1998 SEAT Arosa 1.0	https://www.automobile-catalog.com/car/1998/3070955/seat_arosa_1_0.html
EU-SEAT-AROSA-I-6H-HATCHBACK-3D-FACELIFT-01	3551	1639	1460	Automobile-Catalog 2001 SEAT Arosa 1.0	https://www.automobile-catalog.com/car/2001/3071015/seat_arosa_1_0.html
EU-OPEL-MERIVA-B-MPV-5D-01	4288	1812	1615	Auto-Data.net Opel Meriva B specifications	https://www.auto-data.net/en/opel-meriva-b-1.3-cdti-75hp-17003
EU-MERCEDES-BENZ-GL-X164-FACELIFT-SUV-5D-01	5099	1920	1840	Auto-Data.net Mercedes-Benz GL X164 facelift GL 350 CDI BlueTEC	https://www.auto-data.net/en/mercedes-benz-gl-x164-facelift-2009-gl-350-cdi-bluetec-211hp-4matic-g-tronic-27877
EU-WIESMANN-GT-MF4-COUPE-2D-01	4230	1880	1190	UltimateSpecs Wiesmann GT MF4	https://www.ultimatespecs.com/car-specs/Wiesmann/38767/Wiesmann-GT-MF4.html
EU-WIESMANN-GT-MF5-COUPE-2D-01	4220	1950	1180	UltimateSpecs Wiesmann GT MF5	https://www.ultimatespecs.com/car-specs/Wiesmann/38768/Wiesmann-GT-MF5.html
EU-WIESMANN-ROADSTER-MF4-CONVERTIBLE-2D-01	4230	1880	1190	Carfolio Wiesmann Roadster MF4	https://www.carfolio.com/wiesmann-roadster-mf4-235301
EU-WIESMANN-ROADSTER-MF5-CONVERTIBLE-2D-01	4220	1950	1180	Carfolio Wiesmann Roadster MF5	https://www.carfolio.com/wiesmann-roadster-mf5-235268
EU-FIAT-PANDA-II-169-HATCHBACK-5D-01	3538	1589	1540	Auto-Data.net Fiat Panda II 169 1.2 MPI	https://www.auto-data.net/en/fiat-panda-ii-169-1.2-mpi-60hp-6903
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-PREFL-01	3937	1683	1426	Automobile-Catalog 2010 MINI Cooper Clubman	https://www.automobile-catalog.com/car/2010/1753175/mini_cooper_clubman.html
EU-MINI-MINI-R55-CLUBMAN-WAGON-3D-FACELIFT-01	3961	1683	1426	Automobile-Catalog 2010 MINI Cooper Clubman facelift	https://www.automobile-catalog.com/car/2010/1754750/mini_cooper_clubman.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-PREFL-01	3958	1683	1432	Automobile-Catalog 2010 MINI Cooper S Clubman	https://www.automobile-catalog.com/car/2010/1753625/mini_cooper_s_clubman.html
EU-MINI-MINI-R55-CLUBMAN-COOPER-S-WAGON-3D-FACELIFT-01	3961	1683	1432	Automobile-Catalog 2010 MINI Cooper S Clubman facelift	https://www.automobile-catalog.com/car/2010/1754840/mini_cooper_s_clubman.html
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-01	3699	1683	1414	Auto-Data.net MINI Convertible R57 Cooper	https://www.auto-data.net/en/mini-convertible-r57-cooper-1.6-120hp-21561
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-FACELIFT-01	3723	1683	1414	Automobile-Catalog 2010 MINI Cooper Convertible facelift	https://www.automobile-catalog.com/car/2010/1754915/mini_cooper_convertible.html
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-01	3714	1683	1414	Auto-Data.net MINI Convertible R57 Cooper S	https://www.auto-data.net/en/mini-convertible-r57-cooper-s-1.6i-16v-turbo-175hp-15325
EU-MINI-MINI-R57-CONVERTIBLE-COOPER-S-FACELIFT-01	3729	1683	1414	Automobile-Catalog 2010 MINI Cooper S Convertible facelift	https://www.automobile-catalog.com/car/2010/1755020/mini_cooper_s_convertible_automatic.html
EU-AUDI-80-F103-VARIANT-WAGON-3D-01	4380	1626	1456	Automobile-Catalog 1967 Audi 80 Variant	https://www.automobile-catalog.com/car/1967/74420/audi_80_variant.html
EU-MAZDA-CX-9-I-TB-SUV-PREFL-01	5074	1936	1728	Auto-Data.net Mazda CX-9 I generation	https://www.auto-data.net/en/mazda-cx-9-i-generation-2424
EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2010-01	5085	1935	1727	Auto-Data.net Mazda CX-9 I facelift 2010 generation	https://www.auto-data.net/en/mazda-cx-9-i-facelift-2010-generation-7034
EU-MAZDA-CX-9-I-TB-SUV-FACELIFT-2013-01	5232	1935	1727	Auto-Data.net Mazda CX-9 I facelift 2013 generation	https://www.auto-data.net/en/mazda-cx-9-i-facelift-2013-generation-7035
EU-RENAULT-LAGUNA-II-PHASE-I-HATCHBACK-01	4576	1772	1429	Auto-Data.net Renault Laguna model specifications	https://www.auto-data.net/en/renault-laguna-model-1016
EU-CHRYSLER-GRAND-VOYAGER-V-RT-MPV-5D-01	5143	1954	1750	Automobile-Catalog 2008 Chrysler Grand Voyager 2.8 CRD	https://www.automobile-catalog.com/car/2008/1211195/chrysler_grand_voyager_2_8_crd_limited.html
EU-RENAULT-LAGUNA-II-PHASE-I-WAGON-01	4695	1772	1443	Auto-Data.net Renault Laguna model specifications	https://www.auto-data.net/en/renault-laguna-model-1016
EU-CHEVROLET-CORVETTE-C6-COUPE-BASE-01	4435	1844	1244	Automobile-Catalog 2008 Corvette C6 Coupe Europe	https://www.automobile-catalog.com/car/2008/479585/corvette_c6_coupe_6-speed.html
EU-CITROEN-TRACTION-AVANT-11B-NORMALE-SEDAN-4D-01	4650	1790	1540	Stellantis Media Citroën Traction Avant 11B Normale	https://www.media.stellantis.com/at-de/citroen/press/100-jahre-citroen-traction-avant-erstes-franzosisches-fahrzeug-mit-frontantrieb-in-grossserienproduktion
EU-CHRYSLER-NEON-II-PL-SEDAN-4D-01	4390	1715	1421	Auto-Data.net Chrysler Neon II 2.0 16V	https://www.auto-data.net/en/chrysler-neon-ii-2.0-16v-133hp-14780
EU-RENAULT-WIND-I-CONVERTIBLE-2D-01	3833	1689	1381	Auto-Data.net Renault Wind 1.2 TCe	https://www.auto-data.net/en/renault-wind-1.2-tce-101hp-33940
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-2D-01	4485	1811	1434	Auto-Data.net Renault Mégane III CC generation	https://www.auto-data.net/en/renault-megane-iii-cc-generation-3773
EU-MITSUBISHI-L200-IV-KB4T-DOUBLE-CAB-PICKUP-01	5185	1750	1775	Auto-Data.net Mitsubishi L200 IV Double Cab facelift 2010	https://www.auto-data.net/en/mitsubishi-l200-iv-double-cab-facelift-2010-generation-3976
EU-HYUNDAI-IX35-LM-SUV-5D-01	4410	1820	1660	Auto-Data.net Hyundai ix35 2.0 CVVT	https://www.auto-data.net/en/hyundai-ix35-2.0-cvvt-163hp-18179
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_4401-4500_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_4401-4500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_4401-4500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（5159 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2243 行）

- 尺寸冲突协调：
  - EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-01 -> EU-MERCEDES-BENZ-E-CLASS-S212-WAGON-PREFL-02：4895x1854x1512 与 4895x1854x1515，创建新尺寸组
