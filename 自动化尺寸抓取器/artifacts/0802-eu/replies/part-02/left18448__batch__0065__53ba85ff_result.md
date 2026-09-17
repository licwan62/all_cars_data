# 任务：left18448 第 6401-6500 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0065__53ba85ff


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 6401-6500 行

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
left18448 第 6401-6500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-GALLOPER-GALLOPER-II-SUV-3D-01	4020	1770	1860

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Galloper	Galloper	2.5 TD Intercooler	Geländewagen geschlossen	Allrad	Diesel	Nov 1997	Aug 2002	151144
GAZ	69	M	Geländewagen offen	Allrad	Benzin	Apr 1966	Sep 1975	121901
GAZ	Valdaj	3.8 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	Sep 2010	-	55401
GAZ	Volga	2.4	Kombi	Heckantrieb	Benzin	Jan 1972	Jan 1987	117551
Geely	Bl	1.3	Coupe	Frontantrieb	Benzin	Sep 2005	-	19071
Geely	Bl	1.5	Coupe	Frontantrieb	Benzin	Sep 2005	-	19072
Geely	Ck	1.3	Stufenheck	Frontantrieb	Benzin	Sep 2005	-	19073
Geely	Ck	1.5	Stufenheck	Frontantrieb	Benzin	Sep 2005	-	19074
Geely	Ck	1.6	Stufenheck	Frontantrieb	Benzin	Sep 2005	Jun 2011	19075
Geely	Ex5	EV	SUV	Frontantrieb	Elektro	Nov 2024	-	160336
Geely	Hq srv	1.1	Kombi	Frontantrieb	Benzin	Sep 2005	-	19081
Geely	Mr	1.3	Schrägheck	Frontantrieb	Benzin	Sep 2005	-	19083
Geely	Mr sedan	1.1	Stufenheck	Frontantrieb	Benzin	Sep 2005	-	19086
Geely	Mr sedan	1.3	Stufenheck	Frontantrieb	Benzin	Sep 2005	-	19087
Geely	Mr sedan	1.5	Stufenheck	Frontantrieb	Benzin	Sep 2005	-	19088
Geely	Pu	1	Pick-up	Frontantrieb	Benzin	Sep 2005	-	19089
Geely	Pu	1.1	Pick-up	Frontantrieb	Benzin	Sep 2005	-	19090
Geely	Pu	1.3	Pick-up	Frontantrieb	Benzin	Sep 2005	-	19091
Geely	Starray	1.5	SUV	Frontantrieb	Benzin	Dec 2024	-	803177
Geely	Starray	1.5 Em-i Plug-in Hybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2025	-	803179
Geely	Starray	2.0 AWD	SUV	Allrad	Benzin	Dec 2024	-	803178
Genesis	G70	2.0 T-gdi	Stufenheck	Heckantrieb	Benzin	Jun 2021	-	145266
Genesis	G70	2.0 T-gdi	Stufenheck	Heckantrieb	Benzin	Jun 2021	-	145271
Genesis	G70	2.0 T-gdi	Kombi	Heckantrieb	Benzin	Jun 2021	-	145273
Genesis	G70	2.0 T-gdi	Kombi	Heckantrieb	Benzin	Jun 2021	-	145278
Genesis	G70	2.0 T-gdi Htrac	Stufenheck	Allrad	Benzin	Jun 2021	-	145267
Genesis	G70	2.0 T-gdi Htrac	Stufenheck	Allrad	Benzin	Jun 2021	-	145272
Genesis	G70	2.0 T-gdi Htrac	Kombi	Allrad	Benzin	Jun 2021	-	145274
Genesis	G70	2.0 T-gdi Htrac	Kombi	Allrad	Benzin	Jun 2021	-	145279
Genesis	G70	2.2 Crdi	Stufenheck	Heckantrieb	Diesel	Jun 2021	-	145269
Genesis	G70	2.2 Crdi	Kombi	Heckantrieb	Diesel	Jun 2021	-	145275
Genesis	G70	2.2 Crdi Htrac	Stufenheck	Allrad	Diesel	Jun 2021	-	145270
Genesis	G70	2.2 Crdi Htrac	Kombi	Allrad	Diesel	Jun 2021	-	145277
Genesis	G80	2.2 Crdi	Stufenheck	Heckantrieb	Diesel	Jun 2021	-	145739
Genesis	G80	2.2 Crdi AWD	Stufenheck	Allrad	Diesel	Jun 2021	-	144901
Genesis	G80	2.5 T-gdi	Stufenheck	Heckantrieb	Benzin	Aug 2020	-	145767
Genesis	G80	2.5 T-gdi AWD	Stufenheck	Allrad	Benzin	Aug 2020	-	142615
Genesis	G80	Electrified AWD	Stufenheck	Allrad	Elektro	Oct 2021	-	146772
Genesis	G90	3.5 T Mild Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Apr 2022	-	151495
Genesis	Gv60	Electrified	SUV	Heckantrieb	Elektro	Oct 2021	-	145497
Genesis	Gv60	Electrified AWD	SUV	Allrad	Elektro	Oct 2021	-	145498
Genesis	Gv60	Electrified AWD	SUV	Allrad	Elektro	Oct 2021	-	145499
Genesis	Gv60	Magma AWD	SUV	Allrad	Elektro	Jan 2026	-	802802
Genesis	Gv70	2.2	SUV	Heckantrieb	Diesel	Apr 2021	-	145264
Genesis	Gv70	2.2 AWD	SUV	Allrad	Diesel	Apr 2021	-	144942
Genesis	Gv70	2.2 AWD	SUV	Allrad	Diesel	May 2022	-	147724
Genesis	Gv70	2.5 AWD	SUV	Allrad	Benzin	Apr 2021	-	144941
Genesis	Gv70	EV AWD	SUV	Allrad	Elektro	Nov 2022	-	151412
Genesis	Gv80	3.0 Crdi AWD	SUV	Allrad	Diesel	May 2022	-	147725
Geometry	Ex3	E	SUV	Frontantrieb	Elektro	Nov 2021	-	145858
German E Cars	Cetos	Elektro	Schrägheck	Frontantrieb	Elektro	Sep 2011	-	126024
German E Cars	Plantos	Elektro	Kasten	Frontantrieb	Elektro	Sep 2011	-	126025
German E Cars	Plantos	Elektro	Pritsche/Fahrgestell	Frontantrieb	Elektro	Sep 2011	-	126026
German E Cars	Stromos	Elektro	Schrägheck	Frontantrieb	Elektro	Sep 2010	-	126023
Giotti Victoria	Gladiator evo	1.2	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 2020	-	156402
Giotti Victoria	Gladiator evo	1.2 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2020	-	156403
Giotti Victoria	Gladiator top	1.5	Pritsche/Fahrgestell	Heckantrieb	Benzin	Jan 2020	-	156436
Giotti Victoria	Gladiator top	1.5 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	Jan 2020	-	156437
Giotti Victoria	Gladiator top	Electric	Pritsche/Fahrgestell	Heckantrieb	Elektro	Jan 2022	-	156438
Giotti Victoria	Gladiator top	Electric	Kasten	Heckantrieb	Elektro	Jan 2022	-	156439
Glas	1700	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1964	Dec 1968	8832
GMC	Yukon	5.3	SUV	Heckantrieb	Benzin	Sep 2006	Dec 2010	107627
GMC	Yukon	6.2	SUV	Heckantrieb	Benzin	Sep 2008	Dec 2009	53925
GMC	Yukon	6.2 4WD	SUV	Allrad	Benzin	Sep 2010	Jul 2014	55219
Great Wall	Ora 03	300/300 PRO	Schrägheck	Frontantrieb	Elektro	Jan 2024	-	157902
Great Wall	Ora 03	400pro/400 Pro+	Schrägheck	Frontantrieb	Elektro	Jan 2024	-	157903
Great Wall	Ora 03	GT	Schrägheck	Frontantrieb	Elektro	Jan 2024	-	157904
Great Wall	Ora 07	EV	Stufenheck	Frontantrieb	Elektro	Dec 2023	-	162491
Great Wall	Ora 07	EV 4X4	Stufenheck	Allrad	Elektro	Dec 2023	-	162492
Great Wall	Wey 03	2.0 Phev	SUV	Frontantrieb	Benzin/Elektro	Mar 2024	-	158534
Great Wall	Wey 03	2.0 Phev AWD	SUV	Allrad	Benzin/Elektro	Mar 2024	-	158587
Great Wall	Wey 05	2.0 Phev AWD	SUV	Allrad	Benzin/Elektro	Mar 2024	-	158588
Great Wall	Wingle 6	2.4 LPG 4X4	Pick-up	Allrad	Benzin/Autogas (LPG)	Jan 2022	-	151790
Haval	H2	1.5 LPG	SUV	Frontantrieb	LPG	Apr 2021	-	154839
Honda	Accord iii aerodeck	1.6 L	Kombi	Frontantrieb	Benzin	Nov 1985	Dec 1989	14669
Honda	Accord iii aerodeck	2.0 EX	Kombi	Frontantrieb	Benzin	Oct 1987	Dec 1989	5056
Honda	Accord ix	2.4	Stufenheck	Frontantrieb	Benzin	Jul 2014	-	117564
Honda	Accord ix	3.5	Stufenheck	Frontantrieb	Benzin	Sep 2012	-	58318
Honda	Accord v	2	Coupe	Frontantrieb	Benzin	Sep 1993	Dec 1997	17641
Honda	Accord v	2.2 I	Stufenheck	Frontantrieb	Benzin	Apr 1993	Jun 1997	121838
Honda	Accord vi	2.3	Stufenheck	Frontantrieb	Benzin	Jan 2001	Jun 2003	15817
Honda	Accord vi	1.6 I	Stufenheck	Frontantrieb	Benzin	Oct 1998	Dec 2002	14899
Honda	Accord vi	1.8 I	Stufenheck	Frontantrieb	Benzin	Oct 1998	Dec 2002	10026
Honda	Accord vi	2.0 I	Stufenheck	Frontantrieb	Benzin	Oct 1998	Jan 2001	10027
Honda	Accord vi	2.0 I 16V	Coupe	Frontantrieb	Benzin	Feb 1998	Jun 2003	10239
Honda	Accord vi	2.0 Turbo DI	Stufenheck	Frontantrieb	Diesel	Feb 1999	Dec 2002	10299
Honda	Accord vi	2.2 Type-r	Stufenheck	Frontantrieb	Benzin	Feb 1999	Dec 2002	10028
Honda	Accord vi	3.0 V6 24V	Coupe	Frontantrieb	Benzin	Feb 1998	Jun 2003	10240
Honda	Accord vi hatchback	2	Schrägheck	Frontantrieb	Benzin	Dec 1999	Dec 2002	17715
Honda	Accord vi hatchback	2.3	Schrägheck	Frontantrieb	Benzin	Nov 2000	Dec 2002	17714
Honda	Accord vi hatchback	1.8 I	Schrägheck	Frontantrieb	Benzin	Dec 1999	Dec 2002	14411
Honda	Accord vi hatchback	2.0 TDI	Schrägheck	Frontantrieb	Diesel	Dec 1999	Oct 2000	18865
Honda	Accord vii	2	Stufenheck	Frontantrieb	Benzin	Feb 2003	May 2008	17126
Honda	Accord vii	2.4	Stufenheck	Frontantrieb	Benzin	Feb 2003	May 2008	17127
Honda	Accord vii	2.0 Allrad	Stufenheck	Allrad	Benzin	Feb 2003	May 2008	17716
Honda	Accord vii	2.2 I-ctdi	Stufenheck	Frontantrieb	Diesel	Jan 2004	May 2008	17485
Honda	Accord vii tourer	2	Kombi	Frontantrieb	Benzin	Apr 2003	May 2008	17263
Honda	Accord vii tourer	2.4	Kombi	Frontantrieb	Benzin	Apr 2003	May 2008	17264
Honda	Accord vii tourer	2.2 I-ctdi	Kombi	Frontantrieb	Diesel	Jan 2004	May 2008	17486
Honda	Accord viii	2.2 I-dtec	Stufenheck	Frontantrieb	Diesel	Jul 2008	Jun 2015	34928


--- Round 1 / 首次发送 ---
## 更新点

* 完成 Genesis 车型聚类，共处理 28 个 Ktype；其中 27 个已映射为 `READY`，建立 9 个可复用尺寸组。
* G70 Sedan、G70 Shooting Brake、G80、Electrified G80 的外廓分别闭合；相同发动机差异不重复建组。官方规格页支持对应车身三维。([Genesis Worldwide][1])
* 初期 GV60、GV60 Magma、GV70、Electrified GV70、改款前 GV80 分别建组；Magma 因宽体及外部套件独立建组。([Genesis Worldwide][2])
* G90 暂保留 `PENDING`：Genesis 欧洲资料明确存在标准轴距和长轴距两种车身，而输入行未注明轴距，不能任选其一。([Genesis News Europe][3])

## 当前批次进度

* 输入 Ktype：100
* 已处理：28
* READY：27
* PENDING：1
* 尚未进入映射判断：72
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
145266	145266	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145271	145271	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145273	145273	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145278	145278	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145267	145267	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145272	145272	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145274	145274	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145279	145279	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145269	145269	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145275	145275	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145270	145270	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145277	145277	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake 五门旅行车外廓。	READY
145739	145739	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代 G80 四门轿车外廓。	READY
144901	144901	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代 G80 四门轿车外廓。	READY
145767	145767	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代 G80 四门轿车外廓。	READY
142615	142615	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代 G80 四门轿车外廓。	READY
146772	146772	Sedan	G80 II Electrified		4	EU-GENESIS-G80-II-ELECTRIFIED-SEDAN-01	HIGH	纯电版外廓与燃油版分组。	READY
151495	151495	Sedan	G90 II		4		LOW	输入未标明标准轴距或长轴距，暂不建立尺寸组。	PENDING: 轴距分支未确认
145497	145497	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门 SUV 外廓。	READY
145498	145498	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门 SUV 外廓。	READY
145499	145499	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门 SUV 外廓。	READY
802802	802802	SUV	GV60 I Magma		5	EU-GENESIS-GV60-I-MAGMA-SUV-01	HIGH	Magma 宽体及外部套件形成独立外廓。	READY
145264	145264	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门 SUV 外廓。	READY
144942	144942	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门 SUV 外廓。	READY
147724	147724	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门 SUV 外廓。	READY
144941	144941	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门 SUV 外廓。	READY
151412	151412	SUV	GV70 I Electrified		5	EU-GENESIS-GV70-I-ELECTRIFIED-SUV-01	HIGH	纯电版独立尺寸组。	READY
147725	147725	SUV	GV80 I pre-facelift		5	EU-GENESIS-GV80-I-PREFL-SUV-01	HIGH	改款前五门 SUV 外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GENESIS-G70-I-FACELIFT-SEDAN-01	4685	1850	1400	Genesis G70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g70/specs.html
EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	4685	1850	1400	Genesis G70 Shooting Brake official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g70-shooting-brake/specs.html
EU-GENESIS-G80-II-SEDAN-01	4995	1925	1465	Genesis G80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g80/specs.html
EU-GENESIS-G80-II-ELECTRIFIED-SEDAN-01	5005	1925	1475	Genesis Electrified G80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/electrified-g80/specs.html
EU-GENESIS-GV60-I-PREFL-SUV-01	4515	1890	1580	Genesis GV60 official specifications	https://www.genesis.com/ae/en/models/luxury-suv-genesis/gv60/specs.html
EU-GENESIS-GV60-I-MAGMA-SUV-01	4635	1940	1560	Genesis GV60 Magma official specifications	https://www.genesis.com/worldwide/en/models/luxury-suv-genesis/gv60-magma/specs.html
EU-GENESIS-GV70-I-SUV-01	4715	1910	1630	Genesis GV70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/gv70/specs.html
EU-GENESIS-GV70-I-ELECTRIFIED-SUV-01	4715	1910	1630	Genesis Electrified GV70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/electrified-gv70/specs.html
EU-GENESIS-GV80-I-PREFL-SUV-01	4945	1975	1715	Genesis GV80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/gv80/specs.html
```

## 下一步优先处理

1. 先解决 G90 标准轴距/长轴距边界，消除已记录的唯一显式 `PENDING`。
2. 按缓存收益继续处理 Geely 早期 BL、CK、MR、PU、HQ SRV 聚类。
3. 批量闭合 Great Wall Ora、Wey 和 Honda Accord 各代车身组。

推进信号：CONTINUE

[1]: https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g70/specs.html?utm_source=chatgpt.com "GENESIS G70 Specs | GENESIS Middle East & Africa"
[2]: https://www.genesis.com/ae/en/models/luxury-suv-genesis/gv60/specs.html?utm_source=chatgpt.com "SPEC"
[3]: https://www.genesisnewseurope.com/english/g90 "G90"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已消除上一轮 G90 的轴距分支冲突：Ktype `151495` 对应 `G90 II (RS4) 3.5 T Mild Hybrid AWD 415 hp`，匹配长轴距车身，改为 `READY`。([AUTODOC][1])
* 完成 Geely BL、CK、EX5 和 Starray 聚类。BL 两种发动机共用 Coupe 外廓，CK 三种发动机共用 Sedan 外廓。([汽车数据网][2])
* EX5 建立纯电 SUV 尺寸组；Starray 燃油版 1.5 与 2.0 AWD 共用尺寸组，Starray EM-i 因车身三维不同独立建组。([吉利汽车][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：37
* PENDING/待处理映射：63
* 已确认尺寸组：15
* 本轮新增 READY：9
* 本轮修正 READY：1
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151495	151495	Sedan	G90 II LWB	RS4	4	EU-GENESIS-G90-II-LWB-SEDAN-01	HIGH	RS4长轴距四门轿车外廓。	READY
19071	19071	Coupe	Beauty Leopard I		2	EU-GEELY-BL-I-COUPE-01	HIGH	BL双门Coupe外廓。	READY
19072	19072	Coupe	Beauty Leopard I		2	EU-GEELY-BL-I-COUPE-01	HIGH	BL双门Coupe外廓。	READY
19073	19073	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
19074	19074	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
19075	19075	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
160336	160336	SUV	EX5 I		5	EU-GEELY-EX5-I-SUV-01	HIGH	EX5第一代纯电五门SUV外廓。	READY
803177	803177	SUV	Starray I		5	EU-GEELY-STARRAY-I-SUV-01	HIGH	Starray燃油版五门SUV外廓。	READY
803179	803179	SUV	Starray EM-i I		5	EU-GEELY-STARRAY-EMI-I-SUV-01	HIGH	EM-i使用独立车身外廓。	READY
803178	803178	SUV	Starray I		5	EU-GEELY-STARRAY-I-SUV-01	HIGH	Starray燃油版五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GENESIS-G90-II-LWB-SEDAN-01	5465	1930	1490	Auto-Data Genesis G90 II LWB 3.5 T-GDi e-S/C Mild Hybrid specifications	https://www.auto-data.net/en/genesis-g90-ii-lwb-3.5-t-gdi-e-s-c-v6-415hp-mild-hybrid-awd-automatic-4-seat-48346
EU-GEELY-BL-I-COUPE-01	4110	1690	1325	Auto-Data Geely Beauty Leopard 1.3 specifications; Drive.place Geely Beauty Leopard 1.5 specifications	https://www.auto-data.net/en/geely-beauty-leopard-1.3-86hp-10100;https://geely.drive.place/beauty_leopard/i/group_coupe/387786
EU-GEELY-CK-I-SEDAN-01	4152	1680	1440	Drive.place Geely CK 1.3 specifications; Drive.place Geely CK 1.5 specifications	https://geely.drive.place/ck/i/group_sedan/387796;https://geely.drive.place/ck/i/group_sedan/387798
EU-GEELY-EX5-I-SUV-01	4615	1901	1670	Geely Auto UK EX5 official specifications	https://www.geelyauto.co.uk/geely-ex5
EU-GEELY-STARRAY-I-SUV-01	4670	1900	1705	Geely Starray official specifications	https://www.geely.com/en/models/starray
EU-GEELY-STARRAY-EMI-I-SUV-01	4740	1905	1685	Geely New Zealand official Starray EM-i specification sheet; WELT Starray EM-i technical data	https://geely-nz.aueast01.umbraco.io/media/rdll1lfx/geely-starray-em-i-specification-sheet-september-2025-preliminary.pdf;https://www.welt.de/motor/news/article6a4b7141d38ff307b91859b4/fahrbericht-geely-starray-em-i.html
```

## 下一步优先处理

1. 处理 Galloper、GAZ 与 Geometry，优先复用已有 Galloper II 三门 SUV 尺寸组。
2. 聚类 Great Wall Ora 03、Ora 07、Wey 03、Wey 05 与 Wingle 6。
3. 随后批量闭合 Honda Accord 各代 Sedan、Coupe、Hatchback 和 Tourer 外廓。

推进信号：CONTINUE

[1]: https://www.autodoc24.fr/car-parts/engine-oil-12094/genesis/g90/g90-rs4/151495-3-5-t-mild-hybrid-awd?utm_source=chatgpt.com "Engine oil GENESIS G90 II (RS4) 3.5 T Mild Hybrid AWD 415 hp ..."
[2]: https://www.auto-data.net/en/geely-beauty-leopard-1.3-86hp-10100?utm_source=chatgpt.com "Specs of Geely Beauty Leopard 1.3 (86 Hp) /2003, 2004, ..."
[3]: https://www.geelyauto.co.uk/geely-ex5?utm_source=chatgpt.com "Geely Auto UK - Geely EX5"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 新增 12 条 `READY` 映射，首次建立 9 个尺寸组。
* 完成 GAZ 69 M、GAZ-24-02 Volga Wagon 和 Geometry EX3；GAZ 69 M 按双门开放式车身处理，Volga 对应 1972–1987 年 GAZ-24-02 五门旅行版。([gaz69.org][1])
* 完成 ORA 03、ORA 07、WEY 03、WEY 05 和 Haval H2 聚类。ORA 03 GT 的外廓不同于 300/400 系列，因此独立建组。
* Galloper、Valdai 和 Wingle 6 暂列 `PENDING`：分别存在三门/五门、标准/长轴及驾驶室或货斗分支，当前输入不足以选择唯一外廓。([维基百科][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：49
* PENDING 映射：3
* 尚未处理：48
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151144	151144	SUV	Galloper II	JK-01			LOW	三门短轴与五门长轴均存在，当前输入未确认物理分支。	PENDING: 门数及轴距分支未确认
121901	121901	SUV	GAZ-69	69M	2	EU-GAZ-69-I-SUV-2D-01	MEDIUM	M型双门开放式车身外廓。	READY
55401	55401	Pickup	Valdai I				LOW	底盘车型存在标准轴距、长轴及不同驾驶室配置。	PENDING: 轴距及驾驶室分支未确认
117551	117551	Wagon	Volga GAZ-24	24-02	5	EU-GAZ-VOLGA-GAZ-24-WAGON-01	HIGH	GAZ-24-02五门旅行车外廓。	READY
145858	145858	SUV	EX3 I		5	EU-GEOMETRY-EX3-I-SUV-01	HIGH	EX3第一代五门SUV外廓。	READY
157902	157902	Hatchback	ORA 03 I		5	EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	HIGH	300及300 PRO标准车身外廓。	READY
157903	157903	Hatchback	ORA 03 I		5	EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	HIGH	400 PRO及400 PRO+标准车身外廓。	READY
157904	157904	Hatchback	ORA 03 I GT		5	EU-GREAT-WALL-ORA-03-I-GT-HATCHBACK-01	HIGH	GT外部造型造成独立外廓。	READY
162491	162491	Sedan	ORA 07 I		4	EU-GREAT-WALL-ORA-07-I-SEDAN-01	HIGH	前驱四门轿跑式轿车外廓。	READY
162492	162492	Sedan	ORA 07 I		4	EU-GREAT-WALL-ORA-07-I-SEDAN-01	HIGH	四驱版本共用四门车身外廓。	READY
158534	158534	SUV	WEY 03 I		5	EU-GREAT-WALL-WEY-03-I-SUV-01	HIGH	前驱五门SUV外廓。	READY
158587	158587	SUV	WEY 03 I		5	EU-GREAT-WALL-WEY-03-I-SUV-01	HIGH	四驱版本共用五门SUV外廓。	READY
158588	158588	SUV	WEY 05 I		5	EU-GREAT-WALL-WEY-05-I-SUV-01	HIGH	WEY 05五门SUV外廓。	READY
151790	151790	Pickup	Wingle 6 I	CC1031			LOW	存在单排、双排及不同总长配置，当前输入未确认驾驶室和货斗分支。	PENDING: 驾驶室及车身长度分支未确认
154839	154839	SUV	H2 I		5	EU-HAVAL-H2-I-SUV-01	HIGH	LPG动力不改变H2五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GAZ-69-I-SUV-2D-01	3850	1850	2030	GAZ69.org specifications based on Polish Ministry of Defense documentation	https://www.gaz69.org/gaz/SpecEN.html
EU-GAZ-VOLGA-GAZ-24-WAGON-01	4735	1800	1576	Auto-Data GAZ 24-02 station wagon specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GEOMETRY-EX3-I-SUV-01	4005	1760	1575	Auto-Data Geometry EX3 specifications	https://www.auto-data.net/en/geometry-ex3-model-3356
EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	4235	1825	1603	GWM Germany ORA Funky Cat 300 Pro technical data	https://presse.gwm-motor.de/wp-content/uploads/2023/09/ORA-FUNKY-CAT-300-Pro%C2%AD_Technische-Daten.pdf
EU-GREAT-WALL-ORA-03-I-GT-HATCHBACK-01	4254	1848	1603	GWM Germany ORA Funky Cat GT technical data	https://presse.gwm-motor.de/wp-content/uploads/2023/09/ORA-FUNKY-CAT-GT%C2%AD_Technische-Daten.pdf
EU-GREAT-WALL-ORA-07-I-SEDAN-01	4871	1862	1500	GWM Germany ORA 07 technical data	https://presse.gwm-motor.de/wp-content/uploads/2024/06/Technische-Daten.pdf
EU-GREAT-WALL-WEY-03-I-SUV-01	4668	1890	1730	GWM Germany WEY 03 technical data	https://presse.gwm-motor.de/wp-content/uploads/2025/06/Technische-Daten_GWM-WEY-03.pdf
EU-GREAT-WALL-WEY-05-I-SUV-01	4870	1960	1690	GWM Germany WEY 05 technical data	https://presse.gwm-motor.de/wp-content/uploads/2025/04/Technische-Daten_GWM-WEY-05.pdf
EU-HAVAL-H2-I-SUV-01	4335	1814	1695	HAVAL H2 official brochure	https://www.zimoco.co.zw/wp-content/uploads/2019/03/Haval-H2-brochure-Rev7.pdf
```

## 下一步优先处理

1. 优先确认 Galloper、Valdai 和 Wingle 6 的物理分支，消除本轮 3 条显式 `PENDING`。
2. 批量处理 Geely HQ SRV、MR、MR Sedan 和 PU。
3. 随后处理 German E Cars、Giotti Victoria，再集中闭合 Honda Accord 各代车身组。

推进信号：CONTINUE

[1]: https://www.gaz69.org/gaz/SpecEN.html "GAZ 69"
[2]: https://en.wikipedia.org/wiki/Hyundai_Galloper?utm_source=chatgpt.com "Hyundai Galloper"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 解决 Wingle 6 的驾驶室分支：Ktype `151790` 对应 2022 年起的 2.4 LPG 4×4，按双排四门车身映射；对应车型规格为 5345 × 1800 × 1760 mm。([汽车零件在线商店][1])
* 完成 Geely HQ SRV、MR Hatchback、MR Sedan 和 PU 聚类；发动机排量差异不重复建组。
* Galloper 与 Valdai 继续保留 `PENDING`：前者仍需闭合 `KNE1CP/KPE1CP` 与门数的对应关系；后者明确存在标准轴距、长轴距和双排驾驶室分支。([KMotorShop][2])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：58
* PENDING 映射：2
* 尚未处理：40
* 已确认尺寸组：29
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19081	19081	Wagon	HQ I SRV		5	EU-GEELY-HQ-I-SRV-WAGON-01	MEDIUM	HQ SRV五门旅行车外廓。	READY
19083	19083	Hatchback	MR I		5	EU-GEELY-MR-I-HATCHBACK-01	HIGH	MR五门掀背车外廓。	READY
19086	19086	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19087	19087	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19088	19088	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19089	19089	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
19090	19090	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
19091	19091	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
151790	151790	Pickup	Wingle 6 I	CC1031	4	EU-GREAT-WALL-WINGLE-6-I-DOUBLECAB-PICKUP-01	HIGH	双排四门Pickup外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GEELY-HQ-I-SRV-WAGON-01	3900	1650	1420	Geely HQ model specifications	https://en.wikipedia.org/wiki/Geely_HQ
EU-GEELY-MR-I-HATCHBACK-01	3825	1670	1386	17vin 2006 Geely Merrie 1.3L configuration	https://en.17vin.com/model/ixi6x.html
EU-GEELY-MR-I-SEDAN-01	4125	1620	1450	Drive.place Geely MR I 1.3 Sedan specifications	https://geely.drive.place/mr/i/group_sedan/388138
EU-GEELY-PU-I-PICKUP-01	3965	1640	1434	Geely PU model specifications	https://en.wikipedia.org/wiki/Geely_PU
EU-GREAT-WALL-WINGLE-6-I-DOUBLECAB-PICKUP-01	5345	1800	1760	YallaMotor Great Wall Wingle 6 2022 2.4L Double Cabin 4x4 specifications	https://qatar.yallamotor.com/new-cars/great-wall/wingle-6/2022/2-4l-double-cabin-4x4
```

## 下一步优先处理

1. 闭合 Galloper `KNE1CP/KPE1CP` 的三门、五门边界。
2. 将 Valdai 的标准轴距、长轴距单排和长轴距双排拆成稳定派生行。
3. 随后批量处理 German E Cars、Giotti Victoria 与 GMC Yukon。

推进信号：CONTINUE

[1]: https://www.onlinecarparts.co.uk/car-brands/spare-parts-great-wall/wingle-6/151790.html?utm_source=chatgpt.com "GREAT WALL Wingle 6 Pickup 2.4 LPG 4x4 150 hp 2022 - ... parts online catalogue"
[2]: https://www.kmotorshop.com/en/article-detail/view/83829/connecting-rod-bearing-71-4194-4-std-glyco-md024856-md026430-md050365?utm_source=chatgpt.com "Connecting Rod Bearing Shell - 71-4194/4 STD GLYCO - MD024856, MD026430, MD050365 | K MOTORSHOP s.r.o."


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 消除 Galloper 的门数分支冲突：Ktype `151144` 同时覆盖 `KNE1CP` 三门短轴和 `KPE1CP` 五门长轴，现拆为两条派生映射。三门资料得到的三维与累计 `3D-01` 不一致，因此未覆盖旧组，改建 `3D-02`。([Rbrake][1])
* 消除 Valdai 的轴距和驾驶室分支冲突：拆分为 `GAZ-33106` 标准轴距单排、`GAZ-331061` 长轴单排、`GAZ-331063` 长轴双排三种量产外廓。([Газавтомир][2])
* 完成 German E Cars Cetos 与 Stromos。Cetos 对应 Corsa D 五门车身；Stromos 官方资料明确给出五门车身及完整三维。([Motor1.com][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：62
* READY 映射：65
* PENDING/待处理输入 Ktype：38
* 已确认尺寸组：36
* 本轮新增 READY 映射：7
* 本轮首次创建尺寸组：7
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151144_3dr	151144	SUV	Galloper II	KNE1CP	3	EU-GALLOPER-GALLOPER-II-SUV-3D-02	HIGH	KNE1CP三门短轴外廓。	READY
151144_5dr	151144	SUV	Galloper II	KPE1CP	5	EU-GALLOPER-GALLOPER-II-SUV-5D-01	HIGH	KPE1CP五门长轴外廓。	READY
55401_swb	55401	Pickup	Valdai I	GAZ-33106	2	EU-GAZ-VALDAI-I-PICKUP-SWB-01	HIGH	标准轴距单排驾驶室外廓。	READY
55401_lwb	55401	Pickup	Valdai I	GAZ-331061	2	EU-GAZ-VALDAI-I-PICKUP-LWB-01	HIGH	长轴距单排驾驶室外廓。	READY
55401_lwb_doublecab	55401	Pickup	Valdai I	GAZ-331063	4	EU-GAZ-VALDAI-I-PICKUP-LWB-DOUBLECAB-01	HIGH	长轴距双排驾驶室外廓。	READY
126024	126024	Hatchback	Cetos I		5	EU-GERMAN-E-CARS-CETOS-I-HATCHBACK-01	MEDIUM	Corsa D五门基础车身。	READY
126023	126023	Hatchback	Stromos I		5	EU-GERMAN-E-CARS-STROMOS-I-HATCHBACK-01	HIGH	Suzuki Splash五门基础车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GALLOPER-GALLOPER-II-SUV-3D-02	4085	1770	1860	Auto-Data Hyundai Galloper II 3-door specifications	https://www.auto-data.net/en/hyundai-galloper-ii-3.0-i-v6-sport-161hp-13715
EU-GALLOPER-GALLOPER-II-SUV-5D-01	4685	1785	1870	Drive.place Hyundai Galloper II 2.5 MT 99 hp 5-door specifications	https://hyundai.drive.place/galloper/1991-%E2%80%93-2003/group_offroad_5d/103186
EU-GAZ-VALDAI-I-PICKUP-SWB-01	6050	2350	2260	GAZ Valdai Cummins technical specification; GAZ-33106 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://tdagrotehsnab.ru/catalog/avtospetstekhnika/srednetonnazhnye-avtomobili/item/367-gaz-33106-valdaj
EU-GAZ-VALDAI-I-PICKUP-LWB-01	7565	2350	2260	GAZ Valdai Cummins technical specification; GAZ-33106 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://tdagrotehsnab.ru/catalog/avtospetstekhnika/srednetonnazhnye-avtomobili/item/367-gaz-33106-valdaj
EU-GAZ-VALDAI-I-PICKUP-LWB-DOUBLECAB-01	6770	2350	2265	GAZ Valdai Cummins technical specification; GAZ-331063 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://www.26auto.ru/gaz/lmg/gmd04/gaz331063/
EU-GERMAN-E-CARS-CETOS-I-HATCHBACK-01	3999	1737	1488	Motor1 German E-Cars Cetos body identification; Automoli Opel Corsa D facelift 5-door specifications	https://de.motor1.com/news/158234/german-e-cars-cetos-elektrisch-angetriebener-opel-corsa/;https://www.automoli.com/en/vehicles/opel/corsa/corsa-d-facelift-2011-5-door-3806/
EU-GERMAN-E-CARS-STROMOS-I-HATCHBACK-01	3715	1680	1590	German E-Cars Stromos official brochure	https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf
```

## 下一步优先处理

1. 处理 Plantos Van 与底盘车的 Sprinter 轴距、车长和车顶分支。
2. 聚类 Giotti Victoria Gladiator Evo、Gladiator Top 的底盘及厢式车外廓。
3. 随后处理 Glas 1700、GMC Yukon，再集中闭合 Honda Accord 各代车身。

推进信号：CONTINUE

[1]: https://catalogonuevo.rbrake.com/Vehiculo/Details?idTipoVehiculo=2&idVehiculo=151144&utm_source=chatgpt.com "2.5 TD intercooler (KNE1CP, KPE1CP) details - Web Catalogo"
[2]: https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/ "Техническая характеристика автомобилей Валдай с двигателем Cummins"
[3]: https://de.motor1.com/news/158234/german-e-cars-cetos-elektrisch-angetriebener-opel-corsa/?utm_source=chatgpt.com "Cetos von German E-Cars auf der IAA"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成 Giotti Victoria Gladiator Evo、Gladiator Top 燃油底盘聚类；汽油与 LPG 版本复用各自相同外廓。官方产品资料分别给出 Evo 23 底盘和 Top 30 底盘的完整三维。
* 完成 Gladiator Top Electric 厢式车映射。电动底盘 Ktype `156438` 暂保留 `PENDING`：官方车身化资料允许多个成车总长，输入未限定具体底盘或后悬分支。([Automoto.it][1])
* 完成 Glas 1700 四门轿车以及第三代标准轴距 GMC Yukon 聚类；三个 Yukon Ktype 共用 GMT922 外廓。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：72
* READY 映射：74
* PENDING 映射：1
* 尚未处理输入 Ktype：28
* 已确认尺寸组：41
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156402	156402	Pickup	Gladiator Evo	Evo 23	2	EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	HIGH	Evo单排底盘外廓。	READY
156403	156403	Pickup	Gladiator Evo	Evo 23	2	EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	HIGH	LPG动力共用Evo单排底盘外廓。	READY
156436	156436	Pickup	Gladiator Top	Top 30	2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	HIGH	Top单排底盘外廓。	READY
156437	156437	Pickup	Gladiator Top	Top 30	2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	HIGH	LPG动力共用Top单排底盘外廓。	READY
156438	156438	Pickup	Gladiator Top Electric		2		LOW	电动底盘存在多个成车总长分支，输入未限定具体配置。	PENDING: 底盘车长分支未确认
156439	156439	Van	Gladiator Top Electric		4	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-VAN-01	MEDIUM	Top Electric封闭式厢式车外廓。	READY
8832	8832	Sedan	1700		4	EU-GLAS-1700-I-SEDAN-01	HIGH	1700四门轿车外廓。	READY
107627	107627	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	标准轴距五门SUV外廓。	READY
53925	53925	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	6.2升版本共用标准轴距五门外廓。	READY
55219	55219	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	四驱版本共用标准轴距五门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	4190	1560	1850	Giotti Victoria Gladiator official 2020 brochure	https://asset.moto.it/pricelist/auto/04cda2d87ec0693af0103329ca4349e2/brochure-2020.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	4600	1660	1890	Giotti Victoria Gladiator official 2020 brochure	https://asset.moto.it/pricelist/auto/04cda2d87ec0693af0103329ca4349e2/brochure-2020.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-VAN-01	4500	1680	2000	Automoto Giotti Victoria Gladiator Top Electric Van specifications	https://www.automoto.it/catalogo/giotti-victoria/gladiator-furgone/gladiator-top-electric-van-clima/185539
EU-GLAS-1700-I-SEDAN-01	4415	1610	1390	Automobile-Catalog Glas 1700 sedan specifications	https://www.automobile-catalog.com/car/1967/1017725/glas_1700_ts.html
EU-GMC-YUKON-III-SUV-01	5131	2007	1953	General Motors of Canada 2013 GMC Yukon official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2013_yukon.pdf
```

## 下一步优先处理

1. 消除 `156438` 的电动底盘总长分支，确认是否需要拆分短后悬和长后悬派生行。
2. 处理 Plantos 厢式车与底盘车型的 Sprinter 轴距、车长及车顶分支。
3. 随后集中闭合 Honda Accord 各代 Sedan、Coupe、Hatchback、Aerodeck 和 Tourer 尺寸组。

推进信号：CONTINUE

[1]: https://www.automoto.it/catalogo/giotti-victoria/gladiator-furgone/gladiator-top-electric-van-clima/185539?utm_source=chatgpt.com "Giotti Victoria Gladiator Furgone Gladiator Top Electric van clima: prezzo e scheda tecnica - Automoto.it"
[2]: https://www.automobile-catalog.com/car/1967/1017725/glas_1700_ts.html?utm_source=chatgpt.com "1967 Glas 1700 TS Specs Review (73.5 kW / 100 PS / 99 hp) (up to late-year 1967 for Europe )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 消除 Ktype `156438` 的底盘车长分支，按官方技术表中的 `TOP ELECTRIC CHASSIS` 固定外廓建组；同时将既有 `156439` 厢式车尺寸组高度由 `2000` 修正为官方表中的 `1985 mm`。([IRP][1])
* 完成 Honda Accord VII Sedan、Tourer 共 7 个 Ktype 的批量映射，分别复用轿车和旅行车两个尺寸组。Honda 欧洲规格给出的轿车尺寸为 `4665×1760×1445 mm`，Tourer 为 `4750×1760×1470 mm`。([本田新闻][2])
* 完成 Accord VIII `2.2 i-DTEC` 的 `CU3` 四门轿车映射。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖输入 Ktype：80
* READY 映射：83
* PENDING/待处理输入 Ktype：20
* 已确认尺寸组：45
* 本轮新增/修改映射：9
* 本轮首次创建尺寸组：4
* 本轮修正尺寸组：1
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
156438	156438	Pickup	Gladiator Top Electric		2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-PICKUP-CHASSIS-01	HIGH	Top Electric单排电动底盘外廓。	READY
17126	17126	Sedan	Accord VII	CL7	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL7前驱四门轿车外廓。	READY
17127	17127	Sedan	Accord VII	CL9	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL9四门轿车外廓。	READY
17716	17716	Sedan	Accord VII	CL8	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL8四驱四门轿车外廓。	READY
17485	17485	Sedan	Accord VII	CN1	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CN1柴油四门轿车外廓。	READY
17263	17263	Wagon	Accord VII Tourer	CM1	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CM1五门Tourer外廓。	READY
17264	17264	Wagon	Accord VII Tourer	CM2	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CM2五门Tourer外廓。	READY
17486	17486	Wagon	Accord VII Tourer	CN2	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CN2柴油五门Tourer外廓。	READY
34928	34928	Sedan	Accord VIII	CU3	4	EU-HONDA-ACCORD-VIII-SEDAN-01	HIGH	CU3柴油四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-PICKUP-CHASSIS-01	4615	1635	1900	Giotti Victoria Gladiator official technical brochure	https://irp.cdn-website.com/ec5ac99a/files/uploaded/Depliant_Giotti_Victoria.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-VAN-01	4500	1680	1985	Giotti Victoria Gladiator official technical brochure	https://irp.cdn-website.com/ec5ac99a/files/uploaded/Depliant_Giotti_Victoria.pdf
EU-HONDA-ACCORD-VII-SEDAN-01	4665	1760	1445	Honda Europe Accord i-CTDi official specifications	https://hondanews.eu/eu/et/cars/media/pressreleases/34419/accord-i-ctdi-specifications
EU-HONDA-ACCORD-VII-TOURER-WAGON-01	4750	1760	1470	Honda Europe Accord i-CTDi official specifications	https://hondanews.eu/eu/et/cars/media/pressreleases/34419/accord-i-ctdi-specifications
EU-HONDA-ACCORD-VIII-SEDAN-01	4726	1840	1440	Auto-Data Honda Accord VIII 2.2 i-DTEC specifications	https://www.auto-data.net/en/honda-accord-viii-2.2-i-dtec-150hp-17148
```

## 下一步优先处理

1. 批量闭合 Accord VI 欧洲版 Sedan、Coupe 与 Hatchback 三个物理车身。
2. 处理 Accord III Aerodeck、Accord V Sedan/Coupe 和 Accord IX Sedan。
3. 最后处理 Plantos 厢式车与底盘车的 Sprinter 5 吨级轴距、车长和车顶分支。

推进信号：CONTINUE

[1]: https://irp.cdn-website.com/ec5ac99a/files/uploaded/Depliant_Giotti_Victoria.pdf?utm_source=chatgpt.com "Gladiator"
[2]: https://hondanews.eu/eu/et/cars/media/pressreleases/34419/accord-i-ctdi-specifications?utm_source=chatgpt.com "Accord i-CTDi | Specifications"
[3]: https://www.auto-data.net/en/honda-accord-viii-2.2-i-dtec-150hp-17148?utm_source=chatgpt.com "Honda Accord VIII 2.2 i-DTEC (150 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_6401-6500_ktype_dimension_mapping_final.tsv
- left18448_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合剩余 20 个输入 Ktype：Plantos 厢式车与底盘车 2 个，Honda Accord 各代车型 18 个。
* Plantos 按 W906 长轴车身处理：厢式车采用长轴超高顶外廓，底盘车采用长轴单排驾驶室外廓。Plantos 的资料指向 5 吨级 Sprinter 基础车型，Mercedes-Benz 资料确认了对应车身尺寸与不含后视镜宽度。([TU Delft开放期刊][1])
* Accord III Aerodeck、Accord V、VI、IX 的 Sedan、Coupe、Hatchback 和 Aerodeck 外廓已分别闭合；不同车身形式即使三维相同，也保留独立尺寸组。([Honda News][2])
* 已完成一次机械收尾检查：固定表头正确，103 个 `id` 唯一，54 个 `DIMENSION_GROUP_ID` 唯一，所有映射引用闭合，无孤立尺寸组、空尺寸、空来源或 `PENDING`。

## 当前批次进度

* 输入 Ktype：100
* 最终 Ktype 映射行：103
* READY：103
* PENDING：0
* DIMENSION_GROUP：54
* 多外廓 Ktype：`151144`、`55401`
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
151144_3dr	151144	SUV	Galloper II	KNE1CP	3	EU-GALLOPER-GALLOPER-II-SUV-3D-02	HIGH	KNE1CP三门短轴外廓。	READY
151144_5dr	151144	SUV	Galloper II	KPE1CP	5	EU-GALLOPER-GALLOPER-II-SUV-5D-01	HIGH	KPE1CP五门长轴外廓。	READY
121901	121901	SUV	GAZ-69	69M	2	EU-GAZ-69-I-SUV-2D-01	MEDIUM	M型双门开放式车身外廓。	READY
55401_swb	55401	Pickup	Valdai I	GAZ-33106	2	EU-GAZ-VALDAI-I-PICKUP-SWB-01	HIGH	标准轴距单排驾驶室外廓。	READY
55401_lwb	55401	Pickup	Valdai I	GAZ-331061	2	EU-GAZ-VALDAI-I-PICKUP-LWB-01	HIGH	长轴距单排驾驶室外廓。	READY
55401_lwb_doublecab	55401	Pickup	Valdai I	GAZ-331063	4	EU-GAZ-VALDAI-I-PICKUP-LWB-DOUBLECAB-01	HIGH	长轴距双排驾驶室外廓。	READY
117551	117551	Wagon	Volga GAZ-24	24-02	5	EU-GAZ-VOLGA-GAZ-24-WAGON-01	HIGH	GAZ-24-02五门旅行车外廓。	READY
19071	19071	Coupe	Beauty Leopard I		2	EU-GEELY-BL-I-COUPE-01	HIGH	BL双门Coupe外廓。	READY
19072	19072	Coupe	Beauty Leopard I		2	EU-GEELY-BL-I-COUPE-01	HIGH	BL双门Coupe外廓。	READY
19073	19073	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
19074	19074	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
19075	19075	Sedan	CK I		4	EU-GEELY-CK-I-SEDAN-01	HIGH	CK第一代四门轿车外廓。	READY
160336	160336	SUV	EX5 I		5	EU-GEELY-EX5-I-SUV-01	HIGH	EX5第一代纯电五门SUV外廓。	READY
19081	19081	Wagon	HQ I SRV		5	EU-GEELY-HQ-I-SRV-WAGON-01	MEDIUM	HQ SRV五门旅行车外廓。	READY
19083	19083	Hatchback	MR I		5	EU-GEELY-MR-I-HATCHBACK-01	HIGH	MR五门掀背车外廓。	READY
19086	19086	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19087	19087	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19088	19088	Sedan	MR I		4	EU-GEELY-MR-I-SEDAN-01	HIGH	MR四门轿车外廓。	READY
19089	19089	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
19090	19090	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
19091	19091	Pickup	PU I	JL1010E1	2	EU-GEELY-PU-I-PICKUP-01	MEDIUM	两门Pickup外廓。	READY
803177	803177	SUV	Starray I		5	EU-GEELY-STARRAY-I-SUV-01	HIGH	Starray燃油版五门SUV外廓。	READY
803179	803179	SUV	Starray EM-i I		5	EU-GEELY-STARRAY-EMI-I-SUV-01	HIGH	EM-i使用独立车身外廓。	READY
803178	803178	SUV	Starray I		5	EU-GEELY-STARRAY-I-SUV-01	HIGH	Starray燃油版五门SUV外廓。	READY
145266	145266	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145271	145271	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145273	145273	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145278	145278	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145267	145267	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145272	145272	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145274	145274	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145279	145279	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145269	145269	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145275	145275	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145270	145270	Sedan	G70 I facelift		4	EU-GENESIS-G70-I-FACELIFT-SEDAN-01	HIGH	改款后四门轿车外廓。	READY
145277	145277	Wagon	G70 I Shooting Brake		5	EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	HIGH	Shooting Brake五门旅行车外廓。	READY
145739	145739	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代G80四门轿车外廓。	READY
144901	144901	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代G80四门轿车外廓。	READY
145767	145767	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代G80四门轿车外廓。	READY
142615	142615	Sedan	G80 II		4	EU-GENESIS-G80-II-SEDAN-01	HIGH	第二代G80四门轿车外廓。	READY
146772	146772	Sedan	G80 II Electrified		4	EU-GENESIS-G80-II-ELECTRIFIED-SEDAN-01	HIGH	纯电版外廓与燃油版分组。	READY
151495	151495	Sedan	G90 II LWB	RS4	4	EU-GENESIS-G90-II-LWB-SEDAN-01	HIGH	RS4长轴距四门轿车外廓。	READY
145497	145497	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门SUV外廓。	READY
145498	145498	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门SUV外廓。	READY
145499	145499	SUV	GV60 I pre-facelift		5	EU-GENESIS-GV60-I-PREFL-SUV-01	HIGH	初期量产版五门SUV外廓。	READY
802802	802802	SUV	GV60 I Magma		5	EU-GENESIS-GV60-I-MAGMA-SUV-01	HIGH	Magma宽体及外部套件形成独立外廓。	READY
145264	145264	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门SUV外廓。	READY
144942	144942	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门SUV外廓。	READY
147724	147724	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门SUV外廓。	READY
144941	144941	SUV	GV70 I		5	EU-GENESIS-GV70-I-SUV-01	HIGH	第一代燃油版五门SUV外廓。	READY
151412	151412	SUV	GV70 I Electrified		5	EU-GENESIS-GV70-I-ELECTRIFIED-SUV-01	HIGH	纯电版独立尺寸组。	READY
147725	147725	SUV	GV80 I pre-facelift		5	EU-GENESIS-GV80-I-PREFL-SUV-01	HIGH	改款前五门SUV外廓。	READY
145858	145858	SUV	EX3 I		5	EU-GEOMETRY-EX3-I-SUV-01	HIGH	EX3第一代五门SUV外廓。	READY
126024	126024	Hatchback	Cetos I		5	EU-GERMAN-E-CARS-CETOS-I-HATCHBACK-01	MEDIUM	Corsa D五门基础车身。	READY
126025	126025	Van	Plantos I	W906	4	EU-GERMAN-E-CARS-PLANTOS-I-VAN-LWB-SUPERHIGHROOF-01	MEDIUM	W906长轴超高顶厢式车外廓。	READY
126026	126026	Pickup	Plantos I	W906	2	EU-GERMAN-E-CARS-PLANTOS-I-PICKUP-LWB-CHASSIS-01	MEDIUM	W906长轴单排底盘外廓。	READY
126023	126023	Hatchback	Stromos I		5	EU-GERMAN-E-CARS-STROMOS-I-HATCHBACK-01	HIGH	Suzuki Splash五门基础车身。	READY
156402	156402	Pickup	Gladiator Evo	Evo 23	2	EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	HIGH	Evo单排底盘外廓。	READY
156403	156403	Pickup	Gladiator Evo	Evo 23	2	EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	HIGH	LPG动力共用Evo单排底盘外廓。	READY
156436	156436	Pickup	Gladiator Top	Top 30	2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	HIGH	Top单排底盘外廓。	READY
156437	156437	Pickup	Gladiator Top	Top 30	2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	HIGH	LPG动力共用Top单排底盘外廓。	READY
156438	156438	Pickup	Gladiator Top Electric		2	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-PICKUP-CHASSIS-01	HIGH	Top Electric单排电动底盘外廓。	READY
156439	156439	Van	Gladiator Top Electric		4	EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-VAN-01	MEDIUM	Top Electric封闭式厢式车外廓。	READY
8832	8832	Sedan	1700		4	EU-GLAS-1700-I-SEDAN-01	HIGH	1700四门轿车外廓。	READY
107627	107627	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	标准轴距五门SUV外廓。	READY
53925	53925	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	6.2升版本共用标准轴距五门外廓。	READY
55219	55219	SUV	Yukon III	GMT922	5	EU-GMC-YUKON-III-SUV-01	HIGH	四驱版本共用标准轴距五门外廓。	READY
157902	157902	Hatchback	ORA 03 I		5	EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	HIGH	300及300 PRO标准车身外廓。	READY
157903	157903	Hatchback	ORA 03 I		5	EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	HIGH	400 PRO及400 PRO+标准车身外廓。	READY
157904	157904	Hatchback	ORA 03 I GT		5	EU-GREAT-WALL-ORA-03-I-GT-HATCHBACK-01	HIGH	GT外部造型造成独立外廓。	READY
162491	162491	Sedan	ORA 07 I		4	EU-GREAT-WALL-ORA-07-I-SEDAN-01	HIGH	前驱四门轿跑式轿车外廓。	READY
162492	162492	Sedan	ORA 07 I		4	EU-GREAT-WALL-ORA-07-I-SEDAN-01	HIGH	四驱版本共用四门车身外廓。	READY
158534	158534	SUV	WEY 03 I		5	EU-GREAT-WALL-WEY-03-I-SUV-01	HIGH	前驱五门SUV外廓。	READY
158587	158587	SUV	WEY 03 I		5	EU-GREAT-WALL-WEY-03-I-SUV-01	HIGH	四驱版本共用五门SUV外廓。	READY
158588	158588	SUV	WEY 05 I		5	EU-GREAT-WALL-WEY-05-I-SUV-01	HIGH	WEY 05五门SUV外廓。	READY
151790	151790	Pickup	Wingle 6 I	CC1031	4	EU-GREAT-WALL-WINGLE-6-I-DOUBLECAB-PICKUP-01	HIGH	双排四门Pickup外廓。	READY
154839	154839	SUV	H2 I		5	EU-HAVAL-H2-I-SUV-01	HIGH	LPG动力不改变H2五门SUV外廓。	READY
14669	14669	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-WAGON-01	HIGH	三门Aerodeck车身外廓。	READY
5056	5056	Wagon	Accord III Aerodeck		3	EU-HONDA-ACCORD-III-AERODECK-WAGON-01	HIGH	三门Aerodeck车身外廓。	READY
117564	117564	Sedan	Accord IX	CR2	4	EU-HONDA-ACCORD-IX-SEDAN-01	HIGH	CR2四缸四门轿车外廓。	READY
58318	58318	Sedan	Accord IX	CR3	4	EU-HONDA-ACCORD-IX-SEDAN-01	HIGH	CR3 V6四门轿车外廓。	READY
17641	17641	Coupe	Accord V		2	EU-HONDA-ACCORD-V-COUPE-01	HIGH	第五代双门Coupe外廓。	READY
121838	121838	Sedan	Accord V		4	EU-HONDA-ACCORD-V-SEDAN-01	HIGH	第五代四门轿车外廓。	READY
15817	15817	Sedan	Accord VI		4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	2.3升四门轿车外廓。	READY
14899	14899	Sedan	Accord VI	CG7	4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	CG7四门轿车外廓。	READY
10026	10026	Sedan	Accord VI	CG8	4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	CG8四门轿车外廓。	READY
10027	10027	Sedan	Accord VI	CG9	4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	CG9四门轿车外廓。	READY
10239	10239	Coupe	Accord VI	CG4	2	EU-HONDA-ACCORD-VI-COUPE-01	HIGH	CG4双门Coupe外廓。	READY
10299	10299	Sedan	Accord VI	CH2	4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	CH2柴油四门轿车外廓。	READY
10028	10028	Sedan	Accord VI	CH1	4	EU-HONDA-ACCORD-VI-SEDAN-01	HIGH	CH1 Type-R四门轿车外廓。	READY
10240	10240	Coupe	Accord VI	CG2	2	EU-HONDA-ACCORD-VI-COUPE-01	HIGH	CG2 V6双门Coupe外廓。	READY
17715	17715	Hatchback	Accord VI Hatchback		5	EU-HONDA-ACCORD-VI-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
17714	17714	Hatchback	Accord VI Hatchback		5	EU-HONDA-ACCORD-VI-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
14411	14411	Hatchback	Accord VI Hatchback		5	EU-HONDA-ACCORD-VI-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
18865	18865	Hatchback	Accord VI Hatchback		5	EU-HONDA-ACCORD-VI-HATCHBACK-01	HIGH	五门Hatchback外廓。	READY
17126	17126	Sedan	Accord VII	CL7	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL7前驱四门轿车外廓。	READY
17127	17127	Sedan	Accord VII	CL9	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL9四门轿车外廓。	READY
17716	17716	Sedan	Accord VII	CL8	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CL8四驱四门轿车外廓。	READY
17485	17485	Sedan	Accord VII	CN1	4	EU-HONDA-ACCORD-VII-SEDAN-01	HIGH	CN1柴油四门轿车外廓。	READY
17263	17263	Wagon	Accord VII Tourer	CM1	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CM1五门Tourer外廓。	READY
17264	17264	Wagon	Accord VII Tourer	CM2	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CM2五门Tourer外廓。	READY
17486	17486	Wagon	Accord VII Tourer	CN2	5	EU-HONDA-ACCORD-VII-TOURER-WAGON-01	HIGH	CN2柴油五门Tourer外廓。	READY
34928	34928	Sedan	Accord VIII	CU3	4	EU-HONDA-ACCORD-VIII-SEDAN-01	HIGH	CU3柴油四门轿车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_6401-6500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-GALLOPER-GALLOPER-II-SUV-3D-02	4085	1770	1860	Auto-Data Hyundai Galloper II 3-door specifications	https://www.auto-data.net/en/hyundai-galloper-ii-3.0-i-v6-sport-161hp-13715
EU-GALLOPER-GALLOPER-II-SUV-5D-01	4685	1785	1870	Drive.place Hyundai Galloper II 2.5 MT 99 hp 5-door specifications	https://hyundai.drive.place/galloper/1991-%E2%80%93-2003/group_offroad_5d/103186
EU-GAZ-69-I-SUV-2D-01	3850	1850	2030	GAZ69.org specifications based on Polish Ministry of Defense documentation	https://www.gaz69.org/gaz/SpecEN.html
EU-GAZ-VALDAI-I-PICKUP-SWB-01	6050	2350	2260	GAZ Valdai Cummins technical specification; GAZ-33106 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://tdagrotehsnab.ru/catalog/avtospetstekhnika/srednetonnazhnye-avtomobili/item/367-gaz-33106-valdaj
EU-GAZ-VALDAI-I-PICKUP-LWB-01	7565	2350	2260	GAZ Valdai Cummins technical specification; GAZ-33106 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://tdagrotehsnab.ru/catalog/avtospetstekhnika/srednetonnazhnye-avtomobili/item/367-gaz-33106-valdaj
EU-GAZ-VALDAI-I-PICKUP-LWB-DOUBLECAB-01	6770	2350	2265	GAZ Valdai Cummins technical specification; GAZ-331063 dimensional data	https://gazavtomir.ru/info/teh/exploitation/valday_cummins/4/;https://www.26auto.ru/gaz/lmg/gmd04/gaz331063/
EU-GAZ-VOLGA-GAZ-24-WAGON-01	4735	1800	1576	Auto-Data GAZ 24-02 station wagon specifications	https://www.auto-data.net/en/gaz-24-model-1467
EU-GEELY-BL-I-COUPE-01	4110	1690	1325	Auto-Data Geely Beauty Leopard 1.3 specifications; Drive.place Geely Beauty Leopard 1.5 specifications	https://www.auto-data.net/en/geely-beauty-leopard-1.3-86hp-10100;https://geely.drive.place/beauty_leopard/i/group_coupe/387786
EU-GEELY-CK-I-SEDAN-01	4152	1680	1440	Drive.place Geely CK 1.3 specifications; Drive.place Geely CK 1.5 specifications	https://geely.drive.place/ck/i/group_sedan/387796;https://geely.drive.place/ck/i/group_sedan/387798
EU-GEELY-EX5-I-SUV-01	4615	1901	1670	Geely Auto UK EX5 official specifications	https://www.geelyauto.co.uk/geely-ex5
EU-GEELY-HQ-I-SRV-WAGON-01	3900	1650	1420	Geely HQ model specifications	https://en.wikipedia.org/wiki/Geely_HQ
EU-GEELY-MR-I-HATCHBACK-01	3825	1670	1386	17vin 2006 Geely Merrie 1.3L configuration	https://en.17vin.com/model/ixi6x.html
EU-GEELY-MR-I-SEDAN-01	4125	1620	1450	Drive.place Geely MR I 1.3 Sedan specifications	https://geely.drive.place/mr/i/group_sedan/388138
EU-GEELY-PU-I-PICKUP-01	3965	1640	1434	Geely PU model specifications	https://en.wikipedia.org/wiki/Geely_PU
EU-GEELY-STARRAY-I-SUV-01	4670	1900	1705	Geely Starray official specifications	https://www.geely.com/en/models/starray
EU-GEELY-STARRAY-EMI-I-SUV-01	4740	1905	1685	Geely New Zealand official Starray EM-i specification sheet; WELT Starray EM-i technical data	https://geely-nz.aueast01.umbraco.io/media/rdll1lfx/geely-starray-em-i-specification-sheet-september-2025-preliminary.pdf;https://www.welt.de/motor/news/article6a4b7141d38ff307b91859b4/fahrbericht-geely-starray-em-i.html
EU-GENESIS-G70-I-FACELIFT-SEDAN-01	4685	1850	1400	Genesis G70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g70/specs.html
EU-GENESIS-G70-I-SHOOTING-BRAKE-WAGON-01	4685	1850	1400	Genesis G70 Shooting Brake official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g70-shooting-brake/specs.html
EU-GENESIS-G80-II-SEDAN-01	4995	1925	1465	Genesis G80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/g80/specs.html
EU-GENESIS-G80-II-ELECTRIFIED-SEDAN-01	5005	1925	1475	Genesis Electrified G80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-sedan-genesis/electrified-g80/specs.html
EU-GENESIS-G90-II-LWB-SEDAN-01	5465	1930	1490	Auto-Data Genesis G90 II LWB 3.5 T-GDi e-S/C Mild Hybrid specifications	https://www.auto-data.net/en/genesis-g90-ii-lwb-3.5-t-gdi-e-s-c-v6-415hp-mild-hybrid-awd-automatic-4-seat-48346
EU-GENESIS-GV60-I-PREFL-SUV-01	4515	1890	1580	Genesis GV60 official specifications	https://www.genesis.com/ae/en/models/luxury-suv-genesis/gv60/specs.html
EU-GENESIS-GV60-I-MAGMA-SUV-01	4635	1940	1560	Genesis GV60 Magma official specifications	https://www.genesis.com/worldwide/en/models/luxury-suv-genesis/gv60-magma/specs.html
EU-GENESIS-GV70-I-SUV-01	4715	1910	1630	Genesis GV70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/gv70/specs.html
EU-GENESIS-GV70-I-ELECTRIFIED-SUV-01	4715	1910	1630	Genesis Electrified GV70 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/electrified-gv70/specs.html
EU-GENESIS-GV80-I-PREFL-SUV-01	4945	1975	1715	Genesis GV80 official specifications	https://www.genesis.com/middleeast/en/models/luxury-suv-genesis/gv80/specs.html
EU-GEOMETRY-EX3-I-SUV-01	4005	1760	1575	Auto-Data Geometry EX3 specifications	https://www.auto-data.net/en/geometry-ex3-model-3356
EU-GERMAN-E-CARS-CETOS-I-HATCHBACK-01	3999	1737	1488	Motor1 German E-Cars Cetos body identification; Automoli Opel Corsa D facelift 5-door specifications	https://de.motor1.com/news/158234/german-e-cars-cetos-elektrisch-angetriebener-opel-corsa/;https://www.automoli.com/en/vehicles/opel/corsa/corsa-d-facelift-2011-5-door-3806/
EU-GERMAN-E-CARS-PLANTOS-I-VAN-LWB-SUPERHIGHROOF-01	6945	1993	3045	Mercedes-Benz 2011 Sprinter Panel Van official brochure; EJTIR Plantos technical comparison	https://xr793.com/wp-content/uploads/2022/12/2011-Mercedes-Benz-Sprinter-Panel-Van-UK.pdf;https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/
EU-GERMAN-E-CARS-PLANTOS-I-PICKUP-LWB-CHASSIS-01	6845	1988	2385	Mercedes-Benz 2011 Sprinter official range brochure; CarExpert 2011 Sprinter cab chassis specifications; EJTIR Plantos technical comparison	https://xr793.com/wp-content/uploads/2023/10/2011-Mercedes-Benz-Sprinter-Range-AUS.pdf;https://www.carexpert.com.au/mercedes-benz/sprinter/2011-2-1l-cab-chassis-rwd-diesel-automatic-jogg88ag20110203;https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/
EU-GERMAN-E-CARS-STROMOS-I-HATCHBACK-01	3715	1680	1590	German E-Cars Stromos official brochure	https://www.casacota.net/liofilitzats/voltforum/www.atmos.cat/dispara2/gec_stromos_e.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-EVO-PICKUP-CHASSIS-01	4190	1560	1850	Giotti Victoria Gladiator official 2020 brochure	https://asset.moto.it/pricelist/auto/04cda2d87ec0693af0103329ca4349e2/brochure-2020.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-PICKUP-CHASSIS-01	4600	1660	1890	Giotti Victoria Gladiator official 2020 brochure	https://asset.moto.it/pricelist/auto/04cda2d87ec0693af0103329ca4349e2/brochure-2020.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-PICKUP-CHASSIS-01	4615	1635	1900	Giotti Victoria Gladiator official technical brochure	https://irp.cdn-website.com/ec5ac99a/files/uploaded/Depliant_Giotti_Victoria.pdf
EU-GIOTTI-VICTORIA-GLADIATOR-TOP-ELECTRIC-VAN-01	4500	1680	1985	Giotti Victoria Gladiator official technical brochure	https://irp.cdn-website.com/ec5ac99a/files/uploaded/Depliant_Giotti_Victoria.pdf
EU-GLAS-1700-I-SEDAN-01	4415	1610	1390	Automobile-Catalog Glas 1700 sedan specifications	https://www.automobile-catalog.com/car/1967/1017725/glas_1700_ts.html
EU-GMC-YUKON-III-SUV-01	5131	2007	1953	General Motors of Canada 2013 GMC Yukon official brochure	https://www.centuryu.com/uploads/1/4/4/6/144698822/2013_yukon.pdf
EU-GREAT-WALL-ORA-03-I-HATCHBACK-01	4235	1825	1603	GWM Germany ORA Funky Cat 300 Pro technical data	https://presse.gwm-motor.de/wp-content/uploads/2023/09/ORA-FUNKY-CAT-300-Pro%C2%AD_Technische-Daten.pdf
EU-GREAT-WALL-ORA-03-I-GT-HATCHBACK-01	4254	1848	1603	GWM Germany ORA Funky Cat GT technical data	https://presse.gwm-motor.de/wp-content/uploads/2023/09/ORA-FUNKY-CAT-GT%C2%AD_Technische-Daten.pdf
EU-GREAT-WALL-ORA-07-I-SEDAN-01	4871	1862	1500	GWM Germany ORA 07 technical data	https://presse.gwm-motor.de/wp-content/uploads/2024/06/Technische-Daten.pdf
EU-GREAT-WALL-WEY-03-I-SUV-01	4668	1890	1730	GWM Germany WEY 03 technical data	https://presse.gwm-motor.de/wp-content/uploads/2025/06/Technische-Daten_GWM-WEY-03.pdf
EU-GREAT-WALL-WEY-05-I-SUV-01	4870	1960	1690	GWM Germany WEY 05 technical data	https://presse.gwm-motor.de/wp-content/uploads/2025/04/Technische-Daten_GWM-WEY-05.pdf
EU-GREAT-WALL-WINGLE-6-I-DOUBLECAB-PICKUP-01	5345	1800	1760	YallaMotor Great Wall Wingle 6 2022 2.4L Double Cabin 4x4 specifications	https://qatar.yallamotor.com/new-cars/great-wall/wingle-6/2022/2-4l-double-cabin-4x4
EU-HAVAL-H2-I-SUV-01	4335	1814	1695	HAVAL H2 official brochure	https://www.zimoco.co.zw/wp-content/uploads/2019/03/Haval-H2-brochure-Rev7.pdf
EU-HONDA-ACCORD-III-AERODECK-WAGON-01	4335	1695	1335	Carfolio Honda Accord Aerodeck 2.0 EX specifications; Honda official Aerodeck body history	https://www.carfolio.com/honda-accord-aerodeck-2.0-ex-600666;https://global.honda/en/newsroom/worldnews/1997/4970904a.html
EU-HONDA-ACCORD-IX-SEDAN-01	4862	1849	1466	Honda 2013 Accord official body specifications	https://hondanews.com/releases/2013-honda-accord-body
EU-HONDA-ACCORD-V-COUPE-01	4675	1780	1390	Honda 1994 Accord Coupe official specifications	https://hondanews.com/en-US/honda-automobiles/releases/release-ce695ed4e4dc2645d260f5004c34ca33-1994-honda-accord-coupe-specifications
EU-HONDA-ACCORD-V-SEDAN-01	4675	1780	1400	Honda 1994 Accord Sedan official specifications	https://hondanews.com/en-US/honda-automobiles/releases/release-16799e92adef9b18737e92004c34ca32-1994-honda-accord-sedan-specifications
EU-HONDA-ACCORD-VI-SEDAN-01	4595	1750	1430	Honda Europe Geneva Motorshow 2000 official Accord specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-ACCORD-VI-COUPE-01	4745	1785	1400	Honda 1998 Accord Coupe official specifications	https://hondanews.com/en-US/honda-automobiles/releases/release-afb9f78eb14f105b74dac3004c34c994-1998-honda-accord-coupe-specifications
EU-HONDA-ACCORD-VI-HATCHBACK-01	4595	1750	1430	Honda Europe Geneva Motorshow 2000 official Accord 5-door specifications	https://hondanews.eu/eu/en/cars/media/pressreleases/34359/geneva-motorshow-2000
EU-HONDA-ACCORD-VII-SEDAN-01	4665	1760	1445	Honda Europe Accord i-CTDi official specifications	https://hondanews.eu/eu/et/cars/media/pressreleases/34419/accord-i-ctdi-specifications
EU-HONDA-ACCORD-VII-TOURER-WAGON-01	4750	1760	1470	Honda Europe Accord i-CTDi official specifications	https://hondanews.eu/eu/et/cars/media/pressreleases/34419/accord-i-ctdi-specifications
EU-HONDA-ACCORD-VIII-SEDAN-01	4726	1840	1440	Auto-Data Honda Accord VIII 2.2 i-DTEC specifications	https://www.auto-data.net/en/honda-accord-viii-2.2-i-dtec-150hp-17148
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_6401-6500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/ "https://journals.open.tudelft.nl/ejtir/article/download/3160/3347/"
[2]: https://hondanews.com/releases/2013-honda-accord-body "https://hondanews.com/releases/2013-honda-accord-body"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3422 行）
- 累计尺寸组：dimension_groups_final.tsv（879 行）

