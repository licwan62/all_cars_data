# 任务：all 第 3101-3200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0032__e7c481e3


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 3101-3200 行

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
all 第 3101-3200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Land Rover	Range rover i	3.9 CAT 4X4	Geländewagen geschlossen	Allrad	Benzin	127	173	Nov 1988	Jul 1994	2024-03-01	3211
Land Rover	Range rover i	2.4 TD 4X4	Geländewagen geschlossen	Allrad	Diesel	78	106	Apr 1986	Dec 1990	2024-03-01	3212
Land Rover	Range rover i	3.9 Vogue SEI 4X4	Geländewagen geschlossen	Allrad	Benzin	134	182	Nov 1988	Jul 1994	2024-03-01	3214
Land Rover	Range rover i	4.3 Vogue LSE 4X4	Geländewagen geschlossen	Allrad	Benzin	149	203	Sep 1992	Jul 1994	2024-03-01	3215
Land Rover	Discovery i	2.5 TDI 4X4	Geländewagen geschlossen	Allrad	Diesel	83	113	Oct 1989	Oct 1998	2024-03-01	3216
Land Rover	Discovery i	3.5 4X4	Geländewagen geschlossen	Allrad	Benzin	113	154	Jun 1989	Jun 1994	2024-03-01	3217
Rover	200 ii	218 TD	Schrägheck	Frontantrieb	Diesel	65	88	Sep 1991	Oct 1995	2024-03-01	3218
Rover	200 ii	214 Si/gsi	Schrägheck	Frontantrieb	Benzin	66	90	Oct 1989	Oct 1995	2024-03-01	3219
Rover	200 ii	214 Gsi/si	Schrägheck	Frontantrieb	Benzin	76	103	Dec 1992	Oct 1995	2024-03-01	3220
Rover	200 ii	216 GSI	Schrägheck	Frontantrieb	Benzin	82	112	Jan 1990	Dec 1995	2024-03-01	3221
Rover	200 ii	216 GTI	Schrägheck	Frontantrieb	Benzin	90	122	Jan 1990	Oct 1995	2024-03-01	3222
Rover	200 ii	220 GTI	Schrägheck	Frontantrieb	Benzin	100	136	Jan 1993	Oct 1995	2024-03-01	3223
Rover	200 ii	220 GTI	Schrägheck	Frontantrieb	Benzin	103	140	Sep 1991	Oct 1995	2024-03-01	3224
Rover	200 ii	220 Turbo	Schrägheck	Frontantrieb	Benzin	147	200	Jan 1993	Dec 1995	2024-03-01	3225
Rover	200 ii	214 1.4	Cabriolet	Frontantrieb	Benzin	66	90	Jan 1992	Nov 1999	2024-03-01	3226
Rover	200 ii	214 1.4i 16V	Cabriolet	Frontantrieb	Benzin	76	103	Jan 1993	Nov 1999	2024-03-01	3227
Rover	200 ii	216 1.6i	Cabriolet	Frontantrieb	Benzin	90	122	Jan 1992	Nov 1999	2024-03-01	3228
Rover	200	216	Coupe	Frontantrieb	Benzin	90	122	Oct 1992	Jun 1999	2024-03-01	3229
Rover	200	220 Turbo	Coupe	Frontantrieb	Benzin	147	200	Oct 1992	Jun 1999	2024-03-01	3230
Rover	400	414 Gsi/si	Stufenheck	Frontantrieb	Benzin	66	90	Apr 1990	Apr 1995	2024-03-01	3231
Rover	400	418 TD	Stufenheck	Frontantrieb	Diesel	65	88	Sep 1991	Apr 1995	2024-03-01	3232
Rover	400	414 Gsi/si CAT	Stufenheck	Frontantrieb	Benzin	76	103	Oct 1992	Apr 1995	2024-03-01	3233
Rover	400	416 GSI	Stufenheck	Frontantrieb	Benzin	82	112	Apr 1990	Apr 1995	2024-03-01	3234
Rover	400	416 GTI	Stufenheck	Frontantrieb	Benzin	90	122	Apr 1990	Apr 1995	2024-03-01	3235
Rover	400	420 Gsi/sli/gti/vite	Stufenheck	Frontantrieb	Benzin	100	136	Jan 1993	Apr 1995	2024-03-01	3236
Rover	400	420 Gti/gsi/vitesse	Stufenheck	Frontantrieb	Benzin	103	140	Feb 1992	Apr 1995	2024-03-01	3237
Rover	400	420 Turbo	Stufenheck	Frontantrieb	Benzin	147	200	Jan 1993	Apr 1995	2024-03-01	3238
Rover	Montego	2.0 Turbo-d	Kombi	Frontantrieb	Diesel	60	82	Jan 1993	Dec 1993	2024-03-01	3239
Rover	100	114 S/l/gta	Schrägheck	Frontantrieb	Benzin	55	75	Mar 1990	Dec 1998	2024-03-01	3240
Rover	100	111 C/l/s	Schrägheck	Frontantrieb	Benzin	44	60	Mar 1990	Dec 1998	2024-03-01	3241
Rover	100	114 Gti/gt 16V CAT	Schrägheck	Frontantrieb	Benzin	66	90	Mar 1990	Dec 1998	2024-03-01	3242
Triumph	Tr 6 i	2.5	Cabriolet	Heckantrieb	Benzin	90	122	Jan 1972	Dec 1976	2024-03-01	3243
Triumph	Spitfire mk iv	1.3	Cabriolet	Heckantrieb	Benzin	55	76	Jan 1971	Dec 1972	2024-03-01	3244
Triumph	Spitfire 1500	1500	Cabriolet	Heckantrieb	Benzin	51	69	Jan 1975	Jan 1980	2024-03-01	3245
Triumph	Tr 7 i	2	Coupe	Heckantrieb	Benzin	78	106	Jan 1975	Dec 1981	2024-03-01	3246
Fiat	Qubo	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	70	95	Jul 2010	-	2024-03-01	3247
Triumph	Tr 7 ii	2	Cabriolet	Heckantrieb	Benzin	78	106	May 1979	Dec 1981	2024-03-01	3248
Triumph	Acclaim	1.3	Stufenheck	Frontantrieb	Benzin	51	69	Jan 1982	Dec 1985	2024-03-01	3249
Mercedes-benz	Cls	CLS 350	Coupe	Heckantrieb	Benzin	225	306	Jan 2011	Aug 2014	2024-03-01	3251
Lancia	Musa	1.6 D Multijet	Großraumlimousine	Frontantrieb	Diesel	85	116	Jul 2008	Sep 2012	2024-03-01	3252
Mercedes-benz	Cls	CLS 250 CDI / Bluetec / D	Coupe	Heckantrieb	Diesel	150	204	Apr 2011	Dec 2017	2024-03-01	3253
Mitsubishi	Colt i	1.2 GL	Schrägheck	Frontantrieb	Benzin	40	55	Dec 1978	Jan 1984	2024-03-01	3254
Mitsubishi	Colt i	1.4 Glx, GT	Schrägheck	Frontantrieb	Benzin	51	70	May 1979	Jan 1984	2024-03-01	3255
Mitsubishi	Colt i	1.4 Turbo	Schrägheck	Frontantrieb	Benzin	77	105	Sep 1981	Jan 1984	2024-03-01	3256
Mercedes-benz	Cls	CLS 350 CDI / D	Coupe	Heckantrieb	Diesel	195	265	Jan 2011	Aug 2014	2024-03-01	3257
Mitsubishi	Colt ii	1.2 EL, GL	Schrägheck	Frontantrieb	Benzin	40	55	Feb 1984	Sep 1986	2024-03-01	3258
Mitsubishi	Colt ii	1.2 EL, GL	Schrägheck	Frontantrieb	Benzin	44	60	Sep 1986	Apr 1988	2024-03-01	3259
Mitsubishi	Colt ii	1.5 GLX	Schrägheck	Frontantrieb	Benzin	51	70	Sep 1985	Apr 1988	2024-03-01	3260
Mitsubishi	Colt ii	1.5 GLX	Schrägheck	Frontantrieb	Benzin	55	75	Sep 1984	Apr 1988	2024-03-01	3261
Mitsubishi	Colt ii	1.6 Turbo ECI	Schrägheck	Frontantrieb	Benzin	92	125	Feb 1984	Apr 1988	2024-03-01	3262
Mitsubishi	Colt ii	1.8 GL Diesel	Schrägheck	Frontantrieb	Diesel	43	58	Feb 1984	Sep 1986	2024-03-01	3263
Mitsubishi	Colt ii	1.8 GL Diesel	Schrägheck	Frontantrieb	Diesel	44	60	Sep 1986	Apr 1988	2024-03-01	3264
Mitsubishi	Colt iii	1.3	Schrägheck	Frontantrieb	Benzin	51	70	Apr 1988	May 1992	2024-03-01	3265
Renault	Kangoo	1.5 DCI	Kasten/Großraumlimousine	Frontantrieb	Diesel	45	61	Oct 2005	-	2024-03-01	3266
Mitsubishi	Colt iii	1.8 Diesel GLX	Schrägheck	Frontantrieb	Diesel	44	60	Apr 1988	May 1992	2024-03-01	3267
Mitsubishi	Colt iii	1.3 GL	Schrägheck	Frontantrieb	Benzin	44	60	Apr 1988	Dec 1990	2024-03-01	3268
Mitsubishi	Colt iii	1.3 12V	Schrägheck	Frontantrieb	Benzin	55	75	Apr 1988	May 1992	2024-03-01	3269
Mitsubishi	Colt iii	1.5 Glxi	Schrägheck	Frontantrieb	Benzin	62	84	Apr 1988	May 1992	2024-03-01	3270
Mitsubishi	Colt iii	1.5 CAT	Schrägheck	Frontantrieb	Benzin	66	90	Jul 1990	May 1992	2024-03-01	3271
Mitsubishi	Colt iii	1.6 GTI 16V	Schrägheck	Frontantrieb	Benzin	91	124	Apr 1988	May 1990	2024-03-01	3272
Mitsubishi	Colt iii	1.8 GTI 16V CAT	Schrägheck	Frontantrieb	Benzin	100	136	Jun 1990	May 1992	2024-03-01	3273
Mitsubishi	Lancer i	1.2	Stufenheck	Heckantrieb	Benzin	40	55	Jan 1978	Sep 1979	2024-03-01	3274
Mitsubishi	Lancer i	1.4	Stufenheck	Heckantrieb	Benzin	50	68	Jan 1978	Sep 1979	2024-03-01	3275
Mitsubishi	Lancer i	1.6	Stufenheck	Heckantrieb	Benzin	60	82	Jan 1978	Sep 1979	2024-03-01	3276
Mitsubishi	Lancer i station wagon	1.4	Kombi	Heckantrieb	Benzin	50	68	Jan 1978	Sep 1979	2024-03-01	3277
Mitsubishi	Lancer ii	1.2	Stufenheck	Heckantrieb	Benzin	40	54	Jan 1980	Dec 1981	2024-03-01	3278
Mitsubishi	Lancer f	1.2 GLX	Stufenheck	Frontantrieb	Benzin	40	55	Mar 1983	Jan 1984	2024-03-01	3279
Mitsubishi	Lancer ii	1.4 GLX	Stufenheck	Heckantrieb	Benzin	50	68	Sep 1979	Feb 1983	2024-03-01	3280
Mitsubishi	Lancer f	1.4 GLX	Stufenheck	Frontantrieb	Benzin	51	70	Mar 1983	Jan 1984	2024-03-01	3281
Mitsubishi	Lancer f	1.4 Turbo	Stufenheck	Frontantrieb	Benzin	77	105	Mar 1983	Jan 1984	2024-03-01	3282
Mitsubishi	Lancer ii	1.6	Stufenheck	Heckantrieb	Benzin	60	82	Sep 1979	Feb 1983	2024-03-01	3283
Mitsubishi	Lancer ii	1.6	Stufenheck	Heckantrieb	Benzin	62	84	Jan 1981	Feb 1983	2024-03-01	3284
Mitsubishi	Lancer ii	2.0 Turbo ECI	Stufenheck	Heckantrieb	Benzin	125	170	Mar 1981	Feb 1983	2024-03-01	3285
Mitsubishi	Lancer iii	1.2 GL	Stufenheck	Frontantrieb	Benzin	40	55	Jan 1984	Oct 1986	2024-03-01	3286
Mitsubishi	Lancer iii	1.2	Stufenheck	Frontantrieb	Benzin	44	60	Aug 1986	Apr 1988	2024-03-01	3287
Mitsubishi	Lancer iii	1.5 GLX	Stufenheck	Frontantrieb	Benzin	51	70	Jun 1985	Apr 1988	2024-03-01	3288
Mitsubishi	Lancer iii	1.5 GLX	Stufenheck	Frontantrieb	Benzin	55	75	Nov 1983	Apr 1988	2024-03-01	3289
Mitsubishi	Lancer iii	1.8 Diesel	Stufenheck	Frontantrieb	Diesel	43	58	Jan 1984	Sep 1986	2024-03-01	3290
Mitsubishi	Lancer iii	1.8 Diesel	Stufenheck	Frontantrieb	Diesel	44	60	Sep 1986	Apr 1988	2024-03-01	3291
Mitsubishi	Lancer iii station wagon	1.5	Kombi	Frontantrieb	Benzin	51	70	Sep 1985	Aug 1989	2024-03-01	3292
Mitsubishi	Lancer iii station wagon	1.5	Kombi	Frontantrieb	Benzin	55	75	Sep 1985	Dec 1987	2024-03-01	3293
Mitsubishi	Lancer iii station wagon	1.8 4WD	Kombi	Allrad	Benzin	61	83	Jan 1987	Aug 1989	2024-03-01	3294
Mitsubishi	Lancer iii station wagon	1.8 4WD	Kombi	Allrad	Benzin	66	90	Jan 1987	Dec 1987	2024-03-01	3295
Mitsubishi	Lancer iii station wagon	1.8 D	Kombi	Frontantrieb	Diesel	43	58	Sep 1985	Sep 1986	2024-03-01	3296
Mitsubishi	Lancer iii station wagon	1.8 D	Kombi	Frontantrieb	Diesel	44	60	Aug 1986	Jun 1992	2024-03-01	3297
Mitsubishi	Lancer iii station wagon	1.5	Kombi	Frontantrieb	Benzin	61	83	Sep 1988	Dec 1990	2024-03-01	3298
Mitsubishi	Lancer iii station wagon	1.5 12V	Kombi	Frontantrieb	Benzin	66	90	Sep 1990	Dec 1991	2024-03-01	3299
Mitsubishi	Lancer iii station wagon	1.8 4WD	Kombi	Allrad	Benzin	63	86	Mar 1989	Dec 1990	2024-03-01	3300
Mitsubishi	Lancer iii station wagon	1.8 4WD	Kombi	Allrad	Benzin	69	94	Aug 1990	Jun 1992	2024-03-01	3301
Mitsubishi	Lancer iv	1.3	Stufenheck	Frontantrieb	Benzin	51	70	Aug 1988	May 1992	2024-03-01	3302
Mitsubishi	Lancer iv	1.8 GLX Diesel	Stufenheck	Frontantrieb	Diesel	44	60	Apr 1988	May 1992	2024-03-01	3303
Mitsubishi	Lancer iv	1.3	Stufenheck	Frontantrieb	Benzin	44	60	Apr 1988	May 1992	2024-03-01	3304
Mitsubishi	Lancer iv	1.3 12V	Stufenheck	Frontantrieb	Benzin	55	75	Jul 1990	Jun 1992	2024-03-01	3305
Mitsubishi	Lancer iv	1.5	Stufenheck	Frontantrieb	Benzin	62	84	Apr 1988	May 1992	2024-03-01	3306
Mitsubishi	Lancer iv	1.5 12V	Stufenheck	Frontantrieb	Benzin	66	90	Jun 1990	May 1992	2024-03-01	3307
Mitsubishi	Lancer iv	1.8 D	Schrägheck	Frontantrieb	Diesel	44	60	Apr 1988	May 1992	2024-03-01	3308
Mitsubishi	Lancer iv	1.3 12V	Schrägheck	Frontantrieb	Benzin	55	75	Jun 1992	May 1994	2024-03-01	3309
Mitsubishi	Lancer iv	1.5 12V	Schrägheck	Frontantrieb	Benzin	66	90	May 1989	May 1992	2024-03-01	3311
Mitsubishi	Lancer iv	1.6 16V	Schrägheck	Frontantrieb	Benzin	83	113	Jun 1992	May 1994	2024-03-01	3312
Mitsubishi	Lancer iv	1.8 4WD	Schrägheck	Allrad	Benzin	71	97	Sep 1989	Jun 1992	2024-03-01	3313


--- Round 1 / 首次发送 ---
## 更新点

* 已闭合 Range Rover Classic 的 Vogue SEI 标准轴距与 Vogue LSE 长轴距尺寸组；Discovery I 根据三门、五门车([汽车数据][1])

* 已批量完成 Rover 200 II Hatchback、Cabriolet、Coupe，Rover 400 I Sedan，以及 Rover 100 三门、五门分支的映射。([汽车数据][2])s-Benz CLS C218 已区分 2014 年改款前后外廓；Fiat Qubo 已建立首个稳定 MPV 尺寸组。([汽车数据][3])度

* READY 输入 Ktype：32/100

* PENDING 输入 Ktype：68/100

* READY 映射行：38

* 已确认尺寸组：13

* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3214	3214	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-01	HIGH	Vogue SEI五门标准轴距外廓。	READY
3215	3215	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-LWB-5D-01	HIGH	Vogue LSE五门长轴距外廓。	READY
3216_3dr	3216	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3216_5dr	3216	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3217_3dr	3217	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3217_5dr	3217	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3218	3218	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3219	3219	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3220	3220	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3221	3221	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3222	3222	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3223	3223	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3224	3224	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3225	3225	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3226	3226	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3227	3227	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3228	3228	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3229	3229	Coupe	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
3230	3230	Coupe	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
3231	3231	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3232	3232	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3233	3233	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3234	3234	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3235	3235	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3236	3236	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3237	3237	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3238	3238	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3240_3dr	3240	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3240_5dr	3240	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3241_3dr	3241	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3241_5dr	3241	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3242_3dr	3242	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3242_5dr	3242	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3247	3247	MPV	Qubo I		5	EU-FIAT-QUBO-I-MPV-5D-01	HIGH		READY
3251	3251	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	改款前四门轿跑外廓。	READY
3253_prefl	3253	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	该Ktype跨改款，改款前外廓分支。	READY
3253_facelift	3253	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	该Ktype跨改款，改款后外廓分支。	READY
3257	3257	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	改款前四门轿跑外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-01	4450	1818	1790	Automobile-Catalog 1990 Range Rover Vogue SEi catalyst	https://www.automobile-catalog.com/car/1990/1398020/range_rover_vouge_sei_cat.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-LWB-5D-01	4653	1820	1830	Automobile-Catalog 1993 Range Rover Vogue 4.2 LSEi	https://www.automobile-catalog.com/car/1993/1398065/range_rover_vouge_4_2_lsei.html
EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	4520	1795	1915	Auto-Data Land Rover Discovery I 2.5 TDi (3 dr)	https://www.auto-data.net/en/land-rover-discovery-i-2.5-tdi-3-dr-113hp-5228
EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	4520	1795	1960	Auto-Data Land Rover Discovery I 2.5 TDi (5 dr)	https://www.auto-data.net/en/land-rover-discovery-i-2.5-tdi-5-dr-113hp-5229
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390	Auto-Data Rover 200 (XW) generation	https://www.auto-data.net/en/rover-200-xw-generation-2451
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390	Auto-Data Rover 200 model (Cabrio XW)	https://www.auto-data.net/en/rover-200-model-1222
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370	Auto-Data Rover 200 Coupe (XW) 220 Turbo	https://www.auto-data.net/en/rover-200-coupe-xw-220-turbo-200hp-11565
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400	Auto-Data Rover 400 model (XW)	https://www.auto-data.net/en/rover-400-model-1228
EU-ROVER-100-XP-HATCHBACK-3D-01	3521	1550	1377	Auto-Data Rover 100 (METRO) (XP); Automobile-Catalog 1990 Rover 111 S	https://www.auto-data.net/en/rover-100-metro-xp-generation-2440;https://www.automobile-catalog.com/car/1990/3012515/rover_111_s_metro_1_1_s.html
EU-ROVER-100-XP-HATCHBACK-5D-01	3521	1550	1377	Auto-Data Rover 100 (METRO) (XP); Automobile-Catalog 1990 Rover 111 S	https://www.auto-data.net/en/rover-100-metro-xp-generation-2440;https://www.automobile-catalog.com/car/1990/3012515/rover_111_s_metro_1_1_s.html
EU-FIAT-QUBO-I-MPV-5D-01	3959	1716	1735	Auto-Data Fiat Qubo generation	https://www.auto-data.net/en/fiat-qubo-generation-3984
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	4940	1881	1416	Auto-Data Mercedes-Benz CLS C218 CLS 250 CDI	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-cls-250-cdi-204hp-7g-tronic-plus-18694
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	4937	1881	1418	Auto-Data Mercedes-Benz CLS C218 facelift CLS 250 BlueTEC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-cls-250-bluetec-204hp-9g-tronic-20854
```

## 下一步优先处理

1. 按 Colt I、Colt II、Colt III 聚类，批量处理 Ktype 3254–3273。
2. 按 Lancer I、II、F、III、III Station Wagon、IV 聚类，优先覆盖 Ktype 3274–3313。
3. 补齐 Range Rover I 通用 3.9 CAT、2.4 TD 的三门/五门边界。
4. 随后处理 Triumph、Lancia Musa、Renault Kangoo、Rover Montego 和 Mitsubishi Lancer IV Hatchback 的剩余独立外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/land-rover-discovery-i-2.5-tdi-5-dr-113hp-5229 "Land Rover Discovery I 2.5 TDi (5 dr) (113 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/rover-200-xw-generation-2451?utm_source=chatgpt.com "Rover 200 (XW) | Technical Specs, Fuel consumption ..."
[3]: https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-cls-250-cdi-204hp-7g-tronic-plus-18694?utm_source=chatgpt.com "Mercedes-Benz CLS coupe (C218) CLS 250 CDI (204 Hp) ..."


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已首次闭合 Colt III 三门掀背、Lancer III 四门轿车、Lancer III 五门旅行车、Lancer IV 四门轿车及五门掀背共 5 个尺寸组，新增 35 个 READY Ktype 映射。Colt III 为三门车身；Lancer III Sedan、Wagon 分别为四门和五门；Lancer IV Sedan、Hatchback 分别为四门和五门。([汽车数据][1])
* 本轮各尺寸组的长宽高均一次性闭合；后续相同外廓 Ktype 直接复用，不再重复抓取。([汽车目录][2])

## 当前批次进度

* READY 输入 Ktype：67/100
* PENDING 输入 Ktype：33/100
* READY 映射行：73
* 已确认尺寸组：18
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3265	3265	Hatchback	Colt III (C50)	C51A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3267	3267	Hatchback	Colt III (C50)	C54A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3268	3268	Hatchback	Colt III (C50)		3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3269	3269	Hatchback	Colt III (C50)	C51A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3270	3270	Hatchback	Colt III (C50)	C52A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3271	3271	Hatchback	Colt III (C50)	C52A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3272	3272	Hatchback	Colt III (C50)	C53A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3273	3273	Hatchback	Colt III (C50)	C58A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3286	3286	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3287	3287	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3288	3288	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3289	3289	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3290	3290	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3291	3291	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3292	3292	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3293	3293	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3294	3294	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3295	3295	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3296	3296	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3297	3297	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3298	3298	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3299	3299	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3300	3300	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3301	3301	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3302	3302	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3303	3303	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3304	3304	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3305	3305	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3306	3306	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3307	3307	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3308	3308	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3309	3309	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3311	3311	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3312	3312	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3313	3313	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	3950	1670	1380	Auto-Data Mitsubishi Colt III C50 1.3 12V; Automobile-Catalog 1988 Mitsubishi Colt 1300 GL	https://www.auto-data.net/en/mitsubishi-colt-iii-c50-1.3-12v-c51a-75hp-15767;https://www.automobile-catalog.com/car/1988/1933790/mitsubishi_colt_1300_gl.html
EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	4125	1635	1360	Auto-Data Mitsubishi Lancer III 1.5	https://www.auto-data.net/en/mitsubishi-lancer-iii-1.5-75hp-15701
EU-MITSUBISHI-LANCER-III-WAGON-5D-01	4115	1635	1415	Auto-Data Mitsubishi Lancer III Wagon 1.8 D	https://www.auto-data.net/en/mitsubishi-lancer-iii-wagon-1.8-d-60hp-15697
EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	4235	1670	1405	Auto-Data Mitsubishi Lancer IV 1.5 12V	https://www.auto-data.net/en/mitsubishi-lancer-iv-1.5-12v-90hp-15671
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	4235	1670	1405	Auto-Data Mitsubishi Lancer IV Hatchback	https://www.auto-data.net/en/mitsubishi-lancer-iv-hatchback-generation-3452
```

## 下一步优先处理

1. 闭合 Lancer I Sedan/Wagon、Lancer II Sedan 和 Lancer F Sedan，对应 Ktype 3274–3285。
2. 核对 Colt I、Colt II 的三门/五门边界及差异尺寸，对应 Ktype 3254–3264。
3. 处理 Range Rover I 剩余标准轴距三门/五门分支。
4. 最后闭合 Triumph、Rover Montego、Lancia Musa、Renault Kangoo 等独立外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-colt-iii-c50-1.3-12v-c51a-75hp-15767 "Mitsubishi Colt III (C50) 1.3 12V (C51A) (75 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1988/1933790/mitsubishi_colt_1300_gl.html?utm_source=chatgpt.com "1988 Mitsubishi Colt 1300 GL Specs Review (51 kW / 69 ..."


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 首次闭合 Lancer II 四门后驱轿车与 Lancer F 四门前驱轿车两个尺寸组。
* 新增 8 个 READY Ktype 映射；同代发动机、功率差异均复用对应尺寸组。Lancer II 外廓为 4225×1620×1385 mm；Lancer F 欧洲版外廓为 4185×1590×1345 mm，宽度均为不含后视镜口径。([汽车数据][1])

## 当前批次进度

* READY 输入 Ktype：75/100
* PENDING 输入 Ktype：25/100
* READY 映射行：81
* 已确认尺寸组：20
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3278	3278	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3279	3279	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3280	3280	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3281	3281	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3282	3282	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3283	3283	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3284	3284	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3285	3285	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	4225	1620	1385	Auto-Data Mitsubishi Lancer II generation	https://www.auto-data.net/en/mitsubishi-lancer-ii-generation-3456
EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	4185	1590	1345	Automobile-Catalog 1983 Mitsubishi Lancer F 1400 GLX	https://www.automobile-catalog.com/car/1983/1917230/mitsubishi_lancer_f_1400_glx.html
```

## 下一步优先处理

1. Colt I、Colt II 的三门与五门分支，对应 Ktype 3254–3264。
2. Lancer I Sedan 与 Lancer I Station Wagon，对应 Ktype 3274–3277。
3. Range Rover I 剩余标准轴距门数分支，对应 Ktype 3211–3212。
4. 最后闭合 Rover Montego、Triumph、Lancia Musa 与 Renault Kangoo 独立外廓。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mitsubishi-lancer-ii-generation-3456 "Mitsubishi Lancer II | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 已闭合 Mitsubishi Colt I 的三门/五门、改款前/改款后及 Turbo 三门外廓，共首次创建 5 个尺寸组。标准车型在 1982 年中期改款后，三门由 3790×1585×1345 mm 变为 3805×1590×1345 mm，五门由 3895×1585×1345 mm 变为 3930×1590×1345 mm；Turbo 三门为独立的 3810×1585×1345 mm 外廓。([汽车目录][1])
* 已闭合 Mitsubishi Lancer I 欧洲版二门/四门 Sedan 及五门 Wagon 外廓，共首次创建 3 个尺寸组；Sedan 页面明确覆盖二门和四门，Wagon 为独立五门车身。([汽车目录][2])
* 本轮新增 7 个 READY Ktype、16 行映射及 8 个尺寸组。

## 当前批次进度

* READY 输入 Ktype：82/100
* PENDING 输入 Ktype：18/100
* READY 映射行：97
* 已确认尺寸组：28
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3254_3dr_prefl	3254	Hatchback	Colt I (A150)	A151A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	HIGH	该Ktype跨门数与改款，三门改款前分支。	READY
3254_3dr_facelift	3254	Hatchback	Colt I (A150)	A151A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	HIGH	该Ktype跨门数与改款，三门改款后分支。	READY
3254_5dr_prefl	3254	Hatchback	Colt I (A150)	A151A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨门数与改款，五门改款前分支。	READY
3254_5dr_facelift	3254	Hatchback	Colt I (A150)	A151A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨门数与改款，五门改款后分支。	READY
3255_3dr_prefl	3255	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	HIGH	该Ktype跨门数与改款，三门改款前分支。	READY
3255_3dr_facelift	3255	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	HIGH	该Ktype跨门数与改款，三门改款后分支。	READY
3255_5dr_prefl	3255	Hatchback	Colt I (A150)	A152A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨门数与改款，五门改款前分支。	READY
3255_5dr_facelift	3255	Hatchback	Colt I (A150)	A152A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨门数与改款，五门改款后分支。	READY
3256	3256	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-TURBO-01	HIGH		READY
3274_2dr	3274	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3274_4dr	3274	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3275_2dr	3275	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3275_4dr	3275	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3276_2dr	3276	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3276_4dr	3276	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3277	3277	Wagon	Lancer I Station Wagon (A70)		5	EU-MITSUBISHI-LANCER-I-A70-WAGON-5D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	3790	1585	1345	Automobile-Catalog 1979 Mitsubishi Colt 1400 GLX 3-Door	https://www.automobile-catalog.com/car/1979/35765/mitsubishi_colt_1400_glx.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	3805	1590	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 GLX 3-Door	https://www.automobile-catalog.com/car/1983/1913300/mitsubishi_colt_1400_glx_3-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	3895	1585	1345	Automobile-Catalog 1979 Mitsubishi Colt 1400 GLX 5-Door	https://www.automobile-catalog.com/car/1979/36620/mitsubishi_colt_1400_glx_5-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	3930	1590	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 GLX 5-Door	https://www.automobile-catalog.com/car/1983/1913315/mitsubishi_colt_1400_glx_5-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-TURBO-01	3810	1585	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 Turbo	https://www.automobile-catalog.com/car/1983/55625/mitsubishi_colt_1400_turbo.html
EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	3995	1535	1375	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL	https://www.automobile-catalog.com/car/1978/35795/mitsubishi_lancer_1400_gl.html
EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	3995	1535	1375	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL	https://www.automobile-catalog.com/car/1978/35795/mitsubishi_lancer_1400_gl.html
EU-MITSUBISHI-LANCER-I-A70-WAGON-5D-01	3995	1535	1390	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL Estate	https://www.automobile-catalog.com/car/1978/1907045/mitsubishi_lancer_1400_gl_estate.html
```

## 下一步优先处理

1. 闭合 Colt II Ktype 3258–3264，优先区分改款前后、三门/五门及 Turbo 外廓。
2. 批量处理 Triumph TR6、Spitfire、TR7 Coupe/Convertible 与 Acclaim，对应 Ktype 3243–3249。
3. 闭合 Range Rover I 剩余 Ktype 3211、3212 的门数和标准轴距分支。
4. 最后处理 Rover Montego、Lancia Musa 与 Renault Kangoo 混合车身项。

推进信号：CONTINUE

[1]: https://www.automobile-catalog.com/car/1983/1913315/mitsubishi_colt_1400_glx_5-door.html?utm_source=chatgpt.com "1983 Mitsubishi Colt 1400 GLX 5-Door Specs Review (51 kW / 69 PS / 68 hp) (for Europe )"
[2]: https://www.automobile-catalog.com/car/1978/1907045/mitsubishi_lancer_1400_gl_estate.html?utm_source=chatgpt.com "1978 Mitsubishi Lancer 1400 GL Estate Specs Review (50 kW / 68 PS / 67 hp) (for Europe )"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_3101-3200_ktype_dimension_mapping_final.tsv
- all_3101-3200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 已补齐剩余 18 个 Ktype，完成 Range Rover I 柴油外廓、Rover Montego Estate、Triumph 系列、Lancia Musa、Colt II 及 Kangoo 厢式/乘用分支。TR7 Coupé 与 Cabriolet 已按独立车身建组；Colt II Turbo 与普通三门、五门外廓分别闭合。([ADAC][1])
* 已完成轻量机械检查：固定表头、唯一主键、外键闭合、尺寸及来源非空，未发现孤立尺寸组。

## 当前批次进度

* READY 输入 Ktype：100/100
* PENDING 输入 Ktype：0/100
* 最终映射行：120
* 最终尺寸组：43
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
3211	3211	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-01	HIGH		READY
3212	3212	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-DIESEL-01	HIGH	柴油五门标准轴距外廓。	READY
3214	3214	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-01	HIGH	Vogue SEI五门标准轴距外廓。	READY
3215	3215	SUV	Range Rover I (Classic)		5	EU-LAND-ROVER-RANGE-ROVER-I-SUV-LWB-5D-01	HIGH	Vogue LSE五门长轴距外廓。	READY
3216_3dr	3216	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3216_5dr	3216	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3217_3dr	3217	SUV	Discovery I		3	EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3217_5dr	3217	SUV	Discovery I		5	EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3218	3218	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3219	3219	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3220	3220	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3221	3221	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3222	3222	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3223	3223	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3224	3224	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3225	3225	Hatchback	Rover 200 II (R8)	XW	5	EU-ROVER-200-II-XW-HATCHBACK-5D-01	HIGH		READY
3226	3226	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3227	3227	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3228	3228	Convertible	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	HIGH		READY
3229	3229	Coupe	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
3230	3230	Coupe	Rover 200 II (R8)	XW	2	EU-ROVER-200-II-XW-COUPE-2D-01	HIGH		READY
3231	3231	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3232	3232	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3233	3233	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3234	3234	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3235	3235	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3236	3236	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3237	3237	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3238	3238	Sedan	Rover 400 I (R8)	XW	4	EU-ROVER-400-I-XW-SEDAN-4D-01	HIGH		READY
3239	3239	Wagon	Montego Estate		5	EU-ROVER-MONTEGO-ESTATE-WAGON-5D-01	HIGH		READY
3240_3dr	3240	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3240_5dr	3240	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3241_3dr	3241	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3241_5dr	3241	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3242_3dr	3242	Hatchback	Rover 100 (Metro)	XP	3	EU-ROVER-100-XP-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门外廓分支。	READY
3242_5dr	3242	Hatchback	Rover 100 (Metro)	XP	5	EU-ROVER-100-XP-HATCHBACK-5D-01	HIGH	该Ktype覆盖五门外廓分支。	READY
3243	3243	Convertible	TR6		2	EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	HIGH		READY
3244	3244	Convertible	Spitfire Mk IV		2	EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	HIGH		READY
3245	3245	Convertible	Spitfire 1500		2	EU-TRIUMPH-SPITFIRE-1500-CONVERTIBLE-2D-01	HIGH		READY
3246	3246	Coupe	TR7		2	EU-TRIUMPH-TR7-COUPE-2D-01	HIGH	固定车顶双门外廓。	READY
3247	3247	MPV	Qubo I		5	EU-FIAT-QUBO-I-MPV-5D-01	HIGH		READY
3248	3248	Convertible	TR7		2	EU-TRIUMPH-TR7-CONVERTIBLE-2D-01	HIGH	敞篷双门外廓。	READY
3249	3249	Sedan	Acclaim	XD	4	EU-TRIUMPH-ACCLAIM-XD-SEDAN-4D-01	HIGH		READY
3251	3251	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	改款前四门轿跑外廓。	READY
3252	3252	MPV	Musa I (facelift 2007)		5	EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	HIGH		READY
3253_prefl	3253	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	该Ktype跨改款，改款前外廓分支。	READY
3253_facelift	3253	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	HIGH	该Ktype跨改款，改款后外廓分支。	READY
3254_3dr_prefl	3254	Hatchback	Colt I (A150)	A151A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	HIGH	该Ktype跨门数与改款，三门改款前分支。	READY
3254_3dr_facelift	3254	Hatchback	Colt I (A150)	A151A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	HIGH	该Ktype跨门数与改款，三门改款后分支。	READY
3254_5dr_prefl	3254	Hatchback	Colt I (A150)	A151A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨门数与改款，五门改款前分支。	READY
3254_5dr_facelift	3254	Hatchback	Colt I (A150)	A151A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨门数与改款，五门改款后分支。	READY
3255_3dr_prefl	3255	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	HIGH	该Ktype跨门数与改款，三门改款前分支。	READY
3255_3dr_facelift	3255	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	HIGH	该Ktype跨门数与改款，三门改款后分支。	READY
3255_5dr_prefl	3255	Hatchback	Colt I (A150)	A152A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	HIGH	该Ktype跨门数与改款，五门改款前分支。	READY
3255_5dr_facelift	3255	Hatchback	Colt I (A150)	A152A	5	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	HIGH	该Ktype跨门数与改款，五门改款后分支。	READY
3256	3256	Hatchback	Colt I (A150)	A152A	3	EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-TURBO-01	HIGH		READY
3257	3257	Coupe	CLS II (C218)	C218	4	EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	HIGH	改款前四门轿跑外廓。	READY
3258_3dr	3258	Hatchback	Colt II (C10)	C15A	3	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-1P2-01	HIGH	该Ktype覆盖三门与五门，三门分支。	READY
3258_5dr	3258	Hatchback	Colt II (C10)	C15A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门，五门分支。	READY
3259_3dr	3259	Hatchback	Colt II (C10)	C15A	3	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-1P2-01	HIGH	该Ktype覆盖三门与五门，三门分支。	READY
3259_5dr	3259	Hatchback	Colt II (C10)	C15A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门，五门分支。	READY
3260_3dr	3260	Hatchback	Colt II (C10)	C12A	3	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门，三门分支。	READY
3260_5dr	3260	Hatchback	Colt II (C10)	C12A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门，五门分支。	READY
3261_3dr	3261	Hatchback	Colt II (C10)	C12A	3	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-01	HIGH	该Ktype覆盖三门与五门，三门分支。	READY
3261_5dr	3261	Hatchback	Colt II (C10)	C12A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	该Ktype覆盖三门与五门，五门分支。	READY
3262	3262	Hatchback	Colt II (C10)	C13A	3	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-TURBO-01	HIGH	Turbo三门外廓。	READY
3263	3263	Hatchback	Colt II (C10)	C14A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	柴油五门外廓。	READY
3264	3264	Hatchback	Colt II (C10)	C14A	5	EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	HIGH	柴油五门外廓。	READY
3265	3265	Hatchback	Colt III (C50)	C51A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3266_van	3266	Van	Kangoo I Express (facelift 2003)	FC		EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	HIGH	混合车身输入，厢式货车分支。	READY
3266_mpv	3266	MPV	Kangoo I (facelift 2003)	KC	5	EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	HIGH	混合车身输入，乘用MPV分支。	READY
3267	3267	Hatchback	Colt III (C50)	C54A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3268	3268	Hatchback	Colt III (C50)		3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3269	3269	Hatchback	Colt III (C50)	C51A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3270	3270	Hatchback	Colt III (C50)	C52A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3271	3271	Hatchback	Colt III (C50)	C52A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3272	3272	Hatchback	Colt III (C50)	C53A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3273	3273	Hatchback	Colt III (C50)	C58A	3	EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	HIGH		READY
3274_2dr	3274	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3274_4dr	3274	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3275_2dr	3275	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3275_4dr	3275	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3276_2dr	3276	Sedan	Lancer I (A70)		2	EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	HIGH	该Ktype覆盖二门与四门轿车，二门分支。	READY
3276_4dr	3276	Sedan	Lancer I (A70)		4	EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	HIGH	该Ktype覆盖二门与四门轿车，四门分支。	READY
3277	3277	Wagon	Lancer I Station Wagon (A70)		5	EU-MITSUBISHI-LANCER-I-A70-WAGON-5D-01	HIGH		READY
3278	3278	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3279	3279	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3280	3280	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3281	3281	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3282	3282	Sedan	Lancer F		4	EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	HIGH		READY
3283	3283	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3284	3284	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3285	3285	Sedan	Lancer II		4	EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	HIGH		READY
3286	3286	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3287	3287	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3288	3288	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3289	3289	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3290	3290	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3291	3291	Sedan	Lancer III		4	EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	HIGH		READY
3292	3292	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3293	3293	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3294	3294	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3295	3295	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3296	3296	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3297	3297	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3298	3298	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3299	3299	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3300	3300	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3301	3301	Wagon	Lancer III Wagon		5	EU-MITSUBISHI-LANCER-III-WAGON-5D-01	HIGH		READY
3302	3302	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3303	3303	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3304	3304	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3305	3305	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3306	3306	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3307	3307	Sedan	Lancer IV		4	EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	HIGH		READY
3308	3308	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3309	3309	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3311	3311	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3312	3312	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
3313	3313	Hatchback	Lancer IV Hatchback		5	EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_3101-3200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-01	4450	1818	1790	Automobile-Catalog 1990 Range Rover Vogue SEi catalyst	https://www.automobile-catalog.com/car/1990/1398020/range_rover_vouge_sei_cat.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-SWB-5D-DIESEL-01	4450	1818	1800	Automobile-Catalog 1988 Range Rover Turbo D	https://www.automobile-catalog.com/car/1988/1397735/range_rover_turbo_d.html
EU-LAND-ROVER-RANGE-ROVER-I-SUV-LWB-5D-01	4653	1820	1830	Automobile-Catalog 1993 Range Rover Vogue 4.2 LSEi	https://www.automobile-catalog.com/car/1993/1398065/range_rover_vouge_4_2_lsei.html
EU-LAND-ROVER-DISCOVERY-I-SUV-3D-01	4520	1795	1915	Auto-Data Land Rover Discovery I 2.5 TDi (3 dr)	https://www.auto-data.net/en/land-rover-discovery-i-2.5-tdi-3-dr-113hp-5228
EU-LAND-ROVER-DISCOVERY-I-SUV-5D-01	4520	1795	1960	Auto-Data Land Rover Discovery I 2.5 TDi (5 dr)	https://www.auto-data.net/en/land-rover-discovery-i-2.5-tdi-5-dr-113hp-5229
EU-ROVER-200-II-XW-HATCHBACK-5D-01	4220	1680	1390	Auto-Data Rover 200 (XW) generation	https://www.auto-data.net/en/rover-200-xw-generation-2451
EU-ROVER-200-II-XW-CONVERTIBLE-2D-01	4220	1680	1390	Auto-Data Rover 200 model (Cabrio XW)	https://www.auto-data.net/en/rover-200-model-1222
EU-ROVER-200-II-XW-COUPE-2D-01	4270	1680	1370	Auto-Data Rover 200 Coupe (XW) 220 Turbo	https://www.auto-data.net/en/rover-200-coupe-xw-220-turbo-200hp-11565
EU-ROVER-400-I-XW-SEDAN-4D-01	4370	1680	1400	Auto-Data Rover 400 model (XW)	https://www.auto-data.net/en/rover-400-model-1228
EU-ROVER-MONTEGO-ESTATE-WAGON-5D-01	4465	1710	1447	Automobile-Catalog 1993 Montego Estate 2.0 DLX Turbo	https://www.automobile-catalog.com/car/1993/1701485/montego_estate_2_0_dlx_turbo.html
EU-ROVER-100-XP-HATCHBACK-3D-01	3521	1550	1377	Auto-Data Rover 100 (METRO) (XP); Automobile-Catalog 1990 Rover 111 S	https://www.auto-data.net/en/rover-100-metro-xp-generation-2440;https://www.automobile-catalog.com/car/1990/3012515/rover_111_s_metro_1_1_s.html
EU-ROVER-100-XP-HATCHBACK-5D-01	3521	1550	1377	Auto-Data Rover 100 (METRO) (XP); Automobile-Catalog 1990 Rover 111 S	https://www.auto-data.net/en/rover-100-metro-xp-generation-2440;https://www.automobile-catalog.com/car/1990/3012515/rover_111_s_metro_1_1_s.html
EU-TRIUMPH-TR6-CONVERTIBLE-2D-01	3937	1473	1270	ADAC Triumph TR6 2.5 PI; Conceptcarz 1972 Triumph TR6	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/triumph/tr/tr6/351453/;https://www.conceptcarz.com/s7334/triumph-tr6.aspx
EU-TRIUMPH-SPITFIRE-MK-IV-CONVERTIBLE-2D-01	3790	1480	1210	CarsPlusPlus 1971 Triumph Spitfire Mk IV	https://carsplusplus.com/specs1971/triumph_spitfire_mk_iv.php
EU-TRIUMPH-SPITFIRE-1500-CONVERTIBLE-2D-01	3785	1488	1205	Automobile-Catalog 1975 Triumph Spitfire 1500	https://www.automobile-catalog.com/car/1975/33755/triumph_spitfire_1500.html
EU-TRIUMPH-TR7-COUPE-2D-01	4065	1681	1254	ADAC Triumph TR7 Coupé 2.0	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/triumph/tr/tr7/351430/
EU-FIAT-QUBO-I-MPV-5D-01	3959	1716	1735	Auto-Data Fiat Qubo generation	https://www.auto-data.net/en/fiat-qubo-generation-3984
EU-TRIUMPH-TR7-CONVERTIBLE-2D-01	4065	1681	1254	ADAC Triumph TR7 Cabriolet 2.0	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/triumph/tr7/7generation/351431/
EU-TRIUMPH-ACCLAIM-XD-SEDAN-4D-01	4094	1600	1339	Auto-Data Triumph Acclaim 1.3 XD	https://www.auto-data.net/en/triumph-acclaim-1.3-xd-70hp-5746
EU-MERCEDES-BENZ-CLS-C218-COUPE-PREFL-4D-01	4940	1881	1416	Auto-Data Mercedes-Benz CLS C218 CLS 250 CDI	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-cls-250-cdi-204hp-7g-tronic-plus-18694
EU-LANCIA-MUSA-I-FACELIFT-MPV-5D-01	4035	1698	1660	Automobile-Catalog 2010 Lancia Musa 1.6 Multijet 16V 120 Platino DPF	https://www.automobile-catalog.com/car/2010/1387370/lancia_musa_1_6_multijet_16v_120_platino_dpf.html
EU-MERCEDES-BENZ-CLS-C218-COUPE-FACELIFT-4D-01	4937	1881	1418	Auto-Data Mercedes-Benz CLS C218 facelift CLS 250 BlueTEC	https://www.auto-data.net/en/mercedes-benz-cls-coupe-c218-facelift-2014-cls-250-bluetec-204hp-9g-tronic-20854
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-PREFL-01	3790	1585	1345	Automobile-Catalog 1979 Mitsubishi Colt 1400 GLX 3-Door	https://www.automobile-catalog.com/car/1979/35765/mitsubishi_colt_1400_glx.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-FACELIFT-01	3805	1590	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 GLX 3-Door	https://www.automobile-catalog.com/car/1983/1913300/mitsubishi_colt_1400_glx_3-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-PREFL-01	3895	1585	1345	Automobile-Catalog 1979 Mitsubishi Colt 1400 GLX 5-Door	https://www.automobile-catalog.com/car/1979/36620/mitsubishi_colt_1400_glx_5-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-5D-FACELIFT-01	3930	1590	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 GLX 5-Door	https://www.automobile-catalog.com/car/1983/1913315/mitsubishi_colt_1400_glx_5-door.html
EU-MITSUBISHI-COLT-I-A150-HATCHBACK-3D-TURBO-01	3810	1585	1345	Automobile-Catalog 1983 Mitsubishi Colt 1400 Turbo	https://www.automobile-catalog.com/car/1983/55625/mitsubishi_colt_1400_turbo.html
EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-1P2-01	3870	1620	1360	Automobile-Catalog 1984 Mitsubishi Colt 1200 GL 3-Door	https://www.automobile-catalog.com/car/1984/63965/mitsubishi_colt_1_2_gl_5-speed.html
EU-MITSUBISHI-COLT-II-C10-HATCHBACK-5D-01	3870	1635	1360	Automobile-Catalog 1985 Mitsubishi Colt 1500 GLX 5-Door	https://www.automobile-catalog.com/car/1985/1914305/mitsubishi_colt_1500_glx_5-door.html
EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-01	3870	1635	1360	Automobile-Catalog 1985 Mitsubishi Colt 1500 GLX	https://www.automobile-catalog.com/car/1985/49235/mitsubishi_colt_1_5_glx.html
EU-MITSUBISHI-COLT-II-C10-HATCHBACK-3D-TURBO-01	4005	1635	1360	Automobile-Catalog 1986 Mitsubishi Colt 1600 Turbo ECI	https://www.automobile-catalog.com/car/1986/48290/mitsubishi_colt_1_6_turbo_eci.html
EU-MITSUBISHI-COLT-III-C50-HATCHBACK-3D-01	3950	1670	1380	Auto-Data Mitsubishi Colt III C50 1.3 12V; Automobile-Catalog 1988 Mitsubishi Colt 1300 GL	https://www.auto-data.net/en/mitsubishi-colt-iii-c50-1.3-12v-c51a-75hp-15767;https://www.automobile-catalog.com/car/1988/1933790/mitsubishi_colt_1300_gl.html
EU-RENAULT-KANGOO-I-FACELIFT-VAN-01	4035	1672	1885	Auto-Data Renault Kangoo I Express (FC facelift 2003)	https://www.auto-data.net/en/renault-kangoo-model-1045
EU-RENAULT-KANGOO-I-FACELIFT-MPV-5D-01	4035	1672	1885	Auto-Data Renault Kangoo I (KC facelift 2003)	https://www.auto-data.net/en/renault-kangoo-model-1045
EU-MITSUBISHI-LANCER-I-A70-SEDAN-2D-01	3995	1535	1375	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL	https://www.automobile-catalog.com/car/1978/35795/mitsubishi_lancer_1400_gl.html
EU-MITSUBISHI-LANCER-I-A70-SEDAN-4D-01	3995	1535	1375	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL	https://www.automobile-catalog.com/car/1978/35795/mitsubishi_lancer_1400_gl.html
EU-MITSUBISHI-LANCER-I-A70-WAGON-5D-01	3995	1535	1390	Automobile-Catalog 1978 Mitsubishi Lancer 1400 GL Estate	https://www.automobile-catalog.com/car/1978/1907045/mitsubishi_lancer_1400_gl_estate.html
EU-MITSUBISHI-LANCER-II-SEDAN-4D-01	4225	1620	1385	Auto-Data Mitsubishi Lancer II generation	https://www.auto-data.net/en/mitsubishi-lancer-ii-generation-3456
EU-MITSUBISHI-LANCER-F-SEDAN-4D-01	4185	1590	1345	Automobile-Catalog 1983 Mitsubishi Lancer F 1400 GLX	https://www.automobile-catalog.com/car/1983/1917230/mitsubishi_lancer_f_1400_glx.html
EU-MITSUBISHI-LANCER-III-SEDAN-4D-01	4125	1635	1360	Auto-Data Mitsubishi Lancer III 1.5	https://www.auto-data.net/en/mitsubishi-lancer-iii-1.5-75hp-15701
EU-MITSUBISHI-LANCER-III-WAGON-5D-01	4115	1635	1415	Auto-Data Mitsubishi Lancer III Wagon 1.8 D	https://www.auto-data.net/en/mitsubishi-lancer-iii-wagon-1.8-d-60hp-15697
EU-MITSUBISHI-LANCER-IV-SEDAN-4D-01	4235	1670	1405	Auto-Data Mitsubishi Lancer IV 1.5 12V	https://www.auto-data.net/en/mitsubishi-lancer-iv-1.5-12v-90hp-15671
EU-MITSUBISHI-LANCER-IV-HATCHBACK-5D-01	4235	1670	1405	Auto-Data Mitsubishi Lancer IV Hatchback	https://www.auto-data.net/en/mitsubishi-lancer-iv-hatchback-generation-3452
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_3101-3200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/triumph/tr/tr7/351430/ "https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/triumph/tr/tr7/351430/"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_3101-3200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_3101-3200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（3724 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1013 行）
