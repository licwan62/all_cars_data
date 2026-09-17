# 任务：all 第 6701-6800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0068__06f22aad


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6701-6800 行

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
all 第 6701-6800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6701-6800_ktype_dimension_mapping_final.tsv
- all_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-GIULIETTA-116-SEDAN-01	4210	1650	1400
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465
EU-CITROEN-BX-I-PHASE-I-BREAK-WAGON-5D-01	4399	1660	1431
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-01	4230	1660	1358
EU-CITROEN-BX-I-PHASE-I-HATCHBACK-5D-14-01	4230	1650	1358
EU-CITROEN-BX-I-PHASE-II-16V-HATCHBACK-5D-01	4237	1690	1350
EU-CITROEN-BX-I-PHASE-II-BREAK-LATE-WAGON-5D-01	4399	1682	1410
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-01	4237	1682	1360
EU-CITROEN-BX-I-PHASE-II-HATCHBACK-5D-4X4-01	4237	1682	1370
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4290	1740	1525
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534
EU-OPEL-KADETT-E-CARAVAN-01	4228	1666	1430
EU-OPEL-KADETT-E-CONVERTIBLE-16-01	3998	1663	1385
EU-OPEL-KADETT-E-CONVERTIBLE-20-01	3998	1663	1380
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400
EU-OPEL-KADETT-E-SEDAN-01	4218	1658	1400
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	4742	1772	1422
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	4742	1772	1425
EU-OPEL-OMEGA-A-CARAVAN-3L-PHASE-I-01	4730	1772	1530
EU-OPEL-OMEGA-A-CARAVAN-PHASE-I-01	4730	1772	1481
EU-OPEL-OMEGA-A-CARAVAN-PHASE-II-01	4768	1760	1530
EU-OPEL-OMEGA-A-SEDAN-01	4770	1810	1445
EU-OPEL-OMEGA-A-SEDAN-PHASE-I-01	4687	1772	1447
EU-OPEL-OMEGA-A-SEDAN-PHASE-II-01	4738	1760	1445
EU-OPEL-SENATOR-A-SEDAN-FACELIFT-01	4839	1722	1415
EU-OPEL-SENATOR-A-SEDAN-PREFL-01	4811	1728	1415
EU-OPEL-SENATOR-B-SEDAN-01	4845	1743	1450
EU-OPEL-VECTRA-A-CC-FACELIFT-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400
EU-RENAULT-LATITUDE-SEDAN-4D-01	4897	1832	1483
EU-SKODA-105-120-SEDAN-FACELIFT-01	4200	1610	1400
EU-SKODA-105-120-SEDAN-PREFL-01	4160	1595	1400
EU-SKODA-OCTAVIA-II-1Z-HATCHBACK-FACELIFT-01	4569	1769	1462
EU-SKODA-OCTAVIA-II-1Z-WAGON-4X4-FACELIFT-01	4569	1769	1468
EU-SKODA-OCTAVIA-II-1Z-WAGON-PREFL-01	4572	1769	1468
EU-SKODA-RAPID-743-COUPE-01	4200	1610	1380
EU-TALBOT-SIMCA-1301-SEDAN-4D-01	4457	1580	1400
EU-TALBOT-SIMCA-1301-WAGON-5D-01	4315	1580	1420

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Talbot	Simca 1301 tourisme	1.3 Spezial	Kombi	Heckantrieb	Benzin	51	69	Oct 1970	Jul 1972	2024-03-01	7135
Talbot	Simca 1301	1.3 Spezial	Stufenheck	Heckantrieb	Benzin	51	69	Oct 1970	Jul 1972	2024-03-01	7136
Talbot	Simca 1301	1.3 Spezial	Stufenheck	Heckantrieb	Benzin	49	67	Oct 1973	Nov 1976	2024-03-01	7137
Talbot	Simca 1301	1.3 Spezial	Stufenheck	Heckantrieb	Benzin	40	54	May 1974	Nov 1976	2024-03-01	7138
Talbot	Simca 1500	1.5	Stufenheck	Heckantrieb	Benzin	49	67	Oct 1963	Feb 1968	2024-03-01	7139
Talbot	Simca 1500 break	1.5	Kombi	Heckantrieb	Benzin	49	67	Nov 1964	Feb 1968	2024-03-01	7140
Citroën	Bx	19 4X4	Kombi	Allrad	Benzin	80	109	Oct 1990	May 1991	2024-03-01	7141
Talbot	Simca 1501	1.5	Stufenheck	Heckantrieb	Benzin	52	69	Oct 1966	Mar 1972	2024-03-01	7142
Renault	Latitude	3.0 DCI 240	Stufenheck	Frontantrieb	Diesel	177	241	Feb 2011	-	2024-03-01	7143
Talbot	Simca 1501	1.5 Autom.	Stufenheck	Heckantrieb	Benzin	53	72	Oct 1966	Mar 1972	2024-03-01	7144
Talbot	Simca 1501	1.5 Spezial	Stufenheck	Heckantrieb	Benzin	60	82	Oct 1970	May 1972	2024-03-01	7145
Talbot	Simca 1501	1.5 Spezial	Stufenheck	Heckantrieb	Benzin	52	71	Oct 1973	Nov 1976	2024-03-01	7146
Talbot	Simca 1501 break/tourisme	1.5	Kombi	Heckantrieb	Benzin	51	69	Oct 1966	Mar 1972	2024-03-01	7147
Talbot	Simca 1501 break/tourisme	1.5 Autom.	Kombi	Heckantrieb	Benzin	53	72	Oct 1966	Mar 1972	2024-03-01	7148
Talbot	Simca 1501 break/tourisme	1.5 Spezial	Kombi	Heckantrieb	Benzin	60	82	Oct 1970	May 1972	2024-03-01	7149
Talbot	Simca 1501 break/tourisme	1.5 Spezial	Kombi	Heckantrieb	Benzin	52	71	Oct 1973	Nov 1976	2024-03-01	7150
Volvo	V50	D4	Kombi	Frontantrieb	Diesel	130	177	Oct 2010	Dec 2012	2024-03-01	7151
Talbot	Simca 1609/1610	1609 1.6	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1976	Mar 1978	2024-03-01	7152
Talbot	Simca 1609/1610	1610 1.8	Stufenheck	Heckantrieb	Benzin	74	101	Sep 1976	Dec 1980	2024-03-01	7153
Talbot	Simca 1609/1610	1610 2.0	Stufenheck	Heckantrieb	Benzin	81	110	Sep 1976	Dec 1980	2024-03-01	7154
Volvo	V50	D3	Kombi	Frontantrieb	Diesel	110	150	Oct 2010	Dec 2012	2024-03-01	7155
Talbot	Simca 1609/1610	1610 2.0 D	Stufenheck	Heckantrieb	Diesel	44	60	Sep 1976	Dec 1980	2024-03-01	7156
Talbot	Matra bagheera	1.3	Coupe	Heckantrieb	Benzin	62	84	Jan 1974	Mar 1978	2024-03-01	7157
Dacia	Logan	1.6 16V Hi-flex	Kombi	Frontantrieb	Benzin/Ethanol	77	105	Nov 2009	-	2024-03-01	7158
Talbot	Matra bagheera	1.4	Coupe	Heckantrieb	Benzin	66	90	Dec 1975	Nov 1979	2024-03-01	7159
Talbot	Matra bagheera	1.4	Coupe	Heckantrieb	Benzin	62	84	Nov 1979	Sep 1980	2024-03-01	7160
Talbot	Matra bagheera	1.4	Coupe	Heckantrieb	Benzin	66	90	Nov 1979	Sep 1980	2024-03-01	7161
Talbot	Avenger	1.3	Stufenheck	Heckantrieb	Benzin	44	60	Feb 1970	Jul 1981	2024-03-01	7162
Talbot	Avenger	1.6	Stufenheck	Heckantrieb	Benzin	51	70	Feb 1970	Jul 1981	2024-03-01	7163
Talbot	Avenger	1.6	Stufenheck	Heckantrieb	Benzin	59	81	Feb 1970	Jul 1981	2024-03-01	7164
Talbot	Avenger	1.3	Kombi	Heckantrieb	Benzin	44	60	Apr 1972	Jul 1981	2024-03-01	7165
Talbot	Avenger	1.6	Kombi	Heckantrieb	Benzin	51	70	Apr 1972	Jul 1981	2024-03-01	7166
Opel	Kadett e cc	1.3 I CAT	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1985	Aug 1991	2024-03-01	7167
Opel	Kadett e cc	1.6 I CAT	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	7168
Opel	Kadett e cc	2.0 GSI CAT	Schrägheck	Frontantrieb	Benzin	85	115	Sep 1986	Aug 1991	2024-03-01	7169
Opel	Kadett e cc	2.0 GSI 16V CAT	Schrägheck	Frontantrieb	Benzin	110	150	Mar 1988	Aug 1991	2024-03-01	7170
Opel	Kadett e	1.3 I CAT	Stufenheck	Frontantrieb	Benzin	44	60	Sep 1985	Aug 1991	2024-03-01	7171
Opel	Kadett e	1.6 I CAT	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	7172
Opel	Kadett e	2.0 I CAT	Stufenheck	Frontantrieb	Benzin	85	115	Mar 1987	May 1992	2024-03-01	7173
Opel	Kadett e	1.6 I CAT	Cabriolet	Frontantrieb	Benzin	55	75	Oct 1987	Feb 1993	2024-03-01	7174
Opel	Kadett e	2.0 I CAT	Cabriolet	Frontantrieb	Benzin	85	116	Oct 1986	Feb 1993	2024-03-01	7175
Opel	Kadett e caravan	1.3 I CAT	Kombi	Frontantrieb	Benzin	44	60	Sep 1985	Aug 1991	2024-03-01	7176
Opel	Kadett e caravan	1.6 I CAT	Kombi	Frontantrieb	Benzin	55	75	Sep 1986	Aug 1991	2024-03-01	7177
Opel	Kadett e caravan	2.0 I CAT	Kombi	Frontantrieb	Benzin	85	115	Sep 1987	Aug 1991	2024-03-01	7178
Opel	Omega a	3	Stufenheck	Heckantrieb	Benzin	130	177	Mar 1988	Mar 1994	2024-03-01	7179
Opel	Senator	3.0 I CAT	Stufenheck	Heckantrieb	Benzin	130	177	Jan 1988	Sep 1993	2024-03-01	7180
Opel	Vectra a	1.8 S	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1989	Oct 1990	2024-03-01	7182
Opel	Vectra a	2.0 I CAT	Stufenheck	Frontantrieb	Benzin	85	116	Sep 1988	Nov 1995	2024-03-01	7183
Opel	Vectra a	2.0 I CAT 4X4	Stufenheck	Allrad	Benzin	85	116	Jan 1989	Nov 1995	2024-03-01	7184
Opel	Vectra a	2000/gt 16V CAT	Stufenheck	Frontantrieb	Benzin	110	150	Feb 1990	Nov 1995	2024-03-01	7185
Opel	Vectra a	2000/gt 16V CAT 4X4	Stufenheck	Allrad	Benzin	110	150	Feb 1990	Nov 1995	2024-03-01	7186
Opel	Vectra a cc	1.8 I	Schrägheck	Frontantrieb	Benzin	66	90	Sep 1988	Oct 1990	2024-03-01	7187
Opel	Vectra a cc	2.0 I CAT	Schrägheck	Frontantrieb	Benzin	85	116	Sep 1988	Nov 1995	2024-03-01	7188
Opel	Vectra a cc	2.0 I 16V CAT	Schrägheck	Frontantrieb	Benzin	110	150	Feb 1990	Nov 1995	2024-03-01	7189
Dacia	Logan	1.5 DCI	Kasten/Kombi	Frontantrieb	Diesel	55	75	May 2010	-	2024-03-01	7190
Dacia	Logan	1.5 DCI	Kasten/Kombi	Frontantrieb	Diesel	65	88	May 2010	-	2024-03-01	7191
Dacia	Logan	1.6 MPI 85	Kasten/Kombi	Frontantrieb	Benzin	62	84	May 2010	-	2024-03-01	7192
Dacia	Logan	1.6 MPI 85	Pick-up	Frontantrieb	Benzin	62	84	May 2010	-	2024-03-01	7193
Mitsubishi	L 300 / delica ii	2.3 D	Kasten	Heckantrieb	Diesel	50	68	Sep 1983	Oct 1986	2024-03-01	7194
Dacia	Logan	1.5 DCI	Pick-up	Frontantrieb	Diesel	55	75	May 2010	-	2024-03-01	7195
Dacia	Logan	1.5 DCI	Pick-up	Frontantrieb	Diesel	65	88	May 2010	-	2024-03-01	7196
Dacia	Sandero	1.4 MPI LPG	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	53	72	Jan 2009	Dec 2012	2025-12-01	7197
Talbot	Simca sunbeam	0.9	Schrägheck	Heckantrieb	Benzin	31	42	Jul 1977	Apr 1981	2024-03-01	7198
Alfa Romeo	Giulietta	2.0 Jtdm	Schrägheck	Frontantrieb	Diesel	120	163	Apr 2010	Oct 2018	2024-03-01	7199
Talbot	Simca sunbeam	1.3	Schrägheck	Heckantrieb	Benzin	40	54	Jul 1977	Apr 1981	2024-03-01	7200
Talbot	Simca sunbeam	1.3	Schrägheck	Heckantrieb	Benzin	44	60	Jul 1977	Apr 1981	2024-03-01	7201
Talbot	Simca sunbeam	1.6	Schrägheck	Heckantrieb	Benzin	51	70	Jul 1977	Apr 1981	2024-03-01	7202
Talbot	Simca sunbeam	1.6	Schrägheck	Heckantrieb	Benzin	59	80	Oct 1978	Apr 1981	2024-03-01	7203
Talbot	Simca sunbeam	1.6 TI	Schrägheck	Heckantrieb	Benzin	74	101	Oct 1978	Mar 1983	2024-03-01	7204
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	85	116	Apr 2010	Feb 2016	2024-03-01	7205
Alfa Romeo	Giulietta	1.4 TB	Schrägheck	Frontantrieb	Benzin	120	163	Apr 2010	Oct 2018	2024-03-01	7206
Talbot	Simca sunbeam	2.1 Lotus	Schrägheck	Heckantrieb	Benzin	114	155	Oct 1979	Mar 1982	2024-03-01	7207
Talbot	Simca sunbeam	2.1 Lotus	Schrägheck	Heckantrieb	Benzin	110	150	Oct 1979	Apr 1981	2024-03-01	7208
Talbot	160	1.6	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1976	Mar 1979	2024-03-01	7209
Talbot	180	1.8	Stufenheck	Heckantrieb	Benzin	74	101	Jan 1982	Dec 1982	2024-03-01	7210
Talbot	180	1.9 D	Stufenheck	Heckantrieb	Diesel	44	60	Jan 1978	Dec 1982	2024-03-01	7211
Fiat	Doblo cargo	1.6 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	66	90	Feb 2010	Dec 2023	2025-02-03	7213
Skoda	105,120	1.2 120 GLS	Stufenheck	Heckantrieb	Benzin	43	58	Feb 1983	Dec 1990	2024-03-01	7215
Skoda	Rapid	1.2	Coupe	Heckantrieb	Benzin	43	58	Feb 1983	Dec 1990	2024-03-01	7216
Skoda	Rapid	1.3	Coupe	Heckantrieb	Benzin	39	53	Aug 1987	Oct 1991	2024-03-01	7218
Skoda	1000mb	MB	Stufenheck	Heckantrieb	Benzin	27	37	Sep 1964	Jan 1970	2024-03-01	7219
Skoda	1000mb	MB	Stufenheck	Heckantrieb	Benzin	32	44	Mar 1966	Jan 1970	2024-03-01	7220
Toyota	Verso	1.33	Großraumlimousine	Frontantrieb	Benzin	73	99	Nov 2010	Oct 2016	2024-03-01	7221
Skoda	1000mb	MBX DE Luxe	Stufenheck	Heckantrieb	Benzin	34	46	Jan 1969	Jan 1970	2024-03-01	7222
Skoda	1100mb	MB	Stufenheck	Heckantrieb	Benzin	34	46	Jan 1969	Jan 1970	2024-03-01	7223
Skoda	Octavia	1.2 Super	Stufenheck	Heckantrieb	Benzin	33	45	Apr 1959	Feb 1961	2024-03-01	7224
Skoda	Octavia	1.2 Super	Stufenheck	Heckantrieb	Benzin	32	44	Feb 1961	Oct 1971	2024-03-01	7225
Skoda	110	1.1 L	Stufenheck	Heckantrieb	Benzin	33	45	Dec 1969	Mar 1982	2024-03-01	7226
Skoda	110	1.1 L	Stufenheck	Heckantrieb	Benzin	35	48	Dec 1969	Mar 1982	2024-03-01	7227
Skoda	110	1.1 LS	Stufenheck	Heckantrieb	Benzin	38	52	Jul 1970	Mar 1982	2024-03-01	7228
Skoda	110	1.1 R	Coupe	Heckantrieb	Benzin	38	52	Jul 1970	Mar 1982	2024-03-01	7229
Skoda	130	L,gl	Stufenheck	Heckantrieb	Benzin	45	61	Feb 1985	Oct 1991	2024-03-01	7230
Alfa Romeo	1750-2000	1750	Stufenheck	Heckantrieb	Benzin	83	113	Mar 1968	Oct 1972	2024-03-01	7231
Skoda	130	GL	Stufenheck	Heckantrieb	Benzin	39	53	Aug 1987	Oct 1991	2024-03-01	7232
Skoda	130	G,gl	Stufenheck	Heckantrieb	Benzin	46	63	Feb 1985	Oct 1991	2024-03-01	7233
Skoda	130	GL	Stufenheck	Heckantrieb	Benzin	43	58	Jan 1987	Oct 1991	2024-03-01	7234
Toyota	Verso	1.4 D4-d	Großraumlimousine	Frontantrieb	Diesel	66	90	Nov 2010	Oct 2016	2024-03-01	7235
Alfa Romeo	Montreal	2.6	Coupe	Heckantrieb	Benzin	143	194	Dec 1972	Mar 1979	2024-03-01	7236
Skoda	Octavia	1.1	Stufenheck	Heckantrieb	Benzin	29	39	Apr 1959	Feb 1962	2024-03-01	7237
Opel	Antara a	2.4	SUV	Frontantrieb	Benzin	123	167	Dec 2010	Feb 2015	2024-03-01	7238


--- Round 1 / 首次发送 ---
## 更新点

* 已优先闭合可直接命中跨批次尺寸组索引的车型。
* 本轮完成 **36 个输入 Ktype、41 条 READY 映射行**。
* Kadett E CC 按三门/五门拆分；Omega A 3.0 按改款前后拆分。
* 本轮全部复用既有尺寸组，未重复抓取或新建尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：36
* 待处理 Ktype：64
* READY 映射行：41
* PENDING Ktype：64
* 当前已引用尺寸组：22
* 本轮新建/修正尺寸组：0
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7135	7135	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH	1301 tourisme五门旅行车。	READY
7136	7136	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7137	7137	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7138	7138	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7143	7143	Sedan	Latitude I		4	EU-RENAULT-LATITUDE-SEDAN-4D-01	HIGH		READY
7158	7158	Wagon	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	MCV五门旅行车外廓。	READY
7167_3dr	7167	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	MEDIUM	输入未区分门数，拆分三门物理分支。	READY
7167_5dr	7167	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	MEDIUM	输入未区分门数，拆分五门物理分支。	READY
7168_3dr	7168	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	MEDIUM	输入未区分门数，拆分三门物理分支。	READY
7168_5dr	7168	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	MEDIUM	输入未区分门数，拆分五门物理分支。	READY
7169_3dr	7169	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	MEDIUM	GSi输入未区分门数，拆分三门物理分支。	READY
7169_5dr	7169	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSi输入未区分门数，拆分五门物理分支。	READY
7170_3dr	7170	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	MEDIUM	GSi输入未区分门数，拆分三门物理分支。	READY
7170_5dr	7170	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSi输入未区分门数，拆分五门物理分支。	READY
7171	7171	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7172	7172	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7173	7173	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7174	7174	Convertible	Kadett E		2	EU-OPEL-KADETT-E-CONVERTIBLE-16-01	HIGH	1.6敞篷外廓。	READY
7175	7175	Convertible	Kadett E		2	EU-OPEL-KADETT-E-CONVERTIBLE-20-01	HIGH	2.0敞篷外廓。	READY
7176	7176	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7177	7177	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7178	7178	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7179_prefl	7179	Sedan	Omega A		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	MEDIUM	生产区间跨越外廓变化，拆分改款前分支。	READY
7179_facelift	7179	Sedan	Omega A		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	MEDIUM	生产区间跨越外廓变化，拆分改款后分支。	READY
7180	7180	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
7182	7182	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7183	7183	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7184	7184	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7187	7187	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7188	7188	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7189	7189	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7193	7193	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7195	7195	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7196	7196	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7197	7197	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH		READY
7199	7199	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7205	7205	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7206	7206	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7215	7215	Sedan	Škoda 105/120 facelift		4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7216	7216	Coupe	Škoda Rapid 743	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH		READY
7218	7218	Coupe	Škoda Rapid 743	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

无

## 下一步优先处理

1. 集中闭合 Talbot/Simca 1500、1501、1609/1610，并确认轿车与旅行车外廓边界。
2. 处理 Matra Bagheera、Avenger、Simca Sunbeam、Talbot 160/180。
3. 闭合 Volvo V50、Toyota Verso、Fiat Doblò Cargo、Mitsubishi L300 等现代或商用车型。
4. 处理 Škoda 1000 MB、110、130、早期 Octavia，以及 Alfa Romeo 1750/2000、Montreal。
5. 单独核对 Citroën BX 19 4X4 Break、Logan Kasten/Kombi、Vectra 2000/GT 和 Antara A。

推进信号：CONTINUE


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6701-6800_ktype_dimension_mapping_final.tsv
- all_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Citroën BX 19 4X4 Break，并复用既有 Phase II Break 尺寸组；其三维与缓存组一致。([车谱][1])
* 首次创建 Volvo V50 facelift 尺寸组；官方手册明确区分车身宽度与含后视镜宽度。
* Matra Bagheera 按 Series I 与 Series II 外廓变化拆成两个尺寸组，并拆分跨改款生产区间的 Ktype。([汽车目录][2])
* 输入中的 Toyota Verso 1.33、1.4 D-4D 按发动机与生产期归入 Verso-S II；两种动力对应相同外廓。([汽车数据][3])
* 首次闭合 Alfa Romeo 1750 Berlina、Montreal 和 Opel Antara A facelift 尺寸组。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：48
* 待处理 Ktype：52
* READY 映射行：55
* PENDING Ktype：52
* 当前已引用尺寸组：30
* 本轮新建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7141	7141	Wagon	BX I Phase II Break		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH	19 4X4 Break五门旅行车外廓。	READY
7151	7151	Wagon	V50 I facelift	M	5	EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	HIGH		READY
7155	7155	Wagon	V50 I facelift	M	5	EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	HIGH		READY
7157_prefl	7157	Coupe	Bagheera Series I		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款前分支。	READY
7157_facelift	7157	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款后分支。	READY
7159_prefl	7159	Coupe	Bagheera Series I		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款前分支。	READY
7159_facelift	7159	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款后分支。	READY
7160	7160	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	HIGH		READY
7161	7161	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	HIGH		READY
7221	7221	MPV	Verso-S II		5	EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	MEDIUM	1.33动力和生产期对应Verso-S II物理边界。	READY
7231	7231	Sedan	1750 Berlina		4	EU-ALFA-ROMEO-1750-BERLINA-SEDAN-4D-01	HIGH		READY
7235	7235	MPV	Verso-S II		5	EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	MEDIUM	1.4 D-4D动力和生产期对应Verso-S II物理边界。	READY
7236	7236	Coupe	Montreal	105.64	2	EU-ALFA-ROMEO-MONTREAL-10564-COUPE-2D-01	HIGH		READY
7238	7238	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	4522	1770	1457	Volvo V50 Owner's Manual MY10	https://ldgsvccassets.blob.core.windows.net/pdfs/18939bdb9d7f579ebf9812040b32cd622be31e4c/V50_owners_manual_MY10_EN_tp10852.pdf
EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	3974	1734	1175	Automobile-Catalog 1974 Matra-Simca Bagheera	https://www.automobile-catalog.com/car/1974/1458455/matra_simca_bagheera.html
EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	4010	1737	1220	Automobile-Catalog 1977 Matra-Simca Bagheera	https://www.automobile-catalog.com/car/1977/1458485/matra_simca_bagheera.html
EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	3990	1695	1595	Auto-Data Toyota Verso-S II 1.33; Auto-Data Toyota Verso-S II 1.4 D-4D	https://www.auto-data.net/en/toyota-verso-s-ii-1.33-dual-vvt-i-98hp-18486; https://www.auto-data.net/en/toyota-verso-s-ii-1.4-d-4d-dpf-89hp-18488
EU-ALFA-ROMEO-1750-BERLINA-SEDAN-4D-01	4390	1565	1430	Automobile-Catalog 1969 Alfa Romeo 1750 Berlina	https://www.automobile-catalog.com/car/1969/65150/alfa_romeo_1750_berlina.html
EU-ALFA-ROMEO-MONTREAL-10564-COUPE-2D-01	4220	1672	1205	Automobile-Catalog 1973 Alfa Romeo Montreal	https://www.automobile-catalog.com/car/1973/24395/alfa_romeo_montreal.html
EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	4596	1850	1717	Auto-Data Opel Antara facelift 2010 2.4	https://www.auto-data.net/en/opel-antara-facelift-2010-2.4-167hp-16948
```

## 下一步优先处理

1. 闭合 Simca 1500、1501 各生产阶段的高度变化及旅行车边界。
2. 集中处理 Simca 1609/1610、Talbot 160/180，确认后期西班牙生产车型是否共用同一外廓。
3. 处理 Avenger、Simca Sunbeam及 Lotus 宽体差异。
4. 闭合 Škoda 1000 MB、1100 MB、110/130、早期 Octavia 和 Rapid 系列。
5. 处理 Logan Kasten/Kombi、Mitsubishi L300、Fiat Doblò Cargo 等多车身商用车型。

推进信号：CONTINUE

[1]: https://www.carfolio.com/citroen-bx-19-4wd-break-542399?utm_source=chatgpt.com "1990 Citroën BX 19 4WD Break"
[2]: https://www.automobile-catalog.com/car/1974/1458455/matra_simca_bagheera.html?utm_source=chatgpt.com "1974 Matra Simca Bagheera Specs Review (62 kW / 84 PS ..."
[3]: https://www.auto-data.net/en/toyota-verso-s-ii-1.33-dual-vvt-i-98hp-18486?utm_source=chatgpt.com "Toyota Verso-S II 1.33 Dual VVT-i (98 Hp) /MPV 2010 - 2015"
[4]: https://www.automobile-catalog.com/car/1969/65150/alfa_romeo_1750_berlina.html?utm_source=chatgpt.com "1969 Alfa Romeo 1750 Berlina Specs Review (83 kW ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6701-6800_ktype_dimension_mapping_final.tsv
- all_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Simca 1500/1501 共 10 个 Ktype；1501 轿车及旅行车复用既有 1301/1501 共用外廓组，Simca 1500 首次创建轿车、旅行车尺寸组。([汽车目录][1])
* 闭合 Škoda 1000 MB、1100 MB、MBX、早期 Octavia、100/110、110 R 和 130 系列共 15 个 Ktype；首次创建 5 个尺寸组。([汽车目录][2])
* 闭合普通版 Simca Sunbeam 共 6 个 Ktype，并首次创建三门掀背尺寸组；Lotus 版本继续单独核对。([车谱][3])
* 闭合 Logan Kasten/Kombi 共 3 个 Ktype，复用现有 Logan I MCV facelift 物理外廓组。
* 本轮新增 READY Ktype：34；首次创建尺寸组：8。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：82
* 待处理 Ktype：18
* READY 映射行：89
* PENDING Ktype：18
* 当前已引用尺寸组：38
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7139	7139	Sedan	Simca 1300/1500		4	EU-TALBOT-SIMCA-1500-SEDAN-4D-01	HIGH		READY
7140	7140	Wagon	Simca 1300/1500		5	EU-TALBOT-SIMCA-1500-BREAK-WAGON-5D-01	HIGH		READY
7142	7142	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7144	7144	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7145	7145	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7146	7146	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7147	7147	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7148	7148	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7149	7149	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7150	7150	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7190	7190	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7191	7191	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7192	7192	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7198	7198	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7200	7200	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7201	7201	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7202	7202	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7203	7203	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7204	7204	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	MEDIUM	Ktype结束日期晚于整车生产期，物理车身仍为普通三门Sunbeam。	READY
7219	7219	Sedan	1000 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7220	7220	Sedan	1000 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7222	7222	Coupe	1000 MBX		2	EU-SKODA-1000-MBX-COUPE-2D-01	HIGH	MBX为两门无B柱轿跑，纠正输入Stufenheck。	READY
7223	7223	Sedan	1100 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7224	7224	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	HIGH		READY
7225	7225	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	MEDIUM	输入结束日期覆盖旅行车延续期，按Stufenheck两门轿车边界映射。	READY
7226	7226	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7227	7227	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7228	7228	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7229	7229	Coupe	Škoda 110 R		2	EU-SKODA-110R-COUPE-2D-01	HIGH		READY
7230	7230	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7232	7232	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7233	7233	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7234	7234	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7237	7237	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TALBOT-SIMCA-1500-SEDAN-4D-01	4253	1580	1400	Automobile-Catalog 1966 Simca 1500 GL	https://www.automobile-catalog.com/car/1966/3107735/simca_1500_gl.html
EU-TALBOT-SIMCA-1500-BREAK-WAGON-5D-01	4246	1580	1410	Automobile-Catalog 1965 Simca 1500 Tourisme LS	https://www.automobile-catalog.com/car/1965/3107765/simca_1500_tourisme_ls.html
EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	3828	1603	1394	Carfolio 1980 Talbot Sunbeam 1.0 LS	https://www.carfolio.com/talbot-sunbeam-1.0-ls-54417
EU-SKODA-1000-1100-MB-SEDAN-4D-01	4170	1620	1390	Automobile-Catalog 1968 Skoda 1000 MB	https://www.automobile-catalog.com/car/1968/3130655/skoda_1000_mb.html
EU-SKODA-1000-MBX-COUPE-2D-01	4170	1620	1390	Carfolio 1966 Skoda 1000 MBX	https://www.carfolio.com/skoda-1000-mbx-500808
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430	Automobile-Catalog 1959 Skoda Octavia	https://www.automobile-catalog.com/car/1959/3130460/skoda_octavia.html
EU-SKODA-100-110-SEDAN-4D-01	4155	1620	1380	Automobile-Catalog 1970 Skoda 110 L	https://www.automobile-catalog.com/car/1970/3131045/skoda_110_l.html
EU-SKODA-110R-COUPE-2D-01	4155	1620	1340	Škoda Storyboard 50 Years of the 110 R	https://www.skoda-storyboard.com/en/press-releases/50-years-of-the-110-r-half-a-century-ago-skoda-presented-its-legendary-sports-coupe/
```

## 下一步优先处理

1. 闭合 Chrysler-Simca 1609/1610 与 Talbot 160/180，重点区分汽油车型和西班牙柴油车型高度。
2. 按改款前后拆分 Talbot Avenger 轿车与旅行车。
3. 单独核对 Sunbeam Lotus 的外部套件尺寸，避免直接复用普通 Sunbeam 组。
4. 闭合 Vectra A 2000/GT、Mitsubishi L300 和 Fiat Doblò Cargo 的特殊车身分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1966/3107735/simca_1500_gl.html?utm_source=chatgpt.com "1966 Simca 1500 GL Specs Review (48.5 kW / 66 PS ..."
[2]: https://www.automobile-catalog.com/car/1968/3130655/skoda_1000_mb.html?utm_source=chatgpt.com "1968 Skoda 1000 MB Specs Review (31.6 kW / 43 PS / 42 ..."
[3]: https://www.carfolio.com/talbot-sunbeam-1.0-ls-54417?utm_source=chatgpt.com "1980 Talbot Sunbeam 1.0 LS"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6701-6800_ktype_dimension_mapping_final.tsv
- all_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 Chrysler-Simca 1609/1610、Talbot 160/180 共 7 个 Ktype，统一关联同一四门轿车尺寸组。([汽车目录][1])
* Talbot Avenger 按 1976 年外观改款拆分轿车与旅行车的改款前、改款后四个尺寸组，共闭合 5 个 Ktype、10 条派生映射。([汽车目录档案][2])
* Vectra A 2000/GT 使用独立运动版尺寸组，前驱与四驱共用同一外廓。([汽车目录][3])
* Sunbeam Lotus 使用独立尺寸组，不复用普通 Sunbeam 组。([车谱][4])
* Mitsubishi L300 Kasten 与 Fiat Doblò Cargo 仍需闭合标准轴距、长轴和车顶分支边界。

## 当前批次进度

* 输入 Ktype：100
* 已闭合 Ktype：98
* 待处理 Ktype：2
* READY 映射行：110
* PENDING Ktype：2
* 当前已引用尺寸组：45
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7152	7152	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7153	7153	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7154	7154	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7156	7156	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH	柴油动力不改变四门车身外廓。	READY
7162_prefl	7162	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7162_facelift	7162	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7163_prefl	7163	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7163_facelift	7163	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7164_prefl	7164	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7164_facelift	7164	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7165_prefl	7165	Wagon	Avenger pre-facelift		5	EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前旅行车分支。	READY
7165_facelift	7165	Wagon	Avenger facelift		5	EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后旅行车分支。	READY
7166_prefl	7166	Wagon	Avenger pre-facelift		5	EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前旅行车分支。	READY
7166_facelift	7166	Wagon	Avenger facelift		5	EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后旅行车分支。	READY
7185	7185	Sedan	Vectra A 2000		4	EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	HIGH	2000/GT运动版外廓。	READY
7186	7186	Sedan	Vectra A 2000		4	EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	HIGH	四驱系统不改变2000/GT四门外廓。	READY
7207	7207	Hatchback	Talbot Sunbeam Lotus		3	EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	HIGH	Lotus道路版三门物理外廓。	READY
7208	7208	Hatchback	Talbot Sunbeam Lotus		3	EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	HIGH	Lotus道路版三门物理外廓。	READY
7209	7209	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7210	7210	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	MEDIUM	后期Talbot 180四门外廓。	READY
7211	7211	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	MEDIUM	柴油动力不改变后期Talbot 180四门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	4527	1728	1440	Automobile-Catalog 1976 Chrysler-Simca 1609; Automobile-Catalog 1978 Chrysler France 1609-1610 full range	https://www.automobile-catalog.com/car/1976/531650/chrysler_1609_automatic.html; https://www.automobile-catalog.com/make/chrysler_france/1609-2_l/1609-2_l/1978.html
EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	4102	1588	1422	Carfolio 1970 Hillman Avenger 1250	https://www.carfolio.com/hillman-avenger-1250-59983
EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	4144	1615	1408	Chrysler Avenger 1978 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2024/02/Chrysler-Avenger-1978-UK.pdf
EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	4204	1588	1422	Automobile-Catalog 1973 Hillman Avenger Estate 1500 De Luxe	https://www.automobile-catalog.com/car/1973/1028255/hillman_avenger_estate_1500_de_luxe.html
EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	4250	1615	1415	Talbot Avenger 1980 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/05/Talbot-Avenger-1980-UK.pdf
EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	4430	1700	1400	Automobile-Catalog 1990 Opel Vectra 2000 16V	https://www.automobile-catalog.com/car/1990/2472680/opel_vectra_2000_16v.html
EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	3830	1603	1405	Carfolio 1979 Talbot Sunbeam-Lotus	https://www.carfolio.com/talbot-sunbeam-lotus-30338
```

## 下一步优先处理

1. 确认 Ktype `7194` 对应的 L300/Delica II Kasten 是否仅覆盖标准轴距低顶，或需拆分长轴、高顶分支。
2. 确认 Ktype `7213` 的 Doblò Cargo 是否同时覆盖短轴、Maxi 和高顶车身；闭合后立即进入最终机械检查并输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1976/531650/chrysler_1609_automatic.html?utm_source=chatgpt.com "1976 Chrysler-Simca 1609 automatic (aut. 3)"
[2]: https://autocatalogarchive.com/wp-content/uploads/2024/02/Chrysler-Avenger-1978-UK.pdf?utm_source=chatgpt.com "Chrysler Avenger (1976-1981) UK"
[3]: https://www.automobile-catalog.com/car/1990/2472680/opel_vectra_2000_16v.html?utm_source=chatgpt.com "1990 Opel Vectra 2000 16V (man. 5) (model up to mid-year ..."
[4]: https://www.carfolio.com/talbot-sunbeam-lotus-30338?utm_source=chatgpt.com "1979 Talbot Sunbeam-Lotus"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6701-6800_ktype_dimension_mapping_final.tsv
- all_6701-6800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* Ktype `7194` 已按 `L038P` 标准轴距与 `L068P` 长轴高顶拆为两个物理分支。([电子商店][1])
* Ktype `7213` 已按改款前后、标准轴距/Maxi 长轴及改款前高顶拆为五个物理分支。([Stellantis Media][2])
* 最终机械检查通过：表头固定、117 个 `id` 唯一、52 个尺寸组唯一、全部映射引用闭合，三维与来源字段无空缺。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：117
* PENDING：0
* DIMENSION_GROUP：52
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
7135	7135	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH	1301 tourisme五门旅行车。	READY
7136	7136	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7137	7137	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7138	7138	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH	1301四门轿车。	READY
7139	7139	Sedan	Simca 1300/1500		4	EU-TALBOT-SIMCA-1500-SEDAN-4D-01	HIGH		READY
7140	7140	Wagon	Simca 1300/1500		5	EU-TALBOT-SIMCA-1500-BREAK-WAGON-5D-01	HIGH		READY
7141	7141	Wagon	BX I Phase II Break		5	EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	HIGH	19 4X4 Break五门旅行车外廓。	READY
7142	7142	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7143	7143	Sedan	Latitude I		4	EU-RENAULT-LATITUDE-SEDAN-4D-01	HIGH		READY
7144	7144	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7145	7145	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7146	7146	Sedan	Simca 1301/1501		4	EU-TALBOT-SIMCA-1301-SEDAN-4D-01	HIGH		READY
7147	7147	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7148	7148	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7149	7149	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7150	7150	Wagon	Simca 1301/1501		5	EU-TALBOT-SIMCA-1301-WAGON-5D-01	HIGH		READY
7151	7151	Wagon	V50 I facelift	M	5	EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	HIGH		READY
7152	7152	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7153	7153	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7154	7154	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7155	7155	Wagon	V50 I facelift	M	5	EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	HIGH		READY
7156	7156	Sedan	Chrysler-Simca 1609/1610		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH	柴油动力不改变四门车身外廓。	READY
7157_prefl	7157	Coupe	Bagheera Series I		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款前分支。	READY
7157_facelift	7157	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款后分支。	READY
7158	7158	Wagon	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	HIGH	MCV五门旅行车外廓。	READY
7159_prefl	7159	Coupe	Bagheera Series I		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款前分支。	READY
7159_facelift	7159	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	MEDIUM	生产区间跨越Series I/II外廓，拆分改款后分支。	READY
7160	7160	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	HIGH		READY
7161	7161	Coupe	Bagheera Series II		3	EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	HIGH		READY
7162_prefl	7162	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7162_facelift	7162	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7163_prefl	7163	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7163_facelift	7163	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7164_prefl	7164	Sedan	Avenger pre-facelift		4	EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前分支。	READY
7164_facelift	7164	Sedan	Avenger facelift		4	EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后分支。	READY
7165_prefl	7165	Wagon	Avenger pre-facelift		5	EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前旅行车分支。	READY
7165_facelift	7165	Wagon	Avenger facelift		5	EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后旅行车分支。	READY
7166_prefl	7166	Wagon	Avenger pre-facelift		5	EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款前旅行车分支。	READY
7166_facelift	7166	Wagon	Avenger facelift		5	EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	MEDIUM	生产区间跨越1976年外观改款，拆分改款后旅行车分支。	READY
7167_3dr	7167	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	MEDIUM	输入未区分门数，拆分三门物理分支。	READY
7167_5dr	7167	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	MEDIUM	输入未区分门数，拆分五门物理分支。	READY
7168_3dr	7168	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-HATCHBACK-3D-01	MEDIUM	输入未区分门数，拆分三门物理分支。	READY
7168_5dr	7168	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-HATCHBACK-5D-01	MEDIUM	输入未区分门数，拆分五门物理分支。	READY
7169_3dr	7169	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	MEDIUM	GSi输入未区分门数，拆分三门物理分支。	READY
7169_5dr	7169	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSi输入未区分门数，拆分五门物理分支。	READY
7170_3dr	7170	Hatchback	Kadett E		3	EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	MEDIUM	GSi输入未区分门数，拆分三门物理分支。	READY
7170_5dr	7170	Hatchback	Kadett E		5	EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	MEDIUM	GSi输入未区分门数，拆分五门物理分支。	READY
7171	7171	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7172	7172	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7173	7173	Sedan	Kadett E		4	EU-OPEL-KADETT-E-SEDAN-4D-01	HIGH		READY
7174	7174	Convertible	Kadett E		2	EU-OPEL-KADETT-E-CONVERTIBLE-16-01	HIGH	1.6敞篷外廓。	READY
7175	7175	Convertible	Kadett E		2	EU-OPEL-KADETT-E-CONVERTIBLE-20-01	HIGH	2.0敞篷外廓。	READY
7176	7176	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7177	7177	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7178	7178	Wagon	Kadett E		5	EU-OPEL-KADETT-E-CARAVAN-01	HIGH		READY
7179_prefl	7179	Sedan	Omega A		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	MEDIUM	生产区间跨越外廓变化，拆分改款前分支。	READY
7179_facelift	7179	Sedan	Omega A		4	EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	MEDIUM	生产区间跨越外廓变化，拆分改款后分支。	READY
7180	7180	Sedan	Senator B		4	EU-OPEL-SENATOR-B-SEDAN-01	HIGH		READY
7182	7182	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7183	7183	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7184	7184	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
7185	7185	Sedan	Vectra A 2000		4	EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	HIGH	2000/GT运动版外廓。	READY
7186	7186	Sedan	Vectra A 2000		4	EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	HIGH	四驱系统不改变2000/GT四门外廓。	READY
7187	7187	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7188	7188	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7189	7189	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
7190	7190	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7191	7191	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7192	7192	Van	Logan I facelift		5	EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	MEDIUM	Kasten/Kombi按Logan Van五门物理外廓。	READY
7193	7193	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7194_swb	7194	Van	L300 / Delica II (L03)	L038P	4	EU-MITSUBISHI-L300-DELICA-II-L03-VAN-SWB-01	MEDIUM	Ktype同时覆盖L038P与L068P，拆分标准轴距车身。	READY
7194_lwb_highroof	7194	Van	L300 / Delica II (L03)	L068P	4	EU-MITSUBISHI-L300-DELICA-II-L03-VAN-LWB-HIGHROOF-01	MEDIUM	Ktype同时覆盖L038P与L068P，拆分长轴高顶车身。	READY
7195	7195	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7196	7196	Pickup	Logan I facelift		2	EU-DACIA-LOGAN-I-PICKUP-01	HIGH		READY
7197	7197	Hatchback	Sandero I		5	EU-DACIA-SANDERO-I-HATCHBACK-5D-01	HIGH		READY
7198	7198	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7199	7199	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7200	7200	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7201	7201	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7202	7202	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7203	7203	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	HIGH		READY
7204	7204	Hatchback	Chrysler/Talbot Sunbeam		3	EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	MEDIUM	Ktype结束日期晚于整车生产期，物理车身仍为普通三门Sunbeam。	READY
7205	7205	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7206	7206	Hatchback	Giulietta 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
7207	7207	Hatchback	Talbot Sunbeam Lotus		3	EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	HIGH	Lotus道路版三门物理外廓。	READY
7208	7208	Hatchback	Talbot Sunbeam Lotus		3	EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	HIGH	Lotus道路版三门物理外廓。	READY
7209	7209	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	HIGH		READY
7210	7210	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	MEDIUM	后期Talbot 180四门外廓。	READY
7211	7211	Sedan	Chrysler-Simca 160/180		4	EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	MEDIUM	柴油动力不改变后期Talbot 180四门外廓。	READY
7213_swb_lowroof_prefl	7213	Van	Doblò Cargo II pre-facelift	263		EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-LOWROOF-PREFL-01	MEDIUM	生产区间覆盖改款前标准轴距普通顶车身。	READY
7213_swb_highroof_prefl	7213	Van	Doblò Cargo II pre-facelift	263		EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-HIGHROOF-PREFL-01	MEDIUM	生产区间覆盖改款前标准轴距高顶车身。	READY
7213_lwb_prefl	7213	Van	Doblò Cargo II pre-facelift	263		EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-PREFL-01	MEDIUM	生产区间覆盖改款前Maxi长轴车身。	READY
7213_swb_facelift	7213	Van	Doblò Cargo II facelift	263		EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-FACELIFT-01	MEDIUM	生产区间覆盖改款后标准轴距车身。	READY
7213_lwb_facelift	7213	Van	Doblò Cargo II facelift	263		EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-FACELIFT-01	MEDIUM	生产区间覆盖改款后Maxi长轴车身。	READY
7215	7215	Sedan	Škoda 105/120 facelift		4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7216	7216	Coupe	Škoda Rapid 743	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH		READY
7218	7218	Coupe	Škoda Rapid 743	743	2	EU-SKODA-RAPID-743-COUPE-01	HIGH		READY
7219	7219	Sedan	1000 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7220	7220	Sedan	1000 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7221	7221	MPV	Verso-S II		5	EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	MEDIUM	1.33动力和生产期对应Verso-S II物理边界。	READY
7222	7222	Coupe	1000 MBX		2	EU-SKODA-1000-MBX-COUPE-2D-01	HIGH	MBX为两门无B柱轿跑，纠正输入Stufenheck。	READY
7223	7223	Sedan	1100 MB		4	EU-SKODA-1000-1100-MB-SEDAN-4D-01	HIGH		READY
7224	7224	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	HIGH		READY
7225	7225	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	MEDIUM	输入结束日期覆盖旅行车延续期，按Stufenheck两门轿车边界映射。	READY
7226	7226	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7227	7227	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7228	7228	Sedan	Škoda 100/110		4	EU-SKODA-100-110-SEDAN-4D-01	HIGH		READY
7229	7229	Coupe	Škoda 110 R		2	EU-SKODA-110R-COUPE-2D-01	HIGH		READY
7230	7230	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7231	7231	Sedan	1750 Berlina		4	EU-ALFA-ROMEO-1750-BERLINA-SEDAN-4D-01	HIGH		READY
7232	7232	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7233	7233	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7234	7234	Sedan	Škoda 105/120/130 facelift	742	4	EU-SKODA-105-120-SEDAN-FACELIFT-01	HIGH		READY
7235	7235	MPV	Verso-S II		5	EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	MEDIUM	1.4 D-4D动力和生产期对应Verso-S II物理边界。	READY
7236	7236	Coupe	Montreal	105.64	2	EU-ALFA-ROMEO-MONTREAL-10564-COUPE-2D-01	HIGH		READY
7237	7237	Sedan	Octavia (1959)		2	EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	HIGH		READY
7238	7238	SUV	Antara A facelift		5	EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6701-6800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TALBOT-SIMCA-1301-WAGON-5D-01	4315	1580	1420	Automobile-Catalog 1973 Simca 1301 Break Special	https://www.automobile-catalog.com/car/1973/3108665/simca_1301_break_special.html
EU-TALBOT-SIMCA-1301-SEDAN-4D-01	4457	1580	1400	Automobile-Catalog 1973 Simca 1301 Special	https://www.automobile-catalog.com/car/1973/3108770/simca_1301_special.html
EU-TALBOT-SIMCA-1500-SEDAN-4D-01	4253	1580	1400	Automobile-Catalog 1966 Simca 1500 GL	https://www.automobile-catalog.com/car/1966/3107735/simca_1500_gl.html
EU-TALBOT-SIMCA-1500-BREAK-WAGON-5D-01	4246	1580	1410	Automobile-Catalog 1965 Simca 1500 Tourisme LS	https://www.automobile-catalog.com/car/1965/3107765/simca_1500_tourisme_ls.html
EU-CITROEN-BX-I-PHASE-II-BREAK-WAGON-5D-01	4399	1682	1431	Automobile-Catalog 1987 Citroën BX Break 14 E	https://www.automobile-catalog.com/car/1987/539255/citroen_bx_break_14_e.html
EU-RENAULT-LATITUDE-SEDAN-4D-01	4897	1832	1483	Automobile-Catalog 2010 Renault Latitude 3.0 dCi V6	https://www.automobile-catalog.com/car/2010/2982755/renault_latitude_3_0_dci_v6.html
EU-VOLVO-V50-I-FACELIFT-WAGON-5D-01	4522	1770	1457	Volvo V50 Owner's Manual MY10	https://ldgsvccassets.blob.core.windows.net/pdfs/18939bdb9d7f579ebf9812040b32cd622be31e4c/V50_owners_manual_MY10_EN_tp10852.pdf
EU-TALBOT-CHRYSLER-160-180-SEDAN-4D-01	4527	1728	1440	Automobile-Catalog 1976 Chrysler-Simca 1609; Automobile-Catalog 1978 Chrysler France 1609-1610 full range	https://www.automobile-catalog.com/car/1976/531650/chrysler_1609_automatic.html; https://www.automobile-catalog.com/make/chrysler_france/1609-2_l/1609-2_l/1978.html
EU-TALBOT-MATRA-BAGHEERA-SERIES-I-COUPE-3D-01	3974	1734	1175	Automobile-Catalog 1974 Matra-Simca Bagheera	https://www.automobile-catalog.com/car/1974/1458455/matra_simca_bagheera.html
EU-TALBOT-MATRA-BAGHEERA-SERIES-II-COUPE-3D-01	4010	1737	1220	Automobile-Catalog 1977 Matra-Simca Bagheera	https://www.automobile-catalog.com/car/1977/1458485/matra_simca_bagheera.html
EU-DACIA-LOGAN-I-MCV-FACELIFT-WAGON-5D-01	4473	1740	1640	Auto-Data Dacia Logan I MCV facelift 1.5 dCi	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-68hp-46176
EU-TALBOT-AVENGER-PREFL-SEDAN-4D-01	4102	1588	1422	Carfolio 1970 Hillman Avenger 1250	https://www.carfolio.com/hillman-avenger-1250-59983
EU-TALBOT-AVENGER-FACELIFT-SEDAN-4D-01	4144	1615	1408	Chrysler Avenger 1978 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2024/02/Chrysler-Avenger-1978-UK.pdf
EU-TALBOT-AVENGER-PREFL-WAGON-5D-01	4204	1588	1422	Automobile-Catalog 1973 Hillman Avenger Estate 1500 De Luxe	https://www.automobile-catalog.com/car/1973/1028255/hillman_avenger_estate_1500_de_luxe.html
EU-TALBOT-AVENGER-FACELIFT-WAGON-5D-01	4250	1615	1415	Talbot Avenger 1980 UK brochure	https://autocatalogarchive.com/wp-content/uploads/2025/05/Talbot-Avenger-1980-UK.pdf
EU-OPEL-KADETT-E-HATCHBACK-3D-01	3998	1663	1400	Automobile-Catalog 1988 Opel Kadett 1.3 N Euronorm	https://www.automobile-catalog.com/car/1988/2458805/opel_kadett_1_3_n_euronorm_5-speed.html
EU-OPEL-KADETT-E-HATCHBACK-5D-01	3998	1663	1400	Automobile-Catalog 1988 Opel Kadett 1.3 N Euronorm	https://www.automobile-catalog.com/car/1988/2458805/opel_kadett_1_3_n_euronorm_5-speed.html
EU-OPEL-KADETT-E-GSI-HATCHBACK-3D-01	3998	1666	1395	Automobile-Catalog 1988 Opel Kadett GSi 16V	https://www.automobile-catalog.com/car/1988/30725/opel_kadett_gsi_16v.html
EU-OPEL-KADETT-E-GSI-HATCHBACK-5D-01	3998	1666	1395	Automobile-Catalog 1988 Opel Kadett GSi 16V	https://www.automobile-catalog.com/car/1988/30725/opel_kadett_gsi_16v.html
EU-OPEL-KADETT-E-SEDAN-4D-01	4218	1658	1400	Automobile-Catalog 1989 Opel Kadett 1.6 D GL Sedan	https://www.automobile-catalog.com/car/1989/2459780/opel_kadett_1_6_d_gl_sedan.html
EU-OPEL-KADETT-E-CONVERTIBLE-16-01	3998	1663	1385	Automobile-Catalog 1990 Opel Kadett Cabrio Edition 1.6i	https://www.automobile-catalog.com/car/1990/2460845/opel_kadett_cabrio_edition_1_6i_cat.html
EU-OPEL-KADETT-E-CONVERTIBLE-20-01	3998	1663	1380	Automobile-Catalog 1990 Opel Kadett Cabrio GSi	https://www.automobile-catalog.com/car/1990/2461130/opel_kadett_cabrio_gsi_cat.html
EU-OPEL-KADETT-E-CARAVAN-01	4228	1666	1430	Automobile-Catalog 1988 Opel Kadett Caravan 1.3 S	https://www.automobile-catalog.com/car/1988/54365/opel_kadett_caravan_1_3_s_ls.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-I-01	4742	1772	1422	Automobile-Catalog 1987 Opel Omega 3000	https://www.automobile-catalog.com/car/1987/57080/opel_omega_3000.html
EU-OPEL-OMEGA-A-3000-SEDAN-PHASE-II-01	4742	1772	1425	Automobile-Catalog 1992 Opel Omega 3000 24V	https://www.automobile-catalog.com/car/1992/2468165/opel_omega_3000_24v_cat.html
EU-OPEL-SENATOR-B-SEDAN-01	4845	1743	1450	Automobile-Catalog 1989 Opel Senator 3.0i	https://www.automobile-catalog.com/car/1989/2469740/opel_senator_3_0i_automatic.html
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Automobile-Catalog 1992 Opel Vectra GL 1.8i Sedan	https://www.automobile-catalog.com/car/1992/2473340/opel_vectra_gl_4d_1_8i.html
EU-OPEL-VECTRA-A-2000-SEDAN-4D-01	4430	1700	1400	Automobile-Catalog 1990 Opel Vectra 2000 16V	https://www.automobile-catalog.com/car/1990/2472680/opel_vectra_2000_16v.html
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400	Automobile-Catalog 1994 Opel Vectra CDX 5-door 1.7 TD	https://www.automobile-catalog.com/car/1994/2475230/opel_vectra_cdx_5d_1_7_td.html
EU-DACIA-LOGAN-I-PICKUP-01	4499	1735	1554	Auto-Data Dacia Logan I Pick-up 1.5 dCi	https://www.auto-data.net/en/dacia-logan-i-pick-up-1.5-dci-86hp-57274
EU-MITSUBISHI-L300-DELICA-II-L03-VAN-SWB-01	3990	1690	1800	Mitsubishi L300 1983 UK brochure; CarsGuide Mitsubishi Express 1983 dimensions	https://automobilisto.de/uk/archive/mitsubishi/l300/1983-uk.pdf; https://www.carsguide.com.au/mitsubishi/express/car-dimensions/1983
EU-MITSUBISHI-L300-DELICA-II-L03-VAN-LWB-HIGHROOF-01	4435	1690	1995	CarsGuide Mitsubishi Express L300 LWB 1983	https://www.carsguide.com.au/mitsubishi/express/price/1983/l300-lwb
EU-DACIA-SANDERO-I-HATCHBACK-5D-01	4020	1746	1534	Automobile-Catalog 2009 Dacia Sandero 1.4 MPI LPG	https://www.automobile-catalog.com/car/2009/1222100/dacia_sandero_1_4_mpi_ambiance_lpg.html
EU-TALBOT-SIMCA-SUNBEAM-HATCHBACK-3D-01	3828	1603	1394	Carfolio 1980 Talbot Sunbeam 1.0 LS	https://www.carfolio.com/talbot-sunbeam-1.0-ls-54417
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Automobile-Catalog 2010 Alfa Romeo Giulietta 1.4 TB 16V	https://www.automobile-catalog.com/car/2010/1240415/alfa_romeo_giulietta_1_4_tb_16v.html
EU-TALBOT-SUNBEAM-LOTUS-HATCHBACK-3D-01	3830	1603	1405	Carfolio 1979 Talbot Sunbeam-Lotus	https://www.carfolio.com/talbot-sunbeam-lotus-30338
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-LOWROOF-PREFL-01	4390	1832	1845	Fiat Professional Doblò Cargo 2010 press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-HIGHROOF-PREFL-01	4390	1832	2100	Fiat Professional Doblò Cargo 2010 press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-PREFL-01	4740	1832	1880	Fiat Professional Doblò Cargo 2010 press information	https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf
EU-FIAT-DOBLO-CARGO-II-263-VAN-SWB-FACELIFT-01	4406	1832	1832	Fiat Professional New Doblò Cargo brochure	https://i.i-sgcm.com/new_cars/cars/11572/brochures/brochure_20200428044756.pdf
EU-FIAT-DOBLO-CARGO-II-263-VAN-LWB-FACELIFT-01	4756	1832	1880	Fiat Professional New Doblò Cargo brochure	https://i.i-sgcm.com/new_cars/cars/11572/brochures/brochure_20200428044756.pdf
EU-SKODA-105-120-SEDAN-FACELIFT-01	4200	1610	1400	Automobile-Catalog 1983 Škoda 120 GLS	https://www.automobile-catalog.com/car/1983/3131585/skoda_120_gls.html
EU-SKODA-RAPID-743-COUPE-01	4200	1610	1380	Automobile-Catalog 1984 Škoda Rapid 120	https://www.automobile-catalog.com/car/1984/3131615/skoda_rapid_120.html
EU-SKODA-1000-1100-MB-SEDAN-4D-01	4170	1620	1390	Automobile-Catalog 1968 Skoda 1000 MB	https://www.automobile-catalog.com/car/1968/3130655/skoda_1000_mb.html
EU-SKODA-1000-MBX-COUPE-2D-01	4170	1620	1390	Carfolio 1966 Skoda 1000 MBX	https://www.carfolio.com/skoda-1000-mbx-500808
EU-TOYOTA-VERSO-S-II-XP120-MPV-5D-01	3990	1695	1595	Auto-Data Toyota Verso-S II 1.33; Auto-Data Toyota Verso-S II 1.4 D-4D	https://www.auto-data.net/en/toyota-verso-s-ii-1.33-dual-vvt-i-98hp-18486; https://www.auto-data.net/en/toyota-verso-s-ii-1.4-d-4d-dpf-89hp-18488
EU-SKODA-OCTAVIA-1959-SEDAN-2D-01	4065	1600	1430	Automobile-Catalog 1959 Skoda Octavia	https://www.automobile-catalog.com/car/1959/3130460/skoda_octavia.html
EU-SKODA-100-110-SEDAN-4D-01	4155	1620	1380	Automobile-Catalog 1970 Skoda 110 L	https://www.automobile-catalog.com/car/1970/3131045/skoda_110_l.html
EU-SKODA-110R-COUPE-2D-01	4155	1620	1340	Škoda Storyboard 50 Years of the 110 R	https://www.skoda-storyboard.com/en/press-releases/50-years-of-the-110-r-half-a-century-ago-skoda-presented-its-legendary-sports-coupe/
EU-ALFA-ROMEO-1750-BERLINA-SEDAN-4D-01	4390	1565	1430	Automobile-Catalog 1969 Alfa Romeo 1750 Berlina	https://www.automobile-catalog.com/car/1969/65150/alfa_romeo_1750_berlina.html
EU-ALFA-ROMEO-MONTREAL-10564-COUPE-2D-01	4220	1672	1205	Automobile-Catalog 1973 Alfa Romeo Montreal	https://www.automobile-catalog.com/car/1973/24395/alfa_romeo_montreal.html
EU-OPEL-ANTARA-A-FACELIFT-SUV-5D-01	4596	1850	1717	Auto-Data Opel Antara facelift 2010 2.4	https://www.auto-data.net/en/opel-antara-facelift-2010-2.4-167hp-16948
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6701-6800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://e-sklep.ktd.eu/karta-pojazdu/7194/mitsubishi-l-300-delica-ii-furgon-l03-p-2-3-d-l038p-l068p "https://e-sklep.ktd.eu/karta-pojazdu/7194/mitsubishi-l-300-delica-ii-furgon-l03-p-2-3-d-l038p-l068p"
[2]: https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf "https://www.media.stellantis.com/uploads/uk/UK/2010/FIAT_PROF/PRESS/100225_fpro_doblo_pressinfo.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6701-6800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6701-6800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8543 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2650 行）

