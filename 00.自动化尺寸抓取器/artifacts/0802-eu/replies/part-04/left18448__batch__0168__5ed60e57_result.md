# 任务：left18448 第 16701-16800 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0168__5ed60e57


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16701-16800 行

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
left18448 第 16701-16800 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16701-16800_ktype_dimension_mapping_final.tsv
- left18448_16701-16800_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Volvo	S60 ii	D4	Stufenheck	Frontantrieb	Diesel	Apr 2010	Dec 2014	57429
Volvo	S60 ii	D4	Stufenheck	Frontantrieb	Diesel	Sep 2013	Dec 2015	100528
Volvo	S60 ii	D4	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	113263
Volvo	S60 ii	D4 AWD	Stufenheck	Allrad	Diesel	Mar 2015	May 2018	113265
Volvo	S60 ii	D5	Stufenheck	Frontantrieb	Diesel	Apr 2011	Dec 2015	10289
Volvo	S60 ii	D5	Stufenheck	Frontantrieb	Diesel	Apr 2014	Dec 2015	107460
Volvo	S60 ii	D5	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	113266
Volvo	S60 ii	D5 AWD	Stufenheck	Allrad	Diesel	Apr 2011	Dec 2015	10290
Volvo	S60 ii	D5 AWD	Stufenheck	Allrad	Diesel	Apr 2014	Dec 2015	107461
Volvo	S60 ii	T2	Stufenheck	Frontantrieb	Benzin	Oct 2015	May 2018	119110
Volvo	S60 ii	T3	Stufenheck	Frontantrieb	Benzin	Mar 2015	May 2018	113267
Volvo	S60 ii	T3	Stufenheck	Frontantrieb	Benzin	Mar 2015	May 2018	113269
Volvo	S60 ii	T4	Stufenheck	Frontantrieb	Benzin	Mar 2015	May 2018	114198
Volvo	S60 ii	T4F	Stufenheck	Frontantrieb	Benzin/Ethanol	Apr 2011	Dec 2015	12572
Volvo	S60 ii	T5	Stufenheck	Frontantrieb	Benzin	Sep 2011	Dec 2015	51930
Volvo	S60 ii	T5	Stufenheck	Frontantrieb	Benzin	Sep 2013	Dec 2018	100522
Volvo	S60 ii	T5 AWD	Stufenheck	Allrad	Benzin	Jul 2014	Dec 2018	107411
Volvo	S60 ii	T5 AWD	Stufenheck	Allrad	Benzin	Aug 2015	Dec 2018	116593
Volvo	S60 ii	T6	Stufenheck	Frontantrieb	Benzin	Sep 2013	Dec 2018	100520
Volvo	S60 ii	T6 AWD	Stufenheck	Allrad	Benzin	Apr 2014	Dec 2015	57041
Volvo	S60 ii	T6 AWD	Stufenheck	Allrad	Benzin	Sep 2015	Dec 2018	118986
Volvo	S60 ii cross country	D3	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	147927
Volvo	S60 ii cross country	D4	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	147929
Volvo	S60 ii cross country	D4 AWD	Stufenheck	Allrad	Diesel	Mar 2015	May 2018	147930
Volvo	S60 ii cross country	D4 Drive-e Polestar	Stufenheck	Frontantrieb	Diesel	Mar 2015	May 2018	147933
Volvo	S60 ii cross country	T5 AWD	Stufenheck	Allrad	Benzin	Jun 2016	Dec 2018	147926
Volvo	S60 ii cross country	T5 AWD	Stufenheck	Allrad	Benzin	Mar 2015	Dec 2018	147931
Volvo	S60 iii	B3 Mhev	Stufenheck	Frontantrieb	Benzin/Elektro	Mar 2020	Dec 2023	143402
Volvo	S60 iii	B5 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Mar 2022	-	147100
Volvo	S60 iii	B6 Mild-hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Apr 2021	Dec 2022	145093
Volvo	S60 iii	T6 Polestar AWD	Stufenheck	Allrad	Benzin	May 2019	Dec 2021	147403
Volvo	S60 iii	T6 Twin Engine AWD	Stufenheck	Allrad	Benzin/Elektro	Jan 2022	-	151837
Volvo	S60 iii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	May 2019	Dec 2022	143303
Volvo	S60 iii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Jan 2022	-	146655
Volvo	S60 iii	T8 Recharge AWD	Stufenheck	Allrad	Benzin/Elektro	Jan 2023	-	151722
Volvo	S60 iii	T8 Twin Engine Polestar	Stufenheck	Allrad	Benzin/Elektro	Jan 2021	-	152745
Volvo	S70	2	Stufenheck	Frontantrieb	Benzin	Jan 1997	Nov 2000	18331
Volvo	S70	2.4	Stufenheck	Frontantrieb	Benzin	Jun 1998	Nov 2000	11064
Volvo	S70	2.4	Stufenheck	Frontantrieb	Benzin	Aug 1999	Nov 2000	14441
Volvo	S70	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	Oct 1998	Nov 2000	10420
Volvo	S70	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	Jul 1999	Nov 2000	15570
Volvo	S80 i	2	Stufenheck	Frontantrieb	Benzin	Jun 1998	Jul 2006	10172
Volvo	S80 i	2.4	Stufenheck	Frontantrieb	Benzin	Jan 1999	Jul 2006	11066
Volvo	S80 i	2.9	Stufenheck	Frontantrieb	Benzin	Mar 1999	Jul 2006	13087
Volvo	S80 i	3	Stufenheck	Frontantrieb	Benzin	Jun 2001	Jul 2006	16474
Volvo	S80 i	2.0 T	Stufenheck	Frontantrieb	Benzin	Dec 1999	Jul 2006	16078
Volvo	S80 i	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Erdgas (CNG)	Sep 2001	Jul 2006	16081
Volvo	S80 i	2.4 Bifuel	Stufenheck	Frontantrieb	Benzin/Autogas (LPG)	Sep 2001	Jul 2006	100288
Volvo	S80 i	2.4 D	Stufenheck	Frontantrieb	Diesel	Oct 2001	Jul 2006	16476
Volvo	S80 i	2.4 T	Stufenheck	Frontantrieb	Benzin	Jun 2000	Jul 2006	16079
Volvo	S80 i	2.5 T	Stufenheck	Frontantrieb	Benzin	Mar 2003	Jul 2006	18602
Volvo	S80 i	2.5 T AWD	Stufenheck	Allrad	Benzin	Jul 2003	Jul 2006	17283
Volvo	S80 i	D5	Stufenheck	Frontantrieb	Diesel	Aug 2001	Jul 2006	16080
Volvo	S80 i	T6	Stufenheck	Frontantrieb	Benzin	Jun 2001	Jul 2006	16475
Volvo	S80 ii	2	Stufenheck	Frontantrieb	Benzin	Jan 2008	Sep 2012	33802
Volvo	S80 ii	1.6 Drive	Stufenheck	Frontantrieb	Diesel	Jun 2011	Jan 2014	10249
Volvo	S80 ii	2.0 Drive- E	Stufenheck	Frontantrieb	Benzin	Dec 2014	Dec 2016	109981
Volvo	S80 ii	2.0 T	Stufenheck	Frontantrieb	Benzin	Jan 2010	May 2011	33801
Volvo	S80 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	Jan 2010	Dec 2012	33800
Volvo	S80 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	Sep 2012	Dec 2016	109982
Volvo	S80 ii	2.5 T	Stufenheck	Frontantrieb	Benzin	Jan 2012	Apr 2016	109983
Volvo	S80 ii	D4	Stufenheck	Frontantrieb	Diesel	Sep 2013	Dec 2016	100518
Volvo	S80 ii	D5	Stufenheck	Frontantrieb	Diesel	Jun 2011	Apr 2015	10282
Volvo	S80 ii	D5 AWD	Stufenheck	Allrad	Diesel	Jun 2011	Apr 2015	10278
Volvo	S80 ii	T4F	Stufenheck	Frontantrieb	Benzin/Ethanol	May 2011	Jan 2014	12575
Volvo	S80 ii	T5	Stufenheck	Frontantrieb	Benzin	Sep 2013	May 2014	100519
Volvo	S80 ii	T5	Stufenheck	Frontantrieb	Benzin	Jan 2014	Dec 2016	120516
Volvo	S90 ii	B5 Mild Hybrid AWD	Stufenheck	Allrad	Diesel/Elektro	Dec 2020	-	145094
Volvo	S90 ii	B5 Mild Hybrid AWD	Stufenheck	Allrad	Diesel/Elektro	Mar 2023	-	154662
Volvo	S90 ii	B5 Mild-hybrid	Stufenheck	Frontantrieb	Benzin/Elektro	Mar 2022	-	147097
Volvo	S90 ii	D3	Stufenheck	Frontantrieb	Diesel	Mar 2016	Dec 2021	124007
Volvo	S90 ii	D4	Stufenheck	Frontantrieb	Diesel	Mar 2016	Dec 2021	119951
Volvo	S90 ii	D4 AWD	Stufenheck	Allrad	Diesel	Mar 2016	Dec 2021	124006
Volvo	S90 ii	D5 AWD	Stufenheck	Allrad	Diesel	Mar 2016	Dec 2021	119950
Volvo	S90 ii	T5	Stufenheck	Frontantrieb	Benzin	Mar 2016	Dec 2021	120506
Volvo	S90 ii	T6 AWD	Stufenheck	Allrad	Benzin	Mar 2016	Dec 2021	119949
Volvo	S90 ii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Oct 2017	Dec 2022	143304
Volvo	S90 ii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Jan 2022	-	146664
Volvo	S90 ii	T8 Plug-in Hybrid AWD	Stufenheck	Allrad	Benzin/Elektro	Apr 2022	-	152925
Volvo	V40	1.6	Kombi	Frontantrieb	Benzin	Mar 1999	Jun 2004	12520
Volvo	V40	1.8	Kombi	Frontantrieb	Benzin	Mar 1999	Jun 2004	12528
Volvo	V40	1.8 I	Kombi	Frontantrieb	Benzin	Mar 1998	Jun 2004	12361
Volvo	V40	1.8 I	Kombi	Frontantrieb	Benzin	Jun 2001	Jun 2004	16473
Volvo	V40	1.8 LPG	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Mar 1999	Jun 2004	128503
Volvo	V40	1.9 DI	Kombi	Frontantrieb	Diesel	Mar 1999	Jul 2000	11404
Volvo	V40	1.9 DI	Kombi	Frontantrieb	Diesel	Jul 2000	Jun 2004	14960
Volvo	V40	1.9 DI	Kombi	Frontantrieb	Diesel	Jul 2000	Jun 2004	14961
Volvo	V40	1.9 TD	Kombi	Frontantrieb	Diesel	Jul 1995	Aug 1999	5708
Volvo	V40	2.0 T	Kombi	Frontantrieb	Benzin	Oct 1997	Jul 2000	11119
Volvo	V40	2.0 T	Kombi	Frontantrieb	Benzin	Jul 1999	Jun 2004	14963
Volvo	V40	2.0 T	Kombi	Frontantrieb	Benzin	Jun 2001	Jun 2004	16569
Volvo	V40	2.0 T4	Kombi	Frontantrieb	Benzin	Jul 2000	Jun 2004	14962
Volvo	V40	D2	Schrägheck	Frontantrieb	Diesel	Mar 2012	Dec 2016	55098
Volvo	V40	D2	Schrägheck	Frontantrieb	Diesel	Feb 2015	Aug 2019	111861
Volvo	V40	D3	Schrägheck	Frontantrieb	Diesel	Mar 2012	Mar 2015	55100
Volvo	V40	D3	Schrägheck	Frontantrieb	Diesel	Apr 2015	Aug 2019	116224
Volvo	V40	D4	Schrägheck	Frontantrieb	Diesel	Mar 2012	Dec 2014	55102
Volvo	V40	D4	Schrägheck	Frontantrieb	Diesel	May 2014	Aug 2019	106279
Volvo	V40	T2	Schrägheck	Frontantrieb	Benzin	Feb 2015	Aug 2019	111857
Volvo	V40	T2	Schrägheck	Frontantrieb	Benzin	Feb 2015	Aug 2019	111884


--- Round 1 / 首次发送 ---
## 更新点

本批复用 2 个既有 S60 II 尺寸组，新建 13 个尺寸组。S60 III、S80 I/II、S90 II、V40 I 仅对跨越已确认三维变化边界的 Ktype 拆分；动力、能源和驱动差异均直接复用。相关三维由 Volvo 官方支持页和 Auto-Data 等直接规格页支撑。([汽车数据网][1])

## 进度

* 输入 Ktype：100
* 完整映射行：139
* DIMENSION_GROUP：15
* READY：139
* PENDING：0
* 映射引用闭合：通过
* `id`、`DIMENSION_GROUP_ID` 唯一性：通过
* 三维正整数、来源与直接 URL 非空：通过
* 孤立尺寸组：0

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
57429_prefl	57429	Sedan	S60 II pre-facelift		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
57429_facelift	57429	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
100528	100528	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113263	113263	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113265	113265	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
10289_prefl	10289	Sedan	S60 II pre-facelift		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10289_facelift	10289	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
107460	107460	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113266	113266	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
10290_prefl	10290	Sedan	S60 II pre-facelift		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10290_facelift	10290	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
107461	107461	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
119110	119110	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113267	113267	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
113269	113269	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
114198	114198	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
12572_prefl	12572	Sedan	S60 II pre-facelift		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
12572_facelift	12572	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
51930_prefl	51930	Sedan	S60 II pre-facelift		4	EU-VOLVO-S60-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
51930_facelift	51930	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
100522	100522	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
107411	107411	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
116593	116593	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
100520	100520	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
57041	57041	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
118986	118986	Sedan	S60 II facelift		4	EU-VOLVO-S60-II-SEDAN-FACELIFT-01	HIGH		READY
147927	147927	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
147929	147929	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
147930	147930	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
147933	147933	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
147926	147926	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
147931	147931	Sedan	S60 II Cross Country		4	EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	HIGH		READY
143402_prefl	143402	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
143402_facelift	143402	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
147100_prefl	147100	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
147100_facelift	147100	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
145093	145093	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH		READY
147403	147403	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH		READY
151837_prefl	151837	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
151837_facelift	151837	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
143303	143303	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH		READY
146655_prefl	146655	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
146655_facelift	146655	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
151722	151722	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH		READY
152745_prefl	152745	Sedan	S60 III pre-facelift		4	EU-VOLVO-S60-III-SEDAN-PREFL-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
152745_facelift	152745	Sedan	S60 III facelift		4	EU-VOLVO-S60-III-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2023 dimensional update; split by physical exterior.	READY
18331	18331	Sedan	S70		4	EU-VOLVO-S70-I-SEDAN-STANDARD-01	HIGH		READY
11064	11064	Sedan	S70		4	EU-VOLVO-S70-I-SEDAN-STANDARD-01	HIGH		READY
14441	14441	Sedan	S70		4	EU-VOLVO-S70-I-SEDAN-STANDARD-01	HIGH		READY
10420	10420	Sedan	S70		4	EU-VOLVO-S70-I-SEDAN-STANDARD-01	HIGH		READY
15570	15570	Sedan	S70		4	EU-VOLVO-S70-I-SEDAN-STANDARD-01	HIGH		READY
10172_prefl	10172	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
10172_facelift	10172	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
11066_prefl	11066	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
11066_facelift	11066	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
13087_prefl	13087	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
13087_facelift	13087	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16474_prefl	16474	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16474_facelift	16474	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16078_prefl	16078	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16078_facelift	16078	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16081_prefl	16081	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16081_facelift	16081	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
100288_prefl	100288	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
100288_facelift	100288	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16476_prefl	16476	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16476_facelift	16476	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16079_prefl	16079	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16079_facelift	16079	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
18602	18602	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH		READY
17283	17283	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH		READY
16080_prefl	16080	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16080_facelift	16080	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16475_prefl	16475	Sedan	S80 I pre-facelift		4	EU-VOLVO-S80-I-SEDAN-PREFL-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
16475_facelift	16475	Sedan	S80 I facelift		4	EU-VOLVO-S80-I-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2003 dimensional update; split by physical exterior.	READY
33802	33802	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH		READY
10249_prefl	10249	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10249_facelift	10249	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
109981	109981	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH		READY
33801	33801	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH		READY
33800	33800	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH		READY
109982_prefl	109982	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
109982_facelift	109982	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
109983_prefl	109983	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
109983_facelift	109983	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
100518	100518	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH		READY
10282_prefl	10282	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10282_facelift	10282	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10278_prefl	10278	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
10278_facelift	10278	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
12575_prefl	12575	Sedan	S80 II pre-2013		4	EU-VOLVO-S80-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
12575_facelift	12575	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2013 dimensional update; split by physical exterior.	READY
100519	100519	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH		READY
120516	120516	Sedan	S80 II facelift 2013		4	EU-VOLVO-S80-II-SEDAN-FACELIFT-01	HIGH		READY
145094	145094	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH		READY
154662	154662	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH		READY
147097	147097	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH		READY
124007_prefl	124007	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
124007_facelift	124007	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119951_prefl	119951	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119951_facelift	119951	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
124006_prefl	124006	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
124006_facelift	124006	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119950_prefl	119950	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119950_facelift	119950	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
120506_prefl	120506	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
120506_facelift	120506	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119949_prefl	119949	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
119949_facelift	119949	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
143304_prefl	143304	Sedan	S90 II pre-facelift		4	EU-VOLVO-S90-II-SEDAN-PREFL-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
143304_facelift	143304	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH	Ktype spans the 2021 dimensional update; split by physical exterior.	READY
146664	146664	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH		READY
152925	152925	Sedan	S90 II facelift		4	EU-VOLVO-S90-II-SEDAN-FACELIFT-01	HIGH		READY
12520_prefl	12520	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
12520_facelift	12520	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
12528_prefl	12528	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
12528_facelift	12528	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
12361_prefl	12361	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
12361_facelift	12361	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
16473	16473	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH		READY
128503_prefl	128503	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
128503_facelift	128503	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
11404	11404	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH		READY
14960	14960	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH		READY
14961	14961	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH		READY
5708	5708	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH		READY
11119	11119	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH		READY
14963_prefl	14963	Wagon	V40 I pre-facelift		5	EU-VOLVO-V40-I-WAGON-PREFL-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
14963_facelift	14963	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH	Ktype spans the 2000 dimensional update; split by physical exterior.	READY
16569	16569	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH		READY
14962	14962	Wagon	V40 I facelift		5	EU-VOLVO-V40-I-WAGON-FACELIFT-01	HIGH		READY
55098	55098	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
111861	111861	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
55100	55100	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
116224	116224	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
55102	55102	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
106279	106279	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
111857	111857	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
111884	111884	Hatchback	V40 II		5	EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	HIGH		READY
```

[下载完整 Ktype 映射 TSV](sandbox:/mnt/data/left18448_16701-16800_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-S60-II-SEDAN-PREFL-01	4628	1865	1484	Auto-Data	https://www.auto-data.net/en/volvo-s60-ii-generation-3841
EU-VOLVO-S60-II-SEDAN-FACELIFT-01	4635	1865	1484	Auto-Data	https://www.auto-data.net/en/volvo-s60-ii-facelift-2013-generation-4062
EU-VOLVO-S60-II-CROSS-COUNTRY-SEDAN-STANDARD-01	4638	1866	1539	Auto-Data	https://www.auto-data.net/en/volvo-s60-ii-cross-country-generation-4520
EU-VOLVO-S60-III-SEDAN-PREFL-01	4761	1850	1431	Auto-Data	https://www.auto-data.net/en/volvo-s60-iii-2.0-b6-299hp-mild-hybrid-awd-automatic-40912
EU-VOLVO-S60-III-SEDAN-FACELIFT-01	4778	1850	1431	Volvo Cars Support	https://www.volvocars.com/uk/support/car/s60/2023/article/47d2c97fd33effd3c0a8cc3718c999b7-cf578f17ce837790c0a8b04a1abf9aaa-8664b2fa77a7e089c0a8296870d1a409/47d2c97fd33effd3c0a8cc3718c999b7-350655bc554de2a7c0a8b097561c9a50-8664b2fa77a7e089c0a8296870d1a409/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
EU-VOLVO-S70-I-SEDAN-STANDARD-01	4720	1760	1400	Auto-Data	https://www.auto-data.net/en/volvo-s70-model-922
EU-VOLVO-S80-I-SEDAN-PREFL-01	4822	1832	1450	Auto-Data	https://www.auto-data.net/en/volvo-s80-generation-1948
EU-VOLVO-S80-I-SEDAN-FACELIFT-01	4849	1832	1452	Auto-Data	https://www.auto-data.net/en/volvo-s80-facelift-2003-generation-1949
EU-VOLVO-S80-II-SEDAN-PREFL-01	4851	1861	1493	Auto-Data	https://www.auto-data.net/en/volvo-s80-ii-generation-1947
EU-VOLVO-S80-II-SEDAN-FACELIFT-01	4854	1861	1493	Volvo Cars Support	https://www.volvocars.com/sg/support/car/s80/article/18f77489f78f457dc0a801e800a04016/
EU-VOLVO-S90-II-SEDAN-PREFL-01	4963	1879	1443	Volvo Cars Support	https://www.volvocars.com/uk/support/car/s90/18w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/0a9f81ad7fe71c97c0a8015176e5bb71/
EU-VOLVO-S90-II-SEDAN-FACELIFT-01	4969	1890	1446	Volvo Cars Support	https://www.volvocars.com/uk/support/car/s90/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V40-I-WAGON-PREFL-01	4480	1720	1410	Autoevolution	https://www.autoevolution.com/cars/volvo-v40-1996.html
EU-VOLVO-V40-I-WAGON-FACELIFT-01	4516	1716	1425	Auto-Data	https://www.auto-data.net/en/volvo-v40-combi-vw-2.0-16v-136hp-9520
EU-VOLVO-V40-II-HATCHBACK-STANDARD-01	4369	1802	1420	Volvo Cars Support	https://www.volvocars.com/ie/support/car/v40/2015/article/d24bb7d1e21ec6e4c0a801e801cf6114/1fb4a1e231ff3432c0a801e8011f8ab3/d3e3a984c472afb4c0a801e8016918f7/
```

[下载完整 DIMENSION_GROUP TSV](sandbox:/mnt/data/left18448_16701-16800_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volvo-s60-ii-cross-country-generation-4520?utm_source=chatgpt.com "Volvo S60 II Cross Country | Technical Specs, Fuel ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3652 行）
- 累计尺寸组：dimension_groups_final.tsv（964 行）

