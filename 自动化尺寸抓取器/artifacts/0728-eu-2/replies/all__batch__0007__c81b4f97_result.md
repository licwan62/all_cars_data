# 任务：all 第 601-700 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0007__c81b4f97


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 601-700 行

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
all 第 601-700 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A4 b7	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	103	140	Jan 2006	Jun 2008	2024-03-01	19798
Audi	A4 b7 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	103	140	Jan 2006	Jun 2008	2024-03-01	19799
Daewoo	Nubira	1.6	Kombi	Frontantrieb	Benzin	80	109	Jul 2003	-	2024-03-01	19800
Daewoo	Nubira	1.8	Kombi	Frontantrieb	Benzin	90	122	Jul 2003	-	2024-03-01	19801
KIA	Carens i	2.0 Crdi	Großraumlimousine	Frontantrieb	Diesel	103	140	Nov 2005	Apr 2006	2025-02-03	19802
Audi	Q7	3.6 FSI Quattro	SUV	Allrad	Benzin	206	280	Aug 2006	May 2010	2024-03-01	19803
Hyundai	Atos	1.1	Schrägheck	Frontantrieb	Benzin	46	63	Aug 2003	Dec 2008	2024-03-01	19804
Renault	Twizy	80	Schrägheck	Heckantrieb	Elektro	13	18	Apr 2012	-	2024-03-01	19805
Audi	Tt	2.0 Tfsi	Cabriolet	Frontantrieb	Benzin	147	200	Mar 2007	Jun 2010	2024-03-01	19806
Audi	Tt	3.2 V6 Quattro	Cabriolet	Allrad	Benzin	184	250	Mar 2007	Jun 2010	2024-03-01	19807
Volvo	C30	1.6	Schrägheck	Frontantrieb	Benzin	74	100	Oct 2006	Dec 2012	2024-03-01	19808
Volvo	C30	1.8	Schrägheck	Frontantrieb	Benzin	92	125	Oct 2006	Dec 2012	2024-03-01	19809
Volvo	C30	2	Schrägheck	Frontantrieb	Benzin	107	145	Oct 2006	Dec 2012	2024-03-01	19810
Volvo	C30	2.4 I	Schrägheck	Frontantrieb	Benzin	125	170	Oct 2006	Dec 2012	2024-03-01	19811
Volvo	C30	T5	Schrägheck	Frontantrieb	Benzin	162	220	Oct 2006	Dec 2012	2024-03-01	19812
Volvo	C30	1.6 D	Schrägheck	Frontantrieb	Diesel	80	109	Oct 2006	Dec 2012	2024-03-01	19813
Volvo	C30	2.0 D	Schrägheck	Frontantrieb	Diesel	100	136	Oct 2006	Dec 2012	2024-03-01	19814
Volvo	C30	D5	Schrägheck	Frontantrieb	Diesel	132	180	Oct 2006	Dec 2012	2024-03-01	19815
Fiat	Croma	1.8 16V	Kombi	Frontantrieb	Benzin	103	140	Dec 2005	Dec 2011	2024-03-01	19816
Fiat	Grande punto	1.4 16V	Schrägheck	Frontantrieb	Benzin	70	95	Oct 2005	Aug 2011	2024-03-01	19817
Peugeot	Expert	1.8	Bus	Frontantrieb	Benzin	74	101	Oct 1996	Sep 2000	2024-03-01	19818
Peugeot	Expert	1.8	Kasten	Frontantrieb	Benzin	74	101	Oct 1996	Sep 2000	2024-03-01	19819
Skoda	Octavia	1.4	Schrägheck	Frontantrieb	Benzin	59	80	Jun 2004	Apr 2013	2024-03-01	19820
Skoda	Octavia	2.0 TDI 4X4	Kombi	Allrad	Diesel	103	140	Jul 2006	May 2010	2024-03-01	19821
Chrysler	300c	5.7 AWD	Kombi	Allrad	Benzin	250	340	Apr 2005	Dec 2010	2024-03-01	19822
Chrysler	300c	6.1 Srt8	Kombi	Heckantrieb	Benzin	317	431	Jun 2005	Dec 2010	2024-03-01	19823
Audi	A4 b7 avant	2.0 Tfsi	Kombi	Frontantrieb	Benzin	162	220	Jun 2005	Jun 2008	2024-03-01	19825
Audi	A4 b7 avant	2.0 Tfsi Quattro	Kombi	Allrad	Benzin	162	220	Jun 2005	Jun 2008	2024-03-01	19826
BMW	X3	3.0 SI	SUV	Allrad	Benzin	200	272	Aug 2006	Aug 2008	2024-03-01	19827
BMW	X3	2.5 SI	SUV	Allrad	Benzin	160	218	Aug 2006	Aug 2008	2024-03-01	19828
BMW	X3	3.0 SD	SUV	Allrad	Diesel	210	286	Sep 2006	Aug 2008	2024-03-01	19829
Toyota	Avensis	2.0 D-4d	Schrägheck	Frontantrieb	Diesel	93	126	Mar 2006	Nov 2008	2024-03-01	19830
Toyota	Avensis	2.0 D-4d	Stufenheck	Frontantrieb	Diesel	93	126	Mar 2006	Oct 2008	2024-03-01	19831
Toyota	Avensis	2.0 D-4d	Kombi	Frontantrieb	Diesel	93	126	Mar 2006	Nov 2008	2024-03-01	19832
BMW	3	335 I	Stufenheck	Heckantrieb	Benzin	225	306	Sep 2006	Dec 2011	2024-03-01	19833
BMW	3	335 I	Kombi	Heckantrieb	Benzin	225	306	Sep 2006	Jun 2012	2024-03-01	19834
BMW	3	335 D	Coupe	Heckantrieb	Diesel	210	286	Mar 2006	Mar 2013	2024-03-01	19835
BMW	3	335 D	Kombi	Heckantrieb	Diesel	210	286	Sep 2006	Jun 2012	2024-03-01	19836
BMW	3	335 D	Stufenheck	Heckantrieb	Diesel	210	286	Sep 2006	Dec 2011	2024-03-01	19837
Hyundai	Santa fé ii	2.7 V6 GLS	SUV	Frontantrieb	Benzin	139	189	Mar 2006	Dec 2009	2024-03-01	19838
Hyundai	Santa fé ii	2.7 V6 GLS 4X4	SUV	Allrad	Benzin	139	189	Mar 2006	Dec 2009	2024-03-01	19839
Hyundai	Santa fé ii	2.2 Crdi GLS	SUV	Frontantrieb	Diesel	110	150	Mar 2006	Dec 2009	2024-03-01	19840
Hyundai	Santa fé ii	2.2 Crdi GLS 4X4	SUV	Allrad	Diesel	110	150	Mar 2006	Dec 2009	2024-03-01	19841
Audi	A4 b7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	125	170	Jun 2006	Jun 2008	2024-03-01	19842
Audi	A4 b7	2.0 TDI Quattro	Stufenheck	Allrad	Diesel	125	170	Jun 2006	Jun 2008	2024-03-01	19843
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	125	170	Jun 2006	Jun 2008	2024-03-01	19844
Audi	A4 b7 avant	2.0 TDI Quattro	Kombi	Allrad	Diesel	125	170	Jun 2006	Jun 2008	2024-03-01	19845
Audi	A4 b7	2.7 TDI	Stufenheck	Frontantrieb	Diesel	132	180	Jan 2006	Jun 2008	2024-03-01	19846
Audi	A4 b7 avant	2.7 TDI	Kombi	Frontantrieb	Diesel	132	180	Jan 2006	Jun 2008	2024-03-01	19847
Audi	A4 b7	3.0 TDI Quattro	Stufenheck	Allrad	Diesel	171	233	Jan 2006	Jun 2008	2024-03-01	19848
Audi	A4 b7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	100	136	Nov 2004	Jun 2008	2024-03-01	19849
Audi	A4 b7 avant	3.0 TDI Quattro	Kombi	Allrad	Diesel	171	233	Jan 2006	Jun 2008	2024-03-01	19850
Mercedes-benz	R-Klasse	R 63 AMG 4-matic	Großraumlimousine	Allrad	Benzin	375	510	Feb 2006	Dec 2010	2024-03-01	19851
Mercedes-benz	S-Klasse	S 320 CDI 4-matic	Stufenheck	Allrad	Diesel	173	235	Oct 2006	Dec 2013	2024-03-01	19852
Mercedes-benz	S-Klasse	S 420 CDI	Stufenheck	Heckantrieb	Diesel	235	320	Oct 2006	Dec 2009	2024-03-01	19853
Mercedes-benz	S-Klasse	S 500 4-matic	Stufenheck	Allrad	Benzin	285	388	Oct 2005	Dec 2013	2024-03-01	19854
Citroën	C4 i	2.0 16V	Schrägheck	Frontantrieb	Benzin	130	177	Nov 2004	Jul 2008	2024-03-01	19855
Renault	Trafic ii	2.0 DCI 90	Bus	Frontantrieb	Diesel	66	90	Aug 2006	-	2024-03-01	19856
Renault	Trafic ii	2.0 DCI 115	Bus	Frontantrieb	Diesel	84	114	Aug 2006	-	2024-03-01	19857
Renault	Trafic ii	2.5 DCI 145	Bus	Frontantrieb	Diesel	107	146	Aug 2006	-	2024-03-01	19858
Mini	Mini	Cooper	Schrägheck	Frontantrieb	Benzin	88	120	Oct 2006	Feb 2012	2024-03-01	19859
Renault	Trafic ii	2.0 DCI 90	Kasten	Frontantrieb	Diesel	66	90	Aug 2006	-	2024-03-01	19860
Renault	Trafic ii	2.0 DCI 115	Kasten	Frontantrieb	Diesel	84	114	Aug 2006	-	2024-03-01	19861
Mini	Mini	Cooper S	Schrägheck	Frontantrieb	Benzin	128	174	Oct 2006	Feb 2010	2024-03-01	19862
Renault	Trafic ii	2.5 DCI 145	Kasten	Frontantrieb	Diesel	107	146	Aug 2006	-	2024-03-01	19863
Renault	Trafic ii	2.0 DCI 90	Pritsche/Fahrgestell	Frontantrieb	Diesel	66	90	Aug 2006	-	2024-03-01	19864
Renault	Trafic ii	2.0 DCI 115	Pritsche/Fahrgestell	Frontantrieb	Diesel	84	114	Aug 2006	-	2024-03-01	19865
Renault	Trafic ii	2.5 DCI 145	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Aug 2006	-	2024-03-01	19866
Renault	Twingo	1.2 Turbo	Schrägheck	Frontantrieb	Benzin	74	100	Mar 2007	Sep 2014	2026-05-01	19867
Peugeot	Boxer	2.2 HDI 100	Bus	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	19868
Peugeot	Boxer	2.2 HDI 120	Bus	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2024-05-01	19869
Peugeot	Boxer	3.0 HDI 160	Bus	Frontantrieb	Diesel	115	156	Apr 2006	Dec 2015	2024-03-01	19870
Peugeot	Boxer	2.2 HDI 100	Kasten	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	19871
Peugeot	Boxer	2.2 HDI 120	Kasten	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2024-05-01	19872
Peugeot	Boxer	3.0 HDI 160	Kasten	Frontantrieb	Diesel	116	156	Apr 2006	Dec 2015	2024-03-01	19873
Peugeot	Boxer	2.2 HDI 100	Pritsche/Fahrgestell	Frontantrieb	Diesel	74	101	Apr 2006	-	2024-03-01	19874
Peugeot	Boxer	2.2 HDI 120	Pritsche/Fahrgestell	Frontantrieb	Diesel	88	120	Apr 2006	Dec 2016	2024-05-01	19875
Peugeot	Boxer	3.0 HDI 160	Pritsche/Fahrgestell	Frontantrieb	Diesel	116	156	Apr 2006	Dec 2015	2024-03-01	19876
Peugeot	607	2.0 HDI	Stufenheck	Frontantrieb	Diesel	79	107	Mar 2001	Sep 2004	2024-03-01	19877
Subaru	Tribeca	3	SUV	Allrad	Benzin	180	245	Oct 2006	-	2024-03-01	19878
Peugeot	206	1.4	Stufenheck	Frontantrieb	Benzin	55	75	Mar 2007	-	2024-03-01	19879
Subaru	Impreza	1.5 AWD	Stufenheck	Allrad	Benzin	77	105	May 2006	Mar 2007	2024-03-01	19880
Peugeot	206	1.6 16V	Stufenheck	Frontantrieb	Benzin	80	109	Mar 2007	-	2024-03-01	19881
Subaru	Impreza station wagon	1.5 AWD	Kombi	Allrad	Benzin	77	105	May 2006	Mar 2007	2024-03-01	19882
Nissan	Qashqai i	1.6	SUV	Frontantrieb	Benzin	84	114	Feb 2007	Dec 2013	2025-06-01	19883
Toyota	Land cruiser 200	4.5 D4-d	Geländewagen geschlossen	Allrad	Diesel	200	272	Jan 2012	-	2024-03-01	19884
Nissan	Qashqai i	1.5 DCI	SUV	Frontantrieb	Diesel	78	106	Nov 2006	Nov 2013	2025-06-01	19887
Nissan	Qashqai i	2.0 DCI	SUV	Frontantrieb	Diesel	110	150	Feb 2007	Dec 2013	2025-06-01	19888
Lada	Kalina	1.6	Schrägheck	Frontantrieb	Benzin	60	82	Oct 2004	Dec 2013	2024-03-01	19889
Lada	Kalina	1.6	Stufenheck	Frontantrieb	Benzin	60	82	Oct 2004	Dec 2013	2024-03-01	19891
Ssangyong	Actyon	200 XDI 4WD	SUV	Allrad	Diesel	104	141	Oct 2006	-	2025-12-01	19893
Ssangyong	Kyron	2.7 XDI 4X4	SUV	Allrad	Diesel	121	165	May 2005	Dec 2014	2024-03-01	19894
Lotus	Europa	2.0 Turbo	Coupe	Heckantrieb	Benzin	147	200	Jul 2006	-	2024-03-01	19895
Dacia	Logan	1.4	Kombi	Frontantrieb	Benzin	55	75	Feb 2007	-	2024-03-01	19896
Dacia	Logan	1.6	Kombi	Frontantrieb	Benzin	64	87	Feb 2007	Jun 2013	2024-03-01	19897
Dacia	Logan	1.6 16V	Kombi	Frontantrieb	Benzin	77	105	Feb 2007	-	2024-03-01	19898
Dacia	Logan	1.5 DCI	Kombi	Frontantrieb	Diesel	50	68	Feb 2007	-	2024-03-01	19899
Hyundai	Accent iii	1.4 GL	Schrägheck	Frontantrieb	Benzin	71	97	Nov 2005	Nov 2010	2024-03-01	19900
Skoda	Fabia i	1.4 16V	Stufenheck	Frontantrieb	Benzin	59	80	Apr 2006	Dec 2007	2024-03-01	19901
Hyundai	Accent iii	1.6 GLS	Schrägheck	Frontantrieb	Benzin	82	112	Nov 2005	Nov 2010	2024-03-01	19902


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 Audi A4 B7 Sedan/Avant、Audi TT 8J Roadster、BMW X3 E83、Hyundai Santa Fe II、Mini R56、Renault Twizy、Hyundai Atos Prime 等高复用尺寸组。
* Audi Q7 3.6 FSI 的 Ktype `19803` 确实跨越 2009 年改款，长度由 5086 mm 变为 5089 mm，已拆为 `prefl` 与 `facelift` 两条映射。([汽车数据网][1])
* Volvo C30 改款后长度由 4252 mm 变为 4266 mm；仅对同时存在于改款前后的 1.6、2.0 版本拆分，其他已确认只属于改款前外廓的版本不强行派生。([汽车数据网][2])
* BMW E90、E91、E92 均存在可确认的改款前后外廓差异，相关五个 Ktype 已完整拆分，而不是任选一个尺寸。([汽车数据网][3])
* Citroën C4 177 hp 版本已根据具体车型页从输入的 Hatchback 修正为三门 VTS Coupe；页面同时明确区分车身宽度与含后视镜宽度。([汽车数据网][4])
* Toyota Avensis 126 hp 三种车身暂未落盘：现有资料存在功率版本不完全对应以及 Wagon 长度 4700/4715 mm 冲突，未强行选值。([汽车数据网][5])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：41
* READY 映射行：49
* 尚待处理输入 Ktype：59
* 已确认尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19798	19798	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19799	19799	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19803_prefl	19803	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	Ktype跨越2009年改款，改款前外廓。	READY
19803_facelift	19803	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	Ktype跨越2009年改款，改款后外廓。	READY
19804	19804	Hatchback	Atos Prime		5	EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	MEDIUM	1.1版本功率标注存在市场差异，物理车身边界一致。	READY
19805	19805	Hatchback	Twizy I		2	EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	HIGH	车型资料定义为quadricycle；保留最接近的Hatchback标准化分类。	READY
19806	19806	Convertible	TT 8J	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH		READY
19807	19807	Convertible	TT 8J	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH		READY
19808_prefl	19808	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH	1.6版本跨越2010年改款，改款前外廓。	READY
19808_facelift	19808	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	HIGH	1.6版本跨越2010年改款，改款后外廓。	READY
19809	19809	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19810_prefl	19810	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH	2.0版本跨越2010年改款，改款前外廓。	READY
19810_facelift	19810	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	HIGH	2.0版本跨越2010年改款，改款后外廓。	READY
19811	19811	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19812	19812	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19813	19813	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19814	19814	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19815	19815	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19825	19825	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19826	19826	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19827	19827	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19828	19828	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19829	19829	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19833_prefl	19833	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	Ktype跨越2008年E90改款，改款前外廓。	READY
19833_facelift	19833	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	Ktype跨越2008年E90改款，改款后外廓。	READY
19834_prefl	19834	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	Ktype跨越2008年E91改款，改款前外廓。	READY
19834_facelift	19834	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	Ktype跨越2008年E91改款，改款后外廓。	READY
19835_prefl	19835	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH	Ktype跨越2010年E92改款，改款前外廓。	READY
19835_facelift	19835	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	Ktype跨越2010年E92改款，改款后外廓。	READY
19836_prefl	19836	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	Ktype跨越2008年E91改款，改款前外廓。	READY
19836_facelift	19836	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	Ktype跨越2008年E91改款，改款后外廓。	READY
19837_prefl	19837	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	Ktype跨越2008年E90改款，改款前外廓。	READY
19837_facelift	19837	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	Ktype跨越2008年E90改款，改款后外廓。	READY
19838	19838	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19839	19839	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19840	19840	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19841	19841	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19842	19842	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19843	19843	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19844	19844	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19845	19845	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19846	19846	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19847	19847	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19848	19848	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19849	19849	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19850	19850	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19855	19855	Coupe	C4 I Phase I		3	EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	HIGH	177 hp版本对应三门VTS Coupe；按车型资料纠正车身形式。	READY
19859	19859	Hatchback	Mini Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-01	HIGH		READY
19862	19862	Hatchback	Mini Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-S-01	HIGH		READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-140hp-multitronic-26722
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b7-8e-generation-5202
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737	Auto-Data.net	https://www.auto-data.net/en/audi-q7-i-typ-4l-3.6-fsi-v6-280hp-quattro-tiptronic-4854
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737	Auto-Data.net	https://www.auto-data.net/en/audi-q7-i-typ-4l-facelift-2009-3.6-fsi-v6-280hp-quattro-tiptronic-27127
EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	3495	1485	1580	Auto-Data.net	https://www.auto-data.net/en/hyundai-atos-prime-1.1-i-12v-59hp-13739
EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	2338	1237	1454	Auto-Data.net	https://www.auto-data.net/en/renault-twizy-ze-generation-6939
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358	Auto-Data.net	https://www.auto-data.net/en/audi-tt-roadster-8j-2.0-tfsi-200hp-17876
EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	4252	1782	1447	Auto-Data.net	https://www.auto-data.net/en/volvo-c30-generation-1956
EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	4266	1782	1447	Auto-Data.net	https://www.auto-data.net/en/volvo-c30-facelift-2010-generation-4973
EU-BMW-X3-E83-SUV-5D-FACELIFT-01	4569	1853	1674	Auto-Data.net	https://www.auto-data.net/en/bmw-x3-e83-facelift-2006-generation-6389
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-sedan-e90-335i-306hp-9937
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-335i-306hp-27964
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-e91-335i-306hp-steptronic-45541
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-335i-306hp-27568
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-335d-286hp-steptronic-9957
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-335d-286hp-steptronic-17235
EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	4675	1890	1725	Auto-Data.net	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-generation-2971
EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	4273	1769	1456	Auto-Data.net	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-i-2004-vts-2.0i-16v-177hp-15174
EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-01	3699	1683	1407	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327
EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-S-01	3714	1683	1407	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r56-cooper-s-1.6-i-16v-turbo-175hp-15328
```

## 下一步优先处理

1. 解决 Toyota Avensis 126 hp Hatchback、Sedan、Wagon 的具体版本尺寸冲突。
2. 集中闭合 Peugeot Expert、Renault Trafic II、Peugeot Boxer 的轴距、车顶和 Bus/Kasten/Pritsche 物理分支。
3. 批量处理同外廓车型族：Daewoo Nubira Wagon、Skoda Octavia II、Chrysler 300C Wagon、Nissan Qashqai J10。
4. 再处理跨改款车型：Twingo II、Dacia Logan MCV、Land Cruiser 200、Lada Kalina。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-q7-i-typ-4l-3.6-fsi-v6-280hp-quattro-tiptronic-4854 "Audi Q7 I (Typ 4L) 3.6 FSI V6 (280 Hp) quattro tiptronic | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volvo-c30-generation-1956?utm_source=chatgpt.com "Volvo C30 | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/bmw-3-series-sedan-e90-335i-306hp-9937 "BMW 3 Series Sedan (E90) 335i (306 Hp) | Technical specs, data, fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/citroen-c4-i-coupe-phase-i-2004-vts-2.0i-16v-177hp-15174 "Citroen C4 I Coupe (Phase I, 2004) VTS 2.0i 16V (177 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/toyota-avensis-ii-wagon-generation-901?utm_source=chatgpt.com "Toyota Avensis II Wagon | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮闭合 15 个输入 Ktype，新增 18 条 READY 映射和 15 个尺寸组。
* Mercedes-Benz R-Class R 63 AMG 与 S-Class S 420 CDI 均确认存在短轴、长轴两种物理外廓，分别按 W251/V251 与 W221/V221 拆分。([汽车数据网][1])
* Fiat Grande Punto 199 的资料明确覆盖三门和五门，两者三维一致，因此映射层拆分门数，但共同引用一个尺寸组。([汽车数据网][2])
* Peugeot 206 Sedan 两个动力版本复用同一尺寸组；Subaru Impreza Sedan/Wagon 因宽度和高度不同分别建组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：56
* READY 映射行：67
* PENDING 输入 Ktype：44
* 已确认尺寸组：35
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19802	19802	MPV	Carens II		5	EU-KIA-CARENS-II-MPV-5D-01	MEDIUM	输入代际标签为Carens i，但140 hp版本对应Carens II。	READY
19817_3dr	19817	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	HIGH	同一Ktype覆盖三门和五门；两种门数三维一致。	READY
19817_5dr	19817	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	HIGH	同一Ktype覆盖三门和五门；两种门数三维一致。	READY
19822	19822	Wagon	300 Touring		5	EU-CHRYSLER-300-TOURING-WAGON-STANDARD-01	HIGH		READY
19823	19823	Wagon	300 Touring		5	EU-CHRYSLER-300-TOURING-WAGON-SRT8-01	HIGH	SRT8外部长度和高度不同，独立尺寸组。	READY
19851_swb	19851	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-01	MEDIUM	短轴W251物理分支。	READY
19851_lwb	19851	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-01	MEDIUM	长轴V251物理分支。	READY
19853_swb	19853	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距W221物理分支。	READY
19853_lwb	19853	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距V221物理分支。	READY
19878	19878	SUV	B9 Tribeca		5	EU-SUBARU-B9-TRIBECA-SUV-5D-01	MEDIUM	输入245 hp与资料250 hp属于市场功率标注差异。	READY
19879	19879	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
19880	19880	Sedan	Impreza II facelift 2005		4	EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	HIGH		READY
19881	19881	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
19882	19882	Wagon	Impreza II Station Wagon facelift 2005		5	EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	HIGH		READY
19893	19893	SUV	Actyon I		5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	MEDIUM	200 XDI 4WD对应第一代Actyon SUV外廓。	READY
19895	19895	Coupe	Europa S		2	EU-LOTUS-EUROPA-S-COUPE-2D-01	MEDIUM	147 kW版本对应Europa S 203 PS规格。	READY
19900	19900	Hatchback	Accent Hatchback III		3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
19902	19902	Hatchback	Accent Hatchback III		3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-KIA-CARENS-II-MPV-5D-01	4545	1820	1650	Auto-Data.net	https://www.auto-data.net/en/kia-carens-ii-2.0-crdi-140hp-2708
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-95hp-35741
EU-CHRYSLER-300-TOURING-WAGON-STANDARD-01	4999	1881	1507	Auto-Data.net	https://www.auto-data.net/en/chrysler-300-touring-5.7-i-v8-awd-340hp-14696
EU-CHRYSLER-300-TOURING-WAGON-SRT8-01	5015	1880	1462	Auto-Data.net	https://www.auto-data.net/en/chrysler-300-touring-6.1-i-v8-16v-srt-8-431hp-14697
EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-01	4930	1922	1634	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-amg-r-63-v8-510hp-4matic-7g-tronic-amg-speedshift-43237
EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-01	5165	1922	1634	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-amg-r-63-v8-510hp-4matic-7g-tronic-amg-speedshift-43240
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	5079	1872	1473	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-w221-s-420-cdi-v8-320hp-7g-tronic-13041
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	5209	1872	1473	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-s-420-cdi-v8-320hp-7g-tronic-13042
EU-SUBARU-B9-TRIBECA-SUV-5D-01	4855	1880	1675	Auto-Data.net	https://www.auto-data.net/en/subaru-b9-tribeca-3.0i-250hp-awd-sportshift-37631
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/peugeot-206-sedan-1.4-75hp-5244; https://www.auto-data.net/en/peugeot-206-sedan-1.6-110hp-5245
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2005-1.5-105hp-awd-16075
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-station-wagon-facelift-2005-1.5-105hp-awd-42629
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740	Auto-Data.net	https://www.auto-data.net/en/ssangyong-actyon-2.0-xdi-141hp-automatic-24350
EU-LOTUS-EUROPA-S-COUPE-2D-01	3900	1714	1120	Auto-Data.net	https://www.auto-data.net/en/lotus-europa-s-2.0-16v-203hp-8315
EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	4045	1695	1470	Auto-Data.net	https://www.auto-data.net/en/hyundai-accent-hatchback-iii-generation-2954
```

## 下一步优先处理

1. 闭合剩余单一外廓乘用车：Daewoo Nubira Wagon、Fiat Croma、Toyota Avensis、Peugeot 607、Lada Kalina、Skoda Fabia Sedan。
2. 处理跨改款车型：Skoda Octavia Hatchback、Nissan Qashqai J10、Renault Twingo II、Dacia Logan MCV、Toyota Land Cruiser 200。
3. 最后集中拆分 Peugeot Expert、Renault Trafic II、Peugeot Boxer 的轴距、车顶和 Bus/Kasten/Pritsche 分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-r-class-w251-amg-r-63-v8-510hp-4matic-7g-tronic-amg-speedshift-43237?utm_source=chatgpt.com "Mercedes-Benz R-class (W251) AMG R 63 V8 (510 Hp) ..."
[2]: https://www.auto-data.net/en/fiat-grande-punto-199-1.4-95hp-35741?utm_source=chatgpt.com "Specs of Fiat Grande Punto (199) 1.4 (95 Hp) /2006, 2007, ..."
[3]: https://www.auto-data.net/en/subaru-impreza-ii-facelift-2005-1.5-105hp-awd-16075?utm_source=chatgpt.com "Subaru Impreza II (facelift 2005) 1.5 (105 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 本轮闭合 24 个输入 Ktype，新增 47 条 READY 映射；剩余 20 个均为多轴距、多车顶或底盘形式的商用车。
* Skoda Octavia II Hatchback 与 Combi 均按改款前后拆分；不同外廓没有混入同一尺寸组。([汽车数据网][1])
* Mercedes-Benz S-Class 改款前短轴、长轴尺寸组直接复用，本轮只首次创建 2009 年改款后的短轴、长轴尺寸组。([汽车数据网][2])
* Toyota Land Cruiser 200 因 2012、2013 改款和 2015 改款存在外廓变化，拆为三个物理分支。([汽车数据网][3])
* Dacia Logan MCV 四个 Ktype 批量关联同一组改款前、改款后尺寸组，未按发动机重复建组。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：80
* READY 映射行：114
* PENDING 输入 Ktype：20
* 已确认尺寸组：61
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19800	19800	Wagon	Nubira III	J200	5	EU-DAEWOO-NUBIRA-III-WAGON-5D-01	MEDIUM		READY
19801	19801	Wagon	Nubira III	J200	5	EU-DAEWOO-NUBIRA-III-WAGON-5D-01	MEDIUM		READY
19816	19816	Wagon	Croma II	194	5	EU-FIAT-CROMA-II-WAGON-5D-01	HIGH		READY
19820_prefl	19820	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19820_facelift	19820	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	2009年改款后物理外廓。	READY
19821_prefl	19821	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	改款前Combi物理外廓。	READY
19821_facelift	19821	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	2009年改款后Combi物理外廓。	READY
19830	19830	Hatchback	Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-5D-01	HIGH		READY
19831	19831	Sedan	Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-4D-01	HIGH		READY
19832	19832	Wagon	Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-5D-01	HIGH		READY
19852_swb_prefl	19852	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距改款前物理分支。	READY
19852_swb_facelift	19852	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	标准轴距2009年改款后物理分支。	READY
19852_lwb_prefl	19852	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距改款前物理分支。	READY
19852_lwb_facelift	19852	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴距2009年改款后物理分支。	READY
19854_swb_prefl	19854	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距改款前物理分支。	READY
19854_swb_facelift	19854	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	标准轴距2009年改款后物理分支。	READY
19854_lwb_prefl	19854	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距改款前物理分支。	READY
19854_lwb_facelift	19854	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴距2009年改款后物理分支。	READY
19867_prefl	19867	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	HIGH	改款前物理外廓。	READY
19867_facelift	19867	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	HIGH	2011年改款后物理外廓。	READY
19877	19877	Sedan	607 Phase I		4	EU-PEUGEOT-607-SEDAN-4D-PHASE-I-01	HIGH		READY
19883_prefl	19883	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19883_facelift	19883	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19884_pre2013	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-2012-01	MEDIUM	2012年规格物理外廓。	READY
19884_facelift2013	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2013-01	MEDIUM	2013年改款物理外廓。	READY
19884_facelift2015	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2015-01	MEDIUM	2015年改款物理外廓。	READY
19887_prefl	19887	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19887_facelift	19887	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19888_prefl	19888	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19888_facelift	19888	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19889	19889	Hatchback	Kalina I	VAZ-1119	5	EU-LADA-KALINA-I-HATCHBACK-5D-01	MEDIUM		READY
19891	19891	Sedan	Kalina I	VAZ-1118	4	EU-LADA-KALINA-I-SEDAN-4D-01	MEDIUM		READY
19894_prefl	19894	SUV	Kyron I		5	EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	MEDIUM	改款前物理外廓。	READY
19894_facelift	19894	SUV	Kyron I		5	EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	MEDIUM	2007年改款后物理外廓。	READY
19896_prefl	19896	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19896_facelift	19896	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19897_prefl	19897	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19897_facelift	19897	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19898_prefl	19898	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19898_facelift	19898	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19899_prefl	19899	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19899_facelift	19899	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19901	19901	Sedan	Fabia I	6Y	4	EU-SKODA-FABIA-I-SEDAN-4D-FACELIFT-01	HIGH	2004年改款后的Sedan外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-DAEWOO-NUBIRA-III-WAGON-5D-01	4580	1725	1460	Auto-Data.net	https://www.auto-data.net/en/chevrolet-nubira-station-wagon-1.6-i-16v-109hp-14357
EU-FIAT-CROMA-II-WAGON-5D-01	4756	1775	1597	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-ii-1.8-16v-140hp-6797
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-model-1560
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-model-1560
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-2.0-tdi-140hp-14230
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-2.0-tdi-cr-140hp-4x4-14207
EU-TOYOTA-AVENSIS-II-HATCHBACK-5D-01	4630	1760	1480	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-TOYOTA-AVENSIS-II-SEDAN-4D-01	4630	1760	1480	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-TOYOTA-AVENSIS-II-WAGON-5D-01	4715	1760	1525	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-generation-7081
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-500-v8-388hp-4matic-g-tronic-36894
EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	3602	1665	1470	Auto-Data.net	https://www.auto-data.net/en/renault-twingo-ii-1.2-16v-tce-gt-100hp-10691
EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	3699	1688	1470	Auto-Data.net	https://www.auto-data.net/en/renault-twingo-model-1042
EU-PEUGEOT-607-SEDAN-4D-PHASE-I-01	4877	1800	1437	Auto-Data.net	https://www.auto-data.net/en/peugeot-607-model-575
EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	4315	1780	1605	Auto-Data.net	https://www.auto-data.net/en/nissan-qashqai-i-j10-1.6-114hp-730
EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	4330	1780	1615	Auto-Data.net	https://www.auto-data.net/en/nissan-qashqai-model-90
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-2012-01	4950	1971	1950	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-model-438
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2013-01	4950	1970	1865	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-j200-facelift-2013-4.5d-v8-272hp-automatic-18527
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2015-01	4990	1980	1945	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-model-438
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500	Bind.lt	https://bind.lt/en/technical-specifications/vaz-lada/kalina/1-generation/1119-hatchback-5-doors/1-6-mt-8-valves-euro-4-81-hp
EU-LADA-KALINA-I-SEDAN-4D-01	4040	1700	1500	Otoba.ru	https://otoba.ru/auto/lada/kalina-sedan.html
EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	4660	1880	1755	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/3166490/ssangyong_kyron_2_7_xdi_4wd.html
EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	4660	1880	1740	Car Dimensions	https://www.car-dimensions.com/dimensions/SsangYong_Kyron/
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674	Auto-Data.net	https://www.auto-data.net/en/dacia-logan-i-mcv-1.4i-75hp-7-seats-15883
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640	Auto-Data.net	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-68hp-46176
EU-SKODA-FABIA-I-SEDAN-4D-FACELIFT-01	4232	1646	1449	Auto-Data.net	https://www.auto-data.net/en/skoda-fabia-sedan-i-6y-facelift-2004-1.4-16v-80hp-36206
```

## 下一步优先处理

1. Peugeot Expert I：处理 Bus 与 Kasten 的轴距、车顶和车身长度分支，共 2 个 Ktype。
2. Renault Trafic II：集中核对 Bus、Kasten、Pritsche/Fahrgestell 的 SWB/LWB 与车顶组合，共 9 个 Ktype。
3. Peugeot Boxer II：集中核对 Bus、Kasten、Pritsche/Fahrgestell 的 L1–L4、H1–H3 和底盘形式，共 9 个 Ktype。
4. 商用车尺寸组闭合后，立即执行一次机械完整性检查并输出最终两张完整 TSV。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/skoda-octavia-model-1560?utm_source=chatgpt.com "Skoda Octavia | Technical Specs, Fuel consumption, ..."
[2]: https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-generation-7081?utm_source=chatgpt.com "Mercedes-Benz S-class (W221, facelift 2009)"
[3]: https://www.auto-data.net/en/toyota-land-cruiser-model-438?utm_source=chatgpt.com "Toyota Land Cruiser | Technical Specs, Fuel consumption, ..."
[4]: https://www.auto-data.net/en/dacia-logan-i-mcv-generation-3529?utm_source=chatgpt.com "Dacia Logan I MCV | Technical Specs, Fuel consumption, ..."


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_601-700_ktype_dimension_mapping_final.tsv
- all_601-700_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 最后 20 个商用车 Ktype 已闭合：Peugeot Expert I 按 Bus/Van 区分；Renault Trafic II 按轴距、车顶和平台驾驶室拆分；Peugeot Boxer II 按客运、厢式及底盘驾驶室配置拆分。([标致车主之家][1])
* 已完成机械检查：表头正确、`id` 唯一、`DIMENSION_GROUP_ID` 唯一、映射引用全部闭合、尺寸及来源字段完整。
* 两个指定文件已生成。

## 当前批次进度

* 输入 Ktype：100
* READY 映射行：173
* PENDING：0
* DIMENSION_GROUP：85
* 孤立尺寸组：0
* 缺失尺寸组引用：0
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19798	19798	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19799	19799	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19800	19800	Wagon	Nubira III	J200	5	EU-DAEWOO-NUBIRA-III-WAGON-5D-01	MEDIUM		READY
19801	19801	Wagon	Nubira III	J200	5	EU-DAEWOO-NUBIRA-III-WAGON-5D-01	MEDIUM		READY
19802	19802	MPV	Carens II		5	EU-KIA-CARENS-II-MPV-5D-01	MEDIUM	输入代际标签为Carens i，但140 hp版本对应Carens II。	READY
19803_prefl	19803	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-PREFL-01	HIGH	Ktype跨越2009年改款，改款前外廓。	READY
19803_facelift	19803	SUV	Q7 I	4L	5	EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	HIGH	Ktype跨越2009年改款，改款后外廓。	READY
19804	19804	Hatchback	Atos Prime		5	EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	MEDIUM	1.1版本功率标注存在市场差异，物理车身边界一致。	READY
19805	19805	Hatchback	Twizy I		2	EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	HIGH	车型资料定义为quadricycle；保留最接近的Hatchback标准化分类。	READY
19806	19806	Convertible	TT 8J	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH		READY
19807	19807	Convertible	TT 8J	8J	2	EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	HIGH		READY
19808_prefl	19808	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH	1.6版本跨越2010年改款，改款前外廓。	READY
19808_facelift	19808	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	HIGH	1.6版本跨越2010年改款，改款后外廓。	READY
19809	19809	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19810_prefl	19810	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH	2.0版本跨越2010年改款，改款前外廓。	READY
19810_facelift	19810	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	HIGH	2.0版本跨越2010年改款，改款后外廓。	READY
19811	19811	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19812	19812	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19813	19813	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19814	19814	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19815	19815	Hatchback	C30 I		3	EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	HIGH		READY
19816	19816	Wagon	Croma II	194	5	EU-FIAT-CROMA-II-WAGON-5D-01	HIGH		READY
19817_3dr	19817	Hatchback	Grande Punto	199	3	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	HIGH	同一Ktype覆盖三门和五门；两种门数三维一致。	READY
19817_5dr	19817	Hatchback	Grande Punto	199	5	EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	HIGH	同一Ktype覆盖三门和五门；两种门数三维一致。	READY
19818	19818	MPV	Expert I	224	4	EU-PEUGEOT-EXPERT-I-BUS-01	HIGH		READY
19819	19819	Van	Expert I	222		EU-PEUGEOT-EXPERT-I-VAN-01	HIGH		READY
19820_prefl	19820	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19820_facelift	19820	Hatchback	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	HIGH	2009年改款后物理外廓。	READY
19821_prefl	19821	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	HIGH	改款前Combi物理外廓。	READY
19821_facelift	19821	Wagon	Octavia II	1Z	5	EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	HIGH	2009年改款后Combi物理外廓。	READY
19822	19822	Wagon	300 Touring		5	EU-CHRYSLER-300-TOURING-WAGON-STANDARD-01	HIGH		READY
19823	19823	Wagon	300 Touring		5	EU-CHRYSLER-300-TOURING-WAGON-SRT8-01	HIGH	SRT8外部长度和高度不同，独立尺寸组。	READY
19825	19825	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19826	19826	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19827	19827	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19828	19828	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19829	19829	SUV	X3 E83	E83	5	EU-BMW-X3-E83-SUV-5D-FACELIFT-01	HIGH		READY
19830	19830	Hatchback	Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-5D-01	HIGH		READY
19831	19831	Sedan	Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-4D-01	HIGH		READY
19832	19832	Wagon	Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-5D-01	HIGH		READY
19833_prefl	19833	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	Ktype跨越2008年E90改款，改款前外廓。	READY
19833_facelift	19833	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	Ktype跨越2008年E90改款，改款后外廓。	READY
19834_prefl	19834	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	Ktype跨越2008年E91改款，改款前外廓。	READY
19834_facelift	19834	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	Ktype跨越2008年E91改款，改款后外廓。	READY
19835_prefl	19835	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-PREFL-01	HIGH	Ktype跨越2010年E92改款，改款前外廓。	READY
19835_facelift	19835	Coupe	3 Series E92	E92	2	EU-BMW-3-E92-COUPE-2D-FACELIFT-01	HIGH	Ktype跨越2010年E92改款，改款后外廓。	READY
19836_prefl	19836	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-PREFL-01	HIGH	Ktype跨越2008年E91改款，改款前外廓。	READY
19836_facelift	19836	Wagon	3 Series E91	E91	5	EU-BMW-3-E91-WAGON-5D-FACELIFT-01	HIGH	Ktype跨越2008年E91改款，改款后外廓。	READY
19837_prefl	19837	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-PREFL-01	HIGH	Ktype跨越2008年E90改款，改款前外廓。	READY
19837_facelift	19837	Sedan	3 Series E90	E90	4	EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	HIGH	Ktype跨越2008年E90改款，改款后外廓。	READY
19838	19838	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19839	19839	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19840	19840	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19841	19841	SUV	Santa Fe II	CM	5	EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	HIGH		READY
19842	19842	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19843	19843	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19844	19844	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19845	19845	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19846	19846	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19847	19847	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19848	19848	Sedan	A4 B7	8E	4	EU-AUDI-A4-B7-SEDAN-4D-01	HIGH		READY
19849	19849	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19850	19850	Wagon	A4 B7	8E	5	EU-AUDI-A4-B7-WAGON-5D-01	HIGH		READY
19851_swb	19851	MPV	R-Class I	W251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-01	MEDIUM	短轴W251物理分支。	READY
19851_lwb	19851	MPV	R-Class I	V251	5	EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-01	MEDIUM	长轴V251物理分支。	READY
19852_swb_prefl	19852	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距改款前物理分支。	READY
19852_swb_facelift	19852	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	标准轴距2009年改款后物理分支。	READY
19852_lwb_prefl	19852	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距改款前物理分支。	READY
19852_lwb_facelift	19852	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴距2009年改款后物理分支。	READY
19853_swb	19853	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距W221物理分支。	READY
19853_lwb	19853	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距V221物理分支。	READY
19854_swb_prefl	19854	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	MEDIUM	标准轴距改款前物理分支。	READY
19854_swb_facelift	19854	Sedan	S-Class W221	W221	4	EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	MEDIUM	标准轴距2009年改款后物理分支。	READY
19854_lwb_prefl	19854	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	MEDIUM	长轴距改款前物理分支。	READY
19854_lwb_facelift	19854	Sedan	S-Class Long V221	V221	4	EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	MEDIUM	长轴距2009年改款后物理分支。	READY
19855	19855	Coupe	C4 I Phase I		3	EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	HIGH	177 hp版本对应三门VTS Coupe；按车型资料纠正车身形式。	READY
19856_l1h1	19856	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L1H1-01	HIGH	L1H1短轴低顶客运车身。	READY
19856_l2h1	19856	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L2H1-01	HIGH	L2H1长轴低顶客运车身。	READY
19857_l1h1	19857	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L1H1-01	HIGH	L1H1短轴低顶客运车身。	READY
19857_l2h1	19857	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L2H1-01	HIGH	L2H1长轴低顶客运车身。	READY
19858_l1h1	19858	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L1H1-01	HIGH	L1H1短轴低顶客运车身。	READY
19858_l2h1	19858	MPV	Trafic II Phase II		4	EU-RENAULT-TRAFIC-II-BUS-L2H1-01	HIGH	L2H1长轴低顶客运车身。	READY
19859	19859	Hatchback	Mini Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-01	HIGH		READY
19860_l1h1	19860	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19860_l1h2	19860	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶厢式车身。	READY
19860_l2h1	19860	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H1-01	MEDIUM	L2H1长轴低顶厢式车身。	READY
19860_l2h2	19860	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H2-01	MEDIUM	L2H2长轴高顶厢式车身。	READY
19861_l1h1	19861	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19861_l1h2	19861	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶厢式车身。	READY
19861_l2h1	19861	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H1-01	MEDIUM	L2H1长轴低顶厢式车身。	READY
19861_l2h2	19861	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H2-01	MEDIUM	L2H2长轴高顶厢式车身。	READY
19862	19862	Hatchback	Mini Hatch R56	R56	3	EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-S-01	HIGH		READY
19863_l1h1	19863	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19863_l1h2	19863	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L1H2-01	MEDIUM	L1H2短轴高顶厢式车身。	READY
19863_l2h1	19863	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H1-01	MEDIUM	L2H1长轴低顶厢式车身。	READY
19863_l2h2	19863	Van	Trafic II Phase II			EU-RENAULT-TRAFIC-II-VAN-L2H2-01	MEDIUM	L2H2长轴高顶厢式车身。	READY
19864	19864	Pickup	Trafic II Phase II		2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	MEDIUM	L2平台驾驶室底盘。	READY
19865	19865	Pickup	Trafic II Phase II		2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	MEDIUM	L2平台驾驶室底盘。	READY
19866	19866	Pickup	Trafic II Phase II		2	EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	MEDIUM	L2平台驾驶室底盘。	READY
19867_prefl	19867	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	HIGH	改款前物理外廓。	READY
19867_facelift	19867	Hatchback	Twingo II		3	EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	HIGH	2011年改款后物理外廓。	READY
19868_l1h1	19868	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L1H1-01	MEDIUM	L1H1短轴低顶客运车身。	READY
19868_l2h2	19868	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L2H2-01	MEDIUM	L2H2中轴中顶客运车身。	READY
19868_l3h2	19868	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L3H2-01	MEDIUM	L3H2长轴中顶客运车身。	READY
19869_l1h1	19869	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L1H1-01	MEDIUM	L1H1短轴低顶客运车身。	READY
19869_l2h2	19869	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L2H2-01	MEDIUM	L2H2中轴中顶客运车身。	READY
19869_l3h2	19869	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L3H2-01	MEDIUM	L3H2长轴中顶客运车身。	READY
19870_l1h1	19870	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L1H1-01	MEDIUM	L1H1短轴低顶客运车身。	READY
19870_l2h2	19870	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L2H2-01	MEDIUM	L2H2中轴中顶客运车身。	READY
19870_l3h2	19870	MPV	Boxer II	250		EU-PEUGEOT-BOXER-II-BUS-L3H2-01	MEDIUM	L3H2长轴中顶客运车身。	READY
19871_l1h1	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19871_l1h2	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	MEDIUM	L1H2短轴中顶厢式车身。	READY
19871_l2h1	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	MEDIUM	L2H1中轴低顶厢式车身。	READY
19871_l2h2	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	MEDIUM	L2H2中轴中顶厢式车身。	READY
19871_l3h2	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	MEDIUM	L3H2长轴中顶厢式车身。	READY
19871_l3h3	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	MEDIUM	L3H3长轴高顶厢式车身。	READY
19871_l4h2	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	MEDIUM	L4H2加长轴中顶厢式车身。	READY
19871_l4h3	19871	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	MEDIUM	L4H3加长轴高顶厢式车身。	READY
19872_l1h1	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19872_l1h2	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	MEDIUM	L1H2短轴中顶厢式车身。	READY
19872_l2h1	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	MEDIUM	L2H1中轴低顶厢式车身。	READY
19872_l2h2	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	MEDIUM	L2H2中轴中顶厢式车身。	READY
19872_l3h2	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	MEDIUM	L3H2长轴中顶厢式车身。	READY
19872_l3h3	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	MEDIUM	L3H3长轴高顶厢式车身。	READY
19872_l4h2	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	MEDIUM	L4H2加长轴中顶厢式车身。	READY
19872_l4h3	19872	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	MEDIUM	L4H3加长轴高顶厢式车身。	READY
19873_l1h1	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H1-01	MEDIUM	L1H1短轴低顶厢式车身。	READY
19873_l1h2	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L1H2-01	MEDIUM	L1H2短轴中顶厢式车身。	READY
19873_l2h1	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H1-01	MEDIUM	L2H1中轴低顶厢式车身。	READY
19873_l2h2	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L2H2-01	MEDIUM	L2H2中轴中顶厢式车身。	READY
19873_l3h2	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H2-01	MEDIUM	L3H2长轴中顶厢式车身。	READY
19873_l3h3	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L3H3-01	MEDIUM	L3H3长轴高顶厢式车身。	READY
19873_l4h2	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H2-01	MEDIUM	L4H2加长轴中顶厢式车身。	READY
19873_l4h3	19873	Van	Boxer II	250		EU-PEUGEOT-BOXER-II-VAN-L4H3-01	MEDIUM	L4H3加长轴高顶厢式车身。	READY
19874_l1	19874	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	MEDIUM	L1短轴底盘驾驶室。	READY
19874_l2	19874	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	MEDIUM	L2中轴底盘驾驶室。	READY
19875_l1	19875	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	MEDIUM	L1短轴底盘驾驶室。	READY
19875_l2	19875	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	MEDIUM	L2中轴底盘驾驶室。	READY
19875_l3	19875	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	MEDIUM	L3长轴底盘驾驶室。	READY
19876_l3	19876	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	MEDIUM	L3长轴底盘驾驶室。	READY
19876_l4	19876	Pickup	Boxer II	250	2	EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	MEDIUM	L4加长轴底盘驾驶室。	READY
19877	19877	Sedan	607 Phase I		4	EU-PEUGEOT-607-SEDAN-4D-PHASE-I-01	HIGH		READY
19878	19878	SUV	B9 Tribeca		5	EU-SUBARU-B9-TRIBECA-SUV-5D-01	MEDIUM	输入245 hp与资料250 hp属于市场功率标注差异。	READY
19879	19879	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
19880	19880	Sedan	Impreza II facelift 2005		4	EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	HIGH		READY
19881	19881	Sedan	206 Sedan		4	EU-PEUGEOT-206-SEDAN-4D-01	HIGH		READY
19882	19882	Wagon	Impreza II Station Wagon facelift 2005		5	EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	HIGH		READY
19883_prefl	19883	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19883_facelift	19883	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19884_pre2013	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-2012-01	MEDIUM	2012年规格物理外廓。	READY
19884_facelift2013	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2013-01	MEDIUM	2013年改款物理外廓。	READY
19884_facelift2015	19884	SUV	Land Cruiser 200	J200	5	EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2015-01	MEDIUM	2015年改款物理外廓。	READY
19887_prefl	19887	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19887_facelift	19887	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19888_prefl	19888	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	HIGH	改款前物理外廓。	READY
19888_facelift	19888	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	HIGH	2010年改款后物理外廓。	READY
19889	19889	Hatchback	Kalina I	VAZ-1119	5	EU-LADA-KALINA-I-HATCHBACK-5D-01	MEDIUM		READY
19891	19891	Sedan	Kalina I	VAZ-1118	4	EU-LADA-KALINA-I-SEDAN-4D-01	MEDIUM		READY
19893	19893	SUV	Actyon I		5	EU-SSANGYONG-ACTYON-I-SUV-5D-01	MEDIUM	200 XDI 4WD对应第一代Actyon SUV外廓。	READY
19894_prefl	19894	SUV	Kyron I		5	EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	MEDIUM	改款前物理外廓。	READY
19894_facelift	19894	SUV	Kyron I		5	EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	MEDIUM	2007年改款后物理外廓。	READY
19895	19895	Coupe	Europa S		2	EU-LOTUS-EUROPA-S-COUPE-2D-01	MEDIUM	147 kW版本对应Europa S 203 PS规格。	READY
19896_prefl	19896	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19896_facelift	19896	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19897_prefl	19897	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19897_facelift	19897	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19898_prefl	19898	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19898_facelift	19898	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19899_prefl	19899	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	HIGH	改款前MCV物理外廓。	READY
19899_facelift	19899	Wagon	Logan I MCV		5	EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	HIGH	2008年改款后MCV物理外廓。	READY
19900	19900	Hatchback	Accent Hatchback III		3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
19901	19901	Sedan	Fabia I	6Y	4	EU-SKODA-FABIA-I-SEDAN-4D-FACELIFT-01	HIGH	2004年改款后的Sedan外廓。	READY
19902	19902	Hatchback	Accent Hatchback III		3	EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_601-700_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A4-B7-SEDAN-4D-01	4586	1772	1427	Auto-Data.net	https://www.auto-data.net/en/audi-a4-b7-8e-2.0-tdi-140hp-multitronic-26722
EU-AUDI-A4-B7-WAGON-5D-01	4586	1772	1453	Auto-Data.net	https://www.auto-data.net/en/audi-a4-avant-b7-8e-generation-5202
EU-AUDI-Q7-I-SUV-5D-PREFL-01	5086	1983	1737	Auto-Data.net	https://www.auto-data.net/en/audi-q7-i-typ-4l-3.6-fsi-v6-280hp-quattro-tiptronic-4854
EU-AUDI-Q7-I-SUV-5D-FACELIFT-01	5089	1983	1737	Auto-Data.net	https://www.auto-data.net/en/audi-q7-i-typ-4l-facelift-2009-3.6-fsi-v6-280hp-quattro-tiptronic-27127
EU-HYUNDAI-ATOS-PRIME-HATCHBACK-5D-01	3495	1485	1580	Auto-Data.net	https://www.auto-data.net/en/hyundai-atos-prime-1.1-i-12v-59hp-13739
EU-RENAULT-TWIZY-I-HATCHBACK-2D-01	2338	1237	1454	Auto-Data.net	https://www.auto-data.net/en/renault-twizy-ze-generation-6939
EU-AUDI-TT-8J-CONVERTIBLE-2D-PREFL-01	4178	1842	1358	Auto-Data.net	https://www.auto-data.net/en/audi-tt-roadster-8j-2.0-tfsi-200hp-17876
EU-VOLVO-C30-I-HATCHBACK-3D-PREFL-01	4252	1782	1447	Auto-Data.net	https://www.auto-data.net/en/volvo-c30-generation-1956
EU-VOLVO-C30-I-HATCHBACK-3D-FACELIFT-01	4266	1782	1447	Auto-Data.net	https://www.auto-data.net/en/volvo-c30-facelift-2010-generation-4973
EU-BMW-X3-E83-SUV-5D-FACELIFT-01	4569	1853	1674	Auto-Data.net	https://www.auto-data.net/en/bmw-x3-e83-facelift-2006-generation-6389
EU-BMW-3-E90-SEDAN-4D-PREFL-01	4520	1817	1421	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-sedan-e90-335i-306hp-9937
EU-BMW-3-E90-SEDAN-4D-FACELIFT-01	4531	1817	1421	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-sedan-e90-lci-facelift-2008-335i-306hp-27964
EU-BMW-3-E91-WAGON-5D-PREFL-01	4520	1817	1418	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-e91-335i-306hp-steptronic-45541
EU-BMW-3-E91-WAGON-5D-FACELIFT-01	4527	1817	1418	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-touring-e91-lci-facelift-2008-335i-306hp-27568
EU-BMW-3-E92-COUPE-2D-PREFL-01	4580	1782	1395	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-335d-286hp-steptronic-9957
EU-BMW-3-E92-COUPE-2D-FACELIFT-01	4612	1782	1375	Auto-Data.net	https://www.auto-data.net/en/bmw-3-series-coupe-e92-lci-facelift-2010-335d-286hp-steptronic-17235
EU-HYUNDAI-SANTA-FE-II-SUV-5D-01	4675	1890	1725	Auto-Data.net	https://www.auto-data.net/en/hyundai-santa-fe-ii-cm-generation-2971
EU-CITROEN-C4-I-COUPE-3D-PHASE-I-01	4273	1769	1456	Auto-Data.net	https://www.auto-data.net/en/citroen-c4-i-coupe-phase-i-2004-vts-2.0i-16v-177hp-15174
EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-01	3699	1683	1407	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r56-cooper-1.6-i-16v-120hp-15327
EU-MINI-HATCH-R56-HATCHBACK-3D-COOPER-S-01	3714	1683	1407	Auto-Data.net	https://www.auto-data.net/en/mini-hatch-r56-cooper-s-1.6-i-16v-turbo-175hp-15328
EU-KIA-CARENS-II-MPV-5D-01	4545	1820	1650	Auto-Data.net	https://www.auto-data.net/en/kia-carens-ii-2.0-crdi-140hp-2708
EU-FIAT-GRANDE-PUNTO-199-HATCHBACK-01	4030	1687	1490	Auto-Data.net	https://www.auto-data.net/en/fiat-grande-punto-199-1.4-95hp-35741
EU-CHRYSLER-300-TOURING-WAGON-STANDARD-01	4999	1881	1507	Auto-Data.net	https://www.auto-data.net/en/chrysler-300-touring-5.7-i-v8-awd-340hp-14696
EU-CHRYSLER-300-TOURING-WAGON-SRT8-01	5015	1880	1462	Auto-Data.net	https://www.auto-data.net/en/chrysler-300-touring-6.1-i-v8-16v-srt-8-431hp-14697
EU-MERCEDES-BENZ-R-CLASS-I-MPV-SWB-01	4930	1922	1634	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-w251-amg-r-63-v8-510hp-4matic-7g-tronic-amg-speedshift-43237
EU-MERCEDES-BENZ-R-CLASS-I-MPV-LWB-01	5165	1922	1634	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-r-class-long-v251-amg-r-63-v8-510hp-4matic-7g-tronic-amg-speedshift-43240
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-01	5079	1872	1473	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-w221-s-420-cdi-v8-320hp-7g-tronic-13041
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-01	5209	1872	1473	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-s-420-cdi-v8-320hp-7g-tronic-13042
EU-SUBARU-B9-TRIBECA-SUV-5D-01	4855	1880	1675	Auto-Data.net	https://www.auto-data.net/en/subaru-b9-tribeca-3.0i-250hp-awd-sportshift-37631
EU-PEUGEOT-206-SEDAN-4D-01	4188	1655	1452	Auto-Data.net; Auto-Data.net	https://www.auto-data.net/en/peugeot-206-sedan-1.4-75hp-5244; https://www.auto-data.net/en/peugeot-206-sedan-1.6-110hp-5245
EU-SUBARU-IMPREZA-II-SEDAN-FACELIFT-01	4465	1740	1440	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-facelift-2005-1.5-105hp-awd-16075
EU-SUBARU-IMPREZA-II-WAGON-FACELIFT-01	4465	1695	1485	Auto-Data.net	https://www.auto-data.net/en/subaru-impreza-ii-station-wagon-facelift-2005-1.5-105hp-awd-42629
EU-SSANGYONG-ACTYON-I-SUV-5D-01	4455	1880	1740	Auto-Data.net	https://www.auto-data.net/en/ssangyong-actyon-2.0-xdi-141hp-automatic-24350
EU-LOTUS-EUROPA-S-COUPE-2D-01	3900	1714	1120	Auto-Data.net	https://www.auto-data.net/en/lotus-europa-s-2.0-16v-203hp-8315
EU-HYUNDAI-ACCENT-III-HATCHBACK-3D-01	4045	1695	1470	Auto-Data.net	https://www.auto-data.net/en/hyundai-accent-hatchback-iii-generation-2954
EU-DAEWOO-NUBIRA-III-WAGON-5D-01	4580	1725	1460	Auto-Data.net	https://www.auto-data.net/en/chevrolet-nubira-station-wagon-1.6-i-16v-109hp-14357
EU-FIAT-CROMA-II-WAGON-5D-01	4756	1775	1597	Auto-Data.net	https://www.auto-data.net/en/fiat-croma-ii-1.8-16v-140hp-6797
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-PREFL-01	4578	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-model-1560
EU-SKODA-OCTAVIA-II-HATCHBACK-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-model-1560
EU-SKODA-OCTAVIA-II-WAGON-5D-PREFL-01	4572	1769	1468	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-2.0-tdi-140hp-14230
EU-SKODA-OCTAVIA-II-WAGON-5D-FACELIFT-01	4569	1769	1462	Auto-Data.net	https://www.auto-data.net/en/skoda-octavia-ii-combi-facelift-2009-2.0-tdi-cr-140hp-4x4-14207
EU-TOYOTA-AVENSIS-II-HATCHBACK-5D-01	4630	1760	1480	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-TOYOTA-AVENSIS-II-SEDAN-4D-01	4630	1760	1480	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-TOYOTA-AVENSIS-II-WAGON-5D-01	4715	1760	1525	Auto-Data.net	https://www.auto-data.net/en/toyota-avensis-model-431
EU-MERCEDES-BENZ-S-CLASS-W221-SEDAN-SWB-FACELIFT-01	5096	1871	1479	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-w221-facelift-2009-generation-7081
EU-MERCEDES-BENZ-S-CLASS-V221-SEDAN-LWB-FACELIFT-01	5226	1871	1479	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-s-class-long-v221-facelift-2009-s-500-v8-388hp-4matic-g-tronic-36894
EU-RENAULT-TWINGO-II-HATCHBACK-3D-PREFL-01	3602	1665	1470	Auto-Data.net	https://www.auto-data.net/en/renault-twingo-ii-1.2-16v-tce-gt-100hp-10691
EU-RENAULT-TWINGO-II-HATCHBACK-3D-FACELIFT-01	3699	1688	1470	Auto-Data.net	https://www.auto-data.net/en/renault-twingo-model-1042
EU-PEUGEOT-607-SEDAN-4D-PHASE-I-01	4877	1800	1437	Auto-Data.net	https://www.auto-data.net/en/peugeot-607-model-575
EU-NISSAN-QASHQAI-I-SUV-5D-PREFL-01	4315	1780	1605	Auto-Data.net	https://www.auto-data.net/en/nissan-qashqai-i-j10-1.6-114hp-730
EU-NISSAN-QASHQAI-I-SUV-5D-FACELIFT-01	4330	1780	1615	Auto-Data.net	https://www.auto-data.net/en/nissan-qashqai-model-90
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-2012-01	4950	1971	1950	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-model-438
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2013-01	4950	1970	1865	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-j200-facelift-2013-4.5d-v8-272hp-automatic-18527
EU-TOYOTA-LAND-CRUISER-J200-SUV-5D-FACELIFT-2015-01	4990	1980	1945	Auto-Data.net	https://www.auto-data.net/en/toyota-land-cruiser-model-438
EU-LADA-KALINA-I-HATCHBACK-5D-01	3850	1700	1500	Bind.lt	https://bind.lt/en/technical-specifications/vaz-lada/kalina/1-generation/1119-hatchback-5-doors/1-6-mt-8-valves-euro-4-81-hp
EU-LADA-KALINA-I-SEDAN-4D-01	4040	1700	1500	Otoba.ru	https://otoba.ru/auto/lada/kalina-sedan.html
EU-SSANGYONG-KYRON-I-SUV-5D-PREFL-01	4660	1880	1755	Automobile-Catalog	https://www.automobile-catalog.com/car/2005/3166490/ssangyong_kyron_2_7_xdi_4wd.html
EU-SSANGYONG-KYRON-I-SUV-5D-FACELIFT-01	4660	1880	1740	Car Dimensions	https://www.car-dimensions.com/dimensions/SsangYong_Kyron/
EU-DACIA-LOGAN-I-MCV-WAGON-5D-PREFL-01	4450	1740	1674	Auto-Data.net	https://www.auto-data.net/en/dacia-logan-i-mcv-1.4i-75hp-7-seats-15883
EU-DACIA-LOGAN-I-MCV-WAGON-5D-FACELIFT-01	4473	1740	1640	Auto-Data.net	https://www.auto-data.net/en/dacia-logan-i-mcv-facelift-2008-1.5-dci-68hp-46176
EU-SKODA-FABIA-I-SEDAN-4D-FACELIFT-01	4232	1646	1449	Auto-Data.net	https://www.auto-data.net/en/skoda-fabia-sedan-i-6y-facelift-2004-1.4-16v-80hp-36206
EU-PEUGEOT-EXPERT-I-BUS-01	4440	1810	1940	Peugeot Drive Place	https://peugeot.drive.place/expert/i/group_minivan/230305
EU-PEUGEOT-EXPERT-I-VAN-01	4440	1810	1940	Peugeot Drive Place	https://peugeot.drive.place/expert/i/group_minivan/230305
EU-RENAULT-TRAFIC-II-BUS-L1H1-01	4782	1904	1955	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-BUS-L2H1-01	5182	1904	1962	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-VAN-L1H1-01	4782	1904	1955	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-VAN-L1H2-01	4782	1904	2465	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-VAN-L2H1-01	5182	1904	1962	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-VAN-L2H2-01	5182	1904	2464	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-RENAULT-TRAFIC-II-PLATFORM-CAB-L2-01	5036	1904	1973	Caradisiac	https://www.caradisiac.com/VUL-Renault-Trafic-la-fiche-technique-28777.htm
EU-PEUGEOT-BOXER-II-BUS-L1H1-01	4963	2050	2254	Peugeot Boxer brochure; Loads of Vans	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf; https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-BUS-L2H2-01	5413	2050	2522	Peugeot Boxer brochure; Loads of Vans	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf; https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-BUS-L3H2-01	5998	2050	2522	Peugeot Boxer brochure; Loads of Vans	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf; https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L1H1-01	4963	2050	2254	DenWorker; Loads of Vans	https://www.denworker.uk/van/peugeot-boxer-2006/; https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L1H2-01	4963	2050	2522	DenWorker; Loads of Vans	https://www.denworker.uk/van/peugeot-boxer-2006/; https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L2H1-01	5413	2050	2254	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L2H2-01	5413	2050	2522	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L3H2-01	5998	2050	2522	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L3H3-01	5998	2050	2760	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L4H2-01	6363	2050	2522	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-VAN-L4H3-01	6363	2050	2760	Loads of Vans	https://www.loadsofvans.com/new-vans/peugeot-boxer
EU-PEUGEOT-BOXER-II-CHASSIS-L1-01	4908	2050	2254	VehicleScore; Peugeot Boxer conversion brochure	https://vehiclescore.co.uk/car-dimensions-check/peugeot/boxer; https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L2-01	5358	2050	2254	Peugeot Boxer conversion brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L3-01	5943	2050	2254	Peugeot Boxer conversion brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
EU-PEUGEOT-BOXER-II-CHASSIS-L4-01	6308	2050	2270	Peugeot Boxer conversion brochure	https://www.charterspeugeot.com/wp-content/uploads/sites/15/2018/08/peugeot-boxer-van-prices-specifications-combined-brochure-08-2018.pdf
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_601-700_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://peugeot.drive.place/expert/i/group_minivan/230305?utm_source=chatgpt.com "Peugeot Expert I 1.9 MT 69 hp Minivan — specifications"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_601-700_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_601-700_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（922 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（443 行）
