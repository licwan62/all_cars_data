# 任务：all 第 1201-1300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0013__9e1aedd0


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1201-1300 行

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
all 第 1201-1300 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A4-B9-ALLROAD-WAGON-01	4750	1842	1493
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A4-B9-SEDAN-PREFL-01	4726	1842	1427
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-BMW-1-E82-COUPE-01	4360	1748	1423
EU-BMW-1-E87-HATCHBACK-5D-FACELIFT-01	4239	1748	1421
EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430
EU-BMW-1-F20-HATCHBACK-5D-01	4329	1765	1421
EU-BMW-1-F20-HATCHBACK-5D-M140-01	4324	1765	1411
EU-BMW-1-F21-HATCHBACK-3D-01	4329	1765	1421
EU-BMW-1-F21-HATCHBACK-3D-M140-01	4324	1765	1411
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E36-COMPACT-HATCHBACK-01	4210	1698	1393
EU-BMW-3-E46-COMPACT-HATCHBACK-01	4262	1751	1408
EU-BMW-3-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372
EU-BMW-3-E46-CONVERTIBLE-PREFL-01	4488	1757	1372
EU-BMW-3-E46-COUPE-FACELIFT-01	4488	1757	1369
EU-BMW-3-E46-COUPE-PREFL-01	4490	1755	1370
EU-BMW-3-E46-SEDAN-FACELIFT-01	4471	1739	1415
EU-BMW-3-E46-SEDAN-PREFL-01	4471	1739	1415
EU-BMW-3-E46-WAGON-FACELIFT-01	4478	1739	1409
EU-BMW-3-E46-WAGON-PREFL-01	4478	1739	1409
EU-BMW-3-E90-SEDAN-FACELIFT-01	4531	1817	1421
EU-BMW-3-E90-SEDAN-PREFL-01	4520	1817	1421
EU-BMW-3-E91-WAGON-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-PREFL-01	4520	1817	1418
EU-BMW-3-E93-CONVERTIBLE-FACELIFT-01	4612	1782	1384
EU-BMW-3-E93-CONVERTIBLE-PREFL-01	4580	1782	1384
EU-BMW-3-F31-WAGON-PREFL-RWD-01	4624	1811	1429
EU-BMW-3-F31-WAGON-PREFL-XDRIVE-01	4624	1811	1434
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508
EU-BMW-340-SEDAN-01	4600	1765	1630
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498
EU-BMW-502-SEDAN-01	4730	1780	1530
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275
EU-DACIA-LOGAN-I-MCV-FACELIFT-01	4473	1740	1640
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1539
EU-DACIA-LOGAN-II-SEDAN-PREFL-01	4346	1733	1517
EU-DACIA-SANDERO-I-HATCHBACK-01	4020	1746	1534
EU-FORD-FOCUS-III-FACELIFT-VAN-5D-01	4358	1823	1484
EU-FORD-FOCUS-III-PREFL-VAN-5D-01	4358	1823	1484
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481
EU-MITSUBISHI-L200-IV-PICKUP-DOUBLECAB-FACELIFT-01	5185	1750	1775
EU-NISSAN-NV300-X82-COMBI-L1H1-01	4999	1956	1971
EU-NISSAN-NV300-X82-COMBI-L2H1-01	5399	1956	1971
EU-OPEL-ASTRA-J-SPORTS-TOURER-01	4698	1814	1535
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448
EU-RENAULT-CLIO-IV-FACELIFT-WAGON-01	4267	1732	1445
EU-RENAULT-TWINGO-III-HATCHBACK-01	3595	1647	1557
EU-TESLA-MODEL-S-FACELIFT-2016-HATCHBACK-01	4979	1964	1445
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445
EU-VW-CRAFTER-II-CHASSIS-DCAB-L3-01	5996	2040	2321
EU-VW-CRAFTER-II-CHASSIS-DCAB-L4-01	6846	2040	2321
EU-VW-CRAFTER-II-CHASSIS-SCAB-L3-01	5996	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L4-01	6846	2040	2305
EU-VW-CRAFTER-II-CHASSIS-SCAB-L5-01	7211	2040	2305
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492
EU-VW-GOLF-VII-SPORTSVAN-FACELIFT-01	4351	1807	1613
EU-VW-GOLF-VII-VARIANT-FACELIFT-01	4567	1799	1515
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A5	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	140	190	Jan 2017	Feb 2020	2026-07-01	126165
BMW	3	340 I	Schrägheck	Heckantrieb	Benzin	265	360	Jul 2016	-	2024-03-01	126168
BMW	3	340 I Xdrive	Schrägheck	Allrad	Benzin	265	360	Jul 2016	-	2024-03-01	126169
Morgan	Four	2	Cabriolet	Heckantrieb	Benzin	106	144	Jan 2010	-	2024-03-01	126175
Mahindra	Goa	2.2 Crde AWD	Geländewagen geschlossen	Allrad	Diesel	85	116	Jan 2010	-	2024-03-01	126179
Audi	A5	2.0 Tfsi G-tron	Schrägheck	Frontantrieb	Benzin/Erdgas (CNG)	125	170	Feb 2017	Feb 2020	2024-03-01	126180
Alpina	B7	Biturbo Heckantrieb	Stufenheck	Heckantrieb	Benzin	447	608	Mar 2017	Dec 2022	2026-06-01	126181
Audi	A4 b9	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	120	163	Sep 2016	Nov 2019	2024-03-01	126182
Audi	A4 b9 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	120	163	Sep 2016	Sep 2018	2024-03-01	126183
Audi	A4 b9 avant	2.0 Tfsi G-tron	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	125	170	Nov 2016	Oct 2019	2024-03-01	126184
BMW	5	520 D	Kombi	Heckantrieb	Diesel	120	163	Mar 2017	-	2024-03-01	126185
Renault	Clio iv	0.9 TCE 90 LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	66	90	Jun 2016	Aug 2021	2026-05-01	126186
Peugeot	3008 ii	1.6 Bluehdi 100	SUV	Frontantrieb	Diesel	73	100	Nov 2016	Dec 2019	2025-02-03	126187
Peugeot	3008 ii	1.6 Bluehdi 115	SUV	Frontantrieb	Diesel	85	116	Nov 2016	Dec 2019	2024-11-01	126188
Peugeot	3008 ii	2.0 Bluehdi 136	SUV	Frontantrieb	Diesel	100	136	Nov 2016	-	2024-11-01	126189
Peugeot	5008	1.6 Bluehdi 115	Großraumlimousine	Frontantrieb	Diesel	85	116	Dec 2016	Nov 2019	2024-03-01	126190
Peugeot	5008	2.0 Bluehdi 136	Großraumlimousine	Frontantrieb	Diesel	100	136	Dec 2016	-	2024-03-01	126191
Tesla	Model s	P85	Schrägheck	Heckantrieb	Elektro	350	476	May 2013	Dec 2014	2024-03-01	126196
Tesla	Model s	85D AWD	Schrägheck	Allrad	Elektro	290	394	Oct 2014	Jul 2015	2024-03-01	126198
Tesla	Model s	P85d AWD	Schrägheck	Allrad	Elektro	543	738	Oct 2014	Oct 2015	2024-03-01	126200
Dacia	Sandero	1.0 SCE 75	Schrägheck	Frontantrieb	Benzin	54	73	Dec 2016	Sep 2020	2025-12-01	126214
Dacia	Logan	1.0 SCE 75	Kombi	Frontantrieb	Benzin	54	73	Dec 2016	-	2024-03-01	126215
Alpina	B5	Biturbo	Stufenheck	Allrad	Benzin	447	608	Mar 2017	Jun 2020	2024-03-01	126216
Alpina	B5	Biturbo	Kombi	Allrad	Benzin	447	608	Mar 2017	Jun 2020	2024-03-01	126217
Nissan	Primastar	2	Kasten	Frontantrieb	Benzin	86	117	Apr 2006	-	2024-03-01	126218
Nissan	Primastar	2	Bus	Frontantrieb	Benzin	86	117	Apr 2006	-	2024-03-01	126219
Nissan	Primastar	2	Pritsche/Fahrgestell	Frontantrieb	Benzin	88	120	Jul 2002	Aug 2006	2024-03-01	126220
Nissan	Primastar	2.5 DCI 150	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2006	-	2024-03-01	126221
BMW	5	530 D Xdrive	Stufenheck	Allrad	Diesel	183	249	Sep 2016	Jun 2020	2024-03-01	126257
Land Rover	Range rover velar	2.0 D180 TD4 4X4	SUV	Allrad	Diesel	132	180	Mar 2017	-	2024-03-01	126259
Land Rover	Range rover velar	2.0 D240 SD4 4X4	SUV	Allrad	Diesel	177	241	Mar 2017	-	2024-03-01	126260
Land Rover	Range rover velar	3.0 P380 Scv6 4X4	SUV	Allrad	Benzin	280	380	Mar 2017	-	2024-03-01	126261
Land Rover	Range rover velar	2.0 P250 SI4 4X4	SUV	Allrad	Benzin	184	250	Mar 2017	-	2024-03-01	126262
Jeep	Compass	2.0 CRD 4X4	SUV	Allrad	Diesel	125	170	Dec 2016	-	2024-03-01	126318
VW	Caddy iv	1.6 SRE	Großraumlimousine	Frontantrieb	Benzin	81	110	Nov 2015	Sep 2020	2025-06-01	126341
VW	Caddy iv	1.6 SRE	Kasten/Großraumlimousine	Frontantrieb	Benzin	81	110	Nov 2015	Sep 2020	2025-06-01	126342
Pagani	Huayra	6	Coupe	Heckantrieb	Benzin	537	730	Jun 2011	-	2024-03-01	126344
Donkervoort	D8	2.5 GTO Performance	Cabriolet	Heckantrieb	Benzin	280	381	Mar 2013	-	2024-03-01	126370
MIA Electric	Mia	Electric	Kasten/Schrägheck	Heckantrieb	Elektro	18	24	Jan 2011	Apr 2014	2024-03-01	126388
Renault	Clio iv	1.2 16V	Schrägheck	Frontantrieb	Benzin	55	75	Jun 2015	Aug 2021	2026-05-01	126404
Opel	Crossland x /	1.2	SUV	Frontantrieb	Benzin	96	131	Mar 2017	-	2024-03-01	126414
Opel	Crossland x /	1.2	SUV	Frontantrieb	Benzin	60	82	Mar 2017	-	2024-03-01	126415
Opel	Crossland x /	1.2	SUV	Frontantrieb	Benzin	81	110	Mar 2017	-	2024-03-01	126416
Opel	Crossland x /	1.6 Turbo D	SUV	Frontantrieb	Diesel	73	99	Mar 2017	May 2018	2025-02-03	126417
Opel	Crossland x /	1.6 Turbo D	SUV	Frontantrieb	Diesel	88	120	Mar 2017	May 2018	2025-02-03	126418
Maserati	Quattroporte vi	3	Stufenheck	Heckantrieb	Benzin	257	350	Oct 2016	-	2024-03-01	126475
Volvo	Xc60 ii	D4 AWD	SUV	Allrad	Diesel	140	190	Mar 2017	Dec 2021	2024-05-01	126478
Volvo	Xc60 ii	D5 AWD	SUV	Allrad	Diesel	173	235	Mar 2017	Dec 2022	2024-05-01	126479
Volvo	Xc60 ii	T5 AWD	SUV	Allrad	Benzin	187	254	Mar 2017	Dec 2021	2024-05-01	126480
Volvo	Xc60 ii	T6 AWD	SUV	Allrad	Benzin	235	320	Mar 2017	Dec 2021	2024-05-01	126481
Volvo	Xc60 ii	T8 Hybrid AWD	SUV	Allrad	Benzin/Elektro	299	407	Mar 2017	Dec 2022	2024-05-01	126482
BMW	1	118 I	Schrägheck	Heckantrieb	Benzin	95	129	Sep 2006	Feb 2008	2024-03-01	126495
Honda	Civic x	1.5 Vtec	Schrägheck	Frontantrieb	Benzin	134	182	Feb 2017	Dec 2022	2024-03-01	126522
Honda	Civic x	1.0 Vtec	Schrägheck	Frontantrieb	Benzin	95	129	Feb 2017	Dec 2022	2024-03-01	126524
Land Rover	Range rover velar	3.0 D300 Sdv6 4X4	SUV	Allrad	Diesel	221	300	Mar 2017	-	2024-03-01	126526
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	74	101	May 2017	-	2024-03-01	126554
Ford	Fiesta vii	1.0 Ecoboost	Schrägheck	Frontantrieb	Benzin	92	125	May 2017	-	2024-03-01	126555
Ford	Fiesta vii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	63	86	May 2017	-	2025-06-01	126556
Ford	Fiesta vii	1.5 Tdci	Schrägheck	Frontantrieb	Diesel	88	120	May 2017	-	2024-03-01	126557
Ford	Fiesta vii	1.1 Ti-vct	Schrägheck	Frontantrieb	Benzin	52	71	May 2017	-	2025-06-01	126566
Ford	Fiesta vii	1.1 Ti-vct	Schrägheck	Frontantrieb	Benzin	63	86	May 2017	-	2024-03-01	126567
Ford	Gt	3.5 Ecoboost V6	Coupe	Heckantrieb	Benzin	483	657	Sep 2016	-	2024-03-01	126569
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	75	102	Feb 2017	Jun 2024	2024-05-01	126571
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	103	140	Feb 2017	-	2024-03-01	126572
MAN	Tge	2.0 TDI	Kasten	Frontantrieb	Diesel	130	177	Feb 2017	-	2024-03-01	126573
MAN	Tge	2.0 TDI AWD	Kasten	Allrad	Diesel	103	140	Apr 2017	-	2024-03-01	126577
MAN	Tge	2.0 TDI AWD	Kasten	Allrad	Diesel	130	177	Mar 2017	-	2024-03-01	126578
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	75	102	Nov 2016	Jun 2024	2024-05-01	126581
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	103	140	Nov 2016	-	2024-03-01	126582
MAN	Tge	2.0 TDI	Pritsche/Fahrgestell	Frontantrieb	Diesel	130	177	Nov 2016	-	2024-03-01	126583
Opel	Insignia b grand sport	1.5	Schrägheck	Frontantrieb	Benzin	103	140	Mar 2017	-	2024-03-01	126593
Opel	Insignia b grand sport	1.5	Schrägheck	Frontantrieb	Benzin	121	165	Mar 2017	-	2024-03-01	126596
Opel	Insignia b grand sport	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Mar 2017	-	2024-03-01	126598
Opel	Insignia b grand sport	1.6 Cdti	Schrägheck	Frontantrieb	Diesel	100	136	Mar 2017	-	2024-03-01	126599
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	125	170	Mar 2017	-	2024-03-01	126600
Opel	Insignia b grand sport	2.0 Biturbo Diesel 4X4	Schrägheck	Allrad	Diesel	154	210	Mar 2017	-	2026-04-01	126601
VW	Crafter	2.0 TDI 4motion	Kasten	Allrad	Diesel	130	177	Mar 2017	-	2024-03-01	126602
Opel	Insignia b grand sport	2.0 4X4	Schrägheck	Allrad	Benzin	191	260	Mar 2017	-	2024-03-01	126603
Opel	Insignia b sports tourer	1.5	Kombi	Frontantrieb	Benzin	103	140	Mar 2017	-	2024-03-01	126609
Opel	Insignia b sports tourer	1.5	Kombi	Frontantrieb	Benzin	121	165	Mar 2017	-	2024-03-01	126610
Opel	Insignia b sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	81	110	Mar 2017	-	2024-03-01	126611
Opel	Insignia b sports tourer	1.6 Cdti	Kombi	Frontantrieb	Diesel	100	136	Mar 2017	-	2024-03-01	126612
Opel	Insignia b sports tourer	2.0 Cdti	Kombi	Frontantrieb	Diesel	125	170	Mar 2017	-	2024-03-01	126615
Opel	Insignia b sports tourer	2.0 Biturbo Diesel 4X4	Kombi	Allrad	Diesel	154	210	Mar 2017	-	2026-04-01	126616
Opel	Insignia b sports tourer	2.0 4X4	Kombi	Allrad	Benzin	191	260	Mar 2017	-	2024-03-01	126617
Audi	A5	3.0 TDI Quattro	Coupe	Allrad	Diesel	210	286	Jan 2017	Feb 2020	2024-03-01	126622
Audi	A5	3.0 TDI Quattro	Schrägheck	Allrad	Diesel	210	286	Jan 2017	Feb 2020	2024-03-01	126623
Audi	A5	3.0 TDI Quattro	Cabriolet	Allrad	Diesel	210	286	Nov 2016	Dec 2019	2024-03-01	126624
VW	Golf vii	E-golf	Schrägheck	Frontantrieb	Elektro	100	136	Dec 2016	Jan 2021	2024-03-01	126625
Dacia	Duster	1.5 DCI	SUV	Frontantrieb	Diesel	81	110	Aug 2013	Jan 2018	2024-03-01	126627
Nissan	Nv300	1.6 DCI 125	Pritsche/Fahrgestell	Frontantrieb	Diesel	92	125	Sep 2016	-	2024-03-01	126641
Nissan	Nv300	1.6 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Sep 2016	-	2024-03-01	126643
Opel	Astra j	1.6 Turbo 4X4	Schrägheck	Allrad	Benzin	132	180	Dec 2009	Oct 2015	2024-03-01	126646
Renault	Twingo	1.2 16V	Schrägheck	Heckantrieb	Benzin	55	75	Mar 2008	Sep 2014	2026-05-01	126647
Ford	Focus i	1.4 16V	Schrägheck	Heckantrieb	Benzin	55	75	Oct 1998	Sep 1999	2024-03-01	126648
VW	Polo	75 1.6 4motion	Schrägheck	Allrad	Benzin	55	75	Aug 1995	Oct 1999	2024-03-01	126649
Subaru	Legacy iv	2.0 2WD	Stufenheck	Heckantrieb	Benzin	132	179	Aug 2005	Mar 2012	2024-03-01	126650
Toyota	Camry	2.5	Stufenheck	Frontantrieb	Benzin	131	178	Oct 2011	Mar 2018	2024-05-01	126651
Mitsubishi	L200	2.5 Di-d	Pritsche/Fahrgestell	Heckantrieb	Diesel	94	128	Aug 2007	Dec 2015	2024-03-01	126659
Mitsubishi	Outlander iii	2.4 4WD	SUV	Allrad	Benzin	123	167	Oct 2012	Dec 2022	2025-06-01	126681


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理外廓完成首轮聚类：16 个历史尺寸组直接复用，未重复输出来源；本轮首次闭合 18 个新尺寸组。
* Fiesta VII 因三门和五门长度不同，6 个 Ktype 均拆分为 `3dr`、`5dr` 派生行；Twingo II 的生产区间跨越改款，拆分为 `prefl`、`facelift`。相关外廓差异由车型规格资料支持。([autocatalogarchive.com][1])
* Crossland X、XC60 II、Civic X、Velar、Compass II、Ford GT 和 Insignia B 两种车身已完成三维及不含后视镜宽度闭合。([Stellantis Media][2])
* 当前剩余阻塞主要集中在商用车多轴距/多车顶组合，以及输入动力或驱动字段存在冲突的异常 Ktype。

## 当前批次进度

* 输入 Ktype：100
* 当前映射行：107
* READY Ktype：72
* PENDING Ktype：28
* READY 映射行：79
* PENDING 映射行：28
* 已确认尺寸组：34

  * 历史尺寸组复用：16
  * 本轮首次创建：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126165	126165	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Sportback 五门外廓。	READY
126168	126168	Hatchback	3 Series Gran Turismo (F34)	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 五门 Gran Turismo 外廓。	READY
126169	126169	Hatchback	3 Series Gran Turismo (F34)	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 五门 Gran Turismo 外廓。	READY
126175	126175	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-CONVERTIBLE-01	MEDIUM	输入 Four/2 与 Plus 4 2.0 版本对应。	READY
126179	126179	SUV	Goa		5		LOW	现有资料对 Goa 2.2 CRDe AWD 的物理外廓数据冲突。	PENDING: 车型外廓与三维来源冲突待消解
126180	126180	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Sportback 五门外廓。	READY
126181	126181	Sedan	B7 (G12)	G12	4	EU-ALPINA-B7-G12-SEDAN-01	MEDIUM	G12 长轴轿车外廓；驱动差异不单独建组。	READY
126182	126182	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-PREFL-01	HIGH	改款前 B9 轿车外廓。	READY
126183	126183	Wagon	A4 B9 Avant	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	B9 Avant 外廓。	READY
126184	126184	Wagon	A4 B9 Avant	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	B9 Avant 外廓。	READY
126185	126185	Wagon	5 Series Touring (G31)	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31 改款前 Touring 外廓。	READY
126186	126186	Hatchback	Clio IV facelift	X98	5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	HIGH	Clio IV 改款后五门外廓。	READY
126187	126187	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126188	126188	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126189	126189	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126190	126190	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入 MPV 标签按第二代 5008 的 SUV 物理车身归一。	READY
126191	126191	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入 MPV 标签按第二代 5008 的 SUV 物理车身归一。	READY
126196	126196	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126198	126198	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126200	126200	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126214	126214	Hatchback	Sandero II facelift	B52	5	EU-DACIA-SANDERO-II-FACELIFT-HATCHBACK-01	HIGH	第二代 Sandero 改款后外廓。	READY
126215	126215	Wagon	Logan II MCV	K52	5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代 Logan MCV 外廓。	READY
126216	126216	Sedan	B5 (G30)	G30	4		LOW	现有资料对 ALPINA 前后外廓与标准 G30 的长度口径不一致。	PENDING: ALPINA B5 Sedan 直接规格口径待闭合
126217	126217	Wagon	B5 Touring (G31)	G31	5		LOW	现有资料对 ALPINA Touring 的长度和高度口径不一致。	PENDING: ALPINA B5 Touring 直接规格口径待闭合
126218	126218	Van	Primastar I	X83			LOW	Kasten 未区分轴距和车顶组合。	PENDING: Primastar Kasten 轴距与车顶分支未确认
126219	126219	MPV	Primastar I	X83			LOW	Bus 未区分短轴/长轴及车身高度。	PENDING: Primastar Bus 物理分支未确认
126220	126220	Pickup	Primastar I	X83			LOW	Pritsche/Fahrgestell 未区分驾驶室、轴距及车架长度。	PENDING: Primastar chassis cab 分支未确认
126221	126221	Pickup	Primastar I	X83			LOW	Pritsche/Fahrgestell 未区分驾驶室、轴距及车架长度。	PENDING: Primastar chassis cab 分支未确认
126257	126257	Sedan	5 Series (G30)	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	G30 改款前轿车外廓。	READY
126259	126259	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126260	126260	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126261	126261	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126262	126262	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126318	126318	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH	第二代 Compass MP 四驱外廓。	READY
126341	126341	MPV	Caddy IV	2K			LOW	输入未区分标准轴距与 Maxi 长轴。	PENDING: Caddy passenger 标准轴距/Maxi 分支未确认
126342	126342	Van	Caddy IV	2K			LOW	组合标签未区分标准轴距/Maxi及厢式车门体。	PENDING: Caddy van 物理分支未确认
126344	126344	Coupe	Huayra		2	EU-PAGANI-HUAYRA-COUPE-01	HIGH	Huayra Coupe 标准外廓。	READY
126370	126370	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	D8 GTO Performance 外廓。	READY
126388	126388	Van	Mia		3		LOW	组合标签可能覆盖 Mia 短车身与 Mia L/Mia U 长车身。	PENDING: Mia 车身长度分支未确认
126404	126404	Hatchback	Clio IV facelift	X98	5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	HIGH	Clio IV 改款后五门外廓。	READY
126414	126414	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126415	126415	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126416	126416	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126417	126417	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126418	126418	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126475	126475	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH	M156 轿车外廓。	READY
126478	126478	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126479	126479	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126480	126480	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126481	126481	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126482	126482	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126495	126495	Hatchback	1 Series (E87) pre-facelift	E87	5	EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	HIGH	E87 五门改款前外廓。	READY
126522	126522	Hatchback	Civic X	FK7	5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	1.5 VTEC 五门掀背 FK7。	READY
126524	126524	Hatchback	Civic X	FK6	5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	1.0 VTEC 五门掀背 FK6，与 FK7 共用外廓。	READY
126526	126526	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126554_3dr	126554	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126554_5dr	126554	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126555_3dr	126555	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126555_5dr	126555	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126556_3dr	126556	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126556_5dr	126556	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126557_3dr	126557	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126557_5dr	126557	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126566_3dr	126566	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126566_5dr	126566	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126567_3dr	126567	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126567_5dr	126567	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126569	126569	Coupe	Ford GT II		2	EU-FORD-GT-II-COUPE-01	HIGH	第二代 Ford GT 标准外廓。	READY
126571	126571	Van	TGE I				LOW	Kasten 同时覆盖多个轴距与车顶高度，动力不能唯一确定外廓。	PENDING: TGE Kasten L/H 分支未确认
126572	126572	Van	TGE I				LOW	Kasten 同时覆盖多个轴距与车顶高度，动力不能唯一确定外廓。	PENDING: TGE Kasten L/H 分支未确认
126573	126573	Van	TGE I				LOW	Kasten 同时覆盖多个轴距与车顶高度，动力不能唯一确定外廓。	PENDING: TGE Kasten L/H 分支未确认
126577	126577	Van	TGE I				LOW	Kasten 同时覆盖多个轴距与车顶高度，动力不能唯一确定外廓。	PENDING: TGE Kasten L/H 分支未确认
126578	126578	Van	TGE I				LOW	Kasten 同时覆盖多个轴距与车顶高度，动力不能唯一确定外廓。	PENDING: TGE Kasten L/H 分支未确认
126581	126581	Pickup	TGE I				LOW	Pritsche/Fahrgestell 未区分单排/双排驾驶室及车架长度。	PENDING: TGE chassis cab 分支未确认
126582	126582	Pickup	TGE I				LOW	Pritsche/Fahrgestell 未区分单排/双排驾驶室及车架长度。	PENDING: TGE chassis cab 分支未确认
126583	126583	Pickup	TGE I				LOW	Pritsche/Fahrgestell 未区分单排/双排驾驶室及车架长度。	PENDING: TGE chassis cab 分支未确认
126593	126593	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126596	126596	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126598	126598	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126599	126599	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126600	126600	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126601	126601	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126602	126602	Van	Crafter II				LOW	4Motion Kasten 未区分轴距和车顶高度组合。	PENDING: Crafter II 4Motion L/H 分支未确认
126603	126603	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126609	126609	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126610	126610	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126611	126611	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126612	126612	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126615	126615	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126616	126616	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126617	126617	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126622	126622	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	F5 Coupe 外廓。	READY
126623	126623	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback 五门外廓。	READY
126624	126624	Convertible	A5 F5 Cabriolet	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	F5 Cabriolet 外廓。	READY
126625	126625	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH	改款后 e-Golf 五门外廓。	READY
126627	126627	SUV	Duster I facelift	H79	5	EU-DACIA-DUSTER-I-FACELIFT-SUV-01	HIGH	第一代 Duster 改款后 4x2 外廓。	READY
126641	126641	Pickup	NV300	X82			LOW	Pritsche/Fahrgestell 未区分驾驶室与底盘长度。	PENDING: NV300 chassis cab 分支未确认
126643	126643	Pickup	NV300	X82			LOW	Pritsche/Fahrgestell 未区分驾驶室与底盘长度。	PENDING: NV300 chassis cab 分支未确认
126646	126646	Hatchback	Astra J	P10	5		LOW	输入的 1.6 Turbo 4X4 与已知 Astra J 动力/驱动组合不一致。	PENDING: Ktype 车型身份冲突待核验
126647_facelift	126647	Hatchback	Twingo II facelift	CN0	3	EU-RENAULT-TWINGO-II-HATCHBACK-FACELIFT-01	MEDIUM	生产区间跨越外观改款；改款后分支。	READY
126647_prefl	126647	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-HATCHBACK-PREFL-01	MEDIUM	生产区间跨越外观改款；改款前分支。	READY
126648	126648	Hatchback	Focus I				LOW	输入未区分三门/五门，且直接规格来源存在长度与高度冲突。	PENDING: Focus I 门数与三维口径待闭合
126649	126649	Hatchback	Polo III	6N			LOW	1.6 4Motion 版本与该年款常规车型资料不一致。	PENDING: Ktype 车型身份待核验
126650	126650	Sedan	Legacy IV	BL	4		LOW	2WD/RWD、功率及结束年月与 BL 代车型资料相互冲突。	PENDING: Ktype 车型身份与市场版本待核验
126651	126651	Sedan	Camry XV50	XV50	4		LOW	生产区间跨越外观改款，尚未闭合改款前后物理分支。	PENDING: Camry XV50 facelift 分支待拆分
126659	126659	Pickup	L200 IV				LOW	Pritsche/Fahrgestell 未区分驾驶室，且区间跨越改款。	PENDING: L200 cab 与 facelift 分支待确认
126681	126681	SUV	Outlander III	GF/GG	5		LOW	生产区间跨越多次外观改款，需按外廓变化拆分。	PENDING: Outlander III facelift 分支待确认
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MORGAN-PLUS-4-CONVERTIBLE-01	4010	1720	1220	CarsGuide Morgan Plus 4 dimensions	https://www.carsguide.com.au/morgan/plus-4/car-dimensions
EU-ALPINA-B7-G12-SEDAN-01	5250	1902	1491	ALPINA B7 BITURBO official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/B7_BITURBO/epaper/ausgabe.pdf
EU-DACIA-SANDERO-II-FACELIFT-HATCHBACK-01	4057	1733	1523	Automoli Dacia Sandero II specifications	https://www.automoli.com/en/vehicles/dacia/sandero/sandero-ii-3954/
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	4803	2032	1665	Land Rover Range Rover Velar official brochure;CarsGuide 2017 Range Rover Velar dimensions	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/range-rover-velar/Range-Rover-Velar-Brochure-1L5601910000BGBEN01P_tcm295-607384.pdf;https://www.carsguide.com.au/land-rover/range-rover-velar/car-dimensions/2017
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644	Jeep All-New Compass official technical specifications	https://www.media.stellantis.com/uploads/nl/NL/SYSTEM_ARCHIVE/2017/JEEP/Schede_tecniche/170606_Jeep_Tech_Specs_All_New_Compass.pdf
EU-PAGANI-HUAYRA-COUPE-01	4605	2036	1169	Auto-Data Pagani Huayra specifications	https://www.auto-data.net/en/pagani-huayra-model-2122
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140	Donkervoort D8 GTO official heritage specifications;Automobile-Catalog 2013 D8 GTO Performance	https://www.donkervoort.com/en/models/heritage/donkervoort-d8-gto/;https://www.automobile-catalog.com/car/2013/2065370/donkervoort_s8_gto_performance.html
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Opel Crossland X official press specifications	https://www.media.stellantis.com/me-tr/opel-archive/press/turkey-yeni-opel-crossland-x-stil-sahibi-ve-havali
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars XC60 official dimensions	https://www.volvocars.com/uk/support/car/xc60/20w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434	Honda Civic 5 Door official brochure	https://www.honda.co.uk/content/dam/local/uk/brochures/cars/Civic-5-Door-Brochure.pdf
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford All-New Fiesta 2017 UK brochure;Automobile-Catalog 2017 Fiesta 1.5 TDCi	https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Fiesta-2017-UK.pdf;https://www.automobile-catalog.com/car/2017/2562950/ford_fiesta_1_5_tdci_85.html
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4065	1735	1476	Ford All-New Fiesta 2017 UK brochure;Automobile-Catalog 2017 Fiesta 1.5 TDCi	https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Fiesta-2017-UK.pdf;https://www.automobile-catalog.com/car/2017/2562950/ford_fiesta_1_5_tdci_85.html
EU-FORD-GT-II-COUPE-01	4779	2003	1109	Ford GT official EU technical specifications	https://fordmediacenter.nl/wp-content/uploads/2017/05/gt_technical_specs_EU.pdf
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall New Insignia official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/014_New_Insignia_Spec_PG_1_August_2017-1504607950.pdf
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1500	Vauxhall New Insignia official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/014_New_Insignia_Spec_PG_1_August_2017-1504607950.pdf
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1695	Automobile-Catalog 2016 Dacia Duster dCi 110 4x2	https://www.automobile-catalog.com/car/2016/2513870/dacia_duster_dci_110_4x2.html
EU-RENAULT-TWINGO-II-HATCHBACK-PREFL-01	3600	1654	1470	Automobile-Catalog Renault Twingo II 1.2 16V 75	https://www.automobile-catalog.com/car/2007/2956010/renault_twingo_1_2_16v_75_quickshift.html
EU-RENAULT-TWINGO-II-HATCHBACK-FACELIFT-01	3687	1654	1470	Automoli Renault Twingo II facelift specifications	https://www.automoli.com/en/vehicles/renault/twingo/twingo-ii-facelift-2011-3870/
```

## 下一步优先处理

1. 批量闭合 MAN TGE、VW Crafter II、Nissan Primastar/NV300 的轴距、车顶和单排/双排驾驶室分支，并优先复用现有 Crafter II 尺寸组。
2. 处理 Caddy IV、Mia、L200 与 Outlander III 的多外廓拆分。
3. 最后消解 Mahindra Goa、ALPINA B5、Astra J、Focus I、Polo、Legacy 和 Camry 的来源或输入身份冲突。

推进信号：CONTINUE

[1]: https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Fiesta-2017-UK.pdf?utm_source=chatgpt.com "ALL-NEW FIESTA"
[2]: https://www.media.stellantis.com/me-tr/opel-archive/press/turkey-yeni-opel-crossland-x-stil-sahibi-ve-havali?utm_source=chatgpt.com "Turkey - Yeni Opel Crossland X: Stil Sahibi ve Havali"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* Mahindra Goa 2.2 AWD 已按对应五门 SUV 规格闭合，长度采用该 2.2 版本的 4430 mm，不再沿用其他 Goa 年款的候选长度。([Mahindra][1])
* ALPINA B5 G30 轿车与 G31 Touring 已由同一份 B5 BITURBO 规格表闭合，二者三维均为 4956 × 1868 × 1466 mm，但因车身形式不同分别建组。([i.i-sgcm][2])
* Mia 已确认包含短车身 mia、长车身 mia L 和同尺寸商用 mia U 三个分支；mia L 与 mia U 复用同一长车身尺寸组。([汽车中心][3])
* MAN TGE 前驱厢式车按六个现有 Crafter II 尺寸组复用；前驱底盘驾驶室按单排/双排和 L3/L4 建立四个新组。官方配置表显示前驱底盘不覆盖超长 L5，因此未创建猜测性 L5 分支。([MAN Global][4])
* Astra J 与 Focus I 的异常驱动字段不再阻塞已经明确的物理车身；Focus I 三门和五门分别保留映射行，但复用相同三维尺寸组。([汽车数据网][5])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：84
* PENDING Ktype：16
* 当前映射行：134
* READY 映射行：118
* PENDING 映射行：16
* 当前已引用尺寸组：51
* 本轮首次创建尺寸组：11
* 本轮新增引用的历史尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126179	126179	SUV	Goa		5	EU-MAHINDRA-GOA-SUV-01	HIGH	五门 Goa SUV 外廓。	READY
126216	126216	Sedan	B5 (G30)	G30	4	EU-ALPINA-B5-G30-SEDAN-01	HIGH	G30 轿车外廓。	READY
126217	126217	Wagon	B5 Touring (G31)	G31	5	EU-ALPINA-B5-G31-WAGON-01	HIGH	G31 Touring 外廓。	READY
126388_mia	126388	Hatchback	Mia		3	EU-MIA-ELECTRIC-MIA-HATCHBACK-SHORT-01	HIGH	短车身 mia。	READY
126388_mial	126388	Hatchback	Mia L		3	EU-MIA-ELECTRIC-MIA-LONG-01	HIGH	长车身 mia L。	READY
126388_miau	126388	Van	Mia U		3	EU-MIA-ELECTRIC-MIA-LONG-01	HIGH	长车身商用 mia U。	READY
126571_l3h2	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126571_l3h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126571_l4h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126571_l4h4	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126571_l5h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126571_l5h4	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126572_l3h2	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126572_l3h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126572_l4h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126572_l4h4	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126572_l5h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126572_l5h4	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126573_l3h2	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126573_l3h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126573_l4h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126573_l4h4	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126573_l5h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126573_l5h4	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126581_scab_l3	126581	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126581_scab_l4	126581	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126581_dcab_l3	126581	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126581_dcab_l4	126581	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126582_scab_l3	126582	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126582_scab_l4	126582	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126582_dcab_l3	126582	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126582_dcab_l4	126582	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126583_scab_l3	126583	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126583_scab_l4	126583	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126583_dcab_l3	126583	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126583_dcab_l4	126583	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126646	126646	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-HATCHBACK-5D-01	MEDIUM	输入驱动字段异常；五门车身边界明确。	READY
126648_3dr	126648	Hatchback	Focus I pre-facelift	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	MEDIUM	输入驱动字段异常；三门分支。	READY
126648_5dr	126648	Hatchback	Focus I pre-facelift	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	MEDIUM	输入驱动字段异常；五门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MAHINDRA-GOA-SUV-01	4430	1775	1975	Mahindra Croatia Goa SUV GLX 2.2 technical specifications	https://mahindra.panda.hr/index.php?Itemid=6&id=5&option=com_content&task=view
EU-ALPINA-B5-G30-SEDAN-01	4956	1868	1466	BMW ALPINA B5 BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G31-WAGON-01	4956	1868	1466	BMW ALPINA B5 BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-MIA-ELECTRIC-MIA-HATCHBACK-SHORT-01	2870	1640	1550	mia electric official brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-MIA-ELECTRIC-MIA-LONG-01	3190	1640	1550	mia electric official brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-OPEL-ASTRA-J-HATCHBACK-5D-01	4419	1814	1510	Auto-Data Opel Astra J 1.6 Turbo 180 specifications	https://www.auto-data.net/en/opel-astra-j-1.6-turbo-180hp-16969
EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	4152	1699	1430	Ford Focus 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
```

## 下一步优先处理

1. 闭合 Nissan Primastar X83 与 NV300 X82 的 Van、Bus、单排/双排底盘和轴距分支。
2. 处理 Caddy IV 标准轴距/Maxi、MAN TGE AWD 与 Crafter II 4Motion 的驱动高度差异。
3. 集中解决 Polo III、Legacy IV、Camry XV50、L200 IV 和 Outlander III 的身份或改款分支。

推进信号：CONTINUE

[1]: https://www.mahindra.panda.hr/index.php?Itemid=6&id=5&option=com_content&task=view "https://www.mahindra.panda.hr/index.php?Itemid=6&id=5&option=com_content&task=view"
[2]: https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf "https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf"
[3]: https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF "https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF"
[4]: https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf "https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf"
[5]: https://www.auto-data.net/en/opel-astra-j-1.6-turbo-180hp-16969 "https://www.auto-data.net/en/opel-astra-j-1.6-turbo-180hp-16969"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* VW Caddy IV 已按乘用车/厢式车及标准轴距/Maxi 长轴拆成四个物理外廓；官方规格显示两种用途车身的高度存在差异，因此不合并尺寸组。([volkswagen-transportbilar.se][1])
* MAN TGE AWD 与 VW Crafter II 4Motion 已关联至六个现有 Crafter II 厢式车尺寸组，本轮未重复创建或输出这些尺寸组。([MAN Global][2])
* NV300 Platform Cab、Polo III 6N1、Legacy IV BL、Camry XV50、L200 IV 单排后驱及 Outlander III 改款前后分支已闭合。
* 当前仅剩四个 Nissan Primastar X83 Ktype。其输入未限定厢体轴距、车顶高度或底盘驾驶室配置，暂不创建猜测性派生行。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：96
* PENDING Ktype：4
* 当前映射行：154
* READY 映射行：150
* PENDING 映射行：4
* 当前已引用尺寸组：63
* 本轮首次创建尺寸组：12
* 本轮复用既有尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126341_swb	126341	MPV	Caddy IV	SAB	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	标准轴距乘用车外廓。	READY
126341_maxi	126341	MPV	Caddy IV	SAJ	5	EU-VW-CADDY-IV-MPV-MAXI-01	MEDIUM	Maxi长轴乘用车外廓。	READY
126342_swb	126342	Van	Caddy IV	SAA		EU-VW-CADDY-IV-VAN-SWB-01	MEDIUM	标准轴距厢式车外廓。	READY
126342_maxi	126342	Van	Caddy IV	SAH		EU-VW-CADDY-IV-VAN-MAXI-01	MEDIUM	Maxi长轴厢式车外廓。	READY
126577_l3h2	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4x4 L3H2分支。	READY
126577_l3h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4x4 L3H3分支。	READY
126577_l4h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4x4 L4H3分支。	READY
126577_l4h4	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4x4 L4H4分支。	READY
126577_l5h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4x4 L5H3分支。	READY
126577_l5h4	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4x4 L5H4分支。	READY
126578_l3h2	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4x4 L3H2分支。	READY
126578_l3h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4x4 L3H3分支。	READY
126578_l4h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4x4 L4H3分支。	READY
126578_l4h4	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4x4 L4H4分支。	READY
126578_l5h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4x4 L5H3分支。	READY
126578_l5h4	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4x4 L5H4分支。	READY
126602_l3h2	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4Motion L3H2分支。	READY
126602_l3h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4Motion L3H3分支。	READY
126602_l4h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4Motion L4H3分支。	READY
126602_l4h4	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4Motion L4H4分支。	READY
126602_l5h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4Motion L5H3分支。	READY
126602_l5h4	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4Motion L5H4分支。	READY
126641	126641	Pickup	NV300	X82	2	EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1 Platform Cab外廓。	READY
126643	126643	Pickup	NV300	X82	2	EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1 Platform Cab外廓。	READY
126649_3dr	126649	Hatchback	Polo III	6N1	3	EU-VW-POLO-III-6N1-HATCHBACK-01	MEDIUM	输入驱动字段异常；三门分支。	READY
126649_5dr	126649	Hatchback	Polo III	6N1	5	EU-VW-POLO-III-6N1-HATCHBACK-01	MEDIUM	输入驱动字段异常；五门分支。	READY
126650	126650	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-01	MEDIUM	输入驱动字段异常；BL轿车外廓明确。	READY
126651_prefl	126651	Sedan	Camry XV50	XV50	4	EU-TOYOTA-CAMRY-XV50-SEDAN-PREFL-01	MEDIUM	生产区间跨越改款；改款前分支。	READY
126651_facelift	126651	Sedan	Camry XV50 facelift	XV50	4	EU-TOYOTA-CAMRY-XV50-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越改款；改款后分支。	READY
126659	126659	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLECAB-2WD-01	HIGH	KA4T后驱单排驾驶室外廓。	READY
126681_prefl	126681	SUV	Outlander III	GF8W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	MEDIUM	生产区间跨越外廓改款；改款前分支。	READY
126681_facelift	126681	SUV	Outlander III facelift	GF8W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	MEDIUM	生产区间跨越外廓改款；改款后分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Caddy passenger official brochure	https://www.volkswagen-transportbilar.se/idhub/content/dam/onehub_nfz/importers/se/broschyrer/modellbroschyrer/caddy_personbil.pdf
EU-VW-CADDY-IV-MPV-MAXI-01	4878	1793	1831	Volkswagen Caddy passenger official brochure	https://www.volkswagen-transportbilar.se/idhub/content/dam/onehub_nfz/importers/se/broschyrer/modellbroschyrer/caddy_personbil.pdf
EU-VW-CADDY-IV-VAN-SWB-01	4408	1793	1823	Volkswagen Caddy Panel Van official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-VW-CADDY-IV-VAN-MAXI-01	4878	1793	1836	Volkswagen Caddy Panel Van official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	5399	1956	1971	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-VW-POLO-III-6N1-HATCHBACK-01	3715	1655	1420	Volkswagen Newsroom Polo III;Auto-Data Volkswagen Polo III 1.6 75	https://www.volkswagen-newsroom.com/en/polo-3-19942001-19147;https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.6-75hp-8476
EU-SUBARU-LEGACY-IV-BL-SEDAN-01	4665	1730	1425	Auto-Data Subaru Legacy IV specifications	https://www.auto-data.net/en/subaru-legacy-model-1844
EU-TOYOTA-CAMRY-XV50-SEDAN-PREFL-01	4825	1825	1480	Auto-Data Toyota Camry VII XV50 specifications	https://www.auto-data.net/en/toyota-camry-vii-xv50-generation-4696
EU-TOYOTA-CAMRY-XV50-SEDAN-FACELIFT-01	4850	1825	1480	Toyota Camry 2017 Singapore brochure	https://www.cnp.sg/wp-content/uploads/2024/03/camry-2017-brochure.pdf
EU-MITSUBISHI-L200-IV-PICKUP-SINGLECAB-2WD-01	5040	1750	1655	Mitsubishi genuine parts catalog;EncyCARpedia L200 2WD Single Cab	https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD326170;https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-single-cab-128-pick-up
EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	4655	1800	1680	Mitsubishi Outlander 2013 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Mitsubishi-Outlander-2013-UK.pdf
EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	4695	1810	1710	Mitsubishi Outlander 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Mitsubishi-Outlander-2017-UK.pdf
```

## 下一步优先处理

1. 闭合 Primastar X83 Kasten 与 Bus 的短轴/长轴及车顶高度分支。
2. 闭合 Primastar X83 Platform/Chassis 的驾驶室和底盘长度分支，消除最后四个 PENDING。
3. PENDING 清零后仅执行一次表头、唯一键、引用闭合及下载文件机械检查，并直接输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.volkswagen-transportbilar.se/idhub/content/dam/onehub_nfz/importers/se/broschyrer/modellbroschyrer/caddy_personbil.pdf "Caddy Personbil"
[2]: https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf "730232-99852-Update Pricelist and Launch Brochure 297x210_DEE.indd"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* Primastar X83 Kasten 已按 L1H1、L1H2、L2H1、L2H2 四种明确外廓拆分；四组均使用不含后视镜宽度 1904 mm。
* 两个 `Pritsche/Fahrgestell` Ktype 已关联至 X83 长轴 Dropside 外廓。官方同平台 Vivaro 资料明确给出 5350 × 1980 × 2000 mm，其中宽度为不含后视镜口径。
* 目前仅剩 Primastar Bus Ktype 126219：短轴、长轴已确认，但官方资料将高度写为 1942–1963 mm 范围，尚不能为各分支落盘唯一正整数。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* 当前映射行：157
* READY 映射行：156
* PENDING 映射行：1
* 当前已引用尺寸组：68
* 本轮首次创建尺寸组：5
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126218_l1h1	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L1H1-01	MEDIUM	输入未区分轴距与车顶；L1H1分支。	READY
126218_l1h2	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L1H2-01	MEDIUM	输入未区分轴距与车顶；L1H2分支。	READY
126218_l2h1	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L2H1-01	MEDIUM	输入未区分轴距与车顶；L2H1分支。	READY
126218_l2h2	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L2H2-01	MEDIUM	输入未区分轴距与车顶；L2H2分支。	READY
126219	126219	MPV	Primastar I facelift	X83				LOW	已确认L1/L2低顶Bus分支；各配置唯一外部高度尚未闭合。	PENDING: Bus短轴与长轴的唯一HeightMM待确认
126220_dropside	126220	Pickup	Primastar I pre-facelift	X83	2	EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	MEDIUM	长轴Dropside外廓。	READY
126221_dropside	126221	Pickup	Primastar I facelift	X83	2	EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	MEDIUM	长轴Dropside外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-NISSAN-PRIMASTAR-X83-VAN-L1H1-01	4782	1904	1963	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L1H2-01	4782	1904	2465	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L2H1-01	5182	1904	1962	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L2H2-01	5182	1904	2464	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	5350	1980	2000	Vauxhall Vivaro Dropside 2007 official brochure, X83 sister model	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_ChassisCabConv_August_2007.pdf
```

## 下一步优先处理

1. 仅核对 126219 Bus 的 L1、L2 具体配置高度，将基础 PENDING 行替换为完整派生行。
2. PENDING 清零后立即进行一次表头、唯一键、引用闭合和下载文件检查，并直接输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已将最后一个 Primastar Bus Ktype `126219` 拆分为 L1/L2、6座/9座四个明确物理分支。官方规格表分别给出四种配置的长度、1904 mm 不含后视镜宽度及唯一高度，最后一个 PENDING 已消除。([xr793.com][1])
* 已完成轻量机械收尾：固定表头、`id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用闭合、尺寸及来源非空、下载文件存在。
* 未重新核验已经闭合或复用的尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* PENDING Ktype：0
* 最终 Ktype 映射：160 行
* 最终 DIMENSION_GROUP：72 行
* 所有映射均为 `READY`
* 所有尺寸组均被引用，不存在孤立组

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
126165	126165	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Sportback 五门外廓。	READY
126168	126168	Hatchback	3 Series Gran Turismo (F34)	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 五门 Gran Turismo 外廓。	READY
126169	126169	Hatchback	3 Series Gran Turismo (F34)	F34	5	EU-BMW-3-F34-GRAN-TURISMO-01	HIGH	F34 五门 Gran Turismo 外廓。	READY
126175	126175	Convertible	Plus 4		2	EU-MORGAN-PLUS-4-CONVERTIBLE-01	MEDIUM	输入 Four/2 与 Plus 4 2.0 版本对应。	READY
126179	126179	SUV	Goa		5	EU-MAHINDRA-GOA-SUV-01	HIGH	五门 Goa SUV 外廓。	READY
126180	126180	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	Sportback 五门外廓。	READY
126181	126181	Sedan	B7 (G12)	G12	4	EU-ALPINA-B7-G12-SEDAN-01	MEDIUM	G12 长轴轿车外廓；驱动差异不单独建组。	READY
126182	126182	Sedan	A4 B9	8W2	4	EU-AUDI-A4-B9-SEDAN-PREFL-01	HIGH	改款前 B9 轿车外廓。	READY
126183	126183	Wagon	A4 B9 Avant	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	B9 Avant 外廓。	READY
126184	126184	Wagon	A4 B9 Avant	8W5	5	EU-AUDI-A4-B9-AVANT-WAGON-01	HIGH	B9 Avant 外廓。	READY
126185	126185	Wagon	5 Series Touring (G31)	G31	5	EU-BMW-5-G31-WAGON-PREFL-01	HIGH	G31 改款前 Touring 外廓。	READY
126186	126186	Hatchback	Clio IV facelift	X98	5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	HIGH	Clio IV 改款后五门外廓。	READY
126187	126187	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126188	126188	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126189	126189	SUV	3008 II	P84	5	EU-PEUGEOT-3008-II-SUV-01	HIGH	第二代 3008 SUV 外廓。	READY
126190	126190	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入 MPV 标签按第二代 5008 的 SUV 物理车身归一。	READY
126191	126191	SUV	5008 II Phase I	P87	5	EU-PEUGEOT-5008-II-PHASE-I-SUV-01	HIGH	输入 MPV 标签按第二代 5008 的 SUV 物理车身归一。	READY
126196	126196	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126198	126198	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126200	126200	Hatchback	Model S pre-facelift		5	EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	HIGH	2016 外观改款前 Model S 外廓。	READY
126214	126214	Hatchback	Sandero II facelift	B52	5	EU-DACIA-SANDERO-II-FACELIFT-HATCHBACK-01	HIGH	第二代 Sandero 改款后外廓。	READY
126215	126215	Wagon	Logan II MCV	K52	5	EU-DACIA-LOGAN-II-MCV-WAGON-01	HIGH	第二代 Logan MCV 外廓。	READY
126216	126216	Sedan	B5 (G30)	G30	4	EU-ALPINA-B5-G30-SEDAN-01	HIGH	G30 轿车外廓。	READY
126217	126217	Wagon	B5 Touring (G31)	G31	5	EU-ALPINA-B5-G31-WAGON-01	HIGH	G31 Touring 外廓。	READY
126218_l1h1	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L1H1-01	MEDIUM	输入未区分轴距与车顶；L1H1分支。	READY
126218_l1h2	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L1H2-01	MEDIUM	输入未区分轴距与车顶；L1H2分支。	READY
126218_l2h1	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L2H1-01	MEDIUM	输入未区分轴距与车顶；L2H1分支。	READY
126218_l2h2	126218	Van	Primastar I facelift	X83		EU-NISSAN-PRIMASTAR-X83-VAN-L2H2-01	MEDIUM	输入未区分轴距与车顶；L2H2分支。	READY
126219_l1_6seat	126219	MPV	Primastar I facelift	X83	4	EU-NISSAN-PRIMASTAR-X83-MINIBUS-L1H1-6SEAT-01	HIGH	L1H1六座Minibus外廓。	READY
126219_l1_9seat	126219	MPV	Primastar I facelift	X83	4	EU-NISSAN-PRIMASTAR-X83-MINIBUS-L1H1-9SEAT-01	HIGH	L1H1九座Minibus外廓。	READY
126219_l2_6seat	126219	MPV	Primastar I facelift	X83	4	EU-NISSAN-PRIMASTAR-X83-MINIBUS-L2H1-6SEAT-01	HIGH	L2H1六座Minibus外廓。	READY
126219_l2_9seat	126219	MPV	Primastar I facelift	X83	4	EU-NISSAN-PRIMASTAR-X83-MINIBUS-L2H1-9SEAT-01	HIGH	L2H1九座Minibus外廓。	READY
126220_dropside	126220	Pickup	Primastar I pre-facelift	X83	2	EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	MEDIUM	长轴Dropside外廓。	READY
126221_dropside	126221	Pickup	Primastar I facelift	X83	2	EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	MEDIUM	长轴Dropside外廓。	READY
126257	126257	Sedan	5 Series (G30)	G30	4	EU-BMW-5-G30-SEDAN-PREFL-01	HIGH	G30 改款前轿车外廓。	READY
126259	126259	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126260	126260	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126261	126261	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126262	126262	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126318	126318	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH	第二代 Compass MP 四驱外廓。	READY
126341_swb	126341	MPV	Caddy IV	SAB	5	EU-VW-CADDY-IV-MPV-SWB-01	MEDIUM	标准轴距乘用车外廓。	READY
126341_maxi	126341	MPV	Caddy IV	SAJ	5	EU-VW-CADDY-IV-MPV-MAXI-01	MEDIUM	Maxi长轴乘用车外廓。	READY
126342_swb	126342	Van	Caddy IV	SAA		EU-VW-CADDY-IV-VAN-SWB-01	MEDIUM	标准轴距厢式车外廓。	READY
126342_maxi	126342	Van	Caddy IV	SAH		EU-VW-CADDY-IV-VAN-MAXI-01	MEDIUM	Maxi长轴厢式车外廓。	READY
126344	126344	Coupe	Huayra		2	EU-PAGANI-HUAYRA-COUPE-01	HIGH	Huayra Coupe 标准外廓。	READY
126370	126370	Convertible	D8 GTO		2	EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	HIGH	D8 GTO Performance 外廓。	READY
126388_mia	126388	Hatchback	Mia		3	EU-MIA-ELECTRIC-MIA-HATCHBACK-SHORT-01	HIGH	短车身 mia。	READY
126388_mial	126388	Hatchback	Mia L		3	EU-MIA-ELECTRIC-MIA-LONG-01	HIGH	长车身 mia L。	READY
126388_miau	126388	Van	Mia U		3	EU-MIA-ELECTRIC-MIA-LONG-01	HIGH	长车身商用 mia U。	READY
126404	126404	Hatchback	Clio IV facelift	X98	5	EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	HIGH	Clio IV 改款后五门外廓。	READY
126414	126414	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126415	126415	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126416	126416	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126417	126417	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126418	126418	SUV	Crossland X	P17	5	EU-OPEL-CROSSLAND-X-P17-SUV-01	HIGH	Crossland X P17 标准外廓。	READY
126475	126475	Sedan	Quattroporte VI	M156	4	EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	HIGH	M156 轿车外廓。	READY
126478	126478	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126479	126479	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126480	126480	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126481	126481	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126482	126482	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH	第二代 XC60 标准外廓。	READY
126495	126495	Hatchback	1 Series (E87) pre-facelift	E87	5	EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	HIGH	E87 五门改款前外廓。	READY
126522	126522	Hatchback	Civic X	FK7	5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	1.5 VTEC 五门掀背 FK7。	READY
126524	126524	Hatchback	Civic X	FK6	5	EU-HONDA-CIVIC-X-HATCHBACK-01	HIGH	1.0 VTEC 五门掀背 FK6，与 FK7 共用外廓。	READY
126526	126526	SUV	Range Rover Velar I	L560	5	EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	HIGH	L560 标准车身外廓。	READY
126554_3dr	126554	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126554_5dr	126554	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126555_3dr	126555	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126555_5dr	126555	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126556_3dr	126556	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126556_5dr	126556	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126557_3dr	126557	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126557_5dr	126557	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126566_3dr	126566	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126566_5dr	126566	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126567_3dr	126567	Hatchback	Fiesta VII		3	EU-FORD-FIESTA-VII-HATCHBACK-3D-01	MEDIUM	输入未区分门数；按三门外廓派生。	READY
126567_5dr	126567	Hatchback	Fiesta VII		5	EU-FORD-FIESTA-VII-HATCHBACK-5D-01	MEDIUM	输入未区分门数；按五门外廓派生。	READY
126569	126569	Coupe	Ford GT II		2	EU-FORD-GT-II-COUPE-01	HIGH	第二代 Ford GT 标准外廓。	READY
126571_l3h2	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126571_l3h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126571_l4h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126571_l4h4	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126571_l5h3	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126571_l5h4	126571	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126572_l3h2	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126572_l3h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126572_l4h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126572_l4h4	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126572_l5h3	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126572_l5h4	126572	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126573_l3h2	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；L3H2 分支。	READY
126573_l3h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；L3H3 分支。	READY
126573_l4h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；L4H3 分支。	READY
126573_l4h4	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；L4H4 分支。	READY
126573_l5h3	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；L5H3 分支。	READY
126573_l5h4	126573	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；L5H4 分支。	READY
126577_l3h2	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4x4 L3H2分支。	READY
126577_l3h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4x4 L3H3分支。	READY
126577_l4h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4x4 L4H3分支。	READY
126577_l4h4	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4x4 L4H4分支。	READY
126577_l5h3	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4x4 L5H3分支。	READY
126577_l5h4	126577	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4x4 L5H4分支。	READY
126578_l3h2	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4x4 L3H2分支。	READY
126578_l3h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4x4 L3H3分支。	READY
126578_l4h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4x4 L4H3分支。	READY
126578_l4h4	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4x4 L4H4分支。	READY
126578_l5h3	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4x4 L5H3分支。	READY
126578_l5h4	126578	Van	TGE I			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4x4 L5H4分支。	READY
126581_scab_l3	126581	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126581_scab_l4	126581	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126581_dcab_l3	126581	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126581_dcab_l4	126581	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126582_scab_l3	126582	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126582_scab_l4	126582	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126582_dcab_l3	126582	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126582_dcab_l4	126582	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126583_scab_l3	126583	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L3 分支。	READY
126583_scab_l4	126583	Pickup	TGE I		2	EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；单排驾驶室 L4 分支。	READY
126583_dcab_l3	126583	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L3 分支。	READY
126583_dcab_l4	126583	Pickup	TGE I		4	EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	MEDIUM	输入未区分驾驶室与车架长度；双排驾驶室 L4 分支。	READY
126593	126593	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126596	126596	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126598	126598	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126599	126599	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126600	126600	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126601	126601	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126602_l3h2	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H2-01	MEDIUM	输入未区分车长与车顶；4Motion L3H2分支。	READY
126602_l3h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L3H3-01	MEDIUM	输入未区分车长与车顶；4Motion L3H3分支。	READY
126602_l4h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H3-01	MEDIUM	输入未区分车长与车顶；4Motion L4H3分支。	READY
126602_l4h4	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L4H4-01	MEDIUM	输入未区分车长与车顶；4Motion L4H4分支。	READY
126602_l5h3	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H3-01	MEDIUM	输入未区分车长与车顶；4Motion L5H3分支。	READY
126602_l5h4	126602	Van	Crafter II			EU-VW-CRAFTER-II-VAN-L5H4-01	MEDIUM	输入未区分车长与车顶；4Motion L5H4分支。	READY
126603	126603	Hatchback	Insignia B Grand Sport	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport 五门掀背外廓。	READY
126609	126609	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126610	126610	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126611	126611	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126612	126612	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126615	126615	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126616	126616	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126617	126617	Wagon	Insignia B Sports Tourer	Z18	5	EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	HIGH	Sports Tourer 旅行车外廓。	READY
126622	126622	Coupe	A5 F5	F53	2	EU-AUDI-A5-F5-COUPE-01	HIGH	F5 Coupe 外廓。	READY
126623	126623	Hatchback	A5 F5	F5A	5	EU-AUDI-A5-F5-SPORTBACK-01	HIGH	F5 Sportback 五门外廓。	READY
126624	126624	Convertible	A5 F5 Cabriolet	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	F5 Cabriolet 外廓。	READY
126625	126625	Hatchback	Golf VII facelift	5G1	5	EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	HIGH	改款后 e-Golf 五门外廓。	READY
126627	126627	SUV	Duster I facelift	H79	5	EU-DACIA-DUSTER-I-FACELIFT-SUV-01	HIGH	第一代 Duster 改款后 4x2 外廓。	READY
126641	126641	Pickup	NV300	X82	2	EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1 Platform Cab外廓。	READY
126643	126643	Pickup	NV300	X82	2	EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	HIGH	L2H1 Platform Cab外廓。	READY
126646	126646	Hatchback	Astra J	P10	5	EU-OPEL-ASTRA-J-HATCHBACK-5D-01	MEDIUM	输入驱动字段异常；五门车身边界明确。	READY
126647_facelift	126647	Hatchback	Twingo II facelift	CN0	3	EU-RENAULT-TWINGO-II-HATCHBACK-FACELIFT-01	MEDIUM	生产区间跨越外观改款；改款后分支。	READY
126647_prefl	126647	Hatchback	Twingo II	CN0	3	EU-RENAULT-TWINGO-II-HATCHBACK-PREFL-01	MEDIUM	生产区间跨越外观改款；改款前分支。	READY
126648_3dr	126648	Hatchback	Focus I pre-facelift	DBW	3	EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	MEDIUM	输入驱动字段异常；三门分支。	READY
126648_5dr	126648	Hatchback	Focus I pre-facelift	DAW	5	EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	MEDIUM	输入驱动字段异常；五门分支。	READY
126649_3dr	126649	Hatchback	Polo III	6N1	3	EU-VW-POLO-III-6N1-HATCHBACK-01	MEDIUM	输入驱动字段异常；三门分支。	READY
126649_5dr	126649	Hatchback	Polo III	6N1	5	EU-VW-POLO-III-6N1-HATCHBACK-01	MEDIUM	输入驱动字段异常；五门分支。	READY
126650	126650	Sedan	Legacy IV	BL	4	EU-SUBARU-LEGACY-IV-BL-SEDAN-01	MEDIUM	输入驱动字段异常；BL轿车外廓明确。	READY
126651_prefl	126651	Sedan	Camry XV50	XV50	4	EU-TOYOTA-CAMRY-XV50-SEDAN-PREFL-01	MEDIUM	生产区间跨越改款；改款前分支。	READY
126651_facelift	126651	Sedan	Camry XV50 facelift	XV50	4	EU-TOYOTA-CAMRY-XV50-SEDAN-FACELIFT-01	MEDIUM	生产区间跨越改款；改款后分支。	READY
126659	126659	Pickup	L200 IV	KA4T	2	EU-MITSUBISHI-L200-IV-PICKUP-SINGLECAB-2WD-01	HIGH	KA4T后驱单排驾驶室外廓。	READY
126681_prefl	126681	SUV	Outlander III	GF8W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	MEDIUM	生产区间跨越外廓改款；改款前分支。	READY
126681_facelift	126681	SUV	Outlander III facelift	GF8W	5	EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	MEDIUM	生产区间跨越外廓改款；改款后分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1201-1300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386	Audi UK A5 Sportback official media model page	https://press.audi.co.uk/models/a5-sportback-2016-2020
EU-BMW-3-F34-GRAN-TURISMO-01	4824	1828	1508	BMW Group PressClub BMW 3 Series Gran Turismo technical data	https://www.press.bmwgroup.com/global/article/attachment/T0219422EN/312181
EU-MORGAN-PLUS-4-CONVERTIBLE-01	4010	1720	1220	CarsGuide Morgan Plus 4 dimensions	https://www.carsguide.com.au/morgan/plus-4/car-dimensions
EU-MAHINDRA-GOA-SUV-01	4430	1775	1975	Mahindra Croatia Goa SUV GLX 2.2 technical specifications	https://mahindra.panda.hr/index.php?Itemid=6&id=5&option=com_content&task=view
EU-ALPINA-B7-G12-SEDAN-01	5250	1902	1491	ALPINA B7 BITURBO official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2018_07_DE/B7_BITURBO/epaper/ausgabe.pdf
EU-AUDI-A4-B9-SEDAN-PREFL-01	4726	1842	1427	AutoScout24 Audi A4 B9 Sedan technical data	https://www.autoscout24.es/coches/datos-tecnicos/audi/a4/a4-2-0tdi-140kw-sedan-diesel-8327/
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434	AutoScout24 Audi A4 B9 Avant technical data	https://www.autoscout24.de/auto/technische-daten/audi/a4/a4-avant-18326/
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498	BMW Group PressClub BMW 5 Series Touring technical data	https://www.press.bmwgroup.com/global/article/attachment/T0267496EN/384775
EU-RENAULT-CLIO-IV-FACELIFT-HATCHBACK-01	4062	1732	1448	Renault Clio IV official user manual technical specifications	https://www.user-manual.renault.com/en/content/x98/section-6-technical-specifications
EU-PEUGEOT-3008-II-SUV-01	4447	1841	1620	Peugeot 3008 official price and specification guide	https://business.peugeot.co.uk/content/dam/peugeot/uk/b2c/buy/price-and-spec-guides/pdfs/3008-suv-price-spec-guide.pdf
EU-PEUGEOT-5008-II-PHASE-I-SUV-01	4641	1844	1646	Peugeot 5008 official model dimensions	https://www.peugeot.ie/our-range/new-5008-suv1.html
EU-TESLA-MODEL-S-PREFL-HATCHBACK-01	4970	1964	1445	Tesla Model S official owner's manual dimensions	https://www.tesla.com/ownersmanual/2012_2020_models/en_sg/GUID-5FB8FC1E-0B1D-4ECC-99D6-4EEE2B8FB725.html
EU-DACIA-SANDERO-II-FACELIFT-HATCHBACK-01	4057	1733	1523	Automoli Dacia Sandero II specifications	https://www.automoli.com/en/vehicles/dacia/sandero/sandero-ii-3954/
EU-DACIA-LOGAN-II-MCV-WAGON-01	4492	1733	1539	Dacia Logan MCV official brochure	https://cdn.group.renault.com/dac/ie/transversal-assets/brochures/model-brochures/logan-mcv-brochure-oct.pdf
EU-ALPINA-B5-G30-SEDAN-01	4956	1868	1466	BMW ALPINA B5 BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-ALPINA-B5-G31-WAGON-01	4956	1868	1466	BMW ALPINA B5 BITURBO official brochure	https://i.i-sgcm.com/new_cars/cars/11859/brochures/brochure_20180130093637.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L1H1-01	4782	1904	1963	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L1H2-01	4782	1904	2465	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L2H1-01	5182	1904	1962	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-VAN-L2H2-01	5182	1904	2464	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MINIBUS-L1H1-6SEAT-01	4782	1904	1942	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MINIBUS-L1H1-9SEAT-01	4782	1904	1963	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MINIBUS-L2H1-6SEAT-01	5182	1904	1952	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-MINIBUS-L2H1-9SEAT-01	5182	1904	1968	Nissan Primastar 2011 UK official brochure	https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf
EU-NISSAN-PRIMASTAR-X83-DROPSIDE-L2-01	5350	1980	2000	Vauxhall Vivaro Dropside 2007 official brochure, X83 sister model	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_ChassisCabConv_August_2007.pdf
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479	BMW Group PressClub BMW 5 Series Sedan technical data	https://www.press.bmwgroup.com/global/article/attachment/T0264349EN/379570
EU-LAND-ROVER-RANGE-ROVER-VELAR-L560-SUV-01	4803	2032	1665	Land Rover Range Rover Velar official brochure;CarsGuide 2017 Range Rover Velar dimensions	https://www.landrover.co.uk/content/dam/lrdx/pdfs/uk/brochures/range-rover-velar/Range-Rover-Velar-Brochure-1L5601910000BGBEN01P_tcm295-607384.pdf;https://www.carsguide.com.au/land-rover/range-rover-velar/car-dimensions/2017
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644	Jeep All-New Compass official technical specifications	https://www.media.stellantis.com/uploads/nl/NL/SYSTEM_ARCHIVE/2017/JEEP/Schede_tecniche/170606_Jeep_Tech_Specs_All_New_Compass.pdf
EU-VW-CADDY-IV-MPV-SWB-01	4408	1793	1822	Volkswagen Caddy passenger official brochure	https://www.volkswagen-transportbilar.se/idhub/content/dam/onehub_nfz/importers/se/broschyrer/modellbroschyrer/caddy_personbil.pdf
EU-VW-CADDY-IV-MPV-MAXI-01	4878	1793	1831	Volkswagen Caddy passenger official brochure	https://www.volkswagen-transportbilar.se/idhub/content/dam/onehub_nfz/importers/se/broschyrer/modellbroschyrer/caddy_personbil.pdf
EU-VW-CADDY-IV-VAN-SWB-01	4408	1793	1823	Volkswagen Caddy Panel Van official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-VW-CADDY-IV-VAN-MAXI-01	4878	1793	1836	Volkswagen Caddy Panel Van official brochure	https://www.vw.co.za/idhub/content/dam/onehub_pkw/importers/za/editorials/offers-and-products/brochures-and-specifications/brochures/commercial-vehicles/2019/september/caddy-panel-van-my20-online-brochure.pdf
EU-PAGANI-HUAYRA-COUPE-01	4605	2036	1169	Auto-Data Pagani Huayra specifications	https://www.auto-data.net/en/pagani-huayra-model-2122
EU-DONKERVOORT-D8-GTO-CONVERTIBLE-01	3740	1850	1140	Donkervoort D8 GTO official heritage specifications;Automobile-Catalog 2013 D8 GTO Performance	https://www.donkervoort.com/en/models/heritage/donkervoort-d8-gto/;https://www.automobile-catalog.com/car/2013/2065370/donkervoort_s8_gto_performance.html
EU-MIA-ELECTRIC-MIA-HATCHBACK-SHORT-01	2870	1640	1550	mia electric official brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-MIA-ELECTRIC-MIA-LONG-01	3190	1640	1550	mia electric official brochure	https://www.allcarcentral.com/mia_pdf/Mia_brochure_2013.PDF
EU-OPEL-CROSSLAND-X-P17-SUV-01	4212	1765	1590	Opel Crossland X official press specifications	https://www.media.stellantis.com/me-tr/opel-archive/press/turkey-yeni-opel-crossland-x-stil-sahibi-ve-havali
EU-MASERATI-QUATTROPORTE-VI-M156-SEDAN-01	5262	1948	1481	Maserati Quattroporte MY17 official brochure	https://www.maserati.com/content/dam/maserati/international/Brochures/2016-06-11/ebrochure-Quattroporte-MY17-EN.pdf
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Cars XC60 official dimensions	https://www.volvocars.com/uk/support/car/xc60/20w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-BMW-1-E87-HATCHBACK-5D-PREFL-01	4227	1751	1430	BMW 1 Series E87 technical data	https://www.treffseiten.de/bmw/info/daten_118d_120d_05_09.pdf
EU-HONDA-CIVIC-X-HATCHBACK-01	4518	1799	1434	Honda Civic 5 Door official brochure	https://www.honda.co.uk/content/dam/local/uk/brochures/cars/Civic-5-Door-Brochure.pdf
EU-FORD-FIESTA-VII-HATCHBACK-3D-01	4040	1735	1476	Ford All-New Fiesta 2017 UK brochure;Automobile-Catalog 2017 Fiesta 1.5 TDCi	https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Fiesta-2017-UK.pdf;https://www.automobile-catalog.com/car/2017/2562950/ford_fiesta_1_5_tdci_85.html
EU-FORD-FIESTA-VII-HATCHBACK-5D-01	4065	1735	1476	Ford All-New Fiesta 2017 UK brochure;Automobile-Catalog 2017 Fiesta 1.5 TDCi	https://autocatalogarchive.com/wp-content/uploads/2017/06/Ford-Fiesta-2017-UK.pdf;https://www.automobile-catalog.com/car/2017/2562950/ford_fiesta_1_5_tdci_85.html
EU-FORD-GT-II-COUPE-01	4779	2003	1109	Ford GT official EU technical specifications	https://fordmediacenter.nl/wp-content/uploads/2017/05/gt_technical_specs_EU.pdf
EU-VW-CRAFTER-II-VAN-L3H2-01	5986	2040	2355	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L3H3-01	5986	2040	2590	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L4H3-01	6836	2040	2590	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L4H4-01	6836	2040	2798	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L5H3-01	7391	2040	2590	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-VW-CRAFTER-II-VAN-L5H4-01	7391	2040	2798	Volkswagen Crafter panel van official brochure	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/brochures/crafter/crafter_panel_van-brochure.pdf
EU-MAN-TGE-I-CHASSIS-SCAB-L3-01	5996	2033	2312	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-SCAB-L4-01	6846	2033	2305	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L3-01	5996	2037	2330	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-MAN-TGE-I-CHASSIS-DCAB-L4-01	6846	2037	2321	MAN TGE official technical data	https://www.man.eu/content/dam/man/countries/doc/bw-master/van/datenblaetter/tge/man-tge-technical-data-en.pdf/_jcr_content/renditions/original./man-tge-technical-data-en.pdf
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Vauxhall New Insignia official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/014_New_Insignia_Spec_PG_1_August_2017-1504607950.pdf
EU-OPEL-INSIGNIA-B-SPORTS-TOURER-WAGON-01	4986	1863	1500	Vauxhall New Insignia official specification guide	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/Cars/insignia/price-guides/014_New_Insignia_Spec_PG_1_August_2017-1504607950.pdf
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371	Australian Car.Reviews Audi F5 A5 Coupe specifications	https://australiancar.reviews/review-audi-f5-a5-coupe-2017-on/
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	Australian Car.Reviews Audi F5 A5 Cabriolet specifications	https://www.australiancar.reviews/review-audi-f5-a5-cabriolet-2017-on/
EU-VW-GOLF-VII-HATCHBACK-5D-FACELIFT-01	4258	1799	1492	Volkswagen Golf 2017 official product guide	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/golf-mk7-2017-present/vw_golf_estate_2017-Present_jun_2017.pdf
EU-DACIA-DUSTER-I-FACELIFT-SUV-01	4315	1822	1695	Automobile-Catalog 2016 Dacia Duster dCi 110 4x2	https://www.automobile-catalog.com/car/2016/2513870/dacia_duster_dci_110_4x2.html
EU-NISSAN-NV300-X82-PLATFORM-CAB-L2H1-01	5399	1956	1971	Nissan NV300 official brochure	https://www.nissan-cdn.net/content/dam/Nissan/gb/brochures/Vehicles/Nissan_NV300_UK.pdf
EU-OPEL-ASTRA-J-HATCHBACK-5D-01	4419	1814	1510	Auto-Data Opel Astra J 1.6 Turbo 180 specifications	https://www.auto-data.net/en/opel-astra-j-1.6-turbo-180hp-16969
EU-RENAULT-TWINGO-II-HATCHBACK-FACELIFT-01	3687	1654	1470	Automoli Renault Twingo II facelift specifications	https://www.automoli.com/en/vehicles/renault/twingo/twingo-ii-facelift-2011-3870/
EU-RENAULT-TWINGO-II-HATCHBACK-PREFL-01	3600	1654	1470	Automobile-Catalog Renault Twingo II 1.2 16V 75	https://www.automobile-catalog.com/car/2007/2956010/renault_twingo_1_2_16v_75_quickshift.html
EU-FORD-FOCUS-I-HATCHBACK-PREFL-01	4152	1699	1430	Ford Focus 1998 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2025/08/Ford-Focus-1998-UK.pdf
EU-VW-POLO-III-6N1-HATCHBACK-01	3715	1655	1420	Volkswagen Newsroom Polo III;Auto-Data Volkswagen Polo III 1.6 75	https://www.volkswagen-newsroom.com/en/polo-3-19942001-19147;https://www.auto-data.net/en/volkswagen-polo-iii-6n-1.6-75hp-8476
EU-SUBARU-LEGACY-IV-BL-SEDAN-01	4665	1730	1425	Auto-Data Subaru Legacy IV specifications	https://www.auto-data.net/en/subaru-legacy-model-1844
EU-TOYOTA-CAMRY-XV50-SEDAN-PREFL-01	4825	1825	1480	Auto-Data Toyota Camry VII XV50 specifications	https://www.auto-data.net/en/toyota-camry-vii-xv50-generation-4696
EU-TOYOTA-CAMRY-XV50-SEDAN-FACELIFT-01	4850	1825	1480	Toyota Camry 2017 Singapore brochure	https://www.cnp.sg/wp-content/uploads/2024/03/camry-2017-brochure.pdf
EU-MITSUBISHI-L200-IV-PICKUP-SINGLECAB-2WD-01	5040	1750	1655	Mitsubishi genuine parts catalog;EncyCARpedia L200 2WD Single Cab	https://partsouq.com/en/catalog/genuine/diagram?c=Mitsubishi&number=MD326170;https://www.encycarpedia.com/mitsubishi/10-l200-2-5-di-d-2wd-single-cab-128-pick-up
EU-MITSUBISHI-OUTLANDER-III-SUV-PREFL-01	4655	1800	1680	Mitsubishi Outlander 2013 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Mitsubishi-Outlander-2013-UK.pdf
EU-MITSUBISHI-OUTLANDER-III-SUV-FACELIFT-01	4695	1810	1710	Mitsubishi Outlander 2017 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2017/05/Mitsubishi-Outlander-2017-UK.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1201-1300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://xr793.com/wp-content/uploads/2022/10/2011-Nissan-Primastar-Uk.pdf "Primastar_PT.indd"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1201-1300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1201-1300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1332 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（666 行）

