# 任务：all 第 1101-1200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0012__9b499a01


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1101-1200 行

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
all 第 1101-1200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	80	2.0 E 16V	Stufenheck	Frontantrieb	Benzin	101	137	Mar 1990	Sep 1991	2024-03-01	1131
Opel	Rekord d	1.7	Stufenheck	Heckantrieb	Benzin	44	60	Mar 1975	Aug 1977	2024-03-01	1132
Opel	Rekord d	1.7	Stufenheck	Heckantrieb	Benzin	49	66	Jan 1972	Feb 1975	2024-03-01	1133
Opel	Rekord d	1.7 S	Stufenheck	Heckantrieb	Benzin	61	83	Jan 1972	Feb 1975	2024-03-01	1134
Opel	Rekord d	1.7 S	Coupe	Heckantrieb	Benzin	61	83	Jan 1972	Feb 1975	2024-03-01	1135
Audi	80	1.8 S Quattro	Stufenheck	Allrad	Benzin	65	88	Sep 1986	Jul 1990	2024-03-01	1136
Audi	80	1.8 S Quattro	Stufenheck	Allrad	Benzin	66	90	Sep 1986	Sep 1991	2024-03-01	1137
Audi	80	1.8 Quattro	Stufenheck	Allrad	Benzin	83	113	Sep 1986	-	2024-03-01	1138
Audi	80	2.0 E Quattro	Stufenheck	Allrad	Benzin	83	113	Aug 1988	Sep 1990	2024-03-01	1139
Audi	80	2.0 Quattro	Stufenheck	Allrad	Benzin	85	115	Oct 1990	Aug 1991	2024-03-01	1140
Audi	80	2.0 E 16V Quattro	Stufenheck	Allrad	Benzin	101	137	Mar 1990	Aug 1991	2024-03-01	1141
Opel	Rekord d	1.9	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1975	Aug 1977	2024-03-01	1142
Opel	Rekord d	1.9	Coupe	Heckantrieb	Benzin	55	75	Mar 1975	Aug 1977	2024-03-01	1143
Opel	Rekord d	1.9	Stufenheck	Heckantrieb	Benzin	66	90	Mar 1975	Aug 1977	2024-03-01	1144
Opel	Rekord d	1.9	Coupe	Heckantrieb	Benzin	66	90	Mar 1975	Aug 1977	2024-03-01	1145
Audi	100	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Jan 1975	Jul 1976	2024-03-01	1146
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	63	85	Sep 1971	Jul 1974	2024-03-01	1147
Opel	Rekord d	1.9 S	Coupe	Heckantrieb	Benzin	71	97	Jan 1972	Feb 1975	2024-03-01	1148
Audi	100	1.8	Stufenheck	Frontantrieb	Benzin	74	100	Oct 1970	Jul 1976	2024-03-01	1149
Audi	100	1.9	Stufenheck	Frontantrieb	Benzin	82	112	Sep 1971	Jul 1976	2024-03-01	1150
Opel	Rekord d	1.9 S	Stufenheck	Heckantrieb	Benzin	71	97	Jan 1972	Feb 1975	2024-03-01	1151
Opel	Rekord d	2	Stufenheck	Heckantrieb	Benzin	74	100	Sep 1975	Aug 1977	2024-03-01	1152
Opel	Rekord d	2	Coupe	Heckantrieb	Benzin	74	100	Sep 1975	Aug 1977	2024-03-01	1153
Ford	Transit	2.5 DI	Bus	Heckantrieb	Diesel	59	80	Sep 1991	Jul 1994	2024-03-01	1154
Opel	Rekord d	2.0 D	Stufenheck	Heckantrieb	Diesel	40	54	Aug 1974	Aug 1977	2024-03-01	1155
Opel	Rekord d	2.1 D	Stufenheck	Heckantrieb	Diesel	44	60	Sep 1972	Aug 1977	2024-03-01	1156
Audi	100	1.6	Stufenheck	Frontantrieb	Benzin	63	85	Aug 1976	Jul 1982	2024-03-01	1157
Opel	Rekord d caravan	1.7	Kombi	Heckantrieb	Benzin	44	60	Mar 1975	Aug 1977	2024-03-01	1158
Opel	Rekord d caravan	1.7	Kombi	Heckantrieb	Benzin	49	67	Jan 1972	Feb 1975	2024-03-01	1159
Audi	100	1.9	Stufenheck	Frontantrieb	Benzin	74	100	Aug 1980	Aug 1984	2024-03-01	1160
Opel	Rekord d caravan	1.7 S	Kombi	Heckantrieb	Benzin	61	83	Jan 1972	Feb 1975	2024-03-01	1161
Opel	Rekord d caravan	1.9	Kombi	Heckantrieb	Benzin	55	75	Mar 1975	Aug 1977	2024-03-01	1162
Ford	Transit	2.5 TD	Bus	Heckantrieb	Diesel	63	85	Oct 1992	Jul 1994	2024-03-01	1163
Opel	Rekord d caravan	1.9	Kombi	Heckantrieb	Benzin	66	90	Mar 1975	Aug 1977	2024-03-01	1164
Opel	Rekord d caravan	1.9 S	Kombi	Heckantrieb	Benzin	71	97	Jan 1972	Feb 1975	2024-03-01	1165
Opel	Rekord d caravan	2.0 S	Kombi	Heckantrieb	Benzin	74	100	Sep 1975	Aug 1977	2024-03-01	1166
Opel	Rekord d caravan	2.0 D	Kombi	Heckantrieb	Diesel	40	54	Aug 1974	Aug 1977	2024-03-01	1167
Opel	Rekord d caravan	2.1 D	Kombi	Heckantrieb	Diesel	44	60	Sep 1972	Aug 1977	2024-03-01	1168
BMW	X6	Xdrive 40 D	SUV	Allrad	Diesel	225	306	Jul 2009	Jun 2014	2024-03-01	1169
Ford	Transit	2.5 TD	Bus	Heckantrieb	Diesel	74	100	Sep 1991	Jul 1994	2024-03-01	1170
Cadillac	Cts	6.2 V	Coupe	Heckantrieb	Benzin	415	564	Jan 2008	Jul 2014	2024-03-01	1171
Opel	Rekord e	1.7	Stufenheck	Heckantrieb	Benzin	44	60	Sep 1977	Oct 1982	2024-03-01	1172
Opel	Rekord e	1.8	Stufenheck	Heckantrieb	Benzin	55	75	Nov 1982	Aug 1986	2024-03-01	1173
Opel	Rekord e	1.8 S	Stufenheck	Heckantrieb	Benzin	66	90	Nov 1982	Aug 1986	2024-03-01	1174
Opel	Rekord e	1.8 E	Stufenheck	Heckantrieb	Benzin	74	100	May 1985	Aug 1986	2024-03-01	1175
Opel	Rekord e	1.9	Stufenheck	Heckantrieb	Benzin	55	75	Sep 1977	Oct 1982	2024-03-01	1176
Opel	Rekord e	2	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1977	Oct 1982	2024-03-01	1177
Opel	Rekord e	2.0 S	Stufenheck	Heckantrieb	Benzin	74	100	Aug 1977	Aug 1986	2024-03-01	1178
Opel	Rekord e	2.0 E	Stufenheck	Heckantrieb	Benzin	81	110	Sep 1977	Oct 1984	2024-03-01	1179
Opel	Rekord e	2.2 E	Stufenheck	Heckantrieb	Benzin	85	115	Nov 1984	Aug 1986	2024-03-01	1180
Opel	Rekord e	2.0 D	Stufenheck	Heckantrieb	Diesel	43	58	Sep 1977	Oct 1982	2024-03-01	1181
Opel	Rekord e	2.1 D	Stufenheck	Heckantrieb	Diesel	44	60	Sep 1977	Jul 1978	2024-03-01	1182
Opel	Rekord e	2.2 D	Stufenheck	Heckantrieb	Diesel	48	65	Aug 1978	Aug 1983	2024-03-01	1183
Opel	Rekord e	2.2 D	Stufenheck	Heckantrieb	Diesel	52	71	Nov 1982	Aug 1986	2024-03-01	1184
Opel	Rekord e	2.2 TD	Stufenheck	Heckantrieb	Diesel	63	86	Jun 1984	Aug 1986	2024-03-01	1185
Opel	Rekord e caravan	1.7	Kombi	Heckantrieb	Benzin	44	60	Sep 1977	Oct 1982	2024-03-01	1186
Opel	Rekord e caravan	1.8	Kombi	Heckantrieb	Benzin	55	75	Nov 1982	Aug 1986	2024-03-01	1187
Opel	Rekord e caravan	1.8 S	Kombi	Heckantrieb	Benzin	66	90	Nov 1982	Aug 1986	2024-03-01	1188
Opel	Rekord e caravan	1.8 E	Kombi	Heckantrieb	Benzin	74	100	May 1985	Aug 1986	2024-03-01	1189
Opel	Rekord e caravan	1.9	Kombi	Heckantrieb	Benzin	55	75	Sep 1977	Oct 1982	2024-03-01	1190
Opel	Rekord e caravan	2	Kombi	Heckantrieb	Benzin	66	90	Sep 1977	Oct 1982	2024-03-01	1191
Opel	Rekord e caravan	2.0 S	Kombi	Heckantrieb	Benzin	74	100	Aug 1977	Aug 1986	2024-03-01	1192
Opel	Rekord e caravan	2.0 E	Kombi	Heckantrieb	Benzin	81	110	Sep 1977	Oct 1984	2024-03-01	1193
Opel	Rekord e caravan	2.2 E	Kombi	Heckantrieb	Benzin	85	115	Nov 1984	Aug 1986	2024-03-01	1194
Alpina	B3	S Bi-turbo	Stufenheck	Heckantrieb	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1195
Opel	Rekord e caravan	2.0 D	Kombi	Heckantrieb	Diesel	43	58	Sep 1977	Oct 1982	2024-03-01	1196
Opel	Rekord e caravan	2.1 D	Kombi	Heckantrieb	Diesel	44	60	Sep 1977	Jul 1978	2024-03-01	1197
Opel	Rekord e caravan	2.2 D	Kombi	Heckantrieb	Diesel	48	65	Aug 1978	Aug 1983	2024-03-01	1198
Opel	Rekord e caravan	2.3 D	Kombi	Heckantrieb	Diesel	52	71	Nov 1982	Aug 1986	2024-03-01	1199
Opel	Rekord e caravan	2.2 TD	Kombi	Heckantrieb	Diesel	63	86	Jun 1984	Aug 1986	2024-03-01	1200
Opel	Commodore b	2.5	Stufenheck	Heckantrieb	Benzin	85	115	Jan 1972	Jul 1978	2024-03-01	1201
Cadillac	Cts	3	Kombi	Heckantrieb	Benzin	203	276	Jan 2008	-	2024-03-01	1202
Opel	Commodore b	2.5	Coupe	Heckantrieb	Benzin	85	115	Jan 1972	Jul 1978	2024-03-01	1203
Alpina	B3	S Bi-turbo Allrad	Stufenheck	Allrad	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1204
Opel	Commodore b	2.5 GS	Stufenheck	Heckantrieb	Benzin	96	130	Jan 1972	Aug 1975	2024-03-01	1205
Alpina	B3	S Bi-turbo	Kombi	Heckantrieb	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1206
Opel	Commodore b	2.5 GS	Coupe	Heckantrieb	Benzin	96	130	Jan 1972	Aug 1975	2024-03-01	1207
Opel	Commodore b	2.8 GS	Stufenheck	Heckantrieb	Benzin	103	140	Mar 1975	Jul 1978	2024-03-01	1208
Opel	Commodore b	2.8 GS	Coupe	Heckantrieb	Benzin	103	140	Mar 1975	Jul 1978	2024-03-01	1209
Opel	Commodore b	2.8 GS	Stufenheck	Heckantrieb	Benzin	104	141	Jan 1972	Jul 1978	2024-03-01	1210
Opel	Commodore b	2.8 GS	Coupe	Heckantrieb	Benzin	104	141	Dec 1972	Jul 1978	2024-03-01	1211
Opel	Commodore b	2.8 Gs/e	Coupe	Heckantrieb	Benzin	114	155	Mar 1975	Jul 1978	2024-03-01	1212
Opel	Commodore b	2.8 Gs/e	Stufenheck	Heckantrieb	Benzin	114	155	Mar 1975	Jul 1978	2024-03-01	1213
Opel	Commodore b	2.8 Gs/e	Coupe	Heckantrieb	Benzin	118	160	Jul 1972	Feb 1975	2024-03-01	1214
Opel	Commodore b	2.8 Gs/e	Stufenheck	Heckantrieb	Benzin	118	160	Jul 1972	Feb 1975	2024-03-01	1215
Opel	Commodore c	2.5 S	Stufenheck	Heckantrieb	Benzin	85	115	Aug 1978	Dec 1982	2024-03-01	1216
Opel	Commodore c	2.5 E	Stufenheck	Heckantrieb	Benzin	96	130	May 1981	Dec 1982	2024-03-01	1217
Opel	Commodore c caravan	2.5 S	Kombi	Heckantrieb	Benzin	85	115	Dec 1980	Dec 1982	2024-03-01	1218
Opel	Commodore c caravan	2.5 E	Kombi	Heckantrieb	Benzin	96	130	Dec 1980	Dec 1982	2024-03-01	1219
Opel	Omega a	1.8 N	Stufenheck	Heckantrieb	Benzin	60	82	Sep 1986	Aug 1987	2024-03-01	1220
Opel	Omega a	1.8	Stufenheck	Heckantrieb	Benzin	65	88	Sep 1987	Mar 1994	2024-03-01	1221
Opel	Omega a	1.8 S	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1986	Mar 1994	2024-03-01	1222
Opel	Omega a	1.8	Stufenheck	Heckantrieb	Benzin	85	115	Sep 1986	Mar 1994	2024-03-01	1223
Opel	Omega a	2	Stufenheck	Heckantrieb	Benzin	90	122	Sep 1986	Mar 1994	2024-03-01	1224
Opel	Omega a	3	Stufenheck	Heckantrieb	Benzin	115	156	Mar 1987	Dec 1987	2024-03-01	1225
Opel	Omega a	2.3 TD	Stufenheck	Heckantrieb	Diesel	66	90	Oct 1986	Aug 1988	2024-03-01	1226
Opel	Omega a	2.3 D	Stufenheck	Heckantrieb	Diesel	54	73	Oct 1986	Mar 1994	2024-03-01	1227
Opel	Omega a	2.3 TD Interc.	Stufenheck	Heckantrieb	Diesel	74	100	Aug 1988	Mar 1994	2024-03-01	1228
Opel	Omega a	2	Stufenheck	Heckantrieb	Benzin	74	100	Sep 1990	Mar 1994	2024-03-01	1229
Opel	Omega a	2	Stufenheck	Heckantrieb	Benzin	73	99	Sep 1990	Mar 1994	2024-03-01	1230


--- Round 1 / 首次发送 ---
## 更新点

* 已按物理车身聚类完成 Audi 80 B3、Opel Rekord D/E、BMW X6 E71、Cadillac CTS、Alpina B3 S、Opel Commodore B/C 和 Omega A 等车型的映射。

* Rekord E 跨 1982 年([汽车数据][1])均建立独立尺寸组。([汽车数据][2])6 Ktype `1169` 已按 E71 改款前后拆分。改款后官方技术表给出的最大高度为 1699 mm，并注明不含车顶天线时为 1690 mm。([汽车数据][3])100 暂未强行建组：C1 同版本资料出现 4600 mm 与 4635 mm 两种车长，且部分 Ktype 横跨 C1/C2/C3 或前后期。([汽车数据][1])次进度

* 输入 Ktype：100

* READY 输入 Ktype：91

* PENDING 输入 Ktype：9

* READY 映射行：98

* PENDING 映射行：9

* 已确认尺寸组：20

* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1131	1131	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	MEDIUM	16V版本资料不完整；B3四门轿车外廓已确认。	READY
1132	1132	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1133	1133	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1134	1134	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1135	1135	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1136	1136	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1137	1137	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1138	1138	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1139	1139	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1140	1140	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1141	1141	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	MEDIUM	16V版本资料不完整；B3四门轿车外廓已确认。	READY
1142	1142	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1143	1143	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1144	1144	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1145	1145	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1146	1146	Sedan	Audi 100 C1	F104			LOW	C1年段存在前后期车长资料冲突，候选尺寸组暂不落盘。	PENDING: C1前后期外廓与宽度口径冲突
1147	1147	Sedan	Audi 100 C1	F104			LOW	C1年段存在前后期车长资料冲突，候选尺寸组暂不落盘。	PENDING: C1前后期外廓与宽度口径冲突
1148	1148	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1149	1149	Sedan	Audi 100 C1	F104			LOW	C1年段存在前后期车长资料冲突，候选尺寸组暂不落盘。	PENDING: C1前后期外廓与宽度口径冲突
1150	1150	Sedan	Audi 100 C1	F104			LOW	C1年段存在前后期车长资料冲突，候选尺寸组暂不落盘。	PENDING: C1前后期外廓与宽度口径冲突
1151	1151	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1152	1152	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1153	1153	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1154	1154	MPV	Transit Mk4				LOW	Bus输入未区分轴距与车顶，候选含多个物理外廓。	PENDING: 轴距与车顶分支未确认
1155	1155	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1156	1156	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1157	1157	Sedan	Audi 100 C2	Typ 43			LOW	Ktype覆盖C2前后期，候选车长存在差异。	PENDING: C2前后期外廓边界未闭合
1158	1158	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1159	1159	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1160	1160	Sedan					LOW	生产区间跨Audi 100 C2与C3，具体物理分支待拆分。	PENDING: 跨代物理分支未闭合
1161	1161	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1162	1162	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1163	1163	MPV	Transit Mk4				LOW	Bus输入未区分轴距与车顶，候选含多个物理外廓。	PENDING: 轴距与车顶分支未确认
1164	1164	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1165	1165	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1166	1166	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1167	1167	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1168	1168	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1169_prefl	1169	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	同一Ktype跨2012年LCI，按改款前外廓拆分。	READY
1169_facelift	1169	SUV	X6 E71 LCI	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	同一Ktype跨2012年LCI，按改款后外廓拆分。	READY
1170	1170	MPV	Transit Mk4				LOW	Bus输入未区分轴距与车顶，候选含多个物理外廓。	PENDING: 轴距与车顶分支未确认
1171	1171	Coupe	CTS II Coupe		2	EU-CADILLAC-CTS-II-COUPE-V-01	MEDIUM	输入起始年月早于Coupe量产资料；按2011-2014 CTS-V Coupe映射。	READY
1172	1172	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1173	1173	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1174	1174	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1175	1175	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1176	1176	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1177	1177	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1178_prefl	1178	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1178_facelift	1178	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1179_prefl	1179	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1179_facelift	1179	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1180	1180	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1181	1181	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1182	1182	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1183_prefl	1183	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1183_facelift	1183	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1184	1184	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1185	1185	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1186	1186	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1187	1187	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1188	1188	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1189	1189	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1190	1190	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1191	1191	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1192_prefl	1192	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1192_facelift	1192	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1193_prefl	1193	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1193_facelift	1193	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1194	1194	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1195	1195	Sedan	B3 S Bi-Turbo	E90	4	EU-ALPINA-B3-S-E90-SEDAN-RWD-01	HIGH		READY
1196	1196	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1197	1197	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1198_prefl	1198	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1198_facelift	1198	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1199	1199	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1200	1200	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1201	1201	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1202	1202	Wagon	CTS II Sport Wagon		5	EU-CADILLAC-CTS-II-WAGON-01	MEDIUM	203 kW对应资料中的273 hp SAE标注；Wagon量产始于2010年。	READY
1203	1203	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1204	1204	Sedan	B3 S Bi-Turbo	E90	4	EU-ALPINA-B3-S-E90-SEDAN-AWD-01	HIGH		READY
1205	1205	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1206	1206	Wagon	B3 S Bi-Turbo Touring	E91	5	EU-ALPINA-B3-S-E91-WAGON-RWD-01	HIGH		READY
1207	1207	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1208	1208	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1209	1209	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1210	1210	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1211	1211	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1212	1212	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1213	1213	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1214	1214	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1215	1215	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1216	1216	Sedan	Commodore C			EU-OPEL-COMMODORE-C-SEDAN-01	HIGH		READY
1217	1217	Sedan	Commodore C			EU-OPEL-COMMODORE-C-SEDAN-01	HIGH		READY
1218	1218	Wagon	Commodore C Caravan		5	EU-OPEL-COMMODORE-C-WAGON-01	HIGH		READY
1219	1219	Wagon	Commodore C Caravan		5	EU-OPEL-COMMODORE-C-WAGON-01	HIGH		READY
1220	1220	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1221	1221	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1222	1222	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1223	1223	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1224	1224	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1225	1225	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1226	1226	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1227	1227	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1228	1228	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1229	1229	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1230	1230	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397	Auto-Data Audi 80 B3 generation	https://www.auto-data.net/en/audi-80-b3-typ-89-89q-8a-generation-1111
EU-OPEL-REKORD-D-SEDAN-01	4567	1718	1415	Auto-Data Opel Rekord D generation	https://www.auto-data.net/en/opel-rekord-d-generation-535
EU-OPEL-REKORD-D-COUPE-01	4607	1728	1380	Automobile-Catalog 1972 Opel Rekord Coupe 1700 S	https://www.automobile-catalog.com/car/1972/2422535/opel_rekord_coupe_1700_s.html
EU-OPEL-REKORD-D-WAGON-01	4594	1715	1440	Auto-Data Opel Rekord D Caravan generation	https://www.auto-data.net/en/opel-rekord-d-caravan-generation-536
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690	Auto-Data BMW X6 E71 40d specifications	https://www.auto-data.net/en/bmw-x6-e71-40d-306hp-xdrive-steptronic-17311
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699	BMW Group PressClub BMW X6 xDrive40d specifications valid from 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124596EN/207898
EU-CADILLAC-CTS-II-COUPE-V-01	4788	1882	1422	Car and Driver 2011 Cadillac CTS-V Coupe specifications	https://www.caranddriver.com/cadillac/cts-v/specs/2011/cadillac_cts-v_cadillac-cts-v-coupe_2011
EU-OPEL-REKORD-E1-SEDAN-01	4593	1726	1420	Auto-Data Opel Rekord E generation	https://www.auto-data.net/en/opel-rekord-e-generation-533
EU-OPEL-REKORD-E2-SEDAN-01	4652	1726	1420	Auto-Data Opel Rekord E facelift 1982 generation	https://www.auto-data.net/en/opel-rekord-e-facelift-1982-generation-5163
EU-OPEL-REKORD-E1-WAGON-01	4620	1726	1470	Auto-Data Opel Rekord E Caravan generation	https://www.auto-data.net/en/opel-rekord-e-caravan-generation-534
EU-OPEL-REKORD-E2-WAGON-01	4678	1720	1475	Auto-Data Opel Rekord E Caravan facelift 1982 generation	https://www.auto-data.net/en/opel-rekord-e-caravan-facelift-1982-generation-5162
EU-ALPINA-B3-S-E90-SEDAN-RWD-01	4545	1817	1422	Automobile-Catalog 2010 Alpina B3 S Biturbo	https://www.automobile-catalog.com/car/2010/1339640/alpina_b3_s_biturbo.html
EU-OPEL-COMMODORE-B-SEDAN-01	4607	1728	1415	Auto-Data Opel Commodore B generation	https://www.auto-data.net/en/opel-commodore-b-generation-500
EU-CADILLAC-CTS-II-WAGON-01	4878	1842	1473	Auto-Data Cadillac CTS II Sport Wagon 3.0 V6	https://www.auto-data.net/en/cadillac-cts-ii-sport-wagon-3.0-v6-273hp-automatic-30174
EU-OPEL-COMMODORE-B-COUPE-01	4607	1728	1380	Auto-Data Opel Commodore B Coupe generation	https://www.auto-data.net/en/opel-commodore-b-coupe-generation-501
EU-ALPINA-B3-S-E90-SEDAN-AWD-01	4545	1817	1437	Automobile-Catalog 2010 Alpina B3 S Biturbo Allrad	https://www.automobile-catalog.com/car/2010/1339655/alpina_b3_s_biturbo_allrad.html
EU-ALPINA-B3-S-E91-WAGON-RWD-01	4541	1817	1450	Automobile-Catalog 2010 Alpina B3 S Biturbo Touring	https://www.automobile-catalog.com/car/2010/1339670/alpina_b3_s_biturbo_touring.html
EU-OPEL-COMMODORE-C-SEDAN-01	4705	1730	1410	Auto-Data Opel Commodore C generation	https://www.auto-data.net/en/opel-commodore-c-generation-498
EU-OPEL-COMMODORE-C-WAGON-01	4732	1722	1470	Auto-Data Opel Commodore C Caravan 2.5 E	https://www.auto-data.net/en/opel-commodore-c-caravan-2.5-e-130hp-1831
EU-OPEL-OMEGA-A-SEDAN-01	4770	1810	1445	Auto-Data Opel Omega A generation	https://www.auto-data.net/en/opel-omega-a-generation-515
```

## 下一步优先处理

1. 集中处理 Audi 100：先确定 C1 的 4600/4635 mm 差异对应的具体发动机、生产期和保险杠外廓，再闭合 Ktype `1146`、`1147`、`1149`、`1150`。
2. 拆分 Audi 100 C2 前后期 Ktype `1157`，以及跨 C2/C3 的 Ktype `1160`。
3. 核对 Ford Transit Bus Ktype `1154`、`1163`、`1170` 是否能由 Ktype 资料反查 SWB/LWB 与普通顶/高顶；无法唯一反查时保留明确派生分支，而不任选单一尺寸。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.6-l-85hp-4168 "https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.6-l-85hp-4168"
[2]: https://www.auto-data.net/en/opel-rekord-e-generation-533 "https://www.auto-data.net/en/opel-rekord-e-generation-533"
[3]: https://www.auto-data.net/en/bmw-x6-e71-40d-306hp-xdrive-steptronic-17311 "https://www.auto-data.net/en/bmw-x6-e71-40d-306hp-xdrive-steptronic-17311"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 1. 更新点

* 已消除 Audi 100 的 6 个 PENDING Ktype：`1146`、`1147`、`1149`、`1150`、`1157`、`1160`。
* Audi 100 C1 已按 1973 年改款和不同量产外廓拆成 4 个尺寸组：4590、4600、4625、4635 mm 车长分支。([汽车数据][1])
* Audi 100 C2 Ktype `1157` 已拆为改款前 4680 mm 和改款后 4683 mm 外廓；Ktype `1160` 已拆为 C2 与 C3 两个代际。([汽车数据][2])
* Ford Transit Bus 的 `1154`、`1163`、`1170` 仍保持 PENDING。现有资料显示同一时期 Bus/Kombi 至少涉及短轴低顶及多个长轴、中高顶外廓，而输入没有轴距、车顶或车型代码，暂不能可靠创建派生行。([Transit Center Ford Transit Spare Parts][3])

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* PENDING 输入 Ktype：3
* READY 映射行：109
* PENDING 映射行：3
* 已确认尺寸组：27
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1146	1146	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	HIGH		READY
1147_prefl	1147	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1147_facelift	1147	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-01	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1149_prefl	1149	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-02	MEDIUM	同一Ktype跨1973年改款；输入年段与规格页存在部分错位。	READY
1149_facelift	1149	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	MEDIUM	同一Ktype跨1973年改款；输入年段与规格页存在部分错位。	READY
1150_prefl	1150	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-02	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1150_facelift	1150	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1157_prefl	1157	Sedan	Audi 100 C2	Typ 43		EU-AUDI-100-C2-SEDAN-PREFL-01	HIGH	同一Ktype跨1979年改款，按前后期外廓拆分。	READY
1157_facelift	1157	Sedan	Audi 100 C2 facelift	Typ 43	4	EU-AUDI-100-C2-SEDAN-FACELIFT-01	HIGH	同一Ktype跨1979年改款，按前后期外廓拆分。	READY
1160_c2	1160	Sedan	Audi 100 C2 facelift	Typ 43	4	EU-AUDI-100-C2-SEDAN-FACELIFT-01	HIGH	同一Ktype跨C2与C3代际，按代际外廓拆分。	READY
1160_c3	1160	Sedan	Audi 100 C3	Typ 44	4	EU-AUDI-100-C3-SEDAN-01	HIGH	同一Ktype跨C2与C3代际，按代际外廓拆分。	READY
```

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421	Auto-Data Audi 100 C1 facelift 1.6 L; Auto-Data Audi 100 C1 facelift 1.8 LS; Auto-Data Audi 100 C1 facelift 1.9 GL	https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.6-l-85hp-4168; https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.8-ls-100hp-27119; https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.9-gl-112hp-27129
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421	Auto-Data Audi 100 C1 1.8 85 hp	https://www.auto-data.net/en/audi-100-c1-1.8-85hp-4171
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421	Auto-Data Audi 100 C1 facelift 1.8 85 hp	https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.8-85hp-27064
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421	Auto-Data Audi 100 C1 1.8 LS; Auto-Data Audi 100 C1 1.9 GL	https://www.auto-data.net/en/audi-100-c1-1.8-ls-100hp-4169; https://www.auto-data.net/en/audi-100-c1-1.9-gl-112hp-4174
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390	Auto-Data Audi 100 C2 Typ 43 1.6 L	https://www.auto-data.net/en/audi-100-c2-typ-43-1.6-l-85hp-4156
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390	Auto-Data Audi 100 C2 facelift 1.6 L; Auto-Data Audi 100 C2 facelift 1.9	https://www.auto-data.net/en/audi-100-c2-typ-43-facelift-1979-1.6-l-85hp-27140; https://www.auto-data.net/en/audi-100-c2-typ-43-facelift-1979-1.9-100hp-4157
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422	Auto-Data Audi 100 C3 Typ 44 1.9	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-1.9-100hp-4103
```

## 5. 下一步优先处理

1. 仅处理 Ford Transit Bus Ktype `1154`、`1163`、`1170`，优先反查其 Ford 车型代码、轴距和车顶高度。
2. 若能确认覆盖多个物理外廓，则一次性建立 SWB/LWB、低顶/中高顶派生映射及对应尺寸组。
3. 不重新检查已经闭合的 Audi、Opel、BMW、Cadillac 和 Alpina 尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-100-c1-1.8-85hp-4171 "Audi 100 (C1) 1.8 (85 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/audi-100-c2-typ-43-1.6-l-85hp-4156 "Audi 100 (C2, Typ 43) 1.6 L (85 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.transitcenter.uk/transit-mk3-data-specification.php?srsltid=AfmBOor7t-9Qm2oZgh7mTtdEMe9kAZcMNinvhWSTGmPirJOhrtbYmOUE "FORD TRANSIT MK3 - SPECIFICATIONS"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1. 更新点

* 已确认 `1154` 覆盖 `EBS / EDS / EGL / ESS / EUS`，`1163` 覆盖 `EBS / EBL / ECL / EDS / EDL / ESS / EUS`，`1170` 覆盖 `ECL / EDS / EDL / EGL / ESS / EUS`，三个 Ktype 均不是单一车身代码。([AUTODOC UK][1])
* 车型代码资料已确认其中同时存在短车身 `S` 与长车身 `L` 分支；同期规格资料还显示不同载荷等级和车顶高度会造成不同整车高度。([Die Versicherer][2])
* 现有证据仍无法将每个 `E**` 代码无歧义对应到具体轴距、车顶和完整三维，因此本轮不创建猜测性派生行或尺寸组。
* 已闭合的 27 个尺寸组未重新核对或重复输出。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：97
* PENDING 输入 Ktype：3
* READY 映射行：109
* PENDING 映射行：3
* 已确认尺寸组：27
* 当前批次尚未完成。

## 3. 本轮新增/修改的 Ktype 映射 TSV

无

## 4. 本轮首次创建/修正的 DIMENSION_GROUP TSV

无

## 5. 下一步优先处理

1. 优先查找能够直接解码 `EBS / EBL / ECL / EDS / EDL / EGL / ESS / EUS` 与轴距、车顶、载荷等级关系的 Ford 原厂车型代码表或认证资料。
2. 解码完成后，一次性为 `1154`、`1163`、`1170` 建立全部确定的物理分支及尺寸组。
3. 不重新检查其余 97 个 READY Ktype 和既有 27 个尺寸组。

推进信号：CONTINUE

[1]: https://www.autodoc.co.uk/car-parts/glow-plug-10252/ford/transit/transit-bus-e-1991/1154-2-5-di-ebs-eds-egl-ess-eus?utm_source=chatgpt.com "FORD Transit Mk3 Minibus (VE64) 2.5 DI Glow plugs"
[2]: https://www.dieversicherer.de/typklassen/versicherer/Ford_Transit-hsn-0928-tsn-796?utm_source=chatgpt.com "Typklasse für Ford Transit (HSN: 0928, TSN: 796)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1101-1200_ktype_dimension_mapping_final.tsv
- all_1101-1200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1. 更新点

* 已消除剩余 3 个 Ford Transit Bus PENDING。
* Ktype `1154`、`1163`、`1170` 已根据登记车型中的 `80/100/120/150S` 与 `100L` 分支拆分，并链接至短轴或长轴标准顶尺寸组；映射置信度设为 `MEDIUM`。([Die Versicherer][1])
* 已完成固定表头、唯一主键、外键闭合、正整数三维、来源及下载文件检查。
* 未重新核对已经闭合的其他尺寸组。

## 2. 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：100
* PENDING 输入 Ktype：0
* 最终映射行：118
* 最终尺寸组：31
* 映射缺失尺寸组：0
* 孤立尺寸组：0
* 当前批次已完成。

## 3. 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1131	1131	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	MEDIUM	16V版本资料不完整；B3四门轿车外廓已确认。	READY
1132	1132	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1133	1133	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1134	1134	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1135	1135	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1136	1136	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1137	1137	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1138	1138	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1139	1139	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1140	1140	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	HIGH		READY
1141	1141	Sedan	Audi 80 B3		4	EU-AUDI-80-B3-SEDAN-01	MEDIUM	16V版本资料不完整；B3四门轿车外廓已确认。	READY
1142	1142	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1143	1143	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1144	1144	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1145	1145	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1146	1146	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	HIGH		READY
1147_prefl	1147	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-01	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1147_facelift	1147	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-01	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1148	1148	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1149_prefl	1149	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-02	MEDIUM	同一Ktype跨1973年改款；输入年段与规格页存在部分错位。	READY
1149_facelift	1149	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	MEDIUM	同一Ktype跨1973年改款；输入年段与规格页存在部分错位。	READY
1150_prefl	1150	Sedan	Audi 100 C1	C1		EU-AUDI-100-C1-SEDAN-PREFL-02	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1150_facelift	1150	Sedan	Audi 100 C1 facelift	C1	4	EU-AUDI-100-C1-SEDAN-FACELIFT-02	HIGH	同一Ktype跨1973年改款，按前后期外廓拆分。	READY
1151	1151	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1152	1152	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1153	1153	Coupe	Rekord D		2	EU-OPEL-REKORD-D-COUPE-01	HIGH		READY
1154_100s	1154	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	MEDIUM	100S短轴标准顶物理分支。	READY
1154_150s	1154	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	MEDIUM	150S短轴标准顶物理分支。	READY
1154_100l	1154	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	MEDIUM	100L长轴标准顶物理分支。	READY
1155	1155	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1156	1156	Sedan	Rekord D			EU-OPEL-REKORD-D-SEDAN-01	HIGH		READY
1157_prefl	1157	Sedan	Audi 100 C2	Typ 43		EU-AUDI-100-C2-SEDAN-PREFL-01	HIGH	同一Ktype跨1979年改款，按前后期外廓拆分。	READY
1157_facelift	1157	Sedan	Audi 100 C2 facelift	Typ 43	4	EU-AUDI-100-C2-SEDAN-FACELIFT-01	HIGH	同一Ktype跨1979年改款，按前后期外廓拆分。	READY
1158	1158	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1159	1159	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1160_c2	1160	Sedan	Audi 100 C2 facelift	Typ 43	4	EU-AUDI-100-C2-SEDAN-FACELIFT-01	HIGH	同一Ktype跨C2与C3代际，按代际外廓拆分。	READY
1160_c3	1160	Sedan	Audi 100 C3	Typ 44	4	EU-AUDI-100-C3-SEDAN-01	HIGH	同一Ktype跨C2与C3代际，按代际外廓拆分。	READY
1161	1161	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1162	1162	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1163_80_100s	1163	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	MEDIUM	80S/100S短轴标准顶共用外廓。	READY
1163_120s	1163	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	MEDIUM	120S短轴标准顶物理分支。	READY
1163_150s	1163	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	MEDIUM	150S短轴标准顶物理分支。	READY
1163_100l	1163	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	MEDIUM	100L长轴标准顶物理分支。	READY
1164	1164	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1165	1165	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1166	1166	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1167	1167	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1168	1168	Wagon	Rekord D Caravan			EU-OPEL-REKORD-D-WAGON-01	HIGH		READY
1169_prefl	1169	SUV	X6 E71	E71	5	EU-BMW-X6-E71-SUV-PREFL-01	HIGH	同一Ktype跨2012年LCI，按改款前外廓拆分。	READY
1169_facelift	1169	SUV	X6 E71 LCI	E71	5	EU-BMW-X6-E71-SUV-FACELIFT-01	HIGH	同一Ktype跨2012年LCI，按改款后外廓拆分。	READY
1170_150s	1170	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	MEDIUM	150S短轴标准顶物理分支。	READY
1170_100l	1170	MPV	Transit Mk3	VE64		EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	MEDIUM	100L长轴标准顶物理分支。	READY
1171	1171	Coupe	CTS II Coupe		2	EU-CADILLAC-CTS-II-COUPE-V-01	MEDIUM	输入起始年月早于Coupe量产资料；按2011-2014 CTS-V Coupe映射。	READY
1172	1172	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1173	1173	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1174	1174	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1175	1175	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1176	1176	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1177	1177	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1178_prefl	1178	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1178_facelift	1178	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1179_prefl	1179	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1179_facelift	1179	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1180	1180	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1181	1181	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1182	1182	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH		READY
1183_prefl	1183	Sedan	Rekord E1			EU-OPEL-REKORD-E1-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1183_facelift	1183	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1184	1184	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1185	1185	Sedan	Rekord E2			EU-OPEL-REKORD-E2-SEDAN-01	HIGH		READY
1186	1186	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1187	1187	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1188	1188	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1189	1189	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1190	1190	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1191	1191	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1192_prefl	1192	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1192_facelift	1192	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1193_prefl	1193	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1193_facelift	1193	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1194	1194	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1195	1195	Sedan	B3 S Bi-Turbo	E90	4	EU-ALPINA-B3-S-E90-SEDAN-RWD-01	HIGH		READY
1196	1196	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1197	1197	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH		READY
1198_prefl	1198	Wagon	Rekord E1 Caravan			EU-OPEL-REKORD-E1-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E1。	READY
1198_facelift	1198	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH	同一Ktype跨1982年改款，拆分为E2。	READY
1199	1199	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1200	1200	Wagon	Rekord E2 Caravan			EU-OPEL-REKORD-E2-WAGON-01	HIGH		READY
1201	1201	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1202	1202	Wagon	CTS II Sport Wagon		5	EU-CADILLAC-CTS-II-WAGON-01	MEDIUM	203 kW对应资料中的273 hp SAE标注；Wagon量产始于2010年。	READY
1203	1203	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1204	1204	Sedan	B3 S Bi-Turbo	E90	4	EU-ALPINA-B3-S-E90-SEDAN-AWD-01	HIGH		READY
1205	1205	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1206	1206	Wagon	B3 S Bi-Turbo Touring	E91	5	EU-ALPINA-B3-S-E91-WAGON-RWD-01	HIGH		READY
1207	1207	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1208	1208	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1209	1209	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1210	1210	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1211	1211	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1212	1212	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1213	1213	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1214	1214	Coupe	Commodore B		2	EU-OPEL-COMMODORE-B-COUPE-01	HIGH		READY
1215	1215	Sedan	Commodore B			EU-OPEL-COMMODORE-B-SEDAN-01	HIGH		READY
1216	1216	Sedan	Commodore C			EU-OPEL-COMMODORE-C-SEDAN-01	HIGH		READY
1217	1217	Sedan	Commodore C			EU-OPEL-COMMODORE-C-SEDAN-01	HIGH		READY
1218	1218	Wagon	Commodore C Caravan		5	EU-OPEL-COMMODORE-C-WAGON-01	HIGH		READY
1219	1219	Wagon	Commodore C Caravan		5	EU-OPEL-COMMODORE-C-WAGON-01	HIGH		READY
1220	1220	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1221	1221	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1222	1222	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1223	1223	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1224	1224	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1225	1225	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1226	1226	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1227	1227	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1228	1228	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1229	1229	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
1230	1230	Sedan	Omega A		4	EU-OPEL-OMEGA-A-SEDAN-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1101-1200_ktype_dimension_mapping_final.tsv)

## 4. 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-80-B3-SEDAN-01	4393	1695	1397	Auto-Data Audi 80 B3 generation	https://www.auto-data.net/en/audi-80-b3-typ-89-89q-8a-generation-1111
EU-OPEL-REKORD-D-SEDAN-01	4567	1718	1415	Auto-Data Opel Rekord D generation	https://www.auto-data.net/en/opel-rekord-d-generation-535
EU-OPEL-REKORD-D-COUPE-01	4607	1728	1380	Automobile-Catalog 1972 Opel Rekord Coupe 1700 S	https://www.automobile-catalog.com/car/1972/2422535/opel_rekord_coupe_1700_s.html
EU-AUDI-100-C1-SEDAN-FACELIFT-02	4635	1729	1421	Auto-Data Audi 100 C1 facelift 1.6 L; Auto-Data Audi 100 C1 facelift 1.8 LS; Auto-Data Audi 100 C1 facelift 1.9 GL	https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.6-l-85hp-4168; https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.8-ls-100hp-27119; https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.9-gl-112hp-27129
EU-AUDI-100-C1-SEDAN-PREFL-01	4590	1729	1421	Auto-Data Audi 100 C1 1.8 85 hp	https://www.auto-data.net/en/audi-100-c1-1.8-85hp-4171
EU-AUDI-100-C1-SEDAN-FACELIFT-01	4600	1729	1421	Auto-Data Audi 100 C1 facelift 1.8 85 hp	https://www.auto-data.net/en/audi-100-c1-facelift-1973-1.8-85hp-27064
EU-AUDI-100-C1-SEDAN-PREFL-02	4625	1729	1421	Auto-Data Audi 100 C1 1.8 LS; Auto-Data Audi 100 C1 1.9 GL	https://www.auto-data.net/en/audi-100-c1-1.8-ls-100hp-4169; https://www.auto-data.net/en/audi-100-c1-1.9-gl-112hp-4174
EU-FORD-TRANSIT-VE64-MPV-SWB-80-100-01	4616	1974	2021	Ford Transit 1991 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE64-MPV-SWB-150-01	4616	1974	2048	Ford Transit 1991 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-FORD-TRANSIT-VE64-MPV-LWB-100-01	5367	1974	2247	Ford Transit 1991 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-AUDI-100-C2-SEDAN-PREFL-01	4680	1768	1390	Auto-Data Audi 100 C2 Typ 43 1.6 L	https://www.auto-data.net/en/audi-100-c2-typ-43-1.6-l-85hp-4156
EU-AUDI-100-C2-SEDAN-FACELIFT-01	4683	1768	1390	Auto-Data Audi 100 C2 facelift 1.6 L; Auto-Data Audi 100 C2 facelift 1.9	https://www.auto-data.net/en/audi-100-c2-typ-43-facelift-1979-1.6-l-85hp-27140; https://www.auto-data.net/en/audi-100-c2-typ-43-facelift-1979-1.9-100hp-4157
EU-OPEL-REKORD-D-WAGON-01	4594	1715	1440	Auto-Data Opel Rekord D Caravan generation	https://www.auto-data.net/en/opel-rekord-d-caravan-generation-536
EU-AUDI-100-C3-SEDAN-01	4793	1814	1422	Auto-Data Audi 100 C3 Typ 44 1.9	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-1.9-100hp-4103
EU-FORD-TRANSIT-VE64-MPV-SWB-120-01	4616	1974	2024	Ford Transit 1991 UK official brochure	https://autocatalogarchive.com/wp-content/uploads/2026/04/Ford-Transit-1991-UK.pdf
EU-BMW-X6-E71-SUV-PREFL-01	4877	1983	1690	Auto-Data BMW X6 E71 40d specifications	https://www.auto-data.net/en/bmw-x6-e71-40d-306hp-xdrive-steptronic-17311
EU-BMW-X6-E71-SUV-FACELIFT-01	4877	1983	1699	BMW Group PressClub BMW X6 xDrive40d specifications valid from 04/2012	https://www.press.bmwgroup.com/global/article/attachment/T0124596EN/207898
EU-CADILLAC-CTS-II-COUPE-V-01	4788	1882	1422	Car and Driver 2011 Cadillac CTS-V Coupe specifications	https://www.caranddriver.com/cadillac/cts-v/specs/2011/cadillac_cts-v_cadillac-cts-v-coupe_2011
EU-OPEL-REKORD-E1-SEDAN-01	4593	1726	1420	Auto-Data Opel Rekord E generation	https://www.auto-data.net/en/opel-rekord-e-generation-533
EU-OPEL-REKORD-E2-SEDAN-01	4652	1726	1420	Auto-Data Opel Rekord E facelift 1982 generation	https://www.auto-data.net/en/opel-rekord-e-facelift-1982-generation-5163
EU-OPEL-REKORD-E1-WAGON-01	4620	1726	1470	Auto-Data Opel Rekord E Caravan generation	https://www.auto-data.net/en/opel-rekord-e-caravan-generation-534
EU-OPEL-REKORD-E2-WAGON-01	4678	1720	1475	Auto-Data Opel Rekord E Caravan facelift 1982 generation	https://www.auto-data.net/en/opel-rekord-e-caravan-facelift-1982-generation-5162
EU-ALPINA-B3-S-E90-SEDAN-RWD-01	4545	1817	1422	Automobile-Catalog 2010 Alpina B3 S Biturbo	https://www.automobile-catalog.com/car/2010/1339640/alpina_b3_s_biturbo.html
EU-OPEL-COMMODORE-B-SEDAN-01	4607	1728	1415	Auto-Data Opel Commodore B generation	https://www.auto-data.net/en/opel-commodore-b-generation-500
EU-CADILLAC-CTS-II-WAGON-01	4878	1842	1473	Auto-Data Cadillac CTS II Sport Wagon 3.0 V6	https://www.auto-data.net/en/cadillac-cts-ii-sport-wagon-3.0-v6-273hp-automatic-30174
EU-OPEL-COMMODORE-B-COUPE-01	4607	1728	1380	Auto-Data Opel Commodore B Coupe generation	https://www.auto-data.net/en/opel-commodore-b-coupe-generation-501
EU-ALPINA-B3-S-E90-SEDAN-AWD-01	4545	1817	1437	Automobile-Catalog 2010 Alpina B3 S Biturbo Allrad	https://www.automobile-catalog.com/car/2010/1339655/alpina_b3_s_biturbo_allrad.html
EU-ALPINA-B3-S-E91-WAGON-RWD-01	4541	1817	1450	Automobile-Catalog 2010 Alpina B3 S Biturbo Touring	https://www.automobile-catalog.com/car/2010/1339670/alpina_b3_s_biturbo_touring.html
EU-OPEL-COMMODORE-C-SEDAN-01	4705	1730	1410	Auto-Data Opel Commodore C generation	https://www.auto-data.net/en/opel-commodore-c-generation-498
EU-OPEL-COMMODORE-C-WAGON-01	4732	1722	1470	Auto-Data Opel Commodore C Caravan 2.5 E	https://www.auto-data.net/en/opel-commodore-c-caravan-2.5-e-130hp-1831
EU-OPEL-OMEGA-A-SEDAN-01	4770	1810	1445	Auto-Data Opel Omega A generation	https://www.auto-data.net/en/opel-omega-a-generation-515
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1101-1200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.dieversicherer.de/typklassen/versicherer/Ford_Transit "Typklassen für Ford Transit"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1101-1200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1101-1200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1654 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（393 行）
