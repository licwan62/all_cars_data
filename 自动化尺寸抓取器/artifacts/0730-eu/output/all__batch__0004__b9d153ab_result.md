# 任务：all 第 301-400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0004__b9d153ab


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 301-400 行

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
all 第 301-400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671
EU-AUDI-A4-B9-AVANT-WAGON-01	4725	1842	1434
EU-AUDI-A5-F5-COUPE-01	4673	1846	1371
EU-AUDI-A5-F5-SPORTBACK-01	4733	1843	1386
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457
EU-AUDI-A6-C8-4A5-WAGON-01	4939	1886	1494
EU-AUDI-A6-C8-4AH-WAGON-ALLROAD-01	4951	1902	1497
EU-AUDI-A6-C8-ALLROAD-WAGON-01	4951	1902	1497
EU-AUDI-Q3-8U-FACELIFT-SUV-01	4388	1831	1608
EU-AUDI-Q5-I-8R-SUV-01	4629	1898	1655
EU-AUDI-Q5-II-FY-SQ5-SUV-01	4671	1893	1635
EU-AUDI-Q5-II-FY-SUV-01	4663	1893	1659
EU-AUDI-Q5-II-FY-SUV-02	4682	1893	1662
EU-BMW-3-E30-BAUR-TC-CONVERTIBLE-01	4325	1645	1380
EU-BMW-3-E30-M3-CONVERTIBLE-01	4345	1680	1370
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
EU-BMW-3-G21-WAGON-PREFL-PHEV-XDRIVE-01	4709	1827	1442
EU-BMW-340-SEDAN-01	4600	1765	1630
EU-BMW-4-F32-COUPE-01	4638	1825	1377
EU-BMW-4-F33-CONVERTIBLE-01	4638	1825	1384
EU-BMW-4-F82-COUPE-M4-CS-01	4672	1870	1392
EU-BMW-5-E39-SEDAN-FACELIFT-01	4775	1800	1435
EU-BMW-5-E39-WAGON-FACELIFT-01	4805	1800	1445
EU-BMW-5-E39-WAGON-PREFL-01	4805	1800	1445
EU-BMW-5-E60-SEDAN-01	4841	1846	1468
EU-BMW-5-E61-WAGON-01	4843	1846	1491
EU-BMW-5-F07-GRAN-TURISMO-FACELIFT-01	5004	1901	1559
EU-BMW-5-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-F11-WAGON-FACELIFT-01	4907	1860	1462
EU-BMW-5-F90-M5-CS-SEDAN-01	5001	1903	1468
EU-BMW-5-G30-SEDAN-FACELIFT-01	4963	1868	1479
EU-BMW-5-G30-SEDAN-M550D-01	4962	1868	1467
EU-BMW-5-G30-SEDAN-PREFL-01	4936	1868	1479
EU-BMW-5-G31-WAGON-FACELIFT-01	4963	1868	1498
EU-BMW-5-G31-WAGON-M550D-01	4962	1868	1488
EU-BMW-5-G31-WAGON-PREFL-01	4943	1868	1498
EU-BMW-502-SEDAN-01	4730	1780	1530
EU-BMW-507-CONVERTIBLE-01	4380	1680	1275
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525
EU-FIAT-500X-I-SUV-PREFL-01	4248	1796	1600
EU-HONDA-CR-V-V-SUV-01	4587	1854	1689
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	4785	1900	1710
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644
EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	4232	1803	1689
EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	4232	1803	1664
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700
EU-LAMBORGHINI-HURACAN-PERFORMANTE-COUPE-01	4506	1924	1165
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455
EU-SEAT-ATECA-I-SUV-PREFL-01	4363	1841	1601
EU-SEAT-LEON-III-5F-HATCHBACK-3D-FACELIFT-01	4247	1810	1446
EU-SEAT-LEON-III-5F-HATCHBACK-5D-FACELIFT-01	4282	1816	1459
EU-SEAT-LEON-III-5F-WAGON-FACELIFT-01	4549	1816	1454
EU-SKODA-OCTAVIA-III-HATCHBACK-FACELIFT-01	4670	1814	1461
EU-SKODA-OCTAVIA-III-HATCHBACK-PREFL-01	4659	1814	1461
EU-SKODA-OCTAVIA-III-WAGON-FACELIFT-01	4667	1814	1465
EU-SKODA-OCTAVIA-III-WAGON-PREFL-01	4659	1814	1465
EU-SKODA-OCTAVIA-IV-HATCHBACK-PREFL-01	4689	1829	1470
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468
EU-TOYOTA-COROLLA-VI-AE92-COUPE-01	4245	1665	1300
EU-TOYOTA-COROLLA-VIII-E110-SEDAN-01	4295	1690	1385
EU-TOYOTA-COROLLA-XI-E170-SEDAN-01	4620	1775	1465
EU-VOLVO-V90-II-CROSS-COUNTRY-WAGON-01	4939	1879	1543
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460
EU-VW-ARTEON-I-3H-LIFTBACK-PREFL-01	4862	1871	1450
EU-VW-CADDY-V-MPV-LWB-01	4853	1855	1800
EU-VW-CADDY-V-MPV-SWB-01	4500	1855	1798
EU-VW-CADDY-V-VAN-LWB-01	4853	1855	1860
EU-VW-CADDY-V-VAN-SWB-01	4500	1855	1856
EU-VW-GOLF-VIII-ALLTRACK-WAGON-01	4639	1795	1510
EU-VW-GOLF-VIII-VARIANT-WAGON-01	4633	1789	1498
EU-VW-POLO-III-6N1-HATCHBACK-01	3715	1655	1420
EU-VW-POLO-IV-9N2-SEDAN-01	4179	1650	1465
EU-VW-POLO-V-FACELIFT-CITYVAN-3D-01	3972	1682	1462
EU-VW-POLO-V-FACELIFT-CITYVAN-BLUEGT-3D-01	3972	1682	1453
EU-VW-POLO-VI-AW1-HATCHBACK-01	4053	1751	1446

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	Q3	45 Tfsi Quattro	SUV	Allrad	Benzin	180	245	Jan 2021	-	2024-03-01	143499
Audi	Q3	45 Tfsi Quattro	SUV	Allrad	Benzin	180	245	Jan 2021	-	2024-03-01	143500
Audi	Q5	SQ5 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	251	341	Jan 2021	-	2024-07-01	143501
Audi	Q5	35 TDI Mild Hybrid	SUV	Frontantrieb	Diesel/Elektro	120	163	Apr 2021	-	2024-03-01	143502
Audi	Q5	SQ5 TDI Mild Hybrid Quattro	SUV	Allrad	Diesel/Elektro	251	341	Feb 2021	-	2024-03-01	143503
Skoda	Octavia	2.0 TDI 4X4	Kombi	Allrad	Diesel	110	150	Sep 2020	-	2024-03-01	143518
Skoda	Octavia	2.0 TSI 4X4	Kombi	Allrad	Benzin	140	190	Sep 2020	-	2024-03-01	143519
VW	Golf viii	2.0 TDI GTD	Schrägheck	Frontantrieb	Diesel	147	200	Sep 2020	-	2024-03-01	143527
Seat	Ateca	2.0 TDI	SUV	Frontantrieb	Diesel	85	116	Jan 2021	-	2025-12-01	143531
Jeep	Compass	1.3	SUV	Frontantrieb	Benzin	110	150	Aug 2020	-	2024-03-01	143535
Cupra	Formentor	2.0 TDI	SUV	Frontantrieb	Diesel	110	150	Mar 2021	-	2024-03-01	143537
Cupra	Formentor	2.0 TDI 4drive	SUV	Allrad	Diesel	110	150	Mar 2021	-	2024-03-01	143539
Cupra	Formentor	1.4 E-hybrid	SUV	Frontantrieb	Benzin/Elektro	150	204	Jan 2021	-	2024-03-01	143541
Cupra	Formentor	2.0 TSI	SUV	Frontantrieb	Benzin	180	245	Mar 2021	-	2024-03-01	143542
Cupra	Formentor	1.4 E-hybrid VZ	SUV	Frontantrieb	Benzin/Elektro	180	245	Feb 2021	-	2025-02-03	143543
Cupra	Formentor	2.0 TSI 4drive	SUV	Allrad	Benzin	140	190	Aug 2020	-	2024-03-01	143544
Ford	Kuga iii	2.5 Fhev 4X4	SUV	Allrad	Benzin/Elektro	140	190	Jan 2021	-	2024-03-01	143547
Ford	Kuga iii	2.5 Fhev	SUV	Frontantrieb	Benzin/Elektro	140	190	Jan 2021	-	2024-03-01	143548
Alfa Romeo	Stelvio	2.0 Q4	SUV	Allrad	Benzin	184	250	Dec 2019	-	2024-03-01	143549
Seat	Tarraco	2.0 Tfsi 4drive	SUV	Allrad	Benzin	180	245	Jan 2021	May 2024	2025-06-01	143551
Volvo	V90 ii	B5 Mild Hybrid AWD	Kombi	Allrad	Diesel/Elektro	173	235	Dec 2020	-	2024-03-01	143552
Alpina	B8	Biturbo Allrad	Coupe	Allrad	Benzin	457	621	Mar 2021	Dec 2025	2026-06-01	143575
Mercedes-benz	C-Klasse	C 180	Stufenheck	Heckantrieb	Benzin/Elektro	125	170	Mar 2021	-	2024-03-01	143576
Mercedes-benz	C-Klasse	C 200	Stufenheck	Heckantrieb	Benzin/Elektro	150	204	Mar 2021	-	2024-03-01	143578
Mercedes-benz	C-Klasse	C 200 4-matic	Stufenheck	Allrad	Benzin/Elektro	150	204	Mar 2021	-	2024-03-01	143579
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel/Elektro	147	200	Mar 2021	-	2024-03-01	143580
Mercedes-benz	C-Klasse	C 300 D	Stufenheck	Heckantrieb	Diesel/Elektro	195	265	Mar 2021	-	2024-03-01	143581
BMW	5	520 E Plug-in-hybrid	Stufenheck	Heckantrieb	Benzin/Elektro	150	204	Mar 2021	May 2022	2024-03-01	143607
Ferrari	Portofino	3.9	Cabriolet	Heckantrieb	Benzin	456	620	Feb 2021	-	2024-03-01	143610
Audi	A6 c8	35 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	120	163	Nov 2020	-	2024-05-01	143622
Audi	A6 c8	40 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	150	204	Jul 2018	-	2024-03-01	143623
Audi	A6 c8 avant	35 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	120	163	Oct 2020	-	2024-05-01	143625
Mercedes-benz	C-Klasse	C 300 4-matic	Stufenheck	Allrad	Benzin/Elektro	190	258	Mar 2021	-	2024-03-01	143630
Mercedes-benz	C-Klasse	C 300	Stufenheck	Heckantrieb	Benzin/Elektro	190	258	Mar 2021	-	2024-03-01	143631
Mercedes-benz	C-Klasse	C 200	Kombi	Heckantrieb	Benzin/Elektro	150	204	Mar 2021	-	2024-03-01	143633
Mercedes-benz	C-Klasse	C 300 D	Kombi	Heckantrieb	Diesel/Elektro	195	265	Mar 2021	-	2024-03-01	143634
Mercedes-benz	C-Klasse	C 220 D	Kombi	Heckantrieb	Diesel/Elektro	147	200	Mar 2021	-	2024-03-01	143635
Maxus	Edeliver 9	Electric	Kasten	Frontantrieb	Elektro	150	204	Jul 2020	-	2024-03-01	143649
Seat	Leon	1.0 TSI Mild Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	81	110	Aug 2020	-	2024-03-01	143677
Seat	Leon	2.0 Tfsi	Schrägheck	Frontantrieb	Benzin	140	190	Mar 2021	-	2024-03-01	143678
Seat	Leon	1.0 TSI Mild Hybrid	Kombi	Frontantrieb	Benzin/Elektro	81	110	Aug 2020	-	2024-03-01	143680
Seat	Leon	2.0 TDI	Kombi	Frontantrieb	Diesel	85	116	Nov 2020	-	2025-12-01	143681
Piaggio	Porter np6	1.5 LPG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Autogas (LPG)	78	106	Jan 2021	-	2024-03-01	143695
Piaggio	Porter np6	1.5 CNG	Pritsche/Fahrgestell	Heckantrieb	Benzin/Erdgas (CNG)	78	106	Jan 2021	-	2024-03-01	143697
Opel	Insignia b grand sport	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	125	170	Aug 2020	-	2025-04-01	143717
Mercedes-benz	Cls	CLS 300 D 4-matic	Coupe	Allrad	Diesel/Elektro	195	265	Apr 2021	-	2024-03-01	143725
Mercedes-benz	E-Klasse	E 300 D 4-matic	Cabriolet	Allrad	Diesel/Elektro	195	265	Apr 2021	-	2024-03-01	143728
Mercedes-benz	E-Klasse	E 300 D 4-matic	Coupe	Allrad	Diesel/Elektro	195	265	Jan 2021	-	2024-03-01	143729
Hyundai	Santa fe iv	2.5 MPI	SUV	Frontantrieb	Benzin	132	180	Jul 2021	-	2024-03-01	143732
Mitsubishi	Space star vi	1.2	Schrägheck	Frontantrieb	Benzin	52	71	Aug 2020	-	2024-03-01	143733
Opel	Insignia b grand sport	2.0 Cdti	Schrägheck	Frontantrieb	Diesel	128	174	Apr 2021	-	2024-03-01	143737
Opel	Insignia b grand sport	2.0 Cdti 4X4	Schrägheck	Allrad	Diesel	128	174	Apr 2021	-	2024-03-01	143738
Honda	Cr-V v	2.0 E-cvt Hybrid AWD	SUV	Allrad	Benzin/Elektro	158	215	Feb 2019	Aug 2023	2025-06-01	143743
BMW	3	M3 Competition Xdrive	Stufenheck	Allrad	Benzin	375	510	May 2021	-	2024-03-01	143769
BMW	4	M4 Competition M Xdrive	Coupe	Allrad	Benzin	375	510	May 2021	Feb 2024	2024-05-01	143770
VW	Caddy v	2.0 TDI 4motion	Großraumlimousine	Allrad	Diesel	90	122	Mar 2021	-	2025-11-01	143775
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	110	150	Jul 2019	-	2024-03-01	143793
Mercedes-benz	S-Klasse	S 450 EQ Boost	Stufenheck	Heckantrieb	Benzin/Elektro	270	367	Jul 2021	-	2024-03-01	143798
VW	Caddy v	2.0 TDI 4motion	Kasten/Großraumlimousine	Allrad	Diesel	90	122	Mar 2021	-	2025-11-01	143809
Ford	Kuga iii	1.5 Ecoboost	SUV	Frontantrieb	Benzin	134	183	Sep 2019	-	2024-03-01	143819
Audi	A1	40 Tfsi	Schrägheck	Frontantrieb	Benzin	152	207	Apr 2021	-	2024-03-01	143831
VW	Arteon	1.4 Ehybrid	Schrägheck	Frontantrieb	Benzin/Elektro	160	218	Nov 2020	-	2024-03-01	143835
VW	Arteon	2.0 TSI R 4motion	Schrägheck	Allrad	Benzin	235	320	Nov 2020	-	2025-06-01	143836
VW	Arteon	2.0 TSI R 4motion	Kombi	Allrad	Benzin	235	320	Nov 2020	-	2025-11-01	143837
VW	Arteon	1.4 Ehybrid	Kombi	Frontantrieb	Benzin/Elektro	160	218	Nov 2020	-	2024-03-01	143838
Ford USA	Mustang mach-E	EV 4X4	Geländewagen geschlossen	Allrad	Elektro	216	294	Apr 2021	-	2024-05-01	143870
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	216	294	Apr 2021	-	2024-11-01	143871
Ford USA	Mustang mach-E	EV 4X4	Geländewagen geschlossen	Allrad	Elektro	342	465	Apr 2021	-	2024-05-01	143872
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	258	351	Apr 2021	-	2024-11-01	143873
Ford USA	Mustang mach-E	EV 4X4	SUV	Allrad	Elektro	198	269	Apr 2021	-	2024-11-01	143874
Ford USA	Mustang mach-E	EV	SUV	Heckantrieb	Elektro	198	269	Apr 2021	-	2024-11-01	143876
Polestar	Polestar 2	EV	Schrägheck	Frontantrieb	Elektro	170	231	Apr 2021	-	2024-03-01	143879
VW	Polo	GTI	Schrägheck	Frontantrieb	Benzin	152	207	Apr 2021	-	2024-03-01	143880
Maxus	T90	EV	Pick-up	Heckantrieb	Elektro	130	177	Mar 2021	-	2024-03-01	143943
Audi	A6 c8	50 Tfsi E Quattro	Stufenheck	Allrad	Benzin/Elektro	220	299	Feb 2021	-	2024-03-01	143949
Audi	A6 c8 avant	50 Tfsi E Quattro	Kombi	Allrad	Benzin/Elektro	220	299	Feb 2021	-	2024-03-01	143950
Audi	A6 c8 avant	45 TDI Quattro	Kombi	Allrad	Diesel	183	249	Jul 2019	-	2024-03-01	143951
Audi	A7 sportback	3.0 Tfsi Quattro	Schrägheck	Allrad	Benzin	250	340	May 2016	May 2018	2024-03-01	143953
Audi	A7 sportback	50 Tfsi E Quattro	Schrägheck	Allrad	Benzin/Elektro	220	299	Feb 2021	-	2025-06-01	143954
Citroën	C4 iii	Bluehdi 110	Schrägheck	Frontantrieb	Diesel	81	110	Dec 2020	-	2024-03-01	143961
Toyota	Corolla	1.3	Kombi	Frontantrieb	Benzin	65	88	Sep 2002	Aug 2007	2025-02-03	143981
Mercedes-benz	E-Klasse	E 250	Stufenheck	Heckantrieb	Benzin	150	204	May 2009	Dec 2011	2024-03-01	143996
Elaris	Finn	EV	Schrägheck	Frontantrieb	Elektro	35	48	Jan 2020	-	2024-03-01	144010
Fiat	500x	1.6 D Multijet	SUV	Frontantrieb	Diesel	96	130	May 2021	-	2024-03-01	144054
Audi	A4 b9 avant	S4 TDI Mild Hybrid Quattro	Kombi	Allrad	Diesel/Elektro	251	341	Jan 2021	-	2024-03-01	144058
Audi	A5	30 TDI Mild Hybrid	Cabriolet	Frontantrieb	Diesel/Elektro	100	136	Jul 2018	-	2024-03-01	144059
Audi	A5	S5 TDI Mild Hybrid Quattro	Coupe	Allrad	Diesel/Elektro	251	341	Jan 2021	-	2024-03-01	144060
Audi	A5	S5 TDI Mild Hybrid Quattro	Schrägheck	Allrad	Diesel/Elektro	251	341	Jan 2021	-	2024-03-01	144061
Audi	A6 c8	S6 TDI Mild Hybrid Quattro	Stufenheck	Allrad	Diesel/Elektro	253	344	Jan 2021	-	2024-03-01	144062
Audi	A6 c8	45 TDI Quattro	Stufenheck	Allrad	Diesel	183	249	Jul 2019	-	2024-03-01	144063
Audi	A6 c8	40 TDI	Stufenheck	Frontantrieb	Diesel	140	190	Feb 2019	-	2024-03-01	144064
Jeep	Gladiator	3.0 D 4WD	Pick-up	Allrad	Diesel	194	264	Apr 2021	-	2024-03-01	144083
VW	Golf viii	1.4 GTE Plug-in Hybrid	Schrägheck	Frontantrieb	Benzin/Elektro	180	245	Jul 2020	-	2024-03-01	144084
Lamborghini	Huracán	LP 640-2	Coupe	Heckantrieb	Benzin	470	640	Mar 2021	-	2024-03-01	144087
Audi	Q5	50 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	220	299	Feb 2021	-	2024-03-01	144107
Audi	Q5	50 Tfsi E Quattro	SUV	Allrad	Benzin/Elektro	220	299	Feb 2021	-	2024-03-01	144108
Jeep	Renegade	1.6 Multijet	SUV	Frontantrieb	Diesel	96	130	Feb 2020	-	2024-03-01	144112
Jeep	Renegade	1.3 Phev 4XE	SUV	Allrad	Benzin/Elektro	140	190	Aug 2020	-	2024-03-01	144113
Skoda	Scala	1.6 TDI	Schrägheck	Frontantrieb	Diesel	70	95	Sep 2019	-	2024-03-01	144116
KIA	Sorento iv	2.5 MPI	SUV	Frontantrieb	Benzin	132	180	Apr 2021	-	2024-03-01	144122


--- Round 1 / 首次发送 ---
## 更新点

* 已复用 11 个既有尺寸组，闭合 20 个 Ktype 映射。
* 新建 BMW 520e 专属尺寸组。官方技术规格确认其高度为 1483 mm，与既有普通 G30 改款三厢组的 1479 mm 不同，因此使用同系列下一序号 `-02`，未覆盖原尺寸组。
* 新建 Polestar 2 标准悬架尺寸组。官方规格分别列出不含后视镜宽度 1859 mm、含镜宽度 1985 mm，并区分标准悬架高度 1482 mm 与 Performance 高度 1477 mm。
* Jeep Compass 1.3、Volvo V90 B5 改款、Honda CR-V Hybrid AWD 和 Jeep Renegade 1.6 暂未复用已有组：当前版本尺寸与缓存存在差异或来源间高度冲突，继续保持 PENDING，不创建猜测性尺寸组。([汽车数据网][1])

## 当前批次进度

* READY 映射：22
* PENDING 映射：78
* 已确认尺寸组：13

  * 复用既有组：11
  * 本轮新增组：2
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143502	143502	SUV	Q5 II (FY)	FY	5	EU-AUDI-Q5-II-FY-SUV-02	HIGH	FY改款标准SUV外廓。	READY
143518	143518	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH	Octavia IV Combi四驱外廓。	READY
143519	143519	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH	Octavia IV Combi四驱外廓。	READY
143549	143549	SUV	Stelvio	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949标准SUV外廓。	READY
143607	143607	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-02	HIGH	G30改款520e PHEV增高外廓。	READY
143622	143622	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143623	143623	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143625	143625	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143717	143717	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143732	143732	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	TM改款标准SUV外廓。	READY
143737	143737	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143738	143738	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143835	143835	Hatchback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	3H改款五门liftback外廓。	READY
143879	143879	Hatchback	Polestar 2 I		5	EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	HIGH	五门fastback标准悬架外廓。	READY
143949	143949	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143950	143950	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143951	143951	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143961	143961	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41五门两厢外廓。	READY
144059	144059	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	F57双门敞篷外廓。	READY
144063	144063	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
144064	144064	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
144122	144122	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4标准SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-G30-SEDAN-FACELIFT-02	4963	1868	1483	BMW 5 Series Sedan 520e official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0328308IT/475174
EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	4606	1859	1482	Polestar 2 official specifications	https://www.polestar.com/dato-assets/11286/1622123441-specifications-ps2-uk.pdf
```

## 下一步优先处理

1. 闭合 SEAT Leon IV 两厢和 Sportstourer，并确认普通悬架与 FR 低悬架高度分支。
2. 处理 Audi Q3 F3、Q5 改款、SQ5 和 Q5 PHEV，避免把改款前尺寸组误用于改款版本。
3. 解决 CUPRA Formentor 官方规格表中的宽度及高度冲突。
4. 建立 Mercedes-Benz W206/S206、Ford Kuga III 和 Mustang Mach-E 高复用尺寸组。
5. 最后处理 Maxus、Piaggio、Caddy、Gladiator 等存在轴距、车顶、厢式或底盘分支的商用车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/jeep-compass-ii-mp-1.3-gse-t4-150hp-dct-50875?utm_source=chatgpt.com "Jeep Compass II (MP) 1.3 GSE T4 (150 Hp) DCT"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
ChatGPT 说：Unusual activity has been detected from your device. Try again later. (3d8b6f67-0e62-4a82-852e-1013c201739e)


--- 发送 / 推进信号纠偏 / Round 3 ---
你的上一轮回复缺少正常推进信号。继续当前批次：尺寸组首次建档后必须复用；仅输出本轮新增/修改的 Ktype 映射行和首次创建/修正的 DIMENSION_GROUP 行，无变化明确写“无”，并给出下一步优先处理。未完成输出“推进信号：CONTINUE”；只有同一回复包含两张最终完整表且全部映射闭合时才可 COMPLETE。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 22 个 Ktype：4 个直接复用既有尺寸组，18 个关联 8 个首次建档尺寸组。
* Audi Q3、改款 SQ5 与 Q5 TFSI e 均采用官方尺寸图；图中车身宽度和含后视镜宽度分别标注，已按不含后视镜口径落盘。
* CUPRA Formentor 闭合 4 套实际外廓；官方规格中的 2.0 TSI 245 宽度排版异常已由对应车型规格交叉闭合。
* 2021 款 Mustang Mach-E 官方欧洲规格显示 RWD、AWD、First Edition 与 GT 共用同一套外廓，本轮统一建组。([Ford From the Road][1])

## 当前批次进度

* READY 映射：44
* PENDING 映射：56
* 已确认尺寸组：25
* 本轮首次创建尺寸组：8
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143499	143499	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
143500	143500	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
143501	143501	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-02	HIGH	FY改款SQ5五门SUV外廓。	READY
143503	143503	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-02	HIGH	FY改款SQ5五门SUV外廓。	READY
143535	143535	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH	MP五门SUV外廓。	READY
143537	143537	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-FWD-01	HIGH	前驱五门SUV外廓。	READY
143539	143539	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-01	HIGH	4Drive柴油五门SUV外廓。	READY
143541	143541	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	HIGH	e-Hybrid五门SUV外廓。	READY
143542	143542	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-FWD-01	HIGH	前驱VZ五门SUV外廓。	READY
143543	143543	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	HIGH	e-Hybrid VZ五门SUV外廓。	READY
143544	143544	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-02	HIGH	4Drive汽油五门SUV外廓。	READY
143552	143552	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II标准旅行车外廓。	READY
143743	143743	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-01	HIGH	第五代Hybrid AWD五门SUV外廓。	READY
143870	143870	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143871	143871	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143872	143872	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	GT五门电动SUV外廓。	READY
143873	143873	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143874	143874	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143876	143876	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
144107	144107	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH	FY改款TFSI e五门SUV外廓。	READY
144108	144108	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH	FY改款TFSI e五门SUV外廓。	READY
144112	144112	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	BU前驱五门SUV外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Audi Q3 official dimensions	https://www.audi.com/de/publikationen/abmessungen/abmessungen-q3-1413/download
EU-AUDI-Q5-II-FY-SQ5-SUV-02	4682	1893	1635	Audi SQ5 TDI official dimensions	https://www.audi.com/de/publikationen/abmessungen/abmessungen-sq5-tdi-bis-2024-1604/download
EU-CUPRA-FORMENTOR-I-SUV-FWD-01	4446	1839	1520	CUPRA Formentor 2022 official technical specifications; Automobile-Catalog 2022 CUPRA Formentor VZ 2.0 TSI 245	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf;https://www.automobile-catalog.com/car/2022/3103220/cupra_formentor_vz_2_0_tsi_245_dsg.html
EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-01	4450	1839	1520	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	4450	1839	1510	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-02	4450	1839	1511	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-FORD-MUSTANG-MACH-E-I-SUV-01	4713	1881	1625	Ford Mustang Mach-E 2021 official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2020/12/Mach-E_AWD/Ford_Mustang_Mach-E_2020_TechSpecs_EU.pdf
EU-AUDI-Q5-II-FY-PHEV-SUV-01	4682	1893	1652	Audi Q5 TFSI e official dimensions	https://media.audi.com/is/content/audi/country/ch/assets/dimensions/q5/Q5-TFSI-e-PA-Abmessungen.pdf
```

## 下一步优先处理

1. 闭合 SEAT Leon IV 两厢、Sportstourer 与 VW Golf VIII 两厢车型族。
2. 集中建立 Mercedes-Benz W206、S206、C238、A238 与 C257 尺寸组。
3. 批量处理 Ford Kuga III、Audi A4/A5/A7 和 Arteon Shooting Brake。
4. 最后处理 Maxus eDeliver 9、Caddy V、Piaggio Porter NP6 与 Jeep Gladiator 的轴距、车顶及底盘分支。

推进信号：CONTINUE

[1]: https://media.ford.com/content/dam/fordmedia/Europe/en/2020/12/Mach-E_AWD/Ford_Mustang_Mach-E_2020_TechSpecs_EU.pdf "Technical Specifications (pdf)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 17 个输入 Ktype，共新增 20 条 READY 映射行。
* SEAT Leon IV 按普通悬架与 FR 低悬架拆分：五门两厢高度分别为 1456/1442 mm，Sportstourer 分别为 1448/1437 mm；对应发动机在普通配置与 FR 配置中的覆盖关系已同步拆分。
* Mercedes-Benz W206 三厢和 S206 旅行车分别建组；宽度均采用官方明确标注的不含后视镜 1820 mm。
* Golf VIII GTD 与 GTE 因长度、高度不同分别建组；Audi A1 GB 使用官方尺寸图建组。([汽车数据网][1])

## 当前批次进度

* READY 输入 Ktype：61
* READY 映射行：64
* PENDING 输入 Ktype：39
* 已确认尺寸组：34
* 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143527	143527	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-GTD-01	HIGH	GTD五门运动悬架外廓。	READY
143576	143576	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143578	143578	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143579	143579	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143580	143580	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143581	143581	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143630	143630	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143631	143631	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143633	143633	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143634	143634	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143635	143635	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143677_standard	143677	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	普通悬架五门外廓。	READY
143677_fr	143677	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低悬架五门外廓。	READY
143678	143678	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	2.0 TSI FR五门外廓。	READY
143680_standard	143680	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	普通悬架Sportstourer外廓。	READY
143680_fr	143680	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架Sportstourer外廓。	READY
143681_standard	143681	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	普通悬架Sportstourer外廓。	READY
143681_fr	143681	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架Sportstourer外廓。	READY
143831	143831	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	GB五门Sportback外廓。	READY
144084	144084	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-GTE-01	HIGH	GTE五门插混外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-GOLF-VIII-HATCHBACK-GTD-01	4287	1789	1478	Auto-Data Volkswagen Golf VIII GTD 2.0 TDI 200	https://www.auto-data.net/en/volkswagen-golf-viii-gtd-2.0-tdi-200hp-dsg-41548
EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	4751	1820	1437	Mercedes-Benz C-Class Saloon official dimensions	https://www.mercedes-benz-mena.com/static/pdfs/c-klasse-w206-epaper-24-2-02-eng.pdf
EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	4751	1820	1455	Mercedes-Benz C-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/c-class/overview.html
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1800	1456	SEAT Leon official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1800	1442	SEAT Leon official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1448	SEAT Leon Sportstourer official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	SEAT Leon Sportstourer official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Audi A1 Sportback official dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-a1-sportback-1382/download
EU-VW-GOLF-VIII-HATCHBACK-GTE-01	4287	1789	1484	Volkswagen Golf GTE official technical data	https://www.volkswagen-newsroom.com/en/golf-etsi-golf-ehybrid-and-golf-gte-international-media-drive-6336/the-technical-data-of-the-new-golf-hybrid-models-6344
```

## 下一步优先处理

1. 闭合 Audi A4/A5/A7、Arteon R 与 Shooting Brake 车型族。
2. 集中处理 Mercedes-Benz CLS C257、E-Class C238/A238、S-Class W223。
3. 处理 BMW G80/G82、Ferrari Portofino M、Lamborghini Huracán LP 640-2。
4. 最后核对 Caddy V、eDeliver 9、Porter NP6、Gladiator、T90 等多轴距或商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/volkswagen-golf-viii-gtd-2.0-tdi-200hp-dsg-41548 "Volkswagen Golf VIII GTD 2.0 TDI (200 Hp) DSG | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 7 个 Ktype：6 个首次建组，1 个复用既有尺寸组。
* BMW 官方规格确认 G80 M3 Competition 外廓为 4794 × 1903 × 1433 mm，G82 M4 Competition 为 4794 × 1887 × 1393 mm。
* Volkswagen 官方技术数据确认 Arteon R Liftback 与 Shooting Brake 长宽相同，高度分别为 1460 mm 和 1462 mm。([Volkswagen Newsroom][1])
* ALPINA 官方资料分别列出 B8 车身宽度 1932 mm 与含后视镜宽度 2137 mm；Ferrari 官方技术表也将 Portofino M 的 1938 mm 车身宽度与 2020 mm 展开后视镜宽度分开列示。([阿尔皮纳汽车][2])

## 当前批次进度

* READY 输入 Ktype：68
* READY 映射行：71
* PENDING 输入 Ktype：32
* 已确认尺寸组：40
* 本轮首次创建尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143575	143575	Coupe	B8 Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupé外廓。	READY
143610	143610	Convertible	Portofino M		2	EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	HIGH	Portofino M双门敞篷外廓。	READY
143769	143769	Sedan	M3 G80	G80	4	EU-BMW-M3-G80-SEDAN-01	HIGH	G80四门三厢外廓。	READY
143770	143770	Coupe	M4 G82	G82	2	EU-BMW-M4-G82-COUPE-01	HIGH	G82双门轿跑外廓。	READY
143836	143836	Hatchback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-R-01	HIGH	改款R五门liftback外廓。	READY
143837	143837	Wagon	Arteon I	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-R-01	HIGH	R版Shooting Brake外廓。	READY
144113	144113	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	HIGH	BU 4xe四驱五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALPINA-B8-G16-GRAN-COUPE-01	5092	1932	1428	BMW ALPINA B8 Gran Coupé official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2021_03_INT/B8/epaper/ausgabe.pdf
EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	4594	1938	1318	Ferrari Portofino M official technical specifications	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/cs_ferrari_portofino_m_full_gbr_def.pdf
EU-BMW-M3-G80-SEDAN-01	4794	1903	1433	BMW M3 Competition Sedan official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326323EN/472229
EU-BMW-M4-G82-COUPE-01	4794	1887	1393	BMW M4 Competition Coupé official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326324EN/472231
EU-VW-ARTEON-I-3H-LIFTBACK-R-01	4866	1871	1460	Volkswagen Arteon R official technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-R-01	4866	1871	1462	Volkswagen Arteon R Shooting Brake official technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
```

## 下一步优先处理

1. 闭合 Mercedes-Benz CLS C257、E-Class C238/A238 与 S-Class W223。
2. 处理 Audi A4、A5、A7 及 Arteon eHybrid Shooting Brake。
3. 集中核对 Ford Kuga III、SEAT Ateca/Tarraco 和 Mitsubishi Space Star。
4. 最后处理 Caddy V、Maxus eDeliver 9/T90、Piaggio Porter NP6、Jeep Gladiator等多轴距或商用车分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015 "Technical data | Volkswagen Newsroom"
[2]: https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2021_03_INT/B8/epaper/ausgabe.pdf?utm_source=chatgpt.com "ALPINA

MANUFACTURER OF
EXCLUSIVE AUTOMOBILESB M W"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮闭合 11 个 Ktype，全部按首次建组规则保存三维和来源。
* Audi A7、Arteon Shooting Brake、Kuga 等来源同时列出车身宽度和含后视镜宽度，本轮统一采用不含后视镜口径。([汽车数据][1])
* Lamborghini Huracán `LP 640-2` 根据后驱、640 PS 与投产时间识别为 Huracán STO，并建立独立外廓组。([Lamborghini.com][2])

## 当前批次进度

* READY 输入 Ktype：79
* READY 映射行：82
* PENDING 输入 Ktype：21
* 已确认尺寸组：51
* 本轮首次创建尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143531	143531	SUV	Ateca I		5	EU-SEAT-ATECA-I-FACELIFT-SUV-01	HIGH	改款五门SUV外廓。	READY
143547	143547	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-FHEV-AWD-01	HIGH	FHEV四驱五门SUV外廓。	READY
143551	143551	SUV	Tarraco I		5	EU-SEAT-TARRACO-I-SUV-01	HIGH	五门SUV外廓。	READY
143725	143725	Coupe	CLS C257	C257	4	EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	HIGH	C257改款四门轿跑外廓。	READY
143728	143728	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷外廓。	READY
143729	143729	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑外廓。	READY
143733	143733	Hatchback	Space Star VI		5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-FACELIFT-01	MEDIUM	2019改款五门两厢外廓。	READY
143838	143838	Wagon	Arteon I	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	HIGH	eHybrid Shooting Brake外廓。	READY
143954	143954	Hatchback	A7 C8		5	EU-AUDI-A7-C8-LIFTBACK-PHEV-01	HIGH	插混五门liftback外廓。	READY
144087	144087	Coupe	Huracán STO		2	EU-LAMBORGHINI-HURACAN-STO-COUPE-01	HIGH	STO后驱双门轿跑外廓。	READY
144116	144116	Hatchback	Scala I		5	EU-SKODA-SCALA-I-HATCHBACK-01	MEDIUM	五门两厢外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-SEAT-ATECA-I-FACELIFT-SUV-01	4381	1841	1615	Auto-Data SEAT Ateca I facelift 2.0 TDI 115	https://www.auto-data.net/en/seat-ateca-i-facelift-2020-2.0-tdi-115hp-43832
EU-FORD-KUGA-III-SUV-FHEV-AWD-01	4614	1883	1658	Auto-Data Ford Kuga III 2.5 FHEV i-AWD	https://www.auto-data.net/en/ford-kuga-iii-2.5-duratec-190hp-fhev-i-awd-cvt-41723
EU-SEAT-TARRACO-I-SUV-01	4735	1839	1674	AutoData1 SEAT Tarraco 2.0 TSI 245 4Drive	https://www.autodata1.com/en/car/seat/tarraco/tarraco-20-tsi-245-hp-4drive-dsg-7-seat
EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 facelift CLS 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-facelift-2021-cls-300d-265hp-mild-hybrid-4matic-9g-tronic-43348
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class A238 facelift E 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43739
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E-Class C238 facelift E 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43738
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-FACELIFT-01	3845	1665	1505	Auto-Data Mitsubishi Space Star facelift 1.2	https://www.auto-data.net/en/mitsubishi-space-star-facelift-2019-1.2-mivec-80hp-39342
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	4866	1871	1450	Auto-Data Volkswagen Arteon Shooting Brake eHybrid	https://www.auto-data.net/en/volkswagen-arteon-shooting-brake-facelift-2020-1.4-tsi-218hp-ehybrid-dsg-41796
EU-AUDI-A7-C8-LIFTBACK-PHEV-01	4969	1908	1421	Auto-Data Audi A7 C8 50 TFSI e	https://www.auto-data.net/en/audi-a7-sportback-c8-50-tfsi-e-299hp-plug-in-hybrid-quattro-ultra-s-tronic-45397
EU-LAMBORGHINI-HURACAN-STO-COUPE-01	4549	1945	1220	Lamborghini Huracán STO official model page; Auto-Data Lamborghini Huracán STO dimensions	https://www.lamborghini.com/en-en/history/huracan-sto;https://www.auto-data.net/en/lamborghini-huracan-sto-facelift-2020-5.2-v10-640hp-ldf-41726
EU-SKODA-SCALA-I-HATCHBACK-01	4362	1793	1471	Auto-Data Škoda Scala 1.6 TDI	https://www.auto-data.net/en/skoda-scala-1.6-tdi-115hp-35204
```

## 下一步优先处理

1. 闭合 Audi A4 Avant、A5 S5 Coupe/Sportback、A6 S6 和早期 A7 Sportback。
2. 处理 Mercedes-Benz S-Class W223、E-Class W212 与 VW Polo GTI。
3. 处理 Fiat 500X、Toyota Corolla Wagon、Elaris Finn。
4. 最后集中处理 Caddy V、Maxus eDeliver 9/T90、Piaggio Porter NP6、Jeep Gladiator等多轴距或多车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-kuga-iii-2.5-duratec-190hp-fhev-i-awd-cvt-41723 "Ford Kuga III 2.5 Duratec (190 Hp) FHEV i-AWD CVT | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.lamborghini.com/en-en/history/huracan-sto?utm_source=chatgpt.com "Lamborghini Huracán STO"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 本轮闭合 14 个输入 Ktype，新增 19 条 READY 映射。
* Caddy V 的乘用版、厢式版及 SWB/LWB 分支全部复用已有 4 个尺寸组，未重复输出尺寸和来源。
* Fiat 500X 1.6 MultiJet 130 同时覆盖 Sport 与 Cross，两者外廓不同，本轮拆为两个物理分支。Sport 来源明确标注宽度不含后视镜。([汽车目录][1])
* Audi S4、S5、S6 及 A7 来源分别列出车身宽度与含后视镜宽度，本轮采用前者。([汽车数据][2])
* Jeep Gladiator 的当前可靠来源只给出 `1843–1905 mm` 高度范围，尚不能落盘单一高度或完整分支，因此继续保持 PENDING。([汽车数据][3])

## 当前批次进度

* READY 输入 Ktype：93
* READY 映射行：101
* PENDING 输入 Ktype：7
* 已确认尺寸组：64
* 本轮首次创建尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143775_swb	143775	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	HIGH	SWB乘用版外廓。	READY
143775_lwb	143775	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	HIGH	LWB乘用版外廓。	READY
143798	143798	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	HIGH	W223标准轴距四门三厢外廓。	READY
143809_mpv_swb	143809	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	MEDIUM	SWB乘用版外廓。	READY
143809_mpv_lwb	143809	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	MEDIUM	LWB乘用版外廓。	READY
143809_van_swb	143809	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-SWB-01	MEDIUM	SWB厢式版外廓。	READY
143809_van_lwb	143809	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-LWB-01	MEDIUM	LWB厢式版外廓。	READY
143880	143880	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-GTI-HATCHBACK-FACELIFT-01	HIGH	改款GTI五门两厢外廓。	READY
143943	143943	Pickup	T90 I		4	EU-MAXUS-T90-EV-PICKUP-01	HIGH	双排座标准货箱电动皮卡外廓。	READY
143953	143953	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-LIFTBACK-FACELIFT-01	HIGH	C7改款五门Sportback外廓。	READY
143981	143981	Wagon	Corolla IX (E120)	NZE120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-01	HIGH	NZE120五门旅行车外廓。	READY
143996	143996	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	W212改款前四门三厢外廓。	READY
144010	144010	Hatchback	Finn I		3	EU-ELARIS-FINN-I-HATCHBACK-01	HIGH	三门双座微型两厢外廓。	READY
144054_sport	144054	SUV	500X I	334	5	EU-FIAT-500X-I-334-SUV-FACELIFT-SPORT-01	MEDIUM	Sport低悬架外廓分支。	READY
144054_cross	144054	SUV	500X I	334	5	EU-FIAT-500X-I-334-SUV-FACELIFT-CROSS-01	MEDIUM	Cross外廓分支。	READY
144058	144058	Wagon	S4 B9	8W5	5	EU-AUDI-S4-B9-8W5-WAGON-FACELIFT-01	HIGH	B9改款S4 Avant外廓。	READY
144060	144060	Coupe	S5 F5	F53	2	EU-AUDI-S5-F5-F53-COUPE-FACELIFT-01	HIGH	F5改款双门轿跑外廓。	READY
144061	144061	Hatchback	S5 F5	F5A	5	EU-AUDI-S5-F5-F5A-SPORTBACK-FACELIFT-01	HIGH	F5改款五门Sportback外廓。	READY
144062	144062	Sedan	S6 C8	4A2	4	EU-AUDI-S6-C8-4A2-SEDAN-01	HIGH	C8 S6四门三厢外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	5179	1954	1503	Auto-Data Mercedes-Benz S-Class W223 model specifications; Auto-Data Mercedes-Benz S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-model-1394;https://www.auto-data.net/en/mercedes-benz-s-class-w223-s-450-367hp-eq-boost-4matic-9g-tronic-41083
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-FACELIFT-01	4074	1751	1431	Auto-Data Volkswagen Polo VI facelift GTI 2.0 TSI 207	https://www.auto-data.net/en/volkswagen-polo-vi-facelift-2021-gti-2.0-tsi-207hp-dsg-44419
EU-MAXUS-T90-EV-PICKUP-01	5365	1900	1809	Auto-Data Maxus T90 Standard box EV 88.55 kWh 177	https://www.auto-data.net/en/maxus-t90-standard-box-ev-88.55-kwh-177hp-46828
EU-AUDI-A7-C7-4G8-LIFTBACK-FACELIFT-01	4974	1911	1420	Auto-Data Audi A7 Sportback C7 facelift 3.0 TFSI quattro	https://www.auto-data.net/en/audi-a7-sportback-c7-facelift-2014-3.0-tfsi-v6-333hp-quattro-s-tronic-22438
EU-TOYOTA-COROLLA-IX-E120-WAGON-01	4410	1710	1520	Auto-Data Toyota Corolla Wagon IX E120/E130	https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-generation-820
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	4868	1854	1470	Auto-Data Mercedes-Benz E-Class W212 E 250 CGI	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-ELARIS-FINN-I-HATCHBACK-01	2871	1563	1568	Auto-Data Elaris Finn 31.5 kWh 48	https://www.auto-data.net/en/elaris-finn-31.5-kwh-48hp-50309
EU-FIAT-500X-I-334-SUV-FACELIFT-SPORT-01	4264	1796	1582	Automobile-Catalog 2021 Fiat 500X 1.6 MultiJet 130 Sport	https://www.automobile-catalog.com/car/2021/3045440/fiat_500x_1_6_multijet_130_4x2_sport.html
EU-FIAT-500X-I-334-SUV-FACELIFT-CROSS-01	4269	1796	1603	Automobile-Catalog 2021 Fiat 500X 1.6 MultiJet 130 Cross; Auto-Data Fiat 500X Cross facelift generation	https://www.automobile-catalog.com/car/2021/3045380/fiat_500x_1_6_multijet_130_4x2_cross.html;https://www.auto-data.net/en/fiat-500x-model-3415
EU-AUDI-S4-B9-8W5-WAGON-FACELIFT-01	4770	1847	1433	Auto-Data Audi S4 Avant B9 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s4-avant-b9-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47368
EU-AUDI-S5-F5-F53-COUPE-FACELIFT-01	4705	1846	1368	Auto-Data Audi S5 Coupe F5 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s5-coupe-f5-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47390
EU-AUDI-S5-F5-F5A-SPORTBACK-FACELIFT-01	4765	1843	1395	Auto-Data Audi S5 Sportback F5 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s5-sportback-f5-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47394
EU-AUDI-S6-C8-4A2-SEDAN-01	4954	1886	1446	Auto-Data Audi S6 C8 3.0 TDI	https://www.auto-data.net/en/audi-s6-c8-3.0-tdi-v6-344hp-mild-hybrid-quattro-tiptronic-47372
```

## 下一步优先处理

1. 闭合 Ford Kuga III 的 `143548`、`143793`、`143819`，确认 FHEV 前驱及 EcoBoost 的实际高度分支。
2. 拆分 Maxus eDeliver 9 `143649` 的轴距和车顶组合。
3. 拆分 Piaggio Porter NP6 `143695`、`143697` 的轴距、单后轮和双后轮底盘。
4. 解决 Jeep Gladiator `144083` 的车型配置与车顶高度范围，避免将范围值强行落盘。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2021/3045380/fiat_500x_1_6_multijet_130_4x2_cross.html?utm_source=chatgpt.com "2021 Fiat 500X 1.6 MultiJet 130 4x2 Cross Specs Review (95.5 kW / 130 PS / 128 hp) (since mid-year 2021 for Europe )"
[2]: https://www.auto-data.net/en/audi-s4-avant-b9-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47368 "Audi S4 Avant (B9, facelift 2019) 3.0 TDI V6 (341 Hp) Mild Hybrid quattro tiptronic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/jeep-gladiator-jt-3.0-multijet-v6-264hp-4wd-automatic-43243 "Jeep Gladiator (JT) 3.0 Multijet V6 (264 Hp) 4WD Automatic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 剩余 7 个 Ktype 已全部闭合，本轮新增 32 条 READY 映射和 17 个尺寸组。
* Kuga III 按标准外观、ST-Line、Vignale 外廓拆分；eDeliver 9 按 L2H2/L3H2 拆分；Porter NP6 按货台/底盘、轴距及 SRW/DRW 拆分；Gladiator 按硬顶/软顶拆分。([Vanparison Leasing][1])
* 已完成唯一一次机械检查：表头正确、id 唯一、尺寸组 ID 唯一、引用完全闭合、尺寸和来源字段非空、下载文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* 最终映射行：133
* 最终尺寸组：86
* PENDING：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
143499	143499	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
143500	143500	SUV	Q3 II	F3	5	EU-AUDI-Q3-II-F3-SUV-01	HIGH	F3五门SUV外廓。	READY
143501	143501	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-02	HIGH	FY改款SQ5五门SUV外廓。	READY
143502	143502	SUV	Q5 II (FY)	FY	5	EU-AUDI-Q5-II-FY-SUV-02	HIGH	FY改款标准SUV外廓。	READY
143503	143503	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-SQ5-SUV-02	HIGH	FY改款SQ5五门SUV外廓。	READY
143518	143518	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH	Octavia IV Combi四驱外廓。	READY
143519	143519	Wagon	Octavia IV	NX5	5	EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	HIGH	Octavia IV Combi四驱外廓。	READY
143527	143527	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-GTD-01	HIGH	GTD五门运动悬架外廓。	READY
143531	143531	SUV	Ateca I		5	EU-SEAT-ATECA-I-FACELIFT-SUV-01	HIGH	改款五门SUV外廓。	READY
143535	143535	SUV	Compass II	MP	5	EU-JEEP-COMPASS-II-MP-SUV-01	HIGH	MP五门SUV外廓。	READY
143537	143537	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-FWD-01	HIGH	前驱五门SUV外廓。	READY
143539	143539	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-01	HIGH	4Drive柴油五门SUV外廓。	READY
143541	143541	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	HIGH	e-Hybrid五门SUV外廓。	READY
143542	143542	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-FWD-01	HIGH	前驱VZ五门SUV外廓。	READY
143543	143543	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	HIGH	e-Hybrid VZ五门SUV外廓。	READY
143544	143544	SUV	Formentor I		5	EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-02	HIGH	4Drive汽油五门SUV外廓。	READY
143547	143547	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-FHEV-AWD-01	HIGH	FHEV四驱五门SUV外廓。	READY
143548_stline	143548	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-STLINE-01	HIGH	FHEV前驱ST-Line外廓。	READY
143548_vignale	143548	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	FHEV前驱Vignale外廓。	READY
143549	143549	SUV	Stelvio	949	5	EU-ALFA-ROMEO-STELVIO-949-SUV-01	HIGH	949标准SUV外廓。	READY
143551	143551	SUV	Tarraco I		5	EU-SEAT-TARRACO-I-SUV-01	HIGH	五门SUV外廓。	READY
143552	143552	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-01	HIGH	V90 II标准旅行车外廓。	READY
143575	143575	Coupe	B8 Gran Coupé	G16	4	EU-ALPINA-B8-G16-GRAN-COUPE-01	HIGH	G16四门Gran Coupé外廓。	READY
143576	143576	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143578	143578	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143579	143579	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143580	143580	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143581	143581	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143607	143607	Sedan	5 Series G30	G30	4	EU-BMW-5-G30-SEDAN-FACELIFT-02	HIGH	G30改款520e PHEV增高外廓。	READY
143610	143610	Convertible	Portofino M		2	EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	HIGH	Portofino M双门敞篷外廓。	READY
143622	143622	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143623	143623	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143625	143625	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143630	143630	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143631	143631	Sedan	C-Class W206	W206	4	EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	HIGH	W206四门三厢外廓。	READY
143633	143633	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143634	143634	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143635	143635	Wagon	C-Class S206	S206	5	EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	HIGH	S206五门旅行车外廓。	READY
143649_l2h2	143649	Van	eDeliver 9 I			EU-MAXUS-EDELIVER-9-I-VAN-L2H2-01	HIGH	中轴中顶厢式车外廓。	READY
143649_l3h2	143649	Van	eDeliver 9 I			EU-MAXUS-EDELIVER-9-I-VAN-L3H2-01	HIGH	长轴中顶厢式车外廓。	READY
143677_standard	143677	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	HIGH	普通悬架五门外廓。	READY
143677_fr	143677	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	FR低悬架五门外廓。	READY
143678	143678	Hatchback	Leon IV	KL1	5	EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	HIGH	2.0 TSI FR五门外廓。	READY
143680_standard	143680	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	普通悬架Sportstourer外廓。	READY
143680_fr	143680	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架Sportstourer外廓。	READY
143681_standard	143681	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	HIGH	普通悬架Sportstourer外廓。	READY
143681_fr	143681	Wagon	Leon IV	KL8	5	EU-SEAT-LEON-IV-KL8-WAGON-FR-01	HIGH	FR低悬架Sportstourer外廓。	READY
143695_flatbed_srw_wb2650	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB2650-01	HIGH	短轴单后轮固定货台外廓。	READY
143695_flatbed_srw_wb3070_std	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-STDBED-01	HIGH	长轴单后轮标准货台外廓。	READY
143695_flatbed_srw_wb3070_long	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-LONGBED-01	HIGH	长轴单后轮加长货台外廓。	READY
143695_flatbed_drw_wb3000_std	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-STDBED-01	HIGH	双后轮标准货台外廓。	READY
143695_flatbed_drw_wb3000_long	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-LONGBED-01	HIGH	双后轮加长货台外廓。	READY
143695_flatbed_drw_wb3250	143695	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3250-01	HIGH	超长轴双后轮固定货台外廓。	READY
143695_chassis_srw_wb2650	143695	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB2650-01	HIGH	短轴单后轮底盘驾驶室外廓。	READY
143695_chassis_srw_wb3070	143695	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB3070-01	HIGH	长轴单后轮底盘驾驶室外廓。	READY
143695_chassis_drw_wb3000	143695	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3000-01	HIGH	长轴双后轮底盘驾驶室外廓。	READY
143695_chassis_drw_wb3250	143695	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3250-01	HIGH	超长轴双后轮底盘驾驶室外廓。	READY
143697_flatbed_srw_wb2650	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB2650-01	HIGH	短轴单后轮固定货台外廓。	READY
143697_flatbed_srw_wb3070_std	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-STDBED-01	HIGH	长轴单后轮标准货台外廓。	READY
143697_flatbed_srw_wb3070_long	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-LONGBED-01	HIGH	长轴单后轮加长货台外廓。	READY
143697_flatbed_drw_wb3000_std	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-STDBED-01	HIGH	双后轮标准货台外廓。	READY
143697_flatbed_drw_wb3000_long	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-LONGBED-01	HIGH	双后轮加长货台外廓。	READY
143697_flatbed_drw_wb3250	143697	Pickup	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3250-01	HIGH	超长轴双后轮固定货台外廓。	READY
143697_chassis_srw_wb2650	143697	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB2650-01	HIGH	短轴单后轮底盘驾驶室外廓。	READY
143697_chassis_srw_wb3070	143697	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB3070-01	HIGH	长轴单后轮底盘驾驶室外廓。	READY
143697_chassis_drw_wb3000	143697	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3000-01	HIGH	长轴双后轮底盘驾驶室外廓。	READY
143697_chassis_drw_wb3250	143697	Chassis Cab	Porter NP6	NP6	2	EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3250-01	HIGH	超长轴双后轮底盘驾驶室外廓。	READY
143717	143717	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143725	143725	Coupe	CLS C257	C257	4	EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	HIGH	C257改款四门轿跑外廓。	READY
143728	143728	Convertible	E-Class A238	A238	2	EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	HIGH	A238改款双门敞篷外廓。	READY
143729	143729	Coupe	E-Class C238	C238	2	EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	HIGH	C238改款双门轿跑外廓。	READY
143732	143732	SUV	Santa Fe IV	TM	5	EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	HIGH	TM改款标准SUV外廓。	READY
143733	143733	Hatchback	Space Star VI		5	EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-FACELIFT-01	MEDIUM	2019改款五门两厢外廓。	READY
143737	143737	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143738	143738	Hatchback	Insignia B	Z18	5	EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	HIGH	Grand Sport五门liftback外廓。	READY
143743	143743	SUV	CR-V V		5	EU-HONDA-CR-V-V-SUV-01	HIGH	第五代Hybrid AWD五门SUV外廓。	READY
143769	143769	Sedan	M3 G80	G80	4	EU-BMW-M3-G80-SEDAN-01	HIGH	G80四门三厢外廓。	READY
143770	143770	Coupe	M4 G82	G82	2	EU-BMW-M4-G82-COUPE-01	HIGH	G82双门轿跑外廓。	READY
143775_swb	143775	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	HIGH	SWB乘用版外廓。	READY
143775_lwb	143775	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	HIGH	LWB乘用版外廓。	READY
143793_standard	143793	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-STANDARD-01	HIGH	EcoBoost标准外观外廓。	READY
143793_stline	143793	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-STLINE-01	HIGH	EcoBoost ST-Line外廓。	READY
143793_vignale	143793	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	HIGH	EcoBoost Vignale外廓。	READY
143798	143798	Sedan	S-Class W223	W223	4	EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	HIGH	W223标准轴距四门三厢外廓。	READY
143809_mpv_swb	143809	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-SWB-01	MEDIUM	SWB乘用版外廓。	READY
143809_mpv_lwb	143809	MPV	Caddy V	SB	5	EU-VW-CADDY-V-MPV-LWB-01	MEDIUM	LWB乘用版外廓。	READY
143809_van_swb	143809	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-SWB-01	MEDIUM	SWB厢式版外廓。	READY
143809_van_lwb	143809	Van	Caddy V	SB		EU-VW-CADDY-V-VAN-LWB-01	MEDIUM	LWB厢式版外廓。	READY
143819_standard	143819	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-STANDARD-01	MEDIUM	183 hp前驱标准外观分支。	READY
143819_stline	143819	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-STLINE-01	MEDIUM	183 hp前驱ST-Line分支。	READY
143819_vignale	143819	SUV	Kuga III		5	EU-FORD-KUGA-III-SUV-VIGNALE-01	MEDIUM	183 hp前驱Vignale分支。	READY
143831	143831	Hatchback	A1 II	GB	5	EU-AUDI-A1-GB-HATCHBACK-01	HIGH	GB五门Sportback外廓。	READY
143835	143835	Hatchback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	HIGH	3H改款五门liftback外廓。	READY
143836	143836	Hatchback	Arteon I	3H	5	EU-VW-ARTEON-I-3H-LIFTBACK-R-01	HIGH	改款R五门liftback外廓。	READY
143837	143837	Wagon	Arteon I	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-R-01	HIGH	R版Shooting Brake外廓。	READY
143838	143838	Wagon	Arteon I	3H	5	EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	HIGH	eHybrid Shooting Brake外廓。	READY
143870	143870	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143871	143871	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143872	143872	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	GT五门电动SUV外廓。	READY
143873	143873	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143874	143874	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143876	143876	SUV	Mustang Mach-E I		5	EU-FORD-MUSTANG-MACH-E-I-SUV-01	HIGH	标准五门电动SUV外廓。	READY
143879	143879	Hatchback	Polestar 2 I		5	EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	HIGH	五门fastback标准悬架外廓。	READY
143880	143880	Hatchback	Polo VI	AW1	5	EU-VW-POLO-VI-AW1-GTI-HATCHBACK-FACELIFT-01	HIGH	改款GTI五门两厢外廓。	READY
143943	143943	Pickup	T90 I		4	EU-MAXUS-T90-EV-PICKUP-01	HIGH	双排座标准货箱电动皮卡外廓。	READY
143949	143949	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
143950	143950	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143951	143951	Wagon	A6 C8	4A5	5	EU-AUDI-A6-C8-4A5-WAGON-01	HIGH	C8 4A5 Avant外廓。	READY
143953	143953	Hatchback	A7 C7	4G8	5	EU-AUDI-A7-C7-4G8-LIFTBACK-FACELIFT-01	HIGH	C7改款五门Sportback外廓。	READY
143954	143954	Hatchback	A7 C8		5	EU-AUDI-A7-C8-LIFTBACK-PHEV-01	HIGH	插混五门liftback外廓。	READY
143961	143961	Hatchback	C4 III	C41	5	EU-CITROEN-C4-III-C41-HATCHBACK-01	HIGH	C41五门两厢外廓。	READY
143981	143981	Wagon	Corolla IX (E120)	NZE120	5	EU-TOYOTA-COROLLA-IX-E120-WAGON-01	HIGH	NZE120五门旅行车外廓。	READY
143996	143996	Sedan	E-Class W212	W212	4	EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	HIGH	W212改款前四门三厢外廓。	READY
144010	144010	Hatchback	Finn I		3	EU-ELARIS-FINN-I-HATCHBACK-01	HIGH	三门双座微型两厢外廓。	READY
144054_sport	144054	SUV	500X I	334	5	EU-FIAT-500X-I-334-SUV-FACELIFT-SPORT-01	MEDIUM	Sport低悬架外廓分支。	READY
144054_cross	144054	SUV	500X I	334	5	EU-FIAT-500X-I-334-SUV-FACELIFT-CROSS-01	MEDIUM	Cross外廓分支。	READY
144058	144058	Wagon	S4 B9	8W5	5	EU-AUDI-S4-B9-8W5-WAGON-FACELIFT-01	HIGH	B9改款S4 Avant外廓。	READY
144059	144059	Convertible	A5 II (F5)	F57	2	EU-AUDI-A5-II-F5-CABRIOLET-01	HIGH	F57双门敞篷外廓。	READY
144060	144060	Coupe	S5 F5	F53	2	EU-AUDI-S5-F5-F53-COUPE-FACELIFT-01	HIGH	F5改款双门轿跑外廓。	READY
144061	144061	Hatchback	S5 F5	F5A	5	EU-AUDI-S5-F5-F5A-SPORTBACK-FACELIFT-01	HIGH	F5改款五门Sportback外廓。	READY
144062	144062	Sedan	S6 C8	4A2	4	EU-AUDI-S6-C8-4A2-SEDAN-01	HIGH	C8 S6四门三厢外廓。	READY
144063	144063	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
144064	144064	Sedan	A6 C8	4A2	4	EU-AUDI-A6-C8-4A2-SEDAN-01	HIGH	C8 4A2三厢外廓。	READY
144083_hardtop	144083	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-HARDTOP-01	HIGH	四门硬顶皮卡外廓。	READY
144083_softtop	144083	Pickup	Gladiator JT	JT	4	EU-JEEP-GLADIATOR-JT-PICKUP-SOFTTOP-01	HIGH	四门软顶皮卡外廓。	READY
144084	144084	Hatchback	Golf VIII		5	EU-VW-GOLF-VIII-HATCHBACK-GTE-01	HIGH	GTE五门插混外廓。	READY
144087	144087	Coupe	Huracán STO		2	EU-LAMBORGHINI-HURACAN-STO-COUPE-01	HIGH	STO后驱双门轿跑外廓。	READY
144107	144107	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH	FY改款TFSI e五门SUV外廓。	READY
144108	144108	SUV	Q5 II	FY	5	EU-AUDI-Q5-II-FY-PHEV-SUV-01	HIGH	FY改款TFSI e五门SUV外廓。	READY
144112	144112	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	HIGH	BU前驱五门SUV外廓。	READY
144113	144113	SUV	Renegade I	BU	5	EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	HIGH	BU 4xe四驱五门SUV外廓。	READY
144116	144116	Hatchback	Scala I		5	EU-SKODA-SCALA-I-HATCHBACK-01	MEDIUM	五门两厢外廓。	READY
144122	144122	SUV	Sorento IV	MQ4	5	EU-KIA-SORENTO-IV-MQ4-SUV-01	HIGH	MQ4标准SUV外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q3-II-F3-SUV-01	4484	1856	1616	Audi Q3 official dimensions	https://www.audi.com/de/publikationen/abmessungen/abmessungen-q3-1413/download
EU-AUDI-Q5-II-FY-SQ5-SUV-02	4682	1893	1635	Audi SQ5 TDI official dimensions	https://www.audi.com/de/publikationen/abmessungen/abmessungen-sq5-tdi-bis-2024-1604/download
EU-AUDI-Q5-II-FY-SUV-02	4682	1893	1662	Auto-Data Audi Q5 II FY facelift 35 TDI Mild Hybrid	https://www.auto-data.net/en/audi-q5-ii-fy-facelift-2020-35-tdi-163hp-mild-hybrid-s-tronic-41477
EU-SKODA-OCTAVIA-IV-WAGON-PREFL-01	4689	1829	1468	Auto-Data Škoda Octavia IV Combi 2.0 TSI 4x4	https://www.auto-data.net/en/skoda-octavia-iv-combi-2.0-tsi-190hp-4x4-dsg-38017
EU-VW-GOLF-VIII-HATCHBACK-GTD-01	4287	1789	1478	Auto-Data Volkswagen Golf VIII GTD 2.0 TDI 200	https://www.auto-data.net/en/volkswagen-golf-viii-gtd-2.0-tdi-200hp-dsg-41548
EU-SEAT-ATECA-I-FACELIFT-SUV-01	4381	1841	1615	Auto-Data SEAT Ateca I facelift 2.0 TDI 115	https://www.auto-data.net/en/seat-ateca-i-facelift-2020-2.0-tdi-115hp-43832
EU-JEEP-COMPASS-II-MP-SUV-01	4394	1819	1644	Auto-Data Jeep Compass II MP 2.0 Multijet 4x4	https://www.auto-data.net/en/jeep-compass-ii-mp-2.0-multijet-140hp-4x4-30040
EU-CUPRA-FORMENTOR-I-SUV-FWD-01	4446	1839	1520	CUPRA Formentor 2022 official technical specifications; Automobile-Catalog 2022 CUPRA Formentor VZ 2.0 TSI 245	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf;https://www.automobile-catalog.com/car/2022/3103220/cupra_formentor_vz_2_0_tsi_245_dsg.html
EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-01	4450	1839	1520	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-CUPRA-FORMENTOR-I-SUV-EHYBRID-01	4450	1839	1510	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-CUPRA-FORMENTOR-I-SUV-4DRIVE-02	4450	1839	1511	CUPRA Formentor 2022 official technical specifications	https://www.cupraofficial.com/content/dam/public/cupra-website/generic/pdf/cupra-formentor-2022.pdf
EU-FORD-KUGA-III-SUV-FHEV-AWD-01	4614	1883	1658	Auto-Data Ford Kuga III 2.5 FHEV i-AWD	https://www.auto-data.net/en/ford-kuga-iii-2.5-duratec-190hp-fhev-i-awd-cvt-41723
EU-FORD-KUGA-III-SUV-STLINE-01	4620	1883	1666	Ford Kuga 2021 official brochure; DrivingElectric Ford Kuga ST-Line specifications	https://www.vanparisonleasing.co.uk/files/a8a/Kuga.pdf;https://www.drivingelectric.com/ford/kuga/plug-in-hybrid/prices-specs/91458/2.5-phev-st-line-5dr-cvt
EU-FORD-KUGA-III-SUV-VIGNALE-01	4629	1883	1680	Ford Kuga 2021 official brochure; Auto Express Ford Kuga FHEV Vignale specifications	https://www.vanparisonleasing.co.uk/files/a8a/Kuga.pdf;https://www.autoexpress.co.uk/ford/kuga/prices-specs/94673/2.5-duratec-fhev-vignale-5dr-cvt
EU-ALFA-ROMEO-STELVIO-949-SUV-01	4687	1903	1671	Auto-Data Alfa Romeo Stelvio 949 2.0 AWD	https://www.auto-data.net/en/alfa-romeo-stelvio-949-2.0-280hp-awd-automatic-28578
EU-SEAT-TARRACO-I-SUV-01	4735	1839	1674	AutoData1 SEAT Tarraco 2.0 TSI 245 4Drive	https://www.autodata1.com/en/car/seat/tarraco/tarraco-20-tsi-245-hp-4drive-dsg-7-seat
EU-VOLVO-V90-II-WAGON-01	4936	1879	1475	Auto-Data Volvo V90 2.0 D3	https://www.auto-data.net/en/volvo-v90-2016-2.0-d3-150hp-27524
EU-ALPINA-B8-G16-GRAN-COUPE-01	5092	1932	1428	BMW ALPINA B8 Gran Coupé official brochure	https://www.alpina-automobiles.com/fileadmin/user_upload/PDF_Brochure/ALPINA_Models/2021_03_INT/B8/epaper/ausgabe.pdf
EU-MERCEDES-BENZ-C-CLASS-W206-SEDAN-01	4751	1820	1437	Mercedes-Benz C-Class Saloon official dimensions	https://www.mercedes-benz-mena.com/static/pdfs/c-klasse-w206-epaper-24-2-02-eng.pdf
EU-BMW-5-G30-SEDAN-FACELIFT-02	4963	1868	1483	BMW 5 Series Sedan 520e official technical specifications	https://www.press.bmwgroup.com/italy/article/attachment/T0328308IT/475174
EU-FERRARI-PORTOFINO-M-CONVERTIBLE-01	4594	1938	1318	Ferrari Portofino M official technical specifications	https://www.ferrari.com/content/dam/ferrari-fcom/old/pdf/cs_ferrari_portofino_m_full_gbr_def.pdf
EU-AUDI-A6-C8-4A2-SEDAN-01	4939	1886	1457	Auto-Data Audi A6 Sedan C8 35 TDI Mild Hybrid	https://www.auto-data.net/en/audi-a6-limousine-c8-35-tdi-163hp-mild-hybrid-s-tronic-36910
EU-AUDI-A6-C8-4A5-WAGON-01	4939	1886	1494	Auto-Data Audi A6 Avant C8 50 TDI Mild Hybrid	https://www.auto-data.net/en/audi-a6-avant-c8-50-tdi-v6-286hp-mild-hybrid-quattro-tiptronic-50762
EU-MERCEDES-BENZ-C-CLASS-S206-WAGON-01	4751	1820	1455	Mercedes-Benz C-Class Estate official technical data	https://www.mercedes-benz.co.uk/passengercars/models/estate/c-class/overview.html
EU-MAXUS-EDELIVER-9-I-VAN-L2H2-01	5546	2062	2525	MAXUS eDELIVER 9 official brochure; Vansdirect MAXUS Deliver 9 width specification	https://i0.motionx.ie/wp-content/uploads/sites/39/2025/10/06095801/e-deliver9-brochure.pdf;https://www.vansdirect.co.uk/load-sizing-guide/maxus-deliver-9-dimensions/
EU-MAXUS-EDELIVER-9-I-VAN-L3H2-01	5940	2062	2525	MAXUS eDELIVER 9 official brochure; Vansdirect MAXUS Deliver 9 width specification	https://i0.motionx.ie/wp-content/uploads/sites/39/2025/10/06095801/e-deliver9-brochure.pdf;https://www.vansdirect.co.uk/load-sizing-guide/maxus-deliver-9-dimensions/
EU-SEAT-LEON-IV-KL1-HATCHBACK-STANDARD-01	4368	1800	1456	SEAT Leon official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL1-HATCHBACK-FR-01	4368	1800	1442	SEAT Leon official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL8-WAGON-STANDARD-01	4642	1799	1448	SEAT Leon Sportstourer official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-SEAT-LEON-IV-KL8-WAGON-FR-01	4642	1799	1437	SEAT Leon Sportstourer official specifications	https://www.seat.com/content/dam/public/seat-website/myco/2130/car-shopping-tools/brochure-download/brochures/new-seat-leon/other-shoppingtools-brochure-leon-specs-final-jul-2020.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB2650-01	4215	1680	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-STDBED-01	4545	1680	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-SRW-WB3070-LONGBED-01	4815	1680	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-STDBED-01	4545	1800	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3000-LONGBED-01	4815	1800	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-PICKUP-DRW-WB3250-01	5095	1800	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB2650-01	4085	1640	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-CHASSIS-SRW-WB3070-01	4505	1640	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3000-01	4435	1714	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-PIAGGIO-PORTER-NP6-CHASSIS-DRW-WB3250-01	4685	1714	1840	Piaggio Porter NP6 official brochure	https://www.technika-ziva.cz/data/catalog-products/attachments/orig/brozura-piaggio-v-anglickem-jazyce.pdf
EU-OPEL-INSIGNIA-B-GRAND-SPORT-HATCHBACK-01	4897	1863	1455	Auto-Data Opel Insignia Grand Sport B 2.0 CDTI	https://www.auto-data.net/en/opel-insignia-grand-sport-b-2.0-cdti-170hp-29213
EU-MERCEDES-BENZ-CLS-C257-COUPE-FACELIFT-01	4988	1890	1435	Auto-Data Mercedes-Benz CLS C257 facelift CLS 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c257-facelift-2021-cls-300d-265hp-mild-hybrid-4matic-9g-tronic-43348
EU-MERCEDES-BENZ-E-CLASS-A238-CONVERTIBLE-FACELIFT-01	4835	1860	1430	Auto-Data Mercedes-Benz E-Class A238 facelift E 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-cabrio-a238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43739
EU-MERCEDES-BENZ-E-CLASS-C238-COUPE-FACELIFT-01	4835	1860	1428	Auto-Data Mercedes-Benz E-Class C238 facelift E 300d 4MATIC	https://www.auto-data.net/en/mercedes-benz-e-class-coupe-c238-facelift-2020-e-300d-265hp-eq-boost-4matic-9g-tronic-43738
EU-HYUNDAI-SANTA-FE-IV-TM-SUV-FACELIFT-01	4785	1900	1710	Auto-Data Hyundai Santa Fe IV TM facelift generation	https://www.auto-data.net/en/hyundai-santa-fe-iv-tm-facelift-2020-generation-7838
EU-MITSUBISHI-SPACE-STAR-VI-HATCHBACK-FACELIFT-01	3845	1665	1505	Auto-Data Mitsubishi Space Star facelift 1.2	https://www.auto-data.net/en/mitsubishi-space-star-facelift-2019-1.2-mivec-80hp-39342
EU-HONDA-CR-V-V-SUV-01	4587	1854	1689	Auto-Data Honda CR-V V Hybrid AWD-i	https://www.auto-data.net/en/honda-cr-v-v-facelift-2019-2.0-212hp-hybrid-awd-i-e-cvt-40083
EU-BMW-M3-G80-SEDAN-01	4794	1903	1433	BMW M3 Competition Sedan official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326323EN/472229
EU-BMW-M4-G82-COUPE-01	4794	1887	1393	BMW M4 Competition Coupé official technical specifications	https://www.press.bmwgroup.com/global/article/attachment/T0326324EN/472231
EU-VW-CADDY-V-MPV-SWB-01	4500	1855	1798	Volkswagen Caddy Life official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Caddy_Life.pdf
EU-VW-CADDY-V-MPV-LWB-01	4853	1855	1800	Volkswagen Caddy Life Maxi official dimension drawing	https://www.volkswagen-vans.co.uk/idhub/content/dam/onehub_nfz/importers/gb/downloads/dimensions/Dimension-Drawings-Caddy_Life.pdf
EU-FORD-KUGA-III-SUV-STANDARD-01	4614	1883	1678	Ford Kuga 2021 official brochure; Auto Express Ford Kuga 1.5 EcoBoost 150 Titanium specifications	https://www.vanparisonleasing.co.uk/files/a8a/Kuga.pdf;https://www.autoexpress.co.uk/ford/kuga/prices-specs/91441/1.5-ecoboost-150-titanium-5dr
EU-MERCEDES-BENZ-S-CLASS-W223-SEDAN-01	5179	1954	1503	Auto-Data Mercedes-Benz S-Class W223 model specifications; Auto-Data Mercedes-Benz S 450 EQ Boost	https://www.auto-data.net/en/mercedes-benz-s-class-model-1394;https://www.auto-data.net/en/mercedes-benz-s-class-w223-s-450-367hp-eq-boost-4matic-9g-tronic-41083
EU-VW-CADDY-V-VAN-SWB-01	4500	1855	1856	Volkswagen Caddy Cargo official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/caddy-cargo/Caddy-Cargo.pdf
EU-VW-CADDY-V-VAN-LWB-01	4853	1855	1860	Volkswagen Caddy Cargo Maxi official technical drawing	https://www.volkswagen-nutzfahrzeuge.de/idhub/content/dam/onehub_nfz/importers/de/download/technische-zeichnungen/caddy-cargo/Caddy-Cargo.pdf
EU-AUDI-A1-GB-HATCHBACK-01	4029	1740	1409	Audi A1 Sportback official dimensions	https://www.audi-mediacenter.com/en/publications/dimensions/dimensions-a1-sportback-1382/download
EU-VW-ARTEON-I-3H-LIFTBACK-FACELIFT-01	4866	1871	1460	Auto-Data Volkswagen Arteon facelift 2.0 TDI	https://www.auto-data.net/en/volkswagen-arteon-facelift-2020-2.0-tdi-190hp-scr-dsg-40772
EU-VW-ARTEON-I-3H-LIFTBACK-R-01	4866	1871	1460	Volkswagen Arteon R official technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-R-01	4866	1871	1462	Volkswagen Arteon R Shooting Brake official technical data	https://www.volkswagen-newsroom.com/en/arteon-r-and-arteon-r-shooting-brake-test-drive-7003/technical-data-7015
EU-VW-ARTEON-I-3H-SHOOTING-BRAKE-EHYBRID-01	4866	1871	1450	Auto-Data Volkswagen Arteon Shooting Brake eHybrid	https://www.auto-data.net/en/volkswagen-arteon-shooting-brake-facelift-2020-1.4-tsi-218hp-ehybrid-dsg-41796
EU-FORD-MUSTANG-MACH-E-I-SUV-01	4713	1881	1625	Ford Mustang Mach-E 2021 official European technical specifications	https://media.ford.com/content/dam/fordmedia/Europe/en/2020/12/Mach-E_AWD/Ford_Mustang_Mach-E_2020_TechSpecs_EU.pdf
EU-POLESTAR-POLESTAR-2-I-FASTBACK-01	4606	1859	1482	Polestar 2 official specifications	https://www.polestar.com/dato-assets/11286/1622123441-specifications-ps2-uk.pdf
EU-VW-POLO-VI-AW1-GTI-HATCHBACK-FACELIFT-01	4074	1751	1431	Auto-Data Volkswagen Polo VI facelift GTI 2.0 TSI 207	https://www.auto-data.net/en/volkswagen-polo-vi-facelift-2021-gti-2.0-tsi-207hp-dsg-44419
EU-MAXUS-T90-EV-PICKUP-01	5365	1900	1809	Auto-Data Maxus T90 Standard box EV 88.55 kWh 177	https://www.auto-data.net/en/maxus-t90-standard-box-ev-88.55-kwh-177hp-46828
EU-AUDI-A7-C7-4G8-LIFTBACK-FACELIFT-01	4974	1911	1420	Auto-Data Audi A7 Sportback C7 facelift 3.0 TFSI quattro	https://www.auto-data.net/en/audi-a7-sportback-c7-facelift-2014-3.0-tfsi-v6-333hp-quattro-s-tronic-22438
EU-AUDI-A7-C8-LIFTBACK-PHEV-01	4969	1908	1421	Auto-Data Audi A7 C8 50 TFSI e	https://www.auto-data.net/en/audi-a7-sportback-c8-50-tfsi-e-299hp-plug-in-hybrid-quattro-ultra-s-tronic-45397
EU-CITROEN-C4-III-C41-HATCHBACK-01	4360	1800	1525	Auto-Data Citroën C4 III BlueHDi 110	https://www.auto-data.net/en/citroen-c4-iii-phase-i-2020-1.5-bluehdi-110hp-42199
EU-TOYOTA-COROLLA-IX-E120-WAGON-01	4410	1710	1520	Auto-Data Toyota Corolla Wagon IX E120/E130	https://www.auto-data.net/en/toyota-corolla-wagon-ix-e120-e130-generation-820
EU-MERCEDES-BENZ-E-CLASS-W212-SEDAN-PREFL-01	4868	1854	1470	Auto-Data Mercedes-Benz E-Class W212 E 250 CGI	https://www.auto-data.net/en/mercedes-benz-e-class-w212-e-250-cgi-blueefficiency-204hp-5g-tronic-17371
EU-ELARIS-FINN-I-HATCHBACK-01	2871	1563	1568	Auto-Data Elaris Finn 31.5 kWh 48	https://www.auto-data.net/en/elaris-finn-31.5-kwh-48hp-50309
EU-FIAT-500X-I-334-SUV-FACELIFT-SPORT-01	4264	1796	1582	Automobile-Catalog 2021 Fiat 500X 1.6 MultiJet 130 Sport	https://www.automobile-catalog.com/car/2021/3045440/fiat_500x_1_6_multijet_130_4x2_sport.html
EU-FIAT-500X-I-334-SUV-FACELIFT-CROSS-01	4269	1796	1603	Automobile-Catalog 2021 Fiat 500X 1.6 MultiJet 130 Cross; Auto-Data Fiat 500X Cross facelift generation	https://www.automobile-catalog.com/car/2021/3045380/fiat_500x_1_6_multijet_130_4x2_cross.html;https://www.auto-data.net/en/fiat-500x-model-3415
EU-AUDI-S4-B9-8W5-WAGON-FACELIFT-01	4770	1847	1433	Auto-Data Audi S4 Avant B9 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s4-avant-b9-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47368
EU-AUDI-A5-II-F5-CABRIOLET-01	4673	1846	1383	Auto-Data Audi A5 Cabriolet F5 2.0 TFSI	https://www.auto-data.net/en/audi-a5-cabriolet-f5-2.0-tfsi-190hp-28388
EU-AUDI-S5-F5-F53-COUPE-FACELIFT-01	4705	1846	1368	Auto-Data Audi S5 Coupe F5 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s5-coupe-f5-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47390
EU-AUDI-S5-F5-F5A-SPORTBACK-FACELIFT-01	4765	1843	1395	Auto-Data Audi S5 Sportback F5 facelift 3.0 TDI	https://www.auto-data.net/en/audi-s5-sportback-f5-facelift-2019-3.0-tdi-v6-341hp-mild-hybrid-quattro-tiptronic-47394
EU-AUDI-S6-C8-4A2-SEDAN-01	4954	1886	1446	Auto-Data Audi S6 C8 3.0 TDI	https://www.auto-data.net/en/audi-s6-c8-3.0-tdi-v6-344hp-mild-hybrid-quattro-tiptronic-47372
EU-JEEP-GLADIATOR-JT-PICKUP-HARDTOP-01	5591	1894	1843	Jeep Gladiator official technical specifications	https://www.media.stellantis.com/em-en/download-model-document/166
EU-JEEP-GLADIATOR-JT-PICKUP-SOFTTOP-01	5591	1894	1905	Jeep Gladiator official technical specifications	https://www.media.stellantis.com/em-en/download-model-document/166
EU-VW-GOLF-VIII-HATCHBACK-GTE-01	4287	1789	1484	Volkswagen Golf GTE official technical data	https://www.volkswagen-newsroom.com/en/golf-etsi-golf-ehybrid-and-golf-gte-international-media-drive-6336/the-technical-data-of-the-new-golf-hybrid-models-6344
EU-LAMBORGHINI-HURACAN-STO-COUPE-01	4549	1945	1220	Lamborghini Huracán STO official model page; Auto-Data Lamborghini Huracán STO dimensions	https://www.lamborghini.com/en-en/history/huracan-sto;https://www.auto-data.net/en/lamborghini-huracan-sto-facelift-2020-5.2-v10-640hp-ldf-41726
EU-AUDI-Q5-II-FY-PHEV-SUV-01	4682	1893	1652	Audi Q5 TFSI e official dimensions	https://media.audi.com/is/content/audi/country/ch/assets/dimensions/q5/Q5-TFSI-e-PA-Abmessungen.pdf
EU-JEEP-RENEGADE-I-BU-SUV-FWD-01	4232	1803	1664	AutoScout24 Jeep Renegade 1.6 MultiJet 4x2 technical data	https://www.autoscout24.es/coches/datos-tecnicos/jeep/renegade/renegade-1-6mjt-rebel-4x2-88kw-suv-4x4-pickup-diesel-7987/
EU-JEEP-RENEGADE-I-BU-SUV-4X4-01	4232	1803	1689	Jeep Renegade official specifications	https://www.fcapresskit.ca/2015/Contents/Press-Releases/PDFs/Jeep/Renegade/CN_2015_JP_Renegade_SP.pdf
EU-SKODA-SCALA-I-HATCHBACK-01	4362	1793	1471	Auto-Data Škoda Scala 1.6 TDI	https://www.auto-data.net/en/skoda-scala-1.6-tdi-115hp-35204
EU-KIA-SORENTO-IV-MQ4-SUV-01	4810	1900	1700	Auto-Data Kia Sorento IV 1.6 T-GDI PHEV AWD	https://www.auto-data.net/en/kia-sorento-iv-1.6-t-gdi-265hp-plug-in-hybrid-awd-automatic-7-seat-44829
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.vanparisonleasing.co.uk/files/a8a/Kuga.pdf "https://www.vanparisonleasing.co.uk/files/a8a/Kuga.pdf"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_301-400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_301-400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2306 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1109 行）

