# 任务：all 第 6401-6500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0065__d9338031


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 6401-6500 行

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
all 第 6401-6500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6401-6500_ktype_dimension_mapping_final.tsv
- all_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-AUDI-100-C1-COUPE-01	4398	1750	1340
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421
EU-AUDI-100-C2-AVANT-01	4587	1768	1390
EU-AUDI-100-C2-SEDAN-01	4680	1768	1390
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390
EU-AUDI-100-C2-WAGON-FACELIFT-01	4590	1768	1390
EU-AUDI-100-C2-WAGON-PREFL-01	4587	1768	1390
EU-AUDI-100-C3-AVANT-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422
EU-AUDI-100-C3-SEDAN-02	4793	1814	1421
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422
EU-AUDI-100-C3-WAGON-QUATTRO-01	4793	1814	1422
EU-AUDI-100-C4-S4-AVANT-WAGON-01	4790	1805	1422
EU-AUDI-100-C4-S4-SEDAN-01	4790	1805	1420
EU-AUDI-100-C4-SEDAN-FWD-01	4790	1777	1431
EU-AUDI-100-C4-SEDAN-QUATTRO-01	4790	1777	1437
EU-AUDI-100-C4-WAGON-FWD-01	4790	1777	1440
EU-AUDI-100-C4-WAGON-QUATTRO-01	4790	1777	1448
EU-AUDI-80-B1-SEDAN-FACELIFT-01	4245	1600	1360
EU-AUDI-80-B1-SEDAN-PREFL-01	4220	1600	1362
EU-AUDI-80-B2-SEDAN-FACELIFT-01	4406	1682	1365
EU-AUDI-80-B2-SEDAN-PREFL-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-20-01	4383	1682	1376
EU-AUDI-80-B2-SEDAN-QUATTRO-22-01	4383	1682	1365
EU-AUDI-80-B2-SEDAN-QUATTRO-FACELIFT-01	4406	1682	1350
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397
EU-AUDI-80-B4-RS2-AVANT-01	4510	1695	1386
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406
EU-AUDI-80-B4-WAGON-01	4482	1695	1408
EU-BMW-501-502-V8-SEDAN-4D-01	4730	1780	1530
EU-BMW-503-CONVERTIBLE-2D-01	4750	1710	1430
EU-BMW-5-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-E28-SEDAN-01	4620	1700	1415
EU-BMW-5-E28-SEDAN-M535I-01	4605	1710	1400
EU-BMW-5-E34-M5-WAGON-01	4720	1751	1392
EU-BMW-5-E34-SEDAN-01	4720	1751	1412
EU-BMW-5-E34-SEDAN-IX-01	4720	1751	1421
EU-BMW-5-E34-SEDAN-M5-01	4720	1751	1392
EU-BMW-5-E34-WAGON-01	4720	1751	1417
EU-BMW-5-E34-WAGON-IX-01	4720	1751	1422
EU-BMW-5-E39-SEDAN-01	4775	1800	1435
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425
EU-BMW-5-SERIES-F10-SEDAN-FACELIFT-01	4907	1860	1464
EU-BMW-5-SERIES-F10-SEDAN-PREFL-01	4899	1860	1464
EU-BMW-5-SERIES-F11-WAGON-M550D-XDRIVE-01	4910	1860	1462
EU-FORD-C-MAX-II-MPV-FACELIFT-02	4379	1828	1610
EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626
EU-FORD-GRAND-C-MAX-II-MPV-01	4520	1828	1684
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658
EU-JAGUAR-XJ40-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ40-XJ81-SEDAN-01	4988	1798	1380
EU-JAGUAR-XJ-SC-XJ27-CONVERTIBLE-TARGA-01	4764	1793	1261
EU-JAGUAR-XJ-SERIES-III-SEDAN-01	4959	1770	1377
EU-JAGUAR-XJ-SERIES-III-SEDAN-02	4959	1770	1372
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375
EU-JAGUAR-XJ-SERIES-II-SEDAN-LWB-01	4945	1770	1375
EU-JAGUAR-XJS-XJ27-CONVERTIBLE-FACELIFT-01	4820	1793	1276
EU-JAGUAR-XJ-S-XJ27-CONVERTIBLE-PREFL-01	4764	1793	1254
EU-JAGUAR-XJS-XJ27-COUPE-FACELIFT-01	4820	1793	1254
EU-JAGUAR-XJ-S-XJ27-COUPE-PREFL-01	4764	1793	1261
EU-JAGUAR-XJ-X300-SEDAN-SWB-COMFORT-01	5023	1798	1314
EU-JAGUAR-XJ-X306-XJR-SEDAN-SWB-01	5023	1798	1303
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457
EU-VOLVO-740-SEDAN-4D-01	4785	1760	1430
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435
EU-VOLVO-760-SEDAN-FACELIFT-01	4790	1760	1410
EU-VOLVO-760-SEDAN-PREFL-01	4800	1750	1410
EU-VOLVO-760-WAGON-FACELIFT-01	4790	1760	1435
EU-VOLVO-760-WAGON-PREFL-01	4800	1750	1435

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Daimler	Daimler xj	Double SIX 6.0	Stufenheck	Heckantrieb	Benzin	229	311	Oct 1994	Jun 2003	2024-03-01	6822
Daimler	Coupe	Sovereign 4.2	Coupe	Heckantrieb	Benzin	127	172	Sep 1973	Dec 1977	2024-03-01	6823
Daimler	Coupe	Double SIX 5.3	Coupe	Heckantrieb	Benzin	213	289	May 1975	Dec 1977	2024-03-01	6824
Daimler	Limousine	4.2	Stufenheck	Heckantrieb	Benzin	123	167	Jun 1968	Dec 1991	2024-03-01	6825
Daimler	Limousine	4.2	Stufenheck	Heckantrieb	Benzin	131	178	Jan 1988	Dec 1991	2024-03-01	6826
Daimler	Landaulette	4.2	Cabriolet	Heckantrieb	Benzin	123	167	Mar 1974	Dec 1991	2024-03-01	6827
Daimler	Landaulette	4.2	Cabriolet	Heckantrieb	Benzin	131	178	Jan 1988	Dec 1991	2024-03-01	6828
Jaguar	Xj	6 2.8	Stufenheck	Heckantrieb	Benzin	110	149	Sep 1968	Oct 1975	2024-03-01	6829
BMW	1502-2002	1600-2	Cabriolet	Heckantrieb	Benzin	63	86	Dec 1967	Oct 1971	2024-03-01	6830
BMW	2000	CS	Coupe	Heckantrieb	Benzin	88	120	Oct 1965	Jun 1970	2024-03-01	6831
BMW	2000	C/ca	Coupe	Heckantrieb	Benzin	74	101	Oct 1965	Jun 1970	2024-03-01	6832
BMW	2.5-3.2	3.0 Csil	Coupe	Heckantrieb	Benzin	152	206	Jan 1974	Nov 1975	2024-03-01	6833
Jaguar	Xj	6 4.2	Stufenheck	Heckantrieb	Benzin	137	186	Oct 1969	May 1975	2024-03-01	6834
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	96	131	Aug 1972	Oct 1975	2024-03-01	6835
Jaguar	Xj	12 5.3	Stufenheck	Heckantrieb	Benzin	198	269	Jun 1972	Sep 1973	2024-03-01	6836
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	Feb 2011	Jun 2019	2024-03-01	6837
BMW	5	520 I	Stufenheck	Heckantrieb	Benzin	92	125	Mar 1972	Jul 1979	2024-03-01	6838
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	120	163	Dec 2010	Jun 2019	2024-03-01	6839
Jaguar	Xj	5.3	Coupe	Heckantrieb	Benzin	213	289	Sep 1975	Jul 1981	2024-03-01	6840
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	198	269	Jul 1968	May 1971	2024-03-01	6841
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	127	173	Mar 1971	Apr 1975	2024-03-01	6842
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	195	265	May 1964	Sep 1970	2024-03-01	6843
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	195	265	Jun 1966	Sep 1968	2024-03-01	6844
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	127	173	Mar 1971	Apr 1975	2024-03-01	6845
Jaguar	E-Type	V12 5.3	Coupe	Heckantrieb	Benzin	203	276	Mar 1971	Apr 1975	2024-03-01	6846
Jaguar	E-Type	4.2	Cabriolet	Heckantrieb	Benzin	198	269	Jul 1968	May 1971	2024-03-01	6847
Jaguar	E-Type	4.2	Cabriolet	Heckantrieb	Benzin	127	173	Mar 1971	Apr 1975	2024-03-01	6848
Jaguar	E-Type	V12 5.3	Cabriolet	Heckantrieb	Benzin	203	276	Mar 1971	Apr 1975	2024-03-01	6849
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Feb 2011	Jun 2019	2024-03-01	6850
Jaguar	E-Type	3.8	Coupe	Heckantrieb	Benzin	195	265	Apr 1961	Jul 1964	2024-03-01	6851
Jaguar	E-Type	4.2	Coupe	Heckantrieb	Benzin	127	173	May 1968	May 1971	2024-03-01	6852
Jaguar	E-Type	3.8	Cabriolet	Heckantrieb	Benzin	195	265	Apr 1961	Jul 1964	2024-03-01	6853
Jaguar	E-Type	4.2	Cabriolet	Heckantrieb	Benzin	195	265	May 1964	Sep 1968	2024-03-01	6854
DAF	33	0.7	Stufenheck	Heckantrieb	Benzin	21	29	Jul 1967	Sep 1974	2024-03-01	6855
DAF	44	0.8	Stufenheck	Heckantrieb	Benzin	25	34	Nov 1966	Sep 1974	2024-03-01	6856
DAF	44	0.8	Kombi	Heckantrieb	Benzin	25	34	May 1968	Sep 1974	2024-03-01	6857
DAF	55	1.1	Stufenheck	Heckantrieb	Benzin	33	45	Oct 1967	Sep 1972	2024-03-01	6858
DAF	55	1.1	Kombi	Heckantrieb	Benzin	33	45	Oct 1968	Sep 1972	2024-03-01	6859
DAF	55	1.1 Marathon	Stufenheck	Heckantrieb	Benzin	40	54	Dec 1971	Sep 1972	2024-03-01	6860
DAF	55	1.1 Marathon	Coupe	Heckantrieb	Benzin	40	54	Dec 1971	Sep 1972	2024-03-01	6861
DAF	55	1.1	Coupe	Heckantrieb	Benzin	33	45	May 1968	Sep 1972	2024-03-01	6862
DAF	46	0.8 DE Luxe	Stufenheck	Heckantrieb	Benzin	25	34	Sep 1974	Aug 1975	2024-03-01	6863
DAF	46	0.8 Super LUX	Kombi	Heckantrieb	Benzin	25	34	Sep 1974	Aug 1975	2024-03-01	6864
DAF	66	1.1	Stufenheck	Heckantrieb	Benzin	35	48	Oct 1972	Aug 1975	2024-03-01	6865
DAF	66	1.1 SL	Stufenheck	Heckantrieb	Benzin	40	54	Oct 1972	Aug 1975	2024-03-01	6866
DAF	66	1.1	Kombi	Heckantrieb	Benzin	35	48	Oct 1972	Aug 1975	2024-03-01	6867
DAF	66	1.1 Marathon	Kombi	Heckantrieb	Benzin	40	54	Oct 1972	Aug 1975	2024-03-01	6868
DAF	66	1300 Marathon	Kombi	Heckantrieb	Benzin	42	57	Sep 1973	Aug 1975	2024-03-01	6869
DAF	66	1300 Marathon	Coupe	Heckantrieb	Benzin	42	57	Sep 1973	Aug 1975	2024-03-01	6870
DAF	66	1300 Marathon	Stufenheck	Heckantrieb	Benzin	42	57	Sep 1973	Aug 1975	2024-03-01	6871
NSU	Prinz	600 4L	Stufenheck	Heckantrieb	Benzin	22	30	Aug 1961	Jul 1970	2024-03-01	6872
NSU	Prinz	600	Stufenheck	Heckantrieb	Benzin	22	30	Sep 1969	Nov 1971	2024-03-01	6873
NSU	Prinz	1000	Stufenheck	Heckantrieb	Benzin	29	39	Sep 1969	Mar 1974	2024-03-01	6874
NSU	Prinz	1200	Stufenheck	Heckantrieb	Benzin	48	65	Sep 1969	Mar 1974	2024-03-01	6875
NSU	1000	C	Stufenheck	Heckantrieb	Benzin	29	40	Aug 1963	Dec 1972	2024-03-01	6876
NSU	Tt	1.2	Stufenheck	Heckantrieb	Benzin	48	65	Jul 1965	Nov 1971	2024-03-01	6877
NSU	Tts	1	Stufenheck	Heckantrieb	Benzin	51	70	Feb 1967	Nov 1971	2024-03-01	6878
NSU	1200	C	Stufenheck	Heckantrieb	Benzin	40	54	Sep 1969	Nov 1971	2024-03-01	6879
Audi	60	1.5	Stufenheck	Frontantrieb	Benzin	40	55	Sep 1968	Aug 1972	2024-03-01	6880
Audi	75	1.7	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1968	Aug 1972	2024-03-01	6881
Renault	Clio iii	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	50	68	Oct 2005	Jul 2010	2026-05-01	6882
Audi	75	1.7	Kombi	Frontantrieb	Benzin	55	75	Sep 1968	Aug 1972	2024-03-01	6883
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	59	80	Nov 1968	Nov 1971	2024-03-01	6884
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	66	90	Nov 1968	Nov 1971	2024-03-01	6885
Ford	C-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	103	140	Apr 2010	Jun 2019	2024-03-01	6886
Auto Union	Munga	LKW 0.25t GL	Geländewagen offen	Allrad	Benzin	32	44	Nov 1956	Dec 1959	2024-03-01	6887
Auto Union	Munga	F 91/4	Geländewagen offen	Allrad	Benzin	32	44	Mar 1957	May 1969	2024-03-01	6888
Auto Union	Munga	F 91/6	Geländewagen offen	Allrad	Benzin	32	44	Jul 1958	Nov 1960	2024-03-01	6889
Auto Union	Munga	F 91/8	Geländewagen offen	Allrad	Benzin	32	44	Apr 1962	May 1969	2024-03-01	6890
Auto Union	Munga	F 91/6	Geländewagen offen	Allrad	Benzin	32	44	Apr 1962	Jun 1969	2024-03-01	6891
Auto Union	Dkw f10	0.7	Stufenheck	Frontantrieb	Benzin	15	20	Apr 1950	Jun 1953	2024-03-01	6892
Auto Union	Dkw f11	0.7 Junior	Stufenheck	Frontantrieb	Benzin	25	34	Feb 1959	Aug 1961	2024-03-01	6893
Auto Union	Dkw f12	0.9	Stufenheck	Frontantrieb	Benzin	29	39	Oct 1963	Jun 1965	2024-03-01	6894
Auto Union	Dkw f12	0.9	Cabriolet	Frontantrieb	Benzin	33	45	Nov 1962	Jun 1965	2024-03-01	6895
Auto Union	Dkw f12	0.9	Stufenheck	Frontantrieb	Benzin	33	45	Jan 1965	Aug 1966	2024-03-01	6896
Auto Union	Dkw f102	1.2	Stufenheck	Frontantrieb	Benzin	44	60	Mar 1964	Aug 1966	2024-03-01	6897
Auto Union	Dkw meisterklasse f	0.7	Stufenheck	Frontantrieb	Benzin	17	23	Aug 1950	Feb 1955	2024-03-01	6898
Auto Union	Dkw meisterklasse universal	0.7	Kombi	Frontantrieb	Benzin	17	23	Dec 1951	Jan 1955	2024-03-01	6899
Auto Union	Dkw sonderklasse	0.9 LC	Cabriolet	Frontantrieb	Benzin	25	34	Apr 1953	Feb 1957	2024-03-01	6900
Auto Union	Dkw sonderklasse universal	0.9	Kombi	Frontantrieb	Benzin	25	34	Apr 1953	Feb 1957	2024-03-01	6901
Auto Union	Dkw sonderklasse f	93 LC	Stufenheck	Frontantrieb	Benzin	32	44	Sep 1955	Feb 1960	2024-03-01	6902
Auto Union	Dkw sonderklasse f	94	Stufenheck	Frontantrieb	Benzin	32	44	May 1956	Nov 1959	2024-03-01	6903
Auto Union	Dkw sonderklasse f universal	94	Kombi	Frontantrieb	Benzin	32	44	May 1956	Feb 1960	2024-03-01	6904
Auto Union	Dkw f11	0.8 Junior DE Luxe	Stufenheck	Frontantrieb	Benzin	25	34	Jul 1961	Aug 1966	2024-03-01	6905
Auto Union	Au 1000	1	Stufenheck	Frontantrieb	Benzin	32	44	Apr 1958	Feb 1960	2024-03-01	6906
Auto Union	Au 1000	1	Stufenheck	Frontantrieb	Benzin	32	44	Aug 1959	Jun 1963	2024-03-01	6907
Auto Union	Au 1000	1.0 S	Stufenheck	Frontantrieb	Benzin	37	50	Aug 1959	Mar 1964	2024-03-01	6908
Auto Union	Au 1000	SP.	Coupe	Frontantrieb	Benzin	40	54	Jun 1958	Jun 1965	2024-03-01	6909
Audi	72	1.7	Stufenheck	Heckantrieb	Benzin	53	72	Aug 1965	Aug 1968	2025-12-01	6910
Audi	72	1.7	Kombi	Heckantrieb	Benzin	53	72	Apr 1966	Aug 1968	2025-12-01	6912
Audi	80	1.7	Stufenheck	Frontantrieb	Benzin	59	80	Sep 1966	Aug 1968	2024-03-01	6913
Renault	Clio iii	1.5 DCI	Kasten/Schrägheck	Frontantrieb	Diesel	78	106	Oct 2005	Oct 2007	2026-05-01	6914
Ford	S-Max	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	118	160	Feb 2011	Dec 2014	2024-03-01	6915
Volvo	740	2.3	Kombi	Heckantrieb	Benzin	96	131	Jul 1990	Dec 1992	2024-03-01	6916
Ford	S-Max	2.2 Tdci	Großraumlimousine	Frontantrieb	Diesel	147	200	Jul 2010	Dec 2014	2024-03-01	6918
Volvo	740	2.3 Turbo	Kombi	Heckantrieb	Benzin	134	182	Aug 1985	Jul 1988	2024-03-01	6919
Volvo	740	2.3 Turbo	Kombi	Heckantrieb	Benzin	140	190	Aug 1989	Jul 1990	2024-03-01	6920
Ford	S-Max	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	176	240	Jul 2010	Dec 2014	2024-03-01	6921
Volvo	760	2.8	Kombi	Heckantrieb	Benzin	115	156	Aug 1986	Aug 1990	2024-03-01	6922
Volvo	740	2.3	Kombi	Heckantrieb	Benzin	111	151	Jul 1989	Aug 1992	2024-03-01	6923


--- Round 1 / 首次发送 ---
## 更新点

* 已完成 Jaguar XJ-C、BMW 1600 Cabriolet、BMW 2000 C/CS、BMW 3.0 CSL 与 Jaguar XJ12 Series I 的首次建组；BMW 3.0 CSL 当前记录对应 1973 年中后加宽至 1730 mm 的外廓。([automobile-catalog.com][1])
* 已一次性闭合 DAF 33、44、46、55、66 的 Sedan、Wagon、Coupe 物理分支，共新增 11 个尺寸组。([automobile-catalog.com][2])
* 已闭合 NSU Prinz 4/4L、NSU 1000/TT/TTS 与 NSU 1200 C 三类外廓。([automobile-catalog.com][3])
* Audi F103 Sedan 已按 2 门、4 门拆分，Variant Wagon 按 3 门独立建组；相同三维但门数外形不同，不合并为同一物理尺寸组。([automobile-catalog.com][4])
* Ford C-Max、Grand C-Max、S-Max，BMW E12，以及 Volvo 740/760 均直接引用跨批次现有尺寸组，未重复输出尺寸或来源。

## 当前批次进度

* 输入 Ktype：100
* 已处理并达到 READY 的 Ktype：53
* 本轮 READY 映射行：62
* 本轮首次创建尺寸组：22
* 本轮复用既有尺寸组：9
* 尚待处理 Ktype：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6823	6823	Coupe	Jaguar XJ Series II	2J	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH	Daimler Sovereign 4.2 two-door XJ-C body.	READY
6824	6824	Coupe	Jaguar XJ Series II	2G	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH	Daimler Double Six 5.3 two-door XJ-C body.	READY
6830	6830	Convertible	BMW 02 Series	E10	2	EU-BMW-02-E10-CONVERTIBLE-2D-01	HIGH	Baur-built 1600 Cabriolet body.	READY
6831	6831	Coupe	BMW 2000 C/CS	120	2	EU-BMW-2000-C-CS-COUPE-2D-01	HIGH		READY
6832	6832	Coupe	BMW 2000 C/CS	120	2	EU-BMW-2000-C-CS-COUPE-2D-01	HIGH		READY
6833	6833	Coupe	BMW E9	E9	2	EU-BMW-E9-30-CSL-COUPE-WIDE-01	HIGH	Post-July-1973 widened 3.0 CSL outer body.	READY
6835	6835	Sedan	BMW 5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
6836	6836	Sedan	Jaguar XJ Series I	1P	4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH		READY
6837_prefl	6837	MPV	Ford Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6837_facelift	6837	MPV	Ford Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6838	6838	Sedan	BMW 5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
6839_prefl	6839	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6839_facelift	6839	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6840	6840	Coupe	Jaguar XJ Series II	2G	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH		READY
6850_prefl	6850	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6850_facelift	6850	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6855	6855	Sedan	DAF 33		2	EU-DAF-33-SEDAN-2D-01	HIGH		READY
6856	6856	Sedan	DAF 44		2	EU-DAF-44-SEDAN-2D-01	HIGH		READY
6857	6857	Wagon	DAF 44		3	EU-DAF-44-WAGON-3D-01	HIGH		READY
6858	6858	Sedan	DAF 55		2	EU-DAF-55-SEDAN-2D-01	HIGH		READY
6859	6859	Wagon	DAF 55		3	EU-DAF-55-WAGON-3D-01	HIGH		READY
6860	6860	Sedan	DAF 55		2	EU-DAF-55-SEDAN-2D-01	HIGH		READY
6861	6861	Coupe	DAF 55		2	EU-DAF-55-COUPE-2D-01	HIGH		READY
6862	6862	Coupe	DAF 55		2	EU-DAF-55-COUPE-2D-01	HIGH		READY
6863	6863	Sedan	DAF 46		2	EU-DAF-46-SEDAN-2D-01	HIGH		READY
6864	6864	Wagon	DAF 46		3	EU-DAF-46-WAGON-3D-01	HIGH		READY
6865	6865	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6866	6866	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6867	6867	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6868	6868	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6869	6869	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6870	6870	Coupe	DAF 66		2	EU-DAF-66-COUPE-2D-01	HIGH		READY
6871	6871	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6872	6872	Sedan	NSU Prinz 4/4L		2	EU-NSU-PRINZ-4-4L-SEDAN-2D-01	HIGH		READY
6873	6873	Sedan	NSU Prinz 4/4L		2	EU-NSU-PRINZ-4-4L-SEDAN-2D-01	HIGH		READY
6874	6874	Sedan	NSU 1000		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6875	6875	Sedan	NSU TT		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	MEDIUM	65 PS 1200 variant uses the TT outer body.	READY
6876	6876	Sedan	NSU 1000 C		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6877	6877	Sedan	NSU TT		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6878	6878	Sedan	NSU TTS		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6879	6879	Sedan	NSU 1200 C		2	EU-NSU-1200-C-SEDAN-2D-01	HIGH		READY
6880_2dr	6880	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6880_4dr	6880	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6881_2dr	6881	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6881_4dr	6881	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6883	6883	Wagon	Audi F103	F103	3	EU-AUDI-F103-VARIANT-WAGON-3D-01	HIGH		READY
6886_prefl	6886	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6886_facelift	6886	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6910_2dr	6910	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6910_4dr	6910	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6912	6912	Wagon	Audi F103	F103	3	EU-AUDI-F103-VARIANT-WAGON-3D-01	HIGH		READY
6913_2dr	6913	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6913_4dr	6913	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6915	6915	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6916	6916	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6918	6918	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6919	6919	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6920	6920	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6921	6921	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6922_prefl	6922	Wagon	Volvo 760	765	5	EU-VOLVO-760-WAGON-PREFL-01	HIGH	Pre-facelift outer body.	READY
6922_facelift	6922	Wagon	Volvo 760	765	5	EU-VOLVO-760-WAGON-FACELIFT-01	HIGH	Facelift outer body.	READY
6923	6923	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-JAGUAR-XJ-SERIES-II-COUPE-01	4843	1770	1375	Automobile-Catalog 1976 Jaguar XJ 5.3 C	https://www.automobile-catalog.com/car/1976/1279505/jaguar_xj_5_3_c.html
EU-BMW-02-E10-CONVERTIBLE-2D-01	4230	1590	1360	Automobile-Catalog 1968 BMW 1600 Cabriolet	https://www.automobile-catalog.com/car/1968/77150/bmw_1600_cabriolet.html
EU-BMW-2000-C-CS-COUPE-2D-01	4530	1675	1360	Automobile-Catalog 1969 BMW 2000 CS	https://www.automobile-catalog.com/car/1969/77465/bmw_2000_cs.html
EU-BMW-E9-30-CSL-COUPE-WIDE-01	4660	1730	1370	Automobile-Catalog 1974 BMW 3.0 CSL	https://www.automobile-catalog.com/car/1974/78290/bmw_3_0_csl.html
EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	4814	1768	1343	Automobile-Catalog 1972 Jaguar XJ12	https://www.automobile-catalog.com/car/1972/1278770/jaguar_xj12.html
EU-DAF-33-SEDAN-2D-01	3620	1440	1420	Automobile-Catalog 1969 DAF 33	https://www.automobile-catalog.com/car/1969/1455050/daf_33.html
EU-DAF-44-SEDAN-2D-01	3850	1540	1380	Automobile-Catalog 1974 DAF 44	https://www.automobile-catalog.com/car/1974/2058680/daf_44.html
EU-DAF-44-WAGON-3D-01	3850	1540	1380	Automobile-Catalog 1968 DAF 44 Kombi	https://www.automobile-catalog.com/car/1968/128210/daf_44_kombi.html
EU-DAF-55-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1970 DAF 55	https://www.automobile-catalog.com/car/1970/2058710/daf_55.html
EU-DAF-55-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1971 DAF 55 Kombi	https://www.automobile-catalog.com/car/1971/2058740/daf_55_kombi.html
EU-DAF-55-COUPE-2D-01	3880	1540	1310	Automobile-Catalog 1970 DAF 55 Coupe	https://www.automobile-catalog.com/car/1970/2058725/daf_55_coupe.html
EU-DAF-46-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1975 DAF 46	https://www.automobile-catalog.com/car/1975/38210/daf_46.html
EU-DAF-46-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1976 DAF 46 Kombi	https://www.automobile-catalog.com/car/1976/128225/daf_46_kombi.html
EU-DAF-66-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1972 DAF 66 L	https://www.automobile-catalog.com/car/1972/128315/daf_66.html
EU-DAF-66-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1972 DAF 66 L Kombi	https://www.automobile-catalog.com/car/1972/128375/daf_66_kombi.html
EU-DAF-66-COUPE-2D-01	3880	1540	1310	Automobile-Catalog 1974 DAF 66 SL Coupe	https://www.automobile-catalog.com/car/1974/128345/daf_66_coupe.html
EU-NSU-PRINZ-4-4L-SEDAN-2D-01	3440	1490	1360	Automobile-Catalog 1969 NSU Prinz 4L	https://www.automobile-catalog.com/car/1969/2057660/nsu_prinz_4l.html
EU-NSU-1000-TT-TTS-SEDAN-2D-01	3793	1490	1364	Automobile-Catalog 1966 NSU Prinz 1000 L; Automobile-Catalog 1967 NSU TT; Automobile-Catalog 1970 NSU TTS	https://www.automobile-catalog.com/car/1966/2057735/nsu_prinz_1000_l.html;https://www.automobile-catalog.com/car/1967/2058020/nsu_tt.html;https://www.automobile-catalog.com/car/1970/2058140/nsu_tts.html
EU-NSU-1200-C-SEDAN-2D-01	4000	1500	1390	Automobile-Catalog 1971 NSU 1200 C	https://www.automobile-catalog.com/car/1971/2058095/nsu_1200_c.html
EU-AUDI-F103-SEDAN-2D-01	4380	1626	1451	Automobile-Catalog 1967 Audi 72 F103 Sedan	https://www.automobile-catalog.com/car/1967/74360/audi_72.html
EU-AUDI-F103-SEDAN-4D-01	4380	1626	1451	Automobile-Catalog 1967 Audi 72 F103 Sedan	https://www.automobile-catalog.com/car/1967/74360/audi_72.html
EU-AUDI-F103-VARIANT-WAGON-3D-01	4380	1626	1456	Automobile-Catalog 1969 Audi 75 Variant	https://www.automobile-catalog.com/car/1969/74480/audi_75_variant.html
```

## 下一步优先处理

1. 处理 Daimler X300/DS420/Landaulette，并解决 DS420 长度和宽度变更的准确分界。
2. 按 Series I、II、III，以及 FHC、2+2、Roadster 分解 Jaguar E-Type。
3. 处理 Renault Clio III Kasten、Auto Union Munga，以及 DKW/Auto Union 历史车型组。
4. 最后解决跨代时间段较长的 Jaguar XJ6 与 Audi 100 C1 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1976/1279505/jaguar_xj_5_3_c.html?utm_source=chatgpt.com "1976 Jaguar XJ 5.3 C (aut. 3) (model for Europe ) car ..."
[2]: https://www.automobile-catalog.com/car/1969/1455050/daf_33.html?utm_source=chatgpt.com "1969 Daf 33 Specs Review (20.5 kW / 28 PS / 27 hp) (since late-year 1969 for Europe )"
[3]: https://www.automobile-catalog.com/car/1969/2057660/nsu_prinz_4l.html?utm_source=chatgpt.com "1969 NSU Prinz 4L Specs Review (22 kW / 30 PS / 30 hp) (up to mid-year 1969 for Europe )"
[4]: https://www.automobile-catalog.com/car/1967/74360/audi_72.html?utm_source=chatgpt.com "1967 Audi (72) (L) Specs Review (53 kW / 72 PS / 71 hp) (since mid-year 1967 for Europe )"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6401-6500_ktype_dimension_mapping_final.tsv
- all_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 Daimler Double Six X305 的 SWB/LWB，以及 DS420 Limousine/Landaulette 的早期、后期外廓分支。X305 两种轴距分别为 5024×1799×1314 mm、5149×1799×1333 mm；DS420 在后期车身更新后由 5740×1968×1619 mm 变为 5510×1995×1630 mm。([automobile-catalog.com][1])
* 闭合 Jaguar XJ6 Series I、Series II SWB/LWB 分支；Series I 复用本批已创建尺寸组，Series II LWB 复用跨批次既有尺寸组，仅新建 Series II SWB。([automobile-catalog.com][2])
* 一次性闭合 Jaguar E-Type Series I、II、III 的 FHC、2+2 和 OTS 外廓，共新增八个尺寸组。([automobile-catalog.com][3])
* Audi 100 C1 80/90 PS 车型按 2 门、4 门拆分；4 门复用既有组，2 门新建独立尺寸组。([automobile-catalog.com][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：75
* READY 映射行：92
* PENDING Ktype：25
* 本轮新增/修改 Ktype：22
* 本轮新增/修改映射行：30
* 本轮首次创建尺寸组：16
* 剩余待处理范围：Renault Clio III Kasten 与 Auto Union/DKW/Munga，共25个 Ktype
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6822_swb	6822	Sedan	Daimler X300	X305	4	EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-SWB-01	MEDIUM	SWB物理外廓。	READY
6822_lwb	6822	Sedan	Daimler X300	X305	4	EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-LWB-01	MEDIUM	LWB物理外廓。	READY
6825_early	6825	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-EARLY-01	HIGH	早期Limousine外廓。	READY
6825_late	6825	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-LATE-01	HIGH	后期Limousine外廓。	READY
6826	6826	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-LATE-01	HIGH		READY
6827_early	6827	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-EARLY-01	MEDIUM	早期Landaulette外廓。	READY
6827_late	6827	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-LATE-01	MEDIUM	后期Landaulette外廓。	READY
6828	6828	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-LATE-01	MEDIUM		READY
6829_series1	6829	Sedan	Jaguar XJ Series I		4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH	Series I物理外廓。	READY
6829_series2_swb	6829	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Series II短轴距外廓。	READY
6834_series1	6834	Sedan	Jaguar XJ Series I		4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH	Series I物理外廓。	READY
6834_series2_swb	6834	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Series II短轴距外廓。	READY
6834_series2_lwb	6834	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	HIGH	Series II长轴距外廓。	READY
6841	6841	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-FHC-COUPE-01	HIGH		READY
6842	6842	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	六缸2+2物理外廓；输入结束年月超出实际生产边界。	READY
6843	6843	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	MEDIUM	Series I短轴距FHC外廓。	READY
6844	6844	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-2PLUS2-COUPE-01	HIGH	Series I长轴距2+2外廓。	READY
6845	6845	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	六缸2+2物理外廓；输入结束年月超出实际生产边界。	READY
6846	6846	Coupe	E-Type Series III		3	EU-JAGUAR-E-TYPE-S3-2PLUS2-COUPE-01	HIGH	V12 Series III 2+2外廓。	READY
6847	6847	Convertible	E-Type Series II		2	EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	HIGH		READY
6848	6848	Convertible	E-Type Series II		2	EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	MEDIUM	六缸OTS外廓；输入结束年月超出实际生产边界。	READY
6849	6849	Convertible	E-Type Series III		2	EU-JAGUAR-E-TYPE-S3-OTS-CONVERTIBLE-01	HIGH	V12 Series III OTS外廓。	READY
6851	6851	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	HIGH		READY
6852	6852	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	低功率六缸2+2外廓。	READY
6853	6853	Convertible	E-Type Series I		2	EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	HIGH		READY
6854	6854	Convertible	E-Type Series I		2	EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	HIGH		READY
6884_2dr	6884	Sedan	Audi 100 C1	F104	2	EU-AUDI-100-C1-SEDAN-PREFL-03	HIGH	两门Sedan物理分支。	READY
6884_4dr	6884	Sedan	Audi 100 C1	F104	4	EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	四门Sedan物理分支。	READY
6885_2dr	6885	Sedan	Audi 100 C1	F104	2	EU-AUDI-100-C1-SEDAN-PREFL-03	HIGH	两门Sedan物理分支。	READY
6885_4dr	6885	Sedan	Audi 100 C1	F104	4	EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	四门Sedan物理分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-SWB-01	5024	1799	1314	Automobile-Catalog 1996 Daimler Double Six	https://www.automobile-catalog.com/car/1996/1285760/daimler_double_six.html
EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-LWB-01	5149	1799	1333	Automobile-Catalog 1996 Daimler Double Six LWB	https://www.automobile-catalog.com/car/1996/1285775/daimler_double_six_lwb.html
EU-DAIMLER-DS420-LIMOUSINE-EARLY-01	5740	1968	1619	Automobile-Catalog 1972 Daimler Limousine DS-420	https://www.automobile-catalog.com/car/1972/32045/daimler_limousine_ds-420.html
EU-DAIMLER-DS420-LIMOUSINE-LATE-01	5510	1995	1630	Automobile-Catalog 1988 Daimler Limousine DS-420	https://www.automobile-catalog.com/car/1988/2062235/daimler_limousine_ds-420.html
EU-DAIMLER-DS420-LANDAULETTE-EARLY-01	5740	1968	1619	Automobile-Catalog 1972 Daimler Limousine DS-420; Kucarfa Daimler DS420 Landaulette	https://www.automobile-catalog.com/car/1972/32045/daimler_limousine_ds-420.html;https://www.kucarfa.nl/Daimler/Daimler.html
EU-DAIMLER-DS420-LANDAULETTE-LATE-01	5510	1995	1630	Automobile-Catalog 1988 Daimler Limousine DS-420; Kucarfa Daimler DS420 Landaulette	https://www.automobile-catalog.com/car/1988/2062235/daimler_limousine_ds-420.html;https://www.kucarfa.nl/Daimler/Daimler.html
EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	4843	1770	1375	Automobile-Catalog 1974 Jaguar XJ6 2.8	https://www.automobile-catalog.com/car/1974/1279370/jaguar_xj6_2_8.html
EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	4455	1657	1222	Automobile-Catalog 1962 Jaguar E-Type GT Fixed Head Coupe	https://www.automobile-catalog.com/car/1962/1276850/jaguar_e-type_g_t__fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	4455	1657	1222	Automobile-Catalog 1962 Jaguar E-Type GT Open Two-Seater	https://www.automobile-catalog.com/car/1962/1276910/jaguar_e-type_g_t__open_two-seater.html
EU-JAGUAR-E-TYPE-S1-2PLUS2-COUPE-01	4686	1657	1270	Automobile-Catalog 1967 Jaguar E-Type 4.2 Litre 2+2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1967/1277600/jaguar_e-type_4_2_litre_22_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S2-FHC-COUPE-01	4453	1657	1219	Automobile-Catalog 1970 Jaguar E-Type Series 2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1970/1278290/jaguar_e-type_series_2_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	4453	1657	1219	Automobile-Catalog 1970 Jaguar E-Type Series 2 Open Two-Seater	https://www.automobile-catalog.com/car/1970/1278335/jaguar_e-type_series_2_open_two-seater.html
EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	4686	1657	1270	Automobile-Catalog 1970 Jaguar E-Type Series 2 2+2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1970/1278380/jaguar_e-type_series_2_22_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S3-2PLUS2-COUPE-01	4684	1678	1306	Automobile-Catalog 1972 Jaguar E-Type Series 3 V12 2+2 Coupe	https://www.automobile-catalog.com/car/1972/1278875/jaguar_e-type_series_3_v12_22_coupe.html
EU-JAGUAR-E-TYPE-S3-OTS-CONVERTIBLE-01	4684	1678	1226	Automobile-Catalog 1972 Jaguar E-Type Series 3 V12 Open Two-Seater	https://www.automobile-catalog.com/car/1972/1278935/jaguar_e-type_series_3_v12_open_2-seater.html
EU-AUDI-100-C1-SEDAN-PREFL-03	4590	1729	1421	Automobile-Catalog 1969 Audi 100 S 90; Gazoo Audi 100 C1 1.8 two-door dimensions	https://www.automobile-catalog.com/car/1969/74525/audi_100_s_90.html;https://gazoo.pl/samochody/audi/audi-100/wymiary/
```

## 下一步优先处理

1. 先闭合 Renault Clio III Kasten 两个 Ktype，判断是否复用同代三门商用车外廓。
2. 按 F91/4、F91/6、F91/8 聚类处理 Auto Union Munga。
3. 批量闭合 DKW F10/F11/F12/F102、Meisterklasse、Sonderklasse 与 AU 1000。
4. 完成后立即进行一次机械引用闭合检查；若 PENDING=0，下一轮直接输出两张完整 TSV、两个指定下载链接和 COMPLETE。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1996/1285760/daimler_double_six.html?utm_source=chatgpt.com "1996 Daimler Double Six Specs Review (235 kW / 320 PS / 315 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1974/1279370/jaguar_xj6_2_8.html?utm_source=chatgpt.com "1974 Jaguar XJ6 2.8 Specs Review (100.5 kW / 137 PS / 135 hp) (up to mid-year 1974 for Europe France)"
[3]: https://www.automobile-catalog.com/car/1962/1276850/jaguar_e-type_g_t__fixed_head_coupe.html?utm_source=chatgpt.com "1962 Jaguar E-Type G.T. Fixed Head Coupe Specs Review (198 kW / 269 PS / 265 hp) (for Europe )"
[4]: https://www.automobile-catalog.com/car/1969/74510/audi_100_80.html?utm_source=chatgpt.com "1969 Audi 100 (80) Specs Review (59 kW / 80 PS / 79 hp) (for Europe )"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6401-6500_ktype_dimension_mapping_final.tsv
- all_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已闭合 Renault Clio III 三门商用厢式外廓，Ktype 6882、6914 共用同一尺寸组。
* 已按 `F91/4`、`F91/6`、`F91/8` 三种物理车体闭合 Auto Union Munga。
* 已闭合 DKW Junior、F11/F12、F102、F89、F91、F93、F94，以及 Auto Union 1000/1000 S/1000 SP 的已确认分支。
* Ktype 6892 对应的 DKW F10 Baur 车身仍缺少可追溯且明确为不含后视镜口径的完整三维，暂不创建尺寸组。
* 本轮新增 29 行 READY 映射、1 行 PENDING 映射及 21 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：99
* PENDING Ktype：1
* READY 映射行：121
* PENDING 映射行：1
* 已确认尺寸组：70
* 本轮首次创建尺寸组：21
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6882	6882	Van	Renault Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	MEDIUM	三门商用厢式外廓。	READY
6887	6887	SUV	Auto Union Munga	F91/4	2	EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	HIGH	四座开放式车体。	READY
6888	6888	SUV	Auto Union Munga	F91/4	2	EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	HIGH	四座开放式车体。	READY
6889	6889	SUV	Auto Union Munga	F91/6	2	EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	HIGH	六座短货台车体。	READY
6890	6890	SUV	Auto Union Munga	F91/8	2	EU-AUTO-UNION-MUNGA-F91-8-OPEN-SUV-01	HIGH	八座加长车体。	READY
6891	6891	SUV	Auto Union Munga	F91/6	2	EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	HIGH	六座短货台车体。	READY
6892	6892	Sedan	DKW F10	F10	2		LOW	F10 Baur车身三维尚缺可追溯的不含镜来源。	PENDING: F10车身三维来源未闭合
6893	6893	Sedan	DKW Junior	F11	2	EU-DKW-JUNIOR-F11-SEDAN-2D-01	HIGH		READY
6894	6894	Sedan	DKW F12	F12	2	EU-DKW-F12-SEDAN-2D-01	HIGH		READY
6895	6895	Convertible	DKW F12	F12	2	EU-DKW-F12-ROADSTER-CONVERTIBLE-2D-01	HIGH		READY
6896	6896	Sedan	DKW F12	F12	2	EU-DKW-F12-SEDAN-2D-01	HIGH		READY
6897	6897	Sedan	DKW F102	F102	2	EU-DKW-F102-SEDAN-2D-01	HIGH		READY
6898	6898	Sedan	DKW F89 Meisterklasse	F89	2	EU-DKW-F89-MEISTERKLASSE-SEDAN-2D-01	HIGH		READY
6899	6899	Wagon	DKW F89 Meisterklasse	F89 U	3	EU-DKW-F89-MEISTERKLASSE-UNIVERSAL-WAGON-3D-01	HIGH		READY
6900_f91	6900	Convertible	DKW F91 Sonderklasse	F91	2	EU-DKW-F91-SONDERKLASSE-CONVERTIBLE-2D-01	MEDIUM	F91早期Cabriolet分支。	READY
6900_f93	6900	Convertible	DKW F93 3=6	F93	2	EU-DKW-F93-3-6-CONVERTIBLE-2D-01	MEDIUM	F93后期Cabriolet分支。	READY
6901	6901	Wagon	DKW F91 Sonderklasse	F91 U	3	EU-DKW-F91-U-SONDERKLASSE-WAGON-3D-01	HIGH		READY
6902_2dr	6902	Sedan	DKW F93 3=6	F93	2	EU-DKW-F93-3-6-SEDAN-2D-01	MEDIUM	F93两门物理分支。	READY
6902_4dr	6902	Sedan	DKW F94 3=6	F94	4	EU-DKW-F94-3-6-SEDAN-4D-01	MEDIUM	F94四门物理分支。	READY
6903	6903	Sedan	DKW F94 3=6	F94	4	EU-DKW-F94-3-6-SEDAN-4D-01	HIGH		READY
6904	6904	Wagon	DKW F94 3=6	F94 U	3	EU-DKW-F94-U-3-6-WAGON-3D-01	HIGH		READY
6905	6905	Sedan	DKW Junior de Luxe	F11	2	EU-DKW-JUNIOR-DE-LUXE-F11-SEDAN-2D-01	MEDIUM	输入结束年月晚于该车型实际边界。	READY
6906_2dr	6906	Sedan	Auto Union 1000		2	EU-AUTO-UNION-1000-SEDAN-2D-01	MEDIUM	两门Sedan物理分支。	READY
6906_4dr	6906	Sedan	Auto Union 1000		4	EU-AUTO-UNION-1000-SEDAN-4D-01	MEDIUM	四门Sedan物理分支。	READY
6907	6907	Sedan	Auto Union 1000		2	EU-AUTO-UNION-1000-SEDAN-2D-01	HIGH		READY
6908_2dr	6908	Sedan	Auto Union 1000 S		2	EU-AUTO-UNION-1000-SEDAN-2D-01	MEDIUM	两门物理分支。	READY
6908_4dr	6908	Sedan	Auto Union 1000 S		4	EU-AUTO-UNION-1000-SEDAN-4D-01	MEDIUM	四门物理分支。	READY
6909_prefl	6909	Coupe	Auto Union 1000 SP		2	EU-AUTO-UNION-1000-SP-COUPE-PREFL-01	HIGH	早期车身外廓。	READY
6909_facelift	6909	Coupe	Auto Union 1000 SP		2	EU-AUTO-UNION-1000-SP-COUPE-FACELIFT-01	HIGH	后期车身外廓。	READY
6914	6914	Van	Renault Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	MEDIUM	三门商用厢式外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-RENAULT-CLIO-III-X85-VAN-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I dimensions	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-generation-11029
EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	3445	1810	1735	Automobile-Catalog 1960 DKW Munga F91/4	https://www.automobile-catalog.com/car/1960/588050/dkw_munga_f_91_4.html
EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	3445	1830	1937	Auto Union Munga operating manual technical data	https://de.wikipedia.org/wiki/DKW_Munga
EU-AUTO-UNION-MUNGA-F91-8-OPEN-SUV-01	3690	1830	1937	Auto Union Munga operating manual technical data	https://de.wikipedia.org/wiki/DKW_Munga
EU-DKW-JUNIOR-F11-SEDAN-2D-01	3965	1575	1430	Automobile-Catalog 1959 DKW Junior	https://www.automobile-catalog.com/car/1959/588095/dkw_junior.html
EU-DKW-F12-SEDAN-2D-01	3968	1575	1453	Automobile-Catalog 1963 DKW F12	https://www.automobile-catalog.com/car/1963/588155/dkw_f_12.html
EU-DKW-F12-ROADSTER-CONVERTIBLE-2D-01	3968	1575	1375	Automobile-Catalog 1964 DKW F12 Roadster	https://www.automobile-catalog.com/car/1964/588170/dkw_f_12_roadster.html
EU-DKW-F102-SEDAN-2D-01	4280	1618	1459	Automobile-Catalog 1964 DKW F102	https://www.automobile-catalog.com/car/1964/588185/dkw_f_102.html
EU-DKW-F89-MEISTERKLASSE-SEDAN-2D-01	4200	1600	1450	Automobile-Catalog 1950 DKW F89 Meisterklasse	https://www.automobile-catalog.com/car/1950/587570/dkw_f_89_meisterklasse.html
EU-DKW-F89-MEISTERKLASSE-UNIVERSAL-WAGON-3D-01	4055	1520	1555	DKW F89 factory technical data	https://de.wikipedia.org/wiki/DKW_F_89
EU-DKW-F91-SONDERKLASSE-CONVERTIBLE-2D-01	4220	1600	1450	Automobile-Catalog 1954 DKW F91 Cabriolet de Luxe	https://www.automobile-catalog.com/car/1954/587735/dkw_f_91_sonderklasse_cabriolet_de_luxe_karmann.html
EU-DKW-F93-3-6-CONVERTIBLE-2D-01	4225	1695	1465	Automobile-Catalog 1955 DKW F93 3=6 Cabriolet de Luxe	https://www.automobile-catalog.com/car/1955/587900/dkw_f_93_3-6_cabriolet_de_luxe_karmann.html
EU-DKW-F91-U-SONDERKLASSE-WAGON-3D-01	4100	1520	1570	Automobile-Catalog 1954 DKW F91 U Sonderklasse Universal	https://www.automobile-catalog.com/car/1954/587780/dkw_f_91_u_sonderklasse_universal.html
EU-DKW-F93-3-6-SEDAN-2D-01	4225	1695	1465	Automobile-Catalog 1956 DKW F93 3=6	https://www.automobile-catalog.com/car/1956/587930/dkw_f_93_3-6.html
EU-DKW-F94-3-6-SEDAN-4D-01	4325	1695	1490	Automobile-Catalog 1957 DKW F94 3=6 four-door	https://www.automobile-catalog.com/car/1957/587975/dkw_f_94_3-6_4-door.html
EU-DKW-F94-U-3-6-WAGON-3D-01	4170	1645	1495	Automobile-Catalog 1957 DKW F94 U 3=6 Universal	https://www.automobile-catalog.com/car/1957/588020/dkw_f_94_u_3-6_universal.html
EU-DKW-JUNIOR-DE-LUXE-F11-SEDAN-2D-01	3980	1575	1440	Automobile-Catalog 1961 DKW Junior de Luxe	https://www.automobile-catalog.com/car/1961/588110/dkw_junior_de_luxe.html
EU-AUTO-UNION-1000-SEDAN-2D-01	4225	1695	1465	Automobile-Catalog 1959 Auto Union 1000 two-door	https://www.automobile-catalog.com/car/1959/259310/auto_union_1000_limousine_2-turig.html
EU-AUTO-UNION-1000-SEDAN-4D-01	4325	1695	1488	Automobile-Catalog 1959 Auto Union 1000 S four-door	https://www.automobile-catalog.com/car/1959/259325/auto_union_1000_s_limousine_4-turig.html
EU-AUTO-UNION-1000-SP-COUPE-PREFL-01	4170	1680	1335	Automobile-Catalog 1959 Auto Union 1000 SP	https://www.automobile-catalog.com/car/1959/259370/auto_union_1000_sp.html
EU-AUTO-UNION-1000-SP-COUPE-FACELIFT-01	4195	1680	1325	Automobile-Catalog 1961 Auto Union 1000 SP	https://www.automobile-catalog.com/car/1961/259385/auto_union_1000_sp.html
```

## 下一步优先处理

1. 仅处理 Ktype 6892 的 DKW F10 Baur 双门车身。
2. 优先寻找能同时明确 `LengthMM`、不含后视镜 `WidthMM`、`HeightMM` 的历史技术资料或可信规格页。
3. 该尺寸组闭合后，立即进行一次机械检查并输出两张最终完整 TSV、两个指定 sandbox 下载链接和 `推进信号：COMPLETE`。

推进信号：CONTINUE


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_6401-6500_ktype_dimension_mapping_final.tsv
- all_6401-6500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合最后一个 PENDING：Ktype `6892` 确认为 DKW F10 Baur 双门 Limousine，尺寸组为 `4110 × 1500 × 1450 mm`。([de.wikipedia.org][1])([维基百科][1]) 已完成固定表头、唯一键、映射引用、尺寸与来源非空检查。
* 当前批次全部完成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：122
* PENDING 映射行：0
* DIMENSION_GROUP：71
* `id`：全部唯一
* `DIMENSION_GROUP_ID`：全部唯一且引用闭合

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6822_swb	6822	Sedan	Daimler X300	X305	4	EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-SWB-01	MEDIUM	SWB物理外廓。	READY
6822_lwb	6822	Sedan	Daimler X300	X305	4	EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-LWB-01	MEDIUM	LWB物理外廓。	READY
6823	6823	Coupe	Jaguar XJ Series II	2J	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH	Daimler Sovereign 4.2 two-door XJ-C body.	READY
6824	6824	Coupe	Jaguar XJ Series II	2G	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH	Daimler Double Six 5.3 two-door XJ-C body.	READY
6825_early	6825	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-EARLY-01	HIGH	早期Limousine外廓。	READY
6825_late	6825	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-LATE-01	HIGH	后期Limousine外廓。	READY
6826	6826	Sedan	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LIMOUSINE-LATE-01	HIGH		READY
6827_early	6827	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-EARLY-01	MEDIUM	早期Landaulette外廓。	READY
6827_late	6827	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-LATE-01	MEDIUM	后期Landaulette外廓。	READY
6828	6828	Convertible	Daimler DS420	DS420	4	EU-DAIMLER-DS420-LANDAULETTE-LATE-01	MEDIUM		READY
6829_series1	6829	Sedan	Jaguar XJ Series I		4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH	Series I物理外廓。	READY
6829_series2_swb	6829	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Series II短轴距外廓。	READY
6830	6830	Convertible	BMW 02 Series	E10	2	EU-BMW-02-E10-CONVERTIBLE-2D-01	HIGH	Baur-built 1600 Cabriolet body.	READY
6831	6831	Coupe	BMW 2000 C/CS	120	2	EU-BMW-2000-C-CS-COUPE-2D-01	HIGH		READY
6832	6832	Coupe	BMW 2000 C/CS	120	2	EU-BMW-2000-C-CS-COUPE-2D-01	HIGH		READY
6833	6833	Coupe	BMW E9	E9	2	EU-BMW-E9-30-CSL-COUPE-WIDE-01	HIGH	Post-July-1973 widened 3.0 CSL outer body.	READY
6834_series1	6834	Sedan	Jaguar XJ Series I		4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH	Series I物理外廓。	READY
6834_series2_swb	6834	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	HIGH	Series II短轴距外廓。	READY
6834_series2_lwb	6834	Sedan	Jaguar XJ Series II		4	EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	HIGH	Series II长轴距外廓。	READY
6835	6835	Sedan	BMW 5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
6836	6836	Sedan	Jaguar XJ Series I	1P	4	EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	HIGH		READY
6837_prefl	6837	MPV	Ford Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6837_facelift	6837	MPV	Ford Grand C-Max II	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6838	6838	Sedan	BMW 5 Series E12	E12	4	EU-BMW-5-E12-SEDAN-01	HIGH		READY
6839_prefl	6839	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6839_facelift	6839	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6840	6840	Coupe	Jaguar XJ Series II	2G	2	EU-JAGUAR-XJ-SERIES-II-COUPE-01	HIGH		READY
6841	6841	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-FHC-COUPE-01	HIGH		READY
6842	6842	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	六缸2+2物理外廓；输入结束年月超出实际生产边界。	READY
6843	6843	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	MEDIUM	Series I短轴距FHC外廓。	READY
6844	6844	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-2PLUS2-COUPE-01	HIGH	Series I长轴距2+2外廓。	READY
6845	6845	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	六缸2+2物理外廓；输入结束年月超出实际生产边界。	READY
6846	6846	Coupe	E-Type Series III		3	EU-JAGUAR-E-TYPE-S3-2PLUS2-COUPE-01	HIGH	V12 Series III 2+2外廓。	READY
6847	6847	Convertible	E-Type Series II		2	EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	HIGH		READY
6848	6848	Convertible	E-Type Series II		2	EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	MEDIUM	六缸OTS外廓；输入结束年月超出实际生产边界。	READY
6849	6849	Convertible	E-Type Series III		2	EU-JAGUAR-E-TYPE-S3-OTS-CONVERTIBLE-01	HIGH	V12 Series III OTS外廓。	READY
6850_prefl	6850	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6850_facelift	6850	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6851	6851	Coupe	E-Type Series I		3	EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	HIGH		READY
6852	6852	Coupe	E-Type Series II		3	EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	MEDIUM	低功率六缸2+2外廓。	READY
6853	6853	Convertible	E-Type Series I		2	EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	HIGH		READY
6854	6854	Convertible	E-Type Series I		2	EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	HIGH		READY
6855	6855	Sedan	DAF 33		2	EU-DAF-33-SEDAN-2D-01	HIGH		READY
6856	6856	Sedan	DAF 44		2	EU-DAF-44-SEDAN-2D-01	HIGH		READY
6857	6857	Wagon	DAF 44		3	EU-DAF-44-WAGON-3D-01	HIGH		READY
6858	6858	Sedan	DAF 55		2	EU-DAF-55-SEDAN-2D-01	HIGH		READY
6859	6859	Wagon	DAF 55		3	EU-DAF-55-WAGON-3D-01	HIGH		READY
6860	6860	Sedan	DAF 55		2	EU-DAF-55-SEDAN-2D-01	HIGH		READY
6861	6861	Coupe	DAF 55		2	EU-DAF-55-COUPE-2D-01	HIGH		READY
6862	6862	Coupe	DAF 55		2	EU-DAF-55-COUPE-2D-01	HIGH		READY
6863	6863	Sedan	DAF 46		2	EU-DAF-46-SEDAN-2D-01	HIGH		READY
6864	6864	Wagon	DAF 46		3	EU-DAF-46-WAGON-3D-01	HIGH		READY
6865	6865	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6866	6866	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6867	6867	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6868	6868	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6869	6869	Wagon	DAF 66		3	EU-DAF-66-WAGON-3D-01	HIGH		READY
6870	6870	Coupe	DAF 66		2	EU-DAF-66-COUPE-2D-01	HIGH		READY
6871	6871	Sedan	DAF 66		2	EU-DAF-66-SEDAN-2D-01	HIGH		READY
6872	6872	Sedan	NSU Prinz 4/4L		2	EU-NSU-PRINZ-4-4L-SEDAN-2D-01	HIGH		READY
6873	6873	Sedan	NSU Prinz 4/4L		2	EU-NSU-PRINZ-4-4L-SEDAN-2D-01	HIGH		READY
6874	6874	Sedan	NSU 1000		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6875	6875	Sedan	NSU TT		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	MEDIUM	65 PS 1200 variant uses the TT outer body.	READY
6876	6876	Sedan	NSU 1000 C		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6877	6877	Sedan	NSU TT		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6878	6878	Sedan	NSU TTS		2	EU-NSU-1000-TT-TTS-SEDAN-2D-01	HIGH		READY
6879	6879	Sedan	NSU 1200 C		2	EU-NSU-1200-C-SEDAN-2D-01	HIGH		READY
6880_2dr	6880	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6880_4dr	6880	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6881_2dr	6881	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6881_4dr	6881	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6882	6882	Van	Renault Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	MEDIUM	三门商用厢式外廓。	READY
6883	6883	Wagon	Audi F103	F103	3	EU-AUDI-F103-VARIANT-WAGON-3D-01	HIGH		READY
6884_2dr	6884	Sedan	Audi 100 C1	F104	2	EU-AUDI-100-C1-SEDAN-PREFL-03	HIGH	两门Sedan物理分支。	READY
6884_4dr	6884	Sedan	Audi 100 C1	F104	4	EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	四门Sedan物理分支。	READY
6885_2dr	6885	Sedan	Audi 100 C1	F104	2	EU-AUDI-100-C1-SEDAN-PREFL-03	HIGH	两门Sedan物理分支。	READY
6885_4dr	6885	Sedan	Audi 100 C1	F104	4	EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	四门Sedan物理分支。	READY
6886_prefl	6886	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	HIGH	Pre-facelift outer body.	READY
6886_facelift	6886	MPV	Ford C-Max II	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	HIGH	Facelift outer body.	READY
6887	6887	SUV	Auto Union Munga	F91/4	2	EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	HIGH	四座开放式车体。	READY
6888	6888	SUV	Auto Union Munga	F91/4	2	EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	HIGH	四座开放式车体。	READY
6889	6889	SUV	Auto Union Munga	F91/6	2	EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	HIGH	六座短货台车体。	READY
6890	6890	SUV	Auto Union Munga	F91/8	2	EU-AUTO-UNION-MUNGA-F91-8-OPEN-SUV-01	HIGH	八座加长车体。	READY
6891	6891	SUV	Auto Union Munga	F91/6	2	EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	HIGH	六座短货台车体。	READY
6892	6892	Sedan	DKW F10	F10	2	EU-DKW-F10-SEDAN-2D-01	MEDIUM	Baur双门Limousine车身。	READY
6893	6893	Sedan	DKW Junior	F11	2	EU-DKW-JUNIOR-F11-SEDAN-2D-01	HIGH		READY
6894	6894	Sedan	DKW F12	F12	2	EU-DKW-F12-SEDAN-2D-01	HIGH		READY
6895	6895	Convertible	DKW F12	F12	2	EU-DKW-F12-ROADSTER-CONVERTIBLE-2D-01	HIGH		READY
6896	6896	Sedan	DKW F12	F12	2	EU-DKW-F12-SEDAN-2D-01	HIGH		READY
6897	6897	Sedan	DKW F102	F102	2	EU-DKW-F102-SEDAN-2D-01	HIGH		READY
6898	6898	Sedan	DKW F89 Meisterklasse	F89	2	EU-DKW-F89-MEISTERKLASSE-SEDAN-2D-01	HIGH		READY
6899	6899	Wagon	DKW F89 Meisterklasse	F89 U	3	EU-DKW-F89-MEISTERKLASSE-UNIVERSAL-WAGON-3D-01	HIGH		READY
6900_f91	6900	Convertible	DKW F91 Sonderklasse	F91	2	EU-DKW-F91-SONDERKLASSE-CONVERTIBLE-2D-01	MEDIUM	F91早期Cabriolet分支。	READY
6900_f93	6900	Convertible	DKW F93 3=6	F93	2	EU-DKW-F93-3-6-CONVERTIBLE-2D-01	MEDIUM	F93后期Cabriolet分支。	READY
6901	6901	Wagon	DKW F91 Sonderklasse	F91 U	3	EU-DKW-F91-U-SONDERKLASSE-WAGON-3D-01	HIGH		READY
6902_2dr	6902	Sedan	DKW F93 3=6	F93	2	EU-DKW-F93-3-6-SEDAN-2D-01	MEDIUM	F93两门物理分支。	READY
6902_4dr	6902	Sedan	DKW F94 3=6	F94	4	EU-DKW-F94-3-6-SEDAN-4D-01	MEDIUM	F94四门物理分支。	READY
6903	6903	Sedan	DKW F94 3=6	F94	4	EU-DKW-F94-3-6-SEDAN-4D-01	HIGH		READY
6904	6904	Wagon	DKW F94 3=6	F94 U	3	EU-DKW-F94-U-3-6-WAGON-3D-01	HIGH		READY
6905	6905	Sedan	DKW Junior de Luxe	F11	2	EU-DKW-JUNIOR-DE-LUXE-F11-SEDAN-2D-01	MEDIUM	输入结束年月晚于该车型实际边界。	READY
6906_2dr	6906	Sedan	Auto Union 1000		2	EU-AUTO-UNION-1000-SEDAN-2D-01	MEDIUM	两门Sedan物理分支。	READY
6906_4dr	6906	Sedan	Auto Union 1000		4	EU-AUTO-UNION-1000-SEDAN-4D-01	MEDIUM	四门Sedan物理分支。	READY
6907	6907	Sedan	Auto Union 1000		2	EU-AUTO-UNION-1000-SEDAN-2D-01	HIGH		READY
6908_2dr	6908	Sedan	Auto Union 1000 S		2	EU-AUTO-UNION-1000-SEDAN-2D-01	MEDIUM	两门物理分支。	READY
6908_4dr	6908	Sedan	Auto Union 1000 S		4	EU-AUTO-UNION-1000-SEDAN-4D-01	MEDIUM	四门物理分支。	READY
6909_prefl	6909	Coupe	Auto Union 1000 SP		2	EU-AUTO-UNION-1000-SP-COUPE-PREFL-01	HIGH	早期车身外廓。	READY
6909_facelift	6909	Coupe	Auto Union 1000 SP		2	EU-AUTO-UNION-1000-SP-COUPE-FACELIFT-01	HIGH	后期车身外廓。	READY
6910_2dr	6910	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6910_4dr	6910	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6912	6912	Wagon	Audi F103	F103	3	EU-AUDI-F103-VARIANT-WAGON-3D-01	HIGH		READY
6913_2dr	6913	Sedan	Audi F103	F103	2	EU-AUDI-F103-SEDAN-2D-01	HIGH	Two-door F103 sedan branch.	READY
6913_4dr	6913	Sedan	Audi F103	F103	4	EU-AUDI-F103-SEDAN-4D-01	HIGH	Four-door F103 sedan branch.	READY
6914	6914	Van	Renault Clio III	X85	3	EU-RENAULT-CLIO-III-X85-VAN-3D-01	MEDIUM	三门商用厢式外廓。	READY
6915	6915	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6916	6916	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6918	6918	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6919	6919	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6920	6920	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
6921	6921	MPV	Ford S-Max I	WA6	5	EU-FORD-S-MAX-I-WA6-MPV-01	HIGH		READY
6922_prefl	6922	Wagon	Volvo 760	765	5	EU-VOLVO-760-WAGON-PREFL-01	HIGH	Pre-facelift outer body.	READY
6922_facelift	6922	Wagon	Volvo 760	765	5	EU-VOLVO-760-WAGON-FACELIFT-01	HIGH	Facelift outer body.	READY
6923	6923	Wagon	Volvo 740	745	5	EU-VOLVO-740-WAGON-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_6401-6500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-SWB-01	5024	1799	1314	Automobile-Catalog 1996 Daimler Double Six	https://www.automobile-catalog.com/car/1996/1285760/daimler_double_six.html
EU-DAIMLER-X300-X305-DOUBLE-SIX-SEDAN-LWB-01	5149	1799	1333	Automobile-Catalog 1996 Daimler Double Six LWB	https://www.automobile-catalog.com/car/1996/1285775/daimler_double_six_lwb.html
EU-JAGUAR-XJ-SERIES-II-COUPE-01	4843	1770	1375	Automobile-Catalog 1976 Jaguar XJ 5.3 C	https://www.automobile-catalog.com/car/1976/1279505/jaguar_xj_5_3_c.html
EU-DAIMLER-DS420-LIMOUSINE-EARLY-01	5740	1968	1619	Automobile-Catalog 1972 Daimler Limousine DS-420	https://www.automobile-catalog.com/car/1972/32045/daimler_limousine_ds-420.html
EU-DAIMLER-DS420-LIMOUSINE-LATE-01	5510	1995	1630	Automobile-Catalog 1988 Daimler Limousine DS-420	https://www.automobile-catalog.com/car/1988/2062235/daimler_limousine_ds-420.html
EU-DAIMLER-DS420-LANDAULETTE-EARLY-01	5740	1968	1619	Automobile-Catalog 1972 Daimler Limousine DS-420; Kucarfa Daimler DS420 Landaulette	https://www.automobile-catalog.com/car/1972/32045/daimler_limousine_ds-420.html;https://www.kucarfa.nl/Daimler/Daimler.html
EU-DAIMLER-DS420-LANDAULETTE-LATE-01	5510	1995	1630	Automobile-Catalog 1988 Daimler Limousine DS-420; Kucarfa Daimler DS420 Landaulette	https://www.automobile-catalog.com/car/1988/2062235/daimler_limousine_ds-420.html;https://www.kucarfa.nl/Daimler/Daimler.html
EU-JAGUAR-XJ-SERIES-I-XJ12-SEDAN-01	4814	1768	1343	Automobile-Catalog 1972 Jaguar XJ12	https://www.automobile-catalog.com/car/1972/1278770/jaguar_xj12.html
EU-JAGUAR-XJ-SERIES-II-SEDAN-SWB-01	4843	1770	1375	Automobile-Catalog 1974 Jaguar XJ6 2.8	https://www.automobile-catalog.com/car/1974/1279370/jaguar_xj6_2_8.html
EU-BMW-02-E10-CONVERTIBLE-2D-01	4230	1590	1360	Automobile-Catalog 1968 BMW 1600 Cabriolet	https://www.automobile-catalog.com/car/1968/77150/bmw_1600_cabriolet.html
EU-BMW-2000-C-CS-COUPE-2D-01	4530	1675	1360	Automobile-Catalog 1969 BMW 2000 CS	https://www.automobile-catalog.com/car/1969/77465/bmw_2000_cs.html
EU-BMW-E9-30-CSL-COUPE-WIDE-01	4660	1730	1370	Automobile-Catalog 1974 BMW 3.0 CSL	https://www.automobile-catalog.com/car/1974/78290/bmw_3_0_csl.html
EU-JAGUAR-XJ-SERIES-II-LWB-SEDAN-01	4945	1770	1375	Automobile-Catalog 1974 Jaguar XJ6L	https://www.automobile-catalog.com/car/1974/1279325/jaguar_xj6l.html
EU-BMW-5-E12-SEDAN-01	4620	1690	1425	Automobile-Catalog 1974 BMW 520i	https://www.automobile-catalog.com/car/1974/35195/bmw_520i.html
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Ford C-MAX and Grand C-MAX 2011 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642	Ford C-MAX and Grand C-MAX official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf
EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	Ford C-MAX and Grand C-MAX 2011 official brochure	https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf
EU-FORD-C-MAX-II-MPV-FACELIFT-02	4379	1828	1610	Ford C-MAX and Grand C-MAX official brochure	https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf
EU-JAGUAR-E-TYPE-S2-FHC-COUPE-01	4453	1657	1219	Automobile-Catalog 1970 Jaguar E-Type Series 2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1970/1278290/jaguar_e-type_series_2_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S2-2PLUS2-COUPE-01	4686	1657	1270	Automobile-Catalog 1970 Jaguar E-Type Series 2 2+2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1970/1278380/jaguar_e-type_series_2_22_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S1-FHC-COUPE-01	4455	1657	1222	Automobile-Catalog 1962 Jaguar E-Type GT Fixed Head Coupe	https://www.automobile-catalog.com/car/1962/1276850/jaguar_e-type_g_t__fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S1-2PLUS2-COUPE-01	4686	1657	1270	Automobile-Catalog 1967 Jaguar E-Type 4.2 Litre 2+2 Fixed Head Coupe	https://www.automobile-catalog.com/car/1967/1277600/jaguar_e-type_4_2_litre_22_fixed_head_coupe.html
EU-JAGUAR-E-TYPE-S3-2PLUS2-COUPE-01	4684	1678	1306	Automobile-Catalog 1972 Jaguar E-Type Series 3 V12 2+2 Coupe	https://www.automobile-catalog.com/car/1972/1278875/jaguar_e-type_series_3_v12_22_coupe.html
EU-JAGUAR-E-TYPE-S2-OTS-CONVERTIBLE-01	4453	1657	1219	Automobile-Catalog 1970 Jaguar E-Type Series 2 Open Two-Seater	https://www.automobile-catalog.com/car/1970/1278335/jaguar_e-type_series_2_open_two-seater.html
EU-JAGUAR-E-TYPE-S3-OTS-CONVERTIBLE-01	4684	1678	1226	Automobile-Catalog 1972 Jaguar E-Type Series 3 V12 Open Two-Seater	https://www.automobile-catalog.com/car/1972/1278935/jaguar_e-type_series_3_v12_open_2-seater.html
EU-JAGUAR-E-TYPE-S1-OTS-CONVERTIBLE-01	4455	1657	1222	Automobile-Catalog 1962 Jaguar E-Type GT Open Two-Seater	https://www.automobile-catalog.com/car/1962/1276910/jaguar_e-type_g_t__open_two-seater.html
EU-DAF-33-SEDAN-2D-01	3620	1440	1420	Automobile-Catalog 1969 DAF 33	https://www.automobile-catalog.com/car/1969/1455050/daf_33.html
EU-DAF-44-SEDAN-2D-01	3850	1540	1380	Automobile-Catalog 1974 DAF 44	https://www.automobile-catalog.com/car/1974/2058680/daf_44.html
EU-DAF-44-WAGON-3D-01	3850	1540	1380	Automobile-Catalog 1968 DAF 44 Kombi	https://www.automobile-catalog.com/car/1968/128210/daf_44_kombi.html
EU-DAF-55-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1970 DAF 55	https://www.automobile-catalog.com/car/1970/2058710/daf_55.html
EU-DAF-55-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1971 DAF 55 Kombi	https://www.automobile-catalog.com/car/1971/2058740/daf_55_kombi.html
EU-DAF-55-COUPE-2D-01	3880	1540	1310	Automobile-Catalog 1970 DAF 55 Coupe	https://www.automobile-catalog.com/car/1970/2058725/daf_55_coupe.html
EU-DAF-46-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1975 DAF 46	https://www.automobile-catalog.com/car/1975/38210/daf_46.html
EU-DAF-46-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1976 DAF 46 Kombi	https://www.automobile-catalog.com/car/1976/128225/daf_46_kombi.html
EU-DAF-66-SEDAN-2D-01	3880	1540	1380	Automobile-Catalog 1972 DAF 66 L	https://www.automobile-catalog.com/car/1972/128315/daf_66.html
EU-DAF-66-WAGON-3D-01	3880	1540	1380	Automobile-Catalog 1972 DAF 66 L Kombi	https://www.automobile-catalog.com/car/1972/128375/daf_66_kombi.html
EU-DAF-66-COUPE-2D-01	3880	1540	1310	Automobile-Catalog 1974 DAF 66 SL Coupe	https://www.automobile-catalog.com/car/1974/128345/daf_66_coupe.html
EU-NSU-PRINZ-4-4L-SEDAN-2D-01	3440	1490	1360	Automobile-Catalog 1969 NSU Prinz 4L	https://www.automobile-catalog.com/car/1969/2057660/nsu_prinz_4l.html
EU-NSU-1000-TT-TTS-SEDAN-2D-01	3793	1490	1364	Automobile-Catalog 1966 NSU Prinz 1000 L; Automobile-Catalog 1967 NSU TT; Automobile-Catalog 1970 NSU TTS	https://www.automobile-catalog.com/car/1966/2057735/nsu_prinz_1000_l.html;https://www.automobile-catalog.com/car/1967/2058020/nsu_tt.html;https://www.automobile-catalog.com/car/1970/2058140/nsu_tts.html
EU-NSU-1200-C-SEDAN-2D-01	4000	1500	1390	Automobile-Catalog 1971 NSU 1200 C	https://www.automobile-catalog.com/car/1971/2058095/nsu_1200_c.html
EU-AUDI-F103-SEDAN-2D-01	4380	1626	1451	Automobile-Catalog 1967 Audi 72 F103 Sedan	https://www.automobile-catalog.com/car/1967/74360/audi_72.html
EU-AUDI-F103-SEDAN-4D-01	4380	1626	1451	Automobile-Catalog 1967 Audi 72 F103 Sedan	https://www.automobile-catalog.com/car/1967/74360/audi_72.html
EU-RENAULT-CLIO-III-X85-VAN-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I dimensions	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-generation-11029
EU-AUDI-F103-VARIANT-WAGON-3D-01	4380	1626	1456	Automobile-Catalog 1969 Audi 75 Variant	https://www.automobile-catalog.com/car/1969/74480/audi_75_variant.html
EU-AUDI-100-C1-SEDAN-PREFL-03	4590	1729	1421	Automobile-Catalog 1969 Audi 100 S 90; Gazoo Audi 100 C1 1.8 two-door dimensions	https://www.automobile-catalog.com/car/1969/74525/audi_100_s_90.html;https://gazoo.pl/samochody/audi/audi-100/wymiary/
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421	Automobile-Catalog 1969 Audi 100 80	https://www.automobile-catalog.com/car/1969/74510/audi_100_80.html
EU-AUTO-UNION-MUNGA-F91-4-OPEN-SUV-01	3445	1810	1735	Automobile-Catalog 1960 DKW Munga F91/4	https://www.automobile-catalog.com/car/1960/588050/dkw_munga_f_91_4.html
EU-AUTO-UNION-MUNGA-F91-6-OPEN-SUV-01	3445	1830	1937	Auto Union Munga operating manual technical data	https://de.wikipedia.org/wiki/DKW_Munga
EU-AUTO-UNION-MUNGA-F91-8-OPEN-SUV-01	3690	1830	1937	Auto Union Munga operating manual technical data	https://de.wikipedia.org/wiki/DKW_Munga
EU-DKW-F10-SEDAN-2D-01	4110	1500	1450	DKW F10 technical specification summary	https://de.wikipedia.org/wiki/DKW_F_10
EU-DKW-JUNIOR-F11-SEDAN-2D-01	3965	1575	1430	Automobile-Catalog 1959 DKW Junior	https://www.automobile-catalog.com/car/1959/588095/dkw_junior.html
EU-DKW-F12-SEDAN-2D-01	3968	1575	1453	Automobile-Catalog 1963 DKW F12	https://www.automobile-catalog.com/car/1963/588155/dkw_f_12.html
EU-DKW-F12-ROADSTER-CONVERTIBLE-2D-01	3968	1575	1375	Automobile-Catalog 1964 DKW F12 Roadster	https://www.automobile-catalog.com/car/1964/588170/dkw_f_12_roadster.html
EU-DKW-F102-SEDAN-2D-01	4280	1618	1459	Automobile-Catalog 1964 DKW F102	https://www.automobile-catalog.com/car/1964/588185/dkw_f_102.html
EU-DKW-F89-MEISTERKLASSE-SEDAN-2D-01	4200	1600	1450	Automobile-Catalog 1950 DKW F89 Meisterklasse	https://www.automobile-catalog.com/car/1950/587570/dkw_f_89_meisterklasse.html
EU-DKW-F89-MEISTERKLASSE-UNIVERSAL-WAGON-3D-01	4055	1520	1555	DKW F89 factory technical data	https://de.wikipedia.org/wiki/DKW_F_89
EU-DKW-F91-SONDERKLASSE-CONVERTIBLE-2D-01	4220	1600	1450	Automobile-Catalog 1954 DKW F91 Cabriolet de Luxe	https://www.automobile-catalog.com/car/1954/587735/dkw_f_91_sonderklasse_cabriolet_de_luxe_karmann.html
EU-DKW-F93-3-6-CONVERTIBLE-2D-01	4225	1695	1465	Automobile-Catalog 1955 DKW F93 3=6 Cabriolet de Luxe	https://www.automobile-catalog.com/car/1955/587900/dkw_f_93_3-6_cabriolet_de_luxe_karmann.html
EU-DKW-F91-U-SONDERKLASSE-WAGON-3D-01	4100	1520	1570	Automobile-Catalog 1954 DKW F91 U Sonderklasse Universal	https://www.automobile-catalog.com/car/1954/587780/dkw_f_91_u_sonderklasse_universal.html
EU-DKW-F93-3-6-SEDAN-2D-01	4225	1695	1465	Automobile-Catalog 1956 DKW F93 3=6	https://www.automobile-catalog.com/car/1956/587930/dkw_f_93_3-6.html
EU-DKW-F94-3-6-SEDAN-4D-01	4325	1695	1490	Automobile-Catalog 1957 DKW F94 3=6 four-door	https://www.automobile-catalog.com/car/1957/587975/dkw_f_94_3-6_4-door.html
EU-DKW-F94-U-3-6-WAGON-3D-01	4170	1645	1495	Automobile-Catalog 1957 DKW F94 U 3=6 Universal	https://www.automobile-catalog.com/car/1957/588020/dkw_f_94_u_3-6_universal.html
EU-DKW-JUNIOR-DE-LUXE-F11-SEDAN-2D-01	3980	1575	1440	Automobile-Catalog 1961 DKW Junior de Luxe	https://www.automobile-catalog.com/car/1961/588110/dkw_junior_de_luxe.html
EU-AUTO-UNION-1000-SEDAN-2D-01	4225	1695	1465	Automobile-Catalog 1959 Auto Union 1000 two-door	https://www.automobile-catalog.com/car/1959/259310/auto_union_1000_limousine_2-turig.html
EU-AUTO-UNION-1000-SEDAN-4D-01	4325	1695	1488	Automobile-Catalog 1959 Auto Union 1000 S four-door	https://www.automobile-catalog.com/car/1959/259325/auto_union_1000_s_limousine_4-turig.html
EU-AUTO-UNION-1000-SP-COUPE-PREFL-01	4170	1680	1335	Automobile-Catalog 1959 Auto Union 1000 SP	https://www.automobile-catalog.com/car/1959/259370/auto_union_1000_sp.html
EU-AUTO-UNION-1000-SP-COUPE-FACELIFT-01	4195	1680	1325	Automobile-Catalog 1961 Auto Union 1000 SP	https://www.automobile-catalog.com/car/1961/259385/auto_union_1000_sp.html
EU-FORD-S-MAX-I-WA6-MPV-01	4768	1884	1658	Ford S-MAX 2012 official brochure	https://autocatalogarchive.com/wp-content/uploads/2023/09/Ford-S-Max-2012-UK.pdf
EU-VOLVO-740-WAGON-5D-01	4785	1761	1435	Automobile-Catalog 1988 Volvo 740 Kombi GL	https://www.automobile-catalog.com/car/1988/52940/volvo_740_kombi_gl.html
EU-VOLVO-760-WAGON-PREFL-01	4800	1750	1435	AutoCentrum Volvo 760 Kombi 2.8 1986-1988	https://www.autocentrum.pl/dane-techniczne/volvo/760/kombi/silnik-benzynowy-2.8-156km-1986-1988/
EU-VOLVO-760-WAGON-FACELIFT-01	4790	1760	1435	Volvo 760 model dimensions summary	https://en.wikipedia.org/wiki/Volvo_760?oldformat=true
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_6401-6500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://de.wikipedia.org/wiki/DKW_F_10?utm_source=chatgpt.com "DKW F 10"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_6401-6500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_6401-6500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（8169 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（2528 行）

