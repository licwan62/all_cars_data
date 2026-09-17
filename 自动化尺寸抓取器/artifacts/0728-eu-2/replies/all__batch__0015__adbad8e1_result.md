# 任务：all 第 1401-1500 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0015__adbad8e1


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1401-1500 行

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
all 第 1401-1500 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	Q7	4.2 TDI Quattro	SUV	Allrad	Diesel	240	326	Mar 2007	Jun 2009	2024-03-01	22558
Mazda	Bt-50	2.5 Mrz-cd 4X4	Pick-up	Allrad	Diesel	105	143	Dec 2006	Dec 2015	2024-03-01	22559
Opel	Meriva a	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	51	69	Apr 2005	May 2010	2024-03-01	22560
Smart	Forfour	1.5	Schrägheck	Frontantrieb	Benzin	90	122	Jan 2004	Jun 2006	2024-03-01	22561
Alfa Romeo	Spider	2.4 Jtdm	Cabriolet	Frontantrieb	Diesel	147	200	Mar 2006	Mar 2011	2024-03-01	22562
Chevrolet	Caprice	5.7 D	Stufenheck	Heckantrieb	Diesel	78	106	Oct 1979	Dec 1985	2024-03-01	22570
Chevrolet	Corvette	5.7	Cabriolet	Heckantrieb	Benzin	207	282	Oct 1991	Sep 1997	2024-03-01	22572
Daihatsu	Sirion	1	Schrägheck	Frontantrieb	Benzin	40	54	Apr 1998	Oct 2000	2024-03-01	22576
Chevrolet	Epica	2	Stufenheck	Frontantrieb	Benzin	98	133	Jan 2005	Dec 2006	2024-03-01	22591
Cadillac	Fleetwood	5	Stufenheck	Heckantrieb	Benzin	104	141	Oct 1985	Sep 1986	2024-03-01	22594
Cadillac	Fleetwood	5	Stufenheck	Heckantrieb	Benzin	127	173	Sep 1988	Sep 1990	2024-03-01	22595
VW	Passat b2	2	Stufenheck	Frontantrieb	Benzin	85	116	Aug 1984	Jul 1985	2024-03-01	22613
Volvo	740	2.0 GLE	Stufenheck	Heckantrieb	Benzin	85	116	Apr 1983	Jul 1984	2024-03-01	22616
Volvo	850	2.4 GLE	Stufenheck	Frontantrieb	Benzin	142	193	Sep 1993	Oct 1997	2024-03-01	22618
Daihatsu	Gran move	1.6 GX	Großraumlimousine	Frontantrieb	Benzin	67	91	Jun 1998	Jul 2002	2024-03-01	22623
Alfa Romeo	156	1.9 JTD	Kombi	Frontantrieb	Diesel	110	150	Mar 2005	May 2006	2024-03-01	22625
Volvo	S80 i	T5 AWD	Stufenheck	Allrad	Benzin	147	200	Apr 2000	Sep 2003	2024-03-01	22639
Volvo	S60 i	T5	Stufenheck	Frontantrieb	Benzin	195	265	Jul 2000	Sep 2002	2024-03-01	22640
Volvo	S70	2.3 T5 AWD	Stufenheck	Allrad	Benzin	177	241	Nov 1996	Sep 1998	2024-03-01	22641
Volvo	S70	2.4 T5 AWD	Stufenheck	Allrad	Benzin	142	193	Nov 1996	Apr 1999	2024-03-01	22644
Buick	Park avenue	3.8 Ultra	Stufenheck	Frontantrieb	Benzin	168	228	Oct 1990	Sep 1996	2024-03-01	22649
Honda	Cr-V iii	2.0 I-vtec 4WD	SUV	Allrad	Benzin	110	150	Oct 2006	Jun 2012	2024-03-01	22650
Honda	Cr-V iii	2.2 I-ctdi 4WD	SUV	Allrad	Diesel	103	140	Jan 2007	Feb 2010	2025-12-01	22651
Mitsubishi	Pajero iv	3.8 V6	SUV	Allrad	Benzin	184	250	Feb 2007	-	2024-03-01	22652
Mitsubishi	Pajero iv	3.2 Di-d	SUV	Allrad	Diesel	118	160	Feb 2007	-	2024-03-01	22653
Mitsubishi	Pajero iv	3.2 Di-d	SUV	Allrad	Diesel	125	170	Feb 2007	-	2024-03-01	22654
BMW	5	535 D	Stufenheck	Heckantrieb	Diesel	210	286	Jan 2007	Mar 2010	2024-03-01	22656
BMW	5	525 I	Stufenheck	Heckantrieb	Benzin	160	218	Jan 2007	Mar 2010	2024-03-01	22657
BMW	5	525 XI	Stufenheck	Allrad	Benzin	160	218	Mar 2007	Dec 2009	2024-03-01	22658
BMW	5	523 I	Stufenheck	Heckantrieb	Benzin	140	190	Mar 2007	Dec 2009	2024-03-01	22659
BMW	5	525 D	Stufenheck	Heckantrieb	Diesel	145	197	Jan 2007	Mar 2010	2024-03-01	22660
BMW	5	530 D	Stufenheck	Heckantrieb	Diesel	173	235	Feb 2007	Dec 2009	2024-03-01	22661
BMW	5	530 XD	Stufenheck	Allrad	Diesel	173	235	Mar 2007	Aug 2007	2024-03-01	22662
BMW	5	530 I	Stufenheck	Heckantrieb	Benzin	200	272	Mar 2007	Dec 2009	2024-03-01	22663
BMW	5	530 XI	Stufenheck	Allrad	Benzin	200	272	Feb 2007	Aug 2008	2024-03-01	22664
BMW	5	525 D	Kombi	Heckantrieb	Diesel	145	197	Mar 2007	May 2010	2024-03-01	22665
BMW	5	530 D	Kombi	Heckantrieb	Diesel	173	235	Feb 2007	May 2010	2024-03-01	22666
BMW	5	530 XD	Kombi	Allrad	Diesel	173	235	Mar 2007	Aug 2007	2024-03-01	22667
BMW	5	530 I	Kombi	Heckantrieb	Benzin	200	272	Jan 2007	Dec 2010	2024-03-01	22668
BMW	5	530 XI	Kombi	Allrad	Benzin	200	272	Mar 2007	May 2010	2024-03-01	22669
BMW	5	525 I	Kombi	Heckantrieb	Benzin	160	218	Jan 2007	Dec 2010	2024-03-01	22670
BMW	5	525 XI	Kombi	Allrad	Benzin	160	218	Jan 2007	Dec 2010	2024-03-01	22671
BMW	5	535 D	Kombi	Heckantrieb	Diesel	210	286	Jan 2007	Dec 2010	2024-03-01	22672
BMW	5	523 I	Kombi	Heckantrieb	Benzin	140	190	Mar 2007	Jan 2010	2024-03-01	22673
Renault	Clio iii	2.0 16V	Schrägheck	Frontantrieb	Benzin	102	139	Sep 2006	Dec 2014	2026-05-01	22674
Opel	Corsa d	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	141	192	Nov 2006	Aug 2014	2024-03-01	22675
Opel	Astra h	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Feb 2007	Oct 2010	2024-03-01	22676
Opel	Astra h twintop	1.6 Turbo	Cabriolet	Frontantrieb	Benzin	132	180	Feb 2007	Oct 2010	2024-03-01	22677
Opel	Astra h caravan	1.6 Turbo	Kombi	Frontantrieb	Benzin	132	180	Feb 2007	Oct 2010	2024-03-01	22678
Opel	Astra h gtc	1.6 Turbo	Schrägheck	Frontantrieb	Benzin	132	180	Feb 2007	Oct 2010	2024-03-01	22679
Opel	Astra h gtc	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Dec 2006	Oct 2010	2024-03-01	22680
Peugeot	207/207+	1.6 16V VTI	Schrägheck	Frontantrieb	Benzin	88	120	Feb 2007	Dec 2012	2024-03-01	22681
Opel	Astra h	1.6	Schrägheck	Frontantrieb	Benzin	85	116	Nov 2006	Sep 2009	2026-05-01	22682
Opel	Astra h caravan	1.6	Kombi	Frontantrieb	Benzin	85	116	Nov 2006	Oct 2010	2026-05-01	22683
Opel	Astra h twintop	1.6	Cabriolet	Frontantrieb	Benzin	85	116	Dec 2006	Oct 2010	2024-03-01	22684
Peugeot	207/207+	1.6 16V RC	Schrägheck	Frontantrieb	Benzin	128	174	Feb 2007	Dec 2012	2024-03-01	22685
Opel	Astra h	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Apr 2007	Sep 2009	2026-05-01	22686
Opel	Astra h gtc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	81	110	Feb 2007	Oct 2010	2024-03-01	22687
Opel	Astra h caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	81	110	Dec 2008	Oct 2010	2026-04-01	22688
Opel	Astra h	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	92	125	Apr 2007	Sep 2009	2026-05-01	22689
Opel	Astra h gtc	1.7 Cdti	Schrägheck	Frontantrieb	Diesel	92	125	Feb 2007	Oct 2010	2024-03-01	22690
Opel	Astra h caravan	1.7 Cdti	Kombi	Frontantrieb	Diesel	92	125	Apr 2007	Oct 2010	2026-05-01	22691
Peugeot	Expert	2.0 16V	Bus	Frontantrieb	Benzin	103	140	Jan 2007	Mar 2016	2024-03-01	22692
Peugeot	Expert	2.0 16V	Kasten	Frontantrieb	Benzin	103	140	Jan 2007	-	2024-03-01	22693
Seat	Altea	2.0 TDI	Großraumlimousine	Frontantrieb	Diesel	125	170	Jun 2007	Dec 2013	2024-03-01	22694
Seat	Altea	1.8 Tfsi	Großraumlimousine	Frontantrieb	Benzin	118	160	Jan 2007	Jul 2015	2024-05-01	22695
BMW	5	M5	Kombi	Heckantrieb	Benzin	373	507	Feb 2007	Dec 2010	2024-03-01	22696
Toyota	Land cruiser prado	3.0 D-4d	Geländewagen geschlossen	Allrad	Diesel	127	173	Sep 2002	Dec 2010	2024-03-01	22697
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	70	95	Sep 2006	Dec 2012	2024-03-01	22698
Toyota	Hiace iv	2.5 D-4d	Bus	Heckantrieb	Diesel	86	117	Aug 2006	Dec 2012	2024-03-01	22699
Mercedes-benz	C-Klasse	C 280	Stufenheck	Heckantrieb	Benzin	170	231	Jan 2007	Jan 2014	2024-03-01	22700
Mercedes-benz	C-Klasse	C 350	Stufenheck	Heckantrieb	Benzin	200	272	Jan 2007	Jan 2014	2024-03-01	22701
Nissan	Cabstar	2	Pritsche/Fahrgestell	Heckantrieb	Benzin	66	90	Jan 1982	Jun 1992	2024-03-01	22714
Nissan	Cedric	3	Stufenheck	Heckantrieb	Benzin	132	179	Oct 1983	Aug 1987	2024-03-01	22723
Nissan	Cedric	3	Stufenheck	Heckantrieb	Benzin	118	160	Sep 1987	May 1991	2024-03-01	22725
Audi	A4 b8 avant	3.0 TDI	Kombi	Frontantrieb	Diesel	150	204	Nov 2011	Dec 2015	2024-03-01	22732
Fiat	Sedici	1.9 D Multijet	SUV	Frontantrieb	Diesel	88	120	Jun 2006	Oct 2011	2024-03-01	22740
Audi	A5	2.0 TDI	Cabriolet	Frontantrieb	Diesel	105	143	Oct 2011	May 2015	2024-03-01	22766
Audi	A5	2.0 TDI Quattro	Cabriolet	Allrad	Diesel	130	177	Jan 2012	May 2015	2024-03-01	22769
Toyota	Corona	1.6	Stufenheck	Frontantrieb	Benzin	73	99	Feb 1992	Sep 1997	2024-03-01	22795
Audi	A5	3.0 Tfsi Quattro	Cabriolet	Allrad	Benzin	200	272	Nov 2011	Jan 2017	2024-03-01	22808
Audi	A5	2.0 TDI Quattro	Coupe	Allrad	Diesel	130	177	Dec 2011	Jan 2017	2024-03-01	22826
Audi	A5	3.0 Tfsi Quattro	Coupe	Allrad	Benzin	200	272	Dec 2011	Jan 2017	2024-03-01	22836
Mazda	929 iv	3	Stufenheck	Heckantrieb	Benzin	123	167	Dec 1990	Sep 1992	2024-03-01	22865
KIA	Cerato i	1.6	Stufenheck	Frontantrieb	Benzin	90	122	May 2006	Dec 2009	2024-03-01	22922
Audi	A6 c7	2.0 TDI	Stufenheck	Frontantrieb	Diesel	100	136	Jan 2012	Sep 2018	2024-03-01	22928
Audi	A6 c7 avant	2.0 TDI	Kombi	Frontantrieb	Diesel	100	136	Jan 2012	Sep 2018	2024-03-01	22929
Ford USA	Bronco	5.0 XLT	SUV	Heckantrieb	Benzin	103	140	Oct 1977	Sep 1980	2024-03-01	22931
Ford USA	Bronco	5.0 XLT 4WD	SUV	Allrad	Benzin	103	140	Oct 1977	Sep 1980	2024-03-01	22932
Ford USA	Expedition	4.6 XLT	SUV	Heckantrieb	Benzin	158	215	Aug 1996	Sep 2002	2024-03-01	22933
Ford USA	Expedition	5.4 XLT	SUV	Heckantrieb	Benzin	194	264	Aug 1996	Sep 2002	2024-03-01	22934
VW	Amarok	2.0 Bitdi 4motion	Pick-up	Allrad	Diesel	132	180	Nov 2011	May 2022	2024-03-01	22936
BMW	3	M3	Coupe	Heckantrieb	Benzin	309	420	Jun 2007	Jun 2013	2024-03-01	22939
VW	Golf v variant	2.0 TDI	Kombi	Frontantrieb	Diesel	103	140	Jun 2007	Jul 2009	2024-03-01	22940
Opel	Antara a	3.2 V6	SUV	Allrad	Benzin	167	227	Aug 2006	Dec 2011	2024-03-01	22941
Nissan	Qashqai i	2.0 DCI Allrad	SUV	Allrad	Diesel	110	150	Feb 2007	Dec 2013	2025-06-01	22942
Skoda	Fabia ii	1.2	Schrägheck	Frontantrieb	Benzin	44	60	Dec 2006	Dec 2014	2024-03-01	22944
Skoda	Fabia ii	1.2	Schrägheck	Frontantrieb	Benzin	51	70	Jan 2007	Dec 2014	2024-03-01	22945
Skoda	Fabia ii	1.4	Schrägheck	Frontantrieb	Benzin	63	86	Jan 2007	Dec 2014	2024-03-01	22946
Skoda	Fabia ii	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Apr 2007	Dec 2014	2024-03-01	22947


--- Round 1 / 首次发送 ---
## 更新点

* 本轮按物理外廓聚类，闭合 **BMW 5 Series E60/E61、BMW M5 Touring、BMW M3 E92、Opel Astra H 四种车身，以及 Audi Q7/A4/A5/A6**，共处理 43 个 Ktype。
* BMW 轿车、旅行车及 M 车型分别建组，未因同属 5 系而错误合并。([汽车数据网][1])
* Astra H 的五门掀背、GTC 三门、Caravan 和 TwinTop 四种外廓分别建组。([汽车数据网][2])
* Audi Q7、A4 Avant、A5 Cabriolet/Coupe、A6 Sedan/Avant 已按车身代码和结构拆分；尺寸宽度统一采用车身宽度字段，不采用含后视镜宽度。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* READY 映射：43
* PENDING／待闭合：57
* 已确认尺寸组：14
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22558	22558	SUV	Q7 I	4L	5	EU-AUDI-Q7-4L-SUV-01	HIGH	4L五门SUV外廓。	READY
22656	22656	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22657	22657	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22658	22658	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22659	22659	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22660	22660	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22661	22661	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22662	22662	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22663	22663	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22664	22664	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22665	22665	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22666	22666	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22667	22667	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22668	22668	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22669	22669	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22670	22670	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22671	22671	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22672	22672	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22673	22673	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22676	22676	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22677	22677	Convertible	Astra H		2	EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	HIGH	TwinTop双门敞篷外廓。	READY
22678	22678	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22679	22679	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22680	22680	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22682	22682	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22683	22683	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22684	22684	Convertible	Astra H		2	EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	HIGH	TwinTop双门敞篷外廓。	READY
22686	22686	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22687	22687	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22688	22688	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22689	22689	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22690	22690	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22691	22691	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22696	22696	Wagon	M5 E61 LCI	E61	5	EU-BMW-M5-E61-LCI-WAGON-01	HIGH	E61 M5 Touring专用外廓。	READY
22732	22732	Wagon	A4 B8 facelift	8K	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	B8 Avant五门旅行车外廓。	READY
22766	22766	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22769	22769	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22808	22808	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22826	22826	Coupe	A5 I facelift	8T3	2	EU-AUDI-A5-8T3-FACELIFT-COUPE-01	HIGH	8T3双门轿跑外廓。	READY
22836	22836	Coupe	A5 I facelift	8T3	2	EU-AUDI-A5-8T3-FACELIFT-COUPE-01	HIGH	8T3双门轿跑外廓。	READY
22928	22928	Sedan	A6 C7	4G	4	EU-AUDI-A6-C7-SEDAN-01	HIGH	C7四门轿车外廓。	READY
22929	22929	Wagon	A6 C7	4G	5	EU-AUDI-A6-C7-AVANT-WAGON-01	HIGH	C7 Avant五门旅行车外廓。	READY
22939	22939	Coupe	M3 E92	E92	2	EU-BMW-M3-E92-COUPE-01	HIGH	E92双门轿跑外廓。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737	Auto-Data Audi Q7 I Typ 4L 4.2 TDI	https://www.auto-data.net/en/audi-q7-i-typ-4l-4.2-tdi-v8-326hp-quattro-dpf-tiptronic-4858
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468	Auto-Data BMW 5 Series E60 LCI 523i	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-523i-190hp-27944
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491	Auto-Data BMW 5 Series Touring E61 LCI 535d	https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-535d-286hp-steptronic-28307
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1460	Auto-Data Opel Astra H facelift 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-turbo-ecotec-180hp-47450
EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	4476	1759	1411	Auto-Data Opel Astra H TwinTop 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-twintop-1.6i-16v-turbo-180hp-26337
EU-OPEL-ASTRA-H-WAGON-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift 1.6	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.6-ecotec-115hp-47461
EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	4290	1753	1435	Auto-Data Opel Astra H GTC facelift 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.6-turbo-ecotec-180hp-47428
EU-BMW-M5-E61-LCI-WAGON-01	4855	1846	1512	Auto-Data BMW M5 Touring E61 LCI	https://www.auto-data.net/en/bmw-m5-touring-e61-lci-facelift-2007-5.0-v10-507hp-smg-9867
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 facelift	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-2.0-tdi-136hp-start-stop-18899
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383	Auto-Data Audi A5 Cabriolet 8F7 facelift	https://www.auto-data.net/en/audi-a5-cabriolet-8f7-facelift-2011-2.0-tdi-143hp-26629
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372	Auto-Data Audi A5 Coupe 8T3 facelift	https://www.auto-data.net/en/audi-a5-coupe-8t3-facelift-2011-3.0-tfsi-v6-272hp-quattro-s-tronic-19041
EU-AUDI-A6-C7-SEDAN-01	4915	1874	1468	Auto-Data Audi A6 Sedan C7	https://www.auto-data.net/en/audi-a6-limousine-4g-c7-2.0-tdi-136hp-19099
EU-AUDI-A6-C7-AVANT-WAGON-01	4926	1874	1468	Auto-Data Audi A6 Avant C7	https://www.auto-data.net/en/audi-a6-avant-4g-c7-2.0-tfsi-180hp-19103
EU-BMW-M3-E92-COUPE-01	4615	1804	1424	Auto-Data BMW M3 Coupe E92; Auto-Data BMW M3 Coupe E92 LCI	https://www.auto-data.net/en/bmw-m3-coupe-e92-generation-2003;https://www.auto-data.net/en/bmw-m3-coupe-e92-lci-facelift-2010-4.0-v8-420hp-52643
```

## 下一步优先处理

1. 批量闭合 Honda CR-V III、Mitsubishi Pajero IV、Skoda Fabia II、Peugeot 207 和 Seat Altea 等可多 Ktype 复用的尺寸组。
2. 单独处理可能需要物理分支拆分的 Mazda BT-50、Peugeot Expert、Toyota Hiace IV、VW Amarok、Nissan Cabstar及经典美系车型。
3. 核对 Mitsubishi Pajero IV 三门与五门、Toyota Land Cruiser Prado 短轴与长轴是否需要派生 `id`。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-523i-190hp-27944 "BMW 5 Series (E60 LCI, facelift 2007) 523i (190 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-turbo-ecotec-180hp-47450 "Opel Astra H (facelift 2007) 1.6 Turbo ECOTEC (180 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/audi-q7-i-typ-4l-4.2-tdi-v8-326hp-quattro-dpf-tiptronic-4858 "Audi Q7 I (Typ 4L) 4.2 TDI V8 (326 Hp) quattro DPF tiptronic | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 本轮新增闭合 10 个尺寸组，覆盖 Honda CR-V III、Mitsubishi Pajero IV、Renault Clio III、Opel Corsa D OPC、Peugeot 207、Seat Altea 与 Skoda Fabia II。([汽车数据网][1])
* Pajero IV 按三门短轴、五门长轴拆分；Clio III 与 Peugeot 207 按三门、五门物理车身拆分。相同三维未被当作相同物理车身合并。([汽车数据网][2])
* Corsa D 192 hp 已确定为三门 OPC 外廓，采用该具体性能版本的 4040 × 1713 × 1488 mm，而非普通 Corsa D 长度。([汽车数据网][3])
* Peugeot Expert 的 L1/L2 与乘用版/厢式版边界仍需一次车型直接来源闭合，本轮未创建临时尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype 覆盖：58
* READY 映射行：63
* PENDING Ktype：42
* 已确认尺寸组：24
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22650	22650	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
22651	22651	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
22652_3dr	22652	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22652_5dr	22652	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22653_3dr	22653	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22653_5dr	22653	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22654_3dr	22654	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22654_5dr	22654	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22674_3dr	22674	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-01	MEDIUM	输入未区分门数；拆分三门车身。	READY
22674_5dr	22674	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-01	MEDIUM	输入未区分门数；拆分五门车身。	READY
22675	22675	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	HIGH	192 hp OPC仅对应三门性能车身。	READY
22681_3dr	22681	Hatchback	207		3	EU-PEUGEOT-207-HATCHBACK-3D-01	MEDIUM	输入未区分门数；拆分三门车身。	READY
22681_5dr	22681	Hatchback	207		5	EU-PEUGEOT-207-HATCHBACK-5D-01	MEDIUM	输入未区分门数；拆分五门车身。	READY
22685	22685	Hatchback	207		3	EU-PEUGEOT-207-HATCHBACK-3D-01	HIGH	RC版本为三门车身。	READY
22694	22694	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门标准Altea外廓。	READY
22695	22695	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门标准Altea外廓。	READY
22944	22944	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22945	22945	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22946	22946	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22947	22947	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675	Auto-Data Honda CR-V III 2.0 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-12335
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV 3.8 V6 3-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-3-doors-15485
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870	Auto-Data Mitsubishi Pajero IV 3.8 V6 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-5-doors-15486
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 2.0 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-2.0-16v-139hp-25243
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 5-door 2.0 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-2.0-16v-139hp-56137
EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	4040	1713	1488	Auto-Data Opel Corsa D 3-door OPC 192 hp	https://www.auto-data.net/en/opel-corsa-d-3-door-1.6i-16v-opc-192hp-2088
EU-PEUGEOT-207-HATCHBACK-3D-01	4030	1720	1472	Auto-Data Peugeot 207 RC 1.6 174 hp	https://www.auto-data.net/en/peugeot-207-rc-1.6-174hp-33994
EU-PEUGEOT-207-HATCHBACK-5D-01	4030	1720	1472	Auto-Data Peugeot 207 1.6 16V 120 hp	https://www.auto-data.net/en/peugeot-207-1.6-i-16v-120hp-automatic-5357
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Auto-Data Seat Altea 5P 1.8 TSI	https://www.auto-data.net/en/seat-altea-5p-1.8-tsi-160hp-dsg-16901
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498	Auto-Data Skoda Fabia II 1.2 HTP	https://www.auto-data.net/en/skoda-fabia-ii-1.2-i-htp-12v-69hp-14130
```

## 下一步优先处理

1. 闭合 Peugeot Expert 的 L1/L2 乘用版与厢式版边界。
2. 批量处理 Volvo S60/S70/S80、740、850 及 BMW 之外的欧洲轿车簇。
3. 处理 Toyota Hiace、Land Cruiser Prado、Mazda BT-50、VW Amarok 等需要轴距或车身分支拆分的车型。
4. 最后处理美系经典车型、Nissan Cabstar/Cedric 等低复用单项。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-12335 "Honda CR-V III 2.0 i-VTEC (150 Hp) AWD | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-3-doors-15485 "Mitsubishi Pajero IV 3.8 i V6 24V MIVEC (250 Hp) 3-doors | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-corsa-d-3-door-1.6i-16v-opc-192hp-2088 "Opel Corsa D 3-door 1.6i 16V OPC (192 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 闭合 Alfa Romeo Spider 939 双门敞篷外廓，新增 1 个映射和 1 个尺寸组。([Stellantis Media][1])
* Toyota Hiace IV 的两条 Bus Ktype 均未注明轴距，按照官方 SWB、LWB 两种外廓完整拆分，共新增 4 个派生映射和 2 个尺寸组。([Toyota Media Site][2])
* Mercedes-Benz C 280 与 C 350 均确认属于 W204 四门轿车；两者官方高度分别为 1444 mm、1448 mm，因此分别建组，未强行合并。([marsClassic][3])
* 闭合 Fiat Sedici 五门 SUV 外廓，新增 1 个映射和 1 个尺寸组。([Stellantis Media][4])
* 本轮未重复输出前两轮已闭合的 24 个尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype 覆盖：64
* READY 映射行：71
* PENDING Ktype：36
* 已确认尺寸组：30
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22562	22562	Convertible	Spider (939)	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
22698_swb	22698	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距；拆分短轴外廓。	READY
22698_lwb	22698	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距；拆分长轴外廓。	READY
22699_swb	22699	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距；拆分短轴外廓。	READY
22699_lwb	22699	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距；拆分长轴外廓。	READY
22700	22700	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C280-01	HIGH	W204 C 280四门轿车；官方高度与C 350不同。	READY
22701	22701	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C350-01	HIGH	W204 C 350四门轿车；官方高度与C 280不同。	READY
22740	22740	SUV	Sedici		5	EU-FIAT-SEDICI-SUV-01	HIGH	五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Alfa Romeo New Spider official UK press material	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-spider-on-sale-in-uk
EU-TOYOTA-HIACE-IV-BUS-SWB-01	4795	1800	2000	Toyota Hiace 2007 official technical specification	https://media.toyota.co.uk/more-power-new-looks-for-2007-toyota-hiace/
EU-TOYOTA-HIACE-IV-BUS-LWB-01	5240	1800	1995	Toyota Hiace 2007 official technical specification	https://media.toyota.co.uk/more-power-new-looks-for-2007-toyota-hiace/
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C280-01	4581	1770	1444	Mercedes-Benz Public Archive W204 saloons; Mercedes-Benz C-Class 2007 Owner's Manual	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://static.oneweb.mercedes-benz.com/css-oom-assets/en-mt/pdf/mercedes-c-class-sedan-2007-w204-owners-manual-1.pdf
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C350-01	4581	1770	1448	Mercedes-Benz Public Archive W204 saloons; Mercedes-Benz C-Class 2007 Owner's Manual	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://static.oneweb.mercedes-benz.com/css-oom-assets/en-mt/pdf/mercedes-c-class-sedan-2007-w204-owners-manual-1.pdf
EU-FIAT-SEDICI-SUV-01	4115	1755	1620	Fiat Sedici official price list	https://www.media.stellantis.com/uploads/at/AT/Preislisten/FIAT/Preisliste_Sedici.pdf
```

## 下一步优先处理

1. 批量闭合 Volvo 740、850、S60 I、S70、S80 I 的轿车尺寸组。
2. 处理 Opel Meriva A、Smart Forfour、Daihatsu Sirion、Gran Move、Kia Cerato I 等单一紧凑车身。
3. 核对 Peugeot Expert Bus/Kasten 的 L1、L2 分支及高度边界。
4. 处理 Toyota Land Cruiser Prado、Mazda BT-50、VW Amarok、Nissan Cabstar等轴距、驾驶室或车身分支较多的车型。

推进信号：CONTINUE

[1]: https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-spider-on-sale-in-uk?utm_source=chatgpt.com "NEW ALFA SPIDER ON SALE IN UK | Alfa Romeo"
[2]: https://media.toyota.co.uk/more-power-new-looks-for-2007-toyota-hiace/?utm_source=chatgpt.com "More Power, New Looks For 2007 Toyota Hiace"
[3]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327&utm_source=chatgpt.com "204 series C-Class Saloons, 2007 - 2011"
[4]: https://www.media.stellantis.com/uploads/at/AT/Preislisten/FIAT/Preisliste_Sedici.pdf?utm_source=chatgpt.com "Fiat SEDICI"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 本轮闭合 Opel Meriva A、Smart Forfour W454、Daihatsu Sirion M1，共新增 3 个映射和 3 个尺寸组。([汽车数据网][1])
* 闭合 Volvo 850 LS 与 Volvo S60 I 改款前轿车外廓，共新增 2 个映射和 2 个尺寸组。([汽车数据网][2])
* 闭合 Volkswagen Golf V Variant 与 Opel Antara A，共新增 2 个映射和 2 个尺寸组。([汽车数据网][3])
* 本轮未重复输出前序已确认的尺寸组。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype 覆盖：71
* READY 映射行：78
* PENDING Ktype：29
* 已确认尺寸组：37
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22560	22560	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH	Meriva A五门MPV外廓。	READY
22561	22561	Hatchback	Forfour W454	W454	5	EU-SMART-FORFOUR-W454-HATCHBACK-01	HIGH	W454五门掀背外廓。	READY
22576	22576	Hatchback	Sirion M1	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH	M1五门掀背外廓。	READY
22618	22618	Sedan	850	LS	4	EU-VOLVO-850-LS-SEDAN-01	MEDIUM	LS四门轿车外廓。	READY
22640	22640	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-PREFL-01	HIGH	第一代改款前四门轿车外廓。	READY
22940	22940	Wagon	Golf V Variant		5	EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-01	HIGH	五门旅行车外廓。	READY
22941	22941	SUV	Antara A		5	EU-OPEL-ANTARA-A-SUV-01	HIGH	初代五门SUV外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-MERIVA-A-MPV-01	4042	1694	1624	Auto-Data Opel Meriva A 1.3 CDTI	https://www.auto-data.net/en/opel-meriva-a-1.3-cdti-75hp-ecotec-2515
EU-SMART-FORFOUR-W454-HATCHBACK-01	3752	1684	1450	Auto-Data Smart Forfour W454 generation	https://www.auto-data.net/en/smart-forfour-w454-generation-3286
EU-DAIHATSU-SIRION-M1-HATCHBACK-01	3675	1595	1450	Auto-Data Daihatsu Sirion M1 1.0 i 12V	https://www.auto-data.net/en/daihatsu-sirion-m1-1.0-i-12v-56hp-84
EU-VOLVO-850-LS-SEDAN-01	4660	1761	1415	Auto-Data Volvo 850 LS generation	https://www.auto-data.net/en/volvo-850-ls-generation-1928
EU-VOLVO-S60-I-SEDAN-PREFL-01	4576	1804	1428	Auto-Data Volvo S60 2.3 T5 20V	https://www.auto-data.net/en/volvo-s60-2.3-t5-20v-250hp-9227
EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-01	4556	1781	1504	Auto-Data Volkswagen Golf V Variant 2.0 TDI	https://www.auto-data.net/en/volkswagen-golf-v-variant-2.0-tdi-140hp-8647
EU-OPEL-ANTARA-A-SUV-01	4575	1850	1704	Auto-Data Opel Antara generation	https://www.auto-data.net/en/opel-antara-generation-497
```

## 下一步优先处理

1. 闭合 Peugeot Expert Bus/Kasten 的 L1、L2 车长及车顶高度分支。
2. 处理 Nissan Qashqai I 改款前后，以及 Land Cruiser Prado、Mazda BT-50、VW Amarok 的多外廓分支。
3. 闭合 Volvo S70/S80 AWD、Daihatsu Gran Move 改款前后和 Alfa Romeo 156 Sportwagon。
4. 最后处理美系经典车型及 Nissan Cabstar、Cedric 等低复用车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-meriva-a-1.3-cdti-75hp-ecotec-2515 "Opel Meriva A 1.3 CDTI (75 Hp) ECOTEC | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/volvo-850-ls-generation-1928 "Volvo 850 (LS) | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/volkswagen-golf-v-variant-2.0-tdi-140hp-8647 "Volkswagen Golf V Variant 2.0 TDI (140 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 本轮新增 11 条 READY 映射，覆盖 8 个 Ktype；首次创建 10 个尺寸组。
* Chevrolet Epica 22591 确认为 KL1/V200 旧车身，未与 2006 年后长度 4805 mm 的新一代 Epica 合并。([Autodoc][1])
* Volvo 740、S70、S80 I 和 Daihatsu Gran Move 的单一轿车或 MPV 外廓已闭合；S80 输入版本名称存在异常，因此映射置信度保留为 MEDIUM。([车库网][2])
* Peugeot Expert Bus 由于输入未区分 L1/L2 和 1942/1880 mm 两种车高，拆成四个明确物理分支，没有任选单一尺寸。([汽车展示网][3])
* Kia Cerato I 122 hp 已按匹配生产期的 LD 改款四门轿车外廓闭合。([CarSpecsGuru][4])

## 当前批次进度

* 输入 Ktype：100
* READY Ktype 覆盖：79
* READY 映射行：89
* PENDING Ktype：21
* 已确认尺寸组：47
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22591	22591	Sedan	Epica V200	KL1	4	EU-CHEVROLET-EPICA-V200-SEDAN-01	HIGH	KL1/V200四门轿车；与后续V250车身分开。	READY
22616	22616	Sedan	740		4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	早期四门轿车外廓。	READY
22623	22623	MPV	Gran Move		5	EU-DAIHATSU-GRAN-MOVE-MPV-01	HIGH	1.6升五门MPV外廓。	READY
22639	22639	Sedan	S80 I		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	MEDIUM	输入版本名含AWD；物理边界按S80 I改款前四门轿车。	READY
22641	22641	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	MEDIUM	AWD版本四门轿车外廓。	READY
22644	22644	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	MEDIUM	AWD版本四门轿车外廓。	READY
22692_l1_standard	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	MEDIUM	输入未区分轴距和车高；L1标准车高分支。	READY
22692_l1_low	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	MEDIUM	输入未区分轴距和车高；L1低车高分支。	READY
22692_l2_standard	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	MEDIUM	输入未区分轴距和车高；L2标准车高分支。	READY
22692_l2_low	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	MEDIUM	输入未区分轴距和车高；L2低车高分支。	READY
22922	22922	Sedan	Cerato I facelift	LD	4	EU-KIA-CERATO-I-FACELIFT-SEDAN-01	HIGH	LD改款四门轿车外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440	AutoCango 2005 Chevrolet Epica 2.0; AutoZine Daewoo Magnus/Chevrolet Epica	https://www.autocango.com/carspecs-detail/Chevrolet-Epica-XBA4;https://www.autozine.org/Archive/Daewoo/old/Magnus.html
EU-VOLVO-740-SEDAN-PREFL-01	4785	1760	1430	Carfolio 1983 Volvo 740 GLE	https://www.carfolio.com/volvo-740-gle-106293
EU-DAIHATSU-GRAN-MOVE-MPV-01	4100	1640	1600	UltimateSpecs Daihatsu Grand Move 1.6i	https://www.ultimatespecs.com/car-specs/Daihatsu/4839/Daihatsu-Grand-Move-16i.html
EU-VOLVO-S80-I-SEDAN-PREFL-01	4822	1832	1434	Auto-Data Volvo S80 2.4T 200 hp	https://www.auto-data.net/en/volvo-s80-2.4t-200hp-9374
EU-VOLVO-S70-SEDAN-01	4720	1760	1400	Auto-Data Volvo S70 2.5 20V Turbo	https://www.auto-data.net/en/volvo-s70-2.5-20v-turbo-193hp-9305
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942	Peugeot Expert Tepee 2007 specifications	https://www.netcarshow.com/peugeot/2007-expert_tepee/
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880	Autogidas Peugeot Expert II Tepee L1 Premium; Auto-Data Citroen Jumpy II Multispace L1 platform twin	https://autogidas.lt/en/auto-katalogas/peugeot/expert/ii-tepee-l1-premium-2007-2011-k67403;https://www.auto-data.net/en/citroen-jumpy-ii-multispace-2.0-16v-140hp-l1-46287
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942	Peugeot Expert Tepee 2007 specifications	https://www.netcarshow.com/peugeot/2007-expert_tepee/
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880	Autogidas Peugeot Expert II Tepee L2 Premium; Auto-Data Citroen Jumpy II Multispace L2 platform twin	https://autogidas.lt/en/auto-katalogas/peugeot/expert/ii-tepee-l2-premium-2007-2011-k67404;https://www.auto-data.net/en/citroen-jumpy-ii-multispace-2.0-16v-140hp-l2-46302
EU-KIA-CERATO-I-FACELIFT-SEDAN-01	4480	1735	1470	CarSpecsGuru Kia Cerato I facelift 1.6 122 hp; Auto.ru Kia Cerato I facelift 1.6 122 hp	https://www.carspecsguru.com/kia/cerato/1528/2332/modification-16016;https://auto.ru/catalog/cars/kia/cerato/2307201/2307202/specifications/2307202_2434128_2434109/
```

## 下一步优先处理

1. 闭合 Peugeot Expert Kasten 的 L1/L2、标准顶和高顶分支。
2. 处理 Mazda BT-50、Toyota Land Cruiser Prado、VW Amarok 的轴距、驾驶室及货斗边界。
3. 处理 Chevrolet Caprice、Corvette、Cadillac Fleetwood、Buick Park Avenue及 Ford Bronco/Expedition。
4. 解决 Passat B2 Sedan、Alfa Romeo 156 Sportwagon、Nissan Qashqai I、Nissan Cabstar/Cedric 等剩余冲突或多分支车型。

推进信号：CONTINUE

[1]: https://www.autodoc.parts/car-parts/engine-electrics-10854/chevrolet/epica/epica-kl1/22591-2-0?utm_source=chatgpt.com "Engine electrics CHEVROLET Epica KL1 2.0 133 hp Petrol ..."
[2]: https://www.carfolio.com/volvo-740-gle-106293?utm_source=chatgpt.com "1983 Volvo 740 GLE: detailed specifications, performance ..."
[3]: https://www.netcarshow.com/peugeot/2007-expert_tepee/?utm_source=chatgpt.com "Peugeot Expert Tepee (2007) - pictures, information & specs"
[4]: https://www.carspecsguru.com/kia/cerato/1528/2332/modification-16016 "Kia Cerato I Facelift 1.6 AT 122 HP specifications and technical data | CarSpecsGuru.com"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 本轮新增闭合 **15 个 Ktype、18 条 READY 映射、16 个尺寸组**。
* Peugeot Expert Kasten 按该 2.0 16V 车型实际存在的 L1H1、L2H1 两种外廓拆分，没有扩展不存在的高顶分支。([汽车数据网][1])
* Buick Park Avenue Ultra 和 Nissan Qashqai I 均因改款导致外廓尺寸变化，分别拆成改款前后两组。([汽车目录][2])
* Volkswagen Passat B2 使用 Volkswagen 官方 notchback sedan 尺寸；Ford Bronco 与 Expedition 的发动机或驱动差异未重复建组。([Volkswagen Newsroom][3])
* 当前仅剩 6 个 Ktype，集中于驾驶室、轴距、宽体或代际边界较复杂的车型。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype 覆盖：94
* READY 映射行：107
* PENDING Ktype：6
* 已确认尺寸组：63
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22570	22570	Sedan	Caprice III	B	4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH	第三代B-body四门轿车外廓。	READY
22572	22572	Convertible	Corvette C4	Y	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH	C4双门敞篷外廓。	READY
22594	22594	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-1986-SEDAN-01	HIGH	1986年后驱Fleetwood Brougham外廓。	READY
22595	22595	Sedan	Brougham	D	4	EU-CADILLAC-BROUGHAM-1989-SEDAN-01	HIGH	输入沿用Fleetwood名称；实际为1989 Cadillac Brougham外廓。	READY
22613	22613	Sedan	Passat B2	32B	4	EU-VOLKSWAGEN-PASSAT-B2-NOTCHBACK-SEDAN-01	HIGH	B2 notchback四门轿车外廓。	READY
22625	22625	Wagon	156 facelift	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	932改款Sportwagon外廓。	READY
22649_prefl	22649	Sedan	Park Avenue I	C	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	MEDIUM	输入生产期跨越外廓调整；改款前分支。	READY
22649_facelift	22649	Sedan	Park Avenue I facelift	C	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越外廓调整；改款后分支。	READY
22693_l1h1	22693	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	MEDIUM	输入未区分车长；L1H1厢式车分支。	READY
22693_l2h1	22693	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	MEDIUM	输入未区分车长；L2H1厢式车分支。	READY
22795	22795	Sedan	Corona T190	AT190	4	EU-TOYOTA-CORONA-T190-SEDAN-01	HIGH	AT190四门轿车外廓。	READY
22865	22865	Sedan	929 IV	HC	4	EU-MAZDA-929-IV-HC-SEDAN-01	HIGH	HC四门轿车外廓。	READY
22931	22931	SUV	Bronco II		3	EU-FORD-USA-BRONCO-II-SUV-01	HIGH	第二代三门全尺寸SUV外廓。	READY
22932	22932	SUV	Bronco II		3	EU-FORD-USA-BRONCO-II-SUV-01	HIGH	第二代三门全尺寸SUV外廓。	READY
22933	22933	SUV	Expedition I	UN93	5	EU-FORD-USA-EXPEDITION-I-SUV-01	HIGH	UN93五门SUV外廓。	READY
22934	22934	SUV	Expedition I	UN93	5	EU-FORD-USA-EXPEDITION-I-SUV-01	HIGH	UN93五门SUV外廓。	READY
22942_prefl	22942	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-J10-SUV-PREFL-01	MEDIUM	输入生产期跨越2010年改款；改款前外廓。	READY
22942_facelift	22942	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-01	MEDIUM	输入生产期跨越2010年改款；改款后外廓。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420	Automobile-Catalog 1981 Chevrolet Caprice Classic Sedan 5.7 Diesel	https://www.automobile-catalog.com/car/1981/1481900/chevrolet_caprice_classic_sedan_5_7l_diesel_v-8.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201	Edmunds 1992 Chevrolet Corvette Convertible specifications	https://www.edmunds.com/chevrolet/corvette/1992/convertible/features-specs/
EU-CADILLAC-FLEETWOOD-BROUGHAM-1986-SEDAN-01	5613	1913	1440	Automobile-Catalog 1986 Cadillac Fleetwood Brougham 5.0	https://www.automobile-catalog.com/car/1986/331985/cadillac_fleetwood_brougham_sedan_5_0l_v-8.html
EU-CADILLAC-BROUGHAM-1989-SEDAN-01	5614	1942	1440	Automobile-Catalog 1989 Cadillac Brougham 5.0 Trailering Package; AutoRestorer 1989 Cadillac Brougham	https://www.automobile-catalog.com/car/1989/332765/cadillac_brougham_5_0l_v-8_trailering_package.html;https://autorestorer.com/articles/1989_cadillac_brougham-1439
EU-VOLKSWAGEN-PASSAT-B2-NOTCHBACK-SEDAN-01	4530	1710	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390	Automobile-Catalog 2005 Alfa Romeo 156 Sportwagon 1.9 JTD 16V	https://www.automobile-catalog.com/car/2005/220535/alfa_romeo_156_sportwagon_1_9_jtd_16v_impression_business__base.html
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400	Automobile-Catalog 1991 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1991/321530/buick_park_avenue_ultra.html
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400	Automobile-Catalog 1995 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1995/322025/buick_park_avenue_ultra.html
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1880	Auto-Data Citroen Jumpy II 2.0 16V L1H1 platform twin	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l1h1-46277
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1880	Auto-Data Citroen Jumpy II 2.0 16V L2H1 platform twin	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l2h1-46313
EU-TOYOTA-CORONA-T190-SEDAN-01	4520	1695	1410	Automobile-Catalog Toyota Corona T190 1600 Select Saloon; AUTODOC Ktype 22795 AT190 identification	https://www.automobile-catalog.com/car/1992/3598835/toyota_corona_1600_select_saloon_5speed.html;https://www.autodoc.co.uk/car-parts/brake-kit-12344/toyota/corona/corona-saloon-1992/22795-1-6-at190
EU-MAZDA-929-IV-HC-SEDAN-01	4885	1705	1425	Automobile-Catalog 1991 Mazda 929 3.0i 167 PS; Automobile-Catalog Mazda 929 IV HC body dimensions	https://www.automobile-catalog.com/car/1991/1638650/mazda_929_3_0i_ssp_glx_cat.html;https://www.automobile-catalog.com/car/1991/60320/mazda_929_2_0i_glx.html
EU-FORD-USA-BRONCO-II-SUV-01	4580	2014	1918	AutoEvolution Ford Bronco 1978-1979 specifications	https://www.autoevolution.com/cars/ford-bronco-1978.html
EU-FORD-USA-EXPEDITION-I-SUV-01	5197	1996	1890	Edmunds 1997 Ford Expedition specifications	https://www.edmunds.com/ford/expedition/1997/features-specs/
EU-NISSAN-QASHQAI-J10-SUV-PREFL-01	4315	1783	1606	Automobile-Catalog 2010 Nissan Qashqai 2.0 dCi 4x4	https://www.automobile-catalog.com/car/2010/2318240/nissan_qashqai_2_0_dci_tekna_4x4.html
EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-01	4330	1780	1615	Auto-Data Nissan Qashqai J10 facelift 2.0 dCi 4x4; Automobile-Catalog 2011 Qashqai J10 4WD	https://www.auto-data.net/en/nissan-qashqai-i-j10-facelift-2010-2.0-dci-150hp-4x4-30021;https://www.automobile-catalog.com/make/nissan/qashqai_1gen/qashqai_j10_2_4wd/2011.html
```

## 下一步优先处理

1. Mazda BT-50：确认 Regular Cab、Freestyle Cab、Double Cab 的完整外廓分支。
2. Toyota Land Cruiser Prado J120：闭合三门、五门以及标准车身、宽体边界。
3. Volkswagen Amarok：确认 Single Cab、Double Cab 是否均由当前 Ktype 覆盖。
4. Nissan Cabstar：核对驾驶室和轴距组合。
5. Nissan Cedric Y30、Y31：分别闭合两个代际轿车尺寸组。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l1h1-46277?utm_source=chatgpt.com "Citroen Jumpy II 2.0 16V (140 Hp) L1H1 | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.automobile-catalog.com/car/1991/321530/buick_park_avenue_ultra.html?utm_source=chatgpt.com "1991 Buick Park Avenue Ultra Specs Review (127 kW ..."
[3]: https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538?utm_source=chatgpt.com "Vehicle data Passat B2 profile"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1401-1500_ktype_dimension_mapping_final.tsv
- all_1401-1500_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 剩余 6 个 Ktype 已全部闭合，新增 10 条映射：Mazda BT-50 按 Single Cab、Freestyle Cab、Double Cab 拆分；Toyota Prado J120 按三门、五门拆分；Volkswagen Amarok 按 Single Cab、Double Cab 拆分；Cabstar F22、Cedric Y30、Cedric Y31 各闭合一条。([Vans][1])
* 修正上一轮 Ford Bronco 的错误代际名称：`Bronco II` 改为 `Bronco second generation`，尺寸组 ID 同步纠正；1978–1979 年第二代 Bronco 的三维保持 4580 × 2014 × 1918 mm。([Ford Motor Company][2])
* 已完成机械检查：映射表 10 列、尺寸组表 6 列；117 个 `id` 唯一；73 个尺寸组唯一；全部外键闭合；无孤立尺寸组；无空尺寸或来源。

## 当前批次进度

* 输入 Ktype：100
* READY Ktype：100
* READY 映射行：117
* PENDING：0
* 最终尺寸组：73
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
22558	22558	SUV	Q7 I	4L	5	EU-AUDI-Q7-4L-SUV-01	HIGH	4L五门SUV外廓。	READY
22559_singlecab	22559	Pickup	BT-50 I	UN	2	EU-MAZDA-BT-50-I-PICKUP-SINGLECAB-01	MEDIUM	输入未区分驾驶室；单排驾驶室外廓。	READY
22559_freestylecab	22559	Pickup	BT-50 I	UN	4	EU-MAZDA-BT-50-I-PICKUP-FREESTYLECAB-01	MEDIUM	输入未区分驾驶室；对开式加长驾驶室外廓。	READY
22559_doublecab	22559	Pickup	BT-50 I	UN	4	EU-MAZDA-BT-50-I-PICKUP-DOUBLECAB-01	MEDIUM	输入未区分驾驶室；双排驾驶室外廓。	READY
22560	22560	MPV	Meriva A		5	EU-OPEL-MERIVA-A-MPV-01	HIGH	Meriva A五门MPV外廓。	READY
22561	22561	Hatchback	Forfour W454	W454	5	EU-SMART-FORFOUR-W454-HATCHBACK-01	HIGH	W454五门掀背外廓。	READY
22562	22562	Convertible	Spider (939)	939	2	EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	HIGH	939双门敞篷外廓。	READY
22570	22570	Sedan	Caprice III	B	4	EU-CHEVROLET-CAPRICE-III-SEDAN-01	HIGH	第三代B-body四门轿车外廓。	READY
22572	22572	Convertible	Corvette C4	Y	2	EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	HIGH	C4双门敞篷外廓。	READY
22576	22576	Hatchback	Sirion M1	M1	5	EU-DAIHATSU-SIRION-M1-HATCHBACK-01	HIGH	M1五门掀背外廓。	READY
22591	22591	Sedan	Epica V200	KL1	4	EU-CHEVROLET-EPICA-V200-SEDAN-01	HIGH	KL1/V200四门轿车；与后续V250车身分开。	READY
22594	22594	Sedan	Fleetwood Brougham	D	4	EU-CADILLAC-FLEETWOOD-BROUGHAM-1986-SEDAN-01	HIGH	1986年后驱Fleetwood Brougham外廓。	READY
22595	22595	Sedan	Brougham	D	4	EU-CADILLAC-BROUGHAM-1989-SEDAN-01	HIGH	输入沿用Fleetwood名称；实际为1989 Cadillac Brougham外廓。	READY
22613	22613	Sedan	Passat B2	32B	4	EU-VOLKSWAGEN-PASSAT-B2-NOTCHBACK-SEDAN-01	HIGH	B2 notchback四门轿车外廓。	READY
22616	22616	Sedan	740		4	EU-VOLVO-740-SEDAN-PREFL-01	HIGH	早期四门轿车外廓。	READY
22618	22618	Sedan	850	LS	4	EU-VOLVO-850-LS-SEDAN-01	MEDIUM	LS四门轿车外廓。	READY
22623	22623	MPV	Gran Move		5	EU-DAIHATSU-GRAN-MOVE-MPV-01	HIGH	1.6升五门MPV外廓。	READY
22625	22625	Wagon	156 facelift	932	5	EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	HIGH	932改款Sportwagon外廓。	READY
22639	22639	Sedan	S80 I		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	MEDIUM	输入版本名含AWD；物理边界按S80 I改款前四门轿车。	READY
22640	22640	Sedan	S60 I		4	EU-VOLVO-S60-I-SEDAN-PREFL-01	HIGH	第一代改款前四门轿车外廓。	READY
22641	22641	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	MEDIUM	AWD版本四门轿车外廓。	READY
22644	22644	Sedan	S70		4	EU-VOLVO-S70-SEDAN-01	MEDIUM	AWD版本四门轿车外廓。	READY
22649_prefl	22649	Sedan	Park Avenue I	C	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	MEDIUM	输入生产期跨越外廓调整；改款前分支。	READY
22649_facelift	22649	Sedan	Park Avenue I facelift	C	4	EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	MEDIUM	输入生产期跨越外廓调整；改款后分支。	READY
22650	22650	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
22651	22651	SUV	CR-V III		5	EU-HONDA-CR-V-III-SUV-01	HIGH	第三代五门SUV外廓。	READY
22652_3dr	22652	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22652_5dr	22652	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22653_3dr	22653	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22653_5dr	22653	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22654_3dr	22654	SUV	Pajero IV		3	EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	MEDIUM	输入未区分门数；拆分三门短轴外廓。	READY
22654_5dr	22654	SUV	Pajero IV		5	EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	MEDIUM	输入未区分门数；拆分五门长轴外廓。	READY
22656	22656	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22657	22657	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22658	22658	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22659	22659	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22660	22660	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22661	22661	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22662	22662	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22663	22663	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22664	22664	Sedan	5 Series E60 LCI	E60	4	EU-BMW-5-E60-LCI-SEDAN-01	HIGH	E60四门轿车外廓。	READY
22665	22665	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22666	22666	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22667	22667	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22668	22668	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22669	22669	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22670	22670	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22671	22671	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22672	22672	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22673	22673	Wagon	5 Series E61 LCI	E61	5	EU-BMW-5-E61-LCI-WAGON-01	HIGH	E61五门旅行车外廓。	READY
22674_3dr	22674	Hatchback	Clio III Phase I		3	EU-RENAULT-CLIO-III-HATCHBACK-3D-01	MEDIUM	输入未区分门数；拆分三门车身。	READY
22674_5dr	22674	Hatchback	Clio III Phase I		5	EU-RENAULT-CLIO-III-HATCHBACK-5D-01	MEDIUM	输入未区分门数；拆分五门车身。	READY
22675	22675	Hatchback	Corsa D	L08	3	EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	HIGH	192 hp OPC仅对应三门性能车身。	READY
22676	22676	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22677	22677	Convertible	Astra H		2	EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	HIGH	TwinTop双门敞篷外廓。	READY
22678	22678	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22679	22679	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22680	22680	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22681_3dr	22681	Hatchback	207		3	EU-PEUGEOT-207-HATCHBACK-3D-01	MEDIUM	输入未区分门数；拆分三门车身。	READY
22681_5dr	22681	Hatchback	207		5	EU-PEUGEOT-207-HATCHBACK-5D-01	MEDIUM	输入未区分门数；拆分五门车身。	READY
22682	22682	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22683	22683	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22684	22684	Convertible	Astra H		2	EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	HIGH	TwinTop双门敞篷外廓。	READY
22685	22685	Hatchback	207		3	EU-PEUGEOT-207-HATCHBACK-3D-01	HIGH	RC版本为三门车身。	READY
22686	22686	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22687	22687	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22688	22688	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22689	22689	Hatchback	Astra H		5	EU-OPEL-ASTRA-H-HATCHBACK-5D-01	HIGH	Astra H五门掀背外廓。	READY
22690	22690	Hatchback	Astra H		3	EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	HIGH	GTC三门掀背外廓。	READY
22691	22691	Wagon	Astra H		5	EU-OPEL-ASTRA-H-WAGON-01	HIGH	Caravan五门旅行车外廓。	READY
22692_l1_standard	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	MEDIUM	输入未区分轴距和车高；L1标准车高分支。	READY
22692_l1_low	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	MEDIUM	输入未区分轴距和车高；L1低车高分支。	READY
22692_l2_standard	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	MEDIUM	输入未区分轴距和车高；L2标准车高分支。	READY
22692_l2_low	22692	MPV	Expert II	G9		EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	MEDIUM	输入未区分轴距和车高；L2低车高分支。	READY
22693_l1h1	22693	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	MEDIUM	输入未区分车长；L1H1厢式车分支。	READY
22693_l2h1	22693	Van	Expert II	G9		EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	MEDIUM	输入未区分车长；L2H1厢式车分支。	READY
22694	22694	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门标准Altea外廓。	READY
22695	22695	MPV	Altea	5P	5	EU-SEAT-ALTEA-5P-MPV-01	HIGH	5P五门标准Altea外廓。	READY
22696	22696	Wagon	M5 E61 LCI	E61	5	EU-BMW-M5-E61-LCI-WAGON-01	HIGH	E61 M5 Touring专用外廓。	READY
22697_3dr	22697	SUV	Land Cruiser Prado J120	J125	3	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	MEDIUM	输入未区分门数；三门短轴外廓。	READY
22697_5dr	22697	SUV	Land Cruiser Prado J120	J120	5	EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	MEDIUM	输入未区分门数；五门长轴外廓。	READY
22698_swb	22698	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距；拆分短轴外廓。	READY
22698_lwb	22698	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距；拆分长轴外廓。	READY
22699_swb	22699	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-SWB-01	MEDIUM	输入未区分轴距；拆分短轴外廓。	READY
22699_lwb	22699	MPV	Hiace IV (Europe)			EU-TOYOTA-HIACE-IV-BUS-LWB-01	MEDIUM	输入未区分轴距；拆分长轴外廓。	READY
22700	22700	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C280-01	HIGH	W204 C 280四门轿车；官方高度与C 350不同。	READY
22701	22701	Sedan	C-Class W204	W204	4	EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C350-01	HIGH	W204 C 350四门轿车；官方高度与C 280不同。	READY
22714	22714	Pickup	Cabstar F22	F22	2	EU-NISSAN-CABSTAR-F22-CHASSISCAB-01	MEDIUM	F22标准单排驾驶室底盘外廓；不含后装上装。	READY
22723	22723	Sedan	Cedric Y30	Y30	4	EU-NISSAN-CEDRIC-Y30-WIDEBODY-SEDAN-01	HIGH	Y30 3.0四门宽体轿车外廓。	READY
22725	22725	Sedan	Cedric Y31	Y31	4	EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	HIGH	Y31四门Hardtop外廓。	READY
22732	22732	Wagon	A4 B8 facelift	8K	5	EU-AUDI-A4-B8-AVANT-WAGON-01	HIGH	B8 Avant五门旅行车外廓。	READY
22740	22740	SUV	Sedici		5	EU-FIAT-SEDICI-SUV-01	HIGH	五门SUV外廓。	READY
22766	22766	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22769	22769	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22795	22795	Sedan	Corona T190	AT190	4	EU-TOYOTA-CORONA-T190-SEDAN-01	HIGH	AT190四门轿车外廓。	READY
22808	22808	Convertible	A5 I facelift	8F7	2	EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	HIGH	8F7双门敞篷外廓。	READY
22826	22826	Coupe	A5 I facelift	8T3	2	EU-AUDI-A5-8T3-FACELIFT-COUPE-01	HIGH	8T3双门轿跑外廓。	READY
22836	22836	Coupe	A5 I facelift	8T3	2	EU-AUDI-A5-8T3-FACELIFT-COUPE-01	HIGH	8T3双门轿跑外廓。	READY
22865	22865	Sedan	929 IV	HC	4	EU-MAZDA-929-IV-HC-SEDAN-01	HIGH	HC四门轿车外廓。	READY
22922	22922	Sedan	Cerato I facelift	LD	4	EU-KIA-CERATO-I-FACELIFT-SEDAN-01	HIGH	LD改款四门轿车外廓。	READY
22928	22928	Sedan	A6 C7	4G	4	EU-AUDI-A6-C7-SEDAN-01	HIGH	C7四门轿车外廓。	READY
22929	22929	Wagon	A6 C7	4G	5	EU-AUDI-A6-C7-AVANT-WAGON-01	HIGH	C7 Avant五门旅行车外廓。	READY
22931	22931	SUV	Bronco second generation		3	EU-FORD-USA-BRONCO-SECOND-GEN-SUV-01	HIGH	1978-1979第二代全尺寸三门SUV外廓。	READY
22932	22932	SUV	Bronco second generation		3	EU-FORD-USA-BRONCO-SECOND-GEN-SUV-01	HIGH	1978-1979第二代全尺寸三门SUV外廓。	READY
22933	22933	SUV	Expedition I	UN93	5	EU-FORD-USA-EXPEDITION-I-SUV-01	HIGH	UN93五门SUV外廓。	READY
22934	22934	SUV	Expedition I	UN93	5	EU-FORD-USA-EXPEDITION-I-SUV-01	HIGH	UN93五门SUV外廓。	READY
22936_singlecab	22936	Pickup	Amarok I	2H	2	EU-VOLKSWAGEN-AMAROK-I-PICKUP-SINGLECAB-01	MEDIUM	输入未区分驾驶室；单排驾驶室外廓。	READY
22936_doublecab	22936	Pickup	Amarok I	2H	4	EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLECAB-01	MEDIUM	输入未区分驾驶室；双排驾驶室外廓。	READY
22939	22939	Coupe	M3 E92	E92	2	EU-BMW-M3-E92-COUPE-01	HIGH	E92双门轿跑外廓。	READY
22940	22940	Wagon	Golf V Variant		5	EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-01	HIGH	五门旅行车外廓。	READY
22941	22941	SUV	Antara A		5	EU-OPEL-ANTARA-A-SUV-01	HIGH	初代五门SUV外廓。	READY
22942_prefl	22942	SUV	Qashqai I	J10	5	EU-NISSAN-QASHQAI-J10-SUV-PREFL-01	MEDIUM	输入生产期跨越2010年改款；改款前外廓。	READY
22942_facelift	22942	SUV	Qashqai I facelift	J10	5	EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-01	MEDIUM	输入生产期跨越2010年改款；改款后外廓。	READY
22944	22944	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22945	22945	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22946	22946	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
22947	22947	Hatchback	Fabia II	5J	5	EU-SKODA-FABIA-II-HATCHBACK-01	HIGH	5J五门掀背外廓。	READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1401-1500_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-Q7-4L-SUV-01	5086	1983	1737	Auto-Data Audi Q7 I Typ 4L 4.2 TDI	https://www.auto-data.net/en/audi-q7-i-typ-4l-4.2-tdi-v8-326hp-quattro-dpf-tiptronic-4858
EU-MAZDA-BT-50-I-PICKUP-SINGLECAB-01	5075	1805	1745	Mazda BT-50 official UK brochure	https://xr793.com/wp-content/uploads/2022/10/2008-Mazda-BT-50-UK.pdf
EU-MAZDA-BT-50-I-PICKUP-FREESTYLECAB-01	5075	1805	1745	EncyCARpedia 2007 Mazda BT-50 XL Cab	https://www.encycarpedia.com/mazda/07-bt-50-xl-cab-pick-up
EU-MAZDA-BT-50-I-PICKUP-DOUBLECAB-01	5075	1805	1755	Mazda BT-50 official UK brochure	https://xr793.com/wp-content/uploads/2022/10/2008-Mazda-BT-50-UK.pdf
EU-OPEL-MERIVA-A-MPV-01	4042	1694	1624	Auto-Data Opel Meriva A 1.3 CDTI	https://www.auto-data.net/en/opel-meriva-a-1.3-cdti-75hp-ecotec-2515
EU-SMART-FORFOUR-W454-HATCHBACK-01	3752	1684	1450	Auto-Data Smart Forfour W454 generation	https://www.auto-data.net/en/smart-forfour-w454-generation-3286
EU-ALFA-ROMEO-SPIDER-939-CONVERTIBLE-01	4393	1830	1318	Alfa Romeo New Spider official UK press material	https://www.media.stellantis.com/uk-en/alfa-romeo/press/new-alfa-spider-on-sale-in-uk
EU-CHEVROLET-CAPRICE-III-SEDAN-01	5387	1913	1420	Automobile-Catalog 1981 Chevrolet Caprice Classic Sedan 5.7 Diesel	https://www.automobile-catalog.com/car/1981/1481900/chevrolet_caprice_classic_sedan_5_7l_diesel_v-8.html
EU-CHEVROLET-CORVETTE-C4-CONVERTIBLE-01	4534	1806	1201	Edmunds 1992 Chevrolet Corvette Convertible specifications	https://www.edmunds.com/chevrolet/corvette/1992/convertible/features-specs/
EU-DAIHATSU-SIRION-M1-HATCHBACK-01	3675	1595	1450	Auto-Data Daihatsu Sirion M1 1.0 i 12V	https://www.auto-data.net/en/daihatsu-sirion-m1-1.0-i-12v-56hp-84
EU-CHEVROLET-EPICA-V200-SEDAN-01	4770	1815	1440	AutoCango 2005 Chevrolet Epica 2.0; AutoZine Daewoo Magnus/Chevrolet Epica	https://www.autocango.com/carspecs-detail/Chevrolet-Epica-XBA4;https://www.autozine.org/Archive/Daewoo/old/Magnus.html
EU-CADILLAC-FLEETWOOD-BROUGHAM-1986-SEDAN-01	5613	1913	1440	Automobile-Catalog 1986 Cadillac Fleetwood Brougham 5.0	https://www.automobile-catalog.com/car/1986/331985/cadillac_fleetwood_brougham_sedan_5_0l_v-8.html
EU-CADILLAC-BROUGHAM-1989-SEDAN-01	5614	1942	1440	Automobile-Catalog 1989 Cadillac Brougham 5.0 Trailering Package; AutoRestorer 1989 Cadillac Brougham	https://www.automobile-catalog.com/car/1989/332765/cadillac_brougham_5_0l_v-8_trailering_package.html;https://autorestorer.com/articles/1989_cadillac_brougham-1439
EU-VOLKSWAGEN-PASSAT-B2-NOTCHBACK-SEDAN-01	4530	1710	1385	Volkswagen Newsroom Passat B2 vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-passat-b2-profile-19538
EU-VOLVO-740-SEDAN-PREFL-01	4785	1760	1430	Carfolio 1983 Volvo 740 GLE	https://www.carfolio.com/volvo-740-gle-106293
EU-VOLVO-850-LS-SEDAN-01	4660	1761	1415	Auto-Data Volvo 850 LS generation	https://www.auto-data.net/en/volvo-850-ls-generation-1928
EU-DAIHATSU-GRAN-MOVE-MPV-01	4100	1640	1600	UltimateSpecs Daihatsu Grand Move 1.6i	https://www.ultimatespecs.com/car-specs/Daihatsu/4839/Daihatsu-Grand-Move-16i.html
EU-ALFA-ROMEO-156-932-FACELIFT-WAGON-01	4441	1743	1390	Automobile-Catalog 2005 Alfa Romeo 156 Sportwagon 1.9 JTD 16V	https://www.automobile-catalog.com/car/2005/220535/alfa_romeo_156_sportwagon_1_9_jtd_16v_impression_business__base.html
EU-VOLVO-S80-I-SEDAN-PREFL-01	4822	1832	1434	Auto-Data Volvo S80 2.4T 200 hp	https://www.auto-data.net/en/volvo-s80-2.4t-200hp-9374
EU-VOLVO-S60-I-SEDAN-PREFL-01	4576	1804	1428	Auto-Data Volvo S60 2.3 T5 20V	https://www.auto-data.net/en/volvo-s60-2.3-t5-20v-250hp-9227
EU-VOLVO-S70-SEDAN-01	4720	1760	1400	Auto-Data Volvo S70 2.5 20V Turbo	https://www.auto-data.net/en/volvo-s70-2.5-20v-turbo-193hp-9305
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-PREFL-01	5215	1869	1400	Automobile-Catalog 1991 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1991/321530/buick_park_avenue_ultra.html
EU-BUICK-PARK-AVENUE-I-ULTRA-SEDAN-FACELIFT-01	5230	1882	1400	Automobile-Catalog 1995 Buick Park Avenue Ultra	https://www.automobile-catalog.com/car/1995/322025/buick_park_avenue_ultra.html
EU-HONDA-CR-V-III-SUV-01	4530	1820	1675	Auto-Data Honda CR-V III 2.0 i-VTEC AWD	https://www.auto-data.net/en/honda-cr-v-iii-2.0-i-vtec-150hp-awd-12335
EU-MITSUBISHI-PAJERO-IV-SUV-3D-01	4385	1875	1870	Auto-Data Mitsubishi Pajero IV 3.8 V6 3-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-3-doors-15485
EU-MITSUBISHI-PAJERO-IV-SUV-5D-01	4900	1875	1870	Auto-Data Mitsubishi Pajero IV 3.8 V6 5-door	https://www.auto-data.net/en/mitsubishi-pajero-iv-3.8-i-v6-24v-mivec-250hp-5-doors-15486
EU-BMW-5-E60-LCI-SEDAN-01	4841	1846	1468	Auto-Data BMW 5 Series E60 LCI 523i	https://www.auto-data.net/en/bmw-5-series-e60-lci-facelift-2007-523i-190hp-27944
EU-BMW-5-E61-LCI-WAGON-01	4843	1846	1491	Auto-Data BMW 5 Series Touring E61 LCI 535d	https://www.auto-data.net/en/bmw-5-series-touring-e61-lci-facelift-2007-535d-286hp-steptronic-28307
EU-RENAULT-CLIO-III-HATCHBACK-3D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 3-door 2.0 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-3-door-2.0-16v-139hp-25243
EU-RENAULT-CLIO-III-HATCHBACK-5D-01	3986	1719	1495	Auto-Data Renault Clio III Phase I 5-door 2.0 16V	https://www.auto-data.net/en/renault-clio-iii-phase-i-5-door-2.0-16v-139hp-56137
EU-OPEL-CORSA-D-HATCHBACK-3D-OPC-01	4040	1713	1488	Auto-Data Opel Corsa D 3-door OPC 192 hp	https://www.auto-data.net/en/opel-corsa-d-3-door-1.6i-16v-opc-192hp-2088
EU-OPEL-ASTRA-H-HATCHBACK-5D-01	4249	1753	1460	Auto-Data Opel Astra H facelift 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-facelift-2007-1.6-turbo-ecotec-180hp-47450
EU-OPEL-ASTRA-H-CONVERTIBLE-TWINTOP-01	4476	1759	1411	Auto-Data Opel Astra H TwinTop 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-twintop-1.6i-16v-turbo-180hp-26337
EU-OPEL-ASTRA-H-WAGON-01	4515	1753	1500	Auto-Data Opel Astra H Caravan facelift 1.6	https://www.auto-data.net/en/opel-astra-h-caravan-facelift-2007-1.6-ecotec-115hp-47461
EU-OPEL-ASTRA-H-HATCHBACK-GTC-3D-01	4290	1753	1435	Auto-Data Opel Astra H GTC facelift 1.6 Turbo	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.6-turbo-ecotec-180hp-47428
EU-PEUGEOT-207-HATCHBACK-3D-01	4030	1720	1472	Auto-Data Peugeot 207 RC 1.6 174 hp	https://www.auto-data.net/en/peugeot-207-rc-1.6-174hp-33994
EU-PEUGEOT-207-HATCHBACK-5D-01	4030	1720	1472	Auto-Data Peugeot 207 1.6 16V 120 hp	https://www.auto-data.net/en/peugeot-207-1.6-i-16v-120hp-automatic-5357
EU-PEUGEOT-EXPERT-II-BUS-L1-STANDARD-01	4805	1895	1942	Peugeot Expert Tepee 2007 specifications	https://www.netcarshow.com/peugeot/2007-expert_tepee/
EU-PEUGEOT-EXPERT-II-BUS-L1-LOW-01	4805	1895	1880	Autogidas Peugeot Expert II Tepee L1 Premium; Auto-Data Citroen Jumpy II Multispace L1 platform twin	https://autogidas.lt/en/auto-katalogas/peugeot/expert/ii-tepee-l1-premium-2007-2011-k67403;https://www.auto-data.net/en/citroen-jumpy-ii-multispace-2.0-16v-140hp-l1-46287
EU-PEUGEOT-EXPERT-II-BUS-L2-STANDARD-01	5135	1895	1942	Peugeot Expert Tepee 2007 specifications	https://www.netcarshow.com/peugeot/2007-expert_tepee/
EU-PEUGEOT-EXPERT-II-BUS-L2-LOW-01	5135	1895	1880	Autogidas Peugeot Expert II Tepee L2 Premium; Auto-Data Citroen Jumpy II Multispace L2 platform twin	https://autogidas.lt/en/auto-katalogas/peugeot/expert/ii-tepee-l2-premium-2007-2011-k67404;https://www.auto-data.net/en/citroen-jumpy-ii-multispace-2.0-16v-140hp-l2-46302
EU-PEUGEOT-EXPERT-II-VAN-L1H1-01	4805	1895	1880	Auto-Data Citroen Jumpy II 2.0 16V L1H1 platform twin	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l1h1-46277
EU-PEUGEOT-EXPERT-II-VAN-L2H1-01	5135	1895	1880	Auto-Data Citroen Jumpy II 2.0 16V L2H1 platform twin	https://www.auto-data.net/en/citroen-jumpy-ii-2.0-16v-140hp-l2h1-46313
EU-SEAT-ALTEA-5P-MPV-01	4282	1768	1576	Auto-Data Seat Altea 5P 1.8 TSI	https://www.auto-data.net/en/seat-altea-5p-1.8-tsi-160hp-dsg-16901
EU-BMW-M5-E61-LCI-WAGON-01	4855	1846	1512	Auto-Data BMW M5 Touring E61 LCI	https://www.auto-data.net/en/bmw-m5-touring-e61-lci-facelift-2007-5.0-v10-507hp-smg-9867
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-3D-01	4340	1875	1865	Toyota Land Cruiser Prado 120 3-door 3.0 D-4D 173 specifications	https://toyota.drive.place/land_cruiser_prado/120-series_res/group_offroad_3d/508171
EU-TOYOTA-LAND-CRUISER-PRADO-J120-SUV-5D-01	4715	1875	1855	Toyota Land Cruiser Prado 120 5-door 3.0 D-4D 173 specifications	https://toyota.drive.place/land_cruiser_prado/120-series_res/group_offroad_5d/508256
EU-TOYOTA-HIACE-IV-BUS-SWB-01	4795	1800	2000	Toyota Hiace 2007 official technical specification	https://media.toyota.co.uk/more-power-new-looks-for-2007-toyota-hiace/
EU-TOYOTA-HIACE-IV-BUS-LWB-01	5240	1800	1995	Toyota Hiace 2007 official technical specification	https://media.toyota.co.uk/more-power-new-looks-for-2007-toyota-hiace/
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C280-01	4581	1770	1444	Mercedes-Benz Public Archive W204 saloons; Mercedes-Benz C-Class 2007 Owner's Manual	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://static.oneweb.mercedes-benz.com/css-oom-assets/en-mt/pdf/mercedes-c-class-sedan-2007-w204-owners-manual-1.pdf
EU-MERCEDES-BENZ-C-CLASS-W204-SEDAN-C350-01	4581	1770	1448	Mercedes-Benz Public Archive W204 saloons; Mercedes-Benz C-Class 2007 Owner's Manual	https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/204-series-C-Class-Saloons-2007---2011.xhtml?oid=453327;https://static.oneweb.mercedes-benz.com/css-oom-assets/en-mt/pdf/mercedes-c-class-sedan-2007-w204-owners-manual-1.pdf
EU-NISSAN-CABSTAR-F22-CHASSISCAB-01	4460	1765	1980	Motor-Car Nissan Cabstar F22; AutoTrader 1988 Nissan Cabstar dimensions	https://motor-car.net/nissan/item/26775-datsun-cabstar-f22;https://www.autotrader.com.au/nissan/cabstar/dimensions/1988
EU-NISSAN-CEDRIC-Y30-WIDEBODY-SEDAN-01	4860	1720	1425	Drive.Place Nissan Cedric VI Y30 3.0 Sedan	https://nissan.drive.place/cedric/vi/group_sedan/183532
EU-NISSAN-CEDRIC-Y31-HARDTOP-SEDAN-01	4690	1720	1425	Auto-Data Nissan Cedric Y31 3.0i V6 160 hp	https://www.auto-data.net/en/nissan-cedric-y31-3.0i-v6-160hp-automatic-25303
EU-AUDI-A4-B8-AVANT-WAGON-01	4699	1826	1436	Auto-Data Audi A4 Avant B8 facelift	https://www.auto-data.net/en/audi-a4-avant-b8-8k-facelift-2011-2.0-tdi-136hp-start-stop-18899
EU-FIAT-SEDICI-SUV-01	4115	1755	1620	Fiat Sedici official price list	https://www.media.stellantis.com/uploads/at/AT/Preislisten/FIAT/Preisliste_Sedici.pdf
EU-AUDI-A5-8F7-FACELIFT-CONVERTIBLE-01	4626	1854	1383	Auto-Data Audi A5 Cabriolet 8F7 facelift	https://www.auto-data.net/en/audi-a5-cabriolet-8f7-facelift-2011-2.0-tdi-143hp-26629
EU-TOYOTA-CORONA-T190-SEDAN-01	4520	1695	1410	Automobile-Catalog Toyota Corona T190 1600 Select Saloon; AUTODOC Ktype 22795 AT190 identification	https://www.automobile-catalog.com/car/1992/3598835/toyota_corona_1600_select_saloon_5speed.html;https://www.autodoc.co.uk/car-parts/brake-kit-12344/toyota/corona/corona-saloon-1992/22795-1-6-at190
EU-AUDI-A5-8T3-FACELIFT-COUPE-01	4626	1854	1372	Auto-Data Audi A5 Coupe 8T3 facelift	https://www.auto-data.net/en/audi-a5-coupe-8t3-facelift-2011-3.0-tfsi-v6-272hp-quattro-s-tronic-19041
EU-MAZDA-929-IV-HC-SEDAN-01	4885	1705	1425	Automobile-Catalog 1991 Mazda 929 3.0i 167 PS; Automobile-Catalog Mazda 929 IV HC body dimensions	https://www.automobile-catalog.com/car/1991/1638650/mazda_929_3_0i_ssp_glx_cat.html;https://www.automobile-catalog.com/car/1991/60320/mazda_929_2_0i_glx.html
EU-KIA-CERATO-I-FACELIFT-SEDAN-01	4480	1735	1470	CarSpecsGuru Kia Cerato I facelift 1.6 122 hp; Auto.ru Kia Cerato I facelift 1.6 122 hp	https://www.carspecsguru.com/kia/cerato/1528/2332/modification-16016;https://auto.ru/catalog/cars/kia/cerato/2307201/2307202/specifications/2307202_2434128_2434109/
EU-AUDI-A6-C7-SEDAN-01	4915	1874	1468	Auto-Data Audi A6 Sedan C7	https://www.auto-data.net/en/audi-a6-limousine-4g-c7-2.0-tdi-136hp-19099
EU-AUDI-A6-C7-AVANT-WAGON-01	4926	1874	1468	Auto-Data Audi A6 Avant C7	https://www.auto-data.net/en/audi-a6-avant-4g-c7-2.0-tfsi-180hp-19103
EU-FORD-USA-BRONCO-SECOND-GEN-SUV-01	4580	2014	1918	AutoEvolution Ford Bronco 1978-1979 specifications	https://www.autoevolution.com/cars/ford-bronco-1978.html
EU-FORD-USA-EXPEDITION-I-SUV-01	5197	1996	1890	Edmunds 1997 Ford Expedition specifications	https://www.edmunds.com/ford/expedition/1997/features-specs/
EU-VOLKSWAGEN-AMAROK-I-PICKUP-SINGLECAB-01	5181	1944	1820	Auto-Data Volkswagen Amarok I Single Cab 2.0 TDI 180 4Motion	https://www.auto-data.net/en/volkswagen-amarok-i-single-cab-2.0-tdi-180hp-4motion-20669
EU-VOLKSWAGEN-AMAROK-I-PICKUP-DOUBLECAB-01	5254	1944	1834	Auto-Data Volkswagen Amarok I Double Cab 2.0 TDI 180 4Motion	https://www.auto-data.net/en/volkswagen-amarok-i-double-cab-2.0-tdi-180hp-automatic-4motion-20562
EU-BMW-M3-E92-COUPE-01	4615	1804	1424	Auto-Data BMW M3 Coupe E92; Auto-Data BMW M3 Coupe E92 LCI	https://www.auto-data.net/en/bmw-m3-coupe-e92-generation-2003;https://www.auto-data.net/en/bmw-m3-coupe-e92-lci-facelift-2010-4.0-v8-420hp-52643
EU-VOLKSWAGEN-GOLF-V-VARIANT-WAGON-01	4556	1781	1504	Auto-Data Volkswagen Golf V Variant 2.0 TDI	https://www.auto-data.net/en/volkswagen-golf-v-variant-2.0-tdi-140hp-8647
EU-OPEL-ANTARA-A-SUV-01	4575	1850	1704	Auto-Data Opel Antara generation	https://www.auto-data.net/en/opel-antara-generation-497
EU-NISSAN-QASHQAI-J10-SUV-PREFL-01	4315	1783	1606	Automobile-Catalog 2010 Nissan Qashqai 2.0 dCi 4x4	https://www.automobile-catalog.com/car/2010/2318240/nissan_qashqai_2_0_dci_tekna_4x4.html
EU-NISSAN-QASHQAI-J10-SUV-FACELIFT-01	4330	1780	1615	Auto-Data Nissan Qashqai J10 facelift 2.0 dCi 4x4; Automobile-Catalog 2011 Qashqai J10 4WD	https://www.auto-data.net/en/nissan-qashqai-i-j10-facelift-2010-2.0-dci-150hp-4x4-30021;https://www.automobile-catalog.com/make/nissan/qashqai_1gen/qashqai_j10_2_4wd/2011.html
EU-SKODA-FABIA-II-HATCHBACK-01	3992	1642	1498	Auto-Data Skoda Fabia II 1.2 HTP	https://www.auto-data.net/en/skoda-fabia-ii-1.2-i-htp-12v-69hp-14130
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1401-1500_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://vans.honestjohn.co.uk/mazda/bt-50/?utm_source=chatgpt.com "Mazda BT-50 (2006 – 2010) Review | Honest John"
[2]: https://www.ford.ca/bronco/history/1978-1979/?utm_source=chatgpt.com "2nd Generation Bronco (1978 - 1979): Bronco Goes Bigger | Ford® Bronco History"


--- 脚本异常 ---
异常: DIMENSION_GROUP EU-RENAULT-CLIO-III-HATCHBACK-3D-01 的 WidthMM 与既有最终值冲突


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1401-1500_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1401-1500_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（2392 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（1249 行）

- 尺寸冲突协调：
  - EU-RENAULT-CLIO-III-HATCHBACK-3D-01 -> EU-RENAULT-CLIO-III-HATCHBACK-3D-02：3986x1707x1495 与 3986x1719x1495，创建新尺寸组
  - EU-RENAULT-CLIO-III-HATCHBACK-5D-01 -> EU-RENAULT-CLIO-III-HATCHBACK-5D-02：3986x1707x1495 与 3986x1719x1495，创建新尺寸组
  - EU-OPEL-ASTRA-H-HATCHBACK-5D-01 -> EU-OPEL-ASTRA-H-HATCHBACK-5D-02：4249x1753x1467 与 4249x1753x1460，复用已有尺寸组
  - EU-PEUGEOT-EXPERT-II-VAN-L1H1-01 -> EU-PEUGEOT-EXPERT-II-VAN-L1H1-02：4805x1895x1942 与 4805x1895x1880，创建新尺寸组
  - EU-PEUGEOT-EXPERT-II-VAN-L2H1-01 -> EU-PEUGEOT-EXPERT-II-VAN-L2H1-02：5135x1895x1942 与 5135x1895x1880，创建新尺寸组
  - EU-OPEL-ANTARA-A-SUV-01 -> EU-OPEL-ANTARA-A-SUV-02：4576x1850x1704 与 4575x1850x1704，创建新尺寸组
