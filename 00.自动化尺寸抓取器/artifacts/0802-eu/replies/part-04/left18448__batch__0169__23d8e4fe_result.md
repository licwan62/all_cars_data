# 任务：left18448 第 16801-16900 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0169__23d8e4fe


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16801-16900 行

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
left18448 第 16801-16900 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16801-16900_ktype_dimension_mapping_final.tsv
- left18448_16801-16900_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	4369	1802	1420
EU-VOLVO-V40-I-WAGON-FACELIFT-01	4516	1716	1425
EU-VOLVO-V40-I-WAGON-PREFL-01	4480	1720	1410

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Volvo	V40	T2 Gtdi	Schrägheck	Frontantrieb	Benzin	Apr 2013	Dec 2016	59370
Volvo	V40	T3	Schrägheck	Frontantrieb	Benzin	Feb 2015	Aug 2019	111858
Volvo	V40	T3	Schrägheck	Frontantrieb	Benzin	Feb 2015	Aug 2019	112556
Volvo	V40	T3 Gtdi	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2016	55096
Volvo	V40	T4	Schrägheck	Frontantrieb	Benzin	Apr 2014	Dec 2015	107462
Volvo	V40	T4	Schrägheck	Frontantrieb	Benzin	Aug 2015	Aug 2019	116592
Volvo	V40	T4 Gtdi	Schrägheck	Frontantrieb	Benzin	Mar 2012	Dec 2016	55097
Volvo	V40	T5	Schrägheck	Frontantrieb	Benzin	Dec 2012	Dec 2014	57488
Volvo	V40	T5	Schrägheck	Frontantrieb	Benzin	Mar 2013	Dec 2015	58973
Volvo	V40	T5	Schrägheck	Frontantrieb	Benzin	May 2014	Aug 2019	106280
Volvo	V40 cross country	2.0 D3	Kasten/Schrägheck	Frontantrieb	Diesel	Sep 2013	Dec 2015	147906
Volvo	V40 cross country	D2	Schrägheck	Frontantrieb	Diesel	Feb 2015	Aug 2019	147901
Volvo	V40 cross country	D2	Schrägheck	Frontantrieb	Diesel	Oct 2012	Dec 2016	147919
Volvo	V40 cross country	D3	Schrägheck	Frontantrieb	Diesel	Apr 2015	Aug 2019	147903
Volvo	V40 cross country	D3	Schrägheck	Frontantrieb	Diesel	Oct 2012	Mar 2015	147920
Volvo	V40 cross country	D4	Schrägheck	Frontantrieb	Diesel	May 2014	Aug 2019	147896
Volvo	V40 cross country	D4	Schrägheck	Frontantrieb	Diesel	Oct 2012	Dec 2014	147922
Volvo	V40 cross country	D4 Polestar	Schrägheck	Frontantrieb	Diesel	May 2014	Aug 2019	147908
Volvo	V40 cross country	T3	Schrägheck	Frontantrieb	Benzin	Feb 2015	Aug 2019	147900
Volvo	V40 cross country	T3	Schrägheck	Frontantrieb	Benzin	Apr 2015	Aug 2019	147902
Volvo	V40 cross country	T4	Schrägheck	Frontantrieb	Benzin	Aug 2015	Aug 2019	147904
Volvo	V40 cross country	T4	Schrägheck	Frontantrieb	Benzin	Oct 2013	Dec 2015	147909
Volvo	V40 cross country	T4 AWD	Schrägheck	Allrad	Benzin	May 2014	Aug 2019	112412
Volvo	V40 cross country	T4 Gtdi	Schrägheck	Frontantrieb	Benzin	Oct 2012	Dec 2016	147917
Volvo	V40 cross country	T5	Schrägheck	Frontantrieb	Benzin	Oct 2012	Dec 2016	147923
Volvo	V40 cross country	T5	Schrägheck	Frontantrieb	Benzin	Feb 2013	Dec 2015	147924
Volvo	V40 cross country	T5 AWD	Schrägheck	Allrad	Benzin	Oct 2012	Dec 2016	59786
Volvo	V40 cross country	T5 AWD	Schrägheck	Allrad	Benzin	May 2014	Aug 2019	108766
Volvo	V50	1.6	Kombi	Frontantrieb	Benzin	Jan 2005	Dec 2012	18603
Volvo	V50	1.8	Kombi	Frontantrieb	Benzin	Apr 2004	Dec 2010	18113
Volvo	V50	2.4	Kombi	Frontantrieb	Benzin	Apr 2004	Dec 2010	17820
Volvo	V50	2.4	Kombi	Frontantrieb	Benzin	Apr 2004	Dec 2010	17821
Volvo	V50	1.6 D	Kombi	Frontantrieb	Diesel	Jan 2005	Dec 2011	18604
Volvo	V50	1.6 D	Kombi	Frontantrieb	Diesel	Mar 2005	Dec 2012	128504
Volvo	V50	2.0 D	Kombi	Frontantrieb	Diesel	Apr 2004	Dec 2010	17906
Volvo	V50	2.0 Flexfuel	Kombi	Frontantrieb	Benzin/Ethanol	Jan 2010	Dec 2012	33822
Volvo	V50	D2	Kombi	Frontantrieb	Diesel	Jan 2010	Dec 2012	33806
Volvo	V50	T5	Kombi	Frontantrieb	Benzin	Apr 2004	Dec 2007	17824
Volvo	V50	T5 AWD	Kombi	Allrad	Benzin	Apr 2004	Dec 2007	18112
Volvo	V60 i	1.6 Drive	Kombi	Frontantrieb	Diesel	Feb 2011	Dec 2015	10248
Volvo	V60 i	2.0 Polestar AWD	Kombi	Allrad	Benzin	Jun 2015	May 2018	120524
Volvo	V60 i	2.0 T	Kombi	Frontantrieb	Benzin	Jul 2010	Dec 2012	6047
Volvo	V60 i	2.0 T	Kombi	Frontantrieb	Benzin	Jan 2014	Jul 2018	128085
Volvo	V60 i	3.0 T AWD	Kombi	Allrad	Benzin	Apr 2014	May 2018	106318
Volvo	V60 i	D2	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	113270
Volvo	V60 i	D3	Kombi	Frontantrieb	Diesel	May 2012	Dec 2015	57495
Volvo	V60 i	D3	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	113271
Volvo	V60 i	D3 / D4	Kombi	Frontantrieb	Diesel	Jul 2010	Dec 2014	6051
Volvo	V60 i	D4	Kombi	Frontantrieb	Diesel	Oct 2013	Dec 2015	100369
Volvo	V60 i	D4	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	113272
Volvo	V60 i	D4 AWD	Kombi	Allrad	Diesel	May 2012	Dec 2015	57496
Volvo	V60 i	D4 AWD	Kombi	Allrad	Diesel	Oct 2013	Dec 2015	100372
Volvo	V60 i	D4 AWD	Kombi	Allrad	Diesel	Mar 2015	May 2018	113273
Volvo	V60 i	D5	Kombi	Frontantrieb	Diesel	Apr 2011	Dec 2015	10275
Volvo	V60 i	D5	Kombi	Frontantrieb	Diesel	Apr 2014	Dec 2015	107466
Volvo	V60 i	D5	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	113274
Volvo	V60 i	D5 AWD	Kombi	Allrad	Diesel	Apr 2011	Dec 2015	10277
Volvo	V60 i	D5 AWD	Kombi	Allrad	Diesel	Apr 2014	Dec 2015	107467
Volvo	V60 i	D5 Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Mar 2015	May 2018	116225
Volvo	V60 i	D6 Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Jun 2012	Dec 2015	55138
Volvo	V60 i	D6 Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Mar 2015	May 2018	113276
Volvo	V60 i	T2	Kombi	Frontantrieb	Benzin	Oct 2015	Mar 2017	119086
Volvo	V60 i	T3	Kombi	Frontantrieb	Benzin	Mar 2015	May 2018	113278
Volvo	V60 i	T3	Kombi	Frontantrieb	Benzin	Mar 2015	May 2018	113280
Volvo	V60 i	T4	Kombi	Frontantrieb	Benzin	Mar 2015	May 2018	114200
Volvo	V60 i	T4F	Kombi	Frontantrieb	Benzin/Ethanol	Apr 2011	Dec 2015	12693
Volvo	V60 i	T5	Kombi	Frontantrieb	Benzin	Oct 2013	Dec 2018	100376
Volvo	V60 i	T5	Kombi	Frontantrieb	Benzin	Oct 2013	May 2018	100402
Volvo	V60 i	T5	Kombi	Frontantrieb	Benzin	Jan 2014	Dec 2017	128084
Volvo	V60 i	T5 AWD	Kombi	Allrad	Benzin	Jul 2014	May 2018	107415
Volvo	V60 i	T5 AWD	Kombi	Allrad	Benzin	Apr 2015	May 2018	116595
Volvo	V60 i	T6	Kombi	Frontantrieb	Benzin	Oct 2013	Dec 2018	100377
Volvo	V60 i	T6 AWD	Kombi	Allrad	Benzin	Apr 2014	Dec 2015	107414
Volvo	V60 i	T6 AWD	Kombi	Allrad	Benzin	Oct 2013	Dec 2018	117791
Volvo	V60 i cross country	D2	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	147939
Volvo	V60 i cross country	D3	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	147942
Volvo	V60 i cross country	D4	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	147945
Volvo	V60 i cross country	D4 AWD	Kombi	Allrad	Diesel	Mar 2015	May 2018	147947
Volvo	V60 i cross country	D5	Kombi	Frontantrieb	Diesel	Mar 2015	May 2018	147948
Volvo	V60 i cross country	D5 Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Mar 2015	May 2018	147949
Volvo	V60 i cross country	T5	Kombi	Frontantrieb	Benzin	Mar 2015	May 2018	147937
Volvo	V60 i cross country	T5 AWD	Kombi	Allrad	Benzin	Jun 2016	May 2018	147938
Volvo	V60 i cross country	T5 AWD	Kombi	Allrad	Benzin	Mar 2015	May 2018	147950
Volvo	V60 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Diesel/Elektro	Mar 2020	-	145168
Volvo	V60 ii	T6 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	May 2022	-	151838
Volvo	V60 ii	T6 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	May 2026	-	803454
Volvo	V60 ii	T8 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	May 2022	-	146658
Volvo	V60 ii	T8 Recharge AWD	Kombi	Allrad	Benzin/Elektro	Jan 2023	-	151713
Volvo	V60 ii cross country	B4 Mild-hybrid AWD	Kombi	Allrad	Diesel/Elektro	Oct 2020	-	145169
Volvo	V60 ii cross country	B5 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	Mar 2022	-	147098
Volvo	V60 ii cross country	B5 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	Jan 2020	-	147956
Volvo	V60 ii cross country	D3 AWD	Kombi	Allrad	Diesel	Dec 2018	Dec 2021	147951
Volvo	V60 ii cross country	D4 AWD	Kombi	Allrad	Diesel	Dec 2018	Dec 2021	147952
Volvo	V60 ii cross country	D4 Polestar AWD	Kombi	Allrad	Diesel	Feb 2018	Dec 2020	147955
Volvo	V60 ii cross country	T5 AWD	Kombi	Allrad	Benzin	Dec 2018	Dec 2021	147953
Volvo	V60 ii cross country	T5 Polestar AWD	Kombi	Allrad	Benzin	Jul 2019	-	147954
Volvo	V70 i	2	Kombi	Frontantrieb	Benzin	Jan 1997	Dec 2000	18317
Volvo	V70 i	2.4	Kombi	Frontantrieb	Benzin	Jun 1998	Dec 1999	11063
Volvo	V70 i	2.4	Kombi	Frontantrieb	Benzin	Mar 1999	Dec 2000	14440
Volvo	V70 i	2.3 T AWD	Kombi	Allrad	Benzin	Apr 1997	Mar 2000	11227


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个 Ktype 已全部闭合，共复用或建立 9 个独立物理尺寸组。V40 标准版复用跨批次已有组；V40 Cross Country、V60 Cross C([沃尔沃汽车][1])II Cross Country 使用官方外车身宽度 **1893 mm**，未误用页面括号中的 **1850 mm 底盘宽度**。([沃尔沃汽车][1])([沃尔沃汽车][1])ype `803454` 对应 2026 V60 Plug-in Hybrid，官方尺寸已变为 4778 × 1850 × 1427 mm，因此与此前 V60 II 的 4761 × 1850 × 1437 mm 分组。([沃尔沃汽车][2])([沃尔沃汽车][2]) 进度

READY=100
PENDING=0
DIMENSION_GROUP=9
机械终检：表头、唯一性、Ktype 覆盖、引用闭合、正整数尺寸、来源、URL、孤立组检查全部通过。

## 最终完整 Ktype TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
59370	59370	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
111858	111858	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
112556	112556	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
55096	55096	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
107462	107462	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
116592	116592	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
55097	55097	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
57488	57488	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
58973	58973	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
106280	106280	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
147906	147906	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH	Input Kasten/Schrägheck resolved to Hatchback.	READY
147901	147901	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147919	147919	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147903	147903	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147920	147920	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147896	147896	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147922	147922	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147908	147908	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147900	147900	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147902	147902	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147904	147904	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147909	147909	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
112412	112412	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147917	147917	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147923	147923	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
147924	147924	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
59786	59786	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
108766	108766	Hatchback	II		5	EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	HIGH		READY
18603	18603	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
18113	18113	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
17820	17820	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
17821	17821	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
18604	18604	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
128504	128504	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
17906	17906	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
33822	33822	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
33806	33806	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
17824	17824	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
18112	18112	Wagon	I		5	EU-VOLVO-V50-I-WAGON-STANDARD-01	HIGH		READY
10248	10248	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
120524	120524	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
6047	6047	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
128085	128085	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
106318	106318	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113270	113270	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
57495	57495	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113271	113271	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
6051	6051	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
100369	100369	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113272	113272	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
57496	57496	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
100372	100372	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113273	113273	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
10275	10275	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
107466	107466	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113274	113274	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
10277	10277	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
107467	107467	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
116225	116225	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
55138	55138	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113276	113276	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
119086	119086	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113278	113278	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
113280	113280	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
114200	114200	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
12693	12693	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
100376	100376	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
100402	100402	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
128084	128084	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
107415	107415	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
116595	116595	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
100377	100377	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
107414	107414	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
117791	117791	Wagon	I		5	EU-VOLVO-V60-I-WAGON-STANDARD-01	MEDIUM		READY
147939	147939	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147942	147942	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147945	147945	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147947	147947	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147948	147948	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147949	147949	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147937	147937	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147938	147938	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
147950	147950	Wagon	I		5	EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	HIGH		READY
145168	145168	Wagon	II		5	EU-VOLVO-V60-II-WAGON-STANDARD-01	HIGH		READY
151838	151838	Wagon	II		5	EU-VOLVO-V60-II-WAGON-STANDARD-01	HIGH		READY
803454	803454	Wagon	II		5	EU-VOLVO-V60-II-WAGON-2026-PHEV-01	HIGH	2026 plug-in-hybrid exterior dimensions differ from earlier V60 II.	READY
146658	146658	Wagon	II		5	EU-VOLVO-V60-II-WAGON-STANDARD-01	HIGH		READY
151713	151713	Wagon	II		5	EU-VOLVO-V60-II-WAGON-STANDARD-01	HIGH		READY
145169	145169	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147098	147098	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147956	147956	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147951	147951	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147952	147952	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147955	147955	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147953	147953	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
147954	147954	Wagon	II		5	EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	HIGH		READY
18317	18317	Wagon	I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	MEDIUM		READY
11063	11063	Wagon	I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	MEDIUM		READY
14440	14440	Wagon	I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	MEDIUM		READY
11227	11227	Wagon	I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	MEDIUM		READY
```

[下载 left18448_16801-16900_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_16801-16900_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	4369	1802	1420	Volvo Support	https://www.volvocars.com/ie/support/car/v40/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V40-II-HATCHBACK-CROSS-COUNTRY-01	4370	1802	1458	Volvo Support	https://www.volvocars.com/en-om/support/car/v40-cross-country/15w46/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
EU-VOLVO-V50-I-WAGON-STANDARD-01	4514	1770	1452	Volvo Cars Media	https://www.volvocars.com/se/media/press-releases/25EB4C4816347F97/
EU-VOLVO-V60-I-WAGON-STANDARD-01	4628	1865	1484	CarsGuide	https://www.carsguide.com.au/volvo/v60/car-dimensions/2012
EU-VOLVO-V60-I-WAGON-CROSS-COUNTRY-01	4638	1865	1545	Volvo Support	https://www.volvocars.com/lb/support/car/v60-cross-country/2016/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-V60-II-WAGON-STANDARD-01	4761	1850	1437	Volvo Support	https://www.volvocars.com/en-kw/support/car/v60/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V60-II-WAGON-2026-PHEV-01	4778	1850	1427	Volvo Support	https://www.volvocars.com/uk/support/car/v60-plug-in-hybrid/article/47d2c97fd33effd3c0a8cc3718c999b7-cf578f17ce837790c0a8b04a1abf9aaa-8664b2fa77a7e089c0a8296870d1a409_47d2c97fd33effd3c0a8cc3718c999b7-350655bc554de2a7c0a8b097561c9a50-8664b2fa77a7e089c0a8296870d1a409_0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-V60-II-WAGON-CROSS-COUNTRY-01	4784	1893	1504	Volvo Support	https://www.volvocars.com/en-ca/support/car/v60-cross-country/21w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V70-I-WAGON-STANDARD-01	4730	1760	1430	Auto-Data	https://www.auto-data.net/en/volvo-v70-i-2.4-16v-bifuel-140hp-9265
```

[下载 left18448_16801-16900_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_16801-16900_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.volvocars.com/en-ca/support/car/v60-cross-country/21w46/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/ "V60 Cross Country Dimensions | Volvo Support EN-CA"
[2]: https://www.volvocars.com/uk/support/car/v60-plug-in-hybrid/article/47d2c97fd33effd3c0a8cc3718c999b7-cf578f17ce837790c0a8b04a1abf9aaa-8664b2fa77a7e089c0a8296870d1a409_47d2c97fd33effd3c0a8cc3718c999b7-350655bc554de2a7c0a8b097561c9a50-8664b2fa77a7e089c0a8296870d1a409_0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/ "https://www.volvocars.com/uk/support/car/v60-plug-in-hybrid/article/47d2c97fd33effd3c0a8cc3718c999b7-cf578f17ce837790c0a8b04a1abf9aaa-8664b2fa77a7e089c0a8296870d1a409_47d2c97fd33effd3c0a8cc3718c999b7-350655bc554de2a7c0a8b097561c9a50-8664b2fa77a7e089c0a8296870d1a409_0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/"


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3752 行）
- 累计尺寸组：dimension_groups_final.tsv（972 行）

