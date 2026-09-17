# 任务：all 第 501-600 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0006__00596c50


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 501-600 行

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
all 第 501-600 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A3-8Y-SPORTBACK-01	4343	1816	1449
EU-AUDI-Q5-II-FACELIFT-2020-SUV-AWD-01	4682	1893	1662
EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	4682	1893	1637
EU-AUDI-Q5-II-FY-SUV-01	4671	1893	1661
EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	4096	1765	1653
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	2890	1500	1466
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	4895	1928	1910
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	5370	1928	1910
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	5140	1928	1910
EU-RENAULT-CAPTUR-II-HATCHBACK-01	4227	1797	1576
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Microcar	M.go	0.5	Schrägheck	Frontantrieb	Diesel	6	8	Jan 2020	-	2024-03-01	140429
Mercedes-benz	Gle	GLE 350 DE 4-matic	SUV	Allrad	Diesel/Elektro	235	320	Mar 2020	Mar 2023	2024-03-01	140436
Mercedes-benz	E-Klasse	E 300 DE	Kombi	Heckantrieb	Diesel/Elektro	225	306	Oct 2018	Oct 2023	2024-03-01	140437
Mercedes-benz	C-Klasse	C 300 E	Kombi	Heckantrieb	Benzin/Elektro	235	320	Jul 2019	Feb 2021	2024-03-01	140438
Mercedes-benz	C-Klasse	C 300 DE	Kombi	Heckantrieb	Diesel/Elektro	225	306	May 2019	Feb 2021	2024-03-01	140439
BMW	4	M 440 I Mild-hybrid Xdrive	Coupe	Allrad	Benzin/Elektro	285	387	Jul 2020	-	2024-03-01	140440
Honda	Jazz v	1.5 Ehev	Schrägheck	Frontantrieb	Benzin/Elektro	80	109	Feb 2020	-	2024-03-01	140441
BMW	4	420 I	Coupe	Heckantrieb	Benzin	135	184	Jul 2020	-	2024-03-01	140442
BMW	4	430 I	Coupe	Heckantrieb	Benzin	190	258	Jul 2020	-	2024-03-01	140443
BMW	4	430 I Xdrive	Coupe	Allrad	Benzin	190	258	Jul 2020	-	2025-06-01	140444
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140445
BMW	4	420 D Mild-hybrid	Coupe	Heckantrieb	Diesel/Elektro	120	163	Jul 2020	-	2024-03-01	140446
BMW	4	420 D Mild-hybrid Xdrive	Coupe	Allrad	Diesel/Elektro	140	190	Jul 2020	-	2024-03-01	140448
Seat	Leon	1.0 TSI	Schrägheck	Frontantrieb	Benzin	81	110	Mar 2020	-	2024-03-01	140449
Seat	Leon	1.0 TSI	Kombi	Frontantrieb	Benzin	81	110	Mar 2020	-	2024-03-01	140450
Skoda	Superb iii	1.4 TSI IV	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	Jun 2024	2025-06-01	140451
Skoda	Superb iii	1.4 TSI IV	Kombi	Frontantrieb	Benzin/Elektro	160	218	Aug 2019	Jun 2024	2025-06-01	140452
Ferrari	Sf90	Stradale Phev 4WD	Coupe	Allrad	Benzin/Elektro	735	999	May 2019	-	2024-03-01	140456
Mercedes-benz	Vito	114 CDI	Kasten	Heckantrieb	Diesel	100	136	Apr 2020	-	2024-03-01	140459
Mercedes-benz	Vito	116 CDI	Kasten	Heckantrieb	Diesel	120	163	Apr 2020	-	2024-03-01	140460
Mercedes-benz	Vito	116 CDI 4X4	Kasten	Allrad	Diesel	120	163	Apr 2020	-	2024-03-01	140461
Mercedes-benz	Vito	119 CDI	Kasten	Heckantrieb	Diesel	140	190	Apr 2020	-	2024-03-01	140462
Mercedes-benz	Vito	119 CDI 4X4	Kasten	Allrad	Diesel	140	190	Apr 2020	-	2024-03-01	140463
Volvo	S60 iii	B4 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2024-03-01	140464
Volvo	V60 ii	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2024-03-01	140465
Volvo	V60 ii	B3 Mild-hybrid	Kombi	Frontantrieb	Benzin/Elektro	120	163	Mar 2020	-	2026-02-01	140466
Volvo	V60 ii	B4 Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	145	197	Mar 2020	-	2025-06-01	140467
Volvo	V60 ii	B5 Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	184	250	Mar 2020	-	2025-06-01	140468
Volvo	V60 ii	B5 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	184	250	Mar 2020	-	2024-03-01	140470
Volvo	Xc40	B4 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	145	197	Sep 2019	-	2024-03-01	140474
Volvo	Xc40	B4 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	145	197	Sep 2019	-	2024-03-01	140475
Volvo	Xc40	B5 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	184	250	Sep 2019	Dec 2023	2024-05-01	140476
Volvo	Xc60 ii	B4 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	145	197	Sep 2019	-	2024-03-01	140479
Volvo	140	2	Stufenheck	Heckantrieb	Benzin	99	135	Aug 1972	Aug 1973	2024-03-01	140485
Volvo	140	2	Stufenheck	Heckantrieb	Benzin	103	140	Sep 1971	Aug 1972	2024-03-01	140486
Volvo	Pv 444	1.4	Stufenheck	Heckantrieb	Benzin	32	44	Sep 1950	Nov 1955	2024-03-01	140487
Volvo	Pv 444	1.4	Stufenheck	Heckantrieb	Benzin	38	52	Dec 1955	Aug 1957	2024-03-01	140488
Volvo	Xc90 ii	B6 Mild Hybrid AWD	SUV	Allrad	Benzin/Elektro	220	299	Mar 2020	-	2025-06-01	140489
Volvo	Pv 444	1.6	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1957	Aug 1958	2024-03-01	140490
Volvo	Pv 444	1.6 S	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1957	Aug 1958	2024-03-01	140491
Volvo	Pv 444	1.4 C	Stufenheck	Heckantrieb	Benzin	51	69	Sep 1955	Aug 1957	2024-03-01	140492
Volvo	P 210 duett	1.6	Kombi	Heckantrieb	Benzin	44	60	May 1960	Feb 1962	2024-03-01	140493
Volvo	Pv 445 duett	1.4	Kombi	Heckantrieb	Benzin	29	39	Sep 1953	Aug 1961	2024-03-01	140495
Volvo	Pv 445 duett	1.4	Kombi	Heckantrieb	Benzin	38	52	Sep 1955	Jan 1957	2024-03-01	140496
Volvo	Pv 445 duett	1.6	Kombi	Heckantrieb	Benzin	44	60	Jan 1957	Jun 1960	2024-03-01	140497
Ford	Puma	1.5 Ecoblue	SUV	Frontantrieb	Diesel	88	120	Apr 2020	-	2024-03-01	140498
Volvo	P 122 s amazon	1.8 S	Stufenheck	Heckantrieb	Benzin	85	116	Sep 1967	Aug 1968	2024-03-01	140499
Audi	A3	30 TDI	Stufenheck	Frontantrieb	Diesel	85	116	Jun 2020	-	2024-03-01	140504
Ford	Mondeo v	2.0 Ecoblue	Stufenheck	Frontantrieb	Diesel	110	150	Jan 2019	Mar 2022	2026-04-01	140505
Audi	A3	35 TDI	Stufenheck	Frontantrieb	Diesel	110	150	Apr 2020	-	2024-03-01	140506
Toyota	Hiace iv	2.4	Kasten	Heckantrieb	Benzin	85	116	Aug 1989	Jul 1998	2024-03-01	140511
Toyota	Hiace iv	2.4 I	Kasten	Heckantrieb	Benzin	85	116	Aug 1998	Aug 2004	2024-03-01	140512
Audi	A3	35 Tfsi Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	110	150	Apr 2020	-	2024-03-01	140515
Audi	A3	30 Tfsi	Schrägheck	Frontantrieb	Benzin	81	110	Jun 2020	-	2024-03-01	140516
Audi	A3	35 Tfsi Mild Hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	110	150	Apr 2020	-	2024-03-01	140517
Audi	A3	35 Tfsi	Stufenheck	Frontantrieb	Benzin	110	150	Apr 2020	-	2024-03-01	140518
Seat	Leon	1.0 TSI	Schrägheck	Frontantrieb	Benzin	66	90	Mar 2020	-	2024-03-01	140519
Seat	Leon	1.0 TSI	Kombi	Frontantrieb	Benzin	66	90	Mar 2020	-	2024-03-01	140520
Renault	Captur i	1.2 TCE	Schrägheck	Frontantrieb	Benzin	97	132	Feb 2018	Dec 2018	2025-12-01	140522
Ford	Fiesta vii van	1.1 Ti-vct	Kasten/Schrägheck	Frontantrieb	Benzin	55	75	Apr 2019	-	2024-03-01	140523
Renault	Captur ii	E-tech 160	Schrägheck	Frontantrieb	Benzin/Elektro	116	158	May 2020	-	2024-03-01	140525
Ford	Ecosport	1.0 Ecoboost	SUV	Frontantrieb	Benzin	70	95	Apr 2020	-	2024-03-01	140532
Audi	A6 c8 avant	55 Tfsi E Quattro	Kombi	Allrad	Benzin/Elektro	270	367	Apr 2020	-	2024-03-01	140538
Audi	A6 c8 avant	55 Tfsi E Quattro	Kombi	Allrad	Benzin/Elektro	270	367	Feb 2021	-	2024-03-01	140539
Ssangyong	Tivoli	1.2	SUV	Frontantrieb	Benzin	94	128	Mar 2020	-	2024-03-01	140540
AMC	Matador	3.8	Kombi	Heckantrieb	Benzin	99	135	Sep 1970	Dec 1974	2024-03-01	140545
AMC	Hornet	3.3	Schrägheck	Heckantrieb	Benzin	96	131	Oct 1969	Dec 1970	2024-03-01	140546
ISO	Isetta	0.2	Coupe	Heckantrieb	Benzin	7	10	Nov 1953	Dec 1955	2024-03-01	140548
ISO	Autocarro	0.2	Kasten	Heckantrieb	Benzin	7	10	Jan 1954	Dec 1958	2024-03-01	140549
ISO	Autocarro	0.2	Pritsche/Fahrgestell	Heckantrieb	Benzin	7	10	Jan 1954	Dec 1958	2024-03-01	140550
Alpina	D3	S	Stufenheck	Allrad	Diesel/Elektro	261	355	May 2020	Dec 2025	2026-06-01	140554
Alpina	D3	S	Kombi	Allrad	Diesel/Elektro	261	355	May 2020	Dec 2025	2026-06-01	140555
Ligier	Js50	0.5	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2017	-	2024-03-01	140560
Audi	Q5	30 TDI Mild Hybrid	SUV	Frontantrieb	Diesel/Elektro	100	136	Sep 2019	-	2024-03-01	140561
Isorivolta	Gt	300	Coupe	Heckantrieb	Benzin	220	300	Jan 1962	Dec 1970	2024-03-01	140562
Isorivolta	Gt	340	Coupe	Heckantrieb	Benzin	250	340	Jan 1965	Dec 1968	2024-03-01	140563
Isorivolta	Gt	350	Coupe	Heckantrieb	Benzin	257	350	Jan 1969	Dec 1970	2024-03-01	140564
Ligier	Ixo	0.5	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2012	Jul 2014	2024-03-01	140565
Ligier	Xtoo	0.5	Schrägheck	Frontantrieb	Diesel	4	5	Feb 2005	Dec 2012	2024-03-01	140566
Isorivolta	Grifo	GL 300	Coupe	Heckantrieb	Benzin	220	300	Jan 1965	Dec 1970	2024-03-01	140567
Casalini	M12	0.6	Schrägheck	Frontantrieb	Diesel	4	5	Jan 2013	-	2024-03-01	140568
Isorivolta	Grifo	GL 350	Coupe	Heckantrieb	Benzin	250	340	Jan 1965	Dec 1968	2024-03-01	140569
Isorivolta	Grifo	IR 350	Coupe	Heckantrieb	Benzin	257	350	Jan 1969	Dec 1970	2024-03-01	140570
Isorivolta	Grifo	7 Litri	Coupe	Heckantrieb	Benzin	298	406	Jan 1968	Dec 1969	2024-03-01	140571
Isorivolta	Grifo	Ir-9 "can-am"	Coupe	Heckantrieb	Benzin	290	395	Jan 1970	Dec 1972	2024-03-01	140572
Isorivolta	Grifo	5.8	Coupe	Heckantrieb	Benzin	239	325	Jan 1973	Dec 1974	2024-03-01	140573
Isorivolta	Fidia	300	Stufenheck	Heckantrieb	Benzin	220	300	Jan 1967	Dec 1969	2024-03-01	140574
Isorivolta	Fidia	300	Stufenheck	Heckantrieb	Benzin	220	300	Jan 1970	Dec 1972	2024-03-01	140575
Isorivolta	Fidia	350	Stufenheck	Heckantrieb	Benzin	257	350	Jan 1967	Dec 1969	2024-03-01	140576
Isorivolta	Fidia	350	Stufenheck	Heckantrieb	Benzin	257	350	Jan 1970	Dec 1972	2024-03-01	140577
Isorivolta	Fidia	5.8	Stufenheck	Heckantrieb	Benzin	239	325	Jan 1973	Dec 1974	2024-03-01	140578
Isorivolta	Lele	300	Coupe	Heckantrieb	Benzin	220	300	Jan 1970	Dec 1972	2024-03-01	140579
Isorivolta	Lele	300	Coupe	Heckantrieb	Benzin	220	300	Jan 1969	Dec 1969	2024-03-01	140580
Isorivolta	Lele	350	Coupe	Heckantrieb	Benzin	257	350	Jan 1969	Dec 1969	2024-03-01	140581
Isorivolta	Lele	5.8	Coupe	Heckantrieb	Benzin	239	325	Jan 1973	Dec 1974	2024-03-01	140582
Isorivolta	Lele	350	Coupe	Heckantrieb	Benzin	257	350	Jan 1970	Dec 1972	2024-03-01	140583
Alpina	Xb7	Biturbo	SUV	Allrad	Benzin	457	621	May 2020	Nov 2025	2026-06-01	140600
Lamborghini	Huracán	5.2 LP 610-2	Targa	Heckantrieb	Benzin	449	610	May 2020	-	2024-03-01	140604
Bizzarrini	Gt	5300	Coupe	Heckantrieb	Benzin	272	370	Jan 1964	Dec 1968	2024-03-01	140610
Bizzarrini	Gt	1900	Coupe	Heckantrieb	Benzin	82	111	Jan 1967	Dec 1969	2024-03-01	140611


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 BMW 4 Series II（G22）3 个尺寸组：标准后驱 Coupé、420d xDrive、M440i xDrive；不同高度或长度没有强行合并。
* 已闭合 Honda Jazz V、Volvo S60 III、Volvo XC40 I、Audi A3 8Y Sedan；Audi A3 Sportback 与已有 `EU-AUDI-A3-8Y-SPORTBACK-01` 三维一致，直接复用，没有重复建组。([Honda News][1])
* Vito 后驱 Ktype 已拆分为 Compact、Long、Extra Long；116 CDI 4X4 和 119 CDI 4X4 当前确认覆盖 Long、Extra Long，全部复用已有尺寸组。
* 本轮共完成 36 个输入 Ktype，形成 44 条 READY 映射；首次创建 7 个尺寸组，复用 12 个已有尺寸组。

## 当前批次进度

* 已处理输入 Ktype：36 / 100
* READY 映射：44
* PENDING／尚未闭合 Ktype：64
* 已确认尺寸组：19
* 本轮首次创建尺寸组：7
* 复用已有尺寸组：12
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140440	140440	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	HIGH	M440i xDrive外廓分支。	READY
140441	140441	Hatchback	Jazz V		5	EU-HONDA-JAZZ-V-HATCHBACK-01	HIGH		READY
140442	140442	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140443	140443	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140445	140445	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140446	140446	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140448	140448	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive外廓高度分支。	READY
140449	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140450	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140459_compact	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140459_long	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140459_extralong	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140460_compact	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140460_long	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140460_extralong	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140461_long	140461	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	4MATIC Ktype覆盖Long车长分支。	READY
140461_extralong	140461	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	4MATIC Ktype覆盖Extra Long车长分支。	READY
140462_compact	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140462_long	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140462_extralong	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140463_long	140463	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	4MATIC Ktype覆盖Long车长分支。	READY
140463_extralong	140463	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	4MATIC Ktype覆盖Extra Long车长分支。	READY
140464	140464	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
140465	140465	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140466	140466	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140467	140467	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140468	140468	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140470	140470	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140474	140474	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140475	140475	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140476	140476	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140479	140479	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
140489	140489	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
140504	140504	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140506	140506	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140515	140515	Hatchback	A3 IV (8Y)	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
140516	140516	Hatchback	A3 IV (8Y)	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
140517	140517	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140518	140518	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140519	140519	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140520	140520	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140525	140525	Hatchback	Captur II		5	EU-RENAULT-CAPTUR-II-HATCHBACK-01	HIGH		READY
140532	140532	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH		READY
140560	140560	Hatchback	JS50 I facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	4770	1852	1393	BMW Group Technical specifications – The new BMW 4 Series Coupé (M440i xDrive)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-HONDA-JAZZ-V-HATCHBACK-01	4044	1694	1526	Honda News Europe – 2020 Honda Jazz & Jazz Crosstar specifications	https://hondanews.eu/eu/el/cars/media/pressreleases/303367/2020-honda-jazz-and-jazz-crosstar-1
EU-BMW-4-G22-COUPE-01	4768	1852	1383	BMW Group Technical specifications – The new BMW 4 Series Coupé (420i/430i/420d)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group Technical specifications – The new BMW 4 Series Coupé (420d xDrive)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1437	Volvo Support – S60 2020 dimensions	https://www.volvocars.com/jp/support/car/s60/19w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-XC40-I-SUV-01	4425	1863	1658	Volvo Support – XC40 dimensions	https://www.volvocars.com/jp/support/car/xc40/18w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425	Audi MediaCenter – A3 Sportback and A3 Sedan 2020 facts and figures	https://www.audi-mediacenter.com/en/more-dynamic-than-ever-before-the-new-audi-a3-sportback-and-the-new-a3-sedan-2020-12974/facts-and-figures-12977
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz GLE／E-Class／C-Class、Skoda Superb III、Ferrari SF90、Ford Puma／Mondeo／Fiesta、Audi A6 C8、SsangYong Tivoli、Alpina D3／XB7 和 Lamborghini Huracán。
2. 单独解决 BMW 430i xDrive `140444` 与 Audi Q5 `140561` 的时间边界、改款和尺寸组归属，避免错误命中。
3. 最后集中处理 Volvo、Toyota、AMC、ISO／Isorivolta、Bizzarrini及微型车等历史小众车型。

推进信号：CONTINUE

[1]: https://hondanews.eu/eu/el/cars/media/pressreleases/303367/2020-honda-jazz-and-jazz-crosstar-1?utm_source=chatgpt.com "2020 Honda Jazz & Jazz Crosstar"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* `140444` 已按 BMW 官方规格命中既有 G22 xDrive Coupé 尺寸组，不重复建组。官方规格为 4768 × 1852 × 1390 mm，与缓存组一致。
* 新闭合 Mercedes-Benz GLE V167、C-Class S205 Wagon、Škoda Superb III iV 两种车身、Ferrari SF90、Ford Puma、Renault Captur I facelift 与 Audi A6 C8 Avant。([汽车数据网][1])
* `140554`、`140555` 和 `140600` 的生产区间跨越已确认的外廓改款，已分别拆成改款前、改款后派生行，没有任选单一尺寸。([汽车数据网][2])

## 当前批次进度

* 已闭合输入 Ktype：50 / 100
* READY 映射行：61
* 尚未闭合输入 Ktype：50
* 已确认尺寸组：33
* 本轮新增尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140436	140436	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-SUV-01	HIGH		READY
140438	140438	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	MEDIUM		READY
140439	140439	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	HIGH		READY
140444	140444	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH		READY
140451	140451	Hatchback	Superb III facelift		5	EU-SKODA-SUPERB-III-FACELIFT-HATCHBACK-IV-01	HIGH		READY
140452	140452	Wagon	Superb III facelift		5	EU-SKODA-SUPERB-III-FACELIFT-WAGON-IV-01	HIGH		READY
140456	140456	Coupe	SF90 Stradale		2	EU-FERRARI-SF90-STRADALE-COUPE-01	HIGH		READY
140498	140498	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH		READY
140522	140522	Hatchback	Captur I facelift		5	EU-RENAULT-CAPTUR-I-FACELIFT-HATCHBACK-01	HIGH		READY
140538	140538	Wagon	A6 C8		5	EU-AUDI-A6-C8-WAGON-PREFL-01	HIGH		READY
140539	140539	Wagon	A6 C8		5	EU-AUDI-A6-C8-WAGON-PREFL-01	MEDIUM		READY
140554_prefl	140554	Sedan	D3 S	G20	4	EU-ALPINA-D3-S-G20-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
140554_facelift	140554	Sedan	D3 S facelift	G20	4	EU-ALPINA-D3-S-G20-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
140555_prefl	140555	Wagon	D3 S	G21	5	EU-ALPINA-D3-S-G21-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
140555_facelift	140555	Wagon	D3 S facelift	G21	5	EU-ALPINA-D3-S-G21-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
140600_prefl	140600	SUV	XB7	G07	5	EU-ALPINA-XB7-G07-SUV-PREFL-01	MEDIUM	改款前物理外廓。	READY
140600_facelift	140600	SUV	XB7 facelift	G07	5	EU-ALPINA-XB7-G07-SUV-FACELIFT-01	MEDIUM	改款后物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-GLE-V167-SUV-01	4924	1947	1795	Auto-Data Mercedes-Benz GLE V167 GLE 350de	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350de-320hp-plug-in-hybrid-4matic-9g-tronic-37678
EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	4702	1810	1457	Auto-Data Mercedes-Benz C-Class S205 facelift C 300de	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-300de-306hp-eq-power-9g-tronic-50968
EU-SKODA-SUPERB-III-FACELIFT-HATCHBACK-IV-01	4869	1864	1468	Skoda Superb iV official technical data	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-SKODA-SUPERB-III-FACELIFT-WAGON-IV-01	4862	1864	1477	Skoda Superb iV official technical data	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-FERRARI-SF90-STRADALE-COUPE-01	4710	1972	1186	Ferrari SF90 Stradale official technical specifications	https://cdn.ferrari.com/cms/network/media/pdf/pr_ferrari_sf90_stradale_gbr.pdf
EU-FORD-PUMA-II-SUV-01	4186	1805	1550	Auto-Data Ford Puma 1.5 EcoBlue	https://www.auto-data.net/en/ford-puma-1.5-ecoblue-120hp-41778
EU-RENAULT-CAPTUR-I-FACELIFT-HATCHBACK-01	4122	1778	1556	Auto-Data Renault Captur facelift 2017 1.2 TCe	https://www.auto-data.net/en/renault-captur-facelift-2017-1.2-tce-120hp-start-stop-edc-29779
EU-AUDI-A6-C8-WAGON-PREFL-01	4933	1886	1457	ADAC Audi A6 Avant 55 TFSI e sport quattro	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a6/c8/312163/
EU-ALPINA-D3-S-G20-SEDAN-PREFL-01	4719	1827	1440	Auto-Data Alpina D3 Sedan G20 S	https://www.auto-data.net/en/alpina-d3-sedan-g20-s-3.0-355hp-mild-hybrid-awd-switch-tronic-42604
EU-ALPINA-D3-S-G20-SEDAN-FACELIFT-01	4723	1827	1440	Auto-Data Alpina D3 Sedan G20 facelift S	https://www.auto-data.net/en/alpina-d3-sedan-g20-facelift-2022-s-3.0-355hp-mild-hybrid-awd-switch-tronic-45873
EU-ALPINA-D3-S-G21-WAGON-PREFL-01	4719	1827	1438	Auto-Data Alpina D3 Touring G21 S	https://www.auto-data.net/en/alpina-d3-touring-g21-s-3.0-355hp-mild-hybrid-awd-switch-tronic-42602
EU-ALPINA-D3-S-G21-WAGON-FACELIFT-01	4723	1827	1438	Auto-Data Alpina D3 Touring G21 facelift S	https://www.auto-data.net/en/alpina-d3-touring-g21-facelift-2022-s-3.0-355hp-mild-hybrid-awd-swtich-tronic-45874
EU-ALPINA-XB7-G07-SUV-PREFL-01	5151	2000	1797	Auto-Data Alpina XB7	https://www.auto-data.net/en/alpina-xb7-4.4-v8-621hp-xdrive-switch-tronic-42582
EU-ALPINA-XB7-G07-SUV-FACELIFT-01	5178	2000	1797	Auto-Data Alpina XB7 facelift 2022	https://www.auto-data.net/en/alpina-xb7-facelift-2022-4.4-v8-621hp-mild-hybrid-xdrive-switch-tronic-45674
```

## 下一步优先处理

优先闭合 `140437` E-Class Wagon 的改款前后分支，以及 Ford Mondeo、Fiesta Van、SsangYong Tivoli、Audi Q5 和 Lamborghini Huracán；随后集中处理 Toyota Hiace 多轴距、Volvo 历史车型及 ISO／Isorivolta 系列。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350de-320hp-plug-in-hybrid-4matic-9g-tronic-37678 "Mercedes-Benz GLE SUV (V167) GLE 350de (320 Hp) Plug-in Hybrid 4MATIC 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alpina-d3-sedan-g20-s-3.0-355hp-mild-hybrid-awd-switch-tronic-42604?utm_source=chatgpt.com "Alpina D3 Sedan (G20) S 3.0 (355 Hp) Mild Hybrid AWD Switch-Tronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 `140437` Mercedes-Benz E 300 de Wagon，并按 S213 改款前后不同长度拆成两条映射。([汽车数据网][1])
* 闭合 Ford Mondeo、Fiesta Van、SsangYong Tivoli 和 Lamborghini Huracán EVO RWD Spyder。Fiesta Van 使用 Ford 官方不含后视镜尺寸。([汽车目录][2])
* `140561` Audi Q5 按改款前后拆分，直接复用已有 FWD 尺寸组，未重复创建尺寸记录。

## 当前批次进度

* 已闭合输入 Ktype：56 / 100
* READY 映射行：69
* PENDING／尚未闭合 Ktype：44
* 已确认尺寸组：39
* 本轮新增尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140437_prefl	140437	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
140437_facelift	140437	Wagon	E-Class V facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
140505	140505	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	输入车身类型为Stufenheck，实际对应五门掀背外廓。	READY
140523	140523	Van	Fiesta VII	B479	3	EU-FORD-FIESTA-VII-VAN-01	HIGH	三门厢式车物理外廓。	READY
140540	140540	SUV	Tivoli I facelift		5	EU-SSANGYONG-TIVOLI-I-FACELIFT-SUV-01	HIGH		READY
140561_prefl	140561	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	MEDIUM	改款前物理外廓。	READY
140561_facelift	140561	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	MEDIUM	改款后前驱物理外廓。	READY
140604	140604	Convertible	Huracán EVO		2	EU-LAMBORGHINI-HURACAN-EVO-RWD-SPYDER-01	HIGH	输入Targa对应EVO RWD Spyder开放式车身。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class T-Modell S213 E 300de	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-300de-306hp-plug-in-hybrid-9g-tronic-35179
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1476	Auto-Data Mercedes-Benz E-Class T-Modell S213 facelift E 300de	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-300de-306hp-plug-in-hybrid-9g-tronic-40871
EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	4871	1852	1482	Auto-Data Ford Mondeo Hatchback facelift 2.0 EcoBlue	https://www.auto-data.net/en/ford-mondeo-iv-hatchback-facelift-2019-2.0-ecoblue-150hp-37284
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1476	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-SSANGYONG-TIVOLI-I-FACELIFT-SUV-01	4225	1810	1613	Auto-Data SsangYong Tivoli facelift 1.2 T-GDi	https://www.auto-data.net/en/ssangyong-tivoli-facelift-2019-1.2-t-gdi-128hp-42780
EU-LAMBORGHINI-HURACAN-EVO-RWD-SPYDER-01	4520	1933	1180	Automobile-Catalog Lamborghini Huracán EVO RWD Spyder	https://www.automobile-catalog.com/car/2020/2975555/lamborghini_huracan_evo_rwd_spyder.html
```

## 下一步优先处理

优先闭合 Microcar、Volvo 140／PV／Duett／Amazon、Toyota Hiace 多轴距分支和 Audi Q5 之外剩余现代车型；随后集中处理 AMC、ISO、Isorivolta 与 Bizzarrini 历史车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-300de-306hp-plug-in-hybrid-9g-tronic-35179 "Mercedes-Benz E-class T-modell (S213) E 300de (306 Hp) Plug-In Hybrid 9G-TRONIC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/2019/2874335/ford_mondeo_5-dr_2_0_ecoblue_150.html?utm_source=chatgpt.com "2019 Ford Mondeo (5-dr) 2.0 EcoBlue (150) Specs Review (110 kW / 150 PS / 148 hp) (since April 2019 for Europe )"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Ligier IXO；`140566` Ligier X-Too 按官方手册确认同时覆盖 X-Too R 与 X-Too S，两种车长不同，拆为两条映射和两个尺寸组。([汽车数据网][1])
* Volvo PV445 Duett 与 P210 Duett 的三维一致，四个 Ktype 复用同一尺寸组；Volvo P122 S Amazon 单独建组。([Volvotips][2])
* Iso Rivolta Fidia 的 300、350 与后期 5.8 版本外廓一致；Lele 的早期 Chevrolet 动力和后期 Ford 5.8 版本也保持同一外廓，分别复用一个尺寸组。([汽车目录][3])

## 当前批次进度

* 已闭合输入 Ktype：73 / 100
* READY 映射行：87
* PENDING／尚未闭合 Ktype：27
* 已确认尺寸组：46
* 本轮新增尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140493	140493	Wagon	Duett P210	P210	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140495	140495	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140496	140496	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140497	140497	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140499	140499	Sedan	Amazon 120 Series	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-01	HIGH		READY
140565	140565	Hatchback	IXO I facelift		3	EU-LIGIER-IXO-I-FACELIFT-HATCHBACK-01	HIGH		READY
140566_r	140566	Hatchback	X-Too I		3	EU-LIGIER-X-TOO-I-HATCHBACK-R-01	HIGH	X-Too R长车身分支。	READY
140566_s	140566	Hatchback	X-Too I		3	EU-LIGIER-X-TOO-I-HATCHBACK-S-01	HIGH	X-Too S短车身分支。	READY
140574	140574	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140575	140575	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140576	140576	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140577	140577	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140578	140578	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140579	140579	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140580	140580	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140581	140581	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140582	140582	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140583	140583	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-DUETT-PV445-P210-WAGON-01	4400	1600	1700	Volvotips Volvo PV445 and P210 Duett specifications	https://volvotips.com/pv/specifications/
EU-VOLVO-AMAZON-P120-SEDAN-01	4450	1620	1505	CarsGuide 1968 Volvo 122 dimensions	https://www.carsguide.com.au/volvo/122/car-dimensions/1968
EU-LIGIER-IXO-I-FACELIFT-HATCHBACK-01	3148	1524	1497	Auto-Data Ligier IXO 0.5 Progress	https://www.auto-data.net/en/ligier-ixo-0.5-progress-5hp-cvt-54700
EU-LIGIER-X-TOO-I-HATCHBACK-R-01	3035	1475	1498	Ligier X-Too R and S official owner manual	https://www.caen-sud.com/wp-content/uploads/2022/08/MANUEL-UTILISATION-ET-ENTRETIEN-XTOO-R-ET-S-PROGRESS.pdf
EU-LIGIER-X-TOO-I-HATCHBACK-S-01	2900	1475	1498	Ligier X-Too R and S official owner manual	https://www.caen-sud.com/wp-content/uploads/2022/08/MANUEL-UTILISATION-ET-ENTRETIEN-XTOO-R-ET-S-PROGRESS.pdf
EU-ISORIVOLTA-FIDIA-SEDAN-01	4970	1780	1320	Automobile-Catalog 1969 Iso Rivolta Fidia; Automobile-Catalog 1974 Iso Rivolta Fidia	https://www.automobile-catalog.com/make/iso_rivolta/fidia_s4/fidia/1969.html;https://www.automobile-catalog.com/make/iso_rivolta/fidia_s4/fidia/1974.html
EU-ISORIVOLTA-LELE-COUPE-01	4650	1750	1350	Automobile-Catalog 1972 Iso Rivolta Lele; Automobile-Catalog 1974 Iso Rivolta Lele IR 6	https://www.automobile-catalog.com/make/iso_rivolta/lele/lele/1972.html;https://www.automobile-catalog.com/car/1974/1251380/iso_rivolta_lele_ir_6.html
```

## 下一步优先处理

优先闭合 Iso Rivolta GT 与 Grifo 的改款和高发动机盖分支，以及 Bizzarrini GT；随后处理 Microcar M.Go、Casalini M12、ISO Isetta／Autocarro、Toyota Hiace 多轴距和仍需确认门数边界的 Volvo 140／PV444。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ligier-ixo-0.5-progress-5hp-cvt-54700?utm_source=chatgpt.com "Ligier IXO 0.5 Progress (5 Hp) CVT /Quadricycle 2010"
[2]: https://volvotips.com/pv/specifications/?utm_source=chatgpt.com "Specifications PV"
[3]: https://www.automobile-catalog.com/make/iso_rivolta/fidia_s4/fidia/1969.html?utm_source=chatgpt.com "1969 Iso Rivolta Fidia full range specs"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Isorivolta GT 300／340／350，共用 Rivolta IR 车身尺寸组。
* Grifo 标准车身按 Series I 与 Series II 拆分；`140567`、`140570` 跨越 1970 年外廓改款，因此各输出改款前后两条派生映射。
* Grifo 7 Litri、Can-Am 与 IR-8 因车头、发动机盖或整体高度不同，分别建立尺寸组，未强行合并。Series I 标准车身为 4430 × 1770 × 1200 mm，7 Litri 高度为 1220 mm；Series II 标准车身长 4600 mm，Can-Am 高度为 1220 mm，IR-8 为 1200 mm。([汽车目录][1])
* 闭合 Bizzarrini 5300 GT Strada 与 1900 GT Europa；两者分别采用 4370 × 1760 × 1110 mm、3790 × 1620 × 1040 mm。([汽车目录][2])

## 当前批次进度

* 已闭合输入 Ktype：84 / 100
* READY 映射行：100
* PENDING／尚未闭合 Ktype：16
* 已确认尺寸组：54
* 本轮新增尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140562	140562	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140563	140563	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140564	140564	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140567_prefl	140567	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	MEDIUM	1970年改款前物理外廓。	READY
140567_facelift	140567	Coupe	Grifo Series II		2	EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	MEDIUM	1970年改款后物理外廓。	READY
140569	140569	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	HIGH		READY
140570_prefl	140570	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	MEDIUM	1970年改款前物理外廓。	READY
140570_facelift	140570	Coupe	Grifo Series II		2	EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	MEDIUM	1970年改款后物理外廓。	READY
140571	140571	Coupe	Grifo Series I 7 Litri		2	EU-ISORIVOLTA-GRIFO-7-LITRI-COUPE-01	HIGH	高发动机盖外廓。	READY
140572	140572	Coupe	Grifo Series II Can-Am		2	EU-ISORIVOLTA-GRIFO-CAN-AM-COUPE-01	HIGH	Series II隐藏式前灯及高发动机盖外廓。	READY
140573	140573	Coupe	Grifo Series II IR-8		2	EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	HIGH	IR-8外廓。	READY
140610	140610	Coupe	5300 GT Strada		2	EU-BIZZARRINI-5300-GT-STRADA-COUPE-01	HIGH		READY
140611	140611	Coupe	1900 GT Europa		2	EU-BIZZARRINI-1900-GT-EUROPA-COUPE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	4760	1752	1425	Automobile-Catalog Iso Rivolta IR 300	https://www.automobile-catalog.com/car/1963/1250525/iso_rivolta_ir_300.html
EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	4430	1770	1200	Automobile-Catalog Iso Grifo L GL 350 Series I	https://www.automobile-catalog.com/car/1968/1250900/iso_grifo_l_gl_350.html
EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	4600	1770	1200	Automobile-Catalog Iso Grifo L 350 Series II	https://www.automobile-catalog.com/car/1972/1251170/iso_grifo_l_350.html
EU-ISORIVOLTA-GRIFO-7-LITRI-COUPE-01	4430	1770	1220	Automobile-Catalog Iso Grifo 7 Litri	https://www.automobile-catalog.com/car/1969/1251050/iso_grifo_7_litri_2_32_axle_ratio.html
EU-ISORIVOLTA-GRIFO-CAN-AM-COUPE-01	4600	1770	1220	Automobile-Catalog Iso Grifo Can-Am	https://www.automobile-catalog.com/car/1971/1251350/iso_grifo_can-am.html
EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	4600	1770	1200	Automobile-Catalog Iso Grifo IR-8	https://www.automobile-catalog.com/car/1974/1251470/iso_grifo_ir_8.html
EU-BIZZARRINI-5300-GT-STRADA-COUPE-01	4370	1760	1110	Automobile-Catalog Bizzarrini GT Strada 5300	https://www.automobile-catalog.com/car/1966/261995/bizzarini_gt_strada_5300__gt_america_3_48_axle.html
EU-BIZZARRINI-1900-GT-EUROPA-COUPE-01	3790	1620	1040	Automobile-Catalog Bizzarrini GT Europa 1900	https://www.automobile-catalog.com/car/1966/261920/bizzarini_gt_europa_1900_3_73_axle.html
```

## 下一步优先处理

集中闭合剩余 16 个 Ktype：Microcar M.Go、Volvo 140／PV444、Toyota Hiace IV 多轴距、AMC Matador／Hornet、ISO Isetta／Autocarro及 Casalini M12。优先处理能够共用尺寸组的 Volvo PV444 与 ISO 商用车分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1968/1250900/iso_grifo_l_gl_350.html?utm_source=chatgpt.com "1968 Iso Grifo L GL 350 (man. 4) (model for Europe North ..."
[2]: https://www.automobile-catalog.com/car/1966/261995/bizzarini_gt_strada_5300__gt_america_3_48_axle.html?utm_source=chatgpt.com "1966 Bizzarini GT Strada 5300 / GT America (3.48 axle) Specs Review (261 kW / 355 PS / 350 hp) (since mid-year 1966 for Europe North America )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 闭合 Microcar M.GO 6、Volvo PV444、Iso Isetta 与 Casalini M12；Casalini M12 已确认三门车身及 3010 × 1500 × 1500 mm 外廓。([Engine In Detail][1])
* `140485`、`140486` 的上游车型范围均明确覆盖 Volvo 142 与 144，因此分别拆成两门和四门派生行；两种车身外廓尺寸相同，但物理车身不同，分别建组。([Retromotion][2])
* `140545` AMC Matador Wagon 按 1971–1973 与 1974 外廓拆分；1974 年车身因保险杠及前后造型变化增长至 5474 mm。([汽车目录][3])
* `140546` 输入车身形式为 Schrägheck，但该 1970 年版本实际覆盖两门和四门 Sedan，已纠正并拆分。([汽车目录][4])

## 当前批次进度

* 已闭合输入 Ktype：96 / 100
* READY 映射行：116
* PENDING／尚未闭合 Ktype：4
* 已确认尺寸组：64
* 本轮首次创建尺寸组：10
* 剩余 Ktype：`140511`、`140512`、`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140429	140429	Hatchback	M.GO 6		3	EU-MICROCAR-MGO6-HATCHBACK-01	HIGH		READY
140485_2dr	140485	Sedan	140 Series facelift II	142	2	EU-VOLVO-140-142-SEDAN-01	HIGH	142两门车身分支。	READY
140485_4dr	140485	Sedan	140 Series facelift II	144	4	EU-VOLVO-140-144-SEDAN-01	HIGH	144四门车身分支。	READY
140486_2dr	140486	Sedan	140 Series facelift I	142	2	EU-VOLVO-140-142-SEDAN-01	HIGH	142两门车身分支。	READY
140486_4dr	140486	Sedan	140 Series facelift I	144	4	EU-VOLVO-140-144-SEDAN-01	HIGH	144四门车身分支。	READY
140487	140487	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140488	140488	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140490	140490	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140491	140491	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140492	140492	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140545_prefl	140545	Wagon	Matador I		5	EU-AMC-MATADOR-I-WAGON-01	MEDIUM	1971至1973年物理外廓。	READY
140545_facelift	140545	Wagon	Matador II		5	EU-AMC-MATADOR-II-WAGON-01	MEDIUM	1974年增长后的物理外廓。	READY
140546_2dr	140546	Sedan	Hornet I		2	EU-AMC-HORNET-I-SEDAN-2D-01	MEDIUM	输入Schrägheck已纠正为两门Sedan分支。	READY
140546_4dr	140546	Sedan	Hornet I		4	EU-AMC-HORNET-I-SEDAN-4D-01	MEDIUM	输入Schrägheck已纠正为四门Sedan分支。	READY
140548	140548	Coupe	Isetta		1	EU-ISO-ISETTA-COUPE-01	HIGH	单前门车身。	READY
140568	140568	Hatchback	M12		3	EU-CASALINI-M12-HATCHBACK-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MICROCAR-MGO6-HATCHBACK-01	2999	1500	1560	Engine in Detail Microcar M.Go 6 X Diesel Progress ACT	https://www.engineindetail.com/pa/microcar-m-go-6-x-diesel-progress-act-2019
EU-VOLVO-140-142-SEDAN-01	4640	1730	1440	Motorsporlari 1972 Volvo 142 Saloon technical specifications	https://eng.motorsporlari.net/car/tech_spec.asp?make=Volvo&specID=19748
EU-VOLVO-140-144-SEDAN-01	4640	1730	1440	ADAC Volvo 144 2.0 DL technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/volvo/142-144-145/1generation-facelift-2/349620/
EU-VOLVO-PV444-SEDAN-01	4500	1570	1520	Volvotips Volvo PV444 and PV544 specifications	https://volvotips.com/pv/specifications/
EU-AMC-MATADOR-I-WAGON-01	5207	1962	1430	Automobile-Catalog 1971 AMC Matador Wagon	https://www.automobile-catalog.com/car/1971/70205/amc_matador_wagon_v-8_360_automatic.html
EU-AMC-MATADOR-II-WAGON-01	5474	1961	1443	Automobile-Catalog 1974 AMC Matador Wagon	https://www.automobile-catalog.com/car/1974/71420/amc_matador_wagon_v-8_360-4_220_automatic.html
EU-AMC-HORNET-I-SEDAN-2D-01	4553	1805	1336	Automobile-Catalog 1970 AMC Hornet Sedan 199	https://www.automobile-catalog.com/car/1970/68045/amc_hornet_sedan_199.html
EU-AMC-HORNET-I-SEDAN-4D-01	4553	1805	1336	Automobile-Catalog 1970 AMC Hornet Sedan 199	https://www.automobile-catalog.com/car/1970/68045/amc_hornet_sedan_199.html
EU-ISO-ISETTA-COUPE-01	2250	1340	1320	Automobile-Catalog 1954 Iso Isetta	https://www.automobile-catalog.com/car/1954/1240970/isetta.html
EU-CASALINI-M12-HATCHBACK-01	3010	1500	1500	Automoto.it Casalini M12 SF technical sheet	https://www.automoto.it/catalogo/casalini/m12/m12-sf/102201
```

## 下一步优先处理

1. 解码 Toyota HiAce `RZH103` 与 `RZH113` 的车长、轴距和车顶边界，分别闭合 `140511`、`140512`，不得用 H100 系列范围尺寸代替具体外廓。
2. 补齐 Iso Autocarro Van 与 Pickup 的完整高度和车身边界，闭合 `140549`、`140550`。
3. 四个 Ktype 闭合后立即进行一次机械检查，并输出两张最终完整 TSV及指定下载链接。

推进信号：CONTINUE

[1]: https://www.engineindetail.com/pa/microcar-m-go-6-x-diesel-progress-act-2019?utm_source=chatgpt.com "Microcar M.Go 6 X Diesel Progress ACT 2019 - Specs, Review & Tests"
[2]: https://retromotion.com/ersatzteile/fahrzeuge/volvo/140-142-144/2-0-103-kw-140-ps-ab-09-1971-bis-08-1972?utm_source=chatgpt.com "Ersatzteile für VOLVO 140 (142, 144) 2.0 | 103 KW / 140 PS | ab 09/1971 bis 08/1972 ☑️ VOLVO 140 (142, 144) Teilekatalog ❤️ Retromotion"
[3]: https://www.automobile-catalog.com/car/1971/70205/amc_matador_wagon_v-8_360_automatic.html?utm_source=chatgpt.com "1971 AMC Matador Wagon V-8 360-4 automatic (aut. 3)"
[4]: https://www.automobile-catalog.com/car/1970/68045/amc_hornet_sedan_199.html?utm_source=chatgpt.com "1970 AMC Hornet Sedan 199 Specs Review (95.5 kW ..."


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* `140511` 与 `140512` 均确认覆盖 H100 的 `RZH103R` 短轴厢式车和 `RZH113R` 长轴厢式车，分别拆为 SWB、LWB 两个物理分支。1998 年 2.4 与 2.4i 资料显示两种分支三维一致；GoAuto 明确标注 1690 mm 为不含后视镜宽度。([Carsales][1])
* `140549` 与 `140550` 暂未闭合。可靠资料确认 Autocarro 存在平板、帆布斗和更高的封闭货厢等不同上装，但现有可追溯资料仅提供部分版本长度，无法获得分别对应封闭厢式车与平板/底盘车的完整三维，不能强行创建尺寸组。([RM Sotheby's][2])

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建尺寸组：2
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140511_swb	140511	Van	HiAce IV (H100)	RZH103R	4	EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	MEDIUM	RZH103R短轴厢式车分支。	READY
140511_lwb	140511	Van	HiAce IV (H100)	RZH113R	4	EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	MEDIUM	RZH113R长轴厢式车分支。	READY
140512_swb	140512	Van	HiAce IV (H100)	RZH103R	4	EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	MEDIUM	RZH103R短轴厢式车分支。	READY
140512_lwb	140512	Van	HiAce IV (H100)	RZH113R	4	EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	MEDIUM	RZH113R长轴厢式车分支。	READY
140549	140549	Van	Isettacarro 500			LOW	Autofurgone封闭货厢的完整外廓尚未闭合。	PENDING: 封闭货厢高度和完整三维未确认
140550	140550	Pickup	Isettacarro 500			LOW	平板或底盘上装的完整外廓尚未闭合。	PENDING: 平板或底盘上装高度和完整三维未确认
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	4570	1690	1940	Carsales / RedBook 1998 Toyota Hiace RZH103R specifications;GoAuto Toyota Hiace RZH103R SWB exterior dimensions	https://www.carsales.com.au/research/toyota/hiace/1998/no-badge/f973ea03-43ab-44b1-afcc-bbf9849c2235/;https://www.goauto.com.au/car-reviews/toyota/hiace/swb-van/2003-10-07/55860.html
EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	4830	1690	1930	Carsales / RedBook 1998 Toyota Hiace RZH113R specifications;GoAuto Toyota Hiace RZH113R LWB exterior dimensions	https://www.carsales.com.au/research/toyota/hiace/1998/no-badge/89389273-1a1d-4b60-a855-5565a27309c8/;https://www.goauto.com.au/car-reviews/toyota/hiace/lwb-van/2003-10-07/54510.html
```

## 下一步优先处理

仅处理 `140549`、`140550`：优先寻找 Iso 原厂 Autocarro／Autofurgone 500 手册、型式资料或可区分封闭厢式车与平板车的完整长宽高记录。若仍只能确认底盘长度或单一改装实例，两行继续保持 PENDING，不使用非可靠摘要强行清零。

推进信号：CONTINUE

[1]: https://www.carsales.com.au/research/toyota/hiace/1998/no-badge/8134acb8-385a-42a8-8f43-6ebacb4893a2/ "Toyota Hiace 1998 (No Badge) Pricing & Specifications - carsales"
[2]: https://rmsothebys.com/auctions/bw13/lots/r240-1957-iso-isettacarro/ "1957 Iso Isettacarro | The Bruce Weiner Microcar Museum | RM Sotheby's"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已确认 `140549` 对应 **Iso Autofurgone 500** 封闭货厢，`140550` 对应 **Iso Autocarro 500** 平板货车；两者是独立车身，不能共用一个尺寸组。1959 年原厂手册目录也分别列出 Autocarro 500 与 Autofurgone 500。([isetta.org.uk][1])
* 可追溯资料目前只闭合 Autocarro 的长度 3505 mm、宽度 1475 mm，未提供高度；Autofurgone 的封闭货厢高度及完整三维仍缺失，因此本轮不创建不完整尺寸组。([RM Sotheby's][2])

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140549	140549	Van	Autofurgone 500			LOW	封闭货厢为独立物理车身，候选资料尚缺完整三维。	PENDING: Autofurgone 500完整长宽高未确认
140550	140550	Pickup	Autocarro 500			LOW	平板货车为独立物理车身，现有资料缺少整车高度。	PENDING: Autocarro 500整车高度未确认
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 仅查找 Iso 原厂《Isetta, Autocarro 500 & Autofurgone 500》手册中的尺寸页或同期型式批准资料。
2. 优先补齐 Autocarro 500 整车高度；不得根据照片、模型比例或普通 Isetta 驾驶室高度推算。
3. 补齐 Autofurgone 500 同一配置的完整长宽高后，立即创建两个独立尺寸组并清零 PENDING。

推进信号：CONTINUE

[1]: https://www.isetta.org.uk/page46.html?utm_source=chatgpt.com "Variations of an Isetta Theme"
[2]: https://rmsothebys.com/auctions/bw13/lots/r240-1957-iso-isettacarro/ "1957 Iso Isettacarro | The Bruce Weiner Microcar Museum | RM Sotheby's"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 最后两条物理边界已确认无误：`140549` 是 **Autofurgone 500 封闭货厢**，`140550` 是 **Autocarro 500 开放式货斗**，原车型资料明确将两者区分，不能复用同一尺寸组。([IMCDb.org][1])
* 本轮仍未找到可直接落盘的完整规格：Autocarro 现有资料缺整车高度，Autofurgone 缺同一配置的完整长宽高；普通 Iso Isetta 的尺寸不能代替商用加长底盘和不同上装。([维基百科][2])
* 未强行推算尺寸，未创建不完整尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

仅继续查找 1959 年《Isetta, Autocarro 500 & Autofurgone 500》原厂手册尺寸页、同期型式批准资料或车身制造技术目录，补齐：

1. Autocarro 500 的整车高度。
2. Autofurgone 500 同一封闭货厢配置的完整长宽高。
3. 宽度为不含后视镜口径的明确证据。

推进信号：CONTINUE

[1]: https://www.imcdb.org/v028477.html "IMCDb.org: Iso Autofurgone 500 in \"Checkpoint, 1956\""
[2]: https://it.wikipedia.org/wiki/Iso_Isetta?utm_source=chatgpt.com "Iso Isetta"


--- 发送 / 继续到 Round 10 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 10 / 下一步 ---
## 更新点

* 本轮仅核对剩余 `140549`、`140550`。可追溯资料继续支持两者为不同车身：Autofurgone 500 封闭货厢与 Autocarro 500 开放式货斗，不能合并。([Isetta][1])
* 两种车身目前均可确认长度 `3505 mm`、宽度 `1475 mm`，但资料未给出整车高度；Autofurgone 也缺少能够同时支持完整三维的直接规格页，因此仍不具备建组条件。([Auta5P][2])
* 未采用照片比例、普通 Isetta 驾驶室高度或非可靠社交媒体数据进行推算。

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

仅继续查找包含尺寸页的 Iso 原厂《Isetta, Autocarro 500 & Autofurgone 500》手册扫描件、同期型式批准记录或车身制造技术目录，优先补齐两种独立车身的整车高度及 Autofurgone 完整三维；其他 98 个 Ktype 和既有尺寸组不再复核。

推进信号：CONTINUE

[1]: https://www.isetta.org.uk/page46.html "Variations of an Isetta Theme"
[2]: https://auta5p.eu/katalog/iso/isetta_02.php "ISO Autocarro 500, 1955 [Auta5P ID:7157 CZ]"


--- 发送 / 继续到 Round 11 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 11 / 下一步 ---
## 更新点

* 本轮继续只核对 `140549`、`140550`，未复查其他已闭合 Ktype 或尺寸组。
* 已定位到 1959 年 64 页原厂车主手册，目录明确同时覆盖 **Isetta、Autocarro 500、Autofurgone 500**，但公开页面仅提供书目信息，未开放尺寸页。([autolit.eu][1])
* Autocarro 500 目前仍只能可靠闭合长度 `3505 mm`、宽度 `1475 mm`；现有规格页明确缺少高度。([Auta5P][2])
* Autofurgone 500 与开放式 Autocarro 500 已确认是不同上装和独立物理车身，不能套用同一高度或尺寸组。([IMCDb.org][3])
* 本轮未获得可直接落盘的完整三维，因此不创建尺寸组、不强行清零。

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

继续寻找上述 1959 年原厂手册的完整扫描件或同期型式批准资料，仅补齐：

1. `140550` Autocarro 500 的整车高度。
2. `140549` Autofurgone 500 同一封闭货厢配置的完整长宽高。
3. 两种车身宽度均为不含后视镜口径的可追溯证明。

推进信号：CONTINUE

[1]: https://www.autolit.eu/en/iso-isetta/17871-1959-iso-isetta-autocarro-500-owners-manual-italian.html?utm_source=chatgpt.com "1959 ISO ISETTA & AUTOCARRO 500 OWNERS MANUAL ..."
[2]: https://auta5p.eu/katalog/iso/isetta_02.php "ISO Autocarro 500, 1955 [Auta5P ID:7157 CZ]"
[3]: https://www.imcdb.org/v028477.html?utm_source=chatgpt.com "IMCDb.org: Iso Autofurgone 500 in \"Checkpoint, 1956\""


--- 发送 / 继续到 Round 12 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 12 / 下一步 ---
## 更新点

* 本轮仅核对 `140549`、`140550`，未重新检查其他 Ktype 或既有尺寸组。
* Bruce Weiner Microcar Museum 的车辆规格进一步确认 Autocarro 长度为 11 ft 6 in、宽度为 4 ft 10 in，约合 `3505 × 1473 mm`，与既有 `3505 × 1475 mm` 资料基本一致，但仍未提供整车高度。([微型车博物馆][1])
* 同期资料明确说明 Autocarro 存在低篷平板车和更高封闭箱体等多种上装，因此不能把某一实车的高度直接套用于 `140549` Autofurgone 或全部 `140550` Pickup/Fahrgestell。([RM Sotheby's][2])
* 未获得可直接落盘的完整三维，本轮不创建尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

仅继续寻找能够明确对应 **Autofurgone 500 封闭箱体**和 **Autocarro 500 标准开放货斗**的原厂尺寸图、型式批准表或历史登记资料，重点补齐各自整车高度；不使用照片测量、社交媒体转述或不同上装实车的高度替代。

推进信号：CONTINUE

[1]: https://www.microcarmuseum.com/tour/isettacarro.html?utm_source=chatgpt.com "1957 Isettacarro"
[2]: https://rmsothebys.com/auctions/bw13/lots/r240-1957-iso-isettacarro/?utm_source=chatgpt.com "1957 Iso Isettacarro | The Bruce Weiner Microcar Museum"


--- 发送 / 继续到 Round 13 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 13 / 下一步 ---
## 更新点

* 本轮仅核对 `140549`、`140550`，未复查其他 Ktype 或既有尺寸组。
* 检索到 `1250 mm` 高度数据，但仅出现在来源不明的社交媒体转载中，无法追溯至原厂资料或可靠规格数据库，按规则拒绝落盘。([Facebook][1])
* 可追溯规格页仍只提供 Autocarro 的 `3505 mm` 长度和 `1475 mm` 宽度，高度字段为空；Autofurgone 也未找到完整三维。([Auta5P][2])
* 本轮未创建或修改尺寸组。

## 当前批次进度

* 已闭合输入 Ktype：98 / 100
* READY 映射：120
* PENDING 映射：2
* 已确认尺寸组：66
* 本轮首次创建／修正尺寸组：0
* 剩余 PENDING：`140549`、`140550`
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

无

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 下一步优先处理

仅继续寻找 Iso 原厂手册完整扫描件、同期型式批准资料或可靠历史技术目录，补齐 Autocarro 500 标准开放货斗的整车高度，以及 Autofurgone 500 封闭货厢的完整长宽高；不采用无法追溯的 `1250 mm` 数据。

推进信号：CONTINUE

[1]: https://www.facebook.com/groups/950689934973969/posts/2924620344247575/?utm_source=chatgpt.com "Does the Iso Carro fit the description or is it a bit borderline ..."
[2]: https://auta5p.eu/lang/en/katalog/auto.php?idf=ISO-Autocarro-27889&utm_source=chatgpt.com "ISO Autocarro, 1957 [Auta5P ID:27889 EN]"


--- 发送 / 继续到 Round 14 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- 脚本异常 ---
异常: Playwright browser 请求失败 (eval): 
{
  "ok": false,
  "error": "locator.waitFor: Timeout 20000ms exceeded.\nCall log:\n\u001B[2m  - waiting for locator(\u0027body\u0027)\u001B[22m\n\n    at runAction (/Users/admin/Documents/GitHub/fitment_sheet_generation/projects/qclaw_fitment_automation/playwright_browser_bridge.js:167:32)\n    at async Server.\u003Canonymous\u003E (/Users/admin/Documents/GitHub/fitment_sheet_generation/projects/qclaw_fitment_automation/playwright_browser_bridge.js:222:16)"
}


--- 发送 / checkpoint 续跑到 Round 15 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_501-600_ktype_dimension_mapping_final.tsv
- all_501-600_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 15 / checkpoint 续跑 ---
## 更新点

* `140549` 已闭合为 **Autofurgone 500 封闭货厢**，尺寸为 `3470 × 1400 × 1650 mm`。
* `140550` 已闭合为 **Autocarro 500 标准开放货斗**，尺寸为 `3470 × 1400 × 1360 mm`。同期资料明确指出两种车身长宽相同，但封闭货厢高度为 1.65 m，开放货斗高度为 1.36 m。([Scribd][1])
* 已完成机械检查：固定表头正确、`id` 和 `DIMENSION_GROUP_ID` 唯一、全部引用闭合、尺寸与来源非空、两个指定文件已生成。

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：122
* PENDING 映射：0
* DIMENSION_GROUP：70
* 孤立尺寸组：0
* 未闭合引用：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
140429	140429	Hatchback	M.GO 6		3	EU-MICROCAR-MGO6-HATCHBACK-01	HIGH		READY
140436	140436	SUV	GLE II	V167	5	EU-MERCEDES-BENZ-GLE-V167-SUV-01	HIGH		READY
140437_prefl	140437	Wagon	E-Class V	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
140437_facelift	140437	Wagon	E-Class V facelift	S213	5	EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
140438	140438	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	MEDIUM		READY
140439	140439	Wagon	C-Class IV facelift	S205	5	EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	HIGH		READY
140440	140440	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	HIGH	M440i xDrive外廓分支。	READY
140441	140441	Hatchback	Jazz V		5	EU-HONDA-JAZZ-V-HATCHBACK-01	HIGH		READY
140442	140442	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140443	140443	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140444	140444	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH		READY
140445	140445	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140446	140446	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-01	HIGH		READY
140448	140448	Coupe	4 Series II	G22	2	EU-BMW-4-G22-COUPE-XDRIVE-01	HIGH	xDrive外廓高度分支。	READY
140449	140449	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140450	140450	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140451	140451	Hatchback	Superb III facelift		5	EU-SKODA-SUPERB-III-FACELIFT-HATCHBACK-IV-01	HIGH		READY
140452	140452	Wagon	Superb III facelift		5	EU-SKODA-SUPERB-III-FACELIFT-WAGON-IV-01	HIGH		READY
140456	140456	Coupe	SF90 Stradale		2	EU-FERRARI-SF90-STRADALE-COUPE-01	HIGH		READY
140459_compact	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140459_long	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140459_extralong	140459	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140460_compact	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140460_long	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140460_extralong	140460	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140461_long	140461	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	4MATIC Ktype覆盖Long车长分支。	READY
140461_extralong	140461	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	4MATIC Ktype覆盖Extra Long车长分支。	READY
140462_compact	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	MEDIUM	同一Ktype覆盖Compact车长分支。	READY
140462_long	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	同一Ktype覆盖Long车长分支。	READY
140462_extralong	140462	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	同一Ktype覆盖Extra Long车长分支。	READY
140463_long	140463	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	MEDIUM	4MATIC Ktype覆盖Long车长分支。	READY
140463_extralong	140463	Van	Vito W447 facelift	W447		EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	MEDIUM	4MATIC Ktype覆盖Extra Long车长分支。	READY
140464	140464	Sedan	S60 III		4	EU-VOLVO-S60-III-SEDAN-01	HIGH		READY
140465	140465	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140466	140466	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140467	140467	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140468	140468	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140470	140470	Wagon	V60 II		5	EU-VOLVO-V60-II-WAGON-01	HIGH		READY
140474	140474	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140475	140475	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140476	140476	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-01	HIGH		READY
140479	140479	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-01	HIGH		READY
140485_2dr	140485	Sedan	140 Series facelift II	142	2	EU-VOLVO-140-142-SEDAN-01	HIGH	142两门车身分支。	READY
140485_4dr	140485	Sedan	140 Series facelift II	144	4	EU-VOLVO-140-144-SEDAN-01	HIGH	144四门车身分支。	READY
140486_2dr	140486	Sedan	140 Series facelift I	142	2	EU-VOLVO-140-142-SEDAN-01	HIGH	142两门车身分支。	READY
140486_4dr	140486	Sedan	140 Series facelift I	144	4	EU-VOLVO-140-144-SEDAN-01	HIGH	144四门车身分支。	READY
140487	140487	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140488	140488	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140489	140489	SUV	XC90 II		5	EU-VOLVO-XC90-II-SUV-01	HIGH		READY
140490	140490	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140491	140491	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140492	140492	Sedan	PV444	PV444	2	EU-VOLVO-PV444-SEDAN-01	HIGH		READY
140493	140493	Wagon	Duett P210	P210	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140495	140495	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140496	140496	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140497	140497	Wagon	Duett PV445	PV445	3	EU-VOLVO-DUETT-PV445-P210-WAGON-01	HIGH		READY
140498	140498	SUV	Puma II		5	EU-FORD-PUMA-II-SUV-01	HIGH		READY
140499	140499	Sedan	Amazon 120 Series	P120	4	EU-VOLVO-AMAZON-P120-SEDAN-01	HIGH		READY
140504	140504	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140505	140505	Hatchback	Mondeo V facelift		5	EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	HIGH	输入车身类型为Stufenheck，实际对应五门掀背外廓。	READY
140506	140506	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140511_swb	140511	Van	HiAce IV (H100)	RZH103R	4	EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	MEDIUM	RZH103R短轴厢式车分支。	READY
140511_lwb	140511	Van	HiAce IV (H100)	RZH113R	4	EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	MEDIUM	RZH113R长轴厢式车分支。	READY
140512_swb	140512	Van	HiAce IV (H100)	RZH103R	4	EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	MEDIUM	RZH103R短轴厢式车分支。	READY
140512_lwb	140512	Van	HiAce IV (H100)	RZH113R	4	EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	MEDIUM	RZH113R长轴厢式车分支。	READY
140515	140515	Hatchback	A3 IV (8Y)	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
140516	140516	Hatchback	A3 IV (8Y)	8YA	5	EU-AUDI-A3-8Y-SPORTBACK-01	HIGH		READY
140517	140517	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140518	140518	Sedan	A3 IV (8Y)	8YS	4	EU-AUDI-A3-8Y-SEDAN-01	HIGH		READY
140519	140519	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL-HATCHBACK-01	HIGH		READY
140520	140520	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL-WAGON-01	HIGH		READY
140522	140522	Hatchback	Captur I facelift		5	EU-RENAULT-CAPTUR-I-FACELIFT-HATCHBACK-01	HIGH		READY
140523	140523	Van	Fiesta VII	B479	3	EU-FORD-FIESTA-VII-VAN-01	HIGH	三门厢式车物理外廓。	READY
140525	140525	Hatchback	Captur II		5	EU-RENAULT-CAPTUR-II-HATCHBACK-01	HIGH		READY
140532	140532	SUV	EcoSport II facelift		5	EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	HIGH		READY
140538	140538	Wagon	A6 C8		5	EU-AUDI-A6-C8-WAGON-PREFL-01	HIGH		READY
140539	140539	Wagon	A6 C8		5	EU-AUDI-A6-C8-WAGON-PREFL-01	MEDIUM		READY
140540	140540	SUV	Tivoli I facelift		5	EU-SSANGYONG-TIVOLI-I-FACELIFT-SUV-01	HIGH		READY
140545_prefl	140545	Wagon	Matador I		5	EU-AMC-MATADOR-I-WAGON-01	MEDIUM	1971至1973年物理外廓。	READY
140545_facelift	140545	Wagon	Matador II		5	EU-AMC-MATADOR-II-WAGON-01	MEDIUM	1974年增长后的物理外廓。	READY
140546_2dr	140546	Sedan	Hornet I		2	EU-AMC-HORNET-I-SEDAN-2D-01	MEDIUM	输入Schrägheck已纠正为两门Sedan分支。	READY
140546_4dr	140546	Sedan	Hornet I		4	EU-AMC-HORNET-I-SEDAN-4D-01	MEDIUM	输入Schrägheck已纠正为四门Sedan分支。	READY
140548	140548	Coupe	Isetta		1	EU-ISO-ISETTA-COUPE-01	HIGH	单前门车身。	READY
140549	140549	Van	Autofurgone 500			EU-ISO-AUTOFURGONE-500-VAN-01	MEDIUM	封闭货厢独立外廓。	READY
140550	140550	Pickup	Autocarro 500			EU-ISO-AUTOCARRO-500-PICKUP-01	MEDIUM	标准开放货斗独立外廓。	READY
140554_prefl	140554	Sedan	D3 S	G20	4	EU-ALPINA-D3-S-G20-SEDAN-PREFL-01	HIGH	改款前物理外廓。	READY
140554_facelift	140554	Sedan	D3 S facelift	G20	4	EU-ALPINA-D3-S-G20-SEDAN-FACELIFT-01	HIGH	改款后物理外廓。	READY
140555_prefl	140555	Wagon	D3 S	G21	5	EU-ALPINA-D3-S-G21-WAGON-PREFL-01	HIGH	改款前物理外廓。	READY
140555_facelift	140555	Wagon	D3 S facelift	G21	5	EU-ALPINA-D3-S-G21-WAGON-FACELIFT-01	HIGH	改款后物理外廓。	READY
140560	140560	Hatchback	JS50 I facelift		3	EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	HIGH		READY
140561_prefl	140561	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SUV-01	MEDIUM	改款前物理外廓。	READY
140561_facelift	140561	SUV	Q5 II facelift	FY	5	EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	MEDIUM	改款后前驱物理外廓。	READY
140562	140562	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140563	140563	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140564	140564	Coupe	Rivolta IR		2	EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	HIGH		READY
140565	140565	Hatchback	IXO I facelift		3	EU-LIGIER-IXO-I-FACELIFT-HATCHBACK-01	HIGH		READY
140566_r	140566	Hatchback	X-Too I		3	EU-LIGIER-X-TOO-I-HATCHBACK-R-01	HIGH	X-Too R长车身分支。	READY
140566_s	140566	Hatchback	X-Too I		3	EU-LIGIER-X-TOO-I-HATCHBACK-S-01	HIGH	X-Too S短车身分支。	READY
140567_prefl	140567	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	MEDIUM	1970年改款前物理外廓。	READY
140567_facelift	140567	Coupe	Grifo Series II		2	EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	MEDIUM	1970年改款后物理外廓。	READY
140568	140568	Hatchback	M12		3	EU-CASALINI-M12-HATCHBACK-01	HIGH		READY
140569	140569	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	HIGH		READY
140570_prefl	140570	Coupe	Grifo Series I		2	EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	MEDIUM	1970年改款前物理外廓。	READY
140570_facelift	140570	Coupe	Grifo Series II		2	EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	MEDIUM	1970年改款后物理外廓。	READY
140571	140571	Coupe	Grifo Series I 7 Litri		2	EU-ISORIVOLTA-GRIFO-7-LITRI-COUPE-01	HIGH	高发动机盖外廓。	READY
140572	140572	Coupe	Grifo Series II Can-Am		2	EU-ISORIVOLTA-GRIFO-CAN-AM-COUPE-01	HIGH	Series II隐藏式前灯及高发动机盖外廓。	READY
140573	140573	Coupe	Grifo Series II IR-8		2	EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	HIGH	IR-8外廓。	READY
140574	140574	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140575	140575	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140576	140576	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140577	140577	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140578	140578	Sedan	Fidia		4	EU-ISORIVOLTA-FIDIA-SEDAN-01	HIGH		READY
140579	140579	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140580	140580	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140581	140581	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140582	140582	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140583	140583	Coupe	Lele		3	EU-ISORIVOLTA-LELE-COUPE-01	HIGH		READY
140600_prefl	140600	SUV	XB7	G07	5	EU-ALPINA-XB7-G07-SUV-PREFL-01	MEDIUM	改款前物理外廓。	READY
140600_facelift	140600	SUV	XB7 facelift	G07	5	EU-ALPINA-XB7-G07-SUV-FACELIFT-01	MEDIUM	改款后物理外廓。	READY
140604	140604	Convertible	Huracán EVO		2	EU-LAMBORGHINI-HURACAN-EVO-RWD-SPYDER-01	HIGH	输入Targa对应EVO RWD Spyder开放式车身。	READY
140610	140610	Coupe	5300 GT Strada		2	EU-BIZZARRINI-5300-GT-STRADA-COUPE-01	HIGH		READY
140611	140611	Coupe	1900 GT Europa		2	EU-BIZZARRINI-1900-GT-EUROPA-COUPE-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_501-600_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MICROCAR-MGO6-HATCHBACK-01	2999	1500	1560	Engine in Detail Microcar M.Go 6 X Diesel Progress ACT	https://www.engineindetail.com/pa/microcar-m-go-6-x-diesel-progress-act-2019
EU-MERCEDES-BENZ-GLE-V167-SUV-01	4924	1947	1795	Auto-Data Mercedes-Benz GLE V167 GLE 350de	https://www.auto-data.net/en/mercedes-benz-gle-suv-v167-gle-350de-320hp-plug-in-hybrid-4matic-9g-tronic-37678
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-PREFL-01	4933	1852	1475	Auto-Data Mercedes-Benz E-Class T-Modell S213 E 300de	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-e-300de-306hp-plug-in-hybrid-9g-tronic-35179
EU-MERCEDES-BENZ-E-CLASS-S213-WAGON-FACELIFT-01	4945	1852	1476	Auto-Data Mercedes-Benz E-Class T-Modell S213 facelift E 300de	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s213-facelift-2020-e-300de-306hp-plug-in-hybrid-9g-tronic-40871
EU-MERCEDES-BENZ-C-CLASS-S205-FACELIFT-WAGON-01	4702	1810	1457	Auto-Data Mercedes-Benz C-Class S205 facelift C 300de	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s205-facelift-2018-c-300de-306hp-eq-power-9g-tronic-50968
EU-BMW-4-G22-COUPE-M440I-XDRIVE-01	4770	1852	1393	BMW Group Technical specifications – The new BMW 4 Series Coupé (M440i xDrive)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-HONDA-JAZZ-V-HATCHBACK-01	4044	1694	1526	Honda News Europe – 2020 Honda Jazz & Jazz Crosstar specifications	https://hondanews.eu/eu/el/cars/media/pressreleases/303367/2020-honda-jazz-and-jazz-crosstar-1
EU-BMW-4-G22-COUPE-01	4768	1852	1383	BMW Group Technical specifications – The new BMW 4 Series Coupé (420i/430i/420d)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-BMW-4-G22-COUPE-XDRIVE-01	4768	1852	1390	BMW Group Technical specifications – The new BMW 4 Series Coupé (420d xDrive)	https://www.press.bmwgroup.com/netherlands/article/attachment/T0309157NL/451837
EU-SEAT-LEON-IV-KL-HATCHBACK-01	4368	1799	1456	SEAT official Leon Style dimensions	https://www.seat.com/carworlds/leon/leon-style
EU-SEAT-LEON-IV-KL-WAGON-01	4642	1799	1450	SEAT official Leon Sportstourer Style dimensions	https://www.seat.com/carworlds/leon-sportstourer/style
EU-SKODA-SUPERB-III-FACELIFT-HATCHBACK-IV-01	4869	1864	1468	Skoda Superb iV official technical data	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-SKODA-SUPERB-III-FACELIFT-WAGON-IV-01	4862	1864	1477	Skoda Superb iV official technical data	https://cdn.skoda-storyboard.com/2019/09/TD-SUPERB-iV-en.pdf
EU-FERRARI-SF90-STRADALE-COUPE-01	4710	1972	1186	Ferrari SF90 Stradale official technical specifications	https://cdn.ferrari.com/cms/network/media/pdf/pr_ferrari_sf90_stradale_gbr.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-COMPACT-01	4895	1928	1910	Mercedes-Benz Vito Panel Van official brochure	https://www.kinahan.ie/custom/public/files/vito-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-LONG-01	5140	1928	1910	Mercedes-Benz Vito Panel Van official brochure	https://www.kinahan.ie/custom/public/files/vito-panel-ebrochure-2021-1-.pdf
EU-MERCEDES-BENZ-VITO-W447-FACELIFT-EXTRA-LONG-01	5370	1928	1910	Mercedes-Benz Vito Panel Van official brochure	https://www.kinahan.ie/custom/public/files/vito-panel-ebrochure-2021-1-.pdf
EU-VOLVO-S60-III-SEDAN-01	4761	1850	1437	Volvo Support – S60 2020 dimensions	https://www.volvocars.com/jp/support/car/s60/19w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V60-II-WAGON-01	4761	1850	1437	Volvo Support – V60 dimensions	https://www.volvocars.com/cy/support/car/v60/19w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-XC40-I-SUV-01	4425	1863	1658	Volvo Support – XC40 dimensions	https://www.volvocars.com/jp/support/car/xc40/18w17/article/b0804d54c7fc096bc0a81f6f065ad63e_0362eef4c7fc436fc0a81f6f7c27a289_0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-XC60-II-SUV-01	4688	1902	1658	Volvo Support – XC60 dimensions	https://www.volvocars.com/en-th/support/car/xc60/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-140-142-SEDAN-01	4640	1730	1440	Motorsporlari 1972 Volvo 142 Saloon technical specifications	https://eng.motorsporlari.net/car/tech_spec.asp?make=Volvo&specID=19748
EU-VOLVO-140-144-SEDAN-01	4640	1730	1440	ADAC Volvo 144 2.0 DL technical data	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/volvo/142-144-145/1generation-facelift-2/349620/
EU-VOLVO-PV444-SEDAN-01	4500	1570	1520	Volvotips Volvo PV444 and PV544 specifications	https://volvotips.com/pv/specifications/
EU-VOLVO-XC90-II-SUV-01	4950	1923	1776	Volvo Support – XC90 dimensions	https://www.volvocars.com/uk/support/car/xc90/18w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-DUETT-PV445-P210-WAGON-01	4400	1600	1700	Volvotips Volvo PV445 and P210 Duett specifications	https://volvotips.com/pv/specifications/
EU-FORD-PUMA-II-SUV-01	4186	1805	1550	Auto-Data Ford Puma 1.5 EcoBlue	https://www.auto-data.net/en/ford-puma-1.5-ecoblue-120hp-41778
EU-VOLVO-AMAZON-P120-SEDAN-01	4450	1620	1505	CarsGuide 1968 Volvo 122 dimensions	https://www.carsguide.com.au/volvo/122/car-dimensions/1968
EU-AUDI-A3-8Y-SEDAN-01	4495	1816	1425	Audi MediaCenter – A3 Sportback and A3 Sedan 2020 facts and figures	https://www.audi-mediacenter.com/en/more-dynamic-than-ever-before-the-new-audi-a3-sportback-and-the-new-a3-sedan-2020-12974/facts-and-figures-12977
EU-FORD-MONDEO-V-FACELIFT-HATCHBACK-01	4871	1852	1482	Auto-Data Ford Mondeo Hatchback facelift 2.0 EcoBlue	https://www.auto-data.net/en/ford-mondeo-iv-hatchback-facelift-2019-2.0-ecoblue-150hp-37284
EU-TOYOTA-HIACE-IV-H100-VAN-SWB-01	4570	1690	1940	Carsales / RedBook 1998 Toyota Hiace RZH103R specifications;GoAuto Toyota Hiace RZH103R SWB exterior dimensions	https://www.carsales.com.au/research/toyota/hiace/1998/no-badge/f973ea03-43ab-44b1-afcc-bbf9849c2235/;https://www.goauto.com.au/car-reviews/toyota/hiace/swb-van/2003-10-07/55860.html
EU-TOYOTA-HIACE-IV-H100-VAN-LWB-01	4830	1690	1930	Carsales / RedBook 1998 Toyota Hiace RZH113R specifications;GoAuto Toyota Hiace RZH113R LWB exterior dimensions	https://www.carsales.com.au/research/toyota/hiace/1998/no-badge/89389273-1a1d-4b60-a855-5565a27309c8/;https://www.goauto.com.au/car-reviews/toyota/hiace/lwb-van/2003-10-07/54510.html
EU-AUDI-A3-8Y-SPORTBACK-01	4343	1816	1449	Audi MediaCenter – A3 Sportback and A3 Sedan 2020 facts and figures	https://www.audi-mediacenter.com/en/more-dynamic-than-ever-before-the-new-audi-a3-sportback-and-the-new-a3-sedan-2020-12974/facts-and-figures-12977
EU-RENAULT-CAPTUR-I-FACELIFT-HATCHBACK-01	4122	1778	1556	Auto-Data Renault Captur facelift 2017 1.2 TCe	https://www.auto-data.net/en/renault-captur-facelift-2017-1.2-tce-120hp-start-stop-edc-29779
EU-FORD-FIESTA-VII-VAN-01	4040	1735	1476	Ford Fiesta Van official brochure	https://www.ford.ie/content/dam/guxeu/ie/Documents/Feature-PDFs/FT-NEW_FIESTA_VAN.pdf
EU-RENAULT-CAPTUR-II-HATCHBACK-01	4227	1797	1576	Auto-Data Renault Captur II E-TECH 1.6 specifications	https://www.auto-data.net/en/renault-captur-ii-e-tech-1.6-158hp-plug-in-hybrid-multimode-39733
EU-FORD-ECOSPORT-II-FACELIFT-SUV-01	4096	1765	1653	Automobile-Catalog Ford EcoSport facelift exterior dimensions	https://www.automobile-catalog.com/car/2018/2629325/ford_ecosport_1_5_tdci_100.html
EU-AUDI-A6-C8-WAGON-PREFL-01	4933	1886	1457	ADAC Audi A6 Avant 55 TFSI e sport quattro	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/audi/a6/c8/312163/
EU-SSANGYONG-TIVOLI-I-FACELIFT-SUV-01	4225	1810	1613	Auto-Data SsangYong Tivoli facelift 1.2 T-GDi	https://www.auto-data.net/en/ssangyong-tivoli-facelift-2019-1.2-t-gdi-128hp-42780
EU-AMC-MATADOR-I-WAGON-01	5207	1962	1430	Automobile-Catalog 1971 AMC Matador Wagon	https://www.automobile-catalog.com/car/1971/70205/amc_matador_wagon_v-8_360_automatic.html
EU-AMC-MATADOR-II-WAGON-01	5474	1961	1443	Automobile-Catalog 1974 AMC Matador Wagon	https://www.automobile-catalog.com/car/1974/71420/amc_matador_wagon_v-8_360-4_220_automatic.html
EU-AMC-HORNET-I-SEDAN-2D-01	4553	1805	1336	Automobile-Catalog 1970 AMC Hornet Sedan 199	https://www.automobile-catalog.com/car/1970/68045/amc_hornet_sedan_199.html
EU-AMC-HORNET-I-SEDAN-4D-01	4553	1805	1336	Automobile-Catalog 1970 AMC Hornet Sedan 199	https://www.automobile-catalog.com/car/1970/68045/amc_hornet_sedan_199.html
EU-ISO-ISETTA-COUPE-01	2250	1340	1320	Automobile-Catalog 1954 Iso Isetta	https://www.automobile-catalog.com/car/1954/1240970/isetta.html
EU-ISO-AUTOFURGONE-500-VAN-01	3470	1400	1650	Gazoline 308 – Iso utilitaires historical dimensions	https://fr.scribd.com/document/721289389/Gazoline-2023-03-fr-downmagaz-net
EU-ISO-AUTOCARRO-500-PICKUP-01	3470	1400	1360	Gazoline 308 – Iso utilitaires historical dimensions	https://fr.scribd.com/document/721289389/Gazoline-2023-03-fr-downmagaz-net
EU-ALPINA-D3-S-G20-SEDAN-PREFL-01	4719	1827	1440	Auto-Data Alpina D3 Sedan G20 S	https://www.auto-data.net/en/alpina-d3-sedan-g20-s-3.0-355hp-mild-hybrid-awd-switch-tronic-42604
EU-ALPINA-D3-S-G20-SEDAN-FACELIFT-01	4723	1827	1440	Auto-Data Alpina D3 Sedan G20 facelift S	https://www.auto-data.net/en/alpina-d3-sedan-g20-facelift-2022-s-3.0-355hp-mild-hybrid-awd-switch-tronic-45873
EU-ALPINA-D3-S-G21-WAGON-PREFL-01	4719	1827	1438	Auto-Data Alpina D3 Touring G21 S	https://www.auto-data.net/en/alpina-d3-touring-g21-s-3.0-355hp-mild-hybrid-awd-switch-tronic-42602
EU-ALPINA-D3-S-G21-WAGON-FACELIFT-01	4723	1827	1438	Auto-Data Alpina D3 Touring G21 facelift S	https://www.auto-data.net/en/alpina-d3-touring-g21-facelift-2022-s-3.0-355hp-mild-hybrid-awd-swtich-tronic-45874
EU-LIGIER-JS50-I-FACELIFT-HATCHBACK-01	2890	1500	1466	Ligier official JS50 external dimensions	https://www.ligier.lv/product/newjs50/
EU-AUDI-Q5-II-FY-SUV-01	4671	1893	1661	Auto-Data Audi Q5 II (FY) generation specifications	https://www.auto-data.net/en/audi-q5-ii-fy-generation-5191
EU-AUDI-Q5-II-FACELIFT-2020-SUV-FWD-01	4682	1893	1637	Audi Q5 35 TDI official technical data	https://prensa.audi.es/wp-content/uploads/2020/06/FT-Audi-Q51.pdf
EU-ISORIVOLTA-RIVOLTA-IR-COUPE-01	4760	1752	1425	Automobile-Catalog Iso Rivolta IR 300	https://www.automobile-catalog.com/car/1963/1250525/iso_rivolta_ir_300.html
EU-LIGIER-IXO-I-FACELIFT-HATCHBACK-01	3148	1524	1497	Auto-Data Ligier IXO 0.5 Progress	https://www.auto-data.net/en/ligier-ixo-0.5-progress-5hp-cvt-54700
EU-LIGIER-X-TOO-I-HATCHBACK-R-01	3035	1475	1498	Ligier X-Too R and S official owner manual	https://www.caen-sud.com/wp-content/uploads/2022/08/MANUEL-UTILISATION-ET-ENTRETIEN-XTOO-R-ET-S-PROGRESS.pdf
EU-LIGIER-X-TOO-I-HATCHBACK-S-01	2900	1475	1498	Ligier X-Too R and S official owner manual	https://www.caen-sud.com/wp-content/uploads/2022/08/MANUEL-UTILISATION-ET-ENTRETIEN-XTOO-R-ET-S-PROGRESS.pdf
EU-ISORIVOLTA-GRIFO-SERIES-I-COUPE-01	4430	1770	1200	Automobile-Catalog Iso Grifo L GL 350 Series I	https://www.automobile-catalog.com/car/1968/1250900/iso_grifo_l_gl_350.html
EU-ISORIVOLTA-GRIFO-SERIES-II-COUPE-01	4600	1770	1200	Automobile-Catalog Iso Grifo L 350 Series II	https://www.automobile-catalog.com/car/1972/1251170/iso_grifo_l_350.html
EU-CASALINI-M12-HATCHBACK-01	3010	1500	1500	Automoto.it Casalini M12 SF technical sheet	https://www.automoto.it/catalogo/casalini/m12/m12-sf/102201
EU-ISORIVOLTA-GRIFO-7-LITRI-COUPE-01	4430	1770	1220	Automobile-Catalog Iso Grifo 7 Litri	https://www.automobile-catalog.com/car/1969/1251050/iso_grifo_7_litri_2_32_axle_ratio.html
EU-ISORIVOLTA-GRIFO-CAN-AM-COUPE-01	4600	1770	1220	Automobile-Catalog Iso Grifo Can-Am	https://www.automobile-catalog.com/car/1971/1251350/iso_grifo_can-am.html
EU-ISORIVOLTA-GRIFO-IR8-COUPE-01	4600	1770	1200	Automobile-Catalog Iso Grifo IR-8	https://www.automobile-catalog.com/car/1974/1251470/iso_grifo_ir_8.html
EU-ISORIVOLTA-FIDIA-SEDAN-01	4970	1780	1320	Automobile-Catalog 1969 Iso Rivolta Fidia; Automobile-Catalog 1974 Iso Rivolta Fidia	https://www.automobile-catalog.com/make/iso_rivolta/fidia_s4/fidia/1969.html;https://www.automobile-catalog.com/make/iso_rivolta/fidia_s4/fidia/1974.html
EU-ISORIVOLTA-LELE-COUPE-01	4650	1750	1350	Automobile-Catalog 1972 Iso Rivolta Lele; Automobile-Catalog 1974 Iso Rivolta Lele IR 6	https://www.automobile-catalog.com/make/iso_rivolta/lele/lele/1972.html;https://www.automobile-catalog.com/car/1974/1251380/iso_rivolta_lele_ir_6.html
EU-ALPINA-XB7-G07-SUV-PREFL-01	5151	2000	1797	Auto-Data Alpina XB7	https://www.auto-data.net/en/alpina-xb7-4.4-v8-621hp-xdrive-switch-tronic-42582
EU-ALPINA-XB7-G07-SUV-FACELIFT-01	5178	2000	1797	Auto-Data Alpina XB7 facelift 2022	https://www.auto-data.net/en/alpina-xb7-facelift-2022-4.4-v8-621hp-mild-hybrid-xdrive-switch-tronic-45674
EU-LAMBORGHINI-HURACAN-EVO-RWD-SPYDER-01	4520	1933	1180	Automobile-Catalog Lamborghini Huracán EVO RWD Spyder	https://www.automobile-catalog.com/car/2020/2975555/lamborghini_huracan_evo_rwd_spyder.html
EU-BIZZARRINI-5300-GT-STRADA-COUPE-01	4370	1760	1110	Automobile-Catalog Bizzarrini GT Strada 5300	https://www.automobile-catalog.com/car/1966/261995/bizzarini_gt_strada_5300__gt_america_3_48_axle.html
EU-BIZZARRINI-1900-GT-EUROPA-COUPE-01	3790	1620	1040	Automobile-Catalog Bizzarrini GT Europa 1900	https://www.automobile-catalog.com/car/1966/261920/bizzarini_gt_europa_1900_3_73_axle.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_501-600_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://fr.scribd.com/document/721289389/Gazoline-2023-03-fr-downmagaz-net "https://fr.scribd.com/document/721289389/Gazoline-2023-03-fr-downmagaz-net"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（558 行）
- 累计尺寸组：dimension_groups_final.tsv（290 行）

