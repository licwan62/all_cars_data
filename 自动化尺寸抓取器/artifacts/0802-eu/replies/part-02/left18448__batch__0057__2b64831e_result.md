# 任务：left18448 第 5601-5700 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0057__2b64831e


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 5601-5700 行

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
left18448 第 5601-5700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5601-5700_ktype_dimension_mapping_final.tsv
- left18448_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-FORD-FOCUS-III-HATCHBACK-FACELIFT-01	4360	1823	1469
EU-FORD-FOCUS-III-HATCHBACK-PREFL-01	4358	1823	1484
EU-FORD-FOCUS-III-HATCHBACK-ST-FACELIFT-01	4362	1823	1471
EU-FORD-FOCUS-III-HATCHBACK-ST-PREFL-01	4362	1823	1484
EU-FORD-FOCUS-III-SEDAN-FACELIFT-01	4534	1823	1484
EU-FORD-FOCUS-III-SEDAN-PREFL-01	4534	1823	1484
EU-FORD-FOCUS-III-WAGON-FACELIFT-01	4560	1823	1492
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Ford	Focus iii	2.3 RS AWD	Schrägheck	Allrad	Benzin	Jul 2015	Feb 2018	117983
Ford	Focus iii	Electric	Schrägheck	Frontantrieb	Elektro	Jul 2013	Dec 2017	100022
Ford	Focus iii turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	Sep 2014	Feb 2020	107886
Ford	Focus iii turnier	1.5 Ecoboost	Kombi	Frontantrieb	Benzin	Sep 2014	Feb 2020	107888
Ford	Focus iii turnier	1.5 Tdci	Kombi	Frontantrieb	Diesel	Sep 2014	Feb 2020	107889
Ford	Focus iii turnier	1.5 Tdci	Kombi	Frontantrieb	Diesel	Sep 2014	Feb 2020	107892
Ford	Focus iii turnier	1.5 Tdci Econetic	Kombi	Frontantrieb	Diesel	Sep 2014	Feb 2020	107891
Ford	Focus iii turnier	1.6 Ecoboost	Kombi	Frontantrieb	Benzin	Jul 2010	Jun 2014	8151
Ford	Focus iii turnier	1.6 Ecoboost	Kombi	Frontantrieb	Benzin	Jul 2010	Jun 2014	8165
Ford	Focus iii turnier	1.6 Flexifuel	Kombi	Frontantrieb	Benzin/Ethanol	Jul 2010	Feb 2020	8150
Ford	Focus iii turnier	1.6 Flexifuel	Kombi	Frontantrieb	Benzin/Ethanol	Jul 2013	Feb 2020	39963
Ford	Focus iii turnier	1.6 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Feb 2012	Feb 2020	106487
Ford	Focus iii turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	Jul 2010	Feb 2020	8170
Ford	Focus iii turnier	1.6 Tdci	Kombi	Frontantrieb	Diesel	Jul 2010	Feb 2020	8175
Ford	Focus iii turnier	1.6 Tdci Econetic	Kombi	Frontantrieb	Diesel	May 2012	Jul 2015	55511
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	Jul 2010	Feb 2020	8096
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	Jul 2010	Feb 2020	8111
Ford	Focus iii turnier	1.6 TI	Kombi	Frontantrieb	Benzin	Feb 2012	Feb 2020	109855
Ford	Focus iii turnier	2.0 ST	Kombi	Frontantrieb	Benzin	Jul 2012	Feb 2020	55485
Ford	Focus iii turnier	2.0 Tdci	Kombi	Frontantrieb	Diesel	Nov 2014	Feb 2020	108576
Ford	Focus iii turnier	2.0 Tdci ST	Kombi	Frontantrieb	Diesel	Nov 2014	Feb 2020	108577
Ford	Focus iii turnier	2.0 Ti-gdi	Kombi	Frontantrieb	Benzin	Jul 2010	Feb 2020	51968
Ford	Focus iv	1.0 Ecoboost Mhev Active	Schrägheck	Frontantrieb	Benzin/Elektro	Jan 2021	Nov 2025	143421
Ford	Focus iv	1.0 Ecoboost Mhev Flex	Schrägheck	Frontantrieb	Benzin/Ethanol/Elektro	Jan 2022	Nov 2025	153469
Ford	Focus iv	1.5 Ecoblue	Schrägheck	Frontantrieb	Diesel	Aug 2022	Nov 2025	151776
Ford	Focus iv	1.5 Ecoblue	Stufenheck	Frontantrieb	Diesel	May 2024	Nov 2025	158634
Ford	Focus iv turnier	1.0 Ecoboost Mhev Flex	Kombi	Frontantrieb	Benzin/Ethanol/Elektro	Dec 2022	Nov 2025	153471
Ford	Focus iv turnier	1.5 Ecoblue	Kombi	Frontantrieb	Diesel	Aug 2022	Nov 2025	151777
Ford	Fusion	1.25	Kombi	Frontantrieb	Benzin	Aug 2004	Dec 2012	18692
Ford	Fusion	1.4	Kombi	Frontantrieb	Benzin	Aug 2002	Dec 2012	16624
Ford	Fusion	1.6	Kombi	Frontantrieb	Benzin	Aug 2002	Nov 2009	16625
Ford	Fusion	1.4 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Jan 2010	Dec 2012	56585
Ford	Fusion	1.4 Tdci	Kombi	Frontantrieb	Diesel	Aug 2002	Dec 2012	16626
Ford	Fusion	1.6 Tdci	Kombi	Frontantrieb	Diesel	Nov 2004	Dec 2012	18330
Ford	Galaxy i	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Aug 1997	Apr 2000	8835
Ford	Galaxy i	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Apr 2000	May 2006	14797
Ford	Galaxy i	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	Feb 2003	May 2006	17611
Ford	Galaxy i	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	May 2005	May 2006	18755
Ford	Galaxy i	2.3 16V	Großraumlimousine	Frontantrieb	Benzin	Jan 1997	May 2006	7812
Ford	Galaxy i	2.3 16V	Großraumlimousine	Frontantrieb	Benzin	Sep 2001	May 2006	17307
Ford	Galaxy i	2.8 V6	Großraumlimousine	Frontantrieb	Benzin	Apr 2000	May 2006	14796
Ford	Galaxy ii	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2010	Jun 2015	59494
Ford	Galaxy iii	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Jun 2018	112237
Ford	Galaxy iii	2.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jan 2015	Apr 2023	112239
Ford	Galaxy iii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	112242
Ford	Galaxy iii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	112243
Ford	Galaxy iii	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	112245
Ford	Galaxy iii	2.0 Tdci 4X4	Großraumlimousine	Allrad	Diesel	May 2015	Jun 2018	115107
Ford	Galaxy iii	2.0 Tdci 4X4	Großraumlimousine	Allrad	Diesel	May 2015	Jun 2018	115110
Ford	Galaxy iii	2.0 Tdci Bi-turbo	Großraumlimousine	Frontantrieb	Diesel	Jan 2015	Jun 2018	112247
Ford	Galaxy iii	2.5 Fhev	Großraumlimousine	Frontantrieb	Benzin/Elektro	Jul 2021	Apr 2023	145520
Ford	Galaxy mk i van	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 1996	Mar 2006	142751
Ford	Galaxy mk i van	2.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 2002	Mar 2006	142755
Ford	Galaxy mk i van	2.3	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2000	Oct 2002	142756
Ford	Galaxy mk i van	2.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	Nov 1995	Jul 2000	142760
Ford	Galaxy mk i van	2.8	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2000	Mar 2006	142761
Ford	Galaxy mk i van	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	Sep 1996	Mar 2006	142762
Ford	Galaxy mk i van	1.9 TDI	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2000	Mar 2006	142763
Ford	Galaxy mk ii van	2	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2006	Jun 2015	142738
Ford	Galaxy mk ii van	Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Jun 2015	142744
Ford	Galaxy mk ii van	Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Nov 2006	Jun 2015	142746
Ford	Galaxy mk ii van	Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	May 2006	Jun 2015	142748
Ford	Galaxy mk ii van	Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2013	Jun 2015	142750
Ford	Granada	1.6	Stufenheck	Heckantrieb	Benzin	Jul 1981	Aug 1985	11165
Ford	Granada	1.7	Stufenheck	Heckantrieb	Benzin	Dec 1974	Aug 1977	11560
Ford	Granada	1.7	Kombi	Heckantrieb	Benzin	Dec 1974	Aug 1977	11561
Ford	Granada	1.7	Stufenheck	Heckantrieb	Benzin	Mar 1972	Feb 1975	14968
Ford	Granada	1.7	Kombi	Heckantrieb	Benzin	Mar 1972	Feb 1975	14969
Ford	Granada	1.7	Coupe	Heckantrieb	Benzin	Mar 1972	Feb 1975	14970
Ford	Granada	1.7	Stufenheck	Heckantrieb	Benzin	Aug 1977	May 1982	14971
Ford	Granada	2	Coupe	Heckantrieb	Benzin	Mar 1972	Feb 1975	15275
Ford	Granada	2	Stufenheck	Heckantrieb	Benzin	Jan 1975	Dec 1975	17041
Ford	Granada	2.3	Stufenheck	Heckantrieb	Benzin	Jan 1972	Feb 1976	6602
Ford	Granada	2.3	Coupe	Heckantrieb	Benzin	Jan 1972	Feb 1976	6605
Ford	Granada	2.3	Kombi	Heckantrieb	Benzin	Jan 1972	Feb 1976	6608
Ford	Granada	2.6	Stufenheck	Heckantrieb	Benzin	Jan 1972	Feb 1976	6603
Ford	Granada	2.6	Coupe	Heckantrieb	Benzin	Jan 1972	Feb 1976	6606
Ford	Granada	2.6	Kombi	Heckantrieb	Benzin	Jan 1972	Feb 1976	15277
Ford	Granada	3	Stufenheck	Heckantrieb	Benzin	Jan 1972	Feb 1976	6604
Ford	Granada	3	Coupe	Heckantrieb	Benzin	Jan 1972	Feb 1976	6607
Ford	Granada	3	Kombi	Heckantrieb	Benzin	Jan 1972	Feb 1976	6609
Ford	Granada	1.9 D	Stufenheck	Heckantrieb	Diesel	Aug 1977	Aug 1982	15278
Ford	Grand c-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	56758
Ford	Grand c-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	56761
Ford	Grand c-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2018	Jun 2019	145823
Ford	Grand c-Max	1.0 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Jul 2018	Jun 2019	145825
Ford	Grand c-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	111780
Ford	Grand c-Max	1.5 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	111781
Ford	Grand c-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111782
Ford	Grand c-Max	1.5 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111783
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Feb 2011	Jun 2019	10247
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111784
Ford	Grand c-Max	2.0 Tdci	Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	111785
Ford	Grand c-Max van	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2018	108777
Ford	Grand c-Max van	1.0 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Oct 2012	Jun 2019	108778
Ford	Grand c-Max van	1.5 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Mar 2015	Jun 2019	113257
Ford	Grand c-Max van	1.5 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Mar 2015	Jun 2019	113297
Ford	Grand c-Max van	1.6 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Jun 2019	108779
Ford	Grand c-Max van	1.6 Ecoboost	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Jun 2019	142765
Ford	Grand c-Max van	1.6 Tdci	Kasten/Großraumlimousine	Frontantrieb	Diesel	Dec 2010	Jun 2019	108780


--- Round 1 / 首次发送 ---
## 更新点

* 完成前 28 个输入 Ktype 的映射，共形成 40 条 `READY` 映射。
* Focus III 普通旅行版直接复用历史缓存的改款前、改款后尺寸组；跨越改款日期的 Ktype 已拆为 `prefl` 和 `facelift`。
* Focus III RS、Electric、ST Wagon 均存在不同于普通车型的外廓，已独立建组。([汽车数据][1])
* Focus IV Active 改款前后高度分别为 1483 mm 和 1502 mm，Ktype `143421` 跨越改款周期，因此拆成两个物理分支。([汽车数据][2])
* Focus IV 2022 年后 Hatchback、Sedan、Wagon 已按 Ford 官方规格分别建组。

## 当前批次进度

* 已覆盖输入 Ktype：28 / 100
* READY 映射：40
* PENDING 映射：0（已处理部分）
* 未处理输入 Ktype：72
* 已确认尺寸组：11

  * 复用历史尺寸组：2
  * 本轮首次创建尺寸组：9
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117983	117983	Hatchback	Focus III		5	EU-FORD-FOCUS-III-HATCHBACK-RS-FACELIFT-01	HIGH	RS专属外廓。	READY
100022	100022	Hatchback	Focus III		5	EU-FORD-FOCUS-III-HATCHBACK-ELECTRIC-01	HIGH	Electric专属外廓。	READY
107886	107886	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107888	107888	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107889	107889	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107892	107892	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107891	107891	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
8151	8151	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8165	8165	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8150_prefl	8150	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8150_facelift	8150	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
39963_prefl	39963	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
39963_facelift	39963	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
106487_prefl	106487	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
106487_facelift	106487	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8170_prefl	8170	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8170_facelift	8170	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8175_prefl	8175	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8175_facelift	8175	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55511_prefl	55511	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55511_facelift	55511	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8096_prefl	8096	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8096_facelift	8096	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8111_prefl	8111	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8111_facelift	8111	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
109855_prefl	109855	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
109855_facelift	109855	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55485_prefl	55485	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-PREFL-01	HIGH	Ktype跨改款，ST外廓拆分。	READY
55485_facelift	55485	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	HIGH	Ktype跨改款，ST外廓拆分。	READY
108576	108576	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
108577	108577	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	HIGH	ST专属外廓。	READY
51968_prefl	51968	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
51968_facelift	51968	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
143421_prefl	143421	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-PREFL-01	MEDIUM	Ktype跨改款，Active车身高度变化。	READY
143421_facelift	143421	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-FACELIFT-01	MEDIUM	Ktype跨改款，Active车身高度变化。	READY
153469	153469	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	HIGH		READY
151776	151776	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	HIGH		READY
158634	158634	Sedan	Focus IV		4	EU-FORD-FOCUS-IV-SEDAN-FACELIFT-01	HIGH		READY
153471	153471	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	HIGH		READY
151777	151777	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-HATCHBACK-RS-FACELIFT-01	4390	1823	1472	Auto-Data Ford Focus III Hatchback RS 2.3 EcoBoost AWD	https://www.auto-data.net/en/ford-focus-iii-hatchback-facelift-2014-rs-2.3-ecoboost-350hp-awd-24929
EU-FORD-FOCUS-III-HATCHBACK-ELECTRIC-01	4392	1824	1478	Auto-Data Ford Focus III Hatchback Electric 23 kWh	https://www.auto-data.net/en/ford-focus-iii-hatchback-facelift-2014-23-kwh-145hp-electric-45103
EU-FORD-FOCUS-III-WAGON-ST-PREFL-01	4566	1823	1505	Auto-Data Ford Focus III Wagon ST 2.0 EcoBoost	https://www.auto-data.net/en/ford-focus-iii-wagon-st-2.0-ecoboost-250hp-20086
EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	4563	1823	1486	Auto-Data Ford Focus III Wagon ST 2.0 EcoBoost;Auto-Data Ford Focus III Wagon ST 2.0 TDCi	https://www.auto-data.net/en/ford-focus-iii-wagon-facelift-2014-st-2.0-ecoboost-250hp-s-s-20092;https://www.auto-data.net/en/ford-focus-iii-wagon-facelift-2014-st-2.0-tdci-185hp-20090
EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-PREFL-01	4397	1844	1483	Auto-Data Ford Focus IV Active Hatchback 1.5 EcoBlue	https://www.auto-data.net/en/ford-focus-iv-active-hatchback-1.5-ecoblue-120hp-36132
EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-FACELIFT-01	4397	1844	1502	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	4382	1825	1471	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-SEDAN-FACELIFT-01	4651	1825	1471	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	4672	1825	1494	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
```

## 下一步优先处理

优先按共享外廓批量处理剩余车型：

1. Ford Fusion 全系。
2. Galaxy I、II、III 及对应 Van 分支。
3. Granada Sedan、Wagon、Coupe 的代际边界。
4. Grand C-Max 与 Grand C-Max Van 的改款前后尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-focus-iii-hatchback-facelift-2014-rs-2.3-ecoboost-350hp-awd-24929 "Ford Focus III Hatchback (facelift 2014) RS 2.3 EcoBoost (350 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/ford-focus-iv-active-hatchback-1.5-ecoblue-120hp-36132 "Ford Focus IV Active Hatchback 1.5 EcoBlue (120 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_5601-5700_ktype_dimension_mapping_final.tsv
- left18448_5601-5700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 完成 Fusion、Galaxy I–III、Granada I–II、Grand C-Max 及对应 Van 的物理外廓聚类和映射。
* 跨改款或跨 Coupe 车身修订的 Ktype 已拆分；发动机、燃料和驱动差异未重复建组。
* WidthMM 均采用不含外后视镜口径。Fusion、Galaxy、Granada 与 Grand C-Max 的改款前后尺寸差异已闭合。([汽车目录][1])

## 当前批次进度

* 输入 Ktype：100 / 100
* READY 映射：151
* PENDING 映射：0
* DIMENSION_GROUP：29
* `id` 唯一：通过
* `DIMENSION_GROUP_ID` 唯一：通过
* 映射引用闭合：通过
* 孤立尺寸组：0
* 两张 TSV 固定表头及字段完整性：通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
117983	117983	Hatchback	Focus III		5	EU-FORD-FOCUS-III-HATCHBACK-RS-FACELIFT-01	HIGH	RS专属外廓。	READY
100022	100022	Hatchback	Focus III		5	EU-FORD-FOCUS-III-HATCHBACK-ELECTRIC-01	HIGH	Electric专属外廓。	READY
107886	107886	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107888	107888	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107889	107889	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107892	107892	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
107891	107891	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
8151	8151	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8165	8165	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH		READY
8150_prefl	8150	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8150_facelift	8150	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
39963_prefl	39963	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
39963_facelift	39963	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
106487_prefl	106487	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
106487_facelift	106487	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8170_prefl	8170	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8170_facelift	8170	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8175_prefl	8175	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8175_facelift	8175	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55511_prefl	55511	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55511_facelift	55511	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8096_prefl	8096	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8096_facelift	8096	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8111_prefl	8111	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8111_facelift	8111	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
109855_prefl	109855	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
109855_facelift	109855	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
55485_prefl	55485	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-PREFL-01	HIGH	Ktype跨改款，ST外廓拆分。	READY
55485_facelift	55485	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	HIGH	Ktype跨改款，ST外廓拆分。	READY
108576	108576	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH		READY
108577	108577	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	HIGH	ST专属外廓。	READY
51968_prefl	51968	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
51968_facelift	51968	Wagon	Focus III		5	EU-FORD-FOCUS-III-WAGON-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
143421_prefl	143421	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-PREFL-01	MEDIUM	Ktype跨改款，Active外廓拆分。	READY
143421_facelift	143421	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-FACELIFT-01	MEDIUM	Ktype跨改款，Active外廓拆分。	READY
153469	153469	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	HIGH		READY
151776	151776	Hatchback	Focus IV		5	EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	HIGH		READY
158634	158634	Sedan	Focus IV		4	EU-FORD-FOCUS-IV-SEDAN-FACELIFT-01	HIGH		READY
153471	153471	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	HIGH		READY
151777	151777	Wagon	Focus IV		5	EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	HIGH		READY
18692_prefl	18692	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
18692_facelift	18692	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
16624_prefl	16624	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
16624_facelift	16624	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
16625_prefl	16625	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
16625_facelift	16625	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
56585	56585	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH		READY
16626_prefl	16626	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
16626_facelift	16626	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
18330_prefl	18330	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
18330_facelift	18330	MPV	Fusion I	JU2	5	EU-FORD-FUSION-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
8835	8835	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-PREFL-01	HIGH		READY
14797	14797	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
17611	17611	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
18755	18755	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
7812_prefl	7812	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
7812_facelift	7812	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
17307	17307	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
14796	14796	MPV	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
59494	59494	MPV	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH		READY
112237	112237	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
112239	112239	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
112242	112242	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
112243	112243	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
112245	112245	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
115107	115107	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
115110	115110	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
112247	112247	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
145520	145520	MPV	Galaxy III	CK	5	EU-FORD-GALAXY-III-MPV-01	HIGH		READY
142751_prefl	142751	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142751_facelift	142751	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142755	142755	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
142756	142756	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
142760_prefl	142760	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142760_facelift	142760	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142761	142761	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
142762_prefl	142762	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142762_facelift	142762	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142763	142763	Van	Galaxy I	WGR	5	EU-FORD-GALAXY-I-MPV-FACELIFT-01	HIGH		READY
142738_prefl	142738	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142738_facelift	142738	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142744	142744	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH		READY
142746_prefl	142746	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142746_facelift	142746	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142748_prefl	142748	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142748_facelift	142748	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142750	142750	Van	Galaxy II	WA6	5	EU-FORD-GALAXY-II-MPV-FACELIFT-01	HIGH		READY
11165	11165	Sedan	Granada II	GU	4	EU-FORD-GRANADA-II-SEDAN-FACELIFT-01	HIGH		READY
11560_prefl	11560	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
11560_facelift	11560	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
11561_prefl	11561	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
11561_facelift	11561	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
14968	14968	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM		READY
14969	14969	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-PREFL-01	MEDIUM		READY
14970_early	14970	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-EARLY-01	MEDIUM	Ktype跨1974年Coupe车身修订，按外廓拆分。	READY
14970_series2	14970	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	MEDIUM	Ktype跨1974年Coupe车身修订，按外廓拆分。	READY
14971_prefl	14971	Sedan	Granada II	GU	4	EU-FORD-GRANADA-II-SEDAN-PREFL-01	MEDIUM	Ktype跨1981年改款，按外廓拆分。	READY
14971_facelift	14971	Sedan	Granada II	GU	4	EU-FORD-GRANADA-II-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1981年改款，按外廓拆分。	READY
15275_early	15275	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-EARLY-01	MEDIUM	Ktype跨1974年Coupe车身修订，按外廓拆分。	READY
15275_series2	15275	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	MEDIUM	Ktype跨1974年Coupe车身修订，按外廓拆分。	READY
17041_prefl	17041	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
17041_facelift	17041	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6602_prefl	6602	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6602_facelift	6602	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6605_early	6605	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-EARLY-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6605_series2_prefl	6605	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6605_series2_facelift	6605	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-FACELIFT-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6608_prefl	6608	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6608_facelift	6608	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6603_prefl	6603	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6603_facelift	6603	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6606_early	6606	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-EARLY-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6606_series2_prefl	6606	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6606_series2_facelift	6606	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-FACELIFT-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
15277_prefl	15277	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
15277_facelift	15277	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6604_prefl	6604	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6604_facelift	6604	Sedan	Granada I	GGFL	4	EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6607_early	6607	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-EARLY-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6607_series2_prefl	6607	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6607_series2_facelift	6607	Coupe	Granada I	GGCL	2	EU-FORD-GRANADA-I-COUPE-SERIES2-FACELIFT-01	MEDIUM	Ktype跨Coupe车身修订，按外廓拆分。	READY
6609_prefl	6609	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-PREFL-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
6609_facelift	6609	Wagon	Granada I	GGNL	5	EU-FORD-GRANADA-I-WAGON-FACELIFT-01	MEDIUM	Ktype跨1975年外观修订，按外廓拆分。	READY
15278_prefl	15278	Sedan	Granada II	GU	4	EU-FORD-GRANADA-II-SEDAN-PREFL-01	MEDIUM	Ktype跨1981年改款，按外廓拆分。	READY
15278_facelift	15278	Sedan	Granada II	GU	4	EU-FORD-GRANADA-II-SEDAN-FACELIFT-01	MEDIUM	Ktype跨1981年改款，按外廓拆分。	READY
56758_prefl	56758	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
56758_facelift	56758	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
56761_prefl	56761	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
56761_facelift	56761	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
145823	145823	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
145825	145825	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
111780	111780	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
111781	111781	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
111782	111782	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
111783	111783	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
10247_prefl	10247	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
10247_facelift	10247	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
111784	111784	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
111785	111785	MPV	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
108777_prefl	108777	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108777_facelift	108777	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108778_prefl	108778	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108778_facelift	108778	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
113257	113257	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
113297	113297	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH		READY
108779_prefl	108779	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108779_facelift	108779	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142765_prefl	142765	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
142765_facelift	142765	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108780_prefl	108780	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	HIGH	Ktype跨改款，按外廓拆分。	READY
108780_facelift	108780	Van	Grand C-Max II		5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	HIGH	Ktype跨改款，按外廓拆分。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/left18448_5601-5700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-III-HATCHBACK-RS-FACELIFT-01	4390	1823	1472	Auto-Data Ford Focus III Hatchback RS 2.3 EcoBoost AWD	https://www.auto-data.net/en/ford-focus-iii-hatchback-facelift-2014-rs-2.3-ecoboost-350hp-awd-24929
EU-FORD-FOCUS-III-HATCHBACK-ELECTRIC-01	4392	1824	1478	Automobile-Catalog Ford Focus Electric	https://www.automobile-catalog.com/car/2013/1591985/ford_focus_electric.html
EU-FORD-FOCUS-III-WAGON-FACELIFT-01	4560	1823	1492	Moottori Ford Focus Wagon 1.0 EcoBoost A6 Titanium	https://moottori.fi/koeajo/ford-focus-wagon-1-0-ecoboost-a6-titanium/
EU-FORD-FOCUS-III-WAGON-PREFL-01	4556	1823	1505	Automobile-Catalog Ford Focus Turnier 1.6 TDCi 115 Titanium	https://www.automobile-catalog.com/car/2011/1593470/ford_focus_turnier_1_6_tdci_115_titanium.html
EU-FORD-FOCUS-III-WAGON-ST-PREFL-01	4566	1823	1505	Auto-Data Ford Focus III Wagon ST 2.0 EcoBoost	https://www.auto-data.net/en/ford-focus-iii-wagon-st-2.0-ecoboost-250hp-20086
EU-FORD-FOCUS-III-WAGON-ST-FACELIFT-01	4563	1823	1486	Auto-Data Ford Focus III Wagon ST 2.0 EcoBoost;Auto-Data Ford Focus III Wagon ST 2.0 TDCi	https://www.auto-data.net/en/ford-focus-iii-wagon-facelift-2014-st-2.0-ecoboost-250hp-s-s-20092;https://www.auto-data.net/en/ford-focus-iii-wagon-facelift-2014-st-2.0-tdci-185hp-20090
EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-PREFL-01	4397	1844	1483	Auto-Data Ford Focus IV Active Hatchback 1.5 EcoBlue	https://www.auto-data.net/en/ford-focus-iv-active-hatchback-1.5-ecoblue-120hp-36132
EU-FORD-FOCUS-IV-HATCHBACK-ACTIVE-FACELIFT-01	4397	1844	1502	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-HATCHBACK-FACELIFT-01	4382	1825	1471	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-SEDAN-FACELIFT-01	4651	1825	1471	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FOCUS-IV-WAGON-FACELIFT-01	4672	1825	1494	Ford Hungary New Focus official brochure	https://www.ford.hu/content/dam/guxeu/hu/hu_hu/documents/brochures/cars/BRO-new_focus.pdf
EU-FORD-FUSION-I-MPV-PREFL-01	4020	1708	1503	AutoData1 Ford Fusion 1.2	https://www.autodata1.com/en/car/ford/fusion/fusion-12-75-hp
EU-FORD-FUSION-I-MPV-FACELIFT-01	4013	1724	1543	Automobile-Catalog Ford Fusion 1.4 TDCi Style	https://www.automobile-catalog.com/car/2008/1234295/ford_fusion_1_4_tdci_style.html
EU-FORD-GALAXY-I-MPV-PREFL-01	4617	1810	1730	Automobile-Catalog Ford Galaxy 1.9 TDi 90 Ghia	https://www.automobile-catalog.com/car/1999/959420/ford_galaxy_1_9_tdi_90_ghia.html
EU-FORD-GALAXY-I-MPV-FACELIFT-01	4641	1810	1732	Automobile-Catalog Ford Galaxy 1.9 TDi 115 Ambiente	https://www.automobile-catalog.com/car/2005/958745/ford_galaxy_1_9_tdi_115_ambiente.html
EU-FORD-GALAXY-II-MPV-FACELIFT-01	4819	1884	1770	Auto-Data Ford Galaxy II facelift 2010	https://www.auto-data.net/en/ford-galaxy-ii-facelift-2010-generation-10039
EU-FORD-GALAXY-III-MPV-01	4848	1916	1747	Auto-Data Ford Galaxy III 2.0 TDCi 150;Auto-Data Ford Galaxy III 2.5 Duratec Hybrid	https://www.auto-data.net/en/ford-galaxy-iii-2.0-tdci-150hp-s-s-22072;https://www.auto-data.net/en/ford-galaxy-iii-facelift-2019-2.5-duratec-190hp-hybrid-cvt-5-seats-42203
EU-FORD-GALAXY-II-MPV-PREFL-01	4820	1884	1723	Automobile-Catalog Ford Galaxy 2.0 TDCi 140 Ghia DPF	https://www.automobile-catalog.com/car/2010/1234400/ford_galaxy_2_0_tdci_140_ghia_dpf.html
EU-FORD-GRANADA-II-SEDAN-FACELIFT-01	4679	1800	1416	Automobile-Catalog Ford Granada 1.6 L	https://www.automobile-catalog.com/car/1981/924680/ford_granada_1_6_l.html
EU-FORD-GRANADA-I-SEDAN-PREFL-01	4572	1791	1369	Automobile-Catalog Ford Granada 2300	https://www.automobile-catalog.com/car/1972/34340/ford_granada_2300.html
EU-FORD-GRANADA-I-SEDAN-FACELIFT-01	4596	1791	1416	Automobile-Catalog Ford Granada 1700 L	https://www.automobile-catalog.com/car/1975/915575/ford_granada_1700_l.html
EU-FORD-GRANADA-I-WAGON-PREFL-01	4674	1791	1410	Automobile-Catalog Ford Granada Turnier 2300	https://www.automobile-catalog.com/car/1972/34355/ford_granada_turnier_2300.html
EU-FORD-GRANADA-I-WAGON-FACELIFT-01	4696	1791	1437	Automobile-Catalog Ford Granada Turnier 1700 L	https://www.automobile-catalog.com/car/1975/922940/ford_granada_turnier_1700_l_low_compr_.html
EU-FORD-GRANADA-I-COUPE-EARLY-01	4572	1791	1341	Automobile-Catalog Ford Granada 2300 GXL Coupe Serie 1	https://www.automobile-catalog.com/car/1972/915290/ford_granada_2300_gxl_2tur_.html
EU-FORD-GRANADA-I-COUPE-SERIES2-PREFL-01	4572	1791	1341	Automobile-Catalog Ford Granada 2300 GXL Coupe Serie 2	https://www.automobile-catalog.com/car/1974/917855/ford_granada_2300_gxl_coupe.html
EU-FORD-GRANADA-II-SEDAN-PREFL-01	4633	1791	1416	Automobile-Catalog Ford Granada 1.7	https://www.automobile-catalog.com/car/1978/923030/ford_granada_1_7.html
EU-FORD-GRANADA-I-COUPE-SERIES2-FACELIFT-01	4572	1791	1341	Automobile-Catalog Ford Granada 2300 Coupe	https://www.automobile-catalog.com/car/1975/917840/ford_granada_2300_coupe.html
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Automobile-Catalog Ford Grand C-Max 1.0 EcoBoost 100 Ambiente	https://www.automobile-catalog.com/car/2013/1776500/ford_grand_c-max_1_0_ecoboost_100_ambiente_studio.html
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-01	4519	1828	1642	Automobile-Catalog Ford Grand C-Max 1.5 TDCi 120 PowerShift	https://www.automobile-catalog.com/car/2018/2140610/ford_grand_c-max_1_5_tdci_120__powershift.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/left18448_5601-5700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/2008/1234295/ford_fusion_1_4_tdci_style.html "https://www.automobile-catalog.com/car/2008/1234295/ford_fusion_1_4_tdci_style.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（1719 行）
- 累计尺寸组：dimension_groups_final.tsv（410 行）

