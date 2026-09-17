# 任务：all 第 1301-1400 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0014__0034bb78


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1301-1400 行

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
all 第 1301-1400 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	100	1.8 CAT Quattro	Stufenheck	Allrad	Benzin	66	90	Aug 1985	Nov 1990	2024-03-01	1332
Audi	100	2.2 Quattro	Stufenheck	Allrad	Benzin	101	137	Aug 1984	Dec 1988	2024-03-01	1333
Audi	100	2.2 E Turbo Quattro	Stufenheck	Allrad	Benzin	121	165	Aug 1986	Nov 1990	2024-03-01	1334
Alpina	B3	S Bi-turbo Allrad	Coupe	Allrad	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1335
Audi	100	2.3 E Quattro	Stufenheck	Allrad	Benzin	100	136	Aug 1986	Nov 1990	2024-03-01	1336
Alpina	B3	S Bi-turbo	Cabriolet	Heckantrieb	Benzin	294	400	Apr 2010	May 2013	2024-03-01	1337
Audi	100	2.3 Quattro	Stufenheck	Allrad	Benzin	98	133	Jan 1990	Nov 1990	2024-03-01	1338
Audi	200 c3	2.1 5E	Stufenheck	Frontantrieb	Benzin	100	136	Aug 1983	Jul 1984	2024-03-01	1339
Audi	200 c3	2.1 Turbo	Stufenheck	Frontantrieb	Benzin	134	182	Aug 1983	Jan 1988	2024-03-01	1340
Audi	200 c3	2.2	Stufenheck	Frontantrieb	Benzin	101	137	Aug 1984	Jul 1985	2024-03-01	1341
Audi	200 c3	2.2 Turbo	Stufenheck	Frontantrieb	Benzin	121	165	Aug 1985	Sep 1991	2024-03-01	1342
Ford	Escort v	RS Cosworth 4X4	Schrägheck	Allrad	Benzin	162	220	Oct 1991	Jan 1995	2024-03-01	1343
Audi	200 c3	2.1 Turbo Quattro	Stufenheck	Allrad	Benzin	134	182	Aug 1983	Sep 1986	2024-03-01	1344
Audi	200 c3	2.2 Turbo Quattro	Stufenheck	Allrad	Benzin	121	165	Jan 1985	Dec 1991	2024-03-01	1345
Audi	200 c3	2.2 20V Turbo Quattro	Stufenheck	Allrad	Benzin	162	220	Mar 1989	Dec 1990	2024-03-01	1346
Audi	V8	3.6 Quattro	Stufenheck	Allrad	Benzin	180	245	Apr 1993	Feb 1994	2024-03-01	1347
Audi	V8	3.6 Quattro	Stufenheck	Allrad	Benzin	184	250	Oct 1988	Feb 1994	2024-03-01	1348
Audi	V8	4.2 Quattro	Stufenheck	Allrad	Benzin	206	280	Oct 1991	Feb 1994	2024-03-01	1349
Audi	100	1.9	Coupe	Frontantrieb	Benzin	82	112	Aug 1971	Dec 1976	2024-03-01	1350
Audi	b2	1.8 GT	Coupe	Frontantrieb	Benzin	65	88	Apr 1986	Oct 1988	2024-03-01	1351
Audi	b2	1.8 GT	Coupe	Frontantrieb	Benzin	66	90	Sep 1982	Oct 1988	2024-03-01	1352
Audi	b2	1.8 GT	Coupe	Frontantrieb	Benzin	79	107	Aug 1986	Oct 1987	2024-03-01	1353
Audi	b2	1.9	Coupe	Frontantrieb	Benzin	85	115	Aug 1980	Jul 1983	2024-03-01	1354
Audi	b2	2	Coupe	Frontantrieb	Benzin	85	115	Sep 1983	Jul 1986	2024-03-01	1355
Audi	b2	2.1 GT	Coupe	Frontantrieb	Benzin	96	131	Sep 1982	Oct 1987	2024-03-01	1356
Audi	b2	2.2 GT	Coupe	Frontantrieb	Benzin	85	115	Jul 1981	Oct 1987	2024-03-01	1357
Audi	b2	2.2 GT	Coupe	Frontantrieb	Benzin	100	136	Sep 1984	Oct 1988	2024-03-01	1358
Audi	b2	2.2 Quattro	Coupe	Allrad	Benzin	100	136	Oct 1984	Oct 1988	2024-03-01	1359
Audi	Quattro	2.1 Turbo	Coupe	Allrad	Benzin	147	200	Jul 1980	Jul 1987	2024-03-01	1360
Audi	b3	2.3	Coupe	Frontantrieb	Benzin	100	136	Oct 1988	Jul 1994	2024-03-01	1361
Audi	b3	2	Coupe	Frontantrieb	Benzin	85	115	May 1989	Dec 1996	2024-03-01	1362
Fiat	Balilla 508 saloon	1	Stufenheck	Heckantrieb	Benzin	18	24	Jun 1932	Mar 1934	2024-03-01	1364
Audi	b3	2.0 16 V	Coupe	Frontantrieb	Benzin	103	140	Aug 1992	Dec 1996	2024-03-01	1365
Audi	b3	2.3	Coupe	Frontantrieb	Benzin	98	133	Mar 1990	Dec 1996	2024-03-01	1366
Audi	b3	2.3 20V	Coupe	Frontantrieb	Benzin	123	167	Aug 1990	Jul 1991	2024-03-01	1368
Audi	b3	2.6	Coupe	Frontantrieb	Benzin	110	150	Aug 1992	Dec 1996	2024-03-01	1369
Audi	b3	2.8	Coupe	Frontantrieb	Benzin	128	174	Sep 1991	Dec 1996	2024-03-01	1370
Audi	b3	2.3 Quattro	Coupe	Allrad	Benzin	100	136	Nov 1988	Dec 1992	2024-03-01	1371
Audi	b3	2.3 20V Quattro	Coupe	Allrad	Benzin	125	170	Nov 1988	Jul 1991	2024-03-01	1372
Audi	b3	S2 Quattro	Coupe	Allrad	Benzin	162	220	Sep 1990	Sep 1992	2024-03-01	1373
Audi	b3	S2 Quattro	Coupe	Allrad	Benzin	169	230	Oct 1992	Dec 1996	2024-03-01	1374
Audi	b3	2.3 Quattro	Coupe	Allrad	Benzin	98	134	May 1990	Dec 1996	2024-03-01	1375
Audi	b3	2.3 20V Quattro	Coupe	Allrad	Benzin	123	167	May 1990	Dec 1996	2024-03-01	1376
Audi	b3	2.6 Quattro	Coupe	Allrad	Benzin	110	150	Aug 1992	Dec 1996	2024-03-01	1377
Audi	b3	2.8 Quattro	Coupe	Allrad	Benzin	128	174	Aug 1991	Dec 1996	2024-03-01	1378
Audi	100	2.4 D	Stufenheck	Frontantrieb	Diesel	60	82	Dec 1990	Jul 1994	2024-03-01	1379
Audi	100	2.5 TDI	Stufenheck	Frontantrieb	Diesel	85	115	Dec 1990	Jul 1994	2024-03-01	1380
Audi	100	2	Stufenheck	Frontantrieb	Benzin	74	100	Dec 1990	Jul 1994	2024-03-01	1381
Ford	Escort iii	1.1	Schrägheck	Frontantrieb	Benzin	43	59	Sep 1980	Aug 1983	2024-03-01	1382
Audi	100	2.0 E	Stufenheck	Frontantrieb	Benzin	85	115	Dec 1990	Jul 1994	2024-03-01	1383
Audi	100	2.3 E	Stufenheck	Frontantrieb	Benzin	98	133	Dec 1990	Jul 1994	2024-03-01	1384
Audi	100	2.6	Stufenheck	Frontantrieb	Benzin	110	150	Mar 1992	Jul 1994	2024-03-01	1385
Audi	100	2.8 E	Stufenheck	Frontantrieb	Benzin	128	174	Dec 1990	Jul 1994	2024-03-01	1386
Audi	100	S4 Turbo Quattro	Stufenheck	Allrad	Benzin	169	230	Aug 1991	Jul 1994	2024-03-01	1387
Audi	100	2.3 E Quattro	Stufenheck	Allrad	Benzin	98	133	Dec 1990	Jul 1994	2024-03-01	1388
Audi	100	2.6 Quattro	Stufenheck	Allrad	Benzin	110	150	Apr 1992	Jul 1994	2024-03-01	1389
Audi	100	2.8 E Quattro	Stufenheck	Allrad	Benzin	128	174	Dec 1990	Jul 1994	2024-03-01	1390
Ford	Escort iii	1.3	Schrägheck	Frontantrieb	Benzin	51	69	Sep 1980	Dec 1985	2024-03-01	1391
Audi	80	1.9 TD	Stufenheck	Frontantrieb	Diesel	55	75	Sep 1991	Dec 1994	2024-03-01	1392
Audi	80	1.9 TDI	Stufenheck	Frontantrieb	Diesel	66	90	Sep 1991	Dec 1994	2024-03-01	1393
Audi	80	1.6	Stufenheck	Frontantrieb	Benzin	52	71	Sep 1991	Dec 1994	2024-03-01	1394
Audi	80	1.6 E	Stufenheck	Frontantrieb	Benzin	74	101	Jun 1993	Dec 1994	2024-03-01	1395
Audi	80	2	Stufenheck	Frontantrieb	Benzin	66	90	Sep 1991	Dec 1994	2024-03-01	1396
Audi	80	2.0 E	Stufenheck	Frontantrieb	Benzin	85	115	Sep 1991	Dec 1994	2024-03-01	1397
Audi	80	2.0 E 16V	Stufenheck	Frontantrieb	Benzin	103	140	Aug 1992	Dec 1994	2024-03-01	1398
Audi	80	2.3 E	Stufenheck	Frontantrieb	Benzin	98	133	Sep 1991	Dec 1994	2024-03-01	1399
Audi	80	2.6	Stufenheck	Frontantrieb	Benzin	110	150	Jul 1992	Dec 1994	2024-03-01	1400
Audi	80	2.8	Stufenheck	Frontantrieb	Benzin	128	174	Sep 1991	Dec 1994	2024-03-01	1401
Ford	Escort iii	1.6	Schrägheck	Frontantrieb	Benzin	58	79	Sep 1980	Dec 1985	2024-03-01	1402
Ford	Escort iii	1.6	Schrägheck	Frontantrieb	Benzin	71	97	Sep 1980	Oct 1982	2024-03-01	1403
Audi	80	2.0 E 16V Quattro	Stufenheck	Allrad	Benzin	103	140	Apr 1992	Dec 1994	2024-03-01	1404
Ford	Escort iii	1.6 Xr3i	Schrägheck	Frontantrieb	Benzin	77	105	Oct 1982	Dec 1985	2024-03-01	1405
Ford	Escort iii	1.6 RS Turbo	Schrägheck	Frontantrieb	Benzin	97	132	Nov 1984	Dec 1985	2024-03-01	1406
Ford	Escort iii	1.6 D	Schrägheck	Frontantrieb	Diesel	40	54	Feb 1984	Dec 1985	2024-03-01	1407
Alpina	B7	Biturbo Allrad	Stufenheck	Allrad	Benzin	373	507	Sep 2010	Jun 2012	2024-03-01	1408
Audi	80	2.0 E Quattro	Stufenheck	Allrad	Benzin	85	115	Sep 1991	Dec 1994	2024-03-01	1409
Audi	80	S2 Quattro	Stufenheck	Allrad	Benzin	169	230	Feb 1993	Dec 1994	2024-03-01	1410
Audi	80	2.3 E Quattro	Stufenheck	Allrad	Benzin	98	133	Sep 1991	Dec 1994	2024-03-01	1411
Ford	Escort iii	1.3	Cabriolet	Frontantrieb	Benzin	51	69	Sep 1983	Dec 1985	2024-03-01	1412
Audi	80	2.6 Quattro	Stufenheck	Allrad	Benzin	110	150	Jun 1992	Dec 1994	2024-03-01	1413
Audi	80	2.8 Quattro	Stufenheck	Allrad	Benzin	128	174	Sep 1991	Dec 1994	2024-03-01	1414
Audi	100	1.8	Kombi	Frontantrieb	Benzin	55	75	Aug 1982	Dec 1987	2024-03-01	1415
Ford	Escort iii	1.6	Cabriolet	Frontantrieb	Benzin	58	79	Sep 1983	Dec 1985	2024-03-01	1416
Audi	100	1.8	Kombi	Frontantrieb	Benzin	65	88	Feb 1986	Jul 1990	2024-03-01	1417
Audi	100	1.8	Kombi	Frontantrieb	Benzin	66	90	Aug 1983	Jul 1989	2024-03-01	1418
Audi	100	2	Kombi	Frontantrieb	Benzin	83	113	Sep 1986	Nov 1987	2024-03-01	1419
Audi	100	2.0 E CAT	Kombi	Frontantrieb	Benzin	85	115	Jan 1988	Nov 1990	2024-03-01	1420
Audi	100	2.1	Kombi	Frontantrieb	Benzin	100	136	Aug 1982	Jul 1984	2024-03-01	1421
Audi	100	2.2	Kombi	Frontantrieb	Benzin	85	115	Oct 1984	Sep 1986	2024-03-01	1422
Audi	100	2.2	Kombi	Frontantrieb	Benzin	101	137	Aug 1984	Dec 1988	2024-03-01	1423
Audi	100	2.2 Turbo	Kombi	Frontantrieb	Benzin	121	165	Aug 1986	Nov 1990	2024-03-01	1424
Audi	100	2.3	Kombi	Frontantrieb	Benzin	100	136	Aug 1986	Nov 1990	2024-03-01	1425
Audi	100	2.0 D	Kombi	Frontantrieb	Diesel	51	70	Mar 1983	Nov 1990	2024-03-01	1426
Audi	100	2.0 TD	Kombi	Frontantrieb	Diesel	64	87	Mar 1983	Oct 1987	2024-03-01	1427
Audi	100	2.0 TD	Kombi	Frontantrieb	Diesel	74	100	Mar 1988	Nov 1990	2024-03-01	1428
Audi	100	2.5 TDI	Kombi	Frontantrieb	Diesel	88	120	Jan 1990	Nov 1990	2024-03-01	1429
Audi	100	2.3	Kombi	Frontantrieb	Benzin	98	133	Mar 1990	Nov 1990	2024-03-01	1430
Alpina	D3	2.0 Bi-turbo	Stufenheck	Heckantrieb	Diesel	157	214	Jul 2008	May 2013	2024-03-01	1431
Ford	Escort iii	1.6 I	Cabriolet	Frontantrieb	Benzin	77	105	Sep 1983	Dec 1985	2024-03-01	1432
Audi	100	1.6	Kombi	Frontantrieb	Benzin	63	85	Jul 1977	Feb 1983	2024-03-01	1433


--- Round 1 / 首次发送 ---
## 更新点

* 完成首轮物理外廓聚类，闭合 **14 个 DIMENSION_GROUP**。
* 已确认并批量复用 Audi 100 C3、Audi V8 D11、Audi Coupe B2/B3/B4、Audi Quattro、Audi S2、Audi 80 B4、Audi 100 C3 Avant、Ford Escort RS Cosworth 与 Escort III Cabriolet 尺寸组。Audi 100 C3 轿车改款前后高度分别为 1422/1421 mm；Avant 改款前后外廓尺寸一致。([汽车数据网][1])
* Audi Coupe B2 改款造成车长变化，B3/B4 外廓也发生明显变化；对应跨期 Ktype 已拆成稳定派生行。([汽车数据网][2])
* Ford Escort RS Cosworth 与 Escort III Cabriolet 已取得明确的不含后视镜宽度三维。([汽车目录][3])
* Audi 80 B4 标准轿车与 S2 轿车使用不同车高尺寸组。([汽车数据网][4])

## 当前批次进度

* 输入 Ktype：**100**
* READY Ktype：**68/100**
* PENDING Ktype：**32/100**
* READY 映射行：**82**
* PENDING 映射行：**32**
* 当前映射行总数：**114**
* 已确认尺寸组：**14**
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1332_prefl	1332	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1332_facelift	1332	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1333_prefl	1333	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1333_facelift	1333	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1334_prefl	1334	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1334_facelift	1334	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1335	1335	Coupe	Alpina B3 S Bi-Turbo E92	E92	2		MEDIUM	E92双门轿跑边界明确；ALPINA外部套件的完整三维尚未闭合。	PENDING: ALPINA外部套件三维及不含镜宽度待闭合
1336_prefl	1336	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1336_facelift	1336	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1337	1337	Convertible	Alpina B3 S Bi-Turbo E93	E93	2		MEDIUM	E93硬顶敞篷边界明确；ALPINA外部套件的完整三维尚未闭合。	PENDING: ALPINA外部套件三维及不含镜宽度待闭合
1338	1338	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH		READY
1339	1339	Sedan	Audi 200 C3	44	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1340	1340	Sedan	Audi 200 C3	44	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1341	1341	Sedan	Audi 200 C3	44	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1342	1342	Sedan	Audi 200 C3	44	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1343	1343	Hatchback	Ford Escort V RS Cosworth		3	EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	HIGH	RS Cosworth三门宽体外廓。	READY
1344	1344	Sedan	Audi 200 C3	44Q	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1345	1345	Sedan	Audi 200 C3	44Q	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1346	1346	Sedan	Audi 200 C3 facelift	44Q	4		MEDIUM	早期与后期车长资料尚未完成改款边界归因。	PENDING: 改款前后外廓及来源冲突待闭合
1347	1347	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1348	1348	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1349	1349	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1350	1350	Coupe	Audi 100 Coupe S C1	F105	2		LOW	同一车型的直接资料在车长与车高上存在未解决冲突。	PENDING: 三维来源冲突待闭合
1351	1351	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	改款后前驱双门轿跑。	READY
1352_prefl	1352	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1352_facelift	1352	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1353	1353	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH		READY
1354	1354	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH		READY
1355_prefl	1355	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1355_facelift	1355	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1356_prefl	1356	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1356_facelift	1356	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1357_prefl	1357	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1357_facelift	1357	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1358	1358	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH		READY
1359	1359	Coupe	Audi Coupe B2 facelift	85	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	quattro车身代码85；外廓与同改款轿跑组一致。	READY
1360	1360	Coupe	Audi Quattro Typ 85	85	3	EU-AUDI-QUATTRO-TYP85-COUPE-01	HIGH	Ur-quattro标准轴距三门外廓。	READY
1361_b3	1361	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1361_b4	1361	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1362_b3	1362	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1362_b4	1362	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1364	1364	Sedan	Fiat 508A Balilla	508A	2		MEDIUM	早期两门Saloon边界基本明确，仍缺可直接支撑完整三维与宽度口径的强来源。	PENDING: 完整三维及不含镜宽度来源待闭合
1365	1365	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1366_b3	1366	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1366_b4	1366	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1368	1368	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH		READY
1369	1369	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1370	1370	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1371_b3	1371	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1371_b4	1371	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1372	1372	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH		READY
1373	1373	Coupe	Audi S2 Coupe	8B	3	EU-AUDI-S2-COUPE-8B-01	HIGH	S2专用外廓。	READY
1374	1374	Coupe	Audi S2 Coupe	8B	3	EU-AUDI-S2-COUPE-8B-01	HIGH	S2专用外廓。	READY
1375_b3	1375	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1375_b4	1375	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1376_b3	1376	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1376_b4	1376	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1377	1377	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1378	1378	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1379	1379	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1380	1380	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1381	1381	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1382	1382	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1383	1383	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1384	1384	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1385	1385	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1386	1386	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1387	1387	Sedan	Audi S4 C4	4A	4		MEDIUM	S4宽体边界已确认，轿车高度的直接来源异常尚未排除。	PENDING: S4轿车完整三维来源待闭合
1388	1388	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1389	1389	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1390	1390	Sedan	Audi 100 C4	4A	4		MEDIUM	同代不同动力资料存在未解决的车高差异，候选尺寸组暂不落盘。	PENDING: 车高差异的悬架与轮胎边界待闭合
1391	1391	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1392	1392	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1393	1393	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1394	1394	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1395	1395	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1396	1396	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1397	1397	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1398	1398	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1399	1399	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1400	1400	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1401	1401	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1402	1402	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1403	1403	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1404	1404	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1405	1405	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1406	1406	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1407	1407	Hatchback	Ford Escort III				LOW	输入未区分三门/五门及具体车身代码，物理边界尚不能唯一落盘。	PENDING: 门数与车身代码边界待确认
1408	1408	Sedan	Alpina B7 Bi-Turbo F01	F01	4		MEDIUM	标准轴距F01边界明确；ALPINA外部套件及四驱车高的完整三维尚未闭合。	PENDING: ALPINA专属外廓三维待闭合
1409	1409	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1410	1410	Sedan	Audi S2 B4	8C	4	EU-AUDI-S2-B4-SEDAN-01	HIGH	S2轿车专用低车高外廓。	READY
1411	1411	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1412	1412	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1413	1413	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1414	1414	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1415	1415	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1416	1416	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1417	1417	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1418	1418	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1419	1419	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1420	1420	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1421	1421	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1422	1422	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1423	1423	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1424	1424	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1425	1425	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1426	1426	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1427	1427	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1428	1428	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1429	1429	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1430	1430	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1431	1431	Sedan	Alpina D3 Bi-Turbo E90	E90	4		MEDIUM	E90轿车边界明确；ALPINA前后包围及悬架车高的完整三维尚未闭合。	PENDING: ALPINA专属外廓三维待闭合
1432	1432	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1433	1433	Wagon	Audi 100 C2 Avant	43	5		MEDIUM	生产区间跨C2改款，改款前后旅行车外廓边界尚未闭合。	PENDING: C2 Avant改款前后外廓待闭合
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-generation-1060
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421	Auto-Data	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-facelift-1988-generation-5184
EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	4211	1738	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/947090/ford_escort_rs_cosworth.html
EU-AUDI-V8-D11-SEDAN-01	4874	1814	1420	Auto-Data	https://www.auto-data.net/en/audi-v8-d11-generation-1148
EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	4421	1682	1350	Auto-Data	https://www.auto-data.net/en/audi-coupe-b2-81-85-facelift-1984-generation-5225
EU-AUDI-COUPE-B2-COUPE-PREFL-01	4349	1682	1350	Auto-Data	https://www.auto-data.net/en/audi-coupe-b2-81-85-generation-1091
EU-AUDI-QUATTRO-TYP85-COUPE-01	4404	1723	1344	Auto-Data	https://www.auto-data.net/en/audi-quattro-typ-85-2.1-turbo-200hp-4902
EU-AUDI-COUPE-B3-COUPE-01	4470	1716	1380	Auto-Data	https://www.auto-data.net/en/audi-coupe-b3-89-generation-1090
EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	4366	1716	1375	Auto-Data	https://www.auto-data.net/en/audi-coupe-b4-8c-2.8-v6-e-174hp-4476
EU-AUDI-S2-COUPE-8B-01	4401	1716	1375	Auto-Data	https://www.auto-data.net/en/audi-s2-model-518
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406	Auto-Data	https://www.auto-data.net/en/audi-80-b4-typ-8c-generation-1110
EU-AUDI-S2-B4-SEDAN-01	4509	1695	1386	Auto-Data	https://www.auto-data.net/en/audi-s2-generation-5230
EU-FORD-ESCORT-III-CONVERTIBLE-01	4010	1640	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/30260/ford_escort_cabriolet_1_3.html
EU-AUDI-100-C3-AVANT-01	4793	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-100-avant-c3-typ-44-44q-facelift-1988-generation-5183
```

## 下一步优先处理

1. 优先闭合 Audi 100 C4 普通轿车与 S4 C4 的车高差异，批量解决 Ktype 1379–1390。
2. 核定 Audi 200 C3 改款前后车长边界，处理 Ktype 1339–1346。
3. 确认 Ford Escort III 掀背 Ktype 是否同时覆盖三门和五门，并补齐相应车身代码。
4. 补齐 Alpina B3 S、B7、D3 的 ALPINA 专属前后包围及悬架状态三维。
5. 最后处理 Audi 100 Coupe S C1、Fiat 508A Balilla 与 Audi 100 C2 Avant 的历史来源冲突。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/audi-100-c3-typ-44-44q-generation-1060?utm_source=chatgpt.com "Audi 100 (C3, Typ 44,44Q) | Technical Specs, Fuel ..."
[2]: https://www.auto-data.net/en/audi-coupe-model-502?utm_source=chatgpt.com "Audi Coupe | Technical Specs, Fuel consumption, Dimensions"
[3]: https://www.automobile-catalog.com/car/1992/947090/ford_escort_rs_cosworth.html?utm_source=chatgpt.com "1992 Ford Escort RS Cosworth Specs Review (162 kW / 220 PS / 217 hp) (since mid-year 1992 for Europe Germany)"
[4]: https://www.auto-data.net/en/audi-80-b4-typ-8c-generation-1110?utm_source=chatgpt.com "Audi 80 (B4, Typ 8C) | Technical Specs, Fuel consumption, Dimensions"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_1301-1400_ktype_dimension_mapping_final.tsv
- all_1301-1400_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 已闭合上一轮剩余的 32 个 PENDING，新增 Audi 200 C3 三种外廓、Audi 100 C4 前驱/Quattro、Audi S4 C4、Ford Escort III 三门/五门、四个 Alpina 外廓以及三款历史车型尺寸组。([汽车数据网][1])
* Ford Escort III 普通掀背按 Ktype 实际覆盖范围拆为三门和五门；XR3、XR3i、RS Turbo 保持三门分支。([www.valeoservice.com][2])
* Alpina B3 S E92/E93、B7 F01 与 D3 E90 已分别建立独立尺寸组。([AutoGral][3])
* 已完成轻量机械检查：固定表头正确、120 个 `id` 唯一、29 个尺寸组唯一、全部映射引用闭合、无孤立尺寸组、三维和来源均非空。

## 当前批次进度

* 输入 Ktype：**100/100**
* READY Ktype：**100/100**
* READY 映射行：**120**
* PENDING 映射行：**0**
* DIMENSION_GROUP：**29**
* 当前批次已完成。

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
1332_prefl	1332	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1332_facelift	1332	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1333_prefl	1333	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1333_facelift	1333	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1334_prefl	1334	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1334_facelift	1334	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1335	1335	Coupe	Alpina B3 S Bi-Turbo E92	E92	2	EU-ALPINA-B3S-E92-COUPE-AWD-01	HIGH	E92双门四驱外廓。	READY
1336_prefl	1336	Sedan	Audi 100 C3	44Q	4	EU-AUDI-100-C3-SEDAN-PREFL-01	HIGH	跨1988改款，按改款前物理外廓拆分。	READY
1336_facelift	1336	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH	跨1988改款，按改款后物理外廓拆分。	READY
1337	1337	Convertible	Alpina B3 S Bi-Turbo E93	E93	2	EU-ALPINA-B3S-E93-CONVERTIBLE-01	HIGH	E93硬顶敞篷外廓。	READY
1338	1338	Sedan	Audi 100 C3 facelift	44Q	4	EU-AUDI-100-C3-SEDAN-FACELIFT-01	HIGH		READY
1339	1339	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH		READY
1340	1340	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH		READY
1341	1341	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH		READY
1342_prefl	1342	Sedan	Audi 200 C3	44	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH	生产区间跨1988改款，按改款前外廓拆分。	READY
1342_facelift	1342	Sedan	Audi 200 C3 facelift	44	4	EU-AUDI-200-C3-SEDAN-FACELIFT-01	HIGH	生产区间跨1988改款，按改款后外廓拆分。	READY
1343	1343	Hatchback	Ford Escort V RS Cosworth		3	EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	HIGH	RS Cosworth三门宽体外廓。	READY
1344	1344	Sedan	Audi 200 C3	44Q	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH		READY
1345_prefl	1345	Sedan	Audi 200 C3	44Q	4	EU-AUDI-200-C3-SEDAN-PREFL-01	HIGH	生产区间跨1988改款，按改款前外廓拆分。	READY
1345_facelift	1345	Sedan	Audi 200 C3 facelift	44Q	4	EU-AUDI-200-C3-SEDAN-FACELIFT-01	HIGH	生产区间跨1988改款，按改款后外廓拆分。	READY
1346	1346	Sedan	Audi 200 C3 20V	44Q	4	EU-AUDI-200-C3-20V-SEDAN-01	HIGH	20V专用加长外廓。	READY
1347	1347	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1348	1348	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1349	1349	Sedan	Audi V8 D11	D11	4	EU-AUDI-V8-D11-SEDAN-01	HIGH		READY
1350	1350	Coupe	Audi 100 Coupe S C1	F105	2	EU-AUDI-100-C1-COUPE-01	HIGH		READY
1351	1351	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	改款后前驱双门轿跑。	READY
1352_prefl	1352	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1352_facelift	1352	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1353	1353	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH		READY
1354	1354	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH		READY
1355_prefl	1355	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1355_facelift	1355	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1356_prefl	1356	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1356_facelift	1356	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1357_prefl	1357	Coupe	Audi Coupe B2	81	3	EU-AUDI-COUPE-B2-COUPE-PREFL-01	HIGH	生产区间跨1984改款，按改款前外廓拆分。	READY
1357_facelift	1357	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	生产区间跨1984改款，按改款后外廓拆分。	READY
1358	1358	Coupe	Audi Coupe B2 facelift	81	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH		READY
1359	1359	Coupe	Audi Coupe B2 facelift	85	3	EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	HIGH	quattro车身代码85；外廓与同改款轿跑组一致。	READY
1360	1360	Coupe	Audi Quattro Typ 85	85	3	EU-AUDI-QUATTRO-TYP85-COUPE-01	HIGH	Ur-quattro标准轴距三门外廓。	READY
1361_b3	1361	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1361_b4	1361	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1362_b3	1362	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1362_b4	1362	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1364	1364	Sedan	Fiat 508A Balilla	508A	2	EU-FIAT-508A-BALILLA-SEDAN-01	HIGH	508A两门Berlina外廓。	READY
1365	1365	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1366_b3	1366	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1366_b4	1366	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1368	1368	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH		READY
1369	1369	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1370	1370	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1371_b3	1371	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1371_b4	1371	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1372	1372	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH		READY
1373	1373	Coupe	Audi S2 Coupe	8B	3	EU-AUDI-S2-COUPE-8B-01	HIGH	S2专用外廓。	READY
1374	1374	Coupe	Audi S2 Coupe	8B	3	EU-AUDI-S2-COUPE-8B-01	HIGH	S2专用外廓。	READY
1375_b3	1375	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1375_b4	1375	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1376_b3	1376	Coupe	Audi Coupe B3	8B	3	EU-AUDI-COUPE-B3-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B3拆分。	READY
1376_b4	1376	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH	生产区间跨B3/B4外廓变更，按B4拆分。	READY
1377	1377	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1378	1378	Coupe	Audi Coupe B4 facelift	8B	3	EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	HIGH		READY
1379	1379	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1380	1380	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1381	1381	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1382_3dr	1382	Hatchback	Ford Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1382_5dr	1382	Hatchback	Ford Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-5D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1383	1383	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1384	1384	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1385	1385	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1386	1386	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-FWD-01	HIGH		READY
1387	1387	Sedan	Audi S4 C4	4A	4	EU-AUDI-S4-C4-SEDAN-01	HIGH	S4宽体轿车外廓。	READY
1388	1388	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-QUATTRO-01	HIGH	quattro车高外廓。	READY
1389	1389	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-QUATTRO-01	HIGH	quattro车高外廓。	READY
1390	1390	Sedan	Audi 100 C4	4A	4	EU-AUDI-100-C4-SEDAN-QUATTRO-01	HIGH	quattro车高外廓。	READY
1391_3dr	1391	Hatchback	Ford Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1391_5dr	1391	Hatchback	Ford Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-5D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1392	1392	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1393	1393	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1394	1394	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1395	1395	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1396	1396	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1397	1397	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1398	1398	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1399	1399	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1400	1400	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1401	1401	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1402_3dr	1402	Hatchback	Ford Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1402_5dr	1402	Hatchback	Ford Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-5D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1403	1403	Hatchback	Ford Escort III XR3	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	71 kW版本为XR3三门外廓。	READY
1404	1404	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1405	1405	Hatchback	Ford Escort III XR3i	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	XR3i三门外廓。	READY
1406	1406	Hatchback	Ford Escort III RS Turbo	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	RS Turbo三门外廓。	READY
1407_3dr	1407	Hatchback	Ford Escort III	GAA	3	EU-FORD-ESCORT-III-HATCHBACK-3D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1407_5dr	1407	Hatchback	Ford Escort III	GAA	5	EU-FORD-ESCORT-III-HATCHBACK-5D-01	HIGH	GAA Ktype覆盖三门/五门，按门数拆分。	READY
1408	1408	Sedan	Alpina B7 Bi-Turbo F01	F01	4	EU-ALPINA-B7-F01-SEDAN-AWD-01	HIGH	F01标准轴距四驱外廓。	READY
1409	1409	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1410	1410	Sedan	Audi S2 B4	8C	4	EU-AUDI-S2-B4-SEDAN-01	HIGH	S2轿车专用低车高外廓。	READY
1411	1411	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1412	1412	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1413	1413	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1414	1414	Sedan	Audi 80 B4	8C	4	EU-AUDI-80-B4-SEDAN-01	HIGH		READY
1415	1415	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1416	1416	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1417	1417	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1418	1418	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1419	1419	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1420	1420	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1421	1421	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1422	1422	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1423	1423	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1424	1424	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1425	1425	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1426	1426	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1427	1427	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1428	1428	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1429	1429	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1430	1430	Wagon	Audi 100 C3 Avant	44	5	EU-AUDI-100-C3-AVANT-01	HIGH	改款前后旅行车外廓尺寸一致，复用同一尺寸组。	READY
1431	1431	Sedan	Alpina D3 Bi-Turbo E90	E90	4	EU-ALPINA-D3-E90-SEDAN-01	HIGH	E90轿车外廓。	READY
1432	1432	Convertible	Ford Escort III Cabriolet	ALD	2	EU-FORD-ESCORT-III-CONVERTIBLE-01	MEDIUM	两门Cabriolet车身代码ALD。	READY
1433	1433	Wagon	Audi 100 C2 Avant	43	5	EU-AUDI-100-C2-AVANT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_1301-1400_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-100-C3-SEDAN-PREFL-01	4793	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-generation-1060
EU-AUDI-100-C3-SEDAN-FACELIFT-01	4793	1814	1421	Auto-Data	https://www.auto-data.net/en/audi-100-c3-typ-44-44q-facelift-1988-generation-5184
EU-ALPINA-B3S-E92-COUPE-AWD-01	4622	1782	1410	Autogral	https://autogral.com/alpina-b3-s-bi-turbo-coupe-awd-switch-tronic-000272-versus-bmw-320i-coupe-002707_uk.html
EU-ALPINA-B3S-E93-CONVERTIBLE-01	4623	1782	1385	Autogral	https://autogral.com/alpina-b3-s-bi-turbo-convertible-switch-tronic-000248-versus-audi-a5-convertible-45-tfsi-001382_uk.html
EU-AUDI-200-C3-SEDAN-PREFL-01	4807	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-200-c3-typ-44-44q-2.2-turbo-165hp-4272
EU-AUDI-200-C3-SEDAN-FACELIFT-01	4793	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-200-c3-typ-44-44q-2.2-turbo-200hp-4274
EU-FORD-ESCORT-V-RS-COSWORTH-HATCHBACK-01	4211	1738	1425	Automobile-Catalog	https://www.automobile-catalog.com/car/1992/947090/ford_escort_rs_cosworth.html
EU-AUDI-200-C3-20V-SEDAN-01	4913	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-200-c3-typ-44-44q-2.2-20v-220hp-quattro-4271
EU-AUDI-V8-D11-SEDAN-01	4874	1814	1420	Auto-Data	https://www.auto-data.net/en/audi-v8-d11-generation-1148
EU-AUDI-100-C1-COUPE-01	4398	1750	1340	Automobile-Catalog	https://www.automobile-catalog.com/car/1974/74750/audi_100_coupe_s.html
EU-AUDI-COUPE-B2-COUPE-FACELIFT-01	4421	1682	1350	Auto-Data	https://www.auto-data.net/en/audi-coupe-b2-81-85-facelift-1984-generation-5225
EU-AUDI-COUPE-B2-COUPE-PREFL-01	4349	1682	1350	Auto-Data	https://www.auto-data.net/en/audi-coupe-b2-81-85-generation-1091
EU-AUDI-QUATTRO-TYP85-COUPE-01	4404	1723	1344	Auto-Data	https://www.auto-data.net/en/audi-quattro-typ-85-2.1-turbo-200hp-4902
EU-AUDI-COUPE-B3-COUPE-01	4470	1716	1380	Auto-Data	https://www.auto-data.net/en/audi-coupe-b3-89-generation-1090
EU-AUDI-COUPE-B4-FACELIFT-COUPE-01	4366	1716	1375	Auto-Data	https://www.auto-data.net/en/audi-coupe-b4-8c-2.8-v6-e-174hp-4476
EU-FIAT-508A-BALILLA-SEDAN-01	3140	1400	1530	AutomobilePedia	https://automobilepedia.com/fiat/508.html
EU-AUDI-S2-COUPE-8B-01	4401	1716	1375	Auto-Data	https://www.auto-data.net/en/audi-s2-model-518
EU-AUDI-100-C4-SEDAN-FWD-01	4790	1777	1431	Auto-Data	https://www.auto-data.net/en/audi-100-4a-c4-2.5-tdi-115hp-4091
EU-FORD-ESCORT-III-HATCHBACK-3D-01	3966	1640	1337	AutoData1	https://www.autodata1.com/en/car/ford/escort/escort-iii-gaaawaabftava-16-xr3i-105-hp
EU-FORD-ESCORT-III-HATCHBACK-5D-01	3966	1640	1337	CarsSpecsGuru	https://www.carspecsguru.com/ford/escort/1023/1541/modification-10948
EU-AUDI-S4-C4-SEDAN-01	4790	1804	1443	Automobile-Catalog	https://www.automobile-catalog.com/car/1993/238640/audi_s4.html
EU-AUDI-100-C4-SEDAN-QUATTRO-01	4790	1777	1437	Auto-Data	https://www.auto-data.net/en/audi-100-4a-c4-2.3-e-133hp-quattro-4089
EU-AUDI-80-B4-SEDAN-01	4482	1695	1406	Auto-Data	https://www.auto-data.net/en/audi-80-b4-typ-8c-generation-1110
EU-ALPINA-B7-F01-SEDAN-AWD-01	5087	1902	1485	Automobile-Catalog	https://www.automobile-catalog.com/car/2011/1339610/alpina_b7_biturbo_allrad.html
EU-AUDI-S2-B4-SEDAN-01	4509	1695	1386	Auto-Data	https://www.auto-data.net/en/audi-s2-generation-5230
EU-FORD-ESCORT-III-CONVERTIBLE-01	4010	1640	1403	Automobile-Catalog	https://www.automobile-catalog.com/car/1985/30260/ford_escort_cabriolet_1_3.html
EU-AUDI-100-C3-AVANT-01	4793	1814	1422	Auto-Data	https://www.auto-data.net/en/audi-100-avant-c3-typ-44-44q-facelift-1988-generation-5183
EU-ALPINA-D3-E90-SEDAN-01	4545	1817	1413	Auto-Data	https://www.auto-data.net/en/alpina-d3-e90-2.0-bi-turbo-diesel-214hp-1690
EU-AUDI-100-C2-AVANT-01	4587	1768	1390	Automobile-Catalog	https://www.automobile-catalog.com/car/1977/166235/audi_100_avant_l.html
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_1301-1400_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/audi-200-c3-typ-44-44q-2.2-turbo-165hp-4272 "https://www.auto-data.net/en/audi-200-c3-typ-44-44q-2.2-turbo-165hp-4272"
[2]: https://www.valeoservice.com/en-com/techassist/vehicle/P-1382?country=DE&utm_source=chatgpt.com "Parts FORD ESCORT III (GAA)"
[3]: https://autogral.com/alpina-b3-s-bi-turbo-coupe-awd-switch-tronic-000272-versus-bmw-320i-coupe-002707_uk.html "https://autogral.com/alpina-b3-s-bi-turbo-coupe-awd-switch-tronic-000272-versus-bmw-320i-coupe-002707_uk.html"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_1301-1400_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_1301-1400_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（1774 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（422 行）
