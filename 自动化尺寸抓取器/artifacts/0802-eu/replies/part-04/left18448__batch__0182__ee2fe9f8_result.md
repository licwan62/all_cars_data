# 任务：left18448 第 18101-18200 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0182__ee2fe9f8


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 18101-18200 行

【任务要求】
# EU Auto-Data Ktype 与尺寸组补全规则

输入是 Tab 分隔的欧洲车型表。`Ktype` 是输入外键，但不保证唯一对应物理车身。输出两张解耦的 TSV：Ktype 映射表和 DIMENSION_GROUP 尺寸事实表。

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

## 一、最高优先级

目标是用最少的独立尺寸研究覆盖全部输入 Ktype，不是为每个 Ktype 重复建立研究记录。顺序固定为：

1. 优先复用已闭合的 DIMENSION_GROUP。
2. 合并不改变物理外廓的发动机、能源、功率、变速箱、普通配置和 facelift 标签。
3. 仅研究缓存未覆盖的独立物理外廓。
4. `PENDING=0` 后立即进入一次机械收尾并输出 `COMPLETE`。

不存在明确冲突时，“已有可靠结果并停止”优先于“继续寻找更理想来源”。不得为补非必需字段、提高置信度、优化措辞、增加来源或枚举理论分支而增加轮次。

## 二、输出数据契约

### Ktype 映射表

- 严格使用契约中的 10 列；不输出输入原字段、三维、轴距、来源或抓取过程字段。
- `Ktype` 按文本逐字保留，不得转浮点、改前导零或生成不存在的 Ktype。每个输入 Ktype 至少一行。
- 单一物理外廓时 `id=Ktype`。确认存在多个不同物理外廓时才派生 `{Ktype}_{简短 ASCII 特征}`，如 `_3dr`、`_lwb`、`_facelift`；拆分后不保留无后缀基础行。
- 多行是例外，必须有明确物理证据；不得使用无语义序号或猜测性分支。
- `NormalizedBodyStyle`：Schrägheck/Hatchback→Hatchback，Stufenheck/Limousine/Sedan→Sedan，Kombi/Touring/Estate→Wagon，Cabriolet/Roadster→Convertible，Großraumlimousine→MPV，Kasten/Kastenwagen→Van，Pritsche→Pickup。
- `Generation`、`BodyCode`、`Doors` 是辅助字段。来源未明确时允许留空；若空值不影响外廓区分，不阻塞 `READY`。不得把发动机代号当作 `BodyCode`。
- `MatchConfidence` 只用 `HIGH|MEDIUM|LOW`，表示映射置信度；`MEDIUM/LOW` 不自动阻塞 `READY`。
- `Notes` 只记录必要的分支边界或人工决定，不重复尺寸、来源、缓存和核验过程。
- `IterationStatus` 只用 `READY` 或 `PENDING: <具体原因>`。`PENDING` 行的 `DIMENSION_GROUP_ID` 必须留空。

### DIMENSION_GROUP 表

- 严格使用契约中的 6 列。每个 `DIMENSION_GROUP_ID` 唯一，三维和来源完整，且必须被当前映射表引用。
- 同一物理外廓只使用一个稳定尺寸组；多个 Ktype 应直接复用，不得因发动机、来源或 Ktype 不同重复建组。
- 推荐 ID：`EU-{MAKE}-{MODEL}-{GENERATION}-{BODYSTYLE}-{BRANCH}-{SEQUENCE}`，只用大写 ASCII、数字和连字符。
- 若当前三维与累计表中同名 ID 冲突，不得覆盖；创建新序号 ID 并同步映射。
- `LengthMM/WidthMM/HeightMM` 是同一量产配置的正整数 mm。`WidthMM` 强制为不含外后视镜的车身宽度。不得拼接不同配置的三维。
- 只有含镜宽度或宽度口径无法确认时，该组不得落盘，映射保持 `PENDING`。

## 三、物理分支决策

### 可能需要拆分

只有可靠证据表明当前 Ktype 实际覆盖不同外廓时，才按 BodyStyle/门数外形、轴距 `SWB/LWB`、`L1/L2/L3`、车顶级别、`SRW/DRW`、CAB/BED、宽体或工厂独立特殊车身拆分。不同代际或车身代码需独立核对。

只输出当前 Ktype 有证据覆盖的分支，不得枚举该车系理论上的全部配置，不得将 prefl/facelift 与轴距、车顶、驾驶室或货斗做无证据的笛卡尔积。证据只确认一个分支时只输出该分支；无法确认是否多分支时，保留单行并使用最匹配输入的标准量产外廓。

### Facelift

facelift、LCI、Phase II、改款年份或外观名称本身不是拆分或新建尺寸组的充分条件。

1. 先判断改款是否改变 BodyStyle、门数、BodyCode、轴距/车顶/驾驶室/货斗级别或标准量产三维。
2. 无可靠证据证明上述差异，或资料明确显示三维相同时，视为同一物理外廓：不建 `_prefl/_facelift` 派生行，保留一行并复用同一尺寸组。
3. 只有可靠资料明确证明至少一个三维值或物理边界不同，才拆分并建立不同尺寸组。
4. Ktype 生产期跨越改款日期只是线索，不能单独触发拆分。

### 不拆分

发动机、功率、燃料/能源、变速箱、不改外廓的驱动形式和普通配置不触发拆分或重新抓取。

可拆卸车顶行李架/横杆、天线、普通轮胎轮毂、装饰包、非独立车身的保险杠/扰流板和其他非永久附件默认不拆分。`HeightMM` 优先使用不含可拆附件的标准车身高度；不得仅因资料同时列出含/不含行李架高度而创建 lowroof/highroof。只有工厂定义为独立量产车身且 Ktype 明确覆盖时才例外。

## 四、来源与停止条件

优先级：厂商官网/手册/技术资料/认证资料 > Auto-Data、Car.info、UltimateSpecs、Automobile-Catalog、Parkers > 其他可追溯规格数据库。搜索摘要、AI 摘要、论坛、二手车广告和无出处聚合页不能单独支撑尺寸组。`SourceURL` 必须是直接页面，不得是搜索结果页。

满足任一条后立即闭合，不再搜索：

1. 一个官方来源支持同一配置的完整三维，且宽度口径可确认；
2. 一个允许的可信规格数据库给出匹配车型的完整三维，且未发现具体冲突；
3. 最多两个可靠来源合计支持同一配置的完整三维。

官方来源不是 `READY` 的强制条件。已有可信二级来源且无冲突时，不得仅为寻找官方页面或提高 `MatchConfidence` 继续搜索。只有同市场、同阶段、同车身/配置、同测量口径下存在具体数值冲突，或宽度口径不明时，才增加核验。

## 五、每批执行流程

1. 一次读取当前批全部输入。
2. 按 Make + Model + Generation 候选 + BodyStyle + BodyCode 候选聚类，先消除只由动力和普通配置造成的重复。
3. 查询当前批及历史缓存，批量关联已有尺寸组。已闭合组不得重新打开来源页。
4. 只对缓存未命中的独立物理外廓抓取一次；一个组闭合后立即关联所有适用 Ktype。
5. 最后只处理无组可关联的 `PENDING`。不得按 Ktype 串行重复搜索同一外廓。
6. `PENDING=0` 后停止外部检索，最多执行一次表头、唯一性、引用闭合、非空和链接检查，然后立即 `COMPLETE`。

## 六、输出与终检

### CONTINUE

未完成时仅依次输出：更新点、当前批进度、本轮新增/修改的 Ktype TSV、本轮首次创建/修正的 DIMENSION_GROUP TSV、下一步优先处理，最后一行 `推进信号：CONTINUE`。无变化写“无”；不重复输出未变行或已闭合尺寸组。

### COMPLETE

`PENDING=0` 后的下一条回复必须在同一条消息中依次包含：更新点、进度、最终完整 Ktype TSV、按任务指定文件名创建的可点击 `.tsv` sandbox 链接、最终完整 DIMENSION_GROUP TSV、对应 sandbox 链接，最后一行 `推进信号：COMPLETE`。不得只给变化行、引用上轮或写“其余不变”。

终检只做以下机械项，不重新研究：

1. 两张表的固定表头和列数正确，`id` 与 `DIMENSION_GROUP_ID` 各自唯一。
2. 每个输入 Ktype 至少被覆盖一次；每个映射均为 `READY` 并引用恰好一个存在的尺寸组。
3. 尺寸组三维为正整数、宽度不含后视镜、来源和直接 URL 非空，且没有孤立组。
4. 不存在 `PENDING`、未解决冲突、重复物理组或无证据派生分支。
5. 两个任务指定文件名的可点击 sandbox 链接齐全。

任一机械项不满足时只修复该项，不得重新展开逐车型或逐来源研究；修复后立即输出两张完整表、两个链接和 `COMPLETE`。


【执行顺序】
执行顺序固定为：第一阶段优先消除 PENDING 并补齐会阻塞两张最终表的数据。检测到 PENDING=0 后，第二阶段最多只做一次轻量机械收尾：核对固定表头、id 与 DIMENSION_GROUP_ID 唯一、映射引用闭合、长宽高和来源非空、两个任务指定下载链接齐全。第二阶段不得重新逐车型、逐年份或逐来源做深度检索，不得为了提高置信度反复核对，也不得因非阻塞的排序或措辞问题继续多轮。PENDING=0 后的下一条回复必须直接输出两张最终完整 TSV、两个精确 sandbox 下载链接，并以“推进信号：COMPLETE”结束；不要再输出 CONTINUE。

【配置附加规则】


【当前文件名】
left18448.tsv

【当前独立任务】
left18448 第 18101-18200 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_18101-18200_ktype_dimension_mapping_final.tsv
- left18448_18101-18200_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VW-SHARAN-I-7M-MPV-STANDARD-01	4617	1810	1728
EU-VW-SHARAN-II-7N-MPV-STANDARD-01	4854	1904	1720

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
VW	Sharan	2.0 Tfsi	Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Nov 2015	6021
VW	Sharan	2.0 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Dec 2020	115205
VW	Sharan	2.0 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	Dec 2010	Nov 2015	143005
VW	Sharan	2.8 V6 24V	Großraumlimousine	Frontantrieb	Benzin	Apr 2000	Mar 2010	14854
VW	Sharan	2.8 V6 24V 4motion	Großraumlimousine	Allrad	Benzin	Apr 2000	Mar 2010	14896
VW	Sharan	2.8 VR6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Sep 1996	Apr 2000	143013
VW	Sharan	2.8 VR6	Kasten/Großraumlimousine	Frontantrieb	Benzin	Aug 2001	May 2003	143014
VW	Sharan	2.8 VR6 Syncro	Großraumlimousine	Allrad	Benzin	Nov 1996	Apr 2000	5723
VW	Taigo	1.0 TSI	SUV	Frontantrieb	Benzin	Sep 2021	-	145048
VW	Taigo	1.0 TSI	SUV	Frontantrieb	Benzin	Sep 2021	Mar 2024	145049
VW	Taigo	1.0 TSI	SUV	Frontantrieb	Benzin	Nov 2021	-	148190
VW	Taigo	1.5 TSI	SUV	Frontantrieb	Benzin	Sep 2021	-	145050
VW	Taro	2.2	Pick-up	Heckantrieb	Benzin	Jun 1989	Jul 1994	5964
VW	Taro	2.2 4X4	Pick-up	Allrad	Benzin	Jun 1989	Jul 1994	12105
VW	Taro	2.4 D	Pick-up	Heckantrieb	Diesel	Jul 1994	Mar 1997	10480
VW	Taro	2.4 D	Pick-up	Heckantrieb	Diesel	Jun 1989	Mar 1997	10481
VW	Taro	2.4 D 4X4	Pick-up	Allrad	Diesel	Apr 1989	Mar 1997	18624
VW	Tayron	1.5 Ehybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	-	159795
VW	Tayron	1.5 Ehybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	-	159949
VW	Tayron	1.5 Etsi	SUV	Frontantrieb	Benzin/Elektro	Nov 2024	-	159794
VW	Tayron	2.0 TDI	SUV	Frontantrieb	Diesel	Nov 2024	-	160050
VW	Tayron	2.0 TDI 4motion	SUV	Allrad	Diesel	Nov 2024	-	159785
VW	Tayron	2.0 TSI 4motion	SUV	Allrad	Benzin	Nov 2024	-	160197
VW	Tayron	2.0 TSI 4motion	SUV	Allrad	Benzin	Nov 2024	-	160206
VW	Tiguan	1.4 Ehybrid	SUV	Frontantrieb	Benzin/Elektro	Nov 2020	Apr 2024	143258
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	May 2011	Jul 2018	10929
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	May 2015	Jul 2018	113334
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	May 2015	Jul 2018	116130
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	Jan 2016	Mar 2022	119767
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	May 2016	Mar 2022	119768
VW	Tiguan	1.4 TSI	SUV	Frontantrieb	Benzin	Jun 2017	-	128188
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	Aug 2010	May 2011	143019
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	May 2008	May 2010	143020
VW	Tiguan	1.4 TSI	Kasten/SUV	Frontantrieb	Benzin	Sep 2012	Jul 2018	143021
VW	Tiguan	1.4 TSI 4motion	SUV	Allrad	Benzin	May 2011	Jul 2018	10932
VW	Tiguan	1.4 TSI 4motion	SUV	Allrad	Benzin	May 2016	Mar 2022	120209
VW	Tiguan	1.4 TSI 4motion	Kasten/SUV	Allrad	Benzin	Sep 2012	Jul 2018	143022
VW	Tiguan	1.5 Etsi	SUV	Frontantrieb	Benzin/Elektro	Sep 2023	-	157054
VW	Tiguan	1.5 Etsi	SUV	Frontantrieb	Benzin/Elektro	Sep 2023	-	157055
VW	Tiguan	1.5 TSI Ehybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2024	-	158026
VW	Tiguan	1.5 TSI Ehybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2024	-	158113
VW	Tiguan	1.6 TDI	SUV	Frontantrieb	Diesel	May 2016	Jun 2020	122007
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	May 2015	Jul 2018	112955
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	Jan 2016	Apr 2024	118647
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	May 2016	Jul 2019	120210
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	Aug 2016	Jul 2020	124068
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	Jun 2017	-	128190
VW	Tiguan	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	May 2010	Jul 2011	143040
VW	Tiguan	2.0 TDI	Kasten/SUV	Frontantrieb	Diesel	Nov 2009	Jul 2018	143041
VW	Tiguan	2.0 TDI	SUV	Frontantrieb	Diesel	Sep 2023	-	157056
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Nov 2012	Jul 2018	57510
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	May 2015	Jul 2018	112956
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	May 2015	Jul 2018	113340
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Jan 2016	Apr 2024	118648
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Apr 2016	Jul 2020	119690
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	May 2016	Jul 2020	119766
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Aug 2016	Jul 2020	124077
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Jun 2017	-	128191
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Jun 2017	Jul 2021	128192
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Jun 2017	Sep 2020	128193
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	Nov 2007	Jul 2018	143042
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	May 2010	May 2013	143043
VW	Tiguan	2.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	Nov 2012	Jul 2018	143044
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Jun 2020	-	144761
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Sep 2023	-	157100
VW	Tiguan	2.0 TDI 4motion	SUV	Allrad	Diesel	Mar 2024	-	803196
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	May 2011	Jul 2018	10935
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	May 2011	Jul 2018	10954
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Jan 2016	Apr 2024	118646
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Jun 2016	Apr 2024	121841
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Mar 2017	-	128189
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	Nov 2009	May 2011	143037
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	Nov 2009	May 2011	143038
VW	Tiguan	2.0 TSI 4motion	Kasten/SUV	Allrad	Benzin	May 2011	Jul 2018	143039
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Jan 2021	Apr 2024	143253
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Sep 2020	-	144806
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Aug 2024	-	800130
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Nov 2024	-	800952
VW	Tiguan	2.0 TSI 4motion	SUV	Allrad	Benzin	Mar 2021	Apr 2024	801688
VW	Tiguan	2.0 TSI R 4motion	SUV	Allrad	Benzin	Nov 2020	Apr 2024	142540
VW	Touareg	2.5 R5 TDI	SUV	Allrad	Diesel	Jan 2003	May 2010	17182
VW	Touareg	3.0 Ehybrid 4motion	SUV	Allrad	Benzin/Elektro	Nov 2020	-	143255
VW	Touareg	3.0 R 4motion	SUV	Allrad	Benzin/Elektro	Sep 2020	-	143256
VW	Touareg	3.0 TDI 4motion	Kasten/SUV	Allrad	Diesel	May 2011	Dec 2014	143057
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	Nov 2004	May 2010	18428
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	Jun 2010	Mar 2018	58984
VW	Touareg	3.0 V6 TDI	SUV	Allrad	Diesel	Sep 2014	Mar 2018	107860
VW	Touareg	3.2 V6	SUV	Allrad	Benzin	Oct 2002	Nov 2006	16819
VW	Touareg	3.2 V6	SUV	Allrad	Benzin	Nov 2004	Nov 2006	18427
VW	Touareg	4.2 V8	SUV	Allrad	Benzin	Dec 2002	Nov 2006	17178
VW	Touareg	5.0 V10 TDI	SUV	Allrad	Diesel	Oct 2002	May 2010	16820
VW	Touareg	6.0 W12	SUV	Allrad	Benzin	Aug 2004	May 2010	18527
VW	Touran	1.6	Großraumlimousine	Frontantrieb	Benzin	Jul 2003	May 2010	17572
VW	Touran	1.2 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Jul 2018	113148
VW	Touran	1.2 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2010	May 2015	143045
VW	Touran	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2010	May 2015	55510
VW	Touran	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2010	May 2015	55585
VW	Touran	1.4 TSI	Großraumlimousine	Frontantrieb	Benzin	May 2015	Jul 2022	113149
VW	Touran	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2010	May 2015	142643
VW	Touran	1.4 TSI	Kasten/Großraumlimousine	Frontantrieb	Benzin	May 2010	May 2015	142645


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个 Ktype 已全部闭合，共复用或建立 19 个独立尺寸组。Tayron 按官方数据区分 5 座 PHEV 与 7 座标准车身；第三代 Tiguan 使用无后视镜宽度 1842 mm 的标准量产外廓；跨越 facelift 的宽泛 Ktype 保留单行，按起始阶段映射，未进行无证据拆分。([大众汽车英国][1])

## 进度

* 输入 Ktype：100
* READY：100
* PENDING：0
* DIMENSION_GROUP：19
* 映射引用闭合：是
* 孤立尺寸组：0
* 固定列数、唯一 ID、正整数三维、来源与直接 URL：检查通过

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
6021	6021	MPV	II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
115205	115205	MPV	II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
143005	143005	MPV	II	7N	5	EU-VW-SHARAN-II-7N-MPV-STANDARD-01	HIGH		READY
14854	14854	MPV	I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
14896	14896	MPV	I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
143013	143013	MPV	I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
143014	143014	MPV	I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
5723	5723	MPV	I	7M	5	EU-VW-SHARAN-I-7M-MPV-STANDARD-01	HIGH		READY
145048	145048	SUV	I	CS	5	EU-VW-TAIGO-I-CS-SUV-STANDARD-01	HIGH		READY
145049	145049	SUV	I	CS	5	EU-VW-TAIGO-I-CS-SUV-STANDARD-01	HIGH		READY
148190	148190	SUV	I	CS	5	EU-VW-TAIGO-I-CS-SUV-STANDARD-01	HIGH		READY
145050	145050	SUV	I	CS	5	EU-VW-TAIGO-I-CS-SUV-STANDARD-01	HIGH		READY
5964	5964	Pickup	I	7A	2	EU-VW-TARO-I-7A-PICKUP-RWD-01	MEDIUM	Cab/bed subtype is not stated; mapped to the standard single-cab pickup outer body for the specified drivetrain.	READY
12105	12105	Pickup	I	7A	2	EU-VW-TARO-I-7A-PICKUP-4X4-01	MEDIUM	Cab/bed subtype is not stated; mapped to the standard single-cab pickup outer body for the specified drivetrain.	READY
10480	10480	Pickup	I	7A	2	EU-VW-TARO-I-7A-PICKUP-RWD-01	MEDIUM	Cab/bed subtype is not stated; mapped to the standard single-cab pickup outer body for the specified drivetrain.	READY
10481	10481	Pickup	I	7A	2	EU-VW-TARO-I-7A-PICKUP-RWD-01	MEDIUM	Cab/bed subtype is not stated; mapped to the standard single-cab pickup outer body for the specified drivetrain.	READY
18624	18624	Pickup	I	7A	2	EU-VW-TARO-I-7A-PICKUP-4X4-01	MEDIUM	Cab/bed subtype is not stated; mapped to the standard single-cab pickup outer body for the specified drivetrain.	READY
159795	159795	SUV	2024		5	EU-VW-TAYRON-2024-SUV-PHEV-01	HIGH	PHEV five-seat outer height differs from the standard seven-seat body.	READY
159949	159949	SUV	2024		5	EU-VW-TAYRON-2024-SUV-PHEV-01	HIGH	PHEV five-seat outer height differs from the standard seven-seat body.	READY
159794	159794	SUV	2024		5	EU-VW-TAYRON-2024-SUV-STANDARD-01	HIGH		READY
160050	160050	SUV	2024		5	EU-VW-TAYRON-2024-SUV-STANDARD-01	HIGH		READY
159785	159785	SUV	2024		5	EU-VW-TAYRON-2024-SUV-STANDARD-01	HIGH		READY
160197	160197	SUV	2024		5	EU-VW-TAYRON-2024-SUV-STANDARD-01	HIGH		READY
160206	160206	SUV	2024		5	EU-VW-TAYRON-2024-SUV-STANDARD-01	HIGH		READY
143258	143258	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	HIGH		READY
10929	10929	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
113334	113334	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
116130	116130	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
119767	119767	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
119768	119768	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
128188	128188	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143019	143019	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	HIGH		READY
143020	143020	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	HIGH		READY
143021	143021	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
10932	10932	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
120209	120209	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143022	143022	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
157054	157054	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
157055	157055	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
158026	158026	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
158113	158113	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
122007	122007	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
112955	112955	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
118647	118647	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
120210	120210	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
124068	124068	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
128190	128190	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143040	143040	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2011 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143041	143041	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2011 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
157056	157056	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
57510	57510	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
112956	112956	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
113340	113340	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
118648	118648	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
119690	119690	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
119766	119766	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
124077	124077	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
128191	128191	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
128192	128192	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
128193	128193	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	HIGH		READY
143042	143042	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2011 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143043	143043	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2011 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143044	143044	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
144761	144761	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	MEDIUM	Mapped to the 2020 facelift outer body at the model-change boundary.	READY
157100	157100	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
803196	803196	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
10935	10935	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
10954	10954	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
118646	118646	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
121841	121841	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
128189	128189	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2020 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
143037	143037	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	HIGH		READY
143038	143038	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	HIGH		READY
143039	143039	SUV	I	5N	5	EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	HIGH		READY
143253	143253	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	HIGH		READY
144806	144806	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	HIGH		READY
800130	800130	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
800952	800952	SUV	III	CT1	5	EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	HIGH		READY
801688	801688	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	HIGH		READY
142540	142540	SUV	II	AD1	5	EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	HIGH		READY
17182	17182	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
143255	143255	SUV	III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PHEV-01	HIGH		READY
143256	143256	SUV	III	CR	5	EU-VW-TOUAREG-III-CR-SUV-PHEV-01	HIGH		READY
143057	143057	SUV	II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFACELIFT-01	HIGH		READY
18428	18428	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
58984	58984	SUV	II	7P	5	EU-VW-TOUAREG-II-7P-SUV-PREFACELIFT-01	MEDIUM	Ktype range spans the 2014 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
107860	107860	SUV	II	7P	5	EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	HIGH		READY
16819	16819	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
18427	18427	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
17178	17178	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
16820	16820	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
18527	18527	SUV	I	7L	5	EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	HIGH		READY
17572	17572	MPV	I	1T	5	EU-VW-TOURAN-I-1T-MPV-EARLY-01	MEDIUM	Ktype range spans the 2006 facelift; retained the launch-phase outer body without a Ktype-specific physical split.	READY
113148	113148	MPV	II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
143045	143045	MPV	I	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
55510	55510	MPV	I	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
55585	55585	MPV	I	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
113149	113149	MPV	II	5T	5	EU-VW-TOURAN-II-5T-MPV-STANDARD-01	HIGH		READY
142643	142643	MPV	I	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
142645	142645	MPV	I	1T3	5	EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_18101-18200_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VW-SHARAN-I-7M-MPV-STANDARD-01	4617	1810	1728	Volkswagen Newsroom vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-sharan-1-profile-19714
EU-VW-SHARAN-II-7N-MPV-STANDARD-01	4854	1904	1720	Auto-Data.net	https://www.auto-data.net/en/volkswagen-sharan-ii-2.0-tdi-bmt-170hp-44609
EU-VW-TAIGO-I-CS-SUV-STANDARD-01	4266	1757	1515	Auto-Data.net	https://www.auto-data.net/en/volkswagen-taigo-1.0-tsi-95hp-44420
EU-VW-TARO-I-7A-PICKUP-RWD-01	4725	1650	1550	Automoli	https://www.automoli.com/us/vehicles/volkswagen/taro/taro-1917/
EU-VW-TARO-I-7A-PICKUP-4X4-01	4725	1690	1745	Auto-Data.net	https://www.auto-data.net/en/volkswagen-taro-2.4-d-83hp-4wd-9165
EU-VW-TAYRON-2024-SUV-STANDARD-01	4792	1853	1668	Volkswagen UK dimensions	https://www.volkswagen.co.uk/en/new/tayron/tayron-dimensions.html
EU-VW-TAYRON-2024-SUV-PHEV-01	4792	1853	1666	Volkswagen UK dimensions	https://www.volkswagen.co.uk/en/new/tayron/tayron-dimensions.html
EU-VW-TIGUAN-I-5N-SUV-PREFACELIFT-01	4427	1809	1686	Volkswagen UK brochure	https://www.volkswagen.co.uk/idhub/content/dam/onehub_pkw/importers/gb/downloads/brochures/used-cars/tiguan/tiguan-gp/vw-tiguan-gp-brochure-june-2009.pdf
EU-VW-TIGUAN-I-5N-SUV-FACELIFT-01	4426	1809	1703	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-i-facelift-2011-1.4-tsi-bmt-122hp-16863
EU-VW-TIGUAN-II-AD1-SUV-PREFACELIFT-01	4486	1839	1673	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-ii-2.0-tdi-150hp-4motion-scr-28585
EU-VW-TIGUAN-II-AD1-SUV-FACELIFT-01	4509	1839	1684	Auto-Data.net	https://www.auto-data.net/en/volkswagen-tiguan-ii-facelift-2020-2.0-tsi-190hp-4motion-dsg-44379
EU-VW-TIGUAN-III-CT1-SUV-STANDARD-01	4539	1842	1658	Volkswagen UK technical data	https://www.volkswagen.co.uk/en/new/tiguan.html/__ui/technical-data.app?p=3
EU-VW-TOUAREG-I-7L-SUV-STANDARD-01	4754	1928	1726	Volkswagen Newsroom vehicle data	https://www.volkswagen-newsroom.com/en/vehicle-data-touareg-1-profile-19718
EU-VW-TOUAREG-II-7P-SUV-PREFACELIFT-01	4795	1940	1709	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touareg-ii-7p-3.0-tdi-v6-245hp-4motion-automatic-18460
EU-VW-TOUAREG-II-7P-SUV-FACELIFT-01	4801	1940	1709	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touareg-ii-7p-facelift-2014-3.0-v6-tsi-320hp-4motion-tiptronic-55164
EU-VW-TOUAREG-III-CR-SUV-PHEV-01	4878	1984	1717	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touareg-iii-cr-3.0-v6-tsi-381hp-ehybrid-4motion-tiptronic-41524
EU-VW-TOURAN-I-1T-MPV-EARLY-01	4391	1794	1635	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touran-i-1.6-i-102hp-8540
EU-VW-TOURAN-I-1T3-MPV-FACELIFT-01	4397	1794	1674	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touran-i-facelift-2010-1.4-tsi-140hp-16853
EU-VW-TOURAN-II-5T-MPV-STANDARD-01	4527	1829	1659	Auto-Data.net	https://www.auto-data.net/en/volkswagen-touran-ii-1.2-tsi-110hp-22686
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_18101-18200_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volkswagen.co.uk/en/new/tayron/tayron-dimensions.html "https://www.volkswagen.co.uk/en/new/tayron/tayron-dimensions.html"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（5188 行）
- 累计尺寸组：dimension_groups_final.tsv（1212 行）

