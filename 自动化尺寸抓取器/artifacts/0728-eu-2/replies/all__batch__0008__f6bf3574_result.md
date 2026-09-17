# 任务：all 第 701-800 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0008__f6bf3574


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 701-800 行

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
all 第 701-800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Hyundai	Accent iii	1.5 Crdi GLS	Schrägheck	Frontantrieb	Diesel	81	110	Nov 2005	Nov 2010	2024-03-01	19903
Hyundai	Accent iii	1.4 GL	Stufenheck	Frontantrieb	Benzin	71	97	Nov 2005	Nov 2010	2024-03-01	19904
Skoda	Fabia i combi	1.4 16V	Kombi	Frontantrieb	Benzin	59	80	Apr 2006	Dec 2007	2024-03-01	19905
Hyundai	Accent iii	1.6 GLS	Stufenheck	Frontantrieb	Benzin	82	112	Nov 2005	Nov 2010	2024-03-01	19906
Hyundai	Accent iii	1.5 Crdi GLS	Stufenheck	Frontantrieb	Diesel	81	110	Nov 2005	Nov 2010	2024-03-01	19907
BMW	Z4 roadster	M	Cabriolet	Heckantrieb	Benzin	252	343	Jan 2006	Aug 2008	2024-03-01	19908
BMW	Z4	M	Coupe	Heckantrieb	Benzin	252	343	Apr 2006	Aug 2008	2024-03-01	19909
BMW	6	M6	Cabriolet	Heckantrieb	Benzin	373	507	Sep 2006	Aug 2010	2024-03-01	19910
Audi	A3	S3 Quattro	Schrägheck	Allrad	Benzin	195	265	Nov 2006	Aug 2012	2024-03-01	19914
Jeep	Grand cherokee iii	6.1 Srt8 4X4	Geländewagen geschlossen	Allrad	Benzin	313	426	Mar 2006	Dec 2010	2024-03-01	19916
Hyundai	Getz	1.4 I	Schrägheck	Frontantrieb	Benzin	71	97	Aug 2005	Dec 2010	2024-03-01	19917
Hyundai	Getz	1.5 Crdi	Schrägheck	Frontantrieb	Diesel	65	88	Aug 2005	Jun 2009	2024-03-01	19918
BMW	3	325 I	Coupe	Heckantrieb	Benzin	160	218	Jun 2006	Feb 2010	2024-03-01	19919
BMW	3	330 I	Coupe	Heckantrieb	Benzin	200	272	Sep 2006	Feb 2010	2024-03-01	19920
BMW	3	330 D	Coupe	Heckantrieb	Diesel	170	231	Mar 2006	Aug 2008	2024-03-01	19921
Opel	Vivaro a	2.0 Cdti	Bus	Frontantrieb	Diesel	66	90	Aug 2006	Jul 2014	2024-03-01	19922
Opel	Vivaro a	2.0 Cdti	Bus	Frontantrieb	Diesel	84	114	Aug 2006	Jul 2014	2024-03-01	19923
Opel	Vivaro a	2.5 Cdti	Bus	Frontantrieb	Diesel	107	146	Aug 2006	Jul 2014	2024-03-01	19924
Opel	Vivaro a	2.0 Ecotec	Bus	Frontantrieb	Benzin	86	117	Aug 2006	Jul 2014	2024-03-01	19925
Opel	Vivaro a	2.0 Ecotec	Kasten	Frontantrieb	Benzin	86	117	Aug 2006	Jul 2014	2024-03-01	19926
Opel	Vivaro a	2.0 Cdti	Kasten	Frontantrieb	Diesel	66	90	Aug 2006	Jul 2014	2024-03-01	19927
Opel	Vivaro a	2.0 Cdti	Kasten	Frontantrieb	Diesel	84	114	Aug 2006	Jul 2014	2024-03-01	19928
Opel	Vivaro a	2.5 Cdti	Kasten	Frontantrieb	Diesel	107	146	Aug 2006	Jul 2014	2024-03-01	19929
BMW	3	325 XI	Coupe	Allrad	Benzin	160	218	Sep 2006	Feb 2010	2024-03-01	19930
BMW	3	330 XI	Coupe	Allrad	Benzin	200	272	Sep 2006	Aug 2007	2024-03-01	19931
BMW	3	330 XD	Coupe	Allrad	Diesel	170	231	Mar 2006	Aug 2008	2024-03-01	19932
Opel	Meriva a	1.6 Turbo	Großraumlimousine	Frontantrieb	Benzin	132	180	Sep 2005	May 2010	2024-03-01	19933
Opel	Meriva a	1.7 Cdti	Großraumlimousine	Frontantrieb	Diesel	92	125	Sep 2006	May 2010	2024-03-01	19934
Hyundai	Sonata v	2.0 Crdi	Stufenheck	Frontantrieb	Diesel	103	140	Feb 2006	Dec 2010	2024-03-01	19935
Dacia	Logan	1.5 DCI	Stufenheck	Frontantrieb	Diesel	50	68	Jan 2006	Dec 2012	2024-03-01	19936
Fiat	Strada	1.3 D Multijet	Pick-up	Frontantrieb	Diesel	62	85	May 2006	Aug 2012	2026-01-01	19937
KIA	Cee'd	1.4	Schrägheck	Frontantrieb	Benzin	80	109	Dec 2006	Dec 2012	2024-03-01	19938
KIA	Cee'd	1.6	Schrägheck	Frontantrieb	Benzin	90	122	Dec 2006	Dec 2012	2024-03-01	19939
KIA	Cee'd	2	Schrägheck	Frontantrieb	Benzin	105	143	Dec 2006	Dec 2012	2024-03-01	19940
KIA	Cee'd	1.6 Crdi 90	Schrägheck	Frontantrieb	Diesel	66	90	Dec 2006	Dec 2012	2024-03-01	19941
KIA	Cee'd	1.6 Crdi 115	Schrägheck	Frontantrieb	Diesel	85	115	Dec 2006	Dec 2012	2024-03-01	19942
Chevrolet	Captiva	2.0 D 4WD	SUV	Allrad	Diesel	110	150	Oct 2006	-	2024-03-01	19943
Dodge	Caliber	1.8	Schrägheck	Frontantrieb	Benzin	110	150	Jun 2006	Dec 2009	2024-03-01	19944
Dodge	Caliber	2	Schrägheck	Frontantrieb	Benzin	115	156	Jun 2006	-	2024-03-01	19945
Dodge	Caliber	2.4	Schrägheck	Frontantrieb	Benzin	125	170	Oct 2006	-	2024-03-01	19946
Dodge	Caliber	2.0 CRD	Schrägheck	Frontantrieb	Diesel	103	140	Jun 2006	-	2024-03-01	19947
Opel	Combo	1.7 Cdti 16V	Kasten/Großraumlimousine	Frontantrieb	Diesel	74	101	Dec 2004	-	2024-03-01	19948
BMW	5	525 D	Kombi	Heckantrieb	Diesel	120	163	Mar 2004	Mar 2007	2024-03-01	19949
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	120	163	Dec 2004	Mar 2010	2024-03-01	19950
BMW	3	318 CI	Coupe	Heckantrieb	Benzin	110	150	Mar 2004	May 2006	2024-03-01	19951
BMW	7	745 D	Stufenheck	Heckantrieb	Diesel	220	300	Mar 2005	Aug 2005	2024-03-01	19952
BMW	3	320 D	Stufenheck	Heckantrieb	Diesel	110	150	Dec 2004	Sep 2007	2024-03-01	19953
BMW	3	320 D	Kombi	Heckantrieb	Diesel	110	150	Dec 2004	Aug 2007	2024-03-01	19954
BMW	5	520 D	Stufenheck	Heckantrieb	Diesel	110	150	Sep 2005	Feb 2007	2024-03-01	19955
BMW	5	520 D	Kombi	Heckantrieb	Diesel	110	150	Sep 2005	Feb 2007	2024-03-01	19956
VW	Passat b6	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Mar 2005	May 2009	2024-03-01	19957
VW	Passat b6	2.0 TDI 4motion	Stufenheck	Allrad	Diesel	103	140	Mar 2005	May 2009	2024-03-01	19958
VW	Passat b6 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Aug 2005	May 2009	2024-03-01	19959
VW	Passat b6 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	103	140	Aug 2005	May 2009	2024-03-01	19960
VW	Golf v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Dec 2004	Nov 2008	2024-03-01	19961
VW	Golf v	2.0 TDI 4motion	Schrägheck	Allrad	Diesel	103	140	Jan 2007	Nov 2008	2024-03-01	19962
VW	Golf plus v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Dec 2005	May 2011	2024-03-01	19963
VW	Touran	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	103	140	Dec 2005	May 2010	2024-03-01	19964
VW	Jetta iii	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Oct 2005	Oct 2010	2024-03-01	19965
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Jun 2005	Jun 2008	2024-03-01	19966
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	103	140	Jan 2006	Jun 2008	2024-03-01	19967
Audi	A3	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Jun 2005	Jun 2008	2024-03-01	19968
Audi	A3	2.0 TDI Quattro	Schrägheck	Allrad	Diesel	103	140	Jan 2006	Jun 2008	2024-03-01	19969
Audi	A4 b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Nov 2004	Jun 2008	2024-03-01	19970
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Nov 2004	Jun 2008	2024-03-01	19971
Seat	Leon	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Oct 2005	Oct 2010	2024-03-01	19972
Renault	19 ii chamade	1.7	Stufenheck	Frontantrieb	Benzin	66	90	Apr 1992	Dec 1995	2024-03-01	19973
Fiat	Ducato	100 Multijet 2,2 D	Bus	Frontantrieb	Diesel	74	101	Jul 2006	May 2011	2025-12-01	19974
Fiat	Ducato	120 Multijet 2,3 D	Bus	Frontantrieb	Diesel	88	120	Jul 2006	Oct 2013	2025-06-01	19975
Fiat	Ducato	160 Multijet 3,0 D	Bus	Frontantrieb	Diesel	116	158	Jul 2006	May 2011	2025-06-01	19976
Fiat	Ducato	100 Multijet 2,2 D	Kasten	Frontantrieb	Diesel	74	101	Jul 2006	May 2011	2025-12-01	19977
Fiat	Ducato	120 Multijet 2,3 D	Kasten	Frontantrieb	Diesel	88	120	Jul 2006	-	2024-03-01	19978
Fiat	Ducato	160 Multijet 3,0 D	Kasten	Frontantrieb	Diesel	116	158	Jul 2006	May 2011	2025-06-01	19979
Fiat	Ducato	100 Multijet 2,2 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Jul 2006	May 2011	2025-12-01	19980
Fiat	Ducato	120 Multijet 2,3 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Jul 2006	-	2024-03-01	19981
Fiat	Ducato	160 Multijet 3,0 D	Pritsche/Fahrgestell	Frontantrieb	Diesel	116	158	Jul 2006	May 2014	2025-06-01	19982
Fiat	Multipla	1.6 16V	Großraumlimousine	Frontantrieb	Benzin	70	95	Apr 2002	Jun 2010	2024-03-01	19983
Fiat	Multipla	1.9 JTD	Großraumlimousine	Frontantrieb	Diesel	88	120	Apr 2002	Jun 2010	2024-03-01	19984
Fiat	Stilo	1.9 JTD	Schrägheck	Frontantrieb	Diesel	66	90	Sep 2004	Nov 2006	2024-03-01	19985
Opel	Signum cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	74	100	Aug 2005	Feb 2008	2024-03-01	19986
Opel	Vectra c caravan	3.0 V6 Cdti	Kombi	Frontantrieb	Diesel	135	184	Aug 2005	Aug 2008	2024-03-01	19987
Opel	Astra h gtc	2.0 Turbo	Schrägheck	Frontantrieb	Benzin	177	240	Aug 2005	Oct 2010	2024-03-01	19988
Volvo	V70 ii	2.4 D	Kombi	Frontantrieb	Diesel	93	126	Apr 2005	Dec 2008	2024-03-01	19989
Volvo	Xc90 i	D5 AWD	SUV	Allrad	Diesel	136	185	Apr 2005	Dec 2012	2024-07-01	19990
Suzuki	Jimny	1.3 16V 4X4	Geländewagen geschlossen	Allrad	Benzin	63	86	Aug 2005	-	2024-03-01	19991
Suzuki	Jimny	1.5 Ddis 4X4	Geländewagen geschlossen	Allrad	Diesel	63	86	Aug 2005	-	2024-03-01	19992
Opel	Movano a	3.0 DTI	Kasten	Frontantrieb	Diesel	100	136	Oct 2003	-	2024-03-01	19993
Suzuki	Wagon r+	1.3 4WD	Schrägheck	Allrad	Benzin	69	94	Sep 2003	-	2024-03-01	19994
BMW	3	325 D	Kombi	Heckantrieb	Diesel	145	197	Sep 2006	Jun 2012	2024-03-01	19995
Opel	Movano a	3.0 DTI	Bus	Frontantrieb	Diesel	100	136	Oct 2003	-	2024-03-01	19996
Opel	Movano a	2.5 DTI	Kasten	Frontantrieb	Diesel	73	99	Oct 2003	-	2024-03-01	19997
BMW	3	325 D	Stufenheck	Heckantrieb	Diesel	145	197	Sep 2006	Feb 2010	2024-03-01	19998
Skoda	Octavia	2.0 TDI	Schrägheck	Frontantrieb	Diesel	103	140	Nov 2005	May 2010	2024-03-01	20001
Skoda	Octavia	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Nov 2005	May 2010	2024-03-01	20002
Skoda	Superb i	2.0 TDI	Stufenheck	Frontantrieb	Diesel	103	140	Oct 2005	Mar 2008	2024-03-01	20003
Ford USA	Mustang	4.0 V6	Coupe	Heckantrieb	Benzin	157	214	Dec 2004	Dec 2010	2024-03-01	20004
Ford USA	Mustang	4.6 V8	Coupe	Heckantrieb	Benzin	224	305	Dec 2004	-	2024-03-01	20005
Ford USA	Mustang	5.4 V8	Coupe	Heckantrieb	Benzin	355	483	Jan 2006	-	2024-03-01	20006
Ford USA	Mustang convertible	4.0 V6	Cabriolet	Heckantrieb	Benzin	157	214	Dec 2005	Dec 2010	2024-03-01	20007
Ford USA	Mustang convertible	4.6 V8	Cabriolet	Heckantrieb	Benzin	224	305	Sep 2005	-	2024-03-01	20008


--- Round 1 / 首次发送 ---
## 更新点

* 本轮闭合 **21 个输入 Ktype、22 条映射行、13 个尺寸组**。
* `19914` 覆盖 Audi S3 8P 改款前后两种外廓：长度由 **4214 mm** 变为 **4230 mm**，因此拆分为 `prefl` 与 `facelift` 两条派生映射。([汽车数据网][1])
* Hyundai Getz 的可靠资料将三门和五门列为同一组三维，因此不创建无依据的门数派生组，`Doors` 暂留空。([汽车数据网][2])
* BMW E92 的 325i、330i xDrive、330xd 均命中同一双门 Coupe 外廓，发动机与驱动差异不重复建组。([汽车数据网][3])
* Opel Meriva A OPC 180 与 1.7 CDTI 125 的三维一致，复用同一改款后五门 MPV 尺寸组。([汽车数据网][4])

## 当前批次进度

* READY 映射：**22 行**
* 已覆盖输入 Ktype：**21 / 100**
* 尚未闭合输入 Ktype：**79**
* 已确认尺寸组：**13**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19903	19903	Hatchback	Accent III	MC	3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
19904	19904	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19905	19905	Wagon	Fabia I	6Y	5	EU-SKODA-FABIA-I-WAGON-5D-01	HIGH		READY
19906	19906	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19907	19907	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19908	19908	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-2D-01	HIGH		READY
19909	19909	Coupe	Z4 E86	E86	2	EU-BMW-Z4-E86-COUPE-2D-01	HIGH		READY
19910	19910	Convertible	M6 E64	E64	2	EU-BMW-M6-E64-CONVERTIBLE-2D-01	HIGH		READY
19914_prefl	19914	Hatchback	S3 8P	8P	3	EU-AUDI-S3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008改款前外廓。	READY
19914_facelift	19914	Hatchback	S3 8P	8P	3	EU-AUDI-S3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008改款后外廓。	READY
19916	19916	SUV	Grand Cherokee III	WK	5	EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	HIGH	SRT8专属外廓。	READY
19917	19917	Hatchback	Getz	TB		EU-HYUNDAI-GETZ-TB-HATCHBACK-01	HIGH	3门/5门三维一致；Doors留空。	READY
19918	19918	Hatchback	Getz	TB		EU-HYUNDAI-GETZ-TB-HATCHBACK-01	HIGH	3门/5门三维一致；Doors留空。	READY
19919	19919	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19920	19920	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19921	19921	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19930	19930	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19931	19931	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19932	19932	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19933	19933	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	OPC 180归入Meriva A改款后五门外廓。	READY
19934	19934	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH		READY
19935	19935	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	4045	1695	1470	Auto-Data Hyundai Accent Hatchback III 1.5 CRDi 110	https://www.auto-data.net/en/hyundai-accent-hatchback-iii-1.5-crdi-110hp-13683
EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	4280	1695	1470	Auto-Data Hyundai Accent III 1.4 GL 97	https://www.auto-data.net/en/hyundai-accent-iii-1.4-97hp-gl-13687
EU-SKODA-FABIA-I-WAGON-5D-01	4232	1646	1452	Auto-Data Skoda Fabia I Combi facelift 2004 1.4 16V 80	https://www.auto-data.net/en/skoda-fabia-i-combi-6y-facelift-2004-1.4-16v-80hp-36211
EU-BMW-Z4-E85-CONVERTIBLE-2D-01	4113	1781	1302	Auto-Data BMW Z4 E85 facelift M 3.2	https://www.auto-data.net/en/bmw-z4-e85-lci-facelift-2006-m-3.2-343hp-9909
EU-BMW-Z4-E86-COUPE-2D-01	4113	1781	1271	Auto-Data BMW Z4 Coupe E86 generation	https://www.auto-data.net/en/bmw-z4-coupe-e86-generation-2021
EU-BMW-M6-E64-CONVERTIBLE-2D-01	4871	1855	1377	Auto-Data BMW M6 Convertible E64 5.0 V10	https://www.auto-data.net/en/bmw-m6-convertible-e64-5.0-v10-507hp-smg-9869
EU-AUDI-S3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1399	Auto-Data Audi S3 8P 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8p-2.0-tfsi-265hp-quattro-4905
EU-AUDI-S3-8P-HATCHBACK-3D-FACELIFT-01	4230	1765	1399	Auto-Data Audi S3 8P facelift 2008 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8p-facelift-2008-2.0-tfsi-265hp-quattro-794
EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	4785	1870	1710	Auto-Data Jeep Grand Cherokee III WK SRT8	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-srt8-6.1i-v8-426hp-4x4-automatic-1157
EU-HYUNDAI-GETZ-TB-HATCHBACK-01	3825	1665	1490	Auto-Data Hyundai Getz 1.4 i 16V	https://www.auto-data.net/en/hyundai-getz-1.4-i-16v-97hp-13783
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395	Auto-Data BMW 3 Series Coupe E92 325i	https://www.auto-data.net/en/bmw-3-series-coupe-e92-325i-218hp-9953
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	Auto-Data Opel Meriva A facelift 2006 OPC 1.6 180; Auto-Data Opel Meriva A facelift 2006 1.7 CDTI 125	https://www.auto-data.net/en/opel-meriva-a-facelift-2006-opc-1.6i-16v-180hp-2520;https://www.auto-data.net/en/opel-meriva-a-facelift-2006-1.7-cdti-125hp-ecotec-25982
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475	Auto-Data Hyundai Sonata V NF 2.0 CRDi 140	https://www.auto-data.net/en/hyundai-sonata-v-nf-2.0-crdi-16v-140hp-13816
```

## 下一步优先处理

1. 批量闭合 Kia Cee’d、Dodge Caliber、Passat B6、Golf V、Audi A3 8P、A4 B7 等可多 Ktype 复用的乘用车尺寸组。
2. 核对 Opel Vivaro、Fiat Ducato、Opel Movano 的轴距、车顶高度及 Bus/Kasten 分支；这些 Ktype 不得在配置边界未确认前强行映射。
3. 随后处理 BMW E60/E61/E90/E91、Mustang S197、Volvo、Suzuki 等剩余聚类。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-s3-8p-2.0-tfsi-265hp-quattro-4905 "Audi S3 (8P) 2.0 TFSI (265 Hp) quattro | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/hyundai-getz-1.4-i-16v-97hp-13783 "Hyundai Getz 1.4 i 16V (97 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/bmw-3-series-coupe-e92-325i-218hp-9953 "BMW 3 Series Coupe (E92) 325i (218 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/opel-meriva-a-facelift-2006-opc-1.6i-16v-180hp-2520 "Opel Meriva A (facelift 2006) OPC 1.6i 16V (180 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 **20 个输入 Ktype、23 条映射、13 个尺寸组**。
* Kia Cee’d I 改款前后长宽高一致，本轮复用同一尺寸组，不因改款年份重复建组。([汽车数据网][1])
* Golf V 的 Ktype 同时覆盖三门和五门车身，已分别建立稳定派生行；两种车身三维相同，但门数物理边界不同。([汽车数据网][2])
* Audi A3 已按 8P1 三门与 8PA Sportback 五门分别闭合；前驱和 quattro 不重复建组。([汽车数据网][3])
* Touran Ktype 跨越 2006 年改款，改款前后长度不同，因此拆分为 `prefl` 与 `facelift`。([汽车数据网][4])
* Passat B6、Jetta V、Audi A4 B7 和 Seat Leon II 的发动机及驱动差异均未重复创建尺寸组。([汽车数据网][5])

## 当前批次进度

* READY 映射：**45 行**
* 已覆盖输入 Ktype：**41 / 100**
* PENDING 输入 Ktype：**59**
* 已确认尺寸组：**26**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19938	19938	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19939	19939	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19940	19940	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19941	19941	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19942	19942	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19957	19957	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-SEDAN-4D-01	HIGH		READY
19958	19958	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-SEDAN-4D-01	HIGH		READY
19959	19959	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-WAGON-5D-01	HIGH		READY
19960	19960	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-WAGON-5D-01	HIGH		READY
19961_3dr	19961	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	Ktype覆盖三门和五门车身；本行为三门分支。	READY
19961_5dr	19961	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	Ktype覆盖三门和五门车身；本行为五门分支。	READY
19962_3dr	19962	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	Ktype覆盖三门和五门车身；本行为三门分支。	READY
19962_5dr	19962	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	Ktype覆盖三门和五门车身；本行为五门分支。	READY
19964_prefl	19964	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-MPV-PREFL-01	HIGH	2006年改款前外廓。	READY
19964_facelift	19964	MPV	Touran I	1T2	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	2006年改款后外廓。	READY
19965	19965	Sedan	Jetta V	1K2	4	EU-VW-JETTA-V-SEDAN-4D-01	HIGH		READY
19966	19966	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-01	HIGH		READY
19967	19967	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-01	HIGH		READY
19968	19968	Hatchback	A3 Sportback 8PA	8PA	5	EU-AUDI-A3-8PA-HATCHBACK-5D-01	HIGH		READY
19969	19969	Hatchback	A3 Sportback 8PA	8PA	5	EU-AUDI-A3-8PA-HATCHBACK-5D-01	HIGH		READY
19970	19970	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19971	19971	Wagon	A4 B7 Avant	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19972	19972	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CEED-I-HATCHBACK-5D-01	4235	1790	1480	Auto-Data Kia Cee'd I 1.4 CVVT 109; Auto-Data Kia Cee'd I facelift 2009 1.6D 115	https://www.auto-data.net/en/kia-ceed-i-1.4-cvvt-109hp-42277;https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.6d-16v-115hp-17064
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tdi-140hp-28711
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-tdi-140hp-8902
EU-VW-GOLF-V-HATCHBACK-3D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-3-door-2.0-tdi-16v-140hp-8633
EU-VW-GOLF-V-HATCHBACK-5D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 5-door 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-5-door-2.0-tdi-16v-140hp-51645
EU-VW-TOURAN-I-MPV-PREFL-01	4391	1794	1635	Auto-Data Volkswagen Touran I 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-16v-140hp-44603
EU-VW-TOURAN-I-MPV-FACELIFT-01	4407	1794	1635	Auto-Data Volkswagen Touran I facelift 2006 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-2.0-tdi-140hp-44606
EU-VW-JETTA-V-SEDAN-4D-01	4554	1781	1459	Auto-Data Volkswagen Jetta V 2.0 TDI PDE 140	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-pde-140hp-dsg-46493
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005 2.0 TDI 140; Auto-Data Audi A3 8P facelift 2005 2.0 TDI quattro	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-8v-140hp-26888;https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-8v-140hp-quattro-27067
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA 2.0 TDI 140; Auto-Data Audi A3 Sportback 8PA 2.0 TDI quattro	https://www.auto-data.net/en/audi-a3-sportback-8pa-2.0-tdi-16v-140hp-4217;https://www.auto-data.net/en/audi-a3-sportback-8pa-2.0-tdi-8v-140hp-quattro-46445
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data Audi A4 B7 2.0 TDI 140	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-140hp-26679
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1427	Auto-Data Audi A4 Avant B7 2.0 TDI 140	https://www.auto-data.net/en/audi-a4-avant-b7-8e-2.0-tdi-140hp-4392
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458	Auto-Data Seat Leon II 1P 2.0 TDI 140	https://www.auto-data.net/en/seat-leon-ii-1p-2.0-tdi-16v-140hp-automatic-46460
```

## 下一步优先处理

1. 闭合 BMW E60/E61、E90/E91、E46 和 E65 聚类。
2. 处理 Skoda Octavia II、Superb I、Opel Signum、Vectra C Caravan、Astra H GTC、Volvo V70 II 与 XC90 I。
3. 最后集中处理 Vivaro、Ducato、Movano 等多轴距、多车顶及 Bus/Kasten 商用车分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/kia-ceed-i-1.4-cvvt-109hp-42277 "Kia Cee'd I 1.4 CVVT (109 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volkswagen-golf-v-3-door-2.0-tdi-16v-140hp-8633 "Volkswagen Golf V (3-door) 2.0 TDI 16V (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-8v-140hp-26888?utm_source=chatgpt.com "Audi A3 (8P, facelift 2005) 2.0 TDI 8V (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-16v-140hp-44603?utm_source=chatgpt.com "Volkswagen Touran I 2.0 TDI 16V (140 Hp) /Minivan 2004"
[5]: https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tdi-140hp-28711 "Volkswagen Passat (B6) 2.0 TDI (140 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 BMW E60/E61、E46、E65、E90/E91 与 Skoda Octavia II、Superb I 聚类，共覆盖 **13 个输入 Ktype**。
* BMW E60 Sedan 与 E61 Touring 分别复用尺寸组，不因 520d、525d 的功率版本差异重复建组。([汽车数据网][1])
* `19995` 和 `19998` 的生产区间跨越 2008 年 E9x LCI 改款；改款前后长度及部分外廓尺寸不同，均拆分为 `prefl`、`facelift` 两条映射。([汽车数据网][2])
* Superb I 改款前后长宽高一致，因此 `20003` 保持单行、复用一个尺寸组。([汽车数据网][3])

## 当前批次进度

* READY 映射：**60 行**
* 已覆盖输入 Ktype：**54 / 100**
* PENDING 输入 Ktype：**46**
* 已确认尺寸组：**39**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19949	19949	Wagon	5 Series E61	E61	5	EU-BMW-5-SERIES-E61-WAGON-5D-01	HIGH		READY
19950	19950	Sedan	5 Series E60	E60	4	EU-BMW-5-SERIES-E60-SEDAN-4D-01	HIGH		READY
19951	19951	Coupe	3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	HIGH		READY
19952	19952	Sedan	7 Series E65 facelift	E65	4	EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	HIGH		READY
19953	19953	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	HIGH		READY
19954	19954	Wagon	3 Series E46 facelift	E46	5	EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	HIGH		READY
19955	19955	Sedan	5 Series E60	E60	4	EU-BMW-5-SERIES-E60-SEDAN-4D-01	HIGH		READY
19956	19956	Wagon	5 Series E61	E61	5	EU-BMW-5-SERIES-E61-WAGON-5D-01	HIGH		READY
19995_prefl	19995	Wagon	3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	HIGH	2008年LCI改款前外廓。	READY
19995_facelift	19995	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	HIGH	2008年LCI改款后外廓。	READY
19998_prefl	19998	Sedan	3 Series E90	E90	4	EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	HIGH	2008年LCI改款前外廓。	READY
19998_facelift	19998	Sedan	3 Series E90 LCI	E90	4	EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	HIGH	2008年LCI改款后外廓。	READY
20001	20001	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	HIGH	五门掀背式车身。	READY
20002	20002	Wagon	Octavia II Combi	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-01	HIGH		READY
20003	20003	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-SEDAN-4D-01	HIGH	改款前后外廓尺寸一致。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491	Auto-Data BMW 5 Series Touring E61 525d 177	https://www.auto-data.net/en/bmw-5-series-touring-e61-525d-177hp-9615
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468	Auto-Data BMW 5 Series E60 525d 177	https://www.auto-data.net/en/bmw-5-series-e60-525d-177hp-9596
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369	Auto-Data BMW 3 Series Coupe E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-facelift-2003-318ci-143hp-46092
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	5039	1902	1491	Auto-Data BMW 7 Series E65 facelift 745d 300	https://www.auto-data.net/en/bmw-7-series-e65-facelift-2005-745d-300hp-steptronic-9718
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan E46 facelift 320d 150	https://www.auto-data.net/en/bmw-3-series-sedan-e46-facelift-2001-320d-150hp-9981
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410	Auto-Data BMW 3 Series Touring E46 facelift 320d 150	https://www.auto-data.net/en/bmw-3-series-touring-e46-facelift-2001-320d-150hp-10010
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440	Auto-Data BMW 3 Series Touring E91 325d 197	https://www.auto-data.net/en/bmw-3-series-touring-e91-325d-197hp-37143
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI 325d 197	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-325d-197hp-17222
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420	Auto-Data BMW 3 Series Sedan E90 325d 197	https://www.auto-data.net/en/bmw-3-series-sedan-e90-325d-197hp-37133
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421	Auto-Data BMW 3 Series Sedan E90 LCI 325d 197	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-325d-197hp-27770
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462	Auto-Data Skoda Octavia II 2.0 TDI PD 140	https://www.auto-data.net/en/skoda-octavia-ii-2.0-tdi-pd-140hp-14215
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi 2.0 TDI 140	https://www.auto-data.net/en/skoda-octavia-ii-combi-2.0-tdi-140hp-14230
EU-SKODA-SUPERB-I-SEDAN-4D-01	4803	1765	1469	Auto-Data Skoda Superb I 2.0 TDI PD 140; Auto-Data Skoda Superb I facelift 2.0 TDI PD 140	https://www.auto-data.net/en/skoda-superb-i-2.0-tdi-pd-140hp-dpf-23249;https://www.auto-data.net/en/skoda-superb-i-facelift-2006-2.0-tdi-pd-140hp-44982
```

## 下一步优先处理

1. 闭合 Dacia Logan、Fiat Strada、Chevrolet Captiva、Dodge Caliber、Opel Combo 与 Golf Plus。
2. 处理 Fiat Multipla、Stilo、Opel Signum、Vectra C Caravan、Astra H GTC、Volvo V70 II、XC90 I、Suzuki Jimny 与 Wagon R+。
3. 最后集中处理 Vivaro、Ducato、Movano 的多轴距、多车顶和 Bus/Kasten/Pritsche 分支，以及 Mustang S197 Coupe/Convertible。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-5-series-e60-525d-177hp-9596 "BMW 5 Series (E60) 525d (177 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-3-series-touring-e91-325d-197hp-37143 "BMW 3 Series Touring (E91) 325d (197 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/skoda-superb-i-2.0-tdi-pd-140hp-dpf-23249 "Skoda Superb I 2.0 TDI PD (140 Hp) DPF | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 **17 个输入 Ktype、22 条映射行、17 个尺寸组**。
* Logan、Golf Plus、Multipla 和 Astra H GTC 的生产区间跨越外廓发生变化的改款节点，已按 `prefl`、`facelift` 拆分。([汽车数据网][1])
* Mustang 4.0 V6 与普通 4.6 V8 Coupe 复用标准 Mustang V 外廓；5.4 V8 483 HP 对应独立的 Shelby GT500 外廓。([汽车数据网][2])
* Renault 19 Chamade、Signum、Vectra C Caravan、V70 II、Jimny III 和 Wagon R+ II 已完成首次建组。([汽车数据网][3])

## 当前批次进度

* READY 映射：**82 行**
* 已覆盖输入 Ktype：**71 / 100**
* PENDING 输入 Ktype：**29**
* 已确认尺寸组：**56**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19936_prefl	19936	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	2008年改款前外廓。	READY
19936_facelift	19936	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	2008年改款后外廓。	READY
19963_prefl	19963	MPV	Golf V Plus		5	EU-VW-GOLF-V-PLUS-MPV-5D-01	HIGH	2008年改款前外廓。	READY
19963_facelift	19963	MPV	Golf VI Plus		5	EU-VW-GOLF-VI-PLUS-MPV-5D-01	HIGH	2008年改款后外廓。	READY
19973	19973	Sedan	19 Chamade facelift	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
19983_prefl	19983	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	2004年改款前外廓。	READY
19983_facelift	19983	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	MEDIUM	2004年改款后外廓。	READY
19984_prefl	19984	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	2004年改款前外廓。	READY
19984_facelift	19984	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	MEDIUM	2004年改款后外廓。	READY
19986	19986	Hatchback	Signum facelift		5	EU-OPEL-SIGNUM-FACELIFT-HATCHBACK-5D-01	HIGH		READY
19987	19987	Wagon	Vectra C Caravan facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
19988_prefl	19988	Hatchback	Astra H GTC		3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-PREFL-01	HIGH	2007年改款前OPC外廓。	READY
19988_facelift	19988	Hatchback	Astra H GTC facelift		3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-FACELIFT-01	HIGH	2007年改款后OPC外廓。	READY
19989	19989	Wagon	V70 II facelift		5	EU-VOLVO-V70-II-WAGON-FACELIFT-01	HIGH		READY
19991	19991	SUV	Jimny III facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	HIGH		READY
19992	19992	SUV	Jimny III facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	HIGH		READY
19994	19994	MPV	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	HIGH	可靠车型资料归类为Minivan/MPV。	READY
20004	20004	Coupe	Mustang V		2	EU-FORD-USA-MUSTANG-V-COUPE-2D-01	HIGH		READY
20005	20005	Coupe	Mustang V		2	EU-FORD-USA-MUSTANG-V-COUPE-2D-01	HIGH		READY
20006	20006	Coupe	Mustang V Shelby GT500		2	EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	HIGH	5.4 V8 483HP对应Shelby GT500外廓。	READY
20007	20007	Convertible	Mustang V Convertible		2	EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	HIGH		READY
20008	20008	Convertible	Mustang V Convertible		2	EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525	Auto-Data Dacia Logan I 1.5 dCi 65	https://www.auto-data.net/en/dacia-logan-i-1.5-dci-65hp-15892
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534	Auto-Data Dacia Logan I facelift 2008 1.5 dCi 75	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.5-dci-75hp-fap-17993
EU-VW-GOLF-V-PLUS-MPV-5D-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus generation	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412	Auto-Data Renault 19 Chamade L53 facelift 1.9 TD 90	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-1.9-td-90hp-10778
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695	Auto-Data Fiat Multipla 186 1.6 16V Blupower 95	https://www.auto-data.net/en/fiat-multipla-186-1.6-16v-blupower-95hp-7261
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690	Auto-Data Fiat Multipla 186 facelift 2004 generation	https://www.auto-data.net/en/fiat-multipla-186-facelift-2004-generation-7330
EU-OPEL-SIGNUM-FACELIFT-HATCHBACK-5D-01	4651	1798	1460	Auto-Data Opel Signum facelift 2005 1.9 CDTI 100	https://www.auto-data.net/en/opel-signum-facelift-2005-1.9-cdti-100hp-26795
EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	4839	1798	1500	Auto-Data Opel Vectra C Caravan facelift 2005 3.0 V6 CDTI 184	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-3.0-v6-cdti-184hp-2243
EU-OPEL-ASTRA-H-GTC-HATCHBACK-PREFL-01	4290	1753	1415	Auto-Data Opel Astra H GTC OPC 2.0 Turbo 240	https://www.auto-data.net/en/opel-astra-h-gtc-2.0i-16v-turbo-opc-240hp-2385
EU-OPEL-ASTRA-H-GTC-HATCHBACK-FACELIFT-01	4290	1753	1405	Auto-Data Opel Astra H GTC facelift 2007 OPC 2.0 Turbo 240	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-opc-2.0-turbo-ecotec-240hp-47436
EU-VOLVO-V70-II-WAGON-FACELIFT-01	4710	1804	1465	Auto-Data Volvo V70 II facelift 2004 2.4D 126	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4d-126hp-42645
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705	Auto-Data Suzuki Jimny III facelift 2005 generation	https://www.auto-data.net/en/suzuki-jimny-iii-facelift-2005-generation-3835
EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	3500	1600	1660	Auto-Data Suzuki Wagon R+ II 1.3 4WD	https://www.auto-data.net/en/suzuki-wagon-r-ii-1.3-i-16v-93hp-4wd-16498
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385	Auto-Data Ford Mustang V generation	https://www.auto-data.net/en/ford-mustang-v-generation-1713
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407	Auto-Data Ford Shelby II generation	https://www.auto-data.net/en/ford-shelby-ii-generation-1656
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415	Auto-Data Ford Mustang V Convertible generation	https://www.auto-data.net/en/ford-mustang-v-convertible-generation-1714
```

## 下一步优先处理

1. 集中闭合 Vivaro A 的 Bus/Kasten、SWB/LWB 和车顶高度分支。
2. 集中闭合 Ducato 的 Bus/Kasten/Pritsche、轴距及车顶高度分支。
3. 处理 Movano A 的 Bus/Kasten 多轴距与车顶分支。
4. 补齐 Strada、Captiva、Caliber、Combo、Stilo 与 XC90 的剩余外廓或宽度口径冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.5-dci-90hp-fap-17994?utm_source=chatgpt.com "Dacia Logan I (facelift 2008) 1.5 dCi (90 Hp) FAP"
[2]: https://www.auto-data.net/en/ford-mustang-v-generation-1713 "Ford Mustang V | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-1.9-td-90hp-10778 "1992 Renault 19 Chamade (L53) (facelift 1992) 1.9 TD (90 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮闭合 **11 个输入 Ktype、24 条映射行、9 个尺寸组**。
* Vivaro A Kasten 按官方资料拆分为 SWB/LWB 与标准顶/高顶四种明确外廓；四个发动机 Ktype 分别关联这四个尺寸组，不按发动机重复建组。
* Captiva I 已确认采用 4635 × 1850 × 1720 mm，其中宽度为不含后视镜口径。([汽车数据网][1])
* 四个 Dodge Caliber Ktype 共用同一五门外廓，官方规格同时覆盖本批对应的 1.8、2.0、2.4 和 2.0 柴油动力。
* Opel Combo 的输入车身类型同时包含 Kasten 与 Großraumlimousine，已拆为 Van、MPV 两条物理分支。([汽车数据网][2])
* Volvo XC90 I 已按官方技术规格闭合。

## 当前批次进度

* READY 映射：**106 行**
* 已覆盖输入 Ktype：**82 / 100**
* PENDING 输入 Ktype：**18**
* 已确认尺寸组：**65**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19926_swb_lowroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	MEDIUM	SWB标准顶Kasten分支。	READY
19926_swb_highroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶Kasten分支。	READY
19926_lwb_lowroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	MEDIUM	LWB标准顶Kasten分支。	READY
19926_lwb_highroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶Kasten分支。	READY
19927_swb_lowroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19927_swb_highroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19927_lwb_lowroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19927_lwb_highroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19928_swb_lowroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19928_swb_highroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19928_lwb_lowroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19928_lwb_highroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19929_swb_lowroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19929_swb_highroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19929_lwb_lowroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19929_lwb_highroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19943	19943	SUV	Captiva I		5	EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	HIGH		READY
19944	19944	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19945	19945	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19946	19946	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19947	19947	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19948_van	19948	Van	Combo C			EU-OPEL-COMBO-C-VAN-01	MEDIUM	Kasten分支。	READY
19948_mpv	19948	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-5D-01	MEDIUM	Großraumlimousine分支。	READY
19990	19990	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720	Auto-Data Chevrolet Captiva I generation; Automobile-Catalog 2007 Chevrolet Captiva	https://www.auto-data.net/en/chevrolet-captiva-i-generation-3206;https://www.automobile-catalog.com/car/2007/1209860/chevrolet_captiva_2_4_2wd_ls_7-pers_.html
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535	Dodge Caliber 2007 official specification Australia	https://xr793.com/wp-content/uploads/2023/01/2007-Dodge-Caliber-Specification-AUS.pdf
EU-OPEL-COMBO-C-VAN-01	4322	1684	1801	VanDimensions Opel Combo C	https://vandimensions.com/database/opel/combo-c
EU-OPEL-COMBO-C-MPV-5D-01	4332	1684	1801	Auto-Data Vauxhall Combo C 1.7 CDTI 100	https://www.auto-data.net/en/vauxhall-combo-c-1.7-cdti-100hp-25386
EU-VOLVO-XC90-I-SUV-5D-01	4798	1898	1784	Volvo XC90 Model Year 2005 official technical specifications	https://www.volvoclub.org.uk/current/VolvoXC90MY05PricesTechSpecs.pdf
```

## 下一步优先处理

1. 闭合 `19922–19925` Vivaro A Bus 的 SWB/LWB 客运车分支。
2. 集中处理 `19974–19982` Fiat Ducato Bus、Kasten、Pritsche/Fahrgestell 的轴距及车顶组合。
3. 闭合 `19993`、`19996`、`19997` Movano A 的 Bus/Kasten 多轴距与车顶分支。
4. 最后处理 `19937` Fiat Strada 与 `19985` Fiat Stilo 的车身分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/chevrolet-captiva-i-generation-3206?utm_source=chatgpt.com "Chevrolet Captiva I | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/vauxhall-combo-c-1.7-cdti-100hp-25386 "Vauxhall Combo C 1.7 CDTI (100 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_701-800_ktype_dimension_mapping_final.tsv
- all_701-800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 剩余 Vivaro A Bus、Fiat Strada、Fiat Ducato、Fiat Stilo、Opel Movano A 已全部闭合。
* 已完成机械检查：表头正确、`id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸与来源字段完整。
* 已生成两个指定文件名的最终 TSV。

## 当前批次进度

* 输入 Ktype：**100 / 100**
* READY 映射：**179 行**
* PENDING：**0**
* DIMENSION_GROUP：**95 组**
* 孤立尺寸组：**0**
* 缺失尺寸组引用：**0**

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19903	19903	Hatchback	Accent III	MC	3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
19904	19904	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19905	19905	Wagon	Fabia I	6Y	5	EU-SKODA-FABIA-I-WAGON-5D-01	HIGH		READY
19906	19906	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19907	19907	Sedan	Accent III	MC	4	EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	HIGH		READY
19908	19908	Convertible	Z4 E85	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-2D-01	HIGH		READY
19909	19909	Coupe	Z4 E86	E86	2	EU-BMW-Z4-E86-COUPE-2D-01	HIGH		READY
19910	19910	Convertible	M6 E64	E64	2	EU-BMW-M6-E64-CONVERTIBLE-2D-01	HIGH		READY
19914_prefl	19914	Hatchback	S3 8P	8P	3	EU-AUDI-S3-8P-HATCHBACK-3D-PREFL-01	HIGH	2008改款前外廓。	READY
19914_facelift	19914	Hatchback	S3 8P	8P	3	EU-AUDI-S3-8P-HATCHBACK-3D-FACELIFT-01	HIGH	2008改款后外廓。	READY
19916	19916	SUV	Grand Cherokee III	WK	5	EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	HIGH	SRT8专属外廓。	READY
19917	19917	Hatchback	Getz	TB		EU-HYUNDAI-GETZ-TB-HATCHBACK-01	HIGH	3门/5门三维一致；Doors留空。	READY
19918	19918	Hatchback	Getz	TB		EU-HYUNDAI-GETZ-TB-HATCHBACK-01	HIGH	3门/5门三维一致；Doors留空。	READY
19919	19919	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19920	19920	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19921	19921	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19922_swb	19922	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-SWB-01	HIGH	SWB客运Bus分支。	READY
19922_lwb	19922	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-LWB-01	HIGH	LWB客运Bus分支。	READY
19923_swb	19923	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-SWB-01	HIGH	SWB客运Bus分支。	READY
19923_lwb	19923	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-LWB-01	HIGH	LWB客运Bus分支。	READY
19924_swb	19924	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-SWB-01	HIGH	SWB客运Bus分支。	READY
19924_lwb	19924	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-LWB-01	HIGH	LWB客运Bus分支。	READY
19925_swb	19925	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-SWB-01	MEDIUM	SWB客运Bus分支。	READY
19925_lwb	19925	MPV	Vivaro A facelift			EU-OPEL-VIVARO-A-BUS-LWB-01	MEDIUM	LWB客运Bus分支。	READY
19926_swb_lowroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	MEDIUM	SWB标准顶Kasten分支。	READY
19926_swb_highroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	MEDIUM	SWB高顶Kasten分支。	READY
19926_lwb_lowroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	MEDIUM	LWB标准顶Kasten分支。	READY
19926_lwb_highroof	19926	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	MEDIUM	LWB高顶Kasten分支。	READY
19927_swb_lowroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19927_swb_highroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19927_lwb_lowroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19927_lwb_highroof	19927	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19928_swb_lowroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19928_swb_highroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19928_lwb_lowroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19928_lwb_highroof	19928	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19929_swb_lowroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	HIGH	SWB标准顶Kasten分支。	READY
19929_swb_highroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	HIGH	SWB高顶Kasten分支。	READY
19929_lwb_lowroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	HIGH	LWB标准顶Kasten分支。	READY
19929_lwb_highroof	19929	Van	Vivaro A facelift		4	EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	HIGH	LWB高顶Kasten分支。	READY
19930	19930	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19931	19931	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19932	19932	Coupe	3 Series E92	E92	2	EU-BMW-3-SERIES-E92-COUPE-2D-01	HIGH		READY
19933	19933	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	OPC 180归入Meriva A改款后五门外廓。	READY
19934	19934	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH		READY
19935	19935	Sedan	Sonata V	NF	4	EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	HIGH		READY
19936_prefl	19936	Sedan	Logan I		4	EU-DACIA-LOGAN-I-SEDAN-PREFL-01	MEDIUM	2008年改款前外廓。	READY
19936_facelift	19936	Sedan	Logan I facelift		4	EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	MEDIUM	2008年改款后外廓。	READY
19937_shortcab	19937	Pickup	Strada 178	178	2	EU-FIAT-STRADA-178-PICKUP-SHORTCAB-01	MEDIUM	短驾驶室分支。	READY
19937_longcab	19937	Pickup	Strada 178	178	2	EU-FIAT-STRADA-178-PICKUP-LONGCAB-01	MEDIUM	长驾驶室分支。	READY
19938	19938	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19939	19939	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19940	19940	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19941	19941	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19942	19942	Hatchback	Cee'd I	ED	5	EU-KIA-CEED-I-HATCHBACK-5D-01	HIGH		READY
19943	19943	SUV	Captiva I		5	EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	HIGH		READY
19944	19944	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19945	19945	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19946	19946	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19947	19947	Hatchback	Caliber		5	EU-DODGE-CALIBER-HATCHBACK-5D-01	HIGH		READY
19948_van	19948	Van	Combo C			EU-OPEL-COMBO-C-VAN-01	MEDIUM	Kasten分支。	READY
19948_mpv	19948	MPV	Combo C		5	EU-OPEL-COMBO-C-MPV-5D-01	MEDIUM	Großraumlimousine分支。	READY
19949	19949	Wagon	5 Series E61	E61	5	EU-BMW-5-SERIES-E61-WAGON-5D-01	HIGH		READY
19950	19950	Sedan	5 Series E60	E60	4	EU-BMW-5-SERIES-E60-SEDAN-4D-01	HIGH		READY
19951	19951	Coupe	3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	HIGH		READY
19952	19952	Sedan	7 Series E65 facelift	E65	4	EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	HIGH		READY
19953	19953	Sedan	3 Series E46 facelift	E46	4	EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	HIGH		READY
19954	19954	Wagon	3 Series E46 facelift	E46	5	EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	HIGH		READY
19955	19955	Sedan	5 Series E60	E60	4	EU-BMW-5-SERIES-E60-SEDAN-4D-01	HIGH		READY
19956	19956	Wagon	5 Series E61	E61	5	EU-BMW-5-SERIES-E61-WAGON-5D-01	HIGH		READY
19957	19957	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-SEDAN-4D-01	HIGH		READY
19958	19958	Sedan	Passat B6	3C2	4	EU-VW-PASSAT-B6-SEDAN-4D-01	HIGH		READY
19959	19959	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-WAGON-5D-01	HIGH		READY
19960	19960	Wagon	Passat B6	3C5	5	EU-VW-PASSAT-B6-WAGON-5D-01	HIGH		READY
19961_3dr	19961	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	Ktype覆盖三门和五门车身；本行为三门分支。	READY
19961_5dr	19961	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	Ktype覆盖三门和五门车身；本行为五门分支。	READY
19962_3dr	19962	Hatchback	Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-3D-01	HIGH	Ktype覆盖三门和五门车身；本行为三门分支。	READY
19962_5dr	19962	Hatchback	Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-5D-01	HIGH	Ktype覆盖三门和五门车身；本行为五门分支。	READY
19963_prefl	19963	MPV	Golf V Plus		5	EU-VW-GOLF-V-PLUS-MPV-5D-01	HIGH	2008年改款前外廓。	READY
19963_facelift	19963	MPV	Golf VI Plus		5	EU-VW-GOLF-VI-PLUS-MPV-5D-01	HIGH	2008年改款后外廓。	READY
19964_prefl	19964	MPV	Touran I	1T1	5	EU-VW-TOURAN-I-MPV-PREFL-01	HIGH	2006年改款前外廓。	READY
19964_facelift	19964	MPV	Touran I	1T2	5	EU-VW-TOURAN-I-MPV-FACELIFT-01	HIGH	2006年改款后外廓。	READY
19965	19965	Sedan	Jetta V	1K2	4	EU-VW-JETTA-V-SEDAN-4D-01	HIGH		READY
19966	19966	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-01	HIGH		READY
19967	19967	Hatchback	A3 8P	8P1	3	EU-AUDI-A3-8P-HATCHBACK-3D-01	HIGH		READY
19968	19968	Hatchback	A3 Sportback 8PA	8PA	5	EU-AUDI-A3-8PA-HATCHBACK-5D-01	HIGH		READY
19969	19969	Hatchback	A3 Sportback 8PA	8PA	5	EU-AUDI-A3-8PA-HATCHBACK-5D-01	HIGH		READY
19970	19970	Sedan	A4 B7	8EC	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19971	19971	Wagon	A4 B7 Avant	8ED	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19972	19972	Hatchback	Leon II	1P1	5	EU-SEAT-LEON-II-HATCHBACK-5D-01	HIGH		READY
19973	19973	Sedan	19 Chamade facelift	L53	4	EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	HIGH		READY
19974_swb_lowroof	19974	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	MEDIUM	SWB标准顶Bus分支。	READY
19974_mwb_highroof	19974	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	MEDIUM	MWB高顶Bus分支。	READY
19974_lwb_highroof	19974	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	MEDIUM	LWB高顶Bus分支。	READY
19975_swb_lowroof	19975	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	MEDIUM	SWB标准顶Bus分支。	READY
19975_mwb_highroof	19975	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	MEDIUM	MWB高顶Bus分支。	READY
19975_lwb_highroof	19975	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	MEDIUM	LWB高顶Bus分支。	READY
19976_swb_lowroof	19976	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	MEDIUM	SWB标准顶Bus分支。	READY
19976_mwb_highroof	19976	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	MEDIUM	MWB高顶Bus分支。	READY
19976_lwb_highroof	19976	MPV	Ducato III	250		EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	MEDIUM	LWB高顶Bus分支。	READY
19977_l1h1	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H1-01	MEDIUM	L1H1 Kasten分支。	READY
19977_l1h2	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H2-01	MEDIUM	L1H2 Kasten分支。	READY
19977_l2h1	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H1-01	MEDIUM	L2H1 Kasten分支。	READY
19977_l2h2	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H2-01	MEDIUM	L2H2 Kasten分支。	READY
19977_l3h2	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H2-01	MEDIUM	L3H2 Kasten分支。	READY
19977_l3h3	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H3-01	MEDIUM	L3H3 Kasten分支。	READY
19977_l4h2	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H2-01	MEDIUM	L4H2 Kasten分支。	READY
19977_l4h3	19977	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H3-01	MEDIUM	L4H3 Kasten分支。	READY
19978_l1h1	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H1-01	MEDIUM	L1H1 Kasten分支。	READY
19978_l1h2	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H2-01	MEDIUM	L1H2 Kasten分支。	READY
19978_l2h1	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H1-01	MEDIUM	L2H1 Kasten分支。	READY
19978_l2h2	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H2-01	MEDIUM	L2H2 Kasten分支。	READY
19978_l3h2	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H2-01	MEDIUM	L3H2 Kasten分支。	READY
19978_l3h3	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H3-01	MEDIUM	L3H3 Kasten分支。	READY
19978_l4h2	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H2-01	MEDIUM	L4H2 Kasten分支。	READY
19978_l4h3	19978	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H3-01	MEDIUM	L4H3 Kasten分支。	READY
19979_l1h1	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H1-01	MEDIUM	L1H1 Kasten分支。	READY
19979_l1h2	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L1H2-01	MEDIUM	L1H2 Kasten分支。	READY
19979_l2h1	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H1-01	MEDIUM	L2H1 Kasten分支。	READY
19979_l2h2	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L2H2-01	MEDIUM	L2H2 Kasten分支。	READY
19979_l3h2	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H2-01	MEDIUM	L3H2 Kasten分支。	READY
19979_l3h3	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L3H3-01	MEDIUM	L3H3 Kasten分支。	READY
19979_l4h2	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H2-01	MEDIUM	L4H2 Kasten分支。	READY
19979_l4h3	19979	Van	Ducato III	250		EU-FIAT-DUCATO-III-VAN-L4H3-01	MEDIUM	L4H3 Kasten分支。	READY
19980_swb	19980	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-SWB-01	MEDIUM	SWB底盘驾驶室分支。	READY
19980_mwb	19980	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MWB-01	MEDIUM	MWB底盘驾驶室分支。	READY
19980_mlwb	19980	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	MEDIUM	中长轴底盘驾驶室分支。	READY
19980_lwb	19980	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-LWB-01	MEDIUM	LWB底盘驾驶室分支。	READY
19980_xlwb	19980	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	MEDIUM	XLWB底盘驾驶室分支。	READY
19981_swb	19981	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-SWB-01	MEDIUM	SWB底盘驾驶室分支。	READY
19981_mwb	19981	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MWB-01	MEDIUM	MWB底盘驾驶室分支。	READY
19981_mlwb	19981	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	MEDIUM	中长轴底盘驾驶室分支。	READY
19981_lwb	19981	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-LWB-01	MEDIUM	LWB底盘驾驶室分支。	READY
19981_xlwb	19981	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	MEDIUM	XLWB底盘驾驶室分支。	READY
19982_swb	19982	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-SWB-01	MEDIUM	SWB底盘驾驶室分支。	READY
19982_mwb	19982	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MWB-01	MEDIUM	MWB底盘驾驶室分支。	READY
19982_mlwb	19982	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	MEDIUM	中长轴底盘驾驶室分支。	READY
19982_lwb	19982	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-LWB-01	MEDIUM	LWB底盘驾驶室分支。	READY
19982_xlwb	19982	Pickup	Ducato III	250	2	EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	MEDIUM	XLWB底盘驾驶室分支。	READY
19983_prefl	19983	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	2004年改款前外廓。	READY
19983_facelift	19983	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	MEDIUM	2004年改款后外廓。	READY
19984_prefl	19984	MPV	Multipla 186	186	5	EU-FIAT-MULTIPLA-186-MPV-PREFL-01	MEDIUM	2004年改款前外廓。	READY
19984_facelift	19984	MPV	Multipla 186 facelift	186	5	EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	MEDIUM	2004年改款后外廓。	READY
19985_3dr	19985	Hatchback	Stilo 192	192	3	EU-FIAT-STILO-192-HATCHBACK-3D-01	HIGH	三门掀背分支。	READY
19985_5dr	19985	Hatchback	Stilo 192	192	5	EU-FIAT-STILO-192-HATCHBACK-5D-01	HIGH	五门掀背分支。	READY
19986	19986	Hatchback	Signum facelift		5	EU-OPEL-SIGNUM-FACELIFT-HATCHBACK-5D-01	HIGH		READY
19987	19987	Wagon	Vectra C Caravan facelift		5	EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	HIGH		READY
19988_prefl	19988	Hatchback	Astra H GTC		3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-PREFL-01	HIGH	2007年改款前OPC外廓。	READY
19988_facelift	19988	Hatchback	Astra H GTC facelift		3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-FACELIFT-01	HIGH	2007年改款后OPC外廓。	READY
19989	19989	Wagon	V70 II facelift		5	EU-VOLVO-V70-II-WAGON-FACELIFT-01	HIGH		READY
19990	19990	SUV	XC90 I		5	EU-VOLVO-XC90-I-SUV-5D-01	HIGH		READY
19991	19991	SUV	Jimny III facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	HIGH		READY
19992	19992	SUV	Jimny III facelift		3	EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	HIGH		READY
19993_l1h1	19993	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L1H1-01	MEDIUM	L1H1 Kasten分支。	READY
19993_l1h2	19993	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L1H2-01	MEDIUM	L1H2 Kasten分支。	READY
19993_l2h2	19993	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L2H2-01	MEDIUM	L2H2 Kasten分支。	READY
19993_l3h2	19993	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L3H2-01	MEDIUM	L3H2 Kasten分支。	READY
19993_l3h3	19993	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L3H3-01	MEDIUM	L3H3 Kasten分支。	READY
19994	19994	MPV	Wagon R+ II		5	EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	HIGH	可靠车型资料归类为Minivan/MPV。	READY
19995_prefl	19995	Wagon	3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	HIGH	2008年LCI改款前外廓。	READY
19995_facelift	19995	Wagon	3 Series E91 LCI	E91	5	EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	HIGH	2008年LCI改款后外廓。	READY
19996_l1h1	19996	MPV	Movano A facelift			EU-OPEL-MOVANO-A-BUS-L1H1-01	MEDIUM	L1H1 Bus分支。	READY
19996_l2h2	19996	MPV	Movano A facelift			EU-OPEL-MOVANO-A-BUS-L2H2-01	MEDIUM	L2H2 Bus分支。	READY
19996_l3h3	19996	MPV	Movano A facelift			EU-OPEL-MOVANO-A-BUS-L3H3-01	MEDIUM	L3H3 Bus分支。	READY
19997_l1h1	19997	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L1H1-01	MEDIUM	L1H1 Kasten分支。	READY
19997_l1h2	19997	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L1H2-01	MEDIUM	L1H2 Kasten分支。	READY
19997_l2h2	19997	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L2H2-01	MEDIUM	L2H2 Kasten分支。	READY
19997_l3h2	19997	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L3H2-01	MEDIUM	L3H2 Kasten分支。	READY
19997_l3h3	19997	Van	Movano A facelift			EU-OPEL-MOVANO-A-VAN-L3H3-01	MEDIUM	L3H3 Kasten分支。	READY
19998_prefl	19998	Sedan	3 Series E90	E90	4	EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	HIGH	2008年LCI改款前外廓。	READY
19998_facelift	19998	Sedan	3 Series E90 LCI	E90	4	EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	HIGH	2008年LCI改款后外廓。	READY
20001	20001	Hatchback	Octavia II	1Z3	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	HIGH	五门掀背式车身。	READY
20002	20002	Wagon	Octavia II Combi	1Z5	5	EU-SKODA-OCTAVIA-II-WAGON-5D-01	HIGH		READY
20003	20003	Sedan	Superb I	3U4	4	EU-SKODA-SUPERB-I-SEDAN-4D-01	HIGH	改款前后外廓尺寸一致。	READY
20004	20004	Coupe	Mustang V		2	EU-FORD-USA-MUSTANG-V-COUPE-2D-01	HIGH		READY
20005	20005	Coupe	Mustang V		2	EU-FORD-USA-MUSTANG-V-COUPE-2D-01	HIGH		READY
20006	20006	Coupe	Mustang V Shelby GT500		2	EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	HIGH	5.4 V8 483HP对应Shelby GT500外廓。	READY
20007	20007	Convertible	Mustang V Convertible		2	EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	HIGH		READY
20008	20008	Convertible	Mustang V Convertible		2	EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_701-800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	4045	1695	1470	Auto-Data Hyundai Accent Hatchback III 1.5 CRDi 110	https://www.auto-data.net/en/hyundai-accent-hatchback-iii-1.5-crdi-110hp-13683
EU-HYUNDAI-ACCENT-III-SEDAN-4D-01	4280	1695	1470	Auto-Data Hyundai Accent III 1.4 GL 97	https://www.auto-data.net/en/hyundai-accent-iii-1.4-97hp-gl-13687
EU-SKODA-FABIA-I-WAGON-5D-01	4232	1646	1452	Auto-Data Skoda Fabia I Combi facelift 2004 1.4 16V 80	https://www.auto-data.net/en/skoda-fabia-i-combi-6y-facelift-2004-1.4-16v-80hp-36211
EU-BMW-Z4-E85-CONVERTIBLE-2D-01	4113	1781	1302	Auto-Data BMW Z4 E85 facelift M 3.2	https://www.auto-data.net/en/bmw-z4-e85-lci-facelift-2006-m-3.2-343hp-9909
EU-BMW-Z4-E86-COUPE-2D-01	4113	1781	1271	Auto-Data BMW Z4 Coupe E86 generation	https://www.auto-data.net/en/bmw-z4-coupe-e86-generation-2021
EU-BMW-M6-E64-CONVERTIBLE-2D-01	4871	1855	1377	Auto-Data BMW M6 Convertible E64 5.0 V10	https://www.auto-data.net/en/bmw-m6-convertible-e64-5.0-v10-507hp-smg-9869
EU-AUDI-S3-8P-HATCHBACK-3D-PREFL-01	4214	1765	1399	Auto-Data Audi S3 8P 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8p-2.0-tfsi-265hp-quattro-4905
EU-AUDI-S3-8P-HATCHBACK-3D-FACELIFT-01	4230	1765	1399	Auto-Data Audi S3 8P facelift 2008 2.0 TFSI quattro	https://www.auto-data.net/en/audi-s3-8p-facelift-2008-2.0-tfsi-265hp-quattro-794
EU-JEEP-GRAND-CHEROKEE-III-SUV-SRT8-01	4785	1870	1710	Auto-Data Jeep Grand Cherokee III WK SRT8	https://www.auto-data.net/en/jeep-grand-cherokee-iii-wk-srt8-6.1i-v8-426hp-4x4-automatic-1157
EU-HYUNDAI-GETZ-TB-HATCHBACK-01	3825	1665	1490	Auto-Data Hyundai Getz 1.4 i 16V	https://www.auto-data.net/en/hyundai-getz-1.4-i-16v-97hp-13783
EU-BMW-3-SERIES-E92-COUPE-2D-01	4580	1782	1395	Auto-Data BMW 3 Series Coupe E92 325i	https://www.auto-data.net/en/bmw-3-series-coupe-e92-325i-218hp-9953
EU-OPEL-VIVARO-A-BUS-SWB-01	4782	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-BUS-LWB-01	5182	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-SWB-LOWROOF-01	4782	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-SWB-HIGHROOF-01	4782	1904	2492	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-LOWROOF-01	5182	1904	1960	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-VIVARO-A-VAN-LWB-HIGHROOF-01	5182	1904	2492	Vauxhall Vivaro May 2008 official brochure	https://www.vauxhall.co.uk/content/dam/vauxhall/Home/PDFs/historical-brochures/discounted-models/vivaro/Vivaro_May_2008.pdf
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	Auto-Data Opel Meriva A facelift 2006 OPC 1.6 180; Auto-Data Opel Meriva A facelift 2006 1.7 CDTI 125	https://www.auto-data.net/en/opel-meriva-a-facelift-2006-opc-1.6i-16v-180hp-2520;https://www.auto-data.net/en/opel-meriva-a-facelift-2006-1.7-cdti-125hp-ecotec-25982
EU-HYUNDAI-SONATA-V-NF-SEDAN-4D-01	4800	1832	1475	Auto-Data Hyundai Sonata V NF 2.0 CRDi 140	https://www.auto-data.net/en/hyundai-sonata-v-nf-2.0-crdi-16v-140hp-13816
EU-DACIA-LOGAN-I-SEDAN-PREFL-01	4250	1735	1525	Auto-Data Dacia Logan I 1.5 dCi 65	https://www.auto-data.net/en/dacia-logan-i-1.5-dci-65hp-15892
EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01	4288	1740	1534	Auto-Data Dacia Logan I facelift 2008 1.5 dCi 75	https://www.auto-data.net/en/dacia-logan-i-facelift-2008-1.5-dci-75hp-fap-17993
EU-FIAT-STRADA-178-PICKUP-SHORTCAB-01	4444	1664	1525	Fiat Professional New Fiat Strada official press information	https://www.media.stellantis.com/em-en/fiat-professional/press/the-new-fiat-strada-is-coming
EU-FIAT-STRADA-178-PICKUP-LONGCAB-01	4444	1664	1525	Fiat Professional New Fiat Strada official press information	https://www.media.stellantis.com/em-en/fiat-professional/press/the-new-fiat-strada-is-coming
EU-KIA-CEED-I-HATCHBACK-5D-01	4235	1790	1480	Auto-Data Kia Cee'd I 1.4 CVVT 109; Auto-Data Kia Cee'd I facelift 2009 1.6D 115	https://www.auto-data.net/en/kia-ceed-i-1.4-cvvt-109hp-42277;https://www.auto-data.net/en/kia-ceed-i-facelift-2009-1.6d-16v-115hp-17064
EU-CHEVROLET-CAPTIVA-I-SUV-5D-01	4635	1850	1720	Auto-Data Chevrolet Captiva I generation; Automobile-Catalog 2007 Chevrolet Captiva	https://www.auto-data.net/en/chevrolet-captiva-i-generation-3206;https://www.automobile-catalog.com/car/2007/1209860/chevrolet_captiva_2_4_2wd_ls_7-pers_.html
EU-DODGE-CALIBER-HATCHBACK-5D-01	4415	1800	1535	Dodge Caliber 2007 official specification Australia	https://xr793.com/wp-content/uploads/2023/01/2007-Dodge-Caliber-Specification-AUS.pdf
EU-OPEL-COMBO-C-VAN-01	4322	1684	1801	VanDimensions Opel Combo C	https://vandimensions.com/database/opel/combo-c
EU-OPEL-COMBO-C-MPV-5D-01	4332	1684	1801	Auto-Data Vauxhall Combo C 1.7 CDTI 100	https://www.auto-data.net/en/vauxhall-combo-c-1.7-cdti-100hp-25386
EU-BMW-5-SERIES-E61-WAGON-5D-01	4843	1846	1491	Auto-Data BMW 5 Series Touring E61 525d 177	https://www.auto-data.net/en/bmw-5-series-touring-e61-525d-177hp-9615
EU-BMW-5-SERIES-E60-SEDAN-4D-01	4841	1846	1468	Auto-Data BMW 5 Series E60 525d 177	https://www.auto-data.net/en/bmw-5-series-e60-525d-177hp-9596
EU-BMW-3-SERIES-E46-COUPE-FACELIFT-2D-01	4488	1757	1369	Auto-Data BMW 3 Series Coupe E46 facelift 318Ci	https://www.auto-data.net/en/bmw-3-series-coupe-e46-facelift-2003-318ci-143hp-46092
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-4D-01	5039	1902	1491	Auto-Data BMW 7 Series E65 facelift 745d 300	https://www.auto-data.net/en/bmw-7-series-e65-facelift-2005-745d-300hp-steptronic-9718
EU-BMW-3-SERIES-E46-SEDAN-FACELIFT-4D-01	4471	1739	1415	Auto-Data BMW 3 Series Sedan E46 facelift 320d 150	https://www.auto-data.net/en/bmw-3-series-sedan-e46-facelift-2001-320d-150hp-9981
EU-BMW-3-SERIES-E46-WAGON-FACELIFT-5D-01	4480	1740	1410	Auto-Data BMW 3 Series Touring E46 facelift 320d 150	https://www.auto-data.net/en/bmw-3-series-touring-e46-facelift-2001-320d-150hp-10010
EU-VW-PASSAT-B6-SEDAN-4D-01	4765	1820	1472	Auto-Data Volkswagen Passat B6 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-passat-b6-2.0-tdi-140hp-28711
EU-VW-PASSAT-B6-WAGON-5D-01	4774	1820	1517	Auto-Data Volkswagen Passat Variant B6 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-passat-variant-b6-2.0-tdi-140hp-8902
EU-VW-GOLF-V-HATCHBACK-3D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 3-door 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-3-door-2.0-tdi-16v-140hp-8633
EU-VW-GOLF-V-HATCHBACK-5D-01	4204	1759	1485	Auto-Data Volkswagen Golf V 5-door 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-5-door-2.0-tdi-16v-140hp-51645
EU-VW-GOLF-V-PLUS-MPV-5D-01	4206	1759	1580	Auto-Data Volkswagen Golf V Plus 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-VW-GOLF-VI-PLUS-MPV-5D-01	4204	1759	1592	Auto-Data Volkswagen Golf VI Plus generation	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-VW-TOURAN-I-MPV-PREFL-01	4391	1794	1635	Auto-Data Volkswagen Touran I 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-touran-i-2.0-tdi-16v-140hp-44603
EU-VW-TOURAN-I-MPV-FACELIFT-01	4407	1794	1635	Auto-Data Volkswagen Touran I facelift 2006 2.0 TDI 140	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2006-2.0-tdi-140hp-44606
EU-VW-JETTA-V-SEDAN-4D-01	4554	1781	1459	Auto-Data Volkswagen Jetta V 2.0 TDI PDE 140	https://www.auto-data.net/en/volkswagen-jetta-v-2.0-tdi-pde-140hp-dsg-46493
EU-AUDI-A3-8P-HATCHBACK-3D-01	4214	1765	1421	Auto-Data Audi A3 8P facelift 2005 2.0 TDI 140; Auto-Data Audi A3 8P facelift 2005 2.0 TDI quattro	https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-8v-140hp-26888;https://www.auto-data.net/en/audi-a3-8p-facelift-2005-2.0-tdi-8v-140hp-quattro-27067
EU-AUDI-A3-8PA-HATCHBACK-5D-01	4286	1765	1423	Auto-Data Audi A3 Sportback 8PA 2.0 TDI 140; Auto-Data Audi A3 Sportback 8PA 2.0 TDI quattro	https://www.auto-data.net/en/audi-a3-sportback-8pa-2.0-tdi-16v-140hp-4217;https://www.auto-data.net/en/audi-a3-sportback-8pa-2.0-tdi-8v-140hp-quattro-46445
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data Audi A4 B7 2.0 TDI 140	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-140hp-26679
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1427	Auto-Data Audi A4 Avant B7 2.0 TDI 140	https://www.auto-data.net/en/audi-a4-avant-b7-8e-2.0-tdi-140hp-4392
EU-SEAT-LEON-II-HATCHBACK-5D-01	4315	1768	1458	Auto-Data Seat Leon II 1P 2.0 TDI 140	https://www.auto-data.net/en/seat-leon-ii-1p-2.0-tdi-16v-140hp-automatic-46460
EU-RENAULT-19-II-CHAMADE-SEDAN-4D-01	4248	1696	1412	Auto-Data Renault 19 Chamade L53 facelift 1.9 TD 90	https://www.auto-data.net/en/renault-19-chamade-l53-facelift-1992-1.9-td-90hp-10778
EU-FIAT-DUCATO-III-BUS-SWB-LOWROOF-01	4963	2050	2254	Fiat New Ducato passenger transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoPersoneConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-BUS-MWB-HIGHROOF-01	5413	2050	2524	Fiat New Ducato passenger transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoPersoneConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-BUS-LWB-HIGHROOF-01	5998	2050	2524	Fiat New Ducato passenger transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoPersoneConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L1H1-01	4963	2050	2254	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L1H2-01	4963	2050	2522	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L2H1-01	5413	2050	2254	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L2H2-01	5413	2050	2524	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L3H2-01	5998	2050	2524	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L3H3-01	5998	2050	2764	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L4H2-01	6363	2050	2539	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-VAN-L4H3-01	6363	2050	2779	Fiat New Ducato goods transport official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoMerciConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-CHASSIS-SWB-01	4908	2050	2254	Fiat New Ducato conversions official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-CHASSIS-MWB-01	5358	2050	2254	Fiat New Ducato conversions official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-CHASSIS-MLWB-01	5708	2050	2254	Fiat New Ducato conversions official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-CHASSIS-LWB-01	5943	2050	2254	Fiat New Ducato conversions official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-DUCATO-III-CHASSIS-XLWB-01	6308	2050	2254	Fiat New Ducato conversions official technical specifications	https://www.media.stellantis.com/uploads/em/2014/schede_tecniche/DucatoTrasfConv_CT_ENG.pdf
EU-FIAT-MULTIPLA-186-MPV-PREFL-01	3994	1871	1695	Auto-Data Fiat Multipla 186 1.6 16V Blupower 95	https://www.auto-data.net/en/fiat-multipla-186-1.6-16v-blupower-95hp-7261
EU-FIAT-MULTIPLA-186-MPV-FACELIFT-01	4090	1870	1690	Auto-Data Fiat Multipla 186 facelift 2004 generation	https://www.auto-data.net/en/fiat-multipla-186-facelift-2004-generation-7330
EU-FIAT-STILO-192-HATCHBACK-3D-01	4182	1784	1475	Fiat Stilo official eLearn body dimensions	https://aftersales.fiat.com/elearnsections/frmMainPage.aspx?langDesc=English&languageID=2&markID=1&modelID=2000001&modelName=Fiat+-+192+-+Stilo&nodeID=5013522&prodID=2001202&sectionName=Service+News&valID=2000108&validityName=1.4+16v
EU-FIAT-STILO-192-HATCHBACK-5D-01	4253	1756	1525	Fiat Stilo official eLearn body dimensions	https://aftersales.fiat.com/elearnsections/frmMainPage.aspx?langDesc=English&languageID=2&markID=1&modelID=2000001&modelName=Fiat+-+192+-+Stilo&nodeID=5013522&prodID=2001202&sectionName=Service+News&valID=2000108&validityName=1.4+16v
EU-OPEL-SIGNUM-FACELIFT-HATCHBACK-5D-01	4651	1798	1460	Auto-Data Opel Signum facelift 2005 1.9 CDTI 100	https://www.auto-data.net/en/opel-signum-facelift-2005-1.9-cdti-100hp-26795
EU-OPEL-VECTRA-C-CARAVAN-FACELIFT-5D-01	4839	1798	1500	Auto-Data Opel Vectra C Caravan facelift 2005 3.0 V6 CDTI 184	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-3.0-v6-cdti-184hp-2243
EU-OPEL-ASTRA-H-GTC-HATCHBACK-PREFL-01	4290	1753	1415	Auto-Data Opel Astra H GTC OPC 2.0 Turbo 240	https://www.auto-data.net/en/opel-astra-h-gtc-2.0i-16v-turbo-opc-240hp-2385
EU-OPEL-ASTRA-H-GTC-HATCHBACK-FACELIFT-01	4290	1753	1405	Auto-Data Opel Astra H GTC facelift 2007 OPC 2.0 Turbo 240	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-opc-2.0-turbo-ecotec-240hp-47436
EU-VOLVO-V70-II-WAGON-FACELIFT-01	4710	1804	1465	Auto-Data Volvo V70 II facelift 2004 2.4D 126	https://www.auto-data.net/en/volvo-v70-ii-facelift-2004-2.4d-126hp-42645
EU-VOLVO-XC90-I-SUV-5D-01	4798	1898	1784	Volvo XC90 Model Year 2005 official technical specifications	https://www.volvoclub.org.uk/current/VolvoXC90MY05PricesTechSpecs.pdf
EU-SUZUKI-JIMNY-III-SUV-FACELIFT-01	3665	1600	1705	Auto-Data Suzuki Jimny III facelift 2005 generation	https://www.auto-data.net/en/suzuki-jimny-iii-facelift-2005-generation-3835
EU-OPEL-MOVANO-A-VAN-L1H1-01	4899	1990	2253	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-VAN-L1H2-01	4899	1990	2496	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-VAN-L2H2-01	5399	1990	2493	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-VAN-L3H2-01	5899	1990	2490	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-VAN-L3H3-01	5899	1990	2720	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-SUZUKI-WAGON-R-PLUS-II-MPV-01	3500	1600	1660	Auto-Data Suzuki Wagon R+ II 1.3 4WD	https://www.auto-data.net/en/suzuki-wagon-r-ii-1.3-i-16v-93hp-4wd-16498
EU-BMW-3-SERIES-E91-WAGON-PREFL-5D-01	4520	1820	1440	Auto-Data BMW 3 Series Touring E91 325d 197	https://www.auto-data.net/en/bmw-3-series-touring-e91-325d-197hp-37143
EU-BMW-3-SERIES-E91-WAGON-FACELIFT-5D-01	4527	1817	1418	Auto-Data BMW 3 Series Touring E91 LCI 325d 197	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-325d-197hp-17222
EU-OPEL-MOVANO-A-BUS-L1H1-01	4899	1990	2253	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-BUS-L2H2-01	5399	1990	2493	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-OPEL-MOVANO-A-BUS-L3H3-01	5899	1990	2720	Anchor Vans Opel Movano dimensions	https://www.anchorvans.co.uk/specifications/movano
EU-BMW-3-SERIES-E90-SEDAN-PREFL-4D-01	4520	1820	1420	Auto-Data BMW 3 Series Sedan E90 325d 197	https://www.auto-data.net/en/bmw-3-series-sedan-e90-325d-197hp-37133
EU-BMW-3-SERIES-E90-SEDAN-FACELIFT-4D-01	4531	1817	1421	Auto-Data BMW 3 Series Sedan E90 LCI 325d 197	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-325d-197hp-27770
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-01	4572	1769	1462	Auto-Data Skoda Octavia II 2.0 TDI PD 140	https://www.auto-data.net/en/skoda-octavia-ii-2.0-tdi-pd-140hp-14215
EU-SKODA-OCTAVIA-II-WAGON-5D-01	4572	1769	1468	Auto-Data Skoda Octavia II Combi 2.0 TDI 140	https://www.auto-data.net/en/skoda-octavia-ii-combi-2.0-tdi-140hp-14230
EU-SKODA-SUPERB-I-SEDAN-4D-01	4803	1765	1469	Auto-Data Skoda Superb I 2.0 TDI PD 140; Auto-Data Skoda Superb I facelift 2006 2.0 TDI PD 140	https://www.auto-data.net/en/skoda-superb-i-2.0-tdi-pd-140hp-dpf-23249;https://www.auto-data.net/en/skoda-superb-i-facelift-2006-2.0-tdi-pd-140hp-44982
EU-FORD-USA-MUSTANG-V-COUPE-2D-01	4765	1875	1385	Auto-Data Ford Mustang V generation	https://www.auto-data.net/en/ford-mustang-v-generation-1713
EU-FORD-USA-MUSTANG-V-COUPE-GT500-01	4775	1877	1407	Auto-Data Ford Shelby II generation	https://www.auto-data.net/en/ford-shelby-ii-generation-1656
EU-FORD-USA-MUSTANG-V-CONVERTIBLE-2D-01	4765	1877	1415	Auto-Data Ford Mustang V Convertible generation	https://www.auto-data.net/en/ford-mustang-v-convertible-generation-1714
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_701-800_dimension_groups_final.tsv)

推进信号：COMPLETE


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-AUDI-A4-B7-WAGON-5D-01 的 HeightMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_701-800_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_701-800_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2094 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1054 行）

- 尺寸冲突协调：
  - EU-DACIA-LOGAN-I-SEDAN-PREFL-01 -> EU-DACIA-LOGAN-I-SEDAN-PREFL-02：4247x1740x1534 与 4250x1735x1525，创建新尺寸组
  - EU-DACIA-LOGAN-I-SEDAN-FACELIFT-01 -> EU-DACIA-LOGAN-I-SEDAN-FACELIFT-02：4290x1740x1534 与 4288x1740x1534，创建新尺寸组
  - EU-AUDI-A4-B7-WAGON-5D-01 -> EU-AUDI-A4-B7-WAGON-5D-02：4586x1772x1453 与 4586x1772x1427，创建新尺寸组
