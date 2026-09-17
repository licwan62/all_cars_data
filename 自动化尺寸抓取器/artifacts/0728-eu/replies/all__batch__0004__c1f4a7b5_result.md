# 任务：all 第 301-400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0004__c1f4a7b5


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

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Ford	Fiesta i	0.9	Schrägheck	Frontantrieb	Benzin	33	45	May 1976	Aug 1983	2024-03-01	321
Ford	Fiesta ii	1.1	Schrägheck	Frontantrieb	Benzin	36	49	May 1986	Feb 1989	2024-03-01	322
Ford	Fiesta i	1.1	Schrägheck	Frontantrieb	Benzin	39	53	May 1976	Aug 1983	2024-03-01	323
Ford	Fiesta i	1.3	Schrägheck	Frontantrieb	Benzin	49	66	Aug 1977	Aug 1983	2024-03-01	324
Ford	Fiesta i	1.6 XR2	Schrägheck	Frontantrieb	Benzin	62	84	Aug 1981	Aug 1983	2024-03-01	325
VW	Passat b7 variant	1.8 TSI	Kombi	Frontantrieb	Benzin	118	160	Aug 2010	Dec 2014	2024-03-01	326
VW	Passat b7 variant	1.6 TDI	Kombi	Frontantrieb	Diesel	77	105	Aug 2010	Dec 2014	2024-03-01	327
Ford	Escort i	1100	Stufenheck	Heckantrieb	Benzin	32	45	Jan 1968	Dec 1974	2024-03-01	328
Ford	Escort ii	1.1	Stufenheck	Heckantrieb	Benzin	32	45	Dec 1974	Aug 1980	2024-03-01	329
Ford	Escort ii	1.1	Stufenheck	Heckantrieb	Benzin	34	46	Jun 1975	Aug 1980	2024-03-01	330
Mercedes-benz	190	E 2.3-16	Stufenheck	Heckantrieb	Benzin	125	170	Sep 1985	Dec 1987	2024-03-01	331
Ford	Escort ii	1.1	Stufenheck	Heckantrieb	Benzin	35	48	Dec 1974	Aug 1980	2024-03-01	332
Ford	Escort ii	1.3	Stufenheck	Heckantrieb	Benzin	40	54	Dec 1974	Aug 1980	2024-03-01	333
Ford	Escort ii	1.3	Stufenheck	Heckantrieb	Benzin	42	57	Dec 1974	Aug 1980	2024-03-01	334
Ford	Escort ii	1.3	Stufenheck	Heckantrieb	Benzin	44	60	Mar 1979	Aug 1980	2024-03-01	335
Mercedes-benz	190	E 2.3-16	Stufenheck	Heckantrieb	Benzin	130	177	Sep 1985	Aug 1988	2024-03-01	336
Mercedes-benz	190	E 2.3-16	Stufenheck	Heckantrieb	Benzin	136	185	Apr 1984	Jan 1987	2024-03-01	337
Mercedes-benz	190	E 2.3	Stufenheck	Heckantrieb	Benzin	97	132	Sep 1986	Aug 1991	2024-03-01	338
Mercedes-benz	190	E 2.3	Stufenheck	Heckantrieb	Benzin	100	136	Oct 1986	Aug 1993	2024-03-01	339
Mercedes-benz	190	E 2.5-16 Evolution	Stufenheck	Heckantrieb	Benzin	143	194	Mar 1989	Aug 1993	2024-03-01	340
Ford	Escort ii	1.3	Stufenheck	Heckantrieb	Benzin	51	70	Dec 1974	Aug 1980	2024-03-01	341
Ford	Escort ii	1.6 RS	Stufenheck	Heckantrieb	Benzin	62	84	Dec 1974	Aug 1980	2024-03-01	342
Ford	Escort ii	2.0 RS	Stufenheck	Heckantrieb	Benzin	80	110	Aug 1975	Aug 1980	2024-03-01	343
Mercedes-benz	190	E 2.5-16	Stufenheck	Heckantrieb	Benzin	150	204	Sep 1988	Aug 1993	2024-03-01	344
Ford	Escort iii	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Aug 1983	Dec 1985	2024-03-01	345
VW	Passat b7 variant	2.0 TSI	Kombi	Frontantrieb	Benzin	155	210	Nov 2010	Dec 2015	2024-03-01	346
Mercedes-benz	190	E 2.6	Stufenheck	Heckantrieb	Benzin	122	166	Sep 1986	Dec 1989	2024-03-01	347
Mercedes-benz	190	D 2.0	Stufenheck	Heckantrieb	Diesel	53	72	Aug 1983	Aug 1989	2024-03-01	348
Mercedes-benz	190	D 2.0	Stufenheck	Heckantrieb	Diesel	55	75	Aug 1989	Aug 1993	2024-03-01	349
Mercedes-benz	190	D 2.5	Stufenheck	Heckantrieb	Diesel	66	90	Apr 1985	Aug 1993	2024-03-01	350
Ford	Escort iv	1.1	Schrägheck	Frontantrieb	Benzin	37	50	Dec 1985	Jul 1990	2024-03-01	351
Ford	Escort iii	1.1	Schrägheck	Frontantrieb	Benzin	40	55	Sep 1980	Aug 1983	2024-03-01	352
Mercedes-benz	190	D 2.5	Stufenheck	Heckantrieb	Diesel	69	94	Aug 1989	Aug 1993	2024-03-01	353
Mercedes-benz	190	Turbo-d 2.5	Stufenheck	Heckantrieb	Diesel	90	122	Feb 1988	Aug 1993	2024-03-01	354
Mercedes-benz	190	Turbo-d 2.5	Stufenheck	Heckantrieb	Diesel	93	126	Feb 1988	Aug 1993	2024-03-01	355
VW	Passat b7 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Aug 2010	Dec 2014	2024-03-01	356
VW	Passat b7 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	103	140	Aug 2010	Dec 2014	2024-03-01	357
VW	Passat b7 variant	2.0 TDI	Kombi	Frontantrieb	Diesel	125	170	Aug 2010	Dec 2014	2024-03-01	358
VW	Passat b7 variant	2.0 TDI 4motion	Kombi	Allrad	Diesel	125	170	Aug 2010	Jan 2013	2024-03-01	359
Mercedes-benz	190	E 2.5-16 Evolution II	Stufenheck	Heckantrieb	Benzin	173	235	May 1990	Aug 1993	2024-03-01	360
VW	Passat b7 variant	1.4 TSI Ecofuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	110	150	Aug 2010	Dec 2014	2024-03-01	361
Mercedes-benz	190	E 2.6	Stufenheck	Heckantrieb	Benzin	118	160	Sep 1986	Aug 1993	2024-03-01	362
Mercedes-benz	Heckflosse	190 C	Stufenheck	Heckantrieb	Benzin	59	80	Apr 1961	Aug 1965	2024-03-01	363
Mercedes-benz	Heckflosse	200	Stufenheck	Heckantrieb	Benzin	61	83	Jul 1965	Feb 1968	2024-03-01	364
Mercedes-benz	Heckflosse	200	Stufenheck	Heckantrieb	Benzin	70	95	Jul 1965	Feb 1968	2024-03-01	365
Mercedes-benz	Heckflosse	220 B	Stufenheck	Heckantrieb	Benzin	70	95	Aug 1959	Aug 1965	2024-03-01	366
Mercedes-benz	Heckflosse	220 SB	Stufenheck	Heckantrieb	Benzin	81	110	Aug 1959	Aug 1965	2024-03-01	367
Mercedes-benz	Heckflosse	220 SEB	Stufenheck	Heckantrieb	Benzin	88	120	Aug 1959	Aug 1965	2024-03-01	368
Mercedes-benz	Heckflosse	230	Stufenheck	Heckantrieb	Benzin	77	105	Jul 1965	Feb 1968	2024-03-01	369
Renault	Megane iii grandtour	1.5 DCI	Kombi	Frontantrieb	Diesel	78	106	Feb 2009	Aug 2015	2024-03-01	370
Renault	Megane iii	1.5 DCI	Schrägheck	Frontantrieb	Diesel	78	106	Dec 2008	Jan 2016	2026-03-01	371
Mercedes-benz	Heckflosse	230	Stufenheck	Heckantrieb	Benzin	88	120	Jun 1966	Dec 1967	2024-03-01	372
Mercedes-benz	Heckflosse	230 S	Stufenheck	Heckantrieb	Benzin	88	120	Jul 1965	Jan 1968	2024-03-01	373
Mercedes-benz	Heckflosse	200 D	Stufenheck	Heckantrieb	Diesel	40	55	Jul 1965	Feb 1968	2024-03-01	374
Mercedes-benz	Heckflosse	190 DC	Stufenheck	Heckantrieb	Diesel	40	54	Jun 1961	Aug 1965	2024-03-01	375
Mitsubishi	Asx	1.8 Di-d	SUV	Frontantrieb	Diesel	85	116	Jun 2010	-	2024-03-01	376
Mercedes-benz	/8	230.6	Stufenheck	Heckantrieb	Benzin	88	120	Jan 1968	Nov 1976	2024-03-01	377
Mitsubishi	Asx	1.8	SUV	Frontantrieb	Benzin	102	139	Feb 2010	-	2024-03-01	378
Mercedes-benz	/8	250	Stufenheck	Heckantrieb	Benzin	85	116	Jan 1968	Aug 1972	2024-03-01	379
Mercedes-benz	/8	250	Stufenheck	Heckantrieb	Benzin	96	130	Jul 1968	Aug 1972	2024-03-01	380
Mercedes-benz	/8	280	Stufenheck	Heckantrieb	Benzin	118	160	Jun 1972	Nov 1976	2024-03-01	381
Mercedes-benz	/8	280 E	Stufenheck	Heckantrieb	Benzin	136	185	Jun 1972	Nov 1976	2024-03-01	382
Mercedes-benz	/8	250 2.8	Stufenheck	Heckantrieb	Benzin	96	130	Jun 1972	Nov 1976	2024-03-01	383
Mercedes-benz	/8	250 C	Coupe	Heckantrieb	Benzin	96	130	Apr 1969	Jun 1972	2024-03-01	384
Mercedes-benz	/8	250 CE	Coupe	Heckantrieb	Benzin	110	150	Apr 1969	Apr 1972	2024-03-01	385
Mercedes-benz	/8	280 C	Coupe	Heckantrieb	Benzin	118	160	Jun 1972	Feb 1977	2024-03-01	386
Mercedes-benz	/8	280 CE	Coupe	Heckantrieb	Benzin	136	185	Jun 1972	Jan 1977	2024-03-01	387
Mercedes-benz	/8	250 C 2.8	Coupe	Heckantrieb	Benzin	96	130	Jun 1972	Nov 1976	2024-03-01	388
Mercedes-benz	/8	200	Stufenheck	Heckantrieb	Benzin	63	86	Jan 1968	Jan 1977	2024-03-01	389
Mercedes-benz	/8	200	Stufenheck	Heckantrieb	Benzin	70	95	Jan 1968	Jan 1977	2024-03-01	390
Mercedes-benz	/8	220	Stufenheck	Heckantrieb	Benzin	66	90	Jan 1968	Jul 1973	2024-03-01	391
Mercedes-benz	/8	220	Stufenheck	Heckantrieb	Benzin	77	105	Jan 1968	Jul 1973	2024-03-01	392
Mercedes-benz	/8	230.4	Stufenheck	Heckantrieb	Benzin	81	110	Aug 1973	Dec 1976	2024-03-01	393
Mercedes-benz	/8	200 D	Stufenheck	Heckantrieb	Diesel	40	55	Jan 1968	Jan 1977	2024-03-01	394
Mercedes-benz	/8	220 D	Stufenheck	Heckantrieb	Diesel	44	60	Jan 1968	Jan 1977	2024-03-01	395
Mercedes-benz	/8	240 D	Stufenheck	Heckantrieb	Diesel	48	65	Aug 1973	Jan 1977	2024-03-01	396
Mercedes-benz	/8	240 D 3.0	Stufenheck	Heckantrieb	Diesel	59	80	Aug 1974	Nov 1976	2024-03-01	397
Mercedes-benz	123	200	Stufenheck	Heckantrieb	Benzin	62	84	Feb 1976	Aug 1980	2024-03-01	398
Mercedes-benz	123	200	Stufenheck	Heckantrieb	Benzin	69	94	Feb 1976	Aug 1980	2024-03-01	399
Mercedes-benz	123	200	Stufenheck	Heckantrieb	Benzin	74	101	Jun 1980	Nov 1985	2024-03-01	400
Mercedes-benz	123	200	Stufenheck	Heckantrieb	Benzin	80	109	Jun 1980	Nov 1985	2024-03-01	401
Mercedes-benz	123	230 E	Stufenheck	Heckantrieb	Benzin	100	136	Apr 1980	Dec 1985	2024-03-01	402
Mercedes-benz	123	230	Stufenheck	Heckantrieb	Benzin	80	109	Feb 1976	Mar 1981	2024-03-01	403
Mercedes-benz	123	250	Stufenheck	Heckantrieb	Benzin	103	140	Oct 1979	Jul 1985	2024-03-01	404
Mercedes-benz	123	280	Stufenheck	Heckantrieb	Benzin	115	156	Feb 1976	Aug 1981	2024-03-01	405
Mercedes-benz	123	280 E	Stufenheck	Heckantrieb	Benzin	130	177	Aug 1976	Aug 1981	2024-03-01	406
Mercedes-benz	123	280 E	Stufenheck	Heckantrieb	Benzin	136	185	Feb 1976	Nov 1985	2024-03-01	407
Mercedes-benz	123	200 D	Stufenheck	Heckantrieb	Diesel	40	55	Jul 1976	Feb 1979	2024-03-01	408
Mercedes-benz	123	200 D	Stufenheck	Heckantrieb	Diesel	44	60	Mar 1979	Nov 1985	2024-03-01	409
Mercedes-benz	123	220 D	Stufenheck	Heckantrieb	Diesel	44	60	Jan 1976	Feb 1979	2024-03-01	410
Mercedes-benz	123	220 D	Stufenheck	Heckantrieb	Diesel	49	67	Jan 1977	Mar 1979	2024-03-01	411
Mercedes-benz	123	240 D	Stufenheck	Heckantrieb	Diesel	53	72	Mar 1979	Nov 1985	2024-03-01	412
Mercedes-benz	123	240 D	Stufenheck	Heckantrieb	Diesel	48	65	Feb 1976	Feb 1979	2024-03-01	413
Mercedes-benz	123	300 D	Stufenheck	Heckantrieb	Diesel	59	80	Feb 1976	Jul 1980	2024-03-01	415
Mercedes-benz	123	300 D	Stufenheck	Heckantrieb	Diesel	65	88	Mar 1979	Nov 1985	2024-03-01	416
Mercedes-benz	123	300 Turbo-d	Stufenheck	Heckantrieb	Diesel	92	125	Aug 1981	Jul 1985	2024-03-01	417
Saab	9-5	2.0 Ttid	Stufenheck	Frontantrieb	Diesel	140	190	May 2010	Jan 2012	2024-03-01	418
Mercedes-benz	123	250	Stufenheck	Heckantrieb	Benzin	95	129	Feb 1976	Oct 1979	2024-03-01	419
Mercedes-benz	123 t-Model	200 T	Kombi	Heckantrieb	Benzin	74	101	Nov 1980	Nov 1985	2024-03-01	421
Mercedes-benz	123 t-Model	200 T	Kombi	Heckantrieb	Benzin	80	109	Nov 1980	Nov 1985	2024-03-01	422


--- Round 1 / 首次发送 ---
## 更新点

* 完成 Mercedes-Benz 190（W201）车型簇，共覆盖 16 个输入 Ktype，生成 24 条 READY 映射。
* 普通 W201 按 1988 年 9 月改款节点拆分；190 E 2.6 改款前因车长不同单独建组。
* 190 E 2.3-16 与标准 190 E 2.5-16 的外廓三维一致，复用同一尺寸组；Evolution I、Evolution II 因宽体及空气动力套件差异分别建组。Mercedes-Benz 官方档案直接确认了相应 Baumuster、生产边界和三维。([marsClassic][1])
* 普通车身改款前采用 `4420 × 1678 × 1390 mm`，改款后采用 `4448 × 1690 × 1375 mm`；改款前 190 E 2.6 为 `4428 × 1678 × 1390 mm`。([marsClassic][2])
* 本轮首次闭合 6 个尺寸组，没有重复为发动机、功率或燃料差异建组。

## 当前批次进度

* 输入 Ktype：100
* 已闭合输入 Ktype：16/100
* READY 映射行：24
* 待建立映射的输入 Ktype：84/100
* 已确认尺寸组：6
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
331	331	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
336	336	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
337	337	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
338_prefl	338	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
338_facelift	338	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
339_prefl	339	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
339_facelift	339	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
340	340	Sedan	190 (W201)	201.036	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EVO1-01	HIGH	Evolution I宽体外廓；上游结束月宽于该特定版本。	READY
344	344	Sedan	190 (W201)	201.035	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.035标准16V外廓。	READY
347_prefl	347	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	HIGH	1988年9月改款前2.6专属前部外廓。	READY
347_facelift	347	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
348_prefl	348	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
348_facelift	348	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
349	349	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	改款后201.122物理外廓。	READY
350_prefl	350	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
350_facelift	350	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
353	353	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	改款后201.126物理外廓。	READY
354_prefl	354	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
354_facelift	354	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
355_prefl	355	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
355_facelift	355	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
360	360	Sedan	190 (W201)	201.036	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EVO2-01	HIGH	Evolution II专属空气动力套件外廓；上游结束月宽于该特定版本。	READY
362_prefl	362	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	HIGH	1988年9月改款前2.6专属前部外廓。	READY
362_facelift	362	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	4430	1706	1361	Mercedes-Benz Public Archive;Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-23-16.xhtml?oid=5476;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16.xhtml?oid=5511
EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	4420	1678	1390	Mercedes-Benz Public Archive;Automobile-Catalog	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-D-25.xhtml?oid=5481;https://www.automobile-catalog.com/car/1986/1477385/mercedes-benz_190_e_2_3_ece-version.html
EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	4448	1690	1375	Mercedes-Benz Public Archive;Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-D.xhtml?oid=5513;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26.xhtml?oid=5502
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO1-01	4430	1720	1342	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16-Evolution.xhtml?oid=5515
EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	4428	1678	1390	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26--W-201-E-26-1986---1988.xhtml?oid=5475
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO2-01	4543	1720	1342	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16-Evolution-II.xhtml?oid=5505
```

## 下一步优先处理

1. 批量闭合 Mercedes-Benz Heckflosse 的 W110、W111 车身分支。
2. 继续处理 `/8` 的 W114 Coupe、W114/W115 Sedan 尺寸组。
3. 处理 123 系列 Sedan 与 T-Model，随后集中处理 Ford Fiesta、Escort 和 VW Passat B7 Variant 复用簇。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-23-16.xhtml?oid=5476 "190 E 2.3-16"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-D-25.xhtml?oid=5481 "190 D 2.5"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 闭合 **Heckflosse W110** 与 **W111** 两个尺寸组，共新增 11 条 Ktype 映射。W110 的 230 从 105 hp 升至 120 hp 时仍为 `110.011`，未改变物理外廓；W111 的 220 S 与 230 S 也无外形差异。([marsClassic][1])
* 闭合 **W123 标准四门轿车**、**W123 北美/日本出口加长保险杠轿车**和 **S123 T-Model** 三个尺寸组，共新增 22 条 Ktype 映射。
* W123 普通汽油与柴油版本统一复用 `4725 × 1786 × 1438 mm` 标准轿车尺寸组；发动机、功率和 1980—1982 年车型改进均未触发重复建组。([marsClassic][2])
* `300 D Turbodiesel` 为北美及日本出口车型，官方长度为 `4848 mm`，因此使用独立加长保险杠尺寸组；S123 200 T 使用 `4725 × 1786 × 1470 mm` 旅行车尺寸组。([marsClassic][3])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：49/100
* PENDING 输入 Ktype：51/100
* READY 映射行：57
* 已确认尺寸组：11
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
363	363	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
364	364	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
365	365	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
366	366	Sedan	Heckflosse (W111)	111.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
367	367	Sedan	Heckflosse (W111)	111.012	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
368	368	Sedan	Heckflosse (W111)	111.014	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
369	369	Sedan	Heckflosse (W110)	110.011	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110六缸230四门轿车外廓。	READY
372	372	Sedan	Heckflosse (W110)	110.011	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	1966年功率升级未改变外廓。	READY
373	373	Sedan	Heckflosse (W111)	111.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	230 S沿用W111四门轿车外廓。	READY
374	374	Sedan	Heckflosse (W110)	110.110	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110柴油四门轿车外廓。	READY
375	375	Sedan	Heckflosse (W110)	110.110	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110柴油四门轿车外廓。	READY
398	398	Sedan	123 (W123)	123.020	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
399	399	Sedan	123 (W123)	123.020	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
400	400	Sedan	123 (W123)	123.220	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	M102发动机未改变标准轿车外廓。	READY
401	401	Sedan	123 (W123)	123.220	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	M102发动机未改变标准轿车外廓。	READY
402	402	Sedan	123 (W123)	123.223	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
403	403	Sedan	123 (W123)	123.023	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
404	404	Sedan	123 (W123)	123.026	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
405	405	Sedan	123 (W123)	123.030	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
406	406	Sedan	123 (W123)	123.033	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
407	407	Sedan	123 (W123)	123.033	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
408	408	Sedan	123 (W123)	123.120	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
409	409	Sedan	123 (W123)	123.120	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
410	410	Sedan	123 (W123)	123.126	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
411	411	Sedan	123 (W123)	123.126	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率差异未改变标准轿车外廓。	READY
412	412	Sedan	123 (W123)	123.123	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
413	413	Sedan	123 (W123)	123.123	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	早期功率版本未改变标准轿车外廓。	READY
415	415	Sedan	123 (W123)	123.130	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
416	416	Sedan	123 (W123)	123.130	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
417	417	Sedan	123 (W123)	123.133	4	EU-MERCEDES-BENZ-123-W123-SEDAN-EXPORT-BUMPER-01	HIGH	北美及日本出口型加长保险杠外廓。	READY
419	419	Sedan	123 (W123)	123.026	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	早期功率版本未改变标准轿车外廓。	READY
421	421	Wagon	123 T-Model (S123)	123.280	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH	S123五门旅行车外廓。	READY
422	422	Wagon	123 T-Model (S123)	123.280	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH	S123五门旅行车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	4730	1795	1495	Mercedes-Benz Public Archive 190 c;Mercedes-Benz Public Archive 200 D;Mercedes-Benz Public Archive W110 model overview	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-c.xhtml?oid=5129;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-D.xhtml?oid=5122;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Fintail-Mercedes-four-cylinder-models-W-110-1961---1968.xhtml?oid=5111
EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	4875	1795	1510	Mercedes-Benz Public Archive 220 SEb;Mercedes-Benz Public Archive W111/W112 model overview	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-SEb.xhtml?oid=4898;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Fintail-Mercedes-six-cylinder-models-W-111-W-112-1959---1968.xhtml?oid=4888
EU-MERCEDES-BENZ-123-W123-SEDAN-01	4725	1786	1438	Mercedes-Benz Public Archive 230 E;Mercedes-Benz Public Archive 240 D	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-E.xhtml?oid=5098;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/240-D.xhtml?oid=5094
EU-MERCEDES-BENZ-123-W123-SEDAN-EXPORT-BUMPER-01	4848	1786	1438	Mercedes-Benz Public Archive 300 D Turbodiesel	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-D-Turbodiesel.xhtml?oid=5103
EU-MERCEDES-BENZ-123-S123-WAGON-01	4725	1786	1470	Mercedes-Benz Public Archive 200 T	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-T.xhtml?oid=5383
```

## 下一步优先处理

1. 闭合 Mercedes-Benz `/8` 的 W114/W115 四门轿车、改款前后外廓和 C114 双门 Coupe。
2. 批量处理 Ford Fiesta、Escort 代际及门数分支。
3. 处理 Passat B7 Variant、Megane III、ASX 和 Saab 9-5 高复用车型簇。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-c.xhtml?oid=5129 "190 c"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-E.xhtml?oid=5098 "
            230 E

    "
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-D-Turbodiesel.xhtml?oid=5103 "300 D Turbodiesel"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 Mercedes-Benz `/8` 车型簇，新增 20 条 READY 映射。
* W114 六缸 Sedan、W115 四缸/柴油 Sedan 的官方三维均为 `4680 × 1770 × 1440 mm`。1973 年改款改变了格栅、保险杠及外部饰件，但未改变三维，因此尺寸事实层复用同一 Sedan 组，不拆 `prefl/facelift`。([marsClassic][1])
* C114 Coupe 各发动机版本和改款前后均复用 `4680 × 1790 × 1395 mm`；仅与 Sedan 按车身形式分组。([marsClassic][2])
* 本轮首次创建 2 个尺寸组；没有对发动机、功率或燃料差异重复建组。

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：69/100
* PENDING 输入 Ktype：31/100
* READY 映射行：77
* 已确认尺寸组：13
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
377	377	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
379	379	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
380	380	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
381	381	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
382	382	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
383	383	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
384	384	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
385	385	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
386	386	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
387	387	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
388	388	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
389	389	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
390	390	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
391	391	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
392	392	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
393	393	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
394	394	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
395	395	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
396	396	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
397	397	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	4680	1770	1440	Mercedes-Benz Public Archive 230.6;Mercedes-Benz Public Archive 220/8	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/2306.xhtml?oid=5178;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/2208.xhtml?oid=5241
EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	4680	1790	1395	Mercedes-Benz Public Archive 250 C;Mercedes-Benz Public Archive 280 CE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-C.xhtml?oid=4586;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-CE.xhtml?oid=4582
```

## 下一步优先处理

1. 批量闭合 VW Passat B7 Variant、Renault Mégane III Hatchback/Grandtour、Mitsubishi ASX 与 Saab 9-5 II。
2. 最后处理 Ford Fiesta I/II 与 Escort I—IV 的代际、门数和 Sedan/Hatchback 物理分支。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Stroke-Eight-saloons-Types-200-D---280-E-114-115-series-1973---1976.xhtml?oid=5174 "\"Stroke Eight\" saloons, Types 200 D - 280 E (114, 115 series), 1973 - 1976"
[2]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-C.xhtml?oid=4586&utm_source=chatgpt.com "250 C"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 闭合 VW Passat B7 Variant 车型簇，8 个 Ktype 复用同一 `3C` 五门旅行车尺寸组。Volkswagen 官方资料给出的 Variant 三维为 `4771 × 1820 × 1508 mm`。([Volkswagen Newsroom][1])
* 闭合 Renault Mégane III Hatchback 与 Grandtour 两个物理车身组。官方手册确认五门 Hatchback 为 `4295 × 1808 × 1471 mm`；Grandtour 按独立旅行车外廓建组。
* 闭合 Mitsubishi ASX I 与 Saab 9-5 II Sedan；发动机和燃料差异未触发重复尺寸组。ASX 采用明确标注不含后视镜宽度的 `4295 × 1770 × 1615 mm`，Saab 9-5 II 为 `5008 × 1868 × 1466 mm`。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：82/100
* PENDING 输入 Ktype：18/100
* READY 映射行：90
* 已确认尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
326	326	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
327	327	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
346	346	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
356	356	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
357	357	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	4MOTION未改变基础外廓。	READY
358	358	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
359	359	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	4MOTION未改变基础外廓。	READY
361	361	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	EcoFuel动力系统未改变基础外廓。	READY
370	370	Wagon	Mégane III	K95	5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Mégane III Grandtour五门旅行车外廓。	READY
371	371	Hatchback	Mégane III	B95	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH	Mégane III五门掀背车外廓。	READY
376	376	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH	ASX I五门SUV外廓。	READY
378	378	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH	汽油动力未改变ASX I基础外廓。	READY
418	418	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-01	HIGH	YS3G四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-PASSAT-B7-VARIANT-WAGON-01	4771	1820	1508	Volkswagen Newsroom Passat B7 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Automobile-Catalog Renault Megane Estate Grandtour 1.5 dCi 110	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471	Renault official X95 owner manual	https://cdn.group.renault.com/ren/ru/manuals/Fluence_manual_260513.pdf.asset.pdf/59cdae6519.pdf
EU-MITSUBISHI-ASX-I-SUV-01	4295	1770	1615	Automobile-Catalog Mitsubishi ASX 1.8 DI-D 2WD	https://www.automobile-catalog.com/car/2010/2009720/mitsubishi_asx_1_8_di-d_2wd.html
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466	Automobile-Catalog Saab 9-5 2.0 TTiD	https://www.automobile-catalog.com/car/2010/3038975/saab_9-5_2_0_ttid.html
```

## 下一步优先处理

集中闭合剩余 18 个 Ford Ktype：Fiesta I/II 以及 Escort I—IV，优先确认 Escort Sedan 的二门/四门边界和 Escort III/IV Hatchback 的三门/五门分支。

推进信号：CONTINUE

[1]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037 "Vehicle data Passat B7 profile | Volkswagen Newsroom"
[2]: https://www.automobile-catalog.com/car/2010/2009720/mitsubishi_asx_1_8_di-d_2wd.html?utm_source=chatgpt.com "2010 Mitsubishi ASX 1.8 DI-D 2WD Specs Review (85 kW / 116 PS / 114 hp) (since June 2010 for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 闭合 Fiesta I、Fiesta II 共 5 个 Ktype，新增 8 条 READY 映射。
* Fiesta I 按 **1981 年 9 月改款前后**拆分基础外廓；1.3 长保险杠外廓和 XR2 专属外廓独立建组。Fiesta I 全系均为三门 Hatchback。([汽车目录][1])
* Fiesta II Ktype `322` 对应 `FBD` 三门 Hatchback，采用该 49 hp 生产阶段的完整不含后视镜三维。([汽车目录][2])

## 当前批次进度

* 输入 Ktype：100
* READY 输入 Ktype：87/100
* PENDING 输入 Ktype：13/100
* READY 映射行：98
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
321_prefl	321	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	HIGH	1981年9月前标准外廓。	READY
321_facelift	321	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	HIGH	1981年9月后改款外廓。	READY
322	322	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	HIGH	FBD三门掀背车外廓。	READY
323_prefl	323	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	HIGH	1981年9月前标准外廓。	READY
323_facelift	323	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	上游功率标注跨越改款节点，按生产期拆分。	READY
324_prefl	324	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	HIGH	改款前长保险杠外廓。	READY
324_facelift	324	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	HIGH	改款后长保险杠外廓。	READY
325	325	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	HIGH	XR2专属外部包围外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	3565	1567	1360	Automobile-Catalog Ford Fiesta 1.0 1977	https://www.automobile-catalog.com/car/1977/27770/ford_fiesta_1_0.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359	Automobile-Catalog Ford Fiesta 1.0 1983	https://www.automobile-catalog.com/car/1983/922775/ford_fiesta_1_0.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	3609	1567	1360	Automobile-Catalog Ford Fiesta S 1.3 1977	https://www.automobile-catalog.com/car/1977/40610/ford_fiesta_s_1_3.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	3718	1567	1359	Automobile-Catalog Ford Fiesta 1.3 Ghia 1983	https://www.automobile-catalog.com/car/1983/922730/ford_fiesta_1_3_ghia.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	3718	1580	1371	Automobile-Catalog Ford Fiesta XR-2 1981	https://www.automobile-catalog.com/car/1981/922895/ford_fiesta_xr-2.html
EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	3648	1585	1376	Automobile-Catalog Ford Fiesta 1.1 Super catalyst 1986;Auto-Data Ford Fiesta II 1.1 FBD 49 Hp	https://www.automobile-catalog.com/car/1986/941225/ford_fiesta_1_1_super_cat.html;https://www.auto-data.net/en/ford-fiesta-ii-mk2-1.1-fbd-49hp-8066
```

## 下一步优先处理

集中闭合剩余 13 个 Escort Ktype：先处理 Escort I/II 的二门与四门 Sedan 分支及 RS 专属外廓，再处理 Escort III/IV 的三门与五门 Hatchback 分支。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1981/27770/ford_fiesta_1_0.html?utm_source=chatgpt.com "1981 Ford Fiesta 1.0 Specs Review (33 kW / 45 PS / 44 hp) (up to September 1981 for Europe )"
[2]: https://www.automobile-catalog.com/car/1986/941225/ford_fiesta_1_1_super_cat.html?utm_source=chatgpt.com "1986 Ford Fiesta 1.1 Super catalyst Specs Review (36 kW / 49 PS / 48 hp) (since November 1986 for Europe )"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_301-400_ktype_dimension_mapping_final.tsv
- all_301-400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 完成最后 13 个 Ford Escort Ktype，并按已确认的门数、改款和特殊外廓生成派生映射。
* Escort I 的 Ktype `328` 同时覆盖 2/4 门及改款前后车身，因此拆为四条映射；Escort II 普通版本的 2/4 门共用同一尺寸组，RS2000 因独立前部外形使用专属尺寸组。([汽车目录][1])
* Escort III 的 3/5 门分别落映射，但同阶段共用尺寸组；早期与后期高度不同，分别使用两个组。Escort IV 的 3/5 门共用 `4022 × 1640 × 1385 mm` 尺寸组。([汽车目录][2])
* 已完成固定表头、唯一主键、输入覆盖、外键闭合、正整数三维和来源非空检查。

## 当前批次进度

* 输入 Ktype：100/100
* READY 输入 Ktype：100/100
* PENDING 输入 Ktype：0/100
* 最终 Ktype 映射行：124
* 最终 DIMENSION_GROUP：31
* 映射引用闭合：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
321_prefl	321	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	HIGH	1981年9月前标准外廓。	READY
321_facelift	321	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	HIGH	1981年9月后改款外廓。	READY
322	322	Hatchback	Fiesta II	FBD	3	EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	HIGH	FBD三门掀背车外廓。	READY
323_prefl	323	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	HIGH	1981年9月前标准外廓。	READY
323_facelift	323	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	MEDIUM	上游功率标注跨越改款节点，按生产期拆分。	READY
324_prefl	324	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	HIGH	改款前长保险杠外廓。	READY
324_facelift	324	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	HIGH	改款后长保险杠外廓。	READY
325	325	Hatchback	Fiesta I	GFBT	3	EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	HIGH	XR2专属外部包围外廓。	READY
326	326	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
327	327	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
328_2dr_prefl	328	Sedan	Escort I	AFH	2	EU-FORD-ESCORT-I-SEDAN-PREFL-01	HIGH	Escort I两门轿车改款前外廓。	READY
328_2dr_facelift	328	Sedan	Escort I	AFH	2	EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH	Escort I两门轿车改款后外廓。	READY
328_4dr_prefl	328	Sedan	Escort I	ATH	4	EU-FORD-ESCORT-I-SEDAN-PREFL-01	HIGH	Escort I四门轿车改款前外廓。	READY
328_4dr_facelift	328	Sedan	Escort I	ATH	4	EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	HIGH	Escort I四门轿车改款后外廓。	READY
329_2dr	329	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
329_4dr	329	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
330_2dr	330	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
330_4dr	330	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
331	331	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
332_2dr	332	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
332_4dr	332	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
333_2dr	333	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
333_4dr	333	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
334_2dr	334	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
334_4dr	334	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
335_2dr	335	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
335_4dr	335	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
336	336	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
337	337	Sedan	190 (W201)	201.034	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.034标准16V外廓。	READY
338_prefl	338	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
338_facelift	338	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
339_prefl	339	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
339_facelift	339	Sedan	190 (W201)	201.028	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
340	340	Sedan	190 (W201)	201.036	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EVO1-01	HIGH	Evolution I宽体外廓；上游结束月宽于该特定版本。	READY
341_2dr	341	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II两门轿车外廓。	READY
341_4dr	341	Sedan	Escort II	ATH	4	EU-FORD-ESCORT-II-SEDAN-01	HIGH	Escort II四门轿车外廓。	READY
342	342	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-SEDAN-01	HIGH	1.6 RS两门运动版；基础外廓三维与标准Sedan一致。	READY
343	343	Sedan	Escort II	ATH	2	EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	HIGH	RS2000前部外形造成专属车长。	READY
344	344	Sedan	190 (W201)	201.035	4	EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	HIGH	201.035标准16V外廓。	READY
345_3dr	345	Hatchback	Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-LATE-01	HIGH	Escort III后期三门掀背车外廓。	READY
345_5dr	345	Hatchback	Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-LATE-01	HIGH	Escort III后期五门掀背车外廓。	READY
346	346	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
347_prefl	347	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	HIGH	1988年9月改款前2.6专属前部外廓。	READY
347_facelift	347	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
348_prefl	348	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
348_facelift	348	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
349	349	Sedan	190 (W201)	201.122	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	改款后201.122物理外廓。	READY
350_prefl	350	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
350_facelift	350	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
351_3dr	351	Hatchback	Escort IV	GAF	3	EU-FORD-ESCORT-IV-HATCHBACK-01	HIGH	Escort IV三门掀背车外廓。	READY
351_5dr	351	Hatchback	Escort IV	GAF	5	EU-FORD-ESCORT-IV-HATCHBACK-01	HIGH	Escort IV五门掀背车外廓。	READY
352_3dr	352	Hatchback	Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-EARLY-01	HIGH	Escort III早期三门掀背车外廓。	READY
352_5dr	352	Hatchback	Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-EARLY-01	HIGH	Escort III早期五门掀背车外廓。	READY
353	353	Sedan	190 (W201)	201.126	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	改款后201.126物理外廓。	READY
354_prefl	354	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
354_facelift	354	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
355_prefl	355	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	HIGH	1988年9月改款前物理外廓。	READY
355_facelift	355	Sedan	190 (W201)	201.128	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
356	356	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
357	357	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	4MOTION未改变基础外廓。	READY
358	358	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	B7 Variant五门旅行车外廓。	READY
359	359	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	4MOTION未改变基础外廓。	READY
360	360	Sedan	190 (W201)	201.036	4	EU-MERCEDES-BENZ-190-W201-SEDAN-EVO2-01	HIGH	Evolution II专属空气动力套件外廓；上游结束月宽于该特定版本。	READY
361	361	Wagon	Passat B7	3C	5	EU-VW-PASSAT-B7-VARIANT-WAGON-01	HIGH	EcoFuel动力系统未改变基础外廓。	READY
362_prefl	362	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	HIGH	1988年9月改款前2.6专属前部外廓。	READY
362_facelift	362	Sedan	190 (W201)	201.029	4	EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	HIGH	1988年9月改款后物理外廓。	READY
363	363	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
364	364	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
365	365	Sedan	Heckflosse (W110)	110.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110四门轿车外廓。	READY
366	366	Sedan	Heckflosse (W111)	111.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
367	367	Sedan	Heckflosse (W111)	111.012	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
368	368	Sedan	Heckflosse (W111)	111.014	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	W111四门轿车外廓。	READY
369	369	Sedan	Heckflosse (W110)	110.011	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110六缸230四门轿车外廓。	READY
370	370	Wagon	Mégane III	K95	5	EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	HIGH	Mégane III Grandtour五门旅行车外廓。	READY
371	371	Hatchback	Mégane III	B95	5	EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	HIGH	Mégane III五门掀背车外廓。	READY
372	372	Sedan	Heckflosse (W110)	110.011	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	1966年功率升级未改变外廓。	READY
373	373	Sedan	Heckflosse (W111)	111.010	4	EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	HIGH	230 S沿用W111四门轿车外廓。	READY
374	374	Sedan	Heckflosse (W110)	110.110	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110柴油四门轿车外廓。	READY
375	375	Sedan	Heckflosse (W110)	110.110	4	EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	HIGH	W110柴油四门轿车外廓。	READY
376	376	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH	ASX I五门SUV外廓。	READY
377	377	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
378	378	SUV	ASX I		5	EU-MITSUBISHI-ASX-I-SUV-01	HIGH	汽油动力未改变ASX I基础外廓。	READY
379	379	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
380	380	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
381	381	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
382	382	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
383	383	Sedan	Stroke Eight (/8)	W114	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W114四门轿车外廓。	READY
384	384	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
385	385	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
386	386	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
387	387	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
388	388	Coupe	Stroke Eight (/8)	C114	2	EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	HIGH	C114双门Coupe外廓。	READY
389	389	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
390	390	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
391	391	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
392	392	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
393	393	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
394	394	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
395	395	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
396	396	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
397	397	Sedan	Stroke Eight (/8)	W115	4	EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	HIGH	W115四门轿车外廓。	READY
398	398	Sedan	123 (W123)	123.020	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
399	399	Sedan	123 (W123)	123.020	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
400	400	Sedan	123 (W123)	123.220	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	M102发动机未改变标准轿车外廓。	READY
401	401	Sedan	123 (W123)	123.220	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	M102发动机未改变标准轿车外廓。	READY
402	402	Sedan	123 (W123)	123.223	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
403	403	Sedan	123 (W123)	123.023	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
404	404	Sedan	123 (W123)	123.026	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
405	405	Sedan	123 (W123)	123.030	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
406	406	Sedan	123 (W123)	123.033	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
407	407	Sedan	123 (W123)	123.033	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
408	408	Sedan	123 (W123)	123.120	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
409	409	Sedan	123 (W123)	123.120	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
410	410	Sedan	123 (W123)	123.126	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
411	411	Sedan	123 (W123)	123.126	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率差异未改变标准轿车外廓。	READY
412	412	Sedan	123 (W123)	123.123	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
413	413	Sedan	123 (W123)	123.123	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	早期功率版本未改变标准轿车外廓。	READY
415	415	Sedan	123 (W123)	123.130	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	W123标准四门轿车外廓。	READY
416	416	Sedan	123 (W123)	123.130	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	功率升级未改变标准轿车外廓。	READY
417	417	Sedan	123 (W123)	123.133	4	EU-MERCEDES-BENZ-123-W123-SEDAN-EXPORT-BUMPER-01	HIGH	北美及日本出口型加长保险杠外廓。	READY
418	418	Sedan	9-5 II	YS3G	4	EU-SAAB-9-5-II-YS3G-SEDAN-01	HIGH	YS3G四门轿车外廓。	READY
419	419	Sedan	123 (W123)	123.026	4	EU-MERCEDES-BENZ-123-W123-SEDAN-01	HIGH	早期功率版本未改变标准轿车外廓。	READY
421	421	Wagon	123 T-Model (S123)	123.280	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH	S123五门旅行车外廓。	READY
422	422	Wagon	123 T-Model (S123)	123.280	5	EU-MERCEDES-BENZ-123-S123-WAGON-01	HIGH	S123五门旅行车外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_301-400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-PREFL-01	3565	1567	1360	Automobile-Catalog Ford Fiesta 1.0 1977	https://www.automobile-catalog.com/car/1977/27770/ford_fiesta_1_0.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-FACELIFT-01	3648	1567	1359	Automobile-Catalog Ford Fiesta 1.0 1983	https://www.automobile-catalog.com/car/1983/922775/ford_fiesta_1_0.html
EU-FORD-FIESTA-II-FBD-HATCHBACK-3D-01	3648	1585	1376	Automobile-Catalog Ford Fiesta 1.1 Super catalyst 1986;Auto-Data Ford Fiesta II 1.1 FBD 49 Hp	https://www.automobile-catalog.com/car/1986/941225/ford_fiesta_1_1_super_cat.html;https://www.auto-data.net/en/ford-fiesta-ii-mk2-1.1-fbd-49hp-8066
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-PREFL-01	3609	1567	1360	Automobile-Catalog Ford Fiesta S 1.3 1977	https://www.automobile-catalog.com/car/1977/40610/ford_fiesta_s_1_3.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-LONG-BUMPER-FACELIFT-01	3718	1567	1359	Automobile-Catalog Ford Fiesta 1.3 Ghia 1983	https://www.automobile-catalog.com/car/1983/922730/ford_fiesta_1_3_ghia.html
EU-FORD-FIESTA-I-GFBT-HATCHBACK-3D-XR2-01	3718	1580	1371	Automobile-Catalog Ford Fiesta XR-2 1981	https://www.automobile-catalog.com/car/1981/922895/ford_fiesta_xr-2.html
EU-VW-PASSAT-B7-VARIANT-WAGON-01	4771	1820	1508	Volkswagen Newsroom Passat B7 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b7-profile-20037
EU-FORD-ESCORT-I-SEDAN-PREFL-01	3978	1572	1402	Automobile-Catalog Ford Escort 1100 1968	https://www.automobile-catalog.com/car/1968/909470/ford_escort_1100.html
EU-FORD-ESCORT-I-SEDAN-FACELIFT-01	3977	1570	1393	Automobile-Catalog Ford Escort 1100 1970	https://www.automobile-catalog.com/car/1970/908600/ford_escort_1100.html
EU-FORD-ESCORT-II-SEDAN-01	3978	1596	1398	Automobile-Catalog Ford Escort 1100 1975;Automobile-Catalog Ford Escort 1300 1975	https://www.automobile-catalog.com/car/1975/919700/ford_escort_1100.html;https://www.automobile-catalog.com/car/1975/919730/ford_escort_1300.html
EU-MERCEDES-BENZ-190-W201-SEDAN-16V-01	4430	1706	1361	Mercedes-Benz Public Archive;Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-23-16.xhtml?oid=5476;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16.xhtml?oid=5511
EU-MERCEDES-BENZ-190-W201-SEDAN-PREFL-01	4420	1678	1390	Mercedes-Benz Public Archive;Automobile-Catalog	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-D-25.xhtml?oid=5481;https://www.automobile-catalog.com/car/1986/1477385/mercedes-benz_190_e_2_3_ece-version.html
EU-MERCEDES-BENZ-190-W201-SEDAN-FACELIFT-01	4448	1690	1375	Mercedes-Benz Public Archive;Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-D.xhtml?oid=5513;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26.xhtml?oid=5502
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO1-01	4430	1720	1342	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16-Evolution.xhtml?oid=5515
EU-FORD-ESCORT-II-RS2000-SEDAN-2D-01	4150	1590	1410	Automobile-Catalog Ford Escort RS 2000 1979	https://www.automobile-catalog.com/car/1979/27785/ford_escort_rs_2000.html
EU-FORD-ESCORT-III-HATCHBACK-LATE-01	3970	1640	1384	Automobile-Catalog Ford Escort 1.1 L 1983	https://www.automobile-catalog.com/car/1983/929000/ford_escort_1_1_l.html
EU-MERCEDES-BENZ-190-W201-SEDAN-26-PREFL-01	4428	1678	1390	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-26--W-201-E-26-1986---1988.xhtml?oid=5475
EU-FORD-ESCORT-IV-HATCHBACK-01	4022	1640	1385	Automobile-Catalog Ford Escort 1.1 CL 1986	https://www.automobile-catalog.com/car/1986/941615/ford_escort_1_1_cl.html
EU-FORD-ESCORT-III-HATCHBACK-EARLY-01	3970	1640	1400	Automobile-Catalog Ford Escort 1.1 1981	https://www.automobile-catalog.com/car/1981/927935/ford_escort_1_1.html
EU-MERCEDES-BENZ-190-W201-SEDAN-EVO2-01	4543	1720	1342	Mercedes-Benz Public Archive	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-E-25-16-Evolution-II.xhtml?oid=5505
EU-MERCEDES-BENZ-HECKFLOSSE-W110-SEDAN-01	4730	1795	1495	Mercedes-Benz Public Archive 190 c;Mercedes-Benz Public Archive 200 D;Mercedes-Benz Public Archive W110 model overview	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/190-c.xhtml?oid=5129;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-D.xhtml?oid=5122;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Fintail-Mercedes-four-cylinder-models-W-110-1961---1968.xhtml?oid=5111
EU-MERCEDES-BENZ-HECKFLOSSE-W111-SEDAN-01	4875	1795	1510	Mercedes-Benz Public Archive 220 SEb;Mercedes-Benz Public Archive W111/W112 model overview	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/220-SEb.xhtml?oid=4898;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/Fintail-Mercedes-six-cylinder-models-W-111-W-112-1959---1968.xhtml?oid=4888
EU-RENAULT-MEGANE-III-GRANDTOUR-WAGON-01	4559	1804	1507	Automobile-Catalog Renault Megane Estate Grandtour 1.5 dCi 110	https://www.automobile-catalog.com/car/2009/2959940/renault_megane_estate_grandtour_1_5_dci_110_fap.html
EU-RENAULT-MEGANE-III-HATCHBACK-5D-01	4295	1808	1471	Renault official X95 owner manual	https://cdn.group.renault.com/ren/ru/manuals/Fluence_manual_260513.pdf.asset.pdf/59cdae6519.pdf
EU-MITSUBISHI-ASX-I-SUV-01	4295	1770	1615	Automobile-Catalog Mitsubishi ASX 1.8 DI-D 2WD	https://www.automobile-catalog.com/car/2010/2009720/mitsubishi_asx_1_8_di-d_2wd.html
EU-MERCEDES-BENZ-STROKE-EIGHT-SEDAN-01	4680	1770	1440	Mercedes-Benz Public Archive 230.6;Mercedes-Benz Public Archive 220/8	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/2306.xhtml?oid=5178;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/2208.xhtml?oid=5241
EU-MERCEDES-BENZ-STROKE-EIGHT-C114-COUPE-01	4680	1790	1395	Mercedes-Benz Public Archive 250 C;Mercedes-Benz Public Archive 280 CE	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/250-C.xhtml?oid=4586;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/280-CE.xhtml?oid=4582
EU-MERCEDES-BENZ-123-W123-SEDAN-01	4725	1786	1438	Mercedes-Benz Public Archive 230 E;Mercedes-Benz Public Archive 240 D	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/230-E.xhtml?oid=5098;https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/240-D.xhtml?oid=5094
EU-MERCEDES-BENZ-123-W123-SEDAN-EXPORT-BUMPER-01	4848	1786	1438	Mercedes-Benz Public Archive 300 D Turbodiesel	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/300-D-Turbodiesel.xhtml?oid=5103
EU-SAAB-9-5-II-YS3G-SEDAN-01	5008	1868	1466	Automobile-Catalog Saab 9-5 2.0 TTiD	https://www.automobile-catalog.com/car/2010/3038975/saab_9-5_2_0_ttid.html
EU-MERCEDES-BENZ-123-S123-WAGON-01	4725	1786	1470	Mercedes-Benz Public Archive 200 T	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/200-T.xhtml?oid=5383
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_301-400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.automobile-catalog.com/car/1968/909455/ford_escort_1100_low_compr_.html "https://www.automobile-catalog.com/car/1968/909455/ford_escort_1100_low_compr_.html"
[2]: https://www.automobile-catalog.com/car/1984/928670/ford_escort_1_3_l_5-speed.html "https://www.automobile-catalog.com/car/1984/928670/ford_escort_1_3_l_5-speed.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_301-400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_301-400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（494 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（130 行）
