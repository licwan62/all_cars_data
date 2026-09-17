# 任务：all 第 901-1000 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0010__fe6d785a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 901-1000 行

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
all 第 901-1000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Mercedes-benz	Sl	300 Sl-24	Cabriolet	Heckantrieb	Benzin	170	231	Mar 1989	Jul 1993	2024-03-01	930
Mercedes-benz	Sl	320	Cabriolet	Heckantrieb	Benzin	170	231	Sep 1993	Oct 2001	2024-03-01	931
Ford	Scorpio i	2.4 I	Stufenheck	Heckantrieb	Benzin	92	125	Oct 1988	Oct 1994	2024-03-01	932
Mercedes-benz	Sl	500	Cabriolet	Heckantrieb	Benzin	235	320	Sep 1992	Oct 2001	2024-03-01	933
Mercedes-benz	Sl	500 SL	Cabriolet	Heckantrieb	Benzin	240	326	Sep 1989	Aug 1992	2024-03-01	934
Mercedes-benz	Sl	600	Cabriolet	Heckantrieb	Benzin	290	394	Jul 1992	Oct 2001	2024-03-01	935
Mercedes-benz	G-Klasse	230 GE	Geländewagen geschlossen	Allrad	Benzin	92	125	Jun 1993	Jul 2000	2024-03-01	936
Mercedes-benz	G-Klasse	300 GE	Geländewagen geschlossen	Allrad	Benzin	128	174	Jun 1990	Aug 1997	2024-03-01	937
Mercedes-benz	G-Klasse	290 Gd/g 290 D	Geländewagen geschlossen	Allrad	Diesel	70	95	Jun 1993	Jul 2000	2024-03-01	938
Mercedes-benz	G-Klasse	300 GD	Geländewagen geschlossen	Allrad	Diesel	83	113	Sep 1989	Aug 1993	2024-03-01	939
Mercedes-benz	G-Klasse	230 GE	Geländewagen geschlossen	Allrad	Benzin	90	122	Sep 1989	Jul 1996	2024-03-01	940
Mercedes-benz	G-Klasse	230 GE	Geländewagen geschlossen	Allrad	Benzin	93	126	Jun 1990	Jun 1993	2024-03-01	941
Mercedes-benz	G-Klasse	300 GE	Geländewagen geschlossen	Allrad	Benzin	125	170	Sep 1989	Aug 1993	2024-03-01	942
Ford	Scorpio i	2.4 I CAT	Schrägheck	Heckantrieb	Benzin	92	125	Oct 1988	Sep 1994	2024-03-01	943
Opel	Ascona c cc	2.0 I GT	Schrägheck	Frontantrieb	Benzin	95	130	Mar 1987	Aug 1988	2024-03-01	944
Ford	Scorpio i	2.9 I CAT	Schrägheck	Heckantrieb	Benzin	107	145	Oct 1987	Sep 1994	2024-03-01	945
Opel	Ascona c	1.6 D	Stufenheck	Frontantrieb	Diesel	40	54	Mar 1982	Aug 1988	2024-03-01	946
Opel	Ascona c cc	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Mar 1982	Aug 1988	2024-03-01	947
Ford	Scorpio i	2.9 I 4X4	Stufenheck	Allrad	Benzin	107	145	Dec 1989	Oct 1994	2024-03-01	948
Mercedes-benz	S-Klasse	S 350 Turbo-d	Stufenheck	Heckantrieb	Diesel	110	150	Jan 1993	Oct 1998	2024-03-01	949
Mercedes-benz	S-Klasse	S 280	Stufenheck	Heckantrieb	Benzin	142	193	Feb 1993	Oct 1998	2024-03-01	950
Mercedes-benz	S-Klasse	300 SE 2.8	Stufenheck	Heckantrieb	Benzin	145	197	Jan 1993	Oct 1998	2024-03-01	951
Mercedes-benz	S-Klasse	300 SE, Sel/s320	Stufenheck	Heckantrieb	Benzin	170	231	Mar 1991	Oct 1998	2024-03-01	952
Mercedes-benz	S-Klasse	S 420	Stufenheck	Heckantrieb	Benzin	205	279	Jan 1993	Oct 1998	2024-03-01	953
Mercedes-benz	S-Klasse	400 SE, Sel/s420	Stufenheck	Heckantrieb	Benzin	210	286	Feb 1991	Oct 1998	2024-03-01	954
Mercedes-benz	S-Klasse	S 500	Stufenheck	Heckantrieb	Benzin	235	320	Jan 1993	Oct 1998	2024-03-01	955
Mercedes-benz	S-Klasse	500 SE, SEL	Stufenheck	Heckantrieb	Benzin	240	326	Feb 1991	Oct 1998	2024-03-01	956
Mercedes-benz	S-Klasse	S 600	Stufenheck	Heckantrieb	Benzin	290	394	Jan 1993	Oct 1998	2024-03-01	957
Mercedes-benz	S-Klasse	600 SE, SEL	Stufenheck	Heckantrieb	Benzin	300	408	Apr 1991	Dec 1992	2024-03-01	958
Mercedes-benz	S-Klasse	500 SEC / CL 500	Coupe	Heckantrieb	Benzin	235	320	Oct 1992	Dec 1999	2024-03-01	959
Mercedes-benz	S-Klasse	Sec/cl 600	Coupe	Heckantrieb	Benzin	290	394	Sep 1992	Feb 1999	2024-03-01	960
Ford	Scorpio i	2.9 I 24V	Schrägheck	Heckantrieb	Benzin	143	195	Apr 1991	Sep 1994	2024-03-01	961
Mercedes-benz	C-Klasse	C 200 D	Stufenheck	Heckantrieb	Diesel	55	75	Mar 1993	May 2000	2024-03-01	962
Mercedes-benz	C-Klasse	C 220 D	Stufenheck	Heckantrieb	Diesel	70	95	Aug 1993	May 2000	2024-03-01	963
Mercedes-benz	C-Klasse	C 250 D	Stufenheck	Heckantrieb	Diesel	83	113	May 1993	May 2000	2024-03-01	964
Opel	Vectra a	1.6 I	Stufenheck	Frontantrieb	Benzin	55	75	Sep 1988	Nov 1995	2024-03-01	965
Mercedes-benz	C-Klasse	C 180	Stufenheck	Heckantrieb	Benzin	90	122	Mar 1993	May 2000	2024-03-01	966
Mercedes-benz	C-Klasse	C 220	Stufenheck	Heckantrieb	Benzin	110	150	Mar 1993	May 2000	2024-03-01	967
Mercedes-benz	C-Klasse	C 280	Stufenheck	Heckantrieb	Benzin	142	193	May 1993	May 2000	2024-03-01	968
Mercedes-benz	Coupe	220 SEB	Coupe	Heckantrieb	Benzin	88	120	Jan 1961	Dec 1965	2024-03-01	969
Ford	Scorpio i	2.9 I 24V	Stufenheck	Heckantrieb	Benzin	143	195	Apr 1991	Sep 1994	2024-03-01	970
Mercedes-benz	Coupe	250 SE	Coupe	Heckantrieb	Benzin	110	150	Jan 1965	Dec 1967	2024-03-01	971
Mercedes-benz	Coupe	280 SE	Coupe	Heckantrieb	Benzin	118	160	Jan 1967	Dec 1971	2024-03-01	972
Mercedes-benz	Coupe	280 SE 3.5	Coupe	Heckantrieb	Benzin	147	200	Jan 1969	Dec 1971	2024-03-01	973
Mercedes-benz	Cabriolet	280 SE 3.5	Cabriolet	Heckantrieb	Benzin	147	200	Apr 1968	Dec 1971	2024-03-01	974
Ford	Capri	1700	Coupe	Heckantrieb	Benzin	55	75	Dec 1968	Aug 1972	2025-02-03	975
Mercedes-benz	Sl	280 SLC	Coupe	Heckantrieb	Benzin	130	177	Jun 1976	Sep 1981	2024-03-01	976
Ford	Capri	1.6	Coupe	Heckantrieb	Benzin	50	68	Sep 1974	Dec 1977	2025-02-03	977
Mercedes-benz	Sl	280 SLC	Coupe	Heckantrieb	Benzin	136	185	Aug 1974	Sep 1981	2024-03-01	978
Opel	Vectra a cc	1.6 I CAT	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1988	Nov 1995	2024-03-01	979
Ford	Capri	1.6	Coupe	Heckantrieb	Benzin	53	72	Feb 1974	Dec 1977	2025-02-03	980
Mercedes-benz	Sl	350 SLC	Coupe	Heckantrieb	Benzin	143	195	Mar 1976	Feb 1980	2024-03-01	981
Opel	Vectra a	1.6	Stufenheck	Frontantrieb	Benzin	60	82	Sep 1988	May 1993	2024-03-01	982
Mercedes-benz	Sl	350 SLC	Coupe	Heckantrieb	Benzin	147	200	Jan 1972	Feb 1976	2024-03-01	983
Mercedes-benz	Sl	380 SLC	Coupe	Heckantrieb	Benzin	160	218	Jul 1980	Aug 1981	2024-03-01	984
Opel	Vectra a cc	1.6 S	Schrägheck	Frontantrieb	Benzin	60	82	Sep 1988	May 1993	2024-03-01	985
Opel	Astra j caravan	1.3 Cdti	Kombi	Frontantrieb	Diesel	70	95	Oct 2010	Oct 2014	2024-03-01	986
Ford	Capri	1.6	Coupe	Heckantrieb	Benzin	54	73	Jan 1978	Apr 1987	2025-02-03	987
Mercedes-benz	Sl	450 SLC	Coupe	Heckantrieb	Benzin	165	225	Jan 1973	Nov 1975	2024-03-01	988
Opel	Vectra a	1.8 S	Stufenheck	Frontantrieb	Benzin	65	88	Sep 1988	Jul 1989	2024-03-01	989
Ford	Capri	2	Coupe	Heckantrieb	Benzin	74	101	Jan 1978	Dec 1985	2025-02-03	990
Mercedes-benz	Sl	450 SLC 5.0	Coupe	Heckantrieb	Benzin	177	241	Jun 1978	Feb 1980	2024-03-01	991
Opel	Astra j caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	81	110	Oct 2010	Oct 2015	2024-03-01	992
Opel	Vectra a cc	1.8 S	Schrägheck	Frontantrieb	Benzin	65	88	Sep 1988	Jul 1989	2024-03-01	993
Opel	Vectra a	1.8 S 4X4	Stufenheck	Allrad	Benzin	65	88	Jan 1989	Jul 1989	2024-03-01	994
Ford	Capri	2	Coupe	Heckantrieb	Benzin	66	90	Apr 1976	Dec 1977	2025-02-03	995
Opel	Vectra a cc	2	Schrägheck	Frontantrieb	Benzin	74	100	Apr 1988	Sep 1989	2024-03-01	996
Opel	Vectra a	2	Stufenheck	Frontantrieb	Benzin	74	100	Sep 1988	Sep 1989	2024-03-01	997
Ford	Capri	2.3	Coupe	Heckantrieb	Benzin	79	108	Feb 1974	Dec 1977	2025-02-03	998
Opel	Vectra a	2.0 I	Stufenheck	Frontantrieb	Benzin	85	115	Sep 1988	Oct 1990	2024-03-01	999
Ford	Capri	2.3 Super	Coupe	Heckantrieb	Benzin	84	114	Jun 1979	Dec 1985	2025-02-03	1000
Opel	Vectra a cc	2.0 I	Schrägheck	Frontantrieb	Benzin	85	115	Sep 1988	Oct 1990	2024-03-01	1001
Ford	Capri	2.8 Super Injection	Coupe	Heckantrieb	Benzin	118	160	Jan 1981	Apr 1987	2025-02-03	1002
Opel	Vectra a	2.0 I 4X4	Stufenheck	Allrad	Benzin	85	115	Jan 1989	Oct 1990	2024-03-01	1003
Ford	Capri	3	Coupe	Heckantrieb	Benzin	101	138	Feb 1974	Dec 1977	2025-02-03	1004
Opel	Vectra a cc	2.0 I GT	Schrägheck	Frontantrieb	Benzin	95	129	Sep 1988	Nov 1995	2024-03-01	1005
Opel	Vectra a	2.0 I	Stufenheck	Frontantrieb	Benzin	95	129	Sep 1988	Sep 1992	2024-03-01	1006
Opel	Vectra a	2.0 I 4X4	Stufenheck	Allrad	Benzin	95	129	Aug 1989	Jul 1992	2024-03-01	1007
Ford	Transit	1.7 FT 100	Bus	Heckantrieb	Benzin	48	65	Apr 1971	Mar 1978	2024-03-01	1008
Opel	Vectra a	1.7 TD	Stufenheck	Frontantrieb	Diesel	60	82	Mar 1990	Nov 1995	2024-03-01	1009
Ford	Transit	1.6	Bus	Heckantrieb	Benzin	48	65	Dec 1977	Oct 1986	2024-03-01	1010
Opel	Vectra a cc	1.7 TD	Schrägheck	Frontantrieb	Diesel	60	82	Mar 1990	Nov 1995	2024-03-01	1011
Opel	Vectra a cc	1.7 D	Schrägheck	Frontantrieb	Diesel	42	57	Sep 1988	Sep 1992	2024-03-01	1012
Opel	Vectra a	1.7 D	Stufenheck	Frontantrieb	Diesel	42	57	Oct 1988	Sep 1992	2024-03-01	1013
Ford	Transit	2	Bus	Heckantrieb	Benzin	57	78	Nov 1977	Oct 1986	2024-03-01	1014
Ford	Transit	2.5 D	Bus	Heckantrieb	Diesel	50	68	Oct 1983	Oct 1986	2024-03-01	1015
Opel	Vectra a	1.8 I CAT	Stufenheck	Frontantrieb	Benzin	66	90	Mar 1990	Nov 1995	2024-03-01	1016
Opel	Vectra a cc	1.8 I CAT	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1990	Nov 1995	2024-03-01	1017
Opel	Vectra a	2000/gt 16V	Stufenheck	Frontantrieb	Benzin	110	150	Jan 1989	Jun 1994	2024-03-01	1018
Opel	Vectra a cc	2.0 I 16V	Schrägheck	Frontantrieb	Benzin	110	150	Feb 1989	Oct 1990	2024-03-01	1019
Ford	Transit	2.4 D	Bus	Heckantrieb	Diesel	46	62	Jan 1978	Dec 1985	2024-08-01	1020
Opel	Astra j caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	92	125	Oct 2010	Oct 2015	2024-03-01	1021
Opel	Vectra a	2000 16V 4X4	Stufenheck	Allrad	Benzin	110	150	Jan 1989	Oct 1990	2024-03-01	1022
Opel	Vectra a	2.0 I Turbo 4X4	Stufenheck	Allrad	Benzin	150	204	Jun 1994	Nov 1995	2024-03-01	1023
Opel	Vectra a cc	2.5 V6	Schrägheck	Frontantrieb	Benzin	125	170	Feb 1993	Nov 1995	2024-03-01	1024
Opel	Vectra a	2.5 V6	Stufenheck	Frontantrieb	Benzin	125	170	Feb 1993	Nov 1995	2024-03-01	1025
Opel	Astra j caravan	2.0 Cdti	Kombi	Frontantrieb	Diesel	118	160	Oct 2010	Oct 2015	2024-03-01	1026
Ford	Transit	1.6	Bus	Heckantrieb	Benzin	46	63	Dec 1985	Jan 1989	2024-03-01	1027
Ford	Transit	2	Bus	Heckantrieb	Benzin	57	78	Nov 1985	Sep 1992	2024-03-01	1028
Jaguar	Xj	5.0 Scv8	Stufenheck	Heckantrieb	Benzin	346	471	Oct 2009	Dec 2019	2025-02-03	1029


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 **Mercedes-Benz SL R129** 的主要外廓边界：普通车型需区分改款前、1995 年第一次改款、1998 年第二次改款；V12 改款前高度独立，但两次改款后的三维一致，可共用一个 V12 改款组。([汽车数据][1])
* 已建立 **Ford Scorpio I 四门 Sedan** 与 **五门 Hatchback** 两个独立尺寸组；两种车身的长度、宽度和高度均不同。([汽车数据][2])
* 已闭合 **Opel Ascona C 四门 Sedan** 尺寸组。([汽车数据][3])
* 已确认 **Opel Astra J Sports Tourer** 改款前后标准外廓不变；页面另列含后视镜宽度，因此落盘的 `1814 mm` 为不含后视镜车身宽度。([汽车数据][4])

## 当前批次进度

* READY 输入 Ktype：**13/100**
* READY 映射行：**18**
* PENDING 输入 Ktype：**87/100**
* 已确认尺寸组：**9**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
930	930	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH		READY
931_prefl	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH	改款前外廓。	READY
931_facelift95	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	HIGH	1995年第一次改款外廓。	READY
931_facelift98	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998年第二次改款外廓。	READY
932	932	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	HIGH	四门三厢外廓。	READY
933_prefl	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH	改款前外廓。	READY
933_facelift95	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	HIGH	1995年第一次改款外廓。	READY
933_facelift98	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998年第二次改款外廓。	READY
934	934	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH		READY
935_prefl	935	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	HIGH	V12改款前外廓。	READY
935_facelift	935	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	HIGH	V12改款后外廓；1995与1998改款三维相同。	READY
943	943	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	HIGH	GGE五门掀背外廓。	READY
945	945	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	HIGH	GGE五门掀背外廓。	READY
946	946	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
986	986	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
992	992	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
1021	1021	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
1026	1026	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303	Auto-Data.net Mercedes-Benz SL R129 300 SL-24	https://www.auto-data.net/en/mercedes-benz-sl-r129-300-sl-24-231hp-automatic-44461
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303	Auto-Data.net Mercedes-Benz SL R129 facelift 1995 SL 320	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1995-sl-320-231hp-automatic-41286
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300	Auto-Data.net Mercedes-Benz SL R129 facelift 1998 SL 320	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1998-sl-320-v6-224hp-automatic-41294
EU-FORD-SCORPIO-I-SEDAN-01	4744	1766	1450	Auto-Data.net Ford Scorpio I 2.4i	https://www.auto-data.net/en/ford-scorpio-i-gae-gge-2.4i-125hp-8158
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296	Auto-Data.net Mercedes-Benz SL R129 600 SL V12	https://www.auto-data.net/en/mercedes-benz-sl-r129-600-sl-v12-394hp-automatic-41274
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296	Auto-Data.net Mercedes-Benz SL R129 facelift 1995 SL 600;Auto-Data.net Mercedes-Benz SL R129 facelift 1998 SL 600	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1995-sl-600-v12-394hp-automatic-41284;https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1998-sl-600-v12-394hp-automatic-40997
EU-FORD-SCORPIO-I-HATCHBACK-01	4669	1760	1440	Auto-Data.net Ford Scorpio I Hatch 2.4i	https://www.auto-data.net/en/ford-scorpio-i-hatch-gge-2.4i-125hp-8174
EU-OPEL-ASCONA-C-SEDAN-01	4366	1668	1395	Auto-Data.net Opel Ascona C 1.6 D	https://www.auto-data.net/en/opel-ascona-c-1.6-d-54hp-2028
EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	4698	1814	1535	Auto-Data.net Opel Astra J Sports Tourer;Auto-Data.net Opel Astra J Sports Tourer facelift 2012	https://www.auto-data.net/en/opel-astra-j-sports-tourer-1.3-cdti-95hp-19424;https://www.auto-data.net/en/opel-astra-j-sports-tourer-facelift-2012-1.3-cdti-95hp-ecotec-19466
```

## 下一步优先处理

1. 拆分 Mercedes-Benz S-Klasse W140/V140 的短轴、长轴及改款高度边界，并单独处理 C140 Coupe。
2. 处理 Mercedes-Benz C-Klasse W202 改款前后及柴油车型不同高度。
3. 批量闭合 Opel Vectra A Sedan/Hatchback，并独立核对 GT、4×4、Turbo 等可能改变外廓的版本。
4. 核对 Mercedes-Benz G-Klasse W463 的 SWB/LWB 和门数边界。
5. 处理 Ford Capri 各代、Ford Transit 不同轴距/车顶，以及 Jaguar XJ X351 改款与轴距分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-sl-r129-300-sl-24-231hp-automatic-44461 "Mercedes-Benz SL (R129) 300 SL-24 (231 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/ford-scorpio-i-gae-gge-2.4i-125hp-8158 "Ford Scorpio I (GAE,GGE) 2.4i (125 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-ascona-c-1.6-d-54hp-2028 "Opel Ascona C 1.6 D (54 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/opel-astra-j-sports-tourer-1.3-cdti-95hp-19424 "Opel Astra J Sports Tourer 1.3 CDTI (95 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新增并闭合 **Opel Vectra A** 四门 Sedan、五门 Hatchback 两个尺寸组；普通版、改款版、4×4、V6、16V 与 Turbo 均保持对应车身组的相同外廓。([汽车数据][1])
* 新增 **Opel Ascona C CC 五门 Hatchback** 尺寸组，并完成两个 Ktype 映射。([汽车数据][2])
* 新增 **Mercedes-Benz W111 Coupe/Cabriolet** 四个尺寸组；220 SEb、六缸 250/280 SE、280 SE 3.5 Coupe 和 Cabriolet 分别落组。([汽车数据][3])
* 新增 **Mercedes-Benz SLC C107** 尺寸组，七个发动机 Ktype 共用同一外廓。([汽车数据][4])
* Ford Scorpio I 新增三个映射，直接复用上一轮已建立的 Sedan 与 Hatchback 尺寸组。([汽车数据][5])

## 当前批次进度

* READY 输入 Ktype：**57/100**
* READY 映射行：**62**
* PENDING 输入 Ktype：**43/100**
* 已确认尺寸组：**17**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
944	944	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
947	947	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
948	948	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	MEDIUM	输入版本期晚于资料所列2.9i 4x4版本期；物理外廓仍属Scorpio I四门。	READY
961	961	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	MEDIUM	输入版本期晚于资料所列2.9i 24V版本期；物理外廓仍属GGE五门。	READY
965	965	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
969	969	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-220SEB-01	HIGH	220 SEb早期外廓。	READY
970	970	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	MEDIUM	输入版本期晚于资料所列2.9i 24V版本期；物理外廓仍属Scorpio I四门。	READY
971	971	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	HIGH	250 SE十四英寸轮系外廓。	READY
972	972	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	HIGH	六缸280 SE与250 SE共用外廓。	READY
973	973	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-280SE35-01	HIGH	V8低格栅改型外廓。	READY
974	974	Convertible	W111 Cabriolet	W111	2	EU-MERCEDES-BENZ-W111-CABRIOLET-280SE35-01	HIGH	280 SE 3.5 Cabriolet外廓。	READY
976	976	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
978	978	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
979	979	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
981	981	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
982	982	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
983	983	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
984	984	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
985	985	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
988	988	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
989	989	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
991	991	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
993	993	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
994	994	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
996	996	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
997	997	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
999	999	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1001	1001	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1003	1003	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1005	1005	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH	普通版与1992年改款版外廓相同。	READY
1006	1006	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1007	1007	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1009	1009	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1011	1011	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1012	1012	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1013	1013	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1016	1016	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1017	1017	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1018	1018	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH	改款前后标准外廓相同。	READY
1019	1019	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1022	1022	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1023	1023	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	MEDIUM	输入终止月晚于资料所列Turbo版本期；外廓仍属改款四门车身。	READY
1024	1024	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1025	1025	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385	Auto-Data.net Opel Ascona C CC 1.6 D;Auto-Data.net Opel Ascona C CC 2.0i GT	https://www.auto-data.net/en/opel-ascona-c-cc-1.6-d-54hp-2044;https://www.auto-data.net/de/opel-ascona-c-cc-2.0i-gt-129hp-2052
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Auto-Data.net Opel Vectra A;Auto-Data.net Opel Vectra A facelift 1992	https://www.auto-data.net/en/opel-vectra-a-generation-544;https://www.auto-data.net/en/opel-vectra-a-facelift-1992-generation-5167
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400	Auto-Data.net Opel Vectra A CC;Auto-Data.net Opel Vectra A CC facelift 1992	https://www.auto-data.net/en/opel-vectra-a-cc-generation-545;https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-generation-5166
EU-MERCEDES-BENZ-W111-COUPE-220SEB-01	4880	1845	1445	Auto-Data.net Mercedes-Benz W111 Coupe 220 SEb	https://www.auto-data.net/en/mercedes-benz-w111-coupe-220-seb-120hp-44705
EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	4880	1845	1420	Auto-Data.net Mercedes-Benz W111 Coupe 250 SE;Auto-Data.net Mercedes-Benz W111 Coupe 280 SE	https://www.auto-data.net/en/mercedes-benz-w111-coupe-250-se-150hp-44707;https://www.auto-data.net/en/mercedes-benz-w111-coupe-280-se-160hp-automatic-44710
EU-MERCEDES-BENZ-W111-COUPE-280SE35-01	4905	1845	1410	Auto-Data.net Mercedes-Benz W111 Coupe 280 SE 3.5	https://www.auto-data.net/en/mercedes-benz-w111-coupe-280-se-3.5-v8-200hp-44711
EU-MERCEDES-BENZ-W111-CABRIOLET-280SE35-01	4905	1845	1435	Auto-Data.net Mercedes-Benz W111 Cabriolet 280 SE 3.5	https://www.auto-data.net/en/mercedes-benz-w111-cabriolet-280-se-3.5-v8-200hp-automatic-43818
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330	Auto-Data.net Mercedes-Benz SLC C107	https://www.auto-data.net/en/mercedes-benz-slc-c107-generation-8623
```

## 下一步优先处理

1. 闭合 Mercedes-Benz S-Klasse W140/V140 的短轴、长轴、V12 高度和改款边界。
2. 闭合 Mercedes-Benz C-Klasse W202 改款前后尺寸组。
3. 拆分 Mercedes-Benz G-Klasse W463 的三门/五门、SWB/LWB 外廓。
4. 补齐 Ford Capri I/II/III、Ford Transit 不同轴距与车顶分支。
5. 最后处理 Jaguar XJ X351 的 SWB/LWB 与改款边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-vectra-a-facelift-1992-generation-5167?utm_source=chatgpt.com "Opel Vectra A (facelift 1992) | Technical Specs, Fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-ascona-c-cc-1.6-d-54hp-2044?utm_source=chatgpt.com "Opel Ascona C CC 1.6 D (54 Hp) /Hatchback 1982"
[3]: https://www.auto-data.net/en/mercedes-benz-w111-coupe-220-seb-120hp-44705?utm_source=chatgpt.com "Mercedes-Benz W111 Coupe 220 SEb (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/mercedes-benz-slc-c107-280-slc-185hp-automatic-44692?utm_source=chatgpt.com "Mercedes-Benz SLC (C107) 280 SLC (185 Hp) Automatic"
[5]: https://www.auto-data.net/en/ford-scorpio-i-hatch-gge-2.9i-24v-195hp-8178?utm_source=chatgpt.com "Ford Scorpio I Hatch (GGE) 2.9i 24V (195 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 1) 更新点

* 已闭合 **G-Klasse W461** 三门短轴与五门长轴尺寸组。Mercedes-Benz 官方档案确认短轴为 `4015×1700×1940 mm`，长轴为 `4465×1700×1945 mm`；230 GE 与 290 GD 可按相同 W461 物理外廓复用。([marsClassic][1])
* 已闭合 **G-Klasse W463** 三门短轴与五门长轴尺寸组，分别为 `4185×1690×1908 mm` 和 `4635×1690×1936 mm`。([汽车数据][2])
* 已闭合 **C-Klasse W202** 的改款前五种高度外廓及 1997 改款尺寸组；C 220 D 与 C 180 跨越改款边界，拆成派生映射。([汽车数据][3])

## 2) 当前批次进度

* READY 输入 Ktype：**70/100**
* READY 映射行：**84**
* PENDING 输入 Ktype：**30/100**
* 已确认尺寸组：**26**
* 当前批次尚未完成。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
936_swb	936	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	MEDIUM	三门短轴分支。	READY
936_lwb	936	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	MEDIUM	五门长轴分支。	READY
937_swb	937	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
937_lwb	937	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
938_swb	938	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
938_lwb	938	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
939_swb	939	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
939_lwb	939	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
940_swb	940	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
940_lwb	940	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
941_swb	941	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
941_lwb	941	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
942_swb	942	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
942_lwb	942	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
962	962	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	HIGH		READY
963_prefl	963	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	HIGH	改款前外廓。	READY
963_facelift	963	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	HIGH	1997年改款外廓。	READY
964	964	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	HIGH		READY
966_prefl	966	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	HIGH	改款前外廓。	READY
966_facelift	966	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	HIGH	1997年改款外廓。	READY
967	967	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1424-01	HIGH		READY
968	968	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1427-01	HIGH		READY
```

## 4) 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	4015	1700	1940	Mercedes-Benz Public Archive 290 GD short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-short-wheelbase-1991---1997.xhtml?oid=191011038
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	4465	1700	1945	Mercedes-Benz Public Archive 230 GE long wheelbase;Mercedes-Benz Public Archive 290 GD long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-GE-long-wheelbase-1992---1996.xhtml?oid=191011044;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-long-wheelbase-1991---1997.xhtml?oid=191011039
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	4185	1690	1908	Auto-Data.net Mercedes-Benz G-Class W463 300 GE	https://www.auto-data.net/en/mercedes-benz-g-class-w463-300-ge-170hp-4matic-automatic-42309
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	4635	1690	1936	Auto-Data.net Mercedes-Benz G-Class Long W463 300 GE	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-300-ge-170hp-4matic-42514
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	4487	1720	1414	Auto-Data.net Mercedes-Benz C-Class W202 C 200 D;Auto-Data.net Mercedes-Benz C-Class W202 C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-200-d-75hp-12645;https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-180-122hp-12643
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	4487	1720	1418	Auto-Data.net Mercedes-Benz C-Class W202 C 220 D;Auto-Data.net Mercedes-Benz C-Class W202 C 250 D	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-220-d-95hp-4g-tronic-44177;https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-250-d-113hp-12656
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1424-01	4487	1720	1424	Auto-Data.net Mercedes-Benz C-Class W202 C 220	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-220-150hp-4g-tronic-44179
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1427-01	4487	1720	1427	Auto-Data.net Mercedes-Benz C-Class W202 C 280	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-280-193hp-12659
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	4516	1723	1427	Auto-Data.net Mercedes-Benz C-Class W202 facelift 1997 C 220 D	https://www.auto-data.net/en/mercedes-benz-c-class-w202-facelift-1997-c-220-d-95hp-12652
```

## 5) 下一步优先处理

1. 闭合 Mercedes-Benz S-Klasse W140/V140 的短轴、长轴、改款前高度差异及 C140 Coupe。
2. 批量闭合 Ford Capri I、Capri II、Capri III 三个代际尺寸组。
3. 拆分 Ford Transit Bus 的代际、轴距和车顶分支。
4. 最后闭合 Jaguar XJ X351 的 SWB/LWB 分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-short-wheelbase-1991---1997.xhtml?oid=191011038 "290 GD (short wheelbase), 1991 - 1997"
[2]: https://www.auto-data.net/en/mercedes-benz-g-class-w463-230-ge-126hp-4matic-42271?utm_source=chatgpt.com "Mercedes-Benz G-class (W463) 230 GE (126 Hp) 4MATIC"
[3]: https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-200-d-75hp-12645?utm_source=chatgpt.com "Mercedes-Benz C-class (W202) C 200 D (75 Hp)"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 1) 更新点

* 已闭合 Mercedes-Benz S-Klasse W140/V140：区分短轴、长轴、1993 年 6 月前后，以及六缸/V8/V12 不同高度边界。Mercedes-Benz 官方档案明确给出了各车身在 1993 年 6 月前后的高度变化。([梅賽德斯-奔驰档案馆][1])
* 已闭合 C140 Coupe；CL 500 与 CL 600 长宽相同但高度不同，因此建立两个尺寸组。([汽车数据网][2])
* 已闭合 Ford Capri I、II、III 三代尺寸组，并完成本批全部 Capri Ktype 映射。([福特卡普里][3])
* 已闭合 Jaguar XJ X351 346 kW/470 hp 的短轴与长轴分支；该动力规格资料对应 2009–2012 年外廓，因此未创建猜测性的后期改款分支。([汽车数据网][4])

## 2) 当前批次进度

* READY 输入 Ktype：**93/100**
* READY 映射行：**123**
* PENDING 输入 Ktype：**7/100**
* 已确认尺寸组：**43**
* 剩余 PENDING 全部为 Ford Transit Bus。

## 3) 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
949	949	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	MEDIUM		READY
950_pre93	950	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	1993年6月前外廓。	READY
950_post93	950	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
951_pre93	951	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	1993年6月前外廓。	READY
951_post93	951	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
952_swb_pre93	952	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	短轴，1993年6月前。	READY
952_lwb_pre93	952	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-6CYL-PRE93-01	HIGH	长轴，1993年6月前。	READY
952_swb_post93	952	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
952_lwb_post93	952	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
953_pre93	953	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	1993年6月前外廓。	READY
953_post93	953	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
954_swb_pre93	954	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	短轴，1993年6月前。	READY
954_lwb_pre93	954	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	HIGH	长轴，1993年6月前。	READY
954_swb_post93	954	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
954_lwb_post93	954	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
955_pre93	955	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	1993年6月前外廓。	READY
955_post93	955	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
956_swb_pre93	956	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	短轴，1993年6月前。	READY
956_lwb_pre93	956	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	HIGH	长轴，1993年6月前。	READY
956_swb_post93	956	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
956_lwb_post93	956	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
957_pre93	957	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	HIGH	1993年6月前V12外廓。	READY
957_post93	957	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-POST93-01	HIGH	1993年6月后V12外廓。	READY
958_swb	958	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	HIGH	短轴V12外廓。	READY
958_lwb	958	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V12-PRE93-01	HIGH	长轴V12外廓。	READY
959	959	Coupe	S-Class Coupe C140	C140	2	EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V8-01	HIGH		READY
960	960	Coupe	S-Class Coupe C140	C140	2	EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V12-01	HIGH		READY
975	975	Coupe	Capri I		2	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
977	977	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
980	980	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
987	987	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
990	990	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
995	995	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
998	998	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
1000	1000	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
1002	1002	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
1004	1004	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
1029_swb	1029	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	MEDIUM	短轴分支。	READY
1029_lwb	1029	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	MEDIUM	长轴分支。	READY
```

## 4) 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	5113	1886	1492	Mercedes-Benz Public Archive 300 SE / S 320	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SE-from-061993-S-320.xhtml?oid=4928
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-6CYL-PRE93-01	5213	1886	1492	Mercedes-Benz Public Archive 300 SEL / S 320 long wheelbase	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SEL-from-061993-S-320-long-wheelbase.xhtml?oid=4930
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	5113	1886	1495	Mercedes-Benz Public Archive 500 SE / S 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SE-from-061993-S-500.xhtml?oid=4925
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	5213	1886	1495	Mercedes-Benz Public Archive 500 SEL / S 500 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEL-from-061993-S-500-long-wheelbase.xhtml?oid=4932
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	5113	1886	1491	Mercedes-Benz Public Archive 600 SE / S 600	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SE-from-061993-S-600.xhtml?oid=4933
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V12-PRE93-01	5213	1886	1491	Mercedes-Benz Public Archive 600 SEL / S 600 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SEL-from-061993-S-600-long-wheelbase.xhtml?oid=4934
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	5113	1886	1486	Mercedes-Benz Public Archive 300 SE / S 320;Mercedes-Benz Public Archive 500 SE / S 500	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SE-from-061993-S-320.xhtml?oid=4928;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SE-from-061993-S-500.xhtml?oid=4925
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	5213	1886	1486	Mercedes-Benz Public Archive 300 SEL / S 320 long wheelbase;Mercedes-Benz Public Archive 500 SEL / S 500 long wheelbase	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SEL-from-061993-S-320-long-wheelbase.xhtml?oid=4930;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEL-from-061993-S-500-long-wheelbase.xhtml?oid=4932
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-POST93-01	5113	1886	1482	Mercedes-Benz Public Archive 600 SE / S 600	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SE-from-061993-S-600.xhtml?oid=4933
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V12-POST93-01	5213	1886	1482	Mercedes-Benz Public Archive 600 SEL / S 600 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SEL-from-061993-S-600-long-wheelbase.xhtml?oid=4934
EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V8-01	5065	1912	1452	Auto-Data.net Mercedes-Benz CL C140 CL 500 V8	https://www.auto-data.net/en/mercedes-benz-cl-c140-cl-500-v8-320hp-automatic-12720
EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V12-01	5065	1912	1478	Auto-Data.net Mercedes-Benz CL C140 CL 600 V12	https://www.auto-data.net/en/mercedes-benz-cl-c140-cl-600-v12-394hp-automatic-12721
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330	Capri Switzerland Ford Capri Mk I technical data	https://www.ford-capri.ch/technics/technical-data-I/1600gt-69-72-e.html
EU-FORD-CAPRI-II-COUPE-01	4286	1695	1295	UltimateSpecs Ford Capri Mk II	https://www.ultimatespecs.com/car-specs/Ford/M14131/Capri-Mk-II
EU-FORD-CAPRI-III-COUPE-01	4440	1700	1350	Auto-Data.net Ford Capri III GECP	https://www.auto-data.net/en/ford-capri-iii-gecp-generation-1728
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457	Auto-Data.net Jaguar XJ X351 5.0 V8 Supercharged 470 Hp	https://www.auto-data.net/en/jaguar-xj-x351-5.0-v8-supercharged-470hp-automatic-6-speed-17473
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457	Auto-Data.net Jaguar XJ Long X351 5.0 V8 Supercharged 470 Hp	https://www.auto-data.net/en/jaguar-xj-long-x351-5.0-v8-supercharged-470hp-automatic-6-speed-51395
```

## 5) 下一步优先处理

1. 闭合 Ktype `1008` 的第一代 Ford Transit FT 100 Bus 轴距与车顶分支。
2. 聚类处理 Ktype `1010`、`1014`、`1015`、`1020` 的 1977–1986 Transit Bus。
3. 处理 Ktype `1027`、`1028` 的 1985–1992 Transit 改款代际。
4. Transit 全部闭合后立即执行一次机械收尾，并输出两张最终完整 TSV 与指定下载链接。

推进信号：CONTINUE

[1]: https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SE-from-061993-S-320.xhtml?oid=4928 "300 SE; from 06.1993: S 320"
[2]: https://www.auto-data.net/en/mercedes-benz-cl-c140-cl-500-v8-320hp-automatic-12720 "Mercedes-Benz CL (C140) CL 500 V8 (320 Hp) Automatic | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.ford-capri.ch/technics/technical-data-I/1600gt-69-72-e.html "Technical data Ford Capri Mk I - 1600 GT (1969-1972)"
[4]: https://www.auto-data.net/en/jaguar-xj-x351-5.0-v8-supercharged-470hp-automatic-6-speed-17473 "Jaguar XJ (X351) 5.0 V8 Supercharged (470 Hp) Automatic 6-speed | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_901-1000_ktype_dimension_mapping_final.tsv
- all_901-1000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 1) 更新点

* 已闭合剩余 7 个 Ford Transit Ktype：Mk1 FT100 落入短轴低顶组；Mk2 Bus 按短轴低顶与长轴高顶拆分；VE6 Bus 按短轴/长轴以及 1992 年改款前后拆分。([Transit Center Ford Transit Spare Parts][1])
* 已完成轻量机械收尾：固定表头正确，`id` 与 `DIMENSION_GROUP_ID` 唯一，100 个输入 Ktype 全覆盖，映射外键全部闭合，无孤立尺寸组，三维及来源字段均非空。
* 删除了未被当前映射引用的孤立尺寸组，未修改任何已被引用的尺寸事实。

## 2) 当前批次进度

* READY 输入 Ktype：**100/100**
* READY 映射行：**138**
* PENDING 输入 Ktype：**0/100**
* 最终尺寸组：**49**
* 当前批次已完成。

## 3) 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
930	930	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH		READY
931_prefl	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH	改款前外廓。	READY
931_facelift95	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	HIGH	1995年第一次改款外廓。	READY
931_facelift98	931	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998年第二次改款外廓。	READY
932	932	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	HIGH	四门三厢外廓。	READY
933_prefl	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH	改款前外廓。	READY
933_facelift95	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	HIGH	1995年第一次改款外廓。	READY
933_facelift98	933	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	HIGH	1998年第二次改款外廓。	READY
934	934	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	HIGH		READY
935_prefl	935	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	HIGH	V12改款前外廓。	READY
935_facelift	935	Convertible	SL R129	R129	2	EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	HIGH	V12改款后外廓；1995与1998改款三维相同。	READY
936_swb	936	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	MEDIUM	三门短轴分支。	READY
936_lwb	936	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	MEDIUM	五门长轴分支。	READY
937_swb	937	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
937_lwb	937	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
938_swb	938	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
938_lwb	938	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
939_swb	939	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
939_lwb	939	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
940_swb	940	SUV	G-Class W461	W461	3	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
940_lwb	940	SUV	G-Class W461	W461	5	EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
941_swb	941	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
941_lwb	941	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
942_swb	942	SUV	G-Class W463	W463	3	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	HIGH	三门短轴分支。	READY
942_lwb	942	SUV	G-Class W463	W463	5	EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	HIGH	五门长轴分支。	READY
943	943	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	HIGH	GGE五门掀背外廓。	READY
944	944	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
945	945	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	HIGH	GGE五门掀背外廓。	READY
946	946	Sedan	Ascona C		4	EU-OPEL-ASCONA-C-SEDAN-01	HIGH		READY
947	947	Hatchback	Ascona C CC		5	EU-OPEL-ASCONA-C-CC-HATCHBACK-01	HIGH		READY
948	948	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	MEDIUM	输入版本期晚于资料所列2.9i 4x4版本期；物理外廓仍属Scorpio I四门。	READY
949	949	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	MEDIUM		READY
950_pre93	950	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	1993年6月前外廓。	READY
950_post93	950	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
951_pre93	951	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	1993年6月前外廓。	READY
951_post93	951	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
952_swb_pre93	952	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	HIGH	短轴，1993年6月前。	READY
952_lwb_pre93	952	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-6CYL-PRE93-01	HIGH	长轴，1993年6月前。	READY
952_swb_post93	952	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
952_lwb_post93	952	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
953_pre93	953	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	1993年6月前外廓。	READY
953_post93	953	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
954_swb_pre93	954	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	短轴，1993年6月前。	READY
954_lwb_pre93	954	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	HIGH	长轴，1993年6月前。	READY
954_swb_post93	954	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
954_lwb_post93	954	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
955_pre93	955	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	1993年6月前外廓。	READY
955_post93	955	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	1993年6月后外廓。	READY
956_swb_pre93	956	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	HIGH	短轴，1993年6月前。	READY
956_lwb_pre93	956	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	HIGH	长轴，1993年6月前。	READY
956_swb_post93	956	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	HIGH	短轴，1993年6月后。	READY
956_lwb_post93	956	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	HIGH	长轴，1993年6月后。	READY
957_pre93	957	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	HIGH	1993年6月前V12外廓。	READY
957_post93	957	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-POST93-01	HIGH	1993年6月后V12外廓。	READY
958_swb	958	Sedan	S-Class W140	W140	4	EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	HIGH	短轴V12外廓。	READY
958_lwb	958	Sedan	S-Class V140	V140	4	EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V12-PRE93-01	HIGH	长轴V12外廓。	READY
959	959	Coupe	S-Class Coupe C140	C140	2	EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V8-01	HIGH		READY
960	960	Coupe	S-Class Coupe C140	C140	2	EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V12-01	HIGH		READY
961	961	Hatchback	Scorpio I	GGE	5	EU-FORD-SCORPIO-I-HATCHBACK-01	MEDIUM	输入版本期晚于资料所列2.9i 24V版本期；物理外廓仍属GGE五门。	READY
962	962	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	HIGH		READY
963_prefl	963	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	HIGH	改款前外廓。	READY
963_facelift	963	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	HIGH	1997年改款外廓。	READY
964	964	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	HIGH		READY
965	965	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
966_prefl	966	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	HIGH	改款前外廓。	READY
966_facelift	966	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	HIGH	1997年改款外廓。	READY
967	967	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1424-01	HIGH		READY
968	968	Sedan	C-Class W202	W202	4	EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1427-01	HIGH		READY
969	969	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-220SEB-01	HIGH	220 SEb早期外廓。	READY
970	970	Sedan	Scorpio I		4	EU-FORD-SCORPIO-I-SEDAN-01	MEDIUM	输入版本期晚于资料所列2.9i 24V版本期；物理外廓仍属Scorpio I四门。	READY
971	971	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	HIGH	250 SE十四英寸轮系外廓。	READY
972	972	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	HIGH	六缸280 SE与250 SE共用外廓。	READY
973	973	Coupe	W111 Coupe	W111	2	EU-MERCEDES-BENZ-W111-COUPE-280SE35-01	HIGH	V8低格栅改型外廓。	READY
974	974	Convertible	W111 Cabriolet	W111	2	EU-MERCEDES-BENZ-W111-CABRIOLET-280SE35-01	HIGH	280 SE 3.5 Cabriolet外廓。	READY
975	975	Coupe	Capri I		2	EU-FORD-CAPRI-I-COUPE-01	HIGH		READY
976	976	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
977	977	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
978	978	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
979	979	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
980	980	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
981	981	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
982	982	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
983	983	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
984	984	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
985	985	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
986	986	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
987	987	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
988	988	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
989	989	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
990	990	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
991	991	Coupe	SLC C107	C107	2	EU-MERCEDES-BENZ-SLC-C107-COUPE-01	HIGH		READY
992	992	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
993	993	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
994	994	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
995	995	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
996	996	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
997	997	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
998	998	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
999	999	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1000	1000	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
1001	1001	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1002	1002	Coupe	Capri III	GECP	3	EU-FORD-CAPRI-III-COUPE-01	HIGH		READY
1003	1003	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1004	1004	Coupe	Capri II	GECP	3	EU-FORD-CAPRI-II-COUPE-01	HIGH		READY
1005	1005	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH	普通版与1992年改款版外廓相同。	READY
1006	1006	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1007	1007	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1008	1008	MPV	Transit Mk1		4	EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	MEDIUM	1.7 FT100为短轴Bus外廓。	READY
1009	1009	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1010_swb	1010	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴Bus分支。	READY
1010_lwb	1010	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴Bus分支。	READY
1011	1011	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1012	1012	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1013	1013	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1014_swb	1014	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴Bus分支。	READY
1014_lwb	1014	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴Bus分支。	READY
1015_swb	1015	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴Bus分支。	READY
1015_lwb	1015	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴Bus分支。	READY
1016	1016	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1017	1017	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1018	1018	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH	改款前后标准外廓相同。	READY
1019	1019	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1020_swb	1020	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	MEDIUM	短轴Bus分支。	READY
1020_lwb	1020	MPV	Transit Mk2		4	EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	MEDIUM	长轴Bus分支。	READY
1021	1021	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
1022	1022	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1023	1023	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	MEDIUM	输入终止月晚于资料所列Turbo版本期；外廓仍属改款四门车身。	READY
1024	1024	Hatchback	Vectra A		5	EU-OPEL-VECTRA-A-HATCHBACK-01	HIGH		READY
1025	1025	Sedan	Vectra A		4	EU-OPEL-VECTRA-A-SEDAN-01	HIGH		READY
1026	1026	Wagon	Astra J Sports Tourer		5	EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	HIGH		READY
1027_swb	1027	MPV	Transit VE6		4	EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	MEDIUM	短轴低顶Bus分支。	READY
1027_lwb	1027	MPV	Transit VE6		4	EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	MEDIUM	长轴Bus分支。	READY
1028_swb_pre92	1028	MPV	Transit VE6		4	EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	MEDIUM	1992年改款前短轴Bus。	READY
1028_lwb_pre92	1028	MPV	Transit VE6		4	EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	MEDIUM	1992年改款前长轴Bus。	READY
1028_swb_post92	1028	MPV	Transit VE6 facelift		4	EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	MEDIUM	1992年改款后短轴Bus。	READY
1028_lwb_post92	1028	MPV	Transit VE6 facelift		4	EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	MEDIUM	1992年改款后长轴Bus。	READY
1029_swb	1029	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	MEDIUM	短轴分支。	READY
1029_lwb	1029	Sedan	XJ X351	X351	4	EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	MEDIUM	长轴分支。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_901-1000_ktype_dimension_mapping_final.tsv)

## 4) 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-STD-01	4470	1812	1303	Auto-Data.net Mercedes-Benz SL R129 300 SL-24	https://www.auto-data.net/en/mercedes-benz-sl-r129-300-sl-24-231hp-automatic-44461
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT95-STD-01	4499	1812	1303	Auto-Data.net Mercedes-Benz SL R129 facelift 1995 SL 320	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1995-sl-320-231hp-automatic-41286
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT98-STD-01	4499	1812	1300	Auto-Data.net Mercedes-Benz SL R129 facelift 1998 SL 320	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1998-sl-320-v6-224hp-automatic-41294
EU-FORD-SCORPIO-I-SEDAN-01	4744	1766	1450	Auto-Data.net Ford Scorpio I 2.4i	https://www.auto-data.net/en/ford-scorpio-i-gae-gge-2.4i-125hp-8158
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-PREFL-V12-01	4470	1812	1296	Auto-Data.net Mercedes-Benz SL R129 600 SL V12	https://www.auto-data.net/en/mercedes-benz-sl-r129-600-sl-v12-394hp-automatic-41274
EU-MERCEDES-BENZ-SL-R129-CONVERTIBLE-FACELIFT-V12-01	4499	1812	1296	Auto-Data.net Mercedes-Benz SL R129 facelift 1995 SL 600;Auto-Data.net Mercedes-Benz SL R129 facelift 1998 SL 600	https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1995-sl-600-v12-394hp-automatic-41284;https://www.auto-data.net/en/mercedes-benz-sl-r129-facelift-1998-sl-600-v12-394hp-automatic-40997
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-SWB-3D-01	4015	1700	1940	Mercedes-Benz Public Archive 290 GD short wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-short-wheelbase-1991---1997.xhtml?oid=191011038
EU-MERCEDES-BENZ-G-CLASS-W461-SUV-LWB-5D-01	4465	1700	1945	Mercedes-Benz Public Archive 230 GE long wheelbase;Mercedes-Benz Public Archive 290 GD long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-GE-long-wheelbase-1992---1996.xhtml?oid=191011044;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/290-GD-long-wheelbase-1991---1997.xhtml?oid=191011039
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-SWB-3D-01	4185	1690	1908	Auto-Data.net Mercedes-Benz G-Class W463 300 GE	https://www.auto-data.net/en/mercedes-benz-g-class-w463-300-ge-170hp-4matic-automatic-42309
EU-MERCEDES-BENZ-G-CLASS-W463-SUV-LWB-5D-01	4635	1690	1936	Auto-Data.net Mercedes-Benz G-Class Long W463 300 GE	https://www.auto-data.net/en/mercedes-benz-g-class-long-w463-300-ge-170hp-4matic-42514
EU-FORD-SCORPIO-I-HATCHBACK-01	4669	1760	1440	Auto-Data.net Ford Scorpio I Hatch 2.4i	https://www.auto-data.net/en/ford-scorpio-i-hatch-gge-2.4i-125hp-8174
EU-OPEL-ASCONA-C-CC-HATCHBACK-01	4264	1668	1385	Auto-Data.net Opel Ascona C CC 1.6 D;Auto-Data.net Opel Ascona C CC 2.0i GT	https://www.auto-data.net/en/opel-ascona-c-cc-1.6-d-54hp-2044;https://www.auto-data.net/de/opel-ascona-c-cc-2.0i-gt-129hp-2052
EU-OPEL-ASCONA-C-SEDAN-01	4366	1668	1395	Auto-Data.net Opel Ascona C 1.6 D	https://www.auto-data.net/en/opel-ascona-c-1.6-d-54hp-2028
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-POST93-01	5113	1886	1486	Mercedes-Benz Public Archive 300 SE / S 320;Mercedes-Benz Public Archive 500 SE / S 500	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SE-from-061993-S-320.xhtml?oid=4928;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SE-from-061993-S-500.xhtml?oid=4925
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-6CYL-PRE93-01	5113	1886	1492	Mercedes-Benz Public Archive 300 SE / S 320	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SE-from-061993-S-320.xhtml?oid=4928
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-6CYL-PRE93-01	5213	1886	1492	Mercedes-Benz Public Archive 300 SEL / S 320 long wheelbase	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SEL-from-061993-S-320-long-wheelbase.xhtml?oid=4930
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-POST93-01	5213	1886	1486	Mercedes-Benz Public Archive 300 SEL / S 320 long wheelbase;Mercedes-Benz Public Archive 500 SEL / S 500 long wheelbase	https://mercedes-benz-archive.com/marsClassic/en/instance/ko/300-SEL-from-061993-S-320-long-wheelbase.xhtml?oid=4930;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEL-from-061993-S-500-long-wheelbase.xhtml?oid=4932
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V8-PRE93-01	5113	1886	1495	Mercedes-Benz Public Archive 500 SE / S 500	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SE-from-061993-S-500.xhtml?oid=4925
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V8-PRE93-01	5213	1886	1495	Mercedes-Benz Public Archive 500 SEL / S 500 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/500-SEL-from-061993-S-500-long-wheelbase.xhtml?oid=4932
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-PRE93-01	5113	1886	1491	Mercedes-Benz Public Archive 600 SE / S 600	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SE-from-061993-S-600.xhtml?oid=4933
EU-MERCEDES-BENZ-S-CLASS-W140-SEDAN-SWB-V12-POST93-01	5113	1886	1482	Mercedes-Benz Public Archive 600 SE / S 600	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SE-from-061993-S-600.xhtml?oid=4933
EU-MERCEDES-BENZ-S-CLASS-V140-SEDAN-LWB-V12-PRE93-01	5213	1886	1491	Mercedes-Benz Public Archive 600 SEL / S 600 long wheelbase	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/600-SEL-from-061993-S-600-long-wheelbase.xhtml?oid=4934
EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V8-01	5065	1912	1452	Auto-Data.net Mercedes-Benz CL C140 CL 500 V8	https://www.auto-data.net/en/mercedes-benz-cl-c140-cl-500-v8-320hp-automatic-12720
EU-MERCEDES-BENZ-S-CLASS-C140-COUPE-V12-01	5065	1912	1478	Auto-Data.net Mercedes-Benz CL C140 CL 600 V12	https://www.auto-data.net/en/mercedes-benz-cl-c140-cl-600-v12-394hp-automatic-12721
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1414-01	4487	1720	1414	Auto-Data.net Mercedes-Benz C-Class W202 C 200 D;Auto-Data.net Mercedes-Benz C-Class W202 C 180	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-200-d-75hp-12645;https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-180-122hp-12643
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1418-01	4487	1720	1418	Auto-Data.net Mercedes-Benz C-Class W202 C 220 D;Auto-Data.net Mercedes-Benz C-Class W202 C 250 D	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-220-d-95hp-4g-tronic-44177;https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-250-d-113hp-12656
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-FACELIFT-H1427-01	4516	1723	1427	Auto-Data.net Mercedes-Benz C-Class W202 facelift 1997 C 220 D	https://www.auto-data.net/en/mercedes-benz-c-class-w202-facelift-1997-c-220-d-95hp-12652
EU-OPEL-VECTRA-A-SEDAN-01	4432	1706	1400	Auto-Data.net Opel Vectra A;Auto-Data.net Opel Vectra A facelift 1992	https://www.auto-data.net/en/opel-vectra-a-generation-544;https://www.auto-data.net/en/opel-vectra-a-facelift-1992-generation-5167
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1424-01	4487	1720	1424	Auto-Data.net Mercedes-Benz C-Class W202 C 220	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-220-150hp-4g-tronic-44179
EU-MERCEDES-BENZ-C-CLASS-W202-SEDAN-PREFL-H1427-01	4487	1720	1427	Auto-Data.net Mercedes-Benz C-Class W202 C 280	https://www.auto-data.net/en/mercedes-benz-c-class-w202-c-280-193hp-12659
EU-MERCEDES-BENZ-W111-COUPE-220SEB-01	4880	1845	1445	Auto-Data.net Mercedes-Benz W111 Coupe 220 SEb	https://www.auto-data.net/en/mercedes-benz-w111-coupe-220-seb-120hp-44705
EU-MERCEDES-BENZ-W111-COUPE-6CYL-14IN-01	4880	1845	1420	Auto-Data.net Mercedes-Benz W111 Coupe 250 SE;Auto-Data.net Mercedes-Benz W111 Coupe 280 SE	https://www.auto-data.net/en/mercedes-benz-w111-coupe-250-se-150hp-44707;https://www.auto-data.net/en/mercedes-benz-w111-coupe-280-se-160hp-automatic-44710
EU-MERCEDES-BENZ-W111-COUPE-280SE35-01	4905	1845	1410	Auto-Data.net Mercedes-Benz W111 Coupe 280 SE 3.5	https://www.auto-data.net/en/mercedes-benz-w111-coupe-280-se-3.5-v8-200hp-44711
EU-MERCEDES-BENZ-W111-CABRIOLET-280SE35-01	4905	1845	1435	Auto-Data.net Mercedes-Benz W111 Cabriolet 280 SE 3.5	https://www.auto-data.net/en/mercedes-benz-w111-cabriolet-280-se-3.5-v8-200hp-automatic-43818
EU-FORD-CAPRI-I-COUPE-01	4262	1646	1330	Capri Switzerland Ford Capri Mk I technical data	https://www.ford-capri.ch/technics/technical-data-I/1600gt-69-72-e.html
EU-MERCEDES-BENZ-SLC-C107-COUPE-01	4750	1790	1330	Auto-Data.net Mercedes-Benz SLC C107	https://www.auto-data.net/en/mercedes-benz-slc-c107-generation-8623
EU-FORD-CAPRI-II-COUPE-01	4286	1695	1295	UltimateSpecs Ford Capri Mk II	https://www.ultimatespecs.com/car-specs/Ford/M14131/Capri-Mk-II
EU-OPEL-VECTRA-A-HATCHBACK-01	4352	1706	1400	Auto-Data.net Opel Vectra A CC;Auto-Data.net Opel Vectra A CC facelift 1992	https://www.auto-data.net/en/opel-vectra-a-cc-generation-545;https://www.auto-data.net/en/opel-vectra-a-cc-facelift-1992-generation-5166
EU-OPEL-ASTRA-J-SPORTS-TOURER-WAGON-01	4698	1814	1535	Auto-Data.net Opel Astra J Sports Tourer;Auto-Data.net Opel Astra J Sports Tourer facelift 2012	https://www.auto-data.net/en/opel-astra-j-sports-tourer-1.3-cdti-95hp-19424;https://www.auto-data.net/en/opel-astra-j-sports-tourer-facelift-2012-1.3-cdti-95hp-ecotec-19466
EU-FORD-CAPRI-III-COUPE-01	4440	1700	1350	Auto-Data.net Ford Capri III GECP	https://www.auto-data.net/en/ford-capri-iii-gecp-generation-1728
EU-FORD-TRANSIT-MK1-BUS-SWB-LOWROOF-01	4420	1855	1991	Transit Center Ford Transit Mk1 specifications;Classic & Sports Car Ford Transit 60	https://www.transitcenter.uk/transit-mk1-data-specification.php;https://www.classicandsportscar.com/en-au/features/ford-transit-60
EU-FORD-TRANSIT-MK2-BUS-SWB-LOWROOF-01	4552	1855	2020	Transit Center Ford Transit Mk2 specifications;CarsGuide Ford Transit 1980 dimensions	https://www.transitcenter.uk/transit-mk2-data-specification.php;https://www.carsguide.com.au/ford/transit/car-dimensions/1980
EU-FORD-TRANSIT-MK2-BUS-LWB-HIGHROOF-01	5302	2060	2143	Transit Center Ford Transit Mk2 specifications;CarsGuide Ford Transit 1980 dimensions	https://www.transitcenter.uk/transit-mk2-data-specification.php;https://www.carsguide.com.au/ford/transit/car-dimensions/1980
EU-FORD-TRANSIT-VE6-BUS-SWB-PRE92-LOWROOF-01	4606	1938	1974	FordBook Transit 2 dimensions;Transit Center Ford Transit Mk3 specifications	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya;https://www.transitcenter.uk/transit-mk3-data-specification.php
EU-FORD-TRANSIT-VE6-BUS-LWB-PRE92-MIDROOF-01	5368	1972	2051	FordBook Transit 2 dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-BUS-SWB-POST92-LOWROOF-01	4616	1972	1978	FordBook Transit 2 dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-FORD-TRANSIT-VE6-BUS-LWB-POST92-MIDROOF-01	5368	1972	2051	FordBook Transit 2 dimensions	https://www.fordbook.ru/en/transit/2/main/manual/razmery-avtomobilya
EU-JAGUAR-XJ-X351-SEDAN-SWB-PREFL-01	5127	1894	1457	Auto-Data.net Jaguar XJ X351 5.0 V8 Supercharged 470 Hp	https://www.auto-data.net/en/jaguar-xj-x351-5.0-v8-supercharged-470hp-automatic-6-speed-17473
EU-JAGUAR-XJ-X351-SEDAN-LWB-PREFL-01	5252	1894	1457	Auto-Data.net Jaguar XJ Long X351 5.0 V8 Supercharged 470 Hp	https://www.auto-data.net/en/jaguar-xj-long-x351-5.0-v8-supercharged-470hp-automatic-6-speed-51395
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_901-1000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.transitcenter.uk/transit-mk1-data-specification.php?srsltid=AfmBOor_TvFUHEi7uDAwnzuLhZbQNnjSqvsrhyPZKWXHBZT-Y6e6zsPN "FORD TRANSIT MK1 - SPECIFICATIONS"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_901-1000_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_901-1000_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1337 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（313 行）
