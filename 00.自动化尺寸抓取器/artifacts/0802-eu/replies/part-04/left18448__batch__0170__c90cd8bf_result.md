# 任务：left18448 第 16901-17000 行
# 来源文件：left18448.tsv
# 任务 ID：left18448__batch__0170__c90cd8bf


--- 发送 / 首次任务 ---
【任务名称】
【全量表更新】left18448 第 16901-17000 行

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
left18448 第 16901-17000 行

【COMPLETE 下载文件硬性要求】
准备 COMPLETE 时，除两张完整内嵌 TSV 外，还必须创建并提供以下两个可点击 sandbox 下载链接，文件名必须完全一致：
- left18448_16901-17000_ktype_dimension_mapping_final.tsv
- left18448_16901-17000_dimension_groups_final.tsv
缺少任一下载链接时不得输出推进信号：COMPLETE。

【跨批次已有尺寸组索引】
以下 ID 已经存在于累计表。三维和物理外廓完全相同时才可复用；如果当前证据得到不同三维，禁止改写已有组，必须使用同系列下一个可用序号创建新 DIMENSION_GROUP_ID，并把当前批次相关 Ktype 全部指向新组。

DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM
EU-VOLVO-V70-I-WAGON-STANDARD-01	4730	1760	1430

【TSV 数据】
Make	Model	VariantName	BodyStyle	DriveType	Energy	Product Start Month-Year	Product End Month-Year	Ktype
Volvo	V70 i	2.3 T-5 AWD	Kombi	Allrad	Benzin	Jan 1997	Dec 2000	10173
Volvo	V70 i	2.4 Bifuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	May 1998	Dec 1999	10419
Volvo	V70 i	2.4 Bifuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	Aug 1999	Dec 2000	12530
Volvo	V70 i	2.4 Turbo AWD	Kombi	Allrad	Benzin	Mar 1999	Dec 2000	14607
Volvo	V70 ii	2.4	Kombi	Frontantrieb	Benzin	Mar 2000	Aug 2007	14810
Volvo	V70 ii	2.4	Kombi	Frontantrieb	Benzin	Mar 2000	Aug 2007	14811
Volvo	V70 ii	2.0 T	Kombi	Frontantrieb	Benzin	Nov 1999	Aug 2007	16493
Volvo	V70 ii	2.4 Bifuel	Kombi	Frontantrieb	Benzin/Erdgas (CNG)	Sep 2001	Aug 2007	16083
Volvo	V70 ii	2.4 Bifuel	Kombi	Frontantrieb	Benzin/Autogas (LPG)	Sep 2001	Aug 2007	100286
Volvo	V70 ii	2.4 D	Kombi	Frontantrieb	Diesel	Jul 2001	Aug 2007	16599
Volvo	V70 ii	2.4 T	Kombi	Frontantrieb	Benzin	Nov 1999	Aug 2003	14618
Volvo	V70 ii	2.4 T AWD	Kombi	Allrad	Benzin	Sep 2001	Aug 2002	16495
Volvo	V70 ii	2.5 T	Kombi	Frontantrieb	Benzin	Jul 2001	Aug 2007	18221
Volvo	V70 ii	2.5 T AWD	Kombi	Allrad	Benzin	Jul 2002	Aug 2007	17139
Volvo	V70 ii	2.5 TDI	Kombi	Frontantrieb	Diesel	Nov 1999	Aug 2007	14619
Volvo	V70 ii	D5	Kombi	Frontantrieb	Diesel	Jan 2001	Dec 2008	16082
Volvo	V70 ii	D5 AWD	Kombi	Allrad	Diesel	Jul 2002	Aug 2007	17521
Volvo	V70 ii	R 2,5 T AWD	Kombi	Allrad	Benzin	Mar 2003	Aug 2007	16925
Volvo	V70 ii	T5	Kombi	Frontantrieb	Benzin	Nov 1999	Dec 2004	14617
Volvo	V70 ii	T5	Kombi	Frontantrieb	Benzin	Apr 2004	Aug 2007	18222
Volvo	V70 iii	3.2	Kombi	Frontantrieb	Benzin	Apr 2010	Dec 2014	12347
Volvo	V70 iii	1.6 Drive / D2	Kombi	Frontantrieb	Diesel	Apr 2011	Dec 2015	10250
Volvo	V70 iii	2.0 GDI	Kombi	Frontantrieb	Benzin	Apr 2012	Dec 2015	117368
Volvo	V70 iii	2.0 T	Kombi	Frontantrieb	Benzin	Sep 2009	Dec 2011	33816
Volvo	V70 iii	2.5 T	Kombi	Frontantrieb	Benzin	Apr 2009	Dec 2012	33815
Volvo	V70 iii	3.2 AWD	Kombi	Allrad	Benzin	Apr 2010	Dec 2015	12731
Volvo	V70 iii	D2	Kombi	Frontantrieb	Diesel	Mar 2015	Apr 2016	113281
Volvo	V70 iii	D3	Kombi	Frontantrieb	Diesel	Oct 2007	Dec 2015	59385
Volvo	V70 iii	D3	Kombi	Frontantrieb	Diesel	Mar 2015	Apr 2016	113283
Volvo	V70 iii	D3 / D4	Kombi	Frontantrieb	Diesel	Mar 2010	Dec 2015	10064
Volvo	V70 iii	D4	Kombi	Frontantrieb	Diesel	Oct 2013	Apr 2016	100378
Volvo	V70 iii	D4 AWD	Kombi	Allrad	Diesel	Oct 2007	Dec 2015	59028
Volvo	V70 iii	D4 AWD	Kombi	Allrad	Diesel	Oct 2013	Apr 2016	100379
Volvo	V70 iii	D5	Kombi	Frontantrieb	Diesel	Apr 2011	Dec 2015	10274
Volvo	V70 iii	D5 AWD	Kombi	Allrad	Diesel	Apr 2011	Dec 2015	10294
Volvo	V70 iii	T4	Kombi	Frontantrieb	Benzin	Mar 2015	Apr 2016	113284
Volvo	V70 iii	T4F	Kombi	Frontantrieb	Benzin/Ethanol	Jan 2011	Dec 2015	12730
Volvo	V70 iii	T5	Kombi	Frontantrieb	Benzin	Oct 2013	Apr 2016	100380
Volvo	V70 iii	T6 AWD	Kombi	Allrad	Benzin	Jan 2010	Dec 2015	14645
Volvo	V90 ii	B4 Mild-hybrid	Kombi	Frontantrieb	Diesel/Elektro	Oct 2020	-	143433
Volvo	V90 ii	B4 Mild-hybrid AWD	Kombi	Allrad	Diesel/Elektro	Oct 2020	-	146124
Volvo	V90 ii	B5 Mild Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Dec 2020	-	143552
Volvo	V90 ii	B5 Mild Hybrid Polestar AWD	Kombi	Allrad	Diesel/Elektro	Nov 2021	-	148103
Volvo	V90 ii	D3	Kombi	Frontantrieb	Diesel	Mar 2016	Dec 2021	123999
Volvo	V90 ii	D3 AWD	Kombi	Allrad	Diesel	Mar 2016	Dec 2021	124000
Volvo	V90 ii	D4	Kombi	Frontantrieb	Diesel	Mar 2016	Dec 2021	119946
Volvo	V90 ii	D4 AWD	Kombi	Allrad	Diesel	Mar 2016	Dec 2021	124001
Volvo	V90 ii	D5 AWD	Kombi	Allrad	Diesel	Mar 2016	Dec 2021	119947
Volvo	V90 ii	T5	Kombi	Frontantrieb	Benzin	Mar 2016	Dec 2018	119944
Volvo	V90 ii	T6 AWD	Kombi	Allrad	Benzin	Mar 2016	Dec 2018	119945
Volvo	V90 ii	T6 Plug-in-hybrid AWD	Kombi	Allrad	Benzin/Elektro	Jan 2022	-	151836
Volvo	V90 ii	T8 Plug-in Hybrid AWD	Kombi	Allrad	Benzin/Elektro	May 2022	-	146645
Volvo	V90 ii	T8 Plug-in-hybrid AWD	Kombi	Allrad	Benzin/Elektro	Mar 2016	Dec 2018	119948
Volvo	V90 ii	T8 Recharge AWD	Kombi	Allrad	Benzin/Elektro	Jan 2023	-	151725
Volvo	V90 ii cross country	B4 Mild-hybrid AWD	Kombi	Allrad	Diesel/Elektro	Oct 2020	-	147971
Volvo	V90 ii cross country	B5 Mild Hybrid AWD	Kombi	Allrad	Diesel/Elektro	Dec 2020	-	147970
Volvo	V90 ii cross country	B5 Mild Hybrid Polestar AWD	Kombi	Allrad	Diesel/Elektro	Nov 2021	-	148104
Volvo	V90 ii cross country	B5 Mild-hybrid	Kombi	Allrad	Benzin/Elektro	Mar 2022	-	147096
Volvo	V90 ii cross country	B6 Mild-hybrid AWD	Kombi	Allrad	Benzin/Elektro	Mar 2020	-	147969
Volvo	V90 ii cross country	D4 AWD	Kombi	Allrad	Diesel	Oct 2016	-	147963
Volvo	V90 ii cross country	D5 AWD	Kombi	Allrad	Diesel	Oct 2016	-	147962
Volvo	V90 ii cross country	D5 Polestar AWD	Kombi	Allrad	Diesel	Oct 2016	-	147966
Volvo	V90 ii cross country	Polestar AWD	Kombi	Allrad	Diesel	Oct 2016	-	147965
Volvo	V90 ii cross country	T5 AWD	Kombi	Allrad	Benzin	Oct 2016	Dec 2018	124002
Volvo	V90 ii cross country	T5 Drive-e Polestar AWD	Kombi	Allrad	Benzin	Oct 2016	Dec 2018	148002
Volvo	V90 ii cross country	T6 AWD	Kombi	Allrad	Benzin	Oct 2016	-	147961
Volvo	V90 ii cross country	T6 AWD	Kombi	Allrad	Benzin	Oct 2017	-	147967
Volvo	V90 ii cross country	T6 Polestar AWD	Kombi	Allrad	Benzin	Oct 2017	-	147968
Volvo	Xc40	B3 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Jan 2022	-	146666
Volvo	Xc40	B3 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Aug 2025	-	802149
Volvo	Xc40	B5 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	Mar 2022	Dec 2023	147099
Volvo	Xc40	D3 Polestar	SUV	Frontantrieb	Diesel	Dec 2019	Dec 2021	149991
Volvo	Xc40	D3 Polestar AWD	SUV	Allrad	Diesel	Dec 2019	Dec 2021	149992
Volvo	Xc40	Recharge	SUV	Frontantrieb	Elektro	Feb 2022	Dec 2022	146656
Volvo	Xc40	Recharge	SUV	Heckantrieb	Elektro	Jan 2023	-	152029
Volvo	Xc40	Recharge	SUV	Heckantrieb	Elektro	Jan 2023	-	152030
Volvo	Xc40	Recharge AWD	SUV	Allrad	Elektro	Nov 2020	-	144518
Volvo	Xc40	T3	SUV	Frontantrieb	Benzin	Dec 2020	Dec 2022	143452
Volvo	Xc40	T5 Plug-in Hybrid Polestar Performance	SUV	Frontantrieb	Benzin/Elektro	Jun 2019	-	145510
Volvo	Xc60 i	D3	SUV	Frontantrieb	Diesel	Apr 2012	Dec 2015	58950
Volvo	Xc60 i	D3	SUV	Frontantrieb	Diesel	Mar 2015	Apr 2017	113285
Volvo	Xc60 i	D4	SUV	Frontantrieb	Diesel	Oct 2013	Dec 2015	100381
Volvo	Xc60 i	D4	SUV	Frontantrieb	Diesel	Mar 2015	Feb 2017	113286
Volvo	Xc60 i	D4 AWD	SUV	Allrad	Diesel	Oct 2013	Dec 2015	100284
Volvo	Xc60 i	D4 AWD	SUV	Allrad	Diesel	Mar 2015	Feb 2017	113289
Volvo	Xc60 i	D5	SUV	Frontantrieb	Diesel	Jun 2011	Feb 2017	12732
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	Apr 2011	Dec 2015	10292
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	Apr 2014	Dec 2015	107469
Volvo	Xc60 i	D5 AWD	SUV	Allrad	Diesel	Mar 2015	Feb 2017	113291
Volvo	Xc60 i	T5	SUV	Frontantrieb	Benzin	Oct 2013	Feb 2017	100383
Volvo	Xc60 i	T5 AWD	SUV	Allrad	Benzin	Apr 2014	Feb 2017	108270
Volvo	Xc60 i	T6	SUV	Frontantrieb	Benzin	Oct 2013	Feb 2017	100384
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	Apr 2014	Dec 2015	107468
Volvo	Xc60 i	T6 AWD	SUV	Allrad	Benzin	Oct 2013	Dec 2017	117792
Volvo	Xc60 i van	D3	Kasten/SUV	Frontantrieb	Diesel	Sep 2013	Dec 2015	142996
Volvo	Xc60 i van	D4	Kasten/SUV	Frontantrieb	Diesel	Sep 2013	Feb 2017	142997
Volvo	Xc60 i van	D4 AWD	Kasten/SUV	Allrad	Diesel	Sep 2013	Feb 2017	142998
Volvo	Xc60 i van	D5 AWD	Kasten/SUV	Allrad	Diesel	Sep 2013	Feb 2017	142999
Volvo	Xc60 ii	2.0 B5 Mild-hybrid	SUV	Frontantrieb	Benzin/Elektro	Mar 2022	-	147101
Volvo	Xc60 ii	2.0 B5 Mild-hybrid AWD	SUV	Allrad	Benzin/Elektro	Mar 2022	-	147102


--- Round 1 / 首次发送 ---
## 更新点

本批 100 个 Ktype 已全部闭合，共复用或建立 13 个独立物理尺寸组：

* 复用既有 `EU-VOLVO-V70-I-WAGON-STANDARD-01`。
* V70 II 按统一外廓合并；V70 III 按有明确三维差异的改款前后分组。([汽车数据网][1])
* V90 II、V90 II Cross Country 按改款前后实际三维分组；宽度采用不含后视镜的车身宽度。([沃尔沃汽车][2])
* XC40、XC60 I 按明确改变外廓的改款节点分组；XC60 II 当前输入统一关联 2022 年后外廓。([汽车数据网][3])
* 跨越改款日期但没有 Ktype 多外廓直接证据的记录保留单行，不进行猜测性拆分。
* 4 个 XC60 I Van Ktype 属商用车认证形式，但物理外廓与 XC60 I facelift SUV 相同，复用同一尺寸组。

## 进度

`READY=100`　`PENDING=0`　`DIMENSION_GROUP=13`　`孤立尺寸组=0`　`未闭合引用=0`

## 最终完整 Ktype 映射 TSV

```tsv
id	Ktype	NormalizedBodyStyle	Generation	BodyCode	Doors	DIMENSION_GROUP_ID	MatchConfidence	Notes	IterationStatus
10173	10173	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	HIGH		READY
10419	10419	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	HIGH		READY
12530	12530	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	HIGH		READY
14607	14607	Wagon	V70 I		5	EU-VOLVO-V70-I-WAGON-STANDARD-01	HIGH		READY
14810	14810	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
14811	14811	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16493	16493	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16083	16083	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
100286	100286	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16599	16599	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
14618	14618	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16495	16495	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
18221	18221	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
17139	17139	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
14619	14619	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16082	16082	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
17521	17521	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
16925	16925	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
14617	14617	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
18222	18222	Wagon	V70 II		5	EU-VOLVO-V70-II-WAGON-STANDARD-01	HIGH		READY
12347	12347	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
10250	10250	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
117368	117368	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
33816	33816	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH		READY
33815	33815	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	HIGH		READY
12731	12731	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
113281	113281	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
59385	59385	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
113283	113283	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
10064	10064	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
100378	100378	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
59028	59028	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
100379	100379	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
10274	10274	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
10294	10294	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
113284	113284	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
12730	12730	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
100380	100380	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-FACELIFT-01	HIGH		READY
14645	14645	Wagon	V70 III		5	EU-VOLVO-V70-III-WAGON-PREFL-01	MEDIUM	Production span crosses 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
143433	143433	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
146124	146124	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
143552	143552	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
148103	148103	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
123999	123999	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	MEDIUM	Production span crosses 2020 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
124000	124000	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	MEDIUM	Production span crosses 2020 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
119946	119946	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	MEDIUM	Production span crosses 2020 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
124001	124001	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	MEDIUM	Production span crosses 2020 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
119947	119947	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	MEDIUM	Production span crosses 2020 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
119944	119944	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	HIGH		READY
119945	119945	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	HIGH		READY
151836	151836	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
146645	146645	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
119948	119948	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-PREFL-01	HIGH		READY
151725	151725	Wagon	V90 II		5	EU-VOLVO-V90-II-WAGON-FACELIFT-01	HIGH		READY
147971	147971	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	HIGH		READY
147970	147970	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	HIGH		READY
148104	148104	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	HIGH		READY
147096	147096	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	HIGH		READY
147969	147969	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	HIGH		READY
147963	147963	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
147962	147962	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
147966	147966	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
147965	147965	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
124002	124002	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	HIGH		READY
148002	148002	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	HIGH		READY
147961	147961	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
147967	147967	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
147968	147968	Wagon	V90 II Cross Country		5	EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	MEDIUM	Open production span crosses 2020 facelift; retained one launch-phase Cross Country exterior because no Ktype-specific multi-body evidence was found.	READY
146666	146666	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-FACELIFT-01	HIGH		READY
802149	802149	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-FACELIFT-01	HIGH		READY
147099	147099	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-FACELIFT-01	HIGH		READY
149991	149991	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	HIGH		READY
149992	149992	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	HIGH		READY
146656	146656	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	HIGH		READY
152029	152029	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-FACELIFT-01	HIGH		READY
152030	152030	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-FACELIFT-01	HIGH		READY
144518	144518	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	HIGH		READY
143452	143452	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	MEDIUM	Production span reaches the 2022 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
145510	145510	SUV	XC40 I		5	EU-VOLVO-XC40-I-SUV-PREFL-01	HIGH		READY
58950	58950	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	MEDIUM	Production span crosses the 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
113285	113285	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
100381	100381	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
113286	113286	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
100284	100284	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
113289	113289	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
12732	12732	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	MEDIUM	Production span crosses the 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
10292	10292	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-PREFL-01	MEDIUM	Production span crosses the 2013 facelift; retained one launch-phase exterior because no Ktype-specific multi-body evidence was found.	READY
107469	107469	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
113291	113291	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
100383	100383	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
108270	108270	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
100384	100384	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
107468	107468	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
117792	117792	SUV	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	HIGH		READY
142996	142996	Van	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	MEDIUM	Commercial van homologation; exterior envelope matches the XC60 I facelift SUV body.	READY
142997	142997	Van	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	MEDIUM	Commercial van homologation; exterior envelope matches the XC60 I facelift SUV body.	READY
142998	142998	Van	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	MEDIUM	Commercial van homologation; exterior envelope matches the XC60 I facelift SUV body.	READY
142999	142999	Van	XC60 I		5	EU-VOLVO-XC60-I-SUV-FACELIFT-01	MEDIUM	Commercial van homologation; exterior envelope matches the XC60 I facelift SUV body.	READY
147101	147101	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-FACELIFT-01	HIGH		READY
147102	147102	SUV	XC60 II		5	EU-VOLVO-XC60-II-SUV-FACELIFT-01	HIGH		READY
```

[下载 left18448_16901-17000_ktype_dimension_mapping_final.tsv](sandbox:/mnt/data/left18448_16901-17000_ktype_dimension_mapping_final.tsv)

## 最终完整 DIMENSION_GROUP TSV

```tsv
DIMENSION_GROUP_ID	LengthMM	WidthMM	HeightMM	DimensionSource	SourceURL
EU-VOLVO-V70-I-WAGON-STANDARD-01	4730	1760	1430	Auto-Data Volvo V70 I generation specifications	https://www.auto-data.net/en/volvo-v70-i-generation-1934
EU-VOLVO-V70-II-WAGON-STANDARD-01	4710	1804	1465	Volvo Car Corporation technical specifications (Volvo Owners Club archive)	https://www.volvoclub.org.uk/background_v70.shtml
EU-VOLVO-V70-III-WAGON-PREFL-01	4823	1861	1547	Volvo Cars UK media technical data	https://www.media.volvocars.com/uk/en-gb/media/pressreleases/15088
EU-VOLVO-V70-III-WAGON-FACELIFT-01	4814	1861	1547	Volvo Car Germany MY2014 overview	https://news.cision.com/de/volvo-car-germany-presse/r/volvo-v70-ubersicht-my-2014%2Cc4188917
EU-VOLVO-V90-II-WAGON-PREFL-01	4936	1879	1475	Volvo Support V90 Twin Engine 2020 dimensions	https://www.volvocars.com/uk/support/car/v90-twin-engine/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V90-II-WAGON-FACELIFT-01	4945	1879	1478	Volvo Support V90 2021 dimensions	https://www.volvocars.com/mt/support/car/v90/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-PREFL-01	4939	1879	1543	Volvo V90 Cross Country MY2018 technical specifications	https://www.volvoclub.org.uk/press/volvo2018/206089_Volvo_V90_Cross_Country_Model_Year_2018_Technical_Specifications.pdf
EU-VOLVO-V90-II-WAGON-CROSS-COUNTRY-FACELIFT-01	4959	1879	1543	Volvo Support V90 Cross Country 2021 dimensions	https://www.volvocars.com/hk/support/car/v90-cross-country/20w17/article/b0804d54c7fc096bc0a81f6f065ad63e/0362eef4c7fc436fc0a81f6f7c27a289/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-XC40-I-SUV-PREFL-01	4425	1863	1652	Auto-Data Volvo XC40 2018-2022 generation specifications	https://www.auto-data.net/en/volvo-xc40-generation-5808
EU-VOLVO-XC40-I-SUV-FACELIFT-01	4440	1863	1652	Volvo Support XC40 2024 dimensions	https://www.volvocars.com/mt/support/car/xc40/article/766ee075f0e03896c0a8015109ee0749/
EU-VOLVO-XC60-I-SUV-PREFL-01	4628	1891	1713	Auto-Data Volvo XC60 I specifications	https://www.auto-data.net/en/volvo-xc60-i-2.4-d5-185hp-awd-geartronic-9387
EU-VOLVO-XC60-I-SUV-FACELIFT-01	4644	1891	1713	Auto-Data Volvo XC60 I 2013 facelift specifications	https://www.auto-data.net/en/volvo-xc60-i-2013-facelift-2.4-d4-190hp-awd-21808
EU-VOLVO-XC60-II-SUV-FACELIFT-01	4708	1902	1655	Volvo Support XC60 vehicle dimensions	https://www.volvocars.com/us/support/car/xc60/article/0ed816eed33d98cac0a8cc377bc12bc7-e6a7973b2bf222b2c0a8b09757c97ec8-8664b2fa77a7e089c0a8296870d1a409/
```

[下载 left18448_16901-17000_dimension_groups_final.tsv](sandbox:/mnt/data/left18448_16901-17000_dimension_groups_final.tsv)

推进信号：COMPLETE

[1]: https://www.auto-data.net/en/volvo-v70-i-generation-1934?utm_source=chatgpt.com "Volvo V70 I - specs, Fuel consumption, Dimensions"
[2]: https://www.volvocars.com/uk/support/car/v90-twin-engine/article/766ee075f0e03896c0a8015109ee0749/ "V90 Twin Engine Dimensions | Volvo Support UK"
[3]: https://www.auto-data.net/en/volvo-xc40-generation-5808?utm_source=chatgpt.com "Volvo XC40 | Technical Specs, Fuel consumption, ..."


--- 累计最终 TSV 已更新 ---
- 累计 Ktype 映射：ktype_mapping_final.tsv（3852 行）
- 累计尺寸组：dimension_groups_final.tsv（984 行）

