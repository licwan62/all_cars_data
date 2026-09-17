# 任务：all 第 101-200 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0002__b5a82ede


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 101-200 行

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
all 第 101-200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
Audi	A6 c6	2.7 TDI Quattro	Stufenheck	Allrad	Diesel	120	163	Jun 2005	Mar 2011	2024-03-01	19234
Audi	A6 c6 avant	2.7 TDI Quattro	Kombi	Allrad	Diesel	120	163	Jun 2005	Aug 2011	2024-03-01	19235
VW	Caddy iii	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2005	Aug 2010	2024-03-01	19236
VW	New beetle	1.9 TDI	Schrägheck	Frontantrieb	Diesel	77	105	Jul 2005	Sep 2010	2024-03-01	19237
VW	New beetle	1.9 TDI	Cabriolet	Frontantrieb	Diesel	77	105	Jul 2005	Sep 2010	2024-03-01	19238
Audi	Tt	1.8 T	Cabriolet	Frontantrieb	Benzin	120	163	Sep 2005	Jun 2006	2024-03-01	19239
Honda	Civic viii hatchback	1.4	Schrägheck	Frontantrieb	Benzin	61	83	Sep 2005	Sep 2008	2024-03-01	19240
Honda	Civic viii hatchback	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Sep 2005	Dec 2011	2024-03-01	19241
Honda	Civic viii hatchback	2.2 Ctdi	Schrägheck	Frontantrieb	Diesel	103	140	Sep 2005	Dec 2011	2024-03-01	19242
Toyota	Aygo	1.4 D-4d	Schrägheck	Frontantrieb	Diesel	40	54	Jul 2005	Aug 2010	2024-03-01	19243
Mazda	6	2.3 MPS Turbo	Stufenheck	Allrad	Benzin	191	260	Dec 2005	Aug 2007	2024-03-01	19244
Toyota	Corolla	2.2 D-4d	Großraumlimousine	Frontantrieb	Diesel	100	136	Oct 2005	Mar 2009	2024-03-01	19245
Toyota	Avensis	2.2 D-4d	Schrägheck	Frontantrieb	Diesel	110	150	Oct 2005	Nov 2008	2024-03-01	19246
Toyota	Avensis	2.2 D-4d	Stufenheck	Frontantrieb	Diesel	110	150	Oct 2005	Nov 2008	2024-03-01	19247
Toyota	Avensis	2.2 D-4d	Kombi	Frontantrieb	Diesel	110	150	Oct 2005	Nov 2008	2024-03-01	19248
Toyota	Avensis	2.2 D-cat	Schrägheck	Frontantrieb	Diesel	130	177	Jul 2005	Nov 2008	2024-03-01	19249
Toyota	Avensis	2.2 D-cat	Stufenheck	Frontantrieb	Diesel	130	177	Jul 2005	Nov 2008	2024-03-01	19250
Toyota	Avensis	2.2 D-cat	Kombi	Frontantrieb	Diesel	130	177	Jul 2005	Nov 2008	2024-03-01	19251
Toyota	Corolla	1.8 Vvtl-i TS	Schrägheck	Frontantrieb	Benzin	165	224	Feb 2005	Feb 2007	2024-03-01	19252
VW	Polo	1.8 GTI	Schrägheck	Frontantrieb	Benzin	110	150	Sep 2005	Nov 2009	2024-03-01	19253
Toyota	Yaris	1.0 Vvt-i	Schrägheck	Frontantrieb	Benzin	51	69	Aug 2005	Dec 2011	2024-03-01	19254
Toyota	Yaris	1.4 D-4d	Schrägheck	Frontantrieb	Diesel	66	90	Aug 2005	Dec 2012	2024-03-01	19255
Toyota	Yaris	1.3 Vvt-i	Schrägheck	Frontantrieb	Benzin	64	87	Aug 2005	Nov 2010	2024-03-01	19256
Mercedes-benz	C-Klasse	C 320 CDI	Kombi	Heckantrieb	Diesel	165	224	Jun 2005	Aug 2007	2024-03-01	19257
BMW	Z4 roadster	2.5 I	Cabriolet	Heckantrieb	Benzin	130	177	Sep 2005	Feb 2009	2024-03-01	19258
BMW	Z4 roadster	2.5 SI	Cabriolet	Heckantrieb	Benzin	160	218	Jan 2006	Aug 2008	2024-03-01	19259
BMW	Z4 roadster	3.0 SI	Cabriolet	Heckantrieb	Benzin	195	265	Jan 2006	Aug 2008	2024-03-01	19260
Opel	Zafira	2	Großraumlimousine	Frontantrieb	Benzin	177	241	Jan 2006	Dec 2010	2024-03-01	19261
Ford	Focus c-Max	1.8 Flexifuel	Großraumlimousine	Frontantrieb	Benzin/Ethanol	92	125	Jan 2006	Mar 2007	2024-03-01	19262
Mercedes-benz	E-Klasse	E 420 CDI	Stufenheck	Heckantrieb	Diesel	231	314	Jan 2006	Dec 2008	2024-03-01	19263
Ford	Focus ii	1.8 Flexifuel	Schrägheck	Frontantrieb	Benzin/Ethanol	92	125	Jan 2006	Sep 2012	2024-03-01	19264
Ford	Focus ii turnier	1.8 Flexifuel	Kombi	Frontantrieb	Benzin/Ethanol	92	125	Jan 2006	Sep 2012	2024-03-01	19265
Mercedes-benz	E-Klasse	E 280 4-matic	Stufenheck	Allrad	Benzin	170	231	Jan 2006	Dec 2008	2024-03-01	19266
Mercedes-benz	E-Klasse	E 350 4-matic	Stufenheck	Allrad	Benzin	200	272	Mar 2005	Dec 2008	2024-03-01	19267
Opel	Vectra c cc	1.8	Schrägheck	Frontantrieb	Benzin	103	140	Aug 2005	Aug 2008	2024-03-01	19268
Opel	Vectra c cc	1.6	Schrägheck	Frontantrieb	Benzin	77	105	Jan 2006	Aug 2008	2024-03-01	19269
Skoda	Fabia i combi	1.2	Kombi	Frontantrieb	Benzin	40	54	Jul 2001	Dec 2007	2024-03-01	19270
Skoda	Fabia i praktik	1.2	Kasten/Kombi	Frontantrieb	Benzin	40	54	Jul 2001	Dec 2007	2024-03-01	19271
Saab	9-3	2.8 Turbo V6	Cabriolet	Frontantrieb	Benzin	184	250	Feb 2006	Feb 2015	2024-03-01	19272
Skoda	Roomster	1.2	Großraumlimousine	Frontantrieb	Benzin	47	64	May 2006	Jan 2007	2024-03-01	19273
Skoda	Roomster	1.4	Großraumlimousine	Frontantrieb	Benzin	63	86	Sep 2006	May 2015	2024-03-01	19274
Skoda	Roomster	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Sep 2006	May 2015	2024-03-01	19275
Skoda	Roomster	1.4 TDI	Großraumlimousine	Frontantrieb	Diesel	51	70	Jul 2006	Mar 2010	2024-03-01	19276
Skoda	Roomster	1.4 TDI	Großraumlimousine	Frontantrieb	Diesel	59	80	Sep 2006	Mar 2010	2024-03-01	19277
Skoda	Roomster	1.9 TDI	Großraumlimousine	Frontantrieb	Diesel	77	105	Sep 2006	Mar 2010	2024-03-01	19278
Opel	Corsa c	1.2	Kasten/Schrägheck	Frontantrieb	Benzin	59	80	Jul 2005	Jun 2006	2024-03-01	19279
Opel	Vectra c	1.6	Stufenheck	Frontantrieb	Benzin	77	105	Aug 2005	Aug 2008	2024-03-01	19280
Opel	Vectra c	1.8	Stufenheck	Frontantrieb	Benzin	103	140	Aug 2005	Aug 2008	2024-03-01	19281
Opel	Vectra c	3.0 Cdti	Stufenheck	Frontantrieb	Diesel	135	184	Aug 2005	Aug 2008	2024-03-01	19282
Opel	Vectra c cc	3.0 Cdti	Schrägheck	Frontantrieb	Diesel	135	184	Aug 2005	Aug 2008	2024-03-01	19283
Opel	Vectra c caravan	1.9 Cdti	Kombi	Frontantrieb	Diesel	74	100	Jun 2005	Aug 2008	2024-03-01	19284
Opel	Vectra c	1.9 Cdti	Stufenheck	Frontantrieb	Diesel	74	100	Oct 2005	Aug 2008	2024-03-01	19285
Opel	Vectra c cc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	74	100	Jun 2005	Aug 2008	2024-03-01	19286
Opel	Astra h gtc	1.9 Cdti	Schrägheck	Frontantrieb	Diesel	74	101	Jan 2006	Oct 2010	2024-03-01	19287
Alfa Romeo	Giulietta	1.4 Bifuel	Schrägheck	Frontantrieb	Benzin/Autogas (LPG)	88	120	Dec 2011	Feb 2017	2024-03-01	19288
Opel	Meriva a	1.6	Großraumlimousine	Frontantrieb	Benzin	77	105	Jan 2006	May 2010	2024-03-01	19289
Opel	Meriva a	1.3 Cdti	Großraumlimousine	Frontantrieb	Diesel	55	75	Sep 2003	May 2010	2024-03-01	19290
Mercedes-benz	E-Klasse	E 320 T CDI 4-matic	Kombi	Allrad	Diesel	165	224	Mar 2005	Jul 2009	2024-03-01	19291
Mercedes-benz	E-Klasse	E 350 T 4-matic	Kombi	Allrad	Benzin	200	272	Mar 2005	Jul 2009	2024-03-01	19292
Mercedes-benz	E-Klasse	E 320 CDI 4-matic	Stufenheck	Allrad	Diesel	165	224	Mar 2005	Dec 2008	2024-03-01	19293
Mercedes-benz	M-Klasse	ML 63 AMG 4-matic	SUV	Allrad	Benzin	375	510	Jan 2006	Dec 2011	2024-03-01	19294
Toyota	Rav 4 iii	2.0 4WD	SUV	Allrad	Benzin	112	152	Feb 2006	Jun 2013	2024-03-01	19295
Toyota	Rav 4 iii	2.2 D 4WD	SUV	Allrad	Diesel	100	136	Feb 2006	Dec 2012	2024-03-01	19296
Toyota	Rav 4 iii	2.2 D 4WD	SUV	Allrad	Diesel	130	177	Feb 2006	Jun 2013	2024-03-01	19297
BMW	3	318 D	Kombi	Heckantrieb	Diesel	90	122	Sep 2005	Aug 2007	2024-03-01	19298
BMW	3	318 I	Kombi	Heckantrieb	Benzin	95	129	Jan 2006	Aug 2007	2024-03-01	19299
BMW	Z4	3.0 SI	Coupe	Heckantrieb	Benzin	195	265	Apr 2006	Aug 2008	2024-03-01	19300
BMW	3	330 CD	Cabriolet	Heckantrieb	Diesel	150	204	Aug 2005	Dec 2007	2024-03-01	19301
Honda	Civic viii	1.3 IMA	Stufenheck	Frontantrieb	Benzin/Elektro	70	95	Jan 2006	Dec 2012	2024-03-01	19302
Mini	Mini	John Cooper Works	Cabriolet	Frontantrieb	Benzin	155	210	Jul 2004	Nov 2007	2024-03-01	19303
Mini	Mini	ONE D	Schrägheck	Frontantrieb	Diesel	65	88	Jun 2003	Sep 2006	2024-03-01	19304
Chrysler	Pt cruiser	2.4	Kombi	Frontantrieb	Benzin	105	143	Aug 2005	Dec 2010	2024-03-01	19305
Chrysler	Pt cruiser	2.2 CRD	Kombi	Frontantrieb	Diesel	110	150	Aug 2005	Dec 2010	2024-03-01	19306
Fiat	Ducato	2.8 JTD Power	Kasten	Frontantrieb	Diesel	107	146	Apr 2004	Jul 2006	2024-03-01	19312
Fiat	Ducato	2.8 JTD Power	Pritsche/Fahrgestell	Frontantrieb	Diesel	107	146	Apr 2004	Jul 2006	2024-03-01	19313
Fiat	Bravo i	1.9 JTD	Schrägheck	Frontantrieb	Diesel	74	100	Sep 2000	Oct 2001	2024-03-01	19314
Fiat	Brava	1.9 JTD	Schrägheck	Frontantrieb	Diesel	74	100	Sep 2000	Oct 2001	2024-03-01	19315
BMW	7	730 I, LI	Stufenheck	Heckantrieb	Benzin	190	258	Mar 2005	Aug 2008	2024-03-01	19316
Opel	Vectra c caravan	1.8	Kombi	Frontantrieb	Benzin	103	140	Aug 2005	Aug 2008	2024-03-01	19317
Daihatsu	Copen	1.3	Cabriolet	Frontantrieb	Benzin	64	87	Mar 2006	Sep 2012	2024-03-01	19318
Peugeot	307	2.0 HDI 110	Kombi	Frontantrieb	Diesel	79	107	Mar 2002	Dec 2009	2024-03-01	19319
Peugeot	607	3.0 V6 24V	Stufenheck	Frontantrieb	Benzin	155	211	Mar 2004	Jul 2011	2024-03-01	19320
Peugeot	5008	2.0 HDI 136 / Bluehdi 136	Großraumlimousine	Frontantrieb	Diesel	100	136	Feb 2012	Mar 2017	2024-03-01	19322
Smart	Forfour	1.1	Schrägheck	Frontantrieb	Benzin	47	64	Feb 2005	Jun 2006	2024-03-01	19323
Fiat	Doblo	1.3 D Multijet	Großraumlimousine	Frontantrieb	Diesel	62	84	Oct 2005	-	2024-03-01	19324
Fiat	Doblo	1.9 D Multijet	Großraumlimousine	Frontantrieb	Diesel	88	120	Oct 2005	-	2024-03-01	19325
Fiat	Doblo	1.4	Großraumlimousine	Frontantrieb	Benzin	57	77	Oct 2005	-	2024-03-01	19326
Fiat	Doblo	1.6 Natural Power	Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	76	103	Sep 2002	-	2024-03-01	19327
Fiat	Doblo	1.4	Kasten/Großraumlimousine	Frontantrieb	Benzin	57	77	Oct 2005	-	2024-03-01	19328
Fiat	Doblo	1.6 Natural Power	Kasten/Großraumlimousine	Frontantrieb	Benzin/Erdgas (CNG)	76	103	Sep 2002	-	2024-03-01	19329
Fiat	Doblo	1.3 D Multijet	Kasten/Großraumlimousine	Frontantrieb	Diesel	55	75	Oct 2005	Jan 2010	2024-03-01	19330
Opel	Astra h gtc	1.3 Cdti	Schrägheck	Frontantrieb	Diesel	66	90	Apr 2005	Oct 2010	2024-03-01	19331
VW	Golf v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	Oct 2003	Nov 2008	2024-03-01	19332
VW	Golf plus v	2.0 TDI	Schrägheck	Frontantrieb	Diesel	100	136	May 2005	Dec 2013	2024-03-01	19333
BMW	3	318 CI	Cabriolet	Heckantrieb	Benzin	110	150	Mar 2004	Aug 2006	2024-03-01	19334
Skoda	Fabia i praktik	1.4	Kasten/Kombi	Frontantrieb	Benzin	50	68	Jul 2001	May 2003	2024-03-01	19335
Volvo	S80 ii	D5	Stufenheck	Frontantrieb	Diesel	136	185	Mar 2006	Aug 2009	2024-03-01	19336
Volvo	S80 ii	4.4 V8 AWD	Stufenheck	Allrad	Benzin	232	316	Mar 2006	Mar 2012	2024-03-01	19337
Lexus	Rx	350 AWD	SUV	Allrad	Benzin	203	276	Feb 2006	Dec 2008	2024-03-01	19339
Citroën	C3 i	1.6 16V HDI	Schrägheck	Frontantrieb	Diesel	66	90	Oct 2005	Dec 2009	2024-07-01	19340


--- Round 1 / 首次发送 ---
## 更新点

* 已完成首段 `19234–19253`，覆盖 **20 个输入 Ktype、29 条映射、20 个尺寸组**。
* `19243 Toyota Aygo` 确认同时覆盖三门、五门，但柴油版本属于改款前外廓，两条派生映射复用同一尺寸组。
* `19245 Toyota Corolla Verso` 跨越 2007 年改款，改款前后长宽高均有变化，必须拆分。
* `19246–19251 Toyota Avensis` 跨越 2006 年改款，官方资料确认改款后车长增加 15 mm；轿车和掀背车改款后高度为 **1485 mm**，不能沿用改款前的 1480 mm。
* `19252 Corolla TS Compressor` 官方资料确认是三门车身，运动悬架使高度降至 **1440 mm**，宽度明确不含后视镜。([Dezo's Garage][1])
* `19253 Polo GTI` 的三门和五门并非同一外廓，分别为两套尺寸，不能合并。
* Audi A6 的 120 kW 版本限定在改款前阶段；输入结束月虽延伸到 2011 年，但不能据此套用改款后 140 kW 车身资料。([维基百科][2])
* Corolla Verso 改款前官方规格为 4360 × 1770 × 1620 mm；1660 mm 是带车顶行李架高度，本表采用标准车身高度 1620 mm。([Dezo's Garage][3])

## 当前批次进度

* 输入 Ktype 总数：100
* 已完成输入 Ktype：20
* READY 映射：29
* 本轮已输出范围内 PENDING：0
* 已确认尺寸组：20
* 尚待处理输入 Ktype：80
* 当前批次尚未完成。

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19234	19234	Sedan	Audi A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH	120 kW版本限定改款前外廓。	READY
19235	19235	Wagon	Audi A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-5D-PREFL-01	HIGH	120 kW版本限定改款前外廓。	READY
19236	19236	MPV	Volkswagen Caddy III	2K	5	EU-VW-CADDY-III-MPV-5D-SWB-01	HIGH	短轴乘用型车身。	READY
19237	19237	Hatchback	Volkswagen New Beetle I facelift	9C1	3	EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	HIGH		READY
19238	19238	Convertible	Volkswagen New Beetle I facelift	1Y7	2	EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
19239	19239	Convertible	Audi TT 8N facelift	8N9	2	EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
19240	19240	Hatchback	Honda Civic VIII	FK1	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19241	19241	Hatchback	Honda Civic VIII	FK2	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19242	19242	Hatchback	Honda Civic VIII	FK3	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19243_3dr	19243	Hatchback	Toyota Aygo I	AB10	3	EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	HIGH	三门分支。	READY
19243_5dr	19243	Hatchback	Toyota Aygo I	AB10	5	EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	HIGH	五门分支。	READY
19244	19244	Sedan	Mazda 6 I facelift	GG1	4	EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	HIGH	MPS四门轿车车身。	READY
19245_prefl	19245	MPV	Toyota Corolla Verso II	AR10	5	EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	HIGH	2007年改款前车身。	READY
19245_facelift	19245	MPV	Toyota Corolla Verso II facelift	AR10	5	EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	HIGH	2007年改款后车身。	READY
19246_prefl	19246	Hatchback	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	HIGH	2006年改款前车身。	READY
19246_facelift	19246	Hatchback	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	HIGH	2006年改款后车身。	READY
19247_prefl	19247	Sedan	Toyota Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	HIGH	2006年改款前车身。	READY
19247_facelift	19247	Sedan	Toyota Avensis II facelift	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	HIGH	2006年改款后车身。	READY
19248_prefl	19248	Wagon	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	HIGH	2006年改款前车身。	READY
19248_facelift	19248	Wagon	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	HIGH	2006年改款后车身。	READY
19249_prefl	19249	Hatchback	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	HIGH	2006年改款前车身。	READY
19249_facelift	19249	Hatchback	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	HIGH	2006年改款后车身。	READY
19250_prefl	19250	Sedan	Toyota Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	HIGH	2006年改款前车身。	READY
19250_facelift	19250	Sedan	Toyota Avensis II facelift	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	HIGH	2006年改款后车身。	READY
19251_prefl	19251	Wagon	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	HIGH	2006年改款前车身。	READY
19251_facelift	19251	Wagon	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	HIGH	2006年改款后车身。	READY
19252	19252	Hatchback	Toyota Corolla IX	E12	3	EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	HIGH	TS Compressor三门车身。	READY
19253_3dr	19253	Hatchback	Volkswagen Polo IV facelift	9N3	3	EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	HIGH	GTI三门分支。	READY
19253_5dr	19253	Hatchback	Volkswagen Polo IV facelift	9N3	5	EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	HIGH	GTI五门分支。	READY
```

## 本轮新增/修改的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4f-c6-2.7-tdi-v6-180hp-quattro-tiptronic-26845
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463	Auto-Data.net	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.7-tdi-v6-180hp-quattro-tiptronic-4677
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833	Auto-Data.net	https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-75hp-28303
EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Auto-Data.net	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-1.9-tdi-105hp-28079
EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	4129	1721	1502	Auto-Data.net	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-facelift-2005-1.9-tdi-105hp-28151
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349	Auto-Data.net	https://www.auto-data.net/en/audi-tt-roadster-8n-facelift-2000-1.8-t-163hp-4868
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460	Auto-Data.net	https://www.auto-data.net/en/honda-civic-viii-hatchback-5d-generation-2621
EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	3405	1615	1465	Auto-Data.net;Toyota UK Media Site	https://www.auto-data.net/en/toyota-aygo-generation-913;https://media.toyota.co.uk/aygos-a-go-go/
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-sedan-typ-gg-gy-gg1-facelift-2005-mps-2.3-260hp-awd-30762
EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	4360	1770	1620	Toyota Corolla Verso 2005 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Corolla-Verso-UK.pdf
EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	4370	1770	1625	Auto-Data.net	https://www.auto-data.net/en/toyota-corolla-verso-ii-ar10-facelift-2007-generation-815
EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	4630	1760	1480	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	4645	1760	1485	Toyota Avensis Gen2 MC official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf
EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	4630	1760	1480	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	4645	1760	1485	Toyota Avensis Gen2 MC official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf
EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	4700	1760	1525	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	4715	1760	1525	Toyota Avensis Gen2 MC official launch pack;Auto-Data.net	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf;https://www.auto-data.net/en/toyota-avensis-ii-wagon-generation-901
EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	4200	1710	1440	Toyota Corolla 2006 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2006-Toyota-Corolla-UK.pdf
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-1.8-150hp-3-d-8428
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-1.8-150hp-5-d-8429
```

## 下一步优先处理

1. `19254–19256 Toyota Yaris II`：核对三门/五门以及 2009 年改款前后外廓。
2. `19257–19267`：闭合 Mercedes S203、W211、BMW Z4 E85、Zafira B、Ford C-Max/Focus II。
3. 批量处理 Vectra C 的 Sedan、Hatchback、Wagon 三套车身，避免按发动机重复建组。
4. 提前拆解高风险商用车：Fiat Ducato 与 Doblo 的轴距、车顶和厢式/底盘分支。

推进信号：CONTINUE

[1]: https://xr793.com/wp-content/uploads/2022/12/2006-Toyota-Corolla-UK.pdf "untitled"
[2]: https://de.wikipedia.org/wiki/Audi_A6_C6?utm_source=chatgpt.com "Audi A6 C6"
[3]: https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Corolla-Verso-UK.pdf "untitled"


--- 发送 / 继续到 Round 2 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 2 / 下一步 ---
## 更新点

* 新完成 `19254–19263`，新增 **10 个 Ktype、20 条 READY 映射、8 个尺寸组**。
* Toyota 官方资料确认 Yaris II 的 1.0、1.3 和 1.4 D-4D 均存在三门与五门版本；三门、五门尺寸相同，门数分别建映射行并复用同一阶段尺寸组。2009 年改款后车长由 3750 mm 增至 3785 mm，因此按改款前后拆分尺寸组。
* `19258–19260` 均归入 BMW Z4 E85 LCI Roadster，同一物理外廓直接复用一个尺寸组。([汽车数据网][1])
* `19261` Zafira B OPC 改款前后核得相同三维，因此不重复建组。([汽车数据网][2])
* `19263` Mercedes E 420 CDI 跨越 2006 年中期改款，改款前后长度和高度均不同，拆为两个映射分支及两个尺寸组。([汽车数据网][3])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：30
* READY 映射：49
* 已确认尺寸组：28
* 已处理范围内无 PENDING 映射
* 尚未处理 Ktype：70
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19254_3dr_prefl	19254	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19254_5dr_prefl	19254	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19254_3dr_facelift	19254	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19254_5dr_facelift	19254	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19255_3dr_prefl	19255	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19255_5dr_prefl	19255	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19255_3dr_facelift	19255	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19255_5dr_facelift	19255	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19256_3dr_prefl	19256	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19256_5dr_prefl	19256	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19256_3dr_facelift	19256	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19256_5dr_facelift	19256	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19257	19257	Wagon	Mercedes-Benz C-Class S203 facelift	S203	5	EU-MERCEDES-BENZ-C-CLASS-S203-WAGON-FACELIFT-01	HIGH		READY
19258	19258	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19259	19259	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19260	19260	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19261	19261	MPV	Opel Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-OPC-01	HIGH		READY
19262	19262	MPV	Ford Focus C-MAX I		5	EU-FORD-FOCUS-C-MAX-I-MPV-PREFL-01	HIGH		READY
19263_prefl	19263	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-PREFL-01	HIGH	2006年改款前车身。	READY
19263_facelift	19263	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-FACELIFT-01	HIGH	2006年改款后车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	3750	1695	1530	Toyota Gen2 Yaris official archive press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen2-Yaris-archive-press-pack.pdf
EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	3785	1695	1530	Toyota UK Media Site 2009 Yaris specifications	https://media.toyota.co.uk/2009-toyota-yaris-less-is-so-much-more/
EU-MERCEDES-BENZ-C-CLASS-S203-WAGON-FACELIFT-01	4541	1728	1465	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s203-facelift-2004-c-320-cdi-v6-224hp-7g-tronic-40945
EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	4091	1781	1299	Auto-Data.net	https://www.auto-data.net/en/bmw-z4-e85-lci-facelift-2006-2.5i-177hp-9903
EU-OPEL-ZAFIRA-B-MPV-OPC-01	4467	1801	1645	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/opel-zafira-b-opc-2.0i-16v-turbo-240hp-2597;https://www.auto-data.net/en/opel-zafira-b-facelift-2008-opc-2.0i-16v-turbo-240hp-26232
EU-FORD-FOCUS-C-MAX-I-MPV-PREFL-01	4333	1825	1595	Auto-Data.net	https://www.auto-data.net/fr/ford-focus-c-max-i-1.8-16v-125hp-flexfuel-37914
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-PREFL-01	4818	1822	1431	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-e-420-cdi-v8-314hp-7g-tronic-12900
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-FACELIFT-01	4856	1822	1465	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-420-cdi-v8-314hp-7g-tronic-37048
```

## 下一步优先处理

1. `19264–19265`：Ford Focus II Hatchback、Turnier 的 2008 年改款前后尺寸边界。
2. `19266–19267`：Mercedes W211 E 280/E 350 4MATIC，按改款前后及四驱标准车高拆分。
3. `19268–19286`：集中闭合 Vectra C Sedan、CC 和 Caravan 三套外廓并批量复用。
4. `19270–19278`：Fabia Combi、Fabia Praktik、Saab 9-3 Convertible 和 Roomster 改款边界。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/bmw-z4-e85-lci-facelift-2006-2.5i-177hp-9903 "BMW Z4 (E85 LCI, facelift 2006) 2.5i (177 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/opel-zafira-b-opc-2.0i-16v-turbo-240hp-2597 "Opel Zafira B OPC 2.0i 16V Turbo (240 Hp) | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-420-cdi-v8-314hp-7g-tronic-37048 "Mercedes-Benz E-class (W211, facelift 2006) E 420 CDI V8 (314 Hp) 7G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 3 / 下一步 ---
## 更新点

* 完成 `19264–19286`，本轮新增 **23 个 Ktype、32 条 READY 映射、15 个尺寸组**。
* Focus II 掀背和旅行版均跨越 2008 年改款，改款前后长宽高发生变化，因此按车身形式和改款阶段拆组；掀背的三门、五门尺寸相同，只拆映射、不重复建尺寸组。([汽车数据网][1])
* `19266` 与 `19267` 都是 W211 4MATIC，发动机不同不构成尺寸组差异；两者分别复用相同的改款前组和改款后组。([Ultimate Specs][2])
* Fabia Praktik 历史技术资料明确其基于 Fabia Combi，且车长在 2004 年由 4222 mm 变为 4232 mm，宽高不变，因此 Praktik 与 Combi 按改款阶段共用尺寸组。([汽车中央][3])
* Vectra C Sedan、CC Hatchback、Caravan 虽有部分相同三维，但属于不同物理车身，分别建组；同车身下的多个发动机 Ktype 批量复用。([汽车数据网][4])
* Roomster 2010 年改款后车长由 4205 mm 变为 4214 mm；1.6 汽油版本于改款前结束，不创建不存在的改款后分支。([汽车数据网][5])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：53
* READY 映射：81
* 已确认尺寸组：43
* 已处理范围内未产生 PENDING
* 尚未处理 Ktype：47
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19264_3dr_prefl	19264	Hatchback	Ford Focus II		3	EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19264_5dr_prefl	19264	Hatchback	Ford Focus II		5	EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19264_3dr_facelift	19264	Hatchback	Ford Focus II facelift		3	EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH	三门改款后车身。	READY
19264_5dr_facelift	19264	Hatchback	Ford Focus II facelift		5	EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH	五门改款后车身。	READY
19265_prefl	19265	Wagon	Ford Focus II		5	EU-FORD-FOCUS-II-WAGON-PREFL-01	HIGH	改款前旅行车。	READY
19265_facelift	19265	Wagon	Ford Focus II facelift		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH	改款后旅行车。	READY
19266_prefl	19266	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC车身。	READY
19266_facelift	19266	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC车身。	READY
19267_prefl	19267	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC车身。	READY
19267_facelift	19267	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC车身。	READY
19268	19268	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19269	19269	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19270_prefl	19270	Wagon	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	2004年改款前Combi外廓。	READY
19270_facelift	19270	Wagon	Skoda Fabia I facelift	6Y5	5	EU-SKODA-FABIA-I-COMBI-FACELIFT-01	HIGH	2004年改款后Combi外廓。	READY
19271_prefl	19271	Van	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	Praktik商用车采用改款前Combi外廓。	READY
19271_facelift	19271	Van	Skoda Fabia I facelift	6Y5	5	EU-SKODA-FABIA-I-COMBI-FACELIFT-01	HIGH	Praktik商用车采用改款后Combi外廓。	READY
19272	19272	Convertible	Saab 9-3 II		2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH	250 hp版本限定改款前车身。	READY
19273	19273	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19274_prefl	19274	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19274_facelift	19274	MPV	Skoda Roomster I facelift		5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH	2010年改款后车身。	READY
19275	19275	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	1.6汽油版本限定2010年改款前车身。	READY
19276	19276	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19277	19277	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19278	19278	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19279	19279	Van	Opel Corsa C facelift		3	EU-OPEL-CORSA-C-VAN-FACELIFT-01	MEDIUM	三门商用厢式车身。	READY
19280	19280	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19281	19281	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19282	19282	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19283	19283	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19284	19284	Wagon	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Caravan五门旅行车车身。	READY
19285	19285	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19286	19286	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497	Auto-Data.net	https://www.auto-data.net/en/ford-focus-ii-hatchback-1.8-i-16v-125hp-7320
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/969140/ford_focus_1_8_flexifuel_style.html
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501	Auto-Data.net	https://www.auto-data.net/en/ford-focus-turnier-ii-1.8-i-16v-125hp-7348
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/969230/ford_focus_turnier_1_8_flexifuel_titanium.html
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	4818	1822	1452	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2581/Mercedes-Benz-E-Class-%28W211%29-280-4Matic.html
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	4856	1822	1499	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1542020/mercedes-benz_e_280_4matic.html
EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	4611	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-1.8i-16v-140hp-2248
EU-SKODA-FABIA-I-COMBI-PREFL-01	4222	1646	1452	Auto-Data.net;Škoda Fabia Praktik historical technical sheet	https://www.auto-data.net/fr/skoda-fabia-i-combi-6y-1.4-16v-75hp-14164;https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-COMBI-FACELIFT-01	4232	1646	1452	Auto-Data.net;Škoda Fabia Praktik historical technical sheet	https://www.auto-data.net/en/skoda-fabia-i-combi-6y-facelift-2004-1.2-htp-64hp-14159;https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data.net	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.8t-v6-250hp-11952
EU-SKODA-ROOMSTER-I-MPV-PREFL-01	4205	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-1.2-12v-64hp-14270
EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	4214	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-facelift-2010-1.4-86hp-19232
EU-OPEL-CORSA-C-VAN-FACELIFT-01	3839	1646	1440	MotorEU;UltimateSpecs	https://motoreu.com/opel-corsa-van-1.2-twinport-mpg-fuel-consumption-technical-specifications-168768;https://www.ultimatespecs.com/car-specs/Opel/1121/Opel-Corsa-C-12-16v.html
EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	4611	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-facelift-2005-1.8i-16v-140hp-2219
EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	4839	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-1.9-cdti-120hp-26130
```

## 下一步优先处理

1. `19287–19293`：Astra H GTC、Giulietta、Meriva A，以及 W211 Sedan/Wagon 4MATIC 的现有尺寸组复用。
2. `19294–19302`：M-Class W164、RAV4 III、BMW E91/E86/E46 与 Honda Civic VIII Sedan。
3. 批量闭合 `19303–19318` 中 Mini、PT Cruiser、Ducato、BMW 7 Series 长短轴及 Vectra Caravan 的复用关系。
4. Ducato 优先核对厢式车与底盘车的轴距、车顶和车身长度分支。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/ford-focus-ii-hatchback-1.8-i-16v-125hp-7320 "Ford Focus II Hatchback 1.8 i 16V (125 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2581/Mercedes-Benz-E-Class-%28W211%29-280-4Matic.html "Mercedes Benz E Class (W211) 280 4Matic Specs, Performance, Comparisons"
[3]: https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf "https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf"
[4]: https://www.auto-data.net/en/opel-vectra-c-facelift-2005-1.8i-16v-140hp-2219 "Opel Vectra C (facelift 2005) 1.8i 16V (140 Hp) | Technical specs, data, fuel consumption, Dimensions"
[5]: https://www.auto-data.net/en/skoda-roomster-1.2-12v-64hp-14270 "Skoda Roomster 1.2 12V (64 Hp) | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 4 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 4 / 下一步 ---
## 更新点

* 完成 `19287–19293`，新增 **7 个 Ktype、12 条 READY 映射、8 个尺寸组**。
* `19287 Astra H GTC` 跨越 2007 年改款。车长和车宽不变，但标准高度由 **1415 mm** 变为 **1435 mm**，因此必须拆分改款前后尺寸组。两阶段均为三门 GTC。([汽车数据网][1])
* `19288 Giulietta 1.4 LPG` 的原始 Type 940 与 2016 年改款版本三维均为 **4351 × 1798 × 1465 mm**，不因普通改款重复建组。([汽车数据网][2])
* `19290 Meriva A 1.3 CDTI` 覆盖改款前后车身，长度由 **4042 mm** 增至 **4052 mm**，宽度和高度不变；`19289` 从 2006 年开始，仅关联改款后组。([汽车数据网][3])
* `19291` 与 `19292` 的改款前 S211 旅行车高度、长度不同，不能因同属 4MATIC 而合并；改款后两者三维相同，可共享一个尺寸组。([汽车数据网][4])
* `19293` 只新增映射，直接复用此前闭合的 W211 Sedan 4MATIC 改款前后尺寸组，本轮不重复输出尺寸组。

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：60
* READY 映射：93
* 已确认尺寸组：51
* 已处理范围内 PENDING：0
* 尚未处理 Ktype：40
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19287_prefl	19287	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	2007年改款前三门GTC外廓。	READY
19287_facelift	19287	Hatchback	Opel Astra H GTC facelift	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	2007年改款后三门GTC外廓。	READY
19288	19288	Hatchback	Alfa Romeo Giulietta Type 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
19289	19289	MPV	Opel Meriva A facelift		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	2006年改款后车身。	READY
19290_prefl	19290	MPV	Opel Meriva A		5	EU-OPEL-MERIVA-A-MPV-PREFL-01	HIGH	2006年改款前车身。	READY
19290_facelift	19290	MPV	Opel Meriva A facelift		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	2006年改款后车身。	READY
19291_prefl	19291	Wagon	Mercedes-Benz E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E320-CDI-4MATIC-PREFL-01	HIGH	2006年改款前E 320 CDI 4MATIC旅行车。	READY
19291_facelift	19291	Wagon	Mercedes-Benz E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC旅行车。	READY
19292_prefl	19292	Wagon	Mercedes-Benz E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E350-4MATIC-PREFL-01	HIGH	2006年改款前E 350 4MATIC旅行车。	READY
19292_facelift	19292	Wagon	Mercedes-Benz E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC旅行车。	READY
19293_prefl	19293	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC轿车。	READY
19293_facelift	19293	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC轿车。	READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	4290	1753	1415	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-gtc-1.9-cdti-120hp-2381
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	4290	1753	1435	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.9-cdti-ecotec-120hp-automatic-47425
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-1.4-120hp-lpg-18680
EU-OPEL-MERIVA-A-MPV-PREFL-01	4042	1694	1624	Auto-Data.net	https://www.auto-data.net/en/opel-meriva-a-generation-561
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	Auto-Data.net	https://www.auto-data.net/en/opel-meriva-a-facelift-2006-1.6i-16v-105hp-2521
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E320-CDI-4MATIC-PREFL-01	4847	1822	1499	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-320-cdi-v6-224hp-4matic-5g-tronic-51989
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E350-4MATIC-PREFL-01	4850	1822	1495	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-350-272hp-4matic-5g-tronic-12930
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	4888	1822	1506	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-320-cdi-v6-224hp-4matic-5g-tronic-37050;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-350-v6-272hp-4matic-5g-tronic-37052
```

## 下一步优先处理

1. `19294 Mercedes ML 63 AMG`：解决 W164 改款后空气悬架高度口径差异，只在标准量产高度闭合后建组。
2. `19295–19297 Toyota RAV4 III`：分别核对普通车身、T180 宽体以及中期改款外廓。
3. `19298–19304`：批量处理 BMW E91、E85/E86、E46、Honda Civic VIII Sedan 和 Mini R50/R52。
4. `19305–19318`：处理 PT Cruiser、Ducato 厢式与底盘车、BMW E65/E66 长短轴和 Daihatsu Copen。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/opel-astra-h-gtc-1.9-cdti-120hp-2381 "Opel Astra H GTC 1.9 CDTI (120 Hp) | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-1.4-120hp-lpg-18680?utm_source=chatgpt.com "Alfa Romeo Giulietta (Type 940) 1.4 (120 Hp) LPG | Technical specs, data, fuel consumption, Dimensions"
[3]: https://www.auto-data.net/en/opel-meriva-a-generation-561 "Opel Meriva A | Technical Specs, Fuel consumption, Dimensions"
[4]: https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-320-cdi-v6-224hp-4matic-5g-tronic-51989 "Mercedes-Benz E-class T-modell (S211) E 320 CDI V6 (224 Hp) 4MATIC 5G-TRONIC | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 5 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 5 / 下一步 ---
## 更新点

* 完成 `19294–19304` 的映射判断，新增 **11 条 READY 映射、1 条 PENDING 映射、9 个尺寸组**。
* `19294 ML 63 AMG` 确认跨越 2008 年改款，改款前后长度分别为 4812 mm、4814 mm，但奔驰官方将空气悬架车高分别列为 `1764–1844 mm` 和 `1765–1845 mm`，无法唯一确定标准状态高度，因此暂不创建尺寸组。([marsClassic][1])
* RAV4 III 普通车身与 T180 不是同一外廓：普通版本为 `4395 × 1815 × 1685 mm`，T180 因无后挂备胎且带宽体轮眉，为 `4315 × 1855 × 1685 mm`；2010 年改款后的 177 hp D-CAT 使用 `4335 × 1855 × 1685 mm`。([丰田媒体][2])
* `19298` 与 `19299` 均为改款前 BMW E91 Touring，发动机不同但物理外廓相同，复用同一尺寸组。BMW 官方资料给出的三维为 `4520 × 1817 × 1418 mm`。([宝马新闻部][3])
* `19301` 确认为 BMW E46 330Cd 双门敞篷车，而非 Coupe 或后续 E93 车身。([宝马经典][4])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：71
* READY 映射：104
* PENDING 映射：1
* 已确认尺寸组：60
* 尚未处理 Ktype：29
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19294	19294	SUV	Mercedes-Benz M-Class W164	W164	5		MEDIUM	已确认跨越2008年改款；AIRMATIC标准高度尚未闭合。	PENDING: AIRMATIC标准车高无法由已核来源唯一确定
19295	19295	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	HIGH	标准后挂备胎车身。	READY
19296	19296	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	HIGH	标准后挂备胎车身。	READY
19297_prefl	19297	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-T180-01	HIGH	T180无后挂备胎宽体外廓。	READY
19297_facelift	19297	SUV	Toyota RAV4 III facelift	XA30	5	EU-TOYOTA-RAV4-III-SUV-FACELIFT-WIDEBODY-01	HIGH	2010年改款后宽体外廓。	READY
19298	19298	Wagon	BMW 3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-01	HIGH		READY
19299	19299	Wagon	BMW 3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-01	HIGH		READY
19300	19300	Coupe	BMW Z4 E86	E86	2	EU-BMW-Z4-E86-COUPE-3-0SI-01	HIGH		READY
19301	19301	Convertible	BMW 3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	HIGH		READY
19302	19302	Sedan	Honda Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-IMA-01	HIGH		READY
19303	19303	Convertible	MINI Convertible R52	R52	2	EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	HIGH		READY
19304	19304	Hatchback	MINI Hatch R50 facelift	R50	3	EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	4395	1815	1685	Toyota RAV4 Gen3 official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen3-launch-pack-2006.pdf
EU-TOYOTA-RAV4-III-SUV-PREFL-T180-01	4315	1855	1685	Toyota RAV4 Gen3 official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen3-launch-pack-2006.pdf
EU-TOYOTA-RAV4-III-SUV-FACELIFT-WIDEBODY-01	4335	1855	1685	Auto-Data.net	https://www.auto-data.net/en/toyota-rav4-iii-xa30-facelift-2010-2.2-d-cat-177hp-4wd-37204
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418	BMW Group PressClub	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0012853EN_GB/the-new-bmw-3-series-touring?language=en_GB
EU-BMW-Z4-E86-COUPE-3-0SI-01	4091	1781	1268	Auto-Data.net	https://www.auto-data.net/en/bmw-z4-coupe-e86-3.0-si-265hp-9908
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372	BMW Group Classic;UltimateSpecs	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1122-1.bmw-330cd-convertible-e46.html;https://www.ultimatespecs.com/car-specs/BMW/152222/BMW-E46-LCI-3-Series-Cabrio-330Cd-.html
EU-HONDA-CIVIC-VIII-SEDAN-IMA-01	4488	1753	1430	Auto-Data.net	https://www.auto-data.net/en/honda-civic-viii-sedan-1.3-i-dsi-ima-110hp-hybrid-e-cvt-12214
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415	ADAC;AutoScout24	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mini/mini/r50-r53-r52/998063/;https://www.autoscout24.de/auto/technische-daten/mini/john-cooper-works-cabrio/mini-cabrio-13706/
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mini/930/Mini-Mini-R50-One-D-90.html
```

## 下一步优先处理

1. 只针对 `19294` 查明 ML 63 AMG 的标准行驶高度；若仍只能获得空气悬架范围，则保持 PENDING，不强行取范围端点或平均值。
2. 处理 `19305–19318`：PT Cruiser、Fiat Ducato、Bravo/Brava、BMW E65/E66、Vectra Caravan、Copen。
3. Ducato 按厢式车和底盘车分别确认轴距、车顶高度及长度分支，禁止用单一尺寸覆盖全部配置。
4. 随后处理剩余 `19319–19340`，集中复用 Doblo、Fabia Praktik、Astra GTC 等已出现或相邻车身组。

推进信号：CONTINUE

[1]: https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/ML-63-AMG-4MATIC-2006---2008.xhtml?oid=191401386 "ML 63 AMG 4MATIC, 2006 - 2008"
[2]: https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen3-launch-pack-2006.pdf?utm_source=chatgpt.com "THE NEW TOYOTA RAV4"
[3]: https://www.press.bmwgroup.com/united-kingdom/article/detail/T0012853EN_GB/the-new-bmw-3-series-touring?language=en_GB "The new BMW 3 Series Touring"
[4]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1122-1.bmw-330cd-convertible-e46.html "BMW 330Cd Convertible (E46)"


--- 发送 / 继续到 Round 6 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 6 / 下一步 ---
## 更新点

* 已解决 `19294`：ML 63 AMG 按 2008 年改款前后拆为两套物理外廓，不再保留原 PENDING 基础行。改款前采用 `4820 × 1951 × 1863 mm`，改款后采用 `4818 × 1952 × 1863 mm`，宽度均为不含后视镜口径。([汽车数据网][1])
* `19316 BMW 730 I, LI` 明确同时覆盖 E65 标准轴距和 E66 长轴距，必须拆成 `swb`、`lwb` 两条映射。([汽车数据网][2])
* `19317` 直接关联既有 Vectra C Caravan 尺寸组，本轮不重复输出该尺寸组。
* `19312–19313 Ducato` 已确认 Ktype 涉及多个轴距、车顶或底盘外廓，但尚不能闭合具体分支覆盖关系，因此保持 PENDING，不创建猜测性派生行。

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：80
* READY 映射：114
* PENDING 映射：2
* 已确认尺寸组：68
* 尚未处理 Ktype：20
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19294_prefl	19294	SUV	Mercedes-Benz M-Class W164	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-PREFL-01	HIGH	2008年改款前ML 63 AMG外廓。	READY
19294_facelift	19294	SUV	Mercedes-Benz M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-FACELIFT-01	HIGH	2008年改款后ML 63 AMG外廓。	READY
19305	19305	Wagon	Chrysler PT Cruiser facelift	PT	5	EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	HIGH		READY
19306	19306	Wagon	Chrysler PT Cruiser facelift	PT	5	EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	HIGH		READY
19312	19312	Van	Fiat Ducato II facelift	244			LOW	Kasten版本存在多个轴距及车顶高度，具体Ktype覆盖分支尚未闭合。	PENDING: 无法确认Ktype覆盖的轴距和车顶分支
19313	19313	Pickup	Fiat Ducato II facelift	244	2		LOW	平台及底盘驾驶室存在多个轴距和后部车架外廓，具体分支尚未闭合。	PENDING: 无法确认Ktype覆盖的底盘轴距分支
19314	19314	Hatchback	Fiat Bravo I	182	3	EU-FIAT-BRAVO-I-HATCHBACK-3D-01	HIGH		READY
19315	19315	Hatchback	Fiat Brava	182	5	EU-FIAT-BRAVA-HATCHBACK-5D-01	HIGH		READY
19316_swb	19316	Sedan	BMW 7 Series E65 facelift	E65	4	EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	HIGH	730i标准轴距分支。	READY
19316_lwb	19316	Sedan	BMW 7 Series E66 facelift	E66	4	EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	HIGH	730Li长轴距分支。	READY
19317	19317	Wagon	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Caravan五门旅行车车身。	READY
19318	19318	Convertible	Daihatsu Copen L8	L8	2	EU-DAIHATSU-COPEN-L8-CONVERTIBLE-2D-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-PREFL-01	4820	1951	1863	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-m-class-w164-amg-ml-63-v8-510hp-4matic-7g-tronic-amg-speedshift-12766
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-FACELIFT-01	4818	1952	1863	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1560395/mercedes-benz_ml_63_amg.html
EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	4290	1705	1600	Auto-Data.net	https://www.auto-data.net/en/chrysler-pt-cruiser-2.4-i-16v-150hp-14752
EU-FIAT-BRAVO-I-HATCHBACK-3D-01	4025	1755	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/2068010/fiat_bravo_jtd_100_sx.html
EU-FIAT-BRAVA-HATCHBACK-5D-01	4187	1741	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/2067995/fiat_brava_jtd_100_sx.html
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	5039	1902	1491	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-e65-facelift-2005-730i-258hp-steptronic-9710
EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	5179	1902	1484	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-long-e66-facelift-2005-730li-258hp-steptronic-9712
EU-DAIHATSU-COPEN-L8-CONVERTIBLE-2D-01	3395	1475	1245	Auto-Data.net	https://www.auto-data.net/en/daihatsu-copen-l8-1.3-i-16v-87hp-37
```

## 下一步优先处理

1. 集中处理剩余 `19319–19340`，优先复用 Astra H GTC、Fabia Praktik、BMW E46 Convertible 等既有尺寸组。
2. 批量闭合 Peugeot 307 Wagon、607、5008、Smart Forfour、Golf V、Golf Plus、Volvo S80 II、Lexus RX II 与 Citroën C3 I。
3. 单独聚类 Fiat Doblo 的乘用车、厢式车、标准顶及可能的加高顶外廓。
4. 最后返回 `19312–19313`，只解决 Ducato Ktype 实际覆盖的轴距与车顶分支，不重新核对已闭合车型。

推进信号：CONTINUE

[1]: https://www.auto-data.net/en/mercedes-benz-m-class-w164-amg-ml-63-v8-510hp-4matic-7g-tronic-amg-speedshift-12766 "Mercedes-Benz M-class (W164) AMG ML 63 V8 (510 Hp) 4MATIC 7G-TRONIC AMG SPEEDSHIFT | Technical specs, data, fuel consumption, Dimensions"
[2]: https://www.auto-data.net/en/bmw-7-series-e65-facelift-2005-730i-258hp-steptronic-9710?utm_source=chatgpt.com "BMW 7 Series (E65, facelift 2005) 730i (258 Hp) Steptronic"


--- 发送 / 继续到 Round 7 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 7 / 下一步 ---
## 更新点

* 已处理剩余 20 个 Ktype，本轮新增 **23 条 READY 映射、11 个尺寸组**。
* `19319` 的 Ktype 专属资料明确对应 `Peugeot 307 Break (3E) 2.0 HDi 110` Phase I。虽然上游结束日期写到 2009 年，但不能因此派生改款后车身。([Meyer Motoren][1])
* `19320` 的 155 kW／211 hp 版本对应 Peugeot 607 Phase II，直接关联改款后尺寸组，不创建不存在的改款前派生行。([汽车数据网][2])
* Golf Plus 的 Ktype 跨越 V Plus 与 VI Plus，两阶段车长分别为 4206 mm、4204 mm，因此拆成两个物理分支。([汽车数据网][3])
* `19324–19330` 均落在 Fiat Doblò 223 改款后标准短轴外廓，发动机和乘用／厢式分类不重复建组。([汽车数据网][4])
* 当前仅剩 `19312–19313` 两个 PENDING。Ducato 的同一 Ktype/KBA 覆盖多种车长和车高，现有资料可见 4381 mm、5181 mm、5599 mm 等不同外廓，不能强行归为单一尺寸组。([autoscout24.de][5])

## 当前批次进度

* 输入 Ktype：100
* 已处理 Ktype：100
* READY 映射：137
* PENDING 映射：2
* 已确认尺寸组：79
* 尚未处理 Ktype：0
* 当前批次尚未完成

## 本轮新增/修改的 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19319	19319	Wagon	Peugeot 307 Phase I	3E	5	EU-PEUGEOT-307-WAGON-PREFL-01	HIGH	Ktype限定Phase I Break外廓。	READY
19320	19320	Sedan	Peugeot 607 Phase II	Z8	4	EU-PEUGEOT-607-SEDAN-FACELIFT-01	HIGH	211 hp版本对应Phase II外廓。	READY
19322	19322	MPV	Peugeot 5008 I		5	EU-PEUGEOT-5008-I-MPV-01	HIGH		READY
19323	19323	Hatchback	Smart Forfour W454	W454	5	EU-SMART-FORFOUR-W454-HATCHBACK-5D-01	HIGH		READY
19324	19324	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19325	19325	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19326	19326	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19327	19327	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19328	19328	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19329	19329	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19330	19330	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19331_prefl	19331	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	2007年改款前三门GTC外廓。	READY
19331_facelift	19331	Hatchback	Opel Astra H GTC facelift	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	2007年改款后三门GTC外廓。	READY
19332_3dr	19332	Hatchback	Volkswagen Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-01	HIGH	三门分支。	READY
19332_5dr	19332	Hatchback	Volkswagen Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-01	HIGH	五门分支。	READY
19333_prefl	19333	MPV	Volkswagen Golf V Plus	5M1	5	EU-VW-GOLF-PLUS-V-MPV-PREFL-01	HIGH	Golf V Plus外廓。	READY
19333_facelift	19333	MPV	Volkswagen Golf VI Plus	5M1	5	EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	HIGH	2008年改款后Golf VI Plus外廓。	READY
19334	19334	Convertible	BMW 3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	HIGH		READY
19335	19335	Van	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	Praktik商用版本采用改款前Combi物理外廓。	READY
19336	19336	Sedan	Volvo S80 II	AS	4	EU-VOLVO-S80-II-SEDAN-01	HIGH		READY
19337	19337	Sedan	Volvo S80 II	AS	4	EU-VOLVO-S80-II-SEDAN-01	HIGH		READY
19339	19339	SUV	Lexus RX II	XU30	5	EU-LEXUS-RX-II-SUV-350-AWD-01	HIGH		READY
19340	19340	Hatchback	Citroën C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	HIGH		READY
```

## 本轮首次创建/修正的 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-PEUGEOT-307-WAGON-PREFL-01	4419	1757	1544	Auto-Data.net	https://www.auto-data.net/en/peugeot-307-station-wagon-generation-1226
EU-PEUGEOT-607-SEDAN-FACELIFT-01	4902	1800	1442	Auto-Data.net	https://www.auto-data.net/en/peugeot-607-phase-ii-2004-3.0-v6-211hp-tiptronic-45877
EU-PEUGEOT-5008-I-MPV-01	4529	1888	1647	Auto-Data.net	https://www.auto-data.net/en/peugeot-5008-model-1953
EU-SMART-FORFOUR-W454-HATCHBACK-5D-01	3752	1684	1450	Auto-Data.net	https://www.auto-data.net/en/smart-forfour-w454-1.1i-64hp-14856
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818	Auto-Data.net	https://www.auto-data.net/en/fiat-doblo-i-223-facelift-2005-generation-10488
EU-VW-GOLF-V-HATCHBACK-01	4204	1759	1485	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-3-door-2.0-tdi-16v-140hp-8633;https://www.auto-data.net/en/volkswagen-golf-v-5-door-2.0-tdi-8v-140hp-dpf-51672
EU-VW-GOLF-PLUS-V-MPV-PREFL-01	4206	1759	1592	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/volvo-s80-ii-2.4-d5-185hp-9364;https://www.auto-data.net/en/volvo-s80-ii-generation-1947
EU-LEXUS-RX-II-SUV-350-AWD-01	4740	1845	1705	Auto-Data.net	https://www.auto-data.net/en/lexus-rx-ii-350-4wd-276hp-5892
EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	3860	1667	1510	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.6-hdi-90hp-15091
```

## 下一步优先处理

1. `19312`：从 Ducato 244 官方规格矩阵中确定该 Ktype 覆盖的全部厢式车轴距和车顶分支，分别闭合三维。
2. `19313`：确定平台／底盘驾驶室对应的轴距、驾驶室形式和原厂后部外廓边界，不以改装货箱尺寸代替原厂尺寸。
3. 两个 PENDING 消除后，下一轮只执行一次引用闭合、唯一性和文件链接机械检查，随后直接输出 COMPLETE。

推进信号：CONTINUE

[1]: https://www.meyermotoren.de/en/fahrzeuge/19319/peugeot/307_break_3e_/2_0_hdi_110 "https://www.meyermotoren.de/en/fahrzeuge/19319/peugeot/307_break_3e_/2_0_hdi_110"
[2]: https://www.auto-data.net/en/peugeot-607-phase-ii-2004-3.0-v6-211hp-tiptronic-45877 "https://www.auto-data.net/en/peugeot-607-phase-ii-2004-3.0-v6-211hp-tiptronic-45877"
[3]: https://www.auto-data.net/en/volkswagen-golf-v-plus-generation-1875 "https://www.auto-data.net/en/volkswagen-golf-v-plus-generation-1875"
[4]: https://www.auto-data.net/en/fiat-doblo-i-223-facelift-2005-generation-10488 "https://www.auto-data.net/en/fiat-doblo-i-223-facelift-2005-generation-10488"
[5]: https://www.autoscout24.de/auto/technische-daten/fiat/ducato/ducato-15-244-5ga-0-2004-2006-transporter-diesel/ "https://www.autoscout24.de/auto/technische-daten/fiat/ducato/ducato-15-244-5ga-0-2004-2006-transporter-diesel/"


--- 发送 / 继续到 Round 8 ---
继续当前批次并采用缓存优先模式。尺寸组只在首次创建或纠错时完整核对一次三维和来源；后续 Ktype 只判断关联哪个现有 DIMENSION_GROUP_ID，不重复抓取，不输出缓存来源或匹配理由。仍有 PENDING 时，CONTINUE 轮仅输出：1) 更新点；2) 当前批次进度；3) 本轮新增/修改的 Ktype 映射 TSV（无变化写“无”）；4) 本轮首次创建/修正的 DIMENSION_GROUP TSV（复用既有组不重复输出，无变化写“无”）；5) 下一步优先处理。若当前或上一轮进度已经是 PENDING=0，本轮不要继续检索或再次输出 CONTINUE，必须立刻汇总并输出两张最终完整 TSV、两个任务指定 sandbox 下载链接和“推进信号：COMPLETE”。执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。Ktype 映射 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus。另需维护完整 DIMENSION_GROUP TSV，表头固定为：DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL。缺少任一张表、任一映射引用的尺寸组，或尺寸组字段不完整时不得 COMPLETE。不要输出子车系匹配表。
【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- all_101-200_ktype_dimension_mapping_final.tsv
- all_101-200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。


--- Round 8 / 下一步 ---
## 更新点

* 最后两个阻塞项已闭合：`19312` 拆分为 Ducato 244 厢式车的轴距、车顶及 MAXI 外廓；`19313` 拆分为标准 15 系列和 MAXI 的底盘驾驶室外廓。Ktype 车型边界与各分支三维由对应 Ktype 资料及 Fiat 官方手册闭合。([汽车手册在线][1])
* 已完成机械检查：表头固定、154 个 `id` 唯一、96 个 `DIMENSION_GROUP_ID` 唯一、所有映射引用闭合、无孤立尺寸组、三维及来源均非空。
* 当前批次 `PENDING=0`，进入最终完整快照。

## 当前批次进度

* 输入 Ktype：100
* READY 映射：154
* PENDING 映射：0
* 已确认尺寸组：96
* 映射引用缺失：0
* 孤立尺寸组：0
* 当前批次已完成

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
19234	19234	Sedan	Audi A6 C6	4F2	4	EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	HIGH	120 kW版本限定改款前外廓。	READY
19235	19235	Wagon	Audi A6 C6	4F5	5	EU-AUDI-A6-C6-WAGON-5D-PREFL-01	HIGH	120 kW版本限定改款前外廓。	READY
19236	19236	MPV	Volkswagen Caddy III	2K	5	EU-VW-CADDY-III-MPV-5D-SWB-01	HIGH	短轴乘用型车身。	READY
19237	19237	Hatchback	Volkswagen New Beetle I facelift	9C1	3	EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	HIGH		READY
19238	19238	Convertible	Volkswagen New Beetle I facelift	1Y7	2	EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
19239	19239	Convertible	Audi TT 8N facelift	8N9	2	EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	HIGH		READY
19240	19240	Hatchback	Honda Civic VIII	FK1	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19241	19241	Hatchback	Honda Civic VIII	FK2	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19242	19242	Hatchback	Honda Civic VIII	FK3	5	EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	HIGH		READY
19243_3dr	19243	Hatchback	Toyota Aygo I	AB10	3	EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	HIGH	三门分支。	READY
19243_5dr	19243	Hatchback	Toyota Aygo I	AB10	5	EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	HIGH	五门分支。	READY
19244	19244	Sedan	Mazda 6 I facelift	GG1	4	EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	HIGH	MPS四门轿车车身。	READY
19245_prefl	19245	MPV	Toyota Corolla Verso II	AR10	5	EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	HIGH	2007年改款前车身。	READY
19245_facelift	19245	MPV	Toyota Corolla Verso II facelift	AR10	5	EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	HIGH	2007年改款后车身。	READY
19246_prefl	19246	Hatchback	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	HIGH	2006年改款前车身。	READY
19246_facelift	19246	Hatchback	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	HIGH	2006年改款后车身。	READY
19247_prefl	19247	Sedan	Toyota Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	HIGH	2006年改款前车身。	READY
19247_facelift	19247	Sedan	Toyota Avensis II facelift	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	HIGH	2006年改款后车身。	READY
19248_prefl	19248	Wagon	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	HIGH	2006年改款前车身。	READY
19248_facelift	19248	Wagon	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	HIGH	2006年改款后车身。	READY
19249_prefl	19249	Hatchback	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	HIGH	2006年改款前车身。	READY
19249_facelift	19249	Hatchback	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	HIGH	2006年改款后车身。	READY
19250_prefl	19250	Sedan	Toyota Avensis II	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	HIGH	2006年改款前车身。	READY
19250_facelift	19250	Sedan	Toyota Avensis II facelift	T25	4	EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	HIGH	2006年改款后车身。	READY
19251_prefl	19251	Wagon	Toyota Avensis II	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	HIGH	2006年改款前车身。	READY
19251_facelift	19251	Wagon	Toyota Avensis II facelift	T25	5	EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	HIGH	2006年改款后车身。	READY
19252	19252	Hatchback	Toyota Corolla IX	E12	3	EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	HIGH	TS Compressor三门车身。	READY
19253_3dr	19253	Hatchback	Volkswagen Polo IV facelift	9N3	3	EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	HIGH	GTI三门分支。	READY
19253_5dr	19253	Hatchback	Volkswagen Polo IV facelift	9N3	5	EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	HIGH	GTI五门分支。	READY
19254_3dr_prefl	19254	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19254_5dr_prefl	19254	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19254_3dr_facelift	19254	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19254_5dr_facelift	19254	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19255_3dr_prefl	19255	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19255_5dr_prefl	19255	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19255_3dr_facelift	19255	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19255_5dr_facelift	19255	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19256_3dr_prefl	19256	Hatchback	Toyota Yaris II	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19256_5dr_prefl	19256	Hatchback	Toyota Yaris II	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19256_3dr_facelift	19256	Hatchback	Toyota Yaris II facelift	XP90	3	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	三门2009年改款后车身。	READY
19256_5dr_facelift	19256	Hatchback	Toyota Yaris II facelift	XP90	5	EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	HIGH	五门2009年改款后车身。	READY
19257	19257	Wagon	Mercedes-Benz C-Class S203 facelift	S203	5	EU-MERCEDES-BENZ-C-CLASS-S203-WAGON-FACELIFT-01	HIGH		READY
19258	19258	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19259	19259	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19260	19260	Convertible	BMW Z4 E85 LCI	E85	2	EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	HIGH		READY
19261	19261	MPV	Opel Zafira B	A05	5	EU-OPEL-ZAFIRA-B-MPV-OPC-01	HIGH		READY
19262	19262	MPV	Ford Focus C-MAX I		5	EU-FORD-FOCUS-C-MAX-I-MPV-PREFL-01	HIGH		READY
19263_prefl	19263	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-PREFL-01	HIGH	2006年改款前车身。	READY
19263_facelift	19263	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-FACELIFT-01	HIGH	2006年改款后车身。	READY
19264_3dr_prefl	19264	Hatchback	Ford Focus II		3	EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	HIGH	三门改款前车身。	READY
19264_5dr_prefl	19264	Hatchback	Ford Focus II		5	EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	HIGH	五门改款前车身。	READY
19264_3dr_facelift	19264	Hatchback	Ford Focus II facelift		3	EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH	三门改款后车身。	READY
19264_5dr_facelift	19264	Hatchback	Ford Focus II facelift		5	EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	HIGH	五门改款后车身。	READY
19265_prefl	19265	Wagon	Ford Focus II		5	EU-FORD-FOCUS-II-WAGON-PREFL-01	HIGH	改款前旅行车。	READY
19265_facelift	19265	Wagon	Ford Focus II facelift		5	EU-FORD-FOCUS-II-WAGON-FACELIFT-01	HIGH	改款后旅行车。	READY
19266_prefl	19266	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC车身。	READY
19266_facelift	19266	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC车身。	READY
19267_prefl	19267	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC车身。	READY
19267_facelift	19267	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC车身。	READY
19268	19268	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19269	19269	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19270_prefl	19270	Wagon	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	2004年改款前Combi外廓。	READY
19270_facelift	19270	Wagon	Skoda Fabia I facelift	6Y5	5	EU-SKODA-FABIA-I-COMBI-FACELIFT-01	HIGH	2004年改款后Combi外廓。	READY
19271_prefl	19271	Van	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	Praktik商用车采用改款前Combi外廓。	READY
19271_facelift	19271	Van	Skoda Fabia I facelift	6Y5	5	EU-SKODA-FABIA-I-COMBI-FACELIFT-01	HIGH	Praktik商用车采用改款后Combi外廓。	READY
19272	19272	Convertible	Saab 9-3 II		2	EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	HIGH	250 hp版本限定改款前车身。	READY
19273	19273	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19274_prefl	19274	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19274_facelift	19274	MPV	Skoda Roomster I facelift		5	EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	HIGH	2010年改款后车身。	READY
19275	19275	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	1.6汽油版本限定2010年改款前车身。	READY
19276	19276	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19277	19277	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19278	19278	MPV	Skoda Roomster I		5	EU-SKODA-ROOMSTER-I-MPV-PREFL-01	HIGH	改款前车身。	READY
19279	19279	Van	Opel Corsa C facelift		3	EU-OPEL-CORSA-C-VAN-FACELIFT-01	MEDIUM	三门商用厢式车身。	READY
19280	19280	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19281	19281	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19282	19282	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19283	19283	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19284	19284	Wagon	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Caravan五门旅行车车身。	READY
19285	19285	Sedan	Opel Vectra C facelift		4	EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	HIGH	四门轿车车身。	READY
19286	19286	Hatchback	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	HIGH	CC五门掀背车身。	READY
19287_prefl	19287	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	2007年改款前三门GTC外廓。	READY
19287_facelift	19287	Hatchback	Opel Astra H GTC facelift	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	2007年改款后三门GTC外廓。	READY
19288	19288	Hatchback	Alfa Romeo Giulietta Type 940	940	5	EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	HIGH		READY
19289	19289	MPV	Opel Meriva A facelift		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	2006年改款后车身。	READY
19290_prefl	19290	MPV	Opel Meriva A		5	EU-OPEL-MERIVA-A-MPV-PREFL-01	HIGH	2006年改款前车身。	READY
19290_facelift	19290	MPV	Opel Meriva A facelift		5	EU-OPEL-MERIVA-A-MPV-FACELIFT-01	HIGH	2006年改款后车身。	READY
19291_prefl	19291	Wagon	Mercedes-Benz E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E320-CDI-4MATIC-PREFL-01	HIGH	2006年改款前E 320 CDI 4MATIC旅行车。	READY
19291_facelift	19291	Wagon	Mercedes-Benz E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC旅行车。	READY
19292_prefl	19292	Wagon	Mercedes-Benz E-Class S211	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E350-4MATIC-PREFL-01	HIGH	2006年改款前E 350 4MATIC旅行车。	READY
19292_facelift	19292	Wagon	Mercedes-Benz E-Class S211 facelift	S211	5	EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC旅行车。	READY
19293_prefl	19293	Sedan	Mercedes-Benz E-Class W211	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	HIGH	2006年改款前4MATIC轿车。	READY
19293_facelift	19293	Sedan	Mercedes-Benz E-Class W211 facelift	W211	4	EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	HIGH	2006年改款后4MATIC轿车。	READY
19294_prefl	19294	SUV	Mercedes-Benz M-Class W164	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-PREFL-01	HIGH	2008年改款前ML 63 AMG外廓。	READY
19294_facelift	19294	SUV	Mercedes-Benz M-Class W164 facelift	W164	5	EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-FACELIFT-01	HIGH	2008年改款后ML 63 AMG外廓。	READY
19295	19295	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	HIGH	标准后挂备胎车身。	READY
19296	19296	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	HIGH	标准后挂备胎车身。	READY
19297_prefl	19297	SUV	Toyota RAV4 III	XA30	5	EU-TOYOTA-RAV4-III-SUV-PREFL-T180-01	HIGH	T180无后挂备胎宽体外廓。	READY
19297_facelift	19297	SUV	Toyota RAV4 III facelift	XA30	5	EU-TOYOTA-RAV4-III-SUV-FACELIFT-WIDEBODY-01	HIGH	2010年改款后宽体外廓。	READY
19298	19298	Wagon	BMW 3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-01	HIGH		READY
19299	19299	Wagon	BMW 3 Series E91	E91	5	EU-BMW-3-SERIES-E91-WAGON-PREFL-01	HIGH		READY
19300	19300	Coupe	BMW Z4 E86	E86	2	EU-BMW-Z4-E86-COUPE-3-0SI-01	HIGH		READY
19301	19301	Convertible	BMW 3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	HIGH		READY
19302	19302	Sedan	Honda Civic VIII Sedan		4	EU-HONDA-CIVIC-VIII-SEDAN-IMA-01	HIGH		READY
19303	19303	Convertible	MINI Convertible R52	R52	2	EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	HIGH		READY
19304	19304	Hatchback	MINI Hatch R50 facelift	R50	3	EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	HIGH		READY
19305	19305	Wagon	Chrysler PT Cruiser facelift	PT	5	EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	HIGH		READY
19306	19306	Wagon	Chrysler PT Cruiser facelift	PT	5	EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	HIGH		READY
19312_swb_lowroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	HIGH	15系列短轴低顶外廓。	READY
19312_swb_highroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	HIGH	15系列短轴高顶外廓。	READY
19312_mwb_lowroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	HIGH	15系列中轴低顶外廓。	READY
19312_mwb_highroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	HIGH	15系列中轴高顶外廓。	READY
19312_mwb_superhighroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	HIGH	15系列中轴超高顶外廓。	READY
19312_mwb_maxi_lowroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	HIGH	MAXI中轴低顶外廓。	READY
19312_mwb_maxi_highroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	HIGH	MAXI中轴高顶外廓。	READY
19312_mwb_maxi_superhighroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	HIGH	MAXI中轴超高顶外廓。	READY
19312_lwb_highroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	HIGH	长轴高顶外廓。	READY
19312_lwb_superhighroof	19312	Van	Fiat Ducato II facelift	244		EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	HIGH	长轴超高顶外廓。	READY
19313_swb	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	HIGH	15系列短轴底盘驾驶室。	READY
19313_mwb	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	HIGH	15系列中轴底盘驾驶室。	READY
19313_mwb_maxi	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	HIGH	MAXI中轴底盘驾驶室。	READY
19313_lwb	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	HIGH	15系列长轴底盘驾驶室。	READY
19313_lwb_maxi	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	HIGH	MAXI长轴底盘驾驶室。	READY
19313_xlwb	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	HIGH	15系列4050 mm轴距底盘驾驶室。	READY
19313_xlwb_maxi	19313	Pickup	Fiat Ducato II facelift	244	2	EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	HIGH	MAXI 4050 mm轴距底盘驾驶室。	READY
19314	19314	Hatchback	Fiat Bravo I	182	3	EU-FIAT-BRAVO-I-HATCHBACK-3D-01	HIGH		READY
19315	19315	Hatchback	Fiat Brava	182	5	EU-FIAT-BRAVA-HATCHBACK-5D-01	HIGH		READY
19316_swb	19316	Sedan	BMW 7 Series E65 facelift	E65	4	EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	HIGH	730i标准轴距分支。	READY
19316_lwb	19316	Sedan	BMW 7 Series E66 facelift	E66	4	EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	HIGH	730Li长轴距分支。	READY
19317	19317	Wagon	Opel Vectra C facelift		5	EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	HIGH	Caravan五门旅行车车身。	READY
19318	19318	Convertible	Daihatsu Copen L8	L8	2	EU-DAIHATSU-COPEN-L8-CONVERTIBLE-2D-01	HIGH		READY
19319	19319	Wagon	Peugeot 307 Phase I	3E	5	EU-PEUGEOT-307-WAGON-PREFL-01	HIGH	Ktype限定Phase I Break外廓。	READY
19320	19320	Sedan	Peugeot 607 Phase II	Z8	4	EU-PEUGEOT-607-SEDAN-FACELIFT-01	HIGH	211 hp版本对应Phase II外廓。	READY
19322	19322	MPV	Peugeot 5008 I		5	EU-PEUGEOT-5008-I-MPV-01	HIGH		READY
19323	19323	Hatchback	Smart Forfour W454	W454	5	EU-SMART-FORFOUR-W454-HATCHBACK-5D-01	HIGH		READY
19324	19324	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19325	19325	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19326	19326	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19327	19327	MPV	Fiat Doblò I facelift	223	5	EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	HIGH		READY
19328	19328	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19329	19329	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19330	19330	Van	Fiat Doblò I facelift	223		EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	MEDIUM	输入分类兼含厢式和乘用车身，采用相同标准短轴外廓。	READY
19331_prefl	19331	Hatchback	Opel Astra H GTC	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	HIGH	2007年改款前三门GTC外廓。	READY
19331_facelift	19331	Hatchback	Opel Astra H GTC facelift	L08	3	EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	HIGH	2007年改款后三门GTC外廓。	READY
19332_3dr	19332	Hatchback	Volkswagen Golf V	1K1	3	EU-VW-GOLF-V-HATCHBACK-01	HIGH	三门分支。	READY
19332_5dr	19332	Hatchback	Volkswagen Golf V	1K1	5	EU-VW-GOLF-V-HATCHBACK-01	HIGH	五门分支。	READY
19333_prefl	19333	MPV	Volkswagen Golf V Plus	5M1	5	EU-VW-GOLF-PLUS-V-MPV-PREFL-01	HIGH	Golf V Plus外廓。	READY
19333_facelift	19333	MPV	Volkswagen Golf VI Plus	5M1	5	EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	HIGH	2008年改款后Golf VI Plus外廓。	READY
19334	19334	Convertible	BMW 3 Series E46 facelift	E46	2	EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	HIGH		READY
19335	19335	Van	Skoda Fabia I	6Y5	5	EU-SKODA-FABIA-I-COMBI-PREFL-01	HIGH	Praktik商用版本采用改款前Combi物理外廓。	READY
19336	19336	Sedan	Volvo S80 II	AS	4	EU-VOLVO-S80-II-SEDAN-01	HIGH		READY
19337	19337	Sedan	Volvo S80 II	AS	4	EU-VOLVO-S80-II-SEDAN-01	HIGH		READY
19339	19339	SUV	Lexus RX II	XU30	5	EU-LEXUS-RX-II-SUV-350-AWD-01	HIGH		READY
19340	19340	Hatchback	Citroën C3 I facelift		5	EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	HIGH		READY
```

[下载 Ktype 映射表](sandbox:/mnt/data/all_101-200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-AUDI-A6-C6-SEDAN-4D-PREFL-01	4916	1855	1459	Auto-Data.net	https://www.auto-data.net/en/audi-a6-4f-c6-2.7-tdi-v6-180hp-quattro-tiptronic-26845
EU-AUDI-A6-C6-WAGON-5D-PREFL-01	4933	1855	1463	Auto-Data.net	https://www.auto-data.net/en/audi-a6-avant-4f-c6-2.7-tdi-v6-180hp-quattro-tiptronic-4677
EU-VW-CADDY-III-MPV-5D-SWB-01	4405	1802	1833	Auto-Data.net	https://www.auto-data.net/en/volkswagen-caddy-iii-1.9-tdi-75hp-28303
EU-VW-NEW-BEETLE-I-HATCHBACK-3D-FACELIFT-01	4129	1721	1498	Auto-Data.net	https://www.auto-data.net/en/volkswagen-new-beetle-9c-facelift-2005-1.9-tdi-105hp-28079
EU-VW-NEW-BEETLE-I-CONVERTIBLE-2D-FACELIFT-01	4129	1721	1502	Auto-Data.net	https://www.auto-data.net/en/volkswagen-new-beetle-convertible-facelift-2005-1.9-tdi-105hp-28151
EU-AUDI-TT-8N-CONVERTIBLE-2D-FACELIFT-01	4041	1764	1349	Auto-Data.net	https://www.auto-data.net/en/audi-tt-roadster-8n-facelift-2000-1.8-t-163hp-4868
EU-HONDA-CIVIC-VIII-HATCHBACK-5D-01	4255	1765	1460	Auto-Data.net	https://www.auto-data.net/en/honda-civic-viii-hatchback-5d-generation-2621
EU-TOYOTA-AYGO-I-HATCHBACK-PREFL-01	3405	1615	1465	Auto-Data.net;Toyota UK Media Site	https://www.auto-data.net/en/toyota-aygo-generation-913;https://media.toyota.co.uk/aygos-a-go-go/
EU-MAZDA-6-I-SEDAN-MPS-FACELIFT-01	4765	1780	1430	Auto-Data.net	https://www.auto-data.net/en/mazda-6-i-sedan-typ-gg-gy-gg1-facelift-2005-mps-2.3-260hp-awd-30762
EU-TOYOTA-COROLLA-VERSO-II-MPV-PREFL-01	4360	1770	1620	Toyota Corolla Verso 2005 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2005-Toyota-Corolla-Verso-UK.pdf
EU-TOYOTA-COROLLA-VERSO-II-MPV-FACELIFT-01	4370	1770	1625	Auto-Data.net	https://www.auto-data.net/en/toyota-corolla-verso-ii-ar10-facelift-2007-generation-815
EU-TOYOTA-AVENSIS-II-HATCHBACK-PREFL-01	4630	1760	1480	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-HATCHBACK-FACELIFT-01	4645	1760	1485	Toyota Avensis Gen2 MC official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf
EU-TOYOTA-AVENSIS-II-SEDAN-PREFL-01	4630	1760	1480	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-SEDAN-FACELIFT-01	4645	1760	1485	Toyota Avensis Gen2 MC official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf
EU-TOYOTA-AVENSIS-II-WAGON-PREFL-01	4700	1760	1525	Toyota UK Media Site	https://media.toyota.co.uk/the-new-toyota-avensis-a-superior-quality-experience/
EU-TOYOTA-AVENSIS-II-WAGON-FACELIFT-01	4715	1760	1525	Toyota Avensis Gen2 MC official launch pack;Auto-Data.net	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Avensis-Gen2-MC-launch-pack-2006.pdf;https://www.auto-data.net/en/toyota-avensis-ii-wagon-generation-901
EU-TOYOTA-COROLLA-IX-HATCHBACK-3D-COMPRESSOR-01	4200	1710	1440	Toyota Corolla 2006 UK brochure	https://xr793.com/wp-content/uploads/2022/12/2006-Toyota-Corolla-UK.pdf
EU-VW-POLO-IV-HATCHBACK-3D-FACELIFT-GTI-01	3916	1650	1459	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-1.8-150hp-3-d-8428
EU-VW-POLO-IV-HATCHBACK-5D-FACELIFT-GTI-01	3897	1650	1465	Auto-Data.net	https://www.auto-data.net/en/volkswagen-polo-iv-9n-facelift-2005-gti-1.8-150hp-5-d-8429
EU-TOYOTA-YARIS-II-HATCHBACK-PREFL-01	3750	1695	1530	Toyota Gen2 Yaris official archive press pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/Gen2-Yaris-archive-press-pack.pdf
EU-TOYOTA-YARIS-II-HATCHBACK-FACELIFT-01	3785	1695	1530	Toyota UK Media Site 2009 Yaris specifications	https://media.toyota.co.uk/2009-toyota-yaris-less-is-so-much-more/
EU-MERCEDES-BENZ-C-CLASS-S203-WAGON-FACELIFT-01	4541	1728	1465	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-c-class-t-modell-s203-facelift-2004-c-320-cdi-v6-224hp-7g-tronic-40945
EU-BMW-Z4-E85-CONVERTIBLE-FACELIFT-01	4091	1781	1299	Auto-Data.net	https://www.auto-data.net/en/bmw-z4-e85-lci-facelift-2006-2.5i-177hp-9903
EU-OPEL-ZAFIRA-B-MPV-OPC-01	4467	1801	1645	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/opel-zafira-b-opc-2.0i-16v-turbo-240hp-2597;https://www.auto-data.net/en/opel-zafira-b-facelift-2008-opc-2.0i-16v-turbo-240hp-26232
EU-FORD-FOCUS-C-MAX-I-MPV-PREFL-01	4333	1825	1595	Auto-Data.net	https://www.auto-data.net/fr/ford-focus-c-max-i-1.8-16v-125hp-flexfuel-37914
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-PREFL-01	4818	1822	1431	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-e-420-cdi-v8-314hp-7g-tronic-12900
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-E420-FACELIFT-01	4856	1822	1465	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-w211-facelift-2006-e-420-cdi-v8-314hp-7g-tronic-37048
EU-FORD-FOCUS-II-HATCHBACK-PREFL-01	4342	1840	1497	Auto-Data.net	https://www.auto-data.net/en/ford-focus-ii-hatchback-1.8-i-16v-125hp-7320
EU-FORD-FOCUS-II-HATCHBACK-FACELIFT-01	4337	1839	1500	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/969140/ford_focus_1_8_flexifuel_style.html
EU-FORD-FOCUS-II-WAGON-PREFL-01	4472	1840	1501	Auto-Data.net	https://www.auto-data.net/en/ford-focus-turnier-ii-1.8-i-16v-125hp-7348
EU-FORD-FOCUS-II-WAGON-FACELIFT-01	4468	1839	1503	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/969230/ford_focus_turnier_1_8_flexifuel_titanium.html
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-PREFL-01	4818	1822	1452	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mercedes-Benz/2581/Mercedes-Benz-E-Class-%28W211%29-280-4Matic.html
EU-MERCEDES-BENZ-E-CLASS-W211-SEDAN-4MATIC-FACELIFT-01	4856	1822	1499	Automobile-Catalog	https://www.automobile-catalog.com/car/2008/1542020/mercedes-benz_e_280_4matic.html
EU-OPEL-VECTRA-C-HATCHBACK-FACELIFT-01	4611	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-cc-facelift-2005-1.8i-16v-140hp-2248
EU-SKODA-FABIA-I-COMBI-PREFL-01	4222	1646	1452	Auto-Data.net;Škoda Fabia Praktik historical technical sheet	https://www.auto-data.net/fr/skoda-fabia-i-combi-6y-1.4-16v-75hp-14164;https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SKODA-FABIA-I-COMBI-FACELIFT-01	4232	1646	1452	Auto-Data.net;Škoda Fabia Praktik historical technical sheet	https://www.auto-data.net/en/skoda-fabia-i-combi-6y-facelift-2004-1.2-htp-64hp-14159;https://www.allcarcentral.com/Skoda_pdf/Skoda_Fabia_Praktik_2002_2006.pdf
EU-SAAB-9-3-II-CONVERTIBLE-PREFL-01	4635	1762	1434	Auto-Data.net	https://www.auto-data.net/en/saab-9-3-convertible-ii-2.8t-v6-250hp-11952
EU-SKODA-ROOMSTER-I-MPV-PREFL-01	4205	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-1.2-12v-64hp-14270
EU-SKODA-ROOMSTER-I-MPV-FACELIFT-01	4214	1684	1607	Auto-Data.net	https://www.auto-data.net/en/skoda-roomster-facelift-2010-1.4-86hp-19232
EU-OPEL-CORSA-C-VAN-FACELIFT-01	3839	1646	1440	MotorEU;UltimateSpecs	https://motoreu.com/opel-corsa-van-1.2-twinport-mpg-fuel-consumption-technical-specifications-168768;https://www.ultimatespecs.com/car-specs/Opel/1121/Opel-Corsa-C-12-16v.html
EU-OPEL-VECTRA-C-SEDAN-FACELIFT-01	4611	1798	1460	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-facelift-2005-1.8i-16v-140hp-2219
EU-OPEL-VECTRA-C-WAGON-FACELIFT-01	4839	1798	1500	Auto-Data.net	https://www.auto-data.net/en/opel-vectra-c-caravan-facelift-2005-1.9-cdti-120hp-26130
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-PREFL-01	4290	1753	1415	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-gtc-1.9-cdti-120hp-2381
EU-OPEL-ASTRA-H-GTC-HATCHBACK-3D-FACELIFT-01	4290	1753	1435	Auto-Data.net	https://www.auto-data.net/en/opel-astra-h-gtc-facelift-2007-1.9-cdti-ecotec-120hp-automatic-47425
EU-ALFA-ROMEO-GIULIETTA-940-HATCHBACK-5D-01	4351	1798	1465	Auto-Data.net	https://www.auto-data.net/en/alfa-romeo-giulietta-type-940-1.4-120hp-lpg-18680
EU-OPEL-MERIVA-A-MPV-FACELIFT-01	4052	1694	1624	Auto-Data.net	https://www.auto-data.net/en/opel-meriva-a-facelift-2006-1.6i-16v-105hp-2521
EU-OPEL-MERIVA-A-MPV-PREFL-01	4042	1694	1624	Auto-Data.net	https://www.auto-data.net/en/opel-meriva-a-generation-561
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E320-CDI-4MATIC-PREFL-01	4847	1822	1499	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-320-cdi-v6-224hp-4matic-5g-tronic-51989
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-4MATIC-FACELIFT-01	4888	1822	1506	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-320-cdi-v6-224hp-4matic-5g-tronic-37050;https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-facelift-2006-e-350-v6-272hp-4matic-5g-tronic-37052
EU-MERCEDES-BENZ-E-CLASS-S211-WAGON-E350-4MATIC-PREFL-01	4850	1822	1495	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-e-class-t-modell-s211-e-350-272hp-4matic-5g-tronic-12930
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-PREFL-01	4820	1951	1863	Auto-Data.net	https://www.auto-data.net/en/mercedes-benz-m-class-w164-amg-ml-63-v8-510hp-4matic-7g-tronic-amg-speedshift-12766
EU-MERCEDES-BENZ-M-CLASS-W164-SUV-ML63-FACELIFT-01	4818	1952	1863	Automobile-Catalog	https://www.automobile-catalog.com/car/2009/1560395/mercedes-benz_ml_63_amg.html
EU-TOYOTA-RAV4-III-SUV-PREFL-SPARE-01	4395	1815	1685	Toyota RAV4 Gen3 official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen3-launch-pack-2006.pdf
EU-TOYOTA-RAV4-III-SUV-PREFL-T180-01	4315	1855	1685	Toyota RAV4 Gen3 official launch pack	https://media.toyota.co.uk/wp-content/uploads/sites/5/pdf/RAV4-gen3-launch-pack-2006.pdf
EU-TOYOTA-RAV4-III-SUV-FACELIFT-WIDEBODY-01	4335	1855	1685	Auto-Data.net	https://www.auto-data.net/en/toyota-rav4-iii-xa30-facelift-2010-2.2-d-cat-177hp-4wd-37204
EU-BMW-3-SERIES-E91-WAGON-PREFL-01	4520	1817	1418	BMW Group PressClub	https://www.press.bmwgroup.com/united-kingdom/article/detail/T0012853EN_GB/the-new-bmw-3-series-touring?language=en_GB
EU-BMW-Z4-E86-COUPE-3-0SI-01	4091	1781	1268	Auto-Data.net	https://www.auto-data.net/en/bmw-z4-coupe-e86-3.0-si-265hp-9908
EU-BMW-3-SERIES-E46-CONVERTIBLE-FACELIFT-01	4488	1757	1372	BMW Group Classic;UltimateSpecs	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-1122-1.bmw-330cd-convertible-e46.html;https://www.ultimatespecs.com/car-specs/BMW/152222/BMW-E46-LCI-3-Series-Cabrio-330Cd-.html
EU-HONDA-CIVIC-VIII-SEDAN-IMA-01	4488	1753	1430	Auto-Data.net	https://www.auto-data.net/en/honda-civic-viii-sedan-1.3-i-dsi-ima-110hp-hybrid-e-cvt-12214
EU-MINI-MINI-R52-CONVERTIBLE-JCW-01	3635	1688	1415	ADAC;AutoScout24	https://www.adac.de/rund-ums-fahrzeug/autokatalog/marken-modelle/mini/mini/r50-r53-r52/998063/;https://www.autoscout24.de/auto/technische-daten/mini/john-cooper-works-cabrio/mini-cabrio-13706/
EU-MINI-MINI-R50-HATCHBACK-ONE-D-FACELIFT-01	3626	1688	1416	UltimateSpecs	https://www.ultimatespecs.com/car-specs/Mini/930/Mini-Mini-R50-One-D-90.html
EU-CHRYSLER-PT-CRUISER-WAGON-5D-01	4290	1705	1600	Auto-Data.net	https://www.auto-data.net/en/chrysler-pt-cruiser-2.4-i-16v-150hp-14752
EU-FIAT-DUCATO-II-VAN-244-SWB-LOWROOF-01	4749	2024	2150	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-SWB-HIGHROOF-01	4749	2024	2470	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-LOWROOF-01	5099	2024	2150	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-HIGHROOF-01	5099	2024	2470	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-SUPERHIGHROOF-01	5099	2024	2725	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-LOWROOF-01	5099	2024	2160	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-HIGHROOF-01	5099	2024	2480	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-MWB-MAXI-SUPERHIGHROOF-01	5099	2024	2735	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-LWB-HIGHROOF-01	5599	2024	2470	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-VAN-244-LWB-SUPERHIGHROOF-01	5599	2024	2860	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-SWB-15-01	4831	1932	2100	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-15-01	5181	1932	2100	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-MWB-MAXI-01	5181	1932	2125	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-15-01	5681	1932	2100	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-LWB-MAXI-01	5681	1932	2125	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-15-01	5980	2040	2100	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-DUCATO-II-CHASSIS-244-XLWB-MAXI-01	5980	2040	2125	Fiat Ducato 244 official owner handbook	https://aftersales.fiat.com/eLumData/EN/77/244_DUCATO/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG/77_244_DUCATO_603.45.862_EN_03_04.05_L_LG.pdf
EU-FIAT-BRAVO-I-HATCHBACK-3D-01	4025	1755	1420	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/2068010/fiat_bravo_jtd_100_sx.html
EU-FIAT-BRAVA-HATCHBACK-5D-01	4187	1741	1410	Automobile-Catalog	https://www.automobile-catalog.com/car/2000/2067995/fiat_brava_jtd_100_sx.html
EU-BMW-7-SERIES-E65-SEDAN-FACELIFT-01	5039	1902	1491	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-e65-facelift-2005-730i-258hp-steptronic-9710
EU-BMW-7-SERIES-E66-SEDAN-LWB-FACELIFT-01	5179	1902	1484	Auto-Data.net	https://www.auto-data.net/en/bmw-7-series-long-e66-facelift-2005-730li-258hp-steptronic-9712
EU-DAIHATSU-COPEN-L8-CONVERTIBLE-2D-01	3395	1475	1245	Auto-Data.net	https://www.auto-data.net/en/daihatsu-copen-l8-1.3-i-16v-87hp-37
EU-PEUGEOT-307-WAGON-PREFL-01	4419	1757	1544	Auto-Data.net	https://www.auto-data.net/en/peugeot-307-station-wagon-generation-1226
EU-PEUGEOT-607-SEDAN-FACELIFT-01	4902	1800	1442	Auto-Data.net	https://www.auto-data.net/en/peugeot-607-phase-ii-2004-3.0-v6-211hp-tiptronic-45877
EU-PEUGEOT-5008-I-MPV-01	4529	1888	1647	Auto-Data.net	https://www.auto-data.net/en/peugeot-5008-model-1953
EU-SMART-FORFOUR-W454-HATCHBACK-5D-01	3752	1684	1450	Auto-Data.net	https://www.auto-data.net/en/smart-forfour-w454-1.1i-64hp-14856
EU-FIAT-DOBLO-I-STANDARD-SWB-FACELIFT-01	4253	1722	1818	Auto-Data.net	https://www.auto-data.net/en/fiat-doblo-i-223-facelift-2005-generation-10488
EU-VW-GOLF-V-HATCHBACK-01	4204	1759	1485	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-3-door-2.0-tdi-16v-140hp-8633;https://www.auto-data.net/en/volkswagen-golf-v-5-door-2.0-tdi-8v-140hp-dpf-51672
EU-VW-GOLF-PLUS-V-MPV-PREFL-01	4206	1759	1592	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-v-plus-2.0-tdi-140hp-8658
EU-VW-GOLF-PLUS-VI-MPV-FACELIFT-01	4204	1759	1592	Auto-Data.net	https://www.auto-data.net/en/volkswagen-golf-vi-plus-generation-3938
EU-VOLVO-S80-II-SEDAN-01	4851	1861	1493	Auto-Data.net;Auto-Data.net	https://www.auto-data.net/en/volvo-s80-ii-2.4-d5-185hp-9364;https://www.auto-data.net/en/volvo-s80-ii-generation-1947
EU-LEXUS-RX-II-SUV-350-AWD-01	4740	1845	1705	Auto-Data.net	https://www.auto-data.net/en/lexus-rx-ii-350-4wd-276hp-5892
EU-CITROEN-C3-I-HATCHBACK-FACELIFT-01	3860	1667	1510	Auto-Data.net	https://www.auto-data.net/en/citroen-c3-i-phase-ii-2005-1.6-hdi-90hp-15091
```

[下载 DIMENSION_GROUP 表](sandbox:/mnt/data/all_101-200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.carmanualsonline.info/fiat-ducato-244-2005-3-g-owners-manual/23 "https://www.carmanualsonline.info/fiat-ducato-244-2005-3-g-owners-manual/23"


--- 本地最终 TSV 已更新 ---
- 本批 Ktype 映射：all_101-200_ktype_dimension_mapping_final.tsv
- 本批尺寸组：all_101-200_dimension_groups_final.tsv
- 累计 Ktype 映射：all_1-100_ktype_dimension_mapping_final.tsv（284 行）
- 累计尺寸组：all_1-100_dimension_groups_final.tsv（175 行）
