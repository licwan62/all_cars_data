# 任务：all 第 1201-1300 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0013__517dff89


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

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Chevrolet	Caprice	5	Stufenheck	Heckantrieb	Benzin	170	231	Oct 1990	Sep 1993	2024-03-01	21827
Chevrolet	Caprice	5.7	Stufenheck	Heckantrieb	Benzin	138	188	Oct 1990	Sep 1992	2024-03-01	21828
Chevrolet	Caprice	5.7 LS	Stufenheck	Heckantrieb	Benzin	183	249	Oct 1993	Sep 1996	2024-03-01	21829
Chevrolet	Caprice	5	Kombi	Heckantrieb	Benzin	127	173	Oct 1990	Sep 1991	2024-03-01	21830
Chevrolet	Caprice	5.7	Kombi	Heckantrieb	Benzin	138	188	Oct 1991	Sep 1993	2024-03-01	21831
Chevrolet	Caprice	5.7	Kombi	Heckantrieb	Benzin	194	264	Oct 1993	Sep 1996	2024-03-01	21832
Chevrolet	Caprice	5.7	Kombi	Heckantrieb	Benzin	207	282	Oct 1993	Sep 1996	2024-03-01	21833
Chevrolet	Cavalier	2.2	Stufenheck	Frontantrieb	Benzin	71	97	Oct 1989	Sep 1991	2024-03-01	21834
Chevrolet	Cavalier	3.1	Coupe	Frontantrieb	Benzin	103	140	Oct 1989	Sep 1994	2024-03-01	21836
Chevrolet	Cavalier convertible	3.1	Cabriolet	Frontantrieb	Benzin	103	140	Oct 1989	Sep 1991	2024-03-01	21837
Chevrolet	Cavalier	2.2 RS	Stufenheck	Frontantrieb	Benzin	90	122	Oct 1991	Sep 1996	2024-03-01	21838
Buick	Century	2.8 Limited	Stufenheck	Frontantrieb	Benzin	82	112	Oct 1981	Aug 1986	2024-03-01	21845
Buick	Century	2.8 Custom	Kombi	Frontantrieb	Benzin	82	112	Sep 1983	Sep 1986	2024-03-01	21847
Buick	Century	3.3	Stufenheck	Frontantrieb	Benzin	119	162	Oct 1986	Dec 1990	2024-03-01	21850
Buick	Century	3.8 Custom	Stufenheck	Frontantrieb	Benzin	112	152	Sep 1985	Dec 1988	2024-03-01	21852
Buick	Century	3.3	Kombi	Frontantrieb	Benzin	119	162	Oct 1986	Sep 1991	2024-03-01	21854
Buick	Century	2.2 Special	Kombi	Frontantrieb	Benzin	87	118	Oct 1991	Dec 1996	2024-03-01	21858
Chrysler	Cirrus	2.0 LX	Stufenheck	Frontantrieb	Benzin	96	131	May 1994	Sep 1997	2024-03-01	21861
Chrysler	Cirrus	2.0 LX	Stufenheck	Frontantrieb	Benzin	98	133	Oct 1997	Sep 2000	2024-03-01	21862
Chrysler	Cirrus	2.5 LX	Stufenheck	Frontantrieb	Benzin	120	163	Oct 1994	Sep 2000	2024-03-01	21864
Honda	City	1.5	Stufenheck	Frontantrieb	Benzin	77	105	Feb 1997	Nov 1999	2024-03-01	21867
Honda	City	1.5	Stufenheck	Frontantrieb	Benzin	77	105	Dec 1999	Sep 2003	2024-03-01	21869
Honda	City	1.3	Stufenheck	Frontantrieb	Benzin	60	82	Oct 2005	Jul 2008	2024-03-01	21873
Lada	110	1.5	Stufenheck	Frontantrieb	Benzin	52	71	Jun 1996	Sep 2004	2024-03-01	21896
Seat	Leon	1.8 TSI	Kombi	Frontantrieb	Benzin	132	180	Oct 2013	Aug 2018	2024-03-01	21897
Chrysler	Concorde	3.3 LX	Stufenheck	Frontantrieb	Benzin	120	163	Oct 1992	Sep 1997	2024-03-01	21917
Chrysler	Concorde	2.7 LX	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1997	Sep 2003	2024-03-01	21919
Chrysler	Concorde	3.5 LX	Stufenheck	Frontantrieb	Benzin	174	237	Oct 1997	Sep 2003	2024-03-01	21920
Chrysler	Concorde	3.5 LX Supercharged	Stufenheck	Frontantrieb	Benzin	186	253	Oct 1997	Sep 2003	2024-03-01	21921
Bentley	Continental	6.75	Cabriolet	Heckantrieb	Benzin	166	226	Oct 1989	Sep 1992	2024-03-01	21925
Chevrolet	Corsa	1	Stufenheck	Frontantrieb	Benzin	50	68	Aug 1997	Jul 2002	2024-03-01	21927
Chevrolet	Corsa	1.7 D	Stufenheck	Frontantrieb	Diesel	44	60	Aug 2000	Jul 2002	2024-03-01	21931
Cadillac	Deville	4.6 Concours	Stufenheck	Frontantrieb	Benzin	205	279	Oct 1993	Sep 1999	2024-03-01	21969
Cadillac	Deville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1993	Sep 1999	2024-03-01	21970
Cadillac	Deville	4.9	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1993	Sep 1995	2024-03-01	21971
Cadillac	Deville	4.6	Stufenheck	Frontantrieb	Benzin	205	279	Oct 1999	Dec 2005	2024-03-01	21972
Cadillac	Deville	4.6	Stufenheck	Frontantrieb	Benzin	224	305	Oct 1999	Sep 2004	2024-03-01	21973
AMC	Eagle	4.2 4WD	Stufenheck	Allrad	Benzin	90	122	Oct 1979	Aug 1985	2024-03-01	21981
Buick	Electra	4.1	Stufenheck	Heckantrieb	Benzin	92	125	Oct 1981	Sep 1984	2024-03-01	21988
Lexus	Gs	250	Stufenheck	Heckantrieb	Benzin	154	209	Jan 2012	-	2024-03-01	21990
Buick	Electra	3.8	Stufenheck	Frontantrieb	Benzin	121	165	Oct 1986	Sep 1990	2024-03-01	21993
Buick	Electra	3	Stufenheck	Frontantrieb	Benzin	81	110	Oct 1984	Sep 1985	2024-03-01	21995
Buick	Electra	3.8	Stufenheck	Frontantrieb	Benzin	103	140	Oct 1984	Sep 1986	2024-03-01	21996
Buick	Electra	3.8	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1989	2024-03-01	21997
Buick	Electra	3.8	Stufenheck	Frontantrieb	Benzin	123	167	Oct 1984	Sep 1990	2024-03-01	21998
Buick	Electra	3.8	Stufenheck	Frontantrieb	Benzin	127	173	Oct 1990	Sep 1991	2024-03-01	21999
Honda	Element	2.4 Vtec 4X4	SUV	Allrad	Benzin	118	160	Jul 2002	Dec 2011	2024-03-01	22005
Chevrolet	Express	4.3	Kasten	Heckantrieb	Benzin	142	193	Oct 1995	Sep 1998	2024-03-01	22010
Cadillac	Fleetwood	4.9	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1990	Sep 1993	2024-03-01	22013
Cadillac	Fleetwood	5.7 Brougham	Stufenheck	Heckantrieb	Benzin	130	177	Oct 1989	Sep 1993	2024-03-01	22014
Cadillac	Fleetwood	5.7 D	Stufenheck	Heckantrieb	Diesel	77	105	Oct 1979	Sep 1985	2026-06-01	22017
Cadillac	Fleetwood	5.7	Stufenheck	Heckantrieb	Benzin	138	188	Sep 1992	Sep 1994	2024-03-01	22019
Cadillac	Fleetwood	5.7	Stufenheck	Heckantrieb	Benzin	194	264	Oct 1994	Sep 1997	2024-03-01	22020
Jeep	Wrangler iii	3.8	Geländewagen offen	Allrad	Benzin	153	208	Apr 2007	Dec 2011	2024-03-01	22024
Jeep	Wrangler iii	3.8 RWD	Geländewagen offen	Heckantrieb	Benzin	153	208	Apr 2007	Dec 2010	2024-03-01	22026
Maserati	Gransport	4.2	Coupe	Heckantrieb	Benzin	295	400	Jun 2004	Nov 2007	2024-03-01	22051
Maserati	Gransport	4.2	Cabriolet	Heckantrieb	Benzin	295	400	Oct 2004	-	2024-03-01	22052
Hyundai	H-1	2.5 D	Pritsche/Fahrgestell	Heckantrieb	Diesel	73	99	Jun 2000	Oct 2006	2024-03-01	22054
Daihatsu	Hijet	1.3	Pritsche/Fahrgestell	Heckantrieb	Benzin	48	65	Jun 1998	-	2024-03-01	22061
GMC	S15 jimmy	4.3	SUV	Heckantrieb	Benzin	110	150	Jan 1989	Dec 1994	2024-03-01	22094
GMC	S15 jimmy	4.3 AWD	SUV	Allrad	Benzin	110	150	Jan 1989	Dec 1994	2024-03-01	22095
Buick	Lesabre	3.8	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1986	Sep 1987	2024-03-01	22127
Buick	Lesabre	3.8	Stufenheck	Frontantrieb	Benzin	127	173	Oct 1991	Sep 1995	2024-03-01	22129
Chevrolet	Lumina	3.4 Z34	Stufenheck	Frontantrieb	Benzin	149	203	Oct 1989	Sep 1994	2024-03-01	22145
Chevrolet	Lumina	3.1	Stufenheck	Frontantrieb	Benzin	110	150	Oct 1994	Sep 1997	2024-03-01	22147
Bentley	Mulsanne	6.75 S	Stufenheck	Heckantrieb	Benzin	160	218	Oct 1989	Sep 1992	2024-07-01	22173
Buick	Regal	2.8	Stufenheck	Frontantrieb	Benzin	97	132	Oct 1987	Sep 1989	2024-03-01	22218
Buick	Regal	3.1	Stufenheck	Frontantrieb	Benzin	104	141	Oct 1988	Sep 1991	2024-03-01	22219
Buick	Regal	3.8	Stufenheck	Frontantrieb	Benzin	127	173	Oct 1989	Sep 1991	2024-03-01	22220
Buick	Regal	3.1	Stufenheck	Frontantrieb	Benzin	101	137	Oct 1991	Sep 1993	2024-03-01	22221
Buick	Regal	3.1	Stufenheck	Frontantrieb	Benzin	119	162	Oct 1993	Sep 1997	2024-03-01	22222
Buick	Regal	3.8	Stufenheck	Frontantrieb	Benzin	112	152	Oct 1991	Sep 1994	2024-03-01	22223
Buick	Regal	3.8	Stufenheck	Frontantrieb	Benzin	127	173	Oct 1991	Sep 1994	2024-03-01	22224
Buick	Regal	3.8	Stufenheck	Frontantrieb	Benzin	150	204	Oct 1991	Sep 1997	2024-03-01	22225
Buick	Roadmaster	5	Kombi	Heckantrieb	Benzin	127	173	Oct 1990	Sep 1992	2024-03-01	22234
Chevrolet	S10 pick up	4.3 AWD	Pick-up	Allrad	Benzin	119	162	Oct 1987	Sep 1991	2024-03-01	22243
Chevrolet	S10	2.2	Pick-up	Heckantrieb	Benzin	90	122	Oct 1994	Sep 1998	2024-03-01	22245
Chevrolet	S10	2.2 4X4	Pick-up	Allrad	Benzin	90	122	Oct 1994	Sep 1998	2024-03-01	22246
Chevrolet	S10	4.3 4X4	Pick-up	Allrad	Benzin	119	162	Oct 1994	Sep 1995	2024-03-01	22247
Mitsubishi	Eclipse i	2.0 Turbo	Coupe	Frontantrieb	Benzin	147	200	Dec 1989	Mar 1994	2024-03-01	22257
Renault	Laguna ii grandtour	1.6 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	79	107	Jun 2005	Dec 2007	2024-03-01	22259
Chrysler	Sebring	2.5 LE	Coupe	Frontantrieb	Benzin	120	163	May 1995	Dec 1996	2024-03-01	22285
Chevrolet	Spark	0.8	Schrägheck	Frontantrieb	Benzin	38	52	Sep 2000	Dec 2006	2024-03-01	22303
Chevrolet	Spark	0.8	Schrägheck	Frontantrieb	Benzin	37	50	May 2005	Feb 2010	2024-03-01	22305
Chevrolet	Spark	1.0 SX	Schrägheck	Frontantrieb	Benzin	46	63	May 2005	-	2024-03-01	22306
Maserati	Spyder	2.0 BI Turbo	Cabriolet	Heckantrieb	Benzin	177	241	Jun 1989	Sep 1996	2024-03-01	22307
Maserati	Spyder	2.8	Cabriolet	Heckantrieb	Benzin	165	224	Oct 1991	Sep 1995	2024-03-01	22309
Mercedes-benz	B-Klasse sports tourer	B 220 4-matic	Schrägheck	Allrad	Benzin	135	184	May 2013	Dec 2018	2024-03-01	22311
Ssangyong	Stavic	2.7 270 Sxdi	Großraumlimousine	Heckantrieb	Diesel	121	165	Feb 2005	Dec 2012	2026-06-01	22312
Ssangyong	Stavic	2.7 270 Sxdi 4X4	Großraumlimousine	Allrad	Diesel	121	165	Feb 2005	Dec 2012	2026-06-01	22313
Suzuki	Grand vitara ii	2	Geländewagen geschlossen	Heckantrieb	Benzin	103	140	Oct 2005	Feb 2015	2024-03-01	22327
Chevrolet	Tahoe	5.7 AWD	SUV	Allrad	Benzin	147	200	Oct 1994	Sep 1995	2024-03-01	22345
Chevrolet	Tahoe	6.5 Tdic	SUV	Heckantrieb	Diesel	135	184	Oct 1994	Sep 1996	2024-03-01	22346
Chevrolet	Tahoe	6.5 Tdic AWD	SUV	Allrad	Diesel	135	184	Oct 1994	Sep 1996	2024-03-01	22347
Bentley	Turbo r	6.7	Stufenheck	Heckantrieb	Benzin	235	320	Oct 1985	Jun 1997	2024-03-01	22381
Chevrolet	Zafira	2	Großraumlimousine	Frontantrieb	Benzin	100	136	Apr 2001	Jul 2012	2024-03-01	22433
Peugeot	106 i	1.4	Schrägheck	Frontantrieb	Benzin	51	69	Aug 1991	Mar 1996	2024-03-01	22443
Suzuki	Grand vitara ii	1.6	Geländewagen geschlossen	Heckantrieb	Benzin	78	106	Oct 2005	-	2024-03-01	22449
Suzuki	Grand vitara i	1.6 4X4	Geländewagen geschlossen	Allrad	Benzin	71	97	Sep 2003	Sep 2005	2024-03-01	22453
Mercedes-benz	C-Klasse	C 200 CDI	Stufenheck	Heckantrieb	Diesel	100	136	Jan 2007	Dec 2009	2024-03-01	22457


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 Chevrolet Caprice 第四代的改款前轿车、改款后轿车和旅行车三个尺寸组；Cavalier 第二代按 1991 年改款拆分轿车与 Coupe，但第三代轿车的公开车长、车宽仍存在实质冲突，因此不强行建组。([汽车目录][1])
* 输入中的 Chrysler Cirrus 2.0/2.5 欧洲版本与 JA 平台 Chrysler Stratus 的动力及外廓对应，本轮归并为一个四门尺寸组，映射置信度暂定为 MEDIUM。([汽车数据网][2])
* 已闭合 Honda City 第三代改款前、Lada 110、Seat Leon III ST、Lexus GS IV，以及 Honda Element 改款前后尺寸组。Honda City 2000 年改款后的车长和 2005 年 GD6 的车宽仍有来源冲突，继续保留 PENDING。([维基百科][3])

## 当前批次进度

* 输入 Ktype：100
* 已覆盖研究 Ktype：21
* READY 输入 Ktype：17
* 已明确 PENDING 输入 Ktype：4
* 尚未研究 Ktype：79
* 当前合计待完成 Ktype：83
* READY 映射行：22
* PENDING 映射行：4
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21827	21827	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH		READY
21828	21828	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH		READY
21829_prefl	21829	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH	1994年款改款前外廓。	READY
21829_facelift	21829	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	HIGH	1995-1996年款改款后外廓。	READY
21830	21830	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21831	21831	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21832	21832	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21833	21833	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21834_prefl	21834	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-PREFL-01	HIGH	1990年款改款前外廓。	READY
21834_facelift	21834	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	HIGH	1991年款改款后外廓。	READY
21836_prefl	21836	Coupe	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-COUPE-PREFL-01	HIGH	1990年款改款前外廓。	READY
21836_facelift	21836	Coupe	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-COUPE-FACELIFT-01	HIGH	1991-1994年款改款后外廓。	READY
21837	21837	Convertible	Cavalier II	J	2		LOW	输入生产期覆盖1990-1991车型年，但3.1敞篷的恢复时间边界仍需锁定。	PENDING: 敞篷车型年边界未闭合
21838_gen2	21838	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	HIGH	1992-1994年款第二代改款后外廓。	READY
21838_gen3	21838	Sedan	Cavalier III	J	4		LOW	1995-1996年款第三代；公开规格存在4580/4630 mm车长及1684/1704/1712 mm车宽冲突。	PENDING: 第三代轿车三维来源冲突
21861	21861	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.0版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21862	21862	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.0版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21864	21864	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.5版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21867	21867	Sedan	City III	3A3	4	EU-HONDA-CITY-III-SEDAN-PREFL-01	HIGH		READY
21869	21869	Sedan	City III	3A3	4		LOW	2000年Type Z改款边界已确认，但改款后车长来源存在4225 mm与4270 mm冲突。	PENDING: 改款后车长来源冲突
21873	21873	Sedan	City IV	GD6	4		LOW	候选为GD6四门改款车身；公开规格的车宽存在1595 mm与1690 mm冲突。	PENDING: 车宽来源冲突
21896	21896	Sedan	Lada 110	VAZ-2110	4	EU-LADA-110-SEDAN-01	HIGH		READY
21897	21897	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	MEDIUM		READY
21990	21990	Sedan	GS IV	GRL11	4	EU-LEXUS-GS-IV-SEDAN-01	HIGH		READY
22005_prefl	22005	SUV	Element I	YH2	5	EU-HONDA-ELEMENT-I-SUV-PREFL-01	MEDIUM	2003-2008年款改款前外廓。	READY
22005_facelift	22005	SUV	Element I	YH2	5	EU-HONDA-ELEMENT-I-SUV-FACELIFT-01	MEDIUM	2009-2011年款改款后外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440	Automobile-Catalog 1991 Chevrolet Caprice Sedan 5.0L V8;Automobile-Catalog 1993 Chevrolet Caprice Classic LS Sedan 5.0L V8	https://www.automobile-catalog.com/car/1991/471800/chevrolet_caprice_sedan_5_0l_v-8.html;https://www.automobile-catalog.com/car/1993/471920/chevrolet_caprice_classic_ls_sedan_5_0l_v-8.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415	Automobile-Catalog 1995 Chevrolet Caprice Classic Sedan 5.7L V8	https://www.automobile-catalog.com/car/1995/472115/chevrolet_caprice_classic_sedan_5_7l_v-8.html
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547	Automobile-Catalog 1991 Chevrolet Caprice Station Wagon 5.0L V8	https://www.automobile-catalog.com/car/1991/471845/chevrolet_caprice_station_wagon_5_0l_v-8.html
EU-CHEVROLET-CAVALIER-II-SEDAN-PREFL-01	4536	1676	1361	Edmunds 1990 Chevrolet Cavalier Sedan specifications	https://www.edmunds.com/chevrolet/cavalier/1990/sedan/features-specs/
EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	4630	1684	1361	Edmunds 1992 Chevrolet Cavalier specifications	https://www.edmunds.com/chevrolet/cavalier/1992/features-specs/
EU-CHEVROLET-CAVALIER-II-COUPE-PREFL-01	4531	1676	1321	Automobile-Catalog 1990 Chevrolet Cavalier Coupe 2.2L EFI	https://www.automobile-catalog.com/car/1990/468305/chevrolet_cavalier_coupe_2_2l_efi.html
EU-CHEVROLET-CAVALIER-II-COUPE-FACELIFT-01	4630	1684	1321	Automobile-Catalog 1992 Chevrolet Cavalier Z24 Coupe	https://www.automobile-catalog.com/car/1992/468905/chevrolet_cavalier_z24_coupe.html
EU-CHRYSLER-CIRRUS-I-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus JA 2.0 LE;Auto-Data Chrysler Stratus JA 2.5 LX V6	https://www.auto-data.net/en/chrysler-stratus-ja-2.0-le-131hp-14720;https://www.auto-data.net/en/chrysler-stratus-ja-2.5-lx-v6-163hp-14721
EU-HONDA-CITY-III-SEDAN-PREFL-01	4225	1690	1400	Auto-Data Honda City Sedan III 1.5i 16V	https://www.auto-data.net/en/honda-city-sedan-iii-1.5i-16v-105hp-12188
EU-LADA-110-SEDAN-01	4277	1676	1430	Auto-Data Lada 2110 model specifications	https://www.auto-data.net/en/lada-2110-model-1423
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data Seat Leon III ST 1.8 TSI specifications	https://www.auto-data.net/en/seat-leon-iii-st-1.8-tsi-180hp-start-stop-19415
EU-LEXUS-GS-IV-SEDAN-01	4850	1840	1455	Auto-Data Lexus GS IV 250 V6 specifications	https://www.auto-data.net/en/lexus-gs-iv-250-v6-209hp-automatic-21321
EU-HONDA-ELEMENT-I-SUV-PREFL-01	4326	1816	1788	Automobile-Catalog 2008 Honda Element EX 4WD	https://www.automobile-catalog.com/car/2008/1144160/honda_element_ex_4wd.html
EU-HONDA-ELEMENT-I-SUV-FACELIFT-01	4315	1819	1788	Honda 2009 Element official specifications;Car and Driver 2009 Honda Element specifications	https://hondanews.com/en-US/releases/release-86da9dae004ffe6c4bd1af004c34bc16-2009-honda-element-specifications-and-features;https://www.caranddriver.com/honda/element/specs/2009/honda_element_honda-element_2009
```

## 下一步优先处理

1. 优先解决 `21837`、`21838_gen3`、`21869`、`21873` 四个已定位冲突，避免重新核对已闭合尺寸组。
2. 按 Buick 共平台车型聚类处理 Century、Electra、LeSabre、Regal、Roadmaster，批量复用相同外廓。
3. 随后处理 Cadillac DeVille/Fleetwood，以及容易出现轴距、车顶或车身长度分支的 Express、S10、Tahoe、Wrangler、H-1 和 Hijet。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1991/471800/chevrolet_caprice_sedan_5_0l_v-8.html "https://www.automobile-catalog.com/car/1991/471800/chevrolet_caprice_sedan_5_0l_v-8.html"
[2]: https://www.auto-data.net/en/chrysler-stratus-ja-2.0-le-131hp-14720 "https://www.auto-data.net/en/chrysler-stratus-ja-2.0-le-131hp-14720"
[3]: https://en.wikipedia.org/wiki/Honda_City?utm_source=chatgpt.com "Honda City"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已消除 `21838_gen3`、`21869`、`21873` 三条 PENDING：分别闭合 Cavalier III 四门、Honda City III Type Z 和 City IV GD6 改款车身。([汽车目录][1])
* Buick Century 已按外廓变化建立两套轿车组和两套旅行车组，相关发动机 Ktype 直接复用。([汽车目录][2])
* 新增闭合 Mitsubishi Eclipse I、Renault Laguna II Grandtour、Chevrolet Spark II、Mercedes-Benz B-Class W246 尺寸组。
* `21837` 已确认车型边界，但 1991 Cavalier Convertible 的公开高度仍存在 `1321 mm` 与 `1340 mm` 冲突，继续保留 PENDING。([Edmunds][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：31
* 明确 PENDING 输入 Ktype：1
* 尚未研究 Ktype：68
* 当前待完成 Ktype：69
* READY 映射行：38
* PENDING 映射行：1
* 已确认尺寸组：26
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21837	21837	Convertible	Cavalier II	J	2		LOW	1991年3.1 RS敞篷物理边界已确认；公开规格高度存在1321 mm与1340 mm冲突。	PENDING: 敞篷高度来源冲突
21838_gen3	21838	Sedan	Cavalier III	J	4	EU-CHEVROLET-CAVALIER-III-SEDAN-01	HIGH	1995-1996年款第三代四门外廓。	READY
21845_prefl	21845	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	MEDIUM	1982-1985年款改款前外廓。	READY
21845_facelift	21845	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	MEDIUM	1986年款改款后外廓。	READY
21847	21847	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH		READY
21850	21850	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH		READY
21852	21852	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH		READY
21854	21854	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH		READY
21858	21858	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	1992-1996年款旅行车外廓。	READY
21869	21869	Sedan	City III	3A3	4	EU-HONDA-CITY-III-SEDAN-TYPE-Z-01	HIGH	2000年Type Z改款外廓。	READY
21873	21873	Sedan	City IV	GD6	4	EU-HONDA-CITY-IV-SEDAN-FACELIFT-01	HIGH	2005年改款GD6四门外廓。	READY
22257	22257	Coupe	Eclipse I		3	EU-MITSUBISHI-ECLIPSE-I-COUPE-01	MEDIUM		READY
22259	22259	Wagon	Laguna II facelift		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	MEDIUM		READY
22305	22305	Hatchback	Spark II	M200	5	EU-CHEVROLET-SPARK-II-HATCHBACK-01	HIGH		READY
22306	22306	Hatchback	Spark II	M200	5	EU-CHEVROLET-SPARK-II-HATCHBACK-01	HIGH		READY
22311_prefl	22311	Hatchback	B-Class W246	W246	5	EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-PREFL-01	HIGH	2013-2014年款改款前外廓。	READY
22311_facelift	22311	Hatchback	B-Class W246 facelift	W246	5	EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-FACELIFT-01	HIGH	2015-2018年款改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAVALIER-III-SEDAN-01	4580	1712	1392	Automobile-Catalog 1996 Chevrolet Cavalier Sedan 2.2L SFI	https://www.automobile-catalog.com/car/1996/474815/chevrolet_cavalier_sedan_2_2l_sfi.html
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364	Automobile-Catalog 1984 Buick Century Limited Sedan 2.5L	https://www.automobile-catalog.com/car/1984/314255/buick_century_limited_sedan_2_5l.html
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364	Automobile-Catalog 1988 Buick Century Limited Sedan 2.8L V6	https://www.automobile-catalog.com/car/1988/1490375/buick_century_limited_sedan_2_8l_v-6.html
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377	Automobile-Catalog 1984 Buick Century Custom Wagon 3.0L V6	https://www.automobile-catalog.com/car/1984/314570/buick_century_custom_wagon_3_0l_v-6.html
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377	Automobile-Catalog 1992 Buick Century Limited Wagon 3.3L V6	https://www.automobile-catalog.com/car/1992/320930/buick_century_limited_wagon_3_3l_v-6.html
EU-HONDA-CITY-III-SEDAN-TYPE-Z-01	4270	1690	1375	Automobile-Catalog 2000 Honda City Type-Z	https://www.automobile-catalog.com/car/2000/1271420/honda_city_type-z.html
EU-HONDA-CITY-IV-SEDAN-FACELIFT-01	4390	1690	1485	Automobile-Catalog 2006 Honda City 1.4 i-DSI LS CVT	https://www.automobile-catalog.com/car/2006/1143035/honda_city_1_4_i-dsi_ls_cvt.html
EU-MITSUBISHI-ECLIPSE-I-COUPE-01	4390	1695	1321	Auto-Data Mitsubishi Eclipse I specifications	https://www.auto-data.net/en/mitsubishi-eclipse-model-1739
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443	Auto-Data Renault Laguna II Grandtour 1.6 i 16V;AutoMoli Renault Laguna II Grandtour	https://www.auto-data.net/en/renault-laguna-ii-grandtour-1.6-i-16v-112hp-10308;https://www.automoli.com/us/vehicles/renault/laguna/laguna-ii-grandtour-2119/
EU-CHEVROLET-SPARK-II-HATCHBACK-01	3495	1495	1485	Auto-Data Chevrolet Spark II 0.8i	https://www.auto-data.net/en/chevrolet-spark-ii-0.8-i-52hp-14551
EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-PREFL-01	4359	1786	1558	Automobile-Catalog 2013 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2013/2025935/mercedes-benz_b_220_4matic.html
EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-FACELIFT-01	4393	1786	1558	Automobile-Catalog 2015 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2015/2080145/mercedes-benz_b_220_4matic.html
```

## 下一步优先处理

1. 继续优先消除 `21837` 的单一高度冲突。
2. 批量处理 Buick Electra、LeSabre、Regal 和 Roadmaster，先区分平台、代际及 Park Avenue 名称边界。
3. 随后处理 Cadillac DeVille/Fleetwood，以及可能涉及轴距、车顶或车身分支的 Express、S10、Tahoe、Wrangler、H-1 和 Hijet。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1996/474815/chevrolet_cavalier_sedan_2_2l_sfi.html?utm_source=chatgpt.com "1996 Chevrolet Cavalier Sedan 2.2L SFI Specs Review (89.5 kW / 122 PS / 120 hp) (since mid-year 1995 for North America U.S.)"
[2]: https://www.automobile-catalog.com/car/1984/314255/buick_century_limited_sedan_2_5l.html?utm_source=chatgpt.com "1984 Buick Century Limited Sedan 2.5L Specs Review (68.5 kW / 93 PS / 92 hp) (since October 1983 for North America U.S.)"
[3]: https://www.edmunds.com/chevrolet/cavalier/1991/convertible/st-12809/features-specs/?utm_source=chatgpt.com "Used 1991 Chevrolet Cavalier Convertible RS Specs & Features | Edmunds"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 已消除 `21837` 的高度冲突：1991 Chevrolet Cavalier RS Convertible 的官方车型资料与 Edmunds 均支持 `4630 × 1684 × 1321 mm`。([Dezo's Garage][1])
* Buick Electra 已按 1982–1984 后驱车身、1985–1988 前驱车身和 1989–1990 外廓调整后的前驱车身建立三个尺寸组；跨越外廓变化的 Ktype 已拆分。([汽车目录][2])
* 已闭合 Buick LeSabre VI、LeSabre VII、Chrysler Concorde I 改款前后、Maserati GranSport Coupe，以及 SsangYong Stavic/Rodius I 尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：44
* 尚待处理输入 Ktype：56
* READY 映射行：55
* 已确认尺寸组：36
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21837	21837	Convertible	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-CONVERTIBLE-01	HIGH		READY
21917_prefl	21917	Sedan	Concorde I	LH	4	EU-CHRYSLER-CONCORDE-I-SEDAN-PREFL-01	HIGH	1993-1996年款外廓。	READY
21917_facelift	21917	Sedan	Concorde I	LH	4	EU-CHRYSLER-CONCORDE-I-SEDAN-FACELIFT-01	HIGH	1997年款缩短前后保险杠外廓。	READY
21988	21988	Sedan	Electra V	C	4	EU-BUICK-ELECTRA-V-SEDAN-01	HIGH	1982-1984年款后驱全尺寸车身。	READY
21993_prefl	21993	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1987-1988年款外廓。	READY
21993_facelift	21993	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989-1990年款外廓。	READY
21995	21995	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH		READY
21996	21996	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH		READY
21997_prefl	21997	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1987-1988年款外廓。	READY
21997_facelift	21997	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989年款外廓。	READY
21998_prefl	21998	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1985-1988年款外廓。	READY
21998_facelift	21998	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989-1990年款外廓。	READY
22051	22051	Coupe	GranSport	M138	2	EU-MASERATI-GRANSPORT-I-COUPE-01	HIGH		READY
22127	22127	Sedan	LeSabre VI	H	4	EU-BUICK-LESABRE-VI-SEDAN-01	HIGH		READY
22129	22129	Sedan	LeSabre VII	H	4	EU-BUICK-LESABRE-VII-SEDAN-01	HIGH		READY
22312	22312	MPV	Rodius/Stavic I	A100	5	EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	HIGH	Stavic为Rodius的市场名称。	READY
22313	22313	MPV	Rodius/Stavic I	A100	5	EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	HIGH	Stavic为Rodius的市场名称；四驱不改变外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAVALIER-II-CONVERTIBLE-01	4630	1684	1321	Chevrolet 1991 Cavalier RS Convertible official foldout;Edmunds 1991 Chevrolet Cavalier Convertible RS specifications	https://xr793.com/wp-content/uploads/2020/02/1991-Chevrolet-Cavalier-RS-Convertible-Foldout.pdf;https://www.edmunds.com/chevrolet/cavalier/1991/convertible/st-12809/features-specs/
EU-CHRYSLER-CONCORDE-I-SEDAN-PREFL-01	5151	1890	1430	Automobile-Catalog 1996 Chrysler Concorde LX 3.3L	https://www.automobile-catalog.com/car/1996/518615/chrysler_concorde_lx_3_3l_v-6_automatic.html
EU-CHRYSLER-CONCORDE-I-SEDAN-FACELIFT-01	5118	1890	1430	Edmunds 1997 Chrysler Concorde LX specifications	https://www.edmunds.com/chrysler/concorde/1997/st-3/features-specs/
EU-BUICK-ELECTRA-V-SEDAN-01	5621	1928	1445	Automobile-Catalog 1983 Buick Electra Park Avenue Sedan 4.1L	https://www.automobile-catalog.com/car/1983/309455/buick_electra_park_avenue_sedan_4_1l_v-6.html
EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	5004	1831	1379	Automobile-Catalog 1985 Buick Electra Park Avenue Sedan 3.8L;Automobile-Catalog 1988 Buick Electra Park Avenue Sedan	https://www.automobile-catalog.com/car/1985/317225/buick_electra_park_avenue_sedan_3_8l_v-6.html;https://www.automobile-catalog.com/car/1988/317840/buick_electra_park_avenue_sedan.html
EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	5000	1840	1379	Automobile-Catalog 1989 Buick Electra Park Avenue Sedan;Automobile-Catalog 1990 Buick Electra Park Avenue Sedan	https://www.automobile-catalog.com/car/1989/318065/buick_electra_park_avenue_sedan.html;https://www.automobile-catalog.com/car/1990/318200/buick_electra_park_avenue_sedan.html
EU-MASERATI-GRANSPORT-I-COUPE-01	4523	1822	1295	Auto-Data Maserati GranSport 4.2 V8 Coupe	https://www.auto-data.net/en/maserati-gransport-4.2-i-v8-32v-400hp-10896
EU-BUICK-LESABRE-VI-SEDAN-01	4991	1831	1410	Automobile-Catalog 1987 Buick LeSabre Custom Sedan	https://www.automobile-catalog.com/car/1987/317780/buick_le_sabre_custom_sedan.html
EU-BUICK-LESABRE-VII-SEDAN-01	5080	1902	1415	Automobile-Catalog 1992 Buick LeSabre Custom;Edmunds 1992 Buick LeSabre specifications	https://www.automobile-catalog.com/car/1992/321590/buick_le_sabre_custom.html;https://www.edmunds.com/buick/lesabre/1992/features-specs/
EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	5125	1915	1820	Auto-Online SsangYong Stavic launch specifications;Automobile-Catalog 2012 SsangYong Rodius SV270	https://www.auto-online.com.tw/news/0-7716;https://www.automobile-catalog.com/car/2012/3164675/ssangyong_rodius_sv270_xdi_automatic.html
```

## 下一步优先处理

1. 处理 Cadillac DeVille 与 Fleetwood，按前驱/后驱、代际和改款边界聚类。
2. 处理 Buick Regal、Roadmaster，并重点拆分 Coupe/Sedan 与跨车型年的外廓变化。
3. 随后处理 Express、S10、Tahoe、Wrangler、H-1 和 Hijet 等可能涉及轴距、驾驶室、车顶或门数分支的车型。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2020/02/1991-Chevrolet-Cavalier-RS-Convertible-Foldout.pdf?utm_source=chatgpt.com "1991-Chevrolet-Cavalier-RS-Convertible- ..."
[2]: https://www.automobile-catalog.com/car/1983/309455/buick_electra_park_avenue_sedan_4_1l_v-6.html?utm_source=chatgpt.com "1983 Buick Electra Park Avenue Sedan 4.1L V-6 (aut. 4)"
[3]: https://www.automobile-catalog.com/car/1987/317780/buick_le_sabre_custom_sedan.html?utm_source=chatgpt.com "1987 Buick Le Sabre Custom Sedan (aut. 4)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Cadillac DeVille VII、DeVille VIII 两个轿车尺寸组，发动机功率差异不另建组；2000 与 2005 年 DeVille 的三维保持一致。([Edmunds][1])
* 已闭合 Cadillac Fleetwood 4.9 前驱轿车、Cadillac Brougham 5.7 后驱轿车及 1993–1996 Fleetwood 后驱轿车。([Edmunds][2])
* Buick Roadmaster 5.0 已锁定为 1991 Estate Wagon 外廓；1992 年改用 5.7 发动机，因此本 Ktype 不拆入 1992 尺寸组。([Edmunds][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：54
* PENDING／尚未闭合输入 Ktype：46
* READY 映射行：65
* 已确认尺寸组：42
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21969	21969	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21970	21970	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21971	21971	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21972	21972	Sedan	DeVille VIII	K	4	EU-CADILLAC-DEVILLE-VIII-SEDAN-01	HIGH		READY
21973	21973	Sedan	DeVille VIII	K	4	EU-CADILLAC-DEVILLE-VIII-SEDAN-01	HIGH		READY
22013	22013	Sedan	Fleetwood FWD	C	4	EU-CADILLAC-FLEETWOOD-FWD-SEDAN-01	MEDIUM	4.9发动机对应1991-1992年前驱四门车身；输入结束日期晚于Fleetwood前驱名称边界。	READY
22014	22014	Sedan	Brougham D-body	D	4	EU-CADILLAC-BROUGHAM-D-SEDAN-01	HIGH	输入Fleetwood名称对应1990-1992 Cadillac Brougham 5.7后驱车身。	READY
22019	22019	Sedan	Fleetwood RWD	D	4	EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	HIGH		READY
22020	22020	Sedan	Fleetwood RWD	D	4	EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	HIGH		READY
22234	22234	Wagon	Roadmaster VIII	B	5	EU-BUICK-ROADMASTER-VIII-ESTATE-WAGON-01	HIGH	5.0发动机对应1991 Estate Wagon外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CADILLAC-DEVILLE-VII-SEDAN-01	5326	1943	1433	Edmunds 1996 Cadillac DeVille specifications;Edmunds 1997 Cadillac DeVille specifications	https://www.edmunds.com/cadillac/deville/1996/features-specs/;https://www.edmunds.com/cadillac/deville/1997/features-specs/
EU-CADILLAC-DEVILLE-VIII-SEDAN-01	5263	1892	1440	Edmunds 2000 Cadillac DeVille specifications;Edmunds 2005 Cadillac DeVille specifications	https://www.edmunds.com/cadillac/deville/2000/features-specs/;https://www.edmunds.com/cadillac/deville/2005/features-specs/
EU-CADILLAC-FLEETWOOD-FWD-SEDAN-01	5222	1864	1402	Edmunds 1991 Cadillac Fleetwood Sedan specifications	https://www.edmunds.com/cadillac/fleetwood/1991/sedan/features-specs/
EU-CADILLAC-BROUGHAM-D-SEDAN-01	5613	1943	1458	Edmunds 1991 Cadillac Brougham specifications	https://www.edmunds.com/cadillac/brougham/1991/features-specs/
EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	5718	1981	1450	Edmunds 1993 Cadillac Fleetwood specifications;Edmunds 1996 Cadillac Fleetwood specifications	https://www.edmunds.com/cadillac/fleetwood/1993/st-766/features-specs/;https://www.edmunds.com/cadillac/fleetwood/1996/features-specs/
EU-BUICK-ROADMASTER-VIII-ESTATE-WAGON-01	5524	2004	1527	Edmunds 1991 Buick Roadmaster Estate Wagon specifications	https://www.edmunds.com/buick/roadmaster/1991/wagon/features-specs/
```

## 下一步优先处理

1. 批量闭合 Buick Regal 的 Coupe、Sedan 及跨年份物理分支。
2. 处理 Chrysler Concorde II、Chevrolet Lumina 与 Bentley Mulsanne/Turbo R。
3. 随后集中处理 Express、S10、Tahoe、Wrangler、H-1、Hijet 等多轴距或多车身风险车型。

推进信号：CONTINUE

[1]: https://www.edmunds.com/cadillac/deville/1996/features-specs/ "Used 1996 Cadillac DeVille Specs & Features | Edmunds"
[2]: https://www.edmunds.com/cadillac/fleetwood/1991/sedan/features-specs/?utm_source=chatgpt.com "Used 1991 Cadillac Fleetwood Sedan Specs & Features"
[3]: https://www.edmunds.com/buick/roadmaster/1991/wagon/features-specs/ "Used 1991 Buick Roadmaster Wagon Specs & Features | Edmunds"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已闭合 Chrysler Concorde II：`2.7 LX` 按 1998–2001 与 2002–2003 外廓拆分；237 hp、253 hp 的 3.5 版本对应 2002 年后的改款车身，不按输入中偏早的开始日期虚构改款前分支。([汽车目录][1])
* 已闭合 Chevrolet Lumina 两代边界；`3.4 Z34` 实际为两门 Coupe，不能按输入的 Stufenheck 直接写成四门 Sedan。([汽车目录][2])
* Bentley Continental、Mulsanne S 依据厂方技术手册闭合；Mulsanne S 因同时存在标准轴距和长轴距，拆成 SWB、LWB 两行。
* 同时闭合 Maserati GranSport Spyder、Biturbo Spyder 和 Mercedes-Benz C-Class W204 三个尺寸组。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：65
* PENDING／尚待闭合输入 Ktype：35
* READY 映射行：78
* 已确认尺寸组：52
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21919_prefl	21919	Sedan	Concorde II	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-PREFL-01	HIGH	1998-2001年款改款前外廓。	READY
21919_facelift	21919	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	HIGH	2002-2003年款改款后外廓。	READY
21920	21920	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	MEDIUM	237 hp 3.5版本对应2002年后的改款车身；输入开始日期偏早。	READY
21921	21921	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	MEDIUM	253 hp 3.5版本对应2002年后的改款车身；输入版本名称与实际配置存在偏差。	READY
21925	21925	Convertible	Continental Convertible	D	2	EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	HIGH		READY
22052	22052	Convertible	GranSport Spyder	M138	2	EU-MASERATI-GRANSPORT-SPYDER-CONVERTIBLE-01	HIGH		READY
22145	22145	Coupe	Lumina I	W	2	EU-CHEVROLET-LUMINA-I-Z34-COUPE-01	HIGH	Z34为两门Coupe，修正输入车身形式边界。	READY
22147	22147	Sedan	Lumina II	W	4	EU-CHEVROLET-LUMINA-II-SEDAN-01	HIGH		READY
22173_swb	22173	Sedan	Mulsanne S	S	4	EU-BENTLEY-MULSANNE-S-SEDAN-SWB-01	HIGH	标准轴距物理分支。	READY
22173_lwb	22173	Sedan	Mulsanne S	N	4	EU-BENTLEY-MULSANNE-S-SEDAN-LWB-01	HIGH	长轴距物理分支。	READY
22307	22307	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	MEDIUM		READY
22309	22309	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	MEDIUM		READY
22457	22457	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHRYSLER-CONCORDE-II-SEDAN-PREFL-01	5311	1890	1420	Automobile-Catalog 1998 Chrysler Concorde LX;Edmunds 1999 Chrysler Concorde LX specifications	https://www.automobile-catalog.com/car/1998/520115/chrysler_concorde_lx.html;https://www.edmunds.com/chrysler/concorde/1999/sedan/st-12673/features-specs/
EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	5276	1890	1417	Automobile-Catalog 2002 Chrysler Concorde LX;Edmunds 2003 Chrysler Concorde specifications	https://www.automobile-catalog.com/car/2002/520175/chrysler_concorde_lx.html;https://www.edmunds.com/chrysler/concorde/2003/features-specs/
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-MASERATI-GRANSPORT-SPYDER-CONVERTIBLE-01	4303	1822	1295	Automobile-Catalog 2005 Maserati GranSport Spyder Cambiocorsa	https://www.automobile-catalog.com/car/2005/1447220/maserati_gransport_spyder_cambiocorsa.html
EU-CHEVROLET-LUMINA-I-Z34-COUPE-01	5062	1821	1354	Automobile-Catalog 1991 Chevrolet Lumina Z34	https://www.automobile-catalog.com/car/1991/471200/chevrolet_lumina_z34.html
EU-CHEVROLET-LUMINA-II-SEDAN-01	5103	1842	1402	Automobile-Catalog 1996 Chevrolet Lumina Sedan 3100 V6	https://www.automobile-catalog.com/car/1996/474335/chevrolet_lumina_sedan_3100_v6_sfi_automatic.html
EU-BENTLEY-MULSANNE-S-SEDAN-SWB-01	5268	1887	1485	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-BENTLEY-MULSANNE-S-SEDAN-LWB-01	5370	1887	1485	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog 1987 Maserati Biturbo Spyder;Automobile-Catalog 1991 Maserati Biturbo Spyder range	https://www.automobile-catalog.com/car/1987/1445300/maserati_biturbo_spyder.html;https://www.automobile-catalog.com/make/maserati/biturbo/biturbo_spyder/1991.html
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 200 CDI	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-200-cdi-136hp-12540
```

## 下一步优先处理

1. 闭合 Buick Regal 的 Coupe、Sedan、跨代及跨改款分支。
2. 拆分 Bentley Turbo R 的早期高度、SWB/LWB 和 1995 年后外廓。
3. 集中处理 Express、S10、Tahoe、Wrangler、H-1、Hijet 等多轴距、多门数或多车身车型。
4. 再处理剩余 Chevrolet Corsa/Spark/Zafira、Peugeot 106、Suzuki Grand Vitara 等单车或少分支车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1998/520115/chrysler_concorde_lx.html?utm_source=chatgpt.com "1998 Chrysler Concorde LX (aut. 4) (model since mid-year ..."
[2]: https://www.automobile-catalog.com/car/1991/471200/chevrolet_lumina_z34.html?utm_source=chatgpt.com "1991 Chevrolet Lumina Z34 5-speed (man. 5)"
[3]: https://www.automobile-catalog.com/car/2006/1447685/maserati_gransport_spyder.html?utm_source=chatgpt.com "2006 Maserati Gransport Spyder (s-aut. 6) (model since mid-year ..."


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已闭合 Buick Regal III 车型簇。8 个 Ktype 按 Coupe/Sedan 以及 1988–1991、1992–1993、1994、1995–1996 外廓变化拆分，避免把不同保险杠长度和车顶高度压入同一尺寸组。([汽车目录][1])
* Bentley Turbo R 已按早期/后期车身和 SWB/LWB 拆为四个物理分支。([汽车目录][2])
* 已闭合 Chevrolet Corsa Sedan、Chevrolet Spark M150、Suzuki Grand Vitara II 三门/五门、Grand Vitara I 窄体/宽体及 Peugeot 106 I 三门/五门映射。([汽车目录][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：81
* PENDING／尚未闭合输入 Ktype：19
* READY 映射行：110
* 已确认尺寸组：70
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21927	21927	Sedan	Corsa B Sedan	GM4200	4	EU-CHEVROLET-CORSA-B-SEDAN-01	HIGH		READY
21931	21931	Sedan	Corsa B Sedan	GM4200	4	EU-CHEVROLET-CORSA-B-SEDAN-01	HIGH		READY
22218	22218	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	该动力生产期仅覆盖早期两门车身。	READY
22219_coupe	22219	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	1989-1991年款两门外廓。	READY
22219_sedan	22219	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1990-1991-01	HIGH	1990-1991年款四门外廓。	READY
22220_coupe	22220	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	1990-1991年款两门外廓。	READY
22220_sedan	22220	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1990-1991-01	HIGH	1990-1991年款四门外廓。	READY
22221_coupe	22221	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1992-1993年款两门外廓。	READY
22221_sedan	22221	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	HIGH	1992-1993年款四门外廓。	READY
22222_coupe_1994	22222	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1994年款两门外廓。	READY
22222_sedan_1994	22222	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	HIGH	1994年款四门外廓。	READY
22222_coupe_1995	22222	Coupe	Regal III facelift	W	2	EU-BUICK-REGAL-III-COUPE-1995-1996-01	HIGH	1995-1996年款两门外廓。	READY
22222_sedan_1995	22222	Sedan	Regal III facelift	W	4	EU-BUICK-REGAL-III-SEDAN-1995-1996-01	HIGH	1995-1996年款四门外廓。	READY
22223_coupe	22223	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	MEDIUM	1992-1994年款两门外廓。	READY
22223_sedan_1992	22223	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	MEDIUM	1992-1993年款四门外廓。	READY
22223_sedan_1994	22223	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	MEDIUM	1994年款四门外廓。	READY
22224_coupe	22224	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1992-1994年款两门外廓。	READY
22224_sedan_1992	22224	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	HIGH	1992-1993年款四门外廓。	READY
22224_sedan_1994	22224	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	HIGH	1994年款四门外廓。	READY
22225_coupe	22225	Coupe	Regal III facelift	W	2	EU-BUICK-REGAL-III-COUPE-1995-1996-01	MEDIUM	204 hp版本对应末期两门外廓。	READY
22225_sedan	22225	Sedan	Regal III facelift	W	4	EU-BUICK-REGAL-III-SEDAN-1995-1996-01	MEDIUM	204 hp版本对应末期四门外廓。	READY
22303	22303	Hatchback	Spark M150	M150	5	EU-CHEVROLET-SPARK-M150-HATCHBACK-01	HIGH		READY
22327	22327	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	HIGH	2.0汽油版本对应五门车身。	READY
22381_early_swb	22381	Sedan	Turbo R	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-EARLY-SWB-01	HIGH	早期标准轴距外廓。	READY
22381_early_lwb	22381	Sedan	Turbo RL	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-EARLY-LWB-01	HIGH	早期长轴距外廓。	READY
22381_late_swb	22381	Sedan	Turbo R facelift	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-LATE-SWB-01	MEDIUM	1995年后加宽标准轴距外廓。	READY
22381_late_lwb	22381	Sedan	Turbo R facelift	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-LATE-LWB-01	MEDIUM	1995年后加宽长轴距外廓。	READY
22443_3dr	22443	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-01	HIGH	三门物理分支。	READY
22443_5dr	22443	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-01	HIGH	五门物理分支；三维与三门相同。	READY
22449	22449	SUV	Grand Vitara II	JT	3	EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	HIGH	1.6汽油版本对应三门车身。	READY
22453_narrow	22453	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	MEDIUM	标准窄体三门分支。	READY
22453_widebody	22453	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	MEDIUM	SE宽体三门分支。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CORSA-B-SEDAN-01	4026	1608	1387	Automobile-Catalog 1998 Chevrolet Corsa Sedan Wind	https://www.automobile-catalog.com/car/1998/491525/chevrolet_corsa_sedan_wind.html
EU-BUICK-REGAL-III-COUPE-1988-1991-01	4882	1842	1346	Automobile-Catalog 1989 Buick Regal Gran Sport Coupe 3.1L V6	https://www.automobile-catalog.com/car/1989/318845/buick_regal_gran_sport_coupe_3_1l_v-6_automatic.html
EU-BUICK-REGAL-III-SEDAN-1990-1991-01	4943	1801	1384	Automobile-Catalog 1990 Buick Regal Limited Sedan 3.1L V6	https://www.automobile-catalog.com/car/1990/319055/buick_regal_limited_sedan_3_1l_v-6.html
EU-BUICK-REGAL-III-COUPE-1992-1994-01	4917	1842	1346	Automobile-Catalog 1994 Buick Regal Custom Coupe 3100 V6	https://www.automobile-catalog.com/car/1994/319565/buick_regal_custom_coupe_3100_v6.html
EU-BUICK-REGAL-III-SEDAN-1992-1993-01	4925	1842	1384	Automobile-Catalog 1992 Buick Regal Gran Sport Sedan	https://www.automobile-catalog.com/car/1992/319310/buick_regal_gran_sport_sedan.html
EU-BUICK-REGAL-III-SEDAN-1994-01	4948	1842	1384	Automobile-Catalog 1994 Buick Regal Custom Sedan 3100 V6	https://www.automobile-catalog.com/car/1994/319640/buick_regal_custom_sedan_3100_v6.html
EU-BUICK-REGAL-III-COUPE-1995-1996-01	4925	1842	1354	Automobile-Catalog 1995 Buick Regal Gran Sport Coupe	https://www.automobile-catalog.com/car/1995/319745/buick_regal_gran_sport_coupe.html
EU-BUICK-REGAL-III-SEDAN-1995-1996-01	4920	1842	1384	Automobile-Catalog 1995 Buick Regal Custom Sedan 3100 V6	https://www.automobile-catalog.com/car/1995/319760/buick_regal_custom_sedan_3100_v6.html
EU-CHEVROLET-SPARK-M150-HATCHBACK-01	3495	1495	1485	Auto-Data Daewoo Matiz I facelift 0.8 i	https://www.auto-data.net/en/daewoo-matiz-i-facelift-2000-0.8-i-52hp-16371
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695	Automobile-Catalog 2007 Suzuki Grand Vitara 2.7 V6 5-Door	https://www.automobile-catalog.com/car/2007/3414920/suzuki_grand_vitara_2_7_v6_5-door_4wd_automatic.html
EU-BENTLEY-TURBO-R-SEDAN-EARLY-SWB-01	5268	1887	1480	Automobile-Catalog 1986 Bentley Turbo R	https://www.automobile-catalog.com/car/1986/260315/bentley_turbo_r.html
EU-BENTLEY-TURBO-R-SEDAN-EARLY-LWB-01	5370	1887	1480	Automobile-Catalog 1990 Bentley Turbo R LWB	https://www.automobile-catalog.com/car/1990/260495/bentley_turbo_r_lwb.html
EU-BENTLEY-TURBO-R-SEDAN-LATE-SWB-01	5295	1914	1480	Automobile-Catalog 1995 Bentley Turbo R	https://www.automobile-catalog.com/car/1995/260840/bentley_turbo_r.html
EU-BENTLEY-TURBO-R-SEDAN-LATE-LWB-01	5395	1914	1480	Automobile-Catalog 1995 Bentley Turbo R LWB	https://www.automobile-catalog.com/car/1995/260855/bentley_turbo_r_lwb.html
EU-PEUGEOT-106-I-HATCHBACK-01	3564	1590	1369	Auto-Data Peugeot 106 I generation specifications	https://www.auto-data.net/en/peugeot-106-i-1a-c-generation-1244
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695	Auto-Data Suzuki Grand Vitara II 3 Door 1.6	https://www.auto-data.net/en/suzuki-grand-vitara-ii-3-door-1.6-i-16v-107hp-16578
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	3905	1695	1685	Automobile-Catalog 2004 Suzuki Grand Vitara 1.6 16V Estate 4WD	https://www.automobile-catalog.com/car/2004/3352925/suzuki_grand_vitara_1_6_16v_estate_4wd.html
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	3905	1780	1740	Automobile-Catalog 2004 Suzuki Grand Vitara 1.6 16V SE Estate 4WD	https://www.automobile-catalog.com/car/2004/3352940/suzuki_grand_vitara_1_6_16v_se_estate_4wd.html
```

## 下一步优先处理

1. 优先闭合 Chevrolet Express、S10、Tahoe、Jeep Wrangler、GMC S15 Jimmy 的轴距、门数和车身分支。
2. 处理 Hyundai H-1、Daihatsu Hijet 等底盘驾驶室车型。
3. 最后处理 AMC Eagle、Cadillac Fleetwood Diesel、Buick Electra 末期、Chrysler Sebring、Chevrolet Spark/Zafira 等剩余车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1989/318845/buick_regal_gran_sport_coupe_3_1l_v-6_automatic.html?utm_source=chatgpt.com "1989 Buick Regal Gran Sport Coupe 3.1L V-6 automatic ..."
[2]: https://www.automobile-catalog.com/car/1986/260315/bentley_turbo_r.html?utm_source=chatgpt.com "1986 Bentley Turbo R Specs Review (223.5 kW / 304 PS / 300 hp) (for Europe )"
[3]: https://www.automobile-catalog.com/car/1998/491525/chevrolet_corsa_sedan_wind.html?utm_source=chatgpt.com "1998 Chevrolet Corsa Sedan Wind Specs Review (44 kW / 60 PS / 59 hp) (since mid-year 1998 for South America )"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已闭合 AMC Eagle 4 门 Sedan。该 Ktype 跨越 1980、1981、1982、1983 和 1984–1985 五套不同外廓，按车型年拆为五个稳定物理分支，未将年度保险杠及车身高度变化混入同一尺寸组。([汽车目录][1])
* 已闭合 Buick `21999`。输入中的 Electra 名称实际对应 1991 Buick Park Avenue 独立车型，尺寸为 `5215 × 1869 × 1400 mm`。([汽车目录][2])
* 已闭合 Cadillac Fleetwood 5.7 Diesel，并按 1980 年宽车身与 1981–1985 年窄化车身拆分；同时闭合 Chrysler Sebring I Coupe。([汽车目录][3])
* 已闭合 Chevrolet Zafira A，并按 2001–2004 早期外廓与 2005–2012 后期外廓拆分。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：86
* 待处理输入 Ktype：14
* READY 映射行：121
* 已确认尺寸组：81
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21981_1980	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1980-01	HIGH	1980年款物理外廓。	READY
21981_1981	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1981-01	HIGH	1981年款物理外廓。	READY
21981_1982	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1982-01	HIGH	1982年款物理外廓。	READY
21981_1983	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1983-01	HIGH	1983年款物理外廓。	READY
21981_1984	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1984-1985-01	HIGH	1984-1985年款物理外廓。	READY
21999	21999	Sedan	Park Avenue I	C	4	EU-BUICK-PARK-AVENUE-I-SEDAN-01	HIGH	输入Electra名称对应1991年独立Park Avenue车型。	READY
22017_1980	22017	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1980-01	HIGH	1980年款宽车身外廓。	READY
22017_1981	22017	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1981-1985-01	HIGH	1981-1985年款窄化车身外廓。	READY
22285	22285	Coupe	Sebring I	FJ	2	EU-CHRYSLER-SEBRING-I-COUPE-01	HIGH		READY
22433_prefl	22433	MPV	Zafira A	F75	5	EU-CHEVROLET-ZAFIRA-A-MPV-PREFL-01	HIGH	2001-2004年早期外廓。	READY
22433_facelift	22433	MPV	Zafira A facelift	F75	5	EU-CHEVROLET-ZAFIRA-A-MPV-FACELIFT-01	HIGH	2005-2012年后期外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AMC-EAGLE-I-SEDAN-1980-01	4729	1826	1407	Automobile-Catalog 1980 AMC Eagle 4-Door Sedan 258ci	https://www.automobile-catalog.com/car/1980/46430/amc_eagle_4-door_sedan_258ci.html
EU-AMC-EAGLE-I-SEDAN-1981-01	4674	1826	1407	Automobile-Catalog 1981 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1981/1877225/amc_eagle_4-door_sedan_4_2l_automatic.html
EU-AMC-EAGLE-I-SEDAN-1982-01	4732	1836	1407	Automobile-Catalog 1982 AMC Eagle Limited 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1982/1879970/amc_eagle_limited_4-door_sedan_4_2l.html
EU-AMC-EAGLE-I-SEDAN-1983-01	4653	1836	1407	Automobile-Catalog 1983 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1983/1883075/amc_eagle_4-door_sedan_4_2l.html
EU-AMC-EAGLE-I-SEDAN-1984-1985-01	4595	1836	1382	Automobile-Catalog 1984 AMC Eagle 4-Door Sedan 4.2L;Automobile-Catalog 1985 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1984/1883330/amc_eagle_4-door_sedan_4_2l.html;https://www.automobile-catalog.com/car/1985/1883570/amc_eagle_4-door_sedan_4_2l_automatic.html
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400	Automobile-Catalog 1991 Buick Park Avenue	https://www.automobile-catalog.com/car/1991/321515/buick_park_avenue.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1980-01	5613	1941	1440	Automobile-Catalog 1980 Cadillac Fleetwood Brougham 5.7L Diesel	https://www.automobile-catalog.com/car/1980/187010/cadillac_fleetwood_brougham_5_7l_v-8_diesel.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1981-1985-01	5613	1913	1440	Automobile-Catalog 1981 Cadillac Fleetwood Brougham Sedan 5.7L Diesel;Automobile-Catalog 1985 Cadillac Fleetwood Brougham Sedan 5.7L Diesel	https://www.automobile-catalog.com/car/1981/330890/cadillac_fleetwood_brougham_sedan_5_7l_v-8_diesel.html;https://www.automobile-catalog.com/car/1985/331895/cadillac_fleetwood_brougham_sedan_5_7l_v-8_diesel.html
EU-CHRYSLER-SEBRING-I-COUPE-01	4760	1770	1296	Auto-Data Chrysler Sebring Coupe FJ 2.5 V6	https://www.auto-data.net/en/chrysler-sebring-coupe-fj-2.5-v6-166hp-14821
EU-CHEVROLET-ZAFIRA-A-MPV-PREFL-01	4317	1742	1629	Automobile-Catalog 2001 Chevrolet Zafira 2.0 16V	https://www.automobile-catalog.com/car/2001/492035/chevrolet_zafira_2_0_16v.html
EU-CHEVROLET-ZAFIRA-A-MPV-FACELIFT-01	4334	1742	1687	Automobile-Catalog 2005 Chevrolet Zafira Elegance 2.0 Flexpower;Automobile-Catalog 2012 Chevrolet Zafira Elegance 2.0 Flexpower	https://www.automobile-catalog.com/car/2005/492545/chevrolet_zafira_elegance_2_0_flexpower_gasolina.html;https://www.automobile-catalog.com/car/2012/1208105/chevrolet_zafira_elegance_2_0_flexpower_gasolina.html
```

## 下一步优先处理

1. 闭合 Jeep Wrangler III 的三门、五门及 Rubicon 特殊悬架高度分支。
2. 闭合 GMC S15 Jimmy 的三门、五门、后驱和四驱外廓。
3. 集中处理 Chevrolet Express、S10 Pickup、Tahoe，以及 Hyundai H-1、Daihatsu Hijet 底盘驾驶室车型。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1980/46430/amc_eagle_4-door_sedan_258ci.html?utm_source=chatgpt.com "1980 AMC Eagle 4-Door Sedan Specs Review (82 kW / 112 PS / 110 hp) (since September 1979 for North America U.S.)"
[2]: https://www.automobile-catalog.com/car/1991/321515/buick_park_avenue.html?utm_source=chatgpt.com "1991 Buick Park Avenue Specs Review (127 kW / 173 PS / ..."
[3]: https://www.automobile-catalog.com/car/1980/187010/cadillac_fleetwood_brougham_5_7l_v-8_diesel.html?utm_source=chatgpt.com "1980 Cadillac Fleetwood Brougham 5.7L V-8 Diesel (aut. 3)"
[4]: https://www.automobile-catalog.com/car/2001/492035/chevrolet_zafira_2_0_16v.html?utm_source=chatgpt.com "2001 Chevrolet Zafira 2.0 16V Specs Review (100 kW / 136 PS / 134 hp) (since April 2001 for South America )"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 已闭合 Chevrolet Express GMT600 的 1500 短轴、2500 短轴和 2500 长轴货运车外廓；侧门数量不改变三维，3 门和 4 门映射复用对应尺寸组。([Edmunds][1])
* 已闭合 Jeep Wrangler JK/JKU 的两门、四门以及 X、Sahara、Rubicon 标准外廓；后驱 Ktype 仅关联四门 X、Sahara 分支。([Edmunds][2])
* 已闭合 GMC S-15 Jimmy 的两门/四门及后驱/四驱分支。([AutoDetective][3])
* 已闭合 Chevrolet Tahoe 5.7 四驱的两门、四门分支；6.5 柴油四驱确认仅关联两门外廓。`22346` 的后驱柴油输入边界仍未闭合，本轮不强行关联。([汽车目录][4])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：93
* PENDING／待闭合输入 Ktype：7
* READY 映射行：142
* 已确认尺寸组：96
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22010_swb_1500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	MEDIUM	1500短轴三门货运车分支。	READY
22010_swb_1500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	MEDIUM	1500短轴四门货运车分支。	READY
22010_swb_2500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	MEDIUM	2500短轴三门货运车分支。	READY
22010_swb_2500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	MEDIUM	2500短轴四门货运车分支。	READY
22010_lwb_2500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	MEDIUM	2500长轴三门货运车分支。	READY
22010_lwb_2500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	MEDIUM	2500长轴四门货运车分支。	READY
22024_2dr_x	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-X-01	MEDIUM	两门X标准外廓。	READY
22024_2dr_sahara	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-SAHARA-01	MEDIUM	两门Sahara标准外廓。	READY
22024_2dr_rubicon	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-RUBICON-01	MEDIUM	两门Rubicon外廓。	READY
22024_4dr_x	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	MEDIUM	四门Unlimited X标准外廓。	READY
22024_4dr_sahara	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	MEDIUM	四门Unlimited Sahara标准外廓。	READY
22024_4dr_rubicon	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-RUBICON-01	MEDIUM	四门Unlimited Rubicon外廓。	READY
22026_4dr_x	22026	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	MEDIUM	后驱Unlimited X分支。	READY
22026_4dr_sahara	22026	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	MEDIUM	后驱Unlimited Sahara分支。	READY
22094_2dr	22094	SUV	S-15 Jimmy I		3	EU-GMC-S15-JIMMY-I-SUV-2D-RWD-01	HIGH	两门后驱外廓。	READY
22094_4dr	22094	SUV	S-15 Jimmy I		5	EU-GMC-S15-JIMMY-I-SUV-4D-RWD-01	HIGH	四门后驱外廓。	READY
22095_2dr	22095	SUV	S-15 Jimmy I		3	EU-GMC-S15-JIMMY-I-SUV-2D-4WD-01	HIGH	两门四驱外廓。	READY
22095_4dr	22095	SUV	S-15 Jimmy I		5	EU-GMC-S15-JIMMY-I-SUV-4D-4WD-01	HIGH	四门四驱外廓。	READY
22345_2dr	22345	SUV	Tahoe I		3	EU-CHEVROLET-TAHOE-I-SUV-2D-01	HIGH	两门四驱外廓。	READY
22345_4dr	22345	SUV	Tahoe I		5	EU-CHEVROLET-TAHOE-I-SUV-4D-01	HIGH	四门四驱外廓。	READY
22347	22347	SUV	Tahoe I		3	EU-CHEVROLET-TAHOE-I-SUV-2D-01	HIGH	6.5涡轮柴油四驱两门外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	5558	2012	2068	Edmunds 1996 Chevrolet Express G1500 specifications	https://www.edmunds.com/chevrolet/express/1996/st-13251/features-specs/
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	5558	2012	2062	Edmunds 1996 Chevrolet Express G2500 specifications	https://www.edmunds.com/chevrolet/express/1996/st-13257/features-specs/
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	6066	2012	2108	Edmunds 1996 Chevrolet Chevy Van G2500 Extended specifications	https://www.edmunds.com/chevrolet/chevy-van/1996/st-13255/features-specs/
EU-JEEP-WRANGLER-JK-SUV-2D-X-01	4138	1872	1801	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/features-specs/
EU-JEEP-WRANGLER-JK-SUV-2D-SAHARA-01	4153	1872	1834	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-JEEP-WRANGLER-JK-SUV-2D-RUBICON-01	4161	1872	1839	Kelley Blue Book 2007 Jeep Wrangler specifications;Jeep 2007 Wrangler full specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.jeepfan.com/tech/07Wrangler/full-specifications.pdf
EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	4684	1877	1831	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	4648	1877	1798	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler Unlimited Sahara specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/suv/st-100782108/features-specs/
EU-JEEP-WRANGLER-JKU-SUV-4D-RUBICON-01	4684	1877	1836	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-GMC-S15-JIMMY-I-SUV-2D-RWD-01	4326	1661	1628	AutoDetective 1989 GMC S15 Jimmy specifications	https://www.autodetective.com/directory/1989/gmc/s15-jimmy/
EU-GMC-S15-JIMMY-I-SUV-4D-RWD-01	4491	1661	1595	Edmunds 1991 GMC S-15 Jimmy SLE specifications	https://www.edmunds.com/gmc/s-15-jimmy/1991/st-4422/features-specs/
EU-GMC-S15-JIMMY-I-SUV-2D-4WD-01	4326	1661	1633	Edmunds 1994 GMC Jimmy specifications	https://www.edmunds.com/gmc/jimmy/1994/features-specs/
EU-GMC-S15-JIMMY-I-SUV-4D-4WD-01	4491	1661	1633	AutoDetective 1991 GMC S15 Jimmy 4-Door 4WD specifications	https://www.autodetective.com/directory/1991/gmc/s15-jimmy/trim/4-door-4wd/
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839	Automobile-Catalog 1995 Chevrolet Tahoe K1500 2-Door 5.7L	https://www.automobile-catalog.com/car/1995/483965/chevrolet_tahoe_k1500_2-door_5_7l_v-8_efi_automatic.html
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783	Automobile-Catalog 1995 Chevrolet Tahoe K1500 4-Door 5.7L	https://www.automobile-catalog.com/car/1995/484025/chevrolet_tahoe_k1500_4-door_5_7l_v-8_efi_automatic.html
```

## 下一步优先处理

1. 解决 `22346` 的 Tahoe 6.5 柴油后驱输入与量产资料冲突。
2. 按驾驶室、货斗及驱动形式闭合第一代和第二代 Chevrolet S10：`22243`、`22245`、`22246`、`22247`。
3. 最后闭合 Hyundai H-1 底盘驾驶室 `22054` 与 Daihatsu Hijet 底盘驾驶室 `22061`。

推进信号：CONTINUE

[1]: https://www.edmunds.com/chevrolet/express/1996/st-13257/features-specs/?utm_source=chatgpt.com "Used 1996 Chevrolet Express G2500 Specs & Features | Edmunds"
[2]: https://www.edmunds.com/jeep/wrangler/2007/trims/?utm_source=chatgpt.com "2007 Jeep Wrangler Trims Comparison [+ Chart]"
[3]: https://www.autodetective.com/directory/1989/gmc/s15-jimmy/?utm_source=chatgpt.com "1989 GMC S15 Jimmy VINs, Configurations, MSRP & Specs"
[4]: https://www.automobile-catalog.com/car/1995/484025/chevrolet_tahoe_k1500_4-door_5_7l_v-8_efi_automatic.html?utm_source=chatgpt.com "1995 Chevrolet Tahoe K1500 4-Door 5.7L V-8 EFi automatic Specs Review (149 kW / 203 PS / 200 hp) (since mid-year 1994 for North America U.S.)"


--- 发送 / 继续到 Round 9 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1201-1300_ktype_dimension_mapping_final.tsv
- all_1201-1300_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 9 / 下一步 ---
## 更新点

* 剩余 7 个 Ktype 已全部闭合。Chevrolet S10 按代际、驱动、驾驶室及货斗长度拆分；第二代加长驾驶室的两门与可选第三门复用相同尺寸组。([通用汽车][1])
* Hyundai H-1 长轴底盘车、Daihatsu Hijet 标准及加长加宽底盘车已完成建组；`22346` 已按量产事实关联 Tahoe 两门四驱尺寸组，并在 Notes 保留输入后驱字段冲突。([汽车目录][2])
* 已完成机械检查：表头正确、`id` 与 `DIMENSION_GROUP_ID` 唯一、100 个输入 Ktype 全覆盖、所有映射 READY、引用完全闭合、尺寸及来源无空值。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING：0
* READY 映射行：161
* DIMENSION_GROUP：108
* 孤立尺寸组：0
* 未闭合映射引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
21827	21827	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH		READY
21828	21828	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH		READY
21829_prefl	21829	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	HIGH	1994年款改款前外廓。	READY
21829_facelift	21829	Sedan	Caprice IV	B	4	EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	HIGH	1995-1996年款改款后外廓。	READY
21830	21830	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21831	21831	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21832	21832	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21833	21833	Wagon	Caprice IV	B	5	EU-CHEVROLET-CAPRICE-IV-WAGON-01	HIGH		READY
21834_prefl	21834	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-PREFL-01	HIGH	1990年款改款前外廓。	READY
21834_facelift	21834	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	HIGH	1991年款改款后外廓。	READY
21836_prefl	21836	Coupe	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-COUPE-PREFL-01	HIGH	1990年款改款前外廓。	READY
21836_facelift	21836	Coupe	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-COUPE-FACELIFT-01	HIGH	1991-1994年款改款后外廓。	READY
21837	21837	Convertible	Cavalier II	J	2	EU-CHEVROLET-CAVALIER-II-CONVERTIBLE-01	HIGH		READY
21838_gen2	21838	Sedan	Cavalier II	J	4	EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	HIGH	1992-1994年款第二代改款后外廓。	READY
21838_gen3	21838	Sedan	Cavalier III	J	4	EU-CHEVROLET-CAVALIER-III-SEDAN-01	HIGH	1995-1996年款第三代四门外廓。	READY
21845_prefl	21845	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	MEDIUM	1982-1985年款改款前外廓。	READY
21845_facelift	21845	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	MEDIUM	1986年款改款后外廓。	READY
21847	21847	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH		READY
21850	21850	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH		READY
21852	21852	Sedan	Century IV	A	4	EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	HIGH		READY
21854	21854	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-PREFL-01	HIGH		READY
21858	21858	Wagon	Century IV	A	5	EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	HIGH	1992-1996年款旅行车外廓。	READY
21861	21861	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.0版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21862	21862	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.0版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21864	21864	Sedan	Cirrus I	JA	4	EU-CHRYSLER-CIRRUS-I-SEDAN-01	MEDIUM	欧洲2.5版本按JA平台四门外廓归并；输入名Cirrus与欧洲Stratus命名交叉。	READY
21867	21867	Sedan	City III	3A3	4	EU-HONDA-CITY-III-SEDAN-PREFL-01	HIGH		READY
21869	21869	Sedan	City III	3A3	4	EU-HONDA-CITY-III-SEDAN-TYPE-Z-01	HIGH	2000年Type Z改款外廓。	READY
21873	21873	Sedan	City IV	GD6	4	EU-HONDA-CITY-IV-SEDAN-FACELIFT-01	HIGH	2005年改款GD6四门外廓。	READY
21896	21896	Sedan	Lada 110	VAZ-2110	4	EU-LADA-110-SEDAN-01	HIGH		READY
21897	21897	Wagon	Leon III	5F8	5	EU-SEAT-LEON-III-ST-WAGON-01	MEDIUM		READY
21917_prefl	21917	Sedan	Concorde I	LH	4	EU-CHRYSLER-CONCORDE-I-SEDAN-PREFL-01	HIGH	1993-1996年款外廓。	READY
21917_facelift	21917	Sedan	Concorde I	LH	4	EU-CHRYSLER-CONCORDE-I-SEDAN-FACELIFT-01	HIGH	1997年款缩短前后保险杠外廓。	READY
21919_prefl	21919	Sedan	Concorde II	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-PREFL-01	HIGH	1998-2001年款改款前外廓。	READY
21919_facelift	21919	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	HIGH	2002-2003年款改款后外廓。	READY
21920	21920	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	MEDIUM	237 hp 3.5版本对应2002年后的改款车身；输入开始日期偏早。	READY
21921	21921	Sedan	Concorde II facelift	LH	4	EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	MEDIUM	253 hp 3.5版本对应2002年后的改款车身；输入版本名称与实际配置存在偏差。	READY
21925	21925	Convertible	Continental Convertible	D	2	EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	HIGH		READY
21927	21927	Sedan	Corsa B Sedan	GM4200	4	EU-CHEVROLET-CORSA-B-SEDAN-01	HIGH		READY
21931	21931	Sedan	Corsa B Sedan	GM4200	4	EU-CHEVROLET-CORSA-B-SEDAN-01	HIGH		READY
21969	21969	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21970	21970	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21971	21971	Sedan	DeVille VII	K	4	EU-CADILLAC-DEVILLE-VII-SEDAN-01	HIGH		READY
21972	21972	Sedan	DeVille VIII	K	4	EU-CADILLAC-DEVILLE-VIII-SEDAN-01	HIGH		READY
21973	21973	Sedan	DeVille VIII	K	4	EU-CADILLAC-DEVILLE-VIII-SEDAN-01	HIGH		READY
21981_1980	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1980-01	HIGH	1980年款物理外廓。	READY
21981_1981	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1981-01	HIGH	1981年款物理外廓。	READY
21981_1982	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1982-01	HIGH	1982年款物理外廓。	READY
21981_1983	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1983-01	HIGH	1983年款物理外廓。	READY
21981_1984	21981	Sedan	Eagle I		4	EU-AMC-EAGLE-I-SEDAN-1984-1985-01	HIGH	1984-1985年款物理外廓。	READY
21988	21988	Sedan	Electra V	C	4	EU-BUICK-ELECTRA-V-SEDAN-01	HIGH	1982-1984年款后驱全尺寸车身。	READY
21990	21990	Sedan	GS IV	GRL11	4	EU-LEXUS-GS-IV-SEDAN-01	HIGH		READY
21993_prefl	21993	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1987-1988年款外廓。	READY
21993_facelift	21993	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989-1990年款外廓。	READY
21995	21995	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH		READY
21996	21996	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH		READY
21997_prefl	21997	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1987-1988年款外廓。	READY
21997_facelift	21997	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989年款外廓。	READY
21998_prefl	21998	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	HIGH	1985-1988年款外廓。	READY
21998_facelift	21998	Sedan	Electra VI	C	4	EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	HIGH	1989-1990年款外廓。	READY
21999	21999	Sedan	Park Avenue I	C	4	EU-BUICK-PARK-AVENUE-I-SEDAN-01	HIGH	输入Electra名称对应1991年独立Park Avenue车型。	READY
22005_prefl	22005	SUV	Element I	YH2	5	EU-HONDA-ELEMENT-I-SUV-PREFL-01	MEDIUM	2003-2008年款改款前外廓。	READY
22005_facelift	22005	SUV	Element I	YH2	5	EU-HONDA-ELEMENT-I-SUV-FACELIFT-01	MEDIUM	2009-2011年款改款后外廓。	READY
22010_swb_1500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	MEDIUM	1500短轴三门货运车分支。	READY
22010_swb_1500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	MEDIUM	1500短轴四门货运车分支。	READY
22010_swb_2500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	MEDIUM	2500短轴三门货运车分支。	READY
22010_swb_2500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	MEDIUM	2500短轴四门货运车分支。	READY
22010_lwb_2500_3dr	22010	Van	Express I	GMT600	3	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	MEDIUM	2500长轴三门货运车分支。	READY
22010_lwb_2500_4dr	22010	Van	Express I	GMT600	4	EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	MEDIUM	2500长轴四门货运车分支。	READY
22013	22013	Sedan	Fleetwood FWD	C	4	EU-CADILLAC-FLEETWOOD-FWD-SEDAN-01	MEDIUM	4.9发动机对应1991-1992年前驱四门车身；输入结束日期晚于Fleetwood前驱名称边界。	READY
22014	22014	Sedan	Brougham D-body	D	4	EU-CADILLAC-BROUGHAM-D-SEDAN-01	HIGH	输入Fleetwood名称对应1990-1992 Cadillac Brougham 5.7后驱车身。	READY
22017_1980	22017	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1980-01	HIGH	1980年款宽车身外廓。	READY
22017_1981	22017	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1981-1985-01	HIGH	1981-1985年款窄化车身外廓。	READY
22019	22019	Sedan	Fleetwood RWD	D	4	EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	HIGH		READY
22020	22020	Sedan	Fleetwood RWD	D	4	EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	HIGH		READY
22024_2dr_x	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-X-01	MEDIUM	两门X标准外廓。	READY
22024_2dr_sahara	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-SAHARA-01	MEDIUM	两门Sahara标准外廓。	READY
22024_2dr_rubicon	22024	SUV	Wrangler III	JK	3	EU-JEEP-WRANGLER-JK-SUV-2D-RUBICON-01	MEDIUM	两门Rubicon外廓。	READY
22024_4dr_x	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	MEDIUM	四门Unlimited X标准外廓。	READY
22024_4dr_sahara	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	MEDIUM	四门Unlimited Sahara标准外廓。	READY
22024_4dr_rubicon	22024	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-RUBICON-01	MEDIUM	四门Unlimited Rubicon外廓。	READY
22026_4dr_x	22026	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	MEDIUM	后驱Unlimited X分支。	READY
22026_4dr_sahara	22026	SUV	Wrangler III Unlimited	JKU	5	EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	MEDIUM	后驱Unlimited Sahara分支。	READY
22051	22051	Coupe	GranSport	M138	2	EU-MASERATI-GRANSPORT-I-COUPE-01	HIGH		READY
22052	22052	Convertible	GranSport Spyder	M138	2	EU-MASERATI-GRANSPORT-SPYDER-CONVERTIBLE-01	HIGH		READY
22054	22054	Pickup	H-1 Truck	SR	2	EU-HYUNDAI-H1-TRUCK-SR-PICKUP-LONG-01	MEDIUM	长轴底盘驾驶室/平板车外廓。	READY
22061_standard	22061	Pickup	Hijet S85	S85P	2	EU-DAIHATSU-HIJET-S85-PICKUP-STANDARD-01	HIGH	标准窄体平板车分支。	READY
22061_longwide	22061	Pickup	Hijet S85	S85P	2	EU-DAIHATSU-HIJET-S85-PICKUP-LONG-WIDE-01	HIGH	加长加宽平板车分支。	READY
22094_2dr	22094	SUV	S-15 Jimmy I		3	EU-GMC-S15-JIMMY-I-SUV-2D-RWD-01	HIGH	两门后驱外廓。	READY
22094_4dr	22094	SUV	S-15 Jimmy I		5	EU-GMC-S15-JIMMY-I-SUV-4D-RWD-01	HIGH	四门后驱外廓。	READY
22095_2dr	22095	SUV	S-15 Jimmy I		3	EU-GMC-S15-JIMMY-I-SUV-2D-4WD-01	HIGH	两门四驱外廓。	READY
22095_4dr	22095	SUV	S-15 Jimmy I		5	EU-GMC-S15-JIMMY-I-SUV-4D-4WD-01	HIGH	四门四驱外廓。	READY
22127	22127	Sedan	LeSabre VI	H	4	EU-BUICK-LESABRE-VI-SEDAN-01	HIGH		READY
22129	22129	Sedan	LeSabre VII	H	4	EU-BUICK-LESABRE-VII-SEDAN-01	HIGH		READY
22145	22145	Coupe	Lumina I	W	2	EU-CHEVROLET-LUMINA-I-Z34-COUPE-01	HIGH	Z34为两门Coupe，修正输入车身形式边界。	READY
22147	22147	Sedan	Lumina II	W	4	EU-CHEVROLET-LUMINA-II-SEDAN-01	HIGH		READY
22173_swb	22173	Sedan	Mulsanne S	S	4	EU-BENTLEY-MULSANNE-S-SEDAN-SWB-01	HIGH	标准轴距物理分支。	READY
22173_lwb	22173	Sedan	Mulsanne S	N	4	EU-BENTLEY-MULSANNE-S-SEDAN-LWB-01	HIGH	长轴距物理分支。	READY
22218	22218	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	该动力生产期仅覆盖早期两门车身。	READY
22219_coupe	22219	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	1989-1991年款两门外廓。	READY
22219_sedan	22219	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1990-1991-01	HIGH	1990-1991年款四门外廓。	READY
22220_coupe	22220	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1988-1991-01	HIGH	1990-1991年款两门外廓。	READY
22220_sedan	22220	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1990-1991-01	HIGH	1990-1991年款四门外廓。	READY
22221_coupe	22221	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1992-1993年款两门外廓。	READY
22221_sedan	22221	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	HIGH	1992-1993年款四门外廓。	READY
22222_coupe_1994	22222	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1994年款两门外廓。	READY
22222_sedan_1994	22222	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	HIGH	1994年款四门外廓。	READY
22222_coupe_1995	22222	Coupe	Regal III facelift	W	2	EU-BUICK-REGAL-III-COUPE-1995-1996-01	HIGH	1995-1996年款两门外廓。	READY
22222_sedan_1995	22222	Sedan	Regal III facelift	W	4	EU-BUICK-REGAL-III-SEDAN-1995-1996-01	HIGH	1995-1996年款四门外廓。	READY
22223_coupe	22223	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	MEDIUM	1992-1994年款两门外廓。	READY
22223_sedan_1992	22223	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	MEDIUM	1992-1993年款四门外廓。	READY
22223_sedan_1994	22223	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	MEDIUM	1994年款四门外廓。	READY
22224_coupe	22224	Coupe	Regal III	W	2	EU-BUICK-REGAL-III-COUPE-1992-1994-01	HIGH	1992-1994年款两门外廓。	READY
22224_sedan_1992	22224	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1992-1993-01	HIGH	1992-1993年款四门外廓。	READY
22224_sedan_1994	22224	Sedan	Regal III	W	4	EU-BUICK-REGAL-III-SEDAN-1994-01	HIGH	1994年款四门外廓。	READY
22225_coupe	22225	Coupe	Regal III facelift	W	2	EU-BUICK-REGAL-III-COUPE-1995-1996-01	MEDIUM	204 hp版本对应末期两门外廓。	READY
22225_sedan	22225	Sedan	Regal III facelift	W	4	EU-BUICK-REGAL-III-SEDAN-1995-1996-01	MEDIUM	204 hp版本对应末期四门外廓。	READY
22234	22234	Wagon	Roadmaster VIII	B	5	EU-BUICK-ROADMASTER-VIII-ESTATE-WAGON-01	HIGH	5.0发动机对应1991 Estate Wagon外廓。	READY
22243_regcab_short	22243	Pickup	S10 I		2	EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-SHORT-01	HIGH	四驱单排短货斗分支。	READY
22243_regcab_long	22243	Pickup	S10 I		2	EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-LONG-01	HIGH	四驱单排长货斗分支。	READY
22243_extcab_short	22243	Pickup	S10 I		2	EU-CHEVROLET-S10-I-PICKUP-4WD-EXTCAB-SHORT-01	HIGH	四驱加长驾驶室短货斗分支。	READY
22245_regcab_short	22245	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	HIGH	后驱单排短货斗分支。	READY
22245_regcab_long	22245	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	HIGH	后驱单排长货斗分支。	READY
22245_extcab_short_2dr	22245	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	HIGH	后驱加长驾驶室短货斗两门分支。	READY
22245_extcab_short_3dr	22245	Pickup	S10 II		3	EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	HIGH	1996年后可选第三门；三维不变。	READY
22246_regcab_short	22246	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	MEDIUM	四驱单排短货斗分支。	READY
22246_regcab_long	22246	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	MEDIUM	四驱单排长货斗分支。	READY
22246_extcab_short_2dr	22246	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	MEDIUM	四驱加长驾驶室短货斗两门分支。	READY
22246_extcab_short_3dr	22246	Pickup	S10 II		3	EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	MEDIUM	1996年后可选第三门；三维不变。	READY
22247_regcab_short	22247	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	HIGH	四驱单排短货斗分支。	READY
22247_regcab_long	22247	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	HIGH	四驱单排长货斗分支。	READY
22247_extcab_short_2dr	22247	Pickup	S10 II		2	EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	HIGH	四驱加长驾驶室短货斗两门分支。	READY
22247_extcab_short_3dr	22247	Pickup	S10 II		3	EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	HIGH	1996年后可选第三门；三维不变。	READY
22257	22257	Coupe	Eclipse I		3	EU-MITSUBISHI-ECLIPSE-I-COUPE-01	MEDIUM		READY
22259	22259	Wagon	Laguna II facelift		5	EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	MEDIUM		READY
22285	22285	Coupe	Sebring I	FJ	2	EU-CHRYSLER-SEBRING-I-COUPE-01	HIGH		READY
22303	22303	Hatchback	Spark M150	M150	5	EU-CHEVROLET-SPARK-M150-HATCHBACK-01	HIGH		READY
22305	22305	Hatchback	Spark II	M200	5	EU-CHEVROLET-SPARK-II-HATCHBACK-01	HIGH		READY
22306	22306	Hatchback	Spark II	M200	5	EU-CHEVROLET-SPARK-II-HATCHBACK-01	HIGH		READY
22307	22307	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	MEDIUM		READY
22309	22309	Convertible	Biturbo Spyder		2	EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	MEDIUM		READY
22311_prefl	22311	Hatchback	B-Class W246	W246	5	EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-PREFL-01	HIGH	2013-2014年款改款前外廓。	READY
22311_facelift	22311	Hatchback	B-Class W246 facelift	W246	5	EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-FACELIFT-01	HIGH	2015-2018年款改款后外廓。	READY
22312	22312	MPV	Rodius/Stavic I	A100	5	EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	HIGH	Stavic为Rodius的市场名称。	READY
22313	22313	MPV	Rodius/Stavic I	A100	5	EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	HIGH	Stavic为Rodius的市场名称；四驱不改变外廓。	READY
22327	22327	SUV	Grand Vitara II	JT	5	EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	HIGH	2.0汽油版本对应五门车身。	READY
22345_2dr	22345	SUV	Tahoe I		3	EU-CHEVROLET-TAHOE-I-SUV-2D-01	HIGH	两门四驱外廓。	READY
22345_4dr	22345	SUV	Tahoe I		5	EU-CHEVROLET-TAHOE-I-SUV-4D-01	HIGH	四门四驱外廓。	READY
22346	22346	SUV	Tahoe I		3	EU-CHEVROLET-TAHOE-I-SUV-2D-01	MEDIUM	输入后驱字段与量产配置冲突；6.5涡轮柴油仅对应两门四驱外廓。	READY
22347	22347	SUV	Tahoe I		3	EU-CHEVROLET-TAHOE-I-SUV-2D-01	HIGH	6.5涡轮柴油四驱两门外廓。	READY
22381_early_swb	22381	Sedan	Turbo R	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-EARLY-SWB-01	HIGH	早期标准轴距外廓。	READY
22381_early_lwb	22381	Sedan	Turbo RL	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-EARLY-LWB-01	HIGH	早期长轴距外廓。	READY
22381_late_swb	22381	Sedan	Turbo R facelift	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-LATE-SWB-01	MEDIUM	1995年后加宽标准轴距外廓。	READY
22381_late_lwb	22381	Sedan	Turbo R facelift	SZ	4	EU-BENTLEY-TURBO-R-SEDAN-LATE-LWB-01	MEDIUM	1995年后加宽长轴距外廓。	READY
22433_prefl	22433	MPV	Zafira A	F75	5	EU-CHEVROLET-ZAFIRA-A-MPV-PREFL-01	HIGH	2001-2004年早期外廓。	READY
22433_facelift	22433	MPV	Zafira A facelift	F75	5	EU-CHEVROLET-ZAFIRA-A-MPV-FACELIFT-01	HIGH	2005-2012年后期外廓。	READY
22443_3dr	22443	Hatchback	106 I		3	EU-PEUGEOT-106-I-HATCHBACK-01	HIGH	三门物理分支。	READY
22443_5dr	22443	Hatchback	106 I		5	EU-PEUGEOT-106-I-HATCHBACK-01	HIGH	五门物理分支；三维与三门相同。	READY
22449	22449	SUV	Grand Vitara II	JT	3	EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	HIGH	1.6汽油版本对应三门车身。	READY
22453_narrow	22453	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	MEDIUM	标准窄体三门分支。	READY
22453_widebody	22453	SUV	Grand Vitara I		3	EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	MEDIUM	SE宽体三门分支。	READY
22457	22457	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1201-1300_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPRICE-IV-SEDAN-PREFL-01	5438	1956	1440	Automobile-Catalog 1991 Chevrolet Caprice Sedan 5.0L V8;Automobile-Catalog 1993 Chevrolet Caprice Classic LS Sedan 5.0L V8	https://www.automobile-catalog.com/car/1991/471800/chevrolet_caprice_sedan_5_0l_v-8.html;https://www.automobile-catalog.com/car/1993/471920/chevrolet_caprice_classic_ls_sedan_5_0l_v-8.html
EU-CHEVROLET-CAPRICE-IV-SEDAN-FACELIFT-01	5438	1968	1415	Automobile-Catalog 1995 Chevrolet Caprice Classic Sedan 5.7L V8	https://www.automobile-catalog.com/car/1995/472115/chevrolet_caprice_classic_sedan_5_7l_v-8.html
EU-CHEVROLET-CAPRICE-IV-WAGON-01	5519	2022	1547	Automobile-Catalog 1991 Chevrolet Caprice Station Wagon 5.0L V8	https://www.automobile-catalog.com/car/1991/471845/chevrolet_caprice_station_wagon_5_0l_v-8.html
EU-CHEVROLET-CAVALIER-II-SEDAN-PREFL-01	4536	1676	1361	Edmunds 1990 Chevrolet Cavalier Sedan specifications	https://www.edmunds.com/chevrolet/cavalier/1990/sedan/features-specs/
EU-CHEVROLET-CAVALIER-II-SEDAN-FACELIFT-01	4630	1684	1361	Edmunds 1992 Chevrolet Cavalier specifications	https://www.edmunds.com/chevrolet/cavalier/1992/features-specs/
EU-CHEVROLET-CAVALIER-II-COUPE-PREFL-01	4531	1676	1321	Automobile-Catalog 1990 Chevrolet Cavalier Coupe 2.2L EFI	https://www.automobile-catalog.com/car/1990/468305/chevrolet_cavalier_coupe_2_2l_efi.html
EU-CHEVROLET-CAVALIER-II-COUPE-FACELIFT-01	4630	1684	1321	Automobile-Catalog 1992 Chevrolet Cavalier Z24 Coupe	https://www.automobile-catalog.com/car/1992/468905/chevrolet_cavalier_z24_coupe.html
EU-CHEVROLET-CAVALIER-II-CONVERTIBLE-01	4630	1684	1321	Chevrolet 1991 Cavalier RS Convertible official foldout;Edmunds 1991 Chevrolet Cavalier Convertible RS specifications	https://xr793.com/wp-content/uploads/2020/02/1991-Chevrolet-Cavalier-RS-Convertible-Foldout.pdf;https://www.edmunds.com/chevrolet/cavalier/1991/convertible/st-12809/features-specs/
EU-CHEVROLET-CAVALIER-III-SEDAN-01	4580	1712	1392	Automobile-Catalog 1996 Chevrolet Cavalier Sedan 2.2L SFI	https://www.automobile-catalog.com/car/1996/474815/chevrolet_cavalier_sedan_2_2l_sfi.html
EU-BUICK-CENTURY-IV-SEDAN-PREFL-01	4803	1720	1364	Automobile-Catalog 1984 Buick Century Limited Sedan 2.5L	https://www.automobile-catalog.com/car/1984/314255/buick_century_limited_sedan_2_5l.html
EU-BUICK-CENTURY-IV-SEDAN-FACELIFT-01	4803	1763	1364	Automobile-Catalog 1988 Buick Century Limited Sedan 2.8L V6	https://www.automobile-catalog.com/car/1988/1490375/buick_century_limited_sedan_2_8l_v-6.html
EU-BUICK-CENTURY-IV-WAGON-PREFL-01	4851	1763	1377	Automobile-Catalog 1984 Buick Century Custom Wagon 3.0L V6	https://www.automobile-catalog.com/car/1984/314570/buick_century_custom_wagon_3_0l_v-6.html
EU-BUICK-CENTURY-IV-WAGON-FACELIFT-01	4849	1763	1377	Automobile-Catalog 1992 Buick Century Limited Wagon 3.3L V6	https://www.automobile-catalog.com/car/1992/320930/buick_century_limited_wagon_3_3l_v-6.html
EU-CHRYSLER-CIRRUS-I-SEDAN-01	4746	1822	1374	Auto-Data Chrysler Stratus JA 2.0 LE;Auto-Data Chrysler Stratus JA 2.5 LX V6	https://www.auto-data.net/en/chrysler-stratus-ja-2.0-le-131hp-14720;https://www.auto-data.net/en/chrysler-stratus-ja-2.5-lx-v6-163hp-14721
EU-HONDA-CITY-III-SEDAN-PREFL-01	4225	1690	1400	Auto-Data Honda City Sedan III 1.5i 16V	https://www.auto-data.net/en/honda-city-sedan-iii-1.5i-16v-105hp-12188
EU-HONDA-CITY-III-SEDAN-TYPE-Z-01	4270	1690	1375	Automobile-Catalog 2000 Honda City Type-Z	https://www.automobile-catalog.com/car/2000/1271420/honda_city_type-z.html
EU-HONDA-CITY-IV-SEDAN-FACELIFT-01	4390	1690	1485	Automobile-Catalog 2006 Honda City 1.4 i-DSI LS CVT	https://www.automobile-catalog.com/car/2006/1143035/honda_city_1_4_i-dsi_ls_cvt.html
EU-LADA-110-SEDAN-01	4277	1676	1430	Auto-Data Lada 2110 model specifications	https://www.auto-data.net/en/lada-2110-model-1423
EU-SEAT-LEON-III-ST-WAGON-01	4535	1816	1454	Auto-Data Seat Leon III ST 1.8 TSI specifications	https://www.auto-data.net/en/seat-leon-iii-st-1.8-tsi-180hp-start-stop-19415
EU-CHRYSLER-CONCORDE-I-SEDAN-PREFL-01	5151	1890	1430	Automobile-Catalog 1996 Chrysler Concorde LX 3.3L	https://www.automobile-catalog.com/car/1996/518615/chrysler_concorde_lx_3_3l_v-6_automatic.html
EU-CHRYSLER-CONCORDE-I-SEDAN-FACELIFT-01	5118	1890	1430	Edmunds 1997 Chrysler Concorde LX specifications	https://www.edmunds.com/chrysler/concorde/1997/st-3/features-specs/
EU-CHRYSLER-CONCORDE-II-SEDAN-PREFL-01	5311	1890	1420	Automobile-Catalog 1998 Chrysler Concorde LX;Edmunds 1999 Chrysler Concorde LX specifications	https://www.automobile-catalog.com/car/1998/520115/chrysler_concorde_lx.html;https://www.edmunds.com/chrysler/concorde/1999/sedan/st-12673/features-specs/
EU-CHRYSLER-CONCORDE-II-SEDAN-FACELIFT-01	5276	1890	1417	Automobile-Catalog 2002 Chrysler Concorde LX;Edmunds 2003 Chrysler Concorde specifications	https://www.automobile-catalog.com/car/2002/520175/chrysler_concorde_lx.html;https://www.edmunds.com/chrysler/concorde/2003/features-specs/
EU-BENTLEY-CONTINENTAL-CONVERTIBLE-01	5196	1836	1518	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-CHEVROLET-CORSA-B-SEDAN-01	4026	1608	1387	Automobile-Catalog 1998 Chevrolet Corsa Sedan Wind	https://www.automobile-catalog.com/car/1998/491525/chevrolet_corsa_sedan_wind.html
EU-CADILLAC-DEVILLE-VII-SEDAN-01	5326	1943	1433	Edmunds 1996 Cadillac DeVille specifications;Edmunds 1997 Cadillac DeVille specifications	https://www.edmunds.com/cadillac/deville/1996/features-specs/;https://www.edmunds.com/cadillac/deville/1997/features-specs/
EU-CADILLAC-DEVILLE-VIII-SEDAN-01	5263	1892	1440	Edmunds 2000 Cadillac DeVille specifications;Edmunds 2005 Cadillac DeVille specifications	https://www.edmunds.com/cadillac/deville/2000/features-specs/;https://www.edmunds.com/cadillac/deville/2005/features-specs/
EU-AMC-EAGLE-I-SEDAN-1980-01	4729	1826	1407	Automobile-Catalog 1980 AMC Eagle 4-Door Sedan 258ci	https://www.automobile-catalog.com/car/1980/46430/amc_eagle_4-door_sedan_258ci.html
EU-AMC-EAGLE-I-SEDAN-1981-01	4674	1826	1407	Automobile-Catalog 1981 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1981/1877225/amc_eagle_4-door_sedan_4_2l_automatic.html
EU-AMC-EAGLE-I-SEDAN-1982-01	4732	1836	1407	Automobile-Catalog 1982 AMC Eagle Limited 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1982/1879970/amc_eagle_limited_4-door_sedan_4_2l.html
EU-AMC-EAGLE-I-SEDAN-1983-01	4653	1836	1407	Automobile-Catalog 1983 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1983/1883075/amc_eagle_4-door_sedan_4_2l.html
EU-AMC-EAGLE-I-SEDAN-1984-1985-01	4595	1836	1382	Automobile-Catalog 1984 AMC Eagle 4-Door Sedan 4.2L;Automobile-Catalog 1985 AMC Eagle 4-Door Sedan 4.2L	https://www.automobile-catalog.com/car/1984/1883330/amc_eagle_4-door_sedan_4_2l.html;https://www.automobile-catalog.com/car/1985/1883570/amc_eagle_4-door_sedan_4_2l_automatic.html
EU-BUICK-ELECTRA-V-SEDAN-01	5621	1928	1445	Automobile-Catalog 1983 Buick Electra Park Avenue Sedan 4.1L	https://www.automobile-catalog.com/car/1983/309455/buick_electra_park_avenue_sedan_4_1l_v-6.html
EU-LEXUS-GS-IV-SEDAN-01	4850	1840	1455	Auto-Data Lexus GS IV 250 V6 specifications	https://www.auto-data.net/en/lexus-gs-iv-250-v6-209hp-automatic-21321
EU-BUICK-ELECTRA-VI-SEDAN-PREFL-01	5004	1831	1379	Automobile-Catalog 1985 Buick Electra Park Avenue Sedan 3.8L;Automobile-Catalog 1988 Buick Electra Park Avenue Sedan	https://www.automobile-catalog.com/car/1985/317225/buick_electra_park_avenue_sedan_3_8l_v-6.html;https://www.automobile-catalog.com/car/1988/317840/buick_electra_park_avenue_sedan.html
EU-BUICK-ELECTRA-VI-SEDAN-FACELIFT-01	5000	1840	1379	Automobile-Catalog 1989 Buick Electra Park Avenue Sedan;Automobile-Catalog 1990 Buick Electra Park Avenue Sedan	https://www.automobile-catalog.com/car/1989/318065/buick_electra_park_avenue_sedan.html;https://www.automobile-catalog.com/car/1990/318200/buick_electra_park_avenue_sedan.html
EU-BUICK-PARK-AVENUE-I-SEDAN-01	5215	1869	1400	Automobile-Catalog 1991 Buick Park Avenue	https://www.automobile-catalog.com/car/1991/321515/buick_park_avenue.html
EU-HONDA-ELEMENT-I-SUV-PREFL-01	4326	1816	1788	Automobile-Catalog 2008 Honda Element EX 4WD	https://www.automobile-catalog.com/car/2008/1144160/honda_element_ex_4wd.html
EU-HONDA-ELEMENT-I-SUV-FACELIFT-01	4315	1819	1788	Honda 2009 Element official specifications;Car and Driver 2009 Honda Element specifications	https://hondanews.com/en-US/releases/release-86da9dae004ffe6c4bd1af004c34bc16-2009-honda-element-specifications-and-features;https://www.caranddriver.com/honda/element/specs/2009/honda_element_honda-element_2009
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-1500-01	5558	2012	2068	Edmunds 1996 Chevrolet Express G1500 specifications	https://www.edmunds.com/chevrolet/express/1996/st-13251/features-specs/
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-SWB-2500-01	5558	2012	2062	Edmunds 1996 Chevrolet Express G2500 specifications	https://www.edmunds.com/chevrolet/express/1996/st-13257/features-specs/
EU-CHEVROLET-EXPRESS-I-CARGO-VAN-LWB-2500-01	6066	2012	2108	Edmunds 1996 Chevrolet Chevy Van G2500 Extended specifications	https://www.edmunds.com/chevrolet/chevy-van/1996/st-13255/features-specs/
EU-CADILLAC-FLEETWOOD-FWD-SEDAN-01	5222	1864	1402	Edmunds 1991 Cadillac Fleetwood Sedan specifications	https://www.edmunds.com/cadillac/fleetwood/1991/sedan/features-specs/
EU-CADILLAC-BROUGHAM-D-SEDAN-01	5613	1943	1458	Edmunds 1991 Cadillac Brougham specifications	https://www.edmunds.com/cadillac/brougham/1991/features-specs/
EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1980-01	5613	1941	1440	Automobile-Catalog 1980 Cadillac Fleetwood Brougham 5.7L Diesel	https://www.automobile-catalog.com/car/1980/187010/cadillac_fleetwood_brougham_5_7l_v-8_diesel.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-SEDAN-1981-1985-01	5613	1913	1440	Automobile-Catalog 1981 Cadillac Fleetwood Brougham Sedan 5.7L Diesel;Automobile-Catalog 1985 Cadillac Fleetwood Brougham Sedan 5.7L Diesel	https://www.automobile-catalog.com/car/1981/330890/cadillac_fleetwood_brougham_sedan_5_7l_v-8_diesel.html;https://www.automobile-catalog.com/car/1985/331895/cadillac_fleetwood_brougham_sedan_5_7l_v-8_diesel.html
EU-CADILLAC-FLEETWOOD-RWD-SEDAN-01	5718	1981	1450	Edmunds 1993 Cadillac Fleetwood specifications;Edmunds 1996 Cadillac Fleetwood specifications	https://www.edmunds.com/cadillac/fleetwood/1993/st-766/features-specs/;https://www.edmunds.com/cadillac/fleetwood/1996/features-specs/
EU-JEEP-WRANGLER-JK-SUV-2D-X-01	4138	1872	1801	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/features-specs/
EU-JEEP-WRANGLER-JK-SUV-2D-SAHARA-01	4153	1872	1834	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-JEEP-WRANGLER-JK-SUV-2D-RUBICON-01	4161	1872	1839	Kelley Blue Book 2007 Jeep Wrangler specifications;Jeep 2007 Wrangler full specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.jeepfan.com/tech/07Wrangler/full-specifications.pdf
EU-JEEP-WRANGLER-JKU-SUV-4D-X-01	4684	1877	1831	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-JEEP-WRANGLER-JKU-SUV-4D-SAHARA-01	4648	1877	1798	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler Unlimited Sahara specifications	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/suv/st-100782108/features-specs/
EU-JEEP-WRANGLER-JKU-SUV-4D-RUBICON-01	4684	1877	1836	Kelley Blue Book 2007 Jeep Wrangler specifications;Edmunds 2007 Jeep Wrangler trim dimensions	https://www.kbb.com/jeep/wrangler/2007/specs/;https://www.edmunds.com/jeep/wrangler/2007/trims/
EU-MASERATI-GRANSPORT-I-COUPE-01	4523	1822	1295	Auto-Data Maserati GranSport 4.2 V8 Coupe	https://www.auto-data.net/en/maserati-gransport-4.2-i-v8-32v-400hp-10896
EU-MASERATI-GRANSPORT-SPYDER-CONVERTIBLE-01	4303	1822	1295	Automobile-Catalog 2005 Maserati GranSport Spyder Cambiocorsa	https://www.automobile-catalog.com/car/2005/1447220/maserati_gransport_spyder_cambiocorsa.html
EU-HYUNDAI-H1-TRUCK-SR-PICKUP-LONG-01	5415	1820	1905	Hasznaltauto Hyundai H-1 Truck Long Basic catalog	https://katalogus.hasznaltauto.hu/hyundai/h-1_truck_long_basic/50062
EU-DAIHATSU-HIJET-S85-PICKUP-STANDARD-01	3390	1395	1705	Motoro Swiss USTRA type approval 3DC109	https://motoro.ch/it/fiche-technique/daihatsu/hijet-pick-up-1-3
EU-DAIHATSU-HIJET-S85-PICKUP-LONG-WIDE-01	3745	1460	1705	Motoro Swiss USTRA type approval 3DC110	https://motoro.ch/it/fiche-technique/daihatsu/hijet-pick-up-1-3
EU-GMC-S15-JIMMY-I-SUV-2D-RWD-01	4326	1661	1628	AutoDetective 1989 GMC S15 Jimmy specifications	https://www.autodetective.com/directory/1989/gmc/s15-jimmy/
EU-GMC-S15-JIMMY-I-SUV-4D-RWD-01	4491	1661	1595	Edmunds 1991 GMC S-15 Jimmy SLE specifications	https://www.edmunds.com/gmc/s-15-jimmy/1991/st-4422/features-specs/
EU-GMC-S15-JIMMY-I-SUV-2D-4WD-01	4326	1661	1633	Edmunds 1994 GMC Jimmy specifications	https://www.edmunds.com/gmc/jimmy/1994/features-specs/
EU-GMC-S15-JIMMY-I-SUV-4D-4WD-01	4491	1661	1633	AutoDetective 1991 GMC S15 Jimmy 4-Door 4WD specifications	https://www.autodetective.com/directory/1991/gmc/s15-jimmy/trim/4-door-4wd/
EU-BUICK-LESABRE-VI-SEDAN-01	4991	1831	1410	Automobile-Catalog 1987 Buick LeSabre Custom Sedan	https://www.automobile-catalog.com/car/1987/317780/buick_le_sabre_custom_sedan.html
EU-BUICK-LESABRE-VII-SEDAN-01	5080	1902	1415	Automobile-Catalog 1992 Buick LeSabre Custom;Edmunds 1992 Buick LeSabre specifications	https://www.automobile-catalog.com/car/1992/321590/buick_le_sabre_custom.html;https://www.edmunds.com/buick/lesabre/1992/features-specs/
EU-CHEVROLET-LUMINA-I-Z34-COUPE-01	5062	1821	1354	Automobile-Catalog 1991 Chevrolet Lumina Z34	https://www.automobile-catalog.com/car/1991/471200/chevrolet_lumina_z34.html
EU-CHEVROLET-LUMINA-II-SEDAN-01	5103	1842	1402	Automobile-Catalog 1996 Chevrolet Lumina Sedan 3100 V6	https://www.automobile-catalog.com/car/1996/474335/chevrolet_lumina_sedan_3100_v6_sfi_automatic.html
EU-BENTLEY-MULSANNE-S-SEDAN-SWB-01	5268	1887	1485	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-BENTLEY-MULSANNE-S-SEDAN-LWB-01	5370	1887	1485	Rolls-Royce Motor Cars TSD 4700 General Information	https://rrtechnical.info/sz/sz87/a1.pdf
EU-BUICK-REGAL-III-COUPE-1988-1991-01	4882	1842	1346	Automobile-Catalog 1989 Buick Regal Gran Sport Coupe 3.1L V6	https://www.automobile-catalog.com/car/1989/318845/buick_regal_gran_sport_coupe_3_1l_v-6_automatic.html
EU-BUICK-REGAL-III-SEDAN-1990-1991-01	4943	1801	1384	Automobile-Catalog 1990 Buick Regal Limited Sedan 3.1L V6	https://www.automobile-catalog.com/car/1990/319055/buick_regal_limited_sedan_3_1l_v-6.html
EU-BUICK-REGAL-III-COUPE-1992-1994-01	4917	1842	1346	Automobile-Catalog 1994 Buick Regal Custom Coupe 3100 V6	https://www.automobile-catalog.com/car/1994/319565/buick_regal_custom_coupe_3100_v6.html
EU-BUICK-REGAL-III-SEDAN-1992-1993-01	4925	1842	1384	Automobile-Catalog 1992 Buick Regal Gran Sport Sedan	https://www.automobile-catalog.com/car/1992/319310/buick_regal_gran_sport_sedan.html
EU-BUICK-REGAL-III-SEDAN-1994-01	4948	1842	1384	Automobile-Catalog 1994 Buick Regal Custom Sedan 3100 V6	https://www.automobile-catalog.com/car/1994/319640/buick_regal_custom_sedan_3100_v6.html
EU-BUICK-REGAL-III-COUPE-1995-1996-01	4925	1842	1354	Automobile-Catalog 1995 Buick Regal Gran Sport Coupe	https://www.automobile-catalog.com/car/1995/319745/buick_regal_gran_sport_coupe.html
EU-BUICK-REGAL-III-SEDAN-1995-1996-01	4920	1842	1384	Automobile-Catalog 1995 Buick Regal Custom Sedan 3100 V6	https://www.automobile-catalog.com/car/1995/319760/buick_regal_custom_sedan_3100_v6.html
EU-BUICK-ROADMASTER-VIII-ESTATE-WAGON-01	5524	2004	1527	Edmunds 1991 Buick Roadmaster Estate Wagon specifications	https://www.edmunds.com/buick/roadmaster/1991/wagon/features-specs/
EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-SHORT-01	4526	1646	1610	Chevrolet 1990 S/T Pickup official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1990-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-I-PICKUP-4WD-REGCAB-LONG-01	4933	1646	1610	Chevrolet 1990 S/T Pickup official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1990-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-I-PICKUP-4WD-EXTCAB-SHORT-01	4897	1646	1610	Chevrolet 1990 S/T Pickup official vehicle information kit	https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1990-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-SHORT-01	4793	1725	1577	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-2WD-REGCAB-LONG-01	5197	1725	1577	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-2WD-EXTCAB-SHORT-01	5164	1725	1580	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-SHORT-01	4793	1725	1621	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-4WD-REGCAB-LONG-01	5197	1725	1661	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-CHEVROLET-S10-II-PICKUP-4WD-EXTCAB-SHORT-01	5164	1725	1621	Chevrolet 1995 S-10 Pickup official technical guide	https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1995-Chevrolet-S-10.pdf
EU-MITSUBISHI-ECLIPSE-I-COUPE-01	4390	1695	1321	Auto-Data Mitsubishi Eclipse I specifications	https://www.auto-data.net/en/mitsubishi-eclipse-model-1739
EU-RENAULT-LAGUNA-II-GRANDTOUR-WAGON-FACELIFT-01	4695	1772	1443	Auto-Data Renault Laguna II Grandtour 1.6 i 16V;AutoMoli Renault Laguna II Grandtour	https://www.auto-data.net/en/renault-laguna-ii-grandtour-1.6-i-16v-112hp-10308;https://www.automoli.com/us/vehicles/renault/laguna/laguna-ii-grandtour-2119/
EU-CHRYSLER-SEBRING-I-COUPE-01	4760	1770	1296	Auto-Data Chrysler Sebring Coupe FJ 2.5 V6	https://www.auto-data.net/en/chrysler-sebring-coupe-fj-2.5-v6-166hp-14821
EU-CHEVROLET-SPARK-M150-HATCHBACK-01	3495	1495	1485	Auto-Data Daewoo Matiz I facelift 0.8 i	https://www.auto-data.net/en/daewoo-matiz-i-facelift-2000-0.8-i-52hp-16371
EU-CHEVROLET-SPARK-II-HATCHBACK-01	3495	1495	1485	Auto-Data Chevrolet Spark II 0.8i	https://www.auto-data.net/en/chevrolet-spark-ii-0.8-i-52hp-14551
EU-MASERATI-BITURBO-SPYDER-CONVERTIBLE-01	4043	1714	1310	Automobile-Catalog 1987 Maserati Biturbo Spyder;Automobile-Catalog 1991 Maserati Biturbo Spyder range	https://www.automobile-catalog.com/car/1987/1445300/maserati_biturbo_spyder.html;https://www.automobile-catalog.com/make/maserati/biturbo/biturbo_spyder/1991.html
EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-PREFL-01	4359	1786	1558	Automobile-Catalog 2013 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2013/2025935/mercedes-benz_b_220_4matic.html
EU-MERCEDES-BENZ-B-CLASS-W246-HATCHBACK-FACELIFT-01	4393	1786	1558	Automobile-Catalog 2015 Mercedes-Benz B 220 4MATIC	https://www.automobile-catalog.com/car/2015/2080145/mercedes-benz_b_220_4matic.html
EU-SSANGYONG-RODIUS-STAVIC-I-MPV-01	5125	1915	1820	Auto-Online SsangYong Stavic launch specifications;Automobile-Catalog 2012 SsangYong Rodius SV270	https://www.auto-online.com.tw/news/0-7716;https://www.automobile-catalog.com/car/2012/3164675/ssangyong_rodius_sv270_xdi_automatic.html
EU-SUZUKI-GRAND-VITARA-II-SUV-5D-01	4470	1810	1695	Automobile-Catalog 2007 Suzuki Grand Vitara 2.7 V6 5-Door	https://www.automobile-catalog.com/car/2007/3414920/suzuki_grand_vitara_2_7_v6_5-door_4wd_automatic.html
EU-CHEVROLET-TAHOE-I-SUV-2D-01	4788	1958	1839	Automobile-Catalog 1995 Chevrolet Tahoe K1500 2-Door 5.7L	https://www.automobile-catalog.com/car/1995/483965/chevrolet_tahoe_k1500_2-door_5_7l_v-8_efi_automatic.html
EU-CHEVROLET-TAHOE-I-SUV-4D-01	5057	1941	1783	Automobile-Catalog 1995 Chevrolet Tahoe K1500 4-Door 5.7L	https://www.automobile-catalog.com/car/1995/484025/chevrolet_tahoe_k1500_4-door_5_7l_v-8_efi_automatic.html
EU-BENTLEY-TURBO-R-SEDAN-EARLY-SWB-01	5268	1887	1480	Automobile-Catalog 1986 Bentley Turbo R	https://www.automobile-catalog.com/car/1986/260315/bentley_turbo_r.html
EU-BENTLEY-TURBO-R-SEDAN-EARLY-LWB-01	5370	1887	1480	Automobile-Catalog 1990 Bentley Turbo R LWB	https://www.automobile-catalog.com/car/1990/260495/bentley_turbo_r_lwb.html
EU-BENTLEY-TURBO-R-SEDAN-LATE-SWB-01	5295	1914	1480	Automobile-Catalog 1995 Bentley Turbo R	https://www.automobile-catalog.com/car/1995/260840/bentley_turbo_r.html
EU-BENTLEY-TURBO-R-SEDAN-LATE-LWB-01	5395	1914	1480	Automobile-Catalog 1995 Bentley Turbo R LWB	https://www.automobile-catalog.com/car/1995/260855/bentley_turbo_r_lwb.html
EU-CHEVROLET-ZAFIRA-A-MPV-PREFL-01	4317	1742	1629	Automobile-Catalog 2001 Chevrolet Zafira 2.0 16V	https://www.automobile-catalog.com/car/2001/492035/chevrolet_zafira_2_0_16v.html
EU-CHEVROLET-ZAFIRA-A-MPV-FACELIFT-01	4334	1742	1687	Automobile-Catalog 2005 Chevrolet Zafira Elegance 2.0 Flexpower;Automobile-Catalog 2012 Chevrolet Zafira Elegance 2.0 Flexpower	https://www.automobile-catalog.com/car/2005/492545/chevrolet_zafira_elegance_2_0_flexpower_gasolina.html;https://www.automobile-catalog.com/car/2012/1208105/chevrolet_zafira_elegance_2_0_flexpower_gasolina.html
EU-PEUGEOT-106-I-HATCHBACK-01	3564	1590	1369	Auto-Data Peugeot 106 I generation specifications	https://www.auto-data.net/en/peugeot-106-i-1a-c-generation-1244
EU-SUZUKI-GRAND-VITARA-II-SUV-3D-01	4005	1810	1695	Auto-Data Suzuki Grand Vitara II 3 Door 1.6	https://www.auto-data.net/en/suzuki-grand-vitara-ii-3-door-1.6-i-16v-107hp-16578
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-NARROW-01	3905	1695	1685	Automobile-Catalog 2004 Suzuki Grand Vitara 1.6 16V Estate 4WD	https://www.automobile-catalog.com/car/2004/3352925/suzuki_grand_vitara_1_6_16v_estate_4wd.html
EU-SUZUKI-GRAND-VITARA-I-SUV-3D-WIDEBODY-01	3905	1780	1740	Automobile-Catalog 2004 Suzuki Grand Vitara 1.6 16V SE Estate 4WD	https://www.automobile-catalog.com/car/2004/3352940/suzuki_grand_vitara_1_6_16v_se_estate_4wd.html
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-01	4581	1770	1447	Auto-Data Mercedes-Benz C-Class W204 C 200 CDI	https://www.auto-data.net/en/mercedes-benz-c-class-w204-c-200-cdi-136hp-12540
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1201-1300_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1990-Chevrolet-S-10.pdf "https://www.gm.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1990-Chevrolet-S-10.pdf"
[2]: https://katalogus.hasznaltauto.hu/hyundai/h-1_truck_long_basic/50062 "https://katalogus.hasznaltauto.hu/hyundai/h-1_truck_long_basic/50062"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1201-1300_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1201-1300_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1239 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（643 行）
