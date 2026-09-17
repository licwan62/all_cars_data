# 任务：all 第 1-100 行
# 来源文件：all.tsv
# 任务 ID：all__batch__0001__36300f0a


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】all 第 1-100 行

【任务要求】
# EU Auto-Data Ktype 车型尺寸补全规则

本规则适用于以下 13 列、Tab 分隔的欧洲车型输入表。`Ktype` 是输入车型标识，但不保证能唯一标识一个物理车身或一套尺寸。输出处理单位是“一个 Ktype 下的一条已区分物理车身尺寸记录”。

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
    - WheelbaseMM
    - DIMENSION_GROUP_ID
    - LengthMM
    - WidthMM
    - HeightMM
    - WidthBasis
    - EndDateStatus
    - ResolutionStatus
    - CacheSourceKtype
    - MatchReason
    - MatchConfidence
    - DimensionSource
    - SourceURL
    - Notes
    - IterationStatus
  auto_empty_columns: []
subseries_match:
  enabled: false
  columns: []
  auto_empty_columns: []
-->

## 一、目标与输出粒度

每轮输出一张完整 TSV。输出表头必须严格使用上方 `full_table.columns` 的字段及顺序，不得增删、改名或调换。

输出是输入车型表的尺寸结果子表，只保留主外键和相比输入新增的结果字段：

- `id` 是输出表唯一主键，按文本处理。
- `Ktype` 是指向输入表的外键，必须逐字保留，禁止转为浮点数、改写前导零或生成不存在的 Ktype。
- 输出不重复 `Make`、`Model`、`VariantName`、生产年月等其余输入字段；需要时通过 `Ktype` 回查输入表。
- 一个 Ktype 可以输出一行或多行；每行必须表示一个已经区分的物理车身/尺寸记录。
- 多个 Ktype 也可以引用同一个 `DIMENSION_GROUP_ID`。因此 Ktype 与物理尺寸记录按业务关系允许多对多。
- 每个输入 Ktype 至少输出一行；不得因待处理、无结果或与其他 Ktype 共用尺寸组而删除。
- 不输出子车系匹配表，不在同一回答中另建第二张或第三张 TSV。

### id 生成规则

- 当一个 Ktype 能唯一对应一条物理尺寸记录时，`id` 直接等于原始 Ktype，例如 `2`。
- 当一个 Ktype 对应多个不同物理车身或尺寸时，分别输出多行，`id` 使用 `{Ktype}_{描述}`，例如 `1_3dr`、`1_5dr`。
- 描述后缀必须简短、稳定、可读，并直接表达造成尺寸差异的物理特征。优先使用 `3dr`、`5dr`、`swb`、`lwb`、`lowroof`、`highroof`、`srw`、`drw`、`prefl`、`facelift` 等小写 ASCII 标记；需要同时区分多个特征时可组合，例如 `12_5dr_facelift`。
- 同一 Ktype 下不得重复 `id`；不得使用无语义的临时序号来掩盖尚未确认的差异。
- Ktype 拆成派生行后，不再同时保留无后缀的 `id=Ktype` 基础行，避免重复表达同一关系。
- 一旦某个派生 `id` 已用于已确认记录，后续批次必须保持稳定，不能因排序或来源变化改名。
- 若已确认 Ktype 覆盖多个物理外廓，就应输出多个派生 `id`，不能任选其中一个，也不能仅因 Ktype 不唯一而保持 `PENDING`。
- 若证据只表明“可能有多个尺寸”，但尚不能确认具体分支，则保留一行 `id=Ktype` 并标记 `PENDING`；不得提前创建猜测性的派生行。

`DIMENSION_GROUP_ID` 表示一套真实存在且经过确认的物理车身外轮廓。不同 `id` 可以引用同一个尺寸组；同一 Ktype 下物理外廓不同的行必须使用不同尺寸组。

## 二、输入字段解释

| 字段 | 处理规则 |
| --- | --- |
| Make | 原始品牌。查询时允许使用标准品牌写法。输出表不重复此字段。 |
| Model | 原始车型/车系，可能包含代际提示，例如 `Corsa d`、`Megane iii`。不得擅自删除罗马数字或字母。输出表不重复此字段。 |
| VariantName | 发动机或版本名称。用于区分 Ktype，不等于物理车身。 |
| BodyStyle | 原始德语或欧洲市场车身形式。原值保留，标准化结果写入 `NormalizedBodyStyle`。 |
| DriveType | 原始驱动形式。通常不单独决定尺寸组，但不能忽略可能影响车高的特殊底盘。 |
| Energy | 原始能源类型。通常不单独决定尺寸组。 |
| EngineOutputKW / EngineOutputHP | 原始功率，仅用于版本核验，不得作为尺寸组相同或不同的唯一依据。 |
| Product Start Month-Year | Ktype 的生产开始月，格式通常为 `MMM YYYY`。 |
| Product End Month-Year | Ktype 的生产结束月；`-`、空值或未知值不能解释为生产至今。 |
| LastProcessedDate | 上游处理日期，不作为车型生产日期或资料发布日期。输出表不重复此字段。 |
| Ktype | 输入车型标识和输出外键，不保证唯一对应一套物理尺寸。按文本处理，禁止转为浮点数或改写前导零。 |
| LatestStatus | 上游状态；本轮结论写入 `IterationStatus`。输出表不重复此字段。 |

输入表必须按 Tab 解析。字段内容中的空格不是分隔符，`Product Start Month-Year` 和 `Product End Month-Year` 是单个字段。

## 三、标准化字段

### 1. NormalizedBodyStyle

读取输入表的 `BodyStyle` 原文，并在输出的 `NormalizedBodyStyle` 中按物理车身形式写入以下优先标准值：

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

### 2. Generation、BodyCode、Doors、WheelbaseMM

- `Generation`：正式代际名称，例如 `Corsa D`。不能仅从生产年份推断。
- `BodyCode`：厂商平台/车身代码；一行只能填写一个明确代码，不能写 `L08/L68` 之类的组合值。无可靠证据时留空。
- `Doors`：只写整数，例如 `3`、`5`；一行只能表示一种门数。来源未明确时留空。
- `WheelbaseMM`：只写毫米数字，不写单位。不同轴距不能共用尺寸组。

不得把发动机代号、底盘配置或营销版本误写为 `BodyCode`。

若门数、车身代码、轴距、车顶、驾驶室、货斗、宽体或改款差异造成不同物理外廓，必须在同一 Ktype 下拆成不同 `id` 行。

## 四、尺寸字段与尺寸组

### 1. 统一口径

- `LengthMM`：量产标准状态下的最大车身外部长度，单位 mm。
- `WidthMM`：优先使用不含外后视镜的车身宽度，单位 mm。
- `HeightMM`：量产标准状态下的外部高度，单位 mm。
- 三个尺寸格中只写数字，不写 `mm`、约数符号、范围或多个候选值。
- 同一行的长、宽、高必须对应同一物理车身配置，不能从不同版本拼接。
- 英寸换算毫米时使用 `1 in = 25.4 mm`，最终取整到 1 mm，并在 `Notes` 标注换算。
- 厘米换算毫米时使用 `1 cm = 10 mm`。

### 2. WidthBasis

只允许以下值：

- `WITHOUT_MIRRORS`
- `WITH_MIRRORS`
- `UNKNOWN`

`WITH_MIRRORS` 或 `UNKNOWN` 不能标记为 `READY`，除非存在明确人工豁免；豁免必须写入 `Notes`。

### 3. DIMENSION_GROUP_ID

只有长、宽、高和物理车身边界均已确认后才能创建或命中尺寸组。ID 在当前批次及后续缓存中必须稳定，推荐格式：

```text
EU-{MAKE}-{MODEL}-{GENERATION}-{BODYSTYLE}-{SEQUENCE}
```

示例：

```text
EU-OPEL-CORSA-D-HATCHBACK-01
```

ID 中使用大写 ASCII、数字和连字符。不得把 `id` 或 Ktype 直接当作尺寸组 ID，也不得在证据不足时创建“临时确认”尺寸组。

以下差异通常不单独创建尺寸组：

- 发动机排量、功率、增压方式
- 燃料或能源类型
- 变速箱
- 不改变外部轮廓的驱动形式
- 普通配置等级

以下差异必须独立核对，存在差异时使用不同尺寸组：

- 不同代际或车身代码
- 不同 BodyStyle、门数且外形不同
- 不同轴距、SWB/LWB
- 普通车身/宽体、SRW/DRW
- 普通顶/高顶
- facelift 前后长宽高变化
- 不同 CAB/BED
- 特殊悬架高度、保险杠或外部套件
- 同名车型停产后重新推出

不得仅凭 `Make + Model + VariantName` 相似命中缓存。

## 五、生产日期与 EndDateStatus

月份使用英文三字母缩写：`Jan`、`Feb`、`Mar`、`Apr`、`May`、`Jun`、`Jul`、`Aug`、`Sep`、`Oct`、`Nov`、`Dec`。

`EndDateStatus` 只允许：

- `KNOWN`：输入或可靠来源给出明确结束年月。
- `STILL_IN_PRODUCTION`：可靠的当前官方资料确认仍在生产。
- `SOURCE_MISSING`：来源未提供结束时间。
- `UNKNOWN`：来源冲突或无法判断。

当 `Product End Month-Year` 为 `-` 或空值时：

- 不得自动补成当前年月或当前年份。
- 只有可靠官方资料明确仍在生产时，才能写 `STILL_IN_PRODUCTION`。
- 已确认停产且查到结束年月时，只在 `Notes` 记录补充值；输入表通过 Ktype 关联，不修改输入原字段。
- 历史车型默认使用 `SOURCE_MISSING` 或 `UNKNOWN`，不得扩展到当前年份。

车型年份覆盖只能由输入表中的有效生产月份展开。首尾年可视为覆盖年，但若同一年存在换代、改款或不同车身并行，必须在 `Notes` 保留对应尺寸组的实际月份边界，不能只按年份强行合并。派生行的适用范围不得超出其 Ktype 在输入表中的生产范围。

## 六、解析状态与缓存

`ResolutionStatus` 只允许：

- `DIRECT_NEW`：本次由可靠来源直接确认并创建新尺寸组。
- `CACHE_EXACT`：有直接证据确认与已有尺寸组完全相同。
- `CACHE_VERIFIED`：经过代际、车身代码、轴距或尺寸交叉核验后命中缓存。
- `MANUAL_OVERRIDE`：依据明确的人工决定；原因必须写入 `Notes`。
- `PENDING`：证据不足、来源冲突或关键字段缺失。

命中缓存时必须填写：

- `CacheSourceKtype`：提供已确认尺寸组的来源 Ktype；它是来源车型标识，不是唯一尺寸行主键。
- `MatchReason`：简洁说明相同代际、车身、轴距和尺寸等依据。
- `MatchConfidence`：只允许 `HIGH`、`MEDIUM`、`LOW`。

同一个来源 Ktype 有多个尺寸行时，`MatchReason` 必须同时写明来源行的 `id` 或足以唯一定位的 `BodyCode`/门数等物理特征。未命中缓存时 `CacheSourceKtype` 留空。`PENDING` 不得填写确定的 `DIMENSION_GROUP_ID`；可在 `Notes` 写候选 ID。

## 七、来源要求

来源优先级如下：

1. 厂商欧洲/国家官网、官方 brochure、technical specification、press kit、历史资料、homologation 或 type approval。
2. Auto-Data、Car.info、UltimateSpecs、Automobile-Catalog、Parkers。
3. 其他可信规格数据库，只用于交叉验证。

二手车广告、论坛、搜索摘要、AI 摘要和无出处聚合页只能作为线索，不能单独支撑 `DIRECT_NEW`、`CACHE_EXACT` 或最终 `READY`。

`DimensionSource` 填来源名称；`SourceURL` 填直接支持尺寸或车身判断的页面 URL。多个来源用分号分隔，并保持名称与 URL 顺序对应。不得填写搜索结果页 URL。

来源冲突时依次核对市场、年份、代际、BodyStyle、门数、轴距、含镜/不含镜和特殊版本；仍无法解决则使用 `PENDING`。

## 八、IterationStatus

`IterationStatus` 只允许：

- `READY`
- `PENDING: <具体原因>`

只有同时满足以下条件才能写 `READY`：

- `id` 在输出表中唯一，`Ktype` 能回查到输入表。
- 若 Ktype 对应多个已确认物理外廓，相关派生 `id` 均已分别输出，没有遗漏或任选其一。
- Generation、NormalizedBodyStyle 及必要的物理车身边界已经确认。
- LengthMM、WidthMM、HeightMM 均有值且属于同一配置。
- WidthBasis 为 `WITHOUT_MIRRORS`。
- DIMENSION_GROUP_ID 和 ResolutionStatus 有效。
- 生产结束状态处理正确。
- 来源可追溯，无未解决冲突。

待处理原因必须具体，例如：

```text
PENDING: 缺少不含后视镜宽度
PENDING: Corsa D 三门与五门车长是否一致未确认
PENDING: Product End 缺失且无法确认是否停产
PENDING: 官方与 Auto-Data 高度冲突
```

不得只写 `待查`、`未完成`、`有问题` 或沿用输入的 `LatestStatus`。

## 九、每轮固定输出

每轮回答依次包含：

1. `更新点`
2. `当前批次进度`
3. `本轮更新后的全量 TSV`
4. 未完成时输出 `下一步优先处理`
5. 最后一行输出 `下一步` 或 `本批次完成`

全量 TSV 必须覆盖当前输入文件的全部 Ktype，并包含当前已确认的全部派生 `id`。不得只输出变化行，不得用“其余不变”代替完整数据。

排序规则：

1. 首先保持输入 Ktype 的原始顺序。
2. 同一 Ktype 有多行时，按稳定的物理分支顺序排列，例如 `3dr` 在 `5dr` 前、`swb` 在 `lwb` 前、`lowroof` 在 `highroof` 前。
3. 后续轮次不得无故改变已经输出的 `id` 或行顺序。

未完成时：

````text
更新点
- ……

当前批次进度
- 已完成：……
- 待处理：……
- 当前批次尚未完成。

本轮更新后的全量 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus
1_3dr	1	Hatchback	Corsa D	L08	3	2511	EU-OPEL-CORSA-D-HATCHBACK-3D-01	3999	1713	1488	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Ktype 1覆盖L08与L68；本行为L08三门物理外廓	HIGH	Vauxhall official brochure	https://example.com/corsa-d-brochure	L08三门尺寸。	READY
1_5dr	1	Hatchback	Corsa D	L68	5	2511	EU-OPEL-CORSA-D-HATCHBACK-5D-01	3999	1737	1488	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Ktype 1覆盖L08与L68；本行为L68五门物理外廓	HIGH	Vauxhall official brochure	https://example.com/corsa-d-brochure	L68五门尺寸。	READY
2	2	Sedan	BMW 02 Series	114	2	2500	EU-BMW-02-SERIES-SEDAN-01	4230	1590	1410	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		单一标准两门车身	HIGH	BMW period brochure	https://example.com/bmw-1502-brochure		READY
```

下一步优先处理
1. ……

下一步
……
````

全部完成时，仍需输出完整 TSV，最后一行改为：

```text
本批次完成
```

## 十、强制检查

提交每轮结果前逐项检查：

1. 表头是否严格为 21 列且顺序正确。
2. `id` 是否每行有值并在输出表中唯一。
3. 每个 `Ktype` 是否能逐字匹配输入表，并且每个输入 Ktype 至少出现一次。
4. 输出是否只包含 `id`、`Ktype` 和新增结果字段，没有重复其余 12 个输入字段。
5. 已确认一个 Ktype 覆盖多个物理外廓时，是否分别输出了稳定派生 `id`，且没有任选、合并或遗漏。
6. 同一 Ktype 的多行是否确实由物理尺寸/车身边界差异造成，而不是仅由发动机、功率、燃料或普通配置差异造成。
7. 是否错误地把不同代际、BodyStyle、门数外形、轴距、车顶、驾驶室、货斗或宽体合并。
8. 长宽高是否来自同一配置并统一为 mm。
9. WidthBasis 是否明确。
10. 缓存命中是否有来源 Ktype、可唯一定位来源物理分支的理由和置信度。
11. `-` 结束时间是否被错误解释为生产至今，派生行范围是否超出输入 Ktype 的生产范围。
12. 每个 `READY` 是否有可追溯来源。
13. 是否保持输入 Ktype 顺序及同一 Ktype 内的稳定分支顺序，且未新增输入不存在的 Ktype。


【执行顺序】
执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。

【配置附加规则】


【当前文件名】
all.tsv

【当前独立任务】
all 第 1-100 行

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	EngineOutputKW	EngineOutputHP	Product Start Month-Year	Product End Month-Year	LastProcessedDate	Ktype
BMW	1500-2000	2000	Stufenheck	Heckantrieb	Benzin	74	100	Sep 1968	Jul 1972	2024-03-01	10
BMW	3	315	Stufenheck	Heckantrieb	Benzin	55	75	Mar 1981	Mar 1984	2024-03-01	11
BMW	3	316	Stufenheck	Heckantrieb	Benzin	66	90	Aug 1975	Aug 1980	2024-03-01	12
BMW	3	316	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1980	Dec 1982	2024-03-01	13
BMW	3	318	Stufenheck	Heckantrieb	Benzin	72	98	Aug 1975	Aug 1980	2024-03-01	14
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	77	105	Nov 1979	Aug 1982	2024-03-01	15
BMW	3	320	Stufenheck	Heckantrieb	Benzin	80	109	Jun 1975	Jul 1979	2024-03-01	16
BMW	3	320/6	Stufenheck	Heckantrieb	Benzin	90	122	Aug 1977	Oct 1982	2024-03-01	17
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	92	125	Jun 1975	Aug 1982	2024-03-01	18
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	105	143	Jan 1978	Oct 1982	2024-03-01	19
BMW	3	316	Stufenheck	Heckantrieb	Benzin	66	90	Sep 1983	Jun 1988	2024-03-01	20
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	73	100	Sep 1987	Jun 1991	2024-03-01	21
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	75	102	Dec 1984	Aug 1988	2024-03-01	22
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	77	105	Sep 1982	Aug 1987	2024-03-01	23
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	85	115	Sep 1987	Jun 1991	2024-03-01	24
Renault	Megane cc	1.6 16V	Cabriolet	Frontantrieb	Benzin	81	110	Jun 2010	Aug 2015	2024-03-01	25
Suzuki	Swift iv	1.2	Schrägheck	Frontantrieb	Benzin	69	94	Oct 2010	Apr 2017	2026-03-01	26
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	83	113	Jun 1987	Dec 1991	2024-03-01	27
BMW	3	318 IS	Stufenheck	Heckantrieb	Benzin	100	136	Sep 1989	Aug 1991	2024-03-01	28
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	95	129	Oct 1986	Apr 1991	2024-03-01	29
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	92	125	Sep 1982	Dec 1991	2024-03-01	30
BMW	3	M3 2.3	Stufenheck	Heckantrieb	Benzin	143	195	Jul 1986	Jun 1991	2024-03-01	31
BMW	3	M3 2.3	Stufenheck	Heckantrieb	Benzin	147	200	Feb 1987	May 1989	2024-03-01	32
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	102	139	Sep 1982	Aug 1983	2024-03-01	33
BMW	3	323 I	Stufenheck	Heckantrieb	Benzin	110	150	Sep 1983	Sep 1986	2024-03-01	34
BMW	3	M3 2.3	Stufenheck	Heckantrieb	Benzin	158	215	Jan 1986	Dec 1990	2024-03-01	35
BMW	3	325 I X	Stufenheck	Allrad	Benzin	125	170	Sep 1986	Aug 1991	2024-03-01	36
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	125	170	Dec 1986	Jun 1991	2024-03-01	37
BMW	3	325 I X	Stufenheck	Allrad	Benzin	126	171	Mar 1986	Dec 1987	2024-03-01	38
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	126	171	Sep 1983	Nov 1989	2024-03-01	39
BMW	3	325 E 2.7	Stufenheck	Heckantrieb	Benzin	90	122	Oct 1983	Dec 1988	2024-03-01	40
BMW	3	325 E 2.7	Stufenheck	Heckantrieb	Benzin	95	129	Jan 1985	Aug 1987	2024-03-01	41
BMW	3	324 D	Stufenheck	Heckantrieb	Diesel	63	86	Sep 1985	Dec 1990	2024-03-01	42
BMW	3	324 TD	Stufenheck	Heckantrieb	Diesel	85	115	Sep 1987	Aug 1991	2024-03-01	43
BMW	3	318 I	Kombi	Heckantrieb	Benzin	83	113	Apr 1989	Jun 1994	2024-03-01	44
BMW	3	320 I	Kombi	Heckantrieb	Benzin	95	129	Jan 1988	Dec 1991	2024-03-01	45
BMW	3	325 I	Kombi	Heckantrieb	Benzin	125	170	Jul 1987	Mar 1993	2024-03-01	46
BMW	3	325 I X	Kombi	Allrad	Benzin	125	170	Jun 1988	Oct 1993	2024-03-01	47
BMW	3	324 TD	Kombi	Heckantrieb	Diesel	85	115	Jan 1988	Jun 1993	2024-03-01	48
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	73	100	Mar 1991	Aug 1993	2024-03-01	49
BMW	3	316 I	Stufenheck	Heckantrieb	Benzin	75	102	Sep 1993	May 1998	2024-03-01	50
BMW	3	318 I	Stufenheck	Heckantrieb	Benzin	83	113	Sep 1990	Aug 1993	2024-03-01	51
BMW	3	318 IS	Stufenheck	Heckantrieb	Benzin	103	140	Sep 1993	Dec 1995	2024-03-01	52
BMW	3	318 IS	Coupe	Heckantrieb	Benzin	103	140	Jan 1992	Dec 1995	2024-03-01	53
BMW	3	320 I	Stufenheck	Heckantrieb	Benzin	110	150	Jan 1991	Feb 1998	2024-03-01	54
BMW	3	320 I	Coupe	Heckantrieb	Benzin	110	150	Dec 1991	Nov 1998	2024-03-01	55
Suzuki	Swift iv	1.2 4X4	Schrägheck	Allrad	Benzin	69	94	Oct 2010	Apr 2017	2026-03-01	56
Suzuki	Swift iv	1.3 Ddis	Schrägheck	Frontantrieb	Diesel	55	75	Oct 2010	Apr 2017	2026-03-01	57
Renault	Megane cc	2.0 CVT	Cabriolet	Frontantrieb	Benzin	103	140	Jun 2010	Aug 2015	2024-03-01	58
BMW	3	325 I	Stufenheck	Heckantrieb	Benzin	141	192	Sep 1990	Dec 1995	2024-03-01	59
Ford	C-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	92	125	Dec 2010	Jun 2019	2024-03-01	60
BMW	3	325 I	Coupe	Heckantrieb	Benzin	141	192	Oct 1991	Feb 1995	2024-03-01	61
BMW	3	325 TD	Stufenheck	Heckantrieb	Diesel	85	115	Sep 1991	Feb 1998	2024-03-01	62
BMW	3	325 TDS	Stufenheck	Heckantrieb	Diesel	105	143	May 1993	Feb 1998	2024-03-01	63
BMW	5	518	Stufenheck	Heckantrieb	Benzin	66	90	Jul 1974	May 1981	2024-03-01	64
Alfa Romeo	Gtv	2	Coupe	Heckantrieb	Benzin	94	128	Jan 1985	Dec 1985	2024-03-01	65
Ford	C-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	77	105	Dec 2010	Jun 2019	2024-03-01	66
Alfa Romeo	Gtv	6 2.5	Coupe	Heckantrieb	Benzin	116	158	Nov 1980	Feb 1987	2024-03-01	67
Ford	C-Max	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	110	150	Dec 2010	Jun 2019	2024-03-01	68
Ford	C-Max	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	134	182	Dec 2010	Jun 2019	2024-03-01	69
Ford	C-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	70	95	Dec 2010	Jun 2019	2024-03-01	70
Ford	C-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Dec 2010	Jun 2019	2024-03-01	71
Ford	Grand c-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	77	105	Dec 2010	Jun 2019	2024-03-01	72
Ford	Grand c-Max	1.6 TI	Großraumlimousine	Frontantrieb	Benzin	92	125	Dec 2010	Jun 2019	2024-03-01	73
Ford	Grand c-Max	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	110	150	Dec 2010	Jun 2019	2024-03-01	74
Ford	Grand c-Max	1.6 Ecoboost	Großraumlimousine	Frontantrieb	Benzin	134	182	Dec 2010	Jun 2019	2024-03-01	75
Ford	Grand c-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	70	95	Dec 2010	Jun 2019	2024-03-01	76
Ford	Grand c-Max	1.6 Tdci	Großraumlimousine	Frontantrieb	Diesel	85	115	Dec 2010	Jun 2019	2024-03-01	77
Minelli	Tf	1800	Cabriolet	Heckantrieb	Benzin	86	117	Jan 1998	Aug 2011	2024-03-01	78
Saab	9-5	2.0 Ttid XWD	Stufenheck	Allrad	Diesel	140	190	May 2010	Jan 2012	2024-03-01	79
Alfa Romeo	Alfasud	1.3	Coupe	Frontantrieb	Benzin	55	76	Sep 1976	Jul 1979	2024-03-01	81
Alfa Romeo	Alfasud	1.3	Coupe	Frontantrieb	Benzin	55	76	May 1978	Feb 1980	2024-03-01	82
Alfa Romeo	Alfasud	1.3	Coupe	Frontantrieb	Benzin	63	85	Jul 1979	Dec 1989	2024-03-01	83
Alfa Romeo	Alfasud	1.5	Coupe	Frontantrieb	Benzin	61	83	May 1978	Dec 1981	2024-03-01	84
Alfa Romeo	Alfasud	1.5	Coupe	Frontantrieb	Benzin	70	95	Jul 1979	Jan 1987	2024-03-01	85
Alfa Romeo	Alfasud	1.7 I.e.	Coupe	Frontantrieb	Benzin	77	105	Oct 1987	Dec 1989	2024-03-01	86
Alfa Romeo	Alfasud	1.5	Coupe	Frontantrieb	Benzin	77	105	Mar 1982	Dec 1988	2024-03-01	87
Alfa Romeo	33	1.2	Schrägheck	Frontantrieb	Benzin	50	68	Jun 1983	Dec 1989	2024-03-01	88
Alfa Romeo	33	1.3	Schrägheck	Frontantrieb	Benzin	55	75	Jun 1983	Dec 1989	2024-03-01	89
Alfa Romeo	33	1.3	Schrägheck	Frontantrieb	Benzin	63	86	Oct 1984	Dec 1989	2024-03-01	90
Alfa Romeo	33	1.5	Schrägheck	Frontantrieb	Benzin	62	84	May 1983	Dec 1987	2024-03-01	91
Alfa Romeo	33	1.5	Schrägheck	Frontantrieb	Benzin	75	102	Jul 1986	Dec 1989	2024-03-01	93
Alfa Romeo	33	1.5 QV	Schrägheck	Frontantrieb	Benzin	77	105	Jun 1984	Dec 1989	2024-03-01	94
Alfa Romeo	33	1.7 I.e.	Schrägheck	Frontantrieb	Benzin	77	105	Sep 1988	Dec 1989	2024-03-01	95
Alfa Romeo	33	1.7 QV	Schrägheck	Frontantrieb	Benzin	84	114	Mar 1988	Dec 1989	2024-03-01	96
Alfa Romeo	33	1.5 4X4	Kombi	Allrad	Benzin	66	90	Sep 1984	Dec 1986	2024-03-01	97
Alfa Romeo	33	1.5 4X4	Kombi	Allrad	Benzin	75	102	Dec 1986	Dec 1989	2024-03-01	98
Alfa Romeo	33	1.5 4X4	Kombi	Allrad	Benzin	77	105	Dec 1986	Mar 1989	2024-03-01	99
Alfa Romeo	33	1.7 I.e. 4X4	Kombi	Allrad	Benzin	77	105	Sep 1988	Dec 1989	2024-03-01	100
Alfa Romeo	33	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	65	88	Jun 1991	Sep 1994	2024-03-01	101
Alfa Romeo	33	1.4 I.e.	Schrägheck	Frontantrieb	Benzin	66	90	Jun 1991	Sep 1994	2024-03-01	102
Alfa Romeo	33	1.7 I.e.	Schrägheck	Frontantrieb	Benzin	79	107	Jan 1990	Sep 1994	2024-03-01	103
Alfa Romeo	33	1.7 I.e.	Schrägheck	Frontantrieb	Benzin	77	105	Apr 1992	Sep 1994	2024-03-01	105
Alfa Romeo	33	1.7 16V	Schrägheck	Frontantrieb	Benzin	95	129	Jan 1990	Sep 1994	2024-03-01	107
Alfa Romeo	33	1.7 16V	Schrägheck	Frontantrieb	Benzin	97	132	Jan 1990	Mar 1992	2024-03-01	108
Alfa Romeo	33	1.4 I.e.	Kombi	Frontantrieb	Benzin	65	88	Jun 1991	Sep 1994	2024-03-01	109
Alfa Romeo	33	1.4 I.e.	Kombi	Frontantrieb	Benzin	66	90	Jun 1991	Sep 1994	2024-03-01	110
Alfa Romeo	33	1.7 I.e.	Kombi	Frontantrieb	Benzin	79	107	Jan 1990	Mar 1992	2024-03-01	111
Alfa Romeo	33	1.7 16V	Kombi	Frontantrieb	Benzin	97	132	Jan 1990	Sep 1994	2024-03-01	112
Alfa Romeo	33	1.7 I.e.	Kombi	Frontantrieb	Benzin	77	105	Apr 1992	Sep 1994	2024-03-01	113


--- Round 1 / 首次发送 ---
## 更新点

* 已覆盖当前输入的全部 **100 个 Ktype**，输出保持原始 Ktype 顺序，未新增不存在的 Ktype；共建立 **19 个已确认尺寸组**。
* 已补齐所有记录的候选长宽高、标准化车身、代际和轴距。Alfasud Sprint 根据时期 brochure 确认为三门车身，尺寸采用 4019×1610×1305 mm；Alfa GTV Tipo 116 修正为两门 Coupe。([汽车目录][1])
* BMW E30 普通 Stufenheck 的尺寸已补齐，但部分发动机同时存在两门和四门目录记录，输入没有门数，因此未猜测建立尺寸组；318is 能明确定位为两门分支，已单独完成。([汽车数据][2])
* Suzuki Swift 1.2 94PS 同时存在三门、五门记录，Ktype 26 暂不能唯一确定；4X4 与 DDiS 的五门外廓已确认。([汽车数据][3])
* Ford C-Max/Grand C-Max 的输入生产区间跨越 2015 年改款，且改款前后长度或高度发生变化，因此 12 条记录保留 `PENDING`，没有把两套尺寸强行合并。([福特服务内容][4])

## 当前批次进度

* 已完成：**68 / 100 个 Ktype 为 READY**
* 已确认尺寸组：**19 个**
* 待处理：**32 / 100 个 Ktype**

  * BMW E30 普通 Stufenheck 门数范围：18 条
  * Ford C-Max/Grand C-Max 改款边界：12 条
  * Suzuki Swift 1.2 门数范围：1 条
  * Minelli TF 生产结束时间冲突：1 条
* 当前批次尚未完成。

## 本轮更新后的全量 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus
10	10	Sedan	BMW New Class 2000		4	2550	EU-BMW-NEW-CLASS-2000-SEDAN-01	4500	1710	1445	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		2000四门New Class单一标准车身	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1968/77360/bmw_2000.html;https://www.auto-data.net/en/bmw-new-class-2000-100hp-44621		READY
11	11	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E21两门Stufenheck标准物理外廓	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
12	12	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
13	13	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
14	14	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
15	15	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
16	16	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
17	17	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
18	18	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
19	19	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
20	20	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
21	21	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
22	22	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
23	23	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
24	24	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
25	25	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Megane III Coupe-Cabriolet两门单一外廓	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392	来源同时列出含镜宽2072，采用不含后视镜宽1811。	READY
26	26	Hatchback	Suzuki Swift IV	AZG		2430		3850	1695	1510	WITHOUT_MIRRORS	KNOWN	PENDING		同一1.2 94PS存在3门与5门，输入Ktype未给门数	MEDIUM	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-3d-17132;https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133	3门与5门长宽高相同，但属于不同门数物理车身；当前不猜测拆分。	PENDING: Swift 1.2三门与五门适用范围未确认
27	27	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
28	28	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		318is为E30两门Stufenheck物理分支	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-318is-136hp-10078	输入BodyStyle为Stufenheck，按规则标准化为Sedan；318is为两门车身。	READY
29	29	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
30	30	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
31	31	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 M3两门宽体标准物理外廓	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
32	32	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
33	33	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
34	34	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
35	35	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
36	36	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
37	37	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
38	38	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
39	39	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
40	40	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
41	41	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
42	42	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
43	43	Sedan	BMW 3 Series E30	E30		2570		4325	1645	1380	WITHOUT_MIRRORS	KNOWN	PENDING		候选E30标准外廓已确认，但Ktype未给门数且对应发动机存在两门/四门车身可能	MEDIUM	Auto-Data E30 Sedan; Auto-Data E30 Coupe	https://www.auto-data.net/en/bmw-3-series-sedan-e30-318i-105hp-10074;https://www.auto-data.net/en/bmw-3-series-coupe-e30-generation-8961	候选尺寸4325×1645×1380，轴距2570；不得在门数未确认前建立尺寸组。	PENDING: E30两门与四门适用范围未确认
44	44	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 Touring五门旅行车标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
45	45	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
46	46	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
47	47	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
48	48	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
49	49	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36四门Sedan标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
50	50	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
51	51	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
52	52	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
53	53	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36两门Coupe标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
54	54	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
55	55	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
56	56	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Swift 1.2 4X4五门；2011与2013改款规格外廓一致	HIGH	Auto-Data; Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3405905/suzuki_swift_1_2_4x4.html;https://www.auto-data.net/en/suzuki-swift-v-facelift-2013-1.2-94hp-4x4-5d-21694	4X4车高1535，高于前驱版本1510；Automobile-Catalog明确宽度不含后视镜。	READY
57	57	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Swift 1.3 DDiS五门前驱单一外廓	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.3-ddis-75hp-5d-17135		READY
58	58	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	25	同代Megane III CC两门；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-2.0-16v-140hp-cvt-29896	采用不含后视镜宽1811。	READY
59	59	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
60	60	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
61	61	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
62	62	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
63	63	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
64	64	Sedan	BMW 5 Series E12	E12	4	2636	EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E12 518四门Sedan标准外廓	HIGH	Auto-Data; BMW Group Classic	https://www.auto-data.net/en/bmw-5-series-e12-518-90hp-9691;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-138-1.bmw-518-e12.html		READY
65	65	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Tipo 116 GTV两门Coupe标准外廓	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144125/alfa_romeo_gtv_2_0.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
66	66	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
67	67	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	65	GTV6 2.5与GTV 2.0同属Tipo 116两门车身，轴距及外廓一致	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144140/alfa_romeo_gtv6_2_5.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
68	68	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
69	69	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
70	70	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
71	71	MPV	Ford C-Max II	C344	5	2648		4380	1828	1626	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1593875/ford_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4380×1828×1626、轴距2648；改款约4379×1828×1610。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨C-Max改款且物理分支范围未确认
72	72	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
73	73	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
74	74	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
75	75	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
76	76	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
77	77	MPV	Ford Grand C-Max II	C344	5	2788		4520	1828	1684	WITHOUT_MIRRORS	KNOWN	PENDING		已补2010-2015前期Grand C-Max外廓；输入结束Jun 2019跨越2015改款且改款尺寸变化	MEDIUM	Ford official owner manual; Ford 2011 brochure; Automobile-Catalog; Ford facelift brochure	https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263;https://autocatalogarchive.com/wp-content/uploads/2016/08/Ford-C-Max-2011-UK.pdf;https://www.automobile-catalog.com/car/2011/1594235/ford_grand_c-max_1_6_tdci_115_titanium.html;https://www.ford.co.uk/content/dam/guxeu/uk/documents/brochures/cars/BRO-New_Grand_CMAX.pdf	前期候选4520×1828×1684、轴距2788；改款约4519×1828×1642。需确认该Ktype实际仅前期适用或拆分改款分支。	PENDING: Ktype日期跨Grand C-Max改款且物理分支范围未确认
78	78	Convertible	Minelli TF 1800		2	2400		3815	1680	1180	WITHOUT_MIRRORS	UNKNOWN	PENDING		物理尺寸已由两来源一致支持，但输入结束Aug 2011与来源生产期1998-2001冲突	LOW	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/minelli-tf-1800-1.8-i-16v-115hp-14854;https://www.automobile-catalog.com/car/2000/2046185/minelli_tf_1800.html	候选尺寸3815×1680×1180、轴距2400；先解决生产期冲突，再创建尺寸组。	PENDING: 输入结束时间与规格来源生产期冲突
79	79	Sedan	Saab 9-5 II	YS3G	4	2837	EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		第二代9-5四门Sedan；TTiD XWD对应同一标准外廓	HIGH	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3038990/saab_9-5_2_0_ttid_xwd.html		READY
81	81	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		902.A三门Alfasud Sprint标准外廓	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
82	82	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
83	83	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
84	84	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
85	85	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
86	86	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
87	87	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
88	88	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905早期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
89	89	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
90	90	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
91	91	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
93	93	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
94	94	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
95	95	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905后期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
96	96	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期1.7 QV与来源Ktype 95同一五门车身，轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410	来源目录存在114/118 hp标注差异；功率差异不改变本物理车身判断。	READY
97	97	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905A五门Sport Wagon 4X4标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
98	98	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
99	99	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
100	100	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
101	101	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907A五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
102	102	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
103	103	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
105	105	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
107	107	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
108	108	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
109	109	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907B五门Sport Wagon标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
110	110	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
111	111	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
112	112	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
113	113	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
```

[下载本轮完整 TSV 文件](sandbox:/mnt/data/all_1-100_updated.tsv)

## 下一步优先处理

1. 优先补 BMW E30 普通 Stufenheck 的两门/四门适用范围；确认一个 Ktype 同时覆盖两种车身时，再稳定拆为 `_2dr`、`_4dr`。
2. 补 Ford C-Max 和 Grand C-Max 各发动机的实际改款切换月，判断 Ktype 是仅适用前期车身，还是必须拆为 `_prefl`、`_facelift`。
3. 补 Suzuki Ktype 26 的门数映射，并解决 Minelli TF 输入结束时间与来源生产期冲突。

## 下一步

下一步优先补缺失：先解决 BMW E30 门数范围，再处理 Ford C-Max 改款分界、Suzuki Swift 门数及 Minelli 生产期冲突。

[1]: https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html "https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html"
[2]: https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-318is-136hp-10078 "https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-318is-136hp-10078"
[3]: https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133 "https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133"
[4]: https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263 "https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G1298265&Uid=G1276685&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G539689&userMarket=GBR&vFilteringEnabled=False&variantid=2263"


--- 发送 / 继续到 Round 2 ---
继续补强当前批次，并严格按以下格式回复：1) 更新点；2) 当前批次进度；3) 本轮更新后的全量 TSV（必须是真正更新过的 TSV，不能只写计划或说明，全量 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus。不要输出子车系匹配表。）；5) 下一步优先处理（有数据缺失时必须写下一步优先补缺失，缺失补齐后再写下一步优先核对）；6) 若仍未完成，TSV 代码块外最后一行必须单独输出“推进信号：CONTINUE”；全部完成时最后一行单独输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。若输入记录已有年份范围，拆分后的年份合集不得超出该范围；若输入未提供年份，只可补入可靠来源明确支持的生产年份。不得新增输入不存在的 MAKE/MODEL；最终 TSV 顺序必须保持当前 split 第一条到最后一条的边界。不要只描述这一轮将要做什么而不给 TSV，不要连续重复上一轮内容。


--- Round 2 / 下一步 ---
## 1) 更新点

* 已解决上一轮 **31 个 PENDING Ktype**：BMW E30 普通 Stufenheck 按两门、四门物理车身拆分；其中 Ktype 33 的输入范围截止至 1983 年 8 月，只保留 `33_2dr`，没有生成超出输入范围的四门记录。BMW 官方历史资料确认 E30 两门车身先推出，四门车身于 1983 年加入。([宝马经典集团][1])([宝马经典集团][1])物理车身边界不同，因此使用独立 `DIMENSION_GROUP_ID`。
* Ford C-Max 与 Grand C-Max 已按具体发动机版本补齐：

  * 105/125 PS TI-VCT、150/182 PS EcoBoost、95 PS TDCi 均限定为改款前车身。
  * 115 PS TDCi 同时覆盖改款前后，分别拆为 `71_prefl`、`71_facelift`、`77_prefl`、`77_facelift`，改款后的长度和高度变化，不再强行共用尺寸组。([汽车数据][2])([汽车数据][2])、门数、轴距和候选长宽高均已补齐；仅 Ktype 78 的输入生产结束时间与车型规格来源生产期仍冲突，暂不创建确定尺寸组。

## 2) 当前批次进度

* 输入 Ktype：**100 / 100 已覆盖**
* 当前物理尺寸记录：**120 行**
* READY：**119 行，覆盖 99 个 Ktype**
* PENDING：**1 行，覆盖 1 个 Ktype**
* 已确认尺寸组：**25 个**
* 第一阶段的数据缺失已补齐。
* 当前进入第二阶段，剩余工作为来源和生产期冲突核对。
* 当前批次尚未完成。

## 3) 本轮更新后的全量 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus
10	10	Sedan	BMW New Class 2000		4	2550	EU-BMW-NEW-CLASS-2000-SEDAN-01	4500	1710	1445	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		2000四门New Class单一标准车身	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1968/77360/bmw_2000.html;https://www.auto-data.net/en/bmw-new-class-2000-100hp-44621		READY
11	11	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E21两门Stufenheck标准物理外廓	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
12	12	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
13	13	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
14	14	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
15	15	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
16	16	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
17	17	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
18	18	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
19	19	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
20_2dr	20	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		BMW官方确认E30 Stufenheck存在2门车身；本行为首次建立2门物理外廓尺寸组	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
20_4dr	20	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		BMW官方确认E30 Stufenheck存在4门车身；本行为首次建立4门物理外廓尺寸组	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
21_2dr	21	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
21_4dr	21	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
22_2dr	22	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
22_4dr	22	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
23_2dr	23	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。输入范围Sep 1982-Aug 1987；2dr覆盖完整输入范围。	READY
23_4dr	23	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。输入范围始于Sep 1982，但4dr仅从Sep 1983起适用。	READY
24_2dr	24	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
24_4dr	24	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
25	25	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Megane III Coupe-Cabriolet两门单一外廓	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392	来源同时列出含镜宽2072，采用不含后视镜宽1811。	READY
26_3dr	26	Hatchback	Suzuki Swift IV	AZG	3	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.2 94 PS来源明确列出三门车身；与五门外廓尺寸相同但门数物理边界不同，独立建组	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-3d-17132	三门物理分支；尺寸3850×1695×1510，轴距2430。	READY
26_5dr	26	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.2 94 PS来源明确列出五门车身；与三门外廓尺寸相同但门数物理边界不同，独立建组	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133	五门物理分支；尺寸3850×1695×1510，轴距2430。	READY
27_2dr	27	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
27_4dr	27	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
28	28	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		318is为E30两门Stufenheck物理分支	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-318is-136hp-10078	输入BodyStyle为Stufenheck，按规则标准化为Sedan；318is为两门车身。	READY
29_2dr	29	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
29_4dr	29	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
30_2dr	30	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
30_4dr	30	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
31	31	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 M3两门宽体标准物理外廓	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
32	32	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
33_2dr	33	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。输入范围Sep 1982-Aug 1983结束于四门上市前，因此只输出2dr，不生成4dr。	READY
34_2dr	34	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
34_4dr	34	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
35	35	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
36_2dr	36	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
36_4dr	36	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
37_2dr	37	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
37_4dr	37	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
38_2dr	38	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。BMW零件目录确认325iX E30两门欧洲车型。	READY
38_4dr	38	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。BMW零件目录确认325iX E30四门欧洲车型。	READY
39_2dr	39	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
39_4dr	39	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
40_2dr	40	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
40_4dr	40	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
41_2dr	41	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。	READY
41_4dr	41	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。	READY
42_2dr	42	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。BMW零件目录确认该柴油型号存在E30两门欧洲车型。	READY
42_4dr	42	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。BMW零件目录确认该柴油型号存在E30四门欧洲车型。	READY
43_2dr	43	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30两门Stufenheck物理分支。BMW零件目录确认该柴油型号存在E30两门欧洲车型。	READY
43_4dr	43	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30四门Stufenheck于Sep 1983起供应；本派生行只覆盖输入Ktype范围内且不早于该月的四门生产期。BMW零件目录确认该柴油型号存在E30四门欧洲车型。	READY
44	44	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 Touring五门旅行车标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
45	45	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
46	46	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
47	47	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
48	48	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
49	49	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36四门Sedan标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
50	50	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
51	51	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
52	52	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
53	53	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36两门Coupe标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
54	54	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
55	55	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
56	56	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Swift 1.2 4X4五门；2011与2013改款规格外廓一致	HIGH	Auto-Data; Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3405905/suzuki_swift_1_2_4x4.html;https://www.auto-data.net/en/suzuki-swift-v-facelift-2013-1.2-94hp-4x4-5d-21694	4X4车高1535，高于前驱版本1510；Automobile-Catalog明确宽度不含后视镜。	READY
57	57	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	26	与来源Ktype 26的来源行26_5dr同为Swift IV/AZG五门前驱标准车身；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.3-ddis-75hp-5d-17135	五门前驱柴油版本命中26_5dr尺寸组。	READY
58	58	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	25	同代Megane III CC两门；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-2.0-16v-140hp-cvt-29896	采用不含后视镜宽1811。	READY
59	59	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
60	60	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		首次建立C-Max II改款前五门MPV尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratec-ti-vct-125hp-19845	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
61	61	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
62	62	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
63	63	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
64	64	Sedan	BMW 5 Series E12	E12	4	2636	EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E12 518四门Sedan标准外廓	HIGH	Auto-Data; BMW Group Classic	https://www.auto-data.net/en/bmw-5-series-e12-518-90hp-9691;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-138-1.bmw-518-e12.html		READY
65	65	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Tipo 116 GTV两门Coupe标准外廓	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144125/alfa_romeo_gtv_2_0.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
66	66	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratec-ti-vct-105hp-19808	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
67	67	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	65	GTV6 2.5与GTV 2.0同属Tipo 116两门车身，轴距及外廓一致	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144140/alfa_romeo_gtv6_2_5.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
68	68	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-ecoboost-scti-150hp-s-s-19846	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
69	69	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-ecoboost-182hp-s-s-46351	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
70	70	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratorq-tdci-95hp-dpf-s-s-19809	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
71_prefl	71	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60改款前车身一致；本Ktype同时覆盖改款前后，当前行为prefl分支	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratorq-tdci-115hp-dpf-s-s-19810	改款前分支限定为输入范围内Dec 2010至Mar 2015；不覆盖Apr 2015后的facelift外廓。	READY
71_facelift	71	MPV	Ford C-Max II facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-FACELIFT-02	4379	1828	1610	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.6 TDCi 115 PS在2015改款后继续存在；改款后长度和高度变化，建立独立物理尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-facelift-2015-1.6-tdci-115hp-21454	改款后分支限定为输入范围内Apr 2015至Jun 2019；长/高变化，不能与prefl共用尺寸组。	READY
72	72	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		首次建立Grand C-Max II改款前五门长轴MPV尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratec-ti-vct-105hp-19814	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
73	73	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-1.6-duratec-ti-vct-125hp-19854	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
74	74	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-ecoboost-scti-150hp-s-s-19855	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
75	75	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-ecoboost-182hp-s-s-56864	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
76	76	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratorq-tdci-95hp-dpf-s-s-19815	精确功率版本来源仅列于改款前代际；实际物理分支限定在2010年至2014/2015改款前，未扩展到输入范围之外。	READY
77_prefl	77	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72改款前车身一致；本Ktype同时覆盖改款前后，当前行为prefl分支	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-1.6-duratorq-tdci-115hp-dpf-s-s-19816	改款前分支限定为输入范围内Dec 2010至Mar 2015；不覆盖Apr 2015后的facelift外廓。	READY
77_facelift	77	MPV	Ford Grand C-Max II facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.6 TDCi 115 PS在2015改款后继续存在；改款后长度和高度变化，建立独立物理尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-facelift-2015-1.6-tdci-115hp-21469	改款后分支限定为输入范围内Apr 2015至Jun 2019；长/高变化，不能与prefl共用尺寸组。	READY
78	78	Convertible	Minelli TF 1800		2	2400		3815	1680	1180	WITHOUT_MIRRORS	UNKNOWN	PENDING		物理尺寸已由两来源一致支持，但输入结束Aug 2011与来源生产期1998-2001冲突	LOW	Auto-Data; Automobile-Catalog	https://www.auto-data.net/en/minelli-tf-1800-1.8-i-16v-115hp-14854;https://www.automobile-catalog.com/car/2000/2046185/minelli_tf_1800.html	候选尺寸3815×1680×1180、轴距2400；先解决生产期冲突，再创建尺寸组。	PENDING: 输入结束时间与规格来源生产期冲突
79	79	Sedan	Saab 9-5 II	YS3G	4	2837	EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		第二代9-5四门Sedan；TTiD XWD对应同一标准外廓	HIGH	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3038990/saab_9-5_2_0_ttid_xwd.html		READY
81	81	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		902.A三门Alfasud Sprint标准外廓	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
82	82	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
83	83	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
84	84	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
85	85	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
86	86	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
87	87	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
88	88	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905早期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
89	89	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
90	90	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
91	91	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
93	93	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
94	94	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
95	95	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905后期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
96	96	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期1.7 QV与来源Ktype 95同一五门车身，轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410	来源目录存在114/118 hp标注差异；功率差异不改变本物理车身判断。	READY
97	97	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905A五门Sport Wagon 4X4标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
98	98	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
99	99	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
100	100	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
101	101	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907A五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
102	102	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
103	103	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
105	105	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
107	107	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
108	108	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
109	109	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907B五门Sport Wagon标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
110	110	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
111	111	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
112	112	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
113	113	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
```

## 5) 下一步优先处理

**下一步优先核对：**

1. 核对 Minelli TF 1800 的真实生产结束时间，重点查找 Minelli 原厂资料、欧洲型式认证、TecDoc 车型节点或可证明 2001 年后持续生产的可靠资料。
2. 若确认车辆仅生产至 2001 年，则保留输入 `Aug 2011` 冲突说明，并依据可靠生产资料建立尺寸组或继续按冲突规则保持 `PENDING`。
3. 若确认 1998–2011 为有效生产范围，则创建 `EU-MINELLI-TF-1800-CONVERTIBLE-01`，将 Ktype 78 转为 `READY`。
4. Ktype 78 解决后，再进行本批次最终逐行口径、来源对应关系和缓存来源复核。

推进信号：CONTINUE

[1]: https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-sedan-e30.html?utm_source=chatgpt.com "BMW 3 Series sedan (E30)"
[2]: https://www.auto-data.net/en/ford-c-max-ii-1.6-duratorq-tdci-115hp-dpf-s-s-19810?utm_source=chatgpt.com "Ford C-MAX II 1.6 Duratorq TDCi (115 Hp) DPF S&S | Technical specs, data, fuel consumption, Dimensions"


--- 发送 / 继续到 Round 3 ---
继续补强当前批次，并严格按以下格式回复：1) 更新点；2) 当前批次进度；3) 本轮更新后的全量 TSV（必须是真正更新过的 TSV，不能只写计划或说明，全量 TSV 表头必须严格使用 requirement 指定的字段顺序：id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus。不要输出子车系匹配表。）；5) 下一步优先处理（有数据缺失时必须写下一步优先补缺失，缺失补齐后再写下一步优先核对）；6) 若仍未完成，TSV 代码块外最后一行必须单独输出“推进信号：CONTINUE”；全部完成时最后一行单独输出“推进信号：COMPLETE”。执行顺序必须固定为：第一阶段先解决数据缺失，优先补齐缺失年份、缺失结构/版本/门数/驾驶室/货斗、缺失尺寸、缺失参考车型等会阻塞成表的数据；第二阶段才解决核对问题，逐年核对参考车型覆盖、尺寸口径和迭代状态。只要仍存在任何数据缺失，不要把主要精力转到核对问题，也不要写全部可入库或本批次完成。回复中的下一步方向请按阶段写：有缺失时写“下一步优先补缺失”，缺失已补齐后再写“下一步优先核对”。若输入记录已有年份范围，拆分后的年份合集不得超出该范围；若输入未提供年份，只可补入可靠来源明确支持的生产年份。不得新增输入不存在的 MAKE/MODEL；最终 TSV 顺序必须保持当前 split 第一条到最后一条的边界。不要只描述这一轮将要做什么而不给 TSV，不要连续重复上一轮内容。


--- Round 3 / 下一步 ---
## 1) 更新点

* Ktype `78` 已由 `PENDING` 转为 `READY`，正式建立尺寸组 `EU-MINELLI-TF-1800-CONVERTIBLE-01`。
* 瑞士道路交通主管部门型式批准资料 `1MN901` 直接确认：两门开放式车身、轴距 `2390 mm`、长度 `3815 mm`、宽度 `1680 mm`、高度范围 `1200–1350 mm`。按照本任务“采用标准状态最大外部高度”的规则，`HeightMM` 写入 `1350`。型式批准将左右后视镜单独列项，因此 `1680` 按不含后视镜宽度处理。([Typenscheinschweiz.ch][1])
* Minelli 原厂资料确认该车为手工小批量生产的双座 `TF 1800 MK I Roadster`，与型式批准的品牌、发动机、车身形式和功率一致。([Minelli Automotive][2])
* 型式批准备注明确瑞士制造有效至 `31 Dec 2000`。输入中的 `Aug 2011` 保留为上游 Ktype 日期，但不再解释为车辆持续生产至 2011 年。([Typenscheinschweiz.ch][3])
* 已完成程序化强制检查：严格 21 列、`id` 全部唯一、100 个输入 Ktype 全部覆盖、120 条物理记录全部有尺寸组和三维、全部为 `WITHOUT_MIRRORS`、无 `PENDING`。

## 2) 当前批次进度

* 输入 Ktype：**100 / 100 已覆盖**
* 输出物理尺寸记录：**120 行**
* READY：**120 / 120**
* PENDING：**0**
* 已确认尺寸组：**26 个**
* 数据缺失阶段：**完成**
* 逐行核对阶段：**完成**
* 当前批次已完成。

## 3) 本轮更新后的全量 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	WheelbaseMM	DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	WidthBasis	EndDateStatus	ResolutionStatus	CacheSourceKtype	MatchReason	MatchConfidence	DimensionSource	SourceURL	Notes	IterationStatus
10	10	Sedan	BMW New Class 2000		4	2550	EU-BMW-NEW-CLASS-2000-SEDAN-01	4500	1710	1445	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		2000四门New Class单一标准车身	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1968/77360/bmw_2000.html;https://www.auto-data.net/en/bmw-new-class-2000-100hp-44621		READY
11	11	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E21两门Stufenheck标准物理外廓	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
12	12	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
13	13	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
14	14	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
15	15	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
16	16	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
17	17	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
18	18	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
19	19	Sedan	BMW 3 Series E21	E21	2	2563	EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	11	E21两门Stufenheck；轴距及长宽高一致	HIGH	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091		READY
20_2dr	20	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		BMW官方历史资料确认E30 Stufenheck存在2门车身；本行为首次建立2门物理外廓尺寸组	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
20_4dr	20	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		BMW官方历史资料确认E30 Stufenheck存在4门车身；本行为首次建立4门物理外廓尺寸组	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
21_2dr	21	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
21_4dr	21	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
22_2dr	22	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
22_4dr	22	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
23_2dr	23	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
23_4dr	23	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。输入范围始于Sep 1982，四门仅覆盖Sep 1983起的重叠期间。	READY
24_2dr	24	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
24_4dr	24	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
25	25	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Megane III Coupe-Cabriolet两门单一外廓	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392	来源同时列出含镜宽2072，采用不含后视镜宽1811。	READY
26_3dr	26	Hatchback	Suzuki Swift IV	AZG	3	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.2 94 PS来源明确列出3门车身；与另一门数外廓尺寸相同但物理车身边界不同，独立建组	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-3d-17132	3门物理分支；尺寸3850×1695×1510，轴距2430。	READY
26_5dr	26	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.2 94 PS来源明确列出5门车身；与另一门数外廓尺寸相同但物理车身边界不同，独立建组	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133	5门物理分支；尺寸3850×1695×1510，轴距2430。	READY
27_2dr	27	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
27_4dr	27	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
28	28	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		318is为E30两门Stufenheck物理分支	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e30-facelift-1987-318is-136hp-10078	输入BodyStyle为Stufenheck，按规则标准化为Sedan；318is为两门车身。	READY
29_2dr	29	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
29_4dr	29	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
30_2dr	30	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
30_4dr	30	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
31	31	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 M3两门宽体标准物理外廓	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
32	32	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
33_2dr	33	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。输入范围Sep 1982-Aug 1983结束于四门上市前，因此不生成4dr分支。	READY
34_2dr	34	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
34_4dr	34	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
35	35	Sedan	BMW M3 E30	E30	2	2565	EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	31	E30 M3两门宽体Stufenheck；轴距及外廓一致	HIGH	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
36_2dr	36	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
36_4dr	36	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
37_2dr	37	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
37_4dr	37	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
38_2dr	38	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
38_4dr	38	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
39_2dr	39	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
39_4dr	39	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
40_2dr	40	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
40_4dr	40	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
41_2dr	41	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
41_4dr	41	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
42_2dr	42	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
42_4dr	42	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
43_2dr	43	Sedan	BMW 3 Series E30	E30	2	2570	EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_2dr同为E30 2门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129	E30 2门Stufenheck物理分支。	READY
43_4dr	43	Sedan	BMW 3 Series E30	E30	4	2570	EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	20	与来源Ktype 20的来源行20_4dr同为E30 4门Stufenheck；轴距及长宽高一致	HIGH	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
44	44	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E30 Touring五门旅行车标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
45	45	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
46	46	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
47	47	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
48	48	Wagon	BMW 3 Series E30 Touring	E30	5	2570	EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	44	E30 Touring五门旅行车；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058		READY
49	49	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36四门Sedan标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
50	50	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
51	51	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
52	52	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
53	53	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E36两门Coupe标准物理外廓	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
54	54	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
55	55	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
56	56	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Swift 1.2 4X4五门；2011与2013改款规格外廓一致	HIGH	Auto-Data; Automobile-Catalog	https://www.automobile-catalog.com/car/2011/3405905/suzuki_swift_1_2_4x4.html;https://www.auto-data.net/en/suzuki-swift-v-facelift-2013-1.2-94hp-4x4-5d-21694	4X4车高1535，高于前驱版本1510；Automobile-Catalog明确宽度不含后视镜。	READY
57	57	Hatchback	Suzuki Swift IV	AZG	5	2430	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	26	与来源Ktype 26的来源行26_5dr同为Swift IV/AZG五门前驱标准车身；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.3-ddis-75hp-5d-17135	五门前驱柴油版本命中26_5dr尺寸组。	READY
58	58	Convertible	Renault Megane III CC		2	2609	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	25	同代Megane III CC两门；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-2.0-16v-140hp-cvt-29896	采用不含后视镜宽1811。	READY
59	59	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
60	60	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		首次建立C-Max II改款前五门MPV尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratec-ti-vct-125hp-19845	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
61	61	Coupe	BMW 3 Series E36	E36	2	2700	EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	53	E36两门Coupe；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051		READY
62	62	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
63	63	Sedan	BMW 3 Series E36	E36	4	2700	EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	49	E36四门Sedan；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034		READY
64	64	Sedan	BMW 5 Series E12	E12	4	2636	EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		E12 518四门Sedan标准外廓	HIGH	Auto-Data; BMW Group Classic	https://www.auto-data.net/en/bmw-5-series-e12-518-90hp-9691;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-138-1.bmw-518-e12.html		READY
65	65	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Tipo 116 GTV两门Coupe标准外廓	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144125/alfa_romeo_gtv_2_0.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
66	66	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratec-ti-vct-105hp-19808	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
67	67	Coupe	Alfa Romeo GTV (116)	116	2	2400	EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	65	GTV6 2.5与GTV 2.0同属Tipo 116两门车身，轴距及外廓一致	HIGH	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144140/alfa_romeo_gtv6_2_5.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401		READY
68	68	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-ecoboost-scti-150hp-s-s-19846	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
69	69	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-ecoboost-182hp-s-s-46351	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
70	70	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60同为C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratorq-tdci-95hp-dpf-s-s-19809	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
71_prefl	71	MPV	Ford C-Max II pre-facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	60	与来源Ktype 60改款前车身一致；本Ktype同时覆盖改款前后，当前行为prefl分支	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratorq-tdci-115hp-dpf-s-s-19810	改款前分支限定为输入范围内Dec 2010-Mar 2015。	READY
71_facelift	71	MPV	Ford C-Max II facelift	C344	5	2648	EU-FORD-C-MAX-II-MPV-FACELIFT-02	4379	1828	1610	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.6 TDCi 115 PS在2015改款后继续存在；改款后长度和高度变化，建立独立尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-facelift-2015-1.6-tdci-115hp-21454	改款后分支限定为输入范围内Apr 2015-Jun 2019；不得与prefl共用尺寸组。	READY
72	72	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		首次建立Grand C-Max II改款前五门长轴MPV尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratec-ti-vct-105hp-19814	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
73	73	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-1.6-duratec-ti-vct-125hp-19854	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
74	74	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-ecoboost-scti-150hp-s-s-19855	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
75	75	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-ecoboost-182hp-s-s-56864	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
76	76	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72同为Grand C-Max II改款前五门车身；轴距及长宽高一致	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratorq-tdci-95hp-dpf-s-s-19815	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
77_prefl	77	MPV	Ford Grand C-Max II pre-facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	72	与来源Ktype 72改款前车身一致；本Ktype同时覆盖改款前后，当前行为prefl分支	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-1.6-duratorq-tdci-115hp-dpf-s-s-19816	改款前分支限定为输入范围内Dec 2010-Mar 2015。	READY
77_facelift	77	MPV	Ford Grand C-Max II facelift	C344	5	2788	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		1.6 TDCi 115 PS在2015改款后继续存在；改款后长度和高度变化，建立独立尺寸组	HIGH	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-facelift-2015-1.6-tdci-115hp-21469	改款后分支限定为输入范围内Apr 2015-Jun 2019；不得与prefl共用尺寸组。	READY
78	78	Convertible	Minelli TF 1800 MK I		2	2390	EU-MINELLI-TF-1800-CONVERTIBLE-01	3815	1680	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		Swiss type approval 1MN901直接确认两门Roadster车身、轴距及尺寸；按最大外部高度口径采用1350	HIGH	Swiss FEDRO type approval 1MN901; Minelli Automotive factory data	https://typenscheinschweiz.ch/typenschein/auto/1MN901;https://www.minelli-automotive.com/tf-1800-roadster/;https://storage.e.jimdo.com/file/7ec74357-afb3-41a4-b1e1-02ef708eed12/TF%20Fahrzeugdaten.pdf	官方型式批准列出3815×1680、车高1200-1350、轴距2390；按最大外部高度规则取1350。型式批准将左右后视镜单列，宽度1680按不含后视镜口径处理。批准备注确认瑞士制造截至Dec 2000；输入Aug 2011保留为上游Ktype日期，不据此延长车型生产期。	READY
79	79	Sedan	Saab 9-5 II	YS3G	4	2837	EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		第二代9-5四门Sedan；TTiD XWD对应同一标准外廓	HIGH	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3038990/saab_9-5_2_0_ttid_xwd.html		READY
81	81	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		902.A三门Alfasud Sprint标准外廓	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
82	82	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
83	83	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
84	84	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
85	85	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
86	86	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
87	87	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	2455	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	81	902.A三门Sprint；轴距及外廓一致	HIGH	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
88	88	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905早期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
89	89	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
90	90	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
91	91	Hatchback	Alfa Romeo 33 905	905	5	2455	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	88	905早期五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399		READY
93	93	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
94	94	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期五门车身；与来源Ktype 95的轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
95	95	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905后期五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410		READY
96	96	Hatchback	Alfa Romeo 33 905	905	5	2465	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	95	905后期1.7 QV与来源Ktype 95同一五门车身，轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410	来源目录存在114/118 hp标注差异；功率差异不改变本物理车身判断。	READY
97	97	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		905A五门Sport Wagon 4X4标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
98	98	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
99	99	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
100	100	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	2455	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	97	905A五门Sport Wagon 4X4；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417		READY
101	101	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907A五门Hatchback标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
102	102	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
103	103	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
105	105	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
107	107	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
108	108	Hatchback	Alfa Romeo 33 907A	907A	5	2475	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	101	907A五门Hatchback；轴距及外廓一致	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375		READY
109	109	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	DIRECT_NEW		907B五门Sport Wagon标准外廓	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
110	110	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
111	111	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
112	112	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
113	113	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	2475	EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	WITHOUT_MIRRORS	KNOWN	CACHE_VERIFIED	109	907B五门Sport Wagon；多个具体发动机页均为4200×1614×1350、轴距2475	HIGH	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387		READY
```

[下载本轮完成版 TSV](sandbox:/mnt/data/all_1-100_completed.tsv)

## 5) 下一步优先处理

下一步优先核对已完成；当前 split 无缺失、无待处理记录，可进入下一批输入行。

推进信号：COMPLETE

[1]: https://typenscheinschweiz.ch/typenschein/auto/1MN901?utm_source=chatgpt.com "Typenschein 1MN901 - MINELLI TF 1800 | Gratis PDF"
[2]: https://www.minelli-automotive.com/tf-1800-roadster/ "TF 1800 Roadster | Minelli Automotive"
[3]: https://typenscheinschweiz.ch/pdf/auto/1MN901?utm_source=chatgpt.com "MINELLI TF 1800"

已按新结构拆分：

* **Ktype 关系表：120 行**
* **DIMENSION_GROUP 尺寸表：26 行**
* 同一 `DIMENSION_GROUP_ID` 的长宽高无冲突。
* `WidthMM` 统一约定为 `WITHOUT_MIRRORS`，不再单独落盘 `WidthBasis`。

## 表 1：Ktype 与尺寸组关系表

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	EndDateStatus	MatchConfidence	Notes	IterationStatus
10	10	Sedan	BMW New Class 2000		4	EU-BMW-NEW-CLASS-2000-SEDAN-01	KNOWN	HIGH		READY
11	11	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
12	12	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
13	13	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
14	14	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
15	15	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
16	16	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
17	17	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
18	18	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
19	19	Sedan	BMW 3 Series E21	E21	2	EU-BMW-3-SERIES-E21-SEDAN-01	KNOWN	HIGH		READY
20_2dr	20	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
20_4dr	20	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
21_2dr	21	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
21_4dr	21	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
22_2dr	22	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
22_4dr	22	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
23_2dr	23	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
23_4dr	23	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；输入范围始于Sep 1982，四门仅覆盖Sep 1983起的重叠期间。	READY
24_2dr	24	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
24_4dr	24	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
25	25	Convertible	Renault Megane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	KNOWN	HIGH		READY
26_3dr	26	Hatchback	Suzuki Swift IV	AZG	3	EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	KNOWN	HIGH	3门物理分支。	READY
26_5dr	26	Hatchback	Suzuki Swift IV	AZG	5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	KNOWN	HIGH	5门物理分支。	READY
27_2dr	27	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
27_4dr	27	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
28	28	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	输入BodyStyle为Stufenheck，按规则标准化为Sedan；318is为两门车身。	READY
29_2dr	29	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
29_4dr	29	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
30_2dr	30	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
30_4dr	30	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
31	31	Sedan	BMW M3 E30	E30	2	EU-BMW-M3-E30-SEDAN-01	KNOWN	HIGH	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
32	32	Sedan	BMW M3 E30	E30	2	EU-BMW-M3-E30-SEDAN-01	KNOWN	HIGH	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
33_2dr	33	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。输入范围Sep 1982-Aug 1983结束于四门上市前，因此不生成4dr分支。	READY
34_2dr	34	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
34_4dr	34	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
35	35	Sedan	BMW M3 E30	E30	2	EU-BMW-M3-E30-SEDAN-01	KNOWN	HIGH	输入BodyStyle为Stufenheck，按规则标准化为Sedan；M3宽体不得命中普通E30尺寸组。	READY
36_2dr	36	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
36_4dr	36	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
37_2dr	37	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
37_4dr	37	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
38_2dr	38	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
38_4dr	38	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
39_2dr	39	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
39_4dr	39	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
40_2dr	40	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
40_4dr	40	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
41_2dr	41	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
41_4dr	41	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
42_2dr	42	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
42_4dr	42	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
43_2dr	43	Sedan	BMW 3 Series E30	E30	2	EU-BMW-3-SERIES-E30-SEDAN-2D-01	KNOWN	HIGH	E30 2门Stufenheck物理分支。	READY
43_4dr	43	Sedan	BMW 3 Series E30	E30	4	EU-BMW-3-SERIES-E30-SEDAN-4D-01	KNOWN	HIGH	E30 4门Stufenheck物理分支。四门车身自Sep 1983起供应；派生分支不早于该月且不超出输入Ktype范围。	READY
44	44	Wagon	BMW 3 Series E30 Touring	E30	5	EU-BMW-3-SERIES-E30-WAGON-01	KNOWN	HIGH		READY
45	45	Wagon	BMW 3 Series E30 Touring	E30	5	EU-BMW-3-SERIES-E30-WAGON-01	KNOWN	HIGH		READY
46	46	Wagon	BMW 3 Series E30 Touring	E30	5	EU-BMW-3-SERIES-E30-WAGON-01	KNOWN	HIGH		READY
47	47	Wagon	BMW 3 Series E30 Touring	E30	5	EU-BMW-3-SERIES-E30-WAGON-01	KNOWN	HIGH		READY
48	48	Wagon	BMW 3 Series E30 Touring	E30	5	EU-BMW-3-SERIES-E30-WAGON-01	KNOWN	HIGH		READY
49	49	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
50	50	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
51	51	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
52	52	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
53	53	Coupe	BMW 3 Series E36	E36	2	EU-BMW-3-SERIES-E36-COUPE-01	KNOWN	HIGH		READY
54	54	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
55	55	Coupe	BMW 3 Series E36	E36	2	EU-BMW-3-SERIES-E36-COUPE-01	KNOWN	HIGH		READY
56	56	Hatchback	Suzuki Swift IV	AZG	5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	KNOWN	HIGH	四驱版本外廓不同于前驱五门，使用独立尺寸组。	READY
57	57	Hatchback	Suzuki Swift IV	AZG	5	EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	KNOWN	HIGH	五门前驱柴油版本与26_5dr共用尺寸组。	READY
58	58	Convertible	Renault Megane III CC		2	EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	KNOWN	HIGH		READY
59	59	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
60	60	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
61	61	Coupe	BMW 3 Series E36	E36	2	EU-BMW-3-SERIES-E36-COUPE-01	KNOWN	HIGH		READY
62	62	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
63	63	Sedan	BMW 3 Series E36	E36	4	EU-BMW-3-SERIES-E36-SEDAN-01	KNOWN	HIGH		READY
64	64	Sedan	BMW 5 Series E12	E12	4	EU-BMW-5-SERIES-E12-SEDAN-01	KNOWN	HIGH		READY
65	65	Coupe	Alfa Romeo GTV (116)	116	2	EU-ALFA-ROMEO-GTV-116-COUPE-01	KNOWN	HIGH		READY
66	66	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
67	67	Coupe	Alfa Romeo GTV (116)	116	2	EU-ALFA-ROMEO-GTV-116-COUPE-01	KNOWN	HIGH		READY
68	68	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
69	69	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
70	70	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
71_prefl	71	MPV	Ford C-Max II pre-facelift	C344	5	EU-FORD-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	改款前分支限定为输入范围内Dec 2010-Mar 2015。	READY
71_facelift	71	MPV	Ford C-Max II facelift	C344	5	EU-FORD-C-MAX-II-MPV-FACELIFT-02	KNOWN	HIGH	改款后分支限定为输入范围内Apr 2015-Jun 2019；不得与prefl共用尺寸组。	READY
72	72	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
73	73	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
74	74	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
75	75	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
76	76	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	精确功率版本仅见于改款前代际；物理分支限定在输入范围内的改款前生产期间。	READY
77_prefl	77	MPV	Ford Grand C-Max II pre-facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	KNOWN	HIGH	改款前分支限定为输入范围内Dec 2010-Mar 2015。	READY
77_facelift	77	MPV	Ford Grand C-Max II facelift	C344	5	EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	KNOWN	HIGH	改款后分支限定为输入范围内Apr 2015-Jun 2019；不得与prefl共用尺寸组。	READY
78	78	Convertible	Minelli TF 1800 MK I		2	EU-MINELLI-TF-1800-CONVERTIBLE-01	KNOWN	HIGH	型式批准备注确认瑞士制造截至Dec 2000；输入Aug 2011保留为上游Ktype日期，不据此延长车型生产期。	READY
79	79	Sedan	Saab 9-5 II	YS3G	4	EU-SAAB-9-5-II-SEDAN-01	KNOWN	HIGH		READY
81	81	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
82	82	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
83	83	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
84	84	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
85	85	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
86	86	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
87	87	Coupe	Alfa Romeo Alfasud Sprint	902.A	3	EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	KNOWN	HIGH	输入Model为Alfasud、BodyStyle为Coupe；来源对应Alfasud Sprint 902.A。	READY
88	88	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	KNOWN	HIGH		READY
89	89	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	KNOWN	HIGH		READY
90	90	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	KNOWN	HIGH		READY
91	91	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	KNOWN	HIGH		READY
93	93	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	KNOWN	HIGH		READY
94	94	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	KNOWN	HIGH		READY
95	95	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	KNOWN	HIGH		READY
96	96	Hatchback	Alfa Romeo 33 905	905	5	EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	KNOWN	HIGH	来源目录存在114/118 hp标注差异；功率差异不改变本物理车身判断。	READY
97	97	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	KNOWN	HIGH		READY
98	98	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	KNOWN	HIGH		READY
99	99	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	KNOWN	HIGH		READY
100	100	Wagon	Alfa Romeo 33 Sport Wagon 905A	905A	5	EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	KNOWN	HIGH		READY
101	101	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
102	102	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
103	103	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
105	105	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
107	107	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
108	108	Hatchback	Alfa Romeo 33 907A	907A	5	EU-ALFA-ROMEO-33-907A-HATCHBACK-01	KNOWN	HIGH		READY
109	109	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	KNOWN	HIGH		READY
110	110	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	KNOWN	HIGH		READY
111	111	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	KNOWN	HIGH		READY
112	112	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	KNOWN	HIGH		READY
113	113	Wagon	Alfa Romeo 33 Sport Wagon 907B	907B	5	EU-ALFA-ROMEO-33-907B-WAGON-01	KNOWN	HIGH		READY
```

[下载 Ktype 与尺寸组关系表](sandbox:/mnt/data/all_1-100_ktype_dimension_mapping_final.tsv)

## 表 2：DIMENSION_GROUP 尺寸表

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-BMW-NEW-CLASS-2000-SEDAN-01	4500	1710	1445	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1968/77360/bmw_2000.html;https://www.auto-data.net/en/bmw-new-class-2000-100hp-44621
EU-BMW-3-SERIES-E21-SEDAN-01	4355	1610	1380	BMW factory technical data; Auto-Data	https://www.bmwe21.net/79_on_specs.pdf;https://www.auto-data.net/en/bmw-3-series-e21-315-75hp-10091
EU-BMW-3-SERIES-E30-SEDAN-2D-01	4325	1645	1380	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-coupe-e30-325i-171hp-46129
EU-BMW-3-SERIES-E30-SEDAN-4D-01	4325	1645	1380	BMW Group Classic; Auto-Data	https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-872-1.bmw-3-series-saloon-e30.html;https://www.auto-data.net/en/bmw-3-series-sedan-e30-325i-171hp-10088
EU-RENAULT-MEGANE-III-CC-CONVERTIBLE-01	4485	1811	1434	Auto-Data	https://www.auto-data.net/en/renault-megane-iii-cc-1.6-16v-110hp-30392
EU-SUZUKI-SWIFT-IV-HATCHBACK-3D-01	3850	1695	1510	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-3d-17132
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-01	3850	1695	1510	Auto-Data	https://www.auto-data.net/en/suzuki-swift-v-1.2-94hp-5d-17133
EU-BMW-M3-E30-SEDAN-01	4345	1680	1370	Auto-Data; BMW M	https://www.auto-data.net/en/bmw-m3-coupe-e30-2.3-195hp-cat-9886;https://www.bmw-m.com/en/topics/magazine-article-pool/bmw-m3-e30-portraet.html
EU-BMW-3-SERIES-E30-WAGON-01	4325	1645	1380	Auto-Data	https://www.auto-data.net/en/bmw-3-series-touring-e30-facelift-1987-318i-113hp-10058
EU-BMW-3-SERIES-E36-SEDAN-01	4433	1698	1393	Auto-Data	https://www.auto-data.net/en/bmw-3-series-sedan-e36-316i-102hp-10034
EU-BMW-3-SERIES-E36-COUPE-01	4433	1710	1366	Auto-Data	https://www.auto-data.net/en/bmw-3-series-coupe-e36-318is-140hp-10051
EU-SUZUKI-SWIFT-IV-HATCHBACK-5D-4X4-01	3850	1695	1535	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/2011/3405905/suzuki_swift_1_2_4x4.html;https://www.auto-data.net/en/suzuki-swift-v-facelift-2013-1.2-94hp-4x4-5d-21694
EU-FORD-C-MAX-II-MPV-PREFL-01	4380	1828	1626	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-1.6-duratec-ti-vct-125hp-19845
EU-BMW-5-SERIES-E12-SEDAN-01	4620	1690	1425	Auto-Data; BMW Group Classic	https://www.auto-data.net/en/bmw-5-series-e12-518-90hp-9691;https://www.bmwgroup-classic.com/en/models/bmw-classics/product-description-page.ad-138-1.bmw-518-e12.html
EU-ALFA-ROMEO-GTV-116-COUPE-01	4260	1664	1330	Automobile-Catalog; Auto-Data	https://www.automobile-catalog.com/car/1985/144125/alfa_romeo_gtv_2_0.html;https://www.auto-data.net/en/alfa-romeo-gtv-116-generation-401
EU-FORD-C-MAX-II-MPV-FACELIFT-02	4379	1828	1610	Auto-Data	https://www.auto-data.net/en/ford-c-max-ii-facelift-2015-1.6-tdci-115hp-21454
EU-FORD-GRAND-C-MAX-II-MPV-PREFL-01	4520	1828	1684	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-1.6-duratec-ti-vct-105hp-19814
EU-FORD-GRAND-C-MAX-II-MPV-FACELIFT-02	4519	1828	1642	Auto-Data	https://www.auto-data.net/en/ford-grand-c-max-ii-facelift-2015-1.6-tdci-115hp-21469
EU-MINELLI-TF-1800-CONVERTIBLE-01	3815	1680	1350	Swiss FEDRO type approval 1MN901; Minelli Automotive factory page; Minelli Automotive factory technical sheet	https://typenscheinschweiz.ch/typenschein/auto/1MN901;https://www.minelli-automotive.com/tf-1800-roadster/;https://storage.e.jimdo.com/file/7ec74357-afb3-41a4-b1e1-02ef708eed12/TF%20Fahrzeugdaten.pdf
EU-SAAB-9-5-II-SEDAN-01	5008	1868	1467	Automobile-Catalog	https://www.automobile-catalog.com/car/2010/3038990/saab_9-5_2_0_ttid_xwd.html
EU-ALFA-ROMEO-ALFASUD-SPRINT-COUPE-01	4019	1610	1305	Alfa Romeo 1978 brochure; Automobile-Catalog; Auto-Data	https://autocatalogarchive.com/wp-content/uploads/2016/07/Alfa-Romeo-Alfasud-Sprint-1978-GER.pdf;https://www.automobile-catalog.com/car/1978/143480/alfa_romeo_alfasud_sprint_1_3.html;https://www.auto-data.net/en/alfa-romeo-alfasud-sprint-902.a-1.3-76hp-1322
EU-ALFA-ROMEO-33-905-HATCHBACK-EARLY-01	4015	1612	1340	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.3-68hp-1399
EU-ALFA-ROMEO-33-905-HATCHBACK-LATE-02	4015	1612	1345	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-905-1.7-i.e.-105hp-1410
EU-ALFA-ROMEO-33-905A-WAGON-4X4-01	4167	1612	1345	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-905a-1.5-90hp-4x4-1417
EU-ALFA-ROMEO-33-907A-HATCHBACK-01	4075	1614	1350	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-907a-1.4-i.e.-88hp-1375
EU-ALFA-ROMEO-33-907B-WAGON-01	4200	1614	1350	Auto-Data	https://www.auto-data.net/en/alfa-romeo-33-sport-wagon-907b-1.4-i.e.-88hp-1387
```

[下载 DIMENSION_GROUP 尺寸表](sandbox:/mnt/data/all_1-100_dimension_groups_final.tsv)
