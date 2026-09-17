# 任务：all 第 8101-8200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0082__b0b05fe4


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 8101-8200 行

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
all 第 8101-8200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8101-8200_ktype_dimension_mapping_final.tsv
- all_8101-8200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453
EU-BMW-3200-CS-COUPE-2D-01	4830	1720	1460
EU-BMW-3-E30-CONVERTIBLE-01	4325	1645	1370
EU-BMW-3-E30-CONVERTIBLE-PREFL-01	4325	1645	1380
EU-BMW-3-E30-TOURING-01	4321	1641	1379
EU-BMW-3-E36-COMPACT-HATCHBACK-3D-01	4210	1700	1390
EU-BMW-3-E36-CONVERTIBLE-01	4433	1710	1348
EU-BMW-3-E36-M3-CONVERTIBLE-01	4433	1710	1340
EU-BMW-3-E36-M3-COUPE-01	4433	1710	1335
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393
EU-BMW-3-SERIES-E36-TOURING-5D-01	4433	1698	1391
EU-CITROEN-BERLINGO-II-B9-MPV-5D-01	4380	1810	1801
EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	4108	1698	1802
EU-CITROEN-BERLINGO-I-M59-MPV-VAN-01	4137	1724	1810
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150
EU-CITROEN-XM-Y3-HATCHBACK-01	4708	1794	1385
EU-CITROEN-XM-Y3-WAGON-01	4963	1794	1467
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467
EU-FIAT-DUCATO-I-280-PICKUP-DOUBLECAB-01	5598	2000	2092
EU-FIAT-DUCATO-I-280-PICKUP-SINGLECAB-01	5598	2000	2096
EU-FIAT-DUCATO-I-280-VAN-LWB-HIGHROOF-01	5489	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-HIGHROOF-01	4759	1965	2400
EU-FIAT-DUCATO-I-280-VAN-SWB-LOWROOF-01	4759	1965	2100
EU-FIAT-DUCATO-I-290-VAN-LWB-HIGHROOF-01	5495	1965	2450
EU-FIAT-DUCATO-I-290-VAN-LWB-LOWROOF-01	5495	1965	2100
EU-FIAT-DUCATO-I-290-VAN-SWB-HIGHROOF-01	4765	1965	2450
EU-FIAT-DUCATO-I-290-VAN-SWB-LOWROOF-01	4765	1965	2100
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150
EU-FIAT-DUCATO-I-PANORAMA-280-01	4759	1965	2100
EU-FIAT-DUCATO-I-PANORAMA-290-01	4765	1965	2100
EU-FIAT-DUCATO-X250-VAN-L2H2-01	5413	2050	2524
EU-FIAT-PUNTO-EVO-HATCHBACK-3D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-5D-01	4065	1687	1490
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-3D-01	4065	1687	1514
EU-FIAT-PUNTO-EVO-HATCHBACK-CNG-5D-01	4065	1687	1514
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447
EU-FIAT-PUNTO-I-176-GT-HATCHBACK-3D-01	3770	1625	1450
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460
EU-LAND-ROVER-FREELANDER-II-SUV-FL2010-01	4500	1910	1740
EU-LAND-ROVER-FREELANDER-II-SUV-FL2012-01	4500	1910	1740
EU-LAND-ROVER-FREELANDER-II-SUV-PREFL-01	4500	1910	1740
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490
EU-PEUGEOT-605-I-FACELIFT-SEDAN-STANDARD-01	4765	1799	1417
EU-PEUGEOT-605-I-FACELIFT-SEDAN-SV24-01	4765	1799	1411
EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	4765	1799	1415
EU-PEUGEOT-605-I-SEDAN-STANDARD-01	4723	1799	1417
EU-PEUGEOT-605-I-SEDAN-SV24-01	4723	1799	1411
EU-PEUGEOT-605-I-SEDAN-V6-01	4723	1799	1415
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885
EU-RENAULT-KANGOO-I-FACELIFT-STANDARD-SWB-01	4035	1672	1825
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1802-01	4666	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-FACELIFT-H1826-01	4666	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1802-01	4597	1829	1802
EU-RENAULT-KANGOO-II-X61-ZE-MPV-LWB-5S-PREFL-H1826-01	4597	1829	1826
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1810-01	4666	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-FACELIFT-H1836-01	4666	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1810-01	4597	1829	1810
EU-RENAULT-KANGOO-II-X61-ZE-VAN-LWB-2S-PREFL-H1836-01	4597	1829	1836
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1805-01	4282	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-FACELIFT-H1844-01	4282	1829	1844
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1805-01	4213	1829	1805
EU-RENAULT-KANGOO-II-X61-ZE-VAN-SWB-PREFL-H1844-01	4213	1829	1844
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	4508	1752	1433
EU-RENAULT-LAGUNA-III-B91-HATCHBACK-5D-01	4695	1811	1445
EU-RENAULT-LAGUNA-III-K91-WAGON-5D-01	4803	1811	1445
EU-RENAULT-LAGUNA-I-K56-WAGON-01	4620	1752	1448
EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	4628	1752	1448
EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	4620	1752	1448
EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	4530	1695	1620
EU-VW-SHARAN-I-MPV-01	4634	1810	1730

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Toyota	Avensis	1.6 I	Kombi	Frontantrieb	Benzin	81	110	Sep 1997	Oct 2000	2024-03-01	8934
Toyota	Avensis	1.8 I	Kombi	Frontantrieb	Benzin	81	110	Sep 1997	Oct 2000	2024-03-01	8935
Toyota	Avensis	2.0 I	Kombi	Frontantrieb	Benzin	94	128	Sep 1997	Oct 2000	2024-03-01	8936
Toyota	Avensis	2.0 TD	Kombi	Frontantrieb	Diesel	66	90	Sep 1997	Feb 2003	2024-03-01	8937
Toyota	Picnic	2.2 D	Großraumlimousine	Frontantrieb	Diesel	66	90	Aug 1997	Dec 2001	2024-03-01	8938
Audi	A6 c5 avant	1.9 TDI	Kombi	Frontantrieb	Diesel	81	110	Feb 1998	Apr 2001	2024-03-01	8939
Audi	A6 c5 avant	1.8	Kombi	Frontantrieb	Benzin	92	125	Dec 1997	Jan 2005	2024-03-01	8940
Audi	A6 c5 avant	2.8 Quattro	Kombi	Allrad	Benzin	142	193	Dec 1997	Jan 2005	2024-03-01	8941
Audi	A6 c5 avant	1.8 T	Kombi	Frontantrieb	Benzin	110	150	Dec 1997	Jan 2005	2024-03-01	8942
Audi	A6 c5 avant	2.4	Kombi	Frontantrieb	Benzin	121	165	Dec 1997	Jan 2005	2024-03-01	8943
Audi	A6 c5 avant	2.8	Kombi	Frontantrieb	Benzin	142	193	Dec 1997	Jan 2005	2024-03-01	8944
Audi	A6 c5 avant	1.8 T Quattro	Kombi	Allrad	Benzin	110	150	Dec 1997	Jan 2005	2024-03-01	8945
Audi	A6 c5 avant	2.4 Quattro	Kombi	Allrad	Benzin	121	165	Dec 1997	Jan 2005	2024-03-01	8946
Audi	A6 c5 avant	2.5 TDI	Kombi	Frontantrieb	Diesel	110	150	Dec 1997	Jan 2005	2024-03-01	8947
Audi	A6 c5 avant	2.5 TDI Quattro	Kombi	Allrad	Diesel	110	150	Dec 1997	Jan 2005	2024-03-01	8948
Citroën	Jumper i	2	Kasten	Frontantrieb	Benzin	80	109	Mar 1994	Apr 2002	2024-03-01	8949
Citroën	Jumper i	1.9 D	Kasten	Frontantrieb	Diesel	51	69	Feb 1994	Apr 2002	2024-03-01	8950
Citroën	Jumper i	1.9 TD	Kasten	Frontantrieb	Diesel	68	92	Mar 1994	Apr 2002	2024-03-01	8951
Citroën	Jumper i	2.5 D	Kasten	Frontantrieb	Diesel	63	86	Mar 1994	Apr 2002	2024-03-01	8952
Citroën	Jumper i	2.5 TD	Kasten	Frontantrieb	Diesel	76	103	Mar 1994	Apr 2002	2024-03-01	8953
Citroën	Berlingo	1.8 I	Großraumlimousine	Frontantrieb	Benzin	66	90	May 1997	Oct 2002	2024-03-01	8955
Citroën	Xsara	1.9 D	Schrägheck	Frontantrieb	Diesel	50	68	Apr 1997	Sep 2000	2024-03-01	8957
VW	Sharan	1.8 T 20V	Großraumlimousine	Frontantrieb	Benzin	110	150	Sep 1997	Mar 2010	2024-03-01	8958
Fiat	Ducato	2	Kasten	Frontantrieb	Benzin	80	109	Mar 1994	Apr 2002	2024-03-01	8959
Fiat	Ducato	2.8 TDI	Bus	Frontantrieb	Diesel	90	122	Oct 1997	Apr 2002	2024-03-01	8960
Fiat	Punto	1.2 16V	Schrägheck	Frontantrieb	Benzin	63	86	Apr 1997	Sep 1999	2024-03-01	8961
Fiat	Punto	85 16V 1.2	Cabriolet	Frontantrieb	Benzin	63	86	Apr 1997	Jun 2000	2024-03-01	8962
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	87	118	Dec 1997	Sep 2001	2024-03-01	8963
BMW	3	328 I	Stufenheck	Heckantrieb	Benzin	142	193	Feb 1998	Jun 2000	2024-03-01	8964
Audi	A6 c5 avant	2.7 T	Kombi	Frontantrieb	Benzin	169	230	Feb 1999	Jan 2005	2024-03-01	8965
Audi	A6 c5 avant	2.7 T Quattro	Kombi	Allrad	Benzin	169	230	Dec 1997	Jan 2005	2024-03-01	8966
Audi	A6 c5	2.7 T	Stufenheck	Frontantrieb	Benzin	169	230	Feb 1999	Jan 2005	2024-03-01	8967
Audi	A6 c5	2.7 T Quattro	Stufenheck	Allrad	Benzin	169	230	Dec 1997	Jan 2005	2024-03-01	8968
Fiat	Seicento / 600	0.9	Schrägheck	Frontantrieb	Benzin	29	39	Nov 1997	Dec 2008	2024-03-01	8969
Fiat	Seicento / 600	1.1	Schrägheck	Frontantrieb	Benzin	40	54	Jan 1998	Jan 2010	2024-03-01	8970
VW	Lupo i	1	Schrägheck	Frontantrieb	Benzin	37	50	Sep 1998	Jul 2005	2024-03-01	8971
VW	Lupo i	1.4 16V	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1998	Jul 2005	2024-03-01	8972
VW	Lupo i	1.7 SDI	Schrägheck	Frontantrieb	Diesel	44	60	Sep 1998	Jul 2005	2024-03-01	8973
Mazda	626 v station wagon	1.8	Kombi	Frontantrieb	Benzin	66	90	Feb 1998	Jan 2000	2024-03-01	8974
Mazda	626 v station wagon	2	Kombi	Frontantrieb	Benzin	85	116	Feb 1998	Oct 2002	2024-03-01	8975
Mazda	626 v station wagon	2.0 H.p.	Kombi	Frontantrieb	Benzin	100	136	Feb 1998	Oct 2002	2024-03-01	8976
Mazda	626 v hatchback	2.0 H.p.	Schrägheck	Frontantrieb	Benzin	100	136	Feb 1998	Oct 2002	2024-03-01	8977
Smart	City-	0.6	Coupe	Heckantrieb	Benzin	33	45	Jul 1998	Jan 2004	2024-03-01	8978
VW	New beetle	2	Schrägheck	Frontantrieb	Benzin	85	115	Jan 1998	Sep 2010	2024-03-01	8979
VW	New beetle	1.9 TDI	Schrägheck	Frontantrieb	Diesel	66	90	Jan 1998	Jun 2004	2024-03-01	8980
Ford	Puma	1.4 16V	Coupe	Frontantrieb	Benzin	66	90	Nov 1997	Oct 2000	2024-03-01	8981
Hyundai	Atos	1.0 I	Schrägheck	Frontantrieb	Benzin	40	54	Feb 1998	Dec 2000	2024-03-01	8982
Mercedes-benz	V-Klasse	V 200	Bus	Frontantrieb	Benzin	95	129	Feb 1997	Jul 2003	2024-03-01	8983
Suzuki	Wagon r+	1	Schrägheck	Frontantrieb	Benzin	48	65	Feb 1998	May 2000	2024-03-01	8984
Land Rover	Freelander i	1.8 I 16V 4X4	Geländewagen geschlossen	Allrad	Benzin	88	120	Feb 1998	Nov 2000	2024-03-01	8985
Land Rover	Freelander i	2.0 DI 4X4	Geländewagen geschlossen	Allrad	Diesel	72	98	Feb 1998	Nov 2000	2024-03-01	8986
Renault	Kangoo	1.2	Großraumlimousine	Frontantrieb	Benzin	43	58	Aug 1997	-	2024-03-01	8987
Renault	Kangoo	1.4	Großraumlimousine	Frontantrieb	Benzin	55	75	Aug 1997	-	2024-03-01	8988
Renault	Kangoo	D 55 1.9	Großraumlimousine	Frontantrieb	Diesel	40	54	Aug 1997	-	2024-03-01	8989
Renault	Kangoo	D 65 1.9	Großraumlimousine	Frontantrieb	Diesel	47	64	Aug 1997	Jun 2001	2024-03-01	8990
Renault	Laguna i	1.9 DTI	Schrägheck	Frontantrieb	Diesel	72	98	Oct 1997	Mar 2001	2024-03-01	8991
Renault	Laguna i grandtour	1.9 DTI	Kombi	Frontantrieb	Diesel	72	98	Oct 1997	Mar 2001	2024-03-01	8992
Opel	Astra g cc	1.2 16V	Schrägheck	Frontantrieb	Benzin	48	65	Feb 1998	Sep 2000	2024-03-01	8993
Opel	Astra g cc	1.6	Schrägheck	Frontantrieb	Benzin	55	75	Feb 1998	Sep 2000	2024-03-01	8994
Opel	Astra g cc	1.6 16V	Schrägheck	Frontantrieb	Benzin	74	101	Feb 1998	Jan 2005	2024-03-01	8995
Opel	Astra g cc	1.8 16V	Schrägheck	Frontantrieb	Benzin	85	116	Feb 1998	Sep 2000	2024-03-01	8996
Opel	Astra g cc	2.0 16V	Schrägheck	Frontantrieb	Benzin	100	136	Feb 1998	Jan 2005	2024-03-01	8997
Opel	Astra g cc	1.7 TD	Schrägheck	Frontantrieb	Diesel	50	68	Feb 1998	Aug 2000	2024-03-01	8998
Opel	Astra g cc	2.0 DI	Schrägheck	Frontantrieb	Diesel	60	82	Feb 1998	Jan 2005	2024-03-01	8999
Opel	Astra g caravan	1.2 16V	Kombi	Frontantrieb	Benzin	48	65	Feb 1998	Sep 2000	2024-03-01	9000
Opel	Astra g caravan	1.6	Kombi	Frontantrieb	Benzin	55	75	Feb 1998	Sep 2000	2024-03-01	9001
Opel	Astra g caravan	1.6 16V	Kombi	Frontantrieb	Benzin	74	101	Feb 1998	Jul 2004	2024-03-01	9002
Opel	Astra g caravan	1.8 16V	Kombi	Frontantrieb	Benzin	85	116	Feb 1998	Sep 2000	2024-03-01	9003
Opel	Astra g caravan	2.0 16V	Kombi	Frontantrieb	Benzin	100	136	Feb 1998	Jul 2004	2024-03-01	9004
Opel	Astra g caravan	1.7 TD	Kombi	Frontantrieb	Diesel	50	68	Feb 1998	Aug 2000	2024-03-01	9005
Opel	Astra g caravan	2.0 DI	Kombi	Frontantrieb	Diesel	60	82	Feb 1998	Jul 2004	2024-03-01	9006
Opel	Omega b	2.0 DTI 16V	Stufenheck	Heckantrieb	Diesel	74	101	Sep 1997	Sep 2000	2024-03-01	9007
Opel	Omega b caravan	2.0 DTI 16V	Kombi	Heckantrieb	Diesel	74	101	Sep 1997	Sep 2000	2024-03-01	9008
Opel	Vectra b	2.0 DTI 16V	Stufenheck	Frontantrieb	Diesel	74	101	Jun 1997	Apr 2002	2024-03-01	9009
Opel	Vectra b cc	2.0 DTI 16V	Schrägheck	Frontantrieb	Diesel	74	101	Jun 1997	Jul 2003	2024-03-01	9010
Opel	Vectra b caravan	2.0 DTI 16V	Kombi	Frontantrieb	Diesel	74	101	Jun 1997	Jul 2003	2024-03-01	9011
Opel	Corsa b	1.2 I 16V	Schrägheck	Frontantrieb	Benzin	48	65	Mar 1998	Sep 2000	2024-03-01	9012
Citroën	Xm	3.0 V6	Schrägheck	Frontantrieb	Benzin	140	190	Apr 1997	Oct 2000	2024-03-01	9013
Citroën	Xm	3.0 V6	Kombi	Frontantrieb	Benzin	140	190	Apr 1997	Oct 2000	2024-03-01	9014
Peugeot	605	3.0 V6	Stufenheck	Frontantrieb	Benzin	140	190	Apr 1997	Sep 1999	2024-03-01	9015
Fiat	Duna	60 1.1	Stufenheck	Frontantrieb	Benzin	43	58	Jan 1987	Dec 1991	2024-03-01	9016
Fiat	Duna	60 1.1	Kombi	Frontantrieb	Benzin	43	58	Jan 1987	Dec 1991	2024-03-01	9017
Fiat	Duna	70 1.3	Stufenheck	Frontantrieb	Benzin	49	67	Jan 1987	Dec 1991	2024-03-01	9018
Fiat	Duna	70 1.3	Kombi	Frontantrieb	Benzin	49	67	Jan 1987	Dec 1991	2024-03-01	9019
Fiat	Duna	1.7 DS	Stufenheck	Frontantrieb	Diesel	44	60	Jan 1987	Dec 1991	2024-03-01	9020
Fiat	Duna	1.7 DS	Kombi	Frontantrieb	Diesel	44	60	Jan 1987	Dec 1991	2024-03-01	9021
ZAZ	Tavria	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Jan 1989	Dec 2007	2024-03-01	9022
ZAZ	Tavria	1.3	Schrägheck	Frontantrieb	Benzin	44	60	Jan 1989	Dec 2007	2024-03-01	9023
Daewoo	Nubira	2.0 16V	Schrägheck	Frontantrieb	Benzin	98	133	May 1997	-	2024-03-01	9024
Daewoo	Nubira	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	May 1997	-	2024-03-01	9025
Daewoo	Nubira	1.6 16V	Stufenheck	Frontantrieb	Benzin	78	106	May 1997	May 1999	2024-03-01	9026
Daewoo	Nubira	1.6 16V	Kombi	Frontantrieb	Benzin	78	106	May 1997	May 1999	2024-03-01	9027
Daewoo	Nubira	2.0 16V	Kombi	Frontantrieb	Benzin	98	133	May 1997	-	2024-03-01	9028
Daewoo	Leganza	2.0 16V	Stufenheck	Frontantrieb	Benzin	98	133	Jun 1997	Dec 2002	2024-03-01	9029
Daewoo	Lanos	1.3	Schrägheck	Frontantrieb	Benzin	55	75	May 1997	-	2024-03-01	9030
Daewoo	Lanos	1.3	Stufenheck	Frontantrieb	Benzin	55	75	May 1997	-	2024-03-01	9031
Daewoo	Lanos	1.5	Schrägheck	Frontantrieb	Benzin	63	86	May 1997	-	2024-03-01	9032
Daewoo	Lanos	1.5	Stufenheck	Frontantrieb	Benzin	63	86	May 1997	-	2024-03-01	9033
Daewoo	Lanos	1.6 16V	Schrägheck	Frontantrieb	Benzin	78	106	May 1997	-	2024-03-01	9034
VW	Passat b5 variant	2.3 VR5 Syncro/4motion	Kombi	Allrad	Benzin	110	150	Oct 1997	Nov 2000	2024-03-01	9035


--- Round 1 / 首次发送 ---
## 更新点

* 本轮完成 60 个输入 Ktype 的映射闭合，共形成 75 条 READY 映射行。
* 新建 16 个尺寸组，复用跨批次既有尺寸组 21 个；当前已引用并闭合 37 个尺寸组。
* Avensis T22 Wagon 当前只闭合改款前的 8934–8936；8937 跨越改款边界，暂不强行复用改款前尺寸组。改款前 Wagon 为 4570×1710×1500 mm。([汽车数据网][1])
* New Beetle 8979 已按改款前后拆分：改款前 4081×1725×1500 mm，2005 改款后 4129×1721×1498 mm；8980 仅关联改款前组。([汽车数据网][2])
* Astra G Hatchback 按 F08 三门和 F48 五门拆分，Caravan 使用 F35；三种分支均独立建组。([汽车数据网][3])
* Lupo 与 Passat B5 Variant 使用 Volkswagen 官方历史车型资料闭合。([Volkswagen Newsroom][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：60
* READY 映射行：75
* PENDING 输入 Ktype：40
* 已确认尺寸组：37

  * 本轮新建：16
  * 复用既有组：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8934	8934	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8935	8935	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8936	8936	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8938	8938	MPV	Picnic I	XM1	5	EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	HIGH		READY
8939	8939	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8940	8940	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8941	8941	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8942	8942	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8943	8943	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8944	8944	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8945	8945	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8946	8946	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8947	8947	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8948	8948	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8957	8957	Hatchback	Xsara I Phase I	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	HIGH		READY
8958	8958	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH	第一代同一外廓组。	READY
8961_3dr	8961	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8961_5dr	8961	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8962	8962	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH		READY
8963	8963	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
8964	8964	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
8965	8965	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8966	8966	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8967	8967	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8968	8968	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8971	8971	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8972	8972	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8973	8973	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8974	8974	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8975	8975	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8976	8976	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8977	8977	Hatchback	626 V	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-5D-01	HIGH		READY
8979_prefl	8979	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
8979_facelift	8979	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	HIGH	改款后外廓。	READY
8980	8980	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH		READY
8981	8981	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-ECT-COUPE-3D-01	HIGH		READY
8982	8982	Hatchback	Atos I	MX	5	EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	MEDIUM	同代1.0车型外廓；功率标注存在市场差异。	READY
8984	8984	MPV	Wagon R+ I	EM	5	EU-SUZUKI-WAGON-R-EM-MPV-5D-01	MEDIUM	同代1.0车型外廓；功率标注存在市场差异。	READY
8993_3dr	8993	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8993_5dr	8993	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8994_3dr	8994	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8994_5dr	8994	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8995_3dr	8995	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8995_5dr	8995	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8996_3dr	8996	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8996_5dr	8996	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8997_3dr	8997	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8997_5dr	8997	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8998_3dr	8998	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8998_5dr	8998	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8999_3dr	8999	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8999_5dr	8999	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9000	9000	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9001	9001	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9002	9002	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9003	9003	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9004	9004	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9005	9005	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9006	9006	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9007_prefl	9007	Sedan	Omega B	V94	4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
9007_facelift	9007	Sedan	Omega B	V94	4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
9008_prefl	9008	Wagon	Omega B	V94	5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH	改款前外廓。	READY
9008_facelift	9008	Wagon	Omega B	V94	5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
9009_prefl	9009	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
9009_facelift	9009	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
9010_prefl	9010	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
9010_facelift	9010	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
9011_prefl	9011	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	改款前外廓。	READY
9011_facelift	9011	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
9012_3dr	9012	Hatchback	Corsa B	S93	3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9012_5dr	9012	Hatchback	Corsa B	S93	5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9013	9013	Hatchback	XM II (Y4)	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
9014	9014	Wagon	XM II (Y4)	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
9015	9015	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	HIGH		READY
9035	9035	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	4570	1710	1500	Auto-Data Toyota Avensis Wagon (T22) 2.0	https://www.auto-data.net/en/toyota-avensis-wagon-t22-2.0-128hp-3620
EU-AUDI-A6-C5-4B5-WAGON-5D-01	4796	1810	1479	Auto-Data Audi A6 Avant (4B,C5) 2.8 V6	https://www.auto-data.net/en/audi-a6-avant-4b-c5-2.8-v6-30v-193hp-tiptronic-26842
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405	Automobile-Catalog 1997 Citroen Xsara 1.9 D SX	https://www.automobile-catalog.com/car/1997/546530/citroen_xsara_1_9_d_sx.html
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan (E46) 318i	https://www.auto-data.net/en/bmw-3-series-sedan-e46-318i-118hp-9978
EU-VW-LUPO-I-6X-HATCHBACK-3D-01	3527	1639	1460	Volkswagen Newsroom Lupo profile	https://www.volkswagen-newsroom.com/en/vehicle-data-lupo-profile-19705
EU-MAZDA-626-V-GW-WAGON-5D-01	4660	1710	1515	Auto-Data Mazda 626 V Station Wagon (GF,GW) 2.0 H.P.	https://www.auto-data.net/en/mazda-626-v-station-wagon-gf-gw-2.0-h.p.-136hp-11275
EU-MAZDA-626-V-GF-HATCHBACK-5D-01	4574	1710	1430	Auto-Data Mazda 626 V Hatchback (GF) 2.0	https://www.auto-data.net/en/mazda-626-v-hatchback-gf-2.0-136hp-11279
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	4081	1725	1500	Auto-Data Volkswagen NEW Beetle (9C) 2.0	https://www.auto-data.net/en/volkswagen-new-beetle-9c-2.0-115hp-automatic-27939
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Auto-Data Volkswagen NEW Beetle (9C, facelift 2005) 2.0	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-2.0-115hp-28090
EU-FORD-PUMA-I-ECT-COUPE-3D-01	3984	1674	1345	Auto-Data Ford Puma Coupe (ECT) 1.4 16V	https://www.auto-data.net/en/ford-puma-coupe-ect-1.4-16v-90hp-8008
EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	3495	1495	1615	Auto-Data Hyundai Atos 1.0 i	https://www.auto-data.net/en/hyundai-atos-1.0-i-56hp-automatic-29338
EU-SUZUKI-WAGON-R-EM-MPV-5D-01	3410	1575	1700	Auto-Data Suzuki Wagon R+ (EM) 1.0 i	https://www.auto-data.net/en/suzuki-wagon-r-em-1.0-i-69hp-automatic-23925
EU-OPEL-ASTRA-G-HATCHBACK-3D-01	4110	1709	1425	Auto-Data Opel Astra G 1.6 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.6-ecotec-16v-101hp-automatic-25829
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425	Auto-Data Opel Astra G 1.6 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.6-ecotec-16v-101hp-automatic-25829
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.6	https://www.auto-data.net/en/opel-astra-g-caravan-1.6-75hp-automatic-26385
EU-VW-PASSAT-B5-3B5-WAGON-5D-01	4670	1740	1500	Volkswagen Newsroom Passat B5 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b5-profile-19547
```

## 下一步优先处理

1. 集中闭合 Citroën Jumper I 与 Fiat Ducato 的 SWB/MWB/LWB、低顶/高顶及 Bus/Van 分支。
2. 核对 Avensis 8937、Seicento 8969–8970 跨改款范围，避免把改款前尺寸覆盖到后期外廓。
3. 处理 Berlingo、Smart City-Coupé、V-Klasse W638、Freelander I、Kangoo I 和 Laguna I 的门数、改款及车身边界。
4. 批量闭合 Duna、Tavria、Nubira、Leganza、Lanos 等剩余车型簇。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/toyota-avensis-wagon-t22-2.0-128hp-3620 "Toyota Avensis  Wagon (T22) 2.0 (128 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-new-beetle-9c-2.0-115hp-automatic-27939 "Volkswagen NEW Beetle (9C) 2.0 (115 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-astra-g-1.6-ecotec-16v-101hp-automatic-25829 "Opel Astra G 1.6 Ecotec 16V (101 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.volkswagen-newsroom.com/en/vehicle-data-lupo-profile-19705 "Vehicle data Lupo profile | Volkswagen Newsroom"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8101-8200_ktype_dimension_mapping_final.tsv
- all_8101-8200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮完成 24 个此前 PENDING 的 Ktype，新增 31 条 READY 映射；首次闭合 15 个尺寸组，并新增引用 5 个跨批次既有尺寸组。
* 已处理 Avensis T22 跨改款、Smart City-Coupé 跨改款、V-Class W638、Kangoo I、Laguna I、Duna、Tavria、Nubira 与 Leganza 车型簇。([汽车目录][1])
* Seicento 8969–8970 暂不闭合：0.9、早期 1.1 与后期 1.1 的直接规格分别出现 3319×1508×1440、3335×1510×1450 和 3337×1508×1445，需要继续确认 Ktype 对应的改款及配置边界。([汽车数据网][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：84
* READY 映射行：106
* PENDING 输入 Ktype：16
* 已确认并引用尺寸组：57
* 本轮首次创建尺寸组：15
* 剩余 PENDING：8949–8953、8959–8960、8969–8970、8985–8986、9030–9034
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8937_prefl	8937	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8937_facelift	8937	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
8955	8955	MPV	Berlingo I	M49	5	EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	HIGH		READY
8978_prefl	8978	Coupe	City-Coupé (W450)	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	HIGH	改款前外廓。	READY
8978_facelift	8978	Coupe	City-Coupé (W450)	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	HIGH	改款后外廓。	READY
8983	8983	MPV	V-Class W638	W638	5	EU-MERCEDES-BENZ-V-CLASS-W638-MPV-5D-01	HIGH		READY
8987	8987	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8988	8988	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8989	8989	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8990	8990	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8991_prefl	8991	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	改款前外廓。	READY
8991_facelift	8991	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	改款后外廓。	READY
8992_prefl	8992	Wagon	Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	改款前外廓。	READY
8992_facelift	8992	Wagon	Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
9016	9016	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9017	9017	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9018	9018	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9019	9019	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9020	9020	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9021	9021	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9022	9022	Hatchback	Tavria 1102	1102	3	EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	HIGH		READY
9023	9023	Hatchback	Tavria 1102	1102	3	EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	HIGH		READY
9024_prefl	9024	Hatchback	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-HATCHBACK-5D-01	HIGH	改款前外廓。	READY
9024_facelift	9024	Hatchback	Nubira I Phase II	J150	5	EU-DAEWOO-NUBIRA-I-J150-HATCHBACK-5D-01	HIGH	改款后外廓。	READY
9025_prefl	9025	Sedan	Nubira I Phase I	J100	4	EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	HIGH	改款前外廓。	READY
9025_facelift	9025	Sedan	Nubira I Phase II	J150	4	EU-DAEWOO-NUBIRA-I-J150-SEDAN-4D-01	HIGH	改款后外廓。	READY
9026	9026	Sedan	Nubira I Phase I	J100	4	EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	HIGH		READY
9027	9027	Wagon	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	HIGH		READY
9028_prefl	9028	Wagon	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	HIGH	改款前外廓。	READY
9028_facelift	9028	Wagon	Nubira I Phase II	J150	5	EU-DAEWOO-NUBIRA-I-J150-WAGON-5D-01	HIGH	改款后外廓。	READY
9029	9029	Sedan	Leganza	V100	4	EU-DAEWOO-LEGANZA-V100-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-FACELIFT-01	4600	1710	1500	Automobile-Catalog Toyota Avensis Estate Wagon 2.0 D-4D	https://www.automobile-catalog.com/car/2000/3605705/toyota_avensis_estate_wagon_2_0_d-4d.html
EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	2500	1515	1529	Automobile-Catalog Smart City-Coupé Smart and Pure 45	https://www.automobile-catalog.com/car/1999/3154295/smart_city-coupe_smart_and_pure_45.html
EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	2500	1515	1549	AutoData24 Smart Fortwo Coupe 0.6i 45	https://autodata24.com/smart/fortwo/fortwo-coupe/06i-45-hp/details
EU-MERCEDES-BENZ-V-CLASS-W638-MPV-5D-01	4659	1880	1844	Automobile-Catalog Mercedes-Benz V 200	https://www.automobile-catalog.com/car/1998/1529495/mercedes-benz_v_200.html
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827	Auto-Data Renault Kangoo I (KC) 1.2	https://www.auto-data.net/en/renault-kangoo-i-kc-1.2-58hp-10718
EU-FIAT-DUNA-146B-SEDAN-4D-01	4037	1558	1430	Automobile-Catalog Fiat Duna 70	https://www.automobile-catalog.com/car/1987/56285/fiat_duna_70.html
EU-FIAT-DUNA-146B-WAGON-5D-01	4037	1555	1430	Automobile-Catalog Fiat Duna Weekend 60	https://www.automobile-catalog.com/car/1987/56270/fiat_duna_weekend_60.html
EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	3708	1554	1410	Auto-Data ZAZ 1102 1.1	https://www.auto-data.net/en/zaz-1102-1.1-53hp-13942
EU-DAEWOO-NUBIRA-I-J100-HATCHBACK-5D-01	4248	1700	1425	Automobile-Catalog Daewoo Nubira 2.0 CDX Hatchback	https://www.automobile-catalog.com/car/1997/556565/daewoo_nubira_2_0_cdx_hatchback.html
EU-DAEWOO-NUBIRA-I-J150-HATCHBACK-5D-01	4250	1700	1430	Auto-Data Daewoo Nubira Hatchback II 2.0	https://www.auto-data.net/en/daewoo-nubira-hatchback-ii-2.0-133hp-16328
EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	4467	1700	1425	Automobile-Catalog Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/1997/556535/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-I-J150-SEDAN-4D-01	4495	1700	1430	Automobile-Catalog Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/2001/556820/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	4514	1700	1432	Automobile-Catalog Daewoo Nubira 1.6 SX Wagon	https://www.automobile-catalog.com/car/1997/556595/daewoo_nubira_1_6_sx_wagon.html
EU-DAEWOO-NUBIRA-I-J150-WAGON-5D-01	4550	1720	1430	Automobile-Catalog Daewoo Nubira 2.0 CDX Wagon	https://www.automobile-catalog.com/car/2003/557000/daewoo_nubira_2_0_cdx_wagon.html
EU-DAEWOO-LEGANZA-V100-SEDAN-4D-01	4671	1779	1437	Automobile-Catalog Daewoo Leganza 2.0 CDX	https://www.automobile-catalog.com/car/1997/557225/daewoo_leganza_2_0_cdx.html
```

## 下一步优先处理

1. 优先处理 Jumper I 与 Ducato II 的车长、车顶和 Bus/Van 分支，先匹配已有 SWB/MWB/LWB、低顶/高顶缓存组。
2. 闭合 Freelander I 的三门/五门及外部备胎长度边界。
3. 解决 Seicento 的改款与高度冲突。
4. 最后集中处理 Lanos 的 Hatchback/Sedan、三门/五门和改款范围。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/2000/3605705/toyota_avensis_estate_wagon_2_0_d-4d.html "https://www.automobile-catalog.com/car/2000/3605705/toyota_avensis_estate_wagon_2_0_d-4d.html"
[2]: https://www.auto-data.net/en/fiat-seicento-187-0.9-39hp-7263 "https://www.auto-data.net/en/fiat-seicento-187-0.9-39hp-7263"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8101-8200_ktype_dimension_mapping_final.tsv
- all_8101-8200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮完成 9 个 PENDING Ktype，新增 17 条 READY 映射和 8 个尺寸组。
* Seicento／600 按标准车身、Sporting 外部套件和 2005 年后 Fiat 600 外廓拆分。([汽车数据网][1])
* Freelander I 按三门 Hardback 与五门 Station Wagon 拆分；两者三维相同，但门体和车身结构不同，因此分别建组。([汽车目录档案][2])
* Lanos Hatchback 按三门、五门分别建组，Sedan 使用独立四门组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：93
* READY 映射行：123
* PENDING 输入 Ktype：7
* 已确认并引用尺寸组：65
* 本轮首次创建尺寸组：8
* 剩余 PENDING：8949–8953、8959–8960
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8969_standard	8969	Hatchback	Seicento (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	MEDIUM	标准车身物理分支。	READY
8969_600	8969	Hatchback	600 (187)	187	3	EU-FIAT-600-187-HATCHBACK-3D-01	MEDIUM	2005年后600名称及外廓分支。	READY
8970_standard	8970	Hatchback	Seicento (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	MEDIUM	标准车身物理分支。	READY
8970_sporting	8970	Hatchback	Seicento Sporting (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-SPORTING-01	MEDIUM	Sporting外部套件物理分支。	READY
8970_600	8970	Hatchback	600 (187)	187	3	EU-FIAT-600-187-HATCHBACK-3D-01	MEDIUM	2005年后600名称及外廓分支。	READY
8985_3dr	8985	SUV	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	HIGH	三门Hardback物理分支。	READY
8985_5dr	8985	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	HIGH	五门Station Wagon物理分支。	READY
8986_3dr	8986	SUV	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	HIGH	三门Hardback物理分支。	READY
8986_5dr	8986	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	HIGH	五门Station Wagon物理分支。	READY
9030_3dr	9030	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9030_5dr	9030	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9031	9031	Sedan	Lanos I	KLAT	4	EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	HIGH		READY
9032_3dr	9032	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9032_5dr	9032	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9033	9033	Sedan	Lanos I	KLAT	4	EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	HIGH		READY
9034_3dr	9034	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9034_5dr	9034	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	3319	1508	1440	Auto-Data Fiat Seicento 0.9	https://www.auto-data.net/en/fiat-seicento-187-0.9-39hp-7263
EU-FIAT-SEICENTO-187-HATCHBACK-3D-SPORTING-01	3332	1508	1445	Automobile-Catalog 1998 Fiat Seicento Sporting	https://www.automobile-catalog.com/car/1998/722750/fiat_seicento_sporting.html
EU-FIAT-600-187-HATCHBACK-3D-01	3337	1508	1420	Automobile-Catalog 2005 Fiat 600 1.1	https://www.automobile-catalog.com/car/2005/722885/fiat_600_1_1.html
EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	4382	1805	1757	Automobile-Catalog 1998 Land Rover Freelander 1.8 Xi Hardback; Land Rover Freelander 1998 official brochure	https://www.automobile-catalog.com/car/1998/1401335/land_rover_freelander_1_8_xi_hardback.html;https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Freelander-1998-UK.pdf
EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	4382	1805	1757	Land Rover Freelander 1998 official brochure; Drive.Place Land Rover Freelander I 5-door	https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Freelander-1998-UK.pdf;https://land-rover.drive.place/freelander/i/group_offroad_5d/123792
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	4074	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 SX Hatchback; Automobile-Catalog Daewoo Lanos model catalogue	https://www.automobile-catalog.com/car/1997/555770/daewoo_lanos_1_5_sx_hatchback.html;https://www.automobile-catalog.com/model/daewoo/lanos.html
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	4074	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 SX Hatchback; Automobile-Catalog Daewoo Lanos model catalogue	https://www.automobile-catalog.com/car/1997/555770/daewoo_lanos_1_5_sx_hatchback.html;https://www.automobile-catalog.com/model/daewoo/lanos.html
EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	4237	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 S Sedan	https://www.automobile-catalog.com/car/1997/1340000/daewoo_lanos_1_5_s_sedan.html
```

## 下一步优先处理

1. 将 Citroën Jumper I 的 8949–8953 按 SWB／MWB、低顶／高顶边界批量关联现有 `230P` 缓存组。
2. 将 Fiat Ducato 8959–8960 按 Van／Bus 及长度、车顶分支关联现有 Ducato II `230P` 缓存组。
3. PENDING 归零后仅执行一次机械闭合检查，并直接输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/fiat-seicento-187-0.9-39hp-7263?utm_source=chatgpt.com "Specs of Fiat Seicento (187) 0.9 (39 Hp) /1998, 1999, 2000"
[2]: https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Freelander-1998-UK.pdf?utm_source=chatgpt.com "Land Rover Freelander (1998) UK"
[3]: https://www.automobile-catalog.com/model/daewoo/lanos.html?utm_source=chatgpt.com "Daewoo Lanos (T100-T150) data and specifications catalogue"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_8101-8200_ktype_dimension_mapping_final.tsv
- all_8101-8200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 剩余 7 个 Ktype 已全部通过现有 Jumper I／Ducato II 缓存尺寸组闭合。
* 已完成固定表头、唯一性、引用闭合、尺寸与来源非空检查。
* 两张最终 TSV 文件已生成并通过机械校验。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* 最终映射行：145
* PENDING：0
* 最终尺寸组：75
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一且引用闭合：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
8934	8934	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8935	8935	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8936	8936	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8937_prefl	8937	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	HIGH	改款前外廓。	READY
8937_facelift	8937	Wagon	Avensis I (T22)	T22	5	EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-FACELIFT-01	HIGH	改款后外廓。	READY
8938	8938	MPV	Picnic I	XM1	5	EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	HIGH		READY
8939	8939	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8940	8940	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8941	8941	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8942	8942	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8943	8943	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8944	8944	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8945	8945	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8946	8946	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8947	8947	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8948	8948	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8949_swb_lowroof	8949	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8949_mwb_lowroof	8949	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8949_mwb_highroof	8949	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8950_swb_lowroof	8950	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8950_mwb_lowroof	8950	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8950_mwb_highroof	8950	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8951_swb_lowroof	8951	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8951_mwb_lowroof	8951	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8951_mwb_highroof	8951	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8952_swb_lowroof	8952	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8952_mwb_lowroof	8952	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8952_mwb_highroof	8952	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8953_swb_lowroof	8953	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8953_mwb_lowroof	8953	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8953_mwb_highroof	8953	Van	Jumper I	230P		EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8955	8955	MPV	Berlingo I	M49	5	EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	HIGH		READY
8957	8957	Hatchback	Xsara I Phase I	N1	5	EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	HIGH		READY
8958	8958	MPV	Sharan I	7M	5	EU-VW-SHARAN-I-MPV-01	HIGH	第一代同一外廓组。	READY
8959_swb_lowroof	8959	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	HIGH	SWB低顶物理分支。	READY
8959_swb_highroof	8959	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶物理分支。	READY
8959_mwb_lowroof	8959	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	HIGH	MWB低顶物理分支。	READY
8959_mwb_highroof	8959	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	HIGH	MWB高顶物理分支。	READY
8959_lwb_highroof	8959	Van	Ducato II	230P		EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶物理分支。	READY
8960_swb	8960	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-SWB-01	HIGH	SWB Bus物理分支。	READY
8960_mwb_highroof	8960	MPV	Ducato II	230P		EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	HIGH	MWB高顶Bus物理分支。	READY
8961_3dr	8961	Hatchback	Punto I	176	3	EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8961_5dr	8961	Hatchback	Punto I	176	5	EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8962	8962	Convertible	Punto I Cabrio	176C	2	EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	HIGH		READY
8963	8963	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
8964	8964	Sedan	3 Series E46	E46	4	EU-BMW-3-E46-SEDAN-4D-01	HIGH		READY
8965	8965	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8966	8966	Wagon	A6 C5	4B5	5	EU-AUDI-A6-C5-4B5-WAGON-5D-01	HIGH		READY
8967	8967	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8968	8968	Sedan	A6 C5	4B2	4	EU-AUDI-A6-C5-4B2-SEDAN-01	HIGH		READY
8969_standard	8969	Hatchback	Seicento (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	MEDIUM	标准车身物理分支。	READY
8969_600	8969	Hatchback	600 (187)	187	3	EU-FIAT-600-187-HATCHBACK-3D-01	MEDIUM	2005年后600名称及外廓分支。	READY
8970_standard	8970	Hatchback	Seicento (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	MEDIUM	标准车身物理分支。	READY
8970_sporting	8970	Hatchback	Seicento Sporting (187)	187	3	EU-FIAT-SEICENTO-187-HATCHBACK-3D-SPORTING-01	MEDIUM	Sporting外部套件物理分支。	READY
8970_600	8970	Hatchback	600 (187)	187	3	EU-FIAT-600-187-HATCHBACK-3D-01	MEDIUM	2005年后600名称及外廓分支。	READY
8971	8971	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8972	8972	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8973	8973	Hatchback	Lupo I	6X	3	EU-VW-LUPO-I-6X-HATCHBACK-3D-01	HIGH		READY
8974	8974	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8975	8975	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8976	8976	Wagon	626 V	GW	5	EU-MAZDA-626-V-GW-WAGON-5D-01	HIGH		READY
8977	8977	Hatchback	626 V	GF	5	EU-MAZDA-626-V-GF-HATCHBACK-5D-01	HIGH		READY
8978_prefl	8978	Coupe	City-Coupé (W450)	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	HIGH	改款前外廓。	READY
8978_facelift	8978	Coupe	City-Coupé (W450)	W450	3	EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	HIGH	改款后外廓。	READY
8979_prefl	8979	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH	改款前外廓。	READY
8979_facelift	8979	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	HIGH	改款后外廓。	READY
8980	8980	Hatchback	New Beetle I	9C	3	EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	HIGH		READY
8981	8981	Coupe	Puma I	ECT	3	EU-FORD-PUMA-I-ECT-COUPE-3D-01	HIGH		READY
8982	8982	Hatchback	Atos I	MX	5	EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	MEDIUM	同代1.0车型外廓；功率标注存在市场差异。	READY
8983	8983	MPV	V-Class W638	W638	5	EU-MERCEDES-BENZ-V-CLASS-W638-MPV-5D-01	HIGH		READY
8984	8984	MPV	Wagon R+ I	EM	5	EU-SUZUKI-WAGON-R-EM-MPV-5D-01	MEDIUM	同代1.0车型外廓；功率标注存在市场差异。	READY
8985_3dr	8985	SUV	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	HIGH	三门Hardback物理分支。	READY
8985_5dr	8985	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	HIGH	五门Station Wagon物理分支。	READY
8986_3dr	8986	SUV	Freelander I	LN	3	EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	HIGH	三门Hardback物理分支。	READY
8986_5dr	8986	SUV	Freelander I	LN	5	EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	HIGH	五门Station Wagon物理分支。	READY
8987	8987	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8988	8988	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8989	8989	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8990	8990	MPV	Kangoo I Phase I	KC	5	EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	HIGH		READY
8991_prefl	8991	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	HIGH	改款前外廓。	READY
8991_facelift	8991	Hatchback	Laguna I	B56	5	EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	HIGH	改款后外廓。	READY
8992_prefl	8992	Wagon	Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	HIGH	改款前外廓。	READY
8992_facelift	8992	Wagon	Laguna I	K56	5	EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
8993_3dr	8993	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8993_5dr	8993	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8994_3dr	8994	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8994_5dr	8994	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8995_3dr	8995	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8995_5dr	8995	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8996_3dr	8996	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8996_5dr	8996	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8997_3dr	8997	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8997_5dr	8997	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8998_3dr	8998	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8998_5dr	8998	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
8999_3dr	8999	Hatchback	Astra G	F08	3	EU-OPEL-ASTRA-G-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
8999_5dr	8999	Hatchback	Astra G	F48	5	EU-OPEL-ASTRA-G-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9000	9000	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9001	9001	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9002	9002	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9003	9003	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9004	9004	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9005	9005	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9006	9006	Wagon	Astra G	F35	5	EU-OPEL-ASTRA-G-CARAVAN-5D-01	HIGH		READY
9007_prefl	9007	Sedan	Omega B	V94	4	EU-OPEL-OMEGA-B-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
9007_facelift	9007	Sedan	Omega B	V94	4	EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
9008_prefl	9008	Wagon	Omega B	V94	5	EU-OPEL-OMEGA-B-WAGON-PREFL-01	HIGH	改款前外廓。	READY
9008_facelift	9008	Wagon	Omega B	V94	5	EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
9009_prefl	9009	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	HIGH	改款前外廓。	READY
9009_facelift	9009	Sedan	Vectra B	J96	4	EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	HIGH	改款后外廓。	READY
9010_prefl	9010	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	HIGH	改款前外廓。	READY
9010_facelift	9010	Hatchback	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	HIGH	改款后外廓。	READY
9011_prefl	9011	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	HIGH	改款前外廓。	READY
9011_facelift	9011	Wagon	Vectra B	J96	5	EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	HIGH	改款后外廓。	READY
9012_3dr	9012	Hatchback	Corsa B	S93	3	EU-OPEL-CORSA-B-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9012_5dr	9012	Hatchback	Corsa B	S93	5	EU-OPEL-CORSA-B-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9013	9013	Hatchback	XM II (Y4)	Y4	5	EU-CITROEN-XM-Y4-HATCHBACK-01	HIGH		READY
9014	9014	Wagon	XM II (Y4)	Y4	5	EU-CITROEN-XM-Y4-WAGON-01	HIGH		READY
9015	9015	Sedan	605 I Facelift	6B	4	EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	HIGH		READY
9016	9016	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9017	9017	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9018	9018	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9019	9019	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9020	9020	Sedan	Duna	146B	4	EU-FIAT-DUNA-146B-SEDAN-4D-01	HIGH		READY
9021	9021	Wagon	Duna Weekend	146B	5	EU-FIAT-DUNA-146B-WAGON-5D-01	HIGH		READY
9022	9022	Hatchback	Tavria 1102	1102	3	EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	HIGH		READY
9023	9023	Hatchback	Tavria 1102	1102	3	EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	HIGH		READY
9024_prefl	9024	Hatchback	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-HATCHBACK-5D-01	HIGH	改款前外廓。	READY
9024_facelift	9024	Hatchback	Nubira I Phase II	J150	5	EU-DAEWOO-NUBIRA-I-J150-HATCHBACK-5D-01	HIGH	改款后外廓。	READY
9025_prefl	9025	Sedan	Nubira I Phase I	J100	4	EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	HIGH	改款前外廓。	READY
9025_facelift	9025	Sedan	Nubira I Phase II	J150	4	EU-DAEWOO-NUBIRA-I-J150-SEDAN-4D-01	HIGH	改款后外廓。	READY
9026	9026	Sedan	Nubira I Phase I	J100	4	EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	HIGH		READY
9027	9027	Wagon	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	HIGH		READY
9028_prefl	9028	Wagon	Nubira I Phase I	J100	5	EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	HIGH	改款前外廓。	READY
9028_facelift	9028	Wagon	Nubira I Phase II	J150	5	EU-DAEWOO-NUBIRA-I-J150-WAGON-5D-01	HIGH	改款后外廓。	READY
9029	9029	Sedan	Leganza	V100	4	EU-DAEWOO-LEGANZA-V100-SEDAN-4D-01	HIGH		READY
9030_3dr	9030	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9030_5dr	9030	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9031	9031	Sedan	Lanos I	KLAT	4	EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	HIGH		READY
9032_3dr	9032	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9032_5dr	9032	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9033	9033	Sedan	Lanos I	KLAT	4	EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	HIGH		READY
9034_3dr	9034	Hatchback	Lanos I	KLAT	3	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	HIGH	三门物理分支。	READY
9034_5dr	9034	Hatchback	Lanos I	KLAT	5	EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	HIGH	五门物理分支。	READY
9035	9035	Wagon	Passat B5	3B5	5	EU-VW-PASSAT-B5-3B5-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_8101-8200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-PREFL-01	4570	1710	1500	Auto-Data Toyota Avensis Wagon (T22) 2.0	https://www.auto-data.net/en/toyota-avensis-wagon-t22-2.0-128hp-3620
EU-TOYOTA-AVENSIS-I-T22-WAGON-5D-FACELIFT-01	4600	1710	1500	Automobile-Catalog Toyota Avensis Estate Wagon 2.0 D-4D	https://www.automobile-catalog.com/car/2000/3605705/toyota_avensis_estate_wagon_2_0_d-4d.html
EU-TOYOTA-PICNIC-I-XM1-MPV-5D-01	4530	1695	1620	Auto-Data Toyota Picnic XM1	https://www.auto-data.net/en/toyota-picnic-model-404
EU-AUDI-A6-C5-4B5-WAGON-5D-01	4796	1810	1479	Auto-Data Audi A6 Avant (4B,C5) 2.8 V6	https://www.auto-data.net/en/audi-a6-avant-4b-c5-2.8-v6-30v-193hp-tiptronic-26842
EU-CITROEN-JUMPER-I-230P-MPV-SWB-LOWROOF-01	4655	1998	2150	Citroën Jumper I 230P locked cross-batch specification; EngineInDetail Jumper I	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-CITROEN-JUMPER-I-230P-MPV-MWB-LOWROOF-01	5005	1998	2150	Citroën Jumper I 230P locked cross-batch specification; EngineInDetail Jumper I	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-CITROEN-JUMPER-I-230P-MPV-MWB-HIGHROOF-01	5005	1998	2470	Citroën Jumper I 230P locked cross-batch specification; EngineInDetail Jumper I	https://www.engineindetail.com/cars/citroen/jumper/jumper-i-estate-wagon-1997-2002
EU-CITROEN-BERLINGO-I-M49-MPV-VAN-01	4108	1698	1802	Automobile-Catalog Citroën Berlingo Multispace 1.8i	https://www.automobile-catalog.com/car/2000/547760/citroen_berlingo_multispace_1_8i.html
EU-CITROEN-XSARA-I-N1-HATCHBACK-5D-01	4167	1698	1405	Automobile-Catalog 1997 Citroën Xsara 1.9 D SX	https://www.automobile-catalog.com/car/1997/546530/citroen_xsara_1_9_d_sx.html
EU-VW-SHARAN-I-MPV-01	4634	1810	1730	VehicleScore Volkswagen Sharan dimensions	https://vehiclescore.co.uk/car-dimensions-check/volkswagen/sharan
EU-FIAT-DUCATO-II-230P-VAN-SWB-LOWROOF-01	4655	1998	2150	Fiat Ducato 230 locked cross-batch specification; MotoBase Ducato L1H1	https://motobase.pl/en/fiat%2Cducato%2Cii_typ_230_244%2Cfurgon_l1h1_1%2Csamochody_osobowe.html
EU-FIAT-DUCATO-II-230P-VAN-SWB-HIGHROOF-01	4655	1998	2470	Fiat Ducato 230 locked cross-batch specification; RTA Ducato 1994 technical data	https://www.scribd.com/document/804996593/Rta-Ducato-94-Et-Apres
EU-FIAT-DUCATO-II-230P-VAN-MWB-LOWROOF-01	5005	1998	2150	Fiat Ducato 230 locked cross-batch specification; RTA Ducato 1994 technical data	https://www.scribd.com/document/804996593/Rta-Ducato-94-Et-Apres
EU-FIAT-DUCATO-II-230P-VAN-MWB-HIGHROOF-01	5005	1998	2470	Fiat Ducato 230 locked cross-batch specification; RTA Ducato 1994 technical data	https://www.scribd.com/document/804996593/Rta-Ducato-94-Et-Apres
EU-FIAT-DUCATO-II-230P-VAN-LWB-HIGHROOF-01	5505	1998	2480	Fiat Ducato 230 locked cross-batch specification; MotoBase Ducato L3H2	https://motobase.pl/en/fiat%2Cducato%2Cii_typ_230_244%2Cfurgon_l3h2%2Csamochody_osobowe.html
EU-FIAT-DUCATO-II-230P-BUS-SWB-01	4655	1998	2150	Fiat Ducato 230 locked cross-batch specification; EngineInDetail Ducato 230 Estate/Wagon	https://www.engineindetail.com/cars/fiat/ducato/ducato-230-estate-wagon-1994-2002
EU-FIAT-DUCATO-II-230P-BUS-MWB-HIGHROOF-01	5005	1998	2465	Fiat Ducato 230 locked cross-batch specification; EngineInDetail Ducato 230 Estate/Wagon	https://www.engineindetail.com/cars/fiat/ducato/ducato-230-estate-wagon-1994-2002
EU-FIAT-PUNTO-I-176-HATCHBACK-3D-01	3760	1625	1460	Auto-Data Fiat Punto model specifications	https://www.auto-data.net/en/fiat-punto-model-761
EU-FIAT-PUNTO-I-176-HATCHBACK-5D-01	3760	1625	1460	Auto-Data Fiat Punto model specifications	https://www.auto-data.net/en/fiat-punto-model-761
EU-FIAT-PUNTO-I-176C-CONVERTIBLE-01	3760	1625	1447	Automobile-Catalog Fiat Punto Cabrio S	https://www.automobile-catalog.com/car/1999/720065/fiat_punto_cabrio_s.html
EU-BMW-3-E46-SEDAN-4D-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan (E46) 318i	https://www.auto-data.net/en/bmw-3-series-sedan-e46-318i-118hp-9978
EU-AUDI-A6-C5-4B2-SEDAN-01	4796	1810	1453	Audi Drive.Place A6 C5 Sedan specifications	https://audi.drive.place/a6/ii_res/group_sedan/15544
EU-FIAT-SEICENTO-187-HATCHBACK-3D-STANDARD-01	3319	1508	1440	Auto-Data Fiat Seicento 0.9	https://www.auto-data.net/en/fiat-seicento-187-0.9-39hp-7263
EU-FIAT-600-187-HATCHBACK-3D-01	3337	1508	1420	Automobile-Catalog 2005 Fiat 600 1.1	https://www.automobile-catalog.com/car/2005/722885/fiat_600_1_1.html
EU-FIAT-SEICENTO-187-HATCHBACK-3D-SPORTING-01	3332	1508	1445	Automobile-Catalog 1998 Fiat Seicento Sporting	https://www.automobile-catalog.com/car/1998/722750/fiat_seicento_sporting.html
EU-VW-LUPO-I-6X-HATCHBACK-3D-01	3527	1639	1460	Volkswagen Newsroom Lupo profile	https://www.volkswagen-newsroom.com/en/vehicle-data-lupo-profile-19705
EU-MAZDA-626-V-GW-WAGON-5D-01	4660	1710	1515	Auto-Data Mazda 626 V Station Wagon (GF,GW) 2.0 H.P.	https://www.auto-data.net/en/mazda-626-v-station-wagon-gf-gw-2.0-h.p.-136hp-11275
EU-MAZDA-626-V-GF-HATCHBACK-5D-01	4574	1710	1430	Auto-Data Mazda 626 V Hatchback (GF) 2.0	https://www.auto-data.net/en/mazda-626-v-hatchback-gf-2.0-136hp-11279
EU-SMART-CITY-COUPE-W450-COUPE-3D-PREFL-01	2500	1515	1529	Automobile-Catalog Smart City-Coupé Smart and Pure 45	https://www.automobile-catalog.com/car/1999/3154295/smart_city-coupe_smart_and_pure_45.html
EU-SMART-CITY-COUPE-W450-COUPE-3D-FACELIFT-01	2500	1515	1549	AutoData24 Smart Fortwo Coupe 0.6i 45	https://autodata24.com/smart/fortwo/fortwo-coupe/06i-45-hp/details
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-PREFL-01	4081	1725	1500	Auto-Data Volkswagen New Beetle (9C) 2.0	https://www.auto-data.net/en/volkswagen-new-beetle-9c-2.0-115hp-automatic-27939
EU-VW-NEW-BEETLE-I-9C-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Auto-Data Volkswagen New Beetle facelift 2005 2.0	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-2.0-115hp-28090
EU-FORD-PUMA-I-ECT-COUPE-3D-01	3984	1674	1345	Auto-Data Ford Puma Coupe (ECT) 1.4 16V	https://www.auto-data.net/en/ford-puma-coupe-ect-1.4-16v-90hp-8008
EU-HYUNDAI-ATOS-I-HATCHBACK-5D-01	3495	1495	1615	Auto-Data Hyundai Atos 1.0 i	https://www.auto-data.net/en/hyundai-atos-1.0-i-56hp-automatic-29338
EU-MERCEDES-BENZ-V-CLASS-W638-MPV-5D-01	4659	1880	1844	Automobile-Catalog Mercedes-Benz V 200	https://www.automobile-catalog.com/car/1998/1529495/mercedes-benz_v_200.html
EU-SUZUKI-WAGON-R-EM-MPV-5D-01	3410	1575	1700	Auto-Data Suzuki Wagon R+ (EM) 1.0 i	https://www.auto-data.net/en/suzuki-wagon-r-em-1.0-i-69hp-automatic-23925
EU-LAND-ROVER-FREELANDER-I-LN-SUV-3D-HARDBACK-01	4382	1805	1757	Automobile-Catalog 1998 Land Rover Freelander 1.8 Xi Hardback; Land Rover Freelander 1998 official brochure	https://www.automobile-catalog.com/car/1998/1401335/land_rover_freelander_1_8_xi_hardback.html;https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Freelander-1998-UK.pdf
EU-LAND-ROVER-FREELANDER-I-LN-SUV-5D-01	4382	1805	1757	Land Rover Freelander 1998 official brochure; Drive.Place Land Rover Freelander I 5-door	https://autocatalogarchive.com/wp-content/uploads/2017/05/Land-Rover-Freelander-1998-UK.pdf;https://land-rover.drive.place/freelander/i/group_offroad_5d/123792
EU-RENAULT-KANGOO-I-KC-MPV-5D-PREFL-01	3995	1663	1827	Auto-Data Renault Kangoo I (KC) 1.2	https://www.auto-data.net/en/renault-kangoo-i-kc-1.2-58hp-10718
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-01	4508	1752	1432	EncyCARpedia Renault Laguna 1.6 16v	https://www.encycarpedia.com/renault/98-laguna-1-6-16v-fastback
EU-RENAULT-LAGUNA-I-B56-HATCHBACK-02	4508	1752	1433	Automobile-Catalog 1998 Renault Laguna 1.6 16V	https://www.automobile-catalog.com/car/1998/2945960/renault_laguna_1_6_16v.html
EU-RENAULT-LAGUNA-I-K56-WAGON-PREFL-01	4620	1752	1448	Automobile-Catalog 1997 Renault Laguna Wagon 2.0i	https://www.automobile-catalog.com/car/1997/2945780/renault_laguna_wagon_2_0i.html
EU-RENAULT-LAGUNA-I-K56-WAGON-FACELIFT-01	4628	1752	1448	Automobile-Catalog 1998 Renault Laguna Wagon 2.0 8V	https://www.automobile-catalog.com/car/1998/2946080/renault_laguna_wagon_2_0_8v.html
EU-OPEL-ASTRA-G-HATCHBACK-3D-01	4110	1709	1425	Auto-Data Opel Astra G 1.6 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.6-ecotec-16v-101hp-automatic-25829
EU-OPEL-ASTRA-G-HATCHBACK-5D-01	4110	1709	1425	Auto-Data Opel Astra G 1.6 Ecotec 16V	https://www.auto-data.net/en/opel-astra-g-1.6-ecotec-16v-101hp-automatic-25829
EU-OPEL-ASTRA-G-CARAVAN-5D-01	4288	1709	1510	Auto-Data Opel Astra G Caravan 1.6	https://www.auto-data.net/en/opel-astra-g-caravan-1.6-75hp-automatic-26385
EU-OPEL-OMEGA-B-SEDAN-PREFL-01	4785	1785	1450	Auto-Data Opel Omega model specifications	https://www.auto-data.net/en/opel-omega-model-245
EU-OPEL-OMEGA-B-SEDAN-FACELIFT-01	4898	1785	1455	Auto-Data Opel Omega model specifications	https://www.auto-data.net/en/opel-omega-model-245
EU-OPEL-OMEGA-B-WAGON-PREFL-01	4820	1785	1500	Auto-Data Opel Omega model specifications	https://www.auto-data.net/en/opel-omega-model-245
EU-OPEL-OMEGA-B-WAGON-FACELIFT-01	4898	1776	1540	Opel Omega B locked cross-batch specification; Auto-Data Opel Omega model specifications	https://www.auto-data.net/en/opel-omega-model-245
EU-OPEL-VECTRA-B-J96-SEDAN-PREFL-01	4477	1707	1425	Opel Vectra B locked cross-batch specification; Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-J96-SEDAN-FACELIFT-01	4495	1707	1425	Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-J96-HATCHBACK-PREFL-01	4495	1707	1425	Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-J96-HATCHBACK-FACELIFT-01	4495	1707	1425	Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-J96-WAGON-PREFL-01	4490	1707	1490	Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-VECTRA-B-J96-WAGON-FACELIFT-01	4490	1707	1490	Auto-Data Opel Vectra model specifications	https://www.auto-data.net/en/opel-vectra-model-251
EU-OPEL-CORSA-B-HATCHBACK-3D-01	3740	1610	1420	Opel Drive.Place Corsa B 3-door	https://opel.drive.place/corsa/b/group_hatchback_3d/209318
EU-OPEL-CORSA-B-HATCHBACK-5D-01	3740	1610	1420	Auto-Data Opel Corsa B specifications	https://www.auto-data.net/en/opel-corsa-b-generation-528
EU-CITROEN-XM-Y4-HATCHBACK-01	4708	1794	1396	Auto-Data Citroën XM model specifications	https://www.auto-data.net/en/citroen-xm-model-1688
EU-CITROEN-XM-Y4-WAGON-01	4963	1794	1467	Citroën XM technical specification	https://www.ckc.dk/pubs/xm_tech_spec.pdf
EU-PEUGEOT-605-I-FACELIFT-SEDAN-V6-01	4765	1799	1415	FastCarCheck Peugeot 605 3.0 specifications	https://fastcarcheck.uk/specs/make/peugeot/605/202228
EU-FIAT-DUNA-146B-SEDAN-4D-01	4037	1558	1430	Automobile-Catalog Fiat Duna 70	https://www.automobile-catalog.com/car/1987/56285/fiat_duna_70.html
EU-FIAT-DUNA-146B-WAGON-5D-01	4037	1555	1430	Automobile-Catalog Fiat Duna Weekend 60	https://www.automobile-catalog.com/car/1987/56270/fiat_duna_weekend_60.html
EU-ZAZ-TAVRIA-1102-HATCHBACK-3D-01	3708	1554	1410	Auto-Data ZAZ 1102 1.1	https://www.auto-data.net/en/zaz-1102-1.1-53hp-13942
EU-DAEWOO-NUBIRA-I-J100-HATCHBACK-5D-01	4248	1700	1425	Automobile-Catalog Daewoo Nubira 2.0 CDX Hatchback	https://www.automobile-catalog.com/car/1997/556565/daewoo_nubira_2_0_cdx_hatchback.html
EU-DAEWOO-NUBIRA-I-J150-HATCHBACK-5D-01	4250	1700	1430	Auto-Data Daewoo Nubira Hatchback II 2.0	https://www.auto-data.net/en/daewoo-nubira-hatchback-ii-2.0-133hp-16328
EU-DAEWOO-NUBIRA-I-J100-SEDAN-4D-01	4467	1700	1425	Automobile-Catalog Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/1997/556535/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-I-J150-SEDAN-4D-01	4495	1700	1430	Automobile-Catalog Daewoo Nubira 2.0 CDX Sedan	https://www.automobile-catalog.com/car/2001/556820/daewoo_nubira_2_0_cdx_sedan.html
EU-DAEWOO-NUBIRA-I-J100-WAGON-5D-01	4514	1700	1432	Automobile-Catalog Daewoo Nubira 1.6 SX Wagon	https://www.automobile-catalog.com/car/1997/556595/daewoo_nubira_1_6_sx_wagon.html
EU-DAEWOO-NUBIRA-I-J150-WAGON-5D-01	4550	1720	1430	Automobile-Catalog Daewoo Nubira 2.0 CDX Wagon	https://www.automobile-catalog.com/car/2003/557000/daewoo_nubira_2_0_cdx_wagon.html
EU-DAEWOO-LEGANZA-V100-SEDAN-4D-01	4671	1779	1437	Automobile-Catalog Daewoo Leganza 2.0 CDX	https://www.automobile-catalog.com/car/1997/557225/daewoo_leganza_2_0_cdx.html
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-3D-01	4074	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 SX Hatchback	https://www.automobile-catalog.com/car/1997/555770/daewoo_lanos_1_5_sx_hatchback.html
EU-DAEWOO-LANOS-I-KLAT-HATCHBACK-5D-01	4074	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 SX Hatchback	https://www.automobile-catalog.com/car/1997/555770/daewoo_lanos_1_5_sx_hatchback.html
EU-DAEWOO-LANOS-I-KLAT-SEDAN-4D-01	4237	1678	1432	Automobile-Catalog 1997 Daewoo Lanos 1.5 S Sedan	https://www.automobile-catalog.com/car/1997/1340000/daewoo_lanos_1_5_s_sedan.html
EU-VW-PASSAT-B5-3B5-WAGON-5D-01	4670	1740	1500	Volkswagen Newsroom Passat B5 profile	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b5-profile-19547
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_8101-8200_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_8101-8200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_8101-8200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（10060 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（3082 行）

- 尺寸冲突协调：
  - EU-MAZDA-626-V-GF-HATCHBACK-5D-01 -> EU-MAZDA-626-V-GF-HATCHBACK-5D-02：4575x1710x1430 与 4574x1710x1430，创建新尺寸组
